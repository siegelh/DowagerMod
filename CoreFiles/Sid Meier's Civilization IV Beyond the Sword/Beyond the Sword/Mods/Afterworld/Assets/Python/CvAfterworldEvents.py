# Afterworld
# Civilization 4 (c) 2007 Firaxis Games

# Created by - Tim McCracken & Jon Shafer

from CvPythonExtensions import *
import sys
import Popup as PyPopup
from PyHelpers import PyPlayer
import pickle
import CvEventManager
import CvScreenEnums
from CvScreenEnums import *
from PyHelpers import *
import CvUtil
import CvGameUtils
import AW

Afterworld = AW.g_Afterworld
AI_DISTANCE_NUM = 12

# globals
gc = CyGlobalContext()
localText = CyTranslator()

DefaultUnitAI = UnitAITypes.UNITAI_ATTACK_CITY_LEMMING

class CvAfterworldEvents(CvEventManager.CvEventManager):
	
	def __init__(self):
		
		self.parent = CvEventManager.CvEventManager
		self.parent.__init__(self)
		
		# if the first value is 1 then the positions need to be updated
		# the second value is a list of plots the players on
		self.PlayersPosition = None
		self.iIntroText = 0
		self.iSeverTurn = -1
		
	def onBeginGameTurn(self, argsList):
		'Called at the beginning of the end of each turn'
		iGameTurn = argsList[0]		
		Afterworld.updateMinimapSection()		
		
	def getReconPlot(self):
		return CyMap().plot(32, 4)
		
	def getUplinkPlot(self):
		return CyMap().plot(97, 1)
		
	def doCameraZoomUnit(self, pUnit):
		iActivePlayer = CyGame().getActivePlayer()
		iActiveTeam = gc.getPlayer(iActivePlayer).getTeam()
		pUnit.plot().changeVisibilityCount(iActiveTeam, 1, InvisibleTypes.NO_INVISIBLE)
		
		CyGInterfaceScreen("MainInterface", MAIN_INTERFACE).updateMinimapSection(true, true)
		
#		CyCamera().LookAtUnit(pUnit)
		CyCamera().JustLookAtPlot(pUnit.plot())
		CyCamera().ZoomIn(10.0)

	def doCameraZoomPlot(self, pPlot):
		iActivePlayer = CyGame().getActivePlayer()
		iActiveTeam = gc.getPlayer(iActivePlayer).getTeam()
		
		CyGInterfaceScreen("MainInterface", MAIN_INTERFACE).updateMinimapSection(true, true)
		
#		CyCamera().LookAtUnit(pUnit)
		CyCamera().JustLookAtPlot(pPlot)
		CyCamera().ZoomIn(10.0)

	def onEndGameTurn(self, argsList):
		self.parent.onEndGameTurn(self, argsList)
		iGameTurn = argsList[0]
		self.updateUnitData()
		pyPlayer = PyPlayer(0) #similar to pPlayer, but not, it's a wrapper; like MC Chris.
		pPlayer = gc.getPlayer(0)
		iTeam = pPlayer.getTeam()
		
		self.setPlayerOptions()
		
		unitList = pyPlayer.getUnitList()
		iBleeder = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_BLEEDER')
		iRabidBleeder = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_RABID_BLEEDER')
		iSavageBleeder = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_SAVAGE_BLEEDER')
		iFeral = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_FERAL')
		iW= CvUtil.findInfoTypeNum(gc.getFeatureInfo,gc.getNumFeatureInfos(),'FEATURE_AFTERWORLD_WALLS')
		iIW= CvUtil.findInfoTypeNum(gc.getFeatureInfo,gc.getNumFeatureInfos(),'FEATURE_AFTERWORLD_INTERIOR_WALLS')
		iT1= CvUtil.findInfoTypeNum(gc.getFeatureInfo,gc.getNumFeatureInfos(),'FEATURE_AFTERWORLD_TREE')
		iT2= CvUtil.findInfoTypeNum(gc.getFeatureInfo,gc.getNumFeatureInfos(),'FEATURE_AFTERWORLD_TREE2')
		iT3= CvUtil.findInfoTypeNum(gc.getFeatureInfo,gc.getNumFeatureInfos(),'FEATURE_AFTERWORLD_TREE3')
		iGround= CvUtil.findInfoTypeNum(gc.getFeatureInfo,gc.getNumFeatureInfos(),'FEATURE_AFTERWORLD_GROUND1')
		iB1= CvUtil.findInfoTypeNum(gc.getFeatureInfo,gc.getNumFeatureInfos(),'FEATURE_BARRIER1')
		iB2= CvUtil.findInfoTypeNum(gc.getFeatureInfo,gc.getNumFeatureInfos(),'FEATURE_BARRIER2')
		iB3= CvUtil.findInfoTypeNum(gc.getFeatureInfo,gc.getNumFeatureInfos(),'FEATURE_BARRIER3')
		iSever = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_SEVER')
		iShadow = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_SEVER_INVISIBLE')

		pHeadSelected = CyInterface().getHeadSelectedUnit()
		pReconPlot = self.getReconPlot()
		pUplinkPlot = self.getUplinkPlot()
		iReconTimerValue = int(pReconPlot.getScriptData())
		iUplinkTimerValue = int(pUplinkPlot.getScriptData())
		iUnitIDRagah = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_RAGAH')
		iSentinel1 = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_SENTINEL1')
		iJal = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_JAL')
		iRiest = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_RIEST')
		iAtticus= CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_ATTICUS')

		pSever_SecurityConsole = CyMap().plot(96, 7)
		pAtticus_SecurityConsole = CyMap().plot(86, 10)
		pJalUplinkPlot = CyMap().plot(91, 7)
		
		pReconPlot = self.getReconPlot()
		iReconTimerValue = int(pReconPlot.getScriptData())
		
		pUplinkPlot = self.getUplinkPlot()
		iUplinkTimerValue = int(pUplinkPlot.getScriptData())
		
		pDeceptionBeaconPlot = CyMap().plot(64, 2)
		
		pSecurityConsolePlot = CyMap().plot(85, 1)
		pUplinkTerminalPlot = CyMap().plot(91, 7)
		
		pBarricadeTerminal1Plot = CyMap().plot(103, 6)
		pBarricadeTerminal2Plot = CyMap().plot(114, 3)
		pBarricadeTerminal3Plot = CyMap().plot(131, 3)
		
		iBOPEN = CvUtil.findInfoTypeNum(gc.getFeatureInfo,gc.getNumFeatureInfos(),'FEATURE_AFTERWORLD_BARRICADES2')
		unitEntityChowList = PyPlayer(0).getUnitList()
		self.setupUnitAI()
		
		pFeralAppear = gc.getMap().plot(81, 7)
		pBustedWall = gc.getMap().plot(85, 10)
		pFakeFeral = pFeralAppear.getUnit(0)
		iFakeFeral = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_FAKEFERAL')
		
		if iGameTurn == 1:
			self.addPopup(localText.getText("TXT_KEY_TUTORIALTITLE", ()), localText.getText("TXT_KEY_TUTORIAL3", ()))

		if iGameTurn == 2:
			self.addPopup(localText.getText("TXT_KEY_TUTORIALTITLE", ()), localText.getText("TXT_KEY_TURNCAMERATUT", ()))
		
		#Entity Battle
		EntityBlast1 = gc.getInfoTypeForString('EFFECT_CREATION_BIG_FAST')
		EntityBlast2 = gc.getInfoTypeForString('EFFECT_CREATION_BIG')
		TeleportType = gc.getInfoTypeForString('EFFECT_EXPLOSION_SHOCKWAVE')
		
		if Afterworld.pAngryEntity == 1:
			
			print "Entity has reached stage 1"
			iRandomChow1 = CyGame().getSorenRandNum(len(unitEntityChowList), "Afterworld")
			pRandomUnit = unitEntityChowList[iRandomChow1]
			pPlot = pRandomUnit.plot()
			CyEngine().triggerEffect(EntityBlast1, pPlot.getPoint())
			pRandomUnit.changeDamage(20, 0)
			
		if Afterworld.pAngryEntity == 2:
			print "Entity has reached stage 2"
			iRandomChow2 = CyGame().getSorenRandNum(len(unitEntityChowList), "Afterworld")
			pRandomUnit = unitEntityChowList[iRandomChow2]
			pPlot = pRandomUnit.plot()
			CyEngine().triggerEffect(EntityBlast2, pPlot.getPoint())
			pRandomUnit.changeDamage(40, 0)
			print "The Entity has shot:"
			print pRandomUnit
			
