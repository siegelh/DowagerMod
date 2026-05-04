#include "CvGameCoreDLL.h"
#include "CyMessageControl.h"

//
// published python interface for CyMessageControl
//

void CyMessageControlInterface()
{
	python::class_<CyMessageControl>("CyMessageControl")
		.def("sendPushOrder", &CyMessageControl::sendPushOrder, "void (int iCityID, int eOrder, int iData, bool bAlt, bool bShift, bool bCtrl)")
		.def("sendDoTask", &CyMessageControl::sendDoTask, "void (int iCity, int eTask, int iData1, int iData2, bool bOption, bool bAlt, bool bShift, bool bCtrl)")
		.def("sendTurnComplete", &CyMessageControl::sendTurnComplete, "void () - allows you to force a turn to end")
		.def("sendUpdateCivics", &CyMessageControl::sendUpdateCivics, "void (list iCivics)")
		.def("sendResearch", &CyMessageControl::sendResearch, "void (int eTech, bool bShift)")
		.def("sendPlayerOption", &CyMessageControl::sendPlayerOption, "void (int /*PlayerOptionTypes*/ eOption, bool bValue)")
		.def("sendEspionageSpendingWeightChange", &CyMessageControl::sendEspionageSpendingWeightChange, "void (int /*TeamTypes*/ eTargetTeam, int iChange)")
		.def("sendAdvancedStartAction", &CyMessageControl::sendAdvancedStartAction, "void (int /*AdvancedStartActionTypes*/ eAction, int /*PlayerTypes*/ ePlayer, int iX, int iY, int iData, bool bAdd)")
		.def("sendModNetMessage", &CyMessageControl::sendModNetMessage, "void (int iData1, int iData2, int iData3, int iData4, int iData5) - This is a NetMessage designed specifically for modders to use to make their mods Multiplayer friendly, eliminating Out-of-Sync errors. Check out 'onModNetMessage()' in CvEventManager for the callback")
		.def("sendChat", &CyMessageControl::sendChat, "void (wstring szText, int eTarget) - DowagerMod: broadcast a chat message to all players (CHATTARGET_ALL=-2), team (CHATTARGET_TEAM=-3), or specific player (player ID >= 0). Receivers get the message via CvEventManager.onChat. The sender is always the calling player.")
		.def("sendConvert", &CyMessageControl::sendConvert, "void ( int /*ReligionTypes*/ iReligion )")
		.def("sendEmpireSplit", &CyMessageControl::sendEmpireSplit, "void (int /*PlayerTypes*/ ePlayer, int iAreaId)")
		.def("GetFirstBadConnection", &CyMessageControl::GetFirstBadConnection, "int ()")
		.def("GetConnState", &CyMessageControl::GetConnState, "int (int iPlayer)")
	;
}