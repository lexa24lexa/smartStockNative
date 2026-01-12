
from pydantic import BaseModel
from typing import Optional, List


class ProductBase(BaseModel):
    name: str
    unit_price: float
    supplier_id: int
    category_id: int

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    product_id: int
    class Config:
        from_attributes = True

class StockBase(BaseModel):
    store_id: int
    batch_id: int
    quantity: int