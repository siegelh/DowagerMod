"""Per-leader voice picker for DowagerMod Chatter voiceover.

Loads ``leader_voices.json`` (hand-curated leader -> Azure Speech voice map
with gendered fallback pools). Provides ``pick_voice(leader_name, gender_hint)``
which:
  1. Normalizes the leader name (lowercase, alphanumeric only).
  2. Looks it up in the curated map. Returns the curated voice if found.
  3. Falls back to a stable hash-based pick from the gendered pool.

If the JSON file is missing or malformed, returns the default voice on every
call (graceful degradation - voiceover still works, just not per-leader).
"""
from __future__ import annotations

import hashlib
import json
import logging
import re
from pathlib import Path
from typing import Optional

_NORMALIZE_RE = re.compile(r"[^a-z0-9]")


def normalize_name(name: str) -> str:
    return _NORMALIZE_RE.sub("", (name or "").lower())


class VoicePicker:
    def __init__(
        self,
        *,
        default_voice: str = "en-US-AriaNeural",
        json_path: Optional[Path] = None,
        logger: Optional[logging.Logger] = None,
    ):
        self.default_voice = default_voice
        self.logger = logger or logging.getLogger("dowager.chatter.voice")
        self._map: dict = {}
        self._fallback_male: list = []
        self._fallback_female: list = []
        self._loaded = False

        path = json_path or (Path(__file__).resolve().parent / "leader_voices.json")
        try:
            with path.open("r", encoding="utf-8") as fh:
                data = json.load(fh)
            self._map = {str(k).lower(): str(v) for k, v in (data.get("map") or {}).items()}
            self._fallback_male = list(data.get("_fallback_male") or [])
            self._fallback_female = list(data.get("_fallback_female") or [])
            self._loaded = True
            self.logger.info(
                "voice picker loaded: %d entries, fallback_male=%d fallback_female=%d",
                len(self._map), len(self._fallback_male), len(self._fallback_female),
            )
        except FileNotFoundError:
            self.logger.warning("voice picker: no leader_voices.json at %s; using default voice for all", path)
        except Exception as exc:  # noqa: BLE001
            self.logger.warning("voice picker: leader_voices.json malformed at %s: %s", path, exc)

    def pick_voice(self, leader_name: str, *, gender_hint: str = "") -> str:
        """Return a voice ID for the given leader. Stable: same input -> same voice."""
        if not self._loaded:
            return self.default_voice
        norm = normalize_name(leader_name)
        if norm in self._map:
            return self._map[norm]
        # Fall back to gendered pool
        pool = self._fallback_female if gender_hint.lower().startswith("f") else self._fallback_male
        if not pool:
            return self.default_voice
        # Stable hash so re-runs map the same name to the same voice
        h = int(hashlib.sha256(norm.encode("utf-8") or b"x").hexdigest(), 16)
        return pool[h % len(pool)]
