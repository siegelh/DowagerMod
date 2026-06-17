"""Thin wrapper around the ElevenLabs REST API for text-to-speech.

Used by :mod:`tools.chatter.tts_dispatcher` as an OPTIONAL per-leader
override in front of the existing Azure Speech path. Any failure here
(auth, quota, network, timeout, 5xx) is caught by the dispatcher and
silently falls back to Azure -- this module does not try to be clever
about recovery; it just raises typed exceptions.

Error class hierarchy intentionally mirrors :mod:`azure_speech_client`
so the dispatcher can use a unified `except` ladder:

  * :class:`ElevenLabsAuthError`   -> 401 / 403
  * :class:`ElevenLabsQuotaError`  -> 429, or daily char-cap exhausted
  * :class:`ElevenLabsApiError`    -> anything else (timeout, 5xx, network)

The HTTP call requests raw PCM at 24 kHz so the bytes line up with
Azure's default ``riff-24khz-16bit-mono-pcm`` output, which means the
RIFF/WAV wrapper added here is wire-compatible with the existing
``audio_postprocess`` pipeline and Discord voice playback.

No external dependency (no `requests`, no `httpx`) -- stdlib `urllib`
keeps the sidecar dependency footprint identical to before.
"""
from __future__ import annotations

import datetime as dt
import json
import logging
import struct
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Optional


class ElevenLabsAuthError(Exception):
    """ElevenLabs API key is missing, wrong, or revoked (401 / 403)."""


class ElevenLabsQuotaError(Exception):
    """ElevenLabs quota exhausted (429), or our local daily char cap hit."""


class ElevenLabsApiError(Exception):
    """Any other ElevenLabs failure (timeout, 5xx, network, malformed body)."""


@dataclass
class ElevenLabsResult:
    """Mirrors :class:`azure_speech_client.SpeechResult` for dispatcher symmetry."""
    audio_bytes: bytes        # ALWAYS a RIFF/WAV blob (PCM auto-wrapped here)
    voice: str                # ElevenLabs voice ID
    char_count: int           # chars billed against ElevenLabs (== len(text))
    latency_ms: int           # wall-clock for the HTTP round-trip


class _DailyBudget:
    """Tracks character usage per UTC day. Resets at midnight UTC.

    Identical contract to :class:`azure_speech_client._DailyBudget` so the
    behaviour is symmetric across providers. cap == 0 means "no cap".
    """

    def __init__(self, cap: int):
        self.cap = max(0, int(cap))
        self._date = dt.date.min
        self._used = 0

    def _maybe_roll(self) -> None:
        today = dt.datetime.utcnow().date()
        if today != self._date:
            self._date = today
            self._used = 0

    def remaining(self) -> int:
        self._maybe_roll()
        if self.cap == 0:
            return 1 << 31  # effectively unbounded
        return max(0, self.cap - self._used)

    def consume(self, chars: int) -> None:
        self._maybe_roll()
        self._used += int(chars)

    def used_today(self) -> int:
        self._maybe_roll()
        return self._used


_SAMPLE_RATE = 24000
_BITS_PER_SAMPLE = 16
_CHANNELS = 1


