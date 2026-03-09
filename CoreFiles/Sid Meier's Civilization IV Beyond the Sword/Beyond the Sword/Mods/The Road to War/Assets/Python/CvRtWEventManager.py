## Sid Meier's Civilization 4
## Copyright Firaxis Games 2005
## 
## CvRtWEventManager


from CvPythonExtensions import *
from CvScreenEnums import *
from PyHelpers import PyPlayer
import CvEventManager
import CvUtil
import Popup as PyPopup
import pickle
import sys
import CvWonderMovieScreen

gc = CyGlobalContext()
localText = CyTranslator()
DefaultUnitAI = UnitAITypes.NO_UNITAI
#########   AIAutoPlay - Delete when finished
game = CyGame()
#########   AIAutoPlay - Delete when finished

import CvRtWGlobal
rtwglobal = CvRtWGlobal.CvRtWGlobal()

# The main bits
###################################################
class CvRtWEventManager:
	def __init__(self):
                # Load variables
                self.initValues()
                
#########   AIAutoPlay - Delete when finished
                CvUtil.pyPrint("Initializing AIAutoPlay Mod")
                self.LOG_DEBUG = False
                self.SHOW_NEW_LEADER_POPUP = True
                self.blockPopups = True
                self.EventKeyDown=6
                self.TurnsToAuto = 10
                self.toAIChooserPopup = 7000
                self.abdicatePopup = 7001
                self.playerID = 0
                self.AutoCounter = 0
                self.bAutoMoves = False
                # These settings don't work currently
                self.bPause = False
                self.bPauseEveryTen = False
                self.bWakeOnWar = False
                self.bWakeOnVic = True
                self.AutoTypes={
                    0 : 'No automation',
                    1 : 'Fully Automate',
                    }
#########   AIAutoPlay - Delete when finished

# RtW Event Manager
###################################################
	def turnChecker(self, iTurn):
		# Insert all game turn events here
		# Victory check
		if (self.endGame == 0):
                    if (self.HistEvents == 0 or self.HistEvents == 1):
                            if (self.Map == 0 or self.Map == 2 or self.Map == 4):
                                if (gc.getTeam(gc.getPlayer(self.pGermanyID).getTeam()).isAlive() == 0):
                                        game.setWinner(gc.getTeam(gc.getPlayer(self.pEnglandID).getTeam()).getID(), 2)
                                        self.doVictory(true)
                                if (gc.getTeam(gc.getPlayer(self.pEnglandID).getTeam()).isAlive() == 0):
                                        game.setWinner(gc.getTeam(gc.getPlayer(self.pGermanyID).getTeam()).getID(), 2)
                                        self.doVictory(false)
                            if (self.Map == 1):
                                if (gc.getTeam(gc.getPlayer(self.pJapanID).getTeam()).isAlive() == 0):
                                        game.setWinner(gc.getTeam(gc.getPlayer(self.pEnglandID).getTeam()).getID(), 2)
                                        self.doVictory(true)
                                if (gc.getTeam(gc.getPlayer(self.pEnglandID).getTeam()).isAlive() == 0):
                                        game.setWinner(gc.getTeam(gc.getPlayer(self.pJapanID).getTeam()).getID(), 2)
                                        self.doVictory(false)
                # Game mode choice
		if (iTurn == 1 + self.iTurnOffset):
                        if (self.Map < 99 and self.HistEvents > 2):
                            if (gc.getPlayer(gc.getGame().getActivePlayer()).isHuman()):
                                game.setChangeCiv(0)
                                self.Jan2_1936()

		# Check Bitter Winter
		if (self.isBitterWinterTurn(iTurn)):
                        if (self.Map == 0 or self.Map == 2 or self.Map == 4):
                                self.doBitterWinter(true)
                else:
                        self.doBitterWinter(false)
                # Vichy France trigger
		if (game.getVichyHappened() == 0):
                        if (self.Map == 0 or self.Map == 2 or self.Map == 4):
                                if (self.HistEvents == 0 or self.HistEvents == 1):
                                        if (self.getFrenchAxisCities() > self.numFrenchCitiesFall):
                                                self.EVichy()
                # Fighters
                for i in range(gc.getMAX_CIV_PLAYERS()):
                        self.doAIWarPlans(i)
                        if (self.Map < 99):
                            self.buildFighter(i)

                # Historical events
                if (iTurn == self.Event1 + self.iTurnOffset):
                        if(self.Map == 0 or self.Map == 2 or self.Map == 4):
                            self.ESep1_1939()
                        if(self.Map == 1):
                            self.AJul1_1937()
                        if(self.Map == 3):
                            rtwglobal.doEvent(1)
                        if(self.Map == 5):
                            self.ADec1_1941()
                if (iTurn == self.Event2 + self.iTurnOffset):
                        if(self.Map == 0 or self.Map == 2 or self.Map == 4):
                            self.ESep2_1939()
                        if(self.Map == 1):
                            self.ASep2_1940()
                        if(self.Map == 3):
                            rtwglobal.doEvent(2)
                        if(self.Map == 5):
                            self.AAug1_1945()
                if (iTurn == self.Event3 + self.iTurnOffset):
                        if(self.Map == 0 or self.Map == 2 or self.Map == 4):
                            self.ENov2_1939()
                        if(self.Map == 1):
                            self.ADec1_1941()
                        if(self.Map == 3):
                            rtwglobal.doEvent(3)
                if (iTurn == self.Event4 + self.iTurnOffset):
                        if(self.Map == 0 or self.Map == 2 or self.Map == 4):
                            self.EMar1_1940()
                        if(self.Map == 1):
                            self.AAug1_1945()
                        if(self.Map == 3):
                            rtwglobal.doEvent(4)
                if (iTurn == self.Event5 + self.iTurnOffset):
                        if(self.Map == 0 or self.Map == 2 or self.Map == 4):
                            self.EApr1_1940()
                        if(self.Map == 1):
                            self.testMsg()
                        if(self.Map == 3):
                            rtwglobal.doEvent(5)
                if (iTurn == self.Event6 + self.iTurnOffset):
                        if(self.Map == 0 or self.Map == 2 or self.Map == 4):
                            self.EMay1_1940()
                        if(self.Map == 1):
                            self.testMsg()
                        if(self.Map == 3):
                            rtwglobal.doEvent(6)
                if (iTurn == self.Event7 + self.iTurnOffset):
                        if(self.Map == 0 or self.Map == 2 or self.Map == 4):
                            self.EJun1_1940()
                        if(self.Map == 1):
                            self.testMsg()
                        if(self.Map == 3):
                            rtwglobal.doEvent(7)
                if (iTurn == self.Event8 + self.iTurnOffset):
                        if(self.Map == 0 or self.Map == 2 or self.Map == 4):
                            self.EJul2_1940()
                        if(self.Map == 1):
                            self.testMsg()
                        if(self.Map == 3):
                            rtwglobal.doEvent(8)
                if (iTurn == self.Event9 + self.iTurnOffset):
                        if(self.Map == 0 or self.Map == 2 or self.Map == 4):
                            self.EOct1_1940()
                        if(self.Map == 1):
                            self.testMsg()
                        if(self.Map == 3):
                            rtwglobal.doEvent(9)
                if (iTurn == self.Event10 + self.iTurnOffset):
                        if(self.Map == 0 or self.Map == 2 or self.Map == 4):
                            self.EOct2_1940()
                        if(self.Map == 1):
                            self.testMsg()
                        if(self.Map == 3):
                            rtwglobal.doEvent(10)
                if (iTurn == self.Event11 + self.iTurnOffset):
                        if(self.Map == 0 or self.Map == 2 or self.Map == 4):
                            self.EJun2_1941()
                        if(self.Map == 1):
                            self.testMsg()
                        if(self.Map == 3):
                            rtwglobal.doEvent(11)
                if (iTurn == self.Event12 + self.iTurnOffset):
                        if(self.Map == 1):
                            self.testMsg()
                        if(self.Map == 3):
                            rtwglobal.doEvent(12)
                if (iTurn == self.Event13 + self.iTurnOffset):
                        if(self.Map == 0 or self.Map == 2 or self.Map == 4):
                            self.EDec1_1941()
                        if(self.Map == 1):
                            self.testMsg()
                        if(self.Map == 3):
                            rtwglobal.doEvent(13)
                if (iTurn == self.Event14 + self.iTurnOffset):
                        if(self.Map == 0 or self.Map == 2 or self.Map == 4):
                            self.EApr1_1939()
                        if(self.Map == 3):
                            rtwglobal.doEvent(14)
                if (iTurn == self.Event15 + self.iTurnOffset):
                        if(self.Map == 0 or self.Map == 2 or self.Map == 4):
                            self.EJul2_1936()
                        if(self.Map == 3):
                            rtwglobal.doEvent(15)
                if (iTurn == self.Event16 + self.iTurnOffset):
                        if(self.Map == 0 or self.Map == 2 or self.Map == 4):
                            self.EMar1_1938()
                        if(self.Map == 3):
                            rtwglobal.doEvent(16)
                if (iTurn == self.Event17 + self.iTurnOffset):
                        if(self.Map == 0 or self.Map == 2 or self.Map == 4):
                            self.ESep2_1938()
                        if(self.Map == 3):
                            rtwglobal.doEvent(17)
                if (iTurn == self.Event18 + self.iTurnOffset):
                        if(self.Map == 3):
                            rtwglobal.doEvent(18)
                if (iTurn == self.Event19 + self.iTurnOffset):
                        if(self.Map == 3):
                            rtwglobal.doEvent(19)

