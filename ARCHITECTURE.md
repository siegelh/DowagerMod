# Architecture

This document describes the repository as implemented now. It is intentionally code-first. If this file and the code disagree, trust the code.

## System Overview

### Confirmed from code/config

- This repo is a `Sid Meier's Civilization IV: Beyond the Sword` mod workspace, not a web/service application.
- `CoreFiles/Sid Meier's Civilization IV Beyond the Sword` is an intentional mirror of the local game install and the payload copied by the installer.
- The default modding target is the BtS assets root: `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets`.
- The main implementation layers are XML gameplay/data under `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML`, Python runtime/UI under `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/Python`, custom DLL source under `third_party/beyond-the-sword-sdk/CvGameCoreDLL`, and local installer/build/test tooling under `CoreFiles/install.py` and `tools/`.
- Repo-side development automation now also includes a local Python orchestration tool under `symphony/`. It is not part of the Civ4 runtime; it exists to drive GitHub-backed agent work on this repository.
- Symphony now has a checked-in squad layer under `symphony/squad/` that defines functional roles (`Lead`, `Implementer`, `Reviewer`, `Research`, `Triage`, `Hygiene`) and job routing over GitHub Issues, PRs, and scheduled hygiene work.
- The repo also includes the **AI Leader Chatter** subsystem: a Python 3 sidecar at `tools/chatter/` that calls Azure Foundry (GPT-5.4-mini, OpenAI Responses API) on diplomatic events, and a game-side hook at `CoreFiles/.../Beyond the Sword/Assets/Python/Chatter/CvLeaderChatter.py` that elects a single broadcaster per event and routes generated lines through the engine's native chat channel via a small DLL binding on `CyMessageControl::sendChat`. The sidecar is repo-only and **not** included in the friend-facing installer payload — chatter only fires in games where at least one connected human has a working sidecar+key configured locally. See `docs/CHATTER_OVERVIEW.md` for the design and `docs/CHATTER_RUNBOOK.md` for the operator flow.
- The mirror also contains base `Assets`, `Warlords`, stock scenario mods, binaries, and media for installer completeness. Those mirrored files exist on purpose, but they are not all default edit targets.
- A few oversized stock archives are intentionally excluded from git, so the repo mirror should be treated as operationally complete for mod work, not as a byte-for-byte stock backup.

### Inferred but likely

- The BtS tree is the primary gameplay override, while some missing Python entrypoints may still be inherited from the base `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Assets` tree at runtime.

### Human guidance

- The repo owner's current working assumption is "BtS overlay plus inherited base files," but that has not been fully proven from code/config alone.

## Main Components / Modules

### Confirmed from code/config

- XML rules/content live primarily in `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Buildings/CIV4BuildingInfos.xml`, `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/GameInfo/CIV4CorporationInfo.xml`, `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Civilizations/CIV4LeaderHeadInfos.xml`, and `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/PythonCallbackDefines.xml`.
- Python event/runtime code lives primarily in `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/Python/CvEventManager.py`, `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/Python/CvArtMasterpieceSystem.py`, and `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/Python/CvArtMasterpieceData.py`.
- Python UI/screen code lives primarily in `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/Python/EntryPoints/CvAppInterface.py`, `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/Python/EntryPoints/CvScreensInterface.py`, `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/Python/EntryPoints/CvScreenUtilsInterface.py`, `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/Python/Screens/CvIndustryAdvisor.py`, and `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/Python/Screens/CvArtAdvisor.py`.
- Custom DLL behavior is most visible in `third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvCity.cpp`, `third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvInfos.cpp`, and `third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvGameTextMgr.cpp`.
- Generator/patch tooling lives in `tools/generate_art_masterpieces.py`, `tools/apply_supply_chain_overhaul.py`, `tools/apply_industry_wave2.py`, and `tools/rebuild_industry_buttons_v2.py`.

### Inferred but likely

- The mod's distinctive current systems are the industry/corporation supply-chain layer and the Art Masterpieces layer.

### Unknown / requires human confirmation

- Whether there are other major custom gameplay systems implemented mainly in DLL/XML that have not yet been documented separately.

## Runtime Entrypoints

### Confirmed from code/config

- `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/Python/EntryPoints/CvAppInterface.py` is the C++ app-entry bridge. `preGameStart()` calls `CvScreensInterface.showMainInterface()`.
- `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/Python/EntryPoints/CvScreensInterface.py` imports and instantiates the major screens and advisors.
- `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/Python/Screens/CvMainInterface.py` is only a loader stub. It dynamically imports the real HUD implementation from `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/Art/Leaderheads/new/petromod_v1/Assets/Python/Screens/CvMainInterface.py`.
- `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/Python/EntryPoints/CvScreenUtilsInterface.py` composes `CvIndustryScreenUtils` and `CvArtScreenUtils` with the default screen utils.
- `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/Python/Screens/CvIndustryAdvisor.py` defines screen id `4999`.
- `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/Python/Screens/CvArtAdvisor.py` defines screen id `5000`.
- `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/Python/CvEventManager.py` wires live runtime hooks for the Art Masterpiece system on update, load, game start, begin-player-turn, and building-built events.
- `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/PythonCallbackDefines.xml` leaves the visible `USE_*_CALLBACK` flags at `0`.

