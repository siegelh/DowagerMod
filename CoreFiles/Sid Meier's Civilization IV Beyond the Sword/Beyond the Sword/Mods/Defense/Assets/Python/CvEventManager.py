## Sid Meier's Civilization 4
## Copyright Firaxis Games 2006
## 
## CvEventManager
## This class is passed an argsList from CvAppInterface.onEvent
## The argsList can contain anything from mouse location to key info
## The EVENTLIST that are being notified can be found 


from CvPythonExtensions import *
import CvUtil
import CvScreensInterface
import CvDebugTools
import CvWBPopups
import PyHelpers
import Popup as PyPopup
import CvCameraControls
import CvTopCivs
import sys
import CvWorldBuilderScreen
import CvAdvisorUtils
import CvTechChooser
import pickle


gc = CyGlobalContext()
localText = CyTranslator()
PyPlayer = PyHelpers.PyPlayer
PyInfo = PyHelpers.PyInfo


# globals
###################################################
class CvEventManager:
	def __init__(self):
		#################### ON EVENT MAP ######################
		#Defense variables
		#private
		self.clearDefenseVariables()
		
		#print "EVENTMANAGER INIT"
						
		self.bCtrl = False
		self.bShift = False
		self.bAlt = False
		self.bAllowCheats = False
		
		# OnEvent Enums
		self.EventLButtonDown=1
		self.EventLcButtonDblClick=2
		self.EventRButtonDown=3
		self.EventBack=4
		self.EventForward=5
		self.EventKeyDown=6
		self.EventKeyUp=7
	
		self.__LOG_MOVEMENT = 0
		self.__LOG_BUILDING = 0
		self.__LOG_COMBAT = 0
		self.__LOG_CONTACT = 0
		self.__LOG_IMPROVEMENT =0
		self.__LOG_CITYLOST = 0
		self.__LOG_CITYBUILDING = 0
		self.__LOG_TECH = 0
		self.__LOG_UNITBUILD = 0
		self.__LOG_UNITKILLED = 0
		self.__LOG_UNITLOST = 0
		self.__LOG_UNITPROMOTED = 0
		self.__LOG_UNITSELECTED = 0
		self.__LOG_UNITPILLAGE = 0
		self.__LOG_GOODYRECEIVED = 0
		self.__LOG_GREATPERSON = 0
		self.__LOG_RELIGION = 0
		self.__LOG_RELIGIONSPREAD = 0
		self.__LOG_GOLDENAGE = 0
		self.__LOG_ENDGOLDENAGE = 0
		self.__LOG_WARPEACE = 0
		self.__LOG_PUSH_MISSION = 0
		self.DemoCount = 0
		
		## EVENTLIST
		self.EventHandlerMap = {
			'mouseEvent'			: self.onMouseEvent,
			'kbdEvent' 				: self.onKbdEvent,
			'ModNetMessage'					: self.onModNetMessage,
			'Init'					: self.onInit,
			'Update'				: self.onUpdate,
			'UnInit'				: self.onUnInit,
			'OnSave'				: self.onSaveGame,
			'OnPreSave'				: self.onPreSave,
			'OnLoad'				: self.onLoadGame,
			'GameStart'				: self.onGameStart,
			'GameEnd'				: self.onGameEnd,
			'plotRevealed' 			: self.onPlotRevealed,
			'plotFeatureRemoved' 	: self.onPlotFeatureRemoved,
			'plotPicked'			: self.onPlotPicked,
			'nukeExplosion'			: self.onNukeExplosion,
			'gotoPlotSet'			: self.onGotoPlotSet,
			'BeginGameTurn'			: self.onBeginGameTurn,
			'EndGameTurn'			: self.onEndGameTurn,
			'BeginPlayerTurn'		: self.onBeginPlayerTurn,
			'EndPlayerTurn'			: self.onEndPlayerTurn,
			'endTurnReady'			: self.onEndTurnReady,
			'combatResult' 			: self.onCombatResult,
		  'combatLogCalc'	 		: self.onCombatLogCalc,
		  'combatLogHit'				: self.onCombatLogHit,
			'improvementBuilt' 		: self.onImprovementBuilt,
			'improvementDestroyed' 		: self.onImprovementDestroyed,
			'routeBuilt' 		: self.onRouteBuilt,
			'firstContact' 			: self.onFirstContact,
			'cityBuilt' 			: self.onCityBuilt,
			'cityRazed'				: self.onCityRazed,
			'cityAcquired' 			: self.onCityAcquired,
			'cityAcquiredAndKept' 	: self.onCityAcquiredAndKept,
			'cityLost'				: self.onCityLost,
			'cultureExpansion' 		: self.onCultureExpansion,
			'cityGrowth' 			: self.onCityGrowth,
			'cityDoTurn' 			: self.onCityDoTurn,
			'cityBuildingUnit'	: self.onCityBuildingUnit,
			'cityBuildingBuilding'	: self.onCityBuildingBuilding,
			'cityRename'				: self.onCityRename,
			'cityHurry'				: self.onCityHurry,
			'selectionGroupPushMission'		: self.onSelectionGroupPushMission,
			'unitMove' 				: self.onUnitMove,
			'unitSetXY' 			: self.onUnitSetXY,
			'unitCreated' 			: self.onUnitCreated,
			'unitBuilt' 			: self.onUnitBuilt,
			'unitKilled'			: self.onUnitKilled,
			'unitLost'				: self.onUnitLost,
			'unitPromoted'			: self.onUnitPromoted,
			'unitSelected'			: self.onUnitSelected, 
			'UnitRename'				: self.onUnitRename,
			'unitPillage'				: self.onUnitPillage,
			'unitSpreadReligionAttempt'	: self.onUnitSpreadReligionAttempt,
			'unitGifted'				: self.onUnitGifted,
			'unitBuildImprovement'				: self.onUnitBuildImprovement,
			'goodyReceived'        	: self.onGoodyReceived,
			'greatPersonBorn'      	: self.onGreatPersonBorn,
			'buildingBuilt' 		: self.onBuildingBuilt,
			'projectBuilt' 			: self.onProjectBuilt,
			'techAcquired'			: self.onTechAcquired,
			'techSelected'			: self.onTechSelected,
			'religionFounded'		: self.onReligionFounded,
			'religionSpread'		: self.onReligionSpread, 
			'religionRemove'		: self.onReligionRemove, 
			'corporationFounded'	: self.onCorporationFounded,
			'corporationSpread'		: self.onCorporationSpread, 
			'corporationRemove'		: self.onCorporationRemove, 
			'goldenAge'				: self.onGoldenAge,
			'endGoldenAge'			: self.onEndGoldenAge,
			'chat' 					: self.onChat,
			'victory'				: self.onVictory,
			'vassalState'			: self.onVassalState,
			'changeWar'				: self.onChangeWar,
			'setPlayerAlive'		: self.onSetPlayerAlive,
			'playerChangeStateReligion'		: self.onPlayerChangeStateReligion,
			'playerGoldTrade'		: self.onPlayerGoldTrade,
			'windowActivation'		: self.onWindowActivation,
			'gameUpdate'			: self.onGameUpdate,		# sample generic event
		}

		################## Events List ###############################
		#
		# Dictionary of Events, indexed by EventID (also used at popup context id)
		#   entries have name, beginFunction, applyFunction [, randomization weight...]
		#
		# Normal events first, random events after
		#	
		################## Events List ###############################
		self.Events={
			CvUtil.EventEditCityName : ('EditCityName', self.__eventEditCityNameApply, self.__eventEditCityNameBegin),
			CvUtil.EventEditCity : ('EditCity', self.__eventEditCityApply, self.__eventEditCityBegin),
			CvUtil.EventPlaceObject : ('PlaceObject', self.__eventPlaceObjectApply, self.__eventPlaceObjectBegin),
			CvUtil.EventAwardTechsAndGold: ('AwardTechsAndGold', self.__eventAwardTechsAndGoldApply, self.__eventAwardTechsAndGoldBegin),
			CvUtil.EventEditUnitName : ('EditUnitName', self.__eventEditUnitNameApply, self.__eventEditUnitNameBegin),
			CvUtil.EventWBAllPlotsPopup : ('WBAllPlotsPopup', self.__eventWBAllPlotsPopupApply, self.__eventWBAllPlotsPopupBegin),
			CvUtil.EventWBLandmarkPopup : ('WBLandmarkPopup', self.__eventWBLandmarkPopupApply, self.__eventWBLandmarkPopupBegin),
			CvUtil.EventWBScriptPopup : ('WBScriptPopup', self.__eventWBScriptPopupApply, self.__eventWBScriptPopupBegin),
			CvUtil.EventWBStartYearPopup : ('WBStartYearPopup', self.__eventWBStartYearPopupApply, self.__eventWBStartYearPopupBegin),
			CvUtil.EventShowWonder: ('ShowWonder', self.__eventShowWonderApply, self.__eventShowWonderBegin),
		}	
#################### EVENT STARTERS ######################
	def handleEvent(self, argsList):
		'EventMgr entry point'
		# extract the last 6 args in the list, the first arg has already been consumed
		self.origArgsList = argsList	# point to original
		tag = argsList[0]				# event type string
		idx = len(argsList)-6
		bDummy = false
		self.bDbg, bDummy, self.bAlt, self.bCtrl, self.bShift, self.bAllowCheats = argsList[idx:]
		ret = 0
		if self.EventHandlerMap.has_key(tag):
			fxn = self.EventHandlerMap[tag]
			ret = fxn(argsList[1:idx])
		return ret
		
#################### EVENT APPLY ######################	
	def beginEvent( self, context, argsList=-1 ):
		'Begin Event'
		entry = self.Events[context]
		return entry[2]( argsList )
	
	def applyEvent( self, argsList ):
		'Apply the effects of an event '
		context, playerID, netUserData, popupReturn = argsList
		
		if context == CvUtil.PopupTypeEffectViewer:
			return CvDebugTools.g_CvDebugTools.applyEffectViewer( playerID, netUserData, popupReturn )
		
		entry = self.Events[context]
				
		if ( context not in CvUtil.SilentEvents ):
			self.reportEvent(entry, context, (playerID, netUserData, popupReturn) )
		return entry[1]( playerID, netUserData, popupReturn )   # the apply function

	def reportEvent(self, entry, context, argsList):
		'Report an Event to Events.log '
		if (gc.getGame().getActivePlayer() != -1):
			message = "DEBUG Event: %s (%s)" %(entry[0], gc.getActivePlayer().getName())
			CyInterface().addImmediateMessage(message,"")
			CvUtil.pyPrint(message)
		return 0
		
