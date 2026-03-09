# Desert War Scenario
# by Wouter "Locutus" Snijders - 2005-08-01
# Events for Desert War Scenario
# No sheep were harmed in the making of this file

# Note: This code was designed to be very 'newbie-friendly', so experienced
# programmers will recognize it's not always very efficient, concise, sensible,
# etc. This is deliberate, so don't bug me about it ;)

from CvPythonExtensions import *
import CvUtil
import CvCameraControls
import CvTranslator
import PyHelpers
import Popup as PyPopup
import math
import pickle

################
### Globals ###
##############

gc = CyGlobalContext()
PyPlayer = PyHelpers.PyPlayer
localText = CyTranslator()

# initialise misc variables
iX = 0
iY = 1
iNoFocus = -1
iFocusBoth = -2
bForceCoastal = True
bUsePythagoras = True
#tAlAqabahOilField = (51, 7)

# initialise team variables
iAllies = 0
iAxis = 1

# initialise player variables to player IDs from WBS
iBritish = 0
iAllied = 1
iFreeFrench = 2
iVichyFrench = 3
iGermans = 4
iItalians = 5
iSpanish = 6
iTurkish = 7

# initialise unit variables to unit indices from XML
iAlliedInfantry = 0
iBritishInfantry = 1
iVichyFrenchInfantry = 2
iFreeFrenchInfantry = 3
iGermanInfantry = 4
iTurkishInfantry = 5
iItalianInfantry = 6
iSpanishInfantry = 7
iVickers = 8		# Allied light tank
iCrusader = 9		# British light tank
iRenault = 10		# French light tank
iPanzerIII = 11		# German light tank
iL3tank = 12		# Italian light tank
iVerdeja = 13		# Spanish light tank
iMatilda = 16		# British heavy tank
iPanzerIV = 17		# German heavy tank
iTiger = 18		# German very heavy tank
iTransport = 21
iATransport = 23	# Allied transport
iDestroyer = 24
iBattleship = 25
iSubmarine = 26
iCarrier = 27
iACarrier = 28		# Allied carrier
iMesserschmidt = 32	# German fighter
iB25 = 45		# Allied tactical bomber
iStuka = 47		# German tactical bomber
iRommel = 59		# first German Great Commander

# units the British can't build if they lose the Middle East
forbiddenUnitList =	[	iCrusader,
				iMatilda,
				iTransport,
				iDestroyer,
				iBattleship,
				iSubmarine,
				iCarrier	]

# initialise promotion variables to promotion indices from XML
iAmbush = 10
iMedicI = 12
iMedicII = 13
iGuerillaI = 14
iRepair = 39

# initialise tech variables to tech indices from XML
iDesertFox = 11		# Desert Fox
iBarbarossa = 12	# Operation Barbarossa
iPearlHarbor = 13	# Pearl Harbor
iTorch = 14		# Operation Torch
iArmySupport = 15	# Army Support


# initialise civic variables to civic indices from XML
iGuerrilla = 2

# initialises city variables to city coords from WBS
tMarrakech = (1, 6)
tRabat = (2, 12)
tValladolid = (2, 29)
tTangiers = (3, 16)
tCadiz = (3, 21)
tMadrid = (5, 25)
tBechar = (6, 6)
tGibraltar = (6, 18)
tOran = (7, 13)
tCartagena = (9, 22)
tBarcelona = (9, 28)
tAlgiers = (11, 14)
tPalma = (13, 24)
tGabes = (16, 10)
tTunis = (16, 14)
tAlghero = (17, 28)
tCagliari = (18, 24)
tTripoli = (20, 8)
tPalermo = (21, 16)
tValletta = (22, 12)
tSurt = (24, 5)
tMessina = (24, 16)
tNaples = (24, 26)
tFoggia = (25, 29)
tCatanzaro = (28, 20)
tBari = (28, 25)
tAjdabiya = (30, 3)
tBenghazi = (31, 8)
tIgoumenitsa = (32, 29)
tPreveza = (33, 23)
tTobruk = (35, 10)
tYithion = (36, 17)
tAthens = (37, 20)
tLarisa = (37, 29)
tVolos = (38, 25)
tElAlamein = (39, 8)
tIraklion = (39, 15)
tAlBawiti = (40, 5)
tAlMinya = (42, 1)
tAlexandria = (42, 9)
tIzmir = (43, 24)
tIstanbul = (43, 29)
tCairo = (44, 5)
tNicosia = (45, 15)
tAntalya = (45, 19)
tSuez = (46, 9)
tKonya = (47, 23)
tAnkarra = (47, 29)
tRasGharib = (48, 2)
tBeirut = (49, 14)
tAlAqabah = (50, 8)
tLatakia = (50, 20)
tDamascus = (51, 11)
tHoms = (51, 17)
tKaysen = (51, 25)

# define regions as lists of city coords

# order: west to east
tWestAfricaList =	[	tMarrakech,
				tRabat,
				tTangiers,
				tBechar,
				tGibraltar,
				tOran,
				tAlgiers,
				tTunis,
				tGabes		]

# order: west to east
tLibyaList =		[	tTripoli,
				tSurt,
				tAjdabiya,
				tBenghazi,
				tTobruk		]

# order: west to east
tEgyptList =		[	tElAlamein,
				tAlBawiti,
				tAlMinya,
				tAlexandria,
				tCairo,
				tSuez,
				tRasGharib	]

# order: west to east
tTurkeyList =		[	tIzmir,
				tIstanbul,
				tAntalya,
				tAnkarra,
				tKonya,
				tKaysen		]

# order: south to north
tArabiaList =		[	tAlAqabah,
				tDamascus,
				tBeirut,
				tHoms,
				tLatakia	]

# order: west to east
tMediterraneanList =	[	tAlghero,
				tCagliari,
				tPalermo,
				tValletta,
				tMessina,
				tIraklion,
				tNicosia	]

# order: west to east
tSpainList =		[	tValladolid,
				tCadiz,
				tMadrid,
				tGibraltar,
				tCartagena,
				tBarcelona,
				tPalma		]

# order: south to north
tItalyList =		[	tPalermo,
				tMessina,
				tCatanzaro,
				tCagliari,
				tBari,
				tNaples,
				tAlghero,
				tFoggia		]

# order: south to north
tGreeceList =		[	tIraklion,
				tYithion,
				tAthens,
				tPreveza,
				tVolos,
				tIgoumenitsa,
				tLarisa		]

tEastAfricaList = tLibyaList + tEgyptList
tAfricaList = tWestAfricaList + tEastAfricaList
tAsiaList = tArabiaList + tTurkeyList
tEuropeList = tSpainList + tItalyList + tGreeceList

# order: west to east
tObjectivesList =	[	tGibraltar,
				tAlgiers,
				tMessina,
				tAthens,
				tSuez,
				tDamascus	]

def getCity( tCoords ):
	"""Returns the city at coordinates tCoords."""
	return gc.getMap().plot( tCoords[iX], tCoords[iY] ).getPlotCity()



class CvDesertWar:

