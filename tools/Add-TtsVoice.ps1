<#
.SYNOPSIS
    Add a new voice to the local TTS server.
.DESCRIPTION
    Interactive wizard that guides you through adding a new voice for
    zero-shot cloning. Handles reference audio, voice registry, leader
    wiring, and interactive audition.

    After running this, commit + push and every machine with git pull
    will have the new voice immediately (no training needed).

.PARAMETER VoiceId
    Voice identifier (lowercase, no spaces). Used in voice_registry.json
    and config. E.g., "stalin", "gandhi", "tokugawa".
.PARAMETER DisplayName
    Human-readable name. E.g., "Joseph Stalin", "Tokugawa Ieyasu".
.PARAMETER RefWav
    Path to an existing reference WAV file (6-12 seconds optimal).
    If omitted, the wizard will ask interactively.
.PARAMETER Transcript
    Verbatim transcript of what is said in the reference WAV.
    Required for future model compatibility. If omitted, wizard asks.
.PARAMETER ServerUrl
    URL of a running TTS server for audition (default: http://localhost:8080).
.PARAMETER NoAudition
    Skip the interactive audition step.
#>
param(
    [string]$VoiceId,
    [string]$DisplayName,
    [string]$RefWav,
    [string]$Transcript,
    [string]$ServerUrl = "http://localhost:8080",
    [switch]$NoAudition
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$serverDir = Join-Path $repoRoot "tools\tts-server"
$voicesDir = Join-Path $serverDir "voices"
$registryFile = Join-Path $serverDir "voice_registry.json"
$leaderVoicesFile = Join-Path $repoRoot "tools\chatter\leader_voices.json"
$venvPython = Join-Path $serverDir ".venv\Scripts\python.exe"

Write-Host ""
Write-Host "=== Add TTS Voice ===" -ForegroundColor Cyan
Write-Host "This wizard sets up a new voice for zero-shot cloning." -ForegroundColor DarkGray
Write-Host ""

# ----- Gather inputs -----

if (-not $VoiceId) {
    $VoiceId = Read-Host "Voice ID (lowercase, no spaces, e.g. 'stalin', 'tokugawa')"
}
$VoiceId = $VoiceId.Trim().ToLower() -replace '[^a-z0-9_]', ''
if (-not $VoiceId) {
    Write-Error "Voice ID cannot be empty."
    exit 1
}
Write-Host "  Voice ID: $VoiceId" -ForegroundColor White

if (-not $DisplayName) {
    $DisplayName = Read-Host "Display name (e.g. 'Tokugawa Ieyasu')"
}
if (-not $DisplayName) { $DisplayName = $VoiceId }
Write-Host "  Display name: $DisplayName" -ForegroundColor White

# Reference WAV
$targetWav = Join-Path $voicesDir "${VoiceId}_ref.wav"

if (-not $RefWav) {
    Write-Host ""
    Write-Host "Reference audio source:" -ForegroundColor Yellow
    Write-Host "  [1] Use an existing WAV file (provide path)"
    Write-Host "  [2] Generate via ElevenLabs (uses Generate-TtsReference.ps1)"
    $choice = Read-Host "Choice [1/2]"

    if ($choice -eq "2") {
        Write-Host "Running Generate-TtsReference.ps1..." -ForegroundColor Cyan
        & (Join-Path $repoRoot "tools\Generate-TtsReference.ps1")
        Write-Host ""
        $RefWav = Read-Host "Path to the generated WAV file"
    } else {
        $RefWav = Read-Host "Path to reference WAV (6-12 seconds, clean audio)"
    }
}

if (-not (Test-Path $RefWav)) {
    Write-Error "File not found: $RefWav"
    exit 1
}

# Check duration
$wavSize = (Get-Item $RefWav).Length
$estDuration = [math]::Round(($wavSize - 44) / (24000 * 2), 1)
Write-Host "  Reference audio: $RefWav (~${estDuration}s)" -ForegroundColor White

# Transcript (mandatory for future model compatibility)
if (-not $Transcript) {
    Write-Host ""
    Write-Host "What is said in the reference audio? (verbatim transcript)" -ForegroundColor Yellow
    Write-Host "This is stored for future models that require it." -ForegroundColor DarkGray
    $Transcript = Read-Host "Transcript"
}
if (-not $Transcript) {
    Write-Error "Transcript is required. It ensures future model compatibility."
    exit 1
}

# ----- Copy/resample reference WAV -----
Write-Host ""
Write-Host "Copying reference audio..." -ForegroundColor Yellow

if (Test-Path $venvPython) {
    # Use Python to resample to 24kHz mono 16-bit if needed
    & $venvPython -c @"
import wave, struct, sys
from pathlib import Path

src = r'$($RefWav -replace "'", "''")'
dst = r'$($targetWav -replace "'", "''")'

# Try to read and normalize
try:
    import numpy as np
    try:
        import soundfile as sf
        data, sr = sf.read(src, dtype='int16')
    except ImportError:
        # Fallback: just copy the file
        import shutil
        shutil.copy2(src, dst)
        print(f'Copied (no soundfile for resampling): {dst}')
        sys.exit(0)

    # If stereo, take left channel
    if len(data.shape) > 1:
        data = data[:, 0]

    # Resample to 24000 if needed
    if sr != 24000:
        try:
            import torchaudio
            import torch
            t = torch.from_numpy(data.astype('float32')).unsqueeze(0) / 32768.0
            t = torchaudio.functional.resample(t, sr, 24000)
            data = (t.squeeze().numpy() * 32768).astype('int16')
            sr = 24000
        except ImportError:
            print(f'WARNING: Sample rate is {sr}Hz, not 24kHz. Install torchaudio to auto-resample.')

    # Write as 24kHz mono 16-bit WAV
    with wave.open(dst, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(data.tobytes())
    print(f'Saved: {dst} ({len(data)/sr:.1f}s, {sr}Hz mono)')
except Exception as e:
    import shutil
    shutil.copy2(src, dst)
    print(f'Copied (fallback): {dst}')
"@
} else {
    Copy-Item $RefWav $targetWav -Force
    Write-Host "  Copied: $targetWav (venv not available for resampling)" -ForegroundColor DarkGray
}

if (-not (Test-Path $targetWav)) {
    Write-Error "Failed to create reference WAV at $targetWav"
    exit 1
}
Write-Host "  [OK] $targetWav" -ForegroundColor Green

# ----- Update voice_registry.json -----
Write-Host ""
Write-Host "Updating voice_registry.json..." -ForegroundColor Yellow

$registry = Get-Content $registryFile -Raw | ConvertFrom-Json
if (-not $registry.voices) {
    $registry | Add-Member -NotePropertyName "voices" -NotePropertyValue ([PSCustomObject]@{})
}

$voiceEntry = [PSCustomObject]@{
    display_name = $DisplayName
    reference_wav = "voices/${VoiceId}_ref.wav"
    reference_transcript = $Transcript
    description = "Zero-shot cloned voice for $DisplayName."
}
$registry.voices | Add-Member -NotePropertyName $VoiceId -NotePropertyValue $voiceEntry -Force
$registry | ConvertTo-Json -Depth 10 | Set-Content $registryFile -Encoding UTF8
Write-Host "  [OK] Added '$VoiceId' to voice_registry.json" -ForegroundColor Green

# ----- Wire leader_voices.json -----
Write-Host ""
Write-Host "Checking leader_voices.json..." -ForegroundColor Yellow

if (Test-Path $leaderVoicesFile) {
    $leaders = Get-Content $leaderVoicesFile -Raw | ConvertFrom-Json
    # Find matching leaders by fuzzy name search
    $normalizedId = $VoiceId -replace '_', ''
    $matches = @()
    foreach ($prop in $leaders | Get-Member -MemberType NoteProperty) {
        $key = $prop.Name
        if ($key -like "*$normalizedId*" -or $key -like "*$VoiceId*") {
            $matches += $key
        }
    }

    if ($matches.Count -gt 0) {
        Write-Host "  Found matching leader(s): $($matches -join ', ')" -ForegroundColor White
        $wire = Read-Host "  Set tts_provider to 'elevenlabs' (enables local+EL fallback)? [Y/n]"
        if ($wire -ne 'n' -and $wire -ne 'N') {
            foreach ($key in $matches) {
                $leaders.$key.tts_provider = "elevenlabs"
            }
            $leaders | ConvertTo-Json -Depth 10 | Set-Content $leaderVoicesFile -Encoding UTF8
            Write-Host "  [OK] Updated $($matches.Count) leader entry(ies)" -ForegroundColor Green
        }
    } else {
        Write-Host "  No matching leaders found for '$VoiceId' in leader_voices.json" -ForegroundColor DarkGray
        Write-Host "  You can manually add tts_provider later." -ForegroundColor DarkGray
    }
} else {
    Write-Host "  leader_voices.json not found (normal if running from tts-server worktree)" -ForegroundColor DarkGray
}

# ----- Interactive Audition -----
if (-not $NoAudition) {
    Write-Host ""
    Write-Host "=== Audition ===" -ForegroundColor Cyan

    # Check if server is running
    $serverOk = $false
    try {
        $health = Invoke-RestMethod -Uri "$ServerUrl/health" -TimeoutSec 3
        $serverOk = $true
        Write-Host "  Server: $ServerUrl (model=$($health.model))" -ForegroundColor Green
    } catch {
        Write-Host "  Server not reachable at $ServerUrl" -ForegroundColor Yellow
        Write-Host "  Start it with: .\tools\Start-TtsServer.ps1" -ForegroundColor DarkGray
        Write-Host "  Skipping audition." -ForegroundColor DarkGray
    }

    if ($serverOk) {
        Write-Host ""
        Write-Host "  Type text to hear it in this voice. Blank line to finish." -ForegroundColor White
        Write-Host ""

        while ($true) {
            $text = Read-Host "  >"
            if (-not $text -or $text.Trim() -eq "") { break }

            try {
                $body = @{ text = $text; voice_id = $VoiceId } | ConvertTo-Json
                $t0 = Get-Date
                $response = Invoke-WebRequest -Uri "$ServerUrl/synthesize" `
                    -Method POST -ContentType "application/json" -Body $body `
                    -TimeoutSec 60
                $elapsed = ((Get-Date) - $t0).TotalSeconds

                # Save to temp file and play
                $tempWav = Join-Path $env:TEMP "tts_audition_${VoiceId}.wav"
                [System.IO.File]::WriteAllBytes($tempWav, $response.Content)
                Write-Host "    Playing... ($([math]::Round($elapsed, 1))s)" -ForegroundColor DarkGray

                # Play using Windows default player (non-blocking with SoundPlayer)
                $player = New-Object System.Media.SoundPlayer $tempWav
                $player.PlaySync()
            } catch {
                Write-Host "    Error: $_" -ForegroundColor Red
            }
        }
    }
}

# ----- Summary -----
Write-Host ""
Write-Host "=== Done! ===" -ForegroundColor Green
Write-Host ""
Write-Host "Voice '$VoiceId' ($DisplayName) is ready." -ForegroundColor White
Write-Host ""
Write-Host "Files changed:" -ForegroundColor DarkGray
Write-Host "  + $targetWav" -ForegroundColor DarkGray
Write-Host "  ~ $registryFile" -ForegroundColor DarkGray
if ($matches.Count -gt 0) {
    Write-Host "  ~ $leaderVoicesFile" -ForegroundColor DarkGray
}
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. git add tools/tts-server/voices/${VoiceId}_ref.wav tools/tts-server/voice_registry.json"
Write-Host "  2. git commit -m 'feat(tts): add $VoiceId voice'"
Write-Host "  3. git push"
Write-Host "  -> Every machine with git pull now has this voice."
Write-Host ""
