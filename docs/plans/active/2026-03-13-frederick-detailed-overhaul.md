# Detailed Overhaul V4 – Frederick (Prussia)

- GitHub Issue: #45
- Branch: `symphony/45-detailed-overhaul-v4-design-a-new-frederick`
- Status: `design complete`
- Last updated: 2026-03-13

## Plan-of-Record Checklist (docs/LEADER_OVERHAUL_PLAN_OF_RECORD.md)
- Historical thesis: "Frederick II fused a militarized canton system with enlightened absolutism, turning Silesia’s wealth and refugee talent into a drill-and-reform machine." ✔
- Gameplay thesis: "Hybrid pressure civ that spikes in mid-game wars through disciplined line infantry and industry-backed bureaucracy, then transitions into late-game science/gold scaling." ✔
- Power budget thesis: `Hybrid` (trait delivers map economy; UU/UB deliver military + admin spikes). ✔
- Trait channels evaluated: scalar modifiers, ImprovementYieldChanges, ImprovementCityCommerceChangesWorked, BuildingCommerceChanges (selected subset noted below). ✔
- UU decision: `REPLACE` vanilla Panzer with `Frederician Fusilier` (Musketman-class) for era fidelity and to avoid overlap with other German leaders. ✔
- UB decision: `REPLACE` vanilla Assembly Plant with `Generaldirektorium` (Courthouse-class) to foreground Frederick’s administrative reforms. ✔
- Unique improvement decision: `None` (per issue constraint) – documented rationale in spec. ✔
- Art sourcing plan: Searched workspace `CIV4ArtDefines_Unit.xml` (found `ART_DEF_UNIT_FREDERICK_BARBAROSSA`) and external library `C:\Users\Harrison\Downloads\civ4mods-code` for "Fusilier" assets (multiple unit meshes/buttons such as `Art/Units/Unique/Austria/Fusilier Austria`). Identified viable donor meshes for a Prussian blue fusilier variant; future implementation will copy chosen asset into `CoreFiles/.../Assets/Art/Units/PrussianFusilier/`. ✔
- UI clarity plan: Trait text will list each tile/class effect in bullet form; UU/UB Civilopedia entries describe conditional bonuses (worked-tile vs. BFC, canton reserve counter) in first paragraph per UI standard; diplo text updated for new playstyle cues. ✔
- AI impact notes: Documented evaluation logic for canton reserve meter, UU target selection, and admin economies in Implementation Plan. ✔

## 1) Historical Summary (Plain English)
Frederick II seized the Prussian throne in 1740 and immediately invaded Austrian Silesia, exploiting a newly drilled standing army trained through the canton system; his surprise victories at Mollwitz and Hohenfriedberg turned Prussia into a European power and yielded the rich textile and mining base that financed further reforms. citeturn0search0turn0search3turn0search13 After the Silesian Wars he codified enlightened absolutism by centralizing the General Directory, demanding that provincial war and finance colleges report to Berlin, and writing marginalia on bureaucratic memos to enforce austerity, canal building, and land reclamation programs that resettled refugees and introduced potatoes and clover rotations. citeturn0search3turn1search2turn1search9 Frederick simultaneously cultivated cameralist economics—rewarding silk weaving, porcelain works, and state credit banks—while also acting as "philosopher-king": he corresponded with Voltaire, reformed education, and enforced limited religious toleration to attract Huguenots, Silesian Protestants, and Salzburgers as skilled settlers. citeturn0search3turn0search8 During the Seven Years’ War (1756–1763) he weaponized oblique-order tactics, mobile artillery, and rapid forced marches to survive encirclement by Austria, Russia, and France; despite catastrophic losses such as Kunersdorf, the drilled reserve and British subsidies kept Prussia afloat until Peter III’s accession removed Russia from the war. citeturn0search0turn0search2 After 1763 Frederick doubled down on canals (e.g., Finow, Bromberg), draining marshes, and enforcing agricultural inspection tours, creating grain surpluses that supported cheap bread in Berlin while his officer corps supervised both civil works and regimental depots. citeturn1search2turn0search3 Late in his reign he institutionalized a dual identity: relentless military readiness plus measured patronage of philosophy, opera, and architecture at Sanssouci, aiming for a disciplined yet prosperous society tightly managed from the top. citeturn0search3turn0search8

