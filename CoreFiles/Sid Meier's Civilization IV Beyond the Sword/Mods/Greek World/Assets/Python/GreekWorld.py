# Greek World Scenario

from CvPythonExtensions import *
import CvUtil
import PyHelpers		# LOQ
import Popup
import pickle			# LOQ 2005-10-12

# globals
gc = CyGlobalContext()
PyPlayer = PyHelpers.PyPlayer	# LOQ

### Constants ###


# initialise player variables to player IDs from WBS
iRome = 0
iPersia = 1
iMacedonia = 2
iEgypt = 3
iIndia = 4
iCelts = 5
iBabylon = 6
iPhoenicia = 7
iIsrael = 8
iGermanic = 9
iScythia = 10
iEtruria = 11
iGreece = 12
iGreekCol = 13
iSeleucia = 14
iParthia = 15 

iNumPlayers = 16

pRome = gc.getPlayer(iRome)
pPersia = gc.getPlayer(iPersia)
pMacedonia = gc.getPlayer(iMacedonia)
pEgypt = gc.getPlayer(iEgypt)
pIndia = gc.getPlayer(iIndia)
pCelts = gc.getPlayer(iCelts)
pBabylon = gc.getPlayer(iBabylon)
pPhoenicia = gc.getPlayer(iPhoenicia)
pIsrael = gc.getPlayer(iIsrael)
pGermanic = gc.getPlayer(iGermanic)
pScythia = gc.getPlayer(iScythia)
pEtruria = gc.getPlayer(iEtruria)
pGreece = gc.getPlayer(iGreece)
pGreekCol = gc.getPlayer(iGreekCol)
pSeleucia = gc.getPlayer(iSeleucia)
pParthia = gc.getPlayer(iParthia)

# initialise unit variables to unit indices from XML
iSettler = 4
iWorker = 5
iChristianMissionary = 11
iSwordsman = 19
iAxeman = 22
iPhalanx = 26
iArcher = 38
iHorseArcher = 46
iCamelArcher = 49
iGalley = 63

# initialise religion variables to religion indices from XML
iJudaism = 0
iChristianity = 1
iZoroastrianism = 2
iHinduism = 3
iMesopotamian = 4
iGreek = 5
iEgyptian = 6

# initialise city coordinates
tYerushalayim = (46, 32)
tRome = (23, 45)
tArezzo = (22, 48)
tAdria = (23, 51)
tMilano = (19, 50)
tCarthage = (21, 34)
tPalemmo = (21, 39)
tNora = (18, 40)
tAlalia = (19, 44)
tGadir = (8, 39)
tTaranto = (27, 42)
tLeptis = (25, 32)
tHippo = (17, 34)
tSiracusa = (24, 39)
tTyre = (45, 35)
tMarseilles = (16, 46)
tAleppo = (48, 38)
tSaguntum = (13, 42)
tParsa = (62, 29)
tEcbatana = (58, 35)
tGabae = (62, 34)
tRagha = (62, 38)
tHasanlu = (58, 42)
tBactra = (68, 42)
tTaxila = (70, 39)
tTarsus = (45, 39)
tSardis = (42, 41)
tTrapezus = (49, 43)
tBabylon = (52, 31)
tNineveh = (55, 39)
tSusa = (57, 30)
tAshur = (54, 36)
tLarsa = (55, 27)
tByzantium = (41, 44)
tMiletos = (40, 40)
tTanis = (39, 30)
tMemphis = (37, 28)
tHeliopolis = (38, 25)
tThebes = (39, 22)
tCyrene = (33, 31)
tAthens = (36, 40)
tSparta = (33, 38)
tCorinth = (34, 40)
tDelphi = (33, 42)
tRhodes = (40, 37)
tIsmara = (37, 46)
tEpidamnos = (30, 46)
tArgos = (34, 46)
tAlesia = (17, 56)
tGergovia = (14, 51)
tPetra = (47, 29)
tTayma = (49, 22)
tMarib = (50, 13)
tGerrha = (56, 19)
tPura = (67, 31)
tPannonia = (31, 52)


# LOQ 2005-10-12: removed Fates




class GreekWorld:

        iSpawnTurn = 500

	def makeUnit(self, iUnit, iPlayer, tCoords, iNum): #by LOQ
		'Makes iNum units for player iPlayer of the type iUnit at tCoords.'
		for i in range(iNum):
			player = gc.getPlayer(iPlayer)
			player.initUnit(iUnit, tCoords[0], tCoords[1], UnitAITypes.NO_UNITAI)

	def displayWelcomePopup( self ):
		popup = Popup.PyPopup()
		popup.setHeaderString( CyTranslator().getText("TXT_KEY_GREEK_WORLD_TITLE", ()) )
		popup.setBodyString( CyTranslator().getText("TXT_KEY_GREEK_WORLD_INTRO", ()) )
		popup.launch()

# ***** LOQ 2005-10-12: begin ***** #
	def setupScriptData( self ):
		"""Initialise the global script data dictionary for usage."""
		# random variables
		scriptDict =	{	'iPunicFate': -1,
					'iJerusalemFate': -1,
					'iPersianFate': -1,
					'iAlexanderFate': -1
				}
		gc.getPlayer(0).setScriptData( pickle.dumps(scriptDict) )

	def getPunicFate( self ):
		"""Returns PunicFate."""
		scriptDict = pickle.loads( gc.getPlayer(0).getScriptData() )
		return scriptDict['iPunicFate']

	def setPunicFate( self, iNewValue ):
		"""Sets PunicFate."""
		scriptDict = pickle.loads( gc.getPlayer(0).getScriptData() )
		scriptDict['iPunicFate'] = iNewValue
		gc.getPlayer(0).setScriptData( pickle.dumps(scriptDict) )

	def getJerusalemFate( self ):
		"""Returns JerusalemFate."""
		scriptDict = pickle.loads( gc.getPlayer(0).getScriptData() )
		return scriptDict['iJerusalemFate']

	def setJerusalemFate( self, iNewValue ):
		"""Sets JerusalemFate."""
		scriptDict = pickle.loads( gc.getPlayer(0).getScriptData() )
		scriptDict['iJerusalemFate'] = iNewValue
		gc.getPlayer(0).setScriptData( pickle.dumps(scriptDict) )

	def getPersianFate( self ):
		"""Returns PersianFate."""
		scriptDict = pickle.loads( gc.getPlayer(0).getScriptData() )
		return scriptDict['iPersianFate']

	def setPersianFate( self, iNewValue ):
		"""Sets PersianFate."""
		scriptDict = pickle.loads( gc.getPlayer(0).getScriptData() )
		scriptDict['iPersianFate'] = iNewValue
		gc.getPlayer(0).setScriptData( pickle.dumps(scriptDict) )

	def getAlexanderFate( self ):
		"""Returns AlexanderFate."""
		scriptDict = pickle.loads( gc.getPlayer(0).getScriptData() )
		return scriptDict['iAlexanderFate']

	def setAlexanderFate( self, iNewValue ):
		"""Sets AlexanderFate."""
		scriptDict = pickle.loads( gc.getPlayer(0).getScriptData() )
		scriptDict['iAlexanderFate'] = iNewValue
		gc.getPlayer(0).setScriptData( pickle.dumps(scriptDict) )

