# Detailed Overhaul V4 – Frederick (Prussia)

- GitHub Issue: #45
- Branch: `symphony/45-detailed-overhaul-v4-design-a-new-frederick`
- Status: `design complete`
- Last updated: 2026-03-13

## 1) Historical Summary (Plain English)
Frederick II inherited the Prussian throne in 1740, immediately seized Silesia from Austria, and spent the next two decades executing rapid campaigns that fused his father’s drilled army with his own flair for maneuver warfare; victories at Hohenfriedberg, Rossbach, and the oblique-order masterpiece at Leuthen convinced Europe that Prussia could survive against larger coalitions if its logistics and staff kept pace with Frederick’s operational audacity.[^1][^5] The army that carried those campaigns rested on the canton system formalized only a few years earlier, which bound each regiment to specific recruiting districts so that peasant households could rotate into three-month training blocks before returning to farms, giving Frederick a reserve pool that could be mobilized quickly when the front collapsed or new regiments had to be raised.[^3] While campaigning, Frederick also tightened central administration: he expanded the General Directory with new commerce, mining, and forestry departments so that tax enforcement, war finance, and provincial development all reported through a single audit chain that he annotated personally.[^2]

After the traumatic Seven Years’ War he doubled down on cameralist economic fixes: new indirect taxes, protected tariffs, and a school-reform program anchored by the 1763 general school law modernized bureaucracy while keeping Junker nobles loyal through continued control of the officer corps.[^2][^4] Frederick’s self-described “peopling policy” drained the Oderbruch marshes, built the Finow and Bromberg canal links, and invited more than 300,000 immigrants—Huguenots, Salzburg Protestants, Jesuit educators, and Jewish merchants—to settle reclaimed land so that grain surpluses and workshops could fund future mobilizations without crushing urban populations.[^4] This hybrid of canton militarism, centralized paper trails, industrial patronage, and selective toleration defines the historical pillars for his overhaul: Prussia’s military resiliency depended on drilled reserves tied to districts, civil servants who could micromanage industrial quotas, canal-fed workshops, and a propaganda narrative that Frederick was the “first servant of the state.”

## 2) Sources
1. Matthew S. Anderson, “Frederick II,” *Encyclopaedia Britannica*, updated February 27, 2026.[^1]
2. Matthew S. Anderson, “Frederick II – Domestic Policies,” *Encyclopaedia Britannica*, updated February 27, 2026.[^2]
3. “Introduction of the Brandenburg-Prussian Canton System of Military Recruitment,” German History in Documents and Images.[^3]
4. “Prussia Under Frederick the Great,” *History of Western Civilization II* (Lumen Learning).[^4]
5. Vince Hawkins, “Frederick the Great at Leuthen: The Oblique Order,” *Warfare History Network*.[^5]

## 3) Salient Pillars
1. **Cantonist Machine** – Regiment-linked districts rotating peasants into short-service training created a rapid mobilization backbone.[^3]
2. **General Directory Oversight** – Frederick’s habit of annotating fiscal and provincial dossiers tied war, finance, and infrastructure under one office.[^2]
3. **Canal-Backed Cameralism** – Finow/Oderbruch drainage and Bromberg links tied industrial workshops to crown supervision and grain reserves.[^4]
4. **Refugee Toleration for Talent** – Promoting Jesuits, Huguenots, and Jewish bankers into Prussian towns accelerated artisan and scientific capacity.[^4]
5. **Oblique-Order Professionalism** – Regiment-level drilling plus staff discipline let Frederick pivot entire armies at Leuthen for local superiority.[^1][^5]

