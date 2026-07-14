# Great Person landmark improvements

- Status: `in_progress`
- Owner / agent: GitHub Copilot CLI
- Last updated: `2026-07-13`
## Problem Statement

- Task: give Great Engineers, Scientists, Merchants, Prophets, and the Venetian
  Merchant Prince consumptive map landmarks with distinctive placement and
  adjacency mechanics.
- Current observed behavior: the Great Artist's Grand Colosseum is the only
  reusable precedent. Other Great People cannot build the approved landmarks.
- Why this is a real repo/code problem: native improvements only expose plot
  Food, Production, and generic Commerce. The approved Research Campus,
  radius-two Naval Foundry aura, state-religion art selection, shared spacing,
  and deterministic AI choice require XML-backed DLL support.

## Why This Matters

- Great People gain enduring map-shaping alternatives to settling, discovery,
  trade missions, construction, religion, corporations, and Golden Ages.
- Adjacency turns terrain and existing infrastructure into strategic placement
  decisions while preserving the traditional Great Person action set.

## Scope

- Add Industrial Zone and Naval Foundry choices for Great Engineers.
- Add Research Campus for Great Scientists.
- Add Commercial District and Grand Bazaar for Great Merchants and Venetian
  Merchant Princes.
- Add eight art-persistent Sacred Grove variants for Great Prophets.
- Preserve the existing Grand Colosseum for Great Artists.
- Add generic XML-backed placement, yield, radius, worked-city commerce,
  spacing, help, refresh, and AI support in the authoritative DLL source.
- Add exact XML/unit-action contracts and manual smoke coverage.

## Non-Goals

- No landmark for Great Generals or Great Spies.
- No additional technology prerequisites.
- No replacement or weakening of traditional Great Person actions.
- No edits to base `Assets`, `Warlords`, generated installer payloads, or
  `petromod_v1`.
- No installer execution; the user owns installation.
- No old-save compatibility promise. All new InfoTypes are appended and fresh
  games are mandatory.

## Trusted Sources Of Truth

- XML:
  - `Beyond the Sword/Assets/XML/Units/CIV4BuildInfos.xml`
  - `Beyond the Sword/Assets/XML/Units/CIV4UnitInfos.xml`
  - `Beyond the Sword/Assets/XML/Terrain/CIV4ImprovementInfos.xml`
  - `Beyond the Sword/Assets/XML/Terrain/CIV4TerrainSchema.xml`
  - `Beyond the Sword/Assets/XML/Art/CIV4ArtDefines_Improvement.xml`
- DLL:
  - `third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvInfos.{h,cpp}`
  - `CvPlot.{h,cpp}`, `CvCity.{h,cpp}`, `CvGameTextMgr.cpp`
  - `CvUnitAI.{h,cpp}`
- Positive control: `BUILD_GRAND_COLOSSEUM_BTG`,
  `IMPROVEMENT_GRAND_COLOSSEUM_BTG`, and its AI placement path.
- Validation: `tools/test_gate.ps1`, `tools/build_civ4_dll.ps1 -NoDeploy`,
  focused `tools/tests`, and `docs/MANUAL_SMOKE_TESTS.md`.

## Locked Mechanics

### Global rules

- Diagonals count as adjacent.
- Natural terrain, features, peaks, and water count regardless of ownership.
- Infrastructure and resources count only when owned by the landmark owner.
- Same logical landmark types require plot distance four.
- Sacred Grove variants form one logical type.
- Commercial District is exempt from distance four but cannot touch another
  Commercial District.
- Placement requires an owned, workable city-radius plot and never destroys a
  resource.
- Pillaging destroys the landmark completely.
- Each player's first copy of each logical type receives a strong one-time AI
  score bonus.
- AI evaluates landmarks against traditional actions with deterministic scans
  and stable tie-breaking.

### Great Engineer

- **Industrial Zone** — Factory art; owned workable flat land; zero base
  Production. Adjacent owned Watermill `+3 Production`, Workshop `+2`, and
  Mine/Quarry `+1`.
