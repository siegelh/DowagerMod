# DowagerMod Leader Chatter — Overview

**Status:** v1, in active development (branch `agent-baseline-leader-chatter`).

## What it is

An optional cosmetic feature that has computer-controlled civilizations in
Sid Meier's Civilization IV: Beyond the Sword exchange short, AI-generated
in-character lines on notable diplomatic events. Lines come from Azure
Foundry (GPT-5.4-mini, OpenAI Responses API) via a small local Python 3
sidecar process.

Examples of what you might see in chat during a game:

```
Victoria: Mr. Lincoln, your republic shall find that the Crown's patience
          is refined, but its displeasure is most industriously dreadful.
Lincoln:  Madam, your cannon smoke may cloud the air, yet this republic
          has weathered thicker fogs than Victorian manners ever produced.
Victoria: Then brace yourself, Mr. Lincoln; Britannia has thickened her fog
          with steel, and your prairie republic shall cough upon it most
          unbecomingly.
```

(Real output from `tools/chatter/tests/test_e2e.py` against the live endpoint.)

## How it works

```
[Civ4 game]                            [Sidecar (Python 3)]
trigger event (DoW etc.)
   │
   ▼
CvLeaderChatter.py                     chatter_daemon.py
  - elect "chatter elector"            - watch spool/req-*.json
  - if elector & not on cooldown:      - call Azure Foundry
      write spool/req-*.json           - parse multi-line JSON if requested
                                       - write spool/resp-*.json
  - poll spool/resp-*.json
  - queue lines with 5-10s spacing
  - on each tick:
      if line due & game not paused
      & speaker still alive:
          send line as chunked sendModNetMessage
          stream (CHATTER_LINE_MAGIC)
                                       │
                                       ▼
                                 Every client (incl. elector)
                                 reassembles chunks in
                                 onModNetMessage and renders
                                 locally via CyInterface().addMessage
                                 with the speaker's leader portrait
                                 and civ color (no chat-channel
                                 elector-name prefix).
```

Key architectural points:

- **Civ4 Python is 2.4-era.** It cannot make HTTPS calls or run the modern
  `openai` SDK. Hence the out-of-process Python 3 sidecar.
