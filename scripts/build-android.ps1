param(
    [ValidateSet('PersonalVoice','CoreDebug','CoreRelease')][string]$Profile = 'PersonalVoice',
    [string]$SdkRoot = '',
    [switch]$CheckOnly
)
$ErrorActionPreference = 'Stop'
$adaRoot = Split-Path -Parent $PSScriptRoot
$adaRelease = Get-Content -LiteralPath (Join-Path $adaRoot 'release.json') -Raw | ConvertFrom-Json
$adaPython = Join-Path $adaRoot '.venv/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $adaPython)) { throw 'Run scripts/setup.ps1 first.' }
if (-not $SdkRoot) {
    $SdkRoot = $env:ANDROID_HOME
    if (-not $SdkRoot) { $SdkRoot = $env:ANDROID_SDK_ROOT }
    if (-not $SdkRoot) { $SdkRoot = Join-Path $env:LOCALAPPDATA 'Android/Sdk' }
}
$adaAapt = Join-Path $SdkRoot 'build-tools/35.0.0/aapt2.exe'
if (-not (Test-Path -LiteralPath $adaAapt)) { throw 'Install Android Build-Tools 35.0.0; pass -SdkRoot if needed.' }
$adaNative = $Profile -eq 'PersonalVoice'
$adaBundle = Join-Path $adaRoot 'build/private-voice'
if ($adaNative -and -not (Test-Path -LiteralPath (Join-Path $adaBundle 'sherpa-onnx-1.13.8.aar'))) {
    throw 'Run .venv/Scripts/python.exe scripts/prepare_private_voice.py --download first.'
}
$adaVariant = if ($Profile -eq 'CoreRelease') { 'release' } else { 'debug' }
$adaAppId = if ($adaVariant -eq 'release') { 'dev.ada.assistant' } else { 'dev.ada.assistant.debug' }
Write-Host "ADA $($adaRelease.version) [$($adaRelease.status)] - $Profile"
Write-Host "Application ID: $adaAppId; native speech bundled: $adaNative"
if ($CheckOnly) { Write-Host 'Preflight complete. No build or installation performed.'; return }
Push-Location $adaRoot
try {
    $adaArguments = @('-p', 'apps/android')
    if ($adaNative) {
        & $adaPython scripts/prepare_private_voice.py
        if ($LASTEXITCODE -ne 0) { throw 'Pinned speech preparation failed.' }
        $adaArguments += "-PadaSpeechRuntimeDir=$($adaBundle.Replace('\','/'))"
    }
    $adaArguments += @('testDebugUnitTest', 'lintDebug', "assemble$((Get-Culture).TextInfo.ToTitleCase($adaVariant))")
    & (Join-Path $adaRoot 'apps/android/gradlew.bat') @adaArguments
    if ($LASTEXITCODE -ne 0) { throw 'Android verification/build failed; no candidate staged.' }
    $adaMetadataPath = Join-Path $adaRoot "apps/android/app/build/outputs/apk/$adaVariant/output-metadata.json"
    $adaMetadata = Get-Content -LiteralPath $adaMetadataPath -Raw | ConvertFrom-Json
    if ($adaMetadata.applicationId -ne $adaAppId -or $adaMetadata.elements.Count -ne 1 -or
        $adaMetadata.elements[0].versionName -ne $adaRelease.version -or
        $adaMetadata.elements[0].versionCode -ne $adaRelease.android_version_code) {
        throw 'APK metadata does not match the intended version/profile.'
    }
    $adaApk = Join-Path (Split-Path -Parent $adaMetadataPath) $adaMetadata.elements[0].outputFile
    $adaBadging = & $adaAapt dump badging $adaApk
    if ($LASTEXITCODE -ne 0 -or -not ($adaBadging | Select-String -SimpleMatch "package: name='$adaAppId' versionCode='$($adaRelease.android_version_code)' versionName='$($adaRelease.version)'" -Quiet)) {
        throw 'Actual APK identity does not match its metadata.'
    }
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $adaZip = [System.IO.Compression.ZipFile]::OpenRead($adaApk)
    try {
        $adaCatalogue = $adaZip.GetEntry('assets/speech-models/catalogue.json')
        if (($null -ne $adaCatalogue) -ne $adaNative) { throw 'Actual APK speech payload does not match the selected profile.' }
        if ($adaNative) {
            $adaStream = $adaCatalogue.Open()
            $adaHasher = [System.Security.Cryptography.SHA256]::Create()
            try { $adaDigest = [BitConverter]::ToString($adaHasher.ComputeHash($adaStream)).Replace('-','').ToLowerInvariant() }
            finally { $adaStream.Dispose(); $adaHasher.Dispose() }
            if ($adaDigest -ne '403b9e4b16a87eedaec87bcd5219c02f7f2bc44e274092fc2a237cc0a9036038') { throw 'Packaged speech catalogue failed verification.' }
        }
    }
    finally { $adaZip.Dispose() }
    $adaDestination = Join-Path $adaRoot 'dist/android'
    New-Item -ItemType Directory -Path $adaDestination -Force | Out-Null
    $adaName = "ada-$($adaRelease.version)-$($Profile.ToLowerInvariant())"
    $adaTarget = Join-Path $adaDestination "$adaName.apk"
    Copy-Item -LiteralPath $adaApk -Destination "$adaTarget.partial" -Force
    Move-Item -LiteralPath "$adaTarget.partial" -Destination $adaTarget -Force
    $adaCommit = (& git rev-parse HEAD).Trim()
    if ($LASTEXITCODE -ne 0) { throw 'Cannot identify build source.' }
    $adaDirty = [bool](& git status --porcelain)
    $adaReceipt = [ordered]@{
        version = $adaRelease.version; status = $adaRelease.status; profile = $Profile
        application_id = $adaAppId; version_code = $adaRelease.android_version_code
        native_speech = $adaNative; signing = $(if ($adaVariant -eq 'release') { 'unsigned' } else { 'debug' })
        apk = "$adaName.apk"; sha256 = (Get-FileHash -LiteralPath $adaTarget -Algorithm SHA256).Hash.ToLowerInvariant()
        source_commit = $adaCommit; working_tree_dirty = $adaDirty
    }
    [IO.File]::WriteAllText((Join-Path $adaDestination "$adaName.json"), ($adaReceipt | ConvertTo-Json), [Text.UTF8Encoding]::new($false))
    Write-Host "Candidate: $adaTarget"
    if ($adaVariant -eq 'release') { Write-Host 'UNSIGNED core APK: sign and verify it before installation. Native speech is excluded.' }
    else { Write-Host 'Debug-signed personal APK. Use adb install -r with an explicit device serial; no installation was performed.' }
}
finally { Pop-Location }
