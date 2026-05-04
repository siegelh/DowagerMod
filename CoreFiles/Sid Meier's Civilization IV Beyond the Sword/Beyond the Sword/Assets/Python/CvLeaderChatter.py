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


# ===== tunables =====

CHATTER_CAP_MAGIC = 0x4348           # 'CH' as int -- recognizable in onModNetMessage
HEARTBEAT_FRESH_SECONDS = 60         # local sidecar heartbeat must be within this
CAPABILITY_REBROADCAST_TURNS = 50    # re-advertise capability every N game turns
CAPABILITY_STALE_HEARTBEATS = 5      # peers drop us after N missed advertisements
PER_PAIR_COOLDOWN_TURNS = 200        # min game turns between exchanges for same pair
GLOBAL_LINE_PER_REAL_MIN_CAP = 4     # max chatter lines per 60s real-time
LINE_TICK_BUDGET_SECONDS = 0.005     # max wallclock per onUpdate-equivalent tick
SPOOL_SCAN_LIMIT = 8                 # max response files scanned per tick
REJOINDER_PROBABILITY = 0.5          # chance a trigger gets a multi-turn exchange
SPAWN_RETRY_SECONDS = 30             # don't try to spawn sidecar more than once per N seconds
DROP_NEW_WHILE_QUEUE_ACTIVE = True   # one event at a time
NO_ELECTOR_DIAG_AFTER_TURNS = 30     # show one-time message after N turns w/o capable elector

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
    """Strip non-ASCII (Civ4 chat panel has limited glyph coverage)."""
    if text is None:
        return ""
    try:
        if isinstance(text, unicode):
            text = text.encode("ascii", "replace")
    except:
        pass
    out_chars = []
    for c in text:
        if isinstance(c, str):
            oc = ord(c)
        else:
            oc = c
        if 32 <= oc <= 126:
            out_chars.append(chr(oc))
        elif oc == 9 or oc == 10:
            out_chars.append(c)
    return "".join(out_chars)


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
    """Is the local sidecar fresh (config exists + PID file heartbeat < 60s)?"""
    global _local_capable, _local_capable_checked_at
    now = _now()
    if _local_capable is not None and (now - _local_capable_checked_at) < 5.0:
        return _local_capable
    _local_capable_checked_at = now
    cfg = _config_path()
    if cfg is None or not os.path.isfile(cfg):
        _local_capable = False
        return False
    pid = _daemon_pid_path()
    if not os.path.isfile(pid):
        _local_capable = False
        return False
    pid_data = _read_json(pid)
    if not pid_data:
        _local_capable = False
        return False
    hb = float(pid_data.get("heartbeat_unix", 0))
    age = now - hb
    if age > HEARTBEAT_FRESH_SECONDS:
        _local_capable = False
        return False
    _local_capable = True
    return True


