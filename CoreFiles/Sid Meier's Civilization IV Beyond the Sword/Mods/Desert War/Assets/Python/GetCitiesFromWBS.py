# Get Cities From WBS
# by Wouter "Locutus" Snijders - 2005-08-05
# Extracts city names from a WBS file for use in other Python scenario scripts

# Instructions
# You can use this script to automatically generate Python code that initialises
# city variables of all cities in a WBS (WorldBuilderSave) file. This is useful
# when creating code for scenarios that deals with a lot of pre-placed cities.
#
# Warning: while this script should be perfectly safe, one can never be careful 
# enough. So back up your files (esp. your WBS file) before you use this script.
# Especially if you start messing with the code below...
#
# This script will run when and only when (1) the variable self.runScript (see
# below) is set to True, (2) this file is part of an active mod (by default it's
# part of the Desert War scenario, but you can place it in any other mod folder
# too) and (3) it's imported from any other Python file in that mod. To import
# it into an existing script file, place the following line (without the
# preceeding #) below the line 'from CvPythonExtensions import *' in that file:
#
# import GetCitiesFromWBS
#
# You can set the WBS file that the script uses to extract cities from in the
# variable self.filePath below. By default, the code that is generated is placed
# in GetCitiesFromWBS.txt in your main Civ4 folder. To use, put the code from
# that file near the top of CvMod.py (or in whatever file you're putting your
# own code): after the imports but before any class definition. Also add the
# following function below it (without the preceeding #s):
#
# def getCity(tCoords):
#	'Returns a city at coordinates tCoords.'
#	return CyGlobalContext().getMap().plot(tCoords[0], tCoords[1]).getPlotCity()
#
# When you do this, you can within CvMod.py refer to a pre-placed city as
# getCity(t<city name>) and outside CvMod.py as CvMod.getCity(t<city name>),
# where you should remove any spaces and the special characters ', `, " and -
# from the name. So New York becomes tNewYork and 's-Hertogenbosch becomes
# tsHertogenbosch. See CvDesertWar.py as an example of the result of this script
# in action.

class GetCitiesFromWBS:
	def __init__(self):

		# set this to True to run the script, to False to ignore it
		self.runScript = False
		
		# path of the WBS file, from the main Civ4 folder
		self.filePath = 'PublicMaps/DesertWar.Civ4WorldBuilderSave'

		# set this to the name of the output file
		self.outputFile = 'GetCitiesFromWBS.txt'

		# set this to the format of the output
		self.formatStr = 't%s = (%s, %s)\n'

		# set this to the list of characters that should be removed from the city name
		self.unwantedCharList = ["'", '"', '-', '`', ' ']

	def run(self):
		if self.runScript:
			wbsFile = open(self.filePath, 'r')
			citiesFile = open(self.outputFile, 'w')

			# read every line from the WBS
			strLine = wbsFile.readline()
			while strLine:
				# store the last known set of coordinates
				iBeginX = strLine.find('x=')
				if iBeginX != -1:
					iEndX = strLine.find(',', iBeginX)
					if iEndX != -1:
						iBeginY = strLine.find('y=', iEndX)
						if iBeginY != -1:
							strX = strLine[iBeginX+2:iEndX]
							strY = strLine[iBeginY+2:-1]

				# look for a city name
				iBeginCity = strLine.find('CityName=')
				if iBeginCity != -1:
					strCityName = strLine[iBeginCity+9:-1]

					# remove unwanted characters
					strCityName = self.remove(strCityName, self.unwantedCharList)

					# write the city name and the last known set of coordinates to file
					citiesFile.write(self.formatStr %(strCityName, strX, strY))

				# continue with next line
				strLine = wbsFile.readline()

			wbsFile.close()
			citiesFile.close()
	
	def remove(self, strCityName, cUnwantedList):
		'Remove unwanted character char from cityStr.'
		for cUnwanted in cUnwantedList:
			if cUnwanted == ' ':
				lParts = strCityName.split()
			else:
				lParts = strCityName.split(cUnwanted)
			strCityName = ''
			for strPart in lParts:
				strCityName += strPart
			return strCityName

def runGetCitiesFromWBS():
	app = GetCitiesFromWBS()
	app.run()

runGetCitiesFromWBS()