# Civ4 Unit Art Crash Playbook

Use this whenever a unit crashes the game on build, selection, or Civilopedia render.

## Core Rule

When working with unit art, always verify every referenced asset path exists on disk before trusting an XML entry.

Do not assume an `ART_DEF_*` is valid just because it exists in `CIV4ArtDefines_Unit.xml`.

## Typical Crash Pattern

- Unit XML points to an `EarlyArtDefineTag`.
- That `ART_DEF_*` has one or more missing files:
  - `NIF`
  - `KFM`
  - `SHADERNIF` (if present)
  - `ShadowDef/ShadowNIF`
  - `Button`
- Game crashes when opening build UI, clicking build, or loading pedia/model preview.

## Fast Triage Workflow

1. Find the unit:
   - `CIV4UnitInfos.xml` -> `<Type>UNIT_...</Type>`
2. Read its art tag:
   - `<EarlyArtDefineTag>ART_DEF_...</EarlyArtDefineTag>`
3. Open matching `UnitArtInfo`:
   - `CIV4ArtDefines_Unit.xml` -> `<Type>ART_DEF_...</Type>`
4. Validate every referenced file exists in `Assets/Art/...`.
5. If any file is missing:
   - Create a new dedicated `ART_DEF_UNIT_<UNITNAME>_BTG`.
   - Point it to known-good, existing files.
   - Update only that unit to use the new art define.

## Why Dedicated Art Defines Are Preferred

- Safer: avoids breaking other units sharing a generic art define.
- Faster rollback/testing: isolate risky edits to one unit.
- Easier debugging: one unit, one art chain.

## Known Good Practice For New Unit Art

- Start from a working art block with matching unit class/rig.
- Copy the block to a new `ART_DEF_UNIT_*`.
- Change only what you need.
- Re-validate all referenced files after edits.

## Mandatory Validation Checklist

For the final `ART_DEF_*`, confirm these exist:

- `Button`
- `NIF`
- `KFM`
- `SHADERNIF` (if set)
- `ShadowDef/ShadowNIF`

If any item is missing, treat the define as unstable.

## Example PowerShell Checks

```powershell
# 1) Locate unit and art define
rg -n "UNIT_APACHE_MEDICINE_MAN_BTG|EarlyArtDefineTag" "CoreFiles/.../Assets/XML/Units/CIV4UnitInfos.xml"
rg -n "ART_DEF_UNIT_APACHE_MEDICINE_MAN_BTG" "CoreFiles/.../Assets/XML/Art/CIV4ArtDefines_Unit.xml"

# 2) Verify asset paths exist
$assets = "CoreFiles/.../Assets"
@(
  "Art/Caveman2Cosmos/art/interface/buttons/units/medicine_man.dds",
  "Art/Caveman2Cosmos/art/units/native_american_sparth/warden/converted_native.nif",
  "Art/Caveman2Cosmos/art/units/native_american_sparth/warden/converted_native.kfm",
  "Art/Units/01_UnitShadows/UnitShadow.nif"
) | ForEach-Object { "$_ => " + (Test-Path (Join-Path $assets $_)) }
```

## Notes

- Button size alone is not a reliable crash indicator.
- A 64x64 button can still crash if model/animation paths are broken.
- Missing KFM is a frequent hard-crash cause.
