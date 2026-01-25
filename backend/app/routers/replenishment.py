from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date
from typing import List, Optional
from datetime import date, date as date_class, timedelta
from .. import models, database, schemas
from .deps import get_current_user
from ..models import Stock, Batch
from ..database import get_db

router = APIRouter()

# Replenishment Frequency CRUD

# Create or update a replenishment frequency for a product at a store
@router.post("/replenishment-frequency", response_model=schemas.ReplenishmentFrequencyResponse)
def create_replenishment_frequency(frequency_data: schemas.ReplenishmentFrequencyCreate, db: Session = Depends(database.get_db)):
    """Create a new or update an existing replenishment frequency."""
    if not (1 <= frequency_data.replenishment_frequency <= 3):
        raise HTTPException(status_code=400, detail="Replenishment frequency must be between 1 and 3")

    product = db.query(models.Product).filter(models.Product.product_id == frequency_data.product_id, models.Product.is_active).first()
    if not product:
        raise HTTPException(status_code=404, detail=f"Product {frequency_data.product_id} not found or inactive")
    
    store = db.query(models.Store).filter(models.Store.store_id == frequency_data.store_id, models.Store.is_active).first()
    if not store:
        raise HTTPException(status_code=404, detail=f"Store {frequency_data.store_id} not found or inactive")

    existing = db.query(models.ReplenishmentFrequency).filter(
        models.ReplenishmentFrequency.product_id == frequency_data.product_id,
        models.ReplenishmentFrequency.store_id == frequency_data.store_id
    ).first()

    if existing:
        existing.replenishment_frequency = frequency_data.replenishment_frequency
        existing.last_replenishment_date = frequency_data.last_replenishment_date or existing.last_replenishment_date
        db.commit()
        db.refresh(existing)
        return existing

    new_frequency = models.ReplenishmentFrequency(**frequency_data.dict())
    db.add(new_frequency)
    db.commit()
    db.refresh(new_frequency)
    return new_frequency

# Get all replenishment frequencies (optional filtering)
@router.get("/replenishment-frequency", response_model=List[schemas.ReplenishmentFrequencyResponse])
def get_replenishment_frequencies(store_id: Optional[int] = None, product_id: Optional[int] = None, db: Session = Depends(database.get_db)):
    query = db.query(models.ReplenishmentFrequency)
    if store_id is not None:
        query = query.filter(models.ReplenishmentFrequency.store_id == store_id)
    if product_id is not None:
        query = query.filter(models.ReplenishmentFrequency.product_id == product_id)
    return query.all()

# Get a specific replenishment frequency
@router.get("/replenishment-frequency/{product_id}/{store_id}", response_model=schemas.ReplenishmentFrequencyResponse)
def get_replenishment_frequency(product_id: int, store_id: int, db: Session = Depends(database.get_db)):
    frequency = db.query(models.ReplenishmentFrequency).filter(
        models.ReplenishmentFrequency.product_id == product_id,
        models.ReplenishmentFrequency.store_id == store_id
    ).first()
    if not frequency:
        raise HTTPException(status_code=404, detail=f"Replenishment frequency for product {product_id} at store {store_id} not found")
    return frequency

# Update a replenishment frequency
@router.put("/replenishment-frequency/{product_id}/{store_id}", response_model=schemas.ReplenishmentFrequencyResponse)
def update_replenishment_frequency(product_id: int, store_id: int, frequency_update: schemas.ReplenishmentFrequencyUpdate, db: Session = Depends(database.get_db)):
    if frequency_update.replenishment_frequency is not None and not (1 <= frequency_update.replenishment_frequency <= 3):
        raise HTTPException(status_code=400, detail="Replenishment frequency must be between 1 and 3")

    frequency = db.query(models.ReplenishmentFrequency).filter(
        models.ReplenishmentFrequency.product_id == product_id,
        models.ReplenishmentFrequency.store_id == store_id
    ).first()

    if not frequency:
        raise HTTPException(status_code=404, detail=f"Replenishment frequency for product {product_id} at store {store_id} not found")

    if frequency_update.replenishment_frequency is not None:
        frequency.replenishment_frequency = frequency_update.replenishment_frequency
    if frequency_update.last_replenishment_date is not None:
        frequency.last_replenishment_date = frequency_update.last_replenishment_date

    db.commit()
    db.refresh(frequency)
    return frequency

