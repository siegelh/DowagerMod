#!/usr/bin/env python3
"""Validate generic city-art coverage for Dowager's Anglo-American style."""

from __future__ import annotations

import argparse
from pathlib import Path
import xml.etree.ElementTree as ET


STYLE = "ARTSTYLE_ANGLO_AMERICA"
LEAVES = ("Leaf_1x1", "Leaf_2x1", "Leaf_3x1", "Leaf_2x2")
ERAS = (
    "ERA_ANCIENT",
    "ERA_CLASSICAL",
    "ERA_MEDIEVAL",
    "ERA_RENAISSANCE",
    "ERA_INDUSTRIAL",
    "ERA_MODERN",
    "ERA_FUTURE",
)


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def matches(specification: str, value: str, all_value: str) -> bool:
    values = [item.strip() for item in specification.split(",") if item.strip()]
    if f"!{value}" in values:
        return False
    return value in values or all_value in values


def attributes(art_ref: ET.Element) -> dict[str, str]:
    result = {}
    for child in art_ref:
        if local_name(child.tag) == "Attribute":
            result[child.get("Class", "")] = child.text or ""
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    args = parser.parse_args()

    path = (
        args.repo_root
        / "CoreFiles"
        / "Sid Meier's Civilization IV Beyond the Sword"
        / "Beyond the Sword"
        / "Assets"
        / "XML"
        / "Buildings"
        / "CIV4CityLSystem.xml"
    )
    root = ET.parse(path).getroot()
    coverage: dict[tuple[str, str, str], list[str]] = {}
    industrial_colony_leaves = set()
    errors = []

    for node in root:
        if local_name(node.tag) != "LNode" or node.get("Name") not in LEAVES:
            continue
        leaf = node.get("Name", "")
        for art_ref in node:
            name = art_ref.get("Name", "")
            if local_name(art_ref.tag) != "ArtRef" or not name.startswith("generic:"):
                continue
            attrs = attributes(art_ref)
            eras = attrs.get("Era", "ERA_ALL")
            styles = attrs.get("ArtStyle", attrs.get("Artstyle", "ARTSTYLE_ALL"))
            if "ARTSTYLE_EUROPE" in styles and STYLE in styles and "ERA_INDUSTRIAL" in eras:
                errors.append(
                    f"{leaf} {name} mixes the European fallback into Industrial."
                )
            for era in ERAS:
                if not matches(eras, era, "ERA_ALL"):
                    continue
                for style in (STYLE, "ARTSTYLE_EUROPE"):
                    if matches(styles, style, "ARTSTYLE_ALL"):
                        coverage.setdefault((style, leaf, era), []).append(name)
                if (
                    era == "ERA_INDUSTRIAL"
                    and matches(styles, STYLE, "ARTSTYLE_ALL")
                    and name.startswith("generic:colony_euro_late.nif::")
                ):
                    industrial_colony_leaves.add(leaf)

    fallback_eras = {
        "ERA_ANCIENT",
        "ERA_CLASSICAL",
        "ERA_MEDIEVAL",
        "ERA_RENAISSANCE",
        "ERA_MODERN",
    }
    for era in fallback_eras:
        for leaf in LEAVES:
            european_count = len(
                coverage.get(("ARTSTYLE_EUROPE", leaf, era), [])
            )
            anglo_count = len(coverage.get((STYLE, leaf, era), []))
            if european_count and anglo_count < european_count:
                errors.append(
                    f"{STYLE} {leaf} coverage in {era} is {anglo_count}; "
                    f"European fallback coverage is {european_count}."
                )

    missing_colony = set(LEAVES) - industrial_colony_leaves
    if missing_colony:
        errors.append(
            "Industrial colony art missing for: " + ", ".join(sorted(missing_colony))
        )

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    for era in ERAS:
        counts = ", ".join(
            f"{leaf}={len(coverage.get((STYLE, leaf, era), []))}"
            for leaf in LEAVES
        )
        print(f"{era}: {counts}")
    print("Anglo-American generic city-art coverage passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
