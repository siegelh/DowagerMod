## Sid Meier's Civilization 4
## Copyright Firaxis Games 2005

import CvUtil
from CvPythonExtensions import *

ArtFileMgr = CyArtFileMgr()
localText = CyTranslator()
gc = CyGlobalContext()

class CvDawnOfMan:
	"Dawn of man screen"
	def __init__(self, iScreenID):
		self.iScreenID = iScreenID
		
		self.X_SCREEN = 0
		self.Y_SCREEN = 0
		self.W_SCREEN = 1024
		self.H_SCREEN = 768
		
		# < Dawn Of Man Start >
		self.W_TECH = 425
		self.H_TECH = 80

		self.W_MAIN_PANEL = 750 # Was 550
		# < Dawn Of Man End   >
		
		self.H_MAIN_PANEL = 250#500
		
		# < Dawn Of Man Start >
		self.X_MAIN_PANEL = (self.W_SCREEN/2) - (self.W_MAIN_PANEL/2)# Was 250
		# < Dawn Of Man End   >
		
		self.Y_MAIN_PANEL = 70
		
		self.iMarginSpace = 15
		
		self.X_HEADER_PANEL = self.X_MAIN_PANEL + self.iMarginSpace
		self.Y_HEADER_PANEL = self.Y_MAIN_PANEL + self.iMarginSpace
		self.W_HEADER_PANEL = self.W_MAIN_PANEL - (self.iMarginSpace * 2)
		self.H_HEADER_PANEL = int(self.H_MAIN_PANEL * (2.0 / 5.0))
		
		self.X_LEADER_ICON = self.X_HEADER_PANEL + self.iMarginSpace
		self.Y_LEADER_ICON = self.Y_HEADER_PANEL + self.iMarginSpace
		self.H_LEADER_ICON = self.H_HEADER_PANEL - (15 * 2)#140
		self.W_LEADER_ICON = int(self.H_LEADER_ICON / 1.272727)#110
		
		
		# < Dawn Of Man Start >
		self.X_FANCY_ICON1 = self.X_HEADER_PANEL + 170
		self.X_FANCY_ICON2 = self.X_HEADER_PANEL + (self.W_MAIN_PANEL - 120) # Was 430
		self.Y_FANCY_ICON = (self.Y_HEADER_PANEL + self.iMarginSpace + 6) - 6
		self.WH_FANCY_ICON = 64
		# < Dawn Of Man End   >
		