## 2) Sources
1. Encyclopedia Britannica, “Frederick II | Biography, Accomplishments, & Facts.” citeturn0search0
2. Encyclopedia Britannica, “History of Europe – The Seven Years’ War.” citeturn0search3
3. Encyclopedia Britannica, “Prussia – Military and the Canton System.” citeturn0search13
4. Encyclopedia Britannica, “Agriculture and Industry Under Frederick the Great.” citeturn1search2
5. German History in Documents and Images, “Frederick II’s Instructions for his Provincial Officials (1763).” citeturn1search9
6. Encyclopedia Britannica, “Frederick the Great – Cultural Patronage and Enlightenment.” citeturn0search8

## 3) Salient Pillars
1. **Canton-Made Line Infantry** – Militarized provinces fed drilled regiments that executed oblique-order assaults even while marching under extreme attrition.
2. **Centralized General Directory** – Frederick’s handwritten directives enforced a single budget office spanning war, finance, and infrastructure.
3. **Cameralist Industrial Patronage** – State capital built silk, porcelain, and metal industries in Silesia tied to canals and refugee craft guilds.
4. **Refuge Toleration and Enlightened Schools** – Huguenots, Salzburgers, and domestic minorities gained freedom to settle, boosting artisan/scientific output.
5. **War-Ready Logistics with Lean Treasury** – Frederick hoarded cash, audited depots, and kept reserve battalions ready to redeploy within days.

## 4) History → Mechanics Mapping
- **Canton-Made Line Infantry** → Trait grants free Drill I to Gunpowder units built in cities with Barracks; UU replaces Musketman with stronger first-strike fusiliers; civic-style scaling via `ImprovementCityCommerceChangesWorked` on Villages/Towns to reward developed provinces feeding the army.
- **Centralized General Directory** → UB (Generaldirektorium) replaces Courthouse, increasing maintenance reduction, adding science/espionage commerce, and granting +25% production toward Industry-category buildings to reflect paperwork routing.
- **Cameralist Industrial Patronage** → Trait uses `ImprovementYieldChanges` to add +1  to Workshops on river/plains plus +1  to Watermills; UB adds Merchant slot and Gold% when Core Industry buildings are active (implemented via BuildingCommerceChanges and XML check for IndustryCategory tag on local buildings).
- **Refuge Toleration & Schools** → Trait grants +1  for Specialists in cities with at least two religions (via `SpecialistCommerceChanges` scoped by new text key) and +10% Great People rate globally; UB adds +2  Great Person Points and +1 Scientist slot to model academies.
- **War-Ready Logistics** → Novel mechanic `Canton Reserve Meter` accumulates charges whenever a city with Barracks finishes a land unit; charges can be consumed (button on city screen) to instantly draft a 6 XP Frederician Fusilier in that city without anarchy once every 10 turns, modeling rapid reserve mobilization.

## 4b) Novel Mechanic Candidates and Decision Log
| Candidate | Historical Anchor | Prototype Mechanic & History-to-Formula | XML/DLL Touchpoints | AI Plan | Decision |
| --- | --- | --- | --- | --- | --- |
| **Canton Reserve Meter** | 1733 canton reform tying adult males to regimental districts. citeturn0search13 | Add new `iCantonReserve` player value. Each time a city with Barracks completes a Gunpowder or Melee unit, +1 charge (cap 3). City button “Mobilize Canton” consumes 1 charge to spawn a 6 XP Frederician Fusilier (or contemporary Land unit) with +15% maintenance for 5 turns. | New DLL hooks: player-level counter, city action, UI help text; XML flag on trait to enable; `CvCity::canTrain` gating; `CvPlayer::changeCantonReserve`. | AI monitors war prep; when planning offensive, ensures at least 2 charges and triggers mobilization near target; defensive AI uses when enemy stack within 6 tiles. | **Selected** – passes traceability, introduces unique decision (saving charges), AI path described, fallback is manual unit builds if hook unavailable. |
| **Industry Audit Switch** | Frederick’s marginalia on industrial subsidies (1763 instructions). citeturn1search9 | Proposed city toggle that, when enabled, grants +10%  in a city per active Core Industry but cuts 2  if local resource quota fails. | Would require new building state machine referencing `IndustryCategory`. | AI would need to monitor tile counts per city; complexity high. | **Rejected** – heavy new UI for marginal payoff; baseline UB bonuses already model oversight. |
| **Sanssouci Patronage Track** | Frederick’s patronage of philosophers and musicians. citeturn0search8 | Global meter fills via Artist/Musician specialists, unlocking empire-wide +1  per University for 20 turns. | Would need DLL player event + new text. | AI evaluation unclear; duplicates existing golden age pattern. | **Rejected** – benefits replicate Golden Ages; better handled via existing GP/trait buffs. |

