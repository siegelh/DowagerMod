# Neutral World Wonders v1

- Status: `complete`
- Owner / agent: Copilot
- Last updated: `2026-07-17` (expanded to 14 wonders)

## Problem Statement

- Task: Add a deterministic prototype of capturable neutral world wonders.
- Current observed behavior: The repository contains usable wonder art and
  unobtainable placeholder buildings, but no neutral map-wonder system.
- Why this is a real repo/code problem: The feature crosses map initialization,
  XML data, native ownership effects, art routing, AI valuation, and UI help.

## Why This Matters

- User or gameplay impact: Exploration and territorial expansion gain a small
  set of visually distinctive, contested objectives.
- Maintenance / workflow / agent impact: The prototype must remain save-safe,
  multiplayer-deterministic, observable, and isolated for runtime testing.

## Scope

- Add Great Sphinx, Library of Nineveh, Terracotta Army, Tomb of Cyrus,
  Pergamon Altar, and Sun Tzu's Art of War as permanent improvements
  (original 6).
- Expansion (append-only, final 14 XML entries): add Ishtar Gate, Great
  Ziggurat of Ur, Ekur of Nippur, Temple of Thoth, Temple of Melqart,
  Erechtheum, Labyrinth of Knossos, and Solomon's Temple as permanent
  improvements 7-14, reusing the exact same eight-angle rotation hub and
  spawn/AI/UI machinery as the original 6.
- Spawn `3/4/5/6/6/6` by world size after starting-plot normalization, drawn
  as a Fisher-Yates shuffled random subset of the full 14-wonder pool on
  every generated map (no longer sub-Standard only).
- Activate one nonstacking civilization benefit from current plot ownership.
- Reuse verified art with deterministic eight-angle model rotation.
- Attribute each active neutral-wonder-derived benefit (culture, research,
  civic upkeep, great-person rate, military production, land-unit XP) back
  to its specific named wonder in the relevant help/pedia text, with
  distinct active wonders stacking as separate lines and duplicate copies of
  the same wonder collapsing into one line.

## Non-Goals

- Do not change or remove the existing unobtainable BuildingInfos.
- Do not add restoration, special war targeting, persistent save fields, or
  scenario auto-placement.
- Do not install, merge, push, or remove the local branch/worktree.

## Trusted Sources Of Truth

- DLL: `third_party/beyond-the-sword-sdk/CvGameCoreDLL`.
- XML: `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML`.
- Spawn entrypoint: `CvGame::setInitialItems()`.
- Ownership transfer: `CvPlot::setOwner()` improvement-count bookkeeping.
- Validation: `tools/test_gate.ps1`, `tools/test_xml.ps1`, `tools/tests`.

## Existing Docs / Plans Trust Review

- `AGENTS.md`, `WORKFLOW.md`, and `docs/TESTING_WORKFLOW.md`: trusted.
- Session discovery report and prior wonder inventory: useful context; verify
  every implementation detail against current files.
- Unobtainable BuildingInfos: art reference source only, not behavior truth.

## Affected Files / Directories

- Primary: terrain/game-option/art/text XML, PlotLSystem, `CvGame`,
  `CvPlot`, `CvPlayer`, `CvCity`, `CvUnit`, help/AI code, and focused tests.
- Adjacent: enum/Python exposure, XML cache serialization, manual smoke docs.
- Avoid: base/Warlords compatibility trees, generated `dist`, and legacy tools.

## Locked Design

| Wonder | Placement | Tile yield | Owned benefit |
|---|---|---:|---|
| Great Sphinx | Flat Desert; favor river/floodplain proximity | +2 Commerce | +10% city Culture |
| Library of Nineveh | Riverside flat Grass/Plains/Desert | +2 Commerce | +10% Research |
| Terracotta Army | Grass/Plains hill or flat; favor hills | +2 Production | +1 XP to new land combat units |
| Tomb of Cyrus | Inland Desert/Plains hill or flat | +1 Production, +1 Commerce | -10% Civic Upkeep |
| Pergamon Altar | Grass/Plains hill; favor coast | +2 Commerce | +10% Great Person rate |
| Sun Tzu's Art of War | Grass/Plains hill; favor Forest/Hills | +2 Production | +10% military-unit Production |
| Ishtar Gate | Flat Desert/Plains; riverside required | +2 Commerce (+10 Culture) | +10% city Culture |
| Great Ziggurat of Ur | Flat Desert/Plains; riverside required | +1 Production, +1 Commerce | -10% Civic Upkeep |
| Ekur of Nippur | Flat Desert/Plains; inland required | +2 Production | +10% military-unit Production |
| Temple of Thoth | Flat Desert/Plains; riverside required | +2 Commerce (+10 Research) | +10% Research |
| Temple of Melqart | Flat Grass/Plains/Desert; coastal required | +2 Production | +1 XP to new land combat units |
| Erechtheum | Grass/Plains hill | +2 Commerce (+10 GPP) | +10% Great Person rate |
| Labyrinth of Knossos | Grass/Plains, hill or flat; coastal preferred | +1 Production, +1 Commerce | -10% Civic Upkeep |
| Solomon's Temple | Grass/Plains hill; inland preferred | +2 Commerce (+10 GPP) | +10% Great Person rate |

Global placement requires unowned non-peak land, area size at least 20, no city,
feature, improvement, goody, or bonus, plot distance at least 6 from starts,
and at least 8 from another neutral wonder. Hard thematic requirements are
never silently relaxed.

Add visible default-on `GAMEOPTION_NEUTRAL_WORLD_WONDERS`; explicitly preserve
that default after multiplayer lobby initialization clears options. Skip
WorldBuilder/scenario maps and consume no spawn RNG when disabled.

