from __future__ import annotations

from pathlib import Path
import shutil
import sys
from xml.dom import minidom

ROOT = Path(r"C:/DowagerMod")
sys.path.insert(0, str(ROOT / 'tools'))
import apply_supply_chain_overhaul as base

BP = base.BP
BCP = base.BCP
BAP = base.BAP
BONP = base.BONP
BONP_BTS = base.BONP_BTS
BOAP = base.BOAP
BOAP_BTS = base.BOAP_BTS
CP = base.CP
BBTN = base.BBTN
TEXTP = ROOT / "CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Text/ZZZZ_CIV4GameText_IndustryWave2.xml"
STP = base.STP

GOLD, RESEARCH, CULTURE, ESPIONAGE = 0, 1, 2, 3

MARBLE_BONUS = {
    'type': 'BONUS_MARBLE_STATUARY',
    'name': 'Marble Statuary',
    'art': 'ART_DEF_BONUS_MARBLE_STATUARY',
    'source_art': 'ART_DEF_BONUS_MARBLE',
}

NEW_PROC = {
    'type': 'BUILDING_INDUSTRY_SCULPTORS_YARD',
    'class': 'BUILDINGCLASS_INDUSTRY_SCULPTORS_YARD',
    'name': "Sculptors' Yard",
    'art': 'ART_DEF_BUILDING_INDUSTRY_SCULPTORS_YARD',
    'button': 'sculptors_yard.dds',
    'tech': 'TECH_MASONRY',
    'free': 'BONUS_MARBLE_STATUARY',
    'cost': 130,
    'needs': ['BUILDINGCLASS_OBELISK'],
    'local': [{'bonuses': ['BONUS_MARBLE'], 'min': 1, 'improved': 1, 'connected': 1, 'city': 1}],
    'culture': 2,
    'cmods': {CULTURE: 10},
    'spec': {'SPECIALIST_ARTIST': 1},
    'flv': {'FLAVOR_CULTURE': 8, 'FLAVOR_GOLD': 2},
    'tmpl': 'ART_DEF_BUILDING_INDUSTRY_IVORY_CARVERS_ATELIER',
    'button_source': 'ivory_carvers_atelier.dds',
}

