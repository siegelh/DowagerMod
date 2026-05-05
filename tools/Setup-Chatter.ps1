#requires -Version 5.0
<#
.SYNOPSIS
    Interactive setup for the DowagerMod Chatter sidecar.

.DESCRIPTION
    Writes an Azure Foundry config to %LOCALAPPDATA%\DowagerMod\chatter\config.json
    with restrictive ACLs (current user only). Idempotent — re-running edits in
    place. Optionally registers a Windows scheduled task to start the sidecar
    at logon.

.EXAMPLE
    .\tools\Setup-Chatter.ps1
#>

[CmdletBinding()]
param(
    [string] $Endpoint = "https://hasiegeltestingfoundry.services.ai.azure.com/openai/v1",
    [string] $Deployment = "gpt-5.4-mini",
    [string] $ApiKey,
    [switch] $RegisterScheduledTask,
    [switch] $NoPrompt
)

$ErrorActionPreference = 'Stop'

$configDir = Join-Path $env:LOCALAPPDATA 'DowagerMod\chatter'
$configPath = Join-Path $configDir 'config.json'

Write-Host ""
Write-Host "DowagerMod Chatter setup" -ForegroundColor Cyan
Write-Host "========================="
Write-Host ""

if (-not (Test-Path $configDir)) {
    New-Item -ItemType Directory -Path $configDir -Force | Out-Null
    Write-Host "Created: $configDir"
}

# Load existing config if present (so re-run is idempotent)
$existing = @{}
if (Test-Path $configPath) {
    try {
        $existing = Get-Content -Path $configPath -Raw | ConvertFrom-Json -AsHashtable
        Write-Host "Existing config found at $configPath; will edit in place."
    } catch {
        Write-Warning "Existing config at $configPath is unreadable; will overwrite."
        $existing = @{}
    }
}

if (-not $NoPrompt) {
    if (-not $Endpoint) { $Endpoint = Read-Host "Endpoint URL" }
    elseif ($existing.endpoint -and $existing.endpoint -ne $Endpoint) {
        $reply = Read-Host "Endpoint [$Endpoint] (Enter to keep)"
        if ($reply) { $Endpoint = $reply }
    }
    if (-not $Deployment) { $Deployment = Read-Host "Deployment name" }
    elseif ($existing.deployment -and $existing.deployment -ne $Deployment) {
        $reply = Read-Host "Deployment [$Deployment] (Enter to keep)"
        if ($reply) { $Deployment = $reply }
    }
    if (-not $ApiKey) {
        $hasExistingKey = ($existing -and $existing.ContainsKey('api_key') -and $existing.api_key)
        if ($hasExistingKey) {
            $secure = Read-Host "API Key (input hidden, press Enter to keep existing)" -AsSecureString
        } else {
            $secure = Read-Host "API Key (input hidden)" -AsSecureString
        }
        $bstr = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
        try {
            $entered = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($bstr)
        } finally {
            [System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
        }
        if ($entered) {
            $ApiKey = $entered
        } elseif ($hasExistingKey) {
            $ApiKey = $existing.api_key
            $script:KeyUnchanged = $true
        }
    }
}

if (-not $ApiKey) {
    Write-Error "API key is required. Re-run interactively or pass -ApiKey."
    exit 2
}

# Build config (preserving any non-required fields the user has customized)
$config = [ordered]@{
    "_comment" = "DowagerMod Chatter sidecar config. NEVER COMMIT THIS FILE. NEVER SHARE THIS KEY."
    endpoint = $Endpoint
    deployment = $Deployment
    api_key = $ApiKey
    enabled = $true
    max_tokens = 80
    max_tokens_multi_turn = 400
    request_timeout_seconds = 8
    rate_limit_seconds = 1.0
    max_in_flight = 4
    circuit_breaker = @{ failure_threshold = 3; open_seconds = 120 }
    spool_poll_interval_seconds = 0.5
    request_ttl_seconds = 60
    response_ttl_seconds = 3600
    log_level = "INFO"
}

# Preserve user customizations from existing config (override defaults but not the ones we just set)
foreach ($key in @('max_tokens','max_tokens_multi_turn','request_timeout_seconds','rate_limit_seconds',
                   'max_in_flight','spool_poll_interval_seconds','request_ttl_seconds',
                   'response_ttl_seconds','log_level','enabled')) {
    if ($existing.ContainsKey($key)) {
        $config[$key] = $existing[$key]
    }
}
if ($existing.ContainsKey('circuit_breaker')) { $config['circuit_breaker'] = $existing['circuit_breaker'] }

$json = $config | ConvertTo-Json -Depth 10
[IO.File]::WriteAllText($configPath, $json, [Text.UTF8Encoding]::new($false))

# Restrict ACL: only current user has full control
try {
    $user = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
    & icacls.exe $configPath /inheritance:r /grant:r "${user}:F" 2>&1 | Out-Null
    & icacls.exe $configDir /inheritance:r /grant:r "${user}:(OI)(CI)F" 2>&1 | Out-Null
    Write-Host "ACLs restricted to: $user"
} catch {
    Write-Warning "Could not lock down ACLs: $_"
}

Write-Host ""
Write-Host "Wrote config: $configPath" -ForegroundColor Green
Write-Host "Endpoint:    $Endpoint"
Write-Host "Deployment:  $Deployment"
if ($script:KeyUnchanged) {
    Write-Host "API key:     (unchanged)"
} else {
    $redacted = if ($ApiKey.Length -gt 8) { $ApiKey.Substring(0,4) + "..." + $ApiKey.Substring($ApiKey.Length - 4) } else { "***" }
    Write-Host "API key:     $redacted"
}
Write-Host ""

if ($RegisterScheduledTask) {
    Write-Host "Registering Windows scheduled task to auto-start at logon..."
    $taskName = "DowagerMod-Chatter"
    $startScript = Join-Path $PSScriptRoot 'Start-Chatter.ps1'
    $action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -WindowStyle Hidden -File `"$startScript`""
    $trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
    $settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -DontStopIfGoingOnBatteries -AllowStartIfOnBatteries
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Force | Out-Null
    Write-Host "Registered task '$taskName'."
}

Write-Host "Done. Start the daemon with: .\tools\Start-Chatter.ps1" -ForegroundColor Cyan
