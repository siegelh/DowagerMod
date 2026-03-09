# Final Frontier
# Civilization 4 (c) 2007 Firaxis Games

# Designed & Programmed by:	Jon 'Trip' Shafer

import CvUtil
import CvEventManager
import CvFinalFrontierEvents
from CvPythonExtensions import *

ModEventManager = CvFinalFrontierEvents.CvFinalFrontierEvents()
normalEventManager = CvEventManager.CvEventManager()

def getEventManager():
	return ModEventManager
	
def onEvent(argsList):
	'Called when a game event happens - return 1 if the event was consumed'
	return getEventManager().handleEvent(argsList)

def applyEvent(argsList):
	context, playerID, netUserData, popupReturn = argsList
	return getEventManager().applyEvent(argsList)

def beginEvent(context, argsList=-1):
	return getEventManager().beginEvent(context, argsList)
