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
    "voiceover_daily_char_cap": 100000,
    "discord_bot_token": "",
    "discord_guild_id": "",
    "discord_voice_channel_id": "",
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
    daily_char_cap: int = 100000
    discord_bot_token: str = ""
    discord_guild_id: str = ""
    discord_voice_channel_id: str = ""

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
    """Return the actual chatter spool path under Civ4's My Games\\Beyond the Sword.

    Civ4 uses SHGetFolderPath(CSIDL_PERSONAL) which respects OneDrive Documents
    redirection. USERPROFILE\\Documents may NOT match — when Documents is
    redirected to OneDrive, the game writes to OneDrive\\Documents\\... but a
    naive expanduser uses the empty USERPROFILE\\Documents. We probe both.
    """
    candidates: list[Path] = []
    user_profile = os.environ.get("USERPROFILE", "")
    if user_profile:
        # OneDrive-prefixed sibling dirs under USERPROFILE
        try:
            for name in os.listdir(user_profile):
                if name.lower().startswith("onedrive"):
                    root = Path(user_profile) / name
                    candidates.append(root / "Documents" / "My Games" / "Beyond the Sword")
                    candidates.append(root / "Documents" / "My Games" / "beyond the sword")
        except OSError:
            pass
        candidates.append(Path(user_profile) / "Documents" / "My Games" / "Beyond the Sword")
        candidates.append(Path(user_profile) / "Documents" / "My Games" / "beyond the sword")
    for key in ("OneDriveCommercial", "OneDriveConsumer", "OneDrive"):
        root_str = os.environ.get(key, "")
        if root_str:
            root = Path(root_str)
            candidates.append(root / "Documents" / "My Games" / "Beyond the Sword")
            candidates.append(root / "Documents" / "My Games" / "beyond the sword")
    # Pick the first that exists; if none, fall back to the first candidate
    chosen: Path | None = None
    for c in candidates:
        if c.is_dir():
            chosen = c
            break
    if chosen is None and candidates:
        chosen = candidates[0]
    if chosen is None:
        chosen = Path(os.path.expanduser("~")) / "Documents" / "My Games" / "Beyond the Sword"
    return chosen / "Logs" / "DowagerMod" / "chatter"


def load_config(path: Optional[Path] = None) -> Config:
    """Load config from file (if it exists) merged with defaults, then env overrides."""
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

    # Env overrides (DOWAGER_CHATTER_*).
    for env_key, cfg_key in [
        ("DOWAGER_CHATTER_ENDPOINT", "endpoint"),
        ("DOWAGER_CHATTER_DEPLOYMENT", "deployment"),
        ("DOWAGER_CHATTER_API_KEY", "api_key"),
        ("DOWAGER_CHATTER_LOG_LEVEL", "log_level"),
    ]:
        if env_key in os.environ and os.environ[env_key]:
            raw[cfg_key] = os.environ[env_key]

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
        voiceover=VoiceoverConfig(
            enabled=bool(raw.get("voiceover_enabled", False)),
            azure_speech_endpoint=str(raw.get("azure_speech_endpoint", "")),
            azure_speech_key=str(raw.get("azure_speech_key", "")),
            azure_speech_voice=str(raw.get("azure_speech_voice", "en-US-AriaNeural")),
            daily_char_cap=int(raw.get("voiceover_daily_char_cap", 100000)),
            discord_bot_token=str(raw.get("discord_bot_token", "")),
            discord_guild_id=str(raw.get("discord_guild_id", "")),
            discord_voice_channel_id=str(raw.get("discord_voice_channel_id", "")),
        ),
    )


def is_configured(cfg: Config) -> bool:
    """True iff config has the minimum fields needed to call the API."""
    return bool(cfg.endpoint and cfg.deployment and cfg.api_key and cfg.enabled)
