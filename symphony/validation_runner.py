from __future__ import annotations

import subprocess
from pathlib import Path

from .models import ChangeSet, ValidationResult


class ValidationRunner:
    def __init__(self, repo_root: Path):
        self._repo_root = repo_root

    def run(self, change_set: ChangeSet) -> ValidationResult:
        if not (change_set.requires_xml_gate or change_set.requires_dll_gate):
            return ValidationResult(
                required=False,
                passed=True,
                command=(),
                output="No repo-native validation gate required for this change set.",
            )

        script_path = self._repo_root / "tools" / "test_gate.ps1"
        command = [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(script_path),
            "-RepoRoot",
            str(self._repo_root),
        ]
        if change_set.requires_dll_gate:
            command.append("-CheckDll")

        result = subprocess.run(
            command,
            cwd=self._repo_root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        output = "\n".join(part for part in [result.stdout.strip(), result.stderr.strip()] if part)
        return ValidationResult(
            required=True,
            passed=result.returncode == 0,
            command=tuple(command),
            output=output,
        )
