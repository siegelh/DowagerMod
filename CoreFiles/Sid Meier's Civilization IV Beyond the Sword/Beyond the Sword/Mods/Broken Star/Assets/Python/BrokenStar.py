## Sid Meier's Civilization 4
## Copyright Firaxis Games 2007
from CvPythonExtensions import *
import PyHelpers
import CvUtil
import Popup as PyPopup
import CvGameUtils
import ScreenInput
import CvScreenEnums
import pickle
gc = CyGlobalContext()

localText = CyTranslator()

PyPlayer = PyHelpers.PyPlayer

#PURCHASE_BASECOST = 1.2
PURCHASE_BONUS_MOD = 2.5
g_iNukesforVictory = 4

class BrokenStar:
		
	def __init__(self):
		
		self.iNetMessage_BuyUnit = 0
		self.iNetMessage_BuyPromotion = 1
		
		return
		
	def atGameStart(self):
		#print "Happening!"
		if CyGame().getGameTurn() == 0:
			CyGame().setGameTurn(1)
			#print "New Game Turn: ", CyGame().getGameTurn()	
		
		for iPlayer in range(gc.getMAX_PLAYERS()):
			player = gc.getPlayer(iPlayer)
			if (player.isAlive() and player.isHuman()):
				popupInfo = CyPopupInfo()
				popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON_SCREEN)
				popupInfo.setText(u"showDawnOfMan")
				popupInfo.addPopup(iPlayer)
				
		if gc.getGame().isPbem():
			for iPlayer in range(gc.getMAX_PLAYERS()):
				player = gc.getPlayer(iPlayer)
				if (player.isAlive() and player.isHuman()):
					popupInfo = CyPopupInfo()
					popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_DETAILS)
					popupInfo.setOption1(true)
					popupInfo.addPopup(iPlayer)
			
	def atBeginGameTurn(self, argsList):
		iGameTurn = argsList[0]		
		
		coalitionPlayer = 9
		iHasUNuke = 0
		iNukePerPlot = 0
		
		if iGameTurn == 1:
			if not CyGame().isGameMultiPlayer():
				CvGameUtils.CvGameUtils().addPopup(localText.getText("TXT_KEY_BROKEN_STAR_TUTORIAL_TITLE",()), localText.getText("TXT_KEY_BROKEN_STAR_TUTORIAL", (g_iNukesforVictory,g_iNukesforVictory)))
									
		for player in PyHelpers.PyGame().getCivPlayerList():
			if player.getID() != coalitionPlayer:
				iNukeCount = 0
				for unit in player.getUnitList():
					if(unit.getUnitType() == gc.getInfoTypeForString("UNIT_NUKE")):
						iNukeCount = iNukeCount + 1
#				print("%s has %d Nukes" %(gc.getPlayer(player.getID()).getName(), iNukeCount))
#				print("NukeCount = %d" %(iNukeCount))
				if (iNukeCount > 3):
					iPlayer = player.getID()
					pPlayer = gc.getPlayer(iPlayer)
					CyGame().setWinner(pPlayer.getTeam(), 7)
		
		for player in PyHelpers.PyGame().getCivPlayerList():
			if player.getID() != coalitionPlayer:
				for unit in player.getUnitList():
					if(unit.getUnitType() == gc.getInfoTypeForString("UNIT_UNARMED_NUKE")):
						iPlayerID = player.getID()
						pPlayerTeam = gc.getTeam(iPlayerID)
#						print("Player %d has an unarmed nuke" %(iPlayerID))
						if (pPlayerTeam.isAtWar(coalitionPlayer)):
							pCoalitionTeam = gc.getTeam(coalitionPlayer)
							pCoalitionTeam.setPermanentWarPeace(player.getID(), true)
							iHasUNuke = 1
#							print("Player %d cannot peace with %s" %(iPlayerID, gc.getPlayer(coalitionPlayer).getName()))
						else:
							pCoalitionTeam = gc.getTeam(coalitionPlayer)
							pCoalitionTeam.declareWar(player.getID(), true, WarPlanTypes.WARPLAN_DOGPILE)
							pCoalitionTeam.setPermanentWarPeace(player.getID(), true)
							iHasUNuke = 1
					else:
						iHasUNuke = 0
						
