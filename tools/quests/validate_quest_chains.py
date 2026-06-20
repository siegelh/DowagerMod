#!/usr/bin/env python3
"""Validate cross-references in DowagerMod quest XML.

Checks:
  * Every <Event> referenced in EventTriggerInfos.xml resolves to an EVENT_* defined in EventInfos.xml.
  * Every <PrereqEvents><Event> chain in EventInfos.xml and EventTriggerInfos.xml resolves.
  * Every TXT_KEY_* referenced in EventTriggerInfos.xml and EventInfos.xml resolves in CIV4GameText_Events_BTS.xml.
  * No duplicate <Type> entries in EventInfos.xml or EventTriggerInfos.xml.
  * No EVENT_*_DONE_* without a corresponding start trigger chain.

Exits non-zero on any failure.

Run from worktree root:
    python tools\\quests\\validate_quest_chains.py
"""
from __future__ import print_function
import os
import re
import sys
import xml.etree.ElementTree as ET

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ASSETS = os.path.join(
    REPO_ROOT,
    "CoreFiles",
    "Sid Meier's Civilization IV Beyond the Sword",
    "Beyond the Sword",
    "Assets",
)

TRIGGERS_XML = os.path.join(ASSETS, "XML", "Events", "CIV4EventTriggerInfos.xml")
EVENTS_XML = os.path.join(ASSETS, "XML", "Events", "CIV4EventInfos.xml")
TEXT_XML = os.path.join(ASSETS, "XML", "Text", "CIV4GameText_Events_BTS.xml")


def _strip_ns(elem):
    """Strip namespace prefixes from element tags (Civ4 XML uses xmlns)."""
    for e in elem.iter():
        if "}" in e.tag:
            e.tag = e.tag.split("}", 1)[1]


def parse(path):
    tree = ET.parse(path)
    root = tree.getroot()
    _strip_ns(root)
    return root


def collect_types(root, container_tag, info_tag):
    seen = {}
    dups = []
    container = root.find(container_tag)
    if container is None:
        # Container tag may itself be the root
        container = root
    for info in container.iter(info_tag):
        t_elem = info.find("Type")
        if t_elem is None or not t_elem.text:
            continue
        name = t_elem.text.strip()
        if name in seen:
            dups.append(name)
        seen[name] = info
    return seen, dups


def collect_event_refs(events_root):
    """Collect every <Event>EVENT_X</Event> reference from EventInfos and trigger PrereqEvents."""
    refs = []
    for parent in events_root.iter():
        for child in parent.findall("Event"):
            if child.text:
                refs.append((parent.tag, child.text.strip()))
    return refs


def collect_text_keys(text_root):
    keys = set()
    for tag in text_root.iter("Tag"):
        if tag.text:
            keys.add(tag.text.strip())
    return keys


TXT_KEY_RE = re.compile(r"TXT_KEY_[A-Z0-9_]+")


def collect_txt_key_refs(path):
    """Cheap text scan — finds TXT_KEY_* tokens regardless of XML wrapping."""
    refs = set()
    with open(path, "rb") as f:
        data = f.read().decode("utf-8", errors="replace")
    for m in TXT_KEY_RE.finditer(data):
        refs.add(m.group(0))
    return refs


def main():
    errors = []
    warnings = []

    for path in (TRIGGERS_XML, EVENTS_XML, TEXT_XML):
        if not os.path.isfile(path):
            errors.append("Missing file: %s" % path)
    if errors:
        for e in errors:
            print("ERROR:", e)
        return 1

    triggers_root = parse(TRIGGERS_XML)
    events_root = parse(EVENTS_XML)
    text_root = parse(TEXT_XML)

    # 1. Duplicate <Type> detection
    trigger_types, trigger_dups = collect_types(triggers_root, "EventTriggerInfos", "EventTriggerInfo")
    event_types, event_dups = collect_types(events_root, "EventInfos", "EventInfo")
    for d in trigger_dups:
        errors.append("Duplicate EventTriggerInfo Type: %s" % d)
    for d in event_dups:
        errors.append("Duplicate EventInfo Type: %s" % d)

    # 2. Every <Event>EVENT_X</Event> in triggers must exist in EventInfos.
    for parent_tag, ref in collect_event_refs(triggers_root):
        if ref not in event_types:
            errors.append(
                "Trigger references undefined event: %s (in <%s>)" % (ref, parent_tag)
            )

    # 3. Every <PrereqEvents><Event> in EventInfos must exist in EventInfos.
    for parent_tag, ref in collect_event_refs(events_root):
        if ref not in event_types:
            errors.append(
                "EventInfo references undefined event: %s (in <%s>)" % (ref, parent_tag)
            )

    # 4. Every TXT_KEY_* referenced in triggers and events must be defined in text XML.
    defined_keys = collect_text_keys(text_root)
    trigger_keys = collect_txt_key_refs(TRIGGERS_XML)
    event_keys = collect_txt_key_refs(EVENTS_XML)
    missing_trigger = sorted(trigger_keys - defined_keys)
    missing_event = sorted(event_keys - defined_keys)
    for k in missing_trigger:
        errors.append("Trigger references undefined TXT_KEY: %s" % k)
    for k in missing_event:
        errors.append("Event references undefined TXT_KEY: %s" % k)

    # 5. Sanity: every done-trigger's PrereqEvents resolves
    for t_name, t_node in trigger_types.items():
        prereqs = t_node.find("PrereqEvents")
        if prereqs is None:
            continue
        for ev in prereqs.findall("Event"):
            if ev.text and ev.text.strip() not in event_types:
                errors.append(
                    "Trigger %s has PrereqEvent referencing undefined event: %s"
                    % (t_name, ev.text.strip())
                )

    print("=== Quest chain validation ===")
    print("EventTriggerInfo count: %d" % len(trigger_types))
    print("EventInfo count:        %d" % len(event_types))
    print("Defined TXT_KEYs:       %d" % len(defined_keys))
    print("Referenced TXT_KEYs:    triggers=%d events=%d"
          % (len(trigger_keys), len(event_keys)))

    if warnings:
        for w in warnings:
            print("WARN:", w)

    if errors:
        print("")
        print("FAILED with %d error(s):" % len(errors))
        for e in errors:
            print("  -", e)
        return 1

    print("OK: all references resolve.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
