from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from .. import models, schemas, database
from ..services.stock_service import StockService, FIFOService
from ..reports.stock_report import generate_stock_pdf_report, generate_stock_excel_report

# Stock router
router = APIRouter(prefix="/stock", tags=["Stock"])

# Create a new stock entry
@router.post("", response_model=schemas.StockOut)
def create_stock(stock_in: schemas.StockCreate, db: Session = Depends(database.get_db)):
    return StockService.create_stock(db, stock_in)

# Update stock entry
@router.put("/{stock_id}", response_model=schemas.StockOut)
def update_stock(stock_id: int, stock_in: schemas.StockUpdate, db: Session = Depends(database.get_db)):
    return StockService.update_stock(db, stock_id, stock_in)

# Delete stock entry
@router.delete("/{stock_id}", status_code=204)
def delete_stock(stock_id: int, db: Session = Depends(database.get_db)):
    StockService.delete_stock(db, stock_id)

# Get stock for a store
@router.get("/{store_id}", response_model=List[schemas.StockResponse])
def get_store_stock(store_id: int, db: Session = Depends(database.get_db)):
    return StockService.get_store_stock(db, store_id)

# Get product batches in a store
@router.get("/{store_id}/product/{product_id}/batches", response_model=List[schemas.BatchStockResponse])
def get_product_batches_in_store(store_id: int, product_id: int, db: Session = Depends(database.get_db)):
    return StockService.get_product_batches(db, store_id, product_id)

# Daily stock report (pdf/excel)
@router.get("/daily-report")
def get_daily_stock_report(
    store_id: int,
    format: str = Query(..., description="Report format: 'pdf' or 'excel'"),
    report_date: Optional[date] = None,
    db: Session = Depends(database.get_db)
):
    store = StockService.get_store(db, store_id)
    report_date = report_date or date.today()
    stock_data = StockService.get_store_stock_serialized(db, store_id)

    if format.lower() == "pdf":
        buffer = generate_stock_pdf_report(stock_data, store.name, report_date)
        return StreamingResponse(buffer, media_type="application/pdf",
                                 headers={"Content-Disposition": f"attachment; filename=daily_stock_report_{report_date}.pdf"})
    elif format.lower() == "excel":
        buffer = generate_stock_excel_report(stock_data, store.name, report_date)
        return StreamingResponse(buffer, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                 headers={"Content-Disposition": f"attachment; filename=daily_stock_report_{report_date}.xlsx"})
    raise HTTPException(status_code=400, detail="Format must be 'pdf' or 'excel'")

# FIFO violation check
@router.get("/fifo-check")
def check_fifo_violation(store_id: int, product_id: int, selected_batch_id: int, db: Session = Depends(database.get_db)):
    return FIFOService.check_fifo_violation(db, store_id, product_id, selected_batch_id)

ALLOWED_TYPES = ["STORE", "BATCH", "SUPPLIER"]

# Check if entity exists
def check_entity_exists(db: Session, entity_type: str, entity_id: int):
    model_map = {"STORE": models.Store, "BATCH": models.Batch, "SUPPLIER": models.Supplier}
    entity = db.query(model_map.get(entity_type, None)).filter(getattr(model_map[entity_type], f"{entity_type.lower()}_id") == entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail=f"{entity_type} with id {entity_id} not found")

# Validate stock movement before commit
def validate_stock_movement(db: Session, movement: schemas.StockMovementCreate):
    if movement.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be greater than 0")
    if movement.origin_type not in ALLOWED_TYPES or movement.destination_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Invalid origin or destination type")
    if movement.origin_id:
        check_entity_exists(db, movement.origin_type, movement.origin_id)
    if movement.destination_id:
        check_entity_exists(db, movement.destination_type, movement.destination_id)

    # Check stock at origin
    origin_stock = 0
    if movement.origin_type == "STORE" and movement.origin_id:
        stock_entry = db.query(models.Stock).filter(
            models.Stock.store_id == movement.origin_id,
            models.Stock.product_id == movement.product_id,
            models.Stock.batch_id == movement.batch_id
        ).first()
        origin_stock = stock_entry.quantity if stock_entry else 0
    elif movement.origin_type == "BATCH" and movement.origin_id:
        batch_stock = db.query(models.Stock).filter(
            models.Stock.batch_id == movement.origin_id,
            models.Stock.product_id == movement.product_id
        ).first()
        origin_stock = batch_stock.quantity if batch_stock else 0

    if movement.origin_type != "SUPPLIER" and movement.quantity > origin_stock:
        raise HTTPException(status_code=400, detail="Not enough stock at origin")

# Create stock movement
@router.post("/movements/", response_model=schemas.StockMovementResponse)
def create_stock_movement(movement: schemas.StockMovementCreate, db: Session = Depends(database.get_db)):
    validate_stock_movement(db, movement)
    db_movement = models.StockMovement(**movement.dict())
    db.add(db_movement)
    db.commit()
    db.refresh(db_movement)
    return db_movement

# Get stock movements for a product
@router.get("/movements/{product_id}", response_model=List[schemas.StockMovementResponse])
def get_stock_movements(product_id: int, db: Session = Depends(database.get_db)):
    return db.query(models.StockMovement).filter(models.StockMovement.product_id == product_id).all()

# Update stock movement
@router.put("/movements/{movement_id}", response_model=schemas.StockMovementResponse)
def update_stock_movement(movement_id: int, movement: schemas.StockMovementCreate, db: Session = Depends(database.get_db)):
    db_movement = db.query(models.StockMovement).filter(models.StockMovement.movement_id == movement_id).first()
    if not db_movement:
        raise HTTPException(status_code=404, detail="Stock movement not found")
    validate_stock_movement(db, movement)
    for key, value in movement.dict().items():
        setattr(db_movement, key, value)
    db.commit()
    db.refresh(db_movement)
    return db_movement

# Delete stock movement
@router.delete("/movements/{movement_id}")
def delete_stock_movement(movement_id: int, db: Session = Depends(database.get_db)):
    db_movement = db.query(models.StockMovement).filter(models.StockMovement.movement_id == movement_id).first()
    if not db_movement:
        raise HTTPException(status_code=404, detail="Stock movement not found")
    db.delete(db_movement)
    db.commit()
    return {"detail": "Stock movement deleted"}
