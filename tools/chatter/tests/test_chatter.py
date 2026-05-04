"""Unit tests for the chatter sidecar — no live API calls.

Run with:
    python -m unittest discover -s tools\\chatter\\tests
"""
from __future__ import annotations

import json
import os
import sys
import time
import unittest
from pathlib import Path
from unittest.mock import patch

# Ensure repo root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from tools.chatter import config as cfg_mod
from tools.chatter import spool as spool_mod
from tools.chatter import circuit
from tools.chatter import azure_client
from tools.chatter import prompts


class TestConfig(unittest.TestCase):
    def test_defaults_load_when_no_file(self):
        # Use an explicit path that does not exist
        cfg = cfg_mod.load_config(Path(os.devnull + "_does_not_exist.json"))
        self.assertEqual(cfg.endpoint, cfg_mod.DEFAULTS["endpoint"])
        self.assertFalse(cfg_mod.is_configured(cfg))  # no key

    def test_env_overrides(self):
        with patch.dict(os.environ, {
            "DOWAGER_CHATTER_API_KEY": "test-key-1234",
            "DOWAGER_CHATTER_DEPLOYMENT": "test-deployment",
        }, clear=False):
            cfg = cfg_mod.load_config(Path(os.devnull + "_does_not_exist.json"))
            self.assertEqual(cfg.api_key, "test-key-1234")
            self.assertEqual(cfg.deployment, "test-deployment")
            self.assertTrue(cfg_mod.is_configured(cfg))

    def test_redacted_api_key(self):
        cfg = cfg_mod.Config(api_key="abcdefghijklmnop")
        r = cfg.redacted_api_key()
        self.assertNotIn("efghijkl", r)
        self.assertTrue(r.startswith("abcd"))
        self.assertTrue(r.endswith("mnop"))

    def test_malformed_config_falls_back_to_defaults(self):
        import tempfile
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            f.write("{ this is not json")
            path = Path(f.name)
        try:
            cfg = cfg_mod.load_config(path)
            self.assertEqual(cfg.endpoint, cfg_mod.DEFAULTS["endpoint"])
        finally:
            path.unlink()


class TestSpool(unittest.TestCase):
    def setUp(self):
        import tempfile
        self.tmp = Path(tempfile.mkdtemp(prefix="chatter_spool_test_"))

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_atomic_write_and_read(self):
        path = self.tmp / "test.json"
        spool_mod.atomic_write_json(path, {"hello": "world"})
        data = spool_mod.safe_read_json(path)
        self.assertEqual(data, {"hello": "world"})

    def test_safe_read_returns_none_on_missing(self):
        self.assertIsNone(spool_mod.safe_read_json(self.tmp / "absent.json"))

    def test_safe_read_returns_none_on_bad_json(self):
        path = self.tmp / "bad.json"
        path.write_text("not json", encoding="utf-8")
        self.assertIsNone(spool_mod.safe_read_json(path))

    def test_list_requests_skips_tmp(self):
        spool_mod.atomic_write_json(self.tmp / "req-001.json", {"x": 1})
        (self.tmp / "req-002.json.tmp").write_text("partial", encoding="utf-8")
        names = [p.name for p in spool_mod.list_requests(self.tmp)]
        self.assertIn("req-001.json", names)
        self.assertNotIn("req-002.json.tmp", names)

    def test_gc_old_files(self):
        old = self.tmp / "req-old.json"
        new = self.tmp / "req-new.json"
        spool_mod.atomic_write_json(old, {})
        spool_mod.atomic_write_json(new, {})
        # Backdate the "old" mtime
        old_time = time.time() - 3600
        os.utime(str(old), (old_time, old_time))
        n = spool_mod.gc_old_files(self.tmp, "req-", max_age_seconds=300)
        self.assertEqual(n, 1)
        self.assertFalse(old.exists())
        self.assertTrue(new.exists())


