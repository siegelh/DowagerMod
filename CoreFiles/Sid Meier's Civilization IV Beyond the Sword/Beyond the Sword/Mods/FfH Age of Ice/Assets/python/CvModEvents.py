
from CvPythonExtensions import *
import sys
import Popup as PyPopup
from PyHelpers import PyPlayer
import pickle
import CvEventManager
from CvScreenEnums import *
from PyHelpers import *
import CvUtil
import CvTopCivs
import CvAdvisorUtils
import PyHelpers

# globals
gc = CyGlobalContext()
localText = CyTranslator()

DefaultUnitAI = UnitAITypes.NO_UNITAI

class CvModEvents(CvEventManager.CvEventManager):

##################################################################
	
	def __init__(self):
		
		CvEventManager.CvEventManager.__init__(self)

# insert mod specific variables here

###########################################################################################
#################################### UTILITY FUNCTIONS ####################################
###########################################################################################

	def addPopup(self, szText):
		szTitle = self.szGameDate = CyGameTextMgr().getTimeStr(CyGame().getGameTurn(), false)
		popup = PyPopup.PyPopup(-1)
		popup.setHeaderString(szTitle)
		popup.setBodyString(szText)
		popup.launch(true, PopupStates.POPUPSTATE_QUEUED)

	def canBlizzard(self, pPlot):
		if pPlot.isPeak():
			return False
		if pPlot.getFeatureType() == gc.getInfoTypeForString('FEATURE_VOLCANO'):
			return False
		if pPlot.isOwned():
			if pPlot.getBonusType(-1) != -1:
				if pPlot.getImprovementType() != -1:
					if gc.getPlayer(pPlot.getOwner()).getCivilizationType() == gc.getInfoTypeForString('CIVILIZATION_ILLIANS'):
						return False
		return True

	def doBlizzard(self, pPlot):
		iBlizzardClimateChange = gc.getDefineINT('BLIZZARD_CLIMATE_CHANGE')
		szText = "AS3D_GUST"
		bValid = False
		iX = pPlot.getX()
		iY = pPlot.getY()

		for iiX in range(iX-1, iX+2, 1):
			for iiY in range(iY-1, iY+2, 1):
				targetPlot = CyMap().plot(iiX,iiY)
				if targetPlot.isNone() == False:
					self.changeClimate(targetPlot, iBlizzardClimateChange)
					for i in range(targetPlot.getNumUnits()):
						pUnit = targetPlot.getUnit(i)
						self.doBlizzardOnUnit(pUnit)
						if pUnit.isHuman():
							bValid = True
		if bValid:
			point = pPlot.getPoint()
			CyAudioGame().Play3DSound(szText,point.x,point.y,point.z)

	def doBlizzardOnUnit(self, pUnit):
		if pUnit.isHasPromotion(gc.getInfoTypeForString('PROMOTION_RESIST_COLD')) == False:
			if pUnit.getDamage() < 25:
				pUnit.setDamage(pUnit.getDamage()+5, False)
			pUnit.setMoves(pUnit.getMoves() + 30)

	def doMapTurn(self):
		iBlizzard = gc.getInfoTypeForString('IMPROVEMENT_BLIZZARD')
		iBlizzardChance = gc.getDefineINT('BLIZZARD_CHANCE')
		iBlizzardDriftChance = gc.getDefineINT('BLIZZARD_DRIFT_CHANCE')
		iBlizzardKillChance = gc.getDefineINT('BLIZZARD_KILL_CHANCE')
		iFrostGiant = gc.getInfoTypeForString('UNIT_FROST_GIANT')
		iFrostGiantCastle = gc.getInfoTypeForString('FEATURE_FROST_GIANT_CASTLE')
		iFrostling = gc.getInfoTypeForString('UNIT_FROSTLING')
		iFrostlingArcher = gc.getInfoTypeForString('UNIT_FROSTLING_ARCHER')
		iFrostlingHunter = gc.getInfoTypeForString('UNIT_FROSTLING_HUNTER')
		iHut = gc.getInfoTypeForString('FEATURE_HUT')
		iLairSpawnChance = (gc.getHandicapInfo(CyGame().getHandicapType()).getBarbarianCityCreationProb()) * 2
		iLairSpawnUpgradeChance = gc.getHandicapInfo(CyGame().getHandicapType()).getBarbarianCityCreationProb()
		iWolfRider = gc.getInfoTypeForString('UNIT_WOLF_RIDER')
		bPlayer = gc.getPlayer(gc.getBARBARIAN_PLAYER())
	
		for iX in range(CyMap().getGridWidth() - 1, -1, -1):
			for iY in range(CyMap().getGridHeight()):
				pPlot = CyMap().plot(iX,iY)
				if pPlot.getFeatureType() == iHut:
					if CyGame().getSorenRandNum(150, "Hut") <= iLairSpawnChance:
						iUnit = iFrostling
						if CyGame().getSorenRandNum(100, "Hut") <= iLairSpawnUpgradeChance:
							iUnit = iFrostlingArcher
						if CyGame().getSorenRandNum(100, "Hut") <= iLairSpawnUpgradeChance:
							iUnit = iFrostlingHunter
						if CyGame().getSorenRandNum(100, "Hut") <= iLairSpawnUpgradeChance:
							iUnit = iWolfRider
						newUnit = bPlayer.initUnit(iUnit, iX, iY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_NORTH)
				if pPlot.getFeatureType() == iFrostGiantCastle:
					if CyGame().getSorenRandNum(100, "Frost Giant Castle") <= (iLairSpawnChance / 2):
						newUnit = bPlayer.initUnit(iFrostGiant, iX, iY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_NORTH)
				if pPlot.getImprovementType() == iBlizzard:
					iRnd = CyGame().getSorenRandNum(100, "Blizzard")
					if iRnd <= iBlizzardDriftChance:
						newPlot = CyMap().plot(pPlot.getX() + 1, pPlot.getY() + 1)
					if (iRnd > iBlizzardDriftChance and iRnd < (100 - iBlizzardDriftChance)):
						newPlot = CyMap().plot(pPlot.getX() + 1, pPlot.getY())
					if iRnd >= 100 - iBlizzardDriftChance:
						newPlot = CyMap().plot(pPlot.getX() + 1, pPlot.getY() - 1)
					if self.canBlizzard(newPlot) and newPlot.isNone() == False:
						if newPlot.isOwned():
							if (gc.getPlayer(newPlot.getOwner()).isHuman() and newPlot.getImprovementType() != -1 and newPlot.getImprovementType() != iBlizzard):
								CyInterface().addMessage(newPlot.getOwner(),True,25,CyTranslator().getText("TXT_KEY_POPUP_DESTROY_IMPROVEMENT",()),'AS2D_CITYRAZE',1,'Art/Interface/Buttons/Actions/Pillage.dds',ColorTypes(7),newPlot.getX(),newPlot.getY(),True,True)
						newPlot.setImprovementType(iBlizzard)
						self.doBlizzard(newPlot)
						pPlot.setImprovementType(-1)
				else:
					self.changeClimate(pPlot, -1)
				if pPlot.getImprovementType() == iBlizzard:
					self.doBlizzard(pPlot)
					if CyGame().getSorenRandNum(100, "Blizzard") < 25:
						pPlot.setImprovementType(-1)
				if pPlot.getX() == 0:
					if CyGame().getSorenRandNum(100, "Blizzard") <= iBlizzardChance:
						pPlot.setImprovementType(iBlizzard)
						self.doBlizzard(pPlot)

	def findClearPlot(self, pUnit):
		BestPlot = -1
		iBestPlot = 0
		pOldPlot = pUnit.plot()
		iX = pOldPlot.getX()
		iY = pOldPlot.getY()
		for iiX in range(iX-1, iX+2, 1):
			for iiY in range(iY-1, iY+2, 1):
				iCurrentPlot = 0
				pPlot = CyMap().plot(iiX,iiY)
				if pPlot.getNumUnits() == 0:
					iCurrentPlot = iCurrentPlot + 5
				if iCurrentPlot >= 1:
					iCurrentPlot = iCurrentPlot + CyGame().getSorenRandNum(5, "findClearPlot")
					if iCurrentPlot >= iBestPlot:
						BestPlot = pPlot
						iBestPlot = iCurrentPlot
		return BestPlot

	def changeClimate(self, pPlot, i):
		iClimate = self.getClimate(pPlot)
		iClimate = iClimate + i
		if iClimate > 200:
			iClimate = 200
		if iClimate < 0:
			iClimate = 0
		self.setClimate(pPlot, iClimate)

	def getClimate(self, pPlot):
		szScriptData = pickle.loads(pPlot.getScriptData())
		iClimate = int(szScriptData)
		return iClimate

	def setClimate(self, pPlot, iClimate):
		iCoast = gc.getInfoTypeForString('TERRAIN_COAST')
		iCoastFrozen = gc.getInfoTypeForString('TERRAIN_COAST_FROZEN')
		iForest = gc.getInfoTypeForString('FEATURE_FOREST')
		iGrass = gc.getInfoTypeForString('TERRAIN_GRASS')
		iIce = gc.getInfoTypeForString('FEATURE_ICE')
		iJungle = gc.getInfoTypeForString('FEATURE_JUNGLE')
		iPlains = gc.getInfoTypeForString('TERRAIN_PLAINS')
		iSnow = gc.getInfoTypeForString('TERRAIN_SNOW')
		iTundra = gc.getInfoTypeForString('TERRAIN_TUNDRA')

		iFeature = pPlot.getFeatureType()
		iTerrain = pPlot.getTerrainType()

		if (iTerrain != iCoast and iTerrain != iCoastFrozen):
			if (iClimate <= 50 and iTerrain != iPlains and pPlot.isFreshWater() == False and iFeature != iJungle):
				pPlot.setTerrainType(iPlains,True,True)
				if iFeature == iForest:
					pPlot.setFeatureType(iForest,1)
			if (iClimate <= 100 and iClimate > 50 and iTerrain != iGrass):
				pPlot.setTerrainType(iGrass,True,True)
				if iFeature == iForest:
					pPlot.setFeatureType(iForest,1)
			if (iClimate <= 150 and iClimate > 100 and iTerrain != iTundra):
				pPlot.setTerrainType(iTundra,True,True)
				if iFeature == iForest:
					pPlot.setFeatureType(iForest,2)
			if (iClimate > 150 and iTerrain != iSnow):
				pPlot.setTerrainType(iSnow,True,True)
				if iFeature == iForest:
					pPlot.setFeatureType(iForest,2)
		else:
			if (iClimate > 100 and iFeature == -1):
				pPlot.setFeatureType(iIce, -1)
				pPlot.setTerrainType(iCoastFrozen,True,True)
			else:
				if (iClimate < 100 and iFeature == iIce):
					pPlot.setRouteType(-1)
					pPlot.setFeatureType(-1, -1)
					pPlot.setTerrainType(iCoast,True,True)
					for i in range(pPlot.getNumUnits(), -1, -1):
						pUnit = pPlot.getUnit(i)
						pUnit.jumpToNearestValidPlot()
		szScriptData = str(iClimate)
		pPlot.setScriptData(pickle.dumps(szScriptData))
		
	def addUnit(self, iUnit):
		pBestPlot = -1
		iBestPlot = -1
		iBlizzard = gc.getInfoTypeForString('IMPROVEMENT_BLIZZARD')
		iSnow = gc.getInfoTypeForString('TERRAIN_SNOW')
		iTundra = gc.getInfoTypeForString('TERRAIN_TUNDRA')
		for i in range (CyMap().numPlots()):
			pPlot = CyMap().plotByIndex(i)
			iPlot = -1
			if pPlot.getNumUnits() == 0:
				if pPlot.isCity() == False:
					if pPlot.isImpassable() == False:
						if pPlot.isWater() == False:
							iPlot = CyGame().getSorenRandNum(500, "Add Unit")
							if pPlot.getTerrainType() == iSnow:
								iPlot = iPlot + 500
							if pPlot.getImprovementType() == iBlizzard:
								iPlot = iPlot + 500
							if pPlot.getTerrainType() == iTundra:
								iPlot = iPlot + 200
							if pPlot.isOwned() == False:
								iPlot = iPlot + 200
			if iPlot > iBestPlot:
				iBestPlot = iPlot
				pBestPlot = pPlot
		if iBestPlot != -1:
			bPlayer = gc.getPlayer(gc.getBARBARIAN_PLAYER())
			newUnit = bPlayer.initUnit(iUnit, pBestPlot.getX(), pBestPlot.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_NORTH)


