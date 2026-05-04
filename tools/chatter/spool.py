"""Atomic file I/O for the chatter spool directory."""
from __future__ import annotations

import json
import os
import time
import uuid
from pathlib import Path
from typing import Iterator, Optional


REQ_PREFIX = "req-"
RESP_PREFIX = "resp-"
TMP_SUFFIX = ".tmp"
JSON_SUFFIX = ".json"


def ensure_spool_dir(spool: Path) -> None:
    spool.mkdir(parents=True, exist_ok=True)


def gen_filename(prefix: str) -> str:
    """e.g. req-20260503T203015-3f2a91.json"""
    ts = time.strftime("%Y%m%dT%H%M%S", time.gmtime())
    rand = uuid.uuid4().hex[:6]
    return f"{prefix}{ts}-{rand}{JSON_SUFFIX}"


def atomic_write_json(path: Path, payload: dict) -> None:
    """Write JSON via tmp + rename (atomic on Windows + Unix)."""
    tmp = path.with_suffix(path.suffix + TMP_SUFFIX)
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.flush()
        try:
            os.fsync(f.fileno())
        except Exception:
            pass  # Some filesystems don't support fsync; not fatal
    os.replace(tmp, path)


def safe_read_json(path: Path) -> Optional[dict]:
    """Read + parse JSON. Returns None on any error (truncated / invalid / gone)."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def safe_unlink(path: Path) -> None:
    try:
        path.unlink()
    except Exception:
        pass


def list_requests(spool: Path) -> Iterator[Path]:
    """Yield request files in deterministic order. Skips .tmp partials."""
    if not spool.exists():
        return
    items = []
    for p in spool.iterdir():
        name = p.name
        if not name.startswith(REQ_PREFIX):
            continue
        if not name.endswith(JSON_SUFFIX):
            continue
        if name.endswith(TMP_SUFFIX):
            continue
        items.append(p)
    items.sort()
    yield from items


def list_responses(spool: Path) -> Iterator[Path]:
    if not spool.exists():
        return
    items = []
    for p in spool.iterdir():
        name = p.name
        if not name.startswith(RESP_PREFIX):
            continue
        if not name.endswith(JSON_SUFFIX):
            continue
        if name.endswith(TMP_SUFFIX):
            continue
        items.append(p)
    items.sort()
    yield from items


def gc_old_files(spool: Path, prefix: str, max_age_seconds: float, *, now: Optional[float] = None) -> int:
    """Delete files matching prefix older than max_age_seconds. Returns count."""
    if not spool.exists():
        return 0
    if now is None:
        now = time.time()
    removed = 0
    for p in spool.iterdir():
        name = p.name
        if not name.startswith(prefix) or not name.endswith(JSON_SUFFIX):
            continue
        try:
            age = now - p.stat().st_mtime
        except Exception:
            continue
        if age > max_age_seconds:
            safe_unlink(p)
            removed += 1
    return removed


def write_pid_file(spool: Path, pid: int) -> None:
    payload = {"pid": pid, "heartbeat_unix": time.time()}
    atomic_write_json(spool / "daemon.pid", payload)


def read_pid_file(spool: Path) -> Optional[dict]:
    return safe_read_json(spool / "daemon.pid")
