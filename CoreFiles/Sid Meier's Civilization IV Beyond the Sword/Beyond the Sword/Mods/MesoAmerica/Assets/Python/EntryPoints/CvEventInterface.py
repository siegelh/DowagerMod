# Mesoamerica Scenario
# Civilization 4 (c) 2007 Firaxis Games

# Programmed by Will Miller

import CvUtil
import CvEventManager
import CvMesoamericaEvents
from CvPythonExtensions import *

gMesoamericaEventManager = CvMesoamericaEvents.CvMesoamericaEvents()
gDefaultEventManager = CvEventManager.CvEventManager()

def getEventManager():
    return gMesoamericaEventManager

def onEvent(argsList):
    'Called when a game event happnes - returns 1 if the event is consumed'
    return getEventManager().handleEvent(argsList)

def applyEvent(argsList):
    context, playerID, netUserData, popupReturn = argsList
    return getEventManager().applyEvent(argsList)

def beginEvent(context, argsList = -1):
    return getEventManager().beginEvent(context, argsList)
