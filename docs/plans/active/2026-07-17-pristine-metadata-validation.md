# Pristine Metadata Validation

- Status: `complete`
- Owner / agent: Copilot
- Last updated: `2026-07-17`

## Problem Statement

- Task: Prevent the installer from restoring a corrupted pristine snapshot.
- Current observed behavior: Existing pristine folders are trusted without
  rechecking their file count or size.
- Why this is a real repo/code problem: A damaged baseline is mirrored into
  every live install and can surface later as multiplayer OOS.

## Scope

- Capture the known-good baseline as exact recursive file count and logical
  byte size.
- Validate a new capture after copy and every existing pristine before restore.
- Abort with actionable diagnostics on mismatch or unreadable files.
- Add focused temporary-directory tests and installer documentation.

## Non-Goals

- No per-file or whole-tree content hashes.
- Aggregate metadata is a fast sanity check, not proof of byte identity.
- No automatic deletion, repair, refresh, or tolerance for alternate builds.
- No changes to pristine/live mirror semantics.

## Trusted Sources Of Truth

- Installer runtime: `CoreFiles/install.py`.
- Known-good local pristine measured on 2026-07-17: `30,496` files and
  `3,677,850,103` logical bytes.
- Tests: `tools/tests/test_installer_pristine_validation.py` and
  `tools/tests/test_installer_restore_migration.py`.

## Proposed Implementation Steps

1. Add one-pass recursive count/size measurement with explicit read errors.
2. Require an exact baseline match before capture and before every restore.
3. Revalidate immediately after first-time capture.
4. Stage and validate refresh captures before replacing the current pristine.
5. Document the metadata-only guarantee and its same-size/offsetting-change
   limitation.
6. Validate on the parent branch, commit locally, then cherry-pick into the
   neutral-world-wonder branch.

## Validation Plan

- Focused installer tests.
- Full repository Python tests.
- `git diff --check`.
- Measure the known-good pristine with the same runtime helper.

## Risks / Rollback

- Alternate Steam branches/locales with different file sizes are rejected by
  design.
- Metadata checks cannot detect same-size mutations or offsetting size changes.
- Rollback is limited to the installer, tests, and related docs.

## Completion Checklist

- [x] Known-good metadata recorded.
- [x] Existing and newly captured pristine paths validated.
- [x] Restore is blocked on mismatch.
- [x] Focused tests and documentation added.
- [x] Parent and neutral-wonder local commits created.

## Final Outcome Summary

- What changed: Fast exact count/byte validation around pristine use.
- Validation performed: 22 focused installer tests and 253 full repository
  tests passed (10 skipped); packaged installer rebuilt and `--help` smoke
  passed; the real pristine matched in 13.22 seconds; independent review found
  no remaining significant issue.
- Docs updated: This plan and `INSTALLER.md`.
- Remaining risks: Same-size content edits require hashing and remain outside
  the approved metadata-only scope.
