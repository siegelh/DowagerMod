from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import apply_supply_chain_overhaul as base
from apply_guild_armaments import surgical_write, set_list, text_entry


ASSETS = ROOT / "CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets"
BUILDING_CLASSES = ASSETS / "XML/Buildings/CIV4BuildingClassInfos.xml"
BUILDINGS = ASSETS / "XML/Buildings/CIV4BuildingInfos.xml"
UNIT_CLASSES = ASSETS / "XML/Units/CIV4UnitClassInfos.xml"
UNITS = ASSETS / "XML/Units/CIV4UnitInfos.xml"
UNIT_ART = ASSETS / "XML/Art/CIV4ArtDefines_Unit.xml"
TEXT = ASSETS / "XML/Text/ZZZZZ_CIV4GameText_GuildNetworks.xml"


GUILDS = (
    {
        "key": "ARTIFICERS",
        "name": "Artificers and Farriers",
        "founder": "UNIT_ENGINEER",
        "specialist": "SPECIALIST_ENGINEER",
        "advisor": "ADVISOR_ECONOMY",
        "house": {"yield": (0, 0, 0), "ymod": (0, 25, 0), "commerce": (0, 0, 0, 0), "cmod": (0, 0, 0, 0), "health": 0, "happy": 0, "routes": 0},
        "button": "Art/Interface/Buttons/Buildings/Industries/iron_foundry.dds",
    },
    {
        "key": "MERCHANT_ADVENTURERS",
        "name": "Merchant Adventurers",
        "founder": "UNIT_MERCHANT",
        "specialist": "SPECIALIST_MERCHANT",
        "advisor": "ADVISOR_ECONOMY",
        "house": {"yield": (0, 0, 0), "ymod": (0, 0, 0), "commerce": (0, 0, 0, 0), "cmod": (25, 0, 0, 0), "health": 0, "happy": 0, "routes": 2},
        "button": "Art/Interface/Buttons/Buildings/Industries/exchange_hall.dds",
    },
    {
        "key": "APOTHECARIES",
        "name": "Apothecaries and Chandlers",
        "founder": "UNIT_SCIENTIST",
        "specialist": "SPECIALIST_SCIENTIST",
        "advisor": "ADVISOR_SCIENCE",
        "house": {"yield": (0, 0, 0), "ymod": (0, 0, 0), "commerce": (0, 0, 0, 0), "cmod": (0, 25, 0, 0), "health": 3, "happy": 0, "routes": 0},
        "button": "Art/Interface/Buttons/Buildings/Industries/whale_oil_chandlery.dds",
    },
    {
        "key": "VICTUALLERS",
        "name": "Victuallers",
        "founder": "UNIT_MERCHANT",
        "specialist": "SPECIALIST_MERCHANT",
        "advisor": "ADVISOR_ECONOMY",
        "house": {"yield": (3, 0, 0), "ymod": (0, 0, 0), "commerce": (0, 0, 0, 0), "cmod": (0, 0, 0, 0), "health": 3, "happy": 0, "routes": 0},
        "button": "Art/Interface/Buttons/Buildings/Industries/victuallers_exchange.dds",
    },
    {
        "key": "PAGEANTRY",
        "name": "Fellowship of Pageantry",
        "founder": "UNIT_ARTIST",
        "specialist": "SPECIALIST_ARTIST",
        "advisor": "ADVISOR_CULTURE",
        "house": {"yield": (0, 0, 0), "ymod": (0, 0, 0), "commerce": (0, 0, 0, 0), "cmod": (0, 0, 25, 0), "health": 0, "happy": 3, "routes": 0},
        "button": "Art/Interface/Buttons/Buildings/Industries/illuminated_theatre.dds",
    },
)


def ids(guild):
    key = guild["key"]
    return {
        "hq_class": f"BUILDINGCLASS_GUILD_{key}_HEADQUARTERS",
        "hq": f"BUILDING_GUILD_{key}_HEADQUARTERS",
        "house_class": f"BUILDINGCLASS_GUILD_{key}_HOUSE",
        "house": f"BUILDING_GUILD_{key}_HOUSE",
        "unit_class": f"UNITCLASS_GUILD_{key}_EMISSARY",
        "unit": f"UNIT_GUILD_{key}_EMISSARY",
        "art": f"ART_DEF_UNIT_GUILD_{key}_EMISSARY",
    }


def patch_building_classes():
    doc = base.parse(BUILDING_CLASSES)
    template = base.by_type(doc, "BuildingClassInfo", "BUILDINGCLASS_INDUSTRY_DYE_WORKS")
    changed = []
    for guild in GUILDS:
        gid = ids(guild)
        for class_type, building_type, max_player in (
            (gid["hq_class"], gid["hq"], 1),
            (gid["house_class"], gid["house"], -1),
        ):
            node = base.ensure(doc, "BuildingClassInfos", "BuildingClassInfo", class_type, template)
            for tag, value in (
                ("Type", class_type),
                ("Description", f"TXT_KEY_{building_type}"),
                ("iMaxGlobalInstances", -1),
                ("iMaxTeamInstances", -1),
                ("iMaxPlayerInstances", max_player),
                ("iExtraPlayerInstances", 0),
                ("bNoLimit", 0),
                ("bMonument", 0),
                ("DefaultBuilding", building_type),
            ):
                base.setc(node, tag, value)
            base.empty(node, "VictoryThresholds")
            changed.append(class_type)
    surgical_write(doc, BUILDING_CLASSES, "BuildingClassInfo", tuple(changed), "BuildingClassInfos")


def reset_building_identity(node, guild, building_type, class_type):
    for tag, value in (
        ("BuildingClass", class_type),
        ("Type", building_type),
        ("Description", f"TXT_KEY_{building_type}"),
        ("Civilopedia", f"TXT_KEY_{building_type}_PEDIA"),
        ("Strategy", f"TXT_KEY_{building_type}_STRATEGY"),
        ("Advisor", guild["advisor"]),
        ("MovieDefineTag", "NONE"),
        ("HolyCity", "NONE"),
        ("ReligionType", "NONE"),
        ("StateReligion", "NONE"),
        ("PrereqReligion", "NONE"),
        ("PrereqCorporation", "NONE"),
        ("FoundsCorporation", "NONE"),
        ("GlobalReligionCommerce", "NONE"),
        ("GlobalCorporationCommerce", "NONE"),
        ("VictoryPrereq", "NONE"),
        ("ObsoleteTech", "NONE"),
        ("PrereqTech", "TECH_GUILDS"),
        ("Bonus", "NONE"),
        ("NoBonus", "NONE"),
        ("PowerBonus", "NONE"),
        ("FreeBonus", "NONE"),
        ("iNumFreeBonuses", 0),
        ("FreeBuilding", "NONE"),
        ("FreePromotion", "NONE"),
        ("CivicOption", "NONE"),
        ("bStateReligion", 0),
        ("bTeamShare", 0),
        ("bWater", 0),
        ("bRiver", 0),
        ("bPower", 0),
        ("bDirtyPower", 0),
        ("bAreaCleanPower", 0),
        ("bCapital", 0),
        ("bGovernmentCenter", 0),
        ("bGoldenAge", 0),
        ("bAllowsNukes", 0),
        ("bMapCentering", 0),
        ("bNoUnhappiness", 0),
        ("bNoUnhealthyPopulation", 0),
        ("bBuildingOnlyHealthy", 0),
        ("bPrereqReligion", 0),
        ("iAIWeight", 0),
        ("iCost", -1),
        ("iAdvancedStartCost", -1),
        ("iMinAreaSize", -1),
        ("iConquestProb", 100),
        ("iCitiesPrereq", 0),
        ("iTeamsPrereq", 0),
        ("iLevelPrereq", 0),
        ("iMinLatitude", 0),
        ("iMaxLatitude", 90),
        ("iMilitaryProductionModifier", 0),
        ("iTradeRoutes", 0),
        ("iAsset", 4),
        ("iPower", 0),
        ("fVisibilityPriority", 1.0),
    ):
        base.setc(node, tag, value)
    for tag in (
        "TechTypes",
        "PrereqBonuses",
        "ProductionTraits",
        "HappinessTraits",
        "SeaPlotYieldChanges",
        "RiverPlotYieldChanges",
        "GlobalSeaPlotYieldChanges",
        "GlobalCommerceModifiers",
        "SpecialistExtraCommerces",
        "StateReligionCommerces",
        "CommerceHappinesses",
        "ReligionChanges",
        "SpecialistYieldChanges",
        "BonusHealthChanges",
        "BonusHappinessChanges",
        "BonusProductionModifiers",
        "UnitCombatFreeExperiences",
        "DomainFreeExperiences",
        "DomainProductionModifiers",
        "BuildingHappinessChanges",
        "PrereqBuildingClasses",
        "BuildingClassNeededs",
        "SpecialistYieldChanges",
        "BonusYieldModifiers",
        "LocalImprovementCountPrereqs",
        "LocalBonusPrereqs",
        "ConnectedBonusPrereqs",
    ):
        base.empty(node, tag)


