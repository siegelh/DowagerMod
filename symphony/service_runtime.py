from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import msvcrt


class ServiceRuntimeError(RuntimeError):
    """Raised when Symphony cannot manage its local worker runtime state."""


@dataclass(frozen=True)
class ServiceStatus:
    is_running: bool
    payload: dict[str, Any]


class ServiceRuntime:
    def __init__(self, state_root: Path):
        self._state_root = state_root
        self._state_root.mkdir(parents=True, exist_ok=True)
        self._status_path = self._state_root / "service-status.json"
        self._lock_path = self._state_root / "service.lock"
        self._stop_path = self._state_root / "service.stop"

    @property
    def status_path(self) -> Path:
        return self._status_path

    def acquire_singleton(self, mode: str) -> "ActiveServiceLease":
        return ActiveServiceLease(self, mode)

    def read_status(self) -> ServiceStatus:
        if not self._status_path.is_file():
            return ServiceStatus(
                is_running=False,
                payload={
                    "is_running": False,
                    "state": "stopped",
                    "status_path": str(self._status_path),
                },
            )

        payload = json.loads(self._status_path.read_text(encoding="utf-8"))
        pid = payload.get("pid")
        state = str(payload.get("state", "unknown"))
        is_running = bool(pid) and state not in {"stopped", "crashed"} and _pid_exists(int(pid))
        payload["is_running"] = is_running
        payload["status_path"] = str(self._status_path)
        if not is_running and state != "stopped":
            payload["state"] = "stopped"
        return ServiceStatus(is_running=is_running, payload=payload)

    def request_stop(self) -> None:
        self._stop_path.write_text("stop\n", encoding="utf-8")

    def clear_stop_request(self) -> None:
        if self._stop_path.exists():
            self._stop_path.unlink()

    def is_stop_requested(self) -> bool:
        return self._stop_path.exists()

    def _write_status(self, payload: dict[str, Any]) -> None:
        self._status_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


class ActiveServiceLease:
    def __init__(self, runtime: ServiceRuntime, mode: str):
        self._runtime = runtime
        self._mode = mode
        self._lock_handle = None
        self._payload: dict[str, Any] = {}
        self._started_at = _utc_now()

    def __enter__(self) -> "ActiveServiceLease":
        self._runtime.clear_stop_request()
        self._lock_handle = open(self._runtime._lock_path, "a+b")
        self._lock_handle.seek(0)
        if self._lock_handle.tell() == 0:
            self._lock_handle.write(b" ")
            self._lock_handle.flush()
        self._lock_handle.seek(0)
        try:
            msvcrt.locking(self._lock_handle.fileno(), msvcrt.LK_NBLCK, 1)
        except OSError as exc:
            self._lock_handle.close()
            status = self._runtime.read_status()
            pid = status.payload.get("pid")
            raise ServiceRuntimeError(f"Symphony is already running{f' (pid {pid})' if pid else ''}.") from exc

        self.write_status(
            state="starting",
            mode=self._mode,
            started_at=self._started_at,
            pid=os.getpid(),
        )
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        note = None
        state = "stopped"
        if exc is not None:
            state = "crashed"
            note = str(exc)
        self.mark_stopped(state=state, note=note)
        self._runtime.clear_stop_request()
        if self._lock_handle is not None:
            try:
                self._lock_handle.seek(0)
                msvcrt.locking(self._lock_handle.fileno(), msvcrt.LK_UNLCK, 1)
            finally:
                self._lock_handle.close()
                self._lock_handle = None

    def write_status(self, *, state: str, **fields: Any) -> None:
        payload = dict(self._payload)
        payload.update(fields)
        payload.update(
            {
                "mode": self._mode,
                "state": state,
                "pid": os.getpid(),
                "is_running": True,
                "started_at": payload.get("started_at", self._started_at),
                "heartbeat_at": _utc_now(),
            }
        )
        self._payload = payload
        self._runtime._write_status(payload)

    def heartbeat(self, *, state: str | None = None, **fields: Any) -> None:
        self.write_status(state=state or str(self._payload.get("state", "running")), **fields)

    def mark_stopped(self, *, state: str = "stopped", note: str | None = None) -> None:
        payload = dict(self._payload)
        for key in (
            "current_job_name",
            "current_role",
            "current_issue_number",
            "current_pull_request_number",
            "current_branch_name",
            "current_workspace_path",
        ):
            payload.pop(key, None)
        payload.update(
            {
                "mode": self._mode,
                "state": state,
                "is_running": False,
                "last_pid": payload.get("pid", os.getpid()),
                "pid": None,
                "heartbeat_at": _utc_now(),
                "stopped_at": _utc_now(),
            }
        )
        if note:
            payload["note"] = note
        self._payload = payload
        self._runtime._write_status(payload)


def wait_for_stop(runtime: ServiceRuntime, timeout_seconds: int, poll_seconds: float = 1.0) -> ServiceStatus:
    deadline = time.time() + timeout_seconds
    status = runtime.read_status()
    while status.is_running and time.time() < deadline:
        time.sleep(poll_seconds)
        status = runtime.read_status()
    return status


def _pid_exists(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
