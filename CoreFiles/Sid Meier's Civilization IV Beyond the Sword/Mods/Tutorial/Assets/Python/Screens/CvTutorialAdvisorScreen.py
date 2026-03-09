import CvScreenEnums
import ScreenInput
import CvAdvisorScreen
import Tutorial
import CvUtil
import PyHelpers
from CvPythonExtensions import *

# globals
gc = CyGlobalContext()
TEXT_AREA_ADVISOR = 0
TEXT_AREA_DEBUG = 1

TUTORIAL_ADVISOR_SCREEN_ID = 2000

ArtFileMgr = CyArtFileMgr()

class CvTutorialAdvisorScreen(CvAdvisorScreen.CvAdvisorScreen):	
	
	advisorButtons={
#		'Previous' : ("Previous","Previous","",255,160,120,30,WidgetTypes.WIDGET_GENERAL,-1,-1,ButtonStyles.BUTTON_STYLE_STANDARD),
		'Continue':("Continue","Continue","",690,164,120,30,WidgetTypes.WIDGET_GENERAL,-1,-1,ButtonStyles.BUTTON_STYLE_STANDARD),
		'End Tutorial':("End Tutorial","End Tutorial","",400,164,120,30,WidgetTypes.WIDGET_GENERAL,-1,-1,ButtonStyles.BUTTON_STYLE_STANDARD),
#		'Reset':("Reset","Reset","",750,160,120,30,WidgetTypes.WIDGET_GENERAL,-1,-1,ButtonStyles.BUTTON_STYLE_STANDARD),
		}
	FirstTutorialInfoType = "TUTORIAL_INTRODUCTION"
	
	WIDGET_ID = "TutorialAdvisorWidget"
	
	def __init__(self):
		CvAdvisorScreen.CvAdvisorScreen.__init__(self)
		self.setScreenValues("TutorialAdvisorScreen", TUTORIAL_ADVISOR_SCREEN_ID)
		self.parent = CvAdvisorScreen.CvAdvisorScreen
		self.tutorial = Tutorial.tutorial
		self.nWidgetCount = 0
		self.resetTutorialScreen()
		self.iBackgroundX = 120
		self.iBackgroundY = 48
		
	def resetTutorialScreen(self):
		self.bPassInput = True
		self.bWaitToContinue = False
		self.bWaitForRecenterToContinue = False
		self.__iMessageCount = 0
		self.__iCompletedTutorialInfos = 0
		self.__l_TutorialInfos = []
		self.resetActiveTutorialInfo()
		
	def startTutorial(self, tutorialInfo):
		self.tutorial.resetTutorial()
		self.resetTutorialScreen()
		ContinueButtonText = CyTranslator().getText("TXT_KEY_SCREEN_CONTINUE",())
		EndButtonText = CyTranslator().getText("TXT_KEY_SCREEN_END_TUTORIAL",())
		self.advisorButtons['Continue'] = ("Continue", ContinueButtonText, "", 690,164,120,30,WidgetTypes.WIDGET_GENERAL,-1,-1,ButtonStyles.BUTTON_STYLE_STANDARD)
		self.advisorButtons['End Tutorial'] = ("End Tutorial", EndButtonText, "", 400,164,120,30,WidgetTypes.WIDGET_GENERAL,-1,-1,ButtonStyles.BUTTON_STYLE_STANDARD)
		self.clearScreen()
		self.interfaceScreen()
		self.setLeaderheadAdvisor( 0 ) # ADVISOR_GROWTH
		if tutorialInfo:
			self.processTutorialInfoByType(tutorialInfo)
		else:
			self.processTutorialInfoByType(self.FirstTutorialInfoType)
	
	def doNextInfo(self):
		self.__doEndTutorialInfo()
		
	def __doBeginTutorialInfo(self):
		print "__doBeginTutorialInfo -> %s" %self.activeTutorialInfo.getType()
		tutorialInfoType = self.activeTutorialInfo.getType()	
#		if tutorialInfoType == "TUTORIAL_INTRODUCTION":
#			self.tutorial.doWaitForSelected("SETTLER_1")
	def __doEndTutorialInfo(self):
		print "__doEndTutorialInfo -> %s" %self.activeTutorialInfo.getType()
		tutorialInfoType = self.activeTutorialInfo.getType()	
