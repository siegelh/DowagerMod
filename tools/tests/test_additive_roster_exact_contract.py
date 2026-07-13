from __future__ import annotations

import copy
import subprocess
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASELINE = "12e22297f"
XML_ROOT = (
    "CoreFiles/Sid Meier's Civilization IV Beyond the Sword/"
    "Beyond the Sword/Assets/XML"
)
BUILDINGS = f"{XML_ROOT}/Buildings/CIV4BuildingInfos.xml"
CIVILIZATIONS = f"{XML_ROOT}/Civilizations/CIV4CivilizationInfos.xml"
LEADERS = f"{XML_ROOT}/Civilizations/CIV4LeaderHeadInfos.xml"
TRAITS = f"{XML_ROOT}/Civilizations/CIV4TraitInfos.xml"
CIVICS = f"{XML_ROOT}/GameInfo/CIV4CivicInfos.xml"
CORPORATIONS = f"{XML_ROOT}/GameInfo/CIV4CorporationInfo.xml"
BUILDS = f"{XML_ROOT}/Units/CIV4BuildInfos.xml"
UNITS = f"{XML_ROOT}/Units/CIV4UnitInfos.xml"
IMPROVEMENTS = f"{XML_ROOT}/Terrain/CIV4ImprovementInfos.xml"


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def direct_children(node: ET.Element, name: str) -> list[ET.Element]:
    return [item for item in node if local_name(item.tag) == name]


def child(node: ET.Element, name: str) -> ET.Element:
    matches = direct_children(node, name)
    if len(matches) != 1:
        raise AssertionError(
            f"expected one {name} child, found {len(matches)}"
        )
    return matches[0]


def text(node: ET.Element, name: str) -> str:
    return (child(node, name).text or "").strip()


def keyed_entry(
    node: ET.Element, container: str, key: str, value: str
) -> ET.Element:
    matches = [
        item
        for item in child(node, container)
        if text(item, key) == value
    ]
    if len(matches) != 1:
        raise AssertionError(
            f"expected one {container} entry keyed by {key}={value}, "
            f"found {len(matches)}"
        )
    return matches[0]


def canonicalize(node: ET.Element) -> ET.Element:
    result = copy.deepcopy(node)
    for item in result.iter():
        item.tail = None
        if item.text is not None:
            item.text = item.text.strip() or None
    return result


def canonical_value(node: ET.Element) -> tuple:
    return (
        node.tag,
        tuple(sorted(node.attrib.items())),
        node.text,
        tuple(canonical_value(item) for item in node),
    )


