<#
.SYNOPSIS
    Set up the local TTS server virtual environment.
.DESCRIPTION
    Creates a dedicated Python venv and installs all dependencies for the
    local TTS server (XTTSv2, Qwen3-TTS, FastAPI, torch with CUDA).
.PARAMETER CpuOnly
    Install CPU-only PyTorch (for laptops without CUDA toolkit).
#>
param(
    [switch]$CpuOnly
)

$ErrorActionPreference = "Stop"
$serverDir = Join-Path (Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)) "tools\tts-server"
$venvDir = Join-Path $serverDir ".venv"

Write-Host "=== Setting up TTS Server venv ===" -ForegroundColor Cyan
Write-Host "Location: $venvDir"

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
    & $pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu --quiet
} else {
    Write-Host "Installing PyTorch (CUDA 12.4)..." -ForegroundColor Yellow
    & $pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124 --quiet
}

# Install remaining deps
Write-Host "Installing TTS server dependencies..." -ForegroundColor Yellow
& $pip install -r (Join-Path $serverDir "requirements.txt") --quiet

Write-Host ""
Write-Host "=== Setup complete ===" -ForegroundColor Green
Write-Host "Verify: & '$python' -c `"import torch; print(f'torch={torch.__version__} cuda={torch.cuda.is_available()}')`""
Write-Host "Start:  .\tools\Start-TtsServer.ps1"
Write-Host ""

# Quick validation
& $python -c "import torch; print(f'  torch={torch.__version__} cuda={torch.cuda.is_available()}')"
& $python -c "import fastapi; print(f'  fastapi={fastapi.__version__}')"
