# Rhye's and Fall of Civilization - Main Scenario

from CvPythonExtensions import *
import CvUtil
import PyHelpers        # LOQ
import Popup
import pickle        	# LOQ 2005-10-12
import CvTranslator
import RFCUtils
import Consts as con




################
### Globals ###
##############

gc = CyGlobalContext()	# LOQ
PyPlayer = PyHelpers.PyPlayer	# LOQ
utils = RFCUtils.RFCUtils()

iCheatersPeriod = 12
iBetrayalPeriod = 8
iBetrayalThreshold = 66
iRebellionDelay = 15
iEscapePeriod = 30
tAIStopBirthThreshold = con.tAIStopBirthThreshold
tBirth = con.tBirth

iWorker = con.iWorker
iSettler = con.iSettler
iWarrior = con.iWarrior
iScout = con.iScout
iGalley = con.iGalley


# initialise player variables

iEgypt = con.iEgypt
iIndia = con.iIndia
iChina = con.iChina
iBabylonia = con.iBabylonia
iGreece = con.iGreece
iPersia = con.iPersia
iCarthage = con.iCarthage
iRome = con.iRome
iJapan = con.iJapan
iEthiopia = con.iEthiopia
iMaya = con.iMaya
iVikings = con.iVikings
iArabia = con.iArabia
iKhmer = con.iKhmer
iSpain = con.iSpain
iFrance = con.iFrance
iEngland = con.iEngland
iGermany = con.iGermany
iRussia = con.iRussia
iNetherlands = con.iNetherlands
iHolland = con.iHolland
iMali = con.iMali
iTurkey = con.iTurkey
iPortugal = con.iPortugal
iInca = con.iInca
iMongolia = con.iMongolia
iAztecs = con.iAztecs
iAmerica = con.iAmerica
iNumPlayers = con.iNumPlayers
iNumMajorPlayers = con.iNumMajorPlayers
iNumActivePlayers = con.iNumActivePlayers
iIndependent = con.iIndependent
iIndependent2 = con.iIndependent2
iNative = con.iNative
iCeltia = con.iCeltia
iBarbarian = con.iBarbarian
iNumTotalPlayers = con.iNumTotalPlayers


pEgypt = gc.getPlayer(iEgypt)
pIndia = gc.getPlayer(iIndia)
pChina = gc.getPlayer(iChina)
pBabylonia = gc.getPlayer(iBabylonia)
pGreece = gc.getPlayer(iGreece)
pPersia = gc.getPlayer(iPersia)
pCarthage = gc.getPlayer(iCarthage)
pRome = gc.getPlayer(iRome)
pJapan = gc.getPlayer(iJapan)
pEthiopia = gc.getPlayer(iEthiopia)
pMaya = gc.getPlayer(iMaya)
pVikings = gc.getPlayer(iVikings)
pArabia = gc.getPlayer(iArabia)
pKhmer = gc.getPlayer(iKhmer)
pSpain = gc.getPlayer(iSpain)
pFrance = gc.getPlayer(iFrance)
pEngland = gc.getPlayer(iEngland)
pGermany = gc.getPlayer(iGermany)
pRussia = gc.getPlayer(iRussia)
pNetherlands = gc.getPlayer(iNetherlands)
pHolland = gc.getPlayer(iHolland)
pMali = gc.getPlayer(iMali)
pTurkey = gc.getPlayer(iTurkey)
pPortugal = gc.getPlayer(iPortugal)
pInca = gc.getPlayer(iInca)
pMongolia = gc.getPlayer(iMongolia)
pAztecs = gc.getPlayer(iAztecs)
pAmerica = gc.getPlayer(iAmerica)
pIndependent = gc.getPlayer(iIndependent)
pIndependent2 = gc.getPlayer(iIndependent2)
pNative = gc.getPlayer(iNative)
pCeltia = gc.getPlayer(iCeltia)
pBarbarian = gc.getPlayer(iBarbarian)

teamEgypt = gc.getTeam(pEgypt.getTeam())
teamIndia = gc.getTeam(pIndia.getTeam())
teamChina = gc.getTeam(pChina.getTeam())
teamBabylonia = gc.getTeam(pBabylonia.getTeam())
teamGreece = gc.getTeam(pGreece.getTeam())
teamPersia = gc.getTeam(pPersia.getTeam())
teamCarthage = gc.getTeam(pCarthage.getTeam())
teamRome = gc.getTeam(pRome.getTeam())
teamJapan = gc.getTeam(pJapan.getTeam())
teamEthiopia = gc.getTeam(pEthiopia.getTeam())
teamMaya = gc.getTeam(pMaya.getTeam())
teamVikings = gc.getTeam(pVikings.getTeam())
teamArabia = gc.getTeam(pArabia.getTeam())
teamKhmer = gc.getTeam(pKhmer.getTeam())
teamSpain = gc.getTeam(pSpain.getTeam())
teamFrance = gc.getTeam(pFrance.getTeam())
teamEngland = gc.getTeam(pEngland.getTeam())
teamGermany = gc.getTeam(pGermany.getTeam())
teamRussia = gc.getTeam(pRussia.getTeam())
teamNetherlands = gc.getTeam(pNetherlands.getTeam())
teamHolland = gc.getTeam(pHolland.getTeam())
teamMali = gc.getTeam(pMali.getTeam())
teamTurkey = gc.getTeam(pTurkey.getTeam())
teamPortugal = gc.getTeam(pPortugal.getTeam())
teamInca = gc.getTeam(pInca.getTeam())
teamMongolia = gc.getTeam(pMongolia.getTeam())
teamAztecs = gc.getTeam(pAztecs.getTeam())
teamAmerica = gc.getTeam(pAmerica.getTeam())
teamIndependent = gc.getTeam(pIndependent.getTeam())
teamIndependent2 = gc.getTeam(pIndependent2.getTeam())
teamNative = gc.getTeam(pNative.getTeam())
teamCeltia = gc.getTeam(pCeltia.getTeam())
teamBarbarian = gc.getTeam(pBarbarian.getTeam())


#for not allowing new civ popup if too close
tDifference = (0, 0, 0, 0, 3, 2, 2, 1, 1, 1, 0, 8, 7, 6, 5, 4, 3, 2, 2, 2, 2, 3, 2, 1, 0, 0, 0)
                                                                          #ma po in mo az tu am

                    


# starting locations coordinates
tCapitals = con.tCapitals



# core areas coordinates (top left and bottom right)

tCoreAreasTL = con.tCoreAreasTL
tCoreAreasBR = con.tCoreAreasBR

tExceptions = con.tExceptions

tNormalAreasTL = con.tNormalAreasTL
tNormalAreasBR = con.tNormalAreasBR

tBroaderAreasTL = con.tBroaderAreasTL 
tBroaderAreasBR = con.tBroaderAreasBR

tLeaders = con.tLeaders
tEarlyLeaders = con.tEarlyLeaders
tLateLeaders = con.tLateLeaders

class RiseAndFall:


##################################################
### Secure storage & retrieval of script data ###
################################################
        

        def getNewCiv( self ):
                scriptDict = pickle.loads( gc.getGame().getScriptData() )
                return scriptDict['iNewCiv']

        def setNewCiv( self, iNewValue ):
                scriptDict = pickle.loads( gc.getGame().getScriptData() )
                scriptDict['iNewCiv'] = iNewValue
                gc.getGame().setScriptData( pickle.dumps(scriptDict) )        

        def getNewCivFlip( self ):
                scriptDict = pickle.loads( gc.getGame().getScriptData() )
                return scriptDict['iNewCivFlip']

        def setNewCivFlip( self, iNewValue ):
                scriptDict = pickle.loads( gc.getGame().getScriptData() )
                scriptDict['iNewCivFlip'] = iNewValue
                gc.getGame().setScriptData( pickle.dumps(scriptDict) )      

        def getOldCivFlip( self ):
                scriptDict = pickle.loads( gc.getGame().getScriptData() )
                return scriptDict['iOldCivFlip']

        def setOldCivFlip( self, iNewValue ):
                scriptDict = pickle.loads( gc.getGame().getScriptData() )
                scriptDict['iOldCivFlip'] = iNewValue
                gc.getGame().setScriptData( pickle.dumps(scriptDict) )
                
        def getTempTopLeft( self ):
                scriptDict = pickle.loads( gc.getGame().getScriptData() )
                return scriptDict['tempTopLeft']

        def setTempTopLeft( self, tNewValue ):
                scriptDict = pickle.loads( gc.getGame().getScriptData() )
                scriptDict['tempTopLeft'] = tNewValue
                gc.getGame().setScriptData( pickle.dumps(scriptDict) ) 

        def getTempBottomRight( self ):
                scriptDict = pickle.loads( gc.getGame().getScriptData() )
                return scriptDict['tempBottomRight']

        def setTempBottomRight( self, tNewValue ):
                scriptDict = pickle.loads( gc.getGame().getScriptData() )
                scriptDict['tempBottomRight'] = tNewValue
                gc.getGame().setScriptData( pickle.dumps(scriptDict) ) 

        def getSpawnWar( self ):
                scriptDict = pickle.loads( gc.getGame().getScriptData() )
                return scriptDict['iSpawnWar']

        def setSpawnWar( self, iNewValue ):
                scriptDict = pickle.loads( gc.getGame().getScriptData() )
                scriptDict['iSpawnWar'] = iNewValue
                gc.getGame().setScriptData( pickle.dumps(scriptDict) )

        def getAlreadySwitched( self ):
                scriptDict = pickle.loads( gc.getGame().getScriptData() )
                return scriptDict['bAlreadySwitched']

        def setAlreadySwitched( self, bNewValue ):
                scriptDict = pickle.loads( gc.getGame().getScriptData() )
                scriptDict['bAlreadySwitched'] = bNewValue
                gc.getGame().setScriptData( pickle.dumps(scriptDict) )

        def getColonistsAlreadyGiven( self, iCiv ):
                scriptDict = pickle.loads( gc.getGame().getScriptData() )
                return scriptDict['lColonistsAlreadyGiven'][iCiv]

        def setColonistsAlreadyGiven( self, iCiv, iNewValue ):
                scriptDict = pickle.loads( gc.getGame().getScriptData() )
                scriptDict['lColonistsAlreadyGiven'][iCiv] = iNewValue
                gc.getGame().setScriptData( pickle.dumps(scriptDict) )

        def getNumCities( self, iCiv ):
                scriptDict = pickle.loads( gc.getGame().getScriptData() )
                return scriptDict['lNumCities'][iCiv]

        def setNumCities( self, iCiv, iNewValue ):
                scriptDict = pickle.loads( gc.getGame().getScriptData() )
                scriptDict['lNumCities'][iCiv] = iNewValue
                gc.getGame().setScriptData( pickle.dumps(scriptDict) )
                
        def getSpawnDelay( self, iCiv ):
                scriptDict = pickle.loads( gc.getGame().getScriptData() )
                return scriptDict['lSpawnDelay'][iCiv]

        def setSpawnDelay( self, iCiv, iNewValue ):
                scriptDict = pickle.loads( gc.getGame().getScriptData() )
                scriptDict['lSpawnDelay'][iCiv] = iNewValue
                gc.getGame().setScriptData( pickle.dumps(scriptDict) )

        def getFlipsDelay( self, iCiv ):
                scriptDict = pickle.loads( gc.getGame().getScriptData() )
                return scriptDict['lFlipsDelay'][iCiv]

        def setFlipsDelay( self, iCiv, iNewValue ):
                scriptDict = pickle.loads( gc.getGame().getScriptData() )
                scriptDict['lFlipsDelay'][iCiv] = iNewValue
                gc.getGame().setScriptData( pickle.dumps(scriptDict) )

        def getBetrayalTurns( self ):
                scriptDict = pickle.loads( gc.getGame().getScriptData() )
                return scriptDict['iBetrayalTurns']

        def setBetrayalTurns( self, iNewValue ):
                scriptDict = pickle.loads( gc.getGame().getScriptData() )
                scriptDict['iBetrayalTurns'] = iNewValue
                gc.getGame().setScriptData( pickle.dumps(scriptDict) )  

        def getLatestFlipTurn( self ):
                scriptDict = pickle.loads( gc.getGame().getScriptData() )
                return scriptDict['iLatestFlipTurn']

        def setLatestFlipTurn( self, iNewValue ):
                scriptDict = pickle.loads( gc.getGame().getScriptData() )
                scriptDict['iLatestFlipTurn'] = iNewValue
                gc.getGame().setScriptData( pickle.dumps(scriptDict) )

        def getLatestRebellionTurn( self, iCiv ):
                scriptDict = pickle.loads( gc.getGame().getScriptData() )
                return scriptDict['lLatestRebellionTurn'][iCiv]

        def setLatestRebellionTurn( self, iCiv, iNewValue ):
                scriptDict = pickle.loads( gc.getGame().getScriptData() )
                scriptDict['lLatestRebellionTurn'][iCiv] = iNewValue
                gc.getGame().setScriptData( pickle.dumps(scriptDict) )

        def getRebelCiv( self ):
                scriptDict = pickle.loads( gc.getGame().getScriptData() )
                return scriptDict['iRebelCiv']

        def setRebelCiv( self, iNewValue ):
                scriptDict = pickle.loads( gc.getGame().getScriptData() )
                scriptDict['iRebelCiv'] = iNewValue
                gc.getGame().setScriptData( pickle.dumps(scriptDict) )
                
        def getExileData( self, i ):
                scriptDict = pickle.loads( gc.getGame().getScriptData() )
                return scriptDict['lExileData'][i]

        def setExileData( self, i, iNewValue ):
                scriptDict = pickle.loads( gc.getGame().getScriptData() )
                scriptDict['lExileData'][i] = iNewValue
                gc.getGame().setScriptData( pickle.dumps(scriptDict) )
        
        def getTempFlippingCity( self ):
                scriptDict = pickle.loads( gc.getGame().getScriptData() )
                return scriptDict['tempFlippingCity']

        def setTempFlippingCity( self, tNewValue ):
                scriptDict = pickle.loads( gc.getGame().getScriptData() )
                scriptDict['tempFlippingCity'] = tNewValue
                gc.getGame().setScriptData( pickle.dumps(scriptDict) ) 

        def getCheatersCheck( self, i ):
                scriptDict = pickle.loads( gc.getGame().getScriptData() )
                return scriptDict['lCheatersCheck'][i]

        def setCheatersCheck( self, i, iNewValue ):
                scriptDict = pickle.loads( gc.getGame().getScriptData() )
                scriptDict['lCheatersCheck'][i] = iNewValue
                gc.getGame().setScriptData( pickle.dumps(scriptDict) )

        def getBirthTurnModifier( self, iCiv ):
                scriptDict = pickle.loads( gc.getGame().getScriptData() )
                return scriptDict['lBirthTurnModifier'][iCiv]

        def setBirthTurnModifier( self, iCiv, iNewValue ):
                scriptDict = pickle.loads( gc.getGame().getScriptData() )
                scriptDict['lBirthTurnModifier'][iCiv] = iNewValue
                gc.getGame().setScriptData( pickle.dumps(scriptDict) )   

        def getDeleteMode( self, i ):
                scriptDict = pickle.loads( gc.getGame().getScriptData() )
                return scriptDict['lDeleteMode'][i]

        def setDeleteMode( self, i, iNewValue ):
                scriptDict = pickle.loads( gc.getGame().getScriptData() )
                scriptDict['lDeleteMode'][i] = iNewValue
                gc.getGame().setScriptData( pickle.dumps(scriptDict) )

        def getFirstContactConquerors( self, iCiv ):
                scriptDict = pickle.loads( gc.getGame().getScriptData() )
                return scriptDict['lFirstContactConquerors'][iCiv]

        def setFirstContactConquerors( self, iCiv, iNewValue ):
                scriptDict = pickle.loads( gc.getGame().getScriptData() )
                scriptDict['lFirstContactConquerors'][iCiv] = iNewValue
                gc.getGame().setScriptData( pickle.dumps(scriptDict) ) 
                
###############
### Popups ###
#############

        ''' popupID has to be a registered ID in CvRhyesCatapultEventManager.__init__!! '''
        def showPopup(self, popupID, title, message, labels):
                popup = Popup.PyPopup(popupID, EventContextTypes.EVENTCONTEXT_ALL)
                popup.setHeaderString(title)
                popup.setBodyString(message)
                for i in labels:
                    popup.addButton( i )
                popup.launch(False)


        def newCivPopup(self, iCiv):
                self.showPopup(7614, CyTranslator().getText("TXT_KEY_NEWCIV_TITLE", ()), CyTranslator().getText("TXT_KEY_NEWCIV_MESSAGE", (gc.getPlayer(iCiv).getCivilizationAdjectiveKey(),)), (CyTranslator().getText("TXT_KEY_POPUP_YES", ()), CyTranslator().getText("TXT_KEY_POPUP_NO", ())))
                self.setNewCiv(iCiv)

        def eventApply7614(self, popupReturn):
                if( popupReturn.getButtonClicked() == 0 ): # 1st button
                        iOldHandicap = gc.getActivePlayer().getHandicapType()
                        gc.getActivePlayer().setHandicapType(gc.getPlayer(self.getNewCiv()).getHandicapType())
                        gc.getGame().setActivePlayer(self.getNewCiv(), False)
                        gc.getPlayer(self.getNewCiv()).setHandicapType(iOldHandicap)
                        for i in range(con.iNumStabilityParameters):
                                utils.setStabilityParameters(i, 0)
                        utils.setLastRecordedStabilityStuff(0, 0)
                        utils.setLastRecordedStabilityStuff(1, 0)
                        utils.setLastRecordedStabilityStuff(2, 0)
                        utils.setLastRecordedStabilityStuff(3, 0)
                        utils.setLastRecordedStabilityStuff(4, 0)
                        utils.setLastRecordedStabilityStuff(5, 0)
                        for iMaster in range(con.iNumPlayers):
                                if (gc.getTeam(gc.getPlayer(self.getNewCiv()).getTeam()).isVassal(iMaster)):
                                        gc.getTeam(gc.getPlayer(self.getNewCiv()).getTeam()).setVassal(iMaster, False, False)
                        self.setAlreadySwitched(True)
                        gc.getPlayer(self.getNewCiv()).setPlayable(True)
                        #CyInterface().addImmediateMessage("first button", "")
                #elif( popupReturn.getButtonClicked() == 1 ): # 2nd button
                        #CyInterface().addImmediateMessage("second button", "")


        def flipPopup(self, iNewCiv, tTopLeft, tBottomRight):
                iHuman = utils.getHumanID()
                flipText = CyTranslator().getText("TXT_KEY_FLIPMESSAGE1", ())
                for x in range(tTopLeft[0], tBottomRight[0]+1):
                        for y in range(tTopLeft[1], tBottomRight[1]+1):
                                pCurrent = gc.getMap().plot( x, y )
                                if ( pCurrent.isCity()):
                                        if (pCurrent.getPlotCity().getOwner() == iHuman):
                                                if (not pCurrent.getPlotCity().isCapital()):
                                                        flipText += (pCurrent.getPlotCity().getName() + "\n")
                #exceptions
                if (len(tExceptions[iNewCiv])):
                        for j in range(len(tExceptions[iNewCiv])):
                                pCurrent = gc.getMap().plot( tExceptions[iNewCiv][j][0], tExceptions[iNewCiv][j][1] )
                                if (pCurrent.isCity()):
                                        if (pCurrent.getPlotCity().getOwner() == iHuman):
                                                if (not pCurrent.getPlotCity().isCapital()):
                                                        flipText += (pCurrent.getPlotCity().getName() + "\n")                                                
                flipText += CyTranslator().getText("TXT_KEY_FLIPMESSAGE2", ())
                                                        
                self.showPopup(7615, CyTranslator().getText("TXT_KEY_NEWCIV_TITLE", ()), flipText, (CyTranslator().getText("TXT_KEY_POPUP_YES", ()), CyTranslator().getText("TXT_KEY_POPUP_NO", ())))
                self.setNewCivFlip(iNewCiv)
                self.setOldCivFlip(iHuman)
                self.setTempTopLeft(tTopLeft)
                self.setTempBottomRight(tBottomRight)

        def eventApply7615(self, popupReturn):
                iHuman = utils.getHumanID()
                tTopLeft = self.getTempTopLeft()
                tBottomRight = self.getTempBottomRight()
                iNewCivFlip = self.getNewCivFlip()

                humanCityList = []
                for x in range(tTopLeft[0], tBottomRight[0]+1):
                        for y in range(tTopLeft[1], tBottomRight[1]+1):
                                pCurrent = gc.getMap().plot( x, y )
                                if ( pCurrent.isCity()):
                                        city = pCurrent.getPlotCity()
                                        if (city.getOwner() == iHuman):
                                                if (not city.isCapital()):
                                                        humanCityList.append(city)
                #exceptions
                if (len(tExceptions[iNewCivFlip])):
                        for j in range(len(tExceptions[self.getNewCivFlip()])):
                                pCurrent = gc.getMap().plot( tExceptions[iNewCivFlip][j][0], tExceptions[iNewCivFlip][j][1] )
                                if (pCurrent.isCity()):
                                        city = pCurrent.getPlotCity()
                                        if (city.getOwner() == iHuman):
                                                if (not city.isCapital()):
                                                        humanCityList.append(city)
                
                if( popupReturn.getButtonClicked() == 0 ): # 1st button
                        print ("Flip agreed")
                        CyInterface().addMessage(iHuman, True, con.iDuration, CyTranslator().getText("TXT_KEY_FLIP_AGREED", ()), "", 0, "", ColorTypes(con.iGreen), -1, -1, True, True)
                                                
                        if (len(humanCityList)):
                                for i in range(len(humanCityList)):
                                        city = humanCityList[i]
                                        print ("flipping ", city.getName())
                                        utils.cultureManager((city.getX(),city.getY()), 100, iNewCivFlip, iHuman, False, False, False)
                                        utils.flipUnitsInCityBefore((city.getX(),city.getY()), iNewCivFlip, iHuman)
                                        self.setTempFlippingCity((city.getX(),city.getY()))
                                        utils.flipCity((city.getX(), city.getY()), 0, 0, iNewCivFlip, [iHuman])                                        
                                        utils.flipUnitsInCityAfter(self.getTempFlippingCity(), iNewCivFlip)

                                        #iEra = gc.getPlayer(iNewCivFlip).getCurrentEra()
                                        #if (iEra >= 2): #medieval
                                        #        if (city.getPopulation() < iEra):
                                        #                city.setPopulation(iEra) #causes an unidentifiable C++ exception

                                        #humanCityList[i].setHasRealBuilding(con.iPlague, False) #buggy

                        #same code as Betrayal - done just once to make sure human player doesn't hold a stack just outside of the cities
                        for x in range(tTopLeft[0], tBottomRight[0]+1):
                                for y in range(tTopLeft[1], tBottomRight[1]+1):
                                        betrayalPlot = gc.getMap().plot(x,y)
                                        iNumUnitsInAPlot = betrayalPlot.getNumUnits()
                                        if (iNumUnitsInAPlot):                                                                  
                                                for i in range(iNumUnitsInAPlot):                                                
                                                        unit = betrayalPlot.getUnit(i)
                                                        if (unit.getOwner() == iHuman):
                                                                rndNum = gc.getGame().getSorenRandNum(100, 'betrayal')
                                                                if (rndNum >= iBetrayalThreshold):
                                                                        if (unit.getDomainType() == 2): #land unit
                                                                                iUnitType = unit.getUnitType()
                                                                                unit.kill(False, iNewCivFlip)
                                                                                utils.makeUnit(iUnitType, iNewCivFlip, (x,y), 1)
                                                                                i = i - 1


                        if (self.getCheatersCheck(0) == 0):
                                self.setCheatersCheck(0, iCheatersPeriod)
                                self.setCheatersCheck(1, self.getNewCivFlip())
                                
                elif( popupReturn.getButtonClicked() == 1 ): # 2nd button
                        print ("Flip disagreed")
                        CyInterface().addMessage(iHuman, True, con.iDuration, CyTranslator().getText("TXT_KEY_FLIP_REFUSED", ()), "", 0, "", ColorTypes(con.iGreen), -1, -1, True, True)
                                                

                        if (len(humanCityList)):
                                for i in range(len(humanCityList)):
                                        city = humanCityList[i]
                                        #city.setCulture(self.getNewCivFlip(), city.countTotalCulture(), True)
                                        pCurrent = gc.getMap().plot(city.getX(), city.getY())
                                        oldCulture = pCurrent.getCulture(iHuman)
                                        pCurrent.setCulture(iNewCivFlip, oldCulture/2, True)
                                        pCurrent.setCulture(iHuman, oldCulture/2, True)                                        
                                        iWar = self.getSpawnWar() + 1
                                        self.setSpawnWar(iWar)
                                        if (self.getSpawnWar() == 1):
                                                #CyInterface().addImmediateMessage(CyTranslator().getText("TXT_KEY_FLIP_REFUSED", ()), "")
                                                gc.getTeam(gc.getPlayer(iNewCivFlip).getTeam()).declareWar(iHuman, False, -1) ##True??
                                                self.setBetrayalTurns(iBetrayalPeriod)
                                                self.initBetrayal()


                                        
                                                                
                                
        def rebellionPopup(self, iRebelCiv):
                self.showPopup(7622, CyTranslator().getText("TXT_KEY_REBELLION_TITLE", ()), \
                               CyTranslator().getText("TXT_KEY_REBELLION_TEXT", (gc.getPlayer(iRebelCiv).getCivilizationAdjectiveKey(),)), \
                               (CyTranslator().getText("TXT_KEY_POPUP_YES", ()), \
                                CyTranslator().getText("TXT_KEY_POPUP_NO", ())))
                

        def eventApply7622(self, popupReturn):
                iHuman = utils.getHumanID()
                iRebelCiv = self.getRebelCiv()
                if( popupReturn.getButtonClicked() == 0 ): # 1st button
                        gc.getTeam(gc.getPlayer(iHuman).getTeam()).makePeace(iRebelCiv)                                                   
                elif( popupReturn.getButtonClicked() == 1 ): # 2nd button
                        gc.getTeam(gc.getPlayer(iHuman).getTeam()).declareWar(iRebelCiv, False, -1)



