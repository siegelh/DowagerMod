from __future__ import annotations

from pathlib import Path
import re
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import apply_supply_chain_overhaul as base


BONUS_INFOS = base.BONP_BTS
BONUS_ART = base.BOAP_BTS
BUILDING_CLASSES = base.BCP
BUILDING_INFOS = base.BP
BUILDING_ART = base.BAP
CORPORATIONS = base.CP
UNIT_INFOS = (
    ROOT
    / "CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Units/CIV4UnitInfos.xml"
)
TEXT = (
    ROOT
    / "CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Text/ZZZZZ_CIV4GameText_GuildArmaments.xml"
)
BUILDING_BUTTONS = (
    ROOT
    / "CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/Art/Interface/Buttons/Buildings/Industries"
)
BONUS_BUTTONS = (
    ROOT
    / "CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/Art/Interface/Buttons/Bonuses/Synthetic"
)

FOOD, PRODUCTION, COMMERCE = 0, 1, 2
GOLD, RESEARCH, CULTURE, ESPIONAGE = 0, 1, 2, 3

BONUSES = (
    {
        "type": "BONUS_FORGED_IRON",
        "name": "Forged Iron",
        "art": "ART_DEF_BONUS_FORGED_IRON",
        "source_art": "ART_DEF_BONUS_IRON",
        "button": "forged_iron.dds",
        "button_source": "worked_silver.dds",
    },
    {
        "type": "BONUS_COPPERWARE",
        "name": "Copperware",
        "art": "ART_DEF_BONUS_COPPERWARE",
        "source_art": "ART_DEF_BONUS_COPPER",
        "button": "copperware.dds",
        "button_source": "gold_bullion.dds",
    },
    {
        "type": "BONUS_TRAINED_MOUNTS",
        "name": "Trained Mounts",
        "art": "ART_DEF_BONUS_TRAINED_MOUNTS",
        "source_art": "ART_DEF_BONUS_HORSE",
        "button": "trained_mounts.dds",
        "button_source": "fine_furs.dds",
    },
)

PROCESSORS = (
    {
        "type": "BUILDING_INDUSTRY_IRON_FOUNDRY",
        "class": "BUILDINGCLASS_INDUSTRY_IRON_FOUNDRY",
        "name": "Iron Foundry",
        "art": "ART_DEF_BUILDING_INDUSTRY_IRON_FOUNDRY",
        "art_source": "ART_DEF_BUILDING_IRONWORKS",
        "button": "iron_foundry.dds",
        "button_source": "minting_house.dds",
        "tech": "TECH_METAL_CASTING",
        "needs": ("BUILDINGCLASS_FORGE",),
        "local": ("BONUS_IRON",),
        "free": "BONUS_FORGED_IRON",
        "food": 0,
        "hammer": 2,
        "gold": 0,
        "health": -1,
        "specialists": {"SPECIALIST_ENGINEER": 1},
        "flavors": {"FLAVOR_PRODUCTION": 9, "FLAVOR_MILITARY": 5},
    },
    {
        "type": "BUILDING_INDUSTRY_COPPERSMITHS_HALL",
        "class": "BUILDINGCLASS_INDUSTRY_COPPERSMITHS_HALL",
        "name": "Coppersmiths' Hall",
        "art": "ART_DEF_BUILDING_INDUSTRY_COPPERSMITHS_HALL",
        "art_source": "ART_DEF_BUILDING_INDUSTRY_SILVERSMITHS_HALL",
        "button": "coppersmiths_hall.dds",
        "button_source": "silversmiths_hall.dds",
        "tech": "TECH_METAL_CASTING",
        "needs": ("BUILDINGCLASS_FORGE",),
        "local": ("BONUS_COPPER",),
        "free": "BONUS_COPPERWARE",
        "food": 0,
        "hammer": 1,
        "gold": 2,
        "health": 0,
        "specialists": {"SPECIALIST_ENGINEER": 1},
        "flavors": {"FLAVOR_PRODUCTION": 7, "FLAVOR_GOLD": 6},
    },
    {
        "type": "BUILDING_INDUSTRY_STUD_FARM",
        "class": "BUILDINGCLASS_INDUSTRY_STUD_FARM",
        "name": "Stud Farm",
        "art": "ART_DEF_BUILDING_INDUSTRY_STUD_FARM",
        "art_source": "ART_DEF_BUILDING_STABLE",
        "button": "stud_farm.dds",
        "button_source": "smokehouse.dds",
        "tech": "TECH_HORSEBACK_RIDING",
        "needs": ("BUILDINGCLASS_STABLE",),
        "local": ("BONUS_HORSE",),
        "free": "BONUS_TRAINED_MOUNTS",
        "food": 1,
        "hammer": 1,
        "gold": 0,
        "health": 1,
        "specialists": {},
        "flavors": {"FLAVOR_MILITARY": 7, "FLAVOR_GROWTH": 5},
    },
)

