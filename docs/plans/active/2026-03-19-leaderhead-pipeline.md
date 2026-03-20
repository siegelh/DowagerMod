# Photo-to-Leaderhead Production Pipeline

- Status: `blocked`
- Owner / agent: Symphony Squad — Implementer
- Last updated: `2026-03-19`

## Problem Statement

- Task: Build a complete, repeatable workflow that ingests real-world reference photos and outputs a fully functional Civilization IV: Beyond the Sword leaderhead, including Blender source assets, exported meshes/textures/animations, and XML integration.
- Current observed behavior: The repo contains historical/custom leaderhead assets (e.g., `CoreFiles/.../Assets/Art/Leaderheads/DowagerCountess/`, `.../Leaderheads/new/*`) plus scattered Blender files, but there is no documented or automated workflow that starts from photographs and ends with validated, in-game leaderheads. Mandatory creation tools (Blender with Civ4 NIF import/export support) are not present on this workstation.
- Why this is a real repo/code problem: Without a proven production path, new DowagerMod leaders cannot be authored. Issue #58 explicitly requires an implemented pipeline and an end-to-end prototype, not just planning or folder scaffolding.

## Why This Matters

- User or gameplay impact: No new leaders can be added even if design work exists; artists lack a supported method to contribute assets.
- Maintenance / workflow / agent impact: Symphony cannot deliver future leaderhead issues because core dependencies (Blender toolchain, exporter scripts, validation steps) are undefined or unavailable, so this remains a blocking capability gap.

## Scope

- In scope:
  - Reverse-engineer current Civ4 leaderhead asset expectations (NIF/KFM hierarchy, texture maps, XML hooks).
  - Define and implement a Blender-based authoring/export workflow with repeatable inputs/outputs under version control.
  - Produce at least one prototype leaderhead (photo reference → Blender source → exported NIF/KFM/texture → XML hookup → in-game validation).
  - Document the workflow, manual vs automated steps, and repository layout for both reusable templates and per-leader deliverables.
- Out of scope (for this issue):
  - Non-leader art systems (units, buildings, UI) beyond what is needed to test the new leaderhead.
  - Reworking the Civ4 HUD (`petromod_v1`) or unrelated art install scripts.

## Non-Goals

- Not changing: Existing working leaderheads or their art defines unless needed for the prototype comparison.
- Not changing: Installer behavior beyond ensuring new art assets are packaged.

## Trusted Sources Of Truth

- Primary code/config/scripts:
  - `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/Art/Leaderheads/`
  - `CoreFiles/.../Assets/XML/Art/CIV4ArtDefines_Leaderhead.xml`
  - `CoreFiles/.../Assets/XML/Civilizations/CIV4LeaderHeadInfos.xml`
  - `CoreFiles/.../Assets/XML/Art/CIV4ArtDefines_Misc.xml` (for buttons/backgrounds)
  - Existing leaderhead assets under `Assets/Art/Leaderheads/new/` for reference rigs/textures.
- Runtime entrypoints/import paths to verify:
  - Art defines referenced via `CIV4ArtDefines_Leaderhead.xml`
  - Diplomacy scene usage through `LeaderHeadInfos`.
- Validation scripts/tests/hooks:
  - `.\tools\test_gate.ps1` (XML validation)
  - Manual smoke tests per `docs/MANUAL_SMOKE_TESTS.md` once assets exist.

## Existing Docs / Plans Trust Review

- Reviewed docs/plans:
  - `docs/ARCHITECTURE.md` → `trusted for this task`.
  - `docs/CIV4_UNIT_ART_CRASH_PLAYBOOK.md` → `useful context only` (covers art crash triage but not leaderhead production).
  - Historical readmes bundled with imported leaderheads (`Assets/Art/Leaderheads/new/*/ReadMe.txt`) → `historical / verify before relying`.
- Conflicts with code/config/scripts: None yet, but no doc explains a working Blender export path.

## Potentially Stale Or Conflicting Materials

- Bundled third-party leaderhead readmes:
  - Why stale: Reference external workflows (Poser, Atlantica Online conversions) not reproducible here.
  - Code override: Only final NIF/DDS assets are wired into XML; readmes give no guarantee about repeatable source files.
- Legacy art planning docs:
  - Why stale: Focus on Dowager baseline normalization rather than new-leader production.
  - Code override: Current repo lacks any scripts matching those docs.

## Affected Files / Directories

- Primary implementation paths:
  - `CoreFiles/.../Assets/Art/Leaderheads/<PrototypeLeader>/` (source + exported assets)
  - `CoreFiles/.../Assets/XML/Art/CIV4ArtDefines_Leaderhead.xml`
  - `CoreFiles/.../Assets/XML/Civilizations/CIV4LeaderHeadInfos.xml`
  - Potential shared Blender template path under `tools/leaderhead_pipeline/` (new).
- Adjacent paths to inspect:
  - `CoreFiles/.../Assets/Art/shared/` for textures/backgrounds.
  - `CoreFiles/.../Assets/Art/Leaderheads/new/*` for reusable rigs.
- Paths to avoid unless evidence requires them:
  - `CoreFiles/.../Assets/Warlords/...` (legacy root)
  - `CoreFiles/dist`, `tmp`

## Assumptions That Need Human Confirmation

