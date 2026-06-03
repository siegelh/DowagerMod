"""DowagerMod Chatter sidecar daemon.

Watches the spool directory for chatter requests, calls Azure Foundry,
writes responses back. Runs forever; safe to restart anytime.

Usage:
    python -m tools.chatter.chatter_daemon

Or via the helper script tools\\Start-Chatter.ps1.
"""
from __future__ import annotations

import logging
import logging.handlers
import os
import random
import re
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
from tools.chatter.chat_reply import handle_chat_reply
from tools.chatter.circuit import CircuitBreaker
from tools.chatter.conversations import ConversationStore
from tools.chatter.prompts import build_single_line_prompt, build_multi_turn_prompt
from tools.chatter.state import StateStore
from tools.chatter.tone import add_percent, prosody_for


REJOINDER_MIN_MS = 5000
REJOINDER_MAX_MS = 10000
SCHEMA_VERSION = 1
HEARTBEAT_INTERVAL_SECONDS = 5


# Matches the JSON `"line": "<text>"` fragment in a multi-turn payload,
# tolerating escaped quotes inside the line. Used by
# _salvage_multi_turn_lines as a last-ditch recovery when
# parse_multi_turn_lines raises (e.g. LLM hit max_tokens mid-string, or
# emitted a bare title element before the dicts).
_LINE_FIELD_RE = re.compile(r'"line"\s*:\s*"((?:\\.|[^"\\])*)"', re.DOTALL)


def _salvage_multi_turn_lines(raw: str) -> list:
    """Best-effort recovery of speakable text from a malformed multi-turn payload.

    The strict parse (parse_multi_turn_lines) fails on truncated output,
    bare-string array elements, or other LLM quirks. Rather than dumping
    the raw JSON-shaped text into the message scroll (which the player
    then hears the TTS voice literally read aloud), we yank any
    well-formed `"line": "<text>"` fragments out via regex.

    Returns a list of recovered line strings (possibly empty). The caller
    decides whether to use them or fall back to a stock canned line.
    """
    out = []
    try:
        for m in _LINE_FIELD_RE.finditer(raw or ""):
            # Decode the JSON-escaped content (\\n, \\", etc.).
            try:
                import json as _json
                decoded = _json.loads('"' + m.group(1) + '"')
            except Exception:
                decoded = m.group(1)
            decoded = (decoded or "").strip()
            if decoded:
                out.append(decoded)
    except Exception:
        return []
    return out


def setup_logging(spool_path: Path, level_name: str) -> logging.Logger:
    spool_path.mkdir(parents=True, exist_ok=True)
    log_path = spool_path / "daemon.log"
    # C9: rotate at 5 MB, keep 3 backups. Was unbounded FileHandler.
    handler = logging.handlers.RotatingFileHandler(
        str(log_path), maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    handler.setFormatter(logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    ))
    logger = logging.getLogger("chatter")
    logger.setLevel(getattr(logging, level_name.upper(), logging.INFO))
    # Idempotent — clear existing handlers first
    for h in list(logger.handlers):
        logger.removeHandler(h)
    logger.addHandler(handler)
    logger.propagate = False
    return logger


# C1: structured kv logging helpers. Format mirrors game-side _log_kv so
# rid=abc12345 grep works across both daemon.log and chatter.log.
_LOG_LEVELS_NUM = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARN": logging.WARNING,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
}


def _kv_escape(v) -> str:
    """Format a value for key=val. Wrap in quotes if it contains space/=/quote."""
    if v is None:
        return "none"
    if isinstance(v, bool):
        return "1" if v else "0"
    if isinstance(v, (int, float)):
        return str(v)
    try:
        s = str(v)
    except Exception:
        try:
            s = repr(v)
        except Exception:
            return "?"
    if any(ch in s for ch in (" ", "\t", "\n", "\r", '"', "=")):
        s = s.replace("\\", "\\\\").replace('"', '\\"')
        s = s.replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t")
        return '"' + s + '"'
    return s