COMPOSITES = (
    {
        "type": "BUILDING_INDUSTRY_ARSENAL",
        "class": "BUILDINGCLASS_INDUSTRY_ARSENAL",
        "name": "Arsenal",
        "art": "ART_DEF_BUILDING_INDUSTRY_ARSENAL",
        "art_source": "ART_DEF_BUILDING_MILITARY_ACADEMY",
        "button": "arsenal.dds",
        "button_source": "royal_mint.dds",
        "tech": "TECH_STEEL",
        "goods": ("BONUS_FORGED_IRON", "BONUS_COPPERWARE"),
        "hammer": 3,
        "gold": 0,
        "happy": 0,
    },
    {
        "type": "BUILDING_INDUSTRY_REMOUNT_DEPOT",
        "class": "BUILDINGCLASS_INDUSTRY_REMOUNT_DEPOT",
        "name": "Remount Depot",
        "art": "ART_DEF_BUILDING_INDUSTRY_REMOUNT_DEPOT",
        "art_source": "ART_DEF_BUILDING_STABLE",
        "button": "remount_depot.dds",
        "button_source": "victuallers_exchange.dds",
        "tech": "TECH_MILITARY_TRADITION",
        "goods": ("BONUS_FORGED_IRON", "BONUS_TRAINED_MOUNTS"),
        "hammer": 2,
        "gold": 0,
        "happy": 1,
    },
    {
        "type": "BUILDING_INDUSTRY_MILITARY_OUTFITTERS",
        "class": "BUILDINGCLASS_INDUSTRY_MILITARY_OUTFITTERS",
        "name": "Military Outfitters",
        "art": "ART_DEF_BUILDING_INDUSTRY_MILITARY_OUTFITTERS",
        "art_source": "ART_DEF_BUILDING_INDUSTRY_IMPERIAL_OUTFITTERS",
        "button": "military_outfitters.dds",
        "button_source": "imperial_outfitters.dds",
        "tech": "TECH_RIFLING",
        "goods": ("BONUS_COPPERWARE", "BONUS_TRAINED_MOUNTS"),
        "hammer": 2,
        "gold": 2,
        "happy": 0,
    },
)


def surgical_write(doc, path, entry_tag, type_names, container_tag):
    raw = path.read_bytes().decode("utf-8-sig")
    newline = "\r\n" if "\r\n" in raw else "\n"
    raw = raw.replace("\r\n", "\n")
    for type_name in type_names:
        node = base.by_type(doc, entry_tag, type_name)
        fragment = node.toprettyxml(indent="\t")
        fragment = "\n".join(line for line in fragment.splitlines() if line.strip())
        fragment = "\n".join(f"\t{line}" for line in fragment.splitlines()) + "\n"
        pattern = re.compile(
            rf"^[ \t]*<{entry_tag}>(?:(?!</{entry_tag}>).)*?<Type>{re.escape(type_name)}</Type>"
            rf".*?</{entry_tag}>\s*",
            re.DOTALL | re.MULTILINE,
        )
        if pattern.search(raw):
            raw = pattern.sub(fragment, raw, count=1)
        else:
            closing = f"</{container_tag}>"
            if closing not in raw:
                raise ValueError(f"Missing {closing} in {path}")
            raw = raw.replace(closing, fragment + closing, 1)
    path.write_bytes(raw.replace("\n", newline).encode("utf-8"))


def set_list(node, tag, item_tag, values, before=None):
    container = node.ownerDocument.createElement(tag)
    for value in values:
        container.appendChild(base.mk(node.ownerDocument, item_tag, value))
    base.rep(node, container, before)


