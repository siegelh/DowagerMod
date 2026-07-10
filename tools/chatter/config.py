"""Config loader for the DowagerMod Chatter sidecar.

**`.env` is the single source of truth.**

Loading model (side-effect free; never mutates ``os.environ``):

  1. Snapshot ``os.environ`` once at boot. Real shell exports always win
     so an operator can do ``$env:DOWAGER_CHATTER_LOG_LEVEL='DEBUG'`` for a
     one-shot debug session without touching ``.env``.
  2. Find ``.env`` via ``tools.chatter.dotenv.find_dotenv`` (override,
     repo root, ``tools/chatter/.env``).
  3. Parse it into a dict.
  4. Merge: ``DEFAULTS`` → parsed ``.env`` → real-env snapshot.

If ``.env`` is missing the loader still returns a Config populated from
DEFAULTS so callers (tests, ``Chatter-Status.ps1``) don't crash, but the
daemon and the PS launcher call ``ensure_env_file()`` first to fail
loudly with operator guidance -- we never want the daemon to come up
unauthenticated.

Legacy ``%LOCALAPPDATA%\\DowagerMod\\chatter\\config.json`` is no longer
read; it's only surfaced via ``legacy_config_path()`` so the daemon and
``Chatter-Status.ps1`` can warn that an old file is being ignored.
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional, Tuple

from tools.chatter.dotenv import (
    EnvFileMissingError,
    ensure_dotenv_file,
    find_dotenv,
    parse_dotenv_file,
)


DEFAULTS = {
    "endpoint": "https://discordagent.cognitiveservices.azure.com/",
    "deployment": "gpt-5.4-mini",
    "api_key": "",
    "api_version": "2024-12-01-preview",
    "enabled": True,
    "max_tokens": 10000,
    "max_tokens_multi_turn": 10000,
    "request_timeout_seconds": 180,
    "rate_limit_seconds": 1.0,
    "max_in_flight": 4,
    "circuit_breaker": {"failure_threshold": 3, "open_seconds": 120},
    "spool_poll_interval_seconds": 0.5,
    "request_ttl_seconds": 60,
    "response_ttl_seconds": 3600,
    "log_level": "INFO",
    # Voiceover (Azure Speech + Discord bot) -- all optional. When
    # voiceover_enabled is False or any required field is empty, the daemon
    # skips TTS and the bot is never started; text chatter is unaffected.
    "voiceover_enabled": False,
    "azure_speech_endpoint": "",
    "azure_speech_key": "",
    "azure_speech_voice": "en-US-AriaNeural",
    # Default SSML <prosody rate=...> applied to every leader voice that
    # doesn't override it in leader_voices.json. Empty string = no global
    # rate offset; leaders speak at the neutral TTS baseline. Per-leader
    # rate overrides in leader_voices.json still apply, and CHAT_REPLY
    # tone-specific rate adjustments still layer on top per-line.
    "speech_rate": "",
    "voiceover_daily_char_cap": 0,
    "discord_bot_token": "",
    "discord_guild_id": "",
    "discord_voice_channel_id": "",
    # Chat-reply (player <-> AI conversations via the in-game chat box)
    "chat_idle_seconds": 120,           # active-partner pointer expires after this much silence
    "chat_history_seconds": 300,        # shared room is wiped after this much silence (5 min idle)
    "chat_max_history_turns": 24,       # rolling window: oldest turns drop off the front past this many
    "chat_reply_max_tokens": 10000,     # generous budget -- an 18-word line + JSON wrapper is ~40 tokens, but we never want to risk truncation
    "ask_max_tokens": 10000,            # Discord 'ask:' / 'ask as <leader>:' command -- generous, since user values quality over budget
    # Native-tongue mode: when true, the LLM also generates a translation
    # of each line into the speaker's native language, and the TTS speaks
    # the native version. The English version still appears in-game in the
    # event log (subtitles). Trade-off: slightly higher token use, voice
    # quality varies on rare languages. False = English audio for all leaders.
    "native_tongue_mode": False,
    # ElevenLabs (optional, per-leader override). When the API key is empty
    # the dispatcher skips ElevenLabs entirely and all leaders use Azure
    # Speech as today. When set, leaders whose leader_voices.json entry
    # carries "tts_provider": "elevenlabs" try ElevenLabs first and fall
    # back to Azure Speech on any failure.
    "elevenlabs_api_key": "",
    "elevenlabs_endpoint": "https://api.elevenlabs.io",
    "elevenlabs_model": "eleven_flash_v2_5",
    "elevenlabs_voice_id_dowager": "",
    "elevenlabs_timeout_seconds": 20.0,
    "elevenlabs_daily_char_cap": 0,
    # Circuit-breaker tuning for the ElevenLabs provider. Two consecutive
    # failures trip the breaker for 600 seconds; while open, the dispatcher
    # skips ElevenLabs and goes straight to Azure. Azure failures are
    # unaffected by this counter.
    "elevenlabs_failure_threshold": 2,
    "elevenlabs_cooldown_seconds": 600,
    # Local TTS server (optional). When set, leaders with ElevenLabs or
    # local tts_provider try the local server first (free, GPU-accelerated)
    # and fall back to ElevenLabs / Azure on failure.
    "local_tts_url": "",
    "local_tts_voice_id_dowager": "dowager",
    "local_tts_timeout_seconds": 30.0,
}


# Strings that ``.env.example`` ships with as placeholders. If any one of
# these is left in ``.env`` we treat the field as un-set (validation
# rejects, the daemon's ``is_configured`` returns False). Update this set
# whenever a new ``paste-your-*-here`` placeholder is added to
# ``.env.example``.
PLACEHOLDER_VALUES = frozenset({
    "paste-your-foundry-key-here",
    "paste-your-speech-key-here",
    "paste-your-bot-token-here",
    "paste-your-server-id-here",
    "paste-your-voice-channel-id-here",
})


def is_placeholder(value: str) -> bool:
    """True if ``value`` is one of the ``.env.example`` placeholder strings."""
    return bool(value) and value.strip() in PLACEHOLDER_VALUES


@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = 3
    open_seconds: int = 120


@dataclass
class VoiceoverConfig:
    enabled: bool = False
    azure_speech_endpoint: str = ""
    azure_speech_key: str = ""
    azure_speech_voice: str = "en-US-AriaNeural"
    speech_rate: str = ""
    daily_char_cap: int = 0
    discord_bot_token: str = ""
    discord_guild_id: str = ""
    discord_voice_channel_id: str = ""
    native_tongue_mode: bool = False
    # ElevenLabs (optional per-leader override; Azure remains the fallback).
    elevenlabs_api_key: str = ""
    elevenlabs_endpoint: str = "https://api.elevenlabs.io"
    elevenlabs_model: str = "eleven_flash_v2_5"
    elevenlabs_voice_id_dowager: str = ""
    elevenlabs_timeout_seconds: float = 20.0
    elevenlabs_daily_char_cap: int = 0
    elevenlabs_failure_threshold: int = 2
    elevenlabs_cooldown_seconds: int = 600
    # Local TTS server (optional; highest priority when running).
    local_tts_url: str = ""
    local_tts_voice_id_dowager: str = "dowager"
    local_tts_timeout_seconds: float = 30.0

    def elevenlabs_enabled(self) -> bool:
        """True iff ElevenLabs is configured to be attempted at all.

        Missing key => feature off; voiceover still works on Azure.
        """
        return bool(
            self.elevenlabs_api_key
            and not is_placeholder(self.elevenlabs_api_key)
        )

    def redacted_elevenlabs_key(self) -> str:
        if not self.elevenlabs_api_key:
            return "<empty>"
        if len(self.elevenlabs_api_key) <= 8:
            return "***"
        return self.elevenlabs_api_key[:4] + "..." + self.elevenlabs_api_key[-4:]

    def local_tts_enabled(self) -> bool:
        """True iff a local TTS server URL is configured."""
        return bool(self.local_tts_url and self.local_tts_url.strip())

    def is_ready(self) -> bool:
        """True iff all fields needed to actually run voiceover are populated."""
        return bool(
            self.enabled
            and self.azure_speech_endpoint
            and self.azure_speech_key
            and not is_placeholder(self.azure_speech_key)
            and self.discord_bot_token
            and not is_placeholder(self.discord_bot_token)
            and self.discord_guild_id
            and not is_placeholder(self.discord_guild_id)
            and self.discord_voice_channel_id
            and not is_placeholder(self.discord_voice_channel_id)
        )

    def redacted_speech_key(self) -> str:
        if not self.azure_speech_key:
            return "<empty>"
        if len(self.azure_speech_key) <= 8:
            return "***"
        return self.azure_speech_key[:4] + "..." + self.azure_speech_key[-4:]

    def redacted_bot_token(self) -> str:
        if not self.discord_bot_token:
            return "<empty>"
        if len(self.discord_bot_token) <= 8:
            return "***"
        return self.discord_bot_token[:4] + "..." + self.discord_bot_token[-4:]


@dataclass
class Config:
    endpoint: str = ""
    deployment: str = ""
    api_key: str = ""
    api_version: str = "2024-12-01-preview"
    enabled: bool = True
    max_tokens: int = 10000
    max_tokens_multi_turn: int = 10000
    request_timeout_seconds: float = 180.0
    rate_limit_seconds: float = 1.0
    max_in_flight: int = 4
    circuit_breaker: CircuitBreakerConfig = field(default_factory=CircuitBreakerConfig)
    spool_poll_interval_seconds: float = 0.5
    request_ttl_seconds: float = 60.0
    response_ttl_seconds: float = 3600.0
    log_level: str = "INFO"
    chat_idle_seconds: float = 120.0
    chat_history_seconds: float = 300.0
    chat_max_history_turns: int = 24
    chat_reply_max_tokens: int = 10000
    ask_max_tokens: int = 10000
    voiceover: VoiceoverConfig = field(default_factory=VoiceoverConfig)
    # Path to the .env file that supplied values, or None if no .env was
    # found at load time. Populated by load_config(); not user-settable.
    env_file: Optional[Path] = None

    def redacted_api_key(self) -> str:
        if not self.api_key:
            return "<empty>"
        if len(self.api_key) <= 8:
            return "***"
        return self.api_key[:4] + "..." + self.api_key[-4:]


def config_dir() -> Path:
    """Per-user, per-machine state dir for chatter (spool, etc.).

    Still used by ``spool_dir()``. The directory itself is fine; we just
    no longer write a ``config.json`` into it.
    """
    appdata = os.environ.get("LOCALAPPDATA", str(Path.home() / "AppData" / "Local"))
    return Path(appdata) / "DowagerMod" / "chatter"


def legacy_config_path() -> Path:
    """Path of the deprecated ``config.json`` (pre-.env refactor).

    The file is never read anymore; the daemon and ``Chatter-Status.ps1``
    use this to surface a one-time IGNORED warning so operators know
    their old settings are no longer in effect.
    """
    return config_dir() / "config.json"


def legacy_config_exists() -> bool:
    try:
        return legacy_config_path().is_file()
    except OSError:
        return False


def env_path() -> Optional[Path]:
    """Return the resolved .env path (first existing candidate), or None."""
    return find_dotenv()


def ensure_env_file() -> Path:
    """Return the .env path or raise ``EnvFileMissingError`` with guidance.

    Re-exported from ``dotenv.ensure_dotenv_file`` so callers don't have
    to know about the two-module split.
    """
    return ensure_dotenv_file()


def spool_dir() -> Path:
    """Return the chatter spool directory.

    Lives at ``%LOCALAPPDATA%\\DowagerMod\\chatter\\spool``. Per-user,
    per-machine, never synced. Survives the installer's wipe of
    ``Documents\\My Games\\Beyond the Sword`` (which used to clobber the
    daemon's PID file mid-flight). Sibling of where ``config.json`` used
    to live -- ``config_dir()`` returns ``%LOCALAPPDATA%\\DowagerMod\\chatter``.

    NOT inside Civ4's ``My Games`` tree because:
      1. That tree may live in OneDrive (Documents redirection); OneDrive
         sync delays caused 60+ second heartbeat-staleness gaps that
         tripped the game-side capability check.
      2. The DowagerMod installer wipes the entire ``My Games\\Beyond the
         Sword`` tree (preserving only ``Saves/`` + ``CivilizationIV.ini``)
         to invalidate Civ4's XML cache. That wipe used to delete the
         spool directory while the daemon was running.

    Old (pre-relocation) location was
    ``Documents\\My Games\\Beyond the Sword\\Logs\\DowagerMod\\chatter``.
    """
    return config_dir() / "spool"


# Bool caster shared by every "0/1/true/false/yes/no/on/off" env var.
def _as_bool(v: str) -> bool:
    return str(v).strip().lower() in ("1", "true", "yes", "on")


# (cfg-dict-key, caster) keyed by env-var name. Every chatter knob that
# can be tuned via .env or shell export is listed here exactly once.
# Add new ones at the bottom of the matching section and also extend
# .env.example so the two surfaces stay in lockstep.
_ENV_MAP: Dict[str, Tuple[str, callable]] = {
    # --- Core LLM client ---
    "DOWAGER_CHATTER_ENDPOINT": ("endpoint", str),
    "DOWAGER_CHATTER_DEPLOYMENT": ("deployment", str),
    "DOWAGER_CHATTER_API_KEY": ("api_key", str),
    "DOWAGER_CHATTER_API_VERSION": ("api_version", str),
    "DOWAGER_CHATTER_LOG_LEVEL": ("log_level", str),
    "DOWAGER_CHATTER_ENABLED": ("enabled", _as_bool),
    # --- Request budgets / throttling ---
    "DOWAGER_CHATTER_MAX_TOKENS": ("max_tokens", int),
    "DOWAGER_CHATTER_MAX_TOKENS_MULTI_TURN": ("max_tokens_multi_turn", int),
    "DOWAGER_CHATTER_REQUEST_TIMEOUT_SECONDS": ("request_timeout_seconds", float),
    "DOWAGER_CHATTER_RATE_LIMIT_SECONDS": ("rate_limit_seconds", float),
    "DOWAGER_CHATTER_MAX_IN_FLIGHT": ("max_in_flight", int),
    "DOWAGER_CHATTER_SPOOL_POLL_INTERVAL_SECONDS": ("spool_poll_interval_seconds", float),
    "DOWAGER_CHATTER_REQUEST_TTL_SECONDS": ("request_ttl_seconds", float),
    "DOWAGER_CHATTER_RESPONSE_TTL_SECONDS": ("response_ttl_seconds", float),
    # Circuit-breaker keys are flat in env-var space, nested in DEFAULTS
    # under "circuit_breaker". Resolved by _merge_circuit_breaker() below.
    "DOWAGER_CHATTER_CIRCUIT_BREAKER_FAILURE_THRESHOLD": ("circuit_breaker.failure_threshold", int),
    "DOWAGER_CHATTER_CIRCUIT_BREAKER_OPEN_SECONDS": ("circuit_breaker.open_seconds", int),
    # --- Voiceover ---
    "DOWAGER_CHATTER_VOICEOVER_ENABLED": ("voiceover_enabled", _as_bool),
    "DOWAGER_CHATTER_SPEECH_ENDPOINT": ("azure_speech_endpoint", str),
    "DOWAGER_CHATTER_SPEECH_KEY": ("azure_speech_key", str),
    "DOWAGER_CHATTER_SPEECH_VOICE": ("azure_speech_voice", str),
    "DOWAGER_CHATTER_SPEECH_RATE": ("speech_rate", str),
    "DOWAGER_CHATTER_VOICEOVER_DAILY_CHAR_CAP": ("voiceover_daily_char_cap", int),
    "DOWAGER_CHATTER_DISCORD_BOT_TOKEN": ("discord_bot_token", str),
    "DOWAGER_CHATTER_DISCORD_GUILD_ID": ("discord_guild_id", str),
    "DOWAGER_CHATTER_DISCORD_VOICE_CHANNEL_ID": ("discord_voice_channel_id", str),
    "DOWAGER_CHATTER_NATIVE_TONGUE_MODE": ("native_tongue_mode", _as_bool),
    # --- ElevenLabs (optional per-leader override) ---
    "DOWAGER_CHATTER_ELEVENLABS_API_KEY": ("elevenlabs_api_key", str),
    "DOWAGER_CHATTER_ELEVENLABS_ENDPOINT": ("elevenlabs_endpoint", str),
    "DOWAGER_CHATTER_ELEVENLABS_MODEL": ("elevenlabs_model", str),
    "DOWAGER_CHATTER_ELEVENLABS_VOICE_ID_DOWAGER": ("elevenlabs_voice_id_dowager", str),
    "DOWAGER_CHATTER_ELEVENLABS_TIMEOUT_SECONDS": ("elevenlabs_timeout_seconds", float),
    "DOWAGER_CHATTER_ELEVENLABS_DAILY_CHAR_CAP": ("elevenlabs_daily_char_cap", int),
    "DOWAGER_CHATTER_ELEVENLABS_FAILURE_THRESHOLD": ("elevenlabs_failure_threshold", int),
    "DOWAGER_CHATTER_ELEVENLABS_COOLDOWN_SECONDS": ("elevenlabs_cooldown_seconds", int),
    # --- Local TTS server ---
    "DOWAGER_CHATTER_LOCAL_TTS_URL": ("local_tts_url", str),
    "DOWAGER_CHATTER_LOCAL_TTS_VOICE_ID_DOWAGER": ("local_tts_voice_id_dowager", str),
    "DOWAGER_CHATTER_LOCAL_TTS_TIMEOUT_SECONDS": ("local_tts_timeout_seconds", float),
    # --- Chat-reply tunables ---
    "DOWAGER_CHATTER_CHAT_IDLE_SECONDS": ("chat_idle_seconds", float),
    "DOWAGER_CHATTER_CHAT_HISTORY_SECONDS": ("chat_history_seconds", float),
    "DOWAGER_CHATTER_CHAT_MAX_HISTORY_TURNS": ("chat_max_history_turns", int),
    "DOWAGER_CHATTER_CHAT_REPLY_MAX_TOKENS": ("chat_reply_max_tokens", int),
    "DOWAGER_CHATTER_ASK_MAX_TOKENS": ("ask_max_tokens", int),
}


def _set_dotted(raw: dict, dotted_key: str, value) -> None:
    """Set ``raw[a][b] = value`` for dotted_key ``"a.b"``; otherwise raw[k]=v."""
    if "." not in dotted_key:
        raw[dotted_key] = value
        return
    head, _, tail = dotted_key.partition(".")
    sub = raw.get(head)
    if not isinstance(sub, dict):
        sub = {}
        raw[head] = sub
    _set_dotted(sub, tail, value)


def _apply_env_map(raw: dict, source: Dict[str, str]) -> None:
    """Apply ``DOWAGER_CHATTER_*`` keys from ``source`` into ``raw`` in place."""
    for env_key, (cfg_key, caster) in _ENV_MAP.items():
        if env_key not in source:
            continue
        value = source[env_key]
        if value == "":
            continue
        try:
            _set_dotted(raw, cfg_key, caster(value))
        except Exception:  # noqa: BLE001 — never raise from config load
            pass


def load_config(path: Optional[Path] = None) -> Config:
    """Load config from ``.env`` + real process env.

    Precedence (last wins):
        1. ``DEFAULTS``
        2. ``.env`` file (parsed, never injected into ``os.environ``)
        3. real shell exports captured at the start of this call

    Always returns a ``Config`` -- never raises. If ``.env`` is missing,
    DEFAULTS apply and ``cfg.env_file`` is ``None``. Callers that REQUIRE
    a .env (the daemon, ``Setup-Chatter.ps1``, ``Start-Chatter.ps1``) must
    call :func:`ensure_env_file` themselves before this.

    Tests can:
      * point ``$env:DOWAGER_CHATTER_ENV_PATH`` at a tmp .env to inject values
      * set ``DOWAGER_CHATTER_SKIP_DOTENV=1`` to ignore any found .env
        (used by ``conftest.py`` so tests don't pick up the dev's real .env)

    The ``path`` parameter is accepted for back-compat with the old
    signature (``load_config(path_to_config_json)``) and is IGNORED;
    .env is the only file we read now.
    """
    # 1. Snapshot real env up front. Doing it now (vs. reading os.environ
    #    repeatedly later) makes the merge order explicit and lets a
    #    future hot-reload path reason about "what did the shell set vs.
    #    what came from .env" without state drift.
    real_env = {k: v for k, v in os.environ.items() if k.startswith("DOWAGER_CHATTER_")}

    raw = dict(DEFAULTS)
    # Deep-copy the nested dict so per-call mutations never leak into DEFAULTS.
    raw["circuit_breaker"] = dict(DEFAULTS["circuit_breaker"])

    # 2. .env (best-effort; never raises).
    env_file_used: Optional[Path] = None
    if not os.environ.get("DOWAGER_CHATTER_SKIP_DOTENV"):
        env_file_used = find_dotenv()
        if env_file_used is not None:
            parsed = parse_dotenv_file(env_file_used)
            _apply_env_map(raw, parsed)

    # 3. Real shell exports always win over .env.
    _apply_env_map(raw, real_env)

    cb = raw.get("circuit_breaker", {}) or {}
    return Config(
        endpoint=str(raw.get("endpoint", "")),
        deployment=str(raw.get("deployment", "")),
        api_key=str(raw.get("api_key", "")),
        api_version=str(raw.get("api_version", "2024-12-01-preview")),
        enabled=bool(raw.get("enabled", True)),
        max_tokens=int(raw.get("max_tokens", 10000)),
        max_tokens_multi_turn=int(raw.get("max_tokens_multi_turn", 10000)),
        request_timeout_seconds=float(raw.get("request_timeout_seconds", 180)),
        rate_limit_seconds=float(raw.get("rate_limit_seconds", 1.0)),
        max_in_flight=int(raw.get("max_in_flight", 4)),
        circuit_breaker=CircuitBreakerConfig(
            failure_threshold=int(cb.get("failure_threshold", 3)),
            open_seconds=int(cb.get("open_seconds", 120)),
        ),
        spool_poll_interval_seconds=float(raw.get("spool_poll_interval_seconds", 0.5)),
        request_ttl_seconds=float(raw.get("request_ttl_seconds", 60)),
        response_ttl_seconds=float(raw.get("response_ttl_seconds", 3600)),
        log_level=str(raw.get("log_level", "INFO")).upper(),
        chat_idle_seconds=float(raw.get("chat_idle_seconds", 120)),
        chat_history_seconds=float(raw.get("chat_history_seconds", 300)),
        chat_max_history_turns=int(raw.get("chat_max_history_turns", 24)),
        chat_reply_max_tokens=int(raw.get("chat_reply_max_tokens", 10000)),
        ask_max_tokens=int(raw.get("ask_max_tokens", 10000)),
        voiceover=VoiceoverConfig(
            enabled=bool(raw.get("voiceover_enabled", False)),
            azure_speech_endpoint=str(raw.get("azure_speech_endpoint", "")),
            azure_speech_key=str(raw.get("azure_speech_key", "")),
            azure_speech_voice=str(raw.get("azure_speech_voice", "en-US-AriaNeural")),
            speech_rate=str(raw.get("speech_rate", "")),
            daily_char_cap=int(raw.get("voiceover_daily_char_cap", 0)),
            discord_bot_token=str(raw.get("discord_bot_token", "")),
            discord_guild_id=str(raw.get("discord_guild_id", "")),
            discord_voice_channel_id=str(raw.get("discord_voice_channel_id", "")),
            native_tongue_mode=bool(raw.get("native_tongue_mode", False)),
            elevenlabs_api_key=str(raw.get("elevenlabs_api_key", "")),
            elevenlabs_endpoint=str(raw.get("elevenlabs_endpoint", "https://api.elevenlabs.io")),
            elevenlabs_model=str(raw.get("elevenlabs_model", "eleven_flash_v2_5")),
            elevenlabs_voice_id_dowager=str(raw.get("elevenlabs_voice_id_dowager", "")),
            elevenlabs_timeout_seconds=float(raw.get("elevenlabs_timeout_seconds", 20.0)),
            elevenlabs_daily_char_cap=int(raw.get("elevenlabs_daily_char_cap", 0)),
            elevenlabs_failure_threshold=int(raw.get("elevenlabs_failure_threshold", 2)),
            elevenlabs_cooldown_seconds=int(raw.get("elevenlabs_cooldown_seconds", 600)),
            local_tts_url=str(raw.get("local_tts_url", "")),
            local_tts_voice_id_dowager=str(raw.get("local_tts_voice_id_dowager", "dowager")),
            local_tts_timeout_seconds=float(raw.get("local_tts_timeout_seconds", 30.0)),
        ),
        env_file=env_file_used,
    )


def is_configured(cfg: Config) -> bool:
    """True iff config has the minimum fields needed to call the API.

    Rejects placeholder strings (``paste-your-foundry-key-here`` etc.)
    so a freshly-copied ``.env.example`` never silently passes muster.
    """
    return bool(
        cfg.endpoint
        and cfg.deployment
        and cfg.api_key
        and not is_placeholder(cfg.api_key)
        and cfg.enabled
    )


def validate_required(cfg: Config) -> list:
    """Return a list of human-readable problems with ``cfg``.

    Empty list means ready to run. Used by ``Setup-Chatter.ps1`` to give
    operator-friendly errors before scheduling the daemon. Validation is
    conditional: text-only mode needs Foundry credentials; voiceover
    mode additionally needs Speech + Discord credentials.
    """
    problems: list = []

    def _missing(label: str, value: str) -> None:
        if not value:
            problems.append("missing: " + label)
        elif is_placeholder(value):
            problems.append("placeholder not replaced: " + label)

    _missing("DOWAGER_CHATTER_ENDPOINT", cfg.endpoint)
    _missing("DOWAGER_CHATTER_DEPLOYMENT", cfg.deployment)
    _missing("DOWAGER_CHATTER_API_KEY", cfg.api_key)

    if cfg.voiceover.enabled:
        _missing("DOWAGER_CHATTER_SPEECH_ENDPOINT", cfg.voiceover.azure_speech_endpoint)
        _missing("DOWAGER_CHATTER_SPEECH_KEY", cfg.voiceover.azure_speech_key)
        _missing("DOWAGER_CHATTER_DISCORD_BOT_TOKEN", cfg.voiceover.discord_bot_token)
        _missing("DOWAGER_CHATTER_DISCORD_GUILD_ID", cfg.voiceover.discord_guild_id)
        _missing("DOWAGER_CHATTER_DISCORD_VOICE_CHANNEL_ID", cfg.voiceover.discord_voice_channel_id)

    return problems


__all__ = [
    "DEFAULTS",
    "PLACEHOLDER_VALUES",
    "Config",
    "CircuitBreakerConfig",
    "VoiceoverConfig",
    "EnvFileMissingError",
    "config_dir",
    "env_path",
    "ensure_env_file",
    "is_configured",
    "is_placeholder",
    "legacy_config_exists",
    "legacy_config_path",
    "load_config",
    "spool_dir",
    "validate_required",
]
