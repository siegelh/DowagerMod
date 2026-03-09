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

# RtW Stuff
import CvRtWEventManager
rtw = CvRtWEventManager.CvRtWEventManager()
import CvRtWGlobal
rtwglobal = CvRtWGlobal.CvRtWGlobal()

gc = CyGlobalContext()
localText = CyTranslator()
PyPlayer = PyHelpers.PyPlayer
PyInfo = PyHelpers.PyInfo


# globals
###################################################
class CvEventManager:
	def __init__(self):
		#################### ON EVENT MAP ######################
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
		self.__LOG_UNITKILLED = 1
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
# RtW Stuff
			CvUtil.EventJan2_1936Popup : ('Jan2_1936Popup', self.Jan2_1936Apply, self.Jan2_1936Begin),
##### Dale - Customiser START
                        CvUtil.EventDCMPopup : ('DCMPopup', self.DCMApply, self.DCMBegin),
                        CvUtil.EventLHPopup : ('LHPopup', self.LHApply, self.LHBegin),
                        CvUtil.EventTraitPopup : ('TraitPopup', self.TraitApply, self.TraitBegin),
                        CvUtil.EventTechPopup : ('TechPopup', self.TechApply, self.TechBegin),
                        CvUtil.EventUBPopup : ('UBPopup', self.UBApply, self.UBBegin),
                        CvUtil.EventUUPopup : ('UUPopup', self.UUApply, self.UUBegin),
##### Dale - Customiser END
##### Dale - Chooser START
                        CvUtil.EventChangeCiv_Popup : ('ChangeCiv_Popup', self.ChangeCivApply, self.ChangeCivBegin),
##### Dale - Chooser END
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
##### RtW Stuff			CyInterface().addImmediateMessage(message,"")
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
						
##### RtW Stuff
                	if( theKey == int(InputTypes.KB_X) and self.bShift and self.bCtrl ) :
                        # Get it?  Shift ... control ... to the AI
                                TurnsToAuto = 5
                                rtw.setAIAutoPlay(TurnsToAuto )
                        if( theKey == int(InputTypes.KB_C) and self.bShift and self.bCtrl ) :
                                TurnsToAuto = 50
                                rtw.setAIAutoPlay(TurnsToAuto )
                        if( theKey == int(InputTypes.KB_V) and self.bShift and self.bCtrl ) :
                                TurnsToAuto = 100
                                rtw.setAIAutoPlay(TurnsToAuto )
                        if( theKey == int(InputTypes.KB_B) and self.bShift and self.bCtrl ) :
                                TurnsToAuto = 200
                                rtw.setAIAutoPlay(TurnsToAuto )
                        if( theKey == int(InputTypes.KB_N) and self.bShift and self.bCtrl ) :
                                TurnsToAuto = 300
                                rtw.setAIAutoPlay(TurnsToAuto )
                        if( theKey == int(InputTypes.KB_M) and self.bShift and self.bCtrl ) :
                                TurnsToAuto = 350
                                rtw.setAIAutoPlay(TurnsToAuto )
                        if( theKey == int(InputTypes.KB_Z) and self.bShift and self.bCtrl ) :
                                if (gc.getDCM_CIV_CHANGER()):
                                        self.ChangeCiv_Popup()
##### RtW Stuff

			if (self.bAllowCheats):
				# Shift - T (Debug - No MP)
				if (theKey == int(InputTypes.KB_T)):
					if ( self.bShift ):
						self.beginEvent(CvUtil.EventAwardTechsAndGold)
						#self.beginEvent(CvUtil.EventCameraControlPopup)
						return 1
							
				elif (theKey == int(InputTypes.KB_W)):
					if ( self.bShift and self.bCtrl):
						self.beginEvent(CvUtil.EventShowWonder)
						return 1
							
				# Shift - ] (Debug - currently mouse-overd unit, health += 10
				elif (theKey == int(InputTypes.KB_LBRACKET) and self.bShift ):
					unit = CyMap().plot(px, py).getUnit(0)
					if ( not unit.isNone() ):
						d = min( unit.maxHitPoints()-1, unit.getDamage() + 10 )
						unit.setDamage( d, PlayerTypes.NO_PLAYER )
					
				# Shift - [ (Debug - currently mouse-overd unit, health -= 10
				elif (theKey == int(InputTypes.KB_RBRACKET) and self.bShift ):
					unit = CyMap().plot(px, py).getUnit(0)
					if ( not unit.isNone() ):
						d = max( 0, unit.getDamage() - 10 )
						unit.setDamage( d, PlayerTypes.NO_PLAYER )
					
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
	
	def onSaveGame(self, argsList):
		"return the string to be saved - Must be a string"
		return ""

	def onLoadGame(self, argsList):
		CvAdvisorUtils.resetNoLiberateCities()
