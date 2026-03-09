# Final Frontier
# Civilization 4 (c) 2007 Firaxis Games

# Designed & Programmed by:	Jon 'Trip' Shafer

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

from CvSolarSystem import *
import CvAI

# globals
gc = CyGlobalContext()
localText = CyTranslator()
AI = CvAI.CvAI()

DefaultUnitAI = UnitAITypes.NO_UNITAI

iPlanetQuantityTypeGood = 6
iPlanetQuantityTypeAverage = 4
iPlanetQuantityTypePoor = 3

iPreferredYieldRandBonus = 15

class CvFinalFrontierEvents(CvEventManager.CvEventManager):
	
	def __init__(self):
		
		self.parent = CvEventManager.CvEventManager
		self.parent.__init__(self)
		
		# Net Messages
		self.iNetMessage_setSelectedPlanet = 0
		self.iNetMessage_addPopulation = 1
		self.iNetMessage_RemovePopulation = 2
		self.iNetMessage_AssignBuilding = 3
		
		self.bUpdateDisplay = false	# Used when loading, since the order is wonky and trying to update display in onLoad 'splodes
		
		self.iWinningTeam = -1
		self.iTimeLeft = 0
		
		self.aiKillTimerData = -1
		
		self.iMaxPopulation = 0
		
		self.initMembers()
		
	def initMembers(self):
		
		self.iNumSystems = 0
		self.apSystems = []
		
		# Orbit ID of selected planet
		iDefaultSelectedPlanetRing = -1
		
		self.aaiPlayerDatas = []
		aiTempPlayerData = [iDefaultSelectedPlanetRing]
		for iPlayerLoop in range(gc.getMAX_PLAYERS()):
			self.aaiPlayerDatas.append(aiTempPlayerData[:])
		
	def getAI(self):
		return AI
		
	def initValues(self):
		
		self.iFeatureIDSolarSystem = CvUtil.findInfoTypeNum(gc.getFeatureInfo,gc.getNumFeatureInfos(),'FEATURE_SOLAR_SYSTEM')
		
	def onGameStart(self, argsList):
		'Called at the start of the game'
		self.parent.onGameStart(self, argsList)
		
		self.iWinningTeam = -1
		self.iTimeLeft = 0
		
		self.initValues()
		self.initMembers()
		
		CyGame().makeNukesValid(true)
		CyGame().setStartYear(2302)
		
		AI.initPlayerAIInfos()
		
		# Give Barbs some techs
		iTechHappy0 = CvUtil.findInfoTypeNum(gc.getTechInfo,gc.getNumTechInfos(),'TECH_HAPPY_0')
		iTechIndustry0 = CvUtil.findInfoTypeNum(gc.getTechInfo,gc.getNumTechInfos(),'TECH_INDUSTRY_0')
		iTechMilitary0 = CvUtil.findInfoTypeNum(gc.getTechInfo,gc.getNumTechInfos(),'TECH_MILITARY_0')
		iTechMilitary1 = CvUtil.findInfoTypeNum(gc.getTechInfo,gc.getNumTechInfos(),'TECH_MILITARY_1')
		
		pBarbPlayer = gc.getPlayer(18)
		pBarbTeam = gc.getTeam(pBarbPlayer.getTeam())
		pBarbTeam.setHasTech(iTechHappy0, true, 18, false, false)
		pBarbTeam.setHasTech(iTechIndustry0, true, 18, false, false)
		pBarbTeam.setHasTech(iTechMilitary0, true, 18, false, false)
		pBarbTeam.setHasTech(iTechMilitary1, false, 18, false, false)
		
		# Is this a scenario file?
		if ('.CivBeyondSwordWBSave' in CyMap().getMapScriptName()):
			
			import CvWBInterface
			
			# Search through all plots on the map for Solar Systems to add content for
			for pWBPlotLoop in CvWBInterface.WBDesc.plotDesc:
				
				iX = pWBPlotLoop.iX
				iY = pWBPlotLoop.iY
				
				pPlot = CyMap().plot(iX, iY)
				
				if (pPlot.getFeatureType() == self.iFeatureIDSolarSystem):
					
					iStarType = getStarIndexFromTag(pWBPlotLoop.szStarType)
					
					pSystem = CvSystem(iX,iY,iStarType)
					
					for iPlanetLoop in range(pWBPlotLoop.iNumPlanets):
						iPlanetType = getPlanetIndexFromTag(pWBPlotLoop.aszPlanetType[iPlanetLoop])
						iOrbitRing = pWBPlotLoop.aiOrbitRing[iPlanetLoop]
						iPlanetSize = pWBPlotLoop.aiPlanetSize[iPlanetLoop]
						bMoon = pWBPlotLoop.aiMoon[iPlanetLoop]
						bRings = pWBPlotLoop.aiRings[iPlanetLoop]
						
						pSystem.addPlanet(iPlanetType, iPlanetSize, iOrbitRing, bMoon, bRings)
						
					self.addSystem(pSystem)
			
			# Add Buildings in WBS to Home Planet of Star System
			for iPlayerLoop in range(gc.getMAX_CIV_PLAYERS()):
				pPlayer = gc.getPlayer(iPlayerLoop)
				for iCityLoop in range(pPlayer.getNumCities()):
					pCity = pPlayer.getCity(iCityLoop)
					
					pSystem = self.getSystemAt(pCity.getX(), pCity.getY())
					iBestPlanet = getBestPlanetInSystem(pSystem)
					pPlanet = pSystem.getPlanetByIndex(iBestPlanet)
					
					for iBuildingLoop in range(gc.getNumBuildingInfos()):
						
						if (pCity.isHasBuilding(iBuildingLoop)):
							pPlanet.setHasBuilding(iBuildingLoop, true)
			
		else:
			
			# Loop through all plots, find the Solar Systems and give them randomized starting junk
			for iPlotLoop in range(CyMap().numPlots()):
				pPlot = CyMap().plotByIndex(iPlotLoop)
				
				if (pPlot.getFeatureType() == self.iFeatureIDSolarSystem):
					iYield = -1 #No preference
					pSystem = createRandomSystem(pPlot.getX(), pPlot.getY(), iYield, iPlanetQuantityTypePoor)	# Called from CvSolarSystem
					self.addSystem(pSystem)
				
		# Debug stuff
		for iSystemLoop in range(self.getNumSystems()):
			printd("System (%d, %d) Num Planets: %d" %(self.getSystem(iSystemLoop).getX(), self.getSystem(iSystemLoop).getY(), self.getSystem(iSystemLoop).getNumPlanets()))
		
		# Players starting city stuff
		for iPlayerLoop in range(gc.getMAX_CIV_PLAYERS()):
			
			pPlayer = gc.getPlayer(iPlayerLoop)
			
			if (pPlayer.isAlive()):
				
				# XXX - This only works because at the start of the game we know player's starting city exists
				pCity = pPlayer.getCity(0)
				pSystem = self.getSystemAt(pCity.getX(), pCity.getY())
				
				# New Earth gets extra population when city built
				iTrait = CvUtil.findInfoTypeNum(gc.getTraitInfo,gc.getNumTraitInfos(),'TRAIT_NEW_EARTH')
				if (pPlayer.hasTrait(iTrait)):
					pCity.changePopulation(1)
				
				# Paradise gets free Mag-Lev on every planet
				iTrait = CvUtil.findInfoTypeNum(gc.getTraitInfo,gc.getNumTraitInfos(),'TRAIT_PARADISE')
				if (pPlayer.hasTrait(iTrait)):
					
					iBuildingMagLev = CvUtil.findInfoTypeNum(gc.getBuildingInfo,gc.getNumBuildingInfos(),'BUILDING_MAG_LEV_NETWORK')
					
					for iPlanetLoop in range(pSystem.getNumPlanets()):
						pPlanet = pSystem.getPlanetByIndex(iPlanetLoop)
						pPlanet.setHasBuilding(iBuildingMagLev, true)
						
					pCity.setNumRealBuilding(iBuildingMagLev, pSystem.getNumPlanets())
				
				# Red Syndicate gets 1 free trade routes when city built
				iTrait = CvUtil.findInfoTypeNum(gc.getTraitInfo,gc.getNumTraitInfos(),'TRAIT_SYNDICATE')
				if (pPlayer.hasTrait(iTrait)):
					pCity.changeExtraTradeRoutes(1)
		
		
		# Set up Player stuff: Star Systems & Gold
		for iPlayerLoop in range(gc.getMAX_CIV_PLAYERS()):
			
			pPlayer = gc.getPlayer(iPlayerLoop)
			
			if (pPlayer.isAlive()):
				
				self.doBeginTurnAI(iPlayerLoop, false)
				
				pPlayer.setGold(10)
				
				# Paradise starts with 10x normal amount of gold
				iTrait = CvUtil.findInfoTypeNum(gc.getTraitInfo,gc.getNumTraitInfos(),'TRAIT_PARADISE')
				if (pPlayer.hasTrait(iTrait)):
					pPlayer.setGold(pPlayer.getGold() * 10)
		
		self.doTerrainExtraCost()
		
		# First tutorial popup
		if (not CyUserProfile().getPlayerOption(PlayerOptionTypes.PLAYEROPTION_MODDER_1)):
			if (not Tutorial.isIntro()):
				
				Tutorial.setIntro(1)
				
				for iPlayer in range(gc.getMAX_PLAYERS()):
					player = gc.getPlayer(iPlayer)
					if (player.isAlive() and player.isHuman()):
						popupInfo = CyPopupInfo()
						popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
						szBody = localText.getText("TXT_KEY_FF_TUTORIAL_INTRO", ()) + " " + localText.getText("TXT_KEY_FF_CHECK_PEDIA_CONCEPTS", ()) + "\n\n" + localText.getText("TXT_KEY_FF_TUTORIAL_INTRO_3", ())
						popupInfo.setText(szBody)
						popupInfo.addPopup(iPlayer)
						
		self.updateSystemsDisplay()
		
		self.initScoreStuff()
		
	def doTerrainExtraCost(self):
		
		# Reset extra cost
		for iPlotLoop in range(CyMap().numPlots()):
			pPlot = CyMap().plotByIndex(iPlotLoop)
			pPlot.changeExtraMovePathCost(-pPlot.getExtraMovePathCost())
		
		iRadiationChange = 2000
		iRadiation = CvUtil.findInfoTypeNum(gc.getFeatureInfo,gc.getNumFeatureInfos(),'FEATURE_FALLOUT')
		iSupernovaChange = 60000
		iSupernova = CvUtil.findInfoTypeNum(gc.getFeatureInfo,gc.getNumFeatureInfos(),'FEATURE_JUNGLE')
		iBlackHoleChange = 10000
		iBlackHole = CvUtil.findInfoTypeNum(gc.getFeatureInfo,gc.getNumFeatureInfos(),'FEATURE_OASIS')
			
		# Set extra path cost
		for iPlotLoop in range(CyMap().numPlots()):
			
			pFeaturePlot = CyMap().plotByIndex(iPlotLoop)
			
			iFeature = pFeaturePlot.getFeatureType()
			
			# Feature: Radiation
			if (iFeature == iRadiation):
				
				pFeaturePlot.changeExtraMovePathCost(iRadiationChange)
				
			# Feature: Supernova or Black Hole
			elif (iFeature == iSupernova or iFeature == iBlackHole):
				
				# Stay at least 2 plots away
				for iXLoop in range(pFeaturePlot.getX()-2, pFeaturePlot.getX()+3):
					for iYLoop in range(pFeaturePlot.getY()-2, pFeaturePlot.getY()+3):
						
						# Exclude corners
						if ((iXLoop == pFeaturePlot.getX()-2) or (iXLoop == pFeaturePlot.getX()+2)) and ((iYLoop == pFeaturePlot.getY()-2) or (iYLoop == pFeaturePlot.getY()+2)):
							continue
						
						iActiveX = iXLoop
						iActiveY = iYLoop
						
						if (iActiveX >= CyMap().getGridWidth()):
							iActiveX = iActiveX - CyMap().getGridWidth()
						if (iActiveY >= CyMap().getGridHeight()):
							iActiveY = iActiveY - CyMap().getGridHeight()
						if (iActiveX < 0):
							iActiveX = CyMap().getGridWidth() + iActiveX
						if (iActiveY < 0):
							iActiveY = CyMap().getGridHeight() + iActiveY
						
						pLoopPlot = CyMap().plot(iActiveX, iActiveY)
						
						iChange = 0
						# Supernova
						if (iFeature == iSupernova):
							iChange = iSupernovaChange
						elif (iFeature == iBlackHole):
							iChange = iBlackHoleChange
						
						pLoopPlot.changeExtraMovePathCost(iChange)
		
	def onBeginGameTurn(self, argsList):
		'Called at the beginning of the end of each turn'
		
		self.parent.onBeginGameTurn(self, argsList)
		
		iGameTurn = argsList[0]
		
		self.updateMapYield()
		
		self.checkForTerrainEffects()
		
		# Loop through all of players
		for iPlayer in range(gc.getMAX_PLAYERS()):
			pPlayer = gc.getPlayer(iPlayer)
			
			if (pPlayer.isAlive()):
				pyPlayer = PyPlayer(iPlayer)
				
				# Show production popup for cities which don't have assigned production yet
				
				apCityList = pyPlayer.getCityList()
				for pyCity in apCityList:
					pCity = pyCity.GetCy()
					# Production assigned? If not, bring up the popup
					if (not pCity.isProduction()):
						pCity.chooseProduction(-1,-1,-1, false, false)
				
		# Update appearance of all Star Systems & Planets
		self.bUpdateDisplay = true
		
		self.doPirateSpawning()
		
		#self.initScoreStuff()
		
	def doPirateSpawning(self):
		
		printd("\n*********************************************")
		printd("*********************************************")
		printd("           Doing Pirate Spawning")
		printd("*********************************************")
		printd("*********************************************\n")
		
		iPlayer = gc.getBARBARIAN_PLAYER()
		pPlayer = gc.getPlayer(iPlayer)
		
		iNumPirateUnits = pPlayer.getNumUnits()
		
		iTurnPiratesAppear = 30
		iTurnPiratesMax = 250
		
		iTurn = CyGame().getElapsedGameTurns()
		printd("iTurn")
		printd(iTurn)
		
		if (iTurn >= iTurnPiratesAppear):
			
			iNumPlayers = CyGame().countCivPlayersEverAlive()
			
			iMinPirateQuantity = 1
			iMaxPirateQuantity = iNumPlayers * 4
			
			# Alter for gameoptions
			if (CyGame().isOption(GameOptionTypes.GAMEOPTION_NO_BARBARIANS)):
				iMinPirateQuantity = 0
				iMaxPirateQuantity = 0
			
			elif (CyGame().isOption(GameOptionTypes.GAMEOPTION_RAGING_BARBARIANS)):
				iMinPirateQuantity = 4
				iMaxPirateQuantity = iNumPlayers * 12
			
			printd("iMinPirateQuantity")
			printd(iMinPirateQuantity)
			printd("iMaxPirateQuantity")
			printd(iMaxPirateQuantity)
			
			iTurnsSincePiratesStarted = iTurn - iTurnPiratesAppear
			printd("iTurnsSincePiratesStarted")
			printd(iTurnsSincePiratesStarted)
			
			iNumPiratesRatio = iTurnsSincePiratesStarted * 1.0 / (iTurnPiratesMax - iTurnPiratesAppear)
			if (iNumPiratesRatio > 1):
				iNumPiratesRatio = 1
			printd("iNumPiratesRatio")
			printd(iNumPiratesRatio)
			
			iNumTotalPirateUnitsNeeded = int((iMaxPirateQuantity - iMinPirateQuantity) * iNumPiratesRatio) + iMinPirateQuantity
			printd("iNumTotalPirateUnitsNeeded")
			printd(iNumTotalPirateUnitsNeeded)
			
			printd("iNumPirateUnits")
			printd(iNumPirateUnits)
			
			iNumPirateUnitsNeeded = iNumTotalPirateUnitsNeeded - iNumPirateUnits
			printd("iNumPirateUnitsNeeded (pre-change)")
			printd(iNumPirateUnitsNeeded)
			
			# This can be a negative number if we already have more Pirates than we need
			if (iNumPirateUnitsNeeded > 0):
				
				aiValidPlotIndexList = []
				
				# Create list of valid plots to reference
				for iPlotLoop in range(CyMap().numPlots()):
					pPlot = CyMap().plotByIndex(iPlotLoop)
					
					bPlotValid = true
					
					# Impassable == no
					if (pPlot.isImpassable()):
						continue
					
					iFeature = pPlot.getFeatureType()
					
					iRadiation = CvUtil.findInfoTypeNum(gc.getFeatureInfo,gc.getNumFeatureInfos(),'FEATURE_FALLOUT')
					iBlackHole = CvUtil.findInfoTypeNum(gc.getFeatureInfo,gc.getNumFeatureInfos(),'FEATURE_OASIS')
					iGravField = CvUtil.findInfoTypeNum(gc.getFeatureInfo,gc.getNumFeatureInfos(),'FEATURE_GRAV_FIELD')
					iSupernova = CvUtil.findInfoTypeNum(gc.getFeatureInfo,gc.getNumFeatureInfos(),'FEATURE_JUNGLE')
					iDamageZone = CvUtil.findInfoTypeNum(gc.getFeatureInfo,gc.getNumFeatureInfos(),'FEATURE_SUPERNOVA_AREA')
					
					# Bad Features
					if (iFeature == iRadiation or iFeature == iBlackHole or iFeature == iGravField or iFeature == iSupernova or iFeature == iDamageZone):
						continue
					
					# Loop through all teams to see if anyone can see this plot
					for iTeamLoop in range(gc.getMAX_TEAMS()):
						if (gc.getTeam(iTeamLoop).isAlive()):
							if (pPlot.isVisible(iTeamLoop, false)):
								bPlotValid = false
								break
					
					# Plot invalid, quit
					if (not bPlotValid):
						continue
					
					if (pPlot.isCity()):
						fassert
					
					# Plot is valid! Add it to the list
					aiValidPlotIndexList.append(iPlotLoop)
				
				# Reduce number that can spawn on a single turn
				iNumPirateUnitsNeeded /= 2
				iNumPirateUnitsNeeded += 1
				
				printd("iNumPirateUnitsNeeded (Final)")
				printd(iNumPirateUnitsNeeded)
				
				iNumNeededRand = CyGame().getSorenRandNum(iNumPirateUnitsNeeded, "Rolling to see how many new Pirates should spawn")
				
				printd("Randomly selected number to add (0 through max to add this turn)")
				printd(iNumNeededRand)
				
				# Now add the proper number of Pirates
				for iUnitLoop in range(iNumNeededRand):
					
					iPass = 0
					
					# Pick random plot from the list we made a bit ago
					iRand = CyGame().getSorenRandNum(len(aiValidPlotIndexList), "Final Frontier: Picking random spawn plot for Pirates")
					iPlotID = aiValidPlotIndexList[iRand]
					pPlot = CyMap().plotByIndex(iPlotID)
					
					# Pick random unit
					
					iDestroyerI = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_DESTROYER_I')
					iInvasionShipI = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_INVASION_SHIP_I')
					iPlanetaryDefenseI = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_PLANETARY_DEFENSE_I')
					iBattleshipI = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_BATTLESHIP_I')
					
					iInvasionShipII = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_INVASION_SHIP_II')
					iPlanetaryDefenseII = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_PLANETARY_DEFENSE_II')
					iDestroyerII = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_DESTROYER_II')
					iBattleshipII = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_BATTLESHIP_II')
					
					iInvasionShipIII = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_INVASION_SHIP_III')
					iPlanetaryDefenseIII = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_PLANETARY_DEFENSE_III')
					iDestroyerIII = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_DESTROYER_III')
					iBattleshipIII = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_BATTLESHIP_III')
					
					aiUnitList = -1
					
					aiUnitList1 = [iDestroyerI, iInvasionShipI, iInvasionShipI, iPlanetaryDefenseI, iPlanetaryDefenseI] # More Inv & PD ships than Destroyers
					aiUnitList2 = [iDestroyerII, iDestroyerII, iInvasionShipII, iPlanetaryDefenseII, iBattleshipI]
					aiUnitList3 = [iDestroyerIII, iDestroyerIII, iDestroyerIII, iInvasionShipIII, iPlanetaryDefenseIII, iBattleshipII, iBattleshipII, iBattleshipIII]
					
					# Which 1/3rd of the game is it?
					if (CyGame().getElapsedGameTurns() < (CyGame().getEstimateEndTurn() / 3)):
						aiUnitList = aiUnitList1
					elif (CyGame().getElapsedGameTurns() < (CyGame().getEstimateEndTurn() * 2 / 3)):
						aiUnitList = aiUnitList2
					else:
						aiUnitList = aiUnitList3
					
					iRandUnit = CyGame().getSorenRandNum(len(aiUnitList), "Final Frontier: Picking random unit to spawn for Pirates")
					pPlayer.initUnit(aiUnitList[iRandUnit], pPlot.getX(), pPlot.getY(), UnitAITypes.UNITAI_ATTACK, DirectionTypes.NO_DIRECTION)
				
	def checkForTerrainEffects(self):
		
		# Loop through all plots
		for iPlotLoop in range(CyMap().numPlots()):
			pFeaturePlot = CyMap().plotByIndex(iPlotLoop)
			
			# Check for feature type
			iFeature = pFeaturePlot.getFeatureType()
			iRadiation = CvUtil.findInfoTypeNum(gc.getFeatureInfo,gc.getNumFeatureInfos(),'FEATURE_FALLOUT')
			iBlackHole = CvUtil.findInfoTypeNum(gc.getFeatureInfo,gc.getNumFeatureInfos(),'FEATURE_OASIS')
			iSupernova = CvUtil.findInfoTypeNum(gc.getFeatureInfo,gc.getNumFeatureInfos(),'FEATURE_JUNGLE')
			iDamageZone = CvUtil.findInfoTypeNum(gc.getFeatureInfo,gc.getNumFeatureInfos(),'FEATURE_SUPERNOVA_AREA')
			
			# For Message Display
			if (iFeature == iSupernova):
				
				abMessagePlayers = []
				
				if (pFeaturePlot.getNumUnits() > 0):
					for iUnitLoop in range(pFeaturePlot.getNumUnits()):
						pUnit = pFeaturePlot.getUnit(iUnitLoop)
						
						printd("HOSTILE_TERRAIN: Player %d lost a %s to a SUPERNOVA at %d, %d" %(pUnit.getOwner(), pUnit.getName(), pFeaturePlot.getX(), pFeaturePlot.getX()))
						
						# Only show message once for each player
						if (pUnit.getOwner() not in abMessagePlayers):
							szText = localText.getText("TXT_KEY_FF_TERRAIN_UNIT_LOST", ())
							if (pUnit.getUnitType() > -1):
								szButton = gc.getUnitInfo(pUnit.getUnitType()).getButton()
								CyInterface().addMessage(pUnit.getOwner(), False, gc.getEVENT_MESSAGE_TIME(), szText, "AS2D_LOSS_FF", InterfaceMessageTypes.MESSAGE_TYPE_MINOR_EVENT, szButton, gc.getInfoTypeForString("COLOR_RED"), pFeaturePlot.getX(), pFeaturePlot.getY(), True, True)	
								abMessagePlayers.append(pUnit.getOwner())
							
							iEffectID = CvUtil.findInfoTypeNum(gc.getEffectInfo, gc.getNumEffectInfos(), "EFFECT_INVASIONSHIP_REALLY_LARGE_HIT")
							CyEngine().triggerEffect(iEffectID, pFeaturePlot.getPoint())
							
							
			# For Message Display
			if (iFeature == iDamageZone):
				
				abMessagePlayers = []
				
				if (pFeaturePlot.getNumUnits() > 0):
					
					printd("Unit found in Supernova Damage Zone")
					
					for iUnitLoop in range(pFeaturePlot.getNumUnits()):
						pUnit = pFeaturePlot.getUnit(iUnitLoop)
						
						printd("HOSTILE_TERRAIN: Player %d had a %s damaged in a SUPERNOVA DAMAGE ZONE at %d, %d" %(pUnit.getOwner(), pUnit.getName(), pFeaturePlot.getX(), pFeaturePlot.getX()))
						
						# Only show message once for each player
						if (pUnit.getOwner() not in abMessagePlayers):
							szText = localText.getText("TXT_KEY_FF_TERRAIN_UNIT_DAMAGED", ())
							if (pUnit.getUnitType() > -1):
								szButton = gc.getUnitInfo(pUnit.getUnitType()).getButton()
								CyInterface().addMessage(pUnit.getOwner(), False, gc.getEVENT_MESSAGE_TIME(), szText, "AS2D_AIR_ATTACKED", InterfaceMessageTypes.MESSAGE_TYPE_MINOR_EVENT, szButton, gc.getInfoTypeForString("COLOR_RED"), pFeaturePlot.getX(), pFeaturePlot.getY(), True, True)	
								abMessagePlayers.append(pUnit.getOwner())
							
							iEffectID = CvUtil.findInfoTypeNum(gc.getEffectInfo, gc.getNumEffectInfos(), "EFFECT_INVASIONSHIP_REALLY_LARGE_HIT")
							CyEngine().triggerEffect(iEffectID, pFeaturePlot.getPoint())
			
			# Look for all plots that are radiation, damage units on them
			if (iFeature == iRadiation):
				if (pFeaturePlot.getNumUnits > 0):
					
					abMessagePlayers = []
					
					for iUnitLoop in range(pFeaturePlot.getNumUnits()):
						pUnit = pFeaturePlot.getUnit(iUnitLoop)
						
						printd("HOSTILE_TERRAIN: Player %d had a %s damaged in a RADIATION at %d, %d" %(pUnit.getOwner(), pUnit.getName(), pFeaturePlot.getX(), pFeaturePlot.getX()))
						
						# Only show message once for each player
						if (pUnit.getOwner() not in abMessagePlayers):
							szText = localText.getText("TXT_KEY_FF_TERRAIN_UNIT_DAMAGED", ())
							if (pUnit.getUnitType() > -1):
								szButton = gc.getUnitInfo(pUnit.getUnitType()).getButton()
								CyInterface().addMessage(pUnit.getOwner(), False, gc.getEVENT_MESSAGE_TIME(), szText, "AS2D_AIR_ATTACKED", InterfaceMessageTypes.MESSAGE_TYPE_MINOR_EVENT, szButton, gc.getInfoTypeForString("COLOR_RED"), pFeaturePlot.getX(), pFeaturePlot.getY(), True, True)	
								abMessagePlayers.append(pUnit.getOwner())
							
							iEffectID = CvUtil.findInfoTypeNum(gc.getEffectInfo, gc.getNumEffectInfos(), "EFFECT_INVASIONSHIP_REALLY_LARGE_HIT")
							CyEngine().triggerEffect(iEffectID, pFeaturePlot.getPoint())
								
			if (iFeature == iBlackHole):
