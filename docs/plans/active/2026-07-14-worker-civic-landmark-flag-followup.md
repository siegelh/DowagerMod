# Worker, State Property, Landmark, and Flag Follow-up

- Status: `automated implementation/validation complete; installed runtime acceptance pending`
- Owner / agent: GitHub Copilot CLI
- Last updated: `2026-07-15`

## Problem Statement

This follow-up consolidates four approved investigation tracks:

1. Automated workers sometimes idle or redirect despite owned, workable plots
   having valid improvements.
2. State Property should be evaluated for a Palace-based Great Engineer point
   identity without adding recurring scans or fragile stored state.
3. Commercial District and Grand Bazaar remain too large after their first
   reduction from `0.65` to `0.25`.
4. The era-specific civilization packages have unique border colors but still
   reuse many civilization flags, including one clear Native
   America/Apache/Polynesia cross-wiring defect.

The user-owned State Property edit was preserved, repaired, validated, and
committed separately as `b42569d8b`. It sets `bMilitaryFoodProduction` to `0`;
the canceled all-specialist commerce experiment is absent.

## Why This Matters

- Worker automation that silently abandons valid work makes both human
  automation and AI empires unreliable.
- The city-specific worker scoring is already sophisticated; narrow gaps
  should be fixed instead of replacing it with a more expensive planner.
- State Property currently grants unlimited Engineer slots, but the proposed
  Palace effect would give the civic a visible Great Engineer identity without
  multiplying output by every assigned specialist.
- The roster intentionally represents leaders as distinct era-specific
  civilization packages. Shared or incorrect flags erase that distinction
  even though their border colors are now unique.

## Scope

- Repair the malformed State Property XML while retaining the user's intended
  `bMilitaryFoodProduction=0` change and removing the canceled
  all-specialist Commerce/Culture experiment.
- Make cities report at least one worker needed when they have at least one
  unworked, unimproved plot with a valid cached Build.
- Make ordinary worker build scoring retain the direct Research value of an
  existing Research Campus.
- Add a derived `+10` base GPP Palace bonus under State Property, assigned
  entirely to the civilization's Great Engineer unit.
- Further reduce Commercial District and Grand Bazaar map scale together.
- Give each affected playable era-specific civilization package its own
  historically grounded flag ArtDefine/decal.
- Correct the Native America/Apache/Polynesia flag ArtDefine cross-wiring.

## Non-Goals

- No broad rewrite of `AI_workerMove`, `AI_bestPlotBuild`, pathfinding,
  mission targeting, worker scrapping, or city governor logic.
- No second city-tile sweep, map scan, per-turn allocation, logging, or RNG.
- No change to landmark yields, rotation, interface scale, or model identity.
- No leader-specific flag runtime mechanic. Civ4 flags are civilization-level;
  the 1:1 leader/civilization packages provide the desired leader distinction.
- No automatic replacement of civilization-selection buttons in the first
  flag pass; buttons are separate atlas/standalone assets and require a
  separate visual decision.
- No State Property bonus for every Engineer specialist unless separately
  approved.

## Trusted Sources Of Truth

- Worker mission flow:
  `third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvUnitAI.cpp:1348-1670`,
  `13383-13666`.
- City worker demand and build scoring:
  `third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvCityAI.cpp:5004-5359`,
  `7521-8150`, `9298-9491`.
- Research Campus direct Research:
  `CvCityAI.cpp:7401-7470`,
  `CvPlot.cpp:6479-6544`.
- GPP accounting:
  `CvCity.cpp:4876-4930`, `6279-6324`, `10606-10630`,
  `12930-12937`.
- Civic transitions and AI:
  `CvPlayer.cpp:11737-11766`, `15854-15940`;
  `CvPlayerAI.cpp:9193-9440`.
- Palace variants:
  `Assets/XML/Buildings/CIV4BuildingInfos.xml:10-187,350-357,58599-58606`.
- Civilization/flag wiring:
  `Assets/XML/Civilizations/CIV4CivilizationInfos.xml`;
  `Assets/XML/Art/CIV4ArtDefines_Civilization.xml`.
- Existing color work:
  `docs/plans/active/2026-07-13-unique-civilization-colors.md`.
- Required gates:
  `tools/test_gate.ps1`, `tools/test_xml.ps1`,
  `tools/tests/test_great_person_landmarks.py`.

## Existing Behavior and Root-Cause Findings

### Worker automation

