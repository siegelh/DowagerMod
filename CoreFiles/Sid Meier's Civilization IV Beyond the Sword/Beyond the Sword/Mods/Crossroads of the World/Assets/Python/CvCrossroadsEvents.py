# Crossroads of the World
# Civilization 4 (c) 2007 Firaxis Games

from CvPythonExtensions import *
import sys
import Popup as PyPopup
from PyHelpers import PyPlayer
import pickle
import CvEventManager
from CvScreenEnums import *
from PyHelpers import *
import CvUtil
import CvGameUtils

# globals
gc = CyGlobalContext()
localText = CyTranslator()

DefaultUnitAI = UnitAITypes.NO_UNITAI

g_iCaptureExecutiveGold = 1000
g_iGoldVictoryReq = 30000
g_iAIGoldPerTurnBonus = 130
g_iCaptureHeadquartersGold = 7500
g_VictoryThresholdsList = [150000, 20000, 22500, 25000, 275000]
g_iThresholdNum = 5

class CvCrossroadsEvents(CvEventManager.CvEventManager):
	
	def __init__(self):
		
		self.parent = CvEventManager.CvEventManager
		self.parent.__init__(self)
		
		
	def onGameStart(self, argsList):
		'Called at the start of the game'
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
					
					
	def onUnitKilled(self, argsList):
		'Unit Killed'
		self.parent.onUnitKilled(self, argsList)
		pUnit, iAttacker = argsList
		
		pUnitInfo = gc.getUnitInfo(pUnit.getUnitType())
		iMerchant = gc.getInfoTypeForString("UNIT_MERCHANT")
		
		# Loop through to see if this unit can spread any corporation (is it an executive)
		for iCorpLoop in range(gc.getNumCorporationInfos()):
			
			if (pUnitInfo.getCorporationSpreads(iCorpLoop) > 0):
				
				pPlayer = gc.getPlayer(iAttacker)
				
				if(pPlayer.isHuman()):
					
					# Change amount of gold for player
					pPlayer.changeGold(g_iCaptureExecutiveGold)
					
					szBuffer = localText.getText("TXT_KEY_XROADS_MERCHANT_CAPTURE", ())
					CyInterface().addMessage(iAttacker, false, gc.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_BUILD_BANK", InterfaceMessageTypes.MESSAGE_TYPE_INFO, "", gc.getInfoTypeForString("COLOR_YELLOW"), -1, -1, false, false)
	
				# Don't process any more corporations, we already know this is an executive
				break
			
		if ((pUnit.getUnitType()) == iMerchant):
			
			pPlayer = gc.getPlayer(iAttacker)
			
			if(pPlayer.isHuman()):
			
				pPlayer.changeGold(g_iCaptureExecutiveGold)
				
				szBuffer = localText.getText("TXT_KEY_XROADS_MERCHANT_CAPTURE", ())
				CyInterface().addMessage(iAttacker, false, gc.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_BUILD_BANK", InterfaceMessageTypes.MESSAGE_TYPE_INFO, "", gc.getInfoTypeForString("COLOR_YELLOW"), -1, -1, false, false)
				
	def onCityAcquired(self, argsList):
		'City Acquired'
		self.parent.onCityAcquired(self, argsList)
		iPreviousOwner,iNewOwner,pCity,bConquest,bTrade = argsList
		CvUtil.pyPrint('City Acquired Event: %s' %(pCity.getName()))
		
		pPlayer = gc.getPlayer(iNewOwner)
		if (bConquest):
			if (pCity.isHeadquarters()):
				if(pPlayer.isHuman()):
					pPlayer.changeGold(g_iCaptureHeadquartersGold)
					print('Headquarters Captured!: %s' %(pCity.getName()))
			
	def onEndGameTurn(self, argsList):
		'Called at the end of the end of each turn'
		iGameTurn = argsList[0]
		
		if((iGameTurn % 5) == 0):
			for iPlayerLoop in range(gc.getMAX_CIV_PLAYERS()):
				pPlayer = gc.getPlayer(iPlayerLoop)
				iPlayerGold = pPlayer.getGold()
				#if(pPlayer.isAlive()):
				if(iPlayerGold > (g_iGoldVictoryReq * .75)):
					print("Player %d has %d gold" %(iPlayerLoop, iPlayerGold))
					iRandMajor = CyGame().getSorenRandNum(5, "Player Type")
					pPlayerWar = gc.getPlayer(iRandMajor)
					print("The Random Killer will be %s" %(pPlayerWar.getName()))
					if(pPlayerWar.isAlive() and not pPlayerWar.isHuman() and not pPlayerWar.isBarbarian()):
						if(pPlayerWar.getTeam() != pPlayer.getTeam()):
							pPlayerWar.AI_changeAttitudeExtra(pPlayer.getTeam(), -10)
							gc.getTeam(pPlayerWar.getTeam()).declareWar(pPlayer.getTeam(), true, WarPlanTypes.WARPLAN_TOTAL)
							print("%s is declaring war against %s" %(pPlayerWar.getName(), pPlayer.getName()))
		
		if(CyGame().getWinner() < 0):
			for iPlayerLoop in range(gc.getMAX_CIV_PLAYERS()):
				pPlayer = gc.getPlayer(iPlayerLoop)
				if (pPlayer.isAlive() and not pPlayer.isBarbarian()): 
					iGold = pPlayer.getGold()
#					print("Player %d has %d gold. The victory goal is %d" %(iPlayerLoop, iGold, g_iGoldVictoryReq))
					if(iGameTurn < 201):
						if (pPlayer.getGold() >=  g_iGoldVictoryReq):
							CyGame().setWinner(pPlayer.getTeam(), 6)
							print("Winner: %d" %(iPlayerLoop))
						else:	
							if (pPlayer.isAlive() and not pPlayer.isHuman() and not pPlayer.isBarbarian()):
								pPlayer.setGold(pPlayer.getGold() + g_iAIGoldPerTurnBonus)
	
	def onCorporationSpread(self, argsList):
		'Corporation Has Spread to a City'
		self.parent.onCorporationSpread(self, argsList)
		iCorporation, iOwner, pSpreadCity = argsList
		
		for iPlayerLoop in range(gc.getMAX_CIV_PLAYERS()):
			if(gc.getPlayer(iPlayerLoop).hasHeadquarters(iCorporation)):
				szBuffer = localText.getText("", ())
				CyInterface().addMessage(iPlayerLoop, false, gc.getEVENT_MESSAGE_TIME(), szBuffer, "", InterfaceMessageTypes.MESSAGE_TYPE_INFO, gc.getCorporationInfo(iCorporation).getButton() , gc.getInfoTypeForString("COLOR_GREEN"), pSpreadCity.getX(), pSpreadCity.getY(), true, true)
			else:
				szBuffer = localText.getText("TXT_KEY_MISC_CORPORATION_SPREAD", (gc.getCorporationInfo(iCorporation).getDescription(), pSpreadCity.getNameKey()))
				CyInterface().addMessage(iPlayerLoop, false, gc.getEVENT_MESSAGE_TIME(), szBuffer, "AS2D_BUILD_BANK", InterfaceMessageTypes.MESSAGE_TYPE_INFO, gc.getCorporationInfo(iCorporation).getButton() , gc.getInfoTypeForString("COLOR_GREEN"), pSpreadCity.getX(), pSpreadCity.getY(), true, true)
	

	def onBeginGameTurn(self, argsList):
		'Called at the beginning of the end of each turn'
		self.parent.onBeginGameTurn(self, argsList)
		iGameTurn = argsList[0]
		
		if(iGameTurn == 1):
			if not CyGame().isGameMultiPlayer():
				szTitle = localText.getText("TXT_KEY_CROSSROADS_HINTS_TITLE", ())
				szText = localText.getText("TXT_KEY_CROSSROADS_HINTS", ())
				CvGameUtils.CvGameUtils().addPopup(szTitle, szText)
			
		self.m_playerThreshold = []
		self.m_playerDisplays = []
		

		if(CyGame().getWinner() < 0):
			#Messaging System
			for iIndexLoop in range(gc.getMAX_CIV_PLAYERS()):
				self.m_playerThreshold.append(iIndexLoop)
				self.m_playerDisplays.append(iIndexLoop)
				self.m_playerDisplays[iIndexLoop] = -1
#				print("The value of playerdisplays is %d" %(self.m_playerDisplays[iIndexLoopA]))
	
			for iPlayerLoop in range(gc.getMAX_CIV_PLAYERS()):
				pPlayer = gc.getPlayer(iPlayerLoop)
				self.m_playerThreshold[iPlayerLoop] = pPlayer.getGold()
			
			for iPlayerLoopA in range(gc.getMAX_CIV_PLAYERS()):
				for iThresholdLoop in range(g_iThresholdNum):
					print("Player %u has %u gold" %(iPlayerLoopA, self.m_playerThreshold[iPlayerLoopA]))
					if(gc.getPlayer(iPlayerLoopA).isAlive()):
						if(self.m_playerThreshold[iPlayerLoopA] <= g_iGoldVictoryReq):
							if (self.m_playerThreshold[iPlayerLoopA] >= g_VictoryThresholdsList[iThresholdLoop]):
								self.m_playerDisplays[iPlayerLoopA] = iPlayerLoopA
#								print ("The current threshold victory is number %d, which is %d" %(iThresholdLoop, g_VictoryThresholdsList[iThresholdLoop]))
#								print ("The value of PlayerDisplays[%d] at this point is %d" %(iPlayerLoopA, self.m_playerDisplays[iPlayerLoopA]))		
			
			for iPlayerLoop in self.m_playerDisplays:
#				pPlayerDisplay = gc.getPlayer(self.m_playerDisplays[iPlayerLoop])
				if (((iGameTurn)% 5) == 0):
#					if(gc.getPlayer(iPlayerLoop).isAlive()):
					if (CyGame().getActivePlayer() != iPlayerLoop and CyGame().getActivePlayer() != -1):
						if (self.m_playerDisplays[iPlayerLoop] >= 0):
							iPlayerID = self.m_playerDisplays[iPlayerLoop]
#							print("The Player being displayed is %d" %(iPlayerID))
							pPlayer = gc.getPlayer(iPlayerID)
#							print("Player ID bottom is %s" %(pPlayer.getName()))
							strPlayer = pPlayer.getName()
							iPlayerGold = g_iGoldVictoryReq - (pPlayer.getGold())
							szTitle = localText.getText("TXT_KEY_ENEMY_GOLD_UPDATE_TITLE", ())
							szText = localText.getText("TXT_KEY_ENEMY_GOLD_UPDATE", (strPlayer, iPlayerGold))
#							print("Player name is totally %s and has %d gold" %(strPlayer, iPlayerGold))
							CvGameUtils.CvGameUtils().addPopup(szTitle, szText)
#							print("Humans rock!")

