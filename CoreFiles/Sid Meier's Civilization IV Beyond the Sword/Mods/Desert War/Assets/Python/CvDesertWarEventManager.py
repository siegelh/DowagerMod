## Sid Meier's Civilization 4
## Copyright Firaxis Games 2005
## 
## CvDesertWarEventManager
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
import CvEventManager
import CvDesertWar
import sys
	
gc = CyGlobalContext()
localText = CyTranslator()
PyPlayer = PyHelpers.PyPlayer
PyInfo = PyHelpers.PyInfo
dw = CvDesertWar.CvDesertWar()

# globals
###################################################
class CvDesertWarEventManager(CvEventManager.CvEventManager):
	def __init__(self):
		# initialize base class
		self.parent = CvEventManager.CvEventManager
		self.parent.__init__(self)
		
	def onGameStart(self, argsList):
		'Called at the start of the game'
		# display welcome message
		self.parent.onGameStart(self, argsList)
		dw.welcome()
		
	def onBeginGameTurn(self, argsList):
		'Called at the beginning of a players turn'
		self.parent.onBeginGameTurn(self, argsList)
		iGameTurn = argsList[0]

		# check for events
		dw.checkGameTurnEvents(iGameTurn)

	def onBeginPlayerTurn(self, argsList):
		'Called at the beginning of a players turn'
		self.parent.onBeginPlayerTurn(self, argsList)
		iGameTurn, iPlayer = argsList

		# check for events
		dw.checkPlayerTurnEvents(iGameTurn, iPlayer)
	
	def onCombatResult(self, argsList):
		'Combat Result'
		self.parent.onCombatResult(self, argsList)

		dw.updateExtraUnitCosts()
		
	def onUnitCreated(self, argsList):
		'Unit Completed'
		self.parent.onUnitCreated(self, argsList)

		dw.updateExtraUnitCosts()

	def onUnitBuilt(self, argsList):
		'Unit Completed'
		self.parent.onUnitBuilt(self, argsList)
	
		dw.updateExtraUnitCosts()

	def onUnitKilled(self, argsList):
		'Unit Killed'
		self.parent.onUnitKilled(self, argsList)
	
		dw.updateExtraUnitCosts()

	def onUnitLost(self, argsList):
		'Unit Lost'
		self.parent.onUnitLost(self, argsList)

		dw.updateExtraUnitCosts()

	def onGoodyReceived(self, argsList):
		'Goody received'
		self.parent.onGoodyReceived(self, argsList)
		
		dw.updateExtraUnitCosts()

	def onGreatPersonBorn(self, argsList):
		'Unit Promoted'
		self.parent.onGreatPersonBorn(self, argsList)
		
		dw.updateExtraUnitCosts()

	def onReligionSpread(self, argsList):
		'Religion Has Spread to a City'
		self.parent.onReligionSpread(self, argsList)
		
		dw.updateExtraUnitCosts()

	def onGoldenAge(self, argsList):
		self.parent.onGoldenAge(self, argsList)
		
		dw.updateExtraUnitCosts()
		
	def onSetPlayerAlive(self, argsList):
		'Set Player Alive Event'
		self.parent.onSetPlayerAlive(self, argsList)
		iPlayerID = argsList[0]
		bNewValue = argsList[1]
		
		if not bNewValue:
			dw.defeatCheck(iPlayerID)
		
	def onCityBuilt(self, argsList):
		'City Built'
		self.parent.onCityBuilt(self, argsList)

		dw.updateExtraUnitCosts()

	def onCityAcquired(self, argsList):
		'City Acquired'
		self.parent.onCityAcquired(self, argsList)
		owner,playerType,city,bConquest,bTrade = argsList
		
		# in case of capture, check for events
		if bConquest:
			dw.checkCaptureEvents(owner, city, playerType)

	def onVictory(self, argsList):
		'Victory'
		self.parent.onVictory(self, argsList)
		iTeam, iVictory = argsList
	
		dw.victory()
