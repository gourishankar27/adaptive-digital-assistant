[CmdletBinding(SupportsShouldProcess)]
param([ValidateSet('Snapshot','ApplyAcAwake','Restore')][string]$Action = 'Snapshot', [Parameter(Mandatory)][string]$Snapshot, [switch]$IncludeLid)
$ErrorActionPreference = 'Stop'
# Read/modify only the selected active scheme's AC settings. DC, firewall and login remain unchanged.
$adaSchemeText = & powercfg.exe /getactivescheme
if ($LASTEXITCODE -ne 0 -or $adaSchemeText -notmatch '[0-9a-fA-F]{8}(-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}') { throw 'Cannot read active power scheme.' }
$adaScheme = $Matches[0]
$adaItems = @(@{Group='SUB_SLEEP'; Setting='STANDBYIDLE'}, @{Group='SUB_SLEEP'; Setting='HIBERNATEIDLE'})
if ($IncludeLid) { $adaItems += @{Group='SUB_BUTTONS'; Setting='LIDACTION'} }
function Get-AdaAcValue($adaGroup, $adaSetting) {
    $adaText = (& powercfg.exe /qh $adaScheme $adaGroup $adaSetting) -join "`n"
    $adaValues = [regex]::Matches($adaText, '0x[0-9a-fA-F]{8}')
    if ($LASTEXITCODE -ne 0 -or $adaValues.Count -lt 2) { throw 'Cannot parse AC/DC power values safely.' }
    # Numeric ranges can also be hex. AC/DC are the final two indexes, independent of UI language.
    return [Convert]::ToInt32($adaValues[$adaValues.Count - 2].Value.Substring(2),16)
}
if ($Action -eq 'Snapshot') {
    if (Test-Path -LiteralPath $Snapshot) { throw 'Power snapshot already exists; do not overwrite originals.' }
    $adaValues = @($adaItems | ForEach-Object { @{group=$_.Group; setting=$_.Setting; original_ac=(Get-AdaAcValue $_.Group $_.Setting)} })
    @{format='ada-ac-power-v1'; scheme=$adaScheme; values=$adaValues} | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $Snapshot -Encoding UTF8
    return
}
$adaSaved = Get-Content -LiteralPath $Snapshot -Raw | ConvertFrom-Json
if ($adaSaved.format -ne 'ada-ac-power-v1' -or $adaSaved.scheme -ne $adaScheme) { throw 'Active scheme differs from the saved originals.' }
foreach ($adaItem in $adaSaved.values) {
    if ($adaItem.group -notin @('SUB_SLEEP','SUB_BUTTONS') -or $adaItem.setting -notin @('STANDBYIDLE','HIBERNATEIDLE','LIDACTION') -or [int]$adaItem.original_ac -lt 0) { throw 'Invalid saved power setting.' }
    if ($Action -eq 'ApplyAcAwake' -and $adaItem.setting -eq 'LIDACTION' -and -not $IncludeLid) { continue }
    $adaValue = if ($Action -eq 'Restore') { [int]$adaItem.original_ac } else { 0 }
    if ($Action -eq 'Restore' -and (Get-AdaAcValue $adaItem.group $adaItem.setting) -notin @(0, [int]$adaItem.original_ac)) { throw 'Power setting changed independently; refusing to overwrite it.' }
    if ($PSCmdlet.ShouldProcess('Selected active scheme AC setting', $Action)) {
        & powercfg.exe /setacvalueindex $adaScheme $adaItem.group $adaItem.setting $adaValue
        if ($LASTEXITCODE -ne 0) { throw 'Power setting update failed.' }
    }
}
if (-not $WhatIfPreference) { & powercfg.exe /setactive $adaScheme; if ($LASTEXITCODE -ne 0) { throw 'Power scheme refresh failed.' } }
