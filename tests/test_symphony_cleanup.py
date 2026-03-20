from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

from symphony.cleanup import CleanupManager
from symphony.config import GitHubConfig, WorkspaceConfig
from symphony.models import CleanupCandidate, GitHubIssue, PullRequestInfo, WorktreeInfo


class CleanupManagerTests(unittest.TestCase):
    def test_scan_auto_cleanup_candidates_requires_closed_issue_and_merged_pr(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            github_config = GitHubConfig(
                owner="siegelh",
                owner_type="user",
                repo="DowagerMod",
                project_number=1,
                status_field="Status",
                ready_state="Ready",
                planning_state="Planning",
                in_progress_state="In Progress",
                blocked_state="Blocked",
                human_review_state="Human Review",
                done_state="Done",
                blocker_labels=(),
                token="x",
            )
            workspace_config = WorkspaceConfig(
                root=repo_root / "workspaces",
                base_branch="agent-baseline",
                branch_prefix="symphony",
            )
            manager = CleanupManager(repo_root, github_config, workspace_config)

            with mock.patch.object(
                manager,
                "scan",
                return_value=(
                    CleanupCandidate(
                        issue_number=43,
                        issue_title="closed and merged",
                        issue_state="CLOSED",
                        project_status="Human Review",
                        branch_name="symphony/43-fix",
                        workspace_path=str(repo_root / "workspaces" / "gh-43"),
                        has_open_pull_request=False,
                        merged_pull_request_url="https://example.com/pr/43",
                        is_clean=True,
                        eligible=True,
                        reasons=(),
                    ),
                    CleanupCandidate(
                        issue_number=44,
                        issue_title="closed but no merged pr",
                        issue_state="CLOSED",
                        project_status="Done",
                        branch_name="symphony/44-fix",
                        workspace_path=str(repo_root / "workspaces" / "gh-44"),
                        has_open_pull_request=False,
                        merged_pull_request_url=None,
                        is_clean=True,
                        eligible=True,
                        reasons=(),
                    ),
                    CleanupCandidate(
                        issue_number=45,
                        issue_title="merged but issue still open",
                        issue_state="OPEN",
                        project_status="Done",
                        branch_name="symphony/45-fix",
                        workspace_path=str(repo_root / "workspaces" / "gh-45"),
                        has_open_pull_request=False,
                        merged_pull_request_url="https://example.com/pr/45",
                        is_clean=True,
                        eligible=True,
                        reasons=(),
                    ),
                ),
            ):
                candidates = manager.scan_auto_cleanup_candidates()

        self.assertEqual([candidate.issue_number for candidate in candidates], [43])

    def test_scan_marks_merged_clean_issue_as_eligible(self) -> None:
        now = datetime.now(timezone.utc)
        issue = GitHubIssue(
            node_id="node-43",
            project_item_id="item-43",
            repository_full_name="siegelh/DowagerMod",
            number=43,
            title="Fix issue",
            body="",
            state="CLOSED",
            url="https://example.com/issues/43",
            created_at=now,
            updated_at=now,
            labels=(),
            assignees=(),
            project_status="Human Review",
        )

        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            github_config = GitHubConfig(
                owner="siegelh",
                owner_type="user",
                repo="DowagerMod",
                project_number=1,
                status_field="Status",
                ready_state="Ready",
                planning_state="Planning",
                in_progress_state="In Progress",
                blocked_state="Blocked",
                human_review_state="Human Review",
                done_state="Done",
                blocker_labels=(),
                token="x",
            )
            workspace_config = WorkspaceConfig(
                root=repo_root / "workspaces",
                base_branch="agent-baseline",
                branch_prefix="symphony",
            )

            with mock.patch("symphony.cleanup.GitHubClient") as github_cls, mock.patch(
                "symphony.cleanup.WorktreeManager"
            ) as worktree_cls, mock.patch("symphony.cleanup.GitManager") as git_manager_cls:
                github = github_cls.return_value
                github.get_project_issue.return_value = issue
                github.find_pull_request.return_value = PullRequestInfo(
                    number=44,
                    url="https://example.com/pr/44",
                    title="Fix issue",
                    is_draft=False,
                    existing=True,
                    state="CLOSED",
                    merged=True,
                )

                worktree = WorktreeInfo(
                    branch_name="symphony/43-fix-issue",
                    path=repo_root / "workspaces" / "gh-43",
                    created_now=False,
                )
                worktree_cls.return_value.list_issue_worktrees.return_value = (worktree,)
                git_manager_cls.return_value.is_clean.return_value = True

                manager = CleanupManager(repo_root, github_config, workspace_config)
                candidates = manager.scan()

        self.assertEqual(len(candidates), 1)
        self.assertTrue(candidates[0].eligible)
        self.assertEqual(candidates[0].merged_pull_request_url, "https://example.com/pr/44")

    def test_scan_blocks_dirty_or_open_pull_request_worktrees(self) -> None:
        now = datetime.now(timezone.utc)
        issue = GitHubIssue(
            node_id="node-45",
            project_item_id="item-45",
            repository_full_name="siegelh/DowagerMod",
            number=45,
            title="Open review",
            body="",
            state="OPEN",
            url="https://example.com/issues/45",
            created_at=now,
            updated_at=now,
            labels=(),
            assignees=(),
            project_status="Human Review",
        )

        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            github_config = GitHubConfig(
                owner="siegelh",
                owner_type="user",
                repo="DowagerMod",
                project_number=1,
                status_field="Status",
                ready_state="Ready",
                planning_state="Planning",
                in_progress_state="In Progress",
                blocked_state="Blocked",
                human_review_state="Human Review",
                done_state="Done",
                blocker_labels=(),
                token="x",
            )
            workspace_config = WorkspaceConfig(
                root=repo_root / "workspaces",
                base_branch="agent-baseline",
                branch_prefix="symphony",
            )

            with mock.patch("symphony.cleanup.GitHubClient") as github_cls, mock.patch(
                "symphony.cleanup.WorktreeManager"
            ) as worktree_cls, mock.patch("symphony.cleanup.GitManager") as git_manager_cls:
                github = github_cls.return_value
                github.get_project_issue.return_value = issue
                github.find_pull_request.return_value = PullRequestInfo(
                    number=45,
                    url="https://example.com/pr/45",
                    title="Open review",
                    is_draft=False,
                    existing=True,
                    state="OPEN",
                    merged=False,
                )

                worktree = WorktreeInfo(
                    branch_name="symphony/45-open-review",
                    path=repo_root / "workspaces" / "gh-45",
                    created_now=False,
                )
                worktree_cls.return_value.list_issue_worktrees.return_value = (worktree,)
                git_manager_cls.return_value.is_clean.return_value = False

                manager = CleanupManager(repo_root, github_config, workspace_config)
                candidates = manager.scan()

        self.assertEqual(len(candidates), 1)
        self.assertFalse(candidates[0].eligible)
        self.assertIn("dirty_worktree", candidates[0].reasons)
        self.assertIn("open_pull_request", candidates[0].reasons)
        self.assertIn("not_done", candidates[0].reasons)

    def test_apply_updates_done_and_removes_worktree_and_branch(self) -> None:
        now = datetime.now(timezone.utc)
        issue = GitHubIssue(
            node_id="node-43",
            project_item_id="item-43",
            repository_full_name="siegelh/DowagerMod",
            number=43,
            title="Fix issue",
            body="",
            state="CLOSED",
            url="https://example.com/issues/43",
            created_at=now,
            updated_at=now,
            labels=(),
            assignees=(),
            project_status="Human Review",
        )

        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            github_config = GitHubConfig(
                owner="siegelh",
                owner_type="user",
                repo="DowagerMod",
                project_number=1,
                status_field="Status",
                ready_state="Ready",
                planning_state="Planning",
                in_progress_state="In Progress",
                blocked_state="Blocked",
                human_review_state="Human Review",
                done_state="Done",
                blocker_labels=(),
                token="x",
            )
            workspace_config = WorkspaceConfig(
                root=repo_root / "workspaces",
                base_branch="agent-baseline",
                branch_prefix="symphony",
            )

            with mock.patch("symphony.cleanup.GitHubClient") as github_cls, mock.patch(
                "symphony.cleanup.WorktreeManager"
            ) as worktree_cls:
                github = github_cls.return_value
                github.get_project_issue.return_value = issue

                manager = CleanupManager(repo_root, github_config, workspace_config)
                apply_candidate = CleanupCandidate(
                    issue_number=43,
                    issue_title="Fix issue",
                    issue_state="CLOSED",
                    project_status="Human Review",
                    branch_name="symphony/43-fix-issue",
                    workspace_path=str(repo_root / "workspaces" / "gh-43"),
                    has_open_pull_request=False,
                    merged_pull_request_url="https://example.com/pr/44",
                    is_clean=True,
                    eligible=True,
                    reasons=(),
                )

                cleaned = manager.apply((apply_candidate,))

        self.assertEqual(len(cleaned), 1)
        github.update_status.assert_called_once_with(issue, "Done")
        worktree_cls.return_value.remove_worktree.assert_called_once()
        worktree_cls.return_value.delete_branch.assert_called_once_with("symphony/43-fix-issue")


if __name__ == "__main__":
    unittest.main()
