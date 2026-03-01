from pathlib import Path
import math

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets"
INDUSTRY_DIR = ASSETS / "Art/Interface/Buttons/Buildings/Industries"
SYNTH_DIR = ASSETS / "Art/Interface/Buttons/Bonuses/Synthetic"


def p(rel: str) -> Path:
    return ASSETS / rel.replace("/", "\\")


BASES = {
    "agrarian_board.dds": p("Art/Caveman2Cosmos/art/interface/buttons/buildings/modern_granary.dds"),
    "exchange_hall.dds": p("Art/BTG/Buildings/CentralBank/Bank.dds"),
    "mining_bureau.dds": p("Art/Caveman2Cosmos/art/structures/improvements/core_mine/mine.dds"),
    "manufactories_office.dds": p("Art/Caveman2Cosmos/art/structures/improvements/workshop/workshop.dds"),
    "forestry_commission.dds": p("Art/Interface/Buttons/btn_build_forest.dds"),
    "hydraulic_office.dds": p("Art/Caveman2Cosmos/art/structures/improvements/watermill/watermill.dds"),
    "estate_office.dds": p("Art/Caveman2Cosmos/art/structures/improvements/plantation/plantation_anglo/plantation.dds"),
    "pastoral_board.dds": p("Art/Caveman2Cosmos/art/structures/buildings/barracks/greco_roman_barracks/barracks.dds"),
    "frontier_lodge.dds": p("Art/Caveman2Cosmos/art/structures/buildings/poacher_camp/camp.dds"),
    "maritime_exchange.dds": p("Art/Caveman2Cosmos/art/event_images/goodharbor.dds"),
    "energy_directorate.dds": p("Art/BTG/OilRefinery/OilRefineryBase.dds"),
    "dye_works.dds": SYNTH_DIR / "fine_dyes.dds",
    "furriers_hall.dds": SYNTH_DIR / "fine_furs.dds",
    "jewelers_quarter.dds": SYNTH_DIR / "cut_gems.dds",
    "minting_house.dds": SYNTH_DIR / "gold_bullion.dds",
    "perfumers_sanctuary.dds": SYNTH_DIR / "temple_incense.dds",
    "ivory_carvers_atelier.dds": SYNTH_DIR / "ivory_carvings.dds",
    "silk_weavers_workshop.dds": SYNTH_DIR / "fine_silk.dds",
    "silversmiths_hall.dds": SYNTH_DIR / "worked_silver.dds",
    "spice_exchange.dds": SYNTH_DIR / "spice_blends.dds",
    "confectioners_guild.dds": SYNTH_DIR / "confections.dds",
    "vintners_guild.dds": SYNTH_DIR / "vintage_wine.dds",
    "whale_oil_chandlery.dds": SYNTH_DIR / "lamp_oil.dds",
    "playwrights_guild.dds": SYNTH_DIR / "stage_plays.dds",
    "recording_house.dds": SYNTH_DIR / "master_recordings.dds",
    "film_studio_district.dds": SYNTH_DIR / "film_prints.dds",
    "millers_guild.dds": SYNTH_DIR / "flour.dds",
    "smokehouse.dds": SYNTH_DIR / "cured_meats.dds",
    "cannery.dds": SYNTH_DIR / "preserved_seafood.dds",
    "fruit_preservers.dds": SYNTH_DIR / "fruit_preserves.dds",
    "royal_garments_house.dds": SYNTH_DIR / "fine_silk.dds",
    "noble_tailors_hall.dds": SYNTH_DIR / "fine_furs.dds",
    "court_regalia_atelier.dds": SYNTH_DIR / "ivory_carvings.dds",
    "dyed_fur_salon.dds": SYNTH_DIR / "fine_dyes.dds",
    "crown_jeweler.dds": SYNTH_DIR / "gold_bullion.dds",
    "royal_mint.dds": SYNTH_DIR / "worked_silver.dds",
    "gemcutters_exchange.dds": SYNTH_DIR / "cut_gems.dds",
    "regal_treasures_court.dds": SYNTH_DIR / "ivory_carvings.dds",
    "perfumers_quarter.dds": SYNTH_DIR / "temple_incense.dds",
    "grand_banquet_hall.dds": SYNTH_DIR / "vintage_wine.dds",
    "confectioners_exchange.dds": SYNTH_DIR / "confections.dds",
    "ceremonial_cellars.dds": SYNTH_DIR / "vintage_wine.dds",
    "festival_market.dds": SYNTH_DIR / "spice_blends.dds",
    "imperial_outfitters.dds": SYNTH_DIR / "fine_furs.dds",
    "admiralty_curios_house.dds": SYNTH_DIR / "lamp_oil.dds",
    "navigators_instrument_works.dds": SYNTH_DIR / "worked_silver.dds",
    "opera_house.dds": SYNTH_DIR / "stage_plays.dds",
    "cinema_palace.dds": SYNTH_DIR / "film_prints.dds",
    "soundstage_complex.dds": SYNTH_DIR / "master_recordings.dds",
    "mass_entertainment_network.dds": SYNTH_DIR / "film_prints.dds",
    "bakers_exchange.dds": SYNTH_DIR / "flour.dds",
    "festival_kitchens.dds": SYNTH_DIR / "vintage_wine.dds",
    "royal_kitchens.dds": SYNTH_DIR / "cured_meats.dds",
    "spiced_carvery.dds": SYNTH_DIR / "spice_blends.dds",
    "maritime_supper_club.dds": SYNTH_DIR / "preserved_seafood.dds",
    "preserves_market.dds": SYNTH_DIR / "fruit_preserves.dds",
}


