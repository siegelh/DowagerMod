# Task Title

- Status: `draft | in_progress | blocked | complete | superseded`
- Owner / agent:
- Last updated: `YYYY-MM-DD`

## Problem Statement

- Task:
- Current observed behavior:
- Why this is a real repo/code problem:

## Why This Matters

- User or gameplay impact:
- Maintenance / workflow / agent impact:

## Scope

- In scope:
- In scope:

## Non-Goals

- Not changing:
- Not changing:

## Trusted Sources Of Truth

- Primary code/config/scripts:
- Runtime entrypoints/import paths to verify:
- Validation scripts/tests/hooks:

## Existing Docs / Plans Trust Review

- Reviewed docs/plans:
- Classification for each:
  - `trusted for this task`
  - `useful context only`
  - `historical / verify before relying`
- Conflicts with code/config/scripts:

## Potentially Stale Or Conflicting Materials

- Item:
  - Why it may be stale:
  - What code/config overrode or verified it:
- Item:
  - Why it may be stale:
  - What code/config overrode or verified it:

## Affected Files / Directories

- Primary implementation paths:
- Adjacent paths to inspect:
- Paths to avoid unless evidence requires them:

## Assumptions That Need Human Confirmation

- Assumption:
  - Why it matters:
  - What changes if false:
- Assumption:
  - Why it matters:
  - What changes if false:

## Proposed Implementation Steps

1. Verify live entrypoints, imports, runtime paths, and active asset roots.
2. Confirm trusted sources and classify stale/conflicting materials in this area.
3. Implement the smallest change that solves the problem.
4. Update related docs/runbooks affected by the change.
5. Validate with repo test gates and required smoke testing.

### Task-Specific Steps

1.
2.
3.

## Validation Plan

- Required automated checks:
- Required repo scripts:
  - `.\tools\test_gate.ps1`
- Required manual smoke test:
  - install or copy updated files into the live game tree
  - launch the mod and confirm it reaches the main menu without XML/Python popups
  - load a representative save or start a quick single-player game
  - open the affected screen or advisor if relevant
  - exercise the changed mechanic, building, unit, or art reference
  - end one turn
  - save and reload once if persistence changed
- Validation blocked or not yet runnable:

## Documentation Updates Required

- Docs to update with the implementation:
- Docs/plans to mark stale, historical, or superseded:
- `docs/index.md` updates needed:
- `ARCHITECTURE.md` / `WORKFLOW.md` / runbook updates needed:

## Risks / Rollback

- Main risks:
- Likely failure modes:
- Safe rollback approach:
- Paths that should not be touched during rollback:

## Open Questions

- Question:
- Question:

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
