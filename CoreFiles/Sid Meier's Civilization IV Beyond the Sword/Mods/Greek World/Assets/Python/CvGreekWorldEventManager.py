## Sid Meier's Civilization 4
## Copyright Firaxis Games 2005
## 
## CvGreekWorldEventManager
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
import GreekWorld	# Rhye
import sys
	
gc = CyGlobalContext()
localText = CyTranslator()
PyPlayer = PyHelpers.PyPlayer
PyInfo = PyHelpers.PyInfo
gw1 = GreekWorld.GreekWorld()	# Rhye

# globals
###################################################
class CvGreekWorldEventManager(CvEventManager.CvEventManager):
	def __init__(self):
		# initialize base class
		self.parent = CvEventManager.CvEventManager
		self.parent.__init__(self)

	def onGameStart(self, argsList):
		'Called at the start of the game'
		self.parent.onGameStart(self, argsList)
		gw1.setup()
	
	def onBeginGameTurn(self, argsList):
		iGameTurn = argsList[0]
		self.parent.onBeginGameTurn(self, argsList)
		gw1.checkTurn(iGameTurn)
		
	def onCityAcquired(self, argsList):
		#'City Acquired'
		owner,playerType,city,bConquest,bTrade = argsList
		#CvUtil.pyPrint('City Acquired Event: %s' %(city.getName()))
		self.parent.onCityAcquired(self, argsList)
		gw1.checkCities(city, playerType)
