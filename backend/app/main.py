from app.routers import analytics
from fastapi import FastAPI
from .database import engine, Base
from .routers import products
from .routers import products, stock
from .routers import products, stock, sales
from .routers import products, stock, sales, alerts

Base.metadata.create_all(bind=engine)

app = FastAPI(title="SmartStock API")

app.include_router(products.router, tags=["Products"])
app.include_router(stock.router, tags=["Stock"])
app.include_router(sales.router, tags=["Sales"])
app.include_router(alerts.router, tags=["Alerts"])
app.include_router(analytics.router)

@app.get("/")
def read_root():
    return {"message": "Bienvenido al Backend de SmartStock"}