#				printd("\n\nFound a black hole at %d, %d" %(pFeaturePlot.getX(), pFeaturePlot.getY()))
				
				# Loop within 1 plot each direction to kill units which are too close to the black hole
				for iXLoop in range(pFeaturePlot.getX()-1, pFeaturePlot.getX()+2):
					for iYLoop in range(pFeaturePlot.getY()-1, pFeaturePlot.getY()+2):
						
						iActiveX = iXLoop
						iActiveY = iYLoop
						
						abMessagePlayers = []
						
#						printd("Checking Plot %d, %d" %(iActiveX, iActiveY))
						
						if (iActiveX >= CyMap().getGridWidth()):
							iActiveX = iActiveX - CyMap().getGridWidth()
						if (iActiveY >= CyMap().getGridHeight()):
							iActiveY = iActiveY - CyMap().getGridHeight()
						if (iActiveX < 0):
							iActiveX = CyMap().getGridWidth() + iActiveX
						if (iActiveY < 0):
							iActiveY = CyMap().getGridHeight() + iActiveY
						
#						printd("Revised Plot is %d, %d" %(iActiveX, iActiveY))
						
						pLoopPlot = CyMap().plot(iActiveX, iActiveY)
						
						if (pLoopPlot.getNumUnits() > 0):
							
							for iUnitLoop in range(pLoopPlot.getNumUnits()):
								pUnit = pLoopPlot.getUnit(iUnitLoop)
								
								printd("HOSTILE_TERRAIN: Player %d lost a %s to a BLACK HOLE at %d, %d" %(pUnit.getOwner(), pUnit.getName(), pFeaturePlot.getX(), pFeaturePlot.getX()))
								
