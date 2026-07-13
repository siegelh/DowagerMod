#!/usr/bin/env python3
"""Generate the deterministic leader/civilization roster baseline fixture."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
ASSETS_ROOT = (
    REPO_ROOT
    / "CoreFiles"
    / "Sid Meier's Civilization IV Beyond the Sword"
    / "Beyond the Sword"
    / "Assets"
)
XML_ROOT = ASSETS_ROOT / "XML"
OUTPUT = Path(__file__).with_name("roster_baseline.json")

RECENT_27_LEADERS = {
    "LEADER_ALEXANDER",
    "LEADER_AUGUSTUS",
    "LEADER_BOUDICA",
    "LEADER_BRENNUS",
    "LEADER_CHARLEMAGNE",
    "LEADER_CYRUS",
    "LEADER_DARIUS",
    "LEADER_DOWAGER_COUNTESS",
    "LEADER_FRANKLIN_ROOSEVELT",
    "LEADER_FREDERICK",
    "LEADER_GILGAMESH",
    "LEADER_HAILE_SELASSIE",
    "LEADER_HATSHEPSUT",
    "LEADER_JULIUS_CAESAR",
    "LEADER_JUSTINIAN",
    "LEADER_LINCOLN",
    "LEADER_LOUIS_XIV",
    "LEADER_MANSA_MUSA",
    "LEADER_MEHMED",
    "LEADER_NAPOLEON",
    "LEADER_PERICLES",
    "LEADER_RAMESSES",
    "LEADER_REGINALD_ENDICOTT_BARCLAY",
    "LEADER_SALADIN",
    "LEADER_SULEIMAN",
    "LEADER_VICTORIA",
    "LEADER_ZARA_YAQOB",
}

TABLES = (
    ("civilizations", "Civilizations/CIV4CivilizationInfos.xml", "CivilizationInfo"),
    ("leaders", "Civilizations/CIV4LeaderHeadInfos.xml", "LeaderHeadInfo"),
    ("traits", "Civilizations/CIV4TraitInfos.xml", "TraitInfo"),
    ("unit_classes", "Units/CIV4UnitClassInfos.xml", "UnitClassInfo"),
    ("units", "Units/CIV4UnitInfos.xml", "UnitInfo"),
    ("building_classes", "Buildings/CIV4BuildingClassInfos.xml", "BuildingClassInfo"),
    ("buildings", "Buildings/CIV4BuildingInfos.xml", "BuildingInfo"),
    ("civics", "GameInfo/CIV4CivicInfos.xml", "CivicInfo"),
    ("builds", "Units/CIV4BuildInfos.xml", "BuildInfo"),
    ("improvements", "Terrain/CIV4ImprovementInfos.xml", "ImprovementInfo"),
    ("promotions", "Units/CIV4PromotionInfos.xml", "PromotionInfo"),
)


def local_name(element: ET.Element) -> str:
    return element.tag.rsplit("}", 1)[-1]


def children(element: ET.Element, name: str) -> list[ET.Element]:
    return [child for child in element if local_name(child) == name]


def child(element: ET.Element, name: str) -> ET.Element | None:
    return next((item for item in element if local_name(item) == name), None)


def text(element: ET.Element, name: str, default: str = "") -> str:
    item = child(element, name)
    return default if item is None or item.text is None else item.text.strip()


def entries(path: Path, entry_name: str) -> list[ET.Element]:
    root = ET.parse(path).getroot()
    return [item for item in root.iter() if local_name(item) == entry_name]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def relative(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def tree_snapshot(root: Path) -> dict[str, object]:
    listed = subprocess.run(
        ["git", "ls-files", "-z", "--", relative(root)],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
    ).stdout
    files = [
        REPO_ROOT / item.decode("utf-8")
        for item in listed.split(b"\0")
        if item
    ]
    if any(not path.is_file() for path in files):
        raise ValueError(f"Tracked file missing below {relative(root)}")
    files.sort(key=relative)
    digest = hashlib.sha256()
    total_bytes = 0
    for path in files:
        file_hash = sha256_file(path)
        total_bytes += path.stat().st_size
        digest.update(relative(path).encode("utf-8"))
        digest.update(b"\0")
        digest.update(file_hash.encode("ascii"))
        digest.update(b"\n")
    return {
        "root": relative(root),
        "file_count": len(files),
        "total_bytes": total_bytes,
        "sha256": digest.hexdigest(),
    }


def direct_mapping(parent: ET.Element, group: str, row: str, key: str, value: str) -> list[dict[str, str]]:
    container = child(parent, group)
    if container is None:
        return []
    result = []
    for item in children(container, row):
        result.append({key: text(item, key), value: text(item, value)})
    return result


def main() -> None:
    global REPO_ROOT, ASSETS_ROOT, XML_ROOT, OUTPUT

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=REPO_ROOT,
        help="Clean repository worktree to snapshot (defaults to this script's worktree).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=OUTPUT,
        help="Fixture path to write.",
    )
    args = parser.parse_args()
    REPO_ROOT = args.repo_root.resolve()
    ASSETS_ROOT = (
        REPO_ROOT
        / "CoreFiles"
        / "Sid Meier's Civilization IV Beyond the Sword"
        / "Beyond the Sword"
        / "Assets"
    )
    XML_ROOT = ASSETS_ROOT / "XML"
    OUTPUT = args.output.resolve()

    source_commit = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()

    table_snapshots: dict[str, dict[str, object]] = {}
    relevant_hashes: dict[str, str] = {}
    for table_name, relative_xml, entry_name in TABLES:
        path = XML_ROOT / relative_xml
        type_order = [text(item, "Type") for item in entries(path, entry_name)]
        if not type_order or any(not item for item in type_order):
            raise ValueError(f"Missing Type in {relative_xml}:{entry_name}")
        if len(type_order) != len(set(type_order)):
            raise ValueError(f"Duplicate Type in {relative_xml}:{entry_name}")
        repo_path = relative(path)
        table_snapshots[table_name] = {
            "file": repo_path,
            "entry": entry_name,
            "count": len(type_order),
            "type_order": type_order,
        }
        relevant_hashes[repo_path] = sha256_file(path)

    leader_path = XML_ROOT / "Civilizations" / "CIV4LeaderHeadInfos.xml"
    leader_traits = {
        text(info, "Type"): [
            text(item, "TraitType")
            for traits in children(info, "Traits")
            for item in children(traits, "Trait")
        ]
        for info in entries(leader_path, "LeaderHeadInfo")
    }

    civilization_path = XML_ROOT / "Civilizations" / "CIV4CivilizationInfos.xml"
    packages = []
    excluded = {"CIVILIZATION_BARBARIAN", "CIVILIZATION_MINOR"}
    for civilization in entries(civilization_path, "CivilizationInfo"):
        civilization_type = text(civilization, "Type")
        if text(civilization, "bPlayable") != "1" or civilization_type in excluded:
            continue
        leaders = child(civilization, "Leaders")
        if leaders is None:
            continue
        unit_replacements = direct_mapping(
            civilization, "Units", "Unit", "UnitClassType", "UnitType"
        )
        building_replacements = direct_mapping(
            civilization,
            "Buildings",
            "Building",
            "BuildingClassType",
            "BuildingType",
        )
        for leader in children(leaders, "Leader"):
            if text(leader, "bLeaderAvailability") != "1":
                continue
            leader_type = text(leader, "LeaderName")
            if leader_type not in leader_traits:
                raise ValueError(f"Unknown leader {leader_type} in {civilization_type}")
            packages.append(
                {
                    "leader": leader_type,
                    "civilization": civilization_type,
                    "scope_cohort": (
                        "recent_27"
                        if leader_type in RECENT_27_LEADERS
                        else "remaining_32"
                    ),
                    "traits": leader_traits[leader_type],
                    "unit_replacements": unit_replacements,
                    "building_replacements": building_replacements,
                }
            )

    packages.sort(key=lambda item: (item["civilization"], item["leader"]))
    recent_count = sum(item["scope_cohort"] == "recent_27" for item in packages)
    remaining_count = sum(item["scope_cohort"] == "remaining_32" for item in packages)
    if (len(packages), recent_count, remaining_count) != (59, 27, 32):
        raise ValueError(
            "Expected 59 playable mappings split 27/32; got "
            f"{len(packages)} split {recent_count}/{remaining_count}"
        )

    fixture = {
        "schema_version": 1,
        "source_commit": source_commit,
        "assets_root": relative(ASSETS_ROOT),
        "scope": {
            "playable_mapping_count": len(packages),
            "recent_27_count": recent_count,
            "remaining_32_count": remaining_count,
            "excluded_from_playable_packages": sorted(excluded),
            "structural_snapshots_include_excluded_types": True,
        },
        "packages": packages,
        "info_type_snapshots": table_snapshots,
        "hashes": {
            "algorithm": "SHA-256",
            "tree_digest_contract": (
                "Select Git-tracked regular files below the root and sort by "
                "repository-relative POSIX path; for each append UTF-8 path, NUL, "
                "lowercase file SHA-256, and LF; SHA-256 the concatenated byte stream."
            ),
            "relevant_xml_files": dict(sorted(relevant_hashes.items())),
            "trees": {
                "xml": tree_snapshot(XML_ROOT),
                "python": tree_snapshot(ASSETS_ROOT / "Python"),
                "dll_source": tree_snapshot(
                    REPO_ROOT / "third_party" / "beyond-the-sword-sdk" / "CvGameCoreDLL"
                ),
            },
        },
    }
    OUTPUT.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
    try:
        output_label = relative(OUTPUT)
    except ValueError:
        output_label = str(OUTPUT)
    print(
        f"Wrote {output_label}: {len(packages)} mappings "
        f"({recent_count} recent, {remaining_count} remaining)"
    )


if __name__ == "__main__":
    main()