## 4) History → Mechanics Mapping
- **Cantonist Machine** → Leader trait grants worked-Town science commerce and Plains/Grassland Workshop hammers, while the Canton Reserve novel mechanic (see §6) stores charges whenever Barracks cities finish land units, enabling instant fusilier mobilization to simulate regimental depots.
- **General Directory Oversight** → Courthouse-class UB (Generaldirektorium) adds stronger maintenance reduction, specialist slots, and +25% production toward buildings flagged with `IndustryCategory`, representing paperwork-driven acceleration of core industries.
- **Canal-Backed Cameralism** → Trait river-farm commerce and water mill production bonuses reward canal corridors; UB grants conditional gold bonus when Core Industry requirements are met, nudging players to pair canals, industries, and bureaucrats.
- **Refugee Toleration for Talent** → Trait gives +1 gold to all specialists in cities containing at least two religions plus +25% Great Person Rate to mirror Frederick’s pragmatic toleration; UB adds +2 GPP and mixed specialist slots to represent Jesuit-led academies.
- **Oblique-Order Professionalism** → UU (Frederician Fusilier) replaces Musketman with Drill I and new Oblique Order promotion (first strike + withdrawal) plus +15% vs Gunpowder, while Barracks-trained gunpowder units receive free Drill I to propagate Frederick’s drill schools.

## 4b) Novel Mechanic Candidates and Decision Log
| Candidate | Historical Anchor & History-to-Formula | XML/DLL Touchpoints | AI Plan | Decision |
| --- | --- | --- | --- | --- |
| **Canton Reserve Meter** (Selected) | 1733 canton orders plus Leuthen-era depots → player stores up to 3 charges; each qualifying land unit built in a Barracks/Armory city adds 1; consuming a charge via new city button instantly spawns a 6 XP Frederician Fusilier with 1-turn immobility and adds +25% city maintenance for 5 turns.[^3][^5] | New `bEnableCantonReserve` trait flag, `CvPlayer::m_iCantonReserve`, serialized save data, Python city command hook, UI pip in HUD. | Tactical AI saves 2 charges before offensive DoW, reaction AI fires when hostile stack ≤6 tiles. | **Selected** – satisfies traceability, distinct decision layer, AI spec, emergent gameplay, and has a clear fallback (+2 XP to Barracks gunpowder units) if DLL work slips. |
| **State Canal Edict** | 1760s Oderbruch/Bromberg program → toggle in canal-adjacent cities to push +15% building production but -1 food until a Core Industry completes, simulating forced labor on waterways.[^4] | Would require city-level state toggle referencing `FeatureRiver` adjacency and `IndustryCategory`; new UI states. | AI would need to predict surplus food and industry backlog. | **Rejected** – micromanagement-heavy, food penalty punishes AI more than players, and UB already covers canal incentives. |
| **Royal Refugee Lottery** | Frederick’s mass immigration edicts promising land regardless of faith → empire project that, once every 30 turns, converts 2 population in capital into 2 free Specialists plus +2 happiness empire-wide.[^4] | Project entry + DLL to spawn specialists empire-wide. | Hard to teach AI to time growth vs whip; overlaps with Golden Age economy. | **Rejected** – effect duplicates existing specialist bursts and destabilizes tall cities. |

## 5) Mechanics Coverage Check
| Entry | Key Mechanics Reviewed | Used? | Reason if not used | Source Mode |
| --- | --- | --- | --- | --- |
| Civ4BuildingInfos | Costs, BuildingClass replacements, specialist slots, `BuildingClassProductionModifiers`, `IndustryCategory` tags. | Yes | UB relies on Courthouse class swap and IndustryCategory-aware production. | Web |
| Civ4CivilizationInfos | Leader slots, free units/tech, unit art, diplomacy text. | Yes | Need to remap Frederick to new trait/UU/UB and update diplo text. | Web |
| Civ4TraitInfos | Scalar modifiers, Improvement yield hooks, `SpecialistCommerceChanges`, free promotions. | Yes | Trait drives tile buffs, specialist gold, upkeep, Drill I gating, and Canton flag. | Web |
| Civ4ImprovementInfos | Base yields, tech prereqs, upgrade chains. | Partial | No new improvement created per constraint; only referenced to balance workshop/farm buffs. | Web |
| Civ4SpecialUnitInfos | Replacement limits for workers/missionaries. | No | UU shares existing Musketman class; no unique special unit required. | Web |
| Civ4PromotionInfos | Combat modifiers, first strikes, prerequisites. | Yes | Adds `PROMOTION_OBLIQUE_ORDER` for UU and upgrade path. | Web |
| Civ4UnitClassInfos | Determines Musketman replacement mapping. | Yes | Map `UNITCLASS_MUSKETMAN` → `UNIT_FREDERICIAN_FUSILIER` for Frederick’s civ only. | Web |
| Civ4UnitInfos | Strength, cost, XP, default promotions. | Yes | Defines UU stats, art, and Canton synergy. | Web |
| Trait-level Improvement Yield hooks | `ImprovementYieldChanges`, `ImprovementCityCommerceChangesWorked/BFC`. | Yes | Trait uses Town science bonus and Plains/Grassland Workshop hammer boosts. | Repo |
| Trait-level building/specialist/bonus hooks | `BuildingCommerceChanges`, `SpecialistCommerceChanges`. | Yes | Multi-religion specialist gold and UB-dependent gold bonus. | Repo |
| Civic-level improvement commerce hooks | Civic `ImprovementCityCommerceChanges`. | No | Scope limited to leader trait this issue; civics untouched. | Repo |
| Civ-specific unique improvement framework | Custom `ImprovementInfo`, Build button, cap handlers. | No | User forbade new UI; economy covered via trait/UB instead. | Repo |
| Rare improvement caps | Per-player cap elements. | No | Not applicable without unique improvement. | Repo |
| IndustryCategory & local prereq schema | `IndustryCategory`, `bRequiresActiveLocalPrereqs`, `iPlayerMaxInstances` tags in `CIV4BuildingsSchema`. | Yes | UB references IndustryCategory to accelerate Core/Composite industries while respecting prereqs. | Repo |

