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

function Test-PortAvailable {
  Param([int]$Port)
  $listener = $null
  try {
    $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Parse("127.0.0.1"), $Port)
    $listener.Start()
    return $true
  } catch {
    return $false
  } finally {
    if ($listener -ne $null) {
      $listener.Stop()
    }
  }
}

$candidatePorts = @(8765, 8000, 8001, 8002, 8080)
$selectedPort = $candidatePorts | Where-Object { Test-PortAvailable $_ } | Select-Object -First 1

if (-not $selectedPort) {
  throw "No free port found in: $($candidatePorts -join ', ')"
}

Write-Host "Starting API at http://127.0.0.1:$selectedPort ..."
.\.venv\Scripts\python.exe -m uvicorn app.api.main:app --host 127.0.0.1 --port $selectedPort --reload
