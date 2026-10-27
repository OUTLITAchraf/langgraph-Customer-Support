from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_support_endpoint_rejects_empty_message():
    response = client.post(
        "/support",
        json={"customer_message": "   "},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Customer message cannot be empty."