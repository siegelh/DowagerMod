# American Revolution
# Civilization 4 (c) 2005 Firaxis Games

# Created by -	Jon 'Trip' Shafer
# Have fun!

from CvPythonExtensions import *
import sys
import Popup as PyPopup
from PyHelpers import PyPlayer
import pickle
import CvEventManager
from CvScreenEnums import *
from PyHelpers import *
import CvUtil

# globals
gc = CyGlobalContext()
localText = CyTranslator()

DefaultUnitAI = UnitAITypes.NO_UNITAI

class CvAmRevEvents(CvEventManager.CvEventManager):
	
	def __init__(self):
		
		CvEventManager.CvEventManager.__init__(self)
		
		# Offset value set in WorldBuilder save
		self.iTurnOffset = 6
		
		self.iCityUnitSpawnCounterDefault = 8#8
		self.iUnitSpawnRange = 2#2
		self.iMilitiaSpawnChance = 15#15
		self.iLoyalistSpawnChance = 10#10
		
		self.iBritishGoldAmount = 320#250
		self.iBritishReinforceCounter = 12#8
		self.aiBritishReinforceLandPlot = [37, 46]
		self.aiBritishReinforceWaterPlot = [39, 46]
		
		self.iFrenchGoldAmount = 70#200
		self.iFrenchReinforceCounter = 13#8
		self.aiFrenchReinforceWaterPlot = [38, 24]
		
		self.iMilitiaDisbandCounter = 8#8
		
		self.iAlignmentDeclareWarThreshold = 400#400
		
		self.iColonialID =		0
		self.iBritishID =		1
		self.iSpanishID =		2
		self.iFrenchID =		3
		self.iNumPlayers =              4
		
		self.szEventText = ""
		self.szResultText = ""
		
	def turnChecker(self, iTurn):
		
		# Temp for use while debugging/reloading
#		self.initValues()
		
		# Setup players for use in this function
		
		pBritish = gc.getPlayer(self.iBritishID)
		pFrench = gc.getPlayer(self.iFrenchID)
		pFrenchTeam = gc.getTeam(pFrench.getTeam())
		
		self.szGameDate = CyGameTextMgr().getTimeStr(iTurn, false)
		
		# Change alignment on a per-turn basis
		self.changePlayerAlignment(self.iSpanishID, 10)
		self.changePlayerAlignment(self.iFrenchID, 10)
		
		# Check for Spanish and French alignment
		self.checkAlignment()
		
		# Reset culture on captured cities
#		self.resetCityCulture()
		
		# Alter Militia counters and disband the units that are too old
		self.alterMilitiaCounters()
		
		# Alter City Unit Spawning Counters
		self.alterCitySpawnUnitCounters()
		
		# British reinforcements every [self.iBritishReinforceCounter] turns
		if ((iTurn - self.iTurnOffset) > 0 and (iTurn - self.iTurnOffset) % self.iBritishReinforceCounter == 0):
			self.addBritishReinforcements(iTurn)
		
		# French reinforcements every [self.iFrenchReinforceCounter] turns if France is at war with Britain
		if ((iTurn - self.iTurnOffset) > 0
		    and (iTurn - self.iTurnOffset) % self.iFrenchReinforceCounter == 0
		    and pFrenchTeam.isAtWar(pBritish.getTeam())):
			
			self.addFrenchReinforcements(iTurn)
			
		# Insert all game turn events here
#		return
		
#		print("Turn is: %d" %(iTurn))
		if (iTurn == 4 + self.iTurnOffset):
			self.Nov_1775()
		elif (iTurn == 6 + self.iTurnOffset):
			self.Jan_1776()
		elif (iTurn == 10 + self.iTurnOffset):
			self.May_1776_1()
			self.May_1776_2()
		elif (iTurn == 12 + self.iTurnOffset):
			self.Jul_1776()
		elif (iTurn == 27 + self.iTurnOffset):
			self.Oct_1777()
		elif (iTurn == 31 + self.iTurnOffset):
			self.Feb_1778()
		elif (iTurn == 49 + self.iTurnOffset):
			self.Aug_1779()
		elif (iTurn == 60 + self.iTurnOffset):
			self.Jul_1780()
		elif (iTurn == 61 + self.iTurnOffset):
			self.Aug_1780()
		elif (iTurn == 73 + self.iTurnOffset):
			self.Aug_1781()
	
	# Determine the start-game state
	def setupGame(self):
		
		# Temporary Measure to turn off 'Feats'		
		CyMessageControl().sendPlayerOption(PlayerOptionTypes.PLAYEROPTION_ADVISOR_POPUPS, false)
		
		self.initValues()
		
#		pColonists = gc.getPlayer(self.iColonialID)
#		pColonistsTeam = gc.getTeam(pColonists.getTeam())
		
		pBritish = gc.getPlayer(self.iBritishID)
		pBritishTeam = gc.getTeam(pBritish.getTeam())
		
#		pSpanish = gc.getPlayer(self.iSpanishID)
#		pSpanishTeam = gc.getTeam(pSpanish.getTeam())
		
#		pFrench = gc.getPlayer(self.iFrenchID)
#		pFrenchTeam = gc.getTeam(pFrench.getTeam())
		
		# Used to prevent the AI from acting the same at the start of every game
		self.randomizeStartingArmies()
		
		for iPlayerLoop in range(self.iNumPlayers):
			
			self.setPlayerAlignment(iPlayerLoop, 0)
			
			pPlayer = gc.getPlayer(iPlayerLoop)
#			pyPlayer = PyPlayer(iPlayerLoop)
			
			# Set player default commerce to 100% gold since there are no techs
			pPlayer.setCommercePercent(CommerceTypes.COMMERCE_RESEARCH, 0)
			
			# Loop through player's cities
#			apCityList = pyPlayer.getCityList()
#			
#			for pCityLoop in apCityList:
#			for iCityLoop in range(pPlayer.getNumCities()):		# We can iterate through the cities this way because there's no risk of any of them not existing yet since the game has just been initialized
#				
#				pCityLoop = pPlayer.getCity(iCityLoop)
#				
#				# Initialize City
#				self.initCity(pCityLoop)
#				
			# Loop through player's units
			for iUnitLoop in range(pPlayer.getNumUnits()):
				
				self.setUnitDisbandCounter(iPlayerLoop, iUnitLoop, -1)
				
	def initValues(self):
		
		self.iContinentalRegularID =	CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'AMREV_UNIT_CONTINENTAL_REGULAR')#83
		self.iMinutemanID =		CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'AMREV_UNIT_MINUTEMAN')#84
		self.iMilitiaID =		CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'AMREV_UNIT_MILITIA')#85
		self.iPrivateerID =		CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'AMREV_UNIT_PRIVATEER')#86
		self.iBritishRegularID =	CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'AMREV_UNIT_BRITISH_REGULAR')#87
		self.iGermanMercenaryID =	CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'AMREV_UNIT_GERMAN_MERCENARY')#88
		self.iLoyalistIrregularID =	CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'AMREV_UNIT_LOYALIST_IRREGULAR')#89
		self.iTransportID =		CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'AMREV_UNIT_TRANSPORT')#90
		self.iSpanishRegularID =	CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'AMREV_UNIT_SPANISH_REGULAR')#91
		self.iCannonID =		CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'AMREV_UNIT_CANNON')#92
		self.iCavalryID =		CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'AMREV_UNIT_CAVALRY')#93
		self.iShipOfTheLineID =		CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'AMREV_UNIT_SHIP_OF_THE_LINE')#94
		self.iFrigateID =		CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'AMREV_UNIT_FRIGATE')#95
		self.iFrenchRegularID =		CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'AMREV_UNIT_FRENCH_REGULAR')#96
		
		self.iMillID =			CvUtil.findInfoTypeNum(gc.getBuildingInfo,gc.getNumBuildingInfos(),'AMREV_BUILDING_MILL')#99
		self.iTownHallID =		CvUtil.findInfoTypeNum(gc.getBuildingInfo,gc.getNumBuildingInfos(),'AMREV_BUILDING_TOWN_HALL')#100
		self.iChurchID =		CvUtil.findInfoTypeNum(gc.getBuildingInfo,gc.getNumBuildingInfos(),'AMREV_BUILDING_CHURCH')#101
		self.iDockID =			CvUtil.findInfoTypeNum(gc.getBuildingInfo,gc.getNumBuildingInfos(),'AMREV_BUILDING_DOCK')#102
		self.iColonialOutpostID =	CvUtil.findInfoTypeNum(gc.getBuildingInfo,gc.getNumBuildingInfos(),'AMREV_BUILDING_COLONIAL_OUTPOST')#103
		self.iProvincialSeatID =	CvUtil.findInfoTypeNum(gc.getBuildingInfo,gc.getNumBuildingInfos(),'AMREV_BUILDING_PROVINCIAL_SEAT')#104
		
		for iPlayerLoop in range(self.iNumPlayers):
			
			pPlayer = gc.getPlayer(iPlayerLoop)
			pyPlayer = PyPlayer(iPlayerLoop)
			# Loop through player's cities
			apCityList = pyPlayer.getCityList()
			
			for pCityLoop in apCityList:
