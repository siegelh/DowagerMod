#!/usr/bin/env python3
"""Deterministic Remaster visual phase 3-6 importer and auditor."""

from __future__ import annotations

import argparse
import copy
import datetime as dt
import hashlib
import json
import re
import shutil
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path


REMASTER_COMMIT = "a5e232f30eaae9fa980bc8ddcb2dba50b6321a89"
CITYSTYLES_COMMIT = "1af8f06"
DESTINATION_ROOT = (
    "CoreFiles/Sid Meier's Civilization IV Beyond the Sword/"
    "Beyond the Sword"
)
MANIFEST_PATH = "tools/manifests/remaster_visual_overhaul_phase_3_6.json"
MAPPING_PATH = "tools/manifests/remaster_citystyle_mapping.json"
PRIOR_MANIFEST_PATH = "tools/manifests/remaster_visual_overhaul_phase_1_2.json"

PAVEMENT_PATHS = [
    "Assets/Art/structures/Cities/all_an_lots.dds",
    "Assets/Art/structures/Cities/all_mod_lots.dds",
    "Assets/Art/structures/Cities/all_ren_lots.dds",
    "Assets/Art/structures/Cities/native_lots.dds",
    "Assets/Art/structures/Cities/native_lots_alt.dds",
]

REFERENCE_FIXES = {
    "Art/Structures/Buildings/Barracks/Modern_Barracks/Bunker.nif":
        "Art/Structures/Buildings/Barracks/Barracks_Modern/Bunker.nif",
    "Art/Structures/Buildings/Castle/Meso_Castle/Meso_Castle.nif":
        "Art/Structures/Buildings/castle/South_American_Castle/Meso_Castle.nif",
    "Art/Structures/Buildings/Crescent_HeroicEpic/Crescent HeroicEpic.nif":
        "Art/Structures/Buildings/HeroicEpic/Crescent_HeroicEpic/Crescent HeroicEpic.nif",
    "Art/Structures/Buildings/ForbiddenPalace/Greco_Roman_GreatPalace/GreatPalace.nif":
        "Art/Structures/Buildings/ForbiddenPalace/Europe_GreatPalace/GreatPalace.nif",
    "Art/Structures/Buildings/temple/temple.nif":
        "Art/Structures/Buildings/Barracks/Meso_Barracks/Temple.nif",
    "Art/Structures/Improvements/FarmFire/tribalvillage.kfm":
        "Art/Structures/Improvements/Farm/tribalvillage.kfm",
    "Art/Structures/Improvements/Plantation_Plain/Plantation_Mediterranean.nif":
        "Art/Structures/Improvements/Plantation_Plain/Plantation.nif",
}

