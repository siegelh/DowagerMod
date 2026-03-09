import CvUtil
import PyHelpers
import Popup as PyPopup
from CvPythonExtensions import *

PyPlayer = PyHelpers.PyPlayer
gc = CyGlobalContext()

class CvTutorial:
	def __init__(self):
		print "Re-Init the tutorial?? WTF?!"
		self.resetTutorial()
	
	def resetTutorial(self):
		print "In Reset Tutorial"
	
		self.szActiveTutorialInfoType = None
		self.activeTutorialMessage = None
		self.szScriptName = None
		self.szScriptData = None
		
		self.bCanOpenAllOtherScreens = False
		self.bCanOpenDiplomacyScreen = False
		self.bCanOpenCivicScreen = False
		self.bCanOpenReligionScreen = False
		
		self.bHideContinueButton = False
		
		self.bDisableMainInteraceMouseInput = False
		
		self.bWorkerCanBuildQuarry = False
		
		self.bWaitForReturnFirstCity = False

		self.bForceAction = False
		self.iForceActionMissionType = -1
		self.iForceActionInterfaceModeTypes = -1
		self.iForceActionCommandTypes = -1
		self.ValidPlots = tuple()

		self.bTutorialBegun = False
		
		self.bConsumeKeyboardInput = False
		
		self.bShowPlotIndicator = False
		self.iIndicatorPlotX = 0
		self.iIndicatorPlotY = 0
		self.szIndicatorColor = "COLOR_BLUE"
		
		self.bCanEndTurn = False
		
		self.bDisableBuildRoads = True
		
		self.bTutorialComplete = False
		
		self.FirstCityPlot = (33,14)
		self.FirstCity = -1
		
		self.iForcedBuildImprovement = -1
				
		self.SecondCityPlot = (34,9)
		self.SecondCity = -2
				
		self.bPromoteAvailable = False
		self.bStoneHengeAllowed = False
		self.bGoWestNotAllowed = True
		
		self.bWaitForSelectedUnit = False
		self.SelectedUnit = -1
		
		self.bWaitForUnitAction = False
		self.UnitToDoAction = -1

		self.bWaitForWorkerArriveStone = False
		self.bCanOpenCityScreen = False
		
		self.bWaitForBeginPlayerTurn = False
		
		self.bForceLionMoveNorth = True
		self.FirstLion = -1
		
		self.bIncreasedProductionRome = False

		self.bWaitForGoToAction = False
		self.bWaitForRouteToAction = False
		
		self.bCannotMouseMapInput =False
		
		self.bShowTechSplash=False
		self.bWatchCityScreen = False
							
		self.bWaitForUnitFortify = False
		self.bWaitForWorkerToBuild = False
		self.bWaitForBarracksToBuild = False
		self.bWaitForWorkerToBuildRoad = False
		self.bWaitForUnitCombat = False
		self.bShowTechChooserButton = False
		self.bLockFirstWarrior = False
		
		self.bWaitForBuildSelectionWarrior = False
		self.bWaitForBuildSelectionScout = False
		self.bWaitForBuildSelectionObelisk = False
		self.bWaitForBuildSelectionWorker = False
		self.bWaitForBuildSelectionBarracks = False
		self.bWaitForBuildSelectionSettler = False
		self.bWaitForBuildSelectionStonehenge = False
		
		self.bWaitForVillageDiscovered = False
		self.iGoodiesReceived = 0
		self.bWaitForOpenCityScreen = False
		
		self.bCanUnitAutomateExplore = False

		self.bWaitForEscapeCityScreen = False
				
		self.bWaitForWorkerToFinishBuilding = False
		self.bWaitForWarriorToFinishBuilding = False
		self.bWaitForSettlerToFinishBuilding = False
		
		self.bWaitForPromotion = False
		
		self.bWaitForMoveToSecondCity = False

		self.bWaitForResearchSelection = False
		self.bWaitForResearchDiscovered = False
		
		self.bWaitForFirstContact = False
		
		self.bCanDeleteUnit = False
		self.bCanUnitsInterfaceModeGoTo = False
		
		self.iFirstSettler = 0
		self.iFirstWarrior = 1
		self.iSecondWarrior = 2
		self.iFirstScout = 3
		self.iFirstWorker = 4
		self.iThirdWarrior = 5
		self.iSecondSettler = 6
		
		self.bLockCamera = False
		self.bNoCityScreen = False
		self.bCameraScriptOn = False
		
		self.iForcedUnit = -1
		self.iForcedBuilding = -1
		
		self.iGetRecommendedUnit = UnitTypes.NO_UNIT
		self.iGetRecommendedBuilding = BuildingTypes.NO_BUILDING
		self.iGetFirstRecommendedTech = TechTypes.NO_TECH
		self.iGetSecondRecommendedTech = TechTypes.NO_TECH
		self.iAI_chooseTech = TechTypes.NO_TECH


		self.bIsVictoryTest = False
		self.bIsPlayerResearch = True
		self.bCreateBarbarianCities = True
		self.bCreateBarbarianUnits = True
		self.bSkipResearchPopup = True
		self.bSkipProductionPopup = True
		self.bUpdateColoredPlots = True
		self.bIsActionRecommended = False
		self.bCannotHandleAction = False
		self.bCannotSelectionListMove = False
		self.bCanResearch = False
		self.iCanResearch = 0
		self.bCannotResearch = False
		self.iCannotResearch = TechTypes.NO_TECH
		self.bCanDoCivic = False
		self.bCannotDoCivic = False
		self.bCanTrain = False
		self.bCannotTrain = True
		self.bCanConstruct = False
		self.bCannotConstruct = True
		self.bCanCreate = False
		self.bCannotCreate = False
		self.bCanMaintain = False
		self.bCannotMaintain = False
		self.bAI_chooseProduction = False
		self.bAI_unitUpdate = False
		self.bCalculateScore = False
		self.bDoGold = True
		self.bDoResearch = True
		self.bDoGoody = False
		self.bDoGrowth = True
		self.bDoProduction = False
		self.bDoCulture = True
		self.bDoPlotCulture = False
		self.bDoReligion = False
		self.bDoGreatPeople = False
		self.bDoMeltdown = False
		#Ed Added
		self.bCanTrainWarriors = True
		self.bCanTrainScouts = False
		self.bCanTrainWorkers = False
		self.bCanTrainSettlers = False
		self.bCanBuildObelisk = False
		self.bCanBuildBarracks = False
		self.bCanCreateFarm = True
		self.bCanCreateCottage = False
		self.bCanCreateMine = False
		self.bCanCreateRoads = False

	def doTUTORIAL_INTRODUCTION(self):
		self.bUpdateColoredPlots = True
		self.bIsPlayerResearch = False
		self.bSkipResearchPopup = True
		self.bSkipProductionPopup = True
		self.bCannotSelectionListMove = True
		self.bCreateBarbarianUnits = True
	
	def setActiveTutorialMessage(self, activeTutorialMessage):
		self.activeTutorialMessage = activeTutorialMessage

	def doWaitForSelected(self, unitDataString):
		self.bWaitForSelectedUnit = True
		self.SelectedUnit = unitDataString

