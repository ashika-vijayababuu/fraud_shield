from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from app.core.log_export import build_export_key, export_prediction_log_to_s3


class FakeS3Client:
    def __init__(self) -> None:
        self.last_call: dict[str, object] | None = None

    def put_object(self, **kwargs: object) -> None:
        self.last_call = kwargs


def test_build_export_key_uses_prefix_and_date() -> None:
    key = build_export_key(
        "prediction-logs",
        timestamp=datetime(2026, 4, 22, 11, 5, 12, tzinfo=timezone.utc),
    )

    assert key == "prediction-logs/2026/04/22/110512-prediction-log.jsonl"


def test_export_prediction_log_uploads_jsonl_payload(tmp_path: Path) -> None:
    log_path = tmp_path / "prediction_log.jsonl"
    log_path.write_text('{"fraud_label":"fraud"}\n{"fraud_label":"legit"}\n', encoding="utf-8")
    fake_client = FakeS3Client()

    result = export_prediction_log_to_s3(
        log_path=str(log_path),
        bucket="fraudshield-logs",
        prefix="exports",
        client=fake_client,
    )

    assert result.bucket == "fraudshield-logs"
    assert result.record_count == 2
    assert result.bytes_uploaded > 0
    assert fake_client.last_call is not None
    assert fake_client.last_call["Bucket"] == "fraudshield-logs"
    assert str(fake_client.last_call["Key"]).startswith("exports/")
    assert fake_client.last_call["ContentType"] == "application/x-ndjson"


def test_export_prediction_log_rejects_empty_file(tmp_path: Path) -> None:
    log_path = tmp_path / "prediction_log.jsonl"
    log_path.write_text("", encoding="utf-8")

    with pytest.raises(ValueError):
        export_prediction_log_to_s3(
            log_path=str(log_path),
            bucket="fraudshield-logs",
            client=FakeS3Client(),
        )
