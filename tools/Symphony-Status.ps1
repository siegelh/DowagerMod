param(
    [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path,
    [string]$Workflow = "symphony/WORKFLOW.md",
    [switch]$Json
)

$ErrorActionPreference = "Stop"

$python = Get-Command python -ErrorAction Stop
$pythonPath = $python.Source

Push-Location $RepoRoot
try {
    $arguments = @("-m", "symphony.main", "--workflow", $Workflow, "status")
    if ($Json) {
        $arguments += "--json"
    }

    & $pythonPath @arguments
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
