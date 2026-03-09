# Rhye's and Fall of Civilization - Barbarian units and cities

from CvPythonExtensions import *
import CvUtil
import PyHelpers        # LOQ
import Popup
import pickle        	# LOQ 2005-10-12
import RFCUtils
import Consts as con

# globals
gc = CyGlobalContext()
PyPlayer = PyHelpers.PyPlayer	# LOQ
utils = RFCUtils.RFCUtils()


### Constants ###

iIndependent = con.iIndependent
iIndependent2 = con.iIndependent2
iNative = con.iNative
iCeltia = con.iCeltia
pIndependent = gc.getPlayer(iIndependent)
pIndependent2 = gc.getPlayer(iIndependent2)
pNative = gc.getPlayer(iNative)
pCeltia = gc.getPlayer(iCeltia)
teamIndependent = gc.getTeam(pIndependent.getTeam())
teamIndependent2 = gc.getTeam(pIndependent2.getTeam())
teamNative = gc.getTeam(pNative.getTeam())
teamCeltia = gc.getTeam(pCeltia.getTeam())

iBarbarian = con.iBarbarian
pBarbarian = gc.getPlayer(iBarbarian)
teamBarbarian = gc.getTeam(pBarbarian.getTeam())
      

# city coordinates, spawn 1st turn and retries
lUr = [77, 38, 0, 0] #3000BC
lJerusalem = [73, 38, 0, 0] #3000BC
lBabylon = [76, 40, 0, 0] #3000BC
lSusa = [79, 40, 0, 0] #3000BC
lTyre = [73, 40, 0, 0] #2700BC #turn10
lKnossos = [69, 39, 13, 0] #2600BC
lHattusas = [73, 43, 34, 0] #2000BC
lSamarkand = [85, 47, 34, 0] #2000BC
lNineveh = [76, 42, 42, 0] #1800BC
lGadir = [51, 40, 70, 0] #1100BC
lLepcis = [61, 37, 70, 0] #1100BC
lCarthage = [58, 39, 82, 0] #814BC
lGordion = [71, 43, 82, 0] #800BC
lPalermo = [60, 40, 86-3, 0] #700BC
lMilan = [59, 47, 86-3, 0] #700BC
lAugsburg = [60, 49, 86-3, 0] 
lRusadir = [54, 38, 88, 0] #650BC
lLyon = [56, 47, 103, 0] #350BC???
#lAxum = [72, 29, 105, 0] #300BC
lBordeaux = [53, 48, 105, 0] #300BC
lCartagena = [54, 42, 109, 0] #230BC
lArtaxata = [77, 44, 111,0] #190BC
lLutetia = [55, 50, 118, 0] #50BC
lSeoul = [109, 46, 119, 0] #25BC
#lTikal = [22, 35, 124, 0] #60AD
lSanaa = [76, 30, 125, 0] #100AD
lPagan = [98, 36, 126, 0] #107AD
lInverness = [52, 60, 141, 0] #400AD
#lChichenItza = [23, 37, 143, 0] #445AD
lLhasa = [96, 43, 154, 0] #633AD
#lAngkor = [102, 34, 171, 0] #802AD
lHanoi = [101, 37, 178, 0] #866AD
lTucume = [24, 26, 181, 0] #900AD
lJelling = [59, 55, 189, 0] #980AD
lDublin = [49, 56, 190, 0] #990AD
lNidaros = [61, 62, 191, 0] #1000AD
lZimbabwe = [69, 15, 191, 0] #1000AD
lQuelimane = [71, 17, 191, 0] #1000AD
lUppsala = [63, 58, 198, 0] #1070AD
lMombasa = [71, 22, 201, 0] #1100AD
lKongo = [62, 20, 248, 0] #1483AD



#handicap level modifier
iHandicapOld = (gc.getGame().getHandicapType() - 1)



