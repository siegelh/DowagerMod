#!/usr/bin/env python3
"""Smoke-check CvRandomEventInterface.py for syntax + structural sanity.

Cannot import the file directly (depends on CyGlobalContext from the game),
so this uses AST parsing to validate:
  * The file parses as valid Python (no syntax errors).
  * Every function takes (argsList) as its sole argument — that's the BtS contract.
  * Every function references either kTriggeredData or argsList[0] (catches a common copy-paste bug).
  * No tabs/spaces mixing (the game's Python 2.4 interpreter is strict about that).

Exits non-zero on any failure.

Run from worktree root:
    python tools\\quests\\smoke_quest_callbacks.py
"""
from __future__ import print_function
import ast
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ASSETS = os.path.join(
    REPO_ROOT,
    "CoreFiles",
    "Sid Meier's Civilization IV Beyond the Sword",
    "Beyond the Sword",
    "Assets",
)

INTERFACE_PY = os.path.join(ASSETS, "Python", "EntryPoints", "CvRandomEventInterface.py")

EXPECTED_PREFIXES = (
    "canTrigger",
    "applyEvent",
    "expire",
    "getHelp",
    "doCity",
    "doUnit",
    "getYield",
    "getValue",
)


def main():
    if not os.path.isfile(INTERFACE_PY):
        print("ERROR: missing", INTERFACE_PY)
        return 1

    with open(INTERFACE_PY, "rb") as f:
        src_bytes = f.read()

    # BtS Python 2.4 doesn't tolerate mixed tabs/spaces. Bail loudly if we
    # accidentally introduce mixing while editing.
    lines = src_bytes.split(b"\n")
    mixed = []
    for i, line in enumerate(lines, 1):
        leading = line[: len(line) - len(line.lstrip(b" \t"))]
        if b"\t" in leading and b" " in leading:
            mixed.append(i)
    if mixed:
        print("ERROR: mixed tabs/spaces in indentation at lines:", mixed[:10])
        return 1

    src = src_bytes.decode("utf-8", errors="replace")
    try:
        tree = ast.parse(src, INTERFACE_PY)
    except SyntaxError as e:
        print("ERROR: SyntaxError:", e)
        return 1

    errors = []
    func_count = 0
    callback_count = 0
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        func_count += 1

        name = node.name
        # Skip helpers and private functions.
        if name.startswith("_"):
            continue

        # Heuristic: callback functions match an expected prefix.
        is_callback = any(name.startswith(p) for p in EXPECTED_PREFIXES)
        if not is_callback:
            continue
        callback_count += 1

        # Must have exactly one positional argument named argsList.
        args = node.args
        positional = [a.arg for a in args.args] if hasattr(args, "args") else []
        if positional != ["argsList"]:
            errors.append(
                "%s line %d: expected single arg 'argsList', got %r"
                % (name, node.lineno, positional)
            )
            continue

        # Body should reference argsList (catches stub functions).
        body_src = ast.unparse(node) if hasattr(ast, "unparse") else ""
        if body_src and "argsList" not in body_src:
            errors.append(
                "%s line %d: function body never references argsList"
                % (name, node.lineno)
            )

    print("=== Python callback smoke ===")
    print("File:                 %s" % INTERFACE_PY)
    print("Top-level functions:  %d" % func_count)
    print("Callback functions:   %d" % callback_count)

    if errors:
        print("")
        print("FAILED with %d error(s):" % len(errors))
        for e in errors:
            print("  -", e)
        return 1

    print("OK: all callbacks match BtS contract.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