#################### ON EVENTS ######################
	def onKbdEvent(self, argsList):
		'keypress handler - return 1 if the event was consumed'

		eventType,key,mx,my,px,py = argsList
		game = gc.getGame()
		
		if (self.bAllowCheats):
			# notify debug tools of input to allow it to override the control
			argsList = (eventType,key,self.bCtrl,self.bShift,self.bAlt,mx,my,px,py,gc.getGame().isNetworkMultiPlayer())
			if ( CvDebugTools.g_CvDebugTools.notifyInput(argsList) ):
				return 0
		
		if ( eventType == self.EventKeyDown ):
			theKey=int(key)
			
			CvCameraControls.g_CameraControls.handleInput( theKey )
						
			if (self.bAllowCheats):
				# Shift - T (Debug - No MP)
				if (theKey == int(InputTypes.KB_T)):
					if ( self.bShift ):
						self.beginEvent(CvUtil.EventAwardTechsAndGold)
						return 1
							
				elif (theKey == int(InputTypes.KB_W)):
					if ( self.bShift and self.bCtrl):
						self.beginEvent(CvUtil.EventShowWonder)
						return 1
					
				elif (theKey == int(InputTypes.KB_F1)):
					if ( self.bShift ):
						CvScreensInterface.replayScreen.showScreen(False)
						return 1
					# don't return 1 unless you want the input consumed
				
				elif (theKey == int(InputTypes.KB_F2)):
					if ( self.bShift ):
						import CvDebugInfoScreen
						CvScreensInterface.showDebugInfoScreen()
						return 1
				
				elif (theKey == int(InputTypes.KB_F3)):
					if ( self.bShift ):
						CvScreensInterface.showDanQuayleScreen(())
						return 1
						
				elif (theKey == int(InputTypes.KB_F4)):
					if ( self.bShift ):
						CvScreensInterface.showUnVictoryScreen(())
						return 1
				
				elif (self.bCtrl and self.bShift and theKey == int(InputTypes.KB_O)):
					popupInfo = CyPopupInfo()
					popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON_SCREEN)
					popupInfo.setData1(CvUtil.findInfoTypeNum(gc.getBuildingInfo, gc.getNumBuildingInfos(), "BUILDING_APOSTOLIC_PALACE"))
					popupInfo.setData2(gc.getPlayer(0).getCity(7).getID())
					popupInfo.setData3(0)
					popupInfo.setText(u"showWonderMovie")
					popupInfo.addPopup(0)
					return 1
					
		return 0

	def onModNetMessage(self, argsList):
		'Called whenever CyMessageControl().sendModNetMessage() is called - this is all for you modders!'
		
		iData1, iData2, iData3, iData4, iData5 = argsList
		
		print("Modder's net message!")
		
		CvUtil.pyPrint( 'onModNetMessage' )

	def onInit(self, argsList):
		'Called when Civ starts up'
		CvUtil.pyPrint( 'OnInit' )
		
	def onUpdate(self, argsList):
		'Called every frame'
		fDeltaTime = argsList[0]

#		if CyInterface( ).isInAdvancedStart( ):
#			self.bIsInAdvancedStart = 1
#		else:
#			self.bIsInAdvancedStart = 0

		# allow camera to be updated
		CvCameraControls.g_CameraControls.onUpdate( fDeltaTime )
		
	def onWindowActivation(self, argsList):
		'Called when the game window activates or deactivates'
		bActive = argsList[0]
		
	def onUnInit(self, argsList):
		'Called when Civ shuts down'
		CvUtil.pyPrint('OnUnInit')
	
	def onPreSave(self, argsList):
		"called before a game is actually saved"
		CvUtil.pyPrint('OnPreSave')
		self.setDefenseVariables()
	
	def onSaveGame(self, argsList):
		"return the string to be saved - Must be a string"
		return ""

	def onLoadGame(self, argsList):
		self.iGameLevel = 1
		self.iSpawnGameTurn = 5
		self.iTotalMobs = 10
		self.iMobsKilled = 0
		self.getDefenseVariables()
		return 0

	def onGameStart(self, argsList):
		'Called at the start of the game'
		
		self.clearDefenseVariables()
		self.doHutRepopulation( )
		if (gc.getGame().getStartEra() == gc.getDefineINT("STANDARD_ERA") or gc.getGame().isOption(GameOptionTypes.GAMEOPTION_ADVANCED_START)):
			for iPlayer in range(gc.getMAX_PLAYERS()):
				player = gc.getPlayer(iPlayer)
				if (player.isAlive() and player.isHuman()):
					popupInfo = CyPopupInfo()
					popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON_SCREEN)
					popupInfo.setText(u"showDawnOfMan")
					popupInfo.addPopup(iPlayer)
		else:
			CyInterface().setSoundSelectionReady(true)

		if gc.getGame().isPbem():
			for iPlayer in range(gc.getMAX_PLAYERS()):
				player = gc.getPlayer(iPlayer)
				if (player.isAlive() and player.isHuman()):
					popupInfo = CyPopupInfo()
					popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_DETAILS)
					popupInfo.setOption1(true)
					popupInfo.addPopup(iPlayer)

		gc.getMap().plotByIndex(0).setScriptData("Round_1")
																	
	def onGameEnd(self, argsList):
		'Called at the End of the game'
		print("Game is ending")
		return

	def onBeginGameTurn(self, argsList):
		'Called at the beginning of the end of each turn'
		iGameTurn = argsList[0]
		#CvTopCivs.CvTopCivs().turnChecker(iGameTurn)
		self.doMonsterMachine( iGameTurn )

	def onEndGameTurn(self, argsList):
		'Called at the end of the end of each turn'
		iGameTurn = argsList[0]

		self.iTurnTimer	= 0
		self.bTurnTimerOff = 1		
		
		if self.iTotalMobs <= self.iMobsKilled:
			self.doLevelChange( iGameTurn )
		
	def onBeginPlayerTurn(self, argsList):
		'Called at the beginning of a players turn'
		iGameTurn, iPlayer = argsList

		iNumPlots = gc.getMap().numPlots()
		
#		for i in range( iNumPlots ):
#			gc.getMap().plotByIndex( i ).changeVisibilityCount(0 , 1, InvisibleTypes.NO_INVISIBLE)

	def onEndPlayerTurn(self, argsList):
		'Called at the end of a players turn'
		iGameTurn, iPlayer = argsList
		
		if (gc.getGame().getElapsedGameTurns() == 1):
			if (gc.getPlayer(iPlayer).isHuman()):
				if (gc.getPlayer(iPlayer).canRevolution(0)):
					popupInfo = CyPopupInfo()
					popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_CHANGECIVIC)
					popupInfo.addPopup(iPlayer)
		
		CvAdvisorUtils.resetAdvisorNags()
		CvAdvisorUtils.endTurnFeats(iPlayer)

	def onEndTurnReady(self, argsList):
		iGameTurn = argsList[0]

	def onFirstContact(self, argsList):
		'Contact'
		iTeamX,iHasMetTeamY = argsList
		if (not self.__LOG_CONTACT):
			return
		CvUtil.pyPrint('Team %d has met Team %d' %(iTeamX, iHasMetTeamY))
	
	def onCombatResult(self, argsList):
		'Combat Result'
		pWinner,pLoser = argsList
		playerX = PyPlayer(pWinner.getOwner())
		unitX = PyInfo.UnitInfo(pWinner.getUnitType())
		playerY = PyPlayer(pLoser.getOwner())
		unitY = PyInfo.UnitInfo(pLoser.getUnitType())

		if pWinner.getUnitType() == CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(), "UNIT_ZOMBIE"):
			self.spawnUnit( 1, "UNIT_ZOMBIE", pWinner.getX() ,pWinner.getY(), UnitAITypes.UNITAI_ATTACK_CITY_LEMMING)
			self.iMobsKilled += -1
		if pWinner.getUnitType() == CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(), "UNIT_GRENADIER"): 
			CyEngine().triggerEffect( 6, pWinner.plot().getPoint( ) )
			pWinner.kill( 1, PlayerTypes.NO_PLAYER )
		if pLoser.getUnitType() == CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(), "UNIT_GRENADIER"):
			pPlot = pWinner.plot()
			pWinner.NotifyEntity( MissionTypes.MISSION_DIE )
			CyEngine().triggerEffect( 6, pPlot.getPoint( ) )
