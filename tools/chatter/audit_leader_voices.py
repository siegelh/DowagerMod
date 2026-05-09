"""Audit DowagerMod leader voiceover coverage + generate audition WAVs.

Two functions in one script:

1. AUDIT: Reads CIV4LeaderHeadInfos.xml, lists every leader, reports which
   ones have an explicit voice mapping in leader_voices.json and which fall
   back to the gendered auto-pool.

2. AUDITION (default): For each leader, synthesize a single phrase
   ("Hello, I am <Name>. My voice is <voice-name>.") via Azure Speech and
   save as a WAV in voice_audit/<NN>-<Leader>-<voice>.wav. You can browse
   the folder, sort by name, play through them, and tell me which voices
   feel wrong so we can swap them.

Usage:

    # Read leader XML, generate one WAV per leader (~60 calls, takes ~1 min)
    python tools/chatter/audit_leader_voices.py

    # Skip audio generation, just print the audit report
    python tools/chatter/audit_leader_voices.py --no-audio

    # Limit to specific leaders
    python tools/chatter/audit_leader_voices.py --leader Lincoln --leader Hannibal

    # Custom phrase
    python tools/chatter/audit_leader_voices.py --phrase "Tremble before me, mortal."
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
RESET = "\033[0m"

LEADER_XML = (
    Path("CoreFiles") / "Sid Meier's Civilization IV Beyond the Sword"
    / "Beyond the Sword" / "Assets" / "XML" / "Civilizations"
    / "CIV4LeaderHeadInfos.xml"
)


def title_from_leader_type(leader_type: str) -> str:
    """LEADER_DOWAGER_COUNTESS -> 'Dowager Countess'.
    LEADER_REGINALD_ENDICOTT_BARCLAY -> 'Reginald Endicott Barclay'.
    """
    s = leader_type
    if s.startswith("LEADER_"):
        s = s[len("LEADER_"):]
    parts = s.split("_")
    return " ".join(p.capitalize() for p in parts if p)


def list_leaders(xml_path: Path) -> list[tuple[str, str]]:
    """Returns list of (leader_type, display_name) tuples from CIV4LeaderHeadInfos.xml.
    Skips LEADER_BARBARIAN since they don't speak.
    """
    if not xml_path.is_file():
        print(f"{RED}FAIL: {xml_path} not found. Run from repo root.{RESET}")
        sys.exit(2)
    tree = ET.parse(str(xml_path))
    root = tree.getroot()
    out = []
    for li in root.iter():
        if li.tag.endswith("Type"):
            text = (li.text or "").strip()
            if text.startswith("LEADER_") and text != "LEADER_BARBARIAN":
                out.append((text, title_from_leader_type(text)))
    # de-dup while preserving order
    seen = set()
    deduped = []
    for t, n in out:
        if t not in seen:
            seen.add(t)
            deduped.append((t, n))
    return deduped


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-audio", action="store_true",
                        help="Skip audio generation; just print the coverage audit report.")
    parser.add_argument("--leader", action="append", default=[],
                        help="Limit to named leader(s). Repeatable.")
    parser.add_argument("--phrase", default=None,
                        help="Custom test phrase. Default: 'Hello, I am <Name>. My voice is <voice>.'")
    parser.add_argument("--out-dir", default="voice_audit",
                        help="Directory to save WAVs into (default: voice_audit/).")
    args = parser.parse_args()

    print()
    print(f"{CYAN}===== DowagerMod Leader Voice Audit ====={RESET}")
    print()

    leaders = list_leaders(LEADER_XML)
    if args.leader:
        wanted = {l.lower() for l in args.leader}
        leaders = [(t, n) for t, n in leaders if n.lower() in wanted or t.lower() in wanted]
        if not leaders:
            print(f"{RED}FAIL: no leaders matched {args.leader!r}{RESET}")
            return 2
    print(f"  {len(leaders)} leaders found in {LEADER_XML.name}")

    # Load voice picker
    from tools.chatter.voice_picker import VoicePicker, normalize_name
    vp = VoicePicker()
    # Direct access to the curated map for "is this an explicit pick?" reporting
    import json
    voices_path = Path(__file__).resolve().parent / "leader_voices.json"
    with voices_path.open("r", encoding="utf-8") as fh:
        voices_data = json.load(fh)
    explicit_map: dict = voices_data.get("map") or {}

    # Resolve each leader to (display_name, voice, is_explicit_pick)
    rows = []
    for leader_type, name in leaders:
        norm = normalize_name(name)
        is_explicit = norm in explicit_map
        voice = vp.pick_voice(name)
        rows.append((leader_type, name, voice, is_explicit))

    # Coverage report
    print()
    print(f"{CYAN}--- Coverage Report ---{RESET}")
    explicit = [r for r in rows if r[3]]
    fallback = [r for r in rows if not r[3]]
    print(f"  Explicit picks:  {len(explicit)}")
    print(f"  Fallback (auto): {len(fallback)}")
    if fallback:
        print()
        print(f"{YELLOW}  These leaders have NO explicit voice mapping; using auto-fallback:{RESET}")
        for _, name, voice, _ in fallback:
            print(f"    - {name:30}  ->  {voice}  (auto)")
        print()
        print(f"{YELLOW}  To fix: add entries to tools/chatter/leader_voices.json with the{RESET}")
        print(f"{YELLOW}  normalized leader name as key (lowercase + alphanumeric only).{RESET}")

    if args.no_audio:
        print()
        print(f"{CYAN}===== Done (--no-audio) ====={RESET}")
        return 0

    # Audio generation
    print()
    print(f"{CYAN}--- Generating audition WAVs ---{RESET}")
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
        print(f"{RED}FAIL: DOWAGER_CHATTER_SPEECH_ENDPOINT / DOWAGER_CHATTER_SPEECH_KEY missing.{RESET}")
        print(f"{YELLOW}  Re-run with --no-audio to just see the coverage report.{RESET}")
        return 2

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"  output dir:  {out_dir.resolve()}")
    print(f"  voices:      {len(rows)} unique calls")
    print(f"  pacing:      0.4s between calls (avoid free-tier throttle)")
    print()

    from tools.chatter.azure_speech_client import AzureSpeechClient, SpeechAuthError, SpeechApiError
    sc = AzureSpeechClient(
        endpoint=endpoint, key=key,
        default_voice="en-US-AriaNeural",
        request_timeout_seconds=15.0,
        daily_char_cap=100000,
    )

    passed = 0
    failed: list[tuple[str, str, str]] = []
    for idx, (leader_type, name, voice, is_explicit) in enumerate(rows, start=1):
        if args.phrase:
            phrase = args.phrase
        else:
            phrase = f"Hello, I am {name}. My voice is {voice}."
        # Sanitize leader name for filename
        safe_name = re.sub(r"[^A-Za-z0-9]+", "-", name).strip("-")
        out_path = out_dir / f"{idx:02d}-{safe_name}-{voice}.wav"
        marker = "  " if is_explicit else "AUTO"
        # Pace
        if idx > 1:
            time.sleep(0.4)
        # Synthesize with up to 2 retries on throttle
        attempt_err: str | None = None
        for attempt in range(3):
            if attempt > 0:
                time.sleep(2.0 * attempt)
            try:
                t0 = time.perf_counter()
                result = sc.synthesize(phrase, voice=voice)
                elapsed_ms = int((time.perf_counter() - t0) * 1000)
                out_path.write_bytes(result.audio_bytes)
                retry_note = f" (retry {attempt})" if attempt > 0 else ""
                print(f"  {GREEN}OK{RESET}  {marker}  {name:28} -> {out_path.name}  ({elapsed_ms}ms){retry_note}")
                passed += 1
                attempt_err = None
                break
            except SpeechAuthError as exc:
                print(f"{RED}FATAL: Speech auth failure: {exc}{RESET}")
                return 3
            except (SpeechApiError, Exception) as exc:  # noqa: BLE001
                attempt_err = str(exc)[:140]
                if "429" not in attempt_err and "throttle" not in attempt_err.lower():
                    break
        if attempt_err is not None:
            print(f"  {RED}FAIL{RESET}  {marker}  {name:28} voice={voice}")
            print(f"        -> {attempt_err}")
            failed.append((name, voice, attempt_err))

    print()
    print(f"{CYAN}===== Summary ====={RESET}")
    print(f"  Generated: {passed} WAV files in {out_dir.resolve()}")
    if failed:
        print(f"{RED}  Failed: {len(failed)}{RESET}")
        for name, voice, err in failed:
            print(f"    - {name:28} voice={voice}")
        print(f"{YELLOW}  Open leader_voices.json and replace those voices, then re-run.{RESET}")
    print()
    print(f"{CYAN}Listen to the WAVs in alphabetical order:{RESET}")
    print(f"  start {out_dir.resolve()}")
    print()
    print(f"{CYAN}If a leader sounds wrong, ping me with: 'Change Leader X from voice Y to something else'.{RESET}")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
