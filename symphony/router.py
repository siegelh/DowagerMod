from __future__ import annotations

import re

from .config import SymphonyConfig
from .github_client import GitHubClient
from .history import RunHistory
from .models import JobCandidate
from .squad_registry import SquadRegistry

REVIEW_COMMENT_MARKER = "<!-- symphony:review-pr -->"


class SquadRouter:
    def __init__(
        self,
        github: GitHubClient,
        config: SymphonyConfig,
        registry: SquadRegistry,
        history: RunHistory,
    ):
        self._github = github
        self._config = config
        self._registry = registry
        self._history = history

    def pick_next(
        self,
        *,
        explicit_job: str | None = None,
        issue_number: int | None = None,
        pull_request_number: int | None = None,
    ) -> JobCandidate | None:
        if explicit_job:
            return self._pick_for_job(explicit_job, issue_number=issue_number, pull_request_number=pull_request_number)

        jobs = sorted(
            (job for job in self._registry.jobs.values() if job.enabled),
            key=lambda job: job.priority,
            reverse=True,
        )
        for job in jobs:
            candidate = self._pick_for_job(job.name, issue_number=issue_number, pull_request_number=pull_request_number)
            if candidate is not None:
                return candidate
        return None

    def _pick_for_job(
        self,
        job_name: str,
        *,
        issue_number: int | None = None,
        pull_request_number: int | None = None,
    ) -> JobCandidate | None:
        if job_name == "implement_issue":
            issue = self._github.pick_next_ready_issue(issue_number=issue_number)
            return JobCandidate(job_name=job_name, issue=issue) if issue is not None else None

        if job_name == "triage_issue":
            issue = self._github.pick_next_inbox_issue(issue_number=issue_number)
            return JobCandidate(job_name=job_name, issue=issue) if issue is not None else None

        if job_name == "review_pr":
            if pull_request_number is not None:
                pull_request = self._github.get_pull_request(pull_request_number)
                if pull_request.state == "OPEN" and pull_request.head_ref_name.startswith(
                    f"{self._config.workspace.branch_prefix}/"
                ):
                    return JobCandidate(job_name=job_name, pull_request=pull_request)
                return None

            for pull_request in self._github.list_open_symphony_pull_requests(
                self._config.workspace.branch_prefix, self._config.workspace.base_branch
            ):
                comments = self._github.list_issue_comments(pull_request.number)
                if any(REVIEW_COMMENT_MARKER in comment.body for comment in comments):
                    continue
                return JobCandidate(job_name=job_name, pull_request=pull_request)
            return None

        if job_name == "hygiene_scan":
            job = self._registry.get_job(job_name)
            if job.schedule_key is None:
                return None
            schedule = self._registry.schedules.get(job.schedule_key)
            if schedule is None:
                return None
            if self._history.is_job_due(job_name, schedule.interval_seconds):
                return JobCandidate(job_name=job_name, scheduled=True)
            return None

        return None


def issue_number_from_branch(branch_name: str) -> int | None:
    match = re.match(r"^[^/]+/(\d+)-", branch_name)
    if match is None:
        return None
    return int(match.group(1))
