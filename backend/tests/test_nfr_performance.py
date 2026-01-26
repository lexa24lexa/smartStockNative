import time
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_report_latency():
    scenarios = [1,2,3,4,5]
    fast_count = 0
    for s in scenarios:
        start = time.time()
        client.get("/reports/daily?store_id=1")
        if time.time() - start <= 5:
            fast_count += 1
    assert fast_count / len(scenarios) >= 0.8
