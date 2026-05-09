"""Thin wrapper around Azure Speech REST API for text-to-speech.

Uses the standard `Microsoft.CognitiveServices.Speech.cognitiveservices.v1`
REST endpoint to synthesize WAV audio. No SDK dependency — keeps the
sidecar's dependency footprint small.

Includes a daily character budget cap so a runaway loop can't accidentally
rack up Azure spend. Caller passes the cap from VoiceoverConfig.
"""
from __future__ import annotations

import os
import time
import datetime as dt
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


class SpeechAuthError(Exception):
    """Speech API key is wrong / expired."""


class SpeechApiError(Exception):
    """Any other Speech API failure (timeout, 5xx, network)."""


class SpeechBudgetExhausted(Exception):
    """Daily character cap reached; no more synthesis until next UTC day."""


@dataclass
class SpeechResult:
    audio_bytes: bytes
    voice: str
    char_count: int
    latency_ms: int


class _DailyBudget:
    """Tracks character usage per UTC day. Resets at midnight UTC."""

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
        return max(0, self.cap - self._used)

    def consume(self, chars: int) -> None:
        self._maybe_roll()
        self._used += int(chars)

    def used_today(self) -> int:
        self._maybe_roll()
        return self._used


class AzureSpeechClient:
    """Synchronous wrapper around the Azure Speech REST TTS endpoint.

    The endpoint must be the regional Cognitive Services hostname, e.g.
    ``https://<region>.api.cognitive.microsoft.com``. We append the
    required path internally. If a user pastes the full URL with
    ``/cognitiveservices/v1`` already included, we strip it to canonicalize.
    """

    DEFAULT_OUTPUT_FORMAT = "riff-24khz-16bit-mono-pcm"

    def __init__(
        self,
        endpoint: str,
        key: str,
        *,
        default_voice: str = "en-US-AriaNeural",
        request_timeout_seconds: float = 8.0,
        daily_char_cap: int = 100000,
    ):
        self.endpoint = self._canonicalize_endpoint(endpoint)
        self.key = key
        self.default_voice = default_voice
        self.request_timeout = request_timeout_seconds
        self.budget = _DailyBudget(daily_char_cap)

    @staticmethod
    def _canonicalize_endpoint(endpoint: str) -> str:
        ep = (endpoint or "").rstrip("/")
        if not ep:
            return ep
        # Strip any user-pasted suffix; we'll add the canonical path on each call
        for suffix in (
            "/cognitiveservices/v1",
            "/sts/v1.0/issueToken",
        ):
            if ep.endswith(suffix):
                ep = ep[: -len(suffix)].rstrip("/")
        return ep

    def synthesize(
        self,
        text: str,
        *,
        voice: Optional[str] = None,
        output_format: Optional[str] = None,
    ) -> SpeechResult:
        """Synthesize text to WAV bytes. Raises on auth/api failure or budget exhaustion."""
        if not text or not text.strip():
            raise SpeechApiError("empty text")
        char_count = len(text)
        if self.budget.cap > 0 and self.budget.remaining() < char_count:
            raise SpeechBudgetExhausted(
                f"daily TTS char cap exhausted: used {self.budget.used_today()}/{self.budget.cap}, requested {char_count}"
            )

        # Lazy import — only needed when synthesis is actually called
        import urllib.request
        import urllib.error

        v = voice or self.default_voice
        fmt = output_format or self.DEFAULT_OUTPUT_FORMAT
        url = f"{self.endpoint}/cognitiveservices/v1"
        headers = {
            "Ocp-Apim-Subscription-Key": self.key,
            "Content-Type": "application/ssml+xml",
            "X-Microsoft-OutputFormat": fmt,
            "User-Agent": "DowagerMod-Chatter",
        }
        # SSML lang is ALWAYS en-US because chatter is always written in English.
        # The voice itself supplies the accent — Multilingual voices handle this
        # gracefully (e.g. it-IT-MarcelloMultilingualNeural reads English with an
        # Italian accent). For non-Multilingual locale voices, this still works
        # but produces a heavier, funnier accent. The voice's source locale is
        # encoded in the voice name, not in xml:lang.
        ssml = (
            f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" '
            f'xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="en-US">'
            f'<voice name="{v}">'
            f'<lang xml:lang="en-US">{_xml_escape(text)}</lang>'
            f'</voice>'
            f'</speak>'
        )

        t0 = time.perf_counter()
        try:
            req = urllib.request.Request(url, data=ssml.encode("utf-8"), headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=self.request_timeout) as resp:
                audio_bytes = resp.read()
        except urllib.error.HTTPError as exc:
            elapsed_ms = int((time.perf_counter() - t0) * 1000)
            body = ""
            try:
                body = exc.read().decode("utf-8", errors="replace")[:200]
            except Exception:
                pass
            if exc.code in (401, 403):
                raise SpeechAuthError(
                    f"Speech auth failure ({exc.code}) after {elapsed_ms}ms: {body}"
                ) from exc
            raise SpeechApiError(
                f"Speech HTTP {exc.code} after {elapsed_ms}ms: {body}"
            ) from exc
        except Exception as exc:  # noqa: BLE001
            elapsed_ms = int((time.perf_counter() - t0) * 1000)
            raise SpeechApiError(f"Speech failure after {elapsed_ms}ms: {exc}") from exc

        elapsed_ms = int((time.perf_counter() - t0) * 1000)
        self.budget.consume(char_count)
        return SpeechResult(audio_bytes=audio_bytes, voice=v, char_count=char_count, latency_ms=elapsed_ms)


def _xml_escape(s: str) -> str:
    """Minimal XML escaping for SSML text content."""
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )
