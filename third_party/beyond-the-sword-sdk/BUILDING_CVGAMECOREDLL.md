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

- Civ4 SDK toolkit (any of these locations are auto-detected by the script):
  - `C:\Program Files (x86)\Civ4SDK\` (preferred — Nightinggale default)
  - `C:\Civ4SDK\Civ4SDK\` (Nightinggale installer's nested fallback layout)
  - `C:\Civ4SDK\`
  - Override with `-Civ4SdkRoot <path>`.
  - Inside that root the script expects:
    - `Microsoft Visual C++ Toolkit 2003\bin\cl.exe` and `link.exe`
    - `WindowsSDK\Include\` headers and `WindowsSDK\bin\rc.exe`
- VS2022 `nmake.exe` / `cvtres.exe` under:
  - `C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\<version>\bin\Hostx64\x86`
  - The script's default `-VsToolsVersion` is `14.38.33130`, but if that exact
    folder is not present and the `MSVC` root has any installed toolset, the
    script auto-falls-back to the highest-numbered one found there. Override
    with `-VsToolsVersion <version>` if you need a specific build.

The build script writes `Makefile.settings` with the resolved toolkit paths before building.

### `sal.h` workaround for Nightinggale's WindowsSDK

The CivFanatics-packaged WindowsSDK ships `specstrings*.h` but **not** `sal.h`,
so a fresh install of the Civ4 SDK toolkit will fail the precompile step with
`fatal error C1083: Cannot open include file: 'sal.h'`.

A pre-tested empty-macro stub is checked in at `tools/civ4sdk_sal_stub.h`. To
fix a fresh machine after installing the Civ4 SDK toolkit, copy it to the
WindowsSDK include folder, e.g.:

```powershell
Copy-Item tools\civ4sdk_sal_stub.h "C:\Civ4SDK\Civ4SDK\WindowsSDK\include\sal.h"
# or, for the (x86) install location:
# Copy-Item tools\civ4sdk_sal_stub.h "C:\Program Files (x86)\Civ4SDK\WindowsSDK\Include\sal.h"
```

The stub defines all SAL/specstrings annotation macros (`__in`, `__out`,
`__checkReturn`, `__inner_checkReturn`, etc.) as no-ops so the legacy VC7.1
compiler can parse modern Win32 headers.

## First-time machine setup

If `C:\Program Files (x86)\Civ4SDK\` is missing, install in this order:

1. **Visual Studio 2022 Community + Desktop development with C++ workload**:
   ```powershell
   winget install --id Microsoft.VisualStudio.2022.Community --accept-source-agreements --accept-package-agreements `
     --override "--add Microsoft.VisualStudio.Workload.NativeDesktop --includeRecommended --quiet --wait --norestart"
   ```
2. **Civ4 SDK toolkit** (legacy MS VC++ Toolkit 2003 + Platform SDK,
   no longer hosted by Microsoft). Download Nightinggale's SDK installer
   from CivFanatics:
   - Forum thread: `https://forums.civfanatics.com/threads/sdk-installer.649662/`
   - Run the installer interactively. The installer may write to
     `C:\Program Files (x86)\Civ4SDK\` or to `C:\Civ4SDK\Civ4SDK\` (nested);
     either is auto-detected by the build script.
3. **Patch `sal.h`** (the installer omits it — see the stub workaround
   section above):
   ```powershell
   # adjust path to wherever the installer placed WindowsSDK\Include
   Copy-Item tools\civ4sdk_sal_stub.h "C:\Civ4SDK\Civ4SDK\WindowsSDK\include\sal.h"
   ```
4. Verify install with `.\tools\build_civ4_dll.ps1 -NoDeploy`.

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