#			for iCityLoop in range(pPlayer.getNumCities()):		# We can iterate through the cities this way because there's no risk of any of them not existing yet since the game has just been initialized
				
#				pCityLoop = pPlayer.getCity(iCityLoop)
				
				# Initialize City
				self.initCity(pCityLoop)
				
	def initCity(self, pCity):
		
		aiCityXY = [pCity.getX(), pCity.getY()]
		
		# This will become the city "ID" within the scenario used to identify it later (in case it's renamed or something)
		iCityCount = 0
		
		iCitySpawnUnitCounterDefault = 0
		
		if (aiCityXY == [28, 41]):
			self.iPORTLAND = iCityCount = 0
			print("self.iPORTLAND = iCityCount = 0")
		elif (aiCityXY == [16, 37]):
			self.iYORK = iCityCount = 1
			print("self.iYORK = iCityCount = 1")
		elif (aiCityXY == [10, 32]):
			self.iDETROIT = iCityCount = 2
			print("self.iDETROIT = iCityCount = 2")
		elif (aiCityXY == [16, 30]):
			self.iFT_PITT = iCityCount = 3
			print("self.iFT_PITT = iCityCount = 3")
		elif (aiCityXY == [6, 26]):
			self.iFT_VINCENNES = iCityCount = 4
			print("self.iFT_VINCENNES = iCityCount = 4")
		elif (aiCityXY == [13, 14]):
			self.iFT_AUGUSTA = iCityCount = 5
			print("self.iFT_AUGUSTA = iCityCount = 5")
		elif (aiCityXY == [6, 10]):
			self.iMOBILE = iCityCount = 6
			print("self.iMOBILE = iCityCount = 6")
		elif (aiCityXY == [10, 10]):
			self.iPENSACOLA = iCityCount = 7
			print("self.iPENSACOLA = iCityCount = 7")
		elif (aiCityXY == [17, 7]):
			self.iST_AUGUSTINE = iCityCount = 8
			print("self.iST_AUGUSTINE = iCityCount = 8")
		
		elif (aiCityXY == [26, 37]):
			self.iBOSTON = iCityCount = 9
			print("self.iBOSTON = iCityCount = 9")
		elif (aiCityXY == [22, 36]):
			self.iALBANY = iCityCount = 10
			print("self.iALBANY = iCityCount = 10")
		elif (aiCityXY == [24, 33]):
			self.iNEW_YORK_CITY = iCityCount = 11
			print("self.iNEW_YORK_CITY = iCityCount = 11")
		elif (aiCityXY == [22, 30]):
			self.iPHILADELPHIA = iCityCount = 12
			print("self.iPHILADELPHIA = iCityCount = 12")
		elif (aiCityXY == [20, 27]):
			self.iBALTIMORE = iCityCount = 13
			print("self.iBALTIMORE = iCityCount = 13")
		elif (aiCityXY == [19, 23]):
			self.iRICHMOND = iCityCount = 14
			print("self.iRICHMOND = iCityCount = 14")
		elif (aiCityXY == [22, 22]):
			self.iNORFOLK = iCityCount = 15
			print("self.iNORFOLK = iCityCount = 15")
		elif (aiCityXY == [16, 19]):
			self.iCHARLOTTE = iCityCount = 16
			print("self.iCHARLOTTE = iCityCount = 16")
		elif (aiCityXY == [20, 18]):
			self.iWILMINGTON = iCityCount = 17
			print("self.iWILMINGTON = iCityCount = 17")
		elif (aiCityXY == [17, 15]):
			self.iCHARLESTON = iCityCount = 18
			print("self.iCHARLESTON = iCityCount = 18")
		elif (aiCityXY == [15, 12]):
			self.iSAVANNAH = iCityCount = 19
			print("self.iSAVANNAH = iCityCount = 19")
		
		if (aiCityXY == [34, 43]):
			self.iHALIFAX = iCityCount = 20
			print("self.iHALIFAX = iCityCount = 20")
		elif (aiCityXY == [25, 46]):
			self.iQUEBEC = iCityCount = 21
			print("self.iQUEBEC = iCityCount = 21")
		elif (aiCityXY == [23, 43]):
			self.iTROIS_RIVIERES = iCityCount = 22
			print("self.iTROIS_RIVIERES = iCityCount = 22")
		elif (aiCityXY == [21, 40]):
			self.iMONTREAL = iCityCount = 23
			print("self.iMONTREAL = iCityCount = 23")
		
		elif (aiCityXY == [1, 24]):
			self.iST_LOUIS = iCityCount = 24
			print("self.iST_LOUIS = iCityCount = 24")
		elif (aiCityXY == [2, 8]):
			self.iNEW_ORLEANS = iCityCount = 25
			print("self.iNEW_ORLEANS = iCityCount = 25")
		
		# Set default script data manually since we need defaults for all values in array
		aScriptData = [iCityCount, iCitySpawnUnitCounterDefault]
		pCity.setScriptData(pickle.dumps(aScriptData))
		