NEW_COMPOSITES = [
    {
        'type': 'BUILDING_INDUSTRY_HALL_OF_CAMEOS', 'class': 'BUILDINGCLASS_INDUSTRY_HALL_OF_CAMEOS', 'name': 'Hall of Cameos',
        'art': 'ART_DEF_BUILDING_INDUSTRY_HALL_OF_CAMEOS', 'button': 'hall_of_cameos.dds', 'tech': 'TECH_AESTHETICS', 'cost': 190,
        'conn': ['BONUS_MARBLE_STATUARY', 'BONUS_CUT_GEMS'], 'happy': 1, 'cmods': {GOLD: 15, CULTURE: 15}, 'flv': {'FLAVOR_GOLD': 7, 'FLAVOR_CULTURE': 8},
        'tmpl': 'ART_DEF_BUILDING_INDUSTRY_CROWN_JEWELER', 'button_source': 'crown_jeweler.dds'
    },
    {
        'type': 'BUILDING_INDUSTRY_TRIUMPHAL_COURT', 'class': 'BUILDINGCLASS_INDUSTRY_TRIUMPHAL_COURT', 'name': 'Triumphal Court',
        'art': 'ART_DEF_BUILDING_INDUSTRY_TRIUMPHAL_COURT', 'button': 'triumphal_court.dds', 'tech': 'TECH_AESTHETICS', 'cost': 200,
        'conn': ['BONUS_MARBLE_STATUARY', 'BONUS_GOLD_BULLION'], 'happy': 1, 'cmods': {GOLD: 10, CULTURE: 20}, 'flv': {'FLAVOR_GOLD': 6, 'FLAVOR_CULTURE': 9},
        'tmpl': 'ART_DEF_BUILDING_INDUSTRY_REGAL_TREASURES_COURT', 'button_source': 'regal_treasures_court.dds'
    },
    {
        'type': 'BUILDING_INDUSTRY_GALLERY_OF_ANTIQUITIES', 'class': 'BUILDINGCLASS_INDUSTRY_GALLERY_OF_ANTIQUITIES', 'name': 'Gallery of Antiquities',
        'art': 'ART_DEF_BUILDING_INDUSTRY_GALLERY_OF_ANTIQUITIES', 'button': 'gallery_of_antiquities.dds', 'tech': 'TECH_AESTHETICS', 'cost': 190,
        'conn': ['BONUS_MARBLE_STATUARY', 'BONUS_IVORY_CARVINGS'], 'happy': 1, 'cmods': {CULTURE: 20}, 'spec': {'SPECIALIST_ARTIST': 1}, 'flv': {'FLAVOR_CULTURE': 10},
        'tmpl': 'ART_DEF_BUILDING_INDUSTRY_REGAL_TREASURES_COURT', 'button_source': 'imperial_outfitters.dds'
    },
    {
        'type': 'BUILDING_INDUSTRY_SACRED_PRECINCT', 'class': 'BUILDINGCLASS_INDUSTRY_SACRED_PRECINCT', 'name': 'Sacred Precinct',
        'art': 'ART_DEF_BUILDING_INDUSTRY_SACRED_PRECINCT', 'button': 'sacred_precinct.dds', 'tech': 'TECH_AESTHETICS', 'cost': 190,
        'conn': ['BONUS_MARBLE_STATUARY', 'BONUS_TEMPLE_INCENSE'], 'happy': 1, 'cmods': {CULTURE: 15}, 'spec': {'SPECIALIST_PRIEST': 1}, 'flv': {'FLAVOR_CULTURE': 8, 'FLAVOR_RELIGION': 6},
        'tmpl': 'ART_DEF_BUILDING_INDUSTRY_PERFUMERS_QUARTER', 'button_source': 'perfumers_quarter.dds'
    },
    {
        'type': 'BUILDING_INDUSTRY_PASTRY_HOUSE', 'class': 'BUILDINGCLASS_INDUSTRY_PASTRY_HOUSE', 'name': 'Pastry House',
        'art': 'ART_DEF_BUILDING_INDUSTRY_PASTRY_HOUSE', 'button': 'pastry_house.dds', 'tech': 'TECH_CALENDAR', 'cost': 180,
        'conn': ['BONUS_FLOUR', 'BONUS_FRUIT_PRESERVES'], 'health': 1, 'happy': 1, 'cmods': {GOLD: 15}, 'flv': {'FLAVOR_GOLD': 7, 'FLAVOR_GROWTH': 4},
        'tmpl': 'ART_DEF_BUILDING_INDUSTRY_PRESERVES_MARKET', 'button_source': 'preserves_market.dds'
    },
    {
        'type': 'BUILDING_INDUSTRY_VICTUALLERS_EXCHANGE', 'class': 'BUILDINGCLASS_INDUSTRY_VICTUALLERS_EXCHANGE', 'name': "Victuallers' Exchange",
        'art': 'ART_DEF_BUILDING_INDUSTRY_VICTUALLERS_EXCHANGE', 'button': 'victuallers_exchange.dds', 'tech': 'TECH_CURRENCY', 'cost': 180,
        'conn': ['BONUS_FLOUR', 'BONUS_CURED_MEATS'], 'health': 1, 'hammer': 1, 'cmods': {GOLD: 10}, 'flv': {'FLAVOR_GOLD': 6, 'FLAVOR_PRODUCTION': 4},
        'tmpl': 'ART_DEF_BUILDING_INDUSTRY_SPICED_CARVERY', 'button_source': 'spiced_carvery.dds'
    },
    {
        'type': 'BUILDING_INDUSTRY_SPICED_FISH_MARKET', 'class': 'BUILDINGCLASS_INDUSTRY_SPICED_FISH_MARKET', 'name': 'Spiced Fish Market',
        'art': 'ART_DEF_BUILDING_INDUSTRY_SPICED_FISH_MARKET', 'button': 'spiced_fish_market.dds', 'tech': 'TECH_COMPASS', 'cost': 190,
        'conn': ['BONUS_PRESERVED_SEAFOOD', 'BONUS_SPICE_BLENDS'], 'health': 1, 'happy': 1, 'cmods': {GOLD: 15}, 'flv': {'FLAVOR_GOLD': 7, 'FLAVOR_GROWTH': 4},
        'tmpl': 'ART_DEF_BUILDING_INDUSTRY_MARITIME_SUPPER_CLUB', 'button_source': 'maritime_supper_club.dds'
    },
    {
        'type': 'BUILDING_INDUSTRY_DESSERT_CELLARS', 'class': 'BUILDINGCLASS_INDUSTRY_DESSERT_CELLARS', 'name': 'Dessert Cellars',
        'art': 'ART_DEF_BUILDING_INDUSTRY_DESSERT_CELLARS', 'button': 'dessert_cellars.dds', 'tech': 'TECH_MONARCHY', 'cost': 180,
        'conn': ['BONUS_FRUIT_PRESERVES', 'BONUS_VINTAGE_WINE'], 'happy': 1, 'cmods': {GOLD: 10, CULTURE: 10}, 'flv': {'FLAVOR_GOLD': 6, 'FLAVOR_CULTURE': 5},
        'tmpl': 'ART_DEF_BUILDING_INDUSTRY_GRAND_BANQUET_HALL', 'button_source': 'grand_banquet_hall.dds'
    },
    {
        'type': 'BUILDING_INDUSTRY_PERFUMED_SALON', 'class': 'BUILDINGCLASS_INDUSTRY_PERFUMED_SALON', 'name': 'Perfumed Salon',
        'art': 'ART_DEF_BUILDING_INDUSTRY_PERFUMED_SALON', 'button': 'perfumed_salon.dds', 'tech': 'TECH_DRAMA', 'cost': 190,
        'conn': ['BONUS_TEMPLE_INCENSE', 'BONUS_FINE_SILK'], 'happy': 1, 'cmods': {GOLD: 10, CULTURE: 10}, 'flv': {'FLAVOR_GOLD': 5, 'FLAVOR_CULTURE': 7},
        'tmpl': 'ART_DEF_BUILDING_INDUSTRY_ROYAL_GARMENTS_HOUSE', 'button_source': 'royal_garments_house.dds'
    },
    {
        'type': 'BUILDING_INDUSTRY_LANTERN_PROCESSION_WORKS', 'class': 'BUILDINGCLASS_INDUSTRY_LANTERN_PROCESSION_WORKS', 'name': 'Lantern Procession Works',
        'art': 'ART_DEF_BUILDING_INDUSTRY_LANTERN_PROCESSION_WORKS', 'button': 'lantern_procession_works.dds', 'tech': 'TECH_DRAMA', 'cost': 190,
        'conn': ['BONUS_TEMPLE_INCENSE', 'BONUS_LAMP_OIL'], 'happy': 1, 'cmods': {CULTURE: 15}, 'spec': {'SPECIALIST_PRIEST': 1}, 'flv': {'FLAVOR_CULTURE': 8, 'FLAVOR_RELIGION': 5},
        'tmpl': 'ART_DEF_BUILDING_INDUSTRY_PERFUMERS_QUARTER', 'button_source': 'opera_house.dds'
    },
    {
        'type': 'BUILDING_INDUSTRY_CURIO_AUCTION_HOUSE', 'class': 'BUILDINGCLASS_INDUSTRY_CURIO_AUCTION_HOUSE', 'name': 'Curio Auction House',
        'art': 'ART_DEF_BUILDING_INDUSTRY_CURIO_AUCTION_HOUSE', 'button': 'curio_auction_house.dds', 'tech': 'TECH_CURRENCY', 'cost': 190,
        'conn': ['BONUS_IVORY_CARVINGS', 'BONUS_CUT_GEMS'], 'happy': 1, 'cmods': {GOLD: 15, CULTURE: 10}, 'flv': {'FLAVOR_GOLD': 8, 'FLAVOR_CULTURE': 5},
        'tmpl': 'ART_DEF_BUILDING_INDUSTRY_ADMIRALTY_CURIOS_HOUSE', 'button_source': 'admiralty_curios_house.dds'
    },
    {
        'type': 'BUILDING_INDUSTRY_ILLUMINATED_THEATRE', 'class': 'BUILDINGCLASS_INDUSTRY_ILLUMINATED_THEATRE', 'name': 'Illuminated Theatre',
        'art': 'ART_DEF_BUILDING_INDUSTRY_ILLUMINATED_THEATRE', 'button': 'illuminated_theatre.dds', 'tech': 'TECH_DRAMA', 'cost': 200,
        'conn': ['BONUS_LAMP_OIL', 'BONUS_STAGE_PLAYS'], 'happy': 1, 'cmods': {CULTURE: 15}, 'spec': {'SPECIALIST_ARTIST': 1}, 'flv': {'FLAVOR_CULTURE': 9},
        'tmpl': 'ART_DEF_BUILDING_INDUSTRY_OPERA_HOUSE', 'button_source': 'opera_house.dds'
    },
]

