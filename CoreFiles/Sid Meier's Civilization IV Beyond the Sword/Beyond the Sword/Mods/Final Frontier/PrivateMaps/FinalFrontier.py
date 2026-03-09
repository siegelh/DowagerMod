#
#	FILE:	 Final_Frontier_Standard.py
#	AUTHOR:  Bob Thomas, Jon Shafer
#	PURPOSE: Final Frontier mod's default map script
#-----------------------------------------------------------------------------
#	Copyright (c) 2004, 2005 Firaxis Games, Inc. All rights reserved.
#-----------------------------------------------------------------------------
#

from CvPythonExtensions import *
import CvUtil
import CvMapGeneratorUtil
import random
import sys
from CvMapGeneratorUtil import FractalWorld
from CvMapGeneratorUtil import TerrainGenerator
from CvMapGeneratorUtil import FeatureGenerator

g_apSolarSystemPlotList = []
g_aiPickedPlotForPlayer = []

def getDescription():
	return "TXT_KEY_FINAL_FRONTIER_INTRO"
	
def isAdvancedMap():
	"This map should show up in simple mode"
	return 0

def getNumCustomMapOptions():
	return 3
	
def getCustomMapOptionName(argsList):
	[iOption] = argsList
	option_names = {
		0:	"TXT_KEY_FF_MAP_NUM_STAR_SYSTEMS",
		1:	"TXT_KEY_FF_MAP_NUM_FEATURES",
		2:	"TXT_KEY_FF_MAP_NUM_HOSTILE_FEATURES"
		}
	translated_text = unicode(CyTranslator().getText(option_names[iOption], ()))
	return translated_text
	
def getNumCustomMapOptionValues(argsList):
	[iOption] = argsList
	option_values = {
		0:	4,
		1:	4,
		2:	4
		}
	return option_values[iOption]
	
def getCustomMapOptionDescAt(argsList):
	[iOption, iSelection] = argsList
	selection_names = {
		0:	{
			0: "TXT_KEY_FF_MAP_NUM_VERY_DENSE",
			1: "TXT_KEY_FF_MAP_NUM_MANY",
			2: "TXT_KEY_FF_MAP_NUM_NORMAL",
			3: "TXT_KEY_FF_MAP_NUM_FEW"
			},
		1:	{
			0: "TXT_KEY_FF_MAP_NUM_VERY_DENSE",
			1: "TXT_KEY_FF_MAP_NUM_MANY",
			2: "TXT_KEY_FF_MAP_NUM_NORMAL",
			3: "TXT_KEY_FF_MAP_NUM_FEW"
			},
		2:	{
			0: "TXT_KEY_FF_MAP_NUM_VERY_DENSE",
			1: "TXT_KEY_FF_MAP_NUM_MANY",
			2: "TXT_KEY_FF_MAP_NUM_NORMAL",
			3: "TXT_KEY_FF_MAP_NUM_FEW"
			}
		}
	translated_text = unicode(CyTranslator().getText(selection_names[iOption][iSelection], ()))
	return translated_text
	
def getCustomMapOptionDefault(argsList):
	[iOption] = argsList
	option_defaults = {
		0:	2,
		1:	2,
		2:	2
		}
	return option_defaults[iOption]

#def getNumHiddenCustomMapOptions():
#	return 0

def isClimateMap():
	return 0

def isSeaLevelMap():
	return 0

def getWrapX():
	return True
def getWrapY():
	return True

def getGridSize(argsList):
	# Jon: the grid blocks are 4x4 plots each.
	# Set the values below to horizontal/vertical counts of blocks for each map size.
	# The values shown currently are the same as in the Pangaea script.
	grid_sizes = {
		WorldSizeTypes.WORLDSIZE_DUEL:		(10,6),#(8,5),
		WorldSizeTypes.WORLDSIZE_TINY:		(13,8),
		WorldSizeTypes.WORLDSIZE_SMALL:		(16,10),
		WorldSizeTypes.WORLDSIZE_STANDARD:	(21,13),
		WorldSizeTypes.WORLDSIZE_LARGE:		(26,16),
		WorldSizeTypes.WORLDSIZE_HUGE:		(32,20)
	}

	if (argsList[0] == -1): # (-1,) is passed to function on loads
		return []
	[eWorldSize] = argsList
	return grid_sizes[eWorldSize]


