NODE_TYPE_RAW = 'raw'
NODE_TYPE_PROCESSOR = 'processor'
NODE_TYPE_SYNTHETIC = 'synthetic'
NODE_TYPE_COMPOSITE = 'composite'
NODE_TYPE_CORPORATION = 'corporation'

EDGE_TYPE_FLOW = 'flow'
EDGE_TYPE_CORP_INPUT = 'corp_input'
EDGE_TYPE_CORP_FOUNDING = 'corp_founding'

FILTER_ALL = 'all'

PROCESSING_CHAINS = (
    {'building': 'BUILDING_INDUSTRY_DYE_WORKS', 'raws': ('BONUS_DYE',), 'synthetic': 'BONUS_FINE_DYES'},
    {'building': 'BUILDING_INDUSTRY_FURRIERS_HALL', 'raws': ('BONUS_FUR',), 'synthetic': 'BONUS_FINE_FURS'},
    {'building': 'BUILDING_INDUSTRY_JEWELERS_QUARTER', 'raws': ('BONUS_GEMS',), 'synthetic': 'BONUS_CUT_GEMS'},
    {'building': 'BUILDING_INDUSTRY_MINTING_HOUSE', 'raws': ('BONUS_GOLD',), 'synthetic': 'BONUS_GOLD_BULLION'},
    {'building': 'BUILDING_INDUSTRY_PERFUMERS_SANCTUARY', 'raws': ('BONUS_INCENSE',), 'synthetic': 'BONUS_TEMPLE_INCENSE'},
    {'building': 'BUILDING_INDUSTRY_IVORY_CARVERS_ATELIER', 'raws': ('BONUS_IVORY',), 'synthetic': 'BONUS_IVORY_CARVINGS'},
    {'building': 'BUILDING_INDUSTRY_SILK_WEAVERS_WORKSHOP', 'raws': ('BONUS_SILK',), 'synthetic': 'BONUS_FINE_SILK'},
    {'building': 'BUILDING_INDUSTRY_SILVERSMITHS_HALL', 'raws': ('BONUS_SILVER',), 'synthetic': 'BONUS_WORKED_SILVER'},
    {'building': 'BUILDING_INDUSTRY_SPICE_EXCHANGE', 'raws': ('BONUS_SPICES',), 'synthetic': 'BONUS_SPICE_BLENDS'},
    {'building': 'BUILDING_INDUSTRY_CONFECTIONERS_GUILD', 'raws': ('BONUS_SUGAR',), 'synthetic': 'BONUS_CONFECTIONS'},
    {'building': 'BUILDING_INDUSTRY_VINTNERS_GUILD', 'raws': ('BONUS_WINE',), 'synthetic': 'BONUS_VINTAGE_WINE'},
    {'building': 'BUILDING_INDUSTRY_WHALE_OIL_CHANDLERY', 'raws': ('BONUS_WHALE',), 'synthetic': 'BONUS_LAMP_OIL'},
    {'building': 'BUILDING_INDUSTRY_PLAYWRIGHTS_GUILD', 'raws': ('BONUS_DRAMA',), 'synthetic': 'BONUS_STAGE_PLAYS'},
    {'building': 'BUILDING_INDUSTRY_RECORDING_HOUSE', 'raws': ('BONUS_MUSIC',), 'synthetic': 'BONUS_MASTER_RECORDINGS'},
    {'building': 'BUILDING_INDUSTRY_FILM_STUDIO_DISTRICT', 'raws': ('BONUS_MOVIES',), 'synthetic': 'BONUS_FILM_PRINTS'},
    {'building': 'BUILDING_INDUSTRY_MILLERS_GUILD', 'raws': ('BONUS_WHEAT', 'BONUS_CORN', 'BONUS_RICE'), 'synthetic': 'BONUS_FLOUR'},
    {'building': 'BUILDING_INDUSTRY_SMOKEHOUSE', 'raws': ('BONUS_COW', 'BONUS_PIG', 'BONUS_SHEEP', 'BONUS_DEER'), 'synthetic': 'BONUS_CURED_MEATS'},
    {'building': 'BUILDING_INDUSTRY_CANNERY', 'raws': ('BONUS_FISH', 'BONUS_CLAM', 'BONUS_CRAB'), 'synthetic': 'BONUS_PRESERVED_SEAFOOD'},
    {'building': 'BUILDING_INDUSTRY_FRUIT_PRESERVERS', 'raws': ('BONUS_BANANA',), 'synthetic': 'BONUS_FRUIT_PRESERVES'},
    {'building': 'BUILDING_INDUSTRY_SCULPTORS_YARD', 'raws': ('BONUS_MARBLE',), 'synthetic': 'BONUS_MARBLE_STATUARY'},
)