- **The game and sidecar communicate via JSON files** in
  `Documents\My Games\Beyond the Sword\Logs\DowagerMod\chatter\`.
  See `tools/chatter/SPEC.md` for the schema.
- **Multiplayer-safe via "single elector" pattern.** When a trigger fires,
  every connected client runs the same elector election (deterministic).
  Exactly ONE machine writes a request, calls the API, and broadcasts the
  result. See "Multiplayer model" below.
- **Real-time pacing.** Multi-line exchanges are generated in a single API
  call (one-shot script) and queued on the elector's machine. Each line
  fires 5-10 seconds after the previous so the back-and-forth feels live.
- **Chunked broadcast + local render.** Lines are streamed as a sequence
  of `sendModNetMessage(CHATTER_LINE_MAGIC, ...)` chunks (8 ASCII bytes
  per chunk). Receiving clients reassemble in `onModNetMessage` and
  render locally via `CyInterface().addMessage` with the leader's
  portrait and civ color. The chat channel is bypassed entirely so
  there is no `[ElectorName]:` prefix.

## Distribution model — who needs what

The chat only happens **in games where at least one connected human player
has a working sidecar**. By default that means **only games you are in**
(since you are the key holder). Friends who install DowagerMod via the
installer get the game-side hooks but no sidecar — chatter just doesn't
fire in their games unless they also configure their own sidecar.

| Component                       | Friends get? | Where it lives          |
|---------------------------------|--------------|-------------------------|
| Custom DLL (`sendChat` binding) | ✅ Yes       | `<install>\Beyond the Sword\Assets\CvGameCoreDLL.dll` |
| `Chatter\CvLeaderChatter.py`    | ✅ Yes       | `<install>\Beyond the Sword\Assets\Python\Chatter\` |
| `CvEventManager.py` (with hooks)| ✅ Yes       | `<install>\Beyond the Sword\Assets\Python\` |
| Sidecar (`tools/chatter/`)      | ❌ No        | Repo only — not installer payload |
| API key / `.env`                | ❌ Never     | `<repo>\.env` on key holder's machine only |

## Multiplayer model

Civ4 MP runs in lockstep — every connected client executes the same
Python. A naive trigger handler would fire on N machines = N parallel API
calls + N different generated lines = split-brain (each player sees
different text).

We solve this with a **deterministic capable-elector election**:

1. **Capability advertisement.** On `onGameStart` and `onLoadGame`, every
   client checks for a fresh local sidecar (config file present + PID
   heartbeat < 60s). If capable, it broadcasts a ping via
   `sendModNetMessage(CHATTER_CAP_MAGIC, playerID, version, 0, 0)`.
   Re-broadcast every 50 turns; peers drop after 5 missed heartbeats.
2. **Election.** Every client builds the same `capable_humans` set from
   incoming pings. Election picks the lowest-id player from that set.
   Exactly one client agrees "I am the elector."
3. **Single API call.** Only the elector writes a request. Sidecar generates.
4. **Broadcast via chunked mod-net-message.** Elector streams the line as
   `CHATTER_LINE_MAGIC` chunks; every client (including the elector)
   reassembles them in `onModNetMessage` and renders locally via
   `CyInterface().addMessage` with the leader's portrait. All clients see
   the same line in their event log, attributed to the speaking leader.
5. **No game state writes.** The chunked message stream is not game state —
   it cannot OOS, cannot corrupt save games, cannot affect the simulation.

Per-game-type behavior:

- **SP / hot-seat:** local machine is always elector.
- **Network MP:** lowest-id capable human is elector.
- **Pitboss / PBEM:** chatter is disabled (no always-on human).

## Triggers

15 trigger types, two prompt modes:

### Directed (1-to-1, multi-turn-eligible marked ⚡)

| Trigger | Civ4 hook | Notes |
|---|---|---|
| `DECLARE_WAR` ⚡ | `onChangeWar` (war=true) | Marquee event |
| `PEACE_TREATY` | `onChangeWar` (war=false) | |
| `CITY_CAPTURED` ⚡ | `onCityAcquiredAndKept` | |
| `CITY_RAZED` ⚡ | `onCityRazed` | |
| `PLAYER_ELIMINATED_GLOAT` ⚡ | `onSetPlayerAlive` (false) | Killer addresses the dead |
| `PLAYER_ELIMINATED_LAST_WORDS` | (same hook) | Eliminated speaks |
| `VASSAL_FORCED` | `onVassalState` (planned) | Loser POV |
| `VASSAL_ACCEPTED` | `onVassalState` (planned) | Winner POV |
| `FIRST_CONTACT` | `onFirstContact` | |
| `BACKSTABBED` ⚡ | `onChangeWar` (war=true) when defender's residual attitude is Pleased+ or has 3+ positive memories of attacker | Defender POV; replaces DECLARE_WAR for that pair |

### Broadcast (proclamation to the world)

| Trigger | Civ4 hook |
|---|---|
| `RELIGION_FOUNDED` | `onReligionFounded` |
| `WONDER_BUILT` | `onBuildingBuilt` (gated to world wonders) |
| `CORPORATION_FOUNDED` | `onCorporationFounded` |
| `FIRST_TO_TECH` | `onTechAcquired` (gated to first-in-world) |
| `GOLDEN_AGE` | `onGoldenAge` |

⚡ = eligible for multi-turn rejoinders (50% probability per fire). Other
triggers always produce a single line.

## Anti-spam guards

Stricter than feels necessary on first pass — designed for restraint:

| Guard | Default | Effect |
|---|---|---|
| Per-pair cooldown | 200 game turns | Same pair won't have a second exchange close in time |
| Global cap per real-minute | 4 lines | Hard ceiling against pile-ups |
| Drop-new-while-queue-active | true | Only one event in flight at a time |
| Rejoinder probability | 50% | Half of marquee events get a 1-line response only |
| Max lines per exchange | 3 | Hard cap |
| Speaker-alive recheck | always | Drops queued lines if speaker eliminated |
| Pause-game guard | always | Queue pauses while game is paused |

## Fault tolerance contract

**Hard rule: chatter must never crash, hang, lag, or corrupt the game.**

- Every game-side public entry point wrapped in `try/except Exception` —
  bugs in chatter cannot raise into Civ4.
- No blocking calls. Atomic `tmp+rename` writes; quick polled reads
  capped at 8 files per tick; per-tick budget ~5 ms.
- Self-disable flag on first I/O failure. Stays out of the way for the
  rest of the session.
- No `getScriptData` writes anywhere in v1. Save games are guaranteed
  byte-identical to vanilla.
- Sidecar circuit breaker: 3 failures → 120s open. Auth failures open
  immediately and stop API calls.
- Refusal fallback: if the model refuses, sidecar returns a canned
  in-character placeholder ("Victoria regards Lincoln in pointed
  silence.") so the user sees something rather than nothing.

| Failure | What happens in-game |
|---|---|
| Sidecar not started | No chat. Zero perf impact. Auto-spawn attempts on next `onGameStart`. |
| API key wrong / missing | No chat. Sidecar logs once, opens circuit. |
| Foundry endpoint down | Brief timeouts → circuit opens → no chat. Resumes when network returns. |
| Disk full on Logs dir | Chatter self-disables for the session. Game unaffected. |
| Bug in `CvLeaderChatter.py` | Caught at entry-point try/except. Logged to `chatter.log`. Self-disables. |
| Bug in sidecar | Daemon may exit. Game-side continues normally; auto-spawn retries on next game start. |

## Cost & latency profile (validated)

From real Foundry calls during pre-flight testing (76 calls total):

- **Median latency:** ~1.0s
- **Max latency observed:** 4.1s
- **Refusal rate:** 3% on directed prompts, 0% on broadcast and
  one-shot multi-turn prompts.
- **Tokens per single line:** ~190 input + ~30 output.
- **Tokens per 3-line multi-turn:** ~280 input + ~110 output.
- **Estimated cost per game (300 turns, ~30 events):** well under 5 cents
  even with multi-turn rejoinders.

## See also

- `docs/CHATTER_RUNBOOK.md` — operator guide (setup, run, troubleshoot)
- `tools/chatter/README.md` — sidecar package README
- `tools/chatter/SPEC.md` — request/response JSON schemas
- `docs/MANUAL_SMOKE_TESTS.md` — required smoke tests for any chatter change