#		iWHeaderPanelRemainingAfterLeader = self.W_HEADER_PANEL - self.W_LEADER_ICON + (self.iMarginSpace * 3)
#		iXHeaderPanelRemainingAfterLeader = self.X_LEADER_ICON + self.W_LEADER_ICON + self.iMarginSpace
		#self.X_LEADER_TITLE_TEXT = 510#iXHeaderPanelRemainingAfterLeader + (iWHeaderPanelRemainingAfterLeader / 2)

		# < Dawn Of Man Start >
		self.X_LEADER_TITLE_TEXT = (self.X_FANCY_ICON1+self.WH_FANCY_ICON)+((self.X_FANCY_ICON2 - (self.X_FANCY_ICON1+self.WH_FANCY_ICON))/2) - ((self.W_HEADER_PANEL / 3)/2)
		# < Dawn Of Man End   >		
		
		self.Y_LEADER_TITLE_TEXT = self.Y_HEADER_PANEL + self.iMarginSpace + 6
		self.W_LEADER_TITLE_TEXT = self.W_HEADER_PANEL / 3
		self.H_LEADER_TITLE_TEXT = self.H_HEADER_PANEL / 2
		
		self.X_STATS_TEXT = self.X_FANCY_ICON1# + self.W_LEADER_ICON + (self.iMarginSpace * 2) + 5
		self.Y_STATS_TEXT = self.Y_LEADER_TITLE_TEXT + 75
		# < Dawn Of Man Start >		
		self.W_STATS_TEXT = int(self.W_HEADER_PANEL * (5 / 7.0)) + (self.iMarginSpace * 2)
		self.H_STATS_TEXT = int(self.H_HEADER_PANEL * (3 / 5.0)) - (self.iMarginSpace * 2)
		# < Dawn Of Man End   >
		
		self.X_TEXT_PANEL = self.X_HEADER_PANEL
		self.Y_TEXT_PANEL = self.Y_HEADER_PANEL + self.H_HEADER_PANEL + self.iMarginSpace - 10 #10 is the fudge factor
		self.W_TEXT_PANEL = self.W_HEADER_PANEL
		self.H_TEXT_PANEL = self.H_MAIN_PANEL - self.H_HEADER_PANEL - (self.iMarginSpace * 3) + 10 #10 is the fudge factor
		self.iTEXT_PANEL_MARGIN = 35
		
		self.W_EXIT = 120
		self.H_EXIT = 30
		
		# < Dawn Of Man Start >
		self.X_EXIT = (self.W_SCREEN/2) - (self.W_EXIT/2) # Was 460
		self.Y_EXIT = self.Y_MAIN_PANEL + 440
		# < Dawn Of Man End   >
				
				
	def interfaceScreen(self):
		'Use a popup to display the opening text'
		if ( CyGame().isPitbossHost() ):
			return
		
		self.calculateSizesAndPositions()
		
		self.player = gc.getPlayer(gc.getGame().getActivePlayer())
		self.EXIT_TEXT = localText.getText("TXT_KEY_SCREEN_CONTINUE", ())
		
		# Create screen
		
		screen = CyGInterfaceScreen( "CvDawnOfMan", self.iScreenID )		
		screen.showScreen(PopupStates.POPUPSTATE_QUEUED, False)
		screen.showWindowBackground( False )
		screen.setDimensions(self.X_SCREEN, screen.centerY(self.Y_SCREEN), self.W_SCREEN, self.H_SCREEN)
		screen.enableWorldSounds( false )
		
		# Create panels
		
		# Main
		szMainPanel = "DawnOfManMainPanel"
		screen.addPanel( szMainPanel, "", "", true, true,
			self.X_MAIN_PANEL, self.Y_MAIN_PANEL, self.W_MAIN_PANEL, self.H_MAIN_PANEL, PanelStyles.PANEL_STYLE_MAIN )
		
		# Top
#		szHeaderPanel = "DawnOfManHeaderPanel"
#		screen.addPanel( szHeaderPanel, "", "", true, false,
#			self.X_HEADER_PANEL, self.Y_HEADER_PANEL, self.W_HEADER_PANEL, self.H_HEADER_PANEL, PanelStyles.PANEL_STYLE_DAWNTOP )
		
		# Bottom
		szTextPanel = "DawnOfManTextPanel"
		screen.addPanel( szTextPanel, "", "", true, true,
			self.X_TEXT_PANEL, self.Y_HEADER_PANEL, self.W_TEXT_PANEL, self.H_TEXT_PANEL+self.H_HEADER_PANEL+10, PanelStyles.PANEL_STYLE_DAWNBOTTOM )
		
		# Add contents
		
		# Leaderhead graphic
#		szLeaderPanel = "DawnOfManLeaderPanel"
#		screen.addPanel( szLeaderPanel, "", "", true, false,
#			self.X_LEADER_ICON - 3, self.Y_LEADER_ICON - 5, self.W_LEADER_ICON + 6, self.H_LEADER_ICON + 8, PanelStyles.PANEL_STYLE_DAWNTOP )
#		screen.addLeaderheadGFC("LeaderHead", self.player.getLeaderType(), AttitudeTypes.ATTITUDE_PLEASED,
#			self.X_LEADER_ICON + 5, self.Y_LEADER_ICON + 5, self.W_LEADER_ICON - 10, self.H_LEADER_ICON - 10, WidgetTypes.WIDGET_GENERAL, -1, -1)
		
		# Info/"Stats" text
		
