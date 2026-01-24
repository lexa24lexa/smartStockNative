# stock_report.py
import io
from datetime import date
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import xlsxwriter
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

router = APIRouter()

# ---------- Report Generators ----------

def generate_stock_pdf_report(stock_data, store_name: str, report_date: date):
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
            f"{item['product_name']} | {item['batch_code']} | {item['expiration_date']} | Qty: {item['quantity']}"
        )
        y -= 20
        if y < 50:
            c.showPage()
            y = 750
    c.save()
    buffer.seek(0)
    return buffer

def generate_stock_excel_report(stock_data, store_name: str, report_date: date):
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
        worksheet.write(row_idx, 2, item['expiration_date'])
        worksheet.write(row_idx, 3, item['quantity'])
    workbook.close()
    buffer.seek(0)
    return buffer

# ---------- Example API Endpoint ----------

# Dummy stock data for testing
sample_stock_data = [
    {"product_name": "Product A", "batch_code": "B123", "expiration_date": "2026-02-28", "quantity": 50},
    {"product_name": "Product B", "batch_code": "B124", "expiration_date": "2026-03-15", "quantity": 20},
]

@router.get("/stock/{store_id}/daily-report")
def daily_report(store_id: int, report_date: date, format: str = "pdf"):
    store_name = f"Store {store_id}"

    if format.lower() == "pdf":
        buffer = generate_stock_pdf_report(sample_stock_data, store_name, report_date)
        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=report-{report_date}.pdf"}
        )

    elif format.lower() == "excel":
        buffer = generate_stock_excel_report(sample_stock_data, store_name, report_date)
        return StreamingResponse(
            buffer,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=report-{report_date}.xlsx"}
        )

    else:
        return {"error": "Invalid format. Use 'pdf' or 'excel'."}
