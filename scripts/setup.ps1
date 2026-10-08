# Run from PowerShell: .\scripts\setup.ps1
$ErrorActionPreference = 'Stop'
Set-Location (Split-Path -Parent $PSScriptRoot)
function Check-Exit { if ($LASTEXITCODE -ne 0) { throw "Command failed: $LASTEXITCODE" } }
py -3.12 -m venv .venv
Check-Exit
& .\.venv\Scripts\python.exe -m pip install -r requirements.lock
Check-Exit
& .\.venv\Scripts\python.exe -m pip install --no-deps -e .
Check-Exit
if (-not (Test-Path .env)) {
    $password = & .\.venv\Scripts\python.exe -c 'import secrets; print(secrets.token_hex(24))'
    Check-Exit
    $template = Get-Content .env.example -Raw
    $template.Replace('replace-with-a-long-random-password', $password.Trim()) |
        Set-Content .env -Encoding ascii
}
Write-Host 'Python environment ready. Continue with the PostgreSQL and Ollama steps in README.md.'