#			pWinner.kill( 1, PlayerTypes.NO_PLAYER )
			self.doKillUnit( pWinner )
		

		if (not self.__LOG_COMBAT):
			return
		if playerX and playerX and unitX and playerY:
			CvUtil.pyPrint('Player %d Civilization %s Unit %s has defeated Player %d Civilization %s Unit %s' 
				%(playerX.getID(), playerX.getCivilizationName(), unitX.getDescription(), 
				playerY.getID(), playerY.getCivilizationName(), unitY.getDescription()))

	def onCombatLogCalc(self, argsList):
		'Combat Result'	
		genericArgs = argsList[0][0]
		cdAttacker = genericArgs[0]
		cdDefender = genericArgs[1]
		iCombatOdds = genericArgs[2]
		CvUtil.combatMessageBuilder(cdAttacker, cdDefender, iCombatOdds)
		
	def onCombatLogHit(self, argsList):
		'Combat Message'
		global gCombatMessages, gCombatLog
		genericArgs = argsList[0][0]
		cdAttacker = genericArgs[0]
		cdDefender = genericArgs[1]
		iIsAttacker = genericArgs[2]
		iDamage = genericArgs[3]
		
		if (iIsAttacker == 0):
			combatMessage = localText.getText("TXT_KEY_COMBAT_MESSAGE_HIT", (gc.getPlayer(cdDefender.eOwner).getNameKey(), cdDefender.sUnitName, iDamage, cdDefender.iCurrHitPoints, cdDefender.iMaxHitPoints))
			CyInterface().addCombatMessage(cdAttacker.eOwner,combatMessage)
			CyInterface().addCombatMessage(cdDefender.eOwner,combatMessage)
			if (cdDefender.iCurrHitPoints <= 0):
				combatMessage = localText.getText("TXT_KEY_COMBAT_MESSAGE_DEFEATED", (gc.getPlayer(cdAttacker.eOwner).getNameKey(), cdAttacker.sUnitName, gc.getPlayer(cdDefender.eOwner).getNameKey(), cdDefender.sUnitName))
				CyInterface().addCombatMessage(cdAttacker.eOwner,combatMessage)
				CyInterface().addCombatMessage(cdDefender.eOwner,combatMessage)
		elif (iIsAttacker == 1):
			combatMessage = localText.getText("TXT_KEY_COMBAT_MESSAGE_HIT", (gc.getPlayer(cdAttacker.eOwner).getNameKey(), cdAttacker.sUnitName, iDamage, cdAttacker.iCurrHitPoints, cdAttacker.iMaxHitPoints))
			CyInterface().addCombatMessage(cdAttacker.eOwner,combatMessage)
			CyInterface().addCombatMessage(cdDefender.eOwner,combatMessage)
			if (cdAttacker.iCurrHitPoints <= 0):
				combatMessage = localText.getText("TXT_KEY_COMBAT_MESSAGE_DEFEATED", (gc.getPlayer(cdDefender.eOwner).getNameKey(), cdDefender.sUnitName, gc.getPlayer(cdAttacker.eOwner).getNameKey(), cdAttacker.sUnitName))
				CyInterface().addCombatMessage(cdAttacker.eOwner,combatMessage)
				CyInterface().addCombatMessage(cdDefender.eOwner,combatMessage)

	def onImprovementBuilt(self, argsList):
		'Improvement Built'
		iImprovement, iX, iY = argsList
		if (not self.__LOG_IMPROVEMENT):
			return
		CvUtil.pyPrint('Improvement %s was built at %d, %d'
			%(PyInfo.ImprovementInfo(iImprovement).getDescription(), iX, iY))

	def onImprovementDestroyed(self, argsList):
		'Improvement Destroyed'
		iImprovement, iOwner, iX, iY = argsList
		if (not self.__LOG_IMPROVEMENT):
			return
		CvUtil.pyPrint('Improvement %s was Destroyed at %d, %d'
			%(PyInfo.ImprovementInfo(iImprovement).getDescription(), iX, iY))

	def onRouteBuilt(self, argsList):
		'Route Built'
		iRoute, iX, iY = argsList
		if (not self.__LOG_IMPROVEMENT):
			return
		CvUtil.pyPrint('Route %s was built at %d, %d'
			%(gc.getRouteInfo(iRoute).getDescription(), iX, iY))

	def onPlotRevealed(self, argsList):
		'Plot Revealed'
		pPlot = argsList[0]
		iTeam = argsList[1]

	def onPlotFeatureRemoved(self, argsList):
		'Plot Revealed'
		pPlot = argsList[0]
		iFeatureType = argsList[1]
		pCity = argsList[2] # This can be null

	def onPlotPicked(self, argsList):
		'Plot Picked'
		pPlot = argsList[0]
		CvUtil.pyPrint('Plot was picked at %d, %d'
			%(pPlot.getX(), pPlot.getY()))

	def onNukeExplosion(self, argsList):
		'Nuke Explosion'
		pPlot, pNukeUnit = argsList
		CvUtil.pyPrint('Nuke detonated at %d, %d'
			%(pPlot.getX(), pPlot.getY()))

	def onGotoPlotSet(self, argsList):
		'Nuke Explosion'
		pPlot, iPlayer = argsList

	def onBuildingBuilt(self, argsList):
		'Building Completed'
		pCity, iBuildingType = argsList
		game = gc.getGame()
		if ((not gc.getGame().isNetworkMultiPlayer()) and (pCity.getOwner() == gc.getGame().getActivePlayer()) and isWorldWonderClass(gc.getBuildingInfo(iBuildingType).getBuildingClassType())):
			# If this is a wonder...
			popupInfo = CyPopupInfo()
			popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON_SCREEN)
			popupInfo.setData1(iBuildingType)
			popupInfo.setData2(pCity.getID())
			popupInfo.setData3(0)
			popupInfo.setText(u"showWonderMovie")
			popupInfo.addPopup(pCity.getOwner())

		CvAdvisorUtils.buildingBuiltFeats(pCity, iBuildingType)

		if (not self.__LOG_BUILDING):
			return
		CvUtil.pyPrint('%s was finished by Player %d Civilization %s' 
			%(PyInfo.BuildingInfo(iBuildingType).getDescription(), pCity.getOwner(), gc.getPlayer(pCity.getOwner()).getCivilizationDescription(0)))
	
	def onProjectBuilt(self, argsList):
		'Project Completed'
		pCity, iProjectType = argsList
		game = gc.getGame()
		if ((not gc.getGame().isNetworkMultiPlayer()) and (pCity.getOwner() == gc.getGame().getActivePlayer())):
			popupInfo = CyPopupInfo()
			popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON_SCREEN)
			popupInfo.setData1(iProjectType)
			popupInfo.setData2(pCity.getID())
			popupInfo.setData3(2)
			popupInfo.setText(u"showWonderMovie")
			popupInfo.addPopup(pCity.getOwner())
				
	def onSelectionGroupPushMission(self, argsList):
		'selection group mission'
		eOwner = argsList[0]
		eMission = argsList[1]
		iNumUnits = argsList[2]
		listUnitIds = argsList[3]
		
		if (not self.__LOG_PUSH_MISSION):
			return
		if pHeadUnit:
			CvUtil.pyPrint("Selection Group pushed mission %d" %(eMission))
	
	def onUnitMove(self, argsList):
		'unit move'
		pPlot,pUnit,pOldPlot = argsList
		player = PyPlayer(pUnit.getOwner())
		unitInfo = PyInfo.UnitInfo(pUnit.getUnitType())
		
		if pOldPlot.getNumUnits > 0:
			self.doPlotUnitPowerModification( pOldPlot.getX( ), pOldPlot.getY( ) )
		self.doPlotUnitPowerModification( pPlot.getX( ), pPlot.getY( ) )
		
		
		
		if (not self.__LOG_MOVEMENT):
			return
		if player and unitInfo:
			CvUtil.pyPrint('Player %d Civilization %s unit %s is moving to %d, %d' 
				%(player.getID(), player.getCivilizationName(), unitInfo.getDescription(), 
				pUnit.getX(), pUnit.getY()))

	def doMapUnitPowerModification( self ):
		
		for i in range ( gc.getMap( ).numPlots( ) ):
			self.doPlotUnitPowerModification( gc.getMap( ).plotByIndex( i ).getX( ), gc.getMap( ).plotByIndex( i ).getY( ) )

	def doPlotUnitPowerModification( self, iX, iY ):
		plot = gc.getMap( ).plot( iX, iY )
		iPowerMod = -1
		
		if plot.getNumUnits( ):
			for i in range( plot.getNumUnits( ) ):
				if plot.getNumUnits( ) > 9:
					iPowerMod = 1
				else:
					iPowerMod = 10 - (plot.getNumUnits( ) -1)
				iUnitTypeStr = gc.getUnitInfo( plot.getUnit( i ).getUnitType( ) ).getCombat( )
				iNewUnitPower = (iUnitTypeStr * iPowerMod) // 10
				if iNewUnitPower > 0:
					plot.getUnit( i ).setBaseCombatStr( iNewUnitPower )
				else:
					plot.getUnit( i ).setBaseCombatStr( 1 )

	def onUnitSetXY(self, argsList):
		'units xy coords set manually'
		pPlot,pUnit = argsList
		player = PyPlayer(pUnit.getOwner())
		unitInfo = PyInfo.UnitInfo(pUnit.getUnitType())
		if (not self.__LOG_MOVEMENT):
			return
		
	def onUnitCreated(self, argsList):
		'Unit Completed'
		unit = argsList[0]
		player = PyPlayer(unit.getOwner())
		if (not self.__LOG_UNITBUILD):
			return

	def onUnitBuilt(self, argsList):
		'Unit Completed'
		city = argsList[0]
		unit = argsList[1]
		player = PyPlayer(city.getOwner())

		CvAdvisorUtils.unitBuiltFeats(city, unit)
		
		if (not self.__LOG_UNITBUILD):
			return
		CvUtil.pyPrint('%s was finished by Player %d Civilization %s' 
			%(PyInfo.UnitInfo(unit.getUnitType()).getDescription(), player.getID(), player.getCivilizationName()))
	
	def onUnitKilled(self, argsList):
		'Unit Killed'
		unit, iAttacker = argsList
		player = PyPlayer(unit.getOwner())
		attacker = PyPlayer(iAttacker)
		
		if (not self.__LOG_UNITKILLED):
			return
		CvUtil.pyPrint('Player %d Civilization %s Unit %s was killed by Player %d' 
			%(player.getID(), player.getCivilizationName(), PyInfo.UnitInfo(unit.getUnitType()).getDescription(), attacker.getID()))

	def onUnitLost(self, argsList):
		'Unit Lost'
		unit = argsList[0]
		player = PyPlayer(unit.getOwner())

		if player.getID() == 1:
			self.iMobsKilled += 1
