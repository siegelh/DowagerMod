#requires -Version 5.0
<#
.SYNOPSIS
    Uninstall the DowagerMod Chatter sidecar from this machine.

.DESCRIPTION
    Cleanly removes the sidecar's runtime presence from this machine:
      1. Stops any running daemon (calls Stop-Chatter.ps1).
      2. Removes the Windows scheduled task 'DowagerMod-Chatter' if present.
      3. Optionally deletes <repo-root>\.env (current source of truth).
      4. Optionally deletes the legacy %LOCALAPPDATA%\DowagerMod\chatter\
         config.json (pre-refactor file; NOT read by the daemon anymore
         but kept around so Setup-Chatter can warn about it).

    By default both .env and the legacy config.json are preserved so you
    can reinstall later without re-entering credentials. Pass -RemoveEnv
    to wipe .env, -RemoveLegacyConfig to wipe the legacy file, or both.

    Idempotent: safe to run when nothing is installed. Each step prints
    what it did (or that it had nothing to do).

    NOTE: This does NOT remove the in-game hooks. Those ship with the mod
    and are silent when no sidecar is running. If you want to remove the
    chatter feature entirely from your game install, simply uninstall the
    DowagerMod itself.

.PARAMETER RemoveEnv
    Also delete <repo-root>\.env (your credentials). Default: keep.

.PARAMETER RemoveConfig
    Deprecated alias for -RemoveEnv (kept so old runbooks still work).

.PARAMETER RemoveLegacyConfig
    Also delete %LOCALAPPDATA%\DowagerMod\chatter\config.json. This file
    is from before the .env refactor and is no longer read by the daemon.

.PARAMETER Force
    Skip confirmation prompts. Useful for scripted runs.

.EXAMPLE
    .\tools\Uninstall-Chatter.ps1
    # Stops daemon, removes scheduled task, keeps .env.

.EXAMPLE
    .\tools\Uninstall-Chatter.ps1 -RemoveEnv -RemoveLegacyConfig -Force
    # Full nuke: daemon stopped, task removed, .env and legacy config.json deleted.
#>

[CmdletBinding()]
param(
    [switch] $RemoveEnv,
    [switch] $RemoveConfig,   # deprecated alias for -RemoveEnv
    [switch] $RemoveLegacyConfig,
    [switch] $Force
)

$ErrorActionPreference = 'Stop'

. (Join-Path $PSScriptRoot 'Chatter-Common.ps1')

# Resolve deprecated alias.
if ($RemoveConfig -and -not $RemoveEnv) {
    Write-Warning "-RemoveConfig is deprecated; treating as -RemoveEnv."
    $RemoveEnv = $true
}

Write-Host ""
Write-Host "DowagerMod Chatter uninstall" -ForegroundColor Cyan
Write-Host "============================="
Write-Host ""

$summary = @()

# ===== Step 1: stop the daemon =====

$stopScript = Join-Path $PSScriptRoot 'Stop-Chatter.ps1'
if (Test-Path $stopScript) {
    Write-Host "[1/4] Stopping sidecar daemon..." -ForegroundColor Cyan
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

# ===== Step 2: remove scheduled task =====

Write-Host ""
Write-Host "[2/4] Checking scheduled task 'DowagerMod-Chatter'..." -ForegroundColor Cyan
$taskName = "DowagerMod-Chatter"
$task = $null
try { $task = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue }
catch { $task = $null }
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

# ===== Step 3: optionally delete .env =====

Write-Host ""
$envPath = Get-ChatterEnvPath
if ($RemoveEnv) {
    Write-Host "[3/4] Removing .env (credentials)..." -ForegroundColor Cyan
    if (Test-Path $envPath) {
        $proceed = $true
        if (-not $Force) {
            Write-Host ""
            Write-Host "About to delete: $envPath" -ForegroundColor Yellow
            Write-Host "This will remove your API keys and Discord tokens. Type 'yes' to confirm: " -NoNewline -ForegroundColor Yellow
            $answer = Read-Host
            if ($answer -ne 'yes') {
                $proceed = $false
                Write-Host "  Skipped (you did not confirm)."
                $summary += "  - .env: kept (delete not confirmed)"
            }
        }
        if ($proceed) {
            try {
                Remove-Item -Path $envPath -Force
                Write-Host "  Deleted: $envPath"
                $summary += "  - .env: deleted"
            } catch {
                Write-Warning "Failed to delete .env: $_"
                $summary += "  - .env: DELETE FAILED ($_)"
            }
        }
    } else {
        Write-Host "  No .env at $envPath. Nothing to remove."
        $summary += "  - .env: not present"
    }
} else {
    Write-Host "[3/4] Keeping .env." -ForegroundColor Cyan
    if (Test-Path $envPath) {
        Write-Host "  $envPath preserved (use -RemoveEnv to delete)."
        $summary += "  - .env: kept (use -RemoveEnv to delete)"
    } else {
        Write-Host "  No .env to keep. Nothing was there."
        $summary += "  - .env: not present"
    }
}

# ===== Step 4: optionally delete legacy config.json =====

Write-Host ""
$legacyPath = Get-ChatterLegacyConfigPath
$legacyDir = Split-Path -Parent $legacyPath
if ($RemoveLegacyConfig) {
    Write-Host "[4/4] Removing legacy chatter config.json..." -ForegroundColor Cyan
    if (Test-Path $legacyPath) {
        try {
            Remove-Item -Path $legacyPath -Force
            Write-Host "  Deleted: $legacyPath"
            $summary += "  - Legacy config.json: deleted"
            # If the chatter dir is now empty (no spool, no other state),
            # try to nuke it too -- keeps %LOCALAPPDATA% tidy.
            try {
                if ((Get-ChildItem -Path $legacyDir -Force -ErrorAction Stop).Count -eq 0) {
                    Remove-Item -Path $legacyDir -Force
                    Write-Host "  Removed empty dir: $legacyDir"
                }
            } catch {
                # Dir not empty (spool/logs live), or doesn't exist -- both fine.
            }
        } catch {
            Write-Warning "Failed to delete legacy config.json: $_"
            $summary += "  - Legacy config.json: DELETE FAILED ($_)"
        }
    } else {
        Write-Host "  No legacy config.json at $legacyPath. Nothing to remove."
        $summary += "  - Legacy config.json: not present"
    }
} else {
    Write-Host "[4/4] Keeping legacy config.json if present." -ForegroundColor Cyan
    if (Test-Path $legacyPath) {
        Write-Host "  $legacyPath preserved (IGNORED by daemon; use -RemoveLegacyConfig to delete)."
        $summary += "  - Legacy config.json: kept (use -RemoveLegacyConfig to delete)"
    } else {
        $summary += "  - Legacy config.json: not present"
    }
}

Write-Host ""
Write-Host "Summary" -ForegroundColor Cyan
Write-Host "-------"
foreach ($line in $summary) { Write-Host $line }
Write-Host ""
Write-Host "Done." -ForegroundColor Green
Write-Host ""
Write-Host "To reinstall later: .\tools\Setup-Chatter.ps1" -ForegroundColor Cyan