#		#Shadow Walk Concludes#
		print "Starting Shadow Walk"
		unitSeverList = PyPlayer(0).getUnitList()
		for pInvisibleUnit in unitSeverList:
			if pInvisibleUnit.getUnitType() == CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_SEVER_INVISIBLE'):
				print "Shadow Walk Started"
				iShadowID = pInvisibleUnit.getID()
				pUnitData = Afterworld.getUnitDataByID(iShadowID)
				print("   Turns left on Shadow Walk %d" %(pUnitData.getInvisibilityTurns()))
				if pUnitData.getInvisibilityTurns() == 0:
					print "invisibility turns"
					plotX = pInvisibleUnit.getX()
					plotY = pInvisibleUnit.getY()
					iGrenades = pUnitData.getGrenadeTimer()
					iRepairMechs = pUnitData.getNumRepairMechanism()
					iAccMechs = pUnitData.getNumAccelerationMechanism()
					iDBeacons = pUnitData.getNumDeceptionBeacon()
					iSilence = pUnitData.getSilenceTimer()
					iExperience = pUnitData.getExperience()
					iPromotions = pUnitData.getNumPromotions()
					iDetonator = pUnitData.getDetonatorTimer()
					
					pInvisibleUnit.kill(true, -1)
					
					iSever = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_SEVER')
					pPlayer.initUnit(iSever, plotX, plotY, UnitAITypes.NO_UNITAI, DirectionTypes.NO_DIRECTION)
					
					# Find the unit we just initialized
					pNewUnit = -1
					pPlot = CyMap().plot(plotX, plotY)
					
					for iUnitLoop in range(pPlot.getNumUnits()):
						pUnitLoop = pPlot.getUnit(iUnitLoop)
						
						if (pUnitLoop.getUnitType() == iSever):
							
							pNewUnit = pUnitLoop
							break
					
					print("pNewUnit.getID()")
					print(pNewUnit.getID())
					
					# Re-assign ID of UnitData to our new unit object
					pUnitData.setID(pNewUnit.getID())
					
					# Transfer Experience amount from UnitData to the new unit object
					pNewUnit.setMoves(pUnitData.getMoves())
					pNewUnit.setLevel(pUnitData.getLevel())
					iMaxXP = 1000
					pNewUnit.setExperience(pUnitData.getExperience(), iMaxXP)
					
					# Transfer promotion data from Unit Data
					for iPromotionLoop in range(pUnitData.getNumPromotions()):
						iPromotionID = pUnitData.getPromotionFromList(iPromotionLoop)
						pNewUnit.setHasPromotion(iPromotionID, true)

					for iUnitDataLoop in range(Afterworld.getNumUnitDatas()):
						pData = Afterworld.getUnitDataByIndex(iUnitDataLoop)
		
		#Objective 1
		
		if Afterworld.iObjective != 0:
			pReconPlot.setOwner(1)
		if Afterworld.iObjective == 0:
			pReconPlot.setOwner(0)
			screen = CyGInterfaceScreen("MainInterface",CvScreenEnums.MAIN_INTERFACE)
			screen.minimapFlashPlot(pReconPlot.getX(), pReconPlot.getY(), 2, 999.0)

		if Afterworld.iStartReconTimer == 1:
			if iReconTimerValue == 10:#20
				self.addPopup(localText.getText("TXT_KEY_JAL", ()), localText.getText("TXT_KEY_LEVEL3END3", ()))
			if iReconTimerValue == 9: #40%
				self.addPopup(localText.getText("TXT_KEY_JAL", ()), localText.getText("TXT_KEY_LEVEL3END5", ()))
			if iReconTimerValue == 8: #60%
				self.addPopup(localText.getText("TXT_KEY_JAL", ()), localText.getText("TXT_KEY_LEVEL3END7", ()))
				self.addPopup(localText.getText("TXT_KEY_ATTICUS", ()), localText.getText("TXT_KEY_DISCOVERSENT1", ()))
				iX = pReconPlot.getX()
				iY = pReconPlot.getY()
				for xLoop in range (iX -2, iX +2):
					for yLoop in range (iY -2, iY +2):
						pSentSpawnPlot = gc.getMap().plot(xLoop, yLoop)
						iNumUnits = pSentSpawnPlot.getNumUnits()
						if iNumUnits == 0:
							gc.getPlayer(2).initUnit(iSentinel1, xLoop, yLoop, UnitAITypes.UNITAI_ATTACK_CITY_LEMMING, DirectionTypes.NO_DIRECTION)
							

			if iReconTimerValue == 7: #80%
				self.addPopup(localText.getText("TXT_KEY_JAL", ()), localText.getText("TXT_KEY_80PERCENT", ()))
			if iReconTimerValue == 6: #100%
				
				self.addPopup(localText.getText("TXT_KEY_JAL", ()), localText.getText("TXT_KEY_100PERCENT", ()))
				i1stBarrier = gc.getMap().plot(43, 10)
				i2ndBarrier = gc.getMap().plot(43, 11)
				i1stBarrier.setFeatureType(iBOPEN,1)
				i2ndBarrier.setFeatureType(iBOPEN,1)
				Afterworld.iObjective = 1
				CyGInterfaceScreen("MainInterface", MAIN_INTERFACE).setMinimapSectionOverride(.15, 0, 0.50, 1)
				Afterworld.addAfterworldMessage( localText.getText("TXT_KEY_JAL", ()), localText.getText("TXT_KEY_CS_1_2_1", ()))
				Afterworld.addAfterworldMessage( localText.getText("TXT_KEY_JAL", ()), localText.getText("TXT_KEY_CS_1_2_2", ()))
				Afterworld.addAfterworldMessage( localText.getText("TXT_KEY_JAL", ()), localText.getText("TXT_KEY_CS_1_2_3", ()))
				Afterworld.addAfterworldMessage( localText.getText("TXT_KEY_JAL", ()), localText.getText("TXT_KEY_CS_1_2_4", ()))
				self.addPopup(localText.getText("TXT_KEY_NEWOBJECTIVE", ()), localText.getText("TXT_KEY_NEWOBJECTIVE2", ()))
				
				Afterworld.addAfterworldMessage( localText.getText("TXT_KEY_JAL", ()), localText.getText("TXT_KEY_CS_2_1_0", ()))
				Afterworld.addAfterworldMessage( localText.getText("TXT_KEY_JAL", ()), localText.getText("TXT_KEY_JALREADS0", ()))
				Afterworld.addAfterworldMessage( localText.getText("TXT_KEY_JAL", ()), localText.getText("TXT_KEY_CS_2_1_01", ()))
				Afterworld.addAfterworldMessage( localText.getText("TXT_KEY_JAL", ()), localText.getText("TXT_KEY_CS_2_1_02", ()))
				Afterworld.addAfterworldMessage( localText.getText("TXT_KEY_JAL", ()), localText.getText("TXT_KEY_JALREADS1", ()))
				Afterworld.addAfterworldMessage( localText.getText("TXT_KEY_JAL", ()), localText.getText("TXT_KEY_CS_2_1_04", ()))
				Afterworld.addAfterworldMessage( localText.getText("TXT_KEY_JAL", ()), localText.getText("TXT_KEY_CS_2_1_05", ()))
				Afterworld.addAfterworldMessage( localText.getText("TXT_KEY_JAL", ()), localText.getText("TXT_KEY_CS_2_1_06", ()))
				
				pDeceptionBeaconPlot.setOwner(0) #Deception Beacon plot

		#Objective 2 location
		if Afterworld.iObjective != 1:
			pDeceptionBeaconPlot.setOwner(1)
			
		if Afterworld.iObjective == 1:
			pDeceptionBeaconPlot.setOwner(0)
			
			screen = CyGInterfaceScreen("MainInterface",CvScreenEnums.MAIN_INTERFACE)
			screen.minimapFlashPlot(64, 2, 2, 90.0)
			
		#Objective 3a location
		if Afterworld.iObjective!= 2:
			pSecurityConsolePlot.setOwner(1)
		
		if Afterworld.iObjective == 2:
			pSecurityConsolePlot.setOwner(0)
			screen = CyGInterfaceScreen("MainInterface",CvScreenEnums.MAIN_INTERFACE)
			screen.minimapFlashPlot(85, 1, 2, 999.0)
			
		#Objective 3b location
		if Afterworld.iObjective!= 9:
			pUplinkTerminalPlot.setOwner(1)
						
		if Afterworld.iObjective == 9:
			pUplinkTerminalPlot.setOwner(0)
			screen = CyGInterfaceScreen("MainInterface",CvScreenEnums.MAIN_INTERFACE)
			screen.minimapFlashPlot(91, 7, 2, 999.0)
			
		bJal = false
		bAtticus = false
		bSever = false
		for pUnits in unitList:
			if (pUnits.getUnitType()) == iJal:
				iX = pUnits.getX()
				iY = pUnits.getY()
				if iX == 91 and iY == 7:
					print "Jal is in place"
					bJal = true
			if (pUnits.getUnitType()) == iAtticus:
				iX = pUnits.getX()
				iY = pUnits.getY()
				if iX == 86 and iY == 10:
					print "Atticus is in place"
					bAtticus = true
			if (pUnits.getUnitType()) == iSever:
				iX = pUnits.getX()
				iY = pUnits.getY()
				if iX == 96 and iY == 7:
					print "Sever is in place"
					bSever = true
					
			if bJal and bAtticus and bSever:
				print "all true"
				if Afterworld.iStartUplinkTimer == 0:
					pUplinkPlot.setScriptData("10")
					self.addPopup(localText.getText("TXT_KEY_JAL", ()), localText.getText("TXT_KEY_LEVEL3END1", ()))
					Afterworld.iStartUplinkTimer = 1
					Afterworld.iObjective = 99
					Afterworld.addAfterworldMessage( localText.getText("TXT_KEY_ATTICUS", ()), localText.getText("TXT_KEY_ATTICUSOB3B", ()))
					Afterworld.addAfterworldMessage( localText.getText("TXT_KEY_ATTICUS", ()), localText.getText("TXT_KEY_ATTICUSOB3B2", ()))
					Afterworld.addAfterworldMessage( localText.getText("TXT_KEY_JAL", ()), localText.getText("TXT_KEY_JALOB32", ()))
					Afterworld.addAfterworldMessage( localText.getText("TXT_KEY_RAGAH", ()), localText.getText("TXT_KEY_RAGAHOB3", ()))
					Afterworld.addAfterworldMessage( localText.getText("TXT_KEY_SEVER", ()), localText.getText("TXT_KEY_SEVEROB3", ()))
					Afterworld.addAfterworldMessage( localText.getText("TXT_KEY_RIEST", ()), localText.getText("TXT_KEY_CS_2_1_7", ()))
					Afterworld.addAfterworldMessage( localText.getText("TXT_KEY_RIEST", ()), localText.getText("TXT_KEY_PAGETHREE2", ()))
					Afterworld.addAfterworldMessage( localText.getText("TXT_KEY_SEVER", ()), localText.getText("TXT_KEY_SEVEROB32", ()))
					Afterworld.addAfterworldMessage( localText.getText("TXT_KEY_RAGAH", ()), localText.getText("TXT_KEY_RAGAHOB32", ()))
					Afterworld.addAfterworldMessage( localText.getText("TXT_KEY_JAL", ()), localText.getText("TXT_KEY_PAGETHREE2JAL", ()))
					Afterworld.addAfterworldMessage( localText.getText("TXT_KEY_RIEST", ()), localText.getText("TXT_KEY_RIESTOB3", ()))
					Afterworld.addAfterworldMessage( localText.getText("TXT_KEY_RAGAH", ()), localText.getText("TXT_KEY_RAGAHOB33", ()))
					Afterworld.addAfterworldMessage( localText.getText("TXT_KEY_JAL", ()), localText.getText("TXT_KEY_PAGETHREE5JAL", ()))
					Afterworld.addAfterworldMessage( localText.getText("TXT_KEY_SEVER", ()), localText.getText("TXT_KEY_SEVEROB33", ()))
					Afterworld.addAfterworldMessage( localText.getText("TXT_KEY_RAGAH", ()), localText.getText("TXT_KEY_RAGAHOB34", ()))
					Afterworld.iChatMessages = 3			

		if Afterworld.iStartUplinkTimer == 1:
			if Afterworld.iObjective == 99:
				print "Afterworld Objective"
				print Afterworld.iObjective
				print iUplinkTimerValue
				print "Uplink"
				if iUplinkTimerValue == 9:#10			
					print iUplinkTimerValue
					self.addPopup(localText.getText("TXT_KEY_JAL", ()), localText.getText("TXT_KEY_LEVEL3END2", ()))  #Show Feral
					gc.getPlayer(2).initUnit(iFakeFeral, 81, 7, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_EAST)
					self.doCameraZoomPlot(pFeralAppear)
					pFeralAppear.setOwner(0)

			if Afterworld.iObjective == 99:
				if iUplinkTimerValue == 8: #UPLINK20%		
					self.addPopup(localText.getText("TXT_KEY_JAL", ()), localText.getText("TXT_KEY_LEVEL3END3", ()))
					pFeralAppear.setOwner(1)
					pFakeFeral.kill(true, -1)
					
			if Afterworld.iObjective == 99:
				if iUplinkTimerValue == 7: #30%		
					self.addPopup(localText.getText("TXT_KEY_JAL", ()), localText.getText("TXT_KEY_LEVEL3END4", ()))
					iX = pJalUplinkPlot.getX()
					iY = pJalUplinkPlot.getY()
					for xLoop in range (iX -1, iX +1):
						for yLoop in range (iY -1, iY +1):
							pSentSpawnPlot = gc.getMap().plot(xLoop, yLoop)
							iNumUnits = pSentSpawnPlot.getNumUnits()
							if iNumUnits == 0:
								gc.getPlayer(2).initUnit(iSentinel1, xLoop, yLoop, UnitAITypes.UNITAI_ATTACK_CITY_LEMMING, DirectionTypes.NO_DIRECTION)					
								
			if Afterworld.iObjective == 99:
				if iUplinkTimerValue == 6: #40%		
					self.addPopup(localText.getText("TXT_KEY_JAL", ()), localText.getText("TXT_KEY_LEVEL3END5", ()))
					pDirt = gc.getInfoTypeForString('EFFECT_EXPLOSION_DIRT')
					pSplode = gc.getInfoTypeForString('EFFECT_LARGE_OILY_DEATH')
					pBustedWall.setFeatureType(iGround,1)
					self.doCameraZoomPlot(pBustedWall)
					pBustedWall.setOwner(0)
					CyEngine().triggerEffect(pSplode, pBustedWall.getPoint())
					CyEngine().triggerEffect(pDirt, pBustedWall.getPoint())
					gc.getPlayer(2).initUnit(iFeral, 84, 10, UnitAITypes.UNITAI_ATTACK_CITY_LEMMING, DirectionTypes.DIRECTION_EAST)
					
			if Afterworld.iObjective == 99:
				if iUplinkTimerValue == 5: #50%		
					self.addPopup(localText.getText("TXT_KEY_JAL", ()), localText.getText("TXT_KEY_LEVEL3END6", ()))
					
			if Afterworld.iObjective == 99:
				if iUplinkTimerValue == 4: #60	
					iX = pJalUplinkPlot.getX()
					iY = pJalUplinkPlot.getY()
					for xLoop in range (iX -2, iX +2):
						for yLoop in range (iY -2, iY +2):
							pSentSpawnPlot = gc.getMap().plot(xLoop, yLoop)
							iNumUnits = pSentSpawnPlot.getNumUnits()
							if iNumUnits == 0:
								gc.getPlayer(2).initUnit(iSentinel1, xLoop, yLoop, UnitAITypes.UNITAI_ATTACK_CITY_LEMMING, DirectionTypes.NO_DIRECTION)
								
					self.addPopup(localText.getText("TXT_KEY_JAL", ()), localText.getText("TXT_KEY_LEVEL3END7", ()))
			
			if Afterworld.iObjective == 99:
				if iUplinkTimerValue == 3: #70			
					self.addPopup(localText.getText("TXT_KEY_JAL", ()), localText.getText("TXT_KEY_LEVEL3END8", ()))
					
			if Afterworld.iObjective == 99:
				if iUplinkTimerValue == 2: #Interruption/End		
					self.addPopup(localText.getText("TXT_KEY_JAL", ()), localText.getText("TXT_KEY_ENDLEVELTHREE1JAL1", ())) #Security is locking everything down.
					self.addPopup(localText.getText("TXT_KEY_JAL", ()), localText.getText("TXT_KEY_JALENDOB4A", ())) #Barricades up ahead just dropped.  We have to reach the gate and inform Augustine....they can't detonate the star!
					self.addPopup(localText.getText("TXT_KEY_JAL", ()), localText.getText("TXT_KEY_JALENDOB4B", ())) #We can't let them detonate the star!
					self.addPopup(localText.getText("TXT_KEY_SEVER", ()), localText.getText("TXT_KEY_ENDLEVELTHREE1SEVER1", ())) #Sometimes to win the game... 
					self.addPopup(localText.getText("TXT_KEY_JAL", ()), localText.getText("TXT_KEY_ENDLEVELTHREE1JAL2", ())) #Sever!  What are you doing!
					iOB3Barrier = gc.getMap().plot(97, 8)
					pSeverLoc = gc.getMap().plot(98, 6)
					iOB3Barrier.setOwner(0) #Doors to level 4
					iOB3Barrier.setFeatureType(iBOPEN,1)
					for pUnits in unitList:
						if (pUnits.getUnitType()) == iSever:
							pUnits.setXY(98, 6, 0, 0, 0)
							CyGInterfaceScreen("MainInterface", MAIN_INTERFACE).setMinimapSectionOverride(.45, 0, 0.90, 1)
							iOB3Barrier.setFeatureType(iBOPEN,1)
							Afterworld.iObjective = 3
							self.addPopup(localText.getText("TXT_KEY_NEWOBJECTIVE", ()), localText.getText("TXT_KEY_LEVELFOUR_VICTORY_COND", ()))
							self.addPopup(localText.getText("TXT_KEY_SEVER", ()), localText.getText("TXT_KEY_ENDLEVELTHREE1SEVER2", ())) #...gotta sacrifice pawns.
			
		#Objective 4 location part 1
		if Afterworld.iObjective != 3:
			pBarricadeTerminal1Plot.setOwner(1)

		if Afterworld.iObjective == 3:
			pBarricadeTerminal1Plot.setOwner(0)
			screen = CyGInterfaceScreen("MainInterface",CvScreenEnums.MAIN_INTERFACE)
			screen.minimapFlashPlot(103, 6, 2, 999.0)
			
		#Objective 4 location part 2
		if Afterworld.iObjective != 4:
			pBarricadeTerminal2Plot.setOwner(1)
		
		if Afterworld.iObjective == 4:
			pBarricadeTerminal2Plot.setOwner(0)
			screen = CyGInterfaceScreen("MainInterface",CvScreenEnums.MAIN_INTERFACE)
			screen.minimapFlashPlot(114, 3, 2, 999.0)
			
		#Objective 4 location part 3
		if Afterworld.iObjective != 5:
			pBarricadeTerminal3Plot.setOwner(1)
		
		if Afterworld.iObjective == 5:
			pBarricadeTerminal3Plot.setOwner(0)
			screen = CyGInterfaceScreen("MainInterface",CvScreenEnums.MAIN_INTERFACE)
			screen.minimapFlashPlot(131, 3, 2, 999.0)
		
		if Afterworld.iStartReconTimer == 1:
			if iReconTimerValue > 0:
				iReconONELESS = iReconTimerValue -1
				pReconPlot.setScriptData(str(iReconONELESS))			

		if Afterworld.iStartUplinkTimer == 1:
			if iUplinkTimerValue > 0:
				iUplinkONELESS = iUplinkTimerValue -1
				pUplinkPlot.setScriptData(str(iUplinkONELESS))
				
		for pUnit in unitList:
			iX = pUnit.getX()
			iY = pUnit.getY()
			for xLoop in range (iX -2, iX +2):
				for yLoop in range (iY -2, iY +2):
					
					# Skip plot if it's outside of the bounds of the map
					if (xLoop < 0 or yLoop < 0 or xLoop >= CyMap().getGridWidth() or yLoop >= CyMap().getGridHeight()):
						continue
					
					pPlot = gc.getMap().plot(xLoop, yLoop)
					iNumUnits = pPlot.getNumUnits()
					iFeatureType = pPlot.getFeatureType()
