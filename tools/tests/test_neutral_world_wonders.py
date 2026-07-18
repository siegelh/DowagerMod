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
    "ISHTAR_GATE",
    "GREAT_ZIGGURAT_OF_UR",
    "EKUR_OF_NIPPUR",
    "TEMPLE_OF_THOTH",
    "TEMPLE_OF_MELQART",
    "ERECHTHEUM",
    "LABYRINTH_OF_KNOSSOS",
    "SOLOMONS_TEMPLE",
]
NEUTRAL_WORLD_WONDER_COUNT = len(WONDERS)
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
    "ISHTAR_GATE": ([0, 0, 2], [10, 0, 0, 0, 0, 0]),
    "GREAT_ZIGGURAT_OF_UR": ([0, 1, 1], [0, 0, 0, 0, -10, 0]),
    "EKUR_OF_NIPPUR": ([0, 2, 0], [0, 0, 0, 10, 0, 0]),
    "TEMPLE_OF_THOTH": ([0, 0, 2], [0, 10, 0, 0, 0, 0]),
    "TEMPLE_OF_MELQART": ([0, 2, 0], [0, 0, 0, 0, 0, 1]),
    "ERECHTHEUM": ([0, 0, 2], [0, 0, 10, 0, 0, 0]),
    "LABYRINTH_OF_KNOSSOS": ([0, 1, 1], [0, 0, 0, 0, -10, 0]),
    "SOLOMONS_TEMPLE": ([0, 0, 2], [0, 0, 10, 0, 0, 0]),
}

