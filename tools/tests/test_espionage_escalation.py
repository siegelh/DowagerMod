from __future__ import annotations

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
DLL = ROOT / "third_party" / "beyond-the-sword-sdk" / "CvGameCoreDLL"
MISSIONS = ASSETS / "XML" / "GameInfo" / "CIV4EspionageMissionInfo.xml"
SCHEMA = ASSETS / "XML" / "GameInfo" / "CIV4GameInfoSchema.xml"
TEXT = ASSETS / "XML" / "Text" / "ZZZ_CIV4GameText_StagedDiplomaticIncident.xml"


def local_name(tag):
    return tag.rsplit("}", 1)[-1]


def child_text(node, name):
    for item in node:
        if local_name(item.tag) == name:
            return (item.text or "").strip()
    return None


def mission_nodes():
    return [
        node
        for node in ET.parse(MISSIONS).getroot().iter()
        if local_name(node.tag) == "EspionageMissionInfo"
    ]


def mission(mission_type):
    return next(
        node for node in mission_nodes() if child_text(node, "Type") == mission_type
    )


class EspionageEscalationTests(unittest.TestCase):
    def test_missions_are_appended_with_locked_contracts(self):
        order = [child_text(node, "Type") for node in mission_nodes()]
        self.assertEqual(
            order[-3:],
            [
                "ESPIONAGEMISSION_STAGE_DIPLOMATIC_INCIDENT",
                "ESPIONAGEMISSION_ESTABLISH_BACKCHANNELS",
                "ESPIONAGEMISSION_FABRICATE_CASUS_BELLI",
            ],
        )

        backchannels = mission("ESPIONAGEMISSION_ESTABLISH_BACKCHANNELS")
        for tag, value in {
            "iCost": "500",
            "bIsPassive": "0",
            "bIsTwoPhases": "0",
            "bTargetsCity": "0",
            "bSelectPlot": "0",
            "TechPrereq": "NONE",
            "bEstablishesBackchannels": "1",
        }.items():
            self.assertEqual(child_text(backchannels, tag), value, tag)

        casus = mission("ESPIONAGEMISSION_FABRICATE_CASUS_BELLI")
        for tag, value in {
            "iCost": "900",
            "bIsPassive": "0",
            "bIsTwoPhases": "1",
            "bTargetsCity": "0",
            "bSelectPlot": "0",
            "TechPrereq": "NONE",
            "bFabricatesCasusBelli": "1",
            "iCasusBelliMinAttitude": "-3",
            "iCasusBelliMinPowerRatio": "70",
            "iCasusBelliBaseChance": "10",
            "iCasusBelliAttitudeChancePerPoint": "4",
            "iCasusBelliFuriousBonus": "15",
            "iCasusBelliMaxChance": "70",
        }.items():
            self.assertEqual(child_text(casus, tag), value, tag)

    def test_optional_info_fields_are_loaded_and_python_exposed(self):
        schema = SCHEMA.read_text(encoding="utf-8")
        sources = "\n".join(
            (DLL / name).read_text(encoding="utf-8", errors="ignore")
            for name in ("CvInfos.h", "CvInfos.cpp", "CyInfoInterface3.cpp")
        )
        fields = (
            "bEstablishesBackchannels",
            "bFabricatesCasusBelli",
            "iCasusBelliMinAttitude",
            "iCasusBelliMinPowerRatio",
            "iCasusBelliBaseChance",
            "iCasusBelliAttitudeChancePerPoint",
            "iCasusBelliFuriousBonus",
            "iCasusBelliMaxChance",
        )
        for field in fields:
            self.assertIn(f'name="{field}"', schema)
            self.assertIn(f'type="{field}" minOccurs="0"', schema)
            self.assertIn(f'"{field}"', sources)
        for getter in (
            "isEstablishesBackchannels",
            "isFabricatesCasusBelli",
            "getCasusBelliMinAttitude",
            "getCasusBelliMinPowerRatio",
            "getCasusBelliBaseChance",
            "getCasusBelliAttitudeChancePerPoint",
            "getCasusBelliFuriousBonus",
            "getCasusBelliMaxChance",
        ):
            self.assertIn(f'.def("{getter}"', sources)

    def test_backchannels_is_ai_only_peaceful_and_unlimited(self):
        source = (DLL / "CvPlayer.cpp").read_text(
            encoding="utf-8", errors="ignore"
        )
        helper = source.split("bool CvPlayer::canEstablishBackchannels", 1)[1].split(
            "bool CvPlayer::canFabricateCasusBelli", 1
        )[0]
        for token in (
            "kTargetPlayer.isHuman()",
            "kTargetPlayer.isBarbarian()",
            "kTargetPlayer.isMinorCiv()",
            "GET_TEAM(getTeam()).isAtWar(eTargetTeam)",
        ):
            self.assertIn(token, helper)

        execution = source.split("bool CvPlayer::doEspionageMission", 1)[1]
        effect = (
            "GET_PLAYER(eTargetPlayer).AI_changeMemoryCount("
            "getID(), MEMORY_GIVE_HELP, 1);"
        )
        self.assertEqual(execution.count(effect), 1)
        self.assertNotIn("AI_setMemoryCount(getID(), MEMORY_GIVE_HELP", execution)
        self.assertNotIn("getMemoryCount(getID(), MEMORY_GIVE_HELP)", execution)

    def test_casus_eligibility_covers_all_hard_exclusions(self):
        source = (DLL / "CvPlayer.cpp").read_text(
            encoding="utf-8", errors="ignore"
        )
        helper = source.split(
            "CvPlayer::FabricateCasusBelliResult "
            "CvPlayer::evaluateFabricateCasusBelli",
            1,
        )[1].split(
            "bool CvPlayer::canFabricateCasusBelli", 1
        )[0]
        for token in (
            "kTargetPlayer.isHuman()",
            "kTargetTeam.isHuman()",
            "kTargetTeam.isAVassal()",
            "kTargetTeam.getAtWarCount(true) > 0",
            "kTargetTeam.getAnyWarPlanCount(true) > 0",
            "kTargetTeam.isVassal(eFramedTeam)",
            "kFramedTeam.isVassal(eTargetTeam)",
            "kTargetTeam.isDefensivePact(eFramedTeam)",
            "kTargetTeam.canDeclareWar(eFramedTeam)",
            "kTargetTeam.AI_isAllyLandTarget(eFramedTeam)",
            "AI_getAttitudeVal(eFramedPlayer)",
            "getCasusBelliMinPowerRatio()",
        ):
            self.assertIn(token, helper)
        for result in (
            "FABRICATE_CASUS_BELLI_TARGET_HAS_NOT_MET_FRAMED",
            "FABRICATE_CASUS_BELLI_TEAM_CONFLICT",
            "FABRICATE_CASUS_BELLI_TARGET_TEAM_HUMAN",
            "FABRICATE_CASUS_BELLI_TARGET_VASSAL",
            "FABRICATE_CASUS_BELLI_TARGET_AT_WAR",
            "FABRICATE_CASUS_BELLI_TARGET_HAS_WAR_PLAN",
            "FABRICATE_CASUS_BELLI_VASSAL_RELATIONSHIP",
            "FABRICATE_CASUS_BELLI_DEFENSIVE_PACT",
            "FABRICATE_CASUS_BELLI_CANNOT_DECLARE_WAR",
            "FABRICATE_CASUS_BELLI_NOT_LAND_TARGET",
            "FABRICATE_CASUS_BELLI_ATTITUDE_TOO_HIGH",
            "FABRICATE_CASUS_BELLI_POWER_TOO_LOW",
        ):
            self.assertIn(result, helper)

        wrapper = source.split("bool CvPlayer::canFabricateCasusBelli", 1)[1].split(
            "int CvPlayer::getFabricateCasusBelliChance", 1
        )[0]
        self.assertIn("evaluateFabricateCasusBelli", wrapper)

    def test_chance_formula_has_exact_boundaries_and_one_shared_helper(self):
        source = (DLL / "CvPlayer.cpp").read_text(
            encoding="utf-8", errors="ignore"
        )
        chance = source.split(
            "CvPlayer::FabricateCasusBelliResult "
            "CvPlayer::evaluateFabricateCasusBelli",
            1,
        )[1].split("bool CvPlayer::canFabricateCasusBelli", 1)[0]
        for token in (
            "getCasusBelliBaseChance()",
            "getCasusBelliAttitudeChancePerPoint()",
            "iAttitude <= -10",
            "getCasusBelliFuriousBonus()",
            "iPowerRatio < 90",
            "iChance -= 20",
            "iPowerRatio >= 130",
            "iChance += 20",
            "iPowerRatio >= 110",
            "iChance += 10",
            "std::max(10, iChance)",
            "getCasusBelliMaxChance()",
        ):
            self.assertIn(token, chance)

        popup = (DLL / "CvDLLButtonPopup.cpp").read_text(
            encoding="utf-8", errors="ignore"
        )
        ai = (DLL / "CvPlayerAI.cpp").read_text(
            encoding="utf-8", errors="ignore"
        )
        self.assertIn("evaluateFabricateCasusBelli", popup)
        self.assertIn("getFabricateCasusBelliChance", ai)
        self.assertGreaterEqual(source.count("getFabricateCasusBelliChance"), 2)
        chance_wrapper = source.split(
            "int CvPlayer::getFabricateCasusBelliChance", 1
        )[1].split("bool CvPlayer::canDoEspionageMission", 1)[0]
        self.assertIn("evaluateFabricateCasusBelli", chance_wrapper)

        def chance(attitude, power_ratio):
            value = 10 + 4 * max(0, -3 - attitude)
            if attitude <= -10:
                value += 15
            if power_ratio < 90:
                value -= 20
            elif power_ratio >= 130:
                value += 20
            elif power_ratio >= 110:
                value += 10
            return min(70, max(10, value))

        self.assertEqual(chance(-3, 70), 10)
        self.assertEqual(chance(-3, 90), 10)
        self.assertEqual(chance(-3, 110), 20)
        self.assertEqual(chance(-3, 130), 30)
        self.assertEqual(chance(-6, 90), 22)
        self.assertEqual(chance(-10, 90), 53)
        self.assertEqual(chance(-15, 130), 70)

    def test_casus_top_level_cost_does_not_require_an_eligible_candidate(self):
        source = (DLL / "CvPlayer.cpp").read_text(
            encoding="utf-8", errors="ignore"
        )
        branch = source.split("else if (kMission.isFabricatesCasusBelli())", 1)[
            1
        ].split("else if (kMission.getStealTreasuryTypes()", 1)[0]
        top_level, selected = branch.split("else if (iExtraData", 1)
        self.assertNotIn("canFabricateCasusBelli", top_level)
        self.assertNotIn("for (int iFramedPlayer", top_level)
        self.assertIn("iMissionCost =", top_level)
        self.assertIn("canFabricateCasusBelli", selected)

    def test_casus_popup_reports_rejections_and_only_buttons_eligible_targets(self):
        popup = (DLL / "CvDLLButtonPopup.cpp").read_text(
            encoding="utf-8", errors="ignore"
        )
        target_popup = popup.split(
            "bool CvDLLButtonPopup::launchDoEspionageTargetPopup", 1
        )[1].split("else if (kMission.getDestroyBuildingCostFactor()", 1)[0]
        self.assertIn("evaluateFabricateCasusBelli", target_popup)
        self.assertIn("FABRICATE_CASUS_BELLI_ELIGIBLE", target_popup)
        self.assertIn(
            "TXT_KEY_ESPIONAGE_CASUS_BELLI_UNAVAILABLE_CIVILIZATION",
            target_popup,
        )
        self.assertIn(
            "TXT_KEY_ESPIONAGE_CASUS_BELLI_NO_ELIGIBLE_TARGET", target_popup
        )
        self.assertNotIn(
            "kFramedPlayer.getTeam() == kPlayer.getTeam()", target_popup
        )
        eligible_branch = target_popup.split(
            "if (eResult == CvPlayer::FABRICATE_CASUS_BELLI_ELIGIBLE)", 1
        )[1].split("else", 1)[0]
        rejected_branch = target_popup.split(
            "if (eResult == CvPlayer::FABRICATE_CASUS_BELLI_ELIGIBLE)", 1
        )[1].split("else", 1)[1].split("continue;", 1)[0]
        self.assertIn("popupAddGenericButton", eligible_branch)
        self.assertNotIn("popupAddGenericButton", rejected_branch)

    def test_execution_revalidates_before_interception_and_uses_sync_rng(self):
        unit = (DLL / "CvUnit.cpp").read_text(encoding="utf-8", errors="ignore")
        validation = unit.index(
            "GC.getEspionageMissionInfo(eMission).isFabricatesCasusBelli()"
        )
        interception = unit.index(
            "testSpyIntercepted(eTargetPlayer, "
            "GC.getEspionageMissionInfo(eMission).getDifficultyMod())",
            validation,
        )
        self.assertLess(validation, interception)

        source = (DLL / "CvPlayer.cpp").read_text(
            encoding="utf-8", errors="ignore"
        )
        execution = source.split("bool CvPlayer::doEspionageMission", 1)[1].split(
            "int CvPlayer::getEspionageSpendingWeightAgainstTeam", 1
        )[0]
        self.assertIn(
            'getSorenRandNum(100, "Fabricate Casus Belli")', execution
        )
        self.assertIn(
            "AI_setWarPlan(GET_PLAYER(eFramedPlayer).getTeam(), "
            "WARPLAN_PREPARING_LIMITED)",
            execution,
        )
        casus = execution.split("else if (kMission.isFabricatesCasusBelli())", 1)[
            1
        ].split("// Destroy Improvement", 1)[0]
        self.assertNotIn("getASyncRand", casus)
        self.assertEqual(casus.count("bSomethingHappened = true;"), 1)
        self.assertIn("TXT_KEY_ESPIONAGE_CASUS_BELLI_SUCCESS", casus)
        self.assertIn("TXT_KEY_ESPIONAGE_CASUS_BELLI_FAILURE", casus)

    def test_ai_selection_is_deterministic(self):
        ai = (DLL / "CvPlayerAI.cpp").read_text(
            encoding="utf-8", errors="ignore"
        )
        selector = ai.split(
            "EspionageMissionTypes CvPlayerAI::AI_bestPlotEspionage", 1
        )[1].split("int CvPlayerAI::AI_espionageVal", 1)[0]
        self.assertIn("kMissionInfo.isEstablishesBackchannels()", selector)
        self.assertIn("kMissionInfo.isFabricatesCasusBelli()", selector)
        self.assertIn(
            "for (int iFramedPlayer = 0; "
            "iFramedPlayer < MAX_CIV_PLAYERS; ++iFramedPlayer)",
            selector,
        )
        self.assertNotIn("getSorenRandNum", selector)
        self.assertNotIn("getASyncRand", selector)

    def test_all_new_player_messages_are_localized(self):
        root = ET.parse(TEXT).getroot()
        text_nodes = [node for node in root if local_name(node.tag) == "TEXT"]
        nodes = {child_text(node, "Tag"): node for node in text_nodes}
        required = {
            "TXT_KEY_ESPIONAGE_ESTABLISH_BACKCHANNELS",
            "TXT_KEY_ESPIONAGE_BACKCHANNELS_SUCCESS",
            "TXT_KEY_ESPIONAGE_FABRICATE_CASUS_BELLI",
            "TXT_KEY_ESPIONAGE_CHOOSE_CASUS_BELLI_TARGET",
            "TXT_KEY_ESPIONAGE_CASUS_BELLI_CIVILIZATION",
            "TXT_KEY_ESPIONAGE_CASUS_BELLI_SUCCESS",
            "TXT_KEY_ESPIONAGE_CASUS_BELLI_FAILURE",
            "TXT_KEY_ESPIONAGE_CASUS_BELLI_UNAVAILABLE_HEADER",
            "TXT_KEY_ESPIONAGE_CASUS_BELLI_UNAVAILABLE_CIVILIZATION",
            "TXT_KEY_ESPIONAGE_CASUS_BELLI_NO_ELIGIBLE_TARGET",
            "TXT_KEY_ESPIONAGE_CASUS_BELLI_REASON_TARGET_NOT_MET",
            "TXT_KEY_ESPIONAGE_CASUS_BELLI_REASON_TEAM_CONFLICT",
            "TXT_KEY_ESPIONAGE_CASUS_BELLI_REASON_HUMAN_TEAM",
            "TXT_KEY_ESPIONAGE_CASUS_BELLI_REASON_TARGET_VASSAL",
            "TXT_KEY_ESPIONAGE_CASUS_BELLI_REASON_TARGET_AT_WAR",
            "TXT_KEY_ESPIONAGE_CASUS_BELLI_REASON_WAR_PLAN",
            "TXT_KEY_ESPIONAGE_CASUS_BELLI_REASON_VASSAL_RELATIONSHIP",
            "TXT_KEY_ESPIONAGE_CASUS_BELLI_REASON_DEFENSIVE_PACT",
            "TXT_KEY_ESPIONAGE_CASUS_BELLI_REASON_CANNOT_DECLARE",
            "TXT_KEY_ESPIONAGE_CASUS_BELLI_REASON_NOT_LAND_TARGET",
            "TXT_KEY_ESPIONAGE_CASUS_BELLI_REASON_ATTITUDE",
            "TXT_KEY_ESPIONAGE_CASUS_BELLI_REASON_POWER",
            "TXT_KEY_ESPIONAGE_CASUS_BELLI_REASON_UNAVAILABLE",
        }
        self.assertTrue(required.issubset(nodes))
        for tag in required:
            for language in ("English", "French", "German", "Italian", "Spanish"):
                self.assertTrue(child_text(nodes[tag], language), (tag, language))


if __name__ == "__main__":
    unittest.main()
