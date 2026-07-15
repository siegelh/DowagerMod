param(
    [string]$RepoRoot = "",
    [string]$VsToolsVersion = "14.38.33130",
    [string]$Target = "Release",
    [string]$Civ4SdkRoot = "",
    [switch]$NoDeploy
)

$ErrorActionPreference = "Stop"

if (-not $RepoRoot) {
    $RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
}

$sdkRoot = Join-Path $RepoRoot "third_party\beyond-the-sword-sdk\CvGameCoreDLL"
$assetsOut = Join-Path $RepoRoot "CoreFiles\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Assets"

$msvcRoot = "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC"
$pinnedDir = Join-Path $msvcRoot $VsToolsVersion
if (!(Test-Path $pinnedDir) -and (Test-Path $msvcRoot)) {
    $detected = Get-ChildItem $msvcRoot -Directory -ErrorAction SilentlyContinue |
        Sort-Object Name -Descending |
        Select-Object -First 1
    if ($detected) {
        Write-Host "[build_civ4_dll] Pinned MSVC $VsToolsVersion not present; using detected $($detected.Name)."
        $VsToolsVersion = $detected.Name
    }
}
$nmake = "$msvcRoot\$VsToolsVersion\bin\Hostx64\x86\nmake.exe"
$cvtresDir = "$msvcRoot\$VsToolsVersion\bin\Hostx64\x86"

if (!(Test-Path $sdkRoot)) {
    throw "SDK folder not found: $sdkRoot"
}
if (!(Test-Path $assetsOut)) {
    throw "Assets output folder not found: $assetsOut"
}
if (!(Test-Path $nmake)) {
    throw "nmake not found: $nmake"
}

if (-not $Civ4SdkRoot) {
    $candidates = @(
        "C:\Program Files (x86)\Civ4SDK",
        "C:\Civ4SDK\Civ4SDK",
        "C:\Civ4SDK"
    )
    foreach ($c in $candidates) {
        if (Test-Path (Join-Path $c "Microsoft Visual C++ Toolkit 2003\bin\cl.exe")) {
            $Civ4SdkRoot = $c
            break
        }
    }
}
if (-not $Civ4SdkRoot -or -not (Test-Path (Join-Path $Civ4SdkRoot "Microsoft Visual C++ Toolkit 2003\bin\cl.exe"))) {
    throw "Civ4 SDK toolkit (Nightinggale's installer) not found. Pass -Civ4SdkRoot pointing to the folder containing 'Microsoft Visual C++ Toolkit 2003' and 'WindowsSDK'."
}
Write-Host "[build_civ4_dll] Using Civ4 SDK at: $Civ4SdkRoot"

Set-Location $sdkRoot

@"
TOOLKIT=$Civ4SdkRoot\Microsoft Visual C++ Toolkit 2003
PSDK=$Civ4SdkRoot\WindowsSDK
"@ | Set-Content -Path ".\Makefile.settings" -Encoding ascii

$env:PATH = "$cvtresDir;$env:PATH"
$env:TARGET = $Target
$env:INCLUDE = ""
$env:LIB = ""

foreach ($nmakeTarget in @("source_list", "fastdep", "dll")) {
    # NOTE: PowerShell variable names are case-insensitive, so a loop variable
    # named "$target" would silently clobber the "-Target" (Release/Debug/...)
    # script parameter once the loop reaches the "dll" nmake target, breaking
    # the expected $Target\CvGameCoreDLL.dll output path below. Keep this
    # loop variable name distinct from $Target.
    & $nmake $nmakeTarget /NOLOGO
    if ($LASTEXITCODE -ne 0) {
        throw "nmake target '$nmakeTarget' failed with exit code $LASTEXITCODE"
    }
}

$builtDll = Join-Path $sdkRoot "$Target\CvGameCoreDLL.dll"
if (!(Test-Path $builtDll)) {
    throw "Build succeeded but DLL not found at expected path: $builtDll"
}

$targetOutPath = Join-Path $assetsOut "CvGameCoreDLL.dll"

if ($NoDeploy) {
    Write-Host "Built DLL: $builtDll"
    Write-Host "NoDeploy enabled. Skipping copy/replace in assets folder."
    return
}

if (Test-Path $targetOutPath) {
    $stamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupName = "CvGameCoreDLL_backup_$stamp.dll"
    $backupOutPath = Join-Path $assetsOut $backupName
    Move-Item $targetOutPath $backupOutPath -Force
    Write-Host "Backed up existing DLL: $backupOutPath"
}

Copy-Item $builtDll $targetOutPath -Force

Write-Host "Built DLL: $builtDll"
Write-Host "Replaced active DLL: $targetOutPath"
