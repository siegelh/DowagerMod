# DowagerMod Leader Chatter — Runbook

This is the operator's guide for the Leader Chatter feature. For the
design overview, see [`CHATTER_OVERVIEW.md`](CHATTER_OVERVIEW.md).

## What you get

Three layers, all opt-in via `.env`:

1. **Text chatter** — leaders trash-talk in the in-game event log on
   major events (DoW, peace, city capture/raze, religion founded,
   wonder built, etc).
2. **Multi-turn exchanges** — sometimes the attacker fires a second
   line in response (50% chance, gated by per-pair cooldown).
3. **Voiceover** — each line is also spoken aloud in a Discord voice
   channel via a bot account (Azure Speech TTS + discord.py).

## Install (single machine, ~60 seconds)

The chatter sidecar is configured **entirely from a `.env` file at the
repo root** (`C:\DowagerMod\.env`). That file is the single source of
truth — there is no interactive setup wizard, no `config.json`, no
hidden state.

```powershell
cd C:\DowagerMod
Copy-Item .env.example .env
notepad .env                  # paste your Azure + Discord credentials
.\tools\Setup-Chatter.ps1     # validates .env, hardens ACL, optional task
.\tools\Start-Chatter.ps1     # launches detached pythonw.exe
```

What `Setup-Chatter.ps1` does:
- Validates `.env` exists and contains real (non-placeholder) values for
  the required fields. **Fails loudly** with operator guidance if `.env`
  is missing or contains `paste-your-*-here` placeholders.
