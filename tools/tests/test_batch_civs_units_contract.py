from __future__ import annotations

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
CIVILIZATIONS = XML / "Civilizations" / "CIV4CivilizationInfos.xml"
UNITS = XML / "Units" / "CIV4UnitInfos.xml"
def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def child(node: ET.Element, name: str) -> ET.Element:
    return next(item for item in node if local_name(item.tag) == name)


def child_text(node: ET.Element, name: str) -> str:
    return (child(node, name).text or "").strip()


def info(path: Path, entry_name: str, type_name: str) -> ET.Element:
    return next(
        node
        for node in ET.parse(path).getroot().iter()
        if local_name(node.tag) == entry_name
        and child_text(node, "Type") == type_name
    )


def mappings(civilization: str, container: str, key: str, value: str) -> dict[str, str]:
    civ = info(CIVILIZATIONS, "CivilizationInfo", civilization)
    entries = child(civ, container)
    return {child_text(node, key): child_text(node, value) for node in entries}


class BatchCivilizationsUnitsContractTests(unittest.TestCase):
    def test_frozen_civilization_mappings(self) -> None:
        england = mappings(
            "CIVILIZATION_ELIZABETHAN_ENGLAND",
            "Units",
            "UnitClassType",
            "UnitType",
        )
        self.assertEqual(england["UNITCLASS_GALLEY"], "UNIT_GALLEY")
        self.assertEqual(england["UNITCLASS_TRIREME"], "UNIT_TRIREME")
        self.assertEqual(
            england["UNITCLASS_PRIVATEER"], "UNIT_ENGLISH_SEA_DOG"
        )

        korea = mappings(
            "CIVILIZATION_KOREA",
            "Buildings",
            "BuildingClassType",
            "BuildingType",
        )
        self.assertEqual(korea["BUILDINGCLASS_LIBRARY"], "BUILDING_LIBRARY")
        self.assertEqual(korea["BUILDINGCLASS_ACADEMY"], "BUILDING_ACADEMY")
        self.assertEqual(
            korea["BUILDINGCLASS_UNIVERSITY"], "BUILDING_KOREAN_SEOWON"
        )

        ussr = mappings(
            "CIVILIZATION_USSR", "Units", "UnitClassType", "UnitType"
        )
        self.assertEqual(ussr["UNITCLASS_SPY"], "UNIT_SPY")

        venice = mappings(
            "CIVILIZATION_VENICE", "Units", "UnitClassType", "UnitType"
        )
        self.assertEqual(venice["UNITCLASS_SETTLER"], "UNIT_VENICE_FOUNDER")
        self.assertEqual(
            venice["UNITCLASS_MERCHANT"], "UNIT_VENETIAN_MERCHANT"
        )

        yuan = mappings(
            "CIVILIZATION_YUAN_DYNASTY",
            "Buildings",
            "BuildingClassType",
            "BuildingType",
        )
        self.assertEqual(
            yuan["BUILDINGCLASS_PALACE"],
            "BUILDING_YUAN_IMPERIAL_SECRETARIAT",
        )
        self.assertEqual(
            yuan["BUILDINGCLASS_GREAT_PALACE"], "BUILDING_MONGOLIAN_PALACE"
        )

    def test_replaced_types_remain_defined(self) -> None:
        unit_types = {
            child_text(node, "Type")
            for node in ET.parse(UNITS).getroot().iter()
            if local_name(node.tag) == "UnitInfo"
        }
        self.assertIn("UNIT_RUSSIA_SPY", unit_types)
        self.assertIn("UNIT_VENICE_FOUNDER", unit_types)

        building_files = list((XML / "Buildings").glob("*.xml"))
        building_types = {
            child_text(node, "Type")
            for path in building_files
            for node in ET.parse(path).getroot().iter()
            if local_name(node.tag) == "BuildingInfo"
        }
        self.assertIn("BUILDING_KOREAN_LIBRARY", building_types)
        self.assertIn("BUILDING_KOREAN_ACADEMY", building_types)

    def test_venetian_merchant_original_actions_are_preserved(self) -> None:
        merchant = info(UNITS, "UnitInfo", "UNIT_VENETIAN_MERCHANT")
        self.assertEqual(child_text(merchant, "bFound"), "1")
        builds = {
            child_text(node, "BuildType")
            for node in child(merchant, "Builds")
        }
        self.assertEqual(builds, {"BUILD_ROAD", "BUILD_GRAND_COLOSSEUM_BTG"})
        self.assertEqual(child_text(merchant, "iWorkRate"), "1000")
        self.assertEqual(child_text(merchant, "iGreatWorkCulture"), "4000")

        self.assertEqual(child_text(merchant, "bGoldenAge"), "1")
        self.assertEqual(child_text(merchant, "iCost"), "-1")
        self.assertEqual(child_text(merchant, "iMoves"), "3")
        self.assertEqual(child_text(merchant, "iBaseTrade"), "1000")
        self.assertEqual(child_text(merchant, "iTradeMultiplier"), "400")
        self.assertEqual(child_text(merchant, "iBaseDiscover"), "1000")
        self.assertEqual(child_text(merchant, "iDiscoverMultiplier"), "2")
        great_people = child(merchant, "GreatPeoples")
        self.assertEqual(
            child_text(great_people[0], "GreatPeopleType"),
            "SPECIALIST_VENETIAN_MERCHANT_PRINCE",
        )
        corporations = {
            child_text(node, "BuildingType")
            for node in child(merchant, "Buildings")
        }
        self.assertEqual(
            corporations,
            {f"BUILDING_CORPORATION_{index}" for index in range(1, 7)},
        )
        art_tags = {
            child_text(node, name)
            for node in child(merchant, "UnitMeshGroups").iter()
            if local_name(node.tag) == "UnitMeshGroup"
            for name in ("EarlyArtDefineTag", "LateArtDefineTag")
        }
        self.assertEqual(
            art_tags,
            {"ART_DEF_UNIT_MERCHANT", "ART_DEF_UNIT_MERCHANT_MODERN"},
        )

    def test_venetian_merchant_original_inline_help_is_preserved(self) -> None:
        merchant = info(UNITS, "UnitInfo", "UNIT_VENETIAN_MERCHANT")
        self.assertEqual(
            child_text(merchant, "Civilopedia"),
            "A patrician merchant-banker of Venice, able to move quickly "
            "between ports and turn diplomacy, credit, and convoy access "
            "into extraordinary trade mission profits.",
        )
        self.assertEqual(
            child_text(merchant, "Strategy"),
            "Venice's unique Great Merchant. Faster movement and stronger "
            "trade missions make it ideal for long-distance gold spikes and "
            "flexible economic play.",
        )


if __name__ == "__main__":
    unittest.main()