def _wrap_pcm_as_wav(pcm: bytes) -> bytes:
    """Wrap raw 16-bit mono PCM at 24 kHz in a minimal RIFF/WAV header."""
    byte_rate = _SAMPLE_RATE * _CHANNELS * (_BITS_PER_SAMPLE // 8)
    block_align = _CHANNELS * (_BITS_PER_SAMPLE // 8)
    data_size = len(pcm)
    riff_size = 36 + data_size
    out = b"RIFF"
    out += struct.pack("<I", riff_size)
    out += b"WAVE"
    out += b"fmt "
    out += struct.pack(
        "<IHHIIHH",
        16, 1, _CHANNELS, _SAMPLE_RATE,
        byte_rate, block_align, _BITS_PER_SAMPLE,
    )
    out += b"data"
    out += struct.pack("<I", data_size)
    return out + pcm


class ElevenLabsClient:
    """Synchronous wrapper around the ElevenLabs TTS REST endpoint.

    Construct with config drawn from :class:`config.VoiceoverConfig`. One
    instance is shared by the dispatcher for the daemon's lifetime; the
    `_DailyBudget` state lives on the instance so all leaders share the
    same daily cap (matching how :class:`AzureSpeechClient` works).
    """

    def __init__(
        self,
        *,
        api_key: str,
        endpoint: str = "https://api.elevenlabs.io",
        model_id: str = "eleven_flash_v2_5",
        timeout_seconds: float = 20.0,
        daily_char_cap: int = 0,
        logger: Optional[logging.Logger] = None,
        opener: Optional[urllib.request.OpenerDirector] = None,
    ):
        if not api_key:
            raise ElevenLabsAuthError("ElevenLabs API key not configured")
        self.api_key = api_key
        self.endpoint = endpoint.rstrip("/")
        self.model_id = model_id
        self.timeout_seconds = float(timeout_seconds)
        self.budget = _DailyBudget(daily_char_cap)
        self.logger = logger or logging.getLogger("dowager.chatter.tts.elevenlabs")
        # `opener` is the seam tests use to inject a mocked HTTP layer
        # without monkey-patching urllib globals.
        self._opener = opener

    # ----- public API -----

    def synthesize(self, *, text: str, voice_id: str, language_code: str = "") -> ElevenLabsResult:
        """Return RIFF/WAV bytes for ``text`` spoken by ``voice_id``.

        Raises :class:`ElevenLabsAuthError`, :class:`ElevenLabsQuotaError`,
        or :class:`ElevenLabsApiError`. Never returns partial audio.
        """
        if not voice_id:
            raise ElevenLabsApiError("ElevenLabs voice_id is empty")
        chars = len(text or "")
        if chars == 0:
            raise ElevenLabsApiError("ElevenLabs request has empty text")
        if self.budget.cap and self.budget.remaining() < chars:
            raise ElevenLabsQuotaError(
                "ElevenLabs daily char cap reached: used=%d cap=%d need=%d"
                % (self.budget.used_today(), self.budget.cap, chars)
            )

        url = (
            self.endpoint
            + "/v1/text-to-speech/"
            + voice_id
            + "?output_format=pcm_24000"
        )
        payload_dict = {"text": text, "model_id": self.model_id}
        if language_code:
            payload_dict["language_code"] = language_code
        payload = json.dumps(payload_dict, ensure_ascii=False).encode("utf-8")
        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "audio/wav",
            "User-Agent": "DowagerMod-Chatter/0.1",
        }
        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")

        t0 = time.perf_counter()
        try:
            if self._opener is not None:
                resp = self._opener.open(req, timeout=self.timeout_seconds)
            else:
                resp = urllib.request.urlopen(req, timeout=self.timeout_seconds)
            with resp:
                raw = resp.read()
        except urllib.error.HTTPError as exc:
            elapsed = int((time.perf_counter() - t0) * 1000)
            body_snippet = ""
            try:
                body_snippet = exc.read().decode("utf-8", errors="replace")[:200]
            except Exception:  # noqa: BLE001
                pass
            self._reraise_http_error(exc.code, body_snippet, elapsed)
        except urllib.error.URLError as exc:
            elapsed = int((time.perf_counter() - t0) * 1000)
            raise ElevenLabsApiError(
                "ElevenLabs network error after %dms: %s" % (elapsed, exc.reason)
            ) from exc
        except Exception as exc:  # noqa: BLE001 - timeouts come up as socket.timeout
            elapsed = int((time.perf_counter() - t0) * 1000)
            raise ElevenLabsApiError(
                "ElevenLabs request failed after %dms: %s" % (elapsed, exc)
            ) from exc

        elapsed = int((time.perf_counter() - t0) * 1000)
        if not raw:
            raise ElevenLabsApiError(
                "ElevenLabs returned empty body after %dms" % elapsed
            )

        # Defensive: if ElevenLabs ever switches to returning WAV directly,
        # accept it verbatim instead of double-wrapping. Today they return
        # raw PCM when output_format=pcm_24000.
        if raw[:4] == b"RIFF":
            wav = raw
        else:
            wav = _wrap_pcm_as_wav(raw)

        self.budget.consume(chars)
        self.logger.info(
            "tts: ok provider=elevenlabs voice=%s chars=%d latency=%dms bytes=%d",
            voice_id, chars, elapsed, len(wav),
        )
        return ElevenLabsResult(
            audio_bytes=wav,
            voice=voice_id,
            char_count=chars,
            latency_ms=elapsed,
        )

    # ----- internals -----

    def _reraise_http_error(self, code: int, body: str, elapsed_ms: int) -> None:
        msg = "ElevenLabs HTTP %d after %dms" % (code, elapsed_ms)
        if body:
            msg += ": " + body
        if code in (401, 403):
            raise ElevenLabsAuthError(msg)
        if code == 429:
            raise ElevenLabsQuotaError(msg)
        raise ElevenLabsApiError(msg)
