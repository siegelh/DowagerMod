"""DowagerMod installer (manifest-free, wipe-and-restore design).

Design:
  Civ4 BTS is a frozen game; we keep a per-machine "pristine" snapshot
  next to the live install. Every install run wipes the live install,
  restores it from pristine, then overlays the mod payload on top. This
  guarantees zero cross-version drift regardless of what was previously
  installed.

  The first time the installer runs on a machine it bootstraps the
  pristine snapshot by copying the live install (which the user must
  confirm is clean — freshly Steam-installed, no mods applied). After
  that, pristine is the authoritative baseline forever.

Persistent state:
  %LOCALAPPDATA%\DowagerMod\config.json
    {
      "install_dir": "...\Sid Meier's Civilization IV Beyond the Sword",
      "pristine_dir": "...\Sid Meier's Civilization IV Beyond the Sword - PRISTINE",
      "last_mod_version": "...",
      "last_install_at": "2026-04-28T17:00:00"
    }

Sentinel file inside live install:
  _DOWAGERMOD_INSTALLED.txt
  Used to detect a dirty install when bootstrapping pristine, and to
  surface the installed mod version to support requests.

CLI:
  install.py
  install.py --install-dir "C:\path\to\install"
  install.py --refresh-pristine

Frozen vs script:
  When run as install.exe, the payload directory is expected to sit
  next to the executable (PyInstaller one-folder layout). When run as
  a script, payload is read from the repo (CoreFiles/...).
"""

from __future__ import annotations

import argparse
import ctypes
import datetime as _dt
import json
import os
import re
import shutil
import string
import subprocess
import sys
import time
from pathlib import Path

PAYLOAD_DIRNAME = "Sid Meier's Civilization IV Beyond the Sword"
PRISTINE_SUFFIX = " - PRISTINE"
SENTINEL_NAME = "_DOWAGERMOD_INSTALLED.txt"
SOUND_FILENAME = "install_noise.wav"

