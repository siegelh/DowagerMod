# Symphony Implementation

- Status: `complete`
- Owner / agent: `Codex`
- Last updated: `2026-03-09`

## Problem Statement

- Task: prepare an implementation-ready plan for a Python Symphony service adapted to DowagerMod.
- Current observed behavior: the repo now has a base spec (`SYMPHONY_SPEC.md`), a DowagerMod delta (`SYMPHONY_REPO_DELTA.md`), a live GitHub Project v2 board, working GitHub CLI auth, and repo workflow docs, but no implementation plan that turns those decisions into a concrete build order.
- Why this is a real repo/code problem: without an implementation plan, the first build prompt will either overbuild the service or skip key repo-specific concerns like worktrees, validation, project status transitions, and human-review handoff.

## Why This Matters

- User or gameplay impact: Symphony is intended to become the work runner for future agentic development in this repo.
- Maintenance / workflow / agent impact: an implementation plan reduces the risk of building the wrong abstractions first and makes the next prompt much more likely to succeed in one pass.

## Scope

- In scope: define the first implementation slice of Symphony for `siegelh/DowagerMod`.
- In scope: identify the concrete Python modules, runtime config files, GitHub integration points, and validation rules required for v1.

## Non-Goals

- Not changing: no Python service code yet.
- Not changing: no automatic issue creation, no full production deployment, and no merge automation.

## Trusted Sources Of Truth

- Primary code/config/scripts:
  - `SYMPHONY_SPEC.md`
  - `SYMPHONY_REPO_DELTA.md`
  - `AGENTS.md`
  - `WORKFLOW.md`
  - `ARCHITECTURE.md`
  - `README.md`
- Runtime entrypoints/import paths to verify:
  - `agent-baseline`
  - `CoreFiles/install.py`
  - `tools/test_gate.ps1`
  - `tools/test_full.ps1`
- Validation scripts/tests/hooks:
  - `.githooks/pre-commit`
  - `tools/test_gate.ps1`

## Existing Docs / Plans Trust Review

- Reviewed docs/plans:
  - `SYMPHONY_SPEC.md`
    - `trusted for this task`
  - `SYMPHONY_REPO_DELTA.md`
    - `trusted for this task`
  - `docs/plans/active/2026-03-09-symphony-repo-delta.md`
    - `trusted for this task`
  - `WORKFLOW.md`
    - `trusted for this task`
- Conflicts with code/config/scripts:
  - none currently blocking; the GitHub board, labels, and auth are now aligned with the repo delta

## Potentially Stale Or Conflicting Materials

- Item: root `WORKFLOW.md` as a machine-readable workflow file
  - Why it may be stale: Symphony needs a separate machine-readable runtime workflow file.
  - What code/config overrode or verified it: `SYMPHONY_REPO_DELTA.md` explicitly keeps root `WORKFLOW.md` human-normative.
- Item: assuming generic empty workspaces
  - Why it may be stale: this repo should use git worktrees from `agent-baseline`.
  - What code/config overrode or verified it: confirmed repo delta policy.

## Affected Files / Directories

- Primary implementation paths:
  - `symphony/`
  - `symphony/WORKFLOW.md`
  - `tests/`
- Adjacent paths to inspect:
  - `AGENTS.md`
  - `WORKFLOW.md`
  - `ARCHITECTURE.md`
  - `docs/MANUAL_SMOKE_TESTS.md`
  - `docs/TESTING_WORKFLOW.md`
- Paths to avoid unless evidence requires them:
  - `CoreFiles/`
  - `third_party/beyond-the-sword-sdk/CvGameCoreDLL`

## Assumptions That Need Human Confirmation

- Assumption: the first implementation slice should stop at branch/prompt/workspace/issue-selection/project-status capability plus a single Codex app-server turn, not full autonomous merge flow.
  - Why it matters: it constrains v1 complexity and keeps review in the loop.
  - What changes if false: the first implementation would need much stronger PR, merge, and issue-close automation.
- Assumption: PR creation should be deferred until after the first end-to-end GitHub/worktree/agent loop is stable.
  - Why it matters: it keeps milestone one focused on issue pickup, worktree creation, Codex execution, and deterministic project-state transitions.
  - What changes if false: the first implementation would need extra git/PR logic and stricter post-run validation.

## Proposed Implementation Steps

1. Verify live entrypoints, imports, runtime paths, and active asset roots.
2. Confirm trusted sources and classify stale/conflicting materials in this area.
3. Implement the smallest change that solves the problem.
4. Update related docs/runbooks affected by the change.
5. Validate with repo test gates and required smoke testing.

