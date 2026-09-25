# Remaster Visual Overhaul Phase 1-2

- Status: complete
- Owner / agent: GitHub Copilot CLI
- Last updated: 2026-09-25

## Problem Statement

- Task: Integrate the terrain, water, farm, mine, watermill, road, and railroad
  visuals from the authorized `C:\civ4remaster-reference` checkout.
- Current observed behavior: DowagerMod uses its current stock-derived terrain,
  water shader, improvements, and route presentation.
- Why this is a real repo/code problem: A direct Remaster overlay would replace
  Dowager XML, Python, shaders, and DLL content that has diverged substantially.
  The visual layer must be imported surgically.

## Why This Matters

- User or gameplay impact: This creates the first installable prototype of a
  coherent visual overhaul while preserving Dowager gameplay.
- Maintenance / workflow / agent impact: A deterministic import manifest keeps
  binary provenance, scope, and rollback auditable.

## Scope

- In scope: terrain blend/detail/grid textures, water texture and water shader,
  farm crops, modern mine, watermill, modern roads, railroads, and crossings.
- In scope: surgical `CIV4RouteModelInfos.xml` late-road model changes.

## Non-Goals

- Not changing: cloud fog, non-water shaders, UI, city styles, Python, DLL,
  units, leaderheads, buildings, gameplay rules, or installer behavior.
- Not changing: Dowager's Plot L-System, custom improvement definitions,
  landmarks, or intentional `CITY_BUILDING_SCALE = 0.33`.

## Trusted Sources Of Truth

- Primary code/config/scripts:
  - `CoreFiles\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword`
  - `CoreFiles\install.py`
  - `tools\manifests\remaster_visual_overhaul_phase_1_2.json`
- Runtime entrypoints/import paths to verify:
  - `Beyond the Sword\Assets\Art`
  - `Beyond the Sword\Assets\XML\Art\CIV4RouteModelInfos.xml`
  - `Beyond the Sword\Shaders\FX\Water.fx`
  - `Beyond the Sword\Shaders\FXO\Water.fx`
- Validation scripts/tests/hooks:
  - `tools\test_gate.ps1`
  - `tools\test_xml.ps1`

## Existing Docs / Plans Trust Review

- `INSTALLER.md`: trusted for this task; confirms pristine restore plus payload
  overlay.
- `docs\TESTING_WORKFLOW.md`: trusted for automated validation.
- `docs\MANUAL_SMOKE_TESTS.md`: trusted for installed-game art validation.
- Remaster `README.md`: not useful; it contains only the project title.
- Remaster commit history: useful context and the strongest available record of
  which assets implement each visual feature.

## Potentially Stale Or Conflicting Materials

- Remaster `CIV4DetailManager.xml`:
  - It would reduce Dowager's city-building scale from `0.33` to `0.224`.
  - It is excluded because the difference is unrelated to the scoped
    improvement art.
- Remaster `CIV4PlotLSystem.xml`:
  - It contains thousands of Cultural Citystyles changes.
  - Dowager already has the required modern-mine and watermill references, so
    the Remaster file is not imported.

## Affected Files / Directories

- Primary implementation paths:
  - `Beyond the Sword\Assets\Art\Terrain`
  - `Beyond the Sword\Assets\Art\structures\improvements`
  - `Beyond the Sword\Assets\XML\Art\CIV4RouteModelInfos.xml`
  - `Beyond the Sword\Shaders\FX\Water.fx`
  - `Beyond the Sword\Shaders\FXO\Water.fx`
  - `tools\baselines\packed_stock_art.json`
- Adjacent paths to inspect:
  - `Beyond the Sword\Assets\XML\Buildings\CIV4PlotLSystem.xml`
  - inherited route models already present in the BtS mirror
- Paths to avoid unless evidence requires them:
  - Python, DLL, Resource themes, city L-Systems, unit art, and every non-water
    shader

## Assumptions That Need Human Confirmation

- Asset authorization:
  - Confirmed by the user before implementation.
