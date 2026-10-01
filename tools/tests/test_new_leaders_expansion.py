from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from add_expansion_packages import ASSETS, XML, FILES, MANIFEST, append_record, baseline, canonical, parse, trait_scalar, retarget_kfm_model, resize_portrait_button
from flags.flag_pipeline import validate_manifest_against_live


class ExpansionWriterTests(unittest.TestCase):
    def test_reviewed_model_repairs_change_only_one_length_prefixed_filename(self):
        import struct
        from prepare_expansion_texture_paths import ART, SPECS
        for spec in SPECS:
            original = (ART / spec["folder"] / spec["source"]).read_bytes()
            output = (ART / spec["folder"] / spec["target"]).read_bytes()
            old = struct.pack("<I", len(spec["old"])) + spec["old"]
            new = struct.pack("<I", len(spec["new"])) + spec["new"]
            matches = 0
            offset = original.find(old)
            while offset >= 0:
                matches += output == original[:offset] + new + original[offset + len(old):]
                offset = original.find(old, offset + len(old))
            self.assertEqual(matches, 1, spec["folder"])

    def test_portrait_resize_retains_rgba_content_without_crop(self):
        import io
        from PIL import Image
        image = Image.new("RGBA", (61, 61), (120, 60, 200, 128))
        image.putpixel((0, 0), (255, 255, 255, 255))
        source = io.BytesIO()
        image.save(source, format="DDS")
        output = resize_portrait_button(source.getvalue(), [61, 61], [64, 64])
        decoded = Image.open(io.BytesIO(output))
        self.assertEqual(decoded.size, (64, 64))
        self.assertEqual(decoded.tobytes(), image.resize((64, 64), Image.Resampling.LANCZOS).tobytes())
        with self.assertRaisesRegex(ValueError, "input dimensions"):
            resize_portrait_button(source.getvalue(), [60, 60], [64, 64])
        with self.assertRaisesRegex(ValueError, "powers of two"):
            resize_portrait_button(source.getvalue(), [61, 61], [63, 63])

    def test_optional_trait_scalar_is_schema_checked(self):
        schema = parse((XML / "Civilizations/CIV4CivilizationsSchema.xml").read_bytes())
        node = parse("<TraitInfo><Type>TEST</Type><iHealth>0</iHealth></TraitInfo>")
        trait_scalar(node, "iOpenBordersKnownTechResearchModifier", 20, schema)
        trait_scalar(node, "iHealth", 1, schema)
        self.assertEqual(node.findtext("iOpenBordersKnownTechResearchModifier"), "20")
        self.assertEqual(node.findtext("iHealth"), "1")
        for tag, value in (("iOpenBorderKnownTechResearchModifier", 20), ("FreePromotions", 1),
                           ("Description", 1), ("iHealth", "bad"), ("iHealth", True)):
            with self.subTest(tag=tag, value=value), self.assertRaisesRegex(ValueError, "declared integer"):
                trait_scalar(node, tag, value, schema)
        with self.assertRaisesRegex(ValueError, "Missing required"):
            trait_scalar(node, "iHappiness", 1, schema)

    def test_kfm_retarget_preserves_every_animation_byte(self):
        import struct
        header = b";Gamebryo KFM File Version 1.2.4b\n"
        old, new = "alexander.nif", "Bolivar.nif"
        suffix = b"\x0c\x00\x00\x00_alex_parent\x00animation-payload"
        source = header + struct.pack("<I", len(old)) + old.encode() + suffix
        expected = header + struct.pack("<I", len(new)) + new.encode() + suffix
        self.assertEqual(retarget_kfm_model(source, old, new), expected)
        with self.assertRaisesRegex(ValueError, "binding differs"):
            retarget_kfm_model(source, "incorrect.nif", new)
        with self.assertRaisesRegex(ValueError, "version"):
            retarget_kfm_model(b"unreviewed", old, new)
        newer = b";Gamebryo KFM File Version 2.0.0.0b\n\x01"
        source2 = newer + struct.pack("<I", len(old)) + old.encode() + suffix
        self.assertEqual(retarget_kfm_model(source2, old, new),
                         newer + struct.pack("<I", len(new)) + new.encode() + suffix)
        with self.assertRaisesRegex(ValueError, "version"):
            retarget_kfm_model(source2.replace(b"\n\x01", b"\n\x00", 1), old, new)

    def test_all_reviewed_fragments_are_well_formed(self):
        for package in json.loads(MANIFEST.read_bytes())["packages"]:
            for label, fragment in (("trait", package["trait_xml"]), ("unit", package["unit"]["xml"]), ("building", package["building"]["xml"])):
                with self.subTest(package=package["id"], fragment=label):
                    parse("<Root>" + fragment + "</Root>")

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
                added_count = sum("promotion" in p for p in packages) if kind == "promotion" else len(packages)
                self.assertEqual(len(new), len(old) + added_count)

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

    def test_worked_plot_packages_have_exact_conditions_caps_and_tradeoffs(self):
        ram = self.entry("trait", "TRAIT_EXP_RAMKHAMHAENG")
        self.assertEqual(ram.findtext("WorkedPlotCondition"), "RIVERSIDE_IMPROVEMENT")
        self.assertEqual(ram.findtext("WorkedPlotPrereqTech"), "TECH_WRITING")
        self.assertEqual((ram.findtext("iWorkedPlotCulture"), ram.findtext("iWorkedPlotCap")), ("1", "3"))
        self.assertEqual([n.text for n in ram.findall("WorkedPlotImprovements/ImprovementType")], ["IMPROVEMENT_FARM"])
        self.assertIsNone(ram.find("WorkedPlotPrereqBuilding"))
        ho = self.entry("trait", "TRAIT_EXP_HO_CHI_MINH")
        self.assertEqual(ho.findtext("WorkedPlotCondition"), "WOODLAND")
        self.assertEqual((ho.findtext("iWorkedPlotProduction"), ho.findtext("iWorkedPlotCap"),
                          ho.findtext("iDomesticGreatGeneralRateModifier")), ("1", "3", "50"))
        self.assertIsNone(ho.find("WorkedPlotImprovements"))
        askia = self.entry("trait", "TRAIT_EXP_ASKIA")
        self.assertEqual(askia.findtext("WorkedPlotCondition"), "RIVERSIDE_IMPROVEMENT")
        self.assertEqual((askia.findtext("iWorkedPlotGold"), askia.findtext("iWorkedPlotCap")), ("1", "4"))
        self.assertEqual([n.text for n in askia.findall("WorkedPlotImprovements/ImprovementType")],
                         ["IMPROVEMENT_COTTAGE", "IMPROVEMENT_HAMLET", "IMPROVEMENT_VILLAGE", "IMPROVEMENT_TOWN"])
        infantry = self.entry("unit", "UNIT_EXP_VIET_MINH_INFANTRY")
        self.assertEqual((infantry.findtext("iCost"), infantry.findtext("iCombat")), ("120", "18"))
        self.assertEqual([n.text for n in infantry.findall("FreePromotions/FreePromotion/PromotionType")],
                         ["PROMOTION_WOODSMAN1", "PROMOTION_WOODSMAN2"])
        headquarters = self.entry("building", "BUILDING_EXP_RESISTANCE_HEADQUARTERS")
        self.assertEqual((headquarters.findtext("PrereqTech"), headquarters.findtext("iMilitaryProductionModifier")),
                         ("TECH_UTOPIA", "15"))
        library = self.entry("building", "BUILDING_EXP_HO_TRAI")
        self.assertEqual([n.text for n in library.findall("CommerceChanges/iCommerce")], ["0", "0", "2", "0"])
        self.assertEqual([n.text for n in library.findall("ObsoleteSafeCommerceChanges/iCommerce")], ["0", "0", "2"])
        self.assertEqual([(n.findtext("SpecialistType"), n.findtext("iSpecialistCount"))
                          for n in library.findall("SpecialistCounts/SpecialistCount")],
                         [("SPECIALIST_SCIENTIST", "2"), ("SPECIALIST_PRIEST", "1")])

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
            self.assertNotIn(b"\r", (ROOT / record["master_path"]).read_bytes(), "SVG digest must survive Git's LF normalization")
            data = (ASSETS / record["runtime_dds_path"]).read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(), record["production_dds_sha256"])
            validate_dds(data)
            self.assertEqual(sum(m["nonzero_alpha_texel_count"] for m in alpha_block_summary(data)), 0)

    def test_professionals_are_granted_only_to_eligible_combat_classes(self):
        trait = self.entry("trait", "TRAIT_EXP_MATTHIAS")
        self.assertEqual(
            {n.text for n in trait.findall("FreePromotionUnitCombats/FreePromotionUnitCombat/UnitCombatType")},
            {"UNITCOMBAT_MELEE", "UNITCOMBAT_GUN"},
        )
        promo = self.entry("promotion", "PROMOTION_EXP_PAID_PROFESSIONALS")
        self.assertEqual(promo.findtext("iUpgradeDiscount"), "25")
        self.assertEqual(promo.findtext("bLeader"), "1", "Must not be generally selectable by unrelated units")
        self.assertEqual(promo.findtext("iCombatPercent"), "0")
        source = (ROOT / "third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvUnit.cpp").read_text()
        override = source.index('"getUpgradePriceOverride"')
        discount = source.index("iPrice -= (iPrice * getUpgradeDiscount()) / 100;", override)
        self.assertIn("return lResult;", source[override:discount])

    def test_diplomatic_and_conquest_packages_match_approved_numbers(self):
        mongkut = self.entry("trait", "TRAIT_EXP_MONGKUT")
        bolivar = self.entry("trait", "TRAIT_EXP_BOLIVAR")
        self.assertEqual(mongkut.findtext("iOpenBordersKnownTechResearchModifier"), "20")
        self.assertEqual(bolivar.findtext("iConquestOccupationReductionPercent"), "50")
        self.assertEqual(bolivar.findtext("iGreatGeneralRateModifier"), "50")
        for trait in self.live["trait"].iter("TraitInfo"):
            name = trait.findtext("Type")
            self.assertEqual(int(trait.findtext("iOpenBordersKnownTechResearchModifier", "0")),
                             20 if name == "TRAIT_EXP_MONGKUT" else 0)
            self.assertEqual(int(trait.findtext("iConquestOccupationReductionPercent", "0")),
                             50 if name == "TRAIT_EXP_BOLIVAR" else 0)
        rifle = self.entry("unit", "UNIT_EXP_SIAMESE_ROYAL_RIFLE")
        self.assertEqual((rifle.findtext("iCost"), rifle.findtext("iCombat"), rifle.findtext("iCityDefense")),
                         ("120", "14", "25"))
        llanero = self.entry("unit", "UNIT_EXP_LLANERO")
        self.assertEqual(tuple(llanero.findtext(tag) for tag in ("iCost", "iCombat", "iMoves", "iWithdrawalProb")),
                         ("140", "15", "3", "40"))
        observatory = self.entry("building", "BUILDING_EXP_ROYAL_OBSERVATORY")
        self.assertEqual(observatory.findtext("SpecialistCounts/SpecialistCount/iSpecialistCount"), "2")
        cabildo = self.entry("building", "BUILDING_EXP_REPUBLICAN_CABILDO")
        experience = cabildo.find("DomainFreeExperiences/DomainFreeExperience")
        self.assertEqual((experience.findtext("DomainType"), experience.findtext("iExperience")), ("DOMAIN_LAND", "2"))

    def test_reviewed_art_repairs_match_exact_inputs_and_outputs(self):
        import hashlib
        for package in self.document["packages"]:
            for repair in package.get("repairs", []):
                with self.subTest(package=package["id"], target=repair["target"]):
                    source = (ASSETS / repair["source"]).read_bytes()
                    current = (ASSETS / repair["target"]).read_bytes()
                    self.assertEqual(hashlib.sha256(source).hexdigest(), repair["sha256"])
                    if "prepared_sha256" in repair:
                        self.assertEqual(hashlib.sha256(current).hexdigest(), repair["prepared_sha256"])
                    else:
                        expected = source
                        if "kfm_model" in repair:
                            expected = retarget_kfm_model(source, **repair["kfm_model"])
                        if "portrait_resize" in repair:
                            expected = resize_portrait_button(source, **repair["portrait_resize"])
                        self.assertEqual(current, expected)

    def test_coastal_trade_package_is_capped_and_preserves_transport_role(self):
        trait = self.entry("trait", "TRAIT_EXP_HIRAM")
        self.assertEqual(trait.findtext("iCoastalForeignTeamGold"), "1")
        self.assertEqual(trait.findtext("iCoastalForeignTeamGoldCap"), "3")
        for current in self.live["trait"].iter("TraitInfo"):
            if current.findtext("Type") != "TRAIT_EXP_HIRAM":
                self.assertEqual(current.findtext("iCoastalForeignTeamGold", "0"), "0")
                self.assertEqual(current.findtext("iCoastalForeignTeamGoldCap", "0"), "0")
        ship = self.entry("unit", "UNIT_EXP_TYRIAN_MERCHANT_GALLEY")
        self.assertEqual(tuple(ship.findtext(tag) for tag in ("iCost", "iMoves", "iCombat")),
                         ("60", "3", "2"))
        parent = self.entry("unit", "UNIT_GALLEY", original=True)
        for tag in ("iCargo", "SpecialCargo", "DomainCargo", "TerrainImpassables"):
            self.assertEqual(canonical(ship.find(tag)), canonical(parent.find(tag)))
        house = self.entry("building", "BUILDING_EXP_TYRIAN_COUNTING_HOUSE")
        self.assertEqual(house.findtext("iForeignTradeRouteModifier"), "25")


if __name__ == "__main__":
    unittest.main()
