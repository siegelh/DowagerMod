## Sid Meier's Civilization 4
## Copyright Firaxis Games 2005
##
## Implementaion of miscellaneous game functions

import CvUtil
import CvGameUtils
import Tutorial
import CvTutorialAdvisorScreen
from CvPythonExtensions import *

# globals
gc = CyGlobalContext()

class CvTutorialGameUtils(CvGameUtils.CvGameUtils):
	"Miscellaneous game functions"
	def __init__(self):
		self.parent = CvGameUtils.CvGameUtils()
		self.tutorial = Tutorial.tutorial
		self.screen = CvTutorialAdvisorScreen.tutorialAdvisorScreen

	def isVictoryTest(self):
		if self.tutorial.bIsVictoryTest:
			return self.parent.isVictoryTest()
		return False
			
	def isPlayerResearch(self, argsList):
		ePlayer = argsList[0]
		return self.tutorial.bIsPlayerResearch

	def createBarbarianCities(self):
		return self.tutorial.bCreateBarbarianCities
		
	def createBarbarianUnits(self):
		return self.tutorial.bCreateBarbarianUnits
		
	def skipResearchPopup(self,argsList):
		ePlayer = argsList[0]
		return self.tutorial.bSkipResearchPopup

	def getFirstRecommendedTech(self,argsList):
		ePlayer = argsList[0]
		return self.tutorial.iGetFirstRecommendedTech

	def getSecondRecommendedTech(self,argsList):
		ePlayer = argsList[0]
		eFirstTech = argsList[1]
		return self.tutorial.iGetSecondRecommendedTech

	def skipProductionPopup(self,argsList):
		pCity = argsList[0]
		return self.tutorial.bSkipProductionPopup

	def showExamineCityButton(self,argsList):
		pCity = argsList[0]
		print ("checking showExamineCityButton")
		return self.tutorial.bCanOpenCityScreen		
		
	def getRecommendedUnit(self,argsList):
		pCity = argsList[0]
		return self.tutorial.iGetRecommendedUnit

	def getRecommendedBuilding(self,argsList):
		pCity = argsList[0]
		return self.tutorial.iGetRecommendedBuilding

	def updateColoredPlots(self):
		if self.tutorial.bShowPlotIndicator:
			self.tutorial.showIndicatorPlot ( )
		return self.tutorial.bUpdateColoredPlots

	def isActionRecommended(self,argsList):
		pUnit = argsList[0]
		iAction = argsList[1]

		iActionMissionType = gc.getActionInfo(iAction).getMissionType()
		iActionCommandType = gc.getActionInfo(iAction).getCommandType()
		iActionInterfaceModeType = gc.getActionInfo(iAction).getInterfaceModeType()
		iActionBuildType = gc.getActionInfo(iAction).getMissionData()
		
		if pUnit.getScriptData() == self.tutorial.szScriptData:
			if iActionMissionType != -1:
				if iActionMissionType == self.tutorial.iForceActionMissionType:
					if iActionMissionType == int ( MissionTypes.MISSION_BUILD ):
						if self.tutorial.isNotAllowedBuildType(iActionBuildType):
							return False
					return True
			if iActionCommandType != -1:
				if iActionCommandType == self.tutorial.iForceActionCommandTypes:
					return True
			if iActionInterfaceModeType != -1:
				if iActionInterfaceModeType == self.tutorial.iForceActionInterfaceModeTypes:
					return True	
		return False

	def cannotSelectionListGameNetMessage(self,argsList):
		eMessage = argsList[0]
		iData2 = argsList[1]
		iData3 = argsList[2]
		iData4 = argsList[3]
		iFlags = argsList[4]
		bAlt = argsList[5]
		bShift = argsList[6]
		
		if self.tutorial.bLockFirstWarrior:
			if CyInterface().getHeadSelectedUnit():
				if CyInterface().getHeadSelectedUnit().getScriptData() == "FIRST_WARRIOR":
					return True 

		if self.tutorial.bGoWestNotAllowed:
			if eMessage == int(GameMessageTypes.GAMEMESSAGE_PUSH_MISSION):
				if iData2 == int(MissionTypes.MISSION_MOVE_TO) and iData3 <= 19:
					self.tutorial.doErrorPopup("TXT_KEY_TUTORIAL_GO_WEST_NOT_ALLOWED")
					return True
		
		if eMessage == int(GameMessageTypes.GAMEMESSAGE_PUSH_MISSION):
			if self.tutorial.bWaitForUnitFortify:
				if iData2 == int(MissionTypes.MISSION_FORTIFY):
					self.tutorial.bWaitForUnitFortify = False
					self.screen.doNextInfo()
					return False
			if CyInterface().getHeadSelectedUnit():
				if CyInterface().getHeadSelectedUnit().getScriptData() == self.tutorial.szScriptData:
					if self.tutorial.iForceActionInterfaceModeTypes == int(InterfaceModeTypes.INTERFACEMODE_GO_TO):	
						if self.tutorial.isValidPlot(CyMap().plot(iData3,iData4)):
							if self.tutorial.bWaitForGoToAction:
								self.tutorial.bWaitForGoToAction = False
								self.screen.doNextInfo()
								return False
							return False
						self.tutorial.doErrorPopup("TXT_KEY_TUTORIAL_ERROR_GO_TO_NOT_ALLOWED")
						return True
					if self.tutorial.iForceActionInterfaceModeTypes == int(InterfaceModeTypes.INTERFACEMODE_ROUTE_TO):	
						if self.tutorial.isValidPlot(CyMap().plot(iData3,iData4)):
							if self.tutorial.bWaitForRouteToAction:
								self.tutorial.bWaitForRouteToAction = False
								self.screen.doNextInfo()
								return False
							return False
						self.tutorial.doErrorPopup("TXT_KEY_TUTORIAL_ERROR_ROUTE_TO_NOT_ALLOWED")
						return True				
			if self.tutorial.bWaitForWorkerToBuild:
				if iData2 == int(MissionTypes.MISSION_BUILD):
					return False		
		return False

	def cannotHandleAction(self,argsList):
		pPlot = argsList[0]
		iAction = argsList[1]
		bTestVisible = argsList[2]
		

		if bTestVisible:
			return False
		
		iActionMissionType = gc.getActionInfo(iAction).getMissionType()
		iActionCommandType = gc.getActionInfo(iAction).getCommandType()
		iActionInterfaceModeType = gc.getActionInfo(iAction).getInterfaceModeType()
		iActionBuildType = gc.getActionInfo(iAction).getMissionData()

		if self.tutorial.bWorkerCanBuildQuarry == False:
			if iActionMissionType == int ( MissionTypes.MISSION_BUILD ) and iActionBuildType == CvUtil.findInfoTypeNum(gc.getBuildInfo, gc.getNumBuildInfos(), "BUILD_QUARRY"):
				return True

		if self.tutorial.bLockFirstWarrior:
			if CyInterface().getHeadSelectedUnit():
				if CyInterface().getHeadSelectedUnit().getScriptData() == "FIRST_WARRIOR":
					return True 

		if iActionInterfaceModeType != -1:
			if self.tutorial.bDisableBuildRoads:
				if iActionInterfaceModeType == int(InterfaceModeTypes.INTERFACEMODE_ROUTE_TO):
					return True
			if CyInterface().getHeadSelectedUnit():
				if CyInterface().getHeadSelectedUnit().getScriptData() == self.tutorial.szScriptData:
					if self.tutorial.iForceActionInterfaceModeTypes == iActionInterfaceModeType:
						return False
					return True