###########################################################################################
#################################### UPDATED FUNCTIONS ####################################
###########################################################################################

	def onGameStart(self, argsList):
		'Called at the start of the game'
		if (gc.getGame().getStartEra() == gc.getDefineINT("STANDARD_ERA")):
			for iPlayer in range(gc.getMAX_PLAYERS()):
				player = gc.getPlayer(iPlayer)
				if (player.isAlive() and player.isHuman()):
					popupInfo = CyPopupInfo()
					popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON_SCREEN)
					popupInfo.setText(u"showDawnOfMan")
					popupInfo.addPopup(iPlayer)

					popupInfo = CyPopupInfo()
					popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON_SCREEN)
					popupInfo.setData1(1)
					popupInfo.setData2(11)
					popupInfo.setData3(3)
					popupInfo.setText(u"showWonderMovie")
					popupInfo.addPopup(iPlayer)

		else:
			CyInterface().setSoundSelectionReady(true)

		if gc.getGame().isPbem():
			for iPlayer in range(gc.getMAX_PLAYERS()):
				player = gc.getPlayer(iPlayer)
				if (player.isAlive() and player.isHuman()):
					popupInfo = CyPopupInfo()
					popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_DETAILS)
					popupInfo.setOption1(true)
					popupInfo.addPopup(iPlayer)					

	def onBeginGameTurn(self, argsList):
		'Called at the beginning of the end of each turn'
		iGameTurn = argsList[0]
		pPlayer = gc.getPlayer(0)
		illianPlayer = gc.getPlayer(1)
		bPlayer = gc.getPlayer(gc.getBARBARIAN_PLAYER())
		iCoast = gc.getInfoTypeForString('TERRAIN_COAST')
		iCoastFrozen = gc.getInfoTypeForString('TERRAIN_COAST_FROZEN')
		iGrass = gc.getInfoTypeForString('TERRAIN_GRASS')
		iIce = gc.getInfoTypeForString('FEATURE_ICE')
		iPlains = gc.getInfoTypeForString('TERRAIN_PLAINS')
		iSnow = gc.getInfoTypeForString('TERRAIN_SNOW')
		iTundra = gc.getInfoTypeForString('TERRAIN_TUNDRA')

		if iGameTurn == 2:
			for i in range (CyMap().numPlots()):
				pPlot = CyMap().plotByIndex(i)
				iClimate = 95
				if pPlot.getTerrainType() == iPlains:
					iClimate = 15
				if pPlot.getTerrainType() == iGrass:
					iClimate = 65
				if pPlot.getTerrainType() == iTundra:
					iClimate = 115
				if pPlot.getTerrainType() == iSnow:
					iClimate = 165
				if pPlot.getTerrainType() == iCoast:
					iClimate = 50
				if pPlot.getTerrainType() == iCoastFrozen:
					iClimate = 150
				iClimate = iClimate + CyGame().getSorenRandNum(20, "onGameStart")
				aScriptData = str(iClimate)
				pPlot.setScriptData(pickle.dumps(aScriptData))

			for iPlayer in range(gc.getMAX_PLAYERS()):
				player = gc.getPlayer(iPlayer)
				if player.isAlive():
					if (player.getCivilizationType() != gc.getInfoTypeForString('CIVILIZATION_AMURITES') and iPlayer != gc.getBARBARIAN_PLAYER()):
						eTeam = gc.getTeam(player.getTeam())
						iTeam = gc.getPlayer(gc.getBARBARIAN_PLAYER()).getTeam()
						eTeam.makePeace(iTeam)
						eTeam = gc.getTeam(player.getTeam())
						iTeam = gc.getPlayer(0).getTeam()
						eTeam.declareWar(iTeam, true, WarPlanTypes.WARPLAN_LIMITED)

		if iGameTurn == 3:
			for iPlayer1 in range(gc.getMAX_PLAYERS()):
				pPlayer1 = gc.getPlayer(iPlayer1)
				if pPlayer1.isAlive():
					for iPlayer2 in range(gc.getMAX_PLAYERS()):
						pPlayer2 = gc.getPlayer(iPlayer2)
						if (pPlayer2.isAlive() and iPlayer1 != iPlayer2):
							eTeam = gc.getTeam(pPlayer1.getTeam())
							iTeam = pPlayer2.getTeam()
							eTeam.setPermanentWarPeace(iTeam, True)

		if iGameTurn > 5:
			self.doMapTurn()

		if iGameTurn == 20:
			self.addPopup(CyTranslator().getText("TXT_KEY_POPUP_BLIZZARD",()))

		iCount = 0
		if pPlayer.getUnitClassCount(gc.getInfoTypeForString('UNITCLASS_GODSLAYER_BLADE')) > 0:
			iCount = iCount + 1
		if pPlayer.getUnitClassCount(gc.getInfoTypeForString('UNITCLASS_GODSLAYER_CROSSGUARD')) > 0:
			iCount = iCount + 1
		if pPlayer.getUnitClassCount(gc.getInfoTypeForString('UNITCLASS_GODSLAYER_HILT')) > 0:
			iCount = iCount + 1
		if pPlayer.getUnitClassCount(gc.getInfoTypeForString('UNITCLASS_KYLORIN')) > 0:
			iCount = 4
		if iCount > 3:
			if CyGame().getUnitClassCreatedCount(gc.getInfoTypeForString('UNITCLASS_DRIFA')) == 0:
				self.addUnit(gc.getInfoTypeForString('UNIT_DRIFA'))
				self.addPopup(CyTranslator().getText("TXT_KEY_POPUP_DRIFA_CREATED",()))
		bSpawn = false
		if illianPlayer.isAlive():
			illianTeam = gc.getTeam(illianPlayer.getTeam())
			if iCount > 0:
				if illianTeam.isHasTech(gc.getInfoTypeForString('TECH_WINTER_TECH_I')) == false:
					illianTeam.setHasTech(gc.getInfoTypeForString('TECH_WINTER_TECH_I'), True, 1, True, True)
					bSpawn = true
			if iCount > 1:
				if illianTeam.isHasTech(gc.getInfoTypeForString('TECH_WINTER_TECH_II')) == false:
					illianTeam.setHasTech(gc.getInfoTypeForString('TECH_WINTER_TECH_II'), True, 1, True, True)
					bSpawn = true
			if iCount > 2:
				if illianTeam.isHasTech(gc.getInfoTypeForString('TECH_WINTER_TECH_III')) == false:
					illianTeam.setHasTech(gc.getInfoTypeForString('TECH_WINTER_TECH_III'), True, 1, True, True)
					bSpawn = true
			if iCount > 3:
				if illianTeam.isHasTech(gc.getInfoTypeForString('TECH_WINTER_TECH_IV')) == false:
					illianTeam.setHasTech(gc.getInfoTypeForString('TECH_WINTER_TECH_IV'), True, 1, True, True)
					bSpawn = true
			if bSpawn:
				pCity = illianPlayer.getCapitalCity()
				iUnit = gc.getInfoTypeForString('UNIT_WARRIOR')
				if illianTeam.isHasTech(gc.getInfoTypeForString('TECH_BRONZE_WORKING')):
					iUnit = gc.getInfoTypeForString('UNIT_AXEMAN')
				if illianTeam.isHasTech(gc.getInfoTypeForString('TECH_IRON_WORKING')):
					iUnit = gc.getInfoTypeForString('UNIT_MACEMAN')
				for i in range(CyGame().getHandicapType() + 1):
					newUnit = illianPlayer.initUnit(iUnit, pCity.getX(), pCity.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
					newUnit.setHasPromotion(gc.getInfoTypeForString('PROMOTION_MOBILITY'), true)

		CvTopCivs.CvTopCivs().turnChecker(iGameTurn)

	def onBeginPlayerTurn(self, argsList):
		'Called at the beginning of a players turn'
		iGameTurn, iPlayer = argsList
		py = PyPlayer(iPlayer)

		iArcher = gc.getInfoTypeForString('UNITCOMBAT_ARCHER')
		iBlizzard = gc.getInfoTypeForString('IMPROVEMENT_BLIZZARD')
		iFrostling = gc.getInfoTypeForString('UNIT_FROSTLING')
		iHamstrung = gc.getInfoTypeForString('PROMOTION_HAMSTRUNG')
		iHasCasted = gc.getInfoTypeForString('PROMOTION_HAS_CASTED')
		iHasted = gc.getInfoTypeForString('PROMOTION_HASTED')
		iLairSpawnChance = gc.getDefineINT('LAIR_SPAWN_CHANCE')
		iMokka = gc.getInfoTypeForString('UNIT_MOKKA')
		iOrbofSucellus = gc.getInfoTypeForString('UNIT_ORB_OF_SUCELLUS')
		iPOrbofSucellus = gc.getInfoTypeForString('PROMOTION_ORB_OF_SUCELLUS')
		pPlayer = gc.getPlayer(iPlayer)

		for pUnit in py.getUnitList():
			if (pUnit.getUnitType() == iOrbofSucellus or pUnit.isHasPromotion(iPOrbofSucellus)):
				iX = pUnit.getX()
				iY = pUnit.getY()
				for iiX in range(iX-3, iX+4, 1):
					for iiY in range(iY-3, iY+4, 1):
						pPlot = CyMap().plot(iiX,iiY)
						if pPlot.getImprovementType() == iBlizzard:
							pPlot.setImprovementType(-1)
			if pUnit.isHasPromotion(iHamstrung):
				if pUnit.getDamage() == 0:
					pUnit.setHasPromotion(iHamstrung, False)
			if pUnit.getUnitType() == iMokka:
				if CyGame().getSorenRandNum(100, "Mokka") <= iLairSpawnChance:
					newUnit = pPlayer.initUnit(iFrostling, pUnit.getX(), pUnit.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_NORTH)
			pUnit.setHasPromotion(iHasted, False)
			pUnit.setHasPromotion(iHasCasted, False)
			if pPlayer.isHuman() == False:
				if pUnit.getUnitCombatType() == iArcher:
					eTeam = gc.getTeam(pPlayer.getTeam())
					iDamageLimit = pUnit.collateralDamageLimit()
					iMaxUnits = pUnit.collateralDamageMaxUnits()
					iX = pUnit.getX()
					iY = pUnit.getY()
					for iiX in range(iX-1, iX+2, 1):
						for iiY in range(iY-1, iY+2, 1):
							pPlot = CyMap().plot(iiX,iiY)
							if pPlot.getNumUnits() > 0:
								bHit = False
								for i in range(pPlot.getNumUnits()):
									pTarget = pPlot.getUnit(i)
									e2Team = gc.getPlayer(pTarget.getOwner()).getTeam()
									if (eTeam.isAtWar(e2Team) and pTarget.getDamage() < iDamageLimit and iMaxUnits > 0):
										iMaxUnits -= 1
										iDmg = CyGame().getSorenRandNum(8 * pUnit.baseCombatStr(), "Barrage")
										iDmg -= 2 * pTarget.baseCombatStr()
										if iDmg < 1:
											iDmg = 1
										if iDmg + pTarget.getDamage() > iDamageLimit:
											iDmg = iDamageLimit - pTarget.getDamage()
										pTarget.changeDamage(iDmg, iPlayer)
										sMessage = PyHelpers.PyInfo.UnitInfo(pTarget.getUnitType()).getDescription() + " " + CyTranslator().getText("TXT_KEY_MESSAGE_BARRAGE", (iDmg, ()))
										CyInterface().addMessage(pTarget.getOwner(),True,25,sMessage,'AS2D_ARCHERY_BARRAGE',1,'Art/Interface/Buttons/Spells/Barrage.dds',ColorTypes(7),pUnit.getX(),pUnit.getY(),True,True)
										bHit = True
								if bHit == True:
									point = pPlot.getPoint()
									CyEngine().triggerEffect(gc.getInfoTypeForString('EFFECT_DIGDIRT'),point)
			if iPlayer == gc.getBARBARIAN_PLAYER():
				if pUnit.getUnitType() == gc.getInfoTypeForString('UNIT_DRIFA'):
					pPlot = pUnit.plot()
					if pPlot.isCity():
						pCity = pPlot.getPlotCity()
						if pCity.getOwner() == gc.getBARBARIAN_PLAYER():
							pCity.kill()

		iFireball = gc.getInfoTypeForString('UNITCLASS_FIREBALL')
		iFloatingEye = gc.getInfoTypeForString('UNITCLASS_FLOATING_EYE')
		if (gc.getPlayer(0).getUnitClassCount(iFireball) > 0 or gc.getPlayer(0).getUnitClassCount(iFloatingEye) > 0):
			py2 = PyPlayer(0)
			for pUnit in py2.getUnitList():
				if (pUnit.getUnitClassType() == iFireball or pUnit.getUnitClassType() == iFloatingEye):
					pUnit.kill(True,0)

	def onCombatResult(self, argsList):
		'Combat Result'
		pWinner,pLoser = argsList
		playerX = PyPlayer(pWinner.getOwner())
		unitX = PyInfo.UnitInfo(pWinner.getUnitType())
		playerY = PyPlayer(pLoser.getOwner())
		unitY = PyInfo.UnitInfo(pLoser.getUnitType())
		pPlayer = gc.getPlayer(pWinner.getOwner())

		if pLoser.isHasPromotion(gc.getInfoTypeForString('PROMOTION_GODSLAYER_BLADE')):
			newUnit = pPlayer.initUnit(gc.getInfoTypeForString('UNIT_GODSLAYER_BLADE'), pWinner.getX(), pWinner.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_NORTH)

		if pLoser.isHasPromotion(gc.getInfoTypeForString('PROMOTION_GODSLAYER_CROSSGUARD')):
			newUnit = pPlayer.initUnit(gc.getInfoTypeForString('UNIT_GODSLAYER_CROSSGUARD'), pWinner.getX(), pWinner.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_NORTH)

		if pLoser.isHasPromotion(gc.getInfoTypeForString('PROMOTION_GODSLAYER_HILT')):
			newUnit = pPlayer.initUnit(gc.getInfoTypeForString('UNIT_GODSLAYER_HILT'), pWinner.getX(), pWinner.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_NORTH)

		if pLoser.isHasPromotion(gc.getInfoTypeForString('PROMOTION_ORB_OF_SUCELLUS')):
			newUnit = pPlayer.initUnit(gc.getInfoTypeForString('UNIT_ORB_OF_SUCELLUS'), pWinner.getX(), pWinner.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_NORTH)

		if pWinner.isHasPromotion(gc.getInfoTypeForString('PROMOTION_SUBDUE_ANIMAL')):
			if pLoser.getUnitCombatType() == gc.getInfoTypeForString('UNITCOMBAT_ANIMAL'):
				iUnit = pLoser.getUnitType()
				pClearPlot = self.findClearPlot(pLoser)
				if (pLoser.plot().getNumUnits() == 1 and pClearPlot != -1):
					pPlot = pLoser.plot()
					pLoser.setXY(pClearPlot.getX(), pClearPlot.getY(), false, true, true)
				else:
					pPlot = pWinner.plot()
				newUnit = pPlayer.initUnit(iUnit, pPlot.getX(), pPlot.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_NORTH)
				pLoser.setDamage(75, False)
				newUnit.convert(pLoser)
				pLoser.setDamage(100, False)
				newUnit.finishMoves()

		if pLoser.getUnitType() == gc.getInfoTypeForString('UNIT_MULCARN'):
			popupInfo = CyPopupInfo()
			popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON_SCREEN)
			popupInfo.setData1(3)
			popupInfo.setData2(1)
			popupInfo.setData3(3)
			popupInfo.setText(u"showWonderMovie")
			popupInfo.addPopup(pWinner.getOwner())
			gc.getGame().setWinner(pWinner.getOwner(), CvUtil.findInfoTypeNum(gc.getHandicapInfo,gc.getNumHandicapInfos(),"VICTORY_CONQUEST"))

		if (pLoser.getUnitType() == gc.getInfoTypeForString('UNIT_KYLORIN') or pLoser.getUnitType() == gc.getInfoTypeForString('UNIT_KYLORIN_MOUNTED')):
			self.addPopup(CyTranslator().getText("TXT_KEY_POPUP_KYLORIN_DEFEATED",()))
			popupInfo = CyPopupInfo()
			popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON_SCREEN)
			popupInfo.setData1(2)
			popupInfo.setData2(1)
			popupInfo.setData3(3)
			popupInfo.setText(u"showWonderMovie")
			popupInfo.addPopup(pWinner.getOwner())
			gc.getGame().setWinner(pWinner.getOwner(), CvUtil.findInfoTypeNum(gc.getHandicapInfo,gc.getNumHandicapInfos(),"VICTORY_CONQUEST"))

		if pLoser.getUnitType() == gc.getInfoTypeForString('UNIT_MALUS'):
			self.addPopup(CyTranslator().getText("TXT_KEY_POPUP_MALUS_DEFEATED",()))
			pPlot = pLoser.plot()
			pPlot.setFeatureType(gc.getInfoTypeForString('FEATURE_ICE'), -1)
			newUnit = pPlayer.initUnit(gc.getInfoTypeForString('UNIT_GALLEON'), pPlot.getX(), pPlot.getY()+1, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_WEST)

		if pWinner.getUnitType() == gc.getInfoTypeForString('UNIT_FIREBALL'):
			py = PyPlayer(pWinner.getOwner())
			iEpona = gc.getInfoTypeForString('UNIT_EPONA_SORCERESS')
			for pUnit in py.getUnitList():
				if pUnit.getUnitType() == iEpona:
					pUnit.changeExperience(1, -1, true, true, true)
					break
			pPlot = pLoser.plot()
			point = pPlot.getPoint()
			CyEngine().triggerEffect(gc.getInfoTypeForString('EFFECT_ARTILLERY_SHELL_EXPLODE'),point)
			CyAudioGame().Play3DSound("AS3D_UN_GRENADE_EXPLODE",point.x,point.y,point.z)

		if pLoser.getUnitType() == gc.getInfoTypeForString('UNIT_FIREBALL'):
			pPlot = pWinner.plot()
			point = pPlot.getPoint()
			CyEngine().triggerEffect(gc.getInfoTypeForString('EFFECT_ARTILLERY_SHELL_EXPLODE'),point)
			CyAudioGame().Play3DSound("AS3D_UN_GRENADE_EXPLODE",point.x,point.y,point.z)

		if (pLoser.getUnitType() == gc.getInfoTypeForString('UNIT_STAG') and pPlayer.getCivilizationType() == gc.getInfoTypeForString('CIVILIZATION_AMURITES')):
			popupInfo = CyPopupInfo()
			popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
			popupInfo.setText(CyTranslator().getText("TXT_KEY_POPUP_STAG_CAPTURE",()))
			popupInfo.setData1(pWinner.getOwner())
			popupInfo.setOnClickedPythonCallback("defeatStagFunc")
			popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_STAG_SPARE", ()), "")
			popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_STAG_KILL", ()), "")
			popupInfo.addPopup(0)

		if (pLoser.getUnitType() == gc.getInfoTypeForString('UNIT_ORB_OF_SUCELLUS') and pPlayer.getCivilizationType() == gc.getInfoTypeForString('CIVILIZATION_AMURITES') and CyGame().getUnitCreatedCount(gc.getInfoTypeForString('UNIT_ORB_OF_SUCELLUS')) == 1):
			self.addPopup(CyTranslator().getText("TXT_KEY_POPUP_ORB_OF_SUCELLUS",()))

		if pLoser.getUnitType() == gc.getInfoTypeForString('UNIT_LUGH'):
			if pPlayer.getCivilizationType() == gc.getInfoTypeForString('CIVILIZATION_AMURITES'):
				pPlayer2 = gc.getPlayer(pLoser.getOwner())
				if pPlayer2.getNumCities() == 1:
					popupInfo = CyPopupInfo()
					popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
					popupInfo.setData1(pLoser.getOwner())
					popupInfo.setData2(pPlayer2.getCapitalCity().getX())
					popupInfo.setData3(pPlayer2.getCapitalCity().getY())
					popupInfo.setText(CyTranslator().getText("TXT_KEY_POPUP_DEFEAT_DOVIELLO",()))
					popupInfo.setOnClickedPythonCallback("defeatDovielloFunc")
					popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_DOVIELLO_PEACE", ()), "")
					popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_DOVIELLO_WAR", ()), "")
					popupInfo.addPopup(pWinner.getOwner())

		if playerX and playerX and unitX and playerY:
			CvUtil.pyPrint('Player %d Civilization %s Unit %s has defeated Player %d Civilization %s Unit %s' 
				%(playerX.getID(), playerX.getCivilizationName(), unitX.getDescription(), 
				playerY.getID(), playerY.getCivilizationName(), unitY.getDescription()))

	def onUnitMove(self, argsList):
		'unit move'
		pPlot,pUnit,pOldPlot = argsList
		player = PyPlayer(pUnit.getOwner())
		unitInfo = PyInfo.UnitInfo(pUnit.getUnitType())
		pPlayer = gc.getPlayer(pUnit.getOwner())
		bPlayer = gc.getPlayer(gc.getBARBARIAN_PLAYER())
		unitType = pUnit.getUnitType()

		if pPlot.getImprovementType() == gc.getInfoTypeForString('IMPROVEMENT_BLIZZARD'):
			self.doBlizzardOnUnit(pUnit)

		if pPlayer.getCivilizationType() == gc.getInfoTypeForString('CIVILIZATION_AMURITES'):
			iX = pUnit.getX()
			iY = pUnit.getY()
			if pPlot.getNumUnits() == 1:
				for iiX in range(iX-1, iX+2, 1):
					for iiY in range(iY-1, iY+2, 1):
						p2Plot = CyMap().plot(iiX,iiY)
						if p2Plot.getFeatureType() == gc.getInfoTypeForString('FEATURE_LETUM_FRIGUS'):
							if unitType == gc.getInfoTypeForString('UNIT_KYLORIN'):
								self.addPopup(CyTranslator().getText("TXT_KEY_POPUP_APPROCH_MULCARN",()))
						if p2Plot.getFeatureType() == gc.getInfoTypeForString('FEATURE_VOLCANO'):
							for i in range(p2Plot.getNumUnits()):
								p2Unit = p2Plot.getUnit(i)
								if p2Unit.getUnitType() == gc.getInfoTypeForString('UNIT_GODSLAYER_HILT'):
									popupInfo = CyPopupInfo()
									popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
									popupInfo.setText(CyTranslator().getText("TXT_KEY_POPUP_HILT",()))
									popupInfo.setData1(iiX)
									popupInfo.setData2(iiY)
									popupInfo.setOnClickedPythonCallback("pullHiltFunc")
									popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_PULL_HILT", ()), "")
									popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_LEAVE_HILT", ()), "")
									popupInfo.addPopup(0)
						if (p2Plot.getFeatureType() == gc.getInfoTypeForString('FEATURE_FROZEN_SHIP') and CyGame().isUnitClassMaxedOut(gc.getInfoTypeForString('UNITCLASS_MALUS'), 0) == False):
							bPlayer = gc.getPlayer(gc.getBARBARIAN_PLAYER())
							newUnit = bPlayer.initUnit(gc.getInfoTypeForString('UNIT_MALUS'), p2Plot.getX(), p2Plot.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
							self.addPopup(CyTranslator().getText("TXT_KEY_POPUP_MALUS",()))
			if pPlot.getFeatureType() == gc.getInfoTypeForString('FEATURE_HUT'):
				pPlot.setFeatureType(-1, -1)
				CyInterface().addMessage(pUnit.getOwner(),True,25,CyTranslator().getText("TXT_KEY_POPUP_DESTROY_DEN",()),'AS2D_CITYRAZE',1,'Art/Interface/Buttons/Actions/Pillage.dds',ColorTypes(7),pUnit.getX(),pUnit.getY(),True,True)
				pPlayer.changeGold(10 + CyGame().getSorenRandNum(30, "Gold"))
			if pPlot.getFeatureType() == gc.getInfoTypeForString('FEATURE_FROST_GIANT_CASTLE'):
				pPlot.setFeatureType(-1, -1)
				pPlot.setImprovementType(gc.getInfoTypeForString('IMPROVEMENT_CITY_RUINS'))
				CyInterface().addMessage(pUnit.getOwner(),True,25,CyTranslator().getText("TXT_KEY_POPUP_DESTROY_FROST_GIANT_CASTLE",()),'AS2D_CITYRAZE',1,'Art/Interface/Buttons/Actions/Pillage.dds',ColorTypes(7),pUnit.getX(),pUnit.getY(),True,True)
				pPlayer.changeGold(30 + CyGame().getSorenRandNum(30, "Gold"))
			if pPlot.getFeatureType() == gc.getInfoTypeForString('FEATURE_CHANCEL'):
				eTeam = gc.getTeam(pPlayer.getTeam())
				if eTeam.isHasTech(gc.getInfoTypeForString('TECH_KNOWLEDGE_OF_THE_ETHER')) == False:
					self.addPopup(CyTranslator().getText("TXT_KEY_POPUP_EXPLORE_CHANCEL",()))
					eTeam.setHasTech(gc.getInfoTypeForString('TECH_KNOWLEDGE_OF_THE_ETHER'), True, pUnit.getOwner(), True, True)

		if pPlayer.getCivilizationType() != gc.getInfoTypeForString('CIVILIZATION_AMURITES'):
			if (pPlot.getFeatureType() == gc.getInfoTypeForString('FEATURE_TRAP') and pUnit.getUnitType() != gc.getInfoTypeForString('UNIT_FIACRA')):
				point = pPlot.getPoint()
				CyEngine().triggerEffect(gc.getInfoTypeForString('EFFECT_SPELL'),point)
				CyAudioGame().Play3DSound("AS3D_UN_OMEN_FIRE",point.x,point.y,point.z)
				pUnit.setHasPromotion(gc.getInfoTypeForString('PROMOTION_HAMSTRUNG'), True)
				pUnit.setDamage(pUnit.getDamage() + 30, False)
				pPlot.setFeatureType(-1, -1)

		if (pUnit.getUnitType() == gc.getInfoTypeForString('UNIT_ORB_OF_SUCELLUS') or pUnit.isHasPromotion(gc.getInfoTypeForString('PROMOTION_ORB_OF_SUCELLUS'))):
			iBlizzard = gc.getInfoTypeForString('IMPROVEMENT_BLIZZARD')
			iX = pUnit.getX()
			iY = pUnit.getY()
			for iiX in range(iX-3, iX+4, 1):
				for iiY in range(iY-3, iY+4, 1):
					pPlot = CyMap().plot(iiX,iiY)
					if pPlot.getImprovementType() == iBlizzard:
						pPlot.setImprovementType(-1)

		if player and unitInfo:
			CvUtil.pyPrint('Player %d Civilization %s unit %s is moving to %d, %d' 
				%(player.getID(), player.getCivilizationName(), unitInfo.getDescription(), 
				pUnit.getX(), pUnit.getY()))

	def onBuildingBuilt(self, argsList):
		'Building Completed'
		pCity, iBuildingType = argsList
		game = CyGame()
		if ((not CyGame().isNetworkMultiPlayer()) and (pCity.getOwner() == CyGame().getActivePlayer()) and isWorldWonderClass(gc.getBuildingInfo(iBuildingType).getBuildingClassType())):
			# If this is a wonder...
			popupInfo = CyPopupInfo()
			popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON_SCREEN)
			popupInfo.setData1(iBuildingType)
			popupInfo.setData2(pCity.getID())
			popupInfo.setData3(0)
			popupInfo.setText(u"showWonderMovie")
			popupInfo.addPopup(pCity.getOwner())

		CvUtil.pyPrint('%s was finished by Player %d Civilization %s' 
			%(PyInfo.BuildingInfo(iBuildingType).getDescription(), pCity.getOwner(), gc.getPlayer(pCity.getOwner()).getCivilizationDescription(0)))

	def onSetPlayerAlive(self, argsList):
		'Set Player Alive Event'
		iPlayerID = argsList[0]
		bNewValue = argsList[1]

		if bNewValue == False:
			pPlayer = gc.getPlayer(iPlayerID)
			if pPlayer.getCivilizationType() == gc.getInfoTypeForString('CIVILIZATION_AMURITES'):
				popupInfo = CyPopupInfo()
				popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON_SCREEN)
				popupInfo.setData1(2)
				popupInfo.setData2(1)
				popupInfo.setData3(3)
				popupInfo.setText(u"showWonderMovie")
				popupInfo.addPopup(iPlayerID)

		CvUtil.pyPrint("Player %d's alive status set to: %d" %(iPlayerID, int(bNewValue)))

	def onImprovementBuilt(self, argsList):
		'Improvement Built'
		iImprovement, iX, iY = argsList

		pPlot = CyMap().plot(iX,iY)
		if iImprovement == gc.getInfoTypeForString('IMPROVEMENT_MAMMOTH_CAMP'):
			pPlot.setBonusType(gc.getInfoTypeForString('BONUS_IVORY'))

	def onUnitCreated(self, argsList):
		'Unit Completed'
		unit = argsList[0]
		player = PyPlayer(unit.getOwner())

		if unit.getUnitType() == gc.getInfoTypeForString('UNIT_CHILDREN_OF_KYLORIN'):
			Promotions = [ 'PROMOTION_MARK_OF_THE_BAT',
				'PROMOTION_MARK_OF_THE_DOG',
				'PROMOTION_MARK_OF_THE_HORSE',
				'PROMOTION_MARK_OF_THE_RABBIT',
				'PROMOTION_MARK_OF_THE_RAT',
				'PROMOTION_MARK_OF_THE_RAVEN',
				'PROMOTION_MARK_OF_THE_SCORPION' ]
			iChildrenMarkChance = gc.getDefineINT('CHILDREN_MARK_CHANCE')
			pPlayer = gc.getPlayer(unit.getOwner())
			if (pPlayer.getUnitClassCount(gc.getInfoTypeForString('UNITCLASS_EPONA')) > 0 or pPlayer.getUnitClassCount(gc.getInfoTypeForString('UNITCLASS_EPONA_SORCERESS'))):
				iChildrenMarkChance = iChildrenMarkChance + (iChildrenMarkChance / 2)
			iRnd = CyGame().getSorenRandNum(len(Promotions), "Children of Kylorin")
			unit.setHasPromotion(gc.getInfoTypeForString(Promotions[iRnd]), True)
			for promotion in Promotions:
				if CyGame().getSorenRandNum(100, "Bob") <= iChildrenMarkChance:
					unit.setHasPromotion(gc.getInfoTypeForString(promotion), True)

	def onCityDoTurn(self, argsList):
		'City Production'
		pCity = argsList[0]
		iPlayer = argsList[1]

		pPlayer = gc.getPlayer(pCity.getOwner())

		pCity.setNumRealBuilding(gc.getInfoTypeForString('BUILDING_EPONAS_HEARTH'), 0)
		if (pPlayer.getUnitClassCount(gc.getInfoTypeForString('UNITCLASS_EPONA')) > 0 or pPlayer.getUnitClassCount(gc.getInfoTypeForString('UNITCLASS_EPONA_SORCERESS'))):
			pPlot = pCity.plot()
			for i in range(pPlot.getNumUnits()):
				pUnit = pPlot.getUnit(i)
				if (pUnit.getUnitType() == gc.getInfoTypeForString('UNIT_EPONA') or pUnit.getUnitType() == gc.getInfoTypeForString('UNIT_EPONA_SORCERESS')):
					pCity.setNumRealBuilding(gc.getInfoTypeForString('BUILDING_EPONAS_HEARTH'), 1)

		CvAdvisorUtils.cityAdvise(pCity, iPlayer)

	def onCityRazed(self, argsList):
		'City Razed'
		city, iPlayer = argsList
		
		owner = PyPlayer(city.getOwner())
		razor = PyPlayer(iPlayer)

		pPlayer = gc.getPlayer(iPlayer)
		pOldPlayer = gc.getPlayer(city.getOwner())
		if pPlayer.getCivilizationType() == gc.getInfoTypeForString('CIVILIZATION_AMURITES'):
			if pOldPlayer.getCivilizationType() == gc.getInfoTypeForString('CIVILIZATION_DOVIELLO'):
				if (pOldPlayer.getNumCities() == 2 and pOldPlayer.getUnitClassCount(gc.getInfoTypeForString('UNITCLASS_LUGH')) == 0):
					popupInfo = CyPopupInfo()
					popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
					popupInfo.setData1(city.getOwner())
					popupInfo.setData2(city.getX())
					popupInfo.setData3(city.getY())
					popupInfo.setText(CyTranslator().getText("TXT_KEY_POPUP_DEFEAT_DOVIELLO",()))
					popupInfo.setOnClickedPythonCallback("defeatDovielloFunc")
					popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_DOVIELLO_PEACE", ()), "")
					popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_DOVIELLO_WAR", ()), "")
					popupInfo.addPopup(iPlayer)

		CvUtil.pyPrint('Player %d Civilization %s City %s was razed by Player %d' 
			%(owner.getID(), owner.getCivilizationName(), city.getName(), razor.getID()))
		CvUtil.pyPrint("City Razed Event: %s" %(city.getName(),))

	def onCityAcquired(self, argsList):
		'City Acquired'
		iPreviousOwner,iNewOwner,pCity,bConquest,bTrade = argsList
		CvUtil.pyPrint('City Acquired Event: %s' %(pCity.getName()))

		pPlayer = gc.getPlayer(iNewOwner)
		pOldPlayer = gc.getPlayer(iPreviousOwner)
		pCity.setHasReligion(gc.getInfoTypeForString('RELIGION_THE_WHITE_HAND'), False, True, True)
		if pPlayer.getCivilizationType() == gc.getInfoTypeForString('CIVILIZATION_AMURITES'):
			if pOldPlayer.getCivilizationType() == gc.getInfoTypeForString('CIVILIZATION_DOVIELLO'):
				if (pOldPlayer.getNumCities() == 1 and pOldPlayer.getUnitClassCount(gc.getInfoTypeForString('UNITCLASS_LUGH')) == 0):
					popupInfo = CyPopupInfo()
					popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
					popupInfo.setData1(iPreviousOwner)
					popupInfo.setData2(pCity.getX())
					popupInfo.setData3(pCity.getY())
					popupInfo.setText(CyTranslator().getText("TXT_KEY_POPUP_DEFEAT_DOVIELLO",()))
					popupInfo.setOnClickedPythonCallback("defeatDovielloFunc")
					popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_DOVIELLO_PEACE", ()), "")
					popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_DOVIELLO_WAR", ()), "")
					popupInfo.addPopup(iNewOwner)
