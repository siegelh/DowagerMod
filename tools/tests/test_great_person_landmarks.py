from __future__ import annotations

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
IMPROVEMENTS = XML / "Terrain" / "CIV4ImprovementInfos.xml"
SCHEMA = XML / "Terrain" / "CIV4TerrainSchema.xml"
BUILDS = XML / "Units" / "CIV4BuildInfos.xml"
UNITS = XML / "Units" / "CIV4UnitInfos.xml"
ART = XML / "Art" / "CIV4ArtDefines_Improvement.xml"
TEXT = XML / "Text" / "ZZZ_CIV4GameText_Landmarks.xml"

DLL = ROOT / "third_party" / "beyond-the-sword-sdk" / "CvGameCoreDLL"


# Plan append order (2026-07-13-great-person-landmark-improvements.md).
LANDMARK_ORDER = [
    "INDUSTRIAL_ZONE_BTG",
    "NAVAL_FOUNDRY_BTG",
    "RESEARCH_CAMPUS_BTG",
    "COMMERCIAL_DISTRICT_BTG",
    "GRAND_BAZAAR_BTG",
    "SACRED_GROVE_NONE_BTG",
    "SACRED_GROVE_JUDAISM_BTG",
    "SACRED_GROVE_CHRISTIANITY_BTG",
    "SACRED_GROVE_ISLAM_BTG",
    "SACRED_GROVE_HINDUISM_BTG",
    "SACRED_GROVE_BUDDHISM_BTG",
    "SACRED_GROVE_CONFUCIANISM_BTG",
    "SACRED_GROVE_TAOISM_BTG",
]

# key -> (ltype, group, mindist, cityadj, noadj, coastal, relgated, religion)
LANDMARK_FIELDS = {
    "INDUSTRIAL_ZONE_BTG": ("1", "0", "4", "0", "0", "0", "0", None),
    "NAVAL_FOUNDRY_BTG": ("2", "1", "4", "0", "0", "1", "0", None),
    "RESEARCH_CAMPUS_BTG": ("3", "2", "4", "0", "0", "0", "0", None),
    "COMMERCIAL_DISTRICT_BTG": ("4", "3", "0", "1", "1", "0", "0", None),
    "GRAND_BAZAAR_BTG": ("5", "4", "4", "0", "0", "0", "0", None),
    "SACRED_GROVE_NONE_BTG": ("6", "5", "4", "0", "0", "0", "1", None),
    "SACRED_GROVE_JUDAISM_BTG": ("6", "5", "4", "0", "0", "0", "1", "RELIGION_JUDAISM"),
    "SACRED_GROVE_CHRISTIANITY_BTG": ("6", "5", "4", "0", "0", "0", "1", "RELIGION_CHRISTIANITY"),
    "SACRED_GROVE_ISLAM_BTG": ("6", "5", "4", "0", "0", "0", "1", "RELIGION_ISLAM"),
    "SACRED_GROVE_HINDUISM_BTG": ("6", "5", "4", "0", "0", "0", "1", "RELIGION_HINDUISM"),
    "SACRED_GROVE_BUDDHISM_BTG": ("6", "5", "4", "0", "0", "0", "1", "RELIGION_BUDDHISM"),
    "SACRED_GROVE_CONFUCIANISM_BTG": ("6", "5", "4", "0", "0", "0", "1", "RELIGION_CONFUCIANISM"),
    "SACRED_GROVE_TAOISM_BTG": ("6", "5", "4", "0", "0", "0", "1", "RELIGION_TAOISM"),
}

