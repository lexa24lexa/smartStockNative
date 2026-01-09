from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date, timedelta
from .. import models, database

router = APIRouter()

@router.get("/alerts")
def get_alerts(db: Session = Depends(database.get_db)):
    
    STOCK_LIMIT = 10
    DAYS_TO_EXPIRE = 30

    today = date.today()
    expiration_threshold = today + timedelta(days=DAYS_TO_EXPIRE)

    alerts_response = {
        "low_stock": [],
        "expiring_soon": []
    }

    low_stock_items = db.query(models.Stock).filter(models.Stock.quantity < STOCK_LIMIT).all()
    
    for item in low_stock_items:
        product = db.query(models.Product).join(models.Batch).filter(models.Batch.batch_id == item.batch_id).first()
        store = db.query(models.Store).filter(models.Store.store_id == item.store_id).first()
        
        alerts_response["low_stock"].append({
            "product": product.name if product else "Unknown",
            "store": store.name if store else "Unknown",
            "current_quantity": item.quantity,
            "message": f"URGENT! Only {item.quantity} units remaining in {store.name if store else 'store'}"
        })

    expiring_batches = db.query(models.Batch).filter(
        models.Batch.expiration_date >= today,
        models.Batch.expiration_date <= expiration_threshold
    ).all()

    for batch in expiring_batches:
        product = db.query(models.Product).filter(models.Product.product_id == batch.product_id).first()
        
        alerts_response["expiring_soon"].append({
            "product": product.name if product else "Unknown",
            "batch_code": batch.batch_code,
            "expiration_date": batch.expiration_date,
            "message": f"Warning: Batch {batch.batch_code} expires on {batch.expiration_date}"
        })

    return alerts_response