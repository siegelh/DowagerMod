"""Local TTS Server — zero-shot voice cloning via XTTSv2 or Chatterbox Turbo.

Exposes a FastAPI endpoint that accepts text + voice_id and returns WAV audio.
Supports multiple voices via reference WAV files in the voice registry.

Usage:
    python -m tools.tts_server.server [--host 0.0.0.0] [--port 8080] [--model xtts|chatterbox]
    # or via the Start-TtsServer.ps1 script
"""

from __future__ import annotations

import argparse
import io
import json
import logging
import os
import time
import wave
from pathlib import Path
from typing import Optional

# --- Compatibility shims (must run before importing TTS/torch downstream) ---
# PyTorch 2.6 defaults torch.load(weights_only=True) which breaks Coqui TTS
# model deserialization. Override globally for this process.
import torch
_original_torch_load = torch.load
def _patched_torch_load(*args, **kwargs):
    kwargs.setdefault("weights_only", False)
    return _original_torch_load(*args, **kwargs)
torch.load = _patched_torch_load

# Coqui TTS requires license acceptance
os.environ["COQUI_TOS_AGREED"] = "1"

import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

logger = logging.getLogger("tts-server")

# ---------------------------------------------------------------------------
# Voice registry
# ---------------------------------------------------------------------------

REGISTRY_PATH = Path(__file__).parent / "voice_registry.json"


def load_registry() -> dict:
    with open(REGISTRY_PATH) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Model backends
# ---------------------------------------------------------------------------

class TtsBackend:
    """Abstract base for TTS model backends."""

    name: str = "base"

    def load(self, device: str) -> None:
        raise NotImplementedError

    def synthesize(self, text: str, reference_wav: Path) -> tuple[np.ndarray, int]:
        """Return (audio_samples_float32, sample_rate)."""
        raise NotImplementedError


class XttsBackend(TtsBackend):
    """Coqui XTTSv2 zero-shot voice cloning."""

    name = "xtts"

    def __init__(self):
        self._tts = None

    def load(self, device: str) -> None:
        from TTS.api import TTS as CoquiTTS
        logger.info("Loading XTTSv2 model (device=%s)...", device)
        self._tts = CoquiTTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
        logger.info("XTTSv2 ready.")

    def synthesize(self, text: str, reference_wav: Path) -> tuple[np.ndarray, int]:
        if self._tts is None:
            raise RuntimeError("XTTSv2 model not loaded")
        wav = self._tts.tts(
            text=text,
            speaker_wav=str(reference_wav),
            language="en",
        )
        # Coqui returns list[float] at 24000 Hz
        return np.array(wav, dtype=np.float32), 24000


class ChatterboxBackend(TtsBackend):
    """Chatterbox Turbo zero-shot voice cloning (Resemble AI)."""

    name = "chatterbox"

    def __init__(self):
        self._model = None
        self._device = "cpu"

    def load(self, device: str) -> None:
        from chatterbox.tts_turbo import ChatterboxTurboTTS
        logger.info("Loading Chatterbox Turbo model (device=%s)...", device)
        self._model = ChatterboxTurboTTS.from_pretrained(device=device)
        self._device = device
        logger.info("Chatterbox Turbo ready.")

    def synthesize(self, text: str, reference_wav: Path) -> tuple[np.ndarray, int]:
        if self._model is None:
            raise RuntimeError("Chatterbox model not loaded")

        wav = self._model.generate(
            text=text,
            audio_prompt_path=str(reference_wav),
        )
        # wav is a torch tensor [1, samples] or [samples]; model.sr is sample rate
        samples = wav.squeeze().cpu().numpy().astype(np.float32)
        # Normalize to [-1, 1] if needed
        peak = np.abs(samples).max()
        if peak > 1.0:
            samples = samples / peak
        return samples, self._model.sr


BACKENDS = {
    "xtts": XttsBackend,
    "chatterbox": ChatterboxBackend,
}