# Hand-crafted by the project author. Do not regenerate or modify.
BANNER = r"""

***################***************###*******#*******************************************************
***################*********************************************************************************
****##########**************###*********************#***********************************************
****##########**************###*********************#***********************************************
***###########***##********#####***##*#####***+=****#**#******************************************##
##############***##********#######*###**+#**=*--=-++*=-*********************************************
###########****************######**#**#++++*=====++==-==+--+=+**************************************
##############************#####**#*+****++++#===+=-++==:=-:-:=-+************************************
##############*************##*******++++++++++++++++***=-+++=::-+==*********************************
##############*********#*#***####*##*##*****+++**#*#####**+-=-:=-:=-=*******************************
##****######***********######%#######*#****######*++++++****+-.:=+-----*****************************
#######*****************#%%%#%###%*+++=+=++***+===+++++==+******=-=+=--=****************************
#######****************#%%%#######+*+++=++**+**+++=++++++=+*****###**+=-=+**************************
***********************#%%%##%####+*++++++**#*************+++++*###**+==-=+*************************
*****************##***#%%%%%%%%##****++*++*******************+==+*****+===+*************************
***************##****#%@@%%%%%%%#***++=+=+++++++++++**++++******=+***#*++++****#********************
**************##****##%@@%%%@%%%%#*+++======------------==+++**###*+*++++***++*********************#
******###***********#%@@%%%%%%%%%#*++====---------:::------===+****++***+**++=+##*******************
*****#####**********#%%%%%%#%%%##**+=====----------:::::-----=====+++==+++*++=+##*******************
##***#######********#%%%%%##%####*++===-----------::::::::----===+++++++****+++##*******************
##***#######*******##%%#########**+====-=--------::::::::::::-=====++++++**++++*##******************
*****#######*******####%%%%#####*++===---==------:::::::::::::--==+**##*+**+++++**#*****************
*****#######*****###*#####%#####*++====---=-==-------:::::::::::-==***###*##**=++*******************
*****######*****####*#%%%%#####**++===-===--===---:::::--:::::::--=++**#*****++++*#*****************
*****####*##*****#**#%%%%%#####**+===----=--==----===---::-::::---=++*+++*#**+++=*%*****************
##***####***********#@%%%%#####*++=====-----=------====--:::::::---=+++++****+===*#*#***************
*******************##@@%%%%######**+====-==-----=======+=--:-:::--==+*+++**##*+=+###*************#**
*****************#**##%%%%%###*****+++*++=--::-==+++=---==-----:--=++++****##*++*###****************
******##*************##%%%%%##%#**+++++#*+-:::=+****##*++=---------=+==+***###*****###************##
####***************######%%%##%%#*%=-+%%#+-:::-+++==++-:-------:----===---*#%%###*******************
#######***##*********#####%#######*+=+#%#+-::::-+++====--::::----------=--##%%%#********************
##########***********####*######**++*#%##+-::::::===--::::::::-------:::--*%%%#*********************
############********##############*#####*=--::::::------:::::-------:::::+%%%##***#******#********##
############********####**######**######+=-::--:::::::::-:::----------::=@%%##%#*********#********##
############****###*####**######*#######+=---------:::::::----------::::#@@%#%%#*****************###
###################********#########%%%%#*+=+%*=-==-::::::----------:-=*%%%##%#********#*********###
###################*#####***########%%###*+-----:--=-----::---------=+=##%%##*********************##
###########**######*#######**#%########*+=---::::::-----------------==*%%%%#*#**********************
###########**######*########*#######***+=---:--::::---===----::::--=+=#%@%%##***********************
#######***##########**##*###*#%#######*++===--=--:::-------::------**=#%%%%#*******************###**
#######******#########**#**#*#%#######%##**+=====-----:--::::------+=+#%###*****#**************###**
#######******#########*******########%###****+==-----=-:-----------=%%*###**###*********************
###########**#########**####*#######%%##**+=-------:----------===##%**++#***************************
#######################################**+==-----::---=-----=+#*%#==++=-****************************
################################**#####*++==-----::--=----=*%#*+=++==+=-+##************************#
###############################****#####*+++====----=+***###**==+-+=--+**%%#******###**#***********#
###############################****##%%%###********##**#*****===-=-++*#%#%%@#***********************
################################**#%@@%%%%%%%%%%%######*==++*=*---**%%@%#%%%%%#*******************##
################################**#%@@@%%%%%%%%%%*+*+*#=+*+=+#-=-+#@%@@%%@%##%%#*****************###
######################***#######***#%%%@%%#@#***+#+++-+*--*++++++##@@@%#%@@@@@@@%#***************###
####################****#########**#%%%%%##+**#*+*+-=*-**+*-#**##%@@%%%%%##%%###%##**************###
####################****########***##%%%##%**+***+*==+++#****%%@%%@%%%@%#%@@@@%%%%%#*************###
##*######################**********##%%##**%+***#+=#+=+*=*#%@@@@@@@@@@@%%%#%%%%%%%%%##**********####
#########################*********##%%%%%%#%%***#*+*%%#%%%%%@@@%%@@@@%%####%%%%%%%%%%%##********####
########################**#**##%@@@@@@%%%%#*##*#%%@%%%%%#%#%@@@@%%@@%###%%@@@@@%%%%%%%%%#*******####
##########################%@@@@@@@@@@@@@@@@%@@@@%%%%%@##%%%%%@@@@@%##%@@@@@@%%%#####%%%%%%#****#####
######################%@@@@@@@@@@@@@@@@@@@@@@@@%%%%%%@@@@@%%@@@@%##%@%@@@%##***########%%%%##****###
###################%@@@@@@@@@@@@@@@@@@@@%%%%@@@%%%@@@@@@@@@@@@@%%@@%@@@%################%#%%%#***###
################%@@@@@@@@@@@@@@@@@@@@@@@%%%@@@@%%%%%@@@@@@@@@%%@@%@@%%%%####********####%%%%%%#**###
##############@@@@@@@@@@@@@@@@@@@@@@@@@@%%@@@@%###@@@%@@@@@%@@@%@@@%%%%%#************####%%%%@%#####
############%@@@@@@@@@@@@@@@@%@@@@@@@@@@@%@@@%%@@%@%@@@@@@@@%%@@@%%%%%####*************##%%%%%%#####
###########@@@@@@@@@@@@@@@@@@@@@@@@@%%@@@@@@%@@@@@@@@@@@@@@@@@@%%%%%##******************##%%%%@%####
##########@@@@@@@@@@@@@@@@%%@@@@@@@%@@@@@@@@@@@%@@@@@@@@@@@@@%%%%#######*******#********###%%%@%####
########%@@@@@@@@@%@@@@@@##@@@@@@%@@@@@@%%@@@@@%%@@@@@@@@@@@%%%############***#*****+****##%%%%%####
#######%@@%@@@@@@@@@@@@@%%@@@@@@@@@@@%#%%%@%%@@%@@@@@@@@%@@@%%%#%%%%%%%###**#****+++*****##%%%%%%##*
#####%@@%%@@@@@@@@%%@@@*%@@@@@@@@@@%%@@@%%%%@@@%@@@@@@%%@@@%%%%%%%@%%#######****+++******###%%%%%%##
#####@@@%@@@@@@@@%@@@##%@@@@@@@@@@%@@@@@@@@@@%@@@@@@@%%%@@@%%%%@@%%%#######****++********###%%%%%%##
#####@@@@@@@@@@%%@@%%*@@@@@@@@@@%@@@@@%@@@@@@@@@@@@@%%%@@@%%%@@%%%#######*****++*********###%%%%%%##
####%@@@@@@@@@@@%@@#%@@@@@@@@%##@@@@@@@%%%@@@@@%%@@%%%%@@@%%%%%%%%%#####******+**********###%%%%%%%#
####@@@@@@@%%@@%@#=*%%@@@%@%%#%@@%@%@@@@%@@@@@%%%%%#%@@@@@%%%%%%%%%%###*************+****###%%%%%%%%
###%@@@@@@%@@@@@+##%%@#*#%%%#@@@%%@%@@@@@@@@@%#%@###%@@@@%%%%@@%%%#####******************###%%%%%%%%
##@@@@@@%%@#%%%%#%#%@#+#%**@@@@@@@%@@@@@@@@%#%%%#**#@@@@%%%@@@%%%%%%%%#******************###%%%%%%%%
#%@@@@@@@@@%%%##%%%#*#%#%%@@@@@@@@@@%@@@@@%####%#*#%@@@@%@@@@%%%%%%%##*******************####%%%%%%%

__        __   _                            _                  
\ \      / /__| | ___ ___  _ __ ___   ___  | |_ ___            
 \ \ /\ / / _ \ |/ __/ _ \| '_ ` _ \ / _ \ | __/ _ \           
  \ V  V /  __/ | (_| (_) | | | | | |  __/ | || (_) |          
 __\_/\_/ \___|_|\___\___/|_| |_| |_|\___|__\__\___/       _ _ 
|  _ \  _____      ____ _  __ _  ___ _ __|  \/  | ___   __| | |
| | | |/ _ \ \ /\ / / _` |/ _` |/ _ \ '__| |\/| |/ _ \ / _` | |
| |_| | (_) \ V  V / (_| | (_| |  __/ |  | |  | | (_) | (_| |_|
|____/ \___/ \_/\_/ \__,_|\__, |\___|_|  |_|  |_|\___/ \__,_(_)
                          |___/                                

      """


