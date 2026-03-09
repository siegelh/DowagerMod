# Mesoamerican Scenario
# Civilization 4 (c) 2007 Firaxis Games

# Programmed by Will Miller

from CvPythonExtensions import *
import sys
import Popup as PyPopup
from PyHelpers import *
import pickle
import CvEventManager
from CvScreenEnums import *
from PyHelpers import *
import CvUtil
import CvGameUtils
import CvScreensInterface
import time
import pickle

# Globals
gc = CyGlobalContext()
localText = CyTranslator()

SPANISH_PLAYER = 6

# Some utility functions

def getSurroundingPlots(plot):
		'Returns a list of the surrounding plots'
		result = []
		x = plot.getX() - 1
		y = plot.getY() - 1
		for xPosition in range(x, x + 3):
				for yPosition in range(y, y + 3):
						adjacentPlot = CyMap().plot(xPosition, yPosition)
						if (adjacentPlot is not 0):
								if (not (adjacentPlot.getX() == plot.getX() and adjacentPlot.getY() == plot.getY())):
										result.append(adjacentPlot)
		return result

def randomNumber(low, high):
		#return CyGame().getSorenRandNum(int1, int2)
		if (low > 0):
				return (CyGame().getSorenRandNum(high, "rolling") % low) + low
		else:
				return CyGame().getSorenRandNum(high, "rolling")
				
def randProbability():
		return CyGame().getSorenRandNum(100, "rolling")

# Our epidemic class

