from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from .. import modelx   s, database

router = APIRouter()

class SaleItemInput(BaseModel):
    product_id : int
    batch_id: int | None = None # For FR16
    quantity: int

class SaleInput(BaseModel):
    store_id: int
    items: List[SaleItemInput]


@router.post("/sales")
def create_sale(sale_input: SaleInput, db: Session = Depends(database.get_db)):
    
    total_amount = 0
    
    new_sale = models.Sale(store_id=sale_input.store_id, total_amount=0)
    db.add(new_sale)
    db.commit()
    db.refresh(new_sale)

    try:
        for item in sale_input.items:
            stock_record = db.query(models.Stock).filter(
                models.Stock.store_id == sale_input.store_id,
                models.Stock.batch_id == item.batch_id
            ).first()

            if not stock_record or stock_record.quantity < item.quantity:
                raise HTTPException(status_code=400, detail=f"Insufficient stock for batch {item.batch_id}")

            stock_record.quantity -= item.quantity

            batch = db.query(models.Batch).filter(models.Batch.batch_id == item.batch_id).first()
            product = db.query(models.Product).filter(models.Product.product_id == batch.product_id).first()
            
            subtotal = product.unit_price * item.quantity
            total_amount += subtotal

            sale_line = models.SaleLine(
                sale_id=new_sale.sale_id,
                batch_id=item.batch_id,
                quantity=item.quantity,
                subtotal=subtotal
            )
            db.add(sale_line)

        new_sale.total_amount = total_amount
        db.commit()
        
        return {"message": "Sale processed successfully", "sale_id": new_sale.sale_id, "total": total_amount}

    except Exception as e:
        db.rollback()
        raise e

class SaleItemFIFOInput(BaseModel):
    product_id: int
    quantity: int
    selected_batch_id: Optional[int] = None # Used on FR16 as warning

class SaleFIFOInput(BaseModel):
    store_id: int
    items: List[SaleItemFIFOInput]


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


@router.post("/sales/fifo")
def create_sale_fifo(payload: SaleFIFOInput, db: Session = Depends(database.get_db)):
    """
    New endpoint that ENFORCES FIFO.
    Does not modify existing /sales endpoint.
    """
    total_amount = 0.0
    used_batches = []
    warnings = []

    new_sale = models.Sale(store_id=payload.store_id, total_amount=0)
    db.add(new_sale)
    db.commit()
    db.refresh(new_sale)

    try:
        for item in payload.items:
            product = db.query(models.Product).filter(models.Product.product_id == item.product_id).first()
            if not product:
                raise HTTPException(status_code=400, detail=f"Unknown product {item.product_id}")

            fifo_rows = _fifo_batches_for_product(db, payload.store_id, item.product_id)
            if not fifo_rows:
                raise HTTPException(status_code=400, detail=f"No stock available for product {item.product_id}")

            remaining = item.quantity

            for batch, stock in fifo_rows:
                if remaining <= 0:
                    break

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
                        subtotal=subtotal
                    )
                )

                used_batches.append({
                    "product_id": item.product_id,
                    "batch_id": batch.batch_id,
                    "batch_code": batch.batch_code,
                    "expiration_date": batch.expiration_date,
                    "quantity": take
                })

            if remaining > 0:
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient stock for product {item.product_id} (missing {remaining})"
                )

        new_sale.total_amount = total_amount
        db.commit()

        return {
            "message": "Sale processed successfully (FIFO enforced)",
            "sale_id": new_sale.sale_id,
            "total": total_amount,
            "used_batches": used_batches,
            "warnings": warnings
        }

    except Exception as e:
        db.rollback()
        raise e

class FIFOViolationCheckInput(BaseModel):
    store_id: int
    product_id: int
    selected_batch_id: int


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


@router.post("/fifo/check")
def fifo_check(payload: FIFOViolationCheckInput, db: Session = Depends(database.get_db)):
    return _check_fifo_violation(db, payload.store_id, payload.product_id, payload.selected_batch_id)

