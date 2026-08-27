# Remaining 32 roster audit — approved additive direction

- Status: `implemented; installed-game validation pending`
- Last updated: `2026-07-14`
- Runtime implementation: landed in `b4020964e` with exact-contract coverage
- Machine-readable contract:
  `tools/baselines/remaining_roster_implementation_matrix.json`

## Audit conclusion

The previous subtractive balance pass is superseded. For every package touched
by that pass, the baseline package is the floor: no baseline feature, mapping,
yield, commerce value, specialist, action, or building effect may be removed or
reduced unless it is one of the explicitly retained fixes below.

This is an additive roster pass. Untouched members of the remaining 32 stay at
baseline. The recent 27 remain comparison context only.

## Approved package dispositions

| Package | Approved disposition |
|---|---|
| Washington | Retain the restored baseline package except for the over-scaling Road Commerce channel, which is removed. |
| Geronimo | Retain the baseline package plus the approved AI/personality adjustment. |
| Hammurabi | Restore and retain the complete baseline Palace and package; no yield or commerce reductions. |
| Elizabeth | Restore and retain all baseline Sea Dog class mappings and package features. |
| Huayna Capac | Retain the baseline package plus approved text/help clarification only. |
| Wang Kon | Restore and retain the Korean Library, Seowon, and Korean Academy layers. |
| Asoka | Retain the baseline package plus the approved Ramesses-reference and war-weariness fixes. |
| Genghis Khan | Restore and retain the complete baseline trait, including the Japanese Castle Town channel. |
| Sitting Bull | Restore and retain the baseline trade-yield array and package. |
| Mao / Chinese Leader | Restore and retain the baseline Mass Line trait, including worked-Farm espionage. |
| Peter | Apply the approved broad science buff detailed below; remove nothing. |
| Casimir | Retain the baseline package plus the approved flavor adjustment. |
| Salamasina | Restore and retain baseline health, happiness, Navigation, units, Marae, and existing Reef Works behavior. |
| Stalin | Restore the complete baseline USSR package and add Factory +1 Production through the existing trait channel. |
| Enrico Dandolo | Exact untouched baseline: no numeric, mapping, action, AI, text, or art changes. |
| Churchill | Restore the complete baseline package, including full MI6 values, and add espionage flavor. |
| Kublai Khan | Retain both approved Palace layers, including the Imperial Secretariat; remove neither layer. |

All other remaining-roster packages are unchanged from baseline.

## Explicit additive records

- **Geronimo AI:** retain `iBasePeaceWeight 8 -> 4` and
  `iLimitedWarRand 200 -> 120`; no gameplay-object reductions.
- **Huayna Capac text:** retain approved text/help clarification; no numeric,
  mapping, unit, building, or promotion changes.
- **Asoka fixes:** Mauryan Obelisk trait references belong to `TRAIT_ASOKA`,
  not `TRAIT_RAMESSES`, and the approved war-weariness correction remains.
- **Casimir flavor:** retain the approved Growth/Culture flavor adjustment;
  do not alter his trait, unit, building, diplomacy, or war settings.
- **Stalin:** add exactly `BUILDINGCLASS_FACTORY` Production `+1` through the
  existing trait building-yield channel; retain every baseline USSR feature.
- **Churchill:** add `FLAVOR_ESPIONAGE = 3`; retain baseline MI6, War Rooms,
  Fighter Command, trait, and all existing values.
- **Kublai:** preserve the baseline Mongolian Palace layer and the approved
  Yuan Imperial Secretariat layer, including the Secretariat's approved
  `+1` trade route and `+2` culture contract. Do not replace one with the
  other or remove either.

## Peter broad science buff

Peter receives the approved additive package:

1. Great People rate: `25 -> 50`.
2. Library trait bonus: `+2` research and `+1` culture.
3. University trait bonus: `+3` research and `+1` culture.
4. `BUILDING_PETER_ADMIRALTY`: `+25%` research.
5. `BUILDING_PETER_COLLEGIUM_OF_FOREIGN_AFFAIRS`: `+25%` research.

All baseline Peter features remain.

## Corporation contract

Corporations use the following ordered gold values:

| Corporation | Gold value | State |
|---|---:|---|
| Corporation 1 | 100 | active |
| Corporation 2 | 200 | active |
| Corporation 3 | 350 | active |
| Corporation 4 | 100 | active |
| Corporation 5 | 250 | active |
| Corporation 6 | 200 | active |
| Corporation 7 | 0 | inert |

Corporation 7 must remain inert: no effective gold output or replacement
effect is authorized.

## Technical constraints

- XML/text changes only during later implementation; no new DLL work.
- No new worker actions and no new worker-action art.
- No new art imports or art remaps.
- Preserve synchronized InfoType order; append-only treatment applies where a
  new Secretariat type is required.
- Enrico must remain exact.
- Fresh games are mandatory for acceptance. Old-save compatibility is not a
  release target for this roster pass.

## Audit acceptance criteria

1. Baseline-restored packages have no removed/reduced baseline feature.
2. Only the named additive changes and Asoka correction are present.
3. Peter's five science values match exactly.
4. Corporation values match `100/200/350/100/250/200`; Corporation 7 is inert.
5. No DLL source, worker-action behavior, worker-action art, or other art is
   added or changed.
6. Enrico is exact and untouched.
7. Installed manual validation starts from fresh games.
