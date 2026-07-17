from __future__ import annotations

import re
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
XML = ASSETS / "XML"
DLL = ROOT / "third_party" / "beyond-the-sword-sdk" / "CvGameCoreDLL"

IMPROVEMENTS = XML / "Terrain" / "CIV4ImprovementInfos.xml"
SCHEMA = XML / "Terrain" / "CIV4TerrainSchema.xml"
ART = XML / "Art" / "CIV4ArtDefines_Improvement.xml"
PLOT_LSYSTEM = XML / "Buildings" / "CIV4PlotLSystem.xml"
GAME_OPTIONS = XML / "GameInfo" / "CIV4GameOptionInfos.xml"
BUILDS = XML / "Units" / "CIV4BuildInfos.xml"
TEXT = XML / "Text" / "ZZZ_CIV4GameText_NeutralWorldWonders.xml"

WONDERS = [
    "GREAT_SPHINX",
    "LIBRARY_OF_NINEVEH",
    "TERRACOTTA_ARMY",
    "TOMB_OF_CYRUS",
    "PERGAMON_ALTAR",
    "SUN_TZU_ART_OF_WAR",
]
IMPROVEMENT_TYPES = [f"IMPROVEMENT_NEUTRAL_{name}" for name in WONDERS]
ART_TYPES = [f"ART_DEF_IMPROVEMENT_NEUTRAL_{name}" for name in WONDERS]
ROTATION_ANGLES = {"0", "45", "90", "135", "180", "225", "270", "315"}
MODIFIER_TAGS = [
    "iNeutralWorldWonderCulturePercent",
    "iNeutralWorldWonderResearchPercent",
    "iNeutralWorldWonderGreatPeopleRatePercent",
    "iNeutralWorldWonderMilitaryProductionPercent",
    "iNeutralWorldWonderCivicUpkeepPercent",
    "iNeutralWorldWonderLandUnitExperience",
]

EXPECTED_DATA = {
    "GREAT_SPHINX": ([0, 0, 2], [10, 0, 0, 0, 0, 0]),
    "LIBRARY_OF_NINEVEH": ([0, 0, 2], [0, 10, 0, 0, 0, 0]),
    "TERRACOTTA_ARMY": ([0, 2, 0], [0, 0, 0, 0, 0, 1]),
    "TOMB_OF_CYRUS": ([0, 1, 1], [0, 0, 0, 0, -10, 0]),
    "PERGAMON_ALTAR": ([0, 0, 2], [0, 0, 10, 0, 0, 0]),
    "SUN_TZU_ART_OF_WAR": ([0, 2, 0], [0, 0, 0, 10, 0, 0]),
}


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def children(node, name):
    return [item for item in node if local_name(item.tag) == name]


def child(node, name):
    matches = children(node, name)
    return matches[0] if matches else None


def child_text(node, name, default=None):
    item = child(node, name)
    if item is None:
        return default
    return (item.text or "").strip()


def entries(path, entry_name):
    root = ET.parse(path).getroot()
    return [node for node in root.iter() if local_name(node.tag) == entry_name]


def find_entry(path, entry_name, type_name):
    for node in entries(path, entry_name):
        if child_text(node, "Type") == type_name:
            return node
    return None


def read_dll(*names):
    return "\n".join(
        (DLL / name).read_text(encoding="utf-8", errors="ignore") for name in names
    )


