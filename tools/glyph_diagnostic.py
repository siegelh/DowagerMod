#!/usr/bin/env python3
"""
Diagnose Civ4 GameFont symbol assignment and atlas-slot hazards.

This is intentionally read-only. It mirrors the high-level symbol ordering in
CvGameTextMgr::assignFontIds so glyph regressions can be measured before any
font, XML, or DLL fix is attempted.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import struct
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable
from xml.etree import ElementTree as ET


DEFAULT_PRISTINE = Path(
    r"C:\Program Files (x86)\Steam\steamapps\common"
    r"\Sid Meier's Civilization IV Beyond the Sword - PRISTINE"
)

FONT_SYMBOLS = [
    "HAPPY_CHAR",
    "UNHAPPY_CHAR",
    "HEALTHY_CHAR",
    "UNHEALTHY_CHAR",
    "BULLET_CHAR",
    "STRENGTH_CHAR",
    "MOVES_CHAR",
    "RELIGION_CHAR",
    "STAR_CHAR",
    "SILVER_STAR_CHAR",
    "TRADE_CHAR",
    "DEFENSE_CHAR",
    "GREAT_PEOPLE_CHAR",
    "BAD_GOLD_CHAR",
    "BAD_FOOD_CHAR",
    "EATEN_FOOD_CHAR",
    "GOLDEN_AGE_CHAR",
    "ANGRY_POP_CHAR",
    "OPEN_BORDERS_CHAR",
    "DEFENSIVE_PACT_CHAR",
    "MAP_CHAR",
    "OCCUPATION_CHAR",
    "POWER_CHAR",
]


@dataclass
class TgaInfo:
    path: str
    exists: bool
    size: int | None = None
    sha256: str | None = None
    width: int | None = None
    height: int | None = None
    pixel_depth: int | None = None
    image_type: int | None = None
    descriptor: int | None = None


@dataclass
class SlotOccupancy:
    slot_index: int
    column: int
    row: int
    x0: int
    y0: int
    x1: int
    y1: int
    non_background_pixels: int
    total_pixels: int
    ratio: float


@dataclass
class SymbolRow:
    family: str
    type: str
    char_code: int
    slot_index: int
    xml_index: int | None = None
    art_define: str | None = None
    font_button_index: int | None = None
    notes: str = ""


@dataclass
class Issue:
    severity: str
    code: str
    message: str
    symbols: list[str]


@dataclass
class AllocationSummary:
    bonus_count: int
    non_art_slot_consuming_bonus_count: int
    art_masterpiece_bonus_count: int
    distinct_bonus_char_count: int
    duplicate_bonus_char_groups: int
    duplicate_bonus_font_index_groups: int
    bonus_base_id: int | None
    first_generic_symbol_id: int | None
    expected_default_first_generic_symbol_id: int
    generic_symbol_start_matches_default: bool | None
    non_art_bonus_count_to_next_padding_boundary: int
    generic_shift_risk: str


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Report Civ4 GameFont assignment, TGA metadata, and likely glyph hazards."
    )
    parser.add_argument("--repo-root", type=Path, default=repo_root_from_script())
    parser.add_argument("--pristine-root", type=Path, default=DEFAULT_PRISTINE)
    parser.add_argument(
        "--first-symbol-code",
        type=int,
        default=8483,
        help="Symbol code passed by the exe to CvGameTextMgr::assignFontIds. Default is a Civ4 BTS convention.",
    )
    parser.add_argument(
        "--pad-amount",
        type=int,
        default=25,
        help="Row padding value passed by the exe to CvGameTextMgr::assignFontIds.",
    )
    parser.add_argument(
        "--slot-count",
        type=int,
        default=512,
        help="Conservative expected GameFont slot capacity used for static range checks.",
    )
    parser.add_argument(
        "--atlas-columns",
        type=int,
        default=25,
        help="Columns to use when --sample-atlas is enabled.",
    )
    parser.add_argument(
        "--empty-threshold",
        type=float,
        default=0.002,
        help="Cell non-background ratio at or below this value is treated as empty.",
    )
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--csv-out", type=Path)
    parser.add_argument(
        "--sample-atlas",
        action="store_true",
        help="Experimentally sample atlas cell occupancy. Off by default because Civ4 GameFont layout needs calibration.",
    )
    parser.add_argument(
        "--fail-on-error",
        action="store_true",
        help="Return a non-zero exit code if any error-severity issue is found.",
    )
    return parser.parse_args()


def bts_assets(repo_root: Path) -> Path:
    return repo_root / "CoreFiles" / "Sid Meier's Civilization IV Beyond the Sword" / "Beyond the Sword" / "Assets"


def base_assets(repo_root: Path) -> Path:
    return repo_root / "CoreFiles" / "Sid Meier's Civilization IV Beyond the Sword" / "Assets"


def find_xml(repo_root: Path, relative: str) -> Path:
    bts_path = bts_assets(repo_root) / "XML" / relative
    if bts_path.exists():
        return bts_path
    base_path = base_assets(repo_root) / "XML" / relative
    if base_path.exists():
        return base_path
    raise FileNotFoundError(f"Could not find XML file in BtS or base assets: {relative}")


def child_text(node: ET.Element, tag: str, default: str = "") -> str:
    child = next((candidate for candidate in node if local_name(candidate.tag) == tag), None)
    return default if child is None or child.text is None else child.text.strip()


def local_name(tag: str) -> str:
    if "}" in tag:
        return tag.rsplit("}", 1)[1]
    return tag


def iter_local(root: ET.Element, tag: str) -> Iterable[ET.Element]:
    for node in root.iter():
        if local_name(node.tag) == tag:
            yield node


def load_info_types(path: Path, item_tag: str) -> list[str]:
    root = ET.parse(path).getroot()
    return [child_text(item, "Type") for item in iter_local(root, item_tag) if child_text(item, "Type")]


def load_bonus_infos(path: Path) -> list[dict[str, str]]:
    root = ET.parse(path).getroot()
    rows: list[dict[str, str]] = []
    for item in iter_local(root, "BonusInfo"):
        bonus_type = child_text(item, "Type")
        if not bonus_type:
            continue
        rows.append(
            {
                "type": bonus_type,
                "art_define": child_text(item, "ArtDefineTag"),
            }
        )
    return rows


def load_bonus_art(path: Path) -> dict[str, int]:
    root = ET.parse(path).getroot()
    result: dict[str, int] = {}
    for item in iter_local(root, "BonusArtInfo"):
        art_type = child_text(item, "Type")
        if not art_type:
            continue
        raw_index = child_text(item, "FontButtonIndex")
        try:
            result[art_type] = int(raw_index)
        except ValueError:
            result[art_type] = -1
    return result


def pad_to_next(current: int, pad_amount: int) -> int:
    current += 1
    while current % pad_amount != 0:
        current += 1
    return current


def assign_symbols(
    yields: list[str],
    commerces: list[str],
    religions: list[str],
    corporations: list[str],
    bonuses: list[dict[str, str]],
    bonus_art: dict[str, int],
    first_symbol_code: int,
    pad_amount: int,
) -> list[SymbolRow]:
    rows: list[SymbolRow] = []
    current = first_symbol_code

    def add(family: str, type_id: str, code: int, index: int | None = None, **extra: object) -> None:
        rows.append(
            SymbolRow(
                family=family,
                type=type_id,
                char_code=code,
                slot_index=code - first_symbol_code,
                xml_index=index,
                art_define=extra.get("art_define") if isinstance(extra.get("art_define"), str) else None,
                font_button_index=extra.get("font_button_index") if isinstance(extra.get("font_button_index"), int) else None,
                notes=extra.get("notes") if isinstance(extra.get("notes"), str) else "",
            )
        )

    for index, type_id in enumerate(yields):
        add("yield", type_id, current, index)
        current += 1

    current = pad_to_next(current, pad_amount)

    for index, type_id in enumerate(commerces):
        add("commerce", type_id, current, index)
        current += 1

    current = pad_to_next(current, pad_amount)
    if len(commerces) < pad_amount:
        current = pad_to_next(current, pad_amount)

    for index, type_id in enumerate(religions):
        add("religion", type_id, current, index)
        current += 1
        add("holy_city_religion", f"{type_id}_HOLY_CITY", current, index)
        current += 1

    for index, type_id in enumerate(corporations):
        add("corporation", type_id, current, index)
        current += 1
        add("corporation_headquarters", f"{type_id}_HEADQUARTERS", current, index)
        current += 1

    current = pad_to_next(current, pad_amount)
    if 2 * (len(religions) + len(corporations)) < pad_amount:
        current = pad_to_next(current, pad_amount)

    bonus_base = current
    current += 1
    for index, bonus in enumerate(bonuses):
        type_id = bonus["type"]
        art_define = bonus["art_define"]
        font_index = bonus_art.get(art_define, -1)
        notes = ""
        char_code = bonus_base + font_index
        if type_id.startswith("BONUS_ART_"):
            char_code = bonus_base + 5
            notes = "BONUS_ART_* forced to bonusBaseID + 5 by DLL"
        add(
            "bonus",
            type_id,
            char_code,
            index,
            art_define=art_define,
            font_button_index=font_index,
            notes=notes,
        )
        if not type_id.startswith("BONUS_ART_"):
            current += 1

    current = pad_to_next(current, pad_amount)
    if len(bonuses) < pad_amount:
        current = pad_to_next(current, pad_amount)
    if len(bonuses) < 2 * pad_amount:
        current = pad_to_next(current, pad_amount)

    for index, symbol in enumerate(FONT_SYMBOLS):
        add("font_symbol", symbol, current, index)
        current += 1

    return rows


def read_tga_info(path: Path) -> TgaInfo:
    if not path.exists():
        return TgaInfo(path=str(path), exists=False)
    data = path.read_bytes()
    width = height = pixel_depth = image_type = descriptor = None
    if len(data) >= 18:
        image_type = data[2]
        width = struct.unpack_from("<H", data, 12)[0]
        height = struct.unpack_from("<H", data, 14)[0]
        pixel_depth = data[16]
        descriptor = data[17]
    return TgaInfo(
        path=str(path),
        exists=True,
        size=len(data),
        sha256=hashlib.sha256(data).hexdigest(),
        width=width,
        height=height,
        pixel_depth=pixel_depth,
        image_type=image_type,
        descriptor=descriptor,
    )


def read_tga_pixels(path: Path) -> tuple[int, int, list[tuple[int, int, int, int]]]:
    data = path.read_bytes()
    if len(data) < 18:
        raise ValueError(f"Not enough data for TGA header: {path}")
    image_id_len = data[0]
    color_map_type = data[1]
    image_type = data[2]
    width = struct.unpack_from("<H", data, 12)[0]
    height = struct.unpack_from("<H", data, 14)[0]
    pixel_depth = data[16]
    descriptor = data[17]
    if color_map_type != 0:
        raise ValueError(f"Color-mapped TGA is not supported: {path}")
    if image_type != 2:
        raise ValueError(f"Only uncompressed true-color TGA is supported, got type {image_type}: {path}")
    if pixel_depth not in (24, 32):
        raise ValueError(f"Only 24/32-bit TGA is supported, got {pixel_depth}: {path}")

    bytes_per_pixel = pixel_depth // 8
    offset = 18 + image_id_len
    expected = width * height * bytes_per_pixel
    pixel_data = data[offset : offset + expected]
    if len(pixel_data) < expected:
        raise ValueError(f"TGA pixel data is truncated: {path}")

    origin_top = bool(descriptor & 0x20)
    pixels: list[tuple[int, int, int, int]] = [(0, 0, 0, 0)] * (width * height)
    for source_y in range(height):
        y = source_y if origin_top else (height - 1 - source_y)
        for x in range(width):
            i = (source_y * width + x) * bytes_per_pixel
            b = pixel_data[i]
            g = pixel_data[i + 1]
            r = pixel_data[i + 2]
            a = pixel_data[i + 3] if bytes_per_pixel == 4 else 255
            pixels[y * width + x] = (r, g, b, a)
    return width, height, pixels


def is_background_pixel(pixel: tuple[int, int, int, int]) -> bool:
    r, g, b, a = pixel
    # Civ4 GameFont TGAs use transparent white/magenta backgrounds, while many
    # real glyph pixels also have alpha 0. Classify by color first, not alpha.
    if r >= 248 and g >= 248 and b >= 248:
        return True
    if r >= 248 and b >= 248 and g <= 8:
        return True
    if a <= 8 and r <= 4 and g <= 4 and b <= 4:
        return True
    return False


def sample_slot_occupancy(
    path: Path,
    slot_indices: Iterable[int],
    columns: int,
    slot_count: int,
) -> dict[int, SlotOccupancy]:
    width, height, pixels = read_tga_pixels(path)
    rows = max(1, math.ceil(slot_count / columns))
    result: dict[int, SlotOccupancy] = {}
    for slot_index in sorted(set(slot_indices)):
        if slot_index < 0:
            continue
        row = slot_index // columns
        column = slot_index % columns
        if row >= rows:
            continue
        x0 = math.floor(column * width / columns)
        x1 = math.floor((column + 1) * width / columns)
        y0 = math.floor(row * height / rows)
        y1 = math.floor((row + 1) * height / rows)
        total = max(0, x1 - x0) * max(0, y1 - y0)
        non_background = 0
        for y in range(y0, y1):
            for x in range(x0, x1):
                if not is_background_pixel(pixels[y * width + x]):
                    non_background += 1
        ratio = (non_background / total) if total else 0.0
        result[slot_index] = SlotOccupancy(
            slot_index=slot_index,
            column=column,
            row=row,
            x0=x0,
            y0=y0,
            x1=x1,
            y1=y1,
            non_background_pixels=non_background,
            total_pixels=total,
            ratio=ratio,
        )
    return result


def compare_files(path_a: Path, path_b: Path) -> bool | None:
    if not path_a.exists() or not path_b.exists():
        return None
    return path_a.read_bytes() == path_b.read_bytes()


def build_issues(rows: list[SymbolRow], slot_count: int) -> list[Issue]:
    issues: list[Issue] = []

    by_code: dict[int, list[SymbolRow]] = {}
    for row in rows:
        by_code.setdefault(row.char_code, []).append(row)
    for code, same_code in sorted(by_code.items()):
        if len(same_code) > 1:
            all_art = all(row.type.startswith("BONUS_ART_") for row in same_code)
            severity = "info" if all_art else "warning"
            issues.append(
                Issue(
                    severity=severity,
                    code="duplicate-char-code",
                    message=f"Character code {code} is assigned to {len(same_code)} symbols.",
                    symbols=[row.type for row in same_code],
                )
            )

    for row in rows:
        if row.slot_index < 0 or row.slot_index >= slot_count:
            issues.append(
                Issue(
                    severity="warning",
                    code="slot-out-of-range",
                    message=f"{row.type} maps to slot {row.slot_index}, outside configured slot count {slot_count}.",
                    symbols=[row.type],
                )
            )
        if row.family == "bonus" and row.font_button_index is not None and row.font_button_index < 0:
            issues.append(
                Issue(
                    severity="error",
                    code="missing-font-button-index",
                    message=f"{row.type} has art define {row.art_define} with no valid FontButtonIndex.",
                    symbols=[row.type],
                )
            )

    by_font_index: dict[int, list[SymbolRow]] = {}
    for row in rows:
        if row.family == "bonus" and row.font_button_index is not None and row.font_button_index >= 0:
            by_font_index.setdefault(row.font_button_index, []).append(row)
    for font_index, same_index in sorted(by_font_index.items()):
        non_art = [row for row in same_index if not row.type.startswith("BONUS_ART_")]
        if len(non_art) > 1:
            issues.append(
                Issue(
                    severity="warning",
                    code="duplicate-bonus-font-index",
                    message=f"FontButtonIndex {font_index} is shared by {len(non_art)} non-art bonuses.",
                    symbols=[row.type for row in non_art],
                )
            )

    return issues


def build_allocation_summary(rows: list[SymbolRow], pad_amount: int) -> AllocationSummary:
    bonus_rows = [row for row in rows if row.family == "bonus"]
    font_symbol_rows = [row for row in rows if row.family == "font_symbol"]
    non_art = [row for row in bonus_rows if not row.type.startswith("BONUS_ART_")]
    art = [row for row in bonus_rows if row.type.startswith("BONUS_ART_")]
    bonus_base = min((row.char_code - (row.font_button_index or 0) for row in non_art if row.font_button_index is not None), default=None)
    first_generic = min((row.char_code for row in font_symbol_rows), default=None)
    by_char: dict[int, int] = {}
    by_font_index: dict[int, int] = {}
    for row in bonus_rows:
        by_char[row.char_code] = by_char.get(row.char_code, 0) + 1
        if row.font_button_index is not None:
            by_font_index[row.font_button_index] = by_font_index.get(row.font_button_index, 0) + 1
    distance = 0
    if bonus_base is not None:
        cursor_after_non_art = bonus_base + 1 + len(non_art)
        boundary = cursor_after_non_art
        while boundary % pad_amount != 0:
            boundary += 1
        distance = max(0, boundary - cursor_after_non_art)
    remainder = len(non_art) % pad_amount
    risk = "near_padding_boundary" if remainder >= 20 else "normal"
    expected_default = 8675
    return AllocationSummary(
        bonus_count=len(bonus_rows),
        non_art_slot_consuming_bonus_count=len(non_art),
        art_masterpiece_bonus_count=len(art),
        distinct_bonus_char_count=len(by_char),
        duplicate_bonus_char_groups=sum(1 for count in by_char.values() if count > 1),
        duplicate_bonus_font_index_groups=sum(1 for count in by_font_index.values() if count > 1),
        bonus_base_id=bonus_base,
        first_generic_symbol_id=first_generic,
        expected_default_first_generic_symbol_id=expected_default,
        generic_symbol_start_matches_default=(first_generic == expected_default) if first_generic is not None else None,
        non_art_bonus_count_to_next_padding_boundary=distance,
        generic_shift_risk=risk,
    )


def add_allocation_issues(issues: list[Issue], allocation: AllocationSummary) -> None:
    if allocation.generic_symbol_start_matches_default is False:
        issues.append(
            Issue(
                severity="warning",
                code="generic-symbol-start-shifted",
                message=(
                    f"First generic FontSymbols ID is {allocation.first_generic_symbol_id}, "
                    f"expected {allocation.expected_default_first_generic_symbol_id} for the current BtS-compatible layout."
                ),
                symbols=["FONT_SYMBOLS"],
            )
        )
    if allocation.generic_shift_risk != "normal":
        issues.append(
            Issue(
                severity="warning",
                code="non-art-bonus-padding-boundary-risk",
                message=(
                    "Non-art slot-consuming bonus count is close to a padding boundary; "
                    "additional non-art bonuses may shift generic FontSymbols."
                ),
                symbols=["BONUS"],
            )
        )


def add_occupancy_issues(
    issues: list[Issue],
    rows: list[SymbolRow],
    repo_occupancy: dict[int, SlotOccupancy],
    repo_75_occupancy: dict[int, SlotOccupancy],
    pristine_occupancy: dict[int, SlotOccupancy],
    pristine_75_occupancy: dict[int, SlotOccupancy],
    empty_threshold: float,
) -> None:
    by_slot: dict[int, list[SymbolRow]] = {}
    for row in rows:
        by_slot.setdefault(row.slot_index, []).append(row)

    for slot_index, slot_rows in sorted(by_slot.items()):
        repo = repo_occupancy.get(slot_index)
        repo_75 = repo_75_occupancy.get(slot_index)
        pristine = pristine_occupancy.get(slot_index)
        pristine_75 = pristine_75_occupancy.get(slot_index)
        symbols = [row.type for row in slot_rows]

        if repo and repo.ratio <= empty_threshold:
            severity = "error" if any(row.family != "bonus" or not row.type.startswith("BONUS_ART_") for row in slot_rows) else "warning"
            issues.append(
                Issue(
                    severity=severity,
                    code="repo-empty-assigned-slot",
                    message=f"Repo GameFont slot {slot_index} appears empty for {len(slot_rows)} assigned symbol(s).",
                    symbols=symbols,
                )
            )
        if repo_75 and repo_75.ratio <= empty_threshold:
            severity = "error" if any(row.family != "bonus" or not row.type.startswith("BONUS_ART_") for row in slot_rows) else "warning"
            issues.append(
                Issue(
                    severity=severity,
                    code="repo-75-empty-assigned-slot",
                    message=f"Repo GameFont_75 slot {slot_index} appears empty for {len(slot_rows)} assigned symbol(s).",
                    symbols=symbols,
                )
            )
        if repo and pristine and repo.ratio <= empty_threshold < pristine.ratio:
            issues.append(
                Issue(
                    severity="warning",
                    code="repo-empty-pristine-filled",
                    message=f"Repo GameFont slot {slot_index} appears empty while pristine is occupied.",
                    symbols=symbols,
                )
            )
        if repo_75 and pristine_75 and repo_75.ratio <= empty_threshold < pristine_75.ratio:
            issues.append(
                Issue(
                    severity="warning",
                    code="repo-75-empty-pristine-filled",
                    message=f"Repo GameFont_75 slot {slot_index} appears empty while pristine is occupied.",
                    symbols=symbols,
                )
            )


def write_csv(path: Path, rows: Iterable[SymbolRow]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(next(iter([SymbolRow('', '', 0, 0)]))).keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    assets = bts_assets(repo_root)
    pristine_assets = args.pristine_root / "Beyond the Sword" / "Assets"

    yields = load_info_types(find_xml(repo_root, r"Terrain\CIV4YieldInfos.xml"), "YieldInfo")
    commerces = load_info_types(find_xml(repo_root, r"GameInfo\CIV4CommerceInfo.xml"), "CommerceInfo")
    religions = load_info_types(find_xml(repo_root, r"GameInfo\CIV4ReligionInfo.xml"), "ReligionInfo")
    corporations = load_info_types(find_xml(repo_root, r"GameInfo\CIV4CorporationInfo.xml"), "CorporationInfo")
    bonuses = load_bonus_infos(find_xml(repo_root, r"Terrain\CIV4BonusInfos.xml"))
    bonus_art = load_bonus_art(find_xml(repo_root, r"Art\CIV4ArtDefines_Bonus.xml"))

    rows = assign_symbols(
        yields,
        commerces,
        religions,
        corporations,
        bonuses,
        bonus_art,
        args.first_symbol_code,
        args.pad_amount,
    )
    allocation = build_allocation_summary(rows, args.pad_amount)
    issues = build_issues(rows, args.slot_count)
    add_allocation_issues(issues, allocation)

    repo_font = assets / "res" / "Fonts" / "GameFont.tga"
    repo_font_75 = assets / "res" / "Fonts" / "GameFont_75.tga"
    pristine_font = pristine_assets / "res" / "Fonts" / "GameFont.tga"
    pristine_font_75 = pristine_assets / "res" / "Fonts" / "GameFont_75.tga"
    tga_infos = {
        "repo_GameFont": read_tga_info(repo_font),
        "repo_GameFont_75": read_tga_info(repo_font_75),
        "pristine_GameFont": read_tga_info(pristine_font),
        "pristine_GameFont_75": read_tga_info(pristine_font_75),
    }

    assigned_slots = [row.slot_index for row in rows]
    occupancy: dict[str, dict[int, SlotOccupancy]] = {}
    if args.sample_atlas:
        try:
            occupancy["repo_GameFont"] = sample_slot_occupancy(repo_font, assigned_slots, args.atlas_columns, args.slot_count)
            occupancy["repo_GameFont_75"] = sample_slot_occupancy(repo_font_75, assigned_slots, args.atlas_columns, args.slot_count)
            occupancy["pristine_GameFont"] = sample_slot_occupancy(pristine_font, assigned_slots, args.atlas_columns, args.slot_count)
            occupancy["pristine_GameFont_75"] = sample_slot_occupancy(pristine_font_75, assigned_slots, args.atlas_columns, args.slot_count)
            add_occupancy_issues(
                issues,
                rows,
                occupancy["repo_GameFont"],
                occupancy["repo_GameFont_75"],
                occupancy["pristine_GameFont"],
                occupancy["pristine_GameFont_75"],
                args.empty_threshold,
            )
        except (OSError, ValueError) as exc:
            issues.append(
                Issue(
                    severity="warning",
                    code="occupancy-sampling-failed",
                    message=str(exc),
                    symbols=[],
                )
            )

    summary = {
        "repo_root": str(repo_root),
        "pristine_root": str(args.pristine_root),
        "first_symbol_code": args.first_symbol_code,
        "pad_amount": args.pad_amount,
        "slot_count": args.slot_count,
        "atlas_columns": args.atlas_columns,
        "sample_atlas": args.sample_atlas,
        "empty_threshold": args.empty_threshold,
        "counts": {
            "yields": len(yields),
            "commerces": len(commerces),
            "religions": len(religions),
            "corporations": len(corporations),
            "bonuses": len(bonuses),
            "font_symbols": len(FONT_SYMBOLS),
            "assigned_symbols": len(rows),
            "issues": len(issues),
        },
        "allocation": asdict(allocation),
        "tga": {name: asdict(info) for name, info in tga_infos.items()},
        "font_file_matches_pristine": {
            "GameFont": compare_files(repo_font, pristine_font),
            "GameFont_75": compare_files(repo_font_75, pristine_font_75),
        },
        "issues": [asdict(issue) for issue in issues],
        "symbols": [asdict(row) for row in rows],
        "occupancy": {
            name: {str(slot): asdict(value) for slot, value in slots.items()}
            for name, slots in occupancy.items()
        },
    }

    if args.csv_out:
        write_csv(args.csv_out, rows)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("Glyph diagnostic summary")
    print("========================")
    print(f"repo: {repo_root}")
    print(f"pristine: {args.pristine_root}")
    print(
        f"first_symbol_code={args.first_symbol_code} pad_amount={args.pad_amount} "
        f"atlas_columns={args.atlas_columns} sample_atlas={args.sample_atlas}"
    )
    print(
        "counts: "
        f"yields={len(yields)}, commerces={len(commerces)}, religions={len(religions)}, "
        f"corporations={len(corporations)}, bonuses={len(bonuses)}, assigned={len(rows)}"
    )
    print(
        "allocation: "
        f"bonus_base_id={allocation.bonus_base_id}, "
        f"non_art_slot_consuming_bonuses={allocation.non_art_slot_consuming_bonus_count}, "
        f"art_masterpiece_bonuses={allocation.art_masterpiece_bonus_count}, "
        f"first_generic_symbol_id={allocation.first_generic_symbol_id}, "
        f"generic_start_matches_default={allocation.generic_symbol_start_matches_default}, "
        f"boundary_distance={allocation.non_art_bonus_count_to_next_padding_boundary}, "
        f"risk={allocation.generic_shift_risk}"
    )
    for name, info in tga_infos.items():
        print(
            f"{name}: exists={info.exists} size={info.size} "
            f"dimensions={info.width}x{info.height} depth={info.pixel_depth} type={info.image_type}"
        )
    print(
        "font file matches pristine: "
        f"GameFont={summary['font_file_matches_pristine']['GameFont']}, "
        f"GameFont_75={summary['font_file_matches_pristine']['GameFont_75']}"
    )

    by_severity: dict[str, int] = {}
    for issue in issues:
        by_severity[issue.severity] = by_severity.get(issue.severity, 0) + 1
    print(f"issues: {by_severity or {}}")
    for issue in issues[:25]:
        print(f"[{issue.severity}] {issue.code}: {issue.message} {'; '.join(issue.symbols[:8])}")
    if len(issues) > 25:
        print(f"... {len(issues) - 25} more issues omitted; use --json-out for full details.")

    return 1 if args.fail_on_error and any(issue.severity == "error" for issue in issues) else 0


if __name__ == "__main__":
    sys.exit(main())