Every generated map (all world sizes, not just sub-Standard) uses the
synchronized map RNG to Fisher-Yates shuffle the full 14-wonder pool once,
then selects the first world-size-appropriate count from that shuffled order
without replacement. Candidate plots use stable plot-index iteration and
deterministic integer scoring. Per-wonder logs and an expected/attempted/
spawned/skipped/duplicate/error reconciliation summary are required.

## Proposed Implementation Steps

1. Append option, schema/cache metadata, six improvements, text, and art.
2. Add exclusive eight-angle PlotLSystem routes using one original model.
3. Implement native deterministic placement after normalized starts.
4. Derive bonuses from cached owned improvement counts without map scans or
   new save fields.
5. Add ownership notifications/help, AI founding value, and protections.
6. Add focused contracts, docs, and resolve independent review findings.
7. Create logical local commits only.

## Validation Plan

- `python -m pytest tools\tests -q`
- `.\tools\test_gate.ps1 -CheckDll`
- `.\tools\test_xml.ps1 -All`
- `git diff --check`
- Compare built and payload DLL SHA256.
- Manual acceptance remains blocked until the user installs: generated-map
  counts, option/scenario behavior, scale/rotation, capture/loss, exact effects,
  AI, save/reload, and two-client multiplayer/OOS.

## Risks / Rollback

- Main risks: enum/cache mismatch, map RNG desync, excessive or missing spawn
  candidates, stale derived modifiers, and unusable model scale/pivot.
- Expansion-specific risk: the 8 new wonders' `fScale` values (art def) were
  chosen conservatively but not verified in-engine; visual scale/pivot for
  each new NIF may need in-game tuning.
- Safe rollback: revert local feature commits; do not alter the parent branch.

## Completion Checklist

- [x] Trusted sources and live entrypoints identified.
- [x] Human design decisions recorded.
- [x] Data, art, spawn, effects, UI, and AI implemented.
- [x] Automated validation passes (original 6-wonder scope).
- [x] Independent reviews pass.
- [x] Logical local commits created without remote changes.
- [ ] Manual installed acceptance completed by the user.
- [x] Expansion: 8 additional wonders (14 total) implemented end-to-end.
- [x] Expansion: focused `tools/tests/test_neutral_world_wonders.py` and
      `tools/tests/test_great_person_landmarks.py` pass (77 passed).
- [ ] Expansion: full DLL/XML gate run (deferred to parent process).
- [ ] Expansion: manual installed acceptance for the 8 new wonders.

## Final Outcome Summary

- What changed: Six permanent capturable neutral wonders, deterministic
  generated-map placement, ownership-derived benefits, rotation art, UI, AI,
  logging, and contracts are implemented locally.
- Validation performed: 258 repository tests passed (10 skipped); 66 focused
  neutral/landmark contracts passed; full XML validation and
  `test_gate.ps1 -CheckDll` passed; built/payload DLL SHA256 values match.
- Docs updated: This plan and `docs/MANUAL_SMOKE_TESTS.md`.
- Remaining risks: Installed visual/gameplay/save/AI/multiplayer acceptance.
- Local-only delivery: implementation commit `c0e847c2f`; no remote push.

## Expansion Outcome Summary (8 additional wonders, 6 -> 14 total)

- What changed: Appended 8 new permanent neutral world wonders (Ishtar Gate,
  Great Ziggurat of Ur, Ekur of Nippur, Temple of Thoth, Temple of Melqart,
  Erechtheum, Labyrinth of Knossos, Solomon's Temple) as the final 14 XML
  `ImprovementInfo` entries, plus matching `ImprovementArtInfo`, PlotLSystem
  rotation/route entries, and game text (option help, source-attribution
  keys, name/help/pedia). `CvGame.cpp` now shuffles the full 14-wonder pool
  with the synchronized map RNG on every generated map (the previous
  below-Standard-only gate was removed) and selects the first world-size
  count without replacement; profile-matching and theme-score hooks were
  extended for wonder indices 6-13. `CvGameTextMgr.cpp` gained a reusable,
  read-only helper (`appendActiveNeutralWorldWonderLines`) that enumerates
  owned neutral-wonder ImprovementInfos and appends one named line per
  active nonzero effect; it is wired into commerce (culture/research), great
  person rate, military production (split from the existing aggregate),
  civic upkeep (raw signed percent, no `abs()`), and land-unit XP help,
  fixing the pre-existing silent assert mismatches in the commerce/GPP help
  by including the named-source aggregate in the reconciled modifier total.
- Design decisions: Great Ziggurat of Ur's button uses the existing
  `mesopotamia/ziggurat.dds` (the requested `temple_nanna.dds` button does
  not exist); Temple of Melqart's button uses the existing
  `canaanism/temple.dds` (no Melqart-specific button exists). All 8 new
  `fScale` values are conservative estimates, not verified in-engine.
- Validation performed (this expansion, in-agent): XML well-formedness for
  all 4 edited XML files; focused
  `pytest tools/tests/test_neutral_world_wonders.py tools/tests/test_great_person_landmarks.py`
  — 77 passed. The C++ changes were reviewed for type/signature correctness
  but **not compiled** in this session; `test_gate.ps1`/`test_xml.ps1`/a full
  DLL build were intentionally deferred to the parent process per task
  instructions.
- Remaining risks: DLL compile has not been verified in-agent; new art
  scale/pivot correctness is unverified in-engine; installed
  visual/gameplay/save/AI/multiplayer acceptance for the 8 new wonders is
  still pending.
