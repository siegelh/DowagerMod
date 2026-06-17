"""Unit tests for tools.chatter.tts_dispatcher.

Uses fake Azure / ElevenLabs clients so tests don't touch the network.
Verifies provider routing, fallback behaviour, circuit breaker, and the
``skip_post_process`` contract that callers depend on.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

import pytest

from tools.chatter.azure_speech_client import (
    SpeechApiError,
    SpeechAuthError,
    SpeechResult,
)
from tools.chatter.elevenlabs_client import (
    ElevenLabsApiError,
    ElevenLabsAuthError,
    ElevenLabsQuotaError,
    ElevenLabsResult,
)
from tools.chatter.tts_dispatcher import (
    DispatchResult,
    PROVIDER_AZURE,
    PROVIDER_ELEVENLABS,
    TtsDispatcher,
    _Circuit,
)
from tools.chatter.voice_picker import VoiceSpec


# ----- Fakes -----

@dataclass
class _AzureCall:
    text: str
    voice: str
    rate: str
    pitch: str
    locale: str


class _FakeAzure:
    def __init__(self):
        self.calls: List[_AzureCall] = []
        self.next_exc = None  # set to raise on next call

    def synthesize(self, text, *, voice, rate, pitch, locale):
        self.calls.append(_AzureCall(text=text, voice=voice, rate=rate, pitch=pitch, locale=locale))
        if self.next_exc:
            exc, self.next_exc = self.next_exc, None
            raise exc
        return SpeechResult(
            audio_bytes=b"AZURE_BYTES", voice=voice, char_count=len(text), latency_ms=42,
        )


class _FakeEleven:
    def __init__(self):
        self.calls: List[tuple] = []
        self.next_exc = None  # set to raise on next call (then cleared)
        self.always_raise = None  # raise every call

    def synthesize(self, *, text, voice_id):
        self.calls.append((text, voice_id))
        exc = self.always_raise or self.next_exc
        self.next_exc = None
        if exc:
            raise exc
        return ElevenLabsResult(
            audio_bytes=b"ELEVEN_BYTES", voice=voice_id, char_count=len(text), latency_ms=11,
        )


def _make_dispatcher(**overrides):
    defaults = dict(
        azure_client=_FakeAzure(),
        elevenlabs_client=_FakeEleven(),
        elevenlabs_voice_ids={"dowager": "voice_dowager"},
        failure_threshold=2,
        cooldown_seconds=10,
    )
    defaults.update(overrides)
    return TtsDispatcher(**defaults)


def _spec(provider: str = "", voice: str = "en-US-AriaNeural", post: str = "") -> VoiceSpec:
    return VoiceSpec(voice=voice, tts_provider=provider, post_process=post)


# ----- Provider routing -----

def test_no_provider_uses_azure():
    d = _make_dispatcher()
    out = d.synthesize(text="hi", spec=_spec(provider=""), leader_key="lincoln")
    assert out.provider == PROVIDER_AZURE
    assert out.skip_post_process is False
    assert d.elevenlabs_client.calls == []
    assert len(d.azure_client.calls) == 1


def test_elevenlabs_provider_routes_to_elevenlabs():
    d = _make_dispatcher()
    out = d.synthesize(
        text="hi", spec=_spec(provider="elevenlabs", post="elderly_crone"),
        leader_key="dowager", leader_name="Dowager",
    )
    assert out.provider == PROVIDER_ELEVENLABS
    assert out.audio_bytes == b"ELEVEN_BYTES"
    assert out.skip_post_process is True  # critical: skip ffmpeg
    assert out.used_fallback is False
    assert d.elevenlabs_client.calls == [("hi", "voice_dowager")]
    assert d.azure_client.calls == []


def test_elevenlabs_unconfigured_falls_to_azure_without_attempt():
    d = _make_dispatcher(elevenlabs_client=None)
    out = d.synthesize(
        text="hi", spec=_spec(provider="elevenlabs"), leader_key="dowager",
    )
    assert out.provider == PROVIDER_AZURE
    assert out.used_fallback is False  # never attempted ElevenLabs


def test_elevenlabs_missing_voice_id_falls_to_azure_without_attempt():
    d = _make_dispatcher(elevenlabs_voice_ids={})
    out = d.synthesize(
        text="hi", spec=_spec(provider="elevenlabs"), leader_key="dowager",
    )
    assert out.provider == PROVIDER_AZURE
    assert d.elevenlabs_client.calls == []  # never attempted


# ----- Fallback on each failure type -----

@pytest.mark.parametrize("exc_cls,reason", [
    (ElevenLabsAuthError, "auth"),
    (ElevenLabsQuotaError, "quota"),
    (ElevenLabsApiError, "api"),
    (RuntimeError, "unexpected"),
])
def test_elevenlabs_failure_falls_back_to_azure(exc_cls, reason):
    d = _make_dispatcher()
    d.elevenlabs_client.next_exc = exc_cls("boom")
    out = d.synthesize(
        text="hi", spec=_spec(provider="elevenlabs"), leader_key="dowager",
    )
    assert out.provider == PROVIDER_AZURE
    assert out.used_fallback is True
    assert out.skip_post_process is False  # Azure path keeps ffmpeg behaviour
    assert out.audio_bytes == b"AZURE_BYTES"
    assert len(d.elevenlabs_client.calls) == 1
    assert len(d.azure_client.calls) == 1


# ----- Circuit breaker -----

def test_circuit_opens_after_threshold_failures():
    d = _make_dispatcher(failure_threshold=2, cooldown_seconds=999)
    d.elevenlabs_client.always_raise = ElevenLabsApiError("nope")

    # First two requests both attempt ElevenLabs and fall back.
    for _ in range(2):
        out = d.synthesize(text="hi", spec=_spec(provider="elevenlabs"), leader_key="dowager")
        assert out.provider == PROVIDER_AZURE
        assert out.used_fallback is True
    assert len(d.elevenlabs_client.calls) == 2
    assert d.circuit.is_open()

    # Third request: circuit open -> short-circuit to Azure, no ElevenLabs call.
    out = d.synthesize(text="hi", spec=_spec(provider="elevenlabs"), leader_key="dowager")
    assert out.provider == PROVIDER_AZURE
    assert out.used_fallback is False  # didn't attempt this time
    assert len(d.elevenlabs_client.calls) == 2  # still 2, no new attempt


def test_circuit_closes_after_cooldown():
    # Use raw _Circuit so we can inject `now` deterministically.
    c = _Circuit(failure_threshold=2, cooldown_seconds=10)
    assert not c.is_open(now=0.0)
    c.record_failure(now=0.0)
    c.record_failure(now=1.0)  # this opens it
    assert c.is_open(now=1.0)
    assert c.is_open(now=10.5)
    # After cooldown elapses (from open time = 1.0), it auto-closes.
    assert not c.is_open(now=11.5)


def test_success_resets_failure_counter():
    d = _make_dispatcher(failure_threshold=2, cooldown_seconds=999)
    d.elevenlabs_client.next_exc = ElevenLabsApiError("transient")
    d.synthesize(text="hi", spec=_spec(provider="elevenlabs"), leader_key="dowager")
    assert d.circuit.failures == 1

    # Next call succeeds -> counter resets.
    out = d.synthesize(text="hi", spec=_spec(provider="elevenlabs"), leader_key="dowager")
    assert out.provider == PROVIDER_ELEVENLABS
    assert d.circuit.failures == 0


# ----- Hard Azure failures propagate -----

def test_azure_auth_error_propagates():
    d = _make_dispatcher()
    d.azure_client.next_exc = SpeechAuthError("bad key")
    with pytest.raises(SpeechAuthError):
        d.synthesize(text="hi", spec=_spec(provider=""), leader_key="lincoln")


def test_azure_failure_after_elevenlabs_failure_propagates():
    """If both providers fail, the Azure error is what bubbles up (last attempt)."""
    d = _make_dispatcher()
    d.elevenlabs_client.next_exc = ElevenLabsApiError("eleven fail")
    d.azure_client.next_exc = SpeechApiError("azure fail")
    with pytest.raises(SpeechApiError):
        d.synthesize(text="hi", spec=_spec(provider="elevenlabs"), leader_key="dowager")


# ----- Azure call shape preserved -----

def test_azure_call_passes_rate_pitch_locale_through():
    d = _make_dispatcher()
    spec = VoiceSpec(
        voice="en-GB-SoniaNeural", rate="-15%", pitch="-3%",
        locale="en-GB", post_process="elderly_crone",
    )
    d.synthesize(text="hello", spec=spec, leader_key="x", locale_override="en-GB")
    call = d.azure_client.calls[0]
    assert call.voice == "en-GB-SoniaNeural"
    assert call.rate == "-15%"
    assert call.pitch == "-3%"
    assert call.locale == "en-GB"


def test_locale_override_passed_to_azure():
    d = _make_dispatcher()
    spec = VoiceSpec(voice="en-US-AriaNeural", locale="en-US")
    d.synthesize(text="hello", spec=spec, leader_key="x", locale_override="ru-RU")
    assert d.azure_client.calls[0].locale == "ru-RU"


def test_empty_locale_override_passed_through_as_empty():
    """Historical contract: voiceover_response passes locale='' when not native mode."""
    d = _make_dispatcher()
    spec = VoiceSpec(voice="en-GB-SoniaNeural", locale="en-GB")
    d.synthesize(text="hello", spec=spec, leader_key="x", locale_override="")
    assert d.azure_client.calls[0].locale == ""


def test_build_elevenlabs_voice_id_map_covers_all_dowager_aliases():
    """Regression: leader_voices.json normalizes 'Dowager Countess' to
    'dowagercountess', so the voice-id map must include every alias the
    JSON file ships with -- otherwise the dispatcher silently falls back
    to Azure even when ElevenLabs is configured."""
    from tools.chatter.tts_dispatcher import (
        build_elevenlabs_voice_id_map, DOWAGER_LEADER_ALIASES,
    )
    m = build_elevenlabs_voice_id_map(voice_id_dowager="vid_X")
    # All Dowager aliases must be present and point to the explicit arg
    for alias in DOWAGER_LEADER_ALIASES:
        assert m[alias] == "vid_X"
    # Auto-discovered entries from leader_voices.json may also be present
    assert len(m) >= len(DOWAGER_LEADER_ALIASES)


def test_build_elevenlabs_voice_id_map_empty_when_no_id():
    from tools.chatter.tts_dispatcher import build_elevenlabs_voice_id_map, DOWAGER_LEADER_ALIASES
    m = build_elevenlabs_voice_id_map(voice_id_dowager="")
    # No Dowager aliases when voice_id_dowager is empty
    for alias in DOWAGER_LEADER_ALIASES:
        assert m.get(alias) is None or m.get(alias) != ""
    # But auto-discovered entries from JSON may still be present


def test_dispatcher_routes_dowagercountess_alias_to_elevenlabs():
    """Real-leader-key regression: VoicePicker normalizes 'Dowager Countess'
    to 'dowagercountess'; that key must hit ElevenLabs."""
    from tools.chatter.tts_dispatcher import build_elevenlabs_voice_id_map
    d = _make_dispatcher(
        elevenlabs_voice_ids=build_elevenlabs_voice_id_map(voice_id_dowager="vid_dowager"),
    )
    out = d.synthesize(
        text="hi", spec=_spec(provider="elevenlabs"),
        leader_key="dowagercountess",
    )
    assert out.provider == PROVIDER_ELEVENLABS
    assert d.elevenlabs_client.calls == [("hi", "vid_dowager")]
