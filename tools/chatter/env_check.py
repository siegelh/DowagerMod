"""Print chatter sidecar config status as JSON. Used by Setup/Status PS scripts.

Exit codes:
  0  ready to run (env present + no validation problems)
  2  env present but validation failed (missing keys, placeholders, ...)
  3  no .env found
  4  unexpected error (printed as JSON)

Output is always a single JSON object on stdout so PowerShell can
``ConvertFrom-Json`` it. Lives in a separate module so we don't bloat
``config.py`` with CLI / formatting concerns.
"""
from __future__ import annotations

import json
import os
import sys
import traceback
from pathlib import Path

# Ensure repo root is on sys.path when this module is run as `python -m
# tools.chatter.env_check` from the repo root. Belt-and-braces; works the
# same way the daemon does it.
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from tools.chatter import config as cfg_mod
from tools.chatter.dotenv import EnvFileMissingError, _candidate_paths, find_dotenv


def _redact(value: str, keep: int = 4) -> str:
    if not value:
        return ""
    if len(value) <= keep * 2:
        return "***"
    return value[:keep] + "..." + value[-keep:]


def build_report() -> dict:
    """Build the status report dict. Never raises (errors -> 'error' key)."""
    try:
        env_file = find_dotenv()
        if env_file is None:
            return {
                "env_present": False,
                "env_path": None,
                "candidates": [str(p) for p in _candidate_paths()],
                "problems": ["no .env file found"],
                "redacted": {},
                "legacy_present": cfg_mod.legacy_config_exists(),
                "legacy_path": str(cfg_mod.legacy_config_path()),
                "ready": False,
            }

        cfg = cfg_mod.load_config()
        problems = cfg_mod.validate_required(cfg)
        report = {
            "env_present": True,
            "env_path": str(env_file),
            "problems": problems,
            "redacted": {
                "endpoint": cfg.endpoint,
                "deployment": cfg.deployment,
                "api_key": cfg.redacted_api_key(),
                "log_level": cfg.log_level,
                "voiceover_enabled": cfg.voiceover.enabled,
                "voiceover_ready": cfg.voiceover.is_ready(),
                "speech_endpoint": cfg.voiceover.azure_speech_endpoint,
                "speech_voice": cfg.voiceover.azure_speech_voice,
                "speech_key": cfg.voiceover.redacted_speech_key(),
                "discord_bot_token": cfg.voiceover.redacted_bot_token(),
                "discord_guild_id": cfg.voiceover.discord_guild_id,
                "discord_voice_channel_id": cfg.voiceover.discord_voice_channel_id,
                "native_tongue_mode": cfg.voiceover.native_tongue_mode,
            },
            "legacy_present": cfg_mod.legacy_config_exists(),
            "legacy_path": str(cfg_mod.legacy_config_path()),
            "ready": (not problems) and cfg_mod.is_configured(cfg),
        }
        return report
    except Exception as exc:  # noqa: BLE001 — never let env_check raise
        return {
            "env_present": False,
            "env_path": None,
            "problems": ["env_check crashed: " + str(exc)],
            "trace": traceback.format_exc(),
            "redacted": {},
            "legacy_present": False,
            "legacy_path": "",
            "ready": False,
        }


def main(argv=None) -> int:
    report = build_report()
    print(json.dumps(report, indent=2, default=str))
    if not report.get("env_present"):
        return 3
    if report.get("problems"):
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
