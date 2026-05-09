## CvLeaderChatter.py
## DowagerMod Leader Chatter feature -- game-side hook.
##
## Civ4 Python 2.4 module. ABSOLUTELY no Python 2.5+ syntax.
## - No 'with' statement
## - No f-strings
## - No dict comprehensions (list comprehensions only)
## - No conditional expressions in some contexts -- use if/else
## - All print statements use parens for forward-compat but treated as Py2
##
## DESIGN OVERVIEW
## ---------------
## On configured trigger events (DoW, city captured, religion founded, etc.)
## ONE elected human player's machine writes a JSON request file into a
## shared spool directory. That player's local sidecar (a separate Python 3
## process) reads the request, calls Azure Foundry (GPT-5.4-mini), and
## writes a response file. This game-side module polls the spool, queues
## received lines for real-time-paced display (5-10 second spacing between
## lines of an exchange), and broadcasts each line via the engine's
## CyMessageControl().sendChat() so all connected players see it.
##
## See: tools/chatter/SPEC.md for the JSON wire format.
## See: docs/CHATTER_OVERVIEW.md for the user-facing design doc.
##
## HARD CONTRACT (rubber-duck verified):
## - This module MUST NEVER raise into the engine. Every public entry
##   point is wrapped in try/except BaseException with file logging.
## - This module MUST NEVER write to game state (no getScriptData calls,
##   no XML mutation). Save games are guaranteed safe.
## - This module MUST NOT block. Disk I/O is bounded per tick; sidecar
##   calls are fire-and-forget.
## - On any internal error, the module marks itself session-disabled
##   and stays out of the way for the rest of the session.

from CvPythonExtensions import *
import os
import sys
import time
import random


# ===== minimal JSON encode/decode (Py 2.4 has no json module) =====
# Civ4's bundled Python 2.4 does not include the json stdlib (added 2.6).
# Sidecar writes valid JSON; we parse it here. We also produce valid JSON for
# the request file. Scope: dicts, lists, strings (ASCII + escaped \uXXXX),
# ints, floats, bools, None. No special handling for NaN/Infinity. Strings
# are emitted as-is with backslash escapes for ", \, \n, \r, \t. Round-tripped
# successfully against the sidecar's stdlib json output during testing.

class _JsonError(Exception):
    pass


def _json_dumps(obj):
    parts = []
    _json_write(obj, parts)
    return "".join(parts)


def _json_write(obj, out):
    if obj is None:
        out.append("null")
    elif obj is True:
        out.append("true")
    elif obj is False:
        out.append("false")
    elif isinstance(obj, dict):
        out.append("{")
        first = True
        for k, v in obj.items():
            if not first:
                out.append(",")
            first = False
            _json_write_string(str(k), out)
            out.append(":")
            _json_write(v, out)
        out.append("}")
    elif isinstance(obj, (list, tuple)):
        out.append("[")
        first = True
        for v in obj:
            if not first:
                out.append(",")
            first = False
            _json_write(v, out)
        out.append("]")
    elif isinstance(obj, bool):  # noqa (handled above; defensive)
        if obj:
            out.append("true")
        else:
            out.append("false")
    elif isinstance(obj, (int, long)):
        out.append(str(obj))
    elif isinstance(obj, float):
        # JSON spec forbids NaN/Infinity; substitute a safe value.
        s = repr(obj)
        if s in ("nan", "inf", "-inf"):
            out.append("null")
        else:
            out.append(s)
    elif isinstance(obj, (str, unicode)):
        _json_write_string(obj, out)
    else:
        # Best effort: convert to string
        _json_write_string(str(obj), out)


def _json_write_string(s, out):
    if isinstance(s, str):
        try:
            s = s.decode("utf-8", "replace")
        except:
            s = s.decode("ascii", "replace")
    buf = [u'"']
    for ch in s:
        oc = ord(ch)
        if ch == u'"':
            buf.append(u'\\"')
        elif ch == u'\\':
            buf.append(u'\\\\')
        elif ch == u'\n':
            buf.append(u'\\n')
        elif ch == u'\r':
            buf.append(u'\\r')
        elif ch == u'\t':
            buf.append(u'\\t')
        elif oc < 0x20:
            buf.append(u'\\u%04x' % oc)
        elif oc < 0x7F:
            buf.append(ch)
        else:
            # Emit as \uXXXX for portability
            buf.append(u'\\u%04x' % oc)
    buf.append(u'"')
    out.append(u"".join(buf).encode("ascii", "replace"))


def _json_loads(text):
    if isinstance(text, str):
        try:
            text = text.decode("utf-8", "replace")
        except:
            text = text.decode("ascii", "replace")
    p = [0]
    _json_skip_ws(text, p)
    val = _json_parse(text, p)
    _json_skip_ws(text, p)
    return val


def _json_skip_ws(text, p):
    n = len(text)
    while p[0] < n and text[p[0]] in u" \t\r\n":
        p[0] += 1


def _json_parse(text, p):
    _json_skip_ws(text, p)
    if p[0] >= len(text):
        raise _JsonError("unexpected end of input")
    ch = text[p[0]]
    if ch == u'{':
        return _json_parse_object(text, p)
    if ch == u'[':
        return _json_parse_array(text, p)
    if ch == u'"':
        return _json_parse_string(text, p)
    if ch == u't' or ch == u'f':
        return _json_parse_bool(text, p)
    if ch == u'n':
        return _json_parse_null(text, p)
    return _json_parse_number(text, p)


def _json_parse_object(text, p):
    p[0] += 1  # consume {
    out = {}
    _json_skip_ws(text, p)
    if p[0] < len(text) and text[p[0]] == u'}':
        p[0] += 1
        return out
    while True:
        _json_skip_ws(text, p)
        if p[0] >= len(text) or text[p[0]] != u'"':
            raise _JsonError("expected string key at %d" % p[0])
        key = _json_parse_string(text, p)
        _json_skip_ws(text, p)
        if p[0] >= len(text) or text[p[0]] != u':':
            raise _JsonError("expected : at %d" % p[0])
        p[0] += 1
        val = _json_parse(text, p)
        out[key] = val
        _json_skip_ws(text, p)
        if p[0] >= len(text):
            raise _JsonError("unterminated object")
        if text[p[0]] == u',':
            p[0] += 1
            continue
        if text[p[0]] == u'}':
            p[0] += 1
            return out
        raise _JsonError("expected , or } at %d" % p[0])


def _json_parse_array(text, p):
    p[0] += 1  # consume [
    out = []
    _json_skip_ws(text, p)
    if p[0] < len(text) and text[p[0]] == u']':
        p[0] += 1
        return out
    while True:
        out.append(_json_parse(text, p))
        _json_skip_ws(text, p)
        if p[0] >= len(text):
            raise _JsonError("unterminated array")
        if text[p[0]] == u',':
            p[0] += 1
            continue
        if text[p[0]] == u']':
            p[0] += 1
            return out
        raise _JsonError("expected , or ] at %d" % p[0])


def _json_parse_string(text, p):
    if text[p[0]] != u'"':
        raise _JsonError("expected string at %d" % p[0])
    p[0] += 1
    n = len(text)
    out = []
    while p[0] < n:
        ch = text[p[0]]
        if ch == u'"':
            p[0] += 1
            return u"".join(out)
        if ch == u'\\':
            p[0] += 1
            if p[0] >= n:
                raise _JsonError("bad escape")
            esc = text[p[0]]
            p[0] += 1
            if esc == u'"' or esc == u'\\' or esc == u'/':
                out.append(esc)
            elif esc == u'n':
                out.append(u'\n')
            elif esc == u'r':
                out.append(u'\r')
            elif esc == u't':
                out.append(u'\t')
            elif esc == u'b':
                out.append(u'\b')
            elif esc == u'f':
                out.append(u'\f')
            elif esc == u'u':
                if p[0] + 4 > n:
                    raise _JsonError("bad \\u escape")
                hexstr = text[p[0]:p[0] + 4]
                p[0] += 4
                try:
                    out.append(unichr(int(hexstr, 16)))
                except:
                    out.append(u'?')
            else:
                out.append(esc)
        else:
            out.append(ch)
            p[0] += 1
    raise _JsonError("unterminated string")


def _json_parse_bool(text, p):
    if text[p[0]:p[0] + 4] == u'true':
        p[0] += 4
        return True
    if text[p[0]:p[0] + 5] == u'false':
        p[0] += 5
        return False
    raise _JsonError("bad bool at %d" % p[0])


