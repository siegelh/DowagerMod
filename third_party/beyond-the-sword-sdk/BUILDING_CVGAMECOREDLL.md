# Building `CvGameCoreDLL.dll` (DowagerMod Notes)

This documents the current working build flow for the BtS SDK source at:

- `third_party/beyond-the-sword-sdk/CvGameCoreDLL`

If this file and `tools/build_civ4_dll.ps1` disagree, trust the script.

## Preferred build command

Run from `C:\DowagerMod`:

```powershell
.\tools\build_civ4_dll.ps1
```

Compile-only validation:

```powershell
.\tools\build_civ4_dll.ps1 -NoDeploy
```

## What the script does now

1. Builds the DLL from `third_party/beyond-the-sword-sdk/CvGameCoreDLL`.
2. If `-NoDeploy` is not used, backs up the current active DLL in:
   `C:\DowagerMod\CoreFiles\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Assets`
3. Replaces the active DLL at:
   `C:\DowagerMod\CoreFiles\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Assets\CvGameCoreDLL.dll`

## Toolchain assumptions

- Civ4 SDK toolkit:
  - `C:\Program Files (x86)\Civ4SDK\Microsoft Visual C++ Toolkit 2003`
  - `C:\Program Files (x86)\Civ4SDK\WindowsSDK`
- VS2022 `nmake.exe` / `cvtres.exe` under:
  - `C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\<version>\bin\Hostx64\x86`

The build script writes `Makefile.settings` with the `(x86)` toolkit paths before building.

## Expected output

Built DLL:

- `C:\DowagerMod\third_party\beyond-the-sword-sdk\CvGameCoreDLL\Release\CvGameCoreDLL.dll`

Deployed active DLL:

- `C:\DowagerMod\CoreFiles\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Assets\CvGameCoreDLL.dll`

Generated backup when deploying:

- `C:\DowagerMod\CoreFiles\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Assets\CvGameCoreDLL_backup_YYYYMMDD_HHMMSS.dll`

## Deploy model

- The build script deploys into the repo mirror unless `-NoDeploy` is used.
- The installer then copies the repo mirror into the live game install.
- Deployment is replace-plus-backup, not timestamped-active-output.

## Manual fallback

If the scripted build breaks, inspect `tools/build_civ4_dll.ps1` first. Any fallback manual instructions should match that script's current toolchain and output behavior.
