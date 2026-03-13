# Symphony Squad Integration

- Status: `complete`
- Owner / agent: `Codex`
- Last updated: `2026-03-13`

## Problem Statement

- Task: extend Symphony from a single issue-delivery worker into a squad-oriented orchestration layer with explicit roles, GitHub-facing job routing, and clearer human handoff.
- Current observed behavior before this change: Symphony handled `Ready` issues only, with one implementation path and no checked-in squad model for triage, PR review, or hygiene work.
- Why this is a real repo/code problem: the repo now relies on GitHub as its control plane, so the orchestration layer needs clearer roles, richer GitHub communication, and background maintenance workflows.

## Why This Matters

- User or gameplay impact: humans can now work through GitHub Issues and draft PRs without manually converting every issue into a branch/worktree/prompt flow.
- Maintenance / workflow / agent impact: squad roles make the orchestration model more legible, extensible, and safer to evolve.

## Scope

- In scope: checked-in squad charters and machine-readable job/schedule definitions.
- In scope: job routing for `implement_issue`, `triage_issue`, `review_pr`, and `hygiene_scan`.
- In scope: richer GitHub comments, local status reporting, and CLI support for explicit jobs.

## Non-Goals

- Not changing: no auto-merge.
- Not changing: no hosted/cloud worker requirement.
- Not changing: `workspace.base_branch` remains pinned to `agent-baseline`.

## Trusted Sources Of Truth

- Primary code/config/scripts:
  - `symphony/WORKFLOW.md`
  - `symphony/main.py`
  - `symphony/orchestrator.py`
  - `symphony/router.py`
  - `symphony/github_client.py`
  - `AGENTS.md`
  - `WORKFLOW.md`
- Validation scripts/tests/hooks:
  - `python -m unittest discover -s tests -p "test_symphony_*.py"`

## Existing Docs / Plans Trust Review

- Reviewed docs/plans:
  - `SYMPHONY_SPEC.md` - useful base context
  - `SYMPHONY_REPO_DELTA.md` - current repo adaptation
  - `docs/plans/active/2026-03-09-symphony-implementation.md` - current implementation history
  - `docs/plans/active/2026-03-12-symphony-local-server.md` - current worker behavior
- Conflicts with code/config/scripts:
  - none blocking after this implementation; docs were updated alongside code

## Affected Files / Directories

- Primary implementation paths:
  - `symphony/`
  - `symphony/squad/`
  - `tests/`
- Documentation:
  - `README.md`
  - `symphony/README.md`
  - `docs/index.md`
  - `ARCHITECTURE.md`

## Proposed Implementation Steps

1. Add checked-in squad definitions and machine-readable job/schedule files.
2. Refactor Symphony into a job router while preserving the existing implementation flow.
3. Add GitHub-facing triage, PR review, and hygiene behavior.
4. Extend local worker observability and CLI surfaces.
5. Validate with unit tests and dry-run-safe commands.

## Validation Plan

- Required automated checks:
  - `python -m unittest discover -s tests -p "test_symphony_*.py"`
- Required repo scripts:
  - none; this task changes Python orchestration code only
- Required manual smoke test:
  - not required for this repo-tooling-only change
- Live smoke:
  - start the local worker
  - confirm `status --verbose` shows active squad job fields
  - stop the worker cleanly

## Documentation Updates Required

- Update:
  - `README.md`
  - `symphony/README.md`
  - `docs/index.md`
  - `ARCHITECTURE.md`

## Risks / Rollback

- Main risks:
  - making routing logic too broad and noisy for real GitHub use
  - duplicate or repetitive GitHub comments
  - hygiene jobs being too aggressive
- Safe rollback approach:
  - revert the squad-related Python modules and `symphony/squad/` definitions on this feature branch

## Open Questions

- Whether the `Research` role should become a first-class routable job in a later phase.
- Whether PR review jobs should eventually post formal GitHub reviews instead of issue comments on PRs.
- Whether hygiene findings should gain more repo-specific checks beyond cleanup, stale docs, and validation attention.

## Completion Checklist

- [x] Checked-in squad definitions added under `symphony/squad/`
- [x] Symphony routing supports issue, PR, and scheduled jobs
- [x] Human-facing GitHub comment flow added for squad roles
- [x] Local status/CLI surface updated for squad jobs
- [x] Tests updated and passing
- [x] Documentation updated

## Final Outcome Summary

- What changed:
  - added a squad layer with functional roles, machine-readable jobs/schedules, and job routing for implementation, triage, PR review, and hygiene
  - preserved `agent-baseline` as the runtime base branch for Symphony issue worktrees
  - expanded local status and CLI support for job-specific execution and visibility
- Validation performed:
  - `python -m unittest discover -s tests -p "test_symphony_*.py"`
  - `python -m symphony.main --workflow symphony/WORKFLOW.md run-once --dry-run`
  - `python -m symphony.main --workflow symphony/WORKFLOW.md run-once --dry-run --job hygiene_scan`
  - live local worker start/status/stop smoke test
- Docs updated:
  - `README.md`
  - `symphony/README.md`
  - `docs/index.md`
  - `ARCHITECTURE.md`
- Remaining risks:
  - real GitHub behavior still needs live smoke testing for the new triage/review/hygiene jobs