###########################################################################################
####################################### MISC EVENTS #######################################
###########################################################################################
		
	def randomizeStartingArmies(self):
		
		# Brits in Boston
		aiBritishPlot = [26, 37]
		# Yanks knockin on the door
		aiColonialPlot = [25, 36]
		
		###### British first ######
		
		pPlot = CyMap().plot(aiBritishPlot[0], aiBritishPlot[1])
		iNumPlotUnits = pPlot.getNumUnits()
		
		# Pick random AI Type: 50% Reserve, 25% city defense, 25% attack
		iRand = self.getRand(4)
		if (iRand <= 1):
			iChosenAIType = UnitAITypes.UNITAI_RESERVE
		elif (iRand == 2):
			iChosenAIType = UnitAITypes.UNITAI_CITY_DEFENSE
		elif (iRand == 3):
			iChosenAIType = UnitAITypes.UNITAI_ATTACK
		
		for iUnitLoop in range(iNumPlotUnits):
			pUnit = pPlot.getUnit(iUnitLoop)
			pUnit.setUnitAIType(iChosenAIType)
		
		###### Now the Colonists ######
		
		pPlot = CyMap().plot(aiColonialPlot[0], aiColonialPlot[1])
		iNumPlotUnits = pPlot.getNumUnits()
		
		# Pick random AI Type: 33% Reserve, 33% attack, 33% counter
		iRand = self.getRand(3)
		if (iRand == 0):
			iChosenAIType = UnitAITypes.UNITAI_RESERVE
		elif (iRand == 1):
			iChosenAIType = UnitAITypes.UNITAI_ATTACK
		elif (iRand == 2):
			iChosenAIType = UnitAITypes.UNITAI_COUNTER
		
		for iUnitLoop in range(iNumPlotUnits):
			pUnit = pPlot.getUnit(iUnitLoop)
			pUnit.setUnitAIType(iChosenAIType)
			
	def checkAlignment(self):
		
		iSpanishAlignment = self.getPlayerAlignment(self.iSpanishID)
		iFrenchAlignment = self.getPlayerAlignment(self.iFrenchID)
		
		# If Alignment is high enough then these nations declare war on Britain
		if (iSpanishAlignment > self.iAlignmentDeclareWarThreshold):
			
			pSpanish = gc.getPlayer(self.iSpanishID)
			pSpanishTeam = gc.getTeam(pSpanish.getTeam())
			
			if (not pSpanishTeam.isAtWar(self.iBritishID)):
				pSpanishTeam.declareWar(self.iBritishID, false)
				
				# Set event text
				self.szEventText = localText.getText("TXT_KEY_AMREV_SPAIN_DECLARES_WAR", ())
				self.szResultText = ""
				
				self.displayEventText()
			
		if (iFrenchAlignment > self.iAlignmentDeclareWarThreshold):
			
			pFrench = gc.getPlayer(self.iFrenchID)
			pFrenchTeam = gc.getTeam(pFrench.getTeam())
			
			if (not pFrenchTeam.isAtWar(self.iBritishID)):
				pFrenchTeam.declareWar(self.iBritishID, false)
				
				# Set event text
				self.szEventText = localText.getText("TXT_KEY_AMREV_FRANCE_DECLARES_WAR", ())
				self.szResultText = ""
				
				self.displayEventText()
		
	def alterMilitiaCounters(self):
		
		pPlayer = PyPlayer(self.iColonialID)
		apUnitList = pPlayer.getUnitList()
		
		# Loop through all Colonial units
		for pUnit in apUnitList:
			if (pUnit.getUnitType() == self.iMilitiaID):
				
				iUnitID = pUnit.getID()
				self.changeUnitDisbandCounter(self.iColonialID, iUnitID, 1)
				
				# This unit's day has come
				if (self.getUnitDisbandCounter(self.iColonialID, iUnitID) >= self.iMilitiaDisbandCounter):
					pUnit.kill(false, PlayerTypes.NO_PLAYER)
					
	def alterCitySpawnUnitCounters(self):
		
		# Loop through all players' cities
		for iPlayerLoop in range(self.iNumPlayers):
			
			pPlayer = PyPlayer(iPlayerLoop)
			apCityList = pPlayer.getCityList()
			
			for pCity in apCityList:
				
				iCityID = pCity.getID()
				# Reduce CitySpawnUnit counter by 1 in applicable cities
				if (self.getCitySpawnUnitCounter(iPlayerLoop, iCityID) > 0):
					
					self.changeCitySpawnUnitCounter(iPlayerLoop, iCityID, -1)
		
#	def resetCityCulture(self):
#		
#		# Loop through each player's cities and reset their culture depending on the list they belong to
#		
#		for iPlayerLoop in range(self.iNumPlayers):
#			
#			pPlayer = PyPlayer(iPlayerLoop)
#			
#			if (pPlayer.isAlive()):
#				
#				if (iPlayerLoop == self.iColonialID):
#					aiValidCities = self.aszColonialCities
#				elif (iPlayerLoop == self.iBritishID):
#					aiValidCities = self.aszBritishCities
#				elif (iPlayerLoop == self.iSpanishID):
#					aiValidCities = self.aszSpanishCities
#				elif (iPlayerLoop == self.iFrenchID):
#					aiValidCities = self.aszNeutralCities
#				
#				apCityList = pPlayer.getCityList()
#				for pCity in apCityList:
#					
#					if (pCity.getName() not in aiValidCities):
#						
#						pCity.setCulture(0, true)
						
	def checkForUnitSpawning(self, iPlayer, iUnitX, iUnitY, eUnitDomainType):
		
		# Units only spawn when Britain walks through
		if (iPlayer == self.iBritishID):
			
#			print("eUnitDomainType: %d" %(eUnitDomainType))
#			print("DomainTypes.DOMAIN_LAND: %d" %(DomainTypes.DOMAIN_LAND))
			
			# Only land units should affect things
			if (eUnitDomainType == DomainTypes.DOMAIN_LAND):
				
				pColonists = PyPlayer(self.iColonialID)
				
				# Loop through Colonial cities
				apCityList = pColonists.getCityList()
				for pCity in apCityList:
					iCityID = pCity.getID()
					iCityX = pCity.getX()
					iCityY = pCity.getY()
					
					# If this city has spawned a unit recently then no more units
					if (self.getCitySpawnUnitCounter(self.iColonialID, iCityID) == 0):
						
						# This unit is in range of a Colonial city
						if ((iUnitX >= (iCityX - self.iUnitSpawnRange)) and
						    (iUnitX <= (iCityX + self.iUnitSpawnRange)) and
						    (iUnitY >= (iCityY - self.iUnitSpawnRange)) and
						    (iUnitY <= (iCityY + self.iUnitSpawnRange))):
							
							iUnitSpawnRoll = self.getRand(99)
							
