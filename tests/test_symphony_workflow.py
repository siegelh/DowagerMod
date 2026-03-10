from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from symphony.workflow_loader import WorkflowError, load_workflow, render_prompt


class WorkflowLoaderTests(unittest.TestCase):
    def test_load_workflow_parses_front_matter_and_prompt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "WORKFLOW.md"
            path.write_text(
                "---\ntracker:\n  kind: github\n---\nHello {{ issue.number }}\n",
                encoding="utf-8",
            )
            workflow = load_workflow(path)

        self.assertEqual(workflow.config["tracker"]["kind"], "github")
        self.assertEqual(workflow.prompt_template, "Hello {{ issue.number }}")

    def test_load_workflow_rejects_non_mapping_front_matter(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "WORKFLOW.md"
            path.write_text("---\n- bad\n---\nbody\n", encoding="utf-8")
            with self.assertRaises(WorkflowError):
                load_workflow(path)

    def test_render_prompt_is_strict_about_missing_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "WORKFLOW.md"
            path.write_text("Hello {{ issue.number }} {{ missing }}", encoding="utf-8")
            workflow = load_workflow(path)
            with self.assertRaises(WorkflowError):
                render_prompt(workflow, {"issue": {"number": 42}})


if __name__ == "__main__":
    unittest.main()
