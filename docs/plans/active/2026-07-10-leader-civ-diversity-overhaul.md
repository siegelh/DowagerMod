# Leader/Civilization Diversity Overhaul

- Status: `implementation complete; installed-game validation pending`
- Owner / agent: Copilot
- Last updated: `2026-07-14`

## Problem Statement

- Twenty-seven era-specific leader/civilization pairs need stronger historical and gameplay identities.
- The civilization split already exists in live XML, but many split civs still share the same UU/UB package:
  - Athens/Macedon
  - both Frances
  - both Ottomans
  - both Persias
  - both Romes
  - Gaul/Iceni
  - both Egypts
  - both Ethiopias
  - Victoria/Dowager
- Mansa Musa and Ramesses have empty custom traits, Lincoln has no UU, and several current uniques are anachronistic for their assigned leader.
- Every package must use existing XML/Python capabilities and repository-controlled art. No new DLL mechanics are allowed.

## Why This Matters

- Each leader is intentionally paired 1:1 with an era-specific civilization, so duplicated packages erase the main benefit of the roster split.
- Historically mismatched units such as Frederick's Panzer, Charlemagne's Landsknecht, and FDR's Navy SEAL make the roster feel arbitrary.
- The repository contains a large dormant art library that can support distinctive UUs and UBs, but each selected package must be validated as carefully as Catherine's repaired Hussar.

## Scope

- Redesign all 27 requested leader/civilization pairs.
- Use custom traits, UU/UB mappings, existing mapped yield channels, leader AI values, text, buttons, and repository art.
- Add multiple uniques where the history and power budget justify them; do not force a one-UU/one-UB template.
- Reuse or activate dormant art only after NIF/KFM/KF/texture closure checks.
- Keep all implementation and this plan in one final commit on
  `agent-baseline-leader-chatter-sol-leader-update`.

## Non-Goals

- No new `CvGameCoreDLL` fields, hooks, or behavior.
- No broad repair of all 4,444 dormant `UnitArtInfo` definitions.
- No new leaders or civilizations beyond the existing requested roster.
- No changes to base `Assets` or `Warlords` compatibility copies unless a live BtS import proves they are required.
- No changes to chatter, installer behavior, quests, or the Catherine Hussar repair.
- No direct references to external download folders; any external asset must first be copied into BtS `Assets/Art`.

## Trusted Sources Of Truth

- Live civ roster and UU/UB mappings:
  `Assets/XML/Civilizations/CIV4CivilizationInfos.xml`
- Live leader traits and AI:
  `Assets/XML/Civilizations/CIV4LeaderHeadInfos.xml`
- Custom mechanics:
  `Assets/XML/Civilizations/CIV4TraitInfos.xml`
- Unit/building definitions and classes:
  `Assets/XML/Units/CIV4UnitInfos.xml`,
  `Assets/XML/Units/CIV4UnitClassInfos.xml`,
  `Assets/XML/Buildings/CIV4BuildingInfos.xml`, and
  `Assets/XML/Buildings/CIV4BuildingClassInfos.xml`
- Art definitions and assets:
  `Assets/XML/Art/` and `Assets/Art/`
- Required gates:
  `tools/test_gate.ps1`, `tools/test_xml.ps1`, and
  `docs/MANUAL_SMOKE_TESTS.md`

## Existing Docs / Plans Trust Review

- `docs/LEADER_OVERHAUL_PLAN_OF_RECORD.md`: trusted methodology.
- `skills/civ-leader-overhaul-architect/SKILL.md`: trusted workflow aid.
- `skills/detailed-overhaul-v2/SKILL.md`: trusted research/design aid.
- `docs/archive/plans/BRENNUS_GAUL_OVERHAUL_DRAFT.md`: historical context only; live XML and this plan supersede it.
- Commit `59a211ce0`: useful Hatshepsut precedent, but not a clean implementation model because it mixed broad schema and DLL work.
- Commit `81307bef0`: useful Tokugawa/art precedent, but any DLL-dependent portions are excluded.
- Commits `f1b4c518f` and `686f13dfe`: useful art-inventory tooling. They are not on this branch and will not be cherry-picked wholesale; only narrowly useful validation logic may be ported if needed.

## Research Basis

Seven independent research tracks covered the Americas, France/Carolingians,
classical Mediterranean, Near East, Celtic/British, Africa, and Prussia.
Representative primary or scholarly anchors include:

- Arrian, *Anabasis*; Thucydides, *Peloponnesian War*; Augustus,
  *Res Gestae*.
- British Museum, Cyrus Cylinder; Behistun Inscription; Briant,
  *From Cyrus to Alexander*.
- Tacitus, *Annals* XIV; Caesar, *Gallic War* IV; Cunliffe,
  *The Ancient Celts*.
- Ganshof, *Frankish Institutions*; Chandler, *The Campaigns of Napoleon*;
  Blanning, *Frederick the Great*.
- Tyldesley, *Hatchepsut*; Kitchen, *Pharaoh Triumphant*; Tamrat,
  *Church and State in Ethiopia*.
- Lincoln-era Morrill and National Banking Acts; FDR-era WPA/CCC/TVA and
  Marine Raiders.

Research proposals are design inputs, not runtime truth. Live XML verification
overrides stale vanilla assumptions, invalid class names, or DLL-dependent
ideas from any report.

## Resolved Design Matrix

| Leader / civilization | Historical and gameplay thesis | Recommended package | Current verdict |
| --- | --- | --- | --- |
| Saladin / Arabia | Ayyubid cavalry, trade routes, and madrasa-backed coalition | Keep Camel Archer and Madrassa; enrich `TRAIT_SALADIN` with incense/spice and Merchant commerce | UU KEEP; UB KEEP; trait MODIFY |
| Alexander / Macedon | Combined-arms shock conquest | Hypaspist UU using the dormant Macedonian package; Companion Barracks; extend Alexander's promotion identity to mounted units without duplicating every melee bonus | Phalanx REPLACE; Odeon REPLACE; trait MODIFY |
| Pericles / Athens | Naval empire financing culture and specialists | Athenian Trireme; keep and coastalize the Odeon; retain GP-focused trait | Phalanx REPLACE; Odeon MODIFY; trait KEEP |
| Louis XIV / Bourbon France | Court culture, centralized finance, and royal manufactures | Keep Musketeer and Salon; replace Broadcast Tower with Manufacture Royale; rebalance Louis's extreme raw upkeep/GP/gold scalars into culture, Artists, and production | Musketeer KEEP/MODIFY; Salon MODIFY; Broadcast Tower REPLACE; trait REBALANCE |
| Justinian / Byzantium | Reconquest, law, orthodoxy, and monumental urban culture | Keep Cataphract and Hippodrome; add Corpus Juris courthouse; activate only proven Cataphract combat fields; reduce trait/building maintenance stacking | UU KEEP/MODIFY; Hippodrome KEEP; second UB ADD; trait REBALANCE |
| Mehmed / Ottoman Conquest | Gunpowder siege and conquest of Constantinople | Keep Janissary and Bombard; replace Hammam with Devshirme Barracks; rewrite trait around unit development and Great Generals | UUs KEEP; UB REPLACE; trait REWRITE |
| Suleiman / Classical Ottoman | Law, commerce, architecture, and Mediterranean power | Sipahi and Ottoman Galleass; Kulliye aqueduct; trade-route/courthouse commerce in trait, with the over-scaling Road yield removed | UUs REPLACE; UB MODIFY/RENAME; trait MODIFY |
| Barclay / Federal America | Fictional satirical security bureaucracy | Border Patrol Agent; Federal Bureau; consolidate Protective/Organized/espionage into one bespoke `TRAIT_BARCLAY` | UU REPLACE; UB REPLACE; traits REPLACE |
| Napoleon / First Empire | Operational mobility, mass armies, and standardized administration | Napoleonic Dragoon using BTG art; Prefecture courthouse; rebuild `TRAIT_GRANDE_ARMEE` around mobility, faster leveling, and positive GG generation without free Leadership on every unit | Musketeer REPLACE; French UBs REPLACE; trait REWRITE |
| Brennus / Gaulic Confederation | War league, mercenary shock infantry, druids, and oppida economy | Gaesatae; Nemeton courthouse/temple hybrid; retain pillage identity and add Priest/culture support | Gallic Warrior REPLACE; Dun REPLACE; trait MODIFY |
| Boudica / Iceni Britain | Chariot-led anti-occupation revolt | Boudiccan Chariot using the female Celtic chariot package; Iceni Hall; mounted Shock/withdrawal identity | Gallic Warrior REPLACE; Dun REPLACE; trait MODIFY |
| Charlemagne / Carolingian Empire | Frontier marches, Frankish warfare, and scriptoria | Frankish Axethrower using the dormant Frank package; Scriptorium; retain expansion/scriptoria identity without excessive Great General or Priest-research stacking | Landsknecht REPLACE; Rathaus REPLACE; trait MODIFY |
| Cyrus / Founding Achaemenid | Mobile coalition, tolerance, and imperial foundation | Keep/tune Immortal; Pasargadae Decree monument using Tomb of Cyrus/Cylinder art; replace raw GG focus with happiness, culture, and mounted mobility | UU MODIFY; UB REPLACE; trait REWRITE |
| Darius / Imperial Achaemenid | Satrapies, Royal Road, taxation, and standardization | Takabara spearman; keep Satrapy Archive exclusively; trade/Merchant trait, with the over-scaling Road yield removed | Immortal REPLACE; UB KEEP; trait REWRITE |
| Frederick / Prussia | Disciplined mobile army plus Enlightenment administration | Zieten Hussar; Prussian Academy; keep strong GP/upkeep core with only modest toleration polish | Panzer REPLACE; Assembly Plant REPLACE; trait KEEP/MINOR MODIFY |
| Julius Caesar / Late Republic | Fast campaigning, siege engineering, and veteran legions | BTG Legionary; Castrum barracks; keep March-centered trait but balance its stacking | Praetorian REPLACE; Forum REPLACE; trait KEEP |
| Augustus / Principate | Veteran settlement, infrastructure, and stable imperial administration | Defensive Praetorian; Colonia granary; shift some GG budget into the already-supported building-production field | UU MODIFY; Forum REPLACE; trait MODIFY |
| Mansa Musa / Mali | Gold, caravan taxation, and scholarly commerce | Keep Skirmisher, Mint, and Mali Market; fill blank trait with gold-resource and Merchant value, without the over-scaling Road yield | UUs/UBs KEEP; trait FILL |
| FDR / New Deal America | Public works converted into wartime production | Marine Raider; Federal Relief Depot; extend Roosevelt trait through Engineer production and civic culture | Navy SEAL REPLACE; Mall REPLACE; trait MODIFY |
| Hatshepsut / Eighteenth Dynasty | Peaceful building program and Punt trade | Preserve Sphinx system; split shared entries into Royal Expedition Chariot and Karnak Obelisk; add AI weight only through existing XML fields | Shared UU/UB REPLACE with dedicated variants; trait KEEP |
| Ramesses / New Kingdom | Kadesh chariot warfare and monumental kingship | Battle Chariot and Temple of Ramesses; fill blank trait with chariot promotion, Engineer production, and supported building-production bonus | Shared UU/UB REPLACE with dedicated variants; trait FILL |
| Dowager / British Regency | Fictional estate hierarchy, social influence, and information control | County Lancers; Country Estate using a valid live building class; merge Paranoid/Pacifist into `TRAIT_DOWAGER_COUNTESS` | Redcoat REPLACE; Stock Exchange REPLACE; traits REPLACE |
| Zara Yaqob / Solomonic Ethiopia | Centralized Orthodox monarchy and disciplined highland defense | Agaw/royal highland infantry; Tabot Shrine; culture/Priest/religious-defense trait | Oromo REPLACE; Stele REPLACE; trait FILL |
| Haile Selassie / Imperial Ethiopia | Modernization, Arbegnoch resistance, and diplomacy | Arbegnoch Rifleman using African rifle art; Imperial University using Afro Academy art; espionage/guerrilla trait | Oromo REPLACE; Stele REPLACE; trait REWRITE |
| Gilgamesh / Sumeria | Irrigation, walls, writing, and early urban state | Keep Vulture and Ziggurat; add floodplain/farm and defensive city identity rather than remapping Ziggurat to an unrelated class | UU KEEP; UB KEEP/MODIFY; trait MODIFY |
| Lincoln / Union America | Emancipation, federal mobilization, rail, land-grant education, and national banking | USCT Rifleman; repair Land Grant College science role; keep National Bank; add rail/scientist channels to Lincoln trait | UU ADD; UBs KEEP/MODIFY; trait MODIFY |
| Victoria / Victorian Britain | Industry, global trade, navy, and empire | Keep Redcoat and Stock Exchange; retain the already rich trait with tuning/documentation; add Victorian Ironclad only if full art closure passes | UU/UB KEEP; second UU ART-GATED; trait TUNE |

