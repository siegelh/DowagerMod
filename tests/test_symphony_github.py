from __future__ import annotations

import unittest
from datetime import datetime, timezone
from unittest import mock

from symphony.config import GitHubConfig
from symphony.github_client import GitHubClient
from symphony.models import GitHubIssue


def make_issue(number: int, title: str, status: str, labels: tuple[str, ...] = ()) -> GitHubIssue:
    now = datetime.now(timezone.utc)
    return GitHubIssue(
        node_id=f"node-{number}",
        project_item_id=f"item-{number}",
        repository_full_name="siegelh/DowagerMod",
        number=number,
        title=title,
        body="",
        state="OPEN",
        url=f"https://example.com/{number}",
        created_at=now,
        updated_at=now,
        labels=labels,
        assignees=(),
        project_status=status,
    )


class GitHubClientTests(unittest.TestCase):
    def test_pick_next_ready_issue_skips_blockers(self) -> None:
        client = GitHubClient(
            GitHubConfig(
                owner="siegelh",
                owner_type="user",
                repo="DowagerMod",
                project_number=1,
                status_field="Status",
                ready_state="Ready",
                planning_state="Planning",
                in_progress_state="In Progress",
                blocked_state="Blocked",
                human_review_state="Human Review",
                done_state="Done",
                blocker_labels=("blocked", "needs-human"),
                token="x",
            )
        )
        issues = [
            make_issue(1, "blocked issue", "Ready", ("blocked",)),
            make_issue(2, "eligible issue", "Ready"),
        ]
        with mock.patch.object(client, "list_project_issues", return_value=issues):
            selected = client.pick_next_ready_issue()

        self.assertIsNotNone(selected)
        self.assertEqual(selected.number, 2)

    def test_normalize_issue_node_reads_project_status(self) -> None:
        client = GitHubClient(
            GitHubConfig(
                owner="siegelh",
                owner_type="user",
                repo="DowagerMod",
                project_number=1,
                status_field="Status",
                ready_state="Ready",
                planning_state="Planning",
                in_progress_state="In Progress",
                blocked_state="Blocked",
                human_review_state="Human Review",
                done_state="Done",
                blocker_labels=(),
                token="x",
            )
        )
        issue = client._normalize_issue_node(  # pylint: disable=protected-access
            {
                "id": "item-1",
                "fieldValues": {
                    "nodes": [
                        {
                            "__typename": "ProjectV2ItemFieldSingleSelectValue",
                            "name": "Ready",
                            "field": {"name": "Status"},
                        }
                    ]
                },
                "content": {
                    "__typename": "Issue",
                    "id": "node-1",
                    "number": 1,
                    "title": "Test",
                    "body": "Body",
                    "state": "OPEN",
                    "url": "https://example.com/1",
                    "createdAt": "2026-03-09T00:00:00Z",
                    "updatedAt": "2026-03-09T00:00:00Z",
                    "repository": {"nameWithOwner": "siegelh/DowagerMod"},
                    "labels": {"nodes": [{"name": "Needs-Human"}]},
                    "assignees": {"nodes": [{"login": "siegelh"}]},
                },
            }
        )

        self.assertIsNotNone(issue)
        self.assertEqual(issue.project_status, "Ready")
        self.assertEqual(issue.labels, ("needs-human",))

    def test_get_or_create_draft_pull_request_reuses_existing_open_pr(self) -> None:
        client = GitHubClient(
            GitHubConfig(
                owner="siegelh",
                owner_type="user",
                repo="DowagerMod",
                project_number=1,
                status_field="Status",
                ready_state="Ready",
                planning_state="Planning",
                in_progress_state="In Progress",
                blocked_state="Blocked",
                human_review_state="Human Review",
                done_state="Done",
                blocker_labels=(),
                token="x",
            )
        )
        with mock.patch.object(
            client,
            "find_open_pull_request",
            return_value=mock.Mock(number=12, url="https://example.com/pr/12", title="Existing", is_draft=True, existing=True),
        ) as find_pr, mock.patch.object(client, "_rest") as rest:
            pull_request = client.get_or_create_draft_pull_request(
                branch_name="symphony/43-test",
                base_branch="agent-baseline",
                title="Test",
                body="Body",
            )

        self.assertEqual(pull_request.number, 12)
        find_pr.assert_called_once_with("symphony/43-test")
        rest.assert_not_called()

    def test_create_issue_comment_uses_rest_endpoint(self) -> None:
        client = GitHubClient(
            GitHubConfig(
                owner="siegelh",
                owner_type="user",
                repo="DowagerMod",
                project_number=1,
                status_field="Status",
                ready_state="Ready",
                planning_state="Planning",
                in_progress_state="In Progress",
                blocked_state="Blocked",
                human_review_state="Human Review",
                done_state="Done",
                blocker_labels=(),
                token="x",
            )
        )
        with mock.patch.object(client, "_rest", return_value={"html_url": "https://example.com/comment/1"}) as rest:
            url = client.create_issue_comment(43, "Hello")

        self.assertEqual(url, "https://example.com/comment/1")
        rest.assert_called_once()


if __name__ == "__main__":
    unittest.main()