#			szString = str(self.iMobsKilled) + ", " + str(unit.getUnitType())
#			self.addPopup( "mobskilled", szString)

		if (not self.__LOG_UNITLOST):
			return
		CvUtil.pyPrint('%s was lost by Player %d Civilization %s' 
			%(PyInfo.UnitInfo(unit.getUnitType()).getDescription(), player.getID(), player.getCivilizationName()))
	
	def onUnitPromoted(self, argsList):
		'Unit Promoted'
		pUnit, iPromotion = argsList
		player = PyPlayer(pUnit.getOwner())
		if (not self.__LOG_UNITPROMOTED):
			return
		CvUtil.pyPrint('Unit Promotion Event: %s - %s' %(player.getCivilizationName(), pUnit.getName(),))
	
	def onUnitSelected(self, argsList):
		'Unit Selected'
		unit = argsList[0]
		player = PyPlayer(unit.getOwner())
		if (not self.__LOG_UNITSELECTED):
			return
		CvUtil.pyPrint('%s was selected by Player %d Civilization %s' 
			%(PyInfo.UnitInfo(unit.getUnitType()).getDescription(), player.getID(), player.getCivilizationName()))
	
	def onUnitRename(self, argsList):
		'Unit is renamed'
		pUnit = argsList[0]
		if (pUnit.getOwner() == gc.getGame().getActivePlayer()):
			self.__eventEditUnitNameBegin(pUnit)
	
	def onUnitPillage(self, argsList):
		'Unit pillages a plot'
		pUnit, iImprovement, iRoute, iOwner = argsList
		iPlotX = pUnit.getX()
		iPlotY = pUnit.getY()
		pPlot = CyMap().plot(iPlotX, iPlotY)
		
		if (not self.__LOG_UNITPILLAGE):
			return
		CvUtil.pyPrint("Player %d's %s pillaged improvement %d and route %d at plot at (%d, %d)" 
			%(iOwner, PyInfo.UnitInfo(pUnit.getUnitType()).getDescription(), iImprovement, iRoute, iPlotX, iPlotY))
	
	def onUnitSpreadReligionAttempt(self, argsList):
		'Unit tries to spread religion to a city'
		pUnit, iReligion, bSuccess = argsList
		
		iX = pUnit.getX()
		iY = pUnit.getY()
		pPlot = CyMap().plot(iX, iY)
		pCity = pPlot.getPlotCity()
	
	def onUnitGifted(self, argsList):
		'Unit is gifted from one player to another'
		pUnit, iGiftingPlayer, pPlotLocation = argsList
	
	def onUnitBuildImprovement(self, argsList):
		'Unit begins enacting a Build (building an Improvement or Route)'
		pUnit, iBuild, bFinished = argsList

	def onGoodyReceived(self, argsList):
		'Goody received'
		iPlayer, pPlot, pUnit, iGoodyType = argsList
		if (not self.__LOG_GOODYRECEIVED):
			return
		CvUtil.pyPrint('%s received a goody' %(gc.getPlayer(iPlayer).getCivilizationDescription(0)),)
	
	def onGreatPersonBorn(self, argsList):
		'Unit Promoted'
		pUnit, iPlayer, pCity = argsList
		player = PyPlayer(iPlayer)
		if pUnit.isNone() or pCity.isNone():
			return
		if (not self.__LOG_GREATPERSON):
			return
		CvUtil.pyPrint('A %s was born for %s in %s' %(pUnit.getName(), player.getCivilizationName(), pCity.getName()))
	
	def onTechAcquired(self, argsList):
		'Tech Acquired'
		iTechType, iTeam, iPlayer, bAnnounce = argsList
		# Note that iPlayer may be NULL (-1) and not a refer to a player object
		
		# Show tech splash when applicable
		if (iPlayer > -1 and bAnnounce and not CyInterface().noTechSplash()):
			if (gc.getGame().isFinalInitialized() and not gc.getGame().GetWorldBuilderMode()):
				if ((not gc.getGame().isNetworkMultiPlayer()) and (iPlayer == gc.getGame().getActivePlayer())):
					popupInfo = CyPopupInfo()
					popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON_SCREEN)
					popupInfo.setData1(iTechType)
					popupInfo.setText(u"showTechSplash")
					popupInfo.addPopup(iPlayer)
				
		if (not self.__LOG_TECH):
			return
		CvUtil.pyPrint('%s was finished by Team %d' 
			%(PyInfo.TechnologyInfo(iTechType).getDescription(), iTeam))
	
	def onTechSelected(self, argsList):
		'Tech Selected'
		iTechType, iPlayer = argsList
		if (not self.__LOG_TECH):
			return
		CvUtil.pyPrint('%s was selected by Player %d' %(PyInfo.TechnologyInfo(iTechType).getDescription(), iPlayer))
	
	def onReligionFounded(self, argsList):
		'Religion Founded'
		iReligion, iFounder = argsList
		player = PyPlayer(iFounder)
		
		iCityId = gc.getGame().getHolyCity(iReligion).getID()
		if (gc.getGame().isFinalInitialized() and not gc.getGame().GetWorldBuilderMode()):
			if ((not gc.getGame().isNetworkMultiPlayer()) and (iFounder == gc.getGame().getActivePlayer())):
				popupInfo = CyPopupInfo()
				popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON_SCREEN)
				popupInfo.setData1(iReligion)
				popupInfo.setData2(iCityId)
				popupInfo.setData3(1)
				popupInfo.setText(u"showWonderMovie")
				popupInfo.addPopup(iFounder)
		
		if (not self.__LOG_RELIGION):
			return
		CvUtil.pyPrint('Player %d Civilization %s has founded %s'
			%(iFounder, player.getCivilizationName(), gc.getReligionInfo(iReligion).getDescription()))

	def onReligionSpread(self, argsList):
		'Religion Has Spread to a City'
		iReligion, iOwner, pSpreadCity = argsList
		player = PyPlayer(iOwner)
		if (not self.__LOG_RELIGIONSPREAD):
			return
		CvUtil.pyPrint('%s has spread to Player %d Civilization %s city of %s'
			%(gc.getReligionInfo(iReligion).getDescription(), iOwner, player.getCivilizationName(), pSpreadCity.getName()))

	def onReligionRemove(self, argsList):
		'Religion Has been removed from a City'
		iReligion, iOwner, pRemoveCity = argsList
		player = PyPlayer(iOwner)
		if (not self.__LOG_RELIGIONSPREAD):
			return
		CvUtil.pyPrint('%s has been removed from Player %d Civilization %s city of %s'
			%(gc.getReligionInfo(iReligion).getDescription(), iOwner, player.getCivilizationName(), pRemoveCity.getName()))
				
	def onCorporationFounded(self, argsList):
		'Corporation Founded'
		iCorporation, iFounder = argsList
		player = PyPlayer(iFounder)
		
		if (not self.__LOG_RELIGION):
			return
		CvUtil.pyPrint('Player %d Civilization %s has founded %s'
			%(iFounder, player.getCivilizationName(), gc.getCorporationInfo(iCorporation).getDescription()))

	def onCorporationSpread(self, argsList):
		'Corporation Has Spread to a City'
		iCorporation, iOwner, pSpreadCity = argsList
		player = PyPlayer(iOwner)
		if (not self.__LOG_RELIGIONSPREAD):
			return
		CvUtil.pyPrint('%s has spread to Player %d Civilization %s city of %s'
			%(gc.getCorporationInfo(iCorporation).getDescription(), iOwner, player.getCivilizationName(), pSpreadCity.getName()))

	def onCorporationRemove(self, argsList):
		'Corporation Has been removed from a City'
		iCorporation, iOwner, pRemoveCity = argsList
		player = PyPlayer(iOwner)
		if (not self.__LOG_RELIGIONSPREAD):
			return
		CvUtil.pyPrint('%s has been removed from Player %d Civilization %s city of %s'
			%(gc.getReligionInfo(iReligion).getDescription(), iOwner, player.getCivilizationName(), pRemoveCity.getName()))
				
	def onGoldenAge(self, argsList):
		'Golden Age'
		iPlayer = argsList[0]
		player = PyPlayer(iPlayer)
		if (not self.__LOG_GOLDENAGE):
			return
		CvUtil.pyPrint('Player %d Civilization %s has begun a golden age'
			%(iPlayer, player.getCivilizationName()))

	def onEndGoldenAge(self, argsList):
		'End Golden Age'
		iPlayer = argsList[0]
		player = PyPlayer(iPlayer)
		if (not self.__LOG_ENDGOLDENAGE):
			return
		CvUtil.pyPrint('Player %d Civilization %s golden age has ended'
			%(iPlayer, player.getCivilizationName()))

	def onChangeWar(self, argsList):
		'War Status Changes'
		bIsWar = argsList[0]
		iTeam = argsList[1]
		iRivalTeam = argsList[2]
		if (not self.__LOG_WARPEACE):
			return
		if (bIsWar):
			strStatus = "declared war"
		else:
			strStatus = "declared peace"
		CvUtil.pyPrint('Team %d has %s on Team %d'
			%(iTeam, strStatus, iRivalTeam))
	
	def onChat(self, argsList):
		'Chat Message Event'
		chatMessage = "%s" %(argsList[0],)
		
	def onSetPlayerAlive(self, argsList):
		'Set Player Alive Event'
		iPlayerID = argsList[0]
		bNewValue = argsList[1]
		CvUtil.pyPrint("Player %d's alive status set to: %d" %(iPlayerID, int(bNewValue)))
		
	def onPlayerChangeStateReligion(self, argsList):
		'Player changes his state religion'
		iPlayer, iNewReligion, iOldReligion = argsList
		
	def onPlayerGoldTrade(self, argsList):
		'Player Trades gold to another player'
		iFromPlayer, iToPlayer, iGoldAmount = argsList
		
	def onCityBuilt(self, argsList):
		'City Built'
		city = argsList[0]
		if (city.getOwner() == gc.getGame().getActivePlayer()):
			self.__eventEditCityNameBegin(city, False)	
		CvUtil.pyPrint('City Built Event: %s' %(city.getName()))
		
	def onCityRazed(self, argsList):
		'City Razed'
		city, iPlayer = argsList
		
		owner = PyPlayer(city.getOwner())
		razor = PyPlayer(iPlayer)
		CvUtil.pyPrint('Player %d Civilization %s City %s was razed by Player %d' 
			%(owner.getID(), owner.getCivilizationName(), city.getName(), razor.getID()))
		CvUtil.pyPrint("City Razed Event: %s" %(city.getName(),))
	
	def onCityAcquired(self, argsList):
		'City Acquired'
		iPreviousOwner,iNewOwner,pCity,bConquest,bTrade = argsList
		CvUtil.pyPrint('City Acquired Event: %s' %(pCity.getName()))
	
	def onCityAcquiredAndKept(self, argsList):
		'City Acquired and Kept'
		iOwner,pCity = argsList
		CvUtil.pyPrint('City Acquired and Kept Event: %s' %(pCity.getName()))
	
	def onCityLost(self, argsList):
		'City Lost'
		city = argsList[0]
		player = PyPlayer(city.getOwner())
		if (not self.__LOG_CITYLOST):
			return
		CvUtil.pyPrint('City %s was lost by Player %d Civilization %s' 
			%(city.getName(), player.getID(), player.getCivilizationName()))
	
	def onCultureExpansion(self, argsList):
		'City Culture Expansion'
		pCity = argsList[0]
		iPlayer = argsList[1]
		CvUtil.pyPrint("City %s's culture has expanded" %(pCity.getName(),))
	
	def onCityGrowth(self, argsList):
		'City Population Growth'
		pCity = argsList[0]
		iPlayer = argsList[1]
		CvUtil.pyPrint("%s has grown" %(pCity.getName(),))
	
	def onCityDoTurn(self, argsList):
		'City Production'
		pCity = argsList[0]
		iPlayer = argsList[1]

		CvAdvisorUtils.cityAdvise(pCity, iPlayer)
	
	def onCityBuildingUnit(self, argsList):
		'City begins building a unit'
		pCity = argsList[0]
		iUnitType = argsList[1]
		if (not self.__LOG_CITYBUILDING):
			return
		CvUtil.pyPrint("%s has begun building a %s" %(pCity.getName(),gc.getUnitInfo(iUnitType).getDescription()))
	
	def onCityBuildingBuilding(self, argsList):
		'City begins building a Building'
		pCity = argsList[0]
		iBuildingType = argsList[1]
		if (not self.__LOG_CITYBUILDING):
			return
		CvUtil.pyPrint("%s has begun building a %s" %(pCity.getName(),gc.getBuildingInfo(iBuildingType).getDescription()))
	
	def onCityRename(self, argsList):
		'City is renamed'
		pCity = argsList[0]
		if (pCity.getOwner() == gc.getGame().getActivePlayer()):
			self.__eventEditCityNameBegin(pCity, True)	
	
	def onCityHurry(self, argsList):
		'City is renamed'
		pCity = argsList[0]
		iHurryType = argsList[1]

	def onVictory(self, argsList):
		'Victory'
		iTeam, iVictory = argsList
		if (iVictory >= 0 and iVictory < gc.getNumVictoryInfos()):
			victoryInfo = gc.getVictoryInfo(int(iVictory))
			CvUtil.pyPrint("Victory!  Team %d achieves a %s victory"
				%(iTeam, victoryInfo.getDescription()))
	
	def onVassalState(self, argsList):
		'Vassal State'
		iMaster, iVassal, bVassal = argsList
		
		if (bVassal):
			CvUtil.pyPrint("Team %d becomes a Vassal State of Team %d"
				%(iVassal, iMaster))
		else:
			CvUtil.pyPrint("Team %d revolts and is no longer a Vassal State of Team %d"
				%(iVassal, iMaster))
	
	def onGameUpdate(self, argsList):
		'sample generic event, called on each game turn slice'
		genericArgs = argsList[0][0]	# tuple of tuple of my args
		turnSlice = genericArgs[0]
		
		if self.iKillTimer > 0:
			self.iKillTimer += - 1
		else:
			self.doCompleteKillUnit()
	
	def onMouseEvent(self, argsList):
		'mouse handler - returns 1 if the event was consumed'
		eventType,mx,my,px,py,interfaceConsumed,screens = argsList
		if ( px!=-1 and py!=-1 ):
			
			if eventType == self.EventLcButtonDblClick:
				if CyMap().plot(px,py).isCity():
					return true
			
			if ( eventType == self.EventLButtonDown ):
				if (self.bAllowCheats and self.bCtrl and self.bAlt and CyMap().plot(px,py).isCity() and not interfaceConsumed):
					# Launch Edit City Event
					self.beginEvent( CvUtil.EventEditCity, (px,py) )
					return 1
				
				elif (self.bAllowCheats and self.bCtrl and self.bShift and not interfaceConsumed):
					# Launch Place Object Event
					self.beginEvent( CvUtil.EventPlaceObject, (px, py) )
					return 1
			
		if ( eventType == self.EventBack ):
			return CvScreensInterface.handleBack(screens)
		elif ( eventType == self.EventForward ):
			return CvScreensInterface.handleForward(screens)
		
		return 0
		