# RtW Event Scripts
###################################################

        def testMsg(self):
                # Test msg
                popup = PyPopup.PyPopup(-1)
                szTitle = localText.getText("TXT_KEY_WW2_TEST_TITLE", ())
                szText = localText.getText("TXT_KEY_WW2_TEST_TEXT", ())
                popup.setHeaderString(szTitle)
                popup.addSeparator()
                popup.setBodyString(szText)
                popup.launch()

        def Jan1_1936(self):
                # Intro Text
                popup = PyPopup.PyPopup(-1)
                szTitle = localText.getText("TXT_KEY_WW2_JAN1_1936_TITLE", ())
                szText = localText.getText("TXT_KEY_WW2_JAN1_1936_TEXT2", ())
                popup.setHeaderString(szTitle)
                popup.addSeparator()
                popup.setBodyString(szText)
                popup.launch()

        def Jan2_1936(self):
                # January 1936 week 2
                popup = PyPopup.PyPopup(CvUtil.EventJan2_1936Popup, contextType = EventContextTypes.EVENTCONTEXT_ALL)
                szTitle = localText.getText("TXT_KEY_WW2_JAN2_1936_TITLE", ())
                szText = localText.getText("TXT_KEY_WW2_JAN2_1936_TEXTB", ())
                popup.setHeaderString(szTitle)
                popup.addSeparator()
                popup.setBodyString(szText)
                popup.addSeparator()
                popup.addButton(localText.getText("TXT_KEY_POPUP_HIST1", ()))
                popup.addButton(localText.getText("TXT_KEY_POPUP_HIST2", ()))
                popup.addButton(localText.getText("TXT_KEY_POPUP_HIST3", ()))
                popup.launch(False)

        def Jan2_1936Handler(self, playerID, netUserData, popupReturn):
                autoIdx = popupReturn.getButtonClicked()
                if(autoIdx == 0):
                        self.HistEvents = 0 # True events
                elif(autoIdx == 1):
                        self.HistEvents = 1 # Rand events
                elif(autoIdx == 2):
                        self.HistEvents = 2 # No events
                        self.resetWarPeace()
                        self.giveSettlerTech()
                game.setHistoryEvents(self.HistEvents)
                self.initEvents()

# RtW Europe 1936 Event Scripts
###################################################
        def doBitterWinter(self, value):
                # Send off to do Bitter Winter
                game.setBitterWinter(value)

        def EVichy(self):
                # Send off to do Vichy France and notify player
                gc.getPlayer(self.pFranceID).doVichyFrance(6, 23, 23, 6)
                popup = PyPopup.PyPopup(-1)
                szTitle = localText.getText("TXT_KEY_WW2_VICHY_TITLE", ())
                szText = localText.getText("TXT_KEY_WW2_VICHY_TEXT", ())
                popup.setHeaderString(szTitle)
                popup.addSeparator()
                popup.setBodyString(szText)
                popup.launch()
                self.pGermanyTeam.addTeam(gc.getPlayer(self.pVichyID).getTeam())
                game.setVichyHappened(2)

        def EJul2_1936(self):
                # Spanish Civil War
                gc.getPlayer(self.pRiberiaID).doSpanishWar(17, 24, 24, 16)
                popup = PyPopup.PyPopup(-1)
                szTitle = localText.getText("TXT_KEY_WW2_EJUL2_1936_TITLE", ())
                szText = localText.getText("TXT_KEY_WW2_EJUL2_1936_TEXT", ())
                popup.setHeaderString(szTitle)
                popup.addSeparator()
                popup.setBodyString(szText)
                popup.launch()
                self.resetTrueWarPeace()
                self.pRiberiaTeam.declareWar(self.pNiberiaID, false, WarPlanTypes.WARPLAN_TOTAL)

        def EMar1_1938(self):
                # Anschluss
                popup = PyPopup.PyPopup(-1)
                szTitle = localText.getText("TXT_KEY_WW2_EMAR1_1938_TITLE", ())
                szText = localText.getText("TXT_KEY_WW2_EMAR1_1938_TEXT", ())
                popup.setHeaderString(szTitle)
                popup.addSeparator()
                popup.setBodyString(szText)
                popup.launch()
                gc.getPlayer(self.pAustriaID).doAnnexation(self.pGermanyID)

        def ESep2_1938(self):
                # Munich Agreement
                popup = PyPopup.PyPopup(-1)
                szTitle = localText.getText("TXT_KEY_WW2_ESEP2_1938_TITLE", ())
                szText = localText.getText("TXT_KEY_WW2_ESEP2_1938_TEXT", ())
                popup.setHeaderString(szTitle)
                popup.addSeparator()
                popup.setBodyString(szText)
                popup.launch()
                gc.getPlayer(self.pCzechID).doAnnexation(self.pGermanyID)

        def EApr1_1939(self):
                # Italy DOW Albania
                popup = PyPopup.PyPopup(-1)
                szTitle = localText.getText("TXT_KEY_WW2_EAPR1_1939_TITLE", ())
                szText = localText.getText("TXT_KEY_WW2_EAPR1_1939_TEXT", ())
                popup.setHeaderString(szTitle)
                popup.addSeparator()
                popup.setBodyString(szText)
                popup.launch()
                self.pItalyTeam.declareWar(self.pAlbaniaID, false, WarPlanTypes.WARPLAN_TOTAL)

        def ESep1_1939(self):
                # Cutscene movie
