#requires -Version 5.0
<#
.SYNOPSIS
    Uninstall the DowagerMod Chatter sidecar from this machine.

.DESCRIPTION
    Cleanly removes the sidecar's runtime presence from this machine:
      1. Stops any running daemon (calls Stop-Chatter.ps1).
      2. Removes the Windows scheduled task 'DowagerMod-Chatter' if present.
      3. Optionally deletes %LOCALAPPDATA%\DowagerMod\chatter\ (config + key).

    By default the config (including your API key) is preserved so you can
    reinstall later without re-entering the key. Pass -RemoveConfig to wipe
    it.

    Idempotent: safe to run when nothing is installed. Each step prints
    what it did (or that it had nothing to do).

    NOTE: This does NOT remove the in-game hooks. Those ship with the mod
    and are silent when no sidecar is running. If you want to remove the
    chatter feature entirely from your game install, simply uninstall the
    DowagerMod itself.

.PARAMETER RemoveConfig
    Also delete %LOCALAPPDATA%\DowagerMod\chatter\ (config + API key).
    Default: keep config.

.PARAMETER Force
    Skip confirmation prompts. Useful for scripted runs.

.EXAMPLE
    .\tools\Uninstall-Chatter.ps1
    # Stops daemon, removes scheduled task, keeps config.

.EXAMPLE
    .\tools\Uninstall-Chatter.ps1 -RemoveConfig -Force
    # Stops daemon, removes scheduled task, deletes config without prompting.
#>

[CmdletBinding()]
param(
    [switch] $RemoveConfig,
    [switch] $Force
)

$ErrorActionPreference = 'Stop'

Write-Host ""
Write-Host "DowagerMod Chatter uninstall" -ForegroundColor Cyan
Write-Host "============================="
Write-Host ""

$summary = @()

# 1. Stop the daemon (Stop-Chatter.ps1 is idempotent).
$stopScript = Join-Path $PSScriptRoot 'Stop-Chatter.ps1'
if (Test-Path $stopScript) {
    Write-Host "[1/3] Stopping sidecar daemon..." -ForegroundColor Cyan
    try {
        & $stopScript | Out-Host
        $summary += "  - Daemon: stopped (or was not running)"
    } catch {
        Write-Warning "Stop-Chatter.ps1 failed: $_"
        $summary += "  - Daemon: stop FAILED ($_)"
    }
} else {
    Write-Warning "Stop-Chatter.ps1 not found at $stopScript; skipping daemon stop."
    $summary += "  - Daemon: skipped (Stop-Chatter.ps1 missing)"
}

# 2. Remove scheduled task.
Write-Host ""
Write-Host "[2/3] Checking scheduled task 'DowagerMod-Chatter'..." -ForegroundColor Cyan
$taskName = "DowagerMod-Chatter"
$task = $null
try {
    $task = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
} catch {
    $task = $null
}
if ($task) {
    try {
        Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
        Write-Host "  Removed scheduled task '$taskName'."
        $summary += "  - Scheduled task: removed"
    } catch {
        Write-Warning "Failed to remove scheduled task: $_"
        $summary += "  - Scheduled task: REMOVE FAILED ($_)"
    }
} else {
    Write-Host "  No scheduled task named '$taskName' was registered. Nothing to remove."
    $summary += "  - Scheduled task: not present"
}

# 3. Optionally delete config dir.
Write-Host ""
$configDir = Join-Path $env:LOCALAPPDATA 'DowagerMod\chatter'
$configPath = Join-Path $configDir 'config.json'
if ($RemoveConfig) {
    Write-Host "[3/3] Removing config directory..." -ForegroundColor Cyan
    if (Test-Path $configDir) {
        $proceed = $true
        if (-not $Force) {
            Write-Host ""
            Write-Host "About to delete: $configDir" -ForegroundColor Yellow
            Write-Host "This will remove your stored API key. Type 'yes' to confirm: " -NoNewline -ForegroundColor Yellow
            $answer = Read-Host
            if ($answer -ne 'yes') {
                $proceed = $false
                Write-Host "  Skipped (you did not confirm)."
                $summary += "  - Config: kept (delete not confirmed)"
            }
        }
        if ($proceed) {
            try {
                Remove-Item -Path $configDir -Recurse -Force
                Write-Host "  Deleted: $configDir"
                $summary += "  - Config: deleted"
            } catch {
                Write-Warning "Failed to delete config dir: $_"
                $summary += "  - Config: DELETE FAILED ($_)"
            }
        }
    } else {
        Write-Host "  Config directory does not exist. Nothing to remove."
        $summary += "  - Config: not present"
    }
} else {
    Write-Host "[3/3] Keeping config directory." -ForegroundColor Cyan
    if (Test-Path $configPath) {
        Write-Host "  $configPath preserved (use -RemoveConfig to delete)."
        $summary += "  - Config: kept (use -RemoveConfig to delete)"
    } else {
        Write-Host "  No config to keep. Nothing was there."
        $summary += "  - Config: not present"
    }
}

Write-Host ""
Write-Host "Summary" -ForegroundColor Cyan
Write-Host "-------"
foreach ($line in $summary) {
    Write-Host $line
}
Write-Host ""
Write-Host "Done." -ForegroundColor Green
Write-Host ""
Write-Host "To reinstall later: .\tools\Setup-Chatter.ps1" -ForegroundColor Cyan
