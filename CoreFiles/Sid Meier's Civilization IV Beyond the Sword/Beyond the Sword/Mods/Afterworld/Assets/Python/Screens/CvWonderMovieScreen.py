## Sid Meier's Civilization 4
## Copyright Firaxis Games 2005

## Afterworld Comic Strip - written by Jesse Smith

from CvPythonExtensions import *
import PyHelpers
import CvUtil
import ScreenInput
import CvScreenEnums
import AW
import Popup as PyPopup

PyPlayer = PyHelpers.PyPlayer
PyInfo = PyHelpers.PyInfo
Afterworld = AW.g_Afterworld	

# globals
gc = CyGlobalContext()
ArtFileMgr = CyArtFileMgr()
localText = CyTranslator()




class AWComicText:
	def __init__( self, iTextBoxX, iTextBoxY, iTextBoxW, iTextBoxH, szTextKey, iColor=0, iSize=3  ):
		self.__iTextBoxX = iTextBoxX
		self.__iTextBoxY = iTextBoxY
		self.__iTextBoxW = iTextBoxW
		self.__iTextBoxH = iTextBoxH
		self.__szTextKey = szTextKey
		self.__iColor = iColor
		self.__iSize = iSize
	
	def getX( self ):
		return self.__iTextBoxX
	
	def getY( self ):
		return self.__iTextBoxY
	
	def getW( self ):
		return self.__iTextBoxW
	
	def getH( self ):
		return self.__iTextBoxH
		
	def getText( self ):
		tColor = self.getColor()
		
		return u"<font=%d><color=%d,%d,%d,%d>%s</color></font>" %(self.__iSize, tColor[0], tColor[1], tColor[2], tColor[3], CyTranslator().getText(self.__szTextKey,()))
	
	def getColor( self ):
		Colors = {
					0:	(255,255,255,255),	# white / 
					1:	(255,0,0,255),		# red / Ragah
					2:	(95,169,46,255),	# green / Atticus
					3:	(2,103,255,255),	# blue / Sever
					4:  (208,155,26,255),	# yellow / Jal
				}
		
		return Colors.get(self.__iColor)
			
