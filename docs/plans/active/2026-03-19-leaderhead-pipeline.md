# Build actual Civ IV BTS leaderhead asset pipeline from photo

- Status: `blocked`
- Owner / agent: Symphony Squad – Implementer
- Last updated: `2026-03-19`

## Problem Statement

- Task: Deliver a working pipeline that converts a historical photo into a fully functional Civilization IV: Beyond the Sword leaderhead, including Blender sources, NIF/KFM exports, textures, rigging, XML hookups, and in-game validation.
- Current observed behavior: The repo only contains preexisting leaderhead assets imported from other mods plus static DDS buttons; there is no scripted or documented process here that starts from a 2D photo and lands a Civ4-ready animated leaderhead.
- Why this is a real repo/code problem: Without a reproducible art pipeline, the mod cannot legally or consistently add bespoke leaders derived from historical imagery, and issue #60 demands a proof-quality prototype.

## Why This Matters

- User or gameplay impact: Players cannot receive the promised new leaderhead content, and there is no guarantee that future leaders can be produced or maintained.
- Maintenance / workflow / agent impact: Agents currently lack any tooling or documented steps to regenerate leaderheads, making future edits brittle and blocking compliance with the issue’s acceptance criteria.

## Scope

- In scope:
  - Selecting a historically sourced, license-compatible reference photo.
  - Building or importing a leaderhead mesh, textures, and rig inside Blender.
  - Exporting Gamebryo NIF/KFM assets plus shader-ready DDS textures.
  - Hooking the art into BtS XML (LeaderHeadInfos, ArtDefines).
  - Validating in-game via manual smoke test evidence.
- Out of scope for this task (unless unblocked later):
  - Broad HUD or DLL refactors not required for the new leaderhead.
  - Replacing every existing leaderhead pipeline.

## Non-Goals

- Not changing: Existing leaderhead catalog beyond the new prototype.
- Not changing: Installer or deployment tooling unless the pipeline requires it.

## Trusted Sources Of Truth

- Primary code/config/scripts:
  - `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/Art/Leaderheads/**`
  - `CoreFiles/.../Assets/XML/Art/CIV4ArtDefines_Leaderhead.xml`
  - `CoreFiles/.../Assets/XML/Civilizations/CIV4LeaderHeadInfos.xml`
- Runtime entrypoints/import paths to verify:
  - Leaderhead art references from `Art/Leaderheads/...`
  - Diplomacy scene animation references in `XML/Art/CIV4ArtDefines_Leaderhead.xml`
- Validation scripts/tests/hooks:
  - `.\tools\test_gate.ps1` (XML validation)
  - Manual smoke test per `docs/MANUAL_SMOKE_TESTS.md`

## Existing Docs / Plans Trust Review

- Reviewed docs/plans:
  - `README.md`, `AGENTS.md`, `WORKFLOW.md`, `ARCHITECTURE.md`, `docs/index.md`, `docs/TESTING_WORKFLOW.md`
- Classification:
  - All above: `trusted for this task` (they define process expectations but do not give leaderhead-specific instructions).
- Conflicts: None; the gap is simply missing art pipeline documentation/assets.

## Potentially Stale Or Conflicting Materials

- Item: Existing leaderhead folders under `Assets/Art/Leaderheads/new/`
  - Why stale: Contain disparate third-party assets without provenance or accompanying Blender + export steps.
  - Override evidence: No scripts or docs connect them to a reproducible workflow; many include only finished NIF/DDS with no pipeline metadata.

## Affected Files / Directories

- Primary implementation paths:
  - `Assets/Art/Leaderheads/<new-leader>/...`
  - `Assets/XML/Art/CIV4ArtDefines_Leaderhead.xml`
  - `Assets/XML/Civilizations/CIV4LeaderHeadInfos.xml`
- Adjacent paths to inspect:
  - `Assets/Art/Shared`, `Assets/Art/Units/Shared` for rig/skeleton reuse
  - `Assets/Res/Fonts` for diplomacy button text if needed