# Record a replenishment event
@router.patch("/replenishment-frequency/{product_id}/{store_id}/replenish", response_model=schemas.ReplenishmentFrequencyResponse)
def record_replenishment(product_id: int, store_id: int, replenishment_data: schemas.ReplenishmentRecord = Body(...), db: Session = Depends(database.get_db)):

    frequency = db.query(models.ReplenishmentFrequency).filter(
        models.ReplenishmentFrequency.product_id == product_id,
        models.ReplenishmentFrequency.store_id == store_id
    ).first()
    if not frequency:
        raise HTTPException(status_code=404, detail=f"Replenishment frequency not found for product {product_id} at store {store_id}")

    if replenishment_data.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be a positive integer")

    batch = db.query(models.Batch).filter(models.Batch.batch_id == replenishment_data.batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail=f"Batch {replenishment_data.batch_id} not found")
    
    user = db.query(models.User).filter(models.User.user_id == replenishment_data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User {replenishment_data.user_id} not found")

    replenishment_date = replenishment_data.replenishment_date or date.today()

    from sqlalchemy.exc import SQLAlchemyError
    try:
        # Update frequency
        frequency.last_replenishment_date = replenishment_date
        db.add(frequency)

        # Create log
        log = models.ReplenishmentLog(
            product_id=product_id,
            store_id=store_id,
            batch_id=replenishment_data.batch_id,
            expiration_date=replenishment_data.expiration_date,
            quantity=replenishment_data.quantity,
            user_id=replenishment_data.user_id
        )
        db.add(log)

        # Commit everything at once
        db.commit()

        # Refresh objects after commit
        db.refresh(frequency)
        db.refresh(log)

    except SQLAlchemyError as e:
        db.rollback()
        print("SQLAlchemyError occurred:", e)
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    return frequency

# Delete a replenishment frequency
@router.delete("/replenishment-frequency/{product_id}/{store_id}")
def delete_replenishment_frequency(product_id: int, store_id: int, db: Session = Depends(database.get_db)):
    frequency = db.query(models.ReplenishmentFrequency).filter(
        models.ReplenishmentFrequency.product_id == product_id,
        models.ReplenishmentFrequency.store_id == store_id
    ).first()

    if not frequency:
        raise HTTPException(status_code=404, detail=f"Replenishment frequency for product {product_id} at store {store_id} not found")

    db.delete(frequency)
    db.commit()
    return {"message": f"Replenishment frequency for product {product_id} at store {store_id} deleted"}

# Replenishment Logs CRUD

# Validation for a replenishment log
def validate_replenishment_log(db: Session, log: schemas.ReplenishmentLogCreate):
    if log.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be greater than 0")
    
    batch = db.query(models.Batch).filter(models.Batch.batch_id == log.batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    if log.expiration_date < date.today() or log.expiration_date < batch.creation_date:
        raise HTTPException(status_code=400, detail="Expiration date is invalid")

    product = db.query(models.Product).filter(models.Product.product_id == log.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    store = db.query(models.Store).filter(models.Store.store_id == log.store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")

    user = db.query(models.User).filter(models.User.user_id == log.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

# Create replenishment log
@router.post("/replenishment-logs/", response_model=schemas.ReplenishmentLogResponse)
def create_replenishment_log(log: schemas.ReplenishmentLogCreate, db: Session = Depends(database.get_db)):
    validate_replenishment_log(db, log)
    db_log = models.ReplenishmentLog(**log.dict())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

# Get logs for a product at a store
@router.get("/replenishment-logs/{store_id}/{product_id}", response_model=List[schemas.ReplenishmentLogResponse])
def get_replenishment_logs(store_id: int, product_id: int, db: Session = Depends(database.get_db)):
    logs = db.query(models.ReplenishmentLog).filter(
        models.ReplenishmentLog.store_id == store_id,
        models.ReplenishmentLog.product_id == product_id
    ).order_by(models.ReplenishmentLog.timestamp.desc()).all()
    return logs

# Update a replenishment log
@router.put("/replenishment-logs/{log_id}", response_model=schemas.ReplenishmentLogResponse)
def update_replenishment_log(log_id: int, log: schemas.ReplenishmentLogCreate, db: Session = Depends(database.get_db)):
    db_log = db.query(models.ReplenishmentLog).filter(models.ReplenishmentLog.log_id == log_id).first()
    if not db_log:
        raise HTTPException(status_code=404, detail="Log not found")
    validate_replenishment_log(db, log)
    for key, value in log.dict().items():
        setattr(db_log, key, value)
    db.commit()
    db.refresh(db_log)
    return db_log

# Delete a replenishment log
@router.delete("/replenishment-logs/{log_id}")
def delete_replenishment_log(log_id: int, db: Session = Depends(database.get_db)):
    db_log = db.query(models.ReplenishmentLog).filter(models.ReplenishmentLog.log_id == log_id).first()
    if not db_log:
        raise HTTPException(status_code=404, detail="Log not found")
    db.delete(db_log)
    db.commit()
    return {"detail": "Replenishment log deleted"}

# Replenishment Lists

# Generate daily replenishment list
@router.get("/replenishment-list/{store_id}", response_model=List[schemas.ReplenishmentItem])
def get_daily_replenishment_list(store_id: int, db: Session = Depends(database.get_db)):
    """
    Generate automated daily replenishment list for a store.
    Includes out-of-stock products and products due for replenishment.
    """
    store = db.query(models.Store).filter(models.Store.store_id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail=f"Store with ID {store_id} not found")

    today = date_class.today()
    replenishment_items = []

    # Get all replenishment frequencies for the store
    frequencies = db.query(models.ReplenishmentFrequency).filter(
        models.ReplenishmentFrequency.store_id == store_id
    ).all()
    frequency_product_ids = {f.product_id for f in frequencies}
    frequency_map = {f.product_id: f for f in frequencies}

    # Get current stock by product
    stock_by_product = db.query(
        models.Product.product_id,
        models.Product.name,
        func.sum(models.Stock.quantity).label('total_quantity')
    ).join(
        models.Batch, models.Batch.product_id == models.Product.product_id
    ).join(
        models.Stock, models.Stock.batch_id == models.Batch.batch_id
    ).filter(
        models.Stock.store_id == store_id
    ).group_by(
        models.Product.product_id,
        models.Product.name
    ).all()
    stock_map = {item.product_id: (item.name, item.total_quantity or 0) for item in stock_by_product}

    # Calculate average daily sales
    daily_sales = db.query(
        models.Batch.product_id,
        cast(models.Sale.date, Date).label('sale_date'),
        func.sum(models.SaleLine.quantity).label('daily_quantity')
    ).select_from(
        models.SaleLine
    ).join(
        models.Sale, models.Sale.sale_id == models.SaleLine.sale_id
    ).join(
        models.Batch, models.Batch.batch_id == models.SaleLine.batch_id
    ).filter(
        models.Sale.store_id == store_id
    ).group_by(
        models.Batch.product_id,
        cast(models.Sale.date, Date)
    ).subquery()

    avg_sales_results = db.query(
        models.Product.product_id,
        func.avg(daily_sales.c.daily_quantity).label('average_daily_sales')
    ).join(
        daily_sales, models.Product.product_id == daily_sales.c.product_id
    ).group_by(
        models.Product.product_id
    ).all()

    avg_sales_map = {item.product_id: float(item.average_daily_sales) if item.average_daily_sales else 0.0
                     for item in avg_sales_results}

    # Generate items based on stock and frequency
    for product_id, frequency in frequency_map.items():
        product_name, current_stock = stock_map.get(product_id, (None, 0))
        if product_name is None:
            product_obj = db.query(models.Product).filter(models.Product.product_id == product_id).first()
            if product_obj:
                product_name = product_obj.name
                current_stock = 0
            else:
                continue

        is_out_of_stock = current_stock == 0
        is_frequency_due = frequency.last_replenishment_date is None or (today - frequency.last_replenishment_date).days >= frequency.replenishment_frequency
        next_replenishment_date = frequency.last_replenishment_date + timedelta(days=frequency.replenishment_frequency) if frequency.last_replenishment_date else None

        if is_out_of_stock and is_frequency_due:
            reason = "Out of stock & Frequency due"
            priority = "high"
        elif is_out_of_stock:
            reason = "Out of stock"
            priority = "high"
        elif is_frequency_due:
            reason = "Frequency due"
            priority = "medium"
        else:
            continue

        average_daily_sales = avg_sales_map.get(product_id, 0.0)
        quantity = int(round(max(0, average_daily_sales * frequency.replenishment_frequency - current_stock))) if average_daily_sales > 0 else None

        replenishment_items.append(schemas.ReplenishmentItem(
            product_id=product_id,
            product_name=product_name,
            current_stock=current_stock,
            replenishment_frequency=frequency.replenishment_frequency,
            last_replenishment_date=frequency.last_replenishment_date,
            next_replenishment_date=next_replenishment_date,
            reason=reason,
            priority=priority,
            quantity=quantity
        ))

    # Include out-of-stock products without frequency
    for product_id, (product_name, current_stock) in stock_map.items():
        if product_id not in frequency_product_ids and current_stock == 0:
            average_daily_sales = avg_sales_map.get(product_id, 0.0)
            quantity = int(round(max(0, average_daily_sales * 3 - current_stock))) if average_daily_sales > 0 else None
            replenishment_items.append(schemas.ReplenishmentItem(
                product_id=product_id,
                product_name=product_name,
                current_stock=current_stock,
                replenishment_frequency=None,
                last_replenishment_date=None,
                next_replenishment_date=None,
                reason="Out of stock",
                priority="high",
                quantity=quantity
            ))

    # Sort by priority and name
    priority_order = {"high": 0, "medium": 1, "low": 2}
    replenishment_items.sort(key=lambda x: (priority_order.get(x.priority, 3), x.product_name))

    return replenishment_items

# Create replenishment list
@router.post("/replenishment-lists", response_model=schemas.ReplenishmentListResponse)
def create_replenishment_list(list_data: schemas.ReplenishmentListCreate, db: Session = Depends(database.get_db)):
    if list_data.list_date < date_class.today():
        raise HTTPException(status_code=400, detail="List date cannot be in the past")
    store = db.query(models.Store).filter(models.Store.store_id == list_data.store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail=f"Store {list_data.store_id} not found")
    existing = db.query(models.ReplenishmentList).filter(
        models.ReplenishmentList.store_id == list_data.store_id,
        models.ReplenishmentList.list_date == list_data.list_date
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Replenishment list already exists for this date")
    new_list = models.ReplenishmentList(
        store_id=list_data.store_id,
        list_date=list_data.list_date,
        status=list_data.status or "draft",
        notes=list_data.notes
    )
    db.add(new_list)
    db.commit()
    db.refresh(new_list)
    return new_list

# Add item to replenishment list
@router.post("/replenishment-lists/{store_id}/{list_date}/items", response_model=schemas.ReplenishmentListItemResponse)
def add_replenishment_list_item(store_id: int, list_date: date_class, item_data: schemas.ReplenishmentListItemCreate, db: Session = Depends(database.get_db)):
    if item_data.quantity < 0:
        raise HTTPException(status_code=400, detail="Quantity cannot be negative")
    replenishment_list = db.query(models.ReplenishmentList).filter(
        models.ReplenishmentList.store_id == store_id,
        models.ReplenishmentList.list_date == list_date
    ).first()
    if not replenishment_list:
        raise HTTPException(status_code=404, detail="Replenishment list not found")
    product = db.query(models.Product).filter(models.Product.product_id == item_data.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if not item_data.reason or not item_data.priority:
        raise HTTPException(status_code=400, detail="Reason and priority are required")
    valid_priorities = ["High", "Medium", "Low"]
    if item_data.priority not in valid_priorities:
        raise HTTPException(status_code=400, detail=f"Priority must be one of {', '.join(valid_priorities)}")
    existing = db.query(models.ReplenishmentListItem).filter(
        models.ReplenishmentListItem.list_id == replenishment_list.list_id,
        models.ReplenishmentListItem.product_id == item_data.product_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Product already exists in this list")
    new_item = models.ReplenishmentListItem(
        list_id=replenishment_list.list_id,
        product_id=item_data.product_id,
        quantity=item_data.quantity,
        current_stock=item_data.current_stock,
        reason=item_data.reason,
        priority=item_data.priority,
        notes=item_data.notes
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return schemas.ReplenishmentListItemResponse(
        item_id=new_item.item_id,
        list_id=new_item.list_id,
        product_id=new_item.product_id,
        product_name=product.name,
        quantity=new_item.quantity,
        current_stock=new_item.current_stock,
        reason=new_item.reason,
        priority=new_item.priority,
        notes=new_item.notes
    )

# Update item in replenishment list
@router.put("/replenishment-lists/{store_id}/{list_date}/items/{product_id}", response_model=schemas.ReplenishmentListItemResponse)
def update_replenishment_list_item(store_id: int, list_date: date_class, product_id: int, item_update: schemas.ReplenishmentListItemUpdate, db: Session = Depends(database.get_db)):
    replenishment_list = db.query(models.ReplenishmentList).filter(
        models.ReplenishmentList.store_id == store_id,
        models.ReplenishmentList.list_date == list_date
    ).first()
    if not replenishment_list:
        raise HTTPException(status_code=404, detail="Replenishment list not found")
    item = db.query(models.ReplenishmentListItem).filter(
        models.ReplenishmentListItem.list_id == replenishment_list.list_id,
        models.ReplenishmentListItem.product_id == product_id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Product not found in list")
    if item_update.quantity is not None:
        if item_update.quantity < 0:
            raise HTTPException(status_code=400, detail="Quantity cannot be negative")
        item.quantity = item_update.quantity
    if item_update.reason is not None:
        item.reason = item_update.reason
    if item_update.priority is not None:
        valid_priorities = ["High", "Medium", "Low"]
        if item_update.priority not in valid_priorities:
            raise HTTPException(status_code=400, detail=f"Priority must be one of {', '.join(valid_priorities)}")
        item.priority = item_update.priority
    if item_update.notes is not None:
        item.notes = item_update.notes
    db.commit()
    db.refresh(item)
    product = db.query(models.Product).filter(models.Product.product_id == item.product_id).first()
    return schemas.ReplenishmentListItemResponse(
        item_id=item.item_id,
        list_id=item.list_id,
        product_id=item.product_id,
        product_name=product.name if product else None,
        quantity=item.quantity,
        current_stock=item.current_stock,
        reason=item.reason,
        priority=item.priority,
        notes=item.notes
    )

# Delete item from replenishment list
@router.delete("/replenishment-lists/{store_id}/{list_date}/items/{product_id}")
def delete_replenishment_list_item(store_id: int, list_date: date_class, product_id: int, db: Session = Depends(database.get_db)):
    replenishment_list = db.query(models.ReplenishmentList).filter(
        models.ReplenishmentList.store_id == store_id,
        models.ReplenishmentList.list_date == list_date
    ).first()
    if not replenishment_list:
        raise HTTPException(status_code=404, detail="Replenishment list not found")
    item = db.query(models.ReplenishmentListItem).filter(
        models.ReplenishmentListItem.list_id == replenishment_list.list_id,
        models.ReplenishmentListItem.product_id == product_id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Product not found in list")
    db.delete(item)
    db.commit()
    return {"message": "Item deleted"}

# Override replenishment item (manager only)
@router.post("/replenishment-lists/{store_id}/{list_date}/items/{product_id}/override", response_model=schemas.ReplenishmentListItemResponse)
def override_replenishment_item(
    store_id: int,
    list_date: date_class,
    product_id: int,
    override_data: schemas.ReplenishmentListItemUpdate = Body(...),
    db: Session = Depends(database.get_db),
    user_id: int = Body(...),
):
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user or user.role_id != 2:
        raise HTTPException(status_code=403, detail="Only managers can override replenishment items")

    # Get the list and item
    replenishment_list = db.query(models.ReplenishmentList).filter(
        models.ReplenishmentList.store_id == store_id,
        models.ReplenishmentList.list_date == list_date
    ).first()
    if not replenishment_list:
        raise HTTPException(status_code=404, detail="Replenishment list not found")

    item = db.query(models.ReplenishmentListItem).filter(
        models.ReplenishmentListItem.list_id == replenishment_list.list_id,
        models.ReplenishmentListItem.product_id == product_id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Product not found in list")

    # Apply overrides
    if override_data.quantity is not None:
        if override_data.quantity < 0:
            raise HTTPException(status_code=400, detail="Quantity cannot be negative")
        item.quantity = override_data.quantity
    if override_data.reason is not None:
        item.reason = override_data.reason
    if override_data.priority is not None:
        valid_priorities = ["High", "Medium", "Low"]
        if override_data.priority not in valid_priorities:
            raise HTTPException(status_code=400, detail=f"Priority must be one of {', '.join(valid_priorities)}")
        item.priority = override_data.priority
    if override_data.notes is not None:
        item.notes = override_data.notes

    db.commit()
    db.refresh(item)

    product = db.query(models.Product).filter(models.Product.product_id == item.product_id).first()
    return schemas.ReplenishmentListItemResponse(
        item_id=item.item_id,
        list_id=item.list_id,
        product_id=item.product_id,
        product_name=product.name if product else None,
        quantity=item.quantity,
        current_stock=item.current_stock,
        reason=item.reason,
        priority=item.priority,
        notes=item.notes
    )

def get_fifo_batch(db: Session, store_id: int, product_id: int):
    stock = (
        db.query(Stock)
        .join(Batch)
        .filter(
            Stock.store_id == store_id,
            Batch.product_id == product_id,
            Stock.quantity > 0
        )
        .order_by(Batch.expiration_date.asc())
        .first()
    )

    if not stock:
        raise HTTPException(status_code=404, detail="No stock available")

    return stock

@router.get("/replenishment/{store_id}/{product_id}")
def get_replenishment_batch(
    store_id: int,
    product_id: int,
    db: Session = Depends(get_db),
):
    stock_item = get_fifo_batch(db, store_id, product_id)

    return {
        "batch_id": stock_item.batch.batch_id,
        "batch_code": stock_item.batch.batch_code,
        "expiration_date": stock_item.batch.expiration_date,
        "quantity": stock_item.quantity,
    }
