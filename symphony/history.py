from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .models import RunSummary


class RunHistory:
    def __init__(self, state_root: Path):
        self._runs_dir = state_root / "runs"

    def latest_for_issue(self, issue_number: int) -> RunSummary | None:
        summaries = [summary for summary in self._load_all() if summary.issue_number == issue_number]
        summaries.sort(key=lambda summary: summary.finished_at, reverse=True)
        return summaries[0] if summaries else None

    def latest_for_job(self, job_name: str) -> RunSummary | None:
        summaries = [summary for summary in self._load_all() if summary.job_name == job_name]
        summaries.sort(key=lambda summary: summary.finished_at, reverse=True)
        return summaries[0] if summaries else None

    def is_job_due(self, job_name: str, interval_seconds: int, now: datetime | None = None) -> bool:
        latest = self.latest_for_job(job_name)
        if latest is None:
            return True
        now = now or datetime.now(timezone.utc)
        elapsed = (now - latest.finished_at).total_seconds()
        return elapsed >= interval_seconds

    def _load_all(self) -> list[RunSummary]:
        if not self._runs_dir.is_dir():
            return []
        summaries: list[RunSummary] = []
        for path in self._runs_dir.glob("*.json"):
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
                summaries.append(_summary_from_payload(payload))
            except Exception:
                continue
        return summaries


def _summary_from_payload(payload: dict) -> RunSummary:
    return RunSummary(
        job_name=str(payload.get("job_name", "implement_issue")),
        issue_number=int(payload.get("issue_number", 0)),
        issue_title=str(payload.get("issue_title", "")),
        branch_name=str(payload.get("branch_name", "")),
        workspace_path=str(payload.get("workspace_path", "")),
        started_at=_parse_datetime(payload["started_at"]),
        finished_at=_parse_datetime(payload["finished_at"]),
        outcome=str(payload.get("outcome", "")),
        project_status=str(payload.get("project_status", "")),
        thread_id=payload.get("thread_id"),
        turn_id=payload.get("turn_id"),
        turn_status=payload.get("turn_status"),
        commit_sha=payload.get("commit_sha"),
        pull_request_number=payload.get("pull_request_number"),
        pull_request_url=payload.get("pull_request_url"),
        issue_comment_url=payload.get("issue_comment_url"),
        changed_files=tuple(payload.get("changed_files", [])),
        plan_paths=tuple(payload.get("plan_paths", [])),
        validation_required=bool(payload.get("validation_required", False)),
        validation_passed=payload.get("validation_passed"),
        validation_command=payload.get("validation_command"),
        current_role=payload.get("current_role"),
        role_sequence=tuple(payload.get("role_sequence", [])),
        note=payload.get("note"),
    )


def _parse_datetime(raw_value: str) -> datetime:
    return datetime.fromisoformat(raw_value.replace("Z", "+00:00"))
