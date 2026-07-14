# Loading and Home Screen Modernization

- Status: `implemented / installed-game validation pending`
- Owner / agent: Copilot
- Last updated: `2026-07-14`

## Problem Statement

- Task: replace the stock Civilization IV: Beyond the Sword loading presentation
  with a DowagerMod-specific presentation.
- Current observed behavior: the active BtS payload still contains the stock
  Florence/Beyond the Sword loading artwork and stock menu-to-art bindings.
- Why this is a real repo problem: the loading presentation does not identify
  the installed game as DowagerMod and visually predates the current roster,
  industries, landmarks, and other mod systems.

## How The Loading Screen Works

The loading presentation is data-driven until it reaches the closed-source
game executable:

1. `CIV4MainMenus.xml` defines four selectable main-menu profiles. Each profile
   supplies a `Loading` art key and a `LoadingSlideshow` art key.
2. `CIV4ArtDefines_Interface.xml` resolves those keys to DDS paths.
3. The Civilization IV executable renders the selected pair while loading.
   There is no matching Python or custom-DLL loading-screen implementation in
   the live BtS tree.

The persistent home screen is a separate path. Each menu profile's `Scene` and
`SceneNoShader` keys resolve through `CIV4ArtDefines_Interface.xml` to a NIF
scene. The BtS scene is `Art/Interface/Main Menu/CIV4MainMenuBG.nif`, whose
foreground texture is `Beyond_The_Sword_Main_Menu.dds`.

The relevant live bindings are:

| Menu profile | Full loading key | Slideshow key |
| --- | --- | --- |
| `MAIN_MENU_CLASSICAL` | `MAINMENU_LOAD_CLASSICAL` | `MAINMENU_SLIDESHOW_LOAD_CLASSICAL` |
| `MAIN_MENU_BEYOND_SWORD` | `MAINMENU_LOAD_BTS` | `MAINMENU_SLIDESHOW_LOAD_BTS` |

The active art files are all DXT1 DDS textures:

| File | Dimensions | Current content |
| --- | ---: | --- |
| `LoadingScreenBGBeyondtheSword.dds` | 1024x1024 | Stock Florence/BtS full loading frame |
| `LoadingScreenBGslideshowBeyondtheSword.dds` | 1024x512 | Stock Florence/BtS slideshow frame |
| `LoadingScreenBGClassical.dds` | 1024x1024 | Stock classical full loading frame |
| `LoadingScreenBGslideshowClassical.dds` | 1024x512 | Stock classical slideshow frame |
| `LoadingScreenBG.dds` | 1024x1024 | Stock vanilla-compatible full loading frame |

Evidence:

- `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the
  Sword/Assets/XML/Art/CIV4MainMenus.xml:9-44`
- `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the
  Sword/Assets/XML/Art/CIV4ArtDefines_Interface.xml:730-760`
- `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the
  Sword/Assets/Art/Interface/Screens/Loading/`
- DDS header inspection: full images are 1024x1024 DXT1; slideshow images are
  1024x512 DXT1.
- Repository search found no Python or authoritative DLL consumer for the four
  BtS/Classical loading keys.
- Git history shows these five files entered as stock runtime-mirror assets in
  `4333d5b65`; no DowagerMod-specific art revision follows it.

## Scope

- Add a DowagerMod full loading texture and matching slideshow texture.
- Add a copied DowagerMod home-scene NIF and branded DXT3 foreground texture.
- Add dedicated DowagerMod interface-art keys.
- Point both the Classical and Beyond the Sword profiles at those dedicated
  keys so the branding does not depend on a player's remembered menu style.
- Preserve engine-owned progress text, tips, and loading behavior.
- Preserve the existing DDS dimensions and DXT1 format unless runtime testing
  proves a different supported format is necessary.

## Non-Goals

- Do not change loading mechanics, save loading, threading, XML initialization,
  or performance.
- Do not alter the Vanilla or Warlords profile bindings.
- Do not replace `MAINMENU_SLIDESHOW_LOAD`: several Python advisor screens use
  that generic key as their background.
- Do not edit scenario/mod copies under `Beyond the Sword/Mods/`.
- Do not reuse third-party artwork without confirmed redistribution rights.

## Trusted Sources Of Truth

- Menu-to-art selection:
  `Beyond the Sword/Assets/XML/Art/CIV4MainMenus.xml`.
- Art-key-to-file resolution:
  `Beyond the Sword/Assets/XML/Art/CIV4ArtDefines_Interface.xml`.