##### RtW Stuff
                rtw.initValues()
		return 0

	def onGameStart(self, argsList):
##### DCM Status Popup START
                for iPlayer in range(gc.getMAX_PLAYERS()):
                        player = gc.getPlayer(iPlayer)
                        if (player.isAlive() and player.isHuman()):
                                self.DisplayDCMStatus()
##### DCM Status Popup END
##### RtW Stuff
		rtw.setupGame()
		# display intro text
		if (not gc.getGame().isPbem()):
                    rtw.Jan1_1936()
		# Setup Global Players and Cities
		if (rtw.getMap() == 3):
                    rtwglobal.globalInit()
                    rtwglobal.globalSetup()
                    rtw.resetTrueWarPeace()
                if (rtw.getMap() == 99):
                    CyGame().setRandomMapWinter()
                # Intro movie
		if (not gc.getGame().isPbem()):
                    popupInfo = CyPopupInfo()
                    popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON_SCREEN)
                    popupInfo.setData1(0)
                    popupInfo.setData2(0)
                    popupInfo.setData3(3)
                    popupInfo.setText(u"showWonderMovie")
                    for i in range(gc.getMAX_CIV_PLAYERS()):
        		if (gc.getPlayer(i).isAlive()):
                                if(gc.getPlayer(i).isHuman()):
                                        popupInfo.addPopup(i)
		# display DoM message
		for iPlayer in range(gc.getMAX_PLAYERS()):
			player = gc.getPlayer(iPlayer)
			if (player.isAlive() and player.isHuman()):
				popupInfo = CyPopupInfo()
				popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON_SCREEN)
				popupInfo.setText(u"showDawnOfMan")
				popupInfo.addPopup(iPlayer)
		if (gc.getGame().isPbem()):
                        count = 0
			for iPlayer in range(gc.getMAX_PLAYERS()):
				player = gc.getPlayer(iPlayer)
				if (player.isAlive() and player.isHuman()):
					popupInfo = CyPopupInfo()
					popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_DETAILS)
					popupInfo.setOption1(true)
					popupInfo.addPopup(iPlayer)
				if (player.isAlive() and player.isHuman() and rtw.HistEvents > 2 and count == 0):
                                        count = 1
                                        rtw.Jan2_1936()
##### RtW Stuff
		CvAdvisorUtils.resetNoLiberateCities()
																	
	def onGameEnd(self, argsList):
		'Called at the End of the game'
		print("Game is ending")
		return

	def onBeginGameTurn(self, argsList):
		'Called at the beginning of the end of each turn'
		iGameTurn = argsList[0]
		CvTopCivs.CvTopCivs().turnChecker(iGameTurn)
