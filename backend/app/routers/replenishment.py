from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date
from typing import List, Optional
from datetime import date, date as date_class, timedelta
from .. import models, database, schemas

router = APIRouter()

@router.post("/replenishment-frequency", response_model=schemas.ReplenishmentFrequencyResponse)
def create_replenishment_frequency(
    frequency_data: schemas.ReplenishmentFrequencyCreate,
    db: Session = Depends(database.get_db)
):
    """
    Create or update replenishment frequency for a product at a store.
    If a frequency already exists for this product-store combination, it will be updated.
    """

    if not (1 <= frequency_data.replenishment_frequency <= 3):
        raise HTTPException(
            status_code=400,
            detail="Replenishment frequency must be between 1 and 3 days"
        )

    product = db.query(models.Product).filter(
        models.Product.product_id == frequency_data.product_id
    ).first()
    if not product:
        raise HTTPException(
            status_code=404,
            detail=f"Product with ID {frequency_data.product_id} not found"
        )

    store = db.query(models.Store).filter(
        models.Store.store_id == frequency_data.store_id
    ).first()
    if not store:
        raise HTTPException(
            status_code=404,
            detail=f"Store with ID {frequency_data.store_id} not found"
        )

    existing = db.query(models.ReplenishmentFrequency).filter(
        models.ReplenishmentFrequency.product_id == frequency_data.product_id,
        models.ReplenishmentFrequency.store_id == frequency_data.store_id
    ).first()

    if existing:
        existing.replenishment_frequency = frequency_data.replenishment_frequency
        if frequency_data.last_replenishment_date is not None:
            existing.last_replenishment_date = frequency_data.last_replenishment_date
        db.commit()
        db.refresh(existing)
        return existing
    else:
        new_frequency = models.ReplenishmentFrequency(
            product_id=frequency_data.product_id,
            store_id=frequency_data.store_id,
            replenishment_frequency=frequency_data.replenishment_frequency,
            last_replenishment_date=frequency_data.last_replenishment_date
        )
        db.add(new_frequency)
        db.commit()
        db.refresh(new_frequency)
        return new_frequency

@router.get("/replenishment-frequency", response_model=List[schemas.ReplenishmentFrequencyResponse])
def get_replenishment_frequencies(
    store_id: int = None,
    product_id: int = None,
    db: Session = Depends(database.get_db)
):
    """
    Get replenishment frequencies.
    Can filter by store_id and/or product_id.
    """
    query = db.query(models.ReplenishmentFrequency)

    if store_id is not None:
        query = query.filter(models.ReplenishmentFrequency.store_id == store_id)

    if product_id is not None:
        query = query.filter(models.ReplenishmentFrequency.product_id == product_id)

    frequencies = query.all()
    return frequencies

@router.get("/replenishment-frequency/{product_id}/{store_id}", response_model=schemas.ReplenishmentFrequencyResponse)
def get_replenishment_frequency(
    product_id: int,
    store_id: int,
    db: Session = Depends(database.get_db)
):
    """
    Get replenishment frequency for a specific product at a specific store.
    """
    frequency = db.query(models.ReplenishmentFrequency).filter(
        models.ReplenishmentFrequency.product_id == product_id,
        models.ReplenishmentFrequency.store_id == store_id
    ).first()

    if not frequency:
        raise HTTPException(
            status_code=404,
            detail=f"Replenishment frequency not found for product {product_id} at store {store_id}"
        )

    return frequency

@router.put("/replenishment-frequency/{product_id}/{store_id}", response_model=schemas.ReplenishmentFrequencyResponse)
def update_replenishment_frequency(
    product_id: int,
    store_id: int,
    frequency_update: schemas.ReplenishmentFrequencyUpdate,
    db: Session = Depends(database.get_db)
):
    """
    Update replenishment frequency for a specific product at a specific store.
    """

    if frequency_update.replenishment_frequency is not None:
        if not (1 <= frequency_update.replenishment_frequency <= 3):
            raise HTTPException(
                status_code=400,
                detail="Replenishment frequency must be between 1 and 3 days"
            )

    frequency = db.query(models.ReplenishmentFrequency).filter(
        models.ReplenishmentFrequency.product_id == product_id,
        models.ReplenishmentFrequency.store_id == store_id
    ).first()

    if not frequency:
        raise HTTPException(
            status_code=404,
            detail=f"Replenishment frequency not found for product {product_id} at store {store_id}"
        )

    if frequency_update.replenishment_frequency is not None:
        frequency.replenishment_frequency = frequency_update.replenishment_frequency
    if frequency_update.last_replenishment_date is not None:
        frequency.last_replenishment_date = frequency_update.last_replenishment_date

    db.commit()
    db.refresh(frequency)

    return frequency