#							print("Unit Spawn Roll: %d" %(iUnitSpawnRoll))
							
							# Create Militia for the Colonists
							if (iUnitSpawnRoll < self.iMilitiaSpawnChance):
								
								aiSpawnPlot = self.findUnitPlacementPlot(self.iColonialID, iCityX, iCityY, true, true, 2)
								
								if (aiSpawnPlot == "Oh Snap"):
									return
								else:
									pColonists.initUnit(self.iMilitiaID, aiSpawnPlot[0], aiSpawnPlot[1], DefaultUnitAI)
									
									self.setCitySpawnUnitCounter(self.iColonialID, iCityID, self.iCityUnitSpawnCounterDefault)
									
									# Set event text
									self.szEventText = localText.getText("TXT_KEY_AMREV_SPAWN_MILITIA_TEXT", ())
									self.szResultText = localText.getText("TXT_KEY_AMREV_SPAWN_MILITIA_RESULT", (pCity.getName(),))
									
									self.displayEventText()
									
							# Create Loyalist Irregular for the British
							elif (iUnitSpawnRoll < self.iMilitiaSpawnChance + self.iLoyalistSpawnChance):
								
								aiSpawnPlot = self.findUnitPlacementPlot(self.iBritishID, iCityX, iCityY, true, false, 2)
								
								if (aiSpawnPlot == "Oh Snap"):
									return
								else:
									
									gc.getPlayer(self.iBritishID).initUnit(self.iLoyalistIrregularID, aiSpawnPlot[0], aiSpawnPlot[1], DefaultUnitAI)
									
									self.setCitySpawnUnitCounter(self.iColonialID, iCityID, self.iCityUnitSpawnCounterDefault)
									
									# Set event text
									self.szEventText = localText.getText("TXT_KEY_AMREV_SPAWN_LOYALIST_TEXT", ())
									self.szResultText = localText.getText("TXT_KEY_AMREV_SPAWN_LOYALIST_RESULT", (pCity.getName(),))
									
									self.displayEventText()
									
	def addBritishReinforcements(self, iTurn):
		
		pBritishPlayer = gc.getPlayer(self.iBritishID)
		
		# Increase coffers (can't be going bankrupt now)
		pBritishPlayer.changeGold(self.iBritishGoldAmount)
		
		# Determine force list based upon what turn it is
		
		if (iTurn < 40 + self.iTurnOffset):
			iNumRegulars =		3
			iRegularChance =	60
			iNumPossRegulars =	3
			
			iNumCavalaries =	0
			iCavalryChance =	30
			iNumPossCavalries =	2
			
			iNumMercenaries =	0
			iMercenaryChance =	30
			iNumPossMercenaries =	2
			
			iNumCannons =		0
			iCannonChance =		20
			iNumPossCannons =	2
			
			iNumSOTL =		0
			iSOTLChance =		20
			iNumPossSOTL =		1
			
			iNumFrigates =		0
			iFrigateChance =	25
			iNumPossFrigates =	2
			
			iNumTransports =	1
			iTransportChance =	20
			iNumPossTransports =	1
			
		else:
			iNumRegulars =		4
			iRegularChance =	50
			iNumPossRegulars =	3
			
			iNumCavalaries =	1
			iCavalryChance =	50
			iNumPossCavalries =	1
			
			iNumMercenaries =	2
			iMercenaryChance =	50
			iNumPossMercenaries =	2
			
			iNumCannons =		1
			iCannonChance =		30
			iNumPossCannons =	2
			
			iNumSOTL =		1
			iSOTLChance =		20
			iNumPossSOTL =		2
			
			iNumFrigates =		2
			iFrigateChance =	30
			iNumPossFrigates =	2
			
			iNumTransports =	1
			iTransportChance =	50
			iNumPossTransports =	1
		
		# Determine the number of units to spawn
		for iUnitNumLoop in range(iNumPossRegulars):
			if (self.getRand(99) < iRegularChance):
				iNumRegulars += 1
		for iUnitNumLoop in range(iNumPossCavalries):
			if (self.getRand(99) < iCavalryChance):
				iNumCavalaries += 1
		for iUnitNumLoop in range(iNumPossMercenaries):
			if (self.getRand(99) < iMercenaryChance):
				iNumMercenaries += 1
		for iUnitNumLoop in range(iNumPossCannons):
			if (self.getRand(99) < iCannonChance):
				iNumCannons += 1
		for iUnitNumLoop in range(iNumPossSOTL):
			if (self.getRand(99) < iSOTLChance):
				iNumSOTL += 1
		for iUnitNumLoop in range(iNumPossFrigates):
			if (self.getRand(99) < iFrigateChance):
				iNumFrigates += 1
		for iUnitNumLoop in range(iNumPossTransports):
			if (self.getRand(99) < iTransportChance):
				iNumTransports += 1
		
		# Determine a plot for land units to go to, then add them
		
		iLandPlotRange = 3
		
		aiLandUnitsPlot = self.findUnitPlacementPlot(self.iBritishID, self.aiBritishReinforceLandPlot[0], self.aiBritishReinforceLandPlot[1])
		
		if (aiLandUnitsPlot == "Oh Snap"):
			return
			
		else:
			iX = aiLandUnitsPlot[0]
			iY = aiLandUnitsPlot[1]
			
			for iUnitLoop in range(iNumRegulars):
				pBritishPlayer.initUnit(self.iBritishRegularID, iX, iY, UnitAITypes.UNITAI_ATTACK)
			for iUnitLoop in range(iNumMercenaries):
				pBritishPlayer.initUnit(self.iGermanMercenaryID, iX, iY, UnitAITypes.UNITAI_ATTACK)
			for iUnitLoop in range(iNumCannons):
				pBritishPlayer.initUnit(self.iCannonID, iX, iY, UnitAITypes.UNITAI_ATTACK)
			for iUnitLoop in range(iNumCavalaries):
				pBritishPlayer.initUnit(self.iCavalryID, iX, iY, UnitAITypes.UNITAI_ATTACK)
		
		# Now naval units
		
		iWaterPlotRange = 3
		
		aiWaterUnitsPlot = self.findUnitPlacementPlot(self.iBritishID, self.aiBritishReinforceWaterPlot[0], self.aiBritishReinforceWaterPlot[1], false)
		
		if (aiWaterUnitsPlot == "Oh Snap"):
			return
			
		else:
			iX = aiWaterUnitsPlot[0]
			iY = aiWaterUnitsPlot[1]
			
			for iUnitLoop in range(iNumSOTL):
				pBritishPlayer.initUnit(self.iShipOfTheLineID, iX, iY, UnitAITypes.UNITAI_ATTACK_SEA)
			for iUnitLoop in range(iNumFrigates):
				pBritishPlayer.initUnit(self.iFrigateID, iX, iY, UnitAITypes.UNITAI_ATTACK_SEA)
			for iUnitLoop in range(iNumTransports):
				pBritishPlayer.initUnit(self.iTransportID, iX, iY, UnitAITypes.UNITAI_ASSAULT_SEA)
		
		# Set event text
		self.szEventText = localText.getText("TXT_KEY_AMREV_BRITISH_REINFORCE_TEXT", ())
		self.szResultText = localText.getText("TXT_KEY_AMREV_BRITISH_REINFORCE_RESULT", ())
		
		self.displayEventText()
									
	def addFrenchReinforcements(self, iTurn):
		
		pFrenchPlayer = gc.getPlayer(self.iFrenchID)
		
		# Increase coffers (can't be going bankrupt now)
		pFrenchPlayer.changeGold(self.iFrenchGoldAmount)
		
		# Determine force list based upon what turn it is
		
		iNumRegulars =		2
		iRegularChance =	50
		iNumPossRegulars =	1
		
		iNumFrigates =		1
		iFrigateChance =	25
		iNumPossFrigates =	1
		
		iNumTransports =	1
		iTransportChance =	0
		iNumPossTransports =	0
		
		# Determine the number of units to spawn
		for iUnitNumLoop in range(iNumPossRegulars):
			if (self.getRand(99) < iRegularChance):
				iNumRegulars += 1
		for iUnitNumLoop in range(iNumPossFrigates):
			if (self.getRand(99) < iFrigateChance):
				iNumFrigates += 1
		for iUnitNumLoop in range(iNumPossTransports):
			if (self.getRand(99) < iTransportChance):
				iNumTransports += 1
		
		# Find a plot out to sea to put the new French fleet
		
		iWaterPlotRange = 5
		
		aiWaterUnitsPlot = self.findUnitPlacementPlot(self.iFrenchID, self.aiFrenchReinforceWaterPlot[0], self.aiFrenchReinforceWaterPlot[1], false)
		
		if (aiWaterUnitsPlot == "Oh Snap"):
			return
			
		else:
			iX = aiWaterUnitsPlot[0]
			iY = aiWaterUnitsPlot[1]
			
			# Add the boats first and the land units will automatically load aboard them - neat!
			for iUnitLoop in range(iNumFrigates):
				pFrenchPlayer.initUnit(self.iFrigateID, iX, iY, UnitAITypes.UNITAI_ATTACK_SEA)
			for iUnitLoop in range(iNumTransports):
				pFrenchPlayer.initUnit(self.iTransportID, iX, iY, UnitAITypes.UNITAI_ASSAULT_SEA)
			for iUnitLoop in range(iNumRegulars):
				pFrenchPlayer.initUnit(self.iFrenchRegularID, iX, iY, UnitAITypes.UNITAI_ATTACK)
		
		# Set event text
#		szSingularKey = "TXT_KEY_AMREV_UNIT_FRENCH_REGULAR"
#		szPluralString = localText.getText("TXT_KEY_PLURAL", ("TXT_KEY_AMREV_UNIT_FRENCH_REGULAR",))
#		self.szEventText = localText.getText("TXT_KEY_AMREV_UNIT_APPEARS_N_CITY_RESULT",
#		    (2, szPlayerAdj, szSingularKey, szPluralString, szCityName,))
#		self.szEventText = localText.getText("TXT_KEY_AMREV_BRITISH_REINFORCE_TEXT", ())
#		self.szResultText = ""#localText.getText("TXT_KEY_AMREV_BRITISH_REINFORCE_RESULT", ())
		
#		self.displayEventText()
		
