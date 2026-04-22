from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class ExportResult:
    bucket: str
    key: str
    record_count: int
    bytes_uploaded: int


def resolve_project_path(path_value: str) -> Path:
    path = Path(path_value)
    if path.is_absolute():
        return path
    project_root = Path(__file__).resolve().parents[2]
    return project_root / path


def build_export_key(prefix: str, timestamp: datetime | None = None) -> str:
    current_time = timestamp or datetime.now(timezone.utc)
    date_path = current_time.strftime("%Y/%m/%d")
    filename = current_time.strftime("%H%M%S-prediction-log.jsonl")
    normalized_prefix = prefix.strip("/").replace("\\", "/")
    if normalized_prefix:
        return f"{normalized_prefix}/{date_path}/{filename}"
    return f"{date_path}/{filename}"


def count_records(payload: bytes) -> int:
    return sum(1 for line in payload.splitlines() if line.strip())


def export_prediction_log_to_s3(
    log_path: str,
    bucket: str,
    prefix: str = "prediction-logs",
    region_name: str | None = None,
    endpoint_url: str | None = None,
    client: Any | None = None,
) -> ExportResult:
    resolved_path = resolve_project_path(log_path)
    if not resolved_path.exists():
        raise FileNotFoundError(f"Prediction log not found at {resolved_path}")
    if not bucket:
        raise ValueError("S3 bucket is required for prediction log export")

    payload = resolved_path.read_bytes()
    if not payload.strip():
        raise ValueError(f"Prediction log at {resolved_path} is empty")

    s3_client = client
    if s3_client is None:
        try:
            import boto3
        except ImportError as exc:
            raise RuntimeError(
                "boto3 is required to export prediction logs. Install dependencies from requirements.txt."
            ) from exc

        client_kwargs: dict[str, Any] = {}
        if region_name:
            client_kwargs["region_name"] = region_name
        if endpoint_url:
            client_kwargs["endpoint_url"] = endpoint_url
        s3_client = boto3.client("s3", **client_kwargs)

    key = build_export_key(prefix)
    s3_client.put_object(
        Bucket=bucket,
        Key=key,
        Body=payload,
        ContentType="application/x-ndjson",
    )
    return ExportResult(
        bucket=bucket,
        key=key,
        record_count=count_records(payload),
        bytes_uploaded=len(payload),
    )
