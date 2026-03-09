# Charlemagne Scenario
# Civilization 4 (c) 2007 Firaxis Games

# Programming by -	Jon 'Trip' Shafer


# NOTES ON MODIFYING VALUES:
	# Search for the strings inside the quotes to find locations where stuff can be changed

# The "getTurnFavorWithRome" function determines how much Rome likes a civ and why; calculated ~ every turn
# "RomePermFavor": Something a player does which permanently alters his favor with Rome
# "FavorEffect": Some effect given based upon what the player's favor with Rome is
# The "doHighestFavorRandomUnit" function determines who gets a free unit and with what odds

# The amount of Permanent Favor Points a player starts with
g_iDefaultPermanentFavorWithRome = 0

# The amount of default "per Turn" favor is defined here
g_iDefaultPerTurnFavor = 55

# This is multiplied by the Pope's favorite civ's favor to get the odds of that Civ getting a free Papal Pikeman (out of 100... e.g. Favor of 60 * 0.25 = 15 out of 100 each turn)
g_iFreeUnitFavorMultiplier = 0.1

# Anyone at or below this level of favor is excommunicated (interface)
g_iExcommunciatedValue = 10

# Amount of favor given automatically when someone becomes the HRE
g_iHREFavorBonus = 10

# Favor: Multiplied by the Production cost of unit gifted to the pope (e.g. 40 prod unit would give (40 * 0.05 =) +2 Favor)
g_iPapalGiftProductionFactor = 0.025

# Amount of favor Pope gives you for spreading Islam in a city
g_iSpreadIslamRomeFavor = -2

# % Chance of a Relic showing up on the map each turn: 1 = 1%, 15 = 15%, etc.
g_iRelicAppearanceChance = 1

# Amount of favor given when player gifts a Relic unit to Rome
g_iRelicFavorBonus = 15

# If this is set to "1" when someone becomes the HRE it ends the game
g_bHREEndsGame = 1
#g_iVictoryType defines which victory the player wins at: default is 0, which I think is conquest... see the victory XML for details
g_iVictoryType = 0


# Favor Levels
g_iFavorLevel_SpawnOfSatan = 0
g_iFavorLevel_Excommunicated = 10
g_iFavorLevel_Apostate = 20
g_iFavorLevel_Heathen = 30
g_iFavorLevel_Heretic = 40
g_iFavorLevel_Fallen = 50
g_iFavorLevel_Believer = 60
g_iFavorLevel_TrueBeliever = 80
g_iFavorLevel_Protector = 100
g_iFavorLevel_Blessed = 150

g_aiFavorLevels = [
	g_iFavorLevel_SpawnOfSatan,
	g_iFavorLevel_Excommunicated,
	g_iFavorLevel_Apostate,
	g_iFavorLevel_Heathen,
	g_iFavorLevel_Heretic,
	g_iFavorLevel_Fallen,
	g_iFavorLevel_Believer,
	g_iFavorLevel_TrueBeliever,
	g_iFavorLevel_Protector,
	g_iFavorLevel_Blessed
	]

g_aiFavorLevelsDict = {
	"Spawn of Satan" : g_iFavorLevel_SpawnOfSatan,
	"Excommunicated" : g_iFavorLevel_Excommunicated,
	"Apostate" : g_iFavorLevel_Apostate,
	"Heathen" : g_iFavorLevel_Heathen,
	"Heretic" : g_iFavorLevel_Heretic,
	"Fallen" : g_iFavorLevel_Fallen,
	"Believer" : g_iFavorLevel_Believer,
	"True Believer" : g_iFavorLevel_TrueBeliever,
	"Protector" : g_iFavorLevel_Protector,
	"Blessed" : g_iFavorLevel_Blessed
	}

def getFavorFromString(szString):
	return g_aiFavorLevelsDict[szString]

from CvPythonExtensions import *
import sys
import Popup as PyPopup
from PyHelpers import PyPlayer
import pickle
import CvEventManager
from CvScreenEnums import *
from PyHelpers import *
import CvUtil
import CvGameUtils

import CvScreensInterface

# globals
gc = CyGlobalContext()
localText = CyTranslator()

DefaultUnitAI = UnitAITypes.NO_UNITAI


