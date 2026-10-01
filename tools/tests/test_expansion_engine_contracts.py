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
