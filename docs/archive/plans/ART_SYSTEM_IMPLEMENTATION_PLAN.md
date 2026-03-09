# Art System Implementation Plan

## Objective

Add a new Great Artist action that creates non-map Art pieces represented as tradeable bonus resources.

The system must:

1. avoid tile improvement gameplay for Art creation
2. support diplomacy/resource trade incentives
3. support corporation gating based on distinct Art pieces
4. be stable under save/load, city capture/raze, and AI turn processing

## Core Product Decisions

1. Start with `40` Art pieces, not `1000`.
2. Represent Art pieces as normal `BonusInfo` resources (`BONUS_ART_*`).
3. Creation is city-based and uses a Great Artist construct action (internal dummy building trigger), not map improvements.
4. Phase 1 uses deterministic auto-selection from eligible Art pool (no popup choice yet).
5. Corp 7 founding is gated by `5` connected Art pieces via `ConnectedBonusPrereqs` on HQ building.
6. AI is allowed to trade Art by a targeted DLL rule for Art bonuses (otherwise AI will never trade unique one-copy resources).

## Why This Architecture

### Why resources

Using bonuses gives us, for free:

1. network connectivity behavior
2. import/export and diplomacy trade UI
3. city bonus consumption for prereqs
4. corporation prereq compatibility

### Why a dummy building trigger

Great People already support `MISSION_CONSTRUCT` in cities.

Using a hidden construct-only building lets us trigger a city-only action without adding a brand-new mission/command pipeline in DLL for the first iteration.

Player-facing behavior remains "Create Masterpiece".

### Why no popup choice in Phase 1

Popup-driven player choice introduces extra synchronization and persistence complexity.

Phase 1 stabilizes state transitions first:

1. consume Great Artist
2. pick valid unowned piece deterministically
3. grant free bonus to city
4. notify player

Once stable, add choice UX in Phase 2.

## Data Model

### Art resources

Add `BONUS_ART_*` entries in `CIV4BonusInfos.xml`:

1. `BonusClassType` initially reuses existing class (`BONUSCLASS_GENERAL`)
2. `iConstAppearance = 0`, `iTilesPer = 0`, `iPlayer = 0` to prevent map spawning
3. baseline `iHappiness = 1`
4. neutral yields (no tile balance impact)

### Trigger building

Add one hidden building in `CIV4BuildingInfos.xml`:

1. type example: `BUILDING_ART_MASTERPIECE_TRIGGER`
2. `iCost = -1` so cities cannot build it from production queue
3. no yields/effects
4. Great Artist can construct it via `UnitInfo.Buildings`

Runtime flow removes this building immediately after triggering Art assignment.

### Artist action

Update `UNIT_ARTIST` in `CIV4UnitInfos.xml`:

1. add `BUILDING_ART_MASTERPIECE_TRIGGER` under `Buildings`
2. keep existing Great Artist actions (culture bomb, etc.)

### Registry metadata

Add Python data module (new):

1. `CvArtCatalogData.py`
2. defines ordered list of eligible Art bonus types
3. optional metadata for later screen tabs (era, medium, region, set tags)

No new DLL serialized fields in Phase 1.

## Runtime Flow (Phase 1)

1. Player moves Great Artist into own city.
2. Player clicks `Create Masterpiece` (construct mission).
3. `onBuildingBuilt` catches `BUILDING_ART_MASTERPIECE_TRIGGER`.
4. System finds candidate Art pieces where no player currently has the bonus.
5. If candidates exist:
   1. pick one with `CyGame().getSorenRandNum` (deterministic RNG)
   2. `city.changeFreeBonus(eArtBonus, +1)`
   3. remove trigger building (`setNumRealBuilding(..., 0)`)
   4. send message with gained artwork name/icon
6. If no candidates exist:
   1. fallback compensation (culture + gold)
   2. remove trigger building

## Trade Rules

### Problem

Default AI trade rule requires more than one tradeable copy for AI-to-others resource deals.

For unique Art (single copy), AI otherwise never trades Art.

### Fix

DLL change in `CvPlayer::canTradeItem` (`TRADE_RESOURCES` branch):

1. treat Art bonuses as tradeable with `>0` copies (same rule humans already effectively get)
2. keep existing logic for non-Art bonuses

Art detection method:

1. Phase 1: explicit helper `isArtBonus(eBonus)` by type prefix `BONUS_ART_`
2. Optional later: dedicated bonus class check if you add `BONUSCLASS_ART`

## Corporation 7 Gating

Re-activate Corp 7 as Art corporation.

Use HQ building prereq instead of hard-coding 5 specific bonuses:

1. on `BUILDING_CORPORATION_7`, add one `ConnectedBonusPrereq`
2. that prereq includes all `BONUS_ART_*` types in `BonusTypes`
3. set `iMinCount = 5`