class CvCharlemagneEvents(CvEventManager.CvEventManager):
	
	def __init__(self):
		
		self.parent = CvEventManager.CvEventManager
		self.parent.__init__(self)
		
		# Amount of happiness Christian cities get if the civ is not at war with Rome's enemies
		self.iNoWarHappyPenalty = -2
		# Happiness penalty to Christian civs if Rome is controlled by a non-Roman power
		self.iForeignRomeHappyPenalty = 2
		
		self.m_iExcommunicatedValue = g_iExcommunciatedValue
		
		# NetMessage ID #s
		self.m_iNetMessage_Inquisitor = 0

	def onModNetMessage(self, argsList):
		'Called whenever CyMessageControl().sendModNetMessage() is called - this is all for you modders!'
		iData1, iData2, iData3, iData4, iData5 = argsList
		
		iMessageID = iData1
		
		# Inquisitor's effect on a city
		if (iMessageID == self.m_iNetMessage_Inquisitor):
			
			iPlotX = iData2
			iPlotY = iData3
			iOwner = iData4
			iUnitID = iData5
			
			pPlot = CyMap().plot(iPlotX, iPlotY)
			pCity = pPlot.getPlotCity()
			
			pPlayer = gc.getPlayer(iOwner)
			pUnit = pPlayer.getUnit(iUnitID)
			
			iStateReligion = -1
			if (pPlayer.getStateReligion() != -1):
				iStateReligion = pPlayer.getStateReligion()
			
			# Loop through all religions, remove them from the city
			for iReligionLoop in range(gc.getNumReligionInfos()):
				if (iReligionLoop != iStateReligion):
					pCity.setHasReligion(iReligionLoop, 0, 0, 0)
			
			# Unit expended
			pUnit.kill(0, -1)
			
		
	def initValues(self):
		
		##### Civs #####
		
		self.iCivRomeID = CvUtil.findInfoTypeNum(gc.getCivilizationInfo,gc.getNumCivilizationInfos(),'CIVILIZATION_HOLY_ROME')
		self.iRomePlayerID = -1
		for iPlayerLoop in range(gc.getMAX_CIV_PLAYERS()):
			if (gc.getPlayer(iPlayerLoop).getCivilizationType() == self.iCivRomeID):
				self.iRomePlayerID = iPlayerLoop
		pPlayer = gc.getPlayer(self.iRomePlayerID)
		self.iRomeTeamID = pPlayer.getTeam()
		
		self.iCivArabiaID = CvUtil.findInfoTypeNum(gc.getCivilizationInfo,gc.getNumCivilizationInfos(),'CIVILIZATION_ARABIA')
		self.iArabiaPlayerID = -1
		for iPlayerLoop in range(gc.getMAX_CIV_PLAYERS()):
			if (gc.getPlayer(iPlayerLoop).getCivilizationType() == self.iCivArabiaID):
				self.iArabiaPlayerID = iPlayerLoop
		pPlayer = gc.getPlayer(self.iArabiaPlayerID)
		self.iArabiaTeamID = pPlayer.getTeam()
		
		##### Religions #####
		
		self.iReligionChristianityID = CvUtil.findInfoTypeNum(gc.getReligionInfo,gc.getNumReligionInfos(),'RELIGION_CHRISTIANITY')
		self.iReligionIslamID = CvUtil.findInfoTypeNum(gc.getReligionInfo,gc.getNumReligionInfos(),'RELIGION_ISLAM')
		
	def onLoadGame(self, argsList):
		
		self.parent.onLoadGame(self, argsList)
		
		self.initValues()
		
	def onGameStart(self, argsList):
		'Called at the start of the game'
		
		self.parent.onGameStart(self, argsList)
		
		self.initValues()
		
		##### Loop through all players #####
		for iPlayerLoop in range(gc.getMAX_PLAYERS()):
			
			self.initPlayer(iPlayerLoop)
			self.updateFavorWithRomeEffects(iPlayerLoop)
			
#			self.setPlayerOldFavorLevel(iPlayerLoop, self.getPlayerFavorLevel(iPlayerLoop))			
			
			
############################################################################################
#		Per-Turn stuff
############################################################################################



	def onEndGameTurn(self, argsList):
		'Called at the end of the end of each turn'
		iGameTurn = argsList[0]
		
		##### Loop through all players #####
		for iPlayerLoop in range(gc.getMAX_CIV_PLAYERS()):
			
			pPlayer = gc.getPlayer(iPlayerLoop)
			
			self.updateFavorWithRomeEffects(iPlayerLoop)
			
			# Popup for new favor level
			if (iPlayerLoop <= 4):		# Only for first 5 Christian civs
				
				iFavorLevel = self.getPlayerFavorLevel(iPlayerLoop)
				
				if (iFavorLevel != self.getPlayerOldFavorLevel(iPlayerLoop)):
					self.setPlayerOldFavorLevel(iPlayerLoop, iFavorLevel)
					szTitle = localText.getText("TXT_KEY_CHARL_NEW_FAVOR_LEVEL_TITLE", ())
					szString = localText.getText("TXT_KEY_CHARL_NEW_FAVOR_LEVEL", (pPlayer.getName(), self.getPlayerFavorLevel(iPlayerLoop, true)))
#					szString = "%s is now considered %s by His Holiness in Rome" %(pPlayer.getName(), self.getPlayerFavorLevel(iPlayerLoop, true))
					
					if (CyGame().getElapsedGameTurns() > 0):
						
						self.addPopup(szTitle, szString)
						
						# HRE Screen :)
						if (iFavorLevel == 10):
							
							# Add 10 favor automatically
							self.changePlayerPermanentFavorWithRome(iPlayerLoop, g_iHREFavorBonus)
							
							argsList = ["Lose Screen"]
							
							if (iPlayerLoop == CyGame().getActivePlayer()):
								argsList = ["Win Screen"]
							
							CvScreensInterface.showCharlemagneScreen(argsList)
							
							# Win?
							if (g_bHREEndsGame == 1):
								
								pPlayer = gc.getPlayer(iPlayerLoop)
								iTeam = pPlayer.getTeam()
								CyGame().setWinner(iTeam, g_iVictoryType)
								
		self.doHighestFavorRandomUnit()
		
		# Relic appearance
		self.doRelicAppearance()
		
	def doRelicAppearance(self):
		
#		print("\n\n\n\n\nSeeing if relic should appear:\n")
		
		iRelicID = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_RELIC')
		
		# Loop through all units in the game, make sure no relic exists already
		for iPlayerLoop in range(gc.getMAX_CIV_PLAYERS()):
			pPlayer = gc.getPlayer(iPlayerLoop)
			pyPlayer = PyPlayer(iPlayerLoop)
			
			if (pPlayer.isAlive()):
				
				# Loop through all units
				apUnitList = pyPlayer.getUnitList()
				for pUnitLoop in apUnitList:
					
					# If we already have a relic, quit, we're done
					if (pUnitLoop.getUnitType() == iRelicID):
						return
		
		# Roll to see if relic appears
		iRoll = CyGame().getSorenRandNum(100, "Rolling to see if relic appears")
		
