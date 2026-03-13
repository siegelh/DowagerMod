from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

from symphony.config import SquadConfig
from symphony.history import RunHistory
from symphony.models import GitHubIssue, IssueComment, JobDefinition, PullRequestInfo, ScheduleEntry
from symphony.router import SquadRouter


class RouterTests(unittest.TestCase):
    def test_router_prefers_ready_implementation_issue(self) -> None:
        config = mock.Mock()
        config.workspace.branch_prefix = "symphony"
        config.workspace.base_branch = "agent-baseline"

        registry = mock.Mock()
        registry.jobs = {
            "implement_issue": JobDefinition(
                name="implement_issue",
                kind="issue",
                roles=("lead", "implementer", "reviewer"),
                concurrency="heavy",
                priority=100,
                source_statuses=("Ready",),
            ),
            "triage_issue": JobDefinition(
                name="triage_issue",
                kind="issue",
                roles=("triage",),
                concurrency="light",
                priority=80,
                source_statuses=("Inbox",),
            ),
        }
        github = mock.Mock()
        github.pick_next_ready_issue.return_value = _build_issue(60, "Ready")
        github.pick_next_inbox_issue.return_value = _build_issue(61, "Inbox")

        with tempfile.TemporaryDirectory() as tmp:
            history = RunHistory(Path(tmp))
            router = SquadRouter(github, config, registry, history)
            candidate = router.pick_next()

        self.assertIsNotNone(candidate)
        self.assertEqual(candidate.job_name, "implement_issue")
        self.assertEqual(candidate.issue.number, 60)

    def test_router_picks_unreviewed_symphony_pr(self) -> None:
        config = mock.Mock()
        config.workspace.branch_prefix = "symphony"
        config.workspace.base_branch = "agent-baseline"
        registry = mock.Mock()
        registry.jobs = {
            "review_pr": JobDefinition(
                name="review_pr",
                kind="pull_request",
                roles=("reviewer",),
                concurrency="light",
                priority=60,
            )
        }
        pull_request = PullRequestInfo(
            number=44,
            url="https://example.com/pr/44",
            title="Review me",
            is_draft=True,
            existing=True,
            head_ref_name="symphony/44-review-me",
            base_ref_name="agent-baseline",
            created_at=datetime.now(timezone.utc),
        )
        github = mock.Mock()
        github.list_open_symphony_pull_requests.return_value = (pull_request,)
        github.list_issue_comments.return_value = (
            IssueComment(
                id=1,
                url="https://example.com/comment/1",
                body="ordinary comment",
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            ),
        )

        with tempfile.TemporaryDirectory() as tmp:
            history = RunHistory(Path(tmp))
            router = SquadRouter(github, config, registry, history)
            candidate = router.pick_next(explicit_job="review_pr")

        self.assertIsNotNone(candidate)
        self.assertEqual(candidate.job_name, "review_pr")
        self.assertEqual(candidate.pull_request.number, 44)

    def test_router_picks_due_hygiene_scan(self) -> None:
        config = mock.Mock()
        config.workspace.branch_prefix = "symphony"
        config.workspace.base_branch = "agent-baseline"
        registry = mock.Mock()
        registry.jobs = {
            "hygiene_scan": JobDefinition(
                name="hygiene_scan",
                kind="scheduled",
                roles=("hygiene",),
                concurrency="light",
                priority=40,
                schedule_key="hygiene_scan",
            )
        }
        registry.get_job.return_value = registry.jobs["hygiene_scan"]
        registry.schedules = {"hygiene_scan": ScheduleEntry(name="hygiene_scan", interval_seconds=60)}
        github = mock.Mock()

        with tempfile.TemporaryDirectory() as tmp:
            state_root = Path(tmp)
            runs_dir = state_root / "runs"
            runs_dir.mkdir(parents=True, exist_ok=True)
            old_summary = {
                "job_name": "hygiene_scan",
                "issue_number": 0,
                "issue_title": "Symphony hygiene report",
                "branch_name": "",
                "workspace_path": "c:\\DowagerMod",
                "started_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
                "finished_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
                "outcome": "completed",
                "project_status": "",
            }
            (runs_dir / "hygiene-old.json").write_text(__import__("json").dumps(old_summary), encoding="utf-8")
            history = RunHistory(state_root)
            router = SquadRouter(github, config, registry, history)
            candidate = router.pick_next(explicit_job="hygiene_scan")

        self.assertIsNotNone(candidate)
        self.assertTrue(candidate.scheduled)


def _build_issue(number: int, project_status: str) -> GitHubIssue:
    now = datetime.now(timezone.utc)
    return GitHubIssue(
        node_id=f"node-{number}",
        project_item_id=f"item-{number}",
        repository_full_name="siegelh/DowagerMod",
        number=number,
        title=f"Issue {number}",
        body="body",
        state="OPEN",
        url=f"https://example.com/{number}",
        created_at=now,
        updated_at=now,
        labels=(),
        assignees=(),
        project_status=project_status,
    )


if __name__ == "__main__":
    unittest.main()