- `AI_updateWorkersNeededHere` counts valid unworked/unimproved plots in
  `iUnimprovedUnworkedPlotCount`, but its final hard floor uses only
  `iUnimprovedWorkedPlotCount` (`CvCityAI.cpp:9307-9364,9488`).
- A city can therefore report zero workers needed while valid future work
  exists. `AI_nextCityToImprove` refuses even to call `AI_bestCityBuild` when
  that demand is zero (`CvUnitAI.cpp:13601-13615`).
- Human automated workers cannot enter the AI-only `scrap()` branch
  (`CvUnitAI.cpp:1642-1650`). They instead fall through to routes, retreat,
  safety, or `MISSION_SKIP`.
- Generic worker selection already uses the city's food balance, production
  needs, financial state, yield modifiers, worked status, feature removal,
  bonuses, upgrades, and actual improvement yield changes
  (`CvCityAI.cpp:5004-5359,7521-8150`). A wholesale scoring rewrite is neither
  necessary nor low risk.
- Direct Research Campus Research is included in city governor valuation but
  not in ordinary worker replacement scoring. AI players can therefore
  undervalue and replace a Campus; human players are protected only when
  `PLAYEROPTION_SAFE_AUTOMATION` is enabled.

### State Property Palace GPP

- Four active building types use `BUILDINGCLASS_PALACE`: standard Palace,
  Venetian Doge Palace, Babylon Royal Palace, and Yuan Imperial Secretariat.
  The effect must key on the class, not `isGovernmentCenter()`, which also
  includes unrelated government centers and Versailles.
- Stored base and per-unit GPP rates are mutated by buildings and specialists.
  A derived bonus must not be folded into
  `changeGreatPeopleUnitRate()`, which calls the current getter and could
  persist or double-count a derived value.
- The safe design is one read-only helper that returns `10` only when the city
  has its civilization's active Palace-class building and its owner runs
  State Property. Include that helper as base GPP before normal city GPP
  modifiers and as 10 unmodified source points in the Great Engineer pool at
  consumption/display/AI boundaries; do not mutate or serialize the stored
  rate arrays.

### Merchant landmark scale

- Both ArtDefines currently use `fScale=0.25`, with
  `fInterfaceScale=1.0` and their original Forum/Market NIFs
  (`CIV4ArtDefines_Improvement.xml:327-344`).
- Runtime feedback says both remain too large. Proposed next calibration:
  `fScale=0.10` for both, pending final approval.

### Duplicate flags

All 59 playable packages now have unique border colors, but only 40
CivilizationArtInfo records exist. The following distinct playable packages
share flags and require unique era/polity ArtDefines:

| Shared family | Packages/leaders requiring differentiation |
| --- | --- |
| America | Union/Lincoln, Founding/Washington, New Deal/FDR, Federal/Barclay |
| England/Britain | Regency/Dowager, Elizabethan/Elizabeth, Victorian/Victoria, Wartime/Churchill |
| France | Bourbon/Louis XIV, First Empire/Napoleon, Fifth Republic/de Gaulle |
| Russia | Petrine/Peter, Imperial/Catherine, USSR/Stalin |
| Persia | Founding Achaemenid/Cyrus, Imperial Achaemenid/Darius |
| Egypt | Eighteenth Dynasty/Hatshepsut, New Kingdom/Ramesses |
| Ottoman | Conquest/Mehmed, Classical/Suleiman |
| Ethiopia | Solomonic/Zara Yaqob, Imperial/Haile Selassie |
| India | India/Gandhi, Maurya/Asoka |
| Gaul/Britain | Gaulic Confederation/Brennus, Iceni/Boudica |
| Greece | Macedonian Empire/Alexander, Athenian Greece/Pericles |
| Mongol/Yuan | Mongol Empire/Genghis, Yuan Dynasty/Kublai |
| Rome | Late Republic/Caesar, Principate/Augustus |
| Germany | Prussia/Frederick, German Empire/Bismarck |
| Native/Apache/Polynesia | currently cross-wired; Sitting Bull uses the Polynesia tag while Apache and Polynesia share Native America |

Historically grounded motif direction:

- Founding America: 13-star ring; Union: Civil War-era stars; New Deal:
  federal eagle/shield; Federal: modern star field.
- Elizabethan: St. George/Tudor rose; Regency: period Union flag; Victorian:
  imperial crown/Union motif; Wartime: period Union/V motif.
- Bourbon: fleur-de-lis; First Empire: imperial eagle; Fifth Republic:
  tricolor/Marianne or cockade.