# Subclass
class FinalFrontierPlotTypes(CvMapGeneratorUtil.FractalWorld):
	def generatePlotTypes(self, shift_plot_types=True, 
	                      grain_amount=3):
		for x in range(self.iNumPlotsX):
			for y in range(self.iNumPlotsY):
				i = y*self.iNumPlotsX + x
				self.plotTypes[i] = 2

		return self.plotTypes

def generatePlotTypes():
	# All Plots are PlotType 2
	NiTextOut("Setting Plot Types (Python Final Frontier Standard) ...")
	global space
	space = FinalFrontierPlotTypes()
	plot_types = space.generatePlotTypes()
	return plot_types


# Subclass
class FinalFrontierTerrainTypes(CvMapGeneratorUtil.TerrainGenerator):
	def __init__(self, fracXExp=-1, fracYExp=-1):
		self.gc = CyGlobalContext()
		self.map = CyMap()

		self.iWidth = self.map.getGridWidth()
		self.iHeight = self.map.getGridHeight()

		self.terrainTundra = self.gc.getInfoTypeForString("TERRAIN_TUNDRA")

	def generateTerrainAtPlot(self,iX,iY):
		terrainVal = self.terrainTundra
		return terrainVal

def generateTerrainTypes():
	# All Terrain types are "TERRAIN_TUNDRA"
	NiTextOut("Generating Terrain (Python FinalFrontierTerrainTypes) ...")
	terraingen = FinalFrontierTerrainTypes()
	terrainTypes = terraingen.generateTerrain()
	return terrainTypes

class FinalFrontierFeatureGenerator(CvMapGeneratorUtil.FeatureGenerator):
	def __init__(self, fracXExp=-1, fracYExp=-1):
		self.gc = CyGlobalContext()
		self.map = CyMap()
		self.mapRand = self.gc.getGame().getMapRand()
		self.nebula = CyFractal()
		self.asteroids = CyFractal()
		self.radiation = CyFractal()
		self.iFlags = 0
		self.iGridW = self.map.getGridWidth()
		self.iGridH = self.map.getGridHeight()
		
		# Grain settings affect the fractalized shape of feature clusters.
		#
		self.nebula_grain = 2
		self.asteroid_grain = 4
		self.radiation_grain = 3

		self.fracXExp = fracXExp
		self.fracYExp = fracYExp

		self.__initFractals()
		self.__initFeatureTypes()
	
	def __initFractals(self):
		self.nebula.fracInit(self.iGridW+1, self.iGridH+1, self.nebula_grain, self.mapRand, self.iFlags, self.fracXExp, self.fracYExp)
		self.asteroids.fracInit(self.iGridW+1, self.iGridH+1, self.asteroid_grain, self.mapRand, self.iFlags, self.fracXExp, self.fracYExp)
		self.radiation.fracInit(self.iGridW+1, self.iGridH+1, self.radiation_grain, self.mapRand, self.iFlags, self.fracXExp, self.fracYExp)
		
		iFeatureDensity = self.map.getCustomMapOption(1)
		iFeatureDensityMod = 0
		if (iFeatureDensity == 0):	# Very High density, make things closer together
			iFeatureDensityMod = -8
		elif (iFeatureDensity == 1):	# High density, make things closer together
			iFeatureDensityMod = 0
		elif (iFeatureDensity == 2):	# Normal density
			iFeatureDensityMod = 5
		elif (iFeatureDensity == 3):	# Low density, make things farther apart
			iFeatureDensityMod = 8
		
		# These values control Nebula quantity.
		# Top needs to stay at 100 to prevent holes in the middle of nebulae.
		# Adjust bottom value to increase or reduce amount (%) of map dedicated to Nebulae.
		self.iNebulaTop = self.nebula.getHeightFromPercent(100)
#		self.iNebulaBottom = self.nebula.getHeightFromPercent(90)
		self.iNebulaBottom = self.nebula.getHeightFromPercent(85 + iFeatureDensityMod)
		
		# These values control Asteroid quantity.
		# Top needs to stay at 100 to prevent holes in the middle of Asteroid clusters.
		# Adjust bottom value to increase or reduce amount (%) of map dedicated to Asteroids.
		self.iAsteroidsTop = self.asteroids.getHeightFromPercent(100)
