from __future__ import annotations

import json
import os
from pathlib import Path

import joblib
import mlflow
import mlflow.sklearn
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


def configure_mlflow(project_root: Path) -> tuple[Path, str]:
    tracking_path = resolve_project_path(os.getenv("MLFLOW_TRACKING_PATH", "mlruns"))
    tracking_path.mkdir(parents=True, exist_ok=True)
    tracking_uri = os.getenv("MLFLOW_TRACKING_URI", tracking_path.as_uri())
    experiment_name = os.getenv("MLFLOW_EXPERIMENT_NAME", "fraudshield-training")
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(experiment_name)
    return tracking_path, experiment_name


def train_model(
    data_path: str = "data/processed/transactions_processed.csv",
    artifact_dir: str = "artifacts",
) -> None:
    project_root = Path(__file__).resolve().parents[2]
    csv_path = resolve_project_path(data_path)
    artifact_path = resolve_project_path(artifact_dir)
    artifact_path.mkdir(parents=True, exist_ok=True)

    if not csv_path.exists():
        raise FileNotFoundError(
            f"Dataset not found at {csv_path}. Run preprocessing first or add a processed CSV."
        )

    dataframe = pd.read_csv(csv_path)
    features, target = select_features(dataframe)
    tracking_path, experiment_name = configure_mlflow(project_root)

    x_train, x_test, y_train, y_test = train_test_split(
        features, target, test_size=0.2, random_state=42, stratify=target
    )

    model = Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            ("classifier", LogisticRegression(max_iter=2000, class_weight="balanced")),
        ]
    )

    with mlflow.start_run(run_name="baseline-logreg") as run:
        model.fit(x_train, y_train)

        predictions = model.predict(x_test)
        probabilities = model.predict_proba(x_test)[:, 1]
        print(classification_report(y_test, predictions))

        precision, recall, f1, _ = precision_recall_fscore_support(
            y_test, predictions, average="binary", zero_division=0
        )
        roc_auc = roc_auc_score(y_test, probabilities)
        metrics = {
            "precision": round(float(precision), 4),
            "recall": round(float(recall), 4),
            "f1": round(float(f1), 4),
            "roc_auc": round(float(roc_auc), 4),
            "train_rows": len(x_train),
            "test_rows": len(x_test),
        }

        mlflow.log_params(
            {
                "model_family": "logistic_regression",
                "feature_count": features.shape[1],
                "test_size": 0.2,
                "random_state": 42,
                "class_weight": "balanced",
                "data_path": str(csv_path),
            }
        )
        mlflow.log_metrics(metrics)
        mlflow.sklearn.log_model(model, artifact_path="model")

        metrics_path = artifact_path / "metrics.txt"
        metrics_path.write_text(
            "\n".join([f"{key}={value}" for key, value in metrics.items()]),
            encoding="utf-8",
        )

        metadata_path = artifact_path / "model_metadata.json"
        metadata_path.write_text(
            json.dumps(
                {
                    "model_version": "baseline",
                    "model_family": "logistic_regression",
                    "feature_count": features.shape[1],
                    "mlflow_tracking_uri": mlflow.get_tracking_uri(),
                    "mlflow_tracking_path": str(tracking_path),
                    "mlflow_experiment_name": experiment_name,
                    "mlflow_run_id": run.info.run_id,
                    "metrics": metrics,
                },
                indent=2,
            ),
            encoding="utf-8",
        )

        mlflow.log_artifact(str(metrics_path))
        mlflow.log_artifact(str(metadata_path))

        joblib.dump(model, artifact_path / "model.joblib")


if __name__ == "__main__":
    train_model()
