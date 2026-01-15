from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from .. import modelx   s, database

router = APIRouter()

class SaleItemFIFOInput(BaseModel):
    product_id: int
    quantity: int
    selected_batch_id: int | None = None  # (FR16 uses it)

class SaleFIFOInput(BaseModel):
    store_id: int
    items: List[SaleItemFIFOInput]

class FIFOViolationCheckInput(BaseModel):
    store_id: int
    product_id: int
    selected_batch_id: int

def _fifo_batches_for_product(db: Session, store_id: int, product_id: int):
    return (
        db.query(models.Batch, models.Stock)
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

def _check_fifo_violation(db: Session, store_id: int, product_id: int, selected_batch_id: int):
    fifo_rows = _fifo_batches_for_product(db, store_id, product_id)
    if not fifo_rows:
        return {
            "is_violation": False,
            "message": "No stock available for this product in this store.",
            "expected_batch_id": None,
            "expected_batch_code": None,
        }

    expected_batch = fifo_rows[0][0]
    if expected_batch.batch_id == selected_batch_id:
        return {
            "is_violation": False,
            "message": "OK (FIFO respected).",
            "expected_batch_id": expected_batch.batch_id,
            "expected_batch_code": expected_batch.batch_code,
        }

    return {
        "is_violation": True,
        "message": "FIFO violation: selected batch is not the next FIFO batch.",
        "expected_batch_id": expected_batch.batch_id,
        "expected_batch_code": expected_batch.batch_code,
    }


@router.post("/sales/fifo")
def create_sale_fifo(sale_input: SaleFIFOInput, db: Session = Depends(database.get_db)):
    total_amount = 0.0
    used_batches: List[dict] = []

    new_sale = models.Sale(store_id=sale_input.store_id, total_amount=0)
    db.add(new_sale)
    db.commit()
    db.refresh(new_sale)

    try:
        for item in sale_input.items:
            fifo_rows = _fifo_batches_for_product(db, sale_input.store_id, item.product_id)
            if not fifo_rows:
                raise HTTPException(status_code=400, detail=f"No stock available for product {item.product_id}")

            remaining = item.quantity
            product = db.query(models.Product).filter(models.Product.product_id == item.product_id).first()
            if not product:
                raise HTTPException(status_code=400, detail=f"Unknown product {item.product_id}")

            for batch, stock in fifo_rows:
                if remaining <= 0:
                    break
                if stock.quantity <= 0:
                    continue

                take = min(stock.quantity, remaining)
                stock.quantity -= take
                remaining -= take

                subtotal = float(product.unit_price) * take
                total_amount += subtotal

                db.add(
                    models.SaleLine(
                        sale_id=new_sale.sale_id,
                        batch_id=batch.batch_id,
                        quantity=take,
                        subtotal=subtotal,
                    )
                )

                used_batches.append(
                    {
                        "product_id": item.product_id,
                        "batch_id": batch.batch_id,
                        "batch_code": batch.batch_code,
                        "expiration_date": batch.expiration_date,
                        "quantity": take,
                    }
                )

            if remaining > 0:
                raise HTTPException(status_code=400, detail=f"Insufficient stock for product {item.product_id} (missing {remaining})")

        new_sale.total_amount = total_amount
        db.commit()

        return {
            "message": "Sale processed successfully (FIFO enforced)",
            "sale_id": new_sale.sale_id,
            "total": total_amount,
            "used_batches": used_batches,
            "warnings": [],
        }

    except Exception as e:
        db.rollback()
        raise e

@router.post("/fifo/check")
def fifo_violation_check(payload: FIFOViolationCheckInput, db: Session = Depends(database.get_db)):
    return _check_fifo_violation(
        db=db,
        store_id=payload.store_id,
        product_id=payload.product_id,
        selected_batch_id=payload.selected_batch_id,
    )
