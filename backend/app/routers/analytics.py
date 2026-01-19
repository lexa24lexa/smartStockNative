from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import datetime, timedelta
import random

from app import models, database

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)

@router.get("/stock-vs-sales")
def get_stock_vs_sales(
    db: Session = Depends(database.get_db),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    category_id: Optional[int] = None
):
    """Get stock vs sales report, optionally filtered by date range and category."""

    stock_query = db.query(
        models.Category.category_name,
        func.sum(models.Stock.quantity).label("total_stock")
    ).join(models.Product, models.Category.category_id == models.Product.category_id)\
     .join(models.Batch, models.Product.product_id == models.Batch.product_id)\
     .join(models.Stock, models.Batch.batch_id == models.Stock.batch_id)

    if category_id:
        stock_query = stock_query.filter(models.Category.category_id == category_id)

    stock_results = stock_query.group_by(models.Category.category_name).all()

    sales_query = db.query(
        models.Category.category_name,
        func.sum(models.SaleLine.quantity).label("total_sales")
    ).join(models.Product, models.Category.category_id == models.Product.category_id)\
     .join(models.Batch, models.Product.product_id == models.Batch.product_id)\
     .join(models.SaleLine, models.Batch.batch_id == models.SaleLine.batch_id)\
     .join(models.Sale, models.SaleLine.sale_id == models.Sale.sale_id)

    if category_id:
        sales_query = sales_query.filter(models.Category.category_id == category_id)

    if start_date:
        sales_query = sales_query.filter(models.Sale.date >= start_date)

    if end_date:
        sales_query = sales_query.filter(models.Sale.date <= end_date)

    sales_results = sales_query.group_by(models.Category.category_name).all()

    report = {}
    for cat_name, qty in stock_results:
        report[cat_name] = {
            "category": cat_name,
            "stock": int(qty) if qty else 0,
            "sales": 0
        }

    for cat_name, qty in sales_results:
        if cat_name not in report:
            report[cat_name] = {"category": cat_name, "stock": 0, "sales": 0}
        report[cat_name]["sales"] = int(qty) if qty else 0

    return list(report.values())

@router.get("/stock-by-category")
def get_stock_by_category(db: Session = Depends(database.get_db)):
    """Get total stock by category."""

    results = (
        db.query(
            models.Category.category_name,
            func.sum(models.Stock.quantity).label("total_stock")
        )
        .join(models.Product, models.Category.category_id == models.Product.category_id)
        .join(models.Batch, models.Product.product_id == models.Batch.product_id)
        .join(models.Stock, models.Batch.batch_id == models.Stock.batch_id)
        .group_by(models.Category.category_name)
        .all()
    )

    return [
        {
            "category": category_name,
            "total_stock": total_stock or 0
        }
        for category_name, total_stock in results
    ]

@router.post("/generate-fake-sales")
def generate_fake_sales(db: Session = Depends(database.get_db)):
    """
    Generates fake sales data with different dates to test analytics and reports.
    Creates 3 sales, each with up to 5 batches, random quantities.
    """
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
    return {"message": f"Successfully generated {created_count} fake sales with different dates."}