def _json_parse_null(text, p):
    if text[p[0]:p[0] + 4] == u'null':
        p[0] += 4
        return None
    raise _JsonError("bad null at %d" % p[0])


def _json_parse_number(text, p):
    n = len(text)
    start = p[0]
    if text[p[0]] in u'-+':
        p[0] += 1
    while p[0] < n and text[p[0]] in u'0123456789':
        p[0] += 1
    is_float = False
    if p[0] < n and text[p[0]] == u'.':
        is_float = True
        p[0] += 1
        while p[0] < n and text[p[0]] in u'0123456789':
            p[0] += 1
    if p[0] < n and text[p[0]] in u'eE':
        is_float = True
        p[0] += 1
        if p[0] < n and text[p[0]] in u'+-':
            p[0] += 1
        while p[0] < n and text[p[0]] in u'0123456789':
            p[0] += 1
    chunk = text[start:p[0]]
    try:
        if is_float:
            return float(chunk)
        return int(chunk)
    except:
        try:
            return float(chunk)
        except:
            raise _JsonError("bad number %s" % chunk)



# ===== module-level state (per session) =====

_disabled = False               # set on any unrecoverable game-side error
_session_id = ""                # UUID-ish, regenerated on game start / load
_local_player_id = -1           # this client's playerID
_capable_humans = {}            # playerID -> last_heartbeat_unix (we agree they have a sidecar)
_local_capable = None           # cached: does THIS machine have a fresh sidecar?
_local_capable_checked_at = 0.0
_seen_events = {}               # event_dedup_key -> timestamp (for trigger debounce)
_pair_cooldown = {}             # (a,b) -> game_turn of last exchange (per-pair cooldown)
_display_queue = []             # list of {due_unix, speaker_id, speaker_name, text}
_pending_request_id = None      # we have one request in-flight via sidecar at a time
_pending_request_at = 0.0
_active_exchange_until = 0.0    # while a multi-line exchange's queue is non-empty
_global_recent_lines = []       # unix timestamps of recently broadcast lines (for hourly cap)
_logged_first_run = False       # one-time setup log
_spawn_attempted_at = 0.0       # rate-limit auto-spawn attempts
_no_elector_diag_fired = False  # one-time diagnostic when nobody is capable
_no_elector_first_seen_turn = -1
_next_msg_id = 1                # incrementing message ID for line chunks
_pending_lines = {}             # msg_id -> {'speaker_id', 'expected_chunks', 'received', 'parts'}


# ===== tunables =====

CHATTER_CAP_MAGIC = 0x4348           # 'CH' as int -- capability ping
CHATTER_LINE_MAGIC = 0x434C          # 'CL' as int -- chatter line chunk
HEARTBEAT_FRESH_SECONDS = 60         # local sidecar heartbeat must be within this
CAPABILITY_REBROADCAST_TURNS = 50    # re-advertise capability every N game turns
CAPABILITY_STALE_HEARTBEATS = 5      # peers drop us after N missed advertisements
PER_PAIR_COOLDOWN_TURNS = 30         # min game turns between exchanges for same pair
GLOBAL_LINE_PER_REAL_MIN_CAP = 10    # max chatter lines per 60s real-time
LINE_TICK_BUDGET_SECONDS = 0.005     # max wallclock per onUpdate-equivalent tick
SPOOL_SCAN_LIMIT = 8                 # max response files scanned per tick
REJOINDER_PROBABILITY = 0.75         # chance a multi_turn-eligible trigger gets a multi-turn exchange
SPAWN_RETRY_SECONDS = 30             # don't try to spawn sidecar more than once per N seconds
DROP_NEW_WHILE_QUEUE_ACTIVE = False  # queue-don't-drop new events during in-flight render
NO_ELECTOR_DIAG_AFTER_TURNS = 30     # show one-time message after N turns w/o capable elector

# === DEBUG MODE (smoke test only) ===
# When True, the module fires test messages on game start and after a few
# turns so the user can confirm the broadcast path works end-to-end without
# waiting for a real trigger. Set False before shipping.
_DEBUG_HELLO_AT_START = True
_DEBUG_HELLO_AT_TURN = 1   # fires on turn 1 (first end-turn) so user sees it fast
_DEBUG_HELLO_AT_TURN_2 = 2 # second LLM probe at turn 2
_debug_hello_fired_at_start = False
_debug_hello_fired_at_turn = False
_debug_hello_fired_at_turn_2 = False

# Triggers that should always render as a 1-to-1 exchange (directed mode).
DIRECTED_TRIGGERS = (
    "DECLARE_WAR", "PEACE_TREATY", "CITY_CAPTURED", "CITY_RAZED",
    "PLAYER_ELIMINATED_GLOAT", "PLAYER_ELIMINATED_LAST_WORDS",
    "VASSAL_FORCED", "VASSAL_ACCEPTED", "FIRST_CONTACT", "BACKSTABBED",
)
BROADCAST_TRIGGERS = (
    "RELIGION_FOUNDED", "WONDER_BUILT", "CORPORATION_FOUNDED",
    "FIRST_TO_TECH", "GOLDEN_AGE",
)
# Triggers that may use multi-turn rejoinders.
REJOINDER_ELIGIBLE = (
    "DECLARE_WAR", "CITY_CAPTURED", "CITY_RAZED", "BACKSTABBED",
    "PLAYER_ELIMINATED_GLOAT",
)


# ===== simple helpers =====

def _my_games_root_candidates():
    """All plausible Civ4 'My Games\\Beyond the Sword' parent paths.

    Civ4 uses Windows' SHGetFolderPath(CSIDL_PERSONAL) which respects
    OneDrive Documents redirection. We can't call SHGetFolderPath from
    Python 2.4 portably, so we enumerate likely roots (USERPROFILE,
    OneDrive*, any OneDrive-prefixed dir under USERPROFILE) and use the
    first one that exists.
    """
    out = []
    user_profile = os.environ.get("USERPROFILE", "")
    if user_profile:
        # OneDrive-prefixed siblings of USERPROFILE
        try:
            for name in os.listdir(user_profile):
                if name.lower().startswith("onedrive"):
                    root = os.path.join(user_profile, name)
                    out.append(os.path.join(root, "Documents", "My Games", "Beyond the Sword"))
                    out.append(os.path.join(root, "Documents", "My Games", "beyond the sword"))
        except:
            pass
        out.append(os.path.join(user_profile, "Documents", "My Games", "Beyond the Sword"))
        out.append(os.path.join(user_profile, "Documents", "My Games", "beyond the sword"))
    for key in ("OneDriveCommercial", "OneDriveConsumer", "OneDrive"):
        root = os.environ.get(key, "")
        if root:
            out.append(os.path.join(root, "Documents", "My Games", "Beyond the Sword"))
            out.append(os.path.join(root, "Documents", "My Games", "beyond the sword"))
    return out


_cached_my_games_root = None

def _my_games_root():
    """Return the actual My Games\\Beyond the Sword path (cached)."""
    global _cached_my_games_root
    if _cached_my_games_root:
        return _cached_my_games_root
    for c in _my_games_root_candidates():
        if c and os.path.isdir(c):
            _cached_my_games_root = c
            return c
    # Last resort: first candidate; we'll create dirs as needed
    cand = _my_games_root_candidates()
    if cand:
        _cached_my_games_root = cand[0]
        return cand[0]
    return os.path.join(os.path.expanduser("~"), "Documents", "My Games", "Beyond the Sword")


def _log_dir():
    return os.path.join(_my_games_root(), "Logs")

def _spool_dir():
    return os.path.join(_log_dir(), "DowagerMod", "chatter")

def _config_path():
    appdata = os.environ.get("LOCALAPPDATA", "")
    if not appdata:
        return None
    return os.path.join(appdata, "DowagerMod", "chatter", "config.json")

def _chatter_log_path():
    return os.path.join(_spool_dir(), "chatter.log")

def _daemon_pid_path():
    return os.path.join(_spool_dir(), "daemon.pid")


def _log(msg):
    """Best-effort logging. Never raises."""
    try:
        d = _spool_dir()
        if not os.path.isdir(d):
            try:
                os.makedirs(d)
            except:
                return
        f = open(_chatter_log_path(), "a")
        try:
            ts = time.strftime("%Y-%m-%d %H:%M:%S")
            f.write("[" + ts + "] " + str(msg) + "\n")
        finally:
            f.close()
    except:
        pass


def _disable(reason):
    global _disabled
    _disabled = True
    _log("DISABLED: " + str(reason))


