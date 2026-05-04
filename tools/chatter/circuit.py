"""Circuit breaker for fault-tolerant API calls.

Three states: CLOSED (normal), OPEN (skip calls), HALF_OPEN (probe).
After `failure_threshold` consecutive failures the breaker opens for
`open_seconds`. After cooldown the next call probes; on success the breaker
re-closes, on failure it re-opens.
"""
from __future__ import annotations

import time
from enum import Enum
from typing import Optional


class State(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    def __init__(self, failure_threshold: int = 3, open_seconds: int = 120, *, now_fn=time.time):
        self.failure_threshold = max(1, failure_threshold)
        self.open_seconds = max(1, open_seconds)
        self._consecutive_failures = 0
        self._opened_at: Optional[float] = None
        self._state = State.CLOSED
        self._now = now_fn

    @property
    def state(self) -> State:
        # Auto-transition OPEN -> HALF_OPEN once cooldown elapses.
        if self._state == State.OPEN and self._opened_at is not None:
            if self._now() - self._opened_at >= self.open_seconds:
                self._state = State.HALF_OPEN
        return self._state

    def can_call(self) -> bool:
        return self.state in (State.CLOSED, State.HALF_OPEN)

    def record_success(self) -> None:
        self._consecutive_failures = 0
        self._state = State.CLOSED
        self._opened_at = None

    def record_failure(self) -> None:
        self._consecutive_failures += 1
        if self._state == State.HALF_OPEN:
            # Probe failed, re-open
            self._state = State.OPEN
            self._opened_at = self._now()
        elif self._consecutive_failures >= self.failure_threshold:
            self._state = State.OPEN
            self._opened_at = self._now()

    def trip_immediately(self) -> None:
        """Force open without waiting for the threshold (e.g., on auth failure)."""
        self._state = State.OPEN
        self._opened_at = self._now()

    def status(self) -> dict:
        return {
            "state": self.state.value,
            "consecutive_failures": self._consecutive_failures,
            "opened_at_unix": self._opened_at,
        }