CIV_STYLE_MAP = {
    "CIVILIZATION_AMERICA_UNION": "ARTSTYLE_ANGLO_AMERICA",
    "CIVILIZATION_ARABIA": "ARTSTYLE_ARABIA",
    "CIVILIZATION_AZTEC": "ARTSTYLE_MESO_AMERICA",
    "CIVILIZATION_BABYLON": "ARTSTYLE_CRESCENT",
    "CIVILIZATION_BYZANTIUM": "ARTSTYLE_GRECO_ROMAN",
    "CIVILIZATION_CARTHAGE": "ARTSTYLE_GRECO_ROMAN",
    "CIVILIZATION_FRANCE_FIFTH_REPUBLIC": "ARTSTYLE_EUROPE",
    "CIVILIZATION_HOLY_ROMAN": "ARTSTYLE_EUROPE",
    "CIVILIZATION_INCA": "ARTSTYLE_SOUTH_AMERICA",
    "CIVILIZATION_INDIA": "ARTSTYLE_INDIA",
    "CIVILIZATION_MAURYA": "ARTSTYLE_INDIA",
    "CIVILIZATION_JAPAN": "ARTSTYLE_JAPAN",
    "CIVILIZATION_KHMER": "ARTSTYLE_SOUTH_EAST_ASIA",
    "CIVILIZATION_KOREA": "ARTSTYLE_ASIA",
    "CIVILIZATION_MALI": "ARTSTYLE_AFRICA",
    "CIVILIZATION_MAYA": "ARTSTYLE_MESO_AMERICA",
    "CIVILIZATION_NATIVE_AMERICA": "ARTSTYLE_NATIVE_AMERICA",
    "CIVILIZATION_NETHERLANDS": "ARTSTYLE_EUROPE",
    "CIVILIZATION_PORTUGAL": "ARTSTYLE_IBERIA",
    "CIVILIZATION_POLAND": "ARTSTYLE_EUROPE",
    "CIVILIZATION_USSR": "ARTSTYLE_RUSSIA",
    "CIVILIZATION_SPAIN": "ARTSTYLE_IBERIA",
    "CIVILIZATION_SUMERIA": "ARTSTYLE_CRESCENT",
    "CIVILIZATION_VIKING": "ARTSTYLE_NORSE",
    "CIVILIZATION_ZULU": "ARTSTYLE_AFRICA",
    "CIVILIZATION_VENICE": "ARTSTYLE_EUROPE",
    "CIVILIZATION_MINOR": "ARTSTYLE_BARBARIAN",
    "CIVILIZATION_BARBARIAN": "ARTSTYLE_BARBARIAN",
    "CIVILIZATION_APACHE_CONFEDERACY": "ARTSTYLE_NATIVE_AMERICA",
    "CIVILIZATION_POLYNESIA_BTG": "ARTSTYLE_SOUTH_AMERICA",
    "CIVILIZATION_BRITISH_REGENCY": "ARTSTYLE_EUROPE",
    "CIVILIZATION_ELIZABETHAN_ENGLAND": "ARTSTYLE_EUROPE",
    "CIVILIZATION_VICTORIAN_BRITAIN": "ARTSTYLE_EUROPE",
    "CIVILIZATION_WARTIME_BRITAIN": "ARTSTYLE_EUROPE",
    "CIVILIZATION_PERSIA_FOUNDING_ACHAEMENID": "ARTSTYLE_CRESCENT",
    "CIVILIZATION_PERSIA_IMPERIAL_ACHAEMENID": "ARTSTYLE_CRESCENT",
    "CIVILIZATION_AMERICA_FOUNDING_REPUBLIC": "ARTSTYLE_ANGLO_AMERICA",
    "CIVILIZATION_AMERICA_NEW_DEAL": "ARTSTYLE_ANGLO_AMERICA",
    "CIVILIZATION_AMERICA_FEDERAL": "ARTSTYLE_ANGLO_AMERICA",
    "CIVILIZATION_EGYPT_EIGHTEENTH_DYNASTY": "ARTSTYLE_EGYPT",
    "CIVILIZATION_EGYPT_NEW_KINGDOM": "ARTSTYLE_EGYPT",
    "CIVILIZATION_OTTOMAN_CONQUEST": "ARTSTYLE_CRESCENT",
    "CIVILIZATION_OTTOMAN_CLASSICAL": "ARTSTYLE_CRESCENT",
    "CIVILIZATION_ETHIOPIA_SOLOMONIC": "ARTSTYLE_AFRICA",
    "CIVILIZATION_ETHIOPIA_IMPERIAL": "ARTSTYLE_AFRICA",
    "CIVILIZATION_GAULIC_CONFEDERATION": "ARTSTYLE_EUROPE",
    "CIVILIZATION_ICENI_BRITAIN": "ARTSTYLE_EUROPE",
    "CIVILIZATION_PETRINE_RUSSIA": "ARTSTYLE_RUSSIA",
    "CIVILIZATION_IMPERIAL_RUSSIA": "ARTSTYLE_RUSSIA",
    "CIVILIZATION_FRANCE_BOURBON": "ARTSTYLE_EUROPE",
    "CIVILIZATION_FRANCE_FIRST_EMPIRE": "ARTSTYLE_EUROPE",
    "CIVILIZATION_MACEDONIAN_EMPIRE": "ARTSTYLE_GRECO_ROMAN",
    "CIVILIZATION_ATHENIAN_GREECE": "ARTSTYLE_GRECO_ROMAN",
    "CIVILIZATION_MONGOL_EMPIRE": "ARTSTYLE_MONGOLIA",
    "CIVILIZATION_YUAN_DYNASTY": "ARTSTYLE_MONGOLIA",
    "CIVILIZATION_ROMAN_REPUBLIC_LATE": "ARTSTYLE_GRECO_ROMAN",
    "CIVILIZATION_ROMAN_PRINCIPATE": "ARTSTYLE_GRECO_ROMAN",
    "CIVILIZATION_QIN_DYNASTY": "ARTSTYLE_ASIA",
    "CIVILIZATION_PEOPLES_REPUBLIC_CHINA": "ARTSTYLE_ASIA",
    "CIVILIZATION_PRUSSIA": "ARTSTYLE_EUROPE",
    "CIVILIZATION_GERMAN_EMPIRE": "ARTSTYLE_EUROPE",
}


