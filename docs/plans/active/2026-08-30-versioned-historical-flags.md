# Versioned Historical Civilization Flags

- Status: `complete`
- Owner / agent: GitHub Copilot CLI
- Last updated: `2026-08-30`

## Problem Statement

- Task: preserve the approved 59 historical flags and make their production
  pipeline reproducible for future maintainers and CLIs.
- Current observed behavior: corrected zero-alpha DXT3 flags render correctly
  in the user's installed smoke test, but their masters and generator were
  session-local.
- Why this is a real repo/code problem: generated DDS files alone cannot be
  safely revised, audited, or reproduced.

## Scope

- Version and document 59 approved masters, provenance, and licensing.
- Add deterministic single/all/check/review tooling and original-design
  recovery metadata.
- Commit tooling/history first and generated runtime adoption second, then push
  both commits.

## Non-Goals

- No in-game flag-generation selector.
- No archive of rejected drafts or generated review HTML.
- No fabricated copies of 16 stock assets unavailable as loose files.

## Trusted Sources Of Truth

- `CIV4CivilizationInfos.xml` and `CIV4ArtDefines_Civilization.xml`.
- `tools/flags/manifest.json` after reconciliation with live XML.
- `tools/test_gate.ps1` and focused flag regression tests.
- Installed Civ4 rendering for final visual behavior.

## Existing Docs / Plans Trust Review

- `WORKFLOW.md`, `AGENTS.md`, and `docs/index.md`: trusted for this task.
- Session research/viewer artifacts: useful source material only; bulky
  generated outputs are not repository truth.
- Previous full-color flag plan: historical implementation context; superseded
  by this reproducible delivery plan.

## Affected Files / Directories

- `tools/flags/`
- `tools/tests/test_flag_pipeline.py`
- `tools/tests/test_flag_contract_fullcolor.py`
- `tools/tests/test_unique_civilization_flags.py`
- `docs/FLAG_PIPELINE.md`, `docs/index.md`, `AGENTS.md`
- Live BtS civilization art XML and 59 runtime DDS paths.

## Assumptions Confirmed By Human

- Preserve two meaningful generations: original and historical-v1.
- Original binary duplication is unnecessary if rollback/recovery is clearly
  documented.
- Push both commits after validation.

## Proposed Implementation Steps

1. Import exactly 59 approved high-resolution masters.
2. Normalize the manifest, research, citations, provenance, and licensing.
3. Port deterministic fixed-color DXT3 generation and temporary review output.
4. Record original recovery through Git baseline, Warlords mirrors, or pristine
   install.
5. Add focused contracts and documentation.
6. Prove a clean byte-for-byte rebuild of all 59.
7. Commit pipeline/history, then production assets/XML/contracts.
8. Push both commits and verify the remote branch head.

## Validation Plan

- Focused pipeline and production flag pytest files.
- `python .\tools\flags\build_flags.py --check`
- `.\tools\test_gate.ps1`
- `.\tools\test_full.ps1` if practical after the focused and gate checks.
- `git diff --check`
- Exact staged-content and two-commit review.
- User already completed a successful installed visual smoke test of the
  corrected zero-alpha production files.

## Documentation Updates Required

- Add the authoritative flag pipeline runbook.
- Add docs index and AGENTS orientation entries.
- Keep this plan updated with final validation and commit hashes.

## Risks / Rollback

- Repository growth from 59 masters is approximately 22.6 MB.
- ShareAlike-derived masters require preserved attribution/license metadata.
- Normal viewers misrepresent zero-alpha DDS files as transparent.
- Roll back the production adoption commit to restore original XML/runtime
  state; use the baseline/history manifest for individual recovery.

## Completion Checklist

- [x] Trusted runtime paths and mappings verified.
- [x] 59 approved masters imported with stable names.
- [x] Original recovery inventory reconciled as 38 Git / 5 Warlords / 16 packed.
- [x] Tooling and documentation tests pass.
- [x] All 59 deterministic outputs match approved runtime bytes.
- [x] Repository gates pass.
- [x] Two-commit delivery structured; remote push verification is recorded in
  the task handoff.

## Final Outcome Summary

- Repository-owned masters, metadata, encoder, transactional builder, review
  generator, original recovery inventory, tests, and docs are implemented.
- All 59 masters reproduce the installed-approved production DDS bytes.
- Focused flag contracts, the changed-file gate, and the broad XML/roster/DLL
  gate pass.
- Tooling/source/history commit:
  `c7457bf` (`Add reproducible historical flag pipeline`).
- Production adoption is the immediate child commit:
  `Adopt historical full-color civilization flags`.