#					if not pPlot.isVisible(iTeam, 0) and iNumUnits == 0:
					if iNumUnits == 0:
						if(iFeatureType != iW and iFeatureType != iIW and iFeatureType != iT1 and iFeatureType != iT2 and iFeatureType != iT3 and iFeatureType != iB1 and iFeatureType != iB2 and iFeatureType != iB3):
							iSpawnRand = CyGame().getSorenRandNum(100, "Afterworld")
							if self.iIntroText == 15:
								if Afterworld.iObjective == 0:
									if iSpawnRand < 3:
										gc.getPlayer(2).initUnit(iBleeder, xLoop, yLoop, UnitAITypes.UNITAI_ATTACK_CITY_LEMMING, DirectionTypes.NO_DIRECTION)
								
							if Afterworld.iObjective == 1:
								if iSpawnRand < 6:
									gc.getPlayer(2).initUnit(iBleeder, xLoop, yLoop, UnitAITypes.UNITAI_ATTACK_CITY_LEMMING, DirectionTypes.NO_DIRECTION)
							
							if Afterworld.iObjective == 2:
								if iSpawnRand < 9:
									gc.getPlayer(2).initUnit(iBleeder, xLoop, yLoop, UnitAITypes.UNITAI_ATTACK_CITY_LEMMING, DirectionTypes.NO_DIRECTION)
							
							if Afterworld.iObjective == 3:
								if iSpawnRand < 12:
									gc.getPlayer(2).initUnit(iBleeder, xLoop, yLoop, UnitAITypes.UNITAI_ATTACK_CITY_LEMMING, DirectionTypes.NO_DIRECTION)
							
							if Afterworld.iObjective == 4:
								if iSpawnRand < 14:
									gc.getPlayer(2).initUnit(iBleeder, xLoop, yLoop, UnitAITypes.UNITAI_ATTACK_CITY_LEMMING, DirectionTypes.NO_DIRECTION)
							
							if Afterworld.iObjective == 5:
								if iSpawnRand < 1:
									gc.getPlayer(2).initUnit(iSavageBleeder, xLoop, yLoop, UnitAITypes.UNITAI_ATTACK_CITY_LEMMING, DirectionTypes.NO_DIRECTION)
									gc.getPlayer(1).initUnit(iBleeder, xLoop, yLoop, UnitAITypes.UNITAI_ATTACK_CITY_LEMMING, DirectionTypes.NO_DIRECTION)
		#Timers
		for iUnitDataLoop in range(Afterworld.getNumUnitDatas()):
			
			pUnitData = Afterworld.getUnitDataByIndex(iUnitDataLoop)
			iMDATimerValue = pUnitData.getMDATimer()
			iRepairTimerValue = pUnitData.getRepairTimer()
			iSpawnTimerValue = pUnitData.getSpawnTimer()
			iDetonatorTimerValue = pUnitData.getDetonatorTimer()
			iMAULerTimerValue = pUnitData.getMAULerTimer()
			iSilenceTimerValue = pUnitData.getSilenceTimer()
			iEnhAccTimerValue = pUnitData.getEnhAccTimer()
			iBarrierTimerValue = pUnitData.getBarrierTimer()
			iInhibitorTimerValue = pUnitData.getInhibitorTimer()
			iProjectTimerValue = pUnitData.getProjectTimer()
			iControlTimerValue = pUnitData.getControlTimer()
			iShadowTimerValue = pUnitData.getShadowTimer()
			iInvisibilityTurnsValue = pUnitData.getInvisibilityTurns()
			iGrenadeTimerValue = pUnitData.getGrenadeTimer()


			if iMDATimerValue > 0:
				pUnitData.changeMDATimer(-1)
			if iRepairTimerValue > 0:
				pUnitData.changeRepairTimer(-1) 
			if iSpawnTimerValue > 0:
				pUnitData.changeSpawnTimer(-1) 
			if iSpawnTimerValue > 0:
				pUnitData.changeSpawn2Timer(-1) 				
			if iSpawnTimerValue > 0:
				pUnitData.changeSpawn3Timer(-1) 				
			if iDetonatorTimerValue > 0:
				pUnitData.changeDetonatorTimer(-1) 
			if iMAULerTimerValue > 0:
				pUnitData.changeMAULerTimer(-1) 
			if iSilenceTimerValue > 0:
				pUnitData.changeSilenceTimer(-1) 
			if iEnhAccTimerValue > 0:
				pUnitData.changeEnhAccTimer(-1) 
			if iBarrierTimerValue > 0:
				pUnitData.changeBarrierTimer(-1) 
			if iInhibitorTimerValue > 0:
				pUnitData.changeInhibitorTimer(-1) 
			if iProjectTimerValue > 0:
				pUnitData.changeProjectTimer(-1) 
			if iControlTimerValue > 0:
				pUnitData.changeControlTimer(-1) 
			if iShadowTimerValue > 0:
				pUnitData.changeShadowTimer(-1)
				print "shadow timer"
				print iShadowTimerValue
			if iInvisibilityTurnsValue > 0:
				pUnitData.changeInvisibilityTurns(-1)
			if iGrenadeTimerValue > 0:
				pUnitData.changeGrenadeTimer(-1)				
		
	def onPreSave(self, argsList):
#		print("called before a game is actually saved")
		self.parent.onPreSave(self, argsList)
	
		Afterworld.saveUnitDatasToScriptData()
		Afterworld.saveAfterworldMessages()
		Afterworld.pickleAfterworld()
		
	def onLoadGame(self, argsList):
		self.parent.onLoadGame(self, argsList)
		Afterworld.resetValues()
		Afterworld.loadUnitDatasFromScriptData()
		Afterworld.loadAfterworldMessages()
		Afterworld.unpickleAfterworld()

#################### ON EVENTS ######################
	def getRand(self, iNum):
			return CyGame().getSorenRandNum(iNum, "Afterworld")
		
	def onKbdEvent(self, argsList):
			'keypress handler - return 1 if the event was consumed'
			
			self.parent.onKbdEvent(self, argsList)
			
			eventType,key,mx,my,px,py = argsList
			
			if ( eventType == self.EventKeyDown ):
					theKey=int(key)
					
					keyList = [InputTypes.KB_DELETE, InputTypes.KB_E, InputTypes.KB_F1, InputTypes.KB_F2, InputTypes.KB_F3, InputTypes.KB_F4, InputTypes.KB_F5, InputTypes.KB_F6, InputTypes.KB_F7, InputTypes.KB_F8, InputTypes.KB_F9, InputTypes.KB_F10, InputTypes.KB_F11, InputTypes.KB_F12]
					
					if (theKey in keyList):
						return 1
					
					if (theKey == int(InputTypes.KB_LEFT)):
						if self.bCtrl:
								CyCamera().SetBaseTurn(CyCamera().GetBaseTurn() - 45.0)
								return 1
						elif self.bShift:
								CyCamera().SetBaseTurn(CyCamera().GetBaseTurn() - 10.0)
								return 1
					
					if (theKey == int(InputTypes.KB_RIGHT)):
							if self.bCtrl:
									CyCamera().SetBaseTurn(CyCamera().GetBaseTurn() + 45.0)
									return 1
							elif self.bShift:
									CyCamera().SetBaseTurn(CyCamera().GetBaseTurn() + 10.0)
									return 1
					

					
