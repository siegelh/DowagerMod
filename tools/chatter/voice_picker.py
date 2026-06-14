"""Per-leader voice picker for DowagerMod Chatter voiceover.

Loads ``leader_voices.json`` (hand-curated leader -> Azure Speech voice map
with gendered fallback pools). Provides ``pick_voice(leader_name, gender_hint)``
which:
  1. Normalizes the leader name (lowercase, alphanumeric only).
  2. Looks it up in the curated map. Returns the curated voice if found.
  3. Falls back to a stable hash-based pick from the gendered pool.

Map entries can be either:
  - A bare string voice name: ``"lincoln": "en-US-BrianNeural"``
  - A spec object with prosody overrides:
        ``"lincoln": {"voice": "en-US-BrianNeural", "rate": "-10%", "pitch": "-5%"}``

If the JSON file is missing or malformed, returns the default voice on every
call (graceful degradation - voiceover still works, just not per-leader).
"""
from __future__ import annotations

import hashlib
import json
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union

_NORMALIZE_RE = re.compile(r"[^a-z0-9]")


def normalize_name(name: str) -> str:
    return _NORMALIZE_RE.sub("", (name or "").lower())


@dataclass(frozen=True)
class VoiceSpec:
    """A picked voice plus optional SSML prosody overrides and native-tongue hints.

    rate examples: "-15%" (slower), "+10%" (faster), "slow", "x-slow"
    pitch examples: "-10%" (lower), "+5%" (higher), "low", "x-low"
    Empty string means "do not emit a prosody attribute for this dimension".

    For native-tongue mode:
    - lang: human-readable language name passed to the LLM (e.g. "Russian",
      "Mongolian", "Khmer"). Empty means "use English audio for this leader
      even when native_tongue_mode is on".
    - locale: BCP-47 tag passed to the SSML xml:lang attribute when native
      audio is being spoken (e.g. "ru-RU", "mn-MN"). If empty, derived from
      the voice ID's first two segments.
    """
    voice: str
    rate: str = ""
    pitch: str = ""
    lang: str = ""
    locale: str = ""
    # voice_native: a different Azure voice ID used WHEN synthesizing the
    # native-language version of a line. Required when the English voice's
    # locale doesn't match the native language locale (e.g. Catherine uses
    # de-DE-Maja for English audio for accent flavor, but for Russian audio
    # she should use ru-RU-SvetlanaNeural since a German voice can't render
    # Cyrillic). When empty, falls back to using `voice` for native too.
    voice_native: str = ""
    # post_process: optional ffmpeg preset name (see audio_postprocess.PRESETS)
    # applied to the synthesized WAV bytes before playback. Used for per-leader
    # vocal character that SSML + Azure voice selection can't produce alone
    # (e.g. Dowager Countess "elderly_crone" preset: deep formant + quaver +
    # rasp). Empty string = no post-processing.
    post_process: str = ""
    # tts_provider: optional per-leader TTS backend override. Empty string
    # (the default for every leader) means "use Azure Speech", which is the
    # only path the daemon has historically taken. "elevenlabs" means the
    # TtsDispatcher will try ElevenLabs first and fall back to Azure on any
    # failure (auth, quota, network, timeout, 5xx, or open circuit). The
    # `voice` field above is the AZURE voice used for that fallback; the
    # ElevenLabs voice ID lives in .env as DOWAGER_CHATTER_ELEVENLABS_VOICE_ID_*
    # so different operators can use their own custom voices without editing
    # the checked-in JSON.
    tts_provider: str = ""

    def derived_locale(self) -> str:
        """Return locale or, if empty, derive it from the voice ID."""
        if self.locale:
            return self.locale
        if "-" in self.voice:
            return "-".join(self.voice.split("-")[:2])
        return "en-US"


