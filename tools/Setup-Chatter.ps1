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
    [string] $Endpoint = "https://discordagent.cognitiveservices.azure.com/",
    [string] $Deployment = "gpt-5.4-mini",
    [string] $ApiKey,
    [string] $ApiVersion = "2024-12-01-preview",
    [switch] $RegisterScheduledTask,
    [switch] $NoPrompt,
    [switch] $ConfigureVoiceover,
    [string] $SpeechEndpoint,
    [string] $SpeechKey,
    [string] $SpeechVoice = "en-US-AriaNeural",
    [string] $DiscordBotToken,
    [string] $DiscordGuildId,
    [string] $DiscordVoiceChannelId
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

# ===== Voiceover (Azure Speech + Discord bot) — optional =====

$voiceoverEnabled = $false
$existingVoiceover = ($existing.ContainsKey('voiceover_enabled') -and $existing['voiceover_enabled'])

if (-not $NoPrompt) {
    if ($ConfigureVoiceover) {
        $configureVo = $true
    } elseif ($existingVoiceover) {
        $reply = Read-Host "Voiceover is currently enabled. Reconfigure? (y/N)"
        $configureVo = ($reply -eq 'y' -or $reply -eq 'Y')
    } else {
        $reply = Read-Host "Configure voiceover (Discord bot + Azure Speech)? (y/N)"
        $configureVo = ($reply -eq 'y' -or $reply -eq 'Y')
    }

    if ($configureVo) {
        Write-Host ""
        Write-Host "Voiceover setup" -ForegroundColor Cyan
        Write-Host "---------------"
        Write-Host "Press Enter at any prompt to keep the existing value (or to skip and disable)."
        Write-Host ""

        # Azure Speech
        if (-not $SpeechEndpoint) {
            $existingSpeechEp = if ($existing.ContainsKey('azure_speech_endpoint')) { $existing.azure_speech_endpoint } else { '' }
            $hint = if ($existingSpeechEp) { "[$existingSpeechEp]" } else { 'e.g. https://<region>.api.cognitive.microsoft.com/' }
            $reply = Read-Host "Azure Speech endpoint $hint"
            if ($reply) { $SpeechEndpoint = $reply } elseif ($existingSpeechEp) { $SpeechEndpoint = $existingSpeechEp }
        }
        if (-not $SpeechKey) {
            $existingSpeechKey = if ($existing.ContainsKey('azure_speech_key')) { $existing.azure_speech_key } else { '' }
            $hasExistingSpeechKey = [bool]$existingSpeechKey
            $prompt = if ($hasExistingSpeechKey) { "Azure Speech key (input hidden, Enter to keep existing)" } else { "Azure Speech key (input hidden)" }
            $secure = Read-Host $prompt -AsSecureString
            $bstr = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
            try { $entered = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($bstr) }
            finally { [System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr) }
            if ($entered) { $SpeechKey = $entered } elseif ($hasExistingSpeechKey) { $SpeechKey = $existingSpeechKey; $script:SpeechKeyUnchanged = $true }
        }
        if (-not $SpeechVoice -or $SpeechVoice -eq "en-US-AriaNeural") {
            $existingVoice = if ($existing.ContainsKey('azure_speech_voice')) { $existing.azure_speech_voice } else { 'en-US-AriaNeural' }
            $reply = Read-Host "Speech voice [$existingVoice]"
            if ($reply) { $SpeechVoice = $reply } else { $SpeechVoice = $existingVoice }
        }

        # Discord
        if (-not $DiscordBotToken) {
            $existingBotToken = if ($existing.ContainsKey('discord_bot_token')) { $existing.discord_bot_token } else { '' }
            $hasExistingBotToken = [bool]$existingBotToken
            $prompt = if ($hasExistingBotToken) { "Discord bot token (input hidden, Enter to keep existing)" } else { "Discord bot token (input hidden)" }
            $secure = Read-Host $prompt -AsSecureString
            $bstr = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
            try { $entered = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($bstr) }
            finally { [System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr) }
            if ($entered) { $DiscordBotToken = $entered } elseif ($hasExistingBotToken) { $DiscordBotToken = $existingBotToken; $script:BotTokenUnchanged = $true }
        }
        if (-not $DiscordGuildId) {
            $existingGuild = if ($existing.ContainsKey('discord_guild_id')) { $existing.discord_guild_id } else { '' }
            $hint = if ($existingGuild) { "[$existingGuild]" } else { '(numeric ID from Discord server settings)' }
            $reply = Read-Host "Discord server (guild) ID $hint"
            if ($reply) { $DiscordGuildId = $reply } elseif ($existingGuild) { $DiscordGuildId = $existingGuild }
        }
        if (-not $DiscordVoiceChannelId) {
            $existingChan = if ($existing.ContainsKey('discord_voice_channel_id')) { $existing.discord_voice_channel_id } else { '' }
            $hint = if ($existingChan) { "[$existingChan]" } else { '(numeric ID, right-click voice channel -> Copy Channel ID)' }
            $reply = Read-Host "Discord voice channel ID $hint"
            if ($reply) { $DiscordVoiceChannelId = $reply } elseif ($existingChan) { $DiscordVoiceChannelId = $existingChan }
        }

        # All fields populated => enable voiceover
        $allPopulated = ($SpeechEndpoint -and $SpeechKey -and $DiscordBotToken -and $DiscordGuildId -and $DiscordVoiceChannelId)
        if ($allPopulated) {
            $voiceoverEnabled = $true
            # Validate FFmpeg presence (required by discord.py for audio playback)
            $ffmpeg = Get-Command ffmpeg -ErrorAction SilentlyContinue
            if (-not $ffmpeg) {
                Write-Warning "FFmpeg not found on PATH. Voiceover will NOT play audio until you install it."
                Write-Warning "Install: https://ffmpeg.org/download.html (or ``winget install ffmpeg`` / ``choco install ffmpeg``)"
            } else {
                Write-Host "FFmpeg found: $($ffmpeg.Source)" -ForegroundColor Green
            }
        } else {
            Write-Warning "Not all voiceover fields populated; voiceover will stay DISABLED."
            $voiceoverEnabled = $false
        }
    } elseif ($existingVoiceover) {
        # User declined to reconfigure; preserve existing voiceover state
        $voiceoverEnabled = $true
        if ($existing.ContainsKey('azure_speech_endpoint')) { $SpeechEndpoint = $existing.azure_speech_endpoint }
        if ($existing.ContainsKey('azure_speech_key')) { $SpeechKey = $existing.azure_speech_key; $script:SpeechKeyUnchanged = $true }
        if ($existing.ContainsKey('azure_speech_voice')) { $SpeechVoice = $existing.azure_speech_voice }
        if ($existing.ContainsKey('discord_bot_token')) { $DiscordBotToken = $existing.discord_bot_token; $script:BotTokenUnchanged = $true }
        if ($existing.ContainsKey('discord_guild_id')) { $DiscordGuildId = $existing.discord_guild_id }
        if ($existing.ContainsKey('discord_voice_channel_id')) { $DiscordVoiceChannelId = $existing.discord_voice_channel_id }
    }
}

