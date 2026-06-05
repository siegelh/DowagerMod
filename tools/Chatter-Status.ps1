#requires -Version 5.0
<#
.SYNOPSIS
    Show DowagerMod Chatter sidecar status.

.EXAMPLE
    .\tools\Chatter-Status.ps1
#>

$ErrorActionPreference = 'Continue'

. (Join-Path $PSScriptRoot 'Chatter-Common.ps1')

$envPath = Get-ChatterEnvPath
$spoolDir = Get-ChatterSpoolDir
$pidFile = Get-ChatterPidFile
$daemonLog = Get-ChatterDaemonLog
$chatterLog = Get-ChatterGameLog

Write-Host ""
Write-Host "DowagerMod Chatter status" -ForegroundColor Cyan
Write-Host "========================="
Write-Host ""

# ===== Config (.env via env_check.py) =====

Write-Host "Config (.env):"
$report = Invoke-ChatterEnvCheck
if ($null -eq $report) {
    Write-Host "  status:          UNKNOWN (env_check.py output unparseable)" -ForegroundColor Yellow
} elseif (-not $report.env_present) {
    Write-Host "  status:          .env MISSING" -ForegroundColor Red
    Write-Host "  expected at:    $envPath"
    Write-Host "  Bootstrap with: .\tools\Setup-Chatter.ps1"
} elseif ($report.problems -and $report.problems.Count -gt 0) {
    Write-Host "  .env path:       $($report.env_path)" -ForegroundColor Yellow
    Write-Host "  status:          INVALID" -ForegroundColor Yellow
    foreach ($p in $report.problems) { Write-Host "    - $p" -ForegroundColor Yellow }
    Write-Host "  Fix with: .\tools\Setup-Chatter.ps1 -Edit"
} else {
    $r = $report.redacted
    Write-Host "  .env path:       $($report.env_path)" -ForegroundColor Green
    Write-Host "  endpoint:        $($r.endpoint)"
    Write-Host "  deployment:      $($r.deployment)"
    Write-Host "  api_key:         $($r.api_key)"
    Write-Host "  log_level:       $($r.log_level)"
    if ($r.voiceover_enabled) {
        $voState = if ($r.voiceover_ready) { 'ENABLED (ready)' } else { 'ENABLED (not ready)' }
        $voColor = if ($r.voiceover_ready) { 'Green' } else { 'Yellow' }
        Write-Host "  voiceover:       $voState" -ForegroundColor $voColor
        Write-Host "    speech:        $($r.speech_endpoint)  voice=$($r.speech_voice)"
        Write-Host "    discord:       guild=$($r.discord_guild_id) channel=$($r.discord_voice_channel_id)"
    } else {
        Write-Host "  voiceover:       disabled"
    }
}

if ($report -and $report.legacy_present) {
    Write-Host ""
    Write-Host "Legacy config detected (IGNORED):" -ForegroundColor Yellow
    Write-Host "  $($report.legacy_path)"
    Write-Host "  Remove with: .\tools\Uninstall-Chatter.ps1 -RemoveLegacyConfig"
}

# ===== Spool =====

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

# ===== Daemon =====

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

# ===== Logs =====

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

