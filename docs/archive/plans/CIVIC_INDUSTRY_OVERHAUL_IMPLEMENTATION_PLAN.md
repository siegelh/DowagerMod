# Civic And Industry Overhaul Implementation Plan

## Purpose

This document is the implementation spec for the civic rebalance and the new industry-building framework.

It is intended to be the single reference for:

1. XML civic changes
2. DLL/schema work for industry gating
3. building content definitions
4. art and button requirements
5. implementation order and testing focus

## Design Goal

Move the economy away from:

- unlock one civic
- spam one improvement family everywhere

and toward:

- choose an empire doctrine
- specialize each city locally by terrain and resources

The guiding split is:

1. civics define doctrine
2. core industries define local tile specialization
3. luxury industries define local resource specialization
4. composite industries define higher-order city identity

## High-Level Design Principles

1. Economic civics should stay strong, but be narrower.
2. The most important tile-side bonuses should live on local buildings, not empire-wide civics.
3. Each city should only support a limited number of industry identities.
4. Temporary retile exploits must not create permanent benefits.
5. Luxury resources should matter much more in city planning.
6. Composite industries should reward sensible combinations, not every possible pair.
7. Core industries own tile effects.
8. Luxury and composite industries are primarily building-side effects in v1.

## Scope For This Pass

Included:

1. economy civic retune
2. labor/support civic retune where needed
3. new industry framework in DLL and XML
4. first-pass core industries
5. first-pass luxury industries
6. first-pass composite industries
7. placeholder 3D art plan
8. button art plan

Excluded from this pass:

1. wonder-based civic unlock changes
2. custom 3D models
3. exact local bonus tile-yield DLL hook for luxury industries
4. fort/logistics specialization system
5. civ-specific improvement specialization pass

## Next-Layer Supply Chain Expansion

This section captures the next major implementation layer to sit on top of the already-implemented
core/luxury/composite framework.

### Design Goal

Move the economy from:

- raw local luxury
- local industry building
- local composite building

to:

- raw local resource
- local processing industry
- synthetic tradable industrial good
- downstream composite sector
- corporation founded from mature sector presence

### Layer Overview

The full economic chain becomes:

1. raw local resource
2. local processing industry
3. synthetic tradable good
4. composite industry
5. corporation

### Categories And Limits

Keep:

1. `CORE` industries at `2` per city
2. local processing industries at `3` per city
3. composite industries at `3` per city

Add:

1. each specific composite industry building type is limited to `1` per civilization

Implementation note:

- local processing industries continue to use the existing `LUXURY` industry category mechanically
- provision industries are processed-goods industries and share the same per-city cap

### Synthetic Goods

Synthetic goods are true `BonusInfo` entries that:

1. are tradable
2. do not spawn naturally on the map
3. give no direct happiness
4. give no direct health
5. give no direct tile yield
6. exist only because active buildings produce them

### Refined Luxury Goods

| Source Building | Raw Input | Synthetic Good |
| --- | --- | --- |
| `Dye Works` | `Dye` | `Fine Dyes` |
| `Furriers' Hall` | `Fur` | `Fine Furs` |
| `Jeweler's Quarter` | `Gems` | `Cut Gems` |
| `Minting House` | `Gold` | `Gold Bullion` |
| `House of Incense` | `Incense` | `Temple Incense` |
| `Ivory Carvers' Atelier` | `Ivory` | `Ivory Carvings` |
| `Silk Weaver's Workshop` | `Silk` | `Fine Silk` |
| `Silversmiths' Hall` | `Silver` | `Worked Silver` |
| `Spice Exchange` | `Spices` | `Spice Blends` |
| `Confectioners' Guild` | `Sugar` | `Confections` |
| `Vintners' Guild` | `Wine` | `Vintage Wine` |
| `Whale Oil Chandlery` | `Whale` | `Lamp Oil` |
| `Playwrights' Guild` | `Drama` | `Stage Plays` |
| `Recording House` | `Music` | `Master Recordings` |
| `Film Studio District` | `Movies` | `Film Prints` |

### Provision Goods

Food resources should not be treated as prestige luxuries. They become a parallel provision chain.

| Provision Building | Raw Inputs | Synthetic Good |
| --- | --- | --- |
| `Millers' Guild` | `Wheat`, `Corn`, `Rice` | `Flour` |
| `Smokehouse` | `Cow`, `Pig`, `Sheep`, `Deer` | `Cured Meats` |
| `Cannery` | `Fish`, `Clam`, `Crab` | `Preserved Seafood` |
| `Fruit Preservers` | `Banana` | `Fruit Preserves` |

Provision building effect direction:

1. health
2. food retention
3. small gold
4. modest production where appropriate

### Composite Industries V2

Composite industries no longer depend on same-city luxury industry buildings.

They depend on connected synthetic goods available through the city trade network.

Rules:

1. composites may be built in any connected city with access to the required synthetic inputs
2. imported synthetic goods count
3. exported surplus can be traded to other civilizations
4. if access to a required synthetic good is lost, the composite remains but becomes inactive
5. if access returns, the composite reactivates automatically

### Composite Industry Remap

| Composite Industry | Required Synthetic Goods |
| --- | --- |
| `Royal Garments House` | `Fine Silk` + `Fine Dyes` |
| `Noble Tailors' Hall` | `Fine Silk` + `Fine Furs` |
| `Court Regalia Atelier` | `Fine Silk` + `Ivory Carvings` |
| `Dyed Fur Salon` | `Fine Dyes` + `Fine Furs` |
| `Crown Jeweler` | `Gold Bullion` + `Cut Gems` |
| `Royal Mint` | `Gold Bullion` + `Worked Silver` |
| `Gemcutters' Exchange` | `Worked Silver` + `Cut Gems` |
| `Regal Treasures Court` | `Gold Bullion` + `Ivory Carvings` |
| `Aromatics Quarter` | `Temple Incense` + `Spice Blends` |
| `Grand Banquet Hall` | `Vintage Wine` + `Confections` |
| `Confectioners' Exchange` | `Confections` + `Spice Blends` |
| `Ceremonial Cellars` | `Vintage Wine` + `Temple Incense` |
| `Festival Market` | `Vintage Wine` + `Spice Blends` |
| `Imperial Outfitters` | `Fine Furs` + `Ivory Carvings` |
| `Admiralty Curios House` | `Lamp Oil` + `Ivory Carvings` |
| `Navigator's Instrument Works` | `Lamp Oil` + `Worked Silver` |
| `Opera House` | `Stage Plays` + `Master Recordings` |
| `Cinema Palace` | `Stage Plays` + `Film Prints` |
| `Soundstage Complex` | `Master Recordings` + `Film Prints` |
| `Mass Entertainment Network` | `Stage Plays` + `Master Recordings` + `Film Prints` |

