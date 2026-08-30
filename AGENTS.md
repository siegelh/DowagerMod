# AGENTS.md

## Repository Purpose

- This repo is a source workspace for a `Sid Meier's Civilization IV: Beyond the Sword` mod.
- `CoreFiles/Sid Meier's Civilization IV Beyond the Sword` is an intentional mirror of the local game install and the payload copied by the installer.
- The default gameplay edit target is the BtS assets root:
  - `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets`
- The main implementation surfaces are:
  - XML game data
  - Python event and screen code
  - custom `CvGameCoreDLL` source
  - local install/build/test/install scripts

## Trust Model / Source Of Truth Hierarchy

1. Running code, imports, configs, tests, scripts, and CI are primary truth.
2. Existing docs are useful but must be corroborated if they conflict with code.
3. Historical plans, specs, notes, and artifacts are not authoritative unless they are still reflected in implementation.
4. If docs and code disagree, follow the current code or script and call out the mismatch explicitly.
5. This repo has local scripts and hooks, but no visible CI configuration. Treat the scripts and hook setup as the active gate.

## Primary Truth Paths

- Main XML target:
  - `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML`
- Main Python target:
  - `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/Python`
- DLL source:
  - `third_party/beyond-the-sword-sdk/CvGameCoreDLL`
- Test/build scripts:
  - `tools/test_gate.ps1`
  - `tools/test_xml.ps1`
  - `tools/test_full.ps1`
  - `tools/build_civ4_dll.ps1`
- Canonical installer source:
  - `CoreFiles/install.py`

## Key Docs To Read First

- `README.md`
- `docs/index.md`
- `WORKFLOW.md`
- `ARCHITECTURE.md`
- `INSTALLER.md` when deploy/package behavior matters
- `docs/TESTING_WORKFLOW.md`
- `docs/MANUAL_SMOKE_TESTS.md` for gameplay validation
- `docs/DLL_TRACING_WORKFLOW.md` when touching DLL tracing or debugging
- `docs/CIV4_UNIT_ART_CRASH_PLAYBOOK.md` when touching unit art
- `docs/FLAG_PIPELINE.md` when touching civilization flags
- `docs/LEADER_OVERHAUL_PLAN_OF_RECORD.md` only for leader/civ overhaul tasks

## Docs And Skills Layout

- `docs/index.md` is the docs table of contents and trust map.
- `WORKFLOW.md` is the normative repo workflow for task execution.
- `docs/plans/active/` is the standard location for checked-in task plans for non-trivial work.
- `docs/archive/` holds historical plans, ideas, and dated debug notes.
- `skills/` holds repo-local task aids. These are workflow references, not runtime truth.

## How To Get Oriented Quickly

1. Read this file and `docs/index.md`.
2. Run `git status --short` before planning.
3. Identify whether the task is mainly XML, Python, DLL, art, installer, tooling, or docs.
4. Inspect the live implementation path before editing:
   - BtS XML first
   - BtS Python callbacks and screens
   - DLL hooks and XML schema support
   - `tools/` for actual validation and build behavior
5. If a BtS Python import target is missing, check the mirrored base tree next:
   - `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Assets/Python`
6. Search for actual imports, call sites, and entrypoints before trusting older prose.
7. If a path looks suspicious, verify that it exists on disk before assuming it is live.

## Important Repo Realities

