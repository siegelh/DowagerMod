<#
.SYNOPSIS
    Build the DowagerMod installer .exe using PyInstaller.

.DESCRIPTION
    Wraps PyInstaller invocation against CoreFiles/install_v2.spec so the
    process is repeatable and contributors don't have to remember the
    exact incantation. Output ends up at CoreFiles/dist/install.exe.

    Requires:
      - Python on PATH
      - pyinstaller installed (pip install pyinstaller)
      - tqdm installed (pip install tqdm) so it gets bundled

.PARAMETER Clean
    Pass -Clean to delete CoreFiles/build and CoreFiles/dist before building.
#>
[CmdletBinding()]
param(
    [switch]$Clean
)

$ErrorActionPreference = "Stop"

# Resolve repo root from this script's location (tools/ -> repo root).
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$coreFiles = Join-Path $repoRoot "CoreFiles"
$spec = Join-Path $coreFiles "install.spec"

# IMPORTANT: always use the dedicated build venv. If PyInstaller is picked
# up from Anaconda or another global Python, builds can hang for 15+ minutes
# instead of finishing in ~25 seconds.
$venvPyInstaller = Join-Path $repoRoot ".build_venv\Scripts\pyinstaller.exe"
if (-not (Test-Path $venvPyInstaller)) {
    throw @"
Build venv missing at: $venvPyInstaller

Create it with:
  python -m venv .build_venv
  .\.build_venv\Scripts\pip install pyinstaller tqdm
"@
}

if (-not (Test-Path $spec)) {
    throw "Spec file not found: $spec"
}

Push-Location $coreFiles
try {
    if ($Clean) {
        foreach ($d in @("build", "dist")) {
            $p = Join-Path $coreFiles $d
            if (Test-Path $p) {
                Write-Host "Removing $p" -ForegroundColor Yellow
                Remove-Item -Recurse -Force $p
            }
        }
    }

    Write-Host "Building installer with PyInstaller..." -ForegroundColor Cyan
    Write-Host "  (using $venvPyInstaller)" -ForegroundColor DarkGray
    # Build into CoreFiles/build and CoreFiles/dist so the .exe lives next to
    # the mod payload (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/).
    # Friends clone the repo, open CoreFiles\dist\DowagerMod-Installer\ and
    # double-click DowagerMod-Installer.exe.
    & $venvPyInstaller --noconfirm `
        --workpath (Join-Path $coreFiles "build") `
        --distpath (Join-Path $coreFiles "dist") `
        install.spec
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller failed with exit code $LASTEXITCODE"
    }

    $exe = Join-Path $coreFiles "dist\DowagerMod-Installer\DowagerMod-Installer.exe"
    if (-not (Test-Path $exe)) {
        throw "Build appeared to succeed but $exe was not produced."
    }

    $folderSize = [Math]::Round(((Get-ChildItem (Split-Path $exe) -Recurse -File | Measure-Object Length -Sum).Sum) / 1MB, 2)
    Write-Host ""
    Write-Host "OK: $exe (folder $folderSize MB)" -ForegroundColor Green
    Write-Host ""
    Write-Host "Friends clone the repo, open CoreFiles\dist\DowagerMod-Installer\," -ForegroundColor Cyan
    Write-Host "right-click DowagerMod-Installer.exe -> Run as administrator." -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Smoke-testing --help..." -ForegroundColor Cyan
    & $exe --help
    if ($LASTEXITCODE -ne 0) {
        throw "Built exe failed --help smoke test (exit $LASTEXITCODE)."
    }
}
finally {
    Pop-Location
}
