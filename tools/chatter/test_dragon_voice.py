"""Pass A sniff test for Dragon HD Omni and elderly-British voice candidates.

Tries multiple voice names against the configured Azure Speech endpoint and
saves WAVs to the session files dir. Lets us hear which voices actually
respond on our subscription tier, and which one sounds closest to an
elderly British aristocrat out-of-the-box.

Usage:
    python tools\chatter\test_dragon_voice.py [--out OUTDIR]

Requires env: DOWAGER_CHATTER_SPEECH_ENDPOINT, DOWAGER_CHATTER_SPEECH_KEY.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

# Insert this dir so the script works regardless of cwd
sys.path.insert(0, str(Path(__file__).resolve().parent))

from azure_speech_client import AzureSpeechClient, SpeechApiError, SpeechAuthError


PHRASE = (
    "I wonder your mother didn't warn you about playing cards with strangers. "
    "One ought never to underestimate the very old."
)

CANDIDATES = [
    # Headline candidate from the research: Dragon HD Omni "mature queen"
    ("dragon_sandoverture", "en-gb-sandoverture:DragonHDOmniLatestNeural", "-15%", "-3%"),
    # Variant naming the API sometimes uses (just in case)
    ("dragon_sandoverture_alt", "en-GB-SandovertureDragonHDLatestNeural", "-15%", "-3%"),
    # Olivia: alternate Sonia-tier female, sometimes reads slightly older
    ("olivia_aged", "en-GB-OliviaNeural", "-18%", "-10%"),
    # Sonia current setup (control)
    ("sonia_current", "en-GB-SoniaNeural", "-18%", "-10%"),
    # Libby: another Azure en-GB female, more matronly tone
    ("libby_aged", "en-GB-LibbyNeural", "-18%", "-10%"),
    # Hollie: alternate
    ("hollie_aged", "en-GB-HollieNeural", "-18%", "-10%"),
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out",
        default=r"C:\Users\hasiegel\.copilot\session-state\c8a88e61-5461-4e5b-a4ab-2dff0b259c4c\files",
        help="Directory to write WAVs to.",
    )
    args = parser.parse_args()

    endpoint = os.environ.get("DOWAGER_CHATTER_SPEECH_ENDPOINT", "").strip()
    key = os.environ.get("DOWAGER_CHATTER_SPEECH_KEY", "").strip()
    if not endpoint or not key:
        print("FAIL: DOWAGER_CHATTER_SPEECH_ENDPOINT / DOWAGER_CHATTER_SPEECH_KEY not set")
        return 2

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    sc = AzureSpeechClient(endpoint=endpoint, key=key, daily_char_cap=200000)

    results = []
    for label, voice, rate, pitch in CANDIDATES:
        out_path = out_dir / f"dowager_passA_{label}.wav"
        print(f"[try] {label}: voice={voice} rate={rate} pitch={pitch}")
        try:
            res = sc.synthesize(PHRASE, voice=voice, rate=rate, pitch=pitch, locale="en-GB")
            out_path.write_bytes(res.audio_bytes)
            size_kb = len(res.audio_bytes) / 1024
            print(f"  OK  {size_kb:.1f} KB in {res.latency_ms} ms -> {out_path.name}")
            results.append((label, voice, "OK", out_path.name, ""))
        except (SpeechApiError, SpeechAuthError) as exc:
            msg = str(exc)
            print(f"  FAIL  {msg}")
            results.append((label, voice, "FAIL", "", msg))

    # Summary
    print()
    print("=" * 78)
    print("PASS A RESULTS:")
    print("=" * 78)
    for label, voice, status, fname, err in results:
        marker = "OK  " if status == "OK" else "FAIL"
        line = f"  {marker}  {label:30s} {voice}"
        print(line)
        if err:
            print(f"           -> {err[:120]}")

    ok_count = sum(1 for r in results if r[2] == "OK")
    print()
    print(f"{ok_count}/{len(results)} candidates synthesized successfully.")
    print(f"WAVs saved to: {out_dir}")
    print()
    if ok_count > 0:
        print("Next: listen to the WAVs and tell which voice sounds closest to")
        print("an elderly British aristocrat. We'll then layer FFmpeg aging on top.")

    return 0 if ok_count > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