# ***** LOQ 2005-10-12: end ***** #


	def setup(self):
              
                # initialise random variables	# LOQ 2005-10-12
		self.setupScriptData()
                self.setPunicFate(gc.getGame().getSorenRandNum(100, 'Greek World - fate of Punic Wars'))
                self.setJerusalemFate(gc.getGame().getSorenRandNum(100, 'Greek World - fate of Jerusalem'))
                self.setPersianFate(gc.getGame().getSorenRandNum(100, 'Greek World - fate of Persia'))
                self.setAlexanderFate(gc.getGame().getSorenRandNum(100, 'Greek World - fate of Alexander'))


                # adds additional units to the human player's civ
                if (pRome.isHuman()):
                        self.makeUnit(iSettler, iRome, tRome, 1)
                        #self.makeUnit(iWorker, iRome, tRome, 1)
                if (pPersia.isHuman()):
                        self.makeUnit(iSettler, iPersia, tParsa, 1)
                        #self.makeUnit(iWorker, iPersia, tParsa, 1)
                if (pMacedonia.isHuman()):
                        self.makeUnit(iSettler, iMacedonia, tArgos, 1)
                        #self.makeUnit(iWorker, iMacedonia, tArgos, 1)
             
		# display welcome message
		self.displayWelcomePopup()

			
        def checkTurn(self, iGameTurn):


                #popup to test if conditions are working