#								if (gc.getPlayer(pUnit.getOwner()).isHuman()): # Temp cheat for AI
								
								# Only show message once for each player
								if (pUnit.getOwner() not in abMessagePlayers):
									szText = localText.getText("TXT_KEY_FF_TERRAIN_UNIT_LOST", ())
									if (pUnit.getUnitType() > -1):
										szButton = gc.getUnitInfo(pUnit.getUnitType()).getButton()
										CyInterface().addMessage(pUnit.getOwner(), False, gc.getEVENT_MESSAGE_TIME(), szText, "AS2D_LOSS_FF", InterfaceMessageTypes.MESSAGE_TYPE_MINOR_EVENT, szButton, gc.getInfoTypeForString("COLOR_RED"), pFeaturePlot.getX(), pFeaturePlot.getY(), True, True)	
										abMessagePlayers.append(pUnit.getOwner())
									
									iEffectID = CvUtil.findInfoTypeNum(gc.getEffectInfo, gc.getNumEffectInfos(), "EFFECT_INVASIONSHIP_REALLY_LARGE_HIT")
									CyEngine().triggerEffect(iEffectID, pFeaturePlot.getPoint())
								
#								printd("Killing unit at %d, %d" %(iActiveX, iActiveY))
								pUnit.kill(false, -1)
								
				iNumUnitsToMove = 0
				aUnitsToMove = []
				
				# Loop within 2 plots each direction to move units towards the hole
				for iXLoop in range(pFeaturePlot.getX()-2, pFeaturePlot.getX()+3):
					for iYLoop in range(pFeaturePlot.getY()-2, pFeaturePlot.getY()+3):
						
						# Exclude corners
						if ((iXLoop == pFeaturePlot.getX()-2) or (iXLoop == pFeaturePlot.getX()+2)) and ((iYLoop == pFeaturePlot.getY()-2) or (iYLoop == pFeaturePlot.getY()+2)):
							continue
						
						iActiveX = iXLoop
						iActiveY = iYLoop
						
						if (iActiveX < 0):
							iActiveX = CyMap().getGridWidth() + iActiveX
						if (iActiveY < 0):
							iActiveY = CyMap().getGridHeight() + iActiveY
						
						pLoopPlot = CyMap().plot(iActiveX, iActiveY)
						
#						printd("New Plot is %d, %d, # units here is %d" %(iActiveX, iActiveY, pLoopPlot.getNumUnits()))
						# Check each plot for unit s, move them towards the black hole
						if (pLoopPlot.getNumUnits() > 0):
							
							# Amount to move a unit towards the hole
							iXChange = 0
							iYChange = 0
							if (pFeaturePlot.getX() > iXLoop):
								iXChange = 1
							elif (pFeaturePlot.getX() < iXLoop):
								iXChange = -1
							if (pFeaturePlot.getY() > iYLoop):
								iYChange = 1
							elif (pFeaturePlot.getY() < iYLoop):
								iYChange = -1
								
							iXDest = pLoopPlot.getX() + iXChange
							iYDest = pLoopPlot.getY() + iYChange
							
							if (iXDest >= CyMap().getGridWidth()):
								iXDest = iXDest - CyMap().getGridWidth()
							if (iYDest >= CyMap().getGridHeight()):
								iYDest = iYDest - CyMap().getGridHeight()
							if (iXDest < 0):
								iXDest = CyMap().getGridWidth() + iXDest
							if (iYDest < 0):
								iYDest = CyMap().getGridHeight() + iYDest
							
							abMessagePlayers = []
							
							for iUnitLoop in range(pLoopPlot.getNumUnits()):
								pUnit = pLoopPlot.getUnit(iUnitLoop)
								iNumUnitsToMove += 1
								aUnitsToMove.append([pUnit, iXDest, iYDest])
#								printd("Moving Unit to %d, %d" %(iXDest, iYDest))
								
								# Only show message once for each player
								if (pUnit.getOwner() not in abMessagePlayers):
									szText = localText.getText("TXT_KEY_FF_TERRAIN_UNIT_GRAV_FIELD", ())
									if (pUnit.getUnitType() > -1):
										szButton = gc.getUnitInfo(pUnit.getUnitType()).getButton()
										CyInterface().addMessage(pUnit.getOwner(), False, gc.getEVENT_MESSAGE_TIME(), szText, "AS2D_BLACK_HOLE_PLAY_ONCE", InterfaceMessageTypes.MESSAGE_TYPE_MINOR_EVENT, szButton, gc.getInfoTypeForString("COLOR_RED"), pUnit.plot().getX(), pUnit.plot().getY(), True, True)	
										abMessagePlayers.append(pUnit.getOwner())
										
									iEffectID = CvUtil.findInfoTypeNum(gc.getEffectInfo, gc.getNumEffectInfos(), "EFFECT_INVASIONSHIP_REALLY_LARGE_HIT")
									CyEngine().triggerEffect(iEffectID, pFeaturePlot.getPoint())
							
				for iUnitLoop in range(iNumUnitsToMove):
					pUnit = aUnitsToMove[iUnitLoop][0]
					iNewX = aUnitsToMove[iUnitLoop][1]
					iNewY = aUnitsToMove[iUnitLoop][2]
					
					pUnit.setXY(iNewX, iNewY, true, true, true)
				
	def onBeginPlayerTurn(self, argsList):
		'Called at the beginning of each players turn'
		
		self.parent.onBeginPlayerTurn(self, argsList)
		
		iGameTurn, iPlayer = argsList
		
		if (gc.getPlayer(iPlayer).isAlive()):
			
			self.doBeginTurnAI(iPlayer)
		
	def onEndGameTurn(self, argsList):
		'Called at the end of the end of each turn'
		
		self.parent.onEndGameTurn(self, argsList)
		
		iGameTurn = argsList[0]
		
		self.updateAllStarbases()
		
		# Tutorial popup about Pirates on turn 10
		if (iGameTurn == 10):
			
			if (not CyUserProfile().getPlayerOption(PlayerOptionTypes.PLAYEROPTION_MODDER_1)):
				if (not Tutorial.isPirates()):
					
					Tutorial.setPirates(1)
					
					for iPlayer in range(gc.getMAX_PLAYERS()):
						player = gc.getPlayer(iPlayer)
						if (player.isAlive() and player.isHuman()):
							popupInfo = CyPopupInfo()
							popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
#							szBody = localText.getText("TXT_KEY_FF_TUTORIAL_INTRO", ()) + " " + localText.getText("TXT_KEY_FF_CHECK_PEDIA_CONCEPTS", ()) + "\n\n" + localText.getText("TXT_KEY_FF_TUTORIAL_INTRO_3", ())
							szBody = localText.getText("TXT_KEY_FF_TUTORIAL_SPACE_PIRATES", ())
							popupInfo.setText(szBody)
							popupInfo.addPopup(iPlayer)
		
