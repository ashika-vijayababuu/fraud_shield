from __future__ import annotations

import pandas as pd


FEATURE_COLUMNS = [
    "transaction_amount",
    "customer_age",
    "merchant_risk_score",
    "transaction_velocity_1h",
    "card_present",
    "international",
]

TARGET_COLUMN = "is_fraud"
BUSINESS_DATASET_COLUMNS = FEATURE_COLUMNS + [TARGET_COLUMN]
KAGGLE_CREDIT_CARD_MIN_COLUMNS = {"Time", "Amount", "Class"}
KAGGLE_SIGNAL_COLUMNS = ["V10", "V12", "V14", "V17"]


def select_features(dataframe: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    features = dataframe[FEATURE_COLUMNS].copy()
    target = dataframe[TARGET_COLUMN].copy()
    return features, target


def has_business_schema(dataframe: pd.DataFrame) -> bool:
    return set(BUSINESS_DATASET_COLUMNS).issubset(dataframe.columns)


def has_kaggle_creditcard_schema(dataframe: pd.DataFrame) -> bool:
    v_columns = {f"V{i}" for i in range(1, 29)}
    required = KAGGLE_CREDIT_CARD_MIN_COLUMNS | v_columns
    return required.issubset(dataframe.columns)


def validate_business_schema(dataframe: pd.DataFrame) -> None:
    missing = [column for column in BUSINESS_DATASET_COLUMNS if column not in dataframe.columns]
    if missing:
        raise ValueError(
            "Dataset is missing required business-schema columns: "
            + ", ".join(missing)
        )
