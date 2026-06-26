#!/usr/bin/env python3
# coding: utf-8
"""Generate a comprehensive enumeration of every DowagerMod quest:
   - completion condition
   - each reward choice (label + actual mechanic delivered)

Prints to stdout. Read or redirect to file.
"""
from __future__ import print_function
import os
import re

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ASSETS = os.path.join(
    REPO, "CoreFiles",
    "Sid Meier's Civilization IV Beyond the Sword",
    "Beyond the Sword", "Assets",
)
TRIGS = os.path.join(ASSETS, "XML", "Events", "CIV4EventTriggerInfos.xml")
EVENTS = os.path.join(ASSETS, "XML", "Events", "CIV4EventInfos.xml")
TEXT = os.path.join(ASSETS, "XML", "Text", "CIV4GameText_Events_BTS.xml")
PY = os.path.join(ASSETS, "Python", "EntryPoints", "CvRandomEventInterface.py")


def read(p):
    with open(p, "rb") as f:
        return f.read().decode("utf-8", errors="replace")


def load_text_keys():
    txt = {}
    for m in re.finditer(r"<Tag>(TXT_KEY_[A-Z0-9_]+)</Tag>\s*<English>(.*?)</English>",
                         read(TEXT), re.DOTALL):
        # Strip COLOR/ICON tags for readability
        body = re.sub(r"\[(COLOR_[A-Z_]+|COLOR_REVERT|ICON_[A-Z_]+)\]", "", m.group(2))
        body = re.sub(r"\s+", " ", body).strip()
        txt[m.group(1)] = body
    return txt


def load_dispatch_dicts():
    p = read(PY)
    specs = {}
    bldgs = {}
    for m in re.finditer(r'\t"(EVENT_[A-Z0-9_]+)": "(SPECIALIST_[A-Z_]+)",', p):
        specs[m.group(1)] = m.group(2).replace("SPECIALIST_GREAT_", "Great ").replace("_", " ").title()
    for m in re.finditer(r'\t"(EVENT_[A-Z0-9_]+)": "(BUILDINGCLASS_[A-Z_]+)",', p):
        bldgs[m.group(1)] = m.group(2).replace("BUILDINGCLASS_", "").replace("_", " ").title()
    return specs, bldgs


def parse_event_block(text, evt_type):
    marker = "<Type>" + evt_type + "</Type>"
    idx = text.find(marker)
    if idx == -1:
        return None
    open_tag = text.rfind("<EventInfo>", 0, idx)
    close_tag = text.find("</EventInfo>", idx)
    if open_tag == -1 or close_tag == -1:
        return None
    return text[open_tag + len("<EventInfo>"):close_tag]


def parse_trigger_block(text, trig_type):
    marker = "<Type>" + trig_type + "</Type>"
    idx = text.find(marker)
    if idx == -1:
        return None
    open_tag = text.rfind("<EventTriggerInfo>", 0, idx)
    close_tag = text.find("</EventTriggerInfo>", idx)
    if open_tag == -1 or close_tag == -1:
        return None
    return text[open_tag + len("<EventTriggerInfo>"):close_tag]


def extract_int(block, field, default=0):
    m = re.search(r"<" + field + r">(-?\d+)</" + field + r">", block)
    return int(m.group(1)) if m else default


def extract_str(block, field, default=""):
    m = re.search(r"<" + field + r">([^<]*)</" + field + r">", block)
    return m.group(1).strip() if m else default


def extract_list(block, parent, child):
    """E.g. ('BuildingsRequired', 'BuildingClass') -> list of strings."""
    pm = re.search(r"<" + parent + r">(.*?)</" + parent + r">", block, re.DOTALL)
    if not pm:
        return []
    return re.findall(r"<" + child + r">([^<]+)</" + child + r">", pm.group(1))