#		print("Roll is: %d, Must be < %s" %(iRoll, g_iRelicAppearanceChance))
		
		if (iRoll < g_iRelicAppearanceChance):
			
#			print("Relic should appear")
			
			# Relic should appear, now find random city that's not Rome
			apRelicCityList = []
			
			for iPlayerLoop in range(gc.getMAX_CIV_PLAYERS()):
				pPlayer = gc.getPlayer(iPlayerLoop)
				pyPlayer = PyPlayer(iPlayerLoop)
				
				if (pPlayer.isAlive()):
					
					# Loop through all Cities
					apCityList = pyPlayer.getCityList()
					for pyCity in apCityList:
						
						pCity = pyCity.GetCy()
						
						# Don't add Rome
						if (pCity.getX() != 22 or pCity.getY() != 14):
							
							apRelicCityList.append(pCity)
			
			# We have our list, now pick one of the cities at random
			
#			print("Possible Cities:")
#			print(apRelicCityList)
			
			iNumCities = len(apRelicCityList)
			
			iRoll = CyGame().getSorenRandNum(iNumCities, "Picking city to spawn Relic in")
			
			pChosenCity = apRelicCityList[iRoll]
			
#			print("Chosen city: %s" %(pChosenCity.getName()))
			
			iX = pChosenCity.getX()
			iY = pChosenCity.getY()
			iOwner = pChosenCity.getOwner()
			pPlayer = gc.getPlayer(iOwner)
			pCivInfo = gc.getCivilizationInfo(pPlayer.getCivilizationType())
			
			pPlayer.initUnit(iRelicID, iX, iY, DefaultUnitAI, DirectionTypes.NO_DIRECTION)
			
			# Show popup & interface junk to announce this glorious business to the world
			szTitle = localText.getText("TXT_KEY_CHARL_RELIC_APPEARS_TITLE", ())
			szText = localText.getText("TXT_KEY_CHARL_RELIC_APPEARS", (pCivInfo.getAdjective(0), pChosenCity.getName()))
			self.addPopup(szTitle, szText)
			
			szButton = gc.getUnitInfo(iRelicID).getButton()
			for iPlayerLoop in range(gc.getMAX_CIV_PLAYERS()):
				if gc.getPlayer(iPlayerLoop).isAlive():
					CyInterface().addMessage(iPlayerLoop, False, gc.getEVENT_MESSAGE_TIME(), szTitle, "AS2D_DISCOVERBONUS", InterfaceMessageTypes.MESSAGE_TYPE_MINOR_EVENT, szButton, gc.getInfoTypeForString("COLOR_GREEN"), iX, iY, True, True)	
			
##############################################
		
	def addPopup(self, szTitle, szText, bImmediate=false):
		
		# Don't display popups for autoplay games
		if (CyGame().getActivePlayer() != -1 and gc.getPlayer(CyGame().getActivePlayer()).isAlive()):
			
			popup = PyPopup.PyPopup(-1)
			popup.setHeaderString(szTitle)
			popup.setBodyString(szText)
			
			iState = PopupStates.POPUPSTATE_QUEUED
			
			if (bImmediate):
				iState = PopupStates.POPUPSTATE_IMMEDIATE
			
			popup.launch(true, iState)
		
##############################################
	
	def getPlayerFavorLevel(self, iPlayerID, bString=false):
		
		iFavor = self.getPlayerTotalFavorWithRome(iPlayerID)
		
		if (iFavor <= getFavorFromString("Spawn of Satan")):
			if (bString):
				return localText.getText("TXT_KEY_CHARL_TITLE_SATAN", ())
#				return "The Spawn of Satan"
			return 0
		elif (iFavor <= getFavorFromString("Excommunicated")):
			if (bString):
				return localText.getText("TXT_KEY_CHARL_TITLE_EXCOM", ())
#				return "Excommunicated"
			return 1
		elif (iFavor <= getFavorFromString("Apostate")):
			if (bString):
				return localText.getText("TXT_KEY_CHARL_TITLE_APOSTATE", ())
#				return "An Apostate"
			return 2
		elif (iFavor <= getFavorFromString("Heathen")):
			if (bString):
				return localText.getText("TXT_KEY_CHARL_TITLE_HEATHEN", ())
#				return "A Heathen"
			return 3
		elif (iFavor <= getFavorFromString("Heretic")):
			if (bString):
				return localText.getText("TXT_KEY_CHARL_TITLE_HERETIC", ())
#				return "A Heretic"
			return 4
		elif (iFavor <= getFavorFromString("Fallen")):
			if (bString):
				return localText.getText("TXT_KEY_CHARL_TITLE_FALLEN", ())
#				return "Fallen from the Righteous Path"
			return 5
		elif (iFavor <= getFavorFromString("Believer")):
			if (bString):
				return localText.getText("TXT_KEY_CHARL_TITLE_BELIEVER", ())
#				return "A Believer"
			return 6
		elif (iFavor <= getFavorFromString("True Believer")):
			if (bString):
				return localText.getText("TXT_KEY_CHARL_TITLE_TRUE_BELIEVER", ())
#				return "A True Believer"
			return 7
		elif (iFavor <= getFavorFromString("Protector")):
			if (bString):
				return localText.getText("TXT_KEY_CHARL_TITLE_PROTECTOR", ())
