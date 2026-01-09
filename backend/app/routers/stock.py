from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import date
from .. import models, database

router = APIRouter()

class StockResponse(BaseModel):
    product_name: str
    batch_code: str
    expiration_date: Optional[date]
    quantity: int

@router.get("/stock/{store_id}", response_model=List[StockResponse])
def get_store_stock(store_id: int, db: Session = Depends(database.get_db)):
    results = db.query(
        models.Product.name,
        models.Batch.batch_code,
        models.Batch.expiration_date,
        models.Stock.quantity
    ).join(models.Batch, models.Batch.product_id == models.Product.product_id)\
     .join(models.Stock, models.Stock.batch_id == models.Batch.batch_id)\
     .filter(models.Stock.store_id == store_id)\
     .all()

    response_data = []
    for r in results:
        response_data.append(StockResponse(
            product_name=r.name,
            batch_code=r.batch_code,
            expiration_date=r.expiration_date,
            quantity=r.quantity
        ))

    return response_data