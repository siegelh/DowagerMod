"""Installer restore + hot-swap migration contract tests.

These prove the reliability fix from the installer overhaul:

  * every install restores the live tree via ``robocopy /MIR`` from pristine
    before overlaying the payload (no rename-based fast path);
  * no code path can create or rename to ``<live> - DELETE_ME``;
  * obsolete ``<live> - PRISTINE_HOT`` / ``<live> - DELETE_ME`` siblings left
    by older installers are removed when deletable (including read-only trees);
  * a genuinely locked stale folder produces an explicit, path-specific
    warning and does NOT block the install;
  * the live and pristine trees are never mistaken for stale artifacts.

All tests use temporary directories and mocks -- no real install is performed.
"""

from __future__ import annotations

import argparse
import io
import stat
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "CoreFiles"))

import install  # noqa: E402


INSTALL_SRC = (ROOT / "CoreFiles" / "install.py").read_text(
    encoding="utf-8", errors="ignore"
)


def _populate(tree: Path) -> Path:
    (tree / "sub").mkdir(parents=True)
    (tree / "sub" / "file.txt").write_text("data", encoding="utf-8")
    return tree


class LegacyArtifactCleanupTests(unittest.TestCase):
    def test_removes_deletable_stale_siblings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            live = base / "Game"
            live.mkdir()
            pristine = Path(str(live) + " - PRISTINE")
            pristine.mkdir()
            hot = _populate(base / "Game - PRISTINE_HOT")
            deleteme = _populate(base / "Game - DELETE_ME")

            buf = io.StringIO()
            with redirect_stdout(buf):
                install.cleanup_legacy_hot_artifacts(live, pristine)

            out = buf.getvalue()
            self.assertFalse(hot.exists())
            self.assertFalse(deleteme.exists())
            self.assertTrue(live.exists())
            self.assertTrue(pristine.exists())
            self.assertIn("Removed Game - PRISTINE_HOT", out)
            self.assertIn("Removed Game - DELETE_ME", out)

    def test_no_stale_siblings_is_silent_noop(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            live = base / "Game"
            live.mkdir()
            pristine = Path(str(live) + " - PRISTINE")
            pristine.mkdir()

            buf = io.StringIO()
            with redirect_stdout(buf):
                install.cleanup_legacy_hot_artifacts(live, pristine)

            self.assertTrue(live.exists())
            self.assertTrue(pristine.exists())
            self.assertEqual(buf.getvalue().strip(), "")

    def test_removes_readonly_stale_tree(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            live = base / "Game"
            live.mkdir()
            pristine = Path(str(live) + " - PRISTINE")
            pristine.mkdir()

            hot = base / "Game - PRISTINE_HOT"
            inner = hot / "locked"
            inner.mkdir(parents=True)
            ro = inner / "readonly.dat"
            ro.write_text("x", encoding="utf-8")
            ro.chmod(stat.S_IREAD)
            inner.chmod(stat.S_IREAD)

            try:
                buf = io.StringIO()
                with redirect_stdout(buf):
                    install.cleanup_legacy_hot_artifacts(live, pristine)
                self.assertFalse(hot.exists())
                self.assertIn("Removed Game - PRISTINE_HOT", buf.getvalue())
            finally:
                for p in (ro, inner):
                    try:
                        p.chmod(stat.S_IWRITE)
                    except OSError:
                        pass

    def test_locked_cleanup_warns_with_exact_path_and_continues(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            live = base / "Game"
            live.mkdir()
            pristine = Path(str(live) + " - PRISTINE")
            pristine.mkdir()
            deleteme = base / "Game - DELETE_ME"
            deleteme.mkdir()

            buf = io.StringIO()
            # Simulate a persistent Windows lock: rmtree always fails, and the
            # bounded retry sleeps are neutralized so the test is fast.
            with mock.patch.object(
                install.shutil, "rmtree", side_effect=PermissionError("locked")
            ), mock.patch.object(
                install.time, "sleep", return_value=None
            ), redirect_stdout(buf):
                install.cleanup_legacy_hot_artifacts(live, pristine)

            out = buf.getvalue()
            self.assertIn("WARNING", out)
            self.assertIn(str(deleteme), out)
            # A failure must never be reported as a success.
            self.assertNotIn("Removed Game - DELETE_ME", out)
            # The call returned (did not raise); the folder simply remains.
            self.assertTrue(deleteme.exists())
            # Live + pristine were never touched.
            self.assertTrue(live.exists())
            self.assertTrue(pristine.exists())

    def test_locked_cleanup_retries_bounded_number_of_times(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            live = base / "Game"
            live.mkdir()
            pristine = Path(str(live) + " - PRISTINE")
            pristine.mkdir()
            (base / "Game - DELETE_ME").mkdir()

            rmtree = mock.Mock(side_effect=PermissionError("locked"))
            with mock.patch.object(install.shutil, "rmtree", rmtree), \
                    mock.patch.object(install.time, "sleep", return_value=None), \
                    redirect_stdout(io.StringIO()):
                install.cleanup_legacy_hot_artifacts(live, pristine)

            # Bounded, not infinite: exactly the retry budget of _rmtree_with_retry.
            self.assertEqual(rmtree.call_count, 5)

    def test_never_deletes_pristine_even_if_it_collides_with_suffix(self) -> None:
        # Defensive resolved-identity guard: if a derived stale path resolves to
        # the pristine (or live) tree, it must be skipped rather than deleted.
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            live = base / "Game"
            live.mkdir()
            # Point "pristine" AT the DELETE_ME sibling path on purpose.
            pristine = Path(str(live) + " - DELETE_ME")
            pristine.mkdir()
            (pristine / "keep.txt").write_text("important", encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                install.cleanup_legacy_hot_artifacts(live, pristine)

            self.assertTrue(pristine.exists())
            self.assertTrue((pristine / "keep.txt").exists())


class InstallMirrorRestoreTests(unittest.TestCase):
    def test_install_mirror_restores_before_overlay_and_makes_no_hot_siblings(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            live = base / "Sid Meier's Civilization IV Beyond the Sword"
            live.mkdir()
            live_resolved = live.resolve()
            pristine = Path(str(live_resolved) + " - PRISTINE")
            pristine.mkdir()
            payload = base / "payload"
            payload.mkdir()

            calls: list[tuple[Path, Path, bool, str]] = []

            def fake_robocopy(src, dst, mirror, *, label):
                calls.append((Path(src), Path(dst), mirror, label))

            args = argparse.Namespace(
                install_dir=str(live), refresh_pristine=False
            )

            with mock.patch.object(
                install, "robocopy", side_effect=fake_robocopy
            ), mock.patch.object(
                install, "get_payload_root", return_value=payload
            ), mock.patch.object(
                install, "clean_civ4_user_data"
            ), mock.patch.object(
                install, "get_mod_version", return_value="test-version"
            ), mock.patch.object(
                install, "save_config"
            ), mock.patch.object(
                install, "load_config", return_value={}
            ), mock.patch.object(
                install, "capture_pristine"
            ) as capture, mock.patch.object(
                install, "validate_pristine_snapshot"
            ), mock.patch.object(
                install, "is_admin", return_value=True
            ), redirect_stdout(io.StringIO()):
                install.install(args)

            # Pristine already existed -> no capture/bootstrap this run.
            capture.assert_not_called()

            self.assertGreaterEqual(len(calls), 2)
            restore, overlay = calls[0], calls[1]

            # Every install restores from pristine via mirror FIRST.
            self.assertTrue(restore[2], "restore must be mirror=True (/MIR)")
            self.assertEqual(restore[3], "restore pristine")
            self.assertEqual(restore[1], live_resolved)
            self.assertEqual(restore[0].name, live_resolved.name + " - PRISTINE")

            # Then the payload overlay (non-mirror) on top.
            self.assertFalse(overlay[2], "overlay must be mirror=False (/E)")
            self.assertEqual(overlay[3], "overlay mod payload")

            # No hot-swap sibling was ever created by the install.
            self.assertFalse(Path(str(live_resolved) + " - DELETE_ME").exists())
            self.assertFalse(Path(str(live_resolved) + " - PRISTINE_HOT").exists())

            # Install completed to sentinel.
            self.assertTrue((live / install.SENTINEL_NAME).exists())

    def test_install_cleans_legacy_siblings_before_restoring(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            live = base / "Sid Meier's Civilization IV Beyond the Sword"
            live.mkdir()
            live_resolved = live.resolve()
            pristine = Path(str(live_resolved) + " - PRISTINE")
            pristine.mkdir()
            payload = base / "payload"
            payload.mkdir()

            # An older installer left both stale siblings behind.
            stale_hot = _populate(Path(str(live_resolved) + " - PRISTINE_HOT"))
            stale_del = _populate(Path(str(live_resolved) + " - DELETE_ME"))

            args = argparse.Namespace(
                install_dir=str(live), refresh_pristine=False
            )

            with mock.patch.object(install, "robocopy"), \
                    mock.patch.object(install, "get_payload_root", return_value=payload), \
                    mock.patch.object(install, "clean_civ4_user_data"), \
                    mock.patch.object(install, "get_mod_version", return_value="v"), \
                    mock.patch.object(install, "save_config"), \
                    mock.patch.object(install, "load_config", return_value={}), \
                    mock.patch.object(install, "capture_pristine"), \
                    mock.patch.object(install, "validate_pristine_snapshot"), \
                    mock.patch.object(install, "is_admin", return_value=True), \
                    redirect_stdout(io.StringIO()):
                install.install(args)

            # Migration removed the stale siblings; live + pristine survive.
            self.assertFalse(stale_hot.exists())
            self.assertFalse(stale_del.exists())
            self.assertTrue(live.exists())
            self.assertTrue(pristine.exists())


class SourceContractTests(unittest.TestCase):
    """Static guarantees that the retired hot-swap path is fully gone."""

    def test_install_hot_module_deleted(self) -> None:
        self.assertFalse((ROOT / "CoreFiles" / "install_hot.py").exists())

    def test_no_active_hot_swap_code_paths(self) -> None:
        src = INSTALL_SRC
        self.assertNotIn("import install_hot", src)
        self.assertNotIn("install_hot.", src)
        # No rename-based swap can create a DELETE_ME sibling.
        self.assertNotIn("os.rename(", src)
        self.assertNotIn("build_pristine_hot", src)
        self.assertNotIn("install_from_pristine_or_hot", src)
        # No FAST/SLOW hot-path status remains.
        self.assertNotIn("FAST PATH", src)
        self.assertNotIn("SLOW PATH", src)

    def test_only_allowed_pristine_hot_reference_is_migration_constant(self) -> None:
        src = INSTALL_SRC
        # The suffix constant is retained solely for migration cleanup.
        self.assertIn(
            'LEGACY_HOT_SUFFIXES = (" - PRISTINE_HOT", " - DELETE_ME")', src
        )
        # The obsolete config key may be popped, never written.
        self.assertNotIn('cfg["pristine_hot_dir"] =', src)

    def test_install_calls_mirror_restore_literal(self) -> None:
        # The canonical restore call must be present verbatim.
        self.assertIn(
            'robocopy(pristine, live, mirror=True, label="restore pristine")',
            INSTALL_SRC,
        )


if __name__ == "__main__":
    unittest.main()
