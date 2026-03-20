# Leaderhead Photo-to-BTS Pipeline

- Status: `in_progress`
- Owner / agent: Symphony Squad – Implementer
- Last updated: `2026-03-19`

## Problem Statement

- Task: Build a repeatable workflow plus repo-side tooling that turns real-person photo references into fully animated Civilization IV: Beyond the Sword leaderheads compatible with DowagerMod.
- Current observed behavior: The repo ships lots of imported leaderheads but no documented or automated path for generating new ones from scratch; adding a new real-person leaderhead is ad-hoc, manual, and not reproducible.
- Why this is a real repo/code problem: Future leaders on the roadmap depend on custom art; without a defined pipeline, the team cannot reliably produce or review new leaderheads, and failures could break diplomacy scenes or crash the game.

## Why This Matters

- User or gameplay impact: Animated leaderheads are a defining UX element; missing or broken leaderheads break immersion and can block new civ content entirely.
- Maintenance / workflow / agent impact: A codified process reduces single-artist dependency, helps agents scope art tasks, and ensures assets land with the correct XML/art wiring and validation.

## Scope

- In scope:
  - Reverse-engineering the required asset stack (NIF/KFM/FGD/texture/button/XML references).
  - Selecting and documenting a modern toolchain (e.g., Blender + Niftools + FaceBuilder/photogrammetry) that outputs compatible Gamebryo assets.
  - Designing repo scripts/templates to organize new leaderhead deliveries and automate validation/packaging where possible.
  - Producing at least one prototype leaderhead package sourced from a real figure photo to prove the pipeline.
  - Updating docs/runbooks so other modders can repeat the workflow.
- In scope:
  - Capturing limitations, manual touchpoints, and testing requirements (XML validation + in-game smoke tests).

## Non-Goals

- Not changing: Core DLL leaderhead logic or diplomacy scene behavior.
- Not changing: Existing vanilla/vended leaderhead assets beyond referencing them as exemplars.

## Trusted Sources Of Truth

- Primary code/config/scripts:
  - `CoreFiles/.../Assets/XML/Art/CIV4ArtDefines_Leaderhead.xml`
  - `CoreFiles/.../Assets/XML/Civilizations/CIV4LeaderHeadInfos.xml`
  - `CoreFiles/.../Assets/Art/Leaderheads/**`
  - `tools/` for packaging/testing
- Runtime entrypoints/import paths to verify:
  - Diplomacy scene art refs in XML
  - Buttons/interface art hooks
- Validation scripts/tests/hooks:
  - `.\tools\test_gate.ps1`
  - Manual diplomacy-scene smoke test per `docs/MANUAL_SMOKE_TESTS.md`

## Existing Docs / Plans Trust Review

- Reviewed docs/plans:
  - `docs/CIV4_UNIT_ART_CRASH_PLAYBOOK.md` – trusted for art validation patterns.
  - `docs/MANUAL_SMOKE_TESTS.md` – trusted for gameplay smoke guidance.
  - `docs/plans/active/2026-03-09-baseline-normalization.md` – context only.
- Conflicts with code/config/scripts: none spotted yet; rely on live XML/art paths.

## Potentially Stale Or Conflicting Materials

- Item: Historical forum tutorials on Civ4 leaderheads.
  - Why it may be stale: Target old 3ds Max + obsolete plugins.
  - What code/config overrode or verified it: Need a Blender-era workflow aligned with repo assets.

## Affected Files / Directories

- Primary implementation paths:
  - `CoreFiles/.../Assets/Art/Leaderheads/**`
  - `CoreFiles/.../Assets/XML/Art/CIV4ArtDefines_Leaderhead.xml`
  - `docs/` (new workflow/readme)
  - `tools/leaderhead_pipeline/**` (new scripts)
- Adjacent paths to inspect:
  - `CoreFiles/.../Assets/Art/interface/Leaderheads`
  - `CoreFiles/.../Assets/Art/Shared` textures/materials
- Paths to avoid unless evidence requires them:
  - Base `Assets` and `Warlords` mirrors
  - `petromod_v1` HUD tree