#					if (theKey == int(InputTypes.KB_Y)):
#						if self.bCtrl:
#							for i in range(gc.getPlayer(0).getNumUnits()): gc.getPlayer(0).getUnit(i).setMoves(0)
#							for i in range(gc.getPlayer(0).getNumUnits()): gc.getPlayer(0).getUnit(i).setDamage(0,0)
#							return 1
#					
#					if (theKey == int(InputTypes.KB_B)):
#						if self.bCtrl:
#							Afterworld.resetValues()
#							Afterworld.loadUnitDatasFromScriptData()
#							CyInterface().addImmediateMessage("Unit Data Loaded","")
#							return 1
##							
#						elif self.bAlt:
#							Afterworld.saveUnitDatasToScriptData()
#							CyInterface().addImmediateMessage("Unit Data Saved","")
#							for i in range(gc.getNumPromotionInfos()):
#								gc.getPlayer(0).getUnit(2).setHasPromotion(i,1)
#								return 1
#			return 0
			
	def onPlotPicked(self, argsList):
		'Plot Picked'
		pPlot = argsList[0]
		iNumUnits = pPlot.getNumUnits()
		pPlotUnit = pPlot.getUnit(0)
		pButtonUnit = Afterworld.pPushedButtonUnit
		pTargetedPlayer = gc.getPlayer(pPlotUnit.getOwner())
		pPlayer = gc.getPlayer(pButtonUnit.getOwner())
		iUnitID = pPlotUnit.getUnitType()
		iUnitX = pButtonUnit.plot().getX()
		iUnitY = pButtonUnit.plot().getY()
		iX = pPlot.getX()
		iY = pPlot.getY()
		iID = pButtonUnit.getID()
		pUnitData = Afterworld.getUnitDataByID(iID)
		iW = CvUtil.findInfoTypeNum(gc.getFeatureInfo,gc.getNumFeatureInfos(),'FEATURE_AFTERWORLD_WALLS')
		iGround = CvUtil.findInfoTypeNum(gc.getFeatureInfo,gc.getNumFeatureInfos(),'FEATURE_AFTERWORLD_GROUND1')
		iT1 = CvUtil.findInfoTypeNum(gc.getFeatureInfo,gc.getNumFeatureInfos(),'FEATURE_AFTERWORLD_TREE')
		iT2 = CvUtil.findInfoTypeNum(gc.getFeatureInfo,gc.getNumFeatureInfos(),'FEATURE_AFTERWORLD_TREE2')
		iT3 = CvUtil.findInfoTypeNum(gc.getFeatureInfo,gc.getNumFeatureInfos(),'FEATURE_AFTERWORLD_TREE3')
		iB1 = CvUtil.findInfoTypeNum(gc.getFeatureInfo,gc.getNumFeatureInfos(),'FEATURE_AFTERWORLD_BARRICADES1')
		iB2 = CvUtil.findInfoTypeNum(gc.getFeatureInfo,gc.getNumFeatureInfos(),'FEATURE_AFTERWORLD_BARRICADES2')
		iIW = CvUtil.findInfoTypeNum(gc.getFeatureInfo,gc.getNumFeatureInfos(),'FEATURE_AFTERWORLD_INTERIOR_WALLS')
		
		iDetonator = CvUtil.findInfoTypeNum(gc.getImprovementInfo,gc.getNumImprovementInfos(),'IMPROVEMENT_LANDMINE')
		iDetonator2 = CvUtil.findInfoTypeNum(gc.getImprovementInfo,gc.getNumImprovementInfos(),'IMPROVEMENT_LANDMINE2')
		iBarrier = CvUtil.findInfoTypeNum(gc.getFeatureInfo,gc.getNumFeatureInfos(),'FEATURE_BARRIER1')
		
		iFeatureType = pPlot.getFeatureType()
		iJal = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_JAL')
		iRagah = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_RAGAH')
		iSever = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_SEVER')
		iInvSever = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_SEVER_INVISIBLE')
		iRiest = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_RIEST')
		iAtticus = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_ATTICUS')
		
		
		iBleeder = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_BLEEDER')
		iRabidBleeder = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_RABID_BLEEDER')
		iSavageBleeder = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_SAVAGE_BLEEDER')
		iControlledBleeder = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_CONTROLLED_BLEEDER')
		iSentinel1 = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_SENTINEL1')
		iSentinel2 = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_SENTINEL2')
		iSentinel3 = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_SENTINEL3')
		iFeral = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_FERAL')
		iFeral2 = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_FERAL2')
		iFeral3 = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_FERAL3')
		iEntity = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_ENTITY')
		iControlledRabid = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_CONTROLLED_RABID')
		
		if plotDistance(iUnitX,iUnitY, iX, iY) <= 3:
			#Detonator 3
			if Afterworld.pPushButton == 12:
				if (not pPlotUnit.isHuman()):
					pUnitData.setGrenadeTimer(4)
					for xLoop in range (iX -1, iX +1):
						for yLoop in range (iY -1, iY +1):
							pBLOWDUP = gc.getMap().plot(xLoop, yLoop)
							pToast = pBLOWDUP.getUnit(0)
							if pToast.getOwner() != 0:
								pToast.changeDamage(90, 0)
								effectType = gc.getInfoTypeForString('EFFECT_INVASIONSHIP_LARGE_HIT')
								CyEngine().triggerEffect(effectType, pBLOWDUP.getPoint())
								if (xLoop < 0 or yLoop < 0 or xLoop >= CyMap().getGridWidth() or yLoop >= CyMap().getGridHeight()):
									continue
								iFeatureType = pBLOWDUP.getFeatureType()
								if(iFeatureType == iW or iFeatureType == iT1 or iFeatureType == iT2 or iFeatureType == iT3):
									pBLOWDUP.setFeatureType(iGround,1)
								

			if Afterworld.pPushButton == 8:
				print "button was 8"
				if (not pPlotUnit.isHuman()):
					print "not human"
					#MAULer 3
					if pButtonUnit.isHasPromotion(gc.getInfoTypeForString('PROMOTION_MAULER3')):
						print "MAUL3 promotion"
						Afterworld.MAUL = 3
						print "Maul = 3"
						pUnitData.setMAULerTimer(4)
						print "set maultimer"
						for xLoop in range (iX -1, iX +1):
							for yLoop in range (iY -1, iY +1):
								pBLOWDUP = gc.getMap().plot(xLoop, yLoop)
								pToast = pBLOWDUP.getUnit(0)
								if pToast.getOwner() != 0:
									pToast.changeDamage(90, 0)
									CyEngine().triggerEffect(4, pPlot.getPoint())
									iFeatureType = pBLOWDUP.getFeatureType()
									if (xLoop < 0 or yLoop < 0 or xLoop >= CyMap().getGridWidth() or yLoop >= CyMap().getGridHeight()):
										continue
									if(iFeatureType == iW or iFeatureType == iT1 or iFeatureType == iT2 or iFeatureType == iT3):
										pBLOWDUP.setFeatureType(iGround,1)
									
				#MAULer 2
					elif pButtonUnit.isHasPromotion(gc.getInfoTypeForString('PROMOTION_MAULER2')):
						Afterworld.MAUL = 2
						
						CyEngine().triggerEffect(4, pPlot.getPoint())
						pPlotUnit.changeDamage(65, 0)
						pUnitData.setMAULerTimer(4)
						if(iFeatureType == iW):
							pPlot.setFeatureType(iGround,1)
						if (iFeatureType == iT1 or iFeatureType == iT2 or iFeatureType == iT3):
							pPlot.setFeatureType(iGround,1)
				#MAULer 1
					elif pButtonUnit.isHasPromotion(gc.getInfoTypeForString('PROMOTION_MAULER1')):
						CyEngine().triggerEffect(4, pPlot.getPoint())
						pPlotUnit.changeDamage(50, 0)
						pUnitData.setMAULerTimer(4)
						CyEngine().triggerEffect(4, pPlot.getPoint())

	########Effects which require a unit
			elif iNumUnits >= 1:
				if plotDistance(pButtonUnit.plot().getX(),pButtonUnit.plot().getY(), pPlotUnit.plot().getX(), pPlotUnit.plot().getY()) > 3:
					return
				
				#Inhibitor
				if Afterworld.pPushButton == 3:
					if (not pPlotUnit.isHuman()):
						if iUnitID == iBleeder or iUnitID == iSentinel1 or iUnitID == iSentinel2 or iUnitID == iSentinel3 or iUnitID == iSavageBleeder or iUnitID == iRabidBleeder or iUnitID == iFeral:
							effectType = gc.getInfoTypeForString('EFFECT_IMPACT_FLASH')
							CyEngine().triggerEffect(effectType, pPlot.getPoint())
							pPlotUnit.setImmobileTimer(2)
							pUnitData.setInhibitorTimer(4)
				# Control Effect
				elif Afterworld.pPushButton == 1:
					if (not pPlotUnit.isHuman()):
						if iUnitID == iBleeder:
							CyEngine().triggerEffect(8, pPlot.getPoint())
							pPlotUnit.kill(true, -1)
							gc.getPlayer(0).initUnit(iControlledBleeder, pPlot.getX(), pPlot.getY(), UnitAITypes.UNITAI_ATTACK_CITY_LEMMING, DirectionTypes.NO_DIRECTION)
							pUnitData.setControlTimer(10)
						
						if iUnitID == iRabidBleeder:
							CyEngine().triggerEffect(8, pPlot.getPoint())
							pPlotUnit.kill(true, -1)
							gc.getPlayer(0).initUnit(iControlledRabid, pPlot.getX(), pPlot.getY(), UnitAITypes.UNITAI_ATTACK_CITY_LEMMING, DirectionTypes.NO_DIRECTION)
							pUnitData.setControlTimer(10)
						
				#Enhance Acceleration
				elif Afterworld.pPushButton == 5:
					effectType = gc.getInfoTypeForString('EFFECT_GREATPEOPLE_ACTIVE_ENGINEER')
					CyEngine().triggerEffect(effectType, pPlot.getPoint())
					pPlotUnit.setMoves(0)
					pUnitData.setEnhAccTimer(4)
				#Silence
				elif Afterworld.pPushButton == 7:
					if (not pPlotUnit.isHuman()):
						if iUnitID == iBleeder or iUnitID == iSentinel1 or iUnitID == iSentinel2 or iUnitID == iSentinel3 or iUnitID == iSavageBleeder or iUnitID == iRabidBleeder or iUnitID == iFeral3 or iUnitID == iFeral2:
							effectType = gc.getInfoTypeForString('EFFECT_WEAPON_CARRIER_BLAST')
							CyEngine().triggerEffect(effectType, pPlot.getPoint())
							pPlotUnit.kill(true, -1)
							pUnitData.setSilenceTimer(10)
				#Repair
				elif Afterworld.pPushButton == 11:
					print "Button 11 is pushed"
					effectType = gc.getInfoTypeForString('EFFECT_HEALSPARKLE')
					CyEngine().triggerEffect(effectType, pPlot.getPoint())
					pPlotUnit.changeDamage(-100, 0)
					pUnitData.setRepairTimer(10)
				#Effects on plots without a unit
				
				
			elif iNumUnits == 0:
				if(iFeatureType == iW or iFeatureType == iT1 or iFeatureType == iT2 or iFeatureType == iT3):
					return
				#Project
				elif Afterworld.pPushButton == 2:
					effectType = gc.getInfoTypeForString('EFFECT_CREATION_BIG_FAST')
					CyEngine().triggerEffect(effectType, pPlot.getPoint())
					pButtonUnit.setXY(iX, iY, 0, 0, 0)
					pUnitData.setProjectTimer(4)
				#Barrier
				elif Afterworld.pPushButton == 4:
					pPlot.setFeatureType(iBarrier, 1)
					pUnitData.setBarrierTimer(10)
				#Field Detonator
				elif Afterworld.pPushButton == 9:
					if pButtonUnit.isHasPromotion(gc.getInfoTypeForString('PROMOTION_DETONATOR2')):
						pPlot.setImprovementType(iDetonator2)
						pUnitData.setDetonatorTimer(4)
					elif pButtonUnit.isHasPromotion(gc.getInfoTypeForString('PROMOTION_DETONATOR1')):
						pPlot.setImprovementType(iDetonator)
						pUnitData.setDetonatorTimer(4)
				# Spawn Sentinel
				elif Afterworld.pPushButton == 15:
					effectType = gc.getInfoTypeForString('EFFECT_CREATION_BIG_FAST')
					CyEngine().triggerEffect(effectType, pPlot.getPoint())
					pPlayer.initUnit(iSentinel3, iX, iY, UnitAITypes.UNITAI_ATTACK_CITY_LEMMING, DirectionTypes.NO_DIRECTION)
					pUnitData.setSpawn3Timer(10)
						
				elif Afterworld.pPushButton == 14:
					effectType = gc.getInfoTypeForString('EFFECT_CREATION_BIG_FAST')
					CyEngine().triggerEffect(effectType, pPlot.getPoint())
					pPlayer.initUnit(iSentinel2, iX, iY, UnitAITypes.UNITAI_ATTACK_CITY_LEMMING, DirectionTypes.NO_DIRECTION)
					pUnitData.setSpawn2Timer(10)
						
				elif Afterworld.pPushButton == 10:
					print "pushed 10"
					effectType = gc.getInfoTypeForString('EFFECT_CREATION_BIG_FAST')
					CyEngine().triggerEffect(effectType, pPlot.getPoint())
					pPlayer.initUnit(iSentinel1, iX, iY, UnitAITypes.UNITAI_ATTACK_CITY_LEMMING, DirectionTypes.NO_DIRECTION)
					pUnitData.setSpawnTimer(10)
					
	def onUnitMove(self, argsList):
			pPlot=argsList[0]
			pUnit=argsList[1]
			iX = pPlot.getX()
			iY = pPlot.getY()
			iUnitType = pUnit.getUnitType()
			iOwner = pUnit.getOwner()
			pPlayer = gc.getPlayer(iOwner)
			iTeam = pPlayer.getTeam()
			iHumanTeam = gc.getPlayer(0).getTeam()
			iFeral = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_FERAL')
			iFeral2 = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_FERAL2')
			iFeral3 = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_FERAL3')
			iBleeder = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_BLEEDER')
			iRagah = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_RAGAH')
			iRiest = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_RIEST')
			
			iJal = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_JAL')
			iAtticus= CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_ATTICUS')
			iSever = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_SEVER')
			iShadow = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_SEVER_INVISIBLE')
			
			pUnitData = Afterworld.getUnitDataByID(pUnit.getID())
			pReconPlot = self.getReconPlot()
			iReconTimerValue = int(pReconPlot.getScriptData())
			
			pUplinkPlot = self.getUplinkPlot()
			iUplinkTimerValue = int(pUplinkPlot.getScriptData())
			
			iImprovementIDRecon = CvUtil.findInfoTypeNum(gc.getImprovementInfo,gc.getNumImprovementInfos(),'IMPROVEMENT_RECON')
			
			iFeatureType = pPlot.getFeatureType()
			iBCLOSED = CvUtil.findInfoTypeNum(gc.getFeatureInfo,gc.getNumFeatureInfos(),'FEATURE_AFTERWORLD_BARRICADES1')
			iBOPEN = CvUtil.findInfoTypeNum(gc.getFeatureInfo,gc.getNumFeatureInfos(),'FEATURE_AFTERWORLD_BARRICADES2')
			iW = CvUtil.findInfoTypeNum(gc.getFeatureInfo,gc.getNumFeatureInfos(),'FEATURE_AFTERWORLD_WALLS')
			iBW = CvUtil.findInfoTypeNum(gc.getFeatureInfo,gc.getNumFeatureInfos(),'FEATURE_AFTERWORLD_BROKEN_WALLS')
			iGround = CvUtil.findInfoTypeNum(gc.getFeatureInfo,gc.getNumFeatureInfos(),'FEATURE_AFTERWORLD_GROUND1')
			iT1 = CvUtil.findInfoTypeNum(gc.getFeatureInfo,gc.getNumFeatureInfos(),'FEATURE_AFTERWORLD_TREE')
			iT2 = CvUtil.findInfoTypeNum(gc.getFeatureInfo,gc.getNumFeatureInfos(),'FEATURE_AFTERWORLD_TREE2')
			iT3 = CvUtil.findInfoTypeNum(gc.getFeatureInfo,gc.getNumFeatureInfos(),'FEATURE_AFTERWORLD_TREE3')
			
			iImprovementIDTerminal = CvUtil.findInfoTypeNum(gc.getImprovementInfo,gc.getNumImprovementInfos(),'IMPROVEMENT_TERMINAL')
			
			iImprovementMine = CvUtil.findInfoTypeNum(gc.getImprovementInfo,gc.getNumImprovementInfos(),'IMPROVEMENT_LANDMINE')
			iImprovementMine2 = CvUtil.findInfoTypeNum(gc.getImprovementInfo,gc.getNumImprovementInfos(),'IMPROVEMENT_LANDMINE2')
			iImprovementMachinery = CvUtil.findInfoTypeNum(gc.getImprovementInfo,gc.getNumImprovementInfos(),'IMPROVEMENT_MACHINERY1')
			iImprovementMachinery2 = CvUtil.findInfoTypeNum(gc.getImprovementInfo,gc.getNumImprovementInfos(),'IMPROVEMENT_MACHINERY2')
			iImprovementMachinery3 = CvUtil.findInfoTypeNum(gc.getImprovementInfo,gc.getNumImprovementInfos(),'IMPROVEMENT_MACHINERY3')
			iBeaconDropoff= CvUtil.findInfoTypeNum(gc.getImprovementInfo,gc.getNumImprovementInfos(),'IMPROVEMENT_DROPOFFBEACON')
			iEmptyConsole = CvUtil.findInfoTypeNum(gc.getImprovementInfo,gc.getNumImprovementInfos(),'IMPROVEMENT_EMPTYCONSOLE')
			iDeceptionPickup = CvUtil.findInfoTypeNum(gc.getImprovementInfo,gc.getNumImprovementInfos(),'IMPROVEMENT_BEACONPICKUP')
			pSever_SecurityConsole = CvUtil.findInfoTypeNum(gc.getImprovementInfo,gc.getNumImprovementInfos(),'IMPROVEMENT_SEVERTERMINAL')
			pAtticus_SecurityConsole = CvUtil.findInfoTypeNum(gc.getImprovementInfo,gc.getNumImprovementInfos(),'IMPROVEMENT_ATTICUSTERMINAL')

			pTerminalPlot = gc.getMap().plot(91, 7)
			pAtticusSecurity = gc.getMap().plot(86, 10)
			pSeverSecurity = gc.getMap().plot(96, 7)
			
			if Afterworld.pAngryEntity == 3:
				unitEntityChowList = PyPlayer(0).getUnitList()
				iRandomChow3 = CyGame().getSorenRandNum(len(unitEntityChowList), "Afterworld")
				pRandomDamagedUnit = unitEntityChowList[iRandomChow3]
				pPlot = pRandomDamagedUnit.plot()
				CyEngine().triggerEffect(EntityBlast2, pPlot.getPoint())
				pRandomDamagedUnit.changeDamage(40, 0)
				
				iRandomChow3B = CyGame().getSorenRandNum(len(unitEntityChowList), "Afterworld")
				pRandomDamagedUnit = unitEntityChowList[iRandomChow3B]
				pOldPlot = pRandomDamagedUnit.plot()
				iX = pRandomDamagedUnit.getX()
				iY = pRandomDamagedUnit.getY()
				
				CyEngine().triggerEffect(TeleportType, pOldPlot.getPoint())
				pRandomDamagedUnit.setImmobileTimer(1)
				iTeleportChance = CyGame().getSorenRandNum(100, "Afterworld")
				if iTeleportChance < 30:
					iTeleportRand = CyGame().getSorenRandNum(8, "Afterworld")
					if iTeleportRand == 0:
						pRandomDamagedUnit.setXY(158,9, 0, 0, 0)
					elif iTeleportRand == 1:
						pRandomDamagedUnit.setXY(138,19, 0, 0, 0)
					elif iTeleportRand == 2:
						pRandomDamagedUnit.setXY(143,0, 0, 0, 0)
					elif iTeleportRand == 3:
						pRandomDamagedUnit.setXY(149,18, 0, 0, 0)
					elif iTeleportRand == 4:
						pRandomDamagedUnit.setXY(156,16, 0, 0, 0)
					elif iTeleportRand == 5:
						pRandomDamagedUnit.setXY(158,7, 0, 0, 0)
					elif iTeleportRand == 6:
						pRandomDamagedUnit.setXY(153,0, 0, 0, 0)
					elif iTeleportRand == 7:
						pRandomDamagedUnit.setXY(152,19, 0, 0, 0)
						
			if Afterworld.pAngryEntity == 4:
				unitEntityChowList = PyPlayer(0).getUnitList()
				iRandomChow3B = CyGame().getSorenRandNum(len(unitEntityChowList), "Afterworld")
				pRandomDamagedUnit = unitEntityChowList[iRandomChow3B]
				pOldPlot = pRandomDamagedUnit.plot()
				iX = pRandomDamagedUnit.getX()
				iY = pRandomDamagedUnit.getY()
				print pOldPlot
				print "that was the plot"
				
				CyEngine().triggerEffect(TeleportType, pOldPlot.getPoint())
				pRandomDamagedUnit.setImmobileTimer(1)
				print "need sleep"
				print pRandomDamagedUnit
				iTeleportChance = CyGame().getSorenRandNum(100, "Afterworld")
				if iTeleportChance < 30:
					print "tired"
					print iTeleportChance
					iTeleportRand = CyGame().getSorenRandNum(8, "Afterworld")
					print "Teleport Rand was"
					print iTeleportRand
					if iTeleportRand == 0:
						pRandomDamagedUnit.setXY(158,9, 0, 0, 0)
					elif iTeleportRand == 1:
						pRandomDamagedUnit.setXY(138,19, 0, 0, 0)
					elif iTeleportRand == 2:
						pRandomDamagedUnit.setXY(143,0, 0, 0, 0)
					elif iTeleportRand == 3:
						pRandomDamagedUnit.setXY(149,18, 0, 0, 0)
					elif iTeleportRand == 4:
						pRandomDamagedUnit.setXY(156,16, 0, 0, 0)
					elif iTeleportRand == 5:
						pRandomDamagedUnit.setXY(158,7, 0, 0, 0)
					elif iTeleportRand == 6:
						pRandomDamagedUnit.setXY(153,0, 0, 0, 0)
					elif iTeleportRand == 7:
						pRandomDamagedUnit.setXY(152,19, 0, 0, 0)
				
				for pRandomUnit in unitEntityChowList:
					pRandomChow = CyGame().getSorenRandNum(4, "Afterworld")
					print "pRandomChow"
					print pRandomChow
					if (pRandomChow == 0):
						pRandomUnit.getUnitType() == iJal
						pPlot = pRandomUnit.plot()
						CyEngine().triggerEffect(EntityBlast2, pPlot.getPoint())
						pRandomUnit.changeDamage(25, 0)
						print "Jal got hit"
					if (pRandomChow == 1):
						pRandomUnit.getUnitType() == iRiest
						pPlot = pRandomUnit.plot()
						pRandomUnit.changeDamage(25, 0)
						print "Riest got hit"
					if (pRandomChow == 2):
						pRandomUnit.getUnitType() == iAtticus
						pPlot = pRandomUnit.plot()
						pRandomUnit.changeDamage(25, 0)
						print "Atticus got hit"
					if (pRandomChow == 3):
						pRandomUnit.getUnitType() == iUnitIDRagah
						pPlot = pRandomUnit.plot()
						pRandomUnit.changeDamage(25, 0)
						print "Ragah got hit"
			
			if (pPlayer.isHuman()):
				if iUnitType == iRagah or iUnitType == iRiest or iUnitType == iJal or iUnitType == iSever or iUnitType == iAtticus or iUnitType == iShadow:
					if (pPlot.getImprovementType() == iImprovementMachinery):
						pUnit.changeExperience(2,Afterworld.pPushedButtonUnit.experienceNeeded()+50,0,0,0)
						pPlot.setImprovementType(-1)
						pPlot.setImprovementType(iEmptyConsole)
						CyEngine().triggerEffect(gc.getInfoTypeForString("EFFECT_CREATION_BIG_FAST"), pPlot.getPoint())
						if  Afterworld.iTutorialMechanism == 0:
							self.addPopup(localText.getText("TXT_KEY_TUTORIALTITLE", ()), localText.getText("TXT_KEY_TUTORIALCONSOLE1", ()))
							self.addPopup(localText.getText("TXT_KEY_TUTORIALTITLE", ()), localText.getText("TXT_KEY_TUTORIALCONSOLE2", ()))
							self.addPopup(localText.getText("TXT_KEY_TUTORIALTITLE", ()), localText.getText("TXT_KEY_TUTORIALCONSOLE3", ()))
							Afterworld.iTutorialMechanism = 1
						
					if (pPlot.getImprovementType() == iImprovementMachinery2):  #Repair Mechanism
						pUnitData.changeNumRepairMechanism(1)
						pPlot.setImprovementType(-1)
						pPlot.setImprovementType(iEmptyConsole)
						CyEngine().triggerEffect(gc.getInfoTypeForString("EFFECT_CREATION_BIG_FAST"), pPlot.getPoint())
						if Afterworld.iTutorialMechanism == 0:
							self.addPopup(localText.getText("TXT_KEY_TUTORIALTITLE", ()), localText.getText("TXT_KEY_TUTORIALCONSOLE1", ()))
							self.addPopup(localText.getText("TXT_KEY_TUTORIALTITLE", ()), localText.getText("TXT_KEY_TUTORIALCONSOLE2", ()))
							self.addPopup(localText.getText("TXT_KEY_TUTORIALTITLE", ()), localText.getText("TXT_KEY_TUTORIALCONSOLE3", ()))
							Afterworld.iTutorialMechanism = 1
						
					if (pPlot.getImprovementType() == iImprovementMachinery3):  #Acceleration Mechanism
						pUnitData.changeNumAccelerationMechanism(1)
						pPlot.setImprovementType(-1)
						pPlot.setImprovementType(iEmptyConsole)
						CyEngine().triggerEffect(gc.getInfoTypeForString("EFFECT_CREATION_BIG_FAST"), pPlot.getPoint())
						if Afterworld.iTutorialMechanism == 0:
							self.addPopup(localText.getText("TXT_KEY_TUTORIALTITLE", ()), localText.getText("TXT_KEY_TUTORIALCONSOLE1", ()))
							self.addPopup(localText.getText("TXT_KEY_TUTORIALTITLE", ()), localText.getText("TXT_KEY_TUTORIALCONSOLE2", ()))
							self.addPopup(localText.getText("TXT_KEY_TUTORIALTITLE", ()), localText.getText("TXT_KEY_TUTORIALCONSOLE3", ()))
							Afterworld.iTutorialMechanism = 1
					
