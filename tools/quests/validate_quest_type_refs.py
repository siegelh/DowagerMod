#!/usr/bin/env python3
"""Validate that every TYPE token referenced in DowagerMod's new quest XML
actually exists in vanilla BtS XML.

Why: the BtS XML schema permits any text in fields like <UnitClass>X</UnitClass>;
the game only validates at load time and rejects unknown TYPEs with errors like
"Tag: BUILDINGCLASS_FOO in Info class was incorrect". This script catches those
errors before the user launches the game.

Scans every BUILDINGCLASS_/UNITCLASS_/UNITCOMBAT_/TECH_/CIVIC_/SPECIALIST_/
PROMOTION_/IMPROVEMENT_/FEATURE_/TERRAIN_/RELIGION_/CORPORATION_/BONUS_ token
in our new quest entries (everything inserted after the EVENTTRIGGER_BLOOD_AND_IRON
marker), validates against the canonical definition files, and reports unknowns.

Run from worktree root:
    python tools\\quests\\validate_quest_type_refs.py
"""
from __future__ import print_function
import os
import re
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ASSETS = os.path.join(
    REPO_ROOT,
    "CoreFiles",
    "Sid Meier's Civilization IV Beyond the Sword",
    "Beyond the Sword",
    "Assets",
)

# Files that define each type. Each file gets fully scanned for <Type>X</Type>.
TYPE_SOURCES = {
    "BUILDINGCLASS_": [
        os.path.join(ASSETS, "XML", "Buildings", "CIV4BuildingClassInfos.xml"),
    ],
    "UNITCLASS_": [
        os.path.join(ASSETS, "XML", "Units", "CIV4UnitClassInfos.xml"),
    ],
    "UNITCOMBAT_": [
        os.path.join(ASSETS, "XML", "BasicInfos", "CIV4UnitCombatInfos.xml"),
    ],
    "TECH_": [
        os.path.join(ASSETS, "XML", "Technologies", "CIV4TechInfos.xml"),
    ],
    "CIVIC_": [
        os.path.join(ASSETS, "XML", "GameInfo", "CIV4CivicInfos.xml"),
    ],
    "SPECIALIST_": [
        os.path.join(ASSETS, "XML", "GameInfo", "CIV4SpecialistInfos.xml"),
    ],
    "PROMOTION_": [
        os.path.join(ASSETS, "XML", "Units", "CIV4PromotionInfos.xml"),
    ],
    "IMPROVEMENT_": [
        os.path.join(ASSETS, "XML", "Terrain", "CIV4ImprovementInfos.xml"),
    ],
    "FEATURE_": [
        os.path.join(ASSETS, "XML", "Terrain", "CIV4FeatureInfos.xml"),
    ],
    "TERRAIN_": [
        os.path.join(ASSETS, "XML", "Terrain", "CIV4TerrainInfos.xml"),
    ],
    "RELIGION_": [
        os.path.join(ASSETS, "XML", "GameInfo", "CIV4ReligionInfo.xml"),
    ],
    "CORPORATION_": [
        os.path.join(ASSETS, "XML", "GameInfo", "CIV4CorporationInfo.xml"),
    ],
    "BONUS_": [
        os.path.join(ASSETS, "XML", "Terrain", "CIV4BonusInfos.xml"),
    ],
}

# Targets to scan for references — only the segments we added (DowagerMod quests).
TARGET_FILES = [
    os.path.join(ASSETS, "XML", "Events", "CIV4EventTriggerInfos.xml"),
    os.path.join(ASSETS, "XML", "Events", "CIV4EventInfos.xml"),
]

# Insertion marker — everything from this line onward is DowagerMod-authored.
DOWAGER_MARKER_TRIG = "EVENTTRIGGER_BLOOD_AND_IRON"
DOWAGER_MARKER_EVT = "EVENT_BLOOD_AND_IRON_1"

TYPE_RE = re.compile(
    r"\b("
    r"BUILDINGCLASS_|UNITCLASS_|UNITCOMBAT_|TECH_|CIVIC_|SPECIALIST_|"
    r"PROMOTION_|IMPROVEMENT_|FEATURE_|TERRAIN_|RELIGION_|CORPORATION_|BONUS_"
    r")[A-Z0-9_]+\b"
)


def load_valid_types():
    valid = set()
    by_prefix = {p: set() for p in TYPE_SOURCES}
    for prefix, files in TYPE_SOURCES.items():
        for path in files:
            if not os.path.isfile(path):
                print("WARN: missing source file:", path)
                continue
            with open(path, "rb") as f:
                data = f.read().decode("utf-8", errors="replace")
            for m in re.finditer(r"<Type>([A-Z0-9_]+)</Type>", data):
                name = m.group(1)
                if name.startswith(prefix):
                    valid.add(name)
                    by_prefix[prefix].add(name)
    return valid, by_prefix


def load_quest_refs():
    refs = []  # list of (filename, line_number, token)
    for path in TARGET_FILES:
        with open(path, "rb") as f:
            lines = f.read().decode("utf-8", errors="replace").splitlines()
        # Find DowagerMod start line.
        marker = DOWAGER_MARKER_TRIG if "Trigger" in path else DOWAGER_MARKER_EVT
        start = None
        for i, line in enumerate(lines, 1):
            if marker in line:
                start = i
                break
        if start is None:
            print("WARN: marker %r not found in %s; scanning whole file" % (marker, path))
            start = 1
        for i in range(start - 1, len(lines)):
            line = lines[i]
            for m in TYPE_RE.finditer(line):
                refs.append((path, i + 1, m.group(0)))
    return refs


def main():
    valid, _ = load_valid_types()
    refs = load_quest_refs()

    print("=== Quest type reference validation ===")
    print("Valid types loaded:           %d" % len(valid))
    print("References in DowagerMod quests: %d" % len(refs))

    unknown = []
    for path, lineno, token in refs:
        # Skip NONE which is the universal "unspecified" sentinel.
        if token in ("BONUS_NONE", "UNITCLASS_NONE", "BUILDINGCLASS_NONE",
                     "TECH_NONE", "CIVIC_NONE", "FEATURE_NONE",
                     "IMPROVEMENT_NONE", "RELIGION_NONE", "CORPORATION_NONE",
                     "PROMOTION_NONE", "BONUS_NONE"):
            continue
        if token in valid:
            continue
        unknown.append((path, lineno, token))

    if not unknown:
        print("OK: every type reference resolves to a vanilla definition.")
        return 0

    print("")
    print("FAILED — %d unknown type reference(s):" % len(unknown))
    last_token = None
    seen = set()
    # Print one occurrence per token first so the user gets a clean overview.
    for path, lineno, token in unknown:
        if token in seen:
            continue
        seen.add(token)
        rel = os.path.relpath(path, REPO_ROOT)
        print("  - %s (e.g. %s:%d)" % (token, rel, lineno))
    if len(unknown) > len(seen):
        print("")
        print("(plus %d more occurrence(s) of the above)" % (len(unknown) - len(seen)))
    return 1


if __name__ == "__main__":
    sys.exit(main())