## Assumptions That Need Human Confirmation

- Assumption: Blender + Niftools (PyNifly or Civ4 FBX to NIF pipeline) is acceptable for repo contributors.
  - Why it matters: Determines tool support we document and script.
  - What changes if false: Need to document 3ds Max pipeline or alternative tooling.
- Assumption: Reusing an existing Firaxis animation skeleton (e.g., Boudica) is acceptable for MVP leaderheads.
  - Why it matters: Avoids building custom KFMs from scratch.
  - What changes if false: Must invest in bespoke animation authoring per leader.

## Proposed Implementation Steps

1. Verify live entrypoints, imports, runtime paths, and active asset roots.
2. Confirm trusted sources and classify stale/conflicting materials in this area.
3. Implement the smallest change that solves the problem.
4. Update related docs/runbooks affected by the change.
5. Validate with repo test gates and required smoke testing.

### Task-Specific Steps

1. Inventory an existing BTS leaderhead (DowagerCountess + vanilla ref) to map required files, textures, and XML hooks.
2. Research and document a Blender-based workflow for generating head mesh + textures from photo refs (FaceBuilder, photogrammetry, or AI-assisted sculpt) and retargeting onto Civ4 rigs.
3. Create repo scaffolding: `tools/leaderhead_pipeline/README.md`, template folders, automation scripts for packaging assets, DDS conversion helpers, and XML stub generator.
4. Produce a prototype leaderhead package (select a historical figure with available photos), showing the configured art tree + XML stub + build log; include instructions for manual animation binding/testing.
5. Update docs (`docs/leaderhead_pipeline.md` + `docs/index.md` entry) and note validation/manual steps; run `.\tools\test_gate.ps1` for XML changes and document pending manual diplomacy smoke test.

## Validation Plan

- Required automated checks:
  - `.\tools\test_gate.ps1`
- Required repo scripts:
  - To be determined (e.g., texture conversion helper tests)
- Required manual smoke test:
  - Install new leaderhead assets, load diplomacy scene, verify animations (document if pending).
- Validation blocked or not yet runnable:
  - Prototype leaderhead in-game validation pending asset completion.

## Documentation Updates Required

- Docs to update with the implementation:
  - New `docs/leaderhead_pipeline.md`
  - `docs/index.md` reference
  - Possibly `README.md` tooling list
- Docs/plans to mark stale, historical, or superseded:
  - Any legacy instructions encountered (TBD)
- `docs/index.md` updates needed:
  - Add the new doc under Engineering / Runbooks
- `ARCHITECTURE.md` / `WORKFLOW.md` / runbook updates needed:
  - Likely none unless new runtime dependencies emerge.

## Risks / Rollback

- Main risks:
  - Toolchain dependency (FaceBuilder license, PyNifly stability)
  - Poor animation quality causing crashes
- Likely failure modes:
  - NIF export incompatible with Civ4 shaders
  - Incorrect texture path causing pink leaderheads
- Safe rollback approach:
  - Remove new art/XML entries and revert doc/tool changes; existing leaderheads unaffected.
- Paths that should not be touched during rollback:
  - Base BtS vanilla leaderheads outside new prototype scope.

## Open Questions

- Question: Which historical figure should serve as the prototype (based on photo availability and licensing)?
- Question: Do we standardize on DDS compression targets per texture map (DXT1 vs DXT5) for pipeline automation?

## Completion Checklist

- [ ] Trusted sources of truth were verified from code/config/scripts.
- [ ] Existing docs/plans in this area were reviewed and classified for trustworthiness.
- [ ] Assumptions needing human confirmation were recorded.
- [ ] Implementation steps were completed or explicitly deferred.
- [ ] Required validation ran and results were recorded.
- [ ] Required manual smoke test ran, or the blocker was escalated.
- [ ] Related docs were updated or explicitly deferred with reason.
- [ ] Residual risks and open questions were summarized.

## Final Outcome Summary

- What changed:
- Validation performed:
- Docs updated:
- Remaining risks:
- Follow-up tasks:
