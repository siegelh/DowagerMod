# Final Frontier
# Civilization 4 (c) 2007 Firaxis Games

# Designed & Programmed by:	Jon 'Trip' Shafer

import CvUtil
from CvPythonExtensions import *
import CvEventInterface

import CvSolarSystem
import CvAI

# globals
gc = CyGlobalContext()
localText = CyTranslator()

class CvGameUtils:
	"Miscellaneous game functions"
	def __init__(self): 
		pass
	
	def isVictoryTest(self):
		if ( gc.getGame().getElapsedGameTurns() > 10 ):
			return True
		else:
			return False

	def isVictory(self, argsList):
		eVictory = argsList[0]
		return True

	def isPlayerResearch(self, argsList):
		ePlayer = argsList[0]
		return True

	def getExtraCost(self, argsList):
		ePlayer = argsList[0]
		return 0

	def createBarbarianCities(self):
		return False
		
	def createBarbarianUnits(self):
		return False
		
	def skipResearchPopup(self,argsList):
		ePlayer = argsList[0]
		return False
		
	def showTechChooserButton(self,argsList):
		ePlayer = argsList[0]
		return True

	def getFirstRecommendedTech(self,argsList):
		ePlayer = argsList[0]
		return TechTypes.NO_TECH

	def getSecondRecommendedTech(self,argsList):
		ePlayer = argsList[0]
		eFirstTech = argsList[1]
		return TechTypes.NO_TECH
	
	def canRazeCity(self,argsList):
		iRazingPlayer, pCity = argsList
		return True
	
	def canDeclareWar(self,argsList):
		iAttackingTeam, iDefendingTeam = argsList
		return True
	
	def skipProductionPopup(self,argsList):
		pCity = argsList[0]
		return False
		
	def showExamineCityButton(self,argsList):
		pCity = argsList[0]
		return True

	def getRecommendedUnit(self,argsList):
		pCity = argsList[0]
		return UnitTypes.NO_UNIT

	def getRecommendedBuilding(self,argsList):
		pCity = argsList[0]
		return BuildingTypes.NO_BUILDING

	def updateColoredPlots(self):
		return False

	def isActionRecommended(self,argsList):
		pUnit = argsList[0]
		iAction = argsList[1]
		return False
	
	def unitCannotMoveInto(self,argsList):
		ePlayer = argsList[0]		
		iUnitId = argsList[1]
		iPlotX = argsList[2]
		iPlotY = argsList[3]
		return False

	def cannotHandleAction(self,argsList):
		pPlot = argsList[0]
		iAction = argsList[1]
		bTestVisible = argsList[2]
		
		# This is all disabled via XML anyways
		
		
