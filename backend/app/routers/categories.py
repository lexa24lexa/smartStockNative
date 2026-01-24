from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import models, database

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.get("")
def get_categories(db: Session = Depends(database.get_db)):
    return db.query(models.Category).order_by(models.Category.category_name).all()
