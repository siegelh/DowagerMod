#!/usr/bin/env python3
"""Generator for DowagerMod Tier-1 batch 2a quests (13 Ancient + Classical).

Reads the three target XML files, finds the last Blood and Iron block in each,
inserts the new quest blocks immediately after, and writes the files back.

Idempotent: refuses to run if any of the new quest IDs already appears in the file.

Run from repo root:
    python tools\\quests\\_gen_batch_2a.py
"""
from __future__ import print_function
import io
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ASSETS = os.path.join(REPO, "CoreFiles",
                      "Sid Meier's Civilization IV Beyond the Sword",
                      "Beyond the Sword", "Assets")
TRIGGERS = os.path.join(ASSETS, "XML", "Events", "CIV4EventTriggerInfos.xml")
EVENTS   = os.path.join(ASSETS, "XML", "Events", "CIV4EventInfos.xml")
TEXT     = os.path.join(ASSETS, "XML", "Text",   "CIV4GameText_Events_BTS.xml")

T = "\t"  # tab

# ---------------------------------------------------------------------------
# Helpers to emit field blocks in canonical order.
# ---------------------------------------------------------------------------

def listfield(tag, items, child_tag):
    """Emit <tag><child_tag>x</child_tag>...</tag> or self-closing if empty."""
    if not items:
        return "<%s/>" % tag
    inner = "".join("<%s>%s</%s>" % (child_tag, x, child_tag) for x in items)
    return "<%s>%s</%s>" % (tag, inner, tag)

def emit_trigger(q, done=False):
    """Emit a full EventTriggerInfo block with all fields in canonical order."""
    name = q["name"]
    type_ = "EVENTTRIGGER_%s%s" % (name, "_DONE" if done else "")

    if done:
        worldnews = "<WorldNewsTexts><Text>TXT_KEY_EVENTTRIGGER_%s_DONE</Text></WorldNewsTexts>" % name
        triggertext = "TXT_KEY_EVENT_TRIGGER_%s_DONE_1" % name
        ipercent = 100
        iweight = -1
        bGlobal = 1
        bPickPlayer = 0
        bShowPlot = 0
        units = q.get("done_units", [])
        iNumUnits = q.get("done_num_units", 0)
        buildings = q.get("done_buildings", [])
        iNumBuildings = q.get("done_num_buildings", 0)
        iNumBuildingsGlobal = q.get("done_num_buildings_global", 0)
        features = q.get("done_features", [])
        improvements = q.get("done_improvements", [])
        bonuses = q.get("done_bonuses", [])
        routes = q.get("done_routes", [])
        iNumPlotsRequired = q.get("done_num_plots", 0)
        bOwnPlot = q.get("done_own_plot", 0)
        iPlotType = q.get("done_plot_type", -1)
        events = ["EVENT_%s_DONE_%d" % (name, i+1) for i in range(q["num_choices"])]
        prereq_events = ["EVENT_%s_1" % name]
        or_techs = []
        and_techs = []
    else:
        worldnews = "<WorldNewsTexts/>"
        triggertext = "TXT_KEY_EVENT_TRIGGER_%s_1" % name
        ipercent = q["iPercent"]
        iweight = q["iWeight"]
        bGlobal = 0
        bPickPlayer = 1
        bShowPlot = 1
        units = q.get("start_units", [])
        iNumUnits = q.get("start_num_units", 0)
        buildings = q.get("start_buildings", [])
        iNumBuildings = q.get("start_num_buildings", 0)
        iNumBuildingsGlobal = 0
        features = q.get("start_features", [])
        improvements = q.get("start_improvements", [])
        bonuses = q.get("start_bonuses", [])
        routes = q.get("start_routes", [])
        iNumPlotsRequired = q.get("start_num_plots", 0)
        bOwnPlot = q.get("start_own_plot", 0)
        iPlotType = q.get("start_plot_type", -1)
        events = ["EVENT_%s_1" % name]
        prereq_events = []
        or_techs = q.get("or_techs", [])
        and_techs = q.get("and_techs", [])
        if not or_techs and not and_techs:
            or_techs = [q["tech"]]

    iMinPop = q.get("iMinPopulation", 0) if not done else q.get("done_min_pop", 0)

    or_pre = listfield("OrPreReqs", or_techs, "PrereqTech") if or_techs else "<OrPreReqs/>"
    and_pre = listfield("AndPreReqs", and_techs, "PrereqTech") if and_techs else "<AndPreReqs/>"

    lines = [
        T*2 + "<EventTriggerInfo>",
        T*3 + "<Type>%s</Type>" % type_,
        T*3 + worldnews,
        T*3 + "<TriggerTexts>",
        T*4 + "<TriggerText>",
        T*5 + "<Text>%s</Text>" % triggertext,
        T*5 + "<Era>NONE</Era>",
        T*4 + "</TriggerText>",
        T*3 + "</TriggerTexts>",
        T*3 + "<bSinglePlayer>0</bSinglePlayer>",
        T*3 + "<iPercentGamesActive>%d</iPercentGamesActive>" % ipercent,
        T*3 + "<iWeight>%d</iWeight>" % iweight,
        T*3 + "<bProbabilityUnitMultiply>0</bProbabilityUnitMultiply>",
        T*3 + "<bProbabilityBuildingMultiply>0</bProbabilityBuildingMultiply>",
        T*3 + "<Civic>NONE</Civic>",
        T*3 + "<iMinTreasury>0</iMinTreasury>",
        T*3 + "<iMinPopulation>%d</iMinPopulation>" % iMinPop,
        T*3 + "<iMaxPopulation>0</iMaxPopulation>",
        T*3 + "<iMinMapLandmass>0</iMinMapLandmass>",
        T*3 + "<iMinOurLandmass>0</iMinOurLandmass>",
        T*3 + "<iMaxOurLandmass>-1</iMaxOurLandmass>",
        T*3 + "<MinDifficulty>NONE</MinDifficulty>",
        T*3 + "<iAngry>0</iAngry>",
        T*3 + "<iUnhealthy>0</iUnhealthy>",
        T*3 + listfield("UnitsRequired", units, "UnitClass"),
        T*3 + "<iNumUnits>%d</iNumUnits>" % iNumUnits,
        T*3 + "<iNumUnitsGlobal>0</iNumUnitsGlobal>",
        T*3 + "<iUnitDamagedWeight>0</iUnitDamagedWeight>",
        T*3 + "<iUnitDistanceWeight>0</iUnitDistanceWeight>",
        T*3 + "<iUnitExperienceWeight>0</iUnitExperienceWeight>",
        T*3 + "<bUnitsOnPlot>0</bUnitsOnPlot>",
        T*3 + listfield("BuildingsRequired", buildings, "BuildingClass"),
        T*3 + "<iNumBuildings>%d</iNumBuildings>" % iNumBuildings,
        T*3 + "<iNumBuildingsGlobal>%d</iNumBuildingsGlobal>" % iNumBuildingsGlobal,
        T*3 + "<iNumPlotsRequired>%d</iNumPlotsRequired>" % iNumPlotsRequired,
        T*3 + "<bOwnPlot>%d</bOwnPlot>" % bOwnPlot,
        T*3 + "<iPlotType>%d</iPlotType>" % iPlotType,
        T*3 + listfield("FeaturesRequired", features, "FeatureType"),
        T*3 + "<TerrainsRequired/>",
        T*3 + listfield("ImprovementsRequired", improvements, "ImprovementType"),
        T*3 + listfield("BonusesRequired", bonuses, "BonusType"),
        T*3 + listfield("RoutesRequired", routes, "RouteType"),
        T*3 + "<ReligionsRequired/>",
        T*3 + "<iNumReligions>0</iNumReligions>",
        T*3 + "<CorporationsRequired/>",
        T*3 + "<iNumCorporations>0</iNumCorporations>",
        T*3 + "<bPickReligion>0</bPickReligion>",
        T*3 + "<bStateReligion>0</bStateReligion>",
        T*3 + "<bHolyCity>0</bHolyCity>",
        T*3 + "<bPickCorporation>0</bPickCorporation>",
        T*3 + "<bHeadquarters>0</bHeadquarters>",
        T*3 + listfield("Events", events, "Event"),
        T*3 + listfield("PrereqEvents", prereq_events, "Event"),
        T*3 + "<bPrereqEventPlot>0</bPrereqEventPlot>",
        T*3 + or_pre,
        T*3 + and_pre,
        T*3 + "<ObsoleteTechs/>",
        T*3 + "<bRecurring>0</bRecurring>",
        T*3 + "<bTeam>0</bTeam>",
        T*3 + "<bGlobal>%d</bGlobal>" % bGlobal,
        T*3 + "<bPickPlayer>%d</bPickPlayer>" % bPickPlayer,
        T*3 + "<bOtherPlayerWar>0</bOtherPlayerWar>",
        T*3 + "<bOtherPlayerHasReligion>0</bOtherPlayerHasReligion>",
        T*3 + "<bOtherPlayerHasOtherReligion>0</bOtherPlayerHasOtherReligion>",
        T*3 + "<bOtherPlayerAI>0</bOtherPlayerAI>",
        T*3 + "<iOtherPlayerShareBorders>0</iOtherPlayerShareBorders>",
        T*3 + "<OtherPlayerHasTech>NONE</OtherPlayerHasTech>",
        T*3 + "<bPickCity>0</bPickCity>",
        T*3 + "<bPickOtherPlayerCity>0</bPickOtherPlayerCity>",
        T*3 + "<bShowPlot>%d</bShowPlot>" % bShowPlot,
        T*3 + "<iCityFoodWeight>0</iCityFoodWeight>",
        T*3 + "<PythonCanDo/>",
        T*3 + "<PythonCanDoCity/>",
        T*3 + "<PythonCanDoUnit/>",
        T*3 + "<PythonCallback/>",
        T*2 + "</EventTriggerInfo>",
    ]
    return "\n".join(lines)