#############################################
### Various helpers for the main methods ###
###########################################

	def makeUnit( self, iUnit, iPlayer, plot, iNum ):
		"""Makes iNum units for player iPlayer of the type iUnit at plot;
		returns a list of the created units."""
		unitList = []
		for i in range(iNum):
			player = gc.getPlayer(iPlayer)
			unit = player.initUnit(iUnit, plot.getX(), plot.getY(), UnitAITypes.NO_UNITAI)
			unitList.append(unit)
		return unitList

	def giveTech( self, iTech, iPlayer ):
		"""Gives advance iTech to iPlayer."""
		iTeam = gc.getPlayer(iPlayer).getTeam()
		gc.getTeam(iTeam).setHasTech(iTech, True, 0, False, False)

	def isMedicInfantry( self, unit ):
		"""Returns True if unit is an Infantry unit with a Medic I and/or Medic II promotion."""
		return (	(  unit.getUnitType() == iAlliedInfantry	\
				or unit.getUnitType() == iBritishInfantry	\
				or unit.getUnitType() == iVichyFrenchInfantry	\
				or unit.getUnitType() == iFreeFrenchInfantry	\
				or unit.getUnitType() == iGermanInfantry	\
				or unit.getUnitType() == iTurkishInfantry	\
				or unit.getUnitType() == iItalianInfantry	\
				or unit.getUnitType() == iSpanishInfantry	)
				and
				(  unit.isHasPromotion(iMedicI)			\
				or unit.isHasPromotion(iMedicII)		)
			)

	def isNonMedicInfantry( self, unit ):
		"""Returns True if unit is an Infantry unit without a Medic I and/or Medic II promotion."""
		return (	(  unit.getUnitType() == iAlliedInfantry	\
				or unit.getUnitType() == iBritishInfantry	\
				or unit.getUnitType() == iVichyFrenchInfantry	\
				or unit.getUnitType() == iFreeFrenchInfantry	\
				or unit.getUnitType() == iGermanInfantry	\
				or unit.getUnitType() == iTurkishInfantry	\
				or unit.getUnitType() == iItalianInfantry	\
				or unit.getUnitType() == iSpanishInfantry	)
				and not
				(  unit.isHasPromotion(iMedicI)			\
				or unit.isHasPromotion(iMedicII)		)
			)

	def isRepairTank( self, unit ):
		"""Returns True if unit is a Light Tank unit with a Repair promotion."""
		return (	(  unit.getUnitType() == iVickers		\
				or unit.getUnitType() == iCrusader		\
				or unit.getUnitType() == iRenault		\
				or unit.getUnitType() == iPanzerIII		\
				or unit.getUnitType() == iL3tank		\
				or unit.getUnitType() == iVerdeja		)
				and
				unit.isHasPromotion(iRepair)
			)

	def isNonRepairTank( self, unit ):
		"""Returns True if unit is a Light Tank unit without a Repair promotion."""
		return (	(  unit.getUnitType() == iVickers		\
				or unit.getUnitType() == iCrusader		\
				or unit.getUnitType() == iRenault		\
				or unit.getUnitType() == iPanzerIII		\
				or unit.getUnitType() == iL3tank		\
				or unit.getUnitType() == iVerdeja		)
				and not
				unit.isHasPromotion(iRepair)
			)

	def isCityAllies( self, city ):
		"""Returns True if city is British, Allied or Free French."""
		iPlayer = city.getOwner()
		return (iPlayer == iBritish or iPlayer == iAllied or iPlayer == iFreeFrench)

	def isCityAxis( self, city ):
		"""Returns True if city is German, Italian or Vichy French."""
		iPlayer = city.getOwner()
		return (iPlayer == iGermans or iPlayer == iItalians or iPlayer == iVichyFrench)

	def isPlayerAllies( self, iPlayer ):
		"""Returns True if player iPlayer is British, Allied or Free French."""
		return (iPlayer == iBritish or iPlayer == iAllied or iPlayer == iFreeFrench)

	def isPlayerAxis( self, iPlayer ):
		"""Returns True if player iPlayer is German, Italian or Vichy French."""
		return (iPlayer == iGermans or iPlayer == iItalians or iPlayer == iVichyFrench)

	def countAlliesObjectives( self ):
		"""Return the number of Objective Cities that the Allies team controls."""
		iCount = 0
		for tCoords in tObjectivesList:
			if self.isCityAllies( getCity(tCoords) ):
				iCount = iCount + 1
		return iCount

	def countAxisObjectives( self ):
		"""Return the number of Objective Cities that the Axis team controls."""
		iCount = 0
		for tCoords in tObjectivesList:
			if self.isCityAxis( getCity(tCoords) ):
				iCount = iCount + 1
		return iCount

	def countNeutralObjectives( self ):
		"""Return the number of Objective Cities that the Spanish and Turkish control."""
		iCount = 0
		for tCoords in tObjectivesList:
			if not ( self.isCityAxis(getCity(tCoords)) or self.isCityAllies(getCity(tCoords)) ):
				iCount = iCount + 1
		return iCount

	def countCitiesInRegion( self, iPlayer, tRegionList, bForceCoastal ):
		"""Returns the number of (coastal) cities tRegionList that player iPlayer controls
		in the region tRegionList."""
		iCount = 0
		for tCoords in tRegionList:
			city = getCity(tCoords)
			if city.getOwner() == iPlayer:
				if bForceCoastal and city.isCoastal():
					iCount = iCount + 1
				elif not bForceCoastal:
					iCount = iCount + 1
		return iCount

	def equals( self, city1, city2 ):
		"""Returns True if city1 is the same city as city2."""
		return ( city1.getX() == city2.getX() and city1.getY() == city2.getY() )

	def numTurnsBasedOnAssets( self, iStartValue, iTeam ):
		"""Return a value based on the relative score of both teams"""
		if iTeam == iAxis:
			if   gc.getTeam(iAxis).getAssets() > 1.5 * gc.getTeam(iAllies).getAssets():
				return iStartValue
			elif gc.getTeam(iAxis).getAssets() > 1.3 * gc.getTeam(iAllies).getAssets():
				return iStartValue + 1
			elif gc.getTeam(iAxis).getAssets() > 1.2 * gc.getTeam(iAllies).getAssets():
				return iStartValue + 2
			elif gc.getTeam(iAxis).getAssets() > 1.1 * gc.getTeam(iAllies).getAssets():
				return iStartValue + 3
			elif gc.getTeam(iAxis).getAssets() > 1.0 * gc.getTeam(iAllies).getAssets():
				return iStartValue + 4
			elif gc.getTeam(iAxis).getAssets() > 0.9 * gc.getTeam(iAllies).getAssets():
				return iStartValue + 5
			elif gc.getTeam(iAxis).getAssets() > 0.8 * gc.getTeam(iAllies).getAssets():
				return iStartValue + 6
			elif gc.getTeam(iAxis).getAssets() > 0.7 * gc.getTeam(iAllies).getAssets():
				return iStartValue + 7
			elif gc.getTeam(iAxis).getAssets() > 0.5 * gc.getTeam(iAllies).getAssets():
				return iStartValue + 8
			else:
				return iStartValue + 9
		elif iTeam == iAllies:
			if   gc.getTeam(iAllies).getAssets() > 1.5 * gc.getTeam(iAxis).getAssets():
				return iStartValue
			elif gc.getTeam(iAllies).getAssets() > 1.3 * gc.getTeam(iAxis).getAssets():
				return iStartValue + 1
			elif gc.getTeam(iAllies).getAssets() > 1.2 * gc.getTeam(iAxis).getAssets():
				return iStartValue + 2
			elif gc.getTeam(iAllies).getAssets() > 1.1 * gc.getTeam(iAxis).getAssets():
				return iStartValue + 3
			elif gc.getTeam(iAllies).getAssets() > 1.0 * gc.getTeam(iAxis).getAssets():
				return iStartValue + 4
			elif gc.getTeam(iAllies).getAssets() > 0.9 * gc.getTeam(iAxis).getAssets():
				return iStartValue + 5
			elif gc.getTeam(iAllies).getAssets() > 0.8 * gc.getTeam(iAxis).getAssets():
				return iStartValue + 6
			elif gc.getTeam(iAllies).getAssets() > 0.7 * gc.getTeam(iAxis).getAssets():
				return iStartValue + 7
			elif gc.getTeam(iAllies).getAssets() > 0.5 * gc.getTeam(iAxis).getAssets():
				return iStartValue + 8
			else:
				return iStartValue + 9

	def findCity( self, tRegionList, tExceptionList, iTeam, bForceCoastal ):
		"""If possible, returns a (coastal) city from tRegionList that belongs to team iTeam 
		and is not in tExceptionList."""
		if iTeam == iAxis:
			for tCoords in tRegionList:
				city = getCity(tCoords)
				if self.isCityAxis(city):
					if not tCoords in tExceptionList:
						if bForceCoastal:
							if city.isCoastal():
								return city
						else:
							return city
		if iTeam == iAllies:
			for tCoords in tRegionList:
				city = getCity(tCoords)
				if self.isCityAllies(city):
					if not city in tExceptionList:
						if bForceCoastal:
							if city.isCoastal():
								return city
						else:
							return city

	def creteCaptured( self, tCoords, iDistance, bPythagoras, result, argsList ):
		"""Called by breadthFirstSearchPyth; checks validity of the plot at the current tCoords,
		returns plot if valid (which stops the search)."""
		bPaint = True
		bContinue = True
		#if bPythagoras:
		#	fDistance = math.sqrt(iSquaredDistance)
		#	iDistance = math.sqrt(iSquaredDistance)
		pCurrent = gc.getMap().plot( tCoords[iX], tCoords[iY] )
		iChance = argsList[0]
		iRndNum = gc.getGame().getSorenRandNum( 100,
				'Desert War - Crete Captured, plot: (%d, %d)' %(tCoords[iX], tCoords[iY]) )

		if ( pCurrent.isHills() or pCurrent.isFlatlands() ):
			if ( not pCurrent.isCity() and not pCurrent.isUnit() ):
				if self.isPlayerAxis( pCurrent.getOwner() ):
					# check if plot is on same landmass as Athens (so on mainland Greece)
					pAthens = gc.getMap().plot( tAthens[iX], tAthens[iY] )
					if not gc.getMap().calculatePathDistance( pCurrent, pAthens ) == -1:
						if iChance < iRndNum:
							# found what we need
							return (pCurrent, bPaint, not bContinue)
						else:	# good plot but dice roll failed
							return (None, bPaint, bContinue)
		# not a good plot, so don't paint it but continue search
		return (None, not bPaint, bContinue)

	def operationTorch( self, tCoords, iDistance, bPythagoras, result, argsList ):
		"""Called by breadthFirstSearchPyth; checks validity of the plot at the current tCoords,
		returns plot if valid (which stops the search)."""
		bPaint = True
		bContinue = True
		#if bPythagoras:
		#	fDistance = math.sqrt(iSquaredDistance)
		#	iDistance = math.sqrt(iSquaredDistance)
		pCurrent = gc.getMap().plot( tCoords[iX], tCoords[iY] )
		iChance = argsList[0]
		iRndNum = gc.getGame().getSorenRandNum( 100,
				'Desert War - Operation Torch, plot: (%d, %d)' %(tCoords[iX], tCoords[iY]) )

		if pCurrent.isWater():
			if not pCurrent.isUnit():
				if iChance < iRndNum:
					# found what we need, so stop and return this plot
					return (pCurrent, bPaint, not bContinue)
				else:
					# good plot but dice roll failed, so paint it and continue
					return (None, bPaint, bContinue)
		# not a good plot, so don't paint it but continue search
		return (None, not bPaint, bContinue)

	def doPlot( self, tCoords, iDistance, bPythagoras, argsList ):
		"""Called by breadthFirstSearch; can stop search by returning something other than None."""
		bPaint = True
		bContinue = True
		#if bPythagoras:
		#	fDistance = math.sqrt(iSquaredDistance)
		#	iDistance = int(math.sqrt(iSquaredDistance))
		pCurrent = gc.getMap().plot( tCoords[iX], tCoords[iY] )
		# format: (result, bPaintedPlot, bContinueSearch)
		return (None, bPaint, bContinue)

	def findFreePlotNear( self, tCentre, iRadius, bPythagoras, function ):
		"""Returns a random plot within iRadius of tCoords where there are no units; bPythagoras
		determines if iRange is calculated using Pythagoras or by counting the number of tiles to
		the tCentre. The function object.strFunction is called to do the actual validity check."""
		# try to find a free plot with a 5% chance a suitable plot is approved
		pResult = self.concentricSearch( tCentre, iRadius, bPythagoras, function, [5] )
		if not pResult[0]:
			# try the same search with a 33% chance of approval
			pResult = self.concentricSearch( tCentre, iRadius, bPythagoras, function, [33] )
		if not pResult[0] and pResult[1]:
			# if any plots are painted, randomly return one of them
			rndNum = gc.getGame().getSorenRandNum(len(pResult[1]), 
							'Desert War - findFreePlotNear: ' + strFunction)
			return pResult[1][rnd]
		# return the result if one was found, else None
		return pResult[0]

	def concentricSearch( self, tCentre, iRange, bPythagoras, function, argsList ):
		"""Concentrically searches all tiles in range iRange around tCentre and calls function for
		every tile, passing argsList. bPythagoras determines if iRange is calculated using Pythagoras
		by counting the number of tiles to the tCentre. The function called must return a as tuple:
		(1) a result, (2) if a plot should be painted and (3) if the search should continue.

		Returns a tuple of the result and the list of all painted plots. Note to programmers: this 
		algorithm is a breadth-first search."""
		tQueueList = [(tCentre, 0)]		# initial queue
		tVisitedList = [tCentre]		# visited children
		tPaintedList = []
		result = None
		while tQueueList:
			# dequeue node (= coords, distance)
			tNode = tQueueList[0]
			tQueueList.remove(tNode)
			# splite node
			tCoords, iDistance = tNode
			# do object.function() and check for goal
			result, bPaintPlot, bContinueSearch = function(tCoords, iDistance, bPythagoras, result, argsList)
			if bPaintPlot:			# paint plot
				tPaintedList.append(tCoords)
			if not bContinueSearch:		# goal reached, so stop
				return result, tPaintedList
			# queue unvisited children (= neighbours within range (queued concentrically))
			for x, y in [(0,0), (0,1), (1,1), (1,0), (1,-1), (0,-1), (-1,-1), (-1,0), (-1,1)]:
				tNeighbour = ( tCoords[iX] + x, tCoords[iY] + y )
				# search in a circular pattern, using Pythagoras for distance
				if ( bPythagoras and self.squaredDistance(tNeighbour, tCentre) < iRange*iRange ):
					if ( self.isOnMap(tNeighbour) and not tNeighbour in tVisitedList ):
						tVisitedList.append(tNeighbour)
						tQueueList.append( (tNeighbour, iDistance) )
				# search in a square pattern, using number of tiles for distance
				elif ( not bPythagoras and iDistance+1 < iRange ):
					if ( self.isOnMap(tNeighbour) and not tNeighbour in tVisitedList ):
						tVisitedList.append(tNeighbour)
						tQueueList.append( (tNeighbour, iDistance+1) )
		return result, tPaintedList

	def isOnMap( self, tCoords ):
		"""Returns if plot at tCoords is a valid map plot."""
		return tCoords[iX] > 0 and tCoords[iY] > 0 and tCoords[iX] < gc.getMap().getGridWidth() and tCoords[iY] < gc.getMap().getGridHeight()

	def squaredDistance( self, tFirst, tSecond ):
		"""Returns the squared distance (using Pythagoras) between the plots at tFirst and tSecond."""
		return ( tFirst[iX] - tSecond[iX] ) * ( tFirst[iX] - tSecond[iX] ) + ( tFirst[iY] - tSecond[iY] ) * ( tFirst[iY] - tSecond[iY] )

	def plotDistance( self, tFirst, tSecond ):
		"""Returns the number distance between tFirst and tSecond in the number of plots."""
		xDistance = tFirst[iX] - tSecond[iX]
		yDistance = tFirst[iY] - tSecond[iY]
		if xDistance < 0:
			xDistance = -xDistance
		if yDistance < 0:
			yDistance = -yDistance
		if xDistance >= yDistance:
			return xDistance
		else:
			return yDistance

