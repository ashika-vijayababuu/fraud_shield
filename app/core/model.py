from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from training.features.build_features import FEATURE_COLUMNS


class BaselineFraudModel:
    def __init__(self, model_path: str) -> None:
        self.model_path = Path(model_path)
        self.model: Any | None = None

    def load(self) -> None:
        if self.model_path.exists():
            self.model = joblib.load(self.model_path)

    def predict_proba(self, features: list[float]) -> float:
        if self.model is None:
            return 0.15
        row = pd.DataFrame([features], columns=FEATURE_COLUMNS)
        return float(self.model.predict_proba(row)[0][1])