#		self.iAsteroidsBottom = self.asteroids.getHeightFromPercent(88)
		self.iAsteroidsBottom = self.asteroids.getHeightFromPercent(80 + iFeatureDensityMod)

		# These values control Radiation quantity.
		# Main controls the large clusters and works like Bottom for the other two.
		# Top and Bottom are taking a snaky slice out of the middle of the fractal, which--
		# --adds in scattered small patches and dots between the larger groups.
		self.iRadiationTop = self.radiation.getHeightFromPercent(40)
		self.iRadiationBottom = self.radiation.getHeightFromPercent(37)
#		self.iRadiationMain = self.radiation.getHeightFromPercent(94)
		self.iRadiationMain = self.radiation.getHeightFromPercent(87 + iFeatureDensityMod)
		
	def __initFeatureTypes(self):
		self.featureSolarSystem = self.gc.getInfoTypeForString("FEATURE_SOLAR_SYSTEM")
		self.featureForest = self.gc.getInfoTypeForString("FEATURE_FOREST")
		self.featureIce = self.gc.getInfoTypeForString("FEATURE_ICE")
		self.featureFallout = self.gc.getInfoTypeForString("FEATURE_FALLOUT")
		self.featureJungle = self.gc.getInfoTypeForString("FEATURE_JUNGLE")
		self.featureSupernovaArea = self.gc.getInfoTypeForString("FEATURE_SUPERNOVA_AREA")
		self.featureOasis = self.gc.getInfoTypeForString("FEATURE_OASIS")
		self.featureGravField = self.gc.getInfoTypeForString("FEATURE_GRAV_FIELD")
		self.featureFloodPlain = self.gc.getInfoTypeForString("FEATURE_FLOOD_PLAINS")

	def addFeatures(self):
		# First add the fractal-based features: Nebula, Asteroids, Radiation.
		for iX in range(self.iGridW):
			for iY in range(self.iGridH):
				self.addFeaturesAtPlot(iX, iY)
		
		# Now add the blunt force random features: Holes, Novas, Systems.
		#
		# These values control the rate of incidence for Hole, Nova, System.
		# As of this writing, all are determined strictly by ratio of total plot count.
		# Some randomness could be introduced by adding dice rolls to the formulae.
		#
		
		# Custom Map Option Stuff
		iStarSystemDensity = self.map.getCustomMapOption(0)
		iStarSystemMod = 0
		if (iStarSystemDensity == 0):	# Very High Density
			iStarSystemMod = -25
		elif (iStarSystemDensity == 1):	# High Density
			iStarSystemMod = -10
		elif (iStarSystemDensity == 2):	# Normal Density
			iStarSystemMod = -5
		elif (iStarSystemDensity == 3):	# Low Density
			iStarSystemMod = 50
		
		iHostileFeatureDensity = self.map.getCustomMapOption(2)
		iHostileFeatureMod = 0
		if (iHostileFeatureDensity == 0):	# Very High Density
			iHostileFeatureMod = -150
		elif (iHostileFeatureDensity == 1):	# High Density
			iHostileFeatureMod = 0
		elif (iHostileFeatureDensity == 2):	# Normal Density
			iHostileFeatureMod = 250
		elif (iHostileFeatureDensity == 3):	# Low Density
			iHostileFeatureMod = 400
		
		iNumPlots = self.iGridW * self.iGridH
#		iNumSolarSystems = int(iNumPlots / (90 + iStarSystemMod))
		iNumSolarSystems = int(iNumPlots / (120 + iStarSystemMod))
		iNumBlackHoles = int(iNumPlots / (600 + iHostileFeatureMod))
		iNumSupernovas = int(iNumPlots / (400 + iHostileFeatureMod))
		#print('------------------------')
		#print('Solar Systems: ', iNumSolarSystems)
		#print('Black Holes: ', iNumBlackHoles)
		#print('Supernovas: ', iNumSupernovas)
		#print('------------------------')
		
		# Reset globals which have to do with player starting positions
