import math
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
XML = (
    ROOT
    / "CoreFiles"
    / "Sid Meier's Civilization IV Beyond the Sword"
    / "Beyond the Sword"
    / "Assets"
    / "XML"
)
CIVS = XML / "Civilizations" / "CIV4CivilizationInfos.xml"
PLAYER_COLORS = XML / "Interface" / "CIV4PlayerColorInfos.xml"
COLOR_VALS = XML / "Interface" / "CIV4ColorVals.xml"

APPENDED = [
    "AMERICA_FOUNDING",
    "AMERICA_NEW_DEAL",
    "AMERICA_FEDERAL",
    "FRANCE_BOURBON",
    "FRANCE_FIRST_EMPIRE",
    "MAURYA",
    "POLAND",
    "POLYNESIA",
    "APACHE",
    "PETRINE_RUSSIA",
    "IMPERIAL_RUSSIA",
    "MACEDON",
    "ATHENS",
    "ELIZABETHAN_ENGLAND",
    "VICTORIAN_BRITAIN",
    "WARTIME_BRITAIN",
    "PERSIA_IMPERIAL",
    "EGYPT_NEW_KINGDOM",
    "OTTOMAN_CLASSICAL",
    "ETHIOPIA_IMPERIAL",
    "ICENI",
    "YUAN",
    "ROMAN_PRINCIPATE",
    "GERMAN_EMPIRE",
]


def entries(path, tag):
    return ET.parse(path).getroot().findall(".//{*}" + tag)


def text(node, tag):
    child = node.find("{*}" + tag)
    return child.text.strip() if child is not None and child.text else ""


def rgb_to_lab(rgb):
    def linear(value):
        if value <= 0.04045:
            return value / 12.92
        return ((value + 0.055) / 1.055) ** 2.4

    red, green, blue = [linear(value) for value in rgb]
    x = (0.4124 * red + 0.3576 * green + 0.1805 * blue) / 0.95047
    y = 0.2126 * red + 0.7152 * green + 0.0722 * blue
    z = (0.0193 * red + 0.1192 * green + 0.9505 * blue) / 1.08883

    def pivot(value):
        if value > 0.008856:
            return value ** (1.0 / 3.0)
        return 7.787 * value + 16.0 / 116.0

    fx, fy, fz = pivot(x), pivot(y), pivot(z)
    return 116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)


def distance(left, right):
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(left, right)))


class CivilizationColorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.civs = entries(CIVS, "CivilizationInfo")
        cls.player_entries = entries(PLAYER_COLORS, "PlayerColorInfo")
        cls.color_entries = entries(COLOR_VALS, "ColorVal")
        cls.player_colors = {
            text(node, "Type"): node for node in cls.player_entries
        }
        cls.color_values = {
            text(node, "Type"): (
                float(text(node, "fRed")),
                float(text(node, "fGreen")),
                float(text(node, "fBlue")),
            )
            for node in cls.color_entries
        }

    def test_all_playable_civilizations_have_unique_defaults(self):
        playable = [
            node for node in self.civs if text(node, "bPlayable") == "1"
        ]
        defaults = [text(node, "DefaultPlayerColor") for node in playable]
        self.assertEqual(len(playable), 59)
        self.assertEqual(len(defaults), len(set(defaults)))

    def test_all_playable_color_references_resolve(self):
        for civ in self.civs:
            if text(civ, "bPlayable") != "1":
                continue
            player_color = text(civ, "DefaultPlayerColor")
            self.assertIn(player_color, self.player_colors)
            info = self.player_colors[player_color]
            for field in (
                "ColorTypePrimary",
                "ColorTypeSecondary",
                "TextColorType",
            ):
                self.assertIn(text(info, field), self.color_values)

    def test_new_definitions_are_append_only_in_locked_order(self):
        expected_players = ["PLAYERCOLOR_" + name for name in APPENDED]
        expected_values = ["COLOR_PLAYER_" + name for name in APPENDED]
        player_order = [text(node, "Type") for node in self.player_entries]
        value_order = [text(node, "Type") for node in self.color_entries]
        self.assertEqual(player_order[-24:], expected_players)
        self.assertEqual(value_order[-24:], expected_values)
        self.assertEqual(len(player_order), 69)

    def test_playable_primary_rgb_values_are_exactly_unique(self):
        primary_values = []
        for civ in self.civs:
            if text(civ, "bPlayable") != "1":
                continue
            info = self.player_colors[text(civ, "DefaultPlayerColor")]
            primary_values.append(
                self.color_values[text(info, "ColorTypePrimary")]
            )
        self.assertEqual(len(primary_values), len(set(primary_values)))

    def test_appended_palette_has_strong_distance_from_prior_colors(self):
        prior = []
        for info in self.player_entries[:-24]:
            primary = text(info, "ColorTypePrimary")
            color = rgb_to_lab(self.color_values[primary])
            if color not in prior:
                prior.append(color)
        added = [
            rgb_to_lab(self.color_values["COLOR_PLAYER_" + name])
            for name in APPENDED
        ]
        for index, color in enumerate(added):
            comparison = prior + added[:index]
            self.assertGreaterEqual(
                min(distance(color, other) for other in comparison),
                20.0,
                APPENDED[index],
            )


if __name__ == "__main__":
    unittest.main()
