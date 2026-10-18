param([switch]$CheckOnly)
$ErrorActionPreference = 'Stop'
$adaRoot = Split-Path -Parent $PSScriptRoot
$adaPython = Join-Path $adaRoot '.venv/Scripts/python.exe'
$adaPin = (Get-Content (Join-Path $adaRoot 'ops/validation-tools.json') -Raw | ConvertFrom-Json).caddy
$adaCaddy = Join-Path $env:LOCALAPPDATA "ADA/tools/caddy-$($adaPin.version)/caddy.exe"
if (-not (Test-Path -LiteralPath $adaCaddy)) { throw 'Run scripts/install-private-proxy.ps1 first.' }
if ((Get-FileHash -LiteralPath $adaCaddy -Algorithm SHA256).Hash.ToLowerInvariant() -ne $adaPin.windows_amd64_exe_sha256) {
    throw 'Caddy executable checksum mismatch; do not run it.'
}
$adaReadDist = @'
import sys
from pathlib import Path
from dotenv import dotenv_values
value = dotenv_values(sys.argv[1], interpolate=False).get("ADA_ADMIN_DIST") or ""
path = Path(value)
if not path.is_absolute() or not (path / "index.html").is_file():
    raise SystemExit("ADA_ADMIN_DIST must be a literal absolute built-admin directory in .env")
print(path.resolve().as_posix())
'@
# Standard input preserves embedded quotes under Windows PowerShell 5.1 as well.
$adaDist = $adaReadDist | & $adaPython -X utf8 - (Join-Path $adaRoot '.env')
if ($LASTEXITCODE -ne 0) { throw 'Cannot read the built-admin directory. Check .env and npm run build.' }
$adaPreviousDist = $env:ADA_ADMIN_DIST
try {
    # Export only the public asset path. Do not import/evaluate arbitrary .env text.
    $env:ADA_ADMIN_DIST = $adaDist.Trim()
    $adaConfig = Join-Path $adaRoot 'ops/Caddyfile.tailnet.example'
    & $adaCaddy validate --config $adaConfig --adapter caddyfile
    if ($LASTEXITCODE -ne 0) { throw 'Private loopback proxy configuration is invalid.' }
    if (-not $CheckOnly) {
        & $adaCaddy run --config $adaConfig --adapter caddyfile
        if ($LASTEXITCODE -ne 0) { throw 'Proxy stopped with an error. Check whether port 18764 is already occupied.' }
    }
}
finally { $env:ADA_ADMIN_DIST = $adaPreviousDist }