def patch_buildings():
    doc = base.parse(BUILDINGS)
    hq_template = base.by_type(doc, "BuildingInfo", "BUILDING_CORPORATION_1")
    house_template = base.by_type(doc, "BuildingInfo", "BUILDING_INDUSTRY_SILVERSMITHS_HALL")
    changed = []
    for guild in GUILDS:
        gid = ids(guild)
        hq = base.ensure(doc, "BuildingInfos", "BuildingInfo", gid["hq"], hq_template)
        reset_building_identity(hq, guild, gid["hq"], gid["hq_class"])
        base.setc(hq, "ArtDefineTag", "ART_DEF_BUILDING_MARKET")
        base.setc(hq, "GreatPeopleUnitClass", f"UNITCLASS_{guild['founder'].replace('UNIT_', '')}")
        base.setc(hq, "iGreatPeopleRateChange", 2)
        base.setc(hq, "bNeverCapture", 1)
        base.build_effects(hq, {"culture": 2, "spec": {guild["specialist"]: 1}}, 2)
        base.flavors(hq, {"FLAVOR_GOLD": 4, "FLAVOR_PRODUCTION": 4, "FLAVOR_CULTURE": 4})

        house = base.ensure(doc, "BuildingInfos", "BuildingInfo", gid["house"], house_template)
        reset_building_identity(house, guild, gid["house"], gid["house_class"])
        base.setc(house, "ArtDefineTag", "ART_DEF_BUILDING_MARKET")
        base.setc(house, "GreatPeopleUnitClass", "NONE")
        base.setc(house, "iGreatPeopleRateChange", 0)
        base.setc(house, "bNeverCapture", 0)
        base.setc(house, "IndustryCategory", "NONE")
        base.setc(house, "bRequiresActiveLocalPrereqs", 0)
        effect = guild["house"]
        base.build_effects(
            house,
            {
                "health": effect["health"],
                "happy": effect["happy"],
                "spec": {guild["specialist"]: 2},
            },
        )
        set_list(house, "YieldChanges", "iYield", effect["yield"], "YieldModifiers")
        set_list(house, "YieldModifiers", "iYield", effect["ymod"], "PowerYieldModifiers")
        set_list(house, "CommerceChanges", "iCommerce", effect["commerce"], "ObsoleteSafeCommerceChanges")
        set_list(house, "CommerceModifiers", "iCommerce", effect["cmod"], "GlobalCommerceModifiers")
        base.setc(house, "iTradeRoutes", effect["routes"])
        base.flavors(house, {"FLAVOR_GOLD": 5, "FLAVOR_PRODUCTION": 5, "FLAVOR_CULTURE": 5})
        changed.extend((gid["hq"], gid["house"]))
    surgical_write(doc, BUILDINGS, "BuildingInfo", tuple(changed), "BuildingInfos")


def patch_unit_classes():
    doc = base.parse(UNIT_CLASSES)
    template = base.by_type(doc, "UnitClassInfo", "UNITCLASS_EXECUTIVE_1")
    changed = []
    for guild in GUILDS:
        gid = ids(guild)
        node = base.ensure(doc, "UnitClassInfos", "UnitClassInfo", gid["unit_class"], template)
        for tag, value in (
            ("Type", gid["unit_class"]),
            ("Description", f"TXT_KEY_{gid['unit']}"),
            ("iMaxGlobalInstances", -1),
            ("iMaxTeamInstances", -1),
            ("iMaxPlayerInstances", -1),
            ("iInstanceCostModifier", 0),
            ("DefaultUnit", gid["unit"]),
        ):
            base.setc(node, tag, value)
        changed.append(gid["unit_class"])
    surgical_write(doc, UNIT_CLASSES, "UnitClassInfo", tuple(changed), "UnitClassInfos")