##### RtW Stuff
		rtw.turnChecker(iGameTurn)

	def onEndGameTurn(self, argsList):
		'Called at the end of the end of each turn'
		iGameTurn = argsList[0]
		
	def onBeginPlayerTurn(self, argsList):
		'Called at the beginning of a players turn'
		iGameTurn, iPlayer = argsList

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
		
		if cdDefender.eOwner == cdDefender.eVisualOwner:
			szDefenderName = gc.getPlayer(cdDefender.eOwner).getNameKey()
		else:
			szDefenderName = localText.getText("TXT_KEY_TRAIT_PLAYER_UNKNOWN", ())
		if cdAttacker.eOwner == cdAttacker.eVisualOwner:
			szAttackerName = gc.getPlayer(cdAttacker.eOwner).getNameKey()
		else:
			szAttackerName = localText.getText("TXT_KEY_TRAIT_PLAYER_UNKNOWN", ())

		if (iIsAttacker == 0):				
			combatMessage = localText.getText("TXT_KEY_COMBAT_MESSAGE_HIT", (szDefenderName, cdDefender.sUnitName, iDamage, cdDefender.iCurrHitPoints, cdDefender.iMaxHitPoints))
			CyInterface().addCombatMessage(cdAttacker.eOwner,combatMessage)
			CyInterface().addCombatMessage(cdDefender.eOwner,combatMessage)
			if (cdDefender.iCurrHitPoints <= 0):
				combatMessage = localText.getText("TXT_KEY_COMBAT_MESSAGE_DEFEATED", (szAttackerName, cdAttacker.sUnitName, szDefenderName, cdDefender.sUnitName))
				CyInterface().addCombatMessage(cdAttacker.eOwner,combatMessage)
				CyInterface().addCombatMessage(cdDefender.eOwner,combatMessage)
		elif (iIsAttacker == 1):
			combatMessage = localText.getText("TXT_KEY_COMBAT_MESSAGE_HIT", (szAttackerName, cdAttacker.sUnitName, iDamage, cdAttacker.iCurrHitPoints, cdAttacker.iMaxHitPoints))
			CyInterface().addCombatMessage(cdAttacker.eOwner,combatMessage)
			CyInterface().addCombatMessage(cdDefender.eOwner,combatMessage)
			if (cdAttacker.iCurrHitPoints <= 0):
				combatMessage = localText.getText("TXT_KEY_COMBAT_MESSAGE_DEFEATED", (szDefenderName, cdDefender.sUnitName, szAttackerName, cdAttacker.sUnitName))
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
##### RtW Stuff
		if (gc.getBuildingInfo(iBuildingType).getDCMNukesOkay()):
                        gc.getPlayer(pCity.getOwner()).setNukesOkay(true)

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
		if (not self.__LOG_MOVEMENT):
			return
		if player and unitInfo:
			CvUtil.pyPrint('Player %d Civilization %s unit %s is moving to %d, %d' 
				%(player.getID(), player.getCivilizationName(), unitInfo.getDescription(), 
				pUnit.getX(), pUnit.getY()))

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
                if (city.getOwner() == gc.getGame().getActivePlayer() and gc.getGame().getAIAutoPlay() == 0 ):
			self.__eventEditCityNameBegin(city, False)	
		CvUtil.pyPrint('City Built Event: %s' %(city.getName()))
		
	def onCityRazed(self, argsList):
		'City Razed'
		city, iPlayer = argsList
		iOwner = city.findHighestCulture()
		CvUtil.pyPrint("City Razed Event: %s" %(city.getName(),))
	
	def onCityAcquired(self, argsList):
		'City Acquired'
		iPreviousOwner,iNewOwner,pCity,bConquest,bTrade = argsList
		CvUtil.pyPrint('City Acquired Event: %s' %(pCity.getName()))
##### RtW Stuff
		player = PyPlayer(pCity.getOwner())
		pCity.setCulture(player.getID(), 1000, True)
	
	def onCityAcquiredAndKept(self, argsList):
		'City Acquired and Kept'
		iOwner,pCity = argsList
		CvUtil.pyPrint('City Acquired and Kept Event: %s' %(pCity.getName()))
##### RtW Stuff
		iPlayer = PyPlayer(pCity.getOwner())
		pCity.setCulture(iPlayer.getID(), 1000, True)
	
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
	
	def onMouseEvent(self, argsList):
		'mouse handler - returns 1 if the event was consumed'
		eventType,mx,my,px,py,interfaceConsumed,screens = argsList
		if ( px!=-1 and py!=-1 ):
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

##### RtW Stuff
        def Jan2_1936Begin(self, argsList):
                rtw.Jan2_1936()
                return

        def Jan2_1936Apply(self, playerID, userData, popupReturn):
                rtw.Jan2_1936Handler(playerID, userData, popupReturn)
                return