COMPOSITE_RECIPES = (
    {'building': 'BUILDING_INDUSTRY_ROYAL_GARMENTS_HOUSE', 'goods': ('BONUS_FINE_SILK', 'BONUS_FINE_DYES')},
    {'building': 'BUILDING_INDUSTRY_NOBLE_TAILORS_HALL', 'goods': ('BONUS_FINE_SILK', 'BONUS_FINE_FURS')},
    {'building': 'BUILDING_INDUSTRY_COURT_REGALIA_ATELIER', 'goods': ('BONUS_FINE_SILK', 'BONUS_IVORY_CARVINGS')},
    {'building': 'BUILDING_INDUSTRY_DYED_FUR_SALON', 'goods': ('BONUS_FINE_DYES', 'BONUS_FINE_FURS')},
    {'building': 'BUILDING_INDUSTRY_CROWN_JEWELER', 'goods': ('BONUS_GOLD_BULLION', 'BONUS_CUT_GEMS')},
    {'building': 'BUILDING_INDUSTRY_ROYAL_MINT', 'goods': ('BONUS_GOLD_BULLION', 'BONUS_WORKED_SILVER')},
    {'building': 'BUILDING_INDUSTRY_GEMCUTTERS_EXCHANGE', 'goods': ('BONUS_WORKED_SILVER', 'BONUS_CUT_GEMS')},
    {'building': 'BUILDING_INDUSTRY_REGAL_TREASURES_COURT', 'goods': ('BONUS_GOLD_BULLION', 'BONUS_IVORY_CARVINGS')},
    {'building': 'BUILDING_INDUSTRY_PERFUMERS_QUARTER', 'goods': ('BONUS_TEMPLE_INCENSE', 'BONUS_SPICE_BLENDS')},
    {'building': 'BUILDING_INDUSTRY_GRAND_BANQUET_HALL', 'goods': ('BONUS_VINTAGE_WINE', 'BONUS_CONFECTIONS')},
    {'building': 'BUILDING_INDUSTRY_CONFECTIONERS_EXCHANGE', 'goods': ('BONUS_CONFECTIONS', 'BONUS_SPICE_BLENDS')},
    {'building': 'BUILDING_INDUSTRY_CEREMONIAL_CELLARS', 'goods': ('BONUS_VINTAGE_WINE', 'BONUS_TEMPLE_INCENSE')},
    {'building': 'BUILDING_INDUSTRY_FESTIVAL_MARKET', 'goods': ('BONUS_VINTAGE_WINE', 'BONUS_SPICE_BLENDS')},
    {'building': 'BUILDING_INDUSTRY_IMPERIAL_OUTFITTERS', 'goods': ('BONUS_FINE_FURS', 'BONUS_IVORY_CARVINGS')},
    {'building': 'BUILDING_INDUSTRY_ADMIRALTY_CURIOS_HOUSE', 'goods': ('BONUS_LAMP_OIL', 'BONUS_IVORY_CARVINGS')},
    {'building': 'BUILDING_INDUSTRY_NAVIGATORS_INSTRUMENT_WORKS', 'goods': ('BONUS_LAMP_OIL', 'BONUS_WORKED_SILVER')},
    {'building': 'BUILDING_INDUSTRY_OPERA_HOUSE', 'goods': ('BONUS_STAGE_PLAYS', 'BONUS_MASTER_RECORDINGS')},
    {'building': 'BUILDING_INDUSTRY_CINEMA_PALACE', 'goods': ('BONUS_STAGE_PLAYS', 'BONUS_FILM_PRINTS')},
    {'building': 'BUILDING_INDUSTRY_SOUNDSTAGE_COMPLEX', 'goods': ('BONUS_MASTER_RECORDINGS', 'BONUS_FILM_PRINTS')},
    {'building': 'BUILDING_INDUSTRY_MASS_ENTERTAINMENT_NETWORK', 'goods': ('BONUS_STAGE_PLAYS', 'BONUS_MASTER_RECORDINGS', 'BONUS_FILM_PRINTS')},
    {'building': 'BUILDING_INDUSTRY_BAKERS_EXCHANGE', 'goods': ('BONUS_FLOUR', 'BONUS_SPICE_BLENDS')},
    {'building': 'BUILDING_INDUSTRY_FESTIVAL_KITCHENS', 'goods': ('BONUS_FLOUR', 'BONUS_VINTAGE_WINE')},
    {'building': 'BUILDING_INDUSTRY_ROYAL_KITCHENS', 'goods': ('BONUS_CURED_MEATS', 'BONUS_VINTAGE_WINE')},
    {'building': 'BUILDING_INDUSTRY_SPICED_CARVERY', 'goods': ('BONUS_CURED_MEATS', 'BONUS_SPICE_BLENDS')},
    {'building': 'BUILDING_INDUSTRY_MARITIME_SUPPER_CLUB', 'goods': ('BONUS_PRESERVED_SEAFOOD', 'BONUS_VINTAGE_WINE')},
    {'building': 'BUILDING_INDUSTRY_PRESERVES_MARKET', 'goods': ('BONUS_FRUIT_PRESERVES', 'BONUS_CONFECTIONS')},
    {'building': 'BUILDING_INDUSTRY_HALL_OF_CAMEOS', 'goods': ('BONUS_MARBLE_STATUARY', 'BONUS_CUT_GEMS')},
    {'building': 'BUILDING_INDUSTRY_TRIUMPHAL_COURT', 'goods': ('BONUS_MARBLE_STATUARY', 'BONUS_GOLD_BULLION')},
    {'building': 'BUILDING_INDUSTRY_GALLERY_OF_ANTIQUITIES', 'goods': ('BONUS_MARBLE_STATUARY', 'BONUS_IVORY_CARVINGS')},
    {'building': 'BUILDING_INDUSTRY_SACRED_PRECINCT', 'goods': ('BONUS_MARBLE_STATUARY', 'BONUS_TEMPLE_INCENSE')},
    {'building': 'BUILDING_INDUSTRY_PASTRY_HOUSE', 'goods': ('BONUS_FLOUR', 'BONUS_FRUIT_PRESERVES')},
    {'building': 'BUILDING_INDUSTRY_VICTUALLERS_EXCHANGE', 'goods': ('BONUS_FLOUR', 'BONUS_CURED_MEATS')},
    {'building': 'BUILDING_INDUSTRY_SPICED_FISH_MARKET', 'goods': ('BONUS_PRESERVED_SEAFOOD', 'BONUS_SPICE_BLENDS')},
    {'building': 'BUILDING_INDUSTRY_DESSERT_CELLARS', 'goods': ('BONUS_FRUIT_PRESERVES', 'BONUS_VINTAGE_WINE')},
    {'building': 'BUILDING_INDUSTRY_PERFUMED_SALON', 'goods': ('BONUS_TEMPLE_INCENSE', 'BONUS_FINE_SILK')},
    {'building': 'BUILDING_INDUSTRY_LANTERN_PROCESSION_WORKS', 'goods': ('BONUS_TEMPLE_INCENSE', 'BONUS_LAMP_OIL')},
    {'building': 'BUILDING_INDUSTRY_CURIO_AUCTION_HOUSE', 'goods': ('BONUS_IVORY_CARVINGS', 'BONUS_CUT_GEMS')},
    {'building': 'BUILDING_INDUSTRY_ILLUMINATED_THEATRE', 'goods': ('BONUS_LAMP_OIL', 'BONUS_STAGE_PLAYS')},
)