- Assumption: It is acceptable to commit large binary Blender `.blend` files plus exported `.nif/.kfm/.dds` artifacts to the repo.
  - Why it matters: Determines whether the pipeline can be version-controlled end-to-end.
  - What changes if false: Need alternate storage or Git LFS before proceeding.
- Assumption: Either Blender 2.79 + Civ4 NIF scripts or another supported toolchain can be installed on the Symphony worker.
  - Why it matters: Without Blender plus NIF exporter, no assets can be produced.
  - What changes if false: Task cannot proceed; requires human-provided environment or pre-generated assets.
- Assumption: A target historical figure (name + reference photos) will be provided or approved.
  - Why it matters: Prototype cannot be completed until a real subject is picked.
  - What changes if false: Need direction before modeling.

## Proposed Implementation Steps

1. Verify live entrypoints, imports, runtime paths, and active asset roots.
2. Confirm trusted sources and classify stale/conflicting materials in this area.
3. Implement the smallest change that solves the problem.
4. Update related docs/runbooks affected by the change.
5. Validate with repo test gates and required smoke testing.

### Task-Specific Steps

1. Reverse-engineer an existing functional leaderhead (e.g., DowagerCountess) to document required asset files, folder structure, XML hooks, and animation references; capture this in a pipeline doc.
2. Stand up the Blender-based production workspace:
   - Install Blender + required Civ4 NIF scripts.
   - Create a repo-tracked base `.blend` template with rig, material slots, export collections, and annotation layers describing manual steps.
3. Produce the prototype leaderhead:
   - Import/reference photo set, sculpt/retopology, UV unwrap, bake textures, create materials.
   - Rig/skin to Civ4-compatible armature, retarget or adapt animation actions, and ensure export settings match NIF requirements.
   - Export `.nif/.kfm`, bake textures to `.dds`, and place outputs under `Assets/Art/Leaderheads/<Prototype>/`.
4. Wire the prototype into gameplay:
   - Add art define entries (leaderhead, buttons, scenes) and update `CIV4LeaderHeadInfos.xml` to reference them.
   - Create a minimal mod config (new leader or scenario) showcasing the leaderhead.
5. Validate:
   - Run `.\tools\test_gate.ps1`.
   - Install assets into a local BTS build, launch the mod, and confirm the leaderhead loads/animates in diplomacy.
6. Generalize & document:
   - Author a `docs/ART_LEADERHEAD_PIPELINE.md` runbook describing inputs, manual vs automated steps, and repository layout.

## Validation Plan

- Required automated checks:
  - `.\tools\test_gate.ps1` (covers XML references to the new leaderhead assets).
- Required repo scripts:
  - `.\tools\test_gate.ps1`
- Required manual smoke test:
  - install or copy updated files into the live game tree
  - launch the mod and confirm it reaches the main menu without XML/Python popups
  - start a single-player game, open diplomacy with the new leaderhead, and observe idle/animation cycles
  - end one turn
  - save and reload once to ensure art references persist
- Validation blocked or not yet runnable:
  - Blocked immediately because no Blender/NIF export toolchain exists on this environment; therefore no new leaderhead assets can be produced or smoke-tested.

## Documentation Updates Required

- Docs to update with the implementation:
  - New pipeline doc (`docs/ART_LEADERHEAD_PIPELINE.md` or similar).
  - `docs/index.md` to reference the new doc.
  - Possibly `ARCHITECTURE.md` (art pipeline section) once implemented.
- Docs/plans to mark stale, historical, or superseded:
  - Any interim notes once the pipeline exists.
- `docs/index.md` updates needed:
  - Add the pipeline doc under “Engineering / Runbooks”.
- `ARCHITECTURE.md` / `WORKFLOW.md` / runbook updates needed:
  - Note the new art production flow when live.

## Risks / Rollback

- Main risks:
  - Large binary assets bloat the repo without Git LFS.
  - Toolchain mismatch (Blender version vs Civ4 NIF exporter) causing unusable exports.
  - Incomplete rigging leading to animation glitches or crashes.
- Likely failure modes:
  - Exported NIFs crash the game due to bad skeleton references.
  - Textures fail to load (pink leaderhead) because of incorrect pathing.
  - Manual steps become unrepeatable if the workstation environment differs.
- Safe rollback approach:
  - Remove new leaderhead art directories and revert XML references.
  - Drop the Blender source files if they prove unusable.
- Paths that should not be touched during rollback:
  - Existing stock leaderheads, `petromod_v1`, non-art assets.

## Open Questions

- Which historical leader should serve as the first fully produced prototype (photo set availability, likeness approvals)?
- Can the repo accept large binary assets directly, or is Git LFS (or a separate asset pack) required?
- Will a shared Blender toolchain (version, addons) be installed on all Symphony-capable machines, or must agents rely on a pre-built container/VM?

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

- What changed: Plan drafted; no implementation due to missing Blender/NIF toolchain and undefined prototype subject.
- Validation performed: None (blocked before asset work).
- Docs updated: This plan only.
- Remaining risks: Entire leaderhead pipeline remains unimplemented until environment/tooling and prototype scope are clarified.
- Follow-up tasks: Provide/approve Blender toolchain installation, select prototype leader + reference material, confirm repository policy on large binary assets.
