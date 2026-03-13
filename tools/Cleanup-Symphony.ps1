param(
    [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path,
    [string]$Workflow = "symphony/WORKFLOW.md",
    [int]$IssueNumber = 0,
    [switch]$Apply,
    [switch]$Json
)

$ErrorActionPreference = "Stop"

$python = Get-Command python -ErrorAction Stop
$pythonPath = $python.Source

Push-Location $RepoRoot
try {
    $arguments = @("-m", "symphony.main", "--workflow", $Workflow, "cleanup")
    if ($IssueNumber -gt 0) {
        $arguments += @("--issue-number", $IssueNumber)
    }
    if ($Apply) {
        $arguments += "--apply"
    }
    if ($Json) {
        $arguments += "--json"
    }

    & $pythonPath @arguments
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
