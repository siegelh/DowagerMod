"""Tests for the per-leader recent-lines ring buffer in StateStore and
the AVOID-ECHOING-YOURSELF prompt block in build_single_line_prompt /
build_multi_turn_prompt.

These pin the anti-repetition machinery added in response to real-game
feedback: every leader kept reaching for the same poetic words
("crumbling", "ashes", etc.) because each commentary call was amnesiac.
The fix: record every spoken line per (session, leader) and feed the
last few back into the next prompt as an explicit "do not echo" block.
"""
from __future__ import annotations

import unittest

from tools.chatter import prompts
from tools.chatter.state import StateStore, RECENT_LINES_PER_LEADER


class TestStateStoreRecentLines(unittest.TestCase):
    def test_record_and_read_round_trip(self):
        s = StateStore()
        s.record_line("sess-1", 3, "First line.")
        s.record_line("sess-1", 3, "Second line.")
        out = s.recent_lines("sess-1", 3)
        self.assertEqual(out, ["First line.", "Second line."])

    def test_recent_lines_empty_when_unseen(self):
        s = StateStore()
        self.assertEqual(s.recent_lines("sess-1", 99), [])

    def test_per_leader_isolation(self):
        s = StateStore()
        s.record_line("sess-1", 3, "Alice line.")
        s.record_line("sess-1", 4, "Bob line.")
        self.assertEqual(s.recent_lines("sess-1", 3), ["Alice line."])
        self.assertEqual(s.recent_lines("sess-1", 4), ["Bob line."])

    def test_per_session_isolation(self):
        s = StateStore()
        s.record_line("sess-1", 3, "Game 1.")
        s.record_line("sess-2", 3, "Game 2.")
        self.assertEqual(s.recent_lines("sess-1", 3), ["Game 1."])
        self.assertEqual(s.recent_lines("sess-2", 3), ["Game 2."])

    def test_ring_buffer_caps_at_max(self):
        s = StateStore()
        for i in range(RECENT_LINES_PER_LEADER + 5):
            s.record_line("sess-1", 3, "line %d" % i)
        out = s.recent_lines("sess-1", 3)
        self.assertEqual(len(out), RECENT_LINES_PER_LEADER)
        # Oldest dropped; the buffer should hold the most-recent N.
        self.assertEqual(out[0], "line 5")
        self.assertEqual(out[-1], "line %d" % (RECENT_LINES_PER_LEADER + 4))

    def test_empty_text_is_dropped_silently(self):
        s = StateStore()
        s.record_line("sess-1", 3, "")
        s.record_line("sess-1", 3, "   ")
        s.record_line("sess-1", 3, "kept")
        self.assertEqual(s.recent_lines("sess-1", 3), ["kept"])

    def test_invalid_player_id_dropped_silently(self):
        s = StateStore()
        s.record_line("sess-1", None, "ignored")
        s.record_line("sess-1", "not-an-int", "ignored")
        s.record_line("sess-1", -1, "ignored")
        # Nothing got recorded so nothing comes back.
        self.assertEqual(s.recent_lines("sess-1", 0), [])

    def test_lines_are_stripped(self):
        s = StateStore()
        s.record_line("sess-1", 3, "  padded line  \n")
        self.assertEqual(s.recent_lines("sess-1", 3), ["padded line"])

    def test_reset_session_clears_recent_lines(self):
        s = StateStore()
        s.record_line("sess-1", 3, "gone")
        s.record_line("sess-2", 3, "kept")
        s.reset_session("sess-1")
        self.assertEqual(s.recent_lines("sess-1", 3), [])
        self.assertEqual(s.recent_lines("sess-2", 3), ["kept"])

    def test_reset_all_clears_everything(self):
        s = StateStore()
        s.record_line("sess-1", 3, "x")
        s.record_line("sess-2", 4, "y")
        s.reset_all()
        self.assertEqual(s.recent_lines("sess-1", 3), [])
        self.assertEqual(s.recent_lines("sess-2", 4), [])


class TestRecentLinesInPrompts(unittest.TestCase):
    def _base_request(self, trigger="DECLARE_WAR"):
        return {
            "trigger": trigger,
            "game_turn": 50,
            "speaker": {"leader_name": "Stalin", "civ_short_name": "Russia"},
            "target": {"leader_name": "Victoria", "civ_short_name": "England"},
            "context": {"era": "industrial"},
        }

    def test_single_line_prompt_includes_recent_lines_block_when_provided(self):
        sys_msg, _ = prompts.build_single_line_prompt(
            self._base_request(),
            recent_lines=["Your fleets rot in port.", "England starves."],
        )
        self.assertIn("AVOID ECHOING YOURSELF", sys_msg)
        self.assertIn("Your fleets rot in port.", sys_msg)
        self.assertIn("England starves.", sys_msg)
        self.assertIn("Stalin", sys_msg)

    def test_single_line_prompt_omits_block_when_no_recent(self):
        sys_msg, _ = prompts.build_single_line_prompt(self._base_request())
        self.assertNotIn("AVOID ECHOING YOURSELF", sys_msg)

    def test_single_line_prompt_omits_block_when_empty_list(self):
        sys_msg, _ = prompts.build_single_line_prompt(
            self._base_request(), recent_lines=[],
        )
        self.assertNotIn("AVOID ECHOING YOURSELF", sys_msg)

    def test_single_line_prompt_omits_block_when_only_blanks(self):
        sys_msg, _ = prompts.build_single_line_prompt(
            self._base_request(), recent_lines=["", "   ", None],
        )
        self.assertNotIn("AVOID ECHOING YOURSELF", sys_msg)

    def test_multi_turn_prompt_includes_both_recent_blocks(self):
        sys_msg, _ = prompts.build_multi_turn_prompt(
            self._base_request(),
            recent_lines=["Stalin previous A."],
            target_recent_lines=["Victoria previous B."],
        )
        self.assertIn("AVOID ECHOING YOURSELF", sys_msg)
        self.assertIn("Stalin previous A.", sys_msg)
        self.assertIn("Victoria previous B.", sys_msg)

    def test_spicy_directive_present_in_directed(self):
        # Phase 1 sanity: the spicy + anti-cliche directives must reach
        # the actually-rendered prompt the daemon ships to the LLM.
        sys_msg, _ = prompts.build_single_line_prompt(self._base_request())
        self.assertIn("SPICY MODE", sys_msg)
        self.assertIn("ANTI-CLICHÉ", sys_msg)
        # And one of our banned words must be explicitly named so the LLM
        # has it in front of it.
        self.assertIn("crumbling", sys_msg)


if __name__ == "__main__":
    unittest.main()
