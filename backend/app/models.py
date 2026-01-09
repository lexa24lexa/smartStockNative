from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date, DateTime
from sqlalchemy.sql import func
from .database import Base

class Category(Base):
    __tablename__ = "CATEGORY"
    category_id = Column(Integer, primary_key=True, index=True)
    category_name = Column(String(100))

class Address(Base):
    __tablename__ = "ADDRESS"
    address_id = Column(Integer, primary_key=True, index=True)
    street = Column(String(200))
    city = Column(String(100))
    country = Column(String(100))

class Supplier(Base):
    __tablename__ = "SUPPLIER"
    supplier_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    address_id = Column(Integer, ForeignKey("ADDRESS.address_id"))

class Store(Base):
    __tablename__ = "STORE"
    store_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    address_id = Column(Integer, ForeignKey("ADDRESS.address_id"))

class Product(Base):
    __tablename__ = "PRODUCT"
    product_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    unit_price = Column(Float)
    supplier_id = Column(Integer, ForeignKey("SUPPLIER.supplier_id"))
    category_id = Column(Integer, ForeignKey("CATEGORY.category_id"))

class Batch(Base):
    __tablename__ = "BATCH"
    batch_id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("PRODUCT.product_id"))
    batch_code = Column(String(50))
    expiration_date = Column(Date)

class Stock(Base):
    __tablename__ = "HAS_STOCK"
    stock_id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("STORE.store_id"))
    batch_id = Column(Integer, ForeignKey("BATCH.batch_id"))
    quantity = Column(Integer)

class Sale(Base):
    __tablename__ = "SALE"
    sale_id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, server_default=func.now())
    total_amount = Column(Float)
    store_id = Column(Integer, ForeignKey("STORE.store_id"))

class SaleLine(Base):
    __tablename__ = "SALE_LINE"
    line_id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("SALE.sale_id"))
    batch_id = Column(Integer, ForeignKey("BATCH.batch_id"))
    quantity = Column(Integer)
    subtotal = Column(Float)