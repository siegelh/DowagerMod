"""Tiny .env file loader for DowagerMod Chatter.

No external dependency on python-dotenv; we only need the basics:
KEY=VALUE per line, # for comments, "" / '' quote stripping.

Search order (first hit wins):
  1. ./.env (current working directory)
  2. <repo_root>/.env (parent of tools/)
  3. tools/chatter/.env

Existing os.environ values are NEVER overwritten; real env wins. This
matches the convention of python-dotenv with override=False.

Used by:
  - tools/chatter/config.py (sidecar daemon config loader)
  - tools/chatter/test_credentials.py (credential smoke test)
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional


def find_dotenv() -> Optional[Path]:
    """Return the first .env file found, or None."""
    here = Path(__file__).resolve()
    candidates = [
        Path.cwd() / ".env",
        here.parent.parent.parent / ".env",  # repo root
        here.parent / ".env",                # tools/chatter/.env
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def load_dotenv(*, verbose: bool = False) -> Optional[Path]:
    """Load .env into os.environ. Returns the path loaded, or None."""
    path = find_dotenv()
    if path is None:
        return None
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
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
            if k and k not in os.environ:
                os.environ[k] = v
        if verbose:
            print(f"[dotenv] loaded {path}")
        return path
    except Exception as exc:  # noqa: BLE001
        if verbose:
            print(f"[dotenv] failed to read {path}: {exc}")
        return None
