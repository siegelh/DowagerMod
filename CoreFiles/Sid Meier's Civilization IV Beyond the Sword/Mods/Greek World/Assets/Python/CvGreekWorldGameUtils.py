## Sid Meier's Civilization 4
## Copyright Firaxis Games 2005
##
## Implementaion of miscellaneous game functions
##
## Override for Greek World sceanrio

import CvUtil
from CvPythonExtensions import *
import CvGameUtils

# globals
gc = CyGlobalContext()

class CvGreekWorldGameUtils(CvGameUtils.CvGameUtils):
	"Miscellaneous game functions"
	def __init__(self):
		self.parent = CvGameUtils.CvGameUtils
		self.parent.__init__(self)
	
	def doHolyCity(self):
		return True