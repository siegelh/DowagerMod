"""Unit tests for tools/chatter/chime_math.py.

These cover the pure-arithmetic core of the AI-to-AI chime-in math
(weight calc, probability decay, weighted pick). The game-side
_maybe_queue_chime function in CvLeaderChatter.py uses an inline copy
of the same constants and algorithm; if you change one, change the
other.
"""
import random
import unittest

from tools.chatter import chime_math


class TestCandidateWeight(unittest.TestCase):
    def test_known_attitudes(self):
        self.assertEqual(chime_math.candidate_weight("Furious", False), 4)
        self.assertEqual(chime_math.candidate_weight("Friendly", False), 4)
        self.assertEqual(chime_math.candidate_weight("Annoyed", False), 2)
        self.assertEqual(chime_math.candidate_weight("Pleased", False), 2)
        self.assertEqual(chime_math.candidate_weight("Cautious", False), 1)

    def test_unknown_attitude_defaults_to_cautious(self):
        self.assertEqual(chime_math.candidate_weight("", False), 1)
        self.assertEqual(chime_math.candidate_weight("BOGUS", False), 1)
        self.assertEqual(chime_math.candidate_weight(None, False), 1)

    def test_at_war_adds_bonus(self):
        self.assertEqual(chime_math.candidate_weight("Furious", True), 4 + 2)
        self.assertEqual(chime_math.candidate_weight("Cautious", True), 1 + 2)
        self.assertEqual(chime_math.candidate_weight("Friendly", True), 4 + 2)


class TestChimeProbability(unittest.TestCase):
    def test_depth_zero_is_base(self):
        self.assertAlmostEqual(chime_math.chime_probability(0), 0.5)

    def test_depth_one_is_decayed(self):
        self.assertAlmostEqual(chime_math.chime_probability(1), 0.5 * 0.6)

    def test_depth_two_is_double_decayed(self):
        self.assertAlmostEqual(chime_math.chime_probability(2), 0.5 * 0.6 * 0.6)

    def test_negative_depth_clamped_to_zero(self):
        self.assertEqual(chime_math.chime_probability(-1), 0.0)
        self.assertEqual(chime_math.chime_probability(-5), 0.0)


class TestWeightedPick(unittest.TestCase):
    def test_empty_returns_none(self):
        self.assertIsNone(chime_math.weighted_pick([]))

    def test_zero_weights_returns_none(self):
        self.assertIsNone(chime_math.weighted_pick([(1, 0), (2, 0)]))

    def test_single_candidate_always_picked(self):
        rng = random.Random(0)
        for _ in range(20):
            self.assertEqual(chime_math.weighted_pick([(7, 5)], rng=rng), 7)

    def test_heavy_weight_dominates(self):
        """A candidate with 10x weight should be picked >70% over 100 trials."""
        rng = random.Random(42)
        hits = 0
        for _ in range(100):
            pid = chime_math.weighted_pick([(1, 1), (2, 10)], rng=rng)
            if pid == 2:
                hits += 1
        self.assertGreater(hits, 70)

    def test_deterministic_with_seeded_rng(self):
        """Same seed gives same picks across runs -- enables MP determinism if needed."""
        rng1 = random.Random(123)
        rng2 = random.Random(123)
        picks1 = [chime_math.weighted_pick([(1, 2), (2, 3), (3, 1)], rng=rng1)
                  for _ in range(10)]
        picks2 = [chime_math.weighted_pick([(1, 2), (2, 3), (3, 1)], rng=rng2)
                  for _ in range(10)]
        self.assertEqual(picks1, picks2)

    def test_negative_weights_filtered_out(self):
        rng = random.Random(0)
        # Candidate 1 has weight -3 (illegal), candidate 2 has weight 4 (legal).
        for _ in range(20):
            pid = chime_math.weighted_pick([(1, -3), (2, 4)], rng=rng)
            self.assertEqual(pid, 2)


if __name__ == "__main__":
    unittest.main()