#		if tutorialInfoType == "TUTORIAL_FIRST_MOVEMENT":
#			self.tutorial.setWaitForAction(MissionTypes.MISSION_MOVE_TO, "", "", self.tutorial.FirstCityPlot)
#			return self.processTutorialInfoByType("TUTORIAL_FIRST_FOUND_CITY")
#		elif tutorialInfoType == "TUTORIAL_FIRST_":
#			self.tutorial.setWaitForAction(MissionTypes.MISSION_FOUND, "", "", self.tutorial.FirstCityPlot)
		# info is complete, reset activeTutorialInfo and MessageCount - but FIRST, get NextTutorialInfoType
		nextTutorialInfoType = self.activeTutorialInfo.getNextTutorialInfoType()
		self.doTutorialInfoComplete(self.activeTutorialInfo.getType())
		self.resetActiveTutorialInfo()
		# start next message if there is one
		if nextTutorialInfoType != "NONE":
			self.processTutorialInfoByType(nextTutorialInfoType)
	def doScript(self, scriptName):
		
		xResolution = self.getScreen().getXResolution()
		yResolution = self.getScreen().getYResolution()
		
		iWarrior = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),"UNIT_WARRIOR")
		iScout = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),"UNIT_SCOUT")
		iObelisk = CvUtil.findInfoTypeNum(gc.getBuildingInfo,gc.getNumBuildingInfos(),"BUILDING_OBELISK")
		iWorker = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),"UNIT_WORKER")
		iBarracks = CvUtil.findInfoTypeNum(gc.getBuildingInfo,gc.getNumBuildingInfos(),"BUILDING_BARRACKS")
		iSettler = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),"UNIT_SETTLER")
		iStonehenge = CvUtil.findInfoTypeNum(gc.getBuildingInfo,gc.getNumBuildingInfos(),"BUILDING_STONEHENGE")

		if scriptName == "TOP":
			return
		#Interface Scripts		
		elif scriptName == "HIDE_INTERFACE_ALL":
			CyInterface().setShowInterface(InterfaceVisibility.INTERFACE_HIDE_ALL)
		elif scriptName == "MINIMAL_INTERFACE":
			CyInterface().setShowInterface(InterfaceVisibility.INTERFACE_HIDE)
		elif scriptName == "SHOW_INTERFACE_ALL":
			CyInterface().setShowInterface(InterfaceVisibility.INTERFACE_SHOW)

		#Advisor Screen Scripts   **** these scripts must be called last since scripts following them don't run****
		elif scriptName == "HIDE_ADVISOR_OK_BUTTON":
			self.tutorial.bHideContinueButton = True	
			self.doHideOKButton()
		elif scriptName == "SHOW_ALL_ADVISOR_BUTTONS":
			self.tutorial.bHideContinueButton = False
			self.doShowAllButtons()	
		elif scriptName == "SHOW_END_TUTORIAL_BUTTON":
			self.tutorial.bHideContinueButton = True	
			self.doShowEndTutorialButtons()
		elif scriptName == "HIDE_END_TUTORIAL_BUTTON":
			self.doHideEndTutorialButton()

		#Camera Scripts
		elif scriptName == "CAMERA_RESET_ALL":
			CyCamera().ResetZoom()

		elif scriptName == "CAMERA_FOCUS_GAME_START_BLACKNESS":
			CyCamera().SimpleLookAt(NiPoint3(45.779320,-1448.957397,1654.818970), NiPoint3(0,0,0))
		elif scriptName == "CAMERA_FOCUS_UNIT_FLAG":
			CyCamera().SimpleLookAt( NiPoint3( 2188.282715, -42.710007, 467.137817 ),NiPoint3( 2151.465332, 765.179077, 49.500000))
		elif scriptName == "CAMERA_FOCUS_FIRST_SETTLE_PLOT_INDICATOR":
			CyCamera().SimpleLookAt( NiPoint3 ( 2301.432373, -1106.147461, 1363.551636), NiPoint3( 2246.625000, 628.593750, 121.599998 ) )


		elif scriptName == "CAMERA_NORMAL_FIRST_SETTLER":
			CyCamera().LookAtUnit( PyHelpers.PyPlayer( gc.getGame().getActivePlayer() ).getUnitByScriptData( "FIRST_SETTLER" ) )
		elif scriptName == "CAMERA_FOCUS_FIRST_SETTLER":
			CyCamera().SimpleLookAt(NiPoint3( 2815.484,296.344,411.070),self.centerCameraFocus(PyHelpers.PyPlayer(gc.getGame().getActivePlayer()).getUnitByScriptData("FIRST_SETTLER").plot()))
		elif scriptName == "CAMERA_RESET_FIRST_SETTLER":
			CyCamera().SimpleLookAt(NiPoint3(2292.250488,-529.876099,824.148438),self.centerCameraFocus(PyHelpers.PyPlayer(gc.getGame().getActivePlayer()).getUnitByScriptData("FIRST_SETTLER").plot()))

		elif scriptName == "CAMERA_FOCUS_FIRST_WARRIOR":
			CyCamera().SimpleLookAt( NiPoint3 ( 1631.293213, -63.911133, 632.493896 ),self.centerCameraFocus( PyHelpers.PyPlayer( gc.getGame().getActivePlayer() ).getUnitByScriptData("FIRST_WARRIOR").plot() ) )
		elif scriptName == "CAMERA_NORMAL_FIRST_WARRIOR":
			CyCamera().LookAtUnit( PyHelpers.PyPlayer( gc.getGame().getActivePlayer() ).getUnitByScriptData( "FIRST_WARRIOR" ) )
		elif scriptName == "CAMERA_RESET_FIRST_WARRIOR":
			CyCamera().SimpleLookAt( NiPoint3( 2292.250488, -529.876099, 824.148438 ),self.centerCameraFocus(PyHelpers.PyPlayer(gc.getGame().getActivePlayer()).getUnitByScriptData("FIRST_WARRIOR").plot()))

		elif scriptName == "CAMERA_FOCUS_LION":
			CyCamera().SimpleLookAt( NiPoint3( 2160.480957, 511.886169, 433.550110 ),NiPoint3( 2842.443359, 78.288330, 49.500000))

		elif scriptName == "CAMERA_FOCUS_FIRST_CITY":
			CyCamera().SimpleLookAt( NiPoint3( 3245.336182, -23.306644, 567.403564), NiPoint3( 2374.620605, 478.554016, 49.500000 ) )

		elif scriptName == "CAMERA_FOCUS_FIRST_TRIBAL_VILLAGE":
			CyCamera().SimpleLookAt( NiPoint3 ( 2211.455566, 367.872192, 415.453064), NiPoint3( 1498.852539, 982.693726, 49.500000 ) )
		elif scriptName == "CAMERA_SCOUT_FAR_OFF_FIRST_TRIBAL":
			CyCamera().SimpleLookAt( NiPoint3 ( 3330.408936, -92.627449, 437.059082), NiPoint3( 2176.128662, 624.421265, 49.500000 ) )
		elif scriptName == "CAMERA_SCOUT_FIRST_TRIBAL_PULLED_BACK":
			CyCamera().SimpleLookAt( NiPoint3 ( 1837.916260, -246.860291, 4111.348633), NiPoint3( 1849.247559, 593.011108, 49.499756 ) )

		elif scriptName == "CAMERA_SCOUT_FAR_OFF_SECOND_TRIBAL":
			CyCamera().SimpleLookAt( NiPoint3 ( 2328.032227, 616.066772, 594.285889), NiPoint3( 1047.814697, 1148.103760, 49.500000 ) )

		elif scriptName == "CAMERA_NORMAL_FIRST_SCOUT":
			CyCamera().LookAtUnit( PyHelpers.PyPlayer( gc.getGame().getActivePlayer() ).getUnitByScriptData( "FIRST_SCOUT" ) )

		elif scriptName == "CAMERA_RESET_FIRST_CITY":
			CyCamera().JustLookAtPlot(CyMap().plot(32,14)) #SimpleLookAt(NiPoint3(2292.250488,-529.876099,824.148438),self.centerCameraFocusOnPlot(CyMap().plot(32,14)))

		elif scriptName == "CAMERA_FOCUS_ON_FARM_LOC":
			CyCamera().SimpleLookAt( NiPoint3 ( 3081.707031, -559.818787, 665.521912), NiPoint3( 2244.266357, 240.791351, 49.499992 ) )
		elif scriptName == "CAMERA_FOCUS_ON_COTTAGE_LOC":
			CyCamera().SimpleLookAt( NiPoint3 ( 1095.563721, -291.925354, 835.348999), NiPoint3( 2182.654785, 474.229187, 49.500000 ) )
		elif scriptName == "CAMERA_FOCUS_ON_MINE_LOC":
			CyCamera().SimpleLookAt( NiPoint3 ( 1319.161133, 275.170929, 773.606262), NiPoint3( 2320.789063, 701.790894, 49.500000 ) )

		elif scriptName == "CAMERA_SECOND_SETTLER_BLUE_CIRCLE":
			CyCamera().SimpleLookAt( NiPoint3 ( 2394.521484, -2199.017334, 4431.910156), NiPoint3( 2342.834473, -87.778557, 49.499992 ) )

		elif scriptName == "CAMERA_FOCUS_SECOND_CITY":
			CyCamera().SimpleLookAt( NiPoint3 ( 3581.761963, -1392.432251, 755.416687), NiPoint3( 2589.805664, -469.913513, 49.500008 ) )

		elif scriptName == "CAMERA_FOCUS_STONE":
			CyCamera().SimpleLookAt( NiPoint3 ( 1676.681396, -1113.909668, 667.913940), NiPoint3( 2429.639160, -196.660477, 49.500008 ) )

		elif scriptName == "CAMERA_FOCUS_ROME_QUARRY":
			CyCamera().SimpleLookAt( NiPoint3 ( 2566.888672, -2178.979004, 2573.208984), NiPoint3( 2482.364746, 39.256107, 49.500000 ) )

		elif scriptName == "CAMERA_FOCUS_WORKER":
			CyCamera().SimpleLookAt(NiPoint3(2371.228,-23.4439,470.1647),self.centerCameraFocus(PyHelpers.PyPlayer(gc.getGame().getActivePlayer()).getUnitByScriptData("FIRST_WORKER").plot()))
		elif scriptName == "CAMERA_RESET_WORKER":
			CyCamera().SimpleLookAt(NiPoint3(2292.250488,-529.876099,824.148438),self.centerCameraFocus(PyHelpers.PyPlayer(gc.getGame().getActivePlayer()).getUnitByScriptData("FIRST_WORKER").plot()))
		elif scriptName == "CAMERA_FOCUS_SECOND_WARRIOR":
			CyCamera().SimpleLookAt(NiPoint3(1663.343,-35.9953,703.4886),self.centerCameraFocus(PyHelpers.PyPlayer(gc.getGame().getActivePlayer()).getUnitByScriptData("SECOND_WARRIOR").plot()))
		elif scriptName == "CAMERA_RESET_SECOND_WARRIOR":
			CyCamera().SimpleLookAt(NiPoint3(2292.250488,-529.876099,824.148438),self.centerCameraFocus(PyHelpers.PyPlayer(gc.getGame().getActivePlayer()).getUnitByScriptData("SECOND_WARRIOR").plot()))
		elif scriptName == "CAMERA_FOCUS_SECOND_SETTLER":
			CyCamera().SimpleLookAt(NiPoint3(1663.343,-35.9953,703.4886),self.centerCameraFocus(PyHelpers.PyPlayer(gc.getGame().getActivePlayer()).getUnitByScriptData("SECOND_SETTLER").plot()))
		elif scriptName == "CAMERA_RESET_SECOND_SETTLER":
			CyCamera().SimpleLookAt(NiPoint3(2292.250488,-529.876099,824.148438),self.centerCameraFocus(PyHelpers.PyPlayer(gc.getGame().getActivePlayer()).getUnitByScriptData("SECOND_SETTLER").plot()))
	

		#Indicator Scripts
		elif scriptName == "FIRST_CITY_PLOT_INDICATOR":
			self.tutorial.setIndicatorPlot ( 33, 14, "COLOR_BLUE" )
			self.tutorial.showIndicatorPlot ( )
			self.tutorial.bShowPlotIndicator = True
		elif scriptName == "COTTAGE_PLOT_INDICATOR":
			self.tutorial.setIndicatorPlot ( 32, 14, "COLOR_BLUE" )
			self.tutorial.showIndicatorPlot ( )
			self.tutorial.bShowPlotIndicator = True
		elif scriptName == "MINE_PLOT_INDICATOR":
			self.tutorial.setIndicatorPlot ( 32, 15, "COLOR_BLUE" )
			self.tutorial.showIndicatorPlot ( )
			self.tutorial.bShowPlotIndicator = True
		elif scriptName == "FARM_PLOT_INDICATOR":
			self.tutorial.setIndicatorPlot ( 32, 13, "COLOR_BLUE" )
			self.tutorial.showIndicatorPlot ( )
			self.tutorial.bShowPlotIndicator = True
		elif scriptName == "QUARRY_PLOT_INDICATOR":
			self.tutorial.setIndicatorPlot ( 33, 10, "COLOR_BLUE" )
			self.tutorial.showIndicatorPlot ( )
			self.tutorial.bShowPlotIndicator = True
		elif scriptName == "SECOND_CITY_PLOT_INDICATOR":
			self.tutorial.setIndicatorPlot ( 34, 9, "COLOR_BLUE" )
			self.tutorial.showIndicatorPlot ( )
			self.tutorial.bShowPlotIndicator = True
		elif scriptName == "DISABLE_PLOT_INDICATOR":
			self.tutorial.bShowPlotIndicator = False

		
		#Screen Changes			
		elif scriptName == "HIGH_ADVISOR_SCREEN":
			self.setBackgroundPosition(120,48)	
			self.iBackgroundX = 120
			self.iBackgroundY = 48
			self.reprocessMessage(self.__iMessageCount)
			self.tutorial.setHighAdvisorCenter()
			self.setLeaderheadAdvisor( 0 )
			self.doHideEndTutorialButton()
		elif scriptName == "MID_ADVISOR_SCREEN":
			self.setBackgroundPosition(120,352)
			self.iBackgroundX = 120
			self.iBackgroundY = 352
			self.reprocessMessage(self.__iMessageCount)
			self.setLeaderheadAdvisor( 0 )
			self.doHideEndTutorialButton()
		elif scriptName == "LOW_ADVISOR_SCREEN":
			self.setBackgroundPosition(120,512)
			self.iBackgroundX = 120
			self.iBackgroundY = 512
			self.reprocessMessage(self.__iMessageCount)
			self.setLeaderheadAdvisor( 0 )
			self.doHideEndTutorialButton()
		elif scriptName == "HIDE_HIGHLIGHT":
			self.hideItem("TutorialHighlight")
		elif scriptName == "HIGHLIGHT_GROWTH_PRODUCTION":
			self.highlightArea (256, 32, xResolution - 512, 128)
		elif scriptName == "HIGHLIGHT_TREASURY":
			self.highlightArea (0, 0, 256, 160)
		elif scriptName == "HIGHLIGHT_CULTURE_BAR":
			self.highlightArea (0, yResolution - 256, 256, 128)
		elif scriptName == "HIGHLIGHT_PRODUCTION_QUE":
			self.highlightArea (0, yResolution - 160, 288, 160)
		elif scriptName == "HIGHLIGHT_PRODUCTION_LIST":
			self.highlightArea (256, yResolution - 160, xResolution - 512, 160)
		elif scriptName == "HIGHLIGHT_RESOURCE_LIST":
			self.highlightArea (xResolution - 256, 64, 256, yResolution - 512)
		elif scriptName == "HIGHLIGHT_BUILDING_LIST":
			self.highlightArea (0, 240, 256, yResolution - 480)
		elif scriptName == "HIGHLIGHT_SPECIALIST":
			self.highlightArea (xResolution - 256, yResolution - 480, 256, 288)		
		elif scriptName == "HIGHLIGHT_TILE_MANAGER":
			self.highlightArea (256, 272, xResolution - 512, yResolution - 400)
		elif scriptName == "HIGHLIGHT_CITY_GOVERNOR":
			self.highlightArea (xResolution - 304, yResolution - 144, 96, 144)

		#Rule Scripts			
		elif scriptName == "RULE_START_CULTURE":
			self.tutorial.bDoCulture = False
		elif scriptName == "RULE_START_GROWTH":
			self.tutorial.bDoGrowth = False
		elif scriptName == "RULE_START_GOLD":
			self.tutorial.bDoGold = False
		elif scriptName == "RULE_START_RESEARCH":
			self.tutorial.bDoResearch = False
		elif scriptName == "RULE_DISABLE_RESEARCH":
			self.tutorial.bDoResearch = True
		elif scriptName == "RULE_START_BARBARIANS":
			self.tutorial.bCreateBarbarianCities = False
			self.tutorial.bCreateBarbarianUnits = False
		elif scriptName == "RULE_START_VICTORY_TEST":
			self.tutorial.bIsVictoryTest = True
		elif scriptName == "RULE_ENABLE_UNIT_DELETE":
			self.tutorial.bCanDeleteUnit = True
		elif scriptName == "RULE_ENABLE_AUTOMATE_EXPLORE":
			self.tutorial.bCanUnitAutomateExplore = True
		elif scriptName == "RULE_ENABLE_INTERFACE_GO_TO_FOR_ALL_UNITS":			
			self.tutorial.bCanUnitsInterfaceModeGoTo = True
		elif scriptName == "RULE_ENABLE_OPEN_CITY_SCREEN":
			self.tutorial.bCanOpenCityScreen = True	
		elif scriptName == "RULE_PLAYER_CAN_BUILD_WHAT_THEY_WANT":
			self.tutorial.bCannotTrain = False
			self.tutorial.bCannotConstruct = False
		elif scriptName == "RULE_UNITS_CAN_BE_PROMOTED":			
			self.tutorial.bPromoteAvailable = True
		elif scriptName == "RULE_ENABLE_TECH_SPLASH_SCREEN":			
			self.tutorial.bShowTechSplash = True


		#City Train/Build Scripts
		elif scriptName == "RULE_CAN_TRAIN_WARRIORS":
			self.tutorial.bCanTrainWarriors = True
		elif scriptName == "RULE_CAN_NOT_TRAIN_WARRIORS":
			self.tutorial.bCanTrainWarriors = False			
		elif scriptName == "RULE_CAN_TRAIN_SCOUTS":
			self.tutorial.bCanTrainScouts = True
		elif scriptName == "RULE_CAN_NOT_TRAIN_SCOUTS":
			self.tutorial.bCanTrainScouts = False
		elif scriptName == "RULE_CAN_TRAIN_WORKERS":
			self.tutorial.bCanTrainWorkers = True
		elif scriptName == "RULE_CAN_NOT_TRAIN_WORKERS":
			self.tutorial.bCanTrainWorkers = False		
		elif scriptName == "RULE_CAN_TRAIN_SETTLERS":
			self.tutorial.bCanTrainSettlers = True
		elif scriptName == "RULE_CAN_NOT_TRAIN_SETTLERS":
			self.tutorial.bCanTrainSettlers = False				
		elif scriptName == "RULE_CAN_BUILD_OBELISK":
			self.tutorial.bCanBuildObelisk = True
		elif scriptName == "RULE_CAN_NOT_BUILD_OBELISK":
			self.tutorial.bCanBuildObelisk = False
		elif scriptName == "RULE_CAN_BUILD_BARRACKS":
			self.tutorial.bCanBuildBarracks = True
		elif scriptName == "RULE_CAN_NOT_BUILD_BARRACKS":
			self.tutorial.bCanBuildBarracks = False

		#Actions Allowed
		elif scriptName == "RULE_CAN_CREATE_FARM":
			self.tutorial.bCanCreateFarm = True
		elif scriptName == "RULE_CAN_NOT_CREATE_FARM":
			self.tutorial.bCanCreateFarm = False
		elif scriptName == "RULE_CAN_CREATE_COTTAGE":
			self.tutorial.bCanCreateCottage = True
		elif scriptName == "RULE_CAN_NOT_CREATE_COTTAGE":
			self.tutorial.bCanCreateCottage = False
		elif scriptName == "RULE_CAN_CREATE_MINE":
			self.tutorial.bCanCreateMine = True
		elif scriptName == "RULE_CAN_NOT_CREATE_MINE":
			self.tutorial.bCanCreateMine = False
		elif scriptName == "RULE_CAN_CREATE_ROADS":
			self.tutorial.bCanCreateRoads = True
		elif scriptName == "RULE_CAN_NOT_CREATE_ROADS":
			self.tutorial.bCanCreateRoads = False
		elif scriptName == "RULE_ENABLE_PRODUCTION_POPUPS":
			self.tutorial.bSkipProductionPopup = False
		elif scriptName == "RULE_DISABLE_PRODUCTION_POPUPS":
			self.tutorial.bSkipProductionPopup = True
		elif scriptName == "RULE_ENABLE_END_TURN":
			self.tutorial.bCanEndTurn = True
		elif scriptName == "RULE_DISABLE_END_TURN":
			self.tutorial.bCanEndTurn = False
		elif scriptName == "RULE_HALT_PRODUCTION":
			self.tutorial.bDoProduction = True
		elif scriptName == "RULE_ALLOW_PRODUCTION":
			self.tutorial.bDoProduction = False
		elif scriptName == "RULE_ENABLE_RESEARCH_POPUPS":
			self.tutorial.bSkipResearchPopup = False
