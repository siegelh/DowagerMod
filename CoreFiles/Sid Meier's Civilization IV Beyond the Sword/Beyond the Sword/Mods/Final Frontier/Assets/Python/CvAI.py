# Final Frontier
# Civilization 4 (c) 2007 Firaxis Games

# Designed & Programmed by -	Jon 'Trip' Shafer

from CvPythonExtensions import *
from PyHelpers import PyPlayer
import CvUtil
import CvGameUtils
import CvEventInterface
import math
import pickle

from CvSolarSystem import *

# globals
gc = CyGlobalContext()
localText = CyTranslator()

DefaultUnitAI = UnitAITypes.NO_UNITAI

class CvAI:
	
	def __init__(self):
		
		printd("\n\n\n\n\n init-ing CvAI \n\n\n\n\n")
		self.iNumPlayerAIInfos = 0
		self.apPlayerAIInfos = []
		
	def addPlayerAIInfo(self, pPlayerAIInfo):
		self.apPlayerAIInfos.append(pPlayerAIInfo)
		self.changeNumPlayerAIInfos(1)
		printd("self.iNumPlayerAIInfos")
		printd(self.iNumPlayerAIInfos)
		
	def getPlayerAIInfo(self, iID):
		printd("self.iNumPlayerAIInfos")
		printd(self.iNumPlayerAIInfos)
		
		if (iID < 0 or iID > self.iNumPlayerAIInfos):
			fassert
			
		return self.apPlayerAIInfos[iID]
		
	def getNumPlayerAIInfos(self):
		return self.iNumPlayerAIInfos
	def setNumPlayerAIInfos(self, iValue):
		self.iNumPlayerAIInfos = iValue
	def changeNumPlayerAIInfos(self, iChange):
		self.iNumPlayerAIInfos += iChange
	
	def initPlayerAIInfos(self):
		
		printd("\nInitializing Player AI object array within CvAI")
		
		for iPlayerLoop in range(gc.getMAX_CIV_PLAYERS()):
			
			pInfo = CvPlayerAIInfo(iPlayerLoop)
			
			self.addPlayerAIInfo(pInfo)
	
	def doSavePlayerAIInfos(self):
		
		printd("\nStoring player AI Object information in CvPlayer scriptData")
		
		for iPlayerLoop in range(gc.getMAX_CIV_PLAYERS()):
			
			pPlayer = gc.getPlayer(iPlayerLoop)
			pPlayerAIInfo = self.getPlayerAIInfo(iPlayerLoop)
			
			aSaveInfo = pPlayerAIInfo.saveData()
			
			pPlayer.setScriptData(pickle.dumps(aSaveInfo))
			printd("Saving array to player %d" %(iPlayerLoop))
			printd(aSaveInfo)
		
	def doLoadPlayerAIInfos(self):
		
		printd("\nLoading player AI Object information from CvPlayer scriptData and creating new objects")
		
		for iPlayerLoop in range(gc.getMAX_CIV_PLAYERS()):
			
			pPlayer = gc.getPlayer(iPlayerLoop)
			
			# Add loaded player to member array
			pInfo = CvPlayerAIInfo(iPlayerLoop)
			self.addPlayerAIInfo(pInfo)
			
			# Get data to be imported
			aLoadInfo = pickle.loads(pPlayer.getScriptData())
			
			# Transfer load data
			self.getPlayerAIInfo(iPlayerLoop).loadData(aLoadInfo)
			
			printd("Loading array from player %d scriptData" %(iPlayerLoop))
			printd(aLoadInfo)
			
			
			
		
	
##########################################################
##########################################################
##########################################################

#		CITY UPDATE

##########################################################
##########################################################
##########################################################
	
	def doCityAIUpdate(self, pCity, iPopulationToAssign = -1):
		
		FinalFrontier = CvEventInterface.getEventManager()
		
		pSystem = FinalFrontier.getSystemAt(pCity.getX(), pCity.getY())
		
		iOwner = pCity.getOwner()
		
		iMaxSupportablePop = pSystem.getPopulationLimit(true)
		
		if (iPopulationToAssign > iMaxSupportablePop):
			iPopulationToAssign = iMaxSupportablePop
		
		printd("pSystem.getPopulation()")
		printd(pSystem.getPopulation())
		printd("pSystem.getPopulationLimit()")
		printd(pSystem.getPopulationLimit())
		printd("iPopulationToAssign")
		printd(iPopulationToAssign)
		
		if (iPopulationToAssign == -1):
			iPopulationToAssign = pCity.getPopulation()
		else:
			if (pSystem.getPopulation() + iPopulationToAssign > iMaxSupportablePop):
				iPopulationToAssign = iMaxSupportablePop - pSystem.getPopulation()
		
		if (iPopulationToAssign <= 0):
			return
		
#		printd("\n\nDoing AI for city %s" %(pCity.getName()))
		
		aaiPlanetValues = []
		
		# Loop through all planets and ascertain their value
		for iPlanetLoop in range(pSystem.getNumPlanets()):
			
			pPlanet = pSystem.getPlanetByIndex(iPlanetLoop)
			
			iPlanetRingID = pPlanet.getOrbitRing()
			
			iFood = pPlanet.getTotalYield(iOwner, 0)
			iProd = pPlanet.getTotalYield(iOwner, 1)
			iGold = pPlanet.getTotalYield(iOwner, 2)
			aaiPlanetValues.append([iFood, iProd, iGold, iPlanetRingID])
			
			# Reset the population so it can be redistributed
			if (iPopulationToAssign == pCity.getPopulation()):
				pPlanet.setPopulation(0)
		
		iYieldNeededMost = 0	# Default yield needed most is food
		
		iBestPlanet = 0
			
		FinalFrontier.updatePlotYield(pCity.plot())
		
		iCurrentFood = pCity.getYieldRate(0)
		iCurrentProduction = pCity.getYieldRate(0)
		iSurplusFood = iCurrentFood - (pCity.getPopulation() * gc.getDefineINT("FOOD_CONSUMPTION_PER_POPULATION"))
		
		printd("iPopulationToAssign")
		printd(iPopulationToAssign)
		
		# Place population 1 by 1
		for iPopLoop in range(iPopulationToAssign):
			
			printd("\n   iPopLoop")
			printd(iPopLoop)
			
			# Determine what the new most important yield is
			
			# Always need food to grow
			if (iSurplusFood < 3):
				iYieldNeededMost = 0
			else:
				iYieldNeededMost = 1
			
			# Barebones Production
			if (iCurrentProduction == 0 and iSurplusFood >= 2):
				iYieldNeededMost = 1
				
#			printd("   iYieldNeededMost")
#			printd(iYieldNeededMost)
			
			aaiTempPlanetValues = []
			
			# Create a new list based on the most needed yield
			for aiPlanetValueLoop in aaiPlanetValues:
				iOtherYield = 0
				
				for iLoop in range(3):
					if (iLoop != iYieldNeededMost):
						iOtherYield += aiPlanetValueLoop[iLoop]
				
				aaiTempPlanetValues.append([aiPlanetValueLoop[iYieldNeededMost], iOtherYield, aiPlanetValueLoop[3]])	# The 3 here is the Ring ID
				
			# Sort the list based on value
			aaiTempPlanetValues.sort()
			aaiTempPlanetValues.reverse()
			
			printd("   Sorted list of most valued planets based on yield")
			printd(aaiTempPlanetValues)
			
			for aiTempPlanetValue in aaiTempPlanetValues:
				
				pCurrentPlanet = pSystem.getPlanet(aiTempPlanetValue[2])
				
				if (pCurrentPlanet.getPopulation() < pCurrentPlanet.getPopulationLimit(iOwner)):
					
					iBestPlanet = aiTempPlanetValue[2]
					break
			
			printd("   iBestPlanetRing")
			printd(iBestPlanet)
			
			# Not a valid ring, return (no usable planets!)
			if (iBestPlanet == 0):
				break
			
			pBestPlanet = pSystem.getPlanet(iBestPlanet)
			
			# Add the population
			FinalFrontier.doAddPopulationToPlanet(pSystem, iBestPlanet)
			
			iCurrentFood += pBestPlanet.getTotalYield(iOwner, 0)
			iCurrentProduction += pBestPlanet.getTotalYield(iOwner, 1)
			iSurplusFood = iCurrentFood - (pCity.getPopulation() * gc.getDefineINT("FOOD_CONSUMPTION_PER_POPULATION"))
			
