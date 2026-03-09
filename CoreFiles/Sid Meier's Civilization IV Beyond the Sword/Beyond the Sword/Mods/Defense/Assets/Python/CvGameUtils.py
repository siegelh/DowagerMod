## Sid Meier's Civilization 4
## Copyright Firaxis Games 2005
##
## Implementaion of miscellaneous game functions

import CvUtil
from CvPythonExtensions import *
import CvEventInterface

# globals
gc = CyGlobalContext()

class CvGameUtils:
	"Miscellaneous game functions"
	def __init__(self): 
		pass
	
	def isVictoryTest(self):
		if ( gc.getGame().getElapsedGameTurns() > 1000):
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
		return True
		
	def createBarbarianUnits(self):
		return True
		
	def skipResearchPopup(self,argsList):
		ePlayer = argsList[0]
		return True
		
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
		return True
		
	def showExamineCityButton(self,argsList):
		pCity = argsList[0]
		return False

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
		return False
	def canBuild(self,argsList):
		iX, iY, iBuild, iPlayer = argsList
		return -1	# Returning -1 means ignore; 0 means Build cannot be performed; 1 or greater means it can

	def cannotFoundCity(self,argsList):
		iPlayer, iPlotX, iPlotY = argsList
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
		
		if eControl == int(ControlTypes.CONTROL_SELECTCAPITAL):
			return True
		elif eControl == int(ControlTypes.CONTROL_SELECTCITY):
			return True
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
		bIgnoreCost = argsList[4]
		bIgnoreUpgrades = argsList[5]
		return False

	def cannotTrain(self,argsList):
		pCity = argsList[0]
		eUnit = argsList[1]
		bContinue = argsList[2]
		bTestVisible = argsList[3]
		bIgnoreCost = argsList[4]
		bIgnoreUpgrades = argsList[5]
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
		return True

	def cannotMaintain(self,argsList):
		pCity = argsList[0]
		eProcess = argsList[1]
		bContinue = argsList[2]
		return True

	def AI_chooseTech(self,argsList):
		ePlayer = argsList[0]
		bFree = argsList[1]
		return TechTypes.NO_TECH

	def AI_chooseProduction(self,argsList):
		pCity = argsList[0]
		return False

	def AI_unitUpdate(self,argsList):
		pUnit = argsList[0]
		
		if pUnit.getOwner() != 0:
			if pUnit.getUnitAIType() != UnitAITypes.UNITAI_ATTACK_CITY_LEMMING and pUnit.getUnitAIType() != UnitAITypes.UNITAI_UNKNOWN:
				if self.getRandomNumber( 3 ) == 0:
					pUnit.setUnitAIType( UnitAITypes.UNITAI_ATTACK_CITY_LEMMING )
			if pUnit.getUnitAIType() == UnitAITypes.UNITAI_ATTACK_CITY_LEMMING:
				iUnitX = pUnit.plot( ).getX( )
				iUnitY = pUnit.plot( ).getY( )
				if self.doEnemyCheck( iUnitX, iUnitY ):
					if self.getRandomNumber( 2 ) == 0:
						if self.getRandomNumber( 2 ) == 0:
							pUnit.setUnitAIType( UnitAITypes.UNITAI_ATTACK )
						else:
							pUnit.setUnitAIType( UnitAITypes.UNITAI_ATTACK_CITY )
			 
		return False

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
		
		iPopulationScore = CvUtil.getScoreComponent(gc.getPlayer(ePlayer).getPopScore(), gc.getGame().getInitPopulation(), gc.getGame().getMaxPopulation(), gc.getDefineINT("SCORE_POPULATION_FACTOR"), True, bFinal, bVictory)
		iLandScore = CvUtil.getScoreComponent(gc.getPlayer(ePlayer).getLandScore(), gc.getGame().getInitLand(), gc.getGame().getMaxLand(), gc.getDefineINT("SCORE_LAND_FACTOR"), True, bFinal, bVictory)
		iTechScore = CvUtil.getScoreComponent(gc.getPlayer(ePlayer).getTechScore(), gc.getGame().getInitTech(), gc.getGame().getMaxTech(), gc.getDefineINT("SCORE_TECH_FACTOR"), True, bFinal, bVictory)
		iWondersScore = CvUtil.getScoreComponent(gc.getPlayer(ePlayer).getWondersScore(), gc.getGame().getInitWonders(), gc.getGame().getMaxWonders(), gc.getDefineINT("SCORE_WONDER_FACTOR"), False, bFinal, bVictory)
		return int(iPopulationScore + iLandScore + iWondersScore + iTechScore)

	def doHolyCity(self):
		return True

	def doHolyCityTech(self,argsList):
		eTeam = argsList[0]
		ePlayer = argsList[1]
		eTech = argsList[2]
		bFirst = argsList[3]
		return False

	def doGold(self,argsList):
		ePlayer = argsList[0]
		return True

	def doResearch(self,argsList):
		ePlayer = argsList[0]
		return True

	def doGoody(self,argsList):
		ePlayer = argsList[0]
		pPlot = argsList[1]
		pUnit = argsList[2]
		return False

	def doGrowth(self,argsList):
		pCity = argsList[0]
		return True

	def doProduction(self,argsList):
		pCity = argsList[0]
		return True

	def doCulture(self,argsList):
		pCity = argsList[0]
		return True

	def doPlotCulture(self,argsList):
		pCity = argsList[0]
		bUpdate = argsList[1]
		ePlayer = argsList[2]
		return False

	def doReligion(self,argsList):
		pCity = argsList[0]
		return True

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
		return True
		
	def canFoundCitiesOnWater(self,argsList):
		iX, iY= argsList
		return False
		
	def doCombat(self,argsList):
		pSelectionGroup, pDestPlot = argsList
		iNumUnits = pSelectionGroup.getNumUnits()

		####Special Units####		
		for i in range( iNumUnits ):
			pUnit = pSelectionGroup.getUnitAt(i)
		####Samurai Units####
			if pUnit.getUnitType() == CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(), "UNIT_SAMURAI"):
				pPlot = pUnit.plot()
				self.doAEDamage( pDestPlot.getX( ), pDestPlot.getY( ) )
		return False

	def getConscriptUnitType(self, argsList):
		iPlayer = argsList[0]
		iConscriptUnitType = -1 #return this with the value of the UNIT TYPE you want to be conscripted, -1 uses default system
		
		return iConscriptUnitType

	def getCityFoundValue(self, argsList):
		iPlayer, iPlotX, iPlotY = argsList
		iFoundValue = -1 # Any value besides -1 will be used
		
		return iFoundValue
		
	def canPickPlot(self, argsList):
		pPlot = argsList[0]
		return true
		
	def getUnitCostMod(self, argsList):
		iPlayer, iUnit = argsList
		iCostMod = -1 # Any value > 0 will be used
		
		return iCostMod
	def getBuildingCostMod(self, argsList):
		iPlayer, iCityID, iBuilding = argsList
		pPlayer = gc.getPlayer(iPlayer)
		pCity = pPlayer.getCity(iCityID)
		
		iCostMod = -1 # Any value > 0 will be used
		
		return iCostMod
		
	def canUpgradeAnywhere(self, argsList):
		pUnit = argsList
		
		bCanUpgradeAnywhere = 0
		
		return bCanUpgradeAnywhere

	def getWidgetHelp(self, argsList):
		eWidgetType, iData1, iData2, bOption = argsList
		
		return u""
		
	def getUpgradePriceOverride(self, argsList):
		iPlayer, iUnitID, iUnitTypeUpgrade = argsList
		
		return -1	# Any value 0 or above will be used
				
	#######Defense#######

	def doAEDamage( self, iX, iY ):
		self.doPlotPlayerDamage( 50, iX-1, iY )
		self.doPlotPlayerDamage( 50, iX-1, iY-1 )		
		self.doPlotPlayerDamage( 50, iX, iY-1 )
		self.doPlotPlayerDamage( 50, iX+1, iY-1 )
		self.doPlotPlayerDamage( 50, iX+1, iY )
		self.doPlotPlayerDamage( 50, iX+1, iY+1 )
		self.doPlotPlayerDamage( 50, iX, iY+1 )
		self.doPlotPlayerDamage( 50, iX-1, iY+1 )

	def doPlotPlayerDamage( self, iValue, iX, iY ):
		if gc.getMap( ).plot( iX , iY ).isUnit( ):
			numUnits = gc.getMap( ).plot( iX , iY ).getNumUnits( )
			for i in range( numUnits ):
				if gc.getMap( ).plot( iX , iY ).getUnit( i ).getOwner( ) == 0:
					 gc.getMap( ).plot( iX , iY ).getUnit( i ).changeDamage( iValue, PlayerTypes.NO_PLAYER )
					 gc.getMap( ).plot( iX , iY ).getUnit( i ).NotifyEntity( MissionTypes.MISSION_GREAT_WORK )
	
	def getExperienceNeeded(self, argsList):
		# use this function to set how much experience a unit needs
		iLevel, iOwner = argsList
		
		iExperienceNeeded = 0

		# regular epic game experience		
		iExperienceNeeded = iLevel * iLevel + 1

		iModifier = gc.getPlayer(iOwner).getLevelExperienceModifier()
		if (0 != iModifier):
			iExperienceNeeded += (iExperienceNeeded * iModifier + 99) / 100   # ROUND UP
			
		return iExperienceNeeded

	def getRandomNumber(self, int):
		return CyGame().getSorenRandNum(int, "Defense")
		
	def doEnemyCheck( self, iX, iY ):
		for i in range(2):
			iIncrease = i+1
		if gc.getMap().plot( iX + iIncrease, iY + iIncrease ).isUnit( ):
			if gc.getMap().plot( iX + iIncrease, iY + iIncrease ).getUnit( 0 ).getOwner( ) == 0:
				return 1
		if gc.getMap().plot( iX, iY + iIncrease ).isUnit( ):
			if gc.getMap().plot( iX, iY + iIncrease ).getUnit( 0 ).getOwner( ) == 0:
				return 1
		if gc.getMap().plot( iX - iIncrease, iY + iIncrease ).isUnit( ):
			if gc.getMap().plot( iX - iIncrease, iY + iIncrease ).getUnit( 0 ).getOwner( ) == 0:
				return 1
		if gc.getMap().plot( iX - iIncrease, iY ).isUnit( ):
			if gc.getMap().plot( iX - iIncrease, iY ).getUnit( 0 ).getOwner( ) == 0:
				return 1
		if gc.getMap().plot( iX - iIncrease, iY - iIncrease ).isUnit( ):
			if gc.getMap().plot( iX - iIncrease, iY - iIncrease ).getUnit( 0 ).getOwner( ) == 0:
				return 1
		if gc.getMap().plot( iX , iY - iIncrease ).isUnit( ):
			if gc.getMap().plot( iX , iY - iIncrease ).getUnit( 0 ).getOwner( ) == 0:
				return 1
		if gc.getMap().plot( iX + iIncrease, iY - iIncrease ).isUnit( ):
			if gc.getMap().plot( iX + iIncrease, iY - iIncrease ).getUnit( 0 ).getOwner( ) == 0:
				return 1
		if gc.getMap().plot( iX + iIncrease, iY ).isUnit( ):
			if gc.getMap().plot( iX + iIncrease, iY ).getUnit( 0 ).getOwner( ) == 0:
				return 1
		return 0		
