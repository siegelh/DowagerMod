from __future__ import annotations

import subprocess
from pathlib import Path

from .models import ChangeSet


class GitManagerError(RuntimeError):
    """Raised when Symphony cannot inspect or publish git state."""


class GitManager:
    def __init__(self, repo_root: Path):
        self._repo_root = repo_root

    def collect_changes(self) -> ChangeSet:
        paths = self._list_changed_paths()
        normalized = tuple(sorted({_normalize_repo_path(path) for path in paths if path.strip()}))
        plan_paths = tuple(
            path
            for path in normalized
            if path.startswith("docs/plans/active/") and path.endswith(".md") and not path.endswith("TEMPLATE.md")
        )
        requires_xml_gate = any(
            path.startswith("CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/")
            for path in normalized
        )
        requires_dll_gate = any(_is_dll_source_path(path) for path in normalized)
        return ChangeSet(
            files=normalized,
            plan_paths=plan_paths,
            requires_xml_gate=requires_xml_gate,
            requires_dll_gate=requires_dll_gate,
        )

    def commit_all(self, message: str) -> str:
        self._git("add", "-A")
        self._git("commit", "-m", message)
        return self.current_head()

    def push_branch(self, branch_name: str) -> None:
        self._git("push", "--set-upstream", "origin", branch_name)

    def current_head(self) -> str:
        return self._git("rev-parse", "HEAD").strip()

    def diff_stat(self) -> str:
        return self._git("diff", "--stat")

    def is_clean(self) -> bool:
        return not any(self._list_changed_paths())

    def _list_changed_paths(self) -> tuple[str, ...]:
        paths = []
        paths.extend(self._git_lines("diff", "--name-only", "--diff-filter=ACMRTUXB"))
        paths.extend(self._git_lines("diff", "--cached", "--name-only", "--diff-filter=ACMRTUXB"))
        paths.extend(self._git_lines("ls-files", "--others", "--exclude-standard"))
        return tuple(paths)

    def _git_lines(self, *args: str) -> list[str]:
        output = self._git(*args)
        return [line.strip() for line in output.splitlines() if line.strip()]

    def _git(self, *args: str) -> str:
        result = subprocess.run(
            ["git", *args],
            cwd=self._repo_root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        stdout = _filter_line_ending_noise(result.stdout)
        stderr = _filter_line_ending_noise(result.stderr)
        if result.returncode != 0:
            message = stderr.strip() or stdout.strip() or f"git {' '.join(args)} failed"
            raise GitManagerError(message)
        return stdout


def _normalize_repo_path(path: str) -> str:
    return path.replace("\\", "/").strip()


def _is_dll_source_path(path: str) -> bool:
    normalized = _normalize_repo_path(path)
    prefix = "third_party/beyond-the-sword-sdk/CvGameCoreDLL/"
    if not normalized.startswith(prefix):
        return False

    file_name = Path(normalized).name
    if file_name.startswith("Makefile"):
        return True

    extension = Path(normalized).suffix.lower()
    return extension in {
        ".c",
        ".cpp",
        ".cc",
        ".h",
        ".hpp",
        ".hh",
        ".inl",
        ".rc",
        ".def",
        ".vcxproj",
        ".sln",
    }


def _filter_line_ending_noise(raw_text: str) -> str:
    filtered = []
    for line in raw_text.splitlines():
        if line.startswith("warning: LF will be replaced by CRLF"):
            continue
        if line.startswith("The file will have its original line endings in your working directory"):
            continue
        filtered.append(line)
    return "\n".join(filtered)
