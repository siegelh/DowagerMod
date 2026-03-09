# Mod Events
# Civilization 4 (c) 2006 Firaxis Games

# Created by -	Jesse Crafts-Finch

from CvPythonExtensions import *
from CvScreenEnums import *
from PyHelpers import PyPlayer
import Popup as PyPopup
import CvEventManager
import CvUtil
import sys
import pickle
import CvGameUtils
import BrokenStar

# globals
gc = CyGlobalContext()
localText = CyTranslator()

DefaultUnitAI = UnitAITypes.NO_UNITAI

class CvModEvents(CvEventManager.CvEventManager):
	
	def __init__(self):
		
		self.parent = CvEventManager.CvEventManager
		self.parent.__init__(self)
###########################################################################################
##################################### EVENT OVERRIDES #####################################
###########################################################################################
	def onGameStart(self, argsList):		
		self.parent.onGameStart(self,argsList)
		BrokenStar.BrokenStar().atGameStart()
		
	def onBeginGameTurn(self, argsList):
		'Called at the beginning of the end of each turn'
		iGameTurn = argsList[0]
#		CvTopCivs.CvTopCivs().turnChecker(iGameTurn)
		BrokenStar.BrokenStar().atBeginGameTurn(argsList)
		
	def onBeginPlayerTurn(self, argsList): #49						
		self.parent.onBeginPlayerTurn(self, argsList)
		BrokenStar.BrokenStar().atBeginPlayerTurn(argsList)
		
	def onUnitCreated(self, argsList):
		self.parent.onUnitCreated(self, argsList)
		BrokenStar.BrokenStar().atUnitCreated(argsList)
		
	def onChangeWar(self, argsList):
		self.parent.onChangeWar(self, argsList)
		BrokenStar.BrokenStar().atChangeWar(argsList)

	def onModNetMessage(self, argsList):
		'Called whenever CyMessageControl().sendModNetMessage() is called - this is all for you modders!'
		
		iData1, iData2, iData3, iData4, iData5 = argsList
		
		BrokenStar.BrokenStar().onModNetMessage(argsList)

	def onNukeExplosion(self, argsList):
		self.parent.onNukeExplosion(self, argsList)
		BrokenStar.BrokenStar().atNukeExplosion(argsList)

	def onUnitKilled(self, argsList):
		self.parent.onUnitKilled(self, argsList)
		BrokenStar.BrokenStar().atUnitKilled(argsList)