### New Provision / Hospitality Composites

| Composite Industry | Required Synthetic Goods |
| --- | --- |
| `Bakers' Exchange` | `Flour` + `Spice Blends` |
| `Festival Kitchens` | `Flour` + `Vintage Wine` |
| `Royal Kitchens` | `Cured Meats` + `Vintage Wine` |
| `Spiced Carvery` | `Cured Meats` + `Spice Blends` |
| `Maritime Supper Club` | `Preserved Seafood` + `Vintage Wine` |
| `Preserves Market` | `Fruit Preserves` + `Confections` |

### Corporation Redesign

Corporations should no longer be founded from raw map bonuses.

They should use:

1. empire-level composite industry presence as the founding gate
2. synthetic goods as the ongoing operating inputs

Recommended roster:

1. `Continental Provisions Company`
2. `Grand Hospitality Company`
3. `Imperial Luxury Exchange`
4. `Courtly Arts & Regalia Consortium`
5. `Aromatics & Festival Consortium`
6. `World Media Syndicate`

Recommended founding model:

1. a corporation defines a set of qualifying composite industry building classes
2. the empire must have an active minimum count from that set
3. the corporation-founder building then founds the corporation if no competitor blocks it

Recommended operating-input model:

1. corporation `PrereqBonuses` become synthetic goods rather than raw map resources
2. corporation scaling should count distinct synthetic-good types, or cap each type at a low value
3. do not allow unchecked linear scaling from many copies of one synthetic good

### Synthetic Good Art Direction

Synthetic goods need a distinct visual language from raw map bonuses.

Rules:

1. synthetic bonus buttons should use the base resource visual language where appropriate
2. synthetic bonus buttons should add a small gold star or seal in the top-right corner
3. city-menu resource requirement icons for synthetic goods should clearly resemble the source resource
4. for especially distinct goods, the icon can be more bespoke as long as the gold synthetic marker remains consistent

Examples:

1. `Gold Bullion`: gold-themed processed icon with gold synthetic marker
2. `Cut Gems`: faceted gem icon with gold synthetic marker
3. `Temple Incense`: incense/censer icon with gold synthetic marker
4. `Flour`: grain/flour sack icon with gold synthetic marker

Final implementation rule:

1. synthetic-good buttons should usually start from the source resource visual language and then push toward the processed form
2. a small gold star or seal should sit in the top-right corner to indicate a manufactured or secondary good
3. city-menu requirement icons should prioritize recognizability over novelty, so the relationship to the raw source stays obvious
4. especially distinct goods like `Gold Bullion`, `Cut Gems`, and `Lamp Oil` can be more bespoke as long as they keep the synthetic gold marker
5. this resource-art pass should be visually stronger than the first building-button pass; avoid flat or bland emblem-style buttons

### Bonus Art Defines

Synthetic goods should receive:

1. valid `BonusInfo` entries
2. valid `ArtDefine_Bonus` entries
3. custom `64x64` DDS buttons

World-model requirement is lower priority than button clarity because these goods do not naturally spawn on map tiles.

### Civilopedia Reference Page

Add an in-game reference page covering:

1. raw resource -> processing building -> synthetic good
2. synthetic good -> composite industry
3. corporation founding groups
4. note that synthetic goods give no direct happiness or health
5. note that losing access can deactivate composite industries

This should live in the text XML as a dedicated supply-chain reference entry so players can consult it during play.

Reference content should include:

1. raw resource -> processing building -> synthetic good
2. synthetic good -> composite industry
3. provision-industry mappings for staple, animal, marine, and preserved produce resources
4. corporation founding groups and required active-composite counts
5. a note that synthetic goods are tradable but provide no direct happiness or health on their own
6. a note that connected access can activate or deactivate downstream composite industries

### Corporation Naming Direction

For implementation, keep the straight descriptive corporation names:

1. `Continental Provisions Company`
2. `Grand Hospitality Company`
3. `Imperial Luxury Exchange`
4. `Courtly Arts & Regalia Consortium`
5. `Aromatics & Festival Consortium`
6. `World Media Syndicate`

Tone can be revisited later, but naming churn should not block the mechanical rollout.

## Files In Scope

Primary XML:

- `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/GameInfo/CIV4CivicInfos.xml`
- `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Buildings/CIV4BuildingClassInfos.xml`
- `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Buildings/CIV4BuildingInfos.xml`
- `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Buildings/CIV4BuildingsSchema.xml`
- `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Art/CIV4ArtDefines_Building.xml`
- `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Text/CIV4GameText_IndustryBuildings.xml`
- `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Assets/XML/GlobalDefinesAlt.xml`

Primary DLL:

- `third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvInfos.h`
- `third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvInfos.cpp`
- `third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvCity.h`
- `third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvCity.cpp`
- `third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvGameTextMgr.cpp`
- `third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvCityAI.cpp`

## Civic Rebalance

### Economy Civics

#### Mercantilism

Target identity:

- protected internal markets
- domestic trade webs
- export goods cities

Changes:

- `iTradeRoutes: 2 -> 1`
- keep `bNoForeignTrade = 1`
- keep `bNoForeignCorporations = 1`
- keep `HURRY_GOLD`
- `TradeYieldModifiers: [0,200,-50] -> [0,100,-25]`
- `CapitalCommerceModifiers: [25,0,0] -> [10,0,0]`

Tile effects:

- `Plantation +1 Commerce`
- `Winery +1 Commerce`
- `Fishing Boats +1 Commerce`
- `Whaling Boats +1 Commerce`

Remove:

- cottage-line hammer bonuses
- lumbermill bonus
- pasture bonus
- camp bonus
- castle-town bonus

Why:

Mercantilism should still reward connected internal exchange and export goods, but it should stop functioning as a broad second economy package for unrelated terrain.

#### Free Market

Target identity:

- open commercial growth
- fast town maturation
- trade-oriented scaling

Changes:

- `iTradeRoutes: 0 -> 1`
- `iCorporationMaintenanceModifier: -90 -> -35`
- `iImprovementUpgradeRateModifier: 200 -> 75`
- `TradeYieldModifiers: [0,0,0] -> [0,0,25]`

Tile effects:

- `Town +1 Food`

Remove:

- well bonus
- offshore platform bonus
- forest preserve bonus
- lumbermill bonus
- winery/plantation food-commerce package
- pasture/camp rewrites
- fishing/whaling bonus
- castle-town bonus

Why:

Free Market should remain the town-growth civic, but actual town-city payoff should now come mostly from `Exchange Hall` and related local specialization.

#### State Property

Target identity:

- centralized administration
- wide land empire
- focused industrial and military economy

Changes:

- `iGreatGeneralRateModifier: 150 -> 75`
- `iDistanceMaintenanceModifier: -100 -> -75`
- keep `bMilitaryFoodProduction = 1`
- keep `bNoCorporations = 1`
- add `iMilitaryProductionModifier = 10`
- remove capital yield modifier
- remove capital commerce modifier
- remove Palace happiness bonus
- keep Engineer specialist validity

Tile effects:

- `Workshop [1F,1H,0C]`
- `Watermill [1F,1H,0C]`
- `Mine [0F,1H,0C]`
- `Quarry [0F,1H,0C]`

Remove:

- well/offshore bonuses
- lumbermill bonus
- camp bonus
- pasture bonus
- fishing/whaling bonus
- fort bonus
- castle-town bonus

Why:

State Property should stay the best civic for wide industrial empires because of empire management and focused industrial support, not because it buffs most productive improvements at once.

#### Environmentalism

Target identity:

- large healthy cities
- specialist support
- eco-urban and preserve/windmill terrain

Changes:

- `iCorporationMaintenanceModifier: 50 -> 25`
- `iMilitaryProductionModifier: -50 -> -20`
- keep `bBuildingOnlyHealthy = 1`
- keep `bNoForeignCorporations = 1`
- `YieldModifiers: [20,0,0] -> [10,0,0]`
- keep `SpecialistExtraCommerces [0,1,0]`
- `Forest happiness: +3 -> +2`
- `Jungle happiness: +3 -> +1`

Building health changes:

- `Granary +1`
- `Market +1`
- `Aqueduct +2`
- `Grocer +2`
- `Supermarket +2`
- `Hospital +3`
- `Public Transportation +3`

Remove temple/monastery-style health spam.

Tile effects:

- `Forest Preserve [1F,0H,1C]`
- `Windmill [1F,0H,1C]`
- `Watermill [0F,0H,1C]`

Remove:

- well/offshore food bonuses
- boats food bonus
- plantation/winery/pasture/camp food package
- castle-town bonus

Why:

Environmentalism should create eco-cities and specialist cities, not turn nearly every rural improvement into a food explosion.

### Labor And Supporting Civics

#### Serfdom

Changes:

- `iWorkerSpeedModifier: 150 -> 100`
- `YieldModifiers [0,0,-10] -> [0,0,-5]`
- `TradeYieldModifiers [0,200,-200] -> [0,100,-100]`

Tile effects:

- keep `Pasture +1 Food`
- keep `Camp +1 Food`
- change `Plantation [1F,1H,-2C] -> [1F,0H,-1C]`

Remove:

- `Farm +1 Food`
- `Mine +1 Hammer`
- `Lumbermill +1 Hammer`

Why:

Serfdom should remain a strong rural labor civic without being a universal farm-plus-production answer.

#### Caste System

Changes:

- `CommerceModifiers [12,12,12,12] -> [5,5,5,5]`
- keep unlimited `Artist`
- keep unlimited `Scientist`
- keep unlimited `Merchant`
- keep unlimited `Priest`

Tile effects:

- `Farm +1 Food`

Why:

Caste System should be the food-to-specialist civic, not a flat generic commerce civic.

#### Emancipation

Changes:

- remove flat commerce on `Cottage/Hamlet/Village/Town`
- add `iImprovementUpgradeRateModifier +50`

Why:

Emancipation should accelerate cottage maturity rather than duplicating full commerce output.

#### Universal Suffrage

Changes:

- `Town +2 Hammer -> +1 Hammer`

#### Free Speech

Changes:

- `Town +4 Commerce -> +2 Commerce`

#### Theocracy

Changes:

- remove town hammer bonus

#### Representation

Changes:

- none in pass 1

## Industry Framework

### City Limits

Add to `GlobalDefinesAlt.xml`:

- `CORE_INDUSTRY_CITY_LIMIT = 1`
- `LUXURY_INDUSTRY_CITY_LIMIT = 3`
- `COMPOSITE_INDUSTRY_CITY_LIMIT = 1`

Why:

1. cities should make one major terrain commitment
2. resource cities should have room for multiple luxury branches
3. composite identity should stay rare

### New Building XML Tags

Add schema support for:

```xml
<IndustryCategory>NONE</IndustryCategory>
<bRequiresActiveLocalPrereqs>0</bRequiresActiveLocalPrereqs>

<LocalImprovementCountPrereqs>
  <LocalImprovementCountPrereq>
    <ImprovementTypes>
      <ImprovementType>IMPROVEMENT_MINE</ImprovementType>
      <ImprovementType>IMPROVEMENT_QUARRY</ImprovementType>
    </ImprovementTypes>
    <iMinCount>3</iMinCount>
  </LocalImprovementCountPrereq>
</LocalImprovementCountPrereqs>

<LocalBonusPrereqs>
  <LocalBonusPrereq>
    <BonusTypes>
      <BonusType>BONUS_SILK</BonusType>
    </BonusTypes>
    <iMinCount>1</iMinCount>
    <bImprovedOnly>1</bImprovedOnly>
    <bConnectedOnly>1</bConnectedOnly>
    <bCityRadiusOnly>1</bCityRadiusOnly>
  </LocalBonusPrereq>
</LocalBonusPrereqs>
```
### DLL Data Structures

Add new enum:

- `NO_BUILDING_INDUSTRY_CATEGORY`
- `BUILDING_INDUSTRY_CORE`
- `BUILDING_INDUSTRY_LUXURY`
- `BUILDING_INDUSTRY_COMPOSITE`

Add to `CvBuildingInfo`:

1. industry category
2. active-local-prereq flag
3. grouped local improvement count prereqs
4. grouped local bonus prereqs

### Construction Rules

In `CvCity::canConstruct`:

1. check category cap
2. check all local improvement count prereqs
3. check all local bonus prereqs
4. for composites, require prerequisite buildings in city and active

### Active/Inactive Behavior

Rule:

1. building remains in city if prereqs are later lost
2. building still consumes its category slot
3. building effects shut off while prereqs are not met
4. building reactivates automatically when prereqs return

Why:

This blocks retile exploits without destroying buildings or forcing one-time irreversible removals.

### Activation Implementation

Use a city-side active-state cache.

Add to `CvCity`:

1. `bool isBuildingLocalPrereqsMet(BuildingTypes eBuilding) const`
2. `bool isBuildingIndustryActive(BuildingTypes eBuilding) const`
3. `int getNumIndustryBuildings(BuildingIndustryCategoryTypes eCategory) const`
4. `void updateIndustryActivation(BuildingTypes eBuilding)`
5. `void updateAllIndustryActivations()`

Important detail:

`getNumActiveBuilding()` alone is not sufficient, because many building effects are processed incrementally.

Implementation approach:

1. maintain an activation cache per building
2. when activation changes, call `processBuilding(eBuilding, +/-count)` to apply or remove effects
3. have `getNumActiveBuilding()` respect both obsolescence and local active-state

### Activation Refresh Triggers

Run industry activation refresh on:

1. city acquired
2. building constructed or removed
3. improvement changed in city radius
4. bonus appearance/removal in city radius
5. connectivity change affecting local bonus prereqs
6. per-turn safety refresh in `CvCity::doTurn()`

### Help Text

Extend building help to show:

1. industry category
2. local improvement requirement
3. local bonus requirement
4. city cap
5. inactive-state warning if not currently satisfied

### AI

Update `CvCityAI` to:

1. prefer industries when a city clearly meets the terrain profile
2. avoid spending the sole core slot on weak fringe fits
3. value luxury industries based on local resource and city economy
4. value composites only when components are active

## Content Definitions

### Core Industries

Core industries have:

1. category `CORE`
2. no gold maintenance
3. tile effects plus modest building effects

#### Agrarian Board

- ids: `BUILDINGCLASS_AGRARIAN_BOARD`, `BUILDING_AGRARIAN_BOARD`
- requirements: `TECH_CIVIL_SERVICE`, `BUILDINGCLASS_GRANARY`, local improvements `4 Farms`, cost `110`
- tile effects: `Farm +1 Commerce`
- building effects: `+1 Food`, `+1 Health`

#### Exchange Hall

- ids: `BUILDINGCLASS_EXCHANGE_HALL`, `BUILDING_EXCHANGE_HALL`
- requirements: `TECH_CURRENCY`, `BUILDINGCLASS_MARKET`, local improvements `4 Cottage/Hamlet/Village/Town`, cost `140`
- tile effects: `Village +1 Commerce`, `Town +1 Commerce`
- building effects: `+10% Gold`, `+1 Merchant slot`

#### Mining Bureau

- ids: `BUILDINGCLASS_MINING_BUREAU`, `BUILDING_MINING_BUREAU`
- requirements: `TECH_METAL_CASTING`, `BUILDINGCLASS_FORGE`, local improvements `3 Mine/Quarry`, cost `140`
- tile effects: `Mine +1 Hammer`, `Quarry +1 Hammer`
- building effects: `+10% Production`, `+1 Engineer slot`

#### Manufactories Office

- ids: `BUILDINGCLASS_MANUFACTORIES_OFFICE`, `BUILDING_MANUFACTORIES_OFFICE`
- requirements: `TECH_GUILDS`, `BUILDINGCLASS_FORGE`, local improvements `3 Workshops`, cost `150`
- tile effects: `Workshop +1 Hammer`
- building effects: `+10% Military Production`, `-1 Health`

#### Forestry Commission

- ids: `BUILDINGCLASS_FORESTRY_COMMISSION`, `BUILDING_FORESTRY_COMMISSION`
- requirements: `TECH_REPLACEABLE_PARTS`, `BUILDINGCLASS_GRANARY` or `BUILDINGCLASS_COURTHOUSE`, local improvements `3 Lumbermill/Forest Preserve/Tree Nursery`, cost `150`
- tile effects: `Lumbermill +1 Hammer`, `Forest Preserve +1 Commerce`, `Tree Nursery +1 Food`
- building effects: `+1 Health`, `+2 Culture`

#### Hydraulic Office

- ids: `BUILDINGCLASS_HYDRAULIC_OFFICE`, `BUILDING_HYDRAULIC_OFFICE`
- requirements: `TECH_ENGINEERING`, `BUILDINGCLASS_AQUEDUCT`, local improvements `3 Watermill/Windmill`, cost `160`
- tile effects: `Watermill +1 Hammer`, `Windmill +1 Commerce`
- building effects: `+1 Health`, `+1 Hammer`

#### Estate Office

- ids: `BUILDINGCLASS_ESTATE_OFFICE`, `BUILDING_ESTATE_OFFICE`
- requirements: `TECH_CALENDAR`, `BUILDINGCLASS_MARKET`, local improvements `2 Plantation/Winery`, cost `130`
- tile effects: `Plantation +1 Commerce`, `Winery +1 Commerce`
- building effects: `+10% Gold`, `+1 Culture`

#### Pastoral Board

- ids: `BUILDINGCLASS_PASTORAL_BOARD`, `BUILDING_PASTORAL_BOARD`
- requirements: `TECH_HORSEBACK_RIDING`, `BUILDINGCLASS_GRANARY`, local improvements `2 Pastures`, cost `120`
- tile effects: `Pasture +1 Hammer`
- building effects: `+1 Food`, `+1 Health`

#### Frontier Lodge

- ids: `BUILDINGCLASS_FRONTIER_LODGE`, `BUILDING_FRONTIER_LODGE`
- requirements: `TECH_CURRENCY`, `BUILDINGCLASS_MARKET`, local improvements `2 Camps`, cost `120`
- tile effects: `Camp +1 Commerce`
- building effects: `+1 Happiness`, `+1 Culture`

#### Maritime Exchange

- ids: `BUILDINGCLASS_MARITIME_EXCHANGE`, `BUILDING_MARITIME_EXCHANGE`
- requirements: `TECH_COMPASS`, `BUILDINGCLASS_HARBOR`, local improvements `2 Fishing Boats/Whaling Boats`, cost `150`
- tile effects: `Fishing Boats +1 Commerce`, `Whaling Boats +1 Commerce`
- building effects: `+10% Trade Route Yield`, `+1 Health`

