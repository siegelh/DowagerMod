"""Tests for the @-mention ask: command.

Covers:
- _parse_ask_command: parses plain 'ask:', 'ask as <leader>:', and rejects non-ask text
- _resolve_ask_voice: returns default Hindi voice + Gandhi persona when no leader; routes
  named leaders through voice_picker
- _build_ask_prompt: applies SPICY/ANTI_CLICHE/STRUCTURAL_VARIETY directives and the
  TTS-friendliness rules (no markdown, no code blocks)
"""
from __future__ import annotations

import unittest
from unittest import mock

from tools.chatter import chatter_daemon as cd


class TestParseAskCommand(unittest.TestCase):
    def test_plain_ask_returns_no_leader(self):
        out = cd._parse_ask_command("ask: what is the capital of France?")
        self.assertEqual(out, (None, "what is the capital of France?"))

    def test_ask_as_leader_extracts_name(self):
        out = cd._parse_ask_command("ask as Stalin: who killed Trotsky?")
        self.assertEqual(out, ("Stalin", "who killed Trotsky?"))

    def test_ask_as_multi_word_leader(self):
        out = cd._parse_ask_command("ask as Catherine the Great: was Russia truly yours?")
        self.assertEqual(out, ("Catherine the Great", "was Russia truly yours?"))

    def test_ask_is_case_insensitive(self):
        out = cd._parse_ask_command("ASK AS GANDHI: tea or coffee?")
        self.assertEqual(out, ("GANDHI", "tea or coffee?"))
        out = cd._parse_ask_command("Ask: hi there")
        self.assertEqual(out, (None, "hi there"))

    def test_ask_tolerates_leading_whitespace(self):
        out = cd._parse_ask_command("   ask:   spaced question  ")
        self.assertEqual(out, (None, "spaced question"))

    def test_ask_multiline_question_preserved(self):
        out = cd._parse_ask_command("ask: line one\nline two\nline three")
        self.assertEqual(out, (None, "line one\nline two\nline three"))

    def test_non_ask_text_returns_none(self):
        self.assertIsNone(cd._parse_ask_command("hello there"))
        self.assertIsNone(cd._parse_ask_command(""))
        self.assertIsNone(cd._parse_ask_command(None))

    def test_ask_without_question_returns_none(self):
        self.assertIsNone(cd._parse_ask_command("ask: "))
        self.assertIsNone(cd._parse_ask_command("ask as Stalin:    "))

    def test_does_not_match_ask_in_middle_of_sentence(self):
        # 'I want to ask: something' is conversational, not a command.
        # The pattern is anchored to start-of-string (after whitespace).
        self.assertIsNone(cd._parse_ask_command("I want to ask: something"))

    def test_leader_name_with_apostrophe(self):
        out = cd._parse_ask_command("ask as Mao's son: hi")
        self.assertEqual(out, ("Mao's son", "hi"))


class TestResolveAskVoice(unittest.TestCase):
    def test_no_leader_uses_default_gandhi_voice(self):
        voice, rate, pitch, persona, _, _provider = cd._resolve_ask_voice(None, None)
        self.assertEqual(voice, "en-IN-PrabhatNeural")
        self.assertEqual(rate, "")
        self.assertEqual(pitch, "")
        self.assertIn("Gandhi", persona)
        self.assertIn("Indian", persona)

    def test_default_when_voice_picker_present_no_leader(self):
        vp = mock.Mock()
        voice, rate, pitch, persona, _, _provider = cd._resolve_ask_voice(vp, None)
        self.assertEqual(voice, "en-IN-PrabhatNeural")
        # voice_picker must NOT be consulted when no leader was named.
        vp.pick_spec.assert_not_called()
        self.assertIn("Gandhi", persona)

    def test_named_leader_routes_through_voice_picker(self):
        vp = mock.Mock()
        spec = mock.Mock()
        spec.voice = "ka-GE-GiorgiNeural"
        spec.rate = "-5%"
        spec.pitch = "-8%"
        vp.pick_spec.return_value = spec
        voice, rate, pitch, persona, _, _provider = cd._resolve_ask_voice(vp, "Stalin")
        self.assertEqual(voice, "ka-GE-GiorgiNeural")
        self.assertEqual(rate, "-5%")
        self.assertEqual(pitch, "-8%")
        self.assertIn("Stalin", persona)
        vp.pick_spec.assert_called_once_with("Stalin")

    def test_named_leader_with_no_voice_picker_falls_back_to_default(self):
        voice, rate, pitch, persona, _, _provider = cd._resolve_ask_voice(None, "Stalin")
        self.assertEqual(voice, "en-IN-PrabhatNeural")
        # Persona still reflects the requested leader, even though the
        # voice fell back.
        self.assertIn("Stalin", persona)


