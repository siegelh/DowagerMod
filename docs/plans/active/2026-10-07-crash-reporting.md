# One-Command Crash Reporting

- Status: `complete; manual runtime acceptance pending`
- Owner / agent: GitHub Copilot CLI
- Last updated: `2026-10-07`

## Problem Statement

- Task: Create a post-crash collector for the thirteen-leader expansion branch.
- Current observed behavior: crash reports arrive without a reproducible save,
  exact build identity, installed-payload comparison, exception stack, or logs.
- Why this is a real repo/code problem: the existing DLL handler records only
  exception code/address, while evidence is spread across Steam, Documents,
  LocalAppData, Windows events, Git, and Civ4 logs.

## Why This Matters

- User or gameplay impact: multiplayer crashes cannot be isolated efficiently.
- Maintenance / workflow / agent impact: every incident currently requires a
  bespoke evidence request before investigation can begin.

## Scope

- Add `Report DowagerMod Crash.bat` and `tools\report_crash.ps1`.
- Add crash-only bounded minidumps, automatic GitHub issue creation, a manual
  issue template, focused tests, and operator documentation.

## Non-Goals

- Do not replace normal Steam launch behavior.
- Do not enable continuous generic/city tracing or upload saves/dumps silently.

## Trusted Sources Of Truth

- Primary code/config/scripts:
  `CvGameCoreDLL.cpp`, `CoreFiles/install.py`,
  `tools/multiplayer_manifest.ps1`.
- Runtime entrypoints/import paths to verify: loaded BtS DLL, Windows Documents
  known folder, `%LOCALAPPDATA%\DowagerMod`, and configured Steam install.
- Validation scripts/tests/hooks:
  `tools/test_gate.ps1 -CheckDll`, focused PowerShell test, `git diff --check`.

## Existing Docs / Plans Trust Review

- `docs/DLL_TRACING_WORKFLOW.md`: trusted for current trace toggles and log path.
- `docs/GLYPH_DIAGNOSTICS.md`: trusted for LocalAppData diagnostic conventions.
- `docs/archive/debug/*`: historical context only.
- Conflict: current crash logging records an address but no minidump stack.

## Affected Files / Directories

- Primary implementation paths:
  `CvGameCoreDLL.cpp`, `Makefile.project`, `tools/report_crash.ps1`,
  root batch launcher, `.github/ISSUE_TEMPLATE`.
- Adjacent paths: docs index, manual smoke tests, tracing runbook.
- Avoid: live Steam installation, generated crash bundles, saves, and `tmp`.

## Assumptions That Need Human Confirmation

- Confirmed: crash-only `MiniDumpNormal` evidence is approved.
- Confirmed: automatic issue creation uses authenticated `gh`, with fallback.
- Confirmed: reports live outside Git under LocalAppData.

## Proposed Implementation Steps

1. Add crash-only dump creation and bounded retention.
2. Add post-crash autosave discovery, sanitization, evidence reconciliation,
   ZIP packaging, and issue-body generation.
3. Add `gh` creation plus browser fallback and exact attachment instructions.
4. Add launcher, issue template, tests, and runbooks.
5. Run focused and DLL validation without creating a live test issue.

## Validation Plan

- Required automated checks:
  synthetic autosave ranking, redaction, retention, fake `gh`, ZIP manifest.
- Required repo scripts:
  `.\tools\test_gate.ps1 -CheckDll`.
- Required manual smoke test:
  run the collector after a representative Steam crash and attach the ZIP.
- Validation blocked or not yet runnable:
  intentionally inducing a live Civ4 crash is not part of automated validation.

## Documentation Updates Required

- Add `docs/CRASH_REPORTING.md`.
- Update tracing, docs index, and manual smoke-test workflow.

## Risks / Rollback

- Exception state may be corrupted; dump creation must never suppress the crash.
- Saves and dumps can contain player/game/process data; no automatic upload.
- Remove the collector/launcher and minidump call to roll back; gameplay data
  and XML are unaffected.

## Completion Checklist

- [x] Trusted sources of truth were verified from code/config/scripts.
- [x] Human policy decisions were confirmed.
- [x] Implementation steps completed.
- [x] Required validation completed.
- [x] Related docs updated.
- [ ] Manual Steam crash acceptance performed or explicitly deferred.

## Final Outcome Summary

- What changed: added bounded crash-only minidumps, one-command evidence
  collection, autosave selection, privacy redaction, GitHub issue creation and
  fallback, launcher, issue template, tests, and runbooks.
- Validation performed: focused synthetic workflow and browser fallback tests,
  real configured-path dry run, DLL source/payload hash parity, PowerShell
  syntax, `git diff --check`, and `tools\test_gate.ps1 -CheckDll`.
- Docs updated: crash-reporting runbook, tracing workflow, docs index, manual
  smoke tests, and discovery context.
- Remaining risks: intentional live Civ4 crash/minidump and real GitHub ZIP
  attachment acceptance remain manual; live install currently does not include
  this newly rebuilt payload.
