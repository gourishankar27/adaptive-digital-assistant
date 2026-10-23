param([ValidateSet('127.0.0.1', '::1')][string]$ListenAddress = '127.0.0.1', [ValidateRange(1024,65535)][int]$Port = 8000)
$ErrorActionPreference = 'Stop'
Set-Location (Split-Path -Parent $PSScriptRoot)
# Refuse an existing listener before Python performs request recovery.
$adaPortProbe = $null
try {
    $adaPortProbe = [Net.Sockets.TcpListener]::new([Net.IPAddress]::Parse($ListenAddress), $Port)
    $adaPortProbe.Server.ExclusiveAddressUse = $true
    $adaPortProbe.Start()
} catch {
    throw 'ADA listen address/port is already in use or unavailable. Stop the existing service before retrying.'
} finally {
    if ($null -ne $adaPortProbe) { $adaPortProbe.Stop() }
}
# Exactly one worker: GPU capacity control is process-local.
Write-Host 'Starting ADA. Loading Python and checking the protected runtime/database gate...'
Write-Host 'Startup progress will appear below. Leave this window open; Ctrl+C stops ADA.'
& .\.venv\Scripts\python.exe -u -m ada.host_ops foreground --listen $ListenAddress --port $Port
if ($LASTEXITCODE -ne 0) { throw "ADA exited with code $LASTEXITCODE" }
