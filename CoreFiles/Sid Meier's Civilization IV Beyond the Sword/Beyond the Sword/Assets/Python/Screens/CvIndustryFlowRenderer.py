from CvPythonExtensions import *
import CvUtil

gc = CyGlobalContext()
ArtFileMgr = CyArtFileMgr()


class CvIndustryFlowRenderer:
    def __init__(self, addWidgetFn):
        self._addWidget = addWidgetFn
        self.GRID_X_SPACING = 172
        self.GRID_Y_SPACING = 114
        self.NODE_W = 198
        self.NODE_H = 94
        self.MARGIN_X = 36
        self.MARGIN_Y = 20
        self.ICON_SIZE = 28
        self.BADGE_SIZE = 18
        self.LINE_THICKNESS = 8
        self._edgeLaneOffsets = {
            'flow': 0,
            'corp_input': 6,
            'corp_founding': -6,
        }

    def _nodeSize(self, kNode):
        szClass = kNode.get('sizeClass', 'normal')
        if szClass == 'corporation':
            return (376, 122)
        if szClass == 'composite':
            return (220, 108)
        return (self.NODE_W, self.NODE_H)

    def render(self, screen, x, y, w, h, widgetPrefix, nodes, edges, sections = None):
        scrollId = self._addWidget('%sScroll' % widgetPrefix)
        screen.addScrollPanel(scrollId, u'', x, y, w, h, PanelStyles.PANEL_STYLE_EXTERNAL)
        screen.setActivation(scrollId, ActivationTypes.ACTIVATE_NORMAL)

        if len(nodes) == 0:
            emptyId = self._addWidget('%sEmpty' % widgetPrefix)
            screen.setTextAt(emptyId, scrollId, u'<font=2>No flow data available.</font>', CvUtil.FONT_LEFT_JUSTIFY, 12, 12, -0.1, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
            screen.setViewMin(scrollId, w, h)
            return

        positions = self._buildPositions(nodes)
        self._drawSections(screen, scrollId, widgetPrefix, sections, positions)
        self._drawEdges(screen, scrollId, widgetPrefix, positions, edges)
        self._drawNodes(screen, scrollId, widgetPrefix, positions, nodes)

        iMaxX = 0
        iMaxY = 0
        for kPos in positions.values():
            if kPos['x'] + kPos['w'] > iMaxX:
                iMaxX = kPos['x'] + kPos['w']
            if kPos['y'] + kPos['h'] > iMaxY:
                iMaxY = kPos['y'] + kPos['h']
        screen.setViewMin(scrollId, iMaxX + self.MARGIN_X, iMaxY + self.MARGIN_Y)

    def _drawSections(self, screen, scrollId, widgetPrefix, sections, positions):
        if not sections:
            return

        for iSection, kSection in enumerate(sections):
            iY = self.MARGIN_Y + (kSection['startGridY'] * self.GRID_Y_SPACING) - 24
            if iY < 4:
                iY = 4
            labelId = self._addWidget('%sSection%d' % (widgetPrefix, iSection))
            screen.setTextAt(labelId, scrollId, u'<font=2><color=255,220,130>%s</color></font>' % kSection['label'], CvUtil.FONT_LEFT_JUSTIFY, 8, iY, -0.1, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

    def _buildPositions(self, nodes):
        positions = {}
        for kNode in nodes:
            iW, iH = self._nodeSize(kNode)
            iX = self.MARGIN_X + (kNode['gridX'] * self.GRID_X_SPACING)
            if kNode['gridX'] >= 7:
                iX += 54
            if kNode['gridX'] >= 10:
                iX += 74
            positions[kNode['id']] = {
                'x': iX,
                'y': self.MARGIN_Y + (kNode['gridY'] * self.GRID_Y_SPACING),
                'w': iW,
                'h': iH,
            }
        return positions

    def _stateColor(self, szState):
        if szState == 'active':
            return (85, 150, 87)
        if szState == 'ready':
            return (104, 158, 165)
        if szState == 'blocked':
            return (100, 104, 160)
        return (206, 65, 69)

    def _drawNodes(self, screen, scrollId, widgetPrefix, positions, nodes):
        for iNode, kNode in enumerate(nodes):
            kPos = positions[kNode['id']]
            panelId = self._addWidget('%sPanel%d' % (widgetPrefix, iNode))
            screen.attachPanelAt(scrollId, panelId, u'', u'', True, False, PanelStyles.PANEL_STYLE_TECH, kPos['x'], kPos['y'], kPos['w'], kPos['h'], WidgetTypes.WIDGET_GENERAL, -1, -1)
            screen.setActivation(panelId, ActivationTypes.ACTIVATE_MIMICPARENTFOCUS)
            iR, iG, iB = self._stateColor(kNode.get('state', 'unavailable'))
            screen.setPanelColor(panelId, iR, iG, iB)

            eWidget = kNode.get('widgetType', WidgetTypes.WIDGET_GENERAL)
            iData1 = kNode.get('data1', -1)
            iData2 = kNode.get('data2', -1)
            titleLines = kNode.get('titleLines', [kNode.get('title', u'')])
            titleFont = kNode.get('titleFont', 2)
            titleLineStep = 16
            if titleFont <= 1:
                titleLineStep = 14
            subtitle = kNode.get('subtitle', u'')
            subtitleAlign = kNode.get('subtitleAlign', 'left')
            metaText = kNode.get('metaText', u'')
            badges = kNode.get('badges', [])
            hasFooter = bool(metaText or badges)

            if hasFooter:
                iIconY = 10
                iTitleStartY = 8
            else:
                iTextBlockH = (len(titleLines) * titleLineStep)
                if subtitle:
                    iTextBlockH += 16
                iTitleStartY = max(8, ((kPos['h'] - iTextBlockH) / 2) - 2)
                iIconY = max(8, ((kPos['h'] - self.ICON_SIZE) / 2) - 2)

            if kNode.get('button', ''):
                iconId = self._addWidget('%sIcon%d' % (widgetPrefix, iNode))
                screen.addDDSGFCAt(iconId, panelId, kNode['button'], 8, iIconY, self.ICON_SIZE, self.ICON_SIZE, eWidget, iData1, iData2, False)

            iTitleY = iTitleStartY
            for iLine, szLine in enumerate(titleLines):
                titleId = self._addWidget('%sTitle%d_%d' % (widgetPrefix, iNode, iLine))
                screen.setTextAt(titleId, panelId, u'<font=%d>%s</font>' % (titleFont, szLine), CvUtil.FONT_LEFT_JUSTIFY, 44, iTitleY, -0.1, FontTypes.SMALL_FONT, eWidget, iData1, iData2)
                iTitleY += titleLineStep

            if subtitle:
                subtitleId = self._addWidget('%sSubtitle%d' % (widgetPrefix, iNode))
                if subtitleAlign == 'center':
                    screen.setTextAt(subtitleId, panelId, u'<font=1>%s</font>' % subtitle, CvUtil.FONT_CENTER_JUSTIFY, (kPos['w'] + 44) / 2, iTitleY + 2, -0.1, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
                else:
                    screen.setTextAt(subtitleId, panelId, u'<font=1>%s</font>' % subtitle, CvUtil.FONT_LEFT_JUSTIFY, 44, iTitleY + 2, -0.1, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
                iBodyBottom = iTitleY + 16
            else:
                iBodyBottom = iTitleY

            if metaText:
                metaId = self._addWidget('%sMeta%d' % (widgetPrefix, iNode))
                iFooterHeight = 16
                if badges:
                    iFooterHeight += self.BADGE_SIZE + 4
                iMetaY = iBodyBottom + 12
                iMaxMetaY = kPos['h'] - iFooterHeight - 8
                if iMetaY > iMaxMetaY:
                    iMetaY = iMaxMetaY
                if kNode.get('metaAlign', 'left') == 'center':
                    screen.setTextAt(metaId, panelId, u'<font=1>%s</font>' % metaText, CvUtil.FONT_CENTER_JUSTIFY, kPos['w'] / 2, iMetaY, -0.1, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
                else:
                    screen.setTextAt(metaId, panelId, u'<font=1>%s</font>' % metaText, CvUtil.FONT_LEFT_JUSTIFY, 8, iMetaY, -0.1, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
            else:
                iMetaY = iBodyBottom

            if badges:
                iBadgeSpan = (len(badges) * self.BADGE_SIZE) + ((len(badges) - 1) * 4)
                iBadgeX = max(8, (kPos['w'] - iBadgeSpan) / 2)
                if metaText:
                    iBadgeY = iMetaY + 16
                else:
                    iBadgeY = iBodyBottom + 12
                iMaxBadgeY = kPos['h'] - self.BADGE_SIZE - 8
                if iBadgeY > iMaxBadgeY:
                    iBadgeY = iMaxBadgeY
                for iBadge, kBadge in enumerate(badges):
                    badgeId = self._addWidget('%sBadge%d_%d' % (widgetPrefix, iNode, iBadge))
                    screen.addDDSGFCAt(
                        badgeId,
                        panelId,
                        kBadge.get('button', u''),
                        iBadgeX,
                        iBadgeY,
                        self.BADGE_SIZE,
                        self.BADGE_SIZE,
                        kBadge.get('widgetType', WidgetTypes.WIDGET_GENERAL),
                        kBadge.get('data1', -1),
                        kBadge.get('data2', -1),
                        False
                    )
                    iBadgeX += self.BADGE_SIZE + 4

    def _drawEdges(self, screen, scrollId, widgetPrefix, positions, edges):
        arrowX = ArtFileMgr.getInterfaceArtInfo('ARROW_X').getPath()
        arrowY = ArtFileMgr.getInterfaceArtInfo('ARROW_Y').getPath()
        arrowXY = ArtFileMgr.getInterfaceArtInfo('ARROW_XY').getPath()
        arrowXMY = ArtFileMgr.getInterfaceArtInfo('ARROW_XMY').getPath()
        arrowMXMY = ArtFileMgr.getInterfaceArtInfo('ARROW_MXMY').getPath()
        arrowMXY = ArtFileMgr.getInterfaceArtInfo('ARROW_MXY').getPath()
        arrowHead = ArtFileMgr.getInterfaceArtInfo('ARROW_HEAD').getPath()
        outgoingSlots, incomingSlots, outgoingCounts, incomingCounts = self._buildEdgeSlots(edges)

        for iEdge, kEdge in enumerate(edges):
            if not positions.has_key(kEdge['from']) or not positions.has_key(kEdge['to']):
                continue
            kFrom = positions[kEdge['from']]
            kTo = positions[kEdge['to']]
            iStartX = kFrom['x'] + kFrom['w']
            iStartY = kFrom['y'] + self._portOffset(outgoingSlots.get(kEdge['from'], {}).get(iEdge, 0), outgoingCounts.get(kEdge['from'], 1), kFrom['h'])
            iEndX = kTo['x']
            iEndY = kTo['y'] + self._portOffset(incomingSlots.get(kEdge['to'], {}).get(iEdge, 0), incomingCounts.get(kEdge['to'], 1), kTo['h'])

            if iEndX <= iStartX:
                iEndX = iStartX + self.LINE_THICKNESS + 8

            if iStartY == iEndY:
                self._drawHorizontal(screen, scrollId, '%sEdge%d' % (widgetPrefix, iEdge), arrowX, arrowHead, iStartX, iStartY, iEndX)
            else:
                iMidX = self._laneMidX(iEdge, kEdge, iStartX, iEndX, outgoingSlots, incomingSlots)
                self._drawCornerPath(screen, scrollId, '%sEdge%d' % (widgetPrefix, iEdge), arrowX, arrowY, arrowXY, arrowXMY, arrowMXMY, arrowMXY, arrowHead, iStartX, iStartY, iMidX, iEndX, iEndY)

    def _buildEdgeSlots(self, edges):
        outgoingSlots = {}
        incomingSlots = {}
        outgoingCounts = {}
        incomingCounts = {}

        for iEdge, kEdge in enumerate(edges):
            if not outgoingSlots.has_key(kEdge['from']):
                outgoingSlots[kEdge['from']] = {}
                outgoingCounts[kEdge['from']] = 0
            outgoingSlots[kEdge['from']][iEdge] = outgoingCounts[kEdge['from']]
            outgoingCounts[kEdge['from']] += 1

            if not incomingSlots.has_key(kEdge['to']):
                incomingSlots[kEdge['to']] = {}
                incomingCounts[kEdge['to']] = 0
            incomingSlots[kEdge['to']][iEdge] = incomingCounts[kEdge['to']]
            incomingCounts[kEdge['to']] += 1

        return outgoingSlots, incomingSlots, outgoingCounts, incomingCounts

    def _portOffset(self, iSlot, iCount, iNodeH):
        iBase = (iNodeH / 2) - (self.LINE_THICKNESS / 2)
        if iCount <= 1:
            return iBase

        iMin = 10
        iMax = iNodeH - self.LINE_THICKNESS - 10
        if iMax <= iMin:
            return iBase

        if iCount == 2:
            if iSlot == 0:
                return iMin
            return iMax

        iSpan = iMax - iMin
        return iMin + ((iSpan * iSlot) / (iCount - 1))

    def _laneMidX(self, iEdge, kEdge, iStartX, iEndX, outgoingSlots, incomingSlots):
        iSpan = iEndX - iStartX
        if iSpan <= 40:
            return iStartX + 16

        iLaneBase = iStartX + 30
        iLaneSource = outgoingSlots.get(kEdge['from'], {}).get(iEdge, 0)
        iLaneDest = incomingSlots.get(kEdge['to'], {}).get(iEdge, 0)
        iTypeBump = 0
        if kEdge.get('type', 'flow') == 'corp_input':
            iTypeBump = 20
        elif kEdge.get('type', 'flow') == 'corp_founding':
            iTypeBump = 40

        iLaneX = iLaneBase + (iLaneSource * 12) + (iLaneDest * 16) + iTypeBump
        iMaxX = iEndX - 28
        if iLaneX > iMaxX:
            iLaneX = iStartX + ((iEndX - iStartX) / 2)
        if iLaneX <= iStartX:
            iLaneX = iStartX + 20
        return iLaneX

    def _drawHorizontal(self, screen, scrollId, prefix, arrowX, arrowHead, iStartX, iY, iEndX):
        iWidth = iEndX - iStartX
        if arrowHead:
            iWidth -= self.LINE_THICKNESS
        if iWidth > 0:
            lineId = self._addWidget('%sLine' % prefix)
            screen.addDDSGFCAt(lineId, scrollId, arrowX, iStartX, iY, iWidth, self.LINE_THICKNESS, WidgetTypes.WIDGET_GENERAL, -1, -1, False)
        if arrowHead:
            headId = self._addWidget('%sHead' % prefix)
            screen.addDDSGFCAt(headId, scrollId, arrowHead, iEndX - self.LINE_THICKNESS, iY, self.LINE_THICKNESS, self.LINE_THICKNESS, WidgetTypes.WIDGET_GENERAL, -1, -1, False)

    def _drawVertical(self, screen, scrollId, prefix, arrowY, iX, iStartY, iEndY):
        iTop = min(iStartY, iEndY)
        iHeight = abs(iEndY - iStartY) + self.LINE_THICKNESS
        if iHeight <= 0:
            return
        lineId = self._addWidget('%sLine' % prefix)
        screen.addDDSGFCAt(lineId, scrollId, arrowY, iX, iTop, self.LINE_THICKNESS, iHeight, WidgetTypes.WIDGET_GENERAL, -1, -1, False)

    def _drawCorner(self, screen, scrollId, prefix, path, iX, iY):
        cornerId = self._addWidget('%sCorner' % prefix)
        screen.addDDSGFCAt(cornerId, scrollId, path, iX, iY, self.LINE_THICKNESS, self.LINE_THICKNESS, WidgetTypes.WIDGET_GENERAL, -1, -1, False)

    def _drawCornerPath(self, screen, scrollId, prefix, arrowX, arrowY, arrowXY, arrowXMY, arrowMXMY, arrowMXY, arrowHead, iStartX, iStartY, iMidX, iEndX, iEndY):
        iCornerStartX = iMidX - self.LINE_THICKNESS
        iCornerEndX = iMidX

        if iEndY < iStartY:
            self._drawHorizontal(screen, scrollId, '%sA' % prefix, arrowX, None, iStartX, iStartY, iCornerStartX)
            self._drawCorner(screen, scrollId, '%sB' % prefix, arrowXY, iCornerStartX, iStartY)
            self._drawVertical(screen, scrollId, '%sC' % prefix, arrowY, iCornerStartX, iEndY + self.LINE_THICKNESS, iStartY)
            self._drawCorner(screen, scrollId, '%sD' % prefix, arrowXMY, iCornerEndX, iEndY)
            self._drawHorizontal(screen, scrollId, '%sE' % prefix, arrowX, arrowHead, iCornerEndX + self.LINE_THICKNESS, iEndY, iEndX)
        else:
            self._drawHorizontal(screen, scrollId, '%sA' % prefix, arrowX, None, iStartX, iStartY, iCornerStartX)
            self._drawCorner(screen, scrollId, '%sB' % prefix, arrowMXMY, iCornerStartX, iStartY)
            self._drawVertical(screen, scrollId, '%sC' % prefix, arrowY, iCornerStartX, iStartY + self.LINE_THICKNESS, iEndY)
            self._drawCorner(screen, scrollId, '%sD' % prefix, arrowMXY, iCornerEndX, iEndY)
            self._drawHorizontal(screen, scrollId, '%sE' % prefix, arrowX, arrowHead, iCornerEndX + self.LINE_THICKNESS, iEndY, iEndX)
