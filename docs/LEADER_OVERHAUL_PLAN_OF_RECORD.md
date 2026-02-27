# Leader Overhaul Plan Of Record

## Status
Accepted as the default methodology for all future leader+civilization overhauls.

## Invocation Protocol (Use Every Overhaul Request)
When starting an overhaul task, use this exact opener:
- `Follow docs/LEADER_OVERHAUL_PLAN_OF_RECORD.md and README.md strictly before proposing or implementing.`

Before making changes, provide:
- a checklist echo of exactly which plan-of-record items will be applied.

After making changes, provide:
- a docs-compliance summary mapping each applied checklist item to concrete file edits.

## Overhaul Prompt Template (Copy/Paste)
Use this prompt to enforce process:
```text
Follow docs/LEADER_OVERHAUL_PLAN_OF_RECORD.md and README.md strictly before proposing or implementing.

Target leader/civ: <LEADER> / <CIV>
Phase: <Planning|Implementation>

First, list the exact checklist items you will apply from the plan-of-record.
Then do the work.
Afterward, provide a docs-compliance summary with file references for each checklist item.
```

## Overhaul Tracker (Living)
Use this section to track actual implementation status and avoid duplicate/partial passes.

### Completed
- `LEADER_HATSHEPSUT` / `CIVILIZATION_EGYPT_EIGHTEENTH_DYNASTY`
- `LEADER_WASHINGTON` / `CIVILIZATION_AMERICA_FOUNDING_REPUBLIC`
- `LEADER_TOKUGAWA` / `CIVILIZATION_JAPAN`

### In Progress
- None

### Planned (Not Started)
- Fill per planning sessions. Keep entries leader-specific and civ-specific.

## Per-Leader Checklist (Required)
For each overhaul, record a short design brief with:
- historical thesis (1-2 sentences)
- gameplay thesis (win-shape and power spike timing)
- trait channels selected (legacy + new mixed)
- UU decision: `KEEP` / `MODIFY` / `REPLACE` + why
- UB decision: `KEEP` / `MODIFY` / `REPLACE` + why
- unique improvement decision (if any): include gating and cap
- art sources actually used (workspace/external) with copied destination paths
- UI clarity checks (Civilopedia, tooltip, build help, trait text)
- AI impact notes (valuation/pathing/build incentives where relevant)

## Proposal Requirements (Planning Gate, Mandatory)
Every proposal must include all of the following before implementation:
- `UU/UB Fit Verdict`:
- explicit `KEEP` / `MODIFY` / `REPLACE` decision for both existing UU and existing UB
- short historical + gameplay justification for each
- `Rare Improvement Justification` (if proposing a civ-unique tile improvement):
- why this civ specifically merits one
- why the mechanic is not better expressed as trait/civic/building instead
- proposed gating (terrain/feature/tech/civ-lock/cap) and target cap
- `Art Feasibility Pass`:
- search both workspace and external library before suggesting replacements
- if suggesting new art, include candidate source path(s) and intended destination path(s) in workspace
- never reference external paths directly from XML
- `UI Exposure Plan`:
- state where each non-obvious effect will be surfaced (build help, pedia, civic/trait tooltip)

## Core Rule
Design must use the full trait toolbox as one unified system.

Do not separate design choices into:
- "legacy trait options"
- "new trait options"

Instead, mix both categories as needed based on:
- historical grounding
- gameplay identity
- balance
- clarity/readability for players

## Scope
This applies to all leader-specific overhauls in DowagerMod (Beyond the Sword).

## Trait Surface To Consider Every Time
### Scalar/base trait fields
- `iHealth`
- `iHappiness`
- `iMaxAnarchy`
- `iUpkeepModifier`
- `iLevelExperienceModifier`
- `iGreatPeopleRateModifier`
- `iGreatGeneralRateModifier`
- `iDomesticGreatGeneralRateModifier`
- `iMaxGlobalBuildingProductionModifier`
- `iMaxTeamBuildingProductionModifier`
- `iMaxPlayerBuildingProductionModifier`
- `ExtraYieldThresholds`
- `TradeYieldModifiers`
- `CommerceChanges`
- `CommerceModifiers`
- `FreePromotions`
- `FreePromotionUnitCombats`

### Mapped trait channels
- `ImprovementYieldChanges`
- `ImprovementTerrainYieldChanges`
- `ImprovementFeatureYieldChanges`
- `BuildingYieldChanges`
- `BuildingCommerceChanges`
- `SpecialistYieldChanges`
- `SpecialistCommerceChanges`
- `BonusYieldChanges`
- `RouteYieldChanges`

## Design Standard
Each leader plan should explicitly evaluate both scalar/base and mapped channels, then choose a curated subset.

Not every leader needs every channel, but every channel class should be considered before finalizing the design.

## Notes
- Historical fidelity is a hard requirement.
- Distinct playstyle per leader+civilization is a hard requirement.
- Avoid overly generic trait bundles when a more specific historical mechanic is feasible.

## Creativity Guardrails
Use these to keep designs differentiated and high-flavor:
- No copy-paste trait shape across leaders, even if numbers differ.
- At least one signature mechanic per leader that another leader does not share.
- If using unique tile improvements, reserve for select leaders only and make gating meaningful.
- Prefer asymmetry with clear counterplay over flat stat stacking.
- Keep power visible to players: every major mechanic needs clear text surfacing.

## Naming Standard
- Avoid placeholder labels (`Node`, `Generic`, etc.).
- Use era-authentic terms when possible (for example, `Jokamachi`).
- Build action names should be verbs that read naturally in UI (for example, `Establish Jokamachi`).

## UI/UX Clarity Standard
- Any hard cap must appear in at least:
- build help text
- Civilopedia entry
- Any worked-vs-BFC bonus must explicitly say:
- `worked tile` or `within city radius (BFC)`
- When mechanics are trait-driven, ensure trait text exposes the effect in readable bullets.

## Tooltip Format Safety (Required)
- When using `gDLL->getText(...)` formatting paths (especially civic help text), avoid `%+d` placeholders in XML text keys.
- Use `%d` for numeric placeholders unless the specific call site is confirmed to support sign formatting safely.
- Known failure mode:
- raw format tokens appear in UI (for example, `%+d%c`) instead of resolved values.
- Current safe keys for improvement-city-commerce civic text use `%d%c`:
- `TXT_KEY_CIVIC_IMPROVEMENT_CITY_COMMERCE_WORKED`
- `TXT_KEY_CIVIC_IMPROVEMENT_CITY_COMMERCE_BFC`
- Regression check after text changes:
- open Civic screen and verify no unresolved `%` tokens appear in tooltip/help text.

## Art Sourcing Protocol (Required)
- Every leader+civ redesign must search all available art sources before finalizing UU/UB/UIV decisions.
- Default goal: use art-driven differentiation whenever feasible (units, buildings, improvements, buttons, flags/teamcolor), not text-only/mechanical differentiation.
- Mandatory search locations:
- `C:\DowagerMod` workspace art paths.
- `C:\Users\Harrison\Downloads\civ4mods-code` external source library.
- If an asset is selected from outside the workspace, copy it into the correct workspace path first.
- XML may only reference assets that already exist inside the workspace.
- Never point XML directly at `C:\Users\Harrison\Downloads\civ4mods-code`.
- For each imported external asset, record:
- original source path
- destination workspace path
- XML tag(s) updated to use it
- Preference order:
- Reuse high-quality existing workspace art first.
- Import from external library when it materially improves historical identity/flavor.

## UU/UB Fit Review Policy (Required)
- Before changing uniques, each leader+civ plan must explicitly review currently assigned UU and UB for historical fit and gameplay fit.
- Default rule:
- Keep existing UU/UB when they are historically plausible for the era and mechanically coherent.
- Modify existing UU/UB when the concept is good but tuning/theme needs adjustment.
- Replace UU/UB only when they are clearly anachronistic, inaccurate, or incompatible with the intended era identity.
- Every plan must record a per-unique decision:
- `KEEP`, `MODIFY`, or `REPLACE`
- with one short justification for each.