def copy_buttons():
    for meta in PROCESSORS + COMPOSITES:
        source = BUILDING_BUTTONS / meta["button_source"]
        target = BUILDING_BUTTONS / meta["button"]
        if not source.exists():
            raise FileNotFoundError(source)
        shutil.copy2(source, target)
    for meta in BONUSES:
        source = BONUS_BUTTONS / meta["button_source"]
        target = BONUS_BUTTONS / meta["button"]
        if not source.exists():
            raise FileNotFoundError(source)
        shutil.copy2(source, target)


def patch_bonuses():
    doc = base.parse(BONUS_INFOS)
    template = base.by_type(doc, "BonusInfo", "BONUS_FLOUR")
    for meta in BONUSES:
        node = base.ensure(doc, "BonusInfos", "BonusInfo", meta["type"], template)
        base.setc(node, "Type", meta["type"])
        base.setc(node, "Description", f'TXT_KEY_{meta["type"]}')
        base.setc(node, "Civilopedia", f'TXT_KEY_{meta["type"]}_PEDIA')
        base.setc(node, "BonusClassType", "BONUSCLASS_GENERAL")
        base.setc(node, "ArtDefineTag", meta["art"])
        base.setc(node, "TechReveal", "NONE")
        base.setc(node, "TechCityTrade", "NONE")
        base.setc(node, "TechObsolete", "NONE")
        base.setc(node, "iAITradeModifier", 0)
        base.setc(node, "iAIObjective", 0)
        base.setc(node, "iHealth", 0)
        base.setc(node, "iHappiness", 0)
        base.setc(node, "iPlacementOrder", -1)
        base.setc(node, "iConstAppearance", 0)
        base.setc(node, "iMinAreaSize", -1)
        base.setc(node, "iMinLatitude", 0)
        base.setc(node, "iMaxLatitude", 90)
        base.setc(node, "iPlayer", 0)
        base.setc(node, "iTilesPer", 0)
        base.setc(node, "iMinLandPercent", 0)
        base.setc(node, "iUnique", 0)
        base.setc(node, "iGroupRange", 0)
        base.setc(node, "iGroupRand", 0)
        base.setc(node, "bArea", 0)
        base.setc(node, "bHills", 0)
        base.setc(node, "bFlatlands", 0)
        base.setc(node, "bNoRiverSide", 0)
        base.setc(node, "bNormalize", 0)
        base.empty(node, "YieldChanges", "iAITradeModifier")
        base.empty(node, "TerrainBooleans", "FeatureBooleans")
        base.empty(node, "FeatureBooleans", "FeatureTerrainBooleans")
        base.empty(node, "FeatureTerrainBooleans")
    surgical_write(
        doc,
        BONUS_INFOS,
        "BonusInfo",
        tuple(meta["type"] for meta in BONUSES),
        "BonusInfos",
    )

    doc = base.parse(BONUS_ART)
    for meta in BONUSES:
        source = base.by_type(doc, "BonusArtInfo", meta["source_art"])
        node = base.ensure(doc, "BonusArtInfos", "BonusArtInfo", meta["art"], source)
        base.setc(node, "Type", meta["art"])
        base.setc(node, "Button", f'Art/Interface/Buttons/Bonuses/Synthetic/{meta["button"]}')
    surgical_write(
        doc,
        BONUS_ART,
        "BonusArtInfo",
        tuple(meta["art"] for meta in BONUSES),
        "BonusArtInfos",
    )


def patch_building_classes_and_art():
    doc = base.parse(BUILDING_CLASSES)
    template = base.by_type(doc, "BuildingClassInfo", "BUILDINGCLASS_INDUSTRY_DYE_WORKS")
    for meta in PROCESSORS + COMPOSITES:
        node = base.ensure(doc, "BuildingClassInfos", "BuildingClassInfo", meta["class"], template)
        for tag, value in (
            ("Type", meta["class"]),
            ("Description", f'TXT_KEY_{meta["type"]}'),
            ("iMaxGlobalInstances", -1),
            ("iMaxTeamInstances", -1),
            ("iMaxPlayerInstances", -1),
            ("iExtraPlayerInstances", 0),
            ("bNoLimit", 0),
            ("bMonument", 0),
            ("DefaultBuilding", meta["type"]),
        ):
            base.setc(node, tag, value)
        base.empty(node, "VictoryThresholds")
    surgical_write(
        doc,
        BUILDING_CLASSES,
        "BuildingClassInfo",
        tuple(meta["class"] for meta in PROCESSORS + COMPOSITES),
        "BuildingClassInfos",
    )

    doc = base.parse(BUILDING_ART)
    for meta in PROCESSORS + COMPOSITES:
        source = base.by_type(doc, "BuildingArtInfo", meta["art_source"])
        node = base.ensure(doc, "BuildingArtInfos", "BuildingArtInfo", meta["art"], source)
        base.setc(node, "Type", meta["art"])
        base.setc(node, "Button", f'Art/Interface/Buttons/Buildings/Industries/{meta["button"]}')
    surgical_write(
        doc,
        BUILDING_ART,
        "BuildingArtInfo",
        tuple(meta["art"] for meta in PROCESSORS + COMPOSITES),
        "BuildingArtInfos",
    )