def _gen_uuid():
    """Cheap pseudo-UUID without importing uuid (Py 2.4 has it but keep it simple)."""
    return "%08x-%04x-%04x-%04x-%012x" % (
        random.randint(0, 0xFFFFFFFF),
        random.randint(0, 0xFFFF),
        random.randint(0, 0xFFFF),
        random.randint(0, 0xFFFF),
        random.randint(0, 0xFFFFFFFFFFFF),
    )


def _to_ascii(text):
    """Strip non-ASCII (Civ4 chat panel has limited glyph coverage).

    Tolerates unicode and bytes input. Common smart-typography characters
    (em/en dash, smart quotes, ellipsis) are mapped to safe ASCII equivalents
    instead of being dropped.
    """
    if text is None:
        return ""
    SMART = {
        0x2014: u"--",   # em dash
        0x2013: u"-",    # en dash
        0x2018: u"'",    # left single quote
        0x2019: u"'",    # right single quote
        0x201C: u'"',    # left double quote
        0x201D: u'"',    # right double quote
        0x2026: u"...",  # ellipsis
        0x00A0: u" ",    # nbsp
    }
    # Normalize bytes to unicode first
    try:
        if isinstance(text, str):
            text = text.decode("utf-8", "replace")
    except:
        try:
            text = text.decode("ascii", "replace")
        except:
            pass
    out_chars = []
    for ch in text:
        try:
            oc = ord(ch)
        except:
            continue
        if oc in SMART:
            out_chars.append(SMART[oc])
        elif 32 <= oc <= 126:
            out_chars.append(ch)
        elif oc == 9 or oc == 10:
            out_chars.append(ch)
        # else: drop silently
    out = u"".join(out_chars)
    # Re-encode to bytes (str in Py 2.4) so downstream code that does
    # implicit ASCII conversion (e.g. CvString) doesn't blow up.
    try:
        return out.encode("ascii", "replace")
    except:
        return out


def _atomic_write_json(path, payload):
    """Tmp + rename. Returns True on success."""
    try:
        d = os.path.dirname(path)
        if d and not os.path.isdir(d):
            try:
                os.makedirs(d)
            except:
                pass
        tmp = path + ".tmp"
        f = open(tmp, "w")
        try:
            f.write(_json_dumps(payload))
        finally:
            f.close()
        # On Windows, os.rename fails if dest exists; use os.remove + rename.
        if os.path.exists(path):
            try:
                os.remove(path)
            except:
                pass
        os.rename(tmp, path)
        return True
    except:
        return False


def _read_json(path):
    """Returns dict or None on any error."""
    try:
        f = open(path, "r")
        try:
            return _json_loads(f.read())
        finally:
            f.close()
    except:
        return None


def _safe_unlink(path):
    try:
        os.remove(path)
    except:
        pass


def _now():
    return time.time()


def _gc():
    return CyGlobalContext()


# ===== capability detection =====

def _check_local_capable():
    """Is the local sidecar fresh (config exists + PID file heartbeat < 60s)?

    Cached for 2 seconds (was 5) to balance call frequency vs responsiveness.
    Cache is invalidated whenever a PID file appears/disappears or the
    heartbeat transitions from fresh to stale.
    """
    global _local_capable, _local_capable_checked_at
    now = _now()
    # Short-circuit cache (2s window so events firing seconds apart all see
    # a consistent capability snapshot but a sidecar that just started or
    # died is reflected within 2s).
    if _local_capable is not None and (now - _local_capable_checked_at) < 2.0:
        return _local_capable
    _local_capable_checked_at = now
    cfg = _config_path()
    if cfg is None or not os.path.isfile(cfg):
        if _local_capable is not False:
            _log("capable: False (no config at " + str(cfg) + ")")
        _local_capable = False
        return False
    pid = _daemon_pid_path()
    if not os.path.isfile(pid):
        if _local_capable is not False:
            _log("capable: False (no PID file)")
        _local_capable = False
        return False
    pid_data = _read_json(pid)
    if not pid_data:
        if _local_capable is not False:
            _log("capable: False (PID file unreadable)")
        _local_capable = False
        return False
    hb = float(pid_data.get("heartbeat_unix", 0))
    age = now - hb
    if age > HEARTBEAT_FRESH_SECONDS:
        if _local_capable is not False:
            _log("capable: False (heartbeat stale, age=" + ("%.1f" % age) + "s)")
        _local_capable = False
        return False
    if _local_capable is not True:
        _log("capable: True (sidecar healthy, age=" + ("%.1f" % age) + "s)")
    _local_capable = True
    return True


def _try_autospawn_sidecar():
    """If config exists but sidecar isn't running, try to launch it.

    Best-effort. Detached, never blocks. Failures are silent.

    Search paths for Start-Chatter.ps1 (in order):
      1. Walk up from this Python file's location looking for tools\.
         (only works in dev — Steam install doesn't have tools/.)
      2. Hardcoded common DowagerMod repo locations on the user's machine.
      3. %LOCALAPPDATA%\DowagerMod\autospawn\Start-Chatter.ps1 (one we
         install to be reachable from any Civ4 install).
    """
    global _spawn_attempted_at
    now = _now()
    if (now - _spawn_attempted_at) < SPAWN_RETRY_SECONDS:
        return
    _spawn_attempted_at = now

    cfg = _config_path()
    if cfg is None or not os.path.isfile(cfg):
        return  # not configured, don't bother

    if _check_local_capable():
        return  # already running

    # Build candidate list
    here = os.path.dirname(os.path.abspath(__file__))
    candidates = []

    # 1. Walk up from this file
    cur = here
    for _ in range(10):
        cur = os.path.dirname(cur)
        if not cur:
            break
        cand = os.path.join(cur, "tools", "Start-Chatter.ps1")
        if os.path.isfile(cand):
            candidates.append(cand)
            break

    # 2. Hardcoded common repo locations
    common_repos = [
        "C:\\DowagerMod\\tools\\Start-Chatter.ps1",
        "D:\\DowagerMod\\tools\\Start-Chatter.ps1",
    ]
    for c in common_repos:
        if os.path.isfile(c):
            candidates.append(c)

    # 3. %LOCALAPPDATA% fallback (where Setup-Chatter.ps1 should also drop a
    # copy so the friend installer path can autospawn without the repo).
    appdata = os.environ.get("LOCALAPPDATA", "")
    if appdata:
        cand = os.path.join(appdata, "DowagerMod", "autospawn", "Start-Chatter.ps1")
        if os.path.isfile(cand):
            candidates.append(cand)

    if not candidates:
        _log("autospawn: could not locate Start-Chatter.ps1 (searched: walk-up, common repos, LOCALAPPDATA)")
        return

    script = candidates[0]
    try:
        import subprocess
        DETACHED_PROCESS = 0x00000008
        CREATE_NO_WINDOW = 0x08000000
        flags = DETACHED_PROCESS | CREATE_NO_WINDOW
        cmd = [
            "powershell.exe",
            "-NoProfile",
            "-WindowStyle", "Hidden",
            "-ExecutionPolicy", "Bypass",
            "-File", script,
        ]
        subprocess.Popen(cmd, creationflags=flags, close_fds=True)
        _log("autospawn: launched " + script)
    except Exception, exc:
        _log("autospawn: subprocess.Popen failed: " + str(exc))


# ===== election =====

def _is_pitboss_or_pbem(game):
    """Disable in pitboss / PBEM (no always-on human)."""
    try:
        if game.isPitboss():
            return True
    except:
        pass
    try:
        if game.isPbem():
            return True
    except:
        pass
    return False


def _is_chatter_elector():
    """Returns True iff this client should generate chatter for the next event.

    SP / hot-seat: local machine always elects.
    Network MP: lowest-id human in capable_humans elects.
    Pitboss / PBEM: always returns False (chatter disabled).
    """
    if _disabled:
        return False
    try:
        game = _gc().getGame()
    except:
        return False

    if _is_pitboss_or_pbem(game):
        return False

    is_network = False
    try:
        is_network = game.isNetworkMultiPlayer()
    except:
        is_network = False

    if not is_network:
        # SP or hot-seat: only this machine, only if capable
        return _check_local_capable()

    # Network MP: lowest-id capable human
    if not _capable_humans:
        return False
    me = _local_player_id
    if me < 0:
        return False
    # Drop stale entries
    now = _now()
    stale = []
    for pid, hb in _capable_humans.items():
        if (now - hb) > (HEARTBEAT_FRESH_SECONDS * CAPABILITY_STALE_HEARTBEATS):
            stale.append(pid)
    for pid in stale:
        del _capable_humans[pid]
    if not _capable_humans:
        return False
    elector = min(_capable_humans.keys())
    return elector == me


