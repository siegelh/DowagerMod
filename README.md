# DowagerMod

## Install

1. Build or obtain the installer executable from `dist`.
2. Run `install.exe`.
3. The installer copies files from:
   - `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/`
   into the live game install.

## Build DLL (CvGameCoreDLL)

Use the canonical build script from repo root:

```powershell
.\tools\build_civ4_dll.ps1
```

What it does:

1. Builds `CvGameCoreDLL.dll` from:
   - `third_party/beyond-the-sword-sdk/CvGameCoreDLL`
2. Copies a timestamped DLL to:
   - `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets`
3. Output name format:
   - `CvGameCoreDLL_YYYYMMDD_HHMMSS.dll`

Notes:

- This timestamped DLL is ignored by git via `.gitignore`.
- Rename/copy it to `CvGameCoreDLL.dll` when you want it to be the active shipped DLL.

## Rebuild Installer

From repo root:

```powershell
python -m PyInstaller --onefile install.py
```

## More DLL Build Details

See:

- `third_party/beyond-the-sword-sdk/BUILDING_CVGAMECOREDLL.md`
