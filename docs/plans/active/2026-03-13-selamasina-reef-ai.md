# Selamasina Reef Works AI

- Status: `in_progress`
- Owner / agent: Symphony Squad - Implementer
- Last updated: `2026-03-13`

## Problem Statement

- Task: Improve Selamasina/Polynesia AI so it actually trains Wayfinder Canoes and repeatedly uses their unique "Build Reef Works" action.
- Current observed behavior: `CvCityAI::AI_neededSeaWorkers()` only counts unimproved seafood bonuses, so cities stop training sea workers once resources are netted. `CvUnitAI::AI_workerSeaMove()` only runs `AI_improveBonus`, so Polynesian work boats never consider Reef Works tiles even if the build is available.
- Why this is a real repo/code problem: Selamasina's signature mechanic depends on Reef Works, but AI code paths still match vanilla BTS expectations (sea workers exist only to net bonus tiles). As a result the new leader's advantage is invisible to AI opponents.

## Why This Matters

- User or gameplay impact: Selamasina's AI plays poorly, failing to exploit her unique infrastructure so human players see no challenge or flavor from facing her civ.
- Maintenance / workflow / agent impact: Without AI hooks, future balance work cannot rely on Reef Works being present in AI games.

## Scope

- In scope: DLL AI logic for sea-worker demand (`CvCityAI`) and work boat behavior (`CvUnitAI`).
- In scope: Supporting helper logic to evaluate Reef Works targets via existing city best-build scoring.

## Non-Goals

- Not changing: Base XML stats for Reef Works, Wayfinder Canoes, or Selamasina's trait.
- Not changing: Human work boat automation beyond reusing existing city best-build logic.

## Trusted Sources Of Truth

- Primary code/config/scripts: `CvUnitAI.cpp`, `CvUnitAI.h`, `CvCityAI.cpp`.
- Runtime entrypoints/import paths to verify: `CvUnitAI::AI_workerSeaMove`, `CvCityAI::AI_neededSeaWorkers`, `CvCityAI::AI_bestBuild`/`AI_getBestBuildValue`.
- Validation scripts/tests/hooks: `.	ools\test_gate.ps1` (covers DLL changes).

## Existing Docs / Plans Trust Review

- Reviewed docs/plans: `README.md`, `AGENTS.md`, `WORKFLOW.md`, `ARCHITECTURE.md`, `docs/index.md`, `docs/TESTING_WORKFLOW.md`, `docs/MANUAL_SMOKE_TESTS.md`.
- Classification: all `trusted for this task` (overview + workflow/runbook references already corroborated by code reading).
- Conflicts with code/config/scripts: none identified for this area.

## Potentially Stale Or Conflicting Materials

- Item: vanilla BTS AI expectation that sea workers only improve resources.
  - Why stale: DowagerMod adds a reusable non-bonus sea improvement.
  - Override: Live XML + issue demonstrate new mechanic; code must follow suit.

## Affected Files / Directories

- Primary implementation paths: `third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvUnitAI.cpp`, `.h`, and `CvCityAI.cpp`.
- Adjacent paths: `CvGameTextMgr.cpp` (already reports needed sea workers; verify no extra wiring required), project build scripts.
- Paths to avoid unless evidence requires: XML asset trees, Python UI/event code.

## Assumptions That Need Human Confirmation

- Assumption: Only Polynesia (Selamasina's civ) can train Wayfinder Canoes / Reef Works, so targeting logic can gate on owning the special build.
  - Why it matters: prevents other civs from chasing nonexistent builds.
  - What changes if false: would need broader capability detection (e.g., via promotions or events) before queuing Reef Works.
- Assumption: City best-build data already ranks Reef Works opportunistically when beneficial.
  - Why it matters: new AI hook can reuse existing scoring instead of inventing another heuristic.
  - What changes if false: would have to craft a custom valuation specific to Reef Works yields.

## Proposed Implementation Steps

1. Verify live paths (`CvUnitAI::AI_workerSeaMove`, `CvCityAI::AI_neededSeaWorkers`) and confirm no existing hook references Reef Works.
2. Add a helper-driven Reef Works job finder to `CvUnitAI` and call it once bonus improvements are exhausted, so eligible Polynesian work boats chase the best city-requested Reef Works tile.
3. Extend `CvCityAI::AI_neededSeaWorkers` to count Reef Works targets in its demand figure (e.g., based on plots whose best build is Reef Works), ensuring Polynesian cities keep a standing Wayfinder force.
4. Wire declarations in `CvUnitAI.h`, and keep logic gated so other civs are unaffected.
5. Run `.	ools\test_gate.ps1` (covers DLL build) and document manual smoke-test expectations since gameplay behavior changed.

### Task-Specific Steps

1. Introduce a cached `BuildTypes` lookup helper (or inline static) for `BUILD_POLYNESIA_REEF_WORKS_BTG` in both `CvUnitAI` and `CvCityAI` to avoid repeated string parsing.
2. Implement `CvUnitAI::AI_buildReefWorks`:
   - Iterate owner cities, reuse `AI_getBestBuild` / `AI_getBestBuildValue` to find plots that specifically request Reef Works.
   - Score candidate plots (worked tiles, shorter paths) and push move/build missions when found.
3. Update `AI_workerSeaMove` to invoke the new function before giving up when no bonuses remain.
4. Enhance `CvCityAI::AI_neededSeaWorkers` by summing Reef Works targets (city plots desiring that build) and translating that into additional worker demand (including safety cap / divisor so 1–2 boats maintain multiple improvements).
5. Add any necessary header declarations and ensure existing demand text (e.g., `CvGameTextMgr`) naturally picks up the new counts.
6. Run DLL gate + outline manual smoke plan in final summary.

## Validation Plan

- Required automated checks: `.	ools\test_gate.ps1`.
- Required repo scripts: `.	ools\test_gate.ps1` (covers XML schema + DLL build due to code changes).
- Required manual smoke test: Polynesia AI scenario (document expectation; execution left for humans per workflow).
- Validation blocked or not yet runnable: manual gameplay validation (blocked until human run per process).

## Documentation Updates Required

- Update plan-only (this file). No runtime doc deltas anticipated unless mismatch discovered. `ARCHITECTURE.md`/`docs/index.md` remain accurate.

## Risks / Rollback

- Main risks: Work boats over-prioritize Reef Works, starving seafood repairs; pathfinding loops if no reachable target.
- Likely failure modes: `AI_neededSeaWorkers` miscounts leading to runaway boat spam, or `AI_buildReefWorks` tries to build on occupied/resource tiles.
- Safe rollback: Revert DLL changes (`CvUnitAI`/`CvCityAI`) and rebuild.

## Open Questions

- None right now.

## Completion Checklist

- [ ] Trusted sources verified.
- [ ] Docs classified.
- [ ] Assumptions logged.
- [ ] Implementation complete.
- [ ] `test_gate.ps1` run.
- [ ] Manual smoke expectations noted.
- [ ] Docs updated/deferred noted.
- [ ] Residual risks captured.

## Final Outcome Summary

- What changed: _TBD_
- Validation performed: _TBD_
- Docs updated: plan doc only.
- Remaining risks: _TBD_
- Follow-up tasks: _TBD_