#		iActionMissionType = gc.getActionInfo(iAction).getMissionType()
#		iActionBuildType = gc.getActionInfo(iAction).getMissionData()
#		
#		# None of this actually works because for some reason this function always gets passed a null plot.  Maybe I'll fix it one day.
#		
#		if (iActionMissionType == MissionTypes.MISSION_BUILD):
#			
#			print("Trying to build something at %d, %d" %(pPlot.getX(), pPlot.getY()))
#			
#			if (iActionBuildType == CvUtil.findInfoTypeNum(gc.getBuildInfo, gc.getNumBuildInfos(), "BUILD_STARBASE")):
#				
#				iUnitStarbaseID = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_STARBASE_I')
#				
#				for iUnitLoop in range(pPlot.getNumUnits()):
#					pUnit = pPlot.getUnit(iUnitLoop)
#					if (pUnit.getUnitType() == iUnitStarbaseID):
#						return True
		
		return False

	def canBuild(self,argsList):
		iX, iY, iBuild, iPlayer = argsList
		
		# Disallow building of stuff on Hostile Terrain
		
		pPlot = CyMap().plot(iX, iY)
		
		# Has a feature
		if (pPlot.getFeatureType() != -1):
			
			iFeatureGravField = CvUtil.findInfoTypeNum(gc.getFeatureInfo,gc.getNumFeatureInfos(),'FEATURE_GRAV_FIELD')
			
			pFeatureInfo = gc.getFeatureInfo(pPlot.getFeatureType())
			
			# Damaging terrain
			if (pFeatureInfo.getTurnDamage() > 0):
				return 0
				
			# Grav Field
			if (pPlot.getFeatureType() == iFeatureGravField):
				return 0
		
		# Starbase restriction
		iBuildStarbase = CvUtil.findInfoTypeNum(gc.getBuildInfo,gc.getNumBuildInfos(),'BUILD_STARBASE')
		if (iBuild == iBuildStarbase):
			
			FinalFrontier = CvEventInterface.getEventManager()
			if (not FinalFrontier.canBuildStarbase(pPlot)):
				return 0
		
		return -1	# Returning -1 means ignore; 0 means Build cannot be performed; 1 or greater means it can
		
	def cannotFoundCity(self,argsList):
		iPlayer, iPlotX, iPlotY = argsList
		
		pPlot = CyMap().plot(iPlotX, iPlotY)
		
		if (pPlot):
			
			iFeatureIDSolarSystem = CvUtil.findInfoTypeNum(gc.getFeatureInfo,gc.getNumFeatureInfos(),'FEATURE_SOLAR_SYSTEM')
			
			if (pPlot.getFeatureType() != iFeatureIDSolarSystem):
				return True
			
		return False

	def cannotSelectionListMove(self,argsList):
		pPlot = argsList[0]
		bAlt = argsList[1]
		bShift = argsList[2]
		bCtrl = argsList[3]
		return False

	def cannotSelectionListGameNetMessage(self,argsList):
		eMessage = argsList[0]
		iData2 = argsList[1]
		iData3 = argsList[2]
		iData4 = argsList[3]
		iFlags = argsList[4]
		bAlt = argsList[5]
		bShift = argsList[6]
		return False

	def cannotDoControl(self,argsList):
		eControl = argsList[0]
		return False

	def canResearch(self,argsList):
		ePlayer = argsList[0]
		eTech = argsList[1]
		bTrade = argsList[2]
		return False

	def cannotResearch(self,argsList):
		ePlayer = argsList[0]
		eTech = argsList[1]
		bTrade = argsList[2]
		return False

	def canDoCivic(self,argsList):
		ePlayer = argsList[0]
		eCivic = argsList[1]
		return False

	def cannotDoCivic(self,argsList):
		ePlayer = argsList[0]
		eCivic = argsList[1]
		return False
		
	def canTrain(self,argsList):
		pCity = argsList[0]
		eUnit = argsList[1]
		bContinue = argsList[2]
		bTestVisible = argsList[3]
		return False

	def cannotTrain(self,argsList):
		pCity = argsList[0]
		eUnit = argsList[1]
		bContinue = argsList[2]
		bTestVisible = argsList[3]
		
		# Block out the rest
		return False
		
		iStarbaseI = CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), "UNIT_STARBASE_I")
		iStarbaseII = CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), "UNIT_STARBASE_II")
		iStarbaseIII = CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), "UNIT_STARBASE_III")
		
		if (eUnit == iStarbaseI or eUnit == iStarbaseII or eUnit == iStarbaseIII):
			return True
		
		return False

	def canConstruct(self,argsList):
		pCity = argsList[0]
		eBuilding = argsList[1]
		bContinue = argsList[2]
		bTestVisible = argsList[3]
		bIgnoreCost = argsList[4]
		
		return False

	def cannotConstruct(self,argsList):
		pCity = argsList[0]
		eBuilding = argsList[1]
		bContinue = argsList[2]
		bTestVisible = argsList[3]
		bIgnoreCost = argsList[4]
		
		FinalFrontier = CvEventInterface.getEventManager()
		
		pSystem = FinalFrontier.getSystemAt(pCity.getX(), pCity.getY())
		pPlanet = pSystem.getPlanet(pSystem.getBuildingPlanetRing())
		
		# Cannot build a building if it already exists on the currently "Building" Planet
		if (pPlanet):
			if (pPlanet.isHasBuilding(eBuilding)):
				return True
		
		# Prereqs are required for the Planet
		if (eBuilding > -1):
			pBuildingInfo = gc.getBuildingInfo(eBuilding)
			for iNeededBuildingLoop in range(gc.getNumBuildingInfos()):
				if (pBuildingInfo.isBuildingClassNeededInCity(iNeededBuildingLoop)):
					if (not pPlanet.isHasBuilding(iNeededBuildingLoop)):
						return True
		
		# Don't allow more than one of certain buildings
		iStarFortress = CvUtil.findInfoTypeNum(gc.getBuildingInfo, gc.getNumBuildingInfos(), "BUILDING_STAR_FORTRESS")
		iSquadronDefense = CvUtil.findInfoTypeNum(gc.getBuildingInfo, gc.getNumBuildingInfos(), "BUILDING_AIR_DEFENSE_NETWORK")
		iCapitalShipyard = CvUtil.findInfoTypeNum(gc.getBuildingInfo, gc.getNumBuildingInfos(), "BUILDING_CAPITAL_SHIPYARD")
		iSquadronFactory = CvUtil.findInfoTypeNum(gc.getBuildingInfo, gc.getNumBuildingInfos(), "BUILDING_SQUADRON_FACTORY")
		if (eBuilding == iStarFortress or eBuilding == iSquadronDefense or eBuilding == iCapitalShipyard or eBuilding == iSquadronFactory):
			if (pCity.getNumRealBuilding(eBuilding) > 0):
				return True
		
		return False
		
	def canCreate(self,argsList):
		pCity = argsList[0]
		eProject = argsList[1]
		bContinue = argsList[2]
		bTestVisible = argsList[3]
		return False

	def cannotCreate(self,argsList):
		pCity = argsList[0]
		eProject = argsList[1]
		bContinue = argsList[2]
		bTestVisible = argsList[3]
		return False

	def canMaintain(self,argsList):
		pCity = argsList[0]
		eProcess = argsList[1]
		bContinue = argsList[2]
		return False

	def cannotMaintain(self,argsList):
		pCity = argsList[0]
		eProcess = argsList[1]
		bContinue = argsList[2]
		return False

	def AI_chooseTech(self,argsList):
		ePlayer = argsList[0]
		bFree = argsList[1]
		return TechTypes.NO_TECH

	def AI_chooseProduction(self,argsList):
		pCity = argsList[0]
		
		FinalFrontier = CvEventInterface.getEventManager()
		
		bOverride = FinalFrontier.getAI().doCityAIProduction(pCity)
		
		return bOverride

	def AI_unitUpdate(self,argsList):
		pUnit = argsList[0]
		
		FinalFrontier = CvEventInterface.getEventManager()
		
		bOverride = false
		
		# Only do it for actual AI units, not automated human ones
		pPlayer = gc.getPlayer(pUnit.getOwner())
		if (not pPlayer.isHuman()):
			iConstructShip = CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), "UNIT_CONSTRUCT_SHIP")
			if (pUnit.getUnitType() == iConstructShip):
				bOverride = FinalFrontier.getAI().doConstructionShipAI(pUnit)
		
		return bOverride

	def AI_doWar(self,argsList):
		eTeam = argsList[0]
		return False

	def AI_doDiplo(self,argsList):
		ePlayer = argsList[0]
		return False

	def calculateScore(self,argsList):
		ePlayer = argsList[0]
		bFinal = argsList[1]
		bVictory = argsList[2]
		
		FinalFrontier = CvEventInterface.getEventManager()
		iMaxPopulation = FinalFrontier.iMaxPopulation
		
		iPopulationScore = CvUtil.getScoreComponent(gc.getPlayer(ePlayer).getPopScore(), gc.getGame().getInitPopulation(), iMaxPopulation, gc.getDefineINT("SCORE_POPULATION_FACTOR"), True, bFinal, bVictory)