#############################################################################################
#		Multiplayer Functionality
#############################################################################################

	def onModNetMessage(self, argsList):
		'Called whenever CyMessageControl().sendModNetMessage() is called - this is all for you modders!'
		
		iData1, iData2, iData3, iData4, iData5 = argsList
		
		iMessage = iData1
		
		# Type of NetMessage:
		
		# Set Selected Planet
		if (iMessage == self.iNetMessage_setSelectedPlanet):
		
			#CyMessageControl().sendModNetMessage(self.iNetMessage_setSelectedPlanet, pSystem.getX(), pSystem.getY(), iPlanetRing, -1)
			
			iX = iData2
			iY = iData3
			iPlanetRing = iData4
			
			pSystem = self.getSystemAt(iX, iY)
			
			pSystem.setSelectedPlanet(iPlanetRing)
			
			pSystem.updateDisplay()
		
		# Assign 1 population to a planet
		elif (iMessage == self.iNetMessage_addPopulation):
		
			#CyMessageControl().sendModNetMessage(FinalFrontier.iNetMessage_addPopulation, pSystem.getX(), pSystem.getY(), iPlanetRing, -1)
			
			iX = iData2
			iY = iData3
			iPlanetRing = iData4
			
			pSystem = self.getSystemAt(iX, iY)
			
			self.doAddPopulationToPlanet(pSystem, iPlanetRing)
			
			# Update
			pPlot = CyMap().plot(iX, iY)
			self.updatePlotYield(pPlot)
			CyInterface().setDirty(InterfaceDirtyBits.CitizenButtons_DIRTY_BIT, True)
		
		# Remove a certain amount of population from a planet
		elif (iMessage == self.iNetMessage_RemovePopulation):
		
			#CyMessageControl().sendModNetMessage(FinalFrontier.iNetMessage_RemovePopulation, pSystem.getX(), pSystem.getY(), iPlanetRing, iRemove)
			
			iX = iData2
			iY = iData3
			iPlanetRing = iData4
			iRemove = iData5
			
			pSystem = self.getSystemAt(iX, iY)
			pPlanet = pSystem.getPlanet(iPlanetRing)
			
			# Fix for bug where clicking the - button too fast would bring a planet's population into negative numbers
			if (pPlanet.getPopulation() > 0):
				
				pPlanet.changePopulation(iRemove)
				
				# Update
				pPlot = CyMap().plot(iX, iY)
				self.updatePlotYield(pPlot)
				CyInterface().setDirty(InterfaceDirtyBits.CitizenButtons_DIRTY_BIT, True)
		
		# Remove a certain amount of population from a planet
		elif (iMessage == self.iNetMessage_AssignBuilding):
		
			#CyMessageControl().sendModNetMessage(FinalFrontier.iNetMessage_AssignBuilding, pSystem.getX(), pSystem.getY(), iPlanetRing, -1)
			
			iX = iData2
			iY = iData3
			iPlanetRing = iData4
			iRemove = iData5
			
			pPlot = CyMap().plot(iX, iY)
			pCity = -1
			if (pPlot.isCity()):
				pCity = pPlot.getPlotCity()
				
			pSystem = self.getSystemAt(iX, iY)
			pPlanet = pSystem.getPlanet(iPlanetRing)
			
			pOldPlanet = pSystem.getPlanet(pSystem.getBuildingPlanetRing())
			
			# Working on a building?
			if (pCity.isProductionBuilding()):
				
				iBuilding = pCity.getProductionBuilding()
				
				pOldPlanet.setBuildingProduction(iBuilding, pCity.getProduction())
				
#				szText = "Old Planet: %s %d: %s" %(pCity.getName(), pOldPlanet.getOrbitRing(), CvSolarSystem.aszPlanetTypeNames[pOldPlanet.getPlanetType()])
#				printd(szText)
#				printd("Assigning %d to production of building %d" %(pCity.getProduction(), iBuilding))
				
				# Planet doesn't already have this building
				if (not pPlanet.isHasBuilding(iBuilding)):
					pCity.setProduction(pPlanet.getBuildingProduction(iBuilding))
				# Planet does have this building, pop the queue
				else:
					pCity.popOrder(0, false, true)
				
				CyInterface().setDirty(InterfaceDirtyBits.CityScreen_DIRTY_BIT, True)
			
			pSystem.setBuildingPlanetRing(iPlanetRing)
			
			CyInterface().setDirty(InterfaceDirtyBits.CitizenButtons_DIRTY_BIT, True)
			CyInterface().setDirty(InterfaceDirtyBits.SelectionButtons_DIRTY_BIT, True)
			
#############################################################################################
#		Starbase Stuff
#############################################################################################
	
	def onUnitBuildImprovement(self, argsList):
		'Unit begins enacting a Build (building an Improvement or Route)'
		pUnit, iBuild, bFinished = argsList
		
		iBuildStarbaseID = CvUtil.findInfoTypeNum(gc.getBuildInfo,gc.getNumBuildInfos(),'BUILD_STARBASE')
		
		# Starbase WAS built
		if (iBuild == iBuildStarbaseID):
			pUnit.setScriptData("BuildingStarbase")

	def onImprovementBuilt(self, argsList):
		'Improvement Built'
		iImprovement, iX, iY = argsList
		
		iImprovementStarbaseID = CvUtil.findInfoTypeNum(gc.getImprovementInfo,gc.getNumImprovementInfos(),'IMPROVEMENT_STARBASE')
		iUnitConstructShipID = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_CONSTRUCT_SHIP')
		
		# Starbase finished
		if (iImprovement == iImprovementStarbaseID):
			
			pPlot = CyMap().plot(iX, iY)
			pPlot.setImprovementType(-1)
			
			# Look for Construction Ship on this plot
			for iUnitLoop in range(pPlot.getNumUnits()):
				pUnit = pPlot.getUnit(iUnitLoop)
				
				if (pUnit.getScriptData() == "BuildingStarbase"):
					self.doMakeStarbase(pUnit.getOwner(), iX, iY)
					self.aiKillTimerData = [3, pUnit.getOwner(), pUnit.getID()]
#					pUnit.kill(true, -1)
	
	def doMakeStarbase(self, iPlayer, iX, iY):
		
		pPlayer = gc.getPlayer(iPlayer)
		pPlot = CyMap().plot(iX, iY)
		
		# Create Starbase Unit
		iUnitStarbaseID = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_STARBASE_I')
		pPlayer.initUnit(iUnitStarbaseID, iX, iY, UnitAITypes.UNITAI_ATTACK, DirectionTypes.NO_DIRECTION)
		
		self.updateStarbaseCulture(iPlayer, iX, iY)
		
	def updateStarbaseCulture(self, iPlayer, iX, iY):
		
		# Create culture around unit
		for iXLoop in range(iX-2, iX+3):
			for iYLoop in range(iY-2, iY+3):
				
				iActiveX = iXLoop
				iActiveY = iYLoop
				
				if (iActiveX < 0):
					iActiveX = CyMap().getGridWidth() + iActiveX
				if (iActiveY < 0):
					iActiveY = CyMap().getGridHeight() + iActiveY
				
				pLoopPlot = CyMap().plot(iActiveX, iActiveY)
#				pPlotLoop = CyMap().plot(iXLoop, iYLoop)
#				printd("Setting Player %d as the owner of %d, %d" %(iPlayer, iXLoop, iYLoop))
				# Don't override culture that's already here
				if (pLoopPlot.getOwner() == -1):
					pLoopPlot.setOwnerNoUnitCheck(iPlayer)
		
	def updateAllStarbases(self):
		
		# Update Starbase culture
		iUnitStarbaseID = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_STARBASE_I')
		iUnitStarbaseIID = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_STARBASE_II')
		iUnitStarbaseIIID = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_STARBASE_III')
		iUnitMissileI = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_MISSILE_I')
		iUnitMissileII = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_MISSILE_II')
		iUnitMissileIII = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_MISSILE_III')
		
		# List made to preserve culture of units built first
		aaiStarbaseList = []
		
		for iPlayerLoop in range(gc.getMAX_CIV_PLAYERS()):
			pPlayer = gc.getPlayer(iPlayerLoop)
			pTeam = gc.getTeam(pPlayer.getTeam())
			pyPlayer = PyPlayer(iPlayerLoop)
			
			iUnitToCreate = -1
			aiPossibleUnitList = [iUnitMissileI, iUnitMissileII, iUnitMissileIII]
			
			for iUnitLoop in aiPossibleUnitList:
				
				pUnitInfo = gc.getUnitInfo(iUnitLoop)
				iNeededTech = pUnitInfo.getPrereqAndTech()
				
				if (pTeam.isHasTech(iNeededTech)):
					iUnitToCreate = iUnitLoop
			
			apUnitList = pyPlayer.getUnitList()
			for pUnitLoop in apUnitList:
				if (pUnitLoop.getUnitType() == iUnitStarbaseID or pUnitLoop.getUnitType() == iUnitStarbaseIID or pUnitLoop.getUnitType() == iUnitStarbaseIIID):
					aaiStarbaseList.append([pUnitLoop.getGameTurnCreated(), iPlayerLoop, pUnitLoop.getX(), pUnitLoop.getY()])
					
					# Need appropriate tech to create Missile
					if (iUnitToCreate != -1):
						# Need appropriate turn to create
						iTurnCreated = pUnitLoop.getGameTurnCreated()
						iCurrentTurn = CyGame().getGameTurn()
						
						if (iTurnCreated != iCurrentTurn):
							iTurnsSinceCreation = iCurrentTurn - iTurnCreated
							# Produce Missile every 15 turns
							if (iTurnsSinceCreation % 15 == 0):
								print "UnitID: %d, X: %d, Y: %d" %(iUnitToCreate, pUnitLoop.getX(), pUnitLoop.getY())
								pUnit = pPlayer.initUnit(iUnitToCreate, pUnitLoop.getX(), pUnitLoop.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.NO_DIRECTION)
								# Load Missile onto Starbase... the C++ doesn't like this but it can deal :)
								pUnit.setTransportUnit(pUnitLoop)
		
#		printd("\n\nXXX: There are %d Starbases on the map" %(len(aaiStarbaseList)))
#		printd(aaiStarbaseList)
			
		if (len(aaiStarbaseList) > 0):
			
			# Make order such that units built first get culture preference
			aaiStarbaseList.sort()
#			aaiStarbaseList.reverse()
			
			for iStarbaseLoop in range(len(aaiStarbaseList)):
				self.updateStarbaseCulture(aaiStarbaseList[iStarbaseLoop][1], aaiStarbaseList[iStarbaseLoop][2], aaiStarbaseList[iStarbaseLoop][3])
		
	def canBuildStarbase(self, pPlot, iOffset=0):
		
		# Starbase restriction
		iBuildStarbase = CvUtil.findInfoTypeNum(gc.getBuildInfo,gc.getNumBuildInfos(),'BUILD_STARBASE')
		
		# Can't build on a Solar System
		iFeatureIDSolarSystem = CvUtil.findInfoTypeNum(gc.getFeatureInfo,gc.getNumFeatureInfos(),'FEATURE_SOLAR_SYSTEM')
		if (pPlot.getFeatureType() == iFeatureIDSolarSystem):
			return 0
		
		# Can't build on top of another Starbase
		iUnitStarbaseI = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_STARBASE_I')
		iUnitStarbaseII = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_STARBASE_II')
		iUnitStarbaseIII = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_STARBASE_III')
		
		iNumUnits = iOffset # Offset so that Interface can disable button
		
		# Loop through all units on the plot
		for iUnitLoop in range(pPlot.getNumUnits()):
			pUnit = pPlot.getUnit(iUnitLoop)
			
			# Can't build on top of another Starbase
			if (pUnit.getUnitType() == iUnitStarbaseI or pUnit.getUnitType() == iUnitStarbaseII or pUnit.getUnitType() == iUnitStarbaseIII):
				return 0
			
			# if there are any Construction Ships already building a Starbase then disallow more	
			if (pUnit.getBuildType() == iBuildStarbase):
				iNumUnits += 1
				if (iNumUnits > 1):	# Account for the one unit actually performing the mission
					return 0
		
		return 1
		
#############################################################################################
#		Player Data
#############################################################################################
	
#	def getPlayerSelectedPlanetRing(self, iPlayerID):
#		aiPlayerData = self.aaiPlayerDatas[iPlayerID]
#		return aiPlayerData[0]
#		
#	def setPlayerSelectedPlanetRing(self, iPlayerID, iRingID):
#		self.aaiPlayerDatas[iPlayerID][0] = iRingID
#		
#		if (CyInterface().isCityScreenUp()):
#			CyInterface().setDirty(InterfaceDirtyBits.CitizenButtons_DIRTY_BIT, True)
#			CyInterface().setDirty(InterfaceDirtyBits.InfoPane_DIRTY_BIT, True)
	
#############################################################################################
#		Systems
#############################################################################################
		
	def getNumSystems(self):
		return self.iNumSystems
	def getSystem(self, iSystemID):
		return self.apSystems[iSystemID]
	def getSystemAt(self, iX, iY):
		for iSystemLoop in range(self.getNumSystems()):
			pSystem = self.getSystem(iSystemLoop)
			if (pSystem.getX() == iX and pSystem.getY() == iY):
				return pSystem
	def addSystem(self, pSystem):
		self.apSystems.append(pSystem)
		self.iNumSystems += 1
	def resetSystems(self):
		self.apSystems = []
		self.iNumSystems = 0
		
	def updateSystemsDisplay(self):
		for iSystemLoop in range(self.getNumSystems()):
			self.getSystem(iSystemLoop).updateDisplay()
		
	def updateNeededSystemsDisplay(self):
		for iSystemLoop in range(self.getNumSystems()):
			pSystem = self.getSystem(iSystemLoop)
			if (pSystem.isNeedsUpdate()):
				pSystem.updateDisplay()
				pSystem.setNeedsUpdate(false)
	
