# Harbor Water Food

## Problem and approach

Water-heavy cities need a midgame progression step after the Lighthouse.
Every active `BUILDINGCLASS_HARBOR` building will therefore add one base Food
for every two water plots in the city's full 20-tile BFC, capped at eight
Food. The city center is excluded. Coast, Ocean, and lakes all count through
`CvPlot::isWater()`; ownership, city assignment, and worked status do not.

The implementation is class-based so the normal Harbor, Carthaginian Cothon,
and Petrine Admiralty inherit the same formula while retaining their current
unique effects.

## Implementation

1. Add tunable divisor and cap defines with values `2` and `8`.
2. Add a full-BFC water counter and Harbor-class resolver to `CvCity`.
3. Cache the derived Food in a nonserialized city member.
   - Recompute when Harbor-class activity changes and after save loading.
   - Include it in effective base Food without mutating serialized base yield.
   - Add no save fields or version changes.
4. Value projected Harbor Food in general and Food-focused city AI building
   evaluation.
5. Add generic, city-projected, and active-city localized help.
6. Add focused source contracts and installed gameplay checks.

## Acceptance

- Formula boundaries are exact: 0-1 water gives 0; 2-3 gives 1; 14-15 gives
  7; and 16-20 gives 8.
- The normal Harbor, Cothon, and Admiralty all inherit the mechanic.
- Existing trade routes, trade yield, Research, Culture, and seafood Health
  effects remain unchanged.
- Existing saves acquire the correct Food after loading; fresh saves do not
  double-count after reload.
- Building and city Food help reconcile the water count, source building, and
  effective base Food.
- AI recognizes the projected Food value without adding recurring map scans.

## Validation

- Run `python -m pytest tools\tests\test_harbor_water_food.py -q`.
- Run `.\tools\test_gate.ps1 -CheckDll`.
- Run `.\tools\test_xml.ps1 -All`.
- Run `git diff --check`.
- In an installed game, test formula thresholds, all three Harbor-class
  buildings, save/reload, AI construction, and two-client OOS consistency.

## Readiness

- Ready for implementation: **Yes**.
- Ready for merge/deploy: **No; automated and installed acceptance remain**.
