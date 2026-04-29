# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for DowagerMod installer (one-FOLDER build).

We deliberately use one-folder mode, NOT one-file. Reasons:
  1. One-file extracts python3xx.dll + ~hundreds of files to %TEMP% at
     runtime; Windows Smart App Control / WDAC / corp Application
     Control policies frequently block DLL loads from %TEMP% and yield
     a "not designed to run on Windows or contains an error" message.
  2. One-folder ships dll/data files as siblings of install.exe, on a
     real path the OS can evaluate, with no extraction step.
  3. Startup is faster (no archive extraction).

Distribution: zip the entire dist/install/ folder (or copy it whole).
Friends launch dist/install/install.exe directly.
"""

block_cipher = None

a = Analysis(
    ['install.py'],
    pathex=[],
    binaries=[],
    datas=[('install_noise.wav', '.')],
    hiddenimports=['tqdm'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# One-folder mode: EXE only takes a.scripts (+ exclude_binaries=True),
# then COLLECT bundles binaries/zipfiles/datas as siblings.
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='DowagerMod-Installer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='DowagerMod-Installer',
)