class AdditiveRosterExactContractTests(unittest.TestCase):
    _roots: dict[tuple[str, str], ET.Element] = {}

    @classmethod
    def root(cls, source: str, repo_path: str) -> ET.Element:
        key = (source, repo_path)
        if key not in cls._roots:
            if source == "current":
                cls._roots[key] = ET.parse(ROOT / Path(repo_path)).getroot()
            else:
                result = subprocess.run(
                    ["git", "show", f"{BASELINE}:{repo_path}"],
                    cwd=ROOT,
                    check=True,
                    capture_output=True,
                )
                cls._roots[key] = ET.fromstring(result.stdout)
        return cls._roots[key]

    def node(
        self,
        source: str,
        repo_path: str,
        entry_name: str,
        type_name: str,
    ) -> ET.Element:
        matches = []
        for node in self.root(source, repo_path).iter():
            if local_name(node.tag) != entry_name:
                continue
            type_nodes = direct_children(node, "Type")
            if len(type_nodes) == 1 and (type_nodes[0].text or "").strip() == type_name:
                matches.append(node)
        self.assertEqual(
            len(matches),
            1,
            msg=(
                f"{type_name} must occur exactly once as {entry_name} "
                f"in {source} {repo_path}"
            ),
        )
        return canonicalize(matches[0])

    def pair(
        self, repo_path: str, entry_name: str, type_name: str
    ) -> tuple[ET.Element, ET.Element]:
        return (
            self.node("current", repo_path, entry_name, type_name),
            self.node("baseline", repo_path, entry_name, type_name),
        )

    def assert_node_equal(
        self,
        current: ET.Element,
        baseline: ET.Element,
        repo_path: str,
        type_name: str,
    ) -> None:
        if canonical_value(current) != canonical_value(baseline):
            self.fail(
                f"{type_name} has an unauthorized XML-node delta in "
                f"{repo_path} versus git {BASELINE}"
            )

    def assert_exact(
        self, repo_path: str, entry_name: str, *type_names: str
    ) -> None:
        for type_name in type_names:
            with self.subTest(type=type_name, path=repo_path):
                current, baseline = self.pair(
                    repo_path, entry_name, type_name
                )
                self.assert_node_equal(
                    current, baseline, repo_path, type_name
                )

    def normalize_direct_field(
        self,
        current: ET.Element,
        baseline: ET.Element,
        field: str,
        approved_value: str,
    ) -> None:
        current_field = child(current, field)
        baseline_field = child(baseline, field)
        self.assertEqual(
            (current_field.text or "").strip(),
            approved_value,
            msg=f"{field} does not have its approved current value",
        )
        current_field.text = baseline_field.text

    def test_exact_restored_package_nodes(self) -> None:
        self.assert_exact(
            TRAITS,
            "TraitInfo",
            "TRAIT_GEORGE_WASHINGTON",
            "TRAIT_HAMMURABI",
            "TRAIT_GENGHIS_KAHN",
            "TRAIT_SITTING_BULL",
            "TRAIT_MAO_MASS_LINE",
            "TRAIT_SALAMASINA_BTG",
            "TRAIT_DANDOLO",
        )
        self.assert_exact(
            LEADERS,
            "LeaderHeadInfo",
            "LEADER_WASHINGTON",
            "LEADER_HAMMURABI",
            "LEADER_SALAMASINA_BTG",
            "LEADER_ENRICO_DANDOLO",
        )
        self.assert_exact(
            CIVILIZATIONS,
            "CivilizationInfo",
            "CIVILIZATION_AMERICA_FOUNDING_REPUBLIC",
            "CIVILIZATION_BABYLON",
            "CIVILIZATION_ELIZABETHAN_ENGLAND",
            "CIVILIZATION_KOREA",
            "CIVILIZATION_POLYNESIA_BTG",
            "CIVILIZATION_VENICE",
        )
        self.assert_exact(
            BUILDINGS,
            "BuildingInfo",
            "BUILDING_BABYLON_ROYAL_PALACE",
            "BUILDING_BABYLON_GARDEN",
            "BUILDING_BABYLON_COURTHOUSE",
            "BUILDING_KOREAN_LIBRARY",
            "BUILDING_KOREAN_SEOWON",
            "BUILDING_KOREAN_ACADEMY",
            "BUILDING_POLYNESIA_MARAE_BTG",
            "BUILDING_VENETIAN_DOGE_PALACE",
            "BUILDING_BRITISH_MI6",
            "BUILDING_RUSSIAN_RESEARCH_INSTITUTE",
            "BUILDING_USSR_MONUMENT",
            "BUILDING_LUBYANKA",
            "BUILDING_MONGOLIAN_PALACE",
        )
        self.assert_exact(
            UNITS,
            "UnitInfo",
            "UNIT_POLYNESIA_OCEAN_CANOE_BTG",
            "UNIT_POLYNESIA_WAYFINDER_WORKBOAT_BTG",
            "UNIT_VENETIAN_MERCHANT",
            "UNIT_RUSSIA_SPY",
        )
        self.assert_exact(
            BUILDS,
            "BuildInfo",
            "BUILD_POLYNESIA_REEF_WORKS_BTG",
        )
        self.assert_exact(
            IMPROVEMENTS,
            "ImprovementInfo",
            "IMPROVEMENT_POLYNESIA_REEF_WORKS_BTG",
        )

    def test_geronimo_has_only_approved_personality_deltas(self) -> None:
        type_name = "LEADER_GERONIMO_BTG"
        current, baseline = self.pair(LEADERS, "LeaderHeadInfo", type_name)
        self.normalize_direct_field(
            current, baseline, "iBasePeaceWeight", "4"
        )
        self.normalize_direct_field(
            current, baseline, "iLimitedWarRand", "120"
        )
        self.assert_node_equal(current, baseline, LEADERS, type_name)

    def test_huayna_has_only_approved_help_delta(self) -> None:
        type_name = "TRAIT_HUAYNA_CAPAC"
        current, baseline = self.pair(TRAITS, "TraitInfo", type_name)
        self.assertEqual(direct_children(baseline, "Help"), [])
        help_nodes = direct_children(current, "Help")
        self.assertEqual(len(help_nodes), 1)
        self.assertEqual(
            (help_nodes[0].text or "").strip(),
            "TXT_KEY_TRAIT_HUAYNA_CAPAC_HELP",
        )
        current.remove(help_nodes[0])
        self.assert_node_equal(current, baseline, TRAITS, type_name)

    def test_asoka_obelisk_has_only_approved_corrections(self) -> None:
        type_name = "BUILDING_MAURYAN_OBELISK"
        current, baseline = self.pair(BUILDINGS, "BuildingInfo", type_name)

        current_production = child(current, "ProductionTraits")
        baseline_production = child(baseline, "ProductionTraits")
        self.assertEqual(len(current_production), 1)
        self.assertEqual(len(baseline_production), 1)
        self.assertEqual(
            text(current_production[0], "ProductionTraitType"),
            "TRAIT_ASOKA",
        )
        child(
            current_production[0], "ProductionTraitType"
        ).text = child(
            baseline_production[0], "ProductionTraitType"
        ).text

        current_happiness = child(current, "HappinessTraits")
        baseline_happiness = child(baseline, "HappinessTraits")
        self.assertEqual(len(current_happiness), len(baseline_happiness))
        self.assertEqual(
            text(current_happiness[0], "HappinessTraitType"),
            "TRAIT_ASOKA",
        )
        child(
            current_happiness[0], "HappinessTraitType"
        ).text = child(
            baseline_happiness[0], "HappinessTraitType"
        ).text

        self.normalize_direct_field(
            current, baseline, "iWarWearinessModifier", "-25"
        )
        self.assert_node_equal(current, baseline, BUILDINGS, type_name)

    def test_casimir_has_only_two_approved_flavor_deltas(self) -> None:
        type_name = "LEADER_CASIMIR"
        current, baseline = self.pair(LEADERS, "LeaderHeadInfo", type_name)
        for flavor, approved_value in (
            ("FLAVOR_GROWTH", "5"),
            ("FLAVOR_CULTURE", "4"),
        ):
            current_flavor = keyed_entry(
                current, "Flavors", "FlavorType", flavor
            )
            baseline_flavor = keyed_entry(
                baseline, "Flavors", "FlavorType", flavor
            )
            self.assertEqual(text(current_flavor, "iFlavor"), approved_value)
            child(current_flavor, "iFlavor").text = child(
                baseline_flavor, "iFlavor"
            ).text
        self.assert_node_equal(current, baseline, LEADERS, type_name)

    def test_stalin_has_only_factory_trait_addition(self) -> None:
        type_name = "TRAIT_STALIN"
        current, baseline = self.pair(TRAITS, "TraitInfo", type_name)
        self.assertEqual(direct_children(baseline, "BuildingYieldChanges"), [])
        containers = direct_children(current, "BuildingYieldChanges")
        self.assertEqual(len(containers), 1)
        self.assertEqual(len(containers[0]), 1)
        factory = containers[0][0]
        self.assertEqual(
            text(factory, "BuildingClassType"), "BUILDINGCLASS_FACTORY"
        )
        self.assertEqual(
            [
                (item.text or "").strip()
                for item in child(factory, "BuildingYields")
            ],
            ["0", "1", "0"],
        )
        current.remove(containers[0])
        self.assert_node_equal(current, baseline, TRAITS, type_name)
        self.assert_exact(
            CIVILIZATIONS, "CivilizationInfo", "CIVILIZATION_USSR"
        )

    def test_churchill_has_only_espionage_flavor_delta(self) -> None:
        type_name = "LEADER_CHURCHILL"
        current, baseline = self.pair(LEADERS, "LeaderHeadInfo", type_name)
        flavors = child(current, "Flavors")
        espionage = [
            item
            for item in flavors
            if text(item, "FlavorType") == "FLAVOR_ESPIONAGE"
        ]
        self.assertEqual(len(espionage), 1)
        self.assertEqual(text(espionage[0], "iFlavor"), "3")
        self.assertEqual(
            [
                item
                for item in child(baseline, "Flavors")
                if text(item, "FlavorType") == "FLAVOR_ESPIONAGE"
            ],
            [],
        )
        flavors.remove(espionage[0])
        self.assert_node_equal(current, baseline, LEADERS, type_name)

    def test_peter_has_only_approved_science_deltas(self) -> None:
        type_name = "TRAIT_PETER"
        current, baseline = self.pair(TRAITS, "TraitInfo", type_name)
        self.normalize_direct_field(
            current, baseline, "iGreatPeopleRateModifier", "50"
        )
        self.assertEqual(direct_children(baseline, "Help"), [])
        help_nodes = direct_children(current, "Help")
        self.assertEqual(len(help_nodes), 1)
        self.assertEqual(
            (help_nodes[0].text or "").strip(),
            "TXT_KEY_TRAIT_PETER_HELP",
        )
        current.remove(help_nodes[0])
        for building_class, approved_research in (
            ("BUILDINGCLASS_LIBRARY", "2"),
            ("BUILDINGCLASS_UNIVERSITY", "3"),
        ):
            current_entry = keyed_entry(
                current,
                "BuildingCommerceChanges",
                "BuildingClassType",
                building_class,
            )
            baseline_entry = keyed_entry(
                baseline,
                "BuildingCommerceChanges",
                "BuildingClassType",
                building_class,
            )
            current_values = child(current_entry, "BuildingCommerces")
            baseline_values = child(baseline_entry, "BuildingCommerces")
            self.assertEqual((current_values[1].text or "").strip(), approved_research)
            current_values[1].text = baseline_values[1].text
        self.assert_node_equal(current, baseline, TRAITS, type_name)

        for building_type in (
            "BUILDING_PETER_ADMIRALTY",
            "BUILDING_PETER_COLLEGIUM_OF_FOREIGN_AFFAIRS",
        ):
            with self.subTest(type=building_type, path=BUILDINGS):
                current, baseline = self.pair(
                    BUILDINGS, "BuildingInfo", building_type
                )
                current_values = child(current, "CommerceModifiers")
                baseline_values = child(baseline, "CommerceModifiers")
                self.assertEqual((current_values[1].text or "").strip(), "25")
                current_values[1].text = baseline_values[1].text
                self.assert_node_equal(
                    current, baseline, BUILDINGS, building_type
                )

    def test_kublai_civ_has_only_secretariat_mapping_delta(self) -> None:
        type_name = "CIVILIZATION_YUAN_DYNASTY"
        current, baseline = self.pair(
            CIVILIZATIONS, "CivilizationInfo", type_name
        )
        buildings = child(current, "Buildings")
        secretariat = [
            item
            for item in buildings
            if text(item, "BuildingClassType") == "BUILDINGCLASS_PALACE"
            and text(item, "BuildingType")
            == "BUILDING_YUAN_IMPERIAL_SECRETARIAT"
        ]
        self.assertEqual(len(secretariat), 1)
        self.assertEqual(
            text(
                keyed_entry(
                    current,
                    "Buildings",
                    "BuildingClassType",
                    "BUILDINGCLASS_GREAT_PALACE",
                ),
                "BuildingType",
            ),
            "BUILDING_MONGOLIAN_PALACE",
        )
        buildings.remove(secretariat[0])
        self.assert_node_equal(
            current, baseline, CIVILIZATIONS, type_name
        )

    def test_corporations_only_change_approved_gold_value(self) -> None:
        approved_gold = {
            "CORPORATION_1": "100",
            "CORPORATION_2": "200",
            "CORPORATION_3": "350",
            "CORPORATION_4": "100",
            "CORPORATION_5": "250",
            "CORPORATION_6": "200",
        }
        for type_name, value in approved_gold.items():
            with self.subTest(type=type_name, path=CORPORATIONS):
                current, baseline = self.pair(
                    CORPORATIONS, "CorporationInfo", type_name
                )
                current_values = child(current, "CommercesProduced")
                baseline_values = child(baseline, "CommercesProduced")
                self.assertEqual((current_values[0].text or "").strip(), value)
                current_values[0].text = baseline_values[0].text
                self.assert_node_equal(
                    current, baseline, CORPORATIONS, type_name
                )
        self.assert_exact(
            CORPORATIONS, "CorporationInfo", "CORPORATION_7"
        )

    def test_free_market_only_removes_town_food(self) -> None:
        type_name = "CIVIC_FREE_MARKET"
        current, baseline = self.pair(CIVICS, "CivicInfo", type_name)
        current_changes = child(current, "ImprovementYieldChanges")
        baseline_changes = child(baseline, "ImprovementYieldChanges")
        self.assertEqual(len(current_changes), 0)
        self.assertEqual(len(baseline_changes), 1)
        town = baseline_changes[0]
        self.assertEqual(text(town, "ImprovementType"), "IMPROVEMENT_TOWN")
        self.assertEqual(
            [
                (item.text or "").strip()
                for item in child(town, "ImprovementYields")
            ],
            ["1", "0", "0"],
        )
        current_changes.append(copy.deepcopy(town))
        self.assert_node_equal(current, baseline, CIVICS, type_name)


if __name__ == "__main__":
    unittest.main()
