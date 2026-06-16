"""Audition script: compare XTTSv2 vs Qwen3-TTS with the same text + voice.

Usage:
    python -m tools.tts_server.audition --text "Hello there" --voice dowager
    python -m tools.tts_server.audition --model xtts --text "Hello"
    python -m tools.tts_server.audition --model qwen3 --text "Hello"
    python -m tools.tts_server.audition --both --text "Hello" --voice dowager
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

VOICES_DIR = Path(__file__).parent / "voices"
REGISTRY_PATH = Path(__file__).parent / "voice_registry.json"
OUTPUT_DIR = Path(__file__).parent / "audition_output"


def load_registry():
    with open(REGISTRY_PATH) as f:
        return json.load(f)


def get_reference_wav(voice_id: str) -> Path:
    reg = load_registry()
    voices = reg.get("voices", {})
    if voice_id not in voices:
        print(f"Error: voice '{voice_id}' not in registry. Available: {list(voices.keys())}")
        sys.exit(1)
    ref = Path(__file__).parent / voices[voice_id]["reference_wav"]
    if not ref.exists():
        print(f"Error: reference WAV not found: {ref}")
        print("Run Generate-TtsReference.ps1 first to create it.")
        sys.exit(1)
    return ref


def synthesize_xtts(text: str, ref_wav: Path, output: Path, device: str) -> float:
    from TTS.api import TTS as CoquiTTS
    import numpy as np
    import wave

    print(f"  Loading XTTSv2 (device={device})...")
    tts = CoquiTTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

    print(f"  Synthesizing ({len(text)} chars)...")
    t0 = time.time()
    wav = tts.tts(text=text, speaker_wav=str(ref_wav), language="en")
    elapsed = time.time() - t0

    # Save as WAV
    samples = np.array(wav, dtype=np.float32)
    samples = np.clip(samples, -1.0, 1.0)
    pcm = (samples * 32767).astype(np.int16)
    with wave.open(str(output), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(24000)
        wf.writeframes(pcm.tobytes())

    return elapsed


def synthesize_qwen3(text: str, ref_wav: Path, output: Path, device: str) -> float:
    import torch
    import numpy as np
    import soundfile as sf
    import wave
    from transformers import AutoProcessor, AutoModelForTextToWaveform

    print(f"  Loading Qwen3-TTS (device={device})...")
    model_id = "Qwen/Qwen3-TTS"
    processor = AutoProcessor.from_pretrained(model_id)
    model = AutoModelForTextToWaveform.from_pretrained(model_id).to(device)

    ref_audio, ref_sr = sf.read(str(ref_wav))
    if len(ref_audio.shape) > 1:
        ref_audio = ref_audio.mean(axis=1)

    inputs = processor(text=text, audio=ref_audio, sampling_rate=ref_sr, return_tensors="pt").to(device)

    print(f"  Synthesizing ({len(text)} chars)...")
    t0 = time.time()
    with torch.no_grad():
        output_wav = model.generate(**inputs)
    elapsed = time.time() - t0

    samples = output_wav.cpu().numpy().squeeze().astype(np.float32)
    samples = np.clip(samples, -1.0, 1.0)
    pcm = (samples * 32767).astype(np.int16)
    with wave.open(str(output), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(24000)
        wf.writeframes(pcm.tobytes())

    return elapsed


def play_wav(path: Path):
    if sys.platform == "win32":
        os.startfile(str(path))
    elif sys.platform == "darwin":
        subprocess.run(["open", str(path)])
    else:
        subprocess.run(["xdg-open", str(path)])


def main():
    import torch

    parser = argparse.ArgumentParser(description="Audition local TTS models")
    parser.add_argument("--text", required=True, help="Text to synthesize")
    parser.add_argument("--voice", default="dowager", help="Voice registry ID")
    parser.add_argument("--model", choices=["xtts", "qwen3", "both"], default="both")
    parser.add_argument("--device", default="auto", help="auto/cuda/cpu")
    parser.add_argument("--no-play", action="store_true", help="Don't auto-play output")
    args = parser.parse_args()

    device = args.device
    if device == "auto":
        device = "cuda" if torch.cuda.is_available() else "cpu"

    ref_wav = get_reference_wav(args.voice)
    OUTPUT_DIR.mkdir(exist_ok=True)

    results = []
    models = ["xtts", "qwen3"] if args.model == "both" else [args.model]

    for model in models:
        print(f"\n{'='*50}")
        print(f"Model: {model.upper()}")
        print(f"{'='*50}")

        out_path = OUTPUT_DIR / f"audition_{model}_{args.voice}_{int(time.time())}.wav"

        if model == "xtts":
            elapsed = synthesize_xtts(args.text, ref_wav, out_path, device)
        else:
            elapsed = synthesize_qwen3(args.text, ref_wav, out_path, device)

        size_kb = out_path.stat().st_size / 1024
        print(f"  Done: {elapsed:.1f}s, {size_kb:.1f} KB → {out_path.name}")
        results.append((model, elapsed, out_path))

        if not args.no_play:
            print("  Playing...")
            play_wav(out_path)
            if len(models) > 1:
                input("  Press Enter for next model...")

    print(f"\n{'='*50}")
    print("Summary:")
    for model, elapsed, path in results:
        print(f"  {model:8s}: {elapsed:.1f}s  →  {path}")


if __name__ == "__main__":
    main()