##################################################
### Secure storage & retrieval of script data ###
################################################

	def setupScriptData( self ):
		"""Initialise the global script data dictionary for usage."""
		scriptDict =	{	'bKasserinePass': False,
					'bMarethLine': False,
					'bOperationBarbarossa': False,
					'bMiddleEast': False,
					'bStalingrad': False,
					'bParisLiberated': False,
					'bEnglandFallen': False,
					'bCapTimerOn': False,
					'bEndCapTimer': False,
					'bVictoryNextTurn': False,
					'bVictoryAchieved': False,
					'iExtraUnitCost': 0,
					'iParisLiberation': -1,
					'iEnglandFalls': -1,
					'iCapTimer': 0,
					'iVictoryTimer': 9,
					'tCapturedObjectivesList': []
				}
		gc.getPlayer(0).setScriptData( pickle.dumps(scriptDict) )

	def isOperationBarbarossa( self ):
		"""Returns if the Operation Barbarossa event already took place."""
		scriptDict = pickle.loads( gc.getPlayer(0).getScriptData() )
		return scriptDict['bOperationBarbarossa']

	def setOperationBarbarossa( self, bNewValue ):
		"""Sets that the Operation Barbarossa event took place."""
		scriptDict = pickle.loads( gc.getPlayer(0).getScriptData() )
		scriptDict['bOperationBarbarossa'] = bNewValue
		gc.getPlayer(0).setScriptData( pickle.dumps(scriptDict) )

	def getExtraUnitCost( self ):
		"""Returns the Extra Unit Cost that is the result of Operation Barbarossa."""
		scriptDict = pickle.loads( gc.getPlayer(0).getScriptData() )
		return scriptDict['iExtraUnitCost']

	def setExtraUnitCost( self, iNewValue ):
		"""Sets the Extra Unit Cost that is the result of Operation Barbarossa."""
		scriptDict = pickle.loads( gc.getPlayer(0).getScriptData() )
		scriptDict['iExtraUnitCost'] = iNewValue
		gc.getPlayer(0).setScriptData( pickle.dumps(scriptDict) )

	def isMiddleEast( self ):
		"""Returns if the Middle East event already took place."""
		scriptDict = pickle.loads( gc.getPlayer(0).getScriptData() )
		return scriptDict['bMiddleEast']

	def setMiddleEast( self, bNewValue ):
		"""Sets that the Middle East event took place."""
		scriptDict = pickle.loads( gc.getPlayer(0).getScriptData() )
		scriptDict['bMiddleEast'] = bNewValue
		gc.getPlayer(0).setScriptData( pickle.dumps(scriptDict) )

	def isStalingrad( self ):
		"""Returns if the Stalingrad event already took place."""
		scriptDict = pickle.loads( gc.getPlayer(0).getScriptData() )
		return scriptDict['bStalingrad']

	def setStalingrad( self, bNewValue ):
		"""Sets that the Stalingrad event took place."""
		scriptDict = pickle.loads( gc.getPlayer(0).getScriptData() )
		scriptDict['bStalingrad'] = bNewValue
		gc.getPlayer(0).setScriptData( pickle.dumps(scriptDict) )

	def isParisLiberated( self ):
		"""Returns if the Paris has been liberated yet."""
		scriptDict = pickle.loads( gc.getPlayer(0).getScriptData() )
		return scriptDict['bParisLiberated']
	
	def setParisLiberated( self, bNewValue ):
		"""Sets that Paris has been liberated."""
		scriptDict = pickle.loads( gc.getPlayer(0).getScriptData() )
		scriptDict['bParisLiberated'] = bNewValue
		gc.getPlayer(0).setScriptData( pickle.dumps(scriptDict) )

	def getParisLiberation( self ):
		"""Returns the turn Paris is/will be liberated."""
		scriptDict = pickle.loads( gc.getPlayer(0).getScriptData() )
		return scriptDict['iParisLiberation']

	def setParisLiberation( self, iNewValue ):
		"""Sets the turn Paris will be liberated."""
		scriptDict = pickle.loads( gc.getPlayer(0).getScriptData() )
		scriptDict['iParisLiberation'] = iNewValue
		gc.getPlayer(0).setScriptData( pickle.dumps(scriptDict) )

	def isKasserinePass( self ):
		"""Returns if the Kasserine Pass event already took place."""
		scriptDict = pickle.loads( gc.getPlayer(0).getScriptData() )
		return scriptDict['bKasserinePass']

	def setKasserinePass( self, bNewValue ):
		"""Sets that the Kasserine Pass event took place."""
		scriptDict = pickle.loads( gc.getPlayer(0).getScriptData() )
		scriptDict['bKasserinePass'] = bNewValue
		gc.getPlayer(0).setScriptData( pickle.dumps(scriptDict) )

	def isMarethLine( self ):
		"""Returns if the Mareth Line event already took place."""
		scriptDict = pickle.loads( gc.getPlayer(0).getScriptData() )
		return scriptDict['bMarethLine']

	def setMarethLine( self, bNewValue ):
		"""Sets that the Mareth Line event took place."""
		scriptDict = pickle.loads( gc.getPlayer(0).getScriptData() )
		scriptDict['bMarethLine'] = bNewValue
		gc.getPlayer(0).setScriptData( pickle.dumps(scriptDict) )

	def isEnglandFallen( self ):
		"""Returns if the England Fallen event already took place."""
		scriptDict = pickle.loads( gc.getPlayer(0).getScriptData() )
		return scriptDict['bEnglandFallen']

	def setEnglandFallen( self, bNewValue ):
		"""Sets that the England Fallen event took place."""
		scriptDict = pickle.loads( gc.getPlayer(0).getScriptData() )
		scriptDict['bEnglandFallen'] = bNewValue
		gc.getPlayer(0).setScriptData( pickle.dumps(scriptDict) )

	def getEnglandFalls( self ):
		"""Returns the turn England has fallen/will fall."""
		scriptDict = pickle.loads( gc.getPlayer(0).getScriptData() )
		return scriptDict['iEnglandFalls']

	def setEnglandFalls( self, iNewValue ):
		"""Sets the turn England will fall."""
		scriptDict = pickle.loads( gc.getPlayer(0).getScriptData() )
		scriptDict['iEnglandFalls'] = iNewValue
		gc.getPlayer(0).setScriptData( pickle.dumps(scriptDict) )

	def isCapTimerOn( self ):
		"""Returns if the Italian Capitulation timer is running."""
		scriptDict = pickle.loads( gc.getPlayer(0).getScriptData() )
		return scriptDict['bCapTimerOn']

	def setCapTimerOn( self, bNewValue ):
		"""Starts the Italian Capitulation timer."""
		scriptDict = pickle.loads( gc.getPlayer(0).getScriptData() )
		scriptDict['bCapTimerOn'] = bNewValue
		gc.getPlayer(0).setScriptData( pickle.dumps(scriptDict) )

	def isEndCapTimer( self ):
		"""Returns if the Italian Capitulation timer has stopped."""
		scriptDict = pickle.loads( gc.getPlayer(0).getScriptData() )
		return scriptDict['bEndCapTimer']

	def setEndCapTimer( self, bNewValue ):
		"""Starts the Italian Capitulation timer."""
		scriptDict = pickle.loads( gc.getPlayer(0).getScriptData() )
		scriptDict['bEndCapTimer'] = bNewValue
		gc.getPlayer(0).setScriptData( pickle.dumps(scriptDict) )

	def getCapTimer( self ):
		"""Returns the value of the Italian Capitulation timer."""
		scriptDict = pickle.loads( gc.getPlayer(0).getScriptData() )
		return scriptDict['iCapTimer']

	def setCapTimer( self, iNewValue ):
		"""Changes the Italian Capitulation timer."""
		scriptDict = pickle.loads( gc.getPlayer(0).getScriptData() )
		scriptDict['iCapTimer'] = iNewValue
		gc.getPlayer(0).setScriptData( pickle.dumps(scriptDict) )

	def isVictoryNextTurn( self ):
		"""Returns if the Victory timer is almost at zero."""
		scriptDict = pickle.loads( gc.getPlayer(0).getScriptData() )
		return scriptDict['bVictoryNextTurn']

	def setVictoryNextTurn( self, bNewValue ):
		"""Sets that the Victory timer is almost at zero."""
		scriptDict = pickle.loads( gc.getPlayer(0).getScriptData() )
		scriptDict['bVictoryNextTurn'] = bNewValue
		gc.getPlayer(0).setScriptData( pickle.dumps(scriptDict) )

	def getVictoryTimer( self ):
		"""Returns the value of the Victory timer."""
		scriptDict = pickle.loads( gc.getPlayer(0).getScriptData() )
		return scriptDict['iVictoryTimer']

	def setVictoryTimer( self, iNewValue ):
		"""Changes the Victory timer."""
		scriptDict = pickle.loads( gc.getPlayer(0).getScriptData() )
		scriptDict['iVictoryTimer'] = iNewValue
		gc.getPlayer(0).setScriptData( pickle.dumps(scriptDict) )

	def isVictoryAchieved( self ):
		"""Returns if the game has been won yet."""
		scriptDict = pickle.loads( gc.getPlayer(0).getScriptData() )
		return scriptDict['bVictoryAchieved']

	def setVictoryAchieved( self, bNewValue ):
		"""Sets that someone won the game."""
		scriptDict = pickle.loads( gc.getPlayer(0).getScriptData() )
		scriptDict['bVictoryAchieved'] = bNewValue
		gc.getPlayer(0).setScriptData( pickle.dumps(scriptDict) )

	def isObjectiveCaptured( self, tCoords ):
		"""Returns if an Objective has already been captured."""
		scriptDict = pickle.loads( gc.getPlayer(0).getScriptData() )
		return tCoords in scriptDict['tCapturedObjectivesList']

	def setObjectiveCaptured( self, tCoords ):
		"""Sets an Objective as having been captured."""
		scriptDict = pickle.loads( gc.getPlayer(0).getScriptData() )
		scriptDict['tCapturedObjectivesList'].append(tCoords)
		gc.getPlayer(0).setScriptData( pickle.dumps(scriptDict) )



