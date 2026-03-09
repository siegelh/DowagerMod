## Sid Meier's Civilization 4
## Copyright Firaxis Games 2005

import CvUtil
import CvScreensInterface
import CvEventManager
import Tutorial
import CvTutorialAdvisorScreen
import CvCameraControls
import PyHelpers
import CvAdvisorUtils
from CvPythonExtensions import *

PyPlayer = PyHelpers.PyPlayer

gc = CyGlobalContext()

# globals
###################################################
class CvTutorialEventManager( CvEventManager.CvEventManager ):
	def __init__( self ):
		CvEventManager.CvEventManager.__init__(self)
		self.screen = CvTutorialAdvisorScreen.tutorialAdvisorScreen
		self.tutorial = Tutorial.tutorial
		
		self.iUnitsCreated = 0
	
	def onSaveGame(self, argsList):
		return ""
	
	def onLoadGame(self, argsList):
		return 
				
	def onKbdEvent(self, argsList):
		eventType,key,mx,my,px,py = argsList
		
		if ( eventType == self.EventKeyDown ):
			theKey=int(key)
			
			if self.tutorial.bConsumeKeyboardInput == True:
				return 1

			# Shift - T (Debug - No MP)
#			if ( theKey == int(InputTypes.KB_J) and self.bCtrl and self.bAlt ):
#				return 0
			if ( theKey == int(InputTypes.KB_C) and self.screen.bWaitForRecenterToContinue == True ):
				self.screen.bWaitForRecenterToContinue = False
				#self.screen.doLeaderheadApproval()
				self.screen.doNextInfo()
			if ( theKey == int(InputTypes.KB_ESCAPE) and self.tutorial.bWaitForEscapeCityScreen == True ):
				self.tutorial.bWaitForEscapeCityScreen = False
				self.tutorial.bWatchCityScreen = False
				
				self.screen.doNextInfo()
			if ( theKey == int(InputTypes.KB_RETURN) and self.tutorial.bWaitForEscapeCityScreen == True ):
				self.tutorial.bWaitForEscapeCityScreen = False
				self.tutorial.bWatchCityScreen = False
				self.screen.doNextInfo()			
		print (" In CvTutorialEventManager....")
		CvEventManager.CvEventManager().onKbdEvent(argsList)
		
	def onGameStart(self, argsList):
		'Called at the start of the game'
		self.setTutorialOption(PlayerOptionTypes.PLAYEROPTION_WAIT_END_TURN, True)
		self.setTutorialOption(PlayerOptionTypes.PLAYEROPTION_SHOW_FRIENDLY_MOVES, True)
		self.setTutorialOption(PlayerOptionTypes.PLAYEROPTION_SHOW_ENEMY_MOVES, True)
		# this is also set at the beginning of every player turn
		self.setTutorialOption(PlayerOptionTypes.PLAYEROPTION_START_AUTOMATED, False)
		# only allow english to have numpad
		self.setTutorialOption(PlayerOptionTypes.PLAYEROPTION_NUMPAD_HELP, False)
		if CyGame().getCurrentLanguage() == 0:
			self.setTutorialOption(PlayerOptionTypes.PLAYEROPTION_NUMPAD_HELP, True)
		
		gc.getPlayer(0).setFeatAccomplished(FeatTypes.FEAT_UNITCOMBAT_MELEE, True)
		gc.getPlayer(0).setFeatAccomplished(FeatTypes.FEAT_TRADE_ROUTE, True)
		
		self.screen.startTutorial(self.screen.FirstTutorialInfoType)
		self.screen.setCloseOnEscape(false)
		self.tutorial.setHighAdvisorCenter()
		
	def setTutorialOption(self, iOption, bOn = True):
		CyMessageControl().sendPlayerOption(int(iOption), bOn)

	def onGameEnd(self, argsList):
		'Called at the End of the game'
		self.screen.clearScreen()
		return

	def onCityBuildingUnit(self, argsList):
		'City begins building a unit'
		pCity = argsList[0]
		iUnitType = argsList[1]
		CvUtil.pyPrint("%s has begun building a %s" %(pCity.getName(),gc.getUnitInfo(iUnitType).getDescription()))
		if self.tutorial.bWaitForBuildSelectionWarrior and iUnitType == CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),"UNIT_WARRIOR"):
			self.tutorial.bWaitForBuildSelectionWarrior = False
			print ("doNextInfo onCityBuildingUnit1")
			self.screen.doNextInfo()
		if self.tutorial.bWaitForBuildSelectionScout and iUnitType == CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),"UNIT_SCOUT"): 
			self.tutorial.bWaitForBuildSelectionScout = False
			print ("doNextInfo onCityBuildingUnit2")
			self.screen.doNextInfo()
		if self.tutorial.bWaitForBuildSelectionWorker and iUnitType == CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),"UNIT_WORKER"): 
			self.tutorial.bWaitForBuildSelectionWorker = False
			print ("doNextInfo onCityBuildingUnit3")
			self.screen.doNextInfo()
		if self.tutorial.bWaitForBuildSelectionSettler and iUnitType == CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),"UNIT_SETTLER"): 
			self.tutorial.bWaitForBuildSelectionSettler = False
			print ("doNextInfo onCityBuildingUnit4")
			self.screen.doNextInfo()	
	
	def onWindowActivation(self, argsList):
		'Called when the game window activates or deactivates'
		bActive = argsList[0]
		if bActive and self.tutorial.bTutorialBegun and self.screen.getScreen().isActive():
			if self.tutorial.bTutorialComplete == False:
				self.screen.doScreenRefresh ()
				self.screen.setLeaderheadAdvisor( 0 )
				if self.tutorial.bHideContinueButton:
					self.screen.doHideOKButton()

	
	def onCityBuildingBuilding(self, argsList):
		'City begins building a Building'
		pCity = argsList[0]
		iBuildingType = argsList[1]
		CvUtil.pyPrint("%s has begun building a %s" %(pCity.getName(),gc.getBuildingInfo(iBuildingType).getDescription()))
		if self.tutorial.bWaitForBuildSelectionObelisk:
			self.tutorial.bWaitForBuildSelectionObelisk = False
			print ("doNextInfo onCityBuildingBuilding1")
			self.screen.doNextInfo()
		if self.tutorial.bWaitForBuildSelectionBarracks:
			self.tutorial.bWaitForBuildSelectionBarracks = False
			print ("doNextInfo onCityBuildingBuilding2")
			self.screen.doNextInfo()
		if self.tutorial.bWaitForBuildSelectionStonehenge:
			self.tutorial.bWaitForBuildSelectionStonehenge = False
			print ("doNextInfo onCityBuildingBuilding3")
			self.screen.doNextInfo()
		
	def onUnitSelected(self, argsList):
		unit = argsList[0]
		iOwner = unit.getOwner()
		player = PyPlayer(iOwner)
		if self.tutorial.bWaitForSelectedUnit:
			if unit.getScriptData() == self.tutorial.SelectedUnit:
				self.tutorial.bWaitForSelectedUnit = False
				self.screen.bWaitToContinue = False
				print ("doNextInfo onUnitSelected")
				self.screen.doNextInfo()
		
	def onUnitMove(self, argsList):
		pPlot,pUnit = argsList
		if self.tutorial.bWaitForReturnFirstCity == True:
			if pUnit.getScriptData() == "FIRST_WARRIOR" and pPlot.getX() == 33 and pPlot.getY() == 14:
				self.tutorial.bWaitForReturnFirstCity = False
				self.screen.doNextInfo()			
		if self.tutorial.bWaitForMoveToSecondCity:
			if pUnit.getScriptData() == "SECOND_SETTLER" and pPlot.getX() == 34 and pPlot.getY() == 9:
				self.tutorial.bWaitForMoveToSecondCity = False
				self.screen.doNextInfo()
		if self.tutorial.bWaitForWorkerArriveStone == True:
			if pUnit.getUnitType() == CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), "UNIT_WORKER") and pPlot.getX() == 33 and pPlot.getY() == 10:
				self.tutorial.bWaitForWorkerArriveStone = False
				self.screen.doNextInfo()
		
	def onBeginPlayerTurn(self, argsList):
		'Called at the beginning of a players turn'
		iGameTurn, iPlayer = argsList
		player = gc.getPlayer(iPlayer)
		# to prevent the worker from starting and thus breaking progression
		self.setTutorialOption(PlayerOptionTypes.PLAYEROPTION_START_AUTOMATED, False)
		if iPlayer == 0:
			if not self.tutorial.bTutorialComplete:
				for i in range (player.getNumCities()):
					if player.getCity(i).isProductionAutomated():
						player.getCity(i).setProductionAutomated ( False )
			
			if self.tutorial.bWaitForBeginPlayerTurn:
				self.tutorial.bWaitForBeginPlayerTurn = False
				self.screen.doNextInfo()
		if self.tutorial.bIncreasedProductionRome:
				self.tutorial.FirstCity.changeProduction(8)
	
	def onEndTurnReady(self, argsList):
		iGameTurn = argsList[0]

	def onCityBuilt(self, argsList):
