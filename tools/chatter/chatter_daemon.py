"""DowagerMod Chatter sidecar daemon.

Watches the spool directory for chatter requests, calls Azure Foundry,
writes responses back. Runs forever; safe to restart anytime.

Usage:
    python -m tools.chatter.chatter_daemon

Or via the helper script tools\\Start-Chatter.ps1.
"""
from __future__ import annotations

import logging
import os
import random
import sys
import time
from pathlib import Path
from typing import Optional

# Allow `python tools/chatter/chatter_daemon.py` invocation alongside `-m`.
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from tools.chatter import config as cfg_mod
from tools.chatter import spool as spool_mod
from tools.chatter.azure_client import AzureClient, AuthError, ApiError, parse_multi_turn_lines, looks_like_refusal
from tools.chatter.circuit import CircuitBreaker
from tools.chatter.prompts import build_single_line_prompt, build_multi_turn_prompt
from tools.chatter.state import StateStore


REJOINDER_MIN_MS = 5000
REJOINDER_MAX_MS = 10000
SCHEMA_VERSION = 1
HEARTBEAT_INTERVAL_SECONDS = 15


def setup_logging(spool_path: Path, level_name: str) -> logging.Logger:
    spool_path.mkdir(parents=True, exist_ok=True)
    log_path = spool_path / "daemon.log"
    handler = logging.FileHandler(str(log_path), encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger = logging.getLogger("chatter")
    logger.setLevel(getattr(logging, level_name.upper(), logging.INFO))
    # Idempotent — clear existing handlers first
    for h in list(logger.handlers):
        logger.removeHandler(h)
    logger.addHandler(handler)
    logger.propagate = False
    return logger


def make_response(*, request: dict, ok: bool, lines, error: Optional[str], latency_ms: int = 0,
                  input_tokens: int = 0, output_tokens: int = 0) -> dict:
    return {
        "schema": SCHEMA_VERSION,
        "request_id": request.get("request_id"),
        "session_id": request.get("session_id"),
        "elector_player_id": request.get("elector_player_id"),
        "ok": ok,
        "lines": lines,
        "error": error,
        "latency_ms": latency_ms,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "completed_at_unix": time.time(),
    }


def render_single_line(request: dict, text: str) -> list:
    speaker = request.get("speaker") or {}
    return [{
        "speaker_player_id": int(speaker.get("player_id", -1)),
        "speaker_name": speaker.get("leader_name", ""),
        "text": text,
        "delay_ms": 0,
    }]


def render_multi_turn(request: dict, parsed: list) -> list:
    """Map parsed [{speaker:'Victoria', line:'...'}] to spool line entries.

    Speaker-name -> player-id resolution is done by name match against the
    request's speaker/target. Anything that doesn't match falls back to the
    speaker's player ID (defensive — better to attribute to original speaker
    than crash later).
    """
    speaker = request.get("speaker") or {}
    target = request.get("target") or {}
    name_map = {}
    if speaker.get("leader_name"):
        name_map[speaker["leader_name"].lower()] = int(speaker.get("player_id", -1))
    if target.get("leader_name"):
        name_map[target["leader_name"].lower()] = int(target.get("player_id", -1))

    out = []
    for i, item in enumerate(parsed):
        spk_name = item["speaker"].strip()
        spk_id = name_map.get(spk_name.lower(), int(speaker.get("player_id", -1)))
        delay_ms = 0 if i == 0 else random.randint(REJOINDER_MIN_MS, REJOINDER_MAX_MS)
        out.append({
            "speaker_player_id": spk_id,
            "speaker_name": spk_name,
            "text": item["line"],
            "delay_ms": delay_ms,
        })
    return out


def process_request(req_path: Path, request: dict, *, client: AzureClient, breaker: CircuitBreaker,
                    logger: logging.Logger, max_tokens: int, max_tokens_multi: int) -> dict:
    """Run one request through the API. Always returns a response dict."""
    if not breaker.can_call():
        logger.info("circuit OPEN, dropping request_id=%s", request.get("request_id"))
        return make_response(request=request, ok=False, lines=[], error="circuit_open")

    multi = bool(request.get("multi_turn"))
    try:
        if multi:
            sys_msg, user_msg = build_multi_turn_prompt(request)
            api_result = client.call_responses(sys_msg, user_msg, max_tokens=max_tokens_multi)
        else:
            sys_msg, user_msg = build_single_line_prompt(request)
            api_result = client.call_responses(sys_msg, user_msg, max_tokens=max_tokens)
    except AuthError as exc:
        breaker.trip_immediately()
        logger.error("auth failure (circuit forced OPEN): %s", exc)
        return make_response(request=request, ok=False, lines=[], error="auth_failure")
    except ApiError as exc:
        breaker.record_failure()
        logger.warning("api failure: %s", exc)
        return make_response(request=request, ok=False, lines=[], error="api_failure")
    except Exception as exc:  # noqa: BLE001 — never raise out of process_request
        breaker.record_failure()
        logger.exception("unexpected failure building/calling: %s", exc)
        return make_response(request=request, ok=False, lines=[], error="unexpected")

    breaker.record_success()
    text = api_result.text

    if looks_like_refusal(text):
        logger.info("model refused, request_id=%s — substituting fallback line",
                    request.get("request_id"))
        # Substitute a canned fallback so the user sees something rather than silence.
        speaker = request.get("speaker") or {}
        target = request.get("target") or {}
        is_broadcast = (request.get("mode") == "broadcast")
        from tools.chatter.azure_client import fallback_line
        fb = fallback_line(
            speaker_name=speaker.get("leader_name", ""),
            target_name=target.get("leader_name", ""),
            broadcast=is_broadcast,
        )
        return make_response(
            request=request, ok=True,
            lines=render_single_line(request, fb),
            error=None,
            latency_ms=api_result.latency_ms,
            input_tokens=api_result.input_tokens,
            output_tokens=api_result.output_tokens,
        )

    if multi:
        try:
            parsed = parse_multi_turn_lines(text)
        except Exception as exc:  # noqa: BLE001
            logger.warning("multi-turn parse failed: %s; falling back to single line", exc)
            lines = render_single_line(request, text)
        else:
            lines = render_multi_turn(request, parsed)
    else:
        lines = render_single_line(request, text)

    return make_response(
        request=request, ok=True, lines=lines, error=None,
        latency_ms=api_result.latency_ms,
        input_tokens=api_result.input_tokens,
        output_tokens=api_result.output_tokens,
    )


def write_response(spool_path: Path, response: dict, logger: logging.Logger) -> None:
    name = spool_mod.gen_filename(spool_mod.RESP_PREFIX)
    out_path = spool_path / name
    try:
        spool_mod.atomic_write_json(out_path, response)
        logger.info("wrote response %s ok=%s lines=%d",
                    name, response.get("ok"), len(response.get("lines") or []))
    except Exception as exc:  # noqa: BLE001
        logger.exception("failed to write response %s: %s", name, exc)


def gc_spool(spool_path: Path, cfg, logger: logging.Logger) -> None:
    try:
        n_req = spool_mod.gc_old_files(spool_path, spool_mod.REQ_PREFIX, cfg.request_ttl_seconds)
        n_resp = spool_mod.gc_old_files(spool_path, spool_mod.RESP_PREFIX, cfg.response_ttl_seconds)
        if n_req or n_resp:
            logger.info("janitor: removed %d stale req, %d stale resp", n_req, n_resp)
        # GC voiceover WAV files older than 1 hour. Best-effort.
        audio_dir = spool_path / "audio"
        if audio_dir.is_dir():
            now = time.time()
            removed = 0
            for p in audio_dir.glob("tts-*.wav"):
                try:
                    if (now - p.stat().st_mtime) > 3600:
                        p.unlink()
                        removed += 1
                except Exception:
                    pass
            if removed:
                logger.info("janitor: removed %d stale tts WAV files", removed)
    except Exception as exc:  # noqa: BLE001
        logger.warning("janitor failed: %s", exc)


def heartbeat(spool_path: Path, logger: logging.Logger) -> None:
    try:
        spool_mod.write_pid_file(spool_path, os.getpid())
    except Exception as exc:  # noqa: BLE001
        logger.warning("heartbeat failed: %s", exc)


def setup_voiceover(cfg, spool_path: Path, logger: logging.Logger):
    """Initialize Speech client + Discord bot + voice picker if voiceover
    is configured.

    Returns (speech_client, bot_worker, voice_picker) tuple. Any may be None
    if not enabled or if startup failed. Failures are logged but don't kill
    the daemon — text chatter remains unaffected.
    """
    if not cfg.voiceover.is_ready():
        if cfg.voiceover.enabled:
            logger.info("voiceover enabled in config but missing fields; skipping")
        return None, None, None

    # Speech client
    try:
        from tools.chatter.azure_speech_client import AzureSpeechClient
        speech_client = AzureSpeechClient(
            endpoint=cfg.voiceover.azure_speech_endpoint,
            key=cfg.voiceover.azure_speech_key,
            default_voice=cfg.voiceover.azure_speech_voice,
            request_timeout_seconds=cfg.request_timeout_seconds,
            daily_char_cap=cfg.voiceover.daily_char_cap,
        )
        logger.info(
            "voiceover: Speech client initialized endpoint=%s voice=%s daily_cap=%d",
            cfg.voiceover.azure_speech_endpoint, cfg.voiceover.azure_speech_voice,
            cfg.voiceover.daily_char_cap,
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("voiceover: Speech client init failed: %s", exc)
        return None, None, None

    # Voice picker (per-leader map)
    voice_picker = None
    try:
        from tools.chatter.voice_picker import VoicePicker
        voice_picker = VoicePicker(
            default_voice=cfg.voiceover.azure_speech_voice,
            logger=logger,
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("voiceover: voice picker init failed: %s", exc)

    # Discord bot
    try:
        from tools.chatter.discord_bot import DiscordBotWorker
        bot = DiscordBotWorker(
            bot_token=cfg.voiceover.discord_bot_token,
            guild_id=int(cfg.voiceover.discord_guild_id),
            voice_channel_id=int(cfg.voiceover.discord_voice_channel_id),
            logger=logger,
        )
        bot.start()
        logger.info(
            "voiceover: Discord bot started guild=%s channel=%s",
            cfg.voiceover.discord_guild_id, cfg.voiceover.discord_voice_channel_id,
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("voiceover: Discord bot init failed: %s", exc)
        return speech_client, None, voice_picker

    return speech_client, bot, voice_picker


def voiceover_response(response: dict, *, speech_client, bot, spool_path: Path, logger: logging.Logger,
                       voice_picker=None) -> None:
    """If voiceover is wired up, synthesize each response line and enqueue
    it to the Discord bot for playback. Failures log + continue (text
    chatter is unaffected).

    If voice_picker is provided, each line's voice is chosen based on the
    speaker's leader name (per-leader voice mapping). Otherwise the speech
    client's default voice is used for every line.
    """
    if speech_client is None or bot is None:
        return
    if not response.get("ok"):
        return
    lines = response.get("lines") or []
    audio_dir = spool_path / "audio"
    try:
        audio_dir.mkdir(parents=True, exist_ok=True)
    except Exception as exc:  # noqa: BLE001
        logger.warning("voiceover: cannot create audio dir %s: %s", audio_dir, exc)
        return

    rid = response.get("request_id") or "unknown"
    from tools.chatter.azure_speech_client import SpeechAuthError, SpeechApiError, SpeechBudgetExhausted
    for idx, ln in enumerate(lines):
        text = (ln.get("text") or "").strip()
        if not text:
            continue
        speaker_name = (ln.get("speaker_name") or "").strip()
        chosen_voice = None
        if voice_picker is not None and speaker_name:
            try:
                chosen_voice = voice_picker.pick_voice(speaker_name)
            except Exception as exc:  # noqa: BLE001
                logger.warning("voiceover: voice pick failed for %r: %s", speaker_name, exc)
                chosen_voice = None
        try:
            result = speech_client.synthesize(text, voice=chosen_voice)
        except SpeechBudgetExhausted as exc:
            logger.warning("voiceover: %s", exc)
            return
        except SpeechAuthError as exc:
            logger.error("voiceover: Speech auth failure (disabling for this run): %s", exc)
            return
        except SpeechApiError as exc:
            logger.warning("voiceover: synth failed for line %d: %s", idx, exc)
            continue
        except Exception as exc:  # noqa: BLE001
            logger.warning("voiceover: unexpected synth failure for line %d: %s", idx, exc)
            continue
        wav_path = audio_dir / f"tts-{rid}-{idx}.wav"
        try:
            wav_path.write_bytes(result.audio_bytes)
        except Exception as exc:  # noqa: BLE001
            logger.warning("voiceover: write WAV failed %s: %s", wav_path, exc)
            continue
        logger.info(
            "voiceover: synth ok rid=%s line=%d speaker=%r voice=%s chars=%d latency=%dms",
            rid, idx, speaker_name, result.voice, result.char_count, result.latency_ms,
        )
        try:
            bot.enqueue_audio(wav_path)
        except Exception as exc:  # noqa: BLE001
            logger.warning("voiceover: enqueue failed for %s: %s", wav_path, exc)


def main_loop(cfg, spool_path: Path, logger: logging.Logger) -> int:
    if not cfg_mod.is_configured(cfg):
        logger.error("config not usable: endpoint=%r deployment=%r api_key=%s enabled=%s",
                     cfg.endpoint, cfg.deployment, cfg.redacted_api_key(), cfg.enabled)
        return 2

    logger.info("starting daemon pid=%d endpoint=%s deployment=%s api_key=%s",
                os.getpid(), cfg.endpoint, cfg.deployment, cfg.redacted_api_key())

    spool_path.mkdir(parents=True, exist_ok=True)
    spool_mod.write_pid_file(spool_path, os.getpid())

    client = AzureClient(
        endpoint=cfg.endpoint,
        api_key=cfg.api_key,
        deployment=cfg.deployment,
        request_timeout_seconds=cfg.request_timeout_seconds,
        api_version=cfg.api_version,
    )
    breaker = CircuitBreaker(
        failure_threshold=cfg.circuit_breaker.failure_threshold,
        open_seconds=cfg.circuit_breaker.open_seconds,
    )
    state = StateStore()  # noqa: F841 — reserved for future use

    speech_client, bot, voice_picker = setup_voiceover(cfg, spool_path, logger)

    last_call_at = 0.0
    last_heartbeat = 0.0
    last_gc = 0.0

    while True:
        now = time.time()

        # Heartbeat & janitor
        if now - last_heartbeat > HEARTBEAT_INTERVAL_SECONDS:
            heartbeat(spool_path, logger)
            last_heartbeat = now
        if now - last_gc > 60:
            gc_spool(spool_path, cfg, logger)
            last_gc = now

        # Process pending requests, respecting rate limit
        processed = 0
        for req_path in spool_mod.list_requests(spool_path):
            now = time.time()
            if now - last_call_at < cfg.rate_limit_seconds:
                break  # wait for rate-limit window
            request = spool_mod.safe_read_json(req_path)
            if request is None:
                logger.warning("dropping unreadable request: %s", req_path.name)
                spool_mod.safe_unlink(req_path)
                continue
            # TTL check — drop if too old
            issued = float(request.get("issued_at_unix") or 0)
            ttl = float(request.get("ttl_seconds") or cfg.request_ttl_seconds)
            if issued and (now - issued) > ttl:
                logger.info("dropping expired request_id=%s age=%.1fs",
                            request.get("request_id"), now - issued)
                spool_mod.safe_unlink(req_path)
                continue

            # Refresh heartbeat BEFORE the API call so the game-side
            # recheck doesn't see us as stale during a slow call.
            heartbeat(spool_path, logger)
            last_heartbeat = time.time()

            response = process_request(
                req_path, request,
                client=client, breaker=breaker, logger=logger,
                max_tokens=cfg.max_tokens,
                max_tokens_multi=cfg.max_tokens_multi_turn,
            )

            # And refresh again after the API call completes, before writing
            # the response, so the game-side check (which happens shortly
            # after) sees a fresh heartbeat.
            heartbeat(spool_path, logger)
            last_heartbeat = time.time()

            write_response(spool_path, response, logger)
            voiceover_response(response, speech_client=speech_client, bot=bot,
                               spool_path=spool_path, logger=logger,
                               voice_picker=voice_picker)
            spool_mod.safe_unlink(req_path)
            last_call_at = time.time()
            processed += 1
            if processed >= cfg.max_in_flight:
                break

        if processed == 0:
            time.sleep(cfg.spool_poll_interval_seconds)


def main(argv: Optional[list] = None) -> int:
    cfg = cfg_mod.load_config()
    spool_path = cfg_mod.spool_dir()
    logger = setup_logging(spool_path, cfg.log_level)
    try:
        return main_loop(cfg, spool_path, logger) or 0
    except KeyboardInterrupt:
        logger.info("shutdown via KeyboardInterrupt")
        return 0
    except Exception as exc:  # noqa: BLE001 — top-level catch
        logger.exception("daemon crashed: %s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