def patch_buildings():
    doc = base.parse(BUILDING_INFOS)
    processor_template = base.by_type(doc, "BuildingInfo", "BUILDING_INDUSTRY_SILVERSMITHS_HALL")
    composite_template = base.by_type(doc, "BuildingInfo", "BUILDING_INDUSTRY_IMPERIAL_OUTFITTERS")

    for meta in PROCESSORS:
        node = base.ensure(doc, "BuildingInfos", "BuildingInfo", meta["type"], processor_template)
        for tag, value in (
            ("BuildingClass", meta["class"]),
            ("Type", meta["type"]),
            ("Description", f'TXT_KEY_{meta["type"]}'),
            ("Civilopedia", f'TXT_KEY_{meta["type"]}_PEDIA'),
            ("Strategy", f'TXT_KEY_{meta["type"]}_STRATEGY'),
            ("Advisor", "ADVISOR_ECONOMY"),
            ("ArtDefineTag", meta["art"]),
            ("PrereqTech", meta["tech"]),
            ("Bonus", "NONE"),
            ("FreeBonus", meta["free"]),
            ("iNumFreeBonuses", 1),
            ("IndustryCategory", "LUXURY"),
            ("bRequiresActiveLocalPrereqs", 1),
            ("iPlayerMaxInstances", 0),
            ("iCost", 120),
            ("iMilitaryProductionModifier", 0),
            ("GreatPeopleUnitClass", "NONE"),
        ):
            base.setc(node, tag, value)
        base.build_effects(
            node,
            {
                "hammer": meta["hammer"],
                "gold": meta["gold"],
                "health": meta["health"],
                "happy": 0,
                "spec": meta["specialists"],
            },
        )
        set_list(node, "YieldChanges", "iYield", (meta["food"], meta["hammer"], 0), "YieldModifiers")
        base.neededs(node, meta["needs"])
        base.empty(node, "LocalImprovementCountPrereqs", "LocalBonusPrereqs")
        base.local_bonus_prereqs(
            node,
            (
                {
                    "bonuses": meta["local"],
                    "min": 1,
                    "improved": 1,
                    "connected": 1,
                    "city": 1,
                },
            ),
        )
        base.connected_bonus_prereqs(node, ())
        base.flavors(node, meta["flavors"])

    for meta in COMPOSITES:
        node = base.ensure(doc, "BuildingInfos", "BuildingInfo", meta["type"], composite_template)
        for tag, value in (
            ("BuildingClass", meta["class"]),
            ("Type", meta["type"]),
            ("Description", f'TXT_KEY_{meta["type"]}'),
            ("Civilopedia", f'TXT_KEY_{meta["type"]}_PEDIA'),
            ("Strategy", f'TXT_KEY_{meta["type"]}_STRATEGY'),
            ("Advisor", "ADVISOR_MILITARY"),
            ("ArtDefineTag", meta["art"]),
            ("PrereqTech", meta["tech"]),
            ("Bonus", "NONE"),
            ("FreeBonus", "NONE"),
            ("iNumFreeBonuses", 0),
            ("IndustryCategory", "COMPOSITE"),
            ("bRequiresActiveLocalPrereqs", 1),
            ("iPlayerMaxInstances", 1),
            ("iCost", 150),
            ("iMilitaryProductionModifier", 10),
            ("GreatPeopleUnitClass", "NONE"),
        ):
            base.setc(node, tag, value)
        base.build_effects(
            node,
            {
                "hammer": meta["hammer"],
                "gold": meta["gold"],
                "health": 0,
                "happy": meta["happy"],
                "spec": {},
            },
        )
        set_list(node, "YieldChanges", "iYield", (0, meta["hammer"], 0), "YieldModifiers")
        base.neededs(node, ())
        base.empty(node, "LocalImprovementCountPrereqs", "LocalBonusPrereqs")
        base.empty(node, "LocalBonusPrereqs", "ConnectedBonusPrereqs")
        base.connected_bonus_prereqs(
            node, tuple({"bonuses": (bonus,), "min": 1} for bonus in meta["goods"])
        )
        base.flavors(node, {"FLAVOR_MILITARY": 9, "FLAVOR_PRODUCTION": 7})

    hq = base.by_type(doc, "BuildingInfo", "BUILDING_CORPORATION_7")
    for tag, value in (
        ("Description", "TXT_KEY_CORPORATION_ROYAL_ARMAMENTS"),
        ("Strategy", "TXT_KEY_BUILDING_ROYAL_ARMAMENTS_STRATEGY"),
        ("PrereqTech", "TECH_RIFLING"),
        ("GreatPeopleUnitClass", "UNITCLASS_ENGINEER"),
        ("FoundsCorporation", "CORPORATION_7"),
        ("GlobalCorporationCommerce", "CORPORATION_7"),
    ):
        base.setc(hq, tag, value)
    surgical_write(
        doc,
        BUILDING_INFOS,
        "BuildingInfo",
        tuple(meta["type"] for meta in PROCESSORS + COMPOSITES) + ("BUILDING_CORPORATION_7",),
        "BuildingInfos",
    )


