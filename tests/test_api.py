from fastapi.testclient import TestClient
from api.main import app


def test_api_validation_paths():
    client = TestClient(app)

    # missing title in knowledge.data should fail
    payload = {"id": "K-010", "domain": "Knowledge", "data": {"foo": "bar"}}
    r = client.post("/knowledge", json=payload)
    assert r.status_code == 400
    assert r.json()["status"] == "FAIL"

    # good knowledge
    payload2 = {"id": "K-011", "domain": "Knowledge", "data": {"title": "T"}}
    r2 = client.post("/knowledge", json=payload2)
    assert r2.status_code == 200
    assert r2.json()["status"] == "success"