- Paths to avoid unless necessary:
  - Base `Assets/` and `Warlords/` mirrors (unless runtime demands)
  - DLL source (not required for pure art addition)

## Assumptions That Need Human Confirmation

1. Assumption: A Windows-accessible Blender environment with the correct NifTools exporter (historically Blender 2.49b + Python 2.6) can be installed or already exists on this workstation.
   - Why it matters: Without Blender plus NifTools, no Gamebryo-compatible NIF/KFM output can be produced.
   - Impact if false: The pipeline cannot be executed; issue remains blocked.
2. Assumption: A legally usable historical photo (clear rights) is available or can be provided for the target leader.
   - Why it matters: The task explicitly requires starting from a photo; licensing risk must be managed.
   - Impact if false: We cannot start modeling, and the deliverable fails.

## Proposed Implementation Steps

1. Confirm toolchain availability:
   - Install/configure Blender + Civ4-capable NifTools exporter.
   - Install supporting civilopedia shader preview scripts if needed.
2. Choose target leader + reference photo with documented licensing.
3. Build Blender scene:
   - Sculpt or photobash a head mesh (either via sculpting from scratch or adapting an existing high-poly head) aligned to Civ4 rig requirements.
   - Generate color, normal, specular, and gloss DDS textures derived from the photo.
4. Rigging & animation prep:
   - Bind the mesh to an existing Civ4 leaderhead armature (e.g., Victoria/Elizabeth skeleton).
   - Bake animations or reuse an existing KFM.
5. Export assets:
   - Export NIF head mesh + KFM using NifTools with Civ4 shader properties.
   - Save Blender `.blend` file and intermediate textures into the repo.
6. Integrate into XML:
   - Add ArtDefine entry referencing the new NIF/KFM.
   - Assign the art define to a test LeaderHead entry (new or existing placeholder).
7. Validate:
   - Run `.\tools\test_gate.ps1`.
   - Install into local Civ4, launch mod, and capture diplomacy screen proof.

### Task-Specific Steps (blocked today)

1. Verify Blender/NifTools availability on this Symphony worker.
2. Acquire licensed reference photo for the chosen historical figure.
3. Model/texture/rig/export assets and wire XML as above.

## Validation Plan

- Automated:
  - `.\tools\test_gate.ps1`
- Manual smoke:
  - Install updated assets, launch mod, open diplomacy screen for the prototype leaderhead, confirm animation and textures render, capture screenshots/video.
- Current status: Blocked before implementation; validation cannot run without the toolchain and assets.

## Documentation Updates Required

- New doc outlining the leaderhead pipeline once implemented.
- Update `docs/index.md` after the pipeline doc exists.
- Add README/ARCHITECTURE references if new process becomes canonical.

## Risks / Rollback

- Toolchain risk: Civ4 NifTools support requires legacy Blender; mixing versions can corrupt files.
- Licensing risk: Using a photo without clear rights could force asset removal.
- Runtime risk: Incorrect shaders/rigging crash diplomacy scenes; rollback by removing XML references and art files.

## Open Questions

1. Which historical figure/photo should the prototype use, and who provides the rights-cleared source?
2. Can we install and run the required Blender + NifTools stack on this environment (or is remote/manual work needed)?
3. Is there an existing Civ4-friendly rig/skeleton in the repo we should standardize on?

## Completion Checklist

- [ ] Toolchain verified/installed.
- [ ] Licensed photo selected and stored in repo references.
- [ ] Blender scene + textures created and committed.
- [ ] NIF/KFM exports validated in-game.
- [ ] XML references added/validated via `test_gate`.
- [ ] Manual diplomacy-screen smoke test recorded.
- [ ] Pipeline documentation added and indexed.
- [ ] Residual risks recorded.

## Final Outcome Summary

- What changed: No implementation yet; recorded blockers and pre-work requirements.
- Validation performed: None (blocked).
- Docs updated: Created this plan to document scope and blockers.
- Remaining risks: Entire deliverable depends on provisioning Blender/NifTools and licensed reference material.
- Follow-up tasks: Provide toolchain/photo, then resume implementation per steps above.
