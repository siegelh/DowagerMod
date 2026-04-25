# Industry Icon Pipeline

This note documents the two separate icon systems used for industry resources in the BtS mod.

## Two icon systems

### 1. Bonus/button art

This is the larger icon used by bonus buttons, many Civilopedia views, and any UI that reads the bonus `Button` path from XML.

Relevant files:

- `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Terrain/CIV4BonusInfos.xml`
- `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Art/CIV4ArtDefines_Bonus.xml`
- `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/Art/Interface/Buttons/Bonuses/Synthetic/*.dds`

Mechanics:

- `CIV4BonusInfos.xml` maps `BONUS_*` to `ART_DEF_BONUS_*` via `<ArtDefineTag>`.
- `CIV4ArtDefines_Bonus.xml` defines the actual button art via `<Button>`.
- Button art files are `DDS`.

Example:

- `BONUS_GOLD_BULLION` -> `ART_DEF_BONUS_GOLD_BULLION`
- `ART_DEF_BONUS_GOLD_BULLION` currently points to `Art/Interface/Buttons/Bonuses/Synthetic/gold_x64.dds`

### 2. Tiny inline glyphs

This is the small symbol rendered in text with `%c`, including the industry advisor table rows that call `gc.getBonusInfo(...).getChar()`.

Relevant files:

- `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Art/CIV4ArtDefines_Bonus.xml`
- `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/res/Fonts/GameFont.tga`
- `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/res/Fonts/GameFont_75.tga`

Mechanics:

- `CIV4ArtDefines_Bonus.xml` assigns a glyph slot via `<FontButtonIndex>`.
- That index points into the `GameFont` sheets.
- The game uses those `TGA` font atlases when UI code renders `%c`.

Formats:

- `GameFont.tga`: `640x320`, `32-bit`
- `GameFont_75.tga`: `512x256`, `32-bit`

Important:

- A `DDS` file cannot be used directly as the tiny inline glyph.
- To change the inline glyph, the icon must be drawn into both `GameFont` sheets.

## Gold example

Raw gold:

- XML art define: `ART_DEF_BONUS_GOLD`
- Glyph slot: `FontButtonIndex 23`

Refined gold bullion:

- XML art define: `ART_DEF_BONUS_GOLD_BULLION`
- Button art: `Art/Interface/Buttons/Bonuses/Synthetic/gold_x64.dds`
- Glyph slot: currently `FontButtonIndex 23`

Current implication:

- Gold bullion has its own button art.
- Gold bullion still reuses the raw gold tiny inline glyph because both use slot `23`.

## How to give a refined resource its own inline glyph later

> **IMPORTANT (regression note, agent-baseline-fix-worker-bugs):** any
> BtS-override `GameFont.tga` / `GameFont_75.tga` MUST be a strict superset of
> the base game's glyph cells — same dimensions, same alpha layout, and every
> base-game cell present at the same X/Y. A stale or hand-edited copy at
> `…/Beyond the Sword/Assets/res/Fonts/` shadows the vanilla atlas and causes
> all `%c` symbols (inline resource icons in text **and** religion badges on
> city bars) to render blank. If you only need to alias new resources to
> existing base glyphs, the override files are redundant and should not exist
> — let the engine fall through to the vanilla atlas.

1. Pick an unused `FontButtonIndex` in `CIV4ArtDefines_Bonus.xml`.
2. Change the resource's `<FontButtonIndex>` to that new slot.
3. Edit both `GameFont.tga` and `GameFont_75.tga`.
4. Draw the new icon into the matching slot in both sheets.
5. Keep canvas size, alpha, and alignment unchanged.

As of this note, free indices visible in the active bonus art XML include:

- `44-55`
- `63+`

## Industry advisor note

The current industry advisor renders inline glyphs, not button art.

Relevant code paths:

- `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/Python/Screens/CvIndustryAdvisor.py`

That means:

- changing `<Button>` updates bonus/button art
- changing `GameFont` plus `<FontButtonIndex>` updates the tiny inline symbol

## Practical rule of thumb

If the icon is large and looks like a button, change `DDS` art and the `<Button>` path.

If the icon is a tiny text-like symbol, change `GameFont.tga`, `GameFont_75.tga`, and the resource's `<FontButtonIndex>`.
