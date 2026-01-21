from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, asc, desc

from app import models, schemas, database

router = APIRouter(prefix="/products", tags=["Products"])

# Get all active products with stock and facing
@router.get("", response_model=List[schemas.ProductResponse])
def get_products(sort: Optional[str] = None, db: Session = Depends(database.get_db)):
    query = (
        db.query(models.Product, func.sum(models.Stock.quantity).label("total_qty"))
        .join(models.Batch, models.Product.product_id == models.Batch.product_id)
        .join(models.Stock, models.Batch.batch_id == models.Stock.batch_id)
        .filter(models.Product.is_active)
        .group_by(models.Product.product_id)
    )
    if sort == "name_asc": query = query.order_by(asc(models.Product.name))
    elif sort == "name_desc": query = query.order_by(desc(models.Product.name))
    elif sort == "price_asc": query = query.order_by(asc(models.Product.unit_price))
    elif sort == "price_desc": query = query.order_by(desc(models.Product.unit_price))

    return [
        schemas.ProductResponse(
            product_id=p.product_id,
            name=p.name,
            unit_price=p.unit_price,
            supplier_id=p.supplier_id,
            category_id=p.category_id,
            quantity=int(total_qty or 0),
            facing=int((total_qty or 0) // 10)
        )
        for p, total_qty in query.all()
    ]

# Create a new product
@router.post("", response_model=schemas.ProductResponse)
def create_product(product: schemas.ProductCreate, db: Session = Depends(database.get_db)):
    if db.query(models.Product).filter(models.Product.name == product.name).first():
        raise HTTPException(400, f"Product '{product.name}' already exists")
    if not db.query(models.Supplier).filter(models.Supplier.supplier_id == product.supplier_id).first():
        raise HTTPException(400, "Supplier does not exist")
    if not db.query(models.Category).filter(models.Category.category_id == product.category_id).first():
        raise HTTPException(400, "Category does not exist")

    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    total_qty = db.query(func.sum(models.Stock.quantity))\
        .join(models.Batch, models.Batch.batch_id == models.Stock.batch_id)\
        .filter(models.Batch.product_id == db_product.product_id)\
        .scalar() or 0

    return schemas.ProductResponse(
        product_id=db_product.product_id,
        name=db_product.name,
        unit_price=db_product.unit_price,
        supplier_id=db_product.supplier_id,
        category_id=db_product.category_id,
        quantity=int(total_qty),
        facing=int(total_qty // 10)
    )

# Update existing product
@router.put("/{product_id}", response_model=schemas.ProductResponse)
def update_product(product_id: int, product: schemas.ProductCreate, db: Session = Depends(database.get_db)):
    db_product = db.query(models.Product).filter(models.Product.product_id == product_id).first()
    if not db_product: raise HTTPException(404, "Product not found")
    if db.query(models.Product).filter(models.Product.name == product.name, models.Product.product_id != product_id).first():
        raise HTTPException(400, f"Another product '{product.name}' exists")
    if not db.query(models.Supplier).filter(models.Supplier.supplier_id == product.supplier_id).first():
        raise HTTPException(400, "Supplier does not exist")
    if not db.query(models.Category).filter(models.Category.category_id == product.category_id).first():
        raise HTTPException(400, "Category does not exist")

    db_product.name = product.name
    db_product.unit_price = product.unit_price
    db_product.supplier_id = product.supplier_id
    db_product.category_id = product.category_id
    db.commit()
    db.refresh(db_product)
    return db_product

# Deactivate a product (soft delete)
@router.delete("/{product_id}", status_code=204)
def delete_product(product_id: int, db: Session = Depends(database.get_db)):
    db_product = db.query(models.Product).filter(models.Product.product_id == product_id).first()
    if not db_product: raise HTTPException(404, "Product not found")
    db_product.is_active = False
    db.commit()
    return {"detail": f"Product '{db_product.name}' deactivated"}
