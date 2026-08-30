from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

import pytest
from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools" / "flags"
sys.path.insert(0, str(TOOLS))

from dxt3_fullcolor import AlphaEncoding, alpha_block_summary, encode_image
from flag_pipeline import (
    EXPECTED_COUNT,
    load_manifest,
    rasterize_master,
    repository_path,
    sha256_bytes,
)
import build_flags


def test_manifest_is_complete_unique_and_repository_relative() -> None:
    manifest = load_manifest()
    assert manifest["record_count"] == EXPECTED_COUNT
    assert manifest["design_version"] == "historical-v1"
    assert manifest["original_work_license"]["spdx"] == "CC0-1.0"
    fields = (
        "civilization_type",
        "art_define",
        "runtime_dds_path",
        "master_path",
        "master_sha256",
        "production_dds_sha256",
        "source_method",
        "source_page_url",
        "source_license",
        "attribution",
        "historical_scope",
        "licensing_note",
        "citations",
    )
    for field in fields:
        values = [record[field] for record in manifest["records"]]
        assert all(values), field
    for field in ("civilization_type", "art_define", "runtime_dds_path", "master_path"):
        values = [record[field] for record in manifest["records"]]
        assert len(set(values)) == EXPECTED_COUNT
    assert Counter(Path(record["master_path"]).suffix for record in manifest["records"]) == {
        ".svg": 36,
        ".png": 23,
    }
    assert all(
        not Path(record["master_path"]).is_absolute()
        and "session-state" not in record["master_path"].lower()
        for record in manifest["records"]
    )


def test_all_master_digests_match() -> None:
    for record in load_manifest()["records"]:
        master = repository_path(record["master_path"])
        assert master.is_file()
        assert sha256_bytes(master.read_bytes()) == record["master_sha256"]


def test_original_history_reconciles_all_59() -> None:
    history = json.loads(
        (TOOLS / "history" / "original-team-color.json").read_text(encoding="utf-8")
    )
    assert history["baseline_commit"] == "178f61f52a0ff96d86830d92e03d7967e655d9d0"
    assert history["record_count"] == EXPECTED_COUNT
    assert history["availability_counts"] == {
        "recoverable_from_git": 38,
        "stock_packed_not_available_loose": 16,
        "available_in_warlords_mirror": 5,
    }
    manifest_types = {
        record["civilization_type"] for record in load_manifest()["records"]
    }
    history_types = {record["civilization_type"] for record in history["records"]}
    assert history_types == manifest_types
    for record in history["records"]:
        if record["availability"] == "stock_packed_not_available_loose":
            assert record["sha256"] is None
            assert record["source"]["recovery"]
        else:
            assert len(record["sha256"]) == 64
            assert record["bytes"] > 128


def test_encoder_reproduces_representative_approved_flag() -> None:
    record = next(
        item
        for item in load_manifest()["records"]
        if item["civilization_type"] == "CIVILIZATION_FRANCE_BOURBON"
    )
    source = rasterize_master(repository_path(record["master_path"]))
    assert source.size == (128, 128)
    data, mip_records = encode_image(
        source, alpha_encoding=AlphaEncoding.FIXED_COLOR_ZERO
    )
    assert sha256_bytes(data) == record["production_dds_sha256"]
    assert [item["output_bytes"] for item in mip_records] == [
        16_384,
        4_096,
        1_024,
        256,
        64,
        16,
        16,
        16,
    ]
    assert all(
        summary["raw_alpha_nibbles"] == [0]
        for summary in alpha_block_summary(data)
    )


def test_fixed_color_mode_is_not_implicit() -> None:
    source = Image.new("RGBA", (128, 128), (20, 40, 80, 127))
    rgba, _ = encode_image(source, alpha_encoding=AlphaEncoding.RGBA)
    fixed, _ = encode_image(
        source, alpha_encoding=AlphaEncoding.FIXED_COLOR_ZERO
    )
    assert rgba != fixed
    assert any(
        summary["nonzero_alpha_texel_count"] > 0
        for summary in alpha_block_summary(rgba)
    )
    assert all(
        summary["nonzero_alpha_texel_count"] == 0
        for summary in alpha_block_summary(fixed)
    )


def test_encoder_cli_accepts_perfect_rgb_fidelity() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        source = root / "solid.png"
        output = root / "solid.dds"
        report = root / "report.json"
        Image.new("RGBA", (128, 128), (0, 0, 0, 255)).save(source)
        subprocess.run(
            [
                sys.executable,
                str(TOOLS / "dxt3_fullcolor.py"),
                str(source),
                str(output),
                "--alpha-encoding",
                "fixed-color-zero-alpha",
                "--report",
                str(report),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        document = json.loads(report.read_text(encoding="utf-8"))
        assert document["fidelity"]["rgb"]["psnr_db"] is None
        assert document["passed"] is True
        assert output.stat().st_size == 22_000


def test_publish_transaction_rolls_back_dds_when_xml_update_fails(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    destination = tmp_path / "flag.dds"
    art_xml = tmp_path / "art.xml"
    destination.write_bytes(b"old-dds")
    art_xml.write_bytes(b"old-xml")
    monkeypatch.setattr(build_flags, "ART_XML", art_xml)
    monkeypatch.setattr(build_flags, "asset_path", lambda _: destination)

    def fail_xml_update(_: set[str]) -> int:
        art_xml.write_bytes(b"partial-xml")
        raise RuntimeError("simulated XML publish failure")

    monkeypatch.setattr(build_flags, "set_fixed_color_flags", fail_xml_update)
    records = {
        "CIVILIZATION_TEST": {
            "runtime_dds_path": "Art/Interface/TeamColor/test.dds",
            "art_define": "ART_DEF_CIVILIZATION_TEST",
        }
    }
    results = {"CIVILIZATION_TEST": {"data": b"new-dds"}}
    with pytest.raises(RuntimeError, match="simulated XML publish failure"):
        build_flags.publish_transaction(
            ["CIVILIZATION_TEST"], records, results
        )
    assert destination.read_bytes() == b"old-dds"
    assert art_xml.read_bytes() == b"old-xml"
    assert not list(tmp_path.glob(".*.tmp"))
    assert not list(tmp_path.glob(".*.rollback"))
