from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date, timedelta
from .. import models, database

router = APIRouter()

# Placeholder for daily sales (used for stockout prediction)
def get_estimated_daily_sales(batch_id: int, db: Session) -> float:
    return 2.0  

@router.get("/alerts")
def get_alerts(db: Session = Depends(database.get_db)):
    DAYS_TO_EXPIRE = 30
    today = date.today()
    expiration_threshold = today + timedelta(days=DAYS_TO_EXPIRE)

    alerts_response = {
        "low_stock": [],
        "overstock": [],
        "expiring_soon": [],
        "stockout_prediction": []
    }

    for item in db.query(models.Stock).all():
        batch = db.query(models.Batch).filter(models.Batch.batch_id == item.batch_id).first()
        if not batch:
            continue

        product = db.query(models.Product).filter(models.Product.product_id == batch.product_id).first()
        store = db.query(models.Store).filter(models.Store.store_id == item.store_id).first()
        product_name = product.name if product else "Unknown"
        store_name = store.name if store else "Unknown"

        # Low stock if below reorder level
        if item.quantity <= item.reorder_level:
            alerts_response["low_stock"].append({
                "product": product_name,
                "store": store_name,
                "current_quantity": item.quantity,
                "reorder_level": item.reorder_level,
                "message": f"Stock ({item.quantity}) at or below reorder level ({item.reorder_level})"
            })

        # Overstock if more than 3x reorder level
        if item.quantity > (item.reorder_level * 3):
            alerts_response["overstock"].append({
                "product": product_name,
                "store": store_name,
                "current_quantity": item.quantity,
                "reorder_level": item.reorder_level,
                "message": f"Quantity ({item.quantity}) exceeds 3x reorder level"
            })

        # Expiring soon
        if batch.expiration_date and today <= batch.expiration_date <= expiration_threshold:
            alerts_response["expiring_soon"].append({
                "product": product_name,
                "batch_code": batch.batch_code,
                "expiration_date": batch.expiration_date,
                "message": f"Batch {batch.batch_code} expires soon ({batch.expiration_date})"
            })

        # Stockout prediction for next 7 days
        daily_sales = get_estimated_daily_sales(item.batch_id, db)
        if daily_sales > 0:
            days_left = item.quantity / daily_sales
            if days_left < 7:
                alerts_response["stockout_prediction"].append({
                    "product": product_name,
                    "store": store_name,
                    "days_remaining": round(days_left, 1),
                    "message": f"Stock will run out in {round(days_left, 1)} days"
                })

    return alerts_response