#		#print("Clearing global arrays when new map is made")
#		g_apSolarSystemPlotList = []
#		g_aiPickedPlotForPlayer = []
#		#print("g_apSolarSystemPlotList")
#		#print("g_aiPickedPlotForPlayer")
#		#print(g_apSolarSystemPlotList)
#		#print(g_aiPickedPlotForPlayer)
		
		# Solar Systems
		for iLoop in range(iNumSolarSystems):
			iAttemptsLeft = 400
			while iAttemptsLeft > 0:
				iUsableWidth = self.iGridW - 4
				iUsableHeight = self.iGridH - 4
				iX = 2 + self.mapRand.get(iUsableWidth, "Solar System X Check - Final Frontier PYTHON")
				iY = 2 + self.mapRand.get(iUsableHeight, "Solar System Y Check - Final Frontier PYTHON")
				
				iStartS = 3
				iStartL = 4
				
				if (iStarSystemDensity == 0): # High density, have to pack Star Systems in closer with stuff to fit everything in
					iStartS -= 1
					iStartL -= 1
				
				# Must not only check the plot itself, but also every plot in its fat cross.
				bAllow = True
				for iSolarX in range((iX - iStartS), (iX + iStartL)):
					if bAllow == False: break
					for iSolarY in range((iY - iStartS), (iY + iStartL)):
						if ((iSolarX == iX - iStartS) or (iSolarX == iX + iStartS)) and ((iSolarY == iY - iStartS) or (iSolarY == iY + iStartS)):
							continue #Skip the four corners.
						else:
							pPlot = self.map.sPlot(iSolarX, iSolarY)
							if (pPlot.getFeatureType() == self.featureFloodPlain or pPlot.getFeatureType() == self.featureIce or pPlot.getFeatureType() == self.featureSupernovaArea or pPlot.getFeatureType() == self.featureGravField):
								bAllow = False
								break
				if bAllow == False:
					iAttemptsLeft -= 1
					continue
				else: # Can place solar system here!
					#print("Adding Solar System to %d, %d" %(pPlot.getX(), pPlot.getY()))
					CyMap().plot(iX, iY).setFeatureType(self.featureSolarSystem, 0)
					#print('+++', 'Solar System placed at', iX, iY, '---', 'Attempts used: ', (401 - iAttemptsLeft), '+++')
					
					for xLoop in range((iX - iStartS), (iX + iStartL)):
						for yLoop in range((iY - iStartS), (iY + iStartL)):
							if ((xLoop == iX - iStartS) or (xLoop == iX + iStartS)) and ((yLoop == iY - iStartS) or (yLoop == iY + iStartS)):
								continue #Skip the four corners.
							elif xLoop == iX and yLoop == iY:
								continue #Don't overwrite the original feature!
							else:
								pEffectPlot = self.map.sPlot(xLoop, yLoop)
								pPlot.setFeatureType(self.featureFloodPlain, 0)
					break #Solar System placed, effects placed, break loop.
#			else:
				#print('Failed to place Solar System Number', (iLoop + 1))
		#print('------------------------')
		
		# Black Holes
		for iLoop in range(iNumBlackHoles):
			iAttemptsLeft = 200
			while iAttemptsLeft > 0:
				iUsableWidth = self.iGridW - 6
				iUsableHeight = self.iGridH - 6
				iX = 3 + self.mapRand.get(iUsableWidth, "Black Hole X Check - Final Frontier PYTHON")
				iY = 3 + self.mapRand.get(iUsableHeight, "Black Hole Y Check - Final Frontier PYTHON")

				# Must not only check the plot itself, but also every plot in its fat cross.
				bAllow = True
				for iHoleX in range((iX - 2), (iX + 3)):
					if bAllow == False: break
					for iHoleY in range((iY - 2), (iY + 3)):
						if ((iHoleX == iX - 2) or (iHoleX == iX + 2)) and ((iHoleY == iY - 2) or (iHoleY == iY + 2)):
							continue #Skip the four corners.
						else:
							pPlot = self.map.sPlot(iHoleX, iHoleY)
							if (pPlot.getFeatureType() == self.featureFloodPlain or pPlot.getFeatureType() == self.featureIce or pPlot.getFeatureType() == self.featureSupernovaArea or pPlot.getFeatureType() == self.featureGravField):
								bAllow = False
								break
				if bAllow == False:
					iAttemptsLeft -= 1
					continue

				pPlot = self.map.sPlot(iX, iY)
				if (pPlot.getFeatureType() == FeatureTypes.NO_FEATURE): #Place Black Hole here.
					pPlot.setFeatureType(self.featureOasis, 0)
					#print('+++', 'Black Hole placed at', iX, iY, '---', 'Attempts used: ', (201 - iAttemptsLeft), '+++')
					for xLoop in range((iX - 2), (iX + 3)):
						for yLoop in range((iY - 2), (iY + 3)):
							if ((xLoop == iX - 2) or (xLoop == iX + 2)) and ((yLoop == iY - 2) or (yLoop == iY + 2)):
								continue #Skip the four corners.
							elif xLoop == iX and yLoop == iY:
								continue #Don't overwrite the original feature!
							else:
								pEffectPlot = self.map.sPlot(xLoop, yLoop)
								pPlot.setFeatureType(self.featureGravField, 0)
					break #Black Hole placed, effects placed, break loop.
				else:
					iAttemptsLeft -= 1
