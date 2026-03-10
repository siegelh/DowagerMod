# Symphony PR Handoff

- Status: `complete`
- Owner / agent: `Codex`
- Last updated: `2026-03-10`

## Problem Statement

- Task: upgrade Symphony from "single agent turn then Human Review" to a real GitHub review handoff for this repo.
- Current observed behavior: Symphony can pick a `Ready` issue, create a worktree/branch, run one Codex turn, and move the issue through project states. It does not yet run repo-native validation, commit/push changes, create a PR, or write an issue summary comment.
- Why this is a real repo/code problem: `Human Review` without a PR, validation result, or summary is too early and too opaque for practical repo use.

## Why This Matters

- User or gameplay impact: humans need a reviewable artifact and validation evidence before spending time on manual gameplay testing.
- Maintenance / workflow / agent impact: the issue delivery loop is not production-ready until it can hand off a branch and PR cleanly.

## Scope

- In scope: add validation-aware handoff to Symphony's one-shot issue runner.
- In scope: create a draft PR and issue summary comment when a run succeeds and validation passes.
- In scope: keep project status transitions aligned with the actual handoff stage.
- In scope: document the intended future split between issue-delivery, PR-review, and hygiene job types.

## Non-Goals

- Not changing: no autonomous merge or issue close logic.
- Not changing: no background daemon or scheduled review/hygiene jobs yet.
- Not changing: no gameplay manual smoke-test automation.

## Trusted Sources Of Truth

- Primary code/config/scripts:
  - `symphony/`
  - `SYMPHONY_SPEC.md`
  - `SYMPHONY_REPO_DELTA.md`
  - `AGENTS.md`
  - `WORKFLOW.md`
  - `ARCHITECTURE.md`
- Runtime entrypoints/import paths to verify:
  - `symphony/main.py`
  - `symphony/orchestrator.py`
  - `symphony/WORKFLOW.md`
  - `tools/test_gate.ps1`
- Validation scripts/tests/hooks:
  - `python -m unittest discover -s tests -p "test_symphony_*.py"`
  - `.\tools\test_gate.ps1`

## Existing Docs / Plans Trust Review

- Reviewed docs/plans:
  - `SYMPHONY_SPEC.md`
    - `trusted for this task`
  - `SYMPHONY_REPO_DELTA.md`
    - `trusted for this task`
  - `docs/plans/active/2026-03-09-symphony-implementation.md`
    - `trusted for this task`
  - `WORKFLOW.md`
    - `trusted for this task`
- Conflicts with code/config/scripts:
  - none blocking, but the current implementation stops earlier than the repo delta's recommended production handoff.

## Potentially Stale Or Conflicting Materials

- Item: treating `Human Review` as "agent turn completed"
  - Why it may be stale: humans need PR and validation context before review is useful.
  - What code/config overrode or verified it: current `symphony/orchestrator.py` behavior; this task will tighten that handoff.

## Affected Files / Directories

- Primary implementation paths:
  - `symphony/orchestrator.py`
  - `symphony/github_client.py`
  - `symphony/models.py`
  - `symphony/WORKFLOW.md`
  - `tests/`
- Adjacent paths to inspect:
  - `tools/test_gate.ps1`
  - `README.md`
  - `ARCHITECTURE.md`
  - `SYMPHONY_REPO_DELTA.md`
- Paths to avoid unless evidence requires them:
  - `CoreFiles/`
  - `third_party/beyond-the-sword-sdk/CvGameCoreDLL`

## Assumptions That Need Human Confirmation

- Assumption: draft PRs are the right default handoff artifact for implementation work.
  - Why it matters: it defines the production review loop.
  - What changes if false: Symphony would need to stop at pushed branches and issue comments only.
- Assumption: manual gameplay testing remains human-owned even when DLL/XML validation passes.
  - Why it matters: it defines the meaning of `Human Review`.
  - What changes if false: Symphony would need additional install/run/smoke automation.

## Proposed Implementation Steps

1. Verify live entrypoints, imports, runtime paths, and active validation scripts.
2. Add a change-inspection and validation layer for Symphony runs.
3. Add git commit/push support for successful runs.
4. Add GitHub draft PR creation and issue comment support.
5. Update docs and tests to match the tighter handoff behavior.

### Task-Specific Steps