def timestamp() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def emit(event: str, **values: object) -> None:
    print(json.dumps({"event": event, "timestamp": timestamp(), **values}, sort_keys=True))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize(path: str) -> str:
    return path.replace("\\", "/")


def load_json(path: Path, default: object) -> object:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def clean_trailing_whitespace(path: Path) -> None:
    text = path.read_text(encoding="utf-8-sig")
    cleaned = "\n".join(line.rstrip() for line in text.splitlines()) + "\n"
    path.write_text(cleaned, encoding="utf-8")


def apply_reference_fixes(path: Path) -> list[dict[str, object]]:
    text = path.read_text(encoding="utf-8-sig")
    applied: list[dict[str, object]] = []
    for old, new in REFERENCE_FIXES.items():
        count = text.count(old)
        if count:
            text = text.replace(old, new)
            applied.append({"old": old, "new": new, "count": count})
    path.write_text(text, encoding="utf-8")
    return applied


def verify_source(remaster: Path) -> None:
    commit = subprocess.check_output(
        ["git", "-C", str(remaster), "rev-parse", "HEAD"],
        text=True,
    ).strip()
    if commit != REMASTER_COMMIT:
        raise RuntimeError(
            "Remaster checkout is at %s; expected %s" % (commit, REMASTER_COMMIT)
        )


def manifest_path(repo: Path) -> Path:
    return repo / MANIFEST_PATH


def update_manifest(
    repo: Path,
    feature: str,
    imports: list[dict[str, object]] | None = None,
    xml_merge: dict[str, object] | None = None,
    skipped: dict[str, object] | None = None,
) -> None:
    path = manifest_path(repo)
    manifest = load_json(
        path,
        {
            "name": "Remaster visual overhaul phase 3-6",
            "sourceRepository": r"C:\civ4remaster-reference",
            "sourceCommit": REMASTER_COMMIT,
            "destinationRoot": DESTINATION_ROOT,
            "features": {},
        },
    )
    feature_data = manifest["features"].setdefault(feature, {})
    if imports is not None:
        feature_data["imports"] = sorted(imports, key=lambda item: item["path"])
    if xml_merge is not None:
        feature_data["xmlMerge"] = xml_merge
    if skipped is not None:
        feature_data["skipped"] = skipped
    save_json(path, manifest)