## Art Feasibility

Concrete repository candidates already found:

- Macedon: `Art/Caveman2Cosmos/art/units/unique/macedonia/hypaspistai`
- Rome: `Art/BTG/Units/legion1` (complete NIF/KFM/KF package)
- Napoleon: `Art/BTG/Units/NapoleonicDragoons`
- Ottoman navy: `Art/BTG/Units/uu_venice_galleass` (complete NIF/KFM/KF package)
- Ottoman cavalry: `Art/Caveman2Cosmos/art/unique/seljuks/sipahi`
- Gaul: `Art/Caveman2Cosmos/art/units/celtic_sparth/light_swordsman`
- Iceni: `Art/Caveman2Cosmos/art/units/celtic_sparth/chariot`
- Prussia: C2C Hungarian Hussar or a proven mounted fallback; package closure is mandatory before selection
- Victoria: `Art/Caveman2Cosmos/art/units/ships/advanced_ironclad`
- Ethiopia: `Art/Caveman2Cosmos/art/units/african_sparth/rifleman`
- Dowager: `Art/Caveman2Cosmos/art/structures/buildings/estate`
- Academy variants: `Art/Caveman2Cosmos/art/structures/buildings/academy`
- Cyrus: `Art/BTG/Buildings/Tomb of Cyrus` and
  `Art/Caveman2Cosmos/art/structures/buildings/cyruscylinder`

