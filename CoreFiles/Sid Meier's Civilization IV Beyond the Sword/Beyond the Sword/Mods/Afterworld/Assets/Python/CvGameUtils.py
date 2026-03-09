## Sid Meier's Civilization 4
## Copyright Firaxis Games 2005
##
## Implementaion of miscellaneous game functions

import CvUtil
from CvPythonExtensions import *
import CvEventInterface
import AW

Afterworld = AW.g_Afterworld

# globals
gc = CyGlobalContext()
pHeadSelectedUnit = CyInterface().getHeadSelectedUnit()
g_pSelectedUnit = pHeadSelectedUnit

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
		
		pUnit = gc.getPlayer(ePlayer).getUnit(iUnitId)
		pPlot = CyMap().plot(iPlotX, iPlotY)
		
		bNoMove = 0
		
		bNoMove = Afterworld.canUnitNotMoveIntoPlot(pUnit, pPlot)
		
		return bNoMove
		
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
		return False

	def AI_unitUpdate(self,argsList):
		pUnit = argsList[0]
		#do whatcha wanna do and return true
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

	def getCityFoundValue(self, argsList):
		iPlayer, iPlotX, iPlotY = argsList
		iFoundValue = -1 # Any value besides -1 will be used  
		
		return iFoundValue
		
	def doCombat(self,argsList):
		pSelectionGroup, pDestPlot = argsList
		iEntity1 = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_ENTITY')
		iEntity2 = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_ENTITY2')
		iEntity3 = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_ENTITY3')
		pAttackingUnit = pSelectionGroup.getHeadUnit()
		iAttackingPlayer = pAttackingUnit.getOwner()
		pDestUnit = pDestPlot.getUnit(0)
		pDefendingOwner = pDestUnit.getOwner()
		pSelectionPlot = pSelectionGroup.plot()
		iDefendingTeam = gc.getPlayer(pDefendingOwner).getTeam()
		
		if pDestUnit.getUnitType() == iEntity1:
			Afterworld.pAngryEntity = 1
			
		
			
			
					
	#setRevealed(int /*TeamTypes*/ eTeam, bool bNewValue, bool bTerrainOnly, int /*TeamTypes*/ eFromTeam)
		# Is there an enemy defender visible to player iAttacker?
		if (pDestPlot.isVisibleEnemyDefender(pAttackingUnit)):
			for iPlayerLoop in range(gc.getMAX_PLAYERS()):
				
				if (pDestPlot.getNumDefenders(iPlayerLoop) > 0):
					
					pDefendingUnit = pDestPlot.getBestDefender(iPlayerLoop, iAttackingPlayer, pAttackingUnit, false, false, false)
					
					if (pDefendingUnit):
						
#						print(gc.getUnitInfo(pDefendingUnit.getUnitType()).getDescription())
						
						iAttackerStrength = pAttackingUnit.currCombatStr(pDestPlot, pDefendingUnit)
						iDefenderStrength = pDefendingUnit.currCombatStr(pDestPlot, pAttackingUnit)
						
						if pAttackingUnit.getUnitType() == iEntity1:
							iAttackerStrength = 20
							
#						print("iAttackerStrength")
#						print(iAttackerStrength)
#						print("iDefenderStrength")
#						print(iDefenderStrength)
						
						iAttackerDamage = 100 * (iDefenderStrength / 5) / pAttackingUnit.maxCombatStr(pDestPlot, pDefendingUnit)
						iDefenderDamage = 100 * (iAttackerStrength / 5) / pDefendingUnit.maxCombatStr(pDestPlot, pAttackingUnit)
						
