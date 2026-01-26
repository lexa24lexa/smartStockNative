from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_stock_movements():
    product_id = 1

    movement_data = {
        "product_id": product_id,
        "batch_id": 1,
        "quantity": 10,
        "origin_type": "SUPPLIER",
        "origin_id": None,
        "destination_type": "STORE",
        "destination_id": 1
    }
    create_resp = client.post("/stock/movements/", json=movement_data)
    assert create_resp.status_code == 200
    created_movement = create_resp.json()
    assert created_movement["product_id"] == product_id

    response = client.get(f"/stock/movements/{product_id}")
    assert response.status_code == 200
    movements = response.json()
    assert isinstance(movements, list)
    assert any(m["movement_id"] == created_movement["movement_id"] for m in movements)

    client.delete(f"/stock/movements/{created_movement['movement_id']}")