LANDMARK_NIF = {
    "INDUSTRIAL_ZONE_BTG": "Art/Structures/Buildings/Factory/Factory.nif",
    "NAVAL_FOUNDRY_BTG": "Art/Structures/Buildings/IronWorks/IronWorks.nif",
    "RESEARCH_CAMPUS_BTG": "Art/Structures/Buildings/Observatory/Observatory.nif",
    "COMMERCIAL_DISTRICT_BTG": "Art/Structures/Buildings/Roman Forum/Forum.nif",
    "GRAND_BAZAAR_BTG": "Art/Structures/Buildings/Market/Market.nif",
    "SACRED_GROVE_NONE_BTG": "Art/BTG/ChooseReligions/Shinto_Files/Buildings/ShintoNaiku.nif",
    "SACRED_GROVE_JUDAISM_BTG": "Art/Structures/Buildings/Shrine/jewish-shrine.nif",
    "SACRED_GROVE_CHRISTIANITY_BTG": "Art/Structures/Buildings/Shrine/christian shrine.nif",
    "SACRED_GROVE_ISLAM_BTG": "Art/Structures/Buildings/Shrine/Islamic_shrine.nif",
    "SACRED_GROVE_HINDUISM_BTG": "Art/Structures/Buildings/Shrine/hindu_shrine.nif",
    "SACRED_GROVE_BUDDHISM_BTG": "Art/Structures/Buildings/Shrine/Buddhist_shrine.nif",
    "SACRED_GROVE_CONFUCIANISM_BTG": "Art/Structures/Buildings/Shrine/confuscian_shrine.nif",
    "SACRED_GROVE_TAOISM_BTG": "Art/Structures/Buildings/Shrine/Taoist_shrine.nif",
}

UNIT_BUILDS = {
    "UNIT_ENGINEER": {"BUILD_INDUSTRIAL_ZONE_BTG", "BUILD_NAVAL_FOUNDRY_BTG"},
    "UNIT_SCIENTIST": {"BUILD_RESEARCH_CAMPUS_BTG"},
    "UNIT_MERCHANT": {"BUILD_COMMERCIAL_DISTRICT_BTG", "BUILD_GRAND_BAZAAR_BTG"},
    "UNIT_PROPHET": {f"BUILD_{k}" for k in LANDMARK_ORDER if k.startswith("SACRED_GROVE")},
    "UNIT_VENETIAN_MERCHANT": {
        "BUILD_ROAD",
        "BUILD_GRAND_COLOSSEUM_BTG",
        "BUILD_COMMERCIAL_DISTRICT_BTG",
        "BUILD_GRAND_BAZAAR_BTG",
    },
}


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def find_child(node, name):
    for item in node:
        if local_name(item.tag) == name:
            return item
    return None


def child_text(node, name, default=None):
    item = find_child(node, name)
    if item is None:
        return default
    return (item.text or "").strip()


def entries(path, entry_name):
    root = ET.parse(path).getroot()
    return [n for n in root.iter() if local_name(n.tag) == entry_name]


def type_order(path, entry_name):
    return [child_text(n, "Type") for n in entries(path, entry_name)]


def find_entry(path, entry_name, type_name):
    for n in entries(path, entry_name):
        if child_text(n, "Type") == type_name:
            return n
    return None


def read_dll(*names):
    return "\n".join((DLL / name).read_text(encoding="utf-8", errors="ignore") for name in names)


class SchemaTests(unittest.TestCase):
    def test_schema_declares_landmark_elements(self):
        text = SCHEMA.read_text(encoding="utf-8")
        for tag in (
            "bLandmark", "iLandmarkType", "iLandmarkGroup", "iLandmarkMinDistance",
            "bLandmarkRequiresCityAdjacency", "bLandmarkNoAdjacentSameGroup",
            "bLandmarkRequiresCoastalLand", "bLandmarkStateReligionGated",
            "LandmarkStateReligion",
        ):
            self.assertIn(f'ElementType name="{tag}"', text, tag)
            self.assertIn(f'<element type="{tag}" minOccurs="0"/>', text, tag)