def describe_trigger_conditions(block):
    parts = []
    # Tech prereqs
    or_techs = extract_list(block, "OrPreReqs", "PrereqTech")
    and_techs = extract_list(block, "AndPreReqs", "PrereqTech")
    if or_techs:
        parts.append("Tech: " + " OR ".join(t.replace("TECH_", "").replace("_", " ").title() for t in or_techs))
    if and_techs:
        parts.append("AND tech: " + " AND ".join(t.replace("TECH_", "").replace("_", " ").title() for t in and_techs))
    # Civic
    civic = extract_str(block, "Civic", "NONE")
    if civic != "NONE":
        parts.append("Civic: " + civic.replace("CIVIC_", "").replace("_", " ").title())
    # Buildings
    bldgs = extract_list(block, "BuildingsRequired", "BuildingClass")
    nb = extract_int(block, "iNumBuildings")
    if bldgs:
        bs = "/".join(b.replace("BUILDINGCLASS_", "").replace("_", " ").title() for b in bldgs)
        parts.append("%d %s" % (nb, bs) if nb else "Any %s" % bs)
    # Units
    units = extract_list(block, "UnitsRequired", "UnitClass")
    nu = extract_int(block, "iNumUnits")
    if units:
        us = "/".join(u.replace("UNITCLASS_", "").replace("_", " ").title() for u in units)
        parts.append("%d %s" % (nu, us) if nu else "Any %s" % us)
    # Bonuses
    bonuses = extract_list(block, "BonusesRequired", "BonusType")
    if bonuses:
        bs = "/".join(b.replace("BONUS_", "").replace("_", " ").title() for b in bonuses)
        parts.append("Resource: " + bs)
    # Improvements
    imps = extract_list(block, "ImprovementsRequired", "ImprovementType")
    np = extract_int(block, "iNumPlotsRequired")
    if imps:
        ims = "/".join(i.replace("IMPROVEMENT_", "").replace("_", " ").title() for i in imps)
        parts.append("%d %s plot(s)" % (np, ims) if np else "Any %s plot" % ims)
    # Treasury
    tr = extract_int(block, "iMinTreasury")
    if tr > 0:
        parts.append("Treasury >= %d" % tr)
    # State religion etc.
    if extract_int(block, "bStateReligion") == 1:
        parts.append("State religion active")
    if extract_int(block, "bHolyCity") == 1:
        parts.append("Own Holy City")
    # Other-player constraints
    if extract_int(block, "bOtherPlayerWar") == 1:
        parts.append("At war with another civ")
    if extract_int(block, "bOtherPlayerHasOtherReligion") == 1:
        parts.append("Other civ has different religion")
    if extract_int(block, "iOtherPlayerShareBorders") == 1:
        parts.append("Shares borders with another civ")
    # Python gate
    pcd = extract_str(block, "PythonCanDo")
    if pcd:
        parts.append("Python gate: %s" % pcd)
    return parts


def describe_event_reward(block, event_type, txt, spec_dict, bldg_dict):
    parts = []
    # Gold
    g = extract_int(block, "iGold")
    if g > 0:
        parts.append("+%d gold" % g)
    rg = extract_int(block, "iRandomGold")
    if rg > 0:
        parts.append("up to +%d random gold" % rg)
    # Happy / Health / Culture / Food / Pop / Espionage / GoldenAge
    for fld, label in [("iHappy", "happy"), ("iHealth", "health"),
                        ("iCulture", "culture"), ("iFood", "food"),
                        ("iEspionagePoints", "espionage"),
                        ("iFreeUnitSupport", "free unit support"),
                        ("iPopulationChange", "population")]:
        v = extract_int(block, fld)
        if v != 0:
            parts.append("+%d %s" % (v, label) if v > 0 else "%d %s" % (v, label))
    if extract_int(block, "bGoldenAge") == 1:
        parts.append("Golden Age")
    # Tech beakers
    t = extract_str(block, "Tech", "NONE")
    tp = extract_int(block, "iTechPercent")
    if t != "NONE" and tp > 0:
        parts.append("%d%% beakers toward %s" % (tp, t.replace("TECH_", "").title()))
    # Free unit
    uc = extract_str(block, "UnitClass", "NONE")
    nfree = extract_int(block, "iNumFreeUnits")
    if uc != "NONE" and nfree > 0:
        parts.append("Free %dx %s" % (nfree, uc.replace("UNITCLASS_", "").replace("_", " ").title()))
    # Free building
    bc = extract_str(block, "BuildingClass", "NONE")
    bchg = extract_int(block, "iBuildingChange")
    if bc != "NONE" and bchg > 0:
        parts.append("Free %s" % bc.replace("BUILDINGCLASS_", "").replace("_", " ").title())
    # FreeSpecialistCounts (XML, rare)
    spec_xml = re.search(r"<FreeSpecialistCount>\s*<SpecialistType>([^<]+)</SpecialistType>", block)
    if spec_xml:
        parts.append("XML specialist: %s" % spec_xml.group(1))
    # UnitCombatPromotions
    for m in re.finditer(r"<UnitCombat>UNITCOMBAT_([^<]+)</UnitCombat>\s*<UnitPromotion>PROMOTION_([^<]+)</UnitPromotion>", block):
        parts.append("%s units get %s" % (m.group(1).title(), m.group(2).replace("_", " ").title()))
    # BuildingExtraYields/Commerces/Happies/Healths
    for m in re.finditer(r"<BuildingExtraYield>\s*<BuildingClass>BUILDINGCLASS_([^<]+)</BuildingClass>\s*<YieldType>YIELD_([^<]+)</YieldType>\s*<iExtraYield>(-?\d+)</iExtraYield>", block):
        parts.append("Every %s +%s %s" % (m.group(1).title().replace("_", " "), m.group(3), m.group(2).lower()))
    for m in re.finditer(r"<BuildingExtraCommerce>\s*<BuildingClass>BUILDINGCLASS_([^<]+)</BuildingClass>\s*<CommerceType>COMMERCE_([^<]+)</CommerceType>\s*<iExtraCommerce>(-?\d+)</iExtraCommerce>", block):
        parts.append("Every %s +%s %s" % (m.group(1).title().replace("_", " "), m.group(3), m.group(2).lower()))
    for m in re.finditer(r"<BuildingExtraHappy>\s*<BuildingClass>BUILDINGCLASS_([^<]+)</BuildingClass>\s*<iExtraHappy>(-?\d+)</iExtraHappy>", block):
        parts.append("Every %s +%s happy" % (m.group(1).title().replace("_", " "), m.group(2)))
    for m in re.finditer(r"<BuildingExtraHealth>\s*<BuildingClass>BUILDINGCLASS_([^<]+)</BuildingClass>\s*<iExtraHealth>(-?\d+)</iExtraHealth>", block):
        parts.append("Every %s +%s health" % (m.group(1).title().replace("_", " "), m.group(2)))
    # Python callbacks
    pcb = extract_str(block, "PythonCallback")
    if pcb == "applyDowagerCapitalSpecialist" and event_type in spec_dict:
        parts.append("Settled %s in capital" % spec_dict[event_type])
    elif pcb == "applyDowagerCapitalFreeBuilding" and event_type in bldg_dict:
        parts.append("Free %s in capital" % bldg_dict[event_type])
    elif pcb and pcb.startswith("applyEvent"):
        # Bespoke Tier 2 callback
        parts.append("Python: %s" % pcb)
    return parts