def emit_event(q, choice=None):
    """Emit a full EventInfo block. choice=None -> start event; int -> done event."""
    name = q["name"]
    if choice is None:
        type_ = "EVENT_%s_1" % name
        desc = "TXT_KEY_EVENT_%s_1" % name
        questfail = "<QuestFailText>TXT_KEY_EVENT_FAIL_%s</QuestFailText>" % name
        bQuest = 1
        bGlobal = 0
        bPickCity = 0
        r = {}
    else:
        type_ = "EVENT_%s_DONE_%d" % (name, choice)
        desc = "TXT_KEY_EVENT_%s_DONE_%d" % (name, choice)
        questfail = "<QuestFailText/>"
        bQuest = 0
        bGlobal = 1
        r = q["choices"][choice-1]
        bPickCity = r.get("pickCity", 0)

    iGold = r.get("iGold", 0)
    iRandomGold = r.get("iRandomGold", 0)
    iCulture = r.get("iCulture", 0)
    iFreeUnitSupport = r.get("iFreeUnitSupport", 0)
    unitClass = r.get("UnitClass", "NONE")
    iNumFreeUnits = r.get("iNumFreeUnits", 0)
    buildingClass = r.get("BuildingClass", "NONE")
    iBuildingChange = r.get("iBuildingChange", 0)
    iHappy = r.get("iHappy", 0)
    iHealth = r.get("iHealth", 0)
    iFood = r.get("iFood", 0)
    iPopulationChange = r.get("iPopulationChange", 0)
    freeSpecBlock = r.get("FreeSpecialistCounts", "<FreeSpecialistCounts/>")
    iEspionagePoints = r.get("iEspionagePoints", 0)

    clear = ""
    if choice is not None:
        clear = (
            "<ClearEvents><EventChance>"
            "<Event>EVENT_%s_1</Event><iEventChance>100</iEventChance>"
            "</EventChance></ClearEvents>" % name
        )
    else:
        clear = "<ClearEvents/>"

    lines = [
        T*2 + "<EventInfo>",
        T*3 + "<Type>%s</Type>" % type_,
        T*3 + "<Description>%s</Description>" % desc,
        T*3 + "<LocalInfoText/>",
        T*3 + "<WorldNewsTexts/>",
        T*3 + "<OtherPlayerPopup/>",
        T*3 + questfail,
        T*3 + "<bQuest>%d</bQuest>" % bQuest,
        T*3 + "<bGlobal>%d</bGlobal>" % bGlobal,
        T*3 + "<bTeam>0</bTeam>",
        T*3 + "<bPickCity>%d</bPickCity>" % bPickCity,
        T*3 + "<bPickOtherPlayerCity>0</bPickOtherPlayerCity>",
        T*3 + "<bDeclareWar>0</bDeclareWar>",
        T*3 + "<iGold>%d</iGold>" % iGold,
        T*3 + "<bGoldToPlayer>0</bGoldToPlayer>",
        T*3 + "<iRandomGold>%d</iRandomGold>" % iRandomGold,
        T*3 + "<iCulture>%d</iCulture>" % iCulture,
        T*3 + "<iEspionagePoints>%d</iEspionagePoints>" % iEspionagePoints,
        T*3 + "<bGoldenAge>0</bGoldenAge>",
        T*3 + "<iFreeUnitSupport>%d</iFreeUnitSupport>" % iFreeUnitSupport,
        T*3 + "<iInflationMod>0</iInflationMod>",
        T*3 + "<iSpaceProductionMod>0</iSpaceProductionMod>",
        T*3 + "<Tech>NONE</Tech>",
        T*3 + "<TechFlavors/>",
        T*3 + "<iTechPercent>0</iTechPercent>",
        T*3 + "<iTechCostPercent>0</iTechCostPercent>",
        T*3 + "<iTechMinTurnsLeft>0</iTechMinTurnsLeft>",
        T*3 + "<PrereqTech>NONE</PrereqTech>",
        T*3 + "<UnitClass>%s</UnitClass>" % unitClass,
        T*3 + "<iNumFreeUnits>%d</iNumFreeUnits>" % iNumFreeUnits,
        T*3 + "<bDisbandUnit>0</bDisbandUnit>",
        T*3 + "<iUnitExperience>0</iUnitExperience>",
        T*3 + "<iUnitImmobileTurns>0</iUnitImmobileTurns>",
        T*3 + "<UnitPromotion/>",
        T*3 + "<UnitName/>",
        T*3 + "<UnitCombatPromotions/>",
        T*3 + "<UnitClassPromotions/>",
        T*3 + "<BuildingClass>%s</BuildingClass>" % buildingClass,
        T*3 + "<iBuildingChange>%d</iBuildingChange>" % iBuildingChange,
        T*3 + "<BuildingExtraYields/>",
        T*3 + "<BuildingExtraCommerces/>",
        T*3 + "<BuildingExtraHappies/>",
        T*3 + "<BuildingExtraHealths/>",
        T*3 + "<iHappy>%d</iHappy>" % iHappy,
        T*3 + "<iHealth>%d</iHealth>" % iHealth,
        T*3 + "<iHurryAnger>0</iHurryAnger>",
        T*3 + "<iHappyTurns>0</iHappyTurns>",
        T*3 + "<iRevoltTurns>0</iRevoltTurns>",
        T*3 + "<iMinPillage>0</iMinPillage>",
        T*3 + "<iMaxPillage>0</iMaxPillage>",
        T*3 + "<iFood>%d</iFood>" % iFood,
        T*3 + "<iFoodPercent>0</iFoodPercent>",
        T*3 + freeSpecBlock,
        T*3 + "<FeatureType>NONE</FeatureType>",
        T*3 + "<iFeatureChange>0</iFeatureChange>",
        T*3 + "<ImprovementType>NONE</ImprovementType>",
        T*3 + "<iImprovementChange>0</iImprovementChange>",
        T*3 + "<BonusType>NONE</BonusType>",
        T*3 + "<iBonusChange>0</iBonusChange>",
        T*3 + "<RouteType>NONE</RouteType>",
        T*3 + "<iRouteChange>0</iRouteChange>",
        T*3 + "<BonusRevealed>NONE</BonusRevealed>",
        T*3 + "<BonusGift>NONE</BonusGift>",
        T*3 + "<PlotExtraYields/>",
        T*3 + "<iConvertOwnCities>0</iConvertOwnCities>",
        T*3 + "<iConvertOtherCities>0</iConvertOtherCities>",
        T*3 + "<iMaxNumReligions>-1</iMaxNumReligions>",
        T*3 + "<iOurAttitudeModifier>0</iOurAttitudeModifier>",
        T*3 + "<iAttitudeModifier>0</iAttitudeModifier>",
        T*3 + "<iTheirEnemyAttitudeModifier>0</iTheirEnemyAttitudeModifier>",
        T*3 + "<iPopulationChange>%d</iPopulationChange>" % iPopulationChange,
        T*3 + "<AdditionalEvents/>",
        T*3 + "<EventTimes/>",
        T*3 + clear,
        T*3 + "<PythonCallback/>",
        T*3 + "<PythonExpireCheck/>",
        T*3 + "<PythonCanDo/>",
        T*3 + "<PythonHelp/>",
        T*3 + "<Button>,Art/Interface/Buttons/Process/Blank.dds,Art/Interface/Buttons/Beyond_the_Sword_Atlas.dds,8,5</Button>",
        T*3 + "<iAIValue>1000</iAIValue>",
        T*2 + "</EventInfo>",
    ]
    return "\n".join(lines)


