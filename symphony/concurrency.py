from __future__ import annotations

from dataclasses import dataclass

from .config import SquadConfig
from .models import JobDefinition


@dataclass(frozen=True)
class ConcurrencyDecision:
    allowed: bool
    reason: str


class ConcurrencyManager:
    def __init__(self, config: SquadConfig):
        self._config = config

    def can_run(self, job: JobDefinition) -> ConcurrencyDecision:
        if job.concurrency == "heavy" and self._config.max_heavy_jobs < 1:
            return ConcurrencyDecision(allowed=False, reason="heavy_jobs_disabled")
        if job.concurrency == "light" and self._config.max_light_jobs < 1:
            return ConcurrencyDecision(allowed=False, reason="light_jobs_disabled")
        return ConcurrencyDecision(allowed=True, reason="allowed")
