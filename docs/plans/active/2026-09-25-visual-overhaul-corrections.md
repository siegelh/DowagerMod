# Visual Overhaul Corrections and Mountain Research Campus

- Status: `in_progress`
- Owner / agent: GitHub Copilot
- Last updated: `2026-09-25`

## Problem Statement

- Replace the unsatisfactory Remaster grassland, plains, and desert textures
  without disturbing the accepted mountains, hills, water, routes, or
  improvements.
- Undo the excessive Remaster scale increases applied to 43 building art
  definitions.
- Repair missing pre-Industrial city graphics for Dowager's four American
  civilizations.
- Redesign the Great Scientist Research Campus as a peak-only, unworked BFC
  Research landmark.

## Confirmed Scope

- Worktree:
  `C:\DowagerMod-visual-overhaul`
- Branch:
  `agent-baseline-leader-chatter-sol-leader-update-visual-overhaul`
- Baseline:
  `2abf223e6 Apply Remaster scaling to all unit art`
- Four local commits:
  1. Blue Marble grass/plains/desert terrain.
  2. Restore the 43 pre-Remaster building scales.
  3. Repair `ARTSTYLE_ANGLO_AMERICA` city generation.
  4. Implement the mountain Research Campus.
- Autopilot stops before installation, manual gameplay acceptance, pushing,
  merging, or implementing contiguous farms.

## Blue Marble Terrain

- Source:
  [Blue Marble Terrain v2.0 on GameFront](https://www.gamefront.com/games/civilization-4/file/blue-marble-terrain-v2-0).
- Author: Kai Fiebach.
- Source archive SHA-256:
  `cbb51b62ed27e89f26f5524d44fd2d0650a1abd032132066c0b882a381d07b9f`.
- The installer was not executed. Its embedded BFS resource and `_mod.zip`
  payload were extracted for inspection.
- License recorded by the embedded About text: free non-commercial
  distribution, installation, and use when kept free of charge and
  unmodified; commercial use requires permission.
- Deterministic source, extraction, DDS metadata, destination, and per-file
  hashes are recorded in
  `tools\manifests\blue_marble_terrain_2_0.json`.
- Import exact, unmodified Blue Marble assets only for:
  - `GrassBlend.dds`
  - `GrassDETAIL.dds`
  - `GrassGrids.dds`
  - `PlainsBlend.dds`
  - `PlainsDETAIL.dds`
  - `PlainsGrids.dds`
  - `DesertBlend.dds`
  - `DesertDetail.dds`
  - `DesertGrids.dds`
- Preserve Remaster peaks, hills, coast, ocean, water shaders, snow, tundra,
  forests, rivers, farms, mines, roads, railroads, and UI.
- Record archive source/version/hash and per-file dimensions, compression,
  mipmaps, and SHA-256 in a deterministic manifest.

## Building Scale Correction

- Commit `96b64170d` enlarged exactly 43 building art definitions, primarily
  wonders, shrines, palaces, and the airport.
- Restore only those entries' `fScale` and `fInterfaceScale` values from
  `96b64170d^`.
- Do not change unit scaling, Cultural Citystyles, individual city filler
  scales, or global `CITY_BUILDING_SCALE = 0.33`.

## Anglo-American City Repair

- All four American civilizations use `ARTSTYLE_ANGLO_AMERICA`.
- Remaster defines that style but has no complete generic Ancient through
  Renaissance city art for it.
- Add `ARTSTYLE_ANGLO_AMERICA` to the appropriate European generic city-art
  rules for Ancient through Renaissance.
- Retain its distinctive colonial/Anglo-American Industrial art and existing
  generic Modern/Future coverage.
- Validate coverage by era and city footprint, not merely token existence.

## Mountain Research Campus

- Great Scientists may traverse peaks through their existing
  `bCanMoveImpassable` unit capability.
- Research Campus placement:
  - peak only;
  - owned by the builder;
  - assigned to one of the builder's city BFCs;
  - no resource destruction;
  - same-owner campus minimum plot distance 3.
- Research contribution to the plot's assigned city:
  - base `+5`;
  - `+5` per adjacent peak;
  - `+2` per adjacent hill;
  - no tundra, snow, or jungle components;
  - does not require a citizen to work the peak;
  - enters before city Research modifiers;
  - overlapping cities do not duplicate the benefit.
- Update AI pathfinding/valuation, placement previews, tooltips, Civilopedia
  text, localization, cache refreshes, tests, and the custom DLL.

## Explicit Non-Goals

- No Blue Marble UI, fonts, cursor, interface theme, water, hills, peaks,
  forest art, or installer integration.
- No global city scale change.
- No unit rescaling.
- No Forest Preserve or pasture art change.
- No contiguous-farm implementation.
- No live installation, push, merge, or PR.

## Deferred Contiguous-Farm Prototype

A true connected-farm system is a separate possible project. Civ IV's Plot
L-System has no verified neighbor-improvement condition. A future isolated
prototype would keep the real improvement as `IMPROVEMENT_FARM`, compute a
four-edge neighbor mask, and render one of 16 graphical configurations or
modular connector pieces. It must prove neighbor redraws, fog-of-war safety,
road/river coexistence, pillage/repair transitions, performance, and save
compatibility before broader use.

## Validation Plan

- After each commit:
  - `git diff --check`
  - exact changed-file/type audit
  - targeted XML/art/manifest tests
  - `.\tools\test_gate.ps1` where required
- Cumulative:
  - `.\tools\test_gate.ps1 -CheckDll`
  - `.\tools\test_xml.ps1 -All`
  - terrain manifest reconciliation
  - citystyle era/footprint coverage
  - roster, localization, and art-reference validation
  - four ordered local commits and a clean worktree
- Manual acceptance remains with the user after running:
  `C:\DowagerMod-visual-overhaul\Install DowagerMod.bat`

## Risks and Rollback

- Blue Marble land colors may not transition cleanly into retained Remaster
  hills, tundra, snow, coast, or water. The terrain commit is the rollback
  boundary.
- City L-System omissions can fail silently by era or footprint. A coverage
  audit is required.
- `bCanMoveImpassable` is broad. Validation must prove Great Scientists gain
  peak traversal without water movement or border-rule bypass.
- Peak improvements are outside vanilla assumptions. Placement, renderer,
  AI, city assignment, cache invalidation, help, and save/load behavior all
  require coverage.

## Completion Checklist

- [ ] Blue Marble nine-file land-only terrain committed and reconciled.
- [ ] Exactly 43 building definitions restored to pre-Remaster scales.
- [ ] Anglo-American cities have eligible art in every era.
- [ ] Mountain Research Campus mechanics, AI, help, tests, and DLL complete.
- [ ] Full automated validation passes.
- [ ] Four local commits exist and the worktree is clean.
- [ ] Manual install/gameplay test matrix handed to the user.