#Objective I - Recon
				if (pPlot.getImprovementType() == iImprovementIDRecon):
					if(iUnitType == iJal):
						if Afterworld.iStartReconTimer == 0:
							pReconPlot.setScriptData("10")
							self.addPopup(localText.getText("TXT_KEY_JAL", ()), localText.getText("TXT_KEY_RECONSTART", ()))
							Afterworld.iStartReconTimer = 1
#				if (iX == 37 and iY == 5) or (iX == 38 and iY == 6) or (iX == 39 and iY == 5) or (iX == 38 and iY == 4):
				if Afterworld.iStartReconTimer == 1:
					if Afterworld.iObjective == 0:
						if(iUnitType == iJal):
							if (pPlot.getImprovementType() != iImprovementIDRecon):
								pReconPlot.setScriptData("10")
								self.addPopup(localText.getText("TXT_KEY_JAL", ()), localText.getText("TXT_KEY_RESET", ()))
								Afterworld.iStartReconTimer = 0

#Objective II - Strategy
				if (iX == 43 and iY == 10) or (iX == 43 and iY == 11):
					if Afterworld.iChatMessages == 0:
						Afterworld.addAfterworldMessage( localText.getText("TXT_KEY_ATTICUS", ()), localText.getText("TXT_KEY_CS_2_1_1", ()))
						Afterworld.addAfterworldMessage( localText.getText("TXT_KEY_RIEST", ()), localText.getText("TXT_KEY_CS_2_1_2", ()))
						Afterworld.addAfterworldMessage( localText.getText("TXT_KEY_ATTICUS", ()), localText.getText("TXT_KEY_CS_2_1_3", ()))
						Afterworld.addAfterworldMessage( localText.getText("TXT_KEY_RIEST", ()), localText.getText("TXT_KEY_CS_2_1_4", ()))
						Afterworld.addAfterworldMessage( localText.getText("TXT_KEY_RIEST", ()), localText.getText("TXT_KEY_CS_2_1_5", ()))
						Afterworld.addAfterworldMessage( localText.getText("TXT_KEY_RIEST", ()), localText.getText("TXT_KEY_CS_2_1_6", ()))
						Afterworld.addAfterworldMessage( localText.getText("TXT_KEY_ATTICUS", ()), localText.getText("TXT_KEY_CS_2_1_7", ()))
						Afterworld.addAfterworldMessage( localText.getText("TXT_KEY_ATTICUS", ()), localText.getText("TXT_KEY_CS_2_1_8", ()))
						Afterworld.iChatMessages =1
				if Afterworld.pSpawnFeralTile == 0: #Spawn the Feral
					if (iX == 64 and iY == 12) or (iX == 64 and iY == 13) or (iX == 64 and iY == 14) or (iX == 64 and iY == 15) or (iX == 64 and iY == 16) or (iX == 64 and iY == 17):
						pFeralPlot = gc.getMap().plot(68, 8)
						self.doCameraZoomPlot(pFeralPlot)
						pFeralPlot.setOwner(0)
						gc.getPlayer(2).initUnit(iFeral, 68, 8, UnitAITypes.UNITAI_ATTACK_CITY_LEMMING, DirectionTypes.NO_DIRECTION)
						Afterworld.pSpawnFeralTile = 1
				
				if (pPlot.getImprovementType() == iDeceptionPickup): #Grab the Beacon
					pUnitData.changeNumDeceptionBeacon(1)
					pPlot.setImprovementType(-1)
					iOBJII_1stBarrier = gc.getMap().plot(72, 6)
					iOBJII_2ndBarrier = gc.getMap().plot(70, 6)
					pBeaconTerminal = gc.getMap().plot(85, 1) #Show the Beacon Terminal
					Afterworld.iObjective = 2
					CyGInterfaceScreen("MainInterface", MAIN_INTERFACE).setMinimapSectionOverride(.30, 0, 0.75, 1)
					pBeaconTerminal.setOwner(0)
					iOBJII_1stBarrier.setFeatureType(iBOPEN,1)
					iOBJII_2ndBarrier.setFeatureType(iBOPEN,1)
					self.addPopup(localText.getText("TXT_KEY_NEWOBJECTIVE", ()), localText.getText("TXT_KEY_OBJECTIVE3A", ()))
					
				if (iX == 72 and iY == 6) or (iX == 70 and iY == 6):
					if Afterworld.iChatMessages == 1:
						Afterworld.addAfterworldMessage( localText.getText("TXT_KEY_ATTICUS", ()), localText.getText("TXT_KEY_CS_2_2_1", ()))
						Afterworld.addAfterworldMessage( localText.getText("TXT_KEY_RIEST", ()), localText.getText("TXT_KEY_CS_2_2_2", ()))
						Afterworld.addAfterworldMessage( localText.getText("TXT_KEY_ATTICUS", ()), localText.getText("TXT_KEY_CS_2_2_3", ()))
						Afterworld.addAfterworldMessage( localText.getText("TXT_KEY_ATTICUS", ()), localText.getText("TXT_KEY_CS_2_2_4", ()))
						Afterworld.addAfterworldMessage( localText.getText("TXT_KEY_ATTICUS", ()), localText.getText("TXT_KEY_CS_2_2_5", ()))
						Afterworld.addAfterworldMessage( localText.getText("TXT_KEY_ATTICUS", ()), localText.getText("TXT_KEY_CS_2_2_6", ()))
						Afterworld.addAfterworldMessage( localText.getText("TXT_KEY_ATTICUS", ()), localText.getText("TXT_KEY_CS_2_2_7", ()))
						Afterworld.addAfterworldMessage( localText.getText("TXT_KEY_ATTICUS", ()), localText.getText("TXT_KEY_CS_2_2_8", ()))
						Afterworld.addAfterworldMessage( localText.getText("TXT_KEY_ATTICUS", ()), localText.getText("TXT_KEY_CS_2_2_9", ()))
						Afterworld.addAfterworldMessage( localText.getText("TXT_KEY_RAGAH", ()), localText.getText("TXT_KEY_CS_2_2_10", ()))
						Afterworld.addAfterworldMessage( localText.getText("TXT_KEY_ATTICUS", ()), localText.getText("TXT_KEY_CS_2_2_11", ()))
						Afterworld.addAfterworldMessage( localText.getText("TXT_KEY_SEVER", ()), localText.getText("TXT_KEY_CS_2_2_12", ()))
						Afterworld.iChatMessages =2