#################
### Messages ###
###############


	def displayPopupTo( self, strText, argsList, iFocus, pFocus=None ):
		"""Displays a pop-up message with either strText_AXIS or strText_ALLIES as XML tag as body
		and strText_TITLE as title; text may contain a variable."""
		popup = PyPopup.PyPopup()
		popup.setHeaderString( localText.getText(strText + "_TITLE", ()) )
		if self.isPlayerAxis( gc.getGame().getActivePlayer() ):
			if ( pFocus and (iFocus == iAxis or iFocus == iFocusBoth) ):
				cam = CvCameraControls.CvCameraControls()
				cam.centerCamera( pFocus )
			# pass a city name if strText contains a %s1_City variable
			popup.setBodyString( localText.getText(strText + "_AXIS", argsList) )
		if self.isPlayerAllies( gc.getGame().getActivePlayer() ):
			if ( pFocus and (iFocus == iAllies or iFocus == iFocusBoth) ):
				cam = CvCameraControls.CvCameraControls()
				cam.centerCamera( pFocus )
			# pass a city name if strText contains a %s1_City variable
			popup.setBodyString( localText.getText(strText + "_ALLIES", argsList) )
		popup.launch()

	def displayPopup( self, strText, argsList ):
		"""Displays a pop-up message with strText as XML tag for the body and strText_TITLE as title;
		text may contain a variable."""
		popup = PyPopup.PyPopup()
		popup.setHeaderString( localText.getText(strText + "_TITLE", ()) )
		popup.setBodyString( localText.getText(strText, argsList) )
		popup.launch()

	def displayObjectivePopup( self, strText ):
		"""Displays a pop-up message with strText as message."""
		popup = PyPopup.PyPopup()
		popup.setBodyString( localText.getText(strText, ()) )
		popup.launch()

	def displayVictoryPopup( self, strText ):
		"""Displays a pop-up message with strText as message."""
		popup = PyPopup.PyPopup()
		popup.setHeaderString( localText.getText("TXT_KEY_WW2_EVENT_VICTORY", ()) )
		popup.setBodyString( localText.getText(strText, ()) )
		popup.launch()

	def defeatCheck(self, iPlayer):
		"""Display a message if a human player has been defeated."""
		if gc.getGame().getActivePlayer() == iPlayer:
			strPlayerAdj = gc.getPlayer(iPlayer).getCivilizationAdjective(2)
			strAllies = ''
			if self.isPlayerAxis(iPlayer):
				if ( iPlayer != iGermans and gc.getPlayer(iGermans).isAlive() ):
					strAllies += gc.getPlayer(iGermans).getCivilizationShortDescription(2)
				if ( iPlayer != iItalians and gc.getPlayer(iItalians).isAlive() ):
					if strAllies == '':
						strAllies += gc.getPlayer(iItalians).getCivilizationShortDescription(2)
					else:
						strAllies += ' ' + localText.getText("TXT_KEY_AND", ()) + gc.getPlayer(iItalians).getCivilizationShortDescription(2)
				if ( iPlayer != iVichyFrench and gc.getPlayer(iVichyFrench).isAlive() ):
					if strAllies == '':
						strAllies += gc.getPlayer(iVichyFrench).getCivilizationShortDescription(2)
					else:
						strAllies += ' ' + localText.getText("TXT_KEY_AND", ()) + gc.getPlayer(iVichyFrench).getCivilizationShortDescription(2)
			if self.isPlayerAllies(iPlayer):
				if ( iPlayer != iBritish and gc.getPlayer(iBritish).isAlive() ):
					strAllies += gc.getPlayer(iBritish).getCivilizationShortDescription(2)
				if ( iPlayer != iAllied and gc.getPlayer(iAllied).isAlive() ):
					if strAllies == '':
						strAllies += gc.getPlayer(iAllied).getCivilizationShortDescription(2)
					else:
						strAllies += ' ' + localText.getText("TXT_KEY_AND", ()) + gc.getPlayer(iAllied).getCivilizationShortDescription(2)
				if ( iPlayer != iFreeFrench and gc.getPlayer(iFreeFrench).isAlive() ):
					if strAllies == '':
						strAllies += gc.getPlayer(iFreeFrench).getCivilizationShortDescription(2)
					else:
						strAllies += ' ' + localText.getText("TXT_KEY_AND", ()) + gc.getPlayer(iFreeFrench).getCivilizationShortDescription(2)
			popup = PyPopup.PyPopup()
			popup.setHeaderString( localText.getText("TXT_KEY_WW2_EVENT_VICTORY", ()) )
			popup.setBodyString( localText.getText("TXT_KEY_WW2_EVENT_DEFEAT_CIV", (strPlayerAdj, strAllies)) )
			popup.launch()

	def displayWelcomePopup( self ):
		"""At the start of the game, display a welcome message."""
		popup = PyPopup.PyPopup()
		popup.setHeaderString( localText.getText("TXT_KEY_DAWN_OF_MAN_SCREEN_TITLE", ()) )
		popup.setBodyString( localText.getText("TXT_KEY_WW2_EVENT_BEGIN", ()) )
		popup.launch()

#######################################
### Main methods (Event-Triggered) ###
#####################################

	def welcome( self ):
		"""Sets everything up at the start of the game."""
		# set the target score
#		gc.getGame().setTargetScore(len(tObjectivesList))

		# make Crete riot
