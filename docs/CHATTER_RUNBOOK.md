# DowagerMod Leader Chatter — Runbook

This is the operator's guide for the Leader Chatter feature. For the
design overview, see [`CHATTER_OVERVIEW.md`](CHATTER_OVERVIEW.md).

## Setup on a new machine

1. Have your Azure Foundry endpoint URL, deployment name, and API key handy.
2. From the repo root, run:
   ```powershell
   .\tools\Setup-Chatter.ps1
   ```
3. Answer the prompts (endpoint and deployment have sensible defaults; API
   key is required and is read with hidden input).
4. The script writes `%LOCALAPPDATA%\DowagerMod\chatter\config.json` with
   restrictive ACLs (current user only).
5. Optionally pass `-RegisterScheduledTask` to register a Windows logon
   task that auto-starts the sidecar at every login. Recommended for your
   gaming desktop; skip on your laptop if you don't want a background
   Python process running all the time.

## Running the sidecar

```powershell
.\tools\Start-Chatter.ps1     # detached background pythonw.exe
.\tools\Stop-Chatter.ps1      # stop a running daemon
.\tools\Chatter-Status.ps1    # check status, see recent log
```

You can also just launch Civ4 directly — the game-side `CvLeaderChatter.py`
will auto-spawn the sidecar on `onGameStart` if your config exists but the
sidecar isn't running. The very first event in a fresh game might be
missed (~3s window while the sidecar boots) but everything after works
normally. The sidecar persists across multiple game launches.

## Multi-machine (laptop + desktop)

Per-machine setup, ~60 seconds each:

1. **Get the repo on the new machine.**
   ```powershell
   git clone https://github.com/siegelh/DowagerMod.git
   # or, if you already have it:
   git pull
   ```
2. **Run setup.** From the repo root on the new machine:
   ```powershell
   .\tools\Setup-Chatter.ps1
   ```
   Same Foundry API key works on every machine — Azure doesn't care.
3. **Recommended for your gaming desktop:** also register the auto-start
   task so the sidecar comes up at every Windows login:
   ```powershell
   .\tools\Setup-Chatter.ps1 -RegisterScheduledTask
   ```
4. **Verify:** `\.tools\Chatter-Status.ps1` should print "RUNNING" within
   a few seconds (or after first logon if you used the scheduled task).

**Don't** auto-sync `%LOCALAPPDATA%\DowagerMod\chatter\config.json` via
OneDrive / Dropbox / etc. — that defeats the ACL and may copy the key to
machines you didn't intend.

**Pulling new sidecar code:** sidecar code lives in `tools/chatter/`. After
`git pull`, just `Stop-Chatter.ps1` then `Start-Chatter.ps1` (or restart
the scheduled task) to pick up the new version. The game-side hooks come
through the normal mod installer.

## Updating endpoint or API key

`Setup-Chatter.ps1` is idempotent — re-run it any time to change values:

```powershell
.\tools\Setup-Chatter.ps1
```

- **Endpoint / deployment:** prompts show the current value; press Enter
  to keep it.
- **API key:** prompts "API Key (input hidden, press Enter to keep
  existing)". Press Enter to leave the current key in place; type a new
  key (then Enter) to replace it. The summary line will say
  `API key:     (unchanged)` when you keep the existing one.

After changing values, restart the sidecar so it picks up the new config:

```powershell
.\tools\Stop-Chatter.ps1
.\tools\Start-Chatter.ps1
```

## Uninstalling the sidecar

Use the dedicated uninstaller from the repo root:

```powershell
.\tools\Uninstall-Chatter.ps1               # stops daemon + removes scheduled task; keeps config
.\tools\Uninstall-Chatter.ps1 -RemoveConfig # also delete config + API key (asks for confirmation)
.\tools\Uninstall-Chatter.ps1 -RemoveConfig -Force  # same, no prompt
```

