"""Validate that every voice in leader_voices.json actually exists and
works against the configured Azure Speech endpoint.

Synthesizes a 1-line test phrase with each unique voice. Prints PASS/FAIL
per voice. Useful after editing leader_voices.json to catch any voice
names that have been retired by Azure or that don't exist in your region.

Usage:

    # .env must have DOWAGER_CHATTER_SPEECH_ENDPOINT and
    # DOWAGER_CHATTER_SPEECH_KEY populated.
    python tools/chatter/test_all_voices.py

    # Or only test specific leaders:
    python tools/chatter/test_all_voices.py --leader Hannibal --leader Catherine

Exit 0 if all voices passed; non-zero if any failed.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
RESET = "\033[0m"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--leader", action="append", default=[],
                        help="Test only the named leader(s). Repeatable. Default: test ALL unique voices.")
    parser.add_argument("--text", default="Greetings from history.",
                        help="Test phrase to synthesize. Default short to keep cost low.")
    args = parser.parse_args()

    try:
        from tools.chatter.dotenv import load_dotenv
        loaded = load_dotenv()
        if loaded:
            print(f"  (loaded env from {loaded})")
    except Exception as exc:  # noqa: BLE001
        print(f"  (warning: dotenv loader failed: {exc})")

    endpoint = os.environ.get("DOWAGER_CHATTER_SPEECH_ENDPOINT", "").strip()
    key = os.environ.get("DOWAGER_CHATTER_SPEECH_KEY", "").strip()
    if not endpoint or not key:
        print(f"{RED}FAIL: DOWAGER_CHATTER_SPEECH_ENDPOINT / DOWAGER_CHATTER_SPEECH_KEY not set in .env{RESET}")
        return 2

    voices_path = Path(__file__).resolve().parent / "leader_voices.json"
    with voices_path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    full_map: dict = data.get("map") or {}

    if args.leader:
        wanted = {l.lower().replace(" ", "").replace("-", "").replace("_", "") for l in args.leader}
        filtered = {k: v for k, v in full_map.items() if k in wanted}
        if not filtered:
            print(f"{RED}FAIL: none of {args.leader!r} matched any leader in the map{RESET}")
            return 2
    else:
        filtered = full_map

    # Reverse-index: voice -> [leader aliases that use it]
    voice_to_leaders: dict[str, list[str]] = {}
    for leader, voice in filtered.items():
        voice_to_leaders.setdefault(voice, []).append(leader)

    print(f"  endpoint:    {endpoint}")
    print(f"  voices:      {len(voice_to_leaders)} unique")
    print(f"  test phrase: {args.text!r}")
    print()

    from tools.chatter.azure_speech_client import AzureSpeechClient, SpeechApiError, SpeechAuthError
    sc = AzureSpeechClient(
        endpoint=endpoint, key=key,
        default_voice="en-US-AriaNeural",
        request_timeout_seconds=15.0,
        daily_char_cap=100000,
    )

    passed: list[str] = []
    failed: list[tuple[str, list[str], str]] = []
    for voice, leaders in sorted(voice_to_leaders.items()):
        leader_label = ",".join(sorted(set(leaders))[:2])
        if len(leaders) > 2:
            leader_label += f"+{len(leaders) - 2}"
        # Retry up to 3 times if Azure throttles us (free tier has aggressive
        # rate limits). Each retry waits longer.
        attempt_err: str | None = None
        for attempt in range(3):
            if attempt > 0:
                time.sleep(2.0 * attempt)
            try:
                t0 = time.perf_counter()
                sc.synthesize(args.text, voice=voice)
                elapsed_ms = int((time.perf_counter() - t0) * 1000)
                retry_note = f" (retry {attempt})" if attempt > 0 else ""
                print(f"  {GREEN}PASS{RESET}  {voice:48} ({elapsed_ms:4d}ms){retry_note} [{leader_label}]")
                passed.append(voice)
                attempt_err = None
                break
            except SpeechAuthError as exc:
                print(f"{RED}FATAL: Speech auth failure ({exc}). Aborting.{RESET}")
                return 3
            except (SpeechApiError, Exception) as exc:  # noqa: BLE001
                attempt_err = str(exc)[:120]
                # Only retry on 429 throttle; other errors are persistent
                if "429" not in attempt_err and "throttle" not in attempt_err.lower():
                    break
        if attempt_err is not None:
            print(f"  {RED}FAIL{RESET}  {voice:48}        [{leader_label}]")
            print(f"        -> {attempt_err}")
            failed.append((voice, leaders, attempt_err))
        # Tiny pacing so Azure free tier doesn't throttle the next voice
        time.sleep(0.3)

    print()
    print("===== Summary =====")
    print(f"  Passed: {len(passed)}")
    print(f"  Failed: {len(failed)}")
    if failed:
        print()
        print(f"{YELLOW}Voices that need to be replaced in leader_voices.json:{RESET}")
        for voice, leaders, err in failed:
            print(f"  - {voice}  used by: {', '.join(sorted(set(leaders)))}")
        return 1
    print(f"{GREEN}All voices verified against your Azure Speech resource.{RESET}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