def play_install_sound() -> None:
    """Play the legacy install_noise.wav if present and we're on Windows."""
    if os.name != "nt":
        return
    try:
        import winsound
    except ImportError:
        return
    # Search order: bundled (PyInstaller _MEIPASS), exe/script dir.
    candidates: list[Path] = []
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        candidates.append(Path(meipass) / SOUND_FILENAME)
    if getattr(sys, "frozen", False):
        candidates.append(Path(sys.executable).resolve().parent / SOUND_FILENAME)
    else:
        candidates.append(Path(__file__).resolve().parent / SOUND_FILENAME)
    for wav in candidates:
        if wav.exists():
            try:
                winsound.PlaySound(str(wav), winsound.SND_FILENAME | winsound.SND_ASYNC)
            except Exception:
                pass
            return


CONFIG_DIR = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "DowagerMod"
CONFIG_FILE = CONFIG_DIR / "config.json"

KNOWN_STEAM_PATHS = [
    r"C:\Program Files (x86)\Steam\steamapps\common",
    r"C:\Program Files\Steam\steamapps\common",
    r"D:\Steam\steamapps\common",
    r"D:\SteamLibrary\steamapps\common",
    r"E:\SteamLibrary\steamapps\common",
]


# ---------------------------------------------------------------------------
# Utilities


def is_admin() -> bool:
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def get_payload_root() -> Path:
    """Return the directory containing the mod payload to overlay.

    The payload directory is named PAYLOAD_DIRNAME and lives inside
    CoreFiles/. We locate it by walking up from the exe/script location
    until we find a directory that contains a child named PAYLOAD_DIRNAME.

    This makes the installer robust to whether it's running as:
      - a script:   <repo>/CoreFiles/install_v2.py
      - a one-file exe at repo root
      - a one-folder exe at <repo>/CoreFiles/dist/DowagerMod-Installer/
      - or anywhere else inside the cloned repo.
    """
    if getattr(sys, "frozen", False):
        start = Path(sys.executable).resolve().parent
    else:
        start = Path(__file__).resolve().parent  # CoreFiles/

    cur = start
    for _ in range(8):
        candidate = cur / PAYLOAD_DIRNAME
        if candidate.is_dir():
            return candidate
        # also check inside CoreFiles/ at this level (common layout)
        cf_candidate = cur / "CoreFiles" / PAYLOAD_DIRNAME
        if cf_candidate.is_dir():
            return cf_candidate
        if cur.parent == cur:
            break
        cur = cur.parent

    # Last resort: return the legacy location even if missing, so the
    # caller's "payload not found" error message is informative.
    return start / PAYLOAD_DIRNAME