#			print ("Trying to open tech Pop up")
			gc.getPlayer(gc.getGame().getActivePlayer()).chooseTech(0, CyTranslator().getText("TXT_KEY_CHOOSE_TECH",()), False)
		elif scriptName == "RULE_DISABLE_RESEARCH_POPUPS":
			self.tutorial.bSkipResearchPopup = True
		elif scriptName == "RULE_DISABLE_COLORED_PLOTS":		
			self.tutorial.bUpdateColoredPlots = True
		elif scriptName == "RULE_ENABLE_COLORED_PLOTS":		
			self.tutorial.bUpdateColoredPlots = False
		elif scriptName == "RULE_DISABLE_BUILD_ROADS":		
			self.tutorial.bDisableBuildRoads = True
		elif scriptName == "RULE_ENABLE_BUILD_ROADS":		
			self.tutorial.bDisableBuildRoads = False
			
		#Research Tech   
		elif scriptName == "WAIT_FOR_ARCHERY_SELECTION":
			self.tutorial.bWaitForResearchSelection = True
			self.tutorial.bCannotResearch = False
			self.tutorial.iCannotResearch = CvUtil.findInfoTypeNum(gc.getTechInfo, gc.getNumTechInfos(), "TECH_ARCHERY")
			self.tutorial.iGetFirstRecommendedTech = CvUtil.findInfoTypeNum(gc.getTechInfo, gc.getNumTechInfos(), "TECH_ARCHERY")
		elif scriptName == "WAIT_FOR_ARCHERY_DISCOVERED":
			self.tutorial.bWaitForResearchDiscovered = True
		elif scriptName == "WAIT_FOR_MASONRY_SELECTION":
			self.tutorial.bWaitForResearchSelection = True
			self.tutorial.bCannotResearch = False
			self.tutorial.iCannotResearch = CvUtil.findInfoTypeNum(gc.getTechInfo, gc.getNumTechInfos(), "TECH_MASONRY")
			self.tutorial.iGetFirstRecommendedTech = CvUtil.findInfoTypeNum(gc.getTechInfo, gc.getNumTechInfos(), "TECH_MASONRY")
		elif scriptName == "WAIT_FOR_MASONRY_DISCOVERED":
			self.tutorial.bWaitForResearchDiscovered = True
		elif scriptName == "WAIT_FOR_MEDITATION_SELECTION":
			self.tutorial.bWaitForResearchSelection = True
			self.tutorial.bCannotResearch = False
			self.tutorial.iCannotResearch = CvUtil.findInfoTypeNum(gc.getTechInfo, gc.getNumTechInfos(), "TECH_MEDITATION")
			self.tutorial.iGetFirstRecommendedTech = CvUtil.findInfoTypeNum(gc.getTechInfo, gc.getNumTechInfos(), "TECH_MEDITATION")
		elif scriptName == "WAIT_FOR_MEDITATION_DISCOVERED":
			self.tutorial.bWaitForResearchDiscovered = True
		elif scriptName == "WAIT_FOR_BRONZE_WORKING_SELECTION":
			self.tutorial.bWaitForResearchSelection = True
			self.tutorial.bCannotResearch = False
			self.tutorial.iCannotResearch = CvUtil.findInfoTypeNum(gc.getTechInfo, gc.getNumTechInfos(), "TECH_BRONZE_WORKING")
			self.tutorial.iGetFirstRecommendedTech = CvUtil.findInfoTypeNum(gc.getTechInfo, gc.getNumTechInfos(), "TECH_BRONZE_WORKING")
		elif scriptName == "WAIT_FOR_BRONZE_WORKING_DISCOVERED":
			self.tutorial.bWaitForResearchDiscovered = True
		elif scriptName == "RULE_CLEAR_RESEARCH_RESTRICTION":
			self.tutorial.bCannotResearch = False
			self.tutorial.iCannotResearch = 0
			self.tutorial.iGetFirstRecommendedTech = TechTypes.NO_TECH

		#Change Advisors 