- **Naval Foundry** — Iron Works art; owned workable flat coastal land;
  `+2 Production` on its tile. Owned water tiles within radius two gain
  `+1 Production`; owned water-resource tiles gain another `+2`. Overlapping
  Foundry auras do not stack.

### Great Scientist

- **Research Campus** — Observatory art; direct base Research to the city
  working the Campus, before normal city Research modifiers.
- Campus on Tundra/Snow: `+3 Research`.
- Adjacent Peak `+3`, Jungle `+2`, Hill `+1`, Tundra `+1`, Snow `+2`.
- Applicable components stack, including Jungle Hills and Snow Peaks.

### Great Merchant and Venetian Merchant Prince

- **Commercial District** — Roman Forum art; must border an owned city center.
  That city-center adjacency supplies `+6` generic Commerce. Adjacent owned
  Cottage/Hamlet/Village/Town supplies `+1/+2/+3/+4` Commerce. Districts may
  not directly touch.
- **Grand Bazaar** — Market art; adjacent owned happiness resource supplies
  `+4` generic Commerce and another `+2` when connected by its valid
  improvement.
- Both use normal plot Commerce and remain slider-dependent.
- The Venetian Merchant Prince receives both Builds additively and retains
  Founder, roads, Grand Colosseum, and every other current action. Its AI
  evaluates both Merchant landmarks separately without weakening Founder
  safety.

### Great Prophet

- **Sacred Grove** — the variant is selected from the owner's state religion
  at construction and never changes afterward.
- Seven religion variants use stock Jewish, Christian, Islamic, Hindu,
  Buddhist, Confucian, and Taoist Shrine models.
- The no-state-religion variant uses Shinto Naiku art.
- Adjacent Forest/Jungle supplies `+1 Food`.
- An owned Forest/Jungle with Forest Preserve supplies another `+1 Food` and
  `+1 Commerce`.
- Adjacent water supplies `+1 Food`.
- Outputs appear on the Grove tile.

## Generic DLL/XML Architecture

1. Extend `CvImprovementInfo` and `CIV4TerrainSchema.xml` with optional
   landmark data. Defaults must preserve every existing improvement.
2. Store a logical group, minimum group distance, city-adjacency and coastal
   requirements, state-religion selector, worked-city commerce, radius-water
   effects, and adjacency rule arrays.
3. Keep cache stream read/write order symmetric and version-safe for freshly
   generated XML caches.
4. Enforce placement centrally through `CvPlot::canBuild` helpers so humans
   and AI share the same legality.
5. Calculate source-tile adjacency and target-tile radius yields in
   `CvPlot::calculateImprovementYieldChange`.
6. Add Research Campus commerce in the worked-plot portion of
   `CvCity::getBaseCommerceRateTimes100`, before Research modifiers.
7. Refresh affected plots/cities when improvements, ownership, terrain,
   features, bonuses, or city assignments change.
8. Generate help from XML-backed mechanics rather than hard-coded landmark
   descriptions where practical.
9. Add a shared deterministic Great Person landmark planner. Reject unsafe,
   unreachable, unworkable, resource-destroying, and replacement-negative
   candidates; score current effects plus bounded future adjacency.
10. Keep detailed candidate scoring behind the repository's DLL debug logging
    convention.

## InfoType And Art Append Order

Append only, in this order:

1. Industrial Zone
2. Naval Foundry
3. Research Campus
4. Commercial District
5. Grand Bazaar
6. Sacred Grove — no state religion
7. Sacred Grove — Judaism
8. Sacred Grove — Christianity
9. Sacred Grove — Islam
10. Sacred Grove — Hinduism
11. Sacred Grove — Buddhism
12. Sacred Grove — Confucianism
13. Sacred Grove — Taoism

BuildInfo and ImprovementInfo order must match. Existing entries, especially
Grand Colosseum, must not move because savegames persist numeric IDs.

