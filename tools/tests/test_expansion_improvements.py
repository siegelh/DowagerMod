from pathlib import Path
import re
import json
import hashlib
import xml.etree.ElementTree as ET

from test_expansion_engine_contracts import function

ROOT = Path(__file__).resolve().parents[2]
DLL = ROOT / "third_party/beyond-the-sword-sdk/CvGameCoreDLL"
XML = ROOT / "CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML"


def test_generated_improvement_contracts_caps_pillage_yields_and_builds():
    from add_expansion_packages import parse
    manifest = json.loads((ROOT / "tools/manifests/new_leaders_expansion.json").read_bytes())
    improvements = {n.findtext("Type"): n for n in parse((XML / "Terrain/CIV4ImprovementInfos.xml").read_bytes()).iter("ImprovementInfo")}
    builds = {n.findtext("Type"): n for n in parse((XML / "Units/CIV4BuildInfos.xml").read_bytes()).iter("BuildInfo")}
    for package in manifest["packages"]:
        if "improvement" not in package:
            continue
        spec = package["improvement"]
        identifier = "IMPROVEMENT_EXP_" + spec["id"]
        for pillaged in (False, True):
            imp = improvements[identifier + ("_PILLAGED" if pillaged else "")]
            assert imp.findtext("BuildCivilization") == "CIVILIZATION_EXP_" + package["civilization"]
            assert imp.findtext("iCityBuildCap") == str(spec["cap"])
            assert imp.findtext("iCityBuildGroup") == str(spec["group"])
            assert imp.findtext("CityBuildCondition") == spec["condition"]
            assert imp.findtext("bCityBuildPillaged") == str(int(pillaged))
            assert [int(n.text) for n in imp.findall("YieldChanges/iYieldChange")] == ([0, 0, 0] if pillaged else spec["yields"])
            assert imp.findtext("ImprovementPillage") == identifier + "_PILLAGED"
            assert imp.findtext("ImprovementUpgrade") == "NONE"
            assert imp.findtext("bCarriesIrrigation") == str(int(spec["irrigation"] and not pillaged))
            for tag in ("bActsAsCity", "bRequiresIrrigation", "bOutsideBorders", "bPermanent", "iDefenseModifier"):
                assert imp.findtext(tag) == "0"
            assert imp.findtext("iAdvancedStartCost") == "-1"
            assert imp.find("BonusTypeStructs") is None
            for tag in ("TechYieldChanges", "RouteYieldChanges", "IrrigatedYieldChange", "FeatureMakesValids", "PrereqNatureYields"):
                assert not list(imp.find(tag))
        build = builds["BUILD_EXP_" + spec["id"]]
        assert int(build.findtext("iTime")) == (int(builds["BUILD_FARM"].findtext("iTime")) * spec["time_percent"] + 99) // 100
        assert build.findtext("PrereqTech") == spec["tech"]
        assert build.findtext("ImprovementType") == identifier
        assert not list(build.find("FeatureStructs"))
        assert build.findtext("bKill") == "0" and build.findtext("RouteType") == "NONE"
        for path, digest in spec["asset_sha256"].items():
            assert hashlib.sha256((XML.parent / path).read_bytes()).hexdigest() == digest


def test_new_improvements_have_one_exclusive_render_route_without_changing_original_routes():
    from add_expansion_packages import parse, baseline, canonical
    path = XML / "Buildings/CIV4PlotLSystem.xml"
    document = json.loads((ROOT / "tools/manifests/new_leaders_expansion.json").read_bytes())
    live = parse(path.read_bytes())
    # Approved pre-expansion route cleanup; this file is unchanged through David.
    original = baseline(path, "40a478e20")
    retained = [n for n in live if not n.get("Name", "").startswith(("Leaf_Expansion_", "ExpansionRoute_"))]
    assert [canonical(n) for n in retained] == [canonical(n) for n in original]
    additions = [n for n in live if n not in retained]
    assert len(additions) == 8
    for package in document["packages"]:
        if "improvement" not in package:
            continue
        for suffix in ("", "_PILLAGED"):
            identifier = "IMPROVEMENT_EXP_" + package["improvement"]["id"] + suffix
            leaf = "Leaf_Expansion_" + package["improvement"]["id"] + suffix
            routes = [n for n in live.findall("LProduction") if n.get("From") == "PLOT_ROOT"
                      and n.findtext("Attribute[@Class='Improvement']") == identifier]
            assert len(routes) == 1 and routes[0].find("To").get("Name") == leaf
            nodes = [n for n in live.findall("LNode") if n.get("Name") == leaf]
            assert len(nodes) == 1
            assert nodes[0].find("ArtRef").get("Name") == "goal:" + identifier


def test_city_build_authority_requires_real_ownership_assignment_and_resource_free_land():
    source = (DLL / "CvPlot.cpp").read_text()
    authority = function(source, "ExpansionRules::CityBuildFailure CvPlot::getCityBuildFailure")
    for token in ("getOwnerINLINE() == ePlayer", "pCity->getOwnerINLINE() == ePlayer",
                  "pCity->getCityPlotIndex(this) >= 0", "getBonusType() == NO_BONUS",
                  "getFeatureType() == NO_FEATURE", "!isCity() && !isWater() && !isPeak()",
                  "isFlatlands()", "info.getTerrainMakesValid", "isLandmark()",
                  "GC.getBuildInfo((BuildTypes)i).isKill()",
                  "isCityBuildPillaged()", "isRiverSide(), isIrrigated()",
                  '"ROUTE_ROAD"', '"ROUTE_RAILROAD"', "ExpansionRules::cityBuildLocation"):
        assert token in authority
    count = function(source, "int CvPlot::getCityBuildCount")
    assert "NUM_CITY_PLOTS" in count
    assert "pOther->getWorkingCity() == pCity" in count
    assert "pOther->getOwnerINLINE() == pCity->getOwnerINLINE()" in count
    assert "getCityBuildGroup() == iGroup" in count
    assert "isBeingWorked" not in count and "isCityBuildPillaged" not in count