- Runtime payload:
  `Beyond the Sword/Assets/Art/Interface/Screens/Loading/`.
- Packaging behavior: `CoreFiles/install.py` mirrors the repository payload
  into the live game installation, so new files under the active BtS asset root
  are packaged automatically.
- Validation: `tools/test_gate.ps1`, followed by an installed-game visual smoke
  test.

## Existing Docs / Plans Trust Review

- `AGENTS.md`, `ARCHITECTURE.md`, and `INSTALLER.md` are trusted for the active
  BtS asset root and installer payload model.
- No existing loading-screen plan or runbook was found.
- Stock scenario copies are reference material only and are not live targets.

## Proposed Implementation Steps

1. Approve one visual brief and source image set.
2. Build a master image with a central safe area that survives 4:3, 16:9, and
   ultrawide scaling/cropping.
3. Export two DXT1 DDS deliverables:
   `LoadingScreenBGDowager.dds` at 1024x1024 and
   `LoadingScreenBGslideshowDowager.dds` at 1024x512.
4. Add `MAINMENU_LOAD_DOWAGER` and `MAINMENU_SLIDESHOW_LOAD_DOWAGER` to
   `CIV4ArtDefines_Interface.xml`.
5. Change only the Classical and Beyond the Sword menu profiles in
   `CIV4MainMenus.xml` to use the new keys.
6. Add a lightweight test that resolves both selected menu profiles through
   interface art and verifies the DDS headers, dimensions, compression, and
   tracked file paths.
7. Update the manual smoke-test runbook with startup and save-load checks at
   representative aspect ratios.
8. Point the Classical and BtS `Scene` and `SceneNoShader` fields at a
   dedicated copied scene so the persistent home screen also displays the Sol
   branding.

## Visual Brief Requiring Approval

Recommended direction: a DowagerMod historical montage with restrained
dark-gold framing, the DowagerMod title centered in the safe area, and visual
references to leaders, industries, and landmarks without embedding gameplay
text. Produce both layouts from the same master composition rather than
cropping the square image mechanically.

The approved loading implementation uses the stock BtS Florence composition.
The approved persistent home implementation preserves the customized Classical
scene: giant Dowager, embedded and floating Barclay imagery, custom sky, title,
and animation. It replaces only the obsolete `State Property Rebalanced!`
label area with a restrained dark-gold `THE SOL PATCH` plaque. Original assets
remain unchanged; dedicated copies are generated by
`tools/build_sol_loading_art.py` and `tools/build_sol_home_art.py`.

Future visual revisions may revisit:

- final title/logo treatment;
- whether the art should emphasize a single historical figure, a broad
  civilization montage, or a landmark/industry tableau;
- which existing repository art, if any, may be composited into the screen.

## Validation Plan

- Run `.\tools\test_gate.ps1`.
- Confirm both new files are tracked, referenced, DXT1, and exactly 1024x1024
  and 1024x512.
- Build the installer package and verify the files are present in its payload.
- Install on a test machine and inspect:
  - initial startup loading;
  - new-game loading;
  - save-game loading;
  - Classical and Beyond the Sword menu selections;
  - 4:3 and widescreen presentation;
  - unchanged advisor backgrounds.
- Manual visual testing is mandatory because the closed-source executable owns
  final layout and scaling.

## Risks / Rollback

- Main risk: important logo or subject matter may be clipped or distorted at
  non-4:3 resolutions.
- DXT compression can create visible artifacts around text and gradients.
- Updating the generic slideshow key would unintentionally alter advisor
  screens; dedicated keys avoid that coupling.
- Rollback is limited to the two XML bindings and two new DDS files.

## Completion Checklist

- [x] Live menu and art bindings mapped.
- [x] Active and inherited files inventoried.
- [x] Python and DLL ownership ruled out.
- [x] Asset format and dimensions verified.
- [x] Installer payload behavior identified.
- [x] Visual brief approved.
- [x] Master art and two DDS exports created.
- [x] Dedicated art keys and menu bindings implemented.
- [x] Automated asset-reference checks added.
- [x] Dedicated copy of the customized Classical home scene added.
- [x] Classical and BtS home-scene bindings implemented.
- [ ] Installed-game visual smoke test completed.

## Final Outcome Summary

- Investigation and implementation are complete.
- Both Classical and Beyond the Sword menu profiles use the dedicated Sol Patch
  loading and home-scene art keys.
- Installed-game aspect-ratio and progress-text validation remains required.
