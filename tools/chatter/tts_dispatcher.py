"""TTS dispatcher: per-leader provider routing with cascading fallback.

Sits in front of every TTS call site so the three call sites
(:func:`chatter_daemon._speak`, :func:`chatter_daemon.voiceover_response`,
and :mod:`tools.chatter.say`) all go through one place.

Routing rule (priority chain):
  * If the leader's VoiceSpec carries ``tts_provider == "local"`` AND
    a local TTS client is configured AND its circuit breaker is closed
    -> try local server first. On failure, fall through to ElevenLabs
    (if configured) then Azure.
  * If the leader's VoiceSpec carries ``tts_provider == "elevenlabs"`` AND
    an ElevenLabs client is configured AND the circuit breaker for
    ElevenLabs is closed -> try ElevenLabs first. On any failure, log
    structured FALLBACK record, trip the breaker (per failure type), and
    fall through to Azure Speech.
  * Otherwise -> go straight to Azure Speech exactly as the daemon did
    before this dispatcher existed.

Circuit breaker:
  * Separate breakers for local and ElevenLabs providers.
  * Counts consecutive failures per provider. A single success resets the
    counter to 0.
  * After ``failure_threshold`` consecutive failures (default 2) the
    breaker opens for ``cooldown_seconds`` (default 600). While open,
    requests are short-circuited to the next provider without a round-trip.
  * When the cooldown expires the breaker auto-closes and the next
    eligible request tries the provider again.

The dispatcher returns a :class:`DispatchResult` whose ``skip_post_process``
field tells the caller whether to apply ``audio_postprocess`` presets
(e.g. ``elderly_crone``). ElevenLabs and local responses skip post-processing
because the operator's custom voice already sounds the way they want;
Azure-fallback responses preserve the existing behaviour
(post-process per ``VoiceSpec.post_process``).
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Optional

from tools.chatter.azure_speech_client import (
    AzureSpeechClient,
    SpeechApiError,
    SpeechAuthError,
    SpeechBudgetExhausted,
    SpeechResult,
)
from tools.chatter.elevenlabs_client import (
    ElevenLabsApiError,
    ElevenLabsAuthError,
    ElevenLabsClient,
    ElevenLabsQuotaError,
    ElevenLabsResult,
)
from tools.chatter.local_tts_client import (
    LocalTtsApiError,
    LocalTtsClient,
    LocalTtsResult,
    LocalTtsUnavailable,
)
from tools.chatter.voice_picker import VoiceSpec


PROVIDER_AZURE = "azure"
PROVIDER_ELEVENLABS = "elevenlabs"
PROVIDER_LOCAL = "local"


# The Dowager Countess appears under four normalized aliases in
# leader_voices.json (dowager, dowagercountess, thedowager,
# thedowagercountess). We map every alias to the same ElevenLabs voice ID
# so leader_key lookup hits regardless of which form the LLM emitted as
# the speaker name.
DOWAGER_LEADER_ALIASES = (
    "dowager",
    "dowagercountess",
    "thedowager",
    "thedowagercountess",
)


def build_elevenlabs_voice_id_map(*, voice_id_dowager: str) -> dict:
    """Return a normalized-leader-key -> ElevenLabs voice ID map.

    Centralised here so daemon + ``say.py`` + smoke tests stay in
    lockstep with ``leader_voices.json``. Adding a new ElevenLabs leader
    means (a) appending its config slot in ``VoiceoverConfig``, (b)
    adding ``"tts_provider": "elevenlabs"`` to its JSON entries, and (c)
    extending this map with its aliases.
    """
    out = {}
    if voice_id_dowager:
        for alias in DOWAGER_LEADER_ALIASES:
            out[alias] = voice_id_dowager
    return out


@dataclass
class DispatchResult:
    """Provider-agnostic TTS result returned by :meth:`TtsDispatcher.synthesize`.

    Shape is the union of :class:`SpeechResult` and :class:`ElevenLabsResult`
    plus two new fields callers need to know about:

    * ``provider`` -- which backend actually produced the audio
      (``"elevenlabs"`` or ``"azure"``).
    * ``used_fallback`` -- True when the request started on ElevenLabs and
      ended up on Azure due to a failure.
    * ``skip_post_process`` -- True for ElevenLabs success only. The chatter
      daemon honours this by skipping ``audio_postprocess`` presets (e.g.
      ``elderly_crone``) -- the operator's custom ElevenLabs voice already
      sounds right and additional ffmpeg munging would degrade it.
    """
    audio_bytes: bytes
    voice: str
    char_count: int
    latency_ms: int
    provider: str
    used_fallback: bool = False
    skip_post_process: bool = False


class _Circuit:
    """Simple consecutive-failure circuit breaker.

    Not thread-safe. The chatter daemon serialises TTS calls behind a
    single asyncio task, so a lock would be dead weight.
    """

    def __init__(self, *, failure_threshold: int, cooldown_seconds: int):
        self.failure_threshold = max(1, int(failure_threshold))
        self.cooldown_seconds = max(0, int(cooldown_seconds))
        self.failures = 0
        self.opened_at: Optional[float] = None

    def is_open(self, *, now: Optional[float] = None) -> bool:
        if self.opened_at is None:
            return False
        ts = now if now is not None else time.monotonic()
        if ts - self.opened_at >= self.cooldown_seconds:
            # Cooldown elapsed; auto-close. Counter stays at threshold so a
            # single new failure re-opens immediately.
            self.opened_at = None
            return False
        return True

    def record_success(self) -> bool:
        """Return True iff this success closed an open circuit."""
        was_open = self.opened_at is not None
        self.failures = 0
        self.opened_at = None
        return was_open

    def record_failure(self, *, now: Optional[float] = None) -> bool:
        """Return True iff this failure tripped the breaker (transition into open)."""
        self.failures += 1
        if self.failures >= self.failure_threshold and self.opened_at is None:
            self.opened_at = now if now is not None else time.monotonic()
            return True
        return False


class TtsDispatcher:
    """Routes TTS requests to local -> ElevenLabs -> Azure (cascading fallback).

    ``azure_client`` is required -- it is the always-on baseline. The
    ``elevenlabs_client``, ``local_client``, and the per-leader voice ID map
    are optional: when missing, the dispatcher behaves exactly like calling
    Azure directly. This is the property that lets the feature ship to users
    who have no ElevenLabs key or no local TTS server running.
    """

    def __init__(
        self,
        *,
        azure_client: AzureSpeechClient,
        elevenlabs_client: Optional[ElevenLabsClient] = None,
        local_client: Optional[LocalTtsClient] = None,
        elevenlabs_voice_ids: Optional[dict] = None,
        local_voice_ids: Optional[dict] = None,
        failure_threshold: int = 2,
        cooldown_seconds: int = 600,
        logger: Optional[logging.Logger] = None,
    ):
        self.azure_client = azure_client
        self.elevenlabs_client = elevenlabs_client
        self.local_client = local_client
        # Mapping of normalized leader keys (e.g. "dowager") -> ElevenLabs
        # voice IDs. Today this only carries "dowager" but the shape is
        # generalisable; the chatter daemon builds it from VoiceoverConfig.
        self.voice_ids = {
            (k or "").strip().lower(): (v or "").strip()
            for k, v in (elevenlabs_voice_ids or {}).items()
            if v
        }
        # Local TTS voice IDs (leader_key -> voice_id in voice_registry.json)
        self.local_voice_ids = {
            (k or "").strip().lower(): (v or "").strip()
            for k, v in (local_voice_ids or {}).items()
            if v
        }
        self.circuit = _Circuit(
            failure_threshold=failure_threshold,
            cooldown_seconds=cooldown_seconds,
        )
        self.local_circuit = _Circuit(
            failure_threshold=failure_threshold,
            cooldown_seconds=cooldown_seconds,
        )
        self.logger = logger or logging.getLogger("dowager.chatter.tts.dispatcher")

    # ----- public API -----

    def synthesize(
        self,
        *,
        text: str,
        spec: VoiceSpec,
        leader_key: str = "",
        leader_name: str = "",
        locale_override: str = "",
    ) -> DispatchResult:
        """Synthesize ``text`` for ``spec``. Returns a :class:`DispatchResult`.

        ``leader_key`` is the normalized name (matches
        ``voice_picker.normalize_name``) used to look up a voice ID.
        ``leader_name`` is the human-readable label used only for
        structured log lines. ``locale_override`` is passed straight through
        to Azure for native-tongue mode.

        Provider priority chain (each skipped if unconfigured/circuit-open):
        local -> elevenlabs -> azure
        """
        provider = self._choose_provider(spec=spec, leader_key=leader_key)

        # Try local first
        if provider == PROVIDER_LOCAL:
            try:
                return self._synthesize_local(
                    text=text, leader_key=leader_key, leader_name=leader_name,
                )
            except _FallbackRequested:
                pass
            # Fall through: try ElevenLabs if available for this leader
            if self._elevenlabs_available(leader_key):
                try:
                    return self._synthesize_elevenlabs(
                        text=text, leader_key=leader_key, leader_name=leader_name,
                    )
                except _FallbackRequested:
                    pass
            return self._synthesize_azure(
                text=text, spec=spec, leader_name=leader_name,
                locale_override=locale_override, used_fallback=True,
            )

        # Try ElevenLabs
        if provider == PROVIDER_ELEVENLABS:
            try:
                return self._synthesize_elevenlabs(
                    text=text, leader_key=leader_key, leader_name=leader_name,
                )
            except _FallbackRequested:
                pass
            return self._synthesize_azure(
                text=text, spec=spec, leader_name=leader_name,
                locale_override=locale_override, used_fallback=True,
            )

        # Azure direct
        return self._synthesize_azure(
            text=text, spec=spec, leader_name=leader_name,
            locale_override=locale_override, used_fallback=False,
        )

    # ----- internals -----

    def _elevenlabs_available(self, leader_key: str) -> bool:
        """Check if ElevenLabs can be tried for this leader (configured + circuit closed)."""
        return (
            self.elevenlabs_client is not None
            and bool(self.voice_ids.get(leader_key))
            and not self.circuit.is_open()
        )

    def _choose_provider(self, *, spec: VoiceSpec, leader_key: str) -> str:
        # Local provider: either explicitly tagged or ElevenLabs-tagged leaders
        # auto-try local first if a local client + voice ID is available.
        if self.local_client is not None and not self.local_circuit.is_open():
            if spec.tts_provider == PROVIDER_LOCAL:
                if self.local_voice_ids.get(leader_key):
                    return PROVIDER_LOCAL
            # Also try local for elevenlabs-tagged leaders if they have a
            # local voice ID (local is free, ElevenLabs costs quota)
            elif spec.tts_provider == PROVIDER_ELEVENLABS:
                if self.local_voice_ids.get(leader_key):
                    return PROVIDER_LOCAL

        if spec.tts_provider in (PROVIDER_ELEVENLABS, PROVIDER_LOCAL):
            if self.elevenlabs_client is not None:
                if self.voice_ids.get(leader_key):
                    if not self.circuit.is_open():
                        return PROVIDER_ELEVENLABS
        return PROVIDER_AZURE

    def _synthesize_local(
        self,
        *,
        text: str,
        leader_key: str,
        leader_name: str,
    ) -> DispatchResult:
        voice_id = self.local_voice_ids.get(leader_key, "dowager")
        t0 = time.perf_counter()
        try:
            result: LocalTtsResult = self.local_client.synthesize(
                text=text, voice_id=voice_id,
            )
        except LocalTtsUnavailable as exc:
            self._handle_local_failure("unavailable", exc, t0, leader_name)
            raise _FallbackRequested() from exc
        except LocalTtsApiError as exc:
            self._handle_local_failure("api", exc, t0, leader_name)
            raise _FallbackRequested() from exc
        except Exception as exc:  # noqa: BLE001
            self._handle_local_failure("unexpected", exc, t0, leader_name)
            raise _FallbackRequested() from exc

        if self.local_circuit.record_success():
            self.logger.info("tts: local circuit closed; retrying")
        self.logger.info(
            "tts: ok provider=local voice=%s model=%s leader=%s chars=%d latency=%dms",
            result.voice_id, result.model, leader_name or "?",
            result.char_count, result.latency_ms,
        )
        return DispatchResult(
            audio_bytes=result.audio_bytes,
            voice=result.voice_id,
            char_count=result.char_count,
            latency_ms=result.latency_ms,
            provider=PROVIDER_LOCAL,
            used_fallback=False,
            # Local TTS uses the same zero-shot cloned voice -> skip post-process
            skip_post_process=True,
        )

    def _handle_local_failure(
        self,
        reason: str,
        exc: BaseException,
        t0: float,
        leader_name: str,
    ) -> None:
        elapsed = int((time.perf_counter() - t0) * 1000)
        self.logger.warning(
            "tts: fallback provider=local->next leader=%s reason=%s elapsed=%dms err=%s",
            leader_name or "?", reason, elapsed, exc,
        )
        if self.local_circuit.record_failure():
            self.logger.warning(
                "tts: local circuit open after %d failures; cooldown %ds",
                self.local_circuit.failures, self.local_circuit.cooldown_seconds,
            )

    def _synthesize_elevenlabs(
        self,
        *,
        text: str,
        leader_key: str,
        leader_name: str,
    ) -> DispatchResult:
        voice_id = self.voice_ids.get(leader_key, "")
        t0 = time.perf_counter()
        try:
            result: ElevenLabsResult = self.elevenlabs_client.synthesize(
                text=text, voice_id=voice_id,
            )
        except ElevenLabsAuthError as exc:
            self._handle_elevenlabs_failure("auth", exc, t0, leader_name)
            raise _FallbackRequested() from exc
        except ElevenLabsQuotaError as exc:
            self._handle_elevenlabs_failure("quota", exc, t0, leader_name)
            raise _FallbackRequested() from exc
        except ElevenLabsApiError as exc:
            self._handle_elevenlabs_failure("api", exc, t0, leader_name)
            raise _FallbackRequested() from exc
        except Exception as exc:  # noqa: BLE001 - paranoia: never let TTS kill the daemon
            self._handle_elevenlabs_failure("unexpected", exc, t0, leader_name)
            raise _FallbackRequested() from exc

        if self.circuit.record_success():
            self.logger.info("tts: elevenlabs circuit closed; retrying")
        return DispatchResult(
            audio_bytes=result.audio_bytes,
            voice=result.voice,
            char_count=result.char_count,
            latency_ms=result.latency_ms,
            provider=PROVIDER_ELEVENLABS,
            used_fallback=False,
            # ElevenLabs voice is custom-tuned by the operator -> skip
            # ffmpeg presets that exist to age/character-shift Azure voices.
            skip_post_process=True,
        )

    def _handle_elevenlabs_failure(
        self,
        reason: str,
        exc: BaseException,
        t0: float,
        leader_name: str,
    ) -> None:
        elapsed = int((time.perf_counter() - t0) * 1000)
        self.logger.warning(
            "tts: fallback provider=elevenlabs->azure leader=%s reason=%s elapsed=%dms err=%s",
            leader_name or "?", reason, elapsed, exc,
        )
        if self.circuit.record_failure():
            self.logger.warning(
                "tts: elevenlabs circuit open after %d failures; cooldown %ds",
                self.circuit.failures, self.circuit.cooldown_seconds,
            )

    def _synthesize_azure(
        self,
        *,
        text: str,
        spec: VoiceSpec,
        leader_name: str,
        locale_override: str,
        used_fallback: bool,
    ) -> DispatchResult:
        result: SpeechResult = self.azure_client.synthesize(
            text,
            voice=spec.voice,
            rate=spec.rate,
            pitch=spec.pitch,
            locale=locale_override,
        )
        self.logger.info(
            "tts: ok provider=azure voice=%s leader=%s chars=%d latency=%dms%s",
            result.voice, leader_name or "?", result.char_count, result.latency_ms,
            " (fallback)" if used_fallback else "",
        )
        return DispatchResult(
            audio_bytes=result.audio_bytes,
            voice=result.voice,
            char_count=result.char_count,
            latency_ms=result.latency_ms,
            provider=PROVIDER_AZURE,
            used_fallback=used_fallback,
            skip_post_process=False,
        )


class _FallbackRequested(Exception):
    """Internal sentinel: ElevenLabs failed, dispatcher must fall back to Azure."""


# Re-export for callers that want to handle hard Azure failures (the
# dispatcher does NOT catch these -- they're terminal for the request,
# matching the daemon's pre-dispatcher behaviour).
__all__ = [
    "DispatchResult",
    "TtsDispatcher",
    "PROVIDER_AZURE",
    "PROVIDER_ELEVENLABS",
    "DOWAGER_LEADER_ALIASES",
    "build_elevenlabs_voice_id_map",
    "SpeechAuthError",
    "SpeechApiError",
    "SpeechBudgetExhausted",
]
