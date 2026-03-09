# Refined Goods Network Debug 2026-03-02

## Problem

Luxury industry buildings were locally active and granting their `FreeBonus`, but the refined good was not always entering the empire network correctly after save/load or after network churn.

Observed symptoms:

- Two valid cities could both have active buildings, but the empire total stayed at `1` instead of stacking to `2`.
- Some cities showed impossible negative raw network counts like `cityNetworkRaw=-1`, `-2`, or lower for refined goods.
- Trading a refined good could look wrong until the network cache was corrected.

Representative live examples during debugging:

- Greece:
  - `Athens` + `Knossos` both had active `Spice Exchange`
  - expected result: `2` `Spice Blends` in the Greek network
- Egypt:
  - `Thebes` + `Memphis` both had active `Sculptors' Yard`
  - expected result: `2` `Marble Statuary` in the Egyptian network

## What The Logs Proved

The important distinction was:

- local activation was mostly correct
- city/plot-group network bonus caches were drifting

That meant the bug was not primarily:

- building visibility
- tile overlap between cities
- duplicate refined goods being disallowed
- corporation-produced bonus logic

Instead, the failure was in the network bookkeeping layer that combines:

- map bonus connectivity
- city `FreeBonus`
- plot-group cached bonus totals
- per-city cached network bonus totals

## Root Causes

### 1. Save/load cache state was stale

Some loaded cities kept bad serialized `m_paiNumBonuses` state instead of rebuilding from the authoritative plot-group state.

Relevant fix:

- [CvPlayer.cpp](/c:/DowagerMod/third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvPlayer.cpp)
  - after player load, rebuild each plot group’s bonus counts
  - then resync each city’s network bonus counts

### 2. Plot-group bonus totals were not rebuilt authoritatively

The plot group needed a full rebuild from actual plots and city free bonuses after load.

Relevant fix:

- [CvPlotGroup.h](/c:/DowagerMod/third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvPlotGroup.h)
- [CvPlotGroup.cpp](/c:/DowagerMod/third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvPlotGroup.cpp)
  - added authoritative `rebuildBonusCounts()`

### 3. City network bonus caches could drift during plot-group churn

Some city bonus totals were being updated incrementally during plot-group reassignment and activation churn, which produced bad intermediate and sometimes persistent totals.

Relevant fixes:

- [CvCity.h](/c:/DowagerMod/third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvCity.h)
- [CvCity.cpp](/c:/DowagerMod/third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvCity.cpp)
  - added city sync helpers and deferred activation updates
- [CvPlot.cpp](/c:/DowagerMod/third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvPlot.cpp)
  - removed redundant manual city bonus delta loops in plot-group/city reassignment paths

### 4. Re-entrant activation during network mutation was unsafe

Industry activation was recalculating while plot groups and city bonus totals were mid-update.

Relevant fix:

- [CvCity.cpp](/c:/DowagerMod/third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvCity.cpp)
  - deferred industry activation refreshes while network mutation is in progress

## Final Verified Behavior

The trace confirmed the intended stable behavior in the user’s test game:

- `Athens` and `Knossos` both reached `cityNetworkRaw=2` for `BONUS_SPICE_BLENDS`
- `Thebes` and `Memphis` both reached `cityNetworkRaw=2` for `BONUS_MARBLE_STATUARY`
- After Greece traded one refined spice to Egypt in exchange for one refined marble:
  - Greek cities showed `cityNetworkRaw=1` for `BONUS_SPICE_BLENDS`
  - Egyptian cities showed `cityNetworkRaw=1` for `BONUS_MARBLE_STATUARY`

That means refined goods are now behaving like normal networked, tradeable resources in the main tested cases.

## About The Remaining Negative Values

Some trace lines still showed transient negatives for another civ during connection / plot-group churn, for example:

- `Bibracte`
- `Tolosa`
- `Verlamion`

Interpretation:

- these negatives appeared while `connected=0`, while `plotGroup` changed, or on immediate activation/deactivation edges
- later lines for the same cities settled back to `0` or `1`
- in other words, they looked like transition-state bookkeeping noise, not the final stable value seen by the player

So the current conclusion is:

- stable user-facing refined-good behavior appears fixed in the tested cases
- transient negative trace lines may still appear during recalculation
- they should not be treated as the intended gameplay representation of “resource lost”

## Related Gameplay Rule Clarified

The intended gameplay rule remains:

- if the owned/improved/connected source is lost, the luxury building should deactivate
- when it deactivates, the refined good should leave the network
- duplicates should stack if multiple active cities produce the same refined good
- exported trade copies should reduce the domestic usable total after production is counted

## Files Most Important For Future Debugging

- [CvCity.cpp](/c:/DowagerMod/third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvCity.cpp)
- [CvCity.h](/c:/DowagerMod/third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvCity.h)
- [CvPlot.cpp](/c:/DowagerMod/third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvPlot.cpp)
- [CvPlotGroup.cpp](/c:/DowagerMod/third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvPlotGroup.cpp)
- [CvPlotGroup.h](/c:/DowagerMod/third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvPlotGroup.h)
- [CvPlayer.cpp](/c:/DowagerMod/third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvPlayer.cpp)

## Practical Rule For Reopening This Investigation

If refined goods ever fail again, debug in this order:

1. Confirm the building is locally active.
2. Confirm the city has the local `FreeBonus`.
3. Confirm the plot group has the expected total.
4. Confirm city network bonus caches were rebuilt after load or after network churn.
5. Only then chase trade/export behavior.
