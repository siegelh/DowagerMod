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
    / "Classical Main Menu"
)
FONT_ROOT = Path(r"C:\Windows\Fonts")
FONT_BOLD = FONT_ROOT / "constanb.ttf"
FONT_REGULAR = FONT_ROOT / "constan.ttf"

SOURCE_TEXTURE = ART / "Duomo3.dds"
TARGET_TEXTURE = ART / "SolBG3.dds"
SOURCE_NIF = ART / "CIV4MainMenuBG.nif"
TARGET_NIF = ART / "CIV4MainMenuBGSol.nif"

GOLD = (224, 184, 91, 255)
LIGHT_GOLD = (247, 224, 157, 255)
DARK_GOLD = (115, 72, 20, 255)


def centered_text(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    text: str,
    font: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int, int],
    stroke_width: int = 0,
) -> None:
    left, top, right, bottom = box
    bounds = draw.textbbox((0, 0), text, font=font, stroke_width=stroke_width)
    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]
    draw.text(
        (
            left + (right - left - width) / 2,
            top + (bottom - top - height) / 2 - bounds[1],
        ),
        text,
        font=font,
        fill=fill,
        stroke_width=stroke_width,
        stroke_fill=(31, 17, 8, 255),
    )


def draw_sol_badge(layer: Image.Image) -> None:
    draw = ImageDraw.Draw(layer)
    cx, cy, radius = 666, 518, 29
    for index in range(24):
        angle = math.radians(index * 15)
        inner = radius + (4 if index % 2 else 2)
        outer = radius + (13 if index % 2 else 19)
        draw.line(
            (
                cx + math.cos(angle) * inner,
                cy + math.sin(angle) * inner,
                cx + math.cos(angle) * outer,
                cy + math.sin(angle) * outer,
            ),
            fill=(208, 160, 67, 225),
            width=2 if index % 2 else 4,
        )
    draw.ellipse(
        (cx - radius, cy - radius, cx + radius, cy + radius),
        fill=(92, 51, 14, 255),
        outline=LIGHT_GOLD,
        width=3,
    )
    draw.ellipse(
        (cx - radius + 6, cy - radius + 6, cx + radius - 6, cy + radius - 6),
        outline=DARK_GOLD,
        width=2,
    )
    centered_text(
        draw,
        (cx - radius, cy - radius, cx + radius, cy + radius),
        "SOL",
        ImageFont.truetype(str(FONT_BOLD), 19),
        LIGHT_GOLD,
        stroke_width=1,
    )


def build_texture() -> None:
    foreground = Image.open(SOURCE_TEXTURE).convert("RGBA")
    foreground = foreground.crop((0, 0, 1024, 1024))
    overlay = Image.new("RGBA", foreground.size, (0, 0, 0, 0))

    shadow = Image.new("RGBA", foreground.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle(
        (625, 475, 933, 579),
        radius=17,
        fill=(0, 0, 0, 190),
    )
    overlay.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(7)))

    draw = ImageDraw.Draw(overlay)
    draw.rounded_rectangle(
        (617, 466, 925, 570),
        radius=17,
        fill=(27, 19, 13, 238),
        outline=GOLD,
        width=3,
    )
    draw.rounded_rectangle(
        (624, 473, 918, 563),
        radius=12,
        outline=(133, 88, 28, 235),
        width=2,
    )
    draw_sol_badge(overlay)
    draw = ImageDraw.Draw(overlay)
    centered_text(
        draw,
        (716, 482, 905, 524),
        "THE SOL PATCH",
        ImageFont.truetype(str(FONT_BOLD), 23),
        LIGHT_GOLD,
        stroke_width=1,
    )
    draw.line((730, 526, 891, 526), fill=GOLD, width=2)
    centered_text(
        draw,
        (716, 531, 905, 555),
        "DOWAGERMOD 2026",
        ImageFont.truetype(str(FONT_REGULAR), 15),
        (235, 211, 153, 255),
    )
    Image.alpha_composite(foreground, overlay).save(TARGET_TEXTURE)


def build_scene() -> None:
    source_name = b"Duomo3.dds"
    target_name = b"SolBG3.dds"
    scene = SOURCE_NIF.read_bytes()
    if len(source_name) != len(target_name) or scene.count(source_name) != 1:
        raise RuntimeError("NIF texture reference cannot be replaced safely")
    TARGET_NIF.write_bytes(scene.replace(source_name, target_name))


def write_previews(preview_dir: Path) -> None:
    preview_dir.mkdir(parents=True, exist_ok=True)
    foreground = Image.open(TARGET_TEXTURE).convert("RGBA")
    foreground.save(preview_dir / "Classical_Main_Menu_Sol_foreground_preview.png")

    sky = Image.open(ART / "Sky.dds").convert("RGBA")
    sky = sky.resize(foreground.size, Image.Resampling.LANCZOS)
    Image.alpha_composite(sky, foreground).convert("RGB").save(
        preview_dir / "Classical_Main_Menu_Sol_composite_preview.png"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build the Sol Patch variant of the customized home scene."
    )
    parser.add_argument(
        "--preview-dir",
        type=Path,
        help="Optionally write exact decoded PNG previews to this directory.",
    )
    args = parser.parse_args()

    missing_fonts = [path for path in (FONT_BOLD, FONT_REGULAR) if not path.exists()]
    if missing_fonts:
        raise FileNotFoundError(
            "Required Constantia fonts are missing: %s"
            % ", ".join(str(path) for path in missing_fonts)
        )

    build_texture()
    build_scene()
    if args.preview_dir is not None:
        write_previews(args.preview_dir)


if __name__ == "__main__":
    main()
