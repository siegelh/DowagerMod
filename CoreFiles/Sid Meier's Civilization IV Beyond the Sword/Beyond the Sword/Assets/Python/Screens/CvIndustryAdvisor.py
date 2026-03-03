from CvPythonExtensions import *
import CvUtil
import ScreenInput
import sys
import CvIndustryFlowData
import CvIndustryFlowRenderer

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

PROCESSING_CHAINS = []
for _kChain in CvIndustryFlowData.getProcessingChains():
    PROCESSING_CHAINS.append((_kChain['building'], _kChain['raws'], _kChain['synthetic']))
PROCESSING_CHAINS = tuple(PROCESSING_CHAINS)

COMPOSITES = []
for _kComposite in CvIndustryFlowData.getCompositeRecipes():
    COMPOSITES.append((_kComposite['building'], _kComposite['goods']))
COMPOSITES = tuple(COMPOSITES)

CORPORATIONS = []
for _kFamily in CvIndustryFlowData.getCorporationFamilies():
    CORPORATIONS.append((_kFamily['corporation'], _kFamily['operating_goods']))
CORPORATIONS = tuple(CORPORATIONS)


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
        self.CHAINS_VIEW_IDS = ('IndustryChainsViewGraph', 'IndustryChainsViewTable')
        self.CHAINS_LEGEND_ID = 'IndustryChainsLegend'
        self.iTab = 0
        self.iChainsView = 0
        self.szFlowFilter = CvIndustryFlowData.FILTER_ALL
        self.iActivePlayer = -1
        self.player = None
        self.team = None
        self.playerCities = []
        self.widgets = []
        self.typeCache = {}
        self.buildingStateCache = {}
        self.bonusStateCache = {}
        self.corporationStateCache = {}
        self.flowRenderer = CvIndustryFlowRenderer.CvIndustryFlowRenderer(self._addWidget)

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

    def _collectCities(self, player):
        cities = []
        (city, iter) = player.firstCity(False)
        while city:
            cities.append(city)
            (city, iter) = player.nextCity(iter, False)
        return cities

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

        self.player = gc.getPlayer(self.iActivePlayer)
        self.team = gc.getTeam(self.player.getTeam())
        self.playerCities = self._collectCities(self.player)
        self.buildingStateCache = {}
        self.bonusStateCache = {}
        self.corporationStateCache = {}

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

    def _buildingSummary(self, eBuilding):
        if self.buildingStateCache.has_key(eBuilding):
            return self.buildingStateCache[eBuilding]

        summary = {'built': 0, 'active': 0, 'can_now': 0, 'visible': 0}
        for city in self.playerCities:
            iBuilt = city.getNumBuilding(eBuilding)
            iActive = city.getNumActiveBuilding(eBuilding)
            if iBuilt > 0:
                summary['built'] += iBuilt
            if iActive > 0:
                summary['active'] += iActive
            if not summary['can_now'] and city.canConstruct(eBuilding, False, False, True):
                summary['can_now'] = 1
            if not summary['visible'] and city.canConstruct(eBuilding, False, True, True):
                summary['visible'] = 1

        self.buildingStateCache[eBuilding] = summary
        return summary

    def _bonusPresence(self, eBonus):
        if self.bonusStateCache.has_key(eBonus):
            return self.bonusStateCache[eBonus]

        data = {'owned': 0, 'connected': 0}
        iWidth = CyMap().getGridWidth()
        iHeight = CyMap().getGridHeight()
        eTeam = self.player.getTeam()
        for iX in range(iWidth):
            for iY in range(iHeight):
                plot = CyMap().plot(iX, iY)
                if plot is None or plot.getOwner() != self.iActivePlayer:
                    continue
                if plot.getBonusType(eTeam) != eBonus:
                    continue
                data['owned'] += 1
                if plot.getImprovementType() >= 0:
                    try:
                        if plot.isBonusNetwork(eTeam):
                            data['connected'] += 1
                    except:
                        data['connected'] += 1

        self.bonusStateCache[eBonus] = data
        return data

    def _stateForRawBonus(self, eBonus):
        iAvailable = self.player.getNumAvailableBonuses(eBonus)
        if iAvailable > 0:
            return {'state': 'active', 'detail': u'Available: %d' % iAvailable}

        kPresence = self._bonusPresence(eBonus)
        if kPresence['owned'] > 0:
            return {'state': 'blocked', 'detail': u'Owned, not connected'}
        return {'state': 'unavailable', 'detail': u'No local supply'}

    def _stateForBuilding(self, eBuilding):
        kSummary = self._buildingSummary(eBuilding)
        if kSummary['active'] > 0:
            return {'state': 'active', 'detail': u'Active in empire'}
        if kSummary['built'] > 0:
            return {'state': 'blocked', 'detail': u'Built but inactive'}
        if kSummary['can_now']:
            return {'state': 'ready', 'detail': u'Can build now'}
        if kSummary['visible']:
            return {'state': 'blocked', 'detail': u'Visible but blocked'}
        return {'state': 'unavailable', 'detail': u'Unavailable'}

    def _stateForSynthetic(self, szSynthetic):
        eBonus = self._infoType(szSynthetic)
        iAvailable = self.player.getNumAvailableBonuses(eBonus)
        if iAvailable > 0:
            return {'state': 'active', 'detail': u'Available: %d' % iAvailable}

        kChain = CvIndustryFlowData.getProcessingChainBySynthetic(szSynthetic)
        if kChain is None:
            return {'state': 'unavailable', 'detail': u'Unavailable'}

        eBuilding = self._infoType(kChain['building'])
        kBuildingState = self._stateForBuilding(eBuilding)
        if kBuildingState['state'] == 'ready':
            return {'state': 'ready', 'detail': u'Can produce now'}
        if kBuildingState['state'] == 'active':
            return {'state': 'blocked', 'detail': u'Produced, not networked'}
        if kBuildingState['state'] == 'blocked':
            return {'state': 'blocked', 'detail': u'Producers blocked'}
        return {'state': 'unavailable', 'detail': u'No active producers'}

    def _familyHasRequiredTechs(self, kFamily):
        eCorp = self._infoType(kFamily['corporation'])
        eTech = gc.getCorporationInfo(eCorp).getTechPrereq()
        if eTech >= 0 and not self.team.isHasTech(eTech):
            return False

        eHQ = self._infoType(kFamily['hq_building'])
        kHQ = gc.getBuildingInfo(eHQ)
        ePrereq = kHQ.getPrereqAndTech()
        if ePrereq >= 0 and not self.team.isHasTech(ePrereq):
            return False
        for i in range(4):
            eExtra = kHQ.getPrereqAndTechs(i)
            if eExtra >= 0 and not self.team.isHasTech(eExtra):
                return False
        return True

    def _familyActiveCompositeCount(self, kFamily):
        iCount = 0
        for szBuilding in kFamily['composites']:
            eBuilding = self._infoType(szBuilding)
            if self._buildingSummary(eBuilding)['active'] > 0:
                iCount += 1
        return iCount

    def _stateForCorporation(self, szCorp):
        if self.corporationStateCache.has_key(szCorp):
            return self.corporationStateCache[szCorp]

        eCorp = self._infoType(szCorp)
        if self.player.getHasCorporationCount(eCorp) > 0:
            kState = {'state': 'active', 'detail': u'Present in empire'}
            self.corporationStateCache[szCorp] = kState
            return kState

        if CyGame().isCorporationFounded(eCorp):
            kState = {'state': 'unavailable', 'detail': u'Founded elsewhere'}
            self.corporationStateCache[szCorp] = kState
            return kState

        kFamily = None
        for kLoopFamily in CvIndustryFlowData.getCorporationFamilies():
            if kLoopFamily['corporation'] == szCorp:
                kFamily = kLoopFamily
                break

        if kFamily is None:
            kState = {'state': 'unavailable', 'detail': u'Unavailable'}
            self.corporationStateCache[szCorp] = kState
            return kState

        bHasTechs = self._familyHasRequiredTechs(kFamily)
        iActive = self._familyActiveCompositeCount(kFamily)
        iMin = kFamily['min_active_composites']
        szProgress = u'%d/%d composites' % (iActive, iMin)

        if bHasTechs and iActive >= iMin:
            kState = {'state': 'ready', 'detail': u'Ready to found'}
        elif bHasTechs or iActive > 0:
            kState = {'state': 'blocked', 'detail': szProgress}
        else:
            kState = {'state': 'unavailable', 'detail': u'No founding progress'}

        self.corporationStateCache[szCorp] = kState
        return kState

    def _bonusBadge(self, szBonus):
        eBonus = self._infoType(szBonus)
        if eBonus < 0:
            return None
        return {
            'button': gc.getBonusInfo(eBonus).getButton(),
            'widgetType': WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS,
            'data1': eBonus,
            'data2': 1,
        }

    def _wrapText(self, szText, iMaxChars, iMaxLines):
        words = szText.split()
        if len(words) == 0:
            return [u'']

        lines = []
        current = u''
        iWord = 0
        while iWord < len(words):
            word = words[iWord]
            if current:
                candidate = current + u' ' + word
            else:
                candidate = word
            if len(candidate) <= iMaxChars:
                current = candidate
                iWord += 1
                continue
            if not current:
                current = word
                iWord += 1
                if iWord < len(words) and len(current) > iMaxChars - 3:
                    current = current[:iMaxChars - 3] + u'...'
                lines.append(current)
                current = u''
                if len(lines) >= iMaxLines:
                    break
                continue
            lines.append(current)
            current = word
            if len(lines) >= iMaxLines - 1:
                break
            iWord += 1

        remaining = iWord < len(words)

        if current:
            if remaining:
                if len(current) > iMaxChars - 3:
                    current = current[:iMaxChars - 3]
                current += u'...'
            lines.append(current)

        if len(lines) > iMaxLines:
            lines = lines[:iMaxLines]
        return lines

    def _renderNodeData(self, kNode):
        kRender = {
            'id': kNode['id'],
            'gridX': kNode['gridX'],
            'gridY': kNode['gridY'],
            'title': u'',
            'titleLines': [],
            'titleFont': 2,
            'subtitle': u'',
            'subtitleAlign': 'left',
            'button': u'',
            'state': 'unavailable',
            'widgetType': WidgetTypes.WIDGET_GENERAL,
            'data1': -1,
            'data2': -1,
            'metaText': u'',
            'metaAlign': 'left',
            'badges': [],
            'sizeClass': 'normal',
        }

        if kNode['type'] == CvIndustryFlowData.NODE_TYPE_RAW or kNode['type'] == CvIndustryFlowData.NODE_TYPE_SYNTHETIC:
            eBonus = self._infoType(kNode['gameType'])
            kBonus = gc.getBonusInfo(eBonus)
            kRender['title'] = u'%c %s' % (kBonus.getChar(), kBonus.getDescription())
            kRender['button'] = kBonus.getButton()
            kRender['widgetType'] = WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS
            kRender['data1'] = eBonus
            kRender['data2'] = 1
            if kNode['type'] == CvIndustryFlowData.NODE_TYPE_RAW:
                kState = self._stateForRawBonus(eBonus)
            else:
                kState = self._stateForSynthetic(kNode['gameType'])
        elif kNode['type'] == CvIndustryFlowData.NODE_TYPE_PROCESSOR or kNode['type'] == CvIndustryFlowData.NODE_TYPE_COMPOSITE:
            eBuilding = self._infoType(kNode['gameType'])
            kBuilding = gc.getBuildingInfo(eBuilding)
            kRender['title'] = kBuilding.getDescription()
            kRender['button'] = kBuilding.getButton()
            kRender['widgetType'] = WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING
            kRender['data1'] = eBuilding
            kRender['data2'] = 1
            kState = self._stateForBuilding(eBuilding)
            if kNode['type'] == CvIndustryFlowData.NODE_TYPE_COMPOSITE:
                kRender['sizeClass'] = 'composite'
                kRender['titleFont'] = 1
                kRender['metaAlign'] = 'center'
                kRecipe = CvIndustryFlowData.getCompositeRecipe(kNode['gameType'])
                if kRecipe is not None:
                    kRender['metaText'] = u'Inputs'
                    for szGood in kRecipe['goods']:
                        kBadge = self._bonusBadge(szGood)
                        if kBadge is not None:
                            kRender['badges'].append(kBadge)
        else:
            eCorp = self._infoType(kNode['gameType'])
            kCorp = gc.getCorporationInfo(eCorp)
            kRender['title'] = kCorp.getDescription()
            kRender['button'] = kCorp.getButton()
            kRender['widgetType'] = WidgetTypes.WIDGET_PEDIA_JUMP_TO_CORPORATION
            kRender['data1'] = eCorp
            kRender['data2'] = 1
            kRender['sizeClass'] = 'corporation'
            kRender['titleFont'] = 1
            kRender['subtitleAlign'] = 'center'
            kRender['metaAlign'] = 'center'
            kState = self._stateForCorporation(kNode['gameType'])
            kFamily = CvIndustryFlowData.getCorporationFamily(kNode['filterId'])
            if kFamily is not None:
                kRender['metaText'] = u'Found: %d active composites' % kFamily['min_active_composites']
                for szGood in kFamily['operating_goods']:
                    kBadge = self._bonusBadge(szGood)
                    if kBadge is not None:
                        kRender['badges'].append(kBadge)

        kRender['state'] = kState['state']
        kRender['subtitle'] = kState['detail']
        if kRender['sizeClass'] == 'corporation':
            kRender['titleLines'] = [kRender['title']]
        elif kRender['sizeClass'] == 'composite':
            kRender['titleLines'] = self._wrapText(kRender['title'], 18, 2)
        else:
            kRender['titleLines'] = self._wrapText(kRender['title'], 22, 2)
        return kRender

    def _drawChainsControls(self, x, y, w):
        screen = self.getScreen()
        labels = ('Graph', 'Table')
        for i in range(2):
            if i == self.iChainsView:
                szStart = u'<color=255,255,0>'
                szEnd = u'</color>'
            else:
                szStart = u''
                szEnd = u''
            screen.setText(self._addWidget(self.CHAINS_VIEW_IDS[i]), 'Background', szStart + u'<font=2>%s</font>' % labels[i] + szEnd, CvUtil.FONT_LEFT_JUSTIFY, x + (i * 88), y, -0.1, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, i, -1)

        self.szFlowFilter = CvIndustryFlowData.FILTER_ALL
        screen.setText(self._addWidget('IndustryChainsAllChainsLabel'), 'Background', u'<color=255,255,0><font=2>All Chains</font></color>', CvUtil.FONT_LEFT_JUSTIFY, x + 190, y, -0.1, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

    def _drawChainsLegend(self, x, y, w):
        screen = self.getScreen()
        szLegend = (
            u'<font=2>'
            u'<color=85,150,87>Active</color>   '
            u'<color=104,158,165>Ready</color>   '
            u'<color=100,104,160>Blocked</color>   '
            u'<color=206,65,69>Unavailable</color>'
            u'   Upper corp paths found, lower paths sustain.'
            u'</font>'
        )
        screen.setText(self._addWidget(self.CHAINS_LEGEND_ID), 'Background', szLegend, CvUtil.FONT_LEFT_JUSTIFY, x, y, -0.1, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

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

        row = 0
        for city in self.playerCities:
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
            for city in self.playerCities:
                if city.hasBonus(eBonus):
                    for buildingType, raws, synthetic in self._activeProcessingChains(city):
                        if self._infoType(synthetic) == eBonus:
                            producedIn.append(city.getName())
                            break
            screen.setTableText(table, 0, row, u'%c %s' % (gc.getBonusInfo(eBonus).getChar(), gc.getBonusInfo(eBonus).getDescription()), '', WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS, eBonus, 1, CvUtil.FONT_LEFT_JUSTIFY)
            screen.setTableInt(table, 1, row, u'%d' % self.player.getNumAvailableBonuses(eBonus), '', WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
            if producedIn:
                producedInText = u', '.join(producedIn)
            else:
                producedInText = u'-'
            screen.setTableText(table, 2, row, producedInText, '', WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
            screen.setTableText(table, 3, row, self._nameList(gc.getBuildingInfo, self._goodsEnabledBy(eBonus)), '', WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
            screen.setTableText(table, 4, row, self._nameList(gc.getCorporationInfo, self._corpsUsing(eBonus)), '', WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
            row += 1

    def drawChainsTab(self, x, y, w, h):
        self._drawChainsControls(x, y, w)
        if self.iChainsView == 0:
            self._drawChainsLegend(x, y + 20, w)
            self.drawChainsGraph(x, y + 44, w, h - 44)
        else:
            self.drawChainsTable(x, y + 24, w, h - 24)

    def drawChainsGraph(self, x, y, w, h):
        screen = self.getScreen()
        try:
            kGraph = CvIndustryFlowData.buildFlowGraph(self.szFlowFilter)
            renderNodes = []
            for kNode in kGraph['nodes']:
                renderNodes.append(self._renderNodeData(kNode))
            renderSections = kGraph.get('sections', [])
            self.flowRenderer.render(screen, x, y, w, h, 'IndustryFlowGraph', renderNodes, kGraph['edges'], renderSections)
        except:
            err = sys.exc_info()[1]
            CvUtil.pyPrint('Industry graph render failed: %s' % err)
            panelId = self._addWidget('IndustryFlowGraphErrorPanel')
            labelId = self._addWidget('IndustryFlowGraphErrorLabel')
            screen.addPanel(panelId, u'', u'', True, True, x, y, w, h, PanelStyles.PANEL_STYLE_MAIN)
            screen.setText(labelId, 'Background', u'<font=2>Graph error: %s</font>' % unicode(err), CvUtil.FONT_LEFT_JUSTIFY, x + 12, y + 12, -0.1, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

    def drawChainsTable(self, x, y, w, h):
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

        allowedSynthetic = {}
        allowedComposite = {}
        allowedCorp = {}
        if self.szFlowFilter != CvIndustryFlowData.FILTER_ALL:
            kFamily = CvIndustryFlowData.getCorporationFamily(self.szFlowFilter)
            if kFamily is not None:
                for szGood in CvIndustryFlowData.getFamilySyntheticGoods(self.szFlowFilter):
                    allowedSynthetic[szGood] = 1
                for szBuilding in kFamily['composites']:
                    allowedComposite[szBuilding] = 1
                allowedCorp[kFamily['corporation']] = 1

        row = 0
        for buildingType, raws, synthetic in PROCESSING_CHAINS:
            if self.szFlowFilter != CvIndustryFlowData.FILTER_ALL and not allowedSynthetic.has_key(synthetic):
                continue

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
            if self.szFlowFilter != CvIndustryFlowData.FILTER_ALL:
                enabled = [eLoop for eLoop in enabled if allowedComposite.has_key(gc.getBuildingInfo(eLoop).getType())]
                corps = [eLoop for eLoop in corps if allowedCorp.has_key(gc.getCorporationInfo(eLoop).getType())]

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
            if fname == self.CHAINS_VIEW_IDS[0]:
                self.iChainsView = 0
                self.drawScreen()
                return 1
            if fname == self.CHAINS_VIEW_IDS[1]:
                self.iChainsView = 1
                self.drawScreen()
                return 1
        return 0

    def update(self, fDelta):
        return 0

    def onClose(self):
        self._clearWidgets()


g_IndustryAdvisor = CvIndustryAdvisor()
