"""Audio post-processing: pipe synthesized WAV bytes through ffmpeg filters.

Used to give individual leaders bespoke vocal character that Azure neural
voices + SSML prosody alone can't produce. Currently:

  - "elderly_crone": ages a young-sounding Azure voice into a frail,
    quavering, raspy old woman. Tuned for the Dowager Countess
    (Dragon HD Omni en-gb-sandoverture base).

The preset chain is intentionally a single string so it stays trivially
auditable in code review and easily duplicable in standalone ffmpeg
testing. Add new presets by extending PRESETS.

If ffmpeg fails or isn't on PATH, returns the original bytes unmodified
and logs the failure -- voice still works, just without aging.
"""
from __future__ import annotations

import logging
import os
import shutil
import subprocess
from typing import Optional

# Suppress console window popup on Windows when spawning ffmpeg
_CREATE_NO_WINDOW = 0x08000000 if os.name == "nt" else 0


# Source sample rate Azure returns for our DEFAULT_OUTPUT_FORMAT
# (riff-24khz-16bit-mono-pcm). asetrate ratios below assume 24kHz input;
# update if AzureSpeechClient.DEFAULT_OUTPUT_FORMAT ever changes.
_AZURE_SR = 24000


# Picked by user during Pass E voice tuning session (E4_raspy variant):
# tempo 0.92 + asetrate*0.87 (deep formant shift) + heavy vibrato +
# tremor + bass cut + treble boost + light bitcrush for raspy texture.
_ELDERLY_CRONE_FILTER = (
    f"atempo=0.92,"
    f"asetrate={_AZURE_SR}*0.87,"
    f"aresample={_AZURE_SR},"
    f"vibrato=f=5.5:d=0.75,"
    f"tremolo=f=4:d=0.30,"
    f"highpass=f=130,"
    f"equalizer=f=200:t=h:w=1:g=-8,"
    f"equalizer=f=3000:t=h:w=2:g=+4,"
    f"acrusher=level_in=1:bits=10:mode=log:aa=1"
)


PRESETS: dict[str, str] = {
    "elderly_crone": _ELDERLY_CRONE_FILTER,
}


def normalize_loudness(
    wav_bytes: bytes,
    *,
    target_lufs: float = -16.0,
    logger: Optional[logging.Logger] = None,
    timeout_seconds: float = 10.0,
) -> bytes:
    """EBU R128 loudness-normalize *wav_bytes* to *target_lufs*.

    Uses ffmpeg ``loudnorm`` in single-pass mode so every provider's
    output ends up at the same perceived volume.  On any failure returns
    the original bytes unmodified.
    """
    log = logger or logging.getLogger(__name__)
    if not wav_bytes:
        return wav_bytes
    if shutil.which("ffmpeg") is None:
        log.warning("normalize_loudness: ffmpeg not on PATH; skipping")
        return wav_bytes
    af = f"loudnorm=I={target_lufs}:LRA=11:TP=-1.5"
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "wav", "-i", "pipe:0",
        "-af", af,
        "-f", "wav", "pipe:1",
    ]
    try:
        proc = subprocess.run(
            cmd, input=wav_bytes, capture_output=True,
            timeout=timeout_seconds, check=False,
            creationflags=_CREATE_NO_WINDOW,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        log.warning("normalize_loudness: ffmpeg failed (%s); skipping", exc)
        return wav_bytes
    if proc.returncode != 0:
        stderr = (proc.stderr or b"").decode("utf-8", errors="replace")[:300]
        log.warning("normalize_loudness: ffmpeg exit=%d stderr=%s; skipping", proc.returncode, stderr)
        return wav_bytes
    if not proc.stdout:
        log.warning("normalize_loudness: ffmpeg produced empty output; skipping")
        return wav_bytes
    return proc.stdout


class PostProcessError(Exception):
    """ffmpeg invocation failed."""


def apply_postprocess(
    wav_bytes: bytes,
    preset: str,
    *,
    logger: Optional[logging.Logger] = None,
    timeout_seconds: float = 10.0,
) -> bytes:
    """Run wav_bytes through ffmpeg with the named preset filter chain.

    Returns the processed WAV bytes. On any failure (ffmpeg missing,
    unknown preset, subprocess error, timeout), logs a warning and
    returns the original bytes unmodified so voice playback still works.

    The input must be a parseable WAV stream (Azure's default
    riff-24khz-16bit-mono-pcm is fine). Output is also WAV.
    """
    log = logger or logging.getLogger(__name__)
    if not preset:
        return wav_bytes
    filter_chain = PRESETS.get(preset)
    if filter_chain is None:
        log.warning("audio_postprocess: unknown preset %r; returning raw audio", preset)
        return wav_bytes
    if shutil.which("ffmpeg") is None:
        log.warning("audio_postprocess: ffmpeg not on PATH; returning raw audio")
        return wav_bytes
    cmd = [
        "ffmpeg",
        "-y",
        "-loglevel", "error",
        "-f", "wav",
        "-i", "pipe:0",
        "-af", filter_chain,
        "-f", "wav",
        "pipe:1",
    ]
    try:
        proc = subprocess.run(
            cmd,
            input=wav_bytes,
            capture_output=True,
            timeout=timeout_seconds,
            check=False,
            creationflags=_CREATE_NO_WINDOW,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        log.warning("audio_postprocess: ffmpeg invocation failed (%s); returning raw audio", exc)
        return wav_bytes
    if proc.returncode != 0:
        stderr = (proc.stderr or b"").decode("utf-8", errors="replace")[:300]
        log.warning(
            "audio_postprocess: ffmpeg preset=%s exit=%d stderr=%s; returning raw audio",
            preset, proc.returncode, stderr,
        )
        return wav_bytes
    if not proc.stdout:
        log.warning("audio_postprocess: ffmpeg produced empty output; returning raw audio")
        return wav_bytes
    return proc.stdout
