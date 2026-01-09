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