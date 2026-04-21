$ErrorActionPreference = "Stop"

Set-Location (Join-Path $PSScriptRoot "..")

if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
  throw "Virtual environment not found. Run .\scripts\bootstrap.ps1 first."
}

if (-not (Test-Path ".\artifacts\model.joblib")) {
  Write-Host "Model artifact not found. Running training pipeline..."
  .\.venv\Scripts\python.exe -m training.pipelines.generate_sample_data
  .\.venv\Scripts\python.exe -m training.pipelines.prepare_real_data
  .\.venv\Scripts\python.exe -m training.pipelines.train
}

Write-Host "Starting API at http://127.0.0.1:8000 ..."
.\.venv\Scripts\python.exe -m uvicorn app.api.main:app --host 127.0.0.1 --port 8000 --reload