#		getCity(tIraklion).setOccupationTimer(2)

		# initialise script data
		self.setupScriptData()

		# display welcome message
		self.displayWelcomePopup()

	def checkPlayerTurnEvents( self, iGameTurn, iPlayer ):
		"""Checks at the start of each player`s turn if an event should be triggered."""

		# Event: Afrika Korps Arrive
		# Trigger: Turn 7
		# Effect: Germany receive 2 Inf., 1 Panzer IV, 1 Fighter, 1 Bomber and Rommel in Tripoli; 
		#         gets Desert Fox tech.
		if ( iGameTurn == 7 and iPlayer == iGermans ):
			# give Germans Desert Fox tech
			self.giveTech(iDesertFox, iGermans)
			# determine city to place units in: by default Tripoli
			if self.isCityAxis( getCity(tTripoli) ):
				city = getCity(tTripoli)
			else:
				# find a nearby alternative city in Africa, east of Tripoli if possible
				tWestAfricaList.reverse()	# reverse order of search (from east to west)
				city = self.findCity(tEastAfricaList + tWestAfricaList, [], iAxis, bForceCoastal)
				tWestAfricaList.reverse()
			# only do the event if a city could be found
			if city:
				# create the units in the city
				self.makeUnit(iGermanInfantry, iGermans, city.plot(), 2)
				self.makeUnit(iPanzerIV, iGermans, city.plot(), 2)
				self.makeUnit(iMesserschmidt, iGermans, city.plot(), 1)
				self.makeUnit(iStuka, iGermans, city.plot(), 1)
				unitList = self.makeUnit(iRommel, iGermans, city.plot(), 1)
				if gc.getGame().getActivePlayer() == iGermans:
					CyInterface().selectUnit(unitList[0], True, False, True)
				# display message and focus camera on new units for Axis team
				self.displayPopupTo("TXT_KEY_WW2_EVENT_AFRIKA_KORPS", 
								(city.getName(), ), iAxis, city.plot())

		# Event: Operation Brevity
		# Trigger: Turn 22
		# Effect: British receive 2 Light Tanks in Alexandria if Allies team is not in control of Tobruk.
		if ( iGameTurn == 22 and iPlayer == iBritish ):
			# only do the event if Tobruk is not Allies-controlled yet
			if not self.isCityAllies( getCity(tTobruk) ):
				# determine city to place units in: by default Alexandria
				if self.isCityAllies( getCity(tAlexandria) ):
					city = getCity(tAlexandria)
				else:
					# find an alternative coastal city in Africa, the Mid-East or the Med
					tLibyaList.reverse()
					tWestAfricaList.reverse()
					tMediterraneanList.reverse()
					city = self.findCity(tEgyptList + tLibyaList + tWestAfricaList +   \
						tArabiaList + tMediterraneanList, [], iAllies, bForceCoastal)
					tLibyaList.reverse()
					tWestAfricaList.reverse()
					tMediterraneanList.reverse()
				# only do the event if a city could be found
				if city:
					# create the units in the city
					unitList = self.makeUnit(iCrusader, iBritish, city.plot(), 2)
					if gc.getGame().getActivePlayer() == iBritish:
						CyInterface().selectUnit(unitList[0], True, False, True)
					# display message and focus camera on new units for Allies team
					self.displayPopupTo("TXT_KEY_WW2_EVENT_OPERATION_BREVITY", 
								(city.getName(), ), iAllies, city.plot())
			# display error message in case Tobruk is already taken
			elif self.isPlayerAllies( gc.getGame().getActivePlayer() ):
					self.displayPopup("TXT_KEY_WW2_EVENT_OPERATION_BREVITY_ERROR", ())

		# Event: Operation Barbarossa
		# Trigger: Turn 26-36
		# Event: Germany pay 50% extra Unit Maintenance for 10 turns; 
		#        all civs get Operation Barbarossa tech.
		if iGameTurn == 26:
			# give everyone Operation Barbarossa tech
			self.giveTech(iBarbarossa, iPlayer)
			if iPlayer == iGermans:		# only do this once, for which player is unimportant
				self.setOperationBarbarossa(True)
				self.displayPopupTo("TXT_KEY_WW2_EVENT_OPERATION_BARBAROSSA", (), iNoFocus)
		# for the next 10 turns, give Germany +50% unit cost
		if ( (iGameTurn >= 26 and iGameTurn < 36) and iPlayer == iGermans ):
			self.setExtraUnitCost( gc.getPlayer(iGermans).calculateUnitCost() / 2 )
			gc.getPlayer(iGermans).changeGold( -self.getExtraUnitCost() )
		# reset the unit cost and gold string afterwards
		if ( iGameTurn == 36 and iPlayer == iGermans ):
			self.setOperationBarbarossa(False)
			self.setExtraUnitCost(0)

		# Event: Pearl Harbor
		# Trigger: Turn 44
		# Effect: Allied Nations can build Air Units and Carriers;
		#         Allies team can build Rats of Tobruk NW
		if ( iGameTurn == 44 and iPlayer == iAllied ):
			# give Allied Nations Pearl Harbor tech
			self.giveTech(iPearlHarbor, iPlayer)
			self.displayPopupTo("TXT_KEY_WW2_EVENT_PEARL_HARBOR", (), iNoFocus)

		# Event: Counter-offensive 
		# Trigger: Turn 50
		# Effect: Germany receive 2 Light Tanks in Tripoli if Axis team is not in control of Tobruk.
		if ( iGameTurn == 50 and iPlayer == iGermans ):
			# only do the event if Tobruk is not Axis anymore
			if not self.isCityAxis( getCity(tTobruk) ):
				# determine city to place units in: by default Tripoli
				if self.isCityAxis( getCity(tTripoli) ):
					city = getCity(tTripoli)
				else:
					# find an alternative city in Africa
					tWestAfricaList.reverse()
					city = self.findCity(tEastAfricaList +	\
								tWestAfricaList, [], iAxis, bForceCoastal)
					tWestAfricaList.reverse()
				# only do the event if a city could be found
				if city:
					# create the units in the city
					unitList = self.makeUnit(iPanzerIII, iGermans, city.plot(), 2)
					if gc.getGame().getActivePlayer() == iGermans:
						CyInterface().selectUnit(unitList[0], True, False, True)
					# display message and focus camera on new units for Axis team
					self.displayPopupTo("TXT_KEY_WW2_EVENT_COUNTEROFFENSIVE", 
								(city.getName(), ), iAxis, city.plot())
			# display error message in case Tobruk is already taken
			elif self.isPlayerAxis( gc.getGame().getActivePlayer() ):
				self.displayPopup("TXT_KEY_WW2_EVENT_COUNTEROFFENSIVE_ERROR", ())

		# Event: Montgomery Arrives
		# Trigger: Turn 80
		# Effect: British receive 2 Heavy Tanks in Alexandria.
		if ( iGameTurn == 80 and iPlayer == iBritish ):
			# determine city to place units in: by default Alexandria
			if self.isCityAllies( getCity(tAlexandria) ):
				city = getCity(tAlexandria)
			else:
				# find an alternative coastal city in Africa, the Mid-East or the Med
				tLibyaList.reverse()
				tWestAfricaList.reverse()
				tMediterraneanList.reverse()
				city = self.findCity(tEgyptList + tLibyaList + tWestAfricaList + tAsiaList   \
							+ tMediterraneanList, [], iAllies, bForceCoastal)
				tLibyaList.reverse()
				tWestAfricaList.reverse()
				tMediterraneanList.reverse()
			# only do the event if a city could be found
			if city:
				# create the units in the city
				unitList = self.makeUnit(iMatilda, iBritish, city.plot(), 2)
				if gc.getGame().getActivePlayer() == iBritish:
					CyInterface().selectUnit(unitList[0], True, False, True)
				# display message and focus camera on new units for Allies team
				self.displayPopupTo("TXT_KEY_WW2_EVENT_MONTGOMERY", 
								(city.getName(), ), iAllies, city.plot())

		# Event: Stalingrad & South Russia
		# Trigger: Turn 84(-94)
		# Effect: If Middle East event has already occured, do South Russia: 
		#         - Germans get 3 Light Tanks, 3 Infantry somewhere in Greece if Greece is still Axis;
		#         If Middle East event hasn't occured yet, do Stalingrad: 
		#         - Happiness in German cities drops 1 for 10 turns.
		if ( iGameTurn == 84 and iPlayer == iGermans ):
			if not self.isMiddleEast():		# Stalingrad
				self.setStalingrad(True)
				gc.getPlayer(iGermans).changeExtraHappiness(-1)	# only need to do this once
				if self.isPlayerAxis( gc.getGame().getActivePlayer() ):
					self.displayPopup("TXT_KEY_WW2_EVENT_STALINGRAD", ())
			else:					# South Russia
				tGreeceList.reverse()
				city = self.findCity(tGreeceList, [], iAxis, not bForceCoastal)
				tGreeceList.reverse()
				if city:
					self.makeUnit(iGermanInfantry, iGermans, city.plot(), 3)
					unitList = self.makeUnit(iPanzerIII, iGermans, city.plot(), 3)
					if gc.getGame().getActivePlayer() == iGermans:
						CyInterface().selectUnit(unitList[0], True, False, True)
					# display message focus camera on new units for Axis team
					self.displayPopupTo("TXT_KEY_WW2_EVENT_STHRUSSIA", (), iAxis, city.plot())
		# reset gold string and unhappy citizen afterwards
		if ( iGameTurn == 94 and iPlayer == iGermans and self.isStalingrad() ):
			gc.getPlayer(iGermans).changeExtraHappiness(1)
			self.setStalingrad(False)

		# Event: Operation Torch
		# Trigger: Turn 87
		# Effect: Americans acquire Operation Torch Technology. American Reinforcements arrive outside Gibraltar,
		#         containing 1 Battleship, 2 Destroyers, 2 Transports containing 4 Infantry & 2 Light Tanks in total.
		if ( iGameTurn == 87 and iPlayer == iAllied ):
			# give Allied Nations Operation Torch tech
			self.giveTech(iTorch, iAllied)
			# create units near Gibraltar
			pStraight = self.findFreePlotNear(tGibraltar, 10, bUsePythagoras, self.operationTorch)
			self.makeUnit(iATransport, iAllied, pStraight, 2)
			self.makeUnit(iDestroyer, iAllied, pStraight, 2)
			self.makeUnit(iAlliedInfantry, iAllied, pStraight, 4)
			self.makeUnit(iVickers, iAllied, pStraight, 2)
			unitList = self.makeUnit(iBattleship, iAllied, pStraight, 1)
			if gc.getGame().getActivePlayer() == iAllied:
				CyInterface().selectUnit(unitList[0], True, False, True)
			# display message and focus camera on new units for Allies team, use capital as parameter
			if not gc.getPlayer(iAllied).getCapitalCity().isNone():
				self.displayPopupTo("TXT_KEY_WW2_EVENT_OPERATION_TORCH", 
					(gc.getPlayer(iAllied).getCapitalCity().getName(), ), iAllies, pStraight)
			else:
				# display message and focus camera on new units for Allies team, use first city
				self.displayPopupTo("TXT_KEY_WW2_EVENT_OPERATION_TORCH", 
					(gc.getPlayer(iAllied).getCity(0).getName(), ), iAllies, pStraight)

		# Event: War in Italy
		# Trigger: Turn 132
		# Effect: If Allies team controls Tunis and a city on Sicily, and the Italians have 2 cities 
		#         or less on the African continent,
		#         Americans receive 1 Transport Ship and 1 Carrier with 2 Bombers.
		if ( iGameTurn == 132 and iPlayer == iAllied ):
			if ( ( self.isCityAllies( getCity(tPalermo) ) or self.isCityAllies( getCity(tMessina) ) )	\
						and self.isCityAllies( getCity(tTunis) )				\
						and self.countCitiesInRegion(iItalians, tAfricaList, not bForceCoastal) <= 2 ):
				# create units in one of the Sicilian cities
				if self.isCityAllies( getCity(tMessina) ):
					city = getCity(tMessina)
				else:
					city = getCity(tPalermo)
				self.makeUnit(iATransport, iAllied, city.plot(), 1)
				self.makeUnit(iB25, iAllied, city.plot(), 2)
				unitList = self.makeUnit(iACarrier, iAllied, city.plot(), 1)
				if gc.getGame().getActivePlayer() == iAllied:
					CyInterface().selectUnit(unitList[0], True, False, True)
				# display message and focus camera on new units for Allies team
				self.displayPopupTo("TXT_KEY_WW2_EVENT_ITALY_INVADED", (), iAllies, city.plot())
			# display error message in case Italian presence in NA is still too strong
			elif self.countCitiesInRegion(iItalians, tAfricaList, not bForceCoastal) > 2:
				if self.isPlayerAllies(gc.getGame().getActivePlayer()):
					self.displayPopup("TXT_KEY_WW2_EVENT_ITALY_INVADED_NA_ERROR", ())
			# display error message in case Sicily is not in Allies hands
			elif ( not self.isCityAllies(getCity(tPalermo)) and not self.isCityAllies(getCity(tMessina)) ):
				if self.isPlayerAllies(gc.getGame().getActivePlayer()):
					self.displayPopup("TXT_KEY_WW2_EVENT_ITALY_INVADED_SICILY_ERROR", ())
			# display error message in case Tunis is not in Allies hands
			elif self.isPlayerAllies(gc.getGame().getActivePlayer()):
					self.displayPopup("TXT_KEY_WW2_EVENT_ITALY_INVADED_ERROR", ())

		# Event: Random Events
		# Trigger: Random
		# Effect: Each turn for each player there's a 3% chance that a random event will happen.
		iRndNum = gc.getGame().getSorenRandNum(100, 'Desert War - Random Event Start')
		if iRndNum < 3:			# 3% chance
			iEventType = gc.getGame().getSorenRandNum(7, 'Desert War - Random Event Type')	# 0-6
			if gc.getGame().getActivePlayer() == iPlayer:
				popup = PyPopup.PyPopup()
				pFocus = gc.getPlayer(iPlayer).getCity(0).plot()
				bLaunch = False
			# 1 in 7 chance of getting each of the 7 events
			if iEventType == 0:
				# give player a random amount of between 100 and 300 gold
				iAmount = 50 + gc.getGame().getSorenRandNum(51, 'Desert War - Random Event Gold')
				gc.getPlayer(iPlayer).changeGold(iAmount)
				if gc.getGame().getActivePlayer() == iPlayer:
					popup.setBodyString( localText.getText("TXT_KEY_WW2_EVENT_RAND_GOLD", (iAmount, )) )
					bLaunch = True
			elif iEventType == 1:
				# gain a random number of between 20 and 40 Hammers in a random city
				iAmount = 20 + gc.getGame().getSorenRandNum(21, 'Desert War - Random Event Hammers Added')
				pyCityList = PyPlayer(iPlayer).getCityList()
				iCity = gc.getGame().getSorenRandNum(len(pyCityList), 'Desert War - Random Event City')
				city = pyCityList[iCity].GetCy()
				city.changeProduction(iAmount)
				if gc.getGame().getActivePlayer() == iPlayer:
					pFocus = city.plot()
					popup.setHeaderString( localText.getText("TXT_KEY_WW2_EVENT_RAND_SUPPLYGAIN_TITLE", ()) )
					popup.setBodyString( localText.getText("TXT_KEY_WW2_EVENT_RAND_SUPPLYGAIN_PROD", (city.getName(), iAmount, )) )
					bLaunch = True
			elif iEventType == 2:
				# lose a random number of between 20 and 40 Hammers in a random city
				iAmount = -20 - gc.getGame().getSorenRandNum(21, 'Desert War - Random Event Hammers Removed')
				pyCityList = PyPlayer(iPlayer).getCityList()
				iCity = gc.getGame().getSorenRandNum(len(pyCityList), 'Desert War - Random Event City')
				city = pyCityList[iCity].GetCy()
				city.changeProduction(iAmount)
				if gc.getGame().getActivePlayer() == iPlayer:
					pFocus = city.plot()
					popup.setHeaderString( localText.getText("TXT_KEY_WW2_EVENT_RAND_SUPPLYLOST_TITLE", ()) )
					popup.setBodyString( localText.getText("TXT_KEY_WW2_EVENT_RAND_SUPPLYLOST_PROD", (city.getName(), -iAmount, )) )
					bLaunch = True
			elif iEventType == 3:
				# gain a Medic promotion for a random Infantry unit that has none
				unitList = PyPlayer(iPlayer).getUnitList()
				uValidList = []
				bFoundUnit = False
				for unit in unitList:
					if self.isNonMedicInfantry(unit):
						uValidList.append(unit)
						bFoundUnit = True
				if bFoundUnit:
					iUnit = gc.getGame().getSorenRandNum(len(uValidList), 'Desert War - Random Event Medic Added')
					unit = uValidList[iUnit]
					unit.setHasPromotion(iMedicI, True)
					if gc.getGame().getActivePlayer() == iPlayer:
						CyInterface().selectUnit(unit, True, False, False)
						pFocus = unit.plot()
						popup.setHeaderString( localText.getText("TXT_KEY_WW2_EVENT_RAND_SUPPLYGAIN_TITLE", ()) )
						popup.setBodyString( localText.getText("TXT_KEY_WW2_EVENT_RAND_SUPPLYGAIN_MEDIC", ()) )
						bLaunch = True
			elif iEventType == 4:
				# lose a Medic promotion from a random Infantry unit that has one
				unitList = PyPlayer(iPlayer).getUnitList()
				uValidList = []
				bFoundUnit = False
				for unit in unitList:
					if self.isMedicInfantry(unit):
						uValidList.append(unit)
						bFoundUnit = True
				if bFoundUnit:
					iUnit = gc.getGame().getSorenRandNum(len(uValidList), 'Desert War - Random Event Medic Removed')
					unit = uValidList[iUnit]
					if unit.isHasPromotion(iMedicII):
						unit.setHasPromotion(iMedicII, False)
					else:
						unit.setHasPromotion(iMedicI, False)
					if gc.getGame().getActivePlayer() == iPlayer:
						CyInterface().selectUnit(unit, True, False, False)
						pFocus = unit.plot()
						popup.setHeaderString( localText.getText("TXT_KEY_WW2_EVENT_RAND_SUPPLYLOST_TITLE", ()) )
						popup.setBodyString( localText.getText("TXT_KEY_WW2_EVENT_RAND_SUPPLYLOST_MEDIC", ()) )
						bLaunch = True
			elif iEventType == 5:
				# gain a Repair promotion for a random Light Tank unit that has none
				unitList = PyPlayer(iPlayer).getUnitList()
				uValidList = []
				bFoundUnit = False
				for unit in unitList:
					if self.isNonRepairTank(unit):
						uValidList.append(unit)
						bFoundUnit = True
				if bFoundUnit:
					iUnit = gc.getGame().getSorenRandNum(len(uValidList), 'Desert War - Random Event Repair Added')
					unit = uValidList[iUnit]
					unit.setHasPromotion(iRepair, True)
					if gc.getGame().getActivePlayer() == iPlayer:
						CyInterface().selectUnit(unit, True, False, False)
						pFocus = unit.plot()
						popup.setHeaderString( localText.getText("TXT_KEY_WW2_EVENT_RAND_SUPPLYGAIN_TITLE", ()) )
						popup.setBodyString( localText.getText("TXT_KEY_WW2_EVENT_RAND_SUPPLYGAIN_REPAIR", ()) )
						bLaunch = True
			else:
				# lose a Repair promotion from a random Light Tank unit that has one
				unitList = PyPlayer(iPlayer).getUnitList()
				uValidList = []
				bFoundUnit = False
				for unit in unitList:
					if self.isRepairTank(unit):
						uValidList.append(unit)
						bFoundUnit = True
				if bFoundUnit:
					iUnit = gc.getGame().getSorenRandNum(len(uValidList), 'Desert War - Random Event Repair Removed')
					unit = uValidList[iUnit]
					unit.setHasPromotion(iRepair, False)
					if gc.getGame().getActivePlayer() == iPlayer:
						CyInterface().selectUnit(unit, True, False, False)
						pFocus = unit.plot()
						popup.setHeaderString( localText.getText("TXT_KEY_WW2_EVENT_RAND_SUPPLYLOST_TITLE", ()) )
						popup.setBodyString( localText.getText("TXT_KEY_WW2_EVENT_RAND_SUPPLYLOST_REPAIR", ()) )
						bLaunch = True
			# when done, focus camera and display a message to the player
			if ( gc.getGame().getActivePlayer() == iPlayer and bLaunch ):
				cam = CvCameraControls.CvCameraControls()
				cam.centerCamera(pFocus)
				popup.launch()

		# Event: Italian capitulation
		# Trigger: Turn after conquest of Naples by Allies - 20 turns after conquest of Naples by Allies
		# Effect: Naples must be re-taken by Axis forces within 20 turns, or Italian player is eliminated.

		# note: self.isCapTimerOn() is set to True at conquest of Naples by Allies, 
		#       self.isEndCapTimer() is set to True after recapture of Naples or Italian capitulation
		if ( self.isCapTimerOn() and not self.isEndCapTimer() and iPlayer == iItalians ):
			# for the first 20 turns, run timer
			if self.getCapTimer() < 2:
				self.setCapTimer(self.getCapTimer() + 1)
			# when timer expires, eliminate Italy
			else:
				# if still alive at this point
				if gc.getPlayer(iItalians).isAlive():
					pyItalians = PyPlayer(iItalians)
					pyCityList = pyItalians.getCityList()
					# give all cities to other players, depending on its location
					for pyCity in pyCityList:
						city = pyCity.GetCy()
						tCoords = (city.getX(), city.getY())
						if tCoords in tTurkeyList:
							gc.getPlayer(iTurkish).acquireCity(city, True, False)
						elif tCoords in tSpainList:
							gc.getPlayer(iSpanish).acquireCity(city, True, False)
						elif tCoords in tGreeceList:
							gc.getPlayer(iGermans).acquireCity(city, True, False)
						elif tCoords in tMediterraneanList:
							gc.getPlayer(iAllied).acquireCity(city, True, False)
						elif tCoords in tItalyList:
							gc.getPlayer(iGermans).acquireCity(city, True, False)
						elif tCoords in tArabiaList:
							gc.getPlayer(iFreeFrench).acquireCity(city, True, False)
						elif tCoords in tEastAfricaList:
							gc.getPlayer(iBritish).acquireCity(city, True, False)
						elif tCoords in tWestAfricaList:
							gc.getPlayer(iVichyFrench).acquireCity(city, True, False)
						else:	# shouldn't happen
							gc.getPlayer(iTurkish).acquireCity(city, True, False)
					# kill all Italian units
					for unit in pyItalians.getUnitList():
						unit.kill(True)
					# move all Axis units inside former Italian cities to nearby Axis cities
					for pyCity in pyCityList:
						city = pyCity.GetCy()
						for i in range(city.plot().getNumUnits()):
							unit = city.plot().getUnit(0)
							if self.isPlayerAxis(unit.getOwner()):
								cNew = gc.getMap().findCity(city.getX(), city.getY(), -1, iAxis, False, False, -1, -1, city)
								unit.setXY(cNew.getX(), cNew.getY())
					# display message to all
					self.displayPopup("TXT_KEY_WW2_EVENT_NAPLES_CAPITULATION", ())
				# cancel timer
				self.setEndCapTimer(True)

	def checkGameTurnEvents( self, iGameTurn):
		"""Checks at the start of each game turn if an event should be triggered."""
		
		# Event: D-Day
		# Trigger: Turn 159, 161, 164
		# Effect: Some military units are disabled and unbuildable from this point.
		if ( iGameTurn == 159 ):
			# display warning message to everyone, 5 turns in advance
			self.displayPopup("TXT_KEY_WW2_EVENT_DDAY_NEAR", ())
		if ( iGameTurn == 161 ):
			# remove Army Support tech (which is a prerequisite of all units) from all players
			for iTeam in range(gc.getGame().countCivTeamsAlive()):
				gc.getTeam(iTeam).setHasTech(iArmySupport, False, 0, False, False)
			# display message (oh, baby, show me your workaround face)
			popup = PyPopup.PyPopup()
			popup.setHeaderString( localText.getText("TXT_KEY_WW2_EVENT_DDAY_TITLE", ()) )
			popup.setBodyString( localText.getText("TXT_KEY_WW2_EVENT_DDAY_FEWTROOPS", ()) )
			popup.launch()
		if ( iGameTurn == 164 ):
			# display message: D-Day is here
			self.displayPopup("TXT_KEY_WW2_EVENT_DDAY_ACTUAL", ())
			# set up Paris liberation, based on how strong Allies are compared to Axis
			self.setParisLiberation( iGameTurn + self.numTurnsBasedOnAssets(8, iAllies) )

		# Event: Paris Liberation
		# Trigger: From somewhere between turn 184-194 onwards, depending on relative strength of Allies
		# Effect: Happiness in Vichy French cities drops 2 permanently; 
		#         hhappiness in Free French cities rises 2 permanently.
		if ( iGameTurn == self.getParisLiberation() ):
			self.setParisLiberated(True)
			gc.getPlayer(iVichyFrench).changeExtraHappiness(-2)
			gc.getPlayer(iFreeFrench).changeExtraHappiness(2)
			# display message
			self.displayPopupTo("TXT_KEY_WW2_EVENT_PARIS_LIBERATED", (), iNoFocus)

		# Event: England Falls
		# Trigger: From somewhere between 16 and 22 turns after Gibraltar is conquered by the Axis
		# Effect: Happiness in Axis cities rises 2 permanently; happiness in Allies cities drops 2 permanently.
		if ( iGameTurn == self.getEnglandFalls() and self.isObjectiveCaptured(tGibraltar) ):
			self.setEnglandFallen(True)
			gc.getPlayer(iBritish).changeExtraHappiness(-2)
			gc.getPlayer(iAllied).changeExtraHappiness(-2)
			gc.getPlayer(iFreeFrench).changeExtraHappiness(-2)
			gc.getPlayer(iGermans).changeExtraHappiness(2)
			gc.getPlayer(iItalians).changeExtraHappiness(2)
			gc.getPlayer(iVichyFrench).changeExtraHappiness(2)
			# display message
			self.displayPopupTo("TXT_KEY_WW2_EVENT_ENGLANDFALLS", (), iNoFocus)

		# Event: VE-Day
		# Trigger: Turn 203, 208
		# Effect: Game Over
		if ( iGameTurn == 203 ):
			# display warning message, 5 turns in advance
			self.displayPopup("TXT_KEY_WW2_EVENT_VEDAY_APPROACHES", ())
		if ( iGameTurn == 208 ):
			if self.countAlliesObjectives() > self.countAxisObjectives():
				# display message
				self.displayPopupTo("TXT_KEY_WW2_EVENT_VEDAY_ALLIES_WIN", (), iNoFocus)
				# Allies win (more Objectives)
				gc.getGame().setWinner(iAllies, 1)
			elif self.countAlliesObjectives() > self.countAxisObjectives():
				# display message
				self.displayPopupTo("TXT_KEY_WW2_EVENT_VEDAY_AXIS_WIN", (), iNoFocus)
				# Axis win (more Objectives)
				gc.getGame().setWinner(iAxis, 1)
			elif gc.getTeam(iAllies).getAssets() > gc.getTeam(iAxis).getAssets():
				# display message
				self.displayPopupTo("TXT_KEY_WW2_EVENT_VEDAY_ALLIES_WIN", (), iNoFocus)
				# Allies win (equal VC, higher score)
				gc.getGame().setWinner(iAllies, 1)
			else:	# Axis win (theoretically could still be a draw but then the Axis beat history)
				# display message
				self.displayPopupTo("TXT_KEY_WW2_EVENT_VEDAY_AXIS_WIN", (), iNoFocus)
				# Axis win (equal VC, higher score)
				gc.getGame().setWinner(iAxis, 1)
			# display message: VE-Day is here (this message is shown first)
			self.displayPopup("TXT_KEY_WW2_EVENT_VEDAY", ())

		# Event: Victory Timer
		# Trigger: Whenever one tema controls all six Objectives
		# Effect: Count down to victory
		if ( (self.countAlliesObjectives() == 6 or self.countAxisObjectives() == 6) ):
			iCount = self.getVictoryTimer()
			self.setVictoryTimer(iCount - 1)
			# let calculateScore() know the game has been won
			if iCount == 1:
				self.setVictoryNextTurn(True)

	def checkCaptureEvents( self, iOwner, city, iConqueror ):
		"""Checks at the capture of each city if an event should be triggered and if so, triggers it."""

		# Event: Italian capitulation
		# Trigger: Conquest of Naples by Allies
		# Effect: Naples must be re-taken by Axis forces within 20 turns, or Italian player is eliminated.

		# if naples in conquered for the first time, start the timer
		if ( self.equals(city, getCity(tNaples)) and self.isPlayerAxis(iOwner) and self.isPlayerAllies(iConqueror) and not self.isCapTimerOn() ):
			# start the timer (and only start it once)
			self.setCapTimerOn(True)
			# display message
			self.displayPopupTo("TXT_KEY_WW2_EVENT_NAPLES_CAPTURED", (5, ), iNoFocus)
		# if naples is re-captured by the Axis while the timer runs, cancel the timer and send German reinforcements
		elif ( self.equals(city, getCity(tNaples)) and self.isPlayerAllies(iOwner) and self.isPlayerAxis(iConqueror) and not self.isEndCapTimer() ):
			# cancel timer
			self.setEndCapTimer(True)
			self.makeUnit(iGermanInfantry, iGermans, getCity(tNaples).plot(), 2)
			unitList = self.makeUnit(iTiger, iGermans, getCity(tNaples).plot(), 1)
			if gc.getGame().getActivePlayer() == iGermans:
				CyInterface().selectUnit(unitList[0], True, False, True)
			# display message
			self.displayPopupTo("TXT_KEY_WW2_EVENT_NAPLES_RECAPTURED", (), iNoFocus)

		# Event: Middle East
		# Trigger: First Time Axis controls both Suez and Damascus
		# Effect: Germans get 1 Battleship, 2 Destroyers, 2 Subs in Suez; British lose oil in Al-Aqabah
		if ( (not self.isMiddleEast()) and self.isPlayerAxis(iConqueror) and ( (self.equals(city, getCity(tDamascus)) and self.isCityAxis(getCity(tSuez))) or 
										(self.equals(city, getCity(tSuez)) and self.isCityAxis(getCity(tDamascus))) ) ):
			self.setMiddleEast(True)
			# create the units in Suez
			cityTmp = getCity(tSuez)
			self.makeUnit(iDestroyer, iGermans, cityTmp.plot(), 2)
			self.makeUnit(iSubmarine, iGermans, cityTmp.plot(), 2)
			unitList = self.makeUnit(iBattleship, iGermans, cityTmp.plot(), 1)
			if gc.getGame().getActivePlayer() == iGermans:
				CyInterface().selectUnit(unitList[0], True, False, True)
			# destroy the Oil in Al-Aqabah
