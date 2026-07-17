# Neutral World Wonders v1

- Status: `complete`
- Owner / agent: Copilot
- Last updated: `2026-07-17`

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
  Pergamon Altar, and Sun Tzu's Art of War as permanent improvements.
- Spawn `3/4/5/6/6/6` by world size after starting-plot normalization.
- Activate one nonstacking civilization benefit from current plot ownership.
- Reuse verified art with deterministic eight-angle model rotation.

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

Global placement requires unowned non-peak land, area size at least 20, no city,
feature, improvement, goody, or bonus, plot distance at least 6 from starts,
and at least 8 from another neutral wonder. Hard thematic requirements are
never silently relaxed.

Add visible default-on `GAMEOPTION_NEUTRAL_WORLD_WONDERS`; explicitly preserve
that default after multiplayer lobby initialization clears options. Skip
WorldBuilder/scenario maps and consume no spawn RNG when disabled.

Sub-Standard maps use synchronized map RNG to vary the attempted candidate
subset. Candidate plots use stable plot-index iteration and deterministic
integer scoring. Per-wonder logs and an expected/attempted/spawned/skipped/
duplicate/error reconciliation summary are required.

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
- Safe rollback: revert local feature commits; do not alter the parent branch.

## Completion Checklist

- [x] Trusted sources and live entrypoints identified.
- [x] Human design decisions recorded.
- [x] Data, art, spawn, effects, UI, and AI implemented.
- [x] Automated validation passes.
- [x] Independent reviews pass.
- [x] Logical local commits created without remote changes.
- [ ] Manual installed acceptance completed by the user.

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