#						if (iAttackerStrength > iDefenderStrength):
#							pDefendingUnit.kill(false, iAttackingPlayer)
#						else:
#							pAttackingUnit.kill(false, iDefendingPlayer)
						
						print("%s did %d damage to %s and received %d damage" %(str(pAttackingUnit.getName()), iDefenderDamage, str(pDefendingUnit.getName()), iAttackerDamage))
						
						iControlledBleeder = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_CONTROLLED_BLEEDER')
						iBleeder = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_BLEEDER')
						iRabidBleeder = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_RABID_BLEEDER')
						iSavageBleeder = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_SAVAGE_BLEEDER')
						iSentinel1 = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_SENTINEL1')
						iSentinel2 = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_SENTINEL2')
						iSentinel3 = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_SENTINEL3')
						iFeral = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_FERAL')
						iFeral2 = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_FERAL2')
						iFeral3 = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_FERAL3')
						iEntity1 = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_ENTITY')
						iEntity2 = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_ENTITY2')
						iEntity3 = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_ENTITY3')
						iEntity4 = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_ENTITY4')
						iEntity5 = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_ENTITY5')
						iEntity6 = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_ENTITY5')
						iEntity7 = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_ENTITY5')
						iEntity8 = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_ENTITY5')
						iBOPEN = CvUtil.findInfoTypeNum(gc.getFeatureInfo,gc.getNumFeatureInfos(),'FEATURE_AFTERWORLD_BARRICADES2')
						
						iSentinel1 = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_SENTINEL1')
						iSentinel2 = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_SENTINEL2')
						iSentinel3 = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_SENTINEL3')
						
						
###############################################################################
# ALL OF THIS FOLLOWING XP STUFF IS HACKED BECAUSE ONUNITKILLED IS CALLED TWICE IN THE EVENT MANAGER #
###############################################################################
						
						
#						pHumanUnit = -1
#						pNonhumanUnit = -1
#						bNonhumanKilled = 0
#						
						# Human unit is defending
						if (pDefendingUnit.getOwner() == 0):
							if pDefendingUnit != None:
								Afterworld.pPushedButtonUnit = pDefendingUnit
#								pHumanUnit = pDefendingUnit
#								pNonhumanUnit = pAttackingUnit

						# Human unit is attacking
						if (pAttackingUnit.getOwner() == 0):
							if pAttackingUnit != None:
								pHumanUnit = pAttackingUnit
								pNonhumanUnit = pDefendingUnit
								
								if (pNonhumanUnit.getDamage() + iDefenderDamage >= 100):
									
									print("   *** REMOVING XP to Defending Human unit %d owner %d (Attacker was %d)" %(pHumanUnit.getID(), pHumanUnit.getOwner(), pNonhumanUnit.getID()))
									
									if (pNonhumanUnit.getUnitType() == iRabidBleeder or pNonhumanUnit.getUnitType() == iSavageBleeder):
										pHumanUnit.changeExperience(-2,pHumanUnit.experienceNeeded()+50,0,0,0)
									elif (pNonhumanUnit.getUnitType() == iBleeder):
										pHumanUnit.changeExperience(-1,pHumanUnit.experienceNeeded()+50,0,0,0)
										#If the units kill a bleeder, they may make a comment
										
									elif(pNonhumanUnit.getUnitType() == iSentinel3):
										pHumanUnit.changeExperience(-2,pHumanUnit.experienceNeeded()+50,0,0,0)
									elif (pNonhumanUnit.getUnitType() == iSentinel1 or pNonhumanUnit.getUnitType() == iSentinel2):
										pHumanUnit.changeExperience(-1,pHumanUnit.experienceNeeded()+50,0,0,0)
										
									elif (pNonhumanUnit.getUnitType() == iFeral or pNonhumanUnit.getUnitType() == iFeral2 or pNonhumanUnit.getUnitType() == iFeral3):
										pHumanUnit.changeExperience(-4,pHumanUnit.experienceNeeded()+50,0,0,0)
						
						