1. Detect changed files after the Codex turn and classify whether repo-native validation is required.
2. Run `tools/test_gate.ps1` for DLL or BtS XML edits before handoff.
3. Stop in `Blocked` if the validation gate fails or no reviewable change exists.
4. Commit and push the issue branch on successful validation.
5. Create or reuse a draft PR targeting `agent-baseline`.
6. Post a GitHub issue comment summarizing:
   - branch
   - PR
   - validations run
   - changed files
   - manual testing expectations
7. Move the issue/project item to `Human Review` only after the review artifact exists.
8. Record future job-type follow-up in docs:
   - `implement_issue`
   - `review_pr`
   - `triage_issue`
   - `hygiene_scan`

## Validation Plan

- Required automated checks:
  - `python -m unittest discover -s tests -p "test_symphony_*.py"`
  - local Symphony dry-run and live-run smoke tests as appropriate
- Required repo scripts:
  - `.\tools\test_gate.ps1` when the worktree changes DLL or BtS XML files
- Required manual smoke test:
  - not automated by this slice; remain human-owned after the draft PR handoff
- Validation blocked or not yet runnable:
  - no blocker; GitHub auth, project access, and local Codex access already work

## Documentation Updates Required

- Docs to update with the implementation:
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/index.md`
  - `SYMPHONY_REPO_DELTA.md`
- Docs/plans to mark stale, historical, or superseded:
  - `docs/plans/active/2026-03-09-symphony-implementation.md` should remain historical context for the first slice
- `docs/index.md` updates needed:
  - yes, if Symphony’s handoff semantics change materially
- `ARCHITECTURE.md` / `WORKFLOW.md` / runbook updates needed:
  - `ARCHITECTURE.md` should mention the delivery/review/hygiene job split as planned evolution

## Risks / Rollback

- Main risks:
  - creating PRs or comments without enough validation context
  - leaving issue/project state inconsistent with branch/PR state
  - overcoupling Symphony to one repo validation pattern without clear heuristics
- Likely failure modes:
  - false-positive "no changes" detection
  - push or PR creation failures after a successful local run
  - duplicate PR creation on retries
- Safe rollback approach:
  - revert only the Symphony code/docs for this milestone
- Paths that should not be touched during rollback:
  - `CoreFiles/`
  - `third_party/`
  - existing gameplay code outside the issue worktree

## Open Questions

- Should a later slice update existing PR bodies/comments on reruns, or only append new comments?
- Should validation policy become configurable per issue type later, or stay heuristic in v1?

## Completion Checklist

- [x] Trusted sources of truth were verified from code/config/scripts.
- [x] Existing docs/plans in this area were reviewed and classified for trustworthiness.
- [x] Assumptions needing human confirmation were recorded.
- [x] Implementation steps were completed or explicitly deferred.
- [x] Required validation ran and results were recorded.
- [x] Related docs were updated or explicitly deferred with reason.
- [x] Residual risks and open questions were summarized.

## Final Outcome Summary

- What changed:
  - added Symphony git/change inspection, validation, draft-PR, and issue-comment handoff support
  - upgraded the orchestrator so `Human Review` now means "validated review artifact exists," not merely "an agent turn completed"
  - documented the next-stage Symphony job split for delivery, review, triage, and hygiene work
- Validation performed:
  - `python -m unittest discover -s tests -p "test_symphony_*.py"`
  - `python -m symphony.main --workflow symphony/WORKFLOW.md run-once --dry-run`
  - `python -m symphony.main --workflow symphony/WORKFLOW.md run-once --dry-run --issue-number 43`
  - live DLL-gate attempt against `C:\sw\gh-43`, which correctly failed and blocked issue `#43`
- Docs updated:
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/index.md`
  - `SYMPHONY_REPO_DELTA.md`
  - `symphony/README.md`
- Remaining risks:
  - the live DLL gate currently fails for issue `#43` because the build environment cannot find `boost/preprocessor/debug/error.hpp`
  - end-to-end "validated branch -> pushed draft PR" still needs one issue whose automated gate passes
  - background `review_pr`, `triage_issue`, and `hygiene_scan` jobs are still planned, not implemented
- Follow-up tasks:
  - fix the DLL build environment so Symphony can complete a validated PR handoff for DLL issues
  - add PR-review and hygiene job types after the delivery loop is stable
