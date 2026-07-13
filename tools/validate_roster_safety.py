#!/usr/bin/env python3
"""Cross-file safety checks for roster XML, text, buttons, and model art."""

from __future__ import annotations

import argparse
import json
import re
import struct
import subprocess
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path, PurePosixPath


GAME_DIR = Path("CoreFiles/Sid Meier's Civilization IV Beyond the Sword")
BTS_ASSETS = GAME_DIR / "Beyond the Sword" / "Assets"
INHERITED_ASSETS = (GAME_DIR / "Assets", GAME_DIR / "Warlords" / "Assets")
BASELINE = Path("tools/baselines/roster_baseline.json")
ART_EXTENSIONS = {".dds", ".nif", ".kfm", ".kf"}
NULL_TYPES = {"", "NONE", "NO_UNIT", "NO_BUILDING", "NO_PROMOTION", "NO_TECH",
              "NO_CIVIC", "NO_RELIGION", "NO_CORPORATION", "NO_IMPROVEMENT",
              "NO_BONUS", "NO_LEADER", "NO_CIVILIZATION"}
TOKEN_RE = re.compile(
    r"%%|%(?:\d+\$)?[A-Za-z](?:\d+(?:_[A-Za-z0-9]+)?)?|\{[A-Za-z_][A-Za-z0-9_]*\}"
)
EMBEDDED_ART_RE = re.compile(
    rb"(?i)([A-Za-z0-9_ .()'@+\-/\\]{1,240}\.(?:dds|nif|kfm|kf))(?=[\x00\s])"
)


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def direct_text(node: ET.Element, name: str) -> str:
    for child in node:
        if local_name(child.tag) == name:
            return (child.text or "").strip()
    return ""


def relative(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path)


