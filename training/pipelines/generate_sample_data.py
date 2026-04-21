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

    amount_scaled = (dataframe["transaction_amount"] - 10) / (3000 - 10)
    velocity_scaled = dataframe["transaction_velocity_1h"] / 24

    # Build a smooth latent score instead of hard thresholds so model outputs are less saturated.
    latent_score = (
        (amount_scaled * 1.1)
        + (dataframe["merchant_risk_score"] * 1.8)
        + (velocity_scaled * 1.0)
        + (dataframe["international"] * 0.7)
        + ((1 - dataframe["card_present"]) * 0.35)
        - 2.0
    )

    jitter = rng.normal(0, 0.35, rows)
    probability = 1 / (1 + np.exp(-(latent_score + jitter)))
    probability = np.clip(probability, 0.01, 0.99)
    dataframe["is_fraud"] = rng.binomial(1, probability).astype(int)
    return dataframe


def main() -> None:
    project_root = Path(__file__).resolve().parents[2]
    output = project_root / "data/raw/transactions.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    build_dataset().to_csv(output, index=False)
    print(f"Wrote sample dataset to {output}")


if __name__ == "__main__":
    main()