#		CvEventManager.CvEventManager().onCityBuild(argsList)
		city = argsList[0]
		if (city.getOwner() == 0 and gc.getPlayer(0).getNumCities() == 1):
			self.tutorial.FirstCity = city
			self.tutorial.bWaitForUnitAction = False
			self.screen.doNextInfo()
		if (city.getOwner() == 0 and gc.getPlayer(0).getNumCities() == 2):
			self.tutorial.SecondCity = city
			self.tutorial.bWaitForUnitAction = False
			self.screen.doNextInfo()

	def onUnitCreated(self, argsList):
		'Unit Completed'
#		print argsList
		unit = argsList[0]
		iOwner = unit.getOwner()
		player = PyPlayer(iOwner)
		print ("Unit is %s" %(unit.getUnitType()))
		if iOwner  == 0:
			self.iUnitsCreated += 1
			print ("%s units have been created" %(self.iUnitsCreated))
			if self.iUnitsCreated == 2:
				unit.setScriptData("FIRST_WARRIOR")
				print ("Warrior is named")
			elif self.iUnitsCreated == 3:
				unit.setScriptData("FIRST_SCOUT")
			elif self.iUnitsCreated == 4:
				unit.setScriptData("FIRST_WORKER")
			elif self.iUnitsCreated == 5:
				unit.setScriptData("SECOND_WARRIOR")
			elif self.iUnitsCreated == 6:
				unit.setScriptData("SECOND_SETTLER")
				
		if self.tutorial.bWaitForWorkerToFinishBuilding and unit.getUnitType() == CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),"UNIT_WORKER"):
			self.tutorial.bWaitForWorkerToFinishBuilding = False
			self.screen.doNextInfo()
		if self.tutorial.bWaitForWarriorToFinishBuilding and unit.getUnitType() == CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),"UNIT_WARRIOR"):
			self.tutorial.bWaitForWarriorToFinishBuilding = False
			self.screen.doNextInfo()	
		if self.tutorial.bWaitForSettlerToFinishBuilding and unit.getUnitType() == CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),"UNIT_SETTLER"):
			self.tutorial.bWaitForSettlerToFinishBuilding = False
			self.screen.doNextInfo()	
		
	def onBeginGameTurn(self, argsList):
		'Called at the beginning of the end of each turn'
		iGameTurn = argsList[0]
		if not self.tutorial.bTutorialComplete:
			self.setTutorialOption(PlayerOptionTypes.PLAYEROPTION_AUTO_PROMOTION,0)
				
	def onMouseEvent(self, argsList):
		'mouse handler - returns 1 if the event was consumed'
		eventType,mx,my,px,py,interfaceConsumed,screens = argsList
		if self.tutorial.bDisableMainInteraceMouseInput == True and screens == 99:
			return 1
		
		if ( px!=-1 and py!=-1 ):
			if self.tutorial.bCannotMouseMapInput == True:
				return 1
			if self.tutorial.bWaitForEscapeCityScreen == True:
				return 1
			if eventType == self.EventLcButtonDblClick and px != -1 and py != -1:
				if CyMap().plot(px,py).isCity():
					if self.tutorial.bCanOpenCityScreen == False:
						self.tutorial.doErrorPopup("TXT_KEY_TUTORIAL_ERROR_CANNOT_OPEN_CITY")
						return True
					if self.tutorial.bWaitForOpenCityScreen == True:
						self.tutorial.bWaitForOpenCityScreen = False
						print ("doNextInfo onMouseEvent")
						self.screen.doNextInfo()
			
			if ( eventType == self.EventLButtonDown ):

				if ( self.bCtrl and self.bAlt and CyMap().plot(px,py).isCity() and not interfaceConsumed):
					# Launch Edit City Event
					self.beginEvent( CvUtil.EventEditCity, (px,py) )
					return 1
				
				elif ( self.bCtrl and self.bShift and not interfaceConsumed):
					# Launch Place Object Event
					self.beginEvent( CvUtil.EventPlaceObject, (px, py) )
					return 1
			
			elif ( eventType == self.EventBack ):
				return CvScreensInterface.handleBack()
			elif ( eventType == self.EventForward ):
				return CvScreensInterface.handleForward()
		
		return 0

	def onImprovementBuilt(self, argsList):
		'Improvement Built'
		iImprovement, iX, iY = argsList
		if self.tutorial.bWaitForWorkerToBuild:
			if iImprovement == CvUtil.findInfoTypeNum(gc.getImprovementInfo,gc.getNumImprovementInfos(),"IMPROVEMENT_FARM") and iX == 32 and iY == 13:
				self.tutorial.bWaitForWorkerToBuild = False
				self.tutorial.bWaitForBeginPlayerTurn = True
			elif iImprovement == CvUtil.findInfoTypeNum(gc.getImprovementInfo,gc.getNumImprovementInfos(),"IMPROVEMENT_COTTAGE") and iX == 32 and iY == 14:
				self.tutorial.bWaitForWorkerToBuild = False
				self.tutorial.bWaitForBeginPlayerTurn = True
			elif iImprovement == CvUtil.findInfoTypeNum(gc.getImprovementInfo,gc.getNumImprovementInfos(),"IMPROVEMENT_MINE") and iX == 32 and iY == 15:
				self.tutorial.bWaitForWorkerToBuild = False
				self.tutorial.bWaitForBeginPlayerTurn = True
			elif iImprovement == CvUtil.findInfoTypeNum(gc.getImprovementInfo,gc.getNumImprovementInfos(),"IMPROVEMENT_QUARRY") and iX == 33 and iY == 10:
				self.tutorial.bWaitForWorkerToBuild = False
				self.tutorial.bWaitForBeginPlayerTurn = True


	def onRouteBuilt(self, argsList):
		'Route Built'
		iRoute, iX, iY = argsList
		if self.tutorial.bWaitForWorkerToBuildRoad:
			if iRoute == CvUtil.findInfoTypeNum(gc.getRouteInfo,gc.getNumRouteInfos(),"ROUTE_ROAD"):
				if self.tutorial.bWaitForWorkerToBuildRoad == True:
					if iX == 33 and iY == 13:
						self.tutorial.bWaitForWorkerToBuildRoad = False
						self.screen.doNextInfo()
					if iX == 32 and iY == 13:
						self.tutorial.bWaitForWorkerToBuildRoad = False
						self.screen.doNextInfo()
	
	def onBuildingBuilt(self, argsList):
		'Building Completed'
		pCity, iBuildingType = argsList
		game = CyGame()
		
		if self.tutorial.bTutorialComplete:
			if ((not self.bMultiPlayer) and (pCity.getOwner() == CyGame().getActivePlayer()) and isWorldWonderClass(gc.getBuildingInfo(iBuildingType).getBuildingClassType())):
				# If this is a wonder...
				popupInfo = CyPopupInfo()
				popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON_SCREEN)
				popupInfo.setData1(iBuildingType)
				popupInfo.setData2(pCity.getID())
				popupInfo.setData3(0)
				popupInfo.setText(u"showWonderMovie")
				popupInfo.addPopup(pCity.getOwner())

		CvAdvisorUtils.buildingBuiltFeats(pCity, iBuildingType)

		if self.tutorial.bWaitForBarracksToBuild:
			if iBuildingType == CvUtil.findInfoTypeNum(gc.getBuildingInfo,gc.getNumBuildingInfos(),"BUILDING_BARRACKS"):
				self.tutorial.bWaitForBarracksToBuild = False
				print ("doNextInfo onBuildingBuilt")
				self.screen.doNextInfo()

	def onUnitPromoted(self, argsList):
		'Unit Promoted'
		pUnit, iPromotion = argsList
		player = PyPlayer(pUnit.getOwner())
		CvUtil.pyPrint('Unit Promotion Event: %s - %s' %(player.getCivilizationName(), pUnit.getName(),))
		if self.tutorial.bWaitForPromotion:
			self.tutorial.bWaitForPromotion = False
			self.tutorial.bWaitForUnitAction = False
			print ("doNextInfo onUnitPromoted")
			self.screen.doNextInfo()
			
	def onTechSelected(self, argsList):
		'Tech Selected'
		iTechType, iPlayer = argsList
		if self.tutorial.bWaitForResearchSelection and iPlayer == 0:
			self.tutorial.bWaitForResearchSelection = False
			print ("doNextInfo onTechSelected")
			self.screen.doNextInfo()

	def onTechAcquired(self, argsList):
		'Tech Acquired'
		iTechType, iTeam, iPlayer, bAnnounce = argsList
		# Note that iPlayer may be NULL (-1) and not a refer to a player object
				
		if self.tutorial.bWaitForResearchDiscovered and iTeam == 0:
			self.tutorial.bWaitForResearchDiscovered = False
			self.screen.doNextInfo()

		# Show tech splash when applicable
		if self.tutorial.bShowTechSplash:
			if (iPlayer > -1 and bAnnounce == true):
				if (gc.getGame().isFinalInitialized() and not gc.getGame().GetWorldBuilderMode()):
					if ((not self.bMultiPlayer) and (iPlayer == CyGame().getActivePlayer())):
						popupInfo = CyPopupInfo()
						popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON_SCREEN)
						popupInfo.setData1(iTechType)
						popupInfo.setText(u"showTechSplash")
						popupInfo.addPopup(iPlayer)

	def onFirstContact(self, argsList):
		'Contact'
		iTeamX,iHasMetTeamY = argsList
		CvUtil.pyPrint('Team %d has met Team %d' %(iTeamX, iHasMetTeamY))
		if self.tutorial.bWaitForFirstContact:
			self.tutorial.bWaitForFirstContact = False
			print ("doNextInfo onFirstContact")
			self.screen.doNextInfo()
			
	def onCombatResult(self, argsList):
		'Combat Result'
		pWinner,pLoser = argsList
		if self.tutorial.bWaitForUnitCombat:
			self.tutorial.bWaitForUnitCombat = False
			print ("doNextInfo onCombatResults")
			self.screen.doNextInfo()

	def onReligionFounded(self, argsList):
		'Religion Founded'
		iReligion, iFounder = argsList
		player = PyPlayer(iFounder)
		iCityId = gc.getGame().getHolyCity(iReligion).getID()
		if self.tutorial.bTutorialComplete:
			if (gc.getGame().isFinalInitialized() and not gc.getGame().GetWorldBuilderMode()):
				if ((not self.bMultiPlayer) and (iFounder == CyGame().getActivePlayer())):
					popupInfo = CyPopupInfo()
					popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON_SCREEN)
					popupInfo.setData1(iReligion)
					popupInfo.setData2(iCityId)
					popupInfo.setData3(1)
					popupInfo.setText(u"showWonderMovie")
					popupInfo.addPopup(iFounder)
	
	def onUpdate(self, argsList):
		'Called every frame'
		fDeltaTime = argsList[0]
		
		if self.tutorial.bWatchCityScreen:
			if not CyInterface().isCityScreenUp():
				self.tutorial.bWatchCityScreen = False
				self.tutorial.bWaitForEscapeCityScreen = False
				self.screen.doNextInfo()
		
		if self.tutorial.bTutorialBegun:
			if not self.tutorial.bTutorialComplete:
				self.screen.show( "Background" )

		# allow camera to be updated
		CvCameraControls.g_CameraControls.onUpdate( fDeltaTime )
