# Symphony Auto Cleanup After Merge And Issue Closure

- Status: `complete`
- Owner / agent: Codex
- Last updated: `2026-03-19`

## Problem Statement

- Task:
  - Make Symphony automatically prune clean per-issue worktrees once the associated PR is merged and the GitHub issue is closed.
- Current observed behavior:
  - Symphony can detect removable worktrees during cleanup scans, but the polling worker only reports candidates and never applies cleanup.
- Why this is a real repo/code problem:
  - Finished issue worktrees accumulate unless a human remembers to run manual cleanup after merge and issue closure.

## Why This Matters

- User or workflow impact:
  - Reduces stale local worktrees and branch clutter after accepted work is fully landed.
- Maintenance / agent impact:
  - Keeps `C:\sw` tidy without removing review/test worktrees prematurely.

## Scope

- In scope:
  - Add an automatic cleanup path for the polling worker.
  - Restrict auto-cleanup to clean worktrees with both a merged PR and a closed GitHub issue.
- In scope:
  - Add tests and update Symphony docs for the new behavior.

## Non-Goals

- Not changing:
  - manual `cleanup` command semantics
  - automatic issue closure or merge behavior

## Trusted Sources Of Truth

- Primary code/config/scripts:
  - `symphony/cleanup.py`
  - `symphony/orchestrator.py`
  - `symphony/server.py`
  - `tests/test_symphony_cleanup.py`
  - `tests/test_symphony_service_runtime.py`
- Validation:
  - targeted Python unit tests

## Proposed Implementation Steps

1. Add a cleanup-manager helper that filters for auto-prune-safe candidates.
2. Add a service-level best-effort auto-cleanup call that logs successful prunes.
3. Invoke auto-cleanup from the local polling worker after each cycle.
4. Cover the new candidate filter and worker hook with tests.
5. Update Symphony docs to explain that merged-plus-closed worktrees are auto-pruned during polling.

## Validation Plan

- Run:
  - `python -m pytest tests/test_symphony_cleanup.py tests/test_symphony_service_runtime.py tests/test_symphony_orchestrator.py`

## Final Outcome Summary

- What changed:
  - Symphony polling can now auto-clean eligible issue worktrees after merge plus issue closure.
- Validation performed:
  - targeted cleanup/server/orchestrator unit tests
- Docs updated:
  - `symphony/README.md`
- Remaining risks:
  - auto-cleanup still depends on the worker running; manual cleanup remains needed when the worker is idle