## Unique Tile Improvement Pattern (Required Consideration)
- Leader/civ designs may include civilization-specific tile improvements when historically justified.
- Pattern supports a unique worker build action, constrained placement rules, tile yields, and optional city-range aura effects.
- Example template:
- `IMPROVEMENT_SPHINX` with `BUILD_SPHINX`.
- Placement constrained to flat desert tiles (no hills/peaks, additional constraints as needed).
- Direct tile output such as `+3` Gold.
- Optional city effect such as `+1` Culture to cities that can work the tile (inside city workable radius), implemented in DLL.
- If a city-range aura is used, update AI logic so AI understands build value and placement.
- If a city-range aura is used, update UI/help text so players can see both tile and city bonus behavior clearly.
- Civilization-specific improvements must follow the same art protocol:
- search all available art first
- copy external assets into workspace before XML reference
- Rarity/gating rule:
- Unique tile improvements are intentionally rare and are not expected for every civilization.
- When used, they should be gated by at least one hard control (examples: era-appropriate tech, terrain/feature restrictions, civilization/leader lock, and/or per-player build cap).
- Preferred default is a low cap (for example 1-3 total), unless historical justification supports broader use.
- If a cap is introduced, UI text must state the cap clearly.

## City Bonus Modes For Unique Improvements
- Both modes are part of the supported design toolkit and must be considered during overhauls:
- `Worked Tile` mode:
- City bonus is granted only if a citizen is actively working the tile.
- This is the default/recommended mode for most designs.
- `In BFC` mode:
- City bonus is granted if the improvement is inside the city workable radius, whether worked or not.
- Use this mode only for intentional passive-aura designs.
- Recommendation standard:
- Prefer `Worked Tile` for clarity, balance, and player agency.
- Use `In BFC` sparingly for monument/influence style mechanics with explicit historical flavor.

## Implementation Status (Current)
- Engine support is implemented for improvement-driven **city commerce** bonuses in both modes:
- `Worked Tile` and `In BFC`.
- Current attach points implemented:
- `Trait`
- `Civic`
- Supported commerce outputs:
- Gold, Science, Culture, Espionage
- Tooltips/civilopedia help text support has been added for these new trait/civic channels.
- Design note:
- Additional attach points (Building/Civilization/Leader direct tables) remain valid future extensions.

## XML Usage Pattern (Implemented)
- Trait example:
```xml
<ImprovementCityCommerceChangesWorked>
  <ImprovementCityCommerceChangeWorked>
    <ImprovementType>IMPROVEMENT_TOWN</ImprovementType>
    <ImprovementCommerces>
      <iCommerce>0</iCommerce> <!-- Gold -->
      <iCommerce>1</iCommerce> <!-- Science -->
      <iCommerce>0</iCommerce> <!-- Culture -->
      <iCommerce>0</iCommerce> <!-- Espionage -->
    </ImprovementCommerces>
  </ImprovementCityCommerceChangeWorked>
</ImprovementCityCommerceChangesWorked>
```
- Civic example:
```xml
<ImprovementCityCommerceChangesBFC>
  <ImprovementCityCommerceChangeBFC>
    <ImprovementType>IMPROVEMENT_TOWN</ImprovementType>
    <ImprovementCommerces>
      <iCommerce>0</iCommerce>
      <iCommerce>0</iCommerce>
      <iCommerce>1</iCommerce>
      <iCommerce>0</iCommerce>
    </ImprovementCommerces>
  </ImprovementCityCommerceChangeBFC>
</ImprovementCityCommerceChangesBFC>
```

- Terrain/feature-conditional improvement yield example (trait):
```xml
<ImprovementTerrainYieldChanges>
  <ImprovementTerrainYieldChange>
    <ImprovementType>IMPROVEMENT_FARM</ImprovementType>
    <TerrainType>TERRAIN_DESERT</TerrainType>
    <ImprovementYields>
      <iYield>1</iYield>
      <iYield>0</iYield>
      <iYield>0</iYield>
    </ImprovementYields>
  </ImprovementTerrainYieldChange>
</ImprovementTerrainYieldChanges>
<ImprovementFeatureYieldChanges>
  <ImprovementFeatureYieldChange>
    <ImprovementType>IMPROVEMENT_FARM</ImprovementType>
    <FeatureType>FEATURE_FLOOD_PLAINS</FeatureType>
    <ImprovementYields>
      <iYield>1</iYield>
      <iYield>0</iYield>
      <iYield>0</iYield>
    </ImprovementYields>
  </ImprovementFeatureYieldChange>
</ImprovementFeatureYieldChanges>
```