##### Dale - Customiser START
        def SetLH(self):
                # This popup allows change of Leaders
                player = gc.getPlayer(gc.getGame().getActivePlayer())
                popup = PyPopup.PyPopup(CvUtil.EventLHPopup, EventContextTypes.EVENTCONTEXT_ALL)
                popup.setHeaderString( "Select Leader" )
                szText = "Select a button to choose a Leader.\n"
                popup.setBodyString( szText )
                popup.addSeparator()
                popup.addButton( "Random Leader: You Only" )
                popup.addButton( "Random Leader: All Civs" )
                for i in range( gc.getNumLeaderHeadInfos() ):
                        popup.addButton( gc.getLeaderHeadInfo(i).getDescription() )
                popup.addSeparator()
                popup.launch(False)

        def LHBegin(self, argsList):
                self.SetLH()
                return

        def LHApply(self, playerID, userData, popupReturn):
        	dice = gc.getGame().getMapRand()
                player = gc.getPlayer(gc.getGame().getActivePlayer())
                autoIdx = popupReturn.getButtonClicked()
                if (autoIdx == 0):
                        leaderList = []
                        for i in range(0, gc.getNumLeaderHeadInfos()):
                            leaderList.append(i)
			if (player.isAlive()):
                            iChoice = dice.get(len(leaderList), "Get Leader")
                            player.setLH(leaderList[iChoice])
                            del leaderList[iChoice]
                        self.SetTraits()
                        return
                if (autoIdx == 1):
                        leaderList = []
                        for i in range(0, gc.getNumLeaderHeadInfos()):
                            leaderList.append(i)
                        for iPlayer in range(gc.getMAX_PLAYERS()):
                            player = gc.getPlayer(iPlayer)
			    if (player.isAlive()):
                                iChoice = dice.get(len(leaderList), "Get Leader")
                                player.setLH(leaderList[iChoice])
                                del leaderList[iChoice]
                        self.SetTraits()
                        return
                autoIdx -= 2
                player.setLH(autoIdx)
                self.SetTraits()
                return

        def SetTraits(self):
                # This popup allows change of traits
                player = gc.getPlayer(gc.getGame().getActivePlayer())
                popup = PyPopup.PyPopup(CvUtil.EventTraitPopup, EventContextTypes.EVENTCONTEXT_ALL)
                popup.setHeaderString( "Select Traits" )
                szText = "Select a button to add/remove your traits. The traits list will update automatically depending on your choices.\nYour current traits are: " + CyGameTextMgr().parseLeaderTraits(player.getLeaderType(), player.getCivilizationType(), True, False) + "\n"
                popup.setBodyString( szText )
                popup.addSeparator()
                popup.addButton( "Finished" )
                popup.addSeparator()
                popup.addButton( "Random Traits: You Only" )
                popup.addButton( "Random Traits: All Civs" )
                for i in range( gc.getNumTraitInfos() ):
                        popup.addButton( gc.getTraitInfo(i).getDescription() )
                popup.addSeparator()
                popup.launch(False)

        def TraitBegin(self, argsList):
                self.SetTraits()
                return

        def TraitApply(self, playerID, userData, popupReturn):
        	dice = gc.getGame().getMapRand()
                player = gc.getPlayer(gc.getGame().getActivePlayer())
                autoIdx = popupReturn.getButtonClicked()
                if (autoIdx == 0):
                        self.SetTechs()
                        return
                if (autoIdx == 1):
			if (player.isAlive()):
                            traitList = []
                            for i in range(0, gc.getNumTraitInfos()):
                                player.setTrait(i, False)
                                traitList.append(i)
                            iChoice = dice.get(len(traitList), "Get Trait")
                            player.setTrait(traitList[iChoice], True)
                            del traitList[iChoice]
                            iChoice = dice.get(len(traitList), "Get Trait")
                            player.setTrait(traitList[iChoice], True)
                            del traitList[iChoice]
                        self.SetTechs()
                        return
                if (autoIdx == 2):
                        for iPlayer in range(gc.getMAX_PLAYERS()):
                            player = gc.getPlayer(iPlayer)
			    if (player.isAlive()):
                                traitList = []
                                for i in range(0, gc.getNumTraitInfos()):
                                    player.setTrait(i, False)
                                    traitList.append(i)
                                iChoice = dice.get(len(traitList), "Get Trait")
                                player.setTrait(traitList[iChoice], True)
                                del traitList[iChoice]
                                iChoice = dice.get(len(traitList), "Get Trait")
                                player.setTrait(traitList[iChoice], True)
                                del traitList[iChoice]
                        self.SetTechs()
                        return
                autoIdx -= 3
                if (player.hasTrait(autoIdx)):
                        player.setTrait(autoIdx, False)
                else:
                        player.setTrait(autoIdx, True)
                self.SetTraits()
                return

        def SetTechs(self):
                # This popup allows change of techs
                player = gc.getPlayer(gc.getGame().getActivePlayer())
                popup = PyPopup.PyPopup(CvUtil.EventTechPopup, EventContextTypes.EVENTCONTEXT_ALL)
                popup.setHeaderString( "Select Techs" )
                szText = "Select a button to add/remove your techs. The techs list will update automatically depending on your choices.\nYour current techs are: "
                comma = False
                for i in range( gc.getNumTechInfos() ):
                        if (player.getTech(i)):
                            if (comma == True):
                                szText += ", "
                            szText += gc.getTechInfo(i).getDescription()
                            comma = True
                szText += "\n"
                popup.setBodyString( szText )
                popup.addSeparator()
                popup.addButton( "Finished" )
                popup.addSeparator()
                for i in range( gc.getNumTechInfos() ):
                        popup.addButton( gc.getTechInfo(i).getDescription() )
                popup.addSeparator()
                popup.launch(False)

        def TechBegin(self, argsList):
                self.SetTechs()
                return

        def TechApply(self, playerID, userData, popupReturn):
                player = gc.getPlayer(gc.getGame().getActivePlayer())
                autoIdx = popupReturn.getButtonClicked()
                if (autoIdx == 0):
                        self.SetUB()
                        return
                autoIdx -= 1
                if (player.getTech(autoIdx)):
                        player.setTech(autoIdx, False)
                        gc.getTeam(player.getTeam()).setHasTech(autoIdx, False, player.getID(), False, False)
                else:
                        player.setTech(autoIdx, True)
                        gc.getTeam(player.getTeam()).setHasTech(autoIdx, True, player.getID(), False, False)
                self.SetTechs()
                return

        def SetUB(self):
                # This popup allows change of UB's
                player = gc.getPlayer(gc.getGame().getActivePlayer())
                popup = PyPopup.PyPopup(CvUtil.EventUBPopup, EventContextTypes.EVENTCONTEXT_ALL)
                popup.setHeaderString( "Select Unique Buildings" )
                popup.setBodyString( "To set unique buildings, choose a building in the pulldown to replace the default building class.  To not replace the default building class leave the pulldown as Default. Click Finished once complete." )
                popup.addSeparator()
                popup.addButton( "Finished" )
                popup.addSeparator()
                for i in range( 0, gc.getNumBuildingClassInfos() ):
                        szText = gc.getBuildingClassInfo(i).getDescription() + " ="
                        popup.setBodyString( szText )
                        popup.createPullDown(i)
                        for j in range(-1, gc.getNumBuildingInfos()):
                            if (j == -1):
                                popup.addPullDownString( "Default", 0, i)
                            else:
                                popup.addPullDownString( gc.getBuildingInfo(j).getDescription(), (j + 1), i)
                        popup.popup.setSelectedPulldownID(0, i)
                popup.addSeparator()
                popup.launch(False)

        def UBBegin(self, argsList):
                self.SetUB()
                return

        def UBApply(self, playerID, userData, popupReturn):
                player = gc.getPlayer(gc.getGame().getActivePlayer())
                for i in range( 0, gc.getNumBuildingClassInfos() ):
                        autoIdx = popupReturn.getSelectedPullDownValue(i)
                        if (not autoIdx == 0):
                            autoIdx -= 1
                            player.setUB(i, autoIdx)
                self.SetUU()
                return

        def SetUU(self):
                # This popup allows change of UU's
                player = gc.getPlayer(gc.getGame().getActivePlayer())
                popup = PyPopup.PyPopup(CvUtil.EventUUPopup, EventContextTypes.EVENTCONTEXT_ALL)
                popup.setHeaderString( "Select Unique Units" )
                popup.setBodyString( "To set unique units, choose a unit in the pulldown to replace the default unit class.  To not replace the default unit class leave the pulldown as Default. Click Finished once complete." )
                popup.addSeparator()
                popup.addButton( "Finished" )
                popup.addSeparator()
                for i in range( 0, gc.getNumUnitClassInfos() ):
                        szText = gc.getUnitClassInfo(i).getDescription() + " ="
                        popup.setBodyString( szText )
                        popup.createPullDown(i)
                        for j in range(-1, gc.getNumUnitInfos()):
                            if (j == -1):
                                popup.addPullDownString( "Default", 0, i)
                            else:
                                popup.addPullDownString( gc.getUnitInfo(j).getDescription(), (j + 1), i)
                        popup.popup.setSelectedPulldownID(0, i)
                popup.addSeparator()
                popup.launch(False)

        def UUBegin(self, argsList):
                self.SetUU()
                return

        def UUApply(self, playerID, userData, popupReturn):
                player = gc.getPlayer(gc.getGame().getActivePlayer())
                for i in range( 0, gc.getNumUnitClassInfos() ):
                        autoIdx = popupReturn.getSelectedPullDownValue(i)
                        if (not autoIdx == 0):
                            autoIdx -= 1
                            player.setUU(i, autoIdx)
                return
