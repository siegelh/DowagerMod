from __future__ import annotations

import copy
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
BUILDINGS = XML / "Buildings" / "CIV4BuildingInfos.xml"
ART = XML / "Art" / "CIV4ArtDefines_Building.xml"
TEXT_DIR = XML / "Text"


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def child(node: ET.Element, name: str) -> ET.Element:
    return next(item for item in node if local_name(item.tag) == name)


def text(node: ET.Element, name: str) -> str:
    return (child(node, name).text or "").strip()


def values(node: ET.Element, name: str) -> list[int]:
    return [int((item.text or "0").strip()) for item in child(node, name)]


class BuildingBatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        root = ET.parse(BUILDINGS).getroot()
        cls.buildings = [
            node for node in root.iter() if local_name(node.tag) == "BuildingInfo"
        ]
        cls.by_type = {text(node, "Type"): node for node in cls.buildings}

    def test_hammurabi_royal_palace_budget_and_retained_fields(self) -> None:
        node = self.by_type["BUILDING_BABYLON_ROYAL_PALACE"]
        self.assertEqual(values(node, "YieldChanges"), [0, 0, 8])
        self.assertEqual(values(node, "CommerceChanges"), [0, 3, 2, 2])
        self.assertEqual(text(node, "iMaintenanceModifier"), "-10")
        self.assertEqual(text(node, "iHealth"), "2")
        self.assertEqual(text(node, "iHappiness"), "2")
        self.assertEqual(text(node, "iTradeRoutes"), "1")
        self.assertEqual(text(node, "GreatPeopleUnitClass"), "UNITCLASS_GREAT_SPY")

    def test_mauryan_obelisk_trait_links_and_war_weariness(self) -> None:
        node = self.by_type["BUILDING_MAURYAN_OBELISK"]
        production = child(node, "ProductionTraits")[0]
        happiness = child(node, "HappinessTraits")
        self.assertEqual(text(production, "ProductionTraitType"), "TRAIT_ASOKA")
        self.assertEqual(text(production, "iProductionTrait"), "50")
        self.assertEqual(
            [(text(item, "HappinessTraitType"), text(item, "iHappinessTrait"))
             for item in happiness],
            [("TRAIT_ASOKA", "1"), ("TRAIT_CHARISMATIC", "1")],
        )
        self.assertEqual(text(node, "iWarWearinessModifier"), "-25")
        self.assertEqual(text(node, "iCost"), "30")

    def test_stalin_building_budgets(self) -> None:
        institute = self.by_type["BUILDING_RUSSIAN_RESEARCH_INSTITUTE"]
        free_scientist = child(institute, "FreeSpecialistCounts")[0]
        self.assertEqual(text(free_scientist, "SpecialistType"), "SPECIALIST_SCIENTIST")
        self.assertEqual(text(free_scientist, "iFreeSpecialistCount"), "1")
        self.assertEqual(values(institute, "CommerceModifiers"), [0, 25])

        monument = self.by_type["BUILDING_USSR_MONUMENT"]
        self.assertEqual(text(monument, "iCost"), "30")
        self.assertEqual(values(monument, "ObsoleteSafeCommerceChanges"), [0, 0, 0, 1])
        spy_slot = child(monument, "SpecialistCounts")[0]
        self.assertEqual(text(spy_slot, "SpecialistType"), "SPECIALIST_SPY")
        self.assertEqual(text(spy_slot, "iSpecialistCount"), "1")

        lubyanka = self.by_type["BUILDING_LUBYANKA"]
        self.assertEqual(text(lubyanka, "iHappiness"), "-1")
        self.assertEqual(values(lubyanka, "CommerceChanges"), [0, 0, 0, 0])
        self.assertEqual(values(lubyanka, "CommerceModifiers"), [0, 0, 0, 100])

    def test_doge_palace_original_budget_is_preserved(self) -> None:
        node = self.by_type["BUILDING_VENETIAN_DOGE_PALACE"]
        actual = {
            name: text(node, name)
            for name in (
                "iGreatPeopleRateChange",
                "iHealth",
                "iHappiness",
                "iTradeRoutes",
                "iTradeRouteModifier",
                "iForeignTradeRouteModifier",
            )
        }
        self.assertEqual(actual, {
            "iGreatPeopleRateChange": "4",
            "iHealth": "30",
            "iHappiness": "15",
            "iTradeRoutes": "6",
            "iTradeRouteModifier": "50",
            "iForeignTradeRouteModifier": "50",
        })
        self.assertEqual(values(node, "YieldChanges"), [0, 0, 8])
        self.assertEqual(values(node, "CommerceChanges"), [0, 0, 0, 4])

    def test_mi6_budget_and_retained_spy_slot(self) -> None:
        node = self.by_type["BUILDING_BRITISH_MI6"]
        self.assertEqual(values(node, "CommerceModifiers"), [0, 0, 0, 100])
        self.assertEqual(text(child(node, "SpecialistCounts")[0], "iSpecialistCount"), "1")
        self.assertEqual(
            text(child(node, "FreeSpecialistCounts")[0], "iFreeSpecialistCount"), "0"
        )

    def test_yuan_secretariat_is_last_and_only_differs_as_frozen(self) -> None:
        self.assertEqual(
            [text(node, "Type") for node in self.buildings][-1],
            "BUILDING_YUAN_IMPERIAL_SECRETARIAT",
        )
        palace = copy.deepcopy(self.by_type["BUILDING_PALACE"])
        yuan = copy.deepcopy(self.by_type["BUILDING_YUAN_IMPERIAL_SECRETARIAT"])
        for node, building_type in (
            (palace, "BUILDING_YUAN_IMPERIAL_SECRETARIAT"),
            (yuan, "BUILDING_YUAN_IMPERIAL_SECRETARIAT"),
        ):
            node.tail = None
            child(node, "Type").text = building_type
            child(node, "Description").text = "DESCRIPTION"
            child(node, "Civilopedia").text = "PEDIA"
            child(node, "Strategy").text = "STRATEGY"
            child(node, "iTradeRoutes").text = "1"
            culture = child(node, "CommerceChanges")[2]
            culture.text = "2"
        self.assertEqual(ET.tostring(yuan), ET.tostring(palace))
        self.assertEqual(text(yuan, "BuildingClass"), "BUILDINGCLASS_PALACE")
        self.assertEqual(text(yuan, "FreeBonus"), "NONE")
        self.assertEqual(text(yuan, "iNumFreeBonuses"), "0")
        self.assertEqual(text(yuan, "bGoldenAge"), "0")
        self.assertEqual(len(child(yuan, "PrereqBuildingClasses")), 0)
        self.assertEqual(text(yuan, "ArtDefineTag"), "ART_DEF_BUILDING_PALACE")

    def test_yuan_text_and_reused_art_resolve(self) -> None:
        tags: set[str] = set()
        for path in TEXT_DIR.glob("*.xml"):
            for node in ET.parse(path).getroot().iter():
                if local_name(node.tag) == "Tag" and node.text:
                    tags.add(node.text.strip())
        yuan = self.by_type["BUILDING_YUAN_IMPERIAL_SECRETARIAT"]
        self.assertTrue({text(yuan, name) for name in ("Description", "Civilopedia", "Strategy")} <= tags)
        art_types = {
            text(node, "Type")
            for node in ET.parse(ART).getroot().iter()
            if local_name(node.tag) == "BuildingArtInfo"
        }
        self.assertIn(text(yuan, "ArtDefineTag"), art_types)


if __name__ == "__main__":
    unittest.main()
