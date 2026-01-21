from datetime import date
from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException

from .. import models, schemas

class StockService:

    @staticmethod
    def get_store(db: Session, store_id: int):
        store = db.query(models.Store).filter(models.Store.store_id == store_id).first()
        if not store:
            raise HTTPException(status_code=404, detail=f"Store with ID {store_id} not found")
        return store

    @staticmethod
    def create_stock(db: Session, stock_in: schemas.StockCreate):
        store = StockService.get_store(db, stock_in.store_id)

        batch = db.query(models.Batch).filter(
            models.Batch.batch_id == stock_in.batch_id,
            models.Batch.is_active.is_(True)
        ).first()
        if not batch:
            raise HTTPException(status_code=404, detail="Batch not found or inactive")

        product = db.query(models.Product).filter(
            models.Product.product_id == batch.product_id,
            models.Product.is_active.is_(True)
        ).first()
        if not product:
            raise HTTPException(status_code=400, detail="Batch belongs to an inactive product")

        existing = db.query(models.Stock).filter(
            models.Stock.store_id == stock_in.store_id,
            models.Stock.batch_id == stock_in.batch_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Stock already exists for this batch in this store")

        stock = models.Stock(**stock_in.dict())
        db.add(stock)
        db.commit()
        db.refresh(stock)
        return stock

    @staticmethod
    def update_stock(db: Session, stock_id: int, stock_in: schemas.StockUpdate):
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
        stock = db.query(models.Stock).filter(models.Stock.stock_id == stock_id).first()
        if not stock:
            raise HTTPException(status_code=404, detail="Stock not found")
        db.delete(stock)
        db.commit()

    @staticmethod
    def get_store_stock(db: Session, store_id: int) -> List[schemas.StockResponse]:
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
        return [
            {'product_name': r.product_name, 'batch_code': r.batch_code, 'expiration_date': r.expiration_date, 'quantity': r.quantity}
            for r in StockService.get_store_stock(db, store_id)
        ]

    @staticmethod
    def get_product_batches(db: Session, store_id: int, product_id: int) -> List[schemas.BatchStockResponse]:
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

class FIFOService:

    @staticmethod
    def _fifo_batches_for_product(db: Session, store_id: int, product_id: int):
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
        fifo_rows = FIFOService._fifo_batches_for_product(db, store_id, product_id)
        if not fifo_rows:
            return {"is_violation": False, "message": "No stock available", "expected_batch_id": None, "expected_batch_code": None}

        expected = fifo_rows[0][0]
        if expected.batch_id == selected_batch_id:
            return {"is_violation": False, "message": "OK (FIFO respected)", "expected_batch_id": expected.batch_id, "expected_batch_code": expected.batch_code}

        return {"is_violation": True, "message": "FIFO violation: selected batch is not the next FIFO batch", "expected_batch_id": expected.batch_id, "expected_batch_code": expected.batch_code}
