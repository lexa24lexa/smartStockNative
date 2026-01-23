from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, timedelta
import random
from app import models, database, schemas
from app.services.stock_service import StockService

router = APIRouter(prefix="/analytics", tags=["Analytics"])

# Stock vs sales per category
@router.get("/stock-vs-sales")
def get_stock_vs_sales(
    db: Session = Depends(database.get_db),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    category_id: Optional[int] = None
):
    """
    Returns total stock and total sales per category.
    """
    # Total stock per category
    stock_query = (
        db.query(
            models.Category.category_name,
            func.sum(models.Stock.quantity).label("total_stock")
        )
        .join(models.Product, models.Product.category_id == models.Category.category_id)
        .join(models.Batch, models.Batch.product_id == models.Product.product_id)
        .join(models.Stock, models.Stock.batch_id == models.Batch.batch_id)
    )

    if category_id:
        stock_query = stock_query.filter(models.Category.category_id == category_id)

    stock_results = stock_query.group_by(models.Category.category_name).all()

    # Total sales per category
    sales_query = (
        db.query(
            models.Category.category_name,
            func.sum(models.SaleLine.quantity).label("total_sales")
        )
        .join(models.Product, models.Product.category_id == models.Category.category_id)
        .join(models.Batch, models.Batch.product_id == models.Product.product_id)
        .join(models.SaleLine, models.SaleLine.batch_id == models.Batch.batch_id)
        .join(models.Sale, models.Sale.sale_id == models.SaleLine.sale_id)
    )

    if category_id:
        sales_query = sales_query.filter(models.Category.category_id == category_id)
    if start_date:
        sales_query = sales_query.filter(models.Sale.date >= start_date)
    if end_date:
        sales_query = sales_query.filter(models.Sale.date <= end_date)

    sales_results = sales_query.group_by(models.Category.category_name).all()

    # Combine stock and sales results
    report = {}
    for cat_name, qty in stock_results:
        report[cat_name] = {"category": cat_name, "stock": int(qty) if qty else 0, "sales": 0}
    for cat_name, qty in sales_results:
        if cat_name not in report:
            report[cat_name] = {"category": cat_name, "stock": 0, "sales": 0}
        report[cat_name]["sales"] = int(qty) if qty else 0

    return list(report.values())

# Total stock per category
@router.get("/stock-by-category", response_model=List[schemas.CategoryStock])
def stock_by_category(db: Session = Depends(database.get_db)):
    results = (
        db.query(
            models.Category.category_name.label("category"),
            func.sum(models.Stock.quantity).label("total_stock")
        )
        .join(models.Product, models.Product.category_id == models.Category.category_id)
        .join(models.Batch, models.Batch.product_id == models.Product.product_id)
        .join(models.Stock, models.Stock.batch_id == models.Batch.batch_id)
        .group_by(models.Category.category_name)
        .all()
    )

    return [
        {"category": r.category, "total_stock": int(r.total_stock) if r.total_stock else 0}
        for r in results
    ]

# Low stock items
@router.get("/low-stock", response_model=List[schemas.ReplenishmentItem])
def low_stock_items(store_id: int, db: Session = Depends(database.get_db)):
    items = (
        db.query(
            models.Product.product_id,
            models.Product.name.label("product_name"),
            func.sum(models.Stock.quantity).label("current_stock")
        )
        .join(models.Batch, models.Batch.product_id == models.Product.product_id)
        .join(models.Stock, models.Stock.batch_id == models.Batch.batch_id)
        .filter(models.Stock.store_id == store_id)
        .group_by(models.Product.product_id)
        .having(func.sum(models.Stock.quantity) < 50)
        .all()
    )

    return [
        {
            "product_id": r.product_id,
            "product_name": r.product_name,
            "current_stock": int(r.current_stock),
            "replenishment_frequency": None,
            "last_replenishment_date": None,
            "next_replenishment_date": None,
            "reason": "Low stock",
            "priority": "High",
            "quantity": None
        }
        for r in items
    ]


# Generate fake sales
@router.post("/generate-fake-sales")
def generate_fake_sales(db: Session = Depends(database.get_db)):
    batches = db.query(models.Batch).limit(5).all()
    if not batches:
        return {"error": "No batches found. Please create stock first."}

    created_count = 0
    for i in range(3):
        fake_date = datetime.now() - timedelta(days=i * 10)
        new_sale = models.Sale(date=fake_date, total_amount=100.0)
        db.add(new_sale)
        db.commit()
        db.refresh(new_sale)

        for batch in batches:
            qty = random.randint(1, 50)
            line = models.SaleLine(
                sale_id=new_sale.sale_id,
                batch_id=batch.batch_id,
                quantity=qty
            )
            db.add(line)

        created_count += 1

    db.commit()
    return {"message": f"Successfully generated {created_count} fake sales."}

# Stock predictions
@router.get("/predictions", response_model=schemas.StockPredictionsResponse)
def get_predictions(
    store_id: int = Query(..., gt=0),
    db: Session = Depends(database.get_db),
):
    return StockService.get_stock_predictions(db, store_id)