Fallback for Canton Reserve: if DLL hook slips, trait gains `iMaxPlayerBuildingProductionModifier +10%` for Barracks and `+2 XP` on Gunpowder units to keep intended theme albeit with lower ceiling.

## 5) Mechanics Coverage Check
| Entry | Key Mechanics Reviewed | Used? | Reason if Not Used | Source Mode |
| --- | --- | --- | --- | --- |
| Civ4BuildingInfos | Cost, BuildingClass, Commerce/Yield modifiers, Specialist slots, `BuildingClassProductionModifiers`, `IndustryCategory`. | Yes | UB relies on Courthouse class plus IndustryCategory-aware production bonus. | Web (Modiki) |
| Civ4CivilizationInfos | Leader slots, free techs/units, art/flag, diplomacy text. | Yes | Personality tuning + new UU/UB references documented. | Web (Modiki) |
| Civ4TraitInfos | Scalar modifiers, mapped channels, ImprovementCityCommerceChangesWorked/BFC. | Yes | Trait leverages scalar GP mods, Specialist commerce, Improvement yields, free promotions. | Web (Modiki) + repo schema |
| Civ4ImprovementInfos | Base yields, tech reveals, upgrade chains. | Partial | No unique improvement per constraint; still reviewed for farm/workshop tuning interplay. | Web (Modiki) |
| Civ4SpecialUnitInfos | Unique worker builds & replacement locks. | No | No new SpecialUnit classes introduced; UU uses existing Musketman class. | Web (Modiki) |
| Civ4PromotionInfos | Drill/formation effects, prerequisites. | Yes | UU introduces `PROMOTION_OBLIQUE_ORDER` (new entry) offering +1 first strike & +10% vs Gunpowder. | Web (Modiki) |
| Civ4UnitClassInfos | Determines Musketman replacement mapping. | Yes | `UNITCLASS_MUSKETMAN` remapped to Frederician Fusilier for Frederick-only leader/civ combo. | Web (Modiki) |
| Civ4UnitInfos | Strength, cost, upgrade tree, XP, default promotions. | Yes | UU stats defined here; fallback unit references recorded. | Web (Modiki) |
| Trait-level improvement yield/commerce hooks | `ImprovementYieldChanges`, `ImprovementCityCommerceChangesWorked/BFC`. | Yes | Trait uses +1  on Workshops (plains/river) and +1  on Town science (worked). | Repo scan |
| Trait-level building/specialist/bonus/route hooks | `BuildingCommerceChanges`, `SpecialistCommerceChanges`. | Yes | Specialist commerce bonus for multi-religion cities; UB synergy via BuildingCommerceChanges. | Repo scan |
| Civic-level improvement commerce hooks | `ImprovementCityCommerceChangesWorked/BFC` inside civics. | No | Scope is leader trait, not civic; future civics rework can reuse. | Repo scan |
| Civ-specific unique improvement framework | Custom Improvement + Build + cap system. | No | Explicitly avoided per issue constraint; nearest effect delivered via trait/UB. | Repo scan |
| Rare improvement caps | Per-player cap enforcement. | No | Not applicable without unique improvement. | Repo scan |
| IndustryCategory / Supply Chain schema (New) | `IndustryCategory` tag plus Core/Luxury/Composite caps and prerequisite text flows in `CIV4BuildingsSchema`. | Yes | UB production bonus references IndustryCategory to accelerate Core & Composite industries. | Repo scan |