CORP4_EXTRA_INPUT = 'BONUS_MARBLE_STATUARY'
CORP4_EXTRA_CLASSES = [
    'BUILDINGCLASS_INDUSTRY_HALL_OF_CAMEOS',
    'BUILDINGCLASS_INDUSTRY_TRIUMPHAL_COURT',
    'BUILDINGCLASS_INDUSTRY_GALLERY_OF_ANTIQUITIES',
    'BUILDINGCLASS_INDUSTRY_SACRED_PRECINCT',
]


def setlist(node, tag, item_tag, values, before=None):
    c = node.ownerDocument.createElement(tag)
    for value in values:
        c.appendChild(base.mk(node.ownerDocument, item_tag, value))
    base.rep(node, c, before)


def ensure_bonus_files():
    for path in (BONP, BONP_BTS):
        d = base.parse(path)
        tmpl = base.by_type(d, 'BonusInfo', 'BONUS_DRAMA')
        n = base.ensure(d, 'BonusInfos', 'BonusInfo', MARBLE_BONUS['type'], tmpl)
        base.setc(n, 'Type', MARBLE_BONUS['type'])
        base.setc(n, 'Description', 'TXT_KEY_BONUS_MARBLE_STATUARY')
        base.setc(n, 'Civilopedia', 'TXT_KEY_BONUS_MARBLE_STATUARY_PEDIA')
        base.setc(n, 'BonusClassType', 'BONUSCLASS_GENERAL')
        base.setc(n, 'ArtDefineTag', MARBLE_BONUS['art'])
        base.setc(n, 'TechReveal', 'NONE')
        base.setc(n, 'TechCityTrade', 'NONE')
        base.setc(n, 'TechObsolete', 'NONE')
        base.setc(n, 'iAITradeModifier', 0)
        if path == BONP_BTS:
            base.setc(n, 'iAIObjective', 0, 'iHealth')
        base.setc(n, 'iHealth', 0)
        base.setc(n, 'iHappiness', 0)
        base.setc(n, 'iPlacementOrder', -1)
        base.setc(n, 'iConstAppearance', 0)
        base.setc(n, 'iMinAreaSize', -1)
        base.setc(n, 'iMinLatitude', 0)
        base.setc(n, 'iMaxLatitude', 90)
        base.setc(n, 'iPlayer', 0)
        base.setc(n, 'iTilesPer', 0)
        base.setc(n, 'iMinLandPercent', 0)
        base.setc(n, 'iUnique', 0)
        base.setc(n, 'iGroupRange', 0)
        base.setc(n, 'iGroupRand', 0)
        base.setc(n, 'bArea', 0)
        base.setc(n, 'bHills', 0)
        base.setc(n, 'bFlatlands', 0)
        base.setc(n, 'bNoRiverSide', 0)
        base.setc(n, 'bNormalize', 0)
        base.empty(n, 'YieldChanges', 'iAITradeModifier')
        if base.child(n, 'Rands') is None:
            r = n.ownerDocument.createElement('Rands')
            for t in ('iRandApp1', 'iRandApp2', 'iRandApp3', 'iRandApp4'):
                r.appendChild(base.mk(n.ownerDocument, t, 0))
            base.rep(n, r, 'iPlayer')
        base.empty(n, 'TerrainBooleans', 'FeatureBooleans')
        base.empty(n, 'FeatureBooleans', 'FeatureTerrainBooleans')
        base.empty(n, 'FeatureTerrainBooleans')
        base.write(d, path)

    for path in (BOAP, BOAP_BTS):
        d = base.parse(path)
        src = base.by_type(d, 'BonusArtInfo', MARBLE_BONUS['source_art'])
        n = base.ensure(d, 'BonusArtInfos', 'BonusArtInfo', MARBLE_BONUS['art'], src)
        base.setc(n, 'Type', MARBLE_BONUS['art'])
        base.setc(n, 'fScale', base.txt(base.child(src, 'fScale')))
        base.setc(n, 'fInterfaceScale', base.txt(base.child(src, 'fInterfaceScale')))
        base.setc(n, 'NIF', base.txt(base.child(src, 'NIF')))
        base.setc(n, 'KFM', base.txt(base.child(src, 'KFM')))
        base.setc(n, 'Button', base.txt(base.child(src, 'Button')))
        if path == BOAP_BTS:
            font = base.child(src, 'FontButtonIndex')
            if font is not None:
                base.setc(n, 'FontButtonIndex', base.txt(font))
        sh = base.child(n, 'SHADERNIF')
        if sh is not None:
            n.removeChild(sh)
        base.write(d, path)


