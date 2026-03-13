param(
    [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path,
    [string]$Workflow = "symphony/WORKFLOW.md",
    [int]$WaitSeconds = 30,
    [switch]$Force
)

$ErrorActionPreference = "Stop"

$python = Get-Command python -ErrorAction Stop
$pythonPath = $python.Source

Push-Location $RepoRoot
try {
    $arguments = @("-m", "symphony.main", "--workflow", $Workflow, "stop", "--wait-seconds", $WaitSeconds)
    if ($Force) {
        $arguments += "--force"
    }

    & $pythonPath @arguments
    $exitCode = $LASTEXITCODE

    if ($exitCode -eq 0) {
        & $pythonPath -m symphony.main --workflow $Workflow status
    }

    exit $exitCode
}
finally {
    Pop-Location
}
