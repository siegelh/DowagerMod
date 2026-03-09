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
import GodsOfOld
import pickle

gc = CyGlobalContext()
localText = CyTranslator()
PyPlayer = PyHelpers.PyPlayer
PyInfo = PyHelpers.PyInfo
PyCity = PyHelpers.PyCity
PyGame = PyHelpers.PyGame


# globals
###################################################
class CvEventManager:
	def __init__(self):
		#################### ON EVENT MAP ######################
		# Gods variables
		# private
		self.clearGodsVariables()
				
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
		self.DemoCount = 0
		
		#Net Messages
		self.m_iNetMessage_Inquisitor = 0
		self.m_iNetMessage_ProphetKi = 1
		self.m_iNetMessage_ProphetEnki = 2
		self.m_iNetMessage_ProphetEnlil = 3
		self.m_iNetMessage_ProphetNanna = 4
		self.m_iNetMessage_ProphetUtu = 5
		self.m_iNetMessage_ProphetAn = 6
		
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
											
				elif (self.bCtrl and self.bShift and theKey == int(InputTypes.KB_Y)):
					if self.DemoCount == 0:
						CyGame().toggleDebugMode()
						CvCameraControls.g_CameraControls.doRotateGlobe()
						self.DemoCount += 1
						return 1
					
					elif self.DemoCount == 1:
						CyCamera().SetZoom(0.2)
						CyCamera().JustLookAtPlot(CyMap().plot(31,16))
						CvCameraControls.g_CameraControls.resetCameraControls()
						CyInterface().setShowInterface(InterfaceVisibility.INTERFACE_SHOW)
						CyEngine().setCityBillboardVisibility(True)
						self.DemoCount += 1
						return 1
					
					elif self.DemoCount == 2:
						CyGame().toggleDebugMode()
						self.DemoCount = 0
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

		iMessageID = iData1
		
		#Inquisitor's Effect on a City
		if ( iMessageID == self.m_iNetMessage_Inquisitor ):
			
			iPlotX = iData2
			iPlotY = iData3
			iOwner = iData4
			iUnitID = iData5
			
			pPlot = CyMap( ).plot( iPlotX, iPlotY )
			pCity = pPlot.getPlotCity( )
			pPlayer = gc.getPlayer( iOwner )
			pUnit = pPlayer.getUnit( iUnitID )
			
			self.doInquisitorPersecution( pCity, pUnit )
			
		#Prophet of Ki Effect
		if ( iMessageID == self.m_iNetMessage_ProphetKi ):
			
			iPlotX = iData2
			iPlotY = iData3
			iOwner = iData4
			iUnitID = iData5
			
			pPlot = CyMap( ).plot( iPlotX, iPlotY )					
			pPlayer = gc.getPlayer( iOwner )
			pUnit = pPlayer.getUnit( iUnitID )

			self.doEventEarthquake(pPlot)
			pUnit.kill( 0, -1 )
			if pPlot.getOwner( ) >= 0:		
				if not ( gc.getPlayer( pPlot.getOwner( ) ).isHuman( ) ):
					gc.getPlayer( pPlot.getOwner()).AI_changeAttitudeExtra( iOwner, -5 )
					szAttackedCiv = gc.getPlayer( pPlot.getOwner()).getCivilizationDescriptionKey()
					szAttackingCiv = pPlayer.getCivilizationDescriptionKey()
					szTitle = localText.getText("TXT_KEY_GODS_DISASTER_ANGER", (szAttackedCiv , szAttackingCiv, ))
					CyInterface().addImmediateMessage( szTitle , None)
				else:
					szAttackedCiv = gc.getPlayer( pPlot.getOwner()).getCivilizationDescriptionKey()
					szAttackingCiv = pPlayer.getCivilizationDescriptionKey()
					szTitle = localText.getText("TXT_KEY_GODS_DISASTER_HUMAN", (szAttackedCiv , szAttackingCiv, ))				

					
			
		#Prophet of Enki Effect
		if ( iMessageID == self.m_iNetMessage_ProphetEnki ):

			iPlotX = iData2
			iPlotY = iData3
			iOwner = iData4
			iUnitID = iData5
			
			pPlot = CyMap( ).plot( iPlotX, iPlotY )					
			pPlayer = gc.getPlayer( iOwner )
			pUnit = pPlayer.getUnit( iUnitID )			
			
			self.doEventTsunami(pPlot)
			pUnit.kill( 0, -1 )	
			if pPlot.getOwner( ) >= 0:
				if not ( gc.getPlayer( pPlot.getOwner( ) ).isHuman( ) ):
					gc.getPlayer( pPlot.getOwner()).AI_changeAttitudeExtra( iOwner, -5 )
					szAttackedCiv = gc.getPlayer( pPlot.getOwner()).getCivilizationDescriptionKey()
					szAttackingCiv = pPlayer.getCivilizationDescriptionKey()
					szTitle = localText.getText("TXT_KEY_GODS_DISASTER_ANGER", (szAttackedCiv , szAttackingCiv, ))
					CyInterface().addImmediateMessage( szTitle , None)
				else:
					szAttackedCiv = gc.getPlayer( pPlot.getOwner()).getCivilizationDescriptionKey()
					szAttackingCiv = pPlayer.getCivilizationDescriptionKey()
					szTitle = localText.getText("TXT_KEY_GODS_DISASTER_HUMAN", (szAttackedCiv , szAttackingCiv, ))				


		#Prophet of Enlil Effect
		if ( iMessageID == self.m_iNetMessage_ProphetEnlil ):

			iPlotX = iData2
			iPlotY = iData3
			iOwner = iData4
			iUnitID = iData5
			
			pPlot = CyMap( ).plot( iPlotX, iPlotY )					
			pPlayer = gc.getPlayer( iOwner )
			pUnit = pPlayer.getUnit( iUnitID )			
			
			self.doEventPlague(pPlot)
			pUnit.kill( 0, -1 )
			if pPlot.getOwner( ) >= 0:
				if not ( gc.getPlayer( pPlot.getOwner( ) ).isHuman( ) ):
					gc.getPlayer( pPlot.getOwner()).AI_changeAttitudeExtra( iOwner, -5 )
					szAttackedCiv = gc.getPlayer( pPlot.getOwner()).getCivilizationDescriptionKey()
					szAttackingCiv = pPlayer.getCivilizationDescriptionKey()
					szTitle = localText.getText("TXT_KEY_GODS_DISASTER_ANGER", (szAttackedCiv , szAttackingCiv, ))
					CyInterface().addImmediateMessage( szTitle , None)
				else:
					szAttackedCiv = gc.getPlayer( pPlot.getOwner()).getCivilizationDescriptionKey()
					szAttackingCiv = pPlayer.getCivilizationDescriptionKey()
					szTitle = localText.getText("TXT_KEY_GODS_DISASTER_HUMAN", (szAttackedCiv , szAttackingCiv, ))				


		#Prophet of Nanna Effect
		if ( iMessageID == self.m_iNetMessage_ProphetNanna ):

			iPlotX = iData2
			iPlotY = iData3
			iOwner = iData4
			iUnitID = iData5
			
			pPlot = CyMap( ).plot( iPlotX, iPlotY )					
			pPlayer = gc.getPlayer( iOwner )
			pUnit = pPlayer.getUnit( iUnitID )			
			
			pUnit.kill( 0, -1 )
			self.doEventMinorMeteorStrike(pPlot)
			if pPlot.getOwner( ) >= 0:
				if not ( gc.getPlayer( pPlot.getOwner( ) ).isHuman( ) ):
					gc.getPlayer( pPlot.getOwner()).AI_changeAttitudeExtra( iOwner, -5 )
					szAttackedCiv = gc.getPlayer( pPlot.getOwner()).getCivilizationDescriptionKey()
					szAttackingCiv = pPlayer.getCivilizationDescriptionKey()
					szTitle = localText.getText("TXT_KEY_GODS_DISASTER_ANGER", (szAttackedCiv , szAttackingCiv, ))
					CyInterface().addImmediateMessage( szTitle , None)
				else:
					szAttackedCiv = gc.getPlayer( pPlot.getOwner()).getCivilizationDescriptionKey()
					szAttackingCiv = pPlayer.getCivilizationDescriptionKey()
					szTitle = localText.getText("TXT_KEY_GODS_DISASTER_HUMAN", (szAttackedCiv , szAttackingCiv, ))				


		#Prophet of Utu Effect
		if ( iMessageID == self.m_iNetMessage_ProphetUtu ):

			iPlotX = iData2
			iPlotY = iData3
			iOwner = iData4
			iUnitID = iData5
			
			pPlot = CyMap( ).plot( iPlotX, iPlotY )					
			pPlayer = gc.getPlayer( iOwner )
			pUnit = pPlayer.getUnit( iUnitID )			
			
			self.doEventBlight(pPlot)
			pUnit.kill( 0, -1 )
			if pPlot.getOwner( ) >= 0:
				if not ( gc.getPlayer( pPlot.getOwner( ) ).isHuman( ) ):
					gc.getPlayer( pPlot.getOwner()).AI_changeAttitudeExtra( iOwner, -5 )
					szAttackedCiv = gc.getPlayer( pPlot.getOwner()).getCivilizationDescriptionKey()
					szAttackingCiv = pPlayer.getCivilizationDescriptionKey()
					szTitle = localText.getText("TXT_KEY_GODS_DISASTER_ANGER", (szAttackedCiv , szAttackingCiv, ))
					CyInterface().addImmediateMessage( szTitle , None)
				else:
					szAttackedCiv = gc.getPlayer( pPlot.getOwner()).getCivilizationDescriptionKey()
					szAttackingCiv = pPlayer.getCivilizationDescriptionKey()
					szTitle = localText.getText("TXT_KEY_GODS_DISASTER_HUMAN", (szAttackedCiv , szAttackingCiv, ))				

			
		#Prophet of An Effect
		if ( iMessageID == self.m_iNetMessage_ProphetAn ):

			iAttackingOwner = iData2
			iAttackingUnitID = iData3
			iDefendingOwner = iData4
			iDefendingUnitID = iData5
			
			pAttackingPlayer = gc.getPlayer( iAttackingOwner )
			pAttackingUnit = pAttackingPlayer.getUnit( iAttackingUnitID )			
			pDefendingPlayer = gc.getPlayer( iDefendingOwner )
			pDefendingUnit = pDefendingPlayer.getUnit( iDefendingUnitID )

			pAttackingUnit.kill( 0, -1 )			
			pDefendingUnit.kill( 0, -1 )

			if not ( pDefendingPlayer.isHuman( ) ):
				pDefendingPlayer.AI_changeAttitudeExtra( iAttackingOwner, -5 )

				szAttackedCiv = pDefendingPlayer.getCivilizationDescriptionKey()
				szAttackingCiv = pAttackingPlayer.getCivilizationDescriptionKey()
				szTitle = localText.getText("TXT_KEY_GODS_DISASTER_ANGER_BLOCKED", (szAttackedCiv , szAttackingCiv, ))
				CyInterface().addImmediateMessage( szTitle , None)			
			else:
				szAttackedCiv = pDefendingPlayer.getCivilizationDescriptionKey()
				szAttackingCiv = pAttackingPlayer.getCivilizationDescriptionKey()
				szTitle = localText.getText("TXT_KEY_GODS_DISASTER_HUMAN_BLOCKED", (szAttackedCiv , szAttackingCiv, ))
				CyInterface().addImmediateMessage( szTitle , None)	
			
						
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
		self.setGodsVariables()
	
	def onSaveGame(self, argsList):
		"return the string to be saved - Must be a string"
		return ""

	def onLoadGame(self, argsList):
		CvAdvisorUtils.resetNoLiberateCities()
		self.getGodsVariables()
		return 0

	def onGameStart(self, argsList):
		'Called at the start of the game'
		self.clearGodsVariables( )

		if (gc.getGame().getGameTurnYear() == gc.getDefineINT("START_YEAR") and not gc.getGame().isOption(GameOptionTypes.GAMEOPTION_ADVANCED_START)):
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
																	
		CvAdvisorUtils.resetNoLiberateCities()
																	
	def onGameEnd(self, argsList):
		'Called at the End of the game'
		print("Game is ending")
		return

	def onBeginGameTurn(self, argsList):
		'Called at the beginning of the end of each turn'
		iGameTurn = argsList[0]
		CvTopCivs.CvTopCivs().turnChecker(iGameTurn)

		# Should we start checking for Religious victory
		if self.iReligiousVictoryPossible == 0:
			self.doReligiousVictoryPossible( )
		
		# Religious Victory check
		if self.iReligiousVictoryPossible == 1:
			self.doReligiousVictoryCheck()
		
		#Plague
		if gc.getMap().plotByIndex(0).getScriptData() == "Plague On":
			self.doPlagueSpread()
		else:
			self.doPlagueDecay()
		
		#Constalations
		if ( iGameTurn % 5 ) == 0:
			self.doChooseNewStarAlignment( )

	def onEndGameTurn(self, argsList):
		'Called at the end of the end of each turn'
		iGameTurn = argsList[0]
		
	def onBeginPlayerTurn(self, argsList):
		'Called at the beginning of a players turn'
		iGameTurn, iPlayer = argsList

		if not gc.getPlayer( iPlayer ).isHuman():
			self.doAIOperations( iPlayer )

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
		pPlotOwner = PyPlayer(pPlot.getOwner())
		CvUtil.pyPrint('Plot was picked at %d, %d'
			%(pPlot.getX(), pPlot.getY()))

		# Protection of An
		if pPlot.getOwner() != -1:
			if pPlotOwner.getStateReligion() == CvUtil.findInfoTypeNum(gc.getReligionInfo, gc.getNumReligionInfos(), "RELIGION_AN"):
				lUnit = pPlotOwner.getUnitList()
				for unit in lUnit:
					if unit.getUnitType() == CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), "UNIT_PROPHET"):
						pAttackingUnit = GodsOfOld.iPushedButtonUnit
						
						
						iMessageID = self.m_iNetMessage_ProphetAn						
						iAttackingOwner = pAttackingUnit.getOwner( )
						iAttackingUnitID = pAttackingUnit.getID( )
						iDefendingOwner = unit.getOwner( )
						iDefendingUnitID = unit.getID( )
			
						CyMessageControl( ).sendModNetMessage( iMessageID, iAttackingOwner, iAttackingUnitID, iDefendingOwner, iDefendingUnitID )
						return
	
		# Prophet of Ki
		if GodsOfOld.iPushButton == 1:
			pUnit = GodsOfOld.iPushedButtonUnit
			
			iMessageID = self.m_iNetMessage_ProphetKi
			iPlotX = pPlot.getX()
			iPlotY = pPlot.getY()
			iOwner = pUnit.getOwner()
			iUnitID = pUnit.getID()
			
			pUnitOwner = gc.getPlayer(iOwner)
			if pUnitOwner.isTurnActive( ):

				CyMessageControl( ).sendModNetMessage( iMessageID, iPlotX, iPlotY, iOwner, iUnitID )

		# Prophet of Enki
		if GodsOfOld.iPushButton == 2:
			pUnit = GodsOfOld.iPushedButtonUnit
			
			iMessageID = self.m_iNetMessage_ProphetEnki
			iPlotX = pPlot.getX()
			iPlotY = pPlot.getY()
			iOwner = pUnit.getOwner()
			iUnitID = pUnit.getID()

			pUnitOwner = gc.getPlayer(iOwner)
			if pUnitOwner.isTurnActive( ):
					
				CyMessageControl( ).sendModNetMessage( iMessageID, iPlotX, iPlotY, iOwner, iUnitID )			
			

		# Prophet of Enlil
		if GodsOfOld.iPushButton == 3:
			pUnit = GodsOfOld.iPushedButtonUnit
						
			iMessageID = self.m_iNetMessage_ProphetEnlil
			iPlotX = pPlot.getX()
			iPlotY = pPlot.getY()
			iOwner = pUnit.getOwner()
			iUnitID = pUnit.getID()

			pUnitOwner = gc.getPlayer(iOwner)
			if pUnitOwner.isTurnActive( ):
					
				CyMessageControl( ).sendModNetMessage( iMessageID, iPlotX, iPlotY, iOwner, iUnitID )				
			
		# Prophet of Nanna
		if GodsOfOld.iPushButton == 4:
			pUnit = GodsOfOld.iPushedButtonUnit
						
			iMessageID = self.m_iNetMessage_ProphetNanna
			iPlotX = pPlot.getX()
			iPlotY = pPlot.getY()
			iOwner = pUnit.getOwner()
			iUnitID = pUnit.getID()

			pUnitOwner = gc.getPlayer(iOwner)
				
			if pUnitOwner.isTurnActive( ):
				CyMessageControl( ).sendModNetMessage( iMessageID, iPlotX, iPlotY, iOwner, iUnitID )				
			
		# Prophet of Utu
		if GodsOfOld.iPushButton == 5:
			pUnit = GodsOfOld.iPushedButtonUnit
						
			iMessageID = self.m_iNetMessage_ProphetUtu
			iPlotX = pPlot.getX()
			iPlotY = pPlot.getY()
			iOwner = pUnit.getOwner()
			iUnitID = pUnit.getID()

			pUnitOwner = gc.getPlayer(iOwner)
			if pUnitOwner.isTurnActive( ):
				CyMessageControl( ).sendModNetMessage( iMessageID, iPlotX, iPlotY, iOwner, iUnitID )				
			
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

		if iBuildingType == CvUtil.findInfoTypeNum(gc.getBuildingInfo, gc.getNumBuildingInfos(), "BUILDING_KI_SHRINE"):
			iReligion = CvUtil.findInfoTypeNum(gc.getReligionInfo, gc.getNumReligionInfos(), "RELIGION_KI")
			gc.getGame( ).setHolyCity(iReligion, pCity, 1)
		if iBuildingType == CvUtil.findInfoTypeNum(gc.getBuildingInfo, gc.getNumBuildingInfos(), "BUILDING_ENKI_SHRINE"):
			iReligion = CvUtil.findInfoTypeNum(gc.getReligionInfo, gc.getNumReligionInfos(), "RELIGION_ENKI")
			gc.getGame( ).setHolyCity(iReligion, pCity, 1)
		if iBuildingType == CvUtil.findInfoTypeNum(gc.getBuildingInfo, gc.getNumBuildingInfos(), "BUILDING_ENLIL_SHRINE"):
			iReligion = CvUtil.findInfoTypeNum(gc.getReligionInfo, gc.getNumReligionInfos(), "RELIGION_ENLIL")
			gc.getGame( ).setHolyCity(iReligion, pCity, 1)
		if iBuildingType == CvUtil.findInfoTypeNum(gc.getBuildingInfo, gc.getNumBuildingInfos(), "BUILDING_INANNA_SHRINE"):
			iReligion = CvUtil.findInfoTypeNum(gc.getReligionInfo, gc.getNumReligionInfos(), "RELIGION_INANNA")
			gc.getGame( ).setHolyCity(iReligion, pCity, 1)
		if iBuildingType == CvUtil.findInfoTypeNum(gc.getBuildingInfo, gc.getNumBuildingInfos(), "BUILDING_NANNA_SHRINE"):
			iReligion = CvUtil.findInfoTypeNum(gc.getReligionInfo, gc.getNumReligionInfos(), "RELIGION_NANNA")
			gc.getGame( ).setHolyCity(iReligion, pCity, 1)
		if iBuildingType == CvUtil.findInfoTypeNum(gc.getBuildingInfo, gc.getNumBuildingInfos(), "BUILDING_UTU_SHRINE"):
			iReligion = CvUtil.findInfoTypeNum(gc.getReligionInfo, gc.getNumReligionInfos(), "RELIGION_UTU")
			gc.getGame( ).setHolyCity(iReligion, pCity, 1)
		if iBuildingType == CvUtil.findInfoTypeNum(gc.getBuildingInfo, gc.getNumBuildingInfos(), "BUILDING_AN_SHRINE"):
			iReligion = CvUtil.findInfoTypeNum(gc.getReligionInfo, gc.getNumReligionInfos(), "RELIGION_AN")
			gc.getGame( ).setHolyCity(iReligion, pCity, 1)

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
		if CyGame().getActivePlayer() == iPlayer:
			if iTechType == CvUtil.findInfoTypeNum(gc.getTechInfo, gc.getNumTechInfos(), "TECH_MASONRY"):
				self.addPopup( "TXT_KEY_GODS_KI_POPUP_TITLE", "TXT_KEY_GODS_KI_POPUP_BODY" )
			if iTechType == CvUtil.findInfoTypeNum(gc.getTechInfo, gc.getNumTechInfos(), "TECH_SAILING"):
				self.addPopup( "TXT_KEY_GODS_ENKI_POPUP_TITLE", "TXT_KEY_GODS_ENKI_POPUP_BODY" )
			if iTechType == CvUtil.findInfoTypeNum(gc.getTechInfo, gc.getNumTechInfos(), "TECH_ARCHERY"):
				self.addPopup( "TXT_KEY_GODS_ENLIL_POPUP_TITLE", "TXT_KEY_GODS_ENLIL_POPUP_BODY" )
			if iTechType == CvUtil.findInfoTypeNum(gc.getTechInfo, gc.getNumTechInfos(), "TECH_BRONZE_WORKING"):
				self.addPopup( "TXT_KEY_GODS_INANNA_POPUP_TITLE", "TXT_KEY_GODS_INANNA_POPUP_BODY" )
			if iTechType == CvUtil.findInfoTypeNum(gc.getTechInfo, gc.getNumTechInfos(), "TECH_MEDITATION"):
				self.addPopup( "TXT_KEY_GODS_NANNA_POPUP_TITLE", "TXT_KEY_GODS_NANNA_POPUP_BODY" )
			if iTechType == CvUtil.findInfoTypeNum(gc.getTechInfo, gc.getNumTechInfos(), "TECH_POLYTHEISM"):
				self.addPopup( "TXT_KEY_GODS_UTU_POPUP_TITLE", "TXT_KEY_GODS_UTU_POPUP_BODY" )
			if iTechType == CvUtil.findInfoTypeNum(gc.getTechInfo, gc.getNumTechInfos(), "TECH_ANIMAL_HUSBANDRY"):
				self.addPopup( "TXT_KEY_GODS_AN_POPUP_TITLE", "TXT_KEY_GODS_AN_POPUP_BODY" )		
				
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
		iOwner = city.findHighestCulture()
		# Partisans!
		if city.getPopulation > 1 and iOwner != -1 and iPlayer != -1:
			owner = gc.getPlayer(iOwner)
			if not owner.isBarbarian() and owner.getNumCities() > 0:
				if gc.getTeam(owner.getTeam()).isAtWar(gc.getPlayer(iPlayer).getTeam()):
					if gc.getNumEventTriggerInfos() > 0: # prevents mods that don't have events from getting an error
						iEvent = CvUtil.findInfoTypeNum(gc.getEventTriggerInfo, gc.getNumEventTriggerInfos(),'EVENTTRIGGER_PARTISANS')
						if iEvent != -1 and gc.getGame().isEventActive(iEvent) and owner.getEventTriggerWeight(iEvent) < 0:
							triggerData = owner.initTriggeredData(iEvent, true, -1, city.getX(), city.getY(), iPlayer, city.getID(), -1, -1, -1, -1)
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


