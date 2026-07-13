# Remaining 32 implementation matrix — additive freeze

- Status: **approved; runtime implementation pending**
- Last updated: `2026-07-13`
- Runtime changes in this task: **none**
- Machine-readable source:
  `tools/baselines/remaining_roster_implementation_matrix.json`

## Frozen rules

1. The pre-last-pass baseline is the minimum package surface. Do not remove,
   reduce, replace, or unmap baseline features for a touched package.
2. Implement only the explicit additions/corrections in this document.
3. No new DLL mechanic, DLL edit, worker action, worker-action art, or other
   art is authorized.
4. Preserve InfoType order. Additions are append-only when a new type is
   required.
5. Enrico Dandolo/Venice is exact and untouched.
6. Acceptance is fresh-game-only; do not claim old-save compatibility.

## Complete 32-package disposition

| Leader | Civilization | Disposition |
|---|---|---|
| `LEADER_WASHINGTON` | `CIVILIZATION_AMERICA_FOUNDING_REPUBLIC` | baseline restored; no new change |
| `LEADER_GERONIMO_BTG` | `CIVILIZATION_APACHE_CONFEDERACY` | baseline + approved AI adjustment |
| `LEADER_MONTEZUMA` | `CIVILIZATION_AZTEC` | unchanged baseline |
| `LEADER_HAMMURABI` | `CIVILIZATION_BABYLON` | baseline restored; no new change |
| `LEADER_HANNIBAL` | `CIVILIZATION_CARTHAGE` | unchanged baseline |
| `LEADER_ELIZABETH` | `CIVILIZATION_ELIZABETHAN_ENGLAND` | baseline restored; no new change |
| `LEADER_DE_GAULLE` | `CIVILIZATION_FRANCE_FIFTH_REPUBLIC` | unchanged baseline |
| `LEADER_BISMARCK` | `CIVILIZATION_GERMAN_EMPIRE` | unchanged baseline |
| `LEADER_CATHERINE` | `CIVILIZATION_IMPERIAL_RUSSIA` | unchanged baseline |
| `LEADER_HUAYNA_CAPAC` | `CIVILIZATION_INCA` | baseline + approved text |
| `LEADER_GANDHI` | `CIVILIZATION_INDIA` | unchanged baseline |
| `LEADER_TOKUGAWA` | `CIVILIZATION_JAPAN` | unchanged baseline |
| `LEADER_SURYAVARMAN` | `CIVILIZATION_KHMER` | unchanged baseline |
| `LEADER_WANGKON` | `CIVILIZATION_KOREA` | baseline restored; no new change |
| `LEADER_ASOKA` | `CIVILIZATION_MAURYA` | baseline + approved fixes |
| `LEADER_PACAL` | `CIVILIZATION_MAYA` | unchanged baseline |
| `LEADER_GENGHIS_KHAN` | `CIVILIZATION_MONGOL_EMPIRE` | baseline restored; no new change |
| `LEADER_SITTING_BULL` | `CIVILIZATION_NATIVE_AMERICA` | baseline restored; no new change |
| `LEADER_WILLEM_VAN_ORANJE` | `CIVILIZATION_NETHERLANDS` | unchanged baseline |
| `LEADER_CHINESE_LEADER` | `CIVILIZATION_PEOPLES_REPUBLIC_CHINA` | baseline restored; no new change |
| `LEADER_PETER` | `CIVILIZATION_PETRINE_RUSSIA` | baseline + broad science buff |
| `LEADER_CASIMIR` | `CIVILIZATION_POLAND` | baseline + approved flavor |
| `LEADER_SALAMASINA_BTG` | `CIVILIZATION_POLYNESIA_BTG` | baseline restored; no new change |
| `LEADER_JOAO` | `CIVILIZATION_PORTUGAL` | unchanged baseline |
| `LEADER_QIN_SHI_HUANG` | `CIVILIZATION_QIN_DYNASTY` | unchanged baseline |
| `LEADER_ISABELLA` | `CIVILIZATION_SPAIN` | unchanged baseline |
| `LEADER_STALIN` | `CIVILIZATION_USSR` | baseline restored + Factory Production |
| `LEADER_ENRICO_DANDOLO` | `CIVILIZATION_VENICE` | exact untouched baseline |
| `LEADER_RAGNAR` | `CIVILIZATION_VIKING` | unchanged baseline |
| `LEADER_CHURCHILL` | `CIVILIZATION_WARTIME_BRITAIN` | baseline restored + espionage flavor |
| `LEADER_KUBLAI_KHAN` | `CIVILIZATION_YUAN_DYNASTY` | baseline + both Palace layers |
| `LEADER_SHAKA` | `CIVILIZATION_ZULU` | unchanged baseline |

## Restored baseline package contracts

- **Washington:** retain the full baseline trait, including Town, Barracks,
  Courthouse, Bank, Spy, Merchant, Wheat, Horse, and Road channels.
- **Hammurabi:** retain all baseline Royal Palace yields/commerce and all
  Garden/Courthouse features.
