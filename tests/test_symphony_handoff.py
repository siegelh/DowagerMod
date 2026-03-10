from __future__ import annotations

import unittest
from datetime import datetime, timezone

from symphony.handoff import build_pull_request_body
from symphony.models import ChangeSet, GitHubIssue, ValidationResult


class HandoffBuilderTests(unittest.TestCase):
    def test_pull_request_body_mentions_manual_testing_for_gameplay_changes(self) -> None:
        now = datetime.now(timezone.utc)
        issue = GitHubIssue(
            node_id="node-43",
            project_item_id="item-43",
            repository_full_name="siegelh/DowagerMod",
            number=43,
            title="Fix city-center luxury industry eligibility",
            body="body",
            state="OPEN",
            url="https://example.com/43",
            created_at=now,
            updated_at=now,
            labels=(),
            assignees=(),
            project_status="In Progress",
        )
        change_set = ChangeSet(
            files=("third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvCity.cpp",),
            plan_paths=("docs/plans/active/2026-03-10-gh-43.md",),
            requires_xml_gate=False,
            requires_dll_gate=True,
        )
        validation = ValidationResult(
            required=True,
            passed=True,
            command=("powershell", "-File", "tools/test_gate.ps1", "-CheckDll"),
            output="[GATE] OK",
        )

        body = build_pull_request_body(issue, "symphony/43-fix", change_set, validation)

        self.assertIn("Closes #43", body)
        self.assertIn("docs/MANUAL_SMOKE_TESTS.md", body)
        self.assertIn("CvCity.cpp", body)


if __name__ == "__main__":
    unittest.main()