def patch_corporation_and_executive():
    doc = base.parse(CORPORATIONS)
    node = base.by_type(doc, "CorporationInfo", "CORPORATION_7")
    for tag, value in (
        ("Description", "TXT_KEY_CORPORATION_ROYAL_ARMAMENTS"),
        ("Civilopedia", "TXT_KEY_CORPORATION_ROYAL_ARMAMENTS_PEDIA"),
        ("TechPrereq", "TECH_RIFLING"),
        ("FreeUnitClass", "NONE"),
        ("iSpreadFactor", 170),
        ("iSpreadCost", 60),
        ("iMaintenance", 110),
        ("iFoundingMinActiveBuildingClasses", 3),
        ("bCountDistinctPrereqBonusesOnly", 1),
        ("iMaxPrereqBonusCountPerType", 1),
        ("iMilitaryExperience", 2),
    ):
        base.setc(node, tag, value)
    set_list(
        node,
        "FoundingBuildingClasses",
        "BuildingClassType",
        tuple(meta["class"] for meta in COMPOSITES),
        "PrereqBonuses",
    )
    set_list(
        node,
        "PrereqBonuses",
        "BonusType",
        tuple(meta["type"] for meta in BONUSES),
        "HeadquarterCommerces",
    )
    set_list(node, "HeadquarterCommerces", "iHeadquarterCommerce", (4, 0, 0, 0), "BonusProduced")
    set_list(node, "CommercesProduced", "iCommerceProduced", (0, 0, 0, 0), "YieldsProduced")
    set_list(node, "YieldsProduced", "iYieldProduced", (0, 100, 0), "Button")
    surgical_write(doc, CORPORATIONS, "CorporationInfo", ("CORPORATION_7",), "CorporationInfos")

    doc = base.parse(UNIT_INFOS)
    node = base.by_type(doc, "UnitInfo", "UNIT_EXECUTIVE_7")
    base.setc(node, "Description", "TXT_KEY_UNIT_ROYAL_ARMAMENTS_FACTOR")
    base.setc(node, "PrereqCorporation", "CORPORATION_7")
    base.setc(node, "PrereqTech", "TECH_RIFLING")
    base.setc(node, "iAIWeight", 0)
    base.setc(node, "iCost", 100)
    surgical_write(doc, UNIT_INFOS, "UnitInfo", ("UNIT_EXECUTIVE_7",), "UnitInfos")


