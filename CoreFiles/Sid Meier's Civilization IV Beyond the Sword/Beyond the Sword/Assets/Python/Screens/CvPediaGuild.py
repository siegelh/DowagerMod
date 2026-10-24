from CvPythonExtensions import *
import CvUtil
import CvScreenEnums

gc = CyGlobalContext()
localText = CyTranslator()


class CvPediaGuild:
	def __init__(self, main):
		self.top = main
		self.iGuild = -1

	def interfaceScreen(self, iGuild):
		self.iGuild = iGuild
		self.top.deleteAllWidgets()
		screen = self.top.getScreen()
		bNotActive = not screen.isActive()
		if bNotActive:
			self.top.setPediaCommonWidgets()

		guild = gc.getGuildInfo(iGuild)
		screen.setLabel(self.top.getNextWidgetName(), "Background", u"<font=4b>%s</font>" % guild.getDescription().upper(),
			CvUtil.FONT_CENTER_JUSTIFY, self.top.X_SCREEN, self.top.Y_TITLE, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
		screen.setText(self.top.getNextWidgetName(), "Background", self.top.MENU_TEXT, CvUtil.FONT_LEFT_JUSTIFY,
			self.top.X_MENU, self.top.Y_MENU, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_PEDIA_MAIN,
			CivilopediaPageTypes.CIVILOPEDIA_PAGE_GUILD, -1)

		if self.top.iLastScreen != CvScreenEnums.PEDIA_GUILD or bNotActive:
			self.placeLinks(True)
			self.top.iLastScreen = CvScreenEnums.PEDIA_GUILD
		else:
			self.placeLinks(False)

		screen.addPanel(self.top.getNextWidgetName(), "", "", False, False, 50, 90, 250, 250, PanelStyles.PANEL_STYLE_BLUE50)
		screen.addPanel(self.top.getNextWidgetName(), "", "", False, False, 98, 125, 150, 190, PanelStyles.PANEL_STYLE_MAIN)
		screen.addDDSGFC(self.top.getNextWidgetName(), guild.getButton(), 141, 188, 64, 64, WidgetTypes.WIDGET_GENERAL, -1, -1)

		self.placeRequires(guild)
		self.placeEffects(guild)
		self.placeText(guild)

	def _defaultBuilding(self, iClass):
		return gc.getBuildingClassInfo(iClass).getDefaultBuildingIndex()

	def _defaultUnit(self, iClass):
		return gc.getUnitClassInfo(iClass).getDefaultUnitIndex()

	def placeRequires(self, guild):
		screen = self.top.getScreen()
		panel = self.top.getNextWidgetName()
		screen.addPanel(panel, localText.getText("TXT_KEY_PEDIA_REQUIRES", ()), "", False, True, 330, 70, 425, 110, PanelStyles.PANEL_STYLE_BLUE50)
		screen.attachLabel(panel, "", "  ")
		if guild.getTechPrereq() >= 0:
			screen.attachImageButton(panel, "", gc.getTechInfo(guild.getTechPrereq()).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM,
				WidgetTypes.WIDGET_PEDIA_JUMP_TO_TECH, guild.getTechPrereq(), 1, False)
		iFounder = self._defaultUnit(guild.getFounderUnitClass())
		if iFounder >= 0:
			screen.attachImageButton(panel, "", gc.getUnitInfo(iFounder).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM,
				WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT, iFounder, 1, False)
		for i in range(guild.getNumProcessorBuildingClasses()):
			iBuilding = self._defaultBuilding(guild.getProcessorBuildingClass(i))
			if iBuilding >= 0:
				screen.attachImageButton(panel, "", gc.getBuildingInfo(iBuilding).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM,
					WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING, iBuilding, 1, False)

	def placeEffects(self, guild):
		screen = self.top.getScreen()
		panel = self.top.getNextWidgetName()
		screen.addPanel(panel, localText.getText("TXT_KEY_PEDIA_EFFECTS", ()), "", True, False, 330, 190, 425, 150, PanelStyles.PANEL_STYLE_BLUE50)
		iHouse = self._defaultBuilding(guild.getHouseBuildingClass())
		iHQ = self._defaultBuilding(guild.getHeadquartersBuildingClass())
		iEmissary = self._defaultUnit(guild.getEmissaryUnitClass())
		lines = [
			u"%d total licenses shared by sponsored branches and living emissaries." % guild.getLicenseCap(),
			u"Headquarters: %s" % (iHQ >= 0 and gc.getBuildingInfo(iHQ).getDescription() or u"-"),
			u"Branch: %s" % (iHouse >= 0 and gc.getBuildingInfo(iHouse).getDescription() or u"-"),
			u"Emissary: %s" % (iEmissary >= 0 and gc.getUnitInfo(iEmissary).getDescription() or u"-"),
			u"Foreign branches require peace and Open Borders; inactive networks become dormant.",
		]
		screen.addMultilineText(self.top.getNextWidgetName(), u"\n".join(lines), 335, 220, 415, 115,
			WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)

	def placeText(self, guild):
		screen = self.top.getScreen()
		panel = self.top.getNextWidgetName()
		screen.addPanel(panel, "", "", True, True, 50, 360, 705, 290, PanelStyles.PANEL_STYLE_BLUE50)
		screen.attachMultilineText(panel, "Text", guild.getCivilopedia() + u"\n\n" + guild.getHelp() + u"\n\n" + guild.getStrategy(),
			WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)

	def placeLinks(self, bRedraw):
		screen = self.top.getScreen()
		if bRedraw:
			screen.clearListBoxGFC(self.top.LIST_ID)
		items = []
		for iGuild in range(gc.getNumGuildInfos()):
			items.append((gc.getGuildInfo(iGuild).getDescription(), iGuild))
		items.sort()
		iSelected = 0
		for i in range(len(items)):
			if bRedraw:
				screen.appendListBoxStringNoUpdate(self.top.LIST_ID, items[i][0], WidgetTypes.WIDGET_GENERAL, items[i][1], 0, CvUtil.FONT_LEFT_JUSTIFY)
			if items[i][1] == self.iGuild:
				iSelected = i
		if bRedraw:
			screen.updateListBox(self.top.LIST_ID)
		screen.setSelectedListBoxStringGFC(self.top.LIST_ID, iSelected)

	def handleInput(self, inputClass):
		if inputClass.getNotifyCode() == NotifyCode.NOTIFY_LISTBOX_ITEM_SELECTED:
			self.interfaceScreen(inputClass.getData1())
			return 1
		return 0