#OBJECTIVE III - Deception
				if (pPlot.getImprovementType() == iBeaconDropoff):
					if pUnitData.getNumDeceptionBeacon() == 1:
						self.addPopup(localText.getText("TXT_KEY_JAL", ()), localText.getText("TXT_KEY_LEVEL3UPLINKSPEECH1", ()))
						self.addPopup(localText.getText("TXT_KEY_JAL", ()), localText.getText("TXT_KEY_LEVEL3UPLINKSPEECH2", ()))
						self.addPopup(localText.getText("TXT_KEY_JAL", ()), localText.getText("TXT_KEY_LEVEL3UPLINKSPEECH3", ()))
						self.addPopup(localText.getText("TXT_KEY_JAL", ()), localText.getText("TXT_KEY_LEVEL3UPLINKSPEECH4", ()))
						pAtticusSecurity.setOwner(0)
						pSeverSecurity.setOwner(0)
						pTerminalPlot.setOwner(0)
						Afterworld.iObjective = 9
				
				if (pPlot.getImprovementType() == pSever_SecurityConsole and iUnitType == iSever):
					if Afterworld.iUplinkSever == 0:
						self.addPopup(localText.getText("TXT_KEY_SEVER", ()), localText.getText("TXT_KEY_READY", ()))
						Afterworld.iUplinkSever = 1
					
				if (pPlot.getImprovementType() == pAtticus_SecurityConsole and iUnitType == iAtticus):
					if Afterworld.iUplinkAtticus == 0:
						self.addPopup(localText.getText("TXT_KEY_ATTICUS", ()), localText.getText("TXT_KEY_SECURITYOVERRIDE", ()))
						Afterworld.iUplinkAtticus = 1
					
				if (pPlot.getImprovementType() == iImprovementIDTerminal and iUnitType == iJal):
					if Afterworld.iUplinkJal == 0:
						self.addPopup(localText.getText("TXT_KEY_JAL", ()), localText.getText("TXT_KEY_READY", ()))
						Afterworld.iUplinkJal = 1
#
#				if Afterworld.iStartUplinkTimer == 1:
#					if Afterworld.iObjective == 99:
#						if(iUnitType == iJal):
#							if iX != 91 and iY != 7:
#								pUplinkPlot.setScriptData("10")
#								self.addPopup(localText.getText("TXT_KEY_JAL", ()), localText.getText("TXT_KEY_RESET", ()))

				if Afterworld.iObjective == 99:
					print "Jal moved"
					print Afterworld.iObjective
					if Afterworld.iStartUplinkTimer == 1:
						if iUnitType ==  iJal:
							if iX != 91 and iY != 7:
								pUplinkPlot.setScriptData("10")
								self.addPopup(localText.getText("TXT_KEY_JAL", ()), localText.getText("TXT_KEY_RESET", ()))

				if Afterworld.iObjective == 99:
					print "Atticus moved"
					print Afterworld.iObjective
					if Afterworld.iStartUplinkTimer == 1:
						print "StartUplink is"
						print Afterworld.iStartUplinkTimer
						if iUnitType ==  iAtticus:
							if iX != 86 and iY != 10:
								pUplinkPlot.setScriptData("10")
								self.addPopup(localText.getText("TXT_KEY_JAL", ()), localText.getText("TXT_KEY_RESET", ()))
				
				if Afterworld.iObjective == 99:
					if Afterworld.iStartUplinkTimer == 1:
						if iUnitType ==  iSever:
							if iX != 96 and iY != 7:
								pUplinkPlot.setScriptData("10")
								self.addPopup(localText.getText("TXT_KEY_JAL", ()), localText.getText("TXT_KEY_RESET", ()))

#OBJECTIVE IV - Sacrifice
				if Afterworld.pBarrier1 == 0:
					if iX == 103 and iY == 6:
						i1stDoor = gc.getMap().plot(102, 8)
						i1stDoor.setOwner(0)
						i1stDoor.setFeatureType(iBOPEN,1)
						
						iBarrier2 = gc.getMap().plot(114, 3)
						iBarrier2.setOwner(0)
						self.doCameraZoomPlot(iBarrier2)
						CyGInterfaceScreen("MainInterface", MAIN_INTERFACE).setMinimapSectionOverride(.55, 0, 1, 1)
						Afterworld.pBarrier1 = 1
						Afterworld.iObjective = 4
						
				if Afterworld.pBarrier2 == 0:
					if iX == 114 and iY == 3:
						i2nddoor= gc.getMap().plot(114, 18)
						i2nddoor.setOwner(0)
						i2nddoor.setFeatureType(iBOPEN,1)
						
						iLastBarrier = gc.getMap().plot(131, 3)
						iLastBarrier.setOwner(0)
						self.doCameraZoomPlot(iLastBarrier)
						Afterworld.pBarrier2 = 1
						Afterworld.iObjective = 4
				
				if Afterworld.pBarrier3 == 0:
					if iX == 131 and iY == 3:
						iLastDoor1 = gc.getMap().plot(130, 15)
						iLastDoor2 = gc.getMap().plot(130, 16)
						
						iLastDoor1.setFeatureType(iBOPEN,1)
						iLastDoor2.setFeatureType(iBOPEN,1)
						iLastDoor1.setOwner(0)
						iLastDoor2.setOwner(0)
						
						Afterworld.pBarrier3 = 1
						Afterworld.iObjective = 5
						Afterworld.addAfterworldMessage( localText.getText("TXT_KEY_JAL", ()), localText.getText("TXT_KEY_JAL_DISTRACTION1", ()))
						Afterworld.addAfterworldMessage( localText.getText("TXT_KEY_SEVER", ()), localText.getText("TXT_KEY_SEVER_DISTRACTION1", ()))
						Afterworld.addAfterworldMessage( localText.getText("TXT_KEY_SEVER", ()), localText.getText("TXT_KEY_SEVER_DISTRACTION2", ()))
						Afterworld.addAfterworldMessage( localText.getText("TXT_KEY_SEVER", ()), localText.getText("TXT_KEY_SEVER_DISTRACTION3", ()))
						Afterworld.addAfterworldMessage( localText.getText("TXT_KEY_SEVER", ()), localText.getText("TXT_KEY_SEVER_DISTRACTION4", ()))
						unitSeverList = PyPlayer(0).getUnitList()
						bSeverEnd = false
						bShadowEnd = false
						for pSeverShadowWalks in unitSeverList:
							if pSeverShadowWalks.getUnitType() == iSever:
								pSeverShadowWalks.kill(true, -1)
								bSeverEnd = true
							if pSeverShadowWalks.getUnitType() == iShadow:
								pSeverShadowWalks.kill(true, -1)
								bShadowEnd = true
							if bShadowEnd and bSeverEnd:
								pSeverShadowWalks.kill(true, -1)
								self.iSeverTurn = CyGame().getGameTurn()
								Afterworld.iSacrificeSever = 1
				
			if (not pPlayer.isHuman()):
				if(iUnitType != iFeral and iUnitType != iFeral2 and iUnitType != iFeral3):
					
	#Barrier I
					iImprovementBarrier = CvUtil.findInfoTypeNum(gc.getImprovementInfo,gc.getNumImprovementInfos(),'IMPROVEMENT_BARRIER1')
					
					if (pPlot.getImprovementType() == iImprovementBarrier):
						pUnit.changeDamage(50, 0)
						pPlot.setImprovementType(-1)
						
	#Barrier II
					iImprovementBarrier2 = CvUtil.findInfoTypeNum(gc.getImprovementInfo,gc.getNumImprovementInfos(),'IMPROVEMENT_BARRIER2')
					
					if (pPlot.getImprovementType() == iImprovementBarrier2):
						pUnit.changeDamage(50, 0)
						
	#Barrier III
					iImprovementBarrier3 = CvUtil.findInfoTypeNum(gc.getImprovementInfo,gc.getNumImprovementInfos(),'IMPROVEMENT_BARRIER3')
					
					if (pPlot.getImprovementType() == iImprovementBarrier3):
						pUnit.changeDamage(50, 0)
						iUnitMove = pUnit.baseMoves * 60
						pUnit.setMoves(iUnitMove)
						
	#Detonator I
				if (pPlot.getImprovementType() == iImprovementMine):
					pPlot.setImprovementType(-1)
					effectType = gc.getInfoTypeForString('EFFECT_EXPLOSION_DIRT')
					CyEngine().triggerEffect(effectType, pPlot.getPoint())
					CyEngine().triggerEffect(3, pPlot.getPoint())
					pUnit.changeDamage(50, 0)
					
	#Detonator II
				if (pPlot.getImprovementType() == iImprovementMine2):
					if (not pPlayer.isHuman()):
						pPlot.setImprovementType(-1)
						for xLoop in range (iX -1, iX +1):
							for yLoop in range (iY -1, iY +1):
								pBLOWDUP = gc.getMap().plot(xLoop, yLoop)
								pToast = pBLOWDUP.getUnit(0)
								pToast.changeDamage(90, 0)
								CyEngine().triggerEffect(3, pBLOWDUP.getPoint())
				#Skip plot if it's outside of the bounds of the map
								if (xLoop < 0 or yLoop < 0 or xLoop >= CyMap().getGridWidth() or yLoop >= CyMap().getGridHeight()):
									continue
								if(iFeatureType != iW):
									pBLOWDUP.setFeatureType(iBW,1)
								if (iFeatureType != iT1 or iFeatureType != iT2 or iFeatureType != iT3):
									pBLOWDUP.setFeatureType(iGround,1)

	def onCombatResult(self, argsList):
		'Combat Result'
		pWinner,pLoser = argsList
		iAX = pWinner.getX()
		iAY = pWinner.getY()
		pPlot = pWinner.plot()
		iWinner = pWinner.getUnitType()
		iLoser = pLoser.getUnitType()
		playerX = PyPlayer(pWinner.getOwner())
		unitX = PyInfo.UnitInfo(pWinner.getUnitType())
		playerY = PyPlayer(pLoser.getOwner())
		unitY = PyInfo.UnitInfo(pLoser.getUnitType())
		
		iControlledBleeder = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_CONTROLLED_BLEEDER')
		iControlledRabid = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_CONTROLLED_RABID')
		iControlledSavage = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_CONTROLLED_SAVAGE')
		iControlledFeral = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_CONTROLLED_FERAL')

		iBleeder = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_BLEEDER')
		iRabidBleeder = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_RABID_BLEEDER')
		iSavageBleeder = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_SAVAGE_BLEEDER')
		iSentinel1 = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_SENTINEL1')
		iSentinel2 = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_SENTINEL2')
		iSentinel3 = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_SENTINEL3')
		
		
		
		iFeral = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_FERAL')
		iFeral2 = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_FERAL2')
		iFeral3 = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_FERAL3')
		iRagah = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_RAGAH')
		iSever = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_SEVER')
		iRiest = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_RIEST')
		iAtticus = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_ATTICUS')
		EvilGlow = gc.getInfoTypeForString('EFFECT_ENEMY_GLOW_UNIT')



		iKillCommentRand = CyGame().getSorenRandNum(100, "Afterworld")
		if iWinner == iAtticus:
			if iKillCommentRand < 5:
				iAtticussays = 0
				if iAtticussays == 0:
					Afterworld.addAfterworldMessage(localText.getText("TXT_KEY_ATTICUS", ()), localText.getText("TXT_KEY_A_KC_1", ()))
					iAtticussays = 1
				elif iAtticussays == 1:
					Afterworld.addAfterworldMessage(localText.getText("TXT_KEY_ATTICUS", ()), localText.getText("TXT_KEY_A_KC_2", ()))
					iAtticussays = 2
				elif iAtticussays == 2:
					Afterworld.addAfterworldMessage(localText.getText("TXT_KEY_ATTICUS", ()), localText.getText("TXT_KEY_A_KC_3", ()))
					iAtticussays = 3
				elif iAtticussays == 3:
					Afterworld.addAfterworldMessage(localText.getText("TXT_KEY_ATTICUS", ()), localText.getText("TXT_KEY_A_KC_4", ()))
					iAtticussays = 4
				elif iAtticussays == 4:
					Afterworld.addAfterworldMessage(localText.getText("TXT_KEY_ATTICUS", ()), localText.getText("TXT_KEY_A_KC_5", ()))
					iAtticussays = 5
				elif iAtticussays == 5:
					Afterworld.addAfterworldMessage(localText.getText("TXT_KEY_ATTICUS", ()), localText.getText("TXT_KEY_A_KC_6", ()))
					iAtticussays = 6
				elif iAtticussays == 6:
					Afterworld.addAfterworldMessage(localText.getText("TXT_KEY_ATTICUS", ()), localText.getText("TXT_KEY_A_KC_7", ()))
					iAtticussays = 7
				elif iAtticussays == 7:
					Afterworld.addAfterworldMessage(localText.getText("TXT_KEY_ATTICUS", ()), localText.getText("TXT_KEY_A_KC_8", ()))
					iAtticussays = 8
				elif iAtticussays == 8:
					return
					
		if iWinner == iRiest:
			if iKillCommentRand < 5:
				iRiestCommentRand = self.getRand(8)
				if (iRiestCommentRand == 0):
					Afterworld.addAfterworldMessage(localText.getText("TXT_KEY_RIEST", ()), localText.getText("TXT_KEY_KA_KC_1", ()))
				elif (iRiestCommentRand == 1):
					Afterworld.addAfterworldMessage(localText.getText("TXT_KEY_RIEST", ()), localText.getText("TXT_KEY_KA_KC_2", ()))
				elif (iRiestCommentRand == 2):
					Afterworld.addAfterworldMessage(localText.getText("TXT_KEY_RIEST", ()), localText.getText("TXT_KEY_KA_KC_3", ()))
				elif (iRiestCommentRand == 3):
					Afterworld.addAfterworldMessage(localText.getText("TXT_KEY_RIEST", ()), localText.getText("TXT_KEY_KA_KC_4", ()))
				elif (iRiestCommentRand == 4):
					Afterworld.addAfterworldMessage(localText.getText("TXT_KEY_RIEST", ()), localText.getText("TXT_KEY_KA_KC_5", ()))
				elif (iRiestCommentRand == 5):
					Afterworld.addAfterworldMessage(localText.getText("TXT_KEY_RIEST", ()), localText.getText("TXT_KEY_KA_KC_6", ()))
				elif (iRiestCommentRand == 6):
					Afterworld.addAfterworldMessage(localText.getText("TXT_KEY_RIEST", ()), localText.getText("TXT_KEY_KA_KC_7", ()))
				elif (iRiestCommentRand == 7):
					Afterworld.addAfterworldMessage(localText.getText("TXT_KEY_RIEST", ()), localText.getText("TXT_KEY_KA_KC_8", ()))
	
		if iWinner == iRagah:
			if iKillCommentRand < 5:
				iRagahCommentRand = self.getRand(8)
				if (iRagahCommentRand == 0):
					Afterworld.addAfterworldMessage(localText.getText("TXT_KEY_RAGAH", ()), localText.getText("TXT_KEY_RA_KC_1", ()))
				elif (iRagahCommentRand == 1):
					Afterworld.addAfterworldMessage(localText.getText("TXT_KEY_RAGAH", ()), localText.getText("TXT_KEY_RA_KC_2", ()))
				elif (iRagahCommentRand == 2):
					Afterworld.addAfterworldMessage(localText.getText("TXT_KEY_RAGAH", ()), localText.getText("TXT_KEY_RA_KC_3", ()))
				elif (iRagahCommentRand == 3):
					Afterworld.addAfterworldMessage(localText.getText("TXT_KEY_RAGAH", ()), localText.getText("TXT_KEY_RA_KC_4", ()))
				elif (iRagahCommentRand == 4):
					Afterworld.addAfterworldMessage(localText.getText("TXT_KEY_RAGAH", ()), localText.getText("TXT_KEY_RA_KC_5", ()))
				elif (iRagahCommentRand == 5):
					Afterworld.addAfterworldMessage(localText.getText("TXT_KEY_RAGAH", ()), localText.getText("TXT_KEY_RA_KC_6", ()))
				elif (iRagahCommentRand == 6):
					Afterworld.addAfterworldMessage(localText.getText("TXT_KEY_RAGAH", ()), localText.getText("TXT_KEY_RA_KC_7", ()))
				elif (iRagahCommentRand == 7):
					Afterworld.addAfterworldMessage(localText.getText("TXT_KEY_RAGAH", ()), localText.getText("TXT_KEY_RA_KC_8", ()))
	
		if iWinner == iSever:
			if iKillCommentRand < 5:
				iSeverCommentRand = self.getRand(8)
				if (iSeverCommentRand == 0):
					Afterworld.addAfterworldMessage(localText.getText("TXT_KEY_SEVER", ()), localText.getText("TXT_KEY_S_KC_1", ()))
				elif (iSeverCommentRand == 1):
					Afterworld.addAfterworldMessage(localText.getText("TXT_KEY_SEVER", ()), localText.getText("TXT_KEY_S_KC_2", ()))
				elif (iSeverCommentRand == 2):
					Afterworld.addAfterworldMessage(localText.getText("TXT_KEY_SEVER", ()), localText.getText("TXT_KEY_S_KC_3", ()))
				elif (iSeverCommentRand == 3):
					Afterworld.addAfterworldMessage(localText.getText("TXT_KEY_SEVER", ()), localText.getText("TXT_KEY_S_KC_4", ()))
				elif (iSeverCommentRand == 4):
					Afterworld.addAfterworldMessage(localText.getText("TXT_KEY_SEVER", ()), localText.getText("TXT_KEY_S_KC_5", ()))
				elif (iSeverCommentRand == 5):
					Afterworld.addAfterworldMessage(localText.getText("TXT_KEY_SEVER", ()), localText.getText("TXT_KEY_S_KC_6", ()))
				elif (iSeverCommentRand == 6):
					Afterworld.addAfterworldMessage(localText.getText("TXT_KEY_SEVER", ()), localText.getText("TXT_KEY_S_KC_7", ()))
				elif (iSeverCommentRand == 7):
					Afterworld.addAfterworldMessage(localText.getText("TXT_KEY_SEVER", ()), localText.getText("TXT_KEY_S_KC_8", ()))


		iEVILUTION = CyGame().getSorenRandNum(100, "Afterworld")
		
		if pLoser.isDead():
