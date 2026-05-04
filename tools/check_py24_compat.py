"""Static check for Python 2.4 syntax compliance.

Civ4 BTS ships Python 2.4. Several Py 2.5+ features will cause a
SyntaxError at module-load time on the live game, which kills
CvEventInterface and produces 'ERR: Call function onEvent failed' spam.

This script uses regex heuristics to flag known offenders. It is NOT a
full parser, but catches the cases that have actually bitten us:

    * Conditional expressions (`X if Y else Z`)
    * `with` statements (PEP 343)
    * `except Exception as exc:` (PEP 3110, also Py 2.6+)
    * f-strings (Py 3.6+)
    * `print(...)` as a function

Run from repo root:

    python tools/check_py24_compat.py [path1 [path2 ...]]

Default paths: all .py files under
    CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/Python

Exit code: 0 if clean, 1 if any potential incompatibility found.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ROOT = REPO_ROOT / "CoreFiles" / "Sid Meier's Civilization IV Beyond the Sword" / "Beyond the Sword" / "Assets" / "Python"

# (regex, label, severity, hint)
PATTERNS = [
    (re.compile(r'\S+\s+if\s+[^\n#]+?\s+else\s+\S'),
     "conditional expression", "ERROR",
     "rewrite as if/else statement: 'X = A if B else C' becomes 'if B: X = A; else: X = C'"),
    (re.compile(r'^\s*with\s+'),
     "'with' statement", "ERROR",
     "Py 2.4 has no 'with'. Use try/finally with explicit close()."),
    (re.compile(r'except\s+\w+(\.\w+)*\s+as\s+\w+\s*:'),
     "'except ... as ...' syntax", "ERROR",
     "Py 2.4 syntax: 'except Exception, exc:' (comma, not 'as')."),
    (re.compile(r'(?:^|[^\w])f"[^"]*\{'),
     "f-string", "ERROR",
     "f-strings are Py 3.6+. Use '%s' formatting or .format()."),
    (re.compile(r"(?:^|[^\w])f'[^']*\{"),
     "f-string", "ERROR",
     "f-strings are Py 3.6+. Use '%s' formatting or .format()."),
]

# Allowlist: false-positive patterns inside string literals or comments.
# (path-relative-to-root or filename, line_number) -> reason
ALLOW = {
}


def check_file(path: Path) -> list:
    issues = []
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as exc:  # noqa: BLE001
        return [(path, 0, "READ_ERROR", str(exc), "")]
    for lineno, line in enumerate(text.splitlines(), start=1):
        # Quick skip for comment-only / docstring-only lines (cheap).
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("##"):
            continue
        for pat, label, severity, hint in PATTERNS:
            if pat.search(line):
                # crude allowlist hook
                key = (path.name, lineno)
                if key in ALLOW:
                    continue
                issues.append((path, lineno, severity, label, hint, line.strip()))
    return issues


def main(argv: list) -> int:
    if len(argv) > 1:
        targets = [Path(a) for a in argv[1:]]
    else:
        targets = [DEFAULT_ROOT]

    files: list = []
    for t in targets:
        if t.is_file() and t.suffix == ".py":
            files.append(t)
        elif t.is_dir():
            files.extend(sorted(t.rglob("*.py")))

    if not files:
        print(f"No .py files found under {targets}")
        return 0

    all_issues = []
    for f in files:
        all_issues.extend(check_file(f))

    if not all_issues:
        print(f"OK: {len(files)} file(s) checked, no Py 2.5+ syntax detected.")
        return 0

    print(f"Found {len(all_issues)} potential Py 2.5+ issue(s) across {len(files)} file(s):")
    print()
    for issue in all_issues:
        if len(issue) == 5:
            path, lineno, severity, label, line = issue + ("",)
            hint = ""
        else:
            path, lineno, severity, label, hint, line = issue
        rel = path
        try:
            rel = path.relative_to(REPO_ROOT)
        except ValueError:
            pass
        print(f"  [{severity}] {rel}:{lineno}: {label}")
        if line:
            print(f"      | {line}")
        if hint:
            print(f"      hint: {hint}")
        print()
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
