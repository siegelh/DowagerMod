<#
.SYNOPSIS
    Start the local TTS server (zero-shot voice cloning).
.DESCRIPTION
    Launches the FastAPI TTS server with the specified model backend.
    Requires the tts-server venv to be set up first (see Setup-TtsServer.ps1).
.PARAMETER Model
    TTS model to use: 'xtts' (default) or 'qwen3'.
.PARAMETER Port
    Port to listen on (default: 8080).
.PARAMETER Device
    Compute device: 'auto' (default), 'cuda', or 'cpu'.
#>
param(
    [ValidateSet("xtts", "qwen3")]
    [string]$Model = "xtts",
    [int]$Port = 8080,
    [ValidateSet("auto", "cuda", "cpu")]
    [string]$Device = "auto"
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path))
$serverDir = Join-Path $repoRoot "tools\tts-server"
$venvPython = Join-Path $serverDir ".venv\Scripts\python.exe"

if (-not (Test-Path $venvPython)) {
    Write-Error @"
TTS server venv not found at $serverDir\.venv
Run Setup-TtsServer.ps1 first to create the environment.
"@
    exit 1
}

Write-Host "Starting local TTS server (model=$Model, port=$Port, device=$Device)..." -ForegroundColor Cyan
Write-Host "Endpoint: http://localhost:$Port" -ForegroundColor Green
Write-Host "Health:   http://localhost:$Port/health" -ForegroundColor Green
Write-Host ""

& $venvPython -m uvicorn tools.tts_server.server:app `
    --host 0.0.0.0 `
    --port $Port `
    --log-level info `
    --app-dir $repoRoot `
    --factory `
    2>&1

# Alternative direct launch if uvicorn module path doesn't work:
# & $venvPython (Join-Path $serverDir "server.py") --model $Model --port $Port --device $Device
