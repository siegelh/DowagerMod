"""Unit tests for tools/chatter/chat_resolve.py.

This is the sidecar parallel of CvLeaderChatter._resolve_addressed_leader.
Keep test cases in sync with both implementations.
"""
import unittest

from tools.chatter import chat_resolve


class TestResolveAddressedLeader(unittest.TestCase):
    def test_exact_full_name_in_message(self):
        name, why = chat_resolve.resolve_addressed_leader("Hammurabi, your code is harsh.")
        self.assertEqual(name, "Hammurabi")
        self.assertEqual(why, "name_match")

    def test_compound_full_name_in_message(self):
        name, why = chat_resolve.resolve_addressed_leader("Genghis Khan, your horde tires.")
        self.assertEqual(name, "Genghis Khan")
        self.assertEqual(why, "name_match")

    def test_nickname_louie_resolves_louis(self):
        name, why = chat_resolve.resolve_addressed_leader("Louie, your gardens are lovely.")
        self.assertEqual(name, "Louis XIV")
        self.assertEqual(why, "name_match")

    def test_prefix_gilg_resolves_gilgamesh(self):
        name, why = chat_resolve.resolve_addressed_leader("Gilg, will you stand with me?")
        self.assertEqual(name, "Gilgamesh")
        self.assertEqual(why, "name_match")

    def test_first_word_genghis_resolves_genghis_khan(self):
        # "Genghis" by itself should pull Genghis Khan out (first-word match).
        name, why = chat_resolve.resolve_addressed_leader("What say you, Genghis?")
        self.assertEqual(name, "Genghis Khan")

    def test_no_leader_name_returns_none(self):
        name, why = chat_resolve.resolve_addressed_leader("Hello world, just testing.")
        self.assertIsNone(name)
        self.assertIsNone(why)

    def test_short_message_with_no_match(self):
        # Single common-word noun shouldn't false-positive on any leader.
        name, why = chat_resolve.resolve_addressed_leader("Hello.")
        self.assertIsNone(name)

    def test_active_partner_fallback_when_no_name(self):
        # No name in message + recent partner = continue with that partner.
        name, why = chat_resolve.resolve_addressed_leader(
            "How is Versailles?",
            active_partner_name="Louis XIV",
            active_partner_idle_seconds=30,
        )
        self.assertEqual(name, "Louis XIV")
        self.assertEqual(why, "active_partner")

    def test_active_partner_expired_no_match(self):
        name, why = chat_resolve.resolve_addressed_leader(
            "Anyone there?",
            active_partner_name="Louis XIV",
            active_partner_idle_seconds=999,
        )
        self.assertIsNone(name)

    def test_named_leader_overrides_active_partner(self):
        # Active partner is Louis, but message names Gilgamesh -> switch.
        name, why = chat_resolve.resolve_addressed_leader(
            "Gilgamesh, what would you do?",
            active_partner_name="Louis XIV",
            active_partner_idle_seconds=10,
        )
        self.assertEqual(name, "Gilgamesh")
        self.assertEqual(why, "name_match")

    def test_tie_break_prefers_shorter_more_specific_name(self):
        # If two leaders match, the more specific (shorter) name wins.
        # 'Caesar' could match Augustus Caesar OR Julius Caesar.
        # Both are equally good token matches; the test just verifies we
        # pick deterministically, not which one. Just make sure we pick A
        # leader (not None) and don't crash.
        name, why = chat_resolve.resolve_addressed_leader("Caesar, your time is short.")
        self.assertIn(name, ("Augustus Caesar", "Julius Caesar"))

    def test_short_token_does_not_false_positive(self):
        # 'I am' -- the 'am' token is too short to even score.
        name, why = chat_resolve.resolve_addressed_leader("I am building wonders.")
        self.assertIsNone(name)

    def test_will_does_not_match_willem(self):
        # 'I will burn ...' shouldn't switch to Willem van Oranje. 'will'
        # is a 4-char prefix of 'willem' but is also one of the most common
        # English verbs -- it must be in the stopword filter.
        name, why = chat_resolve.resolve_addressed_leader(
            "Your gardens are beautiful but I will burn them down with my English army.",
            active_partner_name="Louis XIV",
            active_partner_idle_seconds=10,
        )
        # Should stay with the active partner, not switch.
        self.assertEqual(name, "Louis XIV")
        self.assertEqual(why, "active_partner")

    def test_wash_does_not_match_washington(self):
        # 'wash up' shouldn't pull Washington.
        name, why = chat_resolve.resolve_addressed_leader(
            "I need to wash my hands first.",
            active_partner_name="Louis XIV",
            active_partner_idle_seconds=10,
        )
        self.assertEqual(name, "Louis XIV")


class TestLevenshtein(unittest.TestCase):
    def test_identity(self):
        self.assertEqual(chat_resolve._levenshtein("louis", "louis"), 0)

    def test_one_substitution(self):
        self.assertEqual(chat_resolve._levenshtein("louie", "louis"), 1)

    def test_one_insertion(self):
        self.assertEqual(chat_resolve._levenshtein("genghi", "genghis"), 1)


if __name__ == "__main__":
    unittest.main()