# Build config (preserving any non-required fields the user has customized)
$config = [ordered]@{
    "_comment" = "DowagerMod Chatter sidecar config. NEVER COMMIT THIS FILE. NEVER SHARE THIS KEY."
    endpoint = $Endpoint
    deployment = $Deployment
    api_key = $ApiKey
    api_version = $ApiVersion
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
    voiceover_enabled = [bool]$voiceoverEnabled
    azure_speech_endpoint = if ($SpeechEndpoint) { $SpeechEndpoint } else { "" }
    azure_speech_key = if ($SpeechKey) { $SpeechKey } else { "" }
    azure_speech_voice = if ($SpeechVoice) { $SpeechVoice } else { "en-US-AriaNeural" }
    speech_rate = "+50%"
    voiceover_daily_char_cap = 100000
    discord_bot_token = if ($DiscordBotToken) { $DiscordBotToken } else { "" }
    discord_guild_id = if ($DiscordGuildId) { $DiscordGuildId } else { "" }
    discord_voice_channel_id = if ($DiscordVoiceChannelId) { $DiscordVoiceChannelId } else { "" }
}

# Preserve user customizations from existing config (override defaults but not the ones we just set)
foreach ($key in @('max_tokens','max_tokens_multi_turn','request_timeout_seconds','rate_limit_seconds',
                   'max_in_flight','spool_poll_interval_seconds','request_ttl_seconds',
                   'response_ttl_seconds','log_level','enabled','voiceover_daily_char_cap',
                   'speech_rate')) {
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
if ($voiceoverEnabled) {
    Write-Host "Voiceover:   ENABLED" -ForegroundColor Green
    Write-Host "  Speech endpoint:  $SpeechEndpoint"
    Write-Host "  Speech voice:     $SpeechVoice"
    if ($script:SpeechKeyUnchanged) { Write-Host "  Speech key:       (unchanged)" }
    else { $sk = if ($SpeechKey.Length -gt 8) { $SpeechKey.Substring(0,4) + "..." + $SpeechKey.Substring($SpeechKey.Length - 4) } else { "***" }; Write-Host "  Speech key:       $sk" }
    if ($script:BotTokenUnchanged) { Write-Host "  Discord bot tok:  (unchanged)" }
    else { $bt = if ($DiscordBotToken.Length -gt 8) { $DiscordBotToken.Substring(0,4) + "..." + $DiscordBotToken.Substring($DiscordBotToken.Length - 4) } else { "***" }; Write-Host "  Discord bot tok:  $bt" }
    Write-Host "  Discord guild:    $DiscordGuildId"
    Write-Host "  Discord channel:  $DiscordVoiceChannelId"
} else {
    Write-Host "Voiceover:   disabled"
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