##		if (iGameTurn >= 0):
##                        popup = Popup.PyPopup()
##                        popup.setBodyString( '%d punic \n %d jeru \n %d persia \n %d alex' %(self.getPunicFate(), self.getJerusalemFate(), self.getPersianFate(), self.getAlexanderFate()))
##                        popup.launch()

		if (iGameTurn == 1) or (iGameTurn == 30) or (iGameTurn == 60) or (iGameTurn == 90) or (iGameTurn == 120) or (iGameTurn == 150):
                        self.iSpawnTurn = iGameTurn + gc.getGame().getSorenRandNum(28, 'Greek World - Spawn turn range')

		if (iGameTurn == self.iSpawnTurn) and (iGameTurn <= 149):
                        #Scythian spawn
                        tTopLeft = (41, 44)
                        tBottomRight = (63, 59)
                        dummy, plotList = self.squareSearch( tTopLeft, tBottomRight, self.outerSpawn, [] )
                        rndNum = gc.getGame().getSorenRandNum(len(plotList), 'Greek World - Scythia')
                        result = plotList[rndNum]
                        if (result):
                                self.makeUnit(iHorseArcher, iScythia, result, 3)
                                self.makeUnit(iArcher, iScythia, result, 2)
                                self.makeUnit(iSettler, iScythia, result, 1)
                                self.makeUnit(iWorker, iScythia, result, 1)
        		
		if (iGameTurn == self.iSpawnTurn) and (iGameTurn >= 30):
                        #Germanic spawn
                        tTopLeft = (24, 53)
                        tBottomRight = (41, 70)
                        dummy, plotList = self.squareSearch( tTopLeft, tBottomRight, self.outerSpawn, [] )
                        rndNum = gc.getGame().getSorenRandNum(len(plotList), 'Greek World - Germanic tribes')
                        result = plotList[rndNum]
                        if (result):
                                self.makeUnit(iAxeman, iGermanic, result, 4)
                                self.makeUnit(iArcher, iGermanic, result, 2)
                                self.makeUnit(iSettler, iGermanic, result, 1)
                                self.makeUnit(iWorker, iGermanic, result, 1)
        		
		if (iGameTurn == self.iSpawnTurn) and (iGameTurn <= 111):
                        #Celtic spawn
                        tTopLeft = (8, 43)
                        tBottomRight = (43, 62)
                        dummy, plotList = self.squareSearch( tTopLeft, tBottomRight, self.outerSpawn, [] )
                        rndNum = gc.getGame().getSorenRandNum(len(plotList), 'Greek World - Celts')
                        result = plotList[rndNum]
                        if (result):
                                self.makeUnit(iAxeman, iCelts, result, 4)		
                                self.makeUnit(iArcher, iCelts, result, 2)
                                self.makeUnit(iSettler, iCelts, result, 1)
                                self.makeUnit(iWorker, iCelts, result, 1)


                #Parthian spawn
		if (iGameTurn == 50) or (iGameTurn == 54): 
                        tTopLeft = (53, 36)
                        tBottomRight = (64, 45)
                        dummy, plotList = self.squareSearch( tTopLeft, tBottomRight, self.innerInvasion, [] )
                        rndNum = gc.getGame().getSorenRandNum(len(plotList), 'Greek World - Parthia')
                        result = plotList[rndNum]
                        if (result):
                                self.makeUnit(iHorseArcher, iParthia, result, 4)



                #Pirates from 200BC to 0AD (turn 80 to 120)
		if (iGameTurn >= 80 and iGameTurn <= 120):
                        if (iGameTurn % 4 == 0):
                                tTopLeft = (10, 34)
                                tBottomRight = (51, 46)
                                dummy, plotList = self.squareSearch( tTopLeft, tBottomRight, self.innerSeaSpawn, [] )
                                rndNum = gc.getGame().getSorenRandNum(len(plotList), 'Greek World - Pirates')
                                result = plotList[rndNum]
                                if (result):
                                        self.makeUnit(iGalley, 18, result, 1)



                #Barbarian invasions from 0AD (turn 120)
		if (iGameTurn >= 120 and iGameTurn <= 175):
                        if (iGameTurn % 3 == 0):
                                tTopLeft = (10, 11)
                                tBottomRight = (51, 30)
                                dummy, plotList = self.squareSearch( tTopLeft, tBottomRight, self.outerInvasion, [] )
                                rndNum = gc.getGame().getSorenRandNum(len(plotList), 'Greek World - Barbarians from the South')
                                result = plotList[rndNum]
                                if (result):
                                        self.makeUnit(iCamelArcher, 18, result, 5)
                        if (iGameTurn % 3 == 1):
                                tTopLeft = (20, 41)
                                tBottomRight = (71, 61)
                                dummy, plotList = self.squareSearch( tTopLeft, tBottomRight, self.innerInvasion, [] )
                                rndNum = gc.getGame().getSorenRandNum(len(plotList), 'Greek World - Barbarians from the East')
                                result = plotList[rndNum]
                                if (result):
                                        self.makeUnit(iHorseArcher, 18, result, 7)
                        if (iGameTurn % 3 == 2):
                                tTopLeft = (9, 46)
                                tBottomRight = (43, 72)
                                dummy, plotList = self.squareSearch( tTopLeft, tBottomRight, self.innerInvasion, [] )
                                rndNum = gc.getGame().getSorenRandNum(len(plotList), 'Greek World - Barbarians from the North')
                                result = plotList[rndNum]
                                if (result):
                                        self.makeUnit(iSwordsman, 18, result, 4)
                                        self.makeUnit(iAxeman, 18, result, 5)


                #Saguntum
                if (iGameTurn == 30):
                        iClean = 0
                        Plot = CyMap().plot( tSaguntum[0], tSaguntum[1] )
                        for x in range(tSaguntum[0] - 1, tSaguntum[1] + 2):		# from x-1 to x+1
                                for y in range(tSaguntum[0] - 1, tSaguntum[1] + 2):	# from y-1 to y+1
                                        if (Plot.getNumUnits() != 0):
                                                unit = Plot.getUnit(0)
                                                if (unit.getOwner() != iCelts):
                                                        iClean += 1
                        if (Plot.getPlotCity().isNone()) and (iClean == 0):
                                pCelts.found( tSaguntum[0], tSaguntum[1] )
                                Plot.getPlotCity().setName("Saguntum", True)

                
		#City flips
                                
                #Generic events
                if (self.getJerusalemFate() >= 50):
                        self.flipCity(3, tYerushalayim, 1, 1, iBabylon, [iIsrael])
                self.flipCity(2, tMarseilles, 1, 1, iCelts, [iEtruria])
                if (pRome.isHuman() == 0):
                        self.flipCity(3, tMilano, 1, 1, iCelts, [iEtruria])
                        self.flipCity(5, tAleppo, 1, 1, iBabylon, [iPhoenicia, iIsrael, 18])
                self.flipCity(5, tTyre, 1, 1, iBabylon, [iPhoenicia, iIsrael])
                self.flipCity(11, tPetra, 1, 1, iBabylon, [iIsrael])
                self.flipCity(12, tAlalia, 1, 1, iPhoenicia, [iGreekCol])
                self.flipCity(59, tPannonia, 1, 1, iCelts, [18, iEtruria])
                
                #Saguntum
                if (pPhoenicia.isAlive()):
                        self.flipCity(76, tSaguntum, 1, 1, iPhoenicia, [iCelts])
                        
                #Rise of Parthia
                self.flipCity(56, tGabae, 1, 1, iParthia, [18, iBabylon, iIndia])
                self.flipCity(56, tRagha, 1, 1, iParthia, [18, iBabylon, iIndia])
                self.flipCity(56, tHasanlu, 1, 1, iParthia, [18, iBabylon, iIndia])
                if (iGameTurn == 57):
                        for cityName in PyPlayer(iParthia).getCityList():
                                if not cityName.isNone():
                                        tCoords = (cityName.GetCy().getX(), cityName.GetCy().getY())
                                        self.makeUnit(iHorseArcher, iParthia, tCoords, 2)

                #Roman events
                if (pRome.isHuman() == 0):
                        city = gc.getMap().plot( tRome[0], tRome[1] ).getPlotCity()
                        if not city.isNone():
                                if (city.getOwner() == iRome):
                                        #Italy
                                        self.flipCity(61, tArezzo, 1, 1, iRome, [iEtruria])  
                                        self.flipCity(66, tTaranto, 1, 1, iRome, [iGreekCol])                                        
                                        #1st punic war
                                        self.flipCity(72, tPalemmo, 1, 1, iRome, [iPhoenicia])
                                        self.flipCity(72, tNora, 0, 1, iRome, [iPhoenicia])
                                        self.flipCity(72, tAlalia, 0, 1, iRome, [iPhoenicia])
                                        #2nd punic war
                                        if (self.getPunicFate() >= 30):	# LOQ 2005-10-12
                                                self.flipCity(78, tSiracusa, 1, 1, iRome, [iGreekCol, iPhoenicia])
                                                self.flipCity(79, tGadir, 1, 1, iRome, [iPhoenicia])
                                                #3rd punic war
                                                self.flipCity(91, tCarthage, 1, 1, iRome, [iPhoenicia])
                                                self.flipCity(91, tLeptis, 0, 1, iRome, [iPhoenicia])
                                                self.flipCity(91, tHippo, 0, 1, iRome, [iPhoenicia])
                                        #2nd punic war: alternative (Hannibal wins)
                                        if (self.getPunicFate() < 30) and (pPhoenicia.isAlive()):	# LOQ 2005-10-12
                                                self.flipCity(77, tRome, 1, 1, iPhoenicia, [iRome])
                                                self.flipCity(78, tArezzo, 1, 1, iPhoenicia, [iRome])
                                                self.flipCity(78, tTaranto, 1, 1, iPhoenicia, [iRome])
                                                self.flipCity(79, tPalemmo, 0, 1, iPhoenicia, [iRome])
                                                self.flipCity(79, tNora, 0, 1, iPhoenicia, [iRome])
                                                self.flipCity(79, tAlalia, 0, 1, iPhoenicia, [iRome])
                                        #Celts
                                        self.flipCity(81, tSaguntum, 1, 1, iRome, [iCelts, iPhoenicia])
                                        self.flipCity(82, tAdria, 1, 1, iRome, [iEtruria]) 
                                        self.flipCity(95, tMarseilles, 1, 1, iRome, [iGreekCol, iCelts])
                                        self.flipCity(95, tMilano, 1, 1, iRome, [iCelts, iEtruria])
                                        self.flipCity(110, tGergovia, 1, 1, iRome, [iCelts])
                                        self.flipCity(110, tAlesia, 1, 1, iRome, [iCelts])
                                        self.flipCity(118, tPannonia, 1, 1, iRome, [18, iEtruria, iCelts])
                                        #Roman conquest of Macedonia (only if player is Persia)
                                        if (pMacedonia.isHuman() == 0):
                                                self.flipCity(90, tArgos, 1, 1, iRome, [iMacedonia, iGreece])
                                                self.flipCity(90, tDelphi, 1, 1, iRome, [iMacedonia, iGreece])
                                                self.flipCity(91, tAthens, 1, 1, iRome, [iMacedonia, iGreece])
                                                self.flipCity(91, tSparta, 1, 1, iRome, [iMacedonia, iGreece])
                                                self.flipCity(91, tCorinth, 1, 1, iRome, [iMacedonia, iGreece])
                                                self.flipCity(139, tByzantium, 1, 1, iRome, [iMacedonia, iGreece])
                                        #Roman conquest of Egypt and Middle East
                                        self.flipCity(94, tMiletos, 1, 1, iRome, [iSeleucia, iGreekCol])
                                        self.flipCity(94, tSardis, 1, 1, iRome, [iSeleucia, iGreekCol])
                                        self.flipCity(94, tRhodes, 1, 1, iRome, [iSeleucia, iGreekCol])
                                        self.flipCity(100, tTarsus, 1, 1, iRome, [iSeleucia, iGreekCol])
                                        self.flipCity(105, tCyrene, 1, 1, iRome, [iEgypt, iGreekCol])
                                        self.flipCity(107, tTyre, 1, 1, iRome, [iSeleucia])
                                        self.flipCity(107, tYerushalayim, 1, 1, iRome, [iSeleucia])
                                        self.flipCity(114, tTanis, 1, 1, iRome, [iEgypt])
                                        self.flipCity(114, tMemphis, 1, 1, iRome, [iEgypt])
                                        self.flipCity(114, tHeliopolis, 1, 1, iRome, [iEgypt])
                                        #Roma conquers Persian territories only if Macedonia is the player
                                        if (pPersia.isHuman() == 0):
                                                self.flipCity(94, tMiletos, 1, 1, iRome, [iPersia])
                                                self.flipCity(94, tSardis, 1, 1, iRome, [iPersia])
                                                self.flipCity(94, tRhodes, 1, 1, iRome, [iPersia])
                                                self.flipCity(100, tTarsus, 1, 1, iRome, [iPersia])
                                                self.flipCity(105, tCyrene, 1, 1, iRome, [iPersia])
                                                self.flipCity(107, tTyre, 1, 1, iRome, [iPersia])
                                                self.flipCity(107, tYerushalayim, 1, 1, iRome, [iPersia])
                                                self.flipCity(114, tTanis, 1, 1, iRome, [iPersia])
                                                self.flipCity(114, tMemphis, 1, 1, iRome, [iPersia])
                                                self.flipCity(114, tHeliopolis, 1, 1, iRome, [iPersia])
                                                self.flipCity(139, tByzantium, 1, 1, iRome, [iPersia])


                #Persian events
                if (pPersia.isHuman() == 0):
                        city = gc.getMap().plot( tParsa[0], tParsa[1] ).getPlotCity()
                        if not city.isNone():
                                if (city.getOwner() == iPersia):
                                        #Media, Iran
                                        self.flipCity(9, tEcbatana, 1, 1, iPersia, [18, iIndia])
                                        self.flipCity(9, tGabae, 1, 1, iPersia, [18, iIndia])
                                        self.flipCity(9, tRagha, 1, 1, iPersia, [18, iIndia])
                                        self.flipCity(9, tHasanlu, 1, 1, iPersia, [18, iIndia])
                                        self.flipCity(9, tBactra, 1, 1, iPersia, [18, iIndia])
                                        #Turkey
                                        if (pMacedonia.isHuman() == 0):
                                                self.flipCity(10, tSardis, 1, 1, iPersia, [18, iIndia, iGreekCol, iGreece])
                                                self.flipCity(10, tTrapezus, 1, 1, iPersia, [iGreekCol, iIndia])
                                                self.flipCity(10, tTarsus, 1, 1, iPersia, [18, iIndia, iGreekCol, iGreece])
                                                self.flipCity(10, tMiletos, 0, 1, iPersia, [iGreece])
                                        #Babylon
                                        for cityName in PyPlayer(iBabylon).getCityList():
                                                if not cityName.isNone():
                                                        tCoords = (cityName.GetCy().getX(), cityName.GetCy().getY())
                                                        self.flipCity(12, tCoords, 1, 1, iPersia, [iBabylon])
                                        #Syria
                                        self.flipCity(13, tAleppo, 1, 1, iPersia, [18])
                                        self.flipCity(13, tTyre, 1, 1, iPersia, [18])
                                        #Egypt
                                        if (pMacedonia.isHuman() == 0):
                                                self.flipCity(15, tTanis, 1, 1, iPersia, [iEgypt])
                                                self.flipCity(15, tMemphis, 1, 1, iPersia, [iEgypt])
                                                self.flipCity(15, tHeliopolis, 1, 1, iPersia, [iEgypt])
                                                self.flipCity(15, tThebes, 1, 1, iPersia, [iEgypt])
                                                self.flipCity(15, tCyrene, 1, 1, iPersia, [iEgypt, iGreekCol])
                                        #Darius
                                        self.flipCity(16, tPura, 1, 1, iPersia, [18, iIndia])
                                        self.flipCity(16, tTaxila, 1, 1, iPersia, [iIndia])
                                        self.flipCity(16, tIsmara, 1, 1, iPersia, [18])
                                        if (pMacedonia.isHuman() == 0):
                                                self.flipCity(16, tByzantium, 1, 1, iPersia, [iGreekCol])
                                                #Persian wars
                                                if (self.getPersianFate() >= 30):	# LOQ 2005-10-12
                                                        self.flipCity(24, tMiletos, 0, 1, iGreece, [iPersia])
                                                        #Egypt will be free later
                                                        self.flipCity(39, tTanis, 1, 1, iEgypt, [iPersia])
                                                        self.flipCity(39, tMemphis, 1, 1, iEgypt, [iPersia])
                                                        self.flipCity(39, tHeliopolis, 1, 1, iEgypt, [iPersia])
                                                        self.flipCity(39, tThebes, 1, 1, iEgypt, [iPersia])
                                                        self.flipCity(39, tCyrene, 1, 1, iEgypt, [iPersia])
                                                #Persian wars: alternative (Persia wins)
                                                if (self.getPersianFate() < 30):                       	# LOQ 2005-10-12
                                                        for cityName in PyPlayer(iGreece).getCityList():
                                                                if not cityName.isNone():
                                                                        tCoords = (cityName.GetCy().getX(), cityName.GetCy().getY())
                                                                        self.flipCity(24, tCoords, 1, 1, iPersia, [iGreece])
                                                        self.flipCity(24, tSiracusa, 1, 1, iPhoenicia, [iGreekCol])
                                                        self.flipCity(24, tTrapezus, 1, 1, iGreekCol, [iPersia])
                                                        self.flipCity(24, tTaxila, 1, 1, iIndia, [iPersia])
                                                        self.flipCity(24, tEcbatana, 1, 1, iParthia, [iPersia])
                                        #Parthia
                                        self.flipCity(56, tGabae, 0, 1, iParthia, [iPersia])
                                        self.flipCity(56, tRagha, 0, 1, iParthia, [iPersia])
                                        self.flipCity(56, tHasanlu, 0, 1, iParthia, [iPersia])
                                        self.flipCity(56, tBactra, 0, 1, iParthia, [iPersia])
                                        
                #Macedonian events
                if (pMacedonia.isHuman() == 0):
                        city = gc.getMap().plot( tArgos[0], tArgos[1] ).getPlotCity()
                        if not city.isNone():
                                if (city.getOwner() == iMacedonia):
                                        self.flipCity(51, tIsmara, 1, 1, iMacedonia, [18, iScythia, iGreekCol])
                                        self.flipCity(52, tDelphi, 1, 1, iMacedonia, [iGreece])
                                        self.flipCity(52, tCorinth, 1, 1, iMacedonia, [iGreece])
                                        self.flipCity(52, tSparta, 1, 1, iMacedonia, [iGreece])
                                        self.flipCity(52, tAthens, 1, 1, iMacedonia, [iGreece])
                                        self.flipCity(52, tMiletos, 0, 1, iGreekCol, [iGreece])
                                        self.flipCity(52, tRhodes, 0, 1, iGreekCol, [iGreece])
                                        #Alexander 
                                        self.flipCity(53, tMiletos, 1, 1, iMacedonia, [iGreekCol, iIsrael, iScythia, iBabylon])
                                        self.flipCity(53, tRhodes, 1, 1, iMacedonia, [iGreekCol,iBabylon])
                                        self.flipCity(53, tTarsus, 1, 1, iMacedonia, [18, iGreekCol, iScythia, iIsrael, iParthia, iBabylon])
                                        self.flipCity(53, tSardis, 1, 1, iMacedonia, [18, iGreekCol, iScythia, iIsrael, iParthia, iBabylon])
                                        self.flipCity(53, tAleppo, 1, 1, iMacedonia, [18, iGreekCol, iScythia, iIsrael, iParthia, iBabylon])
                                        self.flipCity(54, tTyre, 1, 1, iMacedonia, [iEgypt, iPhoenicia, iIsrael, iBabylon])
                                        self.flipCity(54, tYerushalayim, 0, 1, iMacedonia, [iIsrael, iBabylon])
                                        self.flipCity(54, tTanis, 0, 1, iMacedonia, [iEgypt, iBabylon])
                                        self.flipCity(54, tMemphis, 0, 1, iMacedonia, [iEgypt, iBabylon])
                                        self.flipCity(54, tHeliopolis, 0, 1, iMacedonia, [iEgypt, iBabylon])
                                        self.flipCity(54, tThebes, 0, 1, iMacedonia, [iEgypt, iBabylon])
                                        self.flipCity(55, tAshur, 0, 1, iMacedonia, [iBabylon, iIsrael])
                                        self.flipCity(55, tBabylon, 0, 1, iMacedonia, [iBabylon, iIsrael])
                                        self.flipCity(55, tSusa, 0, 1, iMacedonia, [iBabylon, iIsrael])
                                        #Alexander attacks Persian territories (only if player is Rome)
                                        if (pPersia.isHuman() == 0):
                                                for cityName in PyPlayer(iPersia).getCityList():
                                                        if not cityName.isNone():
                                                                tCoords = (cityName.GetCy().getX(), cityName.GetCy().getY())
                                                                self.flipCity(55, tCoords, 0, 1, iMacedonia, [iPersia])
                                        if (iGameTurn == 54) or (iGameTurn == 55): #Seleucia spawn
                                                tTopLeft = (45, 32)
                                                tBottomRight = (51, 39)
                                                dummy, plotList = self.squareSearch( tTopLeft, tBottomRight, self.innerInvasion, [] )
                                                rndNum = gc.getGame().getSorenRandNum(len(plotList), 'Greek World - Seleucia')
                                                result = plotList[rndNum]
                                                if (result):
                                                        self.makeUnit(iPhalanx, iSeleucia, result, 4)
                                        #Alexander dies
                                        if (self.getAlexanderFate() >= 30):	# LOQ 2005-10-12
                                                self.flipCity(56, tTrapezus, 0, 1, iGreekCol, [iMacedonia])
                                                self.flipCity(56, tMiletos, 0, 1, iGreekCol, [iMacedonia])
                                                self.flipCity(56, tRhodes, 0, 1, iGreekCol, [iMacedonia])
                                                self.flipCity(56, tSardis, 0, 1, iGreekCol, [iMacedonia])
                                                self.flipCity(56, tTarsus, 0, 1, iSeleucia, [iMacedonia])
                                                self.flipCity(56, tAleppo, 0, 1, iSeleucia, [iMacedonia])
                                                self.flipCity(56, tTyre, 0, 1, iSeleucia, [iMacedonia])
                                                self.flipCity(56, tYerushalayim, 0, 1, iSeleucia, [iMacedonia])
                                                self.flipCity(56, tEcbatana, 0, 1, iSeleucia, [iMacedonia])
                                                self.flipCity(56, tBabylon, 0, 1, iSeleucia, [iMacedonia])
                                                self.flipCity(56, tAshur, 0, 1, iSeleucia, [iMacedonia])
                                                self.flipCity(56, tLarsa, 0, 1, iSeleucia, [iMacedonia])
                                                self.flipCity(56, tNineveh, 0, 1, iSeleucia, [iMacedonia])
                                                self.flipCity(56, tSusa, 0, 1, iSeleucia, [iMacedonia])
                                                self.flipCity(56, tParsa, 0, 1, iSeleucia, [iMacedonia])
                                                #stronger Seleucid empire
                                                if (iGameTurn == 57):
                                                        for cityName in PyPlayer(iSeleucia).getCityList():
                                                                if not cityName.isNone():
                                                                        tCoords = (cityName.GetCy().getX(), cityName.GetCy().getY())
                                                                        self.makeUnit(iPhalanx, iSeleucia, tCoords, 2)
                                                self.flipCity(56, tGabae, 0, 1, iParthia, [iMacedonia])
                                                self.flipCity(56, tRagha, 0, 1, iParthia, [iMacedonia])
                                                self.flipCity(56, tHasanlu, 0, 1, iParthia, [iMacedonia])
                                                self.flipCity(56, tBactra, 0, 1, iIndia, [iMacedonia])
                                                self.flipCity(56, tTaxila, 0, 1, iIndia, [iMacedonia])
                                                self.flipCity(56, tTanis, 0, 1, iEgypt, [iMacedonia])
                                                self.flipCity(56, tMemphis, 0, 1, iEgypt, [iMacedonia])
                                                self.flipCity(56, tHeliopolis, 0, 1, iEgypt, [iMacedonia])
                                                self.flipCity(56, tThebes, 0, 1, iEgypt, [iMacedonia])
                                                self.flipCity(56, tCyrene, 0, 1, iEgypt, [iMacedonia])
                                        #Alexander lives
                                        if (self.getAlexanderFate() < 30):	# LOQ 2005-10-12
                                                self.flipCity(57, tPetra, 1, 1, iMacedonia, [18, iEgypt, iIsrael])
                                                self.flipCity(57, tTayma, 1, 1, iMacedonia, [18, iEgypt, iIsrael])                                            
                                                self.flipCity(57, tMarib, 1, 1, iMacedonia, [18, iEgypt, iIsrael])
                                                self.flipCity(57, tGerrha, 1, 1, iMacedonia, [18, iEgypt, iIsrael])
                                                self.flipCity(59, tGadir, 1, 1, iMacedonia, [iPhoenicia])
                                                if (pRome.isHuman() == 0):
                                                        self.flipCity(58, tSiracusa, 1, 1, iMacedonia, [iPhoenicia, iGreekCol, iRome])
                                                        self.flipCity(58, tPalemmo, 1, 1, iMacedonia, [iPhoenicia, iGreekCol, iRome])
                                                        self.flipCity(59, tGadir, 1, 1, iMacedonia, [iRome]) 
                                                self.flipCity(61, tGabae, 1, 1, iParthia, [iMacedonia])
                                                self.flipCity(61, tRagha, 1, 1, iParthia, [iMacedonia])
                                                self.flipCity(61, tHasanlu, 1, 1, iParthia, [iMacedonia])
                                                self.flipCity(61, tBactra, 1, 1, iIndia, [iMacedonia])
                                                self.flipCity(62, tTaxila, 1, 1, iIndia, [iMacedonia])
                                                self.flipCity(62, tAthens, 1, 1, iGreece, [iMacedonia])
                                                self.flipCity(62, tSparta, 1, 1, iGreece, [iMacedonia])
                                                self.flipCity(62, tDelphi, 1, 1, iGreece, [iMacedonia])
                                                self.flipCity(62, tCorinth, 1, 1, iGreece, [iMacedonia])
                                                self.flipCity(63, tTarsus, 0, 1, iSeleucia, [iMacedonia])
                                                self.flipCity(63, tAleppo, 0, 1, iSeleucia, [iMacedonia])
                                                self.flipCity(63, tTyre, 0, 1, iSeleucia, [iMacedonia])
                                                self.flipCity(63, tYerushalayim, 0, 1, iSeleucia, [iMacedonia])
                                                self.flipCity(63, tPetra, 0, 1, iSeleucia, [iMacedonia])
                                                self.flipCity(63, tTayma, 0, 1, iSeleucia, [iMacedonia])
                                                self.flipCity(63, tMarib, 0, 1, iSeleucia, [iMacedonia])
                                                self.flipCity(63, tGerrha, 0, 1, iSeleucia, [iMacedonia])
                                                if (iGameTurn == 64):
                                                        for cityName in PyPlayer(iSeleucia).getCityList():
                                                                if not cityName.isNone():
                                                                        tCoords = (cityName.GetCy().getX(), cityName.GetCy().getY())
                                                                        self.makeUnit(iPhalanx, iSeleucia, tCoords, 2)
                                        #Parthian expansion
                                        self.flipCity(92, tEcbatana, 1, 1, iParthia, [iSeleucia, iMacedonia])
                                        self.flipCity(92, tBabylon, 1, 1, iParthia, [iSeleucia, iMacedonia])
                                        self.flipCity(92, tAshur, 1, 1, iParthia, [iSeleucia, iMacedonia])
                                        self.flipCity(92, tLarsa, 1, 1, iParthia, [iSeleucia, iMacedonia])
                                        self.flipCity(92, tNineveh, 1, 1, iParthia, [iSeleucia, iMacedonia])
                                        self.flipCity(92, tSusa, 1, 1, iParthia, [iSeleucia, iMacedonia])
                                        self.flipCity(92, tParsa, 1, 1, iParthia, [iSeleucia, iMacedonia])
                                        if (iGameTurn == 93):
                                                for cityName in PyPlayer(iParthia).getCityList():
                                                        if not cityName.isNone():
                                                                tCoords = (cityName.GetCy().getX(), cityName.GetCy().getY())
                                                                self.makeUnit(iHorseArcher, iParthia, tCoords, 2)


                                

		# Christianity by LOQ
		if (iGameTurn == 123):
			city = gc.getMap().plot( tYerushalayim[0], tYerushalayim[1] ).getPlotCity()
			# if Yerushalayim razed
			if city.isNone():
				jewishCityList = []
				for iPlayer in range(iNumPlayers):
					for pyCity in PyPlayer(iPlayer).getCityList():
						if pyCity.GetCy().isHasReligion(iJudaism):
							jewishCityList.append(pyCity.GetCy())
				if jewishCityList:
					iCity = gc.getGame().getSorenRandNum(len(jewishCityList), 'Greek World - Birth of Christianity')
					city = jewishCityList[iCity]
			# if Yerushalayim exists or an alternative is found
			if not city.isNone():
				gc.getGame().setHolyCity(iChristianity, city, True)
                        #Christianity spreads
                        tCoords = (city.getX(), city.getY())
                        if (gc.getPlayer(city.getOwner()).isHuman() == 0):
                                self.makeUnit(iChristianMissionary, city.getOwner(), tCoords, 7)
                                
                #Christianity spreads
		if (iGameTurn >= 130) and (iGameTurn <= 170):
			christianCityList = []
 			for iPlayer in range(iNumPlayers):
				for pyCity in PyPlayer(iPlayer).getCityList():
					if pyCity.GetCy().isHasReligion(iChristianity):
						christianCityList.append(pyCity.GetCy())                              
			if christianCityList:
				iCity = gc.getGame().getSorenRandNum(len(christianCityList), 'Greek World - Spread of Christianity')
				city = christianCityList[iCity]
                                tCoords = (city.getX(), city.getY())
                                if (gc.getPlayer(city.getOwner()).isHuman() == 0):
                                        self.makeUnit(iChristianMissionary, city.getOwner(), tCoords, 1)



        def flipCity(self, iFlipTurn, tCityPlot, bFlipType, bKillUnits, iNewOwner, iOldOwners):
                """Changes owner of city specified by tCityPlot on turn iFlipTurn.
                bFlipType specifies if it's conquered or traded.
                If bKillUnits != 0 all the units in the city will be killed and replaced by two archers.
                iOldOwners is a list. Flip happens only if the old owner is in the list. An empty list will cause the flip to always happen."""
                pNewOwner = gc.getPlayer(iNewOwner)
                if (gc.getGame().getGameTurn() == iFlipTurn):
