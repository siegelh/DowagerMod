"""Unit tests for tools.chatter.elevenlabs_client.

No network: every HTTP call is served by a fake `urllib` opener that
returns canned PCM bytes or raises canned HTTPError / URLError.
"""
from __future__ import annotations

import io
import urllib.error
import urllib.request

import pytest

from tools.chatter.elevenlabs_client import (
    ElevenLabsApiError,
    ElevenLabsAuthError,
    ElevenLabsClient,
    ElevenLabsQuotaError,
)


class _FakeResponse(io.BytesIO):
    """Mimics the minimal context-manager interface urlopen returns."""

    def __init__(self, body: bytes, status: int = 200):
        super().__init__(body)
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
        return False


class _FakeOpener:
    """Stand-in for urllib's OpenerDirector. Records each request."""

    def __init__(self, handler):
        # handler(req) -> bytes | raises HTTPError/URLError/etc.
        self.handler = handler
        self.requests = []

    def open(self, req, timeout=None):  # noqa: A003 - matches urllib signature
        self.requests.append((req, timeout))
        result = self.handler(req)
        if isinstance(result, Exception):
            raise result
        return _FakeResponse(result)


def _make_client(handler, **kwargs):
    defaults = dict(
        api_key="sk_test",
        endpoint="https://fake.elevenlabs.io",
        model_id="eleven_flash_v2_5",
        timeout_seconds=5.0,
    )
    defaults.update(kwargs)
    opener = _FakeOpener(handler)
    return ElevenLabsClient(opener=opener, **defaults), opener


def test_synthesize_wraps_raw_pcm_in_wav_header():
    # 240 samples of silence = 480 bytes of PCM
    pcm = b"\x00" * 480
    client, opener = _make_client(lambda req: pcm)
    out = client.synthesize(text="hello world", voice_id="voice_abc")

    assert out.voice == "voice_abc"
    assert out.char_count == len("hello world")
    assert out.latency_ms >= 0
    # RIFF header + 480 bytes payload
    assert out.audio_bytes[:4] == b"RIFF"
    assert out.audio_bytes[8:12] == b"WAVE"
    assert out.audio_bytes.endswith(pcm)
    assert len(out.audio_bytes) == 44 + 480
    # daily budget incremented
    assert client.budget.used_today() == len("hello world")


def test_synthesize_accepts_already_wrapped_wav():
    wav = b"RIFF\x00\x00\x00\x00WAVEfmt " + b"\x00" * 32
    client, _ = _make_client(lambda req: wav)
    out = client.synthesize(text="x", voice_id="v")
    assert out.audio_bytes == wav  # passthrough, no double-wrap


def test_synthesize_request_shape():
    client, opener = _make_client(lambda req: b"\x00\x00")
    client.synthesize(text="Hello.", voice_id="abc123")

    req, _ = opener.requests[0]
    assert req.full_url == (
        "https://fake.elevenlabs.io/v1/text-to-speech/abc123?output_format=pcm_24000"
    )
    assert req.get_method() == "POST"
    assert req.headers["Xi-api-key"] == "sk_test"
    assert req.headers["Content-type"].startswith("application/json")
    body = req.data
    assert b'"text": "Hello."' in body
    assert b'"model_id": "eleven_flash_v2_5"' in body


def test_http_401_raises_auth_error():
    err = urllib.error.HTTPError(
        url="x", code=401, msg="Unauthorized", hdrs=None,
        fp=io.BytesIO(b'{"detail":"bad key"}'),
    )
    client, _ = _make_client(lambda req: err)
    with pytest.raises(ElevenLabsAuthError):
        client.synthesize(text="hi", voice_id="v")


def test_http_403_raises_auth_error():
    err = urllib.error.HTTPError(
        url="x", code=403, msg="Forbidden", hdrs=None, fp=io.BytesIO(b""),
    )
    client, _ = _make_client(lambda req: err)
    with pytest.raises(ElevenLabsAuthError):
        client.synthesize(text="hi", voice_id="v")


def test_http_429_raises_quota_error():
    err = urllib.error.HTTPError(
        url="x", code=429, msg="Too Many", hdrs=None,
        fp=io.BytesIO(b'{"detail":"quota"}'),
    )
    client, _ = _make_client(lambda req: err)
    with pytest.raises(ElevenLabsQuotaError):
        client.synthesize(text="hi", voice_id="v")


def test_http_500_raises_api_error():
    err = urllib.error.HTTPError(
        url="x", code=502, msg="Bad Gateway", hdrs=None, fp=io.BytesIO(b""),
    )
    client, _ = _make_client(lambda req: err)
    with pytest.raises(ElevenLabsApiError):
        client.synthesize(text="hi", voice_id="v")


def test_network_error_raises_api_error():
    err = urllib.error.URLError("connection refused")
    client, _ = _make_client(lambda req: err)
    with pytest.raises(ElevenLabsApiError):
        client.synthesize(text="hi", voice_id="v")


def test_empty_body_raises_api_error():
    client, _ = _make_client(lambda req: b"")
    with pytest.raises(ElevenLabsApiError):
        client.synthesize(text="hi", voice_id="v")


def test_empty_text_raises_api_error():
    client, _ = _make_client(lambda req: b"\x00\x00")
    with pytest.raises(ElevenLabsApiError):
        client.synthesize(text="", voice_id="v")


def test_empty_voice_raises_api_error():
    client, _ = _make_client(lambda req: b"\x00\x00")
    with pytest.raises(ElevenLabsApiError):
        client.synthesize(text="hi", voice_id="")


def test_missing_api_key_raises_auth_error():
    with pytest.raises(ElevenLabsAuthError):
        ElevenLabsClient(api_key="")


def test_daily_cap_blocks_when_exhausted():
    client, _ = _make_client(lambda req: b"\x00" * 4, daily_char_cap=10)
    client.synthesize(text="hello", voice_id="v")  # 5 chars used
    client.synthesize(text="world", voice_id="v")  # 10 chars used (== cap)
    with pytest.raises(ElevenLabsQuotaError):
        client.synthesize(text="!", voice_id="v")  # would exceed cap


def test_zero_cap_means_unbounded():
    client, _ = _make_client(lambda req: b"\x00" * 4, daily_char_cap=0)
    # Should not raise even after many synth calls
    for _ in range(50):
        client.synthesize(text="hello world", voice_id="v")
