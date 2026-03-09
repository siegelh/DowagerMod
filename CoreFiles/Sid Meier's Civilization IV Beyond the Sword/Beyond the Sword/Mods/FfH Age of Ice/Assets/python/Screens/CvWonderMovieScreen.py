## Sid Meier's Civilization 4
## Copyright Firaxis Games 2005
from CvPythonExtensions import *
import PyHelpers
import CvUtil
import ScreenInput
import CvScreenEnums

PyPlayer = PyHelpers.PyPlayer
PyInfo = PyHelpers.PyInfo

# globals
gc = CyGlobalContext()
ArtFileMgr = CyArtFileMgr()
localText = CyTranslator()

MOVIE_SCREEN_WONDER = 0
MOVIE_SCREEN_RELIGION = 1
MOVIE_SCREEN_PROJECT = 2
MOVIE_SCREEN_SLIDESHOW = 3

class CvWonderMovieScreen:
	"Wonder Movie Screen"

	def __init__(self):
		self.fDelay = -1.0
		self.fTime = 0.0
		self.bDone = false

	def interfaceScreen (self, iMovieItem, iCityId, iMovieType):
		# iMovieItem is either the WonderID, the ReligionID, or the ProjectID, depending on iMovieType
		
		if CyUserProfile().getGraphicOption(GraphicOptionTypes.GRAPHICOPTION_NO_MOVIES):
			return
		
		self.Z_CONTROLS = -2.2

		self.X_SCREEN = 0
		self.Y_SCREEN = 0
		self.W_SCREEN = 1024
		self.H_SCREEN = 768

		self.Y_WINDOW = 40
		self.W_WINDOW = 760
		self.H_WINDOW = 590
		self.Y_TITLE = self.Y_WINDOW + 20
		self.iWonderId = iMovieItem
		self.X_WINDOW = (self.W_SCREEN/2) - (self.W_WINDOW/2)# Was 250
		
		self.X_EXIT = self.X_WINDOW + self.W_WINDOW/2 - 50
		self.Y_EXIT = self.Y_WINDOW + self.H_WINDOW - 50
		self.W_EXIT = 120
		self.H_EXIT = 30
		
		self.X_MOVIE = 20
		self.Y_MOVIE = 50
		self.W_MOVIE = 720
		self.H_MOVIE = 480
		
		self.iMovieType = iMovieType
		self.fTime = 0.0
		self.fDelay = 1.5
		self.bDone = false

		if self.iMovieType == MOVIE_SCREEN_SLIDESHOW:
			self.Y_WINDOW = 20
			self.H_WINDOW = 700
			self.X_TEXT_PANEL = self.X_WINDOW + 20
			self.Y_TEXT_PANEL = 550
			self.W_TEXT_PANEL = 720
			self.H_TEXT_PANEL = 130
			self.iMarginSpace = 20
			self.iMovieItem = iMovieItem
			self.iMaxSlides = iCityId
			self.iCount = 1
			self.szAudio = -1

			self.Y_TITLE = self.Y_WINDOW + 20
			self.Y_EXIT = self.Y_WINDOW + self.H_WINDOW - 50
			self.X_SKIP_ALL = self.X_WINDOW + self.W_WINDOW - (self.W_EXIT + self.iMarginSpace)

		# not all projects have movies
		self.szMovieFile = None
		if self.iMovieType == MOVIE_SCREEN_PROJECT:
			szArtDef = gc.getProjectInfo(iMovieItem).getMovieArtDef()
			if (len(szArtDef) > 0):
				self.szMovieFile = CyArtFileMgr().getMovieArtInfo(szArtDef).getPath()
		elif self.iMovieType == MOVIE_SCREEN_WONDER:
			self.szMovieFile = gc.getBuildingInfo(iMovieItem).getMovie()
		elif self.iMovieType == MOVIE_SCREEN_RELIGION:
			self.szMovieFile = gc.getReligionInfo(iMovieItem).getMovieFile()
		elif self.iMovieType == MOVIE_SCREEN_SLIDESHOW:
			if iMovieItem == 1:
				self.szMoviePrefix = 'Art/Movies/Opening'
				self.szAudio = 'AS2D_FfH_SLIDESHOW'
				self.szMovieFile = self.szMoviePrefix + str(self.iCount) + '.bik'
				self.szTextPrefix = "TXT_KEY_POPUP_OPENING_SLIDESHOW_"
				bodyString = localText.getText(self.szTextPrefix + str(self.iCount), ())
			if iMovieItem == 2:
				self.szMoviePrefix = 'Art/Movies/Defeat'
				self.szAudio = 'AS2D_DEFEAT'
				self.szMovieFile = self.szMoviePrefix + str(self.iCount) + '.bik'
				bodyString = localText.getText("TXT_KEY_POPUP_DEFEAT", ())
			if iMovieItem == 3:
				self.szMoviePrefix = 'Art/Movies/Victory'
				self.szAudio = 'AS2D_VICTORY'
				self.szMovieFile = self.szMoviePrefix + str(self.iCount) + '.bik'
				bodyString = localText.getText("TXT_KEY_POPUP_VICTORY", ())
		if (self.szMovieFile == None or len(self.szMovieFile) == 0):
			return
		
		player = PyPlayer(CyGame().getActivePlayer())
		
		# move the camera and mark the interface camera as dirty so that it gets reset - JW
		if self.iMovieType == MOVIE_SCREEN_WONDER:
			CyInterface().lookAtCityBuilding(iCityId, iMovieItem)