#			pAlAqabahOilField = gc.getMap().plot(tAlAqabahOilField[iX], tAlAqabahOilField[iY])
#			pAlAqabahOilField.setBonusType(-1)	# no resource
			# display message and focus camera on new units for Axis team
			self.displayPopupTo("TXT_KEY_WW2_EVENT_MIDDLEEAST", (), iAxis, cityTmp.plot())

		# Event: Battle of Kasserine Pass
		# Trigger: First Time Axis Forces are down to a single coastal city in Africa
		# Effect: If Axis side only control a single coastal city in Africa:
		#         Italy receive 1 Infantry (w. Guerilla promotion) in that city;
		#         Germany receive 2 Infantry (w. Guerilla promotion) in that city.
		if self.countCitiesInRegion(iGermans, tAfricaList, True) + self.countCitiesInRegion(iItalians, tAfricaList, True) +	\
									self.countCitiesInRegion(iVichyFrench, tAfricaList, True) == 1:
			if not self.isKasserinePass():
				self.setKasserinePass(True)								# do this only once
				unitCity = self.findCity(tAfricaList, [(city.getX(), city.getY())], iAxis, True)	# there is exactly one city
				# create the units in last remaining coastal city and promote them
				unitList = self.makeUnit(iGermanInfantry, iGermans, unitCity.plot(), 2)
				for unit in unitList:
					unit.setHasPromotion(iGuerillaI, True)
				if gc.getGame().getActivePlayer() == iGermans:
					CyInterface().selectUnit(unitList[0], True, False, True)
				unitList = self.makeUnit(iItalianInfantry, iItalians, unitCity.plot(), 1)
				for unit in unitList:
					unit.setHasPromotion(iGuerillaI, True)
				if gc.getGame().getActivePlayer() == iItalians:
					CyInterface().selectUnit(unitList[0], True, False, True)
				# display message and focus camera on new units for Axis team
				self.displayPopupTo("TXT_KEY_WW2_EVENT_KASSERINE_PASS", (unitCity.getName(), ), iAxis, unitCity.plot())

		# Event: Mareth Line breakthrough
		# Trigger: First Time Axis Forces are down to 0 coastal cities in Africa
		# Effect: First Time Axis Forces are down to 0 coastal cities in Africa
		#         Allied Nations receive 2 Infantry with Ambush promotion in Tunis, British receive 1 heavy tank in Tunis;
		if self.countCitiesInRegion(iGermans, tAfricaList, True) + self.countCitiesInRegion(iItalians, tAfricaList, True) +	\
									self.countCitiesInRegion(iVichyFrench, tAfricaList, True) == 0:
			if not self.isMarethLine():
				self.setMarethLine(True)	# do this only once
				unitCity = getCity(tTunis)
				# create the units in Tunis
				unitList = self.makeUnit(iAlliedInfantry, iAllied, unitCity.plot(), 2)
				for unit in unitList:
					unit.setHasPromotion(iAmbush, True)
				if gc.getGame().getActivePlayer() == iAllied:
					CyInterface().selectUnit(unitList[0], True, False, True)
				unitList = self.makeUnit(iMatilda, iBritish, unitCity.plot(), 1)
				if gc.getGame().getActivePlayer() == iBritish:
					CyInterface().selectUnit(unitList[0], True, False, True)
				# display message and focus camera on new units for Allies team
				self.displayPopupTo("TXT_KEY_WW2_EVENT_MARETH_LINE", (), iAllies, unitCity.plot())

		# Event: Objective Cities
		# Trigger: First time capture of Objective City
		# Effect: Display a message to the new owner's team if a city which is an Objective has been captured
		if ( self.equals(city, getCity(tSuez)) and self.isPlayerAxis(iConqueror) and not self.isObjectiveCaptured(tSuez) ):
			if self.isPlayerAxis(gc.getGame().getActivePlayer()):
				self.displayObjectivePopup("TXT_KEY_WW2_EVENT_VC_SUEZ")
			self.setObjectiveCaptured(tSuez)
		if ( self.equals(city, getCity(tAthens)) and self.isPlayerAllies(iConqueror) and not self.isObjectiveCaptured(tAthens) ):
			#if self.isPlayerAllies(gc.getGame().getActivePlayer()):
			#	self.displayObjectivePopup("TXT_KEY_WW2_EVENT_VC_CRETE_ALLIES")
			self.setObjectiveCaptured(tAthens)
		if ( self.equals(city, getCity(tIraklion)) and self.isPlayerAllies(iConqueror) and not self.isObjectiveCaptured(tIraklion) ):
			# add English resistance fighters in Greece if Axis in control of (some of) it
			if self.countCitiesInRegion(iGermans, tGreeceList, False) + self.countCitiesInRegion(iItalians, tGreeceList, False) +	\
									self.countCitiesInRegion(iVichyFrench, tGreeceList, False) > 0:
				pResistance = self.findFreePlotNear(tAthens, 8, bUsePythagoras, self.creteCaptured)
				if pResistance:
					unitList = self.makeUnit(iBritishInfantry, iBritish, pResistance, 2)
					if gc.getGame().getActivePlayer() == iBritish:
						CyInterface().selectUnit(unitList[0], True, False, True)
					city = gc.getMap().findCity(pResistance.getX(), pResistance.getY(), -1, iAxis, False, False, -1, -1, getCity(tSuez))
					# display message and focus camera on new units
					self.displayPopupTo("TXT_KEY_WW2_EVENT_CRETE", (city.getName(), ), iFocusBoth, pResistance)
			self.setObjectiveCaptured(tIraklion)
		if ( self.equals(city, getCity(tAlgiers)) and self.isPlayerAllies(iConqueror) and not self.isObjectiveCaptured(tAlgiers) ):
			#if self.isPlayerAllies(gc.getGame().getActivePlayer()):
			#	self.displayObjectivePopup("TXT_KEY_WW2_EVENT_VC_TUNIS")
			self.setObjectiveCaptured(tAlgiers)
		if ( self.equals(city, getCity(tDamascus)) and self.isPlayerAxis(iConqueror) and not self.isObjectiveCaptured(tDamascus) ):
			if self.isPlayerAxis(gc.getGame().getActivePlayer()):
				self.displayObjectivePopup("TXT_KEY_WW2_EVENT_VC_DAMASCUS")
			self.setObjectiveCaptured(tDamascus)
		if ( self.equals(city, getCity(tMessina)) and self.isPlayerAllies(iConqueror) and not self.isObjectiveCaptured(tMessina) ):
			if self.isPlayerAllies(gc.getGame().getActivePlayer()):
				self.displayObjectivePopup("TXT_KEY_WW2_EVENT_VC_SICILY_ALLIES")
			self.setObjectiveCaptured(tMessina)
		if ( self.equals(city, getCity(tGibraltar)) and self.isPlayerAxis(iConqueror) and not self.isObjectiveCaptured(tGibraltar) ):
			if self.isPlayerAxis(gc.getGame().getActivePlayer()):
				self.displayObjectivePopup("TXT_KEY_WW2_EVENT_GIBRALTAR_TEXT")
			self.setObjectiveCaptured(tGibraltar)
			# set up England Falls, based on how strong Axis are compared to Allies (between 4 and 6 months from now)
			self.setEnglandFalls( gc.getGame().getGameTurn() + self.numTurnsBasedOnAssets(16, iAxis) )

		# (re)set the victory timer if all 6 objectives are in one team's hands and one of the objectives changes owner
		if self.countAlliesObjectives() == 6 and (city.getX(), city.getY()) in tObjectivesList:
			self.setVictoryTimer(9)
			self.setVictoryNextTurn(False)
		if self.countAxisObjectives() == 6 and (city.getX(), city.getY()) in tObjectivesList:
			self.setVictoryTimer(9)
			self.setVictoryNextTurn(False)

	def victory( self ):
		"""Display a victory/defeat message when a player has won or lost."""
		self.setVictoryAchieved(True)		# in case player playes on beyond this point (will this be possible?)
		if self.countAlliesObjectives() == 6:
			if self.isPlayerAllies( gc.getGame().getActivePlayer() ):
				self.displayVictoryPopup("TXT_KEY_WW2_EVENT_ALLIES")
			if self.isPlayerAxis( gc.getGame().getActivePlayer() ):
				self.displayVictoryPopup("TXT_KEY_WW2_EVENT_DEFEAT_SIDE_AXIS")
		if self.countAxisObjectives() == 6:
			if self.isPlayerAllies( gc.getGame().getActivePlayer() ):
				self.displayVictoryPopup("TXT_KEY_WW2_EVENT_DEFEAT_SIDE_ALLIES")
			if self.isPlayerAxis( gc.getGame().getActivePlayer() ):
				self.displayVictoryPopup("TXT_KEY_WW2_EVENT_AXIS")

	def updateExtraUnitCosts( self ):
		"""For every event where units may have been created/destroyed, 
		update the Extra Unit Cost during Operation Barbarossa."""
		game = gc.getGame()
		if ( (game.getGameTurn() >= 26 and game.getGameTurn() < 36) and game.getActivePlayer() == iGermans ):
			self.setExtraUnitCost( gc.getPlayer(iGermans).calculateUnitCost() / 2 )



