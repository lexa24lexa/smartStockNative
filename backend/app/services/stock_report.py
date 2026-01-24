import io
from datetime import date, datetime
from typing import List, Dict
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import xlsxwriter
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app import database, models
from .email_service import send_stock_report_email

router = APIRouter()

# PDF Report Generation
def generate_stock_pdf_report(stock_data: List[Dict], store_name: str, report_date: date) -> io.BytesIO:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 750, f"Daily Stock Report - {store_name}")
    c.setFont("Helvetica", 12)
    c.drawString(50, 730, f"Date: {report_date}")

    y = 700
    for item in stock_data:
        c.drawString(
            50,
            y,
            f"{item['product_name']} | Batch: {item['batch_code']} | Exp: {item['expiration_date']} | Qty: {item['quantity']}"
        )
        y -= 20
        if y < 50:
            c.showPage()
            y = 750

    c.save()
    buffer.seek(0)
    return buffer

# Excel Report Generation
def generate_stock_excel_report(stock_data: List[Dict], store_name: str, report_date: date) -> io.BytesIO:
    buffer = io.BytesIO()
    workbook = xlsxwriter.Workbook(buffer)
    worksheet = workbook.add_worksheet("Stock Report")

    worksheet.write(0, 0, f"Daily Stock Report - {store_name}")
    worksheet.write(1, 0, f"Date: {report_date}")

    headers = ["Product", "Batch", "Expiration Date", "Quantity"]
    for col, header in enumerate(headers):
        worksheet.write(3, col, header)

    for row_idx, item in enumerate(stock_data, start=4):
        worksheet.write(row_idx, 0, item['product_name'])
        worksheet.write(row_idx, 1, item['batch_code'])
        worksheet.write(row_idx, 2, str(item['expiration_date']))
        worksheet.write(row_idx, 3, item['quantity'])

    workbook.close()
    buffer.seek(0)
    return buffer

# Database Query Function
def get_store_stock(db: Session, store_id: int) -> List[Dict]:
    rows = (
        db.query(
            models.Product.name.label("product_name"),
            models.Batch.batch_code,
            models.Batch.expiration_date,
            models.Stock.quantity
        )
        .join(models.Batch, models.Batch.product_id == models.Product.product_id)
        .join(models.Stock, models.Stock.batch_id == models.Batch.batch_id)
        .filter(models.Stock.store_id == store_id)
        .all()
    )
    stock_list = [
        {
            "product_name": r.product_name,
            "batch_code": r.batch_code,
            "expiration_date": r.expiration_date,
            "quantity": r.quantity,
        }
        for r in rows
    ]
    return stock_list

# API Endpoint
@router.get("/stock/{store_id}/daily-report")
def daily_stock_report(
    store_id: int,
    report_date: date = Query(default=date.today(), description="Date of the stock report"),
    format: str = Query(default="pdf", description="Report format: 'pdf' or 'excel'"),
    send_email: bool = Query(default=False, description="Whether to email the report to managers"),
    db: Session = Depends(database.get_db),
):
    store_name = f"Store {store_id}"
    stock_data = get_store_stock(db, store_id)

    # Generate report
    if format.lower() == "pdf":
        buffer = generate_stock_pdf_report(stock_data, store_name, report_date)
        filename = f"stock_report_{store_id}_{report_date}.pdf"
        media_type = "application/pdf"

    elif format.lower() in ("excel", "xlsx"):
        buffer = generate_stock_excel_report(stock_data, store_name, report_date)
        filename = f"stock_report_{store_id}_{report_date}.xlsx"
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    else:
        return {"error": "Invalid format. Use 'pdf' or 'excel'."}

    # Send email if requested
    if send_email:
        recipients = ["manager@example.com"]
        send_stock_report_email(buffer, filename, recipients)
        buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