def get_repo_root() -> Path:
    """Return the repo root by walking up from the payload."""
    payload = get_payload_root()
    # payload = <repo>/CoreFiles/<PAYLOAD_DIRNAME>; repo = payload.parent.parent
    if payload.parent.name == "CoreFiles":
        return payload.parent.parent
    return payload.parent


def get_mod_version() -> str:
    try:
        out = subprocess.check_output(
            ["git", "describe", "--tags", "--always", "--dirty"],
            cwd=str(get_repo_root()),
            stderr=subprocess.DEVNULL,
        )
        return out.decode("utf-8", errors="replace").strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def load_config() -> dict:
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            print(f"WARNING: corrupt config at {CONFIG_FILE}, ignoring.")
    return {}


def save_config(cfg: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2), encoding="utf-8")


# ---------------------------------------------------------------------------
# Install dir discovery


def find_candidate_installs() -> list[Path]:
    """Look for likely Civ4 BtS install dirs without scanning entire drives."""
    candidates: list[Path] = []
    seen: set[str] = set()
    for root in KNOWN_STEAM_PATHS:
        candidate = Path(root) / PAYLOAD_DIRNAME
        key = str(candidate).lower()
        if candidate.exists() and key not in seen:
            candidates.append(candidate)
            seen.add(key)
    return candidates


def walk_drive_for_install(drive_letter: str) -> Path | None:
    """Last-resort drive walk. Slow; only used when known paths fail."""
    drive = drive_letter.rstrip(":") + ":\\"
    if not Path(drive).exists():
        return None
    print(f"Scanning {drive} for Civ4 BtS install (this can take a minute)...")
    for dirpath, dirnames, _files in os.walk(drive):
        # don't recurse into common large/irrelevant trees
        dirnames[:] = [
            d for d in dirnames
            if d.lower() not in {"windows", "$recycle.bin", "system volume information",
                                 "users", "programdata"}
        ]
        if PAYLOAD_DIRNAME in dirnames:
            return Path(dirpath) / PAYLOAD_DIRNAME
    return None


def discover_install_dir() -> Path:
    candidates = find_candidate_installs()
    if len(candidates) == 1:
        c = candidates[0]
        print(f"Found Civ4 BtS install: {c}")
        ans = input("Use this install? [Y/n]: ").strip().lower()
        if ans in ("", "y", "yes"):
            return c
    elif len(candidates) > 1:
        print("Multiple Civ4 BtS installs found:")
        for i, c in enumerate(candidates, 1):
            print(f"  [{i}] {c}")
        while True:
            ans = input(f"Pick one [1-{len(candidates)}]: ").strip()
            try:
                idx = int(ans) - 1
                if 0 <= idx < len(candidates):
                    return candidates[idx]
            except ValueError:
                pass
            print("Invalid choice.")

    # fallback: ask drive, walk
    print("\nCould not find Civ4 BtS in standard Steam locations.")
    drive = input("Drive letter where Civ4 BtS is installed (e.g. C): ").strip()
    if not drive:
        drive = "C"
    found = walk_drive_for_install(drive)
    if found is None:
        raise SystemExit(
            f"Could not locate '{PAYLOAD_DIRNAME}' on drive {drive}:.\n"
            "Specify --install-dir explicitly or install Civ4 BtS via Steam first."
        )
    print(f"Found: {found}")
    ans = input("Use this install? [Y/n]: ").strip().lower()
    if ans not in ("", "y", "yes"):
        raise SystemExit("Aborted.")
    return found


# ---------------------------------------------------------------------------
# Robocopy wrapper


def _count_files(root: Path) -> int:
    n = 0
    try:
        for _dp, _dn, fns in os.walk(root):
            n += len(fns)
    except OSError:
        pass
    return n


