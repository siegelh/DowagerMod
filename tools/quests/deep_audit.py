#!/usr/bin/env python3
# coding: utf-8
"""Deep structural audit of every DowagerMod quest XML entry.

Parses each <EventTriggerInfo> and <EventInfo> in our section. For each one,
extracts every field and reports:

  - Field counts and which non-default fields are present
  - Cross-references between triggers, events, callbacks, and text keys
  - Anomalies: any field that contradicts engine semantics

Goal: find every bug in the 22k lines without literally reading each one,
by encoding what we know about correct quest structure as rules.

Run from worktree root:
    python tools\\quests\\deep_audit.py > tools\\quests\\_audit_report.txt
"""
from __future__ import print_function
import os
import re
import sys
import xml.etree.ElementTree as ET

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

DOWAGER_TRIG_MARKER = "EVENTTRIGGER_BLOOD_AND_IRON"
DOWAGER_EVT_MARKER = "EVENT_BLOOD_AND_IRON_1"


def parse_xml(path):
    with open(path, "rb") as f:
        data = f.read()
    # Civ4 XML uses default namespace; strip it for simpler ET access.
    text = data.decode("utf-8", errors="replace")
    text = re.sub(r' xmlns="[^"]+"', "", text, count=1)
    return ET.fromstring(text)


def child_text(elem, name, default=""):
    c = elem.find(name)
    if c is None or c.text is None:
        return default
    return c.text.strip()


def child_int(elem, name, default=0):
    t = child_text(elem, name, "")
    if not t:
        return default
    try:
        return int(t)
    except ValueError:
        return default


def has_children(elem, name):
    c = elem.find(name)
    if c is None:
        return False
    return len(list(c)) > 0


def child_strs(elem, name, tag):
    """Return list of <tag>text</tag> child texts under <name>."""
    c = elem.find(name)
    if c is None:
        return []
    return [t.text.strip() for t in c.findall(tag) if t.text]


def collect_text_keys(path):
    keys = set()
    bodies = {}
    with open(path, "rb") as f:
        data = f.read().decode("utf-8", errors="replace")
    for m in re.finditer(r"<Tag>(TXT_KEY_[A-Z0-9_]+)</Tag>\s*<English>(.*?)</English>",
                         data, re.DOTALL):
        keys.add(m.group(1))
        bodies[m.group(1)] = m.group(2).strip()
    return keys, bodies


def collect_callback_names(path):
    """Return set of function names defined in the Python file."""
    funcs = set()
    with open(path, "rb") as f:
        for line in f:
            m = re.match(rb"^def (\w+)\(", line)
            if m:
                funcs.add(m.group(1).decode())
    return funcs


