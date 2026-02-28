param(
    [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
)

$ErrorActionPreference = "Stop"

& (Join-Path $PSScriptRoot "test_gate.ps1") -RepoRoot $RepoRoot -All
