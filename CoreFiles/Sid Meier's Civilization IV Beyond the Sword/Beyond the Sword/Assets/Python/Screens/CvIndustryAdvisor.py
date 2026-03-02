from CvPythonExtensions import *
import CvUtil
import ScreenInput

# Game globals

gc = CyGlobalContext()
ArtFileMgr = CyArtFileMgr()
localText = CyTranslator()

INDUSTRY_ADVISOR_SCREEN = 4999

CORE_BUILDINGS = (
    'BUILDING_INDUSTRY_AGRARIAN_BOARD',
    'BUILDING_INDUSTRY_EXCHANGE_HALL',
    'BUILDING_INDUSTRY_MINING_BUREAU',
    'BUILDING_INDUSTRY_MANUFACTORIES_OFFICE',
    'BUILDING_INDUSTRY_FORESTRY_COMMISSION',
    'BUILDING_INDUSTRY_HYDRAULIC_OFFICE',
    'BUILDING_INDUSTRY_ESTATE_OFFICE',
    'BUILDING_INDUSTRY_PASTORAL_BOARD',
    'BUILDING_INDUSTRY_FRONTIER_LODGE',
    'BUILDING_INDUSTRY_MARITIME_EXCHANGE',
    'BUILDING_INDUSTRY_ENERGY_DIRECTORATE',
)

PROCESSING_CHAINS = (
    ('BUILDING_INDUSTRY_DYE_WORKS', ('BONUS_DYE',), 'BONUS_FINE_DYES'),
    ('BUILDING_INDUSTRY_FURRIERS_HALL', ('BONUS_FUR',), 'BONUS_FINE_FURS'),
    ('BUILDING_INDUSTRY_JEWELERS_QUARTER', ('BONUS_GEMS',), 'BONUS_CUT_GEMS'),
    ('BUILDING_INDUSTRY_MINTING_HOUSE', ('BONUS_GOLD',), 'BONUS_GOLD_BULLION'),
    ('BUILDING_INDUSTRY_PERFUMERS_SANCTUARY', ('BONUS_INCENSE',), 'BONUS_TEMPLE_INCENSE'),
    ('BUILDING_INDUSTRY_IVORY_CARVERS_ATELIER', ('BONUS_IVORY',), 'BONUS_IVORY_CARVINGS'),
    ('BUILDING_INDUSTRY_SILK_WEAVERS_WORKSHOP', ('BONUS_SILK',), 'BONUS_FINE_SILK'),
    ('BUILDING_INDUSTRY_SILVERSMITHS_HALL', ('BONUS_SILVER',), 'BONUS_WORKED_SILVER'),
    ('BUILDING_INDUSTRY_SPICE_EXCHANGE', ('BONUS_SPICES',), 'BONUS_SPICE_BLENDS'),
    ('BUILDING_INDUSTRY_CONFECTIONERS_GUILD', ('BONUS_SUGAR',), 'BONUS_CONFECTIONS'),
    ('BUILDING_INDUSTRY_VINTNERS_GUILD', ('BONUS_WINE',), 'BONUS_VINTAGE_WINE'),
    ('BUILDING_INDUSTRY_WHALE_OIL_CHANDLERY', ('BONUS_WHALE',), 'BONUS_LAMP_OIL'),
    ('BUILDING_INDUSTRY_PLAYWRIGHTS_GUILD', ('BONUS_DRAMA',), 'BONUS_STAGE_PLAYS'),
    ('BUILDING_INDUSTRY_RECORDING_HOUSE', ('BONUS_MUSIC',), 'BONUS_MASTER_RECORDINGS'),
    ('BUILDING_INDUSTRY_FILM_STUDIO_DISTRICT', ('BONUS_MOVIES',), 'BONUS_FILM_PRINTS'),
    ('BUILDING_INDUSTRY_MILLERS_GUILD', ('BONUS_WHEAT', 'BONUS_CORN', 'BONUS_RICE'), 'BONUS_FLOUR'),
    ('BUILDING_INDUSTRY_SMOKEHOUSE', ('BONUS_COW', 'BONUS_PIG', 'BONUS_SHEEP', 'BONUS_DEER'), 'BONUS_CURED_MEATS'),
    ('BUILDING_INDUSTRY_CANNERY', ('BONUS_FISH', 'BONUS_CLAM', 'BONUS_CRAB'), 'BONUS_PRESERVED_SEAFOOD'),
    ('BUILDING_INDUSTRY_FRUIT_PRESERVERS', ('BONUS_BANANA',), 'BONUS_FRUIT_PRESERVES'),
    ('BUILDING_INDUSTRY_SCULPTORS_YARD', ('BONUS_MARBLE',), 'BONUS_MARBLE_STATUARY'),
)