- Petrine: early double eagle; Imperial: full regalia eagle; USSR:
  hammer-and-sickle.
- Cyrus/Darius: distinct Achaemenid winged-disc/royal-standard motifs, not the
  current later-era scimitar.
- Hatshepsut/Ramesses: distinct crown/cartouche/falcon or solar motifs.
- Mehmed/Suleiman: conquest crescent versus imperial tughra.
- Zara/Haile: medieval versus imperial Lion of Judah.
- Maurya: Ashokan lion/dharma motif; Gandhi India: historically appropriate
  modern independence-era wheel treatment.
- Gaul: boar/carnyx/triskele; Iceni: torc/horse coinage, replacing the
  anachronistic shared Celtic cross.
- Macedon: Vergina-style sun; Athens: owl of Athena.
- Mongol: horsetail standard; Yuan: Yuan imperial dragon treatment.
- Republic: SPQR/eagle standard; Principate: civic crown/imperial laurel.
- Prussia: Prussian eagle; German Empire: crowned imperial eagle.
- Native America, Apache, and Polynesia: three distinct, culturally specific
  emblems after correcting their swapped/shared ArtDefine tags.

Every motif requires source verification against period coinage, standards,
seals, or public-domain museum/reference material before asset production.

## Proposed Implementation Steps

### Phase 0 — Preserve and repair current user work

1. Save the exact user diff for `CIV4CivicInfos.xml`.
2. Retain `CIVIC_STATE_PROPERTY/bMilitaryFoodProduction=0`.
3. Remove the unmatched `</SpecialistExtraCommerces>` tag and leave
   `SpecialistExtraCommerces` empty; do not add the canceled all-specialist
   bonus.
4. Parse and schema-validate the civic XML before any DLL work.
5. Commit this user-authored civic adjustment separately.

### Phase 1 — Narrow worker correctness fixes

1. In `CvCityAI::AI_updateWorkersNeededHere`, preserve the existing worker
   formula and, after all multipliers/halving and the existing final floor, add
   only:
   `if (iUnimprovedUnworkedPlotCount > 0) iWorkersNeeded = max(1, iWorkersNeeded);`
2. Do not alter worker scrapping. Once demand no longer incorrectly reaches
   zero, existing cross-city targeting checks valid work before that AI-only
   fallback.
3. In `CvCityAI::AI_bestPlotBuild`, account for the current Research Campus's
   direct Research when comparing replacement candidates, using normal
   Research commerce weighting and the existing Campus helper.
4. Keep ordinary plot cost O(1): one cached improvement-type comparison; only
   an actual Campus performs the existing eight-neighbor scan.
5. Add static contracts for the demand floor, no new city/map sweep, no RNG,
   Campus valuation, and unchanged worker-scrap logic.

### Phase 2 — State Property Palace Great Engineer identity

1. Add a `CvCity` helper for the conditional Palace GPP bonus:
   owner runs State Property, city has the civilization's active
   `BUILDINGCLASS_PALACE`, return `10`; otherwise `0`.
2. Add the helper to the base-rate expression inside effective city GPP before
   normal city GPP modifiers, without changing the stored base-rate getter.
3. Add exactly 10 unmodified source points only to the civilization's resolved
   `UNITCLASS_ENGINEER` progress during `doGreatPeople`, preserving the
   vanilla relationship between modified total progress and unmodified
   per-unit source weights.
4. Do not mutate stored `m_iBaseGreatPeopleRate` or
   `m_paiGreatPeopleUnitRate`; add no save fields.
5. Expose the conditional contribution in city GPP help, Palace help, and
   State Property civic help.
6. Add an explicit State Property term to `CvPlayerAI::AI_civicValue` so AI
   civic selection understands the bonus.
7. Add contracts for all four Palace-class variants, exact Engineer-only
   attribution, civic adopt/remove derivation, no persistence, and no
   government-center overreach.

### Phase 3 — Merchant landmark visual calibration

1. Change only Commercial District and Grand Bazaar `fScale` from `0.25` to
   the approved smaller value (proposed `0.10`).
2. Keep `fInterfaceScale=1.0`, original NIFs, rotations, feature behavior,
   and yields unchanged.
3. Update exact landmark scale tests and the manual smoke runbook.

### Phase 4 — Unique historically grounded flags

1. Produce a machine-readable audit from live CivilizationInfos and
   CivilizationArtInfos; reject duplicate ArtDefine/Path ownership among the
   targeted playable packages.