### Task-Specific Steps

1. Create the Python package and runtime file layout under `symphony/`.
2. Implement config/workflow loading for `symphony/WORKFLOW.md`.
3. Implement the GitHub adapter for:
   - project fetch
   - `Ready` issue selection
   - status transitions
   - label inspection
4. Implement worktree creation from `agent-baseline`.
5. Implement the first agent runner path:
   - build prompt
   - start Codex app-server
   - run a turn in the per-issue worktree
6. Implement structured logs and local runtime state outside the repo tree.
7. Add tests for:
   - workflow parsing
   - GitHub issue normalization
   - eligibility logic
   - worktree path creation
8. Stop the first milestone at:
   - fetch the oldest eligible `Ready` issue
   - move it through `Planning` and `In Progress`
   - create or reuse a git worktree from `agent-baseline`
   - launch one Codex app-server turn in that worktree
   - record a structured local run summary outside the repo tree
   - move the project item to `Human Review` on success or `Blocked` on failure
   - explicitly defer PR creation and issue comments to a later slice

## Validation Plan

- Required automated checks:
  - unit tests for Symphony modules
  - a local CLI smoke test for workflow loading, GitHub selection, and worktree creation
- Required repo scripts:
  - only if the implementation task edits BtS XML or DLL files; otherwise not required for pure Python service work
- Required manual smoke test:
  - not required for pure Symphony service code unless the task also changes gameplay files
- Validation blocked or not yet runnable:
  - no blocker; GitHub auth and Project v2 access are now available locally

## Documentation Updates Required

- Docs to update with the implementation:
  - `SYMPHONY_REPO_DELTA.md`
  - `README.md` if Symphony becomes a first-class repo subsystem
  - `docs/index.md` once Symphony docs/config become stable
- Docs/plans to mark stale, historical, or superseded:
  - none yet
- `docs/index.md` updates needed:
  - likely yes once `symphony/` exists
- `ARCHITECTURE.md` / `WORKFLOW.md` / runbook updates needed:
  - `WORKFLOW.md` may need a short section clarifying how Symphony fits into repo operations

## Risks / Rollback

- Main risks:
  - overbuilding the orchestrator before the first end-to-end slice works
  - coupling the service too tightly to CLI behavior instead of stable API calls
  - letting runtime state dirty the repo
- Likely failure modes:
  - GitHub issue/project model implemented incorrectly
  - worktree management from `agent-baseline` is brittle
  - prompt/workflow split conflicts with the repo's existing docs
- Safe rollback approach:
  - remove the `symphony/` package and related docs only
- Paths that should not be touched during rollback:
  - `CoreFiles/`
  - `third_party/`
  - existing mod gameplay files

## Open Questions

- Should Symphony add deterministic issue comments in milestone two, or continue to leave narrative summaries to the coding agent?
- Should a later slice own PR creation directly in the orchestrator, or trigger it only after a successful tracked commit exists?

## Completion Checklist

- [x] Trusted sources of truth were verified from code/config/scripts.
- [x] Existing docs/plans in this area were reviewed and classified for trustworthiness.
- [x] Assumptions needing human confirmation were recorded.
- [x] Implementation steps were completed or explicitly deferred.
- [x] Required validation ran and results were recorded.
- [x] Required manual smoke test ran, or the blocker was escalated.
- [x] Related docs were updated or explicitly deferred with reason.
- [x] Residual risks and open questions were summarized.

## Final Outcome Summary

- What changed:
  - implemented a Python `symphony/` package with workflow loading, config/env resolution, GitHub Project v2 issue selection, git worktree management, Codex app-server execution, local JSON run summaries, and a `run-once` CLI
  - added a machine-readable runtime workflow at `symphony/WORKFLOW.md`
  - added unit tests for workflow parsing, config loading, GitHub selection, and worktree target generation
- Validation performed:
  - `python -m unittest discover -s tests -p "test_symphony_*.py"`
  - `python -m symphony.main --workflow symphony/WORKFLOW.md run-once --dry-run`
  - direct `AgentRunner` smoke test against live `codex app-server`
- Docs updated:
  - `docs/plans/active/2026-03-09-symphony-implementation.md`
  - `docs/index.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `symphony/README.md`
- Remaining risks:
  - PR creation, issue comments, and daemon polling are still deferred
  - real end-to-end project-state movement still needs a live `Ready` issue test
- Follow-up tasks:
  - add PR creation and issue-comment ownership in a later Symphony slice
  - add daemon/poll loop behavior after the one-shot path is proven against a real issue
