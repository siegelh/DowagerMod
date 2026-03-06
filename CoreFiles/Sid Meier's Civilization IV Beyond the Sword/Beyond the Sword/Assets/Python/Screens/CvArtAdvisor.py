from CvPythonExtensions import *
import CvUtil
import CvArtMasterpieceData
import CvArtMasterpieceSystem


gc = CyGlobalContext()
ArtFileMgr = CyArtFileMgr()
localText = CyTranslator()

ART_ADVISOR_SCREEN = 5000
BASE_HAPPINESS_CAP = 10

ERA_LABELS = {
    "ANTIQUITY": "Antiquity",
    "MEDIEVAL": "Medieval",
    "RENAISSANCE": "Renaissance",
    "INDUSTRIAL": "Industrial",
    "MODERN": "Modern",
    "CONTEMPORARY": "Contemporary",
}

TYPE_LABELS = {
    "PAINTING": "Painting",
    "SCULPTURE": "Sculpture",
}


def getArtAdvisor():
    global g_ArtAdvisor
    return g_ArtAdvisor


class CvArtAdvisor:
    def __init__(self):
        self.SCREEN_NAME = "ArtAdvisor"
        self.BACKGROUND_ID = "ArtAdvisorBackground"
        self.TOP_PANEL_ID = "ArtAdvisorTopPanel"
        self.BOTTOM_PANEL_ID = "ArtAdvisorBottomPanel"
        self.MAIN_PANEL_ID = "ArtAdvisorMainPanel"
        self.HEADER_ID = "ArtAdvisorHeader"
        self.EXIT_ID = "ArtAdvisorExit"
        self.SUMMARY_PRIMARY_ID = "ArtAdvisorSummaryPrimary"
        self.SUMMARY_SECONDARY_ID = "ArtAdvisorSummarySecondary"
        self.SUMMARY_HINT_ID = "ArtAdvisorSummaryHint"
        self.SCROLL_ID = "ArtAdvisorScroll"
        self.CIV_BUTTON_PREFIX = "ArtAdvisorCivButton"
        self.widgets = []
        self.iActivePlayer = -1
        self.iViewPlayer = -1

    def getScreen(self):
        return CyGInterfaceScreen(self.SCREEN_NAME, ART_ADVISOR_SCREEN)

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

    def _pieceTextKey(self, pieceType):
        return "TXT_KEY_" + pieceType

    def _pieceName(self, pieceType):
        szKey = self._pieceTextKey(pieceType)
        szName = localText.getText(szKey, ())
        if szName == szKey:
            return pieceType
        return szName

    def _eraLabel(self, szEra):
        if ERA_LABELS.has_key(szEra):
            return ERA_LABELS[szEra]
        return szEra.replace("_", " ").title()

    def _typeLabel(self, szType):
        if TYPE_LABELS.has_key(szType):
            return TYPE_LABELS[szType]
        return szType.replace("_", " ").title()

    def _eraIndex(self, szEra):
        try:
            return CvArtMasterpieceData.ART_ERA_ORDER.index(szEra)
        except:
            return len(CvArtMasterpieceData.ART_ERA_ORDER)

    def _trimLabel(self, szLabel, iMaxChars):
        if len(szLabel) <= iMaxChars:
            return szLabel
        return szLabel[:iMaxChars - 3] + "..."

    def _isGalleryVisible(self, iPlayer):
        if iPlayer < 0 or iPlayer >= gc.getMAX_PLAYERS():
            return False

        player = gc.getPlayer(iPlayer)
        if not player.isAlive():
            return False

        try:
            if player.isBarbarian() or player.isMinorCiv():
                return False
        except:
            pass

        if iPlayer == self.iActivePlayer:
            return True

        activePlayer = gc.getPlayer(self.iActivePlayer)
        return gc.getTeam(activePlayer.getTeam()).isHasMet(player.getTeam())

    def _visibleGalleryPlayers(self):
        players = []
        if self.iActivePlayer >= 0 and self._isGalleryVisible(self.iActivePlayer):
            players.append(self.iActivePlayer)

        extras = []
        for iPlayer in range(gc.getMAX_PLAYERS()):
            if iPlayer == self.iActivePlayer:
                continue
            if not self._isGalleryVisible(iPlayer):
                continue
            player = gc.getPlayer(iPlayer)
            extras.append((player.getCivilizationShortDescription(0), iPlayer))

        extras.sort()
        for row in extras:
            players.append(row[1])
        return players

    def _ensureViewPlayer(self):
        if not self._isGalleryVisible(self.iViewPlayer):
            self.iViewPlayer = self.iActivePlayer

    def _playerButtonLabel(self, iPlayer):
        player = gc.getPlayer(iPlayer)
        return self._trimLabel(player.getCivilizationShortDescription(0), 18)

    def _playerOwnedCount(self, iPlayer):
        return len(self._collectOwnedEntries(iPlayer))

    def _playerGalleryTitle(self, iPlayer):
        player = gc.getPlayer(iPlayer)
        leaderName = gc.getLeaderHeadInfo(player.getLeaderType()).getDescription()
        civName = player.getCivilizationShortDescription(0)
        return u"%s - %s" % (civName, leaderName)

    def _galleryHint(self):
        if self.iViewPlayer == self.iActivePlayer:
            return u"<font=2>Great Artists add globally unique works to your Art Gallery. You can also browse the galleries of civilizations you have met.</font>"
        return u"<font=2>You have met this civilization, so its public Art Gallery is visible here. Bonus totals shown below are for that civilization.</font>"

    def _collectOwnedEntries(self, iPlayer):
        ownedMap = CvArtMasterpieceSystem.getOwnedPieces(iPlayer)
        keyed = []

        for row in CvArtMasterpieceData.ART_MASTERPIECES:
            pieceType = row[0]
            if not ownedMap.has_key(pieceType):
                continue

            entry = {
                "pieceType": pieceType,
                "era": row[1],
                "artType": row[2],
                "button": row[3],
                "gallery": row[4],
                "name": self._pieceName(pieceType),
            }
            keyed.append((self._eraIndex(entry["era"]), self._typeLabel(entry["artType"]), entry["name"], entry))

        keyed.sort()
        return [row[3] for row in keyed]

    def _countOwnedCollections(self, entries):
        eraCounts = {}
        typeCounts = {}

        for entry in entries:
            eraCounts[entry["era"]] = eraCounts.get(entry["era"], 0) + 1
            typeCounts[entry["artType"]] = typeCounts.get(entry["artType"], 0) + 1

        return len(entries), eraCounts, typeCounts

    def _bonusBreakdown(self, eraCounts, typeCounts):
        iEraBonus = 0
        iTypeBonus = 0

        for szEra in eraCounts.keys():
            if eraCounts[szEra] >= 3:
                iEraBonus += 1

        for szType in typeCounts.keys():
            if typeCounts[szType] >= 4:
                iTypeBonus += 1

        iSetTotal = iEraBonus + iTypeBonus
        if iSetTotal > 8:
            iSetTotal = 8

        return iSetTotal, iEraBonus, iTypeBonus

    def _cardColor(self, iEraCount, iTypeCount):
        if iEraCount >= 3 and iTypeCount >= 4:
            return (112, 150, 92)
        if iEraCount >= 3 or iTypeCount >= 4:
            return (112, 136, 92)
        return (92, 92, 104)

    def _wrapTitle(self, szTitle, iMaxChars):
        if len(szTitle) <= iMaxChars:
            return [szTitle]

        words = szTitle.split(" ")
        if len(words) <= 1:
            return [szTitle[:iMaxChars], szTitle[iMaxChars:(iMaxChars * 2)]]

        lines = []
        current = ""
        for word in words:
            if current == "":
                current = word
            elif len(current) + 1 + len(word) <= iMaxChars:
                current += " " + word
            else:
                lines.append(current)
                current = word
                if len(lines) == 2:
                    break

        if len(lines) < 2 and current != "":
            lines.append(current)
        if len(lines) == 0:
            lines = [szTitle[:iMaxChars]]
        if len(lines) == 1 and len(lines[0]) > iMaxChars:
            lines = [lines[0][:iMaxChars], lines[0][iMaxChars:]]
        if len(lines) > 2:
            lines = lines[:2]
        if len(lines) == 2 and len(lines[1]) > iMaxChars:
            lines[1] = lines[1][:iMaxChars - 3] + "..."
        return lines

    def interfaceScreen(self):
        self.iActivePlayer = CyGame().getActivePlayer()
        if self.iActivePlayer < 0:
            return

        if self.iViewPlayer < 0:
            self.iViewPlayer = self.iActivePlayer
        self._ensureViewPlayer()

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
        self._ensureViewPlayer()

        xRes, yRes = self._screenSize()
        screen.setDimensions(0, 0, xRes, yRes)

        visiblePlayers = self._visibleGalleryPlayers()
        entries = self._collectOwnedEntries(self.iViewPlayer)
        iOwnedTotal, eraCounts, typeCounts = self._countOwnedCollections(entries)
        iSetTotal, iEraBonus, iTypeBonus = self._bonusBreakdown(eraCounts, typeCounts)
        iBaseBonus = iOwnedTotal
        if iBaseBonus > BASE_HAPPINESS_CAP:
            iBaseBonus = BASE_HAPPINESS_CAP
        iTotalHappiness = iBaseBonus + iSetTotal

        panelMargin = 24
        topPanelHeight = 55
        bottomPanelHeight = 55
        contentTop = topPanelHeight + 18
        contentBottomMargin = bottomPanelHeight + 18
        x = panelMargin
        y = contentTop
        w = xRes - (panelMargin * 2)
        h = yRes - contentTop - contentBottomMargin

        screen.addDDSGFC(self._addWidget(self.BACKGROUND_ID), ArtFileMgr.getInterfaceArtInfo("SCREEN_BG_OPAQUE").getPath(), 0, 0, xRes, yRes, WidgetTypes.WIDGET_GENERAL, -1, -1)
        screen.addPanel(self._addWidget(self.TOP_PANEL_ID), u"", u"", True, False, 0, 0, xRes, topPanelHeight, PanelStyles.PANEL_STYLE_TOPBAR)
        screen.addPanel(self._addWidget(self.BOTTOM_PANEL_ID), u"", u"", True, False, 0, yRes - bottomPanelHeight, xRes, bottomPanelHeight, PanelStyles.PANEL_STYLE_BOTTOMBAR)
        screen.addPanel(self._addWidget(self.MAIN_PANEL_ID), u"", u"", True, True, x, y, w, h, PanelStyles.PANEL_STYLE_MAIN)
        screen.setLabel(self._addWidget(self.HEADER_ID), "Background", u"<font=4>ART GALLERY</font>", CvUtil.FONT_CENTER_JUSTIFY, xRes / 2, 15, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
        screen.setText(self._addWidget(self.EXIT_ID), "Background", localText.getText("TXT_KEY_PEDIA_SCREEN_EXIT", ()).upper(), CvUtil.FONT_RIGHT_JUSTIFY, xRes - 20, yRes - 40, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_CLOSE_SCREEN, -1, -1)

        iInnerX = x + 20
        iTopY = y + 14
        iSelectorBottom = self._drawPlayerSelector(screen, visiblePlayers, iInnerX, iTopY, w - 40)

        szPrimary = u"<font=3><color=255,220,120>%s</color></font>" % self._playerGalleryTitle(self.iViewPlayer)
        szSecondary = u"<font=2>Art Happiness: +%d   Distinct works: %d   Base collection: +%d   Era sets: +%d   Type sets: +%d</font>" % (iTotalHappiness, iOwnedTotal, iBaseBonus, iEraBonus, iTypeBonus)
        szHint = self._galleryHint()

        screen.setLabel(self._addWidget(self.SUMMARY_PRIMARY_ID), "Background", szPrimary, CvUtil.FONT_LEFT_JUSTIFY, iInnerX, iSelectorBottom + 6, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
        screen.setLabel(self._addWidget(self.SUMMARY_SECONDARY_ID), "Background", szSecondary, CvUtil.FONT_LEFT_JUSTIFY, iInnerX, iSelectorBottom + 34, -0.1, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
        screen.setLabel(self._addWidget(self.SUMMARY_HINT_ID), "Background", szHint, CvUtil.FONT_LEFT_JUSTIFY, iInnerX, iSelectorBottom + 58, -0.1, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

        galleryY = iSelectorBottom + 92
        self._drawCollectionGallery(screen, entries, x + 16, galleryY, w - 32, h - (galleryY - y) - 14, eraCounts, typeCounts, iOwnedTotal)

    def _drawPlayerSelector(self, screen, visiblePlayers, x, y, w):
        headerId = self._addWidget("ArtAdvisorGallerySelectorHeader")
        screen.setLabel(headerId, "Background", u"<font=2><color=255,220,130>Galleries of Met Civilizations</color></font>", CvUtil.FONT_LEFT_JUSTIFY, x, y, -0.1, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

        if len(visiblePlayers) == 0:
            return y + 22

        iCellW = 180
        iRowH = 26
        iButtonsPerRow = w / iCellW
        if iButtonsPerRow < 1:
            iButtonsPerRow = 1
        if iButtonsPerRow > 4:
            iButtonsPerRow = 4

        iBaseY = y + 24
        for iIndex in range(len(visiblePlayers)):
            iPlayer = visiblePlayers[iIndex]
            iCol = iIndex % iButtonsPerRow
            iRow = iIndex / iButtonsPerRow
            iButtonX = x + (iCol * iCellW)
            iButtonY = iBaseY + (iRow * iRowH)

            if iPlayer == self.iViewPlayer:
                szColorStart = u"<color=255,220,120>"
            elif iPlayer == self.iActivePlayer:
                szColorStart = u"<color=150,255,150>"
            else:
                szColorStart = u"<color=220,220,220>"
            szLabel = szColorStart + u"<font=2>%s (%d)</font></color>" % (self._playerButtonLabel(iPlayer), self._playerOwnedCount(iPlayer))
            buttonId = self._addWidget(self.CIV_BUTTON_PREFIX + str(iPlayer))
            screen.setText(buttonId, "Background", szLabel, CvUtil.FONT_LEFT_JUSTIFY, iButtonX, iButtonY, -0.1, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, iPlayer, -1)
            screen.setActivation(buttonId, ActivationTypes.ACTIVATE_NORMAL)

        iRows = (len(visiblePlayers) + iButtonsPerRow - 1) / iButtonsPerRow
        return iBaseY + (iRows * iRowH)

    def _drawCollectionGallery(self, screen, entries, x, y, w, h, eraCounts, typeCounts, iOwnedTotal):
        scrollId = self._addWidget(self.SCROLL_ID)
        screen.addScrollPanel(scrollId, u"", x, y, w, h, PanelStyles.PANEL_STYLE_EXTERNAL)
        screen.setActivation(scrollId, ActivationTypes.ACTIVATE_NORMAL)

        if len(entries) == 0:
            emptyId = self._addWidget("ArtAdvisorEmpty")
            emptyId2 = self._addWidget("ArtAdvisorEmptyHint")
            if self.iViewPlayer == self.iActivePlayer:
                szEmptyHint = u"Use a Great Artist to Curate Masterpiece and begin your gallery."
            else:
                szEmptyHint = u"This civilization has not curated any masterpieces yet."
            screen.setTextAt(emptyId, scrollId, u"<font=3>No masterpieces in this gallery yet.</font>", CvUtil.FONT_LEFT_JUSTIFY, 24, 24, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
            screen.setTextAt(emptyId2, scrollId, u"<font=2>%s</font>" % szEmptyHint, CvUtil.FONT_LEFT_JUSTIFY, 24, 54, -0.1, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
            screen.setViewMin(scrollId, w, h)
            return

        iInnerMargin = 18
        iGapX = 20
        iGapY = 24
        iMinCardW = 280
        iUsableW = w - (iInnerMargin * 2)
        iCardsPerRow = iUsableW / (iMinCardW + iGapX)
        if iCardsPerRow < 1:
            iCardsPerRow = 1
        if iCardsPerRow > 3:
            iCardsPerRow = 3

        iCardW = (iUsableW - ((iCardsPerRow - 1) * iGapX)) / iCardsPerRow
        if iCardW < 260:
            iCardW = 260
        iImageW = iCardW - 20
        iImageH = (iImageW * 260) / 420
        iCardH = iImageH + 116

        iY = 14
        iIndex = 0

        for szEra in CvArtMasterpieceData.ART_ERA_ORDER:
            eraEntries = []
            for entry in entries:
                if entry["era"] == szEra:
                    eraEntries.append(entry)

            if len(eraEntries) == 0:
                continue

            headerId = self._addWidget("ArtAdvisorEraHeader%d" % iIndex)
            screen.setTextAt(headerId, scrollId, u"<font=3><color=255,220,130>%s</color></font>" % self._eraLabel(szEra), CvUtil.FONT_LEFT_JUSTIFY, iInnerMargin, iY, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
            iY += 24

            iEraCount = eraCounts.get(szEra, 0)
            if iEraCount >= 3:
                szEraSummary = u"<font=2><color=120,255,120>%d works   Era set active: +1 Happiness</color></font>" % iEraCount
            else:
                szEraSummary = u"<font=2>%d works   Era set progress: %d / 3</font>" % (iEraCount, iEraCount)
            summaryId = self._addWidget("ArtAdvisorEraSummary%d" % iIndex)
            screen.setTextAt(summaryId, scrollId, szEraSummary, CvUtil.FONT_LEFT_JUSTIFY, iInnerMargin, iY, -0.1, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
            iY += 24

            iRows = (len(eraEntries) + iCardsPerRow - 1) / iCardsPerRow
            iEntryInEra = 0
            iRowBaseY = iY

            for entry in eraEntries:
                iCol = iEntryInEra % iCardsPerRow
                iRow = iEntryInEra / iCardsPerRow
                iCardX = iInnerMargin + (iCol * (iCardW + iGapX))
                iCardY = iRowBaseY + (iRow * (iCardH + iGapY))
                self._drawCollectionCard(screen, scrollId, iIndex, entry, iCardX, iCardY, iCardW, iCardH, eraCounts, typeCounts, iOwnedTotal)
                iIndex += 1
                iEntryInEra += 1

            iY = iRowBaseY + (iRows * (iCardH + iGapY)) + 6

        screen.setViewMin(scrollId, w, max(h, iY + 10))

    def _drawCollectionCard(self, screen, scrollId, iIndex, entry, x, y, w, h, eraCounts, typeCounts, iOwnedTotal):
        panelId = self._addWidget("ArtAdvisorCardPanel%d" % iIndex)
        screen.attachPanelAt(scrollId, panelId, u"", u"", True, False, PanelStyles.PANEL_STYLE_TECH, x, y, w, h, WidgetTypes.WIDGET_GENERAL, -1, -1)
        screen.setActivation(panelId, ActivationTypes.ACTIVATE_MIMICPARENTFOCUS)

        iEraCount = eraCounts.get(entry["era"], 0)
        iTypeCount = typeCounts.get(entry["artType"], 0)
        iR, iG, iB = self._cardColor(iEraCount, iTypeCount)
        screen.setPanelColor(panelId, iR, iG, iB)

        iImageX = 10
        iImageY = 10
        iImageW = w - 20
        iImageH = (iImageW * 260) / 420

        imageId = self._addWidget("ArtAdvisorCardImage%d" % iIndex)
        screen.addDDSGFCAt(imageId, panelId, entry["gallery"], iImageX, iImageY, iImageW, iImageH, WidgetTypes.WIDGET_GENERAL, -1, -1, False)

        iTextY = iImageY + iImageH + 8
        titleLines = self._wrapTitle(entry["name"], 28)
        iTitleX = 12

        for iLine in range(len(titleLines)):
            titleId = self._addWidget("ArtAdvisorCardTitle%d_%d" % (iIndex, iLine))
            screen.setTextAt(titleId, panelId, u"<font=2>%s</font>" % titleLines[iLine], CvUtil.FONT_LEFT_JUSTIFY, iTitleX, iTextY, -0.1, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
            iTextY += 16

        typeId = self._addWidget("ArtAdvisorCardType%d" % iIndex)
        screen.setTextAt(typeId, panelId, u"<font=1><color=255,220,120>%s</color></font>" % self._typeLabel(entry["artType"]), CvUtil.FONT_LEFT_JUSTIFY, iTitleX, iTextY + 1, -0.1, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
        iTextY += 18

        if iOwnedTotal <= BASE_HAPPINESS_CAP:
            szBaseLine = u"<font=1>Base collection: +1 Happiness</font>"
        else:
            szBaseLine = u"<font=1>Base collection: part of the +10 cap</font>"

        if iEraCount >= 3:
            szEraLine = u"<font=1><color=120,255,120>Era set: Active (+1 Happiness)</color></font>"
        else:
            szEraLine = u"<font=1>Era set: %d / 3</font>" % iEraCount

        if iTypeCount >= 4:
            szTypeLine = u"<font=1><color=120,255,120>Type set: Active (+1 Happiness)</color></font>"
        else:
            szTypeLine = u"<font=1>Type set: %d / 4</font>" % iTypeCount

        baseId = self._addWidget("ArtAdvisorCardBase%d" % iIndex)
        eraId = self._addWidget("ArtAdvisorCardEra%d" % iIndex)
        typeLineId = self._addWidget("ArtAdvisorCardTypeLine%d" % iIndex)
        screen.setTextAt(baseId, panelId, szBaseLine, CvUtil.FONT_LEFT_JUSTIFY, iTitleX, iTextY + 2, -0.1, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
        screen.setTextAt(eraId, panelId, szEraLine, CvUtil.FONT_LEFT_JUSTIFY, iTitleX, iTextY + 18, -0.1, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
        screen.setTextAt(typeLineId, panelId, szTypeLine, CvUtil.FONT_LEFT_JUSTIFY, iTitleX, iTextY + 34, -0.1, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

    def handleInput(self, inputClass):
        if inputClass.getNotifyCode() == NotifyCode.NOTIFY_CLICKED:
            fname = inputClass.getFunctionName()
            if fname.startswith(self.CIV_BUTTON_PREFIX):
                try:
                    iPlayer = int(fname[len(self.CIV_BUTTON_PREFIX):])
                except:
                    return 0
                if self._isGalleryVisible(iPlayer):
                    self.iViewPlayer = iPlayer
                    self.drawScreen()
                    return 1
            iPlayer = inputClass.getData1()
            if iPlayer >= 0 and iPlayer < gc.getMAX_PLAYERS():
                if self._isGalleryVisible(iPlayer):
                    self.iViewPlayer = iPlayer
                    self.drawScreen()
                    return 1
        return 0

    def update(self, fDelta):
        return 0

    def onClose(self):
        self._clearWidgets()


g_ArtAdvisor = CvArtAdvisor()