def patch_unit_art():
    doc = base.parse(UNIT_ART)
    template = base.by_type(doc, "UnitArtInfo", "ART_DEF_UNIT_TRADE_CARAVAN")
    changed = []
    for guild in GUILDS:
        gid = ids(guild)
        node = base.ensure(doc, "UnitArtInfos", "UnitArtInfo", gid["art"], template)
        base.setc(node, "Type", gid["art"])
        base.setc(node, "Button", guild["button"])
        changed.append(gid["art"])
    surgical_write(doc, UNIT_ART, "UnitArtInfo", tuple(changed), "UnitArtInfos")


def patch_units_and_founders():
    doc = base.parse(UNITS)
    template = base.by_type(doc, "UnitInfo", "UNIT_EXECUTIVE_1")
    changed = []
    founder_hqs = {}
    for guild in GUILDS:
        gid = ids(guild)
        founder_hqs.setdefault(guild["founder"], []).append(gid["hq"])
        node = base.ensure(doc, "UnitInfos", "UnitInfo", gid["unit"], template)
        for tag, value in (
            ("Class", gid["unit_class"]),
            ("Type", gid["unit"]),
            ("Special", "NONE"),
            ("Capture", "NONE"),
            ("Combat", "NONE"),
            ("Domain", "DOMAIN_LAND"),
            ("DefaultUnitAI", "UNITAI_MISSIONARY"),
            ("Description", f"TXT_KEY_{gid['unit']}"),
            ("Civilopedia", f"TXT_KEY_{gid['unit']}_PEDIA"),
            ("Strategy", f"TXT_KEY_{gid['unit']}_STRATEGY"),
            ("Advisor", guild["advisor"]),
            ("PrereqReligion", "NONE"),
            ("PrereqCorporation", "NONE"),
            ("PrereqBuilding", gid["hq"]),
            ("PrereqTech", "TECH_GUILDS"),
            ("BonusType", "NONE"),
            ("iAIWeight", 0),
            ("iCost", 100),
            ("iAdvancedStartCost", -1),
            ("iMoves", 2),
            ("iWorkRate", 0),
            ("iBaseDiscover", 0),
            ("iDiscoverMultiplier", 0),
            ("iBaseHurry", 0),
            ("iHurryMultiplier", 0),
            ("iBaseTrade", 0),
            ("iTradeMultiplier", 0),
            ("iGreatWorkCulture", 0),
            ("iEspionagePoints", 0),
            ("iCombat", 0),
            ("iAsset", 2),
            ("iPower", 0),
        ):
            base.setc(node, tag, value)
        for tag in ("UniqueNames", "Builds", "ReligionSpreads", "CorporationSpreads", "GreatPeoples", "Buildings", "ForceBuildings", "TechTypes", "PrereqBonuses", "ProductionTraits", "Flavors"):
            base.empty(node, tag)
        unit_ais = node.ownerDocument.createElement("UnitAIs")
        unit_ai = node.ownerDocument.createElement("UnitAI")
        unit_ai.appendChild(base.mk(node.ownerDocument, "UnitAIType", "UNITAI_MISSIONARY"))
        unit_ai.appendChild(base.mk(node.ownerDocument, "bUnitAI", 1))
        unit_ais.appendChild(unit_ai)
        base.rep(node, unit_ais, "NotUnitAIs")
        meshes = node.ownerDocument.createElement("UnitMeshGroups")
        for tag, value in (("iGroupSize", 1), ("fMaxSpeed", 1.75), ("fPadTime", 1), ("iMeleeWaveSize", 1), ("iRangedWaveSize", 1)):
            meshes.appendChild(base.mk(node.ownerDocument, tag, value))
        mesh = node.ownerDocument.createElement("UnitMeshGroup")
        mesh.appendChild(base.mk(node.ownerDocument, "iRequired", 1))
        mesh.appendChild(base.mk(node.ownerDocument, "EarlyArtDefineTag", gid["art"]))
        meshes.appendChild(mesh)
        base.rep(node, meshes, "FormationType")
        changed.append(gid["unit"])

    for founder, hqs in founder_hqs.items():
        node = base.by_type(doc, "UnitInfo", founder)
        buildings = base.child(node, "Buildings")
        if buildings is None:
            buildings = node.ownerDocument.createElement("Buildings")
            base.rep(node, buildings, "ForceBuildings")
        existing = {
            base.txt(base.child(item, "BuildingType"))
            for item in base.els(buildings, "Building")
            if base.child(item, "BuildingType") is not None
        }
        for hq in hqs:
            if hq in existing:
                continue
            item = node.ownerDocument.createElement("Building")
            item.appendChild(base.mk(node.ownerDocument, "BuildingType", hq))
            item.appendChild(base.mk(node.ownerDocument, "bBuilding", 1))
            buildings.appendChild(item)
        changed.append(founder)
    surgical_write(doc, UNITS, "UnitInfo", tuple(changed), "UnitInfos")