class DataOrderTests(unittest.TestCase):
    def test_landmarks_appended_at_end_in_plan_order(self):
        order = type_order(IMPROVEMENTS, "ImprovementInfo")
        expected = [f"IMPROVEMENT_{k}" for k in LANDMARK_ORDER]
        self.assertEqual(order[-13:], expected)

    def test_grand_colosseum_not_moved(self):
        order = type_order(IMPROVEMENTS, "ImprovementInfo")
        self.assertIn("IMPROVEMENT_GRAND_COLOSSEUM_BTG", order)
        # Grand Colosseum must stay before the appended landmarks.
        self.assertLess(
            order.index("IMPROVEMENT_GRAND_COLOSSEUM_BTG"),
            order.index("IMPROVEMENT_INDUSTRIAL_ZONE_BTG"),
        )

    def test_build_order_matches_improvement_order(self):
        order = type_order(BUILDS, "BuildInfo")
        expected = [f"BUILD_{k}" for k in LANDMARK_ORDER]
        self.assertEqual(order[-13:], expected)

    def test_builds_place_matching_improvement_and_are_instant_kill(self):
        for k in LANDMARK_ORDER:
            build = find_entry(BUILDS, "BuildInfo", f"BUILD_{k}")
            self.assertIsNotNone(build, k)
            self.assertEqual(child_text(build, "ImprovementType"), f"IMPROVEMENT_{k}")
            self.assertEqual(child_text(build, "bKill"), "1", k)
            self.assertEqual(child_text(build, "iTime"), "0", k)

    def test_improvement_landmark_fields(self):
        for k, fields in LANDMARK_FIELDS.items():
            imp = find_entry(IMPROVEMENTS, "ImprovementInfo", f"IMPROVEMENT_{k}")
            self.assertIsNotNone(imp, k)
            ltype, group, mindist, cityadj, noadj, coastal, relgated, religion = fields
            self.assertEqual(child_text(imp, "bLandmark"), "1", k)
            self.assertEqual(child_text(imp, "iLandmarkType"), ltype, k)
            self.assertEqual(child_text(imp, "iLandmarkGroup"), group, k)
            self.assertEqual(child_text(imp, "iLandmarkMinDistance"), mindist, k)
            self.assertEqual(child_text(imp, "bLandmarkRequiresCityAdjacency"), cityadj, k)
            self.assertEqual(child_text(imp, "bLandmarkNoAdjacentSameGroup"), noadj, k)
            self.assertEqual(child_text(imp, "bLandmarkRequiresCoastalLand"), coastal, k)
            self.assertEqual(child_text(imp, "bLandmarkStateReligionGated"), relgated, k)
            self.assertEqual(child_text(imp, "LandmarkStateReligion"), religion, k)

    def test_sacred_groves_share_one_logical_group(self):
        groups = set()
        for k in LANDMARK_ORDER:
            if k.startswith("SACRED_GROVE"):
                imp = find_entry(IMPROVEMENTS, "ImprovementInfo", f"IMPROVEMENT_{k}")
                groups.add(child_text(imp, "iLandmarkGroup"))
        self.assertEqual(groups, {"5"})

    def test_naval_foundry_has_base_production(self):
        imp = find_entry(IMPROVEMENTS, "ImprovementInfo", "IMPROVEMENT_NAVAL_FOUNDRY_BTG")
        yields = [n.text.strip() for n in find_child(imp, "YieldChanges")]
        self.assertEqual(yields, ["0", "2", "0"])


class ArtTests(unittest.TestCase):
    def test_art_define_per_landmark_with_expected_nif(self):
        for k, nif in LANDMARK_NIF.items():
            art = find_entry(ART, "ImprovementArtInfo", f"ART_DEF_IMPROVEMENT_{k}")
            self.assertIsNotNone(art, k)
            self.assertEqual(child_text(art, "NIF"), nif, k)

    def test_improvement_artdefinetag_resolves(self):
        art_types = set(type_order(ART, "ImprovementArtInfo"))
        for k in LANDMARK_ORDER:
            imp = find_entry(IMPROVEMENTS, "ImprovementInfo", f"IMPROVEMENT_{k}")
            self.assertIn(child_text(imp, "ArtDefineTag"), art_types, k)


class UnitPermissionTests(unittest.TestCase):
    def unit_builds(self, unit_type):
        unit = find_entry(UNITS, "UnitInfo", unit_type)
        self.assertIsNotNone(unit, unit_type)
        builds_node = find_child(unit, "Builds")
        return {child_text(b, "BuildType") for b in builds_node}

    def test_great_person_landmark_permissions(self):
        for unit, expected in UNIT_BUILDS.items():
            self.assertEqual(self.unit_builds(unit), expected, unit)

    def test_landmark_builders_match_instant_grand_colosseum_work_rate(self):
        artist = find_entry(UNITS, "UnitInfo", "UNIT_ARTIST")
        self.assertEqual(child_text(artist, "iWorkRate"), "1000")
        for unit_type in UNIT_BUILDS:
            unit = find_entry(UNITS, "UnitInfo", unit_type)
            self.assertEqual(
                child_text(unit, "iWorkRate"),
                "1000",
                f"{unit_type} needs positive Grand Colosseum-style work rate "
                "to finish its zero-time, unit-consuming landmark Build",
            )

    def test_venetian_preserves_original_actions(self):
        builds = self.unit_builds("UNIT_VENETIAN_MERCHANT")
        self.assertTrue({"BUILD_ROAD", "BUILD_GRAND_COLOSSEUM_BTG"} <= builds)


