param([string]$Device = 'emulator-5556')
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
$adaTemporary = Join-Path $adaAndroid '.gradle/episode-emulator-check'
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
    $adaHelper = Start-Process -FilePath $adaPython -ArgumentList @('scripts/client_test_server.py', '--port', '18764', '--android-chat-fixtures', '--workspace-temp') -WorkingDirectory $adaRepository -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $adaTemporary 'server-stdout.log') -RedirectStandardError (Join-Path $adaTemporary 'server-stderr.log')
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
    & $adaGradle -p $adaAndroid connectedDebugAndroidTest --console=plain '-Pandroid.testInstrumentationRunnerArguments.class=dev.ada.assistant.EpisodeUiHttpTest,dev.ada.assistant.AgentUiHttpTest'
    if ($LASTEXITCODE -ne 0) { throw 'Owned episode UI HTTP verification failed' }
    # The connected Gradle task uninstalls both APKs after its selected suite.
    & $adaAdb -s $Device install -r (Join-Path $adaAndroid 'app/build/outputs/apk/debug/app-debug.apk')
    if ($LASTEXITCODE -ne 0) { throw 'Staged recovery app installation failed' }
    & $adaAdb -s $Device install -r (Join-Path $adaAndroid 'app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk')
    if ($LASTEXITCODE -ne 0) { throw 'Staged recovery runner installation failed' }
    Set-AdaPrivateTestCredential -AdbPath $adaAdb -SelectedDevice $Device -Credential $adaCredential
    $adaPrepared = & $adaAdb -s $Device shell am instrument -w -e adaEpisodeRecovery true -e class 'dev.ada.assistant.EpisodeRecoveryPrepareTest#prepareCommittedQueueWithoutDelivery' dev.ada.assistant.debug.test/androidx.test.runner.AndroidJUnitRunner
    if ($LASTEXITCODE -ne 0 -or ($adaPrepared -join "`n") -notmatch 'OK \(1 test\)') { throw 'Episode queue recovery preparation failed' }
    $adaRun = [regex]::Match(($adaPrepared -join "`n"), 'recoveryEpisodeJob=([0-9a-fA-F-]{36})')
    if (-not $adaRun.Success) { throw 'Episode recovery UUID metadata missing' }
    & $adaAdb -s $Device shell am force-stop dev.ada.assistant.debug
    if ($LASTEXITCODE -ne 0) { throw 'Episode recovery force-stop failed' }
    $adaRecovered = & $adaAdb -s $Device shell am instrument -w -e adaEpisodeRecovery true -e expectedEpisodeJob $adaRun.Groups[1].Value -e class 'dev.ada.assistant.EpisodeRecoveryResumeTest#exactJobIsRestoredByGetAfterActualForceStop' dev.ada.assistant.debug.test/androidx.test.runner.AndroidJUnitRunner
    if ($LASTEXITCODE -ne 0 -or ($adaRecovered -join "`n") -notmatch 'OK \(1 test\)') { throw 'Episode recovery after actual force-stop failed' }
    Write-Output 'Episode queue force-stop recovery: 2 stages passed; GET restored the original owned job.'
    $adaLaunch = & $adaAdb -s $Device shell am start -S -W -n dev.ada.assistant.debug/dev.ada.assistant.MainActivity
    if ($LASTEXITCODE -ne 0 -or ($adaLaunch -join "`n") -notmatch '(?m)^Status: ok\s*$') { throw 'Emulator cold launch did not confirm success' }
    Write-Output 'Emulator cold launch: Status ok.'
} finally {
    $adaInstalled = & $adaAdb -s $Device shell pm path dev.ada.assistant.debug
    if ($adaInstalled) { & $adaAdb -s $Device shell run-as dev.ada.assistant.debug rm -f files/foundation-test-token }
    if ($adaHelper -and -not $adaHelper.HasExited) { Stop-Process -Id $adaHelper.Id }
    $env:ADA_WEB_TEST_TOKEN = $adaPriorTestCredential
    $env:ANDROID_SERIAL = $adaPriorSerial
    $adaCredential = $null
}

