from __future__ import annotations

import re
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
TRAITS = XML / "Civilizations" / "CIV4TraitInfos.xml"
LEADERS = XML / "Civilizations" / "CIV4LeaderHeadInfos.xml"
TEXT = XML / "Text" / "ZZZ_CIV4GameText_BatchTraitsLeaders.xml"
LOCALES = {"English", "French", "German", "Italian", "Spanish"}
TOKEN_RE = re.compile(r"%%|%(?:\d+\$)?[A-Za-z](?:\d+(?:_[A-Za-z0-9]+)?)?")


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def child(node: ET.Element, name: str) -> ET.Element:
    return next(item for item in node if local_name(item.tag) == name)


def child_text(node: ET.Element, name: str) -> str:
    return (child(node, name).text or "").strip()


def info(path: Path, entry: str, type_name: str, id_tag: str = "Type") -> ET.Element:
    return next(
        node
        for node in ET.parse(path).getroot().iter()
        if local_name(node.tag) == entry
        and child_text(node, id_tag) == type_name
    )


def values(node: ET.Element, container: str, value_tag: str) -> list[int]:
    return [
        int((item.text or "0").strip())
        for item in child(node, container)
        if local_name(item.tag) == value_tag
    ]


def keyed_entries(node: ET.Element, container: str, key: str) -> dict[str, ET.Element]:
    return {
        child_text(item, key): item
        for item in child(node, container)
    }


def flavor_map(node: ET.Element) -> dict[str, int]:
    return {
        child_text(item, "FlavorType"): int(child_text(item, "iFlavor"))
        for item in child(node, "Flavors")
    }


