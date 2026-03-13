# Symphony Local Server

- Status: `complete`
- Owner / agent: `Codex`
- Last updated: `2026-03-12`

## Problem Statement

- Task: turn Symphony from a manual one-shot worker into a local background worker that can be started when modding sessions begin.
- Current observed behavior: Symphony only supports `run-once`, so it must be invoked manually for each issue.
- Why this is a real repo/code problem: the current flow works for ad hoc testing, but it does not support the intended GitHub-driven modding loop where local background automation picks up `Ready` issues and moves them to draft-PR handoff.

## Why This Matters

- User or gameplay impact: the user wants to work from GitHub Issues and Project state while still being able to manually test candidate branches locally.
- Maintenance / workflow / agent impact: a local worker is the bridge between issue orchestration and future background jobs like PR review, issue triage, and hygiene scans.

## Scope

- In scope: add a long-running local Symphony mode that polls GitHub for eligible `Ready` issues.
- In scope: add singleton protection so only one local Symphony worker runs against this repo at a time.
- In scope: add Windows-friendly scripts for starting, stopping, and checking Symphony status.
- In scope: update docs so the local worker flow is discoverable and consistent with the repo workflow.

## Non-Goals

- Not changing: no hosted/cloud deployment.
- Not changing: no merge automation.
- Not changing: no new background job types beyond `implement_issue`.

## Trusted Sources Of Truth

- Primary code/config/scripts:
  - `symphony/main.py`
  - `symphony/orchestrator.py`
  - `symphony/config.py`
  - `symphony/WORKFLOW.md`
  - `tools/`
- Runtime entrypoints/import paths to verify:
  - `python -m symphony.main --workflow symphony/WORKFLOW.md run-once`
- Validation scripts/tests/hooks:
  - `python -m unittest discover -s tests -p "test_symphony_*.py"`
  - Symphony CLI smoke tests

## Existing Docs / Plans Trust Review

- Reviewed docs/plans:
  - `SYMPHONY_SPEC.md`
    - `trusted for this task`
  - `SYMPHONY_REPO_DELTA.md`
    - `trusted for this task`
  - `docs/plans/active/2026-03-09-symphony-implementation.md`
    - `trusted for this task`
- Conflicts with code/config/scripts:
  - `symphony/README.md` still says daemon loop is deferred, which this task will change.

## Potentially Stale Or Conflicting Materials

- Item: assuming Symphony needs to be launched manually for every issue
  - Why it may be stale: the desired next operating mode is a local background worker.
  - What code/config overrode or verified it: user clarified the target workflow explicitly.

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

- Assumption: a local polling worker is the right next step before considering a hosted service.
  - Why it matters: it defines the runtime model for Symphony in this repo.
  - What changes if false: we would need service-host deployment design now instead of local tooling.

## Proposed Implementation Steps

1. Add a `serve` CLI mode around the existing `run-once` service.
2. Add runtime config for poll interval and failure backoff.
3. Add singleton protection plus local heartbeat/status files under Symphony state.
4. Add PowerShell start/stop/status scripts for local use.
5. Update docs and tests for the new workflow.

## Validation Plan

- Required automated checks:
  - `python -m unittest discover -s tests -p "test_symphony_*.py"`
- Required repo scripts:
  - not required unless gameplay files are edited
- Required manual smoke test:
  - start the local Symphony worker
  - confirm it reports running status
  - stop it cleanly
- Validation blocked or not yet runnable:
  - none identified

## Documentation Updates Required

- Docs to update with the implementation:
  - `symphony/README.md`
  - `README.md`
  - `docs/index.md`
  - `ARCHITECTURE.md`
  - `WORKFLOW.md`

## Risks / Rollback

- Main risks:
  - accidentally allowing multiple workers at once
  - background process start/stop behavior being brittle on Windows
  - daemon loop masking repeated failures instead of surfacing them clearly
- Likely failure modes:
  - stale lock/status files after a crash
  - scripts launching from the wrong working directory
- Safe rollback approach:
  - remove the new `serve` mode and helper scripts
- Paths that should not be touched during rollback:
  - gameplay worktrees and issue branches

## Open Questions

- Should the local worker eventually support more than one issue type concurrently, or stay single-threaded for repo safety?
- Should a later slice auto-start Symphony for a session, or remain an explicit manual start/stop tool?

## Completion Checklist

- [x] Local `serve` mode exists.
- [x] Singleton protection prevents duplicate workers.
- [x] Local status/heartbeat information is written outside the repo.
- [x] PowerShell start/stop/status scripts work.
- [x] Docs reflect the local worker flow.
- [x] Symphony tests and CLI smoke checks pass.

## Final Outcome Summary

- What changed:
  - added a local Symphony worker mode via `python -m symphony.main --workflow symphony/WORKFLOW.md serve`
  - added runtime polling and error-backoff config in `symphony/WORKFLOW.md`
  - added a local singleton lock plus status/heartbeat/stop files under `%LOCALAPPDATA%\Symphony\DowagerMod`
  - added `status` and `stop` CLI commands
  - added Windows helper scripts: `tools/Start-Symphony.ps1`, `tools/Symphony-Status.ps1`, and `tools/Stop-Symphony.ps1`
  - documented current worktree persistence explicitly so merged issue worktrees are no longer surprising
- Validation performed:
  - `python -m unittest discover -s tests -p "test_symphony_*.py"`
  - `python -m symphony.main --workflow symphony/WORKFLOW.md run-once --dry-run`
  - `.\tools\Start-Symphony.ps1 -PollIntervalSeconds 5 -ErrorBackoffSeconds 5`
  - `.\tools\Symphony-Status.ps1`
  - `.\tools\Stop-Symphony.ps1`
- Docs updated:
  - `symphony/README.md`
  - `README.md`
  - `docs/index.md`
  - `ARCHITECTURE.md`
  - `WORKFLOW.md`
- Remaining risks:
  - worktree cleanup is still manual/policy-driven rather than automated
  - background job types beyond `implement_issue` are still future work
  - the local worker intentionally depends on a Windows modding machine with repo access and GitHub credentials
- Follow-up tasks:
  - add explicit worktree cleanup tooling/policy after merge or `Done`
  - add PR-review, issue-triage, and hygiene job types as separate worker roles
  - consider a session dashboard or tray/task-scheduler integration if daily use grows