def emit_text(tag, english):
    return "\n".join([
        T + "<TEXT>",
        T*2 + "<Tag>%s</Tag>" % tag,
        T*2 + "<English>%s</English>" % english,
        T + "</TEXT>",
    ])


# ---------------------------------------------------------------------------
# Quest specs (13 quests)
# ---------------------------------------------------------------------------

# Specialist count XML helper
SCIENTIST_1 = "<FreeSpecialistCounts><FreeSpecialistCount><SpecialistType>SPECIALIST_GREAT_SCIENTIST</SpecialistType><iFreeSpecialistCount>1</iFreeSpecialistCount></FreeSpecialistCount></FreeSpecialistCounts>"
MERCHANT_1 = "<FreeSpecialistCounts><FreeSpecialistCount><SpecialistType>SPECIALIST_GREAT_MERCHANT</SpecialistType><iFreeSpecialistCount>1</iFreeSpecialistCount></FreeSpecialistCount></FreeSpecialistCounts>"
ENGINEER_1 = "<FreeSpecialistCounts><FreeSpecialistCount><SpecialistType>SPECIALIST_GREAT_ENGINEER</SpecialistType><iFreeSpecialistCount>1</iFreeSpecialistCount></FreeSpecialistCount></FreeSpecialistCounts>"
PROPHET_1  = "<FreeSpecialistCounts><FreeSpecialistCount><SpecialistType>SPECIALIST_GREAT_PROPHET</SpecialistType><iFreeSpecialistCount>1</iFreeSpecialistCount></FreeSpecialistCount></FreeSpecialistCounts>"