## Proposed Implementation Steps

1. Freeze Grand Colosseum behavior with positive-control tests.
2. Add schema and `CvImprovementInfo` support with neutral defaults.
3. Add generic placement, spacing, adjacency, radius, commerce, and refresh
   helpers.
4. Implement Commercial District end-to-end first.
5. Add both Merchant Builds to Great Merchant and Venetian Merchant Prince;
   integrate separate deterministic AI scoring.
6. Add Grand Bazaar.
7. Add default and one religious Sacred Grove, then all remaining variants.
8. Add Industrial Zone.
9. Add Naval Foundry and non-stacking radius aura.
10. Add Research Campus direct Research.
11. Add help text, art definitions, exact contracts, and manual smoke cases.
12. Run focused tests, full XML validation, and compile-only DLL validation.

## Validation Plan

- Parse all touched XML and validate schema references.
- Assert append-only BuildInfo/ImprovementInfo ordering.
- Assert exact unit Build sets, especially additive Venetian preservation.
- Assert all art tags and stock NIF paths resolve through accepted packed-stock
  aliases.
- Add focused tests for spacing, ownership, religion variants, non-stacking
  radius behavior, direct Research, and AI deterministic ordering where
  practical.
- Run `.\tools\test_gate.ps1`.
- Run `.\tools\build_civ4_dll.ps1 -NoDeploy`; do not use the deploying DLL
  gate and do not run the installer.
- User installs.
- Manual fresh-game validation: map rendering and icons, placement legality,
  every adjacency value, city Research modifiers, pillage destruction,
  ownership transitions, save/reload, AI autoplay, and two-client multiplayer
  OOS checks.

## Documentation Updates Required

- Add this plan to `docs/index.md`.
- Extend `docs/MANUAL_SMOKE_TESTS.md`.
- Update `ARCHITECTURE.md` if the generic improvement-commerce/yield layer
  changes the durable runtime architecture.
- Update roster exact contracts only for the approved additive Venetian Builds
  and any required Great Person work-rate changes.

## Risks / Rollback

- Main risks: XML cache stream mismatch, stale adjacent yields, AI path
  nondeterminism, double-counted auras, Research entering after modifiers,
  accidental resource replacement, packed-stock NIF rendering differences,
  and numeric InfoType movement.
- Safe rollback: remove only appended InfoTypes and generic neutral-default DLL
  fields together. Do not reorder retained entries or touch unrelated roster
  work.
- Fresh games are mandatory after adding or removing these InfoTypes.

## Assumptions And Open Questions

- Approved mechanics above are final and require no further design decision.
- Existing stock building models are acceptable map-improvement art, subject
  to installed-game rendering validation.
- Manual gameplay, rendering, installation, and multiplayer acceptance remain
  human-owned gates.

## Completion Checklist

- [x] Trusted runtime paths and Grand Colosseum precedent verified.
- [x] Mechanics and Venetian preservation contract approved.
- [x] Generic schema and DLL support implemented.
- [x] All BuildInfo, ImprovementInfo, art, text, and unit permissions appended.
- [x] Human and AI placement paths implemented.
- [x] Exact regression contracts updated.
- [x] Automated XML and compile-only DLL gates pass.
- [ ] User installation completed.
- [ ] Manual fresh-game and multiplayer acceptance recorded.

### Playtest correction — instant construction

- [x] Match Great Prophet, Scientist, Merchant, and Engineer work rates to the
  proven Great Artist/Venetian Merchant Prince value (`1000`).
- [x] Add a regression test requiring every landmark builder to retain that
  positive work rate alongside zero-time, unit-consuming BuildInfo records.

### Multiplayer turn-processing optimization

- [x] Skip Naval Foundry radius scans when the player owns no Foundry.
- [x] Reject nonmatching Sacred Grove religion variants before whole-map AI
  candidate scans.
- [x] Skip danger/pathfinding work when a candidate's maximum possible score
  cannot beat the current deterministic winner.
- [x] Add static regression contracts for all three performance fast paths.

### UX enhancement — exact output preview + breakdown

Approved option: **"Exact total + adjacency breakdown (Recommended)."** Surface
an exact plot-specific total plus a short contributor breakdown in both tooltip
paths, sharing one authoritative preview so text can never drift from gameplay.

- [x] Added the shared, read-only `CvPlot::buildLandmarkPreview` +
  `LandmarkBreakdown` struct, filled from the same scans that back the runtime
  helpers. Runtime `getLandmarkAdjacencyYield`, `getLandmarkResearchCampusValue`,
  and `getLandmarkWaterAuraYield` were refactored to reuse those scans
  (`accumulateLandmarkAdjacency`, `accumulateLandmarkResearchCampus`,
  `getNavalFoundryAuraTileValue`) — no second rule implementation.
- [x] Added `CvGameTextMgr::setLandmarkPreviewHelp`, rendering exact totals and
  per-contributor counts for every landmark type, including the exact Research
  Campus value (Research is not a native plot yield, which is why it was missing).
- [x] Build-action tooltip (`CvDLLWidgetData::parseActionHelp`, `MISSION_BUILD`)
  appends a "Projected landmark output" block and suppresses the duplicate
  generic native-yield delta line for landmark Builds.
- [x] Map plot tooltip (`CvGameTextMgr::setPlotHelp`) appends a "Current landmark
  output" block for an existing revealed landmark, using revealed
  improvement/owner semantics (no unrevealed-data leak).
- [x] Naval Foundry aura preview is exact effective (non-stacking): water tiles
  already covered by another owned Foundry are excluded.
- [x] Localized heading/label keys added to `ZZZ_CIV4GameText_Landmarks.xml`
  following the English-duplicated-across-languages convention.
- [x] Focused regression tests added in
  `tools/tests/test_great_person_landmarks.py` (both tooltip paths, Research
  exact preview, per-landmark breakdown, non-duplication/reuse contract,
  localization keys, read-only/no-RNG checks).
- [x] `.\tools\test_gate.ps1 -All -CheckDll` rebuilds/deploys the payload DLL;
  Release and payload DLL SHA-256 confirmed identical.
- [ ] Installed-game manual acceptance: build-hover and built-map-hover checks
  per landmark (see `docs/MANUAL_SMOKE_TESTS.md`), plus save/reload and MP OOS.

### Map model scale correction

The 13 new landmarks reuse stock building NIFs, which render at roughly city
size at the stock `fScale=1.0`. Map scale is pinned to `0.5` so each landmark
reads as an improvement rather than a city. Interface rendering is unchanged.
Tracked in full in
[`2026-07-13-landmark-scale-installer-reliability.md`](2026-07-13-landmark-scale-installer-reliability.md).

- [x] Set `fScale` to `0.5` for all 13 new landmark art records in
`CIV4ArtDefines_Improvement.xml`.
- [x] Keep `fInterfaceScale` at `1.0` (Civilopedia/button size unchanged).
- [x] Leave the pre-existing Grand Colosseum at `fScale=1.5` (not shrunk).
- [x] Add exact art-scale regression tests (all 13 map scales `0.5`, all
interface scales `1.0`, Grand Colosseum `1.5`) in
`tools/tests/test_great_person_landmarks.py`.
- [ ] Installed-game manual acceptance: confirm the 13 landmarks render at
half size (readable, no longer city-sized) at normal and strategic zoom,
buttons/Civilopedia stay normal size, and Grand Colosseum is visually
unchanged (see `docs/MANUAL_SMOKE_TESTS.md`).

## Readiness

**Ready for implementation: Yes.**

**Ready for merge/deploy: No.** Implementation, automated gates, user-run
installation, fresh-game rendering/mechanics checks, AI autoplay, save/reload,
and fresh two-client multiplayer acceptance remain required.