class BatchTraitsLeadersTests(unittest.TestCase):
    def test_washington_removes_eight_channels_and_retains_command_and_road(self) -> None:
        trait = info(TRAITS, "TraitInfo", "TRAIT_GEORGE_WASHINGTON")
        self.assertEqual(child_text(trait, "iGreatGeneralRateModifier"), "50")
        self.assertEqual(child_text(trait, "iDomesticGreatGeneralRateModifier"), "50")
        for container in (
            "ImprovementYieldChanges",
            "BuildingYieldChanges",
            "BuildingCommerceChanges",
            "SpecialistCommerceChanges",
            "BonusYieldChanges",
        ):
            self.assertEqual(len(child(trait, container)), 0, container)
        roads = keyed_entries(trait, "RouteYieldChanges", "RouteType")
        self.assertEqual(set(roads), {"ROUTE_ROAD"})
        self.assertEqual(values(roads["ROUTE_ROAD"], "RouteYields", "iYield"), [0, 0, 1])

    def test_geronimo_uses_frozen_peace_and_limited_war_values(self) -> None:
        leader = info(LEADERS, "LeaderHeadInfo", "LEADER_GERONIMO_BTG")
        self.assertEqual(child_text(leader, "iBasePeaceWeight"), "4")
        self.assertNotEqual(child_text(leader, "iBasePeaceWeight"), "8")
        self.assertEqual(child_text(leader, "iLimitedWarRand"), "120")
        self.assertNotEqual(child_text(leader, "iLimitedWarRand"), "200")
        self.assertEqual(child_text(leader, "iMaxWarRand"), "200")
        self.assertEqual(child_text(leader, "iLimitedWarPowerRatio"), "100")

    def test_huayna_help_clarifies_retained_mechanics_without_format_tokens(self) -> None:
        trait = info(TRAITS, "TraitInfo", "TRAIT_HUAYNA_CAPAC")
        self.assertEqual(child_text(trait, "Help"), "TXT_KEY_TRAIT_HUAYNA_CAPAC_HELP")
        self.assertEqual(values(trait, "ExtraYieldThresholds", "iExtraYieldThreshold"), [0, 0, 5])
        self.assertEqual(values(trait, "TradeYieldModifiers", "iYield"), [0, 0, 25])
        recipients = set(keyed_entries(trait, "FreePromotionUnitCombats", "UnitCombatType"))
        self.assertEqual(
            recipients,
            {"UNITCOMBAT_RECON", "UNITCOMBAT_ARCHER", "UNITCOMBAT_MOUNTED", "UNITCOMBAT_MELEE"},
        )
        text = info(TEXT, "TEXT", "TXT_KEY_TRAIT_HUAYNA_CAPAC_HELP", "Tag")
        translations = {
            local_name(item.tag): (item.text or "").strip()
            for item in text
            if local_name(item.tag) != "Tag"
        }
        self.assertEqual(set(translations), LOCALES)
        for value in translations.values():
            self.assertIn("Huayna Workers and Settlers", value)
            self.assertIn("double movement on Hills", value)
            self.assertEqual(TOKEN_RE.findall(value), [])

    def test_genghis_removes_only_castle_town_worked_commerce_coupling(self) -> None:
        trait = info(TRAITS, "TraitInfo", "TRAIT_GENGHIS_KAHN")
        self.assertEqual(len(child(trait, "ImprovementCityCommerceChangesWorked")), 0)
        workshop = keyed_entries(trait, "ImprovementYieldChanges", "ImprovementType")
        self.assertEqual(values(workshop["IMPROVEMENT_WORKSHOP"], "ImprovementYields", "iYield"), [0, 1, 0])
        self.assertIn("IMPROVEMENT_FARM", keyed_entries(trait, "ImprovementTerrainYieldChanges", "ImprovementType"))

    def test_sitting_bull_zeros_trade_yields_and_retains_health(self) -> None:
        trait = info(TRAITS, "TraitInfo", "TRAIT_SITTING_BULL")
        self.assertEqual(values(trait, "TradeYieldModifiers", "iYield"), [0, 0, 0])
        self.assertNotEqual(values(trait, "TradeYieldModifiers", "iYield"), [150, -500, -500])
        self.assertEqual(child_text(trait, "iHealth"), "2")

    def test_mao_removes_farm_espionage_and_retains_workshop_and_spy(self) -> None:
        trait = info(TRAITS, "TraitInfo", "TRAIT_MAO_MASS_LINE")
        self.assertEqual(len(child(trait, "ImprovementCityCommerceChangesWorked")), 0)
        workshop = keyed_entries(trait, "ImprovementYieldChanges", "ImprovementType")
        self.assertEqual(values(workshop["IMPROVEMENT_WORKSHOP"], "ImprovementYields", "iYield"), [0, 1, 0])
        spy = keyed_entries(trait, "SpecialistCommerceChanges", "SpecialistType")
        self.assertEqual(values(spy["SPECIALIST_SPY"], "SpecialistCommerces", "iCommerce"), [0, 0, 0, 1])

    def test_casimir_rebalances_growth_and_culture_only(self) -> None:
        leader = info(LEADERS, "LeaderHeadInfo", "LEADER_CASIMIR")
        self.assertEqual(flavor_map(leader), {"FLAVOR_GROWTH": 5, "FLAVOR_CULTURE": 4, "FLAVOR_RELIGION": 2})
        self.assertEqual(child_text(leader, "iBasePeaceWeight"), "8")
        self.assertEqual(child_text(leader, "iLimitedWarRand"), "160")

    def test_salamasina_reduces_health_happiness_and_retains_navigation(self) -> None:
        trait = info(TRAITS, "TraitInfo", "TRAIT_SALAMASINA_BTG")
        self.assertEqual(child_text(trait, "iHealth"), "3")
        self.assertEqual(child_text(trait, "iHappiness"), "2")
        promotions = keyed_entries(trait, "FreePromotions", "PromotionType")
        self.assertEqual(set(promotions), {"PROMOTION_NAVIGATION1"})
        recipients = keyed_entries(trait, "FreePromotionUnitCombats", "UnitCombatType")
        self.assertEqual(set(recipients), {"UNITCOMBAT_NAVAL"})

    def test_stalin_rebudgets_espionage_into_factory_production(self) -> None:
        trait = info(TRAITS, "TraitInfo", "TRAIT_STALIN")
        self.assertEqual(child_text(trait, "iHappiness"), "-2")
        self.assertEqual(values(trait, "CommerceChanges", "iCommerce"), [0, 0, 0, 0])
        factories = keyed_entries(trait, "BuildingYieldChanges", "BuildingClassType")
        self.assertEqual(set(factories), {"BUILDINGCLASS_FACTORY"})
        self.assertEqual(values(factories["BUILDINGCLASS_FACTORY"], "BuildingYields", "iYield"), [0, 1, 0])

    def test_dandolo_trait_and_leader_use_frozen_rebudget(self) -> None:
        trait = info(TRAITS, "TraitInfo", "TRAIT_DANDOLO")
        self.assertEqual(child_text(trait, "iUpkeepModifier"), "0")
        self.assertNotEqual(child_text(trait, "iUpkeepModifier"), "100")
        self.assertEqual(values(trait, "TradeYieldModifiers", "iYield"), [0, 0, 25])
        leader = info(LEADERS, "LeaderHeadInfo", "LEADER_ENRICO_DANDOLO")
        self.assertEqual(child_text(leader, "iBasePeaceWeight"), "4")
        self.assertEqual(child_text(leader, "FavoriteCivic"), "CIVIC_CASTE_SYSTEM")
        self.assertEqual(
            flavor_map(leader),
            {
                "FLAVOR_GROWTH": 3,
                "FLAVOR_CULTURE": 3,
                "FLAVOR_RELIGION": 2,
                "FLAVOR_GOLD": 6,
                "FLAVOR_MILITARY": 3,
            },
        )

    def test_churchill_adds_espionage_and_retains_military_gold(self) -> None:
        leader = info(LEADERS, "LeaderHeadInfo", "LEADER_CHURCHILL")
        self.assertEqual(
            flavor_map(leader),
            {"FLAVOR_MILITARY": 5, "FLAVOR_GOLD": 2, "FLAVOR_ESPIONAGE": 3},
        )


if __name__ == "__main__":
    unittest.main()
