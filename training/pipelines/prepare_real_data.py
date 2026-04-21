from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from training.features.build_features import (
    FEATURE_COLUMNS,
    TARGET_COLUMN,
    has_business_schema,
    has_kaggle_creditcard_schema,
    validate_business_schema,
)


def resolve_project_path(path_value: str) -> Path:
    path = Path(path_value)
    if path.is_absolute():
        return path
    project_root = Path(__file__).resolve().parents[2]
    return project_root / path


def min_max_scale(series: pd.Series) -> pd.Series:
    minimum = float(series.min())
    maximum = float(series.max())
    if maximum == minimum:
        return pd.Series(np.zeros(len(series)), index=series.index)
    return (series - minimum) / (maximum - minimum)


def prepare_business_schema(dataframe: pd.DataFrame) -> pd.DataFrame:
    prepared = dataframe.copy()
    validate_business_schema(prepared)

    prepared["card_present"] = prepared["card_present"].astype(int)
    prepared["international"] = prepared["international"].astype(int)
    return prepared[FEATURE_COLUMNS + [TARGET_COLUMN]]


def prepare_kaggle_creditcard_schema(dataframe: pd.DataFrame) -> pd.DataFrame:
    prepared = dataframe.sort_values("Time").reset_index(drop=True)

    amount_scaled = prepared["Amount"].clip(lower=0)
    risky_signal = (
        prepared["V10"].abs()
        + prepared["V12"].abs()
        + prepared["V14"].abs()
        + prepared["V17"].abs()
    )

    rolling_velocity = prepared["Time"].diff().fillna(3600).rdiv(3600).clip(lower=0, upper=20)
    merchant_risk = min_max_scale(risky_signal).round(4)
    age_proxy = (18 + (1 - min_max_scale(prepared["V4"].abs())) * 52).round().clip(18, 70)

    converted = pd.DataFrame(
        {
            "transaction_amount": amount_scaled.round(2),
            "customer_age": age_proxy.astype(int),
            "merchant_risk_score": merchant_risk,
            "transaction_velocity_1h": rolling_velocity.round().astype(int),
            "card_present": (prepared["V13"].abs() < prepared["V13"].abs().median()).astype(int),
            "international": (merchant_risk > 0.6).astype(int),
            "is_fraud": prepared["Class"].astype(int),
        }
    )

    return converted[FEATURE_COLUMNS + ["is_fraud"]]


def prepare_dataset(
    input_path: str | None = None,
    output_path: str = "data/processed/transactions_processed.csv",
) -> Path:
    project_root = Path(__file__).resolve().parents[2]
    if input_path is None:
        candidates = [
            project_root / "data/raw/transactions.csv",
            project_root / "data/raw/creditcard.csv",
        ]
        existing = next(
            (
                candidate
                for candidate in candidates
                if candidate.exists() and candidate.stat().st_size > 0
            ),
            None,
        )
        if existing is None:
            raise FileNotFoundError(
                "No raw dataset found. Place `creditcard.csv` or `transactions.csv` under `data/raw/`."
            )
        source = existing
    else:
        source = resolve_project_path(input_path)
    target = resolve_project_path(output_path)

    if not source.exists():
        raise FileNotFoundError(
            f"Raw dataset not found at {source}. Place your CSV there and rerun preprocessing."
        )

    dataframe = pd.read_csv(source)

    if has_business_schema(dataframe):
        prepared = prepare_business_schema(dataframe)
    elif has_kaggle_creditcard_schema(dataframe):
        prepared = prepare_kaggle_creditcard_schema(dataframe)
    else:
        raise ValueError(
            "Unsupported dataset schema. Expected either the business fraud schema "
            "or the Kaggle credit card fraud schema with V1-V28, Time, Amount, and Class."
        )

    target.parent.mkdir(parents=True, exist_ok=True)
    prepared.to_csv(target, index=False)
    return target


if __name__ == "__main__":
    output = prepare_dataset()
    print(f"Prepared dataset written to {output}")
