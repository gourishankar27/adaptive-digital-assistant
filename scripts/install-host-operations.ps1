param([Parameter(Mandatory)][string]$Config, [ValidateSet('Plan','Install','Remove')][string]$Mode = 'Plan')
$ErrorActionPreference = 'Stop'
if ($PSVersionTable.PSEdition -eq 'Desktop') {
    Import-Module (Join-Path $PSHOME 'Modules/CimCmdlets') -ErrorAction Stop
    Import-Module (Join-Path $PSHOME 'Modules/ScheduledTasks') -ErrorAction Stop
}
$adaRepo = Split-Path -Parent $PSScriptRoot
$adaPython = Join-Path $adaRepo '.venv/Scripts/python.exe'
$adaResult = & $adaPython -m ada.host_ops check-config --config $Config
if ($LASTEXITCODE -ne 0) { throw 'Protected host configuration validation failed.' }
$adaMetadata = $adaResult | ConvertFrom-Json
if ([IO.Path]::GetFullPath($adaMetadata.repository) -ne [IO.Path]::GetFullPath($adaRepo)) { throw 'Task repository differs from this checkout.' }
$adaPythonw = (Join-Path $adaRepo '.venv/Scripts/pythonw.exe').Replace('\','/')
if (-not (Test-Path -LiteralPath $adaPythonw)) { throw 'Pinned repository Python windowless runtime is missing.' }
$adaHash = [Security.Cryptography.SHA256]::Create()
try { $adaSuffix = ([BitConverter]::ToString($adaHash.ComputeHash([Text.Encoding]::UTF8.GetBytes($adaMetadata.owner_sid)))).Replace('-','').Substring(0,12) }
finally { $adaHash.Dispose() }
$adaPrincipal = New-ScheduledTaskPrincipal -UserId $adaMetadata.owner_sid -LogonType Interactive -RunLevel Limited
$adaFolder = Split-Path -Parent $Config
if ($Mode -eq 'Install') {
    & $adaPython -m ada.host_ops check-key --config $Config
    if ($LASTEXITCODE -ne 0) { throw 'Enroll and rehearse the backup key before installing tasks.' }
    foreach ($adaKind in @('Supervisor','Backup')) {
        if (Get-ScheduledTask -TaskName "ADA26-$adaKind-$adaSuffix" -ErrorAction SilentlyContinue) { throw 'Task already exists; review/remove it explicitly rather than overwrite.' }
    }
}
foreach ($adaKind in @('Supervisor','Backup')) {
    $adaName = "ADA26-$adaKind-$adaSuffix"
    if ($Mode -eq 'Remove') {
        $adaExisting = Get-ScheduledTask -TaskName $adaName -ErrorAction SilentlyContinue
        if (-not $adaExisting) { continue }
        if ($adaExisting.Actions.Count -ne 1 -or $adaExisting.Actions[0].WorkingDirectory.Replace('\','/').TrimEnd('/') -ne $adaMetadata.repository.TrimEnd('/') -or -not $adaExisting.Actions[0].Arguments.Contains($adaMetadata.config)) { throw 'Task belongs to another installation/configuration.' }
        # Stop cooperatively first; do not Stop-ScheduledTask/kill external provider processes.
        if ($adaKind -eq 'Supervisor') {
            $adaStatePath = Join-Path $adaFolder 'supervisor.json'
            if (Test-Path -LiteralPath $adaStatePath) {
                & $adaPython -m ada.host_ops stop --config $Config
                $adaDeadline = [DateTime]::UtcNow.AddSeconds(45)
                do {
                    $adaState = Get-Content -LiteralPath $adaStatePath -Raw | ConvertFrom-Json
                    $adaStopped = $adaState.state -eq 'stopped' -and -not $adaState.child_pid -and -not $adaState.proxy_pid
                    if (-not $adaStopped) { Start-Sleep -Milliseconds 250 }
                } until ($adaStopped -or [DateTime]::UtcNow -ge $adaDeadline)
                if (-not $adaStopped) { throw 'Supervisor stop is unconfirmed; task was not removed.' }
            }
        }
        Unregister-ScheduledTask -TaskName $adaName -Confirm:$false
        continue
    }
    $adaVerb = if ($adaKind -eq 'Supervisor') { 'supervise' } else { 'backup' }
    $adaArguments = '-m ada.host_ops ' + $adaVerb + ' --config "' + $adaMetadata.config + '"'
    $adaAction = New-ScheduledTaskAction -Execute $adaPythonw -Argument $adaArguments -WorkingDirectory $adaRepo.Replace('\','/')
    $adaTrigger = if ($adaKind -eq 'Supervisor') { New-ScheduledTaskTrigger -AtLogOn -User $adaMetadata.owner_sid } else { New-ScheduledTaskTrigger -Daily -At $adaMetadata.daily_backup_time }
    $adaLimit = if ($adaKind -eq 'Supervisor') { [TimeSpan]::Zero } else { New-TimeSpan -Minutes 15 }
    # Bounded recovery of the supervisor itself; its persisted crash-stop still blocks API retries.
    $adaSettings = New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew -StartWhenAvailable -ExecutionTimeLimit $adaLimit -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -RestartCount 2 -RestartInterval (New-TimeSpan -Minutes 1)
    $adaTask = New-ScheduledTask -Action $adaAction -Principal $adaPrincipal -Trigger $adaTrigger -Settings $adaSettings -Description 'ADA Phase26 selected-owner logon operations; no dreaming or public exposure.'
    Export-ScheduledTask -InputObject $adaTask | Set-Content -LiteralPath (Join-Path $adaFolder "$adaKind.task.xml") -Encoding Unicode
    if ($Mode -eq 'Install') {
        Register-ScheduledTask -TaskName $adaName -InputObject $adaTask | Out-Null
    }
    [PSCustomObject]@{ Name = $adaName; Mode = $Mode; Principal = 'Selected interactive owner'; StartsNow = $false }
}