class CvWonderMovieScreen:
	"Wonder Movie Screen"
	def __init__(self):
		self.IntroComicStrip = { 	
				# items in the tuple, comic page, duration, text information
				0:	("Art/Comic/Page01_01.dds", 2, AWComicText( 640,665,250,25,"TXT_KEY_PAGEONE1", 4 ) ),
				1:	("Art/Comic/Page01_01.dds", 2, AWComicText( 640,665,250,25,"TXT_KEY_PAGEONE2", 4 ) ),
				2:	("Art/Comic/Page01_02.dds", 4, AWComicText( 640,665,250,55,"TXT_KEY_PAGEONE3", 4 ) ),
				3:	("Art/Comic/Page01_02.dds", 6, AWComicText( 640,665,250,100,"TXT_KEY_PAGEONE4", 4 ) ),
				4:	("Art/Comic/Page01_02.dds", 2, AWComicText( 640,665,250,55,"TXT_KEY_PAGEONE5", 4 ) ),
				5:	("Art/Comic/Page01_02.dds", 2, AWComicText( 640,665,250,25,"TXT_KEY_PAGEONE6", 4 ) ),
				6:	("Art/Comic/Page01_03.dds", 5, AWComicText( 640,665,250,65,"TXT_KEY_PAGEONE7", 4 ) ),
				7:	("Art/Comic/Page01_03.dds", 2, AWComicText( 640,665,250,65,"TXT_KEY_PAGEONE8", 4 ) ),
				8:	("Art/Comic/Page01_03.dds", 5, AWComicText( 640,665,250,80,"TXT_KEY_PAGEONE9", 4 ) ),
				9:	("Art/Comic/Page01_04.dds", 5, AWComicText( 640,665,350,110,"TXT_KEY_PAGEONE10", 4 ) ),
				10:	("Art/Comic/Page01_04.dds", 4, AWComicText( 640,665,250,70,"TXT_KEY_PAGEONE11", 4 ) ),
				11:	("Art/Comic/Page01_05.dds", 4, AWComicText( 640,665,250,100,"TXT_KEY_PAGEONE12", 4 ) ),
				12:	("Art/Comic/Page01_06.dds", 5, AWComicText( 640,665,350,110,"TXT_KEY_PAGEONE13", 4 ) ),
				13:	("Art/Comic/Page01_06.dds", 5,AWComicText( 640,665,250,70,"TXT_KEY_PAGEONE14", 4 ) ),
				14:	("Art/Comic/Page01_07.dds", 5, AWComicText( 640,665,350,110,"TXT_KEY_PAGEONE15", 4 ) ),
				15:	("Art/Comic/Page01_07.dds", 3, AWComicText( 640,665,250,25,"TXT_KEY_PAGEONE16", 4 ) ),
				
				16:	("Art/Comic/Page02_01.dds", 4, AWComicText( 321,84,280,55,"TXT_KEY_PAGETWO1", 2 ) ),
				17:	("Art/Comic/Page02_01.dds", 4, AWComicText( 117,256,250,55,"TXT_KEY_PAGETWO2", 0 ) ),
				18:	("Art/Comic/Page02_01.dds", 4, AWComicText( 206,224,250,25,"TXT_KEY_PAGETWO3", 3 ) ),
				19:	("Art/Comic/Page02_02.dds", 6, AWComicText( 665,94,250,55,"TXT_KEY_PAGETWO4", 1 ) ),
				20:	("Art/Comic/Page02_03.dds", 6, AWComicText( 503,557,280,100,"TXT_KEY_PAGETWO5", 3 ) ),
				21:	("Art/Comic/Page02_03.dds", 4, AWComicText( 665,94,250,25,"TXT_KEY_PAGETWO6", 1 ) ),
				22:	("Art/Comic/Page02_03.dds", 10, AWComicText( 503,557,280,100,"TXT_KEY_PAGETWO7", 3 ) ),
				23:	("Art/Comic/Page02_04.dds", 6, AWComicText( 665,94,250,55,"TXT_KEY_PAGETWO8", 1 )),#Even more reason why Jal is in command and you're...
				24:	("Art/Comic/Page02_05.dds", 10, AWComicText( 822,313,200,100,"TXT_KEY_PAGETWO9", 4 ) ), #Jal
				25:	("Art/Comic/Page02_05.dds", 10, AWComicText( 665,94,250,55,"TXT_KEY_PAGETWO10", 1 ) ), #Ragah
				26:	("Art/Comic/Page02_05.dds", 4, AWComicText( 822,313,70,25,"TXT_KEY_PAGETWO11", 4 ) ), #Jal
				27:	("Art/Comic/Page02_05.dds", 4, AWComicText( 665,94, 120,25,"TXT_KEY_PAGETWO12", 1 ) ), #Ragah
				28:	("Art/Comic/Page02_05.dds", 12, AWComicText( 822,313,190,200,"TXT_KEY_PAGETWO13", 4 ) ), #Jal
				29:	("Art/Comic/Page02_06.dds", 12, AWComicText( 269,460,200,130,"TXT_KEY_PAGETWO14", 2 ) ), #Atticus
				30:	("Art/Comic/Page02_06.dds", 14, AWComicText( 269,460,200,200,"TXT_KEY_PAGETWO15", 2 ) ), #Atticus
				31:	("Art/Comic/Page02_06.dds", 14, AWComicText( 269,460,300,180,"TXT_KEY_PAGETWO16", 2 ) ),
				32:	("Art/Comic/Page02_06.dds", 14, AWComicText( 269,460,200,130,"TXT_KEY_PAGETWO17", 2 ) ),
				33:	("Art/Comic/Page02_06.dds", 4, AWComicText( 62,547,200,25,"TXT_KEY_PAGETWO18", 0 ) ), #Riest
				34:	("Art/Comic/Page02_06.dds", 10, AWComicText( 269,460,200,130,"TXT_KEY_PAGETWO19", 2 ) ),
				35:	("Art/Comic/Page02_06.dds", 14, AWComicText( 227,537,190,200,"TXT_KEY_PAGETWO20", 4 ) ),#Jal
				36:	("Art/Comic/Page02_06.dds", 6, AWComicText( 99,475,270,25,"TXT_KEY_PAGETWO21", 3 ) ), #Sever
				37:	("Art/Comic/Page02_06.dds", 10, AWComicText( 227,537,190,140,"TXT_KEY_PAGETWO22", 4 ) ),
				38:	("Art/Comic/Page02_06.dds", 12, AWComicText( 227,537,250,140,"TXT_KEY_PAGETWO23", 4 ) ),
				39:	("Art/Comic/Page02_06.dds", 16, AWComicText( 269,460,200,190,"TXT_KEY_PAGETWO24", 2 ) ),
				40:	("Art/Comic/Page02_07.dds", 10, AWComicText( 805,655,200,50,"TXT_KEY_PAGETWO25", 1 ) ),
						
			}

		self.VictoryComicStrip = {
				0:	("Art/Comic/Page03_01.dds", 5, AWComicText( 2,57,250,120,"TXT_KEY_LASTPAGE01", 4 ) ),
				1:	("Art/Comic/Page03_02.dds", 3, AWComicText( 2,57,250,65,"TXT_KEY_LASTPAGE02", 4 ) ),
				2:	("Art/Comic/Page03_03.dds", 7, AWComicText( 2,57,250,120,"TXT_KEY_LASTPAGE03", 4 ) ),
				3:	("Art/Comic/Page03_03.dds", 7, AWComicText( 2,57,250,120,"TXT_KEY_LASTPAGE04", 4 ) ),				
				4:	("Art/Comic/Page03_04.dds", 7, AWComicText( 2,57,250,120,"TXT_KEY_LASTPAGE05", 4 ) ),
				5:	("Art/Comic/Page03_04.dds", 8, AWComicText( 2,57,250,120,"TXT_KEY_LASTPAGE06", 4 ) ),
				6:	("Art/Comic/Page03_05.dds", 6, AWComicText( 2,57,250,65,"TXT_KEY_LASTPAGE07", 4 ) ),
				7:	("Art/Comic/Page03_05.dds", 7, AWComicText( 2,57,250,120,"TXT_KEY_LASTPAGE08", 4 ) ),
				8:	("Art/Comic/Page03_05.dds", 8, AWComicText( 2,57,250,120,"TXT_KEY_LASTPAGE09", 4 ) ),
				9:	("Art/Comic/Page03_05.dds", 2, AWComicText( 2,57,250,25,"TXT_KEY_LASTPAGE10", 4 ) ),
				10:	("Art/Comic/Page03_06.dds", 8, AWComicText( 2,57,250,120,"TXT_KEY_LASTPAGE11", 4 ) ),
				11:	("Art/Comic/Page03_06.dds", 6, AWComicText( 2,57,250,75,"TXT_KEY_LASTPAGE12", 4 ) ),
				12:	("Art/Comic/Page03_07.dds", 7, AWComicText( 2,57,250,65,"TXT_KEY_LASTPAGE13", 4 ) ),
				13:	("Art/Comic/Page03_08.dds", 6, AWComicText( 602,703,300,65,"TXT_KEY_LASTPAGE14", 4 ) ),
				14:	("Art/Comic/Page04_01.dds", 4, AWComicText( 602,708,200,50,"TXT_KEY_PAGEFIVE15", 4) ),
			}	

		
		self.szVictoryMusic = "AS2D_DEFEAT"
		
		self.szIntroMusic = "AS2D_OPENING_SLIDESHOW"

	
	def interfaceScreen (self, ComicStripType=0):
		# iMovieItem is either the WonderID, the ReligionID, or the ProjectID, depending on iMovieType
		
		self.iCurrentComic = -1
		self.iCounter = 0
		
		self.iComicStripType = ComicStripType
		
		self.Z_CONTROLS = -2.2

		self.X_SCREEN = 0
		self.Y_SCREEN = 0
		self.W_SCREEN = 1024
		self.H_SCREEN = 768

		self.X_WINDOW = 0
		self.Y_WINDOW = 0
		self.W_WINDOW = 1024
		self.H_WINDOW = 768
		self.Y_TITLE = self.Y_WINDOW + 20
		
		self.X_EXIT = self.X_WINDOW + self.W_WINDOW/2 - 50
		self.Y_EXIT = self.Y_WINDOW + self.H_WINDOW - 50
		self.W_EXIT = 120
		self.H_EXIT = 30
		
		self.X_MOVIE = 20
		self.Y_MOVIE = 50
		self.W_MOVIE = 720
		self.H_MOVIE = 480
		
		player = PyPlayer(CyGame().getActivePlayer())
		
		screen = CyGInterfaceScreen( "WonderMovieScreen", CvScreenEnums.WONDER_MOVIE_SCREEN )
		screen.addPanel("WonderMoviePanel", "", "", true, true,
			self.X_WINDOW, self.Y_WINDOW, self.W_WINDOW, self.H_WINDOW, PanelStyles.PANEL_STYLE_MAIN)
		
		screen.showWindowBackground( True )
		screen.setDimensions(screen.centerX(self.X_SCREEN), screen.centerY(self.Y_SCREEN), self.W_SCREEN, self.H_SCREEN)
		screen.setRenderInterfaceOnly(False)
		screen.setCloseOnEscape(False)
		screen.showScreen(PopupStates.POPUPSTATE_IMMEDIATE, False)
		screen.enableWorldSounds( False )
		
		iNumComics = 0
		ComicStrip = self.getComicStrip()
		iNumComics = len(ComicStrip)
		
		szID = ""
		if self.iComicStripType == 0:
			szID = self.szIntroMusic
		elif self.iComicStripType == 1:
			szID = self.szVictoryMusic
		
		if szID:
			screen.setSoundId(CyAudioGame().Play2DSound(szID))
		
		for i in range(iNumComics):
			szComicName = "ComicStrip" + str(i)
			screen.setImageButton( szComicName, self.getComic(i)[0], self.X_WINDOW, self.Y_WINDOW, 1024, 768, WidgetTypes.WIDGET_GENERAL, -1, -1 )
			
			# if there is text info
			if len(self.getComic(i)) > 2:
				AWComicText = self.getComic(i)[2]
				if AWComicText:
					szComicText = "ComicStripText" + str(i)
					szComicTextPanel = "ComicStripTextPanel" + str(i)
					screen.addPanel( szComicTextPanel, u"", u"", 0, 0, AWComicText.getX()-5, AWComicText.getY()-5, AWComicText.getW()+5, AWComicText.getH()+5, PanelStyles.PANEL_STYLE_MAIN )
					screen.addMultilineText( szComicText, AWComicText.getText(), AWComicText.getX(), AWComicText.getY(), AWComicText.getW(), AWComicText.getH(), WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY )
					#screen.attachMultilineText( szComicTextPanel, szComicText, CyTranslator().getText(AWComicText.getText(),()), WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY )
					screen.hide(szComicText)
					screen.hide(szComicTextPanel)
			
			screen.hide(szComicName)
		
		self.showComic(0)

	def getComicStrip(self):
		if self.iComicStripType == 0:
			ComicStrip = self.IntroComicStrip
		
		elif self.iComicStripType == 1:
			ComicStrip = self.VictoryComicStrip
		
		return ComicStrip		
	
	def getComic(self, iCurrentComic):
		return self.getComicStrip().get(iCurrentComic)

	def showComic(self, iComic):
		screen = CyGInterfaceScreen( "WonderMovieScreen", CvScreenEnums.WONDER_MOVIE_SCREEN )
		AWComic = self.getComic(iComic)
		if AWComic and len(AWComic) > 2:
			screen.show("ComicStripTextPanel" + str(iComic))
			screen.show("ComicStripText" + str(iComic))
			screen.show("ComicStrip" + str(iComic))
			self.iCounter = AWComic[1]
		
	def hideComic(self, iComic):
		screen = CyGInterfaceScreen( "WonderMovieScreen", CvScreenEnums.WONDER_MOVIE_SCREEN )
		AWComic = self.getComic(iComic)
		if AWComic and len(AWComic) > 2:
			screen.hide("ComicStripTextPanel" + str(iComic))
			screen.hide("ComicStripText" + str(iComic))
		screen.hide("ComicStrip" + str(iComic))
				
	def processComicStrip(self, direction):
		screen = CyGInterfaceScreen( "WonderMovieScreen", CvScreenEnums.WONDER_MOVIE_SCREEN )
		if direction == "forward":
			# if the end of the strip, close the screen
			if self.iCurrentComic == len(self.getComicStrip())-1:
				self.closeComicPage()

			if self.iCurrentComic != -1:
				self.hideComic(self.iCurrentComic)
			self.iCurrentComic += 1
			self.showComic(self.iCurrentComic)
		
		elif direction == "backward":
			if self.iCurrentComic == 0: # can only go back to the first comic
				return
			AWComic = self.getComic(self.iCurrentComic)
			
			self.hideComic(self.iCurrentComic)
			self.iCurrentComic -= 1
			self.showComic(self.iCurrentComic)
	
	
	# Will handle the input for this screen...
	def handleInput (self, inputClass):
