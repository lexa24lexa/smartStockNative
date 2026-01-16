from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from typing import Optional, List, Dict, Any
import io
import csv
import os
import smtplib
from email.message import EmailMessage
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from .. import models, database

router = APIRouter()

_scheduler = Optional[BackgroundScheduler] = None
_last_next_run: Optional[str] = None

def _month_range(year: int, month: int):
    if month < 1 or month > 12:
        raise HTTPException(status_code=400, detail="Invalid month")
    start = datetime(year, month, 1)
    if month == 12:
        end = datetime(year + 1, 1, 1)
    else:
        end = datetime(year, month + 1, 1)
    return start, end

def _build_monthly_report(db: Session, store_id: int, year: int, month: int) -> Dict[str, Any]:
    start, end = _month_range(year, month)

    sale_count = (
        db.query(func.count(models.Sale.sale_id))
        .filter(models.Sale.store_id == store_id)
        .filter(models.Sale.date >= start)
        .filter(models.Sale.date < end)
        .scalar()
    ) or 0

    total_items_sold = (
        db.query(func.coalesce(func.sum(models.Sale.total_amount), 0.0))
        .filter(models.Sale.store_id == store_id)
        .filter(models.Sale.date >= start)
        .filter(models.Sale.date < end)
        .scalar()
    ) or 0

    top_products_row = (
        db.query(
            models.Product.product_id,
            models.Product.name,
            func.sum(models.SaleLine.quantity).label("quantity_sold"),
            func.sum(models.SaleLine.subtotal).label("revenue"),
        )
        .join(models.Batch, models.Batch.product_id == models.Product.product_id)
        .join(models.SaleLine, models.SaleLine.batch_id == models.Batch.batch_id)
        .join(models.Sale, models.Sale.sale_id == models.SaleLine.sale_id)
        .filter(models.Sale.store_id == store_id)
        .filter(models.Sale.date >= start)
        .filter(models.Sale.date < end)
        .group_by(models.Product.product_id, models.Product.name)
        .order_by(func.sum(models.SaleLine.quantity).desc())
        .limit(10)
        .all()
    )

    top_products = [
        {
            "product_id": r.product_id,
            "name": r.name,
            "qty_sold": int(r.qty_sold or 0),
            "revenue": float(r.revenue or 0.0),
        }
        for r in top_products_rows
    ]

    return{
        "store_id": store_id,
        "year": year,
        "month": month,
        "period_start": start.isoformat(),
        "period_end": end.isoformat(),
        "sale_count": int(sale_count),
        "total_items_sold": int(total_items_sold),
        "total_revenue": float(total_revenue),
        "top_products": top_products,
    }

def _report_to_csv(report: Dict[str, Any]) -> str:
    out = io.StringIO()
    w = csv.writer(out)

    w.writerow(["Monthly Performance Report"])
    w.writerow(["store_id", report["store_id"]])
    w.writerow(["year", report["year"]])
    w.writerow(["month", report["month"]])
    w.writerow(["sale_count", report["sale_count"]])
    w.writerow(["total_items_sold", report["total_items_sold"]])
    w.writerow(["total_revenue", report["total_revenue"]])
    w.writerow([])

    w.writerow(["Top products (by qty)"])
    w.writerow(["product_id", "name", "qty_sold", "revenue"])
    for p in report["top_products"]:
        w.writerow([p["product_id"], p["name"], p["qty_sold"], p["revenue"]])

    return out.getvalue()

@router.get("/reports/monthly")
def get_monthly_report(
        store_id: int = Query(...),
        year: int = Query(...),
        month: int = Query(...),
        format: str = Query("json", pattern = "`(json|csv)$"),
        db: Session = Depends(database.get_db)
):
    report = _build_monthly_report(db, store_id, year, month)

    if format = "json":
        return report

    csv_text = _report_to_csv(report)
    filename = f"monthly_report_store{store_id}_{year}-{month}.csv"
    return StreamingResponse(
        io.StringIO(csv_text),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )

def _smtp_send_csv(subject: str, body: str, recipients: List[str], filename: str, csv_text: str):
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASS")
    sender = os.getenv("SMTP_FROM", user)

    if not host or not user or not password or not sender:
        raise RuntimeError("SMTP env vars missing: SMTP_HOST, SMTP_USER, SMTP_PASS, SMTP_FROM (and optional SMTP_PORT)")

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)
    msg.set_content(body)

    msg.add_attachment(csv_text.encode("utf-8"), maintype="text", subtype="csv", filename=filename)

    with smtplib.SMTP(host, port) as s:
        s.starttls()
        s.login(user, password)
        s.send_message(msg)

def _send_monthly_reports_job():
    from ..database import SessionLocal  # local import to avoid circulars
    db = SessionLocal()
    try:
        # previous month
        now = datetime.now()
        year = now.year
        month = now.month - 1
        if month == 0:
            month = 12
            year -= 1

        recipients_env = os.getenv("REPORT_RECIPIENTS", "")
        recipients = [r.strip() for r in recipients_env.split(",") if r.strip()]
        if not recipients:
            return

        stores = db.query(models.Store.store_id).all()
        for (store_id,) in stores:
            report = _build_monthly_report(db, store_id=store_id, year=year, month=month)
            csv_text = _report_to_csv(report)
            filename = f"monthly_report_store{store_id}_{year}-{month:02d}.csv"

            try:
                _smtp_send_csv(
                    subject=f"SmartStock Monthly Report - Store {store_id} - {year}-{month:02d}",
                    body="Attached is the monthly performance report (CSV).",
                    recipients=recipients,
                    filename=filename,
                    csv_text=csv_text
                )
                db.add(models.ReportEmailLog(
                    store_id=store_id,
                    year=year,
                    month=month,
                    recipients=", ".join(recipients),
                    status="success",
                    message="sent"
                ))
                db.commit()
            except Exception as e:
                db.add(models.ReportEmailLog(
                    store_id=store_id,
                    year=year,
                    month=month,
                    recipients=", ".join(recipients),
                    status="failed",
                    message=str(e)[:900]
                ))
                db.commit()
    finally:
        db.close()

def _ensure_scheduler_started():
    global _scheduler, _last_next_run
    if _scheduler is not None:
        return

    _scheduler = BackgroundScheduler()

    trigger = CronTrigger(day=1, hour=8, minute=0)
    job = _scheduler.add_job(_send_monthly_reports_job, trigger=trigger, id="send_monthly_reports", replace_existing=True)

    _scheduler.start()
    _last_next_run = job.next_run_time.isoformat() if job.next_run_time else None

@router.on_event("startup")
def reports_startup():
    _ensure_scheduler_started()

@router.get("/reports/email/status")
def email_status(db: Session = Depends(database.get_db)):
    logs = (
        db.query(models.ReportEmailLog)
        .order_by(models.ReportEmailLog.created_at.desc())
        .limit(20)
        .all()
    )

    return {
        "scheduler_running": _scheduler is not None,
        "next_run_time": _last_next_run,
        "last_logs": [
            {
                "created_at": l.created_at.isoformat() if l.created_at else None,
                "store_id": l.store_id,
                "year": l.year,
                "month": l.month,
                "recipients": l.recipients,
                "status": l.status,
                "message": l.message,
            }
            for l in logs
        ]
    }

@router.post("/reports/email/send-now")
def email_send_now(db: Session = Depends(database.get_db)):
    _send_monthly_reports_job()
    return {"message": "Triggered email job"}