#### Energy Directorate

- ids: `BUILDINGCLASS_ENERGY_DIRECTORATE`, `BUILDING_ENERGY_DIRECTORATE`
- requirements: `TECH_COMBUSTION`, `BUILDINGCLASS_FACTORY`, local improvements `1 Well/Offshore Platform`, cost `200`
- tile effects: `Well +1 Hammer`, `Offshore Platform +1 Hammer`
- building effects: `+10% Production`, `-1 Health`

### Luxury Industries

Luxury industries have:

1. category `LUXURY`
2. mostly building-side effects
3. local resource requirement for map luxuries
4. empire resource requirement for `Drama`, `Music`, `Movies`

#### Dye Works

- ids: `BUILDINGCLASS_DYE_WORKS`, `BUILDING_DYE_WORKS`
- requirements: local improved connected `BONUS_DYE`, `TECH_CALENDAR`, `BUILDINGCLASS_MARKET`, cost `120`, maintenance `1`
- tile effects: none
- building effects: `+2 Culture`, `+10% Culture`, `+1 Happiness`

#### Furriers' Hall

- ids: `BUILDINGCLASS_FURRIERS_HALL`, `BUILDING_FURRIERS_HALL`
- requirements: local improved connected `BONUS_FUR`, `TECH_CURRENCY`, `BUILDINGCLASS_MARKET`, cost `120`, maintenance `1`
- tile effects: none
- building effects: `+2 Gold`, `+1 Culture`, `+1 Happiness`

#### Jeweler's Quarter

- ids: `BUILDINGCLASS_JEWELERS_QUARTER`, `BUILDING_JEWELERS_QUARTER`
- requirements: local improved connected `BONUS_GEMS`, `TECH_CURRENCY`, `BUILDINGCLASS_FORGE`, cost `140`, maintenance `1`
- tile effects: none
- building effects: `+10% Gold`, `+2 Culture`, `+1 Happiness`

#### Minting House

- ids: `BUILDINGCLASS_MINTING_HOUSE`, `BUILDING_MINTING_HOUSE`
- requirements: local improved connected `BONUS_GOLD`, `TECH_CURRENCY`, `BUILDINGCLASS_FORGE`, cost `140`, maintenance `1`
- tile effects: none
- building effects: `+15% Gold`, `+1 Happiness`

#### Perfumers' Sanctuary

- ids: `BUILDINGCLASS_PERFUMERS_SANCTUARY`, `BUILDING_PERFUMERS_SANCTUARY`
- requirements: local improved connected `BONUS_INCENSE`, `TECH_CALENDAR`, `BUILDINGCLASS_MARKET`, cost `120`, maintenance `1`
- tile effects: none
- building effects: `+2 Culture`, `+1 Happiness`, `+1 Priest slot`

#### Ivory Carvers' Atelier

- ids: `BUILDINGCLASS_IVORY_CARVERS_ATELIER`, `BUILDING_IVORY_CARVERS_ATELIER`
- requirements: local improved connected `BONUS_IVORY`, `TECH_CONSTRUCTION`, `BUILDINGCLASS_MARKET`, cost `140`, maintenance `1`
- tile effects: none
- building effects: `+2 Culture`, `+10% Gold`, `+1 Artist slot`

#### Silk Weaver's Workshop

- ids: `BUILDINGCLASS_SILK_WEAVERS_WORKSHOP`, `BUILDING_SILK_WEAVERS_WORKSHOP`
- requirements: local improved connected `BONUS_SILK`, `TECH_CALENDAR`, `BUILDINGCLASS_MARKET`, cost `120`, maintenance `1`
- tile effects: none
- building effects: `+2 Gold`, `+2 Culture`, `+1 Happiness`
#### Silversmiths' Hall

- ids: `BUILDINGCLASS_SILVERSMITHS_HALL`, `BUILDING_SILVERSMITHS_HALL`
- requirements: local improved connected `BONUS_SILVER`, `TECH_CURRENCY`, `BUILDINGCLASS_FORGE`, cost `140`, maintenance `1`
- tile effects: none
- building effects: `+10% Gold`, `+1 Culture`, `+1 Happiness`

#### Spice Exchange

- ids: `BUILDINGCLASS_SPICE_EXCHANGE`, `BUILDING_SPICE_EXCHANGE`
- requirements: local improved connected `BONUS_SPICES`, `TECH_CALENDAR`, `BUILDINGCLASS_MARKET`, cost `120`, maintenance `1`
- tile effects: none
- building effects: `+2 Gold`, `+1 Health`, `+1 Happiness`

#### Confectioners' Guild

- ids: `BUILDINGCLASS_CONFECTIONERS_GUILD`, `BUILDING_CONFECTIONERS_GUILD`
- requirements: local improved connected `BONUS_SUGAR`, `TECH_CALENDAR`, `BUILDINGCLASS_MARKET`, cost `120`, maintenance `1`
- tile effects: none
- building effects: `+2 Gold`, `+1 Health`, `+1 Happiness`

#### Vintners' Guild

- ids: `BUILDINGCLASS_VINTNERS_GUILD`, `BUILDING_VINTNERS_GUILD`
- requirements: local improved connected `BONUS_WINE`, `TECH_MONARCHY`, `BUILDINGCLASS_MARKET`, cost `120`, maintenance `1`
- tile effects: none
- building effects: `+2 Gold`, `+1 Culture`, `+1 Happiness`

#### Whale Oil Chandlery

- ids: `BUILDINGCLASS_WHALE_OIL_CHANDLERY`, `BUILDING_WHALE_OIL_CHANDLERY`
- requirements: local improved connected `BONUS_WHALE`, `TECH_COMPASS`, `BUILDINGCLASS_HARBOR`, cost `150`, maintenance `1`
- tile effects: none
- building effects: `+1 Hammer`, `+2 Gold`, `+1 Happiness`

#### Playwrights' Guild

- ids: `BUILDINGCLASS_PLAYWRIGHTS_GUILD`, `BUILDING_PLAYWRIGHTS_GUILD`
- requirements: empire-connected `BONUS_DRAMA`, `BUILDINGCLASS_THEATRE`, cost `160`, maintenance `1`
- tile effects: none
- building effects: `+4 Culture`, `+1 Happiness`, `+1 Artist slot`