def copy_buttons():
    BBTN.mkdir(parents=True, exist_ok=True)
    for meta in [NEW_PROC] + NEW_COMPOSITES:
        src = BBTN / meta['button_source']
        dst = BBTN / meta['button']
        if src.exists():
            shutil.copy2(src, dst)


def patch_building_classes_and_art():
    d = base.parse(BCP)
    tmpl = base.by_type(d, 'BuildingClassInfo', 'BUILDINGCLASS_INDUSTRY_DYE_WORKS')
    for meta in [NEW_PROC] + NEW_COMPOSITES:
        n = base.ensure(d, 'BuildingClassInfos', 'BuildingClassInfo', meta['class'], tmpl)
        for t, v in [
            ('Type', meta['class']),
            ('Description', f'TXT_KEY_{meta["type"]}'),
            ('iMaxGlobalInstances', -1),
            ('iMaxTeamInstances', -1),
            ('iMaxPlayerInstances', -1),
            ('iExtraPlayerInstances', 0),
            ('bNoLimit', 0),
            ('bMonument', 0),
            ('DefaultBuilding', meta['type']),
        ]:
            base.setc(n, t, v)
        base.empty(n, 'VictoryThresholds')
    base.write(d, BCP)

    d = base.parse(BAP)
    tmpl_map = {base.txt(base.child(n, 'Type')): n for n in d.getElementsByTagName('BuildingArtInfo')}
    for meta in [NEW_PROC] + NEW_COMPOSITES:
        src = tmpl_map[meta['tmpl']]
        n = base.ensure(d, 'BuildingArtInfos', 'BuildingArtInfo', meta['art'], src)
        base.setc(n, 'Type', meta['art'])
        base.setc(n, 'Button', f'Art/Interface/Buttons/Buildings/Industries/{meta["button"]}')
    base.write(d, BAP)