#			if self.tutorial.bCanUnitsInterfaceModeGoTo == False:
#				if iActionInterfaceModeType == int(InterfaceModeTypes.INTERFACEMODE_GO_TO):
#					if self.tutorial.iForceActionInterfaceModeTypes == int(InterfaceModeTypes.INTERFACEMODE_GO_TO) and CyInterface().getHeadSelectedUnit().getScriptData() == "FIRST_SCOUT":
#						return False
#					return True
#				if iActionInterfaceModeType == int(InterfaceModeTypes.INTERFACEMODE_GO_TO_ALL):
#					return True
#				if iActionInterfaceModeType == int(InterfaceModeTypes.INTERFACEMODE_GO_TO_TYPE):
#					return True
					

		if iActionCommandType != -1:
			if self.tutorial.bPromoteAvailable == False and iActionCommandType == int(CommandTypes.COMMAND_PROMOTION):
				return True
			if self.tutorial.bCanDeleteUnit == False and iActionCommandType == int(CommandTypes.COMMAND_DELETE):
				return True
			if self.tutorial.bCanUnitAutomateExplore == False and iActionCommandType == int(CommandTypes.COMMAND_AUTOMATE):
				return True
			return False
			

		
		if iActionMissionType != -1:
			if self.tutorial.isNotAllowActionMission(pPlot,iActionMissionType):
				return True
			elif iActionMissionType == int(MissionTypes.MISSION_BUILD):
				return self.tutorial.isNotAllowedBuildType(iActionBuildType)
			return False

	def cannotDoControl(self,argsList):
		eControl = argsList[0]
		print ("eControl is %s" %(eControl))
		screens = [ControlTypes.CONTROL_CIVILOPEDIA,ControlTypes.CONTROL_FOREIGN_SCREEN,ControlTypes.CONTROL_FINANCIAL_SCREEN,ControlTypes.CONTROL_MILITARY_SCREEN,ControlTypes.CONTROL_TECH_CHOOSER,ControlTypes.CONTROL_DOMESTIC_SCREEN,ControlTypes.CONTROL_VICTORY_SCREEN,ControlTypes.CONTROL_INFO]

		if eControl != -1:
			if eControl == int(ControlTypes.CONTROL_SAVE_NORMAL) or eControl == int(ControlTypes.CONTROL_QUICK_SAVE):
				return (gc.getGame().countCivPlayersAlive() == 1 and gc.getGame().getGameState() == GameStateTypes.GAMESTATE_ON)
			elif eControl == int(ControlTypes.CONTROL_SELECTCAPITAL) and self.tutorial.bCanOpenCityScreen == False:
				self.tutorial.doErrorPopup("TXT_KEY_TUTORIAL_ERROR_CANNOT_OPEN_CITY")
				return True	
			elif eControl == int(ControlTypes.CONTROL_ENDTURN) and self.tutorial.bCanEndTurn == False:
				self.tutorial.doErrorPopup("TXT_KEY_TUTORIAL_ERROR_END_TURN_NOT_ALLOWED")
				return True
			elif eControl == int(ControlTypes.CONTROL_ENDTURN_ALT) and self.tutorial.bCanEndTurn == False:
				self.tutorial.doErrorPopup("TXT_KEY_TUTORIAL_ERROR_END_TURN_NOT_ALLOWED")
				return True
			elif eControl == int(ControlTypes.CONTROL_FORCEENDTURN) and self.tutorial.bCanEndTurn == False:
				self.tutorial.doErrorPopup("TXT_KEY_TUTORIAL_ERROR_END_TURN_NOT_ALLOWED")
				return True
			elif eControl == int(ControlTypes.CONTROL_RELIGION_SCREEN) and self.tutorial.bCanOpenReligionScreen == False:
				self.tutorial.doErrorPopup("TXT_KEY_TUTORIAL_RELIGION_SCREEN_NOT_ALLOWED")
				return True
			elif eControl == int(ControlTypes.CONTROL_CIVICS_SCREEN) and self.tutorial.bCanOpenCivicScreen == False:
				self.tutorial.doErrorPopup("TXT_KEY_TUTORIAL_CIVIC_SCREEN_NOT_ALLOWED")
				return True
			elif eControl == int(ControlTypes.CONTROL_DIPLOMACY) and self.tutorial.bCanOpenDiplomacyScreen == False:
				self.tutorial.doErrorPopup("TXT_KEY_TUTORIAL_DIPLOMACY_SCREEN_NOT_ALLOWED")
				return True
			elif self.tutorial.bCanOpenAllOtherScreens == False:
				for i in screens:
					if int(i) == eControl:
						self.tutorial.doErrorPopup("TXT_KEY_TUTORIAL_OTHER_SCREEN_NOT_ALLOWED")
						return True

			return False

		return False
	
	def cannotSelectionListMove(self,argsList):
		pPlot = argsList[0]
		bAlt = argsList[1]
		bShift = argsList[2]
		bCtrl = argsList[3]

		if self.tutorial.bLockFirstWarrior:
			if CyInterface().getHeadSelectedUnit():
				if CyInterface().getHeadSelectedUnit().getScriptData() == "FIRST_WARRIOR":
					return True 		
		
		if self.tutorial.bGoWestNotAllowed and pPlot.getX() <= 19:
			self.tutorial.doErrorPopup("TXT_KEY_TUTORIAL_GO_WEST_NOT_ALLOWED")
			return True
		
		if self.tutorial.isNotAllowActionMission(pPlot,int(MissionTypes.MISSION_MOVE_TO)):
			self.tutorial.doErrorPopup("TXT_KEY_TUTORIAL_ERROR_MOVE_NOT_ALLOWED")
			return True
		else:
			if CyInterface().getHeadSelectedUnit():
				if self.tutorial.bWaitForUnitAction and CyInterface().getHeadSelectedUnit().getScriptData() == self.tutorial.szScriptData:
					self.tutorial.bWaitForUnitAction = False
					print ("doNextInfo cannotSelectionListMove1")
					self.screen.doNextInfo()
			return False

	def canResearch(self,argsList):
		ePlayer = argsList[0]
		eTech = argsList[1]
		bTrade = argsList[2]
		return self.tutorial.bCanResearch

	def cannotResearch(self,argsList):
		ePlayer = argsList[0]
		eTech = argsList[1]
		bTrade = argsList[2]

		if self.tutorial.iCannotResearch:
			if ePlayer == 0 and eTech != self.tutorial.iCannotResearch:
				return True
			elif ePlayer == 1 and eTech == self.tutorial.iCannotResearch:
				return True
			return False		
		
		return self.tutorial.bCannotResearch

	def canDoCivic(self,argsList):
		ePlayer = argsList[0]
		eCivic = argsList[1]
		return self.tutorial.bCanDoCivic

	def cannotDoCivic(self,argsList):
		ePlayer = argsList[0]
		eCivic = argsList[1]
		return self.tutorial.bCannotDoCivic

	def canTrain(self,argsList):
		pCity = argsList[0]
		eUnit = argsList[1]
		bContinue = argsList[2]
		bTestVisible = argsList[3]

		return self.tutorial.bCanTrain

	def cannotTrain(self,argsList):
		pCity = argsList[0]
		eUnit = argsList[1]
		bContinue = argsList[2]
		bTestVisible = argsList[3]
		
		if self.tutorial.iForcedUnit == eUnit:
			return False
			
		if bTestVisible:
			return False

		return self.tutorial.bCannotTrain

	def canConstruct(self,argsList):
		pCity = argsList[0]
		eBuilding = argsList[1]
		bContinue = argsList[2]
		bTestVisible = argsList[3]
		bIgnoreCost = argsList[4]
		return self.tutorial.bCanConstruct

	def cannotConstruct(self,argsList):
		pCity = argsList[0]
		eBuilding = argsList[1]
		bContinue = argsList[2]
		bTestVisible = argsList[3]
		bIgnoreCost = argsList[4]
		
		if self.tutorial.bStoneHengeAllowed == False:
			if eBuilding == CvUtil.findInfoTypeNum(gc.getBuildingInfo,gc.getNumBuildingInfos(),"BUILDING_STONEHENGE"):
				return True
