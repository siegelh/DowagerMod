"""Full-flow chatter demo: simulate an in-game trigger, get the LLM to
generate a multi-line conversation, synthesize each line with that
speaker's voice + prosody, and play the audio locally.

This is exactly what the in-game daemon does when a real Civ4 trigger
fires, except:
  - The trigger is fabricated by command-line args.
  - Audio plays through your default speakers instead of the Discord bot.
  - All artifacts (request JSON, response JSON, individual WAVs, optional
    combined WAV) are saved to demo_flow/ so you can inspect them.

Usage:

    # Default: a DECLARE_WAR exchange between Lincoln and Victoria
    python tools/chatter/demo_full_flow.py

    # Pick the trigger + speakers
    python tools/chatter/demo_full_flow.py \
        --trigger BACKSTABBED \
        --speaker Stalin --target Churchill

    # See list of supported triggers
    python tools/chatter/demo_full_flow.py --list-triggers

    # Don't play audio (just generate WAVs)
    python tools/chatter/demo_full_flow.py --no-play

What you'll see:
  Step 1: shows the synthesized LLM REQUEST payload (the JSON the game
          would have written to disk for the sidecar).
  Step 2: shows the actual SSML system prompt sent to Foundry.
  Step 3: shows the LLM RESPONSE (the multi-line JSON the model returned).
  Step 4: synthesizes + plays each line in order, with the right voice +
          prosody for each speaker.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import uuid
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

# Force UTF-8 stdout so Cyrillic / Hanzi / Arabic / etc. print without
# UnicodeEncodeError on Windows cp1252 consoles.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:  # noqa: BLE001
    pass

GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
DIM = "\033[2m"
RESET = "\033[0m"


# Supported triggers and their default mode/multi_turn flag (mirrors what
# the game-side CvLeaderChatter.py would emit). Only a subset of all
# triggers — focused on the multi-turn ones since they're the most
# interesting to demo.
DEMO_TRIGGERS = {
    "DECLARE_WAR":              {"mode": "directed",  "multi_turn": True,  "speaker_role": "attacker"},
    "BACKSTABBED":              {"mode": "directed",  "multi_turn": True,  "speaker_role": "defender"},
    "PEACE_TREATY":             {"mode": "directed",  "multi_turn": True,  "speaker_role": "either"},
    "FIRST_CONTACT":            {"mode": "directed",  "multi_turn": True,  "speaker_role": "explorer"},
    "CITY_CAPTURED":            {"mode": "directed",  "multi_turn": True,  "speaker_role": "conqueror"},
    "CITY_RAZED":               {"mode": "directed",  "multi_turn": True,  "speaker_role": "razer"},
    "PLAYER_ELIMINATED_GLOAT":  {"mode": "directed",  "multi_turn": True,  "speaker_role": "victor"},
    "PLAYER_ELIMINATED_LAST_WORDS": {"mode": "directed", "multi_turn": True, "speaker_role": "loser"},
    "RELIGION_FOUNDED":         {"mode": "broadcast", "multi_turn": False},
    "WONDER_BUILT":             {"mode": "broadcast", "multi_turn": False},
    "GOLDEN_AGE":               {"mode": "broadcast", "multi_turn": False},
    "FIRST_TO_TECH":            {"mode": "broadcast", "multi_turn": False},
}


def fake_player_info(player_id: int, leader_name: str, civ: str = "") -> dict:
    """Build a fake _player_info dict (mimics game-side CvLeaderChatter.py)."""
    if not civ:
        # Reasonable default civilization for each known leader
        civ_defaults = {
            "Lincoln": "America", "Washington": "America", "Franklin Roosevelt": "America",
            "Victoria": "England", "Elizabeth": "England", "Churchill": "England",
            "Catherine": "Russia", "Catherine the Great": "Russia",
            "Peter": "Russia", "Peter the Great": "Russia", "Stalin": "Russia",
            "Napoleon": "France", "Louis XIV": "France", "Charles de Gaulle": "France",
            "Bismarck": "Germany", "Frederick": "Germany", "Frederick the Great": "Germany",
            "Charlemagne": "Holy Roman Empire",
            "Caesar": "Rome", "Julius Caesar": "Rome", "Augustus": "Rome",
            "Justinian": "Byzantium",
            "Mansa Musa": "Mali", "Hannibal": "Carthage", "Hannibal Barca": "Carthage",
            "Genghis Khan": "Mongolia", "Kublai Khan": "Mongolia",
            "Saladin": "Arabia", "Mehmed": "Ottomans", "Suleiman the Magnificent": "Ottomans",
            "Cyrus": "Persia", "Cyrus the Great": "Persia", "Darius": "Persia",
            "Hatshepsut": "Egypt", "Ramesses": "Egypt", "Ramesses II": "Egypt",
            "Hammurabi": "Babylon", "Gilgamesh": "Sumeria",
            "Pericles": "Greece", "Alexander": "Greece",
            "Mao Zedong": "China", "Qin Shi Huang": "China",
            "Tokugawa": "Japan", "Tokugawa Ieyasu": "Japan",
            "Asoka": "India", "Gandhi": "India",
            "Suryavarman": "Khmer", "Suryavarman II": "Khmer",
            "Wang Kon": "Korea",
            "Isabella": "Spain", "Montezuma": "Aztec",
            "Joao": "Portugal", "Joao II": "Portugal",
            "Ragnar": "Vikings", "Ragnar Lothbrok": "Vikings",
            "Boudica": "Celts", "Brennus": "Celts",
            "Shaka": "Zulu", "Haile Selassie": "Ethiopia", "Zara Yaqob": "Ethiopia",
            "Sitting Bull": "Native America", "Geronimo": "Apache",
            "Huayna Capac": "Inca", "Pacal": "Maya", "Pacal II": "Maya",
            "Willem van Oranje": "Netherlands", "Casimir": "Poland", "Casimir III": "Poland",
            "Salamasina": "Polynesia", "Enrico Dandolo": "Venice",
            "Dowager Countess": "Britain", "Reginald Endicott Barclay": "Federation",
        }
        civ = civ_defaults.get(leader_name, "Unknown")
    return {
        "player_id": player_id,
        "leader_name": leader_name,
        "civ_short_name": civ,
        "score": 100,
        "is_barbarian": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trigger", default="DECLARE_WAR",
                        choices=sorted(DEMO_TRIGGERS.keys()),
                        help="Which trigger to simulate. Default: DECLARE_WAR.")
    parser.add_argument("--speaker", default="Lincoln",
                        help="Speaker leader name (e.g. 'Lincoln', 'Catherine the Great').")
    parser.add_argument("--target", default="Victoria",
                        help="Target leader name (for directed triggers). Ignored for broadcasts.")
    parser.add_argument("--speaker-civ", default="",
                        help="Override speaker civilization. Default: best guess from leader name.")
    parser.add_argument("--target-civ", default="",
                        help="Override target civilization. Default: best guess from target name.")
    parser.add_argument("--game-turn", type=int, default=120,
                        help="Pretend game turn (affects era hint). Default 120.")
    parser.add_argument("--era", default="Renaissance",
                        help="Pretend era. Default Renaissance.")
    parser.add_argument("--n-lines", type=int, default=3,
                        help="Number of conversation lines for multi-turn triggers. Default 3.")
    parser.add_argument("--no-play", action="store_true",
                        help="Skip audio playback. Just synthesize and save WAVs.")
    parser.add_argument("--out-dir", default="demo_flow",
                        help="Where to save artifacts. Default: demo_flow/.")
    parser.add_argument("--list-triggers", action="store_true",
                        help="List supported triggers and exit.")
    parser.add_argument("--native", action="store_true",
                        help="Native-tongue mode: LLM also generates translations into each speaker's native language; TTS speaks the native version, you read English.")
    args = parser.parse_args()

    if args.list_triggers:
        print(f"{CYAN}Supported triggers:{RESET}")
        for name, meta in DEMO_TRIGGERS.items():
            mt = "multi-turn" if meta["multi_turn"] else "single-line"
            print(f"  {name:30}  ({meta['mode']}, {mt})")
        return 0

    print()
    print(f"{CYAN}===== DowagerMod Chatter Full-Flow Demo ====={RESET}")
    print()

    # Load env
    try:
        from tools.chatter.dotenv import load_dotenv
        loaded = load_dotenv()
        if loaded:
            print(f"  (loaded env from {loaded})")
    except Exception as exc:  # noqa: BLE001
        print(f"  (warning: dotenv loader failed: {exc})")

    # Validate config
    foundry_endpoint = os.environ.get("DOWAGER_CHATTER_ENDPOINT", "").strip()
    foundry_key = os.environ.get("DOWAGER_CHATTER_API_KEY", "").strip()
    foundry_deployment = os.environ.get("DOWAGER_CHATTER_DEPLOYMENT", "gpt-5.4-mini").strip()
    foundry_apiver = os.environ.get("DOWAGER_CHATTER_API_VERSION", "2024-12-01-preview").strip()
    speech_endpoint = os.environ.get("DOWAGER_CHATTER_SPEECH_ENDPOINT", "").strip()
    speech_key = os.environ.get("DOWAGER_CHATTER_SPEECH_KEY", "").strip()
    speech_default_voice = os.environ.get("DOWAGER_CHATTER_SPEECH_VOICE", "en-US-AriaNeural").strip()
    if not foundry_endpoint or not foundry_key:
        print(f"{RED}FAIL: Foundry endpoint/key missing in .env{RESET}")
        return 2
    if not speech_endpoint or not speech_key:
        print(f"{RED}FAIL: Speech endpoint/key missing in .env{RESET}")
        return 2

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # ===== Step 1: build the request =====
    trigger_meta = DEMO_TRIGGERS[args.trigger]
    speaker = fake_player_info(0, args.speaker, args.speaker_civ)
    target = fake_player_info(1, args.target, args.target_civ) if trigger_meta["mode"] == "directed" else None

    request_id = str(uuid.uuid4())
    request = {
        "schema": 1,
        "request_id": request_id,
        "session_id": str(uuid.uuid4()),
        "game_turn": args.game_turn,
        "elector_player_id": 0,
        "trigger": args.trigger,
        "mode": trigger_meta["mode"],
        "speaker": speaker,
        "target": target,
        "context": {"era": args.era},
        "multi_turn": trigger_meta["multi_turn"],
        "n_lines": args.n_lines if trigger_meta["multi_turn"] else 1,
        "issued_at_unix": time.time(),
        "ttl_seconds": 60,
    }
    req_path = out_dir / f"req-{request_id}.json"
    req_path.write_text(json.dumps(request, indent=2), encoding="utf-8")
    print(f"{CYAN}--- Step 1: Game-side request payload ---{RESET}")
    print(f"  saved: {req_path.name}")
    print(f"{DIM}{json.dumps(request, indent=2)}{RESET}")
    print()

    # ===== Step 2: build the prompt and show what we're about to ask Foundry =====
    print(f"{CYAN}--- Step 2: SSML prompt to Foundry ---{RESET}")
    from tools.chatter.prompts import build_single_line_prompt, build_multi_turn_prompt
    from tools.chatter.voice_picker import VoicePicker
    vp = VoicePicker(default_voice=speech_default_voice)
    speaker_lang = ""
    target_lang = ""
    if args.native:
        speaker_lang = vp.pick_spec(speaker["leader_name"]).lang
        if target:
            target_lang = vp.pick_spec(target["leader_name"]).lang
        if speaker_lang or target_lang:
            print(f"  {YELLOW}Native mode ON.{RESET} speaker_lang={speaker_lang!r} target_lang={target_lang!r}")
        else:
            print(f"  {YELLOW}Native mode requested but no lang configured for either speaker; reverting to English.{RESET}")
    if request["multi_turn"]:
        sys_msg, user_msg = build_multi_turn_prompt(
            request, native_mode=args.native,
            speaker_native_lang=speaker_lang,
            target_native_lang=target_lang,
        )
    else:
        sys_msg, user_msg = build_single_line_prompt(
            request, native_mode=args.native,
            speaker_native_lang=speaker_lang,
        )
    print(f"  {DIM}SYSTEM:{RESET}")
    for line in sys_msg.splitlines():
        print(f"    {DIM}{line}{RESET}")
    print(f"  {DIM}USER:{RESET}")
    for line in user_msg.splitlines():
        print(f"    {DIM}{line}{RESET}")
    print()

    # ===== Step 3: call Foundry =====
    print(f"{CYAN}--- Step 3: Foundry response ---{RESET}")
    from tools.chatter.azure_client import AzureClient, parse_multi_turn_lines
    client = AzureClient(
        endpoint=foundry_endpoint, api_key=foundry_key,
        deployment=foundry_deployment, request_timeout_seconds=30.0,
        api_version=foundry_apiver,
    )
    t0 = time.perf_counter()
    try:
        max_tok = 400 if request["multi_turn"] else 80
        api_result = client.call_responses(sys_msg, user_msg, max_tokens=max_tok)
    except Exception as exc:  # noqa: BLE001
        print(f"{RED}FAIL: Foundry call raised: {type(exc).__name__}: {exc}{RESET}")
        return 3
    elapsed = int((time.perf_counter() - t0) * 1000)
    print(f"  latency: {elapsed} ms ({api_result.input_tokens} in / {api_result.output_tokens} out tokens)")
    print(f"  raw text: {api_result.text!r}")

    if request["multi_turn"]:
        try:
            parsed = parse_multi_turn_lines(api_result.text)
        except Exception as exc:  # noqa: BLE001
            print(f"{YELLOW}  multi-turn parse failed: {exc}; falling back to single line{RESET}")
            parsed = [{"speaker": speaker["leader_name"], "line": api_result.text}]
        # Build response.lines exactly like the daemon would
        from tools.chatter.chatter_daemon import render_multi_turn
        lines = render_multi_turn(request, parsed)
    else:
        if args.native and speaker_lang:
            from tools.chatter.azure_client import parse_single_line_native
            parsed = parse_single_line_native(api_result.text)
            lines = [{
                "speaker_player_id": int(speaker["player_id"]),
                "speaker_name": speaker["leader_name"],
                "text": parsed.get("line", api_result.text),
                "delay_ms": 0,
            }]
            if parsed.get("line_native"):
                lines[0]["text_native"] = parsed["line_native"]
        else:
            lines = [{
                "speaker_player_id": int(speaker["player_id"]),
                "speaker_name": speaker["leader_name"],
                "text": api_result.text,
                "delay_ms": 0,
            }]

    response = {
        "schema": 1,
        "request_id": request_id,
        "session_id": request["session_id"],
        "ok": True,
        "lines": lines,
        "error": None,
        "latency_ms": elapsed,
        "input_tokens": api_result.input_tokens,
        "output_tokens": api_result.output_tokens,
        "completed_at_unix": time.time(),
    }
    resp_path = out_dir / f"resp-{request_id}.json"
    resp_path.write_text(json.dumps(response, indent=2), encoding="utf-8")
    print(f"  saved: {resp_path.name}")
    print()
    print(f"{CYAN}  Conversation:{RESET}")
    for i, ln in enumerate(lines, 1):
        print(f"    {GREEN}{i}.{RESET} {ln['speaker_name']}: {ln['text']}")
        if ln.get("text_native"):
            print(f"       {DIM}(native: {ln['text_native']}){RESET}")
    print()

    # ===== Step 4: synthesize + play each line =====
    print(f"{CYAN}--- Step 4: Synthesize + play ---{RESET}")
    from tools.chatter.azure_speech_client import AzureSpeechClient, SpeechAuthError, SpeechApiError
    from tools.chatter.voice_picker import VoicePicker

    sc = AzureSpeechClient(
        endpoint=speech_endpoint, key=speech_key,
        default_voice=speech_default_voice,
        request_timeout_seconds=15.0, daily_char_cap=100000,
    )
    # vp already constructed above

    # Probe playback
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
                print(f"{YELLOW}  (no winsound/ffplay; cannot play audio){RESET}")

    def _play(path: Path) -> None:
        if play_method == "winsound":
            import winsound
            try:
                winsound.PlaySound(str(path), winsound.SND_FILENAME)
            except Exception as exc:  # noqa: BLE001
                print(f"    (playback failed: {exc})")
        elif play_method == "ffplay":
            import subprocess
            subprocess.run(["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", str(path)], check=False)

    for idx, ln in enumerate(lines, start=1):
        text = ln["text"]
        text_native = ln.get("text_native", "")
        speaker_name = ln["speaker_name"]
        spec = vp.pick_spec(speaker_name)
        # Choose what to actually synthesize and which voice to use
        synth_text = text_native if text_native else text
        synth_locale = spec.derived_locale() if text_native else ""
        synth_voice = spec.voice_native if (text_native and spec.voice_native) else spec.voice
        prosody_note = ""
        if spec.rate or spec.pitch:
            prosody_note = f"  [{spec.rate or '-'} / {spec.pitch or '-'}]"
        loc_note = f"  [lang={synth_locale}]" if synth_locale else ""
        print(f"  {GREEN}{idx}.{RESET} {speaker_name} (voice={synth_voice}){prosody_note}{loc_note}")
        print(f"     {DIM}EN:     {text!r}{RESET}")
        if text_native:
            print(f"     {DIM}NATIVE: {text_native!r}{RESET}")
        if idx > 1:
            time.sleep(0.4)  # pacing
        try:
            t0 = time.perf_counter()
            result = sc.synthesize(synth_text, voice=synth_voice, rate=spec.rate, pitch=spec.pitch, locale=synth_locale)
            synth_ms = int((time.perf_counter() - t0) * 1000)
        except (SpeechApiError, SpeechAuthError, Exception) as exc:  # noqa: BLE001
            print(f"{RED}     FAIL synth: {exc}{RESET}")
            continue
        wav_path = out_dir / f"line-{idx:02d}-{re.sub(r'[^A-Za-z0-9]+', '-', speaker_name)}.wav"
        wav_path.write_bytes(result.audio_bytes)
        print(f"     synth ok: {synth_ms} ms, {len(result.audio_bytes)} bytes -> {wav_path.name}")
        if play_method is not None:
            _play(wav_path)

    print()
    print(f"{CYAN}===== Done ====={RESET}")
    print(f"  Artifacts in: {out_dir.resolve()}")
    print(f"  Re-run with: python tools/chatter/demo_full_flow.py --trigger ... --speaker ... --target ...")
    return 0


if __name__ == "__main__":
    sys.exit(main())