# Original six wonders' XML profile is unconstrained by the new set (flat Desert only,
# no explicit riverside requirement recorded on the type itself for GREAT_SPHINX etc.);
# the following table only records the append-only wonders' XML hard-filter flags that
# the new spawn-engine profile cases (6-13) must mirror.
APPENDED_PROFILE_FLAGS = {
    "ISHTAR_GATE": {"bRequiresFlatlands": "1", "bRequiresRiverSide": "1"},
    "GREAT_ZIGGURAT_OF_UR": {"bRequiresFlatlands": "1", "bRequiresRiverSide": "1"},
    "EKUR_OF_NIPPUR": {"bRequiresFlatlands": "1", "bRequiresRiverSide": "0"},
    "TEMPLE_OF_THOTH": {"bRequiresFlatlands": "1", "bRequiresRiverSide": "1"},
    "TEMPLE_OF_MELQART": {"bRequiresFlatlands": "1", "bRequiresRiverSide": "0"},
    "ERECHTHEUM": {"bHillsMakesValid": "1", "bRequiresFlatlands": "0"},
    "LABYRINTH_OF_KNOSSOS": {"bHillsMakesValid": "1", "bRequiresFlatlands": "0"},
    "SOLOMONS_TEMPLE": {"bHillsMakesValid": "1", "bRequiresFlatlands": "0"},
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
        self.assertEqual(order[-NEUTRAL_WORLD_WONDER_COUNT:], IMPROVEMENT_TYPES)

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
            for flag_tag, expected_value in APPENDED_PROFILE_FLAGS.get(name, {}).items():
                self.assertEqual(child_text(info, flag_tag), expected_value, (name, flag_tag))

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

    def test_game_option_help_describes_random_subset_of_fourteen(self):
        node = next(
            item
            for item in entries(TEXT, "TEXT")
            if child_text(item, "Tag") == "TXT_KEY_GAME_OPTION_NEUTRAL_WORLD_WONDERS_HELP"
        )
        english = child_text(node, "English")
        self.assertIn("fourteen", english.lower())
        self.assertIn("random", english.lower())
        for language in ("French", "German", "Italian", "Spanish"):
            self.assertEqual(child_text(node, language), english)

    def test_named_source_text_keys_exist_with_english_fallback_in_all_languages(self):
        tags = {child_text(node, "Tag"): node for node in entries(TEXT, "TEXT")}
        for key in (
            "TXT_KEY_NEUTRAL_WORLD_WONDER_HELP_COMMERCE_SOURCE",
            "TXT_KEY_NEUTRAL_WORLD_WONDER_HELP_GREAT_PEOPLE_SOURCE",
            "TXT_KEY_NEUTRAL_WORLD_WONDER_HELP_MILITARY_PRODUCTION_SOURCE",
            "TXT_KEY_NEUTRAL_WORLD_WONDER_HELP_LAND_XP_SOURCE",
            "TXT_KEY_NEUTRAL_WORLD_WONDER_HELP_CIVIC_UPKEEP_SOURCE",
        ):
            self.assertIn(key, tags, key)
            node = tags[key]
            english = child_text(node, "English")
            self.assertTrue(english)
            for language in ("French", "German", "Italian", "Spanish"):
                self.assertEqual(child_text(node, language), english, key)


class NeutralWorldWonderRotationTests(unittest.TestCase):
    def test_exclusive_route_contains_exact_wonder_set(self):
        routes = []
        for production in entries(PLOT_LSYSTEM, "LProduction"):
            if production.attrib.get("Name", "").startswith(
                "DowagerNeutralWonderRotationRoute"
            ):
                routes.append(production)
        self.assertEqual(len(routes), 4)
        routed = set()
        for route in routes:
            improvement_attribute = next(
                node
                for node in children(route, "Attribute")
                if node.attrib.get("Class") == "Improvement"
            )
            selector = (improvement_attribute.text or "").strip()
            self.assertLessEqual(len(selector), 182)
            selector_types = selector.split(",")
            self.assertFalse(routed.intersection(selector_types), route.attrib.get("Name"))
            routed.update(selector_types)
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
        self.assertEqual(len(refs), NEUTRAL_WORLD_WONDER_COUNT)
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

    def test_wonder_pool_is_fourteen_with_unconditional_full_shuffle(self):
        # Fisher-Yates has exactly one call site (asserted above) but, because the
        # loop bound is NEUTRAL_WORLD_WONDER_COUNT - 1 == 13 and the below-standard
        # gate has been removed, it now performs 13 runtime swap iterations on
        # every generated map regardless of world size.
        self.assertIn("NEUTRAL_WORLD_WONDER_COUNT = 14", self.game)
        self.assertNotIn("isBelowStandardWorldSize", self.game)

        definitions_block = self.game.split(
            "g_aNeutralWorldWonderDefinitions[NEUTRAL_WORLD_WONDER_COUNT] =", 1
        )[1].split("};", 1)[0]
        found_order = re.findall(r'"(IMPROVEMENT_NEUTRAL_[A-Z_]+)"', definitions_block)
        self.assertEqual(found_order[0::2], IMPROVEMENT_TYPES)
        self.assertEqual(found_order[1::2], IMPROVEMENT_TYPES)

        spawn = self.game.split("void CvGame::placeNeutralWorldWonders()", 1)[1].split(
            "\n}", 1
        )[0]
        self.assertIn(
            "for (int iI = 0; iI < NEUTRAL_WORLD_WONDER_COUNT - 1; ++iI)",
            spawn,
        )
        # The shuffle loop must not be nested inside any world-size conditional:
        # the initialization loop assigning aiWonderOrder[iI] = iI must be the last
        # thing before the shuffle loop begins, with no intervening "if" gate.
        between = spawn.split("aiWonderOrder[iI] = iI;", 1)[1].split(
            "for (int iI = 0; iI < NEUTRAL_WORLD_WONDER_COUNT - 1; ++iI)", 1
        )[0]
        self.assertNotIn("if (", between)

    def test_profile_and_theme_hooks_cover_indices_six_through_thirteen(self):
        profile_block = self.game.split(
            "bool matchesNeutralWorldWonderProfile(", 1
        )[1].split("int getNeutralWorldWonderSettlementScore(", 1)[0]
        for index in range(6, 14):
            self.assertIn(f"case {index}:", profile_block, index)

        theme_block = self.game.split(
            "int getNeutralWorldWonderThemeScore(", 1
        )[1].split("// Public Functions", 1)[0]
        for index in range(6, 14):
            self.assertIn(f"case {index}:", theme_block, index)

        for snippet in (
            "iWonderIndex == 8 && !pPlot->isCoastalLand()",
            "iWonderIndex == 10 && pPlot->isCoastalLand()",
            "iWonderIndex == 11 && pPlot->isHills()",
            "iWonderIndex == 12 && pPlot->isCoastalLand()",
            "iWonderIndex == 13 && !pPlot->isCoastalLand()",
        ):
            self.assertIn(snippet, theme_block, snippet)

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

    def test_named_source_ui_helper_exists_and_is_read_only(self):
        helper = self.help.split(
            "int appendActiveNeutralWorldWonderLines(", 1
        )[1].split("\n\t}\n", 1)[0]
        self.assertIn("kImprovement.isNeutralWorldWonder()", helper)
        self.assertIn("kPlayer.getImprovementCount(eImprovement) <= 0", helper)
        self.assertIn("(kImprovement.*pGetter)()", helper)
        self.assertIn("return iAggregate", helper)
        # Pure read-only enumeration: no map scan, no persisted state, no RNG.
        self.assertNotIn("getMapRandNum", helper)
        self.assertNotIn("GC.getMapINLINE()", helper)

    def test_named_source_lines_wired_into_commerce_gpp_military_xp_upkeep(self):
        for call in (
            'appendActiveNeutralWorldWonderLines(szBuffer, owner, &CvImprovementInfo::getNeutralWorldWonderCulturePercent, "TXT_KEY_NEUTRAL_WORLD_WONDER_HELP_COMMERCE_SOURCE")',
            'appendActiveNeutralWorldWonderLines(szBuffer, owner, &CvImprovementInfo::getNeutralWorldWonderResearchPercent, "TXT_KEY_NEUTRAL_WORLD_WONDER_HELP_COMMERCE_SOURCE")',
            'appendActiveNeutralWorldWonderLines(szBuffer, owner, &CvImprovementInfo::getNeutralWorldWonderGreatPeopleRatePercent, "TXT_KEY_NEUTRAL_WORLD_WONDER_HELP_GREAT_PEOPLE_SOURCE")',
            'appendActiveNeutralWorldWonderLines(szBuffer, kCityOwner, &CvImprovementInfo::getNeutralWorldWonderMilitaryProductionPercent, "TXT_KEY_NEUTRAL_WORLD_WONDER_HELP_MILITARY_PRODUCTION_SOURCE")',
            'appendActiveNeutralWorldWonderLines(szBuffer, GET_PLAYER(pCity->getOwnerINLINE()), &CvImprovementInfo::getNeutralWorldWonderLandUnitExperience, "TXT_KEY_NEUTRAL_WORLD_WONDER_HELP_LAND_XP_SOURCE")',
            'appendActiveNeutralWorldWonderLines(szBuffer, player, &CvImprovementInfo::getNeutralWorldWonderCivicUpkeepPercent, "TXT_KEY_NEUTRAL_WORLD_WONDER_HELP_CIVIC_UPKEEP_SOURCE")',
        ):
            self.assertIn(call, self.help, call)

    def test_commerce_and_great_people_aggregate_includes_named_source_sum(self):
        commerce_block = self.help.split(
            "void CvGameTextMgr::setCommerceHelp(", 1
        )[1].split("\nvoid CvGameTextMgr::", 1)[0]
        self.assertIn(
            "iModifier += appendActiveNeutralWorldWonderLines(szBuffer, owner, &CvImprovementInfo::getNeutralWorldWonderCulturePercent",
            commerce_block,
        )
        self.assertIn(
            "iModifier += appendActiveNeutralWorldWonderLines(szBuffer, owner, &CvImprovementInfo::getNeutralWorldWonderResearchPercent",
            commerce_block,
        )

        gpp_block = self.help.split(
            "void CvGameTextMgr::parseGreatPeopleHelp(", 1
        )[1].split("\nvoid CvGameTextMgr::", 1)[0]
        self.assertIn(
            "iModifier += appendActiveNeutralWorldWonderLines(szBuffer, owner, &CvImprovementInfo::getNeutralWorldWonderGreatPeopleRatePercent",
            gpp_block,
        )
        self.assertIn(
            "FAssertMsg(iModGreatPeople == city.getGreatPeopleRate()", gpp_block
        )

    def test_military_production_help_splits_base_from_named_wonder_lines(self):
        production_block = self.help.split(
            "void CvGameTextMgr::setProductionHelp(", 1
        )[1].split("\nvoid CvGameTextMgr::", 1)[0]
        self.assertIn(
            "const int iNeutralWorldWonderMilitaryMod = kCityOwner.getNeutralWorldWonderMilitaryProductionPercent();",
            production_block,
        )
        self.assertIn(
            "const int iBaseMilitaryMod = iMilitaryMod - iNeutralWorldWonderMilitaryMod;",
            production_block,
        )
        self.assertIn(
            'appendActiveNeutralWorldWonderLines(szBuffer, kCityOwner, &CvImprovementInfo::getNeutralWorldWonderMilitaryProductionPercent, "TXT_KEY_NEUTRAL_WORLD_WONDER_HELP_MILITARY_PRODUCTION_SOURCE")',
            production_block,
        )
        # Full iMilitaryMod (including the wonder contribution, once) still feeds the real
        # total -- only the *displayed* base line above excludes the wonder contribution.
        self.assertIn("iBaseModifier += iMilitaryMod;", production_block)

    def test_unit_help_shows_xp_lines_only_for_land_combat_units_with_city(self):
        for condition in (
            "pCity != NULL && !bCivilopediaText &&",
            "(DomainTypes)GC.getUnitInfo(eUnit).getDomainType() == DOMAIN_LAND &&",
            "GC.getUnitInfo(eUnit).getCombat() > 0",
        ):
            self.assertIn(condition, self.help, condition)
        self.assertIn(
            'appendActiveNeutralWorldWonderLines(szBuffer, GET_PLAYER(pCity->getOwnerINLINE()), &CvImprovementInfo::getNeutralWorldWonderLandUnitExperience, "TXT_KEY_NEUTRAL_WORLD_WONDER_HELP_LAND_XP_SOURCE")',
            self.help,
        )

    def test_civic_upkeep_help_uses_signed_raw_percent_no_abs(self):
        upkeep_block = self.help.split(
            "void CvGameTextMgr::buildFinanceCivicUpkeepString(", 1
        )[1].split("\nvoid CvGameTextMgr::", 1)[0]
        self.assertIn(
            'appendActiveNeutralWorldWonderLines(szBuffer, player, &CvImprovementInfo::getNeutralWorldWonderCivicUpkeepPercent, "TXT_KEY_NEUTRAL_WORLD_WONDER_HELP_CIVIC_UPKEEP_SOURCE")',
            upkeep_block,
        )
        self.assertNotIn("abs(", upkeep_block)

    def test_active_source_lines_stack_distinct_wonders_but_not_duplicate_copies(self):
        helper = self.help.split(
            "int appendActiveNeutralWorldWonderLines(", 1
        )[1].split("\n\t}\n", 1)[0]
        # One iteration per distinct ImprovementInfo, guarded by ownership count, so
        # duplicate copies of the SAME wonder type collapse to a single aggregated line
        # while each DISTINCT active wonder type still gets its own separate line.
        self.assertIn(
            "for (int iImprovement = 0; iImprovement < GC.getNumImprovementInfos(); ++iImprovement)",
            helper,
        )
        self.assertIn("if (kPlayer.getImprovementCount(eImprovement) <= 0)", helper)


if __name__ == "__main__":
    unittest.main()