#			printd("   iSurplusFood")
#			printd(iSurplusFood)
			
		FinalFrontier.updatePlotYield(pCity.plot())
		
	def doCityAIProduction(self, pCity):
		
		FinalFrontier = CvEventInterface.getEventManager()
		
		bOverride = false
		
		iPlayer = pCity.getOwner()
		pPlayer = gc.getPlayer(iPlayer)
		iTeam = pPlayer.getTeam()
		pTeam = gc.getTeam(iTeam)
		pSystem = FinalFrontier.getSystemAt(pCity.getX(), pCity.getY())
		
		printd("\n\nDoing AI for %s's City %s" %(pPlayer.getName(), pCity.getName()))
		
		# Small chance of randomly letting the AI do whatever it wants... sometimes the weights can go overboard :)
		iRand = CyGame().getSorenRandNum(100, "Final Frontier: Random roll to see if City AI override exits")
		if (iRand < 15):
			return false
		
		iHabitationSystem = CvUtil.findInfoTypeNum(gc.getBuildingInfo,gc.getNumBuildingInfos(),'BUILDING_HABITATION_SYSTEM')
		
		iCapitalShipyard = CvUtil.findInfoTypeNum(gc.getBuildingInfo,gc.getNumBuildingInfos(),'BUILDING_CAPITAL_SHIPYARD')
		iTrainingCompound = CvUtil.findInfoTypeNum(gc.getBuildingInfo,gc.getNumBuildingInfos(),'BUILDING_TRAINING_COMPOUND')
		
		iSportsArena = CvUtil.findInfoTypeNum(gc.getBuildingInfo,gc.getNumBuildingInfos(),'BUILDING_SPORTS_ARENA')
		iRecyclingCenter = CvUtil.findInfoTypeNum(gc.getBuildingInfo,gc.getNumBuildingInfos(),'BUILDING_RECYCLING_CENTER')
		
		iNutritionFacility = CvUtil.findInfoTypeNum(gc.getBuildingInfo,gc.getNumBuildingInfos(),'BUILDING_NUTRITION_FACILITY')
		iMiningFacility = CvUtil.findInfoTypeNum(gc.getBuildingInfo,gc.getNumBuildingInfos(),'BUILDING_MINING_FACILITY')
		iMagLevNetwork = CvUtil.findInfoTypeNum(gc.getBuildingInfo,gc.getNumBuildingInfos(),'BUILDING_MAG_LEV_NETWORK')
		iCommercialSatellites = CvUtil.findInfoTypeNum(gc.getBuildingInfo,gc.getNumBuildingInfos(),'BUILDING_COMMERCIAL_SATELLITES')
		
		# Cheat a little bit, need to get more Construction Ships
		
		iConstructionShip = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_CONSTRUCT_SHIP')
		
		# Size requirement
		if (pPlayer.getNumCities() > 1):
			if (pCity.getPopulation() >= 4):
				
				iNumUnits = 0
				
				pyPlayer = PyPlayer(iPlayer)
				apUnitList = pyPlayer.getUnitList()
				for pUnitLoop in apUnitList:
					if (pUnitLoop.getUnitType() == iConstructionShip):
						iNumUnits += 1
				
				# Either 0 ships or less than certain # of cities...
				iNumCitiesThreshold = (pPlayer.getNumCities() / 2) + 1
				if ((iNumUnits < iNumCitiesThreshold) or (iNumUnits == 0)):
					
					iRand = CyGame().getSorenRandNum(100, "Rolling to see if AI should be forced to build a Construction Ship")
					
					# 15% Chance of forcing AI to build one of these things
					if (iRand < 15):
						
						printd("   Forcing city to make a Construction Ship :)")
						
						pCity.pushOrder(OrderTypes.ORDER_TRAIN, iConstructionShip, -1, False, False, False, True)
						bOverride = true
						
						return bOverride
			
			
		
		#######################################################################
		#######################################################################
		
		# Determine Weighting for what the AI should build
		
		#######################################################################
		#######################################################################
		
		printd("   Determining weights for various things to construct")
		
		# If any one weight is less than this value then we will let the C++ AI do whatever it wants
		iWeightNeeded = 100
		iDefaultWeight = 0
		
		aszWeightList = []
		
		iIterator = 0
		
		iMilitaryWeightType = iIterator
		aszWeightList.append("MilitaryWeightType")
		iIterator += 1
		iPopulationWeightType = iIterator
		aszWeightList.append("PopulationWeightType")
		iIterator += 1
		iProductionWeightType = iIterator
		aszWeightList.append("ProductionWeightType")
		iIterator += 1
		iCommerceWeightType = iIterator
		aszWeightList.append("CommerceWeightType")
		iIterator += 1
		iHappyWeightType = iIterator
		aszWeightList.append("HappyWeightType")
		iIterator += 1
		iHealthWeightType = iIterator
		aszWeightList.append("HealthWeightType")
		iIterator += 1
		iFoodWeightType = iIterator
		aszWeightList.append("FoodWeightType")
		iIterator += 1
		
		iNumWeights = iIterator
		
		aiWeights = []
		for iWeightLoop in range(iNumWeights):
			aiWeights.append(iDefaultWeight)
		
		
		
		#######################################################################
		# HAPPINESS WEIGHTS
		#######################################################################
		
		printd("   Doing Happiness Weight")
		
		iAngryPop = pCity.angryPopulation(0)
		
		# Angry folks
		if (iAngryPop >= 5):
			aiWeights[iHappyWeightType] += 50
		if (iAngryPop >= 4):
			aiWeights[iHappyWeightType] += 50
		if (iAngryPop >= 3):
			aiWeights[iHappyWeightType] += 50
		if (iAngryPop >= 2):
			aiWeights[iHappyWeightType] += 50
		if (iAngryPop >= 1):
			aiWeights[iHappyWeightType] += 115
		
		# Reduce for number of Nutrition Facilities already present
		iNumSportsArenas = pCity.getNumRealBuilding(iSportsArena)
		if (iNumSportsArenas > 0):
			aiWeights[iHappyWeightType] -= (iNumSportsArenas * 10)
		
		#######################################################################
		# HEALTHINESS WEIGHTS
		#######################################################################
		
		printd("   Doing Healthiness Weight")
		
		iUnhealthy = pCity.badHealth(false) - pCity.goodHealth()
		
		# Angry folks
		if (iUnhealthy >= 5):
			aiWeights[iHealthWeightType] += 50
		if (iUnhealthy >= 4):
			aiWeights[iHealthWeightType] += 50
		if (iUnhealthy >= 3):
			aiWeights[iHealthWeightType] += 50
		if (iUnhealthy >= 2):
			aiWeights[iHealthWeightType] += 60
		if (iUnhealthy >= 1):
			aiWeights[iHealthWeightType] += 80
		
		# Reduce for number of Nutrition Facilities already present
		iNumRecyclingCenters = pCity.getNumRealBuilding(iRecyclingCenter)
		if (iNumRecyclingCenters > 0):
			aiWeights[iHealthWeightType] -= (iNumRecyclingCenters * 10)
		
		
		
		#######################################################################
		# MILITARY WEIGHTS
		#######################################################################
		
		printd("   Doing Military Weight")
		
		# AI should really want to build Capital Shipyard if it doesn't already have one :)
		if (pPlayer.canConstruct(iCapitalShipyard, true, false, false)):	# Not actually sure what the middle 2 arguments do here
			aiWeights[iMilitaryWeightType] += 60
		
		# Presence of a Training Compound
		if (pCity.getNumBuilding(iTrainingCompound) > 0):
			aiWeights[iMilitaryWeightType] += 20
		
		# Current production level changes Military weight: 5 Prod gives +20, 10 Prod gives +40
		aiWeights[iMilitaryWeightType] += (pCity.getProduction() * 4)
		
		# War with other players: 50 weight each
		for iTeamLoop in range(gc.getMAX_CIV_TEAMS()):
			if (iTeamLoop != iTeam):
				pTeamLoop = gc.getTeam(iTeamLoop)
				if (pTeamLoop.isAlive() and not pTeamLoop.isBarbarian()):
					if (pTeamLoop.isAtWar(iTeam)):
						aiWeights[iMilitaryWeightType] += 50
						
						# Also a chance of just quitting, letting the game do what it will during wartime
						iRand = CyGame().getSorenRandNum(100, "Final Frontier: Random roll to see if City AI override exits")
						
						if (iRand < 40):
							return false
		
		# Number of military units per city
		aiWeights[iMilitaryWeightType] += 100 * pPlayer.getNumCities() / pPlayer.getNumMilitaryUnits()
		
		
		#######################################################################
		# POPULATION WEIGHTS
		#######################################################################
		
		iPopToCap = pSystem.getPopulationLimit() - pCity.getPopulation()
		
		printd("   Doing Population Weight; iPopToCap is %d; PopLimit is %d" %(iPopToCap, pSystem.getPopulationLimit()))
		
		# Amount of Pop until this system hits its cap
		if (iPopToCap <= 1):
			aiWeights[iPopulationWeightType] += 60
		if (iPopToCap <= 0):
			aiWeights[iPopulationWeightType] += 60
		if (iPopToCap <= -1):
			aiWeights[iPopulationWeightType] += 60
		
		# Increase for City Size
		aiWeights[iPopulationWeightType] += (pCity.getPopulation() * 20)
		
		# Reduce for number of Habitation Systems already present
		iNumHabitationSystems = pCity.getNumRealBuilding(iHabitationSystem)
		if (iNumHabitationSystems > 0):
			aiWeights[iPopulationWeightType] -= (iNumHabitationSystems * 15)
		
		
		
		#######################################################################
		# FOOD WEIGHTS
		#######################################################################
		
		printd("   Doing Food Weight")
		
		# Amount of food surplus in this city
		if (not pPlayer.isAnarchy()):
			if (pCity.foodDifference(true) <= 3):
				aiWeights[iFoodWeightType] += 40
			if (pCity.foodDifference(true) <= 2):
				aiWeights[iFoodWeightType] += 50
			if (pCity.foodDifference(true) <= 1):
				aiWeights[iFoodWeightType] += 60
			if (pCity.foodDifference(true) <= 0):
				aiWeights[iFoodWeightType] += 70
		
		# Increase for City Size
		aiWeights[iFoodWeightType] += (pCity.getPopulation() * 15)
		
		# Decrease for number of Nutrition Facilities already present
		iNumNutritionFacilities = pCity.getNumRealBuilding(iNutritionFacility)
		if (iNumNutritionFacilities > 0):
			aiWeights[iFoodWeightType] -= (iNumNutritionFacilities * 10)
		
		
		
		#######################################################################
		# PRODUCTION WEIGHTS
		#######################################################################
		
		printd("   Doing Production Weight")
		
		iProductionID = 1
		
		iDivisor = pCity.getBaseYieldRate(iProductionID)
		if (iDivisor == 0):
			iDivisor = 0.5
		
		aiWeights[iProductionWeightType] = int(150 * pCity.getPopulation() / iDivisor)		# Ex: 5 Base Production in 5 Pop System has weight of 150
		
		# Increase for City Size
		aiWeights[iProductionWeightType] += (pCity.getPopulation() * 10)
		
		# Decrease for number of Mining Facilities already present
		iNumMiningFacilities = pCity.getNumRealBuilding(iMiningFacility)
		if (iNumMiningFacilities > 0):
			aiWeights[iProductionWeightType] -= (iNumMiningFacilities * 10)
		
		
		
		#######################################################################
		# COMMERCE WEIGHTS
		#######################################################################
		
		printd("   Doing Commerce Weight")
		
		iCommerceID = 2
		
		iDivisor = pCity.getBaseYieldRate(iCommerceID)
		if (iDivisor == 0):
			iDivisor = 0.5
		
		aiWeights[iCommerceWeightType] = int(250 * pCity.getPopulation() / iDivisor)		# Ex: 5 Base Commerce in 5 Pop System has weight of 250
		
		# Increase for City Size
		aiWeights[iCommerceWeightType] += (pCity.getPopulation() * 10)
		
		# Decrease for number of MagLev Networks already present
		iNumMagLevNetworks = pCity.getNumRealBuilding(iMagLevNetwork)
		if (iNumMagLevNetworks > 0):
			aiWeights[iCommerceWeightType] -= (iNumMagLevNetworks * 20)
		
		
		
		#######################################################################
		# Rank the weights
		#######################################################################
		
		printd("   Ranking the Weights...")
		
		aaiWeightRankList = []
		
		# Create list
		for iWeightLoop in range(iNumWeights):
			aaiWeightRankList.append([aiWeights[iWeightLoop], iWeightLoop])
		
		# Order list by largest weight first
		aaiWeightRankList.sort()
		aaiWeightRankList.reverse()
		
		iBestWeight = aaiWeightRankList[0][0]
		iBestWeightType = aaiWeightRankList[0][1]
		
		for iWeightLoop in range(len(aaiWeightRankList)):
			printd("   WeightType: %s   Value: %d" %(aszWeightList[aaiWeightRankList[iWeightLoop][1]], aaiWeightRankList[iWeightLoop][0]))
		
		
		#######################################################################
		#######################################################################
		
		# Weights finished, now figure out what should be built
		
		#######################################################################
		#######################################################################

		
		# Must meet minimum weight to override
		if (iBestWeight >= iWeightNeeded):
			
			#######################################################################
			# Happiness
			#######################################################################
			
			if (iBestWeightType == iHappyWeightType):
				
				# Loop through the planets in the order of best to worst
				for iPlanetLoop in range(pSystem.getNumPlanets()):
					
					pPlanet = pSystem.getPlanetByIndex(iPlanetLoop)
					
					# Can only use planets in our radius
					if (pPlanet.isPlanetWithinCulturalRange()):
						
						# If we have a good enough food planet without a Habitation System (and can build one), then have the place construct one
						if (pPlayer.canConstruct(iSportsArena, true, false, false)):
							
							if (not pPlanet.isHasBuilding(iSportsArena)):
								
								printd("      Telling planet to build a Sports Arena at Ring %d" %(pPlanet.getOrbitRing()))
								
								pSystem.setBuildingPlanetRing(pPlanet.getOrbitRing())
								pCity.pushOrder(OrderTypes.ORDER_CONSTRUCT, iSportsArena, -1, False, False, False, True)
								bOverride = true
								break
			
			#######################################################################
			# Healtiness
			#######################################################################
			
			if (iBestWeightType == iHealthWeightType):
				
				# Loop through the planets in the order of best to worst
				for iPlanetLoop in range(pSystem.getNumPlanets()):
					
					pPlanet = pSystem.getPlanetByIndex(iPlanetLoop)
					
					# Can only use planets in our radius
					if (pPlanet.isPlanetWithinCulturalRange()):
						
						# If we have a good enough food planet without a Habitation System (and can build one), then have the place construct one
						if (pPlayer.canConstruct(iRecyclingCenter, true, false, false)):
							
							if (not pPlanet.isHasBuilding(iRecyclingCenter)):
								
								printd("      Telling planet to build a iRecyclingCenter at Ring %d" %(pPlanet.getOrbitRing()))
								
								pSystem.setBuildingPlanetRing(pPlanet.getOrbitRing())
								pCity.pushOrder(OrderTypes.ORDER_CONSTRUCT, iRecyclingCenter, -1, False, False, False, True)
								bOverride = true
								break
			
			#######################################################################
			# Military
			#######################################################################
			
			if (iBestWeightType == iMilitaryWeightType):
				
				if (pPlayer.canConstruct(iCapitalShipyard, true, false, false)):
					
					# No Capital Shipyard yet? BUILD IT!
					if (pCity.getNumBuilding(iCapitalShipyard) == 0):
						
						printd("      Telling System to build a Capital Shipyard")
						pCity.pushOrder(OrderTypes.ORDER_CONSTRUCT, iCapitalShipyard, -1, False, False, False, True)
						bOverride = true
			
			#######################################################################
			# Population
			#######################################################################
			
			if (iBestWeightType == iPopulationWeightType):
				
				iFood = 0
				
				# Find the best planet to give us some food
				aiFoodPlanetIndexList = pSystem.getYieldPlanetIndexList(iFood)
				
				# Loop through the planets in the order of best to worst
				for iPlanetLoop in range(len(aiFoodPlanetIndexList)):
					
					pPlanet = pSystem.getPlanetByIndex(iPlanetLoop)
					
					# Can only use planets in our radius
					if (pPlanet.isPlanetWithinCulturalRange()):
						
						# If we have a good enough food planet without a Habitation System (and can build one), then have the place construct one
						if (pPlayer.canConstruct(iHabitationSystem, true, false, false)):
							
							# Good food on this planet, good for future growth
							if (pPlanet.getTotalYield(iPlayer, iFood) >= 3):
								
								# Doesn't already have building
								if (not pPlanet.isHasBuilding(iHabitationSystem)):
									
									printd("      Telling planet to build a Habitation System at Ring %d" %(pPlanet.getOrbitRing()))
									
									pSystem.setBuildingPlanetRing(pPlanet.getOrbitRing())
									pCity.pushOrder(OrderTypes.ORDER_CONSTRUCT, iHabitationSystem, -1, False, False, False, True)
									bOverride = true
									break
			
			#######################################################################
			# Food
			#######################################################################
			
			if (iBestWeightType == iFoodWeightType):
				
				iFood = 0
				
				# Find the best planet to give us some food
				aiFoodPlanetIndexList = pSystem.getYieldPlanetIndexList(iFood)
				
				iPass = 0
				
				# Loop through the planets in the order of best to worst (for food)
				for iPlanetLoop in range(len(aiFoodPlanetIndexList)):
					
					pPlanet = pSystem.getPlanetByIndex(iPlanetLoop)
					
					# Can only use planets in our radius
					if (pPlanet.isPlanetWithinCulturalRange()):
						
						if (pPlayer.canConstruct(iNutritionFacility, true, false, false)):
							
							# Doesn't already have building
							if (not pPlanet.isHasBuilding(iNutritionFacility) and iPass < pCity.getPopulation()):
								
								printd("      Telling planet to build a iNutritionFacility at Ring %d" %(pPlanet.getOrbitRing()))
								
								pSystem.setBuildingPlanetRing(pPlanet.getOrbitRing())
								pCity.pushOrder(OrderTypes.ORDER_CONSTRUCT, iNutritionFacility, -1, False, False, False, True)
								bOverride = true
								break
								
							else:
								iPass += 1
			
			#######################################################################
			# Production
			#######################################################################
			
			if (iBestWeightType == iProductionWeightType):
				
				iFood = 0	 #Add to our food planets :)
				
				# Find the best planet to give us some Production
				aiProductionPlanetIndexList = pSystem.getYieldPlanetIndexList(iFood)
				
				iPass = 0
				
				# Loop through the planets in the order of best to worst (for Food)
				for iPlanetLoop in range(len(aiProductionPlanetIndexList)):
					
					pPlanet = pSystem.getPlanetByIndex(iPlanetLoop)
					
					# Can only use planets in our radius
					if (pPlanet.isPlanetWithinCulturalRange()):
						
						if (pPlayer.canConstruct(iMiningFacility, true, false, false)):
							
							# Doesn't already have building
							if (not pPlanet.isHasBuilding(iMiningFacility) and iPass < pCity.getPopulation()):
								
								printd("      Telling planet to build a iMiningFacility at Ring %d" %(pPlanet.getOrbitRing()))
								
								pSystem.setBuildingPlanetRing(pPlanet.getOrbitRing())
								pCity.pushOrder(OrderTypes.ORDER_CONSTRUCT, iMiningFacility, -1, False, False, False, True)
								bOverride = true
								break
								
							else:
								iPass += 1
						
			#######################################################################
			# Commerce
			#######################################################################
			
			if (iBestWeightType == iCommerceWeightType):
				
				iFood = 0	 #Add to our food planets :)
				
				# Find the best planet to give us some Commerce
				aiCommercePlanetIndexList = pSystem.getYieldPlanetIndexList(iFood)
				
				iPass = 0
				
				# Loop through the planets in the order of best to worst (for Food)
				for iPlanetLoop in range(len(aiCommercePlanetIndexList)):
					
					pPlanet = pSystem.getPlanetByIndex(iPlanetLoop)
					
					# Can only use planets in our radius
					if (pPlanet.isPlanetWithinCulturalRange()):
						
						# Commercial Satellites
						if (pPlayer.canConstruct(iCommercialSatellites, true, false, false)):
							
							# Doesn't already have building
							if (not pPlanet.isHasBuilding(iCommercialSatellites) and iPass < pCity.getPopulation()):
								
								printd("      Telling planet to build a iCommercialSatellites at Ring %d" %(pPlanet.getOrbitRing()))
								
								pSystem.setBuildingPlanetRing(pPlanet.getOrbitRing())
								pCity.pushOrder(OrderTypes.ORDER_CONSTRUCT, iCommercialSatellites, -1, False, False, False, True)
								bOverride = true
								break
								
							# Increment if player CANNOT build a MagLev
							elif (not pPlayer.canConstruct(iMagLevNetwork, true, false, false)):
								iPass += 1
								
						# Can't build Commercial Satellites, go for MagLev instead
						if (pPlayer.canConstruct(iMagLevNetwork, true, false, false)):
							
							# Doesn't already have building
							if (not pPlanet.isHasBuilding(iMagLevNetwork) and iPass < pCity.getPopulation()):
								
								printd("      Telling planet to build a iMagLevNetwork at Ring %d" %(pPlanet.getOrbitRing()))
								
								pSystem.setBuildingPlanetRing(pPlanet.getOrbitRing())
								pCity.pushOrder(OrderTypes.ORDER_CONSTRUCT, iMagLevNetwork, -1, False, False, False, True)
								bOverride = true
								break
								
							else:
								iPass += 1
					
				
				
		
		
		return bOverride
		
		
		
		
		
		
		
		