@router.patch("/replenishment-frequency/{product_id}/{store_id}/replenish", response_model=schemas.ReplenishmentFrequencyResponse)
def record_replenishment(
    product_id: int,
    store_id: int,
    replenishment_data: Optional[schemas.ReplenishmentRecord] = Body(None),
    user_id: int = Body(...),
    batch_id: int = Body(...),
    expiration_date: date = Body(...),
    quantity: int = Body(...),
    db: Session = Depends(database.get_db)
):
    frequency = db.query(models.ReplenishmentFrequency).filter(
        models.ReplenishmentFrequency.product_id == product_id,
        models.ReplenishmentFrequency.store_id == store_id
    ).first()

    if not frequency:
        raise HTTPException(
            status_code=404,
            detail=f"Replenishment frequency not found for product {product_id} at store {store_id}"
        )

    replenishment_date = replenishment_data.replenishment_date if replenishment_data and replenishment_data.replenishment_date else date_class.today()
    frequency.last_replenishment_date = replenishment_date
    db.commit()
    db.refresh(frequency)

    log = models.ReplenishmentLog(
        product_id=product_id,
        store_id=store_id,
        batch_id=batch_id,
        expiration_date=expiration_date,
        quantity=quantity,
        user_id=user_id
    )
    db.add(log)
    db.commit()
    db.refresh(log)

    return frequency

@router.get("/replenishment-logs/{store_id}/{product_id}", response_model=List[schemas.ReplenishmentLogResponse])
def get_replenishment_logs(store_id: int, product_id: int, db: Session = Depends(database.get_db)):
    logs = db.query(models.ReplenishmentLog).filter(
        models.ReplenishmentLog.store_id == store_id,
        models.ReplenishmentLog.product_id == product_id
    ).order_by(models.ReplenishmentLog.timestamp.desc()).all()
    return logs

@router.delete("/replenishment-frequency/{product_id}/{store_id}")
def delete_replenishment_frequency(
    product_id: int,
    store_id: int,
    db: Session = Depends(database.get_db)
):
    """
    Delete replenishment frequency for a specific product at a specific store.
    """
    frequency = db.query(models.ReplenishmentFrequency).filter(
        models.ReplenishmentFrequency.product_id == product_id,
        models.ReplenishmentFrequency.store_id == store_id
    ).first()

    if not frequency:
        raise HTTPException(
            status_code=404,
            detail=f"Replenishment frequency not found for product {product_id} at store {store_id}"
        )

    db.delete(frequency)
    db.commit()

    return {"message": f"Replenishment frequency deleted for product {product_id} at store {store_id}"}