#		if bIgnoreCost:
#			return False
		if bTestVisible:
			return False
		if self.tutorial.iForcedBuilding == eBuilding:
			return False
	
		return self.tutorial.bCannotConstruct

	def canCreate(self,argsList):
		pCity = argsList[0]
		eProject = argsList[1]
		bContinue = argsList[2]
		bTestVisible = argsList[3]
		return self.tutorial.bCanCreate

	def cannotCreate(self,argsList):
		pCity = argsList[0]
		eProject = argsList[1]
		bContinue = argsList[2]
		bTestVisible = argsList[3]
		return self.tutorial.bCannotCreate

	def canMaintain(self,argsList):
		pCity = argsList[0]
		eProcess = argsList[1]
		bContinue = argsList[2]
		return self.tutorial.bCanMaintain

	def cannotMaintain(self,argsList):
		pCity = argsList[0]
		eProcess = argsList[1]
		bContinue = argsList[2]
		return self.tutorial.bCannotMaintain

	def AI_chooseTech(self,argsList):
		ePlayer = argsList[0]
		bFree = argsList[1]
		return self.tutorial.iAI_chooseTech

	def AI_chooseProduction(self,argsList):
		pCity = argsList[0]
		return self.tutorial.bAI_chooseProduction

	def AI_unitUpdate(self,argsList):
		pUnit = argsList[0]
		if (self.tutorial.bForceLionMoveNorth == True and self.__doLionMove(pUnit)):
			return True
		return False

	def calculateScore(self,argsList):
		ePlayer = argsList[0]
		if not self.tutorial.bCalculateScore:
			return CyGlobalContext().getPlayer(ePlayer).getAssets()

	def doGold(self,argsList):
		ePlayer = argsList[0]
		return self.tutorial.bDoGold

	def doResearch(self,argsList):
		ePlayer = argsList[0]
		return self.tutorial.bDoResearch

	def doGoody(self,argsList):
		ePlayer = argsList[0]
		pPlot = argsList[1]
		pUnit = argsList[2]

		if self.tutorial.bWaitForVillageDiscovered == True:
			self.tutorial.bWaitForVillageDiscovered = False
			self.tutorial.iGoodiesReceived += 1
			if self.tutorial.iGoodiesReceived == 1:
				CyMap().plot(25,18).setRevealed(CyGame().getActiveTeam(),1,0,TeamTypes.NO_TEAM)
				CyMap().plot(25,16).setRevealed(CyGame().getActiveTeam(),1,0,TeamTypes.NO_TEAM)
				CyMap().plot(25,17).setRevealed(CyGame().getActiveTeam(),1,0,TeamTypes.NO_TEAM)
				CyMap().plot(25,19).setRevealed(CyGame().getActiveTeam(),1,0,TeamTypes.NO_TEAM)
				CyMap().plot(25,20).setRevealed(CyGame().getActiveTeam(),1,0,TeamTypes.NO_TEAM)
				CyMap().plot(26,16).setRevealed(CyGame().getActiveTeam(),1,0,TeamTypes.NO_TEAM)
				CyMap().plot(26,17).setRevealed(CyGame().getActiveTeam(),1,0,TeamTypes.NO_TEAM)
				CyMap().plot(26,18).setRevealed(CyGame().getActiveTeam(),1,0,TeamTypes.NO_TEAM)
				CyMap().plot(26,19).setRevealed(CyGame().getActiveTeam(),1,0,TeamTypes.NO_TEAM)
				CyMap().plot(26,20).setRevealed(CyGame().getActiveTeam(),1,0,TeamTypes.NO_TEAM)
				CyMap().plot(24,16).setRevealed(CyGame().getActiveTeam(),1,0,TeamTypes.NO_TEAM)
				CyMap().plot(24,17).setRevealed(CyGame().getActiveTeam(),1,0,TeamTypes.NO_TEAM)
				CyMap().plot(24,18).setRevealed(CyGame().getActiveTeam(),1,0,TeamTypes.NO_TEAM)
				CyMap().plot(24,19).setRevealed(CyGame().getActiveTeam(),1,0,TeamTypes.NO_TEAM)
				CyMap().plot(24,20).setRevealed(CyGame().getActiveTeam(),1,0,TeamTypes.NO_TEAM)
				CyMap().plot(25,15).setRevealed(CyGame().getActiveTeam(),1,0,TeamTypes.NO_TEAM)
				pPlot.setImprovementType( int(ImprovementTypes.NO_IMPROVEMENT) )
				print ("doNextInfo doGoody")
				self.screen.doNextInfo()
			if self.tutorial.iGoodiesReceived == 2:
				gc.getPlayer(gc.getGame().getActivePlayer()).setGold(100)
				pPlot.setImprovementType( int(ImprovementTypes.NO_IMPROVEMENT) )
				print ("doNextInfo doGoody2")
				self.screen.doNextInfo()
			return True
		return self.tutorial.bDoGoody

	def doGrowth(self,argsList):
		pCity = argsList[0]
		return self.tutorial.bDoGrowth

	def doProduction(self,argsList):
		pCity = argsList[0]
		return self.tutorial.bDoProduction

	def doCulture(self,argsList):
		pCity = argsList[0]
		return self.tutorial.bDoCulture

	def doPlotCulture(self,argsList):
		pCity = argsList[0]
		bUpdate = argsList[1]
		return self.tutorial.bDoPlotCulture

	def doReligion(self,argsList):
		pCity = argsList[0]
		return self.tutorial.bDoReligion

	def doGreatPeople(self,argsList):
		pCity = argsList[0]
		return self.tutorial.bDoGreatPeople

	def doMeltdown(self,argsList):
		pCity = argsList[0]
		return self.tutorial.bDoMeltdown 

	def __doLionMove(self,unit):
		player = gc.getPlayer(unit.getOwner())
		if ( player.isBarbarian()):
			self.__doMoveUnit( (unit, MissionTypes.MISSION_MOVE_TO, unit.getX(), (unit.getY()+1), 0, True, True, MissionAITypes.NO_MISSIONAI, unit.plot(), unit) )
			return True

	def __doMoveUnit(self,argsList):
		pUnit, MissionType, unitX, unitY, iFlags, bAppend, bManual, MissionAITypes, pPlotAIMission, pUnitMissionAI = argsList
		pUnit.getGroup().pushMission( MissionType, unitX, unitY, iFlags, bAppend, bManual, MissionAITypes, pPlotAIMission, pUnitMissionAI )
		
	def showTechChooserButton(self,argsList):
		ePlayer = argsList[0]
		return self.tutorial.bShowTechChooserButton