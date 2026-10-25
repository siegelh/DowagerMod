from pathlib import Path
import argparse
import re
import sys
import xml.etree.ElementTree as ET


LEGACY_MISSION_TYPES = (
    "MISSION_MOVE_TO",
    "MISSION_ROUTE_TO",
    "MISSION_MOVE_TO_UNIT",
    "MISSION_SKIP",
    "MISSION_SLEEP",
    "MISSION_FORTIFY",
    "MISSION_PLUNDER",
    "MISSION_AIRPATROL",
    "MISSION_SEAPATROL",
    "MISSION_HEAL",
    "MISSION_SENTRY",
    "MISSION_AIRLIFT",
    "MISSION_NUKE",
    "MISSION_RECON",
    "MISSION_PARADROP",
    "MISSION_AIRBOMB",
    "MISSION_RANGE_ATTACK",
    "MISSION_BOMBARD",
    "MISSION_PILLAGE",
    "MISSION_SABOTAGE",
    "MISSION_DESTROY",
    "MISSION_STEAL_PLANS",
    "MISSION_FOUND",
    "MISSION_SPREAD",
    "MISSION_SPREAD_CORPORATION",
    "MISSION_JOIN",
    "MISSION_CONSTRUCT",
    "MISSION_DISCOVER",
    "MISSION_HURRY",
    "MISSION_TRADE",
    "MISSION_GREAT_WORK",
    "MISSION_INFILTRATE",
    "MISSION_GOLDEN_AGE",
    "MISSION_BUILD",
    "MISSION_LEAD",
    "MISSION_ESPIONAGE",
    "MISSION_DIE_ANIMATION",
    "MISSION_BEGIN_COMBAT",
    "MISSION_END_COMBAT",
    "MISSION_AIRSTRIKE",
    "MISSION_SURRENDER",
    "MISSION_CAPTURED",
    "MISSION_IDLE",
    "MISSION_DIE",
    "MISSION_DAMAGE",
    "MISSION_MULTI_SELECT",
    "MISSION_MULTI_DESELECT",
)
GUILD_MISSION_TYPE = "MISSION_ESTABLISH_GUILD_BRANCH"
EXPECTED_CIVILOPEDIA_PAGE_TYPES = (
    "CIVILOPEDIA_PAGE_TECH",
    "CIVILOPEDIA_PAGE_UNIT",
    "CIVILOPEDIA_PAGE_BUILDING",
    "CIVILOPEDIA_PAGE_WONDER",
    "CIVILOPEDIA_PAGE_TERRAIN",
    "CIVILOPEDIA_PAGE_FEATURE",
    "CIVILOPEDIA_PAGE_BONUS",
    "CIVILOPEDIA_PAGE_IMPROVEMENT",
    "CIVILOPEDIA_PAGE_SPECIALIST",
    "CIVILOPEDIA_PAGE_PROMOTION",
    "CIVILOPEDIA_PAGE_UNIT_GROUP",
    "CIVILOPEDIA_PAGE_CIV",
    "CIVILOPEDIA_PAGE_LEADER",
    "CIVILOPEDIA_PAGE_RELIGION",
    "CIVILOPEDIA_PAGE_CORPORATION",
    "CIVILOPEDIA_PAGE_CIVIC",
    "CIVILOPEDIA_PAGE_PROJECT",
    "CIVILOPEDIA_PAGE_CONCEPT",
    "CIVILOPEDIA_PAGE_CONCEPT_NEW",
    "CIVILOPEDIA_PAGE_HINTS",
    "CIVILOPEDIA_PAGE_GUILD",
)


def text(node, name):
    for child in node:
        if child.tag.rsplit("}", 1)[-1] == name:
            return "" if child.text is None else child.text.strip()
    return ""


def elements(node, name):
    return [child for child in node.iter() if child.tag.rsplit("}", 1)[-1] == name]


def require(condition, message, errors):
    if not condition:
        errors.append(message)


def by_type(root, element_name):
    return {text(node, "Type"): node for node in elements(root, element_name)}


def nested_text(node, name):
    matches = elements(node, name)
    if not matches or matches[0].text is None:
        return ""
    return matches[0].text.strip()