class NeutralWorldWonderDataTests(unittest.TestCase):
    def test_game_option_is_appended_visible_and_default_on(self):
        options = entries(GAME_OPTIONS, "GameOptionInfo")
        self.assertEqual(child_text(options[-1], "Type"), "GAMEOPTION_NEUTRAL_WORLD_WONDERS")
        self.assertEqual(child_text(options[-1], "bDefault"), "1")
        self.assertEqual(child_text(options[-1], "bVisible"), "1")

        enums = (DLL / "CvEnums.h").read_text(encoding="utf-8")
        enum_body = enums.split("enum GameOptionTypes", 1)[1].split("};", 1)[0]
        self.assertLess(
            enum_body.index("GAMEOPTION_NO_ESPIONAGE"),
            enum_body.index("GAMEOPTION_NEUTRAL_WORLD_WONDERS"),
        )
        self.assertIn(
            ".value(\"GAMEOPTION_NEUTRAL_WORLD_WONDERS\", GAMEOPTION_NEUTRAL_WORLD_WONDERS)",
            (DLL / "CyEnumsInterface.cpp").read_text(encoding="utf-8"),
        )

    def test_improvements_are_final_append_only_entries(self):
        order = [
            child_text(node, "Type")
            for node in entries(IMPROVEMENTS, "ImprovementInfo")
        ]
        self.assertEqual(order[-6:], IMPROVEMENT_TYPES)

    def test_exact_yields_modifiers_and_permanence(self):
        build_text = BUILDS.read_text(encoding="utf-8")
        for name, improvement_type in zip(WONDERS, IMPROVEMENT_TYPES):
            info = find_entry(IMPROVEMENTS, "ImprovementInfo", improvement_type)
            self.assertIsNotNone(info, improvement_type)
            self.assertEqual(child_text(info, "bNeutralWorldWonder"), "1")
            self.assertEqual(child_text(info, "bPermanent"), "1")
            self.assertEqual(child_text(info, "bUseLSystem"), "1")
            self.assertEqual(child_text(info, "bWater"), "0")
            self.assertEqual(child_text(info, "bGoody"), "0")
            self.assertEqual(child_text(info, "iPillageGold"), "0")
            self.assertEqual(
                child_text(info, "ArtDefineTag"),
                f"ART_DEF_IMPROVEMENT_NEUTRAL_{name}",
            )
            yields = [
                int((node.text or "0").strip())
                for node in child(info, "YieldChanges")
            ]
            modifiers = [int(child_text(info, tag, "0")) for tag in MODIFIER_TAGS]
            self.assertEqual((yields, modifiers), EXPECTED_DATA[name])
            self.assertNotIn(f"BUILD_NEUTRAL_{name}", build_text)

    def test_schema_and_cache_are_symmetric(self):
        schema = SCHEMA.read_text(encoding="utf-8")
        infos_h = (DLL / "CvInfos.h").read_text(encoding="utf-8")
        infos_cpp = (DLL / "CvInfos.cpp").read_text(encoding="utf-8")
        for tag in ["bNeutralWorldWonder", *MODIFIER_TAGS]:
            self.assertIn(f'ElementType name="{tag}"', schema)
            self.assertIn(f'<element type="{tag}" minOccurs="0"/>', schema)
            self.assertIn(tag, infos_h)
            self.assertIn(f'"{tag}"', infos_cpp)
        for member in [
            "m_bNeutralWorldWonder",
            "m_iNeutralWorldWonderCulturePercent",
            "m_iNeutralWorldWonderResearchPercent",
            "m_iNeutralWorldWonderGreatPeopleRatePercent",
            "m_iNeutralWorldWonderMilitaryProductionPercent",
            "m_iNeutralWorldWonderCivicUpkeepPercent",
            "m_iNeutralWorldWonderLandUnitExperience",
        ]:
            self.assertIn(f"stream->Read(&{member})", infos_cpp)
            self.assertIn(f"stream->Write({member})", infos_cpp)

    def test_art_records_resolve_to_existing_assets(self):
        for art_type in ART_TYPES:
            art = find_entry(ART, "ImprovementArtInfo", art_type)
            self.assertIsNotNone(art, art_type)
            self.assertEqual(child_text(art, "fInterfaceScale"), "1.0")
            self.assertGreater(float(child_text(art, "fScale")), 0.0)
            for tag in ("NIF", "Button"):
                relative = child_text(art, tag)
                self.assertTrue(relative)
                self.assertTrue((ASSETS / Path(relative)).is_file(), relative)

    def test_text_defines_all_names_help_and_pedia(self):
        tags = {
            child_text(node, "Tag")
            for node in entries(TEXT, "TEXT")
        }
        for improvement_type in IMPROVEMENT_TYPES:
            key = f"TXT_KEY_{improvement_type}"
            self.assertIn(key, tags)
            self.assertIn(f"{key}_HELP", tags)
            self.assertIn(f"{key}_PEDIA", tags)


