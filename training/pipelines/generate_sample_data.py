from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


def build_dataset(rows: int = 1000) -> pd.DataFrame:
    rng = np.random.default_rng(42)

    dataframe = pd.DataFrame(
        {
            "transaction_amount": rng.uniform(10, 3000, rows).round(2),
            "customer_age": rng.integers(18, 80, rows),
            "merchant_risk_score": rng.uniform(0, 1, rows).round(3),
            "transaction_velocity_1h": rng.integers(0, 25, rows),
            "card_present": rng.integers(0, 2, rows),
            "international": rng.integers(0, 2, rows),
        }
    )

    risk_score = (
        (dataframe["transaction_amount"] > 1500).astype(int) * 0.25
        + (dataframe["merchant_risk_score"] > 0.7).astype(int) * 0.35
        + (dataframe["transaction_velocity_1h"] > 10).astype(int) * 0.2
        + (dataframe["international"] == 1).astype(int) * 0.15
        + (dataframe["card_present"] == 0).astype(int) * 0.05
    )

    noise = rng.uniform(0, 0.15, rows)
    dataframe["is_fraud"] = ((risk_score + noise) > 0.55).astype(int)
    return dataframe


def main() -> None:
    output = Path("data/raw/transactions.csv")
    output.parent.mkdir(parents=True, exist_ok=True)
    build_dataset().to_csv(output, index=False)
    print(f"Wrote sample dataset to {output}")


if __name__ == "__main__":
    main()
