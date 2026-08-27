from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RANDOM_EVENTS = (
    ROOT
    / "CoreFiles"
    / "Sid Meier's Civilization IV Beyond the Sword"
    / "Beyond the Sword"
    / "Assets"
    / "Python"
    / "EntryPoints"
    / "CvRandomEventInterface.py"
)
UPRISING_TRIGGERS = (
    "TheHuns",
    "TheVandals",
    "TheGoths",
    "ThePhilistines",
    "TheVedicAryans",
)


class BarbarianUprisingEventTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = RANDOM_EVENTS.read_text(encoding="utf-8")

    def test_shared_uprising_gate_requires_fifty_elapsed_turns(self) -> None:
        self.assertRegex(
            self.source,
            r"BARBARIAN_UPRISING_MIN_ELAPSED_TURNS\s*=\s*50",
        )
        helper = self._function_source("canTriggerBarbarianUprising")
        self.assertIn("getElapsedGameTurns()", helper)
        self.assertIn("BARBARIAN_UPRISING_MIN_ELAPSED_TURNS", helper)

    def test_every_uprising_uses_the_shared_turn_gate(self) -> None:
        for trigger in UPRISING_TRIGGERS:
            with self.subTest(trigger=trigger):
                callback = self._function_source("canTrigger" + trigger)
                self.assertEqual(
                    callback.count("if not canTriggerBarbarianUprising():"),
                    1,
                )
                self.assertRegex(
                    callback,
                    r"if not canTriggerBarbarianUprising\(\):\s+return false",
                )

    def _function_source(self, function_name: str) -> str:
        match = re.search(
            r"^def " + re.escape(function_name) + r"\([^)]*\):.*?(?=^def |\Z)",
            self.source,
            re.MULTILINE | re.DOTALL,
        )
        self.assertIsNotNone(match, "Missing function " + function_name)
        return match.group(0)


if __name__ == "__main__":
    unittest.main()
