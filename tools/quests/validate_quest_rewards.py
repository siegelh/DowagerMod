#!/usr/bin/env python3
"""Validate that DowagerMod done events with city-targeted rewards either:
  (a) have <bPickCity>1</bPickCity>, OR
  (b) have a <PythonCallback> wired (which can apply the reward manually).

Background: BtS silently drops <FreeSpecialistCounts>, <BuildingClass>+<iBuildingChange>
and a few other city-targeted reward fields when <bPickCity>0</bPickCity>, because
the engine's CvCity::applyEvent function (where those fields are processed) is
only called when isCityEffect() is true (which mirrors bPickCity).

This was the root cause of the "Free Great Person did nothing" bug in our first
playtest. The repair commit added Python callbacks to deliver these rewards
manually. This script catches future regressions.

Run from worktree root:
    python tools\\quests\\validate_quest_rewards.py
"""
from __future__ import print_function
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EVENTS_XML = os.path.join(
    REPO,
    "CoreFiles",
    "Sid Meier's Civilization IV Beyond the Sword",
    "Beyond the Sword",
    "Assets",
    "XML",
    "Events",
    "CIV4EventInfos.xml",
)
DOWAGER_EVENT_MARKER = b"<Type>EVENT_BLOOD_AND_IRON_1</Type>"


def main():
    with open(EVENTS_XML, "rb") as f:
        data = f.read()

    dowager_idx = data.find(DOWAGER_EVENT_MARKER)
    if dowager_idx == -1:
        print("ERROR: Blood and Iron marker not found")
        return 1
    dowager_open = data.rfind(b"<EventInfo>", 0, dowager_idx)
    section = data[dowager_open:]

    errors = []
    event_count = 0
    # Iterate every <EventInfo>...</EventInfo> block in DowagerMod section.
    for m in re.finditer(rb"<EventInfo>(.*?)</EventInfo>", section, flags=re.DOTALL):
        body = m.group(1)
        type_m = re.search(rb"<Type>(EVENT_[A-Z_0-9]+)</Type>", body)
        if not type_m:
            continue
        evt = type_m.group(1).decode()
        event_count += 1

        # Check for city-targeted reward fields that the engine silently drops
        # when bPickCity=0 AND no Python callback is wired.
        has_free_specialist = re.search(
            rb"<FreeSpecialistCounts>\s*<FreeSpecialistCount>",
            body,
            flags=re.DOTALL,
        ) is not None
        # <BuildingClass> non-NONE with positive iBuildingChange.
        bclass_m = re.search(rb"<BuildingClass>(BUILDINGCLASS_[A-Z_]+)</BuildingClass>", body)
        ichange_m = re.search(rb"<iBuildingChange>([1-9]\d*)</iBuildingChange>", body)
        has_free_building = bclass_m is not None and ichange_m is not None

        if not (has_free_specialist or has_free_building):
            continue

        # If bPickCity=1, the engine will deliver these correctly.
        has_pick_city = re.search(rb"<bPickCity>1</bPickCity>", body) is not None
        if has_pick_city:
            continue

        # If a PythonCallback is wired, assume it handles the reward manually.
        py_m = re.search(rb"<PythonCallback>([^<]+)</PythonCallback>", body)
        if py_m and py_m.group(1).strip():
            continue

        # Otherwise: BROKEN.
        reasons = []
        if has_free_specialist:
            reasons.append("FreeSpecialistCounts present")
        if has_free_building:
            reasons.append("BuildingClass=%s + iBuildingChange=%s"
                           % (bclass_m.group(1).decode(), ichange_m.group(1).decode()))
        errors.append("%s: %s but bPickCity=0 and no PythonCallback (reward silently dropped)"
                      % (evt, "; ".join(reasons)))

    print("=== Reward delivery validation ===")
    print("DowagerMod events scanned: %d" % event_count)
    if errors:
        print("")
        print("FAILED with %d error(s):" % len(errors))
        for e in errors:
            print("  - %s" % e)
        return 1
    print("OK: all city-targeted rewards either use bPickCity=1 or have a Python callback.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
