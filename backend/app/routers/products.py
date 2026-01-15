from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc
from typing import List
from typing import Optional
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
def get_products(
    db: Session = Depends(database.get_db),
    search: Optional[str] = None,
    sort: Optional[str] = None
):
    query = db.query(models.Product)

    if search:
        query = query.filter(models.Product.name.ilike(f"%{search}%"))

    if sort:
        if sort == "name_asc":
            query = query.order_by(asc(models.Product.name))
        elif sort == "name_desc":
            query = query.order_by(desc(models.Product.name))
        elif sort == "price_asc":
            query = query.order_by(asc(models.Product.unit_price))
        elif sort == "price_desc":
            query = query.order_by(desc(models.Product.unit_price))

    products = query.all()

    for product in products:
        qty = getattr(product, "quantity", 0)
        product.facing = qty // 10 
    
    return products