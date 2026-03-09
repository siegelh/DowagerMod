## Sid Meier's Civilization 4
## Copyright Firaxis Games 2007
from CvPythonExtensions import *
from PyHelpers import PyPlayer

import pickle
import CvScreenEnums

gc = CyGlobalContext()

	
class UnitData:
	
	def __init__(self):

		self.iOwner = -1
		self.iID = -1

		self.iUnitType = -1
		
		self.iMDATimer = 0
		self.iRepairTimer = 0
		self.iSpawnTimer = 0
		self.iSpawn2Timer = 0
		self.iSpawn3Timer = 0				
		self.iDetonatorTimer = 0
		self.iMAULerTimer = 0
		self.iSilenceTimer = 0
		self.iEnhAccTimer = 0
		self.iBarrierTimer = 0
		self.iInhibitorTimer = 0
		self.iProjectTimer = 0
		self.iControlTimer = 0
		self.iGrenadeTimer = 0
		self.iShadowTimer = -1
		self.iInvisibilityTurns = -1
		
		self.iMoves = 0
		self.iExperience = 0
		self.iLevel = 0
		self.iNumPromotions = 0
		self.iNumRepairMechanism = 0
		self.iNumAccelerationMechanism = 0
		self.iNumDeceptionBeacon = 0

		self.aiPromotionList = []
	
	def getOwner(self):
			return self.iOwner
	def setOwner(self, iValue):
			self.iOwner = iValue

	def getID(self):
			return self.iID
	def setID(self, iValue):
			self.iID = iValue

	def getUnitType(self):
			return self.iUnitType
	def setUnitType(self, iValue):
			self.iUnitType = iValue
			
	def getGrenadeTimer(self):
			return self.iGrenadeTimer
	def setGrenadeTimer(self, iValue):
			self.iGrenadeTimer = iValue
	def changeGrenadeTimer(self, iChange):
			self.iGrenadeTimer += iChange			

	def getNumRepairMechanism(self):
			return self.iNumRepairMechanism
	def setNumRepairMechanism(self, iValue):
			self.iNumRepairMechanism = iValue
	def changeNumRepairMechanism(self, iChange):
			self.iNumRepairMechanism += iChange

	def getNumDeceptionBeacon(self):
			return self.iNumDeceptionBeacon
	def setNumDeceptionBeacon(self, iValue):
			self.iNumDeceptionBeacon = iValue
	def changeNumDeceptionBeacon(self, iChange):
			self.iNumDeceptionBeacon += iChange

	def getNumAccelerationMechanism(self):
			return self.iNumAccelerationMechanism
	def setNumAccelerationMechanism(self, iValue):
			self.iNumAccelerationMechanism = iValue
	def changeNumAccelerationMechanism(self, iChange):
			self.iNumAccelerationMechanism += iChange

	def getInvisibilityTurns(self):
			return self.iInvisibilityTurns
	def setInvisibilityTurns(self, iValue):
			self.iInvisibilityTurns = iValue
	def changeInvisibilityTurns(self, iChange):
			self.iInvisibilityTurns += iChange
			
	def getRepairTimer(self):
			return self.iRepairTimer
	def setRepairTimer(self, iValue):
			self.iRepairTimer = iValue
	def changeRepairTimer(self, iChange):
			self.iRepairTimer += iChange

	def getSpawnTimer(self):
			return self.iSpawnTimer
	def setSpawnTimer(self, iValue):
			self.iSpawnTimer = iValue
	def changeSpawnTimer(self, iChange):
			self.iSpawnTimer += iChange
		
	def getSpawn2Timer(self):
			return self.iSpawn2Timer
	def setSpawn2Timer(self, iValue):
			self.iSpawn2Timer = iValue
	def changeSpawn2Timer(self, iChange):
			self.iSpawn2Timer += iChange		

	def getSpawn3Timer(self):
			return self.iSpawn3Timer
	def setSpawn3Timer(self, iValue):
			self.iSpawn3Timer = iValue
	def changeSpawn3Timer(self, iChange):
			self.iSpawn3Timer += iChange		
			
	def getDetonatorTimer(self):
			return self.iDetonatorTimer
	def setDetonatorTimer(self, iValue):
			self.iDetonatorTimer = iValue
	def changeDetonatorTimer(self, iChange):
			self.iDetonatorTimer += iChange
		
	def getMAULerTimer(self):
			return self.iMAULerTimer
	def setMAULerTimer(self, iValue):
			self.iMAULerTimer = iValue
	def changeMAULerTimer(self, iChange):
			self.iMAULerTimer += iChange

	def getSilenceTimer(self):
			return self.iSilenceTimer
	def setSilenceTimer(self, iValue):
			self.iSilenceTimer = iValue
	def changeSilenceTimer(self, iChange):
			self.iSilenceTimer += iChange
			
	def getEnhAccTimer(self):
			return self.iEnhAccTimer
	def setEnhAccTimer(self, iValue):
			self.iEnhAccTimer = iValue
	def changeEnhAccTimer(self, iChange):
			self.iEnhAccTimer += iChange

	def getBarrierTimer(self):
			return self.iBarrierTimer
	def setBarrierTimer(self, iValue):
			self.iBarrierTimer = iValue
	def changeBarrierTimer(self, iChange):
			self.iBarrierTimer += iChange

	def getInhibitorTimer(self):
			return self.iInhibitorTimer
	def setInhibitorTimer(self, iValue):
			self.iInhibitorTimer = iValue
	def changeInhibitorTimer(self, iChange):
			self.iInhibitorTimer += iChange

	def getProjectTimer(self):
			return self.iProjectTimer
	def setProjectTimer(self, iValue):
			self.iProjectTimer = iValue
	def changeProjectTimer(self, iChange):
			self.iProjectTimer += iChange

	def getControlTimer(self):
			return self.iControlTimer
	def setControlTimer(self, iValue):
			self.iControlTimer = iValue
	def changeControlTimer(self, iChange):
			self.iControlTimer += iChange

	def getMDATimer(self):
			return self.iMDATimer
	def setMDATimer(self, iValue):
			self.iMDATimer = iValue
	def changeMDATimer(self, iChange):
			self.iMDATimer += iChange

	def getShadowTimer(self):
			return self.iShadowTimer
	def setShadowTimer(self, iValue):
			self.iShadowTimer = iValue
	def changeShadowTimer(self, iChange):
			self.iShadowTimer += iChange

	def getExperience(self):
			return self.iExperience
	def setExperience(self, iValue):
			self.iExperience = iValue
	def changeExperience(self, iChange):
			self.iExperience += iChange

	def getMoves(self):
			return self.iMoves
	def setMoves(self, iValue):
			self.iMoves = iValue
	def changeMoves(self, iChange):
			self.iMoves += iChange

	def getLevel(self):
			return self.iLevel
	def setLevel(self, iValue):
			self.iLevel = iValue
	def changeLevel(self, iChange):
			self.iLevel += iChange

	def getNumPromotions(self):
			return self.iNumPromotions
	def setNumPromotions(self, iValue):
			self.iNumPromotions = iValue
	def changeNumPromotions(self, iChange):
			self.iNumPromotions += iChange

	def getPromotionList(self):
			return self.aiPromotionList
	def setPromotionList(self, aList):
			self.aiPromotionList = aList
	def getPromotionFromList(self, iIndex):
			return self.aiPromotionList[iIndex]
	def addPromotionToList(self, iValue):
			self.aiPromotionList.append(iValue)
			self.changeNumPromotions(1)
	def resetPromotionList(self):
			self.aiPromotionList = []
			self.setNumPromotions(0)

	def getOutputData(self):
			aData = []

			aData.append(self.getOwner())
			aData.append(self.getID())
			aData.append(self.getUnitType())
			aData.append(self.getNumDeceptionBeacon())
			aData.append(self.getNumRepairMechanism())
			aData.append(self.getNumAccelerationMechanism())

			aData.append(self.getGrenadeTimer())
			aData.append(self.getMDATimer())
			aData.append(self.getInvisibilityTurns())
			aData.append(self.getRepairTimer())
			aData.append(self.getSpawnTimer())
			aData.append(self.getSpawn2Timer())
			aData.append(self.getSpawn3Timer())
			aData.append(self.getDetonatorTimer())
			aData.append(self.getMAULerTimer())
			aData.append(self.getSilenceTimer())
			aData.append(self.getEnhAccTimer())
			aData.append(self.getBarrierTimer())
			aData.append(self.getInhibitorTimer())
			aData.append(self.getProjectTimer())
			aData.append(self.getControlTimer())
			aData.append(self.getShadowTimer())

			aData.append(self.getExperience())
			aData.append(self.getMoves())
			aData.append(self.getLevel())
			aData.append(self.getNumPromotions())
			aData.append(self.getPromotionList())

			return aData
			
	def setInputData(self, aData):

			iIterator = 0
			self.setOwner(aData[iIterator])
			iIterator += 1
			self.setID(aData[iIterator])
			iIterator += 1
			self.setUnitType(aData[iIterator])
			iIterator += 1
			self.setNumDeceptionBeacon(aData[iIterator])
			iIterator += 1
			self.setNumRepairMechanism(aData[iIterator])
			iIterator += 1
			self.setNumAccelerationMechanism(aData[iIterator])
			iIterator += 1

			self.setGrenadeTimer(aData[iIterator])
			iIterator += 1
			self.setMDATimer(aData[iIterator])
			iIterator += 1
			self.setInvisibilityTurns(aData[iIterator])
			iIterator += 1
			self.setRepairTimer(aData[iIterator])
			iIterator += 1
			self.setSpawnTimer(aData[iIterator])
			iIterator += 1
			self.setSpawn2Timer(aData[iIterator])
			iIterator += 1
			self.setSpawn3Timer(aData[iIterator])
			iIterator += 1
			self.setDetonatorTimer(aData[iIterator])
			iIterator += 1
			self.setMAULerTimer(aData[iIterator])
			iIterator += 1
			self.setSilenceTimer(aData[iIterator])
			iIterator += 1
			self.setEnhAccTimer(aData[iIterator])
			iIterator += 1
			self.setBarrierTimer(aData[iIterator])
			iIterator += 1
			self.setInhibitorTimer(aData[iIterator])
			iIterator += 1
			self.setProjectTimer(aData[iIterator])
			iIterator += 1
			self.setControlTimer(aData[iIterator])
			iIterator += 1
			self.setShadowTimer(aData[iIterator])
			iIterator += 1

			self.setExperience(aData[iIterator])
			iIterator += 1
			self.setMoves(aData[iIterator])
			iIterator += 1
			self.setLevel(aData[iIterator])
			iIterator += 1
			self.setNumPromotions(aData[iIterator])
			iIterator += 1
			self.setPromotionList(aData[iIterator])
			iIterator += 1

