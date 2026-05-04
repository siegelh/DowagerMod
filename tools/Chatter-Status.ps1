#requires -Version 5.0
<#
.SYNOPSIS
    Show DowagerMod Chatter sidecar status.

.EXAMPLE
    .\tools\Chatter-Status.ps1
#>

$ErrorActionPreference = 'Continue'

. (Join-Path $PSScriptRoot 'Chatter-Common.ps1')

$configDir = Join-Path $env:LOCALAPPDATA 'DowagerMod\chatter'
$configPath = Join-Path $configDir 'config.json'
$spoolDir = Get-ChatterSpoolDir
$pidFile = Get-ChatterPidFile
$daemonLog = Get-ChatterDaemonLog
$chatterLog = Get-ChatterGameLog

Write-Host ""
Write-Host "DowagerMod Chatter status" -ForegroundColor Cyan
Write-Host "========================="
Write-Host ""

# Config
Write-Host "Config dir:       $configDir"
if (Test-Path $configPath) {
    Write-Host "Config file:      $configPath  (present)" -ForegroundColor Green
    try {
        $cfg = Get-Content -Path $configPath -Raw | ConvertFrom-Json
        $key = $cfg.api_key
        $redacted = if ($key -and $key.Length -gt 8) { $key.Substring(0,4) + "..." + $key.Substring($key.Length - 4) }
                    elseif ($key) { "***" }
                    else { "<empty>" }
        Write-Host "  endpoint:       $($cfg.endpoint)"
        Write-Host "  deployment:     $($cfg.deployment)"
        Write-Host "  api_key:        $redacted"
        Write-Host "  enabled:        $($cfg.enabled)"
    } catch {
        Write-Warning "Could not parse config: $_"
    }
} else {
    Write-Host "Config file:      $configPath  (MISSING)" -ForegroundColor Yellow
    Write-Host "  Run .\tools\Setup-Chatter.ps1 to create it."
}

Write-Host ""
Write-Host "Spool dir:        $spoolDir"
if (Test-Path $spoolDir) {
    $req = (Get-ChildItem -Path $spoolDir -Filter 'req-*.json' -ErrorAction SilentlyContinue).Count
    $resp = (Get-ChildItem -Path $spoolDir -Filter 'resp-*.json' -ErrorAction SilentlyContinue).Count
    Write-Host "  pending requests:  $req"
    Write-Host "  unread responses:  $resp"
} else {
    Write-Host "  (does not exist yet)"
}

Write-Host ""
Write-Host "Daemon:"
if (Test-Path $pidFile) {
    try {
        $pidJson = Get-Content -Path $pidFile -Raw | ConvertFrom-Json
        $daemonPid = [int]$pidJson.pid
        $heartbeat = [double]$pidJson.heartbeat_unix
        $age = [DateTimeOffset]::Now.ToUnixTimeSeconds() - $heartbeat
        try {
            $proc = Get-Process -Id $daemonPid -ErrorAction Stop
            Write-Host "  status:          RUNNING (PID=$daemonPid, last heartbeat $([math]::Round($age,1))s ago)" -ForegroundColor Green
        } catch {
            Write-Host "  status:          STALE PID FILE (no process $daemonPid)" -ForegroundColor Yellow
        }
    } catch {
        Write-Warning "PID file unreadable: $_"
    }
} else {
    Write-Host "  status:          NOT RUNNING" -ForegroundColor Yellow
    Write-Host "  Start with .\tools\Start-Chatter.ps1"
}

Write-Host ""
Write-Host "Logs:"
foreach ($log in @($daemonLog, $chatterLog)) {
    if (Test-Path $log) {
        $size = [math]::Round(((Get-Item $log).Length / 1KB), 1)
        Write-Host "  $log  ($size KB)"
    } else {
        Write-Host "  $log  (none)"
    }
}

if (Test-Path $daemonLog) {
    Write-Host ""
    Write-Host "Recent daemon log entries:" -ForegroundColor Cyan
    Get-Content $daemonLog -Tail 8 | ForEach-Object { Write-Host "  $_" }
}

Write-Host ""
