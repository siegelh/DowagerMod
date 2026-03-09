## Sid Meier's Civilization 4
## Copyright Firaxis Games 2005
##
## Implementaion of miscellaneous game functions
##
## Overrides for Desert War sceanrio

import CvUtil
from CvPythonExtensions import *
import CvGameUtils
import CvDesertWar

# globals
gc = CyGlobalContext()
dw = CvDesertWar.CvDesertWar()

class CvDesertWarGameUtils(CvGameUtils.CvGameUtils):
	"Miscellaneous game functions"
	def __init__(self):
		self.parent = CvGameUtils.CvGameUtils
		self.parent.__init__(self)
	
	def isVictoryTest(self):
		if dw.isVictoryNextTurn():
			return True
		else:
			return False

	def cannotDoCivic(self,argsList):
		ePlayer = argsList[0]
		eCivic = argsList[1]

		# disable Guerrilla for big civs
		if eCivic == CvDesertWar.iGuerrilla:
			if (ePlayer == CvDesertWar.iBritish or ePlayer == CvDesertWar.iAllies \
							or ePlayer == CvDesertWar.iGermans):
				return True
		return False

	def cannotTrain(self,argsList):
		pCity = argsList[0]
		eUnit = argsList[1]
		bContinue = argsList[2]
		bVisibleTest = argsList[3]

		# disable tanks and ships if ME event occurs
		try:
			if dw.isMiddleEast():
				if pCity.getOwner() == CvDesertWar.iBritish:
					if eUnit in CvDesertWar.forbiddenUnitList:
						return True
		# if serialised data not yet setup, do nothing
		except EOFError:
			pass
		return False
	
	def calculateScore(self,argsList):
		ePlayer = argsList[0]

		# return the number of objectives a player controls as score
		iScore = 0
		for tCoords in CvDesertWar.tObjectivesList:
			if CvDesertWar.getCity(tCoords).getOwner() == ePlayer:
				iScore = iScore + 1
		return iScore

	def doHolyCity(self):
		return True