##### Dale - Customiser END

##### DCM Status Popup START
        def DisplayDCMStatus(self):
                popup = PyPopup.PyPopup(CvUtil.EventDCMPopup, EventContextTypes.EVENTCONTEXT_ALL)
                szTitle = localText.getText("TXT_KEY_DCM_TITLE", ())
                szText = localText.getText("TXT_KEY_DCM_TEXT", ())
                szText += "\n\n"
                szText += "Air Bombing: "
                if (gc.getDCM_AIR_BOMBING() == 1):
                        szText += "On\n"
                else:
                        szText += "Off\n"
                szText += "Battle Effects: "
                if (gc.getDCM_BATTLE_EFFECTS() == 1):
                        szText += "On\n"
                else:
                        szText += "Off\n"
                szText += "Civ Customiser: "
                if (gc.getDCM_CIV_CUSTOMISER() == 1):
                        szText += "On\n"
                else:
                        szText += "Off\n"
                szText += "Ranged Bombardment: "
                if (gc.getDCM_RANGE_BOMBARD() == 1):
                        szText += "On\n"
                else:
                        szText += "Off\n"
                szText += "Civ Changer: "
                if (gc.getDCM_CIV_CHANGER() == 1):
                        szText += "On\n"
                else:
                        szText += "Off\n"
                szText += "Stack Attack: "
                if (gc.getDCM_STACK_ATTACK() == 1):
                        szText += "On\n"
                else:
                        szText += "Off\n"
                szText += "Opportunity Fire: "
                if (gc.getDCM_OPP_FIRE() == 1):
                        szText += "On\n"
                else:
                        szText += "Off\n"
                szText += "Active Defense: "
                if (gc.getDCM_ACTIVE_DEFENSE() == 1):
                        szText += "On\n"
                else:
                        szText += "Off\n"
                szText += "Archer Bombard: "
                if (gc.getDCM_ARCHER_BOMBARD() == 1):
                        szText += "On\n"
                else:
                        szText += "Off\n"
                popup.setHeaderString(szTitle)
                popup.addSeparator()
                popup.setBodyString(szText)
