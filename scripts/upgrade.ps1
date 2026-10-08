param([Parameter(Mandatory = $true)][string]$ProjectPath, [switch]$CheckOnly)
$ErrorActionPreference = 'Stop'
$bundle = Split-Path -Parent $PSScriptRoot
$target = (Resolve-Path -LiteralPath $ProjectPath).Path
$python = Join-Path $target '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $python)) {
    throw 'The target must be your existing Phase 1 project with its Python virtual environment.'
}
function Check-Exit {
    if ($LASTEXITCODE -ne 0) { throw "Upgrade command exited with code $LASTEXITCODE" }
}
$copyArgs = @((Join-Path $bundle 'scripts\apply_upgrade.py'), '--project', $target)
if ($CheckOnly) { $copyArgs += '--check' }
& $python @copyArgs
Check-Exit
if ($CheckOnly) { return }
Push-Location $target
try {
    & $python -m pip install --no-deps -e .
    Check-Exit
    & $python -m alembic upgrade head
    Check-Exit
    & $python -m alembic check
    Check-Exit
}
finally { Pop-Location }
Write-Host 'Phase 2 is installed and migrated. Start the API with scripts\start.ps1.'
