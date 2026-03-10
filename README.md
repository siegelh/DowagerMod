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

- Canonical installer source: `CoreFiles/install.py`
- Installer behavior and packaging caveats: [INSTALLER.md](INSTALLER.md)
- Important: deployment is copy-based and does not prune deleted files from the live game install.

## Repo Notes

- `CoreFiles/Sid Meier's Civilization IV Beyond the Sword` is an intentional mirror of the local game install.
- A few oversized stock archives are intentionally excluded from git and may be absent from the repo workspace.
- BtS is the default edit target. Base `Assets` and `Warlords` may still matter for inherited files, but they are not the default place to start editing.
- Historical plans, drafts, and dated debug notes now live under [docs/archive/](docs/archive/).
- Repo-local task aids live under [skills/](skills/).
- The repo now includes a local GitHub-backed orchestration tool under [symphony/](symphony/) for agent issue pickup and worktree execution.
