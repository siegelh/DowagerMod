# Live Building Button Safety

- Status: `implemented_pending_gameplay_validation`
- Owner / agent: GitHub Copilot CLI
- Last updated: `2026-09-02`

## Problem Statement

Selecting Carthage's Byrsa Elephant Treasury for construction crashed the game
while the city queue attempted to load its icon. Its live building art
definition used a leading comma with a standalone DDS path:

`<Button>,Art/.../krak.dds</Button>`

Civ4 interprets a leading comma as atlas syntax, but this value provides no
atlas file or coordinates. The same pattern previously caused the Temple of
Ramesses crash fixed by commit `12e22297f`.

## Scope

- Correct all 20 malformed standalone button values referenced by live
  `BuildingInfo` records.
- Preserve the referenced DDS files and all model/gameplay data.
- Add validation that follows live `BuildingInfo -> ArtDefineTag -> Button`
  relationships even when the art definition is older than the current diff.

## Non-Goals

- Do not rewrite the remaining dormant/imported building art catalog.
- Do not change building gameplay, models, animations, or icon imagery.

## Evidence

- `BUILDING_CARTHAGE_BYRSA_ELEPHANT_TREASURY` uses
  `ART_DEF_BUILDING_KRAK_DES_CHEVALIERS`
  (`Assets/XML/Buildings/CIV4BuildingInfos.xml:703-711`).
- That art definition used malformed standalone syntax
  (`Assets/XML/Art/CIV4ArtDefines_Building.xml:3935-3944`).
- All 20 affected live paths resolve to valid local DDS files.
- The installed Byrsa XML and DDS matched the repository copies.
- Existing validation checked only newly introduced art values, allowing an
  older malformed definition to be reused without error
  (`tools/validate_roster_safety.py`).

## Validation

- Run focused validator tests.
- Run `.\tools\test_gate.ps1`.
- Confirm no live building art definition retains a lone-comma button value.
- Install and select the Byrsa Elephant Treasury in a city queue.
- Spot-check other repaired wonders in the Civilopedia or production UI.

## Completion Checklist

- [x] Root cause traced through live building and art definitions.
- [x] All affected live DDS files verified.
- [x] Twenty live standalone button values corrected.
- [x] Reused live art definitions added to validation.
- [x] Automated repository gate passed.
- [ ] Installed Byrsa queue smoke test passed.

## Final Outcome Summary

- The repair removes only the invalid atlas marker from valid standalone DDS
  paths.
- Five focused validator tests passed, the changed-file repository gate passed,
  and the post-change live-reference scan found zero malformed button values.
- Runtime acceptance remains pending until the updated payload is installed
  and the Byrsa Treasury is selected again.
