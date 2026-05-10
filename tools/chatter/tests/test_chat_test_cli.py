"""Smoke tests for tools/chatter/chat_test.py CLI harness.

Mocks the LLM (handle_chat_reply) so no Azure call is made. Validates:
- --list-leaders prints the roster.
- --leader fuzzy resolution works.
- One-shot --message produces a valid response shape.
- --no-voice path doesn't attempt synthesis.
- REPL meta-commands (:leader, :help, :reset, :switch, :quit).
"""
import io
import sys
import unittest
from unittest import mock

from tools.chatter import chat_test


def _fake_handle_chat_reply(*, request, store, client, max_tokens, logger):
    """Drop-in replacement that doesn't call any LLM. Returns an angry tone."""
    speaker = request.get("speaker") or {}
    line = "How dare you, " + (request.get("target") or {}).get("human_name", "fool") + "!"
    tone = "angry"
    # Walk through the same store-append discipline as the real handler so
    # tests for history can verify it works.
    key = (request.get("session_id"), int(speaker.get("player_id", -1)))
    user_msg = (request.get("context") or {}).get("user_message") or ""
    if user_msg:
        store.append_user(key, user_msg, leader_name=speaker.get("leader_name", ""))
        store.append_assistant(key, line)
    return (
        {
            "schema": 1,
            "request_id": request.get("request_id"),
            "session_id": request.get("session_id"),
            "ok": True,
            "lines": [{"text": line, "tone": tone, "speaker_player_id": speaker.get("player_id")}],
            "trigger": "CHAT_REPLY",
            "latency_ms": 1, "input_tokens": 1, "output_tokens": 1,
            "error": None,
        },
        line,
        tone,
    )


class _CapturingStdout:
    def __init__(self):
        self.buf = io.StringIO()

    def __enter__(self):
        self._prev = sys.stdout
        sys.stdout = self.buf
        return self.buf

    def __exit__(self, *exc):
        sys.stdout = self._prev


class TestLeaderResolution(unittest.TestCase):
    def test_exact_match(self):
        self.assertEqual(chat_test._resolve_leader_arg("Louis XIV"), "Louis XIV")

    def test_nickname(self):
        self.assertEqual(chat_test._resolve_leader_arg("Louie"), "Louis XIV")

    def test_prefix(self):
        self.assertEqual(chat_test._resolve_leader_arg("Gilg"), "Gilgamesh")

    def test_no_match(self):
        self.assertIsNone(chat_test._resolve_leader_arg("Banana"))

    def test_empty(self):
        self.assertIsNone(chat_test._resolve_leader_arg(""))


class TestListLeaders(unittest.TestCase):
    def test_list_leaders_exits_zero_and_prints_roster(self):
        with _CapturingStdout() as buf:
            rc = chat_test.main(["--list-leaders"])
        self.assertEqual(rc, 0)
        out = buf.getvalue()
        # Spot-check a few canonical leaders are present.
        self.assertIn("Louis XIV", out)
        self.assertIn("Gilgamesh", out)
        self.assertIn("Hammurabi", out)


class TestArgParsingErrors(unittest.TestCase):
    def test_no_leader_returns_2(self):
        with mock.patch("tools.chatter.chat_test.load_config") as lc:
            cfg = mock.MagicMock()
            cfg.endpoint = "x"
            cfg.api_key = "y"
            cfg.deployment = "z"
            cfg.api_version = "v1"
            cfg.chat_history_seconds = 600
            cfg.chat_max_history_turns = 24
            cfg.chat_reply_max_tokens = 120
            cfg.request_timeout_seconds = 8.0
            lc.return_value = cfg
            rc = chat_test.main(["--message", "hi"])  # missing --leader
        self.assertEqual(rc, 2)

    def test_unknown_leader_returns_2(self):
        with mock.patch("tools.chatter.chat_test.load_config") as lc:
            cfg = mock.MagicMock()
            cfg.endpoint = "x"
            cfg.api_key = "y"
            cfg.deployment = "z"
            cfg.api_version = "v1"
            cfg.chat_history_seconds = 600
            cfg.chat_max_history_turns = 24
            cfg.chat_reply_max_tokens = 120
            cfg.request_timeout_seconds = 8.0
            lc.return_value = cfg
            rc = chat_test.main(["--leader", "Banana", "--message", "hi"])
        self.assertEqual(rc, 2)

    def test_no_endpoint_returns_2(self):
        with mock.patch("tools.chatter.chat_test.load_config") as lc:
            cfg = mock.MagicMock()
            cfg.endpoint = ""  # missing
            cfg.api_key = ""
            lc.return_value = cfg
            rc = chat_test.main(["--leader", "Louis XIV", "--message", "hi"])
        self.assertEqual(rc, 2)

    def test_message_and_repl_returns_2(self):
        with mock.patch("tools.chatter.chat_test.load_config") as lc, \
             mock.patch("tools.chatter.chat_test.AzureClient"):
            cfg = mock.MagicMock()
            cfg.endpoint = "x"; cfg.api_key = "y"; cfg.deployment = "z"
            cfg.api_version = "v1"
            cfg.chat_history_seconds = 600
            cfg.chat_max_history_turns = 24
            cfg.chat_reply_max_tokens = 120
            cfg.request_timeout_seconds = 8.0
            cfg.voiceover.azure_speech_endpoint = ""
            cfg.voiceover.azure_speech_key = ""
            cfg.voiceover.speech_rate = ""
            cfg.voiceover.azure_speech_voice = "x"
            cfg.voiceover.daily_char_cap = 100
            lc.return_value = cfg
            rc = chat_test.main(["--leader", "Louis XIV", "--message", "hi", "--repl",
                                 "--no-voice"])
        self.assertEqual(rc, 2)