@router.get("/replenishment-list/{store_id}", response_model=List[schemas.ReplenishmentItem])
def get_daily_replenishment_list(
    store_id: int,
    db: Session = Depends(database.get_db)
):
    """
    Generate automated daily replenishment list for a store.
    Includes:
    1. Products that are out of stock (quantity = 0)
    2. Products where replenishment is due based on frequency
    """

    store = db.query(models.Store).filter(models.Store.store_id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail=f"Store with ID {store_id} not found")

    today = date_class.today()
    replenishment_items = []

    frequencies = db.query(models.ReplenishmentFrequency).filter(
        models.ReplenishmentFrequency.store_id == store_id
    ).all()

    frequency_product_ids = {f.product_id for f in frequencies}
    frequency_map = {f.product_id: f for f in frequencies}

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

    for product_id, frequency in frequency_map.items():
        product_name, current_stock = stock_map.get(product_id, (None, 0))

        if product_name is None:
            product = db.query(models.Product).filter(models.Product.product_id == product_id).first()
            if product:
                product_name = product.name
                current_stock = 0
            else:
                continue

        is_out_of_stock = current_stock == 0
        is_frequency_due = False
        next_replenishment_date = None

        if frequency.last_replenishment_date:
            days_since_replenishment = (today - frequency.last_replenishment_date).days
            is_frequency_due = days_since_replenishment >= frequency.replenishment_frequency
            if is_frequency_due:
                next_replenishment_date = frequency.last_replenishment_date + timedelta(days=frequency.replenishment_frequency)
        else:
            is_frequency_due = True

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

        quantity = None
        average_daily_sales = avg_sales_map.get(product_id, 0.0)

        if frequency.replenishment_frequency and average_daily_sales > 0:
            needed_stock = average_daily_sales * frequency.replenishment_frequency
            quantity = max(0, int(round(needed_stock - current_stock)))
        elif is_out_of_stock:
            quantity = None

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

    for product_id, (product_name, current_stock) in stock_map.items():
        if product_id not in frequency_product_ids and current_stock == 0:
            quantity = None
            average_daily_sales = avg_sales_map.get(product_id, 0.0)
            if average_daily_sales > 0:
                needed_stock = average_daily_sales * 3
                quantity = max(0, int(round(needed_stock - current_stock)))

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

    priority_order = {"high": 0, "medium": 1, "low": 2}
    replenishment_items.sort(key=lambda x: (priority_order.get(x.priority, 3), x.product_name))

    return replenishment_items

# ============================================================================
# Replenishment List Management Endpoints
# ============================================================================

@router.post("/replenishment-lists", response_model=schemas.ReplenishmentListResponse)
def create_replenishment_list(
    list_data: schemas.ReplenishmentListCreate,
    db: Session = Depends(database.get_db)
):
    """
    Create a new replenishment list.
    Can be created empty or generated from the automated daily list.
    """
    store = db.query(models.Store).filter(models.Store.store_id == list_data.store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail=f"Store with ID {list_data.store_id} not found")

    existing = db.query(models.ReplenishmentList).filter(
        models.ReplenishmentList.store_id == list_data.store_id,
        models.ReplenishmentList.list_date == list_data.list_date
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Replenishment list already exists for store {list_data.store_id} on {list_data.list_date}"
        )

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

@router.post("/replenishment-lists/generate/{store_id}", response_model=schemas.ReplenishmentListWithItems)
def generate_replenishment_list(
    store_id: int,
    list_date: Optional[date] = None,
    db: Session = Depends(database.get_db)
):
    """
    Generate a new replenishment list from the automated daily list.
    Creates the list and populates it with items from the daily replenishment calculation.
    """
    if list_date is None:
        list_date = date_class.today()

    store = db.query(models.Store).filter(models.Store.store_id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail=f"Store with ID {store_id} not found")

    existing = db.query(models.ReplenishmentList).filter(
        models.ReplenishmentList.store_id == store_id,
        models.ReplenishmentList.list_date == list_date
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Replenishment list already exists for store {store_id} on {list_date}"
        )

    automated_items = get_daily_replenishment_list(store_id, db)

    new_list = models.ReplenishmentList(
        store_id=store_id,
        list_date=list_date,
        status="draft",
        notes=f"Auto-generated on {date_class.today()}"
    )
    db.add(new_list)
    db.commit()
    db.refresh(new_list)

    list_items = []
    for item in automated_items:
        list_item = models.ReplenishmentListItem(
            list_id=new_list.list_id,
            product_id=item.product_id,
            quantity=item.quantity or 0,
            current_stock=item.current_stock,
            reason=item.reason,
            priority=item.priority,
            notes=None
        )
        db.add(list_item)
        list_items.append(list_item)

    db.commit()

    for item in list_items:
        db.refresh(item)
        product = db.query(models.Product).filter(models.Product.product_id == item.product_id).first()
        if product:
            item.product_name = product.name

    return schemas.ReplenishmentListWithItems(
        list_id=new_list.list_id,
        store_id=new_list.store_id,
        list_date=new_list.list_date,
        status=new_list.status,
        created_at=new_list.created_at,
        notes=new_list.notes,
        items=[
            schemas.ReplenishmentListItemResponse(
                item_id=item.item_id,
                list_id=item.list_id,
                product_id=item.product_id,
                product_name=getattr(item, 'product_name', None),
                quantity=item.quantity,
                current_stock=item.current_stock,
                reason=item.reason,
                priority=item.priority,
                notes=item.notes
            )
            for item in list_items
        ]
    )