###########################################################################################
####################################### TURN EVENTS #######################################
###########################################################################################
		
	# New American Navy - 2 Privateers
	def Nov_1775(self):
		
		aiValidCities = [	self.iNEW_YORK_CITY,
					self.iBALTIMORE,
					self.iCHARLESTON	]
		
		iCityID = self.determineValidCities(self.iColonialID, aiValidCities)
		
		# If valid city exists
		if (iCityID > -1):
			
			pPlayer = gc.getPlayer(self.iColonialID)
			szPlayerAdj = pPlayer.getCivilizationAdjective(0)
			
			szCityName = pPlayer.getCity(iCityID).getName()
			
			iUnitType = self.iPrivateerID
			
			iCityX = pPlayer.getCity(iCityID).getX()
			iCityY = pPlayer.getCity(iCityID).getY()
			
			# Spawn units
			pPlayer.initUnit(iUnitType, iCityX, iCityY, DefaultUnitAI)
			pPlayer.initUnit(iUnitType, iCityX, iCityY, DefaultUnitAI)
			
			# Set event text
			self.szEventText = localText.getText("TXT_KEY_AMREV_NOV_1775_TEXT", ())
			szSingularKey = "TXT_KEY_AMREV_UNIT_PRIVATEER"
			szPluralString = localText.getText("TXT_KEY_PLURAL", ("TXT_KEY_AMREV_UNIT_PRIVATEER",))
			self.szResultText = localText.getText("TXT_KEY_AMREV_UNIT_APPEARS_IN_CITY_RESULT",
			    (2, szPlayerAdj, szSingularKey, szPluralString, szCityName,))
			
			self.displayEventText()
		
	# Thomas Paine - 1 Minuteman
	def Jan_1776(self):
		
		aiValidCities = [	self.iPHILADELPHIA,
					self.iBALTIMORE	]
		
		iCityID = self.determineValidCities(self.iColonialID, aiValidCities)
		
		# If valid city exists
		if (iCityID > -1):
			
			pPlayer = gc.getPlayer(self.iColonialID)
			szPlayerAdj = pPlayer.getCivilizationAdjective(0)
			
			szCityName = pPlayer.getCity(iCityID).getName()
			
			iUnitType = self.iMinutemanID

			iCityX = pPlayer.getCity(iCityID).getX()
			iCityY = pPlayer.getCity(iCityID).getY()
			
			# Spawn unit
			pPlayer.initUnit(iUnitType, iCityX, iCityY, UnitAITypes.UNITAI_ATTACK)
			
			# Set event text
			self.szEventText = localText.getText("TXT_KEY_AMREV_JAN_1776_TEXT", ())
			szSingularKey = "TXT_KEY_AMREV_UNIT_MINUTEMAN"
			szPluralString = localText.getText("TXT_KEY_PLURAL", ("TXT_KEY_AMREV_UNIT_MINUTEMAN",))
			self.szResultText = localText.getText("TXT_KEY_AMREV_UNIT_APPEARS_IN_CITY_RESULT",
			    (1, szPlayerAdj, szSingularKey, szPluralString, szCityName,))
#			self.szResultText = localText.getText("TXT_KEY_AMREV_UNIT_APPEARS_IN_CITY_RESULT", (1, szPlayerAdj, "TXT_KEY_AMREV_UNIT_MINUTEMAN", szCityName,))
			
			self.displayEventText()
		
	# France & Spain support - gold, units, alignment
	def May_1776_1(self):
		
		szCityName = ""
		
		pPlayer = gc.getPlayer(self.iColonialID)
		
		##### Add Gold #####
		
		pPlayer.changeGold(25)
		
		##### Add Units #####
		
		aiValidCities = [	self.iPHILADELPHIA,
					self.iNEW_YORK_CITY,
					self.iBALTIMORE	]
		
		iCityID = self.determineValidCities(self.iColonialID, aiValidCities)
		
		# If valid city exists
		if (iCityID > -1):
			szPlayerAdj = pPlayer.getCivilizationAdjective(0)
			
			szCityName = pPlayer.getCity(iCityID).getName()
			
			iUnitType = self.iContinentalRegularID
			szUnitName = localText.getText("TXT_KEY_AMREV_UNIT_CONTINENTAL_REGULAR", ())	# PLURAL?

			iCityX = pPlayer.getCity(iCityID).getX()
			iCityY = pPlayer.getCity(iCityID).getY()
			
			# Spawn units
			pPlayer.initUnit(iUnitType, iCityX, iCityY, UnitAITypes.UNITAI_ATTACK)
			pPlayer.initUnit(iUnitType, iCityX, iCityY, UnitAITypes.UNITAI_ATTACK)
		
		##### Change Alignment #####
		
		self.changePlayerAlignment(self.iFrenchID, 20)
		self.changePlayerAlignment(self.iSpanishID, 15)
		
		# Set event text
		self.szEventText = localText.getText("TXT_KEY_AMREV_MAY_1776_TEXT_1", ())
		self.szResultText = localText.getText("TXT_KEY_AMREV_MAY_1776_RESULT_1", (szCityName,))
		
		self.displayEventText()
		
	# Provincial Governments
	def May_1776_2(self):
		
#		pPlayer = gc.getPlayer(self.iColonialID)
		pPlayer = PyPlayer(self.iColonialID)
		
		aiValidCities = [	self.iBOSTON,
					self.iNEW_YORK_CITY,
					self.iPHILADELPHIA,
					self.iRICHMOND,
					self.iCHARLESTON	]
		
		# Add Provincial Seats to these cities
		apCityList = pPlayer.getCityList()
		for pCity in apCityList:
#		for iCityLoop in range(pPlayer.getNumCities()):
#			pCity = pPlayer.getCity(iCityLoop)
			
			if (pCity.getName() in aiValidCities):
				
				pCity.setHasRealBuildingIdx(self.iProvincialSeatID, true)
		
		# Set event text
		self.szEventText = localText.getText("TXT_KEY_AMREV_MAY_1776_TEXT_2", ())
		self.szResultText = localText.getText("TXT_KEY_AMREV_MAY_1776_RESULT_2", ())
		
		self.displayEventText()
		
	# Independence - France & Spain Alignment
	def Jul_1776(self):
		
		##### Change Alignment #####
		
		iFranceChange = 30
		iSpainChange = 20
		
		self.changePlayerAlignment(self.iFrenchID, iFranceChange)
		self.changePlayerAlignment(self.iSpanishID, iSpainChange)
		
		# Set event text
		self.szEventText = localText.getText("TXT_KEY_AMREV_JULY_1776_TEXT", ())
		self.szResultText = localText.getText("TXT_KEY_AMREV_FRANCE_AND_SPAIN_ALIGN", (iFranceChange, iSpainChange,))
		
		self.displayEventText()
		
	# France Recognizes American Indepedence - France Alignment
	def Oct_1777(self):
		
		##### Change Alignment #####
		
		self.changePlayerAlignment(self.iFrenchID, 30)
		
		# Set event text
		self.szEventText = localText.getText("TXT_KEY_AMREV_OCT_1777_TEXT", ())
		self.szResultText = localText.getText("TXT_KEY_AMREV_OCT_1777_RESULT", ())
		
		self.displayEventText()
		
	# Articles of Confederation - Gold and 1 unit
	def Nov_1777(self):
		
		##### Add Gold #####
		
		pPlayer.changeGold(25)
		
		##### Add Unit #####
		
		aiValidCities = [	self.iPHILADELPHIA,
					self.iBALTIMORE	]
		
		iCityID = self.determineValidCities(self.iColonialID, aiValidCities)
		
		# If valid city exists
		if (iCityID > -1):
			szPlayerAdj = pPlayer.getCivilizationAdjective(0)
			
			szCityName = pPlayer.getCity(iCityID).getName()
			
			iUnitType = self.iContinentalRegularID
			szUnitName = localText.getText("TXT_KEY_AMREV_UNIT_CONTINENTAL_REGULAR", ())

			iCityX = pPlayer.getCity(iCityID).getX()
			iCityY = pPlayer.getCity(iCityID).getY()
			
			# Spawn units
			pPlayer.initUnit(iUnitType, iCityX, iCityY, UnitAITypes.UNITAI_ATTACK)
			
		# Set event text
		self.szEventText = localText.getText("TXT_KEY_AMREV_NOV_1777_TEXT", ())
		self.szResultText = localText.getText("TXT_KEY_AMREV_NOV_1777_RESULT", (szCityName))
		
		self.displayEventText()
		
	# Von Steuben's training
	def Feb_1778(self):
		
		# Loop through all Colonial units and find the Continental Regulars
		pPlayer = PyPlayer(self.iColonialID)
		for pUnit in pPlayer.getUnitList():
			
			if (pUnit.getUnitType() == self.iContinentalRegularID):
				
				# Add 5 to 9 XP to every Continental Regular
				iXPBonus = self.getRand(5) + 5
				pUnit.changeExperience(iXPBonus, sys.maxint)
		
		# Set event text
		self.szEventText = localText.getText("TXT_KEY_AMREV_FEB_1778_TEXT", ())
		self.szResultText = localText.getText("TXT_KEY_AMREV_FEB_1778_RESULT", ())
		
		self.displayEventText()
		
	# Peace to Britain
	def Aug_1779(self):
		
		# Set event text
		self.szEventText = localText.getText("TXT_KEY_AMREV_AUG_1779_TEXT", ())
		self.szResultText = ""
		
		self.displayEventText()
		
	# French land 3 units
	def Jul_1780(self):
		
		iXPlot = 26
		iYPlot = 34
	
		aiUnitPlot = self.findUnitPlacementPlot(self.iFrenchID, iXPlot, iYPlot, true, true, 2)
		
		if (aiUnitPlot == "Oh Snap"):
			return
			
		iNumRegulars = 3
		pFrenchPlayer = gc.getPlayer(self.iFrenchID)
		for iUnitLoop in range(iNumRegulars):
			pFrenchPlayer.initUnit(self.iFrenchRegularID, aiUnitPlot[0], aiUnitPlot[1], UnitAITypes.UNITAI_ATTACK)
		
		# Set event text
		self.szEventText = localText.getText("TXT_KEY_AMREV_JUL_1780_TEXT", ())
		self.szResultText = localText.getText("TXT_KEY_AMREV_JUL_1780_RESULT", ())
		
		self.displayEventText()
		
	# Benedict Arnold's Betrayal
	def Aug_1780(self):
		
		iXPlot = 22
		iYPlot = 34
	
		aiUnitPlot = self.findUnitPlacementPlot(self.iBritishID, iXPlot, iYPlot, true, true, 2)
		
		if (aiUnitPlot == "Oh Snap"):
			return
			
		pBritishPlayer = gc.getPlayer(self.iBritishID)
		pBritishPlayer.initUnit(self.iBritishRegularID, aiUnitPlot[0], aiUnitPlot[1], UnitAITypes.UNITAI_ATTACK)
		
		# Set event text
		self.szEventText = localText.getText("TXT_KEY_AMREV_AUG_1780_TEXT", ())
		self.szResultText = localText.getText("TXT_KEY_AMREV_AUG_1780_RESULT", ())
		
		self.displayEventText()
		
	# French navy Appears
	def Aug_1781(self):
		
		iXPlot = 24
		iYPlot = 26
	
		aiUnitPlot = self.findUnitPlacementPlot(self.iFrenchID, iXPlot, iYPlot, false, true, 2)
		
		if (aiUnitPlot == "Oh Snap"):
			return
			
		pFrenchPlayer = gc.getPlayer(self.iFrenchID)
		iNumShipsOfTheLine = 2
		for iUnitLoop in range(iNumShipsOfTheLine):
			pFrenchPlayer.initUnit(self.iShipOfTheLineID, aiUnitPlot[0], aiUnitPlot[1], UnitAITypes.UNITAI_ATTACK_SEA)
		iNumFrigates = 6
		for iUnitLoop in range(iNumFrigates):
			pFrenchPlayer.initUnit(self.iFrigateID, aiUnitPlot[0], aiUnitPlot[1], UnitAITypes.UNITAI_ATTACK_SEA)
		
		# Set event text
		self.szEventText = localText.getText("TXT_KEY_AMREV_AUG_1781_TEXT", ())
		self.szResultText = localText.getText("TXT_KEY_AMREV_AUG_1781_RESULT", ())
		
		self.displayEventText()
		
###########################################################################################
#################################### UTILITY FUNCTIONS ####################################
###########################################################################################
		
	def getRand(self, iNum):
		
		return CyGame().getSorenRandNum(iNum, "AmRevScenario")
		
	def getScore(self, iPlayerID):
		
		iPopScore = 0
		iVPScore = 0
		iBonusScore = 0
		iUnitScore = 0
		
		# Loop through all players' cities
		pPlayer = PyPlayer(iPlayerID)
		apCityList = pPlayer.getCityList()
		
		for pCity in apCityList:
			
			# Add city all city sizes to score
			iPopScore += pCity.getPopulation()
			
#			iCityID = pCity.getID()
			iCityID = self.getCityIDFromPyPointer(pCity)
			
			# If this is a special city, add more to the score
			if (iCityID == self.iBOSTON or
			    iCityID == self.iNEW_YORK_CITY or
			    iCityID == self.iPHILADELPHIA or
			    iCityID == self.iRICHMOND or
			    iCityID == self.iCHARLESTON or
			    
			    iCityID == self.iMONTREAL or
			    iCityID == self.iQUEBEC or
			    iCityID == self.iHALIFAX):
				
				iVPScore += 15
		
		# Per-player modifiers
		if (iPlayerID == self.iBritishID):
			
			# Bonus for being British
			iBonusScore += 50
			
			pColonialPlayer = PyPlayer(self.iColonialID)
			apUnitList = pColonialPlayer.getUnitList()
			
			# Loop through all Colonial units
			for pUnit in apUnitList:
				if (pUnit.baseCombatStr() > 0):
					
					# British lose one point for every Colonial military unit on the map
					iUnitScore -= 1
					
		print("Player %d Score: %d, %d, %d, %d" %(iPlayerID, iPopScore, iVPScore, iBonusScore, iUnitScore))
		return (iPopScore + iVPScore + iBonusScore + iUnitScore)
		
	def determineValidCities(self, iPlayerID, aiValidCities):
		
		pPlayer = PyPlayer(iPlayerID)
		
		# Loop through Player's cities and see if there are any valid ones
		
		for iValidCity in aiValidCities:
			
			apCityList = pPlayer.getCityList()
			for pCity in apCityList:
				iCityID = pCity.getID()
				
				if (self.getCityIDFromPyPointer(pCity) == iValidCity):
					
					return iCityID
					
		return -1
		
	def findUnitPlacementPlot(self, iPlayerID, iPlotX, iPlotY, bLand = true, bIncludePlot = true, iRange = 3):
		
		aTHEPlot = []
		aiPossiblePlots = []
		iNumPossiblePlots = 0
		aiTempPlotHolder = []
		
		pThisPlayer = gc.getPlayer(iPlayerID)
		pThisTeam = gc.getTeam(pThisPlayer.getTeam())
		
		# Loop through plots in usable range
		for iXLoop in range(iPlotX - iRange, iPlotX + iRange):
			for iYLoop in range(iPlotY - iRange, iPlotY + iRange):
				
				# Map bounds
				if (iXLoop >= 0 and iXLoop < CyMap().getGridWidth() and iYLoop >= 0 and iYLoop < CyMap().getGridHeight()):
					
					# Check to see if center plot should be excluded
					if (bIncludePlot or (not bIncludePlot and (iXLoop != iPlotX) and (iYLoop != iPlotY))):
						
						# Don't include enemy city plots!
						pPlot = CyMap().plot(iXLoop, iYLoop)
						if (pPlot.isEnemyCity(pThisPlayer.getTeam()) == false):
							
							# Check whether plot type is available
							if ((bLand == true and CyMap().plot(iXLoop, iYLoop).isWater() == false) or \
								(bLand == false and CyMap().plot(iXLoop, iYLoop).isWater() == true)):
								aiTempPlotHolder = [iXLoop, iYLoop]
								aiPossiblePlots.append(aiTempPlotHolder)
								iNumPossiblePlots += 1
					
		if (iNumPossiblePlots == 0):
			return "Oh Snap"
		
		# Now that our list of possible plots is made, we pick one of them randomly and shove aside any enemy units already there
		iChosenPlot = self.getRand(iNumPossiblePlots - 1)
		aTHEPlot = aiPossiblePlots[iChosenPlot]
		
		# Check to see if there are any other units already on this plot
		pPlot = CyMap().plot(aTHEPlot[0], aTHEPlot[1])
		
		if (pPlot.getNumUnits() > 0):
			
			bEnemiesPresent = true
			
			while(pPlot.getNumUnits() > 0 and bEnemiesPresent):
