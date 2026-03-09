## Sid Meier's Civilization 4
## Copyright Firaxis Games 2005
##
## Implementaion of miscellaneous game functions

import PyHelpers
import CvUtil
from CvPythonExtensions import *
import CvEventInterface
import Popup as PyPopup
import BrokenStar

# globals
gc = CyGlobalContext()
localText = CyTranslator()
PyPlayer = PyHelpers.PyPlayer

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
	
	#EDITED
	def canDeclareWar(self,argsList): #This code prevents non M.D. players from delcaring war on M.D. players. 
		iAttackingTeam, iDefendingTeam = argsList #gets the variables for the attacking and defending players. 
		i = iAttackingTeam
		if i >= 8 and i < 18: #if the player attempting to declare war is a non M.D...
			return False 
		else: #if it isn't...
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
		
		print "unitCannotMoveInto"
		bHasNuke = False
		pPlot = CyMap().plot(iPlotX, iPlotY)
		for i in range(pPlot.getNumUnits()):
			iUnitType = pPlot.getUnit(i).getUnitType()
			if iUnitType == gc.getInfoTypeForString("UNIT_UNARMED_NUKE") or iUnitType == gc.getInfoTypeForString("UNIT_NUKE"):
				bHasNuke = True
		if iUnitId == gc.getInfoTypeForString("UNIT_SETTLER") and bHasNuke:
			return True
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
		if eUnit == CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_TACTICAL_NUKE'):
			return True
		elif CyGame().getActivePlayer() >= 8 and CyGame().getActivePlayer() < 18 and eUnit == CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_SETTLER'):
			return True
		else:
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
		return False

	def AI_unitUpdate(self,argsList):
		pUnit = argsList[0]
		#B_BROKENSTAR

		if pUnit.getUnitAIType() != UnitAITypes.UNITAI_UNKNOWN:
			for i in range(pUnit.plot().getNumUnits()):
				if pUnit.plot().getUnit(i).getUnitType() == gc.getInfoTypeForString("UNIT_UNARMED_NUKE"):
					pUnit.setUnitAIType(UnitAITypes.UNITAI_UNKNOWN)
					return true

		ranger = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_RANGER')
		antiAir = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_AA_INFANTRY')
		challenger2 = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_CHALLENGER2')
		if (pUnit.getUnitType() == ranger or pUnit.getUnitType() == antiAir or pUnit.getUnitType() == challenger2) and pUnit.getUnitAIType() != 0:
			return BrokenStar.BrokenStar().attackNuke(pUnit)
						
		#E_BROKENSTAR
		
		return False

	def AI_doWar(self,argsList):
		eTeam = argsList[0]
		return False

	def AI_doDiplo(self,argsList):
		ePlayer = argsList[0]
		return False

	#EDITED
	def calculateScore(self,argsList):
		ePlayer = argsList[0]
		bFinal = argsList[1]
		bVictory = argsList[2]
		
		iPopulationScore = CvUtil.getScoreComponent(gc.getPlayer(ePlayer).getPopScore(), gc.getGame().getInitPopulation(), gc.getGame().getMaxPopulation(), gc.getDefineINT("SCORE_POPULATION_FACTOR"), True, bFinal, bVictory)
		iLandScore = CvUtil.getScoreComponent(gc.getPlayer(ePlayer).getLandScore(), gc.getGame().getInitLand(), gc.getGame().getMaxLand(), gc.getDefineINT("SCORE_LAND_FACTOR"), True, bFinal, bVictory)
		#iTechScore = CvUtil.getScoreComponent(gc.getPlayer(ePlayer).getTechScore(), gc.getGame().getInitTech(), gc.getGame().getMaxTech(), gc.getDefineINT("SCORE_TECH_FACTOR"), True, bFinal, bVictory)
		#iWondersScore = CvUtil.getScoreComponent(gc.getPlayer(ePlayer).getWondersScore(), gc.getGame().getInitWonders(), gc.getGame().getMaxWonders(), gc.getDefineINT("SCORE_WONDER_FACTOR"), False, bFinal, bVictory)
		if ePlayer < 8:
			return int(iPopulationScore + iLandScore)
		else:
			return int(0)

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
		ePlayer = argsList[2]
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
			
	#ADDED
	def addPopup(self, szTitle, szText):
		
		# Don't display popups for autoplay games
		iActive = CyGame().getActivePlayer()
		if (iActive != -1 and gc.getPlayer(iActive).isAlive()):
			
			popup = PyPopup.PyPopup(-1)
			popup.setHeaderString(szTitle)
			popup.setBodyString(szText)
			popup.launch(true, PopupStates.POPUPSTATE_IMMEDIATE)
			
	def getUnitCostMod(self, argsList):
		iPlayer, iUnit = argsList
		iCostMod = -1 # Any value > 0 will be used
		
		return iCostMod
		
	def canUpgradeAnywhere(self, argsList):
		iOwner, iUnitID = argsList
		pUnit = gc.getPlayer(iOwner).getUnit(iUnitID)
		
		bCanUpgradeAnywhere = 0
		
		return bCanUpgradeAnywhere

	def getWidgetHelp(self, argsList):
		eWidgetType, iData1, iData2, bOption = argsList
		
		if (iData1 == 611):
			return localText.getText("TXT_KEY_PURCHASE_EXP_MOUSEOVER", (5, 75))
		elif (iData2 == 613):
			# use function to get cost
			iCost = BrokenStar.BrokenStar().getPurchaseUnitCost(iData1, CyGame().getActivePlayer())
			return localText.getText("TXT_KEY_BUY_SELL_WIDGET", (gc.getUnitInfo(iData1).getDescription(), (iCost)))
		elif (iData2 == 669):
			return localText.getText("TXT_KEY_BROKEN_STAR_BUY_SELL_BUTTON", ())
			
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
		