#PLAYER
			if iLoser == iBleeder:
				if iWinner == iControlledBleeder:
					if iEVILUTION < 40:
						pWinner.kill(true, -1)
						CyEngine().triggerEffect(EvilGlow, pPlot.getPoint())
						gc.getPlayer(0).initUnit(iControlledRabid, iAX, iAY, UnitAITypes.UNITAI_ATTACK_CITY_LEMMING, DirectionTypes.NO_DIRECTION)
			elif iLoser == iBleeder:
				if iWinner == iControlledRabid:
					if iEVILUTION < 10:
						pWinner.kill(true, -1)
						gc.getPlayer(0).initUnit(iControlledSavage, iAX, iAY, UnitAITypes.UNITAI_ATTACK_CITY_LEMMING, DirectionTypes.NO_DIRECTION)
						CyEngine().triggerEffect(EvilGlow, pPlot.getPoint())

			elif iLoser == iRabidBleeder:
				if iWinner == iControlledRabid:
					if iEVILUTION < 40:
						pWinner.kill(true, -1)
						gc.getPlayer(0).initUnit(iControlledSavage, iAX, iAY, UnitAITypes.UNITAI_ATTACK_CITY_LEMMING, DirectionTypes.NO_DIRECTION)
						CyEngine().triggerEffect(EvilGlow, pPlot.getPoint())
			elif iLoser == iRabidBleeder:
				if iWinner == iSavageBleeder:
					if iEVILUTION < 10:
						pWinner.kill(true, -1)
						gc.getPlayer(0).initUnit(iControlledFeral, iAX, iAY, UnitAITypes.UNITAI_ATTACK_CITY_LEMMING, DirectionTypes.NO_DIRECTION)
						CyEngine().triggerEffect(EvilGlow, pPlot.getPoint())

			elif iLoser == iSavageBleeder:
				if iWinner == iControlledSavage:
					if iEVILUTION < 20:
						pWinner.kill(true, -1)
						gc.getPlayer(0).initUnit(iControlledFeral, iAX, iAY, UnitAITypes.UNITAI_ATTACK_CITY_LEMMING, DirectionTypes.NO_DIRECTION)
						CyEngine().triggerEffect(EvilGlow, pPlot.getPoint())


#AI
			if iLoser == iBleeder: #If the loser is a Bleeder
				if iWinner == iBleeder:
					if Afterworld.iObjective >= 0:
						if iEVILUTION < 35:  #Bleeder has another Bleeder for lunch and evolves into a Rabid Bleeder
							pWinner.kill(true, -1)
							gc.getPlayer(1).initUnit(iRabidBleeder, iAX, iAY, UnitAITypes.UNITAI_ATTACK_CITY_LEMMING, DirectionTypes.NO_DIRECTION)
							CyEngine().triggerEffect(EvilGlow, pPlot.getPoint())
				elif iWinner == iRabidBleeder:
					if Afterworld.iObjective != 0:
						if iEVILUTION < 5:
							pWinner.kill(true, -1)
							gc.getPlayer(1).initUnit(iSavageBleeder, iAX, iAY, UnitAITypes.UNITAI_ATTACK_CITY_LEMMING, DirectionTypes.NO_DIRECTION)
							CyEngine().triggerEffect(EvilGlow, pPlot.getPoint())
				elif iWinner == iSavageBleeder:
					if Afterworld.iObjective != 4:
						if iEVILUTION < 1:
							pWinner.kill(true, -1)
							gc.getPlayer(2).initUnit(iFeral, iAX, iAY, UnitAITypes.UNITAI_ATTACK_CITY_LEMMING, DirectionTypes.NO_DIRECTION)
							CyEngine().triggerEffect(EvilGlow, pPlot.getPoint())

			elif iLoser == iRabidBleeder: #If the user is a Rabid Bleeder
				if iWinner == iRabidBleeder:
					if Afterworld.iObjective >= 0:
						if iEVILUTION < 30:  #Rabid Bleeder has another Rabid Bleeder for lunch and evolves into a Savage Bleeder
							pWinner.kill(true, -1)
							gc.getPlayer(1).initUnit(iSavageBleeder, iAX, iAY, UnitAITypes.UNITAI_ATTACK_CITY_LEMMING, DirectionTypes.NO_DIRECTION)
							CyEngine().triggerEffect(EvilGlow, pPlot.getPoint())
				elif iWinner == iSavageBleeder:
					if Afterworld.iObjective != 4:
						if iEVILUTION < 2:
							pWinner.kill(true, -1)
							gc.getPlayer(2).initUnit(iFeral, iAX, iAY, UnitAITypes.UNITAI_ATTACK_CITY_LEMMING, DirectionTypes.NO_DIRECTION)
							CyEngine().triggerEffect(EvilGlow, pPlot.getPoint())
				elif iWinner == iSavageBleeder:
					if Afterworld.iObjective == 4:
						if iEVILUTION < 2:
							pWinner.kill(true, -1)
							gc.getPlayer(2).initUnit(iFeral, iAX, iAY, UnitAITypes.UNITAI_ATTACK_CITY_LEMMING, DirectionTypes.NO_DIRECTION)
							CyEngine().triggerEffect(EvilGlow, pPlot.getPoint())

			elif iLoser == iSavageBleeder: #If the user is a Savage Bleeder
				if iWinner == iSavageBleeder:
					if Afterworld.iObjective >= 1:
						if iEVILUTION < 20:  #Savage Bleeder has another Savage Bleeder for lunch and evolves into a Feral
							pWinner.kill(true, -1)
							gc.getPlayer(1).initUnit(iFeral, iAX, iAY, UnitAITypes.UNITAI_ATTACK_CITY_LEMMING, DirectionTypes.NO_DIRECTION)
							CyEngine().triggerEffect(EvilGlow, pPlot.getPoint())
				elif iWinner == iSavageBleeder:
					if Afterworld.iObjective == 4:
						if iEVILUTION < 5:
							pWinner.kill(true, -1)
							gc.getPlayer(2).initUnit(iFeral, iAX, iAY, UnitAITypes.UNITAI_ATTACK_CITY_LEMMING, DirectionTypes.NO_DIRECTION)
							CyEngine().triggerEffect(EvilGlow, pPlot.getPoint())

#		if (not self.__LOG_COMBAT):
#			return
			
#		if playerX and playerX and unitX and playerY:
#			print('Player %d Civilization %s Unit %s has defeated Player %d Civilization %s Unit %s' 
#				%(playerX.getID(), playerX.getCivilizationName(), unitX.getDescription(),
#				playerY.getID(), playerY.getCivilizationName(), unitY.getDescription()))
				
		
			
	def onUnitKilled(self, argsList):
		pUnit, iAttacker = argsList
		iUnitType = pUnit.getUnitType()
		iHumanTeam = gc.getPlayer(0).getTeam()
		
		iX = pUnit.getX()
		iY = pUnit.getY()
		iPlayer = pUnit.getOwner()
		pPlayer = gc.getPlayer(iPlayer)
		
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
		
		iAtticus = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_ATTICUS')
		iRiest = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_RIEST')
		iRagah = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_RAGAH')
		iSever = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_SEVER')
		iControlledRabid = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_CONTROLLED_RABID')
		iControlledSavage = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_CONTROLLED_SAVAGE')
		iControlledFeral = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_CONTROLLED_FERAL')
		
