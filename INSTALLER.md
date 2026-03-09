# Installer

This document describes the installer behavior as implemented now. If this file and `CoreFiles/install.py` disagree, trust `CoreFiles/install.py`.

## Canonical source

- Installer source of truth: `CoreFiles/install.py`
- Installer payload root: `CoreFiles/Sid Meier's Civilization IV Beyond the Sword`
- The repo mirror intentionally omits a few oversized stock archives that are not carried in git.

## What the installer does now

- Runs on Windows only.
- Prompts for the drive letter where the Steam install likely lives.
- Scans that drive for a path containing both:
  - `steamapps`
  - `Sid Meier's Civilization IV Beyond the Sword`
- Asks the user to confirm the discovered install path.
- Copies the mirrored payload from `CoreFiles/Sid Meier's Civilization IV Beyond the Sword` into the live install.
- Copies files only when the destination is missing or when source size/mtime differ.

## Important behavior

- Install is copy-based, not sync/prune-based.
- Deleting a file from the repo does not remove it from the live game install.
- That means stale files can survive in the live install until removed manually.
- The repo mirror is not a byte-for-byte stock installer image. Large stock archives such as `Assets0.fpk`, `Assets1.fpk`, `Assets2.fpk`, and `Art/Movies/Intros/intro.bik` are intentionally excluded from git.

## Important path caveat

- `CoreFiles/install.py` computes its payload source path from `sys.argv[0]` by stripping a fixed suffix length and then appending `Sid Meier's Civilization IV Beyond the Sword`.
- That means installer behavior depends on where the executable or script is launched from.
- The source file is authoritative, but direct invocation patterns should be checked against that path logic before relying on them.

## Secondary / historical packaging paths

These exist, but are not the default source of truth for current installer behavior:

- `CoreFiles/install_for_gui.py`
- `CoreFiles/install_working.py`
- `CoreFiles/setup.py`
- `install.spec`

Treat them as secondary or historical unless a task explicitly targets packaging cleanup.

## Recommended usage for future work

- Treat `CoreFiles/install.py` as the canonical installer implementation.
- If the task changes deploy behavior, update this file, `README.md`, and any affected runbooks in the same task.
- If packaging a new installer executable, verify the source-path assumption before shipping it.