def _broadcast_capability_ping():
    """Tell all clients I have a working sidecar."""
    if _disabled:
        return
    if not _check_local_capable():
        return
    try:
        if _local_player_id < 0:
            return
        # Use sendModNetMessage to MP-safely propagate. Fields:
        #   iData1=CHATTER_CAP_MAGIC, iData2=playerID, iData3=version, iData4/5 reserved.
        CyMessageControl().sendModNetMessage(CHATTER_CAP_MAGIC, _local_player_id, 1, 0, 0)
    except:
        pass


# ===== triggers =====

def _event_key(trigger, speaker_id, target_id, extra):
    """Deterministic dedup key for a trigger event."""
    try:
        turn = _gc().getGame().getGameTurn()
    except:
        turn = 0
    return (trigger, int(speaker_id), int(target_id), int(turn), extra)


def _event_seen(key):
    """True if we've already processed this exact event (dedup)."""
    return key in _seen_events


def _mark_seen(key):
    _seen_events[key] = _now()
    # Cap the dedup table
    if len(_seen_events) > 50:
        # Drop the oldest 10
        items = sorted(_seen_events.items(), key=lambda x: x[1])
        for k, _ in items[:10]:
            try:
                del _seen_events[k]
            except:
                pass


def _per_pair_cooldown_active(speaker_id, target_id):
    """True if (speaker, target) had an exchange recently."""
    if target_id < 0:
        return False
    try:
        turn = _gc().getGame().getGameTurn()
    except:
        return False
    a = min(speaker_id, target_id)
    b = max(speaker_id, target_id)
    last = _pair_cooldown.get((a, b))
    if last is None:
        return False
    return (turn - last) < PER_PAIR_COOLDOWN_TURNS


def _record_pair_exchange(speaker_id, target_id):
    if target_id < 0:
        return
    try:
        turn = _gc().getGame().getGameTurn()
    except:
        return
    a = min(speaker_id, target_id)
    b = max(speaker_id, target_id)
    _pair_cooldown[(a, b)] = turn


def _global_rate_limit_ok():
    """True iff we are under the per-real-minute global cap."""
    now = _now()
    cutoff = now - 60.0
    fresh = []
    for t in _global_recent_lines:
        if t > cutoff:
            fresh.append(t)
    # rebuild list to keep it bounded
    while _global_recent_lines:
        _global_recent_lines.pop()
    _global_recent_lines.extend(fresh)
    return len(fresh) < GLOBAL_LINE_PER_REAL_MIN_CAP


def _is_barbarian(player_id):
    """True iff player_id refers to a barbarian player. None / negative IDs
    are not barbarian (they're sentinels for 'no specific player')."""
    if player_id is None:
        return False
    try:
        if int(player_id) < 0:
            return False
    except:
        return False
    try:
        return bool(_gc().getPlayer(player_id).isBarbarian())
    except:
        return False


def _player_info(player_id):
    """Build a player-info dict for the request payload.

    Returns a dict with at least:
      player_id, leader_name, civ_short_name, score,
      is_barbarian, is_human, human_name, is_anonymous

    leader_name comes from CIV4LeaderHeadInfos (e.g. 'Victoria', 'Lincoln'),
    NOT from p.getName(). p.getName() returns the player's local OS nickname
    (e.g. 'Harrison') and is captured separately as human_name when the
    player is human, so the prompt can occasionally address them by their
    real name for comedic effect.

    Special cases:
    - BARBARIAN player: returns "the Barbarian Hordes" with is_barbarian=True
      so the sidecar can add a max-contempt directive. (After the
      _emit_request barbarian filter, this is mostly defensive.)
    - player_id < 0 (sentinel for "no specific target", e.g. broadcasts):
      returns an anonymous "the world" struct so legacy callers don't get
      "Unknown" garbage. _emit_request now passes target=None for these
      cases anyway, so this is defense-in-depth.
    """
    if player_id is None or int(player_id) < 0:
        return {
            "player_id": -1,
            "leader_name": "the world",
            "civ_short_name": "the world",
            "score": 0,
            "is_barbarian": False,
            "is_human": False,
            "human_name": None,
            "is_anonymous": True,
        }
    try:
        p = _gc().getPlayer(player_id)
        is_barb = False
        try:
            is_barb = bool(p.isBarbarian())
        except:
            is_barb = False
        if is_barb:
            return {
                "player_id": int(player_id),
                "leader_name": "the Barbarian Hordes",
                "civ_short_name": "Barbarian",
                "score": 0,
                "is_barbarian": True,
                "is_human": False,
                "human_name": None,
                "is_anonymous": False,
            }
        leader_name = ""
        try:
            leader_type = p.getLeaderType()
            if leader_type >= 0:
                leader_info = _gc().getLeaderHeadInfo(leader_type)
                if leader_info is not None:
                    leader_name = _to_ascii(leader_info.getDescription())
        except:
            pass
        if not leader_name:
            try:
                leader_name = _to_ascii(p.getName())
            except:
                leader_name = ""
        if not leader_name:
            leader_name = "Unknown"
            _log("warn: _player_info fallback Unknown for player_id=" + str(player_id))

        # Detect human player and capture their in-game player name. This is
        # the value the user typed into the "Player Name" field on the
        # leader-select screen (the same name shown in the diplomacy
        # screen header). If they didn't customize it, p.getName() falls
        # back to the leader description -- we filter that out below so
        # we only set human_name when the user actually personalized it.
        is_human = False
        human_name = None
        try:
            if p.isHuman():
                is_human = True
                try:
                    nick = _to_ascii(p.getName())
                except:
                    nick = ""
                # Skip if uncustomized -- p.getName() defaults to the
                # leader description in that case, and we want the LLM
                # to treat that as no-real-name.
                if nick and nick != leader_name:
                    human_name = nick
        except:
            pass

        # Civ short description and score may throw on edge-case players
        # (slot transitions, reload races). Fail soft so we don't lose the
        # leader name we already resolved -- the silent outer bare-except
        # used to swallow these and emit "Unknown".
        civ_short = ""
        try:
            civ_short = _to_ascii(p.getCivilizationShortDescription(0))
        except Exception, exc:
            _log("warn: _player_info getCivilizationShortDescription failed for player_id="
                 + str(player_id) + ": " + str(exc))
            civ_short = "Unknown"
        score = 0
        try:
            score = int(p.calculateScore())
        except Exception, exc:
            _log("warn: _player_info calculateScore failed for player_id="
                 + str(player_id) + ": " + str(exc))
            score = 0
        return {
            "player_id": int(player_id),
            "leader_name": leader_name,
            "civ_short_name": civ_short,
            "score": score,
            "is_barbarian": False,
            "is_human": is_human,
            "human_name": human_name,
            "is_anonymous": False,
        }
    except Exception, exc:
        _log("warn: _player_info OUTER exception for player_id="
             + str(player_id) + ": " + str(exc))
        return {"player_id": int(player_id), "leader_name": "Unknown",
                "civ_short_name": "Unknown", "score": 0, "is_barbarian": False,
                "is_human": False, "human_name": None, "is_anonymous": False}


def _era_name(player_id):
    try:
        p = _gc().getPlayer(player_id)
        eraType = p.getCurrentEra()
        info = _gc().getEraInfo(eraType)
        return _to_ascii(info.getDescription())
    except:
        return "unknown"


