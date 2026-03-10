from __future__ import annotations

import os
import shlex
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .models import WorkflowDefinition


class ConfigError(RuntimeError):
    """Raised when the Symphony runtime config is incomplete or invalid."""


@dataclass(frozen=True)
class GitHubConfig:
    owner: str
    owner_type: str
    repo: str
    project_number: int
    status_field: str
    ready_state: str
    planning_state: str
    in_progress_state: str
    blocked_state: str
    human_review_state: str
    done_state: str
    blocker_labels: tuple[str, ...]
    token: str


@dataclass(frozen=True)
class WorkspaceConfig:
    root: Path
    base_branch: str
    branch_prefix: str


@dataclass(frozen=True)
class RuntimeConfig:
    state_root: Path


@dataclass(frozen=True)
class CodexConfig:
    command: tuple[str, ...]
    approval_policy: str
    thread_sandbox: str
    turn_sandbox_policy: str
    model: str
    model_provider: str
    effort: str
    read_timeout_ms: int
    turn_timeout_ms: int
    developer_instructions: str
    base_instructions: str


@dataclass(frozen=True)
class SymphonyConfig:
    workflow_path: Path
    github: GitHubConfig
    workspace: WorkspaceConfig
    runtime: RuntimeConfig
    codex: CodexConfig


def load_dotenv(path: Path) -> None:
    if not path.is_file():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def build_config(workflow: WorkflowDefinition, repo_root: Path) -> SymphonyConfig:
    load_dotenv(repo_root / ".env")

    tracker_cfg = _require_object(workflow.config, "tracker")
    if tracker_cfg.get("kind") != "github":
        raise ConfigError("tracker.kind must be 'github'")

    owner = _require_string(tracker_cfg, "owner")
    repo = _require_string(tracker_cfg, "repo")
    project_number = int(tracker_cfg.get("project_number", 0))
    if project_number <= 0:
        raise ConfigError("tracker.project_number must be a positive integer")

    owner_type = str(tracker_cfg.get("owner_type", "user")).strip().lower()
    if owner_type not in {"user", "organization"}:
        raise ConfigError("tracker.owner_type must be 'user' or 'organization'")

    token_env = str(tracker_cfg.get("api_token_env", "GITHUB_TOKEN")).strip()
    token = os.environ.get(token_env, "").strip()
    if not token:
        raise ConfigError(f"missing GitHub token in environment variable {token_env}")

    blocker_labels = tracker_cfg.get("blocker_labels", [])
    if isinstance(blocker_labels, str):
        blocker_values = [part.strip().lower() for part in blocker_labels.split(",") if part.strip()]
    else:
        blocker_values = [str(part).strip().lower() for part in blocker_labels]

    workspace_cfg = _require_object(workflow.config, "workspace")
    runtime_cfg = _require_object(workflow.config, "runtime")
    codex_cfg = _require_object(workflow.config, "codex")

    command_value = codex_cfg.get("command", ["codex", "app-server"])
    command = _coerce_command(command_value)

    return SymphonyConfig(
        workflow_path=workflow.path,
        github=GitHubConfig(
            owner=owner,
            owner_type=owner_type,
            repo=repo,
            project_number=project_number,
            status_field=str(tracker_cfg.get("status_field", "Status")),
            ready_state=str(tracker_cfg.get("ready_state", "Ready")),
            planning_state=str(tracker_cfg.get("planning_state", "Planning")),
            in_progress_state=str(tracker_cfg.get("in_progress_state", "In Progress")),
            blocked_state=str(tracker_cfg.get("blocked_state", "Blocked")),
            human_review_state=str(tracker_cfg.get("human_review_state", "Human Review")),
            done_state=str(tracker_cfg.get("done_state", "Done")),
            blocker_labels=tuple(blocker_values),
            token=token,
        ),
        workspace=WorkspaceConfig(
            root=_resolve_path(str(workspace_cfg.get("root", r"$LOCALAPPDATA\Symphony\workspaces\DowagerMod"))),
            base_branch=str(workspace_cfg.get("base_branch", "agent-baseline")),
            branch_prefix=str(workspace_cfg.get("branch_prefix", "symphony")),
        ),
        runtime=RuntimeConfig(
            state_root=_resolve_path(str(runtime_cfg.get("state_root", r"$LOCALAPPDATA\Symphony\DowagerMod"))),
        ),
        codex=CodexConfig(
            command=command,
            approval_policy=str(codex_cfg.get("approval_policy", "never")),
            thread_sandbox=str(codex_cfg.get("thread_sandbox", "danger-full-access")),
            turn_sandbox_policy=str(codex_cfg.get("turn_sandbox_policy", "danger-full-access")),
            model=str(codex_cfg.get("model", "gpt-5-codex")),
            model_provider=str(codex_cfg.get("model_provider", "openai")),
            effort=str(codex_cfg.get("effort", "low")),
            read_timeout_ms=int(codex_cfg.get("read_timeout_ms", 5000)),
            turn_timeout_ms=int(codex_cfg.get("turn_timeout_ms", 3600000)),
            developer_instructions=str(
                codex_cfg.get(
                    "developer_instructions",
                    (
                        "You are running inside Symphony for siegelh/DowagerMod. "
                        "Work only inside the provided git worktree, follow the repository docs, "
                        "and stop when the task reaches human review."
                    ),
                )
            ),
            base_instructions=str(codex_cfg.get("base_instructions", "")),
        ),
    )


def _require_object(config: dict[str, Any], key: str) -> dict[str, Any]:
    value = config.get(key, {})
    if not isinstance(value, dict):
        raise ConfigError(f"{key} must be an object")
    return value


def _require_string(config: dict[str, Any], key: str) -> str:
    value = str(config.get(key, "")).strip()
    if not value:
        raise ConfigError(f"{key} must be set")
    return value


def _coerce_command(value: Any) -> tuple[str, ...]:
    if isinstance(value, list):
        parts = [str(part).strip() for part in value if str(part).strip()]
        if not parts:
            raise ConfigError("codex.command must not be empty")
        return tuple(parts)
    if isinstance(value, str):
        parts = shlex.split(value, posix=False)
        if not parts:
            raise ConfigError("codex.command must not be empty")
        return tuple(parts)
    raise ConfigError("codex.command must be a string or list")


def _resolve_path(raw_value: str) -> Path:
    expanded = os.path.expanduser(os.path.expandvars(raw_value))
    return Path(expanded).resolve()
