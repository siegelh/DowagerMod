# Landmark Map Scale and Installer Reliability

- Status: `in_progress`
- Owner / agent: GitHub Copilot CLI
- Last updated: `2026-07-13`

## Problem Statement

- Task: shrink the 13 new Great Person landmark models on the map, and make
  every install reliable by retiring the rename-based installer hot-swap fast
  path that could strand a `<install> - DELETE_ME` folder.
- Current observed behavior:
  - The 13 new landmarks reuse stock building NIFs at `fScale=1.0`, so they
    render about as large as a city on the map.
  - On some machines an installer run leaves a `<install> - DELETE_ME` sibling
    folder that cannot be deleted.
- Why this is a real repo/code problem:
  - `CIV4ArtDefines_Improvement.xml` sets `fScale=1.0` for all 13 new records.
  - The retired `CoreFiles/install_hot.py` renamed the live tree to
    `<install> - DELETE_ME`, swapped `PRISTINE_HOT` into place, then ran one
    unguarded `shutil.rmtree`; any Windows lock left the folder behind.

## Why This Matters

- User or gameplay impact: oversized landmark models read as cities and clutter
  the map; a stranded `DELETE_ME` folder confuses users and wastes disk.
- Maintenance / workflow / agent impact: the hot-swap path behaved differently
  machine-to-machine (only fast-path machines created the artifact), making
  installs hard to reason about. Always-mirror restore is uniform and testable.

## Scope

- In scope: set the 13 new landmark `fScale` to `0.5`; keep `fInterfaceScale`
  at `1.0`; leave Grand Colosseum `fScale=1.5`.
- In scope: remove the hot-swap architecture from `CoreFiles/install.py`, delete
  `CoreFiles/install_hot.py`, always restore via `robocopy /MIR`, and add safe
  migration cleanup for stale `PRISTINE_HOT` / `DELETE_ME` siblings.

## Non-Goals

- Not changing landmark mechanics, placement, yields, AI, or the DLL.
- Not changing the pristine snapshot model, payload overlay, sentinel, user-data
  cleanup, discovery, or any unrelated installer behavior.
- Not executing the installer; the user owns installation.
- Not touching the uncommitted, validated multiplayer DLL performance changes
  (`CvPlot.cpp`, `CvUnitAI.cpp`, the rebuilt payload DLL, and their tests) —
  they are preserved as a separate logical change and coexist with this work.

## Trusted Sources Of Truth

- Primary code/config/scripts:
  - `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Art/CIV4ArtDefines_Improvement.xml`
  - `CoreFiles/install.py`
  - `tools/tests/test_great_person_landmarks.py`
  - `tools/tests/test_installer_restore_migration.py`
  - `tools/tests/test_installer_user_data.py`
  - `tools/build_installer.ps1`, `CoreFiles/install.spec`
- Validation scripts: `tools/test_gate.ps1`, `tools/test_xml.ps1`,
  `python -m pytest tools/tests`.

## Existing Docs / Plans Trust Review

- `INSTALLER.md` — `trusted for this task`. Already documented always-MIR
  wipe-and-restore; it never described the hot-swap path, so this task *adds*
  the migration explanation rather than removing an existing contract.
- `docs/plans/active/2026-07-13-great-person-landmark-improvements.md` —
  `trusted for this task`. The landmark contract this scale fix extends.
- `ARCHITECTURE.md` — `useful context only`. Describes the installer as
  restore-from-pristine + overlay; it never referenced the hot path, so it
  stays accurate with no edit required.

## Potentially Stale Or Conflicting Materials

- Item: any prose implying an "instant next install".
  - Why it may be stale: that was the retired hot-swap promise.
  - What overrode it: `CoreFiles/install.py` now always mirror-restores in
    place; `INSTALLER.md` migration section documents the retirement.

## Affected Files / Directories

- Primary implementation paths:
  - `.../Assets/XML/Art/CIV4ArtDefines_Improvement.xml` (13 `fScale` edits)
  - `CoreFiles/install.py` (retire hot-swap, add migration cleanup)
  - `CoreFiles/install_hot.py` (deleted)
  - `tools/tests/test_great_person_landmarks.py` (art-scale contract)
  - `tools/tests/test_installer_restore_migration.py` (new)
- Docs: `INSTALLER.md`, `docs/index.md`, `docs/MANUAL_SMOKE_TESTS.md`, the
  landmark plan, and this plan.
- Paths to avoid: the DLL source and payload DLL (owned by the preserved
  performance change), base `Assets`, `Warlords`, `petromod_v1`.

