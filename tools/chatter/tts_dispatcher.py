"""TTS dispatcher: per-leader provider routing with Azure fallback.

Sits in front of every TTS call site so the three call sites
(:func:`chatter_daemon._speak`, :func:`chatter_daemon.voiceover_response`,
and :mod:`tools.chatter.say`) all go through one place.

Routing rule:
  * If the leader's VoiceSpec carries ``tts_provider == "elevenlabs"`` AND
    an ElevenLabs client is configured AND the circuit breaker for
    ElevenLabs is closed -> try ElevenLabs first. On any failure, log
    structured FALLBACK record, trip the breaker (per failure type), and
    fall through to Azure Speech.
  * Otherwise -> go straight to Azure Speech exactly as the daemon did
    before this dispatcher existed.

Circuit breaker:
  * Counts consecutive failures of the ElevenLabs provider only. Azure
    failures are unaffected. A single success resets the counter to 0.
  * After ``failure_threshold`` consecutive failures (default 2) the
    breaker opens for ``cooldown_seconds`` (default 600). While open,
    ElevenLabs requests are short-circuited to Azure without an HTTP
    round-trip -- this is what lets the free-tier quota recover without
    spamming the API or the operator's logs.
  * When the cooldown expires the breaker auto-closes and the next
    eligible request tries ElevenLabs again.

The dispatcher returns a :class:`DispatchResult` whose ``skip_post_process``
field tells the caller whether to apply ``audio_postprocess`` presets
(e.g. ``elderly_crone``). ElevenLabs responses skip post-processing
because the operator's custom ElevenLabs voice already sounds the way
they want; Azure-fallback responses preserve the existing behaviour
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
from tools.chatter.voice_picker import VoiceSpec


PROVIDER_AZURE = "azure"
PROVIDER_ELEVENLABS = "elevenlabs"


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
    """Routes TTS requests to ElevenLabs (with Azure fallback) or Azure direct.

    ``azure_client`` is required -- it is the always-on baseline. The
    ``elevenlabs_client`` and the per-leader voice ID map are optional:
    when missing, the dispatcher behaves exactly like calling Azure
    directly. This is the property that lets the feature ship to users
    who have no ElevenLabs key.
    """

    def __init__(
        self,
        *,
        azure_client: AzureSpeechClient,
        elevenlabs_client: Optional[ElevenLabsClient] = None,
        elevenlabs_voice_ids: Optional[dict] = None,
        failure_threshold: int = 2,
        cooldown_seconds: int = 600,
        logger: Optional[logging.Logger] = None,
    ):
        self.azure_client = azure_client
        self.elevenlabs_client = elevenlabs_client
        # Mapping of normalized leader keys (e.g. "dowager") -> ElevenLabs
        # voice IDs. Today this only carries "dowager" but the shape is
        # generalisable; the chatter daemon builds it from VoiceoverConfig.
        self.voice_ids = {
            (k or "").strip().lower(): (v or "").strip()
            for k, v in (elevenlabs_voice_ids or {}).items()
            if v
        }
        self.circuit = _Circuit(
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
        ``voice_picker.normalize_name``) used to look up an ElevenLabs voice
        ID. ``leader_name`` is the human-readable label used only for
        structured log lines. ``locale_override`` is passed straight through
        to Azure for native-tongue mode.
        """
        provider = self._choose_provider(spec=spec, leader_key=leader_key)
        if provider == PROVIDER_ELEVENLABS:
            try:
                return self._synthesize_elevenlabs(
                    text=text, leader_key=leader_key, leader_name=leader_name,
                )
            except _FallbackRequested:
                # _synthesize_elevenlabs already logged the FALLBACK record.
                pass
            return self._synthesize_azure(
                text=text, spec=spec, leader_name=leader_name,
                locale_override=locale_override, used_fallback=True,
            )
        return self._synthesize_azure(
            text=text, spec=spec, leader_name=leader_name,
            locale_override=locale_override, used_fallback=False,
        )

    # ----- internals -----

    def _choose_provider(self, *, spec: VoiceSpec, leader_key: str) -> str:
        if spec.tts_provider != PROVIDER_ELEVENLABS:
            return PROVIDER_AZURE
        if self.elevenlabs_client is None:
            return PROVIDER_AZURE
        if not self.voice_ids.get(leader_key):
            return PROVIDER_AZURE
        if self.circuit.is_open():
            return PROVIDER_AZURE
        return PROVIDER_ELEVENLABS

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