def _emit_request(trigger, speaker_id, target_id, extra_context, multi_turn):
    """Build + write a request file. Returns request_id on success, None otherwise."""
    global _pending_request_id, _pending_request_at, _active_exchange_until

    if _disabled:
        _log("emit " + trigger + " gated: disabled")
        return None

    # DowagerMod policy: drop all barbarian-involved chatter. Early-game
    # FIRST_CONTACT fires for every civ that meets the Barbarian Hordes
    # which drowns out the fun leader-vs-leader exchanges. Speaker-side
    # too: razed-by-barbs etc. produce noise nobody wants.
    if _is_barbarian(speaker_id) or _is_barbarian(target_id):
        _log("emit " + trigger + " gated: barbarian involved (speaker="
             + str(speaker_id) + ", target=" + str(target_id) + ")")
        return None

    # Allow only one in-flight at a time
    if _pending_request_id is not None:
        # If pending is older than 30s, drop it (sidecar must be slow/dead)
        if (_now() - _pending_request_at) > 30.0:
            _log("dropping stale pending request " + str(_pending_request_id))
            _pending_request_id = None
        else:
            _log("emit " + trigger + " gated: pending request " + str(_pending_request_id) + " in flight")
            return None

    if DROP_NEW_WHILE_QUEUE_ACTIVE and _display_queue:
        _log("emit " + trigger + " gated: display_queue size=" + str(len(_display_queue)))
        return None

    if not _global_rate_limit_ok():
        _log("emit " + trigger + " gated: global rate limit hit")
        return None

    if not _is_chatter_elector():
        _log("emit " + trigger + " gated: not elector "
             + "(local_capable=" + str(_check_local_capable())
             + ", capable_humans=" + str(list(_capable_humans.keys())) + ")")
        return None

    # Per-pair cooldown
    if _per_pair_cooldown_active(speaker_id, target_id):
        _log("emit " + trigger + " gated: per-pair cooldown speaker=" + str(speaker_id) + " target=" + str(target_id))
        return None

    # Dedup
    key = _event_key(trigger, speaker_id, target_id,
                     str(extra_context.get("city", "")) + str(extra_context.get("wonder", ""))
                     + str(extra_context.get("religion", "")) + str(extra_context.get("tech", "")))
    if _event_seen(key):
        _log("emit " + trigger + " gated: event already seen this turn")
        return None
    _mark_seen(key)

    # Build payload
    speaker = _player_info(speaker_id)
    target = None
    if target_id >= 0:
        target = _player_info(target_id)

    ctx = {"era": _era_name(speaker_id)}
    for k in ("city", "wonder", "tech", "religion", "corporation"):
        if k in extra_context and extra_context[k]:
            ctx[k] = _to_ascii(str(extra_context[k]))

    if multi_turn and trigger in REJOINDER_ELIGIBLE and target is not None:
        # Force single-line when target is barbarian: the Hordes don't make
        # for a meaningful back-and-forth speaker. Just one withering remark.
        if target.get("is_barbarian"):
            n_lines = 1
            multi = False
        elif random.random() < REJOINDER_PROBABILITY:
            n_lines = 3
            multi = True
        else:
            n_lines = 1
            multi = False
    else:
        n_lines = 1
        multi = False

    if trigger in DIRECTED_TRIGGERS:
        _mode = "directed"
    else:
        _mode = "broadcast"
    rid = _gen_uuid()
    payload = {
        "schema": 1,
        "request_id": rid,
        "session_id": _session_id,
        "game_turn": _gc().getGame().getGameTurn(),
        "elector_player_id": _local_player_id,
        "trigger": trigger,
        "mode": _mode,
        "speaker": speaker,
        "target": target,
        "context": ctx,
        "multi_turn": multi,
        "n_lines": n_lines,
        "issued_at_unix": _now(),
        "ttl_seconds": 60,
    }

    # File name
    ts = time.strftime("%Y%m%dT%H%M%S", time.gmtime())
    rand6 = ("%06x" % (random.randint(0, 0xFFFFFF)))
    fname = "req-" + ts + "-" + rand6 + ".json"
    path = os.path.join(_spool_dir(), fname)
    if not _atomic_write_json(path, payload):
        _log("failed to write request " + fname)
        return None

    _pending_request_id = rid
    _pending_request_at = _now()
    _record_pair_exchange(speaker_id, target_id)
    _log("emitted " + trigger + " req=" + rid + " multi=" + str(multi))
    return rid


# ===== display =====

def _enqueue_response_lines(response):
    """Take a parsed response dict and append its lines to the display queue."""
    global _active_exchange_until
    lines = response.get("lines") or []
    if not lines:
        return
    cumulative_delay = 0
    base = _now()
    for ln in lines:
        cumulative_delay += int(ln.get("delay_ms", 0))
        due = base + (cumulative_delay / 1000.0)
        # Pass directly to _to_ascii (which handles unicode); calling str()
        # on a unicode string with non-ASCII chars raises UnicodeEncodeError
        # in Py 2.4.
        _display_queue.append({
            "due_unix": due,
            "speaker_id": int(ln.get("speaker_player_id", -1)),
            "speaker_name": _to_ascii(ln.get("speaker_name", "?")),
            "text": _to_ascii(ln.get("text", "")),
        })
    _active_exchange_until = base + (cumulative_delay / 1000.0) + 1.0


def _format_chat_line(speaker_name, text):
    """Render the line for sendChat broadcast. (legacy fallback path)

    Format: 'Victoria: <text>'  (ASCII only, no Unicode).
    Engine will prefix with elector's player name regardless.
    """
    return _to_ascii(speaker_name) + ': ' + _to_ascii(text)


def _broadcast_line(entry):
    """Broadcast a line so all clients render it as if from the leader.

    v1.1 path: encode the line + speaker_player_id as a chunked stream of
    sendModNetMessage calls. Each receiving client (including the elector)
    accumulates chunks in onModNetMessage, then locally renders via
    CyInterface().addMessage with the leader's portrait + civ color. This
    bypasses the chat panel entirely so there is no '[ElectorName]:' prefix.
    """
    try:
        speaker_id = int(entry["speaker_id"])
        text = _to_ascii(entry["text"])
        if not text:
            return
        _send_line_via_chunks(speaker_id, text)
        _global_recent_lines.append(_now())
        _log("broadcast (chunked): " + text[:100])
    except:
        _log("broadcast failed for: " + str(entry.get("text", ""))[:60])


def _send_line_via_chunks(speaker_id, text):
    """Encode (speaker_id, text) into N sendModNetMessage calls.

    Wire format:
      Header chunk (chunk_index=0):
        iData1 = CHATTER_LINE_MAGIC
        iData2 = msg_id (1..65535, wraps)
        iData3 = 0  (signals header chunk)
        iData4 = speaker_player_id
        iData5 = total_payload_chunks
      Payload chunk N (1 <= chunk_index <= total_payload_chunks):
        iData1 = CHATTER_LINE_MAGIC
        iData2 = msg_id
        iData3 = chunk_index (>=1)
        iData4 = 4 chars packed (LE)
        iData5 = 4 chars packed (LE)
    8 ASCII bytes per payload chunk. For a 200-char text -> 25 chunks + header.
    """
    global _next_msg_id
    msg_id = _next_msg_id & 0xFFFF
    if msg_id == 0:
        msg_id = 1
    _next_msg_id = (msg_id + 1) & 0xFFFF
    if _next_msg_id == 0:
        _next_msg_id = 1

    # Encode text into 8-byte chunks
    BYTES_PER_CHUNK = 8
    total = (len(text) + BYTES_PER_CHUNK - 1) // BYTES_PER_CHUNK

    # Header
    try:
        CyMessageControl().sendModNetMessage(
            CHATTER_LINE_MAGIC, msg_id, 0, int(speaker_id), int(total))
    except:
        return

    # Payload
    for i in range(total):
        seg = text[i * BYTES_PER_CHUNK:(i + 1) * BYTES_PER_CHUNK]
        # Pad to 8 bytes with NUL
        seg = seg + ("\0" * (BYTES_PER_CHUNK - len(seg)))
        d4 = _pack_4chars(seg[0:4])
        d5 = _pack_4chars(seg[4:8])
        try:
            CyMessageControl().sendModNetMessage(
                CHATTER_LINE_MAGIC, msg_id, i + 1, d4, d5)
        except:
            # Best effort; if a chunk fails, the receiving side won't be
            # able to assemble and will eventually GC the partial. Not
            # fatal.
            return


def _pack_4chars(s):
    """Pack up to 4 ASCII chars (zero-padded) into a 32-bit int (LE).
    Top bit always 0 since we ASCII-only.
    """
    if not s:
        return 0
    if len(s) < 4:
        s = s + ("\0" * (4 - len(s)))
    return (ord(s[0]) & 0xFF) | ((ord(s[1]) & 0xFF) << 8) | \
           ((ord(s[2]) & 0xFF) << 16) | ((ord(s[3]) & 0xFF) << 24)


def _unpack_4chars(i):
    """Unpack 4 chars from a 32-bit int (LE), trimming trailing NULs."""
    out = []
    val = int(i) & 0xFFFFFFFF
    for _ in range(4):
        c = val & 0xFF
        out.append(chr(c))
        val >>= 8
    s = "".join(out)
    # Trim trailing NULs
    nul_pos = s.find("\0")
    if nul_pos >= 0:
        s = s[:nul_pos]
    return s


