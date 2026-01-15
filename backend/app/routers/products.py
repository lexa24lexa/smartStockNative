from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
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

@router.get("/analytics/stock-by-category")
def get_stock_by_category(db: Session = Depends(database.get_db)):
    
    results = db.query(
        models.Category.category_name,
        func.sum(models.Stock.quantity).label("total_stock")
    ).join(models.Product, models.Category.category_id == models.Product.category_id)\
     .join(models.Batch, models.Product.product_id == models.Batch.product_id)\
     .join(models.Stock, models.Batch.batch_id == models.Stock.batch_id)\
     .group_by(models.Category.category_name).all()

    response = []
    for category_name, total_qty in results:
        response.append({
            "category": category_name,
            "total_stock": total_qty if total_qty else 0
        })
    
    return response