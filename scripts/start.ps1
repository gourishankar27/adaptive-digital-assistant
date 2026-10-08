param([string]$ListenAddress = '127.0.0.1', [int]$Port = 8000)
$ErrorActionPreference = 'Stop'
Set-Location (Split-Path -Parent $PSScriptRoot)
# Exactly one worker: GPU capacity control is process-local in Phase 0.
& .\.venv\Scripts\python.exe -m uvicorn ada.api:create_app --factory --host $ListenAddress --port $Port --workers 1 --no-access-log
if ($LASTEXITCODE -ne 0) { throw "ADA exited with code $LASTEXITCODE" }