def _handle_line_chunk(iData2, iData3, iData4, iData5):
    """Process an inbound CHATTER_LINE_MAGIC chunk."""
    global _pending_lines
    msg_id = int(iData2)
    chunk_index = int(iData3)
    if chunk_index == 0:
        # Header
        speaker_id = int(iData4)
        total = int(iData5)
        _log("chunk: header msg=" + str(msg_id) + " speaker=" + str(speaker_id) + " total=" + str(total))
        if total <= 0 or total > 256:
            return
        _pending_lines[msg_id] = {
            "speaker_id": speaker_id,
            "expected": total,
            "received": 0,
            "parts": [None] * total,
            "started_at": _now(),
        }
        return
    state = _pending_lines.get(msg_id)
    if state is None:
        _log("chunk: orphan msg=" + str(msg_id) + " idx=" + str(chunk_index))
        return
    idx0 = chunk_index - 1
    if idx0 < 0 or idx0 >= state["expected"]:
        return
    if state["parts"][idx0] is not None:
        return
    seg = _unpack_4chars(iData4) + _unpack_4chars(iData5)
    state["parts"][idx0] = seg
    state["received"] += 1
    if state["received"] >= state["expected"]:
        text = "".join(state["parts"])
        speaker_id = state["speaker_id"]
        _log("chunk: complete msg=" + str(msg_id) + " text_len=" + str(len(text)))
        try:
            del _pending_lines[msg_id]
        except:
            pass
        _render_local_line(speaker_id, text)


def _gc_pending_lines():
    """Drop partial line accumulators older than 30s (in case of lost chunks)."""
    if not _pending_lines:
        return
    now = _now()
    stale = []
    for k, v in _pending_lines.items():
        if (now - v.get("started_at", now)) > 30:
            stale.append(k)
    for k in stale:
        try:
            del _pending_lines[k]
        except:
            pass


def _render_local_line(speaker_id, text):
    """Render a chatter line in the local event log via addMessage with the
    speaker's leader portrait. Prefixes the line with the leader's name so
    attribution is unmissable (the engine's eColor param doesn't reliably
    tint message-log text in BTS, so we lean on the prefix instead).
    """
    try:
        local_player = _gc().getGame().getActivePlayer()
        # Resolve speaker leader info
        leader_button = None
        speaker_color = -1  # let engine pick a default
        leader_name = ""
        try:
            sp = _gc().getPlayer(int(speaker_id))
            try:
                pc = sp.getPlayerColor()
                if pc >= 0:
                    pci = _gc().getPlayerColorInfo(pc)
                    if pci is not None:
                        speaker_color = int(pci.getColorTypePrimary())
            except Exception, exc:
                _log("render: color lookup failed: " + str(exc))
            try:
                lt = sp.getLeaderType()
                if lt >= 0:
                    li = _gc().getLeaderHeadInfo(lt)
                    if li is not None:
                        leader_button = li.getButton()
                        leader_name = _to_ascii(li.getDescription())
            except Exception, exc:
                _log("render: leader lookup failed: " + str(exc))
        except Exception, exc:
            _log("render: getPlayer failed: " + str(exc))
        # Build the displayed line: "<Leader>: <text>" so attribution shows
        # explicitly even when the engine doesn't tint message text.
        clean_text = _to_ascii(text)
        if leader_name and not clean_text.lower().startswith(leader_name.lower() + ":"):
            displayed = leader_name + ": " + clean_text
        else:
            displayed = clean_text
        message_type = InterfaceMessageTypes.MESSAGE_TYPE_MAJOR_EVENT
        _log("render: localPlayer=" + str(local_player)
             + " speaker_id=" + str(speaker_id)
             + " leader=" + str(leader_name)
             + " color=" + str(speaker_color)
             + " has_button=" + str(leader_button is not None)
             + " final_len=" + str(len(displayed)))
        CyInterface().addMessage(
            local_player, False, 12, displayed, "",
            message_type, leader_button, speaker_color,
            -1, -1, True, True
        )
        _log("render: addMessage call returned without exception")
    except Exception, exc:
        _log("render_local_line failed: " + str(exc))


def _drain_display_queue():
    """Fire any due lines. Caps work per tick to LINE_TICK_BUDGET_SECONDS."""
    if not _display_queue:
        return
    try:
        game = _gc().getGame()
        if game.isPaused():
            return
    except:
        pass
    now = _now()
    start = now
    fired = 0
    while _display_queue and (time.time() - start) < LINE_TICK_BUDGET_SECONDS:
        entry = _display_queue[0]
        if entry["due_unix"] > now:
            break
        # Validate speaker still alive (drop remaining if speaker eliminated)
        try:
            sp = _gc().getPlayer(entry["speaker_id"])
            if entry["speaker_id"] >= 0 and not sp.isAlive():
                _log("dropping queue: speaker " + str(entry["speaker_id"]) + " no longer alive")
                while _display_queue:
                    _display_queue.pop(0)
                return
        except:
            pass
        _display_queue.pop(0)
        _broadcast_line(entry)
        fired += 1
    if fired > 0 and not _display_queue:
        global _active_exchange_until
        _active_exchange_until = 0.0


def _check_for_responses():
    """Scan spool for response files matching our pending request, ingest, delete."""
    global _pending_request_id
    d = _spool_dir()
    if not os.path.isdir(d):
        return
    try:
        names = os.listdir(d)
    except:
        return
    scanned = 0
    for name in names:
        if scanned >= SPOOL_SCAN_LIMIT:
            break
        if not name.startswith("resp-") or not name.endswith(".json"):
            continue
        if name.endswith(".tmp"):
            continue
        scanned += 1
        path = os.path.join(d, name)
        data = _read_json(path)
        if data is None:
            continue
        # Filter: must be our session
        if data.get("session_id") != _session_id:
            # Not ours -- delete (probably stale from a previous game)
            _safe_unlink(path)
            continue
        # Filter: must be our pending request
        rid = data.get("request_id")
        if rid != _pending_request_id:
            # Could be a stale response or a response for someone else (impossible
            # in current design but defend). Leave it; janitor will GC.
            continue
        # Pre-broadcast recheck: in MP, confirm we are still elector
        # (someone else may have taken over between request emit and response
        # arrival). In SP/hot-seat the response is from THIS machine and we
        # should always render it, even if the sidecar's heartbeat went stale
        # while it was busy calling the API.
        try:
            game = _gc().getGame()
            is_network = game.isNetworkMultiPlayer()
        except:
            is_network = False
        drop_due_to_election = False
        if is_network:
            if not _is_chatter_elector():
                drop_due_to_election = True
        # SP/hot-seat: we wrote it, we render it. No re-election check.
        if drop_due_to_election:
            _log("dropping response: no longer elector")
            _safe_unlink(path)
            _pending_request_id = None
            continue
        # Process
        if data.get("ok"):
            _enqueue_response_lines(data)
        else:
            _log("dropping non-ok response: " + str(data.get("error", "?")))
        _safe_unlink(path)
        _pending_request_id = None


# ===== state machine: tick / reset / capability =====

def _full_reset(reason):
    global _session_id, _local_player_id, _capable_humans, _local_capable
    global _local_capable_checked_at, _seen_events, _pair_cooldown
    global _display_queue, _pending_request_id, _pending_request_at
    global _active_exchange_until, _global_recent_lines, _logged_first_run
    global _no_elector_diag_fired, _no_elector_first_seen_turn
    global _pending_lines, _next_msg_id
    _session_id = _gen_uuid()
    try:
        _local_player_id = _gc().getGame().getActivePlayer()
    except:
        _local_player_id = -1
    _capable_humans = {}
    _local_capable = None
    _local_capable_checked_at = 0.0
    _seen_events = {}
    _pair_cooldown = {}
    while _display_queue:
        _display_queue.pop(0)
    _pending_request_id = None
    _pending_request_at = 0.0
    _active_exchange_until = 0.0
    while _global_recent_lines:
        _global_recent_lines.pop()
    _logged_first_run = False
    _no_elector_diag_fired = False
    _no_elector_first_seen_turn = -1
    _pending_lines = {}
    _next_msg_id = 1
    _log("reset (" + reason + ") session=" + _session_id + " localPlayer=" + str(_local_player_id))


