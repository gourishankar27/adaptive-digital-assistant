param([string]$Device = 'emulator-5556', [switch]$UiOnly)
$ErrorActionPreference = 'Stop'
if ($Device -notmatch '^emulator-[0-9]+$') { throw 'This disposable verification script accepts an emulator serial only' }
$adaPriorSerial = $env:ANDROID_SERIAL
$adaPriorTestCredential = $env:ADA_WEB_TEST_TOKEN
$adaAndroid = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$adaRepository = (Resolve-Path (Join-Path $adaAndroid '../..')).Path
$adaPython = Join-Path $adaRepository '.venv/Scripts/python.exe'
$adaSdk = $env:ANDROID_HOME
if (-not $adaSdk) { $adaSdk = Join-Path $env:LOCALAPPDATA 'Android/Sdk' }
$adaAdb = Join-Path $adaSdk 'platform-tools/adb.exe'
$adaGradle = Join-Path $adaAndroid 'gradlew.bat'
$adaTemporary = Join-Path $adaAndroid '.gradle/voice-emulator-check'
New-Item -ItemType Directory -Force $adaTemporary | Out-Null
$adaRandom = [byte[]]::new(32)
[Security.Cryptography.RandomNumberGenerator]::Fill($adaRandom)
$adaCredential = [Convert]::ToHexString($adaRandom).ToLowerInvariant()
$adaHelper = $null
function Set-AdaPrivateTestCredential {
    param([string]$AdbPath, [string]$SelectedDevice, [string]$Credential)
    & $AdbPath -s $SelectedDevice shell run-as dev.ada.assistant.debug mkdir -p files
    if ($LASTEXITCODE -ne 0) { throw 'App-private test directory could not be created' }
    $adaPipeInfo = [Diagnostics.ProcessStartInfo]::new($AdbPath)
    $adaPipeInfo.UseShellExecute = $false
    $adaPipeInfo.CreateNoWindow = $true
    $adaPipeInfo.RedirectStandardInput = $true
    $adaPipeInfo.RedirectStandardOutput = $true
    $adaPipeInfo.RedirectStandardError = $true
    foreach ($adaArgument in @('-s', $SelectedDevice, 'shell', 'run-as', 'dev.ada.assistant.debug', 'sh', '-c', '"cat > files/foundation-test-token"')) {
        $adaPipeInfo.ArgumentList.Add($adaArgument)
    }
    $adaPipe = [Diagnostics.Process]::Start($adaPipeInfo)
    $adaPipe.StandardInput.Write($Credential)
    $adaPipe.StandardInput.Close()
    $adaPipe.WaitForExit()
    if ($adaPipe.ExitCode -ne 0) { throw 'App-private test credential could not be provisioned' }
    $adaPipe.Dispose()
}
try {
    $env:ANDROID_SERIAL = $Device
    & $adaGradle -p $adaAndroid assembleDebug assembleDebugAndroidTest --console=plain
    if ($LASTEXITCODE -ne 0) { throw 'Android build failed' }
    & $adaAdb -s $Device install -r (Join-Path $adaAndroid 'app/build/outputs/apk/debug/app-debug.apk')
    if ($LASTEXITCODE -ne 0) { throw 'App installation failed' }
    $env:ADA_WEB_TEST_TOKEN = $adaCredential
    $adaHelper = Start-Process -FilePath $adaPython -ArgumentList @('scripts/client_test_server.py', '--port', '18765', '--android-chat-fixtures', '--workspace-temp') -WorkingDirectory $adaRepository -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $adaTemporary 'server-stdout.log') -RedirectStandardError (Join-Path $adaTemporary 'server-stderr.log')
    $env:ADA_WEB_TEST_TOKEN = $adaPriorTestCredential
    $adaReady = $false
    for ($adaAttempt = 0; $adaAttempt -lt 40; $adaAttempt++) {
        if ($adaHelper.HasExited) { throw 'Disposable HTTP test server exited before becoming ready' }
        try {
            $adaHealth = Invoke-WebRequest 'http://127.0.0.1:18765/health/live' -TimeoutSec 2
            if ($adaHealth.StatusCode -eq 200) { $adaReady = $true; break }
        } catch { Start-Sleep -Milliseconds 500 }
    }
    if (-not $adaReady) { throw 'Disposable HTTP test server did not become ready' }
    Set-AdaPrivateTestCredential -AdbPath $adaAdb -SelectedDevice $Device -Credential $adaCredential
    $adaClasses = if ($UiOnly) { 'dev.ada.assistant.VoiceUiHttpTest' } else { 'dev.ada.assistant.VoicePlatformAvailabilityTest,dev.ada.assistant.VoiceUiHttpTest,dev.ada.assistant.MemoryUiSmokeTest' }
    & $adaGradle -p $adaAndroid connectedDebugAndroidTest --console=plain "-Pandroid.testInstrumentationRunnerArguments.class=$adaClasses"
    if ($LASTEXITCODE -ne 0) { throw 'Owned voice UI HTTP verification failed' }
    if ($UiOnly) { return }
    # The connected Gradle task uninstalls both APKs after its selected suite.
    & $adaAdb -s $Device install -r (Join-Path $adaAndroid 'app/build/outputs/apk/debug/app-debug.apk')
    if ($LASTEXITCODE -ne 0) { throw 'Staged recovery app installation failed' }
    & $adaAdb -s $Device install -r (Join-Path $adaAndroid 'app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk')
    if ($LASTEXITCODE -ne 0) { throw 'Staged recovery runner installation failed' }
    Set-AdaPrivateTestCredential -AdbPath $adaAdb -SelectedDevice $Device -Credential $adaCredential
    foreach ($adaStage in @(
        @{ Prepare='saveEditedDraftBeforeActualForceStop'; Resume='editedDraftRestoresForReviewWithoutAutomaticSubmission'; Key='voiceDraftKey' },
        @{ Prepare='reserveAndSubmitReviewedVoiceBeforeActualForceStop'; Resume='originalReviewedRequestRestoresByGetAndDoesNotAllocateANewTurn'; Key='voiceRequestKey' }
    )) {
        $adaPrepared = & $adaAdb -s $Device shell am instrument -w -e adaVoiceRecovery true -e class "dev.ada.assistant.VoiceRecoveryPrepareTest#$($adaStage.Prepare)" dev.ada.assistant.debug.test/androidx.test.runner.AndroidJUnitRunner
        $adaPrepared | Write-Output
        if ($LASTEXITCODE -ne 0 -or ($adaPrepared -join "`n") -notmatch 'OK \(1 test\)') { throw 'Voice recovery preparation failed' }
        $adaMatchedKey = [regex]::Match(($adaPrepared -join "`n"), "$($adaStage.Key)=([0-9a-f-]{36})")
        if (-not $adaMatchedKey.Success) { throw 'Voice recovery key was not reported' }
        & $adaAdb -s $Device shell am force-stop dev.ada.assistant.debug
        if ($LASTEXITCODE -ne 0) { throw 'Actual force-stop failed' }
        $adaResumed = & $adaAdb -s $Device shell am instrument -w -e adaVoiceRecovery true -e expectedVoiceKey $adaMatchedKey.Groups[1].Value -e class "dev.ada.assistant.VoiceRecoveryResumeTest#$($adaStage.Resume)" dev.ada.assistant.debug.test/androidx.test.runner.AndroidJUnitRunner
        $adaResumed | Write-Output
        if ($LASTEXITCODE -ne 0 -or ($adaResumed -join "`n") -notmatch 'OK \(1 test\)') { throw 'Voice recovery resume failed' }
    }

} finally {
    $adaInstalled = & $adaAdb -s $Device shell pm path dev.ada.assistant.debug
    if ($adaInstalled) { & $adaAdb -s $Device shell run-as dev.ada.assistant.debug rm -f files/foundation-test-token }
    if ($adaHelper -and -not $adaHelper.HasExited) { Stop-Process -Id $adaHelper.Id }
    $env:ADA_WEB_TEST_TOKEN = $adaPriorTestCredential
    $env:ANDROID_SERIAL = $adaPriorSerial
    $adaCredential = $null
}

