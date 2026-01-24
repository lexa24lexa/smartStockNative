from pydantic import BaseModel, Field, field_validator, EmailStr
from typing import Optional, List
from datetime import date, datetime

# Product Models
class ProductBase(BaseModel):
    name: str
    unit_price: float = Field(..., ge=0)
    supplier_id: int
    category_id: int

    @field_validator("supplier_id", "category_id")
    def validate_ids(cls, v):
        if v <= 0:
            raise ValueError("ID must be a positive integer")
        return v

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    product_id: int
    quantity: Optional[int] = None
    facing: Optional[int] = None

    class Config:
        from_attributes = True

# Batch Models

class BatchBase(BaseModel):
    product_id: int
    batch_code: str
    expiration_date: Optional[date]

class BatchCreate(BatchBase):
    pass

class BatchUpdate(BaseModel):
    product_id: Optional[int] = None
    batch_code: Optional[str] = None
    expiration_date: Optional[date] = None

class BatchResponse(BatchBase):
    batch_id: int
    product: Optional[ProductResponse] = None

    class Config:
        from_attributes = True

# Stock Models
class StockBase(BaseModel):
    store_id: int
    batch_id: int
    quantity: int = Field(..., ge=0)
    reorder_level: int = Field(..., ge=0)

class StockCreate(StockBase):
    reorder_level: int = Field(10, ge=0)

class StockUpdate(BaseModel):
    quantity: Optional[int] = Field(None, ge=0)
    reorder_level: Optional[int] = Field(None, ge=0)

class StockOut(BaseModel):
    stock_id: int
    store_id: int
    batch_id: int
    quantity: int
    reorder_level: int
    batch: Optional[BatchResponse] = None

    class Config:
        from_attributes = True

class StockResponse(BaseModel):
    product_name: str
    batch_code: str
    expiration_date: Optional[str]
    quantity: int

class StockOverviewResponse(BaseModel):
    product_id: int
    product_name: str
    total_quantity: int
    reorder_level: int
    status: str
    progress: float
    average_daily_sales: float
    days_to_out_of_stock: Optional[int]
    last_sale_at: Optional[datetime]
    replenishment_frequency: Optional[int] = None
    next_replenishment_date: Optional[datetime] = None
    quantity: Optional[int] = None

    class Config:
        from_attributes = True

class StockPredictionItem(BaseModel):
    product_id: int
    product_name: str
    predicted_stock_change_pct: float
    days_until_restock: Optional[int]

class StockPredictionsResponse(BaseModel):
    last_updated: datetime
    forecast_accuracy: float
    next_restock_in_days: Optional[int]
    predictions: list[StockPredictionItem]

class BatchStockResponse(BaseModel):
    batch_id: int
    batch_code: str
    expiration_date: Optional[str]
    quantity: int

class CategoryStock(BaseModel):
    category: str
    total_stock: int

# Sale Models
class SaleLineBase(BaseModel):
    batch_id: int
    quantity: int
    subtotal: Optional[float]

class SaleLineResponse(SaleLineBase):
    line_id: int
    batch: Optional[BatchResponse] = None

    class Config:
        from_attributes = True

class SaleBase(BaseModel):
    store_id: int
    total_amount: Optional[float]

class SaleCreate(SaleBase):
    lines: List[SaleLineBase]

class SaleResponse(SaleBase):
    sale_id: int
    date: datetime
    lines: List[SaleLineResponse]

    class Config:
        from_attributes = True

# Sales Analytics

class AverageDailySalesPerProduct(BaseModel):
    product_id: int
    product_name: str
    average_daily_sales: float
    total_days_with_sales: int
    total_quantity_sold: int

    class Config:
        from_attributes = True

# Replenishment Models

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
    quantity: int = Field(..., gt=0, description="Quantity must be positive")

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

# Replenishment List Models
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

# Replenishment Logs
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

# Stock Movement Models
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

# User Models
class UserOut(BaseModel):
    user_id: int
    username: str
    email: str
    role_id: int
    store_id: int
    is_active: bool

    class Config:
        from_attributes = True