#######################################
### Main methods (Event-Triggered) ###
#####################################  

        def setup(self):            

                #self.setupBirthTurnModifiers() (causes a crash on civ switch)

                if (not gc.getPlayer(0).isPlayable()): #late start condition
                        self.clear600ADChina()

                if (gc.getPlayer(0).isPlayable()): #late start condition
                        self.create4000BCstartingUnits()
                else:
                        self.create600ADstartingUnits()
                #self.assign4000BCtechs()
                self.setEarlyLeaders()


                if (not gc.getPlayer(0).isPlayable()): #late start condition
                        self.assign600ADTechs()
                        pChina.changeGold(300)
                        pJapan.changeGold(150)
                        pIndependent.changeGold(100)
                        pIndependent2.changeGold(100)
                        pNative.changeGold(300)
                        pCeltia.changeGold(500)
                        utils.setStability(iVikings, utils.getStability(iVikings) + 2)
                        utils.setStability(iChina, utils.getStability(iChina) + 3)
                        utils.setStability(iJapan, utils.getStability(iJapan) + 4)
                        utils.setGoal(iEgypt, 0, 0)
                        utils.setGoal(iEgypt, 1, 0)
                        utils.setGoal(iEgypt, 2, 0)
                        utils.setGoal(iIndia, 0, 0)
                        utils.setGoal(iIndia, 1, 0)
                        utils.setGoal(iIndia, 2, 0)
                        utils.setGoal(iBabylonia, 0, 0)
                        utils.setGoal(iBabylonia, 1, 0)
                        utils.setGoal(iBabylonia, 2, 0)
                        utils.setGoal(iGreece, 0, 0)
                        utils.setGoal(iGreece, 1, 0)
                        utils.setGoal(iGreece, 2, 0)
                        utils.setGoal(iPersia, 0, 0)
                        utils.setGoal(iPersia, 1, 0)
                        utils.setGoal(iPersia, 2, 0)
                        utils.setGoal(iCarthage, 0, 0)
                        utils.setGoal(iCarthage, 1, 0)
                        utils.setGoal(iCarthage, 2, 0)
                        utils.setGoal(iRome, 0, 0)
                        utils.setGoal(iRome, 1, 0)
                        utils.setGoal(iRome, 2, 0)
                        utils.setGoal(iEthiopia, 0, 0)
                        utils.setGoal(iEthiopia, 1, 0)
                        utils.setGoal(iEthiopia, 2, 0)
                        utils.setGoal(iMaya, 0, 0)
                        utils.setGoal(iMaya, 1, 0)
                        utils.setGoal(iMaya, 2, 0)
                else:
                        utils.setStability(iChina, utils.getStability(iChina) + 2)
                        utils.setStability(iIndia, utils.getStability(iIndia) + 2)
                        pIndependent.changeGold(50)
                        pIndependent2.changeGold(50)
                        pNative.changeGold(100)
                               
                # set starting gold
                pGreece.changeGold(100)
                pCarthage.changeGold(200)
                pRome.changeGold(100)
                pPersia.changeGold(200)
                pJapan.changeGold(100)
                pEthiopia.changeGold(100)
                pMaya.changeGold(200)
                pVikings.changeGold(150)
                pArabia.changeGold(300)
                pKhmer.changeGold(200)
                pSpain.changeGold(200)
                pFrance.changeGold(150)    
                pEngland.changeGold(200)
                pGermany.changeGold(150)
                pRussia.changeGold(200)
                pNetherlands.changeGold(300)
                pMali.changeGold(600)                
                pPortugal.changeGold(200)
                pInca.changeGold(700)
                pMongolia.changeGold(250) 
                pAztecs.changeGold(600)
                pTurkey.changeGold(300)
                pAmerica.changeGold(1500)
               
           
                # display welcome message
                #self.displayWelcomePopup()

                #center camera on Egyptian units
                if (pEgypt.isHuman()):
                        plotEgypt = gc.getMap().plot(tCapitals[iEgypt][0], tCapitals[iEgypt][1])   
                        unit = plotEgypt.getUnit(0)
                        unit.centerCamera()
                        #print (unit)


        def clear600ADChina(self):
                pGuiyang = gc.getMap().plot(102, 41)
                #pBarbarian.raze(pGuiyang.getPlotCity())
                pGuiyang.getPlotCity().kill()
                pGuiyang.setImprovementType(-1)
                pGuiyang.setRouteType(-1)
                pGuiyang.setFeatureType(con.iForest, 0)
                tCultureRegionTL = (98, 37)
                tCultureRegionBR = (109, 49)
                for x in range(tCultureRegionTL[0], tCultureRegionBR[0]+1):       
                        for y in range(tCultureRegionTL[1], tCultureRegionBR[1]+1):	
                                pCurrent = gc.getMap().plot(x, y)
                                bCity = False
                                for iX in range(x-1, x+2):        # from x-1 to x+1
                                        for iY in range(y-1, y+2):	# from y-1 to y+1
                                                loopPlot = gc.getMap().plot(iX, iY)
                                                if (loopPlot.isCity()):
                                                     bCity = True
                                                     loopPlot.getPlotCity().setCulture(iIndependent2, 0, False)
                                if (bCity):                                
                                        pCurrent.setCulture(iIndependent2, 1, True)
                                else:
                                        pCurrent.setCulture(iIndependent2, 0, True)
                                        pCurrent.setOwner(-1)
                
                


        def setupBirthTurnModifiers(self):
                for iCiv in range(iNumPlayers):
                        if (iCiv >= iGreece and not gc.getPlayer(iCiv).isHuman()):
                                self.setBirthTurnModifier(iCiv, (gc.getGame().getSorenRandNum(11, 'BirthTurnModifier') - 5)) # -5 to +5
                #now make sure that no civs spawn in the same turn and cause a double "new civ" popup
                for iCiv in range(iNumPlayers):
                        if (iCiv > utils.getHumanID() and iCiv < iAmerica):
                                for j in range(iNumPlayers-1-iCiv):
                                        iNextCiv = iCiv+j+1
                                        if (con.tBirth[iCiv]+self.getBirthTurnModifier(iCiv) == con.tBirth[iNextCiv]+self.getBirthTurnModifier(iNextCiv)):
                                                self.setBirthTurnModifier(iNextCiv, (self.getBirthTurnModifier(iNextCiv)+1))



        def setEarlyLeaders(self):
                for i in range(iNumActivePlayers):
                        if (tEarlyLeaders[i] != tLeaders[i][0]):
                                if (not gc.getPlayer(i).isHuman()):
                                        gc.getPlayer(i).setLeader(tEarlyLeaders[i])
                                        print ("leader starting switch:", tEarlyLeaders[i], "in civ", i)
                                
        	
        def checkTurn(self, iGameTurn):

                #debug
                
                
                #Trigger betrayal mode
                if (self.getBetrayalTurns() > 0):
                        self.initBetrayal()

                if (self.getCheatersCheck(0) > 0):
                        teamPlayer = gc.getTeam(gc.getPlayer(utils.getHumanID()).getTeam())
                        if (teamPlayer.isAtWar(self.getCheatersCheck(1))):
                                print ("No cheaters!")
                                self.initMinorBetrayal(self.getCheatersCheck(1))
                                self.setCheatersCheck(0, 0)
                                self.setCheatersCheck(1, -1)
                        else:
                                self.setCheatersCheck(0, self.getCheatersCheck(0)-1)

                if (iGameTurn % 20 == 0):
                        if (pIndependent.isAlive()):                                  
                                utils.updateMinorTechs(iIndependent, iBarbarian)
                        if (pIndependent2.isAlive()):                                  
                                utils.updateMinorTechs(iIndependent2, iBarbarian)

                #Colonists
                if (iGameTurn >= (con.i1350AD + 5 + self.getColonistsAlreadyGiven(iSpain)*6)) and (iGameTurn <= con.i1918AD):
                        self.giveColonists(iSpain, tBroaderAreasTL[iSpain], tBroaderAreasBR[iSpain])
                if (iGameTurn >= (con.i1450AD + 5 + self.getColonistsAlreadyGiven(iEngland)*6)) and (iGameTurn <= con.i1918AD):
                        self.giveColonists(iEngland, tBroaderAreasTL[iEngland], tBroaderAreasBR[iEngland])
                if (iGameTurn >= (con.i1450AD + 5 + self.getColonistsAlreadyGiven(iFrance)*6)) and (iGameTurn <= con.i1918AD):
                        self.giveColonists(iFrance, tBroaderAreasTL[iFrance], tBroaderAreasBR[iFrance])
                if (iGameTurn >= (con.i1350AD + 5 + self.getColonistsAlreadyGiven(iPortugal)*6)) and (iGameTurn <= con.i1918AD):
                        self.giveColonists(iPortugal, tNormalAreasTL[iPortugal], tNormalAreasBR[iPortugal])
                if (iGameTurn >= (con.i1450AD + 5 + self.getColonistsAlreadyGiven(iHolland)*6)) and (iGameTurn <= con.i1918AD):
                        self.giveColonists(iHolland, tNormalAreasTL[iHolland], tNormalAreasBR[iHolland])
                        
                #birth of civs
##                if (gc.getPlayer(0).isPlayable()): #late start condition
##                        self.initBirth(iGameTurn, con.tBirth[iGreece], iGreece)
##                        self.initBirth(iGameTurn, con.tBirth[iPersia], iPersia)    
##                        self.initBirth(iGameTurn, con.tBirth[iCarthage], iCarthage)
##                        self.initBirth(iGameTurn, con.tBirth[iRome], iRome)
##                        self.initBirth(iGameTurn, con.tBirth[iJapan], iJapan)
##                        self.initBirth(iGameTurn, con.tBirth[iEthiopia], iEthiopia)
##                        self.initBirth(iGameTurn, con.tBirth[iMaya], iMaya)
##                        self.initBirth(iGameTurn, con.tBirth[iVikings], iVikings)
##                        self.initBirth(iGameTurn, con.tBirth[iArabia], iArabia)
##                self.initBirth(iGameTurn, con.tBirth[iKhmer], iKhmer)
##                self.initBirth(iGameTurn, con.tBirth[iSpain], iSpain)
##                self.initBirth(iGameTurn, con.tBirth[iFrance], iFrance)
##                self.initBirth(iGameTurn, con.tBirth[iEngland], iEngland)
##                self.initBirth(iGameTurn, con.tBirth[iGermany], iGermany)
##                self.initBirth(iGameTurn, con.tBirth[iRussia], iRussia)
##                self.initBirth(iGameTurn, con.tBirth[iNetherlands], iNetherlands)
##                self.initBirth(iGameTurn, con.tBirth[iMali], iMali)
##                self.initBirth(iGameTurn, con.tBirth[iTurkey], iTurkey)
##                self.initBirth(iGameTurn, con.tBirth[iPortugal], iPortugal)
##                self.initBirth(iGameTurn, con.tBirth[iInca], iInca)
##                self.initBirth(iGameTurn, con.tBirth[iMongolia], iMongolia)
##                self.initBirth(iGameTurn, con.tBirth[iAztecs], iAztecs)
##                self.initBirth(iGameTurn, con.tBirth[iAmerica], iAmerica)
                        
                if (gc.getPlayer(0).isPlayable()):
                        iFirstSpawn = iGreece
                else:
                        iFirstSpawn = iKhmer
                for iLoopCiv in range(iFirstSpawn, iNumMajorPlayers):
                        if (iGameTurn >= con.tBirth[iLoopCiv] - 2 and iGameTurn <= con.tBirth[iLoopCiv] + 6):
                                self.initBirth(iGameTurn, con.tBirth[iLoopCiv], iLoopCiv)



                if (iGameTurn == 151):
                        if (not gc.getPlayer(0).isPlayable()):  #late start condition
                                print ("late start")
                                iNumAICitiesConverted, iNumHumanCitiesToConvert = self.convertSurroundingCities(iChina, tCoreAreasTL[iChina], tCoreAreasBR[iChina])
                                self.convertSurroundingPlotCulture(iChina, tCoreAreasTL[iChina], tCoreAreasBR[iChina])
                                utils.flipUnitsInArea(tCoreAreasTL[iChina], tCoreAreasBR[iChina], iChina, iBarbarian, False, True) #remaining barbs in the region now belong to the new civ   
                                utils.flipUnitsInArea(tCoreAreasTL[iChina], tCoreAreasBR[iChina], iChina, iIndependent, False, False) #remaining independents in the region now belong to the new civ   
                                utils.flipUnitsInArea(tCoreAreasTL[iChina], tCoreAreasBR[iChina], iChina, iIndependent2, False, False) #remaining independents in the region now belong to the new civ   
                                iNumAICitiesConverted, iNumHumanCitiesToConvert = self.convertSurroundingCities(iArabia, (69, 30), (82, 36))
                                self.convertSurroundingPlotCulture(iArabia, tNormalAreasTL[iArabia], (82, 36))
                                utils.flipUnitsInArea(tNormalAreasTL[iArabia], (82, 36), iArabia, iBarbarian, False, True) #remaining barbs in the region now belong to the new civ   
                                utils.flipUnitsInArea(tNormalAreasTL[iArabia], (82, 36), iArabia, iIndependent, False, False) #remaining independents in the region now belong to the new civ   
                                utils.flipUnitsInArea(tNormalAreasTL[iArabia], (82, 36), iArabia, iIndependent2, False, False) #remaining independents in the region now belong to the new civ
                                #teamArabia.setHasTech(con.iDivineRight, True, iArabia, False, False)
                        

##                bHolland = self.minorBirth(iGameTurn, iHolland, tCapitals[iHolland], "Amsterdam", 3)
##                if (not bHolland):
##                        bHolland = self.minorBirth(iGameTurn, iHolland, con.tReserveCapitals[iHolland][0], "Amsterdam", 3)
##                if (not bHolland):
##                        bHolland = self.minorBirth(iGameTurn, iHolland, con.tReserveCapitals[iHolland][1], "Rotterdam", 3)
##                if (not bHolland):
##                        bHolland = self.minorBirth(iGameTurn, iHolland, con.tReserveCapitals[iHolland][2], "Groningen", 3)
##                bPortugal = self.minorBirth(iGameTurn, iPortugal, tCapitals[iPortugal], "Lisboa", 3)
##                if (not bPortugal):
##                        bPortugal =  self.minorBirth(iGameTurn, iPortugal, con.tReserveCapitals[iPortugal][0], "Lisboa", 3)
##                if (not bPortugal):
##                        bPortugal =  self.minorBirth(iGameTurn, iPortugal, con.tReserveCapitals[iPortugal][1], "Oporto", 3)
                        
                #flip Mesopotamia
                #if (iGameTurn == 1):
                #        self.convertSurroundingCities(iBabylonia, tBroaderAreasTL[iBabylonia], tBroaderAreasBR[iBabylonia])


                #fragment utility
                if (iGameTurn >= con.i50AD and iGameTurn % 15 == 6):
                        self.fragmentIndependents()
                if (iGameTurn >= con.i450AD and iGameTurn % 30 == 12):
                        self.fragmentBarbarians(iGameTurn)
                        
                #fall of civs
                if (iGameTurn >= con.i476AD and iGameTurn % 4 == 0):
                        self.collapseByBarbs(iGameTurn)                                        
                if (iGameTurn >= con.i2000BC and iGameTurn % 18 == 0): #used to be 15 in vanilla, because we must give some time for vassal states to form
                        self.collapseGeneric(iGameTurn)
                if (iGameTurn >= con.i2000BC and iGameTurn % 11 == 7): #used to be 8 in vanilla, because we must give some time for vassal states to form
                        self.collapseMotherland(iGameTurn)
                if (iGameTurn > con.i450AD and iGameTurn % 14 == 3):
                        self.secession(iGameTurn)
                #debug
                #self.collapseMotherland()

                #resurrection of civs
                iNumDeadCivs1 = 11 #5 in vanilla, 8 in warlords (that includes native and celt)
                iNumDeadCivs2 = 9 #3 in vanilla, 6 in Warlords: here we must count natives and celts as dead too
                #if (not gc.getPlayer(0).isPlayable()):  #late start condition
                #        iNumDeadCivs1 -= 2
                #        iNumDeadCivs2 -= 2
                if (gc.getGame().countCivPlayersEverAlive() - gc.getGame().countCivPlayersAlive() > iNumDeadCivs1): 
                        if (iGameTurn % 15 == 10):
                                self.resurrection(iGameTurn)                        
                elif (gc.getGame().countCivPlayersEverAlive() - gc.getGame().countCivPlayersAlive() > iNumDeadCivs2): 
                        if (iGameTurn % 30 == 15):
                                self.resurrection(iGameTurn)

                

                #debug
                #self.resurrection(iGameTurn)          
                #self.resurrectionFromBarbs(iGameTurn)




        def checkPlayerTurn(self, iGameTurn, iPlayer):
                #switch leader on first anarchy if early leader is different from primary one, and in a late game anarchy period to a late leader              
##                if (len(tLeaders[iPlayer]) > 1):
##                        if (tEarlyLeaders[iPlayer] != tLeaders[iPlayer][0]):
##                                if (iGameTurn > tBirth[iPlayer]+3 and iGameTurn < tBirth[iPlayer]+50):
##                                        if (gc.getPlayer(iPlayer).getAnarchyTurns() != 0):                                        
##                                                gc.getPlayer(iPlayer).setLeader(tLeaders[iPlayer][0])
##                                                print ("leader early switch:", tLeaders[iPlayer][0], "in civ", iPlayer)                        
##                        elif (iGameTurn >= tLateLeaders[iPlayer][1]):
##                                if (tLateLeaders[iPlayer][0] != tLeaders[iPlayer][0]):   
##                                        if (gc.getPlayer(iPlayer).getAnarchyTurns() != 0):                                                                                     
##                                                gc.getPlayer(iPlayer).setLeader(tLateLeaders[iPlayer][0])
##                                                print ("leader late switch:", tLateLeaders[iPlayer][0], "in civ", iPlayer) 
                if (len(tLeaders[iPlayer]) > 1):
                        if (len(tLateLeaders[iPlayer]) > 5):
                                if (iGameTurn >= tLateLeaders[iPlayer][5]):
                                        self.switchLateLeaders(iPlayer, 4)
                                elif (iGameTurn >= tLateLeaders[iPlayer][1]):
                                        self.switchLateLeaders(iPlayer, 0)
                        else:
                                if (iGameTurn >= tLateLeaders[iPlayer][1]):
                                        self.switchLateLeaders(iPlayer, 0)
            



        def switchLateLeaders(self, iPlayer, iLeaderIndex):
                if (tLateLeaders[iPlayer][iLeaderIndex] != gc.getPlayer(iPlayer).getLeader()):
                        iThreshold = tLateLeaders[iPlayer][iLeaderIndex+2]
                        if (gc.getPlayer(iPlayer).getCurrentEra() >= tLateLeaders[iPlayer][iLeaderIndex+3]):
                                iThreshold *= 2
                        if (gc.getPlayer(iPlayer).getAnarchyTurns() != 0 or \
                            utils.getPlagueCountdown(iPlayer) > 0 or \
                            utils.getGreatDepressionCountdown(iPlayer) > 0 or \
                            utils.getStability(iPlayer) <= -10 or \
                            gc.getGame().getSorenRandNum(100, 'die roll') < iThreshold):
                                gc.getPlayer(iPlayer).setLeader(tLateLeaders[iPlayer][iLeaderIndex])
                                print ("leader late switch:", tLateLeaders[iPlayer][iLeaderIndex], "in civ", iPlayer)
                                if (gc.getPlayer(iPlayer).getLeader() == con.iStalin):
                                        russianCityList = PyPlayer(iPlayer).getCityList()
                                        for pCity in russianCityList:
                                                city = pCity.GetCy()
                                                if (city.getName() == 'Caricyn'):
                                                        city.setName('Stalingrad', False)
                                                elif (city.getName() == 'Sankt-Peterburg'):
                                                        city.setName('Leningrad', False)
            
            

        def fragmentIndependents(self):

                if (pIndependent.getNumCities() > 8 or pIndependent2.getNumCities() > 8 ):
                        iBigIndependent = -1
                        iSmallIndependent = -1
                        if (pIndependent.getNumCities() > 2*pIndependent2.getNumCities()):
                                iBigIndependent = iIndependent
                                iSmallIndependent = iIndependent2
                        if (2*pIndependent.getNumCities() < 2*pIndependent2.getNumCities()):
                                iBigIndependent = iIndependent2
                                iSmallIndependent = iIndependent
                        if (iBigIndependent != -1):
                                iDivideCounter = 0
                                iCounter = 0
                                cityList = []
                                apCityList = PyPlayer(iBigIndependent).getCityList()
                                for pCity in apCityList:
                                        iDivideCounter += 1 #convert 3 random cities cycling just once
                                        if (iDivideCounter % 2 == 1):
                                                city = pCity.GetCy()
                                                pCurrent = gc.getMap().plot(city.getX(), city.getY())                                        
                                                utils.cultureManager((city.getX(),city.getY()), 50, iSmallIndependent, iBigIndependent, False, True, True)
                                                utils.flipUnitsInCityBefore((city.getX(),city.getY()), iSmallIndependent, iBigIndependent)                            
                                                self.setTempFlippingCity((city.getX(),city.getY()))
                                                utils.flipCity((city.getX(),city.getY()), 0, 0, iSmallIndependent, [iBigIndependent])   #by trade because by conquest may raze the city
                                                utils.flipUnitsInCityAfter(self.getTempFlippingCity(), iSmallIndependent)
                                                iCounter += 1
                                                if (iCounter == 3):
                                                        return



        def fragmentBarbarians(self, iGameTurn):

                iRndnum = gc.getGame().getSorenRandNum(iNumPlayers, 'starting count')
                for j in range(iRndnum, iRndnum + iNumPlayers):
                        iDeadCiv = j % iNumPlayers                                                        
                        if (not gc.getPlayer(iDeadCiv).isAlive() and iGameTurn > con.tBirth[iDeadCiv] + 50):
                                pDeadCiv = gc.getPlayer(iDeadCiv)
                                teamDeadCiv = gc.getTeam(pDeadCiv.getTeam())
                                iCityCounter = 0
                                for x in range(tNormalAreasTL[iDeadCiv][0], tNormalAreasBR[iDeadCiv][0]+1):
                                        for y in range(tNormalAreasTL[iDeadCiv][1], tNormalAreasBR[iDeadCiv][1]+1):
                                                pCurrent = gc.getMap().plot( x, y )
                                                if ( pCurrent.isCity()):
                                                        if (pCurrent.getPlotCity().getOwner() == iBarbarian):
                                                                iCityCounter += 1
                                if (iCityCounter > 3):
                                        iDivideCounter = 0
                                        for x in range(tNormalAreasTL[iDeadCiv][0], tNormalAreasBR[iDeadCiv][0]+1):
                                                for y in range(tNormalAreasTL[iDeadCiv][1], tNormalAreasBR[iDeadCiv][1]+1):
                                                        pCurrent = gc.getMap().plot( x, y )
                                                        if ( pCurrent.isCity()):
                                                                city = pCurrent.getPlotCity()
                                                                if (city.getOwner() == iBarbarian):
                                                                        if (iDivideCounter % 4 == 0):
                                                                                iNewCiv = iIndependent
                                                                        elif (iDivideCounter % 4 == 1):
                                                                                iNewCiv = iIndependent2
                                                                        if (iDivideCounter % 4 == 0 or iDivideCounter % 4 == 1):
                                                                                utils.cultureManager((city.getX(),city.getY()), 50, iNewCiv, iBarbarian, False, True, True)
                                                                                utils.flipUnitsInCityBefore((city.getX(),city.getY()), iNewCiv, iBarbarian)                            
                                                                                self.setTempFlippingCity((city.getX(),city.getY()))
                                                                                utils.flipCity((city.getX(),city.getY()), 0, 0, iNewCiv, [iBarbarian])   #by trade because by conquest may raze the city
                                                                                utils.flipUnitsInCityAfter(self.getTempFlippingCity(), iNewCiv)
                                                                                iDivideCounter += 1
                                        return






