from __future__ import annotations

import hashlib
import io
import json
import re
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path, PurePosixPath
from typing import Any

import cairosvg
from PIL import Image


EXPECTED_COUNT = 59
REPO_ROOT = Path(__file__).resolve().parents[2]
TOOLS_ROOT = Path(__file__).resolve().parent
MANIFEST_PATH = TOOLS_ROOT / "manifest.json"
ASSETS_ROOT = (
    REPO_ROOT
    / "CoreFiles"
    / "Sid Meier's Civilization IV Beyond the Sword"
    / "Beyond the Sword"
    / "Assets"
)
CIVILIZATION_XML = ASSETS_ROOT / "XML" / "Civilizations" / "CIV4CivilizationInfos.xml"
ART_XML = ASSETS_ROOT / "XML" / "Art" / "CIV4ArtDefines_Civilization.xml"

ART_BLOCK_PATTERN = re.compile(
    rb"<CivilizationArtInfo>.*?</CivilizationArtInfo>", re.DOTALL
)
TYPE_PATTERN = re.compile(rb"<Type>\s*([^<]+?)\s*</Type>")
WHITE_FLAG_PATTERN = re.compile(
    rb"<bWhiteFlag>([ \t\r\n]*)([01])([ \t\r\n]*)</bWhiteFlag>"
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def child_text(element: ET.Element, name: str) -> str:
    matches = [
        (child.text or "").strip()
        for child in element
        if local_name(child.tag) == name
    ]
    if len(matches) != 1 or not matches[0]:
        raise ValueError(
            f"Expected one non-empty {name} child, found {len(matches)}"
        )
    return matches[0]


def repository_path(relative_path: str) -> Path:
    relative = PurePosixPath(relative_path.replace("\\", "/"))
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"Unsafe repository path: {relative_path}")
    path = REPO_ROOT.joinpath(*relative.parts)
    path.resolve().relative_to(REPO_ROOT.resolve())
    return path


def asset_path(relative_path: str) -> Path:
    relative = PurePosixPath(relative_path.replace("\\", "/"))
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"Unsafe asset path: {relative_path}")
    path = ASSETS_ROOT.joinpath(*relative.parts)
    path.resolve().relative_to(ASSETS_ROOT.resolve())
    return path


def load_manifest() -> dict[str, Any]:
    document = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    records = document.get("records")
    if not isinstance(records, list) or len(records) != EXPECTED_COUNT:
        raise ValueError(
            f"Manifest records={len(records) if isinstance(records, list) else None}, "
            f"expected={EXPECTED_COUNT}"
        )
    civilization_types = [str(record["civilization_type"]) for record in records]
    art_defines = [str(record["art_define"]) for record in records]
    runtime_paths = [str(record["runtime_dds_path"]) for record in records]
    master_paths = [str(record["master_path"]) for record in records]
    for label, values in (
        ("civilization", civilization_types),
        ("art definition", art_defines),
        ("runtime DDS path", runtime_paths),
        ("master path", master_paths),
    ):
        duplicates = sorted({value for value in values if values.count(value) > 1})
        if duplicates:
            raise ValueError(f"Duplicate {label} values: {duplicates}")
    return document


def records_by_civilization() -> dict[str, dict[str, Any]]:
    return {
        str(record["civilization_type"]): record
        for record in load_manifest()["records"]
    }


def parse_live_mappings() -> tuple[dict[str, str], dict[str, dict[str, str]]]:
    civilization_to_art: dict[str, str] = {}
    for element in ET.parse(CIVILIZATION_XML).getroot().iter():
        if local_name(element.tag) != "CivilizationInfo":
            continue
        civilization_type = child_text(element, "Type")
        if child_text(element, "bPlayable") != "1":
            continue
        if civilization_type in civilization_to_art:
            raise ValueError(f"Duplicate civilization entry: {civilization_type}")
        civilization_to_art[civilization_type] = child_text(element, "ArtDefineTag")

    art_by_type: dict[str, dict[str, str]] = {}
    for element in ET.parse(ART_XML).getroot().iter():
        if local_name(element.tag) != "CivilizationArtInfo":
            continue
        art_type = child_text(element, "Type")
        if art_type in art_by_type:
            raise ValueError(f"Duplicate art definition: {art_type}")
        art_by_type[art_type] = {
            "path": child_text(element, "Path"),
            "white_flag": child_text(element, "bWhiteFlag"),
        }
    return civilization_to_art, art_by_type