class Validator:
    def __init__(self, root: Path, all_files: bool) -> None:
        self.root = root.resolve()
        self.bts = self.root / BTS_ASSETS
        self.asset_layers = (self.bts,) + tuple(self.root / item for item in INHERITED_ASSETS)
        self.all_files = all_files
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self._xml_cache: dict[Path, ET.Element | None] = {}
        self.changed = self.changed_paths()
        self.xml_files = sorted((self.bts / "XML").rglob("*.xml"))
        self._case_maps: dict[Path, dict[str, Path]] = {}

    def fail(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    def changed_paths(self) -> set[str]:
        commands = (
            ("diff", "--name-only", "--diff-filter=ACMRTUXB"),
            ("diff", "--cached", "--name-only", "--diff-filter=ACMRTUXB"),
            ("ls-files", "--others", "--exclude-standard"),
        )
        result: set[str] = set()
        for args in commands:
            proc = subprocess.run(
                ["git", "-C", str(self.root), *args],
                check=True, capture_output=True, text=True,
            )
            result.update(line.strip().replace("\\", "/") for line in proc.stdout.splitlines() if line.strip())
        return result

    def parse(self, path: Path) -> ET.Element | None:
        if path in self._xml_cache:
            return self._xml_cache[path]
        try:
            root = ET.parse(path).getroot()
            self._xml_cache[path] = root
            return root
        except (ET.ParseError, OSError) as exc:
            self.fail(f"{relative(path, self.root)}: cannot parse XML: {exc}")
            self._xml_cache[path] = None
            return None

    def validate_baseline(self) -> None:
        path = self.root / BASELINE
        if not path.is_file():
            self.fail(f"{BASELINE.as_posix()}: roster baseline is missing")
            return
        try:
            snapshots = json.loads(path.read_text(encoding="utf-8"))["info_type_snapshots"]
        except (OSError, ValueError, KeyError) as exc:
            self.fail(f"{BASELINE.as_posix()}: invalid baseline: {exc}")
            return
        for table, snapshot in snapshots.items():
            xml_path = self.root / snapshot["file"]
            root = self.parse(xml_path)
            if root is None:
                continue
            current = [
                direct_text(item, "Type")
                for item in root.iter()
                if local_name(item.tag) == snapshot["entry"]
            ]
            empty = [index + 1 for index, item in enumerate(current) if not item]
            if empty:
                self.fail(f"{snapshot['file']}: {table} entries without Type at positions {empty}")
            duplicates = sorted({item for item in current if item and current.count(item) > 1})
            if duplicates:
                self.fail(f"{snapshot['file']}: duplicate {table} types: {', '.join(duplicates)}")
            baseline = snapshot["type_order"]
            missing = [item for item in baseline if item not in current]
            if missing:
                self.fail(f"{snapshot['file']}: baseline {table} types removed: {', '.join(missing)}")
            retained = [item for item in current if item in set(baseline)]
            if retained != baseline:
                first = next(
                    (index for index, pair in enumerate(zip(retained, baseline)) if pair[0] != pair[1]),
                    min(len(retained), len(baseline)),
                )
                self.fail(
                    f"{snapshot['file']}: baseline {table} order changed near position {first + 1}"
                )

    def definitions(self) -> tuple[set[str], dict[str, list[str]]]:
        values: set[str] = set()
        locations: dict[str, list[str]] = defaultdict(list)
        for layer in self.asset_layers:
            xml_root = layer / "XML"
            if not xml_root.is_dir():
                continue
            for path in xml_root.rglob("*.xml"):
                root = self.parse(path)
                if root is None:
                    continue
                for node in root.iter():
                    if not local_name(node.tag).endswith("Info"):
                        continue
                    value = direct_text(node, "Type")
                    if value:
                        values.add(value)
                        locations[value].append(relative(path, self.root))
        return values, locations

    def validate_references(self) -> None:
        definitions, locations = self.definitions()
        prefixes = {
            value.split("_", 1)[0] + "_"
            for value in definitions
            if "_" in value and value == value.upper()
        }
        # These are identifiers defined in DLL globals rather than XML Info tables.
        hardcoded = {"COLOR_", "DIRECTION_", "PLAYER_", "TEAM_", "BARBARIAN_", "STANDARD_"}
        prefixes -= hardcoded
        selected = [
            path for path in self.xml_files
            if relative(path, self.root) in self.changed
        ]
        all_references: dict[str, set[str]] = defaultdict(set)
        for path in self.xml_files:
            root = self.parse(path)
            if root is None:
                continue
            repo_path = relative(path, self.root)
            for node in root.iter():
                value = (node.text or "").strip()
                if not list(node) and value:
                    all_references[value].add(repo_path)
        for path in selected:
            root = self.parse(path)
            if root is None:
                continue
            repo_path = relative(path, self.root)
            old_values = self.old_leaf_values(repo_path)
            old_types = self.old_info_types(repo_path)
            current_types = {
                direct_text(node, "Type")
                for node in root.iter()
                if local_name(node.tag).endswith("Info") and direct_text(node, "Type")
            }
            for value in sorted(old_types - current_types):
                if value not in definitions and value in all_references:
                    self.fail(
                        f"{repo_path}: removed InfoType {value} remains referenced by "
                        f"{next(iter(sorted(all_references[value])))}"
                    )
            for value in sorted(current_types - old_types):
                live_locations = [
                    item for item in locations[value]
                    if item.startswith(BTS_ASSETS.as_posix() + "/")
                ]
                if len(live_locations) > 1:
                    self.fail(
                        f"{repo_path}: new InfoType {value} duplicates another live BtS definition: "
                        f"{', '.join(live_locations)}"
                    )
            for node in root.iter():
                if list(node) or local_name(node.tag) in {"Type", "Tag"}:
                    continue
                value = (node.text or "").strip()
                if value in NULL_TYPES or not value or "," in value or value.startswith("TXT_KEY_"):
                    continue
                if not re.fullmatch(r"[A-Z][A-Z0-9_]+", value):
                    continue
                if (
                    any(value.startswith(prefix) for prefix in prefixes)
                    and value not in definitions
                    and value not in old_values
                ):
                    self.fail(
                        f"{relative(path, self.root)}: <{local_name(node.tag)}> references undefined InfoType {value}"
                    )

    def text_catalog(self) -> tuple[dict[str, list[tuple[Path, ET.Element]]], set[Path]]:
        catalog: dict[str, list[tuple[Path, ET.Element]]] = defaultdict(list)
        bts_text_files: set[Path] = set()
        for layer in self.asset_layers:
            text_root = layer / "XML" / "Text"
            if not text_root.is_dir():
                continue
            for path in text_root.rglob("*.xml"):
                root = self.parse(path)
                if root is None:
                    continue
                if layer == self.bts:
                    bts_text_files.add(path)
                for node in root.iter():
                    if local_name(node.tag) != "TEXT":
                        continue
                    key = direct_text(node, "Tag")
                    if key:
                        catalog[key].append((path, node))
        return catalog, bts_text_files

    def validate_localization(self) -> None:
        catalog, bts_text_files = self.text_catalog()
        # Legacy stock text contains intentional blanks and overlay duplicates. Enforce
        # strictness on touched files so the gate blocks new debt without relitigating
        # inherited content.
        selected_text = {
            path for path in bts_text_files if relative(path, self.root) in self.changed
        }
        for key, entries in sorted(catalog.items()):
            touched_entries = [(path, node) for path, node in entries if path in selected_text]
            live_entries = [(path, node) for path, node in entries if path in bts_text_files]
            if touched_entries and len(live_entries) > 1:
                places = ", ".join(relative(path, self.root) for path, _ in live_entries)
                self.fail(f"localization key {key} is duplicated in live BtS text: {places}")
            for path, node in touched_entries:
                languages = {
                    local_name(child.tag): (child.text or "")
                    for child in node
                    if local_name(child.tag) not in {"Tag", "Gender", "Plural"}
                }
                english = languages.get("English", "")
                if not english.strip():
                    self.fail(f"{relative(path, self.root)}: {key} has empty English text")
                    continue
                expected = sorted(TOKEN_RE.findall(english))
                for language, value in languages.items():
                    if not value.strip():
                        self.fail(f"{relative(path, self.root)}: {key} has empty {language} text")
                    elif sorted(TOKEN_RE.findall(value)) != expected:
                        self.fail(
                            f"{relative(path, self.root)}: {key} {language} format tokens "
                            f"{sorted(TOKEN_RE.findall(value))} differ from English {expected}"
                        )

        referenced: dict[str, set[str]] = defaultdict(set)
        for path in self.xml_files:
            root = self.parse(path)
            if root is None:
                continue
            for node in root.iter():
                if list(node):
                    continue
                value = (node.text or "").strip()
                if value.startswith("TXT_KEY_"):
                    referenced[value].add(relative(path, self.root))
        for path in self.xml_files:
            repo_path = relative(path, self.root)
            if repo_path not in self.changed:
                continue
            root = self.parse(path)
            if root is None:
                continue
            old_values = self.old_leaf_values(repo_path)
            for node in root.iter():
                if list(node):
                    continue
                key = (node.text or "").strip()
                if key.startswith("TXT_KEY_") and key not in catalog and key not in old_values:
                    self.fail(f"{repo_path}: newly referenced localization key {key} is undefined")

        # A deleted definition is also a regression even when its call sites did not change.
        for path in selected_text:
            repo_path = relative(path, self.root)
            old_keys = {item for item in self.old_leaf_values(repo_path) if item.startswith("TXT_KEY_")}
            root = self.parse(path)
            current_keys = set()
            if root is not None:
                current_keys = {
                    direct_text(node, "Tag")
                    for node in root.iter()
                    if local_name(node.tag) == "TEXT"
                }
            for key in sorted(old_keys - current_keys):
                if key in referenced and key not in catalog:
                    self.fail(
                        f"{repo_path}: removed localization key {key} is still referenced by "
                        f"{next(iter(sorted(referenced[key])))}"
                    )

    def old_leaf_values(self, repo_path: str) -> set[str]:
        proc = subprocess.run(
            ["git", "-C", str(self.root), "show", f"HEAD:{repo_path}"],
            capture_output=True,
        )
        if proc.returncode:
            return set()
        try:
            root = ET.fromstring(proc.stdout)
        except ET.ParseError:
            return set()
        return {
            (node.text or "").strip()
            for node in root.iter()
            if not list(node) and (node.text or "").strip()
        }

    def old_info_types(self, repo_path: str) -> set[str]:
        proc = subprocess.run(
            ["git", "-C", str(self.root), "show", f"HEAD:{repo_path}"],
            capture_output=True,
        )
        if proc.returncode:
            return set()
        try:
            root = ET.fromstring(proc.stdout)
        except ET.ParseError:
            return set()
        return {
            direct_text(node, "Type")
            for node in root.iter()
            if local_name(node.tag).endswith("Info") and direct_text(node, "Type")
        }

    def old_xml_art_values(self, repo_path: str) -> set[str]:
        proc = subprocess.run(
            ["git", "-C", str(self.root), "show", f"HEAD:{repo_path}"],
            capture_output=True,
        )
        if proc.returncode:
            return set()
        try:
            root = ET.fromstring(proc.stdout)
        except ET.ParseError:
            return set()
        return self.art_values(root)

    @staticmethod
    def art_values(root: ET.Element) -> set[str]:
        result: set[str] = set()
        for node in root.iter():
            if list(node):
                continue
            value = (node.text or "").strip()
            if any(ext in value.lower() for ext in ART_EXTENSIONS):
                result.add(value)
        return result

    @staticmethod
    def button_parts(value: str) -> list[str]:
        if not value.startswith(","):
            return [value]
        return [part.strip() for part in value.split(",")[1:]]

    def normalize_art(self, value: str) -> str:
        return str(PurePosixPath(value.strip().replace("\\", "/").lstrip("/")))

    def case_map(self, layer: Path) -> dict[str, Path]:
        if layer not in self._case_maps:
            result: dict[str, Path] = {}
            art = layer / "Art"
            if art.is_dir():
                for path in art.rglob("*"):
                    if path.is_file():
                        result[relative(path, layer).lower()] = path
            self._case_maps[layer] = result
        return self._case_maps[layer]

    def resolve_art(self, value: str, parent: Path | None = None) -> Path | None:
        normalized = self.normalize_art(value)
        candidates = [normalized]
        if parent is not None and not normalized.lower().startswith("art/"):
            for layer in self.asset_layers:
                try:
                    parent_rel = parent.parent.relative_to(layer)
                except ValueError:
                    continue
                candidates.insert(0, (parent_rel / normalized).as_posix())
                break
        for candidate in candidates:
            key = candidate.lower()
            for layer in self.asset_layers:
                found = self.case_map(layer).get(key)
                if found:
                    return found
        return None

    def validate_dds(self, path: Path) -> None:
        try:
            data = path.read_bytes()[:148]
        except OSError as exc:
            self.fail(f"{relative(path, self.root)}: cannot read DDS: {exc}")
            return
        if len(data) < 128 or data[:4] != b"DDS " or struct.unpack_from("<I", data, 4)[0] != 124:
            self.fail(f"{relative(path, self.root)}: invalid DDS header")
            return
        height, width = struct.unpack_from("<II", data, 12)
        if not width or not height or width & (width - 1) or height & (height - 1):
            self.fail(f"{relative(path, self.root)}: DDS dimensions must be positive powers of two; got {width}x{height}")
        pf_size, pf_flags = struct.unpack_from("<II", data, 76)
        fourcc = data[84:88]
        rgb_bits = struct.unpack_from("<I", data, 88)[0]
        if pf_size != 32:
            self.fail(f"{relative(path, self.root)}: invalid DDS pixel-format header")
        compressed = bool(pf_flags & 0x4)
        if compressed and fourcc not in {b"DXT1", b"DXT3", b"DXT5"}:
            self.fail(f"{relative(path, self.root)}: unsupported Civ4 DDS encoding {fourcc!r}")
        if not compressed and rgb_bits not in {24, 32}:
            self.fail(f"{relative(path, self.root)}: unsupported uncompressed DDS depth {rgb_bits}")

    def validate_art(self) -> None:
        changed_xml = [
            path for path in self.xml_files
            if relative(path, self.root) in self.changed
        ]
        new_values: set[str] = set()
        for path in changed_xml:
            root = self.parse(path)
            if root is None:
                continue
            repo_path = relative(path, self.root)
            current = self.art_values(root)
            new_values.update(current - self.old_xml_art_values(repo_path))
            for node in root.iter():
                if local_name(node.tag) != "Button":
                    continue
                value = (node.text or "").strip()
                if value not in current:
                    continue
                parts = self.button_parts(value)
                if value.startswith(","):
                    if len(parts) != 4 or not parts[0] or not parts[1]:
                        self.fail(f"{repo_path}: invalid atlas Button syntax {value!r}")
                        continue
                    try:
                        if int(parts[2]) < 1 or int(parts[3]) < 1:
                            raise ValueError
                    except ValueError:
                        self.fail(f"{repo_path}: atlas Button coordinates must be positive integers: {value!r}")

        targets: set[Path] = set()
        for value in sorted(new_values):
            for part in self.button_parts(value):
                if Path(part).suffix.lower() not in ART_EXTENSIONS:
                    continue
                found = self.resolve_art(part)
                if found is None:
                    self.fail(f"new art reference is missing from BtS/base/Warlords assets: {part}")
                else:
                    targets.add(found)

        for repo_path in self.changed:
            absolute = self.root / repo_path
            if absolute.is_file() and absolute.suffix.lower() in ART_EXTENSIONS:
                try:
                    absolute.relative_to(self.bts / "Art")
                    targets.add(absolute)
                except ValueError:
                    pass

        queue = list(targets)
        visited: set[Path] = set()
        while queue:
            path = queue.pop()
            if path in visited:
                continue
            visited.add(path)
            suffix = path.suffix.lower()
            if suffix == ".dds":
                self.validate_dds(path)
                continue
            if suffix not in {".nif", ".kfm", ".kf"}:
                continue
            try:
                payload = path.read_bytes()
            except OSError as exc:
                self.fail(f"{relative(path, self.root)}: cannot read model/animation: {exc}")
                continue
            if not payload:
                self.fail(f"{relative(path, self.root)}: empty model/animation file")
                continue
            for raw in EMBEDDED_ART_RE.findall(payload):
                embedded = raw.decode("latin-1").strip().replace("\\", "/")
                found = self.resolve_art(embedded, path)
                if found is None:
                    self.fail(
                        f"{relative(path, self.root)}: embedded dependency is missing: {embedded}"
                    )
                elif found not in visited:
                    queue.append(found)

    def run(self) -> int:
        if not self.bts.is_dir():
            self.fail(f"BtS assets root not found: {self.bts}")
        else:
            self.validate_baseline()
            self.validate_references()
            self.validate_localization()
            self.validate_art()
        for warning in self.warnings:
            print(f"[ROSTER][WARN] {warning}")
        if self.errors:
            print(f"[ROSTER] Validation failed with {len(self.errors)} error(s).")
            for error in self.errors:
                print(f"  [FAIL] {error}")
            return 1
        mode = "full" if self.all_files else "changed-file"
        print(f"[ROSTER] {mode} semantic, baseline, localization, and targeted-art checks passed.")
        return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--all", action="store_true", help="check duplicate/empty localization across all BtS text")
    args = parser.parse_args()
    return Validator(args.repo_root, args.all).run()


if __name__ == "__main__":
    sys.exit(main())
