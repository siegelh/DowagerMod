# Installer

This document describes the installer as it works today. If this file and
`CoreFiles/install.py` disagree, trust `CoreFiles/install.py`.

## TL;DR for friends installing DowagerMod

1. Install Civ4 BTS from Steam (clean — no other mods, don't launch it yet).
2. Clone this repo.
3. Double-click `Install DowagerMod.bat` at the repo root. Approve the UAC
   prompt. Done.

That's it. The first run captures a pristine snapshot of your clean Civ4
install. Every run after that wipes the live game back to that snapshot
and reapplies DowagerMod, so you never end up with stale or orphaned mod
files.

## Source of truth

| Thing                                | Path                                                            |
| ------------------------------------ | --------------------------------------------------------------- |
| Installer Python source              | `CoreFiles/install.py`                                          |
| PyInstaller spec                     | `CoreFiles/install.spec`                                        |
| Build script                         | `tools/build_installer.ps1`                                     |
| Built exe (committed to repo)        | `CoreFiles/dist/DowagerMod-Installer/DowagerMod-Installer.exe`  |
| Friend-facing launcher               | `Install DowagerMod.bat` (repo root, self-elevates)             |
| Mod payload (game files we ship)     | `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/`       |
| Per-machine installer state          | `%LOCALAPPDATA%\DowagerMod\config.json`                         |
| Pristine snapshot                    | `<install_dir> - PRISTINE` (sibling of the game install)        |

The repo mirror intentionally omits a few oversized stock archives
(`Assets[012].fpk`, `Art/Movies/Intros/intro.bik`). The pristine snapshot
covers them.

## Wipe-and-restore design

The installer is **not** an additive copy. Every run:

1. Ensures a pristine snapshot exists (one-time bootstrap on first install).
2. `robocopy /MIR pristine -> live` — wipes the live game back to a clean
   pre-mod state, deleting any stale or orphaned files from previous mod
   versions.
3. `robocopy /E payload -> live` — overlays DowagerMod's files on top.
4. Writes a sentinel file (`DOWAGERMOD_INSTALLED.txt`) so subsequent runs
   can detect that the live install has been modded.
5. Cleans `Documents\My Games\Beyond the Sword\` (preserves `Saves/` and
   `CivilizationIV.ini`) so stale XML cache cannot shadow the new mod.
6. Sets `DisableCaching = 1` in `CivilizationIV.ini` so the cache stays
   off across future game launches.

Because step 2 is a full mirror from the pristine, deleting a file from
the repo *does* remove it from the live install. There are no
mod-version-vs-mod-version drift bugs.

Step 2 always copies **in place** — the installer never renames the live
tree out of the way. This is deliberate: an earlier version of the
installer had a same-drive "hot-swap" fast path that renamed the live
folder aside before swapping in a pre-staged clone, and that rename could
strand an undeletable folder on some machines (see *Migration* below).
Copying in place is slightly slower than a directory rename, but it needs
no extra full-size clone on disk and it can never leave a stranded sibling
folder behind. Reliability and bounded disk usage win over raw speed here.

## Pristine snapshot

The pristine snapshot is a sibling folder of the live install, named with
the suffix ` - PRISTINE`. Example:

```
C:\Program Files (x86)\Steam\steamapps\common\
    Sid Meier's Civilization IV Beyond the Sword            <- live
    Sid Meier's Civilization IV Beyond the Sword - PRISTINE <- pristine
```

It is captured **once**, the first time the installer runs on a given
machine, from a clean Steam-installed copy. After that it never changes,
because Civ4 BTS is on Steam's frozen `original_release_unsupported`
beta branch and Firaxis is not patching it.

### First-run validation

Before capturing pristine, the installer runs sanity checks:

- `Civ4BeyondSword.exe` and `Beyond the Sword/Assets/` must exist.
- The DowagerMod sentinel must NOT exist.
- File count must be in `[28000, 33000]`. A complete fresh install has
  ~30,496 files. Below 28k means an interrupted/incomplete download;
  above 33k means another mod or extra files are present.
- No third-party mods under `Beyond the Sword/Mods/` (whitelist of 14
  stock BTS mods).
- `CustomAssets/` must be empty.

If any check fails, the installer refuses and prints numbered Steam
reinstall instructions (uninstall → manually delete leftover folder →
reinstall via Steam → re-run installer). It will not proceed until the
problems are fixed.

### Refreshing pristine

If the pristine ever needs to be recaptured (rare — only if Steam pushes
an update or the snapshot got corrupted), run with `--refresh-pristine`.
The installer will delete the existing snapshot and recapture from the
current live install, which must pass the same validation.

## Migration: retired hot-swap fast path

Older installer builds tried to make the *next* install "instant" by
keeping a same-drive pre-staged clone of pristine and swapping it into
place with directory renames:

- `<install> - PRISTINE_HOT` — a full same-drive clone of pristine,
  staged after an install so the following run could avoid a copy.
- `<install> - DELETE_ME` — the old live tree, renamed aside during the
  swap and then deleted.

That design promised an instant next install, but it was **not** reliable:
the final `rmtree` of `<install> - DELETE_ME` could fail whenever Windows
held any file in the old tree open (a running game, an Explorer window,
antivirus, or the search indexer). When that happened the folder was left
stranded, and only machines that had successfully staged a `PRISTINE_HOT`
ever hit the rename path at all — so behavior differed machine to machine.

The hot-swap architecture is now **fully retired**. There is no
"instant next install" contract anymore. Every install mirror-restores in
place (see *Wipe-and-restore design*), which cannot create either sibling
folder.

**Automatic migration cleanup.** Because older installers may have left
these folders behind, every install now looks for the two exact sibling
paths `<install> - PRISTINE_HOT` and `<install> - DELETE_ME` and removes
them:

- It clears the Windows read-only attribute and retries a bounded number
  of times to ride out *transient* locks.
- If a folder deletes, the installer reports it.
- If a folder is still locked after retries, the installer prints a
  prominent, path-specific WARNING and **continues** — a stale sibling
  never blocks an otherwise valid install, and the installer never claims
  it removed a folder it could not remove.
- Only those two exact derived paths are ever touched. The live install
  and the `<install> - PRISTINE` snapshot are never candidates for
  deletion.

The obsolete `pristine_hot_dir` config key is dropped from
`config.json` the next time the installer runs.

## Friend launcher (`Install DowagerMod.bat`)

A small `.bat` at the repo root so non-technical users don't have to
navigate into `CoreFiles\dist\DowagerMod-Installer\`. It uses `%~dp0`
(the directory of the .bat file itself) so it works regardless of where
the user cloned the repo.

If launched without admin rights it self-elevates via
`powershell Start-Process -Verb RunAs`, which triggers the UAC prompt.

## Build process

Builds use a dedicated venv at `.build_venv/` (gitignored) with **only**
`pyinstaller` and `tqdm` installed. Building from Anaconda or
system-Python pulls in jupyter/sphinx/jedi/zmq/cryptography hooks and
takes 15+ minutes; the dedicated venv builds in ~25 seconds.

```powershell
# One-time setup (already done in this repo):
python -m venv .build_venv
.\.build_venv\Scripts\pip install pyinstaller tqdm

# Build:
$env:PATH = "$PWD\.build_venv\Scripts;$env:PATH"
.\tools\build_installer.ps1 -Clean
```

Output: `CoreFiles/dist/DowagerMod-Installer/DowagerMod-Installer.exe`
(plus `_internal/` sibling folder containing Python DLLs and bundled
data). Total folder ~19 MB.

### Why one-folder mode (not one-file)

PyInstaller one-file mode extracts `python311.dll` to `%TEMP%\_MEIxxxx\`
at runtime, which Windows Application Control / WDAC / Smart App Control
blocks on locked-down Windows 11 installs ("not designed to run on
Windows or contains an error"). One-folder mode ships the DLLs as real
siblings of the .exe, which works on every Windows machine. Always use
one-folder for unsigned installers.

## Per-machine config

`%LOCALAPPDATA%\DowagerMod\config.json` stores:

- `install_dir` — discovered or user-confirmed live install path.
- `pristine_dir` — sibling pristine path (always `<install_dir> - PRISTINE`).
- `last_mod_version` — `git describe` from the most recent install.
- `last_install_at` — ISO timestamp of the most recent install.

After the first successful install, subsequent runs skip discovery and
read these from config. Pass `--install-dir <path>` to override.

> Obsolete: older installers also wrote a `pristine_hot_dir` key for the
> retired hot-swap fast path. The current installer never writes it and
> drops it from `config.json` on the next run.

## Install discovery

If config is missing or stale, the installer searches for the live install:

1. Known Steam paths under `Program Files (x86)\Steam\steamapps\common\`,
   `Program Files\Steam\...`, and similar layouts on other drives.
2. If none match, walks each fixed drive looking for a directory that
   contains both `steamapps` and the BTS folder name.
3. Asks the user to confirm the discovered path before doing anything
   destructive.

## My Games user data cleanup

Every install wipes `Documents\My Games\Beyond the Sword\` except:

- `Saves/` — your saved games.
- `CivilizationIV.ini` — game settings (we hand-edit this; if we deleted
  it, the game would recreate it with `DisableCaching = 0`).

Everything else (`cache/`, `Logs/`, `MODS/`, `Replays/`, ...) is removed
because Civ4's XML cache aggressively shadows mod XML changes — a stale
cache will silently skip your icon updates, leader trait changes, etc.

OneDrive document-redirection is handled: the installer checks
`%OneDrive%`, `%OneDriveCommercial%`, `%OneDriveConsumer%` in addition
to the standard `%USERPROFILE%\Documents` location.

After cleanup the installer flips `DisableCaching` from `0` to `1` in
`CivilizationIV.ini` so the cache stays off across future game launches.
If the line is somehow missing from the .ini, the installer prints a
warning telling the user to add `DisableCaching = 1` under `[CONFIG]`
manually.

## CLI flags

```
DowagerMod-Installer.exe [--install-dir PATH] [--refresh-pristine]
```

- `--install-dir PATH`: skip discovery, use this path as the live install.
- `--refresh-pristine`: delete existing pristine snapshot and recapture
  from the current live install (which must be clean).

## Troubleshooting

- **"is not designed to run on Windows or it contains an error"**: you
  built a one-file exe instead of one-folder. Rebuild with the current
  `install.spec` (which uses `exclude_binaries=True` + `COLLECT`).
- **"Pristine looks INCOMPLETE: found N files"**: the live install is
  partial. Steam → right-click game → Properties → Installed Files →
  Verify. Re-run installer.
- **"Pristine has TOO MANY files"**: a mod is already installed. Steam
  uninstall → manually delete leftover folder → reinstall → re-run
  installer.
- **"DowagerMod is already installed"**: the live install has the
  sentinel file. Either run the installer normally (it'll wipe back to
  pristine and reapply) or delete the sentinel manually if you want to
  capture a fresh pristine.
- **Friend's icons don't match repo**: the XML cache wasn't cleared. The
  current installer handles this automatically; if they're on an older
  installer, have them delete `Documents\My Games\Beyond the Sword\cache\`
  manually and set `DisableCaching = 1` in `CivilizationIV.ini`.
- **A `... - DELETE_ME` or `... - PRISTINE_HOT` folder sits next to the
  install**: it was left by an older installer's retired hot-swap fast
  path (see *Migration*). The current installer never creates these and
  tries to remove them on every run. If the installer warns it could not
  delete one, it was locked — close Civ4, any Explorer window inside that
  folder, and antivirus, then re-run the installer or delete the folder by
  hand. It is safe to delete and does not affect the installed mod.
  Never delete `... - PRISTINE` (that is your clean snapshot) or the live
  install folder itself.
