from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, asc, desc
from typing import List, Optional
from .. import models, schemas, database

router = APIRouter()

@router.get("/products", response_model=List[schemas.ProductResponse])
def get_products(
    db: Session = Depends(database.get_db),
    search: Optional[str] = None, 
    sort: Optional[str] = None     
):
    query = db.query(
        models.Product,
        func.coalesce(func.sum(models.Stock.quantity), 0).label("total_qty")
    ).outerjoin(models.Batch, models.Product.product_id == models.Batch.product_id)\
     .outerjoin(models.Stock, models.Batch.batch_id == models.Stock.batch_id)

    if search:
        query = query.filter(models.Product.name.ilike(f"%{search}%"))

    query = query.group_by(models.Product.product_id)

    if sort:
        if sort == "name_asc":
            query = query.order_by(asc(models.Product.name))
        elif sort == "name_desc":
            query = query.order_by(desc(models.Product.name))
        elif sort == "price_asc":
            query = query.order_by(asc(models.Product.unit_price))
        elif sort == "price_desc":
            query = query.order_by(desc(models.Product.unit_price))

    results = query.all()
    
    response = []
    for product, total_qty in results:
        final_qty = int(total_qty)
        response.append(schemas.ProductResponse(
            product_id=product.product_id,
            name=product.name,
            unit_price=product.unit_price,
            supplier_id=product.supplier_id,
            category_id=product.category_id,
            quantity=final_qty,       
            facing=final_qty // 10    
        ))

    return response