import json
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

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

app = FastAPI(title="Real-Time Fraud Detection API", version="0.1.0")
model = BaselineFraudModel(settings.model_path)
model.load()
frontend_dir = Path(__file__).resolve().parents[2] / "frontend"
project_root = Path(__file__).resolve().parents[2]
prediction_log_path = Path(settings.prediction_log_path)
if not prediction_log_path.is_absolute():
    prediction_log_path = project_root / prediction_log_path
recent_predictions: deque[RecentPrediction] = deque(maxlen=settings.prediction_store_limit)

REQUEST_COUNT = Counter("fraud_prediction_requests_total", "Total fraud prediction requests")
REQUEST_LATENCY = Histogram("fraud_prediction_latency_seconds", "Fraud prediction latency")

app.mount("/static", StaticFiles(directory=frontend_dir / "static"), name="static")


def append_prediction_log(entry: RecentPrediction) -> None:
    prediction_log_path.parent.mkdir(parents=True, exist_ok=True)
    with prediction_log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry.model_dump()) + "\n")


def load_prediction_log() -> Iterable[RecentPrediction]:
    if not prediction_log_path.exists():
        return []

    loaded_entries: list[RecentPrediction] = []
    with prediction_log_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            raw_line = line.strip()
            if not raw_line:
                continue
            loaded_entries.append(RecentPrediction.model_validate_json(raw_line))
    return loaded_entries[-settings.prediction_store_limit :]


recent_predictions.extend(load_prediction_log())


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
    prediction_entry = RecentPrediction(
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
    recent_predictions.append(prediction_entry)
    append_prediction_log(prediction_entry)
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