@router.get("/replenishment-lists", response_model=List[schemas.ReplenishmentListResponse])
def get_replenishment_lists(
    store_id: Optional[int] = None,
    list_date: Optional[date] = None,
    status: Optional[str] = None,
    db: Session = Depends(database.get_db)
):
    """
    Get replenishment lists with optional filters.
    """
    query = db.query(models.ReplenishmentList)

    if store_id is not None:
        query = query.filter(models.ReplenishmentList.store_id == store_id)

    if list_date is not None:
        query = query.filter(models.ReplenishmentList.list_date == list_date)

    if status is not None:
        query = query.filter(models.ReplenishmentList.status == status)

    lists = query.order_by(models.ReplenishmentList.list_date.desc()).all()
    return lists

@router.get("/replenishment-lists/{store_id}/{list_date}", response_model=schemas.ReplenishmentListWithItems)
def get_replenishment_list(
    store_id: int,
    list_date: date,
    db: Session = Depends(database.get_db)
):
    """
    Get a specific replenishment list with all its items by store and date.
    """
    replenishment_list = db.query(models.ReplenishmentList).filter(
        models.ReplenishmentList.store_id == store_id,
        models.ReplenishmentList.list_date == list_date
    ).first()

    if not replenishment_list:
        raise HTTPException(
            status_code=404,
            detail=f"Replenishment list not found for store {store_id} on {list_date}"
        )

    items = db.query(models.ReplenishmentListItem).filter(
        models.ReplenishmentListItem.list_id == replenishment_list.list_id
    ).all()

    items_with_names = []
    for item in items:
        product = db.query(models.Product).filter(models.Product.product_id == item.product_id).first()
        items_with_names.append(schemas.ReplenishmentListItemResponse(
            item_id=item.item_id,
            list_id=item.list_id,
            product_id=item.product_id,
            product_name=product.name if product else None,
            quantity=item.quantity,
            current_stock=item.current_stock,
            reason=item.reason,
            priority=item.priority,
            notes=item.notes
        ))

    return schemas.ReplenishmentListWithItems(
        list_id=replenishment_list.list_id,
        store_id=replenishment_list.store_id,
        list_date=replenishment_list.list_date,
        status=replenishment_list.status,
        created_at=replenishment_list.created_at,
        notes=replenishment_list.notes,
        items=items_with_names
    )

@router.post("/replenishment-lists/{store_id}/{list_date}/items", response_model=schemas.ReplenishmentListItemResponse)
def add_replenishment_list_item(
    store_id: int,
    list_date: date,
    item_data: schemas.ReplenishmentListItemCreate,
    db: Session = Depends(database.get_db)
):
    """
    Add an item to a replenishment list.
    """
    replenishment_list = db.query(models.ReplenishmentList).filter(
        models.ReplenishmentList.store_id == store_id,
        models.ReplenishmentList.list_date == list_date
    ).first()

    if not replenishment_list:
        raise HTTPException(
            status_code=404,
            detail=f"Replenishment list not found for store {store_id} on {list_date}"
        )

    product = db.query(models.Product).filter(models.Product.product_id == item_data.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail=f"Product with ID {item_data.product_id} not found")

    existing = db.query(models.ReplenishmentListItem).filter(
        models.ReplenishmentListItem.list_id == replenishment_list.list_id,
        models.ReplenishmentListItem.product_id == item_data.product_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Product {item_data.product_id} already exists in this list"
        )

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