BADGES = {
    "agrarian_board.dds": "field",
    "exchange_hall.dds": "coin",
    "mining_bureau.dds": "pick",
    "manufactories_office.dds": "gear",
    "forestry_commission.dds": "tree",
    "hydraulic_office.dds": "water",
    "estate_office.dds": "leaf",
    "pastoral_board.dds": "hoof",
    "frontier_lodge.dds": "tent",
    "maritime_exchange.dds": "anchor",
    "energy_directorate.dds": "oil",
    "dye_works.dds": "craft",
    "furriers_hall.dds": "craft",
    "jewelers_quarter.dds": "craft",
    "minting_house.dds": "craft",
    "perfumers_sanctuary.dds": "craft",
    "ivory_carvers_atelier.dds": "craft",
    "silk_weavers_workshop.dds": "craft",
    "silversmiths_hall.dds": "craft",
    "spice_exchange.dds": "craft",
    "confectioners_guild.dds": "craft",
    "vintners_guild.dds": "craft",
    "whale_oil_chandlery.dds": "craft",
    "playwrights_guild.dds": "craft",
    "recording_house.dds": "craft",
    "film_studio_district.dds": "craft",
    "millers_guild.dds": "craft",
    "smokehouse.dds": "craft",
    "cannery.dds": "craft",
    "fruit_preservers.dds": "craft",
    "royal_garments_house.dds": "crown",
    "noble_tailors_hall.dds": "crown",
    "court_regalia_atelier.dds": "crown",
    "dyed_fur_salon.dds": "crown",
    "crown_jeweler.dds": "crown",
    "royal_mint.dds": "crown",
    "gemcutters_exchange.dds": "crown",
    "regal_treasures_court.dds": "crown",
    "perfumers_quarter.dds": "crown",
    "imperial_outfitters.dds": "crown",
    "admiralty_curios_house.dds": "crown",
    "navigators_instrument_works.dds": "crown",
    "grand_banquet_hall.dds": "goblet",
    "confectioners_exchange.dds": "goblet",
    "ceremonial_cellars.dds": "goblet",
    "festival_market.dds": "goblet",
    "bakers_exchange.dds": "goblet",
    "festival_kitchens.dds": "goblet",
    "royal_kitchens.dds": "goblet",
    "spiced_carvery.dds": "goblet",
    "maritime_supper_club.dds": "goblet",
    "preserves_market.dds": "goblet",
    "opera_house.dds": "star",
    "cinema_palace.dds": "star",
    "soundstage_complex.dds": "star",
    "mass_entertainment_network.dds": "star",
}


