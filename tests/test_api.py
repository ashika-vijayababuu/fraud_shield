from __future__ import annotations

from fastapi.testclient import TestClient

from app.api import main


class StubModel:
    def predict_proba(self, features: list[float]) -> float:
        return 0.91 if features[0] > 500 else 0.12


def setup_function() -> None:
    main.recent_predictions.clear()
    main.model = StubModel()


def test_health_endpoint() -> None:
    client = TestClient(main.app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_manual_prediction_updates_dashboard_history() -> None:
    client = TestClient(main.app)

    response = client.post(
        "/predict",
        json={
            "transaction_amount": 2200,
            "customer_age": 34,
            "merchant_risk_score": 0.92,
            "transaction_velocity_1h": 14,
            "card_present": False,
            "international": True,
        },
    )

    assert response.status_code == 200
    assert response.json()["fraud_label"] == "fraud"

    history = client.get("/api/recent-predictions")
    stats = client.get("/api/stats")

    assert history.status_code == 200
    assert history.json()[0]["source"] == "manual"
    assert stats.json()["fraud_count"] == 1
    assert stats.json()["total_predictions"] == 1


def test_stream_ingest_marks_source_as_stream() -> None:
    client = TestClient(main.app)

    response = client.post(
        "/api/ingest-transaction",
        json={
            "transaction_amount": 250,
            "customer_age": 41,
            "merchant_risk_score": 0.2,
            "transaction_velocity_1h": 1,
            "card_present": True,
            "international": False,
        },
    )

    assert response.status_code == 200
    assert response.json()["accepted"] is True
    assert response.json()["fraud_label"] == "legit"

    history = client.get("/api/recent-predictions").json()
    assert history[0]["source"] == "stream"