##########Disasters####################
	def doEventEarthquake(self, plot):
		iSeverity = 3
		plotX = plot.getX()
		plotY = plot.getY()
		
		earthquakeEffect = CvUtil.findInfoTypeNum( gc.getEffectInfo, gc.getNumEffectInfos( ), "EFFECT_RES_BOMB" )
		
		CyEngine( ).triggerEffect( earthquakeEffect, plot.getPoint( ) )
		CyEngine( ).triggerEffect( earthquakeEffect, gc.getMap( ).plot( plot.getX( ) + 1, plot.getY( ) + 1 ).getPoint( ) )
		CyEngine( ).triggerEffect( earthquakeEffect, gc.getMap( ).plot( plot.getX( ) + 1, plot.getY( ) - 1 ).getPoint( ) )
		CyEngine( ).triggerEffect( earthquakeEffect, gc.getMap( ).plot( plot.getX( ) - 1, plot.getY( ) + 1 ).getPoint( ) )		
		CyEngine( ).triggerEffect( earthquakeEffect, gc.getMap( ).plot( plot.getX( ) - 1, plot.getY( ) - 1 ).getPoint( ) )		
		
			
		for i in range(iSeverity):
			if i == 0:
				self.doEarthquakeDevastation(plotX, plotY, iSeverity)
			else:
				self.doEarthquakeDevastation(plotX - i, plotY, iSeverity-i)
				self.doEarthquakeDevastation(plotX - i, plotY - i, iSeverity-i)
				self.doEarthquakeDevastation(plotX, plotY - i, iSeverity-i)
				self.doEarthquakeDevastation(plotX + i, plotY - i, iSeverity-i)
				self.doEarthquakeDevastation(plotX + i, plotY, iSeverity-i)
				self.doEarthquakeDevastation(plotX + i, plotY + i, iSeverity-i)
				self.doEarthquakeDevastation(plotX, plotY + i, iSeverity-i)
				self.doEarthquakeDevastation(plotX - i, plotY + i, iSeverity-i)
	
	def doEarthquakeDevastation(self, iX, iY, iSeverity):
		plot = gc.getMap().plot(iX, iY)
		iEarthquakeEffect = CvUtil.findInfoTypeNum( gc.getEffectInfo, gc.getNumEffectInfos( ), "EFFECT_RES_BOMB" )
		
		if plot.isCity():
			city = plot.getPlotCity()
			szCityName = city.getName()
			pyCity = PyCity(city.getOwner(), city.getID())
			if iSeverity > 0:
				iPopulation = city.getPopulation()
				if iPopulation > 1:
					iChange = iPopulation // iSeverity
					city.changePopulation(-iChange)
					if iChange > 0:
						szTitle = localText.getText("TXT_KEY_GODS_EARTHQUAKE_CITY_TITLE", (szCityName, ))
						CyInterface().addMessage(plot.getOwner(), True, gc.getEVENT_MESSAGE_TIME(), szTitle, "AS2D_EARTHQUAKE", InterfaceMessageTypes.MESSAGE_TYPE_INFO, gc.getEffectInfo(iEarthquakeEffect).getButton(), gc.getInfoTypeForString("COLOR_RED"), plot.getX(), plot.getY(), True, True)	
				lBuilding = pyCity.getBuildingList()
				for iBuilding in lBuilding:
					if iBuilding != CvUtil.findInfoTypeNum(gc.getBuildingInfo, gc.getNumBuildingInfos(), "BUILDING_PALACE"):
						if self.getRandomNumber(8-iSeverity) == 0:
							PyCity( city.getOwner(), city.getID() ).setNumRealBuildingIdx(iBuilding, 0)
							szBuilding = gc.getBuildingInfo(iBuilding).getDescription()
							szTitle = localText.getText("TXT_KEY_GODS_EARTHQUAKE_BUILDING_TITLE", (szBuilding, szCityName, ))
							CyInterface().addImmediateMessage( szTitle , None)
		if plot.getImprovementType() != -1:
			if self.getRandomNumber(6-iSeverity) == 0:
				iCottage = CvUtil.findInfoTypeNum(gc.getImprovementInfo, gc.getNumImprovementInfos(), "IMPROVEMENT_COTTAGE")
				iHamlet = CvUtil.findInfoTypeNum(gc.getImprovementInfo, gc.getNumImprovementInfos(), "IMPROVEMENT_HAMLET")
				iVillage = CvUtil.findInfoTypeNum(gc.getImprovementInfo, gc.getNumImprovementInfos(), "IMPROVEMENT_VILLAGE")
				iTown = CvUtil.findInfoTypeNum(gc.getImprovementInfo, gc.getNumImprovementInfos(), "IMPROVEMENT_TOWN")				
				szCottage = gc.getImprovementInfo(iCottage).getDescription()
				szHamlet = gc.getImprovementInfo(iHamlet).getDescription()
				szVillage = gc.getImprovementInfo(iVillage).getDescription()
				szTown = gc.getImprovementInfo(iTown).getDescription()	
				cottageButton = gc.getImprovementInfo(iCottage).getButton()
				hamletButton = gc.getImprovementInfo(iHamlet).getButton()
				villageButton = gc.getImprovementInfo(iVillage).getButton()
				townButton = gc.getImprovementInfo(iTown).getButton()								
				if plot.getImprovementType() == iHamlet:
					plot.setImprovementType(iCottage)
					szTitle = localText.getText("TXT_KEY_GODS_EARTHQUAKE_TOWN_REDUCTION_TITLE", (szHamlet, szCottage, ))
					CyInterface().addMessage(plot.getOwner(), False, gc.getEVENT_MESSAGE_TIME(), szTitle, "AS2D_EARTHQUAKE", InterfaceMessageTypes.MESSAGE_TYPE_INFO, hamletButton, gc.getInfoTypeForString("COLOR_GREEN"), plot.getX(), plot.getY(), True, True)	
				elif plot.getImprovementType() == iVillage:
					plot.setImprovementType(iHamlet)
					szTitle = localText.getText("TXT_KEY_GODS_EARTHQUAKE_TOWN_REDUCTION_TITLE", (szVillage, szHamlet, ))
					CyInterface().addMessage(plot.getOwner(), False, gc.getEVENT_MESSAGE_TIME(), szTitle, "AS2D_EARTHQUAKE", InterfaceMessageTypes.MESSAGE_TYPE_INFO, villageButton, gc.getInfoTypeForString("COLOR_GREEN"), plot.getX(), plot.getY(), True, True)	
				elif plot.getImprovementType() == CvUtil.findInfoTypeNum(gc.getImprovementInfo, gc.getNumImprovementInfos(), "IMPROVEMENT_TOWN"):
					plot.setImprovementType(iVillage)
					szTitle = localText.getText("TXT_KEY_GODS_EARTHQUAKE_TOWN_REDUCTION_TITLE", (szTown, szVillage, ))
					CyInterface().addMessage(plot.getOwner(), False, gc.getEVENT_MESSAGE_TIME(), szTitle, "AS2D_EARTHQUAKE", InterfaceMessageTypes.MESSAGE_TYPE_INFO, townButton, gc.getInfoTypeForString("COLOR_GREEN"), plot.getX(), plot.getY(), True, True)	
				else:
					iImprovement = plot.getImprovementType()
					szTitle = localText.getText("TXT_KEY_GODS_EARTHQUAKE_IMP_DESTRUCTION_TITLE", (gc.getImprovementInfo(iImprovement).getDescription(), ))
					CyInterface().addMessage(plot.getOwner(), False, gc.getEVENT_MESSAGE_TIME(), szTitle, "AS2D_EARTHQUAKE", InterfaceMessageTypes.MESSAGE_TYPE_INFO, gc.getImprovementInfo(iImprovement).getButton(), gc.getInfoTypeForString("COLOR_GREEN"), plot.getX(), plot.getY(), True, True)	
					plot.setImprovementType(-1)

	def doEventMinorMeteorStrike(self, centerPlot):
		plotX = centerPlot.getX()
		plotY = centerPlot.getY()

		plotPoint = gc.getMap().plot( plotX, plotY ).getPoint( )
		iMeteorEffect = CvUtil.findInfoTypeNum( gc.getEffectInfo, gc.getNumEffectInfos( ), "EFFECT_GODS_METEOR" )
		CyEngine().triggerEffect( iMeteorEffect, plotPoint )

		if gc.getMap().plot(plotX, plotY).isCity():
			city = gc.getMap().plot(plotX, plotY).getPlotCity()
			iChange = city.getPopulation()//2
			city.changePopulation(-iChange)
			szCityName = city.getName()
			plot= city.plot()
			szTitle = localText.getText("TXT_KEY_GODS_MINOR_METEOR_STRIKE_CITY", ( szCityName, ))
			CyInterface().addMessage(plot.getOwner(), True, gc.getEVENT_MESSAGE_TIME(), szTitle, "AS2D_METEORSTRIKE", InterfaceMessageTypes.MESSAGE_TYPE_INFO, gc.getEffectInfo(iMeteorEffect).getButton(), gc.getInfoTypeForString("COLOR_RED"), plot.getX(), plot.getY(), True, True)	
			
			pyCity = PyCity(city.getOwner(), city.getID())
			lBuilding = pyCity.getBuildingList()
			for iBuilding in lBuilding:
				if iBuilding != CvUtil.findInfoTypeNum(gc.getBuildingInfo, gc.getNumBuildingInfos(), "BUILDING_PALACE"):
					if self.getRandomNumber(6) == 0:
						PyCity( city.getOwner(), city.getID() ).setNumRealBuildingIdx(iBuilding, 0)
						szBuilding = gc.getBuildingInfo(iBuilding).getDescription()
						szTitle = localText.getText("TXT_KEY_GODS_METEOR_BUILDING_TITLE", (szBuilding, szCityName, ))
						CyInterface().addImmediateMessage( szTitle , None)

		if gc.getMap().plot(plotX, plotY).getImprovementType() != -1:
			plot = gc.getMap().plot(plotX, plotY)
			iImprovement = plot.getImprovementType()
			szTitle = localText.getText("TXT_KEY_GODS_MINOR_METEOR_STRIKE_IMPROVEMENT", (gc.getImprovementInfo(iImprovement).getDescription(), ))
			CyInterface().addMessage(plot.getOwner(), False, gc.getEVENT_MESSAGE_TIME(), szTitle, "AS2D_METEORSTRIKE", InterfaceMessageTypes.MESSAGE_TYPE_INFO, gc.getImprovementInfo(iImprovement).getButton(), gc.getInfoTypeForString("COLOR_GREEN"), plot.getX(), plot.getY(), True, True)	
			gc.getMap().plot(plotX, plotY).setImprovementType(-1)			
		if gc.getMap().plot(plotX, plotY).isUnit():
			iUnits = gc.getMap().plot(plotX, plotY).getNumUnits()
			lUnitsToBeKilled = [ ]
			for i in range(iUnits):
				unit = gc.getMap().plot(plotX, plotY).getUnit(i)
				szUnitName = unit.getName()
				if self.getRandomNumber(3) == 0:
					plot = gc.getMap().plot(plotX, plotY)
					szTitle = localText.getText("TXT_KEY_GODS_MINOR_METEOR_STRIKE_UNIT", ( szUnitName, ))
					CyInterface().addMessage(plot.getOwner(), False, gc.getEVENT_MESSAGE_TIME(), szTitle, "AS2D_METEORSTRIKE", InterfaceMessageTypes.MESSAGE_TYPE_INFO, gc.getUnitInfo(unit.getUnitType()).getButton(), gc.getInfoTypeForString("COLOR_RED"), plot.getX(), plot.getY(), True, True)	
					lUnitsToBeKilled.append( unit )
			for unit in lUnitsToBeKilled:
				unit.kill( 0, unit.getOwner() )



	def doEventBlight( self, targetPlot ):
		plotX = targetPlot.getX()
		plotY = targetPlot.getY()
		iSeverity = 3

		plotPoint = gc.getMap().plot( plotX, plotY ).getPoint( )
		iBlightEffect = CvUtil.findInfoTypeNum( gc.getEffectInfo, gc.getNumEffectInfos( ), "EFFECT_GODS_BLIGHT" )
		CyEngine().triggerEffect( iBlightEffect, plotPoint )
		CyEngine().triggerEffect( iBlightEffect, plotPoint )

		
		for i in range(iSeverity):
			if i == 0:
				self.doBlightDevastation( plotX, plotY )
			else:
				self.doBlightDevastation( plotX - i, plotY )
				self.doBlightDevastation( plotX - i, plotY - i )
				self.doBlightDevastation( plotX, plotY - i )
				self.doBlightDevastation( plotX + i, plotY - i )
				self.doBlightDevastation( plotX + i, plotY )
				self.doBlightDevastation( plotX + i, plotY + i )
				self.doBlightDevastation( plotX, plotY + i )
				self.doBlightDevastation( plotX - i, plotY + i )

	def doBlightDevastation( self, plotX, plotY ):
		
	
		plot = gc.getMap().plot( plotX, plotY )
		#Turns ice into nothing.
		if plot.getTerrainType() == CvUtil.findInfoTypeNum(gc.getTerrainInfo, gc.getNumTerrainInfos(), "TERRAIN_OCEAN") or plot.getTerrainType() == CvUtil.findInfoTypeNum(gc.getTerrainInfo, gc.getNumTerrainInfos(), "TERRAIN_COAST"):
			if plot.getFeatureType() == CvUtil.findInfoTypeNum(gc.getFeatureInfo, gc.getNumFeatureInfos(), "FEATURE_ICE"):
				plot.setFeatureType(-1, 0)
		
		if plot.getTerrainType() == CvUtil.findInfoTypeNum(gc.getTerrainInfo, gc.getNumTerrainInfos(), "TERRAIN_PLAINS"):
			plot.setTerrainType(CvUtil.findInfoTypeNum(gc.getTerrainInfo, gc.getNumTerrainInfos(), "TERRAIN_DESERT"), 1, 1)
			if plot.getBonusType(-1) == CvUtil.findInfoTypeNum(gc.getBonusInfo, gc.getNumBonusInfos(), "BONUS_RICE"):
				self.doBlightBonus( plot )
			if plot.getBonusType(-1) == CvUtil.findInfoTypeNum(gc.getBonusInfo, gc.getNumBonusInfos(), "BONUS_WHEAT"):
				self.doBlightBonus( plot )				
			if plot.getBonusType(-1) == CvUtil.findInfoTypeNum(gc.getBonusInfo, gc.getNumBonusInfos(), "BONUS_WINE"):
				self.doBlightBonus( plot )				
			if plot.getBonusType(-1) == CvUtil.findInfoTypeNum(gc.getBonusInfo, gc.getNumBonusInfos(), "BONUS_SUGAR"):
				self.doBlightBonus( plot )
			if plot.getBonusType(-1) == CvUtil.findInfoTypeNum(gc.getBonusInfo, gc.getNumBonusInfos(), "BONUS_HORSE"):
				self.doBlightBonus( plot )			
			if plot.getBonusType(-1) == CvUtil.findInfoTypeNum(gc.getBonusInfo, gc.getNumBonusInfos(), "BONUS_CORN"):
				self.doBlightBonus( plot )			
			if plot.getBonusType(-1) == CvUtil.findInfoTypeNum(gc.getBonusInfo, gc.getNumBonusInfos(), "BONUS_COW"):
				self.doBlightBonus( plot )				
			if plot.getBonusType(-1) == CvUtil.findInfoTypeNum(gc.getBonusInfo, gc.getNumBonusInfos(), "BONUS_DEER"):
				self.doBlightBonus( plot )	
			if plot.getBonusType(-1) == CvUtil.findInfoTypeNum(gc.getBonusInfo, gc.getNumBonusInfos(), "BONUS_PIG"):
				self.doBlightBonus( plot )			
			if plot.getBonusType(-1) == CvUtil.findInfoTypeNum(gc.getBonusInfo, gc.getNumBonusInfos(), "BONUS_SHEEP"):
				self.doBlightBonus( plot )	
			if plot.getBonusType(-1) == CvUtil.findInfoTypeNum(gc.getBonusInfo, gc.getNumBonusInfos(), "BONUS_FUR"):
				self.doBlightBonus( plot )			
			if plot.getFeatureType() == CvUtil.findInfoTypeNum(gc.getFeatureInfo, gc.getNumFeatureInfos(), "FEATURE_FOREST"):
				self.doBlightFeature( plot )
			if plot.getFeatureType() == CvUtil.findInfoTypeNum(gc.getFeatureInfo, gc.getNumFeatureInfos(), "FEATURE_JUNGLE"):
				self.doBlightFeature( plot )

		if plot.getTerrainType() == CvUtil.findInfoTypeNum(gc.getTerrainInfo, gc.getNumTerrainInfos(), "TERRAIN_GRASS"):
			plot.setTerrainType(CvUtil.findInfoTypeNum(gc.getTerrainInfo, gc.getNumTerrainInfos(), "TERRAIN_PLAINS"), 1, 1)	
			if plot.getBonusType(-1) == CvUtil.findInfoTypeNum(gc.getBonusInfo, gc.getNumBonusInfos(), "BONUS_RICE"):
				self.doBlightBonus( plot )				
			if plot.getBonusType(-1) == CvUtil.findInfoTypeNum(gc.getBonusInfo, gc.getNumBonusInfos(), "BONUS_SUGAR"):
				self.doBlightBonus( plot )	
			if plot.getBonusType(-1) == CvUtil.findInfoTypeNum(gc.getBonusInfo, gc.getNumBonusInfos(), "BONUS_DEER"):
				self.doBlightBonus( plot )
			if plot.getBonusType(-1) == CvUtil.findInfoTypeNum(gc.getBonusInfo, gc.getNumBonusInfos(), "BONUS_FUR"):
				self.doBlightBonus( plot )
		
		if plot.getTerrainType() == CvUtil.findInfoTypeNum(gc.getTerrainInfo, gc.getNumTerrainInfos(), "TERRAIN_TUNDRA"):
			plot.setTerrainType(CvUtil.findInfoTypeNum(gc.getTerrainInfo, gc.getNumTerrainInfos(), "TERRAIN_GRASS"), 1, 1)
		
		if plot.getTerrainType() == CvUtil.findInfoTypeNum(gc.getTerrainInfo, gc.getNumTerrainInfos(), "TERRAIN_SNOW"):
			plot.setTerrainType(CvUtil.findInfoTypeNum(gc.getTerrainInfo, gc.getNumTerrainInfos(), "TERRAIN_TUNDRA"), 1, 1)

	def doBlightBonus( self, plot ):
		iBonus = plot.getBonusType(-1)
		szTitle = localText.getText("TXT_KEY_GODS_BLIGHT_BONUS", (gc.getBonusInfo(iBonus).getDescription(), ))
		CyInterface().addMessage(plot.getOwner(), False, gc.getEVENT_MESSAGE_TIME(), szTitle, "AS2D_BLIGHT", InterfaceMessageTypes.MESSAGE_TYPE_INFO, gc.getBonusInfo(iBonus).getButton(), gc.getInfoTypeForString("COLOR_GREEN"), plot.getX(), plot.getY(), True, True)	
		plot.setBonusType(-1)

	def doBlightFeature( self, plot ):
		iFeature = plot.getFeatureType()
		szTitle = localText.getText("TXT_KEY_GODS_BLIGHT_FEATURE", (gc.getFeatureInfo(iFeature).getDescription(), ))
		CyInterface().addMessage(plot.getOwner(), False, gc.getEVENT_MESSAGE_TIME(), szTitle, "AS2D_BLIGHT", InterfaceMessageTypes.MESSAGE_TYPE_INFO, gc.getFeatureInfo(iFeature).getButton(), gc.getInfoTypeForString("COLOR_GREEN"), plot.getX(), plot.getY(), True, True)	
		plot.setFeatureType(-1, 0)		

	def doEventTsunami( self, targetPlot ):
		iSeverity = 5
		plotX = targetPlot.getX()
		plotY = targetPlot.getY()
		self.lTsunamiCoor = [ ]

		for i in range(iSeverity):
			if i == 0:
				self.doTsunamiDevastation(plotX, plotY, iSeverity)
			else:
				if gc.getMap( ).plot( plotX - i, plotY ).isCoastalLand( ):
					self.doTsunamiDevastation(plotX - i, plotY, iSeverity-i)
				if gc.getMap( ).plot( plotX - i, plotY - i ).isCoastalLand( ):
					self.doTsunamiDevastation(plotX - i, plotY - i, iSeverity-i)
				if gc.getMap( ).plot( plotX, plotY - i ).isCoastalLand( ):
					self.doTsunamiDevastation(plotX, plotY - i, iSeverity-i)
				if gc.getMap( ).plot( plotX + i, plotY - i ).isCoastalLand( ):
					self.doTsunamiDevastation(plotX + i, plotY - i, iSeverity-i)
				if gc.getMap( ).plot( plotX + i, plotY ).isCoastalLand( ):
					self.doTsunamiDevastation(plotX + i, plotY, iSeverity-i)
				if gc.getMap( ).plot( plotX + i, plotY + i ).isCoastalLand( ):
					self.doTsunamiDevastation(plotX + i, plotY + i, iSeverity-i)
				if gc.getMap( ).plot( plotX, plotY + i ).isCoastalLand( ):
					self.doTsunamiDevastation(plotX, plotY + i, iSeverity-i)
				if gc.getMap( ).plot( plotX - i, plotY + i ).isCoastalLand( ):
					self.doTsunamiDevastation(plotX - i, plotY + i, iSeverity-i)		

	def doTsunamiDevastation( self, iX, iY, iSeverity ):
		plot = gc.getMap().plot(iX, iY)
		
		self.doTsunamiAnimation( iX, iY )

		plotPoint = plot.getPoint()
		iTsunamiEffect = CvUtil.findInfoTypeNum( gc.getEffectInfo, gc.getNumEffectInfos( ), "EFFECT_GODS_TSUNAMI" )
		CyEngine().triggerEffect( iTsunamiEffect, plotPoint )
			
		if plot.isCity():
			city = plot.getPlotCity()
			szCityName = city.getName()
			pyCity = PyCity(city.getOwner(), city.getID())
			if iSeverity > 0:
				iPopulation = city.getPopulation()
				iChange = iPopulation // iSeverity
				city.changePopulation(-iChange)
				if iChange > 0:
					szTitle = localText.getText("TXT_KEY_GODS_TSUNAMI_CITY_TITLE", (szCityName, ))
					CyInterface().addMessage(plot.getOwner(), True, gc.getEVENT_MESSAGE_TIME(), szTitle, "AS2D_TSUNAMI", InterfaceMessageTypes.MESSAGE_TYPE_INFO, gc.getEffectInfo(iTsunamiEffect).getButton(), gc.getInfoTypeForString("COLOR_RED"), plot.getX(), plot.getY(), True, True)	
				lBuilding = pyCity.getBuildingList()
				for iBuilding in lBuilding:
					if iBuilding != CvUtil.findInfoTypeNum(gc.getBuildingInfo, gc.getNumBuildingInfos(), "BUILDING_PALACE"):
						if self.getRandomNumber(8-iSeverity) == 0:
							PyCity( city.getOwner(), city.getID() ).setNumRealBuildingIdx(iBuilding, 0)
							szBuilding = gc.getBuildingInfo(iBuilding).getDescription()
							szTitle = localText.getText("TXT_KEY_GODS_TSUNAMI_BUILDING_TITLE", (szBuilding, szCityName, ))
							CyInterface().addImmediateMessage( szTitle , None)
		if plot.getImprovementType() != -1:
			if self.getRandomNumber(6-iSeverity) == 0:
				iCottage = CvUtil.findInfoTypeNum(gc.getImprovementInfo, gc.getNumImprovementInfos(), "IMPROVEMENT_COTTAGE")
				iHamlet = CvUtil.findInfoTypeNum(gc.getImprovementInfo, gc.getNumImprovementInfos(), "IMPROVEMENT_HAMLET")
				iVillage = CvUtil.findInfoTypeNum(gc.getImprovementInfo, gc.getNumImprovementInfos(), "IMPROVEMENT_VILLAGE")
				iTown = CvUtil.findInfoTypeNum(gc.getImprovementInfo, gc.getNumImprovementInfos(), "IMPROVEMENT_TOWN")				
				szCottage = gc.getImprovementInfo(iCottage).getDescription()
				szHamlet = gc.getImprovementInfo(iHamlet).getDescription()
				szVillage = gc.getImprovementInfo(iVillage).getDescription()
				szTown = gc.getImprovementInfo(iTown).getDescription()	
				cottageButton = gc.getImprovementInfo(iCottage).getButton()
				hamletButton = gc.getImprovementInfo(iHamlet).getButton()
				villageButton = gc.getImprovementInfo(iVillage).getButton()
				townButton = gc.getImprovementInfo(iTown).getButton()								
				if plot.getImprovementType() == iHamlet:
					plot.setImprovementType(iCottage)
					szTitle = localText.getText("TXT_KEY_GODS_TSUNAMI_TOWN_REDUCTION_TITLE", (szHamlet, szCottage, ))
					CyInterface().addMessage(plot.getOwner(), False, gc.getEVENT_MESSAGE_TIME(), szTitle, "AS2D_TSUNAMI", InterfaceMessageTypes.MESSAGE_TYPE_INFO, hamletButton, gc.getInfoTypeForString("COLOR_GREEN"), plot.getX(), plot.getY(), True, True)	
				elif plot.getImprovementType() == iVillage:
					plot.setImprovementType(iHamlet)
					szTitle = localText.getText("TXT_KEY_GODS_TSUNAMI_TOWN_REDUCTION_TITLE", (szVillage, szHamlet, ))
					CyInterface().addMessage(plot.getOwner(), False, gc.getEVENT_MESSAGE_TIME(), szTitle, "AS2D_TSUNAMI", InterfaceMessageTypes.MESSAGE_TYPE_INFO, villageButton, gc.getInfoTypeForString("COLOR_GREEN"), plot.getX(), plot.getY(), True, True)	
				elif plot.getImprovementType() == CvUtil.findInfoTypeNum(gc.getImprovementInfo, gc.getNumImprovementInfos(), "IMPROVEMENT_TOWN"):
					plot.setImprovementType(iVillage)
					szTitle = localText.getText("TXT_KEY_GODS_TSUNAMI_TOWN_REDUCTION_TITLE", (szTown, szVillage, ))
					CyInterface().addMessage(plot.getOwner(), False, gc.getEVENT_MESSAGE_TIME(), szTitle, "AS2D_TSUNAMI", InterfaceMessageTypes.MESSAGE_TYPE_INFO, townButton, gc.getInfoTypeForString("COLOR_GREEN"), plot.getX(), plot.getY(), True, True)	
				else:
					iImprovement = plot.getImprovementType()
					szTitle = localText.getText("TXT_KEY_GODS_TSUNAMI_IMP_DESTRUCTION_TITLE", (gc.getImprovementInfo(iImprovement).getDescription(), ))
					CyInterface().addMessage(plot.getOwner(), False, gc.getEVENT_MESSAGE_TIME(), szTitle, "AS2D_TSUNAMI", InterfaceMessageTypes.MESSAGE_TYPE_INFO, gc.getImprovementInfo(iImprovement).getButton(), gc.getInfoTypeForString("COLOR_GREEN"), plot.getX(), plot.getY(), True, True)	
					plot.setImprovementType(-1)

	def	doTsunamiAnimation( self, iX, iY ):
		
		iTsunamiMovingEastEffect = CvUtil.findInfoTypeNum( gc.getEffectInfo, gc.getNumEffectInfos( ), "EFFECT_GODS_TSUNAMI_WAVE_WEST_OF_LAND" )
		iTsunamiMovingWestEffect = CvUtil.findInfoTypeNum( gc.getEffectInfo, gc.getNumEffectInfos( ), "EFFECT_GODS_TSUNAMI_WAVE_EAST_OF_LAND" )
		iTsunamiMovingSouthEffect = CvUtil.findInfoTypeNum( gc.getEffectInfo, gc.getNumEffectInfos( ), "EFFECT_GODS_TSUNAMI_WAVE_NORTH_OF_LAND" )
		iTsunamiMovingNorthEffect = CvUtil.findInfoTypeNum( gc.getEffectInfo, gc.getNumEffectInfos( ), "EFFECT_GODS_TSUNAMI_WAVE_SOUTH_OF_LAND" )
		
		pEastPlot = gc.getMap( ).plot( iX + 1, iY )
		pWestPlot = gc.getMap( ).plot( iX - 1, iY )
		pNorthPlot = gc.getMap( ).plot( iX, iY + 1 )
		pSouthPlot = gc.getMap( ).plot( iX, iY - 1 )
		
		if pEastPlot.isWater( ):
			if self.lTsunamiCoor.count( (iX + 1, iY) ) == 0:
				plotPoint = pEastPlot.getPoint( )
				CyEngine().triggerEffect( iTsunamiMovingWestEffect, plotPoint )
				self.lTsunamiCoor.append( (iX + 1, iY) )
		if pWestPlot.isWater( ):
			if self.lTsunamiCoor.count( (iX - 1, iY) ) == 0:
				plotPoint = pWestPlot.getPoint( )
				CyEngine().triggerEffect( iTsunamiMovingEastEffect, plotPoint )
				self.lTsunamiCoor.append( (iX - 1, iY) )
		if pNorthPlot.isWater( ):
			if self.lTsunamiCoor.count( (iX, iY + 1) ) == 0:
				plotPoint = pNorthPlot.getPoint( )
				CyEngine().triggerEffect( iTsunamiMovingSouthEffect, plotPoint )
				self.lTsunamiCoor.append( (iX, iY + 1) )
		if pSouthPlot.isWater( ):
			if self.lTsunamiCoor.count( (iX, iY - 1) ) == 0:
				plotPoint = pSouthPlot.getPoint( )
				CyEngine().triggerEffect( iTsunamiMovingNorthEffect, plotPoint )
				self.lTsunamiCoor.append( (iX + 1, iY - 1) )

	def doEventPlague( self, targetPlot ):
		plotX = targetPlot.getX()
		plotY = targetPlot.getY()
		city = gc.getMap( ).plot( plotX, plotY ).getPlotCity()
		szCityName = city.getName()		
		iPlagueEffect = CvUtil.findInfoTypeNum( gc.getEffectInfo, gc.getNumEffectInfos( ), "EFFECT_GODS_PLAGUE" )
		iCoords = ( plotX, plotY )

		self.lPlagueCities.append( iCoords )
		self.doPlagueEffect( city )
		plot = city.plot()
		szTitle = localText.getText("TXT_KEY_GODS_PLAGUE_START", ( szCityName, ))
		CyInterface().addMessage(plot.getOwner(), True, gc.getEVENT_MESSAGE_TIME(), szTitle, "AS2D_PLAGUE", InterfaceMessageTypes.MESSAGE_TYPE_INFO, gc.getEffectInfo(iPlagueEffect).getButton(), gc.getInfoTypeForString("COLOR_RED"), plot.getX(), plot.getY(), True, True)	
		#plot 5 is Plague
		gc.getMap().plotByIndex(0).setScriptData("Plague On")
		#plot 6 is Black Death Counter
		gc.getMap().plotByIndex(1).setScriptData("10")
		
	def doPlagueSpread(self):
		iPlagueEffect = CvUtil.findInfoTypeNum( gc.getEffectInfo, gc.getNumEffectInfos( ), "EFFECT_GODS_PLAGUE" )

		#counts down turns remaining of plague
		if gc.getMap().plotByIndex(1).getScriptData() == "10":
			gc.getMap().plotByIndex(1).setScriptData("9")
		elif gc.getMap().plotByIndex(1).getScriptData() == "9":
			gc.getMap().plotByIndex(1).setScriptData("8")			
		elif gc.getMap().plotByIndex(1).getScriptData() == "8":
			gc.getMap().plotByIndex(1).setScriptData("7")
		elif gc.getMap().plotByIndex(1).getScriptData() == "7":
			gc.getMap().plotByIndex(1).setScriptData("6")
		elif gc.getMap().plotByIndex(1).getScriptData() == "6":
			gc.getMap().plotByIndex(1).setScriptData("5")
		elif gc.getMap().plotByIndex(1).getScriptData() == "5":
			gc.getMap().plotByIndex(1).setScriptData("4")
		elif gc.getMap().plotByIndex(1).getScriptData() == "4":
			gc.getMap().plotByIndex(1).setScriptData("3")
		elif gc.getMap().plotByIndex(1).getScriptData() == "3":
			gc.getMap().plotByIndex(1).setScriptData("2")
		elif gc.getMap().plotByIndex(1).getScriptData() == "2":
			gc.getMap().plotByIndex(1).setScriptData("1")
		else:
			gc.getMap().plotByIndex(0).setScriptData("")
		
		lPlayers = PyGame().getCivPlayerList()
		lValidCities = []
		
			
		for iCoords in self.lPlagueCities:
			city = gc.getMap( ).plot( iCoords[0], iCoords[1] ).getPlotCity( )
			iTradeRoutes = city.getTradeRoutes()
			for i in range(iTradeRoutes):
				tradeCity = city.getTradeCity(i)
				distance = self.doGetDistanceBetweenPlots( city.getX(), city.getY(), tradeCity.getX(), tradeCity.getY() )
				iTradeCityCoords = ( tradeCity.getX( ), tradeCity.getY( ) )
				if self.lPlagueCities.count( iTradeCityCoords ) == 0:
