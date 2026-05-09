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

    Some leader types have artifacts (BTG mod suffix) or generic names that
    aren't the actual leader; override those explicitly.
    """
    overrides = {
        "LEADER_CHINESE_LEADER": "Mao Zedong",
        "LEADER_GERONIMO_BTG": "Geronimo",
        "LEADER_SALAMASINA_BTG": "Salamasina",
        "LEADER_WANGKON": "Wang Kon",
        "LEADER_CASIMIR": "Casimir III",
        "LEADER_LOUIS_XIV": "Louis XIV",
        "LEADER_PACAL": "Pacal II",
        "LEADER_MEHMED": "Mehmed II",
        "LEADER_RAMESSES": "Ramesses II",
        "LEADER_DARIUS": "Darius I",
        "LEADER_FREDERICK": "Frederick the Great",
        "LEADER_PETER": "Peter the Great",
        "LEADER_CYRUS": "Cyrus the Great",
        "LEADER_CATHERINE": "Catherine the Great",
        "LEADER_QIN_SHI_HUANG": "Qin Shi Huang",
        "LEADER_HUAYNA_CAPAC": "Huayna Capac",
        "LEADER_FRANKLIN_ROOSEVELT": "Franklin Roosevelt",
        "LEADER_DE_GAULLE": "Charles de Gaulle",
        "LEADER_HAILE_SELASSIE": "Haile Selassie",
        "LEADER_HAMMURABI": "Hammurabi",
        "LEADER_KUBLAI_KHAN": "Kublai Khan",
        "LEADER_GENGHIS_KHAN": "Genghis Khan",
        "LEADER_ENRICO_DANDOLO": "Enrico Dandolo",
        "LEADER_REGINALD_ENDICOTT_BARCLAY": "Reginald Endicott Barclay",
        "LEADER_ZARA_YAQOB": "Zara Yaqob",
        "LEADER_DOWAGER_COUNTESS": "Dowager Countess",
        "LEADER_SULEIMAN": "Suleiman the Magnificent",
        "LEADER_ELIZABETH": "Elizabeth I",
        "LEADER_AUGUSTUS": "Augustus Caesar",
        "LEADER_JUSTINIAN": "Justinian I",
        "LEADER_ISABELLA": "Isabella I",
        "LEADER_JOAO": "Joao II",
        "LEADER_SURYAVARMAN": "Suryavarman II",
        "LEADER_TOKUGAWA": "Tokugawa Ieyasu",
        "LEADER_RAGNAR": "Ragnar Lothbrok",
        "LEADER_SITTING_BULL": "Sitting Bull",
        "LEADER_MANSA_MUSA": "Mansa Musa",
        "LEADER_WILLEM": "Willem van Oranje",
        "LEADER_HANNIBAL": "Hannibal Barca",
    }
    if leader_type in overrides:
        return overrides[leader_type]
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
    parser.add_argument("--no-play", action="store_true",
                        help="Skip live local playback. Default: play each WAV as it is synthesized.")
    args = parser.parse_args()

    print()
    print(f"{CYAN}===== DowagerMod Leader Voice Audit ====={RESET}")
    print()

    leaders = list_leaders(LEADER_XML)
    if args.leader:
        wanted_raw = [l.lower().strip() for l in args.leader]
        wanted_norm = {re.sub(r"[^a-z0-9]", "", w) for w in wanted_raw}
        def matches(t: str, n: str) -> bool:
            if t.lower() in wanted_raw or n.lower() in wanted_raw:
                return True
            t_norm = re.sub(r"[^a-z0-9]", "", t.lower())
            n_norm = re.sub(r"[^a-z0-9]", "", n.lower())
            return t_norm in wanted_norm or n_norm in wanted_norm
        leaders = [(t, n) for t, n in leaders if matches(t, n)]
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

    # Resolve each leader to (display_name, voice_spec, is_explicit_pick).
    # Voice lookup tries the override name first, falls back to the bare
    # title (LEADER_CATHERINE -> 'Catherine') so map entries stay simple.
    rows = []
    for leader_type, name in leaders:
        bare = leader_type
        if bare.startswith("LEADER_"):
            bare = bare[len("LEADER_"):]
        bare = " ".join(p.capitalize() for p in bare.split("_") if p)
        norm = normalize_name(name)
        bare_norm = normalize_name(bare)
        is_explicit = norm in explicit_map or bare_norm in explicit_map
        if norm in explicit_map:
            spec = vp.pick_spec(name)
        elif bare_norm in explicit_map:
            spec = vp.pick_spec(bare)
        else:
            spec = vp.pick_spec(name)  # auto-fallback
        rows.append((leader_type, name, spec, is_explicit))

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
        for _, name, spec, _ in fallback:
            print(f"    - {name:30}  ->  {spec.voice}  (auto)")
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
    if not args.no_play:
        print(f"  playback:    LIVE (playing each WAV through default audio device)")
    print()

    # Probe winsound up front; falls back to ffplay if available.
    play_method = None
    if not args.no_play:
        try:
            import winsound  # noqa: F401
            play_method = "winsound"
        except ImportError:
            import shutil
            if shutil.which("ffplay"):
                play_method = "ffplay"
            else:
                print(f"{YELLOW}  warning: no winsound (non-Windows) and no ffplay; live playback disabled{RESET}")

    def _play_wav_blocking(path: Path) -> None:
        """Play the WAV synchronously through the default audio device."""
        if play_method == "winsound":
            import winsound
            try:
                winsound.PlaySound(str(path), winsound.SND_FILENAME)
            except Exception as exc:  # noqa: BLE001
                print(f"{YELLOW}    (playback failed: {exc}){RESET}")
        elif play_method == "ffplay":
            import subprocess
            try:
                subprocess.run(
                    ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", str(path)],
                    check=False,
                )
            except Exception as exc:  # noqa: BLE001
                print(f"{YELLOW}    (playback failed: {exc}){RESET}")

    from tools.chatter.azure_speech_client import AzureSpeechClient, SpeechAuthError, SpeechApiError
    sc = AzureSpeechClient(
        endpoint=endpoint, key=key,
        default_voice="en-US-AriaNeural",
        request_timeout_seconds=15.0,
        daily_char_cap=100000,
    )

    passed = 0
    failed: list[tuple[str, str, str]] = []
    for idx, (leader_type, name, spec, is_explicit) in enumerate(rows, start=1):
        voice = spec.voice
        if args.phrase:
            phrase = args.phrase
        else:
            prosody_note = ""
            if spec.rate or spec.pitch:
                bits = []
                if spec.rate:
                    bits.append(f"rate {spec.rate}")
                if spec.pitch:
                    bits.append(f"pitch {spec.pitch}")
                prosody_note = f" with " + ", ".join(bits)
            phrase = f"Hello, I am {name}. My voice is {voice}{prosody_note}."
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
                result = sc.synthesize(phrase, voice=voice, rate=spec.rate, pitch=spec.pitch)
                elapsed_ms = int((time.perf_counter() - t0) * 1000)
                out_path.write_bytes(result.audio_bytes)
                retry_note = f" (retry {attempt})" if attempt > 0 else ""
                pros_note = ""
                if spec.rate or spec.pitch:
                    pros_note = f"  [{spec.rate or '-'} / {spec.pitch or '-'}]"
                print(f"  {GREEN}OK{RESET}  {marker}  {name:28} -> {out_path.name}  ({elapsed_ms}ms){pros_note}{retry_note}")
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
            continue
        # Live play (blocking — waits for the WAV to finish before continuing)
        if not args.no_play and play_method is not None:
            _play_wav_blocking(out_path)

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
