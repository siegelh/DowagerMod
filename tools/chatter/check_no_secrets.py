"""Pre-commit guard: refuse to commit chatter secrets.

Run from PowerShell scripts or git pre-commit hooks. Exit code:
  0 = no secrets detected
  1 = potential secret in staged file (refuse to commit)

Heuristic, not paranoid. Looks for:
- Files containing "api_key" assigned to a non-empty value
- Files containing the literal Foundry endpoint host with a non-empty key
- Filenames matching chatter*config*.json (anywhere)
"""
from __future__ import annotations

import re
import sys
import subprocess
from pathlib import Path


SECRET_FILENAME_PATTERNS = [
    re.compile(r"chatter.*config.*\.json$", re.IGNORECASE),
    re.compile(r"\.env(\..+)?$"),
    re.compile(r".*\.api_key$", re.IGNORECASE),
]

CONTENT_PATTERNS = [
    re.compile(r'api_key["\']?\s*[:=]\s*["\'][A-Za-z0-9\-_]{20,}["\']'),
    re.compile(r'AZURE_FOUNDRY_API_KEY["\']?\s*=\s*["\'][^"\'\s]{16,}["\']'),
]

# Allow-list: example configs are committed but must have empty api_key.
ALLOW_FILES = {
    "tools/chatter/config.example.json",
}


def staged_files() -> list:
    try:
        out = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=AM"],
            capture_output=True, text=True, check=True,
        )
    except Exception:
        return []
    return [p.strip() for p in out.stdout.splitlines() if p.strip()]


def check_file(rel_path: str) -> list:
    issues = []
    p = Path(rel_path)
    name = rel_path.replace("\\", "/")
    if name in ALLOW_FILES:
        # Verify allow-listed files have an empty api_key.
        try:
            content = p.read_text(encoding="utf-8")
            m = re.search(r'"api_key"\s*:\s*"([^"]*)"', content)
            if m and m.group(1):
                issues.append(f"{name}: example config has non-empty api_key")
        except Exception:
            pass
        return issues
    for pat in SECRET_FILENAME_PATTERNS:
        if pat.search(name):
            issues.append(f"{name}: filename matches secret pattern (likely shouldn't be committed)")
            return issues
    if not p.is_file():
        return issues
    try:
        # Skip binaries
        content = p.read_text(encoding="utf-8")
    except Exception:
        return issues
    for pat in CONTENT_PATTERNS:
        m = pat.search(content)
        if m:
            issues.append(f"{name}: content matches potential api-key pattern: {m.group(0)[:80]}...")
    return issues


def main() -> int:
    files = staged_files()
    if not files:
        return 0
    all_issues = []
    for f in files:
        all_issues.extend(check_file(f))
    if all_issues:
        print("REFUSED: potential secrets detected in staged files:", file=sys.stderr)
        for line in all_issues:
            print(f"  - {line}", file=sys.stderr)
        print("If this is a false positive, edit tools/chatter/check_no_secrets.py.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