class Afterworld:
	def __init__(self):
		self.setup()
	
	def setup(self):
		self.pPushButton = 0
		self.pPushedButtonUnit = None
		self.pSpawnFeralTile = 0
		self.pSpawnEntityTile = 0
		self.pBarrier1 = 0
		self.pBarrier2 = 0
		self.pBarrier3 = 0
		self.pBarrier4 = 0
		self.pAngryEntity = 0
		self.iSacrificeSever = 0
		self.MAUL = 0
		
		self.iTutorialMechanism = 0
		self.iStartReconTimer = 0
		self.iStartUplinkTimer = 0
		self.iUplinkSever = 0
		self.iUplinkAtticus = 0
		self.iUplinkJal = 0
		self.iChatMessages = 0
		self.iObjective = -1
		
		self.szMissionText = "No Objective"
		self.szMissionTitleText = "Title"
		
		self.fAfterworldTimer = -1.0
		self.AfterworldMessages = []
		self.bNewAfterworldMessage = False
		self.iCurrentAfterworldMessage = 0
		
		self.resetValues()
	
	def updateMinimapSection(self):
		pScreen = CyGInterfaceScreen("MainInterface", CvScreenEnums.MAIN_INTERFACE)
		if self.iObjective == 0:
			pScreen.setMinimapSectionOverride(0, 0, 0.25, 1)
		elif self.iObjective == 1:
			pScreen.setMinimapSectionOverride(.15, 0, 0.50, 1)
		elif self.iObjective == 2:
			pScreen.setMinimapSectionOverride(.30, 0, 0.75, 1)
		elif self.iObjective == 99:
			pScreen.setMinimapSectionOverride(.30, 0, 0.75, 1)				
		elif self.iObjective == 3:
			pScreen.setMinimapSectionOverride(.30, 0, 0.75, 1)
		elif self.iObjective == 4:
			pScreen.setMinimapSectionOverride(.55, 0, 1, 1)
		elif self.iObjective == 5:
			pScreen.setMinimapSectionOverride(.55, 0, 1, 1)			
		
	def getiTutorialMechanism(self):
		return self.iTutorialMechanism
	
	def getiStartReconTimer(self):
		return self.iStartReconTimer
	
	def getiStartUplinkTimer(self):
		return self.iStartUplinkTimer
		
	def getiUplinkSever(self):
		return self.iUplinkSever
		
	def getiUplinkAtticus(self):
		return self.iUplinkAtticus
		
	def getiUplinkJal(self):
		return self.iUplinkJal
		
	def getiChatMessages(self):
		return self.iChatMessages
		
	def getiObjective(self):
		return self.iObjective


	def pickleAfterworld(self):
		import cPickle
		
		aAfterPickle = []
		aAfterPickle.append(self.getiChatMessages())
		aAfterPickle.append(self.getiStartReconTimer())
		aAfterPickle.append(self.getiStartUplinkTimer())
		aAfterPickle.append(self.getiUplinkSever())
		aAfterPickle.append(self.getiUplinkAtticus())
		aAfterPickle.append(self.getiUplinkJal())
		aAfterPickle.append(self.getiTutorialMechanism())
		aAfterPickle.append(self.getiObjective())

		CyMap().plot(1,2).setScriptData(cPickle.dumps(aAfterPickle))
		
	def unpickleAfterworld(self):
		import cPickle
		
		PickleTime = cPickle.loads(CyMap().plot(1,2).getScriptData())
		
		self.iChatMessages = PickleTime[0]
		self.iStartReconTimer = PickleTime[1]
		self.iStartUplinkTimer = PickleTime[2]
		self.iUplinkSever = PickleTime[3]
		self.iUplinkAtticus = PickleTime[4]
		self.iUplinkJal = PickleTime[5]	
		self.iTutorialMechanism = PickleTime[6]
		self.iObjective = PickleTime[7]											
			
	def resetValues(self):
		
		self.iMapID = -1
		
		self.iNumUnitDatas = 0
		self.apUnitDatas = []	
		
		self.iUnitCap = 1
		
		self.apPlayerGotoPlotList = []
		for iPlayerLoop in range(gc.getMAX_PLAYERS()):
			self.apPlayerGotoPlotList.append([-1,-1])
		
	def getMapID(self):
		return self.iMapID
	def setMapID(self, iValue):
		self.iMapID = iValue
		
	def getNumUnitDatas(self):
			return self.iNumUnitDatas

	def addUnitData(self, pUnit, bIncrement = True):
		self.apUnitDatas.append(pUnit)
		if (bIncrement):
				self.iNumUnitDatas += 1