def log_kv(logger: logging.Logger, level: str, phase: str,
           rid: Optional[str] = None, msg: Optional[str] = None,
           **fields) -> None:
    """Structured kv log line.

    Format: [phase] rid=... key=val ... -- human msg

    The logger's formatter prepends '[ts] [LEVEL]', so the final line is:
      [2026-05-11 14:00:00] [INFO] [emit] rid=abc12345 trigger=CHAT_REPLY -- ok

    Never raises. Field keys are sorted for grep stability.
    """
    try:
        parts = ["[" + str(phase or "info") + "]"]
        if rid is not None:
            rs = str(rid)
            if len(rs) > 8:
                rs = rs[:8]
            parts.append("rid=" + rs)
        if fields:
            for k in sorted(fields.keys()):
                parts.append(str(k) + "=" + _kv_escape(fields[k]))
        body = " ".join(parts)
        if msg:
            body = body + " -- " + str(msg)
        lvl_num = _LOG_LEVELS_NUM.get((level or "INFO").upper(), logging.INFO)
        logger.log(lvl_num, body)
    except Exception:
        try:
            logger.info("[error] log_kv failed phase=%s", phase)
        except Exception:
            pass


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


_STAGE_DIRECTION_RE = re.compile(r"\*[^*\n]{1,80}\*")


def _scrub_stage_directions(text: str) -> str:
    """Remove *stage directions* like '*laughs*' or '*scoffs*' which the
    voice synthesizer would speak literally and ruin the audio. Also
    collapses any leftover double-spaces.
    """
    cleaned = _STAGE_DIRECTION_RE.sub("", text or "")
    return re.sub(r"\s{2,}", " ", cleaned).strip()


def render_single_line(request: dict, text: str) -> list:
    speaker = request.get("speaker") or {}
    return [{
        "speaker_player_id": int(speaker.get("player_id", -1)),
        "speaker_name": speaker.get("leader_name", ""),
        "text": _scrub_stage_directions(text),
        "delay_ms": 0,
    }]


