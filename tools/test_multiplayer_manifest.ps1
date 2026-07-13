[CmdletBinding()]
param(
    [string]$RepoRoot
)

$ErrorActionPreference = "Stop"
if (-not $RepoRoot) {
    $RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
}
$tool = Join-Path $PSScriptRoot "multiplayer_manifest.ps1"
$source = Join-Path $RepoRoot "CoreFiles\Sid Meier's Civilization IV Beyond the Sword"
$scratch = Join-Path $RepoRoot ".mp-manifest-test"
$copy = Join-Path $scratch "payload"
$manifestA = Join-Path $scratch "a.json"
$manifestB = Join-Path $scratch "b.json"
$engine = (Get-Process -Id $PID).Path

try {
    if (Test-Path -LiteralPath $scratch) {
        Remove-Item -LiteralPath $scratch -Recurse -Force
    }
    New-Item -ItemType Directory -Path (Join-Path $copy "Beyond the Sword\Assets") -Force | Out-Null
    $sourceAssets = Join-Path $source "Beyond the Sword\Assets"
    Copy-Item -LiteralPath (Join-Path $sourceAssets "XML") -Destination (Join-Path $copy "Beyond the Sword\Assets") -Recurse
    Copy-Item -LiteralPath (Join-Path $sourceAssets "Python") -Destination (Join-Path $copy "Beyond the Sword\Assets") -Recurse
    Copy-Item -LiteralPath (Join-Path $sourceAssets "CvGameCoreDLL.dll") -Destination (Join-Path $copy "Beyond the Sword\Assets")

    & $engine -NoProfile -File $tool -Root $source -OutputPath $manifestA
    if ($LASTEXITCODE -ne 0) { throw "Reference manifest generation failed." }
    & $engine -NoProfile -File $tool -Root $copy -OutputPath $manifestB
    if ($LASTEXITCODE -ne 0) { throw "Copy manifest generation failed." }
    if ((Get-FileHash -LiteralPath $manifestA -Algorithm SHA256).Hash -ne
        (Get-FileHash -LiteralPath $manifestB -Algorithm SHA256).Hash) {
        throw "Equivalent roots did not produce byte-identical deterministic JSON."
    }
    & $engine -NoProfile -File $tool -ReferenceManifest $manifestA -CandidateManifest $manifestB
    if ($LASTEXITCODE -ne 0) { throw "Identical manifest comparison failed." }

    $altered = Get-ChildItem -LiteralPath (Join-Path $copy "Beyond the Sword\Assets\XML") -Recurse -File -Filter *.xml |
        Sort-Object FullName |
        Select-Object -First 1
    [System.IO.File]::AppendAllText($altered.FullName, "`r`n<!-- deliberate manifest mismatch -->`r`n")

    & $engine -NoProfile -File $tool -ReferenceRoot $source -CandidateRoot $copy
    if ($LASTEXITCODE -ne 1) {
        throw "Altered-file comparison returned $LASTEXITCODE instead of mismatch exit code 1."
    }
    Write-Host "PASS: identical data matched; deliberate alteration was reported with exit code 1."
}
finally {
    if (Test-Path -LiteralPath $scratch) {
        Remove-Item -LiteralPath $scratch -Recurse -Force
    }
}

exit 0
