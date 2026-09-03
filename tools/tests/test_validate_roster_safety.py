from __future__ import annotations

import importlib.util
import shutil
import struct
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "validate_roster_safety.py"
SPEC = importlib.util.spec_from_file_location("roster_validator", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class RosterValidatorTests(unittest.TestCase):
    def test_button_atlas_is_split_without_empty_sentinel(self) -> None:
        self.assertEqual(
            MODULE.Validator.button_parts(",Art/a.dds,Art/atlas.dds,2,3"),
            ["Art/a.dds", "Art/atlas.dds", "2", "3"],
        )

    def test_malformed_standalone_button_is_rejected(self) -> None:
        self.assertTrue(
            MODULE.Validator.is_malformed_standalone_button(",Art/a.dds")
        )
        self.assertFalse(
            MODULE.Validator.is_malformed_standalone_button("Art/a.dds")
        )
        self.assertFalse(
            MODULE.Validator.is_malformed_standalone_button(
                ",Art/a.dds,Art/atlas.dds,2,3"
            )
        )

    def test_format_token_pattern_handles_civ4_tokens(self) -> None:
        text = "%s1 founded %D2_Change%% cities for {player}"
        self.assertEqual(
            MODULE.TOKEN_RE.findall(text),
            ["%s1", "%D2_Change", "%%", "{player}"],
        )

    def test_dds_header_rejects_non_power_of_two_dimensions(self) -> None:
        scratch = Path(__file__).resolve().parent / ".validator-test.dds"
        data = bytearray(128)
        data[:4] = b"DDS "
        struct.pack_into("<I", data, 4, 124)
        struct.pack_into("<II", data, 12, 63, 64)
        struct.pack_into("<II", data, 76, 32, 0x4)
        data[84:88] = b"DXT5"
        scratch.write_bytes(data)
        try:
            validator = object.__new__(MODULE.Validator)
            validator.root = Path(__file__).resolve().parents[2]
            validator.errors = []
            validator.validate_dds(scratch)
            self.assertTrue(any("powers of two" in error for error in validator.errors))
        finally:
            scratch.unlink(missing_ok=True)

    def test_art_resolver_includes_inherited_base_assets(self) -> None:
        scratch = Path(__file__).resolve().parent / ".resolver-fixture"
        inherited = scratch / "Assets"
        target = inherited / "Art" / "Interface" / "StockAtlas.dds"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"stock")
        try:
            validator = object.__new__(MODULE.Validator)
            validator.asset_layers = (scratch / "BTS", inherited)
            validator._case_maps = {}
            self.assertEqual(
                validator.resolve_art("Art/Interface/StockAtlas.dds"),
                target,
            )
        finally:
            shutil.rmtree(scratch, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