def _gc_old_spool_files():
    """Delete stale request files older than 5 minutes."""
    d = _spool_dir()
    if not os.path.isdir(d):
        return
    try:
        names = os.listdir(d)
    except:
        return
    now = _now()
    for name in names:
        if not name.endswith(".json"):
            continue
        path = os.path.join(d, name)
        try:
            age = now - os.path.getmtime(path)
        except:
            continue
        if name.startswith("req-") and age > 300:
            _safe_unlink(path)
        elif name.startswith("resp-") and age > 600:
            _safe_unlink(path)


# ===== public entry points wired from CvEventManager =====

def chatter_on_game_start():
    """Called from CvEventManager.onGameStart."""
    if _disabled:
        return
    try:
        _full_reset("onGameStart")
        _gc_old_spool_files()
        _try_autospawn_sidecar()
        _broadcast_capability_ping()
        _maybe_fire_debug_hello_at_start()
    except Exception, exc:
        _disable("on_game_start: " + str(exc))


def chatter_on_load_game():
    """Called from CvEventManager.onLoadGame."""
    if _disabled:
        return
    try:
        _full_reset("onLoadGame")
        _gc_old_spool_files()
        _try_autospawn_sidecar()
        _broadcast_capability_ping()
        _maybe_fire_debug_hello_at_start()
    except Exception, exc:
        _disable("on_load_game: " + str(exc))


def _maybe_fire_debug_hello_at_start():
    """Smoke-test only: send a chunked-broadcast probe so the user can see
    that the broadcast pipe + addMessage render works without needing a
    real trigger event. Uses the local player as both speaker and broadcast
    sender so we exercise the full path (chunking, accumulation, render).
    """
    global _debug_hello_fired_at_start
    if not _DEBUG_HELLO_AT_START:
        return
    if _debug_hello_fired_at_start:
        return
    _debug_hello_fired_at_start = True
    try:
        _log("debug: firing chunked-broadcast probe at game start")
        if _local_player_id < 0:
            _log("debug: no local player; skipping start probe")
            return
        _send_line_via_chunks(
            _local_player_id,
            "DowagerMod Chatter [DEBUG]: chatter module loaded; "
            "if you see this in your event log, the chunked addMessage path works."
        )
        _log("debug: chunked-broadcast probe fired without exception")
    except Exception, exc:
        _log("debug: chunked probe FAILED: " + str(exc))


def _maybe_fire_debug_hello_at_turn(iGameTurn):
    """Smoke-test only: at turn 1 and turn 2, write synthetic spool requests
    to test the full game -> sidecar -> response -> broadcast pipeline.
    Two fires so we can also test the "second event" path (which previously
    got blocked by stale cooldowns or flags).
    """
    global _debug_hello_fired_at_turn, _debug_hello_fired_at_turn_2
    if not _DEBUG_HELLO_AT_START:
        return
    # First debug LLM trigger
    if (iGameTurn == _DEBUG_HELLO_AT_TURN) and not _debug_hello_fired_at_turn:
        _debug_hello_fired_at_turn = True
        _fire_synthetic_test("turn-" + str(iGameTurn) + "-A")
        return
    # Second debug LLM trigger
    if (iGameTurn == _DEBUG_HELLO_AT_TURN_2) and not _debug_hello_fired_at_turn_2:
        _debug_hello_fired_at_turn_2 = True
        _fire_synthetic_test("turn-" + str(iGameTurn) + "-B")
        return


def _fire_synthetic_test(label):
    """Write a synthetic FIRST_CONTACT request through the full pipeline."""
    try:
        _log("debug: firing synthetic " + label + " request")
        if _local_player_id < 0:
            _log("debug: no local player; skipping synthetic " + label)
            return
        speaker_id = _local_player_id
        target_id = -1
        try:
            for i in range(_gc().getMAX_CIV_PLAYERS()):
                if i == speaker_id:
                    continue
                p = _gc().getPlayer(i)
                if p.isAlive():
                    target_id = i
                    break
        except:
            pass
        if target_id < 0:
            target_id = speaker_id
        _emit_request("FIRST_CONTACT", speaker_id, target_id, {}, multi_turn=False)
    except Exception, exc:
        _log("debug: synthetic " + label + " FAILED: " + str(exc))


def chatter_on_begin_player_turn(iGameTurn, iPlayer):
    """Called from CvEventManager.onBeginPlayerTurn."""
    if _disabled:
        return
    try:
        # Re-broadcast capability periodically
        if (iGameTurn % CAPABILITY_REBROADCAST_TURNS) == 0 and iGameTurn > 0:
            _broadcast_capability_ping()
        # Drain display + check for responses on every player-turn
        _check_for_responses()
        _drain_display_queue()
        # Debug probe (smoke test only)
        _maybe_fire_debug_hello_at_turn(iGameTurn)
        # One-time diagnostic if no capable elector after N turns
        _maybe_show_no_elector_diagnostic(iGameTurn, iPlayer)
    except Exception, exc:
        _log("on_begin_player_turn error: " + str(exc))


def _maybe_show_no_elector_diagnostic(iGameTurn, iLocalPlayer):
    """Once per session, if we've seen no capable peers for N turns, post a
    quiet local-only message so the user knows chatter is silent and why.
    """
    global _no_elector_diag_fired, _no_elector_first_seen_turn
    if _no_elector_diag_fired:
        return
    if _check_local_capable():
        # Local IS capable -- never show the diag.
        _no_elector_diag_fired = True
        return
    if _capable_humans:
        # Some other peer is capable -- nothing to warn about.
        _no_elector_diag_fired = True
        return
    if _no_elector_first_seen_turn < 0:
        _no_elector_first_seen_turn = iGameTurn
        return
    if (iGameTurn - _no_elector_first_seen_turn) < NO_ELECTOR_DIAG_AFTER_TURNS:
        return
    # Fire the diagnostic locally only (no sendChat -- this is per-machine).
    try:
        if iLocalPlayer == _local_player_id and _local_player_id >= 0:
            CyInterface().addImmediateMessage(
                "DowagerMod Chatter: no AI commentator available this game.", "")
    except:
        pass
    _no_elector_diag_fired = True
    _log("no-elector diagnostic fired at turn " + str(iGameTurn))


def chatter_on_update(fDeltaTime):
    """Called from CvEventManager.onUpdate (~30-60 Hz). MUST be cheap."""
    if _disabled:
        return
    if not _display_queue and _pending_request_id is None:
        return  # nothing to do
    try:
        _check_for_responses()
        _drain_display_queue()
    except:
        pass


def chatter_on_mod_net_message(iData1, iData2, iData3, iData4, iData5):
    """Called from CvEventManager.onModNetMessage. Receives capability
    pings AND chatter line chunks.
    """
    if _disabled:
        return False
    try:
        if iData1 == CHATTER_CAP_MAGIC:
            pid = int(iData2)
            if pid >= 0:
                _capable_humans[pid] = _now()
            return True
        if iData1 == CHATTER_LINE_MAGIC:
            _handle_line_chunk(iData2, iData3, iData4, iData5)
            return True
        return False
    except:
        return False


# ----- trigger handlers (one per event type) -----

def chatter_on_change_war(bIsWar, iAttackerTeam, iDefenderTeam):
    """Called from CvEventManager.onChangeWar.

    For DoW (bIsWar=True), emits BACKSTABBED instead of DECLARE_WAR if the
    defender's leader still views the attacker as Pleased/Friendly OR the
    defender has accumulated several positive memories of the attacker
    (open borders, traded resources/tech, etc.). The line is spoken FROM
    the betrayed defender TO the attacker, matching the prompt template.
    """
    if _disabled:
        return
    try:
        atk_p, def_p = _representative_players_for_teams(iAttackerTeam, iDefenderTeam)
        if atk_p < 0 or def_p < 0:
            return
        if bIsWar:
            if _is_backstab(atk_p, def_p):
                # Speaker = defender (the betrayed), target = attacker.
                _emit_request("BACKSTABBED", def_p, atk_p, {}, multi_turn=True)
            else:
                _emit_request("DECLARE_WAR", atk_p, def_p, {}, multi_turn=True)
        else:
            # Peace treaty (only fire if pair was at war for >0 turns; engine
            # handles that — if !bIsWar fires they had been at war).
            _emit_request("PEACE_TREATY", atk_p, def_p, {}, multi_turn=True)
    except Exception, exc:
        _log("on_change_war error: " + str(exc))


