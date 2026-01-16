
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

class AverageDailySalesPerProduct(BaseModel):
    product_id: int
    product_name: str
    average_daily_sales: float
    total_days_with_sales: int
    total_quantity_sold: int

    class Config:
        from_attributes = True
