# Testing Workflow

## Goal

Catch XML and DLL regressions before manual install and game launch.

## Commands

Run from repo root.

1. Smart changed-file gate (daily default):

```powershell
.\tools\test_gate.ps1
```

2. Smart changed-file gate with DLL compile when needed:

```powershell
.\tools\test_gate.ps1 -CheckDll
```

3. XML-only full sweep:

```powershell
.\tools\test_xml.ps1 -All
```

4. Full gate (all XML + DLL build):

```powershell
.\tools\test_full.ps1
```

## What each command does

`test_gate.ps1`
- Runs XML validation against changed BTS XML files.
- If an XML schema file changed, it also validates all XML that reference that schema via `x-schema:...`.
- In default mode, skips DLL build for fast XML-focused feedback.
- With `-CheckDll`, compiles `CvGameCoreDLL.dll` only when DLL source files changed.
- DLL compile runs in non-destructive mode (`build_civ4_dll.ps1 -NoDeploy`).

`test_xml.ps1 -All`
- Validates all BTS XML files under:
- `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML`

`test_full.ps1`
- Always runs full XML validation and full DLL build.

## Failure behavior

- XML failures report file, line, column, and parser reason.
- Any XML validation failure fails the gate.
- Any DLL build failure fails the gate.

## Optional: enforce locally with pre-commit hook

1. Set repo hooks path once:

```powershell
git config core.hooksPath .githooks
```

2. Commit as usual. The hook runs `.\tools\test_gate.ps1` and blocks commit on failure.
