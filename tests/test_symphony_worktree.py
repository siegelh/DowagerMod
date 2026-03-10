from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from symphony.worktree_manager import WorktreeManager


class WorktreeManagerTests(unittest.TestCase):
    def test_describe_target_uses_issue_number_and_slug(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manager = WorktreeManager(
                repo_root=Path(tmp),
                workspace_root=Path(tmp) / "workspaces",
                base_branch="agent-baseline",
                branch_prefix="symphony",
            )
            target = manager.describe_target(42, "Fix Main Interface Loader")

        self.assertEqual(target.branch_name, "symphony/42-fix-main-interface-loader")
        self.assertTrue(str(target.path).endswith("42-fix-main-interface-loader"))


if __name__ == "__main__":
    unittest.main()
