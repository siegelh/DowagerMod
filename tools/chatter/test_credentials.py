"""Test DowagerMod Chatter credentials against the real Azure endpoints.

Reads endpoint+key from a .env file or environment variables. Uses the
SAME variable names as the sidecar daemon, so a single .env file drives
both this test and the actual chatter sidecar.

Usage:

    1. cp tools/chatter/.env.example .env  (or to tools/chatter/.env)
    2. edit .env, paste real keys
    3. python tools/chatter/test_credentials.py --foundry --speech

Variables (all optional unless used by the test you run):
    DOWAGER_CHATTER_ENDPOINT, DOWAGER_CHATTER_DEPLOYMENT, DOWAGER_CHATTER_API_KEY,
    DOWAGER_CHATTER_API_VERSION, DOWAGER_CHATTER_SPEECH_ENDPOINT,
    DOWAGER_CHATTER_SPEECH_KEY, DOWAGER_CHATTER_SPEECH_VOICE.

Older DOWAGER_TEST_* names are also recognized for backwards compat.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

# Make tools/chatter importable when run as a script
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))


def green(s: str) -> str:
    return f"\033[32m{s}\033[0m"


def red(s: str) -> str:
    return f"\033[31m{s}\033[0m"


def yellow(s: str) -> str:
    return f"\033[33m{s}\033[0m"


def test_foundry() -> bool:
    print()
    print("===== Foundry (text/LLM) test =====")
    # Prefer DOWAGER_CHATTER_* (unified with sidecar config). Fall back to
    # DOWAGER_TEST_FOUNDRY_* for backwards compat with earlier .env files.
    endpoint = (
        os.environ.get("DOWAGER_CHATTER_ENDPOINT", "")
        or os.environ.get("DOWAGER_TEST_FOUNDRY_ENDPOINT", "")
    ).strip()
    deployment = (
        os.environ.get("DOWAGER_CHATTER_DEPLOYMENT", "")
        or os.environ.get("DOWAGER_TEST_FOUNDRY_DEPLOYMENT", "gpt-5.4-mini")
    ).strip()
    api_key = (
        os.environ.get("DOWAGER_CHATTER_API_KEY", "")
        or os.environ.get("DOWAGER_TEST_FOUNDRY_KEY", "")
    ).strip()
    api_version = (
        os.environ.get("DOWAGER_CHATTER_API_VERSION", "")
        or os.environ.get("DOWAGER_TEST_FOUNDRY_API_VERSION", "2024-12-01-preview")
    ).strip()
    if not endpoint:
        print(red("FAIL: DOWAGER_CHATTER_ENDPOINT not set in env or .env"))
        return False
    if not api_key:
        print(red("FAIL: DOWAGER_CHATTER_API_KEY not set in env or .env"))
        return False
    redacted = api_key[:4] + "..." + api_key[-4:] if len(api_key) > 8 else "***"
    print(f"  endpoint:   {endpoint}")
    print(f"  deployment: {deployment}")
    print(f"  key:        {redacted}")
    print(f"  version:    {api_version}")
    print()
    try:
        from tools.chatter.azure_client import AzureClient
        client = AzureClient(
            endpoint=endpoint,
            api_key=api_key,
            deployment=deployment,
            request_timeout_seconds=15.0,
            api_version=api_version,
        )
        result = client.call_responses(
            "You are a Civilization IV leader. Respond in one short sentence in character.",
            "Greet a rival leader as if you have just met them.",
            max_tokens=80,
        )
        print(green("PASS: Foundry returned a response."))
        print(f"  text:       {result.text!r}")
        print(f"  latency:    {result.latency_ms} ms")
        print(f"  in_tokens:  {result.input_tokens}")
        print(f"  out_tokens: {result.output_tokens}")
        return True
    except Exception as exc:  # noqa: BLE001
        print(red(f"FAIL: Foundry call raised: {type(exc).__name__}: {exc}"))
        msg = str(exc).lower()
        if "401" in msg or "unauthorized" in msg or "auth" in msg or "invalid api key" in msg:
            print(yellow("  -> Looks like an API key problem. Double-check the key from the Azure portal."))
        elif "404" in msg or "not found" in msg or "deploymentnotfound" in msg:
            print(yellow("  -> Deployment name may be wrong. Check Azure Portal -> your Foundry resource -> Model deployments."))
        elif "timeout" in msg or "connection" in msg or "name resolution" in msg:
            print(yellow("  -> Network or endpoint URL problem. Verify the endpoint URL ends with no extra path."))
        return False


def test_speech() -> bool:
    print()
    print("===== Speech (TTS) test =====")
    endpoint = (
        os.environ.get("DOWAGER_CHATTER_SPEECH_ENDPOINT", "")
        or os.environ.get("DOWAGER_TEST_SPEECH_ENDPOINT", "")
    ).strip()
    key = (
        os.environ.get("DOWAGER_CHATTER_SPEECH_KEY", "")
        or os.environ.get("DOWAGER_TEST_SPEECH_KEY", "")
    ).strip()
    voice = (
        os.environ.get("DOWAGER_CHATTER_SPEECH_VOICE", "")
        or os.environ.get("DOWAGER_TEST_SPEECH_VOICE", "en-US-AriaNeural")
    ).strip()
    if not endpoint:
        print(red("FAIL: DOWAGER_CHATTER_SPEECH_ENDPOINT not set in env or .env"))
        return False
    if not key:
        print(red("FAIL: DOWAGER_CHATTER_SPEECH_KEY not set in env or .env"))
        return False
    redacted = key[:4] + "..." + key[-4:] if len(key) > 8 else "***"
    print(f"  endpoint:   {endpoint}")
    print(f"  key:        {redacted}")
    print(f"  voice:      {voice}")
    print()
    try:
        from tools.chatter.azure_speech_client import AzureSpeechClient
        sc = AzureSpeechClient(
            endpoint=endpoint,
            key=key,
            default_voice=voice,
            request_timeout_seconds=15.0,
            daily_char_cap=10000,
        )
        result = sc.synthesize("Hello world. This is a test of the Dowager Mod chatter voiceover.")
        out_path = Path("test_speech_output.wav")
        out_path.write_bytes(result.audio_bytes)
        print(green("PASS: Speech returned audio."))
        print(f"  voice used: {result.voice}")
        print(f"  chars:      {result.char_count}")
        print(f"  audio size: {len(result.audio_bytes)} bytes")
        print(f"  latency:    {result.latency_ms} ms")
        print(f"  saved to:   {out_path.resolve()}")
        print(yellow("  -> open that .wav file to confirm it sounds right."))
        return True
    except Exception as exc:  # noqa: BLE001
        print(red(f"FAIL: Speech call raised: {type(exc).__name__}: {exc}"))
        msg = str(exc).lower()
        if "401" in msg or "403" in msg or "unauthorized" in msg or "auth" in msg:
            print(yellow("  -> Looks like an API key problem. Use Key 1 or Key 2 from the Azure Portal Speech resource."))
        elif "404" in msg or "not found" in msg:
            print(yellow("  -> Endpoint URL or voice name may be wrong."))
            print(yellow("     Endpoint should look like: https://<region>.api.cognitive.microsoft.com/"))
        elif "timeout" in msg or "connection" in msg:
            print(yellow("  -> Network or endpoint URL problem."))
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--foundry", action="store_true", help="Test Foundry/LLM credentials")
    parser.add_argument("--speech", action="store_true", help="Test Speech/TTS credentials")
    args = parser.parse_args()
    if not args.foundry and not args.speech:
        parser.print_help()
        return 2

    # Load .env via the shared loader (same one the sidecar uses).
    try:
        from tools.chatter.dotenv import load_dotenv
        loaded = load_dotenv()
        if loaded:
            print(f"  (loaded env from {loaded})")
    except Exception as exc:  # noqa: BLE001
        print(f"  (warning: dotenv loader failed: {exc})")

    results = []
    if args.foundry:
        results.append(("foundry", test_foundry()))
    if args.speech:
        results.append(("speech", test_speech()))

    print()
    print("===== Summary =====")
    all_pass = True
    for name, ok in results:
        status = green("PASS") if ok else red("FAIL")
        print(f"  {name}: {status}")
        if not ok:
            all_pass = False
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
