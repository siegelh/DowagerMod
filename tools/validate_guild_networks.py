from pathlib import Path
import argparse
import sys
import xml.etree.ElementTree as ET


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

    mission_root = ET.parse(assets / "XML/Units/CIV4MissionInfos.xml").getroot()
    mission_types = {text(node, "Type") for node in elements(mission_root, "MissionInfo")}
    require("MISSION_ESTABLISH_GUILD_BRANCH" in mission_types, "guild mission is not registered in XML", errors)

    city_source = (root / "third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvCity.cpp").read_text(encoding="latin-1")
    player_source = (root / "third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvPlayer.cpp").read_text(encoding="latin-1")
    unit_source = (root / "third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvUnit.cpp").read_text(encoding="latin-1")
    ai_source = (root / "third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvUnitAI.cpp").read_text(encoding="latin-1")
    require("m_paiGuildSponsor" in city_source and "m_paiGuildProcessor" in city_source,
            "city persistence does not include sponsor and processor state", errors)
    require("getNumAvailableGuildLicenses" in player_source and "getNumGuildEmissaries" in player_source,
            "player license accounting is missing", errors)
    require("establishGuildBranch" in unit_source and "MISSION_ESTABLISH_GUILD_BRANCH" in unit_source,
            "unit branch mission implementation is missing", errors)
    require("AI_establishGuildBranch" in ai_source and "ATTITUDE_PLEASED" in ai_source,
            "guild emissary AI or foreign-attitude gate is missing", errors)

    advisor = (assets / "Python/Screens/CvIndustryAdvisor.py").read_text(encoding="utf-8")
    pedia = (assets / "Python/Screens/CvPediaGuild.py").read_text(encoding="utf-8")
    event_manager = (assets / "Python/CvEventManager.py").read_text(encoding="utf-8")
    require("IndustryTabGuilds" in advisor and "drawGuildsTab" in advisor,
            "Industry Advisor Guilds tab is missing", errors)
    require("requestBranchRemoval" in advisor and "CvGuildNetwork" in event_manager,
            "synchronized branch removal wiring is missing", errors)
    require("getNumProcessorBuildingClasses" in pedia and "getLicenseCap" in pedia,
            "guild Civilopedia details are incomplete", errors)

    if errors:
        print(f"[GUILDS] Validation failed with {len(errors)} error(s).")
        for error in errors:
            print(f"  [FAIL] {error}")
        return 1
    print("[GUILDS] Five guilds, native runtime, AI, advisor, Civilopedia, and network actions validated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
