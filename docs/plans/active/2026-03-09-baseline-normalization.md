# Baseline Normalization For Agent-First Branch

- Status: `in_progress`
- Owner / agent: Codex
- Last updated: `2026-03-09`

## Problem Statement

- Task:
  - Convert the current playable feature branch into a clean, committed baseline suitable for future agent-first development.
- Current observed behavior:
  - The branch contains a mix of:
    - playable tracked mod changes
    - large intentional untracked mirror content under `CoreFiles/Sid Meier's Civilization IV Beyond the Sword`
    - new agent-first docs and archive moves
    - tracked temp artifacts that should not remain in the baseline
- Why this is a real repo/code problem:
  - Future agent work will remain noisy and error-prone until the intentional baseline is fully committed and temporary clutter is removed.

## Why This Matters

- User or gameplay impact:
  - Preserves the current playable state before further agentic refactors or feature work.
- Maintenance / workflow / agent impact:
  - Produces a clean branch tip that can serve as the new long-lived agent-first base.

## Scope

- In scope:
  - Split current work into clean commits for:
    - playable-state changes
    - mirror baseline backfill
    - agent-first scaffolding
  - Remove tracked temp artifacts from the baseline.
  - Create a new long-lived branch from the cleaned baseline.
- In scope:
  - Push the updated precursor branch before switching.

## Non-Goals

- Not changing:
  - gameplay logic beyond the already-present playable-state files
  - major refactors to Python inheritance or `petromod_v1`
- Not changing:
  - unrelated user feature work outside the identified baseline buckets

## Trusted Sources Of Truth

- Primary code/config/scripts:
  - `git status --short`
  - `git diff --name-only`
  - `git ls-files --others --exclude-standard`
  - `tools/test_gate.ps1`
- Runtime entrypoints/import paths to verify:
  - `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Art/CIV4ArtDefines_Leaderhead.xml`
  - `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/Art/Leaderheads/DowagerCountess/`
- Validation scripts/tests/hooks:
  - `.\tools\test_gate.ps1`
  - `.githooks/pre-commit`

## Existing Docs / Plans Trust Review

- Reviewed docs/plans:
  - `AGENTS.md`
  - `WORKFLOW.md`
  - `ARCHITECTURE.md`
  - `docs/index.md`
  - `docs/plans/active/TEMPLATE.md`
- Classification for each:
  - `trusted for this task`
- Conflicts with code/config/scripts:
  - none identified for the baseline-normalization workflow itself

## Potentially Stale Or Conflicting Materials

- Item:
  - `tmp/leaderhead_previews/dowager_grid.png`
  - Why it may be stale:
    - tracked preview artifact, not source
  - What code/config overrode or verified it:
    - current `.gitignore` and workflow treat `tmp/` as generated noise
- Item:
  - `tmp_test.dds`
  - Why it may be stale:
    - tracked temp asset with no known runtime linkage
  - What code/config overrode or verified it:
    - no live docs or scripts point to it

## Affected Files / Directories

- Primary implementation paths:
  - `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Art/CIV4ArtDefines_Leaderhead.xml`
  - `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/Art/Leaderheads/DowagerCountess/`
  - `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/`
  - repo guidance docs and archive paths
- Adjacent paths to inspect:
  - `tmp/leaderhead_previews/`
  - `tmp_test.dds`
- Paths to avoid unless evidence requires them:
  - unrelated gameplay systems outside the current playable-state delta

## Assumptions That Need Human Confirmation

- Assumption:
  - the DowagerCountess leaderhead files and art-define XML belong in the playable-state baseline
  - Why it matters:
    - determines what goes into the first commit
  - What changes if false:
    - they should be separated from the baseline and handled as later feature work
- Assumption:
  - the intentional full mirror should be tracked as committed baseline content
  - Why it matters:
    - determines whether the large untracked `CoreFiles` set becomes a commit
  - What changes if false:
    - the mirror remains intentionally untracked and agent noise persists

## Proposed Implementation Steps

1. Tag the current branch tip before new commits.
2. Validate and commit the playable-state changes plus removal of tracked temp artifacts.
3. Commit the intentional full mirror backfill as a separate mechanical baseline commit.
4. Commit the agent-first scaffolding and archive changes as a separate governance commit.
5. Verify a clean worktree, push the precursor branch, create `agent-baseline`, and push it.

## Validation Plan

- Required automated checks:
  - `.\tools\test_gate.ps1`
- Required manual smoke test:
  - not run in this normalization task unless specifically requested; this task is primarily commit hygiene and branch setup
- Validation blocked or not yet runnable:
  - none

## Documentation Updates Required

- Docs to update with the implementation:
  - none beyond the already-prepared scaffolding set
- Docs/plans to mark stale, historical, or superseded:
  - none further in this task
- `docs/index.md` updates needed:
  - none beyond current state
- `ARCHITECTURE.md` / `WORKFLOW.md` / runbook updates needed:
  - none expected

## Risks / Rollback

- Main risks:
  - mixing unrelated feature work into the baseline commits
  - accidentally omitting intentional baseline files from the mirror commit
- Likely failure modes:
  - dirty worktree remains after commits
  - large mirror commit is incomplete
- Safe rollback approach:
  - use the pre-baseline tag to return to the exact starting point
- Paths that should not be touched during rollback:
  - unrelated user changes outside the committed buckets

## Open Questions

- Should the final baseline tag also be pushed to origin?
- Should a later pass normalize line endings to reduce CRLF warnings?

## Completion Checklist

- [ ] Trusted sources of truth were verified from code/config/scripts.
- [ ] Existing docs/plans in this area were reviewed and classified for trustworthiness.
- [ ] Assumptions needing human confirmation were recorded.
- [ ] Implementation steps were completed or explicitly deferred.
- [ ] Required validation ran and results were recorded.
- [ ] Tracked temp artifacts were removed from the baseline.
- [ ] The precursor branch was pushed after normalization.
- [ ] The `agent-baseline` branch was created from the clean tip.

## Final Outcome Summary

- What changed:
- Validation performed:
- Docs updated:
- Remaining risks:
- Follow-up tasks:
