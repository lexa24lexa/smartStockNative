from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_replenishment():
    store_id = 1
    product_id = 1
    response = client.get(f"/replenishment/{store_id}/{product_id}")
    assert response.status_code == 200

    data = response.json()
    assert "batch_id" in data
    assert "batch_code" in data
    assert "expiration_date" in data
    assert "quantity" in data
