# Trait Capabilities Roadmap (Planned)

This document tracks potential new leader-trait capabilities to add in the future.
Scope target: `Beyond the Sword` content and SDK paths first.

## Status

- Mixed status: several channels are now implemented in DLL/XML, and several remain planned.
- Newly implemented:
1. `ImprovementTerrainYieldChanges` (trait improvement yield changes conditioned by terrain).
2. `ImprovementFeatureYieldChanges` (trait improvement yield changes conditioned by feature, e.g. Flood Plains).

## Candidate Capabilities

1. Trait building-specific commerce bonuses.
- Example: Libraries `+3` science, Universities `+8` science for a specific trait.
- Proposed XML shape: `TraitBuildingCommerceChanges` with `BuildingClassType + CommerceType + iChange`.

2. Trait building-specific yield bonuses.
- Flat yield changes (food/hammers/commerce) on selected building classes.
- Proposed XML shape: `TraitBuildingYieldChanges` with `BuildingClassType + YieldType + iChange`.

3. Trait building-specific happiness/health bonuses.
- Add `+happy` or `+health` from selected building classes for a trait owner.
- Proposed XML shape: `TraitBuildingHappyChanges` and `TraitBuildingHealthChanges`.

4. Trait specialist-specific bonuses.
- Flat commerce/yield changes for specific specialists (Scientist, Merchant, etc.).
- Proposed XML shape: `TraitSpecialistCommerceChanges` / `TraitSpecialistYieldChanges`.

5. Trait bonus-resource yield modifiers.
- Extra output tied to particular resources (e.g., Wheat, Copper, Incense).
- Proposed XML shape: `TraitBonusYieldChanges` or `TraitBonusYieldModifiers`.

6. Trait route-based yield changes.
- Extra yields from routes (Road/Railroad) on worked plots for trait owners.
- Proposed XML shape: `TraitRouteYieldChanges`.

7. Trait building-class production modifiers.
- Production modifiers for selected building classes, beyond global wonder buckets.
- Proposed XML shape: `TraitBuildingProductionModifiers`.

8. Trait building-class GP rate modifiers.
- Great Person rate modifiers tied to selected building classes.
- Proposed XML shape: `TraitBuildingGreatPeopleRateModifiers`.

## Suggested Implementation Order

1. `TraitBuildingCommerceChanges` + `TraitBuildingYieldChanges` (covers Library/University science case).
2. `TraitBuildingHappyChanges` + `TraitBuildingHealthChanges`.
3. Specialist/resource/route channels.
4. Per-building production and GP-rate modifiers.
