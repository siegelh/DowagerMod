from __future__ import annotations

import unittest
from pathlib import Path
from unittest import mock

from symphony.models import ChangeSet
from symphony.validation_runner import ValidationRunner


class ValidationRunnerTests(unittest.TestCase):
    def test_run_skips_gate_when_no_xml_or_dll_changes_exist(self) -> None:
        runner = ValidationRunner(Path(r"C:\repo"))
        result = runner.run(
            ChangeSet(
                files=("README.md",),
                plan_paths=(),
                requires_xml_gate=False,
                requires_dll_gate=False,
            )
        )

        self.assertFalse(result.required)
        self.assertTrue(result.passed)
        self.assertEqual(result.command, ())

    def test_run_uses_checkdll_for_dll_changes(self) -> None:
        runner = ValidationRunner(Path(r"C:\repo"))
        with mock.patch("symphony.validation_runner.subprocess.run") as run:
            run.return_value = mock.Mock(returncode=0, stdout="[GATE] OK", stderr="")
            result = runner.run(
                ChangeSet(
                    files=("third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvCity.cpp",),
                    plan_paths=(),
                    requires_xml_gate=False,
                    requires_dll_gate=True,
                )
            )

        self.assertTrue(result.required)
        self.assertTrue(result.passed)
        self.assertIn("-CheckDll", result.command)


if __name__ == "__main__":
    unittest.main()