- **Elizabeth:** retain the full baseline Sea Dog multi-class mapping,
  including Galley, Trireme, and Privateer mappings.
- **Wang Kon:** retain Korean Library, Seowon, and Korean Academy mappings and
  values.
- **Genghis Khan:** retain every baseline trait entry, including Japanese
  Castle Town commerce.
- **Sitting Bull:** retain the baseline `TradeYieldModifiers` array.
- **Chinese Leader/Mao:** retain every Mass Line channel, including worked
  Farm espionage.
- **Salamasina:** retain baseline `iHealth=5`, `iHappiness=3`, Navigation,
  Canoe, Wayfinder, Marae, and existing Reef Works behavior.
- **Stalin:** retain baseline trait espionage, USSR Spy mapping and values,
  two Research Institute Scientists, USSR Monument values/slots, and Lubyanka
  values. Add Factory Production only.
- **Churchill:** retain baseline MI6 `200%` espionage, two free Spies, Spy
  slot, and all other package values. Add flavor only.

## Retained additive/corrective contracts

### Geronimo

- `LEADER_GERONIMO_BTG`: `iBasePeaceWeight 8 -> 4`.
- `LEADER_GERONIMO_BTG`: `iLimitedWarRand 200 -> 120`.
- Every other personality and gameplay-object field remains baseline.

### Huayna Capac

- Retain approved text/help clarification.
- No numeric, mapping, promotion, unit, building, or art changes.

### Asoka

- `BUILDING_MAURYAN_OBELISK` production trait:
  `TRAIT_RAMESSES -> TRAIT_ASOKA`, value `50`.
- `BUILDING_MAURYAN_OBELISK` happiness trait:
  `TRAIT_RAMESSES -> TRAIT_ASOKA`, value `+1`.
- Retain the approved war-weariness correction `25 -> -25`.
- All other Mauryan features remain baseline.

### Casimir

- `LEADER_CASIMIR`: `FLAVOR_GROWTH 6 -> 5`.
- `LEADER_CASIMIR`: `FLAVOR_CULTURE 3 -> 4`.
- No other AI, diplomacy, war, trait, unit, or building changes.

### Stalin

- Add `BUILDINGCLASS_FACTORY` Production `+1` to `TRAIT_STALIN` through the
  existing `BuildingYieldChanges` channel.
- Do not reduce or remove any baseline USSR feature.

### Churchill

- Add `FLAVOR_ESPIONAGE = 3` to `LEADER_CHURCHILL`.
- Do not reduce MI6 or any other baseline feature.

### Kublai Khan

- Retain `BUILDING_MONGOLIAN_PALACE` as a Kublai package layer.
- Retain the approved `BUILDING_YUAN_IMPERIAL_SECRETARIAT` layer with `+1`
  trade route and `+2` culture.
- Preserve Qianhu Cavalry, Ortoo Hub, trait, Palace prerequisites/effects, and
  all baseline mappings. Neither Palace layer replaces or reduces the other.
- Reuse existing Palace art; no art addition.

## Peter broad science contract

- `TRAIT_PETER`: Great People rate `25 -> 50`.
- `TRAIT_PETER`: Library receives `+2` research and `+1` culture.
- `TRAIT_PETER`: University receives `+3` research and `+1` culture.
- `BUILDING_PETER_ADMIRALTY`: add/retain `25%` research modifier.
- `BUILDING_PETER_COLLEGIUM_OF_FOREIGN_AFFAIRS`: add/retain `25%` research
  modifier.
- Preserve every other baseline Peter trait/building value and mapping.

## Corporation contract

| Ordered corporation | Gold value | Required behavior |
|---|---:|---|
| `CORPORATION_1` | 100 | active |
| `CORPORATION_2` | 200 | active |
| `CORPORATION_3` | 350 | active |
| `CORPORATION_4` | 100 | active |
| `CORPORATION_5` | 250 | active |
| `CORPORATION_6` | 200 | active |
| `CORPORATION_7` | 0 | inert |

## DLL, worker, art, save, and release decisions

- **DLL:** no source/schema/binding/serialization change.
- **Worker actions:** none added or modified.
- **Art:** none added, replaced, or remapped.
- **Saves:** fresh games mandatory; old saves are not acceptance evidence.
- **Multiplayer:** matched payloads and fresh games on both peers.
- **Enrico:** exact equality against baseline is a hard gate.

## Validation contract

1. Compare each restored package against the approved baseline and reject every
   unintended removal/reduction.
2. Assert exact Geronimo, Asoka, Casimir, Stalin, Churchill, Kublai, and Peter
   values above.
3. Assert Huayna changes text only.
4. Assert corporation values `100/200/350/100/250/200` and inert Corp7.
5. Assert no DLL, worker-action, or art file changes.
6. Run repository XML/roster gates during implementation.
7. Complete the remaining-roster section in
   `docs/MANUAL_SMOKE_TESTS.md` using fresh SP and fresh two-client MP games.