#################### TRIGGERED EVENTS ##################	
	
	def __eventEditCityNameBegin(self, city, bRename):
		popup = PyPopup.PyPopup(CvUtil.EventEditCityName, EventContextTypes.EVENTCONTEXT_ALL)
		popup.setUserData((city.getID(), bRename))
		popup.setHeaderString(localText.getText("TXT_KEY_NAME_CITY", ()))
		popup.setBodyString(localText.getText("TXT_KEY_SETTLE_NEW_CITY_NAME", ()))
		popup.createEditBox(city.getName())
		popup.setEditBoxMaxCharCount( 15 )
		popup.launch()
	
	def __eventEditCityNameApply(self, playerID, userData, popupReturn):	
		'Edit City Name Event'
		iCityID = userData[0]
		bRename = userData[1]
		player = gc.getPlayer(playerID)
		city = player.getCity(iCityID)
		cityName = popupReturn.getEditBoxString(0)
		if (len(cityName) > 30):
			cityName = cityName[:30]
		city.setName(cityName, not bRename)

	def __eventEditCityBegin(self, argsList):
		'Edit City Event'
		px,py = argsList
		CvWBPopups.CvWBPopups().initEditCity(argsList)
	
	def __eventEditCityApply(self, playerID, userData, popupReturn):
		'Edit City Event Apply'
		if (getChtLvl() > 0):
			CvWBPopups.CvWBPopups().applyEditCity( (popupReturn, userData) )

	def __eventPlaceObjectBegin(self, argsList):
		'Place Object Event'
		CvDebugTools.CvDebugTools().initUnitPicker(argsList)
	
	def __eventPlaceObjectApply(self, playerID, userData, popupReturn):
		'Place Object Event Apply'
		if (getChtLvl() > 0):
			CvDebugTools.CvDebugTools().applyUnitPicker( (popupReturn, userData) )

	def __eventAwardTechsAndGoldBegin(self, argsList):
		'Award Techs & Gold Event'
		CvDebugTools.CvDebugTools().cheatTechs()
	
	def __eventAwardTechsAndGoldApply(self, playerID, netUserData, popupReturn):
		'Award Techs & Gold Event Apply'
		if (getChtLvl() > 0):
			CvDebugTools.CvDebugTools().applyTechCheat( (popupReturn) )
	
	def __eventShowWonderBegin(self, argsList):
		'Show Wonder Event'
		CvDebugTools.CvDebugTools().wonderMovie()
	
	def __eventShowWonderApply(self, playerID, netUserData, popupReturn):
		'Wonder Movie Apply'
		if (getChtLvl() > 0):
			CvDebugTools.CvDebugTools().applyWonderMovie( (popupReturn) )
	
	def __eventEditUnitNameBegin(self, argsList):
		pUnit = argsList
		popup = PyPopup.PyPopup(CvUtil.EventEditUnitName, EventContextTypes.EVENTCONTEXT_ALL)
		popup.setUserData((pUnit.getID(),))
		popup.setBodyString(localText.getText("TXT_KEY_RENAME_UNIT", ()))
		popup.createEditBox(pUnit.getNameNoDesc())
		popup.launch()

	def __eventEditUnitNameApply(self, playerID, userData, popupReturn):	
		'Edit Unit Name Event'
		iUnitID = userData[0]
		unit = gc.getPlayer(playerID).getUnit(iUnitID)
		newName = popupReturn.getEditBoxString(0)
		if (len(newName) > 25):
			newName = newName[:25]			
		unit.setName(newName)

	def __eventWBAllPlotsPopupBegin(self, argsList):
		CvScreensInterface.getWorldBuilderScreen().allPlotsCB()
		return
	def __eventWBAllPlotsPopupApply(self, playerID, userData, popupReturn):
		if (popupReturn.getButtonClicked() >= 0):
			CvScreensInterface.getWorldBuilderScreen().handleAllPlotsCB(popupReturn)
		return

	def __eventWBLandmarkPopupBegin(self, argsList):
		CvScreensInterface.getWorldBuilderScreen().setLandmarkCB("")
		#popup = PyPopup.PyPopup(CvUtil.EventWBLandmarkPopup, EventContextTypes.EVENTCONTEXT_ALL)
		#popup.createEditBox(localText.getText("TXT_KEY_WB_LANDMARK_START", ()))
		#popup.launch()
		return

	def __eventWBLandmarkPopupApply(self, playerID, userData, popupReturn):
		if (popupReturn.getEditBoxString(0)):
			szLandmark = popupReturn.getEditBoxString(0)
			if (len(szLandmark)):
				CvScreensInterface.getWorldBuilderScreen().setLandmarkCB(szLandmark)
		return

	def __eventWBScriptPopupBegin(self, argsList):
		popup = PyPopup.PyPopup(CvUtil.EventWBScriptPopup, EventContextTypes.EVENTCONTEXT_ALL)
		popup.setHeaderString(localText.getText("TXT_KEY_WB_SCRIPT", ()))
		popup.createEditBox(CvScreensInterface.getWorldBuilderScreen().getCurrentScript())
		popup.launch()
		return

	def __eventWBScriptPopupApply(self, playerID, userData, popupReturn):
		if (popupReturn.getEditBoxString(0)):
			szScriptName = popupReturn.getEditBoxString(0)
			CvScreensInterface.getWorldBuilderScreen().setScriptCB(szScriptName)
		return

	def __eventWBStartYearPopupBegin(self, argsList):
		popup = PyPopup.PyPopup(CvUtil.EventWBStartYearPopup, EventContextTypes.EVENTCONTEXT_ALL)
		popup.createSpinBox(0, "", gc.getGame().getStartYear(), 1, 5000, -5000)
		popup.launch()
		return

	def __eventWBStartYearPopupApply(self, playerID, userData, popupReturn):
		iStartYear = popupReturn.getSpinnerWidgetValue(int(0))
		CvScreensInterface.getWorldBuilderScreen().setStartYearCB(iStartYear)
		return

