<#
.SYNOPSIS
    Test a registered TTS voice end-to-end.
.DESCRIPTION
    Validates that a voice can synthesize audio via the local TTS server.
    Supports single-shot testing and an interactive REPL for free-form audition.

.PARAMETER VoiceId
    Voice to test (default: all registered voices).
.PARAMETER Text
    Custom test line. If omitted, uses a default phrase.
.PARAMETER Interactive
    Enter interactive mode: type any text, hear it, repeat until blank line.
.PARAMETER NoPlay
    Skip audio playback (just validate synthesis succeeds).
.PARAMETER ServerUrl
    TTS server URL (default: http://localhost:8080).
#>
param(
    [string]$VoiceId,
    [string]$Text,
    [switch]$Interactive,
    [switch]$NoPlay,
    [string]$ServerUrl = "http://localhost:8080"
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$serverDir = Join-Path $repoRoot "tools\tts-server"
$registryFile = Join-Path $serverDir "voice_registry.json"

Write-Host ""
Write-Host "=== TTS Voice Test ===" -ForegroundColor Cyan

# ----- Health check -----
Write-Host ""
Write-Host "[1/3] Checking server health..." -NoNewline
try {
    $health = Invoke-RestMethod -Uri "$ServerUrl/health" -TimeoutSec 5
    Write-Host " OK (model=$($health.model))" -ForegroundColor Green
} catch {
    Write-Host " FAILED" -ForegroundColor Red
    Write-Host ""
    Write-Host "Server not reachable at $ServerUrl" -ForegroundColor Red
    Write-Host "Start it with: .\tools\Start-TtsServer.ps1" -ForegroundColor Yellow
    exit 1
}

# ----- Determine voices to test -----
$registry = Get-Content $registryFile -Raw | ConvertFrom-Json
$allVoices = @()
$registry.voices | Get-Member -MemberType NoteProperty | ForEach-Object { $allVoices += $_.Name }

if ($VoiceId) {
    if ($VoiceId -notin $allVoices) {
        Write-Host ""
        Write-Host "Voice '$VoiceId' not found in registry. Available: $($allVoices -join ', ')" -ForegroundColor Red
        exit 1
    }
    $testVoices = @($VoiceId)
} else {
    $testVoices = $allVoices
}

# ----- Interactive mode -----
if ($Interactive) {
    $targetVoice = if ($VoiceId) { $VoiceId } else { $allVoices[0] }
    $displayName = $registry.voices.$targetVoice.display_name
    Write-Host ""
    Write-Host "Interactive audition for '$targetVoice' ($displayName)" -ForegroundColor Cyan
    Write-Host "Type text to hear it. Blank line to quit." -ForegroundColor DarkGray
    Write-Host ""

    while ($true) {
        $input = Read-Host ">"
        if (-not $input -or $input.Trim() -eq "") { break }

        try {
            $body = @{ text = $input; voice_id = $targetVoice } | ConvertTo-Json
            $t0 = Get-Date
            $response = Invoke-WebRequest -Uri "$ServerUrl/synthesize" `
                -Method POST -ContentType "application/json" -Body $body `
                -TimeoutSec 60
            $elapsed = ((Get-Date) - $t0).TotalSeconds
            $sizeKb = [math]::Round($response.Content.Length / 1024, 1)

            $tempWav = Join-Path $env:TEMP "tts_test_${targetVoice}.wav"
            [System.IO.File]::WriteAllBytes($tempWav, $response.Content)

            if (-not $NoPlay) {
                Write-Host "  Playing... ($([math]::Round($elapsed, 1))s, ${sizeKb}KB)" -ForegroundColor DarkGray
                $player = New-Object System.Media.SoundPlayer $tempWav
                $player.PlaySync()
            } else {
                Write-Host "  OK ($([math]::Round($elapsed, 1))s, ${sizeKb}KB)" -ForegroundColor Green
            }
        } catch {
            Write-Host "  Error: $_" -ForegroundColor Red
        }
    }
    Write-Host ""
    Write-Host "Done." -ForegroundColor Green
    exit 0
}

# ----- Single-shot test per voice -----
$defaultTexts = @{
    dowager = "One does wonder what they teach in schools these days. The standards have clearly declined."
}
$genericText = "This is a test of the voice synthesis system. The quick brown fox jumps over the lazy dog."

foreach ($voice in $testVoices) {
    $testText = if ($Text) { $Text } elseif ($defaultTexts[$voice]) { $defaultTexts[$voice] } else { $genericText }
    $displayName = $registry.voices.$voice.display_name

    Write-Host ""
    Write-Host "[2/3] Synthesizing '$voice' ($displayName)..." -NoNewline

    try {
        $body = @{ text = $testText; voice_id = $voice } | ConvertTo-Json
        $t0 = Get-Date
        $response = Invoke-WebRequest -Uri "$ServerUrl/synthesize" `
            -Method POST -ContentType "application/json" -Body $body `
            -TimeoutSec 60
        $elapsed = ((Get-Date) - $t0).TotalSeconds
        $sizeKb = [math]::Round($response.Content.Length / 1024, 1)

        Write-Host " OK ($([math]::Round($elapsed, 1))s, ${sizeKb}KB)" -ForegroundColor Green

        $outWav = Join-Path $serverDir "test_${voice}.wav"
        [System.IO.File]::WriteAllBytes($outWav, $response.Content)

        if (-not $NoPlay) {
            Write-Host "[3/3] Playing audio..." -NoNewline
            $player = New-Object System.Media.SoundPlayer $outWav
            $player.PlaySync()
            Write-Host " done" -ForegroundColor Green
        }

        Write-Host ""
        Write-Host "Voice '$voice' is working! Output: $outWav" -ForegroundColor Green
    } catch {
        Write-Host " FAILED" -ForegroundColor Red
        Write-Host "  Error: $_" -ForegroundColor Red
    }
}

Write-Host ""