#				print("Test0")
				pLoopUnit = pPlot.getUnit(0)
				pUnitOwner = gc.getPlayer(pLoopUnit.getOwner())
				
				if (pUnitOwner):
					# Check to see if this unit belongs to a player that 'our' player is at war with
					if (pThisTeam.isAtWar(pUnitOwner.getTeam())):
						# Move this enemy unit
						self.moveUnitAside(pLoopUnit)
					else:
						# If it's a friendly, don't move it!
						bEnemiesPresent = false
		
		return aTHEPlot
		
	def moveUnitAside(self, pUnitToMove):
		
		iUnitX = pUnitToMove.getX()
		iUnitY = pUnitToMove.getY()
		
		# Don't look further than 10 plots away
		iMaxRange = 10
		iRing = 1
		
		aaiTestedList = [iUnitX, iUnitY]
		
		pPlayer = gc.getPlayer(pUnitToMove.getOwner())
		pTeam = gc.getTeam(pPlayer.getTeam())
		
		# Loop in rings around the unit's plot until we find another plot to move this unit to
		while (iRing < iMaxRange):
#			print("Test0")
			
			aiTempList = []
			aaiToTestList = []
			iNumToTest = 0
			aaiValidPlotList = []
			iNumValid = 0
			
			# Find plots in this ring range
			for iX in range(-iRing, iRing + 1):
				for iY in range(-iRing, iRing + 1):
					aiTempList = [iX + iUnitX, iY + iUnitY]
					
					# Don't test this plot more than once
					if (aiTempList not in aaiTestedList):
						
						pPlot = CyMap().plot(aiTempList[0], aiTempList[1])
						bValidPlot = false
						
						if (pPlot.isWater() and pUnitToMove.getDomainType() == DomainTypes.DOMAIN_SEA):
							bValidPlot = true
						elif (pPlot.isWater() == false):
							if (pUnitToMove.getDomainType() == DomainTypes.DOMAIN_LAND or pUnitToMove.getDomainType() == DomainTypes.DOMAIN_AIR):
								bValidPlot = true
						
						# Make sure this unit can move to this plot type (no land units on water, etc.)
						if (bValidPlot):
							aaiToTestList.append(aiTempList)
							iNumToTest += 1
					
			# Now test these plots
			for iTestLoop in range(iNumToTest):
				
				pPlot = CyMap().plot(iUnitX, iUnitY)
				
				iX = aaiToTestList[iTestLoop][0]
				iY = aaiToTestList[iTestLoop][1]
				
				# If there are no enemy units here then add to the final valid plot list
				if (not self.isEnemyUnits(pTeam, iX, iY)):
					
					aaiValidPlotList.append(aaiToTestList[iTestLoop])
					iNumValid += 1
					
				# Add this plot to the tested list (to prevent it being looked at again) and look at the next in this ring
				aaiTestedList.append(aaiToTestList[iTestLoop])
				
			# This ring has been iterated through and placed in a final list - now pick a random plot from that list and exit the function
			
			if (iNumValid > 0):
#				print(aaiValidPlotList)
				iChosenPlot = self.getRand(iNumValid - 1)
				
				iX = aaiValidPlotList[iChosenPlot][0]
				iY = aaiValidPlotList[iChosenPlot][1]
				
				pUnitToMove.setXY(iX, iY)
				
				return
				
			# None of the plots in this ring are valid, so time to try the next ring
			
			iRing += 1
		
	def isEnemyUnits(self, pThisTeam, iPlotX, iPlotY):
		
		# Check to see if there are any other units already on this plot
		pPlot = CyMap().plot(iPlotX, iPlotY)
		
		if (pPlot.getNumUnits() > 0):
			
			for iUnitLoop in range(pPlot.getNumUnits()):
				
				pLoopUnit = pPlot.getUnit(iUnitLoop)
				
				pUnitOwner = gc.getPlayer(pLoopUnit.getOwner())
				
				# Check to see if this unit belongs to a player that 'our' player is at war with
				if (pThisTeam.isAtWar(pUnitOwner.getTeam())):
					return true
		
		return false
		
	def initUnit(self, pUnit):
		
#		print("Init-ing Unit")
		
		# Militia have a [self.iMilitiaDisbandCounter] turn counter
		aScriptData = [-1]
		
		pUnit.setScriptData(pickle.dumps(aScriptData))
	
#	def getCityList(self, iPlayer):
#		
#		lCity = []
#		(loopCity, iter) = self.player.firstCity(false)
#		while(loopCity):
#			cityOwner = loopCity.getOwner()
#			if ( not loopCity.isNone() and loopCity.getOwner() == self.getID() ): #only valid cities
#				city = PyCity( self.getID(), loopCity.getID() )
#				lCity.append(city)
#			(loopCity, iter) = self.player.nextCity(iter, false)
#		return lCity
		
###### CITY SCRIPT DATA ######
		
	def getCityID(self, iPlayer, iCity):
		
		pPlayer = gc.getPlayer(iPlayer)
		pCity = pPlayer.getCity(iCity)
		
		# Load Script Data - CityID
		szScriptData = pickle.loads(pCity.getScriptData())
		iCityID = szScriptData[0]
		
		return iCityID
		
	def setCityID(self, iPlayer, iCity, iValue):
		
		pPlayer = gc.getPlayer(iPlayer)
		pCity = pPlayer.getCity(iCity)
		
		# Load Script Data - City ID
		szScriptData = pickle.loads(pCity.getScriptData())
		iSpawnUnitCounter = szScriptData[1]
		
		# Save Script Data - City ID
		szScriptData = [iValue, iSpawnUnitCounter]
		pCity.setScriptData(pickle.dumps(szScriptData))
	
	def getCityIDFromPyPointer(self, pCity):
		
		# Load Script Data - CityID
		szScriptData = pickle.loads(pCity.getScriptData())
		iCityID = szScriptData[0]
		
		return iCityID
		
	def getCitySpawnUnitCounter(self, iPlayer, iCity):
		
		pPlayer = gc.getPlayer(iPlayer)
		pCity = pPlayer.getCity(iCity)
		
		# Load Script Data - SpawnUnitCounter
		szScriptData = pickle.loads(pCity.getScriptData())
		iSpawnUnitCounter = szScriptData[1]
		
		return iSpawnUnitCounter
		
	def setCitySpawnUnitCounter(self, iPlayer, iCity, iValue):
		
		pPlayer = gc.getPlayer(iPlayer)
		pCity = pPlayer.getCity(iCity)
		
		# Load Script Data - SpawnUnitCounter
		szScriptData = pickle.loads(pCity.getScriptData())
		iCityID = szScriptData[0]
		
		# Save Script Data - SpawnUnitCounter
		szScriptData = [iCityID, iValue]
		pCity.setScriptData(pickle.dumps(szScriptData))
		
	def changeCitySpawnUnitCounter(self, iPlayer, iCity, iChange):
		
		pPlayer = gc.getPlayer(iPlayer)
		pCity = pPlayer.getCity(iCity)
		
		# Load Script Data - SpawnUnitCounter
		szScriptData = pickle.loads(pCity.getScriptData())
		iCityID = szScriptData[0]
		iSpawnUnitCounter = szScriptData[1]
		
		iSpawnUnitCounter += iChange
		
		# Save Script Data - SpawnUnitCounter
		szScriptData = [iCityID, iSpawnUnitCounter]
		pCity.setScriptData(pickle.dumps(szScriptData))
		