##########################################################
##########################################################
##########################################################

#		UNIT UPDATE

##########################################################
##########################################################
##########################################################
		
	def doStarbaseAI(self, pUnit):
		
		if (not gc.getPlayer(pUnit.getOwner()).isHuman()):
			
			printd("\n\n\n\n\nDoing AI for %s at (%d, %d)" %(pUnit.getName(), pUnit.getX(), pUnit.getY()))
			
			iOwner = pUnit.getOwner()
			pOwner = gc.getPlayer(iOwner)
			iTeam = pOwner.getTeam()
			pTeam = gc.getTeam(iTeam)
			
			aiBombardPlotValues = []
			
			# Check plots within range to see what's around us
			for iXLoop in range(pUnit.getX()-pUnit.airRange(), pUnit.getX()+pUnit.airRange()):
				for iYLoop in range(pUnit.getY()-pUnit.airRange(), pUnit.getY()+pUnit.airRange()):
					
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
					
					iPlotValue = 0
					
					# Look at all the units on this plot
					for iUnitLoop in range(pLoopPlot.getNumUnits()):
						
						pLoopUnit = pLoopPlot.getUnit(iUnitLoop)
						
						# At war with this unit's owner?
						if (pTeam.isAtWar(pLoopUnit.getTeam())):
							
							# The greater the cost of the unit the more we want to kill it :)
							iCost = gc.getUnitInfo(pLoopUnit.getUnitType()).getProductionCost()
							
							if (iCost > 0):
								iPlotValue += iCost
					
					aiBombardPlotValues.append([iPlotValue, iActiveX, iActiveY])
					
			# Any valid plots to hit?
			if (len(aiBombardPlotValues) > 0):
				
				# Order list of plots based on most valuable first (first element in the list)
				aiBombardPlotValues.sort()
				aiBombardPlotValues.reverse()
				
				# Now attack! :)
				
				aiBombardPlotList = aiBombardPlotValues[0]
				
				iX = aiBombardPlotList[1]
				iY = aiBombardPlotList[2]
				
				pUnit.rangeStrike(iX, iY)
				
	def doConstructionShipAI(self, pUnit):
		
		printd("\n\n\n\n\nDoing AI for %s at (%d, %d)" %(pUnit.getName(), pUnit.getX(), pUnit.getY()))
		
		bOverride = false
		
		iBuild = CvUtil.findInfoTypeNum(gc.getBuildInfo,gc.getNumBuildInfos(),'BUILD_STARBASE')
		
		pPlayer = gc.getPlayer(pUnit.getOwner())
		pTeam = gc.getTeam(pPlayer.getTeam())
		
		# Is there a valid Starbase maker assigned?
		pPlayerAIInfo = self.getPlayerAIInfo(pUnit.getOwner())
		
		iMakerID = pPlayerAIInfo.getUnitIDStarbaseMaker()
		pMakingUnit = pPlayer.getUnit(iMakerID)
		
		bUnitExists = false
		if (pMakingUnit):
			if (pMakingUnit.getName()):
				bUnitExists = true
			
		if (iMakerID == -1 or not bUnitExists):
			pPlayerAIInfo.setUnitIDStarbaseMaker(pUnit.getID())
		
		printd("  Unit we want: %d, Unit we have: %d" %(pPlayerAIInfo.getUnitIDStarbaseMaker(), pUnit.getID()))
		
		# This is the right unit to send...
		if (pPlayerAIInfo.getUnitIDStarbaseMaker() == pUnit.getID()):
			
			printd("    This is the unit we want, trying to Override unit AI")
			
			# Enough gold to do?
			iBuildCost = gc.getBuildInfo(iBuild).getCost() * (100 + pPlayer.calculateInflationRate()) / 100
			
			printd("    Build cost for Starbase is %d" %(iBuildCost))
			
			if (pPlayer.getGold() > iBuildCost):
				
				printd("      Player has enough gold (%d)" %(iBuildCost))
				
