from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app import models, database

router = APIRouter()

class StockResponse(BaseModel):
    product_name: str
    batch_code: str
    expiration_date: Optional[date]
    quantity: int

class BatchStockResponse(BaseModel):
    batch_id: int
    batch_code: str
    expiration_date: Optional[date]
    quantity: int

class SaleItemInput(BaseModel):
    product_id: int
    batch_id: Optional[int] = None
    quantity: int

class SaleItemFIFOInput(BaseModel):
    product_id: int
    quantity: int
    selected_batch_id: Optional[int] = None

class SaleFIFOInput(BaseModel):
    store_id: int
    items: List[SaleItemFIFOInput]

class FIFOViolationCheckInput(BaseModel):
    store_id: int
    product_id: int
    selected_batch_id: int


def _fifo_batches_for_product(db: Session, store_id: int, product_id: int):
    """Return batches with stock > 0 in FIFO order (earliest expiration first)."""
    return (
        db.query(models.Batch, models.Stock)
        .join(models.Stock, models.Stock.batch_id == models.Batch.batch_id)
        .filter(models.Stock.store_id == store_id)
        .filter(models.Batch.product_id == product_id)
        .filter(models.Stock.quantity > 0)
        .order_by(
            models.Batch.expiration_date.is_(None),
            models.Batch.expiration_date.asc(),
            models.Batch.batch_id.asc()
        )
        .all()
    )

def _check_fifo_violation(db: Session, store_id: int, product_id: int, selected_batch_id: int):
    fifo_rows = _fifo_batches_for_product(db, store_id, product_id)

    if not fifo_rows:
        return {
            "is_violation": False,
            "message": "No stock available for this product in this store.",
            "expected_batch_id": None,
            "expected_batch_code": None,
        }

    expected = fifo_rows[0][0]

    if expected.batch_id == selected_batch_id:
        return {
            "is_violation": False,
            "message": "OK (FIFO respected).",
            "expected_batch_id": expected.batch_id,
            "expected_batch_code": expected.batch_code,
        }

    return {
        "is_violation": True,
        "message": "FIFO violation: selected batch is not the next FIFO batch.",
        "expected_batch_id": expected.batch_id,
        "expected_batch_code": expected.batch_code,
    }

@router.get("/stock/{store_id}", response_model=List[StockResponse])
def get_store_stock(store_id: int, db: Session = Depends(database.get_db)):
    if store_id <= 0:
        raise HTTPException(status_code=400, detail="store_id must be a positive integer.")

    results = (
        db.query(
            models.Product.name,
            models.Batch.batch_code,
            models.Batch.expiration_date,
            models.Stock.quantity,
        )
        .join(models.Batch, models.Batch.product_id == models.Product.product_id)
        .join(models.Stock, models.Stock.batch_id == models.Batch.batch_id)
        .filter(models.Stock.store_id == store_id)
        .all()
    )

    return [
        StockResponse(
            product_name=r.name,
            batch_code=r.batch_code,
            expiration_date=r.expiration_date,
            quantity=r.quantity
        )
        for r in results
    ]


@router.get("/stock/{store_id}/product/{product_id}/batches", response_model=List[BatchStockResponse])
def get_product_batches_in_store(store_id: int, product_id: int, db: Session = Depends(database.get_db)):
    if store_id <= 0 or product_id <= 0:
        raise HTTPException(status_code=400, detail="store_id and product_id must be positive integers.")

    try:
        results = (
            db.query(
                models.Batch.batch_id,
                models.Batch.batch_code,
                models.Batch.expiration_date,
                models.Stock.quantity,
            )
            .join(models.Stock, models.Stock.batch_id == models.Batch.batch_id)
            .filter(models.Stock.store_id == store_id)
            .filter(models.Batch.product_id == product_id)
            .filter(models.Stock.quantity > 0)
            .order_by(
                models.Batch.expiration_date.is_(None),
                models.Batch.expiration_date.asc(),
                models.Batch.batch_id.asc(),
            )
            .all()
        )

        return [
            BatchStockResponse(
                batch_id=r.batch_id,
                batch_code=r.batch_code,
                expiration_date=r.expiration_date,
                quantity=r.quantity,
            )
            for r in results
        ]
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