# ---------------------------------------------------------------------------
# Audio encoding
# ---------------------------------------------------------------------------


def encode_wav_pcm16(samples: np.ndarray, sample_rate: int) -> bytes:
    """Convert float32 audio to 16-bit PCM WAV bytes."""
    # Clip and convert
    samples = np.clip(samples, -1.0, 1.0)
    pcm = (samples * 32767).astype(np.int16)

    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm.tobytes())
    return buf.getvalue()


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

app = FastAPI(title="Local TTS Server", version="0.1.0")

# Global state (populated on startup)
_backend: Optional[TtsBackend] = None
_registry: dict = {}
_voices_dir: Path = Path(__file__).parent / "voices"


class SynthesizeRequest(BaseModel):
    text: str
    voice_id: str = "dowager"


class HealthResponse(BaseModel):
    status: str
    model: str
    voices: list[str]
    device: str


@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="ready" if _backend else "not_loaded",
        model=_backend.name if _backend else "none",
        voices=list(_registry.get("voices", {}).keys()),
        device=getattr(_backend, "_device", "unknown"),
    )


@app.post("/synthesize")
async def synthesize(req: SynthesizeRequest):
    if _backend is None:
        raise HTTPException(503, "Model not loaded")

    voices = _registry.get("voices", {})
    if req.voice_id not in voices:
        raise HTTPException(
            404, f"Voice '{req.voice_id}' not found. Available: {list(voices.keys())}"
        )

    ref_path = _voices_dir.parent / voices[req.voice_id]["reference_wav"]
    if not ref_path.exists():
        raise HTTPException(
            500, f"Reference WAV not found: {ref_path}"
        )

    t0 = time.time()
    try:
        samples, sr = _backend.synthesize(req.text, ref_path)
    except Exception as exc:
        logger.exception("Synthesis failed: %s", exc)
        raise HTTPException(500, f"Synthesis error: {exc}")

    wav_bytes = encode_wav_pcm16(samples, sr)
    latency_ms = int((time.time() - t0) * 1000)

    logger.info(
        "synth ok voice=%s chars=%d latency=%dms bytes=%d",
        req.voice_id, len(req.text), latency_ms, len(wav_bytes),
    )

    return Response(
        content=wav_bytes,
        media_type="audio/wav",
        headers={
            "X-Latency-Ms": str(latency_ms),
            "X-Voice-Id": req.voice_id,
            "X-Model": _backend.name,
        },
    )


# ---------------------------------------------------------------------------
# Startup
# ---------------------------------------------------------------------------


def create_app(model_name: str = "xtts", device: str = "auto") -> FastAPI:
    """Initialize the backend and return the configured app."""
    import torch

    global _backend, _registry

    if device == "auto":
        device = "cuda" if torch.cuda.is_available() else "cpu"

    _registry = load_registry()

    backend_cls = BACKENDS.get(model_name)
    if not backend_cls:
        raise ValueError(f"Unknown model: {model_name}. Available: {list(BACKENDS.keys())}")

    _backend = backend_cls()
    _backend._device = device
    _backend.load(device)

    return app


def main():
    import uvicorn

    parser = argparse.ArgumentParser(description="Local TTS Server")
    parser.add_argument("--host", default="0.0.0.0", help="Bind address")
    parser.add_argument("--port", type=int, default=8080, help="Port")
    parser.add_argument("--model", choices=list(BACKENDS.keys()), default="xtts",
                        help="TTS model backend")
    parser.add_argument("--device", default="auto",
                        help="Device: 'auto', 'cuda', 'cpu'")
    parser.add_argument("--log-level", default="INFO",
                        choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="[%(asctime)s] %(levelname)s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    create_app(model_name=args.model, device=args.device)

    uvicorn.run(app, host=args.host, port=args.port, log_level=args.log_level.lower())


if __name__ == "__main__":
    main()
