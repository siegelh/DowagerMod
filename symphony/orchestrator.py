from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .agent_runner import AgentRunner
from .config import SymphonyConfig
from .github_client import GitHubClient
from .logging_utils import log_event
from .models import RunSummary, WorkflowDefinition
from .workflow_loader import render_prompt
from .worktree_manager import WorktreeManager


class SymphonyService:
    def __init__(
        self,
        repo_root: Path,
        workflow: WorkflowDefinition,
        config: SymphonyConfig,
        github: GitHubClient,
        logger,
    ):
        self._repo_root = repo_root
        self._workflow = workflow
        self._config = config
        self._github = github
        self._logger = logger

    def run_once(self, issue_number: int | None = None, dry_run: bool = False) -> RunSummary | None:
        issue = self._github.pick_next_ready_issue(issue_number=issue_number)
        if issue is None:
            log_event(
                self._logger,
                "No eligible Ready issue found",
                event="no_ready_issue",
                requested_issue_number=issue_number,
            )
            return None

        started_at = datetime.now(timezone.utc)
        worktree_manager = WorktreeManager(
            repo_root=self._repo_root,
            workspace_root=self._config.workspace.root,
            base_branch=self._config.workspace.base_branch,
            branch_prefix=self._config.workspace.branch_prefix,
        )
        worktree_target = worktree_manager.describe_target(issue.number, issue.title)

        if dry_run:
            summary = RunSummary(
                issue_number=issue.number,
                issue_title=issue.title,
                branch_name=worktree_target.branch_name,
                workspace_path=str(worktree_target.path),
                started_at=started_at,
                finished_at=datetime.now(timezone.utc),
                outcome="dry_run",
                project_status=issue.project_status,
                note="Selected issue but skipped status updates, worktree creation, and agent run.",
            )
            self._write_summary(summary)
            log_event(
                self._logger,
                "Dry run selected issue",
                event="dry_run_selected",
                issue_number=issue.number,
                branch_name=worktree_target.branch_name,
                workspace_path=str(worktree_target.path),
            )
            return summary

        try:
            self._github.update_status(issue, self._config.github.planning_state)
            log_event(
                self._logger,
                "Moved issue to Planning",
                event="status_transition",
                issue_number=issue.number,
                new_status=self._config.github.planning_state,
            )

            worktree = worktree_manager.ensure_worktree(issue.number, issue.title)
            self._github.update_status(issue, self._config.github.in_progress_state)
            log_event(
                self._logger,
                "Moved issue to In Progress",
                event="status_transition",
                issue_number=issue.number,
                new_status=self._config.github.in_progress_state,
                branch_name=worktree.branch_name,
                workspace_path=str(worktree.path),
                created_worktree=worktree.created_now,
            )

            prompt = render_prompt(
                self._workflow,
                {
                    "issue": issue.template_context(),
                    "attempt": None,
                    "branch_name": worktree.branch_name,
                    "workspace_path": str(worktree.path),
                    "repo_root": str(self._repo_root),
                    "workflow_path": str(self._workflow.path),
                },
            )

            result = AgentRunner(self._config.codex, worktree.path).run_turn(prompt)
            self._github.update_status(issue, self._config.github.human_review_state)
            log_event(
                self._logger,
                "Agent turn completed",
                event="agent_turn_completed",
                issue_number=issue.number,
                turn_status=result.status,
                new_status=self._config.github.human_review_state,
                thread_id=result.thread_id,
                turn_id=result.turn_id,
            )
            summary = RunSummary(
                issue_number=issue.number,
                issue_title=issue.title,
                branch_name=worktree.branch_name,
                workspace_path=str(worktree.path),
                started_at=started_at,
                finished_at=datetime.now(timezone.utc),
                outcome="completed",
                project_status=self._config.github.human_review_state,
                thread_id=result.thread_id,
                turn_id=result.turn_id,
                turn_status=result.status,
                note="Stopped at Human Review. PR creation is intentionally deferred in this slice.",
            )
            self._write_summary(summary)
            return summary
        except Exception as exc:
            try:
                self._github.update_status(issue, self._config.github.blocked_state)
            except Exception as status_exc:  # pragma: no cover
                log_event(
                    self._logger,
                    "Failed to move issue to Blocked after run failure",
                    event="status_transition_failed",
                    issue_number=issue.number,
                    error=str(status_exc),
                )
            log_event(
                self._logger,
                "Agent turn failed",
                event="agent_turn_failed",
                issue_number=issue.number,
                error=str(exc),
                new_status=self._config.github.blocked_state,
            )
            summary = RunSummary(
                issue_number=issue.number,
                issue_title=issue.title,
                branch_name=worktree_target.branch_name,
                workspace_path=str(worktree_target.path),
                started_at=started_at,
                finished_at=datetime.now(timezone.utc),
                outcome="blocked",
                project_status=self._config.github.blocked_state,
                note=str(exc),
            )
            self._write_summary(summary)
            raise

    def _write_summary(self, summary: RunSummary) -> None:
        runs_dir = self._config.runtime.state_root / "runs"
        runs_dir.mkdir(parents=True, exist_ok=True)
        timestamp = summary.finished_at.strftime("%Y%m%dT%H%M%SZ")
        filename = f"{summary.issue_number}-{timestamp}.json"
        (runs_dir / filename).write_text(json.dumps(summary.to_dict(), indent=2), encoding="utf-8")
