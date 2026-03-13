from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from symphony.config import build_config
from symphony.models import WorkflowDefinition


class ConfigTests(unittest.TestCase):
    def test_build_config_resolves_env_paths_and_token(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            local_appdata = repo_root / "localappdata"
            os.environ["LOCALAPPDATA"] = str(local_appdata)
            (repo_root / ".env").write_text("GITHUB_TOKEN=test-token\n", encoding="utf-8")
            workflow = WorkflowDefinition(
                path=repo_root / "symphony" / "WORKFLOW.md",
                config={
                    "tracker": {
                        "kind": "github",
                        "owner": "siegelh",
                        "owner_type": "user",
                        "repo": "DowagerMod",
                        "project_number": 1,
                    },
                    "workspace": {
                        "root": r"C:\sw",
                        "base_branch": "agent-baseline",
                        "branch_prefix": "symphony",
                    },
                    "runtime": {
                        "state_root": r"$LOCALAPPDATA\Symphony\DowagerMod",
                    },
                    "codex": {
                        "command": ["codex", "app-server"],
                    },
                },
                prompt_template="body",
            )

            config = build_config(workflow, repo_root)

        self.assertEqual(config.github.token, "test-token")
        self.assertEqual(config.workspace.root, Path(r"C:\sw"))
        self.assertEqual(config.codex.command, ("codex", "app-server"))
        self.assertEqual(config.runtime.poll_interval_seconds, 60)
        self.assertEqual(config.runtime.error_backoff_seconds, 120)


if __name__ == "__main__":
    unittest.main()