#				if tradeCity.getScriptData() != "Plague City":
					if distance < 10:
						if self.getRandomNumber(5) == 0:
							self.lPlagueCities.append( iTradeCityCoords )
#							tradeCity.setScriptData("Plague City")
							self.doPlagueEffect(tradeCity)
							plot = tradeCity.plot()
							szCityName = tradeCity.getName()
							szTitle = localText.getText("TXT_KEY_GODS_PLAGUE_SPREAD", ( szCityName, ))
							CyInterface().addMessage(plot.getOwner(), True, gc.getEVENT_MESSAGE_TIME(), szTitle, "AS2D_PLAGUE", InterfaceMessageTypes.MESSAGE_TYPE_INFO, gc.getEffectInfo(iPlagueEffect).getButton(), gc.getInfoTypeForString("COLOR_RED"), plot.getX(), plot.getY(), True, True)	

	def doPlagueDecay(self):
		lPlayers = PyGame().getCivPlayerList()
		lValidCities = []
		iPlagueEffect = CvUtil.findInfoTypeNum( gc.getEffectInfo, gc.getNumEffectInfos( ), "EFFECT_GODS_PLAGUE" )

		
#		for player in lPlayers:
#			lCities = player.getCityList()
#			for city in lCities:
#				if city.getScriptData() == "Plague City":
#					lValidCities.append(city)
		
		for iCoords in self.lPlagueCities:
			city = gc.getMap( ).plot( iCoords[0], iCoords[1] ).getPlotCity( )
			if self.getRandomNumber(1) == 0:
				self.doPlagueRemoveEffect( city )
				self.lPlagueCities.remove( iCoords )