##                            popup = Popup.PyPopup() 
##                            popup.setBodyString( 'Turn' )
##                            popup.launch()
                            city = gc.getMap().plot( tCityPlot[0], tCityPlot[1] ).getPlotCity()
                            if not city.isNone():
##                                    popup = Popup.PyPopup() 
##                                    popup.setBodyString( 'NoCity' )
##                                    popup.launch()
                                    if (city.getOwner() in iOldOwners or not iOldOwners):
##                                            popup = Popup.PyPopup() 
##                                            popup.setBodyString( 'Owners' )
##                                            popup.launch()
                                            if (bKillUnits):
                                                    killPlot = gc.getMap().plot( tCityPlot[0], tCityPlot[1] )
                                                    for i in range(killPlot.getNumUnits()):
                                                            unit = killPlot.getUnit(0)
                                                            unit.kill(False, iNewOwner)
                                            if (bFlipType): #conquest
                                                    if (city.getPopulation() == 2):
                                                            city.setPopulation(3)
                                                    if (city.getPopulation() == 1):
                                                            city.setPopulation(2)
                                                    pNewOwner.acquireCity(city, True, False)
                                            else: #trade
                                                    pNewOwner.acquireCity(city, False, True)
                                            if (bKillUnits):
                                                    self.makeUnit(iArcher, iNewOwner, tCityPlot, 2)
                                            return True
                return False
                            




	def squareSearch( self, tTopLeft, tBottomRight, function, argsList ): #by LOQ
		"""Searches all tile in the square from tTopLeft to tBottomRight and calls function for
		every tile, passing argsList. The function called must return a tuple: (1) a result, (2) if
		a plot should be painted and (3) if the search should continue."""
		tPaintedList = []
		result = None
		for x in range(tTopLeft[0], tBottomRight[0]):
			for y in range(tTopLeft[1], tBottomRight[1]):
				result, bPaintPlot, bContinueSearch = function((x, y), result, argsList)
				if bPaintPlot:			# paint plot
					tPaintedList.append((x, y))
				if not bContinueSearch:		# goal reached, so stop
					return result, tPaintedList
		return result, tPaintedList


	def innerInvasion( self, tCoords, result, argsList ):
		"""Checks validity of the plot at the current tCoords, returns plot if valid (which stops the search).
		Plot is valid if it's hill or flatlands and it isn't occupied by a unit or city"""
		bPaint = True
		bContinue = True
		pCurrent = gc.getMap().plot( tCoords[0], tCoords[1] )
		if ( pCurrent.isHills() or pCurrent.isFlatlands() ):
			if ( not pCurrent.isCity() and not pCurrent.isUnit() ):
        			# this is a good plot, so paint it and continue search
				return (None, bPaint, bContinue)
		# not a good plot, so don't paint it but continue search
		return (None, not bPaint, bContinue)

	def outerInvasion( self, tCoords, result, argsList ):
		"""Checks validity of the plot at the current tCoords, returns plot if valid (which stops the search).
		Plot is valid if it's hill or flatlands, it isn't occupied by a unit or city and if it isn't a civ's territory"""
		bPaint = True
		bContinue = True
		pCurrent = gc.getMap().plot( tCoords[0], tCoords[1] )
		if ( pCurrent.isHills() or pCurrent.isFlatlands() ):
			if ( not pCurrent.isCity() and not pCurrent.isUnit() ):
				if (pCurrent.countTotalCulture() == 0 ):
					# this is a good plot, so paint it and continue search
					return (None, bPaint, bContinue)
		# not a good plot, so don't paint it but continue search
		return (None, not bPaint, bContinue)

	def innerSeaSpawn( self, tCoords, result, argsList ):
		"""Checks validity of the plot at the current tCoords, returns plot if valid (which stops the search).
		Plot is valid if it's water and it isn't occupied by any unit. Unit check extended to adjacent plots"""
		bPaint = True
		bContinue = True
		pCurrent = gc.getMap().plot( tCoords[0], tCoords[1] )
		if ( pCurrent.isWater()):
			if ( not pCurrent.isCity() and not pCurrent.isUnit() ):
                                iClean = 0
                                for x in range(tCoords[0] - 1, tCoords[0] + 2):		# from x-1 to x+1
                                        for y in range(tCoords[1] - 1, tCoords[1] + 2):	# from y-1 to y+1
                                                if (pCurrent.getNumUnits() != 0):
                                                        iClean += 1
                                if ( iClean == 0 ):   
					# this is a good plot, so paint it and continue search
					return (None, bPaint, bContinue)
		# not a good plot, so don't paint it but continue search
		return (None, not bPaint, bContinue)

	def outerSpawn( self, tCoords, result, argsList ):
		"""Checks validity of the plot at the current tCoords, returns plot if valid (which stops the search).
		Plot is valid if it's hill or flatlands, it isn't occupied by a unit or city and if it isn't a civ's territory.
		Unit check extended to adjacent plots"""
		bPaint = True
		bContinue = True
		pCurrent = gc.getMap().plot( tCoords[0], tCoords[1] )
		if ( pCurrent.isHills() or pCurrent.isFlatlands() ):
			if ( not pCurrent.isCity() and not pCurrent.isUnit() ):
                                iClean = 0
                                for x in range(tCoords[0] - 1, tCoords[0] + 2):		# from x-1 to x+1
                                        for y in range(tCoords[1] - 1, tCoords[1] + 2):	# from y-1 to y+1
                                                if (pCurrent.getNumUnits() != 0):
                                                        iClean += 1
                                if ( iClean == 0 ):
                                        if (pCurrent.countTotalCulture() == 0 ):
                                                # this is a good plot, so paint it and continue search
                                                return (None, bPaint, bContinue)
		# not a good plot, so don't paint it but continue search
		return (None, not bPaint, bContinue)


        def checkCities(self, city, iNewOwner):
                """Renames a city depending on its owner"""
                if city.getName() == 'Taras' and iNewOwner == iRome:
                        city.setName('Tarentum', False)
                if city.getName() == 'Tarentum' and ((iNewOwner == iMacedonia) or (iNewOwner == iGreece) or (iNewOwner == iGreekCol)):
                        city.setName('Taras', False)
                if city.getName() == 'Syrakousai' and iNewOwner == iRome:
                        city.setName('Syracusae', False)
                if city.getName() == 'Syracusae' and ((iNewOwner == iMacedonia) or (iNewOwner == iGreece) or (iNewOwner == iGreekCol)):
                        city.setName('Syrakousai', False)
                if city.getName() == 'Athenai' and iNewOwner == iRome:
                        city.setName('Athanae', False)
                if city.getName() == 'Athanae' and ((iNewOwner == iMacedonia) or (iNewOwner == iGreece) or (iNewOwner == iGreekCol)):
                        city.setName('Athenai', False)
                if city.getName() == 'Miletos' and iNewOwner == iRome:
                        city.setName('Miletus', False)
                if city.getName() == 'Miletus' and ((iNewOwner == iMacedonia) or (iNewOwner == iGreece) or (iNewOwner == iGreekCol)):
                        city.setName('Miletos', False)
                if city.getName() == 'Epidamnos' and iNewOwner == iRome:
                        city.setName('Dyrrachium', False)
                if city.getName() == 'Dyrrachium' and ((iNewOwner == iMacedonia) or (iNewOwner == iGreece) or (iNewOwner == iGreekCol)):
                        city.setName('Epidamnos', False)
                if city.getName() == 'Rhodos' and iNewOwner == iRome:
                        city.setName('Rhodus', False)
                if city.getName() == 'Rhodus' and ((iNewOwner == iMacedonia) or (iNewOwner == iGreece) or (iNewOwner == iGreekCol)):
                        city.setName('Rhodos', False)
                if city.getName() == 'Byzantion' and iNewOwner == iRome:
                        city.setName('Byzantium', False)
                if city.getName() == 'Byzantium' and ((iNewOwner == iMacedonia) or (iNewOwner == iGreece) or (iNewOwner == iGreekCol)):
                        city.setName('Byzantion', False)
                if city.getName() == 'Trapezounda' and iNewOwner == iRome:
                        city.setName('Trapezus', False)
                if city.getName() == 'Trapezus' and ((iNewOwner == iMacedonia) or (iNewOwner == iGreece) or (iNewOwner == iGreekCol)):
                        city.setName('Trapezounda', False)
                if city.getName() == 'Tarsos' and iNewOwner == iRome:
                        city.setName('Tarsus', False)
                if city.getName() == 'Tarsus' and ((iNewOwner == iMacedonia) or (iNewOwner == iGreece) or (iNewOwner == iGreekCol)):
                        city.setName('Tarsos', False)
                if city.getName() == 'Sparte' and iNewOwner == iRome:
                        city.setName('Sparta', False)
                if city.getName() == 'Sparta' and ((iNewOwner == iMacedonia) or (iNewOwner == iGreece) or (iNewOwner == iGreekCol)):
                        city.setName('Sparte', False)
                if city.getName() == 'Korinthos' and iNewOwner == iRome:
                        city.setName('Corinthus', False)
                if city.getName() == 'Corinthus' and ((iNewOwner == iMacedonia) or (iNewOwner == iGreece) or (iNewOwner == iGreekCol)):
                        city.setName('Korinthos', False)
                if city.getName() == 'Delphoi' and iNewOwner == iRome:
                        city.setName('Delphi', False)
                if city.getName() == 'Delphi' and ((iNewOwner == iMacedonia) or (iNewOwner == iGreece) or (iNewOwner == iGreekCol)):
                        city.setName('Delphoi', False)
                if city.getName() == 'Alexandreia' and iNewOwner == iRome:
                        city.setName('Alexandria', False)
                if city.getName() == 'Alexandria' and ((iNewOwner == iMacedonia) or (iNewOwner == iGreece) or (iNewOwner == iGreekCol)):
                        city.setName('Alexandreia', False)
                if city.getName() == 'Alalia' and iNewOwner == iRome:
                        city.setName('Aleria', False)
                if city.getName() == 'Aleria' and ((iNewOwner == iMacedonia) or (iNewOwner == iGreece) or (iNewOwner == iGreekCol)):
                        city.setName('Alalia', False)
                if city.getName() == 'Thasos' and iNewOwner == iRome:
                        city.setName('Thasus', False)
                if city.getName() == 'Thasus' and ((iNewOwner == iMacedonia) or (iNewOwner == iGreece) or (iNewOwner == iGreekCol)):
                        city.setName('Thasos', False)
                if city.getName() == 'Olynthos' and iNewOwner == iRome:
                        city.setName('Olynthus', False)
                if city.getName() == 'Olynthus' and ((iNewOwner == iMacedonia) or (iNewOwner == iGreece) or (iNewOwner == iGreekCol)):
                        city.setName('Olynthos', False)
                if city.getName() == 'Thessaloniki' and iNewOwner == iRome:
                        city.setName('Thessalonica', False)
                if city.getName() == 'Thessalonica' and ((iNewOwner == iMacedonia) or (iNewOwner == iGreece) or (iNewOwner == iGreekCol)):
                        city.setName('Thessaloniki', False)
                if city.getName() == 'Massalia' and iNewOwner == iRome:
                        city.setName('Massilia', False)
                if city.getName() == 'Massilia' and ((iNewOwner == iMacedonia) or (iNewOwner == iGreece) or (iNewOwner == iGreekCol)):
                        city.setName('Massalia', False)

                if city.getName() == 'Roma' and ((iNewOwner == iMacedonia) or (iNewOwner == iGreece) or (iNewOwner == iGreekCol)):
                        city.setName('Rome', False)
                if city.getName() == 'Rome' and iNewOwner == iRome:
                        city.setName('Roma', False)

                        
                if ((city.getName() == 'Sur') or (city.getName() == 'Tyros') or (city.getName() == 'Tsor') or (city.getName() == 'Zara')) and iNewOwner == iRome:
                        city.setName('Tyrus', False)
                if ((city.getName() == 'Tyrus') or (city.getName() == 'Sur') or (city.getName() == 'Tsor') or (city.getName() == 'Zara')) and ((iNewOwner == iMacedonia) or (iNewOwner == iGreece) or (iNewOwner == iGreekCol)):
                        city.setName('Tyros', False)
                if ((city.getName() == 'Tyrus') or (city.getName() == 'Tyros') or (city.getName() == 'Sur') or (city.getName() == 'Zara')) and iNewOwner == iIsrael:
                        city.setName('Tsor', False)
                if ((city.getName() == 'Tyrus') or (city.getName() == 'Tyros') or (city.getName() == 'Tsor') or (city.getName() == 'Sur')) and iNewOwner == iBabylon:
                        city.setName('Zara', False)
                if ((city.getName() == 'Tyrus') or (city.getName() == 'Tyros') or (city.getName() == 'Tsor') or (city.getName() == 'Zara')) and iNewOwner == iPhoenicia:
                        city.setName('Sur', False)
                if ((city.getName() == 'Qart-Hadasht') or (city.getName() == 'Karkhedon')) and iNewOwner == iRome:
                        city.setName('Carthago', False)
                if ((city.getName() == 'Qart-Hadasht') or (city.getName() == 'Carthago')) and ((iNewOwner == iMacedonia) or (iNewOwner == iGreece) or (iNewOwner == iGreekCol)):
                        city.setName('Karkhedon', False)
                if ((city.getName() == 'Carthago') or (city.getName() == 'Karkhedon')) and iNewOwner == iPhoenicia:
                        city.setName('Qart-Hadasht', False)
                if ((city.getName() == 'Lpqy') or (city.getName() == 'Lepcis')) and iNewOwner == iRome:
                        city.setName('Leptis Magna', False)
                if ((city.getName() == 'Lpqy') or (city.getName() == 'Leptis Magna')) and ((iNewOwner == iMacedonia) or (iNewOwner == iGreece) or (iNewOwner == iGreekCol)):
                        city.setName('Lepcis', False)
                if ((city.getName() == 'Leptis Magna') or (city.getName() == 'Lepcis')) and iNewOwner == iPhoenicia:
                        city.setName('Lpqy', False)
                if city.getName() == 'Hippo' and iNewOwner == iRome:
                        city.setName('Hippo Regius', False)
                if city.getName() == 'Hippo Regius' and iNewOwner == iPhoenicia:
                        city.setName('Hippo', False)
                        
                if ((city.getName() == 'Ziz') or (city.getName() == 'Panormos')) and iNewOwner == iRome:
                        city.setName('Panormus', False)
                if ((city.getName() == 'Ziz') or (city.getName() == 'Panormus')) and ((iNewOwner == iMacedonia) or (iNewOwner == iGreece) or (iNewOwner == iGreekCol)):
                        city.setName('Panormos', False)
                if ((city.getName() == 'Panormus') or (city.getName() == 'Panormos')) and iNewOwner == iPhoenicia:
                        city.setName('Ziz', False)
                if city.getName() == 'Gadir' and ((iNewOwner == iMacedonia) or (iNewOwner == iGreece) or (iNewOwner == iGreekCol)):
                        city.setName('Gades', False)
                if city.getName() == 'Gades' and iNewOwner == iPhoenicia:
                        city.setName('Gadir', False)

                if ((city.getName() == 'Yerushalayim') or (city.getName() == 'Hierousalem')) and iNewOwner == iRome:
                        city.setName('Aelia Capitolina', False)
                if ((city.getName() == 'Yerushalayim') or (city.getName() == 'Aelia Capitolina')) and ((iNewOwner == iMacedonia) or (iNewOwner == iGreece) or (iNewOwner == iGreekCol)):
                        city.setName('Hierousalem', False)
                if ((city.getName() == 'Aelia Capitolina') or (city.getName() == 'Hierousalem')) and iNewOwner == iIsrael:
                        city.setName('Yerushalayim', False)

                if city.getName() == 'Hangmatana' and ((iNewOwner == iRome) or (iNewOwner == iMacedonia) or (iNewOwner == iGreece) or (iNewOwner == iGreekCol)):
                        city.setName('Ecbatana', False)
                if city.getName() == 'Ecbatana' and iNewOwner == iPersia:
                        city.setName('Hangmatana', False)

                if city.getName() == 'Parsa' and ((iNewOwner == iRome) or (iNewOwner == iMacedonia) or (iNewOwner == iGreece) or (iNewOwner == iGreekCol)):
                        city.setName('Persepolis', False)
                if city.getName() == 'Persepolis' and iNewOwner == iPersia:
                        city.setName('Parsa', False)
                if city.getName() == 'Pathragada' and ((iNewOwner == iRome) or (iNewOwner == iMacedonia) or (iNewOwner == iGreece) or (iNewOwner == iGreekCol)):
                        city.setName('Pasargadae', False)
                if city.getName() == 'Pasargadae' and iNewOwner == iPersia:
                        city.setName('Pathragada', False)

                if ((city.getName() == 'Niwt-rst') or (city.getName() == 'Thebes')) and iNewOwner == iRome:
                        city.setName('Thebae', False)
                if ((city.getName() == 'Niwt-rst') or (city.getName() == 'Thebae')) and ((iNewOwner == iMacedonia) or (iNewOwner == iGreece) or (iNewOwner == iGreekCol)):
                        city.setName('Thebes', False)
                if ((city.getName() == 'Thebes') or (city.getName() == 'Thebae')) and iNewOwner == iPhoenicia:
                        city.setName('Niwt-rst', False)
                if ((city.getName() == 'Djanet') or (city.getName() == 'Zoan')) and ((iNewOwner == iRome) or (iNewOwner == iMacedonia) or (iNewOwner == iGreece) or (iNewOwner == iGreekCol)):
                        city.setName('Tanis', False)
                if ((city.getName() == 'Djanet') or (city.getName() == 'Tanis')) and iNewOwner == iIsrael:
                        city.setName('Zoan', False)
                if ((city.getName() == 'Tanis') or (city.getName() == 'Zoan')) and iNewOwner == iPhoenicia:
                        city.setName('Niwt-rst', False)
                if city.getName() == 'Ineb Hedj' and ((iNewOwner == iRome) or (iNewOwner == iMacedonia) or (iNewOwner == iGreece) or (iNewOwner == iGreekCol)):
                        city.setName('Memphis', False)
                if city.getName() == 'Memphis' and iNewOwner == iEgypt:
                        city.setName('Ineb Hedj', False)
                if city.getName() == 'Abdju' and ((iNewOwner == iRome) or (iNewOwner == iMacedonia) or (iNewOwner == iGreece) or (iNewOwner == iGreekCol)):
                        city.setName('Abydos', False)
                if city.getName() == 'Abydos' and iNewOwner == iEgypt:
                        city.setName('Abdju', False)
                if city.getName() == 'Iunu' and ((iNewOwner == iRome) or (iNewOwner == iMacedonia) or (iNewOwner == iGreece) or (iNewOwner == iGreekCol)):
                        city.setName('Heliopolis', False)
                if city.getName() == 'Heliopolis' and iNewOwner == iEgypt:
                        city.setName('Iunu', False)
                if city.getName() == 'Yebu' and ((iNewOwner == iRome) or (iNewOwner == iMacedonia) or (iNewOwner == iGreece) or (iNewOwner == iGreekCol)):
                        city.setName('Elephantine', False)
                if city.getName() == 'Elephantine' and iNewOwner == iEgypt:
                        city.setName('Yebu', False)

                if ((city.getName() == 'Babili') or (city.getName() == 'Babel')) and ((iNewOwner == iRome) or (iNewOwner == iMacedonia) or (iNewOwner == iGreece) or (iNewOwner == iGreekCol)):
                        city.setName('Babylon', False)
                if ((city.getName() == 'Babili') or (city.getName() == 'Babylon')) and iNewOwner == iIsrael:
                        city.setName('Babel', False)
                if ((city.getName() == 'Babylon') or (city.getName() == 'Babel')) and iNewOwner == iBabylon:
                        city.setName('Babili', False)
                if ((city.getName() == 'Susan') or (city.getName() == 'Shushan')) and ((iNewOwner == iRome) or (iNewOwner == iMacedonia) or (iNewOwner == iGreece) or (iNewOwner == iGreekCol)):
                        city.setName('Susa', False)
                if ((city.getName() == 'Susan') or (city.getName() == 'Susa')) and iNewOwner == iIsrael:
                        city.setName('Babel', False)
                if ((city.getName() == 'Susa') or (city.getName() == 'Shushan')) and iNewOwner == iBabylon:
                        city.setName('Susan', False)
                if city.getName() == 'Ninua' and iNewOwner == iIsrael:
                        city.setName('Nineveh', False)
                if city.getName() == 'Nineveh' and iNewOwner == iBabylon:
                        city.setName('Ninua', False)
                if city.getName() == 'Assur' and iNewOwner == iIsrael:
                        city.setName('Ashur', False)
                if city.getName() == 'Ashur' and iNewOwner == iBabylon:
                        city.setName('Assur', False)
                if city.getName() == 'Larsa' and iNewOwner == iIsrael:
                        city.setName('Ellasar', False)
                if city.getName() == 'Ellasar' and iNewOwner == iBabylon:
                        city.setName('Larsa', False)

                if city.getName() == 'Richborough' and iNewOwner == iRome:
                        city.setName('Rutupiae', False)
                if city.getName() == 'Rutupiae' and iNewOwner == iCelts:
                        city.setName('Richborough', False)
                if city.getName() == 'Lutetia' and iNewOwner == iRome:
                        city.setName('Lutetia Parisorum', False)
                if city.getName() == 'Lutetia Parisorum' and iNewOwner == iCelts:
                        city.setName('Lutetia', False)
                if city.getName() == 'Melpum' and ((iNewOwner == iRome) or (iNewOwner == iCelts)):
                        city.setName('Mediolanum', False)



     