### Inferred but likely

- The custom Industry and Art advisor screens are opened from HUD buttons defined inside the vendored `petromod_v1` `CvMainInterface.py`, not from `CvScreensInterface.py` directly.
- Because many Python callback flags are disabled, the mod appears to rely more on DLL logic plus `CvEventManager.py` than on Python gameplay callbacks in `CvGameInterface.py`.
- The live Python path likely falls back to `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Assets/Python` for missing modules such as `EntryPoints/CvEventInterface.py` and `CvScreenUtils.py`.

### Unknown / requires human confirmation

- The exact Civ4 Python module resolution order in this workspace.
- Whether any additional live entrypoints still exist under `petromod_v1` beyond the HUD file that the loader imports.
- Whether `CvGameInterface.py` can ever safely be relied on without first resolving how `CvGameInterfaceFile.py` is supplied at runtime.

## Runtime / Data Flow

### Confirmed from code/config

1. Civ4 engine enters Python through `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/Python/EntryPoints/CvAppInterface.py`.
2. `preGameStart()` preloads some UI and calls `CvScreensInterface.showMainInterface()`.
3. `CvScreensInterface.py` constructs the main HUD object from `CvMainInterface`, which then defers to the `petromod_v1` implementation.
4. Screen input/update/close calls are routed through `CvScreenUtilsInterface.py`, which gives custom Industry and Art screens a chance to consume events before default handling.
5. Core gameplay data comes from XML and custom DLL readers in `third_party/beyond-the-sword-sdk/CvGameCoreDLL`.
6. `CvEventManager.py` adds Python-side runtime behavior, most clearly for Art Masterpieces.
7. `CvAppInterface.onSave()` and `onLoad()` pass a Python blob through the event interface, while the Art system also stores state in `CyGame().getScriptData()`.

### Inferred but likely

- Industry gameplay resolution is mostly XML + DLL, while the Python advisor is a read/visualization layer over that data.
- The Art system is a mixed Python/XML system: XML provides bonuses/buildings/text/art hooks, Python owns selection, ownership, and extra-happiness reconciliation.

### Unknown / requires human confirmation

- Whether any other custom systems use save-time Python serialization or `ScriptData` in the same way.

## Frontend / Backend / Service Boundaries

### Confirmed from code/config

- There is no separate backend service, API server, database, or frontend web app.
- There is now a repo-local automation service implementation under `symphony/`, but it is a developer tool, not a gameplay/runtime backend.
- "Frontend" in this repo means in-game Python screens plus 2D/3D assets under `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/Art`.
- "Backend" means Civ4 engine behavior driven by XML plus the custom `CvGameCoreDLL.dll`.
- All runtime code executes inside the Civ4 process.

### Inferred but likely

- `petromod_v1` is effectively a vendored UI dependency rather than a clean module boundary.

### Unknown / requires human confirmation

- Whether the HUD should remain vendored or be moved into the main BtS Python tree.

## Storage / State / Persistence

### Confirmed from code/config

- Static content is file-based: XML, Python, text XML, art, audio, and DLL binaries.
- Runtime game state is primarily Civ4 savegame state handled by the engine/DLL.
- `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/Python/CvArtMasterpieceSystem.py` stores its state inside `CyGame().getScriptData()` using `__ARTSYS_BEGIN__` / `__ARTSYS_END__` markers.
- `CvArtMasterpieceSystem.py` persists claimed pieces, per-player ownership, and an applied happiness offset.
- `tools/build_civ4_dll.ps1` backs up the active `CvGameCoreDLL.dll` in `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets` before replacing it.
- `CoreFiles/install.py` restores the live install from the pristine snapshot, overlays the repo mirror, and removes stale mod files that no longer exist in the repo payload.

### Inferred but likely

- The live install can still retain stale user-data/cache files if they are outside the installer cleanup allowlist, but stale files inside the game install are pruned by the pristine-restore step.

### Unknown / requires human confirmation

- Whether any non-art custom systems also depend on hidden file leftovers in the live install.

## External Integrations

### Confirmed from code/config

