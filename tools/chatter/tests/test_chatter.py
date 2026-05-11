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
        # Use an explicit path that does not exist. Skip .env loading so a
        # user's repo-root .env doesn't override the in-code DEFAULTS that
        # this test is asserting against.
        with patch.dict(os.environ, {"DOWAGER_CHATTER_SKIP_DOTENV": "1"}, clear=False):
            # Strip any DOWAGER_CHATTER_* env vars that an outer process
            # (e.g. an earlier .env load in the same pytest session) may
            # already have injected.
            for k in [k for k in os.environ if k.startswith("DOWAGER_CHATTER_")
                      and k != "DOWAGER_CHATTER_SKIP_DOTENV"]:
                del os.environ[k]
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
            # Skip .env to keep the test deterministic regardless of any
            # user-specific overrides in the repo-root .env.
            with patch.dict(os.environ, {"DOWAGER_CHATTER_SKIP_DOTENV": "1"}, clear=False):
                for k in [k for k in os.environ if k.startswith("DOWAGER_CHATTER_")
                          and k != "DOWAGER_CHATTER_SKIP_DOTENV"]:
                    del os.environ[k]
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
        # Tightened brevity rules: 14-word cap and ban list applied.
        self.assertIn("14 words", sys_msg)
        self.assertIn("Behold", sys_msg)
        self.assertNotIn("interjections encouraged", sys_msg.lower())

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

    def test_chat_reply_prompt(self):
        request = {
            "trigger": "CHAT_REPLY",
            "speaker": {"leader_name": "Louis XIV", "civ_short_name": "France", "player_id": 3},
            "target": {"leader_name": "Harrison", "civ_short_name": "America", "player_id": 0,
                       "human_name": "Harrison"},
            "context": {"user_message": "You are a fool, Louie!"},
        }
        history = [
            {"role": "user", "content": "You are a fool, Louie!"},
        ]
        sys_msg, msgs = prompts.build_chat_reply_prompt(request, history)
        self.assertIn("Louis XIV", sys_msg)
        self.assertIn("France", sys_msg)
        self.assertIn("Harrison", sys_msg)
        self.assertIn("JSON", sys_msg)
        self.assertIn("tone", sys_msg)
        self.assertIn("angry", sys_msg)
        self.assertIn("18 words", sys_msg)
        self.assertEqual(msgs, history)

    def test_chat_reply_prompt_room_state_roster(self):
        """room_state injects a roster preface naming each civ + attitude toward speaker."""
        request = {
            "trigger": "CHAT_REPLY",
            "speaker": {"leader_name": "Louis XIV", "civ_short_name": "France", "player_id": 3},
            "target": {"leader_name": "Harrison", "civ_short_name": "America", "player_id": 0,
                       "human_name": "Harrison"},
            "context": {"user_message": "Hello"},
        }
        room_state = {
            "speaker_id": 3,
            "roster": [
                {"player_id": 3, "leader_name": "Louis XIV", "civ_short": "France",
                 "is_human": False, "human_name": "",
                 "at_war_with_speaker": False, "attitude_toward_speaker": "Friendly"},
                {"player_id": 0, "leader_name": "Washington", "civ_short": "America",
                 "is_human": True, "human_name": "Harrison",
                 "at_war_with_speaker": False, "attitude_toward_speaker": "Pleased"},
                {"player_id": 1, "leader_name": "Victoria", "civ_short": "England",
                 "is_human": False, "human_name": "",
                 "at_war_with_speaker": True, "attitude_toward_speaker": "Furious"},
            ],
            "relations": [
                {"from_pid": 1, "to_pid": 3, "attitude": "Furious", "at_war": True},
            ],
        }
        sys_msg, _ = prompts.build_chat_reply_prompt(request, [], room_state=room_state)
        # Speaker (Louis XIV) himself must NOT appear in the roster lines.
        roster_section = sys_msg.split("ROOM ")[1].split("RELATIONS")[0]
        self.assertNotIn("Louis XIV of France", roster_section)
        # Other entries appear, with attitude toward speaker.
        self.assertIn("Washington of America (HUMAN, \"Harrison\")", sys_msg)
        self.assertIn("Pleased", sys_msg)
        self.assertIn("Victoria of England (AI)", sys_msg)
        self.assertIn("Furious", sys_msg)
        self.assertIn("at war with you", sys_msg)
        # AI-to-AI relations block included.
        self.assertIn("Victoria -> Louis XIV: Furious (at war)", sys_msg)

    def test_chat_reply_prompt_room_state_none_no_preface(self):
        """No room_state means no ROOM / RELATIONS preface."""
        request = {
            "trigger": "CHAT_REPLY",
            "speaker": {"leader_name": "Louis XIV", "civ_short_name": "France", "player_id": 3},
            "target": {"leader_name": "Harrison", "civ_short_name": "America", "player_id": 0,
                       "human_name": "Harrison"},
            "context": {"user_message": "Hello"},
        }
        sys_msg, _ = prompts.build_chat_reply_prompt(request, [])
        self.assertNotIn("ROOM ", sys_msg)
        self.assertNotIn("RELATIONS", sys_msg)

    def test_chat_reply_prompt_active_wars_section_during_war(self):
        """When room_state shows wars, an ACTIVE WARS THIS TURN block lists them."""
        request = {
            "trigger": "CHAT_REPLY",
            "speaker": {"leader_name": "Lincoln", "civ_short_name": "America", "player_id": 2},
            "target": {"leader_name": "hasiegel", "civ_short_name": "", "player_id": 0,
                       "human_name": "hasiegel"},
            "context": {"user_message": "Who are you at war with?"},
        }
        room_state = {
            "speaker_id": 2,
            "roster": [
                {"player_id": 5, "leader_name": "Ragnar", "civ_short": "Vikings",
                 "is_human": False, "human_name": "",
                 "at_war_with_speaker": True, "attitude_toward_speaker": "Furious"},
                {"player_id": 7, "leader_name": "Ramesses II", "civ_short": "Egypt",
                 "is_human": False, "human_name": "",
                 "at_war_with_speaker": True, "attitude_toward_speaker": "Annoyed"},
                {"player_id": 9, "leader_name": "Gilgamesh", "civ_short": "Sumeria",
                 "is_human": False, "human_name": "",
                 "at_war_with_speaker": False, "attitude_toward_speaker": "Pleased"},
            ],
            "relations": [
                {"from_pid": 5, "to_pid": 7, "attitude": "Friendly", "at_war": False},
                {"from_pid": 7, "to_pid": 5, "attitude": "Friendly", "at_war": False},
            ],
        }
        sys_msg, _ = prompts.build_chat_reply_prompt(request, [], room_state=room_state)
        self.assertIn("ACTIVE WARS THIS TURN", sys_msg)
        self.assertIn("AUTHORITATIVE", sys_msg)
        self.assertIn("Lincoln <-> Ragnar", sys_msg)
        self.assertIn("Lincoln <-> Ramesses II", sys_msg)
        # Gilgamesh is NOT at war and must not appear as a war pair.
        self.assertNotIn("Lincoln <-> Gilgamesh", sys_msg)
        self.assertNotIn("Gilgamesh <-> Lincoln", sys_msg)

    def test_chat_reply_prompt_active_wars_section_during_peace(self):
        """When everyone is at peace, the block explicitly states 'none' and
        warns the model that any earlier transcript reference to a war
        has since ended (this is the Ragnar/Ramesses post-treaty bug)."""
        request = {
            "trigger": "CHAT_REPLY",
            "speaker": {"leader_name": "Lincoln", "civ_short_name": "America", "player_id": 2},
            "target": {"leader_name": "hasiegel", "civ_short_name": "", "player_id": 0,
                       "human_name": "hasiegel"},
            "context": {"user_message": "Who are you at war with?"},
        }
        room_state = {
            "speaker_id": 2,
            "roster": [
                # Lincoln, Ragnar, Ramesses II -- all at peace after treaty.
                {"player_id": 5, "leader_name": "Ragnar", "civ_short": "Vikings",
                 "is_human": False, "human_name": "",
                 "at_war_with_speaker": False, "attitude_toward_speaker": "Annoyed"},
                {"player_id": 7, "leader_name": "Ramesses II", "civ_short": "Egypt",
                 "is_human": False, "human_name": "",
                 "at_war_with_speaker": False, "attitude_toward_speaker": "Cautious"},
            ],
            "relations": [
                {"from_pid": 5, "to_pid": 7, "attitude": "Friendly", "at_war": False},
            ],
        }
        sys_msg, _ = prompts.build_chat_reply_prompt(request, [], room_state=room_state)
        self.assertIn("ACTIVE WARS THIS TURN: none", sys_msg)
        # Must not name any pair as actively at war.
        self.assertNotIn("Lincoln <-> Ragnar", sys_msg)
        self.assertNotIn("Lincoln <-> Ramesses II", sys_msg)
        self.assertNotIn("Ragnar <-> Ramesses II", sys_msg)
        # Must give the model a clear "treat current peace as authoritative" hint.
        self.assertIn("at peace", sys_msg.lower())
        self.assertIn("authoritative", sys_msg.lower())

    def test_chat_reply_prompt_active_wars_dedupes_mutual_pairs(self):
        """Mutual at-war relations (A->B and B->A) collapse to a single pair."""
        request = {
            "trigger": "CHAT_REPLY",
            "speaker": {"leader_name": "Catherine", "civ_short_name": "Russia", "player_id": 4},
            "target": {"leader_name": "hasiegel", "civ_short_name": "", "player_id": 0,
                       "human_name": "hasiegel"},
            "context": {"user_message": "What's happening?"},
        }
        room_state = {
            "speaker_id": 4,
            "roster": [
                {"player_id": 1, "leader_name": "Bismarck", "civ_short": "Germany",
                 "is_human": False, "human_name": "",
                 "at_war_with_speaker": False, "attitude_toward_speaker": "Pleased"},
                {"player_id": 2, "leader_name": "Lincoln", "civ_short": "America",
                 "is_human": False, "human_name": "",
                 "at_war_with_speaker": False, "attitude_toward_speaker": "Annoyed"},
            ],
            "relations": [
                {"from_pid": 1, "to_pid": 2, "attitude": "Furious", "at_war": True},
                {"from_pid": 2, "to_pid": 1, "attitude": "Furious", "at_war": True},
            ],
        }
        sys_msg, _ = prompts.build_chat_reply_prompt(request, [], room_state=room_state)
        # Only one war pair line, regardless of direction.
        war_section = sys_msg.split("ACTIVE WARS THIS TURN")[1].split("\n\n")[0]
        bismarck_lincoln = war_section.count("Bismarck") + war_section.count("Lincoln")
        # Each name appears exactly once in the dedup'd pair.
        self.assertEqual(bismarck_lincoln, 2,
                         "expected Bismarck and Lincoln each once; got " + war_section)

    def test_chat_reply_prompt_eliminated_leader_in_roster(self):
        """Met-but-eliminated leaders stay in the roster, tagged ELIMINATED.

        They cannot speak or be addressed, but other leaders may refer
        to them in past tense ('Catherine was a fool when she lived').
        """
        request = {
            "trigger": "CHAT_REPLY",
            "speaker": {"leader_name": "Lincoln", "civ_short_name": "America", "player_id": 2},
            "target": {"leader_name": "h", "player_id": 0, "human_name": "h"},
            "context": {"user_message": "Remember Catherine?"},
        }
        room_state = {
            "speaker_id": 2,
            "roster": [
                {"player_id": 4, "leader_name": "Catherine", "civ_short": "Russia",
                 "is_human": False, "human_name": "",
                 "at_war_with_speaker": False, "eliminated": True,
                 "attitude_toward_speaker": "Furious"},
                {"player_id": 5, "leader_name": "Ragnar", "civ_short": "Vikings",
                 "is_human": False, "human_name": "",
                 "at_war_with_speaker": False, "eliminated": False,
                 "attitude_toward_speaker": "Pleased"},
            ],
            "relations": [],
        }
        sys_msg, _ = prompts.build_chat_reply_prompt(request, [], room_state=room_state)
        # Catherine appears in the roster, but tagged ELIMINATED.
        self.assertIn("Catherine of Russia (AI)", sys_msg)
        self.assertIn("ELIMINATED", sys_msg)
        self.assertIn("past tense", sys_msg)
        # Eliminated Catherine is NOT shown as currently at war.
        self.assertNotIn("Lincoln <-> Catherine", sys_msg)
        # Ragnar is alive, normal attitude shown.
        self.assertIn("Ragnar of Vikings (AI)", sys_msg)
        self.assertIn("Pleased", sys_msg)
        # Closing directive must forbid inventing leaders not on list.
        self.assertIn("never invent", sys_msg.lower().replace(" or ", " "))

    def test_chat_reply_prompt_eliminated_not_in_active_wars(self):
        """Eliminated leaders must not appear as active belligerents even
        if their at_war_with_speaker flag is somehow set upstream."""
        request = {
            "trigger": "CHAT_REPLY",
            "speaker": {"leader_name": "Lincoln", "civ_short_name": "America", "player_id": 2},
            "target": {"leader_name": "h", "player_id": 0, "human_name": "h"},
            "context": {"user_message": "Who fights you?"},
        }
        room_state = {
            "speaker_id": 2,
            "roster": [
                # Defensive case: eliminated entry with at_war flag True
                # (the game-side code already sets at_war to False for
                # eliminated, but the prompt layer should be robust to
                # either).
                {"player_id": 4, "leader_name": "Catherine", "civ_short": "Russia",
                 "is_human": False, "human_name": "",
                 "at_war_with_speaker": True, "eliminated": True,
                 "attitude_toward_speaker": "Furious"},
            ],
            "relations": [],
        }
        sys_msg, _ = prompts.build_chat_reply_prompt(request, [], room_state=room_state)
        # Eliminated Catherine must NOT appear in the WARS pair list.
        self.assertNotIn("Lincoln <-> Catherine", sys_msg)
        self.assertNotIn("Catherine <-> Lincoln", sys_msg)

    def test_chat_reply_prompt_room_state_chain_variant(self):
        """Chain-reply prompt also gets the room_state preface."""
        request = {
            "trigger": "CHAT_REPLY",
            "speaker": {"leader_name": "Victoria", "civ_short_name": "England", "player_id": 1},
            "target": {"leader_name": "Louis XIV", "civ_short_name": "France", "player_id": 3},
            "context": {"user_message": "Bah, Victoria!", "chain_reply": "1"},
        }
        room_state = {
            "speaker_id": 1,
            "roster": [
                {"player_id": 3, "leader_name": "Louis XIV", "civ_short": "France",
                 "is_human": False, "human_name": "",
                 "at_war_with_speaker": True, "attitude_toward_speaker": "Furious"},
            ],
            "relations": [],
        }
        sys_msg, _ = prompts.build_chat_reply_prompt(
            request, [], chain_reply=True,
            prior_leader_speaker_name="Louis XIV",
            room_state=room_state,
        )
        self.assertIn("Louis XIV of France", sys_msg)
        self.assertIn("Furious", sys_msg)
        self.assertIn("at war with you", sys_msg)
        # And the chain variant still kicks in.
        self.assertIn("Reply in character to Louis XIV", sys_msg)

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


