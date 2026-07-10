"""Client for the local TTS server (XTTSv2 / Qwen3-TTS).

Mirrors the interface patterns of :mod:`elevenlabs_client` so the
:class:`TtsDispatcher` can treat it as a drop-in provider.

The local server is expected at ``base_url`` (default ``http://localhost:8080``)
and exposes ``POST /synthesize`` accepting ``{text, voice_id}`` returning WAV.

Connection failures (server not running) raise :class:`LocalTtsUnavailable`
which the dispatcher maps to an immediate circuit-trip + fallback —- no
wasted timeout.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Optional

import httpx


class LocalTtsError(Exception):
    """Base error for local TTS client."""
    pass


class LocalTtsUnavailable(LocalTtsError):
    """Server not reachable (connection refused, timeout, DNS failure)."""
    pass


class LocalTtsApiError(LocalTtsError):
    """Server returned a non-200 response."""
    pass


@dataclass
class LocalTtsResult:
    """Typed result from a successful local TTS synthesis."""
    audio_bytes: bytes
    voice_id: str
    model: str
    char_count: int
    latency_ms: int


class LocalTtsClient:
    """Stateless HTTP client for the local TTS server.

    Constructed once and reused for the life of the daemon.
    """

    def __init__(self, *, base_url: str = "http://localhost:8080", timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def synthesize(self, *, text: str, voice_id: str = "dowager") -> LocalTtsResult:
        """POST /synthesize and return WAV bytes.

        Raises:
            LocalTtsUnavailable: server unreachable or timed out
            LocalTtsApiError: server returned an error
        """
        url = f"{self.base_url}/synthesize"
        t0 = time.perf_counter()

        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.post(url, json={"text": text, "voice_id": voice_id})
        except (httpx.ConnectError, httpx.ConnectTimeout) as exc:
            raise LocalTtsUnavailable(
                f"Local TTS server unreachable at {self.base_url}: {exc}"
            ) from exc
        except httpx.TimeoutException as exc:
            raise LocalTtsUnavailable(f"Local TTS timeout: {exc}") from exc
        except httpx.HTTPError as exc:
            raise LocalTtsApiError(f"HTTP error: {exc}") from exc

        latency_ms = int((time.perf_counter() - t0) * 1000)

        if resp.status_code != 200:
            raise LocalTtsApiError(
                f"Local TTS {resp.status_code}: {resp.text[:200]}"
            )

        return LocalTtsResult(
            audio_bytes=resp.content,
            voice_id=resp.headers.get("X-Voice-Id", voice_id),
            model=resp.headers.get("X-Model", "unknown"),
            char_count=len(text),
            latency_ms=latency_ms,
        )

    def health(self) -> dict:
        """Check server readiness. Returns dict with status key."""
        try:
            with httpx.Client(timeout=5.0) as client:
                resp = client.get(f"{self.base_url}/health")
                resp.raise_for_status()
                return resp.json()
        except Exception as exc:
            return {"status": "unreachable", "error": str(exc)}