This gives "any 5 distinct Art pieces" behavior with existing DLL logic.

## Art Advisor Screen Plan

### Phase 2 screen (read-only first)

New screen module patterned after Industry Advisor:

1. `Screens/CvArtAdvisor.py`
2. enum id like `5001`
3. open from HUD button and optional hotkey

Tabs:

1. `Collection`: owned Art bonuses and providers
2. `Prestige`: summary score and era diversity
3. `Diplomacy`: current imports/exports for Art bonuses

### Integration points

1. add `ArtAdvisorButton` in real main interface implementation:
   - `Assets/Art/Leaderheads/new/petromod_v1/Assets/Python/Screens/CvMainInterface.py`
2. extend `EntryPoints/CvScreenUtilsInterface.py` composite dispatcher to include Art screen utils (same pattern as Industry)

## Bug Risk Matrix

### R1: Great Artist consumed but no Art granted

Mitigation:

1. trigger handling in one function with try/fail-safe
2. grant/compensate before cleanup return
3. explicit message on failure path

### R2: Duplicate Art piece creation

Mitigation:

1. central selector checks active ownership across all players before assignment
2. deterministic selection call site only
3. debug log of selected piece, owner, city, turn

### R3: AI never trades Art

Mitigation:

1. targeted `canTradeItem` exception for Art bonuses
2. validation tests for AI->human trade availability

### R4: Corp gate not matching displayed rules

Mitigation:

1. single XML source of truth (`ConnectedBonusPrereqs` list)
2. in-game help text generated from same configured threshold

### R5: Save/load instability

Mitigation:

1. no new serialized DLL arrays in Phase 1
2. behavior derived from city free bonuses + normal game state
3. regression tests on save/load across creation/trade/capture states

### R6: City raze/capture edge cases

Mitigation:

1. rely on native free bonus ownership transfer/removal behavior
2. explicit tests for capture and raze while art is imported/exported

## Phased Delivery

## Phase 0: Scaffolding

1. Add feature toggle define/text hooks.
2. Add minimal debug logging helper for Art events.
3. Add catalog data module with 40 items.

Exit criteria:

1. No gameplay impact when toggle off.

## Phase 1: Stable Core Loop

1. Add Art bonus resources (40).
2. Add construct-trigger building.
3. Add Great Artist action to construct trigger building.
4. Implement Python handler for assignment + cleanup + notifications.
5. Add AI trade exception for Art bonuses in DLL.

Exit criteria:

1. Human can create Art repeatedly from different artists.
2. No tile improvements required.
3. Art appears in trade table as resource.
4. AI can offer/request Art in diplomacy.
5. Save/load around create/trade remains stable.

## Phase 2: UX Layer

1. Add Art Advisor screen (read-only).
2. Add HUD button integration.
3. Add civilopedia/help text for Art system.

Exit criteria:

1. Player can inspect collection state and trade exposure without digging through city screens.

## Phase 3: Corp 7 Integration

1. Re-activate Corp 7 XML.
2. Add HQ prereq: any 5 connected Art bonuses.
3. Tune corp outputs for cultural/economic role.

Exit criteria:

1. Corp 7 cannot be founded below threshold.
2. Imported Art counts correctly toward threshold.

## Phase 4: Advanced Choice and Sets

1. Replace auto-assignment with 3-choice draft UI at creation time.
2. Add collection sets and prestige bonuses.
3. Add AI valuation improvements for Art trading/founding behavior.

Exit criteria:

1. Choice flow is stable in single-player and network multiplayer.
2. No duplicate grants from race conditions.

## Testing Plan

## Automated/Scripted Gate

After XML/DLL edits, run:

1. `./tools/test_gate.ps1`

## Manual scenarios (required)

1. Create Art in owned city; verify resource appears in trade list.
2. Repeat until pool exhausted; verify fallback behavior.
3. Export Art to AI; cancel deal; verify resource returns.
4. Capture city containing free Art bonus; verify ownership transfer.
5. Raze city containing free Art bonus; verify removal behavior.
6. Found corp 7 with exactly 5 Art, then with 4 Art (should fail).
7. Save/load during each above state.

## Instrumentation

Add temporary log lines (guarded by debug flag):

1. trigger fired
2. candidate pool size
3. selected bonus type
4. grant city/player
5. post-grant availability count

## Scope Guardrails

1. Do not add 1000 bonuses in initial implementation.
2. Do not add new serialized DLL state until core loop is proven.
3. Do not add multiplayer popup choice before deterministic baseline is stable.

## Recommended Next Action

Implement Phase 1 first as a vertical slice, then freeze and playtest before adding choice UI.
