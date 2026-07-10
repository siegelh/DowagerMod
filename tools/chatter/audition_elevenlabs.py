"""Standalone ElevenLabs voice audition helper.

Hits ElevenLabs `/v1/text-to-speech/{voice_id}` once, wraps the returned
24 kHz mono 16-bit PCM into a RIFF/WAV file, writes it to TEMP (or
``--output``), and (by default) opens it with the OS default player so
you can A/B different models and voice settings without touching the
chatter daemon, Discord, or the game.

Use this to pick the right model (``eleven_flash_v2_5`` vs
``eleven_turbo_v2_5`` vs ``eleven_multilingual_v2``) before locking your
choice into ``.env``.

Examples:

    python -m tools.chatter.audition_elevenlabs \\
        --voice-id MQN9MRlBsPTICAJvyqWI \\
        --model eleven_flash_v2_5 \\
        --text "Mr. Lincoln, your republic shall find that the Crown's patience..."

    python -m tools.chatter.audition_elevenlabs --voice-id X --model eleven_turbo_v2_5 --text "..." --no-play

The API key is read from (in order): ``--api-key``, the
``DOWAGER_CHATTER_ELEVENLABS_API_KEY`` shell env var, then ``.env`` at
the repo root.
"""
from __future__ import annotations

import argparse
import os
import struct
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path


DEFAULT_ENDPOINT = "https://api.elevenlabs.io"
DEFAULT_MODEL = "eleven_flash_v2_5"
DEFAULT_OUTPUT_FORMAT = "pcm_24000"
DEFAULT_SAMPLE_RATE = 24000


def wrap_pcm_as_wav(pcm: bytes, sample_rate: int = DEFAULT_SAMPLE_RATE) -> bytes:
    """Wrap raw 16-bit mono PCM bytes in a minimal RIFF/WAV container."""
    channels = 1
    bits_per_sample = 16
    byte_rate = sample_rate * channels * (bits_per_sample // 8)
    block_align = channels * (bits_per_sample // 8)
    data_size = len(pcm)
    riff_size = 36 + data_size
    header = b"RIFF"
    header += struct.pack("<I", riff_size)
    header += b"WAVE"
    header += b"fmt "
    header += struct.pack("<IHHIIHH",
                          16, 1, channels, sample_rate,
                          byte_rate, block_align, bits_per_sample)
    header += b"data"
    header += struct.pack("<I", data_size)
    return header + pcm


def _resolve_api_key(cli_key: str) -> str:
    if cli_key:
        return cli_key
    env_key = os.environ.get("DOWAGER_CHATTER_ELEVENLABS_API_KEY", "").strip()
    if env_key:
        return env_key
    try:
        from tools.chatter.dotenv import find_dotenv, parse_dotenv_file
    except ImportError:
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
        from tools.chatter.dotenv import find_dotenv, parse_dotenv_file
    p = find_dotenv()
    if p is None:
        return ""
    return parse_dotenv_file(p).get("DOWAGER_CHATTER_ELEVENLABS_API_KEY", "").strip()


def synthesize_once(
    *,
    api_key: str,
    voice_id: str,
    text: str,
    model: str = DEFAULT_MODEL,
    endpoint: str = DEFAULT_ENDPOINT,
    output_format: str = DEFAULT_OUTPUT_FORMAT,
    timeout_seconds: float = 20.0,
) -> bytes:
    """Make one ElevenLabs TTS call. Returns the raw response body."""
    url = (
        endpoint.rstrip("/")
        + f"/v1/text-to-speech/{voice_id}?output_format={output_format}"
    )
    body = (
        b'{"text":' + _json_str(text).encode("utf-8")
        + b',"model_id":' + _json_str(model).encode("utf-8")
        + b'}'
    )
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json",
        "Accept": "audio/wav",
        "User-Agent": "DowagerMod-Chatter-Audition",
    }
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout_seconds) as resp:
        return resp.read()


