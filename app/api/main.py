from collections import deque
from pathlib import Path

from fastapi import FastAPI
from prometheus_client import Counter, Histogram, generate_latest
from starlette.responses import FileResponse
from starlette.responses import Response
from starlette.staticfiles import StaticFiles

from app.core.config import settings
from app.core.model import BaselineFraudModel
from app.schemas.prediction import (
    DashboardStats,
    FraudPredictionRequest,
    FraudPredictionResponse,
    RecentPrediction,
    StreamIngestResponse,
)
from datetime import datetime, timezone

app = FastAPI(title="Real-Time Fraud Detection API", version="0.1.0")
model = BaselineFraudModel(settings.model_path)
model.load()
frontend_dir = Path(__file__).resolve().parents[2] / "frontend"
recent_predictions: deque[RecentPrediction] = deque(maxlen=12)

REQUEST_COUNT = Counter("fraud_prediction_requests_total", "Total fraud prediction requests")
REQUEST_LATENCY = Histogram("fraud_prediction_latency_seconds", "Fraud prediction latency")

app.mount("/static", StaticFiles(directory=frontend_dir / "static"), name="static")


@app.get("/", include_in_schema=False)
def home() -> FileResponse:
    return FileResponse(frontend_dir / "index.html")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "environment": settings.environment}


@app.get("/metrics")
def metrics() -> Response:
    return Response(generate_latest(), media_type="text/plain")


@app.get("/api/recent-predictions", response_model=list[RecentPrediction])
def get_recent_predictions() -> list[RecentPrediction]:
    return list(reversed(recent_predictions))


@app.get("/api/stats", response_model=DashboardStats)
def get_stats() -> DashboardStats:
    entries = list(recent_predictions)
    total = len(entries)
    fraud_count = sum(1 for item in entries if item.fraud_label == "fraud")
    legit_count = total - fraud_count
    average_risk = round(
        sum(item.fraud_probability for item in entries) / total, 4
    ) if total else 0.0
    return DashboardStats(
        total_predictions=total,
        fraud_count=fraud_count,
        legit_count=legit_count,
        average_risk=average_risk,
    )


def score_transaction(payload: FraudPredictionRequest, source: str) -> FraudPredictionResponse:
    features = [
        payload.transaction_amount,
        payload.customer_age,
        payload.merchant_risk_score,
        payload.transaction_velocity_1h,
        int(payload.card_present),
        int(payload.international),
    ]
    score = model.predict_proba(features)
    label = "fraud" if score >= 0.5 else "legit"
    rounded_score = round(score, 4)
    recent_predictions.append(
        RecentPrediction(
            source=source,
            transaction_amount=payload.transaction_amount,
            customer_age=payload.customer_age,
            merchant_risk_score=payload.merchant_risk_score,
            transaction_velocity_1h=payload.transaction_velocity_1h,
            card_present=payload.card_present,
            international=payload.international,
            fraud_probability=rounded_score,
            fraud_label=label,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
    )
    return FraudPredictionResponse(
        fraud_probability=rounded_score,
        fraud_label=label,
        model_version=settings.model_version,
    )


@app.post("/predict", response_model=FraudPredictionResponse)
@REQUEST_LATENCY.time()
def predict(payload: FraudPredictionRequest) -> FraudPredictionResponse:
    REQUEST_COUNT.inc()
    return score_transaction(payload, source="manual")


@app.post("/api/ingest-transaction", response_model=StreamIngestResponse)
def ingest_transaction(payload: FraudPredictionRequest) -> StreamIngestResponse:
    REQUEST_COUNT.inc()
    result = score_transaction(payload, source="stream")
    return StreamIngestResponse(
        accepted=True,
        fraud_probability=result.fraud_probability,
        fraud_label=result.fraud_label,
    )