#### Recording House

- ids: `BUILDINGCLASS_RECORDING_HOUSE`, `BUILDING_RECORDING_HOUSE`
- requirements: empire-connected `BONUS_MUSIC`, `BUILDINGCLASS_BROADCAST_TOWER`, cost `180`, maintenance `1`
- tile effects: none
- building effects: `+3 Culture`, `+2 Gold`, `+1 Happiness`

#### Film Studio District

- ids: `BUILDINGCLASS_FILM_STUDIO_DISTRICT`, `BUILDING_FILM_STUDIO_DISTRICT`
- requirements: empire-connected `BONUS_MOVIES`, `BUILDINGCLASS_BROADCAST_TOWER`, cost `200`, maintenance `1`
- tile effects: none
- building effects: `+3 Gold`, `+2 Culture`, `+1 Happiness`, `+10% Gold`

### Composite Industries

Composite industries have:

1. category `COMPOSITE`
2. no tile effects
3. maintenance `2` unless noted
4. `+3` generic GPP with no category

#### Royal Garments House

- ids: `BUILDINGCLASS_ROYAL_GARMENTS_HOUSE`, `BUILDING_ROYAL_GARMENTS_HOUSE`
- requirements: active `Silk Weaver's Workshop` and active `Dye Works`
- cost `180`
- building effects: `+25% Gold`, `+3 Culture`, `+1 Happiness`, `+1 Merchant slot`, `+3 GPP`

#### Noble Tailors' Hall

- ids: `BUILDINGCLASS_NOBLE_TAILORS_HALL`, `BUILDING_NOBLE_TAILORS_HALL`
- requirements: active `Silk Weaver's Workshop` and active `Furriers' Hall`
- cost `180`
- building effects: `+15% Gold`, `+10% Culture`, `+1 Happiness`, `+3 GPP`

#### Court Regalia Atelier

- ids: `BUILDINGCLASS_COURT_REGALIA_ATELIER`, `BUILDING_COURT_REGALIA_ATELIER`
- requirements: active `Silk Weaver's Workshop` and active `Ivory Carvers' Atelier`
- cost `190`
- building effects: `+15% Culture`, `+2 Gold`, `+1 Artist slot`, `+1 Happiness`, `+3 GPP`

#### Dyed Fur Salon

- ids: `BUILDINGCLASS_DYED_FUR_SALON`, `BUILDING_DYED_FUR_SALON`
- requirements: active `Dye Works` and active `Furriers' Hall`
- cost `180`
- building effects: `+20% Culture`, `+2 Gold`, `+1 Happiness`, `+3 GPP`

#### Crown Jeweler

- ids: `BUILDINGCLASS_CROWN_JEWELER`, `BUILDING_CROWN_JEWELER`
- requirements: active `Minting House` and active `Jeweler's Quarter`
- cost `200`
- building effects: `+25% Gold`, `+1 Happiness`, `+1 Merchant slot`, `+3 GPP`

#### Royal Mint

- ids: `BUILDINGCLASS_ROYAL_MINT`, `BUILDING_ROYAL_MINT`
- requirements: active `Minting House` and active `Silversmiths' Hall`
- cost `200`
- building effects: `+20% Gold`, `+3 Gold`, `+1 Happiness`, `+3 GPP`

#### Gemcutters' Exchange

- ids: `BUILDINGCLASS_GEMCUTTERS_EXCHANGE`, `BUILDING_GEMCUTTERS_EXCHANGE`
- requirements: active `Silversmiths' Hall` and active `Jeweler's Quarter`
- cost `190`
- building effects: `+15% Gold`, `+10% Culture`, `+1 Happiness`, `+3 GPP`

#### Regal Treasures Court

- ids: `BUILDINGCLASS_REGAL_TREASURES_COURT`, `BUILDING_REGAL_TREASURES_COURT`
- requirements: active `Minting House` and active `Ivory Carvers' Atelier`
- cost `200`
- building effects: `+10% Gold`, `+10% Culture`, `+1 Happiness`, `+1 Artist slot`, `+3 GPP`

#### Perfumers' Quarter

- ids: `BUILDINGCLASS_PERFUMERS_QUARTER`, `BUILDING_PERFUMERS_QUARTER`
- requirements: active `Perfumers' Sanctuary` and active `Spice Exchange`
- cost `180`
- building effects: `+10% Gold`, `+15% Culture`, `+1 Happiness`, `+3 GPP`

#### Grand Banquet Hall

- ids: `BUILDINGCLASS_GRAND_BANQUET_HALL`, `BUILDING_GRAND_BANQUET_HALL`
- requirements: active `Vintners' Guild` and active `Confectioners' Guild`
- cost `180`
- building effects: `+15% Gold`, `+2 Happiness`, `+1 Health`, `+3 GPP`

#### Confectioners' Exchange

- ids: `BUILDINGCLASS_CONFECTIONERS_EXCHANGE`, `BUILDING_CONFECTIONERS_EXCHANGE`
- requirements: active `Confectioners' Guild` and active `Spice Exchange`
- cost `180`
- building effects: `+15% Gold`, `+1 Happiness`, `+1 Health`, `+3 GPP`

#### Ceremonial Cellars

- ids: `BUILDINGCLASS_CEREMONIAL_CELLARS`, `BUILDING_CEREMONIAL_CELLARS`
- requirements: active `Vintners' Guild` and active `Perfumers' Sanctuary`
- cost `180`
- building effects: `+10% Gold`, `+10% Culture`, `+1 Happiness`, `+1 Priest slot`, `+3 GPP`

#### Festival Market

- ids: `BUILDINGCLASS_FESTIVAL_MARKET`, `BUILDING_FESTIVAL_MARKET`
- requirements: active `Vintners' Guild` and active `Spice Exchange`
- cost `180`
- building effects: `+15% Gold`, `+2 Culture`, `+1 Happiness`, `+3 GPP`
#### Imperial Outfitters

- ids: `BUILDINGCLASS_IMPERIAL_OUTFITTERS`, `BUILDING_IMPERIAL_OUTFITTERS`
- requirements: active `Furriers' Hall` and active `Ivory Carvers' Atelier`
- cost `190`
- building effects: `+15% Gold`, `+10% Culture`, `+1 Happiness`, `+3 GPP`

#### Admiralty Curios House

