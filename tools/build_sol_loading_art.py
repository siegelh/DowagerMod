from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ART = (
    ROOT
    / "CoreFiles"
    / "Sid Meier's Civilization IV Beyond the Sword"
    / "Beyond the Sword"
    / "Assets"
    / "Art"
    / "Interface"
    / "Screens"
    / "Loading"
)
FONT_ROOT = Path(r"C:\Windows\Fonts")
FONT_BOLD = FONT_ROOT / "constanb.ttf"
FONT_REGULAR = FONT_ROOT / "constan.ttf"

GOLD = (224, 184, 91, 255)
LIGHT_GOLD = (247, 224, 157, 255)
DARK_GOLD = (115, 72, 20, 255)
INK = (24, 18, 14, 218)


def centered_text(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    text: str,
    font: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int, int],
    stroke_width: int = 0,
    stroke_fill: tuple[int, int, int, int] | None = None,
) -> None:
    left, top, right, bottom = box
    bounds = draw.textbbox((0, 0), text, font=font, stroke_width=stroke_width)
    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]
    x = left + (right - left - width) / 2
    y = top + (bottom - top - height) / 2 - bounds[1]
    draw.text(
        (x, y),
        text,
        font=font,
        fill=fill,
        stroke_width=stroke_width,
        stroke_fill=stroke_fill,
    )


def draw_sol_badge(
    layer: Image.Image,
    center: tuple[int, int],
    radius: int,
) -> None:
    draw = ImageDraw.Draw(layer)
    cx, cy = center
    for index in range(24):
        radians = math.radians(index * 15)
        inner = radius + (5 if index % 2 else 2)
        outer = radius + (18 if index % 2 else 26)
        draw.line(
            (
                cx + math.cos(radians) * inner,
                cy + math.sin(radians) * inner,
                cx + math.cos(radians) * outer,
                cy + math.sin(radians) * outer,
            ),
            fill=(208, 160, 67, 205),
            width=3 if index % 2 else 5,
        )
    draw.ellipse(
        (cx - radius, cy - radius, cx + radius, cy + radius),
        fill=(92, 51, 14, 244),
        outline=LIGHT_GOLD,
        width=4,
    )
    draw.ellipse(
        (cx - radius + 7, cy - radius + 7, cx + radius - 7, cy + radius - 7),
        outline=DARK_GOLD,
        width=2,
    )
    font = ImageFont.truetype(str(FONT_BOLD), int(radius * 0.72))
    centered_text(
        draw,
        (cx - radius, cy - radius, cx + radius, cy + radius),
        "SOL",
        font,
        LIGHT_GOLD,
        stroke_width=1,
        stroke_fill=(47, 27, 11, 255),
    )


def build(
    source_name: str,
    target_name: str,
    panel: tuple[int, int, int, int],
    badge: tuple[int, int, int],
    title_size: int,
    subtitle_size: int,
    preview_dir: Path | None,
) -> None:
    source = Image.open(ART / source_name).convert("RGBA")
    overlay = Image.new("RGBA", source.size, (0, 0, 0, 0))
    left, top, right, bottom = panel

    shadow = Image.new("RGBA", source.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle(
        (left + 7, top + 9, right + 7, bottom + 9),
        radius=18,
        fill=(0, 0, 0, 170),
    )
    overlay.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(7)))

    draw = ImageDraw.Draw(overlay)
    draw.rounded_rectangle(panel, radius=18, fill=INK, outline=GOLD, width=3)
    draw.rounded_rectangle(
        (left + 7, top + 7, right - 7, bottom - 7),
        radius=13,
        outline=(133, 88, 28, 230),
        width=2,
    )

    draw_sol_badge(overlay, badge[0:2], badge[2])
    draw = ImageDraw.Draw(overlay)
    text_left = badge[0] + badge[2] + 20
    text_right = right - 18
    title_font = ImageFont.truetype(str(FONT_BOLD), title_size)
    subtitle_font = ImageFont.truetype(str(FONT_REGULAR), subtitle_size)
    centered_text(
        draw,
        (text_left, top + 17, text_right, top + 32 + title_size),
        "DOWAGERMOD",
        title_font,
        LIGHT_GOLD,
        stroke_width=1,
        stroke_fill=(24, 12, 6, 255),
    )
    line_y = top + 27 + title_size
    draw.line((text_left + 15, line_y, text_right - 15, line_y), fill=GOLD, width=2)
    centered_text(
        draw,
        (text_left, line_y + 7, text_right, bottom - 14),
        "THE SOL PATCH",
        subtitle_font,
        (235, 211, 153, 255),
    )

    result = Image.alpha_composite(source, overlay).convert("RGB")
    target = ART / target_name
    result.save(target, pixel_format="DXT1")
    if preview_dir is not None:
        preview_dir.mkdir(parents=True, exist_ok=True)
        Image.open(target).convert("RGB").save(
            preview_dir / (Path(target_name).stem + ".png")
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build the DowagerMod Sol Patch loading-screen DDS assets."
    )
    parser.add_argument(
        "--preview-dir",
        type=Path,
        help="Optionally write PNG previews to this directory.",
    )
    args = parser.parse_args()

    missing_fonts = [path for path in (FONT_BOLD, FONT_REGULAR) if not path.exists()]
    if missing_fonts:
        raise FileNotFoundError(
            "Required Constantia fonts are missing: %s"
            % ", ".join(str(path) for path in missing_fonts)
        )

    build(
        "LoadingScreenBGBeyondtheSword.dds",
        "LoadingScreenBGDowager.dds",
        (485, 655, 909, 827),
        (545, 741, 46),
        35,
        25,
        args.preview_dir,
    )
    build(
        "LoadingScreenBGslideshowBeyondtheSword.dds",
        "LoadingScreenBGslideshowDowager.dds",
        (540, 306, 911, 444),
        (588, 375, 36),
        30,
        20,
        args.preview_dir,
    )


if __name__ == "__main__":
    main()