#				return "A Protector of the Faith"
			return 8
		elif (iFavor <= getFavorFromString("Blessed")):
			if (bString):
				return localText.getText("TXT_KEY_CHARL_TITLE_BLESSED", ())
#				return "Blessed by God"
			return 9
		elif (iFavor > getFavorFromString("Blessed") and self.isHolyRomanEmperor(iPlayerID)):
			if (bString):
				return localText.getText("TXT_KEY_CHARL_TITLE_HRE", ())
#				return "Holy Roman Emperor"
			return 10
		
		return -1
			
##############################################
		
	def onEndPlayerTurn(self, argsList):
		'Called at the end of a players turn'
		
		self.parent.onEndPlayerTurn(self, argsList)
		
		iGameTurn, iPlayer = argsList
		
		# XXX - Temporary Measure for Debugging/Reloading
		self.initValues()

##############################################
		
	def updateFavorWithRomeEffects(self, iPlayerID):
		
		pRomePlayer = gc.getPlayer(self.iRomePlayerID)
		pRomeTeam = gc.getTeam(pRomePlayer.getTeam())
		
		pPlayer = gc.getPlayer(iPlayerID)
		iTeam = pPlayer.getTeam()
		pTeam = gc.getTeam(iTeam)
		
		# See what players Rome is at war with
		aiRomeTeamWarList = []
		for iTeamLoop in range(gc.getMAX_CIV_TEAMS()):
			if (pRomeTeam.isAtWar(iTeamLoop)):
				aiRomeTeamWarList.append(iTeamLoop)
		
		# Effects for Christian Civs
		########################################
		if (pPlayer.getStateReligion() == self.iReligionChristianityID):
			
			bWarHappinessPenalty = false
			
			# See if active, Christian player is at war with all of Rome's enemies, if not, Happiness penalty for him...
			for iWarTeamLoop in aiRomeTeamWarList:
				if (not pTeam.isAtWar(iWarTeamLoop)):
					bWarHappinessPenalty = true
					break
			
			self.doCityHappinessModifiers(iPlayerID, bWarHappinessPenalty)
			
			# Relations with other Christian Civs
			self.doChristianRelations(iPlayerID)
			
			# Income for trade routes
			self.doChristianTradeRoutes(iPlayerID)
			
		# NON-Christian Civs
		########################################
		else:
			# Turn off happiness penalty if it's already active for some reason (e.g. if someone switches their religion)
			
			bWarHappinessPenalty = false
			self.doCityHappinessModifiers(iPlayerID, bWarHappinessPenalty)
			
##############################################
			
	def doHighestFavorRandomUnit(self):
		
		# Give pope's favorite player a free unit in his capital?
		
		iUnitType = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_PAPAL_PIKEMAN')
		
		iPlayerID = self.getPlayerWithHighestFavor()
		
		iFavor = self.getPlayerTotalFavorWithRome(iPlayerID)
		iFreeUnitChance = iFavor * g_iFreeUnitFavorMultiplier		# Odds are a percentage of this player's total favor
		
		iRoll = CyGame().getSorenRandNum(100, "Rolling to see if Pope gives his favorite player a free unit")
		
