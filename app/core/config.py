from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "fraud-detection-api"
    environment: str = "dev"
    model_path: str = "artifacts/model.joblib"
    model_version: str = "baseline"
    prediction_log_path: str = "artifacts/prediction_log.jsonl"
    prediction_store_limit: int = 100
    prediction_export_bucket: str = ""
    prediction_export_prefix: str = "prediction-logs"
    aws_region: str = "ap-south-1"
    s3_endpoint_url: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        protected_namespaces=("settings_",),
    )


settings = Settings()
