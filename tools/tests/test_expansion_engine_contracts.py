from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
DLL = ROOT / "third_party/beyond-the-sword-sdk/CvGameCoreDLL"


def test_occupation_discount_only_wraps_new_conquest_duration():
    source = (DLL / "CvPlayer.cpp").read_text()
    start = source.index("if (bTrade)\n\t{\n\t\tif (isHuman()")
    end = source.index("pCityPlot->setRevealed", start)
    block = source[start:end]
    trade, conquest = block.split("if (bConquest)", 1)
    assert "changeOccupationTimer(iOccupationTimer)" in trade
    assert "conquestOccupationTurns" not in trade
    assert conquest.count("ExpansionRules::conquestOccupationTurns") == 1
    assert source.count("ExpansionRules::conquestOccupationTurns") == 1


def test_research_access_is_additive_once_and_uses_live_team_state():
    source = (DLL / "CvPlayer.cpp").read_text()
    start = source.index("int CvPlayer::getOpenBordersKnownTechResearchModifier")
    end = source.index("int CvPlayer::calculateBaseNetResearch", start)
    block = source[start:end]
    assert "if (eTech == NO_TECH)" in block
    assert "if (ePartner == getTeam())" in block
    assert "kPartner.isVassal(getTeam())" in block
    assert "kTeam.isVassal(ePartner)" in block
    assert "return iBonus;" in block
    assert block.count("iModifier += getOpenBordersKnownTechResearchModifier(eTech);") == 1
    assert "TECH_COST_TOTAL_KNOWN_TEAM_MODIFIER" in block
    assert "TECH_COST_KNOWN_PREREQ_MODIFIER" in block


def test_trait_extensions_are_neutral_and_do_not_introduce_cache_or_save_state():
    source = (DLL / "CvInfos.cpp").read_text()
    for field in ("OpenBordersKnownTechResearchModifier", "ConquestOccupationReductionPercent",
                  "CoastalForeignTeamGold", "CoastalForeignTeamGoldCap"):
        assert f'm_i{field}(0)' in source
        assert f'&m_i{field}, "i{field}", 0' in source
    loader = (DLL / "CvXMLLoadUtilitySet.cpp").read_text()
    line = next(line for line in loader.splitlines() if "LoadGlobalClassInfo(GC.getTraitInfo()" in line)
    assert line.rstrip().endswith("false);"), "Trait XML currently has no info-cache serialization"
    assert not re.search(r"CvTraitInfo::(?:read|write)\(FDataStream", source)


def test_coastal_gold_counts_real_routes_before_modifiers_and_refreshes_equal_yields():
    source = (DLL / "CvCity.cpp").read_text()
    start = source.index("int CvCity::getForeignTradeTeamCount")
    end = source.index("void CvCity::clearOrderQueue", start)
    block = source[start:end]
    assert "CvCity* pPartner = getTradeCity(iRoute);" in block
    assert "GET_PLAYER(pPartner->getOwnerINLINE()).isAlive()" in block
    assert "ExpansionRules::distinctForeignTeams" in block
    assert "isCoastal(GC.getMIN_WATER_SIZE_FOR_OCEAN())" in block
    assert "ExpansionRules::cappedContribution" in block
    clear, refresh = block.split("void CvCity::updateTradeRoutes()", 1)
    assert clear.index("m_paTradeCities[iI].reset()") < clear.index("updateCommerce(COMMERCE_GOLD)")
    assert refresh.index("setTradeYield(") < refresh.index("updateCommerce(COMMERCE_GOLD)")
    base = source[source.index("int CvCity::getBaseCommerceRateTimes100"):
                  source.index("int CvCity::getTotalCommerceRateModifier")]
    assert "if (eIndex == COMMERCE_GOLD)" in base
    assert "iBaseCommerceRate += 100 * getCoastalForeignTradeGold();" in base
    assert "m_iCoastalForeign" not in (DLL / "CvCity.h").read_text()