QUESTS = [
    # 1. Sacred Grove
    {
        "name": "SACRED_GROVE",
        "title": "Sacred Grove",
        "iWeight": 250, "iPercent": 35,
        "tech": "TECH_MYSTICISM",
        "start_buildings": ["BUILDINGCLASS_MONUMENT"], "start_num_buildings": 1,
        "start_features": ["FEATURE_FOREST"], "start_num_plots": 2, "start_own_plot": 1,
        "done_features": ["FEATURE_FOREST"], "done_num_plots": 2, "done_own_plot": 1,
        "num_choices": 3,
        "trigger_start": "The druids speak of an ancient grove whose trees remember our forefathers. If we keep its forests intact for twenty turns, the spirits will bless our people.",
        "trigger_done":  "%s1_CivAdjective has consecrated the Sacred Grove.",
        "trigger_done_1":"The grove has stood untouched for a generation. The spirits offer their blessing. How shall we honor them?",
        "quest":         "Preserve the forests around your capital for twenty turns to complete the Sacred Grove quest.",
        "fail":          "The grove has been felled. The spirits are silent. The Sacred Grove quest is lost.",
        "choices": [
            {"iCulture": 80, "iHappy": 1,
             "label": "Let the groves remain holy. (Receive culture and lasting joy in this city.)",
             "help":  "Your capital receives [COLOR_POSITIVE_TEXT]+80 culture[COLOR_REVERT] and [COLOR_POSITIVE_TEXT]+1 happy[COLOR_REVERT]."},
            {"FreeSpecialistCounts": PROPHET_1,
             "label": "Send pilgrims to learn from the spirits. (Free Great Prophet in capital.)",
             "help":  "Your capital gains [COLOR_POSITIVE_TEXT]a free Great Prophet[COLOR_REVERT]."},
            {"iHappy": 1, "iHealth": 1,
             "label": "Build a shrine among the trees. (+1 happy and +1 health in this city.)",
             "help":  "Your capital gains [COLOR_POSITIVE_TEXT]+1 happy[COLOR_REVERT] and [COLOR_POSITIVE_TEXT]+1 health[COLOR_REVERT]."},
        ],
        # Reward 1 substitution note: "+1 culture per forest worked" → lump culture+happy in this city.
    },
    # 2. Mason's Guild
    {
        "name": "MASONS_GUILD",
        "title": "Mason's Guild",
        "iWeight": 200, "iPercent": 30,
        "tech": "TECH_MASONRY",
        "start_bonuses": ["BONUS_STONE", "BONUS_MARBLE"],
        "start_num_buildings": 0,
        "done_buildings": ["BUILDINGCLASS_WALLS"], "done_num_buildings_global": 3,
        "num_choices": 3,
        "trigger_start": "The stonecutters have organized themselves into a proud guild. They petition us to commission great works of masonry. Build Walls in three cities and they will return the favor.",
        "trigger_done":  "%s1_CivAdjective has founded a great Masons' Guild.",
        "trigger_done_1":"Walls now rise in three of our cities. The masons present themselves to our court. How shall we put their craft to use?",
        "quest":         "Build Walls in three of your cities to complete the Mason's Guild quest.",
        "fail":          "The masons have wandered abroad. The Mason's Guild quest is lost.",
        "choices": [
            {"FreeSpecialistCounts": ENGINEER_1,
             "label": "Set them to work on a great wonder. (Free Great Engineer in capital.)",
             "help":  "Your capital gains [COLOR_POSITIVE_TEXT]a free Great Engineer[COLOR_REVERT] to hurry wonders."},
            {"FreeSpecialistCounts": ENGINEER_1, "iGold": 100,
             "label": "Fund a workshop in the capital. (Free Great Engineer plus 100 gold.)",
             "help":  "Your capital gains [COLOR_POSITIVE_TEXT]a free Great Engineer[COLOR_REVERT] and [COLOR_POSITIVE_TEXT]100 gold[COLOR_REVERT]."},
            {"iCulture": 100, "iHappy": 1,
             "label": "Let the masons carve civic monuments. (+100 culture and +1 happy in this city.)",
             "help":  "Your capital gains [COLOR_POSITIVE_TEXT]+100 culture[COLOR_REVERT] and [COLOR_POSITIVE_TEXT]+1 happy[COLOR_REVERT]."},
        ],
        # Substitutions: "Free Pyramids hammers"/"+25% wonder prod"/"Walls give +1 culture" → Great Engineers and lump culture.
    },
    # 3. Salt Caravan
    {
        "name": "SALT_CARAVAN",
        "title": "Salt Caravan",
        "iWeight": 200, "iPercent": 35,
        "tech": "TECH_POTTERY",
        "start_bonuses": ["BONUS_SALT"], "start_own_plot": 1, "start_num_plots": 1,
        "done_buildings": ["BUILDINGCLASS_MARKET"], "done_num_buildings": 1,
        "done_bonuses": ["BONUS_SALT"],
        "num_choices": 3,
        "trigger_start": "A caravan of salt traders has arrived seeking patronage. If we build a Market in our salt-producing city, they will make our name known across the trade routes.",
        "trigger_done":  "%s1_CivAdjective has founded the great Salt Caravan.",
        "trigger_done_1":"The Market is open and the caravans flow freely. Our salt merchants offer us a share of their profits. How shall we use it?",
        "quest":         "Build a Market in your Salt-producing city to complete the Salt Caravan quest.",
        "fail":          "The caravan has moved on to richer lands. The Salt Caravan quest is lost.",
        "choices": [
            {"iGold": 150,
             "label": "Tax the caravan's profits. (Receive 150 gold.)",
             "help":  "Your treasury gains [COLOR_POSITIVE_TEXT]150 gold[COLOR_REVERT]."},
            {"FreeSpecialistCounts": MERCHANT_1,
             "label": "Bind the merchants to our court. (Free Great Merchant in capital.)",
             "help":  "Your capital gains [COLOR_POSITIVE_TEXT]a free Great Merchant[COLOR_REVERT]."},
            {"iHappy": 1, "iGold": 80,
             "label": "Spice the people's table. (+1 happy in this city and 80 gold.)",
             "help":  "Your capital gains [COLOR_POSITIVE_TEXT]+1 happy[COLOR_REVERT] and [COLOR_POSITIVE_TEXT]80 gold[COLOR_REVERT]."},
        ],
        # Substitutions: "+2 gold per Salt" → 150 gold lump; "Free trade route" → Great Merchant.
    },
    # 4. Hunters' Lodge
    {
        "name": "HUNTERS_LODGE",
        "title": "Hunters' Lodge",
        "iWeight": 200, "iPercent": 35,
        "tech": "TECH_HUNTING",
        "start_bonuses": ["BONUS_DEER", "BONUS_FUR"],
        "start_improvements": ["IMPROVEMENT_CAMP"], "start_own_plot": 1, "start_num_plots": 1,
        "done_buildings": ["BUILDINGCLASS_BARRACKS"], "done_num_buildings_global": 2,
        "num_choices": 3,
        "trigger_start": "Our hunters have built a fine lodge in the wilds. They ask that we raise Barracks in two cities so their sons may train as scouts and archers.",
        "trigger_done":  "%s1_CivAdjective has founded a great Hunters' Lodge.",
        "trigger_done_1":"Two Barracks now stand ready, and the lodge masters present their gifts. How shall we reward our hunters?",
        "quest":         "Build Barracks in two cities to complete the Hunters' Lodge quest.",
        "fail":          "The hunters have abandoned their lodge. The Hunters' Lodge quest is lost.",
        "choices": [
            {"iFood": 20, "iHealth": 1,
             "label": "Stock the city's larders. (Capital gains stored food and +1 health.)",
             "help":  "Your capital gains [COLOR_POSITIVE_TEXT]+20 stored food[COLOR_REVERT] and [COLOR_POSITIVE_TEXT]+1 health[COLOR_REVERT]."},
            {"iHappy": 1,
             "label": "Let the people feast on game and wear fine furs. (+1 happy in this city.)",
             "help":  "Your capital gains [COLOR_POSITIVE_TEXT]+1 happy[COLOR_REVERT]."},
            {"UnitClass": "UNITCLASS_ARCHER", "iNumFreeUnits": 1,
             "label": "Conscript the best hunters as archers. (Free Archer in capital.)",
             "help":  "Your capital gains [COLOR_POSITIVE_TEXT]1 free Archer[COLOR_REVERT]."},
        ],
        # Substitutions: "+1 food per Camp" → stored food + health; "+1 happy from Deer/Fur" → iHappy.
    },
    # 5. Fishing Village
    {
        "name": "FISHING_VILLAGE",
        "title": "Fishing Village",
        "iWeight": 230, "iPercent": 40,
        "tech": "TECH_FISHING",
        "start_bonuses": ["BONUS_FISH", "BONUS_CLAM", "BONUS_CRAB"],
        "start_own_plot": 1, "start_num_plots": 2,
        "done_buildings": ["BUILDINGCLASS_LIGHTHOUSE"], "done_num_buildings": 1,
        "num_choices": 3,
        "trigger_start": "Our fisherfolk speak of bountiful waters. If we raise a Lighthouse to guide them home, they will share their catch with the whole city.",
        "trigger_done":  "%s1_CivAdjective has founded a thriving Fishing Village.",
        "trigger_done_1":"The Lighthouse burns bright, and the boats return laden with the sea's bounty. How shall we share their good fortune?",
        "quest":         "Build a Lighthouse in your coastal capital to complete the Fishing Village quest.",
        "fail":          "The boats have rotted at their moorings. The Fishing Village quest is lost.",
        "choices": [
            {"iFood": 25, "iHealth": 1,
             "label": "Fill the city's nets and granaries. (Capital gains stored food and health.)",
             "help":  "Your capital gains [COLOR_POSITIVE_TEXT]+25 stored food[COLOR_REVERT] and [COLOR_POSITIVE_TEXT]+1 health[COLOR_REVERT]."},
            {"UnitClass": "UNITCLASS_WORKBOAT", "iNumFreeUnits": 1,
             "label": "Commission a new fishing fleet. (Free Work Boat.)",
             "help":  "Your capital gains [COLOR_POSITIVE_TEXT]1 free Work Boat[COLOR_REVERT]."},
            {"FreeSpecialistCounts": MERCHANT_1,
             "label": "Send the catch to distant markets. (Free Great Merchant in capital.)",
             "help":  "Your capital gains [COLOR_POSITIVE_TEXT]a free Great Merchant[COLOR_REVERT]."},
        ],
        # Substitution: "+1 food per ocean tile capital" → stored food + health lump.
    },
    # 6. Pottery Wheel (TWEAKED — cottage focus)
    {
        "name": "POTTERY_WHEEL",
        "title": "Pottery Wheel",
        "iWeight": 240, "iPercent": 40,
        "tech": "TECH_POTTERY",
        "start_improvements": ["IMPROVEMENT_COTTAGE"], "start_own_plot": 1, "start_num_plots": 2,
        "iMinPopulation": 4,
        "done_improvements": ["IMPROVEMENT_COTTAGE"], "done_own_plot": 1, "done_num_plots": 6,
        "num_choices": 3,
        "trigger_start": "Our potters have invented a wheel that quickens their craft. With more Cottages around our capital, this little revolution will spread far. Plant four more Cottages near the capital.",
        "trigger_done":  "%s1_CivAdjective has spread the Pottery Wheel throughout the land.",
        "trigger_done_1":"Cottages now dot the countryside around our capital. The potters offer their wares for our pleasure. How shall we put them to use?",
        "quest":         "Build four more Cottages near your capital to complete the Pottery Wheel quest.",
        "fail":          "The wheel has gone silent. The Pottery Wheel quest is lost.",
        "choices": [
            {"iGold": 120, "iCulture": 40,
             "label": "Tax the cottage trade. (Capital gains gold and culture.)",
             "help":  "Your capital gains [COLOR_POSITIVE_TEXT]120 gold[COLOR_REVERT] and [COLOR_POSITIVE_TEXT]+40 culture[COLOR_REVERT]."},
            {"FreeSpecialistCounts": MERCHANT_1,
             "label": "Send our finest pots to foreign markets. (Free Great Merchant.)",
             "help":  "Your capital gains [COLOR_POSITIVE_TEXT]a free Great Merchant[COLOR_REVERT]."},
            {"FreeSpecialistCounts": MERCHANT_1, "iGold": 80,
             "label": "Bankroll the potters' guild. (Free Great Merchant and 80 gold.)",
             "help":  "Your capital gains [COLOR_POSITIVE_TEXT]a free Great Merchant[COLOR_REVERT] and [COLOR_POSITIVE_TEXT]80 gold[COLOR_REVERT]."},
        ],
        # Substitutions: "+1 commerce per Cottage in city" → gold+culture lump; "Cottages grow 50% faster" → Great Merchant.
    },
    # 7. Wheel of Fortune (TWEAKED — road connectivity)
    {
        "name": "WHEEL_OF_FORTUNE",
        "title": "Wheel of Fortune",
        "iWeight": 220, "iPercent": 35,
        "tech": "TECH_THE_WHEEL",
        "start_routes": ["ROUTE_ROAD"], "start_own_plot": 1, "start_num_plots": 4,
        "done_routes": ["ROUTE_ROAD"], "done_own_plot": 1, "done_num_plots": 8,
        "num_choices": 3,
        "trigger_start": "Our wainwrights demand finer roads. Build more roadways across our lands and the wheels of commerce will sing.",
        "trigger_done":  "%s1_CivAdjective has bound the realm with roads.",
        "trigger_done_1":"The new roads ring with traffic. Trade thrives where wagons may pass. How shall we capitalize on this prosperity?",
        "quest":         "Build at least eight road tiles within your borders to complete the Wheel of Fortune quest.",
        "fail":          "The roads lie unused and overgrown. The Wheel of Fortune quest is lost.",
        "choices": [
            {"iGold": 140, "iCulture": 30,
             "label": "Tax the wagoners. (Capital gains gold and culture.)",
             "help":  "Your capital gains [COLOR_POSITIVE_TEXT]140 gold[COLOR_REVERT] and [COLOR_POSITIVE_TEXT]+30 culture[COLOR_REVERT]."},
            {"UnitClass": "UNITCLASS_WORKER", "iNumFreeUnits": 1,
             "label": "Send forth a new road-crew. (Free Worker.)",
             "help":  "Your capital gains [COLOR_POSITIVE_TEXT]1 free Worker[COLOR_REVERT]."},
            {"FreeSpecialistCounts": MERCHANT_1,
             "label": "Sponsor a great trading house. (Free Great Merchant.)",
             "help":  "Your capital gains [COLOR_POSITIVE_TEXT]a free Great Merchant[COLOR_REVERT]."},
        ],
        # Substitutions: "+1 commerce on all roads"/"+1 trade route capital" → gold lump and Great Merchant.
    },
    # 8. Bread Basket
    {
        "name": "BREAD_BASKET",
        "title": "Bread Basket",
        "iWeight": 200, "iPercent": 40,
        "tech": "TECH_CURRENCY",
        "iMinPopulation": 20,
        "start_buildings": ["BUILDINGCLASS_GRANARY"], "start_num_buildings_global": 0, "start_num_buildings": 3,
        "done_buildings": ["BUILDINGCLASS_GRANARY"], "done_num_buildings_global": 5,
        "num_choices": 3,
        "trigger_start": "Our farmers boast of overflowing granaries. If we raise a Granary in every city, the realm will never want for bread again.",
        "trigger_done":  "%s1_CivAdjective has become a Bread Basket of the world.",
        "trigger_done_1":"Granaries gleam in five cities. The harvest is secure and the people sing. How shall we reward the farmers?",
        "quest":         "Build a Granary in at least five of your cities to complete the Bread Basket quest.",
        "fail":          "The harvest has failed. The Bread Basket quest is lost.",
        "choices": [
            {"iFood": 30, "iHealth": 1,
             "label": "Lay in a great store of grain. (Capital gains stored food and health.)",
             "help":  "Your capital gains [COLOR_POSITIVE_TEXT]+30 stored food[COLOR_REVERT] and [COLOR_POSITIVE_TEXT]+1 health[COLOR_REVERT]."},
            {"BuildingClass": "BUILDINGCLASS_AQUEDUCT", "iBuildingChange": 1,
             "label": "Pipe water to the millers. (Free Aqueduct in capital.)",
             "help":  "Your capital gains [COLOR_POSITIVE_TEXT]a free Aqueduct[COLOR_REVERT]."},
            {"iPopulationChange": 2, "iHealth": 1,
             "label": "Encourage the people to raise families. (Capital grows by 2 population.)",
             "help":  "Your capital gains [COLOR_POSITIVE_TEXT]+2 population[COLOR_REVERT] and [COLOR_POSITIVE_TEXT]+1 health[COLOR_REVERT]."},
        ],
        # Substitutions: "+1 food in all cities" → stored food lump in capital; "pop boom in each city" → +2 pop capital + health.
    },
    # 9. Astronomers of the Plain (TWEAKED)
    {
        "name": "ASTRONOMERS_OF_THE_PLAIN",
        "title": "Astronomers of the Plain",
        "iWeight": 220, "iPercent": 40,
        "tech": "TECH_MATHEMATICS",
        "start_buildings": ["BUILDINGCLASS_LIBRARY"], "start_num_buildings_global": 0, "start_num_buildings": 2,
        "done_buildings": ["BUILDINGCLASS_LIBRARY"], "done_num_buildings_global": 3,
        "num_choices": 3,
        "trigger_start": "Our learned men charted the heavens last night. They beg us to support their work with three Libraries and rooms for their scholars.",
        "trigger_done":  "%s1_CivAdjective has gathered the great Astronomers of the Plain.",
        "trigger_done_1":"The scholars gather to share their findings. Their patrons in the libraries await our decision. How shall we reward them?",
        "quest":         "Have at least three Libraries in your empire to complete the Astronomers of the Plain quest.",
        "fail":          "The scholars have scattered. The Astronomers of the Plain quest is lost.",
        "choices": [
            {"FreeSpecialistCounts": SCIENTIST_1,
             "label": "Found an academy! (Free Great Scientist in capital.)",
             "help":  "Your capital gains [COLOR_POSITIVE_TEXT]a free Great Scientist[COLOR_REVERT] who may settle as an Academy."},
            {"iCulture": 100, "iGold": 80,
             "label": "Publish their treatises. (Capital gains culture and gold.)",
             "help":  "Your capital gains [COLOR_POSITIVE_TEXT]+100 culture[COLOR_REVERT] and [COLOR_POSITIVE_TEXT]80 gold[COLOR_REVERT]."},
            {"FreeSpecialistCounts": SCIENTIST_1, "iCulture": 50,
             "label": "Endow a chair of natural philosophy. (Free Great Scientist plus culture.)",
             "help":  "Your capital gains [COLOR_POSITIVE_TEXT]a free Great Scientist[COLOR_REVERT] and [COLOR_POSITIVE_TEXT]+50 culture[COLOR_REVERT]."},
        ],
        # Substitutions: "+1 science per Scientist specialist" → lump culture+gold; "Free Academy" → Great Scientist (can settle as Academy).
    },
    # 10. Aqueduct Engineers
    {
        "name": "AQUEDUCT_ENGINEERS",
        "title": "Aqueduct Engineers",
        "iWeight": 220, "iPercent": 35,
        "and_techs": ["TECH_MASONRY", "TECH_POTTERY"],
        "iMinPopulation": 8,
        "done_buildings": ["BUILDINGCLASS_AQUEDUCT"], "done_num_buildings_global": 3,
        "num_choices": 3,
        "trigger_start": "Our engineers have mastered the art of stone channels and clay pipes. If we raise Aqueducts in three cities, the realm will know clean water.",
        "trigger_done":  "%s1_CivAdjective has formed a great guild of Aqueduct Engineers.",
        "trigger_done_1":"Aqueducts flow into three cities. The engineers present their plans. How shall we reward their craft?",
        "quest":         "Build Aqueducts in three of your cities to complete the Aqueduct Engineers quest.",
        "fail":          "The aqueducts have crumbled. The Aqueduct Engineers quest is lost.",
        "choices": [
            {"iHealth": 2,
             "label": "Let the people drink deep. (+2 health in this city.)",
             "help":  "Your capital gains [COLOR_POSITIVE_TEXT]+2 health[COLOR_REVERT]."},
            {"FreeSpecialistCounts": ENGINEER_1,
             "label": "Set them to a hanging garden. (Free Great Engineer in capital.)",
             "help":  "Your capital gains [COLOR_POSITIVE_TEXT]a free Great Engineer[COLOR_REVERT] to hurry wonders."},
            {"iFood": 25,
             "label": "Irrigate the city's fields. (Capital gains stored food.)",
             "help":  "Your capital gains [COLOR_POSITIVE_TEXT]+25 stored food[COLOR_REVERT]."},
        ],
        # Substitutions: "+2 health in all Aqueduct cities" → +2 health in capital; "Free Hanging Gardens points" → Great Engineer; "+1 food" → stored food.
    },
    # 11. Census Taker
    {
        "name": "CENSUS_TAKER",
        "title": "Census Taker",
        "iWeight": 200, "iPercent": 30,
        "tech": "TECH_CURRENCY",
        "start_buildings": ["BUILDINGCLASS_COURTHOUSE"], "start_num_buildings_global": 0, "start_num_buildings": 1,
        "done_buildings": ["BUILDINGCLASS_COURTHOUSE"], "done_num_buildings_global": 5,
        "num_choices": 3,
        "trigger_start": "Our magistrates have begun a great census of the realm. With Courthouses in four more cities, our records will be the marvel of the world.",
        "trigger_done":  "%s1_CivAdjective has completed the great Census.",
        "trigger_done_1":"The census is complete and the magistrates kneel before us. How shall we put our newfound knowledge to use?",
        "quest":         "Build Courthouses in at least five of your cities to complete the Census Taker quest.",
        "fail":          "The records have been lost. The Census Taker quest is lost.",
        "choices": [
            {"iGold": 200,
             "label": "Audit the treasury. (Receive 200 gold.)",
             "help":  "Your treasury gains [COLOR_POSITIVE_TEXT]200 gold[COLOR_REVERT]."},
            {"UnitClass": "UNITCLASS_SPY", "iNumFreeUnits": 1,
             "label": "Recruit a master of secrets. (Free Spy in capital.)",
             "help":  "Your capital gains [COLOR_POSITIVE_TEXT]1 free Spy[COLOR_REVERT]."},
            {"iGold": 100, "iEspionagePoints": 50,
             "label": "Bribe the foreign clerks. (100 gold and 50 espionage points.)",
             "help":  "You gain [COLOR_POSITIVE_TEXT]100 gold[COLOR_REVERT] and [COLOR_POSITIVE_TEXT]+50 espionage points[COLOR_REVERT]."},
        ],
        # Substitutions: "-25% maintenance for 30 turns" → 200 gold lump; "+1 commerce per Courthouse" → gold+espionage lump.
    },
    # 12. Mountain Pass
    {
        "name": "MOUNTAIN_PASS",
        "title": "Mountain Pass",
        "iWeight": 170, "iPercent": 25,
        "tech": "TECH_MATHEMATICS",
        "start_plot_type": 1,  # PLOT_HILLS
        "start_num_plots": 3, "start_own_plot": 1,
        "done_improvements": ["IMPROVEMENT_FORT"], "done_own_plot": 1, "done_num_plots": 1,
        "num_choices": 3,
        "trigger_start": "Our scouts have charted a pass through the highlands. If we fortify the road with a Fort, none shall threaten the route.",
        "trigger_done":  "%s1_CivAdjective has secured the great Mountain Pass.",
        "trigger_done_1":"The Fort overlooks the pass and our engineers stand at attention. How shall we make the most of this stronghold?",
        "quest":         "Build a Fort on a hill in your territory to complete the Mountain Pass quest.",
        "fail":          "The pass has been overrun. The Mountain Pass quest is lost.",
        "choices": [
            {"iCulture": 60, "iHappy": 1,
             "label": "Make the highlands a proud frontier. (Capital gains culture and happiness.)",
             "help":  "Your capital gains [COLOR_POSITIVE_TEXT]+60 culture[COLOR_REVERT] and [COLOR_POSITIVE_TEXT]+1 happy[COLOR_REVERT]."},
            {"iGold": 100, "iHealth": 1,
             "label": "Open the pass to merchants. (Capital gains gold and health.)",
             "help":  "Your capital gains [COLOR_POSITIVE_TEXT]100 gold[COLOR_REVERT] and [COLOR_POSITIVE_TEXT]+1 health[COLOR_REVERT]."},
            {"UnitClass": "UNITCLASS_CATAPULT", "iNumFreeUnits": 1,
             "label": "Garrison the Fort with siege engines. (Free Catapult.)",
             "help":  "Your capital gains [COLOR_POSITIVE_TEXT]1 free Catapult[COLOR_REVERT]."},
        ],
        # Substitutions: "+25% defense in hill cities" → culture+happy in capital; "+1 prod on hills" → gold+health lump.
    },
    # 13. Wine Country
    {
        "name": "WINE_COUNTRY",
        "title": "Wine Country",
        "iWeight": 230, "iPercent": 35,
        "tech": "TECH_MONARCHY",
        "start_bonuses": ["BONUS_WINE"],
        "start_improvements": ["IMPROVEMENT_WINERY"], "start_own_plot": 1, "start_num_plots": 1,
        "done_buildings": ["BUILDINGCLASS_MARKET"], "done_num_buildings": 1,
        "done_bonuses": ["BONUS_WINE"],
        "num_choices": 3,
        "trigger_start": "Our vintners have produced a vintage worthy of kings. Build a Market in the Wine city and we shall toast the realm's prosperity.",
        "trigger_done":  "%s1_CivAdjective has founded a renowned Wine Country.",
        "trigger_done_1":"The Market is awash in casks of wine and the merchants stand ready. How shall we share the bounty?",
        "quest":         "Build a Market in your Wine-producing city to complete the Wine Country quest.",
        "fail":          "The vines have withered. The Wine Country quest is lost.",
        "choices": [
            {"iGold": 160,
             "label": "Tax the vintage. (Receive 160 gold.)",
             "help":  "Your treasury gains [COLOR_POSITIVE_TEXT]160 gold[COLOR_REVERT]."},
            {"iHappy": 1,
             "label": "Pour wine for the people. (+1 happy in this city.)",
             "help":  "Your capital gains [COLOR_POSITIVE_TEXT]+1 happy[COLOR_REVERT]."},
            {"FreeSpecialistCounts": MERCHANT_1,
             "label": "Toast a great merchant of wine. (Free Great Merchant in capital.)",
             "help":  "Your capital gains [COLOR_POSITIVE_TEXT]a free Great Merchant[COLOR_REVERT]."},
        ],
        # Substitutions: "+2 gold per Wine" → 160 gold lump; "+1 happy from Wine empire-wide" → iHappy in capital.
    },
]