#		elif scriptName == "SET_ADVISOR_GROWTH":


		#Wait for actions
		elif scriptName == "WAIT_FOR_SELECT_SETTLER":
			self.bWaitToContinue = True
			self.tutorial.doWaitForSelected("FIRST_SETTLER")
		elif scriptName == "WAIT_FOR_RECENTER":	
			self.bWaitForRecenterToContinue = True
		elif scriptName == "WAIT_FOR_BUILD_FIRST_CITY":
			self.tutorial.setWaitForAction( MissionTypes.MISSION_FOUND, InterfaceModeTypes.NO_INTERFACEMODE, CommandTypes.NO_COMMAND, scriptName, "FIRST_SETTLER", [[1,1]])
			self.tutorial.bWaitForUnitAction = True
			CyInterface().setDirty(InterfaceDirtyBits.SelectionButtons_DIRTY_BIT, True)
		elif scriptName == "WAIT_FOR_BEGIN_PLAYER_TURN":
			self.tutorial.bWaitForBeginPlayerTurn = True
		elif scriptName == "WAIT_FOR_WARRIOR_TO_FORTIFY":
			self.tutorial.setWaitForAction( MissionTypes.MISSION_FORTIFY, InterfaceModeTypes.NO_INTERFACEMODE, CommandTypes.NO_COMMAND, scriptName, "FIRST_WARRIOR", [[1,1]])		
			self.tutorial.bWaitForUnitFortify = True
			CyInterface().setDirty(InterfaceDirtyBits.SelectionButtons_DIRTY_BIT, True)
		elif scriptName == "WAIT_FOR_SCOUT_MOVE_TO_VILLAGE_1":
			self.tutorial.setWaitForAction( MissionTypes.NO_MISSION, InterfaceModeTypes.INTERFACEMODE_GO_TO, CommandTypes.NO_COMMAND, scriptName, "FIRST_SCOUT", [[28,17]]) 	
			self.tutorial.bWaitForGoToAction = True
			CyInterface().setDirty(InterfaceDirtyBits.SelectionButtons_DIRTY_BIT, True)		
		elif scriptName == "WAIT_UNTIL_TRIBAL_VILLAGE_EXPLORED":
			self.tutorial.bWaitForVillageDiscovered = True
		elif scriptName == "WAIT_FOR_SCOUT_MOVE_TO_VILLAGE_2":
			self.tutorial.setWaitForAction(	MissionTypes.NO_MISSION, InterfaceModeTypes.INTERFACEMODE_GO_TO, CommandTypes.NO_COMMAND, scriptName, "FIRST_SCOUT", [[25,18]])		
			self.tutorial.bWaitForGoToAction = True	
			CyInterface().setDirty(InterfaceDirtyBits.SelectionButtons_DIRTY_BIT, True)
		elif scriptName == "WAIT_FOR_OPEN_CITY_SCREEN":
			self.tutorial.bWaitForOpenCityScreen = True
		elif scriptName == "WAIT_FOR_ESCAPE_FROM_CITY_SCREEN":
			self.tutorial.bWaitForEscapeCityScreen = True
		elif scriptName == "WAIT_FOR_BUILD_SECOND_CITY":
			self.tutorial.setWaitForAction(MissionTypes.MISSION_FOUND, InterfaceModeTypes.NO_INTERFACEMODE, CommandTypes.NO_COMMAND, scriptName, "SECOND_SETTLER", [[1,1]])
			self.tutorial.bWaitForUnitAction = True
			CyInterface().setDirty(InterfaceDirtyBits.SelectionButtons_DIRTY_BIT, True)


		
		#Free up setWaitForAction	
		elif scriptName == "FREE_UNIT_CONTROL":
			self.tutorial.setWaitForAction(MissionTypes.MISSION_MOVE_TO, InterfaceModeTypes.NO_INTERFACEMODE, CommandTypes.NO_COMMAND, scriptName, "NONE", tuple())
			self.tutorial.iForcedBuildImprovement = -1
		elif scriptName == "FREE_BUILD_RECOMMENDATION":
			self.tutorial.FirstCity.chooseProduction(UnitTypes.NO_UNIT,BuildingTypes.NO_BUILDING,ProjectTypes.NO_PROJECT,True,False)
			self.tutorial.iGetRecommendedUnit = UnitTypes.NO_UNIT
			self.tutorial.iGetRecommendedBuilding = BuildingTypes.NO_BUILDING
			
		
		#Freeze Units FREEZE_WARRIOR
		elif scriptName == "RESTRICT_SETTLER_MOVEMENT":
			self.tutorial.setWaitForAction(MissionTypes.MISSION_MOVE_TO, InterfaceModeTypes.NO_INTERFACEMODE, CommandTypes.NO_COMMAND, scriptName, "FIRST_SETTLER", [[1,1]])
		elif scriptName == "RESTRICT_WORKER_MOVEMENT":
			self.tutorial.setWaitForAction(MissionTypes.MISSION_MOVE_TO, InterfaceModeTypes.NO_INTERFACEMODE, CommandTypes.NO_COMMAND, scriptName, "FIRST_WORKER", [[1,1]])
		elif scriptName == "FREEZE_SCOUT":
			self.tutorial.setWaitForAction(MissionTypes.MISSION_MOVE_TO, InterfaceModeTypes.NO_INTERFACEMODE, CommandTypes.NO_COMMAND, scriptName, "FIRST_SCOUT", [[1,1]])
		elif scriptName == "FREEZE_WARRIOR":
			self.tutorial.setWaitForAction(MissionTypes.MISSION_MOVE_TO, InterfaceModeTypes.NO_INTERFACEMODE, CommandTypes.NO_COMMAND, scriptName, "FIRST_WARRIOR", [[1,1]])
		elif scriptName == "FREEZE_SECOND_WARRIOR":
			self.tutorial.setWaitForAction(MissionTypes.MISSION_MOVE_TO, InterfaceModeTypes.NO_INTERFACEMODE, CommandTypes.NO_COMMAND, scriptName, "SECOND_WARRIOR", [[1,1]])
		elif scriptName == "FREEZE_SECOND_SETTLER":
			self.tutorial.setWaitForAction(MissionTypes.MISSION_MOVE_TO, InterfaceModeTypes.NO_INTERFACEMODE, CommandTypes.NO_COMMAND, scriptName, "SECOND_SETTLER", [[1,1]])

		# Can open screen controls
		elif scriptName == "RULE_ENABLE_RELIGION_SCREEN":
			self.tutorial.bCanOpenReligionScreen = True	
		elif scriptName == "RULE_ENABLE_CIVIC_SCREEN":
			self.tutorial.bCanOpenCivicScreen = True			
		elif scriptName == "RULE_ENABLE_DIPLOMACY_SCREEN":
			self.tutorial.setWaitForAction(MissionTypes.MISSION_MOVE_TO, InterfaceModeTypes.NO_INTERFACEMODE, CommandTypes.NO_COMMAND, scriptName, "FIRST_SETTLER", [[33,14]])		
			self.tutorial.bCanOpenDiplomacyScreen = True			
		elif scriptName == "RULE_ENABLE_ALL_OTHER_SCREENS":
			self.tutorial.bCanOpenAllOtherScreens = True		


		#Wait for Moves
		elif scriptName == "WAIT_FOR_SETTLER_1_MOVE":
			self.tutorial.setWaitForAction(MissionTypes.MISSION_MOVE_TO, InterfaceModeTypes.NO_INTERFACEMODE, CommandTypes.NO_COMMAND, scriptName, "FIRST_SETTLER", [[33,14]])		
			self.tutorial.bWaitForUnitAction = True		
		elif scriptName == "WAIT_FOR_WARRIOR_MOVE_TO_LION":
			self.tutorial.setWaitForAction(MissionTypes.MISSION_MOVE_TO, InterfaceModeTypes.NO_INTERFACEMODE, CommandTypes.NO_COMMAND, scriptName, "FIRST_WARRIOR", [[34,13],[34,14]])		
			self.tutorial.bWaitForUnitAction = True
			CyInterface().setDirty(InterfaceDirtyBits.SelectionButtons_DIRTY_BIT, True)
		elif scriptName == "WAIT_FOR_WARRIOR_RETURN_FROM_LION":
			self.tutorial.setWaitForAction(MissionTypes.MISSION_MOVE_TO, InterfaceModeTypes.NO_INTERFACEMODE, CommandTypes.NO_COMMAND, scriptName, "FIRST_WARRIOR", [[34,13],[34,14], [33,14]])		
			self.tutorial.bWaitForReturnFirstCity = True
			CyInterface().setDirty(InterfaceDirtyBits.SelectionButtons_DIRTY_BIT, True)
		elif scriptName == "WAIT_FOR_WARRIOR_TO_ATTACK_LION":
			self.tutorial.setWaitForAction(MissionTypes.MISSION_MOVE_TO, InterfaceModeTypes.NO_INTERFACEMODE, CommandTypes.NO_COMMAND, scriptName, "FIRST_WARRIOR", [[35,13]])		
			self.tutorial.bWaitForUnitCombat = True
		elif scriptName == "WAIT_FOR_WARRIOR_MOVE_TO_CITY":
			self.tutorial.setWaitForAction(MissionTypes.MISSION_MOVE_TO, InterfaceModeTypes.NO_INTERFACEMODE, CommandTypes.NO_COMMAND, scriptName, "FIRST_WARRIOR", [[33,14]])		
			self.tutorial.bWaitForUnitAction = True
		elif scriptName == "WAIT_FOR_WORKER_MOVE_TO_FARM":
			self.tutorial.setWaitForAction(MissionTypes.MISSION_MOVE_TO, InterfaceModeTypes.NO_INTERFACEMODE, CommandTypes.NO_COMMAND, scriptName, "FIRST_WORKER", [[32,13]])		
			self.tutorial.bWaitForUnitAction = True			
		elif scriptName == "WAIT_FOR_WORKER_MOVE_TO_COTTAGE":
			self.tutorial.setWaitForAction(MissionTypes.MISSION_MOVE_TO, InterfaceModeTypes.NO_INTERFACEMODE, CommandTypes.NO_COMMAND, scriptName, "FIRST_WORKER", [[32,14]])		
			self.tutorial.bWaitForUnitAction = True		
		elif scriptName == "WAIT_FOR_WORKER_MOVE_TO_MINE":
			self.tutorial.setWaitForAction(MissionTypes.MISSION_MOVE_TO, InterfaceModeTypes.NO_INTERFACEMODE, CommandTypes.NO_COMMAND, scriptName, "FIRST_WORKER", [[32,15]])		
			self.tutorial.bWaitForUnitAction = True
		elif scriptName == "WAIT_FOR_SETTLER_MOVE_TO_SECOND_CITY":
			self.tutorial.setWaitForAction(MissionTypes.MISSION_MOVE_TO, InterfaceModeTypes.NO_INTERFACEMODE, CommandTypes.NO_COMMAND, scriptName, "SECOND_SETTLER", [[33,13],[34,13],[33,12],[34,12],[33,11],[34,11],[33,10],[34,10],[34,9]])		
			self.tutorial.bWaitForMoveToSecondCity = True
		elif scriptName == "WAIT_FOR_WORKER_MOVE_TO_STONE": 
			self.tutorial.bWaitForWorkerArriveStone = True
		elif scriptName == "WAIT_FOR_WORKER_ROUTE_TO_STONE":
			self.tutorial.setWaitForAction( MissionTypes.NO_MISSION, InterfaceModeTypes.INTERFACEMODE_ROUTE_TO, CommandTypes.NO_COMMAND, scriptName, "FIRST_WORKER", [[33,14]])		
			self.tutorial.bWaitForRouteToAction = True


		#Wait for worker builds
		elif scriptName == "WAIT_FOR_WORKER_BUILD_FARM":
			self.tutorial.setWaitForAction(MissionTypes.MISSION_BUILD, InterfaceModeTypes.NO_INTERFACEMODE, CommandTypes.NO_COMMAND, scriptName, "FIRST_WORKER", [[1,1]])		
			self.tutorial.setBuildImprovement("BUILD_FARM")
			self.tutorial.bWaitForWorkerToBuild = True
			CyInterface().setDirty(InterfaceDirtyBits.SelectionButtons_DIRTY_BIT, True)
		elif scriptName == "WAIT_FOR_WORKER_BUILD_COTTAGE":
			self.tutorial.setWaitForAction(MissionTypes.MISSION_BUILD, InterfaceModeTypes.NO_INTERFACEMODE, CommandTypes.NO_COMMAND, scriptName, "FIRST_WORKER", [[1,1]])
			self.tutorial.setBuildImprovement("BUILD_COTTAGE")
			self.tutorial.bWaitForWorkerToBuild = True
			CyInterface().setDirty(InterfaceDirtyBits.SelectionButtons_DIRTY_BIT, True)
		elif scriptName == "WAIT_FOR_WORKER_BUILD_MINE":
			self.tutorial.setWaitForAction(MissionTypes.MISSION_BUILD, InterfaceModeTypes.NO_INTERFACEMODE, CommandTypes.NO_COMMAND, scriptName, "FIRST_WORKER", [[1,1]])		
			self.tutorial.bWaitForWorkerToBuild = True
			CyInterface().setDirty(InterfaceDirtyBits.SelectionButtons_DIRTY_BIT, True)
			self.tutorial.setBuildImprovement("BUILD_MINE")
		elif scriptName == "WAIT_FOR_WORKER_BUILD_QUARRY":
			self.tutorial.setWaitForAction(MissionTypes.MISSION_BUILD, InterfaceModeTypes.NO_INTERFACEMODE, CommandTypes.NO_COMMAND, scriptName, "FIRST_WORKER", [[1,1]])		
			self.tutorial.bWaitForWorkerToBuild = True
			CyInterface().setDirty(InterfaceDirtyBits.SelectionButtons_DIRTY_BIT, True)
			self.tutorial.setBuildImprovement("BUILD_QUARRY")
		elif scriptName == "WAIT_FOR_ROAD_TO_FINISH":
			self.tutorial.bWaitForWorkerToBuildRoad = True
			
		#Wait for finish building
		elif scriptName == "WAIT_FOR_WORKER_FINISH_IN_ROME":
			self.tutorial.bWaitForWorkerToFinishBuilding = True
		elif scriptName == "WAIT_FOR_BARRACKS_TO_BUILD":
			self.tutorial.bWaitForBarracksToBuild = True
		elif scriptName == "WAIT_FOR_WARRIOR_FINISH_IN_ROME":
			self.tutorial.bWaitForWarriorToFinishBuilding = True
		elif scriptName == "WAIT_FOR_SETTLER_FINISH_IN_ROME":
			self.tutorial.bWaitForSettlerToFinishBuilding = True
		
		
		#Wait for Selections
		elif scriptName == "WAIT_FOR_BUILD_SELECTION_WARRIOR":
			self.tutorial.FirstCity.chooseProduction( UnitTypes.NO_UNIT,BuildingTypes.NO_BUILDING,ProjectTypes.NO_PROJECT,True,False)
			self.tutorial.iGetRecommendedUnit = iWarrior
			self.tutorial.iGetRecommendedBuilding = BuildingTypes.NO_BUILDING
			self.tutorial.iForcedUnit = iWarrior
			self.tutorial.iForcedBuilding = -1			
			self.tutorial.bWaitForBuildSelectionWarrior = True
		elif scriptName == "WAIT_FOR_BUILD_SELECTION_SCOUT":
			self.tutorial.FirstCity.chooseProduction(UnitTypes.NO_UNIT,BuildingTypes.NO_BUILDING,ProjectTypes.NO_PROJECT,True,False)
			self.tutorial.iGetRecommendedUnit = iScout
			self.tutorial.iGetRecommendedBuilding = BuildingTypes.NO_BUILDING
			self.tutorial.iForcedUnit = iScout
			self.tutorial.iForcedBuilding = -1	
			self.tutorial.bWaitForBuildSelectionScout = True
		elif scriptName == "WAIT_FOR_BUILD_SELECTION_OBELISK":
			self.tutorial.FirstCity.chooseProduction(UnitTypes.NO_UNIT,BuildingTypes.NO_BUILDING,ProjectTypes.NO_PROJECT,True,False)
			self.tutorial.iGetRecommendedUnit = UnitTypes.NO_UNIT
			self.tutorial.iGetRecommendedBuilding = iObelisk
			self.tutorial.iForcedUnit = -1
			self.tutorial.iForcedBuilding = iObelisk
			self.tutorial.bWaitForBuildSelectionObelisk = True
		elif scriptName == "WAIT_FOR_BUILD_SELECTION_WORKER":
			self.tutorial.FirstCity.chooseProduction(UnitTypes.NO_UNIT,BuildingTypes.NO_BUILDING,ProjectTypes.NO_PROJECT,True,False)
			self.tutorial.iGetRecommendedUnit = iWorker
			self.tutorial.iGetRecommendedBuilding = BuildingTypes.NO_BUILDING
			self.tutorial.iForcedUnit = iWorker
			self.tutorial.iForcedBuilding = -1
			self.tutorial.bWaitForBuildSelectionWorker = True
		elif scriptName == "WAIT_FOR_BUILD_SELECTION_BARRACKS":
			self.tutorial.FirstCity.chooseProduction(UnitTypes.NO_UNIT,BuildingTypes.NO_BUILDING,ProjectTypes.NO_PROJECT,True,False)
			self.tutorial.iGetRecommendedUnit = UnitTypes.NO_UNIT
			self.tutorial.iGetRecommendedBuilding = iBarracks
			self.tutorial.iForcedUnit = -1
			self.tutorial.iForcedBuilding = iBarracks
			self.tutorial.bWaitForBuildSelectionBarracks = True
		elif scriptName == "WAIT_FOR_BUILD_SELECTION_SETTLER":
			self.tutorial.FirstCity.chooseProduction(UnitTypes.NO_UNIT,BuildingTypes.NO_BUILDING,ProjectTypes.NO_PROJECT,True,False)
			self.tutorial.iGetRecommendedBuilding = BuildingTypes.NO_BUILDING
			self.tutorial.iGetRecommendedUnit = iSettler
			self.tutorial.iForcedUnit = iSettler
			self.tutorial.iForcedBuilding = -1
			self.tutorial.bWaitForBuildSelectionSettler = True
		elif scriptName == "WAIT_FOR_STONEHENGE_SELECTION":
			self.tutorial.bStoneHengeAllowed = True
			self.tutorial.FirstCity.chooseProduction(UnitTypes.NO_UNIT,BuildingTypes.NO_BUILDING,ProjectTypes.NO_PROJECT,True,False)
			self.tutorial.iGetRecommendedUnit = UnitTypes.NO_UNIT
			self.tutorial.iGetRecommendedBuilding = iStonehenge
			self.tutorial.iForcedUnit = -1
			self.tutorial.iForcedBuilding = iStonehenge
			self.tutorial.bWaitForBuildSelectionStonehenge = True


		elif scriptName == "WAIT_FOR_PROMOTION_SELECTION":
			self.tutorial.setWaitForAction( MissionTypes.NO_MISSION, InterfaceModeTypes.NO_INTERFACEMODE, CommandTypes.COMMAND_PROMOTION, scriptName, "SECOND_WARRIOR", [[]])		
			self.tutorial.bWaitForUnitAction = True
			self.tutorial.bWaitForPromotion = True
			CyInterface().setDirty(InterfaceDirtyBits.SelectionButtons_DIRTY_BIT, True)
			
			
		#Events	
		elif scriptName == "ENABLE_INCREASED_PRODUCTION_IN_ROME":
			self.tutorial.bIncreasedProductionRome = True
		elif scriptName == "DISABLE_INCREASED_PRODUCTION_IN_ROME":
			self.tutorial.bIncreasedProductionRome = False
		elif scriptName == "INCREASE_ROMES_PRODUCTION":
			self.tutorial.FirstCity.changeProduction(11)
		elif scriptName == "INCREASE_ROMES_PRODUCTION_ALOT":
			self.tutorial.FirstCity.changeProduction(30)
		elif scriptName == "SPAWN_MARAUDING_LIONS":
			gc.getPlayer(gc.getBARBARIAN_PLAYER()).initUnit(CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(),"UNIT_LION"), 35, 11, UnitAITypes.NO_UNITAI)
			self.tutorial.FirstLion = gc.getPlayer(gc.getBARBARIAN_PLAYER()).getUnit(0)
		elif scriptName == "SPAWN_TRIBAL_VILLAGES":
			CyMap().plot(28,17).setImprovementType(CvUtil.findInfoTypeNum(gc.getImprovementInfo, gc.getNumImprovementInfos(), "IMPROVEMENT_GOODY_HUT"))
			CyMap().plot(25,18).setImprovementType(CvUtil.findInfoTypeNum(gc.getImprovementInfo, gc.getNumImprovementInfos(), "IMPROVEMENT_GOODY_HUT"))
		elif scriptName == "REVEAL_FIRST_TRIBAL_VILLAGE":
			CyMap().plot(28,17).setRevealed(CyGame().getActiveTeam(),1,0,TeamTypes.NO_TEAM)
			CyMap().plot(29,16).setRevealed(CyGame().getActiveTeam(),1,0,TeamTypes.NO_TEAM)
			CyMap().plot(29,17).setRevealed(CyGame().getActiveTeam(),1,0,TeamTypes.NO_TEAM)
			CyMap().plot(29,18).setRevealed(CyGame().getActiveTeam(),1,0,TeamTypes.NO_TEAM)
			CyMap().plot(28,16).setRevealed(CyGame().getActiveTeam(),1,0,TeamTypes.NO_TEAM)
			CyMap().plot(28,18).setRevealed(CyGame().getActiveTeam(),1,0,TeamTypes.NO_TEAM)
			CyMap().plot(27,16).setRevealed(CyGame().getActiveTeam(),1,0,TeamTypes.NO_TEAM)
			CyMap().plot(27,17).setRevealed(CyGame().getActiveTeam(),1,0,TeamTypes.NO_TEAM)
			CyMap().plot(27,18).setRevealed(CyGame().getActiveTeam(),1,0,TeamTypes.NO_TEAM)
			CyMap().plot(29,15).setRevealed(CyGame().getActiveTeam(),1,0,TeamTypes.NO_TEAM)
		elif scriptName == "REVEAL_SECOND_CITY":
			CyMap().plot(34,9).setRevealed(CyGame().getActiveTeam(),1,0,TeamTypes.NO_TEAM)
			CyMap().plot(35,9).setRevealed(CyGame().getActiveTeam(),1,0,TeamTypes.NO_TEAM)
			CyMap().plot(33,9).setRevealed(CyGame().getActiveTeam(),1,0,TeamTypes.NO_TEAM)
			CyMap().plot(34,10).setRevealed(CyGame().getActiveTeam(),1,0,TeamTypes.NO_TEAM)
			CyMap().plot(35,10).setRevealed(CyGame().getActiveTeam(),1,0,TeamTypes.NO_TEAM)
			CyMap().plot(33,10).setRevealed(CyGame().getActiveTeam(),1,0,TeamTypes.NO_TEAM)
			CyMap().plot(34,8).setRevealed(CyGame().getActiveTeam(),1,0,TeamTypes.NO_TEAM)
			CyMap().plot(35,8).setRevealed(CyGame().getActiveTeam(),1,0,TeamTypes.NO_TEAM)
			CyMap().plot(33,8).setRevealed(CyGame().getActiveTeam(),1,0,TeamTypes.NO_TEAM)
		elif scriptName == "WAIT_FOR_FIRST_CONTACT":
			self.tutorial.bWaitForFirstContact = True
		elif scriptName == "SPAWN_INDIA":
			self.tutorial.bGoWestNotAllowed = False
			gc.getPlayer(1).initUnit(CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(),"UNIT_SETTLER"), 11, 9, UnitAITypes.NO_UNITAI)
			gc.getPlayer(1).initUnit(CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(),"UNIT_SPEARMAN"), 11, 9, UnitAITypes.NO_UNITAI)
			gc.getPlayer(1).initUnit(CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(),"UNIT_SCOUT"), 11, 9, UnitAITypes.NO_UNITAI)


		#AI controls 
		elif scriptName == "ENABLE_FORCE_LIONS_MOVE_NORTH":
			self.tutorial.bForceLionMoveNorth = True

		elif scriptName == "DISABLE_FORCE_LIONS_MOVE_NORTH":
			self.tutorial.bForceLionMoveNorth = False
			