#		print("Adding Unit Data")
#		print(pUnit)
#		print("self.iNumUnitDatas")
#		print(self.iNumUnitDatas)
#
	def getUnitDataByIndex(self, iID):
		return self.apUnitDatas[iID]

	def getUnitDataByID(self, iID):
		# necessary to make sure unit datas are reloaded
		for iUnitDataLoop in range(self.getNumUnitDatas()):
				pUnitData = self.getUnitDataByIndex(iUnitDataLoop)
				if (pUnitData.getID() == iID):
						return pUnitData
	
	def resetUnitDatas(self):
		self.iNumUnitDatas = 0
		self.apUnitDatas = []

	def setupUnitData(self):
		# Loop through all of player 0's units and initialize the data for each
		pPlayer = gc.getPlayer(0)
		pyPlayer = PyPlayer(0)
		pPlot = CyMap().plot(0, 0)
		
		apUnitList = pyPlayer.getUnitList()
		for pUnitLoop in apUnitList:
	
			#print("Initializing unit for player 0")
			
			pNewUnitData = UnitData()
	
			pNewUnitData.setOwner(0)
			pNewUnitData.setID(pUnitLoop.getID())
			pNewUnitData.setUnitType(pUnitLoop.getUnitType())
			pNewUnitData.setShadowTimer(0)
			pNewUnitData.setExperience(pUnitLoop.getExperience())
			pNewUnitData.setLevel(pUnitLoop.getLevel())
			pNewUnitData.setMoves(pUnitLoop.getLevel())
			pNewUnitData.setNumRepairMechanism(0)
			pNewUnitData.setNumAccelerationMechanism(0)
			pNewUnitData.setNumDeceptionBeacon(0)
			
			iNumPromotions = 0
			aiPromotionList = []
			for iLoop in range(gc.getNumPromotionInfos()):
					if (pUnitLoop.isHasPromotion(iLoop)):
							iNumPromotions += 1
							aiPromotionList.append(iLoop)
			
			pNewUnitData.setNumPromotions(iNumPromotions)
			pNewUnitData.setPromotionList(aiPromotionList)
			
			self.addUnitData(pNewUnitData)


	def saveUnitDatasToScriptData(self):
		import pickle
		CyGame().setScriptData(str(self.getNumUnitDatas()))
		pPlayer = gc.getPlayer(0)

		aData = []

		for iUnitLoop in range(self.getNumUnitDatas()):
				pUnitData = self.getUnitDataByIndex(iUnitLoop)
				aData.append(pUnitData.getOutputData())
				