############################
### UI Override Methods ###
##########################


	def getGoldStr( self, iPlayer ):
		"""Override the gold string in CvMainInterface.py: returns the new gold string."""
		player = gc.getPlayer(iPlayer)
		if player.getGold() < 0:
			strGold = localText.getText("TXT_KEY_MISC_NEG_GOLD_STR_WWII", (player.getGold(), ))
		else:
			strGold = localText.getText("TXT_KEY_MISC_POS_GOLD_STR_WWII", (player.getGold(), ))
		if iPlayer == iGermans:
			iGoldRate = player.calculateGoldRate() - self.getExtraUnitCost()
		else:
			iGoldRate = player.calculateGoldRate()
		if iGoldRate < 0:
			strGold += localText.getText("TXT_KEY_MISC_NEG_GOLD_PER_TURN", (iGoldRate, ))
		elif iGoldRate > 0:
			strGold += localText.getText("TXT_KEY_MISC_POS_GOLD_PER_TURN", (iGoldRate, ))
		if player.isStrike():
			strGold += localText.getText("TXT_KEY_MISC_STRIKE", ())
		return strGold

	def updateEventStrings( self, iPlayer, screen):
		"""Display info strings during multi-turn events."""
		player = gc.getPlayer(iPlayer)
		iCount = 0
		# make the string
		if self.countAlliesObjectives() == 6 and not self.isVictoryAchieved():
			iTurns = self.getVictoryTimer() + 1
			if self.isPlayerAllies(iPlayer):
				strEvent = ""
				if iTurns == 1:
					strEvent = localText.getText("TXT_KEY_MISC_VICTORY_IMMINENT", ()) + ' ' + localText.getText("TXT_KEY_MISC_WEEKS_SIN", ())
				else:
					strEvent = localText.getText("TXT_KEY_MISC_VICTORY_IMMINENT", ()) + ' '  + localText.getText("TXT_KEY_MISC_WEEKS_PLU", (iTurns, ))
			elif self.isPlayerAxis(iPlayer):
				if iTurns == 1:
					strEvent = localText.getText("TXT_KEY_MISC_DEFEAT_IMMINENT", ()) + ' '  + localText.getText("TXT_KEY_MISC_WEEKS_SIN", ())
				else:
					strEvent = localText.getText("TXT_KEY_MISC_DEFEAT_IMMINENT", ()) + ' '  + localText.getText("TXT_KEY_MISC_WEEKS_PLU", (iTurns, ))
			screen.setText( "EventText" + str(iCount), "Background", strEvent, CvUtil.FONT_LEFT_JUSTIFY, 110, 45 + iCount*17, -0.1, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
			iCount = iCount + 1
		elif self.countAxisObjectives() == 6 and not self.isVictoryAchieved():
			iTurns = self.getVictoryTimer() + 1
			if self.isPlayerAllies(iPlayer):
				strEvent = ""
				if iTurns == 1:
					strEvent = localText.getText("TXT_KEY_MISC_DEFEAT_IMMINENT", ()) + ' '  + localText.getText("TXT_KEY_MISC_WEEKS_SIN", ())
				else:
					strEvent = localText.getText("TXT_KEY_MISC_DEFEAT_IMMINENT", ()) + ' '  + localText.getText("TXT_KEY_MISC_WEEKS_PLU", (iTurns, ))
			elif self.isPlayerAxis(iPlayer):
				if iTurns == 1:
					strEvent = localText.getText("TXT_KEY_MISC_VICTORY_IMMINENT", ()) + ' '  + localText.getText("TXT_KEY_MISC_WEEKS_SIN", ())
				else:
					strEvent = localText.getText("TXT_KEY_MISC_VICTORY_IMMINENT", ()) + ' '  + localText.getText("TXT_KEY_MISC_WEEKS_PLU", (iTurns, ))
			screen.setText( "EventText" + str(iCount), "Background", strEvent, CvUtil.FONT_LEFT_JUSTIFY, 110, 45 + iCount*17, -0.1, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
			iCount = iCount + 1

		if self.isCapTimerOn() and not self.isEndCapTimer():
			iTurns = 20 - self.getCapTimer()
			strEvent = ""
			if iTurns == 1:
				strEvent = localText.getText("TXT_KEY_MISC_ITALIAN_CAPITULATION", ()) + ' '  + localText.getText("TXT_KEY_MISC_WEEKS_SIN", ())
			else:
				strEvent = localText.getText("TXT_KEY_MISC_ITALIAN_CAPITULATION", ()) + ' '  + localText.getText("TXT_KEY_MISC_WEEKS_PLU", (iTurns, ))
			screen.setText( "EventText" + str(iCount), "Background", strEvent, CvUtil.FONT_LEFT_JUSTIFY, 110, 45 + iCount*17, -0.1, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
			iCount = iCount + 1
		if self.isOperationBarbarossa() and iPlayer == iGermans:
			strEvent = localText.getText("TXT_KEY_TECH_BARBAROSSA", ())
			screen.setText( "EventText" + str(iCount), "Background", strEvent, CvUtil.FONT_LEFT_JUSTIFY, 110, 45 + iCount*17, -0.1, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
			iCount = iCount + 1
		if self.isStalingrad() and iPlayer == iGermans:
			strEvent = localText.getText("TXT_KEY_TECH_STALINGRAD", ())
			screen.setText( "EventText" + str(iCount), "Background", strEvent, CvUtil.FONT_LEFT_JUSTIFY, 110, 45 + iCount*17, -0.1, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
			iCount = iCount + 1
		if self.isParisLiberated() and (iPlayer == iVichyFrench or iPlayer == iFreeFrench) and not self.isVictoryAchieved():
			strEvent = localText.getText("TXT_KEY_MISC_PARIS_LIBERATED", ())
			screen.setText( "EventText" + str(iCount), "Background", strEvent, CvUtil.FONT_LEFT_JUSTIFY, 110, 45 + iCount*17, -0.1, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
			iCount = iCount + 1
		if self.isEnglandFallen() and not self.isVictoryAchieved():
			strEvent = localText.getText("TXT_KEY_MISC_ENGLAND_FALLEN", ())
			screen.setText( "EventText" + str(iCount), "Background", strEvent, CvUtil.FONT_LEFT_JUSTIFY, 110, 45 + iCount*17, -0.1, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
			iCount = iCount + 1
#		screen.show( "EventText" )

	def updateScoreStrings(self, screen, xResolution):
		iCount = 0
		if (self.countAxisObjectives()) > 0:
			# title
			szText = u"<font=2>" + localText.getText("TXT_KEY_MISC_OBJECTIVE_CITIES", ()) + ' - ' + localText.getText("TXT_KEY_TECH_AXIS", ()) + ': ' + str(self.countAxisObjectives()) + "</font>"
			screen.setText( "ObjectivesText" + str(iCount), "Background", szText, CvUtil.FONT_LEFT_JUSTIFY, xResolution - 155, 93 + iCount*13, -0.1, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
			iCount = iCount + 1
			# cities
			for tCoords in tObjectivesList:
				city = getCity(tCoords)
				if self.isCityAxis(city):
					szText = u"<font=2><color=%d,%d,%d,%d>%s</color></font>" %(gc.getPlayer(city.getOwner()).getPlayerTextColorR(), gc.getPlayer(city.getOwner()).getPlayerTextColorG(), gc.getPlayer(city.getOwner()).getPlayerTextColorB(), gc.getPlayer(city.getOwner()).getPlayerTextColorA(), city.getName() + '      ')
					screen.setText( "ObjectivesText" + str(iCount), "Background", szText, CvUtil.FONT_LEFT_JUSTIFY, xResolution - 155, 93 + iCount*13, -0.1, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
					iCount = iCount + 1
		if (self.countAlliesObjectives()) > 0:
			# title
			szText = u"<font=2>" + localText.getText("TXT_KEY_MISC_OBJECTIVE_CITIES", ()) + ' - ' + localText.getText("TXT_KEY_TECH_ALLIES", ()) + ': ' + str(self.countAlliesObjectives()) + "</font>"
			screen.setText( "ObjectivesText" + str(iCount), "Background", szText, CvUtil.FONT_LEFT_JUSTIFY, xResolution - 155, 93 + iCount*13, -0.1, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
			iCount = iCount + 1
			# cities
			for tCoords in tObjectivesList:
				city = getCity(tCoords)
				if self.isCityAllies(city):
					szText = u"<font=2><color=%d,%d,%d,%d>%s</color></font>" %(gc.getPlayer(city.getOwner()).getPlayerTextColorR(), gc.getPlayer(city.getOwner()).getPlayerTextColorG(), gc.getPlayer(city.getOwner()).getPlayerTextColorB(), gc.getPlayer(city.getOwner()).getPlayerTextColorA(), city.getName() + '      ')
					screen.setText( "ObjectivesText" + str(iCount), "Background", szText, CvUtil.FONT_LEFT_JUSTIFY, xResolution - 155, 93 + iCount*13, -0.1, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
					iCount = iCount + 1
		if (self.countNeutralObjectives()) > 0:
			# title
			szText = u"<font=2>" + localText.getText("TXT_KEY_MISC_OBJECTIVE_CITIES", ()) + ' - ' + localText.getText("TXT_KEY_MISC_OBJECTIVE_OTHER", ()) + ': ' + str(self.countNeutralObjectives()) + "</font>"
			screen.setText( "ObjectivesText" + str(iCount), "Background", szText, CvUtil.FONT_LEFT_JUSTIFY, xResolution - 155, 93 + iCount*13, -0.1, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
			iCount = iCount + 1
			# cities
			for tCoords in tObjectivesList:
				city = getCity(tCoords)
				if not self.isCityAxis(city) and not self.isCityAllies(city):
					szText = u"<font=2><color=%d,%d,%d,%d>%s</color></font>" %(gc.getPlayer(city.getOwner()).getPlayerTextColorR(), gc.getPlayer(city.getOwner()).getPlayerTextColorG(), gc.getPlayer(city.getOwner()).getPlayerTextColorB(), gc.getPlayer(city.getOwner()).getPlayerTextColorA(), city.getName() + '      ')
					screen.setText( "ObjectivesText" + str(iCount), "Background", szText, CvUtil.FONT_LEFT_JUSTIFY, xResolution - 155, 93 + iCount*13, -0.1, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
					iCount = iCount + 1

		screen.setPanelSize( "ObjectivesBackground", xResolution - 155, 100, 147, 14*iCount )
		screen.show( "ObjectivesBackground" )

	def victoryScreen(self, screen, szTable, nRivals, iPlayer):
		for i in range(14):
			screen.appendTableRow(szTable)
		
		screen.setTableText(szTable, 1, 0, u"<font=4b>" + localText.getText("TXT_KEY_TECH_AXIS", ()) + "</font>", "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
		screen.setTableText(szTable, 3, 0, u"<font=4b>" + localText.getText("TXT_KEY_TECH_ALLIES", ()) + "</font>", "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)

		szVictoryType = u"<font=4b>" + gc.getVictoryInfo(1).getDescription().upper() + u"</font>"
		screen.setTableText(szTable, 0, 1, szVictoryType, "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
		szText1 = localText.getText("TXT_KEY_VICTORY_SCREEN_HIGHEST_SCORE", (CyGameTextMgr().getTimeStr(gc.getGame().getMaxTurns(), false), ))
		szText1 += "  (" + localText.getText("TXT_KEY_MISC_TURNS_LEFT", (gc.getGame().getMaxTurns() - gc.getGame().getElapsedGameTurns(), )) + ")"
		screen.setTableText(szTable, 0, 2, szText1, "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
		screen.setTableText(szTable, 1, 2, u"%d" %gc.getTeam(iAxis).getAssets(), "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
		screen.setTableText(szTable, 3, 2, u"%d" %gc.getTeam(iAllies).getAssets(), "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)

		szVictoryType = u"<font=4b>" + gc.getVictoryInfo(2).getDescription().upper() + u"</font>"
		screen.setTableText(szTable, 0, 4, szVictoryType, "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)

		screen.setTableText(szTable, 0, 5, localText.getText("TXT_KEY_VICTORY_SCREEN_ELIMINATE_ALL", ()), "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
		screen.setTableText(szTable, 1, 5, localText.getText("TXT_KEY_VICTORY_SCREEN_RIVALS_LEFT", ()) + ' ' + unicode(nRivals), "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
		screen.setTableText(szTable, 3, 5, localText.getText("TXT_KEY_VICTORY_SCREEN_RIVALS_LEFT", ()) + ' ' + unicode(nRivals), "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)

		screen.setTableText(szTable, 0, 7, u"<font=4b>" + localText.getText("TXT_KEY_MISC_OBJECTIVE_CITIES", ()).upper() + "</font>", "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
		screen.setTableText(szTable, 0, 8, localText.getText("TXT_KEY_SCREEN_OBJECTIVE", (10, )), "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
		iRowAxis = 7
		iRowAllies = 7
		for tCoords in tObjectivesList:
			city = getCity(tCoords)
			if self.isCityAxis(city):
				iColumn = 1
				iRowAxis += 1
				screen.setTableText(szTable, iColumn, iRowAxis, city.getName(), "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
			if self.isCityAllies(city):
				iColumn = 3
				iRowAllies += 1
				screen.setTableText(szTable, iColumn, iRowAllies, city.getName(), "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