#       		popupInfo = CyPopupInfo()
#                popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON_SCREEN)
#       		popupInfo.setData1(0)
#                popupInfo.setData2(0)
#       		popupInfo.setData3(4)
#       		popupInfo.setText(u"showWonderMovie")
#       		for i in range(gc.getMAX_CIV_PLAYERS()):
#       		    if (gc.getPlayer(i).isAlive()):
#                        if(gc.getPlayer(i).isHuman()):
#                            popupInfo.addPopup(i)
                # Germany DOW Poland
                popup = PyPopup.PyPopup(-1)
                szTitle = localText.getText("TXT_KEY_WW2_ESEP1_1939_TITLE", ())
                szText = localText.getText("TXT_KEY_WW2_ESEP1_1939_TEXT", ())
                popup.setHeaderString(szTitle)
                popup.addSeparator()
                popup.setBodyString(szText)
                popup.launch()
                self.pGermanyTeam.declareWar(self.pPolandID, false, WarPlanTypes.WARPLAN_TOTAL)
                self.pEnglandTeam.declareWar(self.pGermanyID, false, WarPlanTypes.WARPLAN_TOTAL)
                self.pEnglandTeam.addTeam(gc.getPlayer(self.pFranceID).getTeam())
                self.pFranceTeam = gc.getTeam(gc.getPlayer(self.pFranceID).getTeam())
                self.pEnglandTeam.addTeam(gc.getPlayer(self.pCanadaID).getTeam())
                self.pCanadaTeam = gc.getTeam(gc.getPlayer(self.pCanadaID).getTeam())

        def ESep2_1939(self):
                # USSR DOW Poland
                popup = PyPopup.PyPopup(-1)
                szTitle = localText.getText("TXT_KEY_WW2_ESEP2_1939_TITLE", ())
                szText = localText.getText("TXT_KEY_WW2_ESEP2_1939_TEXT", ())
                popup.setHeaderString(szTitle)
                popup.addSeparator()
                popup.setBodyString(szText)
                popup.launch()
                self.pUSSRTeam.declareWar(self.pPolandID, false, WarPlanTypes.WARPLAN_TOTAL)

        def ENov2_1939(self):
                # USSR DOW Finland
                popup = PyPopup.PyPopup(-1)
                szTitle = localText.getText("TXT_KEY_WW2_ENOV2_1939_TITLE", ())
                szText = localText.getText("TXT_KEY_WW2_ENOV2_1939_TEXT", ())
                popup.setHeaderString(szTitle)
                popup.addSeparator()
                popup.setBodyString(szText)
                popup.launch()
                self.pUSSRTeam.declareWar(self.pFinlandID, false, WarPlanTypes.WARPLAN_TOTAL)

        def EMar1_1940(self):
                # USSR Peace Finland
                popup = PyPopup.PyPopup(-1)
                szTitle = localText.getText("TXT_KEY_WW2_EMAR1_1940_TITLE", ())
                szText = localText.getText("TXT_KEY_WW2_EMAR1_1940_TEXT", ())
                popup.setHeaderString(szTitle)
                popup.addSeparator()
                popup.setBodyString(szText)
                popup.launch()
                self.pUSSRTeam.makePeace(gc.getPlayer(self.pFinlandID).getTeam())

        def EApr1_1940(self):
                # Germany DOW Scandinavia
                popup = PyPopup.PyPopup(-1)
                szTitle = localText.getText("TXT_KEY_WW2_EAPR1_1940_TITLE", ())
                szText = localText.getText("TXT_KEY_WW2_EAPR1_1940_TEXT", ())
                popup.setHeaderString(szTitle)
                popup.addSeparator()
                popup.setBodyString(szText)
                popup.launch()
                self.pGermanyTeam.declareWar(self.pScandinaviaID, false, WarPlanTypes.WARPLAN_TOTAL)
                self.pEnglandTeam.addTeam(gc.getPlayer(self.pScandinaviaID).getTeam())
                self.pScandinaviaTeam = gc.getTeam(gc.getPlayer(self.pScandinaviaID).getTeam())

        def EMay1_1940(self):
                # Germany DOW Lowlands
                popup = PyPopup.PyPopup(-1)
                szTitle = localText.getText("TXT_KEY_WW2_EMAY1_1940_TITLE", ())
                szText = localText.getText("TXT_KEY_WW2_EMAY1_1940_TEXT", ())
                popup.setHeaderString(szTitle)
                popup.addSeparator()
                popup.setBodyString(szText)
                popup.launch()
                self.pGermanyTeam.declareWar(self.pLowlandsID, false, WarPlanTypes.WARPLAN_TOTAL)
                self.pEnglandTeam.addTeam(gc.getPlayer(self.pLowlandsID).getTeam())
                self.pLowlandsTeam = gc.getTeam(gc.getPlayer(self.pLowlandsID).getTeam())

        def EJun1_1940(self):
                # Italy DOW Allies; Italy Ally Germany
                popup = PyPopup.PyPopup(-1)
                szTitle = localText.getText("TXT_KEY_WW2_EJUN1_1940_TITLE", ())
                szText = localText.getText("TXT_KEY_WW2_EJUN1_1940_TEXT", ())
                popup.setHeaderString(szTitle)
                popup.addSeparator()
                popup.setBodyString(szText)
                popup.launch()
                self.pItalyTeam.declareWar(self.pEnglandID, false, WarPlanTypes.WARPLAN_TOTAL)
                self.pGermanyTeam.addTeam(gc.getPlayer(self.pItalyID).getTeam())
                self.pItalyTeam = gc.getTeam(gc.getPlayer(self.pItalyID).getTeam())

        def EJul2_1940(self):
                # USSR DOW Baltic
                popup = PyPopup.PyPopup(-1)
                szTitle = localText.getText("TXT_KEY_WW2_EJUL2_1940_TITLE", ())
                szText = localText.getText("TXT_KEY_WW2_EJUL2_1940_TEXT", ())
                popup.setHeaderString(szTitle)
                popup.addSeparator()
                popup.setBodyString(szText)
                popup.launch()
                self.pUSSRTeam.declareWar(self.pBalticID, false, WarPlanTypes.WARPLAN_TOTAL)

        def EOct1_1940(self):
                # East Balkan Ally Axis
                popup = PyPopup.PyPopup(-1)
                szTitle = localText.getText("TXT_KEY_WW2_EOCT1_1940_TITLE", ())
                szText = localText.getText("TXT_KEY_WW2_EOCT1_1940_TEXT", ())
                popup.setHeaderString(szTitle)
                popup.addSeparator()
                popup.setBodyString(szText)
                popup.launch()
                self.pGermanyTeam.addTeam(gc.getPlayer(self.pBalkanID).getTeam())
                self.pBalkanTeam = gc.getTeam(gc.getPlayer(self.pBalkanID).getTeam())
                self.pGermanyTeam.addTeam(gc.getPlayer(self.pRomaniaID).getTeam())
                self.pRomaniaTeam = gc.getTeam(gc.getPlayer(self.pRomaniaID).getTeam())

        def EOct2_1940(self):
                # Axis DOW West Balkan
                popup = PyPopup.PyPopup(-1)
                szTitle = localText.getText("TXT_KEY_WW2_EOCT2_1940_TITLE", ())
                szText = localText.getText("TXT_KEY_WW2_EOCT2_1940_TEXT", ())
                popup.setHeaderString(szTitle)
                popup.addSeparator()
                popup.setBodyString(szText)
                popup.launch()
                self.pGermanyTeam.declareWar(self.pWBalkanID, false, WarPlanTypes.WARPLAN_TOTAL)
                self.pEnglandTeam.addTeam(gc.getPlayer(self.pWBalkanID).getTeam())
                self.pWBalkanTeam = gc.getTeam(gc.getPlayer(self.pWBalkanID).getTeam())
                self.pEnglandTeam.addTeam(gc.getPlayer(self.pGreeceID).getTeam())
                self.pGreeceTeam = gc.getTeam(gc.getPlayer(self.pGreeceID).getTeam())

        def EJun2_1941(self):
                # Cutscene movie
#        	popupInfo = CyPopupInfo()
#                popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON_SCREEN)
#        	popupInfo.setData1(0)
#                popupInfo.setData2(0)
#                popupInfo.setData3(6)
#                popupInfo.setText(u"showWonderMovie")
#        	for i in range(gc.getMAX_CIV_PLAYERS()):
#        	    if (gc.getPlayer(i).isAlive()):
#                        if(gc.getPlayer(i).isHuman()):
#                            popupInfo.addPopup(i)
                # Axis DOW USSR
                popup = PyPopup.PyPopup(-1)
                szTitle = localText.getText("TXT_KEY_WW2_EJUN2_1941_TITLE", ())
                szText = localText.getText("TXT_KEY_WW2_EJUN2_1941_TEXT", ())
                popup.setHeaderString(szTitle)
                popup.addSeparator()
                popup.setBodyString(szText)
                popup.launch()
                game.setBordersOpen(self.pGermanyID, self.pFinlandID)
                self.pGermanyTeam.declareWar(self.pUSSRID, false, WarPlanTypes.WARPLAN_TOTAL)
                self.pFinlandTeam.declareWar(self.pUSSRID, false, WarPlanTypes.WARPLAN_TOTAL)

        def EDec1_1941(self):
                # Axis DOW USA
                popup = PyPopup.PyPopup(-1)
                szTitle = localText.getText("TXT_KEY_WW2_EDEC1_1941_TITLE", ())
                szText = localText.getText("TXT_KEY_WW2_EDEC1_1941_TEXT", ())
                popup.setHeaderString(szTitle)
                popup.addSeparator()
                popup.setBodyString(szText)
                popup.launch()
                self.pGermanyTeam.declareWar(self.pUSAID, false, WarPlanTypes.WARPLAN_TOTAL)
                self.pEnglandTeam.addTeam(gc.getPlayer(self.pUSAID).getTeam())
                self.pUSATeam = gc.getTeam(gc.getPlayer(self.pUSAID).getTeam())