CORPORATION_FAMILIES = (
    {
        'id': 'corp1',
        'short_label': 'Provisions',
        'corporation': 'CORPORATION_1',
        'hq_building': 'BUILDING_CORPORATION_1',
        'min_active_composites': 3,
        'prereq_goods': ('BONUS_FLOUR', 'BONUS_CURED_MEATS', 'BONUS_PRESERVED_SEAFOOD', 'BONUS_FRUIT_PRESERVES'),
        'operating_goods': ('BONUS_FLOUR', 'BONUS_CURED_MEATS', 'BONUS_PRESERVED_SEAFOOD', 'BONUS_FRUIT_PRESERVES'),
        'composites': (
            'BUILDING_INDUSTRY_BAKERS_EXCHANGE',
            'BUILDING_INDUSTRY_SPICED_CARVERY',
            'BUILDING_INDUSTRY_PRESERVES_MARKET',
            'BUILDING_INDUSTRY_VICTUALLERS_EXCHANGE',
            'BUILDING_INDUSTRY_SPICED_FISH_MARKET',
        ),
    },
    {
        'id': 'corp2',
        'short_label': 'Hospitality',
        'corporation': 'CORPORATION_2',
        'hq_building': 'BUILDING_CORPORATION_2',
        'min_active_composites': 3,
        'prereq_goods': ('BONUS_VINTAGE_WINE', 'BONUS_CONFECTIONS'),
        'operating_goods': ('BONUS_VINTAGE_WINE', 'BONUS_CONFECTIONS'),
        'composites': (
            'BUILDING_INDUSTRY_FESTIVAL_KITCHENS',
            'BUILDING_INDUSTRY_ROYAL_KITCHENS',
            'BUILDING_INDUSTRY_GRAND_BANQUET_HALL',
            'BUILDING_INDUSTRY_CEREMONIAL_CELLARS',
            'BUILDING_INDUSTRY_MARITIME_SUPPER_CLUB',
            'BUILDING_INDUSTRY_PASTRY_HOUSE',
            'BUILDING_INDUSTRY_DESSERT_CELLARS',
        ),
    },
    {
        'id': 'corp3',
        'short_label': 'Luxury',
        'corporation': 'CORPORATION_3',
        'hq_building': 'BUILDING_CORPORATION_3',
        'min_active_composites': 3,
        'prereq_goods': ('BONUS_FINE_SILK', 'BONUS_FINE_DYES', 'BONUS_CUT_GEMS', 'BONUS_GOLD_BULLION', 'BONUS_WORKED_SILVER', 'BONUS_FINE_FURS'),
        'operating_goods': ('BONUS_FINE_SILK', 'BONUS_FINE_DYES', 'BONUS_CUT_GEMS', 'BONUS_GOLD_BULLION', 'BONUS_WORKED_SILVER', 'BONUS_FINE_FURS'),
        'composites': (
            'BUILDING_INDUSTRY_ROYAL_GARMENTS_HOUSE',
            'BUILDING_INDUSTRY_NOBLE_TAILORS_HALL',
            'BUILDING_INDUSTRY_DYED_FUR_SALON',
            'BUILDING_INDUSTRY_CROWN_JEWELER',
            'BUILDING_INDUSTRY_ROYAL_MINT',
            'BUILDING_INDUSTRY_GEMCUTTERS_EXCHANGE',
        ),
    },
    {
        'id': 'corp4',
        'short_label': 'Court',
        'corporation': 'CORPORATION_4',
        'hq_building': 'BUILDING_CORPORATION_4',
        'min_active_composites': 3,
        'prereq_goods': ('BONUS_IVORY_CARVINGS', 'BONUS_LAMP_OIL', 'BONUS_MARBLE_STATUARY'),
        'operating_goods': ('BONUS_IVORY_CARVINGS', 'BONUS_LAMP_OIL', 'BONUS_MARBLE_STATUARY'),
        'composites': (
            'BUILDING_INDUSTRY_COURT_REGALIA_ATELIER',
            'BUILDING_INDUSTRY_REGAL_TREASURES_COURT',
            'BUILDING_INDUSTRY_IMPERIAL_OUTFITTERS',
            'BUILDING_INDUSTRY_ADMIRALTY_CURIOS_HOUSE',
            'BUILDING_INDUSTRY_NAVIGATORS_INSTRUMENT_WORKS',
            'BUILDING_INDUSTRY_HALL_OF_CAMEOS',
            'BUILDING_INDUSTRY_TRIUMPHAL_COURT',
            'BUILDING_INDUSTRY_GALLERY_OF_ANTIQUITIES',
            'BUILDING_INDUSTRY_CURIO_AUCTION_HOUSE',
        ),
    },
    {
        'id': 'corp5',
        'short_label': 'Aromatics',
        'corporation': 'CORPORATION_5',
        'hq_building': 'BUILDING_CORPORATION_5',
        'min_active_composites': 3,
        'prereq_goods': ('BONUS_TEMPLE_INCENSE', 'BONUS_SPICE_BLENDS'),
        'operating_goods': ('BONUS_TEMPLE_INCENSE', 'BONUS_SPICE_BLENDS'),
        'composites': (
            'BUILDING_INDUSTRY_PERFUMERS_QUARTER',
            'BUILDING_INDUSTRY_CONFECTIONERS_EXCHANGE',
            'BUILDING_INDUSTRY_FESTIVAL_MARKET',
            'BUILDING_INDUSTRY_PERFUMED_SALON',
            'BUILDING_INDUSTRY_LANTERN_PROCESSION_WORKS',
            'BUILDING_INDUSTRY_SACRED_PRECINCT',
        ),
    },
    {
        'id': 'corp6',
        'short_label': 'Media',
        'corporation': 'CORPORATION_6',
        'hq_building': 'BUILDING_CORPORATION_6',
        'min_active_composites': 3,
        'prereq_goods': ('BONUS_STAGE_PLAYS', 'BONUS_MASTER_RECORDINGS', 'BONUS_FILM_PRINTS'),
        'operating_goods': ('BONUS_STAGE_PLAYS', 'BONUS_MASTER_RECORDINGS', 'BONUS_FILM_PRINTS'),
        'composites': (
            'BUILDING_INDUSTRY_OPERA_HOUSE',
            'BUILDING_INDUSTRY_CINEMA_PALACE',
            'BUILDING_INDUSTRY_SOUNDSTAGE_COMPLEX',
            'BUILDING_INDUSTRY_MASS_ENTERTAINMENT_NETWORK',
            'BUILDING_INDUSTRY_ILLUMINATED_THEATRE',
        ),
    },
)