class TestPromptsTier1Extras(unittest.TestCase):
    """Tier 1 / Tier 1b room_state extension renders cleanly when present
    and is omitted entirely when absent (additive backward-compat)."""

    def _base_request(self):
        return {
            "trigger": "CHAT_REPLY",
            "speaker": {"leader_name": "Louis XIV", "civ_short_name": "France", "player_id": 3},
            "target": {"leader_name": "Harrison", "civ_short_name": "America", "player_id": 0,
                       "human_name": "Harrison"},
            "context": {"user_message": "Hello"},
        }

    def test_leader_stats_line_rendered(self):
        """When roster entries carry Tier 1 scalars they appear on a
        second indented line beneath the leader name."""
        request = self._base_request()
        room_state = {
            "speaker_id": 3,
            "roster": [
                {"player_id": 3, "leader_name": "Louis XIV", "civ_short": "France",
                 "is_human": False, "at_war_with_speaker": False,
                 "attitude_toward_speaker": "Friendly"},
                {"player_id": 1, "leader_name": "Victoria", "civ_short": "England",
                 "is_human": False, "at_war_with_speaker": False,
                 "attitude_toward_speaker": "Cautious",
                 "speaker_attitude_toward": "Pleased",
                 "era": "Industrial", "num_cities": 12, "score": 480,
                 "power": 95000, "military": 38, "gold": 320,
                 "civic_gov": "Hereditary Rule", "religion": "Buddhism",
                 "capital": "London", "research": "Steam Power"},
            ],
            "relations": [],
        }
        sys_msg, _ = prompts.build_chat_reply_prompt(request, [], room_state=room_state)
        self.assertIn("you toward them: Pleased", sys_msg)
        self.assertIn("Industrial era", sys_msg)
        self.assertIn("12 cit", sys_msg)
        self.assertIn("score 480", sys_msg)
        self.assertIn("pwr 95000", sys_msg)
        self.assertIn("38 units", sys_msg)
        self.assertIn("gold 320", sys_msg)
        self.assertIn("Hereditary Rule/Buddhism", sys_msg)
        self.assertIn("cap London", sys_msg)
        self.assertIn("researching Steam Power", sys_msg)

    def test_leader_stats_line_skips_empty_segments(self):
        """Empty/None scalars must NOT produce noise lines like
        'cap (no capital)' or 'researching None'."""
        request = self._base_request()
        room_state = {
            "speaker_id": 3,
            "roster": [
                {"player_id": 1, "leader_name": "Victoria", "civ_short": "England",
                 "is_human": False, "at_war_with_speaker": False,
                 "attitude_toward_speaker": "Cautious",
                 "era": "Ancient", "num_cities": 2,
                 "civic_gov": "Despotism", "religion": "",
                 "capital": "", "research": ""},
            ],
            "relations": [],
        }
        sys_msg, _ = prompts.build_chat_reply_prompt(request, [], room_state=room_state)
        self.assertIn("Ancient era", sys_msg)
        self.assertIn("Despotism", sys_msg)
        # No empty/None segments leaked.
        self.assertNotIn("cap (", sys_msg)
        self.assertNotIn("researching None", sys_msg)
        self.assertNotIn("None era", sys_msg)
        self.assertNotIn("religion ()", sys_msg)

    def test_leader_stats_omitted_when_no_extras(self):
        """Old-style roster entries (no Tier 1 fields) render exactly as
        before -- a single line per leader, no stats line."""
        request = self._base_request()
        room_state = {
            "speaker_id": 3,
            "roster": [
                {"player_id": 1, "leader_name": "Victoria", "civ_short": "England",
                 "is_human": False, "at_war_with_speaker": False,
                 "attitude_toward_speaker": "Cautious"},
            ],
            "relations": [],
        }
        sys_msg, _ = prompts.build_chat_reply_prompt(request, [], room_state=room_state)
        room_section = sys_msg.split("ROOM ")[1].split("\n\n")[0]
        # Only the leader line should be present -- no follow-up indented
        # stats or memory lines.
        leader_lines = [ln for ln in room_section.split("\n") if ln.startswith("- ")]
        all_lines = [ln for ln in room_section.split("\n") if ln.strip()]
        # Header line + one leader line == two lines total.
        self.assertEqual(len(leader_lines), 1)
        self.assertEqual(len(all_lines), 2)

    def test_memory_line_rendered_with_humanized_phrases(self):
        """memories_vs_speaker emits a humanized 'Your memory of them' line."""
        request = self._base_request()
        room_state = {
            "speaker_id": 3,
            "roster": [
                {"player_id": 1, "leader_name": "Victoria", "civ_short": "England",
                 "is_human": False, "at_war_with_speaker": False,
                 "attitude_toward_speaker": "Furious",
                 "memories_vs_speaker": [
                     {"name": "DECLARED_WAR", "count": 1},
                     {"name": "RAZED_CITY", "count": 3},
                     {"name": "DECLARED_WAR_ON_FRIEND", "count": 2},
                 ]},
            ],
            "relations": [],
        }
        sys_msg, _ = prompts.build_chat_reply_prompt(request, [], room_state=room_state)
        self.assertIn("Your memory of them: declared war on you", sys_msg)
        self.assertIn("razed your city x3", sys_msg)
        self.assertIn("declared war on your friend x2", sys_msg)

    def test_memory_line_omitted_when_empty_or_missing(self):
        """No memory line should render for entries without memories."""
        request = self._base_request()
        room_state = {
            "speaker_id": 3,
            "roster": [
                {"player_id": 1, "leader_name": "Victoria", "civ_short": "England",
                 "is_human": False, "at_war_with_speaker": False,
                 "attitude_toward_speaker": "Pleased",
                 "memories_vs_speaker": []},
                {"player_id": 2, "leader_name": "Lincoln", "civ_short": "America",
                 "is_human": False, "at_war_with_speaker": False,
                 "attitude_toward_speaker": "Cautious"},
            ],
            "relations": [],
        }
        sys_msg, _ = prompts.build_chat_reply_prompt(request, [], room_state=room_state)
        self.assertNotIn("Your memory of them:", sys_msg)

    def test_memory_unknown_name_passthrough(self):
        """Unknown memory enum names fall back to the raw identifier
        instead of being silently dropped."""
        request = self._base_request()
        room_state = {
            "speaker_id": 3,
            "roster": [
                {"player_id": 1, "leader_name": "Victoria", "civ_short": "England",
                 "is_human": False, "at_war_with_speaker": False,
                 "attitude_toward_speaker": "Pleased",
                 "memories_vs_speaker": [
                     {"name": "BRAND_NEW_MEMORY_TYPE", "count": 1},
                 ]},
            ],
            "relations": [],
        }
        sys_msg, _ = prompts.build_chat_reply_prompt(request, [], room_state=room_state)
        self.assertIn("BRAND_NEW_MEMORY_TYPE", sys_msg)

    def test_relations_pair_extras_rendered(self):
        """Pair extras (war duration, defensive pact, open borders,
        memories) decorate the RELATIONS line."""
        request = self._base_request()
        room_state = {
            "speaker_id": 3,
            "roster": [
                {"player_id": 1, "leader_name": "Victoria", "civ_short": "England",
                 "is_human": False, "at_war_with_speaker": False,
                 "attitude_toward_speaker": "Cautious"},
                {"player_id": 2, "leader_name": "Lincoln", "civ_short": "America",
                 "is_human": False, "at_war_with_speaker": False,
                 "attitude_toward_speaker": "Pleased"},
                {"player_id": 4, "leader_name": "Ragnar", "civ_short": "Vikings",
                 "is_human": False, "at_war_with_speaker": False,
                 "attitude_toward_speaker": "Pleased"},
            ],
            "relations": [
                {"from_pid": 1, "to_pid": 2, "attitude": "Furious", "at_war": True,
                 "at_war_turns": 8, "war_success": 12,
                 "memories": [{"name": "DECLARED_WAR", "count": 1}]},
                {"from_pid": 2, "to_pid": 4, "attitude": "Friendly", "at_war": False,
                 "has_defensive_pact": True, "has_open_borders": True},
            ],
        }
        sys_msg, _ = prompts.build_chat_reply_prompt(request, [], room_state=room_state)
        # War line: keep the original "(at war)" substring so legacy tests
        # are not broken, but extend it with the duration when known.
        self.assertIn("Victoria -> Lincoln: Furious (at war 8t)", sys_msg)
        self.assertIn("grudges: declared war on you", sys_msg)
        # Peace line with structural state suffixes.
        self.assertIn("Lincoln -> Ragnar: Friendly", sys_msg)
        self.assertIn("defensive pact", sys_msg)
        self.assertIn("open borders", sys_msg)

    def test_relations_war_with_unknown_duration_omits_t_suffix(self):
        """When at_war_turns is missing or 0 we still mark the war but
        omit the misleading '0t' duration."""
        request = self._base_request()
        room_state = {
            "speaker_id": 3,
            "roster": [
                {"player_id": 1, "leader_name": "Victoria", "civ_short": "England",
                 "is_human": False, "at_war_with_speaker": False,
                 "attitude_toward_speaker": "Cautious"},
                {"player_id": 2, "leader_name": "Lincoln", "civ_short": "America",
                 "is_human": False, "at_war_with_speaker": False,
                 "attitude_toward_speaker": "Pleased"},
            ],
            "relations": [
                {"from_pid": 1, "to_pid": 2, "attitude": "Furious", "at_war": True},
            ],
        }
        sys_msg, _ = prompts.build_chat_reply_prompt(request, [], room_state=room_state)
        self.assertIn("Victoria -> Lincoln: Furious (at war)", sys_msg)
        self.assertNotIn("(at war 0t)", sys_msg)

    def test_relations_priority_sort_wars_first(self):
        """When more relations exist than the 12-line cap can show,
        wars and pacts surface first instead of being clipped."""
        request = self._base_request()
        roster = []
        relations = []
        # 15 bland relations + 1 war == cap forces something to drop.
        for i in range(15):
            pid = 100 + i
            roster.append({"player_id": pid, "leader_name": "Boring" + str(i),
                           "civ_short": "Civ" + str(i),
                           "is_human": False, "at_war_with_speaker": False,
                           "attitude_toward_speaker": "Cautious"})
            if i > 0:
                relations.append({"from_pid": 100, "to_pid": pid,
                                  "attitude": "Cautious", "at_war": False})
        roster.append({"player_id": 200, "leader_name": "Warmaker",
                       "civ_short": "Hordes",
                       "is_human": False, "at_war_with_speaker": False,
                       "attitude_toward_speaker": "Cautious"})
        relations.append({"from_pid": 100, "to_pid": 200,
                          "attitude": "Furious", "at_war": True,
                          "at_war_turns": 4})
        room_state = {"speaker_id": 3, "roster": roster, "relations": relations}
        sys_msg, _ = prompts.build_chat_reply_prompt(request, [], room_state=room_state)
        self.assertIn("Boring0 -> Warmaker: Furious (at war 4t)", sys_msg)

    def test_humanize_memories_empty_input(self):
        """Direct helper test: empty/None input yields empty list."""
        self.assertEqual(prompts._humanize_memories(None), [])
        self.assertEqual(prompts._humanize_memories([]), [])
        self.assertEqual(prompts._humanize_memories([{"name": "", "count": 5}]), [])
        self.assertEqual(prompts._humanize_memories([{"name": "DECLARED_WAR",
                                                     "count": 0}]), [])

    def test_humanize_memories_count_formatting(self):
        """Count >=2 emits 'x<N>' suffix; count==1 emits bare phrase."""
        out = prompts._humanize_memories([
            {"name": "DECLARED_WAR", "count": 1},
            {"name": "RAZED_CITY", "count": 2},
            {"name": "NUKED_US", "count": 7},
        ])
        self.assertEqual(out, [
            "declared war on you",
            "razed your city x2",
            "nuked you x7",
        ])


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
        # Refusal substitutes a fallback canned line; we still return ok=True
        # so the user sees something rather than silence.
        self.assertTrue(resp["ok"])
        self.assertEqual(len(resp["lines"]), 1)
        text = resp["lines"][0]["text"]
        # Canned fallbacks reference the speaker name and are short.
        self.assertIn("Victoria", text)

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
        # When the LLM returns garbage that can't be parsed AND has no
        # salvageable "line":"..." fragments, the daemon falls back to a
        # canned stock line instead of broadcasting the raw text. This
        # prevents JSON scaffolding (or partial / truncated output) from
        # ever being spoken aloud.
        client = self._fake_client(text="not valid json at all")
        req = self._basic_request(multi_turn=True, n_lines=3)
        resp = self.daemon.process_request(
            Path("dummy"), req,
            client=client, breaker=self.breaker, logger=self.logger,
            max_tokens=80, max_tokens_multi=400,
        )
        self.assertTrue(resp["ok"])
        self.assertEqual(len(resp["lines"]), 1)
        # MUST NOT be the raw garbage text -- the whole point of the fix
        # is that we never broadcast unparseable LLM output.
        self.assertNotEqual(resp["lines"][0]["text"], "not valid json at all")
        # Should be a stock fallback line (non-empty, natural prose).
        self.assertGreater(len(resp["lines"][0]["text"]), 5)


