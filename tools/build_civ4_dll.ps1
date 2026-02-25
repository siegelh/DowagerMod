param(
    [string]$RepoRoot = "C:\DowagerMod",
    [string]$VsToolsVersion = "14.38.33130",
    [string]$Target = "Release"
)

$ErrorActionPreference = "Stop"

$sdkRoot = Join-Path $RepoRoot "third_party\beyond-the-sword-sdk\CvGameCoreDLL"
$assetsOut = Join-Path $RepoRoot "CoreFiles\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Assets"

$nmake = "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\$VsToolsVersion\bin\Hostx64\x86\nmake.exe"
$cvtresDir = "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\$VsToolsVersion\bin\Hostx64\x86"

if (!(Test-Path $sdkRoot)) {
    throw "SDK folder not found: $sdkRoot"
}
if (!(Test-Path $assetsOut)) {
    throw "Assets output folder not found: $assetsOut"
}
if (!(Test-Path $nmake)) {
    throw "nmake not found: $nmake"
}

Set-Location $sdkRoot

@"
TOOLKIT=C:\Program Files (x86)\Civ4SDK\Microsoft Visual C++ Toolkit 2003
PSDK=C:\Program Files (x86)\Civ4SDK\WindowsSDK
"@ | Set-Content -Path ".\Makefile.settings" -Encoding ascii

$env:PATH = "$cvtresDir;$env:PATH"
$env:TARGET = $Target
$env:INCLUDE = ""
$env:LIB = ""

& $nmake source_list /NOLOGO
& $nmake fastdep /NOLOGO
& $nmake dll /NOLOGO

$builtDll = Join-Path $sdkRoot "$Target\CvGameCoreDLL.dll"
if (!(Test-Path $builtDll)) {
    throw "Build succeeded but DLL not found at expected path: $builtDll"
}

$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$stampedName = "CvGameCoreDLL_$stamp.dll"
$stampedOutPath = Join-Path $assetsOut $stampedName

Copy-Item $builtDll $stampedOutPath -Force

Write-Host "Built DLL: $builtDll"
Write-Host "Stamped copy: $stampedOutPath"
