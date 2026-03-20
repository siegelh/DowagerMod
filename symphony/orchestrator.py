from __future__ import annotations

import json
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from .agent_output import AgentOutputError, extract_json_object
from .agent_runner import AgentRunner
from .cleanup import CleanupManager
from .concurrency import ConcurrencyManager
from .config import CodexConfig, SymphonyConfig
from .git_manager import GitManager
from .github_client import GitHubClient
from .handoff import (
    build_blocked_issue_comment,
    build_commit_message,
    build_hygiene_issue_body,
    build_lead_kickoff_comment,
    build_pr_review_comment,
    build_pull_request_body,
    build_pull_request_title,
    build_reviewer_issue_comment,
    build_triage_comment,
)
from .history import RunHistory
from .logging_utils import log_event
from .models import ChangeSet, GitHubIssue, JobCandidate, PullRequestInfo, RunSummary, ValidationResult, WorkflowDefinition
from .role_prompt_builder import RolePromptBuilder
from .router import SquadRouter, issue_number_from_branch
from .squad_registry import load_squad_registry
from .validation_runner import ValidationRunner
from .worktree_manager import WorktreeManager

StatusHook = Callable[..., None]


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
        self._registry = load_squad_registry(config.squad)
        self._prompt_builder = RolePromptBuilder(workflow, self._registry)
        self._history = RunHistory(config.runtime.state_root)
        self._router = SquadRouter(github, config, self._registry, self._history)
        self._concurrency = ConcurrencyManager(config.squad)
        self._cleanup = CleanupManager(
            repo_root=repo_root,
            github_config=config.github,
            workspace_config=config.workspace,
        )

    def run_once(
        self,
        issue_number: int | None = None,
        dry_run: bool = False,
        job_name: str | None = None,
        pull_request_number: int | None = None,
        status_hook: StatusHook | None = None,
    ) -> RunSummary | None:
        candidate = self._router.pick_next(
            explicit_job=job_name,
            issue_number=issue_number,
            pull_request_number=pull_request_number,
        )
        if candidate is None:
            log_event(
                self._logger,
                "No eligible squad job found",
                event="no_job_candidate",
                requested_issue_number=issue_number,
                requested_pull_request_number=pull_request_number,
                requested_job=job_name,
            )
            return None

        job = self._registry.get_job(candidate.job_name)
        decision = self._concurrency.can_run(job)
        if not decision.allowed:
            raise RuntimeError(f"Concurrency rule blocked {candidate.job_name}: {decision.reason}")

        if dry_run:
            return self._build_dry_run_summary(candidate)

        if candidate.job_name == "implement_issue":
            assert candidate.issue is not None
            return self._run_implement_issue(candidate.issue, status_hook=status_hook)
        if candidate.job_name == "triage_issue":
            assert candidate.issue is not None
            return self._run_triage_issue(candidate.issue, status_hook=status_hook)
        if candidate.job_name == "review_pr":
            assert candidate.pull_request is not None
            return self._run_review_pr(candidate.pull_request, status_hook=status_hook)
        if candidate.job_name == "hygiene_scan":
            return self._run_hygiene_scan(status_hook=status_hook)

        raise RuntimeError(f"Unsupported squad job: {candidate.job_name}")

    def apply_automatic_cleanup(self, issue_number: int | None = None) -> tuple[CleanupCandidate, ...]:
        candidates = self._cleanup.scan_auto_cleanup_candidates(issue_number=issue_number)
        if not candidates:
            return ()

        cleaned = self._cleanup.apply(candidates)
        for candidate in cleaned:
            log_event(
                self._logger,
                "Auto-cleaned completed Symphony worktree",
                event="auto_cleanup_applied",
                issue_number=candidate.issue_number,
                branch_name=candidate.branch_name,
                workspace_path=candidate.workspace_path,
                merged_pull_request_url=candidate.merged_pull_request_url,
                job_name="auto_cleanup",
            )
        return cleaned

    def _run_implement_issue(self, issue: GitHubIssue, *, status_hook: StatusHook | None) -> RunSummary:
        started_at = datetime.now(timezone.utc)
        worktree_manager = self._build_worktree_manager()
        worktree_target = worktree_manager.describe_target(issue.number, issue.title)
        empty_change_set = ChangeSet(files=(), plan_paths=(), requires_xml_gate=False, requires_dll_gate=False)
        change_set: ChangeSet | None = None
        validation: ValidationResult | None = None
        commit_sha: str | None = None
        pull_request = None
        issue_comment_url = None
        self._github.update_status(issue, self._config.github.planning_state)
        self._emit_status(
            status_hook,
            state="planning",
            current_job_name="implement_issue",
            current_role="lead",
            current_issue_number=issue.number,
            current_branch_name=worktree_target.branch_name,
            current_workspace_path=str(worktree_target.path),
        )
        log_event(
            self._logger,
            "Moved issue to Planning",
            event="status_transition",
            issue_number=issue.number,
            new_status=self._config.github.planning_state,
            job_name="implement_issue",
        )

        try:
            worktree = worktree_manager.ensure_worktree(issue.number, issue.title)
            if self._config.squad.kickoff_comments_enabled:
                issue_comment_url = self._github.create_issue_comment(
                    issue.number,
                    build_lead_kickoff_comment(issue, worktree.branch_name, str(worktree.path)),
                )

            self._github.update_status(issue, self._config.github.in_progress_state)
            self._emit_status(
                status_hook,
                state="in_progress",
                current_job_name="implement_issue",
                current_role="implementer",
                current_issue_number=issue.number,
                current_branch_name=worktree.branch_name,
                current_workspace_path=str(worktree.path),
                last_issue_comment_url=issue_comment_url,
            )
            log_event(
                self._logger,
                "Moved issue to In Progress",
                event="status_transition",
                issue_number=issue.number,
                new_status=self._config.github.in_progress_state,
                branch_name=worktree.branch_name,
                workspace_path=str(worktree.path),
                created_worktree=worktree.created_now,
                job_name="implement_issue",
            )

            prompt = self._prompt_builder.build_implementer_prompt(
                issue=issue,
                branch_name=worktree.branch_name,
                workspace_path=str(worktree.path),
                repo_root=str(self._repo_root),
            )
            result = AgentRunner(self._config.codex, worktree.path).run_turn(prompt)
            git_manager = GitManager(worktree.path)
            change_set = git_manager.collect_changes()
            if not change_set.files:
                raise RuntimeError("Agent turn completed without producing any reviewable file changes.")

            validation = ValidationRunner(worktree.path).run(change_set)
            self._emit_status(
                status_hook,
                current_job_name="implement_issue",
                current_role="implementer",
                current_issue_number=issue.number,
                current_branch_name=worktree.branch_name,
                current_workspace_path=str(worktree.path),
                last_validation_command=(" ".join(validation.command) if validation.command else None),
                last_validation_passed=validation.passed,
            )
            log_event(
                self._logger,
                "Validation completed",
                event="validation_completed",
                issue_number=issue.number,
                validation_required=validation.required,
                validation_passed=validation.passed,
                validation_command=(" ".join(validation.command) if validation.command else None),
                job_name="implement_issue",
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
            if self._config.squad.review_comments_enabled:
                issue_comment_url = self._github.create_issue_comment(
                    issue.number,
                    build_reviewer_issue_comment(
                        issue,
                        worktree.branch_name,
                        str(worktree.path),
                        pull_request,
                        change_set,
                        validation,
                    ),
                )
            self._emit_status(
                status_hook,
                current_job_name="implement_issue",
                current_role="reviewer",
                current_issue_number=issue.number,
                current_branch_name=worktree.branch_name,
                current_workspace_path=str(worktree.path),
                last_issue_comment_url=issue_comment_url,
                current_pull_request_number=pull_request.number,
            )
            self._github.update_status(issue, self._config.github.human_review_state)
            log_event(
                self._logger,
                "Implement issue completed",
                event="job_completed",
                issue_number=issue.number,
                new_status=self._config.github.human_review_state,
                thread_id=result.thread_id,
                turn_id=result.turn_id,
                commit_sha=commit_sha,
                pull_request_url=pull_request.url,
                issue_comment_url=issue_comment_url,
                job_name="implement_issue",
            )
            summary = RunSummary(
                job_name="implement_issue",
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
                current_role="reviewer",
                role_sequence=("lead", "implementer", "reviewer"),
                note="Validated draft PR handoff ready for human review.",
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
                        job_name="implement_issue",
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
                    job_name="implement_issue",
                )
            summary = RunSummary(
                job_name="implement_issue",
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
                current_role="implementer",
                role_sequence=("lead", "implementer", "reviewer"),
                note=str(exc),
            )
            self._write_summary(summary)
            raise

    def _run_triage_issue(self, issue: GitHubIssue, *, status_hook: StatusHook | None) -> RunSummary:
        started_at = datetime.now(timezone.utc)
        self._github.update_status(issue, self._config.github.planning_state)
        self._emit_status(
            status_hook,
            state="planning",
            current_job_name="triage_issue",
            current_role="triage",
            current_issue_number=issue.number,
        )
        result = AgentRunner(self._read_only_codex_config("triage"), self._repo_root).run_turn(
            self._prompt_builder.build_triage_prompt(issue)
        )
        response = extract_json_object(result.final_message or "")
        action = str(response.get("action", "inbox")).strip().lower()
        summary_text = str(response.get("summary", "")).strip() or "Issue needs more clarification."
        missing = tuple(str(item).strip() for item in response.get("missing", []) if str(item).strip())
        if action == "ready":
            new_status = self._config.github.ready_state
        elif action == "blocked":
            new_status = self._config.github.blocked_state
        else:
            new_status = "Inbox"
        issue_comment_url = None
        if self._config.squad.triage_comments_enabled:
            issue_comment_url = self._github.create_issue_comment(
                issue.number,
                build_triage_comment(issue, action=new_status, summary=summary_text, missing=missing),
            )
        self._github.update_status(issue, new_status)
        summary = RunSummary(
            job_name="triage_issue",
            issue_number=issue.number,
            issue_title=issue.title,
            branch_name="",
            workspace_path=str(self._repo_root),
            started_at=started_at,
            finished_at=datetime.now(timezone.utc),
            outcome="completed",
            project_status=new_status,
            thread_id=result.thread_id,
            turn_id=result.turn_id,
            turn_status=result.status,
            issue_comment_url=issue_comment_url,
            current_role="triage",
            role_sequence=("triage",),
            note=summary_text,
        )
        self._write_summary(summary)
        return summary

    def _run_review_pr(self, pull_request: PullRequestInfo, *, status_hook: StatusHook | None) -> RunSummary:
        started_at = datetime.now(timezone.utc)
        issue_number = issue_number_from_branch(pull_request.head_ref_name) or 0
        latest_summary = self._history.latest_for_issue(issue_number) if issue_number else None
        files = self._github.list_pull_request_files(pull_request.number)
        self._emit_status(
            status_hook,
            state="reviewing",
            current_job_name="review_pr",
            current_role="reviewer",
            current_pull_request_number=pull_request.number,
            current_branch_name=pull_request.head_ref_name,
        )
        result = AgentRunner(self._read_only_codex_config("reviewer"), self._repo_root).run_turn(
            self._prompt_builder.build_review_pr_prompt(
                pull_request=pull_request,
                files=files,
                latest_summary=latest_summary,
            )
        )
        final_message = (result.final_message or "").strip()
        if not final_message:
            raise AgentOutputError("Reviewer did not produce a review summary.")
        issue_comment_url = self._github.create_issue_comment(
            pull_request.number,
            build_pr_review_comment(final_message),
        )
        summary = RunSummary(
            job_name="review_pr",
            issue_number=issue_number,
            issue_title=pull_request.title,
            branch_name=pull_request.head_ref_name,
            workspace_path=str(self._repo_root),
            started_at=started_at,
            finished_at=datetime.now(timezone.utc),
            outcome="completed",
            project_status=(latest_summary.project_status if latest_summary is not None else ""),
            thread_id=result.thread_id,
            turn_id=result.turn_id,
            turn_status=result.status,
            pull_request_number=pull_request.number,
            pull_request_url=pull_request.url,
            issue_comment_url=issue_comment_url,
            current_role="reviewer",
            role_sequence=("reviewer",),
            note="PR review summary posted.",
        )
        self._write_summary(summary)
        return summary

    def _run_hygiene_scan(self, *, status_hook: StatusHook | None) -> RunSummary:
        started_at = datetime.now(timezone.utc)
        self._emit_status(
            status_hook,
            state="hygiene",
            current_job_name="hygiene_scan",
            current_role="hygiene",
        )
        findings = self._collect_hygiene_findings()
        findings_markdown = self._render_hygiene_findings(findings)
        issue_number = 0
        issue_url = None
        if findings:
            result = AgentRunner(self._read_only_codex_config("hygiene"), self._repo_root).run_turn(
                self._prompt_builder.build_hygiene_prompt(findings_markdown)
            )
            body = build_hygiene_issue_body((result.final_message or "").strip() or findings_markdown)
            issue = self._github.find_open_issue_by_title(self._config.squad.hygiene_issue_title)
            if issue is None:
                created = self._github.create_issue(
                    self._config.squad.hygiene_issue_title,
                    body,
                    labels=("needs-human",),
                )
                if self._github.get_project_issue(created.number) is None:
                    self._github.add_issue_to_project(created, initial_state="Inbox")
                issue_number = created.number
                issue_url = created.url
            else:
                updated = self._github.update_issue(issue.number, body=body)
                if self._github.get_project_issue(updated.number) is None:
                    self._github.add_issue_to_project(updated, initial_state="Inbox")
                issue_number = updated.number
                issue_url = updated.url
        summary = RunSummary(
            job_name="hygiene_scan",
            issue_number=issue_number,
            issue_title=self._config.squad.hygiene_issue_title,
            branch_name="",
            workspace_path=str(self._repo_root),
            started_at=started_at,
            finished_at=datetime.now(timezone.utc),
            outcome="completed",
            project_status="",
            pull_request_url=issue_url,
            current_role="hygiene",
            role_sequence=("hygiene",),
            note=f"{len(findings)} hygiene finding(s)." if findings else "No hygiene findings.",
        )
        self._write_summary(summary)
        return summary

    def _build_dry_run_summary(self, candidate: JobCandidate) -> RunSummary:
        started_at = datetime.now(timezone.utc)
        branch_name = ""
        workspace_path = str(self._repo_root)
        issue_number = 0
        issue_title = candidate.job_name
        project_status = ""
        pull_request_number = None
        pull_request_url = None
        if candidate.issue is not None:
            issue_number = candidate.issue.number
            issue_title = candidate.issue.title
            project_status = candidate.issue.project_status
            if candidate.job_name == "implement_issue":
                worktree_target = self._build_worktree_manager().describe_target(candidate.issue.number, candidate.issue.title)
                branch_name = worktree_target.branch_name
                workspace_path = str(worktree_target.path)
        if candidate.pull_request is not None:
            issue_number = issue_number_from_branch(candidate.pull_request.head_ref_name) or 0
            issue_title = candidate.pull_request.title
            branch_name = candidate.pull_request.head_ref_name
            pull_request_number = candidate.pull_request.number
            pull_request_url = candidate.pull_request.url
        summary = RunSummary(
            job_name=candidate.job_name,
            issue_number=issue_number,
            issue_title=issue_title,
            branch_name=branch_name,
            workspace_path=workspace_path,
            started_at=started_at,
            finished_at=datetime.now(timezone.utc),
            outcome="dry_run",
            project_status=project_status,
            pull_request_number=pull_request_number,
            pull_request_url=pull_request_url,
            note="Selected candidate without mutating git or GitHub.",
        )
        self._write_summary(summary)
        return summary

    def _collect_hygiene_findings(self) -> list[tuple[str, str]]:
        findings: list[tuple[str, str]] = []

        cleanup_candidates = self._cleanup.scan()
        for candidate in cleanup_candidates:
            if candidate.eligible:
                findings.append(
                    (
                        "cleanup_candidate",
                        f"#{candidate.issue_number} has a removable local worktree at `{candidate.workspace_path}`.",
                    )
                )
            elif "dirty_worktree" in candidate.reasons:
                findings.append(
                    (
                        "dirty_worktree",
                        f"#{candidate.issue_number} still has a dirty worktree at `{candidate.workspace_path}`.",
                    )
                )

        for path in sorted((self._repo_root / "docs").glob("*.md")):
            name = path.name.upper()
            if any(marker in name for marker in ("PLAN", "DRAFT", "BRAINSTORM", "ROOT_CAUSE", "DEBUG")):
                findings.append(("stale_doc", f"`docs/{path.name}` looks historical and may belong under `docs/archive/`."))

        for pull_request in self._github.list_open_symphony_pull_requests(
            self._config.workspace.branch_prefix, self._config.workspace.base_branch
        ):
            issue_number = issue_number_from_branch(pull_request.head_ref_name)
            latest_summary = self._history.latest_for_issue(issue_number) if issue_number else None
            if latest_summary is None:
                findings.append(
                    (
                        "validation_attention",
                        f"PR #{pull_request.number} has no local Symphony run summary for validation history.",
                    )
                )
            elif latest_summary.validation_required and not latest_summary.validation_passed:
                findings.append(
                    (
                        "validation_attention",
                        f"PR #{pull_request.number} has a latest Symphony validation result that did not pass.",
                    )
                )
        return findings

    def _render_hygiene_findings(self, findings: list[tuple[str, str]]) -> str:
        if not findings:
            return "- No hygiene findings."
        lines = []
        for category, message in findings:
            lines.append(f"- [{category}] {message}")
        return "\n".join(lines)

    def _build_worktree_manager(self) -> WorktreeManager:
        return WorktreeManager(
            repo_root=self._repo_root,
            workspace_root=self._config.workspace.root,
            base_branch=self._config.workspace.base_branch,
            branch_prefix=self._config.workspace.branch_prefix,
        )

    def _read_only_codex_config(self, role_name: str) -> CodexConfig:
        return replace(
            self._config.codex,
            thread_sandbox="read-only",
            turn_sandbox_policy="read-only",
            developer_instructions=(
                self._config.codex.developer_instructions
                + f" You are executing the Symphony squad role '{role_name}'. Produce only the requested analysis."
            ),
        )

    def _emit_status(self, status_hook: StatusHook | None, **fields) -> None:
        if status_hook is None:
            return
        status_hook(**fields)

    def _write_summary(self, summary: RunSummary) -> None:
        runs_dir = self._config.runtime.state_root / "runs"
        runs_dir.mkdir(parents=True, exist_ok=True)
        timestamp = summary.finished_at.strftime("%Y%m%dT%H%M%SZ")
        filename = f"{summary.issue_number or summary.job_name}-{timestamp}.json"
        (runs_dir / filename).write_text(json.dumps(summary.to_dict(), indent=2), encoding="utf-8")
