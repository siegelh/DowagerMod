#requires -Version 5.0
<#
.SYNOPSIS
    Start the DowagerMod Chatter sidecar daemon as a detached background process.

.DESCRIPTION
    Launches `pythonw.exe -m tools.chatter.chatter_daemon` from the repo root
    with no console window. Exits immediately. The daemon runs until killed
    or the user logs out.

    Idempotent: if a daemon PID file exists with a fresh heartbeat, prints
    the running PID and exits. Use Stop-Chatter.ps1 to stop a running daemon.

.EXAMPLE
    .\tools\Start-Chatter.ps1
#>

[CmdletBinding()]
param(
    [switch] $Foreground,
    [string] $PythonExe
)

$ErrorActionPreference = 'Stop'

. (Join-Path $PSScriptRoot 'Chatter-Common.ps1')

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot '..')
$spoolDir = Get-ChatterSpoolDir
$pidFile = Get-ChatterPidFile

# Check existing daemon
if (Test-Path $pidFile) {
    try {
        $pidJson = Get-Content -Path $pidFile -Raw | ConvertFrom-Json
        $existingPid = [int]$pidJson.pid
        $heartbeat = [double]$pidJson.heartbeat_unix
        $age = ([DateTimeOffset]::Now.ToUnixTimeSeconds() - $heartbeat)
        if ($age -lt 60 -and $existingPid -gt 0) {
            try {
                $proc = Get-Process -Id $existingPid -ErrorAction Stop
                Write-Host "Chatter sidecar is already running. PID=$existingPid age=$([math]::Round($age,1))s"
                exit 0
            } catch {
                # PID file is stale — process is gone
                Write-Host "Stale PID file (process $existingPid not running); starting fresh."
            }
        }
    } catch { }
}

# Pick Python: explicit param > venv > system python > anaconda fallback
function Find-Python {
    param([string]$Override)
    if ($Override -and (Test-Path $Override)) { return $Override }
    $candidates = @(
        (Join-Path $repoRoot '.build_venv\Scripts\pythonw.exe'),
        (Join-Path $repoRoot 'tmp\chatter_smoke_venv\Scripts\pythonw.exe'),
        (Join-Path $repoRoot '.build_venv\Scripts\python.exe'),
        (Join-Path $repoRoot 'tmp\chatter_smoke_venv\Scripts\python.exe')
    )
    foreach ($c in $candidates) {
        if (Test-Path $c) { return $c }
    }
    # Fall back to whatever python is on PATH
    $cmd = Get-Command python -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    $cmd = Get-Command pythonw -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    return $null
}

$python = Find-Python -Override $PythonExe
if (-not $python) {
    Write-Error "No Python interpreter found. Pass -PythonExe or create a venv at .build_venv\."
    exit 2
}

# Verify openai is installed
$check = & $python -c "import openai; print(openai.__version__)" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Warning "openai package not found in $python. Installing..."
    & $python -m pip install --quiet --disable-pip-version-check openai
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to install openai. Run: $python -m pip install openai"
        exit 3
    }
}

if ($Foreground) {
    Write-Host "Starting chatter daemon in foreground (Ctrl+C to stop)..."
    Push-Location $repoRoot
    try {
        & $python -m tools.chatter.chatter_daemon
    } finally {
        Pop-Location
    }
    exit $LASTEXITCODE
}

# Background launch via pythonw if available, falling back to python with hidden window
$pythonw = $python.Replace('\python.exe', '\pythonw.exe')
if (Test-Path $pythonw) {
    $launcher = $pythonw
    $windowStyle = 'Hidden'
} else {
    $launcher = $python
    $windowStyle = 'Hidden'
}

Write-Host "Launching detached daemon: $launcher -m tools.chatter.chatter_daemon"
$startInfo = @{
    FilePath = $launcher
    ArgumentList = @('-m', 'tools.chatter.chatter_daemon')
    WindowStyle = $windowStyle
    WorkingDirectory = $repoRoot
    PassThru = $true
}
$proc = Start-Process @startInfo
Start-Sleep -Seconds 2
if ($proc.HasExited) {
    Write-Error "Daemon exited immediately with code $($proc.ExitCode). Check $spoolDir\daemon.log"
    exit 4
}
Write-Host "Daemon started. PID=$($proc.Id). Logs: $spoolDir\daemon.log" -ForegroundColor Green