#				if (pPlayer.canBuild(CyPlot* pPlot, iBuild, false, false)):
				
				# Has the right techs?
				iTech = CvUtil.findInfoTypeNum(gc.getTechInfo,gc.getNumTechInfos(),'TECH_INDUSTRY_1')
				if (pTeam.isHasTech(iTech)):
					
					printd("         Player has right techs")
					
					# This function is somewhat expensive... should probably call it less frequently
					self.doStarbaseNeed(pUnit.getOwner())
					
					# Should we be trying to send a ship to build a Starbase?
					if (pPlayerAIInfo.getStarbaseTargetValue() > 900):
						
						printd("          Plot value is high enough to send someone to build a Starbase")
						
						printd("            Starbase Target: %s" %(pPlayerAIInfo.getStarbaseTarget()))
						printd("            Unit XY: %d, %d" %(pUnit.getX(), pUnit.getY()))
						
						# Already in the right location?
						iX, iY = pPlayerAIInfo.getStarbaseTarget()
						if (pUnit.getX() == iX and pUnit.getY() == iY):
							
							printd("          Unit at the right location to build Starbase")
							
							# Not already building Starbase?
							if (pUnit.getBuildType() != iBuild):
								
								# Tell unit to build Starbase
								printd("            Telling unit to build Starbase")
								# Can build?
								if (pUnit.canBuild(pUnit.plot(), iBuild, true)):
									
									bCanDo = true
									
									# Loop through all units on the plot, if there are any Construction Ships already building a Starbase then disallow more	
									for iUnitLoop in range(pUnit.plot().getNumUnits()):
										pUnitLoop = pUnit.plot().getUnit(iUnitLoop)
										if (pUnitLoop.getBuildType() == CvUtil.findInfoTypeNum(gc.getBuildInfo,gc.getNumBuildInfos(),'BUILD_STARBASE')):
											bCanDo = false
									
									if (bCanDo):
										printd("              Able to build Starbase, pushing mission & setting override")
										pUnit.getGroup().pushMission(MissionTypes.MISSION_BUILD, iBuild, -1, -1, false, true, MissionAITypes.MISSIONAI_BUILD, pUnit.plot(), pUnit)
										bOverride = true
						
						# Unit not in the right spot, send him in the right direction
						else:
							printd("          Unit isn't in the right spot yet, so we're going to tell him to move there")
							if (pUnit.canMoveInto(CyMap().plot(iX, iY), false, false, false)):
								printd("            And we did")
								pUnit.getGroup().pushMoveToMission(iX, iY)
								pUnit.finishMoves()
								bOverride = true
		
		# Need more gold!
		else:
			pPlayer.AI_setExtraGoldTarget(250)
							
						
		printd("Override unit AI? : %s\n\n\n" %(bOverride))
		return bOverride
		
	def doStarbaseNeed(self, iPlayer):
		
		# Loop through all plots, see if there are any really good places to get resources
		
		pBestPlot, iBestValue = self.findBestResourcePlot(iPlayer, true)
		
		printd("\npBestPlot")
		printd(pBestPlot)
		printd("iBestValue")
		printd(iBestValue)
		
		if (pBestPlot != -1):
			printd("   X: %d Y: %d" %(pBestPlot.getX(), pBestPlot.getY()) )
			
			# 700 is our cutoff point for a good value
			if (iBestValue >= 700):
				
				pPlayerAIInfo = self.getPlayerAIInfo(iPlayer)
				
				# Set the player's current Starbase destination
				pPlayerAIInfo.setStarbaseTarget(pBestPlot.getX(), pBestPlot.getY())
				pPlayerAIInfo.setStarbaseTargetValue(iBestValue)
		
	def findBestResourcePlot(self, iPlayer=-1, bCheckForVisibility=false):
		
		pBestPlot = -1
		iBestValue = -1
		
		pPlayer = -1
		iTeam = -1
		if (iPlayer >= 0):
			pPlayer = gc.getPlayer(iPlayer)
			iTeam = pPlayer.getTeam()
		
		printd("\n    Checking for best plot to build a Starbase \n")
		
		for iPlotLoop in range(CyMap().numPlots()):
			pLoopPlot = CyMap().plotByIndex(iPlotLoop)
