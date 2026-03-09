## Sid Meier's Civilization 4
## Copyright Firaxis Games 2005
##
## Implementaion of miscellaneous game functions

import CvUtil
from CvPythonExtensions import *
from PyHelpers import PyPlayer

# globals
gc = CyGlobalContext()

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
		
		# City of Rome
		if (pCity.getX() == 22 and pCity.getY() == 14):
			return False
		
		return True
	
	def canDeclareWar(self,argsList):
		iAttackingTeam, iDefendingTeam = argsList
		
		# Prevent civs with Christian State Religion from declaring war on Rome
		
		iCivHolyRomeID = CvUtil.findInfoTypeNum(gc.getCivilizationInfo,gc.getNumCivilizationInfos(),'CIVILIZATION_HOLY_ROME')
		iReligionChristianityID = CvUtil.findInfoTypeNum(gc.getReligionInfo,gc.getNumReligionInfos(),'RELIGION_CHRISTIANITY')

		pAttackingTeam = gc.getTeam(iAttackingTeam)
		pAttackingPlayer = gc.getPlayer(pAttackingTeam.getLeaderID())
		iTeamHolyRomeID = gc.getPlayer(iCivHolyRomeID).getTeam()
		
		# Defending Civ is Rome
		if (iDefendingTeam == iTeamHolyRomeID):
			# If attacker is Christian, prevent it
			if (pAttackingPlayer.getStateReligion() == iReligionChristianityID):
				return False
		
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
		return False

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
		
		bOverride = false
		
		# Make AI build Supply Trains sometimes
		
		# Only build in cities of a big enough size
		if (pCity.getPopulation() >= 4):
			
			iNumSupplyTrains = 0
			iNumInquisitors = 0
			
			iUnitSupplyTrain = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_SUPPLY_TRAIN')
			iUnitInquisitor = CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_INQUISITOR')
			
			pyPlayer = PyPlayer(pCity.getOwner())
			
			apUnitList = pyPlayer.getUnitList()
			for pUnitLoop in apUnitList:
				if (pUnitLoop.getUnitType() == iUnitSupplyTrain):
					iNumSupplyTrains += 1
				elif (pUnitLoop.getUnitType() == iUnitInquisitor):
					iNumInquisitors += 1
			
			# Don't build more if this player has enough
			if (iNumSupplyTrains <= 1):
				
				# Random # roll
				iRoll = CyGame().getSorenRandNum(100, "Charlemagne: Rolling to see if AI wants to build a Supply Train")
				
				# 5% chance
				if (iRoll < 5):
					
					pCity.pushOrder(OrderTypes.ORDER_TRAIN, iUnitSupplyTrain, -1, False, False, False, True)
					bOverride = true
			
			# Don't build more if this player has enough
			if (iUnitInquisitor == 0):
				
				# Random # roll
				iRoll = CyGame().getSorenRandNum(100, "Charlemagne: Rolling to see if AI wants to build an Inquisitor")
				
				# 5% chance
				if (iRoll < 5):
					
					pCity.pushOrder(OrderTypes.ORDER_TRAIN, iUnitInquisitor, -1, False, False, False, True)
					bOverride = true
		
		return bOverride

	def AI_unitUpdate(self,argsList):
		pUnit = argsList[0]
		iOwner = pUnit.getOwner( )
		iInquisitor = CvUtil.findInfoTypeNum( gc.getUnitInfo, gc.getNumUnitInfos(), "UNIT_INQUISITOR" )
		
		if not gc.getPlayer( iOwner ).isHuman( ):
			if pUnit.getUnitType( ) == iInquisitor:
				self.doInquisitorCore_AI( pUnit )
				return True
		return False
				
	def doInquisitorCore_AI( self, pUnit ):
		iOwner = pUnit.getOwner( )
		iStateReligion = gc.getPlayer( iOwner ).getStateReligion( )
		lCities = PyPlayer( iOwner ).getCityList( )
		
		#Looks to see if the AI controls a Holy City that is not the State Religion
		for iCity in range( len( lCities ) ):
			for iReligion in range( 7 ):
				if iReligion != iStateReligion:
					pCity = gc.getPlayer( iOwner ).getCity( lCities[ iCity ].getID( ) )
					if pCity.isHolyCityByType( iReligion ):
						#Makes the unit move to the City and purge it
						if pUnit.generatePath( pCity.plot( ), 0, False, None ):
							self.doHolyCitySeekAndDestroy( pUnit, pCity )
							return
		
		for iCity in range( len( lCities ) ):
			for iReligion in range( 7 ):
				if iReligion != iStateReligion:
					pCity = gc.getPlayer( iOwner ).getCity( lCities[ iCity ].getID( ) )
					if pCity.isHasReligion( iReligion ):
						if pUnit.generatePath( pCity.plot( ), 0, False, None ):
							self.doHolyCitySeekAndDestroy( pUnit, pCity )
							return
	
	def doHolyCitySeekAndDestroy( self, pUnit, pCity ):
		pCharlemagne = CvEventInterface.getEventManager( )
		
		if pUnit.getX( ) != pCity.getX( ) or pUnit.getY( ) != pCity.getY( ):
			pUnit.getGroup().pushMission(MissionTypes.MISSION_MOVE_TO, pCity.getX( ), pCity.getY( ), 0, False, True, MissionAITypes.NO_MISSIONAI, pUnit.plot(), pUnit)
		else:
			
			iMessageID = pCharlemagne.m_iNetMessage_Inquisitor
			iPlotX = pCity.getX()
			iPlotY = pCity.getY()
			iOwner = pUnit.getOwner()
			iUnitID = pUnit.getID()
			
			# Send NetMessage to prevent OOS: will be received in the EventManager function "onModNetMessage()"
			CyMessageControl().sendModNetMessage(iMessageID, iPlotX, iPlotY, iOwner, iUnitID)
#			pCharlemagne.doInquisitorPersecution( pCity, pUnit )

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
		return True
				
	def canFoundCitiesOnWater(self,argsList):
		iX, iY= argsList
		return False
		
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
		
		return iFoundValue
		
	def canPickPlot(self, argsList):
		pPlot = argsList[0]
		return true
		
	def getUnitCostMod(self, argsList):
		iPlayer, iUnit = argsList
		iCostMod = -1 # Any value > 0 will be used
		
		return iCostMod
		
	def canUpgradeAnywhere(self, argsList):
		pUnit = argsList
		
		bCanUpgradeAnywhere = 0
		
		return bCanUpgradeAnywhere

	def getWidgetHelp(self, argsList):
		eWidgetType, iData1, iData2, bOption = argsList
		
		# Inquisitor's button
		if (iData1 == 666):
			return CyTranslator().getText("TXT_KEY_CHARLE_INQUISIT_CITY", ())
			
		return u""
		
	def getUpgradePriceOverride(self, argsList):
		iPlayer, iUnitID, iUnitTypeUpgrade = argsList
		
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
		
