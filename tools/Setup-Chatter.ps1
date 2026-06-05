#requires -Version 5.0
<#
.SYNOPSIS
    Set up (or verify) the DowagerMod Chatter sidecar on this machine.

.DESCRIPTION
    Bootstraps and validates the single source of truth for chatter
    credentials and tunables: <repo-root>\.env

    On a fresh machine:
      1. Copies .env.example -> .env (if .env missing).
      2. Opens .env in Notepad so you can paste credentials.
      3. Exits and tells you to re-run after editing.

    On a machine that already has .env:
      1. Validates the file via tools/chatter/env_check.py.
      2. Prints a redacted summary so you can confirm what the daemon
         will see.
      3. Warns if a pre-refactor %LOCALAPPDATA%\DowagerMod\chatter\
         config.json is still on disk (it is IGNORED but kept until
         you remove it with Uninstall-Chatter.ps1 -RemoveLegacyConfig).
      4. Optionally hardens the .env ACL to current user only.
      5. Optionally registers the Windows scheduled task that auto-starts
         the daemon at logon.

    Idempotent. Never edits .env (Notepad does); never prompts for keys.
    To change a setting: edit .env directly, then re-run this script (or
    just Stop-Chatter + Start-Chatter).

.PARAMETER Edit
    Open .env in Notepad and exit. Convenience shortcut.

.PARAMETER RegisterScheduledTask
    Register the 'DowagerMod-Chatter' logon task. Requires no
    elevation when the task runs under your own user.

.PARAMETER NoHardenAcl
    Skip the icacls hardening step. Useful when .env lives in OneDrive
    or any path where forcing inheritance off causes friction.

.EXAMPLE
    .\tools\Setup-Chatter.ps1
    # Validate .env (or bootstrap from .env.example on a fresh machine).

.EXAMPLE
    .\tools\Setup-Chatter.ps1 -RegisterScheduledTask
    # Validate then schedule the daemon to start at logon.

.EXAMPLE
    .\tools\Setup-Chatter.ps1 -Edit
    # Open .env in Notepad and exit.
#>

[CmdletBinding()]
param(
    [switch] $Edit,
    [switch] $RegisterScheduledTask,
    [switch] $NoHardenAcl
)

$ErrorActionPreference = 'Stop'

. (Join-Path $PSScriptRoot 'Chatter-Common.ps1')

$envPath = Get-ChatterEnvPath
$envExample = Get-ChatterEnvExamplePath
$repoRoot = Get-ChatterRepoRoot

Write-Host ""
Write-Host "DowagerMod Chatter setup" -ForegroundColor Cyan
Write-Host "========================="
Write-Host ""
Write-Host ".env path:   $envPath"
Write-Host ""

# ===== Step 1: bootstrap .env if missing =====

if (-not (Test-Path $envPath)) {
    Write-Host "No .env found." -ForegroundColor Yellow
    if (-not (Test-Path $envExample)) {
        Write-Error "Missing .env.example at $envExample. Cannot bootstrap. Pull the latest repo and retry."
        exit 1
    }
    Copy-Item -Path $envExample -Destination $envPath
    Write-Host "Created .env from .env.example." -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "  1. Paste your Azure Foundry / Speech / Discord credentials into .env"
    Write-Host "     (replace every 'paste-your-*-here' placeholder)."
    Write-Host "  2. Save and close Notepad."
    Write-Host "  3. Re-run .\tools\Setup-Chatter.ps1 to validate."
    Write-Host ""
    Write-Host "  Opening $envPath in Notepad..."
    Start-Process notepad.exe -ArgumentList $envPath
    exit 0
}

# ===== Step 2: -Edit shortcut =====

if ($Edit) {
    Write-Host "Opening $envPath in Notepad..." -ForegroundColor Cyan
    Start-Process notepad.exe -ArgumentList $envPath -Wait
    Write-Host "Re-running validation..." -ForegroundColor Cyan
    Write-Host ""
}

# ===== Step 3: preflight -- .env must be in .gitignore =====

$gitignore = Join-Path $repoRoot '.gitignore'
if (Test-Path $gitignore) {
    $gi = Get-Content -Path $gitignore -Raw
    if ($gi -notmatch '(?m)^\.env\s*$' -and $gi -notmatch '(?m)^/?\.env\s*$') {
        Write-Warning "WARNING: '.env' does NOT appear in .gitignore at $gitignore."
        Write-Warning "Your credentials are at risk of being committed. Add a line:"
        Write-Warning "    .env"
        Write-Warning "to .gitignore before pushing anything."
    }
} else {
    Write-Warning "No .gitignore at $gitignore. Confirm .env is excluded from your VCS."
}

# ===== Step 4: validate via env_check.py =====

Write-Host "Validating .env..." -ForegroundColor Cyan
$report = Invoke-ChatterEnvCheck
$exit = $script:LastEnvCheckExit

