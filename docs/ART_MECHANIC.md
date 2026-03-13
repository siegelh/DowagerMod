# Art Mechanic (Art Masterpieces System)

Status: `Current` (last verified March 13, 2026).

DowagerMod replaces the vanilla Great Artist culture-bomb flow with an "Art Masterpieces" inventory that acts like a tradable collection of globally unique bonuses. This page explains what players experience, where the code lives, and how to extend or debug the system safely.

## Player-Facing Loop

| Step | What the player does | Implementation notes |
| --- | --- | --- |
| 1. Earn a Great Artist | Any source of Great Artists works. | Uses the standard `UNIT_ARTIST` entry. |
| 2. Move the Great Artist into one of their own cities and select **Curate Masterpiece** | The unit action builds the hidden `BUILDING_ART_MASTERPIECE_TRIGGER`. | `CIV4UnitInfos.xml` grants Great Artists a building mission that consumes the unit when started. |
| 3. The trigger building instantly removes itself and the Art system rolls a unique piece | `CvArtMasterpieceSystem.onBuildingBuilt` intercepts completion, deletes the dummy building, and picks an unclaimed `BONUS_ART_xxx`. If the global catalog is exhausted the city gains 2000 culture instead. |
| 4. The owning civilization permanently adds that piece to its Art Gallery | Ownership is stored per-player, not per-city, so it survives conquest and razing. |
| 5. Benefits are applied immediately | Each distinct piece is worth +1 global happiness (soft-capped at 10) plus set bonuses: +1 happiness for every era with ≥3 owned pieces and for every art type with ≥4 owned pieces, up to +8 total. |
| 6. Players trade or gift Art like any other bonus | DLL rules allow both humans and AI to trade single-copy Art bonuses so inventory can circulate diplomatically. |
| 7. Track progress in the Art Advisor | The HUD exposes an **Art** button (to the right of the Industry button) that opens `CvArtAdvisor`, showing era/type collections, happiness breakdowns, and each masterpiece’s description and button art. |

### Key takeaways for players

- There are 200 masterpieces spanning Antiquity → Contemporary eras. Once one is claimed it is removed from the global pool until traded, so racing matters.
- Art is an empire-level inventory item; it never sits on the map or ties to a specific city tile.
- The Curate action consumes the Great Artist immediately. There is no partial progress or construction queue.
- Trading, gifting, and demanding Art all work even if a civ owns only one copy of that piece because the DLL overrides the usual “need one spare copy” rule for all `BONUS_ART_*` types.

## Implementation Map

| Layer | Files | Responsibilities |
| --- | --- | --- |
| XML – Bonuses | `CoreFiles/.../Assets/XML/Terrain/CIV4BonusInfos.xml` (`BONUS_ART_001` – `BONUS_ART_200`); `CoreFiles/.../Assets/XML/Art/CIV4ArtDefines_Bonus.xml`; `CoreFiles/.../Assets/XML/Text/ZZZ_ART_Masterpieces_Text.xml` | Declares every masterpiece as a bonus with no map placement (`iPlacementOrder = -1`, `iConstAppearance = 0`) and provides button/gallery art plus localized text pulled from Wikidata. |
| XML – Trigger building | `CoreFiles/.../Assets/XML/Buildings/CIV4BuildingInfos.xml` (dummy `BUILDING_ART_MASTERPIECE_TRIGGER` + class info) | Hidden building that exists only to fire the Python hook and to anchor Civilopedia entries. |
| XML – Unit action | `CoreFiles/.../Assets/XML/Units/CIV4UnitInfos.xml` (`UNIT_ARTIST`) | Adds the Curate Masterpiece action to the Great Artist’s build list so it can spawn the trigger building. |
| Python – Runtime system | `CoreFiles/.../Assets/Python/CvArtMasterpieceSystem.py`; `CvEventManager.py` | Owns all game-time behavior: selecting pieces, persisting ownership, migrating legacy city bonuses, reconciling happiness per player, broadcasting UI notifications, and writing/reading state in `CyGame().getScriptData()` with `__ARTSYS` markers. `CvEventManager` calls into the system on game start, load, begin-player-turn, onUpdate, and when buildings complete to keep state consistent. |
| Python – Data tables | `CoreFiles/.../Assets/Python/CvArtMasterpieceData.py` | Auto-generated table that pairs each `BONUS_ART_*` with its era bucket, art type (Painting/Sculpture), HUD button, and gallery texture. |
| Python – Advisor screen | `CoreFiles/.../Assets/Python/Screens/CvArtAdvisor.py`; `CvArtScreenUtils.py`; `CoreFiles/.../Assets/Python/EntryPoints/CvScreenUtilsInterface.py`; HUD file under `Assets/Art/Leaderheads/new/petromod_v1/.../CvMainInterface.py` | Renders the Art Advisor (screen id 5000), supports screen dispatch, and wires the HUD **Art** button. The button is only shown when `CvArtAdvisor` imports successfully. |
| DLL | `third_party/beyond-the-sword-sdk/CvPlayer.cpp`, `CvPlayerAI.cpp`, `CvGameTextMgr.cpp` | Adds `isArtMasterpieceBonus()` detection (prefix match on `BONUS_ART_`). This lets AI offer Art with zero spare copies, lets diplomacy screens show Art correctly, and tunes text output. |
| Tooling | `tools/generate_art_masterpieces.py`; `docs/art_masterpiece_sources.csv` | Pipeline that refreshes `CvArtMasterpieceData.py`, `ZZZ_ART_Masterpieces_Text.xml`, and button/gallery art references from the curated CSV source list. Run the script after editing the CSV. |