#				print("Player %d has %d nukes" %(player.getID(), iHasUNuke))				
		
				if(iHasUNuke < 1):			
					iPlayerID = player.getID()
					pCoalitionTeam = gc.getTeam(coalitionPlayer)
					pCoalitionTeam.setPermanentWarPeace(player.getID(), false)
#					print("Player %d CAN peace with %s" %(iPlayerID, gc.getPlayer(coalitionPlayer).getName()))
		
		for Player in range(gc.getMAX_PLAYERS()):
			#print "Player: ", Player
			if gc.getPlayer(Player).isAlive() and Player != 9:
				#print "Player is alive"
				for unit in PyPlayer(Player).getUnitList():
					#print "Cycling through units"
					if unit.getUnitType() == CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_UNARMED_NUKE'):
						#print "UNIT_UNARMED_NUKE is present"
						if unit.getScriptData() == "":
							turnsOwned = [1]
							unit.setScriptData(pickle.dumps(turnsOwned))
						else:
							turnsOwned = pickle.loads(unit.getScriptData())	
												
						if turnsOwned[0] < 24:
							turnsOwned[0] = turnsOwned[0] + 1	
							unit.setScriptData(pickle.dumps(turnsOwned))
							if turnsOwned[0] % 5 == 0:
								CvGameUtils.CvGameUtils().addPopup(localText.getText("TXT_KEY_BROKEN_STAR_WARNING",()), localText.getText("TXT_KEY_BROKEN_STAR_WARNING_MESSAGE",(25-turnsOwned[0], gc.getPlayer(Player).getName())))						
						else:
							szName = gc.getPlayer(Player).getName()
							CvGameUtils.CvGameUtils().addPopup(localText.getText("TXT_KEY_BROKEN_STAR_WARNING_NUKE_ACTIVATED",()), localText.getText("TXT_KEY_BROKEN_STAR_WARNING_NUKE_ACTIVATED_MESSAGE", (szName,)))
							xPos = unit.getX()
							yPos = unit.getY()
													
							unit.kill(0, Player)
							PyPlayer(Player).initUnit(CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_NUKE'),xPos,yPos, iNum = 1)					
			
		return
		
	def atBeginPlayerTurn(self, argsList):
		iGameTurn, iPlayer = argsList
		#print "Beginning Players Turn"
		cPlayer = gc.getPlayer(iPlayer)
		cTeam = gc.getTeam(iPlayer)
		warScriptData = [1]			
		spawnLocation = [-1,-1]
		iNukeCount = 0
		
		# randomly have the rebels attack the players
		randNum = CyGame().getSorenRandNum(100, "Random Rebel Attack")
		iRebelAttackRandomChancePercent = 10
		
		# reduce chance if single player game
		if not CyGame().isGameMultiPlayer():
			iRebelAttackRandomChancePercent = 8
		
		# rebel attacks only if the game turn is passed turn 15
		if randNum <= iRebelAttackRandomChancePercent and CyGame().getGameTurn() > 15:
			self.initRebelAttack()
			#CyInterface().addImmediateMessage("Rebel Attack Begun", "")
		
		if cTeam.isAtWar(9) == True and iPlayer != 8 and iPlayer != 18:
			if cPlayer.getScriptData() == "":
				
				cPlayer.setScriptData(pickle.dumps([1]))
			else: 
				warScriptData = pickle.loads(cPlayer.getScriptData())
				warScriptData[0] = warScriptData[0] + 1
				#print "You have been at war with 9 for: ", warScriptData[0], " turns."
				cPlayer.setScriptData(pickle.dumps(warScriptData))
			
			for unit in PyPlayer(iPlayer).getUnitList():
				if(unit.getUnitType() == gc.getInfoTypeForString("UNIT_UNARMED_NUKE")):
					iNukeCount += 1
									
			if(iNukeCount > 0):	
				if warScriptData[0] % 5 == 0:
					if iPlayer == 0:
						spawnLocation = [0,15]
					elif iPlayer == 1:
						spawnLocation = [0,20]
					elif iPlayer == 2:
						spawnLocation = [18,24]
					elif iPlayer == 3:
						spawnLocation = [16,0]
					elif iPlayer == 4:
						spawnLocation = [23,0]
					elif iPlayer == 5:
						spawnLocation = [37,0]
					elif iPlayer == 6 or iPlayer == 7:
						spawnLocation = [54,0]
					else:
						print "Could not successfully identify the current player.", iPlayer
				
				if(spawnLocation[0] >= 0):
					for numUnits in range(CyGame().getSorenRandNum(3, "Number of Units") + 1):
						unitNum = CyGame().getSorenRandNum(12, "Unit Type")
					
						if unitNum == 0 or unitNum == 1:
							PyPlayer(9).initUnit(CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_CHALLENGER2'),spawnLocation[0],spawnLocation[1], iNum = 1)
						elif unitNum == 2 or unitNum == 3 or unitNum == 4 or unitNum == 5 or unitNum == 6 or unitNum == 7:
							PyPlayer(9).initUnit(CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_RANGER'),spawnLocation[0],spawnLocation[1], iNum = 1)
						elif unitNum == 8 or unitNum == 9 or unitNum == 10 or unitNum == 11:
							PyPlayer(9).initUnit(CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_AA_INFANTRY'),spawnLocation[0],spawnLocation[1], iNum = 1)
		return		
			
	def atUnitCreated(self, argsList):
		unit = argsList[0]
		if -1 != CyGame().getActivePlayer() and gc.getPlayer(CyGame().getActivePlayer()).isAlive():
			if unit.getUnitType() == CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_UNARMED_NUKE') and unit.getOwner() != 9:
				CvGameUtils.CvGameUtils().addPopup(localText.getText("TXT_KEY_BROKEN_STAR_NUKE_ACQUIRED",()),localText.getText("TXT_KEY_BROKEN_STAR_NUKE_ACQUIRED_MESSAGE",()))
		return

	def initRebelAttack(self):
		MaxAttackers = 5
		
		iNumAttackers = CyGame().getSorenRandNum(MaxAttackers, "Number of Rebels")
		iPlayerAttack = CyGame().getSorenRandNum(8, "Player to be attacked")
		
		# if its a single player game then the player should be the one attacked
		if not CyGame().isGameMultiPlayer():
			for i in range(gc.getMAX_PLAYERS()):
				if gc.getPlayer(i).isHuman():
					iPlayerAttack = i
		
#		print iNumAttackers, iPlayerAttack
		
		if iNumAttackers > 0:
			player = PyPlayer(8)
			for city in player.getCityList():
				if self.checkRebelCityDistance(city, iPlayerAttack):
					self.spawnRebelUnits(city, player, iNumAttackers)
				
	def checkRebelCityDistance(self, pCity, iPlayerAttack):
		#print "checkRebelCityDistance"
		bCityClose = False
		player = PyPlayer(iPlayerAttack)
		
		# min distance the city has to be from the rebels for attack to happen
		CityDistanceRequirement = 10
		
		for unit in player.getUnitList():
			if stepDistance(pCity.getX(), pCity.getY(), unit.getX(), unit.getY()) <= CityDistanceRequirement:
				#print "city close enough"
				bCityClose = True
		
		return bCityClose
	
	def spawnRebelUnits(self, city, player, iNumAttackers):
		rebelUnitTypes = {	
						0: "UNIT_SAM_INFANTRY1",
						1: "UNIT_MARINE1",
						2: "UNIT_INFANTRY1",
						3: "UNIT_MECHANIZED_INFANTRY1",
					}
		#print "spawnRebelUnits"
		for i in range(iNumAttackers):
			iRandomUnitType = CyGame().getSorenRandNum(len(rebelUnitTypes), "Random Rebel Unit Type")
			player.initUnit( gc.getInfoTypeForString(rebelUnitTypes.get(iRandomUnitType)), city.getX(), city.getY() )
			
			newUnit = player.getUnitList()[len(player.getUnitList())-1]
			newUnit.getGroup().pushMission(MissionTypes.MISSION_MOVE_TO, city.getX(), city.getY(), 0, False, True, MissionAITypes.NO_MISSIONAI, city.plot(), newUnit)
			newUnit.setUnitAIType(UnitAITypes.UNITAI_ATTACK)
			
	def atChangeWar(self, argsList):
		'War Status Changes'
		bIsWar = argsList[0]
		iPlayer = argsList[1]
		iRivalTeam = argsList[2]
#		if iRivalTeam == 9 and (bIsWar) and gc.getActivePlayer() != 9 and CyGame().getGameTurn() > 1:
#			print "Game Turn = ", CyGame().getGameTurn()
#			CvGameUtils.CvGameUtils().addPopup(localText.getText("TXT_KEY_BROKEN_STAR_COALITION_WAR",()), localText.getText("TXT_KEY_BROKEN_STAR_COALITION_WAR_MESSAGE",())) 
		return

	def onModNetMessage(self, argsList):
		'Called whenever CyMessageControl().sendModNetMessage() is called - this is all for you modders!'
		
		iData1, iData2, iData3, iData4, iData5 = argsList
		
		iNetMessageType = iData1
		
		# Identify what this NetMessage is actually doing
		if (iNetMessageType == self.iNetMessage_BuyPromotion):
			
			iPlayer = iData2
			iUnitID = iData3
			self.promoteUnit(iPlayer, iUnitID)
			
		elif (iNetMessageType == self.iNetMessage_BuyUnit):
			
			iPlayer = iData2
			iUnitType = iData3
			
			self.purchaseUnit(iUnitType, iPlayer)
			
		
	def purchaseUnit(self, unitID, iPlayer):
		player = PyPlayer(iPlayer)
		capitalCityID = player.getCapitalCity().getID()
		capitalCityX = PyHelpers.PyCity(player.getID(), capitalCityID).getX()
		capitalCityY = PyHelpers.PyCity(player.getID(), capitalCityID).getY()
		
		# get cost, modified if the player doesn't have the resources
		cost = self.getPurchaseUnitCost(unitID, iPlayer)		

		gold = player.getGold()

		if gold >= cost:
			#iActivePlayer = CyGame().getActivePlayer()
			#if(iPlayer == iActivePlayer):
			pUnit = player.initUnit(unitID, capitalCityX, capitalCityY, iNum = 1)
			player.setGold(gold-cost)
			
			if iPlayer == CyGame().getActivePlayer():
				CvGameUtils.CvGameUtils().addPopup(localText.getText("TXT_KEY_BROKEN_STAR_UNIT_PURCHASED", ()), localText.getText("TXT_KEY_BROKEN_STAR_UNIT_PURCHASED_MESSAGE", (gc.getUnitInfo(unitID).getDescription(),cost)))
			
			# restrict units movement for 1 turn - call is for all players
			pUnit.setImmobileTimer(1)

		else:
			iActivePlayer = CyGame().getActivePlayer()
			if(iPlayer == iActivePlayer):
				CvGameUtils.CvGameUtils().addPopup(localText.getText("TXT_KEY_BROKEN_STAR_GOLD_NOT_ENOUGH", ()), localText.getText("TXT_KEY_BROKEN_STAR_GOLD_NOT_ENOUGH_MESSAGE", ()))
			
		return
		
	def getUnitPrereqBonusList(self, unitID):
		pUnitInfo = gc.getUnitInfo(unitID)
		bonusList = []
		
		# add AND bonus
		if pUnitInfo.getPrereqAndBonus() != -1:
			bonusList.append(pUnitInfo.getPrereqAndBonus())
		
		# add OR bonuses
		for i in range(gc.getNUM_UNIT_PREREQ_OR_BONUSES()):
			if pUnitInfo.getPrereqOrBonuses(i) != -1:
				bonusList.append(pUnitInfo.getPrereqOrBonuses(i))
		
		return bonusList

	def promoteUnit(self, iPlayer, iUnitID):
#		pHeadSelectedUnit = CyInterface().getHeadSelectedUnit()
#		pPlayer = gc.getPlayer(iPlayer)
		player = PyPlayer(iPlayer)
		pHeadSelectedUnit = gc.getPlayer(iPlayer).getUnit(iUnitID)
		
		cost = 75
		expBought = 5
		gold = player.getGold()
		if gold >= cost:
			pHeadSelectedUnit.changeExperience(expBought, 900, false, false, false)
			player.setGold(gold - cost)
			#CvGameUtils.CvGameUtils().addPopup("Experience",str(pHeadSelectedUnit.getExperience()))
			if pHeadSelectedUnit.getExperience() >= pHeadSelectedUnit.experienceNeeded():
				pHeadSelectedUnit.setPromotionReady(1)
						
		else:
#			print("Player is %d. Activate Player is %d. " %(iPlayer, CyGame().getActivePlayer()))
			iActivePlayer = CyGame().getActivePlayer()
			if(iPlayer == iActivePlayer):
				CvGameUtils.CvGameUtils().addPopup(localText.getText("TXT_KEY_BROKEN_STAR_GOLD_NOT_ENOUGH", ()), localText.getText("TXT_KEY_BROKEN_STAR_GOLD_NOT_ENOUGH_MESSAGE", ()))
#				CvGameUtils.CvGameUtils().addPopup("TXT_KEY_BROKEN_STAR_GOLD_NOT_ENOUGH", "TXT_KEY_BROKEN_STAR_GOLD_NOT_ENOUGH_MESSAGE")
			
		return
	
	def attackNuke(self, pUnit):
		closestNuke = 10000
		bestPlot = None
		coalitionPlayer = 9
		for player in PyHelpers.PyGame().getCivPlayerList():
			if player.getID() != coalitionPlayer:
				#print "Player %s and unitOwner %s" %(player, gc.getPlayer(pUnit.getOwner()))
				for unit in player.getUnitList():
					if unit.getUnitType() == CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_UNARMED_NUKE'):
						for i in range(DirectionTypes.NUM_DIRECTION_TYPES):
							pPlot = plotDirection(unit.getX(), unit.getY(), DirectionTypes(i))							
							if (not pPlot.isNone() and not pPlot.isVisibleEnemyDefender(pUnit)):
								iDistance = plotDistance(pPlot.getX(), pPlot.getY(), pUnit.getX(), pUnit.getY())
								if iDistance < closestNuke:
									closestNuke = iDistance
									bestPlot = pPlot

		if bestPlot	!= None and closestNuke > 0:						
			pUnit.getGroup().pushMission(MissionTypes.MISSION_MOVE_TO, bestPlot.getX(), bestPlot.getY(), 0, False, True, MissionAITypes.NO_MISSIONAI, bestPlot, pUnit) 
			#updates pUnit (ChallengerII, AAInfantry, or Ranger) with a goto mission sending it to attack the closest player controlled nuke. 
			#print "Unit is being sent to a nuke anyways."
			return true
		return false
	
	def atNukeExplosion(self, argsList):
		pPlot, pNukeUnit = argsList
		if pPlot != false and not pNukeUnit.isNone():
			pCity = pPlot.getPlotCity()
			pCity.kill()
		
		return
		
	def atUnitKilled(self, argsList):
		unit, iAttacker = argsList
		
		iNukePlotCount = 0
		
		iX = unit.getX()
		iY = unit.getY()
		pPlot = CyMap().plot(iX, iY)
		for iUnit in range(pPlot.getNumUnits()):
			if(pPlot.getUnit(iUnit).getUnitType() == gc.getInfoTypeForString("UNIT_UNARMED_NUKE") or pPlot.getUnit(iUnit).getUnitType() == gc.getInfoTypeForString("UNIT_NUKE")):
				if(iUnit == 0):	
					iNukePlotCount += 1
		if(iNukePlotCount > 0):
			PyPlayer(iAttacker).initUnit(CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_UNARMED_NUKE'),iX,iY, iNum = 1)
			print("There are %d Units on plot %d, %d" %(pPlot.getNumUnits(), iX, iY))
					
		if(unit.getUnitType() == gc.getInfoTypeForString("UNIT_UNARMED_NUKE")):
			if(iAttacker < 8):
				szName = gc.getPlayer(iAttacker).getName()
				szBuffer = localText.getText("TXT_KEY_BROKEN_STAR_WARNING_NUKE_ACQUIRED", (szName,))
				for iPlayerLoop in range(gc.getMAX_PLAYERS()):
					CyInterface().addMessage(iPlayerLoop, false, gc.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_MELTDOWN", InterfaceMessageTypes.MESSAGE_TYPE_INFO, gc.getUnitInfo(gc.getInfoTypeForString("UNIT_UNARMED_NUKE")).getButton() , gc.getInfoTypeForString("COLOR_RED"), unit.getX(), unit.getY(), true, true)
			
		if(unit.getUnitType() == gc.getInfoTypeForString("UNIT_NUKE")):
			if(iAttacker < 8):
				szName = gc.getPlayer(iAttacker).getName()
				szBuffer = localText.getText("TXT_KEY_BROKEN_STAR_WARNING_NUKE_ACQUIRED", (szName,))
				for iPlayerLoop in range(gc.getMAX_PLAYERS()):
					CyInterface().addMessage(iPlayerLoop, false, gc.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_MELTDOWN", InterfaceMessageTypes.MESSAGE_TYPE_INFO, gc.getUnitInfo(gc.getInfoTypeForString("UNIT_NUKE")).getButton() , gc.getInfoTypeForString("COLOR_RED"), unit.getX(), unit.getY(), true, true)
				
	def getPurchaseUnitCost(self, unitID, iPlayer):
		pPlayer = gc.getPlayer(iPlayer)
		
		# base amount
		cost = PyHelpers.PyInfo.UnitInfo(unitID).getProductionCost()
		pUnitInfo = gc.getUnitInfo(unitID)		
		
		
		if(pUnitInfo.getUnitClassType() == gc.getInfoTypeForString("UNITCLASS_GUNSHIP2")):
			baseCost = int(cost * 1.3)
		elif(pUnitInfo.getUnitClassType() == gc.getInfoTypeForString("UNITCLASS_GUNSHIP3")):
			baseCost = int(cost * 1.4)
		elif(pUnitInfo.getUnitClassType() == gc.getInfoTypeForString("UNITCLASS_GUNSHIP4")):
			baseCost = int(cost * 1.5)
		elif(pUnitInfo.getUnitClassType() == gc.getInfoTypeForString("UNITCLASS_JET_FIGHTER2")):
			baseCost = int(cost * 1.3)
		elif(pUnitInfo.getUnitClassType() == gc.getInfoTypeForString("UNITCLASS_JET_FIGHTER3")):
			baseCost = int(cost * 1.4)
		elif(pUnitInfo.getUnitClassType() == gc.getInfoTypeForString("UNITCLASS_JET_FIGHTER4")):
			baseCost = int(cost * 1.5)
		elif(pUnitInfo.getUnitClassType() == gc.getInfoTypeForString("UNITCLASS_STEALTH_BOMBER2")):
			baseCost = int(cost * 1.3)
		elif(pUnitInfo.getUnitClassType() == gc.getInfoTypeForString("UNITCLASS_STEALTH_BOMBER3")):
			baseCost = int(cost * 1.4)
		elif(pUnitInfo.getUnitClassType() == gc.getInfoTypeForString("UNITCLASS_STEALTH_BOMBER4")):
			baseCost = int(cost * 1.5)
		elif(pUnitInfo.getUnitClassType() == gc.getInfoTypeForString("UNITCLASS_INFANTRY2")):
			baseCost = int(cost * 1.3)
		elif(pUnitInfo.getUnitClassType() == gc.getInfoTypeForString("UNITCLASS_INFANTRY3")):
			baseCost = int(cost * 1.4)
		elif(pUnitInfo.getUnitClassType() == gc.getInfoTypeForString("UNITCLASS_INFANTRY4")):
			baseCost = int(cost * 1.5)
		elif(pUnitInfo.getUnitClassType() == gc.getInfoTypeForString("UNITCLASS_AT_INFANTRY2")):
			baseCost = int(cost * 1.3)
		elif(pUnitInfo.getUnitClassType() == gc.getInfoTypeForString("UNITCLASS_AT_INFANTRY3")):
			baseCost = int(cost * 1.4)
		elif(pUnitInfo.getUnitClassType() == gc.getInfoTypeForString("UNITCLASS_AT_INFANTRY4")):
			baseCost = int(cost * 1.5)
		elif(pUnitInfo.getUnitClassType() == gc.getInfoTypeForString("UNITCLASS_MARINE2")):
			baseCost = int(cost * 1.3)
		elif(pUnitInfo.getUnitClassType() == gc.getInfoTypeForString("UNITCLASS_MARINE3")):
			baseCost = int(cost * 1.4)
		elif(pUnitInfo.getUnitClassType() == gc.getInfoTypeForString("UNITCLASS_MARINE4")):
			baseCost = int(cost * 1.5)
		elif(pUnitInfo.getUnitClassType() == gc.getInfoTypeForString("UNITCLASS_SAM_INFANTRY2")):
			baseCost = int(cost * 1.3)
		elif(pUnitInfo.getUnitClassType() == gc.getInfoTypeForString("UNITCLASS_SAM_INFANTRY3")):
			baseCost = int(cost * 1.4)
		elif(pUnitInfo.getUnitClassType() == gc.getInfoTypeForString("UNITCLASS_SAM_INFANTRY4")):
			baseCost = int(cost * 1.5)
		elif(pUnitInfo.getUnitClassType() == gc.getInfoTypeForString("UNITCLASS_MECHANIZED_INFANTRY2")):
			baseCost = int(cost * 1.3)
		elif(pUnitInfo.getUnitClassType() == gc.getInfoTypeForString("UNITCLASS_MECHANIZED_INFANTRY3")):
			baseCost = int(cost * 1.4)
		elif(pUnitInfo.getUnitClassType() == gc.getInfoTypeForString("UNITCLASS_MECHANIZED_INFANTRY4")):
			baseCost = int(cost * 1.5)
		elif(pUnitInfo.getUnitClassType() == gc.getInfoTypeForString("UNITCLASS_MODERN_ARMOR2")):
			baseCost = int(cost * 1.3)
		elif(pUnitInfo.getUnitClassType() == gc.getInfoTypeForString("UNITCLASS_MODERN_ARMOR3")):
			baseCost = int(cost * 1.4)
		elif(pUnitInfo.getUnitClassType() == gc.getInfoTypeForString("UNITCLASS_MODERN_ARMOR4")):
			baseCost = int(cost * 1.5)
		elif(pUnitInfo.getUnitClassType() == gc.getInfoTypeForString("UNITCLASS_ARTILLERY2")):
			baseCost = int(cost * 1.3)
		elif(pUnitInfo.getUnitClassType() == gc.getInfoTypeForString("UNITCLASS_ARTILLERY3")):
			baseCost = int(cost * 1.4)
		elif(pUnitInfo.getUnitClassType() == gc.getInfoTypeForString("UNITCLASS_ARTILLERY4")):
			baseCost = int(cost * 1.5)
		elif(pUnitInfo.getUnitClassType() == gc.getInfoTypeForString("UNITCLASS_MOBILE_ARTILLERY2")):
			baseCost = int(cost * 1.3)
		elif(pUnitInfo.getUnitClassType() == gc.getInfoTypeForString("UNITCLASS_MOBILE_ARTILLERY3")):
			baseCost = int(cost * 1.4)
		elif(pUnitInfo.getUnitClassType() == gc.getInfoTypeForString("UNITCLASS_MOBILE_ARTILLERY4")):
			baseCost = int(cost * 1.5)
		elif(pUnitInfo.getUnitClassType() == gc.getInfoTypeForString("UNITCLASS_MOBILE_SAM2")):
			baseCost = int(cost * 1.3)
		elif(pUnitInfo.getUnitClassType() == gc.getInfoTypeForString("UNITCLASS_MOBILE_SAM3")):
			baseCost = int(cost * 1.4)
		elif(pUnitInfo.getUnitClassType() == gc.getInfoTypeForString("UNITCLASS_MOBILE_SAM4")):
			baseCost = int(cost * 1.5)
		elif(pUnitInfo.getUnitClassType() == gc.getInfoTypeForString("UNITCLASS_ATTACK_SUBMARINE2")):
			baseCost = int(cost * 1.3)
		elif(pUnitInfo.getUnitClassType() == gc.getInfoTypeForString("UNITCLASS_ATTACK_SUBMARINE3")):
			baseCost = int(cost * 1.4)
		elif(pUnitInfo.getUnitClassType() == gc.getInfoTypeForString("UNITCLASS_ATTACK_SUBMARINE4")):
			baseCost = int(cost * 1.5)
		elif(pUnitInfo.getUnitClassType() == gc.getInfoTypeForString("UNITCLASS_CARRIER2")):
			baseCost = int(cost * 1.3)
		elif(pUnitInfo.getUnitClassType() == gc.getInfoTypeForString("UNITCLASS_CARRIER3")):
			baseCost = int(cost * 1.4)
		elif(pUnitInfo.getUnitClassType() == gc.getInfoTypeForString("UNITCLASS_CARRIER4")):
			baseCost = int(cost * 1.5)
		elif(pUnitInfo.getUnitClassType() == gc.getInfoTypeForString("UNITCLASS_DESTROYER2")):
			baseCost = int(cost * 1.3)
		elif(pUnitInfo.getUnitClassType() == gc.getInfoTypeForString("UNITCLASS_DESTROYER3")):
			baseCost = int(cost * 1.4)
		elif(pUnitInfo.getUnitClassType() == gc.getInfoTypeForString("UNITCLASS_DESTROYER4")):
			baseCost = int(cost * 1.5)
		elif(pUnitInfo.getUnitClassType() == gc.getInfoTypeForString("UNITCLASS_SUBMARINE2")):
			baseCost = int(cost * 1.3)
		elif(pUnitInfo.getUnitClassType() == gc.getInfoTypeForString("UNITCLASS_SUBMARINE3")):
			baseCost = int(cost * 1.4)
		elif(pUnitInfo.getUnitClassType() == gc.getInfoTypeForString("UNITCLASS_SUBMARINE4")):
			baseCost = int(cost * 1.5)
		elif(pUnitInfo.getUnitClassType() == gc.getInfoTypeForString("UNITCLASS_TRANSPORT2")):
			baseCost = int(cost * 1.3)
		elif(pUnitInfo.getUnitClassType() == gc.getInfoTypeForString("UNITCLASS_TRANSPORT3")):
			baseCost = int(cost * 1.4)
		elif(pUnitInfo.getUnitClassType() == gc.getInfoTypeForString("UNITCLASS_TRANSPORT4")):
			baseCost = int(cost * 1.5)
		elif(pUnitInfo.getUnitClassType() == gc.getInfoTypeForString("UNITCLASS_STEALTH_DESTROYER2")):
			baseCost = int(cost * 1.3)
		elif(pUnitInfo.getUnitClassType() == gc.getInfoTypeForString("UNITCLASS_STEALTH_DESTROYER3")):
			baseCost = int(cost * 1.4)
		elif(pUnitInfo.getUnitClassType() == gc.getInfoTypeForString("UNITCLASS_STEALTH_DESTROYER4")):
			baseCost = int(cost * 1.5)
		else:		
			baseCost = int(cost * 1.2)

		# get number of prereq bonuses and adjust cost
		bonusList = self.getUnitPrereqBonusList(unitID)
		bNoResource = False
		if bonusList:
			for bonus in bonusList:
				if not pPlayer.hasBonus(bonus):
					bNoResource = True
			
		if bNoResource:
			baseCost *= PURCHASE_BONUS_MOD
		
		return int(baseCost)
