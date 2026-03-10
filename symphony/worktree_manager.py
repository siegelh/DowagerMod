from __future__ import annotations

import re
import subprocess
from pathlib import Path

from .models import WorktreeInfo


class WorktreeError(RuntimeError):
    """Raised when Symphony cannot create or reuse a git worktree."""


class WorktreeManager:
    def __init__(self, repo_root: Path, workspace_root: Path, base_branch: str, branch_prefix: str):
        self._repo_root = repo_root
        self._workspace_root = workspace_root
        self._base_branch = base_branch
        self._branch_prefix = branch_prefix

    def ensure_worktree(self, issue_number: int, issue_title: str) -> WorktreeInfo:
        target = self.describe_target(issue_number, issue_title)
        self._workspace_root.mkdir(parents=True, exist_ok=True)

        existing = self._worktree_for_branch(target.branch_name)
        if existing is not None:
            return WorktreeInfo(branch_name=target.branch_name, path=existing, created_now=False)

        if target.path.exists():
            if self._is_git_worktree(target.path):
                return WorktreeInfo(branch_name=target.branch_name, path=target.path, created_now=False)
            raise WorktreeError(f"Refusing to use non-worktree path {target.path}")

        if self._branch_exists(target.branch_name):
            self._git("worktree", "add", str(target.path), target.branch_name)
        else:
            self._git("worktree", "add", "-b", target.branch_name, str(target.path), self._base_branch)
        return WorktreeInfo(branch_name=target.branch_name, path=target.path, created_now=True)

    def describe_target(self, issue_number: int, issue_title: str) -> WorktreeInfo:
        slug = _slugify(issue_title)
        branch_name = f"{self._branch_prefix}/{issue_number}-{slug}"
        return WorktreeInfo(
            branch_name=branch_name,
            path=(self._workspace_root / f"gh-{issue_number}").resolve(),
            created_now=False,
        )

    def _branch_exists(self, branch_name: str) -> bool:
        result = subprocess.run(
            ["git", "show-ref", "--verify", "--quiet", f"refs/heads/{branch_name}"],
            cwd=self._repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode == 0

    def _is_git_worktree(self, path: Path) -> bool:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=path,
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode == 0

    def _worktree_for_branch(self, branch_name: str) -> Path | None:
        result = self._git("worktree", "list", "--porcelain")
        current_path: Path | None = None
        current_branch: str | None = None
        for line in result.splitlines():
            if line.startswith("worktree "):
                current_path = Path(line.split(" ", 1)[1])
                current_branch = None
            elif line.startswith("branch "):
                current_branch = line.split(" ", 1)[1].removeprefix("refs/heads/")
            elif not line.strip():
                if current_branch == branch_name and current_path is not None:
                    return current_path.resolve()
                current_path = None
                current_branch = None
        if current_branch == branch_name and current_path is not None:
            return current_path.resolve()
        return None

    def _git(self, *args: str) -> str:
        result = subprocess.run(
            ["git", *args],
            cwd=self._repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            stderr = result.stderr.strip() or result.stdout.strip()
            raise WorktreeError(f"git {' '.join(args)} failed: {stderr}")
        return result.stdout


def _slugify(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip("-._").lower()
    return cleaned or "issue"