#				print("Saving out unit to scriptdata")
#				print(pUnitData.getOutputData())
#				
		pPlayer.setScriptData(pickle.dumps(aData))

	def loadUnitDatasFromScriptData(self):
		import pickle
		
		pPlayer = gc.getPlayer(0)
		
		self.iNumUnitDatas = int(CyGame().getScriptData())
		
		aData = pickle.loads(pPlayer.getScriptData())

		for iUnitLoop in range(self.getNumUnitDatas()):
				aInputData = aData[iUnitLoop]
				pNewUnitData = UnitData()
				pNewUnitData.setInputData(aInputData)
				self.addUnitData(pNewUnitData, false)
				
#				print("Loading unit from ScriptData")
#				print(aInputData)
##		
#		print("\n\nLoading Data From Save File:\n\n")
#		
#		print("self.iNumUnitDatas")
#		print(self.iNumUnitDatas)
#		print("self.apUnitDatas")
#		print(self.apUnitDatas)
		
		for i in range(self.iNumUnitDatas):
			pUnitData = self.getUnitDataByIndex(i)
#			print(pUnitData.getOutputData())
			
	def syncUnitDataToUnit(self, pUnitData, pUnit):
		
#		print("pUnitData.getExperience()")
#		print(pUnitData.getExperience())
		
		pUnit.setExperience(pUnitData.getExperience(), 1000)
		pUnit.setLevel(pUnitData.getLevel(), 1000)
		pUnit.setMoves(pUnitData.getMoves())
		
		pUnit.setNumRepairMechanism(pUnitData.getNumRepairMechanism(), 4)
		pUnit.setNumAccelerationMechanism(pUnitData.getNumAccelerationMechanism(), 4)
		pUnit.setNumDeceptionBeacon(pUnitData.getNumDeceptionBeacon(), 3)
		