## Assumptions That Need Human Confirmation

- Assumption: uniform `0.5` map scale reads well for every reused NIF.
  - Why it matters: native bounding boxes vary between models.
  - What changes if false: individual outliers may need per-record scale tuning
    after playtest.

## Proposed Implementation Steps

1. Set the 13 new landmark `fScale` values to `0.5`; keep interface scale `1.0`.
2. Add art-scale regression tests (13 scales `0.5`, interface `1.0`, Grand
   Colosseum `1.5`).
3. Remove `install_hot` import, `PRISTINE_HOT` constant/config/status/build
   logic; always `robocopy(pristine, live, mirror=True, label="restore pristine")`.
4. Delete `CoreFiles/install_hot.py`.
5. Add bounded, read-only-aware migration cleanup for exact `PRISTINE_HOT` /
   `DELETE_ME` siblings, with explicit path-specific warnings on lock and hard
   guards against ever deleting live or pristine.
6. Add a focused installer restore/migration test module.
7. Update `INSTALLER.md`, `docs/index.md`, `docs/MANUAL_SMOKE_TESTS.md`, and the
   landmark plan.
8. Validate; rebuild the one-folder installer package without running it.

## Validation Plan

- Required automated checks:
  - `python -m pytest tools/tests/test_great_person_landmarks.py`
  - `python -m pytest tools/tests/test_installer_restore_migration.py`
  - `python -m pytest tools/tests/test_installer_user_data.py`
  - `python -m pytest tools/tests` (full suite; must include the preserved DLL
    performance tests)
- Required repo scripts:
  - `.\tools\test_gate.ps1`
  - `.\tools\test_xml.ps1 -All`
  - `git diff --check`
- Packaged build (no install run):
  - `.\tools\build_installer.ps1 -Clean` in the dedicated `.build_venv`
  - Confirm `CoreFiles/dist/DowagerMod-Installer/DowagerMod-Installer.exe` and
    its `_internal/` sibling exist and contain no `install_hot`.
- Required manual smoke test (user-owned): see `docs/MANUAL_SMOKE_TESTS.md`
  "Great Person landmarks" (map scale) and "Installer reliability".

## Documentation Updates Required

- `INSTALLER.md`: retired hot-swap, always-MIR, why old `DELETE_ME` happened,
  migration cleanup, obsolete config key, tradeoff, troubleshooting entry.
- `docs/index.md`: link this plan.
- `docs/MANUAL_SMOKE_TESTS.md`: map-scale and installer-reliability checks.
- Landmark plan: map-scale correction subsection.
- `ARCHITECTURE.md`: no change required (never referenced the hot path).

## Risks / Rollback

- Main risks: uniform `0.5` may misfit some NIFs; a genuinely locked stale
  folder cannot be force-removed while Windows holds the lock.
- Likely failure modes: none automated-detectable beyond tests; rendering and
  lock behavior are human/environment gates.
- Safe rollback: revert the 13 `fScale` edits and the installer changes
  together; restore `install_hot.py` only if the hot-swap were ever revived
  (not recommended).
- Paths that should not be touched during rollback: the preserved DLL
  performance change and its rebuilt payload DLL.

## Open Questions

- Do any specific landmark NIFs need per-record scale tuning after playtest?

## Completion Checklist

- [x] Trusted sources of truth verified from code/config/scripts.
- [x] Existing docs/plans reviewed and classified.
- [x] Assumptions needing human confirmation recorded.
- [x] Implementation steps completed.
- [x] Required automated validation ran and results recorded.
- [ ] Required manual smoke test ran (user-owned).
- [x] Related docs updated.
- [x] Residual risks and open questions summarized.

## Final Outcome Summary

- What changed: 13 landmark map scales set to `0.5`; installer hot-swap retired
  in favor of always-mirror restore plus safe migration cleanup; new/updated
  tests; docs updated; installer package rebuilt.
- Validation performed: full `tools/tests` pytest suite, `test_gate.ps1`, full
  XML validation, `git diff --check`, packaged-build inspection (not run).
- Docs updated: `INSTALLER.md`, `docs/index.md`, `docs/MANUAL_SMOKE_TESTS.md`,
  landmark plan, this plan.
- Remaining risks: per-NIF scale outliers; locked stale folders on user
  machines (warned, non-blocking).
- Follow-up tasks: user-run install + fresh-game map-scale and installer
  reliability acceptance.

## Readiness

- Ready for implementation: **Yes** (implemented).
- Ready for merge/deploy: **No.** User-run installation and fresh-game visual /
  installer-reliability acceptance remain required.