PALETTE = {
    "field": ((134, 102, 52), (244, 217, 124), (81, 54, 20)),
    "coin": ((129, 88, 28), (246, 208, 93), (87, 52, 8)),
    "pick": ((126, 78, 31), (233, 187, 100), (71, 45, 18)),
    "gear": ((121, 87, 38), (225, 191, 113), (70, 48, 18)),
    "tree": ((71, 112, 49), (194, 226, 147), (33, 58, 20)),
    "water": ((49, 94, 125), (164, 219, 248), (18, 47, 73)),
    "leaf": ((74, 111, 43), (186, 220, 120), (34, 56, 19)),
    "hoof": ((109, 82, 55), (209, 185, 144), (63, 40, 23)),
    "tent": ((112, 83, 46), (220, 187, 114), (66, 45, 18)),
    "anchor": ((45, 90, 123), (161, 213, 246), (16, 41, 65)),
    "oil": ((73, 64, 53), (219, 184, 97), (28, 22, 17)),
    "craft": ((159, 126, 39), (250, 222, 115), (87, 55, 11)),
    "crown": ((131, 37, 49), (248, 204, 116), (63, 12, 22)),
    "goblet": ((103, 59, 23), (244, 206, 120), (62, 29, 9)),
    "star": ((55, 74, 124), (214, 219, 255), (21, 34, 72)),
}


