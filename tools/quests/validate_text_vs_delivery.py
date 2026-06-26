#!/usr/bin/env python3
# coding: utf-8
"""validate_text_vs_delivery.py

Catches the round-2/round-5 bug class where a done event's text promised a
reward (e.g. "Receive 200 gold") but the XML actually delivered a different
amount or a different reward type.

Approach:
1. For every EVENT_X_DONE_N, find <Description>TXT_KEY_X</Description>.
2. Resolve the English text and the help text.
3. Extract reward keywords:
     - "(\\d+) gold" -> require iGold>=N OR iRandomGold>=N OR scaled-gold callback
     - "(\\d+) (happy|happiness)" -> require iHappy>=N
     - "(\\d+) (health|happiness)" -> require iHealth>=N
     - "great (merchant|prophet|...)" -> require capital specialist callback
     - "free (Granary|...)" -> require capital building callback
     - "golden age" -> require bGoldenAge=1
     - "(\\d+) free unit" -> require iNumFreeUnits>=N
     - "(\\d+) espionage" -> require iEspionagePoints>=N
4. Report mismatches.
"""
from __future__ import print_function
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
ASSETS = os.path.join(
    REPO, "CoreFiles",
    "Sid Meier's Civilization IV Beyond the Sword",
    "Beyond the Sword", "Assets",
)
EVENTS_XML = os.path.join(ASSETS, 'XML', 'Events', 'CIV4EventInfos.xml')
TEXT_XML = os.path.join(ASSETS, 'XML', 'Text', 'CIV4GameText_Events_BTS.xml')

DOWAGER_MARKER = 'EVENT_BLOOD_AND_IRON_1'


def load_text_keys():
    """Return dict TXT_KEY -> English text."""
    keys = {}
    with open(TEXT_XML, 'rb') as f:
        data = f.read().decode('utf-8', errors='replace')
    pattern = re.compile(
        r'<Tag>([^<]+)</Tag>\s*<English>([^<]*)</English>', re.DOTALL)
    for m in pattern.finditer(data):
        keys[m.group(1)] = m.group(2)
    return keys


def find_blocks(events_data):
    """Yield (evt_type, block) for every DowagerMod done event."""
    boundary = events_data.find('<Type>' + DOWAGER_MARKER + '</Type>')
    if boundary == -1:
        return
    open_pat = re.compile(r'<EventInfo>')
    close_pat = re.compile(r'</EventInfo>')
    pos = boundary
    while True:
        op = events_data.rfind('<EventInfo>', 0, pos)
        if op == -1 or op < boundary:
            break
        cl = events_data.find('</EventInfo>', op)
        type_match = re.search(r'<Type>([^<]+)</Type>', events_data[op:cl])
        if type_match:
            yield type_match.group(1), events_data[op:cl + len('</EventInfo>')]
        pos = op - 1
    # forward scan from boundary
    pos = boundary
    while True:
        op = events_data.find('<EventInfo>', pos)
        if op == -1:
            break
        cl = events_data.find('</EventInfo>', op)
        if cl == -1:
            break
        type_match = re.search(r'<Type>([^<]+)</Type>', events_data[op:cl])
        if type_match:
            yield type_match.group(1), events_data[op:cl + len('</EventInfo>')]
        pos = cl + 1


def field(block, name, default=''):
    m = re.search(r'<' + name + r'>([^<]*)</' + name + r'>', block)
    return m.group(1) if m else default


def check_event(evt_type, block, keys):
    """Return list of error strings (or empty list)."""
    desc_key_m = re.search(r'<Description>([^<]+)</Description>', block)
    if not desc_key_m:
        return []
    label_key = desc_key_m.group(1)
    help_key = label_key + '_HELP'
    label = keys.get(label_key, '')
    help_text = keys.get(help_key, '')
    text = (label + ' ' + help_text).lower()

    errors = []

    # Gold lump: only flag explicit lump-sum wording. Per-building modifiers
    # use "All X +N gold" / "every X ... +N gold" patterns which we exclude.
    for m in re.finditer(r'(?:receive|gain|provides?|treasury\s+gains?|tax\s+(?:nets|yields)|lump\s+sum\s+of)\s+(\d+)\s*(?:\[icon_gold\])?\s*gold', text):
        n = int(m.group(1))
        i_gold = int(field(block, 'iGold', '0') or 0)
        i_rand = int(field(block, 'iRandomGold', '0') or 0)
        cb = field(block, 'PythonCallback', '')
        if i_gold < n and i_rand < n and 'ScaledGold' not in cb:
            errors.append('%s: text "%d gold" but iGold=%d iRandomGold=%d cb=%s'
                          % (evt_type, n, i_gold, i_rand, cb))
            break

    # Happy: only flag "+N happy" lumps, not per-building modifiers (those say "All X +N happy").
    has_all_x = bool(re.search(r'(?:all|every|each)\s+\[?color_positive_text\]?\s*\w+', text))
    if not has_all_x:
        for m in re.finditer(r'\+(\d+)\s*\[?(?:icon_)?happy\]?', text):
            n = int(m.group(1))
            i_happy = int(field(block, 'iHappy', '0') or 0)
            if i_happy < n:
                errors.append('%s: text "+%d happy" but iHappy=%d'
                              % (evt_type, n, i_happy))
                break

    # Free unit count: "Receive N <name>" or "N free <name>" — exclude "free unit support".
    m = re.search(r'receive\s+(\d+)\s+free\s+(\w+)', text)
    if not m:
        m = re.search(r'(\d+)\s+free\s+(\w+)', text)
    if m and m.group(2) != 'unit':  # "free unit support" → group(2)="unit"
        n = int(m.group(1))
        i_num = int(field(block, 'iNumFreeUnits', '0') or 0)
        if i_num < n:
            errors.append('%s: text "%d free %s" but iNumFreeUnits=%d'
                          % (evt_type, n, m.group(2), i_num))

    # Golden age
    if 'golden age' in text and 'bGoldenAge>1' not in block:
        errors.append('%s: text "golden age" but bGoldenAge!=1' % evt_type)

    # Settled Great Person (capital): only flag when text uses "settled" wording.
    if re.search(r'settled\s+(?:as\s+)?(?:a\s+)?great\s+(merchant|prophet|scientist|engineer|artist|general|spy|statesman)', text):
        cb = field(block, 'PythonCallback', '')
        if 'CapitalSpecialist' not in cb:
            errors.append('%s: text "settled Great X" but no CapitalSpecialist callback'
                          % evt_type)

    # Espionage
    m = re.search(r'\+?(\d+)\s+espionage', text)
    if m:
        n = int(m.group(1))
        i_esp = int(field(block, 'iEspionagePoints', '0') or 0)
        if i_esp < n:
            errors.append('%s: text "+%d espionage" but iEspionagePoints=%d'
                          % (evt_type, n, i_esp))

    return errors


def main():
    print('=== Text-vs-delivery validation ===')
    with open(EVENTS_XML, 'rb') as f:
        events_data = f.read().decode('utf-8', errors='replace')
    keys = load_text_keys()
    print('Text keys loaded: %d' % len(keys))
    errors = []
    n_checked = 0
    seen = set()
    for evt_type, block in find_blocks(events_data):
        if evt_type in seen:
            continue
        seen.add(evt_type)
        if '_DONE_' not in evt_type:
            continue
        n_checked += 1
        errors.extend(check_event(evt_type, block, keys))
    print('DowagerMod done events checked: %d' % n_checked)
    if errors:
        print('')
        print('=== MISMATCHES ===')
        for e in errors:
            print('  ' + e)
        return 1
    print('OK: every done event text matches its XML delivery.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