def copy_batch(
    repo: Path,
    remaster: Path,
    feature: str,
    paths: list[str],
    reason: str,
) -> list[dict[str, object]]:
    unique_paths = sorted(set(normalize(path) for path in paths))
    started = time.monotonic()
    input_bytes = 0
    output_bytes = 0
    copied = 0
    unchanged = 0
    errors = 0
    records: list[dict[str, object]] = []
    emit(
        "batch_start",
        batch=feature,
        index=1,
        total=1,
        inputCount=len(unique_paths),
        retryCount=0,
    )
    for relative in unique_paths:
        source = remaster / Path(relative)
        destination = repo / DESTINATION_ROOT / Path(relative)
        if not source.is_file():
            errors += 1
            emit("file_error", batch=feature, path=relative, reason="missing source")
            continue
        size = source.stat().st_size
        source_hash = sha256(source)
        input_bytes += size
        if destination.is_file() and sha256(destination) == source_hash:
            unchanged += 1
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            copied += 1
        if sha256(destination) != source_hash:
            errors += 1
            emit("file_error", batch=feature, path=relative, reason="hash mismatch")
            continue
        output_bytes += destination.stat().st_size
        records.append(
            {
                "path": relative,
                "sha256": source_hash,
                "size": size,
                "reason": reason,
            }
        )
    duration = round(time.monotonic() - started, 3)
    emit(
        "batch_end",
        batch=feature,
        inputCount=len(unique_paths),
        outputCount=len(records),
        inputBytes=input_bytes,
        outputBytes=output_bytes,
        copied=copied,
        unchanged=unchanged,
        skipped=0,
        duplicates=len(paths) - len(unique_paths),
        errors=errors,
        durationSeconds=duration,
        status="success" if errors == 0 else "failure",
        retryCount=0,
    )
    emit(
        "reconciliation",
        batch=feature,
        expected=len(unique_paths),
        processed=len(unique_paths),
        persisted=len(records),
        copied=copied,
        unchanged=unchanged,
        skipped=0,
        duplicates=len(paths) - len(unique_paths),
        errors=errors,
        passed=errors == 0 and len(records) == len(unique_paths),
    )
    if errors:
        raise RuntimeError("%s import failed with %d error(s)" % (feature, errors))
    return records


def xml_blocks(text: str, item_tag: str) -> dict[str, str]:
    blocks: dict[str, str] = {}
    pattern = re.compile(
        r"<%s\b[^>]*>.*?</%s>" % (item_tag, item_tag),
        re.DOTALL,
    )
    for match in pattern.finditer(text):
        type_match = re.search(r"<Type>([^<]+)</Type>", match.group(0))
        if type_match:
            blocks[type_match.group(1)] = match.group(0)
    return blocks