#		else:
		elif self.iMovieType != MOVIE_SCREEN_SLIDESHOW:
			CyInterface().lookAtCityBuilding(iCityId, -1)
		CyInterface().setDirty(InterfaceDirtyBits.SelectionCamera_DIRTY_BIT, True)
		
		screen = CyGInterfaceScreen( "WonderMovieScreen" + str(iMovieItem), CvScreenEnums.WONDER_MOVIE_SCREEN )
		screen.addPanel("WonderMoviePanel", "", "", true, true,
			self.X_WINDOW, self.Y_WINDOW, self.W_WINDOW, self.H_WINDOW, PanelStyles.PANEL_STYLE_MAIN)
		
		screen.showWindowBackground( True )
		screen.setDimensions(screen.centerX(self.X_SCREEN), screen.centerY(self.Y_SCREEN), self.W_SCREEN, self.H_SCREEN)
		screen.setRenderInterfaceOnly(False)
		screen.showScreen(PopupStates.POPUPSTATE_IMMEDIATE, False)
		screen.enableWorldSounds( false )
		                		
		# Header...
		szHeaderId = "WonderTitleHeader" + str(iMovieItem)
		if self.iMovieType == MOVIE_SCREEN_RELIGION:
			szHeader = localText.getText("TXT_KEY_MISC_REL_FOUNDED_MOVIE", (gc.getReligionInfo(iMovieItem).getTextKey(), ))
		elif self.iMovieType == MOVIE_SCREEN_WONDER:
			szHeader = gc.getBuildingInfo(iMovieItem).getDescription()
		elif self.iMovieType == MOVIE_SCREEN_PROJECT:
			szHeader = gc.getProjectInfo(iMovieItem).getDescription()
		elif self.iMovieType == MOVIE_SCREEN_SLIDESHOW:
			szHeader = localText.getText("TXT_KEY_POPUP_AGE_OF_ICE",())

		screen.setText(szHeaderId, "Background", szHeader, CvUtil.FONT_CENTER_JUSTIFY,
				self.X_WINDOW + self.W_WINDOW / 2, self.Y_TITLE, self.Z_CONTROLS, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

		if self.iMovieType == MOVIE_SCREEN_SLIDESHOW:	
			szTextPanel = "DawnOfManTextPanel"
			screen.addPanel( szTextPanel, "", "", true, true,
				self.X_TEXT_PANEL, self.Y_TEXT_PANEL, self.W_TEXT_PANEL, self.H_TEXT_PANEL, PanelStyles.PANEL_STYLE_DAWNBOTTOM )
			screen.addMultilineText( "BodyText", bodyString, self.X_TEXT_PANEL + self.iMarginSpace, 
				self.Y_TEXT_PANEL + self.iMarginSpace, self.W_TEXT_PANEL - (self.iMarginSpace * 2),
				self.H_TEXT_PANEL - (self.iMarginSpace * 2), WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)

		screen.hide("Background")
		screen.playMovie("", 0, 0, 0, 0, 0) # dummy call to hide screen if no movies are supposed to be shown

	def playMovie(self):
			
		screen = CyGInterfaceScreen( "WonderMovieScreen" + str(self.iWonderId), CvScreenEnums.WONDER_MOVIE_SCREEN )
		screen.setRenderInterfaceOnly(True)
		screen.show("Background")

		# Play the movie
		if self.iMovieType == MOVIE_SCREEN_RELIGION:
			screen.addReligionMovieWidgetGFC( "ReligionMovie", self.szMovieFile, self.X_WINDOW + self.X_MOVIE, self.Y_WINDOW + self.Y_MOVIE, self.W_MOVIE, self.H_MOVIE, WidgetTypes.WIDGET_GENERAL, -1, -1)
			CyInterface().playGeneralSound(gc.getReligionInfo(self.iWonderId).getMovieSound())
		else:
			screen.playMovie(self.szMovieFile, self.X_WINDOW + self.X_MOVIE, self.Y_WINDOW + self.Y_MOVIE, self.W_MOVIE, self.H_MOVIE, -2.3 )

		if self.iMovieType == MOVIE_SCREEN_SLIDESHOW:
			if self.szAudio != -1:
				screen.setSoundId(CyAudioGame().Play2DSound(self.szAudio))

		eWidget = WidgetTypes.WIDGET_CLOSE_SCREEN
		if (self.iMovieType == MOVIE_SCREEN_SLIDESHOW and self.iMaxSlides > 1):
			eWidget = WidgetTypes.WIDGET_PYTHON
			screen.setButtonGFC("WonderSkipAll" + str(self.iWonderId), localText.getText("TXT_KEY_POPUP_SKIP_ALL", ()), "", self.X_SKIP_ALL, self.Y_EXIT, self.W_EXIT, self.H_EXIT, WidgetTypes.WIDGET_CLOSE_SCREEN, -1, -1, ButtonStyles.BUTTON_STYLE_STANDARD )
		screen.setButtonGFC("WonderExit" + str(self.iWonderId), localText.getText("TXT_KEY_MAIN_MENU_OK", ()), "", self.X_EXIT, self.Y_EXIT, self.W_EXIT, self.H_EXIT, eWidget, -1, -1, ButtonStyles.BUTTON_STYLE_STANDARD )

	# Will handle the input for this screen...
	def handleInput (self, inputClass):
		if self.iMovieType == MOVIE_SCREEN_SLIDESHOW:
			if self.iCount < self.iMaxSlides:
				if (inputClass.getNotifyCode() == NotifyCode.NOTIFY_CLICKED):
					screen = CyGInterfaceScreen( "WonderMovieScreen" + str(self.iWonderId), CvScreenEnums.WONDER_MOVIE_SCREEN )
					self.iCount += 1
					self.szMovieFile = self.szMoviePrefix + str(self.iCount) + '.bik'
					bodyString = localText.getText(self.szTextPrefix + str(self.iCount), ())
					screen.playMovie(self.szMovieFile, self.X_WINDOW + self.X_MOVIE, self.Y_WINDOW + self.Y_MOVIE, self.W_MOVIE, self.H_MOVIE, -2.3 )
					screen.addMultilineText( "BodyText", bodyString, self.X_TEXT_PANEL + self.iMarginSpace, 
						self.Y_TEXT_PANEL + self.iMarginSpace, self.W_TEXT_PANEL - (self.iMarginSpace * 2),
						self.H_TEXT_PANEL - (self.iMarginSpace * 2), WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
					if (self.iMaxSlides > 1 and self.iMaxSlides == self.iCount):
						screen = CyGInterfaceScreen( "WonderMovieScreen" + str(self.iWonderId), CvScreenEnums.WONDER_MOVIE_SCREEN )
						screen.deleteWidget("WonderSkipAll" + str(self.iWonderId))
						screen.deleteWidget("WonderExit" + str(self.iWonderId))
						screen.setButtonGFC("WonderExit2" + str(self.iWonderId), localText.getText("TXT_KEY_MAIN_MENU_OK", ()), "", self.X_EXIT, self.Y_EXIT, self.W_EXIT, self.H_EXIT, WidgetTypes.WIDGET_CLOSE_SCREEN, -1, -1, ButtonStyles.BUTTON_STYLE_STANDARD )
		if (inputClass.getNotifyCode() == NotifyCode.NOTIFY_MOVIE_DONE):
			if (not self.bDone):
				screen = CyGInterfaceScreen( "WonderMovieScreen" + str(self.iWonderId), CvScreenEnums.WONDER_MOVIE_SCREEN )
				if self.iMovieType == MOVIE_SCREEN_WONDER:
					szHelp = CyGameTextMgr().getBuildingHelp(self.iWonderId, False, False, False, None)
				elif self.iMovieType == MOVIE_SCREEN_PROJECT:
					szHelp = CyGameTextMgr().getProjectHelp(self.iWonderId, False, None)
				else:
					szHelp = ""
				
				if len(szHelp) > 0:
					screen.addPanel("MonkeyPanel", "", "", true, true, self.X_WINDOW + self.X_MOVIE + self.W_MOVIE / 8 - 10, self.Y_WINDOW + self.Y_MOVIE + 90, 3 * self.W_MOVIE / 4 + 20, self.H_MOVIE - 180, PanelStyles.PANEL_STYLE_MAIN_BLACK50)
					screen.addMultilineText("MonkeyText", szHelp, self.X_WINDOW + self.X_MOVIE + self.W_MOVIE / 8, self.Y_WINDOW + self.Y_MOVIE + 100, 3 * self.W_MOVIE / 4, self.H_MOVIE - 200, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
				self.bDone = true

		return 0

	def update(self, fDelta):
	
		if self.fDelay > 0:
			self.fTime += fDelta
			if self.fTime > self.fDelay:
				self.playMovie()
				self.fDelay = -1
		return
