# Agent-First Repo Hardening

- Status: `complete`
- Owner / agent: `Codex`
- Last updated: `2026-03-08`

## Problem Statement

- Task: harden repo guidance after a second independent pass found contradictions and missing operational detail.
- Current observed behavior: active docs broadly matched code, but stale authoritative docs, missing archive structure, missing installer/testing notes, and current worktree noise still risked confusing future agents.
- Why this is a real repo/code problem: this repo depends heavily on code-first navigation, and stale docs can send agents to the wrong paths or workflows.

## Why This Matters

- User or gameplay impact: safer edits, fewer wrong-path changes, fewer misleading install/build instructions.
- Maintenance / workflow / agent impact: cleaner cold-start guidance and less ambiguity around historical material.

## Scope

- In scope: active repo guidance, installer/testing docs, archive structure, stale-doc relocation, ignore rules.
- In scope: third-party DLL build notes and overhaul-process wording that directly conflicted with current guidance.

## Non-Goals

- Not changing: runtime XML, Python, or DLL mechanics.
- Not changing: live installer code behavior itself.

## Trusted Sources Of Truth

- Primary code/config/scripts:
  - `CoreFiles/install.py`
  - `tools/test_gate.ps1`
  - `tools/test_xml.ps1`
  - `tools/test_full.ps1`
  - `tools/build_civ4_dll.ps1`
  - BtS XML/Python trees
- Runtime entrypoints/import paths to verify:
  - `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/Python/EntryPoints/CvAppInterface.py`
  - `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/Python/Screens/CvMainInterface.py`
- Validation scripts/tests/hooks:
  - `.githooks/pre-commit`

## Existing Docs / Plans Trust Review

- Reviewed docs/plans:
  - `README.md`
  - `AGENTS.md`
  - `WORKFLOW.md`
  - `ARCHITECTURE.md`
  - `docs/index.md`
  - `docs/TESTING_WORKFLOW.md`
  - `docs/LEADER_OVERHAUL_PLAN_OF_RECORD.md`
  - `third_party/beyond-the-sword-sdk/BUILDING_CVGAMECOREDLL.md`
- Classification for each:
  - current guidance docs: `trusted for this task`
  - old root README and old DLL build note: `historical / verify before relying`
  - overhaul plan doc: `useful context only` until invocation wording was fixed

## Potentially Stale Or Conflicting Materials

- `README.md`
  - Why it may be stale: old installer/build instructions and outdated mandatory wording
  - What code/config overrode or verified it: `CoreFiles/install.py`, `tools/build_civ4_dll.ps1`, `tools/test_xml.ps1`
- `docs/LEADER_OVERHAUL_PLAN_OF_RECORD.md`
  - Why it may be stale: required strict README compliance
  - What code/config overrode or verified it: current workflow/docs trust model
- `third_party/beyond-the-sword-sdk/BUILDING_CVGAMECOREDLL.md`
  - Why it may be stale: described timestamped deploy behavior that no longer matches the build script
  - What code/config overrode or verified it: `tools/build_civ4_dll.ps1`

## Affected Files / Directories

- Primary implementation paths:
  - `AGENTS.md`
  - `WORKFLOW.md`
  - `ARCHITECTURE.md`
  - `README.md`
  - `INSTALLER.md`
  - `docs/index.md`
  - `docs/TESTING_WORKFLOW.md`
  - `docs/MANUAL_SMOKE_TESTS.md`
  - `docs/LEADER_OVERHAUL_PLAN_OF_RECORD.md`
  - `third_party/README.md`
  - `third_party/beyond-the-sword-sdk/BUILDING_CVGAMECOREDLL.md`
  - `.gitignore`
- Adjacent paths to inspect:
  - `docs/archive/`
  - `docs/plans/`
  - `skills/`
- Paths to avoid unless evidence requires them:
  - runtime XML/Python/DLL sources

## Assumptions That Need Human Confirmation

- Assumption: archived docs should move out of the main docs root now
  - Why it matters: changes navigation and future doc references
  - What changes if false: historical docs would stay in place with only labeling changes
- Assumption: the branch should carry the new agent-first docs as the working baseline
  - Why it matters: affects how aggressively current docs replace stale ones
  - What changes if false: some replacements might need to stay provisional

## Proposed Implementation Steps

1. Verify live entrypoints, imports, runtime paths, and active asset roots.
2. Confirm trusted sources and classify stale/conflicting materials in this area.
3. Update active guidance docs and add missing installer/testing runbooks.
4. Archive clearly historical docs and align references.
5. Tighten ignore rules for generated junk and summarize residual risks.

### Task-Specific Steps

1. Patch active guidance docs with second-pass findings.
2. Rewrite root README and add `INSTALLER.md`.
3. Add `docs/MANUAL_SMOKE_TESTS.md` and `docs/archive/README.md`.
4. Move historical plans/debug/ideas into `docs/archive/`.
5. Update third-party build notes and process docs to remove stale authority.

## Validation Plan

- Required automated checks:
  - none mandatory; docs-only and ignore-policy change
- Required repo scripts:
  - not applicable
- Required manual smoke test:
  - not applicable
- Validation blocked or not yet runnable:
  - no runtime code changed

## Documentation Updates Required

- Docs to update with the implementation:
  - active guidance docs, README, installer/testing docs
- Docs/plans to mark stale, historical, or superseded:
  - moved into `docs/archive/`
- `docs/index.md` updates needed:
  - yes
- `ARCHITECTURE.md` / `WORKFLOW.md` / runbook updates needed:
  - yes

## Risks / Rollback

- Main risks:
  - breaking references to moved archived docs
  - overstating installer behavior that is still partly packaging-dependent
- Likely failure modes:
  - forgotten links to moved archive files
  - guidance drifting again if stale docs remain in active root
- Safe rollback approach:
  - revert doc moves and doc edits together
- Paths that should not be touched during rollback:
  - runtime XML, Python, DLL source

## Open Questions

- Should the full mirrored stock tree eventually be normalized into tracked baseline on this branch?
- Should a future pass add a dedicated Python runtime/inheritance note once module-resolution behavior is proven?

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

- What changed: active repo guidance was updated, stale docs were archived, installer/testing docs were added, and ignore rules were tightened for generated artifacts.
- Validation performed: code/script re-read plus path verification; no runtime tests because implementation code did not change.
- Docs updated: yes
- Remaining risks: installer invocation path assumptions and Python inheritance behavior still need human/runtime confirmation.
- Follow-up tasks:
  - normalize the intentional install mirror baseline on this branch
  - decide whether to refresh legacy packaging helpers or archive them