def resolve_asset(assets, path):
    relative = path.lstrip(",").replace("\\", "/")
    roots = (
        assets,
        assets.parent.parent / "Assets",
        assets.parent.parent / "Warlords/Assets",
    )
    for asset_root in roots:
        candidate = asset_root / relative
        if candidate.is_file():
            return candidate
    return None


def validate_nif_textures(assets, nif_path, errors):
    texture_refs = {
        match.decode("latin-1").replace("\\", "/")
        for match in re.findall(rb"[A-Za-z0-9_./\\ ()-]{1,180}\.dds", nif_path.read_bytes(), re.I)
    }
    for texture_ref in sorted(texture_refs):
        candidates = (
            nif_path.parent / texture_ref,
            nif_path.parent / Path(texture_ref).name,
            assets / "Art/Caveman2Cosmos/art/shared" / Path(texture_ref).name,
            assets / "Art/Caveman2Cosmos/art/shared/Environment_FX" / Path(texture_ref).name,
            assets / "Art/Structures/Cities" / Path(texture_ref).name,
        )
        require(any(candidate.is_file() for candidate in candidates),
                f"{nif_path}: missing nested texture {texture_ref}", errors)


def mission_enum_types(enums_source):
    match = re.search(
        r"enum\s+MissionTypes\b.*?\{(?P<body>.*?)\n\};",
        enums_source,
        re.S,
    )
    if match is None:
        return ()
    return tuple(re.findall(r"^\s*(MISSION_[A-Z0-9_]+)\s*,", match.group("body"), re.M))


def enum_types(enums_source, enum_name, prefix):
    match = re.search(
        r"enum\s+%s\b.*?\{(?P<body>.*?)\n\};" % re.escape(enum_name),
        enums_source,
        re.S,
    )
    if match is None:
        return ()
    return tuple(re.findall(
        r"^\s*(%s[A-Z0-9_]+)\s*(?:=[^,]+)?," % re.escape(prefix),
        match.group("body"),
        re.M,
    ))