- Prints a redacted summary of every credential it found.
- Warns if a legacy `%LOCALAPPDATA%\DowagerMod\chatter\config.json`
  exists (it's IGNORED — you can copy values out and delete it).
- Hardens `.env` ACL to current user only (skip with `-NoHardenAcl`).
- Optionally registers the Windows scheduled task
  (`-RegisterScheduledTask`).

Pass `-Edit` to skip validation and just open `.env` in Notepad.

## Voiceover setup (optional)

Voiceover plays each chatter line aloud in a Discord voice channel via a
bot account, so everyone in the channel hears it. Friends in the channel
need ZERO additional setup beyond joining.

**Prerequisites (one-time):**

1. **Azure Speech resource** (separate from Foundry):
   - Create a Speech resource in the Azure portal. Free tier (F0) gives
     500K characters/month — plenty for normal play.
   - Copy the **TTS** endpoint (`https://<region>.tts.speech.microsoft.com/`,
     NOT the generic Cognitive Services URL the portal shows by default)
     and one of the keys.
2. **Discord bot:**
   - Go to https://discord.com/developers/applications and create a new
     application.
   - Add a Bot to the application; copy the bot token.
   - Generate an OAuth2 invite URL with the `bot` scope and `Connect` +
     `Speak` voice permissions.
   - Click the invite URL and add the bot to your Discord server.
   - In Discord, enable Developer Mode (Settings → Advanced) so you can
     right-click and Copy ID. Get your server (guild) ID and the voice
     channel ID where the bot should connect.
3. **FFmpeg** on the sidecar machine (used by discord.py for audio):
   ```powershell
   winget install ffmpeg
   ```
   Or download from https://ffmpeg.org/download.html and add to PATH.
4. **discord.py with voice extras**:
   ```powershell
   pip install -U "discord.py[voice]"
   ```

**Enable:** edit `.env` and set:

```
DOWAGER_CHATTER_SPEECH_ENDPOINT=https://eastus.tts.speech.microsoft.com/
DOWAGER_CHATTER_SPEECH_KEY=<your-speech-key>
DOWAGER_CHATTER_DISCORD_BOT_TOKEN=<your-bot-token>
DOWAGER_CHATTER_DISCORD_GUILD_ID=<your-guild-id>
DOWAGER_CHATTER_DISCORD_VOICE_CHANNEL_ID=<your-voice-channel-id>
DOWAGER_CHATTER_VOICEOVER_ENABLED=true
```

Then restart the sidecar:

```powershell
.\tools\Stop-Chatter.ps1
.\tools\Start-Chatter.ps1
```

The bot will auto-connect to the configured voice channel on startup and
play each chatter line as it is generated.

**To disable later:** set `DOWAGER_CHATTER_VOICEOVER_ENABLED=false` in
`.env` and restart the sidecar. Bot disconnects, no more Speech API
calls, text chatter unchanged.

## Running the sidecar

```powershell
.\tools\Start-Chatter.ps1     # detached background pythonw.exe
.\tools\Stop-Chatter.ps1      # stop a running daemon
.\tools\Chatter-Status.ps1    # check status, see recent log
```

You can also just launch Civ4 directly — the game-side `CvLeaderChatter.py`
will auto-spawn the sidecar on `onGameStart` if `.env` exists but the
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
2. **Copy your `.env` over.** The same `.env` works on every machine —
   Azure and Discord don't care which host is calling.
   ```powershell
   # On the source machine, copy C:\DowagerMod\.env to a USB stick or
   # secure channel. Then on the new machine:
   Copy-Item <wherever>\.env C:\DowagerMod\.env
   ```
   Or just `cp .env.example .env` and paste the values from your password
   manager.
3. **Validate.**
   ```powershell
   .\tools\Setup-Chatter.ps1
   ```
4. **Recommended for your gaming desktop:** also register the auto-start
   task so the sidecar comes up at every Windows login:
   ```powershell
   .\tools\Setup-Chatter.ps1 -RegisterScheduledTask
   ```
5. **Verify:** `.\tools\Chatter-Status.ps1` should print "RUNNING" within
   a few seconds (or after first logon if you used the scheduled task).

**Don't** auto-sync `.env` via OneDrive / Dropbox / etc. — that defeats
the ACL and may copy the keys to machines you didn't intend.

**Pulling new sidecar code:** sidecar code lives in `tools/chatter/`. After
`git pull`, just `Stop-Chatter.ps1` then `Start-Chatter.ps1` (or restart
the scheduled task) to pick up the new version. The game-side hooks come
through the normal mod installer. Your `.env` is untouched by `git pull`.

## Updating endpoint or API key

`.env` is the single source of truth. To change any value:

```powershell
notepad C:\DowagerMod\.env       # or: .\tools\Setup-Chatter.ps1 -Edit
.\tools\Setup-Chatter.ps1        # re-validate (optional but recommended)
.\tools\Stop-Chatter.ps1
.\tools\Start-Chatter.ps1
```

The daemon reads `.env` once at startup. Changes only take effect after
a Stop / Start cycle. (For one-shot debugging without editing `.env`,
real shell env vars override `.env` for the spawned process — e.g.
`$env:DOWAGER_CHATTER_LOG_LEVEL='DEBUG'; .\tools\Start-Chatter.ps1`.)

## Uninstalling the sidecar

Use the dedicated uninstaller from the repo root:

```powershell
.\tools\Uninstall-Chatter.ps1                       # stops daemon + removes scheduled task; keeps .env
.\tools\Uninstall-Chatter.ps1 -RemoveEnv            # also delete .env (asks for confirmation)
.\tools\Uninstall-Chatter.ps1 -RemoveEnv -Force     # same, no prompt
.\tools\Uninstall-Chatter.ps1 -RemoveLegacyConfig   # also delete the legacy %LOCALAPPDATA%\...\config.json
```

What it does, in order:
1. Stops any running daemon (calls `Stop-Chatter.ps1`).
2. Removes the `DowagerMod-Chatter` Windows scheduled task if registered.
3. Optionally deletes `<repo>\.env`.
4. Optionally deletes the legacy
   `%LOCALAPPDATA%\DowagerMod\chatter\config.json` (no longer read by
   the daemon as of the .env refactor).

Default is to keep `.env` so reinstalling later doesn't require
re-pasting your keys.

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

1. Get a copy of the repo (clone, or you send them a small zip of `tools/`).
2. Get their own Azure Foundry + (optionally) Speech key.
3. `Copy-Item .env.example .env`, paste their keys, run `Setup-Chatter.ps1`.

That's documented for them but not the default path.

## Troubleshooting

### "I never see any chat lines"

Run `.\tools\Chatter-Status.ps1`. It tells you in order:

1. Is `.env` present and valid? If "MISSING" or "INVALID" → copy
   `.env.example` and edit; if values are placeholders → fill them in.
2. Are the required fields populated (endpoint, deployment, api_key)?
   The redacted display shows what was found.
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
  the deployment. Circuit forced OPEN; edit `.env` with a fresh key and
  restart the sidecar.
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

Stop the sidecar (`Stop-Chatter.ps1`) and don't restart it for that game.
The in-game hooks are silent without a sidecar. Or, if you want voiceover
off but text on, set `DOWAGER_CHATTER_VOICEOVER_ENABLED=false` in `.env`
and restart.

### "I want to remove the feature entirely"

Use the uninstaller (see "Uninstalling the sidecar" above):

```powershell
.\tools\Uninstall-Chatter.ps1 -RemoveEnv -RemoveLegacyConfig
```

The game-side hooks remain in the mod payload but are entirely silent
when no sidecar is running. To remove them too, uninstall DowagerMod.

## Logs and where to find things

| What | Where |
|---|---|
| Sidecar config (per machine, gitignored) | `<repo>\.env` (e.g. `C:\DowagerMod\.env`) |
| Config template | `<repo>\.env.example` |
| Legacy config (IGNORED, can delete) | `%LOCALAPPDATA%\DowagerMod\chatter\config.json` |
| Sidecar logs | `%LOCALAPPDATA%\DowagerMod\chatter\spool\daemon.log` |
| Game-side logs | `%LOCALAPPDATA%\DowagerMod\chatter\spool\chatter.log` |
| Sidecar PID file | `%LOCALAPPDATA%\DowagerMod\chatter\spool\daemon.pid` |
| Spool req/resp files | `%LOCALAPPDATA%\DowagerMod\chatter\spool\req-*.json`, `resp-*.json` |
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