- The install mirror under `CoreFiles/Sid Meier's Civilization IV Beyond the Sword` is intentional. Do not assume everything inside it is equally relevant to the current task.
- A few oversized stock archives are intentionally excluded from git. Their absence in the repo mirror is not itself a mod change.
- The current branch may still show many untracked stock files in the mirror. Review `git status --short` early and do not treat every untracked file as intentional new work.
- BtS is the default edit target. Do not update base `Assets` or `Warlords` unless the task proves they matter.
- Current working assumption: runtime behaves as a BtS overlay plus some inherited base Python support files, not as a fully self-contained BtS Python tree.
- `CoreFiles/install.py` is the canonical installer source. It uses a wipe-and-restore model with a per-machine pristine snapshot — see `INSTALLER.md` for design.
- The committed installer .exe lives at `CoreFiles/dist/DowagerMod-Installer/DowagerMod-Installer.exe` (built via `tools/build_installer.ps1` from `CoreFiles/install.spec`). The friend-facing launcher `Install DowagerMod.bat` at repo root self-elevates and runs the .exe.
- The .exe must be built in one-folder PyInstaller mode (DLLs as siblings of the .exe). One-file mode triggers Windows Application Control blocks on locked-down machines.
- Builds must use the dedicated `.build_venv/` (gitignored) with only `pyinstaller` + `tqdm`. Building from Anaconda or system Python pulls hostile hooks and takes 15+ minutes.
- The installer maintains a pristine snapshot at `<install_dir> - PRISTINE` (sibling of the live game install). Per-machine state is persisted at `%LOCALAPPDATA%\DowagerMod\config.json`. Pristine is captured once from a clean Steam install and never goes stale (BTS is on Steam's frozen `original_release_unsupported` branch).
- The installer also nukes `Documents\My Games\Beyond the Sword\` (preserving `Saves/` and `CivilizationIV.ini`) and forces `DisableCaching = 1` in the .ini, to prevent stale XML cache from shadowing mod changes.
- `traits_enhanced.py` and `merge_traits_all.py` are legacy workflow files, not default entrypoints.
- `CoreFiles/dist`, `tmp`, backup DLLs, and large imported art folders are not primary sources of truth.
- `petromod_v1` is legacy-looking content, but it is still a live HUD dependency because `Beyond the Sword/Assets/Python/Screens/CvMainInterface.py` imports its `CvMainInterface.py`.
- Leave `petromod_v1` alone unless the task explicitly touches the HUD or main interface cleanup.
- `third_party/beyond-the-sword-sdk/CvGameCoreDLL` is the authoritative DLL source for builds.
- The changed-file test gate uses git diff plus untracked files. Noisy worktrees can widen validation scope unexpectedly.
- Civilization flag masters, mappings, provenance, licensing, and deterministic
  DXT3 tooling live under `tools/flags/`. Read `docs/FLAG_PIPELINE.md` before
  editing a flag. Civ4 fixed-color flags intentionally encode zero DXT3 alpha
  at every mip even though ordinary viewers may display them as transparent.

## Repo-Local Skills

- Repo-local skill packages live under:
  - `skills/civ-leader-overhaul-architect`
  - `skills/detailed-overhaul-v2`
- Use them as task-specific workflow references when the task matches their scope.
- Do not treat them as runtime or architecture truth; they are implementation aids.

## External Import Sources

- The following external directories may be read as asset/reference libraries:
  - `C:\Users\Harrison\Downloads\civ4mods-code`
  - `C:\Users\Harrison\Downloads\BTG_237`
  - `C:\Users\Harrison\Downloads\Caveman2Cosmos_v43`
- They are not part of this repo's source of truth.
- Use them for art imports first.
- Use them for code ideas second; prefer mining them for patterns or concepts rather than copying implementation directly unless the task explicitly calls for it.
- If you import content from them, copy it into the repo workspace first.
- Do not leave game XML or Python pointing at those external absolute paths.

## Planning Expectations

- Inspect the current implementation before proposing changes.
- Keep plans grounded in files that exist now, not in old plans or intended future structure.
- For small tasks, inspect and then edit directly.
- For larger tasks, name the runtime path you are changing and the validation you will run.
- For non-trivial tasks, create or update a checked-in plan doc under `docs/plans/active/` using `YYYY-MM-DD-short-slug.md`.
- Use `docs/plans/active/TEMPLATE.md` as the starting point for new plans.
- If the task is a leader/civ overhaul, use the current overhaul rules doc and any matching repo-local skill, but validate every mechanic against live XML/DLL support.

## Validation Expectations

- After editing any XML under:
  - `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML`
  run:
  - `.\tools\test_gate.ps1`
- After editing DLL source under:
  - `third_party/beyond-the-sword-sdk/CvGameCoreDLL`
  run:
  - `.\tools\test_gate.ps1`
- `tools/test_xml.ps1` validates the BtS XML tree by default; it is not a compatibility-copy sweep.
- Use `.\tools\test_gate.ps1 -CheckDll` when XML work may also need DLL compile coverage.
- Use `.\tools\test_xml.ps1 -All` or `.\tools\test_full.ps1` when the task needs a broader sweep.
- Do not report XML or DLL work as complete until the gate passes.
- If the gate cannot be run, stop and say so clearly.
- There is no visible automated gameplay test suite. If only schema validation or DLL compile was run, say that explicitly.
- Manual smoke testing is required for gameplay changes. Use `docs/MANUAL_SMOKE_TESTS.md`.
- If manual smoke testing was not run, say that explicitly.

## Safe Editing Rules

- Edit the BtS tree first unless the task clearly proves another location is required.
- Do not update base `Assets` or `Warlords` blindly.
- If a BtS Python file imports something that only exists in the base `Assets` mirror, document that dependency instead of silently assuming the BtS tree is self-contained.
- Do not edit generated outputs in `CoreFiles/dist`, `tmp`, or backup DLLs unless the task specifically targets them.
- Be cautious in large art-import areas; verify what is actually referenced before changing or copying files.
- Be cautious with generator scripts that still write across BtS, base `Assets`, and `Warlords`; inspect their target paths before running them.
- Do not regenerate large XML/text/art payloads unless the task is specifically about the generator pipeline.
- Do not delete historical docs or imported assets just because they look stale unless the user asks.
- If you import external assets, copy them into repo-controlled paths and then point XML at the copied files.
- If you change behavior that invalidates a current runbook or doc, update that doc in the same task when practical.

## When Docs And Code Disagree

- Prefer the current script, import path, config, XML schema, or call site.
- Record the mismatch in your response.
- Update the affected doc when practical, or recommend the exact doc change needed.
- Do not blend stale plans with live code into a false narrative.

## When To Stop And Mark Uncertainty

- You cannot identify the live entrypoint or active asset path.
- Docs and code conflict and no executable path shows which one wins.
- A file imports or references a path that no longer exists.
- It is unclear whether a change belongs only in BtS or also in a compatibility copy.
- The installer path matters and `CoreFiles/install.py` is not enough to answer the question safely.
- Required validation cannot be run.

## Useful Secondary Paths

- Legacy trait workflow files:
  - `traits_enhanced.py`
  - `merge_traits_all.py`
- Trait content staging folder:
  - `traits/`
- Treat these as legacy tooling unless the task explicitly targets them.
