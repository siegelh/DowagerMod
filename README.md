# DowagerMod

DowagerMod is a `Sid Meier's Civilization IV: Beyond the Sword` mod workspace built around an intentional mirrored install tree plus local XML, Python, DLL, art, and installer tooling.

## Start Here

- [docs/index.md](docs/index.md)
- [AGENTS.md](AGENTS.md)
- [WORKFLOW.md](WORKFLOW.md)
- [ARCHITECTURE.md](ARCHITECTURE.md)
- [INSTALLER.md](INSTALLER.md)
- [symphony/README.md](symphony/README.md) when working on the GitHub-backed agent orchestrator

## Main Working Roots

- BtS assets root:
  - `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets`
- DLL source:
  - `third_party/beyond-the-sword-sdk/CvGameCoreDLL`
- Tooling:
  - `tools/`

## Basic Commands

Run from repo root.

```powershell
.\tools\test_gate.ps1
.\tools\test_gate.ps1 -CheckDll
.\tools\test_full.ps1
.\tools\build_civ4_dll.ps1
```

See:

- [docs/TESTING_WORKFLOW.md](docs/TESTING_WORKFLOW.md)
- [docs/MANUAL_SMOKE_TESTS.md](docs/MANUAL_SMOKE_TESTS.md)
- [third_party/beyond-the-sword-sdk/BUILDING_CVGAMECOREDLL.md](third_party/beyond-the-sword-sdk/BUILDING_CVGAMECOREDLL.md)

## Install / Deploy

**For installing the mod (friends):** double-click `Install DowagerMod.bat`
at the repo root. Approve the UAC prompt. That's it.

**For mod developers / contributors:**

- Installer source: `CoreFiles/install.py`
- Built exe (committed): `CoreFiles/dist/DowagerMod-Installer/DowagerMod-Installer.exe`
- Build script: `tools\build_installer.ps1` (uses dedicated `.build_venv\`)
- Full design + troubleshooting: [INSTALLER.md](INSTALLER.md)

The installer uses a **wipe-and-restore** model: it captures a pristine
snapshot of the clean Civ4 install on first run, then every subsequent
install mirrors live back to pristine and overlays the mod payload. This
means deleting a file from the repo *does* remove it from the live
install — no cross-version drift.

## Repo Notes

- `CoreFiles/Sid Meier's Civilization IV Beyond the Sword` is an intentional mirror of the local game install.
- A few oversized stock archives are intentionally excluded from git and may be absent from the repo workspace.
- BtS is the default edit target. Base `Assets` and `Warlords` may still matter for inherited files, but they are not the default place to start editing.
- Historical plans, drafts, and dated debug notes now live under [docs/archive/](docs/archive/).
- Repo-local task aids live under [skills/](skills/).
- The repo now includes a local GitHub-backed orchestration tool under [symphony/](symphony/) for agent issue pickup, worktree execution, validation, and draft-PR handoff.
- Symphony now also supports a squad-style local workflow with explicit triage, implementation, PR review, and hygiene jobs routed through GitHub.
- Symphony can also run as a local background worker for a modding session via:
  - `.\tools\Start-Symphony.ps1`
  - `.\tools\Symphony-Status.ps1`
  - `.\tools\Stop-Symphony.ps1`
  - `.\tools\Cleanup-Symphony.ps1`
