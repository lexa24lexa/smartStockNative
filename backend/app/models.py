from datetime import datetime, date
from sqlalchemy import (
    Boolean, CheckConstraint, Column, Integer, String, Float, ForeignKey, Date, DateTime, UniqueConstraint
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base
from sqlalchemy import Enum
import enum

class Category(Base):
    __tablename__ = "CATEGORY"
    category_id = Column(Integer, primary_key=True, index=True)
    category_name = Column(String(100), nullable=False)

    products = relationship("Product", back_populates="category")

class Address(Base):
    __tablename__ = "ADDRESS"
    address_id = Column(Integer, primary_key=True, index=True)
    street = Column(String(200))
    city = Column(String(100))
    country = Column(String(100))

    suppliers = relationship("Supplier", back_populates="address")
    stores = relationship("Store", back_populates="address")

class Supplier(Base):
    __tablename__ = "SUPPLIER"
    supplier_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    address_id = Column(Integer, ForeignKey("ADDRESS.address_id"))

    address = relationship("Address", back_populates="suppliers")
    products = relationship("Product", back_populates="supplier")

class Store(Base):
    __tablename__ = "STORE"
    store_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    address_id = Column(Integer, ForeignKey("ADDRESS.address_id"))

    address = relationship("Address", back_populates="stores")
    stocks = relationship("Stock", back_populates="store")
    sales = relationship("Sale", back_populates="store")
    replenishment_lists = relationship("ReplenishmentList", back_populates="store")
    replenishment_frequencies = relationship("ReplenishmentFrequency", back_populates="store")
    replenishment_logs = relationship("ReplenishmentLog", back_populates="store")
    report_logs = relationship("ReportEmailLog", back_populates="store")

class Product(Base):
    __tablename__ = "PRODUCT"
    product_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    unit_price = Column(Float, nullable=False)
    supplier_id = Column(Integer, ForeignKey("SUPPLIER.supplier_id"), nullable=False)
    category_id = Column(Integer, ForeignKey("CATEGORY.category_id"), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    __table_args__ = (
        CheckConstraint('unit_price >= 0', name='check_unit_price_non_negative'),
    )

    supplier = relationship("Supplier", back_populates="products")
    category = relationship("Category", back_populates="products")
    batches = relationship("Batch", back_populates="product")
    stock_movements = relationship("StockMovement", back_populates="product")
    replenishment_frequencies = relationship("ReplenishmentFrequency", back_populates="product")
    replenishment_list_items = relationship("ReplenishmentListItem", back_populates="product")
    replenishment_logs = relationship("ReplenishmentLog", back_populates="product")

class Batch(Base):
    __tablename__ = "BATCH"
    batch_id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("PRODUCT.product_id"), nullable=False)
    batch_code = Column(String(50), nullable=False)
    expiration_date = Column(Date, nullable=True)

    __table_args__ = (
        UniqueConstraint('product_id', 'batch_code', name='uq_product_batch_code'),
    )

    product = relationship("Product", back_populates="batches")
    stocks = relationship("Stock", back_populates="batch")
    sale_lines = relationship("SaleLine", back_populates="batch")
    stock_movements = relationship("StockMovement", back_populates="batch")
    replenishment_logs = relationship("ReplenishmentLog", back_populates="batch")

class Stock(Base):
    __tablename__ = "HAS_STOCK"
    stock_id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("STORE.store_id"), nullable=False)
    batch_id = Column(Integer, ForeignKey("BATCH.batch_id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    reorder_level = Column(Integer, default=10, nullable=False)

    store = relationship("Store", back_populates="stocks")
    batch = relationship("Batch", back_populates="stocks")

    __table_args__ = (
        CheckConstraint("quantity >= 0", name="ck_stock_quantity_non_negative"),
        CheckConstraint("reorder_level >= 0", name="ck_stock_reorder_non_negative"),
        UniqueConstraint("store_id", "batch_id", name="uq_store_batch_stock"),
    )

class Sale(Base):
    __tablename__ = "SALE"
    sale_id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, server_default=func.now())
    total_amount = Column(Float)
    store_id = Column(Integer, ForeignKey("STORE.store_id"))

    store = relationship("Store", back_populates="sales")
    sale_lines = relationship("SaleLine", back_populates="sale")

class SaleLine(Base):
    __tablename__ = "SALE_LINE"
    line_id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("SALE.sale_id"))
    batch_id = Column(Integer, ForeignKey("BATCH.batch_id"))
    quantity = Column(Integer)
    subtotal = Column(Float)

    sale = relationship("Sale", back_populates="sale_lines")
    batch = relationship("Batch", back_populates="sale_lines")