**Newly Discovered Since Last Scan**
- `bRequiresActiveLocalPrereqs` (CIV4BuildingsSchema.xml lines 367-489) clarifies that Industry bonuses must check local resource fulfillment; UB design assumes this gating when adding conditional +10% gold.
- `iPlayerMaxInstances` (same schema block) offers optional per-player cap if future balancing requires limiting Generaldirektorium per civ (not needed now but recorded).

## 6) Final Overhaul Spec
### Leader Trait – `TRAIT_PHILOSOPHER_GENERAL`
- `+25%` Great People Rate (`iGreatPeopleRateModifier`).
- `+20%` Domestic Great General Rate.
- `-20%` empire upkeep (`iUpkeepModifier`).
- Worked Towns yield `+1` science via `ImprovementCityCommerceChangesWorked`.
- Workshops on Plains or Grassland gain `+1` hammer through `ImprovementYieldChanges`; Farms adjacent to rivers gain `+1` commerce.
- Specialists in cities containing at least two religions receive `+1` gold (`SpecialistCommerceChanges` plus DLL check for `iMinReligionsInCity=2`).
- Gunpowder land units built in cities with a Barracks receive free `PROMOTION_DRILL1` and unlock `PROMOTION_OBLIQUE_ORDER` if the city also has a Canton Reserve charge.
- Trait flag `bEnableCantonReserve=1` activates the novel mechanic described below.

### Unique Unit – `UNIT_FREDERICIAN_FUSILIER` (Musketman replacement)
- Cost 90 hammers (vanilla Musketman 80) but Strength 10 with innate `+15%` vs Gunpowder and `+10%` City Attack.
- Starts with `PROMOTION_OBLIQUE_ORDER`: `+1` first strike, `+10%` withdrawal, counts as prerequisite for Drill II-IV without additional XP.
- Gains `+2` XP if trained while a Canton Reserve charge is available in the producing city (charge not consumed unless Mobilize Canton command used).
- Art: reuse recolored Grenadier mesh (Prussian blue) added under `Art/Units/PrussianFusilier/` with new button; hook in `CIV4ArtDefines_Unit.xml`.

### Unique Building – `BUILDING_GENERALDIREKTORIUM` (Courthouse replacement)
- Base effects: -55% city maintenance (vs -50%), +1 espionage, +2 Great Person Points (all), +1 Merchant slot, +1 Scientist slot.
- Conditional bonus: if city has ≥1 building flagged with `IndustryCategory` and meets local resource prerequisites, gain +10% gold and +1 flat gold via `BuildingCommerceChanges`.
- Production kicker: +25% production toward buildings with `IndustryCategory` (Core, Composite, Luxury) implemented either via enumerated `BuildingClassProductionModifiers` or new DLL helper that checks the category tag each build.
- Synergy requirement: requires Courthouse tech prereqs plus Barracks or Custom House to reflect dual military-fiscal oversight.

