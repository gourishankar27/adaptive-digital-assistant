$ErrorActionPreference = 'Stop'
Push-Location (Split-Path -Parent $PSScriptRoot)
try {
    & .\.venv\Scripts\python.exe scripts\test_postgres.py
    if ($LASTEXITCODE -ne 0) { throw "PostgreSQL verification exited with code $LASTEXITCODE" }
}
finally { Pop-Location }