FLOW_FILTERS = (
    {'id': FILTER_ALL, 'short_label': 'All Chains', 'corporation': None},
    {'id': 'corp1', 'short_label': 'Provisions', 'corporation': 'CORPORATION_1'},
    {'id': 'corp2', 'short_label': 'Hospitality', 'corporation': 'CORPORATION_2'},
    {'id': 'corp3', 'short_label': 'Luxury', 'corporation': 'CORPORATION_3'},
    {'id': 'corp4', 'short_label': 'Court', 'corporation': 'CORPORATION_4'},
    {'id': 'corp5', 'short_label': 'Aromatics', 'corporation': 'CORPORATION_5'},
    {'id': 'corp6', 'short_label': 'Media', 'corporation': 'CORPORATION_6'},
)

_PROCESSING_BY_SYNTHETIC = {}
_COMPOSITE_BY_BUILDING = {}

for _kChain in PROCESSING_CHAINS:
    _PROCESSING_BY_SYNTHETIC[_kChain['synthetic']] = _kChain

for _kComposite in COMPOSITE_RECIPES:
    _COMPOSITE_BY_BUILDING[_kComposite['building']] = _kComposite


def _ordered_unique(seq):
    result = []
    for item in seq:
        if item not in result:
            result.append(item)
    return result


