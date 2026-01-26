from fastapi.testclient import TestClient
from app.main import app
from datetime import date

client = TestClient(app)

def test_get_reports():
    store_id = 1
    report_type = "daily"
    response = client.get(f"/reports/{report_type}?store_id={store_id}&format=json")
    assert response.status_code == 200

    data = response.json()
    expected_keys = ["store_id", "sale_count", "total_items_sold", "total_revenue", "top_products", "replenishment_efficiency_pct", "wastage"]
    for key in expected_keys:
        assert key in data

    assert isinstance(data["store_id"], int)
    assert isinstance(data["sale_count"], int)
    assert isinstance(data["total_revenue"], float)
    assert isinstance(data["top_products"], list)