def robocopy(src: Path, dst: Path, mirror: bool, *, label: str) -> None:
    """Run robocopy with a progress bar (one tick per file).

    Robocopy exit codes (bitmask, 0-7 = success states):
      0 No change, 1 files copied, 2 extra in dest, 4 mismatches,
      8+ failure.
    """
    args = [
        "robocopy", str(src), str(dst),
        "/MIR" if mirror else "/E",
        "/R:2", "/W:2",
        # Keep per-file lines (no /NFL) so we can tick the bar; suppress
        # headers, directory list, summary, classes, sizes, percentages.
        "/NDL", "/NJH", "/NJS", "/NC", "/NS", "/NP",
    ]
    print(f"  {label}: {src}\n    -> {dst}")

    total = _count_files(src) or None  # None -> indeterminate bar

    try:
        from tqdm import tqdm  # type: ignore
        bar = tqdm(total=total, unit="file", desc=label, leave=False)
        use_tqdm = True
    except Exception:
        bar = None
        use_tqdm = False

    proc = subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1,
    )
    n_seen = 0
    try:
        assert proc.stdout is not None
        for line in proc.stdout:
            line = line.rstrip()
            if not line:
                continue
            # Robocopy file lines look like:
            #   "\t   New File  \t   ...\\path\\name.ext"
            # Header/footer lines we kept suppressed; anything left is a
            # file event, so tick once per non-empty line.
            n_seen += 1
            if use_tqdm and bar is not None:
                bar.update(1)
            elif n_seen % 250 == 0:
                # Lightweight fallback: print a count every 250 files.
                print(f"    ...{n_seen} files")
    finally:
        rc = proc.wait()
        if use_tqdm and bar is not None:
            bar.close()

    if rc >= 8:
        raise SystemExit(f"ERROR: {label} failed (robocopy rc={rc})")


# ---------------------------------------------------------------------------
# Pristine bootstrap


def has_dowagermod_sentinel(live: Path) -> bool:
    return (live / SENTINEL_NAME).exists()


# The stock-mod folder names that ship with vanilla Civ4 BTS. Different
# patch/branch versions ship slightly different sets, so this is the union
# of names we've observed across versions. Anything else under
# Beyond the Sword/Mods/ is treated as third-party.
STOCK_BTS_MODS = {
    "Afterworld",
    "American Revolution",
    "Broken Star",
    "Charlemagne",
    "Crossroads of the World",
    "Defense",
    "FfH Age of Ice",
    "Final Frontier",
    "Final Frontier Plus",
    "Fury Road",
    "Gods of Old",
    "MesoAmerica",
    "Mongol Empire",
    "Next War",
    "Rhye's and Fall of Civilization",
    "Road to War",
    "The Ancient Mediterranean",
    "The Road to War",
    "World War II 1939-1945 (Solo)",
}

# Reference numbers for a complete vanilla Civ4 BTS install (from a freshly
# Steam-installed copy, original_release_unsupported branch).
# We check file count only -- it's stable across branches and locales.
EXPECTED_FILE_COUNT = 30496
# Tolerance: friends may be on a different beta branch with slightly
# different locale/EXE versions. Tight enough to catch partial downloads
# (which lose hundreds to thousands of files) and modded installs.
MIN_FILE_COUNT = 28000   # ~92% -- below this, the download is incomplete
MAX_FILE_COUNT = 33000   # ~108% -- above this, something extra is installed


def _count_install_files(live: Path) -> int:
    n = 0
    try:
        for _dp, _dn, fns in os.walk(live):
            n += len(fns)
    except OSError:
        pass
    return n


def _clean_install_problems(live: Path) -> list[str]:
    """Return a list of human-readable problems with this candidate
    pristine source. Empty list means it looks clean."""
    problems: list[str] = []

    # Must be a real BTS install
    exe = live / "Beyond the Sword" / "Civ4BeyondSword.exe"
    if not exe.exists():
        problems.append(
            f"Civ4BeyondSword.exe is missing at:\n    {exe}\n"
            "  This does not look like a real BTS install."
        )
    assets = live / "Beyond the Sword" / "Assets"
    if not assets.is_dir():
        problems.append(
            f"Beyond the Sword/Assets/ is missing at:\n    {assets}"
        )

    # Must NOT already have DowagerMod applied
    if has_dowagermod_sentinel(live):
        problems.append(
            "DowagerMod is already installed (sentinel file present at\n"
            f"    {live / SENTINEL_NAME}\n"
            "  ). Pristine must come from an UNMODIFIED Civ4 install."
        )

    # File count sanity check -- catches incomplete download / extra mods.
    n = _count_install_files(live)
    if n < MIN_FILE_COUNT:
        problems.append(
            f"Install looks INCOMPLETE: found {n:,} files, expected at least\n"
            f"  {MIN_FILE_COUNT:,} (a complete fresh install has ~{EXPECTED_FILE_COUNT:,}).\n"
            "  Steam may still be downloading, or the previous download was\n"
            "  interrupted. In Steam: right-click the game -> Properties ->\n"
            "  Installed Files -> 'Verify integrity of game files' to fix."
        )
    elif n > MAX_FILE_COUNT:
        problems.append(
            f"Install has TOO MANY files: found {n:,}, expected at most\n"
            f"  {MAX_FILE_COUNT:,} (a complete fresh install has ~{EXPECTED_FILE_COUNT:,}).\n"
            "  This usually means another mod is already installed, or the\n"
            "  install dir has accumulated extra files. Do a clean reinstall\n"
            "  (steps below)."
        )

    # Suspicious third-party mods under BTS/Mods/
    bts_mods = live / "Beyond the Sword" / "Mods"
    if bts_mods.is_dir():
        unknown = []
        for child in bts_mods.iterdir():
            if not child.is_dir():
                continue
            if child.name not in STOCK_BTS_MODS:
                unknown.append(child.name)
        if unknown:
            shown = ", ".join(sorted(unknown)[:5])
            more = "" if len(unknown) <= 5 else f" (+{len(unknown)-5} more)"
            problems.append(
                f"Third-party mod(s) found in Beyond the Sword/Mods/:\n"
                f"    {shown}{more}\n"
                "  Pristine must be a clean unmodded install."
            )

    # CustomAssets folder with content (player tweaks)
    custom = live / "Beyond the Sword" / "CustomAssets"
    if custom.is_dir():
        try:
            has_content = any(custom.iterdir())
        except OSError:
            has_content = False
        if has_content:
            problems.append(
                f"CustomAssets/ has files at:\n    {custom}\n"
                "  Player customizations can corrupt pristine. Delete this\n"
                "  folder, OR do a fresh Steam reinstall."
            )

    return problems