#		print("Pop Score Stuff")
#		print(gc.getPlayer(ePlayer).getPopScore())
#		print(gc.getGame().getInitPopulation())
#		print(iMaxPopulation)
#		print(iPopulationScore)
		#iPlayerLandScore = gc.getPlayer(ePlayer).getLandScore()
		iPlayerLandScore = gc.getPlayer(ePlayer).getTotalLand()
		iLandScore = CvUtil.getScoreComponent(iPlayerLandScore , gc.getGame().getInitLand(), gc.getGame().getMaxLand(), gc.getDefineINT("SCORE_LAND_FACTOR"), True, bFinal, bVictory)
#		print("Land Score Stuff")
#		print(iPlayerLandScore)
#		print(gc.getGame().getInitLand())
#		print(gc.getGame().getMaxLand())
#		print(iLandScore)
		iTechScore = CvUtil.getScoreComponent(gc.getPlayer(ePlayer).getTechScore(), gc.getGame().getInitTech(), gc.getGame().getMaxTech(), gc.getDefineINT("SCORE_TECH_FACTOR"), True, bFinal, bVictory)
		iWondersScore = CvUtil.getScoreComponent(gc.getPlayer(ePlayer).getWondersScore(), gc.getGame().getInitWonders(), gc.getGame().getMaxWonders(), gc.getDefineINT("SCORE_WONDER_FACTOR"), False, bFinal, bVictory)
		
		iTotalScore = int(iLandScore + iWondersScore + iTechScore + iPopulationScore)
		