class Barbs:

        def makeUnit(self, iUnit, iPlayer, tCoords, iNum, iForceAttack):
                'Makes iNum units for player iPlayer of the type iUnit at tCoords.'
                for i in range(iNum):
                        player = gc.getPlayer(iPlayer)
                        if (iForceAttack == 0):
                                player.initUnit(iUnit, tCoords[0], tCoords[1], UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
                        elif (iForceAttack == 1):
                                player.initUnit(iUnit, tCoords[0], tCoords[1], UnitAITypes.UNITAI_ATTACK, DirectionTypes.DIRECTION_SOUTH)                                  
                        elif (iForceAttack == 2):
                                player.initUnit(iUnit, tCoords[0], tCoords[1], UnitAITypes.UNITAI_ATTACK_SEA, DirectionTypes.DIRECTION_SOUTH)



        	
        def checkTurn(self, iGameTurn):
            
                #handicap level modifier
                iHandicap = (gc.getGame().getHandicapType() - 1)

                #debug
                #if (iGameTurn % 50 == 1):
                #        print ("iHandicap", iHandicap)
                #        print ("iHandicapOld", iHandicapOld)

                if (iGameTurn >= con.i3000BC and iGameTurn <= con.i850BC):
                        if (iHandicap >= 0):
                                self.spawnUnits( iBarbarian, (76, 46), (99, 53), con.iWarrior, 1, iGameTurn, 5, 0, utils.outerInvasion, 0)
                        self.spawnUnits( iBarbarian, (75, 54), (104, 64), con.iWolf, 1, iGameTurn, 5, 2, utils.outerInvasion, 0)
                        self.spawnUnits( iBarbarian, (75, 54), (104, 64), con.iBear, 1, iGameTurn, 5, 4, utils.outerInvasion, 0)
                        self.spawnUnits( iBarbarian, (55, 10), (72, 29), con.iLion, 1, iGameTurn, 4, 1, utils.outerInvasion, 0)
                        self.spawnUnits( iBarbarian, (55, 10), (72, 29), con.iPanther, 1, iGameTurn, 4, 3, utils.outerInvasion, 0)

                        
                #celts
                if (iGameTurn >= con.i650BC and iGameTurn <= con.i110BC):
                        self.spawnUnits( iCeltia, (49, 46), (65, 52), con.iCelticGallicWarrior, 1, iGameTurn, 8, 0, utils.outerInvasion, 0)
                        if (iHandicap >= 0):
                                self.spawnUnits( iCeltia, (49, 46), (65, 52), con.iAxeman, 1, iGameTurn, 10, 6, utils.outerInvasion, 0)  

                #norse
                if (iGameTurn >= con.i650BC and iGameTurn <= con.i550AD):
                        self.spawnUnits( iCeltia, (50, 49), (61, 61), con.iGalley, 1, iGameTurn, 30, 0, utils.outerSeaSpawn, 2)
                        
                #mongolia
                if (iGameTurn >= con.i210BC and iGameTurn <= con.i900AD):
                        self.spawnUnits( iBarbarian, (91, 50), (107, 54), con.iHorseArcher, 3 + iHandicap*2, iGameTurn, 10, 0, utils.outerInvasion, 0)
                if (iGameTurn > con.i900AD and iGameTurn <= con.i1100AD):
                        self.spawnUnits( iBarbarian, (91, 50), (107, 54), con.iHorseArcher, 2 + iHandicap, iGameTurn, 6, 0, utils.outerInvasion, 0)
                        
                #tibet
                if (iGameTurn >= con.i350BC and iGameTurn <= con.i1100AD):
                        self.spawnUnits( iBarbarian, (92, 41), (99, 45), con.iSwordsman, 1 + iHandicap, iGameTurn, 10-iHandicap, 3, utils.outerInvasion, 0)

                #elephants in india pre-khmer
                if (iGameTurn >= con.i650BC and iGameTurn <= con.i300AD):
                        self.spawnUnits( iBarbarian, (86, 31), (100, 41), con.iWarElephant, 1, iGameTurn, 10-iHandicap, 4, utils.outerInvasion, 0)
       
                        
                #pirates in Mediterranean
                if (iGameTurn >= con.i210BC and iGameTurn <= con.i50AD):
                        self.spawnUnits( iBarbarian, (49, 37), (72, 44), con.iTrireme, 1, iGameTurn, 8, 0, utils.outerSeaSpawn, 2)
                        
                #barbarians in europe
                if (iGameTurn >= con.i10BC and iGameTurn <= con.i550AD):
                        self.spawnUnits( iBarbarian, (49, 41), (56, 52), con.iAxeman, 3 + iHandicap, iGameTurn, 8, 4, utils.outerInvasion, 0)
                        self.spawnUnits( iBarbarian, (57, 45), (63, 63), con.iAxeman, 2 + iHandicap, iGameTurn, 7, 0, utils.outerInvasion, 0)
                        self.spawnUnits( iBarbarian, (64, 49), (69, 56), con.iAxeman, 3 + iHandicap, iGameTurn, 8, 8, utils.outerInvasion, 0)
                        self.spawnUnits( iBarbarian, (49, 41), (57, 52), con.iSwordsman, 4 + iHandicap*2, iGameTurn, 8, 7, utils.outerInvasion, 0)
                        self.spawnUnits( iBarbarian, (58, 45), (70, 60), con.iSwordsman, 4 + iHandicap, iGameTurn, 8, 3, utils.outerInvasion, 0)                       
                if (iGameTurn >= con.i300AD and iGameTurn <= con.i690AD): #late start condition removed
                        self.spawnUnits( iBarbarian, (58, 50), (88, 54), con.iHorseArcher, 3 + iHandicap, iGameTurn, 4, 1, utils.outerInvasion, 0)

                #last barbarians in east europe and caucasus
                if (iGameTurn >= con.i690AD and iGameTurn <= con.i1100AD):
                        if (gc.getPlayer(0).isPlayable()):  #late start condition
                                self.spawnUnits( iBarbarian, (67, 45), (79, 50), con.iHorseArcher, 3 + iHandicap, iGameTurn, 6, 0, utils.outerInvasion, 0)

                #barbarians in central asia
                if (iGameTurn >= con.i210BC and iGameTurn <= con.i860AD):
                        self.spawnUnits( iBarbarian, (78, 42), (88, 50), con.iHorseArcher, 3 + iHandicap, iGameTurn, 6-iHandicap, 2, utils.outerInvasion, 0)
                if (iGameTurn > con.i860AD and iGameTurn <= con.i1100AD):
                        self.spawnUnits( iBarbarian, (78, 42), (88, 50), con.iHorseArcher, 2 + iHandicap, iGameTurn, 6-iHandicap, 2, utils.outerInvasion, 0)
                        
                #barbarians in north africa
                if (iGameTurn >= con.i190AD and iGameTurn <= con.i900AD):
                        self.spawnUnits( iBarbarian, (56, 29), (78, 33), con.iHorseArcher, 2 + iHandicap, iGameTurn, 5-iHandicap, 4, utils.outerInvasion, 0)
                        self.spawnUnits( iBarbarian, (57, 29), (78, 33), con.iCamelArcher, 2 + iHandicap, iGameTurn, 5, 0, utils.outerInvasion, 0)
                if (iGameTurn >= con.i900AD and iGameTurn <= con.i1800AD):
                        self.spawnUnits( iBarbarian, (53, 27), (67, 35), con.iCamelArcher, 1, iGameTurn, 9-iHandicap, 4, utils.outerInvasion, 0)
                        
                #camels in arabia
                if (iGameTurn >= con.i10BC and iGameTurn <= con.i550AD):
                        self.spawnUnits( iBarbarian, (73, 30), (82, 36), con.iCamelArcher, 1, iGameTurn, 9-iHandicap, 4, utils.outerInvasion, 0)

                #African natives
                if (gc.getPlayer(0).isPlayable()):  #late start condition
                        if (iGameTurn >= con.i50AD and iGameTurn <= con.i690AD):
                                self.spawnUnits( iNative, (58, 24), (72, 31), con.iZuluImpi, 3 + iHandicap, iGameTurn, 6, 4, utils.outerInvasion, 1)
                if (iGameTurn >= con.i450AD and iGameTurn <= con.i1700AD):
                        if (gc.getPlayer(0).isPlayable()):  #late start condition
                                self.spawnUnits( iNative, (60, 10), (72, 23), con.iZuluImpi, 3 + iHandicap, iGameTurn, 7, 4, utils.outerInvasion, 1)
                        else:
                                self.spawnUnits( iNative, (60, 10), (72, 23), con.iZuluImpi, 1, iGameTurn, 15, 4, utils.outerInvasion, 1)
                #west africa
                if (iGameTurn >= con.i450AD and iGameTurn <= con.i1700AD):
                        self.spawnUnits( iBarbarian, (48, 26), (65, 37), con.iWarElephant, 2, iGameTurn, 14, 4, utils.outerInvasion, 1)

                #American natives
                if (iGameTurn >= con.i600AD and iGameTurn <= con.i1100AD):
                        self.spawnUnits( iBarbarian, (15, 38), (24, 47), con.iNativeAmericaDogSoldier, 3 + iHandicap, iGameTurn, 14, 0, utils.outerInvasion, 1)
                        self.spawnUnits( iBarbarian, (15, 38), (24, 47), con.iAztecJaguar, 3 + iHandicap, iGameTurn, 14, 7, utils.outerInvasion, 0)
                if (iGameTurn >= con.i1300AD and iGameTurn <= con.i1600AD):
                        self.spawnUnits( iBarbarian, (15, 38), (24, 47), con.iNativeAmericaDogSoldier, 3 + iHandicap, iGameTurn, 7, 0, utils.outerInvasion, 1)
                if (iGameTurn >= con.i1400AD and iGameTurn <= con.i1800AD):
                        self.spawnUnits( iNative, (11, 44), (33, 51), con.iNativeAmericaDogSoldier, 3 + iHandicap, iGameTurn, 8, 0, utils.outerInvasion, 1)
                        self.spawnUnits( iNative, (11, 44), (33, 51), con.iNativeAmericaDogSoldier, 3 + iHandicap, iGameTurn, 8, 4, utils.outerInvasion, 1)
                if (iGameTurn >= con.i1300AD and iGameTurn <= con.i1600AD):
                        if (iGameTurn % 16 == 0):
                                if (gc.getMap().plot(27, 29).getNumUnits() == 0):
                                        self.makeUnit(con.iNativeAmericaDogSoldier, iBarbarian, (27, 29), 3 + iHandicap, 1)
                        if (iGameTurn % 16 == 8):
                                if (gc.getMap().plot(30, 13).getNumUnits() == 0):
                                        self.makeUnit(con.iNativeAmericaDogSoldier, iBarbarian, (30, 13), 3 + iHandicap, 1)
                        
                #pirates in the Caribbean
                if (iGameTurn >= con.i1600AD and iGameTurn <= con.i1800AD):
                        self.spawnUnits( iBarbarian, (24, 32), (35, 46), con.iPrivateer, 1, iGameTurn, 5, 0, utils.outerSeaSpawn, 0)



                #self.foundCity(iIndependent, lUr, "Ur", iGameTurn, 1, con.iWarrior, 1)
                self.foundCity(iIndependent2, lTyre, "Sur", iGameTurn, 1, con.iArcher, 1)
                self.foundCity(iIndependent, lJerusalem, "Yerushalayim", iGameTurn, 2, con.iArcher, 3)                        
                #self.foundCity(lBabylon, "Babel", iGameTurn, 1, con.iArcher, 1)
                self.foundCity(iIndependent2, lSusa, "Shushan", iGameTurn, 1, con.iArcher, 1)
                #self.foundCity(lKnossos, "Knossos", iGameTurn, 1, con.iWarrior, 0)                
                self.foundCity(iBarbarian, lHattusas, "Hattusas", iGameTurn, 1, con.iChariot, 2)
                self.foundCity(iIndependent, lSamarkand, "Afrosiab", iGameTurn, 1, -1, -1)
                #self.foundCity(iBarbarian, lNineveh, "Nineveh", iGameTurn, 1, -1, -1)
                #self.foundCity(lGadir, "Qart-Gadir", iGameTurn, 1, -1, -1)
                #self.foundCity(lLepcis, "Lpqy", iGameTurn, 2, -1, -1)
                #self.foundCity(lCarthage, "Qart-Hadasht", iGameTurn, 2, -1, -1)
                self.foundCity(iBarbarian, lGordion, "Gordion", iGameTurn, 1, con.iChariot, 1)
                #self.foundCity(lPalermo, "Ziz", iGameTurn, 2, con.iArcher, 1)
                self.foundCity(iCeltia, lMilan, "Melpum", iGameTurn, 2, con.iArcher, 2)
                #self.foundCity(iBarbarian, lAugsburg, "Damasia", iGameTurn, 1, -1, -1)
                #self.foundCity(lRusadir, "Rusadir", iGameTurn, 2, -1, -1)
                self.foundCity(iCeltia, lLyon, "Lugodunon", iGameTurn, 2, -1, -1)
                #self.foundCity(iIndependent, lAxum, "Axum", iGameTurn, 1, -1, -1)
                self.foundCity(iCeltia, lBordeaux, "Burdigala", iGameTurn, 2, -1, -1)
                #self.foundCity(lCartagena, "Qart Hadasht", iGameTurn, 1, -1, -1)
                self.foundCity(iIndependent, lSeoul, "Seoul", iGameTurn, 2, -1, -1)
                self.foundCity(iIndependent2, lArtaxata, "Artashat", iGameTurn, 1, -1, -1)
                self.foundCity(iCeltia, lLutetia, "Lutetia", iGameTurn, 2, -1, -1)
                #self.foundCity(iNative, lTikal, "Tikal", iGameTurn, 1, -1, -1)
                self.foundCity(iIndependent, lSanaa, "Sana'a", iGameTurn, 1, -1, -1)
                self.foundCity(iIndependent2, lPagan, "Pagan", iGameTurn, 2, -1, -1)
                self.foundCity(iCeltia, lInverness, "Inbhir Nis", iGameTurn, 2, -1, -1)
                #self.foundCity(iNative, lChichenItza, "Chichen Itza", iGameTurn, 1, -1, -1)
                bLhasaResult = self.foundCity(iBarbarian, lLhasa, "Lhasa", iGameTurn, 2, -1, -1)
                if (bLhasaResult == False):
                        self.foundCity(iBarbarian, (lLhasa[0] - 1, lLhasa[1] - 1, lLhasa[2], lLhasa[3]), "Lhasa", iGameTurn, 2, -1, -1) #try to found it nearby
                #self.foundCity(iIndependent2, lAngkor, "Angkor", iGameTurn, 1, -1, -1)
                self.foundCity(iBarbarian, lHanoi, "Hanoi", iGameTurn, 2, -1, -1)
                self.foundCity(iNative, lTucume, "Tucume", iGameTurn, 1, -1, -1)
                #self.foundCity(lJelling, "Jelling", iGameTurn, 1, -1, -1)
                if (gc.getPlayer(0).isPlayable()):  #late start condition
                        self.foundCity(iCeltia, lDublin, "&#193;th Cliath", iGameTurn, 1, -1, -1)
                else:
                        self.foundCity(iIndependent, lDublin, "&#193;th Cliath", iGameTurn, 1, -1, -1)
                #self.foundCity(lNidaros, "Nidaros", iGameTurn, 1, -1, -1)
                #self.foundCity(iNative, lZimbabwe, "Zimbabwe", iGameTurn, 1, con.iZuluImpi, 1)
                self.foundCity(iNative, lQuelimane, "Quelimane", iGameTurn, 1, con.iZuluImpi, 1)
                #self.foundCity(lUppsala, "Upsala", iGameTurn, 1, -1, -1)
                self.foundCity(iNative, lMombasa, "Mombasa", iGameTurn, 1, con.iZuluImpi, 1)
                self.foundCity(iNative, lKongo, "Mbanza Kongo", iGameTurn, 1, con.iZuluImpi, 1)



        def getCity(self, tCoords): #by LOQ
                'Returns a city at coordinates tCoords.'
                return CyGlobalContext().getMap().plot(tCoords[0], tCoords[1]).getPlotCity()

        def foundCity(self, iCiv, lCity, name, iTurn, iPopulation, iUnitType, iNumUnits):
                if ((iTurn == lCity[2] + lCity[3]) and (lCity[3]<10)):
                        #print self.checkRegion(tUr)
                        bResult, lCity[3] = self.checkRegion(lCity)
                        if (bResult == True):
                                pCiv = gc.getPlayer(iCiv)
                                pCiv.found(lCity[0], lCity[1])
                                self.getCity((lCity[0], lCity[1])).setName(name, False)
                                if (iPopulation != 1):
                                        self.getCity((lCity[0], lCity[1])).setPopulation(iPopulation)
                                if (iNumUnits > 0):
                                        self.makeUnit(iUnitType, iCiv, (lCity[0], lCity[1]), iNumUnits, 0)
                                return True
                        if (bResult == False) and (lCity[3] == -1):
                                return False
                               

        def checkRegion(self, tCity):
                cityPlot = gc.getMap().plot(tCity[0], tCity[1])
##                iNumUnitsInAPlot = cityPlot.getNumUnits()
##                print iNumUnitsInAPlot
                
                #checks if the plot already belongs to someone
                if (cityPlot.isOwned()):
                        if (cityPlot.getOwner() != iBarbarian ):
                                return (False, -1)
                    
##                #checks if there's a unit on the plot
##                if (iNumUnitsInAPlot):
##                        for i in range(iNumUnitsInAPlot):
##                                unit = currentPlot.getUnit(i)
##                                iOwner = unit.getOwner()
##                                pOwner = gc.getPlayer(iOwner)
##                                if (pOwner.isHuman()):
##                                        return (False, tCity[3]+1)                    

                #checks the surroundings and allows only AI units
                for x in range(tCity[0]-1, tCity[0]+2):
                        for y in range(tCity[1]-1, tCity[1]+2):
                                currentPlot=gc.getMap().plot(x,y)
                                if (currentPlot.isCity()):
                                        return (False, -1)                                
                                iNumUnitsInAPlot = currentPlot.getNumUnits()
                                if (iNumUnitsInAPlot):
                                        for i in range(iNumUnitsInAPlot):
                                                unit = currentPlot.getUnit(i)
                                                iOwner = unit.getOwner()
                                                pOwner = gc.getPlayer(iOwner)
                                                if (pOwner.isHuman()):
                                                        return (False, tCity[3]+1)
                return (True, tCity[3])



        def spawnUnits(self, iCiv, tTopLeft, tBottomRight, iUnitType, iNumUnits, iTurn, iPeriod, iRest, function, iForceAttack):
                if (iTurn % iPeriod == iRest):
                        dummy, plotList = utils.squareSearch( tTopLeft, tBottomRight, function, [] )
                        if (len(plotList)):
                                rndNum = gc.getGame().getSorenRandNum(len(plotList), 'Spawn units')
                                result = plotList[rndNum]
                                if (result):
                                        self.makeUnit(iUnitType, iCiv, result, iNumUnits, iForceAttack)
                                


	    
        def killNeighbours(self, tCoords):
                'Kills all units in the neigbbouring tiles of plot (as well as plot itself) so late starters have some space.'
                for x in range(tCoords[0]-1, tCoords[0]+2):        # from x-1 to x+1
                        for y in range(tCoords[1]-1, tCoords[1]+2):	# from y-1 to y+1
                                killPlot = CyMap().getPlot(x, y)
                                for i in range(killPlot.getNumUnits()):
                                        unit = killPlot.getUnit(0)	# 0 instead of i because killing units changes the indices
                                        unit.kill(False, iBarbarian)

