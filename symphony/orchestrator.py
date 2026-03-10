from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .agent_runner import AgentRunner
from .config import SymphonyConfig
from .git_manager import GitManager
from .github_client import GitHubClient
from .handoff import (
    build_blocked_issue_comment,
    build_commit_message,
    build_pull_request_body,
    build_pull_request_title,
    build_success_issue_comment,
)
from .logging_utils import log_event
from .models import ChangeSet, RunSummary, WorkflowDefinition
from .validation_runner import ValidationRunner
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

        empty_change_set = ChangeSet(
            files=(),
            plan_paths=(),
            requires_xml_gate=False,
            requires_dll_gate=False,
        )
        change_set = None
        validation = None
        commit_sha = None
        pull_request = None
        issue_comment_url = None
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
            git_manager = GitManager(worktree.path)
            change_set = git_manager.collect_changes()
            if not change_set.files:
                raise RuntimeError("Agent turn completed without producing any reviewable file changes.")

            validation = ValidationRunner(worktree.path).run(change_set)
            log_event(
                self._logger,
                "Validation completed",
                event="validation_completed",
                issue_number=issue.number,
                validation_required=validation.required,
                validation_passed=validation.passed,
                validation_command=(" ".join(validation.command) if validation.command else None),
            )
            if not validation.passed:
                raise RuntimeError("Repo-native validation failed.")

            commit_sha = git_manager.commit_all(build_commit_message(issue, change_set.plan_paths))
            git_manager.push_branch(worktree.branch_name)
            pull_request = self._github.get_or_create_draft_pull_request(
                branch_name=worktree.branch_name,
                base_branch=self._config.workspace.base_branch,
                title=build_pull_request_title(issue),
                body=build_pull_request_body(issue, worktree.branch_name, change_set, validation),
            )
            issue_comment_url = self._github.create_issue_comment(
                issue.number,
                build_success_issue_comment(
                    issue,
                    worktree.branch_name,
                    str(worktree.path),
                    pull_request,
                    change_set,
                    validation,
                ),
            )
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
                commit_sha=commit_sha,
                pull_request_url=pull_request.url,
                issue_comment_url=issue_comment_url,
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
                commit_sha=commit_sha,
                pull_request_number=pull_request.number,
                pull_request_url=pull_request.url,
                issue_comment_url=issue_comment_url,
                changed_files=change_set.files,
                plan_paths=change_set.plan_paths,
                validation_required=validation.required,
                validation_passed=validation.passed,
                validation_command=" ".join(validation.command),
                note="Validated, pushed, and handed off via draft PR for human review.",
            )
            self._write_summary(summary)
            return summary
        except Exception as exc:
            if issue_comment_url is None:
                try:
                    issue_comment_url = self._github.create_issue_comment(
                        issue.number,
                        build_blocked_issue_comment(
                            issue,
                            worktree_target.branch_name,
                            str(worktree_target.path),
                            change_set or empty_change_set,
                            str(exc),
                            validation,
                        ),
                    )
                except Exception as comment_exc:  # pragma: no cover
                    log_event(
                        self._logger,
                        "Failed to post blocked issue comment",
                        event="issue_comment_failed",
                        issue_number=issue.number,
                        error=str(comment_exc),
                    )
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
                commit_sha=commit_sha,
                pull_request_url=(pull_request.url if pull_request is not None else None),
                issue_comment_url=issue_comment_url,
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
                commit_sha=commit_sha,
                pull_request_number=(pull_request.number if pull_request is not None else None),
                pull_request_url=(pull_request.url if pull_request is not None else None),
                issue_comment_url=issue_comment_url,
                changed_files=(change_set.files if change_set is not None else ()),
                plan_paths=(change_set.plan_paths if change_set is not None else ()),
                validation_required=(validation.required if validation is not None else False),
                validation_passed=(validation.passed if validation is not None else None),
                validation_command=(" ".join(validation.command) if validation is not None and validation.command else None),
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