class TextTests(unittest.TestCase):
    def test_text_keys_present(self):
        text = TEXT.read_text(encoding="ISO-8859-1")
        for k in LANDMARK_ORDER:
            self.assertIn(f"TXT_KEY_IMPROVEMENT_{k}<", text, k)
            self.assertIn(f"TXT_KEY_IMPROVEMENT_{k}_PEDIA<", text, k)
            self.assertIn(f"TXT_KEY_BUILD_{k}<", text, k)
        for help_key in (
            "TXT_KEY_LANDMARK_INDUSTRIAL_ZONE_HELP",
            "TXT_KEY_LANDMARK_NAVAL_FOUNDRY_HELP",
            "TXT_KEY_LANDMARK_RESEARCH_CAMPUS_HELP",
            "TXT_KEY_LANDMARK_COMMERCIAL_DISTRICT_HELP",
            "TXT_KEY_LANDMARK_GRAND_BAZAAR_HELP",
            "TXT_KEY_LANDMARK_SACRED_GROVE_HELP",
            "TXT_KEY_LANDMARK_REQUIRES_CITY_ADJACENCY",
            "TXT_KEY_LANDMARK_REQUIRES_COASTAL_LAND",
            "TXT_KEY_LANDMARK_STATE_RELIGION",
            "TXT_KEY_LANDMARK_NO_STATE_RELIGION",
        ):
            self.assertIn(help_key, text, help_key)


class DllContractTests(unittest.TestCase):
    def assertContains(self, text, needle):
        self.assertTrue(needle in text, f"DLL source missing: {needle!r}")

    def test_improvement_info_fields_and_symmetric_cache(self):
        header = (DLL / "CvInfos.h").read_text(encoding="utf-8", errors="ignore")
        self.assertContains(header, "bool isLandmark() const")
        self.assertContains(header, "enum LandmarkTypes")
        self.assertContains(header, "LANDMARK_RESEARCH_CAMPUS")

        cpp = (DLL / "CvInfos.cpp").read_text(encoding="utf-8", errors="ignore")
        # Cache read/write must both touch the new fields (symmetry).
        self.assertContains(cpp, "stream->Read(&m_bLandmark)")
        self.assertContains(cpp, "stream->Write(m_bLandmark)")
        self.assertContains(cpp, "stream->Read(&m_iLandmarkStateReligion)")
        self.assertContains(cpp, "stream->Write(m_iLandmarkStateReligion)")
        # Version-guarded read for freshly generated caches.
        self.assertContains(cpp, "if (uiFlag >= 1)")

    def test_central_placement_legality(self):
        plot = read_dll("CvPlot.cpp")
        self.assertContains(plot, "bool CvPlot::canBuildLandmark(")
        self.assertContains(plot, "canBuildLandmark(eImprovement, ePlayer, bTestVisible)")
        # Resource preservation, coastal, city adjacency, spacing.
        self.assertContains(plot, "getBonusType(eTeam) != NO_BONUS")
        self.assertContains(plot, "isLandmarkRequiresCoastalLand()")
        self.assertContains(plot, "isLandmarkRequiresCityAdjacency()")
        self.assertContains(plot, "getStateReligion()")

    def test_source_adjacency_and_water_aura(self):
        plot = read_dll("CvPlot.cpp")
        self.assertContains(plot, "getLandmarkAdjacencyYield(eImprovement, eYield, ePlayer)")
        self.assertContains(plot, "getLandmarkWaterAuraYield(eYield, ePlayer)")
        # Non-stacking aura: single boolean presence, not summed per foundry.
        self.assertContains(plot, "bool bInAura = false")

    def test_research_campus_before_modifiers(self):
        city = read_dll("CvCity.cpp")
        self.assertContains(city, "getLandmarkResearchCampusValue(getOwnerINLINE())")
        self.assertContains(city, "LANDMARK_RESEARCH_CAMPUS")

    def test_generated_help(self):
        text_mgr = read_dll("CvGameTextMgr.cpp")
        self.assertContains(text_mgr, "appendLandmarkHelp")
        self.assertContains(text_mgr, "TXT_KEY_LANDMARK_SACRED_GROVE_HELP")

    def test_ai_planner_and_integration(self):
        ai = read_dll("CvUnitAI.cpp")
        self.assertContains(ai, "bool CvUnitAI::AI_buildGreatPersonLandmark(")
        self.assertContains(ai, "int CvUnitAI::AI_scoreLandmarkBuild(")
        # First-copy strong one-time bonus per logical type.
        self.assertContains(ai, "bFirstOfGroup")
        self.assertContains(ai, "iValue += 250")
        # Rejects unreachable / unsafe / resource-destroying / replacement.
        self.assertContains(ai, "generatePath(pLoopPlot, MOVE_SAFE_TERRITORY")
        self.assertContains(ai, "AI_getPlotDanger(pLoopPlot, 2) > 0")
        # Integrated into all four Great Person moves.
        for move in ("AI_engineerMove", "AI_scientistMove", "AI_merchantMove", "AI_prophetMove"):
            self.assertContains(ai, move)
        # Venetian scores both Merchant landmarks separately.
        self.assertContains(ai, "OPT_COMMDIST")
        self.assertContains(ai, "OPT_BAZAAR")
        self.assertContains(ai, "iValueCommDist = AI_scoreLandmarkBuild(eCommDistBuild")
        self.assertContains(ai, "iValueBazaar = AI_scoreLandmarkBuild(eBazaarBuild")