def _json_str(s: str) -> str:
    """Minimal JSON string encoder (avoids importing json for one call)."""
    out = ['"']
    for ch in s:
        if ch == '"':
            out.append('\\"')
        elif ch == "\\":
            out.append("\\\\")
        elif ch == "\n":
            out.append("\\n")
        elif ch == "\r":
            out.append("\\r")
        elif ch == "\t":
            out.append("\\t")
        elif ord(ch) < 0x20:
            out.append("\\u%04x" % ord(ch))
        else:
            out.append(ch)
    out.append('"')
    return "".join(out)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--voice-id", required=True, help="ElevenLabs voice ID")
    p.add_argument("--text", required=True, help="Text to synthesize")
    p.add_argument("--model", default=DEFAULT_MODEL,
                   help=f"Model ID (default: {DEFAULT_MODEL})")
    p.add_argument("--api-key", default="",
                   help="ElevenLabs API key (overrides env/.env)")
    p.add_argument("--endpoint", default=DEFAULT_ENDPOINT,
                   help=f"API endpoint (default: {DEFAULT_ENDPOINT})")
    p.add_argument("--output", default="",
                   help="Output WAV path (default: TEMP/dowager_audition_<ts>.wav)")
    p.add_argument("--no-play", action="store_true",
                   help="Do not open the WAV in the default player after writing")
    p.add_argument("--timeout", type=float, default=20.0,
                   help="HTTP timeout in seconds (default: 20)")
    args = p.parse_args(argv)

    key = _resolve_api_key(args.api_key)
    if not key:
        print("ERROR: no ElevenLabs API key found.\n"
              "  Pass --api-key, or set DOWAGER_CHATTER_ELEVENLABS_API_KEY in shell,\n"
              "  or add DOWAGER_CHATTER_ELEVENLABS_API_KEY=... to <repo>\\.env",
              file=sys.stderr)
        return 2

    out_path = Path(args.output) if args.output else (
        Path(tempfile.gettempdir())
        / f"dowager_audition_{args.model}_{int(time.time())}.wav"
    )

    print(f"[audition] voice_id={args.voice_id} model={args.model} chars={len(args.text)}")
    t0 = time.perf_counter()
    try:
        raw = synthesize_once(
            api_key=key,
            voice_id=args.voice_id,
            text=args.text,
            model=args.model,
            endpoint=args.endpoint,
            timeout_seconds=args.timeout,
        )
    except urllib.error.HTTPError as exc:
        elapsed = int((time.perf_counter() - t0) * 1000)
        body = ""
        try:
            body = exc.read().decode("utf-8", errors="replace")[:300]
        except Exception:
            pass
        print(f"ERROR: HTTP {exc.code} after {elapsed}ms: {body}", file=sys.stderr)
        return 1
    except Exception as exc:
        elapsed = int((time.perf_counter() - t0) * 1000)
        print(f"ERROR: request failed after {elapsed}ms: {exc}", file=sys.stderr)
        return 1
    elapsed = int((time.perf_counter() - t0) * 1000)
    print(f"[audition] got {len(raw)} bytes in {elapsed}ms")

    # ElevenLabs at output_format=pcm_24000 returns raw little-endian
    # 16-bit mono PCM with no header. Wrap it so the OS can play it.
    if raw[:4] == b"RIFF":
        wav_bytes = raw
    else:
        wav_bytes = wrap_pcm_as_wav(raw, sample_rate=DEFAULT_SAMPLE_RATE)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(wav_bytes)
    print(f"[audition] wrote {out_path}")

    if not args.no_play:
        try:
            os.startfile(str(out_path))  # Windows
            print("[audition] opened in default player")
        except AttributeError:
            print("[audition] --no-play not specified but os.startfile unavailable on this OS; skipping playback")
        except Exception as exc:
            print(f"[audition] could not open player: {exc}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
