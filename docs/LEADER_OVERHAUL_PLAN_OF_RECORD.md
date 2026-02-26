# Leader Overhaul Plan Of Record

## Status
Accepted as the default methodology for all future leader+civilization overhauls.

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
