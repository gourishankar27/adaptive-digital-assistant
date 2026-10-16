param(
    [Parameter(Mandatory)][string]$Device,
    [ValidateRange(19000,19999)][int]$Port = 19818,
    [switch]$IncludePermissionDialogs,
    [switch]$NativeFocusProbe
)
$ErrorActionPreference = 'Stop'
if ($Device -notmatch '^[A-Za-z0-9._:-]+$') { throw 'Invalid selected device identifier' }
$adaRoot = (Resolve-Path (Join-Path $PSScriptRoot '../../..')).Path
$adaAndroid = Join-Path $adaRoot 'apps/android'
$adaSdk = if ($env:ANDROID_HOME) { $env:ANDROID_HOME } else { Join-Path $env:LOCALAPPDATA 'Android/Sdk' }
$adaAdb = Join-Path $adaSdk 'platform-tools/adb.exe'
$adaId = 'dev.ada.validation.physical'
$adaPackage = "$adaId.debug"
$adaTestPackage = "$adaPackage.test"
$adaServer = $null
$adaReverse = $false
$adaInstalled = $false
$adaFocusInstalled = $false
$adaPriorToken = $env:ADA_WEB_TEST_TOKEN
$adaOrigin = "http://127.0.0.1:$Port"
$adaTemp = Join-Path $adaAndroid '.gradle/physical-validation'
New-Item -ItemType Directory -Force $adaTemp | Out-Null
function Invoke-AdaAdb {
    param([string[]]$Arguments)
    $adaResult = & $adaAdb -s $Device @Arguments
    if ($LASTEXITCODE -ne 0) { throw 'Selected-device command failed' }
    return $adaResult
}
try {
    if ((Invoke-AdaAdb -Arguments @('get-state')) -ne 'device') { throw 'Selected device is not authorized' }
    if ((Invoke-AdaAdb -Arguments @('shell','am','get-current-user')).Trim() -ne '0') { throw 'Use the primary user 0; private profiles are not inspected' }
    if (Invoke-AdaAdb -Arguments @('shell','pm','list','packages','--user','0',$adaPackage)) { throw 'Validation package already exists; preserve it and use a clean selected device' }
    if ($NativeFocusProbe -and (Invoke-AdaAdb -Arguments @('shell','pm','list','packages','--user','0','dev.ada.validation.focus.debug'))) { throw 'Focus fixture already exists; preserve it' }
    if ((Invoke-AdaAdb -Arguments @('reverse','--list')) -match "tcp:$Port\s") { throw 'Requested USB reverse mapping already exists' }
    if (Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue) { throw 'Fixture port already has a listener' }
    & (Join-Path $adaAndroid 'gradlew.bat') -p $adaAndroid "-PadaValidationApplicationId=$adaId" :app:assembleDebug :app:assembleDebugAndroidTest --console=plain
    if ($LASTEXITCODE -ne 0) { throw 'Validation APK build failed' }
    $adaMetadata = Get-Content (Join-Path $adaAndroid 'app/build/outputs/apk/debug/output-metadata.json') -Raw | ConvertFrom-Json
    if ($adaMetadata.applicationId -ne $adaPackage) { throw 'APK identity does not match the isolated validation package; nothing installed' }
    $adaTestMetadata = Get-Content (Join-Path $adaAndroid 'app/build/outputs/apk/androidTest/debug/output-metadata.json') -Raw | ConvertFrom-Json
    if ($adaTestMetadata.applicationId -ne $adaTestPackage) { throw 'Test APK identity does not match the isolated runner; nothing installed' }
    Invoke-AdaAdb -Arguments @('install','--user','0',(Join-Path $adaAndroid 'app/build/outputs/apk/debug/app-debug.apk')) | Out-Null
    $adaInstalled = $true
    Invoke-AdaAdb -Arguments @('install','--user','0',(Join-Path $adaAndroid 'app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk')) | Out-Null
    $adaRandom = [byte[]]::new(32); [Security.Cryptography.RandomNumberGenerator]::Fill($adaRandom)
    $adaSecret = [Convert]::ToHexString($adaRandom).ToLowerInvariant()
    $env:ADA_WEB_TEST_TOKEN = $adaSecret
    $adaServer = Start-Process -FilePath (Join-Path $adaRoot '.venv/Scripts/python.exe') -ArgumentList @('scripts/client_test_server.py','--port',"$Port",'--android-chat-fixtures','--security-fixtures','--workspace-temp') -WorkingDirectory $adaRoot -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $adaTemp 'server-out.log') -RedirectStandardError (Join-Path $adaTemp 'server-error.log')
    $env:ADA_WEB_TEST_TOKEN = $adaPriorToken
    $adaReady = $false
    for ($adaAttempt=0; $adaAttempt -lt 40; $adaAttempt++) {
        if ($adaServer.HasExited) { throw 'Owned fixture exited before readiness' }
        try { if ((Invoke-WebRequest "$adaOrigin/health/ready" -TimeoutSec 2).StatusCode -eq 200) { $adaReady = $true; break } } catch { Start-Sleep -Milliseconds 500 }
    }
    if (-not $adaReady) { throw 'Owned fixture is not ready' }
    Invoke-AdaAdb -Arguments @('reverse',"tcp:$Port","tcp:$Port") | Out-Null; $adaReverse = $true
    Invoke-AdaAdb -Arguments @('shell','run-as',$adaPackage,'mkdir','-p','files') | Out-Null
    $adaPipeInfo = [Diagnostics.ProcessStartInfo]::new($adaAdb)
    $adaPipeInfo.UseShellExecute = $false; $adaPipeInfo.CreateNoWindow = $true
    $adaPipeInfo.RedirectStandardInput = $true; $adaPipeInfo.RedirectStandardOutput = $true; $adaPipeInfo.RedirectStandardError = $true
    foreach ($adaArgument in @('-s',$Device,'shell','run-as',$adaPackage,'sh','-c','"cat > files/foundation-test-token"')) { $adaPipeInfo.ArgumentList.Add($adaArgument) }
    $adaPipe = [Diagnostics.Process]::Start($adaPipeInfo)
    $adaPipe.StandardInput.Write($adaSecret); $adaPipe.StandardInput.Close(); $adaPipe.WaitForExit()
    if ($adaPipe.ExitCode -ne 0) { throw 'App-private credential provisioning failed' }
    $adaPipe.Dispose(); $adaSecret = $null
    $adaClasses = 'dev.ada.assistant.VoicePlatformAvailabilityTest,dev.ada.assistant.VoiceUiHttpTest,dev.ada.assistant.StreamingUiHttpTest,dev.ada.assistant.MemoryUiSmokeTest'
    $adaResult = Invoke-AdaAdb -Arguments @('shell','am','instrument','--user','0','-w','-e','adaTestOrigin',$adaOrigin,'-e','class',$adaClasses,"$adaTestPackage/androidx.test.runner.AndroidJUnitRunner")
    $adaResult | Write-Output
    if (($adaResult -join "`n") -notmatch 'OK \([0-9]+ tests?\)' -or ($adaResult -join "`n") -match 'FAILURES!!!') { throw 'Physical verification did not pass' }
    if ($IncludePermissionDialogs) {
        foreach ($adaPermissionCase in @('firstGrantPreservesOwnDialogIntent','verifiedDenialAndRepeatedDenialRemainActionable')) {
            # Revocation can kill the target process: reset outside instrumentation.
            Invoke-AdaAdb -Arguments @('shell','pm','revoke','--user','0',$adaPackage,'android.permission.RECORD_AUDIO') | Out-Null
            Invoke-AdaAdb -Arguments @('shell','pm','clear-permission-flags','--user','0',$adaPackage,'android.permission.RECORD_AUDIO','user-set','user-fixed') | Out-Null
            $adaPermissionResult = Invoke-AdaAdb -Arguments @('shell','am','instrument','--user','0','-w','-e','adaTestOrigin',$adaOrigin,'-e','class',"dev.ada.assistant.VoicePermissionDialogTest#$adaPermissionCase","$adaTestPackage/androidx.test.runner.AndroidJUnitRunner")
            $adaPermissionResult | Write-Output
            if (($adaPermissionResult -join "`n") -notmatch 'OK \(1 test\)') { throw 'Verified OS permission-dialog case failed' }
        }
    }
    foreach ($adaStage in @(
        @{ Prepare='saveEditedDraftBeforeActualForceStop'; Resume='editedDraftRestoresForReviewWithoutAutomaticSubmission'; Key='voiceDraftKey' },
        @{ Prepare='reserveAndSubmitReviewedVoiceBeforeActualForceStop'; Resume='originalReviewedRequestRestoresByGetAndDoesNotAllocateANewTurn'; Key='voiceRequestKey' }
    )) {
        $adaPrepared = Invoke-AdaAdb -Arguments @('shell','am','instrument','--user','0','-w','-e','adaTestOrigin',$adaOrigin,'-e','adaVoiceRecovery','true','-e','class',"dev.ada.assistant.VoiceRecoveryPrepareTest#$($adaStage.Prepare)","$adaTestPackage/androidx.test.runner.AndroidJUnitRunner")
        if (($adaPrepared -join "`n") -notmatch 'OK \(1 test\)') { throw 'Force-stop preparation failed' }
        $adaKey = [regex]::Match(($adaPrepared -join "`n"), "$($adaStage.Key)=([0-9a-f-]{36})")
        if (-not $adaKey.Success) { throw 'Prepared recovery ID was not reported' }
        Invoke-AdaAdb -Arguments @('shell','am','force-stop','--user','0',$adaPackage) | Out-Null
        $adaResumed = Invoke-AdaAdb -Arguments @('shell','am','instrument','--user','0','-w','-e','adaTestOrigin',$adaOrigin,'-e','adaVoiceRecovery','true','-e','expectedVoiceKey',$adaKey.Groups[1].Value,'-e','class',"dev.ada.assistant.VoiceRecoveryResumeTest#$($adaStage.Resume)","$adaTestPackage/androidx.test.runner.AndroidJUnitRunner")
        if (($adaResumed -join "`n") -notmatch 'OK \(1 test\)') { throw 'Force-stop recovery failed' }
        Write-Output 'Exact voice recovery stage passed after actual force-stop'
    }
    $adaSecurityResult = Invoke-AdaAdb -Arguments @('shell','am','instrument','--user','0','-w','-e','adaTestOrigin',$adaOrigin,'-e','class','dev.ada.assistant.SecurityUiHttpTest',"$adaTestPackage/androidx.test.runner.AndroidJUnitRunner")
    $adaSecurityResult | Write-Output
    if (($adaSecurityResult -join "`n") -notmatch 'OK \(1 test\)') { throw 'Device credential and privacy HTTP validation failed' }
    if ($NativeFocusProbe) {
        & (Join-Path $adaAndroid 'gradlew.bat') -p $adaAndroid :focus-fixture:assembleDebug --console=plain
        if ($LASTEXITCODE -ne 0) { throw 'Focus fixture build failed' }
        Invoke-AdaAdb -Arguments @('install','--user','0',(Join-Path $adaAndroid 'focus-fixture/build/outputs/apk/debug/focus-fixture-debug.apk')) | Out-Null
        $adaFocusInstalled = $true
        Invoke-AdaAdb -Arguments @('shell','am','start','--user','0','-n',"$adaPackage/dev.ada.assistant.audio.AudioFocusProbeActivity") | Out-Null
        Write-Output 'Manual native check: tap Play public focus sample; open ADA focus fixture and request full, transient and duck focus separately. Confirm OS granted state, adapter interruption callback and audible stopping independently. No automatic resume should occur. This runner does not assert audible results.'
        Read-Host 'Press Enter after recording the native observations in your validation notes' | Out-Null
    }
} finally {
    $env:ADA_WEB_TEST_TOKEN = $adaPriorToken; $adaSecret = $null
    if ($adaReverse) { & $adaAdb -s $Device reverse --remove "tcp:$Port" | Out-Null }
    if ($adaInstalled) {
        & $adaAdb -s $Device shell am force-stop --user 0 $adaPackage | Out-Null
        & $adaAdb -s $Device shell pm uninstall --user 0 $adaTestPackage | Out-Null
        & $adaAdb -s $Device shell pm uninstall --user 0 $adaPackage | Out-Null
    }
    if ($adaFocusInstalled) { & $adaAdb -s $Device shell pm uninstall --user 0 dev.ada.validation.focus.debug | Out-Null }
    if ($adaServer -and -not $adaServer.HasExited) { Stop-Process -Id $adaServer.Id }
}
