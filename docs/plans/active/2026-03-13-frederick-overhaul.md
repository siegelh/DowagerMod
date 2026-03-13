# Frederick Overhaul Detailed Design

- Status: `completed`
- Owner / agent: Symphony (issue #45)
- Last updated: `2026-03-13`

## Problem Statement

- Task: Produce a Detailed Overhaul V4 design for Frederick (Prussia/Germany) using the repo skill contract, including historical research, mechanics coverage, and a quantified implementation-ready spec (traits + UU + UB, no new unique improvement).
- Current observed behavior: No up-to-date Frederick overhaul design doc exists in the repo; existing leader plan of record lists him as planned but lacks implementation detail.
- Why this is a real repo/code problem: Without a vetted design, future implementation work lacks requirements, risking ad-hoc XML/DLL edits that violate the plan-of-record process.

## Why This Matters

- User or gameplay impact: Frederick remains on the vanilla design, so his mod identity is undefined; delivering a documented overhaul unlocks future gameplay implementation.
- Maintenance / workflow / agent impact: Establishes a vetted spec that aligns with LEADER_OVERHAUL_PLAN_OF_RECORD and prevents duplicate discovery work for later agents.

## Scope

- In scope:
  - Full Detailed Overhaul V4 workflow for Frederick (history research, mechanics inventory, novel mechanic evaluation, quantified spec).
  - Checked-in design doc under `docs/` capturing the final plan plus compliance summary.
- In scope:
  - Updating docs index/plan references if needed to reflect the new active design.

## Non-Goals

- Not changing: Actual XML/Python/DLL gameplay data (this issue is design-only).
- Not changing: Other leaders/civilizations besides Frederick/Germany.

## Trusted Sources Of Truth

- Primary code/config/scripts: `CoreFiles/.../Assets/XML/Civilizations/CIV4LeaderHeadInfos.xml`, `CIV4UnitInfos.xml`, `CIV4BuildingInfos.xml` for current Frederick references.
- Runtime entrypoints/import paths to verify: N/A (design-only but will inspect existing XML definitions to understand current implementation).
- Validation scripts/tests/hooks: N/A for design phase (no code change), but future implementation will rely on `tools/test_gate.ps1`.

## Existing Docs / Plans Trust Review

- Reviewed docs/plans:
  - `docs/LEADER_OVERHAUL_PLAN_OF_RECORD.md` – `trusted for this task`.
  - `skills/detailed-overhaul-v4/SKILL.md` – `trusted for workflow`.
  - Issue #45 description – `trusted for constraints`.
- Conflicts with code/config/scripts: None yet; inspection of live XML will confirm baseline Frederick data for reference only.

## Potentially Stale Or Conflicting Materials

- Item: Historical leader drafts under `docs/archive/plans/`.
  - Why it may be stale: Pre-Symphony drafts may not align with Detailed Overhaul V4 workflow.
  - What code/config overrode or verified it: Plan-of-record plus live XML; will only reference archive if clearly marked historical.

## Affected Files / Directories

- Primary implementation paths:
  - `docs/plans/active/2026-03-13-frederick-overhaul.md` (this plan).
  - New Frederick design doc under `docs/` (exact filename TBD during execution).
- Adjacent paths to inspect:
  - `CoreFiles/.../Assets/XML/Civilizations/CIV4LeaderHeadInfos.xml`
  - `CoreFiles/.../Assets/XML/Units/CIV4UnitInfos.xml`
  - `CoreFiles/.../Assets/XML/Buildings/CIV4BuildingInfos.xml`
- Paths to avoid unless evidence requires them:
  - Actual BtS XML, Python, DLL source files (no gameplay edits planned).

## Assumptions That Need Human Confirmation

- Assumption: Deliverable is a design document only; gameplay implementation is a later task.
  - Why it matters: Determines whether validation scripts/tests must run now.
  - What changes if false: Would need to plan for XML/DLL edits plus validation.

## Proposed Implementation Steps

1. Verify Frederick’s current XML definitions (leader traits, UU, UB) to anchor starting point.
2. Follow Detailed Overhaul V4 workflow:
   - Gather historical sources (>=3 credible, mixed academic/popular, cite).
   - Run full Modiki entrypoint scan (`Civ4BuildingInfos` et al.) plus repo mechanics inventory (per skill references).
   - Document any new mechanics discovered during repo scan.
   - Derive historical pillars, baseline + novel mechanics per pillar, admission log.
   - Build mechanics coverage table (vanilla + repo extensions).
   - Produce final overhaul spec (traits, UU, UB, diplomacy/personality, AI notes) with quantified balance table and implementation plan.
   - Include distinctiveness audit and compliance summary with LEADER_OVERHAUL_PLAN_OF_RECORD checklist.
3. Save the final design doc under `docs/plans/active/2026-03-13-frederick-detailed-overhaul.md` (name subject to adjustment) and ensure `docs/index.md` references it if required.
4. Summarize work + validation status in Symphony response, noting no gameplay validation was run (design only).

## Validation Plan

- Required automated checks: None (no code changes).
- Required repo scripts: None at this stage; call out deferred validation for future implementation.
- Required manual smoke test: Not applicable (design work only).
- Validation blocked or not yet runnable: Gameplay validation deferred until implementation.

## Documentation Updates Required

- Docs to update: New Frederick overhaul design doc; potentially `docs/index.md` overhaul tracker entry.
- Docs/plans to mark stale: None identified yet.
- `docs/index.md` updates needed: Add new design doc link if not auto-discoverable.
- `ARCHITECTURE.md` / `WORKFLOW.md` updates: Not expected.

## Risks / Rollback

- Main risks: Insufficient mechanics coverage, missing citations, divergence from plan-of-record guardrails.
- Likely failure modes: Skipping novel mechanic evaluation; forgetting to document Modiki/DLL mechanics scan; producing non-quantified effects.
- Safe rollback approach: Revert new docs.
- Paths that should not be touched during rollback: BtS XML/Python/DLL.

## Open Questions

- Resolved: Design doc lives under `docs/plans/active/2026-03-13-frederick-detailed-overhaul.md`; no separate directory required unless future maintainer requests it.

## Completion Checklist

- [x] Trusted sources verified.
- [x] Existing docs/plans classified.
- [x] Assumptions recorded.
- [x] Implementation steps executed.
- [x] Validation status recorded (design-only).
- [x] Docs updated.
- [x] Residual risks/open questions summarized.

## Final Outcome Summary

- Created `docs/plans/active/2026-03-13-frederick-detailed-overhaul.md`, which delivers the complete Detailed Overhaul V4 spec (history, mechanics inventory, novel mechanic log, trait/UU/UB details, balance table, and implementation plan) per issue #45; no gameplay/code changes were made in this task, so validation remains deferred to the future implementation issue.
