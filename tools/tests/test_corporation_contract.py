from __future__ import annotations

import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CORPORATIONS = (
    ROOT
    / "CoreFiles"
    / "Sid Meier's Civilization IV Beyond the Sword"
    / "Beyond the Sword"
    / "Assets"
    / "XML"
    / "GameInfo"
    / "CIV4CorporationInfo.xml"
)


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def child(node: ET.Element, name: str) -> ET.Element:
    return next(item for item in node if local_name(item.tag) == name)


def text(node: ET.Element, name: str) -> str:
    return (child(node, name).text or "").strip()


def values(node: ET.Element, name: str) -> list[int]:
    return [int((item.text or "0").strip()) for item in child(node, name)]


class CorporationContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        entries = [
            node
            for node in ET.parse(CORPORATIONS).getroot().iter()
            if local_name(node.tag) == "CorporationInfo"
        ]
        cls.by_type = {text(node, "Type"): node for node in entries}

    def test_active_corporation_commerce_outputs_are_exact(self) -> None:
        expected = {
            "CORPORATION_1": [100, 0, 0, 0],
            "CORPORATION_2": [200, 0, 100, 0],
            "CORPORATION_3": [350, 0, 100, 0],
            "CORPORATION_4": [100, 0, 150, 100],
            "CORPORATION_5": [250, 0, 150, 0],
            "CORPORATION_6": [200, 0, 200, 0],
        }
        self.assertEqual(
            {
                corporation: values(self.by_type[corporation], "CommercesProduced")
                for corporation in expected
            },
            expected,
        )

    def test_active_corporation_non_gold_outputs_are_preserved(self) -> None:
        expected = {
            "CORPORATION_1": [0, 0, 0],
            "CORPORATION_2": [0, 100, 0],
            "CORPORATION_3": [0, 100, 0],
            "CORPORATION_4": [0, 150, 100],
            "CORPORATION_5": [0, 150, 0],
            "CORPORATION_6": [0, 200, 0],
        }
        self.assertEqual(
            {
                corporation: values(self.by_type[corporation], "CommercesProduced")[1:]
                for corporation in expected
            },
            expected,
        )

    def test_corporation_seven_remains_fully_inert(self) -> None:
        node = self.by_type["CORPORATION_7"]
        self.assertEqual(text(node, "TechPrereq"), "NONE")
        self.assertEqual(text(node, "FreeUnitClass"), "NONE")
        self.assertEqual(text(node, "iSpreadFactor"), "0")
        self.assertEqual(text(node, "iSpreadCost"), "0")
        self.assertEqual(text(node, "iMaintenance"), "0")
        self.assertEqual(len(child(node, "FoundingBuildingClasses")), 0)
        self.assertEqual(len(child(node, "PrereqBonuses")), 0)
        self.assertEqual(values(node, "HeadquarterCommerces"), [0, 0, 0, 0])
        self.assertEqual(text(node, "BonusProduced"), "NONE")
        self.assertEqual(values(node, "CommercesProduced"), [0, 0, 0, 0])
        self.assertEqual(values(node, "YieldsProduced"), [0, 0, 0])
        self.assertEqual(text(node, "iFoundingMinActiveBuildingClasses"), "99")
        self.assertEqual(text(node, "bCountDistinctPrereqBonusesOnly"), "0")
        self.assertEqual(text(node, "iMaxPrereqBonusCountPerType"), "0")


if __name__ == "__main__":
    unittest.main()