COMPOSITES = (
    ('BUILDING_INDUSTRY_ROYAL_GARMENTS_HOUSE', ('BONUS_FINE_SILK', 'BONUS_FINE_DYES')),
    ('BUILDING_INDUSTRY_NOBLE_TAILORS_HALL', ('BONUS_FINE_SILK', 'BONUS_FINE_FURS')),
    ('BUILDING_INDUSTRY_COURT_REGALIA_ATELIER', ('BONUS_FINE_SILK', 'BONUS_IVORY_CARVINGS')),
    ('BUILDING_INDUSTRY_DYED_FUR_SALON', ('BONUS_FINE_DYES', 'BONUS_FINE_FURS')),
    ('BUILDING_INDUSTRY_CROWN_JEWELER', ('BONUS_GOLD_BULLION', 'BONUS_CUT_GEMS')),
    ('BUILDING_INDUSTRY_ROYAL_MINT', ('BONUS_GOLD_BULLION', 'BONUS_WORKED_SILVER')),
    ('BUILDING_INDUSTRY_GEMCUTTERS_EXCHANGE', ('BONUS_WORKED_SILVER', 'BONUS_CUT_GEMS')),
    ('BUILDING_INDUSTRY_REGAL_TREASURES_COURT', ('BONUS_GOLD_BULLION', 'BONUS_IVORY_CARVINGS')),
    ('BUILDING_INDUSTRY_PERFUMERS_QUARTER', ('BONUS_TEMPLE_INCENSE', 'BONUS_SPICE_BLENDS')),
    ('BUILDING_INDUSTRY_GRAND_BANQUET_HALL', ('BONUS_VINTAGE_WINE', 'BONUS_CONFECTIONS')),
    ('BUILDING_INDUSTRY_CONFECTIONERS_EXCHANGE', ('BONUS_CONFECTIONS', 'BONUS_SPICE_BLENDS')),
    ('BUILDING_INDUSTRY_CEREMONIAL_CELLARS', ('BONUS_VINTAGE_WINE', 'BONUS_TEMPLE_INCENSE')),
    ('BUILDING_INDUSTRY_FESTIVAL_MARKET', ('BONUS_VINTAGE_WINE', 'BONUS_SPICE_BLENDS')),
    ('BUILDING_INDUSTRY_IMPERIAL_OUTFITTERS', ('BONUS_FINE_FURS', 'BONUS_IVORY_CARVINGS')),
    ('BUILDING_INDUSTRY_ADMIRALTY_CURIOS_HOUSE', ('BONUS_LAMP_OIL', 'BONUS_IVORY_CARVINGS')),
    ('BUILDING_INDUSTRY_NAVIGATORS_INSTRUMENT_WORKS', ('BONUS_LAMP_OIL', 'BONUS_WORKED_SILVER')),
    ('BUILDING_INDUSTRY_OPERA_HOUSE', ('BONUS_STAGE_PLAYS', 'BONUS_MASTER_RECORDINGS')),
    ('BUILDING_INDUSTRY_CINEMA_PALACE', ('BONUS_STAGE_PLAYS', 'BONUS_FILM_PRINTS')),
    ('BUILDING_INDUSTRY_SOUNDSTAGE_COMPLEX', ('BONUS_MASTER_RECORDINGS', 'BONUS_FILM_PRINTS')),
    ('BUILDING_INDUSTRY_MASS_ENTERTAINMENT_NETWORK', ('BONUS_STAGE_PLAYS', 'BONUS_MASTER_RECORDINGS', 'BONUS_FILM_PRINTS')),
    ('BUILDING_INDUSTRY_BAKERS_EXCHANGE', ('BONUS_FLOUR', 'BONUS_SPICE_BLENDS')),
    ('BUILDING_INDUSTRY_FESTIVAL_KITCHENS', ('BONUS_FLOUR', 'BONUS_VINTAGE_WINE')),
    ('BUILDING_INDUSTRY_ROYAL_KITCHENS', ('BONUS_CURED_MEATS', 'BONUS_VINTAGE_WINE')),
    ('BUILDING_INDUSTRY_SPICED_CARVERY', ('BONUS_CURED_MEATS', 'BONUS_SPICE_BLENDS')),
    ('BUILDING_INDUSTRY_MARITIME_SUPPER_CLUB', ('BONUS_PRESERVED_SEAFOOD', 'BONUS_VINTAGE_WINE')),
    ('BUILDING_INDUSTRY_PRESERVES_MARKET', ('BONUS_FRUIT_PRESERVES', 'BONUS_CONFECTIONS')),
    ('BUILDING_INDUSTRY_HALL_OF_CAMEOS', ('BONUS_MARBLE_STATUARY', 'BONUS_CUT_GEMS')),
    ('BUILDING_INDUSTRY_TRIUMPHAL_COURT', ('BONUS_MARBLE_STATUARY', 'BONUS_GOLD_BULLION')),
    ('BUILDING_INDUSTRY_GALLERY_OF_ANTIQUITIES', ('BONUS_MARBLE_STATUARY', 'BONUS_IVORY_CARVINGS')),
    ('BUILDING_INDUSTRY_SACRED_PRECINCT', ('BONUS_MARBLE_STATUARY', 'BONUS_TEMPLE_INCENSE')),
    ('BUILDING_INDUSTRY_PASTRY_HOUSE', ('BONUS_FLOUR', 'BONUS_FRUIT_PRESERVES')),
    ('BUILDING_INDUSTRY_VICTUALLERS_EXCHANGE', ('BONUS_FLOUR', 'BONUS_CURED_MEATS')),
    ('BUILDING_INDUSTRY_SPICED_FISH_MARKET', ('BONUS_PRESERVED_SEAFOOD', 'BONUS_SPICE_BLENDS')),
    ('BUILDING_INDUSTRY_DESSERT_CELLARS', ('BONUS_FRUIT_PRESERVES', 'BONUS_VINTAGE_WINE')),
    ('BUILDING_INDUSTRY_PERFUMED_SALON', ('BONUS_TEMPLE_INCENSE', 'BONUS_FINE_SILK')),
    ('BUILDING_INDUSTRY_LANTERN_PROCESSION_WORKS', ('BONUS_TEMPLE_INCENSE', 'BONUS_LAMP_OIL')),
    ('BUILDING_INDUSTRY_CURIO_AUCTION_HOUSE', ('BONUS_IVORY_CARVINGS', 'BONUS_CUT_GEMS')),
    ('BUILDING_INDUSTRY_ILLUMINATED_THEATRE', ('BONUS_LAMP_OIL', 'BONUS_STAGE_PLAYS')),
)