**Newly Discovered Since Last Scan**
- `IndustryCategory` element in `CIV4BuildingsSchema.xml` (lines 366, 487) enabling Core/Luxury/Composite tagging – leveraged for UB targeting.
- Composite industry help-text gating (see `CIV4GameText_IndustryBuildings.xml`), reminding us to surface per-city Core/Composite caps in UB tooltip.

## 6) Final Overhaul Spec
### Leader Trait – `TRAIT_PHILOSOPHER_GENERAL`
- `+25%` Great People Rate (`iGreatPeopleRateModifier`).
- `+25%` Domestic Great General Rate (`iDomesticGreatGeneralRateModifier`).
- Free `PROMOTION_DRILL1` for Gunpowder land units built in cities with Barracks (trait-level FreePromotion + UnitCombat filter + BuildingPrereq tag already supported in repo).
- `ImprovementYieldChanges`: Workshops on Plains or Grassland tiles gain +1  (hammer). River Farms gain +1  (commerce) representing canalized agronomy.
- `ImprovementCityCommerceChangesWorked`: Towns worked by this player yield +1  (science).
- `SpecialistCommerceChanges`: Specialists in cities containing ≥2 religions yield +1  (gold) due to toleration edicts (implementation detail: city script checks building religions, toggles trait commerce bonus through custom DLL hook already in repo for SpecialistCommerceChanges).
- `iUpkeepModifier -20%` to model frugal budgets.

### Unique Unit – `UNIT_FREDERICIAN_FUSILIER` (replaces Musketman)
- Cost: 90  (vs 80 Musketman) to reflect elite training.
- Strength: 10 (base) + `+15%` vs Gunpowder units (intrinsic modifier) and `+10%` City Attack.
- Starts with new promotion `PROMOTION_OBLIQUE_ORDER`: `+1 First Strike`, `+10% Withdraw`, unlocks Drill line.
- Gains `March` upon reaching Level 4 (scripting via promotion prereq) to reward sustained campaigns.
- When produced in a city with Canton Reserve charge available, consumes 0.5 charge (rounded) and spawns with `+2 XP` extra (DLL tie-in) – synergy with novel mechanic.
- Art: Recolor Grenadier mesh to Prussian blue using asset from `civ4mods-code/realism/bts/trunk/Art/Units/Unique/Austria/Fusilier Austria/Hungarian Grenadier.nif`; copy into workspace `CoreFiles/.../Assets/Art/Units/PrussianFusilier/` with new button derived from `Art/interface/buttons/units/heroes/frederick_barbarossa.dds` palette.
- Text: Civilopedia entry explains linear tactics, references recruitment districts.

### Unique Building – `BUILDING_GENERALDIREKTORIUM` (replaces Courthouse)
- Base maintenance reduction: -55% (vs -50%).
- Additional effects when city hosts ≥1 Core Industry building: +10%  (gold) and +1  (merchant slot). Implementation: add BuildingCommerceChanges +1 Gold +10% Gold, and Python/DLL check toggles +10% only while `bHasCoreIndustry` bool true (hook exists via industry system toggles used by local processing buildings).
- Flat bonuses: +1  (espionage), +2  Great Person Points (all types), +1 Scientist slot to represent audit colleges.
- Grants +25% production toward buildings tagged with `IndustryCategory` (all categories) using `BuildingClassProductionModifier` entries for each relevant class (documented in Implementation Plan) or new DLL to apply category-based mod (preferred to avoid enumerating dozens of classes).
- Requires Courthouse tech prerequisites plus a new requirement: city must have either a Barracks or Custom House (mirrors interplay between war/fiscal boards).
- Art: Reskin existing Courthouse model with Prussian green trim; candidate resources exist under `CoreFiles/.../Assets/Art/CityBuildings/Ger_Courthouse/` (verify) or import from `civ4mods-code/realism/.../Buildings/Prussian_Court`.

