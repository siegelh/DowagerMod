#requires -Version 5.0
<#
.SYNOPSIS
    Stop the DowagerMod Chatter sidecar daemon.

.EXAMPLE
    .\tools\Stop-Chatter.ps1
#>

[CmdletBinding()]
param([switch] $Force)

. (Join-Path $PSScriptRoot 'Chatter-Common.ps1')

$spoolDir = Get-ChatterSpoolDir
$pidFile = Get-ChatterPidFile

if (-not (Test-Path $pidFile)) {
    Write-Host "No PID file found at $pidFile. Daemon is not running (or never was)."
    exit 0
}

try {
    $pidJson = Get-Content -Path $pidFile -Raw | ConvertFrom-Json
    $daemonPid = [int]$pidJson.pid
} catch {
    Write-Warning "PID file is corrupt: $_"
    Remove-Item $pidFile -Force
    exit 0
}

try {
    $proc = Get-Process -Id $daemonPid -ErrorAction Stop
    Stop-Process -Id $daemonPid -Force:$Force
    Write-Host "Stopped daemon PID=$daemonPid"
} catch {
    Write-Host "Process $daemonPid is not running (PID file was stale)."
}

Remove-Item $pidFile -Force -ErrorAction SilentlyContinue
