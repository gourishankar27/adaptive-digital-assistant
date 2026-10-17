param([string]$ArchivePath)
$ErrorActionPreference = 'Stop'
$adaRoot = Split-Path -Parent $PSScriptRoot
$adaPin = (Get-Content (Join-Path $adaRoot 'ops/validation-tools.json') -Raw | ConvertFrom-Json).caddy
$adaToolFolder = Join-Path $env:LOCALAPPDATA "ADA/tools/caddy-$($adaPin.version)"
New-Item -ItemType Directory -Path $adaToolFolder -Force | Out-Null
if (-not $ArchivePath) {
    $ArchivePath = Join-Path $adaToolFolder $adaPin.asset
    if (-not (Test-Path -LiteralPath $ArchivePath)) {
        $adaDownload = "https://github.com/caddyserver/caddy/releases/download/v$($adaPin.version)/$($adaPin.asset)"
        Invoke-WebRequest -Uri $adaDownload -OutFile $ArchivePath
    }
}
$ArchivePath = (Resolve-Path -LiteralPath $ArchivePath).Path
if ((Get-FileHash -LiteralPath $ArchivePath -Algorithm SHA512).Hash.ToLowerInvariant() -ne $adaPin.sha512) {
    throw 'Caddy archive checksum mismatch. Nothing was installed.'
}
Add-Type -AssemblyName System.IO.Compression.FileSystem
$adaZip = [System.IO.Compression.ZipFile]::OpenRead($ArchivePath)
try {
    $adaEntry = $adaZip.GetEntry('caddy.exe')
    if (-not $adaEntry) { throw 'Verified archive is missing caddy.exe.' }
    $adaBinary = Join-Path $adaToolFolder 'caddy.exe'
    if (-not (Test-Path -LiteralPath $adaBinary)) {
        [System.IO.Compression.ZipFileExtensions]::ExtractToFile($adaEntry, $adaBinary, $false)
    }
}
finally { $adaZip.Dispose() }
if ((Get-FileHash -LiteralPath $adaBinary -Algorithm SHA256).Hash.ToLowerInvariant() -ne $adaPin.windows_amd64_exe_sha256) {
    throw 'Installed Caddy executable checksum mismatch; do not run it.'
}
Write-Host "Verified Caddy $($adaPin.version): $adaBinary"
Write-Host 'This installs a local binary only. It does not start a service or enable networking.'
