from typing import List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, asc, desc

from app import models, schemas, database

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)

@router.get("", response_model=List[schemas.ProductResponse])
def get_products(
    sort: Optional[str] = None,
    db: Session = Depends(database.get_db)
):
    query = (
        db.query(
            models.Product,
            func.sum(models.Stock.quantity).label("total_qty")
        )
        .join(models.Batch, models.Product.product_id == models.Batch.product_id)
        .join(models.Stock, models.Batch.batch_id == models.Stock.batch_id)
        .group_by(models.Product.product_id)
    )

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
        final_qty = int(total_qty or 0)

        response.append(
            schemas.ProductResponse(
                product_id=product.product_id,
                name=product.name,
                unit_price=product.unit_price,
                supplier_id=product.supplier_id,
                category_id=product.category_id,
                quantity=final_qty,
                facing=final_qty // 10
            )
        )

    return response
