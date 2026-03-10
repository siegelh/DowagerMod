# Clean Worktree DLL Build

- Status: `in_progress`
- Owner / agent: `Codex`
- Last updated: `2026-03-10`

## Problem Statement

- Task: make the DLL build reproducible from a clean Symphony worktree.
- Current observed behavior: Symphony issue `#43` failed its required DLL validation in the clean worktree because `boost/preprocessor/debug/error.hpp` was missing.
- Why this is a real repo/code problem: the main repo can currently build only because certain required third-party headers exist locally but are ignored by git, so a clean worktree does not contain the real build inputs.

## Why This Matters

- User or gameplay impact: DLL issues cannot complete the validated draft-PR handoff until the clean-worktree build succeeds.
- Maintenance / workflow / agent impact: Symphony cannot safely rely on worktrees until tracked repo state is sufficient for the DLL gate.

## Scope

- In scope: identify required ignored files under `third_party/beyond-the-sword-sdk/CvGameCoreDLL` that are needed for a clean DLL build.
- In scope: track or explicitly unignore those required source inputs.
- In scope: prove the DLL gate from both the main repo and a clean worktree.

## Non-Goals

- Not changing: no gameplay code changes beyond the already-existing issue branch.
- Not changing: no broad restructuring of third-party dependencies unless required.
- Not changing: no sparse-checkout optimization work.

## Trusted Sources Of Truth

- Primary code/config/scripts:
  - `third_party/beyond-the-sword-sdk/.gitignore`
  - `third_party/beyond-the-sword-sdk/CvGameCoreDLL/Makefile`
  - `tools/test_gate.ps1`
  - `tools/build_civ4_dll.ps1`
  - live file comparison between `C:\DowagerMod` and `C:\sw\gh-43`
- Runtime entrypoints/import paths to verify:
  - clean DLL build in `third_party/beyond-the-sword-sdk/CvGameCoreDLL`
- Validation scripts/tests/hooks:
  - `.\tools\test_gate.ps1 -CheckDll`

## Existing Docs / Plans Trust Review

- Reviewed docs/plans:
  - `SYMPHONY_REPO_DELTA.md`
    - `trusted for this task`
  - `docs/plans/active/2026-03-10-symphony-pr-handoff.md`
    - `trusted for this task`
- Conflicts with code/config/scripts:
  - none; this task is fixing the repo state needed to satisfy the documented Symphony workflow

## Potentially Stale Or Conflicting Materials

- Item: relying on main-checkout local extras during DLL builds
  - Why it may be stale: clean worktrees do not inherit ignored local files.
  - What code/config overrode or verified it: live `#43` worktree validation failure.

## Affected Files / Directories

- Primary implementation paths:
  - `third_party/beyond-the-sword-sdk/.gitignore`
  - `third_party/beyond-the-sword-sdk/CvGameCoreDLL/Boost-1.32.0/include/boost/preprocessor/debug/`
  - `third_party/beyond-the-sword-sdk/CvGameCoreDLL/Boost-1.32.0/include/boost/spirit/debug/`
- Adjacent paths to inspect:
  - `tools/test_gate.ps1`
  - `tools/build_civ4_dll.ps1`
- Paths to avoid unless evidence requires them:
  - gameplay XML/Python files

## Assumptions That Need Human Confirmation

- Assumption: required third-party source headers should be tracked in git rather than restored by a separate bootstrap script.
  - Why it matters: it defines the reproducibility model for worktrees.
  - What changes if false: we would need a formal bootstrap step before DLL validation.

## Proposed Implementation Steps

1. Compare the main repo against a clean worktree under `third_party/beyond-the-sword-sdk/CvGameCoreDLL`.
2. Identify ignored-but-required source inputs versus ignorable build outputs.
3. Update ignore rules so required source headers can be tracked.
4. Add the required headers to git.
5. Run `.\tools\test_gate.ps1 -CheckDll` in the main repo.
6. Create a fresh clean worktree and run the same DLL gate there.
7. If both pass, rerun Symphony issue `#43`.

## Validation Plan

- Required automated checks:
  - `.\tools\test_gate.ps1 -CheckDll`
  - repeat in a fresh clean worktree
- Required repo scripts:
  - `.\tools\test_gate.ps1 -CheckDll`
- Required manual smoke test:
  - not for this repo-hardening step by itself
- Validation blocked or not yet runnable:
  - no blocker identified

## Documentation Updates Required

- Docs to update with the implementation:
  - `ARCHITECTURE.md` or `BUILDING_CVGAMECOREDLL.md` only if the tracked-input rule needs to be called out
- Docs/plans to mark stale, historical, or superseded:
  - none yet

## Risks / Rollback

- Main risks:
  - accidentally tracking build outputs instead of true source inputs
  - missing another required ignored input after the first fix
- Likely failure modes:
  - `Debug/` ignore patterns still suppress needed nested header folders
  - DLL gate reveals another hidden local dependency after the first missing-header fix
- Safe rollback approach:
  - revert the ignore-rule changes and untrack any newly added third-party files
- Paths that should not be touched during rollback:
  - gameplay issue worktrees except for rerun/retest

## Open Questions

- Are there any other required ignored third-party inputs besides the Boost debug headers?
- Should a later repo-hardening step explicitly audit all ignored files under `CvGameCoreDLL`?

## Completion Checklist

- [ ] Required ignored third-party source inputs were identified.
- [ ] Ignore rules were updated only as much as needed.
- [ ] Required files were tracked in git.
- [ ] `.\tools\test_gate.ps1 -CheckDll` passed in the main repo.
- [ ] The DLL gate also passed in a fresh clean worktree.
- [ ] Issue `#43` was unblocked and rerun if validation became reproducible.

## Final Outcome Summary

- What changed:
- Validation performed:
- Docs updated:
- Remaining risks:
- Follow-up tasks:
