from __future__ import annotations

import logging
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

from symphony.config import CodexConfig, GitHubConfig, RuntimeConfig, SquadConfig, SymphonyConfig, WorkspaceConfig
from symphony.models import (
    AgentRunResult,
    ChangeSet,
    GitHubIssue,
    PullRequestInfo,
    ValidationResult,
    WorkflowDefinition,
)
from symphony.orchestrator import SymphonyService


class SymphonyOrchestratorTests(unittest.TestCase):
    def test_run_once_creates_review_handoff_after_successful_validation(self) -> None:
        now = datetime.now(timezone.utc)
        issue = _build_issue(43, "Ready")

        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            _write_squad_files(repo_root)
            workflow = WorkflowDefinition(path=repo_root / "symphony" / "WORKFLOW.md", config={}, prompt_template="Issue {{ issue.number }}")
            config = _build_config(repo_root, workflow)

            github = mock.Mock()
            github.pick_next_ready_issue.return_value = issue
            github.pick_next_inbox_issue.return_value = None
            github.list_open_symphony_pull_requests.return_value = ()
            github.create_issue_comment.return_value = "https://example.com/comment/12"
            github.get_or_create_draft_pull_request.return_value = PullRequestInfo(
                number=12,
                url="https://example.com/pr/12",
                title=issue.title,
                is_draft=True,
                existing=False,
                head_ref_name="symphony/43-fix",
                base_ref_name="agent-baseline",
            )

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
                    final_message="ok",
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

        self.assertEqual(summary.job_name, "implement_issue")
        self.assertEqual(summary.outcome, "completed")
        self.assertEqual(summary.project_status, "Human Review")
        self.assertEqual(summary.pull_request_url, "https://example.com/pr/12")
        self.assertEqual(summary.commit_sha, "abc123")
        github.update_status.assert_any_call(issue, "Planning")
        github.update_status.assert_any_call(issue, "In Progress")
        github.update_status.assert_any_call(issue, "Human Review")

    def test_run_once_moves_issue_to_blocked_when_validation_fails(self) -> None:
        issue = _build_issue(44, "Ready")

        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            _write_squad_files(repo_root)
            workflow = WorkflowDefinition(path=repo_root / "symphony" / "WORKFLOW.md", config={}, prompt_template="Issue {{ issue.number }}")
            config = _build_config(repo_root, workflow)

            github = mock.Mock()
            github.pick_next_ready_issue.return_value = issue
            github.pick_next_inbox_issue.return_value = None
            github.list_open_symphony_pull_requests.return_value = ()
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
                    final_message="ok",
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

    def test_triage_issue_moves_ready_and_comments(self) -> None:
        issue = _build_issue(50, "Inbox")

        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            _write_squad_files(repo_root)
            workflow = WorkflowDefinition(path=repo_root / "symphony" / "WORKFLOW.md", config={}, prompt_template="body")
            config = _build_config(repo_root, workflow)

            github = mock.Mock()
            github.pick_next_ready_issue.return_value = None
            github.pick_next_inbox_issue.return_value = issue
            github.list_open_symphony_pull_requests.return_value = ()
            github.create_issue_comment.return_value = "https://example.com/comment/50"

            with mock.patch("symphony.orchestrator.AgentRunner") as agent_runner_cls:
                agent_runner_cls.return_value.run_turn.return_value = AgentRunResult(
                    thread_id="thread-3",
                    turn_id="turn-3",
                    status="completed",
                    final_message='{"action":"ready","summary":"Specific enough for implementation.","missing":[]}',
                )
                service = SymphonyService(
                    repo_root=repo_root,
                    workflow=workflow,
                    config=config,
                    github=github,
                    logger=logging.getLogger("test-symphony"),
                )
                summary = service.run_once(job_name="triage_issue", issue_number=50)

        self.assertEqual(summary.job_name, "triage_issue")
        self.assertEqual(summary.project_status, "Ready")
        github.update_status.assert_any_call(issue, "Planning")
        github.update_status.assert_any_call(issue, "Ready")


def _build_issue(number: int, project_status: str) -> GitHubIssue:
    now = datetime.now(timezone.utc)
    return GitHubIssue(
        node_id=f"node-{number}",
        project_item_id=f"item-{number}",
        repository_full_name="siegelh/DowagerMod",
        number=number,
        title=f"Issue {number}",
        body="body",
        state="OPEN",
        url=f"https://example.com/{number}",
        created_at=now,
        updated_at=now,
        labels=(),
        assignees=(),
        project_status=project_status,
    )


def _build_config(repo_root: Path, workflow: WorkflowDefinition) -> SymphonyConfig:
    return SymphonyConfig(
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
        runtime=RuntimeConfig(
            state_root=repo_root / "runtime",
            poll_interval_seconds=60,
            error_backoff_seconds=120,
        ),
        squad=SquadConfig(
            enabled=True,
            team_path=repo_root / "symphony" / "squad" / "team.md",
            jobs_path=repo_root / "symphony" / "squad" / "jobs.yaml",
            schedule_path=repo_root / "symphony" / "squad" / "schedule.yaml",
            max_heavy_jobs=1,
            max_light_jobs=1,
            kickoff_comments_enabled=True,
            review_comments_enabled=True,
            triage_comments_enabled=True,
            hygiene_issue_title="Symphony hygiene report",
        ),
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


def _write_squad_files(repo_root: Path) -> None:
    roles_dir = repo_root / "symphony" / "squad" / "roles"
    roles_dir.mkdir(parents=True, exist_ok=True)
    (repo_root / "symphony" / "squad" / "team.md").write_text("team", encoding="utf-8")
    for role in ("lead", "implementer", "reviewer", "triage", "hygiene", "research"):
        (roles_dir / f"{role}.md").write_text(role, encoding="utf-8")
    (repo_root / "symphony" / "squad" / "jobs.yaml").write_text(
        "jobs:\n"
        "  implement_issue:\n"
        "    kind: issue\n"
        "    roles: [lead, implementer, reviewer]\n"
        "    concurrency: heavy\n"
        "    priority: 100\n"
        "    source_statuses: [Ready]\n"
        "  triage_issue:\n"
        "    kind: issue\n"
        "    roles: [triage]\n"
        "    concurrency: light\n"
        "    priority: 80\n"
        "    source_statuses: [Inbox]\n"
        "  review_pr:\n"
        "    kind: pull_request\n"
        "    roles: [reviewer]\n"
        "    concurrency: light\n"
        "    priority: 60\n"
        "  hygiene_scan:\n"
        "    kind: scheduled\n"
        "    roles: [hygiene]\n"
        "    concurrency: light\n"
        "    priority: 40\n"
        "    schedule_key: hygiene_scan\n",
        encoding="utf-8",
    )
    (repo_root / "symphony" / "squad" / "schedule.yaml").write_text(
        "schedules:\n  hygiene_scan:\n    interval_seconds: 3600\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    unittest.main()
