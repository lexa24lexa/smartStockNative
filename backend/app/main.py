from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .services import stock_report
from .database import engine, Base
from .routers import products, stock, sales, batches, alerts, reports, analytics, replenishment, users

Base.metadata.create_all(bind=engine)

app = FastAPI(title="SmartStock API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products.router, tags=["Products"])
app.include_router(stock.router, tags=["Stock"])
app.include_router(sales.router, tags=["Sales"])
app.include_router(batches.router, tags=["Batches"])
app.include_router(alerts.router, tags=["Alerts"])
app.include_router(reports.router, tags=["Reports"])
app.include_router(stock_report.router, tags=["Stock Reports"])
app.include_router(analytics.router, tags=["Analytics"])
app.include_router(replenishment.router, tags=["Replenishment"])
app.include_router(users.router, tags=["Users"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the SmartStock API"}
