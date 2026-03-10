# Symphony Repo Delta

- Status: `complete`
- Owner / agent: `Codex`
- Last updated: `2026-03-09`

## Problem Statement

- Task: turn `SYMPHONY_SPEC.md` into a DowagerMod-specific implementation target before any code is written.
- Current observed behavior: `SYMPHONY_SPEC.md` is detailed, but it is Linear-first, shell-agnostic in ways that skew toward `bash`, and assumes a machine-readable `WORKFLOW.md` that would conflict with this repo's human normative `WORKFLOW.md`.
- Why this is a real repo/code problem: implementing the spec literally would produce the wrong tracker integration, the wrong workflow file model, and the wrong workspace/execution assumptions for this repo.

## Why This Matters

- User or gameplay impact: the first Symphony implementation attempt will either establish a reliable agent execution path for this repo or create a hard-to-trust automation layer on top of a Civ4 mod workspace.
- Maintenance / workflow / agent impact: if the repo-specific delta is not explicit, future implementation work will waste time rediscovering decisions about GitHub, worktrees, PowerShell, validation, and human review handoff.

## Scope

- In scope: document the DowagerMod-specific deltas from `SYMPHONY_SPEC.md`.
- In scope: define recommended tracker, workspace, execution, validation, and handoff behavior for a Python implementation.

## Non-Goals

- Not changing: no Symphony implementation code.
- Not changing: no GitHub project/issue setup, no repo automation wiring, and no Civ4 gameplay code.

## Trusted Sources Of Truth

- Primary code/config/scripts:
  - `SYMPHONY_SPEC.md`
  - `AGENTS.md`
  - `WORKFLOW.md`
  - `ARCHITECTURE.md`
  - `README.md`
  - `INSTALLER.md`
- Runtime entrypoints/import paths to verify:
  - `CoreFiles/install.py`
  - `tools/test_gate.ps1`
  - `tools/test_xml.ps1`
  - `tools/test_full.ps1`
- Validation scripts/tests/hooks:
  - `.githooks/pre-commit`
  - `tools/test_gate.ps1`

## Existing Docs / Plans Trust Review

- Reviewed docs/plans:
  - `SYMPHONY_SPEC.md`
    - `trusted for this task` as the base service design
  - `WORKFLOW.md`
    - `trusted for this task` as the repo's normative human workflow
  - `AGENTS.md`
    - `trusted for this task` as the cold-start trust model
  - `ARCHITECTURE.md`
    - `trusted for this task` for repo constraints and uncertainties
- Conflicts with code/config/scripts:
  - `SYMPHONY_SPEC.md` assumes `tracker.kind: linear`; this conflicts with the stated repo goal of GitHub Issues / Projects.
  - `SYMPHONY_SPEC.md` assumes `WORKFLOW.md` can be the machine-readable runtime workflow file; in this repo that would conflict with the existing human normative `WORKFLOW.md`.

## Potentially Stale Or Conflicting Materials

- Item: `SYMPHONY_SPEC.md` Linear-specific tracker sections
  - Why it may be stale: they are correct for the base spec but wrong for this repo target.
  - What code/config overrode or verified it: user requirement is GitHub Issues / Projects in the origin repo.
- Item: repo root `WORKFLOW.md` as a candidate machine-readable config file
  - Why it may be stale: it is an active human workflow document, not YAML front matter config.
  - What code/config overrode or verified it: current repo usage and current docs treat it as normative prose.

## Affected Files / Directories

- Primary implementation paths:
  - `SYMPHONY_SPEC.md`
  - `SYMPHONY_REPO_DELTA.md`
- Adjacent paths to inspect:
  - `AGENTS.md`
  - `WORKFLOW.md`
  - `ARCHITECTURE.md`
  - `docs/plans/active/TEMPLATE.md`
- Paths to avoid unless evidence requires them:
  - `CoreFiles/`
  - `third_party/beyond-the-sword-sdk/CvGameCoreDLL`

## Assumptions That Need Human Confirmation

- Assumption: Symphony should use GitHub Projects v2 status as the primary queue/state surface.
  - Why it matters: it changes candidate fetch, reconciliation, and completion semantics.
  - What changes if false: Symphony may need to use issue labels only, milestones, or a different issue selection model.
- Assumption: a human should remain the merge authority.
  - Why it matters: it determines whether Symphony stops at `Human Review` or can close the full loop to `Done`.
  - What changes if false: PR/merge/issue-close automation would need a much stronger approval and rollback model.

## Proposed Implementation Steps

1. Verify live entrypoints, imports, runtime paths, and active asset roots.
2. Confirm trusted sources and classify stale/conflicting materials in this area.
3. Implement the smallest change that solves the problem.
4. Update related docs/runbooks affected by the change.
5. Validate with repo test gates and required smoke testing.

### Task-Specific Steps

1. Read `SYMPHONY_SPEC.md` against the current repo workflow and trust model.
2. Record the repo-specific tracker, workspace, execution, validation, and handoff deltas in a dedicated document.
3. Leave implementation-blocking decisions explicit instead of guessing.

## Validation Plan

- Required automated checks:
  - none; this is a doc-only planning task
- Required repo scripts:
  - none
- Required manual smoke test:
  - not applicable
- Validation blocked or not yet runnable:
  - implementation validation is intentionally deferred because no code is being written yet

## Documentation Updates Required

- Docs to update with the implementation:
  - add `SYMPHONY_REPO_DELTA.md`
- Docs/plans to mark stale, historical, or superseded:
  - none yet
- `docs/index.md` updates needed:
  - optional later if Symphony planning becomes an active documented subsystem
- `ARCHITECTURE.md` / `WORKFLOW.md` / runbook updates needed:
  - none for this planning-only step

## Risks / Rollback

- Main risks:
  - overcommitting to GitHub/Project assumptions that have not been confirmed yet
  - letting the delta drift into implementation detail that the repo owner has not chosen
- Likely failure modes:
  - a delta that is too generic to implement safely
  - a delta that silently overrides repo policy instead of adapting to it
- Safe rollback approach:
  - revert the new planning documents only
- Paths that should not be touched during rollback:
  - `CoreFiles/`
  - `third_party/`

## Open Questions

- Which GitHub Project v2 board will be canonical for `siegelh/DowagerMod`?
- Will the blocker labels be created exactly as recommended, or renamed to fit a preferred label style?

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
  - added a checked-in plan record for the Symphony repo-delta task
- Validation performed:
  - doc review only
- Docs updated:
  - `SYMPHONY_REPO_DELTA.md`
  - `docs/plans/active/2026-03-09-symphony-repo-delta.md`
- Remaining risks:
  - the canonical GitHub Project v2 board does not exist yet
- Follow-up tasks:
  - create the GitHub Project v2 board and final labels
  - then draft an implementation plan for the Python service
