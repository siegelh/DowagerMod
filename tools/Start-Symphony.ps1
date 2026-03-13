param(
    [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path,
    [string]$Workflow = "symphony/WORKFLOW.md",
    [int]$PollIntervalSeconds = 0,
    [int]$ErrorBackoffSeconds = 0,
    [switch]$ShowWindow
)

$ErrorActionPreference = "Stop"

$python = Get-Command python -ErrorAction Stop
$pythonPath = $python.Source

Push-Location $RepoRoot
try {
    $statusArgs = @("-m", "symphony.main", "--workflow", $Workflow, "status", "--json")
    $statusJson = & $pythonPath @statusArgs
    if ($LASTEXITCODE -ne 0) {
        throw "Unable to read Symphony status."
    }

    $status = $statusJson | ConvertFrom-Json
    if ($status.is_running) {
        Write-Host "Symphony is already running (pid $($status.pid))."
        exit 0
    }

    $arguments = @("-m", "symphony.main", "--workflow", $Workflow, "serve")
    if ($PollIntervalSeconds -gt 0) {
        $arguments += @("--poll-interval-seconds", $PollIntervalSeconds)
    }
    if ($ErrorBackoffSeconds -gt 0) {
        $arguments += @("--error-backoff-seconds", $ErrorBackoffSeconds)
    }

    $windowStyle = if ($ShowWindow) { "Normal" } else { "Hidden" }
    $process = Start-Process -FilePath $pythonPath -ArgumentList $arguments -WorkingDirectory $RepoRoot -WindowStyle $windowStyle -PassThru

    Start-Sleep -Seconds 2

    Write-Host "Started Symphony (pid $($process.Id))."
    & $pythonPath -m symphony.main --workflow $Workflow status
}
finally {
    Pop-Location
}
