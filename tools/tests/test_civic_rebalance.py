from __future__ import annotations

import re
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BTS_XML = (
    ROOT
    / "CoreFiles"
    / "Sid Meier's Civilization IV Beyond the Sword"
    / "Beyond the Sword"
    / "Assets"
    / "XML"
)
CIVICS = BTS_XML / "GameInfo" / "CIV4CivicInfos.xml"
COMMERCE = BTS_XML / "GameInfo" / "CIV4CommerceInfo.xml"
HELP_TEXT = BTS_XML / "Text" / "CIV4GameText_ImprovementCityCommerceModes.xml"
DLL = ROOT / "third_party" / "beyond-the-sword-sdk" / "CvGameCoreDLL"
TOKEN_RE = re.compile(r"%(?:\+)?[A-Za-z]")
REQUIRED_LOCALES = {"English", "French", "German", "Italian", "Spanish"}


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def child_text(node: ET.Element, name: str) -> str:
    child = next(item for item in node if local_name(item.tag) == name)
    return (child.text or "").strip()


def civic(civic_type: str) -> ET.Element:
    root = ET.parse(CIVICS).getroot()
    return next(
        node
        for node in root.iter()
        if local_name(node.tag) == "CivicInfo"
        and child_text(node, "Type") == civic_type
    )


class CivicRebalanceTests(unittest.TestCase):
    def test_free_market_has_no_town_food_bonus(self) -> None:
        free_market = civic("CIVIC_FREE_MARKET")
        changes = next(
            node
            for node in free_market
            if local_name(node.tag) == "ImprovementYieldChanges"
        )
        towns = [
            node
            for node in changes
            if child_text(node, "ImprovementType") == "IMPROVEMENT_TOWN"
        ]
        self.assertEqual(towns, [])

    def test_pacifism_has_no_town_food_bonus(self) -> None:
        pacifism = civic("CIVIC_PACIFISM")
        changes = next(
            node for node in pacifism if local_name(node.tag) == "ImprovementYieldChanges"
        )
        towns = [
            node
            for node in changes
            if child_text(node, "ImprovementType") == "IMPROVEMENT_TOWN"
        ]
        self.assertEqual(towns, [])

    def test_emancipation_has_exactly_town_plus_two_gold(self) -> None:
        emancipation = civic("CIVIC_EMANCIPATION")
        worked = next(
            node
            for node in emancipation
            if local_name(node.tag) == "ImprovementCityCommerceChangesWorked"
        )
        self.assertEqual(len(worked), 1)
        entry = worked[0]
        self.assertEqual(child_text(entry, "ImprovementType"), "IMPROVEMENT_TOWN")
        commerces = next(
            node for node in entry if local_name(node.tag) == "ImprovementCommerces"
        )
        self.assertEqual(
            [int((node.text or "0").strip()) for node in commerces],
            [2, 0, 0, 0],
        )

    def test_gold_is_first_commerce_in_live_xml_and_dll(self) -> None:
        xml_types = [
            child_text(node, "Type")
            for node in ET.parse(COMMERCE).getroot().iter()
            if local_name(node.tag) == "CommerceInfo"
        ]
        self.assertEqual(
            xml_types,
            [
                "COMMERCE_GOLD",
                "COMMERCE_RESEARCH",
                "COMMERCE_CULTURE",
                "COMMERCE_ESPIONAGE",
            ],
        )
        enums = (DLL / "CvEnums.h").read_text(encoding="latin-1")
        block = re.search(r"enum CommerceTypes.*?\{(.*?)\};", enums, re.DOTALL)
        self.assertIsNotNone(block)
        dll_types = re.findall(r"\bCOMMERCE_[A-Z_]+\b", block.group(1))
        self.assertEqual(dll_types[:4], xml_types)

    def test_ai_civic_value_prices_worked_improvement_commerce(self) -> None:
        source = (DLL / "CvPlayerAI.cpp").read_text(encoding="latin-1")
        function = source[source.index("int CvPlayerAI::AI_civicValue") :]
        function = function[: function.index("\n}") + 2]
        self.assertIn(
            "kCivic.getImprovementCityCommerceChangesWorked(iJ, iI)",
            function,
        )
        self.assertRegex(
            function,
            r"iWorkedChange\s*\*\s*iImprovementCount\s*\*\s*2",
        )

    def test_civic_help_has_safe_tokens_in_all_required_locales(self) -> None:
        root = ET.parse(HELP_TEXT).getroot()
        text = next(
            node
            for node in root
            if child_text(node, "Tag")
            == "TXT_KEY_CIVIC_IMPROVEMENT_CITY_COMMERCE_WORKED"
        )
        translations = {
            local_name(node.tag): (node.text or "").strip()
            for node in text
            if local_name(node.tag) != "Tag"
        }
        self.assertEqual(set(translations), REQUIRED_LOCALES)
        for locale, value in translations.items():
            self.assertEqual(
                TOKEN_RE.findall(value),
                ["%d", "%c"],
                msg=f"{locale} has malformed or reordered format tokens",
            )
            self.assertEqual(
                value.count("%"),
                2,
                msg=f"{locale} has an unrecognized percent token",
            )


if __name__ == "__main__":
    unittest.main()