class NeutralWorldWonderRotationTests(unittest.TestCase):
    def test_exclusive_route_contains_exact_wonder_set(self):
        routes = []
        for production in entries(PLOT_LSYSTEM, "LProduction"):
            if production.attrib.get("Name", "").startswith(
                "DowagerNeutralWonderRotationRoute"
            ):
                routes.append(production)
        self.assertGreaterEqual(len(routes), 1)
        routed = set()
        for route in routes:
            improvement_attribute = next(
                node
                for node in children(route, "Attribute")
                if node.attrib.get("Class") == "Improvement"
            )
            selector = (improvement_attribute.text or "").strip()
            self.assertLessEqual(len(selector), 182)
            routed.update(selector.split(","))
            self.assertEqual(
                child(route, "To").attrib.get("Name"),
                "Node_Dowager_NeutralWonderRotation_4x4",
            )
        self.assertEqual(routed, set(IMPROVEMENT_TYPES))

    def test_exact_eight_angle_rotation_and_one_model_per_wonder(self):
        angles = set()
        for production in entries(PLOT_LSYSTEM, "LProduction"):
            if production.attrib.get("Name", "").startswith("DowagerNeutralWonderRotate"):
                to_node = child(production, "To")
                angles.add(child_text(to_node, "Rotate"))
        self.assertEqual(angles, ROTATION_ANGLES)

        leaf = next(
            node
            for node in entries(PLOT_LSYSTEM, "LNode")
            if node.attrib.get("Name") == "Leaf_Dowager_NeutralWonderRotation_4x4"
        )
        refs = children(leaf, "ArtRef")
        self.assertEqual(len(refs), 6)
        ref_improvements = []
        for ref in refs:
            attributes = children(ref, "Attribute")
            improvement = next(
                node for node in attributes if node.attrib.get("Class") == "Improvement"
            )
            ref_improvements.append((improvement.text or "").strip())
            scalar_values = {
                (node.text or "").strip()
                for node in attributes
                if node.attrib.get("Class") == "Scalar"
            }
            self.assertIn("bIsPartOfImprovement:1", scalar_values)
            self.assertIn("bApplyRotation:1", scalar_values)
        self.assertEqual(set(ref_improvements), set(IMPROVEMENT_TYPES))


class NeutralWorldWonderNativeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.game = (DLL / "CvGame.cpp").read_text(encoding="utf-8", errors="ignore")
        cls.player = (DLL / "CvPlayer.cpp").read_text(
            encoding="utf-8", errors="ignore"
        )
        cls.city = (DLL / "CvCity.cpp").read_text(encoding="utf-8", errors="ignore")
        cls.plot = (DLL / "CvPlot.cpp").read_text(encoding="utf-8", errors="ignore")
        cls.ai = (DLL / "CvPlayerAI.cpp").read_text(
            encoding="utf-8", errors="ignore"
        )
        cls.help = (DLL / "CvGameTextMgr.cpp").read_text(
            encoding="utf-8", errors="ignore"
        )
        cls.init_core = (DLL / "CvInitCore.cpp").read_text(
            encoding="utf-8", errors="ignore"
        )

    def test_spawn_hook_order_and_multiplayer_default(self):
        initial = self.game.split("void CvGame::setInitialItems()", 1)[1].split(
            "void CvGame::placeNeutralWorldWonders()", 1
        )[0]
        calls = [
            initial.index("normalizeStartingPlots();"),
            initial.index("placeNeutralWorldWonders();"),
            initial.index("initFreeUnits();"),
            initial.index("AI_updateFoundValues();"),
        ]
        self.assertEqual(calls, sorted(calls))

        lobby = self.init_core.split(
            "void applyDefaultMultiplayerLobbySettings(CvInitCore& kInitCore)", 1
        )[1].split("\n}", 1)[0]
        self.assertIn(
            "kInitCore.setOption(GAMEOPTION_NEUTRAL_WORLD_WONDERS, true)", lobby
        )

    def test_disabled_and_scenario_gates_precede_rng(self):
        spawn = self.game.split("void CvGame::placeNeutralWorldWonders()", 1)[1].split(
            "\n}", 1
        )[0]
        rng_pos = spawn.index("getMapRandNum(")
        self.assertLess(spawn.index("getWBMapScript()"), rng_pos)
        self.assertLess(spawn.index("!isOption(eNeutralWorldWondersOption)"), rng_pos)

    def test_world_size_counts_stable_iteration_and_tie_break(self):
        for world_size, expected in {
            "WORLDSIZE_DUEL": 3,
            "WORLDSIZE_TINY": 4,
            "WORLDSIZE_SMALL": 5,
            "WORLDSIZE_STANDARD": 6,
            "WORLDSIZE_LARGE": 6,
            "WORLDSIZE_HUGE": 6,
        }.items():
            if expected < 6:
                self.assertRegex(
                    self.game,
                    rf"case {world_size}:\s*return {expected};",
                )
            else:
                self.assertIn(f"case {world_size}:", self.game)
        self.assertIn(
            "for (int iPlotIndex = 0; iPlotIndex < kMap.numPlotsINLINE(); ++iPlotIndex)",
            self.game,
        )
        self.assertIn(
            "iTotalScore == kBestCandidate.iTotalScore && iPlotIndex < kBestCandidate.iPlotIndex",
            self.game,
        )
        self.assertEqual(
            self.game.count('getMapRandNum(NEUTRAL_WORLD_WONDER_COUNT - iI'),
            1,
        )

    def test_hard_filters_spacing_and_reconciliation_logging(self):
        for contract in [
            "pPlot->isOwned()",
            "pPlot->isWater()",
            "pPlot->isPeak()",
            "pPlot->isCity()",
            "pPlot->getFeatureType()",
            "pPlot->getImprovementType()",
            "pPlot->getBonusType()",
            "pPlot->isGoody()",
            "pArea->getNumTiles() < 20",
            "iDistance < 6",
            "iDistance < 8",
        ]:
            self.assertIn(contract, self.game)
        for field in [
            "expected=%d",
            "attempted=%d",
            "spawned=%d",
            "skipped=%d",
            "duplicate=%d",
            "error=%d",
            "candidate_count=%d",
            "contributors=settlement:%d,area:%d,start:%d,theme:%d",
        ]:
            self.assertIn(field, self.game)

    def test_effects_are_unique_owned_count_derived_and_save_safe(self):
        helper = self.player.split(
            "int getOwnedNeutralWorldWonderEffectSum", 1
        )[1].split("\n\t}", 1)[0]
        self.assertIn("kPlayer.getImprovementCount(eImprovement) <= 0", helper)
        self.assertIn("kImprovement.isNeutralWorldWonder()", helper)
        self.assertIn("(kImprovement.*pGetter)()", helper)
        self.assertIn("bHadWonder == bHasWonder", self.player)
        self.assertIn("changeImprovementCount(getImprovementType(), -1)", self.plot)
        self.assertIn("changeImprovementCount(getImprovementType(), 1)", self.plot)

        for getter in [
            "getNeutralWorldWonderCulturePercent()",
            "getNeutralWorldWonderResearchPercent()",
            "getNeutralWorldWonderGreatPeopleRatePercent()",
            "getNeutralWorldWonderMilitaryProductionPercent()",
            "getNeutralWorldWonderCivicUpkeepPercent()",
        ]:
            self.assertIn(getter, self.player)
        self.assertIn("getNeutralWorldWonderLandUnitExperience()", self.city)
        self.assertIn("getDomainType() == DOMAIN_LAND", self.city)
        self.assertNotRegex(
            read_dll("CvPlayer.h", "CvCity.h", "CvGame.h"),
            r"m_iNeutralWorldWonder|m_bNeutralWorldWonder",
        )

    def test_help_notifications_and_bounded_ai_value_are_wired(self):
        self.assertIn("buildNeutralWorldWonderEffectString", self.help)
        self.assertIn("appendNeutralWorldWonderHelp", self.help)
        self.assertIn("appendNeutralWorldWonderPlotStatus", self.help)
        self.assertIn("TXT_KEY_NEUTRAL_WORLD_WONDER_PLOT_INACTIVE", self.help)
        self.assertIn("TXT_KEY_NEUTRAL_WORLD_WONDER_PLOT_ACTIVE", self.help)
        self.assertIn("TXT_KEY_NEUTRAL_WORLD_WONDER_MESSAGE_CLAIM", self.plot)
        self.assertIn("TXT_KEY_NEUTRAL_WORLD_WONDER_MESSAGE_LOSS", self.plot)
        self.assertIn(
            "TXT_KEY_NEUTRAL_WORLD_WONDER_MESSAGE_TRANSFER_GAIN", self.plot
        )
        self.assertIn(
            "TXT_KEY_NEUTRAL_WORLD_WONDER_MESSAGE_TRANSFER_LOSS", self.plot
        )
        self.assertIn("getNeutralWorldWonderFoundValueBonus", self.ai)
        self.assertIn("aiNeutralWorldWonderPlots", self.ai)
        self.assertIn("aiNeutralWorldWonderTypes", self.ai)
        self.assertIn("getImprovementCount(eExistingImprovement) == 0", self.ai)
        self.assertIn("bIncludeEmpireEffect", self.ai)
        self.assertRegex(
            self.ai,
            r"getNeutralWorldWonderFoundValueBonus[\s\S]+std::min\(",
        )
        self.assertIn(
            "GC.getImprovementInfo(pPlot->getImprovementType()).isNeutralWorldWonder()",
            self.player,
        )


if __name__ == "__main__":
    unittest.main()
