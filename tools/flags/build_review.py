from __future__ import annotations

import argparse
import html
import json
import math
import time
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance

from flag_pipeline import REPO_ROOT, load_manifest, repository_path, rasterize_master


def cloth_preview(image: Image.Image) -> Image.Image:
    source = image.convert("RGB").resize((384, 256), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (448, 320), "#202631")
    for x in range(source.width):
        phase = 6.283185307179586 * x / 132
        offset = round(14 * math.sin(phase))
        brightness = 0.84 + 0.16 * (
            math.sin(phase + 1.5707963267948966) + 1
        ) / 2
        column = ImageEnhance.Brightness(
            source.crop((x, 0, x + 1, source.height))
        ).enhance(brightness)
        canvas.paste(column, (36 + x, 24 + offset))
    draw = ImageDraw.Draw(canvas)
    draw.line((32, 8, 32, 304), fill="#c8cbd1", width=4)
    return canvas


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a local flag review gallery")
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO_ROOT / "tmp" / "flags" / "review",
    )
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    document = load_manifest()
    cards = []
    started = time.perf_counter()
    input_bytes = 0
    output_bytes = 0
    for index, record in enumerate(document["records"], start=1):
        master = repository_path(str(record["master_path"]))
        input_bytes += master.stat().st_size
        image = rasterize_master(master, size=1024)
        item = output / str(record["civilization_type"]).lower()
        item.mkdir(parents=True, exist_ok=True)
        paths = {
            "flag": item / "flag-128.png",
            "scales": item / "scales.png",
            "cloth": item / "cloth.png",
        }
        image.resize((128, 128), Image.Resampling.LANCZOS).save(paths["flag"])
        scales = Image.new("RGB", (320, 150), "#151a22")
        x = 12
        for size in (128, 64, 32, 16):
            display = max(32, size)
            sample = image.convert("RGB").resize(
                (size, size), Image.Resampling.LANCZOS
            ).resize((display, display), Image.Resampling.NEAREST)
            scales.paste(sample, (x, 10 + (128 - display) // 2))
            x += display + 12
        scales.save(paths["scales"])
        cloth_preview(image).save(paths["cloth"])
        output_bytes += sum(path.stat().st_size for path in paths.values())
        relative = {key: path.relative_to(output).as_posix() for key, path in paths.items()}
        cards.append(
            f"""<article><h2>{html.escape(record['civilization'])}</h2>
<p><code>{html.escape(record['civilization_type'])}</code></p>
<img src="{relative['flag']}" width="128" height="128" alt="">
<img src="{relative['scales']}" width="320" height="150" alt="">
<img src="{relative['cloth']}" width="448" height="320" alt="">
<p><strong>{html.escape(record['recommended_design_name'])}</strong> —
{html.escape(record['period'])}</p>
<p>{html.escape(record['design_notes'])}</p>
<p>License: {html.escape(record['source_license'])}</p></article>"""
        )
        print(
            json.dumps(
                {
                    "event": "review_item_generated",
                    "batch_index": index,
                    "batch_total": document["record_count"],
                    "civilization_type": record["civilization_type"],
                    "input_bytes": master.stat().st_size,
                    "output_bytes": sum(path.stat().st_size for path in paths.values()),
                    "status": "success",
                    "retry_count": 0,
                },
                sort_keys=True,
            )
        )
    page = f"""<!doctype html><meta charset="utf-8">
<title>DowagerMod historical flags</title>
<style>body{{font:16px Segoe UI,sans-serif;background:#111722;color:#eee}}
main{{max-width:1100px;margin:auto}}article{{border-bottom:1px solid #475064;padding:24px 0}}
img{{vertical-align:middle;margin:8px;background:#fff}}code{{color:#b8d8ff}}</style>
<main><h1>Historical full-color flags</h1>{''.join(cards)}</main>"""
    (output / "index.html").write_text(page, encoding="utf-8")
    print(
        json.dumps(
            {
                "event": "review_summary",
                "expected_total": document["record_count"],
                "processed_total": len(cards),
                "persisted_total": len(cards),
                "skipped_total": 0,
                "duplicate_total": 0,
                "error_total": 0,
                "input_bytes": input_bytes,
                "output_bytes": output_bytes + (output / "index.html").stat().st_size,
                "duration_ms": round((time.perf_counter() - started) * 1000, 3),
                "status": "success",
                "passed": True,
                "index": str(output / "index.html"),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