- `CoreFiles/install.py` scans a user-selected Windows drive for `steamapps\\...\\Sid Meier's Civilization IV Beyond the Sword`.
- `CoreFiles/install.py` computes its source mirror path from `sys.argv[0]` using a fixed suffix strip. That means packaging or invocation location matters to installer behavior.
- `tools/build_civ4_dll.ps1` depends on a local Visual Studio 2022 install and auto-detects known Civ4 SDK toolkit layouts, with `-Civ4SdkRoot` available for overrides.
- `tools/generate_art_masterpieces.py` uses `requests` and `PIL` and queries Wikidata over HTTP.
- `tools/rebuild_industry_buttons_v2.py` reads art that already exists inside the repo mirror, including imported subtrees such as `Assets/Art/BTG` and `Assets/Art/Caveman2Cosmos`.

### Inferred but likely

- The actual play/deploy target is a local Steam install, not a packaged distribution artifact.

### Unknown / requires human confirmation

- Whether `CoreFiles/install_for_gui.py`, `CoreFiles/install_working.py`, `CoreFiles/setup.py`, and `install.spec` are still part of an active packaging workflow.

## Build / Test / Deploy Structure

### Confirmed from code/config

- `tools/test_gate.ps1` is the main local gate.
- `tools/test_xml.ps1` validates the BtS XML tree and defaults to changed-file validation using git diff.
- `tools/test_full.ps1` runs the full gate (`-All`).
- `.githooks/pre-commit` runs `tools/test_gate.ps1`.
- `tools/test_gate.ps1 -CheckDll` is required for DLL source changes; it builds and deploys the repo-mirror DLL when DLL source files changed.
- `tools/build_civ4_dll.ps1` builds the DLL from `third_party/beyond-the-sword-sdk/CvGameCoreDLL` and deploys it to the BtS assets folder unless `-NoDeploy` is used.
- `CoreFiles/install.py` restores the live game tree from pristine, then overlays the mirrored game tree under `CoreFiles/Sid Meier's Civilization IV Beyond the Sword`.
- No repo CI configuration is present under a root `.github/` directory.
- `symphony/main.py` provides the current local CLI slice for GitHub issue pickup, worktree creation, one-turn Codex execution, repo-native validation, and draft-PR handoff using `symphony/WORKFLOW.md`.
- `symphony/main.py` now also provides a local `serve` mode so Symphony can run as a background polling worker on the modding machine.
- `symphony/orchestrator.py`, `symphony/router.py`, `symphony/role_prompt_builder.py`, and `symphony/squad_registry.py` now implement the squad-oriented job model on top of the original delivery flow.

### Inferred but likely

- The real quality gates are local XML schema validation, local DLL compile, and manual in-game smoke testing.
- The current branch may contain broad untracked mirror content, so git-based changed-file validation can widen unexpectedly until the branch baseline is normalized.
- Symphony can now enforce the repo-native gate before handoff for DLL or BtS XML changes, but manual gameplay smoke testing remains a human step.
- Symphony is currently designed as a local worker, not a hosted service. GitHub is the control plane; the Windows modding machine is the execution environment.
- Symphony now treats GitHub as the visible collaboration surface for:
  - issue triage
  - issue implementation
  - PR review summaries
  - hygiene issue creation

### Unknown / requires human confirmation

- None at the policy level. Repo guidance now treats a manual smoke test as mandatory for gameplay changes; the remaining open question is whether that minimum smoke path should become more detailed over time.

### Proposed working smoke-test path

- Run `.\tools\test_gate.ps1` after BtS XML changes, `.\tools\test_gate.ps1 -CheckDll` after DLL source changes, and widen to `.\tools\test_full.ps1` when the change is broad.
- Copy/install the updated files into the live game tree.
- Launch the mod and confirm it reaches the main menu without XML or Python error popups.
- Load a representative save or start a quick single-player game.
- Open the impacted screen or advisor if relevant.
- Exercise the changed mechanic, unit, building, or art reference at least once.
- End one turn.
- If the task touched save-state, serialization, or persistent Python state, save and reload once.

## Known Inconsistencies Or Transitional Areas

### Confirmed from code/config

- The authoritative editable DLL source is `third_party/beyond-the-sword-sdk/CvGameCoreDLL`.
- The BtS Python tree is not self-contained. `EntryPoints/CvEventInterface.py` and `CvScreenUtils.py` are present in the base `Assets` tree but not in the BtS tree, while BtS modules still import them.
- `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/Python/EntryPoints/CvGameInterface.py` imports `CvGameInterfaceFile`, but the only `CvGameInterfaceFile.py` present in the repo mirror is under `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Warlords/Assets/Python/EntryPoints`.
- `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/Python/Screens/CvMainInterface.py` still defers to `Assets/Art/Leaderheads/new/petromod_v1/.../CvMainInterface.py`.
- `tools/apply_supply_chain_overhaul.py` still patches base `Assets`, BtS, and `Warlords` paths, even though test tooling and current guidance focus on BtS-first edits.
- `tools/apply_industry_wave2.py` imports the supply-chain patch base module and also writes to both BtS and non-BtS roots.
- The branch can still contain broad untracked mirror content, which affects git-based changed-file validation.