def test_availability_and_completion_share_rules_without_destroying_captured_surplus():
    source = (DLL / "CvPlot.cpp").read_text()
    available = function(source, "bool CvPlot::canBuild(")
    assert "getCityBuildFailure(eImprovement, ePlayer)" in available
    assert "!bTestVisible" in available
    assert "canBuildLandmark" in available
    complete = function(source, "bool CvPlot::changeBuildProgress")
    assert complete.index("getCityBuildFailure(eTarget, getOwnerINLINE())") < complete.index("setImprovementType(")
    assert "!canBuild(eBuild, getOwnerINLINE())" in complete
    assert "getTeam() != eTeam" in complete
    assert "m_paiBuildProgress[eBuild] -= iChange;" in complete
    assert '"expansion-build.log"' in complete
    assert "TXT_KEY_EXP_BUILD_COMPLETION_REJECTED" in complete
    for signature in ("void CvPlot::setImprovementType", "void CvPlot::updateWorkingCity",
                      "void CvPlot::setOwner"):
        assert "getCityBuildCap" not in function(source, signature)
    city = (DLL / "CvCityAI.cpp").read_text()
    best = function(city, "void CvCityAI::AI_bestPlotBuild")
    assert "canBuild(pPlot," in best and "calculateImprovementYieldChange" in best
    assert "AI_workedPlotBuildValue" in best
    assert "pPlot->getCityBuildFailure(eTarget, getOwnerINLINE(), eRoute)" in best
    assert "iFutureValue / 2" in best
    assert "isHasTech((TechTypes)build.getTechPrereq())" in best


def test_pillaged_identity_survives_repeated_pillage_but_route_can_be_removed():
    source = (DLL / "CvUnit.cpp").read_text()
    assert "isCityBuildPillaged() && !pPlot->isRoute()" in function(source, "bool CvUnit::canPillage")
    pillage = function(source, "bool CvUnit::pillage()")
    assert "!GC.getImprovementInfo(pPlot->getImprovementType()).isCityBuildPillaged()" in pillage
    assert "else if (pPlot->isRoute())" in pillage
    assert "isCityBuildPillaged()" in function(source, "bool CvUnit::canAirBombAt")
    assert "isCityBuildPillaged()" in function(source, "bool CvUnit::canSabotage")
    player = (DLL / "CvPlayer.cpp").read_text()
    for signature in ("int CvPlayer::getEspionageMissionBaseCost", "bool CvPlayer::doEspionageMission"):
        block = function(player, signature)
        sabotage = block[block.index("if (kMission.isDestroyImprovement())"):]
        assert "!GC.getImprovementInfo(pPlot->getImprovementType()).isCityBuildPillaged()" in sabotage
        assert "pPlot->getRouteType() != NO_ROUTE" in sabotage


def test_improvement_cache_version_and_deferred_civilization_resolution():
    source = (DLL / "CvInfos.cpp").read_text()
    read = function(source, "void CvImprovementInfo::read(FDataStreamBase")
    write = function(source, "void CvImprovementInfo::write(FDataStreamBase")
    assert "if (uiFlag >= 4)" in read and "uint uiFlag=4" in write
    for field in ("m_szBuildCivilization", "m_iCityBuildGroup", "m_iCityBuildCap",
                  "m_iCityBuildCondition", "m_bCityBuildPillaged"):
        assert field in read and field in write
    resolver = function(source, "bool CvImprovementInfo::resolveCityBuildRules")
    assert "iIntact != 1 || iPillaged != 1" in resolver
    assert "getNumCivilizationInfos()" in resolver and "getCivilizationInfo((CivilizationTypes)iCiv).getType()" in resolver
    assert "other.getImprovementPillage() == i" in resolver
    assert "gDLL->MessageBox" in resolver and "return false;" in resolver
    loader = (DLL / "CvXMLLoadUtilitySet.cpp").read_text()
    line = next(line for line in loader.splitlines() if "LoadGlobalClassInfo(GC.getImprovementInfo()" in line)
    assert "createImprovementInfoCacheObject" not in line
    assert loader.index("LoadGlobalClassInfo(GC.getCivilizationInfo()") < loader.index("resolveCityBuildRules()")


def test_improvement_help_and_failure_keys_are_complete():
    source = (DLL / "CvGameTextMgr.cpp").read_text()
    helper = function(source, "void CvGameTextMgr::setCityBuildHelp")
    assert "pPlot->getCityBuildFailure(eImprovement, ePlayer)" in helper
    assert "pPlot->getCityBuildCount(eImprovement)" in helper
    assert "setCityBuildHelp(szBuffer, eImprovement)" in function(source, "void CvGameTextMgr::setImprovementHelp")
    assert "setCityBuildHelp(szString, eImprovement)" in source
    assert "GAMETEXT.setCityBuildHelp" in (DLL / "CvDLLWidgetData.cpp").read_text()
    records = ET.parse(XML / "Text/ZZZ_CIV4GameText_ExpansionBuilds.xml").getroot()
    ns = {"f": "http://www.firaxis.com"}
    keys = {record.findtext("f:Tag", namespaces=ns) for record in records}
    used = set(re.findall(r'"(TXT_KEY_EXP_BUILD_[^"]+)"', source + (DLL / "CvPlot.cpp").read_text()))
    assert used == keys
    for record in records:
        for language in ("English", "French", "German", "Italian", "Spanish"):
            assert record.findtext(f"f:{language}", namespaces=ns)
