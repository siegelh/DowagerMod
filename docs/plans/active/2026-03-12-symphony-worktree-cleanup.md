# Symphony Worktree Cleanup

- Status: `complete`
- Owner / agent: `Codex`
- Last updated: `2026-03-12`

## Problem Statement

- Task: add cleanup automation for Symphony-created local worktrees after issue work is merged or otherwise done.
- Current observed behavior: Symphony-created worktrees persist after PR creation and merge, which is useful for local testing but can accumulate over time.
- Why this is a real repo/code problem: persistent issue worktrees are acceptable short-term, but without a cleanup command the local workspace will become noisy and harder to manage.

## Why This Matters

- User or gameplay impact: the user wants to test locally from worktrees, but also wants a predictable way to clear completed issue branches.
- Maintenance / workflow / agent impact: cleanup automation makes Symphony feel more like a durable local worker instead of a one-off experiment.

## Scope

- In scope: add a conservative cleanup command that scans Symphony issue worktrees.
- In scope: only remove clean local worktrees/branches that are clearly done.
- In scope: update GitHub Project status to `Done` when cleanup confirms merged/completed work.
- In scope: add a Windows helper script and docs for the cleanup flow.

## Non-Goals

- Not changing: no automatic silent cleanup inside the polling loop.
- Not changing: no deletion of dirty worktrees.
- Not changing: no remote-branch deletion.

## Trusted Sources Of Truth

- Primary code/config/scripts:
  - `symphony/main.py`
  - `symphony/github_client.py`
  - `symphony/worktree_manager.py`
  - `tools/`
- Runtime entrypoints/import paths to verify:
  - current local worktrees under `C:\sw`
- Validation scripts/tests/hooks:
  - `python -m unittest discover -s tests -p "test_symphony_*.py"`

## Existing Docs / Plans Trust Review

- Reviewed docs/plans:
  - `docs/plans/active/2026-03-12-symphony-local-server.md`
    - `trusted for this task`
  - `symphony/README.md`
    - `trusted for this task`
- Conflicts with code/config/scripts:
  - none yet; current docs explicitly say cleanup is still manual/policy-driven.

## Potentially Stale Or Conflicting Materials

- Item: assuming merged issue worktrees should stay forever
  - Why it may be stale: the user wants cleanup automation now that the first real PR flow has worked.
  - What code/config overrode or verified it: current Symphony behavior leaves worktrees behind after merge.

## Affected Files / Directories

- Primary implementation paths:
  - `symphony/`
  - `tests/`
  - `tools/`
- Adjacent paths to inspect:
  - `README.md`
  - `docs/index.md`
  - `ARCHITECTURE.md`
  - `WORKFLOW.md`
- Paths to avoid unless evidence requires them:
  - gameplay XML/Python/DLL content

## Assumptions That Need Human Confirmation

- Assumption: cleanup should be explicit and conservative rather than automatic in the background worker.
  - Why it matters: it keeps local testing possible after merge and avoids surprising deletion.
  - What changes if false: cleanup would move into the polling loop and need stronger branch/test-state safeguards.

## Proposed Implementation Steps

1. Add GitHub lookup support for branch PR state and merged/closed status.
2. Add worktree scanning plus eligibility checks for Symphony-created issue worktrees.
3. Add a CLI cleanup command with dry-run by default.
4. Add a PowerShell helper script for local cleanup.
5. Update docs and run Symphony validation.

## Validation Plan

- Required automated checks:
  - `python -m unittest discover -s tests -p "test_symphony_*.py"`
- Required repo scripts:
  - not required unless gameplay files are edited
- Required manual smoke test:
  - run cleanup in dry-run mode
  - run cleanup in apply mode on a known merged issue worktree
- Validation blocked or not yet runnable:
  - none identified

## Documentation Updates Required

- Docs to update with the implementation:
  - `symphony/README.md`
  - `README.md`
  - `docs/index.md`
  - `ARCHITECTURE.md`

## Risks / Rollback

- Main risks:
  - deleting a worktree someone still wants for local testing
  - deleting a branch that is still needed
  - misclassifying incomplete work as done
- Likely failure modes:
  - closed-but-unmerged PR ambiguity
  - stale local branch state
  - dirty worktrees blocking expected cleanup
- Safe rollback approach:
  - remove the cleanup command and helper script
- Paths that should not be touched during rollback:
  - open-review worktrees

## Open Questions

- Should a later slice also clean remote branches after merge, or leave that human-managed?
- Should future `serve` mode perform passive cleanup suggestions without actually deleting anything?

## Completion Checklist

- [x] Cleanup command exists with dry-run and apply modes.
- [x] Only safe, clean, completed issue worktrees are removed.
- [x] GitHub project items can be moved to `Done` during cleanup.
- [x] Helper script and docs are updated.
- [x] Tests and CLI/manual cleanup smoke checks pass.

## Final Outcome Summary

- What changed:
  - added a Symphony `cleanup` CLI command with dry-run-by-default behavior
  - added GitHub PR-state lookup for cleanup eligibility checks
  - added local worktree scanning/removal for safe Symphony issue branches
  - added `tools/Cleanup-Symphony.ps1` as the Windows helper entrypoint
- Validation performed:
  - `python -m unittest discover -s tests -p "test_symphony_*.py"`
  - `python -m symphony.main --workflow symphony/WORKFLOW.md cleanup --issue-number 43`
  - `python -m symphony.main --workflow symphony/WORKFLOW.md cleanup --issue-number 43 --apply`
- Docs updated:
  - `symphony/README.md`
  - `README.md`
  - `docs/index.md`
  - `ARCHITECTURE.md`
- Remaining risks:
  - issue closure still remains separate from cleanup; project status can move to `Done` while the issue stays open
  - detached/manual worktrees outside the Symphony branch pattern are intentionally untouched
- Follow-up tasks:
  - decide whether merged PR cleanup should also comment on or close issues in a future slice
  - consider a non-destructive cleanup suggestion mode inside `serve` before any automatic pruning is added
