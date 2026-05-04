# Glyph Diagnostics

## Purpose

Use this workflow when `GameFont`-rendered symbols disappear, render as text,
or differ between multiplayer clients. This covers religion icons, resource
icons, yields, commerce, corporation icons, and generic font symbols.

## In-game dump

Trigger either from a running game:

```text
Ctrl+Shift+G
!glyphdump
```

The dump is local/read-only. It does not change game state, RNG, network state,
or synchronized script data.

Primary output path:

```text
%LOCALAPPDATA%\DowagerMod\GlyphDiagnostics\
```

File names include turn, player id, leader/civilization labels, and a timestamp,
for example:

```text
GlyphDiagnostics_Turn100_Player01_Enrico_Dandolo_Venice_YYYYMMDD-HHMMSS.log
```

The LocalAppData path is intentional: it avoids OneDrive document-redirection
problems that can affect Civ4's normal `Documents\My Games\Beyond the Sword`
logs.

## What the dump captures

- loaded `GameFont.tga` and `GameFont_75.tga` file fingerprints
- active player, leader, civilization, turn, era, and multiplayer state
- runtime yield, commerce, religion, corporation, bonus, and generic symbol
  character assignments
- city religion expectations for each known city
- bonus/resource glyph allocation summary
- Civ4 user-data/cache state
- trigger context and local probe strings

If one player sees missing city religion icons and another does not, collect
both logs from the same turn. Identical file hashes and runtime symbol tables
point away from XML/font assignment drift and toward client-local rendering,
cache, or UI/font-atlas state.

## Offline diagnostic

Run from repo root:

```powershell
python .\tools\glyph_diagnostic.py --fail-on-error
```

Optional artifacts:

```powershell
python .\tools\glyph_diagnostic.py --fail-on-error `
  --json-out .\tmp\glyph_diagnostic.json `
  --csv-out .\tmp\glyph_symbols.csv
```

The offline diagnostic models `CvGameTextMgr::assignFontIds(...)`, compares the
repo font files against the local pristine install when available, and reports
duplicate or risky character allocations.

## Key implementation paths

- In-game Python:
  - `CoreFiles\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Assets\Python\CvGlyphDiagnostics.py`
  - `CoreFiles\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Assets\Python\CvEventManager.py`
- Offline tool:
  - `tools\glyph_diagnostic.py`
- DLL symbol assignment and city billboard icon text:
  - `third_party\beyond-the-sword-sdk\CvGameCoreDLL\CvGameTextMgr.cpp`

