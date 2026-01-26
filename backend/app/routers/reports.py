from __future__ import annotations
import csv
import io
from datetime import datetime, date
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import func, desc
from sqlalchemy.orm import Session
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import xlsxwriter

from app import models, database

router = APIRouter(prefix="/reports", tags=["Reports"])

# Helpers
def _month_range(year: int, month: int):
    if month < 1 or month > 12:
        raise HTTPException(status_code=400, detail="month must be 1..12")
    start = datetime(year, month, 1)
    end = datetime(year + (month // 12), (month % 12) + 1, 1)
    return start, end

# Build Monthly Report
def _build_monthly_report(db: Session, store_id: int, year: int, month: int,
                          category_id: int | None = None, product_id: int | None = None) -> dict[str, Any]:
    start, end = _month_range(year, month)

    return _build_report(db, store_id, start, end, category_id, product_id, year=year, month=month)

# Build Daily Report
def _build_daily_report(db: Session, store_id: int, report_date: date,
                        category_id: int | None = None, product_id: int | None = None) -> dict[str, Any]:
    start = datetime.combine(report_date, datetime.min.time())
    end = datetime.combine(report_date, datetime.max.time())
    return _build_report(db, store_id, start, end, category_id, product_id, day=report_date.isoformat())

# Core Report Builder
def _build_report(db: Session, store_id: int, start: datetime, end: datetime,
                  category_id: int | None, product_id: int | None,
                  year: int | None = None, month: int | None = None,
                  day: str | None = None) -> dict[str, Any]:
    # Sales
    sale_count = db.query(func.count(models.Sale.sale_id))\
        .filter(models.Sale.store_id == store_id,
                models.Sale.date >= start, models.Sale.date <= end).scalar() or 0

    total_revenue = db.query(func.coalesce(func.sum(models.Sale.total_amount), 0.0))\
        .filter(models.Sale.store_id == store_id,
                models.Sale.date >= start, models.Sale.date <= end).scalar() or 0.0

    total_items_sold = db.query(func.coalesce(func.sum(models.SaleLine.quantity), 0))\
        .join(models.Sale, models.Sale.sale_id == models.SaleLine.sale_id)\
        .filter(models.Sale.store_id == store_id,
                models.Sale.date >= start, models.Sale.date <= end).scalar() or 0

    # Top Products
    top_query = db.query(
        models.Product.product_id, models.Product.name,
        func.sum(models.SaleLine.quantity).label("qty_sold"),
        func.sum(models.SaleLine.subtotal).label("revenue")
    ).join(models.Batch, models.Batch.product_id == models.Product.product_id)\
     .join(models.SaleLine, models.SaleLine.batch_id == models.Batch.batch_id)\
     .join(models.Sale, models.Sale.sale_id == models.SaleLine.sale_id)\
     .filter(models.Sale.store_id == store_id,
             models.Sale.date >= start, models.Sale.date <= end)

    if category_id:
        top_query = top_query.filter(models.Product.category_id == category_id)
    if product_id:
        top_query = top_query.filter(models.Product.product_id == product_id)

    top_products_rows = top_query.group_by(models.Product.product_id, models.Product.name)\
                                .order_by(desc("qty_sold")).limit(10).all()
    top_products = [{"product_id": r.product_id, "name": r.name,
                     "qty_sold": int(r.qty_sold or 0), "revenue": float(r.revenue or 0.0)}
                    for r in top_products_rows]

    # Replenishment
    planned = db.query(func.count(models.Replenishment.replenishment_id))\
        .filter(models.Replenishment.store_id == store_id,
                models.Replenishment.scheduled_date >= start,
                models.Replenishment.scheduled_date <= end).scalar() or 0

    actual = db.query(func.count(models.Replenishment.replenishment_id))\
        .filter(models.Replenishment.store_id == store_id,
                models.Replenishment.completed_date >= start,
                models.Replenishment.completed_date <= end).scalar() or 0

    replenishment_efficiency = round(actual / planned * 100, 1) if planned else None

    # Wastage
    wastage = db.query(func.coalesce(func.sum(models.Stock.quantity), 0))\
        .join(models.Batch, models.Batch.batch_id == models.Stock.batch_id)\
        .filter(models.Stock.store_id == store_id,
                models.Batch.expiration_date >= start,
                models.Batch.expiration_date <= end).scalar() or 0

    report = {
        "store_id": store_id,
        "sale_count": int(sale_count),
        "total_items_sold": int(total_items_sold),
        "total_revenue": float(total_revenue),
        "top_products": top_products,
        "replenishment_efficiency_pct": replenishment_efficiency,
        "wastage": int(wastage),
    }

    if year: report["year"] = year
    if month: report["month"] = month
    if day: report["day"] = day

    return report

# CSV Export
def _report_to_csv(report: dict[str, Any]) -> str:
    out = io.StringIO()
    w = csv.writer(out)
    title = "Monthly Performance Report" if "month" in report else "Daily Performance Report"
    w.writerow([title])
    for key in ["store_id","year","month","day","sale_count","total_items_sold","total_revenue","replenishment_efficiency_pct","wastage"]:
        if key in report:
            w.writerow([key, report[key]])
    w.writerow([])
    w.writerow(["Top Products"])
    w.writerow(["product_id","name","qty_sold","revenue"])
    for p in report["top_products"]:
        w.writerow([p["product_id"],p["name"],p["qty_sold"],p["revenue"]])
    return out.getvalue()

# Excel Export
def _report_to_excel(report: dict[str, Any]) -> bytes:
    buffer = io.BytesIO()
    workbook = xlsxwriter.Workbook(buffer)
    ws = workbook.add_worksheet("Report")

    title = "Monthly Report" if "month" in report else "Daily Report"
    ws.write(0, 0, f"{title} - Store {report['store_id']}")
    if "year" in report and "month" in report:
        ws.write(1, 0, f"Period: {report['year']}-{report['month']:02d}")
    elif "day" in report:
        ws.write(1, 0, f"Date: {report['day']}")

    metrics = ["sale_count","total_items_sold","total_revenue","replenishment_efficiency_pct","wastage"]
    ws.write(3, 0, "Metrics")
    for i, key in enumerate(metrics, start=4):
        ws.write(i, 0, key)
        ws.write(i, 1, report.get(key, ""))

    ws.write(10, 0, "Top Products")
    headers = ["product_id","name","qty_sold","revenue"]
    for col, h in enumerate(headers):
        ws.write(11, col, h)

    for row_idx, p in enumerate(report["top_products"], start=12):
        ws.write(row_idx, 0, p["product_id"])
        ws.write(row_idx, 1, p["name"])
        ws.write(row_idx, 2, p["qty_sold"])
        ws.write(row_idx, 3, p["revenue"])

    workbook.close()
    buffer.seek(0)
    return buffer.getvalue()

# PDF Export
def _report_to_pdf(report: dict[str, Any]) -> bytes:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    title = "Monthly Report" if "month" in report else "Daily Report"
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 750, f"{title} - Store {report['store_id']}")
    y = 730
    if "year" in report and "month" in report:
        c.drawString(50, y, f"Period: {report['year']}-{report['month']:02d}")
    elif "day" in report:
        c.drawString(50, y, f"Date: {report['day']}")
    y -= 20

    c.setFont("Helvetica", 12)
    for key in ["sale_count","total_items_sold","total_revenue","replenishment_efficiency_pct","wastage"]:
        c.drawString(50, y, f"{key}: {report.get(key,'N/A')}")
        y -= 15

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Top Products")
    y -= 15
    c.setFont("Helvetica", 12)
    c.drawString(50, y, "Product")
    c.drawString(250, y, "Qty Sold")
    c.drawString(350, y, "Revenue")
    y -= 15

    for p in report["top_products"]:
        c.drawString(50, y, p["name"])
        c.drawString(250, y, str(p["qty_sold"]))
        c.drawString(350, y, f"{p['revenue']:.2f}")
        y -= 15
        if y < 50:
            c.showPage()
            y = 750

    c.save()
    buffer.seek(0)
    return buffer.getvalue()

# Monthly Endpoint
@router.get("/monthly")
def get_monthly_report(
    store_id: int = Query(...),
    year: int | None = Query(None),
    month: int | None = Query(None),
    category_id: int | None = Query(None),
    product_id: int | None = Query(None),
    format: str = Query("json"),
    db: Session = Depends(database.get_db),
):
    now = datetime.now()
    year = year or now.year
    month = month or now.month
    report = _build_monthly_report(db, store_id, year, month, category_id, product_id)
    return _export_report(report, format)

# Daily Endpoint
@router.get("/daily")
def get_daily_report(
    store_id: int = Query(...),
    report_date: date = Query(default=date.today()),
    category_id: int | None = Query(None),
    product_id: int | None = Query(None),
    format: str = Query("json"),
    db: Session = Depends(database.get_db),
):
    report = _build_daily_report(db, store_id, report_date, category_id, product_id)
    return _export_report(report, format)

# Export Helper
def _export_report(report: dict[str, Any], format: str):
    fmt = format.lower()
    if fmt == "json":
        return report
    elif fmt == "csv":
        csv_text = _report_to_csv(report)
        filename = f"report_{report.get('store_id')}_{report.get('year','')}-{report.get('month','') or report.get('day','')}.csv"
        return StreamingResponse(io.StringIO(csv_text), media_type="text/csv",
                                 headers={"Content-Disposition": f'attachment; filename="{filename}"'})
    elif fmt in ["excel", "xlsx"]:
        excel_bytes = _report_to_excel(report)
        filename = f"report_{report.get('store_id')}_{report.get('year','')}-{report.get('month','') or report.get('day','')}.xlsx"
        return StreamingResponse(io.BytesIO(excel_bytes),
                                 media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                 headers={"Content-Disposition": f'attachment; filename="{filename}"'})
    elif fmt == "pdf":
        pdf_bytes = _report_to_pdf(report)
        filename = f"report_{report.get('store_id')}_{report.get('year','')}-{report.get('month','') or report.get('day','')}.pdf"
        return StreamingResponse(io.BytesIO(pdf_bytes), media_type="application/pdf",
                                 headers={"Content-Disposition": f'attachment; filename="{filename}"'})
    else:
        raise HTTPException(status_code=400, detail=f"Invalid format: {format}")
