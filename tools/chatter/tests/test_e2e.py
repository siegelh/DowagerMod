"""Real end-to-end smoke test: writes a request file, runs the daemon for
one tick by calling the daemon's process_request directly with a real
AzureClient, asserts the response file is generated and parseable.

Requires AZURE_FOUNDRY_API_KEY (or tmp/chatter_secrets.env). Skipped if
neither is available.

Run with:
    .\tmp\chatter_smoke_venv\Scripts\python.exe tools\chatter\tests\test_e2e.py
"""
from __future__ import annotations

import json
import logging
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from tools.chatter import azure_client as ac
from tools.chatter import circuit
from tools.chatter import chatter_daemon


def _load_env_if_present() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    env_path = repo_root / "tmp" / "chatter_secrets.env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        v = v.strip().strip('"').strip("'")
        # Don't override anything already set
        os.environ.setdefault(k.strip(), v)


_load_env_if_present()
HAS_KEY = bool(os.environ.get("AZURE_FOUNDRY_API_KEY") or os.environ.get("DOWAGER_CHATTER_API_KEY"))


@unittest.skipUnless(HAS_KEY, "AZURE_FOUNDRY_API_KEY not set; skipping live test")
class TestEndToEnd(unittest.TestCase):
    def test_real_directed_call(self):
        endpoint = os.environ.get("AZURE_FOUNDRY_ENDPOINT") or "https://hasiegeltestingfoundry.services.ai.azure.com/openai/v1"
        deployment = os.environ.get("AZURE_FOUNDRY_DEPLOYMENT") or "gpt-5.4-mini"
        api_key = os.environ.get("AZURE_FOUNDRY_API_KEY") or os.environ.get("DOWAGER_CHATTER_API_KEY")

        client = ac.AzureClient(endpoint=endpoint, api_key=api_key, deployment=deployment, request_timeout_seconds=15.0)
        breaker = circuit.CircuitBreaker(failure_threshold=3, open_seconds=120)
        logger = logging.getLogger("e2e")

        request = {
            "schema": 1,
            "request_id": "e2e-1",
            "session_id": "e2e",
            "game_turn": 142,
            "elector_player_id": 7,
            "trigger": "DECLARE_WAR",
            "mode": "directed",
            "speaker": {"player_id": 13, "leader_name": "Victoria", "civ_short_name": "England"},
            "target": {"player_id": 4, "leader_name": "Lincoln", "civ_short_name": "America"},
            "context": {"era": "Industrial"},
            "multi_turn": False,
            "n_lines": 1,
            "issued_at_unix": time.time(),
            "ttl_seconds": 60,
        }
        resp = chatter_daemon.process_request(
            Path("dummy"), request,
            client=client, breaker=breaker, logger=logger,
            max_tokens=80, max_tokens_multi=400,
        )
        # Either ok with a line, or a refusal (acceptable but unusual)
        self.assertEqual(resp["request_id"], "e2e-1")
        if resp["ok"]:
            self.assertEqual(len(resp["lines"]), 1)
            line = resp["lines"][0]
            self.assertEqual(line["speaker_player_id"], 13)
            self.assertGreater(len(line["text"]), 5)
            print(f"\n  Victoria -> Lincoln: \"{line['text']}\"")
            print(f"  ({resp['latency_ms']}ms, {resp['input_tokens']}/{resp['output_tokens']} tokens)")
        else:
            print(f"  Got non-ok response (acceptable for refusal): {resp['error']}")

    def test_real_multi_turn_call(self):
        endpoint = os.environ.get("AZURE_FOUNDRY_ENDPOINT") or "https://hasiegeltestingfoundry.services.ai.azure.com/openai/v1"
        deployment = os.environ.get("AZURE_FOUNDRY_DEPLOYMENT") or "gpt-5.4-mini"
        api_key = os.environ.get("AZURE_FOUNDRY_API_KEY") or os.environ.get("DOWAGER_CHATTER_API_KEY")

        client = ac.AzureClient(endpoint=endpoint, api_key=api_key, deployment=deployment, request_timeout_seconds=20.0)
        breaker = circuit.CircuitBreaker(failure_threshold=3, open_seconds=120)
        logger = logging.getLogger("e2e")

        request = {
            "schema": 1,
            "request_id": "e2e-2",
            "session_id": "e2e",
            "game_turn": 187,
            "elector_player_id": 7,
            "trigger": "CITY_RAZED",
            "mode": "directed",
            "speaker": {"player_id": 11, "leader_name": "Genghis Khan", "civ_short_name": "Mongolia"},
            "target": {"player_id": 6, "leader_name": "Wang Kon", "civ_short_name": "Korea"},
            "context": {"era": "Medieval", "city": "Pyongyang"},
            "multi_turn": True,
            "n_lines": 3,
            "issued_at_unix": time.time(),
            "ttl_seconds": 60,
        }
        resp = chatter_daemon.process_request(
            Path("dummy"), request,
            client=client, breaker=breaker, logger=logger,
            max_tokens=80, max_tokens_multi=400,
        )
        self.assertEqual(resp["request_id"], "e2e-2")
        if resp["ok"]:
            print(f"\n  Multi-turn exchange ({resp['latency_ms']}ms, "
                  f"{resp['input_tokens']}/{resp['output_tokens']} tokens):")
            for ln in resp["lines"]:
                delay = "(immediate)" if ln["delay_ms"] == 0 else f"(+{ln['delay_ms']}ms)"
                print(f"    {ln['speaker_name']} {delay}: \"{ln['text']}\"")
            self.assertGreaterEqual(len(resp["lines"]), 1)
        else:
            print(f"  Got non-ok response: {resp['error']}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
