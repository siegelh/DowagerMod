# DowagerMod Chatter Sidecar

This is a small Python 3 process that runs alongside Sid Meier's Civilization
IV: Beyond the Sword to generate AI-driven leader trash-talk lines via Azure
Foundry (GPT-5.4-mini, Responses API).

The sidecar is **not** part of the friend-facing installer payload. It is a
developer/key-holder tool that lives in the repo. Friends who install
DowagerMod via `Install DowagerMod.bat` get the game-side hooks but no
sidecar. Chatter only happens in games where at least one connected human
player has a working sidecar configured.

## How it works

```
[Civ4 game]                            [Sidecar (this package)]
CvLeaderChatter.py             ───►    chatter_daemon.py
  - trigger event              JSON    - watch spool dir
  - write request file         spool   - call Azure Foundry
                                       - write response file
  - poll on tick                       - sleep
  - render line via                    - repeat
    addMessage / sendChat
```

## Files

- `chatter_daemon.py` — main loop: scan spool, dispatch requests, write replies.
- `azure_client.py` — thin wrapper around the OpenAI SDK pointed at Foundry.
- `prompts.py` — system + user prompt templates per trigger type.
- `state.py` — per-pair conversation tracking (in-memory only).
- `circuit.py` — circuit breaker for fault tolerance.
- `spool.py` — atomic file I/O for the request/response spool.
- `config.py` — config loader (file + env vars).
- `requirements.txt` — Python deps (just `openai`).
- `config.example.json` — committed example config (no secrets).
- `tests/` — fault-tolerance and round-trip tests.

## Setup (one-time per machine)

```powershell
.\tools\Setup-Chatter.ps1
```

Interactive script. Prompts for endpoint / deployment / API key and writes
`%LOCALAPPDATA%\DowagerMod\chatter\config.json` with restrictive ACLs.

## Run

```powershell
.\tools\Start-Chatter.ps1     # start the daemon (background pythonw.exe)
.\tools\Stop-Chatter.ps1      # stop it
.\tools\Chatter-Status.ps1    # show status + recent activity
```

The daemon also auto-launches when you start Civ4 if you haven't started it
manually — game-side `CvLeaderChatter.py` does a detached `subprocess.Popen`
on `onGameStart` if no sidecar PID is fresh.

## Spool layout

Per-machine, runtime-only, gitignored. Lives at:
```
%USERPROFILE%\Documents\My Games\Beyond the Sword\Logs\DowagerMod\chatter\
```
- `req-<utc>-<seq>.json`  — game writes, daemon reads + deletes
- `resp-<utc>-<seq>.json` — daemon writes, game reads + deletes
- `daemon.pid`            — daemon process ID + heartbeat timestamp
- `daemon.log`            — daemon log
- `chatter.log`           — game-side log

See `tools/chatter/SPEC.md` for the JSON schemas.

## Fault tolerance

- Per-request timeout (default 8s)
- Circuit breaker (3 failures → 120s open)
- Bounded in-flight queue + 1 req/sec rate cap
- All exceptions caught in the main loop; daemon never dies on a single bad
  request.
- API key never logged (redacted to `sk-***...***`).

## Secrets

Your API key is never in the repo, never in the installer payload, never in
the pristine snapshot. It lives only at `%LOCALAPPDATA%\DowagerMod\chatter\config.json`
on your machine. See `tools/chatter/check_no_secrets.py` for a pre-commit
guard against accidental leaks.