#			else:
				#print('Failed to place Black Hole Number', (iLoop + 1))
		#print('------------------------')
		
		# Supernovas
		for iLoop in range(iNumSupernovas):
			iAttemptsLeft = 300
			while iAttemptsLeft > 0:
				iUsableWidth = self.iGridW - 4
				iUsableHeight = self.iGridH - 4
				iX = 2 + self.mapRand.get(iUsableWidth, "Supernova X Check - Final Frontier PYTHON")
				iY = 2 + self.mapRand.get(iUsableHeight, "Supernova Y Check - Final Frontier PYTHON")

				# Must not only check the plot itself, but also every plot in its fat cross.
				bAllow = True
				for iNovaX in range((iX - 2), (iX + 3)):
					if bAllow == False: break
					for iNovaY in range((iY - 2), (iY + 3)):
						if ((iNovaX == iX - 2) or (iNovaX == iX + 2)) and ((iNovaY == iY - 2) or (iNovaY == iY + 2)):
							continue #Skip the four corners.
						else:
							pPlot = self.map.sPlot(iNovaX, iNovaY)
							if (pPlot.getFeatureType() == self.featureFloodPlain or pPlot.getFeatureType() == self.featureIce or pPlot.getFeatureType() == self.featureSupernovaArea or pPlot.getFeatureType() == self.featureGravField):
								bAllow = False
								break
				if bAllow == False:
					iAttemptsLeft -= 1
					continue

				pPlot = self.map.sPlot(iX, iY)
				if (pPlot.getFeatureType() == FeatureTypes.NO_FEATURE): #Place Supernova here.
					pPlot.setFeatureType(self.featureJungle, 0)
					#print('+++', 'Supernova placed at', iX, iY, '---', 'Attempts used: ', (301 - iAttemptsLeft), '+++')
					for xLoop in range((iX - 2), (iX + 3)):
						for yLoop in range((iY - 2), (iY + 3)):
							if ((xLoop == iX - 2) or (xLoop == iX + 2)) and ((yLoop == iY - 2) or (yLoop == iY + 2)):
								continue #Skip the four corners.
							elif xLoop == iX and yLoop == iY:
								continue #Don't overwrite the original feature!
							else:
								pEffectPlot = self.map.sPlot(xLoop, yLoop)
								pEffectPlot.setFeatureType(self.featureSupernovaArea, 0)
#								#print("Adding Supernova Damage Zone to (%d, %d)" %(xLoop, yLoop))
					break #Supernova placed, effects placed, break loop.
				else:
					iAttemptsLeft -= 1
#			else:
				#print('Failed to place Supernova Number', (iLoop + 1))
		#print('------------------------')
		
		# Now remove all the placeholder Flood Plains.
		#print('-')
		#print('------------------------')
		for iPlotLoop in range(CyMap().numPlots()):
			pPlot = CyMap().plotByIndex(iPlotLoop)
			if (pPlot.getFeatureType() == self.featureFloodPlain):
				pPlot.setFeatureType(-1, -1)
