from __future__ import annotations

import time
from datetime import datetime, timezone

from .logging_utils import log_event
from .orchestrator import SymphonyService
from .service_runtime import ServiceRuntime


class SymphonyServer:
    def __init__(
        self,
        service: SymphonyService,
        runtime: ServiceRuntime,
        logger,
        poll_interval_seconds: int,
        error_backoff_seconds: int,
    ):
        self._service = service
        self._runtime = runtime
        self._logger = logger
        self._poll_interval_seconds = max(5, poll_interval_seconds)
        self._error_backoff_seconds = max(5, error_backoff_seconds)

    def serve_forever(self) -> int:
        with self._runtime.acquire_singleton("serve") as lease:
            lease.write_status(
                state="idle",
                poll_interval_seconds=self._poll_interval_seconds,
                error_backoff_seconds=self._error_backoff_seconds,
                last_error=None,
            )
            log_event(
                self._logger,
                "Symphony local worker started",
                event="service_started",
                poll_interval_seconds=self._poll_interval_seconds,
                error_backoff_seconds=self._error_backoff_seconds,
            )

            while True:
                if self._runtime.is_stop_requested():
                    lease.write_status(state="stopping", note="Stop requested")
                    log_event(self._logger, "Stop requested", event="service_stop_requested")
                    break

                lease.write_status(state="polling")
                try:
                    summary = self._service.run_once()
                except KeyboardInterrupt:
                    lease.write_status(state="stopping", note="Interrupted by keyboard signal")
                    log_event(self._logger, "Symphony local worker interrupted", event="service_interrupted")
                    break
                except Exception as exc:
                    lease.write_status(
                        state="error",
                        last_error=str(exc),
                        last_failure_at=_utc_now(),
                    )
                    log_event(
                        self._logger,
                        "Symphony local worker hit a run failure",
                        event="service_run_failed",
                        error=str(exc),
                    )
                    self._sleep_with_heartbeat(lease, self._error_backoff_seconds, state="backoff")
                    continue

                if summary is None:
                    lease.write_status(
                        state="idle",
                        last_outcome="no_ready_issue",
                        last_polled_at=_utc_now(),
                        last_error=None,
                    )
                    self._sleep_with_heartbeat(lease, self._poll_interval_seconds, state="idle")
                    continue

                lease.write_status(
                    state="idle",
                    last_issue_number=summary.issue_number,
                    last_issue_title=summary.issue_title,
                    last_outcome=summary.outcome,
                    last_project_status=summary.project_status,
                    last_branch_name=summary.branch_name,
                    last_workspace_path=summary.workspace_path,
                    last_pull_request_url=summary.pull_request_url,
                    last_run_finished_at=summary.finished_at.isoformat(),
                    last_error=None,
                )
                self._sleep_with_heartbeat(lease, self._poll_interval_seconds, state="idle")

            log_event(self._logger, "Symphony local worker stopped", event="service_stopped")
        return 0

    def _sleep_with_heartbeat(self, lease, duration_seconds: int, *, state: str) -> None:
        remaining = max(0, duration_seconds)
        while remaining > 0:
            if self._runtime.is_stop_requested():
                return
            sleep_seconds = min(1, remaining)
            time.sleep(sleep_seconds)
            remaining -= sleep_seconds
            lease.heartbeat(state=state)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