#############################################################################################
#		Score calculation
#############################################################################################
	
	def initScoreStuff(self):
		
		iMaxFood = 0
		
		for iSystemLoop in range(self.getNumSystems()):
			pSystem = self.getSystem(iSystemLoop)
			
			for iPlanetLoop in range(pSystem.getNumPlanets()):
				pPlanet = pSystem.getPlanetByIndex(iPlanetLoop)
				
				iMaxFood += pPlanet.getBaseYield(0) # Add up the Food.. mmmm
		
		self.iMaxPopulation = iMaxFood / gc.getDefineINT("FOOD_CONSUMPTION_PER_POPULATION") * 2
		
#		printd("Initing Score; Max Pop %d" %(self.iMaxPopulation))
		
#############################################################################################
#		City Yield
#############################################################################################

	def updateMapYield(self):
		
		self.initValues()
		
		for iPlotLoop in range(CyMap().numPlots()):
			
			pPlot = CyMap().plotByIndex(iPlotLoop)
			
			self.updatePlotYield(pPlot)
			
	def updatePlotYield(self, pPlot):
		
		pCity = pPlot.getPlotCity()
		
		iOwner = pCity.getOwner()
		
		if (iOwner != -1):
			
			if (pPlot.getFeatureType() == self.iFeatureIDSolarSystem):
				
				pPlayer = gc.getPlayer(iOwner)
				
				pSystem = self.getSystemAt(pPlot.getX(), pPlot.getY())
				
				aiSystemYield = [0,0,0]
				
				# The Forge get's 1 fewer food in all cities
				iTrait = CvUtil.findInfoTypeNum(gc.getTraitInfo,gc.getNumTraitInfos(),'TRAIT_THE_FORGE')
				if (pPlayer.hasTrait(iTrait)):
					aiSystemYield[0] -= 1
#					if (pCity.isCapital()):
#						aiSystemYield[1] += 1
#					else:
#						aiSystemYield[1] += 1
						
				# Red Syndicate gets +1 food and production for each Trade Route
				iTrait = CvUtil.findInfoTypeNum(gc.getTraitInfo,gc.getNumTraitInfos(),'TRAIT_SYNDICATE')
				if (pPlayer.hasTrait(iTrait)):
					for iTradeCity in range (pCity.getTradeRoutes()):
						pTradeCity = pCity.getTradeCity(iTradeCity)
#						printd("Trade city object:")
#						printd(pTradeCity)
						if (pTradeCity):
							if (pTradeCity.getName() != ""):
#								printd("entering trade route additions")
								aiSystemYield[0] += 1
								aiSystemYield[1] += 1
				
				# Building mod needs to be done manually
				for iBuildingLoop in range(gc.getNumBuildingInfos()):
					
					# Has buildings
					if (pCity.getNumRealBuilding(iBuildingLoop) > 0):
						
						pBuildingInfo = gc.getBuildingInfo(iBuildingLoop)
						for iYieldLoop in range(3):
							if (pBuildingInfo.getYieldChange(iYieldLoop) > 0):
								aiSystemYield[iYieldLoop] += (pBuildingInfo.getYieldChange(iYieldLoop) * pCity.getNumRealBuilding(iBuildingLoop))
				
				printd("Updating Yield for %s" %(pCity.getName()))
				
				for iPlanetLoop in range(pSystem.getNumPlanets()):
					
					pPlanet = pSystem.getPlanetByIndex(iPlanetLoop)
					
					printd("  Planet at Ring ID %d" %(pPlanet.getOrbitRing()))
					
					for iYieldLoop in range(3):
						iValue = (pPlanet.getTotalYield(iOwner, iYieldLoop) * pPlanet.getPopulation())
						aiSystemYield[iYieldLoop] += iValue
						printd("    Yield %d Value: %d" %(iYieldLoop, iValue))
					
				# Add Trade Route yield
				aiSystemYield[2] += pCity.getTradeYield(2)
					
				for iYieldLoop in range(3):
					pCity.setBaseYieldRate(iYieldLoop, aiSystemYield[iYieldLoop])
					printd("  Setting City Base Yield %d to %d" %(iYieldLoop, aiSystemYield[iYieldLoop]))
		
	def doAddPopulationToPlanet(self, pSystem, iPlanetOrbitRing):
		
		pPlanet = pSystem.getPlanet(iPlanetOrbitRing)
		iPlanetPopulation = pPlanet.getPopulation()
		
		pPlot = CyMap().plot(pSystem.getX(), pSystem.getY())
		pCity = pPlot.getPlotCity()
		iOwner = pCity.getOwner()
		iSystemPopulation = pSystem.getPopulation()

		iCityPopulation = pCity.getPopulation()
		iMaxPopulation = pSystem.getPopulationLimit(true)
		
		printd("pSystem.getPopulationLimit(true)")
		printd(pSystem.getPopulationLimit(true))
		
		if (iCityPopulation < iMaxPopulation):
			iMaxPopulation = iCityPopulation
		
		printd("iPlanetPopulation")
		printd(iPlanetPopulation)
		printd("pCity.getPopulation()")
		printd(pCity.getPopulation())
		printd("iMaxPopulation")
		printd(iMaxPopulation)
		
		printd("pPlanet.getPopulationLimit(iOwner)")
		printd(pPlanet.getPopulationLimit(iOwner))
		
		# If planet has already maxed out this city's pop then it can't get more
		if (iSystemPopulation < pCity.getPopulation()):
			
			printd("System Population is less than City Population")
		
		if (iPlanetPopulation < iMaxPopulation):
			
			printd("Planet Population is less than Max System Population")
			
			# Planet can't have more than its limit
			if (iPlanetPopulation < pPlanet.getPopulationLimit(iOwner)):
				
				iUsedPopulation = 0
				
				# Loop through all planets and see if all pop is allocated...
				for iPlanetLoop in range(pSystem.getNumPlanets()):
					
					pPlanetLoop = pSystem.getPlanetByIndex(iPlanetLoop)
					iUsedPopulation += pPlanetLoop.getPopulation()
					
					printd("iUsedPopulation")
					printd(iUsedPopulation)
					
				printd("iUsedPopulation")
				printd(iUsedPopulation)
				printd("iMaxPopulation")
				printd(iMaxPopulation)
				
				# Pop is already maxed out, have to take it from somewhere else
#				if (iUsedPopulation >= iCityPopulation):
				if (iUsedPopulation >= iMaxPopulation):
					
					iWorstPlanetRing = self.getSystemWorstPlanetRingWithPopulation(iOwner, pSystem, iPlanetOrbitRing)
					
					printd("iWorstPlanetRing")
					printd(iWorstPlanetRing)
					
					pWorstPlanet = pSystem.getPlanet(iWorstPlanetRing)
					pWorstPlanet.changePopulation(-1)
					
				pPlanet.changePopulation(1)
			
	def doCityHappinessPopLimit(self, pCity, pSystem):
		
		printd("Updating happiness for city %s" %(pCity.getName()))
		
		iMaxPop = pSystem.getPopulationLimit(true)
		iUsedPop = 0
		
		for iPlanetLoop in range(pSystem.getNumPlanets()):
			
			pPlanetLoop = pSystem.getPlanetByIndex(iPlanetLoop)
			iUsedPop += pPlanetLoop.getPopulation()
			
			if (pPlanetLoop.getPopulation() > pPlanetLoop.getPopulationLimit(pCity.getOwner())):
				pPlanetLoop.setPopulation(pPlanetLoop.getPopulationLimit(pCity.getOwner()))
			
		iPopOver = iUsedPop - iMaxPop
		
		printd("Max: %d, Used: %d;  PopOver for this city is %d" %(iMaxPop, iUsedPop, iPopOver))
		
		# If too much population is assigned, remove each one by one
		if (iPopOver > 0):
			
			for iPopLoop in range(iPopOver):
				
				iWorstPlanetWithPop = self.getSystemWorstPlanetRingWithPopulation(pCity.getOwner(), pSystem)
				pPlanet = pSystem.getPlanet(iWorstPlanetWithPop)
				pPlanet.changePopulation(-1)
		
	def getSystemWorstPlanetRingWithPopulation(self, iOwner, pSystem, iActivePlanetOrbitRing = -1):
		
		iWorstPlanetRingID = -1
		iWorstPlanetValue= 100
		
		for iPlanetLoop in range(pSystem.getNumPlanets()):
			
			pPlanet = pSystem.getPlanetByIndex(iPlanetLoop)
			
			# Don't check 'active' planet
			if (pPlanet.getOrbitRing() != iActivePlanetOrbitRing):
				
				# Has to be a populated planet
				if (pPlanet.getPopulation() > 0):
					
					iPlanetTotalValue = 0
					
					iPlanetTotalYield = 0
					
					for iYieldLoop in range(3):
						iPlanetTotalYield += pPlanet.getTotalYield(iOwner, iYieldLoop)
						
					iPlanetTotalValue = iPlanetTotalYield + 0 # To be filled in later (building effects & such)
					
					if (iPlanetTotalValue < iWorstPlanetValue):
						iWorstPlanetValue = iPlanetTotalValue
						iWorstPlanetRingID = pPlanet.getOrbitRing()
		
		return iWorstPlanetRingID
		
#############################################################################################
#		Planetary Buildings
#############################################################################################
	
	def onCityBuildingBuilding(self, argsList):
		'City begins building a Building'
		self.parent.onCityBuildingBuilding(self, argsList)
		pCity, iBuilding = argsList
		
	def onBuildingBuilt(self, argsList):
		'Building Completed'
		self.parent.onBuildingBuilt(self, argsList)
		
		pCity, iBuildingType = argsList
		
		pSystem = self.getSystemAt(pCity.getX(), pCity.getY())
		pPlanet = pSystem.getPlanet(pSystem.getBuildingPlanetRing())
		
		pPlanet.setHasBuilding(iBuildingType, true)
		
		pPlot = CyMap().plot(pCity.getX(), pCity.getY())
		self.updatePlotYield(pPlot)
		
		# Is it one of the single-building types which gets added to the map?
		
