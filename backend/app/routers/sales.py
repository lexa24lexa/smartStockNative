from fastapi import APIRouter, Depends, HTTPException, Response, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date, asc, nulls_last
from typing import List, Optional
from pydantic import BaseModel
from datetime import date, datetime
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill

from .. import models, database, schemas

router = APIRouter()

class SaleItemInput(BaseModel):
    product_id: int
    batch_id: Optional[int] = None
    quantity: int

class SaleInput(BaseModel):
    store_id: int
    items: List[SaleItemInput]

class SaleItemFIFOInput(BaseModel):
    product_id: int
    quantity: int
    selected_batch_id: Optional[int] = None

class SaleFIFOInput(BaseModel):
    store_id: int
    items: List[SaleItemFIFOInput]

class FIFOViolationCheckInput(BaseModel):
    store_id: int
    product_id: int
    selected_batch_id: int

def _fifo_batches_for_product(db: Session, store_id: int, product_id: int):
    """Return batches with stock > 0 in FIFO order (earliest expiration first)."""
    return (
        db.query(models.Batch, models.Stock)
        .join(models.Stock, models.Stock.batch_id == models.Batch.batch_id)
        .filter(models.Stock.store_id == store_id)
        .filter(models.Batch.product_id == product_id)
        .filter(models.Stock.quantity > 0)
        .order_by(
            models.Batch.expiration_date.is_(None),
            models.Batch.expiration_date.asc(),
            models.Batch.batch_id.asc()
        )
        .all()
    )

def _check_fifo_violation(db: Session, store_id: int, product_id: int, selected_batch_id: int):
    fifo_rows = _fifo_batches_for_product(db, store_id, product_id)

    if not fifo_rows:
        return {
            "is_violation": False,
            "message": "No stock available for this product in this store.",
            "expected_batch_id": None,
            "expected_batch_code": None,
        }

    expected = fifo_rows[0][0]

    if expected.batch_id == selected_batch_id:
        return {
            "is_violation": False,
            "message": "OK (FIFO respected).",
            "expected_batch_id": expected.batch_id,
            "expected_batch_code": expected.batch_code,
        }

    return {
        "is_violation": True,
        "message": "FIFO violation: selected batch is not the next FIFO batch.",
        "expected_batch_id": expected.batch_id,
        "expected_batch_code": expected.batch_code,
    }

@router.post("/sales")
def create_sale(sale_input: SaleInput, db: Session = Depends(database.get_db)):
    total_amount = 0
    new_sale = models.Sale(store_id=sale_input.store_id, total_amount=0)
    db.add(new_sale)
    db.commit()
    db.refresh(new_sale)

    try:
        for item in sale_input.items:
            stock_record = db.query(models.Stock).filter(
                models.Stock.store_id == sale_input.store_id,
                models.Stock.batch_id == item.batch_id
            ).first()

            if not stock_record or stock_record.quantity < item.quantity:
                raise HTTPException(status_code=400, detail=f"Insufficient stock for batch {item.batch_id}")

            stock_record.quantity -= item.quantity

            movement = models.StockMovement(
                product_id=product.product_id,
                batch_id=batch.batch_id,
                quantity=item.quantity,
                origin_type="Store",
                origin_id=new_sale.store_id,
                destination_type="Customer",
                destination_id=None
            )
            db.add(movement)

            batch = db.query(models.Batch).filter(models.Batch.batch_id == item.batch_id).first()
            product = db.query(models.Product).filter(models.Product.product_id == batch.product_id).first()
            
            subtotal = product.unit_price * item.quantity
            total_amount += subtotal

            sale_line = models.SaleLine(
                sale_id=new_sale.sale_id,
                batch_id=item.batch_id,
                quantity=item.quantity,
                subtotal=subtotal
            )
            db.add(sale_line)

        new_sale.total_amount = total_amount
        db.commit()
        
        return {"message": "Sale processed successfully", "sale_id": new_sale.sale_id, "total": total_amount}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@router.post("/sales/fifo")