##        def collapseCapitals(self, iOldOwner, city, iNewOwner):
##        #Persian UP inside
##        #AI tweaked in CvCity::getCulturePercentAnger()
##        
##                bCapital = False
##                bPersia = False
##                iModifier = 0
##                for i in range(iNumPlayers):
##                        if (city.getX() == tCapitals[i][0] and city.getY() == tCapitals[i][1]):
##                                if (city.getOwner() == i): #otherwise it's no longer a capital
##                                        bCapital = True                                
##                if (iNewOwner == iPersia):
##                        bPersia = True
##                        if (not bCapital):
##                                iModifier = 1
##                if (iNewOwner == self.getRebelCiv() and gc.getGame().getGameTurn() == self.getLatestRebellionTurn(self.getRebelCiv())):
##                        return #don't mess up with resurrection()
##                #print ("iNewOwner", iNewOwner, con.tBirth[iNewOwner])
##                if (iNewOwner == iBarbarian):
##                        return
##                if (iNewOwner != iBarbarian):
##                        if (gc.getGame().getGameTurn() <= con.tBirth[iNewOwner] + 2):
##                                return #don't mess up with birth (case of delay still a problem...)
##                if (bCapital or bPersia):
##                        for x in range(city.getX() -3 +iModifier, city.getX() +4 -iModifier):
##                                for y in range(city.getY() -3 +iModifier, city.getY() +4 -iModifier):
##                                        pCurrent = gc.getMap().plot( x, y )
##                                        if ( pCurrent.isCity()):
##                                                cityNear = pCurrent.getPlotCity()
##                                                iOwnerNear = cityNear.getOwner()
##                                                #print ("iOwnerNear", iOwnerNear, "citynear", cityNear.getName())
##                                                if (iOwnerNear != iNewOwner and iOwnerNear == iOldOwner):
##                                                        if (cityNear != city):
##                                                                if (cityNear.getPopulation() <= city.getPopulation() and not cityNear.isCapital()):
##                                                                        if (bPersia == True and iModifier == 1): #Persian UP - any city, 2x2 area
##                                                                                if (cityNear.getPopulation() <= 8):
##                                                                                        if (self.getLatestFlipTurn() != gc.getGame().getGameTurn()):                                                                               
##                                                                                                utils.flipUnitsInCityBefore((x,y), iNewOwner, iOwnerNear)
##                                                                                                self.setTempFlippingCity((x,y))
##                                                                                                utils.flipCity((x,y), 0, 0, iNewOwner, [iOwnerNear])
##                                                                                                utils.flipUnitsInCityAfter(self.getTempFlippingCity(), iNewOwner)
##                                                                                                self.setLatestFlipTurn(gc.getGame().getGameTurn())
##                                                                                                utils.cultureManager(self.getTempFlippingCity(), 50, iOwnerNear, iNewOwner, False, False, False)
##                                                                        else:   
##                                                                                utils.flipUnitsInCityBefore((x,y), iNewOwner, iOwnerNear)
##                                                                                self.setTempFlippingCity((x,y))
##                                                                                utils.flipCity((x,y), 0, 0, iNewOwner, [iOwnerNear])
##                                                                                utils.flipUnitsInCityAfter(self.getTempFlippingCity(), iNewOwner)
##                                                                                utils.cultureManager(self.getTempFlippingCity(), 50, iOwnerNear, iNewOwner, False, False, False)
##                                                                                print ("COLLAPSE: CAPITALS", gc.getPlayer(iOwnerNear).getCivilizationShortDescription(0))
                                                                                     

                            

        def collapseByBarbs(self, iGameTurn):
                for iCiv in range(iNumPlayers):
                        if (gc.getPlayer(iCiv).isHuman() == 0 and gc.getPlayer(iCiv).isAlive()):
                                if (iGameTurn >= con.tBirth[iCiv] + 25):
                                        iNumCities = gc.getPlayer(iCiv).getNumCities()
                                        iLostCities = 0
                                        for x in range(0, 124):
                                                for y in range(0, 168):
                                                        if (gc.getMap().plot( x,y ).isCity()):
                                                                city = gc.getMap().plot( x,y ).getPlotCity()
                                                                if (city.getOwner() == iBarbarian):
                                                                        if (city.getOriginalOwner() == iCiv):
                                                                                iLostCities = iLostCities + 1                                                
                                        if (iLostCities*2 > iNumCities and iNumCities > 0): #if more than one third is captured, the civ collapses
                                                print ("COLLAPSE BY BARBS", gc.getPlayer(iCiv).getCivilizationAdjective(0))
                                                utils.killAndFragmentCiv(iCiv, iIndependent, iIndependent2, -1, False)

        def collapseGeneric(self, iGameTurn):
                #lNumCitiesNew = con.l0Array
                lNumCitiesNew = con.l0ArrayTotal #for late start
                for iCiv in range(iNumTotalPlayers):
                        if (iCiv < iNumActivePlayers or (iCiv == iCeltia and not gc.getPlayer(0).isPlayable())): #late start condition
                                pCiv = gc.getPlayer(iCiv)
                                teamCiv = gc.getTeam(pCiv.getTeam())
                                if (pCiv.isAlive()):
                                        if (iGameTurn >= con.tBirth[iCiv] + 25):
                                                lNumCitiesNew[iCiv] = pCiv.getNumCities()
                                                if (lNumCitiesNew[iCiv]*2 <= self.getNumCities(iCiv)): #if number of cities is less than half than some turns ago, the civ collapses
                                                        print ("COLLAPSE GENERIC", pCiv.getCivilizationAdjective(0), lNumCitiesNew[iCiv]*2, "<=", self.getNumCities(iCiv))
                                                        if (gc.getPlayer(iCiv).isHuman() == 0):
                                                                bVassal = False
                                                                for iMaster in range(con.iNumPlayers):
                                                                        if (teamCiv.isVassal(iMaster)):
                                                                                bVassal = True
                                                                                break
                                                                if (not bVassal):
                                                                        utils.killAndFragmentCiv(iCiv, iIndependent, iIndependent2, -1, False)
                                                else:
                                                        self.setNumCities(iCiv, lNumCitiesNew[iCiv])

        def collapseMotherland(self, iGameTurn):
                #collapses if completely out of broader areas
                for iCiv in range(iNumPlayers):
                        pCiv = gc.getPlayer(iCiv)
                        teamCiv = gc.getTeam(pCiv.getTeam())
                        if (pCiv.isHuman() == 0 and pCiv.isAlive()):
                                if (iGameTurn >= con.tBirth[iCiv] + 25):
                                        bSafe = False
                                        for x in range(tCoreAreasTL[iCiv][0], tCoreAreasBR[iCiv][0]+1):
                                                for y in range(tCoreAreasTL[iCiv][1], tCoreAreasBR[iCiv][1]+1):
                                                        pCurrent = gc.getMap().plot( x, y )
                                                        if ( pCurrent.isCity()):
                                                                #print (pCurrent.getPlotCity().getOwner(), pCurrent.getPlotCity().getName(), pCurrent.getPlotCity().getX(), pCurrent.getPlotCity().getY())
                                                                if (pCurrent.getPlotCity().getOwner() == iCiv):
                                                                        #print ("iCiv", iCiv, "bSafe", bSafe)
                                                                        bSafe = True
                                                                        break
                                                                        break
                                        if (bSafe == False):
                                                iCitiesOwned = 0
                                                iCitiesLost = 0
                                                for x in range(tNormalAreasTL[iCiv][0], tNormalAreasBR[iCiv][0]+1):
                                                        for y in range(tNormalAreasTL[iCiv][1], tNormalAreasBR[iCiv][1]+1):
                                                                pCurrent = gc.getMap().plot( x, y )
                                                                if ( pCurrent.isCity()):
                                                                        #print (pCurrent.getPlotCity().getOwner(), pCurrent.getPlotCity().getName(), pCurrent.getPlotCity().getX(), pCurrent.getPlotCity().getY())
                                                                        if (pCurrent.getPlotCity().getOwner() == iCiv):
                                                                                iCitiesOwned += 1
                                                                        else:
                                                                                iCitiesLost += 1
                                                if (iCitiesOwned > iCitiesLost):
                                                        bSafe = True
                                        #print ("iCiv", iCiv, "bSafe", bSafe)
                                        if (bSafe == False):
                                                bVassal = False
                                                for iMaster in range(con.iNumPlayers):
                                                        if (teamCiv.isVassal(iMaster)):
                                                                bVassal = True
                                                                break
                                                if (not bVassal):
                                                        print ("COLLAPSE: MOTHERLAND", gc.getPlayer(iCiv).getCivilizationAdjective(0))
                                                        utils.killAndFragmentCiv(iCiv, iIndependent, iIndependent2, -1, False)
                                                return
                        


        def collapseHuman(self, iOldOwner, city, iNewOwner):
                bEnabled = False
                bCapital = False
                bGeneric = False
                
                if (gc.getTeam(gc.getPlayer(iNewOwner).getTeam()).isHasTech(con.iCodeOfLaws)):
                        bEnabled = True
                                    
                iHuman = utils.getHumanID()
                if (city.getX() == tCapitals[iHuman][0] and city.getY() == tCapitals[iHuman][1]):
                        bCapital = True

                print ("bEnabled:", bEnabled, "bCapital:", bCapital, "bGeneric:", bGeneric)

                #debug
                #iNumCitiesNew = gc.getPlayer(iHuman).getNumCities()
                #if (iNumCitiesNew*2 <= self.getNumCities(iHuman)):
                #        print ("HumanCollapseGeneric", iNumCitiesNew*2, "<=", self.getNumCities(iHuman))
                #        bGeneric = True

                #debug
                #bEnabled = True
                #bCapital = True
                
                if ((bCapital or bGeneric) and bEnabled):
                        self.exile(iNewOwner)


        def exile(self, iWinner):
                iHuman = utils.getHumanID()
                pWinner = gc.getPlayer(iWinner)
                teamWinner = gc.getTeam(pWinner.getTeam())
                iDestination = -1
                iRndnum = gc.getGame().getSorenRandNum(iNumPlayers, 'start index')
                for i in range( iRndnum, iNumPlayers + iRndnum ):
                        iCiv = i % iNumPlayers
                        if (gc.getPlayer(iCiv).isAlive() and iCiv != iWinner):
                                if (pWinner.canContact(iCiv)):
                                        if (not teamWinner.isAtWar(iCiv)):
                                                if (gc.getGame().getPlayerRank(iCiv) > gc.getGame().getPlayerRank(iHuman) + 1):
                                                        iDestination = iCiv
                                                        break                                          

                print (iDestination)
                popup = Popup.PyPopup()
                popup.setHeaderString(CyTranslator().getText("TXT_KEY_EXILE_TITLE", ()))          
                popup.setBodyString( CyTranslator().getText("TXT_KEY_EXILE_TEXT", (gc.getPlayer(iWinner).getCivilizationAdjectiveKey(), gc.getPlayer(iDestination).getCivilizationShortDescription(0))))
                popup.launch()
                self.setExileData(0, tCapitals[iHuman][0])
                self.setExileData(1, tCapitals[iHuman][1])
                self.setExileData(2, gc.getGame().getGameTurn())
                self.setExileData(3, iHuman)
                self.setExileData(4, iWinner)

                for iMaster in range(con.iNumPlayers):
                        if (gc.getTeam(gc.getPlayer(iDestination).getTeam()).isVassal(iMaster)):
                                gc.getTeam(gc.getPlayer(iDestination).getTeam()).setVassal(iMaster, False, False)
                
                iTempHumanLeader = gc.getPlayer(iHuman).getLeader()
                iTempDestinationLeader = gc.getPlayer(iDestination).getLeader()
                gc.getPlayer(iDestination).setLeader(iTempHumanLeader)
                gc.getGame().setActivePlayer(iDestination, False)
                gc.getPlayer(iHuman).setLeader(iTempDestinationLeader)
                teamWinner.makePeace(iHuman) #now managed by AI
                iTempLeader = gc.getPlayer(iHuman)

                

        def escape(self, city):
                if (gc.getGame().getGameTurn() <= self.getExileData(2) + iEscapePeriod):
                        iOldHuman = self.getExileData(3)
                        if (gc.getPlayer(iOldHuman).isAlive()):
                                iHuman = utils.getHumanID()
                                utils.flipCity((city.getX(),city.getY()), 0, 0, iOldHuman, [iHuman])
                                popup = Popup.PyPopup()
                                popup.setHeaderString(CyTranslator().getText("TXT_KEY_ESCAPE_TITLE", ()))          
                                popup.setBodyString( CyTranslator().getText("TXT_KEY_ESCAPE_TEXT", (gc.getPlayer(iOldHuman).getCivilizationAdjectiveKey(),)))
                                popup.launch()

                                for iMaster in range(con.iNumPlayers):
                                        if (gc.getTeam(gc.getPlayer(iOldHuman).getTeam()).isVassal(iMaster)):
                                                gc.getTeam(gc.getPlayer(iOldHuman).getTeam()).setVassal(iMaster, False, False)
                                
                                iTempHumanLeader = gc.getPlayer(iHuman).getLeader()
                                iTempOldHumanLeader = gc.getPlayer(iOldHuman).getLeader()
                                gc.getPlayer(iOldHuman).setLeader(iTempHumanLeader)
                                gc.getGame().setActivePlayer(iOldHuman, False)
                                gc.getPlayer(iHuman).setLeader(iTempOldHumanLeader)
                                city.setHasRealBuilding((0), True) #0 == palace
                                teamWinner = gc.getTeam(gc.getPlayer(self.getExileData(4)).getTeam())
                                teamWinner.declareWar(iOldHuman, True, -1)
                                teamWinner.makePeace(iHuman) #now managed by AI
                                self.setExileData(0, -1)
                                self.setExileData(1, -1)
                                self.setExileData(2, -1)
                                self.setExileData(3, -1)
                                self.setExileData(4, -1)

                

        def secession(self, iGameTurn):
            
                iRndnum = gc.getGame().getSorenRandNum(iNumPlayers, 'starting count')
                for j in range(iRndnum, iRndnum + iNumPlayers):
                        iPlayer = j % iNumPlayers   
                        if (gc.getPlayer(iPlayer).isAlive() and iGameTurn >= con.tBirth[iPlayer] + 30):
                                if (utils.getStability(iPlayer) >= -40 and utils.getStability(iPlayer) < -20): #secession

                                        cityList = []
                                        apCityList = PyPlayer(iPlayer).getCityList()
                                        for pCity in apCityList:
                                                city = pCity.GetCy()
                                                pCurrent = gc.getMap().plot(city.getX(), city.getY())

                                                if ((not city.isWeLoveTheKingDay()) and (not city.isCapital()) and (not (city.getX() == tCapitals[iPlayer][0] and city.getY() == tCapitals[iPlayer][1]))):
                                                        if (gc.getPlayer(iPlayer).getNumCities() > 0): #this check is needed, otherwise game crashes
                                                                capital = gc.getPlayer(iPlayer).getCapitalCity()
                                                                iDistance = utils.calculateDistance(city.getX(), city.getY(), capital.getX(), capital.getY())
                                                                if (iDistance > 3):                                                                                               
                                                            
                                                                        if (city.angryPopulation(0) > 0 or \
                                                                            city.healthRate(False, 0) < 0 or \
                                                                            city.getReligionBadHappiness() > 0 or \
                                                                            city.getLargestCityHappiness() < 0 or \
                                                                            city.getHurryAngerModifier() > 0 or \
                                                                            city.getNoMilitaryPercentAnger() > 0 or \
                                                                            city.getWarWearinessPercentAnger() > 0):
                                                                                cityList.append(city)
                                                                                continue
                                                                        
                                                                        for iLoop in range(iNumTotalPlayers+1):
                                                                                if (iLoop != iPlayer):
                                                                                        if (pCurrent.getCulture(iLoop) > 0):
                                                                                                cityList.append(city)
                                                                                                break

                                        if (len(cityList)):
                                                iNewCiv = iIndependent
                                                iRndNum = gc.getGame().getSorenRandNum(2, 'random independent')
                                                if (iRndNum % 2 == 0):
                                                        iNewCiv = iIndependent2                        
                                                splittingCity = cityList[gc.getGame().getSorenRandNum(len(cityList), 'random city')]
                                                utils.cultureManager((splittingCity.getX(),splittingCity.getY()), 50, iNewCiv, iPlayer, False, True, True)
                                                utils.flipUnitsInCityBefore((splittingCity.getX(),splittingCity.getY()), iNewCiv, iPlayer)                            
                                                self.setTempFlippingCity((splittingCity.getX(),splittingCity.getY()))
                                                utils.flipCity((splittingCity.getX(),splittingCity.getY()), 0, 0, iNewCiv, [iPlayer])   #by trade because by conquest may raze the city
                                                utils.flipUnitsInCityAfter(self.getTempFlippingCity(), iNewCiv)
                                                if (iPlayer == utils.getHumanID()):
                                                        CyInterface().addMessage(iPlayer, True, con.iDuration, splittingCity.getName() + " " + \
                                                                                           CyTranslator().getText("TXT_KEY_STABILITY_SECESSION", ()), "", 0, "", ColorTypes(con.iOrange), -1, -1, True, True)
                                                #print ("SECESSION", gc.getPlayer(iPlayer).getCivilizationAdjective(0), splittingCity.getName()) #causes c++ exception??
                                                utils.setStability(iPlayer, utils.getStability(iPlayer) + 2) #to counterbalance the stability hit on city acquired event, leading to a chain reaction
                                        return #just 1 secession per turn


                              
        def resurrection(self, iGameTurn):
                iMinNumCities = 2
                bEnabled = False
                for iCiv in range(iNumActivePlayers):
                        pCiv = gc.getPlayer(iCiv)
                        teamCiv = gc.getTeam(pCiv.getTeam())
                        if (pCiv.isAlive()):
                                if (teamCiv.isHasTech(con.iNationalism)):
                                        bEnabled = True
                                        break
                                #debug
                                #bEnabled = True
                                #break
                #print ("bEnabled", bEnabled)
                if (bEnabled):
                        iRndnum = gc.getGame().getSorenRandNum(iNumPlayers, 'starting count')
                        cityList = []
                        for j in range(iRndnum, iRndnum + iNumPlayers):
                                iDeadCiv = j % iNumPlayers
                                #iDeadCiv = iIndia #DEBUG
                                cityList = []
                                if (not gc.getPlayer(iDeadCiv).isAlive() and iGameTurn > con.tBirth[iDeadCiv] + 50 and iGameTurn > utils.getLastTurnAlive(iDeadCiv) + 20):
                                #if (not gc.getPlayer(iDeadCiv).isAlive() and iGameTurn > con.tBirth[iDeadCiv] + 50): #DEBUG
                                        pDeadCiv = gc.getPlayer(iDeadCiv)
                                        teamDeadCiv = gc.getTeam(pDeadCiv.getTeam())
                                        tTopLeft = tNormalAreasTL[iDeadCiv]
                                        tBottomRight = tNormalAreasBR[iDeadCiv]
                                        #if (self.getLatestRebellionTurn(iDeadCiv) > 0):
                                        #        tTopLeft = tNormalAreasTL[iDeadCiv]
                                        #        tBottomRight = tNormalAreasBR[iDeadCiv]
                                        #else:
                                        #        tTopLeft = tCoreAreasTL[iDeadCiv]
                                        #        tBottomRight = tCoreAreasBR[iDeadCiv]
                                        for x in range(tTopLeft[0], tBottomRight[0]+1):
                                                for y in range(tTopLeft[1], tBottomRight[1]+1):
                                                        if ((x,y) not in con.tNormalAreasSubtract[iDeadCiv]):
                                                                pCurrent = gc.getMap().plot( x, y )
                                                                if ( pCurrent.isCity()):
                                                                        city = pCurrent.getPlotCity()
                                                                        iOwner = city.getOwner()
                                                                        if (iOwner >= iNumActivePlayers): #if (iOwner == iBarbarian or iOwner == iIndependent or iOwner == iIndependent2): #remove in vanilla
                                                                                cityList.append(pCurrent.getPlotCity())
                                                                                #print (iDeadCiv, pCurrent.getPlotCity().getName(), pCurrent.getPlotCity().getOwner(), "1", cityList)
                                                                        else:
                                                                                iMinNumCitiesOwner = 3
                                                                                iOwnerStability = utils.getStability(iOwner)
                                                                                if (not gc.getPlayer(iOwner).isHuman()):
                                                                                        iMinNumCitiesOwner = 2
                                                                                        iOwnerStability -= 20
                                                                                if (gc.getPlayer(iOwner).getNumCities() >= iMinNumCitiesOwner):
                                                                                        if (iOwnerStability < -20):
                                                                                                if (not city.isWeLoveTheKingDay() and not city.isCapital()):
                                                                                                            cityList.append(pCurrent.getPlotCity())
                                                                                                            #print (iDeadCiv, pCurrent.getPlotCity().getName(), pCurrent.getPlotCity().getOwner(), "2", cityList)
                                                                                        elif (iOwnerStability < 0):
                                                                                                if (not city.isWeLoveTheKingDay() and not city.isCapital() and (not (city.getX() == tCapitals[iOwner][0] and city.getY() == tCapitals[iOwner][1]))):
                                                                                                        if (gc.getPlayer(iOwner).getNumCities() > 0): #this check is needed, otherwise game crashes
                                                                                                                capital = gc.getPlayer(iOwner).getCapitalCity()
                                                                                                                iDistance = utils.calculateDistance(x, y, capital.getX(), capital.getY())
                                                                                                                if ((iDistance >= 6 and gc.getPlayer(iOwner).getNumCities() >= 4) or \
                                                                                                                    city.angryPopulation(0) > 0 or \
                                                                                                                    city.healthRate(False, 0) < 0 or \
                                                                                                                    city.getReligionBadHappiness() > 0 or \
                                                                                                                    city.getLargestCityHappiness() < 0 or \
                                                                                                                    city.getHurryAngerModifier() > 0 or \
                                                                                                                    city.getNoMilitaryPercentAnger() > 0 or \
                                                                                                                    city.getWarWearinessPercentAnger() > 0):
                                                                                                                            cityList.append(pCurrent.getPlotCity())
                                                                                                                            #print (iDeadCiv, pCurrent.getPlotCity().getName(), pCurrent.getPlotCity().getOwner(), "3", cityList)
                                                                                        if (iOwnerStability < 20):
                                                                                                 if (city.getX() == tCapitals[iDeadCiv][0] and city.getY() == tCapitals[iDeadCiv][1]):
                                                                                                         if (pCurrent.getPlotCity() not in cityList):
                                                                                                                 cityList.append(pCurrent.getPlotCity())
                                        if (len(cityList) >= iMinNumCities or (len(cityList) >= 1 and (iDeadCiv == iNetherlands))):
                                                if (gc.getGame().getSorenRandNum(100, 'roll') < con.tResurrectionProb[iDeadCiv]):
                                                        break
                        #print ("iDeadCiv", iDeadCiv)
                        if (len(cityList) >= iMinNumCities or (len(cityList) >= 1 and (iDeadCiv == iNetherlands))): #no portugal: they have the azores
                                self.setRebelCiv(iDeadCiv) #for popup and CollapseCapitals()
                                if (len(tLeaders[iDeadCiv]) > 1):
                                        iLen = len(tLeaders[iDeadCiv])
                                        iRnd = gc.getGame().getSorenRandNum(iLen, 'odds')
                                        for k in range (iLen):
                                                iLeader = (iRnd + k) % iLen
                                                if (pDeadCiv.getLeader() != tLeaders[iDeadCiv][iLeader]):
                                                        print ("leader switch after resurrection", pDeadCiv.getLeader(), tLeaders[iDeadCiv][iLeader])
                                                        pDeadCiv.setLeader(tLeaders[iDeadCiv][iLeader])
                                                        break                                                        
                                                
                                for l in range(iNumPlayers):
                                        teamDeadCiv.makePeace(l)
                                self.setNumCities(iDeadCiv, 0) #reset collapse condition

                                #reset vassallage
                                for iOtherCiv in range(iNumPlayers):
                                        if (teamDeadCiv.isVassal(iOtherCiv) or gc.getTeam(gc.getPlayer(iOtherCiv).getTeam()).isVassal(iDeadCiv)):
                                                teamDeadCiv.freeVassal(iOtherCiv)
                                                gc.getTeam(gc.getPlayer(iOtherCiv).getTeam()).freeVassal(iDeadCiv)
                                                               
                                iNewUnits = 2
                                if (self.getLatestRebellionTurn(iDeadCiv) > 0):
                                        iNewUnits = 4
                                self.setLatestRebellionTurn(iDeadCiv, iGameTurn)
                                bHuman = False
                                iHuman = utils.getHumanID()
                                print ("RESURRECTION", gc.getPlayer(iDeadCiv).getCivilizationAdjective(0))
                                
                                for k0 in range(len(cityList)):
                                        iOwner = cityList[k0].getOwner()
                                        if (iOwner == iHuman):
                                                bHuman = True

                                ownersList = []        
                                bAlreadyVassal = False
                                for k in range(len(cityList)):
                                        if (cityList[k] != None): #once happened that it was = none
                                                #print ("INDEPENDENCE: ", cityList[k].getName()) #may cause a c++ exception                                       
                                                iOwner = cityList[k].getOwner()
                                                teamOwner = gc.getTeam(gc.getPlayer(iOwner).getTeam())
                                                bOwnerVassal = teamOwner.isAVassal()
                                                bOwnerHumanVassal = teamOwner.isVassal(iHuman)

                                                if (iOwner == iBarbarian or iOwner == iIndependent or iOwner == iIndependent2 or iOwner == iNative):
                                                        utils.cultureManager((cityList[k].getX(),cityList[k].getY()), 100, iDeadCiv, iOwner, False, True, True)
                                                        utils.flipUnitsInCityBefore((cityList[k].getX(),cityList[k].getY()), iDeadCiv, iOwner)
                                                        self.setTempFlippingCity((cityList[k].getX(),cityList[k].getY()))
                                                        utils.flipCity((cityList[k].getX(),cityList[k].getY()), 0, 0, iDeadCiv, [iOwner])
                                                        tCoords = self.getTempFlippingCity()
                                                        utils.flipUnitsInCityAfter(tCoords, iOwner)
                                                        utils.flipUnitsInArea((tCoords[0]-2, tCoords[1]-2), (tCoords[0]+2, tCoords[1]+2), iDeadCiv, iOwner, True, False)
                                                else:
                                                        utils.cultureManager((cityList[k].getX(),cityList[k].getY()), 50, iDeadCiv, iOwner, False, True, True)
                                                        utils.pushOutGarrisons((cityList[k].getX(),cityList[k].getY()), iOwner)
                                                        utils.relocateSeaGarrisons((cityList[k].getX(),cityList[k].getY()), iOwner)                                                                        
                                                        self.setTempFlippingCity((cityList[k].getX(),cityList[k].getY()))
                                                        utils.flipCity((cityList[k].getX(),cityList[k].getY()), 0, 0, iDeadCiv, [iOwner])   #by trade because by conquest may raze the city
                                                        utils.createGarrisons(self.getTempFlippingCity(), iDeadCiv, iNewUnits)
                                                        
                                                #cityList[k].setHasRealBuilding(con.iPlague, False)

                                                bAtWar = False #AI won't vassalise if another owner has declared war; on the other hand, it won't declare war if another one has vassalised
                                                if (iOwner != iHuman and iOwner not in ownersList and iOwner != iDeadCiv): #declare war or peace only once - the 3rd condition is obvious but "vassal of themselves" was happening
                                                        rndNum = gc.getGame().getSorenRandNum(100, 'odds')
                                                        if (rndNum >= tAIStopBirthThreshold[iOwner] and bOwnerHumanVassal == False and bAlreadyVassal == False): #if bOwnerHumanVassal is true, it will skip to the 3rd condition, as bOwnerVassal is true as well
                                                                teamOwner.declareWar(iDeadCiv, False, -1)
                                                                bAtWar = True
                                                        elif (rndNum <= (100-tAIStopBirthThreshold[iOwner])/2):
                                                                teamOwner.makePeace(iDeadCiv)
                                                                if (bAlreadyVassal == False and bHuman == False and bOwnerVassal == False and bAtWar == False): #bHuman == False cos otherwise human player can be deceived to declare war without knowing the new master
                                                                        if (iOwner < iNumActivePlayers): 
                                                                                gc.getTeam(gc.getPlayer(iDeadCiv).getTeam()).setVassal(iOwner, True, False)  #remove in vanilla
                                                                                bAlreadyVassal = True
                                                        else:
                                                                teamOwner.makePeace(iDeadCiv)
                                                        ownersList.append(iOwner)
                                                        for t in range(con.iNumTechs):
                                                                if (teamOwner.isHasTech(t)): 
                                                                        teamDeadCiv.setHasTech(t, True, iDeadCiv, False, False)

                                for t in range(con.iNumTechs):
                                        if (teamBarbarian.isHasTech(t) or teamIndependent.isHasTech(t) or teamIndependent2.isHasTech(t)): #remove indep in vanilla
                                                teamDeadCiv.setHasTech(t, True, iDeadCiv, False, False)

                                self.moveBackCapital(iDeadCiv)

                                #add former colonies that are still free
                                colonyList = []
                                for iIndCiv in range(iNumTotalPlayers+1): #barbarians too
                                        if (iIndCiv >= iNumActivePlayers):
                                                if (gc.getPlayer(iIndCiv).isAlive()):
                                                        apCityList = PyPlayer(iIndCiv).getCityList()
                                                        for pCity in apCityList:
                                                                indepCity = pCity.GetCy()                                                                
                                                                if (indepCity.getOriginalOwner() == iDeadCiv):
                                                                        print ("colony:", indepCity.getName(), indepCity.getOriginalOwner())
                                                                        indX = indepCity.getX()
                                                                        indY = indepCity.getY()
                                                                        if (gc.getPlayer(iDeadCiv).getSettlersMaps( 67-indY, indX ) >= 90):
                                                                                if (indepCity not in cityList and indepCity not in colonyList):
                                                                                        colonyList.append(indepCity)
                                if (len(colonyList) > 0):
                                        for k in range(len(colonyList)):
                                                print ("INDEPENDENCE: ", colonyList[k].getName())   
                                                iOwner = colonyList[k].getOwner()
                                                utils.cultureManager((colonyList[k].getX(),colonyList[k].getY()), 100, iDeadCiv, iOwner, False, True, True)
                                                utils.flipUnitsInCityBefore((colonyList[k].getX(),colonyList[k].getY()), iDeadCiv, iOwner)
                                                self.setTempFlippingCity((colonyList[k].getX(),colonyList[k].getY()))
                                                utils.flipCity((colonyList[k].getX(),colonyList[k].getY()), 0, 0, iDeadCiv, [iOwner])
                                                tCoords = self.getTempFlippingCity()
                                                utils.flipUnitsInCityAfter(tCoords, iOwner)
                                                utils.flipUnitsInArea((tCoords[0]-2, tCoords[1]-2), (tCoords[0]+2, tCoords[1]+2), iDeadCiv, iOwner, True, False)
                                                
                                CyInterface().addMessage(iHuman, True, con.iDuration, \
                                                        (CyTranslator().getText("TXT_KEY_INDEPENDENCE_TEXT", (pDeadCiv.getCivilizationAdjectiveKey(),))), "", 0, "", ColorTypes(con.iGreen), -1, -1, True, True)
                                if (bHuman == True):                                        
                                        self.rebellionPopup(iDeadCiv)
                                utils.setBaseStabilityLastTurn(iDeadCiv, 0)
                                utils.setStability(iDeadCiv, 10) ##the new civs start as slightly stable
                                utils.setPlagueCountdown(iDeadCiv, -10)
                                utils.clearPlague(iDeadCiv)                                
                                self.convertBackCulture(iDeadCiv)
                                return

        def moveBackCapital(self, iCiv):
                apCityList = PyPlayer(iCiv).getCityList()
                if (gc.getMap().plot(tCapitals[iCiv][0], tCapitals[iCiv][1]).isCity()):
                        oldCapital = gc.getMap().plot(tCapitals[iCiv][0], tCapitals[iCiv][1]).getPlotCity()
                        if (oldCapital.getOwner() == iCiv):
                                if (not oldCapital.hasBuilding(con.iPalace)):                                        
                                        for pCity in apCityList:
                                                pCity.GetCy().setHasRealBuilding((con.iPalace), False)
                                        oldCapital.setHasRealBuilding((con.iPalace), True)
                else:
                        iMaxValue = 0
                        bestCity = None
                        for pCity in apCityList:
                                loopCity = pCity.GetCy()
                                #loopCity.AI_cityValue() doesn't work as area AI types aren't updated yet
                                loopValue = max(0,500-loopCity.getGameTurnFounded()) + loopCity.getPopulation()*10
                                #print ("loopValue", loopCity.getName(), loopCity.AI_cityValue(), loopValue) #causes C++ exception
                                if (loopValue > iMaxValue):
                                        iMaxValue = loopValue
                                        bestCity = loopCity
                        if (bestCity != None):
                                for pCity in apCityList:
                                        loopCity = pCity.GetCy()
                                        if (loopCity != bestCity):
                                                loopCity.setHasRealBuilding((con.iPalace), False)
                                bestCity.setHasRealBuilding((con.iPalace), True)
                                                
                                                

        def convertBackCulture(self, iCiv):
                tTopLeft = tNormalAreasTL[iCiv]
                tBottomRight = tNormalAreasBR[iCiv]         
                cityList = []    
                #collect all the cities in the region
                for x in range(tTopLeft[0], tBottomRight[0]+1):
                        for y in range(tTopLeft[1], tBottomRight[1]+1):
                                pCurrent = gc.getMap().plot( x, y )
                                if ( pCurrent.isCity()):
                                        for ix in range(pCurrent.getX()-1, pCurrent.getX()+2):        # from x-1 to x+1
                                                for iy in range(pCurrent.getY()-1, pCurrent.getY()+2):	# from y-1 to y+1
                                                        pCityArea = gc.getMap().plot( ix, iy )
                                                        iCivCulture = pCityArea.getCulture(iCiv)
                                                        iLoopCivCulture = 0
                                                        for iLoopCiv in range(con.iNumTotalPlayers+1): #barbarians too
                                                                if (iLoopCiv >= iNumPlayers):
                                                                        iLoopCivCulture += pCityArea.getCulture(iLoopCiv)      
                                                                        pCityArea.setCulture(iLoopCiv, 0, True)
                                                        pCityArea.setCulture(iCiv, iCivCulture + iLoopCivCulture, True)

                                        city = pCurrent.getPlotCity()
                                        iCivCulture = city.getCulture(iCiv)
                                        iLoopCivCulture = 0
                                        for iLoopCiv in range(con.iNumTotalPlayers+1): #barbarians too
                                                if (iLoopCiv >= iNumPlayers):
                                                        iLoopCivCulture += city.getCulture(iLoopCiv)                                
                                                        city.setCulture(iLoopCiv, 0, True)
                                        city.setCulture(iCiv, iCivCulture + iLoopCivCulture, True) 

                            
                                    
        def initBirth(self, iCurrentTurn, iBirthYear, iCiv):
                iHuman = utils.getHumanID()
                if (iCurrentTurn == iBirthYear-1 + self.getSpawnDelay(iCiv) + self.getFlipsDelay(iCiv)):
                        tCapital = tCapitals[iCiv]
                        tTopLeft = tCoreAreasTL[iCiv]
                        tBottomRight = tCoreAreasBR[iCiv]
                        tBroaderTopLeft = tBroaderAreasTL[iCiv]
                        tBroaderBottomRight = tBroaderAreasBR[iCiv]                    
                        if (self.getFlipsDelay(iCiv) == 0): #city hasn't already been founded)
                                bDeleteEverything = False
                                if (gc.getMap().plot(tCapital[0], tCapital[1]).isOwned()):
                                        if (iCiv == iHuman or not gc.getPlayer(iHuman).isAlive()):
                                                bDeleteEverything = True
                                                print ("bDeleteEverything 1")
                                        else:
                                                bDeleteEverything = True
                                                for x in range(tCapital[0] - 1, tCapital[0] + 2):        # from x-1 to x+1
                                                        for y in range(tCapital[1] - 1, tCapital[1] + 2):	# from y-1 to y+1
                                                                pCurrent=gc.getMap().plot(x, y)
                                                                if (pCurrent.isCity() and pCurrent.getPlotCity().getOwner() == iHuman):
                                                                        bDeleteEverything = False
                                                                        print ("bDeleteEverything 2")
                                                                        break
                                                                        break
                                print ("bDeleteEverything", bDeleteEverything)
                                if (not gc.getMap().plot(tCapital[0], tCapital[1]).isOwned()):
                                        if (iCiv == iNetherlands or iCiv == iPortugal): #dangerous starts
                                                self.setDeleteMode(0, iCiv)
                                        self.birthInFreeRegion(iCiv, tCapital, tTopLeft, tBottomRight)
                                elif (bDeleteEverything):
                                        for x in range(tCapital[0] - 1, tCapital[0] + 2):        # from x-1 to x+1
                                                for y in range(tCapital[1] - 1, tCapital[1] + 2):	# from y-1 to y+1
                                                        self.setDeleteMode(0, iCiv)
                                                        #print ("deleting", x, y)
                                                        pCurrent=gc.getMap().plot(x, y)
                                                        #self.moveOutUnits(x, y, tCapital[0], tCapital[1])
                                                        for iLoopCiv in range(iNumTotalPlayers+1): #Barbarians as well
                                                                if (iCiv != iLoopCiv):
                                                                        utils.flipUnitsInArea(tTopLeft, tBottomRight, iCiv, iLoopCiv, True, False)
                                                        if (pCurrent.isCity()):
                                                                pCurrent.eraseAIDevelopment() #new function, similar to erase but won't delete rivers, resources and features()
                                                        for iLoopCiv in range(iNumTotalPlayers+1): #Barbarians as well
                                                                if (iCiv != iLoopCiv):
                                                                        pCurrent.setCulture(iLoopCiv, 0, True)
                                                        pCurrent.setOwner(-1)
                                        self.birthInFreeRegion(iCiv, tCapital, tTopLeft, tBottomRight)
                                else:                                
                                        self.birthInForeignBorders(iCiv, tTopLeft, tBottomRight, tBroaderTopLeft, tBroaderBottomRight)
                        else:
                                print ( "setBirthType again: flips" )
                                self.birthInFreeRegion(iCiv, tCapital, tTopLeft, tBottomRight)
                                       
                if (iCurrentTurn == iBirthYear + self.getSpawnDelay(iCiv)) and (gc.getPlayer(iCiv).isAlive()) and (self.getAlreadySwitched() == False) and (iHuman+tDifference[iHuman] < iCiv):
                        self.newCivPopup(iCiv)   


