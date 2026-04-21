from __future__ import annotations

from pathlib import Path

import pandas as pd

from training.features.build_features import FEATURE_COLUMNS
from training.pipelines.prepare_real_data import prepare_dataset


def test_prepare_dataset_accepts_business_schema(tmp_path: Path) -> None:
    input_csv = tmp_path / "transactions.csv"
    output_csv = tmp_path / "processed.csv"

    dataframe = pd.DataFrame(
        [
            {
                "transaction_amount": 125.0,
                "customer_age": 42,
                "merchant_risk_score": 0.33,
                "transaction_velocity_1h": 2,
                "card_present": True,
                "international": False,
                "is_fraud": 0,
            }
        ]
    )
    dataframe.to_csv(input_csv, index=False)

    output_path = prepare_dataset(str(input_csv), str(output_csv))
    processed = pd.read_csv(output_path)

    assert list(processed.columns) == FEATURE_COLUMNS + ["is_fraud"]
    assert int(processed.loc[0, "card_present"]) == 1
    assert int(processed.loc[0, "international"]) == 0


def test_prepare_dataset_converts_kaggle_schema(tmp_path: Path) -> None:
    input_csv = tmp_path / "creditcard.csv"
    output_csv = tmp_path / "processed.csv"

    rows = []
    for index in range(3):
        row = {f"V{i}": float(index + i) for i in range(1, 29)}
        row.update(
            {
                "Time": index * 120.0,
                "Amount": 100.0 + index * 50,
                "Class": 1 if index == 2 else 0,
            }
        )
        rows.append(row)

    pd.DataFrame(rows).to_csv(input_csv, index=False)

    output_path = prepare_dataset(str(input_csv), str(output_csv))
    processed = pd.read_csv(output_path)

    assert list(processed.columns) == FEATURE_COLUMNS + ["is_fraud"]
    assert len(processed) == 3
    assert processed["merchant_risk_score"].between(0, 1).all()
    assert set(processed["is_fraud"].tolist()) == {0, 1}