@router.put("/replenishment-lists/{store_id}/{list_date}/items/{product_id}", response_model=schemas.ReplenishmentListItemResponse)
def update_replenishment_list_item(
    store_id: int,
    list_date: date,
    product_id: int,
    item_update: schemas.ReplenishmentListItemUpdate,
    db: Session = Depends(database.get_db)
):
    """
    Update an item in a replenishment list (quantity, reason, priority, notes).
    Uses product_id to identify the item.
    """
    replenishment_list = db.query(models.ReplenishmentList).filter(
        models.ReplenishmentList.store_id == store_id,
        models.ReplenishmentList.list_date == list_date
    ).first()

    if not replenishment_list:
        raise HTTPException(
            status_code=404,
            detail=f"Replenishment list not found for store {store_id} on {list_date}"
        )

    item = db.query(models.ReplenishmentListItem).filter(
        models.ReplenishmentListItem.list_id == replenishment_list.list_id,
        models.ReplenishmentListItem.product_id == product_id
    ).first()

    if not item:
        raise HTTPException(
            status_code=404,
            detail=f"Product {product_id} not found in list for store {store_id} on {list_date}"
        )

    if item_update.quantity is not None:
        item.quantity = item_update.quantity
    if item_update.reason is not None:
        item.reason = item_update.reason
    if item_update.priority is not None:
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

@router.delete("/replenishment-lists/{store_id}/{list_date}/items/{product_id}")
def delete_replenishment_list_item(
    store_id: int,
    list_date: date,
    product_id: int,
    db: Session = Depends(database.get_db)
):
    """
    Remove an item from a replenishment list.
    Uses product_id to identify the item.
    """
    replenishment_list = db.query(models.ReplenishmentList).filter(
        models.ReplenishmentList.store_id == store_id,
        models.ReplenishmentList.list_date == list_date
    ).first()

    if not replenishment_list:
        raise HTTPException(
            status_code=404,
            detail=f"Replenishment list not found for store {store_id} on {list_date}"
        )

    item = db.query(models.ReplenishmentListItem).filter(
        models.ReplenishmentListItem.list_id == replenishment_list.list_id,
        models.ReplenishmentListItem.product_id == product_id
    ).first()

    if not item:
        raise HTTPException(
            status_code=404,
            detail=f"Product {product_id} not found in list for store {store_id} on {list_date}"
        )

    db.delete(item)
    db.commit()

    return {"message": f"Product {product_id} removed from list for store {store_id} on {list_date}"}

@router.put("/replenishment-lists/{store_id}/{list_date}", response_model=schemas.ReplenishmentListResponse)
def update_replenishment_list(
    store_id: int,
    list_date: date,
    status: Optional[str] = None,
    notes: Optional[str] = None,
    db: Session = Depends(database.get_db)
):
    """
    Update replenishment list status and/or notes.
    """
    replenishment_list = db.query(models.ReplenishmentList).filter(
        models.ReplenishmentList.store_id == store_id,
        models.ReplenishmentList.list_date == list_date
    ).first()

    if not replenishment_list:
        raise HTTPException(
            status_code=404,
            detail=f"Replenishment list not found for store {store_id} on {list_date}"
        )

    if status is not None:
        valid_statuses = ["draft", "completed", "cancelled"]
        if status not in valid_statuses:
            raise HTTPException(
                status_code=400,
                detail=f"Status must be one of: {', '.join(valid_statuses)}"
            )
        replenishment_list.status = status

    if notes is not None:
        replenishment_list.notes = notes

    db.commit()
    db.refresh(replenishment_list)

    return replenishment_list

@router.delete("/replenishment-lists/{store_id}/{list_date}")
def delete_replenishment_list(
    store_id: int,
    list_date: date,
    db: Session = Depends(database.get_db)
):
    """
    Delete a replenishment list and all its items.
    """
    replenishment_list = db.query(models.ReplenishmentList).filter(
        models.ReplenishmentList.store_id == store_id,
        models.ReplenishmentList.list_date == list_date
    ).first()

    if not replenishment_list:
        raise HTTPException(
            status_code=404,
            detail=f"Replenishment list not found for store {store_id} on {list_date}"
        )

    db.delete(replenishment_list)
    db.commit()

    return {"message": f"Replenishment list for store {store_id} on {list_date} deleted"}