##############################################################################
# ALL OF THE PREVIOUS XP STUFF IS HACKED BECAUSE ONUNITKILLED IS CALLED TWICE IN THE EVENT MANAGER #
##############################################################################
						
								
						pAttackingUnit.attackForDamage(pDefendingUnit, iAttackerDamage, iDefenderDamage)
						#pAttackingUnit.changeDamage(iAttackerDamage, iPlayerLoop)
						#pDefendingUnit.changeDamage(iDefenderDamage, iAttackingPlayer)
						
						#pAttackingUnit.changeMoves(gc.getMOVE_DENOMINATOR())
						
						return True

	def getConscriptUnitType(self, argsList):
		iPlayer = argsList[0]
		iConscriptUnitType = -1 #return this with the value of the UNIT TYPE you want to be conscripted
		
		return iConscriptUnitType

	def canPickPlot(self, argsList):
		pPlot = argsList[0]
		#pIntWalls = CvUtil.findInfoTypeNum(gc.getFeatureInfo,gc.getNumFeatureInfos(),'FEATURE_AFTERWORLD_INTERIOR_WALLS')		
		#if 
		#		return false				
		return true
		
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
				
		iType = WidgetTypes.WIDGET_GENERAL
		pHeadSelectedUnit = CyInterface().getHeadSelectedUnit()
		
		if (eWidgetType == iType):
			if (iData1 == 660):
				return CyTranslator().getText("TXT_KEY_REALBTNCONTROL",())

			elif (iData1 == 661):
				return CyTranslator().getText("TXT_KEY_REALBTNPROJECT",())

			elif (iData1 == 662):
				return CyTranslator().getText("TXT_KEY_REALBTNCI",())	

			elif (iData1 == 663):
				return CyTranslator().getText("TXT_KEY_REALBTNBARRIER",())

			elif (iData1 == 664):
				return CyTranslator().getText("TXT_KEY_REALBTNENHAC",())

			elif (iData1 == 665):
				return CyTranslator().getText("TXT_KEY_REALBTNSHADOW",())

			elif (iData1 == 666):
				return CyTranslator().getText("TXT_KEY_BTNMDA",())

			elif (iData1 == 444):
				return CyTranslator().getText("TXT_KEY_TURNLEFTBTN",())

			elif (iData1 == 669):
				return CyTranslator().getText("TXT_KEY_BTNSILENCE",())

			elif (iData1 == 670):
				if pHeadSelectedUnit.isHasPromotion(gc.getInfoTypeForString('PROMOTION_MAULER3')):
					print "Maul 3"
					return CyTranslator().getText("TXT_KEY_REALBTNMAUL3",())
				elif pHeadSelectedUnit.isHasPromotion(gc.getInfoTypeForString('PROMOTION_MAULER2')):
					print "Maul 2"
					return CyTranslator().getText("TXT_KEY_REALBTNMAUL2",())
				elif pHeadSelectedUnit.isHasPromotion(gc.getInfoTypeForString('PROMOTION_MAULER1')):
					print "Maul 1"
					return CyTranslator().getText("TXT_KEY_REALBTNMAUL",())

			elif (iData1 == 445):
				return CyTranslator().getText("TXT_KEY_TURNRIGHTBTN",())

			elif (iData1 == 672):
				return CyTranslator().getText("TXT_KEY_REALBTNFD1",())

			elif (iData1 == 673):
				return CyTranslator().getText("TXT_KEY_REALBTNSENT1",())
				
			elif (iData1 == 684):
				return CyTranslator().getText("TXT_KEY_REALBTNSENT2",())
				
			elif (iData1 == 685):
				return CyTranslator().getText("TXT_KEY_REALBTNSENT3",())

			elif (iData1 == 680):
				return CyTranslator().getText("TXT_KEY_REALBTNREPAIR",())
				
			elif (iData1 == 681):
				return CyTranslator().getText("TXT_KEY_REPAIRMECH",())
				
			elif (iData1 == 682):
				return CyTranslator().getText("TXT_KEY_ACCMECH",())
				
			elif (iData1 == 683):
				return CyTranslator().getText("TXT_KEY_FDTHREE",())
				
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
		