class TestOneShot(unittest.TestCase):
    def _mk_cfg(self):
        cfg = mock.MagicMock()
        cfg.endpoint = "https://example/"; cfg.api_key = "xx"; cfg.deployment = "z"
        cfg.api_version = "v1"
        cfg.chat_history_seconds = 600
        cfg.chat_max_history_turns = 24
        cfg.chat_reply_max_tokens = 120
        cfg.request_timeout_seconds = 8.0
        cfg.voiceover.azure_speech_endpoint = ""
        cfg.voiceover.azure_speech_key = ""
        cfg.voiceover.speech_rate = "+50%"
        cfg.voiceover.azure_speech_voice = "x"
        cfg.voiceover.daily_char_cap = 100
        return cfg

    def test_one_shot_no_voice_prints_line(self):
        with mock.patch("tools.chatter.chat_test.load_config") as lc, \
             mock.patch("tools.chatter.chat_test.AzureClient"), \
             mock.patch("tools.chatter.chat_test.handle_chat_reply",
                        side_effect=_fake_handle_chat_reply):
            lc.return_value = self._mk_cfg()
            with _CapturingStdout() as buf:
                rc = chat_test.main([
                    "--leader", "Louis XIV", "--message", "Tu es ridiculous, Louie!",
                    "--no-voice",
                ])
            out = buf.getvalue()
        self.assertEqual(rc, 0)
        self.assertIn("Louis XIV", out)
        self.assertIn("angry", out)
        # Effective rate should layer +12% on +50% base = +62%
        self.assertIn("+62%", out)

    def test_one_shot_failure_returns_1(self):
        def fail_handler(**kw):
            return ({"ok": False, "error": "api_failure", "lines": []}, "", "theatrical")
        with mock.patch("tools.chatter.chat_test.load_config") as lc, \
             mock.patch("tools.chatter.chat_test.AzureClient"), \
             mock.patch("tools.chatter.chat_test.handle_chat_reply",
                        side_effect=fail_handler):
            lc.return_value = self._mk_cfg()
            with _CapturingStdout():
                rc = chat_test.main([
                    "--leader", "Louis XIV", "--message", "hi",
                    "--no-voice",
                ])
        self.assertEqual(rc, 1)


class TestRepl(unittest.TestCase):
    def _mk_cfg(self):
        cfg = mock.MagicMock()
        cfg.endpoint = "https://example/"; cfg.api_key = "xx"; cfg.deployment = "z"
        cfg.api_version = "v1"
        cfg.chat_history_seconds = 600
        cfg.chat_max_history_turns = 24
        cfg.chat_reply_max_tokens = 120
        cfg.request_timeout_seconds = 8.0
        cfg.voiceover.azure_speech_endpoint = ""
        cfg.voiceover.azure_speech_key = ""
        cfg.voiceover.speech_rate = "+50%"
        cfg.voiceover.azure_speech_voice = "x"
        cfg.voiceover.daily_char_cap = 100
        return cfg

    def _run_repl_with_inputs(self, inputs):
        cfg = self._mk_cfg()
        # Drive input() with a queue.
        it = iter(inputs)
        with mock.patch("tools.chatter.chat_test.load_config", return_value=cfg), \
             mock.patch("tools.chatter.chat_test.AzureClient"), \
             mock.patch("tools.chatter.chat_test.handle_chat_reply",
                        side_effect=_fake_handle_chat_reply), \
             mock.patch("builtins.input", side_effect=lambda *_a, **_kw: next(it)):
            with _CapturingStdout() as buf:
                rc = chat_test.main([
                    "--leader", "Louis XIV", "--repl", "--no-voice",
                ])
        return rc, buf.getvalue()

    def test_quit_exits_cleanly(self):
        rc, out = self._run_repl_with_inputs([":quit"])
        self.assertEqual(rc, 0)
        self.assertIn("Louis XIV", out)

    def test_help_command(self):
        rc, out = self._run_repl_with_inputs([":help", ":quit"])
        self.assertEqual(rc, 0)
        self.assertIn("Meta commands:", out)
        self.assertIn(":switch NAME", out)

    def test_message_then_quit(self):
        rc, out = self._run_repl_with_inputs([
            "Tell me a story.",
            ":quit",
        ])
        self.assertEqual(rc, 0)
        self.assertIn("Louis XIV", out)
        self.assertIn("angry", out)

    def test_switch_leader_then_message(self):
        rc, out = self._run_repl_with_inputs([
            ":switch Gilgamesh",
            "Stand with me?",
            ":quit",
        ])
        self.assertEqual(rc, 0)
        self.assertIn("switched to Gilgamesh", out)
        # The reply line should be from Gilgamesh, not Louis.
        # We can't tell from the line text (mocked), but the bracket header
        # shows the leader name.
        self.assertIn("[Gilgamesh /", out)

    def test_reset_clears_history(self):
        rc, out = self._run_repl_with_inputs([
            "Hello.",
            ":reset",
            ":history",
            ":quit",
        ])
        self.assertEqual(rc, 0)
        self.assertIn("history cleared", out)
        self.assertIn("no history", out)

    def test_named_leader_in_message_switches(self):
        rc, out = self._run_repl_with_inputs([
            "Gilg, what would you do?",
            ":quit",
        ])
        self.assertEqual(rc, 0)
        self.assertIn("switched to Gilgamesh", out)

    def test_unknown_meta_command(self):
        rc, out = self._run_repl_with_inputs([":banana", ":quit"])
        self.assertEqual(rc, 0)
        self.assertIn("unknown command", out)


if __name__ == "__main__":
    unittest.main()
