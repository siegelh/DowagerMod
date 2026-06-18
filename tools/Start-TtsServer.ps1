<#
.SYNOPSIS
    Start the local TTS server (zero-shot voice cloning).
.DESCRIPTION
    Launches the FastAPI TTS server with the configured backend (XTTSv2 or
    Chatterbox Turbo). Reads TTS_MODEL from .env to determine which model.
    Performs preflight checks and guides the user through any missing prerequisites.
.PARAMETER Port
    Port to listen on (default: 8080).
.PARAMETER Model
    Override the TTS model backend: 'xtts' or 'chatterbox'. If not specified,
    reads TTS_MODEL from .env (default: xtts).
.PARAMETER Device
    Compute device: 'auto' (default), 'cuda', or 'cpu'.
.PARAMETER SkipChecks
    Skip preflight validation (for advanced users).
#>
param(
    [int]$Port = 8080,
    [ValidateSet("", "xtts", "chatterbox")]
    [string]$Model = "",
    [ValidateSet("auto", "cuda", "cpu")]
    [string]$Device = "auto",
    [switch]$SkipChecks
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$serverDir = Join-Path $repoRoot "tools\tts-server"
$venvPython = Join-Path $serverDir ".venv\Scripts\python.exe"
$voicesDir = Join-Path $serverDir "voices"
$registryFile = Join-Path $serverDir "voice_registry.json"

# Determine TTS model: CLI param > .env > default
if (-not $Model) {
    $envFile = Join-Path $repoRoot ".env"
    if (Test-Path $envFile) {
        $envLine = Get-Content $envFile | Where-Object { $_ -match '^\s*TTS_MODEL\s*=' }
        if ($envLine) {
            $Model = ($envLine -split '=', 2)[1].Trim().Trim('"').Trim("'")
        }
    }
    if (-not $Model) { $Model = "xtts" }
}
Write-Host "TTS Model: $Model" -ForegroundColor DarkGray

# ===== Preflight Checks =====
function Write-Check($name, $ok, $detail) {
    if ($ok) {
        Write-Host "  [OK]   $name ... $detail" -ForegroundColor Green
    } else {
        Write-Host "  [FAIL] $name" -ForegroundColor Red
        Write-Host "         $detail" -ForegroundColor Yellow
    }
    return $ok
}

if (-not $SkipChecks) {
    Write-Host ""
    Write-Host "=== TTS Server Preflight ===" -ForegroundColor Cyan
    $allOk = $true

    # 1. Python
    $pyVer = $null
    try { $pyVer = (python --version 2>&1) -replace 'Python\s*', '' } catch {}
    $pyOk = $pyVer -and ([version]$pyVer -ge [version]"3.10.0")
    $allOk = $allOk -and (Write-Check "Python 3.10+" $pyOk $(if ($pyOk) { "($pyVer)" } else { "Fix: Install Python 3.10+ from python.org" }))

    # 2. Venv
    $venvOk = Test-Path $venvPython
    $allOk = $allOk -and (Write-Check "Venv exists" $venvOk $(if ($venvOk) { ".venv\Scripts\python.exe" } else { "Fix: .\tools\Setup-TtsServer.ps1" }))

    # 3. Torch + CUDA
    $torchInfo = ""
    $torchOk = $false
    if ($venvOk) {
        try {
            $torchInfo = & $venvPython -c "import torch; print(f'torch={torch.__version__} cuda={torch.cuda.is_available()}')" 2>&1
            $torchOk = $torchInfo -match "cuda=True"
            if (-not $torchOk -and $Device -ne "cpu") {
                $torchInfo = "CUDA not available. Fix: Install CUDA Toolkit 12.x, then re-run Setup-TtsServer.ps1"
            }
            if ($Device -eq "cpu") { $torchOk = $torchInfo -match "torch=" }
        } catch {
            $torchInfo = "torch not installed. Fix: .\tools\Setup-TtsServer.ps1"
        }
    } else {
        $torchInfo = "(skipped — venv missing)"
    }
    $allOk = $allOk -and (Write-Check "torch + CUDA" $torchOk $torchInfo)

    # 4. Model cached (only check for xtts)
    $modelOk = $false
    $modelDetail = ""
    if ($Model -eq "xtts" -and $venvOk) {
        try {
            $modelCheck = & $venvPython -c @"
import os, pathlib
# Coqui TTS caches models here on Windows
cache_dir = pathlib.Path(os.environ.get('XDG_DATA_HOME', pathlib.Path.home() / '.local' / 'share')) / 'tts'
alt_cache = pathlib.Path(os.environ.get('LOCALAPPDATA', '')) / 'tts'
found = any((d / 'tts_models--multilingual--multi-dataset--xtts_v2').exists() for d in [cache_dir, alt_cache] if d.exists())
if not found:
    # Also check the HuggingFace-style path
    hf = pathlib.Path.home() / '.cache' / 'huggingface'
    # Coqui uses its own cache, but check anyway
    pass
print('found' if found else 'missing')
"@ 2>&1
            $modelOk = $modelCheck -match "found"
            $modelDetail = if ($modelOk) { "XTTSv2 weights cached" } else { "Fix: .\tools\Setup-TtsServer.ps1 -DownloadModel (or start server once to auto-download ~1.7GB)" }
        } catch {
            $modelDetail = "Could not check. Will download on first start (~1.7GB)."
            $modelOk = $true  # non-blocking
        }
    } elseif ($Model -eq "chatterbox") {
        $modelOk = $true
        $modelDetail = "Chatterbox (downloads on first start if needed)"
    } else {
        $modelDetail = "(skipped — venv missing)"
    }
    $allOk = $allOk -and (Write-Check "Model cached" $modelOk $modelDetail)

    # 5. Voice registry
    $regOk = Test-Path $registryFile
    $voiceCount = 0
    if ($regOk) {
        try {
            $reg = Get-Content $registryFile -Raw | ConvertFrom-Json
            $voiceCount = ($reg.voices | Get-Member -MemberType NoteProperty).Count
        } catch {}
    }
    $allOk = $allOk -and (Write-Check "voice_registry.json" $regOk $(if ($regOk) { "$voiceCount voice(s) registered" } else { "Fix: Create voice_registry.json (see README.md)" }))

    # 6. Reference audio
    $wavFiles = @()
    if ($regOk -and $voiceCount -gt 0) {
        $reg.voices | Get-Member -MemberType NoteProperty | ForEach-Object {
            $voice = $reg.voices.($_.Name)
            $wavPath = Join-Path $serverDir $voice.reference_wav
            if (Test-Path $wavPath) { $wavFiles += $_.Name }
        }
    }
    $refOk = $wavFiles.Count -eq $voiceCount -and $voiceCount -gt 0
    $refDetail = if ($refOk) { "$($wavFiles.Count)/$voiceCount WAV(s) present" } else { "Missing ref WAVs. Fix: .\tools\Add-TtsVoice.ps1 or copy WAVs to voices/" }
    $allOk = $allOk -and (Write-Check "Reference audio" $refOk $refDetail)

    # 7. Port available
    $portInUse = $false
    try {
        $conn = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
        $portInUse = $null -ne $conn -and $conn.Count -gt 0
    } catch {}
    $portOk = -not $portInUse
    $allOk = $allOk -and (Write-Check "Port $Port available" $portOk $(if ($portOk) { "free" } else { "Fix: Stop the process using port $Port, or use -Port <other>" }))

    Write-Host ""
    if (-not $allOk) {
        Write-Host "Preflight FAILED. Fix the issues above and retry." -ForegroundColor Red
        Write-Host "Run with -SkipChecks to bypass (not recommended)." -ForegroundColor DarkGray
        exit 1
    }
    Write-Host "All checks passed!" -ForegroundColor Green
}

# ===== Launch Server =====
Write-Host ""
Write-Host "Starting local TTS server (model=$Model, port=$Port, device=$Device)..." -ForegroundColor Cyan
Write-Host "Endpoint: http://localhost:$Port" -ForegroundColor Green
Write-Host "Health:   http://localhost:$Port/health" -ForegroundColor Green
Write-Host "Stop:     Ctrl+C" -ForegroundColor DarkGray
Write-Host ""

$env:TTS_SERVER_PORT = $Port
$env:TTS_SERVER_DEVICE = $Device

& $venvPython (Join-Path $serverDir "server.py") --port $Port --device $Device --model $Model