Some candidate folders contain only a NIF and textures because they expect a
stock KFM. That is not automatically invalid, but the selected art definition
must point to a real compatible KFM and pass in-game animation testing. A
missing local KFM must never be papered over with an unverified path.

The documented external libraries are absent on this machine. The plan does
not depend on them.

## Proposed Implementation Steps

1. **Create machine-readable baseline and feasibility checks**
   - Generate a target roster snapshot from live XML.
   - Verify every proposed unit/building class, XML field, promotion, tech,
     bonus, specialist, and art tag exists.
   - Port only the useful read-only portions of the later art-inventory tooling
     if they reduce manual error; do not import its new-leader assumptions.
   - Reject or replace any proposal that requires a DLL change.

2. **Implement shared text/art scaffolding**
   - Add dedicated text files grouped by family.
   - Add dedicated art definitions instead of repointing shared stock tags.
   - Use unique type IDs for every split UU/UB even when two entries share a
     base class.

3. **Batch A: duplicated ancient/classical packages**
   - Macedon, Athens, Caesar, Augustus, Byzantium, Gaul, Iceni, Sumeria.
   - Validate land, naval, and mounted art before moving on.

4. **Batch B: Near East empires**
   - Arabia, Mehmed, Suleiman, Cyrus, Darius.
   - Validate Galleass animation closure and trade trait tooltips.

