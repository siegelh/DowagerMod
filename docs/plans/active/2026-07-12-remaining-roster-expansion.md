# Remaining Roster Expansion

- Status: `in_progress`
- Owner / agent: Copilot
- Last updated: `2026-07-12`

## Problem Statement

- Task: Audit and, in later implementation tasks, differentiate the 32 playable
  leader/civilization packages outside the 27-package July 2026 overhaul.
- Current observed behavior: the recent 27 have a completed design and
  implementation record, but the remaining 32 have not received the same
  package-level historical, gameplay, art, AI, compatibility, and multiplayer
  review.
- Why this is a real repo/code problem: uneven review leaves duplicated,
  under-expressed, or fragile packages in a roster intended to give every
  playable leader/civilization pairing a distinct identity.

## Why This Matters

- User or gameplay impact: all 59 playable mappings should be coherent and
  differentiated without destabilizing saves, multiplayer synchronization, AI,
  art rendering, or UI help.
- Maintenance / workflow / agent impact: a committed baseline and explicit
  tiers make later changes small, comparable, and bisectable.

## Scope

- Audit exactly the 32 packages marked `remaining_32` in
  `tools/baselines/roster_baseline.json`; the 27 packages marked `recent_27`
  are comparison context, not redesign targets.
- Assign every target one tier: `Keep`, `Polish`, `Targeted`, or `Major`, with
  evidence for historical fit, gameplay identity, trait budget, UU/UB fit,
  art closure, UI exposure, and AI behavior.
- Implement approved follow-ups as small, package-oriented, bisectable changes.
- Permit DLL mechanics only behind a written contract and a complete vertical
  slice covering XML/schema, DLL read/write and use sites, Python/UI exposure,
  AI valuation, tests, save behavior, and deterministic multiplayer behavior.
- Permit new worker actions only when complete existing tile art is present and
  static plus in-game wiring/render proof covers build action, improvement,
  worker animation, placement, button/help, AI, and persistence.
- In a later approved slice, remove Pacifism's `+1` food from worked Towns and
  add Emancipation's `+2` gold to worked Towns.
- Preserve strong XML, art, AI, save/load, and multiplayer gates throughout.

## Non-Goals

- Do not revisit the recent 27 merely to normalize their design shape.
- Do not change gameplay, DLL, art, Python, XML, or installer behavior in this
  baseline task.
- Do not add speculative worker actions, placeholder art, incomplete mechanics,
  silent compatibility breaks, or broad cross-roster commits.
- Do not include `CIVILIZATION_BARBARIAN` or `CIVILIZATION_MINOR` in playable
  package work; retain both in structural type-order snapshots.

## Trusted Sources Of Truth

- Primary code/config/scripts: live BtS files under
  `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets`,
  DLL source under `third_party/beyond-the-sword-sdk/CvGameCoreDLL`, and
  `tools/baselines/roster_baseline.json` captured from commit `12e22297f`.
- Runtime entrypoints/import paths to verify: civilization-to-leader and unique
  mappings, leader traits, synchronized Info tables, active BtS Python imports,
  XML schema readers, DLL call sites, and installed-game rendering paths.
- Validation scripts/tests/hooks: `tools/test_gate.ps1`, `tools/test_xml.ps1`,
  `tools/test_full.ps1`, `tools/build_civ4_dll.ps1`, and
  `docs/MANUAL_SMOKE_TESTS.md`.

## Existing Docs / Plans Trust Review

- `docs/LEADER_OVERHAUL_PLAN_OF_RECORD.md`: `trusted for this task` as the
  package design methodology, subject to live implementation verification.
- `docs/plans/active/2026-07-10-leader-civ-diversity-overhaul.md`:
  `trusted for this task` for identifying the completed recent 27 and their
  implementation record.
- `AGENTS.md`, `WORKFLOW.md`, `docs/TESTING_WORKFLOW.md`, and
  `docs/MANUAL_SMOKE_TESTS.md`: `trusted for this task`.
- Archived plans and external asset libraries: `useful context only`; never
  runtime truth and never direct XML targets.
- Conflicts with code/config/scripts: live BtS XML, imports, DLL readers, and
  test scripts win and the conflict must be recorded in the package audit.

## Potentially Stale Or Conflicting Materials

- Historical leader/civilization plans:
  - Why they may be stale: they can predate current type IDs, mappings, schema,
    and the recent 27-package work.
  - What code/config overrode or verified it: baseline fixture plus live BtS XML
    and DLL/Python call sites.
- Dormant or externally sourced art:
  - Why it may be stale: existence does not prove dependency closure,
    compatible skeleton/animation, button format, or runtime rendering.
  - What code/config overrode or verified it: repository-controlled copy,
    static closure checks, Civilopedia render, and complete in-game animation
    smoke tests.

## Affected Files / Directories

- Primary implementation paths:
  - `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML`
  - `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/Python`
  - `third_party/beyond-the-sword-sdk/CvGameCoreDLL`
- Adjacent paths to inspect: BtS `Assets/Art`, XML schemas and text, test tools,
  active runbooks, and repository-controlled external imports.
- Paths to avoid unless evidence requires them: base `Assets`, `Warlords`,
  `CoreFiles/dist`, installer sources, backup DLLs, generated payloads, and
  `petromod_v1`.

## Assumptions That Need Human Confirmation

- Assumption: the fixture's live-code-derived 27/32 cohort split is the approved
  partition.
  - Why it matters: it defines the complete audit queue.
  - What changes if false: adjust only cohort metadata before package design.
- Assumption: tier assignment is an audit verdict, not automatic permission to
  implement every `Polish`, `Targeted`, or `Major` proposal.
  - Why it matters: DLL, worker, civic, and art changes carry distinct gates.
  - What changes if false: batch approvals must explicitly authorize the
    additional implementation scope.