def main():
    print("=== Deep XML audit ===")
    text_keys, _ = collect_text_keys(TEXT)
    py_funcs = collect_callback_names(PY)
    print("Text keys defined:    %d" % len(text_keys))
    print("Python functions:     %d" % len(py_funcs))

    # Build set of all valid event types defined in our XML (for chain validation)
    evts_root = parse_xml(EVENTS)
    trigs_root = parse_xml(TRIGS)

    all_event_types = set()
    all_trigger_types = set()
    event_objs = {}
    trigger_objs = {}
    for ei in evts_root.iter("EventInfo"):
        t = child_text(ei, "Type")
        if t:
            all_event_types.add(t)
            event_objs[t] = ei
    for ti in trigs_root.iter("EventTriggerInfo"):
        t = child_text(ti, "Type")
        if t:
            all_trigger_types.add(t)
            trigger_objs[t] = ti

    # Identify DowagerMod entries
    dowager_events = [t for t in all_event_types if any(
        t.startswith("EVENT_" + n + "_") or t == "EVENT_" + n + "_1"
        for n in [])]  # we'll do this differently
    # Instead: take every event whose Type appears at-or-after the BLOOD_AND_IRON marker.
    with open(EVENTS, "rb") as f:
        edata = f.read().decode("utf-8", errors="replace")
    boundary_e = edata.find(DOWAGER_EVT_MARKER)
    dowager_event_types = []
    for m in re.finditer(r"<Type>(EVENT_[A-Z0-9_]+)</Type>", edata):
        if m.start() >= boundary_e - 100:  # account for the surrounding <EventInfo>
            dowager_event_types.append(m.group(1))

    with open(TRIGS, "rb") as f:
        tdata = f.read().decode("utf-8", errors="replace")
    boundary_t = tdata.find(DOWAGER_TRIG_MARKER)
    dowager_trigger_types = []
    for m in re.finditer(r"<Type>(EVENTTRIGGER_[A-Z0-9_]+)</Type>", tdata):
        if m.start() >= boundary_t - 100:
            dowager_trigger_types.append(m.group(1))

    print("DowagerMod triggers:  %d" % len(dowager_trigger_types))
    print("DowagerMod events:    %d" % len(dowager_event_types))
    print()

    errors = []
    warnings = []
    info = []

    # ============================================================
    # Audit each DowagerMod TRIGGER
    # ============================================================
    for tname in dowager_trigger_types:
        trig = trigger_objs[tname]
        is_done = tname.endswith("_DONE")

        # --- iWeight semantics
        iw = child_int(trig, "iWeight", 0)
        if is_done:
            if iw != -1:
                errors.append("%s: done trigger has iWeight=%d (must be -1 for auto-fire)" % (tname, iw))
        else:
            if iw <= 0:
                errors.append("%s: start trigger has iWeight=%d (must be > 0 to enter lottery; -1 would be illegal here)" % (tname, iw))

        # --- iPercentGamesActive
        ipga = child_int(trig, "iPercentGamesActive", 0)
        if is_done:
            if ipga != 100:
                warnings.append("%s: done trigger iPercentGamesActive=%d (vanilla pattern is 100)" % (tname, ipga))
        else:
            if ipga < 0 or ipga > 100:
                errors.append("%s: iPercentGamesActive=%d out of range" % (tname, ipga))

        # --- bGlobal: vanilla pattern is bGlobal=1 on done, bGlobal=0 on start
        bglobal = child_int(trig, "bGlobal", 0)
        if is_done:
            if bglobal != 1:
                errors.append("%s: done trigger bGlobal=%d (must be 1 per vanilla pattern; affects PrereqEvents scoping)" % (tname, bglobal))
        else:
            if bglobal != 0:
                warnings.append("%s: start trigger bGlobal=%d (vanilla pattern is 0)" % (tname, bglobal))

        # --- bSinglePlayer
        bsp = child_int(trig, "bSinglePlayer", 0)
        if bsp != 0:
            warnings.append("%s: bSinglePlayer=%d (MP players won't see this quest)" % (tname, bsp))

        # --- bPickPlayer semantics
        bpp = child_int(trig, "bPickPlayer", 0)
        if bpp == 1:
            # Must have an other-player constraint
            constraints = (
                child_int(trig, "bOtherPlayerWar", 0)
                + child_int(trig, "bOtherPlayerHasReligion", 0)
                + child_int(trig, "bOtherPlayerHasOtherReligion", 0)
                + child_int(trig, "bOtherPlayerAI", 0)
                + child_int(trig, "iOtherPlayerShareBorders", 0)
            )
            if constraints == 0:
                errors.append("%s: bPickPlayer=1 but no other-player constraints (silent skip)" % tname)

        # --- PrereqEvents on done triggers must reference real events
        if is_done:
            prereqs = child_strs(trig, "PrereqEvents", "Event")
            if not prereqs:
                errors.append("%s: done trigger has no PrereqEvents (will never recognize its quest's start event)" % tname)
            for ev in prereqs:
                if ev not in all_event_types:
                    errors.append("%s: PrereqEvents references undefined event: %s" % (tname, ev))

        # --- <Events> list must reference real events
        events_listed = child_strs(trig, "Events", "Event")
        if not events_listed:
            errors.append("%s: has no <Events> (won't fire anything)" % tname)
        for ev in events_listed:
            if ev not in all_event_types:
                errors.append("%s: <Events> references undefined event: %s" % (tname, ev))

        # --- iNum* sanity for done triggers
        if is_done:
            has_bldgs_req = has_children(trig, "BuildingsRequired")
            has_units_req = has_children(trig, "UnitsRequired")
            has_imps_req = has_children(trig, "ImprovementsRequired")
            inb = child_int(trig, "iNumBuildings", 0)
            inu = child_int(trig, "iNumUnits", 0)
            inp = child_int(trig, "iNumPlotsRequired", 0)
            py_can_do = child_text(trig, "PythonCanDo", "")

            # The classic auto-complete trap: required types present but iNum=0
            if has_bldgs_req and inb == 0 and not py_can_do:
                errors.append("%s: BuildingsRequired set but iNumBuildings=0 and no PythonCanDo (auto-completes)" % tname)
            if has_units_req and inu == 0 and not py_can_do:
                errors.append("%s: UnitsRequired set but iNumUnits=0 and no PythonCanDo (auto-completes)" % tname)
            if has_imps_req and inp == 0 and not py_can_do:
                errors.append("%s: ImprovementsRequired set but iNumPlotsRequired=0 and no PythonCanDo (auto-completes)" % tname)

            # No completion check at all
            if (not has_bldgs_req and not has_units_req and not has_imps_req
                and not py_can_do and child_int(trig, "iMinTreasury", 0) == 0
                and child_int(trig, "iMinPopulation", 0) == 0
                and child_text(trig, "Civic", "NONE") == "NONE"
                and child_int(trig, "iNumReligions", 0) == 0
                and child_int(trig, "iNumCorporations", 0) == 0):
                warnings.append("%s: done trigger has no completion checks (will fire next turn after start)" % tname)

        # --- PythonCanDo points to a function that exists
        py_can_do = child_text(trig, "PythonCanDo", "")
        if py_can_do and py_can_do not in py_funcs:
            errors.append("%s: PythonCanDo references missing function: %s" % (tname, py_can_do))

        # --- Text key references
        for txt in child_strs(trig, "WorldNewsTexts", "Text"):
            if txt not in text_keys:
                errors.append("%s: WorldNewsTexts references missing TXT_KEY: %s" % (tname, txt))
        for tt in trig.findall("TriggerTexts/TriggerText/Text"):
            if tt.text and tt.text.strip() not in text_keys:
                errors.append("%s: TriggerTexts references missing TXT_KEY: %s" % (tname, tt.text.strip()))

    # ============================================================
    # Audit each DowagerMod EVENT
    # ============================================================
    for ename in dowager_event_types:
        evt = event_objs[ename]
        is_done = "_DONE_" in ename
        is_start = ename.endswith("_1") and not is_done

        # --- Required fields
        desc = child_text(evt, "Description", "")
        if not desc:
            errors.append("%s: missing Description" % ename)
        elif desc not in text_keys:
            errors.append("%s: Description references missing TXT_KEY: %s" % (ename, desc))

        # --- bQuest semantics
        bq = child_int(evt, "bQuest", 0)
        if is_start and bq != 1:
            errors.append("%s: start event bQuest=%d (must be 1 to register as quest)" % (ename, bq))
        if is_done and bq != 0:
            errors.append("%s: done event bQuest=%d (must be 0)" % (ename, bq))

        # --- QuestFailText
        qft = child_text(evt, "QuestFailText", "")
        if is_start and not qft:
            warnings.append("%s: start event has no QuestFailText (no message on quest fail)" % ename)
        if qft and qft not in text_keys:
            errors.append("%s: QuestFailText references missing TXT_KEY: %s" % (ename, qft))

        # --- bPickCity semantics for city-targeted rewards
        bpc = child_int(evt, "bPickCity", 0)
        has_free_spec = has_children(evt, "FreeSpecialistCounts")
        bldg_class = child_text(evt, "BuildingClass", "NONE")
        bldg_change = child_int(evt, "iBuildingChange", 0)
        py_cb = child_text(evt, "PythonCallback", "")

        if has_free_spec and bpc != 1 and not py_cb:
            errors.append("%s: FreeSpecialistCounts present, bPickCity=0, no PythonCallback (silently dropped)" % ename)
        if bldg_class != "NONE" and bldg_change > 0 and bpc != 1 and not py_cb:
            errors.append("%s: BuildingClass+iBuildingChange present, bPickCity=0, no PythonCallback (silently dropped)" % ename)

        # --- PythonCallback / PythonHelp / PythonExpireCheck / PythonCanDo all reference existing functions
        for field in ("PythonCallback", "PythonHelp", "PythonExpireCheck", "PythonCanDo"):
            name = child_text(evt, field, "")
            if name and name not in py_funcs:
                errors.append("%s: %s references missing function: %s" % (ename, field, name))

        # --- ClearEvents on done events
        if is_done:
            ce = evt.find("ClearEvents")
            if ce is None or len(list(ce.findall("EventChance"))) == 0:
                warnings.append("%s: done event has no ClearEvents (quest marker stays open after completion)" % ename)
            else:
                for ec in ce.findall("EventChance"):
                    eref = ec.find("Event")
                    if eref is not None and eref.text and eref.text.strip() not in all_event_types:
                        errors.append("%s: ClearEvents references undefined event: %s" % (ename, eref.text.strip()))

        # --- bGlobal=1 expected on done events
        bgl = child_int(evt, "bGlobal", 0)
        if is_done and bgl != 1:
            warnings.append("%s: done event bGlobal=%d (vanilla pattern is 1)" % (ename, bgl))
        if is_start and bgl != 0:
            warnings.append("%s: start event bGlobal=%d (vanilla pattern is 0)" % (ename, bgl))

        # --- UnitClass + iNumFreeUnits sanity
        uclass = child_text(evt, "UnitClass", "NONE")
        nfree = child_int(evt, "iNumFreeUnits", 0)
        if uclass != "NONE" and nfree == 0:
            warnings.append("%s: UnitClass=%s but iNumFreeUnits=0 (no unit will spawn)" % (ename, uclass))
        if uclass == "NONE" and nfree > 0:
            warnings.append("%s: iNumFreeUnits=%d but UnitClass=NONE (nothing to spawn)" % (ename, nfree))

        # --- Tech + iTechPercent sanity
        tech = child_text(evt, "Tech", "NONE")
        tpct = child_int(evt, "iTechPercent", 0)
        if tech != "NONE" and tpct == 0:
            warnings.append("%s: Tech=%s but iTechPercent=0 (no beakers granted)" % (ename, tech))

        # --- BonusType + iBonusChange sanity
        bonus = child_text(evt, "BonusType", "NONE")
        bonus_change = child_int(evt, "iBonusChange", 0)
        if bonus != "NONE" and bonus_change == 0:
            warnings.append("%s: BonusType=%s but iBonusChange=0 (no bonus change)" % (ename, bonus))

        # --- ImprovementType + iImprovementChange sanity
        imp = child_text(evt, "ImprovementType", "NONE")
        imp_change = child_int(evt, "iImprovementChange", 0)
        if imp != "NONE" and imp_change == 0:
            warnings.append("%s: ImprovementType=%s but iImprovementChange=0" % (ename, imp))

    # ============================================================
    # Reverse-check: every start event must be referenced as a PrereqEvent
    # by exactly one done trigger
    # ============================================================
    start_to_done = {}
    for tname in dowager_trigger_types:
        if not tname.endswith("_DONE"):
            continue
        trig = trigger_objs[tname]
        for prereq in child_strs(trig, "PrereqEvents", "Event"):
            start_to_done.setdefault(prereq, []).append(tname)

    for ename in dowager_event_types:
        if ename.endswith("_1") and "_DONE_" not in ename:
            # This is a start event; should be referenced by exactly one done trigger
            refs = start_to_done.get(ename, [])
            if not refs:
                errors.append("%s: start event has no done trigger referencing it via PrereqEvents (quest can never complete)" % ename)
            elif len(refs) > 1:
                warnings.append("%s: referenced by multiple done triggers: %s" % (ename, refs))

    # ============================================================
    # Every start trigger must reference exactly one bQuest=1 start event
    # ============================================================
    for tname in dowager_trigger_types:
        if tname.endswith("_DONE"):
            continue
        trig = trigger_objs[tname]
        events_listed = child_strs(trig, "Events", "Event")
        if len(events_listed) != 1:
            warnings.append("%s: start trigger lists %d events (typical pattern is 1)" % (tname, len(events_listed)))
        for evname in events_listed:
            if evname in event_objs:
                if child_int(event_objs[evname], "bQuest", 0) != 1:
                    errors.append("%s: start trigger fires %s which is not bQuest=1" % (tname, evname))

    # ============================================================
    # Each done trigger should reference >=1 done event with ClearEvents
    # pointing back to the start event
    # ============================================================
    for tname in dowager_trigger_types:
        if not tname.endswith("_DONE"):
            continue
        trig = trigger_objs[tname]
        start_prereqs = child_strs(trig, "PrereqEvents", "Event")
        if not start_prereqs:
            continue
        start_evt = start_prereqs[0]
        events_listed = child_strs(trig, "Events", "Event")
        for done_evt_name in events_listed:
            if done_evt_name not in event_objs:
                continue
            de = event_objs[done_evt_name]
            ce = de.find("ClearEvents")
            if ce is None:
                warnings.append("%s: lists done event %s which has no ClearEvents" % (tname, done_evt_name))
                continue
            cleared = False
            for ec in ce.findall("EventChance"):
                eref = ec.find("Event")
                if eref is not None and eref.text and eref.text.strip() == start_evt:
                    cleared = True
                    break
            if not cleared:
                warnings.append("%s: done event %s does not clear the prereq start event %s" % (tname, done_evt_name, start_evt))

    # ============================================================
    # Print results
    # ============================================================
    print("=== ERRORS (must fix) ===")
    if errors:
        for e in errors:
            print("  ERR: " + e)
    else:
        print("  None")
    print()
    print("=== WARNINGS (should review) ===")
    if warnings:
        for w in warnings:
            print("  WARN: " + w)
    else:
        print("  None")
    print()
    print("Errors:   %d" % len(errors))
    print("Warnings: %d" % len(warnings))

    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