#				city.setScriptData("")
				szCityName = city.getName()
				plot = city.plot()
				szTitle = localText.getText("TXT_KEY_GODS_PLAGUE_DECAY", ( szCityName, ))
				CyInterface().addMessage(plot.getOwner(), True, gc.getEVENT_MESSAGE_TIME(), szTitle, "AS2D_DISCOVERBONUS", InterfaceMessageTypes.MESSAGE_TYPE_INFO, gc.getEffectInfo(iPlagueEffect).getButton(), gc.getInfoTypeForString("COLOR_RED"), plot.getX(), plot.getY(), True, True)	


	def doPlagueEffect(self, city):
		gc.getPlayer(city.getOwner()).getCity(city.getID()).changeExtraHealth(-8)

	def doPlagueRemoveEffect(self, city):
		gc.getPlayer(city.getOwner()).getCity(city.getID()).changeExtraHealth(8)
		
	def getRandomNumber(self, int):
		return CyGame().getSorenRandNum(int, "Gods")

	def doGetDistanceBetweenPlots ( self, iX1, iY1, iX2, iY2):
		return abs(iX1 - iX2) + abs(iY1 - iY2)

	def doAIOperations( self, iPlayer ):
		lPlayers = PyGame().getCivPlayerList( )
		player = gc.getPlayer( iPlayer )
		lUnits = PyPlayer( iPlayer ).getUnitList( )
		playerStateReligion = gc.getPlayer( iPlayer ).getStateReligion( )
		
		for unit in lUnits:
			if unit.getUnitType( ) == CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), "UNIT_PROPHET"):
				if playerStateReligion == CvUtil.findInfoTypeNum(gc.getReligionInfo, gc.getNumReligionInfos(), "RELIGION_KI"):
					for iOpponent in lPlayers:
						if iOpponent.getID() != iPlayer:
							iAttitude = player.AI_getAttitude( iOpponent.getID() )
							if iAttitude == AttitudeTypes.ATTITUDE_ANNOYED:
								if self.getRandomNumber( 15 ) == 0:
									self.doAITargetOpponentEarthquake( iOpponent.getID(), iPlayer )
									unit.kill( 0, unit.getOwner())
							if iAttitude == AttitudeTypes.ATTITUDE_FURIOUS:
								if self.getRandomNumber( 5 ) == 0:
									unit.kill( 0, unit.getOwner())
									self.doAITargetOpponentEarthquake( iOpponent.getID(), iPlayer )
				if playerStateReligion == CvUtil.findInfoTypeNum(gc.getReligionInfo, gc.getNumReligionInfos(), "RELIGION_ENKI"):
					for iOpponent in lPlayers:
						if iOpponent.getID() != iPlayer:
							iAttitude = player.AI_getAttitude( iOpponent.getID() )
							if iAttitude == AttitudeTypes.ATTITUDE_ANNOYED:
								if self.getRandomNumber( 15 ) == 0:
									self.doAITargetOpponentTsunami( iOpponent.getID(), unit, iPlayer )
							if iAttitude == AttitudeTypes.ATTITUDE_FURIOUS:
								if self.getRandomNumber( 5 ) == 0:
									self.doAITargetOpponentTsunami( iOpponent.getID(), unit, iPlayer )
				if playerStateReligion == CvUtil.findInfoTypeNum(gc.getReligionInfo, gc.getNumReligionInfos(), "RELIGION_ENLIL"):
					for iOpponent in lPlayers:
						if iOpponent.getID() != iPlayer:
							iAttitude = player.AI_getAttitude( iOpponent.getID() )
							if iAttitude == AttitudeTypes.ATTITUDE_ANNOYED:
								if self.getRandomNumber( 15 ) == 0:
									self.doAITargetOpponentPlague( iOpponent.getID(), iPlayer )
									unit.kill( 0, unit.getOwner())
							if iAttitude == AttitudeTypes.ATTITUDE_FURIOUS:
								if self.getRandomNumber( 5 ) == 0:
									unit.kill( 0, unit.getOwner())
									self.doAITargetOpponentPlague( iOpponent.getID(), iPlayer )
				if playerStateReligion == CvUtil.findInfoTypeNum(gc.getReligionInfo, gc.getNumReligionInfos(), "RELIGION_NANNA"):
					for iOpponent in lPlayers:
						if iOpponent.getID() != iPlayer:
							iAttitude = player.AI_getAttitude( iOpponent.getID() )
							if iAttitude == AttitudeTypes.ATTITUDE_ANNOYED:
								if self.getRandomNumber( 15 ) == 0:
									self.doAITargetOpponentMeteor( iOpponent.getID(), iPlayer )
									unit.kill( 0, unit.getOwner())
							if iAttitude == AttitudeTypes.ATTITUDE_FURIOUS:
								if self.getRandomNumber( 5 ) == 0:
									unit.kill( 0, unit.getOwner())
									self.doAITargetOpponentMeteor( iOpponent.getID(), iPlayer )									
				if playerStateReligion == CvUtil.findInfoTypeNum(gc.getReligionInfo, gc.getNumReligionInfos(), "RELIGION_UTU"):
					for iOpponent in lPlayers:
						if iOpponent.getID() != iPlayer:
							iAttitude = player.AI_getAttitude( iOpponent.getID() )
							if iAttitude == AttitudeTypes.ATTITUDE_ANNOYED:
								if self.getRandomNumber( 15 ) == 0:
									self.doAITargetOpponentBlight( iOpponent.getID(), iPlayer )
									unit.kill( 0, unit.getOwner())
							if iAttitude == AttitudeTypes.ATTITUDE_FURIOUS:
								if self.getRandomNumber( 5 ) == 0:
									unit.kill( 0, unit.getOwner())
									self.doAITargetOpponentBlight( iOpponent.getID(), iPlayer )	
		
	def doAITargetOpponentEarthquake( self, iOpponent, iPlayer ):
		lCities = PyPlayer( iOpponent ).getCityList()
		numCities = len( lCities )
		pCity = lCities[ self.getRandomNumber( numCities ) ]
		
		if not self.doAnReligionCheck( iOpponent, iPlayer ):
			self.doEventEarthquake( pCity.plot() )
		
	def doAITargetOpponentPlague( self, iOpponent, iPlayer ):
		lCities = PyPlayer( iOpponent ).getCityList()
		numCities = len( lCities )
		pCity = lCities[ self.getRandomNumber( numCities ) ]
		if not self.doAnReligionCheck( iOpponent, iPlayer ):
			self.doEventPlague( pCity.plot() )
	
	def doAITargetOpponentMeteor( self, iOpponent, iPlayer ):
		lCities = PyPlayer( iOpponent ).getCityList()
		numCities = len( lCities )
		pCity = lCities[ self.getRandomNumber( numCities ) ]

		if not self.doAnReligionCheck( iOpponent, iPlayer ):
			self.doEventMinorMeteorStrike( pCity.plot() )
		
	def doAITargetOpponentBlight( self, iOpponent, iPlayer ):
		lCities = PyPlayer( iOpponent ).getCityList()
		numCities = len( lCities )
		pCity = lCities[ self.getRandomNumber( numCities ) ]

		if not self.doAnReligionCheck( iOpponent, iPlayer ):
			self.doEventBlight( pCity.plot() )
		
	def doAITargetOpponentTsunami( self, iOpponent, unit, iPlayer ):
		lAllCities = PyPlayer( iOpponent ).getCityList()
		lValidCities = [ ]
		
		for pCity in lAllCities:
			if pCity.plot().isCoastalLand():
				lValidCities.append( pCity )
		if len( lValidCities ) > 0:
			numCities = len( lValidCities )
			pChosenCity = lValidCities[ self.getRandomNumber( numCities ) ]
			if not self.doAnReligionCheck( iOpponent, iPlayer ):
				self.doEventTsunami( pChosenCity.plot() )
			unit.kill( 0, unit.getOwner( ) )

	def doAnReligionCheck( self, iOpponent, iPlayer ):
		pyTargetPlayer = PyPlayer( iOpponent )
		pDefendingPlayer = gc.getPlayer( iOpponent )
		pAttackingPlayer = gc.getPlayer( iPlayer )
		
		if pyTargetPlayer.getStateReligion( ) == CvUtil.findInfoTypeNum(gc.getReligionInfo, gc.getNumReligionInfos(), "RELIGION_AN"):
			lUnits = pyTargetPlayer.getUnitList()
			for unit in lUnits:
				if unit.getUnitType() == CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), "UNIT_PROPHET"):
					unit.kill( 0, unit.getOwner( ) )

					if not ( pDefendingPlayer.isHuman( ) ):
						pDefendingPlayer.AI_changeAttitudeExtra( iPlayer, -5 )
						szAttackedCiv = pDefendingPlayer.getCivilizationDescriptionKey()
						szAttackingCiv = pAttackingPlayer.getCivilizationDescriptionKey()
						szTitle = localText.getText("TXT_KEY_GODS_DISASTER_ANGER_BLOCKED", (szAttackedCiv , szAttackingCiv, ))
						CyInterface().addImmediateMessage( szTitle , None)			
					else:
						szAttackedCiv = pDefendingPlayer.getCivilizationDescriptionKey()
						szAttackingCiv = pAttackingPlayer.getCivilizationDescriptionKey()
						szTitle = localText.getText("TXT_KEY_GODS_DISASTER_HUMAN_BLOCKED", (szAttackedCiv , szAttackingCiv, ))
						CyInterface().addImmediateMessage( szTitle , None)	
					return 1
		return 0
	
	def doReligiousVictoryCheck( self ):
		lHolyCities = [ ]
		
		for i in range( 7 ):
			if not gc.getGame( ).getHolyCity( i ).isNone():
				lHolyCities.append( gc.getGame( ).getHolyCity( i ) )
		
		if len ( lHolyCities ) == 1:
			gc.getGame().setWinner( lHolyCities[0].getOwner( ), CvUtil.findInfoTypeNum(gc.getHandicapInfo,gc.getNumHandicapInfos(),"VICTORY_RELIGIOUS"))

	def doReligiousVictoryPossible( self ):
		lHolyCities = [ ]
		
		for i in range( 7 ):
			if not gc.getGame( ).getHolyCity( i ).isNone():
				lHolyCities.append( gc.getGame( ).getHolyCity( i ) )
		
		iNumHolyCities = len ( lHolyCities )
		
		if iNumHolyCities > 1:
			for i in range( iNumHolyCities - 1 ):
				if lHolyCities[0].getOwner( ) != lHolyCities[ i + 1 ].getOwner( ):
					self.iReligiousVictoryPossible = 1
					return
		

	def clearGodsVariables( self ):
		
		self.iReligiousVictoryPossible = 0
		self.iStarAlignment = 0
		self.lPlagueCities = [ ]
		self.lTsunamiCoor = [ ]


	def setGodsVariables(self):
		pPlayer = gc.getPlayer(0)
		
		szScriptData = []

		szScriptData.append(self.iReligiousVictoryPossible)
		szScriptData.append(self.iStarAlignment)
		szScriptData.append( self.lPlagueCities )	
		
		print szScriptData

		# Save Script Data - Score
		pPlayer.setScriptData(pickle.dumps(szScriptData))	
		
	def getGodsVariables(self):
		
		pPlayer = gc.getPlayer(0)
		lPlagueCityCoord = [ ]
		
		# Load Script Data - Score
		szScriptData = pickle.loads(pPlayer.getScriptData())
		
		self.iReligiousVictoryPossible = szScriptData[0]
		self.iStarAlignment = szScriptData[1]
		self.lPlagueCities = szScriptData[2]
		
		return 


	def doInquisitorPersecution( self, pCity, pUnit ):
		pPlayer = gc.getPlayer( pCity.getOwner( ) )
		
		#gets a list of all religions in the city except state religion
		lCityReligions = [ ]
		for iReligionLoop in range(gc.getNumReligionInfos( )):
			if pCity.isHasReligion( iReligionLoop ):
				if pPlayer.getStateReligion( ) != iReligionLoop:
					lCityReligions.append( iReligionLoop )
			
		# increases Anger for all AIs in City Religion List
		if len( lCityReligions ) > 0:
			lPlayers =PyGame().getCivPlayerList()
			for iAI_PlayersLoop in range( len(lPlayers) ):
				pSecondPlayer = lPlayers[iAI_PlayersLoop]
				for iAIAngerLoop in range( len( lCityReligions ) ):
					if pSecondPlayer.getStateReligion( ) == lCityReligions[iAIAngerLoop]:
						pSecondPlayer.AI_changeAttitude( pPlayer.getID( ), -1 )

		# Loop through all religions, remove them from the city
		for iReligionLoop in range(gc.getNumReligionInfos()):
			if iReligionLoop != pPlayer.getStateReligion( ):
				if pCity.isHolyCityByType( iReligionLoop ):
					gc.getGame( ).clearHolyCity( iReligionLoop )
			pCity.setHasReligion(iReligionLoop, 0, 0, 0)
			
		# Add player's state religion
		if ( gc.getPlayer( pUnit.getOwner( ) ).getStateReligion( ) != -1 ):
			iStateReligion = gc.getPlayer( pUnit.getOwner( ) ).getStateReligion( )
			pCity.setHasReligion( iStateReligion, 1, 0, 0 )
			
		# Unit expended
		pUnit.kill( 0, -1 )
	
	def doChooseNewStarAlignment( self ):
		
		self.iStarAlignment = self.getRandomNumber( 9 )
		if self.iStarAlignment == 0:
			szTitle = localText.getText( "TXT_KEY_GODS_STARS_NONE", ( ) )
			CyInterface().addImmediateMessage( szTitle , None)
		if self.iStarAlignment == 1:
			szTitle = localText.getText( "TXT_KEY_GODS_STARS_UTU_PRODUCTION", ( ) )
			CyInterface().addImmediateMessage( szTitle , None)
			self.doReligiousProductionBonus( "RELIGION_UTU" )
		if self.iStarAlignment == 2:
			szTitle = localText.getText( "TXT_KEY_GODS_STARS_NANNA_PRODUCTION", ( ) )
			CyInterface().addImmediateMessage( szTitle , None)
			self.doReligiousProductionBonus( "RELIGION_NANNA" )
		if self.iStarAlignment == 3:
			szTitle = localText.getText( "TXT_KEY_GODS_STARS_UTU_WEALTH", ( ) )
			CyInterface().addImmediateMessage( szTitle , None)
			self.doReligiousGoldBonus( "RELIGION_UTU" )		
		if self.iStarAlignment == 4:
			szTitle = localText.getText( "TXT_KEY_GODS_STARS_NANNA_WEALTH", ( ) )
			CyInterface().addImmediateMessage( szTitle , None)
			self.doReligiousGoldBonus( "RELIGION_NANNA" )
		if self.iStarAlignment == 5:
			szTitle = localText.getText( "TXT_KEY_GODS_STARS_UTU_GROWTH", ( ) )
			CyInterface().addImmediateMessage( szTitle , None)
			self.doReligiousHealthBonus( "RELIGION_UTU" )
		if self.iStarAlignment == 6:
			szTitle = localText.getText( "TXT_KEY_GODS_STARS_NANNA_GROWTH", ( ) )
			CyInterface().addImmediateMessage( szTitle , None)	
			self.doReligiousHealthBonus( "RELIGION_NANNA" )	
		if self.iStarAlignment == 7:
			szTitle = localText.getText( "TXT_KEY_GODS_STARS_UTU_CULTURE", ( ) )
			CyInterface().addImmediateMessage( szTitle , None)
			self.doReligiousCultureBonus( "RELIGION_UTU" )		
		if self.iStarAlignment == 8:
			szTitle = localText.getText( "TXT_KEY_GODS_STARS_NANNA_CULTURE", ( ) )
			CyInterface().addImmediateMessage( szTitle , None)
			self.doReligiousCultureBonus( "RELIGION_NANNA" )	
			
	def doReligiousProductionBonus( self, szReligion ):
		lPlayers = PyGame().getCivPlayerList( )
		
		for iPlayer in range( len( lPlayers ) ):
			if lPlayers[ iPlayer ].getStateReligion( ) == CvUtil.findInfoTypeNum(gc.getReligionInfo,gc.getNumReligionInfos(), szReligion ):
				lCities = PyPlayer( lPlayers[ iPlayer ].getID( ) ).getCityList( )
				for iCity in range( len( lCities ) ):
					pCity = lCities[ iCity ]
					pCity.changeProduction( pCity.getProductionRate( ) )
					
	def doReligiousHealthBonus( self, szReligion ):
		lPlayers = PyGame().getCivPlayerList( )
		
		for iPlayer in range( len( lPlayers ) ):
			if lPlayers[ iPlayer ].getStateReligion( ) == CvUtil.findInfoTypeNum(gc.getReligionInfo,gc.getNumReligionInfos(), szReligion ):
				lCities = PyPlayer( lPlayers[ iPlayer ].getID( ) ).getCityList( )
				for iCity in range( len( lCities ) ):
					pCity = lCities[ iCity ]
					pCity.changeFood( pCity.getFoodRate( ) )
	
	def doReligiousCultureBonus( self, szReligion ):
		lPlayers = PyGame().getCivPlayerList( )
		
		for iPlayer in range( len( lPlayers ) ):
			if lPlayers[ iPlayer ].getStateReligion( ) == CvUtil.findInfoTypeNum(gc.getReligionInfo,gc.getNumReligionInfos(), szReligion ):
				lCities = PyPlayer( lPlayers[ iPlayer ].getID( ) ).getCityList( )
				for iCity in range( len( lCities ) ):
					pCity = lCities[ iCity ]
					pCity.changeCulture( 10 )

	def doReligiousGoldBonus( self, szReligion ):
		lPlayers = PyGame().getCivPlayerList( )
		
		for iPlayer in range( len( lPlayers ) ):
			if lPlayers[ iPlayer ].getStateReligion( ) == CvUtil.findInfoTypeNum(gc.getReligionInfo,gc.getNumReligionInfos(), szReligion ):
				iGold = PyPlayer( lPlayers[ iPlayer ].getID( ) ).getGold( )
				if PyPlayer( lPlayers[ iPlayer ].getID( ) ).getGold( ) > 100:
					PyPlayer( lPlayers[ iPlayer ].getID( ) ).changeGold( iGold//10 )
				else:
					PyPlayer( lPlayers[ iPlayer ].getID( ) ).changeGold( 10 )

	def addPopup(self, szTitle, szText):
		
		# Don't display popups for autoplay games
		if (gc.getPlayer(CyGame().getActivePlayer()).isAlive()):
			
			popup = PyPopup.PyPopup(-1)
			popup.setHeaderString(localText.getText(szTitle, ()))
			popup.setBodyString(localText.getText(szText, ()))
			popup.launch(true, PopupStates.POPUPSTATE_QUEUED)
				