#		elif scriptName == "MARAUDING_LIONS_GROWL":
			#Need force Lion Growl
		
		elif scriptName == "RULE_PAUSE_POPUPS":
			CyInterface().setPausedPopups ( True )

		elif scriptName == "RULE_UNPAUSE_POPUPS":
			CyInterface().setPausedPopups ( False )

		elif scriptName == "TUTORIAL_START":
			self.tutorial.bTutorialBegun = True

		elif scriptName == "TUTORIAL_COMPLETE":
			self.tutorial.bTutorialComplete = True
			CyCamera().SetViewPortCenter(NiPoint2(0.5, 0.4))
		
		elif scriptName == "SELECT_OBJECTIVE_UNIT":
			CyInterface().selectUnit( PyHelpers.PyPlayer( gc.getGame().getActivePlayer() ).getUnitByScriptData( self.tutorial.szScriptData ), 0, 0, 0 )

		elif scriptName == "DISABLE_KEYBOARD_INPUT":
			self.tutorial.bConsumeKeyboardInput = True
		elif scriptName == "ENABLE_KEYBOARD_INPUT":
			self.tutorial.bConsumeKeyboardInput = False
		
		elif scriptName == "DISABLE_MOUSE_INPUT_TO_MAIN_INTERFACE":
			self.tutorial.bDisableMainInteraceMouseInput = True
		elif scriptName == "ENABLE_MOUSE_INPUT_TO_MAIN_INTERFACE":
			self.tutorial.bDisableMainInteraceMouseInput = False
		
		elif scriptName == "ENABLE_WORKER_BUILD_QUARRY":
			self.tutorial.bWorkerCanBuildQuarry = True
			
		elif scriptName == "ENABLE_SHOW_TECH_CHOOSER_BUTTON":
			self.tutorial.bShowTechChooserButton = False
		
		elif scriptName == "ENABLE_WATCH_CITY_SCREEN":
			self.tutorial.bWatchCityScreen = True
		
		elif scriptName == "ENABLE_LOCK_FIRST_WARRIOR":
			self.tutorial.bLockFirstWarrior = True

		elif scriptName == "DISABLE_LOCK_FIRST_WARRIOR":
			self.tutorial.bLockFirstWarrior = False
			
		###################

		return
	
	def processTutorialMessage(self, iTutorialMessage):
		if self.activeTutorialInfo:
			self.activeTutorialMessage = self.activeTutorialInfo.getTutorialMessage(iTutorialMessage)
			self.tutorial.setActiveTutorialMessage(self.activeTutorialMessage)
			#self.setText(TEXT_AREA_DEBUG,"TutorialInfo: %s - Message (%s)" %(self.activeTutorialInfo.getType(),self.__iMessageCount))
			# Text
			self.setText(TEXT_AREA_ADVISOR,self.activeTutorialMessage.getText())
			# Sound
			self.playAdvisorSound(self.activeTutorialMessage.getSound())
			# Image - set to "No Text" when XML is loading
			messageImage = self.activeTutorialMessage.getImage()
			if messageImage != "No Text":
				# remove the message
				if messageImage == "CLEAR":
					self.clearHelpImage()
				else:
					self.setHelpImage(messageImage)
			# Scripts
			if self.activeTutorialMessage.getNumTutorialScripts() > 0:
				self.processTutorialScripts()
		else:
			self.setText(TEXT_AREA_DEBUG,"TutorialInfo: INVALID")

	def reprocessMessage(self,iTutorialMessage):
		self.activeTutorialMessage = self.activeTutorialInfo.getTutorialMessage(iTutorialMessage)
		self.tutorial.setActiveTutorialMessage(self.activeTutorialMessage)
		self.setText(TEXT_AREA_ADVISOR,self.activeTutorialMessage.getText())

	def processTutorialInfo(self, tutorialInfoID):
		CvUtil.pyPrint("processTutorialInfo -> %s" %tutorialInfoID)
		self.activeTutorialInfo = gc.getTutorialInfo(tutorialInfoID)
		self.__doBeginTutorialInfo()
		self.processTutorialMessage(0)
	def processTutorialInfoByType(self, name):
		self.processTutorialInfo(gc.getInfoTypeForString(name))
	def handleInput(self, inputClass):
		if self.activeTutorialInfo:
			#CvUtil.pyPrint( "In Tutorial Handle" )
			if (inputClass.getNotifyCode() == NotifyCode.NOTIFY_CLICKED):
				functionName = inputClass.getFunctionName()
				if functionName == "Reset":
					CvUtil.pyPrint("Reset Message being handled")
					self.resetTutorialScreen()
					return 1

				elif functionName == "Continue":
					if self.bWaitToContinue:
						CvUtil.pyPrint("bWaitToContinue is TRUE: Returning")
						return 0
					if self.__iMessageCount+1 == self.activeTutorialInfo.getNumTutorialMessages():
						CvUtil.pyPrint("All Messages Presented, calling doEndTutorialInfo (%s)" %self.activeTutorialInfo.getType())
						self.__doEndTutorialInfo()
						return 0
					else:
						CvUtil.pyPrint("Continue Message (%s) do Next Message (%s)" %(self.activeTutorialInfo.getType(), self.__iMessageCount+1))
						self.__iMessageCount += 1
						self.processTutorialMessage(self.__iMessageCount)
					return 1

				elif functionName == "Previous":
					CvUtil.pyPrint("Previous Message being handled - iCurrentMessageID = %s" %self.__iMessageCount)
					if self.__iMessageCount == 0:
						return
					self.__iMessageCount -= 1
					self.processTutorialMessage(self.__iMessageCount)
				elif functionName == "End Tutorial":
					self.clearScreen()
				else:
					return 0
				
				return 1
		return 0
	def processTutorialScripts(self):
		l_Scripts = self.getScriptList()
		if l_Scripts:
			for script in l_Scripts:
				CvUtil.pyPrint("tutorialAdvisor.processTutorialScripts --> Processing %s" %script)
				self.doScript(script)
		return
	def getScriptList(self):
		numScripts = self.getActiveTutorialMessage().getNumTutorialScripts()
		if numScripts <= 0 or numScripts > 100:
			return
		l_ScriptNames = []
		for i in range(self.getActiveTutorialMessage().getNumTutorialScripts()):
			l_ScriptNames.append(self.getActiveTutorialMessage().getTutorialScriptByIndex(i))
		return l_ScriptNames
	def setText(self, iTextArea, messageText, argsList=()):
		textAreas = { TEXT_AREA_ADVISOR : self.setAdvisorText,
					TEXT_AREA_DEBUG : self.setDebugText,
					 }
		# if the message text is a game text key use it, otherwise display the string
		if messageText.find("TUTORIAL") != -1:
			messageText=CyTranslator().getText(messageText,argsList)
		if textAreas.has_key(iTextArea):
			return textAreas[iTextArea](messageText)
	
	def centerCameraFocus(self, plot):
		x = plot.getX()
		y = plot.getY()
		return CyMap().plot(x,y).getPoint()
	def centerCameraFocusOnPlot(self, plot):
		x = plot.getX()
		y = plot.getY()
		return CyMap().plot(x,y+1).getPoint()
	def resetTutorial(self):
		self.clearScreen()
		self.resetActiveTutorialInfo()
		self.startTutorial(True)
	def resetActiveTutorialInfo(self):
		self.activeTutorialInfo = None
		self.activeTutorialMessage = None
	def getActiveTutorialMessage(self):
		if self.activeTutorialMessage:
			return self.activeTutorialMessage
	def getActiveTutorialInfo(self):
		if self.activeTutorialInfo:
			return self.activeTutorialInfo
	
	def getCompletedTutorialInfos(self):
		print (self.activeTutorialInfo.getType(), self.__l_TutorialInfos)
		return (self.activeTutorialInfo.getType(), self.__l_TutorialInfos)
	def setCompletedTutorialInfos(self, list):
		print list
		self.__l_TutorialInfos = list[1]
	
	def doTutorialInfoComplete(self, type):
		self.__iMessageCount = 0
		self.__iCompletedTutorialInfos += 1
		self.__l_TutorialInfos.append(type)

	def doHideEndTutorialButton(self):
		self.clearAdvisorButtons()
		self.showAdvisorButtons('Continue')

	def doHideOKButton(self):
		self.clearAdvisorButtons()
#		self.showAdvisorButtons('Previous')


	def doShowAllButtons(self):
		self.clearAdvisorButtons()
		self.showAdvisorButtons('Continue')
#		self.showAdvisorButtons('Previous')


	def doShowEndTutorialButtons(self):
		self.clearAdvisorButtons()
		self.showAdvisorButtons('End Tutorial')

	def doScreenRefresh( self ):
		self.setBackgroundPosition(self.iBackgroundX ,self.iBackgroundY)
		self.reprocessMessage(self.__iMessageCount)
		self.doHideEndTutorialButton()
		
	def show( self, szName ):
		screen = self.getScreen()
		screen.show(szName)

	def getNextWidgetName(self):
		szName = self.WIDGET_ID + str(self.nWidgetCount)
		self.nWidgetCount += 1
		return szName
		
	def setCloseOnEscape(self, bClose):
		screen = self.getScreen()
		screen.setCloseOnEscape(bClose)
	
tutorialAdvisorScreen = CvTutorialAdvisorScreen()