#			printd("Checking value of plot at %d, %d" %(pLoopPlot.getX(), pLoopPlot.getY()))
			
			# If we're supposed to be checking for a player's visibility then only check this plot if it's revealed
			if (bCheckForVisibility):
				if (not pLoopPlot.isRevealed(iTeam, false)):
					continue
			
			iDistanceFromCapital = CyMap().getGridWidth()
			
			if (pPlayer.getCapitalCity()):
				iDistanceFromCapital = CyMap().calculatePathDistance(pPlayer.getCapitalCity().plot(), pLoopPlot)
			
			# Don't look too far away (performance, more than anything)
			iMaxRange = max(CyMap().getGridWidth() / 2, 60)
			if (iDistanceFromCapital > 0 and iDistanceFromCapital < iMaxRange):
				
				# Will be a value between 0 and the width of the map * 100, e.g. 64 * 100 (6400)
				iDistanceValueMod = (CyMap().getGridWidth() * 100) / iDistanceFromCapital
				iDistanceValueMod = math.sqrt(iDistanceValueMod) * 10
				
				iPlotValue = 0
				iNumBonuses = 0
				
				for iXSearchLoop in range(pLoopPlot.getX()-2, pLoopPlot.getX()+3):
					for iYSearchLoop in range(pLoopPlot.getY()-2, pLoopPlot.getY()+3):
						pSearchPlot = CyMap().plot(iXSearchLoop, iYSearchLoop)
						
						# Don't search unseen plots in range of the one we're looking at either
						if (bCheckForVisibility):
							if (not pSearchPlot.isRevealed(iTeam, false)):
								continue
						
						# Bonus present?
						if (pSearchPlot.getBonusType(iTeam) != -1):
							# Bonus unowned?
							if (pSearchPlot.getOwner() == -1):
								iNumBonuses += 1
				
				if (iNumBonuses > 0):
					iBonusValueMod = ((1280 / 3) * iNumBonuses)
					iPlotValue = iDistanceValueMod + iBonusValueMod
					printd("      Plot value for (%d, %d) is %d: Distance: %d, Bonus: %d" %(pLoopPlot.getX(), pLoopPlot.getY(), iPlotValue, iDistanceValueMod, iBonusValueMod))
				
				# Don't build anywhere except in empty space & asteroids
				if (pLoopPlot.getFeatureType() != -1 and pLoopPlot.getFeatureType() != CvUtil.findInfoTypeNum(gc.getFeatureInfo,gc.getNumFeatureInfos(),'FEATURE_FOREST')):
					iPlotValue = 0
					
				# Little extra bonus for being in Asteroids (defense)
				if (pLoopPlot.getFeatureType() == CvUtil.findInfoTypeNum(gc.getFeatureInfo,gc.getNumFeatureInfos(),'FEATURE_FOREST')):
					iPlotValue += 15
					
				# If this plot has the most resources in range from what we've found
				if (iPlotValue > iBestValue):
					iBestValue = iPlotValue
					pBestPlot = pLoopPlot
			
		return [pBestPlot, iBestValue]
		