#				#print('Flood Plain Placeholder removed at: ', pPlot.getX(), pPlot.getX())
		#print('------------------------')

	def addFeaturesAtPlot(self, iX, iY):
		"adds any appropriate features at the plot (iX, iY) where (0,0) is in the SW"
		pPlot = self.map.sPlot(iX, iY)
		
		# Need to place Solar Systems, Black Holes, and Supernovas here.

		if (pPlot.getFeatureType() == FeatureTypes.NO_FEATURE):
			self.addNebulaAtPlot(pPlot, iX, iY)

		if (pPlot.getFeatureType() == FeatureTypes.NO_FEATURE):
			self.addAsteroidsAtPlot(pPlot, iX, iY)

		if (pPlot.getFeatureType() == FeatureTypes.NO_FEATURE):
			self.addRadiationAtPlot(pPlot, iX, iY)
			
	def addNebulaAtPlot(self, pPlot, iX, iY):
		if (self.nebula.getHeight(iX+1, iY+1) <= self.iNebulaTop) and (self.nebula.getHeight(iX+1, iY+1) >= self.iNebulaBottom):
			pPlot.setFeatureType(self.featureIce, 0)

	def addAsteroidsAtPlot(self, pPlot, iX, iY):
		if (self.asteroids.getHeight(iX+1, iY+1) <= self.iAsteroidsTop) and (self.asteroids.getHeight(iX+1, iY+1) >= self.iAsteroidsBottom):
			pPlot.setFeatureType(self.featureForest, 0)

	def addRadiationAtPlot(self, pPlot, iX, iY):
		if ((self.radiation.getHeight(iX+1, iY+1) <= self.iRadiationTop) and (self.radiation.getHeight(iX+1, iY+1) >= self.iRadiationBottom)) or (self.radiation.getHeight(iX+1, iY+1) >= self.iRadiationMain):
			pPlot.setFeatureType(self.featureFallout, 0)

def addFeatures():
	global featuregen
	NiTextOut("Adding Features (Python FinalFrontierFeatureGenerator) ...")
	featuregen = FinalFrontierFeatureGenerator()
	featuregen.addFeatures()
	return 0

def findStartingPlot(argsList):
	[iPlayer] = argsList
	
	gc = CyGlobalContext()
	
	iStartPlotNum = -1
	
	#print("Checking for player %d in" %(iPlayer))
	#print(g_aiPickedPlotForPlayer)
	
	# Don't find a starting location more than once for a player
	if (iPlayer in g_aiPickedPlotForPlayer):
		
		pStartPlot = gc.getPlayer(iPlayer).getStartingPlot()
		#print("pStartPlot is already assigned to %d, %d" %(pStartPlot.getX(), pStartPlot.getY()))
		iPlotNum = CyMap().plotNum(pStartPlot.getX(), pStartPlot.getY())
		
		# Reset lists... would do this elsewhere but it appears there are multiple instances of these arrays floating around so I have to clear them in this function it seems
		g_aiPickedPlotForPlayer.remove(iPlayer)
		global g_apSolarSystemPlotList
		g_apSolarSystemPlotList = []
		
		return iPlotNum
	
	#print("Solar System Plot List is of size %d" %(len(g_apSolarSystemPlotList)))
	
	# Make list of valid plots (Solar Systems), but only once
	if (len(g_apSolarSystemPlotList) == 0):
		
		iFeatureSolarSystem = gc.getInfoTypeForString("FEATURE_SOLAR_SYSTEM")
		
		for iPlotLoop in range(CyMap().numPlots()):
			pPlot = CyMap().plotByIndex(iPlotLoop)
			
			if (pPlot.getFeatureType() == iFeatureSolarSystem):
				g_apSolarSystemPlotList.append(pPlot)
	
	# Now pick a random solar system from this list to see if it should become the player's start location
	iNumSolarSystems = len(g_apSolarSystemPlotList)

	pPlayer = gc.getPlayer(iPlayer)
	
	iRange = pPlayer.startingPlotRange()
	iPass = 0
	
	# Loop until we find a valid plot
	while (true):
		
		iRand = CyGame().getSorenRandNum(iNumSolarSystems, "Picking random solar system to start at for player %d" %(iPlayer))
		pRandomPlot = g_apSolarSystemPlotList[iRand]
		