#		print("Player %d Score: %d    Pop: %d    Land: %d    Tech: %d    Wonders:    %d" %(ePlayer, iTotalScore, iPopulationScore, iLandScore, iTechScore, iWondersScore))
		
		return iTotalScore

	def doHolyCity(self):
		return False

	def doHolyCityTech(self,argsList):
		eTeam = argsList[0]
		ePlayer = argsList[1]
		eTech = argsList[2]
		bFirst = argsList[3]
		return False

	def doGold(self,argsList):
		ePlayer = argsList[0]
		return False

	def doResearch(self,argsList):
		ePlayer = argsList[0]
		return False

	def doGoody(self,argsList):
		ePlayer = argsList[0]
		pPlot = argsList[1]
		pUnit = argsList[2]
		return False

	def doGrowth(self,argsList):
		pCity = argsList[0]
		return False

	def doProduction(self,argsList):
		pCity = argsList[0]
		return False

	def doCulture(self,argsList):
		pCity = argsList[0]
		return False

	def doPlotCulture(self,argsList):
		pCity = argsList[0]
		bUpdate = argsList[1]
		return False

	def doReligion(self,argsList):
		pCity = argsList[0]
		return False

	def cannotSpreadReligion(self,argsList):
		iOwner, iUnitID, iReligion, iX, iY = argsList[0]
		return False

	def doGreatPeople(self,argsList):
		pCity = argsList[0]
		return False

	def doMeltdown(self,argsList):
		pCity = argsList[0]
		return False
	
	def doReviveActivePlayer(self,argsList):
		"allows you to perform an action after an AIAutoPlay"
		iPlayer = argsList[0]
		return False
	
	def doPillageGold(self, argsList):
		"controls the gold result of pillaging"
		pPlot = argsList[0]
		pUnit = argsList[1]
		
		iPillageGold = 0
		iPillageGold = CyGame().getSorenRandNum(gc.getImprovementInfo(pPlot.getImprovementType()).getPillageGold(), "Pillage Gold 1")
		iPillageGold += CyGame().getSorenRandNum(gc.getImprovementInfo(pPlot.getImprovementType()).getPillageGold(), "Pillage Gold 2")

		iPillageGold += (pUnit.getPillageChange() * iPillageGold) / 100
		
		return iPillageGold
	
	def doCityCaptureGold(self, argsList):
		"controls the gold result of capturing a city"
		
		pOldCity = argsList[0]
		
		iCaptureGold = 0
		
		iCaptureGold += gc.getDefineINT("BASE_CAPTURE_GOLD")
		iCaptureGold += (pOldCity.getPopulation() * gc.getDefineINT("CAPTURE_GOLD_PER_POPULATION"))
		iCaptureGold += CyGame().getSorenRandNum(gc.getDefineINT("CAPTURE_GOLD_RAND1"), "Capture Gold 1")
		iCaptureGold += CyGame().getSorenRandNum(gc.getDefineINT("CAPTURE_GOLD_RAND2"), "Capture Gold 2")

		if (gc.getDefineINT("CAPTURE_GOLD_MAX_TURNS") > 0):
			iCaptureGold *= cyIntRange((CyGame().getGameTurn() - pOldCity.getGameTurnAcquired()), 0, gc.getDefineINT("CAPTURE_GOLD_MAX_TURNS"))
			iCaptureGold /= gc.getDefineINT("CAPTURE_GOLD_MAX_TURNS")
		
		return iCaptureGold
	
	def citiesDestroyFeatures(self,argsList):
		iX, iY= argsList
		return False
			
	def canFoundCitiesOnWater(self,argsList):
		iX, iY= argsList
		return True
		
	def doCombat(self,argsList):
		pSelectionGroup, pDestPlot = argsList
		return False

	def getConscriptUnitType(self, argsList):
		iPlayer = argsList[0]
		iConscriptUnitType = -1 #return this with the value of the UNIT TYPE you want to be conscripted
		
		return iConscriptUnitType

	def getCityFoundValue(self, argsList):
		iPlayer, iPlotX, iPlotY = argsList
		iFoundValue = -1 # Any value besides -1 will be used
		
		pPlot = CyMap().plot(iPlotX, iPlotY)
		iFeatureIDSolarSystem = CvUtil.findInfoTypeNum(gc.getFeatureInfo,gc.getNumFeatureInfos(),'FEATURE_SOLAR_SYSTEM')
		
		if (pPlot.getFeatureType() == iFeatureIDSolarSystem and not pPlot.isCity()):
			
			#print("Determing Found Value for Plot at %d, %d" %(iPlotX, iPlotY))
			
			iFoundValue = 1000
			
			# Determine System value by planetary composition
			if (CyGame().getElapsedGameTurns() > 0):
				
				iFoundValue = 0
				
				FinalFrontier = CvEventInterface.getEventManager()
				pSystem = FinalFrontier.getSystemAt(iPlotX, iPlotY)
				
				for iPlanetLoop in range(pSystem.getNumPlanets()):
					pPlanet = pSystem.getPlanetByIndex(iPlanetLoop)
					
					iPlanetValue = 0
					
					# Green Planet
					if (pPlanet.getPlanetType() == CvSolarSystem.iPlanetTypeGreen):
						iPlanetValue = 400
					# Not Green Planet
					else:
						iPlanetValue = 200
					
					# Planet Size
					iPlanetValue *= (pPlanet.getPlanetSize() + 1) + 2 # The +2 is to simply weight things a bit so that large planets aren't THAT much more valuable than small ones
					
					# Can it be used right away?
					if (pPlanet.getOrbitRing() < CvSolarSystem.g_iPlanetRange3):
						iPlanetValue *= 2
					
					#print("Orbit Ring %d iPlanetValue: %d" %(pPlanet.getOrbitRing(), iPlanetValue))
					
					iFoundValue += iPlanetValue
			
		else:
			iFoundValue = 0
		
		return iFoundValue
		
	def canPickPlot(self, argsList):
		pPlot = argsList[0]
		return true

	def getUnitCostMod(self, argsList):
		iPlayer, iUnit = argsList
		iCostMod = -1 # Any value > 0 will be used
		
		FinalFrontier = CvEventInterface.getEventManager()
		iCostMod = FinalFrontier.getUnitCostMod(iPlayer, iUnit)
		
		return iCostMod

	def getBuildingCostMod(self, argsList):
		iPlayer, iCityID, iBuilding = argsList
		iCostMod = -1 # Any value > 0 will be used
		
		FinalFrontier = CvEventInterface.getEventManager()
		iCostMod = FinalFrontier.getBuildingCostMod(iPlayer, iCityID, iBuilding)
		
		return iCostMod
		
	def canUpgradeAnywhere(self, argsList):
		iOwner, iUnitID = argsList
		pUnit = gc.getPlayer(iOwner).getUnit(iUnitID)
		
		bCanUpgradeAnywhere = 0
		
		iUnitStarbaseI = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_STARBASE_I')
		iUnitStarbaseII = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_STARBASE_II')
		if (pUnit.getUnitType() == iUnitStarbaseI or pUnit.getUnitType() == iUnitStarbaseII):
			bCanUpgradeAnywhere = 1
		
		return bCanUpgradeAnywhere
		
	def getWidgetHelp(self, argsList):
		eWidgetType, iData1, iData2, bOption = argsList
		