# RtW Pacific 1936 Event Scripts
###################################################
        def AJul1_1937(self):
                # Cutscene movie
#        	popupInfo = CyPopupInfo()
#                popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON_SCREEN)
#        	popupInfo.setData1(0)
#                popupInfo.setData2(0)
#        	popupInfo.setData3(7)
#        	popupInfo.setText(u"showWonderMovie")
#        	for i in range(gc.getMAX_CIV_PLAYERS()):
#        	    if (gc.getPlayer(i).isAlive()):
#                        if(gc.getPlayer(i).isHuman()):
#                            popupInfo.addPopup(i)
                # Japan DOW China
                popup = PyPopup.PyPopup(-1)
                szTitle = localText.getText("TXT_KEY_WW2_AJUL1_1937_TITLE", ())
                szText = localText.getText("TXT_KEY_WW2_AJUL1_1937_TEXT", ())
                popup.setHeaderString(szTitle)
                popup.addSeparator()
                popup.setBodyString(szText)
                popup.launch()
                self.pChinaTeam.addTeam(gc.getPlayer(self.pSinkiangID).getTeam())
                self.pSinkiangTeam = gc.getTeam(gc.getPlayer(self.pSinkiangID).getTeam())
                self.pChinaTeam.addTeam(gc.getPlayer(self.pCChinaID).getTeam())
                self.pCChinaTeam = gc.getTeam(gc.getPlayer(self.pCChinaID).getTeam())
                self.pJapanTeam.declareWar(self.pChinaID, false, WarPlanTypes.WARPLAN_TOTAL)

        def ASep2_1940(self):
                # Siam joins Japan versus France
                popup = PyPopup.PyPopup(-1)
                szTitle = localText.getText("TXT_KEY_WW2_ASEP2_1940_TITLE", ())
                szText = localText.getText("TXT_KEY_WW2_ASEP2_1940_TEXT", ())
                popup.setHeaderString(szTitle)
                popup.addSeparator()
                popup.setBodyString(szText)
                popup.launch()
                self.pJapanTeam.addTeam(gc.getPlayer(self.pSiamID).getTeam())
                self.pSiamTeam = gc.getTeam(gc.getPlayer(self.pSiamID).getTeam())
                self.pJapanTeam.declareWar(self.pFranceID, false, WarPlanTypes.WARPLAN_TOTAL)

        def ADec1_1941(self):
                # Cutscene movie
#        	popupInfo = CyPopupInfo()
#                popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON_SCREEN)
#        	popupInfo.setData1(0)
#                popupInfo.setData2(0)
#        	popupInfo.setData3(5)
#        	popupInfo.setText(u"showWonderMovie")
#        	for i in range(gc.getMAX_CIV_PLAYERS()):
#        	    if (gc.getPlayer(i).isAlive()):
#                        if(gc.getPlayer(i).isHuman()):
#                            popupInfo.addPopup(i)
                # Japan DOW USA, England, Siam, Australia, Dutch, Philippines
                popup = PyPopup.PyPopup(-1)
                szTitle = localText.getText("TXT_KEY_WW2_ADEC1_1941_TITLE", ())
                szText = localText.getText("TXT_KEY_WW2_ADEC1_1941_TEXT", ())
                popup.setHeaderString(szTitle)
                popup.addSeparator()
                popup.setBodyString(szText)
                popup.launch()
                self.pEnglandTeam.addTeam(gc.getPlayer(self.pAustraliaID).getTeam())
                self.pAustraliaTeam = gc.getTeam(gc.getPlayer(self.pAustraliaID).getTeam())
                self.pEnglandTeam.addTeam(gc.getPlayer(self.pCanadaID).getTeam())
                self.pCanadaTeam = gc.getTeam(gc.getPlayer(self.pCanadaID).getTeam())
                self.pEnglandTeam.addTeam(gc.getPlayer(self.pChinaID).getTeam())
                self.pChinaTeam = gc.getTeam(gc.getPlayer(self.pChinaID).getTeam())
                self.pEnglandTeam.addTeam(gc.getPlayer(self.pUSAID).getTeam())
                self.pUSATeam = gc.getTeam(gc.getPlayer(self.pUSAID).getTeam())
                self.pEnglandTeam.addTeam(gc.getPlayer(self.pFranceID).getTeam())
                self.pFranceTeam = gc.getTeam(gc.getPlayer(self.pFranceID).getTeam())
                self.pEnglandTeam.addTeam(gc.getPlayer(self.pPhilippinesID).getTeam())
                self.pPhilippinesTeam = gc.getTeam(gc.getPlayer(self.pPhilippinesID).getTeam())
                self.pEnglandTeam.addTeam(gc.getPlayer(self.pDutchID).getTeam())
                self.pDutchTeam = gc.getTeam(gc.getPlayer(self.pDutchID).getTeam())

        def AAug1_1945(self):
                # USSR DOW Japan
                popup = PyPopup.PyPopup(-1)
                szTitle = localText.getText("TXT_KEY_WW2_AAUG1_1945_TITLE", ())
                szText = localText.getText("TXT_KEY_WW2_AAUG1_1945_TEXT", ())
                popup.setHeaderString(szTitle)
                popup.addSeparator()
                popup.setBodyString(szText)
                popup.launch()
                self.pUSSRTeam.addTeam(gc.getPlayer(self.pMongoliaID).getTeam())
                self.pMongoliaTeam = gc.getTeam(gc.getPlayer(self.pMongoliaID).getTeam())
                self.pEnglandTeam.addTeam(gc.getPlayer(self.pUSSRID).getTeam())
                self.pUSSRTeam = gc.getTeam(gc.getPlayer(self.pUSSRID).getTeam())

