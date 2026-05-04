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
    "endpoint": "https://hasiegeltestingfoundry.services.ai.azure.com/openai/v1",
    "deployment": "gpt-5.4-mini",
    "api_key": "",
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
}


@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = 3
    open_seconds: int = 120


@dataclass
class Config:
    endpoint: str = ""
    deployment: str = ""
    api_key: str = ""
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
    home = Path(os.environ.get("USERPROFILE", str(Path.home())))
    return home / "Documents" / "My Games" / "Beyond the Sword" / "Logs" / "DowagerMod" / "chatter"


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
    )


def is_configured(cfg: Config) -> bool:
    """True iff config has the minimum fields needed to call the API."""
    return bool(cfg.endpoint and cfg.deployment and cfg.api_key and cfg.enabled)