def validate_manifest_against_live(*, require_fixed_color: bool) -> None:
    manifest = load_manifest()
    records = {
        str(record["civilization_type"]): record
        for record in manifest["records"]
    }
    civilization_to_art, art_by_type = parse_live_mappings()
    if set(civilization_to_art) != set(records):
        raise ValueError(
            "Playable civilization mismatch: "
            f"missing={sorted(set(records) - set(civilization_to_art))}, "
            f"unexpected={sorted(set(civilization_to_art) - set(records))}"
        )
    for civilization_type, record in records.items():
        expected_art = str(record["art_define"])
        live_art = civilization_to_art[civilization_type]
        if live_art != expected_art:
            raise ValueError(
                f"{civilization_type} art definition={live_art}, expected={expected_art}"
            )
        if expected_art not in art_by_type:
            raise ValueError(f"Missing art definition: {expected_art}")
        live = art_by_type[expected_art]
        expected_path = str(record["runtime_dds_path"])
        if live["path"].replace("\\", "/") != expected_path.replace("\\", "/"):
            raise ValueError(
                f"{expected_art} path={live['path']}, expected={expected_path}"
            )
        if live["white_flag"] not in {"0", "1"}:
            raise ValueError(
                f"{expected_art} has invalid bWhiteFlag={live['white_flag']}"
            )
        if require_fixed_color and live["white_flag"] != "1":
            raise ValueError(
                f"{expected_art} bWhiteFlag={live['white_flag']}, expected=1"
            )
        master = repository_path(str(record["master_path"]))
        if not master.is_file():
            raise FileNotFoundError(master)
        if sha256_path(master) != record["master_sha256"]:
            raise ValueError(f"Master digest mismatch: {master}")

    excluded = set(manifest["excluded_art_definitions"])
    unexpected_fixed = {
        art_type
        for art_type, values in art_by_type.items()
        if values["white_flag"] == "1" and art_type not in {
            str(record["art_define"]) for record in records.values()
        }
    }
    if unexpected_fixed:
        raise ValueError(f"Unexpected bWhiteFlag=1 entries: {sorted(unexpected_fixed)}")
    missing_excluded = excluded - set(art_by_type)
    if missing_excluded:
        raise ValueError(
            f"Excluded art definitions missing from live XML: {sorted(missing_excluded)}"
        )


def rasterize_master(path: Path, size: int = 128) -> Image.Image:
    if path.suffix.lower() == ".svg":
        payload = cairosvg.svg2png(
            url=str(path),
            output_width=1024,
            output_height=1024,
        )
        image = Image.open(io.BytesIO(payload)).convert("RGBA")
    else:
        image = Image.open(path).convert("RGBA")
    if image.size != (1024, 1024):
        raise ValueError(f"Master must be 1024x1024: {path} is {image.size}")
    if size == 1024:
        return image
    return image.resize((size, size), Image.Resampling.LANCZOS)


def changed_civilizations() -> list[str]:
    records = records_by_civilization()
    command = [
        "git",
        "-C",
        str(REPO_ROOT),
        "diff",
        "--name-only",
        "HEAD",
        "--",
        "tools/flags/designs",
        "tools/flags/manifest.json",
    ]
    changed = {
        line.strip().replace("\\", "/")
        for line in subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        ).stdout.splitlines()
        if line.strip()
    }
    if "tools/flags/manifest.json" in changed:
        return sorted(records)
    return sorted(
        civilization_type
        for civilization_type, record in records.items()
        if str(record["master_path"]).replace("\\", "/") in changed
    )


def set_fixed_color_flags(civilization_types: set[str]) -> int:
    records = records_by_civilization()
    selected_art = {
        str(records[civilization_type]["art_define"])
        for civilization_type in civilization_types
    }
    original = ART_XML.read_bytes()
    changes = 0

    def replace_block(match: re.Match[bytes]) -> bytes:
        nonlocal changes
        block = match.group(0)
        type_match = TYPE_PATTERN.search(block)
        if type_match is None:
            raise ValueError("CivilizationArtInfo block has no Type")
        art_type = type_match.group(1).decode("ascii").strip()
        if art_type not in selected_art:
            return block
        white_matches = list(WHITE_FLAG_PATTERN.finditer(block))
        if len(white_matches) != 1:
            raise ValueError(
                f"{art_type} must have exactly one binary bWhiteFlag value"
            )
        white_match = white_matches[0]
        if white_match.group(2) == b"1":
            return block
        changes += 1
        start, end = white_match.span(2)
        return block[:start] + b"1" + block[end:]

    updated = ART_BLOCK_PATTERN.sub(replace_block, original)
    if selected_art:
        found_art = {
            TYPE_PATTERN.search(match.group(0)).group(1).decode("ascii").strip()
            for match in ART_BLOCK_PATTERN.finditer(original)
            if TYPE_PATTERN.search(match.group(0)) is not None
        }
        missing = selected_art - found_art
        if missing:
            raise ValueError(f"Selected art definitions missing: {sorted(missing)}")
    if updated != original:
        ART_XML.write_bytes(updated)
    return changes