# RtW Utilities
###################################################
        def getFrenchAxisCities(self):
                iCount = 0
                if (self.cParis.getOwner() == self.pGermanyID or self.cParis.getOwner() == self.pItalyID):
                        iCount = iCount + 1
                if (self.cDijon.getOwner() == self.pGermanyID or self.cDijon.getOwner() == self.pItalyID):
                        iCount = iCount + 1
                if (self.cMetz.getOwner() == self.pGermanyID or self.cMetz.getOwner() == self.pItalyID):
                        iCount = iCount + 1
                if (self.cCalais.getOwner() == self.pGermanyID or self.cCalais.getOwner() == self.pItalyID):
                        iCount = iCount + 1
                if (self.cLeharve.getOwner() == self.pGermanyID or self.cLeharve.getOwner() == self.pItalyID):
                        iCount = iCount + 1
                if (self.cNice.getOwner() == self.pGermanyID or self.cNice.getOwner() == self.pItalyID):
                        iCount = iCount + 1
                if (self.cTours.getOwner() == self.pGermanyID or self.cTours.getOwner() == self.pItalyID):
                        iCount = iCount + 1
                if (self.cBrest.getOwner() == self.pGermanyID or self.cBrest.getOwner() == self.pItalyID):
                        iCount = iCount + 1
                if (self.cParis.getOwner() == self.pFranceID):
                        iCount = 0;
                return iCount

	# Determine the start-game state
	def setupGame(self):
                # Initialise values		
		self.initValues()

        # Initialise stuff (includes on loads)
	def initValues(self):
                # Global Init
                rtwglobal.globalInit()
                # Variables
                self.Map = 99
                self.iTurnOffset = 0
                self.numFrenchCitiesFall = 0
		self.iNumPlayers = 0
                # Setup end game trigger
                self.endGame = 0

                if(CyMap().plot(0,0).getTerrainType() == 0):
                    self.Map = 0    # 0 = 1936 Europe, 1 = 1936 Pacific, 2 = 1939 Europe, 3 - 1936 World, 4 - 1938 Europe, 5 - 1941 Pacific
                elif(CyMap().plot(0,0).getTerrainType() == 1):
                    self.Map = 1
                elif(CyMap().plot(0,0).getTerrainType() == 2):
                    self.Map = 2
                elif(CyMap().plot(0,0).getTerrainType() == 3):
                    self.Map = 3
                elif(CyMap().plot(0,0).getTerrainType() == 4):
                    self.Map = 4
                elif(CyMap().plot(0,0).getTerrainType() == 7):
                    self.Map = 5
                self.HistEvents = game.getHistoryEvents()
                if (not self.HistEvents == 2):
                    self.resetTrueWarPeace()

		# Offset value set in WorldBuilder save
		if (self.Map == 0 or self.Map == 1 or self.Map == 3):
                        self.iTurnOffset = 863
                elif (self.Map == 2):
                        self.iTurnOffset = 947
                elif (self.Map == 4):
                        self.iTurnOffset = 911
                elif (self.Map == 5):
                        self.iTurnOffset = 995
                elif (self.Map == 99):
                        self.giveSettlerTech()
                        self.resetWarPeace()
                        self.HistEvents = 2

                # Setup number of French cities to hold for fall
                if (self.Map == 3):
                    self.numFrenchCitiesFall = 4
                else:
                    self.numFrenchCitiesFall = 4

		# Setup player ID's
		for iPlayerLoop in range(gc.getMAX_PLAYERS()):
			if (gc.getPlayer(iPlayerLoop).isAlive()):
				self.iNumPlayers += 1
			else:
				break		# Exit when we hit a non-living player - don't want the barbs (won't work for later in the game when civs might have died)

		if(self.Map == 0 or self.Map == 2 or self.Map == 4):
                    self.pGermanyID = 0
                    self.cBerlin = gc.getMap().plot( 69, 36 ).getPlotCity()
                    self.pItalyID = 1
                    self.cRome = gc.getMap().plot( 68, 20 ).getPlotCity()
                    self.pEnglandID = 2
                    self.cLondon = gc.getMap().plot( 54, 34 ).getPlotCity()
                    self.pUSSRID = 3
                    self.cMoscow = gc.getMap().plot( 95, 44 ).getPlotCity()
                    self.pFranceID = 4
                    self.cParis = gc.getMap().plot( 58, 30 ).getPlotCity()
                    self.pUSAID = 5
                    self.cWashington = gc.getMap().plot( 4, 34 ).getPlotCity()
                    self.pPolandID = 6
                    self.cWarsaw = gc.getMap().plot( 78, 36 ).getPlotCity()
                    self.pBalkanID = 7
                    self.cBucharest = gc.getMap().plot( 83, 24 ).getPlotCity()
                    self.pScandinaviaID = 8
                    self.cOslo = gc.getMap().plot( 65, 47 ).getPlotCity()
                    self.pLowlandsID = 9
                    self.cAmsterdam = gc.getMap().plot( 60, 35 ).getPlotCity()
                    self.pRiberiaID = 10
                    self.cMadrid = gc.getMap().plot( 49, 19 ).getPlotCity()
                    self.pBalticID = 11
                    self.cRiga = gc.getMap().plot( 81, 42 ).getPlotCity()
                    self.pTurkeyID = 12
                    self.cAnkara = gc.getMap().plot( 91, 18 ).getPlotCity()
                    self.pFinlandID = 13
                    self.cHelsinki = gc.getMap().plot( 83, 49 ).getPlotCity()
                    self.pWBalkanID = 14
                    self.cBelgrade = gc.getMap().plot( 76, 25 ).getPlotCity()
                    self.pSwedenID = 15
                    self.cStockholm = gc.getMap().plot( 73, 47 ).getPlotCity()
                    self.pAustriaID = 16
                    self.pCzechID = 17
                    self.pCanadaID = 18
                    self.pIrelandID = 19
                    self.pGreeceID = 20
                    self.pRomaniaID = 21
                    self.pAlbaniaID = 22
                    self.pVichyID = 23
                    self.pNiberiaID = 24
                    self.cVParis = gc.getMap().plot( 58, 30 ).getPlotCity()
                    self.pJapanID = 99
                    self.pChinaID = 99
                if(self.Map == 1 or self.Map == 5):
                    self.pJapanID = 0
                    self.cTokyo = gc.getMap().plot( 58, 30 ).getPlotCity()
                    self.pEnglandID = 1
                    self.c = gc.getMap().plot( 58, 30 ).getPlotCity()
                    self.pChinaID = 2
                    self.cNanjing = gc.getMap().plot( 58, 30 ).getPlotCity()
                    self.pUSSRID = 3
                    self.cVladivostok = gc.getMap().plot( 58, 30 ).getPlotCity()
                    self.pFranceID = 4
                    self.cSaigon = gc.getMap().plot( 58, 30 ).getPlotCity()
                    self.pUSAID = 5
                    self.cSanFran = gc.getMap().plot( 58, 30 ).getPlotCity()
                    self.pMongoliaID = 6
                    self.cParis = gc.getMap().plot( 58, 30 ).getPlotCity()
                    self.pPhilippinesID = 7
                    self.cManilla = gc.getMap().plot( 58, 30 ).getPlotCity()
                    self.pSiamID = 8
                    self.cBangkok = gc.getMap().plot( 58, 30 ).getPlotCity()
                    self.pSinkiangID = 9
                    self.cParis = gc.getMap().plot( 58, 30 ).getPlotCity()
                    self.pDutchID = 10
                    self.cDjakarta = gc.getMap().plot( 58, 30 ).getPlotCity()
                    self.pAustraliaID = 11
                    self.cCanberra = gc.getMap().plot( 58, 30 ).getPlotCity()
                    self.pCanadaID = 12
                    self.pCChinaID = 13
                    self.pGermanyID = 99
                    self.pItalyID = 99

		# Setup team ID's
		if(self.Map == 0 or self.Map == 2 or self.Map == 4):
                    self.pGermanyTeam = gc.getTeam(gc.getPlayer(self.pGermanyID).getTeam())
                    self.pItalyTeam = gc.getTeam(gc.getPlayer(self.pItalyID).getTeam())
                    self.pEnglandTeam = gc.getTeam(gc.getPlayer(self.pEnglandID).getTeam())
                    self.pUSSRTeam = gc.getTeam(gc.getPlayer(self.pUSSRID).getTeam())
                    self.pFranceTeam = gc.getTeam(gc.getPlayer(self.pFranceID).getTeam())
                    self.pUSATeam = gc.getTeam(gc.getPlayer(self.pUSAID).getTeam())
                    self.pPolandTeam = gc.getTeam(gc.getPlayer(self.pPolandID).getTeam())
                    self.pBalkanTeam = gc.getTeam(gc.getPlayer(self.pBalkanID).getTeam())
                    self.pScandinaviaTeam = gc.getTeam(gc.getPlayer(self.pScandinaviaID).getTeam())
                    self.pLowlandsTeam = gc.getTeam(gc.getPlayer(self.pLowlandsID).getTeam())
                    self.pRiberiaTeam = gc.getTeam(gc.getPlayer(self.pRiberiaID).getTeam())
                    self.pBalticTeam = gc.getTeam(gc.getPlayer(self.pBalticID).getTeam())
                    self.pTurkeyTeam = gc.getTeam(gc.getPlayer(self.pTurkeyID).getTeam())
                    self.pFinlandTeam = gc.getTeam(gc.getPlayer(self.pFinlandID).getTeam())
                    self.pWBalkanTeam = gc.getTeam(gc.getPlayer(self.pWBalkanID).getTeam())
                    self.pSwedenTeam = gc.getTeam(gc.getPlayer(self.pSwedenID).getTeam())
                    self.pAustriaTeam = gc.getTeam(gc.getPlayer(self.pAustriaID).getTeam())
                    self.pCzechTeam = gc.getTeam(gc.getPlayer(self.pCzechID).getTeam())
                    self.pCanadaTeam = gc.getTeam(gc.getPlayer(self.pCanadaID).getTeam())
                    self.pIrelandTeam = gc.getTeam(gc.getPlayer(self.pIrelandID).getTeam())
                    self.pGreeceTeam = gc.getTeam(gc.getPlayer(self.pGreeceID).getTeam())
                    self.pRomaniaTeam = gc.getTeam(gc.getPlayer(self.pRomaniaID).getTeam())
                    self.pAlbaniaTeam = gc.getTeam(gc.getPlayer(self.pAlbaniaID).getTeam())
                    self.pVichyTeam = gc.getTeam(gc.getPlayer(self.pVichyID).getTeam())
                    self.pNiberiaTeam = gc.getTeam(gc.getPlayer(self.pNiberiaID).getTeam())
                if(self.Map == 1 or self.Map == 5):
                    self.pJapanTeam = gc.getTeam(gc.getPlayer(self.pJapanID).getTeam())
                    self.pEnglandTeam = gc.getTeam(gc.getPlayer(self.pEnglandID).getTeam())
                    self.pChinaTeam = gc.getTeam(gc.getPlayer(self.pChinaID).getTeam())
                    self.pUSSRTeam = gc.getTeam(gc.getPlayer(self.pUSSRID).getTeam())
                    self.pFranceTeam = gc.getTeam(gc.getPlayer(self.pFranceID).getTeam())
                    self.pUSATeam = gc.getTeam(gc.getPlayer(self.pUSAID).getTeam())
                    self.pMongoliaTeam = gc.getTeam(gc.getPlayer(self.pMongoliaID).getTeam())
                    self.pPhilippinesTeam = gc.getTeam(gc.getPlayer(self.pPhilippinesID).getTeam())
                    self.pSiamTeam = gc.getTeam(gc.getPlayer(self.pSiamID).getTeam())
                    self.pSinkiangTeam = gc.getTeam(gc.getPlayer(self.pSinkiangID).getTeam())
                    self.pDutchTeam = gc.getTeam(gc.getPlayer(self.pDutchID).getTeam())
                    self.pAustraliaTeam = gc.getTeam(gc.getPlayer(self.pAustraliaID).getTeam())
                    self.pCanadaTeam = gc.getTeam(gc.getPlayer(self.pCanadaID).getTeam())
                    self.pCChinaTeam = gc.getTeam(gc.getPlayer(self.pCChinaID).getTeam())

                # Set Vichy France event cities
                if(self.Map == 0 or self.Map == 2 or self.Map == 4):
                    self.cDijon = gc.getMap().plot( 60, 27 ).getPlotCity()
                    self.cMetz = gc.getMap().plot( 62, 28 ).getPlotCity()
                    self.cCalais = gc.getMap().plot( 57, 32 ).getPlotCity()
                    self.cLeharve = gc.getMap().plot( 54, 31 ).getPlotCity()
                    self.cTours = gc.getMap().plot( 55, 26 ).getPlotCity()
                    self.cBrest = gc.getMap().plot( 49, 29 ).getPlotCity()
                    self.cNice = gc.getMap().plot( 61, 22 ).getPlotCity()

                # Set warpeace
                if(self.HistEvents < 2):
                    for iPlayerLoop1 in range(35):#gc.getMAX_PLAYERS()):
                        if(gc.getPlayer(iPlayerLoop1).isAlive()):
                            for iPlayerLoop2 in range(35):#gc.getMAX_PLAYERS()):
                                if(gc.getPlayer(iPlayerLoop2).isAlive()):
                                    gc.getTeam(gc.getPlayer(iPlayerLoop1).getTeam()).setPermanentWarPeace(iPlayerLoop2, true)

                self.initEvents()
                return

        def initEvents(self):
                # Set event turns
                self.Event1 = -1
                self.Event2 = -1
                self.Event3 = -1
                self.Event4 = -1
                self.Event5 = -1
                self.Event6 = -1
                self.Event7 = -1
                self.Event8 = -1
                self.Event9 = -1
                self.Event10 = -1
                self.Event11 = -1
                self.Event12 = -1
                self.Event13 = -1
                self.Event14 = -1
                self.Event15 = -1
                self.Event16 = -1
                self.Event17 = -1
                self.Event18 = -1
                self.Event19 = -1
                if(self.Map == 0):
                    if(self.HistEvents == 0):
                        self.Event1 = 88   # Germany vs Poland, England, France
                        self.Event2 = 89   # USSR vs Poland
                        self.Event3 = 94   # USSR vs Finland
                        self.Event4 = 100  # USSR peace Finland
                        self.Event5 = 102  # Germany vs Scandinavia
                        self.Event6 = 104  # Germany vs Lowlands
                        self.Event7 = 106  # Italy vs France, England; Italy ally Germany
                        self.Event8 = 107  # USSR vs Baltic
                        self.Event9 = 117  # East Balkan ally Germany, Italy
                        self.Event10 = 126 # Axis vs West Balkan
                        self.Event11 = 131 # Axis vs USSR
                        self.Event12 = 133 # USSR ally Allies
                        self.Event13 = 143 # Pearl Harbor; Axis vs USA
                        self.Event14 = 78 # Italy vs Albania
                        self.Event15 = 13 # Spanish Civil War
                        self.Event16 = 52 # Anschluss
                        self.Event17 = 65 # Munich Agreement
                    if(self.HistEvents == 1):
                        self.Event1 = CyGame().getSorenRandNum(11, "Random Historical Events") + 83
                        self.Event2 = self.Event1 + 1 #CyGame().getSorenRandNum(11, "Random Historical Events") + 84
                        self.Event3 = CyGame().getSorenRandNum(11, "Random Historical Events") + 89
                        self.Event4 = self.Event3 + 6 #CyGame().getSorenRandNum(11, "Random Historical Events") + 95
                        self.Event5 = CyGame().getSorenRandNum(11, "Random Historical Events") + 97
                        self.Event6 = CyGame().getSorenRandNum(11, "Random Historical Events") + 99
                        self.Event7 = CyGame().getSorenRandNum(11, "Random Historical Events") + 101
                        self.Event8 = CyGame().getSorenRandNum(11, "Random Historical Events") + 104
                        self.Event9 = CyGame().getSorenRandNum(11, "Random Historical Events") + 109
                        self.Event10 = CyGame().getSorenRandNum(11, "Random Historical Events") + 110
                        self.Event11 = CyGame().getSorenRandNum(11, "Random Historical Events") + 126
                        self.Event12 = CyGame().getSorenRandNum(11, "Random Historical Events") + 128
                        self.Event13 = CyGame().getSorenRandNum(11, "Random Historical Events") + 138
                        self.Event14 = CyGame().getSorenRandNum(11, "Random Historical Events") + 73
                        self.Event15 = CyGame().getSorenRandNum(11, "Random Historical Events") + 8
                        self.Event16 = CyGame().getSorenRandNum(11, "Random Historical Events") + 47
                        self.Event17 = CyGame().getSorenRandNum(11, "Random Historical Events") + 60
                if(self.Map == 1):
                    if(self.HistEvents == 0):
                        self.Event1 = 36  # Luo Kou Bridge incident, Japan vs China (Jul1 1937)
                        self.Event2 = 113 # Japan joins Siam versus France (Sep2 1940)
                        self.Event3 = 142 # Pearl Harbor, Japan vs USA, England, Dutch, Australia, Philippines (Dec1 1941)
                        self.Event4 = 230 # Russia/Mongolia vs Japan (Aug1 1945)
                    if(self.HistEvents == 1):
                        self.Event1 = CyGame().getSorenRandNum(11, "Random Historical Events") + 31
                        self.Event2 = CyGame().getSorenRandNum(11, "Random Historical Events") + 108
                        self.Event3 = CyGame().getSorenRandNum(11, "Random Historical Events") + 137
                        self.Event4 = CyGame().getSorenRandNum(11, "Random Historical Events") + 225
                if(self.Map == 2):
                    if(self.HistEvents == 0):
                        self.Event1 = 4   # Germany vs Poland, England, France
                        self.Event2 = 5   # USSR vs Poland
                        self.Event3 = 10  # USSR vs Finland
                        self.Event4 = 16  # USSR peace Finland
                        self.Event5 = 18  # Germany vs Scandinavia
                        self.Event6 = 20  # Germany vs Lowlands
                        self.Event7 = 22  # Italy vs France, England; Italy ally Germany
                        self.Event8 = 23  # USSR vs Baltic
                        self.Event9 = 33  # East Balkan ally Germany, Italy
                        self.Event10 = 42 # Axis vs West Balkan
                        self.Event11 = 47 # Axis vs USSR
                        self.Event12 = 49 # USSR ally Allies
                        self.Event13 = 59 # Pearl Harbor; Axis vs USA
                    if(self.HistEvents == 1):
                        self.Event1 = CyGame().getSorenRandNum(11, "Random Historical Events") + 0
                        self.Event2 = self.Event1 + 1 #CyGame().getSorenRandNum(11, "Random Historical Events") + 0
                        self.Event3 = CyGame().getSorenRandNum(11, "Random Historical Events") + 5
                        self.Event4 = self.Event3 + 6 #CyGame().getSorenRandNum(11, "Random Historical Events") + 11
                        self.Event5 = CyGame().getSorenRandNum(11, "Random Historical Events") + 13
                        self.Event6 = CyGame().getSorenRandNum(11, "Random Historical Events") + 15
                        self.Event7 = CyGame().getSorenRandNum(11, "Random Historical Events") + 17
                        self.Event8 = CyGame().getSorenRandNum(11, "Random Historical Events") + 18
                        self.Event9 = CyGame().getSorenRandNum(11, "Random Historical Events") + 28
                        self.Event10 = CyGame().getSorenRandNum(11, "Random Historical Events") + 37
                        self.Event11 = CyGame().getSorenRandNum(11, "Random Historical Events") + 42
                        self.Event12 = CyGame().getSorenRandNum(11, "Random Historical Events") + 44
                        self.Event13 = CyGame().getSorenRandNum(11, "Random Historical Events") + 54
                if(self.Map == 3):
                    if(self.HistEvents == 0):
                        self.Event1 = 88   # Germany vs Poland, England, France
                        self.Event2 = 89   # USSR vs Poland
                        self.Event3 = 94   # USSR vs Finland
                        self.Event4 = 100  # USSR peace Finland
                        self.Event5 = 102  # Germany vs Scandinavia
                        self.Event6 = 104  # Germany vs Lowlands
                        self.Event7 = 106  # Italy vs France, England; Italy ally Germany
                        self.Event8 = 107  # USSR vs Baltic
                        self.Event9 = 117  # East Balkan ally Germany, Italy
                        self.Event10 = 126 # Axis vs West Balkan
                        self.Event11 = 131 # Axis vs USSR
                        self.Event12 = 14 # Spanish Civil War
                        self.Event13 = 143 # Pearl Harbor; Axis vs USA
                        self.Event14 = 36  # Luo Kou Bridge incident, Japan vs China (Jul1 1937)
                        self.Event15 = 113 # Japan joins Siam versus France (Sep2 1940)
                        self.Event16 = 142 # Pearl Harbor, Japan vs USA, England, Dutch, Australia, Philippines (Dec1 1941)
                        self.Event17 = 230 # Russia/Mongolia vs Japan (Aug1 1945)
                        self.Event18 = 52 # Germany vs Austria
                        self.Event19 = 65 # Germany vs Czech
                    if(self.HistEvents == 1):
                        self.Event1 = CyGame().getSorenRandNum(11, "Random Historical Events") + 83
                        self.Event2 = self.Event1 + 1 #CyGame().getSorenRandNum(11, "Random Historical Events") + 84
                        self.Event3 = CyGame().getSorenRandNum(11, "Random Historical Events") + 89
                        self.Event4 = self.Event3 + 6 #CyGame().getSorenRandNum(11, "Random Historical Events") + 95
                        self.Event5 = CyGame().getSorenRandNum(11, "Random Historical Events") + 97
                        self.Event6 = CyGame().getSorenRandNum(11, "Random Historical Events") + 99
                        self.Event7 = CyGame().getSorenRandNum(11, "Random Historical Events") + 101
                        self.Event8 = CyGame().getSorenRandNum(11, "Random Historical Events") + 104
                        self.Event9 = CyGame().getSorenRandNum(11, "Random Historical Events") + 109
                        self.Event10 = CyGame().getSorenRandNum(11, "Random Historical Events") + 110
                        self.Event11 = CyGame().getSorenRandNum(11, "Random Historical Events") + 126
                        self.Event12 = CyGame().getSorenRandNum(11, "Random Historical Events") + 9
                        self.Event13 = CyGame().getSorenRandNum(11, "Random Historical Events") + 138
                        self.Event14 = CyGame().getSorenRandNum(11, "Random Historical Events") + 31
                        self.Event15 = CyGame().getSorenRandNum(11, "Random Historical Events") + 108
                        self.Event16 = self.Event13 - 1 #CyGame().getSorenRandNum(11, "Random Historical Events") + 137
                        self.Event17 = CyGame().getSorenRandNum(11, "Random Historical Events") + 225
                        self.Event18 = CyGame().getSorenRandNum(11, "Random Historical Events") + 47
                        self.Event19 = CyGame().getSorenRandNum(11, "Random Historical Events") + 60
                if(self.Map == 4):
                    if(self.HistEvents == 0):
                        self.Event1 = 40  # Germany vs Poland, England, France
                        self.Event2 = 41  # USSR vs Poland
                        self.Event3 = 46  # USSR vs Finland
                        self.Event4 = 52  # USSR peace Finland
                        self.Event5 = 54  # Germany vs Scandinavia
                        self.Event6 = 56  # Germany vs Lowlands
                        self.Event7 = 58  # Italy vs France, England; Italy ally Germany
                        self.Event8 = 59  # USSR vs Baltic
                        self.Event9 = 69  # East Balkan ally Germany, Italy
                        self.Event10 = 78 # Axis vs West Balkan
                        self.Event11 = 83 # Axis vs USSR
                        self.Event12 = 85 # USSR ally Allies
                        self.Event13 = 95 # Pearl Harbor; Axis vs USA
                    if(self.HistEvents == 1):
                        self.Event1 = CyGame().getSorenRandNum(11, "Random Historical Events") + 35
                        self.Event2 = self.Event1 + 1 #CyGame().getSorenRandNum(11, "Random Historical Events") + 36
                        self.Event3 = CyGame().getSorenRandNum(11, "Random Historical Events") + 41
                        self.Event4 = self.Event3 + 6 #CyGame().getSorenRandNum(11, "Random Historical Events") + 47
                        self.Event5 = CyGame().getSorenRandNum(11, "Random Historical Events") + 49
                        self.Event6 = CyGame().getSorenRandNum(11, "Random Historical Events") + 51
                        self.Event7 = CyGame().getSorenRandNum(11, "Random Historical Events") + 53
                        self.Event8 = CyGame().getSorenRandNum(11, "Random Historical Events") + 54
                        self.Event9 = CyGame().getSorenRandNum(11, "Random Historical Events") + 64
                        self.Event10 = CyGame().getSorenRandNum(11, "Random Historical Events") + 73
                        self.Event11 = CyGame().getSorenRandNum(11, "Random Historical Events") + 78
                        self.Event12 = CyGame().getSorenRandNum(11, "Random Historical Events") + 80
                        self.Event13 = CyGame().getSorenRandNum(11, "Random Historical Events") + 90
                if(self.Map == 5):
                    if(self.HistEvents == 0):
                        self.Event1 = 10 # Pearl Harbor, Japan vs USA, England, Dutch, Australia, Philippines (Dec1 1941)
                        self.Event2 = 98 # Russia/Mongolia vs Japan (Aug1 1945)
                    if(self.HistEvents == 1):
                        self.Event1 = CyGame().getSorenRandNum(11, "Random Historical Events") + 5
                        self.Event2 = CyGame().getSorenRandNum(11, "Random Historical Events") + 93
                return

        def resetWarPeace(self):
                # Set warpeace
                for iPlayerLoop1 in range(gc.getMAX_PLAYERS()):
                    if(gc.getPlayer(iPlayerLoop1).isAlive()):
                        gc.getTeam(gc.getPlayer(iPlayerLoop1).getTeam()).setHasTech(2, true, iPlayerLoop1, false, false)
                        for iPlayerLoop2 in range(gc.getMAX_PLAYERS()):
                            if(gc.getPlayer(iPlayerLoop2).isAlive()):
                                gc.getTeam(gc.getPlayer(iPlayerLoop1).getTeam()).setPermanentWarPeace(iPlayerLoop2, false)
                return

        def resetTrueWarPeace(self):
                # Set warpeace
                for iPlayerLoop1 in range(gc.getMAX_PLAYERS()):
                    if(gc.getPlayer(iPlayerLoop1).isAlive()):
                        for iPlayerLoop2 in range(gc.getMAX_PLAYERS()):
                            if(gc.getPlayer(iPlayerLoop2).isAlive()):
                                gc.getTeam(gc.getPlayer(iPlayerLoop1).getTeam()).setPermanentWarPeace(iPlayerLoop2, true)
                return

        def giveSettlerTech(self):
                for iPlayerLoop1 in range(gc.getMAX_PLAYERS()):
                    if(gc.getPlayer(iPlayerLoop1).isAlive()):
                        gc.getTeam(gc.getPlayer(iPlayerLoop1).getTeam()).setHasTech(0, true, iPlayerLoop1, false, false)
                        gc.getTeam(gc.getPlayer(iPlayerLoop1).getTeam()).setHasTech(1, true, iPlayerLoop1, false, false)
                        gc.getTeam(gc.getPlayer(iPlayerLoop1).getTeam()).setHasTech(2, true, iPlayerLoop1, false, false)
                        gc.getTeam(gc.getPlayer(iPlayerLoop1).getTeam()).setHasTech(4, true, iPlayerLoop1, false, false)
                        gc.getTeam(gc.getPlayer(iPlayerLoop1).getTeam()).setHasTech(5, true, iPlayerLoop1, false, false)
                        gc.getTeam(gc.getPlayer(iPlayerLoop1).getTeam()).setHasTech(6, true, iPlayerLoop1, false, false)
                        gc.getTeam(gc.getPlayer(iPlayerLoop1).getTeam()).setHasTech(7, true, iPlayerLoop1, false, false)
                        gc.getTeam(gc.getPlayer(iPlayerLoop1).getTeam()).setHasTech(8, true, iPlayerLoop1, false, false)
                        gc.getTeam(gc.getPlayer(iPlayerLoop1).getTeam()).setHasTech(9, true, iPlayerLoop1, false, false)
                        gc.getTeam(gc.getPlayer(iPlayerLoop1).getTeam()).setHasTech(10, true, iPlayerLoop1, false, false)
                        gc.getTeam(gc.getPlayer(iPlayerLoop1).getTeam()).setHasTech(11, true, iPlayerLoop1, false, false)
                        gc.getTeam(gc.getPlayer(iPlayerLoop1).getTeam()).setHasTech(12, true, iPlayerLoop1, false, false)
                        gc.getTeam(gc.getPlayer(iPlayerLoop1).getTeam()).setHasTech(13, true, iPlayerLoop1, false, false)
                return

        def blankHandler(self, playerID, netUserData, popupReturn ) :
                # Dummy handler to take the second event for popup
                return

        def doVictory(self, bValue):
                # Do victory stuff
                game.rtwGameOver()
                self.endGame = 1

        def getMap(self):
                return self.Map

        def buildFighter(self, playerNum):
                # Keep moving!
                self.iFighter1ID = CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_WW2_FIGHTER')
                self.iFighter2ID = CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_WW2_IMPROVED_FIGHTER')
                self.iFighter3ID = CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_WW2_JET_FIGHTER')
                iChance = 1
                if (playerNum == self.pGermanyID):
                    self.iFighter1ID = CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_WW2_FIG0_GER')
                    self.iFighter2ID = CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_WW2_FIG1_GER')
                    self.iFighter3ID = CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_WW2_FIG2_GER')
                    iChance = 33
                elif (playerNum == self.pItalyID):
                    self.iFighter1ID = CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_WW2_FIG0_ITA')
                    self.iFighter2ID = CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_WW2_FIG1_ITA')
                    self.iFighter3ID = CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_WW2_FIG2_ITA')
                    iChance = 33
                elif (playerNum == self.pJapanID):
                    self.iFighter1ID = CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_WW2_FIG0_JAP')
                    self.iFighter2ID = CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_WW2_FIG1_JAP')
                    self.iFighter3ID = CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_WW2_FIG2_JAP')
                    iChance = 33
                elif (playerNum == self.pChinaID):
                    self.iFighter1ID = CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_WW2_FIG0_CHI')
                    self.iFighter2ID = CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_WW2_FIG1_CHI')
                    self.iFighter3ID = CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_WW2_FIG2_CHI')
                    iChance = 10
                elif (playerNum == self.pEnglandID):
                    self.iFighter1ID = CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_WW2_FIG0_ENG')
                    self.iFighter2ID = CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_WW2_FIG1_ENG')
                    self.iFighter3ID = CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_WW2_FIG2_ENG')
                    iChance = 10
                elif (playerNum == self.pFranceID):
                    self.iFighter1ID = CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_WW2_FIG0_FRA')
                    self.iFighter2ID = CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_WW2_FIG1_FRA')
                    self.iFighter3ID = CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_WW2_FIG2_FRA')
                    iChance = 5
                elif (playerNum == self.pUSAID):
                    self.iFighter1ID = CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_WW2_FIG0_USA')
                    self.iFighter2ID = CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_WW2_FIG1_USA')
                    self.iFighter3ID = CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_WW2_FIG2_USA')
                    iChance = 5
                elif (playerNum == self.pUSSRID):
                    self.iFighter1ID = CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_WW2_FIG0_RUS')
                    self.iFighter2ID = CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_WW2_FIG1_RUS')
                    self.iFighter3ID = CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_WW2_FIG2_RUS')
                    iChance = 15
                player = gc.getPlayer(playerNum)
                if (gc.getGame().getSorenRandNum(100, 'Fighters') < iChance):
                    if (not player.isHuman() and player.isAlive()):
                        city = player.getCapitalCity()
                        if (gc.getTeam(player.getTeam()).isHasTech(46)):
                            player.initUnit(self.iFighter3ID, city.getX(), city.getY(), UnitAITypes.UNITAI_DEFENSE_AIR, DirectionTypes.NO_DIRECTION)
                        elif (gc.getTeam(player.getTeam()).isHasTech(26)):
                            player.initUnit(self.iFighter2ID, city.getX(), city.getY(), UnitAITypes.UNITAI_DEFENSE_AIR, DirectionTypes.NO_DIRECTION)
                        elif (gc.getTeam(player.getTeam()).isHasTech(6)):
                            player.initUnit(self.iFighter1ID, city.getX(), city.getY(), UnitAITypes.UNITAI_DEFENSE_AIR, DirectionTypes.NO_DIRECTION)
                return

        def isBitterWinterTurn(self, iTurn):
                # Calculate if this turn need to increase winter
                # 1935-36
