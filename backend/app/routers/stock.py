from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from .. import models, schemas, database
from ..services.stock_service import (
    StockService,
    FIFOService,
)
from ..reports.stock_report import generate_stock_pdf_report, generate_stock_excel_report

router = APIRouter(prefix="/stock", tags=["Stock"])

@router.post("/", response_model=schemas.StockOut)
def create_stock(
    stock_in: schemas.StockCreate,
    db: Session = Depends(database.get_db)
):
    return StockService.create_stock(db, stock_in)

@router.put("/{stock_id}", response_model=schemas.StockOut)
def update_stock(
    stock_id: int,
    stock_in: schemas.StockUpdate,
    db: Session = Depends(database.get_db)
):
    return StockService.update_stock(db, stock_id, stock_in)

@router.delete("/{stock_id}", status_code=204)
def delete_stock(
    stock_id: int,
    db: Session = Depends(database.get_db)
):
    StockService.delete_stock(db, stock_id)

@router.get("/{store_id}", response_model=List[schemas.StockResponse])
def get_store_stock(
    store_id: int,
    db: Session = Depends(database.get_db)
):
    return StockService.get_store_stock(db, store_id)

@router.get("/{store_id}/product/{product_id}/batches", response_model=List[schemas.BatchStockResponse])
def get_product_batches_in_store(
    store_id: int,
    product_id: int,
    db: Session = Depends(database.get_db)
):
    return StockService.get_product_batches(db, store_id, product_id)

@router.get("/stock/daily-report")
def get_daily_stock_report(
    store_id: int,
    format: str = Query(..., description="Report format: 'pdf' or 'excel'"),
    report_date: Optional[date] = None,
    db: Session = Depends(database.get_db)
):
    store = StockService.get_store(db, store_id)
    if report_date is None:
        report_date = date.today()

    stock_data = StockService.get_store_stock_serialized(db, store_id)

    if format.lower() == 'pdf':
        buffer = generate_stock_pdf_report(stock_data, store.name, report_date)
        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=daily_stock_report_{report_date}.pdf"}
        )
    elif format.lower() == 'excel':
        buffer = generate_stock_excel_report(stock_data, store.name, report_date)
        return StreamingResponse(
            buffer,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=daily_stock_report_{report_date}.xlsx"}
        )
    else:
        raise HTTPException(status_code=400, detail="Format must be 'pdf' or 'excel'")

@router.get("/fifo-check")
def check_fifo_violation(
    store_id: int,
    product_id: int,
    selected_batch_id: int,
    db: Session = Depends(database.get_db)
):
    return FIFOService.check_fifo_violation(db, store_id, product_id, selected_batch_id)
