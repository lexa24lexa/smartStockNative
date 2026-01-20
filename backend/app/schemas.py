from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime

class ProductBase(BaseModel):
    name: str
    unit_price: float
    supplier_id: int
    category_id: int

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    product_id: int
    quantity: int  
    facing: int   

    class Config:
        from_attributes = True

class StockBase(BaseModel):
    store_id: int
    batch_id: int
    quantity: int
    reorder_level: int

class AverageDailySalesPerProduct(BaseModel):
    product_id: int
    product_name: str
    average_daily_sales: float
    total_days_with_sales: int
    total_quantity_sold: int

    class Config:
        from_attributes = True

class ReplenishmentFrequencyBase(BaseModel):
    product_id: int
    store_id: int
    replenishment_frequency: int

class ReplenishmentFrequencyCreate(ReplenishmentFrequencyBase):
    last_replenishment_date: Optional[date] = None

class ReplenishmentFrequencyResponse(ReplenishmentFrequencyBase):
    frequency_id: int
    last_replenishment_date: Optional[date] = None

    class Config:
        from_attributes = True

class ReplenishmentFrequencyUpdate(BaseModel):
    replenishment_frequency: Optional[int] = None
    last_replenishment_date: Optional[date] = None

class ReplenishmentRecord(BaseModel):
    replenishment_date: Optional[date] = None
    user_id: int
    batch_id: int
    expiration_date: date
    quantity: int = Field(..., gt=0, description="Quantity must be a positive integer")

class ReplenishmentItem(BaseModel):
    product_id: int
    product_name: str
    current_stock: int
    replenishment_frequency: Optional[int] = None
    last_replenishment_date: Optional[date] = None
    next_replenishment_date: Optional[date] = None
    reason: str
    priority: str
    quantity: Optional[int] = None

    class Config:
        from_attributes = True

class ReplenishmentListBase(BaseModel):
    store_id: int
    list_date: date
    notes: Optional[str] = None

class ReplenishmentListCreate(ReplenishmentListBase):
    status: Optional[str] = "draft"

class ReplenishmentListResponse(ReplenishmentListBase):
    list_id: int
    status: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ReplenishmentListItemBase(BaseModel):
    product_id: int
    quantity: int
    current_stock: int
    reason: str
    priority: str
    notes: Optional[str] = None

class ReplenishmentListItemCreate(ReplenishmentListItemBase):
    pass

class ReplenishmentListItemResponse(ReplenishmentListItemBase):
    item_id: int
    list_id: int
    product_name: Optional[str] = None

    class Config:
        from_attributes = True

class ReplenishmentListItemUpdate(BaseModel):
    quantity: Optional[int] = None
    reason: Optional[str] = None
    priority: Optional[str] = None
    notes: Optional[str] = None

class ReplenishmentListWithItems(ReplenishmentListResponse):
    items: List[ReplenishmentListItemResponse] = []

class ReplenishmentLogCreate(BaseModel):
    product_id: int
    store_id: int
    batch_id: int
    expiration_date: date
    quantity: int
    user_id: int

class ReplenishmentLogResponse(ReplenishmentLogCreate):
    log_id: int
    timestamp: datetime

    class Config:
        from_attributes = True

class StockMovementCreate(BaseModel):
    product_id: int
    batch_id: int
    quantity: int
    origin_type: str
    origin_id: Optional[int] = None
    destination_type: str
    destination_id: Optional[int] = None

class StockMovementResponse(StockMovementCreate):
    movement_id: int
    timestamp: datetime

    class Config:
        from_attributes = True
