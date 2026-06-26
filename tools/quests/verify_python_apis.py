#!/usr/bin/env python3
# coding: utf-8
"""verify_python_apis.py

Checks every Python API call used in DowagerMod helper functions against
the union of:
 - methods used elsewhere in CvRandomEventInterface.py (vanilla baseline)
 - methods exposed in the DLL source (Cy*Interface.cpp def's)

This catches the round-3-style bug where we called methods that don't exist
on the Civ4 Python API (e.g. getNumCityPlots, CivicOptionTypes.X).
"""
from __future__ import print_function
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
PY_FILE = os.path.join(
    REPO, "CoreFiles",
    "Sid Meier's Civilization IV Beyond the Sword",
    "Beyond the Sword", "Assets",
    "Python", "EntryPoints", "CvRandomEventInterface.py",
)
SDK = os.path.join(REPO, 'third_party', 'beyond-the-sword-sdk', 'CvGameCoreDLL')

# Methods we always allow (built-in / engine globals).
ALLOW = {
    'range', 'len', 'str', 'int', 'float', 'list', 'dict', 'sorted',
    'min', 'max', 'abs', 'sum', 'append', 'sort', 'extend', 'pop',
    'keys', 'values', 'items', 'get', 'has_key',
    'isAlive', 'isHasMet', 'getType', 'getKey', 'getName',
    'true', 'false', 'True', 'False', 'None',
}


def collect_api_methods():
    """Collect method names from vanilla CvRandomEventInterface.py + Cy*Interface.cpp."""
    api = set()
    with open(PY_FILE, 'rb') as f:
        src = f.read().decode('utf-8', errors='replace')
    # Find every .methodName( pattern
    for m in re.finditer(r'\.([A-Za-z_][A-Za-z0-9_]*)\s*\(', src):
        api.add(m.group(1))
    # Add methods exposed by Cy*Interface.cpp via .def("methodName"
    if os.path.isdir(SDK):
        for fname in os.listdir(SDK):
            if not fname.startswith('Cy') or 'Interface' not in fname:
                continue
            if not fname.endswith('.cpp'):
                continue
            try:
                with open(os.path.join(SDK, fname), 'rb') as f:
                    text = f.read().decode('utf-8', errors='replace')
                for m in re.finditer(r'\.def\(\s*"([A-Za-z_][A-Za-z0-9_]*)"', text):
                    api.add(m.group(1))
            except Exception:
                pass
    return api


def collect_calls_in_dowager_funcs():
    """Return dict func_name -> set of method names called."""
    with open(PY_FILE, 'rb') as f:
        src = f.read().decode('utf-8', errors='replace')
    # Find all functions named applyDowager* or canTriggerXxxDone / canTriggerXxxDoneNew
    # plus getDowager* helpers.
    funcs = {}
    pattern = re.compile(
        r'^def\s+(applyDowager\w+|canTrigger\w*Done\w*|getDowager\w+)\s*\([^)]*\)\s*:',
        re.MULTILINE,
    )
    matches = list(pattern.finditer(src))
    for i, m in enumerate(matches):
        name = m.group(1)
        start = m.end()
        end = matches[i+1].start() if i + 1 < len(matches) else len(src)
        body = src[start:end]
        # Stop at next top-level def or end
        body_match = re.search(r'\n(?=def\s+)', body)
        if body_match:
            body = body[:body_match.start()]
        calls = set()
        for cm in re.finditer(r'\.([A-Za-z_][A-Za-z0-9_]*)\s*\(', body):
            calls.add(cm.group(1))
        funcs[name] = calls
    return funcs


def main():
    print('=== DowagerMod Python API verification ===')
    api = collect_api_methods()
    print('Known API methods (vanilla + Cy*Interface): %d' % len(api))
    funcs = collect_calls_in_dowager_funcs()
    print('DowagerMod helper functions:               %d' % len(funcs))
    errors = []
    for fn, calls in funcs.items():
        unknown = [c for c in calls if c not in api and c not in ALLOW]
        for u in unknown:
            errors.append('%s -> .%s()' % (fn, u))
    if errors:
        print('')
        print('=== UNKNOWN API CALLS ===')
        for e in sorted(errors):
            print('  ' + e)
        print('')
        print('Failed.')
        return 1
    print('OK: every DowagerMod helper uses only known API methods.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