def scale_values(block: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for field in ("fScale", "fInterfaceScale"):
        match = re.search(r"<%s>([^<]+)</%s>" % (field, field), block)
        if match:
            values[field] = match.group(1)
    return values


def merge_scale_fields(
    target_path: Path,
    source_path: Path,
    item_tag: str,
    expected_changed_entries: int,
) -> tuple[list[str], dict[str, dict[str, str]]]:
    target_text = target_path.read_text(encoding="utf-8-sig")
    source_text = source_path.read_text(encoding="utf-8-sig")
    source_blocks = xml_blocks(source_text, item_tag)
    source_scales = {
        art_type: scale_values(block) for art_type, block in source_blocks.items()
    }
    changed_types: list[str] = []
    changes: dict[str, dict[str, str]] = {}
    pattern = re.compile(
        r"<%s\b[^>]*>.*?</%s>" % (item_tag, item_tag),
        re.DOTALL,
    )

    def replace_block(match: re.Match[str]) -> str:
        block = match.group(0)
        type_match = re.search(r"<Type>([^<]+)</Type>", block)
        if not type_match:
            return block
        art_type = type_match.group(1)
        wanted = source_scales.get(art_type)
        if not wanted:
            return block
        original = scale_values(block)
        updated = block
        for field, value in wanted.items():
            updated = re.sub(
                r"(<%s>)[^<]+(</%s>)" % (field, field),
                lambda field_match: field_match.group(1) + value + field_match.group(2),
                updated,
                count=1,
            )
        if updated != block:
            changed_types.append(art_type)
            changes[art_type] = {
                "oldScale": original.get("fScale", ""),
                "newScale": wanted.get("fScale", ""),
                "oldInterfaceScale": original.get("fInterfaceScale", ""),
                "newInterfaceScale": wanted.get("fInterfaceScale", ""),
            }
        return updated

    merged = pattern.sub(replace_block, target_text)
    unique_changed = sorted(set(changed_types))
    if len(unique_changed) != expected_changed_entries:
        raise RuntimeError(
            "%s changed %d entries; expected %d"
            % (target_path.name, len(unique_changed), expected_changed_entries)
        )
    target_path.write_text(merged, encoding="utf-8")
    return unique_changed, changes


def git_changed_paths(remaster: Path, commit: str) -> list[str]:
    output = subprocess.check_output(
        [
            "git",
            "-C",
            str(remaster),
            "diff-tree",
            "--no-commit-id",
            "--name-only",
            "-r",
            commit,
        ],
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return [normalize(line.strip()) for line in output.splitlines() if line.strip()]


def strip_namespace(text: str) -> str:
    return re.sub(r'\sxmlns="[^"]+"', "", text, count=1)


def attribute_tokens(element: ET.Element, class_name: str) -> set[str]:
    values: set[str] = set()
    for attribute in element.iter("Attribute"):
        if attribute.get("Class") != class_name or not attribute.text:
            continue
        values.update(
            token.strip().lstrip("!")
            for token in attribute.text.split(",")
            if token.strip()
        )
    return values


def serialize_element(element: ET.Element) -> str:
    clone = copy.deepcopy(element)
    ET.indent(clone, space="\t")
    return ET.tostring(clone, encoding="unicode")


def merge_plot_lsystem(target_path: Path, source_path: Path) -> dict[str, object]:
    target_text = target_path.read_text(encoding="utf-8-sig")
    source_text = source_path.read_text(encoding="utf-8-sig")
    target_root = ET.fromstring(strip_namespace(target_text))
    source_root = ET.fromstring(strip_namespace(source_text))

    source_node_names = {
        element.get("Name") for element in source_root.findall("LNode")
    }
    source_production_names = {
        element.get("Name")
        for element in source_root.findall("LProduction")
        if element.get("Name")
    }
    source_improvements = attribute_tokens(source_root, "Improvement")
    target_improvements = attribute_tokens(target_root, "Improvement")
    missing_improvements = sorted(target_improvements - source_improvements)
    missing_set = set(missing_improvements)

    additions: list[ET.Element] = []
    added_nodes: list[str] = []
    added_productions: list[str] = []

    for element in target_root.findall("LNode"):
        name = element.get("Name")
        if name and name not in source_node_names:
            additions.append(copy.deepcopy(element))
            added_nodes.append(name)

    for element in target_root.findall("LProduction"):
        name = element.get("Name")
        if name and name not in source_production_names:
            additions.append(copy.deepcopy(element))
            added_productions.append(name)

    fallback_index = 0
    covered_fallbacks: set[str] = set()
    for element in target_root.findall("LProduction"):
        if element.get("Name"):
            continue
        tokens = attribute_tokens(element, "Improvement") & missing_set
        if not tokens:
            continue
        clone = copy.deepcopy(element)
        for attribute in clone.iter("Attribute"):
            if attribute.get("Class") == "Improvement" and attribute.text:
                filtered = [
                    token.strip()
                    for token in attribute.text.split(",")
                    if token.strip().lstrip("!") in tokens
                ]
                attribute.text = ",".join(filtered)
        fallback_index += 1
        name = "DowagerPreservedFallback%d" % fallback_index
        clone.set("Name", name)
        additions.append(clone)
        added_productions.append(name)
        covered_fallbacks.update(tokens)

    named_coverage: set[str] = set()
    for element in additions:
        if element.tag == "LProduction":
            named_coverage.update(attribute_tokens(element, "Improvement"))
    uncovered = missing_set - covered_fallbacks - named_coverage
    if uncovered:
        raise RuntimeError(
            "Plot L-System merge left improvements unrouted: %s"
            % ", ".join(sorted(uncovered))
        )

    serialized = "\n\n".join(serialize_element(element) for element in additions)
    merged = source_text.replace(
        "</LSystemInfos>",
        "\n\t<!-- Dowager-preserved custom nodes and routes -->\n"
        + serialized
        + "\n</LSystemInfos>",
        1,
    )
    target_path.write_text(merged, encoding="utf-8")
    return {
        "source": normalize(str(source_path)),
        "preservedNodes": sorted(added_nodes),
        "preservedProductions": sorted(added_productions),
        "preservedImprovementTokens": missing_improvements,
    }


def merge_global_art_styles(target_path: Path, source_path: Path) -> list[str]:
    target_text = target_path.read_text(encoding="utf-8-sig")
    source_text = source_path.read_text(encoding="utf-8-sig")
    source_styles = set(re.findall(r"<ArtStyleType>([^<]+)</ArtStyleType>", source_text))
    target_styles = set(re.findall(r"<ArtStyleType>([^<]+)</ArtStyleType>", target_text))
    missing = sorted(source_styles - target_styles)
    if missing:
        insertion = "".join(
            "\t\t<ArtStyleType>%s</ArtStyleType>\n" % style for style in missing
        )
        target_text, count = re.subn(
            r"(\s*</ArtStyleTypes>)",
            "\n" + insertion + r"\1",
            target_text,
            count=1,
        )
        if count != 1:
            raise RuntimeError("Could not locate ArtStyleTypes in GlobalTypes.xml")
        target_path.write_text(target_text, encoding="utf-8")
    return missing


def apply_civilization_mapping(target_path: Path) -> list[dict[str, str]]:
    text = target_path.read_text(encoding="utf-8-sig")
    seen: set[str] = set()
    mapping_records: list[dict[str, str]] = []
    pattern = re.compile(
        r"<CivilizationInfo\b[^>]*>.*?</CivilizationInfo>",
        re.DOTALL,
    )

    def replace_block(match: re.Match[str]) -> str:
        block = match.group(0)
        type_match = re.search(r"<Type>([^<]+)</Type>", block)
        if not type_match:
            return block
        civ_type = type_match.group(1)
        if civ_type not in CIV_STYLE_MAP:
            raise RuntimeError("No citystyle mapping for %s" % civ_type)
        style = CIV_STYLE_MAP[civ_type]
        old_match = re.search(r"<ArtStyleType>([^<]+)</ArtStyleType>", block)
        if not old_match:
            raise RuntimeError("No ArtStyleType field for %s" % civ_type)
        old_style = old_match.group(1)
        seen.add(civ_type)
        mapping_records.append(
            {"civilization": civ_type, "oldStyle": old_style, "newStyle": style}
        )
        return re.sub(
            r"(<ArtStyleType>)[^<]+(</ArtStyleType>)",
            lambda field_match: field_match.group(1) + style + field_match.group(2),
            block,
            count=1,
        )

    merged = pattern.sub(replace_block, text)
    missing = set(CIV_STYLE_MAP) - seen
    extra = seen - set(CIV_STYLE_MAP)
    if missing or extra or len(seen) != 61:
        raise RuntimeError(
            "Civilization mapping mismatch: seen=%d missing=%s extra=%s"
            % (len(seen), sorted(missing), sorted(extra))
        )
    target_path.write_text(merged, encoding="utf-8")
    return sorted(mapping_records, key=lambda record: record["civilization"])


def apply_buildings(repo: Path, remaster: Path) -> None:
    relative = "Assets/XML/Art/CIV4ArtDefines_Building.xml"
    changed_types, changes = merge_scale_fields(
        repo / DESTINATION_ROOT / relative,
        remaster / relative,
        "BuildingArtInfo",
        43,
    )
    update_manifest(
        repo,
        "larger_buildings",
        xml_merge={
            "path": relative,
            "changedEntryCount": len(changed_types),
            "changedTypes": changed_types,
            "changes": changes,
        },
    )
    emit("xml_merge", feature="larger_buildings", changedEntries=len(changed_types))


def apply_units(repo: Path, remaster: Path) -> None:
    relative = "Assets/XML/Art/CIV4ArtDefines_Unit.xml"
    changed_types, changes = merge_scale_fields(
        repo / DESTINATION_ROOT / relative,
        remaster / relative,
        "UnitArtInfo",
        224,
    )
    unit_root = remaster / "Assets/Art/Units"
    paths = [
        normalize(str(path.relative_to(remaster)))
        for path in unit_root.rglob("*")
        if path.is_file()
        and "selection effect" not in normalize(str(path.relative_to(unit_root))).lower()
        and path.name.lower() != "thumbs.db"
    ]
    imports = copy_batch(
        repo,
        remaster,
        "unit_presentation",
        paths,
        "Selected Remaster unit presentation art",
    )
    update_manifest(
        repo,
        "unit_presentation",
        imports=imports,
        xml_merge={
            "path": relative,
            "changedEntryCount": len(changed_types),
            "changedTypes": changed_types,
            "changes": changes,
        },
    )


def apply_effects(repo: Path, remaster: Path) -> None:
    nuke_root = remaster / "Assets/Art/Effects/explosion_nuke"
    paths = [
        normalize(str(path.relative_to(remaster)))
        for path in nuke_root.rglob("*")
        if path.is_file() and path.name.lower() != "thumbs.db"
    ] + PAVEMENT_PATHS
    imports = copy_batch(
        repo,
        remaster,
        "selected_effects",
        paths,
        "Nuclear explosion and pavement-free city presentation",
    )
    update_manifest(
        repo,
        "selected_effects",
        imports=imports,
        skipped={
            "selectionCircle": {
                "reason": (
                    "selection_ground.nif directly references godrays.tga; "
                    "god rays are excluded"
                ),
                "paths": [
                    "Assets/Art/Units/selection effect/circledot.dds",
                    "Assets/Art/Units/selection effect/groundselectioncircle.dds",
                    "Assets/Art/Units/selection effect/selection_ground.nif",
                    "Assets/Art/Units/selection effect/godrays.tga",
                ],
            }
        },
    )


def apply_citystyles(repo: Path, remaster: Path) -> None:
    feature_paths = git_changed_paths(remaster, CITYSTYLES_COMMIT)
    prefixes = (
        "Assets/Art/structures/Buildings/",
        "Assets/Art/structures/Cities/",
        "Assets/Art/structures/improvements/",
        "Assets/Art/shared/",
    )
    prior_manifest = load_json(repo / PRIOR_MANIFEST_PATH, {"files": []})
    prior_paths = {
        normalize(item["path"]) for item in prior_manifest.get("files", [])
    }
    excluded = prior_paths | set(PAVEMENT_PATHS)
    paths = [
        path
        for path in feature_paths
        if path.startswith(prefixes)
        and path not in excluded
        and Path(path).name.lower() != "thumbs.db"
        and (remaster / path).is_file()
    ]
    imports = copy_batch(
        repo,
        remaster,
        "cultural_citystyles",
        paths,
        "Cultural Citystyles structure, city, improvement, and shared art",
    )

    xml_root = repo / DESTINATION_ROOT / "Assets/XML"
    source_xml_root = remaster / "Assets/XML"
    global_styles = merge_global_art_styles(
        xml_root / "GlobalTypes.xml",
        source_xml_root / "GlobalTypes.xml",
    )
    mapping_records = apply_civilization_mapping(
        xml_root / "Civilizations/CIV4CivilizationInfos.xml"
    )
    save_json(
        repo / MAPPING_PATH,
        {
            "name": "Dowager Cultural Citystyles mapping",
            "sourceCommit": REMASTER_COMMIT,
            "mappingCount": len(mapping_records),
            "mappings": mapping_records,
            "notes": {
                "CIVILIZATION_POLYNESIA_BTG": (
                    "Uses the closest available warm-climate indigenous style, "
                    "ARTSTYLE_SOUTH_AMERICA."
                ),
                "American variants": (
                    "Use ARTSTYLE_ANGLO_AMERICA; European predecessor states "
                    "remain ARTSTYLE_EUROPE."
                ),
            },
        },
    )

    city_path = xml_root / "Buildings/Civ4CityLSystem.xml"
    shutil.copy2(source_xml_root / "Buildings/Civ4CityLSystem.xml", city_path)
    reference_fixes = apply_reference_fixes(city_path)
    clean_trailing_whitespace(city_path)
    plot_path = xml_root / "Buildings/CIV4PlotLSystem.xml"
    plot_merge = merge_plot_lsystem(
        plot_path,
        source_xml_root / "Buildings/CIV4PlotLSystem.xml",
    )
    reference_fixes.extend(apply_reference_fixes(plot_path))
    clean_trailing_whitespace(plot_path)
    update_manifest(
        repo,
        "cultural_citystyles",
        imports=imports,
        xml_merge={
            "globalTypesAdded": global_styles,
            "civilizationMappingCount": len(mapping_records),
            "cityLSystem": "Remaster current file; Dowager had no later edits",
            "plotLSystem": plot_merge,
            "referenceFixes": reference_fixes,
            "retainedCityBuildingScale": "0.33",
        },
    )
    emit(
        "xml_merge",
        feature="cultural_citystyles",
        addedArtStyles=len(global_styles),
        mappedCivilizations=len(mapping_records),
        preservedNodes=len(plot_merge["preservedNodes"]),
        preservedProductions=len(plot_merge["preservedProductions"]),
    )


def audit(repo: Path, remaster: Path) -> None:
    manifest = load_json(manifest_path(repo), None)
    if not manifest:
        raise RuntimeError("Manifest not found")
    errors: list[str] = []
    expected = 0
    persisted = 0
    for feature_name, feature in manifest["features"].items():
        for item in feature.get("imports", []):
            expected += 1
            relative = normalize(item["path"])
            source = remaster / relative
            destination = repo / DESTINATION_ROOT / relative
            if not source.is_file() or not destination.is_file():
                errors.append("%s: missing %s" % (feature_name, relative))
                continue
            if sha256(source) != item["sha256"]:
                errors.append("%s: source hash drift %s" % (feature_name, relative))
                continue
            if sha256(destination) != item["sha256"]:
                errors.append("%s: destination hash mismatch %s" % (feature_name, relative))
                continue
            persisted += 1

    mapping = load_json(repo / MAPPING_PATH, {"mappings": []})
    if mapping.get("mappingCount") != 61 or len(mapping.get("mappings", [])) != 61:
        errors.append("Citystyle mapping does not contain 61 civilizations")

    changed = subprocess.check_output(
        ["git", "-C", str(repo), "diff", "--name-only", "9a53e661e..HEAD"],
        text=True,
        encoding="utf-8",
        errors="replace",
    ).splitlines()
    excluded_needles = [
        "/Python/",
        "CvGameCoreDLL",
        "/Shaders/",
        "/Resource/",
        "godrays.tga",
        "clouds.dds",
    ]
    for path in changed:
        normalized = "/" + normalize(path)
        if any(needle.lower() in normalized.lower() for needle in excluded_needles):
            errors.append("Excluded path changed: %s" % path)

    plot_text = (
        repo
        / DESTINATION_ROOT
        / "Assets/XML/Buildings/CIV4PlotLSystem.xml"
    ).read_text(encoding="utf-8-sig")
    required_tokens = [
        "Node_Dowager_GreatPersonRotation_4x4",
        "Node_Dowager_NeutralWonderRotation_4x4",
        "IMPROVEMENT_JAPAN_CASTLE_TOWN",
        "IMPROVEMENT_NEUTRAL_GREAT_SPHINX",
        "IMPROVEMENT_SACRED_GROVE_NONE_BTG",
    ]
    for token in required_tokens:
        if token not in plot_text:
            errors.append("Preserved Plot L-System token missing: %s" % token)

    emit(
        "reconciliation",
        batch="full_audit",
        expected=expected,
        processed=expected,
        persisted=persisted,
        skipped=1,
        duplicates=0,
        errors=len(errors),
        passed=not errors and expected == persisted,
    )
    if errors:
        for error in errors:
            emit("audit_error", message=error)
        raise RuntimeError("Audit failed with %d error(s)" % len(errors))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "command",
        choices=("buildings", "units", "effects", "citystyles", "audit"),
    )
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument(
        "--remaster-root",
        type=Path,
        default=Path(r"C:\civ4remaster-reference"),
    )
    args = parser.parse_args()
    repo = args.repo_root.resolve()
    remaster = args.remaster_root.resolve()
    verify_source(remaster)
    if args.command == "buildings":
        apply_buildings(repo, remaster)
    elif args.command == "units":
        apply_units(repo, remaster)
    elif args.command == "effects":
        apply_effects(repo, remaster)
    elif args.command == "citystyles":
        apply_citystyles(repo, remaster)
    else:
        audit(repo, remaster)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        emit("fatal", error=str(exc))
        raise