################## DEFENSE FUNCTIONS ##################

	def clearDefenseVariables( self ):
		
		self.iGameLevel = 1
		self.iSpawnGameTurn = 5
		self.iTotalMobs = 10
		self.iMobsKilled = 0
		self.iKillTimer =  0		
		self.pKillUnit = 0
		
		#CvMainInterface Variables
		self.bIsInAdvancedStart = -1
		self.bTurnTimerOff = 1
		self.iTurnTimerTrigger = 1
		self.iTurnTimer = 0
		self.bPlotReveal = 0
		
		self.bHasSetGold = 0
		self.iCurrentAdvancedStartPoints = -1
		
		self.szRoundOverlay = "TXT_KEY_DEFENSE_ROUND_ONE"
		self.szRoundTitleOverlay = "TXT_KEY_DEFENSE_ROUND_ONE_TITLE"
		

	def doLevelChange( self, iGameTurn ):
		self.iGameLevel += 1
		self.iMobsKilled = 0
		self.doHutRepopulation( )
		
		if self.iGameLevel == 21:
			self.doCongratulationMessage()
		else:
			self.doCongratulationMessage()
			self.doSetLevelVaribles( iGameTurn )
			self.doBeginBuildPhase()
	
	def doBeginBuildPhase( self ):
		iPoints = 0 + gc.getPlayer( 0 ).getGold( ) + ( gc.getPlayer( 0 ).getNumCities( ) * 200 )
				
		gc.getPlayer( 0 ).setAdvancedStartPoints( iPoints )
		gc.getPlayer( 0 ).setGold( 0 )
		
		self.bHasSetGold = 0
	
	def doSetLevelVaribles( self, iGameTurn ):
		
		if self.iGameLevel == 2:
			self.iSpawnGameTurn = iGameTurn + 6
			self.iTotalMobs = 20
		if self.iGameLevel == 3:
			self.iSpawnGameTurn = iGameTurn + 6
			self.iTotalMobs = 20
		if self.iGameLevel == 4:
			self.iSpawnGameTurn = iGameTurn + 11
			self.iTotalMobs = 40
		if self.iGameLevel == 5:
			self.iSpawnGameTurn = iGameTurn + 6
			self.iTotalMobs = 20
		if self.iGameLevel == 6:
			self.iSpawnGameTurn = iGameTurn + 6
			self.iTotalMobs = 20
		if self.iGameLevel == 7:
			self.iSpawnGameTurn = iGameTurn + 6
			self.iTotalMobs = 20
		if self.iGameLevel == 8:
			self.iSpawnGameTurn = iGameTurn + 11
			self.iTotalMobs = 40
		if self.iGameLevel == 9:
			self.iSpawnGameTurn = iGameTurn + 11
			self.iTotalMobs = 80
		if self.iGameLevel == 10:
			self.iSpawnGameTurn = iGameTurn + 11
			self.iTotalMobs = 120
		if self.iGameLevel == 11:
			self.iSpawnGameTurn = iGameTurn + 11
			self.iTotalMobs = 40
		if self.iGameLevel == 12:
			self.iSpawnGameTurn = iGameTurn + 6
			self.iTotalMobs = 20
		if self.iGameLevel == 13:
			self.iSpawnGameTurn = iGameTurn + 11
			self.iTotalMobs = 140			
		if self.iGameLevel == 14:
			self.iSpawnGameTurn = iGameTurn + 11
			self.iTotalMobs = 40
		if self.iGameLevel == 15:
			self.iSpawnGameTurn = iGameTurn + 16
			self.iTotalMobs = 80
		if self.iGameLevel == 16:
			self.iSpawnGameTurn = iGameTurn + 11
			self.iTotalMobs = 40
		if self.iGameLevel == 17:
			self.iSpawnGameTurn = iGameTurn + 11
			self.iTotalMobs = 60
		if self.iGameLevel == 18:
			self.iSpawnGameTurn = iGameTurn + 2
			self.iTotalMobs = 2
		if self.iGameLevel == 19:
			self.iSpawnGameTurn = iGameTurn + 16
			self.iTotalMobs = 62
		if self.iGameLevel == 20:
			self.iSpawnGameTurn = iGameTurn + 31
			self.iTotalMobs = 288
									
	def setDefenseVariables(self):
		pPlayer = gc.getPlayer(0)
		
		szScriptData = []
		
		szScriptData.append(self.iGameLevel)
		szScriptData.append(self.iSpawnGameTurn) 
		szScriptData.append(self.iTotalMobs) 
		szScriptData.append(self.iMobsKilled) 

		# Save Script Data - Score
		pPlayer.setScriptData(pickle.dumps(szScriptData))	
		
	def getDefenseVariables(self):
		
		pPlayer = gc.getPlayer(0)
		
		# Load Script Data - Score
		szScriptData = pickle.loads(pPlayer.getScriptData())
		
		self.iGameLevel = szScriptData[0]
		self.iSpawnGameTurn = szScriptData[1]
		self.iTotalMobs = szScriptData[2]
		self.iMobsKilled = szScriptData[3]

		return 

	def spawnUnit(self, player, unit, X, Y, AIType):
		gc.getPlayer(player).initUnit(CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(), unit), X, Y, AIType, DirectionTypes.NO_DIRECTION)

	def doMonsterMachine( self, iGameTurn ):
		
		if self.iGameLevel == 1:
			if iGameTurn < self.iSpawnGameTurn:
				iRandomNumber = self.getRandomNumber(2)
				if iRandomNumber == 0:
					self.doSpawnNorthEast( "UNIT_LION" )
					self.doSpawnSouthEast( "UNIT_LION" )
				if iRandomNumber == 1:				
					self.doSpawnNorth( "UNIT_LION" )
					self.doSpawnSouth( "UNIT_LION" )
		if self.iGameLevel == 2:
			if iGameTurn < self.iSpawnGameTurn:
				self.doSpawnNorth( "UNIT_WOLF" )
				self.doSpawnNorthEast( "UNIT_WOLF" )
				self.doSpawnSouthEast( "UNIT_WOLF" )
				self.doSpawnSouth( "UNIT_WOLF" )
		if self.iGameLevel == 3:
			if iGameTurn < self.iSpawnGameTurn:
				self.doSpawnNorth( "UNIT_BEAR" )
				self.doSpawnNorthEast( "UNIT_BEAR" )
				self.doSpawnSouthEast( "UNIT_BEAR" )
				self.doSpawnSouth( "UNIT_BEAR" )
		if self.iGameLevel == 4:
			if iGameTurn < self.iSpawnGameTurn:
				iRandomNumber = self.getRandomNumber(3)
				if iRandomNumber == 0:
					self.doSpawnNorth( "UNIT_BEAR" )
					self.doSpawnNorthEast( "UNIT_BEAR" )
					self.doSpawnSouthEast( "UNIT_BEAR" )
					self.doSpawnSouth( "UNIT_BEAR" )
				if iRandomNumber == 1:
					self.doSpawnNorth( "UNIT_WOLF" )
					self.doSpawnNorthEast( "UNIT_WOLF" )
					self.doSpawnSouthEast( "UNIT_WOLF" )
					self.doSpawnSouth( "UNIT_WOLF" )
				if iRandomNumber == 2:
					self.doSpawnNorth( "UNIT_LION" )
					self.doSpawnNorthEast( "UNIT_LION" )
					self.doSpawnSouthEast( "UNIT_LION" )
					self.doSpawnSouth( "UNIT_LION" )
		if self.iGameLevel == 5:
			if iGameTurn < self.iSpawnGameTurn:
				self.doSpawnNorth( "UNIT_SAVAGE" )
				self.doSpawnNorthEast( "UNIT_SAVAGE" )
				self.doSpawnSouthEast( "UNIT_SAVAGE" )
				self.doSpawnSouth( "UNIT_SAVAGE" )
		if self.iGameLevel == 6:
			if iGameTurn < self.iSpawnGameTurn:
				self.doSpawnNorth( "UNIT_CHARGER" )
				self.doSpawnNorthEast( "UNIT_CHARGER" )
				self.doSpawnSouthEast( "UNIT_CHARGER" )
				self.doSpawnSouth( "UNIT_CHARGER" )
		if self.iGameLevel == 7:
			if iGameTurn < self.iSpawnGameTurn:
				self.doSpawnNorth( "UNIT_PANTHER" )
				self.doSpawnNorthEast( "UNIT_PANTHER" )
				self.doSpawnSouthEast( "UNIT_PANTHER" )
				self.doSpawnSouth( "UNIT_PANTHER" )
		if self.iGameLevel == 8:
			if iGameTurn < self.iSpawnGameTurn:
				iRandomNumber = self.getRandomNumber(3)
				if iRandomNumber == 0:
					self.doSpawnNorth( "UNIT_SAVAGE" )
					self.doSpawnNorthEast( "UNIT_SAVAGE" )
					self.doSpawnSouthEast( "UNIT_SAVAGE" )
					self.doSpawnSouth( "UNIT_SAVAGE" )
				if iRandomNumber == 1:
					self.doSpawnNorth( "UNIT_CHARGER" )
					self.doSpawnNorthEast( "UNIT_CHARGER" )
					self.doSpawnSouthEast( "UNIT_CHARGER" )
					self.doSpawnSouth( "UNIT_CHARGER" )
				if iRandomNumber == 2:
					self.doSpawnNorth( "UNIT_PANTHER" )
					self.doSpawnNorthEast( "UNIT_PANTHER" )
					self.doSpawnSouthEast( "UNIT_PANTHER" )
					self.doSpawnSouth( "UNIT_PANTHER" )
		if self.iGameLevel == 9:
			if iGameTurn < self.iSpawnGameTurn:
				iRandomNumber = self.getRandomNumber(3)
				if iRandomNumber == 0:
					self.doSpawnNorth( "UNIT_SAVAGE" )
					self.doSpawnNorthEast( "UNIT_ARATHNID" )
					self.doSpawnSouthEast( "UNIT_ARATHNID" )
					self.doSpawnSouth( "UNIT_SAVAGE" )
					self.doSpawnNorth( "UNIT_BEAR" )
					self.doSpawnNorthEast( "UNIT_ARATHNID" )
					self.doSpawnSouthEast( "UNIT_ARATHNID" )
					self.doSpawnSouth( "UNIT_BEAR" )
				if iRandomNumber == 1:
					self.doSpawnNorth( "UNIT_CHARGER" )
					self.doSpawnNorthEast( "UNIT_ARATHNID" )
					self.doSpawnSouthEast( "UNIT_ARATHNID" )
					self.doSpawnSouth( "UNIT_CHARGER" )
					self.doSpawnNorth( "UNIT_WOLF" )
					self.doSpawnNorthEast( "UNIT_ARATHNID" )
					self.doSpawnSouthEast( "UNIT_ARATHNID" )
					self.doSpawnSouth( "UNIT_WOLF" )
				if iRandomNumber == 2:
					self.doSpawnNorth( "UNIT_PANTHER" )
					self.doSpawnNorthEast( "UNIT_ARATHNID" )
					self.doSpawnSouthEast( "UNIT_ARATHNID" )
					self.doSpawnSouth( "UNIT_PANTHER" )
					self.doSpawnNorth( "UNIT_LION" )
					self.doSpawnNorthEast( "UNIT_ARATHNID" )
					self.doSpawnSouthEast( "UNIT_ARATHNID" )
					self.doSpawnSouth( "UNIT_LION" )
		if self.iGameLevel == 10:
			if iGameTurn < self.iSpawnGameTurn:
				self.doSpawnNorth( "UNIT_ZOMBIE" )
				self.doSpawnNorth( "UNIT_ZOMBIE" )
				self.doSpawnNorth( "UNIT_ZOMBIE" )
				self.doSpawnNorthEast( "UNIT_ZOMBIE" )
				self.doSpawnNorthEast( "UNIT_ZOMBIE" )
				self.doSpawnNorthEast( "UNIT_ZOMBIE" )
				self.doSpawnSouthEast( "UNIT_ZOMBIE" )
				self.doSpawnSouthEast( "UNIT_ZOMBIE" )
				self.doSpawnSouthEast( "UNIT_ZOMBIE" )
				self.doSpawnSouth( "UNIT_ZOMBIE" )
				self.doSpawnSouth( "UNIT_ZOMBIE" )
				self.doSpawnSouth( "UNIT_ZOMBIE" )
		if self.iGameLevel == 11:
			if iGameTurn < self.iSpawnGameTurn:
				self.doSpawnNorth( "UNIT_SAMURAI" )
				self.doSpawnNorthEast( "UNIT_SAMURAI" )
				self.doSpawnSouthEast( "UNIT_SAMURAI" )
				self.doSpawnSouth( "UNIT_SAMURAI" )
		if self.iGameLevel == 12:
			if iGameTurn < self.iSpawnGameTurn:
				self.doSpawnNorth( "UNIT_GRENADIER" )
				self.doSpawnNorthEast( "UNIT_GRENADIER" )
				self.doSpawnSouthEast( "UNIT_GRENADIER" )
				self.doSpawnSouth( "UNIT_GRENADIER" )
		if self.iGameLevel == 13:
			if iGameTurn < self.iSpawnGameTurn:
				self.doSpawnNorth( "UNIT_ZOMBIE" )
				self.doSpawnNorth( "UNIT_ZOMBIE" )
				self.doSpawnNorth( "UNIT_ZOMBIE" )
				self.doSpawnNorthEast( "UNIT_ZOMBIE" )
				self.doSpawnNorthEast( "UNIT_ZOMBIE" )
				self.doSpawnNorthEast( "UNIT_ZOMBIE" )
				self.doSpawnSouthEast( "UNIT_ZOMBIE" )
				self.doSpawnSouthEast( "UNIT_ZOMBIE" )
				self.doSpawnSouthEast( "UNIT_ZOMBIE" )
				self.doSpawnSouth( "UNIT_ZOMBIE" )
				self.doSpawnSouth( "UNIT_ZOMBIE" )
				self.doSpawnSouth( "UNIT_ZOMBIE" )
			if iGameTurn == self.iSpawnGameTurn - 2:
				self.doSpawnNorth( "UNIT_GRENADIER" )
				self.doSpawnNorthEast( "UNIT_GRENADIER" )
				self.doSpawnSouthEast( "UNIT_GRENADIER" )
				self.doSpawnSouth( "UNIT_GRENADIER" )
			if iGameTurn == self.iSpawnGameTurn - 4:
				self.doSpawnNorth( "UNIT_GRENADIER" )
				self.doSpawnNorthEast( "UNIT_GRENADIER" )
				self.doSpawnSouthEast( "UNIT_GRENADIER" )
				self.doSpawnSouth( "UNIT_GRENADIER" )
			if iGameTurn == self.iSpawnGameTurn - 6:
				self.doSpawnNorth( "UNIT_GRENADIER" )
				self.doSpawnNorthEast( "UNIT_GRENADIER" )
				self.doSpawnSouthEast( "UNIT_GRENADIER" )
				self.doSpawnSouth( "UNIT_GRENADIER" )
			if iGameTurn == self.iSpawnGameTurn - 8:
				self.doSpawnNorth( "UNIT_GRENADIER" )
				self.doSpawnNorthEast( "UNIT_GRENADIER" )
				self.doSpawnSouthEast( "UNIT_GRENADIER" )
				self.doSpawnSouth( "UNIT_GRENADIER" )
			if iGameTurn == self.iSpawnGameTurn - 10:
				self.doSpawnNorth( "UNIT_GRENADIER" )
				self.doSpawnNorthEast( "UNIT_GRENADIER" )
				self.doSpawnSouthEast( "UNIT_GRENADIER" )
				self.doSpawnSouth( "UNIT_GRENADIER" )
		if self.iGameLevel == 14:
			if iGameTurn < self.iSpawnGameTurn:
				self.doSpawnNorth( "UNIT_ELEPHANT_RIDER" )
				self.doSpawnNorthEast( "UNIT_ELEPHANT_RIDER" )
				self.doSpawnSouthEast( "UNIT_ELEPHANT_RIDER" )
				self.doSpawnSouth( "UNIT_ELEPHANT_RIDER" )
		if self.iGameLevel == 15:
			if iGameTurn < self.iSpawnGameTurn:
				self.doSpawnNorth( "UNIT_SAMURAI" )
				self.doSpawnNorthEast( "UNIT_SAMURAI" )
				self.doSpawnSouthEast( "UNIT_SAMURAI" )
				self.doSpawnSouth( "UNIT_SAMURAI" )
				iRandomNumber = self.getRandomNumber(4)
				if iRandomNumber == 0:
					self.doSpawnNorth( "UNIT_GRENADIER" )
				if iRandomNumber == 1:
					self.doSpawnNorthEast( "UNIT_GRENADIER" )
				if iRandomNumber == 2:
					self.doSpawnSouthEast( "UNIT_GRENADIER" )
				if iRandomNumber == 3:
					self.doSpawnSouth( "UNIT_GRENADIER" )
			if iGameTurn < self.iSpawnGameTurn and iGameTurn >= self.iSpawnGameTurn -10:			
				self.doSpawnNorth( "UNIT_ELEPHANT_RIDER" )
				self.doSpawnNorthEast( "UNIT_ELEPHANT_RIDER" )
				self.doSpawnSouthEast( "UNIT_ELEPHANT_RIDER" )
				self.doSpawnSouth( "UNIT_ELEPHANT_RIDER" )
		if self.iGameLevel == 16:
			if iGameTurn < self.iSpawnGameTurn:
				self.doSpawnNorth( "UNIT_DOOM_ROLLER" )
				self.doSpawnNorthEast( "UNIT_DOOM_ROLLER" )
				self.doSpawnSouthEast( "UNIT_DOOM_ROLLER" )
				self.doSpawnSouth( "UNIT_DOOM_ROLLER" )
		if self.iGameLevel == 17:
			if iGameTurn < self.iSpawnGameTurn:
				self.doSpawnNorth( "UNIT_DOOM_ROLLER" )
				self.doSpawnNorthEast( "UNIT_DOOM_ROLLER" )
				self.doSpawnSouthEast( "UNIT_DOOM_ROLLER" )
				self.doSpawnSouth( "UNIT_DOOM_ROLLER" )
			if iGameTurn == self.iSpawnGameTurn - 2:
				self.doSpawnNorth( "UNIT_DEATH_TRACK" )
				self.doSpawnNorthEast( "UNIT_DEATH_TRACK" )
				self.doSpawnSouthEast( "UNIT_DEATH_TRACK" )
				self.doSpawnSouth( "UNIT_DEATH_TRACK" )
			if iGameTurn == self.iSpawnGameTurn - 4:
				self.doSpawnNorth( "UNIT_DEATH_TRACK" )
				self.doSpawnNorthEast( "UNIT_DEATH_TRACK" )
				self.doSpawnSouthEast( "UNIT_DEATH_TRACK" )
				self.doSpawnSouth( "UNIT_DEATH_TRACK" )
			if iGameTurn == self.iSpawnGameTurn - 6:
				self.doSpawnNorth( "UNIT_DEATH_TRACK" )
				self.doSpawnNorthEast( "UNIT_DEATH_TRACK" )
				self.doSpawnSouthEast( "UNIT_DEATH_TRACK" )
				self.doSpawnSouth( "UNIT_DEATH_TRACK" )
			if iGameTurn == self.iSpawnGameTurn - 8:
				self.doSpawnNorth( "UNIT_DEATH_TRACK" )
				self.doSpawnNorthEast( "UNIT_DEATH_TRACK" )
				self.doSpawnSouthEast( "UNIT_DEATH_TRACK" )
				self.doSpawnSouth( "UNIT_DEATH_TRACK" )
			if iGameTurn == self.iSpawnGameTurn - 10:
				self.doSpawnNorth( "UNIT_DEATH_TRACK" )
				self.doSpawnNorthEast( "UNIT_DEATH_TRACK" )
				self.doSpawnSouthEast( "UNIT_DEATH_TRACK" )
				self.doSpawnSouth( "UNIT_DEATH_TRACK" )
		if self.iGameLevel == 18:
			if iGameTurn < self.iSpawnGameTurn:
				self.doSpawnNorthEast( "UNIT_MONSTER_TANK" )
				self.doSpawnSouthEast( "UNIT_MONSTER_TANK" )
		if self.iGameLevel == 19:
			if iGameTurn < self.iSpawnGameTurn -10:
				self.doSpawnNorth( "UNIT_DOOM_ROLLER" )
				self.doSpawnNorthEast( "UNIT_DOOM_ROLLER" )
				self.doSpawnSouthEast( "UNIT_DOOM_ROLLER" )
				self.doSpawnSouth( "UNIT_DOOM_ROLLER" )
			if iGameTurn < self.iSpawnGameTurn and iGameTurn >= self.iSpawnGameTurn -10:		
				self.doSpawnNorth( "UNIT_DEATH_TRACK" )
				self.doSpawnNorthEast( "UNIT_DEATH_TRACK" )
				self.doSpawnSouthEast( "UNIT_DEATH_TRACK" )
				self.doSpawnSouth( "UNIT_DEATH_TRACK" )
			if iGameTurn < self.iSpawnGameTurn and iGameTurn >= self.iSpawnGameTurn -15:		
				self.doSpawnNorthEast( "UNIT_MONSTER_TANK" )
				self.doSpawnSouthEast( "UNIT_MONSTER_TANK" )
		if self.iGameLevel == 20:
			if iGameTurn < self.iSpawnGameTurn -30:
				self.doSpawnNorthEast( "UNIT_MONSTER_TANK" )
				self.doSpawnSouthEast( "UNIT_MONSTER_TANK" )
			if iGameTurn < self.iSpawnGameTurn -25:			
				self.doSpawnNorth( "UNIT_BEAR" )
				self.doSpawnNorthEast( "UNIT_BEAR" )
				self.doSpawnSouthEast( "UNIT_BEAR" )
				self.doSpawnSouth( "UNIT_BEAR" )
				self.doSpawnNorth( "UNIT_WOLF" )
				self.doSpawnNorthEast( "UNIT_WOLF" )
				self.doSpawnSouthEast( "UNIT_WOLF" )
				self.doSpawnSouth( "UNIT_WOLF" )
				self.doSpawnNorth( "UNIT_LION" )
				self.doSpawnNorthEast( "UNIT_LION" )
				self.doSpawnSouthEast( "UNIT_LION" )
				self.doSpawnSouth( "UNIT_LION" )
			if iGameTurn < self.iSpawnGameTurn - 20 and iGameTurn >= self.iSpawnGameTurn -25:
				self.doSpawnNorth( "UNIT_SAVAGE" )
				self.doSpawnNorthEast( "UNIT_SAVAGE" )
				self.doSpawnSouthEast( "UNIT_SAVAGE" )
				self.doSpawnSouth( "UNIT_SAVAGE" )
				self.doSpawnNorth( "UNIT_CHARGER" )
				self.doSpawnNorthEast( "UNIT_CHARGER" )
				self.doSpawnSouthEast( "UNIT_CHARGER" )
				self.doSpawnSouth( "UNIT_CHARGER" )
				self.doSpawnNorth( "UNIT_PANTHER" )
				self.doSpawnNorthEast( "UNIT_PANTHER" )
				self.doSpawnSouthEast( "UNIT_PANTHER" )
				self.doSpawnSouth( "UNIT_PANTHER" )
			if iGameTurn == self.iSpawnGameTurn - 20:
				self.doSpawnNorthEast( "UNIT_MONSTER_TANK" )
				self.doSpawnSouthEast( "UNIT_MONSTER_TANK" )
			if iGameTurn < self.iSpawnGameTurn - 15 and iGameTurn >= self.iSpawnGameTurn -20:
				self.doSpawnNorth( "UNIT_ZOMBIE" )
				self.doSpawnNorth( "UNIT_ZOMBIE" )
				self.doSpawnNorth( "UNIT_ZOMBIE" )
				self.doSpawnNorthEast( "UNIT_ZOMBIE" )
				self.doSpawnNorthEast( "UNIT_ZOMBIE" )
				self.doSpawnNorthEast( "UNIT_ZOMBIE" )
				self.doSpawnSouthEast( "UNIT_ZOMBIE" )
				self.doSpawnSouthEast( "UNIT_ZOMBIE" )
				self.doSpawnSouthEast( "UNIT_ZOMBIE" )
				self.doSpawnSouth( "UNIT_ZOMBIE" )
				self.doSpawnSouth( "UNIT_ZOMBIE" )
				self.doSpawnSouth( "UNIT_ZOMBIE" )
				self.doSpawnNorth( "UNIT_GRENADIER" )
				self.doSpawnNorthEast( "UNIT_GRENADIER" )
				self.doSpawnSouthEast( "UNIT_GRENADIER" )
				self.doSpawnSouth( "UNIT_GRENADIER" )
			if iGameTurn < self.iSpawnGameTurn - 10 and iGameTurn >= self.iSpawnGameTurn -15:				
				self.doSpawnNorth( "UNIT_ELEPHANT_RIDER" )
				self.doSpawnNorthEast( "UNIT_ELEPHANT_RIDER" )
				self.doSpawnSouthEast( "UNIT_ELEPHANT_RIDER" )
				self.doSpawnSouth( "UNIT_ELEPHANT_RIDER" )
				self.doSpawnNorth( "UNIT_SAMURAI" )
				self.doSpawnNorthEast( "UNIT_SAMURAI" )
				self.doSpawnSouthEast( "UNIT_SAMURAI" )
				self.doSpawnSouth( "UNIT_SAMURAI" )
			if iGameTurn == self.iSpawnGameTurn - 10:
				self.doSpawnNorthEast( "UNIT_MONSTER_TANK" )
				self.doSpawnSouthEast( "UNIT_MONSTER_TANK" )		
			if iGameTurn < self.iSpawnGameTurn - 5 and iGameTurn >= self.iSpawnGameTurn -10:
				self.doSpawnNorth( "UNIT_DOOM_ROLLER" )
				self.doSpawnNorthEast( "UNIT_DOOM_ROLLER" )
				self.doSpawnSouthEast( "UNIT_DOOM_ROLLER" )
				self.doSpawnSouth( "UNIT_DOOM_ROLLER" )				
			if iGameTurn < self.iSpawnGameTurn and iGameTurn >= self.iSpawnGameTurn - 5:
				self.doSpawnNorth( "UNIT_DEATH_TRACK" )
				self.doSpawnNorthEast( "UNIT_DEATH_TRACK" )
				self.doSpawnSouthEast( "UNIT_DEATH_TRACK" )
				self.doSpawnSouth( "UNIT_DEATH_TRACK" )
			if iGameTurn == self.iSpawnGameTurn:			
				self.doSpawnNorthEast( "UNIT_MONSTER_TANK" )
				self.doSpawnSouthEast( "UNIT_MONSTER_TANK" )				
											
	def doSpawnNorth( self, strName ):
		if self.getRandomNumber(5) == 0:
			self.spawnUnit( 1, strName, (23 + self.getRandomNumber(5)) , 0, UnitAITypes.UNITAI_ATTACK_CITY_LEMMING)
		else:	
			self.spawnUnit( 1, strName, (23 + self.getRandomNumber(5)) , 0, UnitAITypes.UNITAI_ATTACK_CITY_LEMMING)
				
	def doSpawnNorthEast( self, strName ):
		if self.getRandomNumber(5) == 0:
			self.spawnUnit( 1, strName, (23 + self.getRandomNumber(5)) , 19, UnitAITypes.UNITAI_ATTACK_CITY_LEMMING)	
		else:
			self.spawnUnit( 1, strName, (23 + self.getRandomNumber(5)) , 19, UnitAITypes.UNITAI_ATTACK_CITY_LEMMING)	


	def doSpawnSouthEast( self, strName ):
		if self.getRandomNumber(5) == 0:
			self.spawnUnit( 1, strName, 31, (12 + self.getRandomNumber(6)), UnitAITypes.UNITAI_ATTACK_CITY_LEMMING)
		else:
			self.spawnUnit( 1, strName, 31, (12 + self.getRandomNumber(6)), UnitAITypes.UNITAI_ATTACK_CITY_LEMMING)


	def doSpawnSouth( self, strName ):
		if self.getRandomNumber(5) == 0:
			self.spawnUnit( 1, strName, 31, (2 + self.getRandomNumber(5)), UnitAITypes.UNITAI_ATTACK_CITY_LEMMING)
		else:
			self.spawnUnit( 1, strName, 31, (2 + self.getRandomNumber(5)), UnitAITypes.UNITAI_ATTACK_CITY_LEMMING)


	def getRandomNumber(self, int):
		return CyGame().getSorenRandNum(int, "Defense")

	def doCongratulationMessage( self ):
		if self.iGameLevel < 21:
			iNumCities = gc.getPlayer( 0 ).getNumCities( )
			iGoldReceived = iNumCities * 200
			szString = localText.getText("TXT_KEY_DEFENSE_LEVEL_COMPLETED_CHANGED", (iNumCities, iGoldReceived, ))
			self.addPopup( localText.getText("TXT_KEY_DEFENSE_LEVEL_CONGRATULATIONS", ()), szString )
		if self.iGameLevel == 21:
			gc.getGame().setWinner( 0, CvUtil.findInfoTypeNum(gc.getHandicapInfo,gc.getNumHandicapInfos(),"VICTORY_DOMINATION"))			
		
	def addPopup(self, szTitle, szText):
		
		# Don't display popups for autoplay games
		if (gc.getPlayer(CyGame().getActivePlayer()).isAlive()):
			
			popup = PyPopup.PyPopup(-1)
			popup.setHeaderString(szTitle)
			popup.setBodyString(szText)
			popup.launch(true, PopupStates.POPUPSTATE_QUEUED)

	def doKillUnit( self, pUnit ):
		
		self.iKillTimer =  6
		self.pKillUnit = pUnit
	
	def doCompleteKillUnit( self ):
		if self.pKillUnit:
			pUnit = self.pKillUnit
			pUnit.kill( 1, PlayerTypes.NO_PLAYER )
			self.pKillUnit = 0
			
	def doHutRepopulation( self ):
		self.doClearAllHuts( )
		self.doSpawnHuts( 5 )
		
	def doSpawnHuts( self, numHuts ):
		totalNumPlots = gc.getMap( ).numPlots( )
		plot = None
						
		while numHuts > 0:
			plot = gc.getMap( ).plotByIndex( self.getRandomNumber( totalNumPlots ) )
			if plot.getX( ) > 10:
				if not plot.isGoody():
					if not plot.isOwned():
						if not plot.isUnit():
							if not plot.isPeak():
								if not plot.isWater():
									plot.setImprovementType( CvUtil.findInfoTypeNum( gc.getImprovementInfo, gc.getNumImprovementInfos( ), "IMPROVEMENT_GOODY_HUT" ) )
									numHuts += -1
		
	def doClearAllHuts( self ):
		
		for i in range( gc.getMap( ).numPlots( ) ):
			if gc.getMap( ).plotByIndex( i ).isGoody( ):
				gc.getMap( ).plotByIndex( i ).setImprovementType( -1 )
				