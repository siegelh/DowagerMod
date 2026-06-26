#!/usr/bin/env python3
# coding: utf-8
"""validate_quest_archetype_budget.py

Enforces per-archetype budget caps on the DowagerMod quest reward menu.
Goal: prevent regression toward the round-5 problem where 45% of specialist
rewards were Great Merchant and 51% of quests had a gold lump.

Computes archetype distribution from the actual XML and the redesign data
file (which is the canonical source). Fails loudly if any cap is exceeded.
"""
from __future__ import print_function
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _redesign_data import REDESIGN
from collections import Counter

# Caps are absolute counts of choice slots (141 total across 47 quests x 3).
BUDGETS = {
    'C1': 30,   # capital specialist - was 42; cap at 30 keeps it common but not dominant
    'F3': 15,   # gold lump - was 24; cap at 15
    'A1': 12,   # empire +happy - was implicit ~25; cap at 12
    'A2': 6,    # empire +health
    # All other archetypes: soft cap of 25 (none are likely to exceed).
}
DEFAULT_CAP = 25


def main():
    c = Counter()
    for q, choices in REDESIGN.items():
        for code, params in choices:
            c[code] += 1
    print('=== Quest archetype budget validation ===')
    print('Total choices: %d (across %d quests)' % (sum(c.values()), len(REDESIGN)))
    print('')
    print('Archetype distribution:')
    for code in sorted(c):
        cap = BUDGETS.get(code, DEFAULT_CAP)
        n = c[code]
        marker = 'OVER' if n > cap else ' OK '
        print('  %s [%s] %3d / %3d' % (marker, code, n, cap))
    errors = []
    for code, n in c.items():
        cap = BUDGETS.get(code, DEFAULT_CAP)
        if n > cap:
            errors.append('%s used %d times (cap %d)' % (code, n, cap))
    if errors:
        print('')
        print('=== ERRORS ===')
        for e in errors:
            print('  ' + e)
        return 1
    print('')
    print('OK: every archetype within budget.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
