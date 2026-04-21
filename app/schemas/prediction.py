from pydantic import BaseModel, ConfigDict, Field


class FraudPredictionRequest(BaseModel):
    transaction_amount: float = Field(..., gt=0)
    customer_age: int = Field(..., ge=18, le=100)
    merchant_risk_score: float = Field(..., ge=0, le=1)
    transaction_velocity_1h: int = Field(..., ge=0)
    card_present: bool
    international: bool


class StreamIngestResponse(BaseModel):
    accepted: bool
    fraud_probability: float
    fraud_label: str


class FraudPredictionResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    fraud_probability: float
    fraud_label: str
    model_version: str


class RecentPrediction(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    source: str
    transaction_amount: float
    customer_age: int
    merchant_risk_score: float
    transaction_velocity_1h: int
    card_present: bool
    international: bool
    fraud_probability: float
    fraud_label: str
    created_at: str


class DashboardStats(BaseModel):
    total_predictions: int
    fraud_count: int
    legit_count: int
    average_risk: float
