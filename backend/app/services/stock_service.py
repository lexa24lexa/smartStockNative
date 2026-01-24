from datetime import datetime
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException
from datetime import timezone

from .. import models, schemas

class StockService:

    @staticmethod
    def get_store(db: Session, store_id: int):
        # Fetch store, raise 404 if not found
        store = db.query(models.Store).filter(models.Store.store_id == store_id).first()
        if not store:
            raise HTTPException(status_code=404, detail=f"Store with ID {store_id} not found")
        return store

    @staticmethod
    def create_stock(db: Session, stock_in: schemas.StockCreate):
        # Ensure store exists
        store = StockService.get_store(db, stock_in.store_id)

        # Ensure batch exists and active
        batch = db.query(models.Batch).filter(
            models.Batch.batch_id == stock_in.batch_id,
            models.Batch.is_active.is_(True)
        ).first()
        if not batch:
            raise HTTPException(status_code=404, detail="Batch not found or inactive")

        # Ensure product is active
        product = db.query(models.Product).filter(
            models.Product.product_id == batch.product_id,
            models.Product.is_active.is_(True)
        ).first()
        if not product:
            raise HTTPException(status_code=400, detail="Batch belongs to an inactive product")

        # Check if stock already exists for this batch in this store
        existing = db.query(models.Stock).filter(
            models.Stock.store_id == stock_in.store_id,
            models.Stock.batch_id == stock_in.batch_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Stock already exists for this batch in this store")

        # Create stock
        stock = models.Stock(**stock_in.dict())
        db.add(stock)
        db.commit()
        db.refresh(stock)
        return stock

    @staticmethod
    def update_stock(db: Session, stock_id: int, stock_in: schemas.StockUpdate):
        # Update quantity or reorder level
        stock = db.query(models.Stock).filter(models.Stock.stock_id == stock_id).first()
        if not stock:
            raise HTTPException(status_code=404, detail="Stock not found")

        if stock_in.quantity is not None:
            stock.quantity = stock_in.quantity
        if stock_in.reorder_level is not None:
            stock.reorder_level = stock_in.reorder_level

        db.commit()
        db.refresh(stock)
        return stock

    @staticmethod
    def delete_stock(db: Session, stock_id: int):
        # Delete stock
        stock = db.query(models.Stock).filter(models.Stock.stock_id == stock_id).first()
        if not stock:
            raise HTTPException(status_code=404, detail="Stock not found")
        db.delete(stock)
        db.commit()

    @staticmethod
    def get_store_stock(db: Session, store_id: int) -> List[schemas.StockResponse]:
        # Fetch all stock in a store
        if store_id <= 0:
            raise HTTPException(status_code=400, detail="store_id must be positive")

        results = db.query(
            models.Product.name,
            models.Batch.batch_code,
            models.Batch.expiration_date,
            models.Stock.quantity
        ).join(models.Batch, models.Batch.product_id == models.Product.product_id)\
         .join(models.Stock, models.Stock.batch_id == models.Batch.batch_id)\
         .filter(models.Stock.store_id == store_id).all()

        return [
            schemas.StockResponse(
                product_name=r.name,
                batch_code=r.batch_code,
                expiration_date=r.expiration_date.strftime('%Y-%m-%d') if r.expiration_date else None,
                quantity=r.quantity
            )
            for r in results
        ]

    @staticmethod
    def get_store_stock_serialized(db: Session, store_id: int):
        # Return stock in dict format
        return [
            {
                'product_name': r.product_name,
                'batch_code': r.batch_code,
                'expiration_date': r.expiration_date,
                'quantity': r.quantity
            }
            for r in StockService.get_store_stock(db, store_id)
        ]

    @staticmethod
    def get_product_batches(db: Session, store_id: int, product_id: int) -> List[schemas.BatchStockResponse]:
        # Fetch all batches of a product in a store, ordered FIFO
        if store_id <= 0 or product_id <= 0:
            raise HTTPException(status_code=400, detail="store_id and product_id must be positive integers")

        results = db.query(
            models.Batch.batch_id,
            models.Batch.batch_code,
            models.Batch.expiration_date,
            models.Stock.quantity
        ).join(models.Stock, models.Stock.batch_id == models.Batch.batch_id)\
         .filter(models.Stock.store_id == store_id,
                 models.Batch.product_id == product_id,
                 models.Stock.quantity > 0)\
         .order_by(models.Batch.expiration_date.is_(None),
                   models.Batch.expiration_date.asc(),
                   models.Batch.batch_id.asc()).all()

        return [
            schemas.BatchStockResponse(
                batch_id=r.batch_id,
                batch_code=r.batch_code,
                expiration_date=r.expiration_date.strftime('%Y-%m-%d') if r.expiration_date else None,
                quantity=r.quantity
            )
            for r in results
        ]

    @staticmethod
    def get_stock_overview(db: Session, store_id: int) -> List[schemas.StockOverviewResponse]:
        """
        Returns stock overview per product including:
        - total quantity
        - status
        - progress
        - average daily sales
        - days to out-of-stock
        - last sale date
        - replenishment frequency & next replenishment
        - suggested quantity
        """
        stock_rows = (
            db.query(
                models.Product.product_id,
                models.Product.name,
                func.sum(models.Stock.quantity).label("total_quantity"),
                func.min(models.Stock.reorder_level).label("reorder_level"),
            )
            .join(models.Batch, models.Batch.product_id == models.Product.product_id)
            .join(models.Stock, models.Stock.batch_id == models.Batch.batch_id)
            .filter(models.Stock.store_id == store_id)
            .group_by(models.Product.product_id, models.Product.name)
            .all()
        )

        results = []

        for row in stock_rows:
            last_sale = (
                db.query(func.max(models.Sale.date))
                .join(models.SaleLine, models.Sale.sale_id == models.SaleLine.sale_id)
                .join(models.Batch, models.Batch.batch_id == models.SaleLine.batch_id)
                .filter(models.Batch.product_id == row.product_id,
                        models.Sale.store_id == store_id)
                .scalar()
            )

            total_sold = (
                db.query(func.sum(models.SaleLine.quantity))
                .join(models.Batch)
                .join(models.Sale)
                .filter(models.Batch.product_id == row.product_id,
                        models.Sale.store_id == store_id)
                .scalar() or 0
            )

            days_with_sales = (
                db.query(func.count(func.distinct(func.date(models.Sale.date))))
                .join(models.SaleLine)
                .join(models.Batch)
                .filter(models.Batch.product_id == row.product_id,
                        models.Sale.store_id == store_id)
                .scalar() or 1
            )

            avg_daily_sales = round(total_sold / days_with_sales, 2) if days_with_sales else 0

            days_to_oos = int(row.total_quantity / avg_daily_sales) if avg_daily_sales > 0 else None

            if row.total_quantity <= row.reorder_level:
                status = "Critical"
            elif row.total_quantity <= row.reorder_level * 2:
                status = "Low"
            else:
                status = "Stable"

            progress = min(row.total_quantity / (row.reorder_level * 3), 1)

            freq_record = (
                db.query(models.ReplenishmentFrequency)
                .filter(models.ReplenishmentFrequency.store_id == store_id,
                        models.ReplenishmentFrequency.product_id == row.product_id)
                .first()
            )

            replenishment_frequency = freq_record.replenishment_frequency if freq_record else None
            last_replenishment_date = freq_record.last_replenishment_date if freq_record else None
            next_replenishment_date = (
                last_replenishment_date + timedelta(days=replenishment_frequency)
                if last_replenishment_date and replenishment_frequency else None
            )

            suggested_qty = (
                int(avg_daily_sales * replenishment_frequency - row.total_quantity)
                if avg_daily_sales and replenishment_frequency else None
            )
            if suggested_qty is not None and suggested_qty < 0:
                suggested_qty = 0

            results.append(
                schemas.StockOverviewResponse(
                    product_id=row.product_id,
                    product_name=row.name,
                    total_quantity=row.total_quantity,
                    reorder_level=row.reorder_level,
                    status=status,
                    progress=progress,
                    average_daily_sales=avg_daily_sales,
                    days_to_out_of_stock=days_to_oos,
                    last_sale_at=last_sale,
                    replenishment_frequency=replenishment_frequency,
                    next_replenishment_date=next_replenishment_date,
                    quantity=suggested_qty
                )
            )

        return results

    @staticmethod
    def get_stock_predictions(db: Session, store_id: int):
        # Predict stock changes based on average sales
        overview = StockService.get_stock_overview(db, store_id)

        predictions = []
        next_restock_days = []

        for item in overview:
            if item.days_to_out_of_stock is None:
                continue

            predicted_change = (
                -100 * (7 / item.days_to_out_of_stock)
                if item.days_to_out_of_stock > 0
                else -100
            )

            days_until_restock = item.days_to_out_of_stock
            next_restock_days.append(days_until_restock)

            predictions.append(
                schemas.StockPredictionItem(
                    product_id=item.product_id,
                    product_name=item.product_name,
                    predicted_stock_change_pct=round(predicted_change, 1),
                    days_until_restock=days_until_restock,
                )
            )

        return schemas.StockPredictionsResponse(
            last_updated=datetime.now(timezone.utc),
            forecast_accuracy=0.89,
            next_restock_in_days=min(next_restock_days) if next_restock_days else None,
            predictions=predictions,
        )

class FIFOService:

    @staticmethod
    def _fifo_batches_for_product(db: Session, store_id: int, product_id: int):
        # Fetch batches ordered by FIFO
        return db.query(models.Batch, models.Stock)\
            .join(models.Stock, models.Stock.batch_id == models.Batch.batch_id)\
            .filter(models.Stock.store_id == store_id,
                    models.Batch.product_id == product_id,
                    models.Stock.quantity > 0)\
            .order_by(models.Batch.expiration_date.is_(None),
                      models.Batch.expiration_date.asc(),
                      models.Batch.batch_id.asc()).all()

    @staticmethod
    def check_fifo_violation(db: Session, store_id: int, product_id: int, selected_batch_id: int):
        # Check if selected batch respects FIFO
        fifo_rows = FIFOService._fifo_batches_for_product(db, store_id, product_id)
        if not fifo_rows:
            return {
                "is_violation": False,
                "message": "No stock available",
                "expected_batch_id": None,
                "expected_batch_code": None
            }

        expected = fifo_rows[0][0]
        if expected.batch_id == selected_batch_id:
            return {
                "is_violation": False,
                "message": "OK (FIFO respected)",
                "expected_batch_id": expected.batch_id,
                "expected_batch_code": expected.batch_code
            }

        return {
            "is_violation": True,
            "message": "FIFO violation: selected batch is not the next FIFO batch",
            "expected_batch_id": expected.batch_id,
            "expected_batch_code": expected.batch_code
        }
