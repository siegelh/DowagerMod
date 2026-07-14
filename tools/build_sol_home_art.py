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
    / "Main Menu"
)
FONT_ROOT = Path(r"C:\Windows\Fonts")
FONT_BOLD = FONT_ROOT / "constanb.ttf"
FONT_REGULAR = FONT_ROOT / "constan.ttf"

SOURCE_TEXTURE = ART / "Beyond_The_Sword_Main_Menu.dds"
TARGET_TEXTURE = ART / "DowagerMod_Sol_Home_Screen.dds"
SOURCE_NIF = ART / "CIV4MainMenuBG.nif"
TARGET_NIF = ART / "CIV4MainMenuBGDowager.nif"

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
    stroke_fill: tuple[int, int, int, int] | None = None,
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
        inner = radius + (4 if index % 2 else 2)
        outer = radius + (12 if index % 2 else 18)
        draw.line(
            (
                cx + math.cos(radians) * inner,
                cy + math.sin(radians) * inner,
                cx + math.cos(radians) * outer,
                cy + math.sin(radians) * outer,
            ),
            fill=(208, 160, 67, 220),
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
        stroke_fill=(47, 27, 11, 255),
    )


def build_texture() -> None:
    image = Image.open(SOURCE_TEXTURE).convert("RGBA")
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))

    shadow = Image.new("RGBA", image.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle(
        (493, 378, 972, 479),
        radius=16,
        fill=(0, 0, 0, 185),
    )
    overlay.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(7)))

    draw = ImageDraw.Draw(overlay)
    draw.rounded_rectangle(
        (486, 370, 965, 471),
        radius=16,
        fill=(27, 19, 13, 225),
        outline=GOLD,
        width=3,
    )
    draw.rounded_rectangle(
        (493, 377, 958, 464),
        radius=11,
        outline=(133, 88, 28, 225),
        width=2,
    )
    draw_sol_badge(overlay, (535, 421), 28)
    draw = ImageDraw.Draw(overlay)
    centered_text(
        draw,
        (590, 383, 943, 425),
        "DOWAGERMOD",
        ImageFont.truetype(str(FONT_BOLD), 32),
        LIGHT_GOLD,
        stroke_width=1,
        stroke_fill=(24, 12, 6, 255),
    )
    draw.line((610, 426, 923, 426), fill=GOLD, width=2)
    centered_text(
        draw,
        (590, 430, 943, 458),
        "THE SOL PATCH",
        ImageFont.truetype(str(FONT_REGULAR), 20),
        (235, 211, 153, 255),
    )
    Image.alpha_composite(image, overlay).save(TARGET_TEXTURE, pixel_format="DXT3")


def build_scene() -> None:
    source_name = b"Beyond_The_Sword_Main_Menu.dds"
    target_name = b"DowagerMod_Sol_Home_Screen.dds"
    scene = SOURCE_NIF.read_bytes()
    if len(source_name) != len(target_name) or scene.count(source_name) != 1:
        raise RuntimeError("NIF texture reference cannot be replaced safely")
    TARGET_NIF.write_bytes(scene.replace(source_name, target_name))


def write_previews(preview_dir: Path) -> None:
    preview_dir.mkdir(parents=True, exist_ok=True)
    decoded = Image.open(TARGET_TEXTURE).convert("RGBA")
    decoded.save(preview_dir / "DowagerMod_Sol_Home_Screen.png")

    checker = Image.new("RGBA", decoded.size, (0, 0, 0, 255))
    draw = ImageDraw.Draw(checker)
    for y in range(0, 1024, 64):
        for x in range(0, 1024, 64):
            color = (
                (45, 45, 45, 255)
                if (x // 64 + y // 64) % 2
                else (85, 85, 85, 255)
            )
            draw.rectangle((x, y, x + 63, y + 63), fill=color)
    checker.alpha_composite(decoded)
    checker.convert("RGB").save(
        preview_dir / "DowagerMod_Sol_Home_Screen_checker.png"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build the dedicated DowagerMod Sol Patch home scene."
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
