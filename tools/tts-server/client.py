"""Client for the local TTS server.

Used by the chatter daemon's TtsDispatcher as the 'local' provider.
Mirrors the interface of elevenlabs_client.py.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import httpx


class LocalTtsError(Exception):
    """Base error for local TTS client."""
    pass


class LocalTtsUnavailable(LocalTtsError):
    """Server not reachable (connection refused, timeout)."""
    pass


class LocalTtsApiError(LocalTtsError):
    """Server returned an error response."""
    pass


@dataclass
class LocalTtsResult:
    audio_bytes: bytes
    voice_id: str
    model: str
    char_count: int
    latency_ms: int


def synthesize(
    text: str,
    voice_id: str = "dowager",
    base_url: str = "http://localhost:8080",
    timeout: float = 30.0,
) -> LocalTtsResult:
    """Synthesize text via the local TTS server.

    Returns WAV bytes (24 kHz mono 16-bit PCM) matching the format expected
    by the chatter daemon's audio pipeline.

    Raises:
        LocalTtsUnavailable: server not reachable
        LocalTtsApiError: server returned an error
    """
    url = f"{base_url.rstrip('/')}/synthesize"
    t0 = time.time()

    try:
        with httpx.Client(timeout=timeout) as client:
            resp = client.post(url, json={"text": text, "voice_id": voice_id})
    except (httpx.ConnectError, httpx.ConnectTimeout) as exc:
        raise LocalTtsUnavailable(f"Local TTS server unreachable at {base_url}: {exc}")
    except httpx.TimeoutException as exc:
        raise LocalTtsUnavailable(f"Local TTS server timeout: {exc}")
    except httpx.HTTPError as exc:
        raise LocalTtsApiError(f"HTTP error: {exc}")

    latency_ms = int((time.time() - t0) * 1000)

    if resp.status_code != 200:
        raise LocalTtsApiError(
            f"Local TTS returned {resp.status_code}: {resp.text[:200]}"
        )

    return LocalTtsResult(
        audio_bytes=resp.content,
        voice_id=resp.headers.get("X-Voice-Id", voice_id),
        model=resp.headers.get("X-Model", "unknown"),
        char_count=len(text),
        latency_ms=latency_ms,
    )


def health_check(base_url: str = "http://localhost:8080", timeout: float = 5.0) -> dict:
    """Check if the local TTS server is running and ready."""
    try:
        with httpx.Client(timeout=timeout) as client:
            resp = client.get(f"{base_url.rstrip('/')}/health")
            resp.raise_for_status()
            return resp.json()
    except Exception as exc:
        return {"status": "unreachable", "error": str(exc)}