# ---------------------------------------------------------------------------
# Assemble blocks and patch files
# ---------------------------------------------------------------------------

def build_blocks():
    triggers_xml = []
    events_xml = []
    text_xml = []
    for q in QUESTS:
        triggers_xml.append(emit_trigger(q, done=False))
        triggers_xml.append(emit_trigger(q, done=True))

        events_xml.append(emit_event(q, choice=None))
        for i in range(q["num_choices"]):
            events_xml.append(emit_event(q, choice=i+1))

        n = q["name"]
        text_xml.append(emit_text("TXT_KEY_EVENT_TRIGGER_%s_1" % n, q["trigger_start"]))
        text_xml.append(emit_text("TXT_KEY_EVENTTRIGGER_%s_DONE" % n, q["trigger_done"]))
        text_xml.append(emit_text("TXT_KEY_EVENT_TRIGGER_%s_DONE_1" % n, q["trigger_done_1"]))
        text_xml.append(emit_text("TXT_KEY_EVENT_%s_1" % n, q["title"]))
        text_xml.append(emit_text("TXT_KEY_EVENT_%s_QUEST" % n, q["quest"]))
        text_xml.append(emit_text("TXT_KEY_EVENT_FAIL_%s" % n, q["fail"]))
        for i, c in enumerate(q["choices"], 1):
            text_xml.append(emit_text("TXT_KEY_EVENT_%s_DONE_%d" % (n, i), c["label"]))
            text_xml.append(emit_text("TXT_KEY_EVENT_%s_DONE_%d_HELP" % (n, i), c["help"]))

    return ("\n".join(triggers_xml),
            "\n".join(events_xml),
            "\n".join(text_xml))