#                popup.launch()

        def DCMBegin(self, argsList):
                self.DisplayDCMStatus()
                return

        def DCMApply(self, playerID, userData, popupReturn):
##### Dale - Customiser START
		if (gc.getDCM_CIV_CUSTOMISER() == 1):
                        for iPlayer in range(gc.getMAX_PLAYERS()):
                                player = gc.getPlayer(iPlayer)
                                if (player.isAlive() and player.isHuman()):
                                        self.SetLH()
##### Dale - Customiser END
                return
##### DCM Status Popup END

##### Dale - Chooser START
        def ChangeCivBegin(self, argsList):
                self.ChangeCiv_Popup()
                return

        def ChangeCivApply(self, playerID, userData, popupReturn):
                self.ChangeCiv_PopupHandler(playerID, userData, popupReturn)
                return

        def ChangeCiv_Popup(self):
                # This popup allows change of Civ
                popup = PyPopup.PyPopup(CvUtil.EventChangeCiv_Popup, contextType = EventContextTypes.EVENTCONTEXT_ALL)
                if (not gc.getDCM_CIV_CHANGER()):
                    return
                if (gc.getDCM_CIV_CHANGER_CHANGES() < CyGame().getChangeCiv()):
                    popup.setHeaderString(localText.getText("TXT_KEY_CHANGECIV_TITLE2", ()))
                    popup.setBodyString(localText.getText("TXT_KEY_CHANGECIV_TEXT2", ()))
                    popup.launch()
                    return
                popup.setHeaderString(localText.getText("TXT_KEY_CHANGECIV_TITLE", ()))
                popup.setBodyString(localText.getText("TXT_KEY_CHANGECIV_TEXT", ()))
                popup.addButton(localText.getText("TXT_KEY_CHANGECIV_CANCEL", ()))
                popup.addSeparator()
                popup.addSeparator()
                for i in range(gc.getMAX_CIV_PLAYERS()):
                    if (gc.getPlayer(i) != gc.getGame().getActivePlayer()):
                        if (gc.getPlayer(i).isAlive()):
                            if (gc.getDCM_CIV_CHANGER_MODE() == 0):
                                popup.addButton(gc.getPlayer(i).getCivilizationShortDescription(0))
                            if (gc.getDCM_CIV_CHANGER_MODE() == 1):
                                if (gc.getGame().getActiveTeam() == gc.getPlayer(i).getTeam()):
                                    popup.addButton(gc.getPlayer(i).getCivilizationShortDescription(0))
                            if (gc.getDCM_CIV_CHANGER_MODE() == 2):
                                if (gc.getTeam(gc.getGame().getActiveTeam()).isHasMet(gc.getPlayer(i).getTeam())):
                                    popup.addButton(gc.getPlayer(i).getCivilizationShortDescription(0))
                            if (gc.getDCM_CIV_CHANGER_MODE() == 3):
                                if (not gc.getActivePlayer().getCapitalCity().isNone() and not gc.getPlayer(i).getCapitalCity().isNone()):
                                    if (gc.getActivePlayer().getCapitalCity().plot().getArea() == gc.getPlayer(i).getCapitalCity().plot().getArea()):
                                        popup.addButton(gc.getPlayer(i).getCivilizationShortDescription(0))
                popup.launch(False)

        def ChangeCiv_PopupHandler(self, playerID, netUserData, popupReturn):
                autoIdx = popupReturn.getButtonClicked()
                if (autoIdx == 0):
                    return
                if (not gc.getDCM_CIV_CHANGER()):
                    return
                autoIdx -= 1
                CyGame().setChangeCiv(CyGame().getChangeCiv() + 1)
                counter = 0
                for i in range(gc.getMAX_CIV_PLAYERS()):
                    if (gc.getPlayer(i).isAlive()):
                        if (gc.getDCM_CIV_CHANGER_MODE() == 0):
                            if (autoIdx == counter):
                                gc.getGame().setActivePlayer(i, False)
                                return
                            else:
                                counter += 1
                        if (gc.getDCM_CIV_CHANGER_MODE() == 1):
                            if (gc.getGame().getActiveTeam() == gc.getPlayer(i).getTeam()):
                                if (autoIdx == counter):
                                    gc.getGame().setActivePlayer(i, False)
                                    return
                                else:
                                    counter += 1
                        if (gc.getDCM_CIV_CHANGER_MODE() == 2):
                            if (gc.getTeam(gc.getGame().getActiveTeam()).isHasMet(gc.getPlayer(i).getTeam())):
                                if (autoIdx == counter):
                                    gc.getGame().setActivePlayer(i, False)
                                    return
                                else:
                                    counter += 1
                        if (gc.getDCM_CIV_CHANGER_MODE() == 3):
                            if (gc.getActivePlayer().getCapitalCity().plot().getArea() == gc.getPlayer(i).getCapitalCity().plot().getArea()):
                                if (autoIdx == counter):
                                    gc.getGame().setActivePlayer(i, False)
                                    return
                                else:
                                    counter += 1
##### Dale - Chooser END