def _parse_entry(raw: Union[str, dict, None], default_voice: str) -> Optional[VoiceSpec]:
    """Convert a JSON map entry into a VoiceSpec. Returns None for invalid entries."""
    if raw is None:
        return None
    if isinstance(raw, str):
        return VoiceSpec(voice=raw)
    if isinstance(raw, dict):
        v = str(raw.get("voice", default_voice)).strip()
        if not v:
            return None
        rate = str(raw.get("rate", "")).strip()
        pitch = str(raw.get("pitch", "")).strip()
        lang = str(raw.get("lang", "")).strip()
        locale = str(raw.get("locale", "")).strip()
        voice_native = str(raw.get("voice_native", "")).strip()
        post_process = str(raw.get("post_process", "")).strip()
        tts_provider = str(raw.get("tts_provider", "")).strip().lower()
        return VoiceSpec(voice=v, rate=rate, pitch=pitch, lang=lang, locale=locale, voice_native=voice_native, post_process=post_process, tts_provider=tts_provider)
    return None


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
            raw_bytes = path.read_bytes()
            sha256 = hashlib.sha256(raw_bytes).hexdigest()[:16]
            data = json.loads(raw_bytes.decode("utf-8"))
            # Map entries may be strings or {voice, rate, pitch} dicts.
            self._map = {str(k).lower(): v for k, v in (data.get("map") or {}).items()}
            self._fallback_male = list(data.get("_fallback_male") or [])
            self._fallback_female = list(data.get("_fallback_female") or [])
            self._loaded = True
            self.logger.info(
                "voice picker loaded: %d entries, fallback_male=%d fallback_female=%d "
                "path=%s sha256=%s size=%dB",
                len(self._map), len(self._fallback_male), len(self._fallback_female),
                path, sha256, len(raw_bytes),
            )
        except FileNotFoundError:
            self.logger.warning("voice picker: no leader_voices.json at %s; using default voice for all", path)
        except Exception as exc:  # noqa: BLE001
            self.logger.warning("voice picker: leader_voices.json malformed at %s: %s", path, exc)

    def pick_spec(self, leader_name: str, *, gender_hint: str = "") -> VoiceSpec:
        """Return a VoiceSpec for the given leader. Stable: same input -> same spec."""
        if not self._loaded:
            return VoiceSpec(voice=self.default_voice)
        norm = normalize_name(leader_name)
        if norm in self._map:
            spec = _parse_entry(self._map[norm], self.default_voice)
            if spec is not None:
                return spec
        # Fall back to gendered pool
        pool = self._fallback_female if gender_hint.lower().startswith("f") else self._fallback_male
        if not pool:
            return VoiceSpec(voice=self.default_voice)
        # Stable hash so re-runs map the same name to the same voice
        h = int(hashlib.sha256(norm.encode("utf-8") or b"x").hexdigest(), 16)
        return VoiceSpec(voice=pool[h % len(pool)])

    def pick_voice(self, leader_name: str, *, gender_hint: str = "") -> str:
        """Backwards-compat: return just the voice name (no prosody)."""
        return self.pick_spec(leader_name, gender_hint=gender_hint).voice

    def pick_random_spec(self, *, rng=None) -> VoiceSpec:
        """Pick a uniformly random VoiceSpec from the loaded leader map.

        Falls back to the default voice if the map is empty or unloaded.
        Pass ``rng`` (a ``random.Random`` instance) for deterministic tests;
        otherwise the module-level ``random`` is used.
        """
        import random as _random
        r = rng or _random
        if not self._loaded or not self._map:
            return VoiceSpec(voice=self.default_voice)
        keys = list(self._map.keys())
        for _ in range(5):
            k = r.choice(keys)
            spec = _parse_entry(self._map[k], self.default_voice)
            if spec is not None:
                return spec
        return VoiceSpec(voice=self.default_voice)

    def random_leader_name(self, *, rng=None) -> str:
        """Pick a random leader (normalized) name from the loaded map."""
        import random as _random
        r = rng or _random
        if not self._loaded or not self._map:
            return ""
        return r.choice(list(self._map.keys()))
