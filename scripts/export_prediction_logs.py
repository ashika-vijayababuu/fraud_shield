from __future__ import annotations

import json

from app.core.config import settings
from app.core.log_export import export_prediction_log_to_s3


def main() -> None:
    if not settings.prediction_export_bucket:
        raise SystemExit(
            "Set PREDICTION_EXPORT_BUCKET before running this export script."
        )

    result = export_prediction_log_to_s3(
        log_path=settings.prediction_log_path,
        bucket=settings.prediction_export_bucket,
        prefix=settings.prediction_export_prefix,
        region_name=settings.aws_region,
        endpoint_url=settings.s3_endpoint_url or None,
    )
    print(
        json.dumps(
            {
                "bucket": result.bucket,
                "key": result.key,
                "record_count": result.record_count,
                "bytes_uploaded": result.bytes_uploaded,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
