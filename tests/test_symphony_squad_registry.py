from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from symphony.config import SquadConfig
from symphony.squad_registry import load_squad_registry


class SquadRegistryTests(unittest.TestCase):
    def test_loads_team_roles_jobs_and_schedules(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            squad_dir = root / "symphony" / "squad"
            roles_dir = squad_dir / "roles"
            roles_dir.mkdir(parents=True)
            (squad_dir / "team.md").write_text("team", encoding="utf-8")
            (roles_dir / "lead.md").write_text("lead", encoding="utf-8")
            (roles_dir / "implementer.md").write_text("implementer", encoding="utf-8")
            (squad_dir / "jobs.yaml").write_text(
                "jobs:\n"
                "  implement_issue:\n"
                "    kind: issue\n"
                "    roles: [lead, implementer]\n"
                "    concurrency: heavy\n"
                "    priority: 100\n",
                encoding="utf-8",
            )
            (squad_dir / "schedule.yaml").write_text(
                "schedules:\n"
                "  hygiene_scan:\n"
                "    interval_seconds: 3600\n",
                encoding="utf-8",
            )

            config = SquadConfig(
                enabled=True,
                team_path=squad_dir / "team.md",
                jobs_path=squad_dir / "jobs.yaml",
                schedule_path=squad_dir / "schedule.yaml",
                max_heavy_jobs=1,
                max_light_jobs=1,
                kickoff_comments_enabled=True,
                review_comments_enabled=True,
                triage_comments_enabled=True,
                hygiene_issue_title="Symphony hygiene report",
            )
            registry = load_squad_registry(config)

        self.assertIn("lead", registry.roles)
        self.assertIn("implement_issue", registry.jobs)
        self.assertIn("hygiene_scan", registry.schedules)


if __name__ == "__main__":
    unittest.main()
