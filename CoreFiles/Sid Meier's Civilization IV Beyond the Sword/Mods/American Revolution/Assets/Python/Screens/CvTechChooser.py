## Sid Meier's Civilization 4
## Copyright Firaxis Games 2005
from CvPythonExtensions import *
import CvUtil
import ScreenInput
import CvScreenEnums

PIXEL_INCREMENT = 7
BOX_INCREMENT_WIDTH = 27 # Used to be 33 #Should be a multiple of 3...
BOX_INCREMENT_HEIGHT = 9 #Should be a multiple of 3...
BOX_INCREMENT_Y_SPACING = 6 #Should be a multiple of 3...
BOX_INCREMENT_X_SPACING = 9 #Should be a multiple of 3...

TEXTURE_SIZE = 24
X_START = 6
X_INCREMENT = 27
Y_ROW = 32

CIV_HAS_TECH = 0
CIV_IS_RESEARCHING = 1
CIV_NO_RESEARCH = 2
CIV_TECH_AVAILABLE = 3

# globals
gc = CyGlobalContext()
ArtFileMgr = CyArtFileMgr()
g_civSelected = 0
localText = CyTranslator()
g_iCurrentState = []

zLevel = -6.1

class CvTechChooser:
	"Tech Chooser Screen"

	def __init__(self):
		self.nWidgetCount = 0
		
	# Screen construction function
	def interfaceScreen(self):
                return
            
	def hideScreen(self):
                return
	    
