param([ValidateSet('127.0.0.1', '::1')][string]$ListenAddress = '127.0.0.1', [ValidateRange(1024,65535)][int]$Port = 8000)
$ErrorActionPreference = 'Stop'
Set-Location (Split-Path -Parent $PSScriptRoot)
# Exactly one worker: GPU capacity control is process-local.
& .\.venv\Scripts\python.exe -m uvicorn ada.api:create_app --factory --host $ListenAddress --port $Port --workers 1 --no-access-log --no-proxy-headers --limit-concurrency 128 --timeout-keep-alive 5 --h11-max-incomplete-event-size 16384
if ($LASTEXITCODE -ne 0) { throw "ADA exited with code $LASTEXITCODE" }
