from __future__ import annotations

import stat
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "CoreFiles"))

import install  # noqa: E402


class InstallerUserDataTests(unittest.TestCase):
    def test_cleanup_removes_readonly_tree_and_preserves_user_state(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            user_data = Path(temp_dir)
            saves = user_data / "Saves"
            saves.mkdir()
            save = saves / "campaign.CivBeyondSwordSave"
            save.write_bytes(b"save")
            ini = user_data / "CivilizationIV.ini"
            ini.write_text("DisableCaching = 1\n", encoding="utf-8")

            cache = user_data / "CustomAssets" / "xml"
            cache.mkdir(parents=True)
            stale = cache / "stale.xml"
            stale.write_text("<stale />\n", encoding="utf-8")
            stale.chmod(stat.S_IREAD)
            cache.chmod(stat.S_IREAD)

            install.clean_user_data(user_data)

            self.assertFalse((user_data / "CustomAssets").exists())
            self.assertEqual(save.read_bytes(), b"save")
            self.assertEqual(
                ini.read_text(encoding="utf-8"),
                "DisableCaching = 1\n",
            )


if __name__ == "__main__":
    unittest.main()
