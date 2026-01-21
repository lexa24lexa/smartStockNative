from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas, database

router = APIRouter(
    prefix="/batches",
    tags=["Batches"]
)

@router.get("", response_model=List[schemas.BatchResponse])
def get_batches(
    product_id: Optional[int] = None,
    db: Session = Depends(database.get_db)
):
    query = db.query(models.Batch)

    if product_id:
        query = query.filter(models.Batch.product_id == product_id)

    return query.all()

@router.get("/{batch_id}", response_model=schemas.BatchResponse)
def get_batch(batch_id: int, db: Session = Depends(database.get_db)):
    batch = db.query(models.Batch).filter(models.Batch.batch_id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    return batch

@router.post("", response_model=schemas.BatchResponse, status_code=status.HTTP_201_CREATED)
def create_batch(batch: schemas.BatchCreate, db: Session = Depends(database.get_db)):

    product = db.query(models.Product).filter(
        models.Product.product_id == batch.product_id,
        models.Product.is_active.is_(True)
    ).first()

    if not product:
        raise HTTPException(
            status_code=400,
            detail="Product does not exist or is inactive"
        )

    existing = db.query(models.Batch).filter(
        models.Batch.product_id == batch.product_id,
        models.Batch.batch_code == batch.batch_code
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Batch code '{batch.batch_code}' already exists for this product"
        )

    if batch.expiration_date and batch.expiration_date < date.today():
        raise HTTPException(
            status_code=400,
            detail="Expiration date cannot be in the past"
        )

    db_batch = models.Batch(**batch.dict())
    db.add(db_batch)
    db.commit()
    db.refresh(db_batch)

    return db_batch

@router.patch("/{batch_id}", response_model=schemas.BatchResponse)
def update_batch(
    batch_id: int,
    batch: schemas.BatchUpdate,
    db: Session = Depends(database.get_db)
):
    db_batch = db.query(models.Batch).filter(models.Batch.batch_id == batch_id).first()
    if not db_batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    if batch.product_id:
        product = db.query(models.Product).filter(
            models.Product.product_id == batch.product_id,
            models.Product.is_active.is_(True)
        ).first()

        if not product:
            raise HTTPException(
                status_code=400,
                detail="Product does not exist or is inactive"
            )

    if batch.batch_code or batch.product_id:
        product_id = batch.product_id or db_batch.product_id
        batch_code = batch.batch_code or db_batch.batch_code

        existing = db.query(models.Batch).filter(
            models.Batch.product_id == product_id,
            models.Batch.batch_code == batch_code,
            models.Batch.batch_id != batch_id
        ).first()

        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Batch code '{batch_code}' already exists for this product"
            )

    if batch.expiration_date and batch.expiration_date < date.today():
        raise HTTPException(
            status_code=400,
            detail="Expiration date cannot be in the past"
        )

    for field, value in batch.dict(exclude_unset=True).items():
        setattr(db_batch, field, value)

    db.commit()
    db.refresh(db_batch)

    return db_batch

@router.delete("/{batch_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_batch(batch_id: int, db: Session = Depends(database.get_db)):
    db_batch = db.query(models.Batch).filter(models.Batch.batch_id == batch_id).first()
    if not db_batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    stock_exists = db.query(models.Stock).filter(
        models.Stock.batch_id == batch_id,
        models.Stock.quantity > 0
    ).first()

    if stock_exists:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete batch with existing stock"
        )

    db.delete(db_batch)
    db.commit()
