from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
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