#		iStarFortress = CvUtil.findInfoTypeNum(gc.getBuildingInfo, gc.getNumBuildingInfos(), "BUILDING_STAR_FORTRESS")		# Handled specially, since it's placed in the center of a Star System
		iSquadronDefense = CvUtil.findInfoTypeNum(gc.getBuildingInfo, gc.getNumBuildingInfos(), "BUILDING_AIR_DEFENSE_NETWORK")
		iCapitalShipyard = CvUtil.findInfoTypeNum(gc.getBuildingInfo, gc.getNumBuildingInfos(), "BUILDING_CAPITAL_SHIPYARD")
		iSquadronFactory = CvUtil.findInfoTypeNum(gc.getBuildingInfo, gc.getNumBuildingInfos(), "BUILDING_SQUADRON_FACTORY")
		
		aiBuildings = [iSquadronDefense, iCapitalShipyard, iSquadronFactory]#, iStarFortress]
		
		if (iBuildingType in aiBuildings):
			pSystem.setSingleBuildingRingLocation(iBuildingType)
		
		# Update
		pSystem.updateDisplay()
		
	def onProjectBuilt(self, argsList):
		'Project Completed'
		pCity, iProjectType = argsList
		
		if (CyGame().getWinner() == -1):
			
			iProjectAstralGate = CvUtil.findInfoTypeNum(gc.getProjectInfo,gc.getNumProjectInfos(),'PROJECT_ASTRAL_GATE')
			
			if (iProjectType == iProjectAstralGate):
				
				pPlayer = gc.getPlayer(pCity.getOwner())
				iTeam = pPlayer.getTeam()
				
				iVictoryAscension = CvUtil.findInfoTypeNum(gc.getVictoryInfo,gc.getNumVictoryInfos(),'VICTORY_SPACE_RACE')
				iNumGatePieces = gc.getTeam(iTeam).getProjectCount(iProjectAstralGate) + 1
				
				printd("iNumGatePieces")
				printd(iNumGatePieces)
				printd("Threshold:")
				printd(gc.getProjectInfo(iProjectAstralGate).getVictoryThreshold(iVictoryAscension))
				
				# Enough gate pieces to win?
				if (iNumGatePieces >= gc.getProjectInfo(iProjectAstralGate).getVictoryThreshold(iVictoryAscension)):
					pPlot = pPlayer.getCapitalCity().plot()
					pPlot.changeVisibilityCount(CyGame().getActiveTeam(), 1, -1);
					CyCamera().JustLookAtPlot(pPlot)
					CyCamera().SetZoom(0.5)
					self.startWinCountdown(iTeam)

	def onNukeExplosion(self, argsList):
		'Nuke Explosion'
		pPlot, pNukeUnit = argsList
		
		if (pPlot.isCity()):
			
			pSystem = self.getSystemAt(pPlot.getX(), pPlot.getY())
			pBestPlanet = pSystem.getPlanetByIndex(getBestPlanetInSystem(pSystem))
			
			pBestPlanet.setDisabled(true)
			pBestPlanet.setPopulation(0)
			
			self.getAI().doCityAIUpdate(pPlot.getPlotCity())
			
			pSystem.updateDisplay()
		
	def startWinCountdown(self, iTeamID):
		
		self.iWinningTeam = iTeamID
		self.iTimeLeft = 20
	
	def onGameUpdate(self, argsList):
		'sample generic event, called on each game turn slice'
		genericArgs = argsList[0][0]	# tuple of tuple of my args
		turnSlice = genericArgs[0]
		
		if (self.iTimeLeft > 0):
			self.iTimeLeft -= 1
		
		# Winnar!
		if (self.iTimeLeft == 0 and self.iWinningTeam != -1):
			iVictoryAscension = CvUtil.findInfoTypeNum(gc.getVictoryInfo,gc.getNumVictoryInfos(),'VICTORY_SPACE_RACE')
			CyGame().setWinner(self.iWinningTeam, iVictoryAscension)
		
		# Timer to kill Construction ships which have built Starbases... necessary because of potential AI crash issue in AI_unitUpdate (killing the unit while inside the update function)
		if (self.aiKillTimerData != -1):
			iTimer = self.aiKillTimerData[0]
			iTimer -= 1
			
			if (iTimer == 0):
				iPlayer = self.aiKillTimerData[1]
				iUnitID = self.aiKillTimerData[2]
				
				pUnit = gc.getPlayer(iPlayer).getUnit(iUnitID)
				pUnit.kill(true, -1)
				
				self.aiKillTimerData = -1
				
			else:
				self.aiKillTimerData[0] = iTimer
		
