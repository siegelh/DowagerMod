from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from .config import SquadConfig
from .models import JobDefinition, ScheduleEntry, SquadRole


class SquadRegistryError(RuntimeError):
    """Raised when the checked-in squad definitions are invalid."""


@dataclass(frozen=True)
class SquadRegistry:
    team_path: Path
    team_charter: str
    roles: dict[str, SquadRole]
    jobs: dict[str, JobDefinition]
    schedules: dict[str, ScheduleEntry]

    def get_role(self, name: str) -> SquadRole:
        try:
            return self.roles[name]
        except KeyError as exc:
            raise SquadRegistryError(f"Unknown squad role: {name}") from exc

    def get_job(self, name: str) -> JobDefinition:
        try:
            return self.jobs[name]
        except KeyError as exc:
            raise SquadRegistryError(f"Unknown squad job: {name}") from exc


def load_squad_registry(config: SquadConfig) -> SquadRegistry:
    team_charter = _read_text(config.team_path)
    jobs_yaml = _read_yaml(config.jobs_path)
    schedule_yaml = _read_yaml(config.schedule_path)

    roles = _load_roles(config.team_path.parent / "roles")
    jobs: dict[str, JobDefinition] = {}
    for job_name, raw_job in _require_mapping(jobs_yaml, "jobs").items():
        if not isinstance(raw_job, dict):
            raise SquadRegistryError(f"Job {job_name!r} must be a mapping")
        roles_for_job = tuple(str(name).strip() for name in raw_job.get("roles", []) if str(name).strip())
        if not roles_for_job:
            raise SquadRegistryError(f"Job {job_name!r} must declare at least one role")
        for role_name in roles_for_job:
            if role_name not in roles:
                raise SquadRegistryError(f"Job {job_name!r} references unknown role {role_name!r}")
        jobs[job_name] = JobDefinition(
            name=job_name,
            kind=str(raw_job.get("kind", "")).strip(),
            roles=roles_for_job,
            concurrency=str(raw_job.get("concurrency", "light")).strip(),
            priority=int(raw_job.get("priority", 0)),
            source_statuses=tuple(str(value).strip() for value in raw_job.get("source_statuses", []) if str(value).strip()),
            enabled=bool(raw_job.get("enabled", True)),
            schedule_key=(str(raw_job.get("schedule_key")).strip() if raw_job.get("schedule_key") else None),
        )

    schedules: dict[str, ScheduleEntry] = {}
    for schedule_name, raw_schedule in _require_mapping(schedule_yaml, "schedules").items():
        if not isinstance(raw_schedule, dict):
            raise SquadRegistryError(f"Schedule {schedule_name!r} must be a mapping")
        schedules[schedule_name] = ScheduleEntry(
            name=schedule_name,
            interval_seconds=max(60, int(raw_schedule.get("interval_seconds", 3600))),
        )

    return SquadRegistry(
        team_path=config.team_path,
        team_charter=team_charter,
        roles=roles,
        jobs=jobs,
        schedules=schedules,
    )


def _load_roles(directory: Path) -> dict[str, SquadRole]:
    if not directory.is_dir():
        raise SquadRegistryError(f"Missing squad roles directory: {directory}")
    roles: dict[str, SquadRole] = {}
    for path in sorted(directory.glob("*.md")):
        role_name = path.stem.strip().lower()
        roles[role_name] = SquadRole(name=role_name, path=path, charter=_read_text(path))
    if not roles:
        raise SquadRegistryError(f"No squad roles found in {directory}")
    return roles


def _read_text(path: Path) -> str:
    if not path.is_file():
        raise SquadRegistryError(f"Missing squad file: {path}")
    return path.read_text(encoding="utf-8").strip()


def _read_yaml(path: Path) -> dict:
    if not path.is_file():
        raise SquadRegistryError(f"Missing squad YAML file: {path}")
    parsed = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(parsed, dict):
        raise SquadRegistryError(f"Squad YAML must be a mapping: {path}")
    return parsed


def _require_mapping(data: dict, key: str) -> dict:
    value = data.get(key, {})
    if not isinstance(value, dict):
        raise SquadRegistryError(f"{key} must be a mapping")
    return value
