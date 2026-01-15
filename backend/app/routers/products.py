from datetime import date, timedelta
from sqlalchemy import func, or_, desc, asc
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from .. import models, database

router = APIRouter()

class ProductResponse(BaseModel):
    product_id: int
    name: str
    unit_price: float

    class Config:
        from_attributes = True

@router.get("/products", response_model=List[ProductResponse])
def get_products(db: Session = Depends(database.get_db)):
    products = db.query(models.Product).all()
    return products

@router.get("/alerts/expiring-soon")
def get_expiring_batches(db: Session = Depends(database.get_db)):

    today = date.today()
    limit_date = today + timedelta(days=30)

    results = db.query(
        models.Batch.batch_code,
        models.Batch.expiration_date,
        models.Product.name
    ).join(models.Product, models.Batch.product_id == models.Product.product_id)\
     .filter(models.Batch.expiration_date >= today)\
     .filter(models.Batch.expiration_date <= limit_date)\
     .order_by(models.Batch.expiration_date)\
     .all()

    response = []
    for batch_code, exp_date, product_name in results:
        days_left = (exp_date - today).days
        response.append({
            "product": product_name,
            "batch_code": batch_code,
            "expiration_date": exp_date,
            "days_left": days_left,
            "status": "Critical" if days_left < 7 else "Warning"
        })
    
    return response