def load_base(path: Path) -> Image.Image:
    img = Image.open(path).convert("RGBA")
    if img.size != (64, 64):
        img = img.resize((64, 64), Image.LANCZOS)
    img = ImageEnhance.Color(img).enhance(0.92)
    img = ImageEnhance.Contrast(img).enhance(1.06)
    vignette = Image.new("L", (64, 64), 0)
    d = ImageDraw.Draw(vignette)
    d.ellipse((-8, -8, 72, 72), fill=255)
    vignette = vignette.filter(ImageFilter.GaussianBlur(10))
    shade = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    shade.putalpha(Image.eval(vignette, lambda x: max(0, 110 - x // 2)))
    return Image.alpha_composite(img, shade)


def draw_star(draw: ImageDraw.ImageDraw, cx: float, cy: float, r_outer: float, r_inner: float, fill, outline):
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        r = r_outer if i % 2 == 0 else r_inner
        pts.append((cx + math.cos(ang) * r, cy + math.sin(ang) * r))
    draw.polygon(pts, fill=fill, outline=outline)


def draw_badge(base: Image.Image, badge: str):
    top, highlight, dark = PALETTE[badge]
    overlay = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    x0, y0, x1, y1 = 40, 4, 62, 26
    d.ellipse((x0 + 1, y0 + 2, x1 + 1, y1 + 2), fill=(0, 0, 0, 110))
    d.ellipse((x0, y0, x1, y1), fill=top + (245,), outline=(255, 234, 180, 255), width=1)
    d.ellipse((x0 + 2, y0 + 2, x1 - 2, y1 - 2), outline=highlight + (190,), width=1)

    cx, cy = 51, 15
    if badge == "field":
        for off in (-4, 0, 4):
            d.line((cx + off, cy + 6, cx + off, cy - 4), fill=dark + (255,), width=2)
            d.line((cx + off, cy - 2, cx + off - 3, cy + 1), fill=dark + (255,), width=1)
            d.line((cx + off, cy - 4, cx + off + 3, cy - 1), fill=dark + (255,), width=1)
    elif badge == "coin":
        d.ellipse((44, 9, 52, 17), fill=dark + (255,), outline=highlight + (255,))
        d.ellipse((49, 12, 57, 20), fill=dark + (255,), outline=highlight + (255,))
    elif badge == "pick":
        d.line((46, 19, 56, 9), fill=dark + (255,), width=2)
        d.line((50, 11, 58, 15), fill=dark + (255,), width=2)
        d.line((49, 10, 45, 18), fill=dark + (255,), width=2)
    elif badge == "gear":
        d.ellipse((45, 9, 57, 21), fill=None, outline=dark + (255,), width=2)
        for ang in range(0, 360, 45):
            rad = math.radians(ang)
            x = cx + math.cos(rad) * 8
            y = cy + math.sin(rad) * 8
            d.line((cx + math.cos(rad) * 5, cy + math.sin(rad) * 5, x, y), fill=dark + (255,), width=2)
        d.ellipse((49, 13, 53, 17), fill=dark + (255,))
    elif badge == "tree":
        d.rectangle((49, 16, 53, 22), fill=dark + (255,))
        d.polygon([(51, 7), (44, 16), (58, 16)], fill=dark + (255,))
        d.polygon([(51, 10), (46, 18), (56, 18)], fill=highlight + (255,))
    elif badge == "water":
        d.arc((43, 10, 51, 18), 0, 180, fill=dark + (255,), width=2)
        d.arc((48, 12, 56, 20), 0, 180, fill=dark + (255,), width=2)
        d.arc((53, 10, 61, 18), 0, 180, fill=dark + (255,), width=2)
    elif badge == "leaf":
        d.polygon([(51, 8), (44, 15), (51, 22), (58, 15)], fill=dark + (255,), outline=highlight + (255,))
        d.line((51, 10, 51, 20), fill=highlight + (255,), width=1)
    elif badge == "hoof":
        d.arc((45, 7, 57, 22), 180, 360, fill=dark + (255,), width=3)
        d.line((46, 15, 46, 21), fill=dark + (255,), width=2)
        d.line((56, 15, 56, 21), fill=dark + (255,), width=2)
    elif badge == "tent":
        d.polygon([(44, 20), (51, 8), (58, 20)], fill=dark + (255,), outline=highlight + (255,))
        d.line((51, 8, 51, 20), fill=highlight + (255,), width=1)
    elif badge == "anchor":
        d.line((51, 8, 51, 19), fill=dark + (255,), width=2)
        d.arc((45, 13, 57, 23), 0, 180, fill=dark + (255,), width=2)
        d.line((46, 19, 42, 16), fill=dark + (255,), width=2)
        d.line((56, 19, 60, 16), fill=dark + (255,), width=2)
        d.line((48, 11, 54, 11), fill=dark + (255,), width=2)
    elif badge == "oil":
        d.polygon([(51, 8), (46, 16), (51, 22), (56, 16)], fill=dark + (255,), outline=highlight + (255,))
    elif badge == "craft":
        d.line((46, 19, 54, 11), fill=dark + (255,), width=2)
        d.line((50, 10, 58, 10), fill=dark + (255,), width=3)
        d.line((46, 19, 44, 21), fill=dark + (255,), width=2)
    elif badge == "crown":
        d.polygon([(44, 18), (46, 10), (50, 15), (54, 8), (58, 15), (60, 10), (62, 18)], fill=dark + (255,), outline=highlight + (255,))
        d.rectangle((44, 18, 62, 22), fill=dark + (255,))
    elif badge == "goblet":
        d.polygon([(46, 9), (56, 9), (53, 15), (49, 15)], fill=dark + (255,), outline=highlight + (255,))
        d.rectangle((50, 15, 52, 20), fill=dark + (255,))
        d.arc((47, 18, 55, 24), 0, 180, fill=dark + (255,), width=2)
    elif badge == "star":
        draw_star(d, cx, cy, 7, 3, dark + (255,), highlight + (255,))

    return Image.alpha_composite(base, overlay)


def build_contact_sheet(paths):
    cols = 4
    tile_w, tile_h = 96, 96
    rows = math.ceil(len(paths) / cols)
    sheet = Image.new("RGBA", (cols * tile_w, rows * tile_h), (24, 24, 26, 255))
    d = ImageDraw.Draw(sheet)
    for i, path in enumerate(paths):
        row = i // cols
        col = i % cols
        img = Image.open(path).convert("RGBA").resize((72, 72), Image.LANCZOS)
        x = col * tile_w + 12
        y = row * tile_h + 4
        sheet.paste(img, (x, y), img)
        d.text((col * tile_w + 4, row * tile_h + 79), path.stem[:24], fill=(240, 219, 170, 255))
    preview = INDUSTRY_DIR / "_preview_v2.png"
    sheet.save(preview)
    return preview


def main():
    generated = []
    for filename, src in BASES.items():
        if not src.exists():
            src = INDUSTRY_DIR / filename
        base = load_base(src)
        out = draw_badge(base, BADGES[filename])
        out.save(INDUSTRY_DIR / filename)
        generated.append(INDUSTRY_DIR / filename)
    preview = build_contact_sheet(generated[:16])
    print(f"Generated {len(generated)} buttons")
    print(preview)


if __name__ == "__main__":
    main()
