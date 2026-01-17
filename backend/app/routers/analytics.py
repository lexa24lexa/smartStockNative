from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from .. import models, database

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)

@router.get("/stock-vs-sales")
def get_stock_vs_sales(db: Session = Depends(database.get_db)):

    stock_results = db.query(
        models.Category.category_name,
        func.sum(models.Stock.quantity).label("total_stock")
    ).join(models.Product, models.Category.category_id == models.Product.category_id)\
     .join(models.Batch, models.Product.product_id == models.Batch.product_id)\
     .join(models.Stock, models.Batch.batch_id == models.Stock.batch_id)\
     .group_by(models.Category.category_name).all()

    sales_results = db.query(
        models.Category.category_name,
        func.sum(models.SaleLine.quantity).label("total_sales")
    ).join(models.Product, models.Category.category_id == models.Product.category_id)\
     .join(models.Batch, models.Product.product_id == models.Batch.product_id)\
     .join(models.SaleLine, models.Batch.batch_id == models.SaleLine.batch_id)\
     .group_by(models.Category.category_name).all()

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

@router.post("/generate-fake-sales")
def generate_fake_sales(db: Session = Depends(database.get_db)):
    import random
    from datetime import datetime
    
    batches = db.query(models.Batch).limit(5).all()
    if not batches:
        return {"error": "No batches found. Please create stock first."}

    new_sale = models.Sale(date=datetime.now(), total_amount=100.0)
    db.add(new_sale)
    db.commit()
    db.refresh(new_sale)

    for batch in batches:
        qty = random.randint(5, 50)
        line = models.SaleLine(
            sale_id=new_sale.sale_id,
            batch_id=batch.batch_id,
            quantity=qty,
        )
        db.add(line)
    
    db.commit()
    return {"message": "Fake sales data generated successfully"}