#############################################################################################
#		Unit Sounds
#############################################################################################
	
	def onUnitMove(self, argsList):
		'unit move'
		pPlot,pUnit,pOldPlot = argsList
		
		# only play sound if in viewing range of active player
		if (pPlot.isVisible(CyGame().getActiveTeam(), false)):
			
			iUnitType = pUnit.getUnitType()
			
			szTag = ""
			
			if (iUnitType == CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_ADVOCATE_POWER') or iUnitType == CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNITCLASS_ADVOCATE_KNOWLEDGE') or iUnitType == CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNITCLASS_ADVOCATE_RELIGION') or iUnitType == CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNITCLASS_ADVOCATE_SURVIVAL') or iUnitType == CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNITCLASS_ADVOCATE_WEALTH')):
				szTag = "AS3D_UN_ADVOCATE_RUN"
			elif (iUnitType == CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_BATTLESHIP_I') or iUnitType == CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_BATTLESHIP_II') or iUnitType == CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_BATTLESHIP_III')):
				szTag = "AS3D_UN_BATTLESHIP_RUN"
			elif (iUnitType == CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_CARRIER_I') or iUnitType == CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_CARRIER_II') or iUnitType == CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_CARRIER_III')):
				szTag = "AS3D_UN_CARRIER_RUN"
			elif (iUnitType == CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_COLONY_SHIP')):
				szTag = "AS3D_UN_COLONY_SHIP_RUN"
			elif (iUnitType == CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_CONSTRUCT_SHIP')):
				szTag = "AS3D_UN_CONSTRUCTION_RUN"
			elif (iUnitType == CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_CRUISER_I') or iUnitType == CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_CRUISER_II') or iUnitType == CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_CRUISER_III')):
				szTag = "AS3D_UN_CRUISER_RUN"
			elif (iUnitType == CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_DESTROYER_I') or iUnitType == CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_DESTROYER_II') or iUnitType == CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_DESTROYER_III')):
				szTag = "AS3D_UN_DESTROYER_RUN"
			elif (iUnitType == CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_INVASION_SHIP_I') or iUnitType == CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_INVASION_SHIP_II') or iUnitType == CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_INVASION_SHIP_III')):
				szTag = "AS3D_UN_INVASION_RUN"
			elif (iUnitType == CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_PLANETARY_DEFENSE_I') or iUnitType == CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_PLANETARY_DEFENSE_II') or iUnitType == CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_PLANETARY_DEFENSE_III')):
				szTag = "AS3D_UN_PLANETARY_DEFENSE_RUN"
			elif (iUnitType == CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_SCOUT_I') or iUnitType == CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_SCOUT_II') or iUnitType == CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_SCOUT_III')):
				szTag = "AS3D_UN_SCOUT_RUN"
			elif (iUnitType == CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_STEALTH_SHIP_I') or iUnitType == CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_STEALTH_SHIP_II') or iUnitType == CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_STEALTH_SHIP_III')):
				szTag = "AS3D_UN_STEALTH_RUN"
			
			CyInterface().playGeneralSoundAtPlot(szTag, pPlot)
		
#############################################################################################
#		Special Civics Unit Cost Mod
#############################################################################################
	
	def getUnitCostMod(self, iPlayer, iUnit):
		
		iMilitaryCivicOption = CvUtil.findInfoTypeNum(gc.getCivicOptionInfo,gc.getNumCivicOptionInfos(),'CIVICOPTION_MILITARY')
		iLightShipDoctrine = CvUtil.findInfoTypeNum(gc.getCivicInfo,gc.getNumCivicInfos(),'CIVIC_LIGHT_SHIP_DOCTRINE')
		iCapitalShipDoctrine = CvUtil.findInfoTypeNum(gc.getCivicInfo,gc.getNumCivicInfos(),'CIVIC_CAPITAL_SHIP_DOCTRINE')
		iSquadronDoctrine = CvUtil.findInfoTypeNum(gc.getCivicInfo,gc.getNumCivicInfos(),'CIVIC_SQUADRON_DOCTRINE')
		
		pUnitInfo = gc.getUnitInfo(iUnit)
		
		iDestroyerI = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_DESTROYER_I')
		iDestroyerII = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_DESTROYER_II')
		iDestroyerIII = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_DESTROYER_III')
		iCruiserI = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_CRUISER_I')
		iCruiserII = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_CRUISER_II')
		iCruiserIII = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_CRUISER_III')
		iCarrierI = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_CARRIER_I')
		iCarrierII = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_CARRIER_II')
		iCarrierIII = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_CARRIER_III')
		iBattleshipI = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_BATTLESHIP_I')
		iBattleshipII = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_BATTLESHIP_II')
		iBattleshipIII = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_BATTLESHIP_III')
		iSpaceFighterI = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_SPACE_FIGHTER_I')
		iSpaceFighterII = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_SPACE_FIGHTER_II')
		iSpaceFighterIII = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_SPACE_FIGHTER_III')
		iSpaceBomberI = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_SPACE_BOMBER_I')
		iSpaceBomberII = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_SPACE_BOMBER_II')
		iSpaceBomberIII = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_SPACE_BOMBER_III')
		
		aiLightShipDoctrineList = [iDestroyerI, iDestroyerII, iDestroyerIII, iCruiserI, iCruiserII, iCruiserIII]
		aiCapitalShipDoctrineList = [iBattleshipI, iBattleshipII, iBattleshipIII]
		aiSquadronDoctrineList = [iCarrierI, iCarrierII, iCarrierIII, iSpaceFighterI, iSpaceFighterII, iSpaceFighterIII, iSpaceBomberI, iSpaceBomberII, iSpaceBomberIII]
		
		pPlayer = gc.getPlayer(iPlayer)
		
		iMilitaryCivic = pPlayer.getCivics(iMilitaryCivicOption)
		
		if (iMilitaryCivic == iLightShipDoctrine):
			if (iUnit in aiLightShipDoctrineList):
				return 90	# 90% of normal cost
		elif (iMilitaryCivic == iCapitalShipDoctrine):
			if (iUnit in aiCapitalShipDoctrineList):
				return 80	# 80% of normal cost
		elif (iMilitaryCivic == iSquadronDoctrine):
			if (iUnit in aiSquadronDoctrineList):
				return 90	# 90% of normal cost
		
		return -1
	
	def getBuildingCostMod(self, iPlayer, iCityID, iBuilding):
		
		iCostMod = -1
		
		pPlayer = gc.getPlayer(iPlayer)
		pCity = pPlayer.getCity(iCityID)
		
		# Buildings already present in this Star System? If so, cost ramps up for each additional
		if (pCity.getNumRealBuilding(iBuilding) > 0):
			
			fCostMod = 2.0
			
			# Special cases for higher cost
			iBuildingTrainingCompound = CvUtil.findInfoTypeNum(gc.getBuildingInfo,gc.getNumBuildingInfos(),'BUILDING_TRAINING_COMPOUND')
			iBuildingFactory = CvUtil.findInfoTypeNum(gc.getBuildingInfo,gc.getNumBuildingInfos(),'BUILDING_FACTORY')
			iBuildingManufacturingPlant = CvUtil.findInfoTypeNum(gc.getBuildingInfo,gc.getNumBuildingInfos(),'BUILDING_MANUFACTURING_PLANT')
			iBuildingStarFortress = CvUtil.findInfoTypeNum(gc.getBuildingInfo,gc.getNumBuildingInfos(),'BUILDING_STAR_FORTRESS')
			aiIncreasedCostList = [iBuildingTrainingCompound, iBuildingFactory, iBuildingManufacturingPlant, iBuildingStarFortress]
			if (iBuilding in aiIncreasedCostList):
				fCostMod = 3.0
			
			iBuildingCost = gc.getBuildingInfo(iBuilding).getProductionCost()
			
			iExtraCostMod = int(fCostMod * iBuildingCost) - iBuildingCost
			iExtraCost = iExtraCostMod * pCity.getNumRealBuilding(iBuilding)
			
			iCostMod = ((iBuildingCost + iExtraCost) * 1.0) / iBuildingCost
			iCostMod = int(iCostMod * 100)
		
		#printd("iCostMod")
		#printd(iCostMod)
		
		return iCostMod
		
#############################################################################################
#		AI Functionality performed at the start of each turn
#############################################################################################
	
	def doBeginTurnAI(self, iPlayer, bIgnoreHuman=true):
		
#		for i in range(4):
#			printd("*")
#		printd("Beginning player turn AI")
#		for i in range(4):
#			printd("*")
		
		pPlayer = gc.getPlayer(iPlayer)
		pyPlayer = PyPlayer(iPlayer)
		
		# Loop through all of player's cities
		apCityList = pyPlayer.getCityList()
		
		# Loop through all of this player's cities in order to gather nearby Resources
		for pyCity in apCityList:
			
			pCity = pyCity.GetCy()
			
			pSystem = self.getSystemAt(pCity.getX(), pCity.getY())
			
			# Update Population distribution, removing some if player has more assigned than he can support (happiness)
			self.doCityHappinessPopLimit(pCity, pSystem)
			
			# Actual City AI part
			if (not gc.getPlayer(iPlayer).isHuman() or not bIgnoreHuman):
				
				blah = 0
#				AI.doCityAIUpdate(pCity)
			
			# Human updates
			else:
				self.updateHumanCityTurn(pCity)
		
		# UNIT AI (Starbases)
		
		iStarbaseI = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_STARBASE_I')
		iStarbaseII = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_STARBASE_II')
		iStarbaseIII = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_STARBASE_III')
		
		apUnitList = pyPlayer.getUnitList()
		for pyUnit in apUnitList:
			iType = pyUnit.getUnitType()
			if (iType == iStarbaseI or iType == iStarbaseII or iType == iStarbaseIII):
				AI.doStarbaseAI(pyUnit)
		
		# War Stuff
		if (not pPlayer.isHuman()):
			self.doAIWarChance(iPlayer)
		
	def doAIWarChance(self, iPlayer):
		
		pPlayer = gc.getPlayer(iPlayer)
		iTeam = pPlayer.getTeam()
		pTeam = gc.getTeam(iTeam)
		
		# No barbs doing weird stuff
		if (not pTeam.isBarbarian()):
			
			# Loop through all teams
			for iLoopTeam in range(gc.getMAX_CIV_TEAMS()):
				
				pLoopTeam = gc.getTeam(iLoopTeam)
				iLoopPlayer = pLoopTeam.getLeaderID()
				pLoopPlayer = gc.getPlayer(iLoopPlayer)
				
				# Don't declare war on own team, silly
				if (iTeam != iLoopTeam):
					
					# Has met this team?
					if (pTeam.isHasMet(iLoopTeam)):
						
						# Not a vassal of current team
						if (not pLoopTeam.isVassal(iTeam)):
							
							# Determine what the liklihood of forcing a war is
							iAttitude = pPlayer.AI_getAttitude(iLoopPlayer)
							
							iWarChance = 0	# Out of 1000
							
							if (iAttitude == AttitudeTypes.ATTITUDE_FURIOUS):
								iWarChance = 6		# 0.6%
							elif (iAttitude == AttitudeTypes.ATTITUDE_ANNOYED):
								iWarChance = 4		# 0.4%
							elif (iAttitude == AttitudeTypes.ATTITUDE_CAUTIOUS):
								iWarChance = 2		# 0.2%
							elif (iAttitude == AttitudeTypes.ATTITUDE_PLEASED):
								iWarChance = 1		# 0.2%
							elif (iAttitude == AttitudeTypes.ATTITUDE_FRIENDLY):
								iWarChance = 1		# 0.1%
							
							iRoll = CyGame().getSorenRandNum(1000, "Final Frontier: Rolling to see if AI wants to declare war on another player")
							
							# War?
							if (iRoll < iWarChance):
								
								# Now pick a war plan at random
								aiWarPlans = [	WarPlanTypes.WARPLAN_PREPARING_LIMITED,
													WarPlanTypes.WARPLAN_PREPARING_TOTAL, 
													WarPlanTypes.WARPLAN_LIMITED, 
													WarPlanTypes.WARPLAN_TOTAL, 
													WarPlanTypes.WARPLAN_DOGPILE]
								
								iNumWarPlans = len(aiWarPlans)
								
								iPlanRoll = CyGame().getSorenRandNum(iNumWarPlans, "Final Frontier: Picking AI Warplan")
								
								iWarPlan = aiWarPlans[iPlanRoll]
								
								# Plan picked, now do it!
								pTeam.AI_setWarPlan(iLoopTeam, iWarPlan)
								
								printd("Telling Team %d to enact WarPlan %d upon Team %d" %(iTeam, iWarPlan, iLoopTeam))
								
			
	def onCityBuilt(self, argsList):
		'City Built'
		self.parent.onCityBuilt(self, argsList)
		pCity = argsList[0]
		
		pSystem = self.getSystemAt(pCity.getX(), pCity.getY())
		
		pPlayer = gc.getPlayer(pCity.getOwner())
		
		self.initValues()
		
		# New Earth gets extra population when city built
		iTrait = CvUtil.findInfoTypeNum(gc.getTraitInfo,gc.getNumTraitInfos(),'TRAIT_NEW_EARTH')
		if (pPlayer.hasTrait(iTrait)):
			pCity.changePopulation(1)
		
		# Paradise gets free Mag-Lev on every planet
		iTrait = CvUtil.findInfoTypeNum(gc.getTraitInfo,gc.getNumTraitInfos(),'TRAIT_PARADISE')
		if (pPlayer.hasTrait(iTrait)):
			
			iBuildingMagLev = CvUtil.findInfoTypeNum(gc.getBuildingInfo,gc.getNumBuildingInfos(),'BUILDING_MAG_LEV_NETWORK')
			
			for iPlanetLoop in range(pSystem.getNumPlanets()):
				pPlanet = pSystem.getPlanetByIndex(iPlanetLoop)
				pPlanet.setHasBuilding(iBuildingMagLev, true)
				
			pCity.setNumRealBuilding(iBuildingMagLev, pSystem.getNumPlanets())
		
		# Red Syndicate gets 1 free trade route when city built
		iTrait = CvUtil.findInfoTypeNum(gc.getTraitInfo,gc.getNumTraitInfos(),'TRAIT_SYNDICATE')
		if (pPlayer.hasTrait(iTrait)):
			pCity.changeExtraTradeRoutes(1)
		
		# Add free buildings to main planet
		addBasicBuildingsToBestPlanet(pSystem)
		
		self.updatePlotYield(pCity.plot())
		
		# Set the default selected & building planet to the best one
		pBestPlanet = pSystem.getPlanetByIndex(getBestPlanetInSystem(pSystem))
		pSystem.setSelectedPlanet(pBestPlanet.getOrbitRing())
		pSystem.setBuildingPlanetRing(pBestPlanet.getOrbitRing())
		pBestPlanet.setName(pCity.getName())
		
		AI.doCityAIUpdate(pCity)

	def onUnitBuilt(self, argsList):
		'Unit Completed'
		self.parent.onUnitBuilt(self, argsList)
		pCity = argsList[0]
		pUnit = argsList[1]
		
		pPlayer = gc.getPlayer(pCity.getOwner())
		
		iTrait = CvUtil.findInfoTypeNum(gc.getTraitInfo,gc.getNumTraitInfos(),'TRAIT_BROTHERHOOD')
		
		if (pPlayer.hasTrait(iTrait)):
			pUnit.changeExperience(4, 100, false, false, false)
		
	def onCityAcquired(self, argsList):
		'City Acquired'
		self.parent.onCityAcquired(self, argsList)
		
		iPreviousOwner,iNewOwner,pCity,bConquest,bTrade = argsList
		
		# Remove Buildings which don't belong
		
		aiNeverCaptureList = [	CvUtil.findInfoTypeNum(gc.getBuildingInfo,gc.getNumBuildingInfos(),'BUILDING_INTERPLANETARY_BEACON'),
										CvUtil.findInfoTypeNum(gc.getBuildingInfo,gc.getNumBuildingInfos(),'BUILDING_CAPITOL'),
										CvUtil.findInfoTypeNum(gc.getBuildingInfo,gc.getNumBuildingInfos(),'BUILDING_UNIVERSITY'),
										CvUtil.findInfoTypeNum(gc.getBuildingInfo,gc.getNumBuildingInfos(),'BUILDING_ACADEMY_OF_KNOWLEDGE'),
										CvUtil.findInfoTypeNum(gc.getBuildingInfo,gc.getNumBuildingInfos(),'BUILDING_SCHOOL_OF_ZEALOTS'),
										CvUtil.findInfoTypeNum(gc.getBuildingInfo,gc.getNumBuildingInfos(),'BUILDING_TEMPLE_OF_WORSHIP'),
										CvUtil.findInfoTypeNum(gc.getBuildingInfo,gc.getNumBuildingInfos(),'BUILDING_SURVIVAL_DOME'),
										CvUtil.findInfoTypeNum(gc.getBuildingInfo,gc.getNumBuildingInfos(),'BUILDING_STELLAR_MARKET'),
										CvUtil.findInfoTypeNum(gc.getBuildingInfo,gc.getNumBuildingInfos(),'BUILDING_STAR_FORTRESS'),
										CvUtil.findInfoTypeNum(gc.getBuildingInfo,gc.getNumBuildingInfos(),'BUILDING_AIR_DEFENSE_NETWORK'),
										CvUtil.findInfoTypeNum(gc.getBuildingInfo,gc.getNumBuildingInfos(),'BUILDING_CAPITAL_SHIPYARD'),
										CvUtil.findInfoTypeNum(gc.getBuildingInfo,gc.getNumBuildingInfos(),'BUILDING_SQUADRON_FACTORY'),
										CvUtil.findInfoTypeNum(gc.getBuildingInfo,gc.getNumBuildingInfos(),'BUILDING_COMMERCIAL_SATELLITES')]
		
		pSystem = self.getSystemAt(pCity.getX(), pCity.getY())
		
		pSystem.aaiSingleBuildingLocations = []
		
		for iPlanetLoop in range(pSystem.getNumPlanets()):
			pPlanet = pSystem.getPlanetByIndex(iPlanetLoop)
			# Loop through all buildings
			for iBuildingLoop in range(gc.getNumBuildingInfos()):
				# Has this building
				if (pPlanet.isHasBuilding(iBuildingLoop)):
					
					# Never capture it...
					if (iBuildingLoop in aiNeverCaptureList):
						# Remove from Planet
						pPlanet.setHasBuilding(iBuildingLoop, false)
						# Remove from City
						pCity.setNumRealBuilding(iBuildingLoop, 0)
					
					# Roll to see if other buildings should be kept (except for the UN)
					elif (iBuildingLoop != CvUtil.findInfoTypeNum(gc.getBuildingInfo,gc.getNumBuildingInfos(),'BUILDING_UNITED_NATIONS')):
						iRand = CyGame().getSorenRandNum(100, "Rolling to see if captured city should keep buildings")
						if (iRand < 50):	# 50% chance to lose it
							# Remove from Planet
							pPlanet.setHasBuilding(iBuildingLoop, false)
							# Remove from City
							pCity.setNumRealBuilding(iBuildingLoop, pCity.getNumRealBuilding(iBuildingLoop) - 1)
							
		pPlayer = gc.getPlayer(iNewOwner)
		
		# Red Syndicate gets 1 free trade route in captured cities
		iTrait = CvUtil.findInfoTypeNum(gc.getTraitInfo,gc.getNumTraitInfos(),'TRAIT_SYNDICATE')
		if (pPlayer.hasTrait(iTrait)):
			if (pCity.getExtraTradeRoutes() < 1):
				pCity.changeExtraTradeRoutes(1)
		
		# Paradise gets free Mag-Lev on every planet
		iTrait = CvUtil.findInfoTypeNum(gc.getTraitInfo,gc.getNumTraitInfos(),'TRAIT_PARADISE')
		if (pPlayer.hasTrait(iTrait)):
			
			iBuildingMagLev = CvUtil.findInfoTypeNum(gc.getBuildingInfo,gc.getNumBuildingInfos(),'BUILDING_MAG_LEV_NETWORK')
			
			for iPlanetLoop in range(pSystem.getNumPlanets()):
				pPlanet = pSystem.getPlanetByIndex(iPlanetLoop)
				pPlanet.setHasBuilding(iBuildingMagLev, true)
				
			pCity.setNumRealBuilding(iBuildingMagLev, pSystem.getNumPlanets())
		
		AI.doCityAIUpdate(pCity)
		
		pSystem.updateDisplay()
		
	def onCityGrowth(self, argsList):
		'City Population Growth'
		self.parent.onCityGrowth(self, argsList)
		
		pCity = argsList[0]
		iPlayer = argsList[1]
		
		AI.doCityAIUpdate(pCity, 1)
		
	# When a new culture level is reached, assign all unallocated population
	def onCultureExpansion(self, argsList):
		'City Culture Expansion'
		pCity = argsList[0]
		iPlayer = argsList[1]
		
		self.updateHumanCityTurn(pCity)
		
	# This function automatically assigns all unassigned population
	def updateHumanCityTurn(self, pCity):
		
		if (not pCity.AI_avoidGrowth()):
			
			pSystem = self.getSystemAt(pCity.getX(), pCity.getY())
			
			printd("\n\n\nWheeeee: Checking City System at %d, %d" %(pCity.getX(), pCity.getY()))
			
			iMax = pSystem.getPopulationLimit(true)#pCity.getPopulation()
			printd("Max Pop is %d" %(iMax))
			iUnassigned = iMax
			for iPlanetLoop in range(pSystem.getNumPlanets()):
				iUnassigned -= pSystem.getPlanetByIndex(iPlanetLoop).getPopulation()
			
			printd("Population which should be assigned on cultural expansion: %d" %(iUnassigned))
			
			if (iUnassigned > 0):
				AI.doCityAIUpdate(pCity, iUnassigned)
		
#############################################################################################
#		Selecting Planets
#############################################################################################
	
	def onMouseEvent(self, argsList):
		'mouse handler - returns 1 if the event was consumed'
		self.parent.onMouseEvent(self, argsList)
		
		eventType,mx,my,px,py,interfaceConsumed,screens = argsList
		
		if ( px!=-1 and py!=-1 ):
			# <FFQF> Changed Left Click to Double Left Click
			if ( eventType == self.EventLcButtonDblClick ):
				
				for iSystemLoop in range(self.getNumSystems()):
					pSystem = self.getSystem(iSystemLoop)
					pPlot = CyMap().plot(pSystem.getX(), pSystem.getY())
					pCity = pPlot.getPlotCity()
					
					szTagName = pPlot.pickFeatureDummyTag(mx, my)
					
					if (szTagName != ""):
						
						print(szTagName)
						
						# Clicking on a sun out on the map: show Info Screen
						if (szTagName == "FEATURE_DUMMY_TAG_SUN" and pPlot.getRevealedOwner(CyGame().getActiveTeam(), false) == -1):
							if (pPlot.isRevealed(CyGame().getActiveTeam(), false)):
								CvScreensInterface.showPlanetInfoScreen([pPlot.getX(), pPlot.getY()])
						
						iPlanetRing = -1
						
						for iDummyLoop in range(len(aszPlanetDummyTypes)):
							if (szTagName == aszPlanetDummyTypes[iDummyLoop]):
								iPlanetRing = iDummyLoop + 1
						

						if (iPlanetRing != -1):
							
							printd(iPlanetRing)
							printd("System (%d, %d) Num Planets %d" %(pSystem.getX(), pSystem.getY(), pSystem.getNumPlanets()))
							for i in range(pSystem.getNumPlanets()):
								pPlanet = pSystem.getPlanetByIndex(i)
								printd("Planet ID %d's orbit ring %d" %(i, pPlanet.getOrbitRing()))
							
							pPlanet = pSystem.getPlanet(iPlanetRing)
							
							printd("Planet:")
							printd(pPlanet)
							
							if (pPlanet != -1):
								
								printd(iPlanetRing)
								
								CyMessageControl().sendModNetMessage(self.iNetMessage_setSelectedPlanet, pSystem.getX(), pSystem.getY(), iPlanetRing, -1)
#								pSystem.setSelectedPlanet(iPlanetRing)
									
								return 1
		
		return 0
		
#############################################################################################
#		Saving and Loading Junk
#############################################################################################
	
	def onPreSave(self, argsList):
		"called before a game is actually saved"
		self.parent.onPreSave(self, argsList)
		
		printd("Calling onPreSave")
		
		self.saveSystemsToPlots()
		AI.doSavePlayerAIInfos()
		
		CyGame().setScriptData(pickle.dumps(Tutorial.saveData()))
		
		# Player Info
#		for iPlayerLoop in range(gc.getMAX_PLAYERS()):
#			pPlayer = gc.getPlayer(iPlayerLoop)
#			aPlayerData = self.aaiPlayerDatas[iPlayerLoop]
#			
#			pPlayer.setScriptData(pickle.dumps(aPlayerData))
			
	def onLoadGame(self, argsList):
		self.parent.onLoadGame(self, argsList)
		
		self.iWinningTeam = -1
		self.iTimeLeft = 0
		
		self.initValues()
		
		CyGame().makeNukesValid(true)
		
		self.doTerrainExtraCost()
		
		self.loadSystemsFromPlots()
		AI.doLoadPlayerAIInfos()
		
		Tutorial.loadData(pickle.loads(CyGame().getScriptData()))
		
		# Player Info
#		for iPlayerLoop in range(gc.getMAX_PLAYERS()):
#			pPlayer = gc.getPlayer(iPlayerLoop)
#			aData = pickle.loads(pPlayer.getScriptData())
#			self.aaiPlayerDatas[iPlayerLoop] = aData
		
#		printd("Loading game, initing score, updating it, then setting it dirty")
		self.initScoreStuff()
		CyGame().updateScore(true)
		CyInterface().setDirty(InterfaceDirtyBits.Score_DIRTY_BIT, True)
		
	def saveSystemsToPlots(self):
		
		for iSystemLoop in range(self.getNumSystems()):
			
			printd("\nSystem ID %d" %(iSystemLoop))
			
			pSystem = self.getSystem(iSystemLoop)
			
			iX = pSystem.getX()
			iY = pSystem.getY()
			
			printd("Saving System at %d, %d" %(iX, iY))
			
			pPlot = CyMap().plot(iX, iY)
			
			aData = pSystem.getData()
			printd("Saving Data Array:")
			printd(aData)
			
			pPlot.setScriptData(pickle.dumps(aData))
	
	def loadSystemsFromPlots(self):
		
		self.resetSystems()
		
		for iPlotLoop in range(CyMap().numPlots()):
			
			pPlot = CyMap().plotByIndex(iPlotLoop)
			
			# Don't load from a plot with no system
			if (pPlot.getScriptData() != ""):
				
				aData = pickle.loads(pPlot.getScriptData())
				printd("Loading Data Array:")
				printd(aData)
				
				pSystem = CvSystem(pPlot.getX(), pPlot.getY())
				
				printd("\nLoading System at %d, %d" %(pPlot.getX(), pPlot.getY()))
				
				pSystem.setData(aData)
#				pSystem.updateDisplay()
				self.addSystem(pSystem)
		
		self.bUpdateDisplay = true
		
	def onUpdate(self, argsList):
		'Called every frame'
		self.parent.onUpdate(self, argsList)
		
		fDeltaTime = argsList[0]
		
		if (self.bUpdateDisplay):
			self.updateSystemsDisplay()
			self.bUpdateDisplay = false
	
#############################################################################################
#		Stuff which makes life easier with regards to debugging
#############################################################################################
		
	def onKbdEvent(self, argsList):
		'keypress handler - return 1 if the event was consumed'
		self.parent.onKbdEvent(self, argsList)

		eventType,key,mx,my,px,py = argsList
		
		if ( eventType == self.EventKeyDown ):
			theKey=int(key)
			
			if (theKey == int(InputTypes.KB_A)):
				
				return 1
				
				printd("Debug hotkey hit")
				
				self.updateMapYield()
				
				for iPlayerLoop in range(gc.getMAX_CIV_PLAYERS()):
					
					pPlayer = gc.getPlayer(iPlayerLoop)
					
					if (pPlayer.isAlive()):
						
						self.doBeginTurnAI(iPlayerLoop)
				
				pSystem = self.getSystemAt(17,11)
				
				printd("System Single Building Array:")
				printd(pSystem.getSingleBuildingLocations())
				
#				pPlanet = pSystem.getPlanet(3)
#				pPlanet.setHasBuilding(3, true)
	
#############################################################################################
#		Tutorial Stuff
#############################################################################################
				
	def getTutorial(self):
		return Tutorial
		
	def addPopup(self, szTitle, szText, bImmediate=false):
		
		# Don't display popups for autoplay games
		if (gc.getPlayer(CyGame().getActivePlayer()).isAlive()):
			
			popup = PyPopup.PyPopup(-1)
			popup.setHeaderString(szTitle)
			popup.setBodyString(szText)
			
			iState = PopupStates.POPUPSTATE_QUEUED
			
			if (bImmediate):
				iState = PopupStates.POPUPSTATE_IMMEDIATE
			
			popup.launch(true, iState)
	
	def onReligionFounded(self, argsList):
		'Religion Founded'
		self.parent.onReligionFounded(self, argsList)
		iReligion, iFounder = argsList
		
		if (CyGame().getActivePlayer() == iFounder):
			
			# TutorialPopup
			if (not CyUserProfile().getPlayerOption(PlayerOptionTypes.PLAYEROPTION_MODDER_1)):
				if (not Tutorial.isValue()):
					self.addPopup(localText.getText("TXT_KEY_FF_TUTORIAL_VALUE_TITLE", ()), localText.getText("TXT_KEY_FF_TUTORIAL_VALUE", ()))
					Tutorial.setValue(1)

	def onPlotRevealed(self, argsList):
		'Plot Revealed'
		pPlot = argsList[0]
		iTeam = argsList[1]
		
		if (CyGame().getActiveTeam() == iTeam):
			
			if (CyGame().getElapsedGameTurns() > 0):
				
				# First Resource
				iBonus = pPlot.getBonusType(iTeam)
				
				if (iBonus != -1):
					
					# TutorialPopup
					if (not CyUserProfile().getPlayerOption(PlayerOptionTypes.PLAYEROPTION_MODDER_1)):
						if (not Tutorial.isResource()):
							CyCamera().JustLookAtPlot(pPlot)
							CyEngine().triggerEffect(gc.getInfoTypeForString('EFFECT_PING'), pPlot.getPoint())
							
							self.addPopup(localText.getText("TXT_KEY_FF_TUTORIAL_RESOURCE_TITLE", ()), localText.getText("TXT_KEY_FF_TUTORIAL_RESOURCE", ()))
							Tutorial.setResource(1)
				
				# First Black Hole & First Radiation
				
				iFeature = pPlot.getFeatureType()
				iRadiation = CvUtil.findInfoTypeNum(gc.getFeatureInfo,gc.getNumFeatureInfos(),'FEATURE_FALLOUT')
				iGravField = CvUtil.findInfoTypeNum(gc.getFeatureInfo,gc.getNumFeatureInfos(),'FEATURE_GRAV_FIELD')
				
				if (iFeature == iGravField):
					
					# TutorialPopup
					if (not CyUserProfile().getPlayerOption(PlayerOptionTypes.PLAYEROPTION_MODDER_1)):
						if (not Tutorial.isBlackHole()):
							CyCamera().JustLookAtPlot(pPlot)
							CyEngine().triggerEffect(gc.getInfoTypeForString('EFFECT_PING'), pPlot.getPoint())
							self.addPopup(localText.getText("TXT_KEY_FF_TUTORIAL_BLACK_HOLE_TITLE", ()), localText.getText("TXT_KEY_FF_TUTORIAL_BLACK_HOLE", ()))
							Tutorial.setBlackHole(1)
				
				elif (iFeature == iRadiation):
					
					# TutorialPopup
					if (not CyUserProfile().getPlayerOption(PlayerOptionTypes.PLAYEROPTION_MODDER_1)):
						if (not Tutorial.isRadiation()):
							CyCamera().JustLookAtPlot(pPlot)
							CyEngine().triggerEffect(gc.getInfoTypeForString('EFFECT_PING'), pPlot.getPoint())
							self.addPopup(localText.getText("TXT_KEY_FF_TUTORIAL_RADIATION_TITLE", ()), localText.getText("TXT_KEY_FF_TUTORIAL_RADIATION", ()))
							Tutorial.setRadiation(1)
		
class Tutorial:
	
	def __init__(self):
		
		self.bIntro = 0
		self.bCityScreen = 0
		self.bValue = 0
		self.bResource = 0
		self.bBlackHole = 0
		self.bRadiation = 0
		self.bPirates = 0
		
	def isIntro(self):
		return self.bIntro
	def setIntro(self, bValue):
		self.bIntro = bValue
		
	def isCityScreen(self):
		return self.bCityScreen
	def setCityScreen(self, bValue):
		self.bCityScreen = bValue
		
	def isValue(self):
		return self.bValue
	def setValue(self, bValue):
		self.bValue = bValue
		
	def isResource(self):
		return self.bResource
	def setResource(self, bValue):
		self.bResource = bValue
		
	def isBlackHole(self):
		return self.bBlackHole
	def setBlackHole(self, bValue):
		self.bBlackHole = bValue
		
	def isRadiation(self):
		return self.bRadiation
	def setRadiation(self, bValue):
		self.bRadiation = bValue
		
	def isPirates(self):
		return self.bPirates
	def setPirates(self, bValue):
		self.bPirates = bValue
		
	def saveData(self):
		
		aData = []
		
		aData.append(self.bIntro)
		aData.append(self.bCityScreen)
		aData.append(self.bValue)
		aData.append(self.bResource)
		aData.append(self.bBlackHole)
		aData.append(self.bRadiation)
		aData.append(self.bPirates)
		
		return aData
		
	def loadData(self, aData):
		
		iIterator = 0
		
		self.bIntro = aData[iIterator]
		iIterator += 1
		self.bCityScreen = aData[iIterator]
		iIterator += 1
		self.bValue = aData[iIterator]
		iIterator += 1
		self.bResource = aData[iIterator]
		iIterator += 1
		self.bBlackHole = aData[iIterator]
		iIterator += 1
		self.bRadiation = aData[iIterator]
		iIterator += 1
		self.bPirates = aData[iIterator]
		iIterator += 1
		
Tutorial = Tutorial()