#		szNameText = "<color=255,255,0,255>" + u"<font=3b>" + gc.getLeaderHeadInfo(self.player.getLeaderType()).getDescription().upper() + u"</font>" + "\n- " + self.player.getCivilizationDescription(0) + " -"
#		screen.addMultilineText( "NameText", szNameText, self.X_LEADER_TITLE_TEXT, self.Y_LEADER_TITLE_TEXT, self.W_LEADER_TITLE_TEXT, self.H_LEADER_TITLE_TEXT, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_CENTER_JUSTIFY)
		
#		self.Text_BoxText = CyGameTextMgr().parseLeaderTraits(self.player.getLeaderType(), self.player.getCivilizationType(), True, False)
		#self.Text_BoxText += "\n" + CyGameTextMgr().parseCivInfos(self.player.getCivilizationType(), True)
		
#		screen.addMultilineText( "HeaderText", localText.getText("TXT_KEY_DEFENSE_MAIN_TITLE", ()) , self.X_STATS_TEXT, self.Y_STATS_TEXT, self.W_STATS_TEXT, self.H_STATS_TEXT, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)

#		screen.addMultilineText( "HeaderText2", localText.getText("TXT_KEY_FREE_TECHS", ()) + ":", self.X_STATS_TEXT, self.Y_STATS_TEXT+20, self.W_STATS_TEXT, self.H_STATS_TEXT, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)

#		screen.addPanel( "HeaderText3", "", "", false, true,
#				 self.X_STATS_TEXT, self.Y_STATS_TEXT+35, self.W_TECH, self.H_TECH, PanelStyles.PANEL_STYLE_EMPTY )
		
#		for iTech in range(gc.getNumTechInfos()):
#			if (gc.getCivilizationInfo(self.player.getCivilizationType()).isCivilizationFreeTechs(iTech)):
#				screen.attachImageButton( "HeaderText3", "", gc.getTechInfo(iTech).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_TECH, iTech, 1, False )
			
#		self.Text_BoxText = localText.getText("TXT_KEY_FREE_UNITS", ()) + ":\n" + CyGameTextMgr().parseCivInfos(self.player.getCivilizationType(), True).split(localText.getText("TXT_KEY_FREE_UNITS", ()) + ":")[1]
		
#		screen.addMultilineText( "HeaderText4", self.Text_BoxText, self.X_STATS_TEXT, self.Y_STATS_TEXT+30+self.H_TECH, self.W_STATS_TEXT - (self.iMarginSpace * 3), self.H_STATS_TEXT - (self.iMarginSpace * 4), WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
							
		# Fancy icon things
		# < Dawn Of Man Start >
		#screen.addDDSGFC( "IconLeft", gc.getMissionInfo(MissionTypes.MISSION_FORTIFY).getButton(), self.X_FANCY_ICON1 , self.Y_FANCY_ICON , self.WH_FANCY_ICON, self.WH_FANCY_ICON, WidgetTypes.WIDGET_GENERAL, -1, -1 )
		#screen.addDDSGFC( "IconRight", gc.getMissionInfo(MissionTypes.MISSION_FORTIFY).getButton(), self.X_FANCY_ICON2 , self.Y_FANCY_ICON , self.WH_FANCY_ICON, self.WH_FANCY_ICON, WidgetTypes.WIDGET_GENERAL, -1, -1 )
