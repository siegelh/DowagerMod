# Remaster Visual Overhaul Phase 3-6

- Status: in progress
- Owner / agent: GitHub Copilot CLI
- Last updated: 2026-09-25

## Problem Statement

- Task: Extend the accepted Remaster terrain prototype with larger buildings,
  larger units, selected unit art, selected effects, pavement-free city
  textures, and Cultural Citystyles.
- Current observed behavior: Terrain, water, improvements, and routes use the
  accepted Remaster layer, while cities, buildings, and units retain Dowager's
  prior presentation.
- Why this is a real repo/code problem: Remaster's city package targets a
  smaller stock civilization roster and replaces global L-System files.
  Dowager has 61 civilizations and custom landmark/improvement L-System rules
  that must survive.

## Scope

- In scope: larger-wonder scale values, larger-unit scale values, selected
  loose unit art, nuclear effects, pavement-free city textures, and Cultural
  Citystyles.
- In scope: automatic, documented city-style assignments for all 61 Dowager
  civilizations.
- In scope: four independent local commits and deterministic import auditing.

## Non-Goals

- Not changing: god rays, cloud fog, additional shaders, interface themes,
  Python, DLL, gameplay, balance, installer behavior, leaderheads, or flags.
- Not changing: Dowager's custom landmarks, improvements, leaders, or
  civilization roster.
- Not pushing, merging, or running the live installer.

## Trusted Sources Of Truth

- Dowager runtime:
  `CoreFiles\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword`
- Remaster source:
  `C:\civ4remaster-reference` at
  `a5e232f30eaae9fa980bc8ddcb2dba50b6321a89`
- Accepted baseline:
  `9a53e661e19ae32d8ecd7d9afb05fe6946e1fe0e`
- Validation:
  `tools\test_gate.ps1` and `tools\test_xml.ps1`

## Existing Docs / Plans Trust Review

- `docs\plans\active\2026-09-25-remaster-visual-overhaul-phase-1-2.md`:
  trusted for the accepted terrain/water/route baseline.
- `docs\MANUAL_SMOKE_TESTS.md`: trusted for installed-game acceptance.
- Remaster README: not useful beyond identifying the project.
- Remaster commit history: useful for separating Cultural Citystyles, larger
  wonders, larger units, effects, and later fixes.

## Implementation

### Commit 1: larger buildings and wonders

- Merge only `fScale` and `fInterfaceScale` from matching Remaster
  `BuildingArtInfo` entries.
- Preserve all Dowager-only entries and all non-scale fields.
- Expected changed set: 43 building art definitions.

### Commit 2: unit presentation

- Merge only `fScale` and `fInterfaceScale` from matching Remaster
  `UnitArtInfo` entries.
- Preserve all Dowager-only entries and all non-scale fields.
- Expected changed set: 224 stock unit art definitions.
- Import selected knight, musketman, modern-worker, gunship, Panzer, and
  Praetorian art.

### Follow-up: universal unit consistency

- After installed testing, the user requested Remaster's scaling treatment
  across every remaining Dowager `UnitArtInfo`.
- Preserve the 224 entries already scaled by Commit 2 so they are not scaled
  twice.
- Apply world `fScale × 0.8` and `fInterfaceScale × 1.25` to all remaining
  unit categories, including civilian, animal, naval, air, missile, custom,
  cultural, and unique art definitions.
- Preserve zero or missing fields. `ART_DEF_UNIT_TERUO_NAKAMURA` has no
  `fScale`, so only its interface scale is changed.
- Record and validate this as a separate local commit.

### Commit 3: selected effects

- The Remaster selection NIF directly references `godrays.tga`; therefore the
  no-god-rays requirement makes the replacement circle unsafe to separate.
  Preserve Dowager's stock selection effect and record the feature as skipped.
- Import the seven-file nuclear explosion effect.
- Import the five current pavement-free city textures.

### Commit 4: Cultural Citystyles

- Import the feature-scoped structures and shared art introduced by the
  Cultural Citystyles merge, using current Remaster file versions.
- Preserve phase 1-2 files and commit-3 pavement files without duplicate
  ownership.
- Merge the additional city art-style declarations into Dowager GlobalTypes.
- Map all 61 Dowager civilizations using the checked-in mapping record.
- Use Remaster's current city L-System because Dowager has no post-import
  modifications to that file.
- Use Remaster's current plot L-System as the citystyle base, then preserve:
  - every Dowager LNode name absent from Remaster;
  - every named Dowager LProduction absent from Remaster;
  - filtered fallback productions for every Dowager improvement token absent
    from Remaster.
- Retain `CITY_BUILDING_SCALE = 0.33`.

## Batch Observability

The import utility logs each feature batch with:

- batch identifier and index;
- input/output file counts and byte sizes;
- start/end timestamps and duration;
- copied, unchanged, skipped, duplicate, and error counts;
- retry count;
- final expected/processed/persisted reconciliation.

## Validation Plan

- After each commit:
  - manifest audit;
  - `git diff --check`;
  - `.\tools\test_gate.ps1`.
- After all commits:
  - `.\tools\test_xml.ps1 -All`;
  - cumulative manifest, scope, mapping, and L-System audit;
  - verify all 61 civilization styles are declared;
  - verify Dowager custom landmark/improvement tokens remain;
  - verify no excluded subsystem changed;
  - verify a clean four-commit worktree.

## Risks / Rollback

- Cultural Citystyles is a global L-System change and carries the highest
  runtime risk.
- Larger wonders may overlap dense cities.
- Larger units may clip formations, transports, or interface previews.
- NIF files can contain packed-stock dependencies not represented as loose
  files.
- Each feature group is an independent rollback commit. Revert the failed
  feature and dependent later commits rather than replacing XML wholesale.

## Manual Acceptance

The user will install from:

`C:\DowagerMod-visual-overhaul\Install DowagerMod.bat`

Test multiple cultures and eras, small/large cities, ordinary buildings and
wonders, custom landmarks, representative units, the nuclear effect, one turn,
and save/reload. Report missing art, city overlap, era-transition problems,
unit clipping, or regressions in the already accepted terrain layer.