#		print("pUnitData.getPromotionList()")
#		print(pUnitData.getPromotionList())
		
		# Loop through all promotions in the unit data
		for iPromotionID in pUnitData.getPromotionList():
			
#			print("Adding iPromotionID")
#			print(iPromotionID)
			pUnit.setHasPromotion(iPromotionID, true)
		
	def canUnitNotMoveIntoPlot(self, pUnit, pPlot, iOffset=0):
		
		iPlayer = pUnit.getOwner()
		
		iGotoX = self.apPlayerGotoPlotList[iPlayer][0]
		iGotoY = self.apPlayerGotoPlotList[iPlayer][1]
		
#		iDistance = stepDistance(pUnit.getX(), pUnit.getY(), pPlot.getX(), pPlot.getY())	# Distance between unit and current move plot
#		print("Distance is: %d" %(iDistance))
		
		iMovesLeft = pUnit.movesLeft() / gc.getMOVE_DENOMINATOR()
#		bUnitsPresent = pPlot.getNumUnits() >= self.getUnitCap()
		
		#print("\nPlayer %d's goto plot is (%d, %d)" %(iPlayer, iGotoX, iGotoY))
		#print("Checking movable for Unit's plot is (%d, %d)" %(pPlot.getX(), pPlot.getY()))
		#print("Unit %s has moves: %d" %(pUnit.getName(), iMovesLeft))
		
		########################################
		##### Destination plot not this plot (just passing through)
		########################################
		