5. **Batch C: Europe**
   - Louis, Napoleon, Charlemagne, Frederick, Victoria, Dowager.
   - Validate Napoleonic, Hussar, Lancer, Ironclad, academy, and estate art.

6. **Batch D: Africa**
   - Mansa Musa, Hatshepsut, Ramesses, Zara Yaqob, Haile Selassie.
   - Preserve Hatshepsut's working Sphinx system; create dedicated Egypt and
     Ethiopia unit/building types rather than mutating shared entries.

7. **Batch E: Americas**
   - Lincoln, FDR, Barclay.
   - Keep the three American identities non-overlapping in era, unit role,
     building class, and economic engine.

8. **Cross-roster balance and UI pass**
   - Compare each trait's total scalar and mapped-channel budget.
   - Remove accidental duplicate identities and excessive maintenance/GP/XP
     stacking.
   - Ensure Civilopedia, strategy, pedia, trait-help, and hover text expose
     every mechanic in plain English.
   - Check AI build roles and leader flavor alignment for every new UU/UB.

9. **Full validation and one-commit handoff**
   - Run the changed-file gate after each batch.
   - Run full XML and final repository gates.
   - Perform installed-game Civilopedia and gameplay smoke tests.
   - Commit all approved implementation, art, text, tests/tooling, and this
     plan as one commit.

## Validation Plan

### Automated

- XML parse and reference checks for all target type IDs.
- No duplicate `Type` values.
- Every civ mapping resolves to a live unit/building.
- Every trait field exists in the current schema and is already supported by
  the checked-in DLL; no DLL source changes.
- Every art definition resolves its button, NIF, shader NIF, KFM, referenced
  KF animations, and embedded textures.
- Every new button is a valid Civ4-compatible DDS with expected dimensions.
- `.\tools\test_gate.ps1` after each coherent batch.
- `.\tools\test_xml.ps1 -All` and `.\tools\test_full.ps1` at final integration.
- `.\tools\test_gate.ps1 -CheckDll` at final integration to prove XML remains
  compatible with the existing DLL even though DLL source is unchanged.

### Manual installed-game smoke test

- Run the canonical root installer from the completed branch.
- Open every changed leader, civ, trait, UU, and UB Civilopedia page.
- Verify every new animated unit model renders without a blank page or crash.
- Start representative Ancient, Medieval/Renaissance, Industrial, naval, and
  modern scenarios.
- Unlock each changed UU/UB, inspect build lists, build/select/move/combat/die
  with every new unit, and construct every new building.
- Exercise road/resource/specialist/improvement trait channels with before/after
  yield checks.
- End turns, save, reload, and re-open affected Civilopedia pages.
- Run at least one AI autoplay or observer game long enough to exercise all
  eras and inspect missing-unit, runaway-economy, and build-priority failures.

## Documentation Updates Required

- This plan remains the implementation record.
- Update `docs/index.md` only if new permanent runbooks or tooling are added.
- Update `docs/LEADER_OVERHAUL_PLAN_OF_RECORD.md` only for genuinely reusable
  lessons, not package-specific details.
- Mark the Brennus draft as superseded if its design is implemented.
- Add a concise roster-differentiation table to an existing player-facing doc
  if one exists; do not create redundant architecture prose.

## Risks / Rollback

- **Art crash risk:** mitigated by dedicated art tags, dependency-closure
  checks, Civilopedia render tests, and full animation smoke tests.
- **Trait overstacking:** especially Louis, Justinian, Napoleon, Frederick,
  Lincoln, and Mansa. Mitigate through whole-package budgets rather than
  one-field balancing.
- **Naval AI:** Athens and Suleiman need valid naval `UnitAI` roles and
  observer-game checks.
- **Map dependence:** resource/road/coastal traits need a useful baseline even
  when their preferred geography is absent.
- **Dormant art quality:** imported C2C art is a candidate library, not trusted
  runtime art. Reject incomplete packages rather than mixing skeletons.