## Proposed Implementation Steps

1. Verify live entrypoints, imports, runtime paths, and active asset roots.
2. Confirm trusted sources and classify stale/conflicting materials in this area.
3. Implement the smallest change that solves the problem.
4. Update related docs/runbooks affected by the change.
5. Validate with repo test gates and required smoke testing.

### Task-Specific Steps

1. Freeze and validate the 59-package roster baseline, including the 27/32
   cohort split, traits, unique mappings, synchronized type orders, and
   deterministic XML/Python/DLL digests.
2. Audit each of the 32 targets against the plan-of-record and record one tier:
   - `Keep`: historically and mechanically sound; validation/documentation only.
   - `Polish`: text, AI weights, or conservative tuning without identity change.
   - `Targeted`: one bounded trait/UU/UB/package correction.
   - `Major`: package redesign requiring a dedicated design and rollout plan.
3. For each non-`Keep` package, record historical/gameplay thesis, power budget,
   trait-channel analysis, explicit UU/UB verdicts, art feasibility, UI plan,
   AI impact, save/MP risk, validation, and rollback boundary.
4. Sequence approved work in small commits/slices, normally one package or one
   shared contract plus its first complete vertical slice; compare every slice
   to the baseline and prohibit unrelated type-order drift.
5. Handle any DLL mechanic as contract-first work with a full vertical slice.
   Handle worker actions only after complete existing tile-art and render/wiring
   evidence is recorded.
6. Deliver the Pacifism/Emancipation worked-Town transfer as its own later
   civic slice, with exact tooltip, AI, save/load, and MP determinism checks.
7. Finish with cross-roster balance, reference integrity, art closure, AI
   autoplay, save/load, multiplayer, and installed-game smoke passes.

## Validation Plan

- Required automated checks:
  - parse and regenerate the baseline deterministically;
  - assert 59 playable mappings split exactly 27 recent / 32 remaining;
  - assert Barbarian and Minor are absent from packages but present in the
    civilization InfoType order;
  - resolve every leader, trait, UU class/type, and UB class/type;
  - compare synchronized type counts/orders and SHA-256 digests after each slice;
  - reject duplicate/missing types and unintended synchronized-order drift;
  - statically close all selected NIF/KFM/KF/texture/button references;
  - build DLL when its source/schema contract is touched.
- Required repo scripts:
  - `.\tools\test_gate.ps1` after each XML or DLL slice;
  - `.\tools\test_gate.ps1 -CheckDll` for XML/DLL contract work;
  - `.\tools\test_xml.ps1 -All` and `.\tools\test_full.ps1` at integration.
- Required manual smoke test:
  - install or copy updated files into the live game tree;
  - launch to the main menu without XML/Python popups;
  - inspect every affected pedia/help surface and art model;
  - exercise changed units, buildings, traits, civics, and worker actions;
  - run AI observer/autoplay coverage appropriate to the changed eras;
  - end turns, save, reload, and compare representative old/new saves;
  - run deterministic multiplayer scenarios for synchronized mechanics.
- Validation blocked or not yet runnable: later gameplay implementation and
  installed-game validation are intentionally outside this baseline todo.

## Documentation Updates Required

- Docs to update with the implementation: this plan's tier matrix and outcome;
  reusable lessons in `docs/LEADER_OVERHAUL_PLAN_OF_RECORD.md` only when proven.
- Docs/plans to mark stale, historical, or superseded: package-specific plans
  superseded by an approved `Major` design.
- `docs/index.md` updates needed: add this active plan and permanent baseline
  tooling if the project requires explicit navigation.
- `ARCHITECTURE.md` / `WORKFLOW.md` / runbook updates needed: only for proven
  new runtime contracts or validation procedures.

## Risks / Rollback

- Main risks: type-order drift, reference breakage, incomplete art, AI blindness,
  excessive power stacking, save incompatibility, and MP desynchronization.
- Likely failure modes: broad shared edits, art that parses but crashes/renders
  incorrectly, UI-hidden mechanics, unvalued AI behavior, and non-deterministic
  DLL/Python logic.
- Safe rollback approach: revert the smallest package or vertical slice and
  compare type orders and tree hashes to the baseline.
- Paths that should not be touched during rollback: installer, unrelated recent
  27 packages, base/Warlords copies, and unrelated shared art.

## Open Questions

- Which audit tiers and package order will be approved after the 32-package
  evidence matrix is complete?
- Which proposed DLL contracts, if any, justify implementation after XML-first
  alternatives are exhausted?

## Completion Checklist

- [x] Trusted sources of truth were verified from code/config/scripts.
- [x] Existing docs/plans in this area were reviewed and classified for trustworthiness.
- [x] Assumptions needing human confirmation were recorded.
- [ ] All 32 package audits and tier assignments are completed.
- [ ] Approved implementation steps are completed or explicitly deferred.
- [x] Baseline validation ran and results were recorded.
- [ ] Required gameplay/manual validation ran, or is recorded as a later-slice gate.
- [x] Related baseline docs were updated.
- [x] Residual risks and open questions were summarized.

## Final Outcome Summary

- What changed: established the active plan and deterministic pre-change roster
  baseline; no runtime behavior changed.
- Validation performed: baseline JSON parse, mapping/reference/count/order/path
  checks, cohort checks, and deterministic hash regeneration.
- Docs updated: this active plan.
- Remaining risks: package tiers and all gameplay implementation remain future
  approved work.
- Follow-up tasks: audit the 32 packages, approve tiered slices, then implement
  and validate each slice independently.