#		#print "OnUnitKilled.iAttacker == %s, iUnitType == %s" %(iAttacker,iUnitType)
#		if pLoser.isDead():
		if (iAttacker == 0):
			if Afterworld.pPushedButtonUnit != None:
				
				print("   *** Player %d Attacking unit ID %d being given XP" %(Afterworld.pPushedButtonUnit.getOwner(), Afterworld.pPushedButtonUnit.getID()))
				
				if (pUnit.getUnitType() == iRabidBleeder or pUnit.getUnitType() == iSavageBleeder):
					Afterworld.pPushedButtonUnit.changeExperience(2,Afterworld.pPushedButtonUnit.experienceNeeded()+50,0,0,0)
					print("Rabid or Savage")
				elif (pUnit.getUnitType() == iBleeder):
					Afterworld.pPushedButtonUnit.changeExperience(1,Afterworld.pPushedButtonUnit.experienceNeeded()+50,0,0,0)
					print("Normal Bleeder")
					#If the units kill a bleeder, they may make a comment
					
				elif(pUnit.getUnitType() == iSentinel3):
					Afterworld.pPushedButtonUnit.changeExperience(2,Afterworld.pPushedButtonUnit.experienceNeeded()+50,0,0,0)
				elif (pUnit.getUnitType() == iSentinel1 or pUnit.getUnitType() == iSentinel2):
					Afterworld.pPushedButtonUnit.changeExperience(1,Afterworld.pPushedButtonUnit.experienceNeeded()+50,0,0,0)
					
				elif (pUnit.getUnitType() == iFeral or pUnit.getUnitType() == iFeral2 or pUnit.getUnitType() == iFeral3):
					Afterworld.pPushedButtonUnit.changeExperience(4,Afterworld.pPushedButtonUnit.experienceNeeded()+50,0,0,0)
		
		
		if pPlayer.isHuman():
			print "human died?"
			if (iUnitType != iSentinel1 and iUnitType != iSentinel2 and iUnitType != iSentinel3 and iUnitType != iControlledBleeder and iUnitType != iControlledRabid and iUnitType != iControlledSavage and iUnitType != iControlledFeral):
				print "not a sent, controlled bleeder, controlled rabid, controlled savage, controlled feral"
				print iUnitType
				iTeamID = 1
				iVictoryID = 1
				#CyGame().setWinner(iTeamID, iVictoryID)
				#self.addPopup(localText.getText("TXT_KEY_EMPTYENTRY", ()), localText.getText("TXT_KEY_FAILURE", ()))
				import CvScreensInterface
				CvScreensInterface.showDanQuayleScreen("nothing")
				
				
		if (iUnitType == iFeral):
			
			bAddUnit = true
			
			pPlot = CyMap().plot(iX, iY)
			for iUnitLoop in range(pPlot.getNumUnits()):
				pUnit = pPlot.getUnit(iUnitLoop)
				
				if (pUnit.getUnitType() == iFeral2):
					bAddUnit = false
			
			# Only add a unit once (onUnitKilled can be called twice in melee combat)
			if (bAddUnit):
				gc.getPlayer(2).initUnit(iFeral2, iX, iY, UnitAITypes.UNITAI_ATTACK_CITY_LEMMING, DirectionTypes.NO_DIRECTION)
					
				if Afterworld.iObjective == 1:
					self.addPopup(localText.getText("TXT_KEY_SEVER", ()), localText.getText("TXT_KEY_FERALFIGHT1", ()))
					self.addPopup(localText.getText("TXT_KEY_RAGAH", ()), localText.getText("TXT_KEY_FERALFIGHT2", ()))

		if (iUnitType == iFeral2):
			
			bAddUnit = true
			
			pPlot = CyMap().plot(iX, iY)
			for iUnitLoop in range(pPlot.getNumUnits()):
				pUnit = pPlot.getUnit(iUnitLoop)
				
				if (pUnit.getUnitType() == iFeral3):
					bAddUnit = false
					
			if (bAddUnit):
				gc.getPlayer(2).initUnit(iFeral3, iX, iY, UnitAITypes.UNITAI_ATTACK_CITY_LEMMING, DirectionTypes.NO_DIRECTION)
		
	#Entity Fight
		if (iUnitType == iEntity1):
			gc.getPlayer(1).initUnit(iEntity2, iX, iY, UnitAITypes.UNITAI_ATTACK_CITY_LEMMING, DirectionTypes.NO_DIRECTION)
			Afterworld.pAngryEntity = 1
			print "Stage 1"

		elif (iUnitType == iEntity2):#AngryEntity 1 ends
			gc.getPlayer(1).initUnit(iEntity3, iX, iY, UnitAITypes.UNITAI_ATTACK_CITY_LEMMING, DirectionTypes.NO_DIRECTION)
			Afterworld.pAngryEntity = 2
			
			print "stage 2"
		elif (iUnitType == iEntity3):
			gc.getPlayer(1).initUnit(iEntity6, iX, iY, UnitAITypes.UNITAI_ATTACK_CITY_LEMMING, DirectionTypes.NO_DIRECTION)
			Afterworld.pAngryEntity = 3
			
			print "stage 3"
		elif (iUnitType == iEntity6):  #AngryEntity 3 ends
#			gc.getPlayer(1).initUnit(iEntity7, iX, iY, UnitAITypes.UNITAI_ATTACK_CITY_LEMMING, DirectionTypes.NO_DIRECTION)
#			Afterworld.pAngryEntity = 4
#			
#			print "Stage 4"
#		elif (iUnitType == iEntity7):
			print "Final one"
			iVictoryID = 1
			CyGame().setWinner(iHumanTeam, iVictoryID)
			
			# victory screen
			import CvScreensInterface
			CvScreensInterface.showWonderMovie((1,))
		
		if (iAttacker == 0):
			
			pAttackingPlayer = gc.getPlayer(0)
			pyPlayer = PyPlayer(0)
			
			apUnitList = pyPlayer.getUnitList()
			for pUnitLoop in apUnitList:
				
				pUnitData = Afterworld.getUnitDataByID(pUnitLoop.getID())
				
				if pUnitData:
					pUnitData.setExperience(pUnitLoop.getExperience())
					pUnitData.setLevel(pUnitLoop.getLevel())		
		
#		if (not iUnitType == iFeral and not iUnitType == iFeral2 and not iUnitType == iEntity1 and not iUnitType == iEntity2 and not iUnitType == iEntity3 and not iUnitType == iEntity4 and not iUnitType == iEntity5):
#			self.addPopup(localText.getText("TXT_KEY_RA_KC_2", ()), localText.getText("TXT_KEY_RA_KC_2", ()))
		
	#Feral Fight
#		#print "Unit Type (%s) Died - iFeral is %s" %(iUnitType, iFeral)
	def setPlayerOptions(self):
		
		CyMessageControl().sendPlayerOption(PlayerOptionTypes.PLAYEROPTION_QUICK_ATTACK, False)
		CyMessageControl().sendPlayerOption(PlayerOptionTypes.PLAYEROPTION_QUICK_MOVES, False)
		CyMessageControl().sendPlayerOption(PlayerOptionTypes.PLAYEROPTION_QUICK_DEFENSE, False)
		CyMessageControl().sendPlayerOption(PlayerOptionTypes.PLAYEROPTION_SHOW_ENEMY_MOVES, True)
		CyMessageControl().sendPlayerOption(PlayerOptionTypes.PLAYEROPTION_SHOW_FRIENDLY_MOVES, True)
	
	def onGameStart(self, argsList):
		'Called at the start of the game'
		self.parent.onGameStart(self, argsList)
		Afterworld.setup()
		CyGame().setOption(GameOptionTypes.GAMEOPTION_ONE_CITY_CHALLENGE, True)
		CyEngine().setCultureVisibility(0)
		CyEngine().setUnitFlagVisibility(0)
		CyGInterfaceScreen("MainInterface", MAIN_INTERFACE).setMinimapSectionOverride(0, 0, 0.25, 1)
		Afterworld.iObjective = 0
		Afterworld.iStartReconTimer = 0
		self.setPlayerOptions()
		
		for iPlayer in range(gc.getMAX_PLAYERS()):
			player = gc.getPlayer(iPlayer)
			if (player.isAlive() and player.isHuman()):
				popupInfo = CyPopupInfo()
				popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON_SCREEN)
				popupInfo.setText(u"showDawnOfMan")
				popupInfo.addPopup(iPlayer)
		
				popupInfo = CyPopupInfo()
				popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON_SCREEN)
				popupInfo.setData1(0)
				popupInfo.setData2(11)
				popupInfo.setData3(3)
				popupInfo.setText(u"showWonderMovie")
				popupInfo.addPopup(iPlayer)
			
		#Objective 1 location
		if Afterworld.iObjective == 0:
			pPlot = self.getReconPlot()
			pPlot.setOwner(0)
			screen = CyGInterfaceScreen("MainInterface",CvScreenEnums.MAIN_INTERFACE)
			screen.minimapFlashPlot(pPlot.getX(), pPlot.getY(), 2, 90.0)
		#Objective 2 location
		if Afterworld.iObjective == 1:
			screen = CyGInterfaceScreen("MainInterface",CvScreenEnums.MAIN_INTERFACE)
			screen.minimapFlashPlot(57, 3, 2, 90.0)
			screen.minimapFlashPlot(67, 18, 2, 90.0)
			screen.minimapFlashPlot(64, 2, 2, 90.0)
		#Objective 3 location
		if Afterworld.iObjective == 2:
			screen = CyGInterfaceScreen("MainInterface",CvScreenEnums.MAIN_INTERFACE)
			screen.minimapFlashPlot(91, 7, 2, 90.0)
		#Objective 4 location part 1
		if Afterworld.iObjective == 3:
			screen = CyGInterfaceScreen("MainInterface",CvScreenEnums.MAIN_INTERFACE)
			
			screen.minimapFlashPlot(103, 6, 2, 90.0)
		#Objective 4 location part 2
		if Afterworld.iObjective == 4:
			screen = CyGInterfaceScreen("MainInterface",CvScreenEnums.MAIN_INTERFACE)
			screen.minimapFlashPlot(114, 3, 2, 90.0)
		#Objective 4 location part 3
		if Afterworld.iObjective == 5:
			screen = CyGInterfaceScreen("MainInterface",CvScreenEnums.MAIN_INTERFACE)
			screen.minimapFlashPlot(131, 3, 2, 90.0)
		
		# Initialize Unit Data for all of human player's (0) units
		Afterworld.setupUnitData()
	
	def setupUnitAI(self):
		## This code turns the AI on and Off so the game isn't slow
		self.updatePlayerPosition()
		player1Units = PyPlayer(1).getUnitList()
		player2Units = PyPlayer(2).getUnitList()
		barbUnits= PyPlayer(18).getUnitList()
		
		iUnitsInRange = 0
		
		for unit1 in player1Units:
			if unit1.getUnitAIType() == UnitAITypes.UNITAI_UNKNOWN:
				if self.checkUnitDistance(unit1):
					iUnitsInRange += 1
					unit1.setUnitAIType(UnitAITypes.UNITAI_ATTACK_CITY_LEMMING)
		
		for unit2 in player2Units:
			if unit2.getUnitAIType() == UnitAITypes.UNITAI_UNKNOWN:
				if self.checkUnitDistance(unit2):
					iUnitsInRange += 1
					unit2.setUnitAIType(UnitAITypes.UNITAI_ATTACK_CITY_LEMMING)
		
		for barbUnit in barbUnits:
			if barbUnit.getUnitAIType() == UnitAITypes.UNITAI_UNKNOWN:
				if self.checkUnitDistance(barbUnit):
					iUnitsInRange += 1
					barbUnit.setUnitAIType(UnitAITypes.UNITAI_ATTACK_CITY_LEMMING)
			
		print "setupUnitAI-> %s Units in range" %iUnitsInRange
		
	def updatePlayerPosition(self):
		'Updates the human players units plot positions'
		print "updatePlayerPositions"
		playerPlots = []
		
		for pUnit in PyPlayer(0).getUnitList():
			playerPlots.append(pUnit.plot())
		
		# set the players units plots
		self.PlayersPosition = playerPlots
		
	def checkUnitDistance(self, pUnit):
		'determines how far away the player is from pUnit'
		# set to False
		bIsClose = False
		# loop through each player plot and check the units distance from it
		for plotPosition in self.PlayersPosition:
			# check the distance the unit must step to get to the players unit
			iDistance = plotDistance(pUnit.getX(), pUnit.getY(), plotPosition.getX(), plotPosition.getY())
			#print "CheckUnitDistance -> Name: %s, Distance %s" %(pUnit.getID(), iDistance)
			if (iDistance <= AI_DISTANCE_NUM):
				#print "checkUnitDistance->Close Enough"
				# unit is within range
				bIsClose = True
				break
		
		return bIsClose
		
	
	def addPopup(self, szTitle, szText):
		# Don't display popups for autoplay games
		if (gc.getPlayer(CyGame().getActivePlayer()).isAlive()):
			Afterworld.addAfterworldMessage(szTitle, szText)
			popup = PyPopup.PyPopup(-1)
			popup.setHeaderString(szTitle)
			popup.setBodyString(szText)
			popup.launch(true, PopupStates.POPUPSTATE_QUEUED)
			
	def updateUnitData(self):
		# Update Experience & Promotions
		pAttackingPlayer = gc.getPlayer(0)
		pyPlayer = PyPlayer(0)
		
		apUnitList = pyPlayer.getUnitList()
		for pUnitLoop in apUnitList:
			
			pUnitData = Afterworld.getUnitDataByID(pUnitLoop.getID())
			
			if pUnitData:
				# EXP
				pUnitData.setExperience(pUnitLoop.getExperience())
				pUnitData.setLevel(pUnitLoop.getLevel())
				pUnitData.setMoves(pUnitLoop.getMoves())
				
				# Promotions
				pUnitData.resetPromotionList()
				for iPromotionLoop in range(gc.getNumPromotionInfos()):
					if (pUnitLoop.isHasPromotion(iPromotionLoop)):
						pUnitData.addPromotionToList(iPromotionLoop)
	
	def onUnitPromoted(self, argsList):
		'Unit Promoted'
		pUnit, iPromotion = argsList
		
		if (pUnit.getOwner() == 0):
			
			self.updateUnitData()
			
	def onGotoPlotSet(self, argsList):
		'Nuke Explosion'
		pPlot, iPlayer = argsList
		
		CyMessageControl().sendModNetMessage(iPlayer, pPlot.getX(), pPlot.getY(), -1, -1)
		
	def onModNetMessage(self, argsList):
		'Called whenever CyMessageControl().sendModNetMessage() is called - this is all for you modders!'
		
		iData1, iData2, iData3, iData4, iData5 = argsList
		
		iPlayer = iData1
		iX = iData2
		iY = iData3
		pPlot = CyMap().plot(iX, iY)
		
		Afterworld.apPlayerGotoPlotList[iPlayer][0] = iX
		Afterworld.apPlayerGotoPlotList[iPlayer][1] = iY
		
#		#print("Setting Goto Plot for Player %d to (%d, %d)" %(iPlayer, iX, iY))

	def highlightArea( self, iX, iY, iWidth, iHeight ):
		screen = CyGInterfaceScreen("MainInterface", 99)
#		screen.addDDSGFC( "TutorialHighlight", ArtFileMgr.getInterfaceArtInfo("INTERFACE_TUTORIAL_HIGHLIGHT_LARGE").getPath(), iX, iY, iWidth, iHeight, WidgetTypes.WIDGET_GENERAL, -1, -1 )
		screen.moveToFront( "TutorialHighlight" )
		screen.moveBackward( "TutorialHighlight" )
		screen.show( "TutorialHighlight" )

	def hideHighlight( self ):
		screen = CyGInterfaceScreen("MainInterface", 99)
		screen.hide("TutorialHighlight")
		