class LandmarkPreviewTooltipTests(unittest.TestCase):
    """UX enhancement: exact plot-specific total + adjacency/contributor
    breakdown surfaced in BOTH the build-action tooltip and the map plot
    tooltip, driven by one shared, authoritative preview API."""

    def assertContains(self, text, needle):
        self.assertTrue(needle in text, f"DLL source missing: {needle!r}")

    def assertMissing(self, text, needle, context):
        self.assertFalse(needle in text, f"{context} unexpectedly contains {needle!r}")

    @staticmethod
    def _slice(text, start, end):
        i = text.index(start)
        j = text.index(end, i + len(start))
        return text[i:j]

    # --- One shared preview API, declared const (read-only) --------------
    def test_shared_preview_api_declared_and_const(self):
        header = (DLL / "CvPlot.h").read_text(encoding="utf-8", errors="ignore")
        self.assertContains(header, "struct LandmarkBreakdown")
        for decl in (
            "void buildLandmarkPreview(ImprovementTypes eImprovement, PlayerTypes ePlayer, LandmarkBreakdown& kOut) const;",
            "void accumulateLandmarkAdjacency(ImprovementTypes eImprovement, PlayerTypes ePlayer, int aiYield[NUM_YIELD_TYPES], LandmarkBreakdown* pBreakdown) const;",
            "int accumulateLandmarkResearchCampus(PlayerTypes ePlayer, LandmarkBreakdown* pBreakdown) const;",
            "int getNavalFoundryAuraTileValue(PlayerTypes ePlayer) const;",
            "void accumulateNavalFoundryFootprint(PlayerTypes ePlayer, LandmarkBreakdown& kOut) const;",
        ):
            self.assertContains(header, decl)

        tmgr_h = (DLL / "CvGameTextMgr.h").read_text(encoding="utf-8", errors="ignore")
        self.assertContains(tmgr_h, "void setLandmarkPreviewHelp(CvWStringBuffer &szString, CvPlot* pPlot, ImprovementTypes eImprovement, PlayerTypes ePlayer, bool bBuilt);")

    # --- Both tooltip paths call the one formatter ----------------------
    def test_build_action_tooltip_wired(self):
        widget = read_dll("CvDLLWidgetData.cpp")
        # Landmark builds are detected and the generic native-yield delta line
        # is skipped for them (avoids duplicating the projected-output block).
        self.assertContains(widget, "bool bLandmarkBuild = (eImprovement != NO_IMPROVEMENT && GC.getImprovementInfo(eImprovement).isLandmark());")
        self.assertContains(widget, "if (!bLandmarkBuild && eImprovement != NO_IMPROVEMENT)")
        # Projected output block based on the actual mission plot + acting player.
        self.assertContains(widget, "GAMETEXT.setLandmarkPreviewHelp(szBuffer, pMissionPlot, eImprovement, pHeadSelectedUnit->getOwnerINLINE(), false);")

    def test_map_plot_tooltip_wired_with_revealed_semantics(self):
        tmgr = read_dll("CvGameTextMgr.cpp")
        # setPlotHelp renders an existing revealed landmark using the revealed
        # improvement + revealed owner (no unrevealed-data leak).
        self.assertContains(tmgr, "eImprovement = pPlot->getRevealedImprovementType(GC.getGameINLINE().getActiveTeam(), true);")
        self.assertContains(tmgr, "setLandmarkPreviewHelp(szString, pPlot, eImprovement, eRevealOwner, true);")

    # --- Formatter renders the shared breakdown, every landmark ----------
    def test_formatter_covers_every_landmark_type(self):
        block = self._slice(
            read_dll("CvGameTextMgr.cpp"),
            "void CvGameTextMgr::setLandmarkPreviewHelp(",
            "void CvGameTextMgr::setPlotHelp(",
        )
        self.assertContains(block, "pPlot->buildLandmarkPreview(eImprovement, ePlayer, kB);")
        for case in (
            "case LANDMARK_INDUSTRIAL_ZONE:",
            "case LANDMARK_NAVAL_FOUNDRY:",
            "case LANDMARK_RESEARCH_CAMPUS:",
            "case LANDMARK_COMMERCIAL_DISTRICT:",
            "case LANDMARK_GRAND_BAZAAR:",
            "case LANDMARK_SACRED_GROVE:",
        ):
            self.assertContains(block, case)
        # Research total is rendered from the exact preview value (the reported
        # missing-Research fix: Research is not a native plot yield).
        self.assertContains(block, "TXT_KEY_LANDMARK_PREVIEW_RESEARCH_TOTAL")
        self.assertContains(block, "kB.iResearchTotal")
        # Naval Foundry distinguishes source tile from effective aura footprint.
        self.assertContains(block, "kB.iFoundryOwnTileYield + kB.iFoundryAuraProduction")

    # --- Non-duplication: text reuses the authoritative runtime scans ----
    def test_runtime_helpers_reused_not_reimplemented(self):
        plot = read_dll("CvPlot.cpp")
        # Runtime yield is a thin wrapper over the shared adjacency scan.
        self.assertContains(plot, "accumulateLandmarkAdjacency(eImprovement, ePlayer, aiYield, NULL);")
        # Runtime Research value is a thin wrapper over the shared campus scan.
        self.assertContains(plot, "return accumulateLandmarkResearchCampus(ePlayer, NULL);")
        # Runtime water aura reuses the shared per-tile value formula.
        self.assertContains(plot, "getNavalFoundryAuraTileValue(ePlayer)")
        # Preview assembles from those same scans.
        preview = self._slice(plot, "void CvPlot::buildLandmarkPreview(", "void CvPlot::updateLandmarkYieldsInRange(")
        self.assertContains(preview, "accumulateLandmarkAdjacency(eImprovement, ePlayer, aiAdj, &kOut);")
        self.assertContains(preview, "accumulateLandmarkResearchCampus(ePlayer, &kOut);")
        self.assertContains(preview, "accumulateNavalFoundryFootprint(ePlayer, kOut);")

    def test_naval_foundry_effective_non_stacking(self):
        footprint = self._slice(
            read_dll("CvPlot.cpp"),
            "void CvPlot::accumulateNavalFoundryFootprint(",
            "// getLandmarkResearchCampusValue",
        )
        # Tiles already covered by a DIFFERENT owned Foundry are excluded, so the
        # preview reflects exact effective (non-stacking) contribution.
        self.assertContains(footprint, "bool bCoveredByOther = false")
        self.assertContains(footprint, "pFoundry == this")

    # --- Read-only: no RNG, no state mutation in the preview paths --------
    def test_preview_paths_are_read_only(self):
        plot = read_dll("CvPlot.cpp")
        preview = self._slice(plot, "void CvPlot::buildLandmarkPreview(", "void CvPlot::updateLandmarkYieldsInRange(")
        for forbidden in ("Rand(", "setImprovementType", "setFeatureType", "->setYield", "changeYield"):
            self.assertMissing(preview, forbidden, "landmark preview scans")
        fmt = self._slice(
            read_dll("CvGameTextMgr.cpp"),
            "void CvGameTextMgr::setLandmarkPreviewHelp(",
            "void CvGameTextMgr::setPlotHelp(",
        )
        for forbidden in ("Rand(", "setImprovementType", "changeYield"):
            self.assertMissing(fmt, forbidden, "landmark tooltip formatter")

    # --- Localization keys for headings/labels ---------------------------
    def test_preview_text_keys_present(self):
        text = TEXT.read_text(encoding="ISO-8859-1")
        for key in (
            "TXT_KEY_LANDMARK_PREVIEW_HEADER",
            "TXT_KEY_LANDMARK_OUTPUT_HEADER",
            "TXT_KEY_LANDMARK_PREVIEW_PROD_TOTAL",
            "TXT_KEY_LANDMARK_PREVIEW_COMMERCE_TOTAL",
            "TXT_KEY_LANDMARK_PREVIEW_FOOD_TOTAL",
            "TXT_KEY_LANDMARK_PREVIEW_RESEARCH_TOTAL",
            "TXT_KEY_LANDMARK_PREVIEW_NF_TOTAL",
            "TXT_KEY_LANDMARK_PREVIEW_IZ_WATERMILL",
            "TXT_KEY_LANDMARK_PREVIEW_IZ_WORKSHOP",
            "TXT_KEY_LANDMARK_PREVIEW_IZ_MINE",
            "TXT_KEY_LANDMARK_PREVIEW_IZ_NONE",
            "TXT_KEY_LANDMARK_PREVIEW_NF_OWN",
            "TXT_KEY_LANDMARK_PREVIEW_NF_AURA",
            "TXT_KEY_LANDMARK_PREVIEW_NF_AURA_RESOURCE",
            "TXT_KEY_LANDMARK_PREVIEW_NF_AURA_NONE",
            "TXT_KEY_LANDMARK_PREVIEW_RC_OWN",
            "TXT_KEY_LANDMARK_PREVIEW_RC_PEAK",
            "TXT_KEY_LANDMARK_PREVIEW_RC_JUNGLE",
            "TXT_KEY_LANDMARK_PREVIEW_RC_HILL",
            "TXT_KEY_LANDMARK_PREVIEW_RC_TUNDRA",
            "TXT_KEY_LANDMARK_PREVIEW_RC_SNOW",
            "TXT_KEY_LANDMARK_PREVIEW_RC_NONE",
            "TXT_KEY_LANDMARK_PREVIEW_CD_CITY",
            "TXT_KEY_LANDMARK_PREVIEW_CD_COTTAGE",
            "TXT_KEY_LANDMARK_PREVIEW_CD_HAMLET",
            "TXT_KEY_LANDMARK_PREVIEW_CD_VILLAGE",
            "TXT_KEY_LANDMARK_PREVIEW_CD_TOWN",
            "TXT_KEY_LANDMARK_PREVIEW_CD_NONE",
            "TXT_KEY_LANDMARK_PREVIEW_GB_HAPPY",
            "TXT_KEY_LANDMARK_PREVIEW_GB_TRADE",
            "TXT_KEY_LANDMARK_PREVIEW_GB_NONE",
            "TXT_KEY_LANDMARK_PREVIEW_SG_FORESTJUNGLE",
            "TXT_KEY_LANDMARK_PREVIEW_SG_WATER",
            "TXT_KEY_LANDMARK_PREVIEW_SG_PRESERVE",
            "TXT_KEY_LANDMARK_PREVIEW_SG_NONE",
        ):
            self.assertIn(f"<Tag>{key}</Tag>", text, key)
            # Convention: English duplicated across the four other languages.
            for lang in ("French", "German", "Italian", "Spanish"):
                self.assertIn(f"<{lang}>", text)


if __name__ == "__main__":
    unittest.main()