#		print("To get a free unit, Out of 100, player has to roll below %d... result was %d" %(iFreeUnitChance, iRoll))
		
		if (iRoll < iFreeUnitChance):
			
			pPlayer = gc.getPlayer(iPlayerID)
			
			if (pPlayer.getNumCities() > 0):
				
				pCapital = pPlayer.getCapitalCity()
				
				pPlayer.initUnit(iUnitType, pCapital.getX(), pCapital.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
				
				if (iPlayerID == CyGame().getActivePlayer()):
					popup = PyPopup.PyPopup(-1)
					szText = localText.getText("TXT_KEY_CHARLEMAGNE_RECEIVED_PAPAL_PIKEMAN", ())
					popup.setBodyString(szText)
					iState = PopupStates.POPUPSTATE_QUEUED
					popup.launch(true, iState)
				
#				print("Player gets free unit from Rome in capital")
		
##############################################
			
	def doCityHappinessModifiers(self, iPlayerID, bWarHappinessPenalty):
		
		pPlayer = gc.getPlayer(iPlayerID)
		pyPlayer = PyPlayer(iPlayerID)
		
		# Loop through all of this player's cities
		apCityList = pyPlayer.getCityList()
		for pyCityLoop in apCityList:
			
			pCityLoop = pyCityLoop.GetCy()
			# Reset extra happiness to 0
			pCityLoop.changeExtraHappiness(-pCityLoop.getExtraHappiness())
			
			if (pPlayer.getStateReligion() == self.iReligionChristianityID):
				
				iHappinessAmount = 0
				
				# Add penalty for not being at war with all of Rome's enemies
				if (bWarHappinessPenalty):
					iHappinessAmount += self.iNoWarHappyPenalty
				
				# If the city of Rome isn't controlled by Rome then more unhappiness
				pRomeCity = CyMap().plot(22, 14).getPlotCity()
				if (pRomeCity.getOwner() != self.iRomePlayerID):
					iHappinessAmount += self.iForeignRomeHappyPenalty
				
				# Modify Happiness for Amount of Favor with Rome
				iFavor = self.getPlayerTotalFavorWithRome(iPlayerID)
				
				# FavorEffect: Less than 0 gives unhappiness
				if (iFavor <= getFavorFromString("Spawn of Satan")):
					iHappinessAmount += -2
				
				# FavorEffect: Less than 30 gives unhappiness
				if (iFavor <= getFavorFromString("Heathen")):
					iHappinessAmount += -1
				
				# FavorEffect: Less than 50 gives unhappiness
				if (iFavor <= getFavorFromString("Fallen")):
					iHappinessAmount += -1
				
				# FavorEffect: More than 60 gives happiness
				if (iFavor > getFavorFromString("Believer")):
					iHappinessAmount += 1
					
				# FavorEffect: More than 90 AND HRE gives happiness
				if (self.isHolyRomanEmperor(iPlayerID)):
					iHappinessAmount += 1
				
				pCityLoop.changeExtraHappiness(iHappinessAmount)
		
##############################################
		
	def getTurnFavorWithRome(self, iPlayerID):
		
		iTurnFavor = g_iDefaultPerTurnFavor
		
		pPlayer = gc.getPlayer(iPlayerID)
		
		if (pPlayer):
			
			pyPlayer = PyPlayer(iPlayerID)
			pTeam = gc.getTeam(pPlayer.getTeam())
			
#			print("\n\nPlayer %d is %s" %(iPlayerID, pPlayer.getName()))
			
			# Christianity State Religion
			if (pPlayer.getStateReligion() == self.iReligionChristianityID):
				iTurnFavor += 10
				
#			print("Favor after Christianity State Religion: %d" %(iTurnFavor))
			
			# Islam State Religion
			if (pPlayer.getStateReligion() == self.iReligionIslamID):
				iTurnFavor += -10
				
#			print("Favor after Islam State Religion: %d" %(iTurnFavor))
				
			# Running Theocracy civic
			iCivicOptionReligion = CvUtil.findInfoTypeNum(gc.getCivicOptionInfo,gc.getNumCivicOptionInfos(),'CIVICOPTION_RELIGION')
			iCivicTheocracy = CvUtil.findInfoTypeNum(gc.getCivicInfo,gc.getNumCivicInfos(),'CIVIC_THEOCRACY')
			if (pPlayer.getCivics(iCivicOptionReligion) == iCivicTheocracy):
				iTurnFavor += 5
				
#			print("Favor after Theo Civic: %d" %(iTurnFavor))
				
			# War with Rome
			if (pTeam.isAtWar(self.iRomeTeamID)):
				iTurnFavor += -20
				
#			print("Favor after War with Rome: %d" %(iTurnFavor))
				
			# Not at War with Arabia
			if (not pTeam.isAtWar(self.iArabiaPlayerID)):
				iTurnFavor += -20
				
#			print("Favor after No Arabia War: %d" %(iTurnFavor))
			
			# Not at war with some other Non-Christian Civ
			for iPlayerLoop in range(gc.getMAX_CIV_PLAYERS()):
				pPlayerLoop = gc.getPlayer(iPlayerLoop)
				if (pPlayerLoop.isAlive()):
					if (pPlayerLoop.getStateReligion() != self.iReligionChristianityID):
						# Not Saladin
						if (pPlayerLoop.getCivilizationType() != self.iCivArabiaID):
							if (not pTeam.isAtWar(pPlayerLoop.getTeam())):
								iTurnFavor += -5
				
#			print("Favor after No non-Christian War: %d" %(iTurnFavor))
			
			# Loop through all player's cities
			iBuildingChristianTemple = CvUtil.findInfoTypeNum(gc.getBuildingInfo,gc.getNumBuildingInfos(),'BUILDING_CHRISTIAN_TEMPLE')
			iBuildingChristianMonastary = CvUtil.findInfoTypeNum(gc.getBuildingInfo,gc.getNumBuildingInfos(),'BUILDING_CHRISTIAN_MONASTERY')
			iBuildingChristianCathedral = CvUtil.findInfoTypeNum(gc.getBuildingInfo,gc.getNumBuildingInfos(),'BUILDING_CHRISTIAN_CATHEDRAL')
			
			apCityList = pyPlayer.getCityList()
			for pyCityLoop in apCityList:
				pCityLoop = pyCityLoop.GetCy()
				
				# City has Christianity
				if (pCityLoop.isHasReligion(self.iReligionChristianityID)):
					iTurnFavor += 3
					
				# City has Islam
				if (pCityLoop.isHasReligion(self.iReligionIslamID)):
					iTurnFavor += -3
					
				# City has Christian Temple
				if (pCityLoop.isHasBuilding(iBuildingChristianTemple)):
					iTurnFavor += 1
					
				# City has Christian Monastary
				if (pCityLoop.isHasBuilding(iBuildingChristianMonastary)):
					iTurnFavor += 2
					
				# City has Christian Cathedral
				if (pCityLoop.isHasBuilding(iBuildingChristianCathedral)):
					iTurnFavor += 3
				
#			print("Favor after Christian Buildings: %d" %(iTurnFavor))
					
			# Now set the amount of favor for this turn
			#self.setPlayerTurnFavorWithRome(iPlayerID, iTurnFavor)
			
#		print("Per-Turn favor for player %d is %d right now\n" %(iPlayerID, iTurnFavor))
		return iTurnFavor
		
##############################################
		
	def doChristianRelations(self, iPlayerID):
		
		iRelationsMod = 0
		
		# Modify Relations for Amount of Favor with Rome
		iFavor = self.getPlayerTotalFavorWithRome(iPlayerID)
		
		# FavorEffect: Less than 10 gives penalty
		if (iFavor <= 10):
			iRelationsMod += -2
		
		# FavorEffect: Less than 40 gives penalty
		if (iFavor <= 40):
			iRelationsMod += -1
		
		# Change relations if mod isn't 0
		if (iRelationsMod != 0):
			
			# Loop through all players, look for Christians
			for iPlayerLoop in range(gc.getMAX_CIV_PLAYERS()):
				if (iPlayerLoop != self.iRomePlayerID):
					pPlayer = gc.getPlayer(iPlayerLoop)
					if (pPlayer.getStateReligion() == self.iReligionChristianityID):
						# Mod value
						pPlayer.AI_setAttitudeExtra(iPlayerID, iRelationsMod)
		
##############################################
		
	def doChristianTradeRoutes(self, iPlayerID):
		
		pPlayer = gc.getPlayer(iPlayerID)
		
		if (pPlayer.getStateReligion() == self.iReligionChristianityID):
			
			iExtraTradeRouteIncome = 0
			
			# Modify Relations for Amount of Favor with Rome
			iFavor = self.getPlayerTotalFavorWithRome(iPlayerID)
			
			# FavorEffect: Less than 20 gives penalty to income
			if (iFavor <= getFavorFromString("Apostate")):
				iExtraTradeRouteIncome += -1
			
			# FavorEffect: Greater than 80 gives bonus to income
			if (iFavor > getFavorFromString("Protector")):
				iExtraTradeRouteIncome += 1
			
			# Loop through all cities and alter commerce yield
			
			pyPlayer = PyPlayer(iPlayerID)
			
			# Loop through all of this player's cities
			apCityList = pyPlayer.getCityList()
			for pyCityLoop in apCityList:
				
				iNumRoutes = 0
				
				pCityLoop = pyCityLoop.GetCy()
				
				for iTradeCity in range (pCityLoop.getTradeRoutes()):
					pTradeCity = pCityLoop.getTradeCity(iTradeCity)
#					print("Trade city object:")
#					print(pTradeCity)
					if (pTradeCity):
						if (pTradeCity.getName() != ""):
							iNumRoutes += 1
				
				iExtraIncome = iNumRoutes * iExtraTradeRouteIncome
				
				iBuildingClassType = CvUtil.findInfoTypeNum(gc.getBuildingInfo,gc.getNumBuildingClassInfos(),'BUILDINGCLASS_CHRISTIAN_TEMPLE')
				pCityLoop.setBuildingYieldChange(iBuildingClassType, YieldTypes.YIELD_COMMERCE, iExtraIncome)
		
##############################################
		
	def isHolyRomanEmperor(self, iPlayerID):
		
		if (iPlayerID != self.iRomePlayerID):
			
			if (self.getPlayerTotalFavorWithRome(iPlayerID) > getFavorFromString("Blessed")):
				
				iHighestFavorPlayer = self.getPlayerWithHighestFavor()
				
				if (iHighestFavorPlayer == iPlayerID):
					return true
		
#		print("Player %d is NOT HRE" %(iPlayerID))
		return false
		
##############################################
		
	def getPlayerWithHighestFavor(self):
		
		# Loop through all players, see if this one has the highest favor
		aiPlayerFavorList = []
		for iPlayerLoop in range(gc.getMAX_CIV_PLAYERS()):
			if (iPlayerLoop != self.iRomePlayerID):
				pPlayer = gc.getPlayer(iPlayerLoop)
				if (pPlayer.isAlive()):
					aiPlayerFavorList.append([self.getPlayerTotalFavorWithRome(iPlayerLoop), iPlayerLoop])
		
		aiPlayerFavorList.sort()
		aiPlayerFavorList.reverse()
		
		return aiPlayerFavorList[0][1]
		
		
		
		
############################################################################################
#		Overrides
############################################################################################
		
		
		
	def onChangeWar(self, argsList):
		'War Status Changes'
		bIsWar = argsList[0]
		iTeam = argsList[1]
		iRivalTeam = argsList[2]
		
		if (CyGame().isFinalInitialized()):
			
			pTeam = gc.getTeam(iTeam)
			pRivalTeam = gc.getTeam(iRivalTeam)
			iPlayer = pTeam.getLeaderID()
			iRivalPlayer = pRivalTeam.getLeaderID()
			
			# If Arabia is involved, see if the other player is Christian and should suffer a happiness penalty
			if (iTeam == self.iArabiaTeamID):
				self.updateFavorWithRomeEffects(iRivalPlayer)
			elif (iRivalTeam == self.iArabiaTeamID):
				self.updateFavorWithRomeEffects(iPlayer)
			
			# RomePermFavor: Declaring War on Rome
			if (bIsWar):
				if (iRivalTeam == self.iRomeTeamID):
					self.changePlayerPermanentFavorWithRome(iPlayer, -10)
		
##############################################

	def onUnitBuilt(self, argsList):
		'Unit Completed'
		self.parent.onUnitBuilt(self, argsList)
		pCity, pUnit = argsList
		
		iPlayer = pCity.getOwner()
		iFavor = self.getPlayerTotalFavorWithRome(iPlayer)
		
		# FavorEffect: Free promotion for civs which have favor greater than 70
		if (iFavor > getFavorFromString("True Believer")):
			iPromotionBlessed = CvUtil.findInfoTypeNum(gc.getPromotionInfo,gc.getNumPromotionInfos(),'PROMOTION_HEAL') # Paul: This should be changed once appropriate Promotion is added to XML
			# Can have promotion?
			if (pUnit.isPromotionValid(iPromotionBlessed)):
				pUnit.setHasPromotion(iPromotionBlessed, true)
		
##############################################
		
	def onCityBuilt(self, argsList):
		'City Built'
		self.parent.onCityBuilt(self, argsList)
		pCity = argsList[0]
		iOwner = pCity.getOwner()
		
		if (iOwner <= 4):
			if (pCity.isCapital()):
				iChristianity = CvUtil.findInfoTypeNum(gc.getReligionInfo,gc.getNumReligionInfos(),'RELIGION_CHRISTIANITY')
				pCity.setHasReligion(iChristianity, true, false, false)
		
		self.updateFavorWithRomeEffects(iOwner)
		
##############################################
	
	def onCityAcquired(self, argsList):
		'City Acquired'
		self.parent.onCityAcquired(self, argsList)
		iPreviousOwner,iNewOwner,pCity,bConquest,bTrade = argsList
		
		# City of Rome: Christian player gives back to Rome
		if (pCity.getX() == 22 and pCity.getY() == 14):
			
			pPlayer = gc.getPlayer(iNewOwner)
			
			# RomePermFavor: Christian player recapturing Rome
			if (pPlayer.getStateReligion() == self.iReligionChristianityID):
				pRomePlayer = gc.getPlayer(self.iRomePlayerID)
				pRomePlayer.acquireCity(pCity, false, true)
				self.changePlayerPermanentFavorWithRome(iNewOwner, 30)
		
		# Last city captured from a player
		pPreviousPlayer = gc.getPlayer(iPreviousOwner)
		
		if (pPreviousPlayer.getNumCities() <= 0):
			
			iRel = pPreviousPlayer.getStateReligion()
#			print("XXX: Killed player's state religion is %d, verify this is correct" %(iRel))
			
			# Heathen player killed
			if (pPreviousPlayer.getStateReligion() == -1):
				self.changePlayerPermanentFavorWithRome(iNewOwner, 15)
			
			# Christian player killed
			elif (pPreviousPlayer.getStateReligion() == self.iReligionChristianityID):
				self.changePlayerPermanentFavorWithRome(iNewOwner, -10)
			
			# Muslim player killed
			elif (pPreviousPlayer.getStateReligion() == self.iReligionIslamID):
				self.changePlayerPermanentFavorWithRome(iNewOwner, 30)
			
#		print("City Captured!")
				
		# City conquered, see if player wins
		if (bConquest):
			
			iNumNonPlayerCities = 0
			
			for iPlayerLoop in range(5):
				
				if (iNewOwner != iPlayerLoop):
					
					pPlayer = gc.getPlayer(iPlayerLoop)
					pyPlayer = PyPlayer(iPlayerLoop)
					
					if (pPlayer.isAlive()):
						
						# Loop through all Cities
						apCityList = pyPlayer.getCityList()
						for pyCity in apCityList:
							
							iNumNonPlayerCities += 1
			
#			print("iNumNonPlayerCities")
#			print(iNumNonPlayerCities)
			
			# All players dead except this one
			if (iNumNonPlayerCities == 0):
				CyGame().setWinner(gc.getPlayer(iNewOwner).getTeam(), 2)		# Conquest victory
		
##############################################
	
	def onCityAcquiredAndKept(self, argsList):
		'City Acquired and Kept'
		self.parent.onCityAcquiredAndKept(self, argsList)
		iOwner,pCity = argsList
		
		aiCityReligionList = []
		
		for iReligionLoop in range(gc.getNumReligionInfos()):
			if (pCity.isHasReligion(iReligionLoop)):
				aiCityReligionList.append(iReligionLoop)
		
		# RomePermFavor: Capture city with no faith
		if (len(aiCityReligionList) == 0):
			self.changePlayerPermanentFavorWithRome(iOwner, 2)
		
		# RomePermFavor: Capture Muslim City
		if (pCity.isHasReligion(self.iReligionIslamID)):
			self.changePlayerPermanentFavorWithRome(iOwner, 5)
		
##############################################
					
	def onCityRazed(self, argsList):
		'City Razed'
		self.parent.onCityRazed(self, argsList)
		pCity, iPlayer = argsList
		
#		print("City Razed!")
		
		# Conquest victory?
		iNumNonPlayerCities = 0
		
		for iPlayerLoop in range(5):
			
			if (iPlayer != iPlayerLoop):
				
				pPlayer = gc.getPlayer(iPlayerLoop)
				pyPlayer = PyPlayer(iPlayerLoop)
				
				if (pPlayer.isAlive()):
					
					# Loop through all Cities
					apCityList = pyPlayer.getCityList()
					for pyCity in apCityList:
						
						iNumNonPlayerCities += 1
		
		iNumNonPlayerCities -=1		# This is the active city
		
#		print("iNumNonPlayerCities")
#		print(iNumNonPlayerCities)
		
		# All players dead except this one
		if (iNumNonPlayerCities == 0):
			CyGame().setWinner(gc.getPlayer(iPlayer).getTeam(), 2)		# Conquest victory
		
		# RomePermFavor: Razing Christian City
		if (pCity.isHasReligion(self.iReligionChristianityID)):
			self.changePlayerPermanentFavorWithRome(iPlayer, -3)
		
		# RomePermFavor: Razing Muslim City
		if (pCity.isHasReligion(self.iReligionIslamID)):
			self.changePlayerPermanentFavorWithRome(iPlayer, 10)
		
##############################################
	
	def onUnitSpreadReligionAttempt(self, argsList):
		'Unit tries to spread religion to a city'
		self.parent.onUnitSpreadReligionAttempt(self, argsList)
		pUnit, iReligion, bSuccess = argsList
		
		iX = pUnit.getX()
		iY = pUnit.getY()
		pPlot = CyMap().plot(iX, iY)
		pCity = pPlot.getPlotCity()
		
		if (bSuccess):
			
			# Spreading Islam makes the Pope sad
			
			if (iReligion == self.iReligionIslamID):
				self.changePlayerPermanentFavorWithRome(pUnit.getOwner(), g_iSpreadIslamRomeFavor)
			
			bHeathen = true
			bMuslim = false
			for iReligionLoop in range(gc.getNumReligionInfos()):
				if (pCity.isHasReligion(iReligionLoop) and iReligionLoop != iReligion):
					bHeathen = false
			if (pCity.isHasReligion(self.iReligionIslamID)):
				bMuslim = true
			
			if (iReligion == self.iReligionChristianityID):
				
				# RomePermFavor: Spreading Christianity to Heathen City
				if (bHeathen):
					self.changePlayerPermanentFavorWithRome(pUnit.getOwner(), 2)
				
				# RomePermFavor: Spreading Christianity to Muslim City
				elif (bMuslim):
					self.changePlayerPermanentFavorWithRome(pUnit.getOwner(), 3)
		
##############################################
	
	def onUnitGifted(self, argsList):
		'Unit pillages a plot'
		self.parent.onUnitGifted(self, argsList)
		pUnit, iGiftingPlayer, pPlotLocation = argsList
		
		# Gifting units to Rome increases yo cred
		if (pPlotLocation.getOwner() == self.iRomePlayerID):
			
			iRelicID = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_RELIC')
			
			# Relic gives Favor
			if (pUnit.getUnitType() == iRelicID):
				self.changePlayerPermanentFavorWithRome(iGiftingPlayer, g_iRelicFavorBonus)
				# Remove the Relic from the map
				pUnit.kill(true, -1)
			
			iCost = gc.getUnitInfo(pUnit.getUnitType()).getProductionCost()
			
			# RomePermFavor: Gifting a unit to Rome
			if (iCost > 0):
				self.changePlayerPermanentFavorWithRome(iGiftingPlayer, iCost * g_iPapalGiftProductionFactor)
		
##############################################
		
	def onPlayerChangeStateReligion(self, argsList):
		'Player changes his state religion'
		self.parent.onPlayerChangeStateReligion(self, argsList)
		iPlayer, iNewReligion, iOldReligion = argsList
		
		# RomePermFavor: Switching to Islam
		if (iNewReligion == self.iReligionIslamID):
			self.changePlayerPermanentFavorWithRome(iPlayer, -20)
		
##############################################
		
	def onPlayerGoldTrade(self, argsList):
		'Player Trades gold to another player'
		self.parent.onPlayerGoldTrade(self, argsList)
		iFromPlayer, iToPlayer, iGoldAmount = argsList
		
		# Gifting gold to Rome increases yo cred
		if (iToPlayer == self.iRomePlayerID):
			
			# RomePermFavor: Gifting gold to Rome
			self.changePlayerPermanentFavorWithRome(iFromPlayer, iGoldAmount * 0.05)


		
		
		
		
############################################################################################
#		Player Script Data
############################################################################################
		
		
		
	def initPlayer(self, iPlayerID):
		"initPlayer: Called when the game first starts in order to set up script data stuff for player objects"
		
		pPlayer = gc.getPlayer(iPlayerID)
		
		# Set default script data manually since we need defaults for all values in the array before any functions can be called on them
		iDefaultOldFavorLevel = -1
		
		aScriptData = [g_iDefaultPermanentFavorWithRome, iDefaultOldFavorLevel]#, iFavorWithRome, bWarHappinessPenalty]
		pPlayer.setScriptData(pickle.dumps(aScriptData))
	
	def getPlayerTotalFavorWithRome(self, iPlayerID):
		return self.getPlayerPermanentFavorWithRome(iPlayerID) + self.getTurnFavorWithRome(iPlayerID)# self.getPlayerTurnFavorWithRome(iPlayerID)
	
	def getPlayerPermanentFavorWithRome(self, iPlayerID):
		pPlayer = gc.getPlayer(iPlayerID)
		szScriptData = pickle.loads(pPlayer.getScriptData())
		iPermanentFavorWithRome = szScriptData[0]		# Relations with civs is the first element in the Player ScriptData list
		return iPermanentFavorWithRome
	def setPlayerPermanentFavorWithRome(self, iPlayerID, iValue):
		pPlayer = gc.getPlayer(iPlayerID)
		szScriptData = pickle.loads(pPlayer.getScriptData())
		szScriptData[0] = iValue
		pPlayer.setScriptData(pickle.dumps(szScriptData))
	def changePlayerPermanentFavorWithRome(self, iPlayerID, iChange):
		pPlayer = gc.getPlayer(iPlayerID)
		szScriptData = pickle.loads(pPlayer.getScriptData())
		szScriptData[0] = szScriptData[0] + iChange
		pPlayer.setScriptData(pickle.dumps(szScriptData))

	def getPlayerOldFavorLevel(self, iPlayerID):
		pPlayer = gc.getPlayer(iPlayerID)
		szScriptData = pickle.loads(pPlayer.getScriptData())
		iOldFavorLevel = szScriptData[1]		# Favor Level
		return iOldFavorLevel
	def setPlayerOldFavorLevel(self, iPlayerID, iValue):
		pPlayer = gc.getPlayer(iPlayerID)
		szScriptData = pickle.loads(pPlayer.getScriptData())
		szScriptData[1] = iValue
		pPlayer.setScriptData(pickle.dumps(szScriptData))
	