#		print("eWidgetType")
#		print(eWidgetType)
#		print("iData1")
#		print(iData1)
#		print("iData2")
#		print(iData2)
#		print("bOption")
#		print(bOption)
		
		szHelpText = u""
		
		# Only show tool tip help when players have the tutorial on
		if (not CyUserProfile().getPlayerOption(PlayerOptionTypes.PLAYEROPTION_MODDER_1)):
			
			# Selected Planet
			if (iData1 == 666):
				szHelpText = localText.getText("TXT_KEY_FF_INTERFACE_SELECTED_PLANET_HELP", ())
				
			# Planet Population
			elif (iData1 == 667):
				szHelpText = localText.getText("TXT_KEY_FF_INTERFACE_PLANET_POPULATION_HELP", ())
				
			# Planet Yield
			elif (iData1 == 668):
				szHelpText = localText.getText("TXT_KEY_FF_INTERFACE_PRODUCES_HELP", ())
				
			# Planet Assign Building
			elif (iData1 == 669):
				szHelpText = localText.getText("TXT_KEY_FF_INTERFACE_PLANET_BUILDINGS_HELP", ())
			
		# Planet Widgets in Lower-Right
		if (iData1 >= 671 and iData1 <= 678):
			
			pHeadSelectedCity = CyInterface().getHeadSelectedCity()
			FinalFrontier = CvEventInterface.getEventManager()
			pSystem = FinalFrontier.getSystemAt(pHeadSelectedCity.getX(), pHeadSelectedCity.getY())
			
			iPlanetRing = iData1 - 670
			pPlanet = pSystem.getPlanet(iPlanetRing)
			iFood = pPlanet.getTotalYield(pHeadSelectedCity.getOwner(), 0)
			iProduction = pPlanet.getTotalYield(pHeadSelectedCity.getOwner(), 1)
			iCommerce = pPlanet.getTotalYield(pHeadSelectedCity.getOwner(), 2)
			
			szHelpText = localText.getText("TXT_KEY_FF_INTERFACE_PLANET_SELECTION_HELP_0", (iFood, iProduction, iCommerce))
			if (not CyUserProfile().getPlayerOption(PlayerOptionTypes.PLAYEROPTION_MODDER_1)):
				szHelpText += "\n" + localText.getText("TXT_KEY_FF_INTERFACE_PLANET_SELECTION_HELP", ())
			
		return szHelpText
		
	def getUpgradePriceOverride(self, argsList):
		iPlayer, iUnitID, iUnitTypeUpgrade = argsList
		
		pPlayer = gc.getPlayer(iPlayer)
		pUnit = pPlayer.getUnit(iUnitID)
		
		iUnitStarbaseI = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_STARBASE_I')
		iUnitStarbaseII = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_STARBASE_II')
		iUnitStarbaseIII = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_STARBASE_III')
		
		# Upgrading Starbase...
		if (pUnit.getUnitType() == iUnitStarbaseI):
			# ...To Delta
			if (iUnitTypeUpgrade == iUnitStarbaseII):
				return 250
			# ...To Omega
			elif (iUnitTypeUpgrade == iUnitStarbaseIII):
				return 500
		
		# Upgrading Delta Starbase...
		elif (pUnit.getUnitType() == iUnitStarbaseII):
			# ...To Omega
			if (iUnitTypeUpgrade == iUnitStarbaseIII):
				return 250
				
		
		return -1	# Any value 0 or above will be used
		
	
	def getExperienceNeeded(self, argsList):
		# use this function to set how much experience a unit needs
		iLevel, iOwner = argsList
		
		iExperienceNeeded = 0

		# regular epic game experience		
		iExperienceNeeded = iLevel * iLevel + 1

		iModifier = gc.getPlayer(iOwner).getLevelExperienceModifier()
		if (0 != iModifier):
			iExperienceNeeded += (iExperienceNeeded * iModifier + 99) / 100
			
		return iExperienceNeeded
		