###### UNIT SCRIPT DATA ######
		
	def getUnitDisbandCounter(self, iPlayer, iUnit):
		
		pPlayer = gc.getPlayer(iPlayer)
		pUnit = pPlayer.getUnit(iUnit)
		
		# Load Script Data - UnitDisbandCounter
		szScriptData = pickle.loads(pUnit.getScriptData())
		iUnitDisbandCounter = szScriptData[0]
		
		return iUnitDisbandCounter
	
	def setUnitDisbandCounter(self, iPlayer, iUnit, iValue):
		
		pPlayer = gc.getPlayer(iPlayer)
		pUnit = pPlayer.getUnit(iUnit)
		
		# Save Script Data - UnitDisbandCounter
		szScriptData = [iValue]
		pUnit.setScriptData(pickle.dumps(szScriptData))
		
	def changeUnitDisbandCounter(self, iPlayer, iUnit, iChange):
		
		pPlayer = gc.getPlayer(iPlayer)
		pUnit = pPlayer.getUnit(iUnit)
		
		# Load Script Data - UnitDisbandCounter
		szScriptData = [-1]
		# This should only return false when adding units via debug (when not built)
#		if (pUnit.getScriptData()):		NEVERMIND
#		print("About to unpickle: %s" %(pUnit.getScriptData()))
		szScriptData = pickle.loads(pUnit.getScriptData())
		iUnitDisbandCounter = szScriptData[0]
		
		iUnitDisbandCounter += iChange
		
		# Save Script Data - UnitDisbandCounter
		szScriptData[0] = iUnitDisbandCounter
		pUnit.setScriptData(pickle.dumps(szScriptData))
		
###### PLAYER SCRIPT DATA ######
		
	def getPlayerAlignment(self, iPlayer):
		
		pPlayer = gc.getPlayer(iPlayer)
		
		# Load Script Data - Alignment
		szScriptData = pickle.loads(pPlayer.getScriptData())
		iAlignment = szScriptData[0]
		
		return iAlignment
		
	def setPlayerAlignment(self, iPlayer, iValue):
		
		pPlayer = gc.getPlayer(iPlayer)
		
		# Save Script Data - Alignment
		szScriptData = [iValue]
		pPlayer.setScriptData(pickle.dumps(szScriptData))
		
	def changePlayerAlignment(self, iPlayer, iChange):
		
		pPlayer = gc.getPlayer(iPlayer)
		
		# Load Script Data - Alignment
		szScriptData = pickle.loads(pPlayer.getScriptData())
		iAlignment = szScriptData[0]
		
		iAlignment += iChange
		
		# Save Script Data - Alignment
		szScriptData[0] = iAlignment
		pPlayer.setScriptData(pickle.dumps(szScriptData))
		
	### EVENTS ###
		
	def displayEventText(self):
		
		if (gc.getPlayer(CyGame().getActivePlayer()).isAlive()):
			
			szTitle = self.szGameDate = CyGameTextMgr().getTimeStr(CyGame().getGameTurn(), false)
			
			popup = PyPopup.PyPopup(-1)
			popup.setHeaderString(szTitle)
			popup.setBodyString(self.szEventText + "\n\n" + self.szResultText)
			popup.launch(true, PopupStates.POPUPSTATE_QUEUED)
		
	def addPopup(self, szText):
		
		szTitle = self.szGameDate = CyGameTextMgr().getTimeStr(CyGame().getGameTurn(), false)
		
		popup = PyPopup.PyPopup(-1)
		popup.setHeaderString(szTitle)
		popup.setBodyString(szText)
		popup.launch(true, PopupStates.POPUPSTATE_QUEUED)
		
###########################################################################################
##################################### EVENT OVERRIDES #####################################
###########################################################################################
	
	def onLoadGame(self, argsList):
		'Called when game is loaded'
		
		self.initValues()
	
	def onGameStart(self, argsList):
		'Called at the start of the game'
		
		self.setupGame()
		
		for iPlayer in range(gc.getMAX_PLAYERS()):
			player = gc.getPlayer(iPlayer)
			if (player.isAlive() and player.isHuman()):
				popupInfo = CyPopupInfo()
				popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON_SCREEN)
				popupInfo.setText(u"showDawnOfMan")
				popupInfo.addPopup(iPlayer)
		
	def onBeginGameTurn(self, argsList):
		'Called at the beginning of the end of each turn'
		iGameTurn = argsList[0]
		
		# American Revolution events
		self.turnChecker(iGameTurn)
		
	def onUnitMove(self, argsList):
		'unit move'
		
		pPlot,pUnit = argsList
		player = PyPlayer(pUnit.getOwner())
		unitInfo = PyInfo.UnitInfo(pUnit.getUnitType())
		if player and unitInfo:
#			CvUtil.pyPrint('Player %d Civilization %s unit %s is moving to %d, %d' 
#				%(player.getID(), player.getCivilizationName(), unitInfo.getDescription(), 
#				pUnit.getX(), pUnit.getY()))
			
			# Possible spawning of units whenever a unit moves near a city
			self.checkForUnitSpawning(player.getID(), pUnit.getX(), pUnit.getY(), pUnit.getDomainType())

	def onUnitBuilt(self, argsList):
		'Unit Completed'
		
		city = argsList[0]
		unit = argsList[1]
		player = PyPlayer(city.getOwner())
		
#		CvUtil.pyPrint('%s was finished by Player %d Civilization %s' 
#			%(PyInfo.UnitInfo(unit.getUnitType()).getDescription(), player.getID(), player.getCivilizationName()))
		
		# Set unit ScriptData - unit disband counter
		self.initUnit(unit)
		
	def onUnitCreated(self, argsList):
		'Unit Completed'
		
		unit = argsList[0]
		iOwner = unit.getOwner()
		player = PyPlayer(iOwner)
		
#		CvUtil.pyPrint('%s was created for Player %d Civilization %s' 
#			%(PyInfo.UnitInfo(unit.getUnitType()).getDescription(), player.getID(), player.getCivilizationName()))
		
		# Set unit ScriptData - unit disband counter
		self.initUnit(unit)

	def onUnitLost(self, argsList):
		'Unit Lost'
		
		unit = argsList[0]
		player = PyPlayer(unit.getOwner())
#		CvUtil.pyPrint('%s was lost by Player %d Civilization %s' 
#			%(PyInfo.UnitInfo(unit.getUnitType()).getDescription(), player.getID(), player.getCivilizationName()))
		
		# Modify alignment by 4-6 for the French and Spanish for each British unit killed
		if (player.getID() == self.iBritishID):
			self.changePlayerAlignment(self.iSpanishID, 4 + self.getRand(2))
			self.changePlayerAlignment(self.iFrenchID, 4 + self.getRand(2))
			
	def onCityAcquired(self, argsList):
		'City Acquired'
		
		owner,playerType,city,bConquest,bTrade = argsList
#		CvUtil.pyPrint('City Acquired Event: %s' %(city.getName()))
		
		self.initCity(city)
		
		# Save Script Data - SpawnUnitCounter
#		szScriptData = [0]
#		city.setScriptData(pickle.dumps(szScriptData))
		
	def onCityLost(self, argsList):
		'City Lost'
		
		city = argsList[0]
		player = PyPlayer(city.getOwner())
#		CvUtil.pyPrint('City %s was lost by Player %d Civilization %s' 
#			%(city.getName(), player.getID(), player.getCivilizationName()))
		
		# Modify alignment by 18-22 for the French and Spanish for each British city lost
		if (player.getID() == self.iBritishID):
			self.changePlayerAlignment(self.iSpanishID, 18 + self.getRand(4))
			self.changePlayerAlignment(self.iFrenchID, 18 + self.getRand(4))