### Inferred but likely

- `petromod_v1` is legacy-looking material that remains live because the HUD loader still points to it.
- Base `Assets` and `Warlords` remain part of the intentional install mirror, but they are not the default development target.

### Human guidance

- Current owner guidance is to focus on BtS and not intentionally keep base `Assets` or `Warlords` in sync unless a task proves it is necessary.
- Current owner guidance is to treat `third_party/beyond-the-sword-sdk/CvGameCoreDLL` as the only DLL build source and not recreate a duplicate source tree under `CoreFiles/`.
- Current owner guidance is to tolerate `petromod_v1` as a live dependency for now rather than force an immediate HUD migration.
- Current Symphony guidance is to treat issue delivery, PR review, issue triage, and repo hygiene as distinct future job types rather than one monolithic background agent.
- Current Symphony guidance is now implemented as a squad model where one heavy implementation job runs at a time, while lighter triage/review/hygiene jobs are routed separately.
- Current Symphony worktrees are intentionally persistent after PR creation and merge so humans can still rebuild/test candidate branches locally until explicit cleanup policy is added.

## What Appears Legacy Or Transitional

- `CoreFiles/install_for_gui.py`
- `CoreFiles/install_working.py`
- `CoreFiles/setup.py`
- `install.spec`
- `traits_enhanced.py`
- `merge_traits_all.py`
- Archived plans, ideas, and dated debug notes under `docs/archive/`
- `CoreFiles/dist`
- `tmp`
- `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/Art/Leaderheads/new/petromod_v1` as a legacy-looking but live dependency

These items may still be useful, but they should not be treated as primary architecture truth without checking the current code first.

## Where Future Agents Should Look

- XML gameplay/content changes: `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML`
- Python event hooks: `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/Python/CvEventManager.py`
- Custom screens: `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/Python/Screens`
- Screen dispatch: `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/Python/EntryPoints/CvScreensInterface.py` and `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/Python/EntryPoints/CvScreenUtilsInterface.py`
- HUD/main interface issues: `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/Python/Screens/CvMainInterface.py` and `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/Art/Leaderheads/new/petromod_v1/Assets/Python/Screens/CvMainInterface.py`
- DLL-backed XML capability work: `third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvInfos.cpp`, `CvCity.cpp`, `CvGameTextMgr.cpp`
- Installer/deploy behavior: `CoreFiles/install.py`
- Validation behavior: `tools/test_gate.ps1`, `tools/test_xml.ps1`, `tools/build_civ4_dll.ps1`
- Repo automation: `symphony/main.py`, `symphony/WORKFLOW.md`, `SYMPHONY_SPEC.md`, `SYMPHONY_REPO_DELTA.md`
- Local Symphony worker controls: `tools/Start-Symphony.ps1`, `tools/Symphony-Status.ps1`, `tools/Stop-Symphony.ps1`
- Local Symphony cleanup control: `tools/Cleanup-Symphony.ps1`
- Planned Symphony job types: issue delivery first, then PR review, issue triage, and hygiene/audit jobs
- Generated Art Masterpiece content: `tools/generate_art_masterpieces.py`, `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/Python/CvArtMasterpieceData.py`, `docs/art_masterpiece_sources.csv`
- Industry content generation: `tools/apply_supply_chain_overhaul.py`, `tools/apply_industry_wave2.py`, `tools/rebuild_industry_buttons_v2.py`

## What Not To Assume

- Do not assume docs under `docs/` are current unless they match code/scripts.
- Do not assume the BtS Python tree is fully self-contained.
- Do not assume deleting `petromod_v1` is safe while `CvMainInterface.py` still imports it.
- Do not assume base `Assets` and `Warlords` are irrelevant just because BtS is the primary target.
- Do not assume generated scripts only affect the BtS tree; some still touch other asset roots.
- Do not assume copied files are live until the repo mirror has been installed or manually copied into the live game install.
- Do not assume `CoreFiles/install.py` can be run from any arbitrary path without checking its source-path logic.
- Do not assume a repo CI pipeline exists.

## Questions That Should Be Resolved Before Large Refactors

- Should the live HUD code eventually be moved out of `Assets/Art/Leaderheads/new/petromod_v1` into the main BtS Python tree, or is leaving it in place acceptable long-term?
- Should the BtS tree eventually be made fully self-contained for Python entrypoints and support files, or should the inherited-base-file model remain intentional?
- Should `tools/apply_supply_chain_overhaul.py` and `tools/apply_industry_wave2.py` stop patching base `Assets` and `Warlords` by default?
- Which installer/package path is still supported besides `CoreFiles/install.py`, if any?
- Should any non-game-install user-data folders besides the current cleanup set be pruned during deployment?
