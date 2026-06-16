<#
.SYNOPSIS
    Generate a reference WAV for zero-shot voice cloning.
.DESCRIPTION
    Uses ElevenLabs to generate a high-quality 6-12 second reference clip
    for use by the local TTS server. The resulting WAV is saved to the
    voice registry folder.
.PARAMETER VoiceId
    Registry voice ID (e.g., 'dowager'). Default: dowager.
.PARAMETER Text
    Text to speak. Should be 6-12 seconds worth (~30-60 words) with varied
    intonation that represents the character's typical speech patterns.
#>
param(
    [string]$VoiceId = "dowager",
    [string]$Text = "My dear boy, one does not simply waltz into a ballroom without the proper introductions. The very notion is as absurd as it is vulgar. I shall speak plainly: breeding, like fine wine, cannot be rushed."
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$voicesDir = Join-Path $repoRoot "tools\tts-server\voices"

# Load .env for ElevenLabs credentials
$envFile = Join-Path $repoRoot ".env"
if (-not (Test-Path $envFile)) {
    Write-Error ".env not found at $envFile — need ELEVENLABS_API_KEY"
    exit 1
}

# Parse .env
Get-Content $envFile | ForEach-Object {
    if ($_ -match '^\s*([A-Z_]+)\s*=\s*(.+)$') {
        Set-Variable -Name $Matches[1] -Value $Matches[2].Trim()
    }
}

# Support both prefixed (DOWAGER_CHATTER_) and bare env var names
if (-not $ELEVENLABS_API_KEY) { $ELEVENLABS_API_KEY = (Get-Variable -Name "DOWAGER_CHATTER_ELEVENLABS_API_KEY" -ValueOnly -ErrorAction SilentlyContinue) }
if (-not $ELEVENLABS_VOICE_ID_DOWAGER) { $ELEVENLABS_VOICE_ID_DOWAGER = (Get-Variable -Name "DOWAGER_CHATTER_ELEVENLABS_VOICE_ID_DOWAGER" -ValueOnly -ErrorAction SilentlyContinue) }

if (-not $ELEVENLABS_API_KEY) {
    Write-Error "ELEVENLABS_API_KEY (or DOWAGER_CHATTER_ELEVENLABS_API_KEY) not found in .env"
    exit 1
}
if (-not $ELEVENLABS_VOICE_ID_DOWAGER) {
    Write-Error "ELEVENLABS_VOICE_ID_DOWAGER (or DOWAGER_CHATTER_ELEVENLABS_VOICE_ID_DOWAGER) not found in .env"
    exit 1
}

$outPath = Join-Path $voicesDir "${VoiceId}_ref.wav"
Write-Host "Generating reference WAV for '$VoiceId'..." -ForegroundColor Cyan
Write-Host "Text: $Text" -ForegroundColor Gray
Write-Host "Output: $outPath" -ForegroundColor Gray

# Call ElevenLabs API
$headers = @{
    "xi-api-key" = $ELEVENLABS_API_KEY
    "Content-Type" = "application/json"
}
$body = @{
    text = $Text
    model_id = "eleven_flash_v2_5"
    voice_settings = @{
        stability = 0.5
        similarity_boost = 0.8
        style = 0.3
    }
    output_format = "pcm_24000"
} | ConvertTo-Json

$uri = "https://api.elevenlabs.io/v1/text-to-speech/$ELEVENLABS_VOICE_ID_DOWAGER"

try {
    $response = Invoke-WebRequest -Uri $uri -Method POST -Headers $headers -Body $body -ContentType "application/json"
} catch {
    Write-Error "ElevenLabs API failed: $_"
    exit 1
}

# Wrap raw PCM in WAV header (24kHz, 16-bit, mono)
$pcmBytes = $response.Content
$sr = 24000
$bitsPerSample = 16
$channels = 1
$byteRate = $sr * $channels * ($bitsPerSample / 8)
$blockAlign = $channels * ($bitsPerSample / 8)
$dataSize = $pcmBytes.Length
$riffSize = 36 + $dataSize

$ms = [System.IO.MemoryStream]::new()
$bw = [System.IO.BinaryWriter]::new($ms)
$bw.Write([System.Text.Encoding]::ASCII.GetBytes("RIFF"))
$bw.Write([uint32]$riffSize)
$bw.Write([System.Text.Encoding]::ASCII.GetBytes("WAVE"))
$bw.Write([System.Text.Encoding]::ASCII.GetBytes("fmt "))
$bw.Write([uint32]16)
$bw.Write([uint16]1)  # PCM
$bw.Write([uint16]$channels)
$bw.Write([uint32]$sr)
$bw.Write([uint32]$byteRate)
$bw.Write([uint16]$blockAlign)
$bw.Write([uint16]$bitsPerSample)
$bw.Write([System.Text.Encoding]::ASCII.GetBytes("data"))
$bw.Write([uint32]$dataSize)
$bw.Write($pcmBytes)
$bw.Flush()

[System.IO.File]::WriteAllBytes($outPath, $ms.ToArray())
$bw.Dispose()
$ms.Dispose()

$duration = [math]::Round($dataSize / $byteRate, 1)
Write-Host ""
Write-Host "=== Reference WAV generated ===" -ForegroundColor Green
Write-Host "  File: $outPath"
Write-Host "  Size: $([math]::Round($dataSize / 1024, 1)) KB"
Write-Host "  Duration: ${duration}s"
Write-Host "  Format: 24kHz 16-bit mono PCM"
Write-Host ""
Write-Host "This file is your zero-shot reference for the local TTS model."
Write-Host "For best results, the reference should be 6-12 seconds of clean speech."