- **Rollback:** one final commit allows complete branch rollback. Within the
  commit, dedicated IDs and art tags isolate each package so a single civ can
  be reverted without changing shared stock definitions.

## Open Questions Resolved During Implementation

- Use only live classes (`UNITCLASS_RIFLEMAN`, not the stale `UNITCLASS_RIFLE`;
  no nonexistent `BUILDINGCLASS_GARDEN`).
- Different civs may map different buildings to the same base class; no new
  class is needed merely to separate their UBs.
- Oppidum inner-ring/cap mechanics are excluded unless already expressible by
  current XML fields; no DLL exception will be made.
- Victoria's second Ironclad and any incomplete Hussar package are art-gated,
  not implementation blockers.
- External asset libraries are optional and currently unavailable.

## Completion Checklist

- [x] All 27 live baselines and proposed IDs are machine-verified.
- [x] Every package has a historical thesis and distinct gameplay thesis.
- [x] Every current UU/UB has a KEEP/MODIFY/REPLACE verdict.
- [x] No new DLL mechanics or DLL source edits were introduced.
- [x] Every selected art package passes static dependency closure.
- [x] Every mechanic is exposed in Civilopedia/help text.
- [x] AI roles and leader flavors were reviewed.
- [x] Batch and final automated gates pass.
- [ ] Installed-game Civilopedia and gameplay smoke tests pass.
- [x] All changes are committed once on the dedicated branch.

## Implementation Notes

- Batches A-E are implemented for all 27 requested leader/civilization pairs.
  Every formerly shared target pair now maps to materially distinct unit and
  building packages; intentional KEEP packages remain isolated from the other
  requested pairs.
- The cross-roster integration pass verified class mappings, prerequisites,
  resources, upgrades, unit combats, AI roles, specialist slots, flavors,
  positional yield/commerce arrays, text references, and art-definition
  closure.
- Invalid promotion combinations were removed or narrowed: Alexander no
  longer attempts to grant Sentry to Melee units, Napoleon grants Mobility
  only to Mounted units, Zara's Melee/Guerrilla combination was removed, the
  Federal Border Patrol Agent no longer carries an inapplicable Sentry
  promotion, and Justinian's Christian Missionary no longer carries combat
  promotions it cannot use.
- The shared base Musketman was restored rather than changed to differentiate
  a target unique. The Satrapy Archive now preserves the Courthouse's Modern
  free-start behavior.
- Target text keys now resolve without same-layer duplicate overrides, and
  custom NIF/KFM/KF/texture paths have static dependency closure. Automated
  closure does not replace in-game model and animation smoke testing.
- Custom long and short trait labels use dedicated diversity keys rather than
  overriding stock/Warlords localization keys. Existing cross-expansion stock
  definitions and their unrelated translations remain untouched.
- Zara's Tabot Shrine intentionally occupies `BUILDINGCLASS_OBELISK`, the
  former Ethiopian Stele/Monument slot, rather than a Temple class. It is an
  early Mysticism building with no religion prerequisite, obsoletes at
  Astronomy, and provides 1 Happiness, 1 Culture, +15% Culture, and one Priest
  slot. Zara's separate Christian Temple culture bonus remains trait-driven.
- Victoria's Ironclad remains intentionally deferred. Victorian Britain keeps
  the Redcoat and Stock Exchange only until the proposed second UU has
  complete art closure and installed-game animation testing.
- Batch gates and the final full repository gate pass. The final gate checked
  66 Python files for Python 2.4 compatibility, validated 156 XML files, and
  completed a clean DLL compatibility build. The build's generated DLL and
  backup were removed afterward, leaving no native binary or source delta.
- No installed-game validation or deployment claim is made here.
  Civilopedia review and gameplay smoke tests remain open; the dedicated
  implementation handoff is complete.

## Final Outcome Summary

- Content implementation, cross-roster static integration, full automated
  validation, and the one-commit handoff are complete. Installed-game
  validation remains pending before merge or deployment.