### Novel Mechanic – Canton Reserve Meter
- Trait flag `bEnableCantonReserve=1`.
- Player stores up to 3 charges (UI pip near flag). Each time a city with Barracks, Armory, or Generals’ Staff finishes a Melee or Gunpowder unit, add 1 charge (cap). Charges decay by 1 if unused for 25 turns to encourage tempo.
- City command `cmdMobilizeCanton` (button on city screen & unit panel). Costs 1 charge + +25% city maintenance for 5 turns, instantly produces a Frederician Fusilier with 6 XP and Oblique Order promotion, placed in city with 1 turn of immobility.
- AI heuristics: define `AI_isThreatened()` to trigger defensive mobilization when enemy stack within 6 tiles; offensive AI uses charges before DoW when power ratio >0.9.
- UI text: `TXT_KEY_TRAIT_FREDERICK_CANTON_COUNTER`, `TXT_KEY_MISC_CANTON_CONSUMED`.

### Personality / Diplomacy
- Higher flavors: Military = 9, Production = 7, Science = 7, Culture = 4, Religion = 2.
- Builds Barracks/Armory earlier; values Industry buildings 20% more than baseline.
- War declaration probability moderate but improves when Canton reserve ≥2.
- Favorite civic: Bureaucracy; shuns Theocracy to reflect toleration.

### Text / Localization
- New trait text enumerates: "+25% Great People Rate; +25% Domestic Great General Rate; Towns (worked) +1 Science; Workshops on Plains/Grassland +1 Hammer; Farms on Rivers +1 Commerce; Specialists in multi-religion cities +1 Gold; Gunpowder units built in cities with Barracks start with Drill I; Upkeep -20%; stores Canton Reserve charges." Ensure bullet format.

## 6b) Quantified Balance Table
| Mechanic | Numeric Effect | Target / Scope | Trigger / Condition | Era Timing | Impact | Counterplay / Constraint |
| --- | --- | --- | --- | --- | --- | --- |
| Philosophical Drill (trait) | +25%  GPP; +25% Domestic GG rate | Player-wide | Always on | Medieval+ | Medium | Competes with empire-wide happiness via maintenance focus; GP surge requires specialist investment |
| Canton Commerce (trait) | Towns +1  Science (worked) | Town improvements empire-wide | Citizen must work tile | Renaissance spike | Medium | Needs time to grow cottages; pillaging towns removes bonus |
| Agrarian Workshops (trait) | Workshops on Plains/Grassland +1  Hammer | Tile improvement | Requires workshop & Chemistry | Renaissance | Medium-High | Costs food; enemy can pillage |
| River Farm Canals (trait) | River-adjacent Farms +1  Commerce | Tile improvement | River farm worked | Medieval | Low | Only on river farms; limited by terrain |
| Multi-Faith Ledger (trait) | Specialists +1  Gold in ≥2-religion cities | Specialists | Requires 2 religions present | Medieval | Low | Spread religions or use espionage to remove |
| Canton Reserve Meter | Stores up to 3 charges; Mobilize consumes 1 to spawn 6 XP UU, +25% maintenance for 5 turns | Player/city | City with Barracks/Armory finishes qualifying unit; button usage limited to 1 per 10 turns per city | Medieval–Industrial | High | Charges decay; mobilization raises maintenance and cannot be used while city is occupied/besieged |
| Frederician Fusilier UU | +15% vs Gunpowder; +10% City Attack; starts with Oblique Order; synergy with Canton charges | Gunpowder unit | Built/raised by Frederick | Renaissance | High | Slightly higher cost; lacks bonus vs melee/cavalry; counter with cavalry/flanking |
| Oblique Order Promotion | +1 First Strike; +10% Withdraw; unlocks Drill line | Promotion | Granted to UU or upgrade path | Renaissance | Medium | Counts toward promotion slots; XP-heavy units can counter |
| Generaldirektorium UB | -55% maintenance; +10% Gold & +1 Merchant slot when Core Industry present; +1 Scientist slot; +2 GPP; +1 Espionage; +25% Industry building production | City building | Requires Code of Laws, Courthouse class, Barracks or Custom House; Industry bonus only active when city meets Core Industry prereqs | Medieval | Medium-High | Needs Industry infrastructure; Industry bonus can deactivate if tile quotas fail |

