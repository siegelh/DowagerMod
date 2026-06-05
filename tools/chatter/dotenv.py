"""Tiny .env file loader for DowagerMod Chatter.

No external dependency on python-dotenv; we only need the basics:
KEY=VALUE per line, # for comments, "" / '' quote stripping.

Two API styles:

* ``parse_dotenv_file(path)`` -- pure parser, returns a dict. Does NOT
  touch ``os.environ``. This is what the daemon config loader uses so
  that a periodic reload would never accumulate env-var pollution and so
  the "real env vs .env" merge can be reasoned about explicitly.

* ``load_dotenv(...)`` -- back-compat helper that mutates ``os.environ``.
  Still used by ``tools/chatter/test_credentials.py`` and other one-shot
  CLIs that want ``os.environ.get(...)`` to "just work" after loading.

Discovery search order (first existing file wins) -- shared by both APIs:
  1. ``$DOWAGER_CHATTER_ENV_PATH`` (explicit override; tests + custom layouts)
  2. ``<repo_root>/.env`` (canonical dev location -- gitignored)
  3. ``tools/chatter/.env`` (legacy fallback)

``Path.cwd() / ".env"`` is intentionally NOT searched anymore: it caused
silent surprises when the daemon was launched from a subdirectory or
when a tester happened to have an unrelated ``.env`` in their shell's
cwd. Use ``DOWAGER_CHATTER_ENV_PATH`` for explicit override.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Optional

ENV_PATH_OVERRIDE = "DOWAGER_CHATTER_ENV_PATH"


def _candidate_paths() -> list:
    """Return the ordered list of .env paths to probe.

    If the ``DOWAGER_CHATTER_ENV_PATH`` override is set, that path is the
    ONLY candidate -- no fallback to the default locations. Explicit
    beats implicit; it also lets tests deterministically simulate "no
    .env" by pointing the override at a nonexistent path.

    With no override, the search order is:
      1. ``<repo_root>/.env`` (canonical dev location -- gitignored)
      2. ``tools/chatter/.env`` (legacy fallback)
    """
    override = os.environ.get(ENV_PATH_OVERRIDE)
    if override:
        return [Path(override)]
    here = Path(__file__).resolve()
    return [
        here.parent.parent.parent / ".env",  # repo root
        here.parent / ".env",                # tools/chatter/.env
    ]


def find_dotenv() -> Optional[Path]:
    """Return the first existing .env file from the search list, or None."""
    for candidate in _candidate_paths():
        try:
            if candidate.is_file():
                return candidate
        except OSError:
            continue
    return None


class EnvFileMissingError(RuntimeError):
    """Raised when the chatter sidecar cannot locate a .env file.

    The chatter daemon refuses to start without a .env because that file
    is the *only* source of truth for credentials and tunables. If we
    silently fell back to DEFAULTS the daemon would come up unauthenticated
    and spend its life logging 401s; far better to fail loudly at boot
    with a message that tells the operator exactly what to do.
    """


def _candidate_paths_message() -> str:
    return "\n".join("  - " + str(p) for p in _candidate_paths())


def ensure_dotenv_file() -> Path:
    """Return the .env path, or raise ``EnvFileMissingError`` with guidance.

    Used by the daemon, ``Start-Chatter.ps1``, and ``Setup-Chatter.ps1``
    so all three surfaces fail the same way with the same message.
    """
    path = find_dotenv()
    if path is not None:
        return path
    raise EnvFileMissingError(
        "DowagerMod chatter could not find a .env file.\n"
        "\n"
        ".env is the single source of truth for chatter credentials\n"
        "(Azure Foundry, Azure Speech, Discord bot) and tunables. The\n"
        "daemon refuses to start without one so you don't end up running\n"
        "with stale or default values.\n"
        "\n"
        "Searched (in order):\n"
        + _candidate_paths_message() + "\n"
        "\n"
        "Fix: from the repo root run\n"
        "    Copy-Item .env.example .env\n"
        "    notepad .env\n"
        "then re-run Setup-Chatter.ps1 (or just start the daemon)."
    )


def _parse_lines(text: str) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        k, _, v = line.partition("=")
        k = k.strip()
        v = v.strip()
        # Strip matching surrounding quotes
        if len(v) >= 2 and v[0] == v[-1] and v[0] in ('"', "'"):
            v = v[1:-1]
        if k:
            out[k] = v
    return out


def parse_dotenv_file(path: Path) -> Dict[str, str]:
    """Read and parse a .env file. Pure: never touches ``os.environ``.

    Returns an empty dict if the file is missing or unreadable. Never
    raises -- callers can treat "no .env" and "broken .env" the same way
    (DEFAULTS apply).
    """
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:  # noqa: BLE001
        return {}
    try:
        return _parse_lines(text)
    except Exception:  # noqa: BLE001
        return {}


def load_dotenv(*, verbose: bool = False, override: bool = False) -> Optional[Path]:
    """Load .env into ``os.environ``. Returns the path loaded, or None.

    Back-compat helper retained for CLIs/tests that rely on os.environ
    being populated (e.g. ``tools/chatter/test_credentials.py``). The
    sidecar daemon's config loader does NOT use this -- it uses the
    pure ``parse_dotenv_file`` instead so reloads stay clean.

    When ``override`` is False (the default) existing ``os.environ``
    keys win -- this matches python-dotenv's default. When True, .env
    values overwrite the process env.
    """
    path = find_dotenv()
    if path is None:
        return None
    values = parse_dotenv_file(path)
    if not values:
        if verbose:
            print(f"[dotenv] {path} parsed to no entries")
        return path
    for k, v in values.items():
        if override or k not in os.environ:
            os.environ[k] = v
    if verbose:
        print(f"[dotenv] loaded {path} ({len(values)} keys)")
    return path
