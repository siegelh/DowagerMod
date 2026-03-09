## Sid Meier's Civilization 4
## Copyright Firaxis Games 2005
from CvPythonExtensions import *
import PyHelpers
import CvUtil
import ScreenInput
import CvScreenEnums
import BrokenStar
import CvGameUtils

PyPlayer = PyHelpers.PyPlayer
PyCity = PyHelpers.PyCity

#	IMPORTANT INFORMATION
#	
#	All widget names MUST be unique when creating screens.  If you create
#	a widget named 'Hello', and then try to create another named 'Hello', it
#	will modify the first hello.
#
#	Also, when attaching widgets, 'Background' is a reserve word meant for
#	the background widget.  Do NOT use 'Background' to name any widget, but
#	when attaching to the background, please use the 'Background' keyword.

# globals
gc = CyGlobalContext()
ArtFileMgr = CyArtFileMgr()
localText = CyTranslator()

class CvBuySellUnits:
	"Buy Sell Units Screen"
	def __init__(self):
		#self.X_SCREEN = 500 # distance from screens left side panel will start from.
		#self.Y_SCREEN = 50 # Distance from the screens top side panel will start from.
		self.W_BG = 400 # The width of the panel's background.
		self.H_BG = 200 # The height of the panel's background.
		self.X_EXIT = 350
		self.Y_EXIT = 175
		self.BUTTON_SIZE = 64
		self.PROMOTION_ICON_SIZE = 32
		self.nWidgetCount = 0
		self.WIDGET_ID = "BuySellUnitsWidget"
		self.UNITS_FOR_BUTTONS = ['UNIT_INFANTRY2','UNIT_GUNSHIP3','UNIT_ARTILLERY3']
		return
	


	# Screen construction function
	def interfaceScreen(self):
		screen = self.getScreen()
		xResolution = screen.getXResolution()
		yResolution = screen.getYResolution()
		
		buttonStartX=300
		buttonStartY=60
		pHeadSelectedCity = CyInterface().getHeadSelectedCity()
		player = PyPlayer(CyGame().getActivePlayer()).CyGet()

		# Create a new screen, called BuySellUnits, using the file CvBuySellUnits.py for input
		screen = CyGInterfaceScreen( "BuySellUnits", CvScreenEnums.BUY_SELL_UNITS )
		#screen.setDimensions(screen.centerX(0), screen.centerY(0), xResolution, yResolution)
		screen.showScreen(PopupStates.POPUPSTATE_IMMEDIATE, False)
	
		# Here we set the background widget and exit button, and we show the screen
		screen.addPanel( "BuySellUnitsBG", u"", u"", True, False, xResolution-self.W_BG, 50, self.W_BG, self.H_BG, PanelStyles.PANEL_STYLE_MAIN )
		screen.setText(self.getNextWidgetName(), "BuySellUnitsBG", localText.getText("TXT_KEY_PEDIA_SCREEN_EXIT", ()).upper(), CvUtil.FONT_RIGHT_JUSTIFY, xResolution-30, 220, -0.03, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_CLOSE_SCREEN, -1, -1 )

		
		screen.addMultiListControlGFCAt( "BuySellUnitsBG", "BuySellUnitsContainer", u"", 5, 5, self.W_BG-10, self.H_BG-35, 4, 48, 48, TableStyles.TABLE_STYLE_STANDARD )		
		screen.hide( "BuySellUnitsContainer" )
		
		iCount = 0
		iRow = 0
		bFound = False
		
		# Units to construct
		g_NumUnitClassInfos = gc.getNumUnitClassInfos()
		print "g_NumUnitClassInfos", g_NumUnitClassInfos
		for i in range ( g_NumUnitClassInfos ):
			eLoopUnit = gc.getCivilizationInfo(CyGame().getActivePlayer()).getCivilizationUnits(i)
			if(eLoopUnit > 0):
				#print "eLoopUnit", eLoopUnit
				bCanTrain = player.canTrain(eLoopUnit, False, True)
				iDomainType = gc.getUnitInfo(eLoopUnit).getDomainType()
				bValid = self.checkUnitValid(eLoopUnit)
				if (bCanTrain and iDomainType != 0 and bValid == True):
					screen.appendMultiListButton( "BuySellUnitsContainer", gc.getUnitInfo(eLoopUnit).getButton(), iRow, WidgetTypes.WIDGET_GENERAL, eLoopUnit, 613, False )
						
					if ( not player.canTrain(eLoopUnit, False, False) ):
						screen.disableMultiListButton( "BuySellUnitsContainer", iRow, iCount, gc.getUnitInfo(eLoopUnit).getButton() )
						
					iCount = iCount + 1
					bFound = True

		screen.show( "BuySellUnitsContainer" )
					
		CyInterface().setDirty(InterfaceDirtyBits.MiscButtons_DIRTY_BIT, True)

		# Draw the city list...
		self.drawContents( )
		
	# Function to draw the contents of the cityList passed in
	def drawContents (self):
		screen = self.getScreen()
		screen.moveToFront( "Background" )
		screen.moveToBack( "BuySellUnitsBG" )
		
	# Will handle the input for this screen...	
	def handleInput (self, inputClass):
		' Calls function mapped in DomesticAdvisorInputMap'
		# only get from the map if it has the key
		
		screen = self.getScreen()
		
		print("\ngetNotifyCode: %s" %(inputClass.getNotifyCode()))
		print("getData: %s" %(inputClass.getData()))
		print("getFlags: %s" %(inputClass.getFlags()))
		print("getID: %s" %(inputClass.getID()))
		print("getFunctionName: %s" %(inputClass.getFunctionName()))
		print("getButtonType: %s" %(inputClass.getButtonType()))
		print("getData1: %s" %(inputClass.getData1()))
		print("getData2: %s" %(inputClass.getData2()))
		print("getOption: %s" %(inputClass.getOption()))
		
		if (inputClass.getNotifyCode() == NotifyCode.NOTIFY_CLICKED):
				if (inputClass.getFunctionName() == "BuySellUnitsExit"):
					self.deleteAllWidgets()
				if (inputClass.getButtonType() == 9):
					BrokenStar.BrokenStar().purchaseUnit(inputClass.getFunctionName())	
		if (inputClass.getNotifyCode() == 11 and inputClass.getData2() == 613):
			
			iNetMessage = BrokenStar.BrokenStar().iNetMessage_BuyUnit
			iPlayer = CyGame().getActivePlayer()
			iUnitType = inputClass.getData1()
			
			CyMessageControl().sendModNetMessage(iNetMessage,iPlayer,iUnitType,-1,-1)
								
	def update(self, fDelta):
		screen = self.getScreen()
		screen.moveToFront( "Background" )
		return
		
	def getNextWidgetName(self):
		szName = self.WIDGET_ID + str(self.nWidgetCount)
		self.nWidgetCount += 1
		return szName
		
	def deleteAllWidgets(self):
		screen = self.getScreen()
		screen.deleteWidget("BuySellUnitsContainer")
		
	def getScreen(self):
		return CyGInterfaceScreen( "BuySellUnits", CvScreenEnums.BUY_SELL_UNITS )
		
	def checkUnitValid(self, eLoopUnit): 
		iEra = 5
		if gc.getUnitInfo(eLoopUnit).getPrereqAndTech() != -1:
			iEra = gc.getTechInfo(gc.getUnitInfo(eLoopUnit).getPrereqAndTech()).getEra()
			
		for i in range(4):
			print iEra
			print i
			if iEra == i:
				return false
		#print "eLoopUnit Class Type", gc.getUnit(eLoopUnit).getUnitType()
		if eLoopUnit == CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_SETTLER'):
			return false
		if eLoopUnit == CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_TACTICAL_NUKE'):
			return false
		if eLoopUnit == CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_WARRIOR'):
			return false
		if eLoopUnit == CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_CANNON'):
			return false
		if eLoopUnit == CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_SETTLER'):
			return false
		if eLoopUnit == CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_JEWISH_MISSIONARY'):
			return false
		if eLoopUnit == CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_CONFUCIAN_MISSIONARY'):
			return false
		if eLoopUnit == CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_ISLAMIC_MISSIONARY'):
			return false
		if eLoopUnit == CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_HINDU_MISSIONARY'):
			return false
		if eLoopUnit == CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_BUDDHIST_MISSIONARY'):
			return false
		if eLoopUnit == CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_TAOIST_MISSIONARY'):
			return false
		if eLoopUnit == CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_GRENADIER'):
			return false
		if eLoopUnit == CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),'UNIT_JET_FIGHTER'):
			return false
		for i in range (8):
			if(i > 0):
				unitName = "UNIT_EXECUTIVE_" + str(i)
				if eLoopUnit == CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(),unitName):
					return false
			
		return true