if ($null -eq $report) {
    Write-Error "env_check.py returned no parseable output (exit=$exit). Cannot continue."
    exit 1
}

if ($report.problems -and $report.problems.Count -gt 0) {
    Write-Host ""
    Write-Host "Problems found in $envPath :" -ForegroundColor Yellow
    foreach ($p in $report.problems) {
        Write-Host "  - $p" -ForegroundColor Yellow
    }
    Write-Host ""
    Write-Host "Fix: open .env (run .\tools\Setup-Chatter.ps1 -Edit) and replace" -ForegroundColor Yellow
    Write-Host "each missing or placeholder value, then re-run this script." -ForegroundColor Yellow
    Write-Host ""
    if (-not $RegisterScheduledTask) { exit 2 }
    Write-Warning "Skipping -RegisterScheduledTask because .env validation failed."
    exit 2
}

# ===== Step 5: show redacted summary =====

$r = $report.redacted
Write-Host ""
Write-Host ".env validated." -ForegroundColor Green
Write-Host "  endpoint:           $($r.endpoint)"
Write-Host "  deployment:         $($r.deployment)"
Write-Host "  api_key:            $($r.api_key)"
Write-Host "  log_level:          $($r.log_level)"
Write-Host ""
if ($r.voiceover_enabled) {
    if ($r.voiceover_ready) {
        Write-Host "Voiceover:           ENABLED (ready)" -ForegroundColor Green
    } else {
        Write-Host "Voiceover:           ENABLED but NOT READY (missing fields)" -ForegroundColor Yellow
    }
    Write-Host "  speech_endpoint:    $($r.speech_endpoint)"
    Write-Host "  speech_voice:       $($r.speech_voice)"
    Write-Host "  speech_key:         $($r.speech_key)"
    Write-Host "  discord_bot_token:  $($r.discord_bot_token)"
    Write-Host "  discord_guild_id:   $($r.discord_guild_id)"
    Write-Host "  discord_channel:    $($r.discord_voice_channel_id)"
    Write-Host "  native_tongue_mode: $($r.native_tongue_mode)"

    # FFmpeg presence check (only relevant when voiceover is on)
    $ffmpeg = Get-Command ffmpeg -ErrorAction SilentlyContinue
    if (-not $ffmpeg) {
        Write-Warning "FFmpeg not found on PATH. Voiceover will NOT play audio until you install it."
        Write-Warning "Install: winget install ffmpeg  (or https://ffmpeg.org/download.html)"
    } else {
        Write-Host "  ffmpeg:             $($ffmpeg.Source)" -ForegroundColor Green
    }
} else {
    Write-Host "Voiceover:           disabled"
}

# ===== Step 6: legacy config.json warning =====

if ($report.legacy_present) {
    Write-Host ""
    Write-Host "Legacy config detected:" -ForegroundColor Yellow
    Write-Host "  $($report.legacy_path)" -ForegroundColor Yellow
    Write-Host "This file is IGNORED -- .env is the only config source now."
    Write-Host "If it contains values you still want, copy them into .env first,"
    Write-Host "then run: .\tools\Uninstall-Chatter.ps1 -RemoveLegacyConfig"
}

# ===== Step 7: harden .env ACL =====

if (-not $NoHardenAcl) {
    try {
        $user = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
        & icacls.exe $envPath /inheritance:r /grant:r "${user}:F" 2>&1 | Out-Null
        Write-Host ""
        Write-Host "Hardened ACL on .env (owner only): $user" -ForegroundColor Green
    } catch {
        Write-Warning "Could not harden .env ACL: $_"
    }
}

# ===== Step 8: optional scheduled-task registration =====

if ($RegisterScheduledTask) {
    Write-Host ""
    Write-Host "Registering Windows scheduled task to auto-start at logon..." -ForegroundColor Cyan
    $taskName = "DowagerMod-Chatter"
    $startScript = Join-Path $PSScriptRoot 'Start-Chatter.ps1'
    $action = New-ScheduledTaskAction -Execute "powershell.exe" `
        -Argument "-NoProfile -WindowStyle Hidden -File `"$startScript`""
    $trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
    $settings = New-ScheduledTaskSettingsSet -StartWhenAvailable `
        -DontStopIfGoingOnBatteries -AllowStartIfOnBatteries
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger `
        -Settings $settings -Force | Out-Null
    Write-Host "Registered task '$taskName'." -ForegroundColor Green
}

Write-Host ""
Write-Host "Done." -ForegroundColor Cyan
Write-Host ""
Write-Host "To start the daemon now:        .\tools\Start-Chatter.ps1"
Write-Host "To change a setting later:      .\tools\Setup-Chatter.ps1 -Edit  (or edit .env directly)"
Write-Host "                                then Stop-Chatter / Start-Chatter to pick it up"
Write-Host "To see live status:             .\tools\Chatter-Status.ps1"
Write-Host ""
