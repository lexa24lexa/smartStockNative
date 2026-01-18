from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date, timedelta
from .. import models, database

router = APIRouter()

# Helper function to simulate daily sales (FR01 dependency)
# In a real scenario, this would query the SALE_LINE table.
def get_estimated_daily_sales(batch_id: int, db: Session) -> float:
    # Placeholder: Returning a static value to enable FR05 logic
    return 2.0 

@router.get("/alerts")
def get_alerts(db: Session = Depends(database.get_db)):
    """
    FR17 - Inventory Dashboard Alerts:
    Returns lists of low stock, overstock, and expiring products.
    Includes FR05 (Stockout Prediction) warnings.
    """
    
    # Constants
    DAYS_TO_EXPIRE = 30
    
    today = date.today()
    expiration_threshold = today + timedelta(days=DAYS_TO_EXPIRE)

    alerts_response = {
        "low_stock": [],
        "overstock": [],       # Added for FR17
        "expiring_soon": [],
        "stockout_prediction": [] # Added for FR05
    }

    # Fetch all stock items
    all_stock_items = db.query(models.Stock).all()
    
    for item in all_stock_items:
        # Fetch related entities
        batch = db.query(models.Batch).filter(models.Batch.batch_id == item.batch_id).first()
        if not batch:
            continue
            
        product = db.query(models.Product).filter(models.Product.product_id == batch.product_id).first()
        store = db.query(models.Store).filter(models.Store.store_id == item.store_id).first()
        
        product_name = product.name if product else "Unknown"
        store_name = store.name if store else "Unknown"

        # --- FR02 & FR17: Low Stock Alert ---
        # Logic: If current quantity is below or equal to the reorder level defined for this store
        if item.quantity <= item.reorder_level:
            alerts_response["low_stock"].append({
                "product": product_name,
                "store": store_name,
                "current_quantity": item.quantity,
                "reorder_level": item.reorder_level,
                "message": f"URGENT: Stock ({item.quantity}) is at or below reorder level ({item.reorder_level})"
            })

        # --- FR17: Overstock Alert ---
        # Rule defined by user: Quantity > 3 * Reorder Level
        # This rule was manually added because it was missing in the comments/specs.
        if item.quantity > (item.reorder_level * 3):
             alerts_response["overstock"].append({
                "product": product_name,
                "store": store_name,
                "current_quantity": item.quantity,
                "reorder_level": item.reorder_level,
                "message": f"Overstock detected: Quantity ({item.quantity}) exceeds 3x reorder level"
            })

        # --- FR17: Expiration Alert ---
        if batch.expiration_date:
            if today <= batch.expiration_date <= expiration_threshold:
                 alerts_response["expiring_soon"].append({
                    "product": product_name,
                    "batch_code": batch.batch_code,
                    "expiration_date": batch.expiration_date,
                    "message": f"Warning: Batch {batch.batch_code} expires soon ({batch.expiration_date})"
                })

        # --- FR05: Stockout Prediction ---
        # Predict when stock will run out based on estimated daily sales
        daily_sales = get_estimated_daily_sales(item.batch_id, db)
        if daily_sales > 0:
            days_left = item.quantity / daily_sales
            if days_left < 7: # Warning if stock will run out in less than a week
                alerts_response["stockout_prediction"].append({
                    "product": product_name,
                    "store": store_name,
                    "days_remaining": round(days_left, 1),
                    "message": f"Prediction: Stock will run out in {round(days_left, 1)} days"
                })

    return alerts_response