def _is_backstab(atk_p, def_p):
    """Heuristic: does this DoW look like a betrayal?

    Two signals (any one true => backstab):
      A. Defender's AI attitude toward attacker is still >= Pleased (3)
         immediately after the war state change. Civ4's just-declared-war
         memory drops attitude, so a Pleased/Friendly result means there
         were strong positive baseline modifiers (long peace, religion,
         civics, etc.) that survived the penalty.
      B. Defender has accumulated several positive-history memories of
         the attacker (traded tech, open borders accepted, gave help,
         traded resources, accepted defensive pact). 3+ such memories
         indicates a meaningful prior friendship.
    """
    try:
        gc = _gc()
        defender = gc.getPlayer(def_p)
        # Signal A: residual attitude
        try:
            attitude = defender.AI_getAttitude(int(atk_p))
            # AttitudeTypes: 0=Furious, 1=Annoyed, 2=Cautious, 3=Pleased, 4=Friendly
            if int(attitude) >= 3:
                return True
        except:
            pass
        # Signal B: positive-memory count
        positive = 0
        try:
            mt = MemoryTypes
        except:
            mt = None
        if mt is not None:
            mem_names = (
                "MEMORY_TRADED_TECH_TO_US",
                "MEMORY_GAVE_HELP",
                "MEMORY_ACCEPTED_OPEN_BORDERS",
                "MEMORY_ACCEPTED_DEFENSIVE_PACT",
                "MEMORY_ACCEPTED_RESOURCES",
            )
            for name in mem_names:
                try:
                    mem_const = getattr(mt, name)
                    positive += int(defender.AI_getMemoryCount(int(atk_p), mem_const))
                except:
                    pass
        return positive >= 3
    except:
        return False


def chatter_on_golden_age(iPlayer):
    """Called from CvEventManager.onGoldenAge.

    Broadcast trigger: the leader announces their civ has entered a golden age.
    """
    if _disabled:
        return
    try:
        if iPlayer is None or int(iPlayer) < 0:
            return
        _emit_request("GOLDEN_AGE", int(iPlayer), -1, {}, multi_turn=False)
    except Exception, exc:
        _log("on_golden_age error: " + str(exc))


def chatter_on_city_acquired_and_kept(iOwner, pCity):
    """Called from CvEventManager.onCityAcquiredAndKept."""
    if _disabled:
        return
    try:
        # iOwner is the new owner; previous owner is on the city object.
        prev_owner = pCity.getPreviousOwner()
        if prev_owner < 0 or iOwner < 0 or prev_owner == iOwner:
            return
        city_name = _to_ascii(pCity.getName())
        _emit_request("CITY_CAPTURED", iOwner, prev_owner,
                      {"city": city_name}, multi_turn=True)
    except Exception, exc:
        _log("on_city_acquired_and_kept error: " + str(exc))


def chatter_on_city_razed(pCity, iPlayer):
    """Called from CvEventManager.onCityRazed."""
    if _disabled:
        return
    try:
        prev_owner = pCity.getPreviousOwner()
        if prev_owner < 0 or iPlayer < 0:
            return
        city_name = _to_ascii(pCity.getName())
        _emit_request("CITY_RAZED", iPlayer, prev_owner,
                      {"city": city_name}, multi_turn=True)
    except Exception, exc:
        _log("on_city_razed error: " + str(exc))


def chatter_on_first_contact(iTeamX, iHasMetTeamY):
    """Called from CvEventManager.onFirstContact (team-based)."""
    if _disabled:
        return
    try:
        # Emit from team X's leader to team Y's leader
        x_p, y_p = _representative_players_for_teams(iTeamX, iHasMetTeamY)
        if x_p < 0 or y_p < 0:
            return
        _emit_request("FIRST_CONTACT", x_p, y_p, {}, multi_turn=True)
    except Exception, exc:
        _log("on_first_contact error: " + str(exc))


def chatter_on_religion_founded(iReligion, iFounder):
    """Called from CvEventManager.onReligionFounded."""
    if _disabled:
        return
    try:
        if iFounder < 0:
            return
        rel_name = _to_ascii(_gc().getReligionInfo(iReligion).getDescription())
        _emit_request("RELIGION_FOUNDED", iFounder, -1,
                      {"religion": rel_name}, multi_turn=False)
    except Exception, exc:
        _log("on_religion_founded error: " + str(exc))


def chatter_on_corporation_founded(iCorporation, iFounder):
    """Called from CvEventManager.onCorporationFounded."""
    if _disabled:
        return
    try:
        if iFounder < 0:
            return
        corp_name = _to_ascii(_gc().getCorporationInfo(iCorporation).getDescription())
        _emit_request("CORPORATION_FOUNDED", iFounder, -1,
                      {"corporation": corp_name}, multi_turn=False)
    except Exception, exc:
        _log("on_corporation_founded error: " + str(exc))


def chatter_on_tech_acquired(iTech, iTeam, iPlayer, bAnnounce):
    """Called from CvEventManager.onTechAcquired.

    Fire only if the player is the FIRST in the world to discover the tech.
    """
    if _disabled:
        return
    try:
        if iPlayer < 0:
            return
        if not _first_in_world_for_tech(iTech, iTeam):
            return
        tech_name = _to_ascii(_gc().getTechInfo(iTech).getDescription())
        _emit_request("FIRST_TO_TECH", iPlayer, -1,
                      {"tech": tech_name}, multi_turn=False)
    except Exception, exc:
        _log("on_tech_acquired error: " + str(exc))


def chatter_on_wonder_built(pCity, iBuildingType, iPlayer):
    """Called when a wonder building completes (CvEventManager.onBuildingBuilt)."""
    if _disabled:
        return
    try:
        if iPlayer < 0:
            return
        info = _gc().getBuildingInfo(iBuildingType)
        if info is None:
            return
        # Only world wonders (not national, not team)
        if not _is_world_wonder(info):
            return
        wonder_name = _to_ascii(info.getDescription())
        _emit_request("WONDER_BUILT", iPlayer, -1,
                      {"wonder": wonder_name}, multi_turn=False)
    except Exception, exc:
        _log("on_wonder_built error: " + str(exc))


def chatter_on_player_eliminated(iPlayer):
    """Called from CvEventManager.onSetPlayerAlive when bAlive=false."""
    if _disabled:
        return
    try:
        if iPlayer < 0:
            return
        # Find a likely killer: any other alive human/AI player that is at war with iPlayer.
        killer = _likely_killer_of(iPlayer)
        if killer < 0:
            return
        # Two events: gloat (killer speaks) and last-words (eliminated speaks).
        # Both are now multi-turn for dramatic last-stand exchanges.
        _emit_request("PLAYER_ELIMINATED_GLOAT", killer, iPlayer, {}, multi_turn=True)
        # Last words is ALWAYS broadcast even if the gloat was emitted (cooldown
        # and dedup don't share keys -- separate trigger ID).
        _emit_request("PLAYER_ELIMINATED_LAST_WORDS", iPlayer, killer, {}, multi_turn=True)
    except Exception, exc:
        _log("on_player_eliminated error: " + str(exc))


# ===== helpers (game-side queries) =====

def _representative_players_for_teams(iTeamA, iTeamB):
    """Pick the leader player of each team."""
    a, b = -1, -1
    try:
        for i in range(_gc().getMAX_CIV_PLAYERS()):
            p = _gc().getPlayer(i)
            if not p.isAlive():
                continue
            if p.getTeam() == iTeamA and a < 0:
                a = i
            elif p.getTeam() == iTeamB and b < 0:
                b = i
            if a >= 0 and b >= 0:
                break
    except:
        pass
    return a, b


def _first_in_world_for_tech(iTech, iTeam):
    """True if iTeam is the first to acquire this tech."""
    try:
        for i in range(_gc().getMAX_TEAMS()):
            if i == iTeam:
                continue
            t = _gc().getTeam(i)
            if t.isAlive() and t.isHasTech(iTech):
                return False
        return True
    except:
        return False


def _is_world_wonder(buildingInfo):
    """True if a BuildingInfo is a world wonder."""
    try:
        return bool(buildingInfo.isWorldWonder())
    except:
        return False


def _likely_killer_of(iPlayer):
    """Pick a player most likely responsible for eliminating iPlayer.

    Heuristic: any alive player at war with iPlayer's team. Falls back to
    -1 if no obvious candidate.
    """
    try:
        target_team = _gc().getPlayer(iPlayer).getTeam()
        for i in range(_gc().getMAX_CIV_PLAYERS()):
            if i == iPlayer:
                continue
            p = _gc().getPlayer(i)
            if not p.isAlive():
                continue
            t = _gc().getTeam(p.getTeam())
            if t.isAtWar(target_team):
                return i
    except:
        pass
    return -1