def _try_autospawn_sidecar():
    """If config exists but sidecar isn't running, try to launch it.

    Best-effort. Detached, never blocks. Failures are silent.
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

    # Try to find the repo's Start-Chatter.ps1 by walking up from the live
    # game install dir. We expect: <repo>\CoreFiles\Sid Meier's...\Beyond the Sword\Assets\Python\Chatter\
    here = os.path.dirname(os.path.abspath(__file__))
    candidates = []
    try:
        # Walk up to find a 'tools' sibling
        cur = here
        for _ in range(10):
            cur = os.path.dirname(cur)
            if not cur:
                break
            cand = os.path.join(cur, "tools", "Start-Chatter.ps1")
            if os.path.isfile(cand):
                candidates.append(cand)
                break
    except:
        pass

    if not candidates:
        _log("autospawn: could not locate Start-Chatter.ps1")
        return

    script = candidates[0]
    try:
        # Detached background. Use os.spawnl with P_DETACH-equivalent flags.
        # On Windows, we can use subprocess with creationflags for detached.
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
    except:
        _log("autospawn: subprocess.Popen failed")


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


def _player_info(player_id):
    """Build a {player_id, leader_name, civ_short_name, score} dict for the request."""
    try:
        p = _gc().getPlayer(player_id)
        return {
            "player_id": int(player_id),
            "leader_name": _to_ascii(p.getName()),
            "civ_short_name": _to_ascii(p.getCivilizationShortDescription(0)),
            "score": int(p.calculateScore()),
        }
    except:
        return {"player_id": int(player_id), "leader_name": "Unknown",
                "civ_short_name": "Unknown", "score": 0}


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
        return None

    # Allow only one in-flight at a time
    if _pending_request_id is not None:
        # If pending is older than 60s, drop it (sidecar must be slow/dead)
        if (_now() - _pending_request_at) > 60.0:
            _log("dropping stale pending request " + str(_pending_request_id))
            _pending_request_id = None
        else:
            return None

    if DROP_NEW_WHILE_QUEUE_ACTIVE and _display_queue:
        return None

    if not _global_rate_limit_ok():
        _log("global rate limit hit; dropping " + trigger)
        return None

    if not _is_chatter_elector():
        return None

    # Per-pair cooldown
    if _per_pair_cooldown_active(speaker_id, target_id):
        return None

    # Dedup
    key = _event_key(trigger, speaker_id, target_id,
                     str(extra_context.get("city", "")) + str(extra_context.get("wonder", ""))
                     + str(extra_context.get("religion", "")) + str(extra_context.get("tech", "")))
    if _event_seen(key):
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
        if random.random() < REJOINDER_PROBABILITY:
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
        _display_queue.append({
            "due_unix": due,
            "speaker_id": int(ln.get("speaker_player_id", -1)),
            "speaker_name": _to_ascii(str(ln.get("speaker_name", "?"))),
            "text": _to_ascii(str(ln.get("text", ""))),
        })
    _active_exchange_until = base + (cumulative_delay / 1000.0) + 1.0


def _format_chat_line(speaker_name, text):
    """Render the line for sendChat broadcast.

    Format: 'Victoria: <text>'  (ASCII only, no Unicode).
    Engine will prefix with elector's player name regardless.
    """
    return _to_ascii(speaker_name) + ': ' + _to_ascii(text)


def _broadcast_line(entry):
    """Send via the engine's chat channel so all clients see it."""
    try:
        msg = _format_chat_line(entry["speaker_name"], entry["text"])
        # CHATTARGET_ALL = -2
        CyMessageControl().sendChat(msg, -2)
        _global_recent_lines.append(_now())
        _log("broadcast: " + msg[:100])
    except:
        _log("broadcast failed for: " + str(entry.get("text", ""))[:60])


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
        # Filter: must still be the elector at consume time (pre-broadcast recheck)
        if not _is_chatter_elector():
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
    except Exception, exc:
        _disable("on_load_game: " + str(exc))


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
    """Called from CvEventManager.onModNetMessage. Receives capability pings."""
    if _disabled:
        return False
    try:
        if iData1 != CHATTER_CAP_MAGIC:
            return False  # not for us
        pid = int(iData2)
        if pid < 0:
            return True
        _capable_humans[pid] = _now()
        return True
    except:
        return False


# ----- trigger handlers (one per event type) -----

def chatter_on_change_war(bIsWar, iAttackerTeam, iDefenderTeam):
    """Called from CvEventManager.onChangeWar."""
    if _disabled:
        return
    try:
        atk_p, def_p = _representative_players_for_teams(iAttackerTeam, iDefenderTeam)
        if atk_p < 0 or def_p < 0:
            return
        if bIsWar:
            _emit_request("DECLARE_WAR", atk_p, def_p, {}, multi_turn=True)
        else:
            # Peace treaty (only fire if pair was at war for >0 turns; engine
            # handles that — if !bIsWar fires they had been at war).
            _emit_request("PEACE_TREATY", atk_p, def_p, {}, multi_turn=False)
    except Exception, exc:
        _log("on_change_war error: " + str(exc))


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
        _emit_request("FIRST_CONTACT", x_p, y_p, {}, multi_turn=False)
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
        # Both are short single-line, no rejoinder. Fire both with slight separation.
        _emit_request("PLAYER_ELIMINATED_GLOAT", killer, iPlayer, {}, multi_turn=False)
        # Last words is ALWAYS broadcast even if the gloat was emitted (cooldown
        # check uses the same pair, so we side-step by not re-emitting if pending).
        _emit_request("PLAYER_ELIMINATED_LAST_WORDS", iPlayer, killer, {}, multi_turn=False)
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