def getFlowFilters():
    return FLOW_FILTERS


def getCorporationFamilies():
    return CORPORATION_FAMILIES


def getCorporationFamily(filterId):
    for kFamily in CORPORATION_FAMILIES:
        if kFamily['id'] == filterId:
            return kFamily
    return None


def getProcessingChains():
    return PROCESSING_CHAINS


def getCompositeRecipes():
    return COMPOSITE_RECIPES


def getProcessingChainBySynthetic(szSynthetic):
    return _PROCESSING_BY_SYNTHETIC.get(szSynthetic, None)


def getCompositeRecipe(szBuilding):
    return _COMPOSITE_BY_BUILDING.get(szBuilding, None)


def getFamilySyntheticGoods(filterId):
    kFamily = getCorporationFamily(filterId)
    if kFamily is None:
        return ()
    return tuple(_familySyntheticGoods(kFamily))


def getFamilyProcessingChains(filterId):
    kFamily = getCorporationFamily(filterId)
    if kFamily is None:
        return ()
    return tuple(_familyProcessingChains(kFamily))


def _familySyntheticGoods(kFamily):
    goods = []
    for szGood in kFamily['operating_goods']:
        goods.append(szGood)
    for szComposite in kFamily['composites']:
        kRecipe = getCompositeRecipe(szComposite)
        if kRecipe is None:
            continue
        for szGood in kRecipe['goods']:
            goods.append(szGood)
    return _ordered_unique(goods)


