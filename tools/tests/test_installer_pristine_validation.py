from __future__ import annotations

import argparse
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "CoreFiles"))

import install  # noqa: E402


class PristineMetadataTests(unittest.TestCase):
    def test_measure_install_tree_counts_files_and_logical_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "nested").mkdir()
            (root / "one.bin").write_bytes(b"1234")
            (root / "nested" / "two.bin").write_bytes(b"abc")

            self.assertEqual(install._measure_install_tree(root), (2, 7))

    def test_exact_metadata_match_has_no_problems(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "one.bin").write_bytes(b"1234")
            with mock.patch.object(
                install, "EXPECTED_PRISTINE_FILE_COUNT", 1
            ), mock.patch.object(
                install, "EXPECTED_PRISTINE_TOTAL_BYTES", 4
            ):
                self.assertEqual(install._pristine_metadata_problems(root), [])

    def test_enumeration_errors_fail_closed(self) -> None:
        def fail_walk(_root, *, onerror):
            onerror(PermissionError("denied"))
            return []

        with mock.patch.object(install.os, "walk", side_effect=fail_walk):
            with self.assertRaisesRegex(RuntimeError, "Could not enumerate"):
                install._measure_install_tree(Path("unreadable"))

    def test_count_and_size_mismatches_are_both_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "one.bin").write_bytes(b"1234")
            with mock.patch.object(
                install, "EXPECTED_PRISTINE_FILE_COUNT", 2
            ), mock.patch.object(
                install, "EXPECTED_PRISTINE_TOTAL_BYTES", 9
            ):
                problems = install._pristine_metadata_problems(root)

            self.assertEqual(len(problems), 2)
            self.assertIn("File count mismatch", problems[0])
            self.assertIn("Total size mismatch", problems[1])

    def test_validation_refuses_mismatched_pristine(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pristine = Path(tmp)
            (pristine / "file.bin").write_bytes(b"x")
            with mock.patch.object(
                install, "EXPECTED_PRISTINE_FILE_COUNT", 1
            ), mock.patch.object(
                install, "EXPECTED_PRISTINE_TOTAL_BYTES", 2
            ), redirect_stdout(io.StringIO()):
                with self.assertRaisesRegex(SystemExit, "validation FAILED"):
                    install.validate_pristine_snapshot(pristine)

    def test_existing_pristine_is_validated_before_restore(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            live = base / "Game"
            live.mkdir()
            pristine = Path(str(live.resolve()) + install.PRISTINE_SUFFIX)
            pristine.mkdir()
            payload = base / "payload"
            payload.mkdir()
            args = argparse.Namespace(
                install_dir=str(live), refresh_pristine=False
            )

            with mock.patch.object(
                install, "get_payload_root", return_value=payload
            ), mock.patch.object(
                install, "load_config", return_value={}
            ), mock.patch.object(
                install, "save_config"
            ), mock.patch.object(
                install, "validate_pristine_snapshot",
                side_effect=SystemExit("bad pristine"),
            ) as validate, mock.patch.object(
                install, "robocopy"
            ) as robocopy, mock.patch.object(
                install, "is_admin", return_value=True
            ), redirect_stdout(io.StringIO()):
                with self.assertRaisesRegex(SystemExit, "bad pristine"):
                    install.install(args)

            validate.assert_called_once_with(pristine)
            robocopy.assert_not_called()

    def test_new_capture_is_validated_after_copy(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            live = base / "Game"
            live.mkdir()
            pristine = base / "Game - PRISTINE"

            def fake_copy(_src, dst, mirror, *, label):
                self.assertTrue(mirror)
                self.assertEqual(label, "capture pristine")
                Path(dst).mkdir()

            with mock.patch.object(
                install, "_clean_install_problems", return_value=[]
            ), mock.patch.object(
                install, "_measure_install_tree", return_value=(30496, 3677850103)
            ), mock.patch.object(
                install, "robocopy", side_effect=fake_copy
            ), mock.patch.object(
                install, "validate_pristine_snapshot"
            ) as validate, mock.patch(
                "builtins.input", return_value="y"
            ), redirect_stdout(io.StringIO()):
                install.capture_pristine(live, pristine)

            validate.assert_called_once_with(pristine)

    def test_failed_refresh_capture_preserves_existing_pristine(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            live = base / "Game"
            live.mkdir()
            pristine = base / "Game - PRISTINE"
            pristine.mkdir()
            original = pristine / "original.bin"
            original.write_bytes(b"known-good")

            with mock.patch.object(
                install, "capture_pristine",
                side_effect=SystemExit("source rejected"),
            ), redirect_stdout(io.StringIO()):
                with self.assertRaisesRegex(SystemExit, "source rejected"):
                    install.refresh_pristine(live, pristine)

            self.assertEqual(original.read_bytes(), b"known-good")
            self.assertFalse(Path(str(pristine) + " - REFRESHING").exists())

    def test_successful_refresh_uses_validated_staging_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            live = base / "Game"
            live.mkdir()
            pristine = base / "Game - PRISTINE"
            pristine.mkdir()
            (pristine / "old.bin").write_bytes(b"old")
            calls = []

            def fake_capture(_live, staged):
                Path(staged).mkdir()
                (Path(staged) / "new.bin").write_bytes(b"new")

            def fake_copy(src, dst, mirror, *, label):
                calls.append((Path(src), Path(dst), mirror, label))
                for child in Path(dst).iterdir():
                    child.unlink()
                (Path(dst) / "new.bin").write_bytes(
                    (Path(src) / "new.bin").read_bytes()
                )

            with mock.patch.object(
                install, "capture_pristine", side_effect=fake_capture
            ), mock.patch.object(
                install, "robocopy", side_effect=fake_copy
            ), mock.patch.object(
                install, "validate_pristine_snapshot"
            ) as validate, redirect_stdout(io.StringIO()):
                install.refresh_pristine(live, pristine)

            self.assertEqual(
                calls,
                [(
                    Path(str(pristine) + " - REFRESHING"),
                    pristine,
                    True,
                    "replace pristine",
                )],
            )
            validate.assert_called_once_with(pristine)
            self.assertFalse((pristine / "old.bin").exists())
            self.assertEqual((pristine / "new.bin").read_bytes(), b"new")
            self.assertFalse(Path(str(pristine) + " - REFRESHING").exists())


if __name__ == "__main__":
    unittest.main()
