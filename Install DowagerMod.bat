@echo off
REM ============================================================
REM   DowagerMod launcher
REM ------------------------------------------------------------
REM   Double-click this file to install DowagerMod.
REM   It self-elevates to administrator (UAC prompt), then runs
REM   the installer .exe inside the cloned repo.
REM
REM   %~dp0 is the directory of THIS .bat file, so the path is
REM   correct regardless of where you cloned the repo.
REM ============================================================

setlocal
set "INSTALLER=%~dp0CoreFiles\dist\DowagerMod-Installer\DowagerMod-Installer.exe"

echo.
echo ============================================================
echo   DowagerMod installer launcher
echo ============================================================
echo.
echo Installer: %INSTALLER%
echo.

if not exist "%INSTALLER%" (
    echo ERROR: Installer not found at the path above.
    echo.
    echo Make sure you cloned the full DowagerMod repo, including the
    echo CoreFiles\dist\DowagerMod-Installer\ folder.
    echo.
    pause
    exit /b 1
)

REM Detect admin.
net session >nul 2>&1
if %errorlevel% equ 0 (
    echo Already running as administrator -- launching installer...
    echo.
    "%INSTALLER%"
    set "EXITCODE=%errorlevel%"
    echo.
    echo Installer exited with code %EXITCODE%.
    pause
    exit /b %EXITCODE%
)

echo Not running as administrator.
echo Requesting elevation -- a UAC prompt should appear.
echo (If you don't see it, check the taskbar or behind other windows.)
echo.
echo The installer will open in a NEW window after you approve the
echo prompt. You can close this window once the new one appears.
echo.

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "try { Start-Process -FilePath '%INSTALLER%' -Verb RunAs -ErrorAction Stop; Write-Host 'Elevation request sent.' } catch { Write-Host ('ERROR: ' + $_.Exception.Message) -ForegroundColor Red; exit 1 }"

if %errorlevel% neq 0 (
    echo.
    echo Elevation failed. If you clicked No on the UAC prompt, just
    echo re-run this .bat file. Otherwise, right-click DowagerMod-Installer.exe
    echo directly and choose 'Run as administrator'.
    echo.
    pause
    exit /b 1
)

echo.
echo Elevation request sent. Look for the new installer window.
echo.
pause
endlocal