def render_multi_turn(request: dict, parsed: list) -> list:
    """Map parsed [{speaker:'Victoria', line:'...', [line_native:'...']}] to spool line entries.

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
        entry = {
            "speaker_player_id": spk_id,
            "speaker_name": spk_name,
            "text": _scrub_stage_directions(item["line"]),
            "delay_ms": delay_ms,
        }
        # Carry through native translation if present
        ln = (item.get("line_native") or "").strip()
        if ln:
            entry["text_native"] = _scrub_stage_directions(ln)
        out.append(entry)
    return out


def process_request(req_path: Path, request: dict, *, client: AzureClient, breaker: CircuitBreaker,
                    logger: logging.Logger, max_tokens: int, max_tokens_multi: int,
                    native_mode: bool = False, voice_picker=None,
                    conversations: ConversationStore = None,
                    chat_reply_max_tokens: int = 120) -> dict:
    """Run one request through the API. Always returns a response dict.

    When native_mode is True, asks the LLM for both English and native-tongue
    versions of each line. The voice_picker is needed to know which native
    language each speaker uses (skipped if leader has no configured 'lang').

    CHAT_REPLY trigger is dispatched separately to handle_chat_reply, which
    builds a multi-turn messages list from the conversation history and asks
    the LLM for a tone-tagged response.
    """
    rid = request.get("request_id")
    trig = request.get("trigger") or "?"
    if not breaker.can_call():
        log_kv(logger, "WARN", "llm", rid=rid, trigger=trig,
               msg="circuit OPEN, dropping")
        return make_response(request=request, ok=False, lines=[], error="circuit_open")

    # Live chat reply: route through the dedicated multi-turn handler.
    if request.get("trigger") == "CHAT_REPLY":
        if conversations is None:
            log_kv(logger, "WARN", "llm", rid=rid, trigger=trig,
                   msg="CHAT_REPLY but no conversation store; dropping")
            return make_response(request=request, ok=False, lines=[], error="no_chat_store")
        try:
            t_start = time.time()
            resp, line, tone = handle_chat_reply(
                request=request, store=conversations, client=client,
                max_tokens=chat_reply_max_tokens, logger=logger,
            )
            latency_ms = int((time.time() - t_start) * 1000)
        except Exception as exc:  # noqa: BLE001
            breaker.record_failure()
            logger.exception("chat_reply unexpected: %s", exc)
            return make_response(request=request, ok=False, lines=[], error="unexpected")
        if resp.get("ok"):
            breaker.record_success()
            log_kv(logger, "INFO", "llm", rid=rid, trigger=trig,
                   tone=str(tone), latency_ms=latency_ms,
                   line=line[:80] if line else "",
                   msg="chat_reply ok")
        else:
            err = resp.get("error") or ""
            log_kv(logger, "WARN", "llm", rid=rid, trigger=trig,
                   reason=err, latency_ms=latency_ms, msg="chat_reply not ok")
            if err == "auth_failure":
                breaker.trip_immediately()
            elif err in ("api_failure", "unexpected"):
                breaker.record_failure()
            # empty_user_message / empty_reply / no_chat_store: don't ding circuit
        return resp

    multi = bool(request.get("multi_turn"))
    # Resolve per-speaker native lang hints if native_mode is on
    speaker_native_lang = ""
    target_native_lang = ""
    if native_mode and voice_picker is not None:
        try:
            sp = (request.get("speaker") or {}).get("leader_name", "")
            if sp:
                speaker_native_lang = voice_picker.pick_spec(sp).lang
            tg = (request.get("target") or {}).get("leader_name", "")
            if tg:
                target_native_lang = voice_picker.pick_spec(tg).lang
        except Exception as exc:  # noqa: BLE001
            logger.warning("native_mode: failed to resolve native langs: %s", exc)
    try:
        t_start = time.time()
        log_kv(logger, "INFO", "llm", rid=rid, trigger=trig, multi=multi,
               native=native_mode, msg="llm_start")
        if multi:
            sys_msg, user_msg = build_multi_turn_prompt(
                request, native_mode=native_mode,
                speaker_native_lang=speaker_native_lang,
                target_native_lang=target_native_lang,
            )
            api_result = client.call_responses(sys_msg, user_msg, max_tokens=max_tokens_multi)
        else:
            sys_msg, user_msg = build_single_line_prompt(
                request, native_mode=native_mode,
                speaker_native_lang=speaker_native_lang,
            )
            api_result = client.call_responses(sys_msg, user_msg, max_tokens=max_tokens)
        latency_ms = int((time.time() - t_start) * 1000)
    except AuthError as exc:
        breaker.trip_immediately()
        log_kv(logger, "ERROR", "llm", rid=rid, trigger=trig,
               msg="auth failure (circuit forced OPEN): " + str(exc))
        return make_response(request=request, ok=False, lines=[], error="auth_failure")
    except ApiError as exc:
        breaker.record_failure()
        log_kv(logger, "WARN", "llm", rid=rid, trigger=trig,
               msg="api failure: " + str(exc))
        return make_response(request=request, ok=False, lines=[], error="api_failure")
    except Exception as exc:  # noqa: BLE001 — never raise out of process_request
        breaker.record_failure()
        logger.exception("unexpected failure building/calling: %s", exc)
        return make_response(request=request, ok=False, lines=[], error="unexpected")

    breaker.record_success()
    text = api_result.text
    log_kv(logger, "INFO", "llm", rid=rid, trigger=trig,
           latency_ms=latency_ms, multi=multi,
           input_tokens=getattr(api_result, "input_tokens", 0),
           output_tokens=getattr(api_result, "output_tokens", 0),
           msg="llm_end")

    if looks_like_refusal(text):
        log_kv(logger, "WARN", "llm", rid=rid, trigger=trig,
               msg="model refused; substituting fallback")
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
            logger.warning("multi-turn parse failed: %s; attempting salvage", exc)
            salvaged = _salvage_multi_turn_lines(text)
            speaker = request.get("speaker") or {}
            target = request.get("target") or {}
            if salvaged:
                logger.info("multi-turn salvage: recovered %d line(s) via regex",
                            len(salvaged))
                lines = render_single_line(request, salvaged[0])
            else:
                logger.info("multi-turn salvage failed; using stock fallback line")
                from tools.chatter.azure_client import fallback_line
                is_broadcast = (request.get("mode") == "broadcast")
                fb = fallback_line(
                    speaker_name=speaker.get("leader_name", ""),
                    target_name=target.get("leader_name", ""),
                    broadcast=is_broadcast,
                )
                lines = render_single_line(request, fb)
        else:
            lines = render_multi_turn(request, parsed)
    else:
        # In native mode, single-line is also a JSON object
        if native_mode and speaker_native_lang:
            from tools.chatter.azure_client import parse_single_line_native
            parsed = parse_single_line_native(text)
            lines = render_single_line(request, parsed.get("line", text))
            ln = parsed.get("line_native", "")
            if ln and lines:
                lines[0]["text_native"] = _scrub_stage_directions(ln)
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
        log_kv(logger, "INFO", "write",
               rid=(response.get("request_id") or ""),
               file=name,
               ok=bool(response.get("ok")),
               lines=len(response.get("lines") or []),
               error=(response.get("error") or ""),
               msg="wrote response")
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
        # Wire the "speak whatever a user types at me" handler.
        # Triggered when a user @mentions DowagerBot OR DMs her.
        _install_user_speak_handler(bot, speech_client, voice_picker, spool_path, logger)
        bot.start()
        logger.info(
            "voiceover: Discord bot started guild=%s channel=%s",
            cfg.voiceover.discord_guild_id, cfg.voiceover.discord_voice_channel_id,
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("voiceover: Discord bot init failed: %s", exc)
        return speech_client, None, voice_picker

    return speech_client, bot, voice_picker


def _install_user_speak_handler(bot, speech_client, voice_picker, spool_path: Path, logger: logging.Logger):
    """Register an on_message handler so users can have DowagerBot speak
    arbitrary lines in a random leader voice by @mentioning her (or DM'ing).

    - Per-user cooldown to throttle abuse.
    - Character cap to protect the daily TTS budget.
    - Heavy work runs in a worker thread so the bot's asyncio loop is free.
    """
    import threading as _t

    MAX_CHARS = 240
    PER_USER_COOLDOWN_SEC = 4.0
    audio_dir = spool_path / "audio"
    try:
        audio_dir.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass

    last_spoke = {}  # author_id -> monotonic timestamp
    lock = _t.Lock()

    def _worker(text: str, author_name: str):
        try:
            # Hardcoded thick-accent voice: Hindi voice on English text.
            voice = "en-IN-PrabhatNeural"
            rate = ""
            pitch = ""
            logger.info(
                "user-speak: author=%s chars=%d voice=%s rate=%r pitch=%r",
                author_name, len(text), voice, rate, pitch,
            )
            result = speech_client.synthesize(text=text, voice=voice, rate=rate, pitch=pitch)
            ts = int(time.time() * 1000)
            wav = audio_dir / ("user_speak_%d.wav" % ts)
            wav.write_bytes(result.audio_bytes)
            bot.enqueue_audio(wav)
        except Exception as exc:  # noqa: BLE001
            logger.warning("user-speak: failed to speak for %s: %s", author_name, exc)

    def handler(text: str, author_name: str, author_id: int, is_dm: bool):
        text = (text or "").strip()
        if not text:
            return
        if len(text) > MAX_CHARS:
            text = text[:MAX_CHARS]
        now = time.monotonic()
        with lock:
            last = last_spoke.get(author_id, 0.0)
            if now - last < PER_USER_COOLDOWN_SEC:
                logger.info("user-speak: cooldown skip author=%s", author_name)
                return
            last_spoke[author_id] = now
        t = _t.Thread(
            target=_worker, args=(text, author_name),
            name="UserSpeak", daemon=True,
        )
        t.start()

    bot.set_message_handler(handler)
    logger.info("voiceover: user-speak handler registered (mention or DM the bot)")


def voiceover_response(response: dict, *, speech_client, bot, spool_path: Path, logger: logging.Logger,
                       voice_picker=None, cfg=None) -> None:
    """If voiceover is wired up, synthesize each response line and enqueue
    it to the Discord bot for playback. Failures log + continue (text
    chatter is unaffected).

    If voice_picker is provided, each line's voice is chosen based on the
    speaker's leader name (per-leader voice mapping). Otherwise the speech
    client's default voice is used for every line.

    cfg is optional. When provided and cfg.voiceover.speech_rate is set,
    that value is used as the default <prosody rate=...> for any leader
    whose voice_picker spec doesn't override rate.
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
    last_synth_at = 0.0
    for idx, ln in enumerate(lines):
        text = (ln.get("text") or "").strip()
        text_native = (ln.get("text_native") or "").strip()
        if not text and not text_native:
            continue
        speaker_name = (ln.get("speaker_name") or "").strip()
        chosen_voice = None
        rate = ""
        pitch = ""
        locale = ""
        # Use native text when available and a locale is configured for speaker
        synth_text = text_native if text_native else text
        if voice_picker is not None and speaker_name:
            try:
                spec = voice_picker.pick_spec(speaker_name)
                # When speaking native and a voice_native is defined, use it.
                # Otherwise (English mode OR no override) use the primary voice.
                if text_native and spec.voice_native:
                    chosen_voice = spec.voice_native
                else:
                    chosen_voice = spec.voice
                rate = spec.rate
                pitch = spec.pitch
                if text_native:
                    locale = spec.derived_locale()
            except Exception as exc:  # noqa: BLE001
                logger.warning("voiceover: voice pick failed for %r: %s", speaker_name, exc)
                chosen_voice = None
        # Apply global speech_rate fallback when the per-leader spec doesn't
        # override it. Per-leader overrides win; the global default just
        # ensures every line is snappier-than-neutral by default.
        if not rate and cfg is not None:
            rate = getattr(cfg.voiceover, "speech_rate", "") or ""
        # CHAT_REPLY tone layering: each line may carry a "tone" key
        # (angry / amused / haughty / pleased / cold / menacing / wistful /
        # theatrical). Tone offsets are ADDITIVE on top of the leader's base
        # rate/pitch -- so an angry Catherine speeds up by +12% from her
        # neutral, not from absolute zero.
        tone = (ln.get("tone") or "").strip().lower()
        if tone:
            pitch_off, rate_off = prosody_for(tone)
            if rate_off:
                rate = add_percent(rate, rate_off)
            if pitch_off:
                pitch = add_percent(pitch, pitch_off)
        elapsed = time.time() - last_synth_at
        if elapsed < 0.5 and last_synth_at > 0:
            time.sleep(0.5 - elapsed)
        try:
            result = speech_client.synthesize(
                synth_text, voice=chosen_voice, rate=rate, pitch=pitch, locale=locale,
            )
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
        last_synth_at = time.time()
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
    conversations = ConversationStore(
        history_seconds=cfg.chat_history_seconds,
        max_turns=cfg.chat_max_history_turns,
    )

    speech_client, bot, voice_picker = setup_voiceover(cfg, spool_path, logger)

    last_call_at = 0.0
    last_heartbeat = 0.0
    last_gc = 0.0
    last_struct_hb = 0.0
    daemon_started_at = time.time()
    processed_count = 0

    while True:
        now = time.time()

        # Heartbeat & janitor
        if now - last_heartbeat > HEARTBEAT_INTERVAL_SECONDS:
            heartbeat(spool_path, logger)
            last_heartbeat = now
        # C8: structured heartbeat once a minute for diagnostics.
        if now - last_struct_hb > 60:
            try:
                pending = 0
                try:
                    pending = len(list(spool_mod.list_requests(spool_path)))
                except Exception:
                    pass
                log_kv(logger, "INFO", "heartbeat",
                       uptime_s=int(now - daemon_started_at),
                       pending=pending,
                       processed_total=processed_count,
                       circuit_open=(not breaker.can_call()),
                       msg="alive")
            except Exception:
                pass
            last_struct_hb = now
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
            rid = request.get("request_id") or ""
            trig = request.get("trigger") or "?"
            # TTL check -- drop if too old.
            # CRITICAL: do NOT trust request["issued_at_unix"] here. Civ4
            # BTS Py2.4's time.time() is quantized to 128-second buckets, so
            # the client clock can be up to ~64s off real wall time per
            # request. We use os.path.getmtime() of the request file as the
            # authoritative emit time (same OS, accurate clock, no
            # quantization). See plan B1.
            ttl = float(request.get("ttl_seconds") or cfg.request_ttl_seconds)
            try:
                mtime = req_path.stat().st_mtime
            except Exception:
                mtime = 0.0
            age = (now - mtime) if mtime else 0.0
            if mtime and age > ttl:
                client_clock = float(request.get("issued_at_unix") or 0)
                log_kv(logger, "WARN", "drop", rid=rid, trigger=trig,
                       age_s=("%.1f" % age),
                       ttl_s=("%.0f" % ttl),
                       client_clock_skew_s=("%+.1f" % ((client_clock - mtime) if client_clock else 0.0)),
                       msg="dropping expired request")
                spool_mod.safe_unlink(req_path)
                continue

            log_kv(logger, "INFO", "pickup", rid=rid, trigger=trig,
                   age_s=("%.1f" % age), file=req_path.name,
                   msg="picked up request")

            # Refresh heartbeat BEFORE the API call so the game-side
            # recheck doesn't see us as stale during a slow call.
            heartbeat(spool_path, logger)
            last_heartbeat = time.time()

            response = process_request(
                req_path, request,
                client=client, breaker=breaker, logger=logger,
                max_tokens=cfg.max_tokens,
                max_tokens_multi=cfg.max_tokens_multi_turn,
                native_mode=cfg.voiceover.native_tongue_mode,
                voice_picker=voice_picker,
                conversations=conversations,
                chat_reply_max_tokens=cfg.chat_reply_max_tokens,
            )

            # And refresh again after the API call completes, before writing
            # the response, so the game-side check (which happens shortly
            # after) sees a fresh heartbeat.
            heartbeat(spool_path, logger)
            last_heartbeat = time.time()

            write_response(spool_path, response, logger)
            voiceover_response(response, speech_client=speech_client, bot=bot,
                               spool_path=spool_path, logger=logger,
                               voice_picker=voice_picker, cfg=cfg)
            spool_mod.safe_unlink(req_path)
            last_call_at = time.time()
            processed += 1
            processed_count += 1
            if processed >= cfg.max_in_flight:
                break

        if processed == 0:
            time.sleep(cfg.spool_poll_interval_seconds)


def main(argv: Optional[list] = None) -> int:
    cfg = cfg_mod.load_config()
    spool_path = cfg_mod.spool_dir()
    logger = setup_logging(spool_path, cfg.log_level)
    # Provenance footer: makes stale-vs-fresh restarts unambiguous in daemon.log.
    try:
        cfg_path = cfg_mod.config_path()
    except Exception:  # noqa: BLE001
        cfg_path = "?"
    logger.info(
        "daemon boot: schema=%d config=%s spool=%s log_level=%s",
        SCHEMA_VERSION, cfg_path, spool_path, cfg.log_level,
    )
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
