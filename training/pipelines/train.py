from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, precision_recall_fscore_support, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from training.features.build_features import select_features


def resolve_project_path(path_value: str) -> Path:
    path = Path(path_value)
    if path.is_absolute():
        return path
    project_root = Path(__file__).resolve().parents[2]
    return project_root / path


def train_model(
    data_path: str = "data/processed/transactions_processed.csv",
    artifact_dir: str = "artifacts",
) -> None:
    csv_path = resolve_project_path(data_path)
    artifact_path = resolve_project_path(artifact_dir)
    artifact_path.mkdir(parents=True, exist_ok=True)

    if not csv_path.exists():
        raise FileNotFoundError(
            f"Dataset not found at {csv_path}. Run preprocessing first or add a processed CSV."
        )

    dataframe = pd.read_csv(csv_path)
    features, target = select_features(dataframe)

    x_train, x_test, y_train, y_test = train_test_split(
        features, target, test_size=0.2, random_state=42, stratify=target
    )

    model = Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            ("classifier", LogisticRegression(max_iter=2000, class_weight="balanced")),
        ]
    )
    model.fit(x_train, y_train)

    predictions = model.predict(x_test)
    probabilities = model.predict_proba(x_test)[:, 1]
    print(classification_report(y_test, predictions))

    precision, recall, f1, _ = precision_recall_fscore_support(
        y_test, predictions, average="binary", zero_division=0
    )
    roc_auc = roc_auc_score(y_test, probabilities)
    metrics_path = artifact_path / "metrics.txt"
    metrics_path.write_text(
        "\n".join(
            [
                f"precision={precision:.4f}",
                f"recall={recall:.4f}",
                f"f1={f1:.4f}",
                f"roc_auc={roc_auc:.4f}",
                f"train_rows={len(x_train)}",
                f"test_rows={len(x_test)}",
            ]
        ),
        encoding="utf-8",
    )

    joblib.dump(model, artifact_path / "model.joblib")


if __name__ == "__main__":
    train_model()
