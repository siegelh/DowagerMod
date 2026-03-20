from __future__ import annotations

import re
from pathlib import Path

from .config import GitHubConfig, WorkspaceConfig
from .git_manager import GitManager
from .github_client import GitHubClient
from .models import CleanupCandidate
from .worktree_manager import WorktreeManager


class CleanupManager:
    def __init__(
        self,
        repo_root: Path,
        github_config: GitHubConfig,
        workspace_config: WorkspaceConfig,
    ):
        self._repo_root = repo_root
        self._github_config = github_config
        self._workspace_config = workspace_config
        self._github = GitHubClient(github_config)
        self._worktrees = WorktreeManager(
            repo_root=repo_root,
            workspace_root=workspace_config.root,
            base_branch=workspace_config.base_branch,
            branch_prefix=workspace_config.branch_prefix,
        )

    def scan(self, issue_number: int | None = None) -> tuple[CleanupCandidate, ...]:
        candidates: list[CleanupCandidate] = []
        for worktree in self._worktrees.list_issue_worktrees():
            parsed_issue_number = _issue_number_from_branch(worktree.branch_name)
            if parsed_issue_number is None:
                continue
            if issue_number is not None and parsed_issue_number != issue_number:
                continue

            issue = self._github.get_project_issue(parsed_issue_number)
            pull_request = self._github.find_pull_request(worktree.branch_name, state="all")
            is_clean = GitManager(worktree.path).is_clean()
            reasons: list[str] = []

            if not is_clean:
                reasons.append("dirty_worktree")

            has_open_pull_request = pull_request is not None and pull_request.state == "OPEN" and not pull_request.merged
            if has_open_pull_request:
                reasons.append("open_pull_request")

            has_done_signal = False
            if issue is None:
                reasons.append("issue_not_on_project")
                issue_title = worktree.branch_name
                issue_state = "UNKNOWN"
                project_status = "UNKNOWN"
            else:
                issue_title = issue.title
                issue_state = issue.state
                project_status = issue.project_status
                if issue.state.upper() == "CLOSED":
                    has_done_signal = True
                if issue.project_status == self._github_config.done_state:
                    has_done_signal = True

            if pull_request is not None and pull_request.merged:
                has_done_signal = True

            if not has_done_signal:
                reasons.append("not_done")

            candidates.append(
                CleanupCandidate(
                    issue_number=parsed_issue_number,
                    issue_title=issue_title,
                    issue_state=issue_state,
                    project_status=project_status,
                    branch_name=worktree.branch_name,
                    workspace_path=str(worktree.path),
                    has_open_pull_request=has_open_pull_request,
                    merged_pull_request_url=(pull_request.url if pull_request is not None and pull_request.merged else None),
                    is_clean=is_clean,
                    eligible=(not reasons),
                    reasons=tuple(reasons),
                )
            )
        candidates.sort(key=lambda candidate: candidate.issue_number)
        return tuple(candidates)

    def scan_auto_cleanup_candidates(self, issue_number: int | None = None) -> tuple[CleanupCandidate, ...]:
        return tuple(
            candidate
            for candidate in self.scan(issue_number=issue_number)
            if candidate.eligible
            and candidate.issue_state.upper() == "CLOSED"
            and candidate.merged_pull_request_url is not None
        )

    def apply(self, candidates: tuple[CleanupCandidate, ...]) -> tuple[CleanupCandidate, ...]:
        cleaned: list[CleanupCandidate] = []
        for candidate in candidates:
            if not candidate.eligible:
                continue

            issue = self._github.get_project_issue(candidate.issue_number)
            if issue is not None and issue.project_status != self._github_config.done_state:
                self._github.update_status(issue, self._github_config.done_state)

            self._worktrees.remove_worktree(Path(candidate.workspace_path))
            self._worktrees.delete_branch(candidate.branch_name)
            cleaned.append(candidate)
        return tuple(cleaned)


def _issue_number_from_branch(branch_name: str) -> int | None:
    match = re.match(r"^[^/]+/(\d+)-", branch_name)
    if match is None:
        return None
    return int(match.group(1))