def patch_file(path, anchor_line_contains, insertion_block):
    """Insert insertion_block on a new line right AFTER the last line containing anchor."""
    with io.open(path, "r", encoding="utf-8", newline="") as f:
        data = f.read()
    # Use last </EventTriggerInfo> or </EventInfo> closure for the Blood and Iron _DONE block.
    # We anchor by the type string of the LAST Blood and Iron entity in that file
    # then walk to its closing tag.
    idx = data.rfind(anchor_line_contains)
    if idx < 0:
        raise SystemExit("Anchor %r not found in %s" % (anchor_line_contains, path))
    # Find the end of the enclosing block (next "</EventTriggerInfo>" or "</EventInfo>")
    for closer in ("</EventTriggerInfo>", "</EventInfo>", "</TEXT>"):
        end = data.find(closer, idx)
        if end >= 0:
            end += len(closer)
            break
    else:
        raise SystemExit("No closer after anchor in %s" % path)
    # idempotency check: refuse if any new quest IDs already present
    for q in QUESTS:
        marker = "EVENTTRIGGER_%s<" % q["name"]
        if marker in data:
            raise SystemExit("Already patched: %s present in %s" % (marker, path))
    new = data[:end] + "\n" + insertion_block + data[end:]
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(new)


def main():
    trig_blk, evt_blk, txt_blk = build_blocks()

    patch_file(TRIGGERS, "EVENTTRIGGER_BLOOD_AND_IRON_DONE", trig_blk)
    patch_file(EVENTS,   "EVENT_BLOOD_AND_IRON_DONE_3",      evt_blk)
    patch_file(TEXT,     "TXT_KEY_EVENT_BLOOD_AND_IRON_DONE_3_HELP", txt_blk)

    print("Inserted %d quests." % len(QUESTS))


if __name__ == "__main__":
    main()