class ReplenishmentFrequency(Base):
    __tablename__ = "REPLENISHMENT_FREQUENCY"
    frequency_id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("PRODUCT.product_id"), nullable=False)
    store_id = Column(Integer, ForeignKey("STORE.store_id"), nullable=False)
    replenishment_frequency = Column(Integer, nullable=False)  # dias (1-3)
    last_replenishment_date = Column(Date, nullable=True)

    __table_args__ = (UniqueConstraint('product_id', 'store_id', name='uq_product_store'),)

    product = relationship("Product", back_populates="replenishment_frequencies")
    store = relationship("Store", back_populates="replenishment_frequencies")

class ReplenishmentList(Base):
    __tablename__ = "REPLENISHMENT_LIST"
    list_id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("STORE.store_id"), nullable=False)
    list_date = Column(Date, nullable=False)
    status = Column(String(20), default="draft")
    created_at = Column(DateTime, server_default=func.now())
    notes = Column(String(500), nullable=True)

    store = relationship("Store", back_populates="replenishment_lists")
    items = relationship("ReplenishmentListItem", back_populates="replenishment_list")

class ReplenishmentListItem(Base):
    __tablename__ = "REPLENISHMENT_LIST_ITEM"
    item_id = Column(Integer, primary_key=True, index=True)
    list_id = Column(Integer, ForeignKey("REPLENISHMENT_LIST.list_id"), nullable=False)
    product_id = Column(Integer, ForeignKey("PRODUCT.product_id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    current_stock = Column(Integer, nullable=False)
    reason = Column(String(100), nullable=False)
    priority = Column(String(20), nullable=False)
    notes = Column(String(500), nullable=True)

    replenishment_list = relationship("ReplenishmentList", back_populates="items")
    product = relationship("Product", back_populates="replenishment_list_items")

class ReplenishmentLog(Base):
    __tablename__ = "REPLENISHMENT_LOG"
    log_id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("PRODUCT.product_id"), nullable=False)
    store_id = Column(Integer, ForeignKey("STORE.store_id"), nullable=False)
    batch_id = Column(Integer, ForeignKey("BATCH.batch_id"), nullable=False)
    expiration_date = Column(Date, nullable=False)
    quantity = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)
    timestamp = Column(DateTime, server_default=func.now())

    product = relationship("Product", back_populates="replenishment_logs")
    store = relationship("Store", back_populates="replenishment_logs")
    batch = relationship("Batch", back_populates="replenishment_logs")

class ReportEmailLog(Base):
    __tablename__ = "REPORT_EMAIL_LOG"
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, server_default=func.now())
    store_id = Column(Integer, ForeignKey("STORE.store_id"), nullable=True)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    recipients = Column(String(500), nullable=False)
    status = Column(String(30), nullable=False)
    message = Column(String(1000), nullable=True)

    store = relationship("Store", back_populates="report_logs")

class StockMovement(Base):
    __tablename__ = "STOCK_MOVEMENT"
    movement_id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("PRODUCT.product_id"), nullable=False)
    batch_id = Column(Integer, ForeignKey("BATCH.batch_id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    origin_type = Column(String(50), nullable=False)
    origin_id = Column(Integer, nullable=True)
    destination_type = Column(String(50), nullable=False)
    destination_id = Column(Integer, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="stock_movements")
    batch = relationship("Batch", back_populates="stock_movements")

class UserRole(str, enum.Enum):
    employee = "employee"
    manager = "manager"

class User(Base):
    __tablename__ = "USER"
    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    store_id = Column(Integer, ForeignKey("STORE.store_id"), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey("USER_ROLE.role_id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    store = relationship("Store")