def patch_text():
    entries = ['<?xml version="1.0" encoding="ISO-8859-1"?>\n<Civ4GameText xmlns="http://www.firaxis.com">\n']
    entries.extend(
        (
            text_entry("TXT_KEY_MISSION_ESTABLISH_GUILD_BRANCH", "Establish Guild Branch"),
            text_entry("TXT_KEY_MISSION_ESTABLISH_GUILD_BRANCH_HELP", "Establish this emissary's guild branch in an eligible city."),
            text_entry("TXT_KEY_MISC_GUILD_BRANCH_ESTABLISHED", "%s1 established a branch in %s2."),
            text_entry("TXT_KEY_PEDIA_CATEGORY_GUILD", "Guilds"),
            text_entry("TXT_KEY_POPUP_CHOOSE_GUILD_PROCESSOR", "Choose the processor that will support %s1 in %s2."),
            text_entry("TXT_KEY_POPUP_GUILD_PROCESSOR_OPTION", "%s1 - establishes %s2 (unclaimed)"),
        )
    )
    for guild in GUILDS:
        gid = ids(guild)
        name = guild["name"]
        entries.extend(
            (
                text_entry(f"TXT_KEY_GUILD_{guild['key']}", name),
                text_entry(f"TXT_KEY_GUILD_{guild['key']}_PEDIA", f"{name} is a nationally sponsored guild network founded at Guilds and extended through processor-bound branches."),
                text_entry(f"TXT_KEY_GUILD_{guild['key']}_HELP", "A headquarters may support three total sponsored branches and living emissaries. Branches require an eligible, active, unclaimed local processor."),
                text_entry(f"TXT_KEY_GUILD_{guild['key']}_STRATEGY", "Use scarce emissary licenses on productive processors at home or in trusted Open Borders partners."),
                text_entry(f"TXT_KEY_{gid['hq']}", f"{name} Headquarters"),
                text_entry(f"TXT_KEY_{gid['hq']}_PEDIA", f"The national headquarters of {name}. It issues limited emissary licenses and earns returns from active sponsored branches."),
                text_entry(f"TXT_KEY_{gid['hq']}_STRATEGY", "Founded by the matching Great Person. Provides Culture, Great Person points, one specialist slot, and network returns."),
                text_entry(f"TXT_KEY_{gid['house']}", f"{name} Guild House"),
                text_entry(f"TXT_KEY_{gid['house']}_PEDIA", f"A processor-bound branch of {name}. The house remains visible but loses its benefits while dormant."),
                text_entry(f"TXT_KEY_{gid['house']}_STRATEGY", "Established by a guild emissary in a city with an eligible active processor."),
                text_entry(f"TXT_KEY_{gid['unit']}", f"{name} Emissary"),
                text_entry(f"TXT_KEY_{gid['unit']}_PEDIA", f"An authorized caravan that establishes one {name} Guild House."),
                text_entry(f"TXT_KEY_{gid['unit']}_STRATEGY", "Move to an eligible city and establish a processor-bound guild branch."),
            )
        )
    entries.append("</Civ4GameText>\n")
    TEXT.write_bytes("".join(entries).encode("iso-8859-1"))


def main():
    patch_building_classes()
    patch_buildings()
    patch_unit_classes()
    patch_unit_art()
    patch_units_and_founders()
    patch_text()
    print("Applied guild headquarters, houses, emissaries, art, and text.")


if __name__ == "__main__":
    main()