def text_entry(tag, english):
    return (
        "\t<TEXT>\n"
        f"\t\t<Tag>{tag}</Tag>\n"
        f"\t\t<English>{english}</English>\n"
        f"\t\t<French>{english}</French>\n"
        f"\t\t<German>{english}</German>\n"
        f"\t\t<Italian>{english}</Italian>\n"
        f"\t\t<Spanish>{english}</Spanish>\n"
        "\t</TEXT>\n"
    )


def patch_text():
    entries = ['<?xml version="1.0" encoding="ISO-8859-1"?>\n<Civ4GameText xmlns="http://www.firaxis.com">\n']
    bonus_text = {
        "BONUS_FORGED_IRON": ("Forged Iron", "Military-grade iron produced by an Iron Foundry."),
        "BONUS_COPPERWARE": ("Copperware", "Worked copper fittings and wares produced by a Coppersmiths' Hall."),
        "BONUS_TRAINED_MOUNTS": ("Trained Mounts", "Selected and trained horses produced by a Stud Farm."),
    }
    for tag, (name, pedia) in bonus_text.items():
        entries.append(text_entry(f"TXT_KEY_{tag}", name))
        entries.append(text_entry(f"TXT_KEY_{tag}_PEDIA", pedia))

    building_text = {
        "BUILDING_INDUSTRY_IRON_FOUNDRY": (
            "Iron Foundry",
            "A forge-centered district that turns local iron into standardized military-grade stock.",
            "Requires a Forge and active local Iron. Produces Forged Iron.",
        ),
        "BUILDING_INDUSTRY_COPPERSMITHS_HALL": (
            "Coppersmiths' Hall",
            "An organized hall of metalworkers producing fittings, vessels, and military hardware.",
            "Requires a Forge and active local Copper. Produces Copperware.",
        ),
        "BUILDING_INDUSTRY_STUD_FARM": (
            "Stud Farm",
            "A controlled breeding and training estate for reliable cavalry mounts.",
            "Requires a Stable and active local Horses. Produces Trained Mounts.",
        ),
        "BUILDING_INDUSTRY_ARSENAL": (
            "Arsenal",
            "A centralized complex for manufacturing and storing standardized arms.",
            "Requires Forged Iron and Copperware. One of three Royal Armaments founding composites.",
        ),
        "BUILDING_INDUSTRY_REMOUNT_DEPOT": (
            "Remount Depot",
            "A military depot combining trained horses with durable forged equipment.",
            "Requires Forged Iron and Trained Mounts. One of three Royal Armaments founding composites.",
        ),
        "BUILDING_INDUSTRY_MILITARY_OUTFITTERS": (
            "Military Outfitters",
            "A coordinated supply market for cavalry fittings, uniforms, and campaign equipment.",
            "Requires Copperware and Trained Mounts. One of three Royal Armaments founding composites.",
        ),
    }
    for tag, (name, pedia, strategy) in building_text.items():
        entries.append(text_entry(f"TXT_KEY_{tag}", name))
        entries.append(text_entry(f"TXT_KEY_{tag}_PEDIA", pedia))
        entries.append(text_entry(f"TXT_KEY_{tag}_STRATEGY", strategy))

    entries.append(text_entry("TXT_KEY_CORPORATION_ROYAL_ARMAMENTS", "Royal Armaments Company"))
    entries.append(
        text_entry(
            "TXT_KEY_CORPORATION_ROYAL_ARMAMENTS_PEDIA",
            "The Royal Armaments Company coordinates arsenals, remount depots, and military outfitters. "
            "Its branches convert Forged Iron, Copperware, and Trained Mounts into production and grant "
            "two experience to combat units trained in the city.",
        )
    )
    entries.append(
        text_entry(
            "TXT_KEY_BUILDING_ROYAL_ARMAMENTS_STRATEGY",
            "Requires an active Arsenal, Remount Depot, and Military Outfitters. Branches gain one "
            "Production from each distinct Armaments input and grant +2 experience to combat units.",
        )
    )
    entries.append(text_entry("TXT_KEY_UNIT_ROYAL_ARMAMENTS_FACTOR", "Royal Armaments Factor"))
    entries.append("</Civ4GameText>\n")
    TEXT.write_bytes("".join(entries).encode("iso-8859-1"))


def main():
    copy_buttons()
    patch_bonuses()
    patch_building_classes_and_art()
    patch_buildings()
    patch_corporation_and_executive()
    patch_text()
    print("Applied guild Armaments content.")


if __name__ == "__main__":
    main()