#		if (iGotoX != pPlot.getX() or iGotoY != pPlot.getY()):
#			#print("Mission doesn't end on bad plot")
#			# Still have at least 1 move left (on our way to the other plot)
#			if (pUnit.movesLeft() > 0):
#			if (iMovesLeft >= iDistance):
#				#print("Unit has enough moves")
#				pGotoPlot = CyMap().plot(iGotoX, iGotoY)
#				# Moving into an enemy unit?
#				bMovingIntoEnemy = pGotoPlot.isVisibleEnemyDefender(pUnit)
#				# Move Plot is already at the cap
#				if (not bMovingIntoEnemy or not bUnitsPresent):
#				if (not bUnitsPresent):
#					#print("Units not present ")
#				return false
		
		# Units may not end up on the same plot as another if their destination is over a turn away
#		if (bUnitsPresent and iMovesLeft <= iDistance):
#			return true
		
		########################
		# Carry on
		########################
		
		bCannotMove = false
		
		pPlayer = gc.getPlayer(iPlayer)
		pTeam = gc.getTeam(pPlayer.getTeam())
		
#		#print("\nUnit can fight: %s" %(pUnit.canFight()))
#		#print("Unit Domain: %s" %(pUnit.getDomainType()))
		
		# Set up lists to see who's already in the plot
		aiNumCombatUnitsByDomain = []
		aiNumNoncombatUnitsByDomain = []
		for iDomainLoop in range(DomainTypes.NUM_DOMAIN_TYPES):
			aiNumCombatUnitsByDomain.append(0)
			aiNumNoncombatUnitsByDomain.append(0)
		
		for iUnitLoop in range(pPlot.getNumUnits()):
			
			pLoopUnit = pPlot.getUnit(iUnitLoop)
			
			# Only count friendly units - you should be able to move a unit in to fight another unit
			if (not pTeam.isAtWar(gc.getPlayer(pLoopUnit.getOwner()).getTeam())):
				
				if (pLoopUnit.canFight()):
					aiNumCombatUnitsByDomain[pLoopUnit.getDomainType()] += 1
				else:
					aiNumNoncombatUnitsByDomain[pLoopUnit.getDomainType()] += 1
		
#		#print("Combat Units:")
#		#print(aiNumCombatUnitsByDomain)
#		#print("Cannot be more than: %d" %((self.getUnitCap() + iOffset)))
#		#print("Noncombat Units:")
#		#print(aiNumNoncombatUnitsByDomain)
#		#print("Cannot be more than: %d" %((self.getUnitCap() + iOffset)))
		
		# Now check to see if this unit can move to the plot based on what we know about who is there
		if (pUnit.canFight()):
			if (aiNumCombatUnitsByDomain[pUnit.getDomainType()] >= (self.getUnitCap() + iOffset)):
				bCannotMove = true
				
		else:
			if (aiNumNoncombatUnitsByDomain[pUnit.getDomainType()] >= (self.getUnitCap() + iOffset)):
				bCannotMove = true
		
