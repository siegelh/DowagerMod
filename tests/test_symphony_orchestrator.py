from __future__ import annotations

import logging
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

from symphony.config import CodexConfig, GitHubConfig, RuntimeConfig, SymphonyConfig, WorkspaceConfig
from symphony.models import AgentRunResult, ChangeSet, GitHubIssue, PullRequestInfo, ValidationResult, WorkflowDefinition
from symphony.orchestrator import SymphonyService


class SymphonyOrchestratorTests(unittest.TestCase):
    def test_run_once_creates_review_handoff_after_successful_validation(self) -> None:
        now = datetime.now(timezone.utc)
        issue = GitHubIssue(
            node_id="node-43",
            project_item_id="item-43",
            repository_full_name="siegelh/DowagerMod",
            number=43,
            title="Fix city-center luxury industry eligibility",
            body="body",
            state="OPEN",
            url="https://example.com/43",
            created_at=now,
            updated_at=now,
            labels=(),
            assignees=(),
            project_status="Ready",
        )

        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            workflow = WorkflowDefinition(path=repo_root / "symphony" / "WORKFLOW.md", config={}, prompt_template="Issue {{ issue.number }}")
            config = SymphonyConfig(
                workflow_path=workflow.path,
                github=GitHubConfig(
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
                ),
                workspace=WorkspaceConfig(
                    root=repo_root / "workspaces",
                    base_branch="agent-baseline",
                    branch_prefix="symphony",
                ),
                runtime=RuntimeConfig(state_root=repo_root / "runtime"),
                codex=CodexConfig(
                    command=("codex", "app-server"),
                    approval_policy="never",
                    thread_sandbox="danger-full-access",
                    turn_sandbox_policy="danger-full-access",
                    model="gpt-5-codex",
                    model_provider="openai",
                    effort="low",
                    read_timeout_ms=1000,
                    turn_timeout_ms=1000,
                    developer_instructions="dev",
                    base_instructions="base",
                ),
            )

            github = mock.Mock()
            github.pick_next_ready_issue.return_value = issue
            github.get_or_create_draft_pull_request.return_value = PullRequestInfo(
                number=12,
                url="https://example.com/pr/12",
                title=issue.title,
                is_draft=True,
                existing=False,
            )
            github.create_issue_comment.return_value = "https://example.com/comment/12"

            worktree_info = mock.Mock(branch_name="symphony/43-fix", path=repo_root / "wt" / "gh-43", created_now=True)
            change_set = ChangeSet(
                files=("third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvCity.cpp",),
                plan_paths=(),
                requires_xml_gate=False,
                requires_dll_gate=True,
            )
            validation = ValidationResult(
                required=True,
                passed=True,
                command=("powershell", "-File", "tools/test_gate.ps1", "-CheckDll"),
                output="[GATE] OK",
            )

            with mock.patch("symphony.orchestrator.WorktreeManager") as worktree_manager_cls, mock.patch(
                "symphony.orchestrator.AgentRunner"
            ) as agent_runner_cls, mock.patch("symphony.orchestrator.GitManager") as git_manager_cls, mock.patch(
                "symphony.orchestrator.ValidationRunner"
            ) as validation_runner_cls:
                worktree_manager = worktree_manager_cls.return_value
                worktree_manager.describe_target.return_value = worktree_info
                worktree_manager.ensure_worktree.return_value = worktree_info

                agent_runner = agent_runner_cls.return_value
                agent_runner.run_turn.return_value = AgentRunResult(
                    thread_id="thread-1",
                    turn_id="turn-1",
                    status="completed",
                )

                git_manager = git_manager_cls.return_value
                git_manager.collect_changes.return_value = change_set
                git_manager.commit_all.return_value = "abc123"

                validation_runner = validation_runner_cls.return_value
                validation_runner.run.return_value = validation

                service = SymphonyService(
                    repo_root=repo_root,
                    workflow=workflow,
                    config=config,
                    github=github,
                    logger=logging.getLogger("test-symphony"),
                )
                summary = service.run_once(issue_number=43, dry_run=False)

        self.assertEqual(summary.outcome, "completed")
        self.assertEqual(summary.project_status, "Human Review")
        self.assertEqual(summary.pull_request_url, "https://example.com/pr/12")
        self.assertEqual(summary.issue_comment_url, "https://example.com/comment/12")
        self.assertEqual(summary.commit_sha, "abc123")
        github.update_status.assert_any_call(issue, "Planning")
        github.update_status.assert_any_call(issue, "In Progress")
        github.update_status.assert_any_call(issue, "Human Review")

    def test_run_once_moves_issue_to_blocked_when_validation_fails(self) -> None:
        now = datetime.now(timezone.utc)
        issue = GitHubIssue(
            node_id="node-44",
            project_item_id="item-44",
            repository_full_name="siegelh/DowagerMod",
            number=44,
            title="Break validation",
            body="body",
            state="OPEN",
            url="https://example.com/44",
            created_at=now,
            updated_at=now,
            labels=(),
            assignees=(),
            project_status="Ready",
        )

        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            workflow = WorkflowDefinition(path=repo_root / "symphony" / "WORKFLOW.md", config={}, prompt_template="Issue {{ issue.number }}")
            config = SymphonyConfig(
                workflow_path=workflow.path,
                github=GitHubConfig(
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
                ),
                workspace=WorkspaceConfig(
                    root=repo_root / "workspaces",
                    base_branch="agent-baseline",
                    branch_prefix="symphony",
                ),
                runtime=RuntimeConfig(state_root=repo_root / "runtime"),
                codex=CodexConfig(
                    command=("codex", "app-server"),
                    approval_policy="never",
                    thread_sandbox="danger-full-access",
                    turn_sandbox_policy="danger-full-access",
                    model="gpt-5-codex",
                    model_provider="openai",
                    effort="low",
                    read_timeout_ms=1000,
                    turn_timeout_ms=1000,
                    developer_instructions="dev",
                    base_instructions="base",
                ),
            )

            github = mock.Mock()
            github.pick_next_ready_issue.return_value = issue
            github.create_issue_comment.return_value = "https://example.com/comment/44"

            worktree_info = mock.Mock(branch_name="symphony/44-break", path=repo_root / "wt" / "gh-44", created_now=True)
            change_set = ChangeSet(
                files=("third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvCity.cpp",),
                plan_paths=(),
                requires_xml_gate=False,
                requires_dll_gate=True,
            )
            validation = ValidationResult(
                required=True,
                passed=False,
                command=("powershell", "-File", "tools/test_gate.ps1", "-CheckDll"),
                output="[GATE] DLL build failed",
            )

            with mock.patch("symphony.orchestrator.WorktreeManager") as worktree_manager_cls, mock.patch(
                "symphony.orchestrator.AgentRunner"
            ) as agent_runner_cls, mock.patch("symphony.orchestrator.GitManager") as git_manager_cls, mock.patch(
                "symphony.orchestrator.ValidationRunner"
            ) as validation_runner_cls:
                worktree_manager = worktree_manager_cls.return_value
                worktree_manager.describe_target.return_value = worktree_info
                worktree_manager.ensure_worktree.return_value = worktree_info

                agent_runner = agent_runner_cls.return_value
                agent_runner.run_turn.return_value = AgentRunResult(
                    thread_id="thread-2",
                    turn_id="turn-2",
                    status="completed",
                )

                git_manager = git_manager_cls.return_value
                git_manager.collect_changes.return_value = change_set

                validation_runner = validation_runner_cls.return_value
                validation_runner.run.return_value = validation

                service = SymphonyService(
                    repo_root=repo_root,
                    workflow=workflow,
                    config=config,
                    github=github,
                    logger=logging.getLogger("test-symphony"),
                )

                with self.assertRaises(RuntimeError):
                    service.run_once(issue_number=44, dry_run=False)

        github.update_status.assert_any_call(issue, "Blocked")
        github.create_issue_comment.assert_called()


if __name__ == "__main__":
    unittest.main()
