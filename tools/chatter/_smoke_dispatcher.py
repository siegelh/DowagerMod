"""One-shot smoke check: exercise the dispatcher end-to-end for the Dowager.

Routes through the same code path the daemon uses (config -> dispatcher ->
ElevenLabs client -> WAV bytes) but never starts Discord. Used during
validation to prove the wiring works against the live ElevenLabs API.

Run: `python tools\\chatter\\_smoke_dispatcher.py`
"""
from __future__ import annotations

import logging
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from tools.chatter import config as cfg_mod
from tools.chatter.azure_speech_client import AzureSpeechClient
from tools.chatter.elevenlabs_client import ElevenLabsClient
from tools.chatter.tts_dispatcher import TtsDispatcher, build_elevenlabs_voice_id_map
from tools.chatter.voice_picker import VoicePicker, normalize_name


def run(force_fallback: bool = False) -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%H:%M:%S",
    )
    log = logging.getLogger("smoke")
    cfg = cfg_mod.load_config()
    vo = cfg.voiceover

    if not vo.is_ready():
        log.error("voiceover not configured: %s", cfg_mod.validate_required(cfg))
        return 2

    azure = AzureSpeechClient(
        endpoint=vo.azure_speech_endpoint,
        key=vo.azure_speech_key,
        default_voice=vo.azure_speech_voice,
        daily_char_cap=vo.daily_char_cap,
    )

    eleven = None
    if vo.elevenlabs_enabled():
        api_key = "INVALID_KEY_FOR_FALLBACK_TEST" if force_fallback else vo.elevenlabs_api_key
        eleven = ElevenLabsClient(
            api_key=api_key,
            endpoint=vo.elevenlabs_endpoint,
            model_id=vo.elevenlabs_model,
            timeout_seconds=vo.elevenlabs_timeout_seconds,
            daily_char_cap=vo.elevenlabs_daily_char_cap,
            logger=log,
        )

    dispatcher = TtsDispatcher(
        azure_client=azure,
        elevenlabs_client=eleven,
        elevenlabs_voice_ids=build_elevenlabs_voice_id_map(
            voice_id_dowager=vo.elevenlabs_voice_id_dowager,
        ),
        failure_threshold=vo.elevenlabs_failure_threshold,
        cooldown_seconds=vo.elevenlabs_cooldown_seconds,
        logger=log,
    )

    picker = VoicePicker(default_voice=vo.azure_speech_voice, logger=log)
    spec = picker.pick_spec("Dowager Countess")
    log.info(
        "spec: voice=%s rate=%r pitch=%r post=%r provider=%r",
        spec.voice, spec.rate, spec.pitch, spec.post_process, spec.tts_provider,
    )

    text = "A small test, dear. Mind your manners, Mr. Lincoln."
    t0 = time.perf_counter()
    out = dispatcher.synthesize(
        text=text, spec=spec,
        leader_key=normalize_name("Dowager Countess"),
        leader_name="Dowager Countess",
        locale_override="",
    )
    elapsed = int((time.perf_counter() - t0) * 1000)

    log.info(
        "RESULT: provider=%s used_fallback=%s skip_post=%s bytes=%d latency=%dms total=%dms",
        out.provider, out.used_fallback, out.skip_post_process,
        len(out.audio_bytes), out.latency_ms, elapsed,
    )

    suffix = "_fallback" if force_fallback else ""
    wav = Path(tempfile.gettempdir()) / f"smoke_dispatcher_{out.provider}{suffix}_{int(time.time())}.wav"
    wav.write_bytes(out.audio_bytes)
    log.info("wav: %s", wav)
    return 0


if __name__ == "__main__":
    force = "--force-fallback" in sys.argv
    sys.exit(run(force_fallback=force))