#		#print("Unit cannot move to plot (%d, %d): %s" %(pPlot.getX(), pPlot.getY(), bCannotMove))
		return bCannotMove
				
	def getUnitCap(self):
		return self.iUnitCap

	def getMissionText(self):
		return self.szMissionText
	
	def getMissionTitleText(self):
		return self.szMissionTitleText
	
	def setMissionText(self, titleText, bodyText):
		self.szMissionTitleText = titleText
		self.szMissionText = bodyText
		CyInterface().setDirty(InterfaceDirtyBits.Flag_DIRTY_BIT, True)
	
	def addAfterworldMessage(self, szTitle, szMessage, fTimer=5):			
		if not (szTitle, szMessage) in self.AfterworldMessages:
			self.AfterworldMessages.append((szTitle, szMessage, fTimer))
			self.fAfterworldTimer = fTimer
			self.bNewAfterworldMessage = True
	
	def getCurrentAfterworldMessage(self):
		if self.AfterworldMessages and self.iCurrentAfterworldMessage <= len(self.AfterworldMessages)-1:
			return self.AfterworldMessages[self.iCurrentAfterworldMessage]

	def getPreviousAfterworldMessage(self):
		if self.AfterworldMessages and self.iCurrentAfterworldMessage != 0:
			self.iCurrentAfterworldMessage -= 1
			self.bNewAfterworldMessage = True
			return self.AfterworldMessages[self.iCurrentAfterworldMessage]
	
	def getNextAfterworldMessage(self):
		if self.AfterworldMessages and self.iCurrentAfterworldMessage != len(self.AfterworldMessages)-1:
			self.processAfterworldMessage()
			return self.AfterworldMessages[self.iCurrentAfterworldMessage]
	
	def processAfterworldMessage(self):
		if self.AfterworldMessages:
			self.iCurrentAfterworldMessage += 1
			self.bNewAfterworldMessage = True
	
	def saveAfterworldMessages(self):
		import cPickle
		
		messageStore = []
		
		if self.AfterworldMessages:
			messageStore.append(self.AfterworldMessages)
			messageStore.append(self.bNewAfterworldMessage)
			messageStore.append(str(self.iCurrentAfterworldMessage))
			messageStore.append(self.fAfterworldTimer)
			
			CyMap().plot(0,0).setScriptData(cPickle.dumps(messageStore))
	
	def getButton(self):
		AfterworldMessage = self.getCurrentAfterworldMessage()
		if AfterworldMessage:
			UnitButtons = { 'TXT_KEY_JAL' : "UNIT_JAL",
								'TXT_KEY_SEVER' : "UNIT_SEVER",
								'TXT_KEY_ATTICUS' : "UNIT_ATTICUS",
								'TXT_KEY_RIEST' : "UNIT_RIEST",
								'TXT_KEY_RAGAH' : "UNIT_RAGAH", }
			
			for key in UnitButtons.keys():
				text = CyTranslator().getText(key, ())
				if AfterworldMessage[0] == text:
					return gc.getUnitInfo(gc.getInfoTypeForString(UnitButtons[key])).getButton()

		return "None"
		
		
	def loadAfterworldMessages(self):
		import cPickle
		self.fAfterworldTimer = -1.0
		self.AfterworldMessages = []
		self.bNewAfterworldMessage = False
		self.iCurrentAfterworldMessage = 0
		
		messageLoad = cPickle.loads(CyMap().plot(0,0).getScriptData())
		
		#print "AfterworldLoad: %s" %messageLoad
		
		self.AfterworldMessages = messageLoad[0]
		self.bNewAfterworldMessage = messageLoad[1]
		self.iCurrentAfterworldMessage = int(messageLoad[2])
		if len(messageLoad) > 3:
			self.fAfterworldTimer = float(messageLoad[3])
			
g_Afterworld = Afterworld()