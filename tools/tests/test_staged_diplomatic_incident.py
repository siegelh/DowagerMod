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
MISSION_TYPE = "ESPIONAGEMISSION_STAGE_DIPLOMATIC_INCIDENT"


def local_name(tag):
    return tag.rsplit("}", 1)[-1]


def children(node, name):
    return [item for item in node if local_name(item.tag) == name]


def child_text(node, name):
    items = children(node, name)
    return None if not items else (items[0].text or "").strip()


def read_dll(*names):
    return "\n".join(
        (DLL / name).read_text(encoding="utf-8", errors="ignore") for name in names
    )


class StagedDiplomaticIncidentTests(unittest.TestCase):
    def setUp(self):
        root = ET.parse(MISSIONS).getroot()
        self.mission = next(
            node
            for node in root.iter()
            if local_name(node.tag) == "EspionageMissionInfo"
            if child_text(node, "Type") == MISSION_TYPE
        )

    def test_exact_mission_contract(self):
        expected = {
            "Description": "TXT_KEY_ESPIONAGE_STAGE_DIPLOMATIC_INCIDENT",
            "iCost": "400",
            "bIsPassive": "0",
            "bIsTwoPhases": "1",
            "bTargetsCity": "0",
            "bSelectPlot": "0",
            "TechPrereq": "NONE",
            "bStagesDiplomaticIncident": "1",
            "iDiplomaticAttitudeChange": "-2",
            "iDifficultyMod": "0",
        }
        for tag, value in expected.items():
            self.assertEqual(child_text(self.mission, tag), value, tag)
        mission_order = [
            child_text(node, "Type")
            for node in ET.parse(MISSIONS).getroot().iter()
            if local_name(node.tag) == "EspionageMissionInfo"
        ]
        self.assertEqual(mission_order[-3], MISSION_TYPE)

    def test_schema_and_info_class_expose_dedicated_fields(self):
        schema = SCHEMA.read_text(encoding="utf-8")
        infos = read_dll("CvInfos.h", "CvInfos.cpp", "CyInfoInterface3.cpp")
        for name in ("bStagesDiplomaticIncident", "iDiplomaticAttitudeChange"):
            self.assertIn(f'name="{name}"', schema)
            self.assertIn(f'"{name}"', infos)
        self.assertIn("bool isStagesDiplomaticIncident() const;", infos)
        self.assertIn("int getDiplomaticAttitudeChange() const;", infos)
        self.assertIn(
            '.def("isStagesDiplomaticIncident", '
            "&CvEspionageMissionInfo::isStagesDiplomaticIncident",
            infos,
        )

    def test_one_shared_eligibility_contract_covers_required_exclusions(self):
        header = (DLL / "CvPlayer.h").read_text(encoding="utf-8")
        source = (DLL / "CvPlayer.cpp").read_text(encoding="utf-8")
        self.assertIn(
            "bool canStageDiplomaticIncident(PlayerTypes eTargetPlayer, "
            "PlayerTypes eFramedPlayer) const;",
            header,
        )
        helper = source.split(
            "bool CvPlayer::canStageDiplomaticIncident", 1
        )[1].split("bool CvPlayer::canDoEspionageMission", 1)[0]
        required = (
            "eFramedPlayer == getID()",
            "eFramedPlayer == eTargetPlayer",
            "kTargetPlayer.isHuman()",
            "kTargetPlayer.isBarbarian()",
            "kTargetPlayer.isMinorCiv()",
            "kFramedPlayer.isBarbarian()",
            "kFramedPlayer.isMinorCiv()",
            "eFramedTeam == getTeam()",
            "eFramedTeam == eTargetTeam",
            "GET_TEAM(getTeam()).isHasMet(eFramedTeam)",
            "GET_TEAM(eTargetTeam).isHasMet(eFramedTeam)",
            "GET_TEAM(eTargetTeam).isVassal(eFramedTeam)",
            "GET_TEAM(eFramedTeam).isVassal(eTargetTeam)",
        )
        for token in required:
            self.assertIn(token, helper)

    def test_existing_destroy_project_difficulty_is_unchanged(self):
        root = ET.parse(MISSIONS).getroot()
        destroy_project = next(
            node
            for node in root.iter()
            if local_name(node.tag) == "EspionageMissionInfo"
            if child_text(node, "Type") == "ESPIONAGEMISSION_DESTROY_PROJECT"
        )
        self.assertEqual(child_text(destroy_project, "iDifficultyMod"), "25")

    def test_availability_and_execution_revalidate_extra_data(self):
        source = (DLL / "CvPlayer.cpp").read_text(encoding="utf-8")
        availability = source.split(
            "bool CvPlayer::canDoEspionageMission", 1
        )[1].split("int CvPlayer::getEspionageMissionCost", 1)[0]
        base_cost = source.split(
            "int CvPlayer::getEspionageMissionBaseCost", 1
        )[1].split("int CvPlayer::getEspionageMissionCostModifier", 1)[0]
        execution = source.split(
            "bool CvPlayer::doEspionageMission", 1
        )[1].split("int CvPlayer::getEspionageSpendingWeightAgainstTeam", 1)[0]
        self.assertIn("if (iExtraData == -1)", base_cost)
        self.assertIn("iExtraData < MAX_CIV_PLAYERS", base_cost)
        self.assertGreaterEqual(
            base_cost.count("canStageDiplomaticIncident"), 2
        )
        self.assertIn(
            "canStageDiplomaticIncident(eTargetPlayer, eFramedPlayer)",
            execution,
        )
        shared_validation = source.split(
            "bool CvPlayer::hasValidDiplomaticEspionageSpy", 1
        )[1].split("bool CvPlayer::canStageDiplomaticIncident", 1)[0]
        for token in (
            "pUnit != NULL",
            "pPlot != NULL",
            "pUnit->getOwnerINLINE() == getID()",
            "pUnit->plot() == pPlot",
            "pPlot->getOwnerINLINE() == eTargetPlayer",
            "pUnit->canEspionage(pPlot)",
        ):
            self.assertIn(token, shared_validation)
        self.assertIn("hasValidDiplomaticEspionageSpy", availability)
        self.assertIn("hasValidDiplomaticEspionageSpy", execution)
        unit = (DLL / "CvUnit.cpp").read_text(encoding="utf-8", errors="ignore")
        staged_validation = unit.index(
            "GC.getEspionageMissionInfo(eMission).isStagesDiplomaticIncident()"
        )
        interception = unit.index(
            "testSpyIntercepted(eTargetPlayer, "
            'GC.getEspionageMissionInfo(eMission).getDifficultyMod())',
            staged_validation,
        )
        self.assertLess(staged_validation, interception)

    def test_effect_is_one_way_fixed_and_stackable(self):
        execution = (DLL / "CvPlayer.cpp").read_text(
            encoding="utf-8", errors="ignore"
        ).split("bool CvPlayer::doEspionageMission", 1)[1]
        effect = (
            "GET_PLAYER(eTargetPlayer).AI_changeAttitudeExtra("
            "eFramedPlayer, kMission.getDiplomaticAttitudeChange());"
        )
        self.assertEqual(execution.count(effect), 1)
        self.assertNotIn("AI_setAttitudeExtra(eFramedPlayer", execution)
        self.assertNotIn("GET_PLAYER(eFramedPlayer).AI_changeAttitudeExtra", execution)

    def test_native_popup_carries_player_id_through_synchronized_mission(self):
        popup = (DLL / "CvDLLButtonPopup.cpp").read_text(
            encoding="utf-8", errors="ignore"
        )
        self.assertIn("TXT_KEY_ESPIONAGE_CHOOSE_FRAMED_CIVILIZATION", popup)
        self.assertIn("TXT_KEY_ESPIONAGE_FRAME_CIVILIZATION", popup)
        self.assertIn(
            "kPlayer.canStageDiplomaticIncident(eTargetPlayer, eFramedPlayer)",
            popup,
        )
        self.assertIn(
            "MISSION_ESPIONAGE, (EspionageMissionTypes)info.getData1(), "
            "pPopupReturn->getButtonClicked()",
            popup,
        )

    def test_ai_selects_framed_player_without_randomness(self):
        ai = (DLL / "CvPlayerAI.cpp").read_text(encoding="utf-8", errors="ignore")
        selector = ai.split(
            "EspionageMissionTypes CvPlayerAI::AI_bestPlotEspionage", 1
        )[1].split("int CvPlayerAI::AI_espionageVal", 1)[0]
        value = ai.split("int CvPlayerAI::AI_espionageVal", 1)[1]
        self.assertIn("kMissionInfo.isStagesDiplomaticIncident()", selector)
        self.assertIn(
            "for (int iFramedPlayer = 0; "
            "iFramedPlayer < MAX_CIV_PLAYERS; ++iFramedPlayer)",
            selector,
        )
        self.assertIn("iData = iFramedPlayer;", selector)
        self.assertIn("isStagesDiplomaticIncident()", value)
        self.assertIn("AI_getAttitudeVal(eFramedPlayer)", value)
        self.assertIn(
            "AI_getAttitudeFromValue(iCurrentAttitude) == "
            "AI_getAttitudeFromValue(iChangedAttitude)",
            value,
        )
        incident_selector = selector.split(
            "kMissionInfo.isStagesDiplomaticIncident()", 1
        )[1].split("if (!AI_isDoStrategy", 1)[0]
        self.assertNotIn("getSorenRandNum", incident_selector)
        self.assertNotIn("getASyncRand", incident_selector)

    def test_required_player_messages_are_localized(self):
        root = ET.parse(TEXT).getroot()
        text_nodes = [node for node in root if local_name(node.tag) == "TEXT"]
        tags = {child_text(node, "Tag") for node in text_nodes}
        self.assertTrue(
            {
                "TXT_KEY_ESPIONAGE_STAGE_DIPLOMATIC_INCIDENT",
                "TXT_KEY_ESPIONAGE_CHOOSE_FRAMED_CIVILIZATION",
                "TXT_KEY_ESPIONAGE_FRAME_CIVILIZATION",
                "TXT_KEY_ESPIONAGE_DIPLOMATIC_INCIDENT_SUCCESS",
                "TXT_KEY_ESPIONAGE_DIPLOMATIC_INCIDENT_TARGET",
            }.issubset(tags)
        )
        for node in text_nodes:
            for language in ("English", "French", "German", "Italian", "Spanish"):
                self.assertTrue(child_text(node, language), (child_text(node, "Tag"), language))


if __name__ == "__main__":
    unittest.main()