#                if (iTurn >= 864 and iTurn <= 865):
#                        return true
                # 1936-37
                if (iTurn >= 878 and iTurn <= 887):
                        return true
                # 1937-38
                if (iTurn >= 902 and iTurn <= 911):
                        return true
                # 1938-39
                if (iTurn >= 926 and iTurn <= 935):
                        return true
                # 1939-40
                if (iTurn >= 950 and iTurn <= 959):
                        return true
                # 1940-41
                if (iTurn >= 974 and iTurn <= 983):
                        return true
                # 1941-42
                if (iTurn >= 998 and iTurn <= 1007):
                        return true
                # 1942-43
                if (iTurn >= 1022 and iTurn <= 1031):
                        return true
                # 1943-44
                if (iTurn >= 1046 and iTurn <= 1055):
                        return true
                # 1944-45
                if (iTurn >= 1070 and iTurn <= 1079):
                        return true
                # 1945-46
                if (iTurn >= 1094 and iTurn <= 1103):
                        return true
                # 1946-47
                if (iTurn >= 1118 and iTurn <= 1127):
                        return true
                # 1947-48
                if (iTurn >= 1142 and iTurn <= 1151):
                        return true
                # 1948-49
                if (iTurn >= 1166 and iTurn <= 1175):
                        return true
                return false

#########   AIAutoPlay - Delete when finished
        def setAIAutoPlay(self, TurnsToAuto) :
                game.setAIAutoPlay(TurnsToAuto)
#########   AIAutoPlay - Delete when finished

        def getChangeCiv(self):
                return game.getChangeCiv()

        def doAIWarPlans(self, playerNum):
                pPlayer = gc.getPlayer(playerNum)
                iTeam = pPlayer.getTeam()
                pTeam = gc.getTeam(iTeam)
                if (not pPlayer.isHuman() and pPlayer.isAlive()):
                    if (pTeam.getAtWarCount(false) > 0):
                        for iLoopTeam in range(gc.getMAX_CIV_TEAMS()):
                            if (iTeam != iLoopTeam):
                                if (pTeam.isAtWar(iLoopTeam)):
                                    pTeam.AI_setWarPlan(iLoopTeam, WarPlanTypes.WARPLAN_TOTAL)
                    else:
                        for iLoopTeam in range(gc.getMAX_CIV_TEAMS()):
                            if (iTeam != iLoopTeam):
                                pTeam.AI_setWarPlan(iLoopTeam, WarPlanTypes.WARPLAN_PREPARING_TOTAL)
                return