#		screen.addDDSGFC( "IconLeft", ArtFileMgr.getCivilizationArtInfo(gc.getCivilizationInfo(self.player.getCivilizationType()).getArtDefineTag()).getButton(), self.X_FANCY_ICON1 , self.Y_FANCY_ICON , self.WH_FANCY_ICON, self.WH_FANCY_ICON, WidgetTypes.WIDGET_GENERAL, -1, -1 )
#		screen.addDDSGFC( "IconRight", ArtFileMgr.getCivilizationArtInfo(gc.getCivilizationInfo(self.player.getCivilizationType()).getArtDefineTag()).getButton(), self.X_FANCY_ICON2 , self.Y_FANCY_ICON , self.WH_FANCY_ICON, self.WH_FANCY_ICON, WidgetTypes.WIDGET_GENERAL, -1, -1 )
		# < Dawn Of Man End   >
		
		# Main Body text
		szDawnTitle = u"<font=3>" + localText.getText("TXT_KEY_DEFENSE_RULES_OF_GAME_SCREEN_TITLE", ()).upper() + u"</font>"
		screen.setLabel("DawnTitle", "Background", szDawnTitle, CvUtil.FONT_CENTER_JUSTIFY,
				self.X_TEXT_PANEL + (self.W_TEXT_PANEL / 2), self.Y_HEADER_PANEL + 15, -2.0, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
		bodyString = localText.getText("TXT_KEY_DEFENSE_RULES_TEXT", (CyGameTextMgr().getTimeStr(gc.getGame().getGameTurn(), false), self.player.getCivilizationAdjectiveKey(), self.player.getNameKey()))
		screen.addMultilineText( "BodyText", bodyString, self.X_TEXT_PANEL + self.iMarginSpace, self.Y_HEADER_PANEL + self.iMarginSpace + self.iTEXT_PANEL_MARGIN, self.W_TEXT_PANEL - (self.iMarginSpace * 2),  self.H_TEXT_PANEL+self.H_TEXT_PANEL - (self.iMarginSpace * 2) - 75, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
		
		screen.setButtonGFC("Exit", self.EXIT_TEXT, "", self.X_EXIT, self.Y_EXIT, self.W_EXIT, self.H_EXIT, WidgetTypes.WIDGET_CLOSE_SCREEN, -1, -1, ButtonStyles.BUTTON_STYLE_STANDARD )
		
		pActivePlayer = gc.getPlayer(CyGame().getActivePlayer())
		pLeaderHeadInfo = gc.getLeaderHeadInfo(pActivePlayer.getLeaderType())
		screen.setSoundId(CyAudioGame().Play2DSoundWithId(pLeaderHeadInfo.getDiploPeaceMusicScriptIds(0)))
		
	def handleInput( self, inputClass ):
		return 0
	
	def update(self, fDelta):
		return
		
	# < Dawn Of Man Start >
	# Added to make the screen Warlords compatible.
	def onClose(self):
		CyInterface().setSoundSelectionReady(true)		
		return 0
	# < Dawn Of Man End   >		
		
		
	# < Dawn Of Man Start >
	
	def calculateSizesAndPositions(self):
		self.X_SCREEN = 0
		self.Y_SCREEN = 0
		
		# < Dawn Of Man Start >
		screen = CyGInterfaceScreen( "CvDawnOfMan", self.iScreenID )
		
		self.W_SCREEN = screen.getXResolution()
		self.H_SCREEN = screen.getYResolution()		
		
		self.W_TECH = 425
		self.H_TECH = 80

		self.W_MAIN_PANEL = 750 # Was 550
		# < Dawn Of Man End   >
		
		# < Dawn Of Man Start >
		self.H_MAIN_PANEL = 525
		self.X_MAIN_PANEL = (self.W_SCREEN/2) - (self.W_MAIN_PANEL/2)# Was 250
		# < Dawn Of Man End   >
		
		self.Y_MAIN_PANEL = 70
		
		self.iMarginSpace = 15
		
		self.X_HEADER_PANEL = self.X_MAIN_PANEL + self.iMarginSpace
		self.Y_HEADER_PANEL = self.Y_MAIN_PANEL + self.iMarginSpace
		self.W_HEADER_PANEL = self.W_MAIN_PANEL - (self.iMarginSpace * 2)
		self.H_HEADER_PANEL = int(self.H_MAIN_PANEL * (2.0 / 5.0)) + 60
		
		self.X_LEADER_ICON = self.X_HEADER_PANEL + self.iMarginSpace
		self.Y_LEADER_ICON = self.Y_HEADER_PANEL + self.iMarginSpace
		self.H_LEADER_ICON = self.H_HEADER_PANEL - (15 * 2)#140
		self.W_LEADER_ICON = int(self.H_LEADER_ICON / 1.272727)#110
		
		
		# < Dawn Of Man Start >
		self.WH_FANCY_ICON = 64
		self.X_FANCY_ICON1 = self.X_LEADER_ICON + self.W_LEADER_ICON + self.iMarginSpace
		self.X_FANCY_ICON2 = self.X_LEADER_ICON + (self.W_HEADER_PANEL - (self.iMarginSpace * 2) - self.WH_FANCY_ICON) # Was 430
		self.Y_FANCY_ICON = (self.Y_HEADER_PANEL + self.iMarginSpace + 6) - 6
		# < Dawn Of Man End   >
		
#		iWHeaderPanelRemainingAfterLeader = self.W_HEADER_PANEL - self.W_LEADER_ICON + (self.iMarginSpace * 3)
#		iXHeaderPanelRemainingAfterLeader = self.X_LEADER_ICON + self.W_LEADER_ICON + self.iMarginSpace
		#self.X_LEADER_TITLE_TEXT = 510#iXHeaderPanelRemainingAfterLeader + (iWHeaderPanelRemainingAfterLeader / 2)

		# < Dawn Of Man Start >
		self.X_LEADER_TITLE_TEXT = (self.X_FANCY_ICON1+self.WH_FANCY_ICON)+((self.X_FANCY_ICON2 - (self.X_FANCY_ICON1+self.WH_FANCY_ICON))/2) - ((self.W_HEADER_PANEL / 3)/2)
		# < Dawn Of Man End   >		
		
		self.Y_LEADER_TITLE_TEXT = self.Y_HEADER_PANEL + self.iMarginSpace + 6
		self.W_LEADER_TITLE_TEXT = self.W_HEADER_PANEL / 3
		self.H_LEADER_TITLE_TEXT = self.H_HEADER_PANEL / 2
		
		self.X_STATS_TEXT = self.X_FANCY_ICON1# + self.W_LEADER_ICON + (self.iMarginSpace * 2) + 5
		
		# < Dawn Of Man Start >		
		self.Y_STATS_TEXT = self.Y_LEADER_TITLE_TEXT + 60
		self.W_STATS_TEXT = int(self.W_HEADER_PANEL * (5 / 7.0)) + (self.iMarginSpace * 2)
		self.H_STATS_TEXT = int(self.H_HEADER_PANEL * (3 / 5.0)) - (self.iMarginSpace * 2)
		
		self.X_TEXT_PANEL = self.X_HEADER_PANEL
		self.Y_TEXT_PANEL = self.Y_HEADER_PANEL + self.H_HEADER_PANEL + self.iMarginSpace - 10 #10 is the fudge factor
		self.W_TEXT_PANEL = self.W_HEADER_PANEL
		self.H_TEXT_PANEL = self.H_MAIN_PANEL - self.H_HEADER_PANEL - (self.iMarginSpace * 3) + 10 #10 is the fudge factor
		self.iTEXT_PANEL_MARGIN = 35
		# < Dawn Of Man End   >
		
		self.W_EXIT = 120
		self.H_EXIT = 30
		
		# < Dawn Of Man Start >
		self.X_EXIT = (self.W_SCREEN/2) - (self.W_EXIT/2) # Was 460
		self.Y_EXIT = self.Y_TEXT_PANEL + self.H_TEXT_PANEL - (self.iMarginSpace * 3)
		# < Dawn Of Man End   >	
	# < Dawn Of Man End   >		