### Novel Mechanic – Canton Reserve Meter
- Player stores up to 3 charges (UI pips near top bar). Each time a city with Barracks, Armory, or West Point finishes a Melee or Gunpowder unit, add 1 charge (cap 3). Charges decay by 1 if unused for 25 turns.
- City screen gains `Mobilize Canton` command (cooldown 10 turns per city). Consuming 1 charge instantly produces a Frederician Fusilier with 6 XP, Oblique Order promotion, and 1-turn immobility; city suffers +25% maintenance for 5 turns to simulate provisioning costs.
- DLL touchpoints: `CvPlayer::changeCantonReserve`, `CvCity::canMobilizeCanton`, mission handling in `CvUnit`, Python/UI update in `CvMainInterface`.
- Fallback (if DLL hook deferred): trait instead grants +2 XP to Gunpowder units in cities with Barracks and +10% military unit production, without reserve UI.

### Personality & Diplomacy
- Flavors: Military 9, Production 7, Science 7, Gold 6, Religion 2.
- Favorite civic: Bureaucracy; disliked civic: Theocracy (conflicts with toleration narrative).
- Higher weight on Industry-category building flavors so AI pursues UB synergy.
- New diplo text references “canton reserves” when threatening war and “canal inspectors” when complimenting infrastructure.

### No Unique Improvement (per constraint)
Econ identity is satisfied through trait tile buffs and the Generaldirektorium’s industry hooks; no new `ImprovementInfo` objects introduced.

## 6b) Quantified Balance Table
| Mechanic | Numeric Effect | Target / Scope | Trigger / Condition | Era Timing | Impact | Counterplay / Constraint |
| --- | --- | --- | --- | --- | --- | --- |
| Town Science Census | Worked Towns +1 science | Improvement (Town) | Citizen must work tile | Renaissance+ | Medium | Pillaging or spying on towns suppresses bonus |
| Canton Workshops | +1 hammer on Plains/Grassland Workshops | Improvement | Requires Workshop + Chemistry | Renaissance | Medium-High | Consumes food; pillage to slow |
| River Farm Canals | +1 commerce on river Farms | Improvement | Farm must touch river | Medieval | Low | Limited by terrain; pillage |
| Multi-Faith Ledgers | Specialists +1 gold in ≥2-religion cities | City specialists | City houses at least two religions | Medieval | Medium | Missionary/spy pressure can deny second religion |
| Drill Patronage | Gunpowder units gain free Drill I in Barracks cities | Units (Gunpowder) | Built where Barracks present | Renaissance | Medium | Target Barracks with espionage; traitless civs still pay higher costs |
| Canton Reserve Meter | Stores up to 3 charges; Mobilize spawns 6 XP Fusilier, +25% city maintenance for 5 turns | Player/city | Charges earned via land-unit builds; command cooldown 10 turns | Renaissance–Industrial | High | Charges decay; high maintenance discourages spam; siege prevents mobilization |
| Frederician Fusilier | 90h, Str 10, +15% vs Gunpowder, +10% City Attack, Oblique Order | Unit | Available with Gunpowder | Renaissance | High | Costs more than Musketman; counter with Cavalry/flanking |
| Oblique Order Promotion | +1 first strike, +10% withdraw, unlocks Drill line | Promotion | Granted to UU/eligible upgrades | Renaissance | Medium | Requires Drill path; vulnerable to anti-first-strike promos |
| Generaldirektorium | -55% maintenance, +2 GPP, +1 Merch +1 Sci slot, +1 espionage, +10%/+1 gold with active IndustryCategory, +25% Industry building production | City building | Requires Code of Laws + Barracks/Custom House | Medieval | Medium-High | Bonus turns off without Core Industry; higher hammer cost than Courthouse |

