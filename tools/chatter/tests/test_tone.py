"""Unit tests for tools/chatter/tone.py."""
import unittest

from tools.chatter import tone


class TestProsodyFor(unittest.TestCase):
    def test_known_tones_distinct(self):
        # Each known tone should map to a (pitch, rate) tuple of strings.
        for t in ("angry", "amused", "haughty", "pleased", "cold",
                  "menacing", "wistful", "theatrical"):
            pitch, rate = tone.prosody_for(t)
            self.assertIsInstance(pitch, str)
            self.assertIsInstance(rate, str)

    def test_angry_is_fast_and_high(self):
        pitch, rate = tone.prosody_for("angry")
        self.assertEqual(pitch, "+8%")
        self.assertEqual(rate, "+12%")

    def test_menacing_is_slow_and_low(self):
        pitch, rate = tone.prosody_for("menacing")
        self.assertTrue(pitch.startswith("-"))
        self.assertTrue(rate.startswith("-"))

    def test_unknown_tone_falls_back_to_theatrical(self):
        unk = tone.prosody_for("nonsense")
        the = tone.prosody_for("theatrical")
        self.assertEqual(unk, the)

    def test_empty_tone_falls_back_to_theatrical(self):
        # Empty string should also map to theatrical (the neutral default).
        unk = tone.prosody_for("")
        the = tone.prosody_for("theatrical")
        self.assertEqual(unk, the)


class TestAddPercent(unittest.TestCase):
    def test_simple_addition(self):
        self.assertEqual(tone.add_percent("+50%", "+12%"), "+62%")

    def test_subtraction(self):
        self.assertEqual(tone.add_percent("+50%", "-10%"), "+40%")

    def test_negative_base(self):
        self.assertEqual(tone.add_percent("-5%", "+12%"), "+7%")

    def test_empty_base_uses_offset(self):
        self.assertEqual(tone.add_percent("", "+12%"), "+12%")

    def test_empty_offset_returns_base(self):
        self.assertEqual(tone.add_percent("+50%", ""), "+50%")

    def test_unparseable_base_falls_back_to_zero(self):
        # 'slow' isn't a percentage; treat as 0 and apply offset cleanly.
        self.assertEqual(tone.add_percent("slow", "+12%"), "+12%")

    def test_zero_result(self):
        # +5% and -5% cancel.
        self.assertEqual(tone.add_percent("+5%", "-5%"), "+0%")


if __name__ == "__main__":
    unittest.main()
