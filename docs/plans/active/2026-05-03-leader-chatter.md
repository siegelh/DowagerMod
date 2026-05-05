# Plan: AI Leader Chatter via Azure Foundry

**Branch:** `agent-baseline-leader-chatter` (off `agent-baseline-fix-venice`).
**Status (2026-05-04):** v1.1 in progress. Chunked addMessage display path
implemented; BACKSTABBED + GOLDEN_AGE triggers wired; lifecycle scripts
(uninstall, key-keep on re-run) added. Awaiting in-game smoke test on
laptop, then push for desktop validation, then PR.

## Goal

Add an optional cosmetic feature that makes computer-controlled
civilizations exchange short, AI-generated, in-character lines on notable
diplomatic events. Lines are produced by Azure Foundry (GPT-5.4-mini, OpenAI
Responses API) via a small Python 3 sidecar process running locally on the
key holder's machine. Lines are routed through the engine's native chat
channel so all connected MP players see the same text.

Cosmetic only — zero gameplay impact, zero save-game state writes.

## Approach (one paragraph)

Civ4 ships Python 2.4 and cannot make HTTPS calls, so we run an
out-of-process Python 3 sidecar (`tools/chatter/`). The game and sidecar
communicate via JSON files in the user's
`Documents\My Games\Beyond the Sword\Logs\DowagerMod\chatter\` directory.
On a trigger, every connected client runs a deterministic capable-elector
election (lowest-id human with a fresh local sidecar heartbeat) — exactly
ONE machine writes a request, the sidecar calls Foundry, and the response
is broadcast via `CyMessageControl().sendChat()` (a small new DLL Python
binding). Multi-line exchanges are generated in a single API call (one-shot
script) and queued on the elector's machine to fire 5-10 seconds apart, so
the back-and-forth feels live. Capability is advertised across clients via
`sendModNetMessage` so every client agrees on who is the elector.

## Affected paths

### New files
- `tools/chatter/` (sidecar package: daemon, prompts, azure_client,
  circuit, spool, state, config, check_no_secrets, README, SPEC, tests)
- `tools/Setup-Chatter.ps1` / `Start-Chatter.ps1` / `Stop-Chatter.ps1` /
  `Chatter-Status.ps1`
- `CoreFiles/.../Beyond the Sword/Assets/Python/Chatter/CvLeaderChatter.py`
  (game-side module, Py 2.4-safe)
- `CoreFiles/.../Beyond the Sword/Assets/Python/Chatter/__init__.py`
- `docs/CHATTER_OVERVIEW.md`, `docs/CHATTER_RUNBOOK.md`

### Modified files
- `third_party/beyond-the-sword-sdk/CvGameCoreDLL/CyMessageControl.h`
  (declare `sendChat`)
- `third_party/beyond-the-sword-sdk/CvGameCoreDLL/CyMessageControl.cpp`
  (implementation)
- `third_party/beyond-the-sword-sdk/CvGameCoreDLL/CyMessageControlInterface.cpp`
  (`.def("sendChat", ...)`)
- `CoreFiles/.../Beyond the Sword/Assets/CvGameCoreDLL.dll` (rebuilt)
- `CoreFiles/.../Beyond the Sword/Assets/Python/CvEventManager.py`
  (1 import + 14 hook call sites)
- `docs/index.md`, `docs/MANUAL_SMOKE_TESTS.md`, `ARCHITECTURE.md`
  (cross-references)

## Validation completed

- `tools/chatter/tests/`: 31 unit + 2 e2e tests passing.
- `tools/test_gate.ps1 -CheckDll`: PASS (DLL builds cleanly with new
  binding).
- Pre-flight A (76 real Foundry calls during design): refusal rate
  3% directed / 0% broadcast / 0% one-shot multi-turn; ~1s median latency;
  in-character output across 17+ leaders and 14 trigger types.
- Pre-flight B (in-game test of `sendChat` Python binding + display
  options): completed; chunked `sendModNetMessage` + `addMessage` render
  path adopted as v1.1 production display.

## Validation pending (user)

- Manual smoke test matrix from `docs/MANUAL_SMOKE_TESTS.md`:
  1. SP DoW chat appears (with leader portrait, no elector prefix)
  2. Multi-turn pacing feels live
  3. Save/reload no-replay
  4. Sidecar killed mid-game, no errors
  5. No sidecar at all, no errors
  6. **2-client MP one-call invariant** (the critical MP test)
- New trigger smoke: WorldBuilder a Golden Age for an AI civ; WorldBuilder
  a Friendly→DoW to confirm BACKSTABBED replaces DECLARE_WAR.
- Lifecycle script smoke on the laptop:
  - Re-run `Setup-Chatter.ps1`, confirm "(unchanged)" for the API key.
  - `Setup-Chatter.ps1 -RegisterScheduledTask`, confirm task created.
  - `Uninstall-Chatter.ps1`, confirm task removed + daemon stopped + config
    preserved.
  - `Uninstall-Chatter.ps1 -RemoveConfig -Force`, confirm config gone.
- Desktop dry run after push: `git pull`, run `Setup-Chatter.ps1` (or
  pull updated key with Enter-to-keep), launch Civ4, verify lines render
  the same way.

## Assumptions

- BtS Python supports Python 2.5+ syntax (verified — `CvGlyphDiagnostics.py`
  uses conditional expressions, so our use is safe).
- The user's API key stays in `%LOCALAPPDATA%\DowagerMod\chatter\config.json`
  with restrictive ACLs and is never committed, never installed, never
  snapshotted by the installer (verified: installer only copies the BtS
  payload, not `tools/` and not LOCALAPPDATA).
- Chatter is acceptable as a key-holder-only feature for v1; friends
  installing the mod don't need an API key.
- Save games remain byte-identical to vanilla (no `getScriptData` writes
  in the chatter path — verified by code review).
- The `agent-baseline-fix-venice` branch will be merged into
  `agent-baseline` later; this feature branch will rebase onto the new
  `agent-baseline` head before PR (near-fast-forward).
- Push to remote is the user's job, never autopilot's (per user
  instruction; respected throughout).

## Unresolved / deferred

- **Watchdog/supervisor for sidecar.** Deferred to v1.2. Auto-spawn
  on `onGameStart` provides the practical equivalent for v1.1: if the
  sidecar dies, next game start re-spawns it.
- **VASSAL_FORCED, VASSAL_ACCEPTED triggers.** Trigger templates exist
  in the sidecar; `onVassalState` hook signature verified, but
  distinguishing forced (war-time surrender) vs accepted (peaceful)
  surrender requires extra state inspection. Deferred to v1.2.
- **Wonder racer detection** for directed-mode WONDER_BUILT lines.
  Deferred to v1.2; v1.1 always uses broadcast mode for wonders.

## Documentation updates landed

- New: `docs/CHATTER_OVERVIEW.md`, `docs/CHATTER_RUNBOOK.md`,
  `tools/chatter/README.md`, `tools/chatter/SPEC.md`.
- Updated: `docs/index.md` (added both Current entries),
  `docs/MANUAL_SMOKE_TESTS.md` (added chatter checklist),
  `ARCHITECTURE.md` (System Overview mention).
- v1.1 update: runbook gained "Updating endpoint or API key" and
  "Uninstalling the sidecar" sections; "Multi-machine" expanded into a
  copy-pasteable checklist; trigger list updated with BACKSTABBED and
  GOLDEN_AGE; chunked addMessage display documented in overview.

## Commits on this branch

1. `f986b1512` — chatter: spike sendChat Python binding + onChat probe
   (Pre-flight B). DLL change + probe.
2. `486de06f7` — chatter: P0 sidecar skeleton + setup/start/stop scripts
   + tests. 20 files, 2244 insertions.
3. `04e5c8c88` — chatter: P1+P2+P3 game-side module + CvEventManager
   wiring. 3 files, 1089 insertions.
4. `10937df2b` — chatter: P4+P5 polish + docs (fallback canned lines,
   no-elector diag, run/test gate clean). 11 files, 503 insertions /
   125 deletions.

## Next steps

1. User runs the manual smoke matrix from `docs/MANUAL_SMOKE_TESTS.md`
   (laptop) plus the new BACKSTABBED + GOLDEN_AGE trigger spot-checks.
2. User flips `_DEBUG_HELLO_*` flags to `False` in `CvLeaderChatter.py`
   if they were left True for the smoke test.
3. User commits + pushes.
4. Desktop: `git pull`, run `Setup-Chatter.ps1` once (Enter to keep
   key on existing installs), play.
5. When `agent-baseline-fix-venice` lands in `agent-baseline`, rebase
   `agent-baseline-leader-chatter` onto the new head (near-fast-forward).
6. Open PR against `agent-baseline`.
7. After merge, autopilot can remove the `tmp/chatter_smoke*.py`
   pre-flight scripts and move this plan doc to `docs/archive/plans/`.