def _print_clean_install_instructions() -> None:
    print()
    print("=" * 60)
    print("HOW TO GET A CLEAN CIV4 BTS INSTALL")
    print("=" * 60)
    print("DowagerMod needs to capture a pristine copy of the game ONCE,")
    print("the first time you install. After that, every install/uninstall")
    print("uses that pristine copy as the source of truth -- you'll never")
    print("need to do this again.")
    print()
    print("To get a clean install:")
    print()
    print("  1. Open Steam.")
    print("  2. Find 'Sid Meier's Civilization IV: Beyond the Sword' in")
    print("     your library. Right-click it -> Manage -> Uninstall.")
    print("     Confirm. Wait for Steam to finish.")
    print()
    print("  3. IMPORTANT: After Steam says it's done, OPEN FILE EXPLORER")
    print("     and go to the install folder, e.g.:")
    print("       C:\\Program Files (x86)\\Steam\\steamapps\\common\\")
    print("       Sid Meier's Civilization IV Beyond the Sword\\")
    print("     If that folder still exists, DELETE IT MANUALLY. Steam")
    print("     often leaves leftover files behind that will contaminate")
    print("     your pristine snapshot.")
    print()
    print("  4. Back in Steam, right-click the game -> Install. Steam")
    print("     will redownload the game from scratch. Wait for the")
    print("     download to fully complete (no 'Downloading' status).")
    print()
    print("  5. (Alternative to 4) If you'd rather skip uninstalling:")
    print("     right-click -> Properties -> Installed Files -> 'Verify")
    print("     integrity of game files'. Steam will redownload anything")
    print("     missing or corrupted. Slower than a fresh install but")
    print("     safer if you've never modded the game.")
    print()
    print("  6. DO NOT launch the game from Steam yet. DO NOT install any")
    print("     other Civ4 mods on top.")
    print()
    print("  7. Re-run this installer.")
    print()
    print("=" * 60)


def capture_pristine(live: Path, pristine: Path) -> None:
    print()
    print("-" * 60)
    print("First-time pristine snapshot")
    print("-" * 60)
    print(f"No pristine snapshot found at:\n  {pristine}")
    print()
    print("Pristine = a clean copy of the original Civ4 BtS install,")
    print("used as the baseline every time DowagerMod is reinstalled.")
    print()
    print("Running automatic sanity checks on your current install...")

    problems = _clean_install_problems(live)
    if problems:
        print()
        print("PROBLEMS DETECTED with the current install:")
        print()
        for i, p in enumerate(problems, 1):
            print(f"  {i}. {p}")
        _print_clean_install_instructions()
        raise SystemExit(
            "Installer cannot proceed until the above is fixed."
        )

    n = _count_install_files(live)
    print(f"  OK: {n:,} files (expected ~{EXPECTED_FILE_COUNT:,}).")
    print("  OK: looks like a clean Civ4 BtS install.")
    print()
    print("Final confirmation: is this install COMPLETELY UNMODIFIED?")
    print("  - Freshly downloaded from Steam, OR")
    print("  - Steam-Verified with no mods/customizations applied?")
    print()
    ans = input("Capture this install as pristine? [y/N]: ").strip().lower()
    if ans != "y":
        _print_clean_install_instructions()
        raise SystemExit(
            "Aborted. Get a clean install (steps above) and re-run."
        )

    print()
    print(f"Capturing pristine snapshot (~3 GB, ~1-3 min on SSD)...")
    robocopy(live, pristine, mirror=True, label="capture pristine")
    print("Pristine snapshot captured.")