#		print("\ngetNotifyCode: %s" %(inputClass.getNotifyCode()))
#		print("getData: %s" %(inputClass.getData()))
#		print("getFlags: %s" %(inputClass.getFlags()))
#		print("getID: %s" %(inputClass.getID()))
#		print("getFunctionName: %s" %(inputClass.getFunctionName()))
#		print("getButtonType: %s" %(inputClass.getButtonType()))
#		print("getData1: %s" %(inputClass.getData1()))
#		print("getData2: %s" %(inputClass.getData2()))
#		print("getOption: %s" %(inputClass.getOption()))
#		
		if inputClass.getID() == 1:
			return
			
		bRightClick = False
		if (inputClass.getFlags() & MouseFlags.MOUSE_RBUTTONUP):
			bRightClick = True
		
		if inputClass.getNotifyCode() == NotifyCode.NOTIFY_CLICKED and bRightClick == False or inputClass.getData() == int(InputTypes.KB_RETURN) or inputClass.getData() == int(InputTypes.KB_SPACE) or inputClass.getData() == int(InputTypes.KB_RIGHT):
			if self.iComicStripType == 1 and self.iCurrentComic == 14:
				return 1
			self.processComicStrip("forward")

		elif inputClass.getNotifyCode() == NotifyCode.NOTIFY_CLICKED or inputClass.getData() == int(InputTypes.KB_BACKSPACE) or inputClass.getData() == int(InputTypes.KB_LEFT):
			self.processComicStrip("backward")

		elif inputClass.getData() == int(InputTypes.KB_ESCAPE):
			self.closeComicPage()

		return 0
	
	def closeComicPage(self):
		CyGInterfaceScreen( "WonderMovieScreen", CvScreenEnums.WONDER_MOVIE_SCREEN ).hideScreen()
		
		if self.iComicStripType == 1:
			self.iCounter = 0
			CyInterface().exitingToMainMenu("", false)
		
		else:
			Afterworld.AfterworldMessages = []
		
			self.addPopup(localText.getText("TXT_KEY_TUTORIALTITLE", ()), localText.getText("TXT_KEY_TUTORIAL1", ()))
			self.addPopup(localText.getText("TXT_KEY_TUTORIALTITLE", ()), localText.getText("TXT_KEY_OBJECTIVE_ONE", ()))
	
			Afterworld.addAfterworldMessage( localText.getText("TXT_KEY_JAL", ()), localText.getText("TXT_KEY_CS_1_1_1", ()))
			Afterworld.addAfterworldMessage( localText.getText("TXT_KEY_JAL", ()), localText.getText("TXT_KEY_CS_1_1_2", ()))
			Afterworld.addAfterworldMessage( localText.getText("TXT_KEY_ATTICUS", ()), localText.getText("TXT_KEY_CS_1_1_3", ()))
			Afterworld.addAfterworldMessage( localText.getText("TXT_KEY_RIEST", ()), localText.getText("TXT_KEY_CS_1_1_4", ()))
			Afterworld.addAfterworldMessage( localText.getText("TXT_KEY_RAGAH", ()), localText.getText("TXT_KEY_RAGAHTOUCHDOWN", ()))
			Afterworld.addAfterworldMessage( localText.getText("TXT_KEY_ATTICUS", ()), localText.getText("TXT_KEY_CS_1_1_6", ()))
			Afterworld.addAfterworldMessage( localText.getText("TXT_KEY_JAL", ()), localText.getText("TXT_KEY_CS_1_1_7", ()))
			Afterworld.addAfterworldMessage( localText.getText("TXT_KEY_JAL", ()), localText.getText("TXT_KEY_JALTOUCHDOWN1", ()))
			Afterworld.addAfterworldMessage( localText.getText("TXT_KEY_JAL", ()), localText.getText("TXT_KEY_ATTICUSTOUCHDOWN", ()))
			Afterworld.addAfterworldMessage( localText.getText("TXT_KEY_SEVER", ()), localText.getText("TXT_KEY_CS_1_1_9", ()))
			Afterworld.addAfterworldMessage( localText.getText("TXT_KEY_SEVER", ()), localText.getText("TXT_KEY_CS_1_1_10", ()))
			Afterworld.addAfterworldMessage( localText.getText("TXT_KEY_RIEST", ()), localText.getText("TXT_KEY_CS_1_1_11", ()))
			Afterworld.addAfterworldMessage( localText.getText("TXT_KEY_ATTICUS", ()), localText.getText("TXT_KEY_CS_1_1_12", ()))
			Afterworld.addAfterworldMessage( localText.getText("TXT_KEY_ATTICUS", ()), localText.getText("TXT_KEY_CS_1_1_14", ()))
			Afterworld.addAfterworldMessage( localText.getText("TXT_KEY_RAGAH", ()), localText.getText("TXT_KEY_CS_1_1_15", ()))
		
	def addPopup(self, szTitle, szText):
		# Don't display popups for autoplay games
		if (gc.getPlayer(CyGame().getActivePlayer()).isAlive()):
			Afterworld.addAfterworldMessage(szTitle, szText)
			popup = PyPopup.PyPopup(-1)
			popup.setHeaderString(szTitle)
			popup.setBodyString(szText)
			popup.launch(true, PopupStates.POPUPSTATE_QUEUED)
	
	def update(self, fDelta):
		if self.iCounter > 0:
			self.iCounter -= fDelta
		
		else:
			self.processComicStrip("forward")
		
		return