class TestCircuitBreaker(unittest.TestCase):
    def test_closed_starts_callable(self):
        cb = circuit.CircuitBreaker(failure_threshold=2, open_seconds=10)
        self.assertTrue(cb.can_call())
        self.assertEqual(cb.state, circuit.State.CLOSED)

    def test_opens_after_threshold(self):
        cb = circuit.CircuitBreaker(failure_threshold=2, open_seconds=10)
        cb.record_failure()
        self.assertTrue(cb.can_call())
        cb.record_failure()
        self.assertFalse(cb.can_call())
        self.assertEqual(cb.state, circuit.State.OPEN)

    def test_half_open_after_cooldown(self):
        # Use a controllable clock
        clock = [1000.0]
        cb = circuit.CircuitBreaker(failure_threshold=1, open_seconds=10, now_fn=lambda: clock[0])
        cb.record_failure()
        self.assertEqual(cb.state, circuit.State.OPEN)
        clock[0] += 11
        self.assertEqual(cb.state, circuit.State.HALF_OPEN)
        self.assertTrue(cb.can_call())

    def test_half_open_failure_reopens(self):
        clock = [1000.0]
        cb = circuit.CircuitBreaker(failure_threshold=1, open_seconds=10, now_fn=lambda: clock[0])
        cb.record_failure()
        clock[0] += 11
        # Now half-open
        cb.record_failure()
        self.assertEqual(cb.state, circuit.State.OPEN)
        self.assertEqual(cb._opened_at, 1011.0)

    def test_success_closes(self):
        cb = circuit.CircuitBreaker(failure_threshold=2)
        cb.record_failure()
        cb.record_success()
        self.assertEqual(cb.state, circuit.State.CLOSED)
        # And consecutive failure count is reset
        cb.record_failure()
        self.assertTrue(cb.can_call())

    def test_trip_immediately(self):
        cb = circuit.CircuitBreaker(failure_threshold=10)
        cb.trip_immediately()
        self.assertFalse(cb.can_call())


class TestAzureClientHelpers(unittest.TestCase):
    def test_parse_multi_turn_basic(self):
        raw = '[{"speaker":"Victoria","line":"Hello"}, {"speaker":"Lincoln","line":"Reply"}]'
        out = azure_client.parse_multi_turn_lines(raw)
        self.assertEqual(len(out), 2)
        self.assertEqual(out[0]["speaker"], "Victoria")
        self.assertEqual(out[1]["line"], "Reply")

    def test_parse_multi_turn_strips_code_fence(self):
        raw = '```json\n[{"speaker":"X","line":"y"}]\n```'
        out = azure_client.parse_multi_turn_lines(raw)
        self.assertEqual(len(out), 1)

    def test_parse_multi_turn_rejects_garbage(self):
        with self.assertRaises(Exception):
            azure_client.parse_multi_turn_lines("not json at all")

    def test_parse_multi_turn_rejects_non_list(self):
        with self.assertRaises(Exception):
            azure_client.parse_multi_turn_lines('{"speaker":"X","line":"y"}')

    def test_refusal_detection(self):
        self.assertTrue(azure_client.looks_like_refusal("I'm sorry, I cannot help with that."))
        self.assertTrue(azure_client.looks_like_refusal("As an AI language model..."))
        self.assertTrue(azure_client.looks_like_refusal(""))
        self.assertFalse(azure_client.looks_like_refusal(
            "Mr. Lincoln, your republic shall find that the Crown's patience is refined."))


class TestPrompts(unittest.TestCase):
    def test_directed_prompt(self):
        request = {
            "trigger": "DECLARE_WAR",
            "game_turn": 142,
            "speaker": {"leader_name": "Victoria", "civ_short_name": "England", "player_id": 13},
            "target": {"leader_name": "Lincoln", "civ_short_name": "America", "player_id": 4},
            "context": {"era": "Industrial"},
        }
        sys_msg, user_msg = prompts.build_single_line_prompt(request)
        self.assertIn("Victoria", sys_msg)
        self.assertIn("Lincoln", sys_msg)
        self.assertIn("declared war", sys_msg)
        self.assertIn("Industrial", user_msg)
        self.assertIn("turn 142", user_msg)

    def test_broadcast_prompt(self):
        request = {
            "trigger": "WONDER_BUILT",
            "game_turn": 110,
            "speaker": {"leader_name": "Ramesses", "civ_short_name": "Egypt", "player_id": 2},
            "target": None,
            "context": {"era": "Classical", "wonder": "Pyramids"},
        }
        sys_msg, user_msg = prompts.build_single_line_prompt(request)
        self.assertIn("proclaiming this to the world", sys_msg)
        self.assertIn("Pyramids", sys_msg)
        self.assertNotIn("addressing", sys_msg)

    def test_unknown_trigger_raises(self):
        with self.assertRaises(ValueError):
            prompts.build_single_line_prompt({"trigger": "BOGUS", "speaker": {"leader_name": "X", "civ_short_name": "Y"}})

    def test_multi_turn_prompt(self):
        request = {
            "trigger": "DECLARE_WAR",
            "game_turn": 142,
            "n_lines": 3,
            "multi_turn": True,
            "speaker": {"leader_name": "Victoria", "civ_short_name": "England", "player_id": 13},
            "target": {"leader_name": "Lincoln", "civ_short_name": "America", "player_id": 4},
            "context": {"era": "Industrial"},
        }
        sys_msg, user_msg = prompts.build_multi_turn_prompt(request)
        self.assertIn("playwright", sys_msg)
        self.assertIn("3 lines", sys_msg)
        self.assertIn("Victoria", sys_msg)
        self.assertIn("Lincoln", sys_msg)


