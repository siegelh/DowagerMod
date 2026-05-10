"""Config loader for the DowagerMod Chatter sidecar.

Loads from %LOCALAPPDATA%\\DowagerMod\\chatter\\config.json (per-machine,
never committed). Env vars override file values for dev/CI use.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


DEFAULTS = {
    "endpoint": "https://discordagent.cognitiveservices.azure.com/",
    "deployment": "gpt-5.4-mini",
    "api_key": "",
    "api_version": "2024-12-01-preview",
    "enabled": True,
    "max_tokens": 80,
    "max_tokens_multi_turn": 400,
    "request_timeout_seconds": 8,
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
    # doesn't override it in leader_voices.json. "+50%" is the global
    # snappier baseline (was implicitly 0 / neutral). Per-leader rate
    # overrides take precedence; CHAT_REPLY tone-specific rates also
    # take precedence per-line.
    "speech_rate": "+50%",
    "voiceover_daily_char_cap": 100000,
    "discord_bot_token": "",
    "discord_guild_id": "",
    "discord_voice_channel_id": "",
    # Chat-reply (player <-> AI conversations via the in-game chat box)
    "chat_idle_seconds": 120,           # active-partner pointer expires after this much silence
    "chat_history_seconds": 600,        # full conversation history is GC'd after this much silence
    "chat_max_history_turns": 24,       # max turns kept in any one conversation (older drop off front)
    "chat_reply_max_tokens": 120,       # token budget for one chat reply (slightly higher than single-line)
    # Native-tongue mode: when true, the LLM also generates a translation
    # of each line into the speaker's native language, and the TTS speaks
    # the native version. The English version still appears in-game in the
    # event log (subtitles). Trade-off: slightly higher token use, voice
    # quality varies on rare languages. False = English audio for all leaders.
    "native_tongue_mode": False,
}


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
    speech_rate: str = "+50%"
    daily_char_cap: int = 100000
    discord_bot_token: str = ""
    discord_guild_id: str = ""
    discord_voice_channel_id: str = ""
    native_tongue_mode: bool = False

    def is_ready(self) -> bool:
        """True iff all fields needed to actually run voiceover are populated."""
        return bool(
            self.enabled
            and self.azure_speech_endpoint
            and self.azure_speech_key
            and self.discord_bot_token
            and self.discord_guild_id
            and self.discord_voice_channel_id
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
    max_tokens: int = 80
    max_tokens_multi_turn: int = 400
    request_timeout_seconds: float = 8.0
    rate_limit_seconds: float = 1.0
    max_in_flight: int = 4
    circuit_breaker: CircuitBreakerConfig = field(default_factory=CircuitBreakerConfig)
    spool_poll_interval_seconds: float = 0.5
    request_ttl_seconds: float = 60.0
    response_ttl_seconds: float = 3600.0
    log_level: str = "INFO"
    chat_idle_seconds: float = 120.0
    chat_history_seconds: float = 600.0
    chat_max_history_turns: int = 24
    chat_reply_max_tokens: int = 120
    voiceover: VoiceoverConfig = field(default_factory=VoiceoverConfig)

    def redacted_api_key(self) -> str:
        if not self.api_key:
            return "<empty>"
        if len(self.api_key) <= 8:
            return "***"
        return self.api_key[:4] + "..." + self.api_key[-4:]


def config_dir() -> Path:
    appdata = os.environ.get("LOCALAPPDATA", str(Path.home() / "AppData" / "Local"))
    return Path(appdata) / "DowagerMod" / "chatter"


def config_path() -> Path:
    return config_dir() / "config.json"


def spool_dir() -> Path:
    """Return the chatter spool directory.

    Lives at ``%LOCALAPPDATA%\\DowagerMod\\chatter\\spool``. Per-user,
    per-machine, never synced. Survives the installer's wipe of
    ``Documents\\My Games\\Beyond the Sword`` (which used to clobber the
    daemon's PID file mid-flight). Sibling of ``config.json`` for symmetry
    -- ``config_dir()`` returns ``%LOCALAPPDATA%\\DowagerMod\\chatter``.

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


def load_config(path: Optional[Path] = None) -> Config:
    """Load config from .env (if present) + file (if it exists) + env overrides.

    Precedence (last wins):
        1. DEFAULTS
        2. config.json file
        3. .env file (loaded into os.environ once)
        4. process env (real shell exports)

    The .env loader is best-effort and never overrides existing env vars.
    Tests can disable .env by setting DOWAGER_CHATTER_SKIP_DOTENV=1.
    """
    if not os.environ.get("DOWAGER_CHATTER_SKIP_DOTENV"):
        try:
            from tools.chatter.dotenv import load_dotenv
            load_dotenv()
        except Exception:  # noqa: BLE001
            pass

    raw = dict(DEFAULTS)
    p = path or config_path()
    if p.exists():
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            # ignore "_comment" field
            for k, v in data.items():
                if k.startswith("_"):
                    continue
                raw[k] = v
        except Exception as exc:  # noqa: BLE001 — never raise from config load
            # Print to stderr; daemon main loop will keep going
            import sys
            print(f"[config] WARN: failed to read {p}: {exc}", file=sys.stderr)

    # Env overrides (DOWAGER_CHATTER_*). All sidecar config fields can be set
    # via env vars OR a .env file with the same names — useful when a user
    # prefers to manage everything from one file rather than via Setup-Chatter.ps1.
    _ENV_MAP = {
        "DOWAGER_CHATTER_ENDPOINT": ("endpoint", str),
        "DOWAGER_CHATTER_DEPLOYMENT": ("deployment", str),
        "DOWAGER_CHATTER_API_KEY": ("api_key", str),
        "DOWAGER_CHATTER_API_VERSION": ("api_version", str),
        "DOWAGER_CHATTER_LOG_LEVEL": ("log_level", str),
        "DOWAGER_CHATTER_ENABLED": ("enabled", lambda v: str(v).lower() in ("1", "true", "yes", "on")),
        # Voiceover
        "DOWAGER_CHATTER_VOICEOVER_ENABLED": ("voiceover_enabled", lambda v: str(v).lower() in ("1", "true", "yes", "on")),
        "DOWAGER_CHATTER_SPEECH_ENDPOINT": ("azure_speech_endpoint", str),
        "DOWAGER_CHATTER_SPEECH_KEY": ("azure_speech_key", str),
        "DOWAGER_CHATTER_SPEECH_VOICE": ("azure_speech_voice", str),
        "DOWAGER_CHATTER_SPEECH_RATE": ("speech_rate", str),
        "DOWAGER_CHATTER_VOICEOVER_DAILY_CHAR_CAP": ("voiceover_daily_char_cap", int),
        "DOWAGER_CHATTER_DISCORD_BOT_TOKEN": ("discord_bot_token", str),
        "DOWAGER_CHATTER_DISCORD_GUILD_ID": ("discord_guild_id", str),
        "DOWAGER_CHATTER_DISCORD_VOICE_CHANNEL_ID": ("discord_voice_channel_id", str),
        "DOWAGER_CHATTER_NATIVE_TONGUE_MODE": ("native_tongue_mode", lambda v: str(v).lower() in ("1", "true", "yes", "on")),
        # Chat-reply tunables
        "DOWAGER_CHATTER_CHAT_IDLE_SECONDS": ("chat_idle_seconds", float),
        "DOWAGER_CHATTER_CHAT_HISTORY_SECONDS": ("chat_history_seconds", float),
        "DOWAGER_CHATTER_CHAT_MAX_HISTORY_TURNS": ("chat_max_history_turns", int),
        "DOWAGER_CHATTER_CHAT_REPLY_MAX_TOKENS": ("chat_reply_max_tokens", int),
    }
    for env_key, (cfg_key, caster) in _ENV_MAP.items():
        if env_key in os.environ and os.environ[env_key] != "":
            try:
                raw[cfg_key] = caster(os.environ[env_key])
            except Exception:  # noqa: BLE001
                pass

    cb = raw.get("circuit_breaker", {}) or {}
    return Config(
        endpoint=str(raw.get("endpoint", "")),
        deployment=str(raw.get("deployment", "")),
        api_key=str(raw.get("api_key", "")),
        api_version=str(raw.get("api_version", "2024-12-01-preview")),
        enabled=bool(raw.get("enabled", True)),
        max_tokens=int(raw.get("max_tokens", 80)),
        max_tokens_multi_turn=int(raw.get("max_tokens_multi_turn", 400)),
        request_timeout_seconds=float(raw.get("request_timeout_seconds", 8)),
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
        chat_history_seconds=float(raw.get("chat_history_seconds", 600)),
        chat_max_history_turns=int(raw.get("chat_max_history_turns", 24)),
        chat_reply_max_tokens=int(raw.get("chat_reply_max_tokens", 120)),
        voiceover=VoiceoverConfig(
            enabled=bool(raw.get("voiceover_enabled", False)),
            azure_speech_endpoint=str(raw.get("azure_speech_endpoint", "")),
            azure_speech_key=str(raw.get("azure_speech_key", "")),
            azure_speech_voice=str(raw.get("azure_speech_voice", "en-US-AriaNeural")),
            speech_rate=str(raw.get("speech_rate", "+50%")),
            daily_char_cap=int(raw.get("voiceover_daily_char_cap", 100000)),
            discord_bot_token=str(raw.get("discord_bot_token", "")),
            discord_guild_id=str(raw.get("discord_guild_id", "")),
            discord_voice_channel_id=str(raw.get("discord_voice_channel_id", "")),
            native_tongue_mode=bool(raw.get("native_tongue_mode", False)),
        ),
    )


def is_configured(cfg: Config) -> bool:
    """True iff config has the minimum fields needed to call the API."""
    return bool(cfg.endpoint and cfg.deployment and cfg.api_key and cfg.enabled)
