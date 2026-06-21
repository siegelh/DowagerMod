#!/usr/bin/env python3
# coding: utf-8
"""Round 2 of deep audit: more semantic checks.

Catches things the first deep_audit.py missed:
  - Tooltip TXT_KEY_<EVENT>_HELP existence for events wired to getDowagerChoiceHelp
  - Quest objective TXT_KEY_<EVENT>_QUEST existence for start events wired to
    getDowagerQuestHelp
  - %d/%s format specifier mismatches in text strings vs Python helper calls
  - Choice text emptiness (just whitespace)
  - Whether every dispatched specialist in DOWAGER_CAPITAL_SPECIALISTS dict
    corresponds to a real done event that actually wires the callback
  - Whether every event wired to applyDowagerCapitalSpecialist is in the dict
  - Same for applyDowagerCapitalFreeBuilding
"""
from __future__ import print_function
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ASSETS = os.path.join(
    REPO, "CoreFiles",
    "Sid Meier's Civilization IV Beyond the Sword",
    "Beyond the Sword", "Assets",
)
EVENTS = os.path.join(ASSETS, "XML", "Events", "CIV4EventInfos.xml")
TEXT = os.path.join(ASSETS, "XML", "Text", "CIV4GameText_Events_BTS.xml")
PY = os.path.join(ASSETS, "Python", "EntryPoints", "CvRandomEventInterface.py")

DOWAGER_EVT_MARKER = "EVENT_BLOOD_AND_IRON_1"


def read(p):
    with open(p, "rb") as f:
        return f.read().decode("utf-8", errors="replace")


def main():
    print("=== Deep audit round 2 ===")
    edata = read(EVENTS)
    tdata = read(TEXT)
    pdata = read(PY)

    text_keys = {}
    for m in re.finditer(r"<Tag>(TXT_KEY_[A-Z0-9_]+)</Tag>\s*<English>(.*?)</English>",
                         tdata, re.DOTALL):
        text_keys[m.group(1)] = m.group(2)

    errors = []
    warnings = []

    boundary = edata.find(DOWAGER_EVT_MARKER)
    if boundary == -1:
        print("ERROR: boundary marker not found")
        return 1

    # Walk every EventInfo block in DowagerMod section.
    for m in re.finditer(r"<EventInfo>(.*?)</EventInfo>", edata[boundary - 50:], re.DOTALL):
        body = m.group(1)
        tm = re.search(r"<Type>(EVENT_[A-Z0-9_]+)</Type>", body)
        if not tm:
            continue
        evt = tm.group(1)
        is_done = "_DONE_" in evt
        is_start = evt.endswith("_1") and not is_done

        # --- Help callback wiring -> TXT_KEY must exist
        php = re.search(r"<PythonHelp>([^<]+)</PythonHelp>", body)
        if php:
            fn = php.group(1).strip()
            if fn == "getDowagerChoiceHelp":
                # Expects TXT_KEY_<EVENT>_HELP
                key = "TXT_KEY_" + evt + "_HELP"
                if key not in text_keys:
                    errors.append("%s: PythonHelp=getDowagerChoiceHelp but TXT_KEY missing: %s" % (evt, key))
                else:
                    body_str = text_keys[key].strip()
                    if not body_str:
                        warnings.append("%s: TXT_KEY %s has empty English content" % (evt, key))
            elif fn == "getDowagerQuestHelp":
                # Expects TXT_KEY_<EVENT_minus_trailing_1>_QUEST
                base = evt[:-2] if evt.endswith("_1") else evt
                key = "TXT_KEY_" + base + "_QUEST"
                if key not in text_keys:
                    errors.append("%s: PythonHelp=getDowagerQuestHelp but TXT_KEY missing: %s" % (evt, key))

        # --- Description TXT_KEY must have non-empty English content
        dm = re.search(r"<Description>([^<]+)</Description>", body)
        if dm and dm.group(1).strip() in text_keys:
            content = text_keys[dm.group(1).strip()].strip()
            if not content:
                warnings.append("%s: Description %s has empty English content" % (evt, dm.group(1).strip()))

        # --- Format specifier consistency: if TXT_KEY contains %d1 / %s1 etc,
        # the Python wrapper must pass corresponding args. We can only flag
        # mismatches in our generic helpers.
        if php:
            fn = php.group(1).strip()
            if fn in ("getDowagerChoiceHelp", "getDowagerQuestHelp"):
                # These callbacks pass () as args -- they cannot substitute %d/%s.
                if fn == "getDowagerChoiceHelp":
                    key = "TXT_KEY_" + evt + "_HELP"
                else:
                    base = evt[:-2] if evt.endswith("_1") else evt
                    key = "TXT_KEY_" + base + "_QUEST"
                text_val = text_keys.get(key, "")
                if re.search(r"%[sdf]\d+", text_val):
                    errors.append("%s: TXT_KEY %s contains format placeholders (%%d1/%%s1) but generic helper passes no args -> will display literal %%d1" % (evt, key))

    # --- Cross-check DOWAGER_CAPITAL_SPECIALISTS dict vs actual XML wiring
    spec_dict_entries = set(re.findall(r'\t"(EVENT_[A-Z0-9_]+)": "SPECIALIST_[A-Z_]+"', pdata))
    bldg_dict_entries = set(re.findall(r'\t"(EVENT_[A-Z0-9_]+)": "BUILDINGCLASS_[A-Z_]+"', pdata))

    # Find every event that wires applyDowagerCapitalSpecialist
    wired_spec = set()
    wired_bldg = set()
    for m in re.finditer(r"<EventInfo>(.*?)</EventInfo>", edata[boundary - 50:], re.DOTALL):
        body = m.group(1)
        tm = re.search(r"<Type>(EVENT_[A-Z0-9_]+)</Type>", body)
        if not tm:
            continue
        evt = tm.group(1)
        if "applyDowagerCapitalSpecialist" in body:
            wired_spec.add(evt)
        if "applyDowagerCapitalFreeBuilding" in body:
            wired_bldg.add(evt)

    # Events wired but not in dict -> reward silently dropped
    for evt in wired_spec - spec_dict_entries:
        errors.append("%s: PythonCallback=applyDowagerCapitalSpecialist but not in DOWAGER_CAPITAL_SPECIALISTS dict (no reward)" % evt)
    for evt in spec_dict_entries - wired_spec:
        warnings.append("%s: in DOWAGER_CAPITAL_SPECIALISTS dict but no event wires applyDowagerCapitalSpecialist" % evt)

    for evt in wired_bldg - bldg_dict_entries:
        errors.append("%s: PythonCallback=applyDowagerCapitalFreeBuilding but not in DOWAGER_CAPITAL_BUILDINGS dict" % evt)
    for evt in bldg_dict_entries - wired_bldg:
        warnings.append("%s: in DOWAGER_CAPITAL_BUILDINGS dict but no event wires applyDowagerCapitalFreeBuilding" % evt)

    print("Specialist dict entries:  %d" % len(spec_dict_entries))
    print("Events wired to specialist callback: %d" % len(wired_spec))
    print("Building dict entries:    %d" % len(bldg_dict_entries))
    print("Events wired to building callback:   %d" % len(wired_bldg))
    print()

    print("=== ERRORS ===")
    if errors:
        for e in errors:
            print("  ERR: " + e)
    else:
        print("  None")
    print()
    print("=== WARNINGS ===")
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