## State & Persistence

- **Storage:** `CvArtMasterpieceSystem` writes ownership + claimed flags + applied happiness per player into `CyGame().getScriptData()` between `__ARTSYS_BEGIN__` / `__ARTSYS_END__`. Save games therefore keep Art collections without additional DLL serialization work.
- **Reconciliation hooks:** `onGameStart`, `onLoadGame`, and `onBeginPlayerTurn` all re-run `_run_full_reconcile()`, which:
  - migrates any leftover free Art bonuses that might still live on cities from pre-inventory builds into the inventory store,
  - rebuilds the claimed-piece cache from ownership,
  - recalculates and reapplies the correct global happiness delta for each alive player.
- **Safety net:** If a save somehow loses the Art block, the system simply treats all pieces as unclaimed until the next Curate or manual repair, so there is no hard crash—only loss of collection data.

## Benefits & Set Bonuses

- `+1` global happiness per distinct owned masterpiece, capped at 10 from this source.
- Set bonuses (`TXT_KEY_ART_MASTERPIECE_SET_BONUS_HELP`):
  - `+1` global happiness for every era where you own ≥3 pieces.
  - `+1` global happiness for every art type where you own ≥4 pieces.
  - Total set happiness capped at 8, so the mechanic tops out at `18` happiness empire-wide (10 base + 8 sets).
- `CvArtAdvisor` surfaces the exact breakdown so players understand where the next breakpoint lies.

## Trading, Diplomacy, and Corporations

- All 200 masterpieces are standard bonuses, so they appear in diplomacy, resource lists, and trade deals.
- Custom DLL code lets both human and AI players trade single-copy Art, removing the normal spare-copy requirement. The AI also considers Art in valuation loops (`CvPlayerAI.cpp`).
- Corporations and industry composites can reference Art bonuses like any other synthetic good. Currently the Courtly Arts & Regalia Consortium expects connected regalia composites rather than Art pieces directly, but future XML/DLL work can safely gate on `BONUS_ART_*` types.

## UI & Advisor Details

- The HUD **Art** button lives next to the Industry advisor button and calls `CvArtAdvisor.getArtAdvisor().interfaceScreen()` through `CvArtScreenUtils`.
- The advisor displays:
  - Collection summary: total pieces, base happiness, set bonuses, cap progress (`BASE_HAPPINESS_CAP = 10`).
  - Era rows ordered by `CvArtMasterpieceData.ART_ERA_ORDER`, showing owned vs. total pieces.
  - Individual cards for every masterpiece with icon, art type, year, and ownership flag.
- The advisor can also view other civ galleries for diplomacy scouting; it hides barbarian or minor civs automatically.

## Extending or Debugging the System

1. **Adding or editing masterpieces**
   - Update `docs/art_masterpiece_sources.csv`.
   - Run `tools/generate_art_masterpieces.py` to regenerate `CvArtMasterpieceData.py`, text, and button/gallery references.
   - Add or update the referenced TGA/DDS art in `CoreFiles/.../Assets/Art/Interface/...`.
   - Update `CIV4BonusInfos.xml` if new bonus types are introduced.
2. **Changing happiness math**
   - Edit `_compute_happiness_from_state` and `_compute_set_bonus_from_state` in `CvArtMasterpieceSystem.py`.
   - Update `TXT_KEY_ART_MASTERPIECE_SET_BONUS_HELP` to match.
3. **Troubleshooting missing pieces**
   - Use the Art Advisor to confirm ownership.
   - Inspect the save’s script data via `CyGame().getScriptData()` to ensure the `__ARTSYS` block exists.
   - `_migrate_bonus_backed_art_to_inventory()` removes any lingering city-level `FreeBonus` counts; if Art is stuck on a city you can trigger a reconcile by loading the game or ending a turn.
4. **HUD issues**
   - Verify `CvArtAdvisor.py` imports correctly; the HUD logs `CvUtil.pyPrint("CvArtAdvisor import failed; Art button disabled.")` if it cannot load.
   - `CvScreenUtilsInterface.py` must include `CvArtScreenUtils.getScreenUtils()` in the dispatcher so hotkeys and screen events route to the advisor.

## Validation expectations

- Documentation-only edits do not require running `tools/test_gate.ps1`, but any XML or Python changes to the Art system must run the gate.
- Gameplay changes to Art should also follow `docs/MANUAL_SMOKE_TESTS.md`, especially the “Art” checklist (open advisor, curate a piece, trade it, and ensure happiness updates).