# ---------------------------------------------------------------------------
# Civ4 user data folder (My Games\Beyond the Sword)
#
# Civ4 caches XML in this folder. A stale cache will shadow our XML changes
# (e.g. icon atlas updates) and cause hard-to-debug rendering bugs. We nuke
# the folder on every install except for Saves/, then force-disable the
# cache via the .ini.

_USER_DATA_PRESERVE = {
    # User's saved games -- never touch.
    "saves",
    # The .ini we hand-edit below. If we delete it, the game recreates it
    # with DisableCaching=0 on next launch and our setting is lost.
    "civilizationiv.ini",
}


def find_user_data_dir() -> Path | None:
    """Locate Documents\\My Games\\Beyond the Sword, accounting for OneDrive
    redirection. Returns None if not found (game has never been launched)."""
    candidates: list[Path] = []
    home = Path.home()
    candidates.append(home / "Documents" / "My Games" / "Beyond the Sword")
    for env_key in ("OneDrive", "OneDriveCommercial", "OneDriveConsumer"):
        v = os.environ.get(env_key)
        if v:
            candidates.append(Path(v) / "Documents" / "My Games" / "Beyond the Sword")
    seen: set[Path] = set()
    for c in candidates:
        try:
            r = c.resolve()
        except OSError:
            continue
        if r in seen:
            continue
        seen.add(r)
        if r.is_dir():
            return r
    return None


def clean_user_data(user_data: Path) -> None:
    """Delete everything under user_data except Saves/ and CivilizationIV.ini."""
    print(f"Cleaning Civ4 user data at:\n  {user_data}")
    print("  (preserving Saves/ and CivilizationIV.ini)")
    removed_dirs = 0
    removed_files = 0
    for child in user_data.iterdir():
        if child.name.lower() in _USER_DATA_PRESERVE:
            continue
        try:
            if child.is_dir():
                shutil.rmtree(child, ignore_errors=False)
                removed_dirs += 1
            else:
                child.unlink()
                removed_files += 1
        except OSError as e:
            print(f"  WARNING: could not remove {child.name}: {e}")
    print(f"  Removed {removed_dirs} folder(s) and {removed_files} file(s).")


def ensure_disable_caching(user_data: Path) -> None:
    """Set DisableCaching = 1 in CivilizationIV.ini so the game does not
    cache XML between launches (cache shadowing causes mod XML to silently
    not take effect)."""
    ini = user_data / "CivilizationIV.ini"
    if not ini.is_file():
        # The game creates this on first launch; nothing for us to fix yet.
        # Next install run after they launch will catch it.
        print("  (CivilizationIV.ini not present yet -- will be created by")
        print("   the game on first launch. Re-run installer afterward to")
        print("   set DisableCaching = 1.)")
        return
    try:
        text = ini.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        print(f"  WARNING: could not read {ini.name}: {e}")
        return

    pattern = re.compile(r"^(\s*)DisableCaching(\s*)=(\s*)(\d+)", re.MULTILINE)
    m = pattern.search(text)
    if m is None:
        # Setting doesn't exist in the file. Don't try to add it -- the .ini
        # has section structure and we'd risk corrupting it. Tell the user
        # exactly what to fix manually.
        print(f"  WARNING: 'DisableCaching = ...' line not found in")
        print(f"  {ini}")
        print()
        print("  For safest mod behavior (prevents stale XML cache from")
        print("  shadowing DowagerMod changes), open that file in Notepad")
        print("  and under the [CONFIG] section add or set:")
        print()
        print("      DisableCaching = 1")
        print()
        return

    if m.group(4) == "1":
        print(f"  OK: DisableCaching already = 1 in {ini.name}")
        return

    new_text = pattern.sub(r"\1DisableCaching\2=\g<3>1", text, count=1)
    try:
        ini.write_text(new_text, encoding="utf-8")
    except OSError as e:
        print(f"  WARNING: could not write {ini.name}: {e}")
        return
    print(f"  Set DisableCaching = 1 in {ini.name} (was {m.group(4)})")


def clean_civ4_user_data() -> None:
    """Top-level entry point for the user-data cleanup step."""
    print()
    print("-" * 60)
    print("Cleaning Civ4 user data (XML cache + logs)")
    print("-" * 60)
    user_data = find_user_data_dir()
    if user_data is None:
        print("No user data folder found at Documents\\My Games\\Beyond the Sword")
        print("(the game probably hasn't been launched yet -- skipping).")
        return
    clean_user_data(user_data)
    ensure_disable_caching(user_data)


