Param(
  [switch]$SkipTrain
)

$ErrorActionPreference = "Stop"

Set-Location (Join-Path $PSScriptRoot "..")

if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
  Write-Host "Creating virtual environment..."
  python -m venv .venv
}

Write-Host "Installing dependencies..."
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

if (-not $SkipTrain) {
  Write-Host "Generating sample data..."
  .\.venv\Scripts\python.exe -m training.pipelines.generate_sample_data

  Write-Host "Preparing processed dataset..."
  .\.venv\Scripts\python.exe -m training.pipelines.prepare_real_data

  Write-Host "Training baseline model..."
  .\.venv\Scripts\python.exe -m training.pipelines.train
}

Write-Host "Bootstrap complete."
Write-Host "Run the app with: .\scripts\run-local.ps1"
