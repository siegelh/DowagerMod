# Civic Capabilities Ideas (Future Work)

This is a theorycrafting list of new civic-effect channels that are not currently standard in the XML design.
Goal: increase variety and specialization of civic strategies.

Scope note: primary target is `Beyond the Sword`.

## Proposed New Capability Channels

1. `CivicBuildingCommerceChanges`
- Per-building-class flat commerce changes.
- Example: Library `+3` science, University `+8` science.

2. `CivicBuildingYieldChanges`
- Per-building-class flat yield changes (food/production/commerce).
- Example: Forge `+1` production, Granary `+1` food.

3. `CivicBuildingGreatPeopleRateModifiersByClass`
- GP rate modifiers tied to selected building classes.

4. `CivicBuildingMaintenanceModifiersByClass`
- Building-specific maintenance reductions/increases by civic.

5. `CivicSpecialistYieldChanges`
- Specialist food/production changes in addition to existing commerce channels.
- Example: Engineer `+1` production under an industry civic.

6. `CivicImprovementCommerceChanges`
- Extra commerce types from worked improvements (city must work the tile).
- Example: Town `+1` science in a commerce civic.

7. `CivicTerrainYieldChanges`
- Yield changes by terrain type.
- Example: Desert `+1` commerce, Grassland `+1` food.

8. `CivicFeatureYieldChanges`
- Yield changes by feature type.
- Example: Forest `+1` food under an ecology civic.

9. `CivicBonusYieldChanges`
- Resource-specific yield changes.
- Example: Oil `+2` production in an industrial civic.

10. `CivicRouteYieldChanges`
- Extra yields from route type on worked plots.
- Example: Roads `+1` commerce, Railroads `+1` production.

11. `CivicTradeRouteModifiersByRouteType`
- Separate domestic and foreign route scaling.
- Useful for clearer Mercantilism vs Free Market differentiation.

12. `CivicUnitClassProductionModifiers`
- Unit-class specific production modifiers by civic.

13. `CivicUnitClassMaintenanceModifiers`
- Unit-class specific upkeep changes by civic.

14. `CivicBuildingClassProductionModifiers`
- Building-class specific production modifiers.
- Example: Markets/Harbors faster in trade civics, Factories faster in industry civics.

15. `CivicComboBonuses`
- Conditional bonuses that activate only with specific cross-tree civic combinations.
- Example: Mercantilism + Serfdom unlocks an extra domestic trade synergy.

## Notes

- These are design candidates, not implemented features.
- Prioritize channels that are high gameplay impact and low implementation risk first.
