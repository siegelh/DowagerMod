from __future__ import annotations

import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ASSETS = (
    ROOT
    / "CoreFiles"
    / "Sid Meier's Civilization IV Beyond the Sword"
    / "Beyond the Sword"
    / "Assets"
)
BONUSES = ASSETS / "XML/Terrain/CIV4BonusInfos.xml"
BUILDINGS = ASSETS / "XML/Buildings/CIV4BuildingInfos.xml"
UNITS = ASSETS / "XML/Units/CIV4UnitInfos.xml"
FLOW_DATA = ASSETS / "Python/Screens/CvIndustryFlowData.py"
CITY_SOURCE = ROOT / "third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvCity.cpp"


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def child(node: ET.Element, name: str) -> ET.Element:
    return next(item for item in node if local_name(item.tag) == name)


def text(node: ET.Element, name: str) -> str:
    return (child(node, name).text or "").strip()


def entries(path: Path, tag: str) -> dict[str, ET.Element]:
    nodes = [node for node in ET.parse(path).getroot().iter() if local_name(node.tag) == tag]
    return {text(node, "Type"): node for node in nodes}


class GuildArmamentsContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bonuses = entries(BONUSES, "BonusInfo")
        cls.buildings = entries(BUILDINGS, "BuildingInfo")
        cls.units = entries(UNITS, "UnitInfo")

    def test_three_armaments_goods_are_neutral_synthetic_resources(self) -> None:
        for bonus in ("BONUS_FORGED_IRON", "BONUS_COPPERWARE", "BONUS_TRAINED_MOUNTS"):
            with self.subTest(bonus=bonus):
                node = self.bonuses[bonus]
                self.assertEqual(text(node, "BonusClassType"), "BONUSCLASS_GENERAL")
                self.assertEqual(text(node, "TechReveal"), "NONE")
                self.assertEqual(text(node, "iHealth"), "0")
                self.assertEqual(text(node, "iHappiness"), "0")

    def test_processors_require_their_local_resource_and_produce_their_good(self) -> None:
        expected = {
            "BUILDING_INDUSTRY_IRON_FOUNDRY": ("BUILDINGCLASS_FORGE", "BONUS_IRON", "BONUS_FORGED_IRON"),
            "BUILDING_INDUSTRY_COPPERSMITHS_HALL": ("BUILDINGCLASS_FORGE", "BONUS_COPPER", "BONUS_COPPERWARE"),
            "BUILDING_INDUSTRY_STUD_FARM": ("BUILDINGCLASS_STABLE", "BONUS_HORSE", "BONUS_TRAINED_MOUNTS"),
        }
        for building, (needed, raw, produced) in expected.items():
            with self.subTest(building=building):
                node = self.buildings[building]
                self.assertEqual(text(node, "IndustryCategory"), "LUXURY")
                self.assertEqual(text(node, "bRequiresActiveLocalPrereqs"), "1")
                self.assertEqual(text(node, "FreeBonus"), produced)
                self.assertEqual(text(child(node, "BuildingClassNeededs")[0], "BuildingClassType"), needed)
                self.assertEqual(
                    text(child(child(node, "LocalBonusPrereqs")[0], "BonusTypes"), "BonusType"),
                    raw,
                )

    def test_composites_require_the_approved_good_pairs(self) -> None:
        expected = {
            "BUILDING_INDUSTRY_ARSENAL": ("BONUS_FORGED_IRON", "BONUS_COPPERWARE"),
            "BUILDING_INDUSTRY_REMOUNT_DEPOT": ("BONUS_FORGED_IRON", "BONUS_TRAINED_MOUNTS"),
            "BUILDING_INDUSTRY_MILITARY_OUTFITTERS": ("BONUS_COPPERWARE", "BONUS_TRAINED_MOUNTS"),
        }
        for building, goods in expected.items():
            with self.subTest(building=building):
                node = self.buildings[building]
                self.assertEqual(text(node, "IndustryCategory"), "COMPOSITE")
                actual = []
                for group in child(node, "ConnectedBonusPrereqs"):
                    actual.append(text(child(group, "BonusTypes"), "BonusType"))
                self.assertEqual(tuple(actual), goods)
                self.assertEqual(text(node, "iMilitaryProductionModifier"), "10")

    def test_armaments_executive_is_active_at_rifling(self) -> None:
        node = self.units["UNIT_EXECUTIVE_7"]
        self.assertEqual(text(node, "PrereqCorporation"), "CORPORATION_7")
        self.assertEqual(text(node, "PrereqTech"), "TECH_RIFLING")
        self.assertEqual(text(node, "iCost"), "100")

    def test_armaments_is_wired_into_advisor_and_native_experience(self) -> None:
        flow = FLOW_DATA.read_text(encoding="utf-8")
        city = CITY_SOURCE.read_text(encoding="utf-8")
        self.assertIn("'id': 'corp7'", flow)
        self.assertIn("'short_label': 'Armaments'", flow)
        self.assertIn("getMilitaryExperience()", city)
        self.assertIn("isActiveCorporation(eCorporation)", city)


if __name__ == "__main__":
    unittest.main()