## 7) Implementation Plan
1. **Data audit** – Snapshot current Frederick trait/UU/UB definitions in `CIV4LeaderHeadInfos.xml`, `CIV4TraitInfos.xml`, `CIV4CivilizationInfos.xml`, `CIV4UnitInfos.xml`, and `CIV4BuildingInfos.xml` for regression diffing.
2. **XML updates**
   - Add `TRAIT_PHILOSOPHER_GENERAL` definition with modifiers listed above.
   - Create `BUILDING_GENERALDIREKTORIUM` entry, update `BuildingClassInfos` to map German civ to UB, and add text keys.
   - Create `UNIT_FREDERICIAN_FUSILIER`, remap `UNITCLASS_MUSKETMAN` for Frederick’s civ entry, update ArtDefines.
   - Add `PROMOTION_OBLIQUE_ORDER` entry in `CIV4PromotionInfos.xml` and tie to UU.
   - Update `CIV4GameText_Leader_Civilopedia.xml` (trait text, unit/building pedia) and diplomacy lines referencing new mechanics.
3. **DLL/schema work**
   - Extend `CvTraitInfo`/schema for `bEnableCantonReserve` plus optional `iMultiReligionSpecialistCommerce` threshold.
   - Implement Canton Reserve counters, serialization, mission handling, cooldown logic, and UI pip.
   - Add helper for checking `IndustryCategory` when applying UB production modifier if enumerations prove too brittle.
4. **Python/UI**
   - Update `CvMainInterface.py` (or petromod_v1 delegate) to render Canton Reserve pips and tooltips.
   - Add city-screen button + help text for Mobilize Canton.
5. **Art**
   - Import/recolor fusilier models/buttons into repo tree and reference in ArtDefines; create UB button using existing Courthouse art with Prussian crest overlay.
6. **Validation**
   - Run `.\tools\test_gate.ps1` after XML edits (expect trait/unit/building schema touch).
   - Run `.\tools\test_gate.ps1 -CheckDll` once DLL mechanic implemented.
   - Manual smoke test per `docs/MANUAL_SMOKE_TESTS.md`: start new game, verify trait text, build Canton charges, test Mobilize command, confirm UB conditional gold, and ensure AI behavior (WorldBuilder) consumes charges when threatened.
7. **Docs**
   - Update `docs/index.md` if referencing this design elsewhere; append to `LEADER_OVERHAUL_PLAN_OF_RECORD.md` if needed.

## 8) Distinctiveness Audit
- Trait combines Town science, workshop hammers, multi-faith specialist gold, and upkeep reduction—no other leader in this mod ties mixed tile economies to religious pluralism plus a reserve meter, differentiating Frederick from existing economic/military hybrids.
- UU shifts Germany’s military identity from late-game armor (Panzer) to mid-game disciplined infantry with bespoke promotion gating, avoiding overlap with any other musket-class unique.
- UB leverages the repo’s IndustryCategory schema and maintenance scaling rather than generic courthouse buffs; Frederick becomes the only civ that speeds Core/Composite industry builds without introducing a unique improvement.
- Novel Canton Reserve introduces a discrete tempo resource that rewards planning instead of flat stat inflation, reinforcing Frederick’s historical logistics without simply giving cheaper units.

[^1]: Matthew S. Anderson, “Frederick II,” *Encyclopaedia Britannica*, https://www.britannica.com/biography/Frederick-II-king-of-Prussia (accessed March 12, 2026).
[^2]: Matthew S. Anderson, “Frederick II – Domestic Policies,” *Encyclopaedia Britannica*, https://www.britannica.com/biography/Frederick-II-king-of-Prussia/Domestic-policies (accessed March 12, 2026).
[^3]: “Introduction of the Brandenburg-Prussian Canton System of Military Recruitment [Kantonreglement]” (May 1, 1733), German History in Documents and Images, https://germanhistorydocs.org/en/the-holy-roman-empire-1648-1815/ghdi:document-3581 (accessed March 12, 2026).
[^4]: “Prussia Under Frederick the Great,” *History of Western Civilization II* (Lumen Learning), https://courses.lumenlearning.com/suny-hccc-worldhistory2/chapter/prussia-under-frederick-the-great/ (accessed March 12, 2026).
[^5]: Vince Hawkins, “Frederick the Great at Leuthen: The Oblique Order,” *Warfare History Network*, https://warfarehistorynetwork.com/article/frederick-the-great-at-leuthen-the-oblique-order/ (accessed March 12, 2026).
