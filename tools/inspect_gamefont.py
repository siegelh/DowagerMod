"""Inspect Civ4 GameFont.tga / GameFont_75.tga atlas integrity.

Civ4 BtS GameFont layout (verified empirically):
- GameFont.tga:    640x320, 32 cols x 16 rows = 512 cells, each 20x20
- GameFont_75.tga: 512x256, 32 cols x 16 rows = 512 cells, each 16x16

FontButtonIndex N in CIV4ArtDefines_Bonus.xml selects cell N in
row-major order across that grid (depending on pipeline).

This script:
1. Loads each atlas and lays it out as the 32x16 grid.
2. For each cell, reports % of pixels with alpha > 0 ("non-empty").
3. Flags any cell below a threshold (default 1%) as suspect-empty.
4. Renders a contact sheet PNG with cell index labels overlaid for
   visual inspection.
5. Cross-references against the unique FontButtonIndex set extracted
   from CIV4ArtDefines_Bonus.xml.

Run from repo root:
    python tools\inspect_gamefont.py

Outputs land in tmp\gamefont_inspect\ (gitignored area).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


REPO_ROOT = Path(__file__).resolve().parent.parent
BTS_ROOT = REPO_ROOT / "CoreFiles" / "Sid Meier's Civilization IV Beyond the Sword" / "Beyond the Sword" / "Assets"
BASE_ROOT = REPO_ROOT / "CoreFiles" / "Sid Meier's Civilization IV Beyond the Sword" / "Assets"
OUT_DIR = REPO_ROOT / "tmp" / "gamefont_inspect"

GRID_COLS = 32
GRID_ROWS = 16
EMPTY_THRESHOLD = 0.01  # cell is "suspect-empty" if <1% pixels have alpha>0


def analyze_atlas(tga_path: Path, label: str) -> dict:
    img = Image.open(tga_path).convert("RGBA")
    w, h = img.size
    cell_w = w // GRID_COLS
    cell_h = h // GRID_ROWS
    cells = []
    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            box = (c * cell_w, r * cell_h, (c + 1) * cell_w, (r + 1) * cell_h)
            cell = img.crop(box)
            alpha = cell.getchannel("A")
            total = alpha.size[0] * alpha.size[1]
            non_empty = sum(1 for p in alpha.getdata() if p > 0)
            ratio = non_empty / total if total else 0.0
            cells.append({
                "index": r * GRID_COLS + c,
                "row": r,
                "col": c,
                "alpha_ratio": round(ratio, 4),
                "suspect_empty": ratio < EMPTY_THRESHOLD,
            })
    return {
        "label": label,
        "path": str(tga_path),
        "size": [w, h],
        "cell": [cell_w, cell_h],
        "cells": cells,
    }


def render_contact_sheet(tga_path: Path, out_path: Path, max_index: int = 64) -> None:
    img = Image.open(tga_path).convert("RGBA")
    w, h = img.size
    cell_w = w // GRID_COLS
    cell_h = h // GRID_ROWS

    scale = 4
    sheet_w = w * scale
    sheet_h = h * scale
    sheet = Image.new("RGBA", (sheet_w, sheet_h), (40, 40, 40, 255))
    sheet.paste(img.resize((sheet_w, sheet_h), Image.NEAREST), (0, 0))

    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("arial.ttf", 11)
    except OSError:
        font = ImageFont.load_default()
    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            idx = r * GRID_COLS + c
            if idx > max_index:
                break
            x = c * cell_w * scale
            y = r * cell_h * scale
            draw.rectangle([x, y, x + cell_w * scale - 1, y + cell_h * scale - 1],
                           outline=(255, 255, 0, 180), width=1)
            draw.text((x + 2, y + 2), str(idx), fill=(255, 255, 0, 255), font=font)
    sheet.save(out_path)


def collect_used_indices(art_xml: Path) -> set[int]:
    text = art_xml.read_text(encoding="utf-8", errors="replace")
    return set(int(m) for m in re.findall(r"<FontButtonIndex>(\d+)</FontButtonIndex>", text))


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    targets = [
        ("bts_gamefont", BTS_ROOT / "res" / "Fonts" / "GameFont.tga"),
        ("bts_gamefont_75", BTS_ROOT / "res" / "Fonts" / "GameFont_75.tga"),
        ("base_gamefont", BASE_ROOT / "res" / "Fonts" / "GameFont.tga"),
        ("base_gamefont_75", BASE_ROOT / "res" / "Fonts" / "GameFont_75.tga"),
    ]

    art_xml = BTS_ROOT / "XML" / "Art" / "CIV4ArtDefines_Bonus.xml"
    used_indices = collect_used_indices(art_xml)
    print(f"[xml] CIV4ArtDefines_Bonus.xml uses {len(used_indices)} unique FontButtonIndex values: "
          f"{sorted(used_indices)}")

    summary = {"used_indices": sorted(used_indices), "atlases": []}

    for label, path in targets:
        if not path.exists():
            print(f"[skip] {label}: not found at {path}")
            continue
        print(f"\n=== {label} ({path.name}) ===")
        report = analyze_atlas(path, label)
        size = report["size"]
        suspect = [c for c in report["cells"] if c["suspect_empty"] and c["index"] in used_indices]
        report["xml_referenced_empty"] = sorted(c["index"] for c in suspect)
        print(f"  size={size}, cell={report['cell']}")
        print(f"  XML-referenced slots that are blank in this atlas: {report['xml_referenced_empty']}")

        # Show alpha ratios for slots 0..63 for visual debugging
        first_64 = [c for c in report["cells"] if c["index"] < 64]
        for c in first_64:
            mark = " <-- BLANK" if c["suspect_empty"] else ""
            ref = " (XML-ref)" if c["index"] in used_indices else ""
            print(f"    slot {c['index']:3d}: alpha={c['alpha_ratio']:.3f}{ref}{mark}")

        contact = OUT_DIR / f"{label}_contact.png"
        render_contact_sheet(path, contact, max_index=63)
        print(f"  contact sheet: {contact}")

        summary["atlases"].append(report)

    (OUT_DIR / "report.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"\nFull report: {OUT_DIR / 'report.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