class CvMesoamericaEpidemic:

		def __init__(self):
				'Constructor'
				self.infectedUnits = []
				self.infectedCities = []
				self.carriers = []

				# Constants
				self.MAX_CITY_INFECTED_TURNS = 10
				self.MAX_UNIT_INFECTED_TURNS = 10
				self.INFECTION_FROM_INFECTED_PROBABILITY = 20
				self.INFECTION_FROM_CARRIER_PROBABILITY = 15
				#self.INFECTION_FROM_CARRIER_PROBABILITY = 100
				#self.INFECTION_FROM_INFECTED_PROBABILITY = 100
			
		def getInfectedUnits(self):
				'Gets the infected units list'

				return self.infectedUnits

		def getCarriers(self):
				'Gets the carrier units list'

				return self.carriers

		def update(self):
				'Update the epidemic'
				
				# Increment turns
				self.__updateTurnsInfected()
				
				# Inflict damage on infected units
				self.__inflictDamage()

				# Decrease the sickness of our infected cities
				#self.__decreaseSickness()

				# Spread the disease to other units
				self.__spreadDisease()

				# Update our effects
				self.__updateEffects()

		def infectUnit(self, unit):
				'Infect a unit'

				# Check if the unit is already infected
				if (self.__isUnitInfected(unit)):
						return
				
				if (unit.getOwner() < 0 or unit.plot().getX() < 0 or unit.plot().getY() < 0):
						pass
				else:
						if (unit.getUnitType() == CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_WARRIOR')):
								ID = CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_INFECTED_WARRIOR')
						elif (unit.getUnitType() == CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_AZTEC_JAGUAR')):
								ID = CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_AZTEC_INFECTED_JAGUAR')
						elif (unit.getUnitType() == CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_AXEMAN')):
								ID = CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_INFECTED_AXEMAN')
						elif (unit.getUnitType() == CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_MACEMAN')):
								ID = CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_INFECTED_MACEMAN')
						elif (unit.getUnitType() == CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_MAYA_HOLKAN')):
								ID = CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_INFECTED_MAYA_HOLKAN')
						else:
								unitArgs = [unit, 0]
								self.getInfectedUnits().append(unitArgs)
								return
					
						player = PyPlayer(unit.getOwner())
						plot = unit.plot()
						infectedUnit = player.initUnit(ID, plot.getX(), plot.getY(), UnitAITypes.NO_UNITAI)
						
						unitArgs = [infectedUnit, 0]
						
						self.getInfectedUnits().append(unitArgs)
						print("Unit infected:")
						print(unit.getID())
					
						# Transfer promotions
						for i in range(0, gc.getNumPromotionInfos()):
								if (unit.isHasPromotion(i)):
										print("assigned promotion")
										infectedUnit.setHasPromotion(i, true)
						
						print("killed unit")	
						unit.kill(0, player.getID())
						
#						print(unit.isPromotionValid(gc.getInfoTypeForString('PROMOTION_DISEASE')))
#						unit.setHasPromotion(gc.getInfoTypeForString('PROMOTION_DISEASE'))
						
#						unitArgs = [unit, 0]
						

		def infectCity(self, city):
				'Infect a city'

				# Check if the city is already infected
				if (self.__isCityInfected(city)):
						return
				
				cityArgs = [city, 0] # The city and number of turns infected
				self.infectedCities.append(cityArgs)

				city.changeEspionageHealthCounter(3)
				print("City infected!")
				

		def addCarrier(self, player):
				'Specifies a player as a disease carrier.  Carriers are not affected by the disease'
				
				self.carriers.append(player)

		def canUnitInfect(self, unit):
				'Returns 1 if the unit can spread the disease'
			
				# Search our infected units
				for infectedUnit, timeInfected in self.getInfectedUnits():
						if (infectedUnit.getID() == unit.getID()):
								print("unit can infect (infected)")
								return 1

				# Search our carrier players units
				for player in self.getCarriers():
						for infectedUnit in player.getUnitList():
								if (infectedUnit.getID() == unit.getID()):
										print("Unit can infect")
										return 1

				print("Cannot infect")
				return 0
				
		def save(self):
				'Saves our infected units'
				
				# Build a list of our unit IDs
				unitIDs = []
				for unit, timeInfected in self.infectedUnits:
						unitIDs.append([unit.getOwner(), unit.getID(), timeInfected])
				
				# Pickel everything to a string	
				pickledData = pickle.dumps(unitIDs)
				
				# Set our script data.  This gets saved.
				CyGame().setScriptData(pickledData)
				
				
			
		def load(self):
				'Loads our infected units'
				
				# Grab the data from CyGame
				data = CyGame().getScriptData()
				
				unpickledData = pickle.loads(data)
				
				for member in unpickledData:
					print(member)
					if (member[0] < 0):
						print("Player ID is less than zero!!")
					player = gc.getPlayer(member[0])
					self.infectedUnits.append([player.getUnit(member[1]), member[2]])
					
		# private methods

		def __isCityInfected(self, city):
				'Returns true if the city is infected'

				for infectedCity, timeInfected in self.infectedCities:
						if (infectedCity.getID() == city.getID()):
								return 1
				return 0
				
		def __isUnitInfected(self, unit):
				'Returns true if the unit is infected'

				for infectedUnit, timeInfected in self.infectedUnits:
						if (infectedUnit.getID() == unit.getID()):
								return 1
				return 0
				

		def __isUnitCarrier(self, unit):
				'Returns true if the unit is a carrier'
				
				for player in self.carriers:
						if (unit.getOwner() == player.getID()):
								return 1
						else:
								return 0
		
		def __updateTurnsInfected(self):
				'Updates the number of turns infected'
				
				for element in self.infectedUnits:
						element[1] = element[1] + 1

				for element in self.infectedCities:
						element[1] = element[1] + 1

		def __inflictDamage(self):
				'Inflicts damage on infected units'

				print("Inflicting damage")
				i = 0
				print(self.infectedUnits)
#				for unit, turnsInfected in self.infectedUnits:
						# If the unit is dead, remove it from our list                
#						if (unit.isDead() or unit.isNone()):
#								self.infectedUnits.pop(i)
#								i = i + 1
#								print("popped unit")
#								continue
								
						# Clamp damage
#						damage = 40
#						if (unit.getDamage() + damage > 80):
#							print("Clamping damage")
#							damage = 80 - unit.getDamage()
						
#						print("owner")
#						print(unit.getOwner())
#						print("unit damage")
#						print(unit.getDamage())
#						print("damage")
#						print(damage)
#						print("Current HP")
#						print(unit.currHitPoints())
#						print("Max HP")
#						print(unit.maxHitPoints())
#						if (not unit.isNone()):
#							unit.changeDamage(damage, -1)
						
#						i = i + 1
						
				for element in self.infectedUnits:
						unit = element[0]
						turnsInfected = element[1]
						
						# If the unit is dead, remove it from our list        
						try:        
								if (unit.isDead() or unit.isNone() or unit.plot().getX() < 0 or unit.plot().getY() < 0 or unit.getGameTurnCreated() <= 0):
										self.infectedUnits.pop(i)
										i = i + 1
										print("popped unit")
										continue
						except:
								self.infectedUnits.pop(i)
								i = i + 1
								print("popped unit")
								continue
								
						# Clamp damage
						damage = 40
						if (unit.getDamage() + damage > 80):
							print("Clamping damage")
							damage = 80 - unit.getDamage()
						
						print("owner")
						print(unit.getOwner())
						print("unit damage")
						print(unit.getDamage())
						print("damage")
						print(damage)
						print("Current HP")
						print(unit.currHitPoints())
						print("Max HP")
						print(unit.maxHitPoints())
						print("position")
						print(unit.plot().getX())
						print(unit.plot().getY())
						print("game turn created")
						print(unit.getGameTurnCreated())
						if (not unit.isNone()):
							try:
								unit.changeDamage(damage, unit.getOwner())
							except:
								self.infectedUnits.pop(i)
								
						i = i + 1

		def __spreadDisease(self):
				'Spread our disease to other units'

				print("Spreading disease\n")
				# Spread from infected units
				#temp = self.getInfectedUnits();
				temp = []
				for element in self.getInfectedUnits():
						temp.append(element)
				for infectedUnit, turnsInfected in temp:
						try:
								plot = infectedUnit.plot()
								# Infect the plot we're in
								for unitIndex in range(0, plot.getNumUnits()):
										victim = plot.getUnit(unitIndex)
										if (not self.__isUnitCarrier(victim) and not infectedUnit.getID() == victim.getID()):
												if (randProbability() < self.INFECTION_FROM_INFECTED_PROBABILITY):
														self.infectUnit(victim)
								# Infect the surrounding plots
								for adjacentPlot in getSurroundingPlots(plot):
										for unitIndex in range(0, adjacentPlot.getNumUnits()):
												victim = adjacentPlot.getUnit(unitIndex)
												if (not self.__isUnitCarrier(victim)):
														if (randProbability() < self.INFECTION_FROM_INFECTED_PROBABILITY):
																self.infectUnit(victim)
								# Spread to city
								if (plot.isCity()):
										self.infectCity(plot.getPlotCity())
						except:
								pass
								
				# Spread from carrier units
				for player in self.getCarriers():
						for carrierUnit in player.getUnitList():
								try:
										plot = carrierUnit.plot()
										# Infect the plot we're in
										for unitIndex in range(0, plot.getNumUnits()):
												victim = plot.getUnit(unitIndex)
												if (not self.__isUnitCarrier(victim) and not carrierUnit.getID() == victim.getID()):
														if (randProbability() < self.INFECTION_FROM_CARRIER_PROBABILITY):
																self.infectUnit(victim)
										# Infect the surrounding plots
										for adjacentPlot in getSurroundingPlots(plot):
												for unitIndex in range(0, adjacentPlot.getNumUnits()):
														victim = adjacentPlot.getUnit(unitIndex)
														if (not self.__isUnitCarrier(victim) and not carrierUnit.getID() == victim.getID()):
																if (randProbability() < self.INFECTION_FROM_CARRIER_PROBABILITY):
																		self.infectUnit(victim)
								except:
										print("bar")
										pass

				print("Infected Units:")                
				print(self.infectedUnits)
				print("Infected Cities:")
				print(self.infectedCities);

		def __updateEffects(self):
				'Update our effects'
				
#				effect = gc.getInfoTypeForString('EFFECT_CITY_DISEASED')
#				for unitArgs in self.getInfectedUnits():
#						CyEngine().triggerEffect(effect, unitArgs[0].plot().getPoint())



class CvMesoamericaSpanishInvation:
		def __init__(self):
				'Constructor'
				
				self.wave = 0
				
				# We keep a list of our invading ships so that we can
				# update their AI in CvGameUtils
				self.ships = []
				
				self.landingPlots = [CyMap().plot(11, 29),
									CyMap().plot(13, 25),
									CyMap().plot(15, 22),
									CyMap().plot(18, 18),
									CyMap().plot(21, 16),
									CyMap().plot(25, 15),
									CyMap().plot(29, 17),
									CyMap().plot(34, 16),
									CyMap().plot(36, 20),
									CyMap().plot(36, 24),
									CyMap().plot(39, 27),
									CyMap().plot(42, 28),
									CyMap().plot(45, 28),
									CyMap().plot(48, 28),
									CyMap().plot(49, 24),
									CyMap().plot(48, 19),
									CyMap().plot(45, 10)]
				self.spawnPlots = [CyMap().plot(24, 33),
								CyMap().plot(25,33),
								CyMap().plot(25, 33)]

		def update(self):
				'Called every turn'
				turn = CyGame().getGameTurn()
				if (turn == 50 or turn == 70 or turn == 100 or turn == 130):
				#if (turn == 3 or turn == 12 or turn == 24 or turn == 36):
					self.__spawnSpanish()
				
					
		def getShips(self):
				return self.ships

		# Private methods

		def __spawnSpanish(self):
				'Spawns a wave of spanish units'

				spanishPlayer = PyPlayer(SPANISH_PLAYER)

				if (self.wave == 0):
						print("Spawing wave 0")
							
						spawnPlot = self.spawnPlots[0]
						landingPlot = self.landingPlots[randomNumber(0, len(self.landingPlots) - 1) ]
						
						unitIDs = []
						
						unitIDs.append([CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_GALLEON'), UnitAITypes.NO_UNITAI])
						unitIDs.append([CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_SETTLER'), UnitAITypes.NO_UNITAI])
						unitIDs.append([CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_EXPLORER'), UnitAITypes.NO_UNITAI])
						unitIDs.append([CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_EXPLORER'), UnitAITypes.NO_UNITAI])
						
						self.__spawnWave(unitIDs, spawnPlot, landingPlot)
				elif (self.wave == 1):
						print("Spawning wave 1")
						
						spawnPlot = self.spawnPlots[0]
						landingPlot = self.landingPlots[randomNumber(0, len(self.landingPlots) - 1) ]
						
						unitIDs = []
						unitIDs.append([CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_GALLEON'), UnitAITypes.NO_UNITAI])
						unitIDs.append([CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_SPANISH_CONQUISTADOR'), UnitAITypes.NO_UNITAI])
						unitIDs.append([CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_EXPLORER'), UnitAITypes.NO_UNITAI])
						unitIDs.append([CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_SETTLER'), UnitAITypes.NO_UNITAI])
						
						self.__spawnWave(unitIDs, spawnPlot, landingPlot)
				elif (self.wave == 2):
						print("Spawning wave 2")
						
						spawnPlot = self.spawnPlots[0]
						landingPlot = self.landingPlots[randomNumber(0, len(self.landingPlots) - 1) ]
						
						unitIDs = []
						unitIDs.append([CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_GALLEON'), UnitAITypes.NO_UNITAI])
						unitIDs.append([CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_SPANISH_CONQUISTADOR'), UnitAITypes.NO_UNITAI])
						unitIDs.append([CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_EXPLORER'), UnitAITypes.NO_UNITAI])
						unitIDs.append([CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_SETTLER'), UnitAITypes.NO_UNITAI])
						
						self.__spawnWave(unitIDs, spawnPlot, landingPlot)
						
						unitIDs = []
						unitIDs.append([CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_GALLEON'), UnitAITypes.NO_UNITAI])
						unitIDs.append([CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_SPANISH_CONQUISTADOR'), UnitAITypes.NO_UNITAI])
						unitIDs.append([CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_EXPLORER'), UnitAITypes.NO_UNITAI])
						unitIDs.append([CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_SETTLER'), UnitAITypes.NO_UNITAI])
						
						spawnPlot = self.spawnPlots[1]
						landingPlot = self.landingPlots[randomNumber(0, len(self.landingPlots) - 1) ]
						
						self.__spawnWave(unitIDs, spawnPlot, landingPlot)
						
						unitIDs = []
						unitIDs.append([CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_GALLEON'), UnitAITypes.NO_UNITAI])
						unitIDs.append([CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_EXPLORER'), UnitAITypes.NO_UNITAI])
						unitIDs.append([CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_EXPLORER'), UnitAITypes.NO_UNITAI])
						unitIDs.append([CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_SETTLER'), UnitAITypes.NO_UNITAI])
						
						spawnPlot = self.spawnPlots[2]
						landingPlot = self.landingPlots[randomNumber(0, len(self.landingPlots) - 1) ]
						
						self.__spawnWave(unitIDs, spawnPlot, landingPlot)
						
				elif (self.wave == 3):
						print("Spawning wave 3")

						unitIDs = []
						unitIDs.append([CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_GALLEON'), UnitAITypes.NO_UNITAI])
						unitIDs.append([CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_EXPLORER'), UnitAITypes.NO_UNITAI])
						unitIDs.append([CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_SPANISH_CONQUISTADOR'), UnitAITypes.NO_UNITAI])
						unitIDs.append([CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_SETTLER'), UnitAITypes.NO_UNITAI])
						
						spawnPlot = self.spawnPlots[1]
						landingPlot = self.landingPlots[randomNumber(0, len(self.landingPlots) - 1) ]
						
						self.__spawnWave(unitIDs, spawnPlot, landingPlot)
						
						unitIDs = []
						unitIDs.append([CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_GALLEON'), UnitAITypes.NO_UNITAI])
						unitIDs.append([CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_EXPLORER'), UnitAITypes.NO_UNITAI])
						unitIDs.append([CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_SPANISH_CONQUISTADOR'), UnitAITypes.NO_UNITAI])
						unitIDs.append([CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_SETTLER'), UnitAITypes.NO_UNITAI])
						
						spawnPlot = self.spawnPlots[1]
						landingPlot = self.landingPlots[randomNumber(0, len(self.landingPlots) - 1) ]
						
						self.__spawnWave(unitIDs, spawnPlot, landingPlot)
						
						unitIDs = []
						unitIDs.append([CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_GALLEON'), UnitAITypes.NO_UNITAI])
						unitIDs.append([CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_EXPLORER'), UnitAITypes.NO_UNITAI])
						unitIDs.append([CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_EXPLORER'), UnitAITypes.NO_UNITAI])
						unitIDs.append([CvUtil.findInfoTypeNum(gc.getUnitInfo, gc.getNumUnitInfos(), 'UNIT_SETTLER'), UnitAITypes.NO_UNITAI])
						
						spawnPlot = self.spawnPlots[2]
						landingPlot = self.landingPlots[randomNumber(0, len(self.landingPlots) - 1) ]
						
						self.__spawnWave(unitIDs, spawnPlot, landingPlot)

				self.wave = self.wave + 1
				
		def __spawnWave(self, unitIDs, spawnPlot, landingPlot):
				spanishPlayer = PyPlayer(SPANISH_PLAYER)
						
				print(unitIDs)
						
				# Init the units
				units = []
				for element in unitIDs:
						print(element)
						newUnit = spanishPlayer.initUnit(element[0], spawnPlot.getX(), spawnPlot.getY(), element[1])
						print(newUnit)
						units.append(newUnit)
						
				print(units)
							
				# Assuming a ship is our first unit..
				self.ships.append([units[0], landingPlot])
						
				# Push our mission
				units[0].getGroup().pushMission(MissionTypes.MISSION_MOVE_TO, landingPlot.getX(), landingPlot.getY(), 0, False, True, MissionAITypes.NO_MISSIONAI, landingPlot, units[0])
											
				

class CvMesoamericaEvents(CvEventManager.CvEventManager):

		def __init__(self):
				'Constructor'

				# Set our parent.  Alows us to call parent class
				# methods in our overloaded ones.
				self.parent = CvEventManager.CvEventManager
				self.parent.__init__(self)

				# Constants. 
				self.CAPTURE_PROBABILITY = 70
				self.SACRIFICE_CULTURE_MULTIPLIER = 1000
				self.SACRIFICE_HAPPINESS_MULTIPLIER = 1
				self.GOODY_HUT_PROBABILITY = 5

				# Initialize our epidemic and invation objects
				self.epidemic = CvMesoamericaEpidemic()
				self.invation = CvMesoamericaSpanishInvation()
				self.epidemic.addCarrier(PyPlayer(SPANISH_PLAYER))
				
				# The number of times the Spanish have spawned
				self.spanishWaveNumber = 0
				
				# We need this for the capture dup hack
				self.lastUnitCaptured = 0
				
				# We need this for the capture placement hack
				self.attackerPlot = 0
				
				# A list of units we need to spawn at the end of combat
				self.capturedUnits = []
				
		def getInvation(self):
				return self.invation
			
		def getEpidemic(self):
				return self.epidemic
				
		def setAttackerPlot(self, plot):
				self.attackerPlot = plot

		def onModNetMessage(self, argsList):
				'Called whenever CyMessageControl().sendModNetMessage() is called - this is all for you modders!'
				data1, data2, data3, data4, data5 = argsList

				# Handle custom messages

				unitID = data1
				playerID = data2
				message = data3
				
				if (message == 0):
						# Culture ritual
						
						player = gc.getPlayer(playerID)
						unit = player.getUnit(unitID)
			
						culture = unit.baseCombatStr() * self.SACRIFICE_CULTURE_MULTIPLIER
						unit.plot().getPlotCity().changeCultureTimes100(playerID, culture, 0)
			
						# Play an effect
						effect = gc.getInfoTypeForString('EFFECT_CREATION_BIG_FAST')
						CyInterface().playGeneralSoundAtPlot('AS3D_UN_WARR_DEATH_VOX', unit.plot())
						CyEngine().triggerEffect(effect, unit.plot().getPoint())
			
						unit.kill(0, playerID)
						
				if (message == 1):
						# Happiness ritutal
						
						player = gc.getPlayer(playerID)
						unit = player.getUnit(unitID)
			
						happiness = self.SACRIFICE_HAPPINESS_MULTIPLIER
						unit.plot().getPlotCity().changeExtraHappiness(happiness)
			
						# Play an effect
						effect = gc.getInfoTypeForString('EFFECT_CREATION_BIG_FAST')
						CyInterface().playGeneralSoundAtPlot('AS3D_UN_WARR_DEATH_VOX', unit.plot())
						CyEngine().triggerEffect(effect, unit.plot().getPoint())
			
						unit.kill(0, playerID)

		def init(self):
				'Called after our game loads - initializes values from game state'
				
				# Initialize our epidemic and invation objects
				self.epidemic = CvMesoamericaEpidemic()
				self.invation = CvMesoamericaSpanishInvation()
				self.epidemic.addCarrier(PyPlayer(SPANISH_PLAYER))	
														
		def doGoodyHuts(self):
				if (CyGame().isOption(GameOptionTypes.GAMEOPTION_NO_GOODY_HUTS)):
						return
			
				# Randomize goodie huts
				for i in range(0, CyMap().numPlots() - 1):
						goodyHutImprovement = CvUtil.findInfoTypeNum(gc.getImprovementInfo,gc.getNumImprovementInfos(),'IMPROVEMENT_GOODY_HUT')
						
						plot = CyMap().plotByIndex(i);
						if not plot.isUnit() and not plot.isCity() and not plot.isWater() and not plot.isOwned() and not plot.isImpassable():
								numSurroundingHuts = 0
								for surroundingPlot in getSurroundingPlots(plot):
										if surroundingPlot.getImprovementType() == goodyHutImprovement:
												numSurroundingHuts = numSurroundingHuts + 1;
								if (numSurroundingHuts == 0):
										if (randProbability() < self.GOODY_HUT_PROBABILITY):
												plot.setImprovementType(goodyHutImprovement)		
				

		def onLoadGame(self, argsList):
				'Called when the game is loaded.  Overloaded to call our init method'

				# Initialize our data from the now loaded game state
				self.init()
				
				# Load our epidemic state
				self.epidemic.load()

				# Call the parent's method
				self.parent.onLoadGame(self, argsList)
				

		def onGameStart(self, argsList):
				'Called at the start of the game'

				self.parent.onGameStart(self, argsList)
				
				# Initialize our data from the now loaded game state
				self.init()
				
				self.doGoodyHuts()
				
				if not CyGame().isGameMultiPlayer():
						title = localText.getText("TXT_KEY_MESOAMERICA_HINTS_TITLE", ())
						text = localText.getText("TXT_KEY_MESOAMERICA_HINTS", ())
						popup = PyPopup.PyPopup(-1)
						popup.setHeaderString(title)
						popup.setBodyString(text)
						popup.launch(true, PopupStates.POPUPSTATE_IMMEDIATE)

		def onBeginGameTurn(self, argsList):
				'Called at the beginning of each turn'
				
				self.parent.onBeginGameTurn(self, argsList)
				
				gameTurn = argsList[0]

				# Update our epidemic object
				self.epidemic.update()

		def onEndGameTurn(self, argsList):
				'Called at the end of each turn'

				# Update our invation object
				self.invation.update()

		def onBeginPlayerTurn(self, argsList):
				'Called at the beginning of each players turn'

				# Grab data from the argument list
				gameTurn, playerID = argsList
				player = gc.getPlayer(playerID)
										
		def onEndPlayerTurn(Self, argsList):
				'Called at the end of each players turn'

		def onCombatLogCalc(self, argsList):
				'Combat result'

				self.parent.onCombatLogCalc(self, argsList)

		def onCombatLogHit(self, argsList):
				'Combat Message'

				self.parent.onCombatLogHit(self, argsList)

		def onUnitKilled(self, argsList):
				'Unit Killed'

				# Call our base class's method
				self.parent.onUnitKilled(self, argsList)

				# A hack to prevent duplication - this callback is buggy

#				unit, attacker = argsList
#				player = PyPlayer(unit.getOwner())
				#attacker = PyPlayer(attacker)
				
#				if (unit.getID() == self.lastUnitCaptured or unit.plot().isCity() or unit.isAnimal() or unit.getOwner() == SPANISH_PLAYER or attacker == SPANISH_PLAYER or PyPlayer(attacker).isBarbarian()):
#						return
#				else:
#						self.lastUnitCaptured = unit.getID()

#				if (randProbability() < self.CAPTURE_PROBABILITY):
						#newUnit = attacker.initUnit(unit.getUnitType(), unit.getX(), unit.getY(), UnitAITypes.NO_UNITAI)
#						if (self.attackerPlot):
#								self.capturedUnits.append([unit.getUnitType(), self.attackerPlot, attacker])
						
#						print("captured!\n")

		def onCombatResult(self, argsList):
				'Combat result'
				
				winner, loser = argsList
				winnerPlayer = PyPlayer(winner.getOwner())
				loserPlayer = PyPlayer(loser.getOwner())
				
				if (loser.getDamage() < 100):
						return
				
				if (not winnerPlayer or not loserPlayer):
						return
				
				if (loser.plot().isCity() or loser.isAnimal() or loser.getOwner() == SPANISH_PLAYER or winner.getOwner() == SPANISH_PLAYER or winner.isBarbarian() or self.epidemic.canUnitInfect(loser)):
						self.parent.onCombatResult(self, argsList)
						return
						
				if (randProbability() < self.CAPTURE_PROBABILITY):
						if (randProbability() < 50):
								unitType = gc.getInfoTypeForString("UNIT_WARRIOR")
						else:
								unitType = gc.getInfoTypeForString("UNIT_WORKER")
								
						newUnit = winnerPlayer.initUnit(unitType, winner.plot().getX(), winner.plot().getY(), UnitAITypes.NO_UNITAI)
						newUnit.setDamage(randomNumber(30, 90), newUnit.getOwner())
						newUnit.setMoves(0)
				
				
				# Call our base class's method
				self.parent.onCombatResult(self, argsList)   
				
				# Spawn captured units
#				for unitType, plot, player in self.capturedUnits:
#					newUnit = PyPlayer(player).initUnit(unitType, plot.getX(), plot.getY(), UnitAITypes.NO_UNITAI)
#					newUnit.setDamage(randomNumber(30, 90), newUnit.getOwner())
#					newUnit.setMoves(0)
					
#				self.capturedUnits = []
				
		def onPreSave(self, argsList):
				'called before a game is actually saved'
				
				# Call our base class's method
				self.parent.onPreSave(self, argsList)
				
				# Save our epidemic state
				self.epidemic.save()
				
		def onCityBuilt(self, argsList):
				'City Built'
				
				city = argsList[0]
				if (city.getOwner() == SPANISH_PLAYER):
						city.setHasReligion(gc.getInfoTypeForString("RELIGION_CHRISTIANITY"), True, False, False)
				if (city.getOwner() == 0 or city.getOwner() == 1 or city.getOwner() == 2):
						city.setHasReligion(gc.getInfoTypeForString("RELIGION_AZTEC"), True, False, False)
				if (city.getOwner() == 3 or city.getOwner() == 4 or city.getOwner() == 5):
						city.setHasReligion(gc.getInfoTypeForString("RELIGION_MAYAN"), True, False, False)
				
				self.parent.onCityBuilt(self, argsList)
				