##        def moveOutUnits(self, x, y, tCapitalX, tCapitalY) #not used
##                pCurrent=gc.getMap().plot(x, y)
##                if (pCurrent.getNumUnits() > 0):
##                        unit = pCurrent.getUnit(0)
##                        tDestination = (-1, -1)
##                        plotList = []
##                        if (unit.getDomainType() == 2): #land unit
##                                dummy, plotList = utils.squareSearch( (tCapitalX-3, tCapitalY-3), (tCapitalX+4, tCapitalY+4), utils.goodPlots, [] )
##                                #dummy, plotList = utils.squareSearch( (tCapitalX-3, tCapitalY-3), (tCapitalX+4, tCapitalY+4), utils.goodOwnedPlots, [] )
##                        else: #sea unit
##                                dummy, plotList = utils.squareSearch( (tCapitalX-3, tCapitalY-3), (tCapitalX+4, tCapitalY+4), utils.goodOwnedPlots, [] )
##                        
##                        rndNum = gc.getGame().getSorenRandNum(len(plotList), 'searching another free plot')
##                        if (len(plotList)):
##                                result = plotList[rndNum]
##                                if (result):
##                                        tDestination = result
##                        print ("moving units around to", (tDestination[0], tDestination[1]))
##                        if (tDestination != (-1, -1)):
##                                for i in range(pCurrent.getNumUnits()):                                                                
##                                        unit = pCurrent.getUnit(0)
##                                        unit.setXY(tDestination[0], tDestination[1])

                                
                

        def deleteMode(self, iCurrentPlayer):
                iCiv = self.getDeleteMode(0)
                print ("deleteMode after", iCurrentPlayer)
                tCapital = con.tCapitals[iCiv]
                if (iCurrentPlayer == iCiv):
                        for x in range(tCapital[0] - 2, tCapital[0] + 3):        # from x-2 to x+2
                                for y in range(tCapital[1] - 2, tCapital[1] + 3):	# from y-2 to y+2
                                        pCurrent=gc.getMap().plot(x, y)
                                        pCurrent.setCulture(iCiv, 300, True)
                        for x in range(tCapital[0] - 1, tCapital[0] + 2):        # from x-1 to x+1
                                for y in range(tCapital[1] - 1, tCapital[1] + 2):	# from y-1 to y+1
                                        pCurrent=gc.getMap().plot(x, y)
                                        utils.convertPlotCulture(pCurrent, iCiv, 100, True)
                                        if (pCurrent.getCulture(iCiv) < 3000):
                                                pCurrent.setCulture(iCiv, 3000, True) #2000 in vanilla/warlords, cos here Portugal is choked by spanish culture
                                        pCurrent.setOwner(iCiv)
                        self.setDeleteMode(0, -1)
                        return
                    
                #print ("iCurrentPlayer", iCurrentPlayer, "iCiv", iCiv)
                if (iCurrentPlayer != iCiv-1):
                        return
                
                bNotOwned = True
                for x in range(tCapital[0] - 1, tCapital[0] + 2):        # from x-1 to x+1
                        for y in range(tCapital[1] - 1, tCapital[1] + 2):	# from y-1 to y+1
                                #print ("deleting again", x, y)
                                pCurrent=gc.getMap().plot(x, y)
                                if (pCurrent.isOwned()):
                                        bNotOwned = False
                                        for iLoopCiv in range(iNumTotalPlayers+1): #Barbarians as well
                                                if(iLoopCiv != iCiv):
                                                        pCurrent.setCulture(iLoopCiv, 0, True)
                                                #else:
                                                #        if (pCurrent.getCulture(iCiv) < 4000):
                                                #                pCurrent.setCulture(iCiv, 4000, True)
                                        #pCurrent.setOwner(-1)
                                        pCurrent.setOwner(iCiv)
                
                for x in range(tCapital[0] - 11, tCapital[0] + 12):        # must include the distance from Sogut to the Caspius
                        for y in range(tCapital[1] - 11, tCapital[1] + 12):
                                #print ("units", x, y, gc.getMap().plot(x, y).getNumUnits(), tCapital[0], tCapital[1])
                                if (x != tCapital[0] or y != tCapital[1]):
                                        pCurrent=gc.getMap().plot(x, y)
                                        if (pCurrent.getNumUnits() > 0 and not pCurrent.isWater()):
                                                unit = pCurrent.getUnit(0)
                                                #print ("units2", x, y, gc.getMap().plot(x, y).getNumUnits(), unit.getOwner(), iCiv)                                                
                                                if (unit.getOwner() == iCiv):
                                                        print ("moving starting units from", x, y, "to", (tCapital[0], tCapital[1]))
                                                        for i in range(pCurrent.getNumUnits()):                                                                
                                                                unit = pCurrent.getUnit(0)
                                                                unit.setXYOld(tCapital[0], tCapital[1])
                                                        #may intersect plot close to tCapital
##                                                        for farX in range(x - 6, x + 7):
##                                                                for farY in range(y - 6, y + 7):
##                                                                        pCurrentFar = gc.getMap().plot(farX, farY)
##                                                                        if (pCurrentFar.getNumUnits() == 0):
##                                                                                pCurrentFar.setRevealed(iCiv, False, True, -1);

                


            
                    
        def birthInFreeRegion(self, iCiv, tCapital, tTopLeft, tBottomRight):
                startingPlot = gc.getMap().plot( tCapital[0], tCapital[1] )
                if (self.getFlipsDelay(iCiv) == 0):
                        iFlipsDelay = self.getFlipsDelay(iCiv) + 2
##                        if (startingPlot.getNumUnits() > 0):
##                                unit = startingPlot.getUnit(0)
##                                if (unit.getOwner() != utils.getHumanID() or iCiv == utils.getHumanID()): #2nd check needed because in delete mode it finds the civ's (human's) units placed
##                                        for i in range(startingPlot.getNumUnits()):
##                                                unit = startingPlot.getUnit(0)	# 0 instead of i because killing units changes the indices
##                                                unit.kill(False, iCiv)
##                                        iFlipsDelay = self.getFlipsDelay(iCiv) + 2
##                                        #utils.debugTextPopup( 'birthInFreeRegion in starting location' ) 
##                                else:   #search another place
##                                        dummy, plotList = utils.squareSearch( tTopLeft, tBottomRight, utils.goodPlots, [] )
##                                        rndNum = gc.getGame().getSorenRandNum(len(plotList), 'searching another free plot')
##                                        if (len(plotList)):
##                                                result = plotList[rndNum]
##                                                if (result):
##                                                        self.createStartingUnits(iCiv, result)
##                                                        tCapital = result
##                                                        print ("birthInFreeRegion in another location")
##                                                        #utils.debugTextPopup( 'birthInFreeRegion in another location' )
##                                                        iFlipsDelay = self.getFlipsDelay(iCiv) + 1 #add delay before flipping other cities
##                                        else: 
##                                                if (self.getSpawnDelay(iCiv) < 10):  #wait
##                                                        iSpawnDelay = self.getSpawnDelay(iCiv) + 1
##                                                        self.setSpawnDelay(iCiv, iSpawnDelay)                                                        
##                        else:
##                                iFlipsDelay = self.getFlipsDelay(iCiv) + 2

                        if (iFlipsDelay > 0):
                                #startingPlot.setImprovementType(-1)
                            
                                #gc.getPlayer(iCiv).found(tCapital[0], tCapital[1])
                                #gc.getMap().plot(tCapital[0], tCapital[1]).setRevealed(iCiv, False, True, -1);
                                #gc.getMap().plot(tCapital[0], tCapital[1]).setRevealed(iCiv, True, True, -1);
                                
                                print ("starting units in", tCapital[0], tCapital[1])
                                self.createStartingUnits(iCiv, (tCapital[0], tCapital[1]))

                                #if (self.getDeleteMode(0) == iCiv):                                                                
                                #        self.createStartingWorkers(iCiv, tCapital) #XXX bugfix? no!
                                                                
##                                settlerPlot = gc.getMap().plot( tCapital[0], tCapital[1] )
##                                for i in range(settlerPlot.getNumUnits()):
##                                        unit = settlerPlot.getUnit(i)
##                                        if (unit.getUnitType() == iSettler):
##                                                break
##                                unit.found()                                
                                utils.flipUnitsInArea((tCapital[0]-2, tCapital[1]-2), (tCapital[0]+2, tCapital[1]+2), iCiv, iBarbarian, True, True) #This is for AI only. During Human player spawn, that area is already cleaned                        
                                utils.flipUnitsInArea((tCapital[0]-2, tCapital[1]-2), (tCapital[0]+2, tCapital[1]+2), iCiv, iIndependent, True, False) #This is for AI only. During Human player spawn, that area is already cleaned                        
                                utils.flipUnitsInArea((tCapital[0]-2, tCapital[1]-2), (tCapital[0]+2, tCapital[1]+2), iCiv, iIndependent2, True, False) #This is for AI only. During Human player spawn, that area is already cleaned                        
                                self.assignTechs(iCiv)
                                utils.setPlagueCountdown(iCiv, -con.iImmunity)
                                utils.clearPlague(iCiv)
                                #gc.getPlayer(iCiv).changeAnarchyTurns(1)
                                #gc.getPlayer(iCiv).setCivics(2, 11)
                                self.setFlipsDelay(iCiv, iFlipsDelay) #save
                                

                else: #starting units have already been placed, now the second part                    
                        iNumAICitiesConverted, iNumHumanCitiesToConvert = self.convertSurroundingCities(iCiv, tTopLeft, tBottomRight)
                        self.convertSurroundingPlotCulture(iCiv, tTopLeft, tBottomRight)
                        utils.flipUnitsInArea(tTopLeft, tBottomRight, iCiv, iBarbarian, False, True) #remaining barbs in the region now belong to the new civ   
                        utils.flipUnitsInArea(tTopLeft, tBottomRight, iCiv, iIndependent, False, False) #remaining independents in the region now belong to the new civ   
                        utils.flipUnitsInArea(tTopLeft, tBottomRight, iCiv, iIndependent2, False, False) #remaining independents in the region now belong to the new civ   
                        print ("utils.flipUnitsInArea()") 
                        #cover plots revealed by the lion
                        plotZero = gc.getMap().plot( 0, 0 )                        
                        if (plotZero.getNumUnits()):
                                catapult = plotZero.getUnit(0)
                                catapult.kill(False, iCiv)
                        gc.getMap().plot(0, 0).setRevealed(iCiv, False, True, -1);
                        gc.getMap().plot(0, 1).setRevealed(iCiv, False, True, -1);
                        gc.getMap().plot(1, 1).setRevealed(iCiv, False, True, -1);
                        gc.getMap().plot(1, 0).setRevealed(iCiv, False, True, -1);
                        gc.getMap().plot(123, 0).setRevealed(iCiv, False, True, -1);
                        gc.getMap().plot(123, 1).setRevealed(iCiv, False, True, -1);
                        gc.getMap().plot(2, 0).setRevealed(iCiv, False, True, -1);
                        gc.getMap().plot(2, 1).setRevealed(iCiv, False, True, -1);
                        gc.getMap().plot(2, 2).setRevealed(iCiv, False, True, -1);
                        gc.getMap().plot(1, 2).setRevealed(iCiv, False, True, -1);
                        gc.getMap().plot(0, 2).setRevealed(iCiv, False, True, -1);
                        gc.getMap().plot(122, 0).setRevealed(iCiv, False, True, -1);
                        gc.getMap().plot(122, 1).setRevealed(iCiv, False, True, -1);
                        gc.getMap().plot(122, 2).setRevealed(iCiv, False, True, -1);
                        gc.getMap().plot(123, 2).setRevealed(iCiv, False, True, -1);
                        print ("Plots covered")

                        if (gc.getPlayer(iCiv).getNumCities() > 0):
                                capital = gc.getPlayer(iCiv).getCapitalCity()
                                self.createStartingWorkers(iCiv, (capital.getX(), capital.getY()))

                        if (iNumHumanCitiesToConvert> 0):
                                self.flipPopup(iCiv, tTopLeft, tBottomRight)

                        
        def birthInForeignBorders(self, iCiv, tTopLeft, tBottomRight, tBroaderTopLeft, tBroaderBottomRight):
                
                iNumAICitiesConverted, iNumHumanCitiesToConvert = self.convertSurroundingCities(iCiv, tTopLeft, tBottomRight)
                self.convertSurroundingPlotCulture(iCiv, tTopLeft, tBottomRight)

                #now starting units must be placed
                if (iNumAICitiesConverted > 0):
                        #utils.debugTextPopup( 'iConverted OK for placing units' )
                        dummy1, plotList = utils.squareSearch( tTopLeft, tBottomRight, utils.ownedCityPlots, iCiv )        
                        rndNum = gc.getGame().getSorenRandNum(len(plotList), 'searching any city just flipped')
                        #print ("rndNum for starting units", rndNum)
                        if (len(plotList)):
                                result = plotList[rndNum]
                                if (result):
                                        self.createStartingUnits(iCiv, result)
                                        #utils.debugTextPopup( 'birthInForeignBorders after a flip' )
                                        self.assignTechs(iCiv)
                                        utils.setPlagueCountdown(iCiv, -con.iImmunity)
                                        utils.clearPlague(iCiv)
                                        #gc.getPlayer(iCiv).changeAnarchyTurns(1)
                        utils.flipUnitsInArea(tTopLeft, tBottomRight, iCiv, iBarbarian, False, True) #remaining barbs in the region now belong to the new civ 
                        utils.flipUnitsInArea(tTopLeft, tBottomRight, iCiv, iIndependent, False, False) #remaining barbs in the region now belong to the new civ 
                        utils.flipUnitsInArea(tTopLeft, tBottomRight, iCiv, iIndependent2, False, False) #remaining barbs in the region now belong to the new civ 
                        
                else:   #search another place
                        dummy, plotList = utils.squareSearch( tTopLeft, tBottomRight, utils.goodPlots, [] )
                        rndNum = gc.getGame().getSorenRandNum(len(plotList), 'searching another free plot')
                        if (len(plotList)):
                                result = plotList[rndNum]
                                if (result):
                                        self.createStartingUnits(iCiv, result)
                                        #utils.debugTextPopup( 'birthInForeignBorders in another location' )
                                        self.assignTechs(iCiv)
                                        utils.setPlagueCountdown(iCiv, -con.iImmunity)
                                        utils.clearPlague(iCiv)
                        else:
                                dummy1, plotList = utils.squareSearch( tBroaderTopLeft, tBroaderBottomRight, utils.goodPlots, [] )        
                                rndNum = gc.getGame().getSorenRandNum(len(plotList), 'searching other good plots in a broader region')
                                if (len(plotList)):
                                        result = plotList[rndNum]
                                        if (result):
                                                self.createStartingUnits(iCiv, result)
                                                self.createStartingWorkers(iCiv, result)
                                                #utils.debugTextPopup( 'birthInForeignBorders in a broader area' )
                                                self.assignTechs(iCiv)
                                                utils.setPlagueCountdown(iCiv, -con.iImmunity)
                                                utils.clearPlague(iCiv)
                        utils.flipUnitsInArea(tTopLeft, tBottomRight, iCiv, iBarbarian, True, True) #remaining barbs in the region now belong to the new civ 
                        utils.flipUnitsInArea(tTopLeft, tBottomRight, iCiv, iIndependent, True, False) #remaining barbs in the region now belong to the new civ 
                        utils.flipUnitsInArea(tTopLeft, tBottomRight, iCiv, iIndependent2, True, False) #remaining barbs in the region now belong to the new civ 

                if (iNumHumanCitiesToConvert> 0):
                        self.flipPopup(iCiv, tTopLeft, tBottomRight)




                                                
        def convertSurroundingCities(self, iCiv, tTopLeft, tBottomRight):
                iConvertedCitiesCount = 0
                iNumHumanCities = 0
                cityList = []
                self.setSpawnWar(0)
                
                #collect all the cities in the spawn region
                for x in range(tTopLeft[0], tBottomRight[0]+1):
                        for y in range(tTopLeft[1], tBottomRight[1]+1):
                                pCurrent = gc.getMap().plot( x, y )
                                if ( pCurrent.isCity()):
                                        if (pCurrent.getPlotCity().getOwner() != iCiv):
                                                cityList.append(pCurrent.getPlotCity())

                #Exceptions
                if (len(tExceptions[iCiv])):
                        for j in range(len(tExceptions[iCiv])):
                                pCurrent = gc.getMap().plot( tExceptions[iCiv][j][0], tExceptions[iCiv][j][1] )
                                if ( pCurrent.isCity()):
                                        if (pCurrent.getPlotCity().getOwner() != iCiv):
                                                print ("append", pCurrent)
                                                cityList.append(pCurrent.getPlotCity())

                print ("Birth", iCiv)
                #print (cityList)

                #for each city
                if (len(cityList)):
                        for i in range(len(cityList)):
                                loopCity = cityList[i]
                                loopX = loopCity.getX()
                                loopY = loopCity.getY()
                                print ("cityList", loopCity.getName(), (loopX, loopY))
                                iHuman = utils.getHumanID()
                                iOwner = loopCity.getOwner()
                                iCultureChange = 0 #if 0, no flip; if > 0, flip will occur with the value as variable for utils.CultureManager()
                                
                                #case 1: barbarian/independent city
                                if (iOwner == iBarbarian or iOwner == iIndependent or iOwner == iIndependent2 or iOwner == iCeltia):
                                        #utils.debugTextPopup( 'BARB' )
                                        iCultureChange = 100
                                #case 2: human city
                                elif (iOwner == iHuman and not loopCity.isCapital()):
                                        #utils.debugTextPopup( 'HUMAN' )
        ##                                bForeigners = False
        ##                                cityPlot = gc.getMap().plot(cityList[i].getX(), cityList[i].getY())
        ##                                cityCulture = cityList[i].countTotalCulture()
        ##                                iCultureThreshold = 10
        ##                                for j in range(iNumPlayers+1):
        ##                                        if (cityList[i].getCulture(j)*100 / cityCulture >= iCultureThreshold) and (j != iHuman):
        ##                                                bForeigners = True
        ##                                humanCapital = gc.getPlayer(iHuman).getCapitalCity()
        ##                                iDistance = gc.getMap().calculatePathDistance(cityPlot, gc.getMap().plot(humanCapital.getX(),humanCapital.getY()))
        ##                                if (cityList[i].isOccupation()) or (cityList[i].isDisorder()) or (bForeigners == True) or (not cityPlot.getNumUnits()) or ((not cityList[i].isGovernmentCenter()) and (iDistance >= 8) and (gc.getPlayer(iHuman).getNumCities() >= 5)):
                                        if (iNumHumanCities == 0):
                                                iNumHumanCities += 1
                                                #iConvertedCitiesCount += 1
                                                #self.flipPopup(iCiv, tTopLeft, tBottomRight)
                                #case 3: other
                                elif (not loopCity.isCapital()):   #utils.debugTextPopup( 'OTHER' )                                
                                        if (iConvertedCitiesCount < 6): #there won't be more than 5 flips in the area
                                                #utils.debugTextPopup( 'iConvertedCities OK' )
                                                iCultureChange = 50
                                                if (gc.getGame().getGameTurn() <= con.tBirth[iCiv] + 5): #if we're during a birth
                                                        rndNum = gc.getGame().getSorenRandNum(100, 'odds')
                                                        if (rndNum >= tAIStopBirthThreshold[iOwner]):
                                                                print (iOwner, "stops birth", iCiv, "rndNum:", rndNum, "threshold:", tAIStopBirthThreshold[iOwner])
                                                                if (not gc.getTeam(gc.getPlayer(iOwner).getTeam()).isAtWar(iCiv)):                                                                        
                                                                        gc.getTeam(gc.getPlayer(iOwner).getTeam()).declareWar(iCiv, False, -1)
                                                                        if (gc.getPlayer(iCiv).getNumCities() > 0): #this check is needed, otherwise game crashes
                                                                                print ("capital:", gc.getPlayer(iCiv).getCapitalCity().getX(), gc.getPlayer(iCiv).getCapitalCity().getY())
                                                                                if (gc.getPlayer(iCiv).getCapitalCity().getX() != -1 and gc.getPlayer(iCiv).getCapitalCity().getY() != -1):
                                                                                        self.createAdditionalUnits(iCiv, (gc.getPlayer(iCiv).getCapitalCity().getX(), gc.getPlayer(iCiv).getCapitalCity().getY()))
                                                                                else:
                                                                                        self.createAdditionalUnits(iCiv, tCapitals[iCiv])
                                                                        
                                                        

                                if (iCultureChange > 0):
                                        #print ("flipping ", cityList[i].getName())
                                        utils.cultureManager((loopX,loopY), iCultureChange, iCiv, iOwner, True, False, False)
                                        #gc.getMap().plot(cityList[i].getX(),cityList[i].getY()).setImprovementType(-1)
                                        
                                        utils.flipUnitsInCityBefore((loopX,loopY), iCiv, iOwner)
                                        self.setTempFlippingCity((loopX,loopY)) #necessary for the (688379128, 0) bug
                                        utils.flipCity((loopX,loopY), 0, 0, iCiv, [iOwner])                                                
                                        #print ("cityList[i].getXY", cityList[i].getX(), cityList[i].getY()) 
                                        utils.flipUnitsInCityAfter(self.getTempFlippingCity(), iCiv)

                                        #iEra = gc.getPlayer(iCiv).getCurrentEra()
                                        #if (iEra >= 2): #medieval
                                        #        if (loopCity.getPopulation() < iEra):
                                        #                loopCity.setPopulation(iEra) #causes an unidentifiable C++ exception
                                                #doesn't work (assigns UBs too)
                                                #for iLoopBuilding in range(con.iNumBuildingsPlague):                                                        
                                                #        if (gc.getBuildingInfo(iLoopBuilding).getFreeStartEra() >= 0):
                                                #                if (iEra >= gc.getBuildingInfo(iLoopBuilding).getFreeStartEra()):
                                                #                        print (iEra, iLoopBuilding, gc.getBuildingInfo(iLoopBuilding).getFreeStartEra(), loopCity.canConstruct(iLoopBuilding, False, False, False))
                                                #                        if (loopCity.canConstruct(iLoopBuilding, False, False, False)):
                                                #                                if (not loopCity.hasBuilding(iLoopBuilding)):
                                                #                                        loopCity.setHasRealBuilding(iLoopBuilding, True)

                                        #cityList[i].setHasRealBuilding(con.iPlague, False)   #buggy
                                        
                                        iConvertedCitiesCount += 1
                                        print ("iConvertedCitiesCount", iConvertedCitiesCount)

                if (iConvertedCitiesCount > 0):
                        if (gc.getPlayer(iCiv).isHuman()):
                                CyInterface().addMessage(iCiv, True, con.iDuration, CyTranslator().getText("TXT_KEY_FLIP_TO_US", ()), "", 0, "", ColorTypes(con.iGreen), -1, -1, True, True)

                #print( "converted cities", iConvertedCitiesCount)
                return (iConvertedCitiesCount, iNumHumanCities)



        def convertSurroundingPlotCulture(self, iCiv, tTopLeft, tBottomRight):
                
                for x in range(tTopLeft[0], tBottomRight[0]+1):
                        for y in range(tTopLeft[1], tBottomRight[1]+1):
                                pCurrent = gc.getMap().plot( x, y )
                                if (not pCurrent.isCity()):
                                        utils.convertPlotCulture(pCurrent, iCiv, 100, False)

                if (len(tExceptions[iCiv])):
                        for j in range(len(tExceptions[iCiv])):
                                pCurrent = gc.getMap().plot( tExceptions[iCiv][j][0], tExceptions[iCiv][j][1] )
                                if (not pCurrent.isCity()):
                                        utils.convertPlotCulture(pCurrent, iCiv, 100, False)




##        def minorBirth(self, iCurrentTurn, iCiv, tCapital, name, iPopulation):
##                iBirthYear = tBirth[iCiv]
##                iHuman = utils.getHumanID()
##                pCiv = gc.getPlayer(iCiv)
##                bRoomFound = False
##                #if (iCurrentTurn > 0 and iCiv == iPortugal): #debug
##                if (iCurrentTurn == iBirthYear-1): #-1
##                        tTopLeft = tCoreAreasTL[iCiv]
##                        tBottomRight = tCoreAreasBR[iCiv]
##                        for x in range(tTopLeft[0], tBottomRight[0] + 1):
##                                for y in range(tTopLeft[1], tBottomRight[1] + 1):
##                                        pCurrent=gc.getMap().plot(x, y)
##                                        #print ("pCurrent", x, y)
##                                        for iLoopCiv in range(iNumTotalPlayers+1): #Barbarians as well
##                                                if (iLoopCiv != iCiv):
##                                                        oldCulture = pCurrent.getCulture(iLoopCiv)
##                                                        pCurrent.setCulture(iLoopCiv, 0, True)
##                                                        pCurrent.changeCulture(iCiv, oldCulture, True)
##                                                        #print (iLoopCiv, oldCulture)
##                        bCityInArea = False                        
##                        for x in range(tCapital[0] - 1, tCapital[0] + 2):        # from x-1 to x+1
##                                for y in range(tCapital[1] - 1, tCapital[1] + 2):	# from y-1 to y+1
##                                        pCurrent=gc.getMap().plot(x, y)
##                                        if (pCurrent.isCity()):
##                                                bCityInArea = True
##                        if (not bCityInArea):
##                                bRoomFound = True
##                                gc.getMap().plot(tCapital[0], tCapital[1]).eraseAIDevelopment()
##                                gc.getMap().plot(tCapital[0], tCapital[1]).setOwner(-1)
##                                for x in range(tCapital[0] - 1, tCapital[0] + 2):      
##                                        for y in range(tCapital[1] - 1, tCapital[1] + 2):
##                                                pCurrent=gc.getMap().plot(x, y)
##                                                pCurrent.setOwner(-1)
##                        else:
##                                bDeleteEverything = True
##                                for x in range(tCapital[0] - 1, tCapital[0] + 2):      
##                                        for y in range(tCapital[1] - 1, tCapital[1] + 2):
##                                                pCurrent=gc.getMap().plot(x, y)
##                                                if (pCurrent.isVisible(iHuman, False)):
##                                                        bDeleteEverything = False
##                                if (bDeleteEverything):
##                                        for x in range(tCapital[0] - 1, tCapital[0] + 2):      
##                                                for y in range(tCapital[1] - 1, tCapital[1] + 2):
##                                                        pCurrent=gc.getMap().plot(x, y)
##                                                        pCurrent.eraseAIDevelopment()
##                                                        pCurrent.setOwner(-1)
##                                        bRoomFound = True
##                        print ("bRoomFound", bRoomFound, tCapital)
##                        if (bRoomFound):
##                                self.createStartingUnits(iCiv, tCapital)
##                                pCiv.found(tCapital[0], tCapital[1])
##                                CyGlobalContext().getMap().plot(tCapital[0], tCapital[1]).getPlotCity().setName(name, False)
##                                CyGlobalContext().getMap().plot(tCapital[0], tCapital[1]).getPlotCity().setPopulation(iPopulation)
##                                for x in range(tCapital[0] - 1, tCapital[0] + 2):      
##                                        for y in range(tCapital[1] - 1, tCapital[1] + 2):
##                                                pCurrent=gc.getMap().plot(x, y)
##                                                pCurrent.changeCulture(iCiv, 100, True)
##                                            
##                                self.assignTechs(iCiv)
##                                utils.setPlagueCountdown(iCiv, -con.iImmunity)
##                                utils.clearPlague(iCiv)
##                                for iLoopCiv in range( iNumActivePlayers ):
##                                        if (iLoopCiv != iCiv and iLoopCiv != iHuman):
##                                                gc.getTeam(gc.getPlayer(iCiv).getTeam()).signOpenBorders(iLoopCiv)
##
##                                #convert surrounding cities
##                                for x in range(tTopLeft[0], tBottomRight[0] + 1):        # from x-1 to x+1
##                                        for y in range(tTopLeft[1], tBottomRight[1] + 1):	# from y-1 to y+1
##                                                pCurrent=gc.getMap().plot(x, y)
##                                                if (pCurrent.isCity()):
##                                                        city = pCurrent.getPlotCity()
##                                                        iOwner = city.getOwner()
##                                                        if (iOwner != iCiv):                                                
##                                                                utils.flipUnitsInCityBefore((x,y), iCiv, iOwner)
##                                                                self.setTempFlippingCity((x,y)) #necessary for the (688379128, 0) bug
##                                                                utils.flipCity((x,y), 0, 0, iCiv, [iOwner])                                                
##                                                                utils.flipUnitsInCityAfter(self.getTempFlippingCity(), iCiv)
##                                return True
##                        else:
##                                return False
                                



        def findSeaPlots( self, tCoords, iRange):
                """Searches a sea plot that isn't occupied by a unit and isn't a civ's territory surrounding the starting coordinates"""
                seaPlotList = []
                for x in range(tCoords[0] - iRange, tCoords[0] + iRange+1):        
                        for y in range(tCoords[1] - iRange, tCoords[1] + iRange+1):	
                                pCurrent = gc.getMap().plot( x, y )
                                if ( pCurrent.isWater()):
                                        if ( not pCurrent.isUnit() ):
                                                if (pCurrent.countTotalCulture() == 0 ):
                                                        seaPlotList.append(pCurrent)
                                                        # this is a good plot, so paint it and continue search
                if (len(seaPlotList) > 0):
                        rndNum = gc.getGame().getSorenRandNum(len(seaPlotList), 'sea plot')
                        result = seaPlotList[rndNum]
                        if (result):                                                        
                                    return ((result.getX(), result.getY()))
                return (None)


        def giveColonists( self, iCiv, tBroaderAreaTL, tBroaderAreaBR):
                pCiv = gc.getPlayer(iCiv)
                teamCiv = gc.getTeam(pCiv.getTeam())
                if (teamCiv.isHasTech(con.iAstronomy)) and (self.getColonistsAlreadyGiven(iCiv) <= 6) and (pCiv.isAlive()) and (pCiv.isHuman() == False):
                        cityList = []
                        #collect all the coastal cities belonging to iCiv in the area
                        for x in range(tBroaderAreaTL[0], tBroaderAreaBR[0]+1):
                                for y in range(tBroaderAreaTL[1], tBroaderAreaBR[1]+1):
                                        pCurrent = gc.getMap().plot( x, y )
                                        if ( pCurrent.isCity()):
                                                city = pCurrent.getPlotCity()
                                                if (city.getOwner() == iCiv):
                                                        if (city.isCoastalOld()):
                                                                cityList.append(city)                                                        
                        if (len(cityList)):
                                result = cityList[0]