## 7) Implementation Plan
1. **XML Edits**
   - `CoreFiles/.../Assets/XML/Civilizations/CIV4LeaderHeadInfos.xml`: Update Frederick’s trait reference, AI flavors, favorite civic, diplomacy texts.
   - `CIV4TraitInfos.xml`: Replace `TRAIT_FREDERICK` definition with `TRAIT_PHILOSOPHER_GENERAL` entries described above (scalar modifiers + mapped channels + Canton flag + new UI text keys).
   - `CIV4UnitClassInfos.xml` & `CIV4CivilizationInfos.xml`: Map `UNITCLASS_MUSKETMAN` to `UNIT_FREDERICIAN_FUSILIER` for Frederick-specific civ entries; ensure other German leaders keep existing uniques.
   - `CIV4UnitInfos.xml`: Add new unit entry with stats/promotions, upgrade path, build prerequisites.
   - `CIV4PromotionInfos.xml`: Introduce `PROMOTION_OBLIQUE_ORDER` with modifiers and icon.
   - `CIV4BuildingInfos.xml`: Add `BUILDING_GENERALDIREKTORIUM` entry (Courthouse class) including IndustryCategory production modifiers; consider new schema hook to apply category-based percentage by referencing `IndustryCategory` element rather than enumerating each class.
   - `CIV4GameText_Leader_Civilopedia.xml` (and localized files): Update trait/unit/building text.
   - `CIV4ArtDefines_Unit.xml` & `CIV4ArtDefines_Building.xml`: Point to copied art assets.
2. **DLL / Schema**
   - Extend `CvTraitInfo` with `bEnableCantonReserve`; extend `CvPlayer` with `m_iCantonReserve`, serialization, getter/setter, UI exposure via Python.
   - Add `CvCity::canMobilizeCanton` and new mission command processed in `CvUnit::command`. Update city interface Python to show button + help text.
   - Implement IndustryCategory-based production bonus for UB either via new building tag (preferred) or enumerated list (temporary).
   - Ensure `SpecialistCommerceChanges` respects multi-religion condition (existing hook may already support conditional logic; otherwise add boolean/threshold fields to trait info).
3. **Python / UI**
   - Update `CvMainInterface` or dedicated city screen helper to display Canton Reserve charges.
   - Add help text functions (Trait, UB, UU) referencing new TXT keys.
4. **Art / Assets**
   - Copy chosen fusilier NIF/KFM/button into workspace; update shader references.
   - Identify/prepare new courthouse button/reskin; ensure mipmaps.
5. **Testing**
   - Run `.	ools	est_gate.ps1` after XML edits; `.	ools	est_gate.ps1 -CheckDll` after DLL work.
   - Manual smoke test per docs: verify Canton command, UB industry condition toggling, UU promotions, AI mobilization.
6. **AI Tuning**
   - `CvPlayerAI::AI_bestTech` weight adjustments for Chemistry/Military Tradition.
   - `CvCityAI::AI_buildUnit` to account for Canton charges (avoid overshoot) and to value UB in high-industry cities.

## 8) Distinctiveness Audit
- Trait mixes town science + workshop hammers + multi-faith specialist gold—a combination not used by Washington, Tokugawa, or Hatshepsut—while overlaying a new reserve-meter mechanic to enforce tempo decisions unique to Frederick.
- UU shifts German identity away from late Industrial armor (Panzer) toward mid-game precision infantry, avoiding overlap with any civ currently fielding musket-class uniques.
- UB interacts with the mod’s IndustryCategory system rather than generic courthouse buffs, making Frederick the only leader who accelerates Core/Composite industry construction without creating new improvements.
- Refused to add unique improvements or broad class buffs, keeping focus on drilled armies + bureaucracy synergy; other civs emphasize religion, corporations, or naval power, so Frederick’s asymmetry remains clear.

## Residual Questions / Follow-Ups
- Confirm whether IndustryCategory-based production bonus can be implemented through existing tags or needs a DLL helper (preferred approach documented above).
- Determine final fusilier art source (workspace vs. imported) before implementation; record provenance per art protocol when copied.