CORPORATIONS = (
    ('CORPORATION_1', ('BONUS_FLOUR', 'BONUS_CURED_MEATS', 'BONUS_PRESERVED_SEAFOOD', 'BONUS_FRUIT_PRESERVES')),
    ('CORPORATION_2', ('BONUS_VINTAGE_WINE', 'BONUS_CONFECTIONS')),
    ('CORPORATION_3', ('BONUS_FINE_SILK', 'BONUS_FINE_DYES', 'BONUS_CUT_GEMS', 'BONUS_GOLD_BULLION', 'BONUS_WORKED_SILVER', 'BONUS_FINE_FURS')),
    ('CORPORATION_4', ('BONUS_IVORY_CARVINGS', 'BONUS_LAMP_OIL', 'BONUS_MARBLE_STATUARY')),
    ('CORPORATION_5', ('BONUS_TEMPLE_INCENSE', 'BONUS_SPICE_BLENDS')),
    ('CORPORATION_6', ('BONUS_STAGE_PLAYS', 'BONUS_MASTER_RECORDINGS', 'BONUS_FILM_PRINTS')),
)


def getIndustryAdvisor():
    global g_IndustryAdvisor
    return g_IndustryAdvisor


class CvIndustryAdvisor:
    def __init__(self):
        self.SCREEN_NAME = 'IndustryAdvisor'
        self.WIDGET_ID = 'IndustryAdvisorWidget'
        self.TABLE_ID = 'IndustryAdvisorTable'
        self.EXIT_ID = 'IndustryAdvisorExit'
        self.BACKGROUND_ID = 'IndustryAdvisorBackground'
        self.TOP_PANEL_ID = 'IndustryAdvisorTopPanel'
        self.BOTTOM_PANEL_ID = 'IndustryAdvisorBottomPanel'
        self.MAIN_PANEL_ID = 'IndustryAdvisorMainPanel'
        self.HEADER_ID = 'IndustryAdvisorHeader'
        self.TAB_IDS = ('IndustryTabCities', 'IndustryTabGoods', 'IndustryTabChains')
        self.iTab = 0
        self.iActivePlayer = -1
        self.widgets = []
        self.typeCache = {}

    def getScreen(self):
        return CyGInterfaceScreen(self.SCREEN_NAME, INDUSTRY_ADVISOR_SCREEN)

    def _infoType(self, szType):
        if not self.typeCache.has_key(szType):
            self.typeCache[szType] = gc.getInfoTypeForString(szType)
        return self.typeCache[szType]

    def _addWidget(self, name):
        self.widgets.append(name)
        return name

    def _clearWidgets(self):
        screen = self.getScreen()
        for name in self.widgets:
            screen.deleteWidget(name)
        self.widgets = []

    def _screenSize(self):
        screen = self.getScreen()
        xRes = screen.getXResolution()
        yRes = screen.getYResolution()
        if xRes <= 0:
            xRes = 1024
        if yRes <= 0:
            yRes = 768
        return (xRes, yRes)

    def interfaceScreen(self, iTab = -1):
        if iTab >= 0:
            self.iTab = iTab
        self.iActivePlayer = CyGame().getActivePlayer()
        if self.iActivePlayer < 0:
            return

        screen = self.getScreen()
        if not screen.isActive():
            screen.setRenderInterfaceOnly(True)
            screen.showScreen(PopupStates.POPUPSTATE_IMMEDIATE, False)
            xRes, yRes = self._screenSize()
            screen.setDimensions(0, 0, xRes, yRes)
            screen.showWindowBackground(False)

        self.drawScreen()

    def drawScreen(self):
        screen = self.getScreen()
        self._clearWidgets()
        xRes, yRes = self._screenSize()
        screen.setDimensions(0, 0, xRes, yRes)

        panelMargin = 24
        topPanelHeight = 55
        bottomPanelHeight = 55
        contentTop = topPanelHeight + 18
        contentBottomMargin = bottomPanelHeight + 18
        x = panelMargin
        y = contentTop
        w = xRes - (panelMargin * 2)
        h = yRes - contentTop - contentBottomMargin

        screen.addDDSGFC(self._addWidget(self.BACKGROUND_ID), ArtFileMgr.getInterfaceArtInfo('SCREEN_BG_OPAQUE').getPath(), 0, 0, xRes, yRes, WidgetTypes.WIDGET_GENERAL, -1, -1)
        screen.addPanel(self._addWidget(self.TOP_PANEL_ID), u'', u'', True, False, 0, 0, xRes, topPanelHeight, PanelStyles.PANEL_STYLE_TOPBAR)
        screen.addPanel(self._addWidget(self.BOTTOM_PANEL_ID), u'', u'', True, False, 0, yRes - bottomPanelHeight, xRes, bottomPanelHeight, PanelStyles.PANEL_STYLE_BOTTOMBAR)
        screen.addPanel(self._addWidget(self.MAIN_PANEL_ID), u'', u'', True, True, x, y, w, h, PanelStyles.PANEL_STYLE_MAIN)
        screen.setLabel(self._addWidget(self.HEADER_ID), 'Background', u'<font=4>INDUSTRY ADVISOR</font>', CvUtil.FONT_CENTER_JUSTIFY, xRes / 2, 15, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
        screen.setText(self._addWidget(self.EXIT_ID), 'Background', localText.getText('TXT_KEY_PEDIA_SCREEN_EXIT', ()).upper(), CvUtil.FONT_RIGHT_JUSTIFY, xRes - 20, yRes - 40, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_CLOSE_SCREEN, -1, -1)

        tabTexts = ('Cities', 'Goods', 'Chains')
        for i in range(3):
            if i == self.iTab:
                colorStart = u'<color=255,255,0>'
                colorEnd = u'</color>'
            else:
                colorStart = u''
                colorEnd = u''
            screen.setText(self._addWidget(self.TAB_IDS[i]), 'Background', colorStart + u'<font=3>' + tabTexts[i] + u'</font>' + colorEnd, CvUtil.FONT_LEFT_JUSTIFY, x + 20 + (i * 170), y - 22, -0.1, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, i, -1)

        if self.iTab == 0:
            self.drawCitiesTab(x + 16, y + 16, w - 32, h - 32)
        elif self.iTab == 1:
            self.drawGoodsTab(x + 16, y + 16, w - 32, h - 32)
        else:
            self.drawChainsTab(x + 16, y + 16, w - 32, h - 32)

    def _ownedBFCPlots(self, city):
        plots = []
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                if abs(dx) == 2 and abs(dy) == 2:
                    continue
                plot = CyMap().plot(city.getX() + dx, city.getY() + dy)
                if plot is None:
                    continue
                try:
                    if plot.isNone():
                        continue
                except:
                    pass
                if plot.getOwner() == city.getOwner():
                    plots.append(plot)
        return plots

    def _bonusChars(self, bonuses):
        chars = u''
        for eBonus in bonuses:
            if eBonus >= 0:
                chars += u'%c' % gc.getBonusInfo(eBonus).getChar()
        if chars:
            return chars
        return u'-'

    def _nameList(self, infoGetter, items):
        names = []
        for item in items:
            if item >= 0:
                names.append(infoGetter(item).getDescription())
        if not names:
            return u'-'
        return u', '.join(names)

    def _plotHasConnectedRawBonus(self, plot, eBonus, eTeam):
        if eBonus < 0:
            return False
        if plot.getBonusType(eTeam) != eBonus:
            return False
        if plot.getImprovementType() < 0:
            return False
        try:
            return plot.isBonusNetwork(eTeam)
        except:
            return True

    def _cityRawBonuses(self, city):
        eTeam = gc.getPlayer(city.getOwner()).getTeam()
        bonuses = []
        for plot in self._ownedBFCPlots(city):
            eBonus = plot.getBonusType(eTeam)
            if eBonus >= 0 and eBonus not in bonuses:
                bonuses.append(eBonus)
        return bonuses

    def _cityHasLocalConnectedBonus(self, city, rawBonusTypes):
        eTeam = gc.getPlayer(city.getOwner()).getTeam()
        for plot in self._ownedBFCPlots(city):
            for raw in rawBonusTypes:
                eBonus = self._infoType(raw)
                if self._plotHasConnectedRawBonus(plot, eBonus, eTeam):
                    return True
        return False

    def _cityHasProcessing(self, city, buildingType):
        eBuilding = self._infoType(buildingType)
        return eBuilding >= 0 and city.getNumBuilding(eBuilding) > 0

    def _activeProcessingChains(self, city):
        active = []
        for buildingType, raws, synthetic in PROCESSING_CHAINS:
            if self._cityHasProcessing(city, buildingType) and self._cityHasLocalConnectedBonus(city, raws):
                active.append((buildingType, raws, synthetic))
        return active

    def _activeGoods(self, city):
        goods = []
        for buildingType, raws, synthetic in self._activeProcessingChains(city):
            eBonus = self._infoType(synthetic)
            if eBonus >= 0 and eBonus not in goods:
                goods.append(eBonus)
        return goods

    def _eligibleProcessingNotBuilt(self, city):
        eligible = []
        for buildingType, raws, synthetic in PROCESSING_CHAINS:
            if not self._cityHasProcessing(city, buildingType) and self._cityHasLocalConnectedBonus(city, raws):
                eBuilding = self._infoType(buildingType)
                if eBuilding >= 0:
                    eligible.append(eBuilding)
        return eligible

    def _coreIndustriesPresent(self, city):
        present = []
        for buildingType in CORE_BUILDINGS:
            eBuilding = self._infoType(buildingType)
            if eBuilding >= 0 and city.getNumBuilding(eBuilding) > 0:
                present.append(eBuilding)
        return present

    def _activeCompositeData(self, city):
        active = []
        inactive = []
        for buildingType, goods in COMPOSITES:
            eBuilding = self._infoType(buildingType)
            if eBuilding < 0 or city.getNumBuilding(eBuilding) <= 0:
                continue
            missing = []
            for goodType in goods:
                eBonus = self._infoType(goodType)
                if eBonus >= 0 and not city.hasBonus(eBonus):
                    missing.append(eBonus)
            if missing:
                inactive.append((eBuilding, missing))
            else:
                active.append(eBuilding)
        return active, inactive

    def _goodsEnabledBy(self, eBonus):
        enabled = []
        for buildingType, goods in COMPOSITES:
            for goodType in goods:
                if self._infoType(goodType) == eBonus:
                    eBuilding = self._infoType(buildingType)
                    if eBuilding >= 0 and eBuilding not in enabled:
                        enabled.append(eBuilding)
        return enabled

    def _corpsUsing(self, eBonus):
        corps = []
        for corpType, goods in CORPORATIONS:
            for goodType in goods:
                if self._infoType(goodType) == eBonus:
                    eCorp = self._infoType(corpType)
                    if eCorp >= 0 and eCorp not in corps:
                        corps.append(eCorp)
        return corps

    def drawCitiesTab(self, x, y, w, h):
        screen = self.getScreen()
        table = self._addWidget(self.TABLE_ID)
        screen.addTableControlGFC(table, 8, x, y, w, h, True, False, 24, 24, TableStyles.TABLE_STYLE_STANDARD)
        screen.enableSelect(table, False)
        screen.setStyle(table, 'Table_StandardCiv_Style')
        headers = (
            ('City', int(w * 0.14)),
            ('Owned BFC', int(w * 0.14)),
            ('Core', int(w * 0.14)),
            ('Processing', int(w * 0.14)),
            ('Goods', int(w * 0.10)),
            ('Eligible', int(w * 0.14)),
            ('Composites', int(w * 0.10)),
            ('Inactive / Missing', int(w * 0.20)),
        )
        for i, (label, width) in enumerate(headers):
            screen.setTableColumnHeader(table, i, u'<font=2>%s</font>' % label, width)

        player = gc.getPlayer(self.iActivePlayer)
        (city, iter) = player.firstCity(False)
        row = 0
        while city:
            screen.appendTableRow(table)
            rawBonuses = self._cityRawBonuses(city)
            activeProcessing = self._activeProcessingChains(city)
            activeGoods = self._activeGoods(city)
            eligible = self._eligibleProcessingNotBuilt(city)
            core = self._coreIndustriesPresent(city)
            activeComp, inactiveComp = self._activeCompositeData(city)
            inactiveText = []
            for eBuilding, missing in inactiveComp:
                inactiveText.append(u'%s (%s)' % (gc.getBuildingInfo(eBuilding).getDescription(), self._bonusChars(missing)))

            screen.setTableText(table, 0, row, city.getName(), '', WidgetTypes.WIDGET_ZOOM_CITY, city.getOwner(), city.getID(), CvUtil.FONT_LEFT_JUSTIFY)
            screen.setTableText(table, 1, row, self._bonusChars(rawBonuses), '', WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
            screen.setTableText(table, 2, row, self._nameList(gc.getBuildingInfo, core), '', WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
            screen.setTableText(table, 3, row, self._nameList(gc.getBuildingInfo, [self._infoType(x[0]) for x in activeProcessing]), '', WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
            screen.setTableText(table, 4, row, self._bonusChars(activeGoods), '', WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
            screen.setTableText(table, 5, row, self._nameList(gc.getBuildingInfo, eligible), '', WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
            screen.setTableText(table, 6, row, self._nameList(gc.getBuildingInfo, activeComp), '', WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
            if inactiveText:
                inactiveLabel = u'; '.join(inactiveText)
            else:
                inactiveLabel = u'-'
            screen.setTableText(table, 7, row, inactiveLabel, '', WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
            row += 1
            (city, iter) = player.nextCity(iter, False)

    def drawGoodsTab(self, x, y, w, h):
        screen = self.getScreen()
        table = self._addWidget(self.TABLE_ID)
        screen.addTableControlGFC(table, 5, x, y, w, h, True, False, 24, 24, TableStyles.TABLE_STYLE_STANDARD)
        screen.enableSelect(table, False)
        screen.setStyle(table, 'Table_StandardCiv_Style')
        headers = (
            ('Good', int(w * 0.18)),
            ('Available', int(w * 0.08)),
            ('Produced In', int(w * 0.26)),
            ('Enables', int(w * 0.28)),
            ('Used By', int(w * 0.20)),
        )
        for i, (label, width) in enumerate(headers):
            screen.setTableColumnHeader(table, i, u'<font=2>%s</font>' % label, width)

        player = gc.getPlayer(self.iActivePlayer)
        goods = []
        for buildingType, raws, synthetic in PROCESSING_CHAINS:
            eBonus = self._infoType(synthetic)
            if eBonus >= 0 and eBonus not in goods:
                goods.append(eBonus)
        goods.sort()

        row = 0
        for eBonus in goods:
            screen.appendTableRow(table)
            producedIn = []
            (city, iter) = player.firstCity(False)
            while city:
                if city.hasBonus(eBonus):
                    for buildingType, raws, synthetic in self._activeProcessingChains(city):
                        if self._infoType(synthetic) == eBonus:
                            producedIn.append(city.getName())
                            break
                (city, iter) = player.nextCity(iter, False)
            screen.setTableText(table, 0, row, u'%c %s' % (gc.getBonusInfo(eBonus).getChar(), gc.getBonusInfo(eBonus).getDescription()), '', WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS, eBonus, 1, CvUtil.FONT_LEFT_JUSTIFY)
            screen.setTableInt(table, 1, row, u'%d' % player.getNumAvailableBonuses(eBonus), '', WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
            if producedIn:
                producedInText = u', '.join(producedIn)
            else:
                producedInText = u'-'
            screen.setTableText(table, 2, row, producedInText, '', WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
            screen.setTableText(table, 3, row, self._nameList(gc.getBuildingInfo, self._goodsEnabledBy(eBonus)), '', WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
            screen.setTableText(table, 4, row, self._nameList(gc.getCorporationInfo, self._corpsUsing(eBonus)), '', WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
            row += 1

    def drawChainsTab(self, x, y, w, h):
        screen = self.getScreen()
        table = self._addWidget(self.TABLE_ID)
        screen.addTableControlGFC(table, 5, x, y, w, h, True, False, 24, 24, TableStyles.TABLE_STYLE_STANDARD)
        screen.enableSelect(table, False)
        screen.setStyle(table, 'Table_StandardCiv_Style')
        headers = (
            ('Raw Resource', int(w * 0.18)),
            ('Processor', int(w * 0.20)),
            ('Synthetic Good', int(w * 0.16)),
            ('Composite Industries', int(w * 0.28)),
            ('Corporations', int(w * 0.18)),
        )
        for i, (label, width) in enumerate(headers):
            screen.setTableColumnHeader(table, i, u'<font=2>%s</font>' % label, width)

        row = 0
        for buildingType, raws, synthetic in PROCESSING_CHAINS:
            eBuilding = self._infoType(buildingType)
            eSynthetic = self._infoType(synthetic)
            if eBuilding < 0 or eSynthetic < 0:
                continue
            rawBonuses = []
            for raw in raws:
                eRaw = self._infoType(raw)
                if eRaw >= 0:
                    rawBonuses.append(eRaw)
            enabled = self._goodsEnabledBy(eSynthetic)
            corps = self._corpsUsing(eSynthetic)
            screen.appendTableRow(table)
            screen.setTableText(table, 0, row, self._bonusChars(rawBonuses), '', WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
            screen.setTableText(table, 1, row, gc.getBuildingInfo(eBuilding).getDescription(), '', WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING, eBuilding, 1, CvUtil.FONT_LEFT_JUSTIFY)
            screen.setTableText(table, 2, row, u'%c %s' % (gc.getBonusInfo(eSynthetic).getChar(), gc.getBonusInfo(eSynthetic).getDescription()), '', WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS, eSynthetic, 1, CvUtil.FONT_LEFT_JUSTIFY)
            screen.setTableText(table, 3, row, self._nameList(gc.getBuildingInfo, enabled), '', WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
            screen.setTableText(table, 4, row, self._nameList(gc.getCorporationInfo, corps), '', WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
            row += 1

    def handleInput(self, inputClass):
        if inputClass.getNotifyCode() == NotifyCode.NOTIFY_CLICKED:
            fname = inputClass.getFunctionName()
            if fname == self.TAB_IDS[0]:
                self.iTab = 0
                self.drawScreen()
                return 1
            if fname == self.TAB_IDS[1]:
                self.iTab = 1
                self.drawScreen()
                return 1
            if fname == self.TAB_IDS[2]:
                self.iTab = 2
                self.drawScreen()
                return 1
        return 0

    def update(self, fDelta):
        return 0

    def onClose(self):
        self._clearWidgets()


g_IndustryAdvisor = CvIndustryAdvisor()
