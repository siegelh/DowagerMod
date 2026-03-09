## Sid Meier's Civilization 4
## Copyright Firaxis Games 2005
from CvPythonExtensions import *
import PyHelpers
import ScreenInput
import CvScreenEnums
import CvUtil
import CvGameUtils
import CvScreensInterface

# globals
gc = CyGlobalContext()
ArtFileMgr = CyArtFileMgr()
localText = CyTranslator()

class CvDanQuayle:

	def __init__(self):
		self.SCREEN_NAME = "CvDanQuayle"
		self.WIDGET_ID = "CvDanQuayleWidget"
		self.EXIT_ID = "CvDanQuayleExitWidget"
		self.BACKGROUND_ID = "CvDanQuayleBackground"
		self.LEADERHEAD_ID = "CvDanQuayleLeaderhead"
		self.LIST_ID = "CvDanQuayleList"
		self.TEXT_ID = "CvDanQuayleText"
		self.SCORE_ID = "CvDanQuayleScore"
		self.SCORE_ID = "CvDanQuayleScore"
		self.WIDGET_HEADER = "CvDanQuayleHeader"

		self.X_SCREEN = 0
		self.Y_SCREEN = 0
		self.W_SCREEN = 1024
		self.H_SCREEN = 768
		self.Y_TITLE = 12
		self.X_EXIT = 994
		self.Y_EXIT = 726
		
	def getScreen(self):
		return CyGInterfaceScreen(self.SCREEN_NAME, CvScreenEnums.DAN_QUAYLE_SCREEN)

	def interfaceScreen (self):
		screen = self.getScreen()
		
		self.iCounter = 3
	
		screen.addPanel("DemoBuyPanel", "", "", true, true,
			self.X_SCREEN, self.Y_SCREEN, self.W_SCREEN, self.H_SCREEN, PanelStyles.PANEL_STYLE_MAIN)

		screen.showWindowBackground(True)
		screen.setRenderInterfaceOnly(True)
		screen.setCloseOnEscape(False)

		screen.showScreen( PopupStates.POPUPSTATE_IMMEDIATE, False)

		screen.setImageButton( "DemoBuy", "Art/Comic/Afterworld_YouLose.dds", self.X_SCREEN, self.Y_SCREEN, 1024, 768, WidgetTypes.WIDGET_GENERAL, -1, -1 )
		screen.addPanel( "LoseTextPanel", u"", u"", 0, 0, 690,50,240,150, PanelStyles.PANEL_STYLE_MAIN )
		screen.addMultilineText( "LoseText", CyTranslator().getText("TXT_KEY_FAILURE",()), 695,55,230,140, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY )
		screen.setDimensions(screen.centerX(0), screen.centerY(0), self.W_SCREEN, self.H_SCREEN)						

		
	# Will handle the input for this screen...
	def handleInput (self, inputClass):
		if self.iCounter > 0:
			return
		
		if (inputClass.getNotifyCode() == NotifyCode.NOTIFY_CLICKED or inputClass.getData() == int(InputTypes.KB_RETURN) or inputClass.getData() == int(InputTypes.KB_ESCAPE) ):
			CyInterface().exitingToMainMenu("nothing", True)
			self.getScreen().hideScreen()
			return 1
		
	def update(self, fDelta):
		self.iCounter -= fDelta
		
		return