def patch_buildings():
    d = base.parse(BP)
    idx = {base.txt(base.child(n, 'Type')): n for n in d.getElementsByTagName('BuildingInfo')}
    tmpl_local = idx['BUILDING_INDUSTRY_IVORY_CARVERS_ATELIER']
    tmpl_comp = idx['BUILDING_INDUSTRY_REGAL_TREASURES_COURT']

    meta = NEW_PROC
    n = base.ensure(d, 'BuildingInfos', 'BuildingInfo', meta['type'], tmpl_local)
    for t, v in [
        ('BuildingClass', meta['class']), ('Type', meta['type']), ('Description', f'TXT_KEY_{meta["type"]}'),
        ('Civilopedia', f'TXT_KEY_{meta["type"]}_PEDIA'), ('Strategy', f'TXT_KEY_{meta["type"]}_STRATEGY'),
        ('Advisor', 'ADVISOR_ECONOMY'), ('ArtDefineTag', meta['art']), ('PrereqTech', meta['tech']),
        ('Bonus', 'NONE'), ('FreeBonus', meta['free']), ('iNumFreeBonuses', 1), ('IndustryCategory', 'LUXURY'),
        ('bRequiresActiveLocalPrereqs', 1), ('iCost', meta['cost']), ('GreatPeopleUnitClass', 'NONE'), ('iPlayerMaxInstances', 0)
    ]:
        base.setc(n, t, v)
    base.build_effects(n, meta)
    base.neededs(n, meta['needs'])
    base.local_bonus_prereqs(n, meta['local'])
    base.connected_bonus_prereqs(n, [])
    base.empty(n, 'LocalImprovementCountPrereqs', 'LocalBonusPrereqs')
    base.flavors(n, meta['flv'])

    for meta in NEW_COMPOSITES:
        n = base.ensure(d, 'BuildingInfos', 'BuildingInfo', meta['type'], tmpl_comp)
        for t, v in [
            ('BuildingClass', meta['class']), ('Type', meta['type']), ('Description', f'TXT_KEY_{meta["type"]}'),
            ('Civilopedia', f'TXT_KEY_{meta["type"]}_PEDIA'), ('Strategy', f'TXT_KEY_{meta["type"]}_STRATEGY'),
            ('Advisor', 'ADVISOR_ECONOMY'), ('ArtDefineTag', meta['art']), ('PrereqTech', meta['tech']),
            ('Bonus', 'NONE'), ('FreeBonus', 'NONE'), ('iNumFreeBonuses', 0), ('IndustryCategory', 'COMPOSITE'),
            ('bRequiresActiveLocalPrereqs', 1), ('iCost', meta['cost']), ('GreatPeopleUnitClass', 'NONE'), ('iPlayerMaxInstances', 1)
        ]:
            base.setc(n, t, v)
        base.build_effects(n, meta, 3)
        base.neededs(n, [])
        base.empty(n, 'LocalImprovementCountPrereqs', 'LocalBonusPrereqs')
        base.empty(n, 'LocalBonusPrereqs', 'ConnectedBonusPrereqs')
        base.connected_bonus_prereqs(n, [{'bonuses': [b], 'min': 1} for b in meta['conn']])
        base.flavors(n, meta['flv'])

    base.write(d, BP)