def cpp_function(source, signature, next_signature):
    start = source.find(signature)
    end = source.find(next_signature, start)
    if start < 0 or end <= start:
        return ""
    return source[start:end]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.repo_root.resolve()
    assets = root / "CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets"
    errors = []

    guild_path = assets / "XML/GameInfo/CIV4GuildInfo.xml"
    guild_root = ET.parse(guild_path).getroot()
    guilds = elements(guild_root, "GuildInfo")
    require(len(guilds) == 5, "expected exactly five guild definitions", errors)

    expected_text_header = b'<?xml version="1.0" encoding="ISO-8859-1"?>'
    expected_text_root = b'<Civ4GameText xmlns="http://www.firaxis.com">'
    for filename in (
        "ZZZZZ_CIV4GameText_GuildArmaments.xml",
        "ZZZZZ_CIV4GameText_GuildNetworks.xml",
    ):
        text_path = assets / "XML/Text" / filename
        raw_text = text_path.read_bytes()
        require(raw_text.startswith(expected_text_header),
                f"{filename}: must use Civ IV's ISO-8859-1 text encoding", errors)
        require(expected_text_root in raw_text,
                f"{filename}: must use Civ IV's Firaxis game-text namespace", errors)
        try:
            ET.parse(text_path)
        except ET.ParseError as exc:
            errors.append(f"{filename}: malformed XML: {exc}")

    guild_types = set()
    for guild in guilds:
        guild_type = text(guild, "Type")
        require(guild_type and guild_type not in guild_types, "guild types must be unique", errors)
        guild_types.add(guild_type)
        require(text(guild, "iLicenseCap") == "3", f"{guild_type}: license cap must be 3", errors)
        require(text(guild, "HeadquartersBuildingClass"), f"{guild_type}: missing headquarters class", errors)
        require(text(guild, "HouseBuildingClass"), f"{guild_type}: missing house class", errors)
        require(text(guild, "EmissaryUnitClass"), f"{guild_type}: missing emissary class", errors)
        require(len(elements(guild, "ProcessorBuildingClass")) > 0,
                f"{guild_type}: must define at least one processor", errors)

    guild_keys = (
        "ARTIFICERS",
        "MERCHANT_ADVENTURERS",
        "APOTHECARIES",
        "VICTUALLERS",
        "PAGEANTRY",
    )
    expected_building_art = {
        "ART_DEF_BUILDING_GUILD_ARTIFICERS_HEADQUARTERS": (
            "Art/Caveman2Cosmos/art/structures/buildings/leonardo/leonardo.nif",
            "Art/Caveman2Cosmos/art/interface/buttons/national_wonders/blacksmith_guild.dds",
        ),
        "ART_DEF_BUILDING_GUILD_ARTIFICERS_HOUSE": (
            "Art/Caveman2Cosmos/art/structures/buildings/wheelwright/wheelwrightb.nif",
            "Art/Caveman2Cosmos/art/interface/buttons/buildings/wheelwright.dds",
        ),
        "ART_DEF_BUILDING_GUILD_MERCHANT_ADVENTURERS_HEADQUARTERS": (
            "Art/Caveman2Cosmos/art/structures/buildings/agora/agora.nif",
            "Art/Caveman2Cosmos/art/interface/buttons/national_wonders/mercers_guild.dds",
        ),
        "ART_DEF_BUILDING_GUILD_MERCHANT_ADVENTURERS_HOUSE": (
            "Art/Caveman2Cosmos/art/structures/buildings/caravanpost/tradingpost.nif",
            "Art/Caveman2Cosmos/art/interface/buttons/buildings/caravanpost.dds",
        ),
        "ART_DEF_BUILDING_GUILD_APOTHECARIES_HEADQUARTERS": (
            "Art/Caveman2Cosmos/art/structures/buildings/granary/greco_roman_granary/alchemist.nif",
            "Art/Caveman2Cosmos/art/interface/buttons/national_wonders/apothecary_guild.dds",
        ),
        "ART_DEF_BUILDING_GUILD_APOTHECARIES_HOUSE": (
            "Art/Caveman2Cosmos/art/structures/buildings/apothecary/apothecary.nif",
            "Art/Caveman2Cosmos/art/interface/buttons/buildings/apothecary_shop_button.dds",
        ),
        "ART_DEF_BUILDING_GUILD_VICTUALLERS_HEADQUARTERS": (
            "Art/Caveman2Cosmos/art/structures/buildings/tavern/tavern.nif",
            "Art/Caveman2Cosmos/art/interface/buttons/national_wonders/victuallers_guild.dds",
        ),
        "ART_DEF_BUILDING_GUILD_VICTUALLERS_HOUSE": (
            "Art/Caveman2Cosmos/art/structures/buildings/gambling_house/grocery.nif",
            "Art/Caveman2Cosmos/art/interface/buttons/buildings/tavern.dds",
        ),
        "ART_DEF_BUILDING_GUILD_PAGEANTRY_HEADQUARTERS": (
            "Art/Caveman2Cosmos/art/structures/buildings/festival/circus.nif",
            "Art/Caveman2Cosmos/art/interface/buttons/national_wonders/artist_guild.dds",
        ),
        "ART_DEF_BUILDING_GUILD_PAGEANTRY_HOUSE": (
            "Art/Caveman2Cosmos/art/structures/buildings/carnival/fest_mid_tentbig.nif",
            "Art/Caveman2Cosmos/art/interface/buttons/buildings/carnival.dds",
        ),
    }
    building_root = ET.parse(assets / "XML/Buildings/CIV4BuildingInfos.xml").getroot()
    building_infos = by_type(building_root, "BuildingInfo")
    building_art_root = ET.parse(assets / "XML/Art/CIV4ArtDefines_Building.xml").getroot()
    building_art_infos = by_type(building_art_root, "BuildingArtInfo")
    guild_art_tags = []
    guild_buttons = []
    for key in guild_keys:
        for suffix in ("HEADQUARTERS", "HOUSE"):
            building_type = f"BUILDING_GUILD_{key}_{suffix}"
            art_type = f"ART_DEF_BUILDING_GUILD_{key}_{suffix}"
            require(building_type in building_infos, f"{building_type}: building definition missing", errors)
            if building_type in building_infos:
                actual_art = text(building_infos[building_type], "ArtDefineTag")
                require(actual_art == art_type,
                        f"{building_type}: expected {art_type}, found {actual_art}", errors)
                require(actual_art != "ART_DEF_BUILDING_MARKET",
                        f"{building_type}: must not reuse the market art definition", errors)
                guild_art_tags.append(actual_art)
            require(art_type in building_art_infos, f"{art_type}: building art definition missing", errors)
            if art_type not in building_art_infos:
                continue
            art_info = building_art_infos[art_type]
            expected_model, expected_button = expected_building_art[art_type]
            actual_model = text(art_info, "NIF")
            actual_button = text(art_info, "Button")
            require(actual_model == expected_model,
                    f"{art_type}: expected model {expected_model}, found {actual_model}", errors)
            require(actual_button == expected_button,
                    f"{art_type}: expected button {expected_button}, found {actual_button}", errors)
            guild_buttons.append(actual_button)
            model_path = resolve_asset(assets, actual_model)
            button_path = resolve_asset(assets, actual_button)
            require(model_path is not None, f"{art_type}: missing model {actual_model}", errors)
            require(button_path is not None, f"{art_type}: missing button {actual_button}", errors)
            if model_path is not None:
                validate_nif_textures(assets, model_path, errors)
    require(len(set(guild_art_tags)) == 10, "guild buildings must use ten distinct art tags", errors)
    require(len(set(guild_buttons)) == 10, "guild buildings must use ten distinct buttons", errors)

    unit_art_root = ET.parse(assets / "XML/Art/CIV4ArtDefines_Unit.xml").getroot()
    unit_art_infos = by_type(unit_art_root, "UnitArtInfo")
    expected_caravan_nif = "Art/Caveman2Cosmos/art/units/caravan/caravan_base.nif"
    expected_caravan_kfm = "Art/Caveman2Cosmos/art/units/caravan/caravan_base.kfm"
    expected_shadow = "Art/Units/01_UnitShadows/UnitShadow.nif"
    for key in guild_keys:
        art_type = f"ART_DEF_UNIT_GUILD_{key}_EMISSARY"
        require(art_type in unit_art_infos, f"{art_type}: emissary art definition missing", errors)
        if art_type not in unit_art_infos:
            continue
        art_info = unit_art_infos[art_type]
        require(text(art_info, "NIF") == expected_caravan_nif,
                f"{art_type}: must use the safe base caravan NIF", errors)
        require(text(art_info, "KFM") == expected_caravan_kfm,
                f"{art_type}: must use the base caravan KFM", errors)
        require(text(art_info, "SHADERNIF") == expected_caravan_nif,
                f"{art_type}: shader fallback must use the safe base caravan NIF", errors)
        require(nested_text(art_info, "ShadowNIF") == expected_shadow,
                f"{art_type}: must use the stock unit shadow", errors)
        require(not elements(art_info, "TrailDefinition"),
                f"{art_type}: must not inherit a wheel trail", errors)
        require(text(art_info, "fScale") == "0.216",
                f"{art_type}: world scale must match the source caravan at 0.216", errors)
        require(resolve_asset(assets, text(art_info, "NIF")) is not None,
                f"{art_type}: caravan NIF is missing", errors)
        require(resolve_asset(assets, text(art_info, "KFM")) is not None,
                f"{art_type}: caravan KFM is missing", errors)
    caravan_path = resolve_asset(assets, expected_caravan_nif)
    if caravan_path is not None:
        validate_nif_textures(assets, caravan_path, errors)

    mission_root = ET.parse(assets / "XML/Units/CIV4MissionInfos.xml").getroot()
    mission_types = tuple(text(node, "Type") for node in elements(mission_root, "MissionInfo"))
    expected_mission_types = LEGACY_MISSION_TYPES + (GUILD_MISSION_TYPE,)
    require(
        mission_types == expected_mission_types,
        "mission XML must preserve all legacy numeric IDs and append the Guild mission",
        errors,
    )

    city_source = (root / "third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvCity.cpp").read_text(encoding="latin-1")
    player_source = (root / "third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvPlayer.cpp").read_text(encoding="latin-1")
    unit_source = (root / "third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvUnit.cpp").read_text(encoding="latin-1")
    ai_source = (root / "third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvUnitAI.cpp").read_text(encoding="latin-1")
    selection_source = (root / "third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvSelectionGroup.cpp").read_text(encoding="latin-1")
    popup_source = (root / "third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvDLLButtonPopup.cpp").read_text(encoding="latin-1")
    enums_source = (root / "third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvEnums.h").read_text(encoding="latin-1")
    enum_bindings_source = (root / "third_party/beyond-the-sword-sdk/CvGameCoreDLL/CyEnumsInterface.cpp").read_text(encoding="latin-1")
    widget_source = (root / "third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvDLLWidgetData.cpp").read_text(encoding="latin-1")
    require(
        mission_enum_types(enums_source) == expected_mission_types,
        "CvEnums.h must preserve all legacy mission IDs and append the Guild mission",
        errors,
    )
    require(
        enum_types(enums_source, "CivilopediaPageTypes", "CIVILOPEDIA_PAGE_")
        == EXPECTED_CIVILOPEDIA_PAGE_TYPES,
        "CvEnums.h must preserve all legacy Civilopedia page IDs and append the Guild page",
        errors,
    )
    widget_types = enum_types(enums_source, "WidgetTypes", "WIDGET_")
    require(
        widget_types.count("WIDGET_PEDIA_JUMP_TO_GUILD") == 1
        and widget_types[-1:] == ("WIDGET_PEDIA_JUMP_TO_GUILD",),
        "WIDGET_PEDIA_JUMP_TO_GUILD must be the final appended widget",
        errors,
    )
    popup_types = enum_types(enums_source, "ButtonPopupTypes", "BUTTONPOPUP_")
    require(
        popup_types.count("BUTTONPOPUP_CHOOSE_GUILD_PROCESSOR") == 1
        and popup_types[-1:] == ("BUTTONPOPUP_CHOOSE_GUILD_PROCESSOR",),
        "BUTTONPOPUP_CHOOSE_GUILD_PROCESSOR must be the final appended popup",
        errors,
    )
    require('value("CIVILOPEDIA_PAGE_GUILD", CIVILOPEDIA_PAGE_GUILD)' in enum_bindings_source,
            "Guild Civilopedia page is not exposed to Python", errors)
    require("m_paiGuildSponsor" in city_source and "m_paiGuildProcessor" in city_source,
            "city persistence does not include sponsor and processor state", errors)
    require("getNumAvailableGuildLicenses" in player_source and "getNumGuildEmissaries" in player_source,
            "player license accounting is missing", errors)
    require("establishGuildBranch" in unit_source and "MISSION_ESTABLISH_GUILD_BRANCH" in unit_source,
            "unit branch mission implementation is missing", errors)
    require("AI_establishGuildBranch" in ai_source and "ATTITUDE_PLEASED" in ai_source,
            "guild emissary AI or foreign-attitude gate is missing", errors)
    require("BUTTONPOPUP_CHOOSE_GUILD_PROCESSOR" in selection_source
            and "BUTTONPOPUP_CHOOSE_GUILD_PROCESSOR" in popup_source
            and "sendPushMission" in popup_source,
            "synchronized human processor selection popup is missing", errors)
    require(enums_source.count("WIDGET_PEDIA_JUMP_TO_GUILD") == 1,
            "native Guild Civilopedia widget enum is missing or duplicated", errors)
    require('value("WIDGET_PEDIA_JUMP_TO_GUILD", WIDGET_PEDIA_JUMP_TO_GUILD)' in enum_bindings_source,
            "Guild Civilopedia widget is not exposed to Python", errors)
    require("doPediaGuildJump" in widget_source
            and '"pediaJumpToGuild"' in widget_source
            and "parsePediaJumpToGuildHelp" in widget_source,
            "native Guild Civilopedia click/help routing is incomplete", errors)
    require("enum GuildBranchRejectionTypes" in enums_source
            and "GUILD_BRANCH_REJECTION_INACTIVE_PROCESSOR" in enums_source
            and "GUILD_BRANCH_REJECTION_CLAIMED_PROCESSOR" in enums_source,
            "ordered native Guild establishment rejection reasons are missing", errors)
    city_header = (root / "third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvCity.h").read_text(encoding="latin-1")
    require("GuildBranchRejectionTypes getGuildBranchRejection" in city_header
            and "CvCity::getGuildBranchRejection" in city_source
            and "getGuildBranchRejection(eGuild, eSponsor, eProcessor) == NO_GUILD_BRANCH_REJECTION" in city_source,
            "Guild branch legality must delegate to one rejection evaluator", errors)
    require("if (bTestVisible)" in unit_source
            and "return true;" in unit_source
            and "canEstablishGuildBranch(eGuild, getOwnerINLINE(), eProcessor, bTestVisible)" in unit_source,
            "Guild mission visibility must remain broad while execution uses native legality", errors)
    require("getGuildBranchRejection" in widget_source
            and "TXT_KEY_GUILD_BRANCH_REJECTION_INACTIVE_PROCESSOR" in widget_source
            and "TXT_KEY_GUILD_BRANCH_REJECTION_CLAIMED_PROCESSOR" in widget_source,
            "Guild action help must report establishment rejection reasons", errors)

    acquire_city = cpp_function(
        player_source,
        "void CvPlayer::acquireCity(",
        "void CvPlayer::killCities()",
    )
    building_loop = acquire_city.find(
        "for (int iBuilding = 0; iBuilding < GC.getNumBuildingInfos(); ++iBuilding)"
    )
    restore_block = acquire_city.find("restoreGuildBranchState")
    refresh_block = acquire_city.find("CvCity::refreshAllGuildBranches();")
    require(building_loop >= 0,
            "city acquisition must use a dedicated building-loop index", errors)
    require(acquire_city.count("CvCity::refreshAllGuildBranches();") == 1,
            "city acquisition must refresh Guild networks exactly once", errors)
    require(restore_block > building_loop and refresh_block > restore_block,
            "Guild transfer finalization must follow building reconstruction", errors)
    require("for (int iI = 0; iI < GC.getNumBuildingInfos(); iI++)" not in acquire_city,
            "city acquisition must not reuse the legacy building-loop index", errors)

    advisor = (assets / "Python/Screens/CvIndustryAdvisor.py").read_text(encoding="utf-8")
    pedia = (assets / "Python/Screens/CvPediaGuild.py").read_text(encoding="utf-8")
    pedia_main = (assets / "Python/Screens/CvPediaMain.py").read_text(encoding="utf-8")
    screens_interface = (assets / "Python/EntryPoints/CvScreensInterface.py").read_text(encoding="utf-8")
    event_manager = (assets / "Python/CvEventManager.py").read_text(encoding="utf-8")
    require("IndustryTabGuilds" in advisor and "drawGuildsTab" in advisor,
            "Industry Advisor Guilds tab is missing", errors)
    require("requestBranchRemoval" in advisor and "CvGuildNetwork" in event_manager,
            "synchronized branch removal wiring is missing", errors)
    require("getNumProcessorBuildingClasses" in pedia and "getLicenseCap" in pedia,
            "guild Civilopedia details are incomplete", errors)
    require("WidgetTypes.WIDGET_PEDIA_JUMP_TO_GUILD" in pedia_main
            and "WidgetTypes.WIDGET_PEDIA_JUMP_TO_GUILD" in pedia,
            "Guild Civilopedia rows and sidebar must use the native Guild widget", errors)
    require('CvUtil.pyPrint("[GUILDS] Civilopedia received zero Guild infos from the DLL")' in pedia_main
            and "TXT_KEY_PEDIA_GUILD_DATA_UNAVAILABLE" in pedia_main,
            "Guild Civilopedia must report a zero-info DLL/XML contract failure", errors)
    require("def pediaJumpToGuild(argsList):" in screens_interface
            and "pediaMainScreen.pediaJump(PEDIA_GUILD" in screens_interface,
            "Guild Civilopedia screen entrypoint is missing", errors)
    require("self.szGuildTable" not in pedia_main,
            "obsolete custom Guild category click routing remains", errors)
    require("NOTIFY_LISTBOX_ITEM_SELECTED" not in pedia,
            "obsolete custom Guild sidebar click routing remains", errors)

    if errors:
        print(f"[GUILDS] Validation failed with {len(errors)} error(s).")
        for error in errors:
            print(f"  [FAIL] {error}")
        return 1
    print("[GUILDS] Five guilds, native runtime, clickable Civilopedia, distinct art, AI, advisor, and network actions validated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
