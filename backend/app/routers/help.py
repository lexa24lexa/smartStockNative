# routers/help.py
from fastapi import APIRouter
from typing import Dict, Any

router = APIRouter()

METRICS_INFO: Dict[str, Dict[str, Any]] = {
    "average_daily_sales": {
        "title": "Average Daily Sales",
        "description": "The mean number of units sold per day over the selected period",
        "formula": "Total Sales / Number of Days",
        "example": "If 140 units sold in 7 days: 140/7 = 20 units/day",
        "category": "sales"
    },
    "minimum_stock": {
        "title": "Minimum Required Stock",
        "description": "The safety stock level to prevent stockouts based on sales velocity and replenishment time",
        "formula": "Average Daily Sales × Replenishment Frequency × Safety Factor",
        "example": "20 units/day × 2 days × 1.5 = 60 units",
        "category": "stock"
    },
    "fifo": {
        "title": "FIFO (First In, First Out)",
        "description": "Stock rotation method ensuring oldest batches are sold first to maintain product freshness",
        "why": "Reduces waste and ensures product quality",
        "category": "stock"
    },
    "product_facing": {
        "title": "Product Facing",
        "description": "Number of product units visible on the shelf front row",
        "formula": "Shelf Width / Product Width",
        "example": "90cm shelf / 6cm product = 15 facings",
        "category": "stock"
    },
    "stockout_prediction": {
        "title": "Stockout Prediction",
        "description": "Estimated time until stock reaches zero based on current sales velocity",
        "formula": "Current Stock / Average Daily Sales",
        "example": "30 units / 10 units/day = 3 days until stockout",
        "category": "predictions"
    },
    "replenishment_frequency": {
        "title": "Replenishment Frequency",
        "description": "How often new stock is ordered and delivered to the store",
        "options": ["Daily (1 day)", "Every 2 days", "Every 3 days"],
        "impact": "Lower frequency = higher minimum stock needed",
        "category": "settings"
    },
    "low_stock_alert": {
        "title": "Low Stock Alert",
        "description": "Warning when product quantity falls below the minimum required stock level",
        "threshold": "Triggered when: Current Stock < Minimum Stock",
        "action": "Consider immediate replenishment",
        "category": "alerts"
    },
    "expiring_soon": {
        "title": "Expiring Soon Alert",
        "description": "Warning for products approaching their expiration date",
        "threshold": "Products expiring within 30 days",
        "action": "Promote or discount to accelerate sales",
        "category": "alerts"
    },
    "batch_code": {
        "title": "Batch Code",
        "description": "Unique identifier for a specific production batch of a product",
        "purpose": "Enables traceability and FIFO enforcement",
        "category": "stock"
    },
    "stock_availability": {
        "title": "Stock Availability",
        "description": "Percentage of products currently in stock vs total product catalog",
        "formula": "(Products In Stock / Total Products) × 100",
        "example": "460 in stock / 500 total = 92%",
        "category": "dashboard"
    }
}

@router.get("/help")
def get_all_help():
    """Retourne toutes les informations d'aide"""
    return METRICS_INFO

@router.get("/help/{metric_key}")
def get_metric_help(metric_key: str):
    """Retourne l'information d'aide pour une métrique spécifique"""
    if metric_key in METRICS_INFO:
        return METRICS_INFO[metric_key]
    return {"error": "Metric not found"}, 404

@router.get("/help/category/{category}")
def get_help_by_category(category: str):
    """Retourne toutes les aides d'une catégorie (sales, stock, predictions, etc.)"""
    filtered = {
        key: value for key, value in METRICS_INFO.items() 
        if value.get("category") == category
    }
    return filtered