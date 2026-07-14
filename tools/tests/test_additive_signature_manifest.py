from __future__ import annotations

import copy
import json
import subprocess
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASELINE = "7da9963f6"
XML_ROOT = (
    "CoreFiles/Sid Meier's Civilization IV Beyond the Sword/"
    "Beyond the Sword/Assets/XML"
)
TRAITS = f"{XML_ROOT}/Civilizations/CIV4TraitInfos.xml"
LEADERS = f"{XML_ROOT}/Civilizations/CIV4LeaderHeadInfos.xml"
CIVS = f"{XML_ROOT}/Civilizations/CIV4CivilizationInfos.xml"
CLASSES = f"{XML_ROOT}/Buildings/CIV4BuildingClassInfos.xml"
MANIFEST = ROOT / "tools/manifests/additive_signature_manifest.json"


def local_name(tag):
    return tag.rsplit("}", 1)[-1]


def children(node, name):
    return [item for item in node if local_name(item.tag) == name]


def child(node, name):
    matches = children(node, name)
    if len(matches) != 1:
        raise AssertionError(f"expected one {name}, found {len(matches)}")
    return matches[0]


def text(node, name):
    return (child(node, name).text or "").strip()


def entries(root, name):
    return [node for node in root.iter() if local_name(node.tag) == name]


def info(root, entry_name, type_name):
    matches = [
        node for node in entries(root, entry_name)
        if children(node, "Type") and text(node, "Type") == type_name
    ]
    if len(matches) != 1:
        raise AssertionError(f"expected one {type_name}, found {len(matches)}")
    return matches[0]


def canonical(node):
    result = copy.deepcopy(node)
    for item in result.iter():
        item.tail = None
        if item.text is not None:
            item.text = item.text.strip() or None
    return ET.tostring(result, encoding="unicode")


def load_root(source, path):
    if source == "current":
        return ET.parse(ROOT / path).getroot()
    data = subprocess.run(
        ["git", "show", f"{BASELINE}:{path}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    ).stdout
    return ET.fromstring(data)


class AdditiveSignatureManifestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        cls.current_traits = load_root("current", TRAITS)
        cls.baseline_traits = load_root("baseline", TRAITS)
        cls.leaders = load_root("current", LEADERS)
        cls.civs = load_root("current", CIVS)
        cls.classes = {
            text(node, "Type")
            for node in entries(load_root("current", CLASSES), "BuildingClassInfo")
        }

    def test_manifest_covers_each_playable_package_trait_once(self):
        leader_traits = {}
        for leader in entries(self.leaders, "LeaderHeadInfo"):
            active = [
                text(item, "TraitType")
                for item in child(leader, "Traits")
                if text(item, "bTrait") == "1"
            ]
            if active:
                leader_traits[text(leader, "Type")] = active

        playable_traits = []
        for civ in entries(self.civs, "CivilizationInfo"):
            if text(civ, "bPlayable") != "1":
                continue
            leaders = [
                text(item, "LeaderName")
                for item in child(civ, "Leaders")
                if text(item, "bLeaderAvailability") == "1"
            ]
            self.assertEqual(len(leaders), 1, text(civ, "Type"))
            self.assertEqual(len(leader_traits[leaders[0]]), 1, leaders[0])
            playable_traits.append(leader_traits[leaders[0]][0])

        manifest_traits = [row["trait"] for row in self.manifest]
        self.assertEqual(len(playable_traits), 59)
        self.assertEqual(len(manifest_traits), 59)
        self.assertEqual(set(manifest_traits), set(playable_traits))
        self.assertEqual(len(manifest_traits), len(set(manifest_traits)))

    def test_all_manifest_building_classes_resolve(self):
        for row in self.manifest:
            self.assertIn(row["building_class"], self.classes, row["trait"])

    def test_every_trait_has_only_its_approved_additive_delta(self):
        for row in self.manifest:
            with self.subTest(trait=row["trait"]):
                current = copy.deepcopy(
                    info(self.current_traits, "TraitInfo", row["trait"])
                )
                baseline = info(
                    self.baseline_traits, "TraitInfo", row["trait"]
                )
                container_name = (
                    "BuildingCommerceChanges"
                    if row["channel"] == "commerce"
                    else "BuildingYieldChanges"
                )
                entry_name = (
                    "BuildingCommerceChange"
                    if row["channel"] == "commerce"
                    else "BuildingYieldChange"
                )
                vector_name = (
                    "BuildingCommerces"
                    if row["channel"] == "commerce"
                    else "BuildingYields"
                )
                item_name = (
                    "iCommerce" if row["channel"] == "commerce" else "iYield"
                )

                current_containers = children(current, container_name)
                baseline_containers = children(baseline, container_name)
                self.assertEqual(len(current_containers), 1)
                current_container = current_containers[0]
                current_entries = [
                    item for item in current_container
                    if local_name(item.tag) == entry_name
                    and text(item, "BuildingClassType")
                    == row["building_class"]
                ]
                self.assertEqual(len(current_entries), 1)
                current_entry = current_entries[0]

                baseline_entry = None
                if baseline_containers:
                    matches = [
                        item for item in baseline_containers[0]
                        if local_name(item.tag) == entry_name
                        and text(item, "BuildingClassType")
                        == row["building_class"]
                    ]
                    self.assertLessEqual(len(matches), 1)
                    baseline_entry = matches[0] if matches else None

                vector = child(current_entry, vector_name)
                values = [
                    int((item.text or "0").strip())
                    for item in vector
                    if local_name(item.tag) == item_name
                ]
                expected_base = [0] * len(row["delta"])
                if baseline_entry is not None:
                    expected_base = [
                        int((item.text or "0").strip())
                        for item in child(baseline_entry, vector_name)
                        if local_name(item.tag) == item_name
                    ]
                self.assertEqual(
                    values,
                    [
                        left + right
                        for left, right in zip(expected_base, row["delta"])
                    ],
                )

                if baseline_entry is None:
                    current_container.remove(current_entry)
                else:
                    for item, value in zip(vector, expected_base):
                        item.text = str(value)
                if not list(current_container) and not baseline_containers:
                    current.remove(current_container)
                self.assertEqual(canonical(current), canonical(baseline))

    def test_every_delta_is_strictly_additive_and_meaningful(self):
        for row in self.manifest:
            self.assertIn(row["channel"], {"yield", "commerce"})
            self.assertEqual(len(row["delta"]), 3 if row["channel"] == "yield" else 4)
            self.assertTrue(all(value >= 0 for value in row["delta"]))
            self.assertEqual(sum(row["delta"]), 1)
            self.assertTrue(row["signature"])
            self.assertTrue(row["rationale"])


if __name__ == "__main__":
    unittest.main()