def test_trade_gold_help_and_diplomacy_ai_use_the_authoritative_calculation():
    help_source = (DLL / "CvGameTextMgr.cpp").read_text()
    assert 'TXT_KEY_TRAIT_EXP_COASTAL_TRADE' in help_source
    assert 'TXT_KEY_CITY_EXP_COASTAL_TRADE' in help_source
    assert "city.getForeignTradeTeamCount(), city.getCoastalForeignTradeGoldCap()" in help_source
    ai = (DLL / "CvTeamAI.cpp").read_text()
    assert "pCity->getCoastalForeignTradeGold(eTeam) - pCity->getCoastalForeignTradeGold()" in ai


def function(source, signature):
    start = source.index(signature)
    body = source.index("{", start)
    depth = 1
    end = body + 1
    while depth:
        depth += (source[end] == "{") - (source[end] == "}")
        end += 1
    return source[start:end]


def test_worked_rules_require_owned_assigned_worked_plots_and_active_prerequisites():
    source = (DLL / "CvCity.cpp").read_text()
    active = function(source, "bool CvCity::isWorkedPlotRuleActive")
    assert "!hasTrait(eTrait)" in active
    assert "isHasTech(kTrait.getWorkedPlotPrereqTech())" in active
    assert "getNumActiveBuilding(eRequired)" in active
    assert "isObsoleteBuilding(eRequired)" in active
    qualifies = function(source, "bool CvCity::qualifiesWorkedPlot")
    for term in ("pPlot->getOwnerINLINE() == getOwnerINLINE()", "pPlot->getWorkingCity() == this",
                 "bWorked, pPlot->isCity(), pPlot->isWater()", 'getDefineINT("RUINS_IMPROVEMENT")',
                 "isWorkedPlotExcludedImprovement", "isFeatureRemove(eFeature)", "kBuild.getRoute()"):
        assert term in qualifies
    count = function(source, "int CvCity::getWorkedPlotCount")
    assert "pPlot != pExclude" in count
    assert "isWorkingPlot(i)" in count
    marginal = function(source, "ExpansionRules::WorkedPlotBonuses CvCity::getWorkedPlotMarginal")
    assert "getWorkedPlotCount(eTrait, pPlot)" in marginal
    assert "bRemove && !isWorkingPlot(pPlot)" in marginal
    assert marginal.count("ExpansionRules::cappedMarginal") == 3


def test_worked_production_is_derived_and_reconstructed_without_new_saved_state():
    source = (DLL / "CvCity.cpp").read_text()
    assert "getWorkedPlotProduction()" in function(source, "int CvCity::getBaseYieldRate")
    setter = function(source, "void CvCity::setBaseYieldRate")
    assert "getWorkedPlotProduction()" in setter and "iNewValue - iDerivedValue" in setter
    update = function(source, "void CvCity::updateImprovementCityCommerceFromTraitsAndCivics")
    assert "m_iWorkedPlotProduction = bonus.production" in update
    assert "invalidateYieldRankCache(YIELD_PRODUCTION)" in update
    assert "bonus.gold" in update and "bonus.culture" in update
    assert "AI_setAssignWorkDirty" not in update, "Assignment refresh must not dirty assignment recursively"
    assert "updateImprovementCityCommerceFromTraitsAndCivics(false)" in function(source, "void CvCity::read")
    assert "m_iWorkedPlotProduction" not in function(source, "void CvCity::write")
    game = function((DLL / "CvGame.cpp").read_text(), "void CvGame::setFinalInitialized")
    assert game.index("updatePlotGroups()") < game.index("updateImprovementCityCommerceFromTraitsAndCivics")


