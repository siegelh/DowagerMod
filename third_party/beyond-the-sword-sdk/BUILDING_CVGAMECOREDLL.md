# Building `CvGameCoreDLL.dll` (DowagerMod Notes)

This documents the **known working** build flow we used for the BTS SDK source at:

- `third_party/beyond-the-sword-sdk/CvGameCoreDLL`

## What this is for

Use this when rebuilding `CvGameCoreDLL.dll` from source and dropping it into Civilization IV Beyond the Sword.

This folder is now treated as a vendored source folder inside the main `DowagerMod` repo (not a nested Git workflow).

## Prerequisites

1. SDK source cloned at:
- `C:\DowagerMod\third_party\beyond-the-sword-sdk`

2. Civ4 toolchain installed at:
- `C:\Program Files (x86)\Civ4SDK\Microsoft Visual C++ Toolkit 2003`
- `C:\Program Files (x86)\Civ4SDK\WindowsSDK`

3. Required headers present:
- `C:\Program Files (x86)\Civ4SDK\WindowsSDK\include\specstrings.h`
- `C:\Program Files (x86)\Civ4SDK\WindowsSDK\include\WinNT.h`
- `C:\Program Files (x86)\Civ4SDK\WindowsSDK\include\WinBase.h`
- `C:\Program Files (x86)\Civ4SDK\WindowsSDK\include\sal.h`

4. `nmake.exe` available (we used VS2022 nmake):
- `C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.38.33130\bin\Hostx64\x86\nmake.exe`

5. `cvtres.exe` available (same VS toolchain):
- `C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.38.33130\bin\Hostx64\x86\cvtres.exe`

## Important gotchas

- The makefile defaults to `C:\Program Files\...` paths. On this machine the SDK is under `C:\Program Files (x86)\...`, so `Makefile.settings` must override paths.
- If link fails with `LNK1158: cannot run 'cvtres.exe'`, prepend the VS `Hostx64\x86` bin folder to `PATH` before running `nmake`.
- Do not leave temporary SAL shim files in the repo source folder. If SAL is missing in the installed SDK include folder, fix the SDK install/header there.

## Preferred build command (PowerShell)

Run from `C:\DowagerMod`:

```powershell
.\tools\build_civ4_dll.ps1
```

This script:

1. Builds the DLL from `third_party/beyond-the-sword-sdk/CvGameCoreDLL`.
2. Copies a timestamped DLL into:
   `C:\DowagerMod\CoreFiles\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Assets`
3. Names it like:
   `CvGameCoreDLL_YYYYMMDD_HHMMSS.dll`

## Manual build commands (fallback)

Run from any shell:

```powershell
$NMAKE = "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.38.33130\bin\Hostx64\x86\nmake.exe"
$CVTRES_DIR = "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.38.33130\bin\Hostx64\x86"

Set-Location "C:\DowagerMod\third_party\beyond-the-sword-sdk\CvGameCoreDLL"

@"
TOOLKIT=C:\Program Files (x86)\Civ4SDK\Microsoft Visual C++ Toolkit 2003
PSDK=C:\Program Files (x86)\Civ4SDK\WindowsSDK
"@ | Set-Content -Path ".\Makefile.settings" -Encoding ascii

$env:PATH = "$CVTRES_DIR;$env:PATH"
$env:TARGET = "Release"
$env:INCLUDE = ""
$env:LIB = ""

& $NMAKE source_list /NOLOGO
& $NMAKE fastdep /NOLOGO
& $NMAKE dll /NOLOGO
```

## Expected output

Built DLL:

- `C:\DowagerMod\third_party\beyond-the-sword-sdk\CvGameCoreDLL\Release\CvGameCoreDLL.dll`

Timestamped installer-ready copy:

- `C:\DowagerMod\CoreFiles\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Assets\CvGameCoreDLL_YYYYMMDD_HHMMSS.dll`

## Deploy to game install (manual)

1. Backup current game DLL:
- `...\Beyond the Sword\Assets\CvGameCoreDLL.dll`

2. Copy built DLL over it.

3. Launch game and smoke-test startup + load a game.

## If build suddenly starts failing again

Check these first:

1. `sal.h` exists in `C:\Program Files (x86)\Civ4SDK\WindowsSDK\include\sal.h`.
2. `Makefile.settings` still points to `(x86)` paths.
3. `PATH` includes folder containing `cvtres.exe`.
4. `TARGET` is `Release` (not Debug).
