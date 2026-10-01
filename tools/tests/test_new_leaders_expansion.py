from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from add_expansion_packages import ASSETS, XML, FILES, MANIFEST, append_record, baseline, canonical, parse
from flags.flag_pipeline import validate_manifest_against_live


class ExpansionWriterTests(unittest.TestCase):
    def test_append_preserves_existing_bytes_and_is_idempotent(self):
        data = b'<?xml version="1.0"?><Root><Infos><Info><Type>OLD</Type></Info></Infos></Root>'
        addition = parse("<Info><Type>NEW</Type><Value>1</Value></Info>")
        output = append_record(data, addition, "Infos")
        self.assertEqual(output.count(b"<?xml"), 1)
        self.assertEqual([n.text for n in parse(output).iter("Type")], ["OLD", "NEW"])
        self.assertIn(b"<Info><Type>OLD</Type></Info>", output)
        self.assertEqual(append_record(output, addition, "Infos"), output)
        addition.find("Value").text = "2"
        with self.assertRaisesRegex(ValueError, "differs"):
            append_record(output, addition, "Infos")


class ExpansionContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = json.loads(MANIFEST.read_bytes())
        cls.live = {kind: parse((XML / row[0]).read_bytes()) for kind, row in FILES.items()}
        cls.original = {kind: baseline(XML / row[0], cls.document["baseline_commit"]) for kind, row in FILES.items()}

    def entry(self, kind, identifier, original=False):
        root = (self.original if original else self.live)[kind]
        matches = [n for n in root.iter(FILES[kind][1]) if n.findtext("Type") == identifier]
        self.assertEqual(len(matches), 1, identifier)
        return matches[0]

    def test_selected_scope_and_old_prefix_are_exact(self):
        self.assertEqual(set(self.document["approved_leaders"]), {
            "SENNACHERIB", "HIRAM", "PIYE", "MATTHIAS", "RAMKHAMHAENG", "MONGKUT",
            "HO_CHI_MINH", "ASKIA", "DUSAN", "PEDRO_II", "BOLIVAR", "ZENOBIA", "DAVID",
        })
        packages = self.document["packages"]
        self.assertEqual(len({p["id"] for p in packages}), len(packages))
        self.assertTrue({p["id"] for p in packages} <= set(self.document["approved_leaders"]))
        for kind, (_, entry_tag, _) in FILES.items():
            with self.subTest(kind=kind):
                old = list(self.original[kind].iter(entry_tag))
                new = list(self.live[kind].iter(entry_tag))
                self.assertEqual([canonical(n) for n in new[:len(old)]], [canonical(n) for n in old])
                self.assertEqual(len(new), len(old) + len(packages))

    def test_unit_and_building_deltas_retain_all_unmodified_parent_fields(self):
        for package in self.document["packages"]:
            for kind in ("unit", "building"):
                spec = package[kind]
                current = copy.deepcopy(self.entry(kind, kind.upper() + "_EXP_" + spec["id"]))
                parent = self.entry(kind, spec["parent"], original=True)
                fragment = parse("<Root>" + spec["xml"] + "</Root>")
                changed = set(spec["scalars"]) | {n.tag for n in fragment}
                with self.subTest(package=package["id"], kind=kind):
                    for tag, expected in spec["scalars"].items():
                        self.assertEqual(current.findtext(tag), str(expected))
                    for expected in fragment:
                        self.assertEqual(canonical(current.find(expected.tag)), canonical(expected))
                    for node in parent:
                        if node.tag not in changed | {"Type", "Description", "Civilopedia", "Strategy", "Help"}:
                            self.assertEqual(canonical(current.find(node.tag)), canonical(node), node.tag)

    def test_pilot_numeric_contracts(self):
        priest = "SPECIALIST_PRIEST"
        piye = self.entry("trait", "TRAIT_EXP_PIYE")
        self.assertEqual(piye.findtext("iDomesticGreatGeneralRateModifier"), "25")
        self.assertEqual(piye.findtext("SpecialistYieldChanges/SpecialistYieldChange/SpecialistType"), priest)
        self.assertEqual([n.text for n in piye.findall("SpecialistYieldChanges/SpecialistYieldChange/SpecialistYields/iYield")], ["1", "0", "0"])
        dusan = self.entry("trait", "TRAIT_EXP_DUSAN")
        self.assertEqual(dusan.findtext("ImprovementYieldChanges/ImprovementYieldChange/ImprovementType"), "IMPROVEMENT_MINE")
        self.assertEqual([n.text for n in dusan.findall("ImprovementYieldChanges/ImprovementYieldChange/ImprovementYields/iYield")], ["0", "0", "1"])
        self.assertEqual([n.text for n in dusan.findall("SpecialistCommerceChanges/SpecialistCommerceChange/SpecialistCommerces/iCommerce")], ["0", "0", "0", "1"])
        archer = self.entry("unit", "UNIT_EXP_KUSHITE_ARCHER")
        self.assertEqual((archer.findtext("iCost"), archer.findtext("iCombat"), archer.findtext("iFirstStrikes"), archer.findtext("iHillsAttack")), ("25", "3", "2", "25"))
        chapel = self.entry("building", "BUILDING_EXP_NAPATAN_CULT_CHAPEL")
        self.assertEqual(chapel.findtext("ObsoleteTech"), "TECH_ASTRONOMY")
        self.assertEqual(chapel.findtext("SpecialistCounts/SpecialistCount/iSpecialistCount"), "1")

    def test_one_selected_leader_and_only_own_unique_content(self):
        civs = list(self.live["civ"].iter("CivilizationInfo"))
        self.assertEqual(sum(n.findtext("bPlayable") == "1" for n in civs), 59 + len(self.document["packages"]))
        for package in self.document["packages"]:
            civ = self.entry("civ", "CIVILIZATION_EXP_" + package["civilization"])
            self.assertEqual([n.text for n in civ.findall("Leaders/Leader/LeaderName")], ["LEADER_EXP_" + package["id"]])
            self.assertEqual([n.text for n in civ.findall("Units/Unit/UnitType")], ["UNIT_EXP_" + package["unit"]["id"]])
            self.assertEqual([n.text for n in civ.findall("Buildings/Building/BuildingType")], ["BUILDING_EXP_" + package["building"]["id"]])
            self.assertEqual([n.text for n in civ.findall("FreeTechs/FreeTech/TechType")], package["techs"])
            leader = self.entry("leader", "LEADER_EXP_" + package["id"])
            self.assertEqual([n.text for n in leader.findall("Traits/Trait/TraitType")], ["TRAIT_EXP_" + package["id"]])

    def test_flags_preserve_every_original_record_and_validate_new_outputs(self):
        import hashlib
        import subprocess
        from flags.dxt3_fullcolor import alpha_block_summary, validate_dds
        path = ROOT / "tools/flags/manifest.json"
        old = json.loads(subprocess.check_output(["git", "show", self.document["baseline_commit"] + ":tools/flags/manifest.json"], cwd=ROOT))
        current = json.loads(path.read_bytes())
        self.assertEqual(current["records"][:59], old["records"])
        self.assertEqual(len(current["records"]), 59 + len(self.document["packages"]))
        validate_manifest_against_live(require_fixed_color=True)
        for record in current["records"][59:]:
            data = (ASSETS / record["runtime_dds_path"]).read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(), record["production_dds_sha256"])
            validate_dds(data)
            self.assertEqual(sum(m["nonzero_alpha_texel_count"] for m in alpha_block_summary(data)), 0)


if __name__ == "__main__":
    unittest.main()