- ids: `BUILDINGCLASS_ADMIRALTY_CURIOS_HOUSE`, `BUILDING_ADMIRALTY_CURIOS_HOUSE`
- requirements: active `Whale Oil Chandlery` and active `Ivory Carvers' Atelier`
- cost `190`
- building effects: `+10% Gold`, `+1 Hammer`, `+1 Happiness`, `+3 GPP`

#### Navigator's Instrument Works

- ids: `BUILDINGCLASS_NAVIGATORS_INSTRUMENT_WORKS`, `BUILDING_NAVIGATORS_INSTRUMENT_WORKS`
- requirements: active `Whale Oil Chandlery` and active `Silversmiths' Hall`
- cost `190`
- building effects: `+15% Gold`, `+1 Engineer slot`, `+1 Happiness`, `+3 GPP`

#### Opera House

- ids: `BUILDINGCLASS_OPERA_HOUSE_INDUSTRY`, `BUILDING_OPERA_HOUSE_INDUSTRY`
- requirements: active `Playwrights' Guild` and active `Recording House`
- cost `220`
- building effects: `+20% Culture`, `+2 Happiness`, `+1 Artist slot`, `+3 GPP`

#### Cinema Palace

- ids: `BUILDINGCLASS_CINEMA_PALACE`, `BUILDING_CINEMA_PALACE`
- requirements: active `Playwrights' Guild` and active `Film Studio District`
- cost `220`
- building effects: `+15% Culture`, `+10% Gold`, `+2 Happiness`, `+3 GPP`

#### Soundstage Complex

- ids: `BUILDINGCLASS_SOUNDSTAGE_COMPLEX`, `BUILDING_SOUNDSTAGE_COMPLEX`
- requirements: active `Recording House` and active `Film Studio District`
- cost `220`
- building effects: `+10% Gold`, `+10% Culture`, `+2 Happiness`, `+3 GPP`

#### Mass Entertainment Network

- ids: `BUILDINGCLASS_MASS_ENTERTAINMENT_NETWORK`, `BUILDING_MASS_ENTERTAINMENT_NETWORK`
- requirements: active `Playwrights' Guild`, active `Recording House`, and active `Film Studio District`
- cost `280`
- maintenance `3`
- building effects: `+25% Culture`, `+15% Gold`, `+3 Happiness`, `+1 Artist slot`, `+1 Merchant slot`, `+3 GPP`

## Improvement Coverage

Covered by core industries:

- `Farm`
- `Cottage/Hamlet/Village/Town`
- `Mine`
- `Quarry`
- `Workshop`
- `Lumbermill`
- `Forest Preserve`
- `Tree Nursery`
- `Windmill`
- `Watermill`
- `Plantation`
- `Winery`
- `Pasture`
- `Camp`
- `Fishing Boats`
- `Whaling Boats`
- `Well`
- `Offshore Platform`

Intentionally not covered:

- `Fort`
- civ-specific unique improvements
- helper and placeholder improvements

## Art Plan

### Button File Requirements

Use individual buttons first.

Specifications:

1. `64x64`
2. `.dds`
3. `DXT3` with alpha
4. stored under `Assets/Art/Interface/Buttons/Buildings/Industries/`
5. directly referenced in `CIV4ArtDefines_Building.xml`

Atlas packing can be deferred until content stabilizes.

### Visual Language

1. core industries: earth, steel, timber palette
2. luxury industries: jewel, lacquer, cloth, perfume palette
3. composite industries: royal trim, deeper contrast, gilded accents

### 3D Placeholder Policy

Do not block implementation on custom NIF creation.

Use existing building art defs as placeholders in v1, then replace selectively later.

### Core Industry Placeholder Art

- `Agrarian Board -> ART_DEF_BUILDING_GRANARY`
- `Exchange Hall -> ART_DEF_BUILDING_ENGLISH_STOCK_EXCHANGE`
- `Mining Bureau -> ART_DEF_BUILDING_FORGE`
- `Manufactories Office -> ART_DEF_BUILDING_GERMAN_ASSEMBLY_PLANT`
- `Forestry Commission -> ART_DEF_BUILDING_COURTHOUSE`
- `Hydraulic Office -> ART_DEF_BUILDING_AQUEDUCT`
- `Estate Office -> ART_DEF_BUILDING_MARKET`
- `Pastoral Board -> ART_DEF_BUILDING_STABLE`
- `Frontier Lodge -> ART_DEF_BUILDING_STABLE`
- `Maritime Exchange -> ART_DEF_BUILDING_CARTHAGE_COTHON`
- `Energy Directorate -> ART_DEF_BUILDING_FACTORY`

### Luxury Industry Placeholder Art

- `Dye Works -> ART_DEF_BUILDING_PERSIAN_APOTHECARY`
- `Furriers' Hall -> ART_DEF_BUILDING_MARKET`
- `Jeweler's Quarter -> ART_DEF_BUILDING_MALI_MINT`
- `Minting House -> ART_DEF_BUILDING_MALI_MINT`
- `Perfumers' Sanctuary -> ART_DEF_BUILDING_PERSIAN_APOTHECARY`
- `Ivory Carvers' Atelier -> ART_DEF_BUILDING_FRENCH_SALON`
- `Silk Weaver's Workshop -> ART_DEF_BUILDING_FRENCH_SALON`
- `Silversmiths' Hall -> ART_DEF_BUILDING_MALI_MINT`
- `Spice Exchange -> ART_DEF_BUILDING_MARKET`
- `Confectioners' Guild -> ART_DEF_BUILDING_GROCER`
- `Vintners' Guild -> ART_DEF_BUILDING_GROCER`
- `Whale Oil Chandlery -> ART_DEF_BUILDING_HARBOR`
- `Playwrights' Guild -> ART_DEF_BUILDING_THEATRE`
- `Recording House -> ART_DEF_BUILDING_BROADCAST_TOWER`
- `Film Studio District -> ART_DEF_BUILDING_BROADCAST_TOWER`

### Composite Industry Placeholder Art

