from __future__ import annotations

import copy
import hashlib
import json
import os
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = REPO_ROOT / "tools" / "manifests" / "industry_building_rebalance_proposal.json"
BUILDINGS_PATH = (
    REPO_ROOT
    / "CoreFiles"
    / "Sid Meier's Civilization IV Beyond the Sword"
    / "Beyond the Sword"
    / "Assets"
    / "XML"
    / "Buildings"
    / "CIV4BuildingInfos.xml"
)

SCALAR_FIELDS = (
    "iFoodKept",
    "iHealth",
    "iAreaHealth",
    "iGlobalHealth",
    "iHappiness",
    "iAreaHappiness",
    "iGlobalHappiness",
    "iStateReligionHappiness",
    "iGreatPeopleRateChange",
    "iGreatPeopleRateModifier",
    "iMaintenanceModifier",
    "iWorkerSpeedModifier",
    "iMilitaryProductionModifier",
    "iSpaceProductionModifier",
    "iTradeRoutes",
    "iCoastalTradeRoutes",
    "iGlobalTradeRoutes",
    "iTradeRouteModifier",
    "iForeignTradeRouteModifier",
    "iExperience",
    "iPower",
)
ARRAY_FIELDS = {
    "yield_changes": ("YieldChanges", "iYield", ("Food", "Production", "Commerce")),
    "yield_modifiers": ("YieldModifiers", "iYield", ("Food", "Production", "Commerce")),
    "commerce_changes": (
        "CommerceChanges",
        "iCommerce",
        ("Gold", "Research", "Culture", "Espionage"),
    ),
    "commerce_modifiers": (
        "CommerceModifiers",
        "iCommerce",
        ("Gold", "Research", "Culture", "Espionage"),
    ),
}
OUTPUT_XML_TAGS = set(SCALAR_FIELDS) | {spec[0] for spec in ARRAY_FIELDS.values()}
EXPECTED_ROW_KEYS = {
    "type",
    "proposal_category",
    "live_industry_category",
    "display_chain_role",
    "food_oriented",
    "current_cost",
    "proposed_cost",
    "current_outputs",
    "proposed_outputs",
    "protected_xml_sha256",
    "rationale",
    "risk",
}
RUNTIME_PREFIXES = (
    "CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/",
    "CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/Python/",
    "third_party/beyond-the-sword-sdk/CvGameCoreDLL/",
)
EXPECTED_FOOD_ROWS = {
    "BUILDING_INDUSTRY_AGRARIAN_BOARD",
    "BUILDING_INDUSTRY_PASTORAL_BOARD",
    "BUILDING_INDUSTRY_MARITIME_EXCHANGE",
    "BUILDING_INDUSTRY_SPICE_EXCHANGE",
    "BUILDING_INDUSTRY_CONFECTIONERS_GUILD",
    "BUILDING_INDUSTRY_VINTNERS_GUILD",
    "BUILDING_INDUSTRY_MILLERS_GUILD",
    "BUILDING_INDUSTRY_SMOKEHOUSE",
    "BUILDING_INDUSTRY_CANNERY",
    "BUILDING_INDUSTRY_FRUIT_PRESERVERS",
    "BUILDING_INDUSTRY_GRAND_BANQUET_HALL",
    "BUILDING_INDUSTRY_CONFECTIONERS_EXCHANGE",
    "BUILDING_INDUSTRY_FESTIVAL_MARKET",
    "BUILDING_INDUSTRY_BAKERS_EXCHANGE",
    "BUILDING_INDUSTRY_FESTIVAL_KITCHENS",
    "BUILDING_INDUSTRY_ROYAL_KITCHENS",
    "BUILDING_INDUSTRY_SPICED_CARVERY",
    "BUILDING_INDUSTRY_MARITIME_SUPPER_CLUB",
    "BUILDING_INDUSTRY_PRESERVES_MARKET",
    "BUILDING_INDUSTRY_PASTRY_HOUSE",
    "BUILDING_INDUSTRY_VICTUALLERS_EXCHANGE",
    "BUILDING_INDUSTRY_SPICED_FISH_MARKET",
    "BUILDING_INDUSTRY_DESSERT_CELLARS",
}


def local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def child(element: ET.Element, name: str) -> ET.Element | None:
    return next((node for node in element if local(node.tag) == name), None)


def child_text(element: ET.Element, name: str, default: str = "0") -> str:
    node = child(element, name)
    return (node.text or default).strip() if node is not None else default


def output_snapshot(building: ET.Element) -> dict:
    result = {"scalars": {name: int(child_text(building, name)) for name in SCALAR_FIELDS}}
    for output_name, (xml_tag, child_tag, labels) in ARRAY_FIELDS.items():
        node = child(building, xml_tag)
        values = [] if node is None else [
            int((entry.text or "0").strip())
            for entry in node
            if local(entry.tag) == child_tag
        ]
        if len(values) != len(labels):
            raise AssertionError(
                "%s has %d values for %s"
                % (child_text(building, "Type"), len(values), xml_tag)
            )
        result[output_name] = dict(zip(labels, values))
    return result


def normalize(element: ET.Element) -> None:
    element.tag = local(element.tag)
    element.attrib.clear()
    for node in element:
        normalize(node)


def protected_hash(building: ET.Element) -> str:
    protected = copy.deepcopy(building)
    normalize(protected)
    for node in list(protected):
        if node.tag == "iCost" or node.tag in OUTPUT_XML_TAGS:
            protected.remove(node)
    return hashlib.sha256(ET.tostring(protected, encoding="utf-8")).hexdigest()


class IndustryBuildingRebalanceProposalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        root = ET.parse(BUILDINGS_PATH).getroot()
        cls.buildings_by_type = {
            child_text(building, "Type"): building
            for building in root.iter()
            if local(building.tag) == "BuildingInfo"
            and child_text(building, "Type").startswith("BUILDING_INDUSTRY_")
        }
        cls.rows_by_type = {row["type"]: row for row in cls.manifest["buildings"]}

    def test_requested_inventory_is_exact_and_resolves_to_live_types(self) -> None:
        rows = self.manifest["buildings"]
        self.assertEqual(69, len(rows))
        self.assertEqual(
            {"CORE": 11, "LUXURY": 19, "COMPOSITE": 39},
            self.manifest["proposal_category_counts"],
        )
        self.assertEqual(
            self.manifest["proposal_category_counts"],
            {
                category: sum(row["proposal_category"] == category for row in rows)
                for category in ("CORE", "LUXURY", "COMPOSITE")
            },
        )
        self.assertEqual(69, len(self.rows_by_type), "proposal types must be unique")
        self.assertEqual(set(self.buildings_by_type), set(self.rows_by_type))
        self.assertEqual(
            {"CORE": 11, "LUXURY": 20, "COMPOSITE": 38},
            {
                category: sum(row["live_industry_category"] == category for row in rows)
                for category in ("CORE", "LUXURY", "COMPOSITE")
            },
        )
        self.assertEqual(
            [("BUILDING_INDUSTRY_SCULPTORS_YARD", "LUXURY", "COMPOSITE")],
            [
                (row["type"], row["live_industry_category"], row["proposal_category"])
                for row in rows
                if row["live_industry_category"] != row["proposal_category"]
            ],
        )

    def test_current_cost_output_and_protected_xml_snapshots_match_live_xml(self) -> None:
        default_live = (
            "proposed"
            if self.manifest["status"] == "approved-implemented"
            else "current"
        )
        expected_live = os.environ.get("INDUSTRY_PROPOSAL_EXPECT_LIVE", default_live)
        self.assertIn(expected_live, {"current", "proposed"})
        for building_type, row in self.rows_by_type.items():
            with self.subTest(building_type=building_type):
                building = self.buildings_by_type[building_type]
                self.assertEqual(
                    int(child_text(building, "iCost")),
                    row[expected_live + "_cost"],
                )
                self.assertEqual(
                    output_snapshot(building),
                    row[expected_live + "_outputs"],
                )
                self.assertEqual(child_text(building, "IndustryCategory"), row["live_industry_category"])
                self.assertEqual(protected_hash(building), row["protected_xml_sha256"])

    def test_proposal_changes_only_cost_and_declared_direct_output_fields(self) -> None:
        for building_type, row in self.rows_by_type.items():
            with self.subTest(building_type=building_type):
                self.assertEqual(EXPECTED_ROW_KEYS, set(row))
                self.assertLessEqual(row["proposed_cost"], row["current_cost"])
                self.assertEqual(set(row["current_outputs"]), set(row["proposed_outputs"]))
                self.assertEqual(
                    {"scalars", *ARRAY_FIELDS},
                    set(row["current_outputs"]),
                )
                for section in ("scalars", *ARRAY_FIELDS):
                    self.assertEqual(
                        set(row["current_outputs"][section]),
                        set(row["proposed_outputs"][section]),
                    )
                    for field, current in row["current_outputs"][section].items():
                        proposed = row["proposed_outputs"][section][field]
                        self.assertGreaterEqual(
                            proposed,
                            current,
                            "review proposal must not reduce any direct output",
                        )

    def test_food_oriented_rows_gain_literal_food(self) -> None:
        food_rows = [row for row in self.manifest["buildings"] if row["food_oriented"]]
        self.assertEqual(EXPECTED_FOOD_ROWS, {row["type"] for row in food_rows})
        for row in food_rows:
            with self.subTest(building_type=row["type"]):
                self.assertGreater(
                    row["proposed_outputs"]["yield_changes"]["Food"],
                    row["current_outputs"]["yield_changes"]["Food"],
                )

    def test_theoretical_food_stack_is_explicitly_bounded(self) -> None:
        # Live category caps permit at most 2 core + 2 luxury + 3 composite
        # buildings in one city. Each proposed food delta is exactly +2.
        deltas = {
            row["type"]: (
                row["proposed_outputs"]["yield_changes"]["Food"]
                - row["current_outputs"]["yield_changes"]["Food"]
            )
            for row in self.manifest["buildings"]
            if row["food_oriented"]
        }
        self.assertEqual({2}, set(deltas.values()))
        self.assertEqual(14, (2 + 2 + 3) * 2)

    def test_runtime_scope_is_limited_to_the_approved_building_xml(self) -> None:
        self.assertEqual(
            [
                "CoreFiles/Sid Meier's Civilization IV Beyond the Sword/"
                "Beyond the Sword/Assets/XML/Buildings/CIV4BuildingInfos.xml"
            ],
            self.manifest["runtime_files_modified"],
        )
        self.assertTrue(
            all(
                path.startswith(RUNTIME_PREFIXES)
                for path in self.manifest["runtime_files_modified"]
            )
        )


if __name__ == "__main__":
    unittest.main()
