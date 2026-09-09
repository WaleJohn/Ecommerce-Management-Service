from fastapi.testclient import TestClient

from app.main import app
from app.repository import store


client = TestClient(app)


def setup_function() -> None:
    store.reset()


def create_user() -> dict:
    response = client.post(
        "/users",
        json={"email": "ada@example.com", "full_name": "Ada Lovelace"},
    )
    assert response.status_code == 201
    return response.json()


def create_order(user_id: str) -> dict:
    response = client.post(
        "/orders",
        json={
            "user_id": user_id,
            "items": [
                {"sku": "SKU-1", "name": "Keyboard", "quantity": 2, "unit_price": 49.99},
                {"sku": "SKU-2", "name": "Mouse", "quantity": 1, "unit_price": 19.99},
            ],
        },
    )
    assert response.status_code == 201
    return response.json()


def test_health_check() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_user_order_payment_flow() -> None:
    user = create_user()
    order = create_order(user["id"])

    assert order["status"] == "pending"
    assert order["total_amount"] == 119.97

    payment_response = client.post(
        "/payments",
        json={"order_id": order["id"], "amount": order["total_amount"], "provider": "stripe"},
    )
    assert payment_response.status_code == 201
    payment = payment_response.json()

    capture_response = client.patch(
        f"/payments/{payment['id']}",
        json={"status": "captured", "external_reference": "pi_123"},
    )
    assert capture_response.status_code == 200
    assert capture_response.json()["status"] == "captured"

    order_response = client.get(f"/orders/{order['id']}")
    assert order_response.status_code == 200
    assert order_response.json()["status"] == "paid"


def test_duplicate_user_email_is_rejected() -> None:
    create_user()
    response = client.post(
        "/users",
        json={"email": "ada@example.com", "full_name": "Ada Again"},
    )
    assert response.status_code == 409


def test_order_requires_existing_user() -> None:
    response = client.post(
        "/orders",
        json={
            "user_id": "missing",
            "items": [{"sku": "SKU-1", "name": "Keyboard", "quantity": 1, "unit_price": 49.99}],
        },
    )
    assert response.status_code == 404


def test_payment_amount_must_match_order_total() -> None:
    user = create_user()
    order = create_order(user["id"])

    response = client.post(
        "/payments",
        json={"order_id": order["id"], "amount": 1.00, "provider": "manual"},
    )
    assert response.status_code == 422