What it does, in order:
1. Stops any running daemon (calls `Stop-Chatter.ps1`).
2. Removes the `DowagerMod-Chatter` Windows scheduled task if registered.
3. Optionally deletes `%LOCALAPPDATA%\DowagerMod\chatter\` (config + key).
   Default is to keep it so reinstalling later doesn't re-prompt for the
   key.

This **does not** remove the in-game hooks — those ship with the mod and
are silent when no sidecar is running. To remove the entire feature from
your game install, simply uninstall DowagerMod itself.

## Distribution to friends

**Friends installing DowagerMod via the installer don't need anything
extra.** The mod payload includes the DLL and game-side hooks. The
sidecar is repo-only. If you (the key holder) are in their game, your
machine elects and broadcasts; if you aren't, no chatter fires and the
game is otherwise normal.

A friend who wants chatter when you're not present needs to:

1. Get a copy of `tools/chatter/` (clone the repo, or you send them a
   small zip).
2. Get their own Azure Foundry / OpenAI API key.
3. Run `Setup-Chatter.ps1`.

That's documented for them but not the default path.

## Troubleshooting

### "I never see any chat lines"

Run `.\tools\Chatter-Status.ps1`. It tells you in order:

1. Is the config file present? If no → run `Setup-Chatter.ps1`.
2. Is the API key non-empty? If the redacted display says `<empty>` → re-run setup.
3. Is the daemon running? If "NOT RUNNING" → `Start-Chatter.ps1`.
4. Is there recent activity in `daemon.log`? If empty for a long time
   while you've been playing → maybe no triggers fired (DoW takes time)
   or your machine isn't the elected elector in MP.

### "I see 'DowagerMod Chatter: no AI commentator available this game.' in chat"

That's the no-elector diagnostic. It means: after 30 turns into your
session, no human player in the game (including you) has a fresh sidecar
heartbeat. Either you forgot to start your sidecar, or in MP nobody has
chatter set up.

### "I see chat but it's the same line repeated"

Either you've hit the per-pair cooldown (no second exchange between Victoria
and Lincoln within 200 game turns) or the global rate cap (4 lines per
real-minute). Both are intentional anti-spam guards.

### "The sidecar log shows API errors"

Open `%USERPROFILE%\Documents\My Games\Beyond the Sword\Logs\DowagerMod\chatter\daemon.log`.
Look for `[ERROR]` lines.

- `auth_failure` → API key is wrong, expired, or doesn't have access to
  the deployment. Circuit forced OPEN; rerun setup with a fresh key and
  restart sidecar.
- `api_failure` → network / 5xx / timeout. Circuit opens after 3 in a row
  and stays open 120s. Should self-recover when the API does.
- `circuit_open` (info, not error) → previous failures opened the breaker;
  daemon is currently dropping requests.

### "The chat shows up with my player name as a prefix, not the leader's"

This was a v1 limitation. As of v1.1 the chunked-broadcast / `addMessage`
display path bypasses the chat channel entirely — lines render in the
event log attributed to the speaking leader (with portrait, civ color,
and a `Leader: text` prefix). If you still see `[YourName]:` style
prefixes, your mod install is still on v1. Reinstall DowagerMod to pick
up the v1.1 game-side hooks.

### "I want to disable chatter for one game"

Edit `%LOCALAPPDATA%\DowagerMod\chatter\config.json` and set
`"enabled": false`. Stop and restart the sidecar. Or just stop the
sidecar entirely (`Stop-Chatter.ps1`) and don't restart it for that
game.

### "I want to remove the feature entirely"

Use the uninstaller (see "Uninstalling the sidecar" above):

```powershell
.\tools\Uninstall-Chatter.ps1 -RemoveConfig
```

The game-side hooks remain in the mod payload but are entirely silent
when no sidecar is running. To remove them too, uninstall DowagerMod.

## Logs and where to find things

| What | Where |
|---|---|
| Sidecar config (per machine, gitignored) | `%LOCALAPPDATA%\DowagerMod\chatter\config.json` |
| Sidecar logs | `%USERPROFILE%\Documents\My Games\Beyond the Sword\Logs\DowagerMod\chatter\daemon.log` |
| Game-side logs | `%USERPROFILE%\Documents\My Games\Beyond the Sword\Logs\DowagerMod\chatter\chatter.log` |
| Sidecar PID file | `%USERPROFILE%\...\Logs\DowagerMod\chatter\daemon.pid` |
| Spool req/resp files | `%USERPROFILE%\...\Logs\DowagerMod\chatter\req-*.json`, `resp-*.json` |
| Sidecar source | `<repo>\tools\chatter\` |
| Game-side source | `<repo>\CoreFiles\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Assets\Python\Chatter\` |
| DLL source | `<repo>\third_party\beyond-the-sword-sdk\CvGameCoreDLL\CyMessageControl*.{cpp,h}` |
| Built DLL (deployed) | `<repo>\CoreFiles\...\Beyond the Sword\Assets\CvGameCoreDLL.dll` |

## Manual smoke tests

Required after any chatter-related code change. See
[`MANUAL_SMOKE_TESTS.md`](MANUAL_SMOKE_TESTS.md) for the full matrix.
At minimum:

1. **SP basics:** start a SP game with at least 2 AI civs, advance turns,
   force a DoW via WorldBuilder. Confirm a chat line appears within ~10s.
2. **Multi-turn:** observe whether the back-and-forth fires (50% chance);
   if it does, verify lines appear ~5-10s apart.
3. **Save/reload:** save mid-game, exit, reload. Confirm chatter state
   resets cleanly (no replay of the previous DoW line).
4. **Sidecar killed:** `Stop-Chatter.ps1` mid-game. Continue playing for
   a few turns. Confirm zero in-game errors. Restart sidecar; verify
   future events work again.
5. **No sidecar:** quit, `Stop-Chatter.ps1`, then launch Civ4 fresh.
   Confirm game runs normally with no chatter and no errors.
6. **2-client MP** (with a friend on LAN, or two Civ4 instances):
   force a DoW. Verify exactly ONE line in your sidecar log AND BOTH
   clients see the same chat line.