def _familyProcessingChains(kFamily):
    synths = _familySyntheticGoods(kFamily)
    chains = []
    for szSynthetic in synths:
        kChain = getProcessingChainBySynthetic(szSynthetic)
        if kChain is not None:
            chains.append(kChain)
    return _ordered_unique(chains)


def _familyRawBonuses(kFamily):
    bonuses = []
    for kChain in _familyProcessingChains(kFamily):
        for szRaw in kChain['raws']:
            bonuses.append(szRaw)
    return _ordered_unique(bonuses)


def _addNode(nodes, nodeId, nodeType, gameType, gridX, gridY, filterId):
    nodes.append({
        'id': nodeId,
        'type': nodeType,
        'gameType': gameType,
        'gridX': gridX,
        'gridY': gridY,
        'filterId': filterId,
    })


def _addEdge(edges, fromNodeId, toNodeId, edgeType):
    edges.append({
        'from': fromNodeId,
        'to': toNodeId,
        'type': edgeType,
    })


def _buildFamilyGraph(kFamily, iStartY):
    nodes = []
    edges = []
    filterId = kFamily['id']
    synths = _familySyntheticGoods(kFamily)
    chains = _familyProcessingChains(kFamily)
    composites = kFamily['composites']
    rawRows = {}
    processorRows = {}
    syntheticRows = {}
    compositeRows = {}
    iRawCursor = iStartY
    iCompositeCursor = iStartY

    for kChain in chains:
        szSynthetic = kChain['synthetic']
        aiRawRows = []
        for szRaw in kChain['raws']:
            if not rawRows.has_key(szRaw):
                rawRows[szRaw] = iRawCursor
                iRawCursor += 1
            aiRawRows.append(rawRows[szRaw])
        if len(aiRawRows) > 0:
            iAnchorRow = aiRawRows[len(aiRawRows) / 2]
        else:
            iAnchorRow = iRawCursor
            iRawCursor += 1
        processorRows[kChain['building']] = iAnchorRow
        syntheticRows[szSynthetic] = iAnchorRow
        if iRawCursor < iAnchorRow + 2:
            iRawCursor = iAnchorRow + 2

    for szComposite in composites:
        compositeRows[szComposite] = iCompositeCursor
        iCompositeCursor += 1

    aiFamilyRows = []
    for iValue in rawRows.values():
        aiFamilyRows.append(iValue)
    for iValue in compositeRows.values():
        aiFamilyRows.append(iValue)
    if len(aiFamilyRows) == 0:
        iCorpRow = iStartY
    else:
        iMinRow = min(aiFamilyRows)
        iMaxRow = max(aiFamilyRows)
        iCorpRow = iMinRow + ((iMaxRow - iMinRow) / 2)

    for szRaw in _familyRawBonuses(kFamily):
        _addNode(nodes, '%s_raw_%s' % (filterId, szRaw), NODE_TYPE_RAW, szRaw, 0, rawRows[szRaw], filterId)

    for kChain in chains:
        _addNode(nodes, '%s_proc_%s' % (filterId, kChain['building']), NODE_TYPE_PROCESSOR, kChain['building'], 2, processorRows[kChain['building']], filterId)
        _addNode(nodes, '%s_syn_%s' % (filterId, kChain['synthetic']), NODE_TYPE_SYNTHETIC, kChain['synthetic'], 4, syntheticRows[kChain['synthetic']], filterId)
        for szRaw in kChain['raws']:
            _addEdge(edges, '%s_raw_%s' % (filterId, szRaw), '%s_proc_%s' % (filterId, kChain['building']), EDGE_TYPE_FLOW)
        _addEdge(edges, '%s_proc_%s' % (filterId, kChain['building']), '%s_syn_%s' % (filterId, kChain['synthetic']), EDGE_TYPE_FLOW)

    for szComposite in composites:
        _addNode(nodes, '%s_comp_%s' % (filterId, szComposite), NODE_TYPE_COMPOSITE, szComposite, 7, compositeRows[szComposite], filterId)
        kRecipe = getCompositeRecipe(szComposite)
        if kRecipe is None:
            continue
        for szGood in kRecipe['goods']:
            if syntheticRows.has_key(szGood):
                _addEdge(edges, '%s_syn_%s' % (filterId, szGood), '%s_comp_%s' % (filterId, szComposite), EDGE_TYPE_FLOW)

    _addNode(nodes, '%s_corp_%s' % (filterId, kFamily['corporation']), NODE_TYPE_CORPORATION, kFamily['corporation'], 10, iCorpRow, filterId)

    for szComposite in composites:
        _addEdge(edges, '%s_comp_%s' % (filterId, szComposite), '%s_corp_%s' % (filterId, kFamily['corporation']), EDGE_TYPE_CORP_FOUNDING)
    for szGood in kFamily['operating_goods']:
        if syntheticRows.has_key(szGood):
            _addEdge(edges, '%s_syn_%s' % (filterId, szGood), '%s_corp_%s' % (filterId, kFamily['corporation']), EDGE_TYPE_CORP_INPUT)

    iHeight = max(iRawCursor, iCompositeCursor)
    return {
        'nodes': nodes,
        'edges': edges,
        'height': iHeight - iStartY,
        'section': {
            'id': filterId,
            'label': kFamily['short_label'],
            'startGridY': iStartY,
            'endGridY': iHeight,
        },
    }


def buildFlowGraph(filterId):
    nodes = []
    edges = []
    sections = []
    if filterId == FILTER_ALL:
        families = CORPORATION_FAMILIES
    else:
        families = []
        for kFamily in CORPORATION_FAMILIES:
            if kFamily['id'] == filterId:
                families.append(kFamily)
                break

    iCursorY = 0
    for kFamily in families:
        kFamilyGraph = _buildFamilyGraph(kFamily, iCursorY)
        nodes.extend(kFamilyGraph['nodes'])
        edges.extend(kFamilyGraph['edges'])
        sections.append(kFamilyGraph['section'])
        iCursorY += kFamilyGraph['height'] + 3

    return {
        'nodes': nodes,
        'edges': edges,
        'filters': FLOW_FILTERS,
        'sections': sections,
    }