##                                for loopCity in cityList:
##                                        if (loopCity.getX() < result.getX() and \
##                                            loopCity.getX() >= tNormalAreasTL[iCiv][0] and \
##                                            loopCity.getX() <= tNormalAreasBR[iCiv][0] and \
##                                            loopCity.getY() >= tNormalAreasTL[iCiv][1] and \
##                                            loopCity.getY() <= tNormalAreasBR[iCiv][1]):
##                                                result = loopCity
                                rndNum = gc.getGame().getSorenRandNum(len(cityList), 'random city')
                                result = cityList[rndNum]
                                if (result):
                                        tPlot = (result.getX(), result.getY())
                                        utils.makeUnit(con.iSettler, iCiv, tPlot, 1)
                                        if (rndNum % 2 == 0):
                                                utils.makeUnit(con.iPikeman, iCiv, tPlot, 1)
                                        else:
                                                utils.makeUnit(con.iWorker, iCiv, tPlot, 1)
                                        if (teamCiv.isHasTech(con.iGunpowder)):
                                                utils.makeUnit(con.iMusketman, iCiv, tPlot, 1)
                                        else:
                                                if (iCiv == iSpain):
                                                        if (teamSpain.isHasTech(con.iGuilds)):
                                                                utils.makeUnit(con.iConquistador, iCiv, tPlot, 1)
                                                        else:
                                                                utils.makeUnit(con.iLongbowman, iCiv, tPlot, 1)
                                                else:
                                                        utils.makeUnit(con.iLongbowman, iCiv, tPlot, 1)
                                        if (iCiv == iNetherlands):
                                                gc.getPlayer(iCiv).initUnit(con.iNetherlandsOostindievaarder, tPlot[0], tPlot[1], UnitAITypes.UNITAI_SETTLER_SEA, DirectionTypes.DIRECTION_SOUTH)
                                        else:
                                                gc.getPlayer(iCiv).initUnit(con.iGalleon, tPlot[0], tPlot[1], UnitAITypes.UNITAI_SETTLER_SEA, DirectionTypes.DIRECTION_SOUTH)
                                        iColonistsAlreadyGiven = self.getColonistsAlreadyGiven(iCiv) + 1
                                        self.setColonistsAlreadyGiven(iCiv, iColonistsAlreadyGiven)
                                        utils.setStability(iCiv, utils.getStability(iCiv) + 1)
                                        print ("colonists", iCiv)

                #part2: upgrade galleys to galleons, just once
                if (gc.getTeam(pCiv.getTeam()).isHasTech(con.iAstronomy)) and (self.getColonistsAlreadyGiven(iCiv) == 0) and (pCiv.isAlive()) and (pCiv.isHuman() == False):
                        for x in range(0, 123+1):
                                for y in range(0, 67+1):
                                        galleyPlot = gc.getMap().plot(x,y)
                                        iNumUnitsInAPlot = galleyPlot.getNumUnits()
                                        if (iNumUnitsInAPlot):  
                                                for i in range(iNumUnitsInAPlot):                                                
                                                        unit = galleyPlot.getUnit(i)
                                                        if (unit.getOwner() == iCiv):
                                                                if (unit.getUnitType() == iGalley):
                                                                        unit.kill(False, iBarbarian)
                                                                        gc.getPlayer(iCiv).initUnit(con.iGalleon, x, y, UnitAITypes.UNITAI_SETTLER_SEA, DirectionTypes.DIRECTION_SOUTH)
                                                                        i = i - 1
                          


        def onFirstContact(self, iTeamX, iHasMetTeamY):
                if (gc.getGame().getGameTurn() > con.tBirth[con.iAztecs] + 5 and gc.getGame().getGameTurn() < con.i1800AD):
                        iOldWorldCiv = -1
                        iNewWorldCiv = -1
                        #if (iTeamX in con.lCivBioOldWorld and iHasMetTeamY in con.lCivBioNewWorld):
                        #        iOldWorldCiv = iTeamX
                        #        iNewWorldCiv = iHasMetTeamY
                        if (iTeamX in con.lCivBioNewWorld and iHasMetTeamY in con.lCivBioOldWorld):
                                iNewWorldCiv = iTeamX
                                iOldWorldCiv = iHasMetTeamY
                        #print ("iOldWorldCiv", iOldWorldCiv, "iNewWorldCiv", iNewWorldCiv)
                        if (iOldWorldCiv != -1 and iNewWorldCiv != -1):
                                
                                iIndex = -1
                                if (iNewWorldCiv == iMaya):
                                        iIndex = 0
                                elif (iNewWorldCiv == iInca):
                                        iIndex = 1
                                elif (iNewWorldCiv == iAztecs):
                                        iIndex = 2
                                        
                                bAlreadyContacted = False
                                if (self.getFirstContactConquerors(iIndex) == 1):
                                        bAlreadyContacted = True
                                        
                                #print ("bAlreadyContacted", bAlreadyContacted)
                                if (bAlreadyContacted == False and iIndex != -1):        

                                        tContactZoneTL = [0, 0]
                                        tContactZoneBR = [1, 1]
                                        tContactPlot = [-1, -1]
                                        tArrivalPlot = [-1, -1]

                                        if (iNewWorldCiv == iMaya):
                                                tContactZoneTL = [15, 30]
                                                tContactZoneBR = [30, 42]
                                        if (iNewWorldCiv == iAztecs):
                                                tContactZoneTL = [11, 31]
                                                tContactZoneBR = [30, 45]
                                        if (iNewWorldCiv == iInca):
                                                tContactZoneTL = [21, 11]
                                                tContactZoneBR = [39, 34]

                                        self.setFirstContactConquerors(iIndex, 1)
                                        print ("1st contact", iNewWorldCiv, iOldWorldCiv)
                                        if (iNewWorldCiv == iInca):
                                                gc.getMap().plot(27, 30).setFeatureType(-1, 0)
                                                gc.getMap().plot(28, 31).setFeatureType(-1, 0)
                                                gc.getMap().plot(31, 13).setPlotType(PlotTypes.PLOT_HILLS, True, True) 
                                        if (iNewWorldCiv == iAztecs):
                                                gc.getMap().plot(40, 66).setPlotType(PlotTypes.PLOT_HILLS, True, True)  #debug

                                            
                                        #print ("tContactZoneTL", tContactZoneTL, "tContactZoneBR", tContactZoneBR)
                                        for x in range(tContactZoneTL[0], tContactZoneBR[0]+1):
                                                for y in range(tContactZoneTL[1], tContactZoneBR[1]+1):
                                                        pCurrent = gc.getMap().plot( x, y )
                                                        if (pCurrent.isVisible(iNewWorldCiv, False) and pCurrent.isVisible(iOldWorldCiv, False)):
                                                                tContactPlot[0] = x
                                                                tContactPlot[1] = y
                                                                print ("1st contact in", x, y)
                                                                break
