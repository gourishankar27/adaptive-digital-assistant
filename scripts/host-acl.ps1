param([ValidateSet('Protect','Check')][string]$Action = 'Check', [Parameter(Mandatory)][string]$Path)
$ErrorActionPreference = 'Stop'
# PowerShell7 may pass its module path to a Windows PowerShell5.1 child.
Import-Module (Join-Path $PSHOME 'Modules/Microsoft.PowerShell.Security') -ErrorAction Stop
try {
    $adaItem = Get-Item -LiteralPath $Path -Force
    if (-not $adaItem.PSIsContainer -or ($adaItem.Attributes -band [IO.FileAttributes]::ReparsePoint)) { throw 'Invalid directory' }
    $adaSid = [Security.Principal.WindowsIdentity]::GetCurrent().User
    if ($Action -eq 'Protect') {
        $adaAcl = New-Object Security.AccessControl.DirectorySecurity
        $adaAcl.SetOwner($adaSid)
        $adaAcl.SetAccessRuleProtection($true, $false)
        foreach ($adaAllowed in @($adaSid, [Security.Principal.SecurityIdentifier]'S-1-5-18')) {
            $adaRule = New-Object Security.AccessControl.FileSystemAccessRule($adaAllowed, 'FullControl', 'ContainerInherit,ObjectInherit', 'None', 'Allow')
            $adaAcl.AddAccessRule($adaRule)
        }
        Set-Acl -LiteralPath $Path -AclObject $adaAcl
    }
    $adaAcl = Get-Acl -LiteralPath $Path
    if (-not $adaAcl.AreAccessRulesProtected -or $adaAcl.GetOwner([Security.Principal.SecurityIdentifier]).Value -ne $adaSid.Value) { throw 'Unexpected owner/inheritance' }
    $adaOwnerAllowed = $false
    foreach ($adaRule in $adaAcl.GetAccessRules($true, $true, [Security.Principal.SecurityIdentifier])) {
        if ($adaRule.AccessControlType -ne 'Allow' -or $adaRule.IdentityReference.Value -notin @($adaSid.Value, 'S-1-5-18')) { throw 'Unexpected access rule' }
        if ($adaRule.IdentityReference.Value -eq $adaSid.Value -and ($adaRule.FileSystemRights -band [Security.AccessControl.FileSystemRights]::FullControl) -eq [Security.AccessControl.FileSystemRights]::FullControl) { $adaOwnerAllowed = $true }
    }
    if (-not $adaOwnerAllowed) { throw 'Owner access missing' }
    exit 0
} catch { Write-Error 'Protected owner directory validation failed.'; exit 1 }