class TestParseChatReplyHardening(unittest.TestCase):
    """Regression guards for parse_chat_reply.

    History: production saw the LLM emit ``{"`` as a chat-reply (Grok
    running out of tokens mid-JSON). The old parser fell back to the raw
    text, so ``{"`` got post-filtered to a non-empty string and was
    actually spoken aloud by TTS. These tests lock down the parser so
    truncated / degenerate JSON cannot leak through as a speakable line.
    """

    def test_truncated_open_brace_returns_empty_line(self):
        got = azure_client.parse_chat_reply('{')
        self.assertEqual(got["line"], "")

    def test_truncated_brace_quote_returns_empty_line(self):
        # The exact Churchill bug from the daemon log.
        got = azure_client.parse_chat_reply('{"')
        self.assertEqual(got["line"], "")

    def test_truncated_line_field_returns_empty_line(self):
        got = azure_client.parse_chat_reply('{"line":"...')
        self.assertEqual(got["line"], "")

    def test_truncated_array_returns_empty_line(self):
        got = azure_client.parse_chat_reply('[')
        self.assertEqual(got["line"], "")

    def test_json_with_brace_only_line_returns_empty(self):
        # Even when JSON parses cleanly, a degenerate line value must be rejected.
        got = azure_client.parse_chat_reply('{"line":"{","tone":"menacing"}')
        self.assertEqual(got["line"], "")

    def test_json_with_empty_line_returns_empty(self):
        got = azure_client.parse_chat_reply('{"line":"","tone":"menacing"}')
        self.assertEqual(got["line"], "")

    def test_valid_json_passes_through(self):
        got = azure_client.parse_chat_reply(
            '{"line":"Your fleets rot in port, fool.","tone":"menacing"}'
        )
        self.assertEqual(got["line"], "Your fleets rot in port, fool.")
        self.assertEqual(got["tone"], "menacing")

    def test_natural_prose_without_wrapper_passes_through(self):
        # Graceful fallback for LLMs that forget the JSON envelope but
        # emit natural speakable text.
        got = azure_client.parse_chat_reply("Your legions march at dawn, fool.")
        self.assertEqual(got["line"], "Your legions march at dawn, fool.")

    def test_short_garbage_returns_empty_line(self):
        got = azure_client.parse_chat_reply("xx")
        self.assertEqual(got["line"], "")

    def test_invalid_tone_coerced_to_theatrical(self):
        got = azure_client.parse_chat_reply(
            '{"line":"A reasonable retort.","tone":"sassy"}'
        )
        self.assertEqual(got["tone"], "theatrical")

    def test_address_to_preserved_when_string(self):
        got = azure_client.parse_chat_reply(
            '{"line":"Victoria, be silent.","tone":"cold","address_to":"Victoria"}'
        )
        self.assertEqual(got["address_to"], "Victoria")

    def test_is_speakable_line_rejects_degenerate(self):
        rej = ["", " ", "a", "{", "}", "{}", '{"', "[", "]", "{leader}", '"', "..."]
        for t in rej:
            self.assertFalse(
                azure_client._is_speakable_line(t),
                msg="should reject %r as non-speakable" % t,
            )

    def test_is_speakable_line_accepts_natural(self):
        ok = ["Hi there", "Yes.", "No, you are wrong.", "Tokugawa, my legions await."]
        for t in ok:
            self.assertTrue(
                azure_client._is_speakable_line(t),
                msg="should accept %r as speakable" % t,
            )


if __name__ == "__main__":
    unittest.main()