#		#print("Randomly chosen plot is at %d, %d" %(pRandomPlot.getX(), pRandomPlot.getY()))
		
		bValid = True
		
		# See if the random Solar System is too close to another player's start
		for iClosePlayerLoop in range(gc.getMAX_CIV_PLAYERS()):
			if (gc.getPlayer(iClosePlayerLoop).isAlive()):
				if (iClosePlayerLoop != iPlayer):
					if startingPlotWithinRange(gc.getPlayer(iClosePlayerLoop), pRandomPlot, iPlayer, iRange, iPass):
						bValid = False
						break
		
#		#print("Valid?")
#		#print(bValid)
		
		# The one we've picked isn't too close, so use it
		if (bValid):
			
			iStartPlotNum = CyMap().plotNum(pRandomPlot.getX(), pRandomPlot.getY())
			g_apSolarSystemPlotList.remove(pRandomPlot)		# Now remove the plot from the list of valid Solar Systems which players can start at
			g_aiPickedPlotForPlayer.append(iPlayer)			# This player has now been assigned a starting plot, so this array tells the game not to do it again
			
			# Remove nearby goody huts
			for iXLoop in range(pRandomPlot.getX()-1, pRandomPlot.getX()+2):
				for iYLoop in range(pRandomPlot.getY()-1, pRandomPlot.getY()+2):
					
					iActiveX = iXLoop
					iActiveY = iYLoop
					
					if (iActiveX < 0):
						iActiveX = CyMap().getGridWidth() + iActiveX
					if (iActiveY < 0):
						iActiveY = CyMap().getGridHeight() + iActiveY
					
					pLoopPlot = CyMap().plot(iActiveX, iActiveY)
					
					# Any improvement? At this point it would only be a goody hut
					if (pLoopPlot.getImprovementType() != -1):
						pLoopPlot.setImprovementType(-1)
			
			# Add player city & Planetary Defense unit to start
			
			#print("Adding player starting city to %d, %d" %(pRandomPlot.getX(), pRandomPlot.getY()))
			pPlayer.initCity(pRandomPlot.getX(), pRandomPlot.getY())
			pCity = pRandomPlot.getPlotCity()
			
			iBuildingCapitol = gc.getInfoTypeForString("BUILDING_CAPITOL")
			pCity.setNumRealBuilding(iBuildingCapitol, 1)
			
			if (pPlayer.getNumUnits() == 0):
				iUnitType = gc.getInfoTypeForString("UNIT_PLANETARY_DEFENSE_I")
				pPlayer.initUnit(iUnitType, pRandomPlot.getX(), pRandomPlot.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.NO_DIRECTION)
			
			break		# We're done searching, exit the while loop
			
		# This run has failed to find a starting plot far enough away, try another random plot
		print "Player ID", iPlayer, "pass", iPass, "failed"
		iPass += 1
	
	return iStartPlotNum
	
def startingPlotWithinRange(pPlayer, pPlot, iOtherPlayer, iRange, iPass):
	
	iRange -= iPass
	
	pStartingPlot = pPlayer.getStartingPlot()
	gc = CyGlobalContext()
	
	if (pStartingPlot != -1):
		
		if (CyGame().isTeamGame()):
			
			if (gc.getPlayer(iOtherPlayer).getTeam() == pPlayer.getTeam()):
				
				iRange *= gc.getDefineINT("OWN_TEAM_STARTING_MODIFIER")
				iRange /= 100
				
			else:
				
				iRange *= gc.getDefineINT("RIVAL_TEAM_STARTING_MODIFIER")
				iRange /= 100
				
		if (plotDistance(pPlot.getX(), pPlot.getY(), pStartingPlot.getX(), pStartingPlot.getY()) <= iRange):
			
			return true
				
	return false
	
# Disable all the default operations that have no place or use in Final Frontier:
def addRivers():
	return None

def addLakes():
	return None

def normalizeAddRiver():
	return None

def normalizeRemovePeaks():
	return None

def normalizeAddLakes():
	return None

def normalizeRemoveBadFeatures():
	return None

def normalizeRemoveBadTerrain():
	return None
	
def normalizeAddFoodBonuses():
	return None

def normalizeAddGoodTerrain():
	return None

def normalizeAddExtras():
	return None