# ---------------------------------------------------------------------------
# Main install flow


def install(args: argparse.Namespace) -> None:
    if not is_admin():
        print(
            "WARNING: not running as administrator. Civ4 in Program Files\n"
            "needs admin rights to write. If install fails with permission\n"
            "errors, re-run as administrator."
        )

    payload_root = get_payload_root()
    if not payload_root.exists():
        raise SystemExit(
            f"ERROR: payload not found:\n  {payload_root}\n"
            "If running install.exe, ensure its data folder sits next to it."
        )

    cfg = load_config()

    # Resolve install dir
    if args.install_dir:
        live = Path(args.install_dir).resolve()
        if not live.exists():
            raise SystemExit(f"--install-dir does not exist: {live}")
        cfg["install_dir"] = str(live)
    elif "install_dir" in cfg and Path(cfg["install_dir"]).exists():
        live = Path(cfg["install_dir"])
        print(f"Using configured install dir: {live}")
    else:
        if "install_dir" in cfg:
            print(f"Configured install dir no longer exists: {cfg['install_dir']}")
            print("Rediscovering...")
            cfg.pop("install_dir", None)
            cfg.pop("pristine_dir", None)
        live = discover_install_dir()
        cfg["install_dir"] = str(live)

    # Resolve pristine dir (always sibling of live)
    pristine = Path(str(live) + PRISTINE_SUFFIX)
    cfg["pristine_dir"] = str(pristine)

    # Refresh pristine if requested
    if args.refresh_pristine and pristine.exists():
        print(f"--refresh-pristine: deleting existing pristine at {pristine}")
        shutil.rmtree(pristine)

    # Bootstrap pristine if missing
    if not pristine.exists():
        capture_pristine(live, pristine)

    save_config(cfg)

    # The actual install: wipe via /MIR from pristine, then overlay payload.
    print()
    print("-" * 60)
    print("Installing DowagerMod")
    print("-" * 60)
    robocopy(pristine, live, mirror=True, label="restore pristine")
    robocopy(payload_root, live, mirror=False, label="overlay mod payload")

    # Sentinel
    version = get_mod_version()
    sentinel = live / SENTINEL_NAME
    sentinel.write_text(
        f"DowagerMod installed.\n"
        f"Version: {version}\n"
        f"Installed at: {_dt.datetime.now().isoformat(timespec='seconds')}\n"
        f"Do not delete this file; the installer uses it as a sentinel.\n",
        encoding="utf-8",
    )

    cfg["last_mod_version"] = version
    cfg["last_install_at"] = _dt.datetime.now().isoformat(timespec="seconds")
    save_config(cfg)

    # Wipe stale XML cache + force DisableCaching=1.
    clean_civ4_user_data()

    print()
    print("=" * 60)
    print(f"DowagerMod installed (version: {version})")
    print(f"  Install dir: {live}")
    print(f"  Pristine:    {pristine}")
    print(f"  Config:      {CONFIG_FILE}")
    print("=" * 60)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="install",
        description="Install DowagerMod (wipe-and-restore from pristine snapshot).",
    )
    parser.add_argument(
        "--install-dir",
        help="Override install location (skip discovery).",
    )
    parser.add_argument(
        "--refresh-pristine",
        action="store_true",
        help="Delete existing pristine snapshot and re-capture from current "
             "live install (which must be clean).",
    )
    args = parser.parse_args(argv)

    print(BANNER)
    play_install_sound()

    print("=" * 60)
    print("DowagerMod installer")
    print("=" * 60)
    rc = 0
    try:
        install(args)
    except KeyboardInterrupt:
        print("\nAborted.")
        rc = 1
    except SystemExit as e:
        print(f"\n{e}")
        rc = 1 if e.code else 0
    except Exception as e:
        print(f"\nERROR: {e}")
        rc = 1

    # Countdown so the user has time to read the result before the window
    # closes (UAC-launched .exe owns its console; it vanishes on return).
    print()
    print("=" * 60)
    if rc == 0:
        print("Done.")
    else:
        print("Installer did NOT complete -- read the messages above.")
    print("=" * 60)
    try:
        for sec in range(15, 0, -1):
            sys.stdout.write(f"\rClosing in {sec:2d} seconds... (Ctrl+C to keep window open) ")
            sys.stdout.flush()
            time.sleep(1)
        sys.stdout.write("\n")
    except KeyboardInterrupt:
        print("\nWindow held open. Press Enter to close.")
        try:
            input()
        except (EOFError, KeyboardInterrupt):
            pass
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
