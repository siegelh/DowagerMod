"""Tests for paralinguistic tag support in prompt builders."""
import unittest

from tools.chatter.prompts import (
    PARALINGUISTIC_DIRECTIVE,
    _STAGE_DIRECTION_BAN,
    apply_paralinguistic,
    _normalize_for_paralinguistic,
    build_single_line_prompt,
    build_multi_turn_prompt,
    build_chat_reply_prompt,
)


class TestNormalize(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(_normalize_for_paralinguistic("Charlemagne"), "charlemagne")

    def test_spaces_and_punctuation(self):
        self.assertEqual(_normalize_for_paralinguistic("George Washington"), "georgewashington")
        self.assertEqual(_normalize_for_paralinguistic("Qin Shi Huang"), "qinshihuang")

    def test_empty(self):
        self.assertEqual(_normalize_for_paralinguistic(""), "")


class TestApplyParalinguistic(unittest.TestCase):
    def test_swaps_ban_for_directive(self):
        msg = "Some preamble.\n" + _STAGE_DIRECTION_BAN + "Some suffix."
        result = apply_paralinguistic(msg)
        self.assertNotIn("NEVER use stage directions", result)
        self.assertIn("EXPRESSIVE SOUNDS", result)
        self.assertIn("[laugh]", result)

    def test_no_ban_still_appends(self):
        msg = "Clean system message with no ban line."
        result = apply_paralinguistic(msg)
        self.assertIn("EXPRESSIVE SOUNDS", result)


class TestSingleLinePromptParalinguistic(unittest.TestCase):
    """Verify chatterbox_voices enables/disables paralinguistic tags."""

    def _make_request(self, speaker="Charlemagne", target="Lincoln"):
        return {
            "trigger": "DECLARE_WAR",
            "speaker": {"leader_name": speaker, "civ_short_name": "Francia"},
            "target": {"leader_name": target, "civ_short_name": "America"},
            "context": {},
        }

    def test_no_chatterbox_voices_has_ban(self):
        sys_msg, _ = build_single_line_prompt(self._make_request())
        self.assertIn("NEVER use stage directions", sys_msg)
        self.assertNotIn("EXPRESSIVE SOUNDS", sys_msg)

    def test_empty_set_has_ban(self):
        sys_msg, _ = build_single_line_prompt(self._make_request(), chatterbox_voices=set())
        self.assertIn("NEVER use stage directions", sys_msg)
        self.assertNotIn("EXPRESSIVE SOUNDS", sys_msg)

    def test_speaker_in_set_enables_directive(self):
        voices = {"charlemagne", "washington"}
        sys_msg, _ = build_single_line_prompt(self._make_request(), chatterbox_voices=voices)
        self.assertNotIn("NEVER use stage directions", sys_msg)
        self.assertIn("EXPRESSIVE SOUNDS", sys_msg)

    def test_speaker_not_in_set_keeps_ban(self):
        voices = {"washington"}
        sys_msg, _ = build_single_line_prompt(self._make_request(speaker="Lincoln"), chatterbox_voices=voices)
        self.assertIn("NEVER use stage directions", sys_msg)
        self.assertNotIn("EXPRESSIVE SOUNDS", sys_msg)


class TestMultiTurnPromptParalinguistic(unittest.TestCase):
    def _make_request(self, speaker="Charlemagne", target="Washington"):
        return {
            "trigger": "DECLARE_WAR",
            "speaker": {"leader_name": speaker, "civ_short_name": "Francia"},
            "target": {"leader_name": target, "civ_short_name": "America"},
            "context": {},
        }

    def test_speaker_in_set_enables(self):
        voices = {"charlemagne"}
        sys_msg, _ = build_multi_turn_prompt(self._make_request(), chatterbox_voices=voices)
        self.assertIn("EXPRESSIVE SOUNDS", sys_msg)

    def test_target_in_set_enables(self):
        voices = {"washington"}
        sys_msg, _ = build_multi_turn_prompt(self._make_request(), chatterbox_voices=voices)
        self.assertIn("EXPRESSIVE SOUNDS", sys_msg)

    def test_neither_in_set_keeps_ban(self):
        voices = {"lincoln"}
        sys_msg, _ = build_multi_turn_prompt(self._make_request(), chatterbox_voices=voices)
        self.assertNotIn("EXPRESSIVE SOUNDS", sys_msg)


class TestChatReplyPromptParalinguistic(unittest.TestCase):
    def _make_request(self, speaker="Charlemagne"):
        return {
            "trigger": "CHAT_REPLY",
            "speaker": {"leader_name": speaker, "civ_short_name": "Francia"},
            "target": {"leader_name": "Player", "human_name": "Harrison"},
            "context": {"user_message": "Hello there"},
        }

    def test_speaker_in_set_enables(self):
        voices = {"charlemagne"}
        sys_msg, _ = build_chat_reply_prompt(
            self._make_request(),
            [{"role": "user", "content": "Hello there"}],
            chatterbox_voices=voices,
        )
        self.assertIn("EXPRESSIVE SOUNDS", sys_msg)

    def test_speaker_not_in_set_keeps_ban(self):
        voices = {"washington"}
        sys_msg, _ = build_chat_reply_prompt(
            self._make_request(),
            [{"role": "user", "content": "Hello there"}],
            chatterbox_voices=voices,
        )
        self.assertNotIn("EXPRESSIVE SOUNDS", sys_msg)


class TestAskPromptBareParalinguistic(unittest.TestCase):
    def test_chatterbox_leader_gets_directive(self):
        from tools.chatter.chatter_daemon import _build_ask_prompt_bare
        voices = {"charlemagne"}
        sys_msg, user_msg = _build_ask_prompt_bare(
            "What is the meaning of life?",
            chatterbox_voices=voices,
            leader_name="Charlemagne",
        )
        self.assertIn("EXPRESSIVE SOUNDS", sys_msg)
        self.assertEqual(user_msg, "What is the meaning of life?")

    def test_non_chatterbox_leader_stays_bare(self):
        from tools.chatter.chatter_daemon import _build_ask_prompt_bare
        voices = {"washington"}
        sys_msg, user_msg = _build_ask_prompt_bare(
            "What is the meaning of life?",
            chatterbox_voices=voices,
            leader_name="Charlemagne",
        )
        self.assertEqual(sys_msg, "")

    def test_no_chatterbox_stays_bare(self):
        from tools.chatter.chatter_daemon import _build_ask_prompt_bare
        sys_msg, user_msg = _build_ask_prompt_bare("Hello?")
        self.assertEqual(sys_msg, "")


if __name__ == "__main__":
    unittest.main()