def create_sale_fifo(payload: SaleFIFOInput, db: Session = Depends(database.get_db)):
    """FIFO enforced sales endpoint with safe checks."""
    if not payload.store_id:
        raise HTTPException(status_code=400, detail="store_id is required")
    if not payload.items or len(payload.items) == 0:
        raise HTTPException(status_code=400, detail="At least one sale item is required")

    total_amount = 0.0
    used_batches = []
    warnings = []

    new_sale = models.Sale(store_id=payload.store_id, total_amount=0)
    db.add(new_sale)
    db.commit()
    db.refresh(new_sale)

    try:
        for item in payload.items:
            if not item.product_id or item.quantity <= 0:
                warnings.append(f"Skipping invalid item: {item}")
                continue

            product = db.query(models.Product).filter(models.Product.product_id == item.product_id).first()
            if not product:
                warnings.append(f"Unknown product {item.product_id}, skipped.")
                continue

            fifo_rows = _fifo_batches_for_product(db, payload.store_id, item.product_id)
            if not fifo_rows:
                warnings.append(f"No stock available for product {item.product_id}, skipped.")
                continue

            remaining = item.quantity

            for batch, stock in fifo_rows:
                if remaining <= 0:
                    break

                take = min(stock.quantity, remaining)
                stock.quantity -= take

                movement = models.StockMovement(
                    product_id=product.product_id,
                    batch_id=batch.batch_id,
                    quantity=take,
                    origin_type="Store",
                    origin_id=new_sale.store_id,
                    destination_type="Customer",
                    destination_id=None
                )
                db.add(movement)

                remaining -= take

                subtotal = float(product.unit_price) * take
                total_amount += subtotal

                db.add(
                    models.SaleLine(
                        sale_id=new_sale.sale_id,
                        batch_id=batch.batch_id,
                        quantity=take,
                        subtotal=subtotal
                    )
                )

                used_batches.append({
                    "product_id": item.product_id,
                    "batch_id": batch.batch_id,
                    "batch_code": batch.batch_code,
                    "expiration_date": batch.expiration_date,
                    "quantity": take
                })

            if remaining > 0:
                warnings.append(
                    f"Insufficient stock for product {item.product_id} (missing {remaining})"
                )

        new_sale.total_amount = total_amount
        db.commit()

        return {
            "message": "Sale processed successfully (FIFO enforced, warnings possible)",
            "sale_id": new_sale.sale_id,
            "total": total_amount,
            "used_batches": used_batches,
            "warnings": warnings
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@router.get("/fifo/check")
def fifo_check(
    store_id: int,
    product_id: int,
    selected_batch_id: int,
    db: Session = Depends(database.get_db)
):
    """Check if a selected batch violates FIFO."""
    return _check_fifo_violation(db, store_id, product_id, selected_batch_id)

def generate_sales_pdf_report(sales_data: List, store_name: str, report_date: date, total_amount: float):
    """Generate PDF report for daily sales"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
        alignment=1
    )

    elements.append(Paragraph("Daily Sales Report", title_style))
    elements.append(Spacer(1, 0.2*inch))

    info_data = [
        ['Store:', store_name],
        ['Report Date:', report_date.strftime('%Y-%m-%d')],
        ['Total Sales:', f'€{total_amount:.2f}'],
        ['Total Transactions:', str(len(sales_data))]
    ]
    info_table = Table(info_data, colWidths=[2*inch, 4*inch])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 0.3*inch))

    if sales_data:
        table_data = [['Sale ID', 'Product', 'Quantity', 'Unit Price', 'Subtotal']]
        for sale in sales_data:
            table_data.append([
                str(sale['sale_id']),
                sale['product_name'],
                str(sale['quantity']),
                f"€{sale['unit_price']:.2f}",
                f"€{sale['subtotal']:.2f}"
            ])

        sales_table = Table(table_data, colWidths=[1*inch, 2.5*inch, 1*inch, 1.2*inch, 1.3*inch])
        sales_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        elements.append(sales_table)
    else:
        elements.append(Paragraph("No sales recorded for this date.", styles['Normal']))

    doc.build(elements)
    buffer.seek(0)
    return buffer

def generate_sales_excel_report(sales_data: List, store_name: str, report_date: date, total_amount: float):
    """Generate Excel report for daily sales"""
    wb = Workbook()
    ws = wb.active
    ws.title = "Daily Sales Report"

    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=12)
    title_font = Font(bold=True, size=16)

    ws['A1'] = "Daily Sales Report"
    ws['A1'].font = title_font
    ws.merge_cells('A1:E1')
    ws['A1'].alignment = Alignment(horizontal='center')

    ws['A3'] = "Store:"
    ws['B3'] = store_name
    ws['A4'] = "Report Date:"
    ws['B4'] = report_date.strftime('%Y-%m-%d')
    ws['A5'] = "Total Sales:"
    ws['B5'] = f'€{total_amount:.2f}'
    ws['A6'] = "Total Transactions:"
    ws['B6'] = len(sales_data)

    headers = ['Sale ID', 'Product', 'Quantity', 'Unit Price', 'Subtotal']
    for col, header in enumerate(headers, start=1):
        cell = ws.cell(row=8, column=col)
        cell.value = header
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center')

    for row_idx, sale in enumerate(sales_data, start=9):
        ws.cell(row=row_idx, column=1).value = sale['sale_id']
        ws.cell(row=row_idx, column=2).value = sale['product_name']
        ws.cell(row=row_idx, column=3).value = sale['quantity']
        ws.cell(row=row_idx, column=4).value = sale['unit_price']
        ws.cell(row=row_idx, column=5).value = sale['subtotal']

        ws.cell(row=row_idx, column=4).number_format = '€#,##0.00'
        ws.cell(row=row_idx, column=5).number_format = '€#,##0.00'

    ws.column_dimensions['A'].width = 12
    ws.column_dimensions['B'].width = 30
    ws.column_dimensions['C'].width = 12
    ws.column_dimensions['D'].width = 15
    ws.column_dimensions['E'].width = 15

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer

@router.get("/sales/daily-report")
def get_daily_sales_report(
    store_id: int,
    format: str = Query(..., description="Report format: 'pdf' or 'excel'"),
    report_date: Optional[date] = None,
    db: Session = Depends(database.get_db)
):
    report_format = format.lower()
    if report_format not in ['pdf', 'excel']:
        raise HTTPException(status_code=400, detail="Format must be 'pdf' or 'excel'")

    store = db.query(models.Store).filter(models.Store.store_id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail=f"Store with ID {store_id} not found")

    if report_date is None:
        report_date = date.today()

    start_datetime = datetime.combine(report_date, datetime.min.time())
    end_datetime = datetime.combine(report_date, datetime.max.time())

    sales = db.query(models.Sale).filter(
        models.Sale.store_id == store_id,
        models.Sale.date >= start_datetime,
        models.Sale.date <= end_datetime
    ).all()

    sales_data = []
    total_amount = 0.0

    for sale in sales:
        sale_lines = db.query(
            models.SaleLine,
            models.Product.name.label('product_name'),
            models.Product.unit_price
        ).join(
            models.Batch, models.Batch.batch_id == models.SaleLine.batch_id
        ).join(
            models.Product, models.Product.product_id == models.Batch.product_id
        ).filter(
            models.SaleLine.sale_id == sale.sale_id
        ).all()

        for sale_line, product_name, unit_price in sale_lines:
            sales_data.append({
                'sale_id': sale.sale_id,
                'product_name': product_name,
                'quantity': sale_line.quantity,
                'unit_price': unit_price,
                'subtotal': sale_line.subtotal
            })
            total_amount += sale_line.subtotal

    if report_format == 'pdf':
        buffer = generate_sales_pdf_report(sales_data, store.name, report_date, total_amount)
        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=daily_sales_report_{report_date}.pdf"}
        )
    else:
        buffer = generate_sales_excel_report(sales_data, store.name, report_date, total_amount)
        return StreamingResponse(
            buffer,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=daily_sales_report_{report_date}.xlsx"}
        )

@router.get("/sales/average-daily-sales-per-product", response_model=List[schemas.AverageDailySalesPerProduct])
def get_average_daily_sales_all_products(store_id: int, db: Session = Depends(database.get_db)):
    store = db.query(models.Store).filter(models.Store.store_id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail=f"Store with ID {store_id} not found")

    daily_sales = db.query(
        models.Batch.product_id,
        cast(models.Sale.date, Date).label('sale_date'),
        func.sum(models.SaleLine.quantity).label('daily_quantity')
    ).select_from(
        models.SaleLine
    ).join(
        models.Sale, models.Sale.sale_id == models.SaleLine.sale_id
    ).join(
        models.Batch, models.Batch.batch_id == models.SaleLine.batch_id
    ).filter(
        models.Sale.store_id == store_id
    ).group_by(
        models.Batch.product_id,
        cast(models.Sale.date, Date)
    ).subquery()

    results = db.query(
        models.Product.product_id,
        models.Product.name.label('product_name'),
        func.avg(daily_sales.c.daily_quantity).label('average_daily_sales'),
        func.count(daily_sales.c.sale_date).label('total_days_with_sales'),
        func.sum(daily_sales.c.daily_quantity).label('total_quantity_sold')
    ).join(
        daily_sales, models.Product.product_id == daily_sales.c.product_id
    ).group_by(
        models.Product.product_id,
        models.Product.name
    ).all()

    return [
        schemas.AverageDailySalesPerProduct(
            product_id=result.product_id,
            product_name=result.product_name,
            average_daily_sales=float(result.average_daily_sales) if result.average_daily_sales else 0.0,
            total_days_with_sales=result.total_days_with_sales or 0,
            total_quantity_sold=int(result.total_quantity_sold) if result.total_quantity_sold else 0
        )
        for result in results
    ]

@router.get("/sales/average-daily-sales-per-product/{product_id}", response_model=schemas.AverageDailySalesPerProduct)
def get_average_daily_sales_per_product(product_id: int, store_id: int, db: Session = Depends(database.get_db)):
    product = db.query(models.Product).filter(models.Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail=f"Product with ID {product_id} not found")

    store = db.query(models.Store).filter(models.Store.store_id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail=f"Store with ID {store_id} not found")

    daily_sales_data = db.query(
        cast(models.Sale.date, Date).label('sale_date'),
        func.sum(models.SaleLine.quantity).label('daily_quantity')
    ).select_from(
        models.SaleLine
    ).join(
        models.Sale, models.Sale.sale_id == models.SaleLine.sale_id
    ).join(
        models.Batch, models.Batch.batch_id == models.SaleLine.batch_id
    ).filter(
        models.Batch.product_id == product_id,
        models.Sale.store_id == store_id
    ).group_by(
        cast(models.Sale.date, Date)
    ).all()

    if not daily_sales_data:
        return schemas.AverageDailySalesPerProduct(
            product_id=product.product_id,
            product_name=product.name,
            average_daily_sales=0.0,
            total_days_with_sales=0,
            total_quantity_sold=0
        )

    total_days = len(daily_sales_data)
    total_quantity = sum(row.daily_quantity for row in daily_sales_data)
    average_daily = total_quantity / total_days if total_days > 0 else 0.0

    return schemas.AverageDailySalesPerProduct(
        product_id=product.product_id,
        product_name=product.name,
        average_daily_sales=float(average_daily),
        total_days_with_sales=total_days,
        total_quantity_sold=int(total_quantity)
    )