class TestDaemonProcessRequest(unittest.TestCase):
    """End-to-end test of process_request with a fake AzureClient."""

    def setUp(self):
        from tools.chatter import chatter_daemon
        self.daemon = chatter_daemon
        import logging
        self.logger = logging.getLogger("test")
        self.breaker = circuit.CircuitBreaker(failure_threshold=2, open_seconds=10)

    def _fake_client(self, *, text="", auth=False, api=False):
        class Fake:
            def call_responses(self, sys_msg, user_msg, **kw):
                if auth:
                    raise azure_client.AuthError("test auth fail")
                if api:
                    raise azure_client.ApiError("test api fail")
                return azure_client.ApiResult(text=text, latency_ms=100, input_tokens=50, output_tokens=20)
        return Fake()

    def _basic_request(self, **overrides):
        req = {
            "schema": 1,
            "request_id": "test-req-1",
            "session_id": "test-session",
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
        req.update(overrides)
        return req

    def test_happy_path_single_line(self):
        client = self._fake_client(text="Test line, Mr. Lincoln.")
        resp = self.daemon.process_request(
            Path("dummy"), self._basic_request(),
            client=client, breaker=self.breaker, logger=self.logger,
            max_tokens=80, max_tokens_multi=400,
        )
        self.assertTrue(resp["ok"])
        self.assertEqual(len(resp["lines"]), 1)
        self.assertEqual(resp["lines"][0]["text"], "Test line, Mr. Lincoln.")
        self.assertEqual(resp["lines"][0]["delay_ms"], 0)

    def test_refusal_detected(self):
        client = self._fake_client(text="I'm sorry, but I cannot assist.")
        resp = self.daemon.process_request(
            Path("dummy"), self._basic_request(),
            client=client, breaker=self.breaker, logger=self.logger,
            max_tokens=80, max_tokens_multi=400,
        )
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "refusal")

    def test_auth_error_trips_breaker(self):
        client = self._fake_client(auth=True)
        resp = self.daemon.process_request(
            Path("dummy"), self._basic_request(),
            client=client, breaker=self.breaker, logger=self.logger,
            max_tokens=80, max_tokens_multi=400,
        )
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "auth_failure")
        self.assertFalse(self.breaker.can_call())

    def test_api_error_records_failure(self):
        client = self._fake_client(api=True)
        resp = self.daemon.process_request(
            Path("dummy"), self._basic_request(),
            client=client, breaker=self.breaker, logger=self.logger,
            max_tokens=80, max_tokens_multi=400,
        )
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "api_failure")

    def test_open_circuit_drops_request(self):
        self.breaker.trip_immediately()
        client = self._fake_client(text="should not be called")
        resp = self.daemon.process_request(
            Path("dummy"), self._basic_request(),
            client=client, breaker=self.breaker, logger=self.logger,
            max_tokens=80, max_tokens_multi=400,
        )
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "circuit_open")

    def test_multi_turn_happy_path(self):
        raw = ('[{"speaker":"Victoria","line":"line1"},'
               '{"speaker":"Lincoln","line":"line2"},'
               '{"speaker":"Victoria","line":"line3"}]')
        client = self._fake_client(text=raw)
        req = self._basic_request(multi_turn=True, n_lines=3)
        resp = self.daemon.process_request(
            Path("dummy"), req,
            client=client, breaker=self.breaker, logger=self.logger,
            max_tokens=80, max_tokens_multi=400,
        )
        self.assertTrue(resp["ok"])
        self.assertEqual(len(resp["lines"]), 3)
        self.assertEqual(resp["lines"][0]["delay_ms"], 0)
        self.assertGreater(resp["lines"][1]["delay_ms"], 0)
        self.assertGreater(resp["lines"][2]["delay_ms"], 0)
        # speakers correctly mapped to player IDs
        self.assertEqual(resp["lines"][0]["speaker_player_id"], 13)
        self.assertEqual(resp["lines"][1]["speaker_player_id"], 4)
        self.assertEqual(resp["lines"][2]["speaker_player_id"], 13)

    def test_multi_turn_parse_failure_falls_back_to_single(self):
        client = self._fake_client(text="not valid json at all")
        req = self._basic_request(multi_turn=True, n_lines=3)
        resp = self.daemon.process_request(
            Path("dummy"), req,
            client=client, breaker=self.breaker, logger=self.logger,
            max_tokens=80, max_tokens_multi=400,
        )
        self.assertTrue(resp["ok"])
        self.assertEqual(len(resp["lines"]), 1)
        self.assertEqual(resp["lines"][0]["text"], "not valid json at all")


if __name__ == "__main__":
    unittest.main()
