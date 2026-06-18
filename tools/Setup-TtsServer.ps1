<#
.SYNOPSIS
    Set up the local TTS server virtual environment.
.DESCRIPTION
    Creates a dedicated Python venv and installs all dependencies for the
    local TTS server. Supports XTTSv2 (default) or Chatterbox Turbo backend.
    Optionally pre-downloads model weights so first server start is instant.
.PARAMETER Model
    TTS backend to install: 'xtts' (default) or 'chatterbox'.
.PARAMETER CpuOnly
    Install CPU-only PyTorch (for machines without CUDA toolkit).
.PARAMETER SkipModel
    Skip model pre-download (it will download on first server start instead).
#>
param(
    [ValidateSet("xtts", "chatterbox")]
    [string]$Model = "xtts",
    [switch]$CpuOnly,
    [switch]$SkipModel
)

$ErrorActionPreference = "Stop"
$serverDir = Join-Path (Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)) "tools\tts-server"
$venvDir = Join-Path $serverDir ".venv"

Write-Host "=== Setting up TTS Server venv ($Model backend) ===" -ForegroundColor Cyan
Write-Host "Location: $venvDir"

# If venv exists but model changed, recreate it
$modelMarker = Join-Path $venvDir ".tts_model"
if (Test-Path $venvDir) {
    $existingModel = ""
    if (Test-Path $modelMarker) { $existingModel = (Get-Content $modelMarker -Raw).Trim() }
    if ($existingModel -ne $Model) {
        Write-Host "Switching model from '$existingModel' to '$Model' — rebuilding venv..." -ForegroundColor Yellow
        Remove-Item $venvDir -Recurse -Force
    }
}

# Create venv
if (-not (Test-Path $venvDir)) {
    Write-Host "Creating venv..." -ForegroundColor Yellow
    python -m venv $venvDir
} else {
    Write-Host "Venv already exists, upgrading pip..." -ForegroundColor Yellow
}

$pip = Join-Path $venvDir "Scripts\pip.exe"
$python = Join-Path $venvDir "Scripts\python.exe"

# Upgrade pip
& $python -m pip install --upgrade pip --quiet

# Install PyTorch (CUDA or CPU)
if ($CpuOnly) {
    Write-Host "Installing PyTorch (CPU-only)..." -ForegroundColor Yellow
    & $pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu --quiet
} else {
    Write-Host "Installing PyTorch (CUDA 12.4)..." -ForegroundColor Yellow
    & $pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu124 --quiet
}

# Install remaining deps (model-specific requirements file)
$reqFile = if ($Model -eq "chatterbox") { "requirements-chatterbox.txt" } else { "requirements.txt" }
Write-Host "Installing TTS server dependencies ($reqFile)..." -ForegroundColor Yellow
& $pip install -r (Join-Path $serverDir $reqFile) --quiet

# Record which model this venv was built for
Set-Content -Path (Join-Path $venvDir ".tts_model") -Value $Model

Write-Host ""
Write-Host "=== Dependencies installed ===" -ForegroundColor Green

# Quick validation
& $python -c "import torch; print(f'  torch={torch.__version__} cuda={torch.cuda.is_available()}')"
& $python -c "import fastapi; print(f'  fastapi={fastapi.__version__}')"

# Pre-download model weights
if (-not $SkipModel) {
    if ($Model -eq "xtts") {
        Write-Host ""
        Write-Host "=== Downloading XTTSv2 model weights (~1.7 GB) ===" -ForegroundColor Cyan
        Write-Host "This is a one-time download. The model is cached globally." -ForegroundColor DarkGray
        Write-Host ""
        $env:COQUI_TOS_AGREED = "1"
        & $python -c @"
import os
os.environ['COQUI_TOS_AGREED'] = '1'
# Monkey-patch torch.load for PyTorch 2.6+ compatibility
import torch
_orig = torch.load
def _patched(*a, **kw):
    kw.setdefault('weights_only', False)
    return _orig(*a, **kw)
torch.load = _patched

from TTS.api import TTS
print('Downloading/verifying XTTSv2 model...')
tts = TTS('tts_models/multilingual/multi-dataset/xtts_v2', progress_bar=True)
print('Model ready!')
"@
        if ($LASTEXITCODE -ne 0) {
            Write-Host "WARNING: Model download may have failed. The server will retry on first start." -ForegroundColor Yellow
        } else {
            Write-Host "Model download complete!" -ForegroundColor Green
        }
    } elseif ($Model -eq "chatterbox") {
        Write-Host ""
        Write-Host "=== Downloading Chatterbox Turbo model weights ===" -ForegroundColor Cyan
        Write-Host "This is a one-time download. The model is cached in HuggingFace cache." -ForegroundColor DarkGray
        Write-Host ""
        & $python -c @"
from chatterbox.tts_turbo import ChatterboxTurboTTS
print('Downloading/verifying Chatterbox Turbo model...')
model = ChatterboxTurboTTS.from_pretrained(device='cpu')
print('Model ready!')
"@
        if ($LASTEXITCODE -ne 0) {
            Write-Host "WARNING: Model download may have failed. The server will retry on first start." -ForegroundColor Yellow
        } else {
            Write-Host "Model download complete!" -ForegroundColor Green
        }
    }
} else {
    Write-Host ""
    Write-Host "Skipping model download (-SkipModel). It will download on first server start." -ForegroundColor DarkGray
}

Write-Host ""
Write-Host "=== Setup complete ===" -ForegroundColor Green
Write-Host "Start the server: .\tools\Start-TtsServer.ps1" -ForegroundColor White
Write-Host ""