- `Royal Garments House -> ART_DEF_BUILDING_FRENCH_SALON`
- `Noble Tailors' Hall -> ART_DEF_BUILDING_FRENCH_SALON`
- `Court Regalia Atelier -> ART_DEF_BUILDING_FRENCH_SALON`
- `Dyed Fur Salon -> ART_DEF_BUILDING_FRENCH_SALON`
- `Crown Jeweler -> ART_DEF_BUILDING_BANK`
- `Royal Mint -> ART_DEF_BUILDING_BANK`
- `Gemcutters' Exchange -> ART_DEF_BUILDING_BANK`
- `Regal Treasures Court -> ART_DEF_BUILDING_FRENCH_SALON`
- `Perfumers' Quarter -> ART_DEF_BUILDING_PERSIAN_APOTHECARY`
- `Grand Banquet Hall -> ART_DEF_BUILDING_ROMAN_FORUM`
- `Confectioners' Exchange -> ART_DEF_BUILDING_GROCER`
- `Ceremonial Cellars -> ART_DEF_BUILDING_ROMAN_FORUM`
- `Festival Market -> ART_DEF_BUILDING_MARKET`
- `Imperial Outfitters -> ART_DEF_BUILDING_FRENCH_SALON`
- `Admiralty Curios House -> ART_DEF_BUILDING_CUSTOM_HOUSE`
- `Navigator's Instrument Works -> ART_DEF_BUILDING_CUSTOM_HOUSE`
- `Opera House -> ART_DEF_BUILDING_GREEK_ODEON`
- `Cinema Palace -> ART_DEF_BUILDING_THEATRE`
- `Soundstage Complex -> ART_DEF_BUILDING_AMERICAN_MALL`
- `Mass Entertainment Network -> ART_DEF_BUILDING_AMERICAN_MALL`

### Button Concepts

Core industry button concepts:

- `Agrarian Board`: ledger tablet over wheat sheaf
- `Exchange Hall`: coin stacks with sealed account scroll
- `Mining Bureau`: pickaxe and ore cart wheel
- `Manufactories Office`: hammer over industrial gear
- `Forestry Commission`: axe, pine bough, timber round
- `Hydraulic Office`: waterwheel with blue current arc
- `Estate Office`: grape cluster and plantation leaves on parchment
- `Pastoral Board`: shepherd crook and ram horns
- `Frontier Lodge`: fur bundle and trap
- `Maritime Exchange`: anchor, crate, and wave stripe
- `Energy Directorate`: derrick silhouette over metal gear
Luxury industry button concepts:

- `Dye Works`: dye vat and folded cloth ribbon
- `Furriers' Hall`: trimmed mantle clasp
- `Jeweler's Quarter`: cut gem in gold setting
- `Minting House`: struck coin and die stamp
- `Perfumers' Sanctuary`: perfume bottle with incense plume
- `Ivory Carvers' Atelier`: carved cameo and burin
- `Silk Weaver's Workshop`: loom shuttle and silk thread
- `Silversmiths' Hall`: silver goblet and ingot
- `Spice Exchange`: spice scoop and powder bowls
- `Confectioners' Guild`: sugar cone and sweets box
- `Vintners' Guild`: wine press and goblet
- `Whale Oil Chandlery`: lamp with whale-tail crest
- `Playwrights' Guild`: theatre mask and quill
- `Recording House`: gramophone horn and record
- `Film Studio District`: film reel and spotlight

Composite button concepts:

- `Royal Garments House`: silk bolt over royal robe
- `Noble Tailors' Hall`: fur collar and gold needle
- `Court Regalia Atelier`: robe clasped with ivory ornament
- `Dyed Fur Salon`: colored pelt over dye ribbon
- `Crown Jeweler`: crown above gem and coin
- `Royal Mint`: crossed gold and silver coinage
- `Gemcutters' Exchange`: jewel over silversmith hammer
- `Regal Treasures Court`: chest, tusk carving, coin glow
- `Perfumers' Quarter`: perfume vial over spice smoke
- `Grand Banquet Hall`: goblet, confection, feast trim
- `Confectioners' Exchange`: sugared confection dusted with spice
- `Ceremonial Cellars`: censer beside amphora
- `Festival Market`: pennant, wine, spice bowl
- `Imperial Outfitters`: fur mantle and ivory ornament
- `Admiralty Curios House`: whale-oil lamp and ivory figurine
- `Navigator's Instrument Works`: sextant with silver fittings
- `Opera House`: opera mask and gramophone flourish
- `Cinema Palace`: stage mask transitioning into film reel
- `Soundstage Complex`: microphone, reel, stage lights
- `Mass Entertainment Network`: mask, record, reel, broadcast rays

### Button Creation Workflow

1. create one reusable Civ4-style 64x64 PSD/Krita template
2. keep border/alpha consistent across the whole set
3. use one dominant silhouette per button
4. add warm rim lighting and dark edge vignette
5. export to DDS `DXT3`
6. wire buttons directly in art defines

### Art Reference Policy

Use public-domain or permissive reference imagery as source material for custom-painted buttons.

Do not use random scraped web images directly as final in-game buttons.

## Text And Civilopedia

Create `CIV4GameText_IndustryBuildings.xml`.

For each new building add:

1. `TXT_KEY_BUILDING_*`
2. `TXT_KEY_BUILDING_*_PEDIA`
3. `TXT_KEY_BUILDING_*_STRATEGY`

Each strategy entry should explicitly distinguish:

1. tile effect
2. building effect
3. local requirement

## Implementation Order

### Phase 1

XML-only civic retune.

Why:

The new building system needs room to matter.

### Phase 2

DLL/schema framework for industries.

Add:

1. industry categories
2. local improvement prereqs
3. local bonus prereqs
4. active/inactive state
5. city caps
6. help text
7. AI support

### Phase 3

Add core industries.

Why:

This rehomes most tile specialization first.

### Phase 4

Add luxury industries.

Why:

This makes local resources matter at city level.

### Phase 5

Add composite industries.

Why:

This creates memorable city identities and resource-combo incentives.

### Phase 6

Add text and art wiring.

### Phase 7

Add custom button DDS assets.

## Testing Focus

Questions to answer in first playtest:

1. does one civic still force a single empire-wide tile spam answer
2. is `Serfdom` still too dominant
3. does `Caste System` now have a real farm-specialist role again
4. are core industry slot decisions meaningful
5. do local resource cities feel distinct enough
6. are composite industries rewarding without being mandatory
7. do any luxury industries need stronger effects
8. does the AI build sensible industries for the terrain

## Mandatory Test Gate Reminder

After editing XML under:

- `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML`

or DLL source under:

- `third_party/beyond-the-sword-sdk/CvGameCoreDLL`

run:

```powershell
.\tools\test_gate.ps1
```

Do not report those edits complete until the gate passes.