##                                                        if (pCurrent.isVisible(iNewWorldCiv, False)):
##                                                                iNumUnitsInAPlot = pCurrent.getNumUnits()
##                                                                print ("pCurrent", x, y, pCurrent.getNumUnits())
##                                                                if (iNumUnitsInAPlot):                                                                  
##                                                                        for i in range(iNumUnitsInAPlot):                                                
##                                                                                unit = pCurrent.getUnit(i)
##                                                                                print ("unit.getOwner()", unit.getOwner())
##                                                                                if (unit.getOwner() == iOldWorldCiv):
##                                                                                        tContactPlot[0] = x
##                                                                                        tContactPlot[1] = y
##                                                                                        print ("1st contact")
##                                                                                        break
                                        #print ("tContactPlot", tContactPlot)
                                        if (tContactPlot != [-1, -1]):
                                                iMinDistance = 100
                                                for x in range(tContactZoneTL[0], tContactZoneBR[0]+1):
                                                        for y in range(tContactZoneTL[1], tContactZoneBR[1]+1):
                                                                pCurrent = gc.getMap().plot( x, y )
                                                                #print ("XY", x, y)
                                                                if (pCurrent.getOwner() == iNewWorldCiv and not pCurrent.isCity()):
                                                                        if ( pCurrent.isHills() or pCurrent.isFlatlands() ):
                                                                                #print ("hills or flat")
                                                                                if ((pCurrent.getFeatureType() != con.iJungle) and (pCurrent.getTerrainType() != con.iMarsh) and not (x == 25 and y == 32)): #(25,32) is sometimes blocked                                                                  
                                                                                        iDistance = utils.calculateDistance(x, y, tContactPlot[0], tContactPlot[1])
                                                                                        #print ("Distance", x, y, iDistance)
                                                                                        if (iDistance < iMinDistance):
                                                                                                iMinDistance = iDistance
                                                                                                tArrivalPlot[0] = x
                                                                                                tArrivalPlot[1] = y

                                        #print ("tArrivalPlot", tArrivalPlot)
                                        if (tArrivalPlot != [-1, -1]):
                                                print ("conquerors triggered in", tArrivalPlot)
                                                teamOldWorldCiv = gc.getTeam(gc.getPlayer(iOldWorldCiv).getTeam())

                                                iModifier1 = 0
                                                if ((iNewWorldCiv == iInca or gc.getPlayer(iNewWorldCiv).getNumCities() > 4) and not gc.getPlayer(iNewWorldCiv).isHuman()):
                                                        iModifier1 = 1
                                                if (gc.getPlayer(iNewWorldCiv).getNumCities() > 6 and gc.getPlayer(iNewWorldCiv).isHuman()):
                                                        iModifier1 = 1

                                                iModifier2 = 0
                                                if (not gc.getPlayer(iOldWorldCiv).isHuman() and not gc.getPlayer(iNewWorldCiv).isHuman()):
                                                        iModifier2 = 1

                                                if (not gc.getPlayer(iOldWorldCiv).isHuman()):
                                                        teamOldWorldCiv.declareWar(iNewWorldCiv, False, -1)

                                                if (teamOldWorldCiv.isHasTech(con.iRifling)):
                                                        if (iOldWorldCiv == iEngland):
                                                                utils.makeUnit(con.iEnglishRedcoat, iOldWorldCiv, tArrivalPlot, 1 + iModifier2)
                                                        else:
                                                                utils.makeUnit(con.iRifleman, iOldWorldCiv, tArrivalPlot, 1 + iModifier2)
                                                elif (teamOldWorldCiv.isHasTech(con.iGunpowder)):
                                                        if (iOldWorldCiv == iFrance):
                                                                utils.makeUnit(con.iFrenchMusketeer, iOldWorldCiv, tArrivalPlot, 1 + iModifier2)
                                                        elif (iOldWorldCiv == iTurkey):
                                                                utils.makeUnit(con.iOttomanJanissary, iOldWorldCiv, tArrivalPlot, 1 + iModifier2)
                                                        else:
                                                                utils.makeUnit(con.iMusketman, iOldWorldCiv, tArrivalPlot, 1 + iModifier2)
                                                else:
                                                        if (iOldWorldCiv == iChina):
                                                                utils.makeUnit(con.iChinaChokonu, iOldWorldCiv, tArrivalPlot, 1 + iModifier2)
                                                        else:
                                                                utils.makeUnit(con.iCrossbowman, iOldWorldCiv, tArrivalPlot, 1 + iModifier2)
                                                        
                                                utils.makeUnit(con.iPikeman, iOldWorldCiv, tArrivalPlot, 2)
                                                
                                                if (teamOldWorldCiv.isHasTech(con.iGunpowder)):
                                                        utils.makeUnit(con.iCannon, iOldWorldCiv, tArrivalPlot, 1 + iModifier1 + iModifier2)
                                                else:
                                                        utils.makeUnit(con.iCatapult, iOldWorldCiv, tArrivalPlot, 1 + iModifier1 + iModifier2)

                                                if (iOldWorldCiv == iSpain and teamOldWorldCiv.isHasTech(con.iGunpowder)):
                                                        utils.makeUnit(con.iConquistador, iOldWorldCiv, tArrivalPlot, 2 + iModifier1)
                                                else:
                                                        if (teamOldWorldCiv.isHasTech(con.iGuilds)):
                                                                if (iOldWorldCiv == iArabia):
                                                                        utils.makeUnit(con.iCamelArcher, iOldWorldCiv, tArrivalPlot, 2 + iModifier1)
                                                                elif (iOldWorldCiv == iMongolia):
                                                                        utils.makeUnit(con.iMongolKeshik, iOldWorldCiv, tArrivalPlot, 2 + iModifier1)
                                                                else:
                                                                        utils.makeUnit(con.iKnight, iOldWorldCiv, tArrivalPlot, 2 + iModifier1)

                                                
                                                if (gc.getPlayer(iNewWorldCiv).isHuman()):
                                                        CyInterface().addMessage(iNewWorldCiv, True, con.iDuration, CyTranslator().getText("TXT_KEY_FIRST_CONTACT_NEWWORLD", ()), "", 0, "", ColorTypes(con.iWhite), -1, -1, True, True)
                                                if (gc.getPlayer(iOldWorldCiv).isHuman()):
                                                        CyInterface().addMessage(iOldWorldCiv, True, con.iDuration, CyTranslator().getText("TXT_KEY_FIRST_CONTACT_OLDWORLD", ()), "", 0, "", ColorTypes(con.iWhite), -1, -1, True, True)




        def initMinorBetrayal( self, iCiv ):
                iHuman = utils.getHumanID()
                dummy, plotList = utils.squareSearch( tCoreAreasTL[iCiv], tCoreAreasBR[iCiv], utils.outerInvasion, [] )
                rndNum = gc.getGame().getSorenRandNum(len(plotList), 'searching a free plot abroad human players borders')
                if (len(plotList)):
                        result = plotList[rndNum]
                        if (result):
                                self.createAdditionalUnits(iCiv, result)
                                self.unitsBetrayal(iCiv, iHuman, tCoreAreasTL[iCiv], tCoreAreasBR[iCiv], result)



        def initBetrayal( self ):
                iHuman = utils.getHumanID()
                turnsLeft = self.getBetrayalTurns()
                dummy, plotList = utils.squareSearch( self.getTempTopLeft(), self.getTempBottomRight(), utils.outerInvasion, [] )
                rndNum = gc.getGame().getSorenRandNum(len(plotList), 'searching a free plot abroad human players (or in general, the old civ if human player just swtiched) borders')
                if (not len(plotList)):
                        dummy, plotList = utils.squareSearch( self.getTempTopLeft(), self.getTempBottomRight(), utils.innerSpawn, [self.getOldCivFlip(), self.getNewCivFlip()] )
                        rndNum = gc.getGame().getSorenRandNum(len(plotList), 'searching a free plot within human or new civs border but distant from units')                                
                if (not len(plotList)):
                        dummy, plotList = utils.squareSearch( self.getTempTopLeft(), self.getTempBottomRight(), utils.innerInvasion, [self.getOldCivFlip(), self.getNewCivFlip()] )
                        rndNum = gc.getGame().getSorenRandNum(len(plotList), 'searching a free plot within human or new civs border')                                
                if (len(plotList)):
                        result = plotList[rndNum]
                        if (result):
                                if (turnsLeft == iBetrayalPeriod):
                                        self.createAdditionalUnits(self.getNewCivFlip(), result)
                                self.unitsBetrayal(self.getNewCivFlip(), self.getOldCivFlip(), self.getTempTopLeft(), self.getTempBottomRight(), result)
                self.setBetrayalTurns(turnsLeft - 1)



        def unitsBetrayal( self, iNewOwner, iOldOwner, tTopLeft, tBottomRight, tPlot ):
                #print ("iNewOwner", iNewOwner, "iOldOwner", iOldOwner, "tPlot", tPlot)
                if (gc.getPlayer(self.getOldCivFlip()).isHuman()):
                        CyInterface().addMessage(self.getOldCivFlip(), False, con.iDuration, CyTranslator().getText("TXT_KEY_FLIP_BETRAYAL", ()), "", 0, "", ColorTypes(con.iGreen), -1, -1, True, True)
                elif (gc.getPlayer(self.getNewCivFlip()).isHuman()):
                        CyInterface().addMessage(self.getNewCivFlip(), False, con.iDuration, CyTranslator().getText("TXT_KEY_FLIP_BETRAYAL_NEW", ()), "", 0, "", ColorTypes(con.iGreen), -1, -1, True, True)
                for x in range(tTopLeft[0], tBottomRight[0]+1):
                        for y in range(tTopLeft[1], tBottomRight[1]+1):
                                killPlot = gc.getMap().plot(x,y)
                                iNumUnitsInAPlot = killPlot.getNumUnits()
                                if (iNumUnitsInAPlot):                                                                  
                                        for i in range(iNumUnitsInAPlot):                                                
                                                unit = killPlot.getUnit(i)
                                                if (unit.getOwner() == iOldOwner):
                                                        rndNum = gc.getGame().getSorenRandNum(100, 'betrayal')
                                                        if (rndNum >= iBetrayalThreshold):
                                                                if (unit.getDomainType() == 2): #land unit
                                                                        iUnitType = unit.getUnitType()
                                                                        unit.kill(False, iNewOwner)
                                                                        utils.makeUnit(iUnitType, iNewOwner, tPlot, 1)
                                                                        i = i - 1



        def createAdditionalUnits( self, iCiv, tPlot ):
                if (iCiv == iGreece):
                        utils.makeUnit(con.iGreekPhalanx, iCiv, tPlot, 4)
                if (iCiv == iPersia):
                        utils.makeUnit(con.iPersiaImmortal, iCiv, tPlot, 4)
                if (iCiv == iCarthage):
                        utils.makeUnit(con.iCarthageNumidianCavalry, iCiv, tPlot, 4)
                if (iCiv == iRome):
                        utils.makeUnit(con.iRomePraetorian, iCiv, tPlot, 4)
                if (iCiv == iJapan):
                        utils.makeUnit(con.iArcher, iCiv, tPlot, 2)
                        utils.makeUnit(con.iSwordsman, iCiv, tPlot, 2)
                if (iCiv == iEthiopia):
                        utils.makeUnit(con.iArcher, iCiv, tPlot, 2)
                        utils.makeUnit(con.iSwordsman, iCiv, tPlot, 2)
                if (iCiv == iMaya):
                        utils.makeUnit(con.iArcher, iCiv, tPlot, 2)
                        utils.makeUnit(con.iMayaHolkan, iCiv, tPlot, 2)   
                if (iCiv == iVikings):
                        utils.makeUnit(con.iAxeman, iCiv, tPlot, 2)
                        utils.makeUnit(con.iSwordsman, iCiv, tPlot, 2)
                if (iCiv == iArabia):
                        utils.makeUnit(con.iLongbowman, iCiv, tPlot, 2)
                        utils.makeUnit(con.iArabiaCamelarcher, iCiv, tPlot, 4)
                if (iCiv == iKhmer):
                        utils.makeUnit(con.iSwordsman, iCiv, tPlot, 3)
                        utils.makeUnit(con.iKhmerBallistaElephant, iCiv, tPlot, 2)
                if (iCiv == iSpain):
                        utils.makeUnit(con.iLongbowman, iCiv, tPlot, 3)
                        utils.makeUnit(con.iSwordsman, iCiv, tPlot, 3)
                if (iCiv == iFrance):
                        utils.makeUnit(con.iLongbowman, iCiv, tPlot, 3)
                        utils.makeUnit(con.iSwordsman, iCiv, tPlot, 3)
                if (iCiv == iEngland):
                        utils.makeUnit(con.iLongbowman, iCiv, tPlot, 3)
                        utils.makeUnit(con.iSwordsman, iCiv, tPlot, 3)
                if (iCiv == iGermany):                        
                        utils.makeUnit(con.iLongbowman, iCiv, tPlot, 3)
                        utils.makeUnit(con.iSwordsman, iCiv, tPlot, 3)
                if (iCiv == iRussia):
                        utils.makeUnit(con.iLongbowman, iCiv, tPlot, 2)
                        utils.makeUnit(con.iSwordsman, iCiv, tPlot, 2)
                        utils.makeUnit(con.iHorseArcher, iCiv, tPlot, 2)
                if (iCiv == iNetherlands):                        
                        utils.makeUnit(con.iLongbowman, iCiv, tPlot, 3)
                        utils.makeUnit(con.iPikeman, iCiv, tPlot, 3)
                if (iCiv == iMali):
                        utils.makeUnit(con.iMaliSkirmisher, iCiv, tPlot, 4)
                        utils.makeUnit(con.iSwordsman, iCiv, tPlot, 3)
                if (iCiv == iTurkey):
                        utils.makeUnit(con.iCrossbowman, iCiv, tPlot, 3)
                        utils.makeUnit(con.iHorseArcher, iCiv, tPlot, 3)
                if (iCiv == iPortugal):                        
                        utils.makeUnit(con.iLongbowman, iCiv, tPlot, 3)
                        utils.makeUnit(con.iPikeman, iCiv, tPlot, 3)
                if (iCiv == iInca):
                        utils.makeUnit(con.iIncanQuechua, iCiv, tPlot, 5)
                        utils.makeUnit(con.iArcher, iCiv, tPlot, 3)
                if (iCiv == iMongolia):
                        utils.makeUnit(con.iCrossbowman, iCiv, tPlot, 2)
                        utils.makeUnit(con.iHorseArcher, iCiv, tPlot, 2) 
                        utils.makeUnit(con.iMongolKeshik, iCiv, tPlot, 4)
                if (iCiv == iAztecs):
                        utils.makeUnit(con.iAztecJaguar, iCiv, tPlot, 5)
                        utils.makeUnit(con.iArcher, iCiv, tPlot, 3)
                if (iCiv == iAmerica):
                        utils.makeUnit(con.iPikeman, iCiv, tPlot, 3)
                        utils.makeUnit(con.iMusketman, iCiv, tPlot, 3)
                        utils.makeUnit(con.iCannon, iCiv, tPlot, 3)


        def createStartingUnits( self, iCiv, tPlot ):
                if (iCiv == iGreece):
                        utils.makeUnit(con.iSettler, iCiv, tPlot, 1)
                        utils.makeUnit(con.iWarrior, iCiv, tPlot, 2)
                        utils.makeUnit(con.iGreekPhalanx, iCiv, tPlot, 2) #3
                        tSeaPlot = self.findSeaPlots(tPlot, 1)
                        if (tSeaPlot):
                                #utils.makeUnit(con.iWorkBoat, iCiv, tSeaPlot, 1)
                                pGreece.initUnit(con.iGalley, tSeaPlot[0], tSeaPlot[1], UnitAITypes.UNITAI_SETTLER_SEA, DirectionTypes.DIRECTION_SOUTH)
                                utils.makeUnit(con.iSettler, iCiv, tSeaPlot, 1)
                if (iCiv == iPersia):
                        utils.makeUnit(con.iSettler, iCiv, tPlot, 2)
                        utils.makeUnit(con.iArcher, iCiv, tPlot, 5)
                        utils.makeUnit(con.iPersiaImmortal, iCiv, tPlot, 7)
                if (iCiv == iCarthage):
                        utils.makeUnit(con.iSettler, iCiv, tPlot, 1)
                        utils.makeUnit(con.iArcher, iCiv, tPlot, 3)
                        utils.makeUnit(con.iCarthageNumidianCavalry, iCiv, tPlot, 3)
                        tSeaPlot = self.findSeaPlots(tPlot, 1)
                        if (tSeaPlot):                                
                                utils.makeUnit(con.iWorkBoat, iCiv, tSeaPlot, 2)
                                pCarthage.initUnit(con.iGalley, tSeaPlot[0], tSeaPlot[1], UnitAITypes.UNITAI_SETTLER_SEA, DirectionTypes.DIRECTION_SOUTH)
                                utils.makeUnit(con.iSettler, iCiv, tSeaPlot, 1)
                                pCarthage.initUnit(con.iGalley, tSeaPlot[0], tSeaPlot[1], UnitAITypes.UNITAI_ASSAULT_SEA, DirectionTypes.DIRECTION_SOUTH)
                                pCarthage.initUnit(con.iTrireme, tSeaPlot[0], tSeaPlot[1], UnitAITypes.UNITAI_ESCORT_SEA, DirectionTypes.DIRECTION_SOUTH)
                if (iCiv == iRome):
                        utils.makeUnit(con.iSettler, iCiv, tPlot, 3)
                        utils.makeUnit(con.iArcher, iCiv, tPlot, 3)
                        utils.makeUnit(con.iRomePraetorian, iCiv, tPlot, 4)
                        tSeaPlot = self.findSeaPlots(tPlot, 1)
                        if (tSeaPlot):                                
                                utils.makeUnit(con.iWorkBoat, iCiv, tSeaPlot, 1)
                                pRome.initUnit(con.iGalley, tSeaPlot[0], tSeaPlot[1], UnitAITypes.UNITAI_ASSAULT_SEA, DirectionTypes.DIRECTION_SOUTH)
                                pRome.initUnit(con.iGalley, tSeaPlot[0], tSeaPlot[1], UnitAITypes.UNITAI_ASSAULT_SEA, DirectionTypes.DIRECTION_SOUTH)
                if (iCiv == iJapan):
                        utils.makeUnit(con.iSettler, iCiv, tPlot, 2)
                        utils.makeUnit(con.iArcher, iCiv, tPlot, 2)
                        utils.makeUnit(con.iSwordsman, iCiv, tPlot, 2)
                        tSeaPlot = self.findSeaPlots(tPlot, 1)
                        if (tSeaPlot):                                
                                utils.makeUnit(con.iWorkBoat, iCiv, tSeaPlot, 2)
                if (iCiv == iEthiopia):
                        utils.makeUnit(con.iSettler, iCiv, tPlot, 2)
                        utils.makeUnit(con.iArcher, iCiv, tPlot, 2)
                        utils.makeUnit(con.iSwordsman, iCiv, tPlot, 1)
                        utils.makeUnit(con.iAxeman, iCiv, tPlot, 1)
                        tSeaPlot = self.findSeaPlots(tPlot, 2)
                        if (tSeaPlot):                                
                                utils.makeUnit(con.iWorkBoat, iCiv, tSeaPlot, 1)
                if (iCiv == iMaya):
                        utils.makeUnit(con.iSettler, iCiv, tPlot, 2)
                        utils.makeUnit(con.iWarrior, iCiv, tPlot, 3)
                if (iCiv == iVikings):
                        utils.makeUnit(con.iSettler, iCiv, tPlot, 3)
                        utils.makeUnit(con.iArcher, iCiv, tPlot, 3)
                        utils.makeUnit(con.iAxeman, iCiv, tPlot, 1)
                        tSeaPlot = self.findSeaPlots(tPlot, 1)
                        if (tSeaPlot):                                
                                utils.makeUnit(con.iWorkBoat, iCiv, tSeaPlot, 1)
                                pVikings.initUnit(con.iGalley, tSeaPlot[0], tSeaPlot[1], UnitAITypes.UNITAI_ASSAULT_SEA, DirectionTypes.DIRECTION_SOUTH)
                                utils.makeUnit(con.iAxeman, iCiv, tSeaPlot, 2)
                                pVikings.initUnit(con.iGalley, tSeaPlot[0], tSeaPlot[1], UnitAITypes.UNITAI_SETTLER_SEA, DirectionTypes.DIRECTION_SOUTH)                                
                if (iCiv == iArabia):
                        utils.makeUnit(con.iSettler, iCiv, tPlot, 3)
                        utils.makeUnit(con.iLongbowman, iCiv, tPlot, 4)
                        utils.makeUnit(con.iSwordsman, iCiv, tPlot, 2)
                        utils.makeUnit(con.iArabiaCamelarcher, iCiv, tPlot, 5)                
                if (iCiv == iKhmer):
                        utils.makeUnit(con.iSettler, iCiv, tPlot, 2)
                        utils.makeUnit(con.iArcher, iCiv, tPlot, 2)
                        utils.makeUnit(con.iKhmerBallistaElephant, iCiv, tPlot, 2)
                        utils.makeUnit(con.iBuddhistMissionary, iCiv, tPlot, 1)
                        tSeaPlot = self.findSeaPlots(tPlot, 2)
                        if (tSeaPlot):                                
                                utils.makeUnit(con.iWorkBoat, iCiv, tSeaPlot, 1)
                                utils.makeUnit(con.iSettler, iCiv, tPlot, 1)
                                utils.makeUnit(con.iArcher, iCiv, tPlot, 1)
                                pKhmer.initUnit(con.iGalley, tSeaPlot[0], tSeaPlot[1], UnitAITypes.UNITAI_SETTLER_SEA, DirectionTypes.DIRECTION_SOUTH)
                if (iCiv == iSpain):
                        utils.makeUnit(con.iSettler, iCiv, tPlot, 3)
                        utils.makeUnit(con.iLongbowman, iCiv, tPlot, 4)
                        utils.makeUnit(con.iSwordsman, iCiv, tPlot, 2)
                        if (not gc.getPlayer(0).isPlayable()): #late start condition
                                utils.makeUnit(con.iWorker, iCiv, tPlot, 1) #there is no carthaginian city in Iberia and Portugal may found 2 cities otherwise (a settler is too much)
                if (iCiv == iFrance):
                        utils.makeUnit(con.iSettler, iCiv, tPlot, 2)
                        utils.makeUnit(con.iLongbowman, iCiv, tPlot, 4)
                        utils.makeUnit(con.iSwordsman, iCiv, tPlot, 2)
                        utils.makeUnit(con.iAxeman, iCiv, tPlot, 3)
                if (iCiv == iEngland):
                        utils.makeUnit(con.iSettler, iCiv, tPlot, 4)
                        utils.makeUnit(con.iLongbowman, iCiv, tPlot, 4)
                        tSeaPlot = self.findSeaPlots(tPlot, 1)
                        if (tSeaPlot):                                
                                utils.makeUnit(con.iWorkBoat, iCiv, tSeaPlot, 2)
                                utils.makeUnit(con.iGalley, iCiv, tSeaPlot, 2)
                                pEngland.initUnit(con.iGalley, tSeaPlot[0], tSeaPlot[1], UnitAITypes.UNITAI_SETTLER_SEA, DirectionTypes.DIRECTION_SOUTH)
                if (iCiv == iGermany):                        
                        utils.makeUnit(con.iSettler, iCiv, tPlot, 3)
                        utils.makeUnit(con.iLongbowman, iCiv, tPlot, 3)
                        utils.makeUnit(con.iSwordsman, iCiv, tPlot, 2)
                        utils.makeUnit(con.iAxeman, iCiv, tPlot, 3)
                if (iCiv == iRussia):
                        utils.makeUnit(con.iSettler, iCiv, tPlot, 4)
                        utils.makeUnit(con.iLongbowman, iCiv, tPlot, 2)
                        utils.makeUnit(con.iSwordsman, iCiv, tPlot, 2)
                        utils.makeUnit(con.iHorseArcher, iCiv, tPlot, 3)
                if (iCiv == iHolland):
                        utils.makeUnit(con.iSettler, iCiv, tPlot, 1)
                        utils.makeUnit(con.iCrossbowman, iCiv, tPlot, 3)
                        utils.makeUnit(con.iPikeman, iCiv, tPlot, 3)
                        tSeaPlot = self.findSeaPlots(tPlot, 1)
                        if (tSeaPlot):                                
                                utils.makeUnit(con.iWorkBoat, iCiv, tSeaPlot, 2)
                                utils.makeUnit(con.iGalley, iCiv, tSeaPlot, 1)
                                utils.makeUnit(con.iSettler, iCiv, tPlot, 1)
                                utils.makeUnit(con.iCrossbowman, iCiv, tPlot, 1)
                                pHolland.initUnit(con.iGalley, tSeaPlot[0], tSeaPlot[1], UnitAITypes.UNITAI_SETTLER_SEA, DirectionTypes.DIRECTION_SOUTH)
                if (iCiv == iMali):
                        utils.makeUnit(con.iSettler, iCiv, tPlot, 3)
                        utils.makeUnit(con.iMaliSkirmisher, iCiv, tPlot, 5)
                if (iCiv == iTurkey):
                        utils.makeUnit(con.iSettler, iCiv, tPlot, 3)
                        utils.makeUnit(con.iLongbowman, iCiv, tPlot, 1)
                        utils.makeUnit(con.iCrossbowman, iCiv, tPlot, 3)
                        utils.makeUnit(con.iHorseArcher, iCiv, tPlot, 3)
                        utils.makeUnit(con.iCannon, iCiv, tPlot, 3)
                        utils.makeUnit(con.iTrebuchet, iCiv, tPlot, 3)
                if (iCiv == iPortugal):
                        utils.makeUnit(con.iSettler, iCiv, tPlot, 1)
                        utils.makeUnit(con.iCrossbowman, iCiv, tPlot, 2)
                        utils.makeUnit(con.iPikeman, iCiv, tPlot, 3)
                        tSeaPlot = self.findSeaPlots(tPlot, 1)
                        if (tSeaPlot):                                
                                utils.makeUnit(con.iWorkBoat, iCiv, tSeaPlot, 2)
                                utils.makeUnit(con.iGalley, iCiv, tSeaPlot, 1)
                                utils.makeUnit(con.iSettler, iCiv, tPlot, 1)
                                utils.makeUnit(con.iCrossbowman, iCiv, tPlot, 1)
                                pPortugal.initUnit(con.iGalley, tSeaPlot[0], tSeaPlot[1], UnitAITypes.UNITAI_SETTLER_SEA, DirectionTypes.DIRECTION_SOUTH)
                if (iCiv == iInca):
                        utils.makeUnit(con.iSettler, iCiv, tPlot, 4)
                        utils.makeUnit(con.iScout, iCiv, tPlot, 2)
                        utils.makeUnit(con.iIncanQuechua, iCiv, tPlot, 4)
                        utils.makeUnit(con.iArcher, iCiv, tPlot, 3)
                if (iCiv == iMongolia):
                        utils.makeUnit(con.iSettler, iCiv, tPlot, 5)
                        utils.makeUnit(con.iLongbowman, iCiv, tPlot, 1)
                        utils.makeUnit(con.iCrossbowman, iCiv, tPlot, 2)
                        utils.makeUnit(con.iHorseArcher, iCiv, tPlot, 2) 
                        utils.makeUnit(con.iMongolKeshik, iCiv, tPlot, 6)
                if (iCiv == iAztecs):
                        utils.makeUnit(con.iSettler, iCiv, tPlot, 2)
                        utils.makeUnit(con.iAztecJaguar, iCiv, tPlot, 4)
                        utils.makeUnit(con.iArcher, iCiv, tPlot, 4)
                if (iCiv == iAmerica):
                        utils.makeUnit(con.iSettler, iCiv, tPlot, 5)
                        utils.makeUnit(con.iGrenadier, iCiv, tPlot, 2)
                        utils.makeUnit(con.iRifleman, iCiv, tPlot, 4)
                        utils.makeUnit(con.iCannon, iCiv, tPlot, 2)
                        self.addMissionary(iCiv, (23, 40), (33, 52), tPlot, 1)
                        tSeaPlot = self.findSeaPlots(tPlot, 1)
                        if (tSeaPlot):  
                                utils.makeUnit(con.iWorkBoat, iCiv, tSeaPlot, 2)
                                utils.makeUnit(con.iGalleon, iCiv, tSeaPlot, 2)
                                utils.makeUnit(con.iFrigate, iCiv, tSeaPlot, 1)



        def addMissionary(self, iCiv, tTopLeft, tBottomRight, tPlot, iNumber):
                lReligions = [0, 0, 0, 0, 0, 0, 0]
                for x in range(tTopLeft[0], tBottomRight[0]+1):
                        for y in range(tTopLeft[1], tBottomRight[1]+1):
                                pCurrent = gc.getMap().plot( x, y )
                                if (pCurrent.isCity()):
                                        city = pCurrent.getPlotCity() 
                                        iOwner = city.getOwner()
                                        if (iOwner != iCiv):
                                                iStateReligion = gc.getPlayer(iOwner).getStateReligion()
                                                if (iStateReligion >= 0 and iStateReligion < con.iNumReligions):
                                                        lReligions[iStateReligion] += 1
                iMax = 0
                iWinnerReligion = -1
                for i in range(1, len(lReligions)+1): #so that Christianity comes first
                        iLoopReligion = i % con.iNumReligions
                        if (lReligions[iLoopReligion] > iMax):
                                iMax = lReligions[iLoopReligion]
                                iWinnerReligion = iLoopReligion

                if (iWinnerReligion == -1):
                        for iLoopCiv in range(iNumMajorPlayers):
                                if (iLoopCiv != iCiv):
                                        if (gc.getMap().plot(tPlot[0], tPlot[1]).isRevealed(iLoopCiv, False)):
                                                iStateReligion = gc.getPlayer(iLoopCiv).getStateReligion()
                                                if (iStateReligion >= 0 and iStateReligion < con.iNumReligions):
                                                        lReligions[iStateReligion] += 1

                        for iLoopReligion in range(1, len(lReligions)+1): #so that Christianity comes first
                                iLoopReligion = i % con.iNumReligions
                                if (lReligions[iLoopReligion] > iMax):
                                        iMax = lReligions[iLoopReligion]
                                        iWinnerReligion = iLoopReligion   

                if (iWinnerReligion != -1):
                        utils.makeUnit(con.iJewishMissionary + iWinnerReligion, iCiv, tPlot, iNumber)
                        

                                
        def createStartingWorkers( self, iCiv, tPlot ):
                if (iCiv == iGreece):
                        utils.makeUnit(con.iWorker, iCiv, tPlot, 2)
                if (iCiv == iPersia):
                        utils.makeUnit(con.iWorker, iCiv, tPlot, 2)
                if (iCiv == iCarthage):
                        utils.makeUnit(con.iWorker, iCiv, tPlot, 2)
                if (iCiv == iRome):
                        utils.makeUnit(con.iWorker, iCiv, tPlot, 2)
                if (iCiv == iJapan):
                        utils.makeUnit(con.iWorker, iCiv, tPlot, 2)
                if (iCiv == iEthiopia):
                        utils.makeUnit(con.iWorker, iCiv, tPlot, 3)
                if (iCiv == iMaya):
                        utils.makeUnit(con.iWorker, iCiv, tPlot, 3)
                if (iCiv == iVikings):
                        utils.makeUnit(con.iWorker, iCiv, tPlot, 3)                              
                if (iCiv == iArabia):
                        utils.makeUnit(con.iWorker, iCiv, tPlot, 3)
                if (iCiv == iKhmer):
                        utils.makeUnit(con.iWorker, iCiv, tPlot, 3)                
                if (iCiv == iSpain):
                        utils.makeUnit(con.iWorker, iCiv, tPlot, 3)
                if (iCiv == iFrance):
                        utils.makeUnit(con.iWorker, iCiv, tPlot, 3)
                if (iCiv == iEngland):
                        utils.makeUnit(con.iWorker, iCiv, tPlot, 3)
                if (iCiv == iGermany):                        
                        utils.makeUnit(con.iWorker, iCiv, tPlot, 3)
                if (iCiv == iRussia):
                        utils.makeUnit(con.iWorker, iCiv, tPlot, 3)
                if (iCiv == iNetherlands):
                        utils.makeUnit(con.iWorker, iCiv, tPlot, 3) 
                if (iCiv == iMali):
                        utils.makeUnit(con.iWorker, iCiv, tPlot, 3)
                if (iCiv == iTurkey):
                        utils.makeUnit(con.iWorker, iCiv, tPlot, 4)
                if (iCiv == iPortugal):
                        utils.makeUnit(con.iWorker, iCiv, tPlot, 3) 
                if (iCiv == iInca):
                        utils.makeUnit(con.iWorker, iCiv, tPlot, 4)
                if (iCiv == iMongolia):
                        utils.makeUnit(con.iWorker, iCiv, tPlot, 4)
                if (iCiv == iAztecs):
                        utils.makeUnit(con.iWorker, iCiv, tPlot, 3)
                if (iCiv == iAmerica):
                        utils.makeUnit(con.iWorker, iCiv, tPlot, 4)

        def create600ADstartingUnits( self ):

                utils.makeUnit(iSettler, iChina, tCapitals[iChina], 3)
                utils.makeUnit(con.iSwordsman, iChina, tCapitals[iChina], 2)
                utils.makeUnit(con.iArcher, iChina, tCapitals[iChina], 1)
                utils.makeUnit(con.iChinaChokonu, iChina, tCapitals[iChina], 2)
                utils.makeUnit(con.iHorseArcher, iChina, tCapitals[iChina], 1)
                utils.makeUnit(con.iWorker, iChina, tCapitals[iChina], 2)
                
                utils.makeUnit(iSettler, iJapan, tCapitals[iJapan], 3)
                utils.makeUnit(con.iSwordsman, iJapan, tCapitals[iJapan], 2)
                utils.makeUnit(con.iArcher, iJapan, tCapitals[iJapan], 2)
                utils.makeUnit(con.iWorker, iJapan, tCapitals[iJapan], 2)
                tSeaPlot = self.findSeaPlots(tCapitals[iJapan], 1)
                if (tSeaPlot):                                
                        utils.makeUnit(con.iWorkBoat, iJapan, tSeaPlot, 2)

                utils.makeUnit(con.iSettler, iVikings, tCapitals[iVikings], 3)
                utils.makeUnit(con.iArcher, iVikings, tCapitals[iVikings], 3)
                utils.makeUnit(con.iAxeman, iVikings, tCapitals[iVikings], 1)
                utils.makeUnit(con.iWorker, iVikings, tCapitals[iVikings], 2)
                tSeaPlot = self.findSeaPlots(tCapitals[iVikings], 1)
                if (tSeaPlot):                                
                        utils.makeUnit(con.iWorkBoat, iVikings, tSeaPlot, 1)
                        pVikings.initUnit(con.iGalley, tSeaPlot[0], tSeaPlot[1], UnitAITypes.UNITAI_ASSAULT_SEA, DirectionTypes.DIRECTION_SOUTH)
                        utils.makeUnit(con.iAxeman, iVikings, tSeaPlot, 2)
                        pVikings.initUnit(con.iGalley, tSeaPlot[0], tSeaPlot[1], UnitAITypes.UNITAI_SETTLER_SEA, DirectionTypes.DIRECTION_SOUTH)                                

                utils.makeUnit(con.iSettler, iArabia, tCapitals[iArabia], 3)
                utils.makeUnit(con.iLongbowman, iArabia, tCapitals[iArabia], 4)
                utils.makeUnit(con.iSwordsman, iArabia, tCapitals[iArabia], 2)
                utils.makeUnit(con.iArabiaCamelarcher, iArabia, tCapitals[iArabia], 5)
                utils.makeUnit(con.iWorker, iArabia, tCapitals[iArabia], 2)

                if ( pKhmer.isHuman() ):
                    utils.makeUnit(iSettler, iKhmer, tCapitals[iKhmer], 1)
                    utils.makeUnit(iWarrior, iKhmer, tCapitals[iKhmer], 1)
                if ( pSpain.isHuman() ):
                    utils.makeUnit(iSettler, iSpain, tCapitals[iSpain], 1)
                    utils.makeUnit(iWarrior, iSpain, tCapitals[iSpain], 1)
                if ( pFrance.isHuman() ):
                    utils.makeUnit(iSettler, iFrance, tCapitals[iFrance], 1)
                    utils.makeUnit(iWarrior, iFrance, tCapitals[iFrance], 1)
                if ( pEngland.isHuman() ):
                    utils.makeUnit(iSettler, iEngland, tCapitals[iEngland], 1)
                    utils.makeUnit(iWarrior, iEngland, tCapitals[iEngland], 1)
                if ( pGermany.isHuman() ):
                    utils.makeUnit(iSettler, iGermany, tCapitals[iGermany], 1)
                    utils.makeUnit(iScout, iGermany, tCapitals[iGermany], 1)
                if ( pRussia.isHuman() ):
                    utils.makeUnit(iSettler, iRussia, tCapitals[iRussia], 1)
                    utils.makeUnit(iScout, iRussia, tCapitals[iRussia], 1)
                if ( pNetherlands.isHuman() ):
                    utils.makeUnit(iSettler, iNetherlands, tCapitals[iNetherlands], 1)
                    utils.makeUnit(iWarrior, iNetherlands, tCapitals[iNetherlands], 1)
                if ( pMali.isHuman() ):
                    utils.makeUnit(iSettler, iMali, tCapitals[iMali], 1)
                    utils.makeUnit(iWarrior, iMali, tCapitals[iMali], 1)
                if ( pTurkey.isHuman() ):
                    utils.makeUnit(iSettler, iTurkey, tCapitals[iTurkey], 1)
                    utils.makeUnit(iWarrior, iTurkey, tCapitals[iTurkey], 1)
                if ( pPortugal.isHuman() ):
                    utils.makeUnit(iSettler, iPortugal, tCapitals[iPortugal], 1)
                    utils.makeUnit(iWarrior, iPortugal, tCapitals[iPortugal], 1)
                if ( pInca.isHuman() ):
                    utils.makeUnit(iSettler, iInca, tCapitals[iInca], 1)
                    utils.makeUnit(iWarrior, iInca, tCapitals[iInca], 1)
                if ( pMongolia.isHuman() ):
                    utils.makeUnit(iSettler, iMongolia, tCapitals[iMongolia], 1)
                    utils.makeUnit(iScout, iMongolia, tCapitals[iMongolia], 1)
                if ( pAztecs.isHuman() ):
                    utils.makeUnit(iSettler, iAztecs, tCapitals[iAztecs], 1)
                    utils.makeUnit(iScout, iAztecs, tCapitals[iAztecs], 1)
                if ( pAmerica.isHuman() ):
                    utils.makeUnit(iSettler, iAmerica, tCapitals[iAmerica], 1)
                    utils.makeUnit(iWarrior, iAmerica, tCapitals[iAmerica], 1)


        def create4000BCstartingUnits( self ):

                utils.makeUnit(iSettler, iEgypt, tCapitals[iEgypt], 1)
                utils.makeUnit(iWarrior, iEgypt, tCapitals[iEgypt], 1)

                utils.makeUnit(iSettler, iIndia, tCapitals[iIndia], 1)
                utils.makeUnit(iWarrior, iIndia, tCapitals[iIndia], 1)

                utils.makeUnit(iSettler, iChina, tCapitals[iChina], 1)
                utils.makeUnit(iWarrior, iChina, tCapitals[iChina], 1)

                utils.makeUnit(iSettler, iBabylonia, tCapitals[iBabylonia], 1)
                utils.makeUnit(iWarrior, iBabylonia, tCapitals[iBabylonia], 1)

                if ( pGreece.isHuman() ):
                    utils.makeUnit(iSettler, iGreece, tCapitals[iGreece], 1)
                    utils.makeUnit(iScout, iGreece, tCapitals[iGreece], 1)
                if ( pPersia.isHuman() ):
                    utils.makeUnit(iSettler, iPersia, tCapitals[iPersia], 1)
                    utils.makeUnit(iScout, iPersia, tCapitals[iPersia], 1)
                if ( pCarthage.isHuman() ):
                    utils.makeUnit(iSettler, iCarthage, tCapitals[iCarthage], 1)
                    utils.makeUnit(iScout, iCarthage, tCapitals[iCarthage], 1)
                if ( pRome.isHuman() ):
                    utils.makeUnit(iSettler, iRome, tCapitals[iRome], 1)
                    utils.makeUnit(iWarrior, iRome, tCapitals[iRome], 1)
                if ( pJapan.isHuman() ):
                    utils.makeUnit(iSettler, iJapan, tCapitals[iJapan], 1)
                    utils.makeUnit(iWarrior, iJapan, tCapitals[iJapan], 1)
                if ( pEthiopia.isHuman() ):
                    utils.makeUnit(iSettler, iEthiopia, tCapitals[iEthiopia], 1)
                    utils.makeUnit(iWarrior, iEthiopia, tCapitals[iEthiopia], 1)
                if ( pMaya.isHuman() ):
                    utils.makeUnit(iSettler, iMaya, tCapitals[iMaya], 1)
                    utils.makeUnit(iWarrior, iMaya, tCapitals[iMaya], 1)
                if ( pVikings.isHuman() ):
                    utils.makeUnit(iSettler, iVikings, tCapitals[iVikings], 1)
                    utils.makeUnit(iScout, iVikings, tCapitals[iVikings], 1)
                if ( pArabia.isHuman() ):
                    utils.makeUnit(con.iSettler, iArabia, tCapitals[iArabia], 1)
                    utils.makeUnit(con.iWarrior, iArabia, tCapitals[iArabia], 1)
                if ( pKhmer.isHuman() ):
                    utils.makeUnit(iSettler, iKhmer, tCapitals[iKhmer], 1)
                    utils.makeUnit(iWarrior, iKhmer, tCapitals[iKhmer], 1)
                if ( pSpain.isHuman() ):
                    utils.makeUnit(iSettler, iSpain, tCapitals[iSpain], 1)
                    utils.makeUnit(iWarrior, iSpain, tCapitals[iSpain], 1)
                if ( pFrance.isHuman() ):
                    utils.makeUnit(iSettler, iFrance, tCapitals[iFrance], 1)
                    utils.makeUnit(iWarrior, iFrance, tCapitals[iFrance], 1)
                if ( pEngland.isHuman() ):
                    utils.makeUnit(iSettler, iEngland, tCapitals[iEngland], 1)
                    utils.makeUnit(iWarrior, iEngland, tCapitals[iEngland], 1)
                if ( pGermany.isHuman() ):
                    utils.makeUnit(iSettler, iGermany, tCapitals[iGermany], 1)
                    utils.makeUnit(iScout, iGermany, tCapitals[iGermany], 1)
                if ( pRussia.isHuman() ):
                    utils.makeUnit(iSettler, iRussia, tCapitals[iRussia], 1)
                    utils.makeUnit(iScout, iRussia, tCapitals[iRussia], 1)
                if ( pNetherlands.isHuman() ):
                    utils.makeUnit(iSettler, iNetherlands, tCapitals[iNetherlands], 1)
                    utils.makeUnit(iWarrior, iNetherlands, tCapitals[iNetherlands], 1)
                if ( pMali.isHuman() ):
                    utils.makeUnit(iSettler, iMali, tCapitals[iMali], 1)
                    utils.makeUnit(iWarrior, iMali, tCapitals[iMali], 1)
                if ( pTurkey.isHuman() ):
                    utils.makeUnit(iSettler, iTurkey, tCapitals[iTurkey], 1)
                    utils.makeUnit(iWarrior, iTurkey, tCapitals[iTurkey], 1)
                if ( pPortugal.isHuman() ):
                    utils.makeUnit(iSettler, iPortugal, tCapitals[iPortugal], 1)
                    utils.makeUnit(iWarrior, iPortugal, tCapitals[iPortugal], 1)
                if ( pInca.isHuman() ):
                    utils.makeUnit(iSettler, iInca, tCapitals[iInca], 1)
                    utils.makeUnit(iWarrior, iInca, tCapitals[iInca], 1)
                if ( pMongolia.isHuman() ):
                    utils.makeUnit(iSettler, iMongolia, tCapitals[iMongolia], 1)
                    utils.makeUnit(iScout, iMongolia, tCapitals[iMongolia], 1)
                if ( pAztecs.isHuman() ):
                    utils.makeUnit(iSettler, iAztecs, tCapitals[iAztecs], 1)
                    utils.makeUnit(iScout, iAztecs, tCapitals[iAztecs], 1)
                if ( pAmerica.isHuman() ):
                    utils.makeUnit(iSettler, iAmerica, tCapitals[iAmerica], 1)
                    utils.makeUnit(iWarrior, iAmerica, tCapitals[iAmerica], 1)



        def assign600ADTechs( self ):
            
                iCiv = iChina
                teamChina.setHasTech(con.iMining, True, iCiv, False, False)
                teamChina.setHasTech(con.iBronzeWorking, True, iCiv, False, False)
                teamChina.setHasTech(con.iIronWorking, True, iCiv, False, False)
                teamChina.setHasTech(con.iMetalCasting, True, iCiv, False, False)
                teamChina.setHasTech(con.iMachinery, True, iCiv, False, False)
                teamChina.setHasTech(con.iMysticism, True, iCiv, False, False)
                teamChina.setHasTech(con.iPolytheism, True, iCiv, False, False)
                teamChina.setHasTech(con.iMeditation, True, iCiv, False, False)
                teamChina.setHasTech(con.iPriesthood, True, iCiv, False, False)
                teamChina.setHasTech(con.iMasonry, True, iCiv, False, False)
                teamChina.setHasTech(con.iMonarchy, True, iCiv, False, False)
                teamChina.setHasTech(con.iFishing, True, iCiv, False, False)
                teamChina.setHasTech(con.iSailing, True, iCiv, False, False)
                teamChina.setHasTech(con.iTheWheel, True, iCiv, False, False)
                teamChina.setHasTech(con.iPottery, True, iCiv, False, False)
                teamChina.setHasTech(con.iAgriculture, True, iCiv, False, False)
                teamChina.setHasTech(con.iWriting, True, iCiv, False, False)
                teamChina.setHasTech(con.iMathematics, True, iCiv, False, False)
                teamChina.setHasTech(con.iCalendar, True, iCiv, False, False)
                teamChina.setHasTech(con.iConstruction, True, iCiv, False, False)
                teamChina.setHasTech(con.iCurrency, True, iCiv, False, False)
                teamChina.setHasTech(con.iCodeOfLaws, True, iCiv, False, False)
                teamChina.setHasTech(con.iCivilService, True, iCiv, False, False)
                teamChina.setHasTech(con.iFeudalism, True, iCiv, False, False)
                teamChina.setHasTech(con.iHunting, True, iCiv, False, False)
                teamChina.setHasTech(con.iArchery, True, iCiv, False, False)
                teamChina.setHasTech(con.iAnimalHusbandry, True, iCiv, False, False)
                teamChina.setHasTech(con.iHorsebackRiding, True, iCiv, False, False)
                teamChina.setHasTech(con.iAesthetics, True, iCiv, False, False)
                teamChina.setHasTech(con.iDrama, True, iCiv, False, False)
                teamChina.setHasTech(con.iMusic, True, iCiv, False, False)
                iCiv = iJapan
                teamJapan.setHasTech(con.iMining, True, iCiv, False, False)
                teamJapan.setHasTech(con.iBronzeWorking, True, iCiv, False, False)
                teamJapan.setHasTech(con.iIronWorking, True, iCiv, False, False)
                teamJapan.setHasTech(con.iMetalCasting, True, iCiv, False, False)
                teamJapan.setHasTech(con.iMachinery, True, iCiv, False, False)
                teamJapan.setHasTech(con.iMysticism, True, iCiv, False, False)
                teamJapan.setHasTech(con.iPolytheism, True, iCiv, False, False)
                teamJapan.setHasTech(con.iMeditation, True, iCiv, False, False)
                teamJapan.setHasTech(con.iPriesthood, True, iCiv, False, False)
                teamJapan.setHasTech(con.iMasonry, True, iCiv, False, False)
                teamJapan.setHasTech(con.iMonarchy, True, iCiv, False, False)
                teamJapan.setHasTech(con.iFishing, True, iCiv, False, False)
                teamJapan.setHasTech(con.iSailing, True, iCiv, False, False)
                teamJapan.setHasTech(con.iTheWheel, True, iCiv, False, False)
                teamJapan.setHasTech(con.iPottery, True, iCiv, False, False)
                teamJapan.setHasTech(con.iAgriculture, True, iCiv, False, False)
                teamJapan.setHasTech(con.iWriting, True, iCiv, False, False)
                teamJapan.setHasTech(con.iMathematics, True, iCiv, False, False)
                #teamJapan.setHasTech(con.iCalendar, True, iCiv, False, False)
                teamJapan.setHasTech(con.iConstruction, True, iCiv, False, False)
                teamJapan.setHasTech(con.iCurrency, True, iCiv, False, False)
                teamJapan.setHasTech(con.iCodeOfLaws, True, iCiv, False, False)
                teamJapan.setHasTech(con.iCivilService, True, iCiv, False, False)
                teamJapan.setHasTech(con.iFeudalism, True, iCiv, False, False)
                teamJapan.setHasTech(con.iHunting, True, iCiv, False, False)
                teamJapan.setHasTech(con.iArchery, True, iCiv, False, False)
                teamJapan.setHasTech(con.iAnimalHusbandry, True, iCiv, False, False)
                teamJapan.setHasTech(con.iAesthetics, True, iCiv, False, False)
                iCiv = iVikings
                teamVikings.setHasTech(con.iMining, True, iCiv, False, False)
                teamVikings.setHasTech(con.iBronzeWorking, True, iCiv, False, False)
                teamVikings.setHasTech(con.iIronWorking, True, iCiv, False, False)
                teamVikings.setHasTech(con.iMetalCasting, True, iCiv, False, False)
                teamVikings.setHasTech(con.iMachinery, True, iCiv, False, False)
                teamVikings.setHasTech(con.iMysticism, True, iCiv, False, False)
                teamVikings.setHasTech(con.iPolytheism, True, iCiv, False, False)
                teamVikings.setHasTech(con.iMasonry, True, iCiv, False, False)
                teamVikings.setHasTech(con.iPriesthood, True, iCiv, False, False)
                teamVikings.setHasTech(con.iMonarchy, True, iCiv, False, False)
                teamVikings.setHasTech(con.iFishing, True, iCiv, False, False)
                teamVikings.setHasTech(con.iSailing, True, iCiv, False, False)
                teamVikings.setHasTech(con.iTheWheel, True, iCiv, False, False)
                teamVikings.setHasTech(con.iPottery, True, iCiv, False, False)
                teamVikings.setHasTech(con.iAgriculture, True, iCiv, False, False)
                teamVikings.setHasTech(con.iWriting, True, iCiv, False, False)
                teamVikings.setHasTech(con.iCodeOfLaws, True, iCiv, False, False)
                teamVikings.setHasTech(con.iFeudalism, True, iCiv, False, False)
                teamVikings.setHasTech(con.iAlphabet, True, iCiv, False, False)
                teamVikings.setHasTech(con.iMathematics, True, iCiv, False, False)
                teamVikings.setHasTech(con.iConstruction, True, iCiv, False, False)
                teamVikings.setHasTech(con.iCurrency, True, iCiv, False, False)
                teamVikings.setHasTech(con.iHunting, True, iCiv, False, False)
                teamVikings.setHasTech(con.iArchery, True, iCiv, False, False)
                teamVikings.setHasTech(con.iAnimalHusbandry, True, iCiv, False, False)
                iCiv = iArabia
                teamArabia.setHasTech(con.iMining, True, iCiv, False, False)
                teamArabia.setHasTech(con.iBronzeWorking, True, iCiv, False, False)
                teamArabia.setHasTech(con.iIronWorking, True, iCiv, False, False)
                teamArabia.setHasTech(con.iMetalCasting, True, iCiv, False, False)
                teamArabia.setHasTech(con.iMachinery, True, iCiv, False, False)
                teamArabia.setHasTech(con.iMysticism, True, iCiv, False, False)
                teamArabia.setHasTech(con.iPolytheism, True, iCiv, False, False)
                teamArabia.setHasTech(con.iMasonry, True, iCiv, False, False)
                teamArabia.setHasTech(con.iPriesthood, True, iCiv, False, False)
                teamArabia.setHasTech(con.iMonotheism, True, iCiv, False, False)
                teamArabia.setHasTech(con.iTheology, True, iCiv, False, False)
                teamArabia.setHasTech(con.iMonarchy, True, iCiv, False, False)
                teamArabia.setHasTech(con.iDivineRight, True, iCiv, False, False)
                teamArabia.setHasTech(con.iFishing, True, iCiv, False, False)
                teamArabia.setHasTech(con.iSailing, True, iCiv, False, False)
                teamArabia.setHasTech(con.iTheWheel, True, iCiv, False, False)
                teamArabia.setHasTech(con.iPottery, True, iCiv, False, False)
                teamArabia.setHasTech(con.iAgriculture, True, iCiv, False, False)
                teamArabia.setHasTech(con.iWriting, True, iCiv, False, False)
                teamArabia.setHasTech(con.iCodeOfLaws, True, iCiv, False, False)
                teamArabia.setHasTech(con.iFeudalism, True, iCiv, False, False)
                teamArabia.setHasTech(con.iGuilds, True, iCiv, False, False)
                teamArabia.setHasTech(con.iAlphabet, True, iCiv, False, False)
                teamArabia.setHasTech(con.iMathematics, True, iCiv, False, False)
                teamArabia.setHasTech(con.iConstruction, True, iCiv, False, False)
                teamArabia.setHasTech(con.iCurrency, True, iCiv, False, False)
                teamArabia.setHasTech(con.iHunting, True, iCiv, False, False)
                teamArabia.setHasTech(con.iArchery, True, iCiv, False, False)
                teamArabia.setHasTech(con.iAnimalHusbandry, True, iCiv, False, False)
                teamArabia.setHasTech(con.iHorsebackRiding, True, iCiv, False, False)
                iCiv = iIndependent
                teamIndependent.setHasTech(con.iMining, True, iCiv, False, False)
                teamIndependent.setHasTech(con.iBronzeWorking, True, iCiv, False, False)
                teamIndependent.setHasTech(con.iIronWorking, True, iCiv, False, False)
                teamIndependent.setHasTech(con.iMetalCasting, True, iCiv, False, False)
                teamIndependent.setHasTech(con.iMachinery, True, iCiv, False, False)
                teamIndependent.setHasTech(con.iMysticism, True, iCiv, False, False)
                teamIndependent.setHasTech(con.iPolytheism, True, iCiv, False, False)
                teamIndependent.setHasTech(con.iMeditation, True, iCiv, False, False)
                teamIndependent.setHasTech(con.iMasonry, True, iCiv, False, False)
                teamIndependent.setHasTech(con.iPriesthood, True, iCiv, False, False)
                teamIndependent.setHasTech(con.iMonarchy, True, iCiv, False, False)
                teamIndependent.setHasTech(con.iFishing, True, iCiv, False, False)
                teamIndependent.setHasTech(con.iSailing, True, iCiv, False, False)
                teamIndependent.setHasTech(con.iTheWheel, True, iCiv, False, False)
                teamIndependent.setHasTech(con.iPottery, True, iCiv, False, False)
                teamIndependent.setHasTech(con.iAgriculture, True, iCiv, False, False)
                teamIndependent.setHasTech(con.iWriting, True, iCiv, False, False)
                teamIndependent.setHasTech(con.iCodeOfLaws, True, iCiv, False, False)
                #teamIndependent.setHasTech(con.iFeudalism, True, iCiv, False, False)
                teamIndependent.setHasTech(con.iAlphabet, True, iCiv, False, False)
                teamIndependent.setHasTech(con.iMathematics, True, iCiv, False, False)
                teamIndependent.setHasTech(con.iCurrency, True, iCiv, False, False)
                teamIndependent.setHasTech(con.iHunting, True, iCiv, False, False)
                teamIndependent.setHasTech(con.iArchery, True, iCiv, False, False)
                teamIndependent.setHasTech(con.iAnimalHusbandry, True, iCiv, False, False)
                iCiv = iIndependent2
                teamIndependent2.setHasTech(con.iMining, True, iCiv, False, False)
                teamIndependent2.setHasTech(con.iBronzeWorking, True, iCiv, False, False)
                teamIndependent2.setHasTech(con.iIronWorking, True, iCiv, False, False)
                teamIndependent2.setHasTech(con.iMetalCasting, True, iCiv, False, False)
                teamIndependent2.setHasTech(con.iMachinery, True, iCiv, False, False)
                teamIndependent2.setHasTech(con.iMysticism, True, iCiv, False, False)
                teamIndependent2.setHasTech(con.iPolytheism, True, iCiv, False, False)
                teamIndependent2.setHasTech(con.iMeditation, True, iCiv, False, False)
                teamIndependent2.setHasTech(con.iMasonry, True, iCiv, False, False)
                teamIndependent2.setHasTech(con.iPriesthood, True, iCiv, False, False)
                teamIndependent2.setHasTech(con.iMonarchy, True, iCiv, False, False)
                teamIndependent2.setHasTech(con.iFishing, True, iCiv, False, False)
                teamIndependent2.setHasTech(con.iSailing, True, iCiv, False, False)
                teamIndependent2.setHasTech(con.iTheWheel, True, iCiv, False, False)
                teamIndependent2.setHasTech(con.iPottery, True, iCiv, False, False)
                teamIndependent2.setHasTech(con.iAgriculture, True, iCiv, False, False)
                teamIndependent2.setHasTech(con.iWriting, True, iCiv, False, False)
                teamIndependent2.setHasTech(con.iCodeOfLaws, True, iCiv, False, False)
                #teamIndependent2.setHasTech(con.iFeudalism, True, iCiv, False, False)
                teamIndependent2.setHasTech(con.iAlphabet, True, iCiv, False, False)
                teamIndependent2.setHasTech(con.iMathematics, True, iCiv, False, False)
                teamIndependent2.setHasTech(con.iCurrency, True, iCiv, False, False)
                teamIndependent2.setHasTech(con.iHunting, True, iCiv, False, False)
                teamIndependent2.setHasTech(con.iArchery, True, iCiv, False, False)
                teamIndependent2.setHasTech(con.iAnimalHusbandry, True, iCiv, False, False)
                iCiv = iNative
                teamNative.setHasTech(con.iHunting, True, iCiv, False, False)
                teamNative.setHasTech(con.iArchery, True, iCiv, False, False)
                iCiv = iCeltia #Byzantium
                teamCeltia.setHasTech(con.iMining, True, iCiv, False, False)
                teamCeltia.setHasTech(con.iBronzeWorking, True, iCiv, False, False)
                teamCeltia.setHasTech(con.iIronWorking, True, iCiv, False, False)
                teamCeltia.setHasTech(con.iMetalCasting, True, iCiv, False, False)
                teamCeltia.setHasTech(con.iMachinery, True, iCiv, False, False)
                teamCeltia.setHasTech(con.iMysticism, True, iCiv, False, False)
                teamCeltia.setHasTech(con.iPolytheism, True, iCiv, False, False)
                teamCeltia.setHasTech(con.iMasonry, True, iCiv, False, False)
                teamCeltia.setHasTech(con.iPriesthood, True, iCiv, False, False)
                teamCeltia.setHasTech(con.iMonotheism, True, iCiv, False, False)
                teamCeltia.setHasTech(con.iTheology, True, iCiv, False, False)
                teamCeltia.setHasTech(con.iMonarchy, True, iCiv, False, False)
                #teamCeltia.setHasTech(con.iDivineRight, True, iCiv, False, False)
                teamCeltia.setHasTech(con.iFishing, True, iCiv, False, False)
                teamCeltia.setHasTech(con.iSailing, True, iCiv, False, False)
                teamCeltia.setHasTech(con.iTheWheel, True, iCiv, False, False)
                teamCeltia.setHasTech(con.iPottery, True, iCiv, False, False)
                teamCeltia.setHasTech(con.iAgriculture, True, iCiv, False, False)
                teamCeltia.setHasTech(con.iWriting, True, iCiv, False, False)
                teamCeltia.setHasTech(con.iCodeOfLaws, True, iCiv, False, False)
                teamCeltia.setHasTech(con.iFeudalism, True, iCiv, False, False)
                #teamCeltia.setHasTech(con.iGuilds, True, iCiv, False, False)
                teamCeltia.setHasTech(con.iAlphabet, True, iCiv, False, False)
                teamCeltia.setHasTech(con.iMathematics, True, iCiv, False, False)
                teamCeltia.setHasTech(con.iConstruction, True, iCiv, False, False)
                teamCeltia.setHasTech(con.iCurrency, True, iCiv, False, False)
                teamCeltia.setHasTech(con.iHunting, True, iCiv, False, False)
                teamCeltia.setHasTech(con.iArchery, True, iCiv, False, False)
                teamCeltia.setHasTech(con.iAnimalHusbandry, True, iCiv, False, False)
                teamCeltia.setHasTech(con.iHorsebackRiding, True, iCiv, False, False)
                teamCeltia.setHasTech(con.iLiterature, True, iCiv, False, False)
                teamCeltia.setHasTech(con.iDrama, True, iCiv, False, False)
                teamCeltia.setHasTech(con.iAesthetics, True, iCiv, False, False)
                teamCeltia.setHasTech(con.iEngineering, True, iCiv, False, False)
                teamCeltia.setHasTech(con.iMusic, True, iCiv, False, False)
                #teamCeltia.setHasTech(con.iPhilosophy, True, iCiv, False, False)
                teamCeltia.setHasTech(con.iCalendar, True, iCiv, False, False)
                
                
        def assignTechs( self, iCiv ):
                #popup = Popup.PyPopup()
                #popup.setBodyString( 'assigning techs to civ #%d' %(iCiv))
                #popup.launch()
                
                if (iCiv == iGreece):
                        teamGreece.setHasTech(con.iMining, True, iCiv, False, False)
                        teamGreece.setHasTech(con.iBronzeWorking, True, iCiv, False, False)
                        teamGreece.setHasTech(con.iMetalCasting, True, iCiv, False, False)
                        teamGreece.setHasTech(con.iMysticism, True, iCiv, False, False)
                        teamGreece.setHasTech(con.iPolytheism, True, iCiv, False, False)
                        teamGreece.setHasTech(con.iFishing, True, iCiv, False, False)
                        teamGreece.setHasTech(con.iSailing, True, iCiv, False, False)
                        teamGreece.setHasTech(con.iTheWheel, True, iCiv, False, False)
                        teamGreece.setHasTech(con.iPottery, True, iCiv, False, False)
                        teamGreece.setHasTech(con.iWriting, True, iCiv, False, False)
                        #teamGreece.setHasTech(con.iAlphabet, True, iCiv, False, False)
                        #teamGreece.setHasTech(con.iLiterature, True, iCiv, False, False)
                        teamGreece.setHasTech(con.iHunting, True, iCiv, False, False)
                if (iCiv == iPersia):
                        teamPersia.setHasTech(con.iMining, True, iCiv, False, False)
                        teamPersia.setHasTech(con.iBronzeWorking, True, iCiv, False, False)
                        #teamPersia.setHasTech(con.iMetalCasting, True, iCiv, False, False)
                        teamPersia.setHasTech(con.iMysticism, True, iCiv, False, False)
                        teamPersia.setHasTech(con.iPolytheism, True, iCiv, False, False)
                        teamPersia.setHasTech(con.iPriesthood, True, iCiv, False, False)
                        teamPersia.setHasTech(con.iMasonry, True, iCiv, False, False)
                        teamPersia.setHasTech(con.iFishing, True, iCiv, False, False)
                        teamPersia.setHasTech(con.iSailing, True, iCiv, False, False)
                        teamPersia.setHasTech(con.iMonotheism, True, iCiv, False, False)
                        teamPersia.setHasTech(con.iMonarchy, True, iCiv, False, False)
                        teamPersia.setHasTech(con.iTheWheel, True, iCiv, False, False)
                        teamPersia.setHasTech(con.iPottery, True, iCiv, False, False)
                        teamPersia.setHasTech(con.iWriting, True, iCiv, False, False)
                        teamPersia.setHasTech(con.iHunting, True, iCiv, False, False)
                        teamPersia.setHasTech(con.iArchery, True, iCiv, False, False)
                        teamPersia.setHasTech(con.iAnimalHusbandry, True, iCiv, False, False)
                        teamPersia.setHasTech(con.iHorsebackRiding, True, iCiv, False, False)
                if (iCiv == iCarthage):
                        teamCarthage.setHasTech(con.iMining, True, iCiv, False, False)
                        teamCarthage.setHasTech(con.iBronzeWorking, True, iCiv, False, False)
                        teamCarthage.setHasTech(con.iMetalCasting, True, iCiv, False, False)
                        teamCarthage.setHasTech(con.iMysticism, True, iCiv, False, False)
                        teamCarthage.setHasTech(con.iPolytheism, True, iCiv, False, False)
                        teamCarthage.setHasTech(con.iPriesthood, True, iCiv, False, False)
                        teamCarthage.setHasTech(con.iMasonry, True, iCiv, False, False)
                        teamCarthage.setHasTech(con.iFishing, True, iCiv, False, False)
                        teamCarthage.setHasTech(con.iSailing, True, iCiv, False, False)
                        #teamCarthage.setHasTech(con.iMonarchy, True, iCiv, False, False)
                        teamCarthage.setHasTech(con.iTheWheel, True, iCiv, False, False)
                        teamCarthage.setHasTech(con.iPottery, True, iCiv, False, False)
                        teamCarthage.setHasTech(con.iWriting, True, iCiv, False, False)
                        teamCarthage.setHasTech(con.iAlphabet, True, iCiv, False, False)
                        teamCarthage.setHasTech(con.iHunting, True, iCiv, False, False)
                        teamCarthage.setHasTech(con.iArchery, True, iCiv, False, False)
                        teamCarthage.setHasTech(con.iAnimalHusbandry, True, iCiv, False, False)
                        teamCarthage.setHasTech(con.iHorsebackRiding, True, iCiv, False, False)
                if (iCiv == iRome):
                        teamRome.setHasTech(con.iMining, True, iCiv, False, False)
                        teamRome.setHasTech(con.iBronzeWorking, True, iCiv, False, False)
                        teamRome.setHasTech(con.iIronWorking, True, iCiv, False, False)
                        teamRome.setHasTech(con.iMetalCasting, True, iCiv, False, False)
                        teamRome.setHasTech(con.iMysticism, True, iCiv, False, False)
                        teamRome.setHasTech(con.iPolytheism, True, iCiv, False, False)
                        teamRome.setHasTech(con.iPriesthood, True, iCiv, False, False)
                        teamRome.setHasTech(con.iMasonry, True, iCiv, False, False)
                        teamRome.setHasTech(con.iFishing, True, iCiv, False, False)
                        teamRome.setHasTech(con.iSailing, True, iCiv, False, False)
                        teamRome.setHasTech(con.iTheWheel, True, iCiv, False, False)
                        teamRome.setHasTech(con.iPottery, True, iCiv, False, False)
                        teamRome.setHasTech(con.iWriting, True, iCiv, False, False)
                        #teamRome.setHasTech(con.iCodeOfLaws, True, iCiv, False, False) founds Confucianism
                        teamRome.setHasTech(con.iAlphabet, True, iCiv, False, False)
                        teamRome.setHasTech(con.iHunting, True, iCiv, False, False)
                        teamRome.setHasTech(con.iAnimalHusbandry, True, iCiv, False, False)
                if (iCiv == iJapan):
                        teamJapan.setHasTech(con.iMining, True, iCiv, False, False)
                        teamJapan.setHasTech(con.iBronzeWorking, True, iCiv, False, False)
                        teamJapan.setHasTech(con.iMetalCasting, True, iCiv, False, False)
                        teamJapan.setHasTech(con.iMysticism, True, iCiv, False, False)
                        teamJapan.setHasTech(con.iPolytheism, True, iCiv, False, False)
                        teamJapan.setHasTech(con.iMeditation, True, iCiv, False, False)
                        teamJapan.setHasTech(con.iPriesthood, True, iCiv, False, False)
                        teamJapan.setHasTech(con.iMasonry, True, iCiv, False, False)
                        teamJapan.setHasTech(con.iMonarchy, True, iCiv, False, False)
                        teamJapan.setHasTech(con.iFishing, True, iCiv, False, False)
                        teamJapan.setHasTech(con.iTheWheel, True, iCiv, False, False)
                        teamJapan.setHasTech(con.iPottery, True, iCiv, False, False)
                        teamJapan.setHasTech(con.iAgriculture, True, iCiv, False, False)
                        teamJapan.setHasTech(con.iWriting, True, iCiv, False, False)
                if (iCiv == iEthiopia):
                        teamEthiopia.setHasTech(con.iMining, True, iCiv, False, False)
                        teamEthiopia.setHasTech(con.iBronzeWorking, True, iCiv, False, False)
                        teamEthiopia.setHasTech(con.iMysticism, True, iCiv, False, False)
                        teamEthiopia.setHasTech(con.iPolytheism, True, iCiv, False, False)
                        teamEthiopia.setHasTech(con.iMeditation, True, iCiv, False, False)
                        teamEthiopia.setHasTech(con.iPriesthood, True, iCiv, False, False)
                        teamEthiopia.setHasTech(con.iMonotheism, True, iCiv, False, False) #
                        teamEthiopia.setHasTech(con.iMasonry, True, iCiv, False, False)
                        teamEthiopia.setHasTech(con.iFishing, True, iCiv, False, False)
                        teamEthiopia.setHasTech(con.iSailing, True, iCiv, False, False)
                        teamEthiopia.setHasTech(con.iMonarchy, True, iCiv, False, False)
                        teamEthiopia.setHasTech(con.iTheWheel, True, iCiv, False, False)
                        teamEthiopia.setHasTech(con.iPottery, True, iCiv, False, False)
                        teamEthiopia.setHasTech(con.iWriting, True, iCiv, False, False)
                        teamEthiopia.setHasTech(con.iHunting, True, iCiv, False, False)
                        teamEthiopia.setHasTech(con.iArchery, True, iCiv, False, False)
                        teamEthiopia.setHasTech(con.iAnimalHusbandry, True, iCiv, False, False)
                        teamEthiopia.setHasTech(con.iHorsebackRiding, True, iCiv, False, False)
                if (iCiv == iMaya):
                        teamMaya.setHasTech(con.iMining, True, iCiv, False, False)
                        teamMaya.setHasTech(con.iMysticism, True, iCiv, False, False)
                        teamMaya.setHasTech(con.iPolytheism, True, iCiv, False, False)
                        teamMaya.setHasTech(con.iMeditation, True, iCiv, False, False)
                        teamMaya.setHasTech(con.iPriesthood, True, iCiv, False, False)
                        teamMaya.setHasTech(con.iMasonry, True, iCiv, False, False)
                        #teamMaya.setHasTech(con.iMonarchy, True, iCiv, False, False)
                        teamMaya.setHasTech(con.iFishing, True, iCiv, False, False)
                        teamMaya.setHasTech(con.iTheWheel, True, iCiv, False, False)
                        teamMaya.setHasTech(con.iPottery, True, iCiv, False, False)
                        teamMaya.setHasTech(con.iAgriculture, True, iCiv, False, False)
                        teamMaya.setHasTech(con.iWriting, True, iCiv, False, False)
                        teamMaya.setHasTech(con.iHunting, True, iCiv, False, False)
                if (iCiv == iVikings):
                        teamVikings.setHasTech(con.iMining, True, iCiv, False, False)
                        teamVikings.setHasTech(con.iBronzeWorking, True, iCiv, False, False)
                        teamVikings.setHasTech(con.iIronWorking, True, iCiv, False, False)
                        teamVikings.setHasTech(con.iMetalCasting, True, iCiv, False, False)
                        teamVikings.setHasTech(con.iMachinery, True, iCiv, False, False)
                        teamVikings.setHasTech(con.iMysticism, True, iCiv, False, False)
                        teamVikings.setHasTech(con.iPolytheism, True, iCiv, False, False)
                        teamVikings.setHasTech(con.iMasonry, True, iCiv, False, False)
                        teamVikings.setHasTech(con.iPriesthood, True, iCiv, False, False)
                        teamVikings.setHasTech(con.iMonarchy, True, iCiv, False, False)
                        teamVikings.setHasTech(con.iFishing, True, iCiv, False, False)
                        teamVikings.setHasTech(con.iSailing, True, iCiv, False, False)
                        teamVikings.setHasTech(con.iTheWheel, True, iCiv, False, False)
                        teamVikings.setHasTech(con.iPottery, True, iCiv, False, False)
                        teamVikings.setHasTech(con.iAgriculture, True, iCiv, False, False)
                        teamVikings.setHasTech(con.iWriting, True, iCiv, False, False)
                        teamVikings.setHasTech(con.iCodeOfLaws, True, iCiv, False, False)
                        teamVikings.setHasTech(con.iFeudalism, True, iCiv, False, False)
                        teamVikings.setHasTech(con.iAlphabet, True, iCiv, False, False)
                        teamVikings.setHasTech(con.iMathematics, True, iCiv, False, False)
                        teamVikings.setHasTech(con.iConstruction, True, iCiv, False, False)
                        teamVikings.setHasTech(con.iCurrency, True, iCiv, False, False)
                        teamVikings.setHasTech(con.iHunting, True, iCiv, False, False)
                        teamVikings.setHasTech(con.iArchery, True, iCiv, False, False)
                        teamVikings.setHasTech(con.iAnimalHusbandry, True, iCiv, False, False)
                if (iCiv == iArabia):
                        teamArabia.setHasTech(con.iMining, True, iCiv, False, False)
                        teamArabia.setHasTech(con.iBronzeWorking, True, iCiv, False, False)
                        teamArabia.setHasTech(con.iIronWorking, True, iCiv, False, False)
                        teamArabia.setHasTech(con.iMetalCasting, True, iCiv, False, False)
                        teamArabia.setHasTech(con.iMachinery, True, iCiv, False, False)
                        teamArabia.setHasTech(con.iMysticism, True, iCiv, False, False)
                        teamArabia.setHasTech(con.iPolytheism, True, iCiv, False, False)
                        teamArabia.setHasTech(con.iMasonry, True, iCiv, False, False)
                        teamArabia.setHasTech(con.iPriesthood, True, iCiv, False, False)
                        teamArabia.setHasTech(con.iMonotheism, True, iCiv, False, False)
                        teamArabia.setHasTech(con.iTheology, True, iCiv, False, False)
                        teamArabia.setHasTech(con.iMonarchy, True, iCiv, False, False)
                        teamArabia.setHasTech(con.iDivineRight, True, iCiv, False, False)
                        teamArabia.setHasTech(con.iFishing, True, iCiv, False, False)
                        teamArabia.setHasTech(con.iSailing, True, iCiv, False, False)
                        teamArabia.setHasTech(con.iTheWheel, True, iCiv, False, False)
                        teamArabia.setHasTech(con.iPottery, True, iCiv, False, False)
                        teamArabia.setHasTech(con.iAgriculture, True, iCiv, False, False)
                        teamArabia.setHasTech(con.iWriting, True, iCiv, False, False)
                        teamArabia.setHasTech(con.iCodeOfLaws, True, iCiv, False, False)
                        teamArabia.setHasTech(con.iFeudalism, True, iCiv, False, False)
                        teamArabia.setHasTech(con.iGuilds, True, iCiv, False, False)
                        teamArabia.setHasTech(con.iAlphabet, True, iCiv, False, False)
                        teamArabia.setHasTech(con.iMathematics, True, iCiv, False, False)
                        teamArabia.setHasTech(con.iConstruction, True, iCiv, False, False)
                        teamArabia.setHasTech(con.iCurrency, True, iCiv, False, False)
                        teamArabia.setHasTech(con.iHunting, True, iCiv, False, False)
                        teamArabia.setHasTech(con.iArchery, True, iCiv, False, False)
                        teamArabia.setHasTech(con.iAnimalHusbandry, True, iCiv, False, False)
                        teamArabia.setHasTech(con.iHorsebackRiding, True, iCiv, False, False)                
                if (iCiv == iKhmer):
                        teamKhmer.setHasTech(con.iMining, True, iCiv, False, False)
                        teamKhmer.setHasTech(con.iBronzeWorking, True, iCiv, False, False)
                        teamKhmer.setHasTech(con.iIronWorking, True, iCiv, False, False)
                        teamKhmer.setHasTech(con.iMetalCasting, True, iCiv, False, False)
                        teamKhmer.setHasTech(con.iMachinery, True, iCiv, False, False)
                        teamKhmer.setHasTech(con.iMysticism, True, iCiv, False, False)
                        teamKhmer.setHasTech(con.iPolytheism, True, iCiv, False, False)
                        teamKhmer.setHasTech(con.iMasonry, True, iCiv, False, False)
                        teamKhmer.setHasTech(con.iMeditation, True, iCiv, False, False)
                        teamKhmer.setHasTech(con.iPriesthood, True, iCiv, False, False)
                        teamKhmer.setHasTech(con.iMonotheism, True, iCiv, False, False)
                        teamKhmer.setHasTech(con.iMonarchy, True, iCiv, False, False)
                        teamKhmer.setHasTech(con.iFishing, True, iCiv, False, False)
                        teamKhmer.setHasTech(con.iTheWheel, True, iCiv, False, False)
                        teamKhmer.setHasTech(con.iPottery, True, iCiv, False, False)
                        teamKhmer.setHasTech(con.iAgriculture, True, iCiv, False, False)
                        teamKhmer.setHasTech(con.iWriting, True, iCiv, False, False)
                        teamKhmer.setHasTech(con.iCodeOfLaws, True, iCiv, False, False)
                        teamKhmer.setHasTech(con.iMathematics, True, iCiv, False, False)
                        teamKhmer.setHasTech(con.iConstruction, True, iCiv, False, False)
                        teamKhmer.setHasTech(con.iHunting, True, iCiv, False, False)
                        teamKhmer.setHasTech(con.iArchery, True, iCiv, False, False)
                        teamKhmer.setHasTech(con.iAnimalHusbandry, True, iCiv, False, False)
                        teamKhmer.setHasTech(con.iHorsebackRiding, True, iCiv, False, False)          
                if (iCiv == iSpain):
                        teamSpain.setHasTech(con.iMining, True, iCiv, False, False)
                        teamSpain.setHasTech(con.iBronzeWorking, True, iCiv, False, False)
                        teamSpain.setHasTech(con.iIronWorking, True, iCiv, False, False)
                        teamSpain.setHasTech(con.iMetalCasting, True, iCiv, False, False)
                        teamSpain.setHasTech(con.iMachinery, True, iCiv, False, False)
                        teamSpain.setHasTech(con.iMysticism, True, iCiv, False, False)
                        teamSpain.setHasTech(con.iPolytheism, True, iCiv, False, False)
                        teamSpain.setHasTech(con.iMasonry, True, iCiv, False, False)
                        teamSpain.setHasTech(con.iPriesthood, True, iCiv, False, False)
                        teamSpain.setHasTech(con.iMonotheism, True, iCiv, False, False)
                        teamSpain.setHasTech(con.iTheology, True, iCiv, False, False)
                        teamSpain.setHasTech(con.iMonarchy, True, iCiv, False, False)
                        teamSpain.setHasTech(con.iFishing, True, iCiv, False, False)
                        teamSpain.setHasTech(con.iSailing, True, iCiv, False, False)
                        teamSpain.setHasTech(con.iTheWheel, True, iCiv, False, False)
                        teamSpain.setHasTech(con.iPottery, True, iCiv, False, False)
                        teamSpain.setHasTech(con.iAgriculture, True, iCiv, False, False)
                        teamSpain.setHasTech(con.iWriting, True, iCiv, False, False)
                        teamSpain.setHasTech(con.iCodeOfLaws, True, iCiv, False, False)
                        teamSpain.setHasTech(con.iFeudalism, True, iCiv, False, False)
                        teamSpain.setHasTech(con.iAlphabet, True, iCiv, False, False)
                        teamSpain.setHasTech(con.iMathematics, True, iCiv, False, False)
                        teamSpain.setHasTech(con.iConstruction, True, iCiv, False, False)
                        teamSpain.setHasTech(con.iCurrency, True, iCiv, False, False)
                        teamSpain.setHasTech(con.iHunting, True, iCiv, False, False)
                        teamSpain.setHasTech(con.iArchery, True, iCiv, False, False)
                        teamSpain.setHasTech(con.iAnimalHusbandry, True, iCiv, False, False)
                        teamSpain.setHasTech(con.iHorsebackRiding, True, iCiv, False, False)
                if (iCiv == iFrance):
                        teamFrance.setHasTech(con.iMining, True, iCiv, False, False)
                        teamFrance.setHasTech(con.iBronzeWorking, True, iCiv, False, False)
                        teamFrance.setHasTech(con.iIronWorking, True, iCiv, False, False)
                        teamFrance.setHasTech(con.iMetalCasting, True, iCiv, False, False)
                        teamFrance.setHasTech(con.iMachinery, True, iCiv, False, False)
                        teamFrance.setHasTech(con.iMysticism, True, iCiv, False, False)                        
                        teamFrance.setHasTech(con.iPolytheism, True, iCiv, False, False)
                        teamFrance.setHasTech(con.iMasonry, True, iCiv, False, False)
                        teamFrance.setHasTech(con.iPriesthood, True, iCiv, False, False)
                        teamFrance.setHasTech(con.iMonotheism, True, iCiv, False, False)
                        teamFrance.setHasTech(con.iTheology, True, iCiv, False, False)
                        teamFrance.setHasTech(con.iMonarchy, True, iCiv, False, False)
                        teamFrance.setHasTech(con.iFishing, True, iCiv, False, False)
                        teamFrance.setHasTech(con.iSailing, True, iCiv, False, False)
                        teamFrance.setHasTech(con.iTheWheel, True, iCiv, False, False)
                        teamFrance.setHasTech(con.iPottery, True, iCiv, False, False)
                        teamFrance.setHasTech(con.iAgriculture, True, iCiv, False, False)
                        teamFrance.setHasTech(con.iWriting, True, iCiv, False, False)
                        teamFrance.setHasTech(con.iCodeOfLaws, True, iCiv, False, False)
                        teamFrance.setHasTech(con.iFeudalism, True, iCiv, False, False)
                        teamFrance.setHasTech(con.iAlphabet, True, iCiv, False, False)
                        teamFrance.setHasTech(con.iMathematics, True, iCiv, False, False)
                        teamFrance.setHasTech(con.iConstruction, True, iCiv, False, False)
                        teamFrance.setHasTech(con.iCurrency, True, iCiv, False, False)
                        teamFrance.setHasTech(con.iHunting, True, iCiv, False, False)
                        teamFrance.setHasTech(con.iArchery, True, iCiv, False, False)
                        teamFrance.setHasTech(con.iAnimalHusbandry, True, iCiv, False, False)
                        teamFrance.setHasTech(con.iHorsebackRiding, True, iCiv, False, False)
                if (iCiv == iEngland):
                        teamEngland.setHasTech(con.iMining, True, iCiv, False, False)
                        teamEngland.setHasTech(con.iBronzeWorking, True, iCiv, False, False)
                        teamEngland.setHasTech(con.iIronWorking, True, iCiv, False, False)
                        teamEngland.setHasTech(con.iMetalCasting, True, iCiv, False, False)
                        teamEngland.setHasTech(con.iMachinery, True, iCiv, False, False)
                        teamEngland.setHasTech(con.iMysticism, True, iCiv, False, False)
                        teamEngland.setHasTech(con.iPolytheism, True, iCiv, False, False)
                        teamEngland.setHasTech(con.iMasonry, True, iCiv, False, False)
                        teamEngland.setHasTech(con.iPriesthood, True, iCiv, False, False)
                        teamEngland.setHasTech(con.iMonotheism, True, iCiv, False, False)
                        teamEngland.setHasTech(con.iTheology, True, iCiv, False, False)
                        teamEngland.setHasTech(con.iMonarchy, True, iCiv, False, False)
                        teamEngland.setHasTech(con.iFishing, True, iCiv, False, False)
                        teamEngland.setHasTech(con.iSailing, True, iCiv, False, False)
                        teamEngland.setHasTech(con.iTheWheel, True, iCiv, False, False)
                        teamEngland.setHasTech(con.iPottery, True, iCiv, False, False)
                        teamEngland.setHasTech(con.iAgriculture, True, iCiv, False, False)
                        teamEngland.setHasTech(con.iWriting, True, iCiv, False, False)
                        teamEngland.setHasTech(con.iCodeOfLaws, True, iCiv, False, False)
                        teamEngland.setHasTech(con.iFeudalism, True, iCiv, False, False)
                        teamEngland.setHasTech(con.iAlphabet, True, iCiv, False, False)
                        teamEngland.setHasTech(con.iMathematics, True, iCiv, False, False)
                        teamEngland.setHasTech(con.iConstruction, True, iCiv, False, False)
                        teamEngland.setHasTech(con.iCurrency, True, iCiv, False, False)
                        teamEngland.setHasTech(con.iHunting, True, iCiv, False, False)
                        teamEngland.setHasTech(con.iArchery, True, iCiv, False, False)
                        teamEngland.setHasTech(con.iAnimalHusbandry, True, iCiv, False, False)
                        teamEngland.setHasTech(con.iHorsebackRiding, True, iCiv, False, False)
                if (iCiv == iGermany):
                        teamGermany.setHasTech(con.iMining, True, iCiv, False, False)
                        teamGermany.setHasTech(con.iBronzeWorking, True, iCiv, False, False)
                        teamGermany.setHasTech(con.iIronWorking, True, iCiv, False, False)
                        teamGermany.setHasTech(con.iMetalCasting, True, iCiv, False, False)
                        teamGermany.setHasTech(con.iMachinery, True, iCiv, False, False)
                        teamGermany.setHasTech(con.iMysticism, True, iCiv, False, False)
                        teamGermany.setHasTech(con.iPolytheism, True, iCiv, False, False)
                        teamGermany.setHasTech(con.iMasonry, True, iCiv, False, False)
                        teamGermany.setHasTech(con.iPriesthood, True, iCiv, False, False)
                        teamGermany.setHasTech(con.iMonotheism, True, iCiv, False, False)
                        teamGermany.setHasTech(con.iTheology, True, iCiv, False, False)
                        teamGermany.setHasTech(con.iMonarchy, True, iCiv, False, False)
                        teamGermany.setHasTech(con.iFishing, True, iCiv, False, False)
                        teamGermany.setHasTech(con.iTheWheel, True, iCiv, False, False)
                        teamGermany.setHasTech(con.iPottery, True, iCiv, False, False)
                        teamGermany.setHasTech(con.iAgriculture, True, iCiv, False, False)
                        teamGermany.setHasTech(con.iWriting, True, iCiv, False, False)
                        teamGermany.setHasTech(con.iCodeOfLaws, True, iCiv, False, False)
                        teamGermany.setHasTech(con.iFeudalism, True, iCiv, False, False)
                        teamGermany.setHasTech(con.iAlphabet, True, iCiv, False, False)
                        teamGermany.setHasTech(con.iMathematics, True, iCiv, False, False)
                        teamGermany.setHasTech(con.iConstruction, True, iCiv, False, False)
                        teamGermany.setHasTech(con.iCurrency, True, iCiv, False, False)
                        teamGermany.setHasTech(con.iHunting, True, iCiv, False, False)
                        teamGermany.setHasTech(con.iArchery, True, iCiv, False, False)
                        teamGermany.setHasTech(con.iAnimalHusbandry, True, iCiv, False, False)
                        teamGermany.setHasTech(con.iHorsebackRiding, True, iCiv, False, False)
                if (iCiv == iRussia):
                        teamRussia.setHasTech(con.iMining, True, iCiv, False, False)
                        teamRussia.setHasTech(con.iBronzeWorking, True, iCiv, False, False)
                        teamRussia.setHasTech(con.iIronWorking, True, iCiv, False, False)
                        teamRussia.setHasTech(con.iMetalCasting, True, iCiv, False, False)
                        teamRussia.setHasTech(con.iMachinery, True, iCiv, False, False)
                        teamRussia.setHasTech(con.iMysticism, True, iCiv, False, False)
                        teamRussia.setHasTech(con.iPolytheism, True, iCiv, False, False)
                        teamRussia.setHasTech(con.iMasonry, True, iCiv, False, False)
                        teamRussia.setHasTech(con.iPriesthood, True, iCiv, False, False)
                        teamRussia.setHasTech(con.iMonotheism, True, iCiv, False, False)
                        teamRussia.setHasTech(con.iTheology, True, iCiv, False, False)
                        teamRussia.setHasTech(con.iMonarchy, True, iCiv, False, False)
                        teamRussia.setHasTech(con.iTheWheel, True, iCiv, False, False)
                        teamRussia.setHasTech(con.iPottery, True, iCiv, False, False)
                        teamRussia.setHasTech(con.iAgriculture, True, iCiv, False, False)
                        teamRussia.setHasTech(con.iWriting, True, iCiv, False, False)
                        teamRussia.setHasTech(con.iCodeOfLaws, True, iCiv, False, False)
                        teamRussia.setHasTech(con.iFeudalism, True, iCiv, False, False)
                        teamRussia.setHasTech(con.iAlphabet, True, iCiv, False, False)
                        teamRussia.setHasTech(con.iMathematics, True, iCiv, False, False)
                        teamRussia.setHasTech(con.iConstruction, True, iCiv, False, False)
                        teamRussia.setHasTech(con.iCurrency, True, iCiv, False, False)
                        teamRussia.setHasTech(con.iHunting, True, iCiv, False, False)
                        teamRussia.setHasTech(con.iArchery, True, iCiv, False, False)
                        teamRussia.setHasTech(con.iAnimalHusbandry, True, iCiv, False, False)
                        teamRussia.setHasTech(con.iHorsebackRiding, True, iCiv, False, False)
                if (iCiv == iHolland):
                        teamHolland.setHasTech(con.iMining, True, iCiv, False, False)
                        teamHolland.setHasTech(con.iBronzeWorking, True, iCiv, False, False)
                        teamHolland.setHasTech(con.iIronWorking, True, iCiv, False, False)
                        teamHolland.setHasTech(con.iMetalCasting, True, iCiv, False, False)
                        teamHolland.setHasTech(con.iMachinery, True, iCiv, False, False)
                        teamHolland.setHasTech(con.iMysticism, True, iCiv, False, False)
                        teamHolland.setHasTech(con.iPolytheism, True, iCiv, False, False)
                        teamHolland.setHasTech(con.iMasonry, True, iCiv, False, False)
                        teamHolland.setHasTech(con.iPriesthood, True, iCiv, False, False)
                        teamHolland.setHasTech(con.iMonotheism, True, iCiv, False, False)
                        teamHolland.setHasTech(con.iTheology, True, iCiv, False, False)
                        teamHolland.setHasTech(con.iMonarchy, True, iCiv, False, False)
                        teamHolland.setHasTech(con.iDivineRight, True, iCiv, False, False)
                        teamHolland.setHasTech(con.iFishing, True, iCiv, False, False)
                        teamHolland.setHasTech(con.iSailing, True, iCiv, False, False)
                        teamHolland.setHasTech(con.iTheWheel, True, iCiv, False, False)
                        teamHolland.setHasTech(con.iPottery, True, iCiv, False, False)
                        teamHolland.setHasTech(con.iAgriculture, True, iCiv, False, False)
                        teamHolland.setHasTech(con.iWriting, True, iCiv, False, False)
                        teamHolland.setHasTech(con.iCodeOfLaws, True, iCiv, False, False)
                        teamHolland.setHasTech(con.iFeudalism, True, iCiv, False, False)
                        teamHolland.setHasTech(con.iGuilds, True, iCiv, False, False)
                        teamHolland.setHasTech(con.iAlphabet, True, iCiv, False, False)
                        teamHolland.setHasTech(con.iMathematics, True, iCiv, False, False)
                        teamHolland.setHasTech(con.iConstruction, True, iCiv, False, False)
                        teamHolland.setHasTech(con.iEngineering, True, iCiv, False, False)
                        teamHolland.setHasTech(con.iCurrency, True, iCiv, False, False)
                        teamHolland.setHasTech(con.iHunting, True, iCiv, False, False)
                        teamHolland.setHasTech(con.iArchery, True, iCiv, False, False)
                        teamHolland.setHasTech(con.iAnimalHusbandry, True, iCiv, False, False)
                        teamHolland.setHasTech(con.iHorsebackRiding, True, iCiv, False, False)
                if (iCiv == iMali):
                        teamMali.setHasTech(con.iMining, True, iCiv, False, False)
                        teamMali.setHasTech(con.iBronzeWorking, True, iCiv, False, False)
                        teamMali.setHasTech(con.iIronWorking, True, iCiv, False, False)
                        teamMali.setHasTech(con.iMetalCasting, True, iCiv, False, False)
                        #teamMali.setHasTech(con.iMachinery, True, iCiv, False, False)
                        teamMali.setHasTech(con.iMysticism, True, iCiv, False, False)
                        teamMali.setHasTech(con.iPolytheism, True, iCiv, False, False)
                        teamMali.setHasTech(con.iMasonry, True, iCiv, False, False)
                        teamMali.setHasTech(con.iPriesthood, True, iCiv, False, False)
                        teamMali.setHasTech(con.iMonotheism, True, iCiv, False, False)
                        teamMali.setHasTech(con.iTheology, True, iCiv, False, False)
                        teamMali.setHasTech(con.iMonarchy, True, iCiv, False, False)
                        teamMali.setHasTech(con.iDivineRight, True, iCiv, False, False)
                        teamMali.setHasTech(con.iTheWheel, True, iCiv, False, False)
                        teamMali.setHasTech(con.iPottery, True, iCiv, False, False)
                        teamMali.setHasTech(con.iAgriculture, True, iCiv, False, False)
                        teamMali.setHasTech(con.iWriting, True, iCiv, False, False)
                        teamMali.setHasTech(con.iAlphabet, True, iCiv, False, False)
                        teamMali.setHasTech(con.iMathematics, True, iCiv, False, False)
                        teamMali.setHasTech(con.iConstruction, True, iCiv, False, False)
                        teamMali.setHasTech(con.iCurrency, True, iCiv, False, False)
                        teamMali.setHasTech(con.iHunting, True, iCiv, False, False)
                        teamMali.setHasTech(con.iArchery, True, iCiv, False, False)
                        teamMali.setHasTech(con.iAnimalHusbandry, True, iCiv, False, False)
                        teamMali.setHasTech(con.iHorsebackRiding, True, iCiv, False, False)
                if (iCiv == iTurkey):
                        teamTurkey.setHasTech(con.iMining, True, iCiv, False, False)
                        teamTurkey.setHasTech(con.iBronzeWorking, True, iCiv, False, False)
                        teamTurkey.setHasTech(con.iIronWorking, True, iCiv, False, False)
                        teamTurkey.setHasTech(con.iMetalCasting, True, iCiv, False, False)
                        teamTurkey.setHasTech(con.iMachinery, True, iCiv, False, False)
                        teamTurkey.setHasTech(con.iMysticism, True, iCiv, False, False)
                        teamTurkey.setHasTech(con.iPolytheism, True, iCiv, False, False)
                        teamTurkey.setHasTech(con.iMasonry, True, iCiv, False, False)
                        teamTurkey.setHasTech(con.iPriesthood, True, iCiv, False, False)
                        teamTurkey.setHasTech(con.iMonotheism, True, iCiv, False, False)
                        teamTurkey.setHasTech(con.iTheology, True, iCiv, False, False)
                        teamTurkey.setHasTech(con.iMonarchy, True, iCiv, False, False)
                        teamTurkey.setHasTech(con.iDivineRight, True, iCiv, False, False)
                        teamTurkey.setHasTech(con.iFishing, True, iCiv, False, False)
                        teamTurkey.setHasTech(con.iSailing, True, iCiv, False, False)
                        teamTurkey.setHasTech(con.iTheWheel, True, iCiv, False, False)
                        teamTurkey.setHasTech(con.iPottery, True, iCiv, False, False)
                        teamTurkey.setHasTech(con.iAgriculture, True, iCiv, False, False)
                        teamTurkey.setHasTech(con.iWriting, True, iCiv, False, False)
                        teamTurkey.setHasTech(con.iCodeOfLaws, True, iCiv, False, False)
                        teamTurkey.setHasTech(con.iFeudalism, True, iCiv, False, False)
                        teamTurkey.setHasTech(con.iCivilService, True, iCiv, False, False)
                        teamTurkey.setHasTech(con.iGuilds, True, iCiv, False, False)
                        teamTurkey.setHasTech(con.iGunpowder, True, iCiv, False, False)
                        teamTurkey.setHasTech(con.iAlphabet, True, iCiv, False, False)
                        teamTurkey.setHasTech(con.iMathematics, True, iCiv, False, False)
                        teamTurkey.setHasTech(con.iCalendar, True, iCiv, False, False)
                        teamTurkey.setHasTech(con.iConstruction, True, iCiv, False, False)
                        teamTurkey.setHasTech(con.iEngineering, True, iCiv, False, False)
                        teamTurkey.setHasTech(con.iCurrency, True, iCiv, False, False)
                        teamTurkey.setHasTech(con.iHunting, True, iCiv, False, False)
                        teamTurkey.setHasTech(con.iArchery, True, iCiv, False, False)
                        teamTurkey.setHasTech(con.iAnimalHusbandry, True, iCiv, False, False)
                        teamTurkey.setHasTech(con.iHorsebackRiding, True, iCiv, False, False)
                if (iCiv == iPortugal):
                        teamPortugal.setHasTech(con.iMining, True, iCiv, False, False)
                        teamPortugal.setHasTech(con.iBronzeWorking, True, iCiv, False, False)
                        teamPortugal.setHasTech(con.iIronWorking, True, iCiv, False, False)
                        teamPortugal.setHasTech(con.iMetalCasting, True, iCiv, False, False)
                        teamPortugal.setHasTech(con.iMachinery, True, iCiv, False, False)
                        teamPortugal.setHasTech(con.iMysticism, True, iCiv, False, False)
                        teamPortugal.setHasTech(con.iPolytheism, True, iCiv, False, False)
                        teamPortugal.setHasTech(con.iMasonry, True, iCiv, False, False)
                        teamPortugal.setHasTech(con.iPriesthood, True, iCiv, False, False)
                        teamPortugal.setHasTech(con.iMonotheism, True, iCiv, False, False)
                        teamPortugal.setHasTech(con.iTheology, True, iCiv, False, False)
                        teamPortugal.setHasTech(con.iMonarchy, True, iCiv, False, False)
                        teamPortugal.setHasTech(con.iDivineRight, True, iCiv, False, False)
                        teamPortugal.setHasTech(con.iFishing, True, iCiv, False, False)
                        teamPortugal.setHasTech(con.iSailing, True, iCiv, False, False)
                        teamPortugal.setHasTech(con.iTheWheel, True, iCiv, False, False)
                        teamPortugal.setHasTech(con.iPottery, True, iCiv, False, False)
                        teamPortugal.setHasTech(con.iAgriculture, True, iCiv, False, False)
                        teamPortugal.setHasTech(con.iWriting, True, iCiv, False, False)
                        teamPortugal.setHasTech(con.iCodeOfLaws, True, iCiv, False, False)
                        teamPortugal.setHasTech(con.iFeudalism, True, iCiv, False, False)
                        teamPortugal.setHasTech(con.iGuilds, True, iCiv, False, False)
                        teamPortugal.setHasTech(con.iAlphabet, True, iCiv, False, False)
                        teamPortugal.setHasTech(con.iMathematics, True, iCiv, False, False)
                        teamPortugal.setHasTech(con.iConstruction, True, iCiv, False, False)
                        teamPortugal.setHasTech(con.iEngineering, True, iCiv, False, False)
                        teamPortugal.setHasTech(con.iCurrency, True, iCiv, False, False)
                        teamPortugal.setHasTech(con.iHunting, True, iCiv, False, False)
                        teamPortugal.setHasTech(con.iArchery, True, iCiv, False, False)
                        teamPortugal.setHasTech(con.iAnimalHusbandry, True, iCiv, False, False)
                        teamPortugal.setHasTech(con.iHorsebackRiding, True, iCiv, False, False)
                if (iCiv == iInca):
                        teamInca.setHasTech(con.iMining, True, iCiv, False, False)
                        #teamInca.setHasTech(con.iBronzeWorking, True, iCiv, False, False)
                        #teamInca.setHasTech(con.iMetalCasting, True, iCiv, False, False)
                        teamInca.setHasTech(con.iMysticism, True, iCiv, False, False)
                        teamInca.setHasTech(con.iPolytheism, True, iCiv, False, False)
                        teamInca.setHasTech(con.iMasonry, True, iCiv, False, False)
                        teamInca.setHasTech(con.iPriesthood, True, iCiv, False, False)
                        #teamInca.setHasTech(con.iMonarchy, True, iCiv, False, False)
                        teamInca.setHasTech(con.iFishing, True, iCiv, False, False)
                        teamInca.setHasTech(con.iTheWheel, True, iCiv, False, False)
                        teamInca.setHasTech(con.iPottery, True, iCiv, False, False)
                        teamInca.setHasTech(con.iAgriculture, True, iCiv, False, False)
                        teamInca.setHasTech(con.iWriting, True, iCiv, False, False)
                        teamInca.setHasTech(con.iCodeOfLaws, True, iCiv, False, False)
                        teamInca.setHasTech(con.iMathematics, True, iCiv, False, False)
                        #teamInca.setHasTech(con.iConstruction, True, iCiv, False, False)
                        teamInca.setHasTech(con.iCurrency, True, iCiv, False, False)
                        teamInca.setHasTech(con.iHunting, True, iCiv, False, False)
                        teamInca.setHasTech(con.iArchery, True, iCiv, False, False)
                if (iCiv == iMongolia):
                        teamMongolia.setHasTech(con.iMining, True, iCiv, False, False)
                        teamMongolia.setHasTech(con.iBronzeWorking, True, iCiv, False, False)
                        teamMongolia.setHasTech(con.iIronWorking, True, iCiv, False, False)
                        teamMongolia.setHasTech(con.iMetalCasting, True, iCiv, False, False)
                        teamMongolia.setHasTech(con.iMachinery, True, iCiv, False, False)
                        teamMongolia.setHasTech(con.iMysticism, True, iCiv, False, False)
                        teamMongolia.setHasTech(con.iPolytheism, True, iCiv, False, False)
                        teamMongolia.setHasTech(con.iMeditation, True, iCiv, False, False)
                        teamMongolia.setHasTech(con.iPriesthood, True, iCiv, False, False)
                        teamMongolia.setHasTech(con.iMasonry, True, iCiv, False, False)
                        teamMongolia.setHasTech(con.iMonarchy, True, iCiv, False, False)
                        teamMongolia.setHasTech(con.iFishing, True, iCiv, False, False)
                        teamMongolia.setHasTech(con.iTheWheel, True, iCiv, False, False)
                        teamMongolia.setHasTech(con.iPottery, True, iCiv, False, False)
                        teamMongolia.setHasTech(con.iAgriculture, True, iCiv, False, False)
                        teamMongolia.setHasTech(con.iWriting, True, iCiv, False, False)
                        teamMongolia.setHasTech(con.iCodeOfLaws, True, iCiv, False, False)
                        teamMongolia.setHasTech(con.iFeudalism, True, iCiv, False, False)
                        teamMongolia.setHasTech(con.iGuilds, True, iCiv, False, False)
                        teamMongolia.setHasTech(con.iMathematics, True, iCiv, False, False)
                        teamMongolia.setHasTech(con.iConstruction, True, iCiv, False, False)
                        teamMongolia.setHasTech(con.iCurrency, True, iCiv, False, False)
                        teamMongolia.setHasTech(con.iHunting, True, iCiv, False, False)
                        teamMongolia.setHasTech(con.iArchery, True, iCiv, False, False)
                        teamMongolia.setHasTech(con.iAnimalHusbandry, True, iCiv, False, False)
                        teamMongolia.setHasTech(con.iHorsebackRiding, True, iCiv, False, False)                      
                if (iCiv == iAztecs):
                        teamAztecs.setHasTech(con.iMining, True, iCiv, False, False)
                        teamAztecs.setHasTech(con.iBronzeWorking, True, iCiv, False, False)
                        #teamAztecs.setHasTech(con.iIronWorking, True, iCiv, False, False)
                        #teamAztecs.setHasTech(con.iMetalCasting, True, iCiv, False, False)
                        teamAztecs.setHasTech(con.iMysticism, True, iCiv, False, False)
                        teamAztecs.setHasTech(con.iPolytheism, True, iCiv, False, False)
                        teamAztecs.setHasTech(con.iMasonry, True, iCiv, False, False)
                        teamAztecs.setHasTech(con.iPriesthood, True, iCiv, False, False)
                        #teamAztecs.setHasTech(con.iMonarchy, True, iCiv, False, False)
                        teamAztecs.setHasTech(con.iFishing, True, iCiv, False, False)
                        teamAztecs.setHasTech(con.iTheWheel, True, iCiv, False, False)
                        teamAztecs.setHasTech(con.iPottery, True, iCiv, False, False)
                        teamAztecs.setHasTech(con.iAgriculture, True, iCiv, False, False)
                        teamAztecs.setHasTech(con.iWriting, True, iCiv, False, False)
                        teamAztecs.setHasTech(con.iCodeOfLaws, True, iCiv, False, False)
                        teamAztecs.setHasTech(con.iMathematics, True, iCiv, False, False)
                        teamAztecs.setHasTech(con.iCalendar, True, iCiv, False, False)
                        #teamAztecs.setHasTech(con.iConstruction, True, iCiv, False, False)
                        teamAztecs.setHasTech(con.iCurrency, True, iCiv, False, False)
                        teamAztecs.setHasTech(con.iHunting, True, iCiv, False, False)
                        teamAztecs.setHasTech(con.iArchery, True, iCiv, False, False)
                if (iCiv == iAmerica):
                        for x in range(con.iLiberalism+1):
                                teamAmerica.setHasTech(x, True, iCiv, False, False)
                        for x in range(con.iFishing, con.iChemistry+1):
                                teamAmerica.setHasTech(x, True, iCiv, False, False)
                        for x in range(con.iHunting, con.iRifling+1):
                                teamAmerica.setHasTech(x, True, iCiv, False, False)

                self.hitNeighboursStability(iCiv)

        def hitNeighboursStability( self, iCiv ):
                if (len(con.lOlderNeighbours[iCiv])):
                        bHuman = False
                        for iLoop in range(len(con.lOlderNeighbours[iCiv])):
                                if (gc.getPlayer(iLoop).isAlive()):
                                        if (iLoop == utils.getHumanID()):
                                                bHuman = True                                        
                                        utils.setStability(iLoop, utils.getStability(iLoop)-2)
                        if (bHuman):
                                utils.setStabilityParameters(con.iParDiplomacyE, utils.getStabilityParameters(con.iParDiplomacyE)-2)