#	def doSelect(self):
#		self.bWaitForSelectedUnit = False
#		self.SelectedUnit = -1
		
	def setWaitForAction(self, ActionMissionType, ActionInterfaceModeTypes, ActionCommandTypes, scriptName, scriptData, ValidPlot):
		self.szScriptName = scriptName
		self.szScriptData = scriptData
		self.bForceAction = True
		self.iForceActionMissionType = int(ActionMissionType)
		self.iForceActionInterfaceModeTypes = int( ActionInterfaceModeTypes )
		self.iForceActionCommandTypes = int( ActionCommandTypes )
		self.ValidPlots = ValidPlot
	
	def setBuildImprovement(self, BuildType):
		self.iForcedBuildImprovement = CvUtil.findInfoTypeNum(gc.getBuildInfo, gc.getNumBuildInfos(), BuildType)

			
	def isNotAllowActionMission(self, pPlot, iActionMissionType):
		if CyInterface().getHeadSelectedUnit():
			if CyInterface().getHeadSelectedUnit().getScriptData() == self.szScriptData:
				if self.bForceAction and iActionMissionType == self.iForceActionMissionType:
					if iActionMissionType == int(MissionTypes.MISSION_MOVE_TO) and self.isValidPlot(pPlot):
						return False
					elif iActionMissionType != int(MissionTypes.MISSION_MOVE_TO):
						return False
				return True
			return False
	
	def isNotAllowedBuildType(self, iActionBuildType):
		if self.bDisableBuildRoads == True and iActionBuildType == CvUtil.findInfoTypeNum(gc.getBuildInfo, gc.getNumBuildInfos(), "BUILD_ROAD"):
			return True
		if self.iForcedBuildImprovement == -1:
			return False
		elif iActionBuildType == self.iForcedBuildImprovement:
			return False
		return True
	
	def isValidPlot(self, pPlot):
		iX = pPlot.getX()
		iY = pPlot.getY()
		numValidMovementPlots = len(self.ValidPlots)
		print ("numValidPlots %d" %(numValidMovementPlots))
		if numValidMovementPlots == 1:
			pX,pY = self.ValidPlots[0]
			if iX == pX and iY == pY:
					return True
		elif numValidMovementPlots > 1:
			for plot in self.ValidPlots:
				pX, pY = plot
				if iX == pX and iY == pY:
					return True
		return False
		
	def doErrorPopup (self, szErrorMessage):
		popup = PyPopup.PyPopup()
		popup.setBodyString(CyTranslator().getText(szErrorMessage, ()))
		popup.setSize(512,192)
		popup.setPosition(320,256)
		popup.launch()
	
	def setHighAdvisorCenter(self):
		CyCamera().SetViewPortCenter(NiPoint2(0.5, 0.4))
		
	def setIndicatorPlot ( self, iX, iY, szColor ):
		self.iIndicatorPlotX = iX
		self.iIndicatorPlotY = iY
		self.szIndicatorColor = szColor

	def showIndicatorPlot( self ):
		CyEngine().addColoredPlotAlt( self.iIndicatorPlotX, self.iIndicatorPlotY, PlotStyles.PLOT_STYLE_CIRCLE,1, self.szIndicatorColor, 1 )
		
tutorial = CvTutorial()