def patch_corp4():
    d = base.parse(CP)
    n = base.by_type(d, 'CorporationInfo', 'CORPORATION_4')
    prereqs = [base.txt(x) for x in base.els(base.child(n, 'PrereqBonuses'), 'BonusType')]
    if CORP4_EXTRA_INPUT not in prereqs:
        prereqs.append(CORP4_EXTRA_INPUT)
    setlist(n, 'PrereqBonuses', 'BonusType', prereqs, 'HeadquarterCommerces')

    found = [base.txt(x) for x in base.els(base.child(n, 'FoundingBuildingClasses'), 'BuildingClassType')]
    for b in CORP4_EXTRA_CLASSES:
        if b not in found:
            found.append(b)
    setlist(n, 'FoundingBuildingClasses', 'BuildingClassType', found, 'PrereqBonuses')
    base.write(d, CP)


def patch_supply_chain_text():
    def entry(tag, english):
        return f'''\t<TEXT>\n\t\t<Tag>{tag}</Tag>\n\t\t<English>{english}</English>\n\t\t<French>{english}</French>\n\t\t<German>{english}</German>\n\t\t<Italian>{english}</Italian>\n\t\t<Spanish>{english}</Spanish>\n\t</TEXT>\n'''

    texts = ['<?xml version="1.0" encoding="utf-8"?>\n<Civ4GameText xmlns="x-schema:CIV4GameTextSchema.xml">\n']
    texts.append(entry('TXT_KEY_BONUS_MARBLE_STATUARY', 'Marble Statuary'))
    texts.append(entry('TXT_KEY_BONUS_MARBLE_STATUARY_PEDIA', 'Manufactured prestige good produced by Sculptors\' Yards. Marble Statuary does not provide direct happiness or health, but it can be traded and used as an input for downstream composite industries and corporations.'))

    building_text = {
        'BUILDING_INDUSTRY_SCULPTORS_YARD': ('Sculptors\' Yard', 'Local marble workshops turn quarried stone into carvings, statuary, and ceremonial display pieces for the wider economy.', 'Build in a marble city to produce Marble Statuary for downstream composites.'),
        'BUILDING_INDUSTRY_HALL_OF_CAMEOS': ('Hall of Cameos', 'A fine-arts exchange for carved stone miniatures and gem-set relief work.', 'Prestige composite built from Marble Statuary and Cut Gems.'),
        'BUILDING_INDUSTRY_TRIUMPHAL_COURT': ('Triumphal Court', 'A monumental court complex dedicated to ceremonial display, victory art, and state grandeur.', 'Prestige composite built from Marble Statuary and Gold Bullion.'),
        'BUILDING_INDUSTRY_GALLERY_OF_ANTIQUITIES': ('Gallery of Antiquities', 'A curated hall of sculpture, carvings, and rare courtly artifacts.', 'Prestige composite built from Marble Statuary and Ivory Carvings.'),
        'BUILDING_INDUSTRY_SACRED_PRECINCT': ('Sacred Precinct', 'Temples, courts, and incense-rich sanctuaries converge into a ceremonial district.', 'Religious composite built from Marble Statuary and Temple Incense.'),
        'BUILDING_INDUSTRY_PASTRY_HOUSE': ('Pastry House', 'A refined bakery quarter specializing in layered pastries, preserves, and sweet luxuries.', 'Hospitality composite built from Flour and Fruit Preserves.'),
        'BUILDING_INDUSTRY_VICTUALLERS_EXCHANGE': ("Victuallers' Exchange", 'A provisioning market for bread, salted goods, and stored supplies moving through urban trade.', 'Provision composite built from Flour and Cured Meats.'),
        'BUILDING_INDUSTRY_SPICED_FISH_MARKET': ('Spiced Fish Market', 'Preserved coastal catches are blended with aromatic spices for high-value urban trade.', 'Provision composite built from Preserved Seafood and Spice Blends.'),
        'BUILDING_INDUSTRY_DESSERT_CELLARS': ('Dessert Cellars', 'Cellared sweets, wines, and preserved fruits supply elite tables and festival circuits.', 'Hospitality composite built from Fruit Preserves and Vintage Wine.'),
        'BUILDING_INDUSTRY_PERFUMED_SALON': ('Perfumed Salon', 'Silks and incense come together in an elite salon of fashion, scent, and display.', 'Luxury composite built from Temple Incense and Fine Silk.'),
        'BUILDING_INDUSTRY_LANTERN_PROCESSION_WORKS': ('Lantern Procession Works', 'Oil, incense, and ceremony produce the lighting and pageantry of night processions.', 'Festival composite built from Temple Incense and Lamp Oil.'),
        'BUILDING_INDUSTRY_CURIO_AUCTION_HOUSE': ('Curio Auction House', 'Rare carved works and precious stones circulate through a market for collectors and courts.', 'Prestige composite built from Ivory Carvings and Cut Gems.'),
        'BUILDING_INDUSTRY_ILLUMINATED_THEATRE': ('Illuminated Theatre', 'Lamp-lit playhouses turn staged performances into a city-defining entertainment trade.', 'Media composite built from Lamp Oil and Stage Plays.'),
    }
    for tag, vals in building_text.items():
        texts.append(entry(f'TXT_KEY_{tag}', vals[0]))
        texts.append(entry(f'TXT_KEY_{tag}_PEDIA', vals[1]))
        texts.append(entry(f'TXT_KEY_{tag}_STRATEGY', vals[2]))

    concept = '''[H1]Industry Supply Chains[\\H1][PARAGRAPH:1]Local Processing Industries only count resources and improvements that are both inside a city's workable radius and inside that city's borders. Enemy or neutral tiles in your BFC do not qualify.[PARAGRAPH:1]The chain now runs from Raw Resource to Local Processing Industry to Synthetic Good to Composite Industry to Corporation.[PARAGRAPH:1][BOLD]Marble Branch[\\BOLD][PARAGRAPH:1]Marble supports the [LINK=BUILDING_INDUSTRY_SCULPTORS_YARD]Sculptors\' Yard[\\LINK], which produces [LINK=BONUS_MARBLE_STATUARY]Marble Statuary[\\LINK]. Marble Statuary feeds [LINK=BUILDING_INDUSTRY_HALL_OF_CAMEOS]Hall of Cameos[\\LINK], [LINK=BUILDING_INDUSTRY_TRIUMPHAL_COURT]Triumphal Court[\\LINK], [LINK=BUILDING_INDUSTRY_GALLERY_OF_ANTIQUITIES]Gallery of Antiquities[\\LINK], and [LINK=BUILDING_INDUSTRY_SACRED_PRECINCT]Sacred Precinct[\\LINK].[PARAGRAPH:1][BOLD]Wave Two Composite Additions[\\BOLD][PARAGRAPH:1]Provision and hospitality chains now extend through [LINK=BUILDING_INDUSTRY_PASTRY_HOUSE]Pastry House[\\LINK], [LINK=BUILDING_INDUSTRY_VICTUALLERS_EXCHANGE]Victuallers\' Exchange[\\LINK], [LINK=BUILDING_INDUSTRY_SPICED_FISH_MARKET]Spiced Fish Market[\\LINK], and [LINK=BUILDING_INDUSTRY_DESSERT_CELLARS]Dessert Cellars[\\LINK].[PARAGRAPH:1]Aromatic, prestige, and performance chains now extend through [LINK=BUILDING_INDUSTRY_PERFUMED_SALON]Perfumed Salon[\\LINK], [LINK=BUILDING_INDUSTRY_LANTERN_PROCESSION_WORKS]Lantern Procession Works[\\LINK], [LINK=BUILDING_INDUSTRY_CURIO_AUCTION_HOUSE]Curio Auction House[\\LINK], and [LINK=BUILDING_INDUSTRY_ILLUMINATED_THEATRE]Illuminated Theatre[\\LINK].[PARAGRAPH:1]Composite Industries require connected synthetic goods in the city network, each composite type is limited to one per civilization, and each city may support up to three Composite Industries.[PARAGRAPH:1]Synthetic goods do not provide direct happiness or health on their own. Their value comes from activating composite industries, corporations, and trade opportunities.'''
    texts.append(entry('TXT_KEY_CONCEPT_INDUSTRY_SUPPLY_CHAINS', 'Industry Supply Chains'))
    texts.append(entry('TXT_KEY_CONCEPT_INDUSTRY_SUPPLY_CHAINS_PEDIA', concept))
    texts.append('</Civ4GameText>\n')
    TEXTP.write_text(''.join(texts), encoding='utf-8')


def main():
    ensure_bonus_files()
    copy_buttons()
    patch_building_classes_and_art()
    patch_buildings()
    patch_corp4()
    patch_supply_chain_text()
    print('Applied industry wave 2 content patch.')


if __name__ == '__main__':
    main()