class CvPlayerAIInfo:
	
	def __init__(self, iID):
		
		self.iID = iID
		
		self.iStarbaseTargetValue = 0
		
		self.iXStarbaseTarget = -1
		self.iYStarbaseTarget = -1
		
		self.iUnitIDStarbaseMaker = -1
		
	def getID(self):
		return self.iID
	def setID(self, iValue):
		self.iID = iValue
		
	def getStarbaseTargetValue(self):
		return self.iStarbaseTargetValue
	def setStarbaseTargetValue(self, iValue):
		self.iStarbaseTargetValue = iValue

	def getStarbaseTarget(self):
		return [self.iXStarbaseTarget, self.iYStarbaseTarget]
	def setStarbaseTarget(self, iX, iY):
		self.iXStarbaseTarget = iX
		self.iYStarbaseTarget = iY
		
	def getXStarbaseTarget(self):
		return self.iXStarbaseTarget
	def setXStarbaseTarget(self, iValue):
		self.iXStarbaseTarget = iValue

	def getYStarbaseTarget(self):
		return self.iYStarbaseTarget
	def setYStarbaseTarget(self, iValue):
		self.iYStarbaseTarget = iValue
		
	def getUnitIDStarbaseMaker(self):
		return self.iUnitIDStarbaseMaker
	def setUnitIDStarbaseMaker(self, iValue):
		printd("Setting Starbase Maker Unit ID to %d for player %d" %(iValue, self.getID()))
		self.iUnitIDStarbaseMaker = iValue
		
	def saveData(self):
		
		aData = []
		
		aData.append(self.iID)
		aData.append(self.iStarbaseTargetValue)
		aData.append(self.iXStarbaseTarget)
		aData.append(self.iYStarbaseTarget)
		aData.append(self.iUnitIDStarbaseMaker)
		
		return aData
		
	def loadData(self, aData):
		
		iIterator = 0
		
		self.setID(aData[iIterator])
		iIterator += 1
		self.setStarbaseTargetValue(aData[iIterator])
		iIterator += 1
		self.setXStarbaseTarget(aData[iIterator])
#		self.iXStarbaseTarget = aData[iIterator]
		iIterator += 1
		self.setYStarbaseTarget(aData[iIterator])
#		self.iYStarbaseTarget = aData[iIterator]
		iIterator += 1
		self.setUnitIDStarbaseMaker(aData[iIterator])