def main():
    txt = load_text_keys()
    spec_dict, bldg_dict = load_dispatch_dicts()
    trigs_data = read(TRIGS)
    events_data = read(EVENTS)

    quest_names = [
        # Tier 1 Ancient/Classical
        "BLOOD_AND_IRON", "SACRED_GROVE", "MASONS_GUILD", "SALT_CARAVAN",
        "HUNTERS_LODGE", "FISHING_VILLAGE", "POTTERY_WHEEL", "WHEEL_OF_FORTUNE",
        "BREAD_BASKET", "ASTRONOMERS_OF_THE_PLAIN", "AQUEDUCT_ENGINEERS",
        "CENSUS_TAKER", "MOUNTAIN_PASS", "WINE_COUNTRY",
        # Tier 1 Medieval/Renaissance
        "CATHEDRAL_BUILDERS", "FEUDAL_LEVY", "PILGRIMS_PATH", "ROYAL_FALCONRY",
        "CATHEDRAL_CHOIR", "TOURNAMENT_GROUNDS", "GOLDSMITHS_GUILD",
        "CRUSADERS_RETURN", "PRINTING_PRESS_BOOM", "ROYAL_NAVY",
        "NAVAL_DRYDOCKS", "WHALERS_FLEET", "COFFEE_HOUSES",
        # Tier 1 Industrial/Modern
        "IRON_HORSE", "MASS_PRODUCTION", "LOCOMOTIVE_WORKS",
        "TELEGRAPH_NETWORK", "COAL_COUNTRY", "PROPAGANDA_MACHINE",
        # Tier 2 batch 3a
        "GOLD_FEVER", "BORDER_DISPUTE", "GREAT_FAMINE", "ROAD_NETWORK",
        "MERCANTILISM", "PAX_ROMANA", "SILK_ROAD",
        # Tier 2 batch 3b
        "SPICE_MERCHANT", "STOIC_ACADEMY", "MASTER_BREWER", "OIL_BARON",
        "JOINT_STOCK_COMPANY", "TULIP_MANIA", "WORKER_SAFETY",
    ]

    print("# DowagerMod Quest Enumeration (%d quests)\n" % len(quest_names))

    tier_headers = {
        0: "## Tier 1 — Ancient / Classical (14 quests)",
        14: "## Tier 1 — Medieval / Renaissance (13 quests)",
        27: "## Tier 1 — Industrial / Modern (6 quests)",
        33: "## Tier 2 — Early/Mid Era (XML+Python, 7 quests)",
        40: "## Tier 2 — Late Era (XML+Python, 7 quests)",
    }

    for i, qname in enumerate(quest_names):
        if i in tier_headers:
            print("\n" + tier_headers[i] + "\n")

        start_trig = parse_trigger_block(trigs_data, "EVENTTRIGGER_" + qname)
        done_trig = parse_trigger_block(trigs_data, "EVENTTRIGGER_" + qname + "_DONE")
        if not start_trig or not done_trig:
            print("### %s\n(missing data)\n" % qname)
            continue

        print("### %s" % qname.replace("_", " ").title())
        # Start prereqs
        sp = describe_trigger_conditions(start_trig)
        print("- **Start prereqs**: " + ("; ".join(sp) if sp else "none"))
        # Done completion check
        dc = describe_trigger_conditions(done_trig)
        print("- **Completion condition**: " + ("; ".join(dc) if dc else "fires immediately when start prereqs hold"))
        # Each reward choice
        for n in range(1, 4):
            done_evt_type = "EVENT_%s_DONE_%d" % (qname, n)
            done_block = parse_event_block(events_data, done_evt_type)
            if not done_block:
                continue
            label = txt.get("TXT_KEY_" + done_evt_type, "(missing label)")
            reward = describe_event_reward(done_block, done_evt_type, txt, spec_dict, bldg_dict)
            reward_str = "; ".join(reward) if reward else "**NO REWARD DETECTED**"
            print("- **Choice %d**: %s" % (n, label))
            print("    - Delivers: %s" % reward_str)
        print()


if __name__ == "__main__":
    main()
