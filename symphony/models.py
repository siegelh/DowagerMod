from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class WorkflowDefinition:
    path: Path
    config: dict[str, Any]
    prompt_template: str


@dataclass(frozen=True)
class ProjectStatusField:
    project_id: str
    field_id: str
    options: dict[str, str]


@dataclass(frozen=True)
class GitHubIssue:
    node_id: str
    project_item_id: str
    repository_full_name: str
    number: int
    title: str
    body: str
    state: str
    url: str
    created_at: datetime
    updated_at: datetime
    labels: tuple[str, ...]
    assignees: tuple[str, ...]
    project_status: str

    def template_context(self) -> dict[str, Any]:
        return {
            "id": self.node_id,
            "number": self.number,
            "title": self.title,
            "body": self.body,
            "state": self.state,
            "url": self.url,
            "labels": list(self.labels),
            "assignees": list(self.assignees),
            "project_status": self.project_status,
            "repository_full_name": self.repository_full_name,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass(frozen=True)
class WorktreeInfo:
    branch_name: str
    path: Path
    created_now: bool


@dataclass(frozen=True)
class AgentRunResult:
    thread_id: str
    turn_id: str
    status: str
    notifications: list[dict[str, Any]] = field(default_factory=list)
    final_turn: dict[str, Any] | None = None


@dataclass(frozen=True)
class ChangeSet:
    files: tuple[str, ...]
    plan_paths: tuple[str, ...]
    requires_xml_gate: bool
    requires_dll_gate: bool


@dataclass(frozen=True)
class ValidationResult:
    required: bool
    passed: bool
    command: tuple[str, ...]
    output: str


@dataclass(frozen=True)
class PullRequestInfo:
    number: int
    url: str
    title: str
    is_draft: bool
    existing: bool


@dataclass(frozen=True)
class RunSummary:
    issue_number: int
    issue_title: str
    branch_name: str
    workspace_path: str
    started_at: datetime
    finished_at: datetime
    outcome: str
    project_status: str
    thread_id: str | None = None
    turn_id: str | None = None
    turn_status: str | None = None
    commit_sha: str | None = None
    pull_request_number: int | None = None
    pull_request_url: str | None = None
    issue_comment_url: str | None = None
    changed_files: tuple[str, ...] = field(default_factory=tuple)
    plan_paths: tuple[str, ...] = field(default_factory=tuple)
    validation_required: bool = False
    validation_passed: bool | None = None
    validation_command: str | None = None
    note: str | None = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["started_at"] = self.started_at.isoformat()
        data["finished_at"] = self.finished_at.isoformat()
        return data
