## Sid Meier's Civilization 4
## Copyright Firaxis Games 2005
from CvPythonExtensions import *
import PyHelpers
import CvUtil
import ScreenInput
import CvScreenEnums
import string

PyPlayer = PyHelpers.PyPlayer
PyInfo = PyHelpers.PyInfo

# globals
gc = CyGlobalContext()
ArtFileMgr = CyArtFileMgr()
localText = CyTranslator()

class CvCharlemagneScreen:
	"Wonder Movie Screen"
	def interfaceScreen (self, argsList):
		
		szScreenID = argsList[0]
		
		self.X_SCREEN = 100
		self.Y_SCREEN = 40
		self.W_SCREEN = 775
		self.H_SCREEN = 660
		self.Y_TITLE = self.Y_SCREEN + 20
		
		self.X_EXIT = self.X_SCREEN + self.W_SCREEN/2 - 50
		self.Y_EXIT = self.Y_SCREEN + self.H_SCREEN - 50
		self.W_EXIT = 120
		self.H_EXIT = 30
		
		if (CyInterface().noTechSplash()):
			return 0
				
		player = PyPlayer(CyGame().getActivePlayer())
			
		screen = CyGInterfaceScreen( "CharlemagneScreen", CvScreenEnums.CHARLEMAGNE_SCREEN)
		screen.addPanel("CharlemagnePanel", "", "", true, true,
			self.X_SCREEN, self.Y_SCREEN, self.W_SCREEN, self.H_SCREEN, PanelStyles.PANEL_STYLE_MAIN)
		
		screen.showWindowBackground(True)
		screen.setRenderInterfaceOnly(False);
		screen.setSound("AS2D_NEW_ERA")
		screen.showScreen(PopupStates.POPUPSTATE_MINIMIZED, False)
		
		# Win or Lose?
		
		szMovie = ""
		szHeader = ""
		
		if (szScreenID == "Win Screen"):
			szMovie = "Art/Interface/Screens/Charlemagne/Charlemagne_Pope_Coronation_LG.dds"
			szHeader = localText.getText("TXT_KEY_CHARLEMAGNE_SCREEN_WIN", ())
		elif (szScreenID == "Lose Screen"):
			szMovie = "Art/Interface/Screens/Charlemagne/Charlemagne_Pope_Excommunicated_LG.dds"
			szHeader = localText.getText("TXT_KEY_CHARLEMAGNE_SCREEN_LOSE", ())
		
		# Header...
		szHeaderId = "EraTitleHeader"
		screen.setText(szHeaderId, "Background", szHeader, CvUtil.FONT_CENTER_JUSTIFY,
			       self.X_SCREEN + self.W_SCREEN / 2, self.Y_TITLE, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		
		screen.setButtonGFC("CharlemagneExit", localText.getText("TXT_KEY_MAIN_MENU_OK", ()), "", self.X_EXIT, self.Y_EXIT, self.W_EXIT, self.H_EXIT, WidgetTypes.WIDGET_CLOSE_SCREEN, -1, -1, ButtonStyles.BUTTON_STYLE_STANDARD )
		
		# Show the screen

		screen.addDDSGFC("CharlemagneMovie", szMovie, self.X_SCREEN + 27, self.Y_SCREEN + 50, 720, 540, WidgetTypes.WIDGET_GENERAL, -1, -1 )
				
		return 0
		
	# Will handle the input for this screen...
	def handleInput (self, inputClass):
		return 0

	def update(self, fDelta):
		return