2. Fix the Native America/Apache/Polynesia ArtDefine assignments first.
3. Search repository art, then the approved external art libraries, before
   creating/importing assets.
4. For each affected package, record historical source, source/license status,
   motif rationale, source asset, destination DDS, new ArtDefine tag, and
   CivilizationInfo wiring.
5. Create one square power-of-two DDS decal per package using the existing
   flag alpha/team-color convention; preserve `bWhiteFlag` behavior unless
   runtime tests prove a full-color flag is required.
6. Add new CivilizationArtInfo records at the end of the existing list and
   repoint only the intended era-specific CivilizationInfos.
7. Do not change PlayerColor mappings or enum order.
8. Validate every flag in the Civilopedia, civilization selection, world map,
   and minimap before accepting the art pass.

## Validation Plan

### Automated

- Parse the edited civic, art, civilization, and improvement XML.
- Add exact tests for:
  - State Property intended fields and no malformed/canceled specialist bonus.
  - Worker-demand floor with buildable unworked plots.
  - No second worker/city/map sweep and no RNG.
  - Research Campus retention valuation.
  - Palace-class conditional total GPP and Engineer-only unit GPP.
  - No stored-rate mutation or save-format addition.
  - Exact Merchant map scales and unchanged interface scales/NIFs.
  - Unique targeted civilization ArtDefine tags and flag paths.
  - Complete flag asset existence and DDS metadata.
- Run:
  - `python -m pytest tools\tests -q`
  - `.\tools\test_gate.ps1 -CheckDll`
  - `.\tools\test_xml.ps1 -All`
  - `git diff --check`
- Confirm built Release DLL and active payload DLL hashes match.

### Runtime

- Human automated worker: city has only unworked/unimproved valid plots;
  confirm worker improves them instead of routing/idling.
- AI worker: same scenario with workers greater than city count; confirm valid
  work is selected before any surplus-worker cleanup.
- City-specific scoring: food-poor, production-poor, and financially troubled
  cities choose different sensible improvements using their existing
  priorities.
- Existing Research Campus is not replaced by a weaker ordinary improvement.
- State Property:
  - Palace city gains exactly 10 base GPP before modifiers and the effective
    total scales through normal city GPP modifiers;
  - exactly 10 unmodified source points feed Great Engineer progress only;
  - non-Palace cities gain none;
  - effect appears/disappears immediately on civic switch;
  - all four Palace variants work;
  - save/reload and two-client OOS checks pass.
- Merchant landmarks render materially smaller without disappearing at normal
  or strategic zoom.
- Flag matrix: inspect every changed package in Civilopedia, setup screen,
  world map, and minimap; verify emblem identity, alpha, team color, orientation,
  and no pink/missing textures.

## Risks and Rollback

- Raising a city's minimum demand to one can keep one worker employed longer;
  it cannot increase demand above one solely because of unworked plots.
- Campus replacement scoring must not double-count its Research in governor
  tile valuation; keep the change confined to worker build comparison.
- Derived Palace GPP must bypass stored-rate mutators to avoid stale or
  compounding values.
- Ten Palace GPP is a strong late-game effect; AI civic valuation and runtime
  balance need explicit review.
- `0.10` may make Merchant landmarks too small. Rollback is a one-field
  ArtDefine adjustment.
- Incorrect flag alpha/DDS encoding can create solid rectangles, invisible
  emblems, or wrong team coloring. Roll back each package independently to its
  prior ArtDefine.
- Never revert or overwrite unrelated user work in `CIV4CivicInfos.xml`.

## Locked Decisions

- Use `+10` Palace base GPP under State Property, all attributed to Great
  Engineer progress.
- Use `fScale=0.10` for both Merchant landmarks as the next calibration.
- Give every era-specific package a unique flag, including same-nation eras,
  rather than fixing only cross-polity errors.
- Keep civilization-selection buttons unchanged in this pass.

## Completion Checklist

- [x] User State Property XML intent is repaired, validated, and committed
  separately.
- [x] Worker-demand and Campus replacement fixes are implemented and compiled.
- [x] Palace State Property GPP is derived, displayed, AI-valued, and covered
  by focused automated contracts.
- [ ] Merchant landmarks pass final visual scale acceptance.
- [x] Complete targeted flag registry has unique, accurate, validated assets.
- [x] Full automated gates pass.
- [ ] Installed worker, GPP, landmark, flag, save/reload, and MP checks pass.