def test_worked_rules_refresh_when_native_yields_do_not_change():
    city = (DLL / "CvCity.cpp").read_text()
    for signature in ("void CvCity::processBuilding", "void CvCity::setWorkingPlot(int"):
        assert "updateImprovementCityCommerceFromTraitsAndCivics" in function(city, signature)
    plot = function((DLL / "CvPlot.cpp").read_text(), "void CvPlot::updateYield()")
    refresh = plot.index("pWorkingCity->updateImprovementCityCommerceFromTraitsAndCivics(true)")
    assert refresh < plot.rindex("if (bChange)")
    assert "AI_setAssignWorkDirty(true)" in plot[refresh:]
    team = (DLL / "CvTeam.cpp").read_text()
    assert "processTech(eIndex," in function(team, "void CvTeam::setHasTech")
    tech = function(team, "void CvTeam::processTech")
    assert "pWorkedCity->updateImprovementCityCommerceFromTraitsAndCivics(true)" in tech
    assert "pWorkedCity->AI_setAssignWorkDirty(true)" in tech


def test_worked_trait_references_resolve_after_buildings_and_validate_type_identity():
    loader = (DLL / "CvXMLLoadUtilitySet.cpp").read_text()
    assert loader.index('LoadGlobalClassInfo(GC.getBuildingInfo()') < loader.index(
        "if (!GC.getTraitInfo((TraitTypes)i).readPass3())")
    source = (DLL / "CvInfos.cpp").read_text()
    third = function(source, "bool CvTraitInfo::readPass3")
    for term in ("getNumTechInfos()", "getNumBuildingInfos()", "getNumImprovementInfos()",
                 "GC.getTechInfo(m_eWorkedPlotPrereqTech).getType()",
                 "GC.getBuildingInfo(m_eWorkedPlotPrereqBuilding).getType()",
                 "GC.getImprovementInfo((ImprovementTypes)iType).getType()",
                 "conflicting worked-plot improvement lists"):
        assert term in third
    read = function(source, "bool CvTraitInfo::read(CvXMLLoadUtility")
    assert "iWorkedChannels != 1" in read
    for channel in ("Production", "Gold", "Culture", "Cap"):
        assert f'&m_iWorkedPlot{channel}, "iWorkedPlot{channel}", 0' in read


def test_worked_rules_reach_governor_workers_chopping_roads_and_buildings():
    source = (DLL / "CvCityAI.cpp").read_text()
    governor = function(source, "int CvCityAI::AI_plotValue")
    assert "getWorkedPlotMarginal(pPlot, bRemove)" in governor
    assert governor.index("iYieldValue /= 16") < governor.index("iValue += std::max(0, iWorkedPlotValue)")
    build = function(source, "void CvCityAI::AI_bestPlotBuild")
    assert build.count("AI_workedPlotBuildValue(") == 5
    assert "if (iTempValue > 0 || bWorkedPlotRules)" in build
    assert "(iTempValue + iWorkedChange) * 5 * 300" in build
    assert "workedBuildingBonus.production * 6" in function(source, "int CvCityAI::AI_buildingValueThreshold")


def test_commerce_breakdown_includes_all_trait_sources_without_double_counting():
    source = (DLL / "CvGameTextMgr.cpp").read_text()
    commerce = function(source, "void CvGameTextMgr::setCommerceHelp")
    assert "city.getTraitSpecialistCommerce(eCommerceType)" in commerce
    assert "appendWorkedPlotCityHelp(szBuffer, city, NO_YIELD, eCommerceType)" in commerce
    assert "city.getImprovementCityCommerceFromTraitsAndCivics(eCommerceType, false) - iWorkedCommerce" in commerce
    assert "appendWorkedPlotCityHelp" in function(source, "void CvGameTextMgr::setYieldHelp")
    import xml.etree.ElementTree as ET
    text = ROOT / "CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Text/ZZZ_CIV4GameText_ExpansionRules.xml"
    records = ET.parse(text).getroot()
    ns = {"f": "http://www.firaxis.com"}
    keys = {record.findtext("f:Tag", namespaces=ns) for record in records}
    used = set(re.findall(r'"(TXT_KEY_(?:TRAIT|CITY)_EXP_WORKED[^"]*|TXT_KEY_EXP_WORKED[^"]*)"', source))
    assert used <= keys
    for record in records:
        for language in ("English", "French", "German", "Italian", "Spanish"):
            assert record.findtext(f"f:{language}", namespaces=ns)
