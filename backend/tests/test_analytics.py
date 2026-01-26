from fastapi.testclient import TestClient
from app.main import app
from datetime import datetime

client = TestClient(app)

# Dashboard: GET /analytics/stock-by-category
def test_stock_by_category():
    response = client.get("/analytics/stock-by-category")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# Predictions: GET /analytics/predictions?store_id={STORE_ID}
def test_predictions():
    store_id = 1
    response = client.get(f"/analytics/predictions?store_id={store_id}")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, dict)
    assert "last_updated" in data
    assert "forecast_accuracy" in data
    assert "predictions" in data
    assert isinstance(data["predictions"], list)

    # Optional: check each prediction item has the required fields
    for item in data["predictions"]:
        assert "product_id" in item
        assert "product_name" in item
        assert "predicted_stock_change_pct" in item
        assert "days_until_restock" in item
