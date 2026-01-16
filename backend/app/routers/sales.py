from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date
from typing import List
from pydantic import BaseModel
from .. import models, database, schemas

router = APIRouter()

class SaleItemInput(BaseModel):
    batch_id: int
    quantity: int

class SaleInput(BaseModel):
    store_id: int
    items: List[SaleItemInput]

@router.post("/sales")
def create_sale(sale_input: SaleInput, db: Session = Depends(database.get_db)):
    
    total_amount = 0
    
    new_sale = models.Sale(store_id=sale_input.store_id, total_amount=0)
    db.add(new_sale)
    db.commit()
    db.refresh(new_sale)

    try:
        for item in sale_input.items:
            stock_record = db.query(models.Stock).filter(
                models.Stock.store_id == sale_input.store_id,
                models.Stock.batch_id == item.batch_id
            ).first()

            if not stock_record or stock_record.quantity < item.quantity:
                raise HTTPException(status_code=400, detail=f"Insufficient stock for batch {item.batch_id}")

            stock_record.quantity -= item.quantity

            batch = db.query(models.Batch).filter(models.Batch.batch_id == item.batch_id).first()
            product = db.query(models.Product).filter(models.Product.product_id == batch.product_id).first()
            
            subtotal = product.unit_price * item.quantity
            total_amount += subtotal

            sale_line = models.SaleLine(
                sale_id=new_sale.sale_id,
                batch_id=item.batch_id,
                quantity=item.quantity,
                subtotal=subtotal
            )
            db.add(sale_line)

        new_sale.total_amount = total_amount
        db.commit()
        
        return {"message": "Sale processed successfully", "sale_id": new_sale.sale_id, "total": total_amount}

    except Exception as e:
        db.rollback()
        raise e

@router.get("/sales/average-daily-sales-per-product", response_model=List[schemas.AverageDailySalesPerProduct])
def get_average_daily_sales_all_products(store_id: int, db: Session = Depends(database.get_db)):
    """
    Calculate and return average daily sales for all products at a specific store.
    For each product, calculates the average quantity sold per day across all days with sales.
    Returns products with sales data only.
    """

    store = db.query(models.Store).filter(models.Store.store_id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail=f"Store with ID {store_id} not found")

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

    results = db.query(
        models.Product.product_id,
        models.Product.name.label('product_name'),
        func.avg(daily_sales.c.daily_quantity).label('average_daily_sales'),
        func.count(daily_sales.c.sale_date).label('total_days_with_sales'),
        func.sum(daily_sales.c.daily_quantity).label('total_quantity_sold')
    ).join(
        daily_sales, models.Product.product_id == daily_sales.c.product_id
    ).group_by(
        models.Product.product_id,
        models.Product.name
    ).all()

    return [
        schemas.AverageDailySalesPerProduct(
            product_id=result.product_id,
            product_name=result.product_name,
            average_daily_sales=float(result.average_daily_sales) if result.average_daily_sales else 0.0,
            total_days_with_sales=result.total_days_with_sales or 0,
            total_quantity_sold=int(result.total_quantity_sold) if result.total_quantity_sold else 0
        )
        for result in results
    ]

@router.get("/sales/average-daily-sales-per-product/{product_id}", response_model=schemas.AverageDailySalesPerProduct)
def get_average_daily_sales_per_product(product_id: int, store_id: int, db: Session = Depends(database.get_db)):
    """
    Calculate and return average daily sales for a specific product at a specific store.
    Calculates the average quantity sold per day across all days with sales for the specified product.
    """

    product = db.query(models.Product).filter(models.Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail=f"Product with ID {product_id} not found")

    store = db.query(models.Store).filter(models.Store.store_id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail=f"Store with ID {store_id} not found")

    daily_sales_data = db.query(
        cast(models.Sale.date, Date).label('sale_date'),
        func.sum(models.SaleLine.quantity).label('daily_quantity')
    ).select_from(
        models.SaleLine
    ).join(
        models.Sale, models.Sale.sale_id == models.SaleLine.sale_id
    ).join(
        models.Batch, models.Batch.batch_id == models.SaleLine.batch_id
    ).filter(
        models.Batch.product_id == product_id,
        models.Sale.store_id == store_id
    ).group_by(
        cast(models.Sale.date, Date)
    ).all()

    if not daily_sales_data:
        return schemas.AverageDailySalesPerProduct(
            product_id=product.product_id,
            product_name=product.name,
            average_daily_sales=0.0,
            total_days_with_sales=0,
            total_quantity_sold=0
        )

    total_days = len(daily_sales_data)
    total_quantity = sum(row.daily_quantity for row in daily_sales_data)
    average_daily = total_quantity / total_days if total_days > 0 else 0.0

    return schemas.AverageDailySalesPerProduct(
        product_id=product.product_id,
        product_name=product.name,
        average_daily_sales=float(average_daily),
        total_days_with_sales=total_days,
        total_quantity_sold=int(total_quantity)
    )
