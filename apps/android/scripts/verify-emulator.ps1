param([string]$Device = 'emulator-5554')
$ErrorActionPreference = 'Stop'
$adaPriorSerial = $env:ANDROID_SERIAL
$adaPriorTestCredential = $env:ADA_WEB_TEST_TOKEN
$adaAndroid = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$adaRepository = (Resolve-Path (Join-Path $adaAndroid '../..')).Path
$adaPython = Join-Path $adaRepository '.venv/Scripts/python.exe'
$adaSdk = $env:ANDROID_HOME
if (-not $adaSdk) { $adaSdk = Join-Path $env:LOCALAPPDATA 'Android/Sdk' }
$adaAdb = Join-Path $adaSdk 'platform-tools/adb.exe'
$adaGradle = Join-Path $adaAndroid 'gradlew.bat'
$adaTemporary = Join-Path $adaAndroid '.gradle/emulator-check'
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
    $adaHelper = Start-Process -FilePath $adaPython -ArgumentList @('scripts/client_test_server.py', '--port', '18764', '--android-chat-fixtures') -WorkingDirectory $adaRepository -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $adaTemporary 'server-stdout.log') -RedirectStandardError (Join-Path $adaTemporary 'server-stderr.log')
    $env:ADA_WEB_TEST_TOKEN = $adaPriorTestCredential
    $adaReady = $false
    for ($adaAttempt = 0; $adaAttempt -lt 40; $adaAttempt++) {
        if ($adaHelper.HasExited) { throw 'Disposable HTTP test server exited before becoming ready' }
        try {
            $adaHealth = Invoke-WebRequest 'http://127.0.0.1:18764/health/live' -TimeoutSec 2
            if ($adaHealth.StatusCode -eq 200) { $adaReady = $true; break }
        } catch { Start-Sleep -Milliseconds 500 }
    }
    if (-not $adaReady) { throw 'Disposable HTTP test server did not become ready' }
    Set-AdaPrivateTestCredential -AdbPath $adaAdb -SelectedDevice $Device -Credential $adaCredential
    & $adaGradle -p $adaAndroid connectedDebugAndroidTest '-Pandroid.testInstrumentationRunnerArguments.adaHttpIntegration=true' '-Pandroid.testInstrumentationRunnerArguments.notClass=dev.ada.assistant.ProcessRecoveryPrepareTest,dev.ada.assistant.ProcessRecoveryResumeTest' --console=plain
    if ($LASTEXITCODE -ne 0) { throw 'Emulator verification failed' }
    # AGP removes test installations; install the verified debug APK for the launch smoke.
    & $adaAdb -s $Device install -r (Join-Path $adaAndroid 'app/build/outputs/apk/debug/app-debug.apk')
    if ($LASTEXITCODE -ne 0) { throw 'Verified app reinstallation failed' }
    & $adaAdb -s $Device install -r (Join-Path $adaAndroid 'app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk')
    if ($LASTEXITCODE -ne 0) { throw 'Verified test APK reinstallation failed' }
    Set-AdaPrivateTestCredential -AdbPath $adaAdb -SelectedDevice $Device -Credential $adaCredential
    # Separate instrumentation invocations retain data; an actual force-stop removes client memory.
    $adaPrepared = & $adaAdb -s $Device shell am instrument -w -e adaProcessRecovery true -e class 'dev.ada.assistant.ProcessRecoveryPrepareTest#prepareCommittedReplyWithoutDelivery' dev.ada.assistant.debug.test/androidx.test.runner.AndroidJUnitRunner
    if ($LASTEXITCODE -ne 0 -or ($adaPrepared -join "`n") -notmatch 'OK \(1 test\)') { throw 'Committed-reply recovery preparation failed' }
    $adaRequestMatch = [regex]::Match(($adaPrepared -join "`n"), 'recoveryRequest=([0-9a-fA-F-]{36})')
    $adaConversationMatch = [regex]::Match(($adaPrepared -join "`n"), 'recoveryConversation=([0-9a-fA-F-]{36})')
    if (-not $adaRequestMatch.Success -or -not $adaConversationMatch.Success) { throw 'Recovery test UUID metadata missing' }
    & $adaAdb -s $Device shell am force-stop dev.ada.assistant.debug
    if ($LASTEXITCODE -ne 0) { throw 'Recovery process interruption failed' }
    $adaRecovered = & $adaAdb -s $Device shell am instrument -w -e adaProcessRecovery true -e expectedRequest $adaRequestMatch.Groups[1].Value -e expectedConversation $adaConversationMatch.Groups[1].Value -e class 'dev.ada.assistant.ProcessRecoveryResumeTest#recoversCommittedReplyAfterProcessStop' dev.ada.assistant.debug.test/androidx.test.runner.AndroidJUnitRunner
    if ($LASTEXITCODE -ne 0 -or ($adaRecovered -join "`n") -notmatch 'OK \(1 test\)') { throw 'Force-stop recovery verification failed' }
    Write-Output 'Committed reply force-stop recovery: 2 staged checks passed; no duplicate server turn.'
    & $adaAdb -s $Device shell am start -W -n dev.ada.assistant.debug/dev.ada.assistant.MainActivity
    if ($LASTEXITCODE -ne 0) { throw 'Emulator launch failed' }
} finally {
    $adaInstalled = & $adaAdb -s $Device shell pm path dev.ada.assistant.debug
    if ($adaInstalled) { & $adaAdb -s $Device shell run-as dev.ada.assistant.debug rm -f files/foundation-test-token }
    if ($adaHelper -and -not $adaHelper.HasExited) { Stop-Process -Id $adaHelper.Id }
    $env:ADA_WEB_TEST_TOKEN = $adaPriorTestCredential
    $env:ANDROID_SERIAL = $adaPriorSerial
    $adaCredential = $null
}