class TestBuildAskPrompt(unittest.TestCase):
    def test_system_msg_contains_persona(self):
        sys_msg, user_msg = cd._build_ask_prompt(
            "what is your favorite color?",
            "the historical leader Stalin",
        )
        self.assertIn("Stalin", sys_msg)
        self.assertEqual(user_msg, "what is your favorite color?")

    def test_system_msg_includes_tts_friendliness_rules(self):
        sys_msg, _ = cd._build_ask_prompt("hi", "Gandhi")
        # The output rules section must explicitly forbid markdown/code blocks
        # so the TTS layer doesn't end up reading "asterisk asterisk" out loud.
        self.assertIn("No markdown", sys_msg)
        self.assertIn("code blocks", sys_msg)

    def test_system_msg_includes_spicy_directives(self):
        sys_msg, _ = cd._build_ask_prompt("hi", "Gandhi")
        # Same spicy + anti-cliche pipeline as in-game commentary.
        self.assertIn("SPICY MODE", sys_msg)
        self.assertIn("ANTI-CLICHÉ", sys_msg)
        self.assertIn("crumbling", sys_msg)

    def test_anachronism_is_allowed(self):
        sys_msg, _ = cd._build_ask_prompt("hi", "Gandhi")
        # We tell the LLM to answer anachronistic questions in character
        # rather than refuse them.
        self.assertIn("anachronism", sys_msg)


class TestBuildAskPromptBare(unittest.TestCase):
    """The 'ask as <Leader>:' path intentionally sends no system prompt --
    just the user's raw question through the LLM, with the leader's voice
    applied only at TTS time."""

    def test_bare_system_msg_is_empty(self):
        sys_msg, user_msg = cd._build_ask_prompt_bare("what is 2 + 2?")
        self.assertEqual(sys_msg, "")
        self.assertEqual(user_msg, "what is 2 + 2?")

    def test_bare_does_not_include_persona_or_directives(self):
        sys_msg, _ = cd._build_ask_prompt_bare("hi")
        self.assertNotIn("SPICY", sys_msg)
        self.assertNotIn("ANTI-CLICHÉ", sys_msg)
        self.assertNotIn("Gandhi", sys_msg)
        self.assertNotIn("persona", sys_msg.lower())

    def test_bare_preserves_question_verbatim(self):
        q = "line one\nline two\n  with spacing  "
        _, user_msg = cd._build_ask_prompt_bare(q)
        self.assertEqual(user_msg, q)


class TestParseSayCommand(unittest.TestCase):
    def test_plain_say_returns_no_leader(self):
        out = cd._parse_say_command("say: hello there")
        self.assertEqual(out, (None, "hello there"))

    def test_say_as_leader_extracts_name(self):
        out = cd._parse_say_command("say as Stalin: glory to the motherland")
        self.assertEqual(out, ("Stalin", "glory to the motherland"))

    def test_say_as_multi_word_leader(self):
        out = cd._parse_say_command("say as Dowager Countess: what insolence")
        self.assertEqual(out, ("Dowager Countess", "what insolence"))

    def test_say_is_case_insensitive(self):
        self.assertEqual(cd._parse_say_command("Say: hi"), (None, "hi"))
        self.assertEqual(cd._parse_say_command("SAY AS GANDHI: hi"), ("GANDHI", "hi"))

    def test_say_tolerates_leading_whitespace(self):
        self.assertEqual(
            cd._parse_say_command("   say:   spaced  "),
            (None, "spaced"),
        )

    def test_say_multiline_preserved(self):
        self.assertEqual(
            cd._parse_say_command("say: line one\nline two"),
            (None, "line one\nline two"),
        )

    def test_non_say_text_returns_none(self):
        self.assertIsNone(cd._parse_say_command("hello there"))
        self.assertIsNone(cd._parse_say_command(""))
        self.assertIsNone(cd._parse_say_command(None))

    def test_say_without_text_returns_none(self):
        self.assertIsNone(cd._parse_say_command("say:"))
        self.assertIsNone(cd._parse_say_command("say as Stalin:    "))

    def test_does_not_match_say_in_middle(self):
        # "I want to say: hello" is conversational, not a command.
        self.assertIsNone(cd._parse_say_command("I want to say: hello"))

    def test_say_does_not_match_ask(self):
        # Make sure say pattern doesn't swallow ask: prefix.
        self.assertIsNone(cd._parse_say_command("ask: what time is it"))

    def test_ask_does_not_match_say(self):
        # And vice versa.
        self.assertIsNone(cd._parse_ask_command("say: hello"))


if __name__ == "__main__":
    unittest.main()