- Visual acceptance:
  - The user will install from the new worktree and decide whether the result
    is aesthetically acceptable.

## Proposed Implementation Steps

1. Import the manifest-listed terrain and water files byte-for-byte.
2. Import the matching water shader source and compiled runtime shader.
3. Import focused farm, mine, and watermill files, including the textures
   directly referenced by the Remaster watermill NIF, without replacing
   Dowager L-System or detail-manager XML.
4. Import route and crossing assets and merge only Remaster's late-road model
   path changes.
   - Register the stock `Modern Roads\RailroadD02.nif` parent model in the
     packed-stock baseline because it is supplied by Firaxis FPK archives
     rather than as a loose file.
5. Audit hashes, excluded paths, and route model resolution.
6. Run the changed-file gate and full XML validation.
7. Stop for installed-game visual testing before tuning, commit, or push.

## Validation Plan

- Required automated checks:
  - every manifest source and destination exists
  - source/destination SHA-256 values match
  - no excluded Remaster subsystem is present in the diff
  - route model references resolve against the complete game mirror
  - `git diff --check`
- Required repo scripts:
  - `.\tools\test_gate.ps1`
  - `.\tools\test_xml.ps1 -All`
- Required manual smoke test:
  - run `C:\DowagerMod-visual-overhaul\Install DowagerMod.bat`
  - launch the game and reach the main menu without errors
  - inspect terrain, coasts, water, fog boundaries, farms, mines, watermills,
    roads, railroads, crossings, and bridges
  - test grid on/off, close/strategic zoom, one turn, and save/reload
- Validation blocked or not yet runnable:
  - Aesthetic and GPU-specific shader acceptance requires the user's installed
    game.

## Documentation Updates Required

- This active plan and the import manifest are sufficient for the prototype.
- No architecture or installer documentation changes are expected because the
  runtime and deployment model are unchanged.

## Risks / Rollback

- Main risks: DDS readability, missing NIF dependencies, route junction seams,
  and GPU-specific `ps_2_0` water rendering.
- Likely failure modes: pink/black assets, broken route crossings, invisible
  water under unexpected fog values, or excessive terrain shimmer.
- Safe rollback approach: reinstall from the original Dowager worktree, or
  discard this branch's scoped changes.
- Paths that should not be touched during rollback: unrelated user worktrees,
  the pristine game snapshot, and Dowager custom XML outside this plan.

## Open Questions

- Does the selected terrain palette preserve resource and border readability?
- Does the Remaster water shader behave correctly on the user's GPU?

## Completion Checklist

- [x] Trusted sources of truth were verified from code/config/scripts.
- [x] Existing docs/plans in this area were reviewed and classified.
- [x] Assumptions needing human confirmation were recorded and answered.
- [x] Implementation steps were completed.
- [x] Required automated validation ran and results were recorded.
- [x] Required manual smoke test remains explicitly assigned to the user.
- [x] Related docs were updated or explicitly deferred.
- [x] Residual risks and open questions were summarized.

## Final Outcome Summary

- What changed: Imported 52 manifest-pinned Remaster files for terrain, water,
  farms, mines, watermills, roads, railroads, and crossings; merged all 70
  late-road model references; registered the Firaxis FPK-only
  `Modern Roads\RailroadD02.nif` parent in the packed-stock baseline.
- Validation performed:
  - manifest SHA-256 and scope audit passed (`52` source/destination files,
    `56` changed files total, no excluded subsystem)
  - `git diff --check` passed
  - `.\tools\test_gate.ps1` passed
  - `.\tools\test_xml.ps1 -All` passed, with the seven known unresolved stock
    schema references warning-skipped
- Docs updated: This plan and the deterministic import manifest.
- Remaining risks: Installed-game aesthetic, animation, crossing, and
  GPU-specific water-shader validation.
- Follow-up tasks: Install from this worktree, capture findings/screenshots,
  and decide whether tuning or rollback is needed before commit.
