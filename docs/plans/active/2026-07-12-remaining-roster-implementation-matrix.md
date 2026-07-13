# Remaining 32 Implementation Matrix

- Status: **implementation-ready design freeze**
- Owner: `design-matrix`
- Runtime changes: **none**
- Machine-readable source: `tools/baselines/remaining_roster_implementation_matrix.json`

## Frozen rules

* Tiers remain 16 Keep, 4 Polish, 10 Targeted differentiation, 2 Major redesign.
* Keep packages receive no gameplay changes. Polish and Targeted packages are limited to the exact decisions below. Major specs are whole-package budgets, not permission to invent additional mechanics.
* No new DLL mechanic is proposed. Existing custom channels and consuming packages are frozen in the JSON.
* No new worker action is proposed. Salamasina keeps the already-wired Reef Works action and must pass its complete render/wiring test.
* Preserve InfoType order. The only proposed new type is appended `BUILDING_YUAN_IMPERIAL_SECRETARIAT`; dormant replaced types remain defined for saves.

## Cross-roster distinctiveness freeze

| Package | Tier | Frozen axis | Collision disposition |
|---|---|---|---|
| `LEADER_WASHINGTON` / `CIVILIZATION_AMERICA_FOUNDING_REPUBLIC` | Targeted differentiation | A clear revolutionary army plus federal administration identity with good early-to-midgame continuity. | bounded correction; The trait occupies ten economic/military channels and overlaps generic American growth, commerce, espionage, and command identities; it is difficult to read and budget. |
| `LEADER_GERONIMO_BTG` / `CIVILIZATION_APACHE_CONFEDERACY` | Polish | Coherent mobile resistance and field-support package; every component reinforces mobility and endurance. | bounded correction; Personality is materially redundant with Sitting Bull, and the Raider is carrying many advantages at once. |
| `LEADER_MONTEZUMA` / `CIVILIZATION_AZTEC` | Keep | Exceptionally unified conquest, sacrifice, forest warfare and priest economy. | unchanged; Some thematic overlap with other extreme warmongers, but the hurry/priest axis is distinct. |
| `LEADER_HAMMURABI` / `CIVILIZATION_BABYLON` | Targeted differentiation | Law/administration and urban prosperity are strongly expressed and the earlier Hammurabi work is visible in live XML. | bounded correction; Three enhanced buildings plus a large Palace cause cumulative city-economy overlap; the culture-10 personality underplays administration and expansion. |
| `LEADER_HANNIBAL` / `CIVILIZATION_CARTHAGE` | Keep | Combined-arms mobility, elephant access and port commerce form a recognizable Carthaginian package. | unchanged; Shares mounted aggression with several leaders, but Cothon/trade and generated Ivory give it a distinct strategic arc. |
| `LEADER_ELIZABETH` / `CIVILIZATION_ELIZABETHAN_ENGLAND` | Targeted differentiation | Naval defense, commerce and Great People create a strong Elizabethan maritime-economy identity. | bounded correction; The same unit replacing three eras/classes collapses naval progression and creates AI/upgrade ambiguity; Royal Exchange and trait are already powerful. |
| `LEADER_DE_GAULLE` / `CIVILIZATION_FRANCE_FIFTH_REPUBLIC` | Keep | Distinct late national-resilience package with useful early civic identity and mobile gunpowder. | unchanged; Some defensive morale overlap with Churchill, but era and production channels differ. |
| `LEADER_BISMARCK` / `CIVILIZATION_GERMAN_EMPIRE` | Keep | Industrial military identity is compact, legible and AI-friendly. | unchanged; Late timing overlaps other industrial leaders, but the armor/engineer combination remains distinct. |
| `LEADER_CATHERINE` / `CIVILIZATION_IMPERIAL_RUSSIA` | Keep | Culture, elite cavalry and provincial administration combine into a broad but coherent imperial-expansion package. | unchanged; Some overlap with other Russian cavalry leaders, but the culture/assembly angle distinguishes it. |
| `LEADER_HUAYNA_CAPAC` / `CIVILIZATION_INCA` | Polish | Strong early expansion and infrastructure identity with a famous, functional Quechua/Terrace core. | bounded correction; Leader-wide promotion plus separate Worker/Settler replacements broadens the package without making their actual advantage obvious. |
| `LEADER_GANDHI` / `CIVILIZATION_INDIA` | Keep | A clear nonmilitary Great People and civil-society package with real tradeoffs. | unchanged; Asoka shares the Fast Worker, but their buildings, trait and personality diverge. |
| `LEADER_TOKUGAWA` / `CIVILIZATION_JAPAN` | Keep | Earlier Tokugawa work produces a focused disciplined-army plus bakufu administration identity. | unchanged; Military promotion breadth is strong but coherent; limited overlap with Qin/Churchill defensive promotions is offset by Samurai and espionage court. |
| `LEADER_SURYAVARMAN` / `CIVILIZATION_KHMER` | Keep | Water management, growth and elephant warfare create a compact Khmer identity. | unchanged; Farm growth overlaps other agrarian packages but the Aqueduct attachment is distinctive. |
| `LEADER_WANGKON` / `CIVILIZATION_KOREA` | Targeted differentiation | Very legible scholarship plus defensive artillery identity. | bounded correction; Library, University and Academy all amplify the same science channel, producing redundant multiplicative scaling and crowding other scholar civilizations. |
| `LEADER_ASOKA` / `CIVILIZATION_MAURYA` | Targeted differentiation | Dharma, Buddhist spread and low-upkeep governance form a strong nonconquest identity. | bounded correction; Fast Worker overlaps Gandhi; the Ramesses coupling appears accidental and the Obelisk's +25% war weariness cuts against the intended thesis. |
| `LEADER_PACAL` / `CIVILIZATION_MAYA` | Keep | Simple growth/culture package with an early defensive UU. | unchanged; Generic health/commerce is less evocative than newer traits but the Ball Court supplies identity. |
| `LEADER_GENGHIS_KHAN` / `CIVILIZATION_MONGOL_EMPIRE` | Targeted differentiation | Mounted mobility, horse access and Great Generals strongly communicate steppe conquest. | bounded correction; The Japanese Castle Town reference is unrelated leakage; broad building/resource/specialist bonuses overfill an already excellent Keshik/Ger/Palace package. |
| `LEADER_SITTING_BULL` / `CIVILIZATION_NATIVE_AMERICA` | Targeted differentiation | Defensive denial, health and archer development offer a recognizable survival identity. | bounded correction; Personality overlaps Geronimo; extreme negative trade-yield values look like a brittle exploit/penalty rather than legible differentiation. |
| `LEADER_WILLEM_VAN_ORANJE` / `CIVILIZATION_NETHERLANDS` | Keep | Exceptionally coherent water, shipping and trade-city package. | unchanged; Strong trade overlap with Portugal/Venice, but Dike terrain dependence and Galleon timing distinguish it. |
| `LEADER_CHINESE_LEADER` / `CIVILIZATION_PEOPLES_REPUBLIC_CHINA` | Targeted differentiation | Mass mobilization, cheaper infantry, workplace organization and state administration are mechanically integrated. | bounded correction; Trait and Danwei both stack production, espionage and administration; the package is much denser than comparable modern leaders. |
| `LEADER_PETER` / `CIVILIZATION_PETRINE_RUSSIA` | Keep | Modernization, maritime development, bureaucracy and knowledge transfer are sharply expressed without another Russian cavalry unit. | unchanged; No-UU shape differs from most packages but avoids Russian cavalry redundancy. |
| `LEADER_CASIMIR` / `CIVILIZATION_POLAND` | Polish | Peaceful domestic identity paired with a bounded mounted military reserve. | bounded correction; Trait is generic and thin; Dragoon/castle military focus does not fully express the AI's growth, law and culture themes. |
| `LEADER_SALAMASINA_BTG` / `CIVILIZATION_POLYNESIA_BTG` | Polish | Excellent seafaring, ocean development and ceremonial/community package. | bounded correction; Large unconditional health/happiness is generic and may overshadow the more distinctive navigation/reef system. |
| `LEADER_JOAO` / `CIVILIZATION_PORTUGAL` | Keep | Exploration, overseas settlement and maritime commerce are clear and highly playable. | unchanged; Some overlap with Willem/Elizabeth, but fast scouting and transport capacity distinguish Portugal. |
| `LEADER_QIN_SHI_HUANG` / `CIVILIZATION_QIN_DYNASTY` | Keep | Strong fortified-state, mass construction and ranged-army identity. | unchanged; Defensive promotion overlap with Churchill/Tokugawa, but collateral crossbows and production AI differentiate it. |
| `LEADER_ISABELLA` / `CIVILIZATION_SPAIN` | Keep | Compact religious-expansion and combined mounted/naval identity. | unchanged; Mounted overlap is common, but naval Morale and siege Citadel provide breadth. |
| `LEADER_STALIN` / `CIVILIZATION_USSR` | Major redesign | Production, research and secret-police identity is unmistakable. | dedicated redesign spec; Numbers are outliers: +50 trait commerce, 100 Spy slots, 5-cost Spy, +5 happiness Lubyanka and multiple research/espionage buildings erase normal constraints. |
| `LEADER_ENRICO_DANDOLO` / `CIVILIZATION_VENICE` | Major redesign | Venetian trade and merchant-government identity is immediately visible. | dedicated redesign spec; Package bypasses normal city, worker, Great Person, health, happiness and trade constraints; copied peaceful AI does not express Dandolo's crusading opportunism. |
| `LEADER_RAGNAR` / `CIVILIZATION_VIKING` | Keep | A direct, legible amphibious raiding progression across land and sea. | unchanged; Extreme warmonger overlap with Genghis/Shaka/Montezuma, but amphibious and naval progression distinguishes Ragnar. |
| `LEADER_CHURCHILL` / `CIVILIZATION_WARTIME_BRITAIN` | Targeted differentiation | Excellent air defense, national resilience and intelligence identity. | bounded correction; War Rooms and MI6 double-stack espionage while the Bank replacement also improves gold; defensive promotions overlap Qin/Tokugawa. |
| `LEADER_KUBLAI_KHAN` / `CIVILIZATION_YUAN_DYNASTY` | Targeted differentiation | Road logistics, postal/trade hub and culturally oriented conquest are a strong Yuan identity. | bounded correction; Shared Palace blurs Genghis/Kublai; mounted package still closely parallels Keshik/Ger. |
| `LEADER_SHAKA` / `CIVILIZATION_ZULU` | Keep | Compact, powerful military expansion package with a real economic enabler. | unchanged; Warmonger overlap is inevitable, but fast spear plus maintenance Barracks is unique. |

## DLL and worker-action decision

No new DLL fields, readers, hooks, serialization, AI valuation, Python exposure, or network behavior are proposed. Existing extended trait-yield tables are consumed by Washington, Huayna Capac, Genghis, Mao, and Kublai; free-promotion tables by Montezuma, Tokugawa, Qin, Isabella, Shaka, and Salamasina; building improvement/sea-yield tables by Suryavarman, Willem, and Joao; existing unit action paths by Willem, Salamasina, and Dandolo. Dandolo removes actions rather than adding one.

## Package implementation records

### 1. `LEADER_WASHINGTON` — `CIVILIZATION_AMERICA_FOUNDING_REPUBLIC` (Targeted differentiation)

**Historical/gameplay thesis.** Revolutionary command backed by federal institutions and road logistics, not a grab bag of unrelated yields.

**Power budget.** Mid: retain +50% Great General and domestic Great General rates plus one map-dependent route channel; delete eight passive channels.

**Frozen object decisions.**

- **MODIFY** `TRAIT_GEORGE_WASHINGTON` — Keep iGreatGeneralRateModifier=50, iDomesticGreatGeneralRateModifier=50 and RouteYieldChanges ROAD commerce +1; delete Town +1 commerce, Barracks +1 production, Courthouse +2 espionage, Bank +2 gold, Spy +1 espionage, Merchant +1 gold, Wheat +1 food and Horse +1 production.
- **KEEP** `UNIT_CONTINENTAL_LINE_INFANTRY` — No field changes.
- **KEEP** `BUILDING_FEDERAL_HALL` — No field changes.

**Art.** Reuse all current art definitions; no new art or tags.

**AI/UI/save/MP risk.** AI loses scattered passive income but understands Great Generals; route help must display. XML-only existing trait tables; existing saves retain type order; deterministic MP.

**Worker action.** None proposed.

**Validation.** Trait-help snapshot; test Road versus non-Road commerce; verify deleted eight channels; AI autoplay; save/reload and MP checksum.

### 2. `LEADER_GERONIMO_BTG` — `CIVILIZATION_APACHE_CONFEDERACY` (Polish)

**Historical/gameplay thesis.** Mobile resistance and field medicine with an AI willing to conduct limited raids.

**Power budget.** Power-neutral Polish: gameplay objects unchanged; personality-only differentiation.

**Frozen object decisions.**

- **KEEP** `TRAIT_LEADER_GERONIMO` — No numeric changes.
- **KEEP** `UNIT_APACHE_MEDICINE_MAN_BTG` — No field changes.
- **KEEP** `UNIT_APACHE_RAIDER_BTG` — No field changes.
- **KEEP** `BUILDING_APACHE_WAR_COUNCIL_BTG` — No field changes.
- **MODIFY** `LEADER_GERONIMO_BTG` — iBasePeaceWeight 8->4 and iLimitedWarRand 200->120; all other diplomacy values unchanged.

**Art.** Reuse current Apache leader/unit/building art; mandatory Raider and Medicine Man animation smoke.

**AI/UI/save/MP risk.** AI behavior changes but synchronized data/type order do not; no save schema or MP logic change.

**Worker action.** None proposed.

**Validation.** Leader XML diff assertion; 3 seeded AI autoplays tracking limited wars and Raider production; diplomacy regression; save/reload/MP checksum.

### 3. `LEADER_MONTEZUMA` — `CIVILIZATION_AZTEC` (Keep)

**Historical/gameplay thesis.** The package captures militarized Mexica state religion, though sacrificial framing should remain precise rather than sensationalized.

**Power budget.** Frozen at live values; zero numeric, mapping, type, art, AI or text changes.

**Frozen object decisions.**

- **KEEP** `TRAIT_MONTEZUMA` — No changes.
- **KEEP** `UNIT_AZTEC_JAGUAR` — No changes.
- **KEEP** `BUILDING_AZTEC_SACRIFICIAL_ALTAR` — No changes.
- **KEEP** `BUILDING_AZTEC_PALACE` — No changes.

**No-change rationale.** Exceptionally unified conquest, sacrifice, forest warfare and priest economy. Some thematic overlap with other extreme warmongers, but the hurry/priest axis is distinct.

**Art.** Retain every current art tag and repository asset; smoke only.

**AI/UI/save/MP risk.** Regression-only: no intended AI/UI/save/MP behavior change.

**Worker action.** None proposed.

**Validation.** Baseline/type/mapping digest unchanged; promotion recipients; Jaguar/Altar/Palace mapping; early hurry/priest economy; palace/help render; pedia/art smoke; AI autoplay; save/reload and MP checksum.

### 4. `LEADER_HAMMURABI` — `CIVILIZATION_BABYLON` (Targeted differentiation)

**Historical/gameplay thesis.** Legal administration remains the center; the Palace should not duplicate every urban-economy reward.

**Power budget.** Mid after correction: remove the Palace raw production/espionage spike while retaining health, happiness, maintenance, trade and Great Spy identity.

**Frozen object decisions.**

- **KEEP** `TRAIT_HAMMURABI` — -35% civic upkeep unchanged.
- **KEEP** `UNIT_BABYLON_BOWMAN` — No field changes.
- **MODIFY** `BUILDING_BABYLON_ROYAL_PALACE` — YieldChanges [0,2,8]->[0,0,8]; CommerceChanges [0,3,2,8]->[0,3,2,2]; all other fields unchanged.
- **KEEP** `BUILDING_BABYLON_GARDEN` — No field changes.
- **KEEP** `BUILDING_BABYLON_COURTHOUSE` — No field changes.

**Art.** Reuse ART_DEF_BUILDING_PALACE and all current unit/building art.

**AI/UI/save/MP risk.** Passive AI-safe reduction; no new IDs/schema; save and MP safe apart from deterministic recalculation.

**Worker action.** None proposed.

**Validation.** Capital yield before/after fixture; courthouse/garden unchanged assertions; AI city-value autoplay; save/reload/MP checksum.

### 5. `LEADER_HANNIBAL` — `CIVILIZATION_CARTHAGE` (Keep)

**Historical/gameplay thesis.** Carthage's maritime commerce and Hannibal's mixed army are well represented.

**Power budget.** Frozen at live values; zero numeric, mapping, type, art, AI or text changes.

**Frozen object decisions.**

- **KEEP** `TRAIT_HANNIBAL` — No changes.
- **KEEP** `UNIT_CARTHAGE_NUMIDIAN_CAVALRY` — No changes.
- **KEEP** `UNIT_CARTHAGE_AFRICAN_WAR_ELEPHANT` — No changes.
- **KEEP** `BUILDING_CARTHAGE_COTHON` — No changes.
- **KEEP** `BUILDING_CARTHAGE_BYRSA_ELEPHANT_TREASURY` — No changes.

**No-change rationale.** Combined-arms mobility, elephant access and port commerce form a recognizable Carthaginian package. Shares mounted aggression with several leaders, but Cothon/trade and generated Ivory give it a distinct strategic arc.

**Art.** Retain every current art tag and repository asset; smoke only.

**AI/UI/save/MP risk.** Regression-only: no intended AI/UI/save/MP behavior change.

**Worker action.** None proposed.

**Validation.** Baseline/type/mapping digest unchanged; Ivory generation/yields; both mounted uniques; Cothon route; elephant treasury render; pedia/art smoke; AI autoplay; save/reload and MP checksum.

### 6. `LEADER_ELIZABETH` — `CIVILIZATION_ELIZABETHAN_ENGLAND` (Targeted differentiation)

**Historical/gameplay thesis.** Elizabethan maritime commerce peaks with the privateering Sea Dog instead of collapsing three naval eras.

**Power budget.** Mid-high package retained; correction removes two premature replacement mappings without buffing Sea Dog or Royal Exchange.

**Frozen object decisions.**

- **KEEP** `TRAIT_ELIZABETH` — No field changes.
- **MODIFY** `CIVILIZATION_ELIZABETHAN_ENGLAND` — UnitClassOverrides: UNITCLASS_GALLEY -> UNIT_GALLEY; UNITCLASS_TRIREME -> UNIT_TRIREME; retain UNITCLASS_PRIVATEER -> UNIT_ENGLISH_SEA_DOG.
- **KEEP** `UNIT_ENGLISH_SEA_DOG` — Strength 6, moves 3, cargo 4 and current promotions/AIs unchanged.
- **KEEP** `BUILDING_ENGLISH_ROYAL_EXCHANGE` — No field changes.

**Art.** Use stock Galley/Trireme art and current Sea Dog/Royal Exchange art; no imports.

**AI/UI/save/MP risk.** Fixes AI class ambiguity; existing Sea Dogs remain valid because UnitType is unchanged. Mapping change is synchronized; old saves and MP scenario required.

**Worker action.** None proposed.

**Validation.** Mapping assertion; Galley/Trireme/Privateer build-list and upgrade tests; naval AI autoplay; Sea Dog animation; old save and deterministic MP.

### 7. `LEADER_DE_GAULLE` — `CIVILIZATION_FRANCE_FIFTH_REPUBLIC` (Keep)

**Historical/gameplay thesis.** Nationhood, resistance and mass communication fit de Gaulle's wartime and Fifth Republic careers.

**Power budget.** Frozen at live values; zero numeric, mapping, type, art, AI or text changes.

**Frozen object decisions.**

- **KEEP** `TRAIT_DE_GAULLE` — No changes.
- **KEEP** `UNIT_FRENCH_MUSKETEER` — No changes.
- **KEEP** `BUILDING_FRENCH_BROADCAST_TOWER` — No changes.
- **KEEP** `BUILDING_FRENCH_FIFTH_REPUBLIC_MONUMENT` — No changes.

**No-change rationale.** Distinct late national-resilience package with useful early civic identity and mobile gunpowder. Some defensive morale overlap with Churchill, but era and production channels differ.

**Art.** Retain every current art tag and repository asset; smoke only.

**AI/UI/save/MP risk.** Regression-only: no intended AI/UI/save/MP behavior change.

**Worker action.** None proposed.

**Validation.** Baseline/type/mapping digest unchanged; Musketeer movement; Broadcast Tower resilience; Monument culture persistence; pedia/art smoke; AI autoplay; save/reload and MP checksum.

### 8. `LEADER_BISMARCK` — `CIVILIZATION_GERMAN_EMPIRE` (Keep)

**Historical/gameplay thesis.** Industrialization and state military power fit imperial Germany under Bismarck, even if the Panzer is chronologically later.

**Power budget.** Frozen at live values; zero numeric, mapping, type, art, AI or text changes.

**Frozen object decisions.**

- **KEEP** `TRAIT_BISMARCK` — No changes.
- **KEEP** `UNIT_GERMAN_PANZER` — No changes.
- **KEEP** `BUILDING_GERMAN_ASSEMBLY_PLANT` — No changes.

**No-change rationale.** Industrial military identity is compact, legible and AI-friendly. Late timing overlaps other industrial leaders, but the armor/engineer combination remains distinct.

**Art.** Retain every current art tag and repository asset; smoke only.

**AI/UI/save/MP risk.** Regression-only: no intended AI/UI/save/MP behavior change.

**Worker action.** None proposed.

**Validation.** Baseline/type/mapping digest unchanged; Panzer armor modifier; Assembly Plant coal/engineers; late AI build; pedia/art smoke; AI autoplay; save/reload and MP checksum.

### 9. `LEADER_CATHERINE` — `CIVILIZATION_IMPERIAL_RUSSIA` (Keep)

**Historical/gameplay thesis.** Elite cavalry, court culture and noble administration plausibly fit Catherine's imperial program.

**Power budget.** Frozen at live values; zero numeric, mapping, type, art, AI or text changes.

**Frozen object decisions.**

- **KEEP** `TRAIT_CATHERINE` — No changes.
- **KEEP** `UNIT_IMPERIAL_RUSSIA_BLACK_SEA_HUSSAR` — No changes.
- **KEEP** `BUILDING_IMPERIAL_RUSSIA_NOBLE_ASSEMBLY` — No changes.

**No-change rationale.** Culture, elite cavalry and provincial administration combine into a broad but coherent imperial-expansion package. Some overlap with other Russian cavalry leaders, but the culture/assembly angle distinguishes it.

**Art.** Retain every current art tag and repository asset; smoke only.

**AI/UI/save/MP risk.** Regression-only: no intended AI/UI/save/MP behavior change.

**Worker action.** None proposed.

**Validation.** Baseline/type/mapping digest unchanged; Hussar movement/promotions; Noble Assembly culture/gold; Russian package comparison; pedia/art smoke; AI autoplay; save/reload and MP checksum.

### 10. `LEADER_HUAYNA_CAPAC` — `CIVILIZATION_INCA` (Polish)

**Historical/gameplay thesis.** Keep the proven early-expansion package; expose exactly what civilian promotion replacements do.

**Power budget.** Power-neutral Polish; text only.

**Frozen object decisions.**

- **KEEP** `TRAIT_HUAYNA_CAPAC` — No numeric changes.
- **KEEP** `UNIT_INCAN_QUECHUA` — No field changes.
- **KEEP** `UNIT_HUAYNA_WORKER` — No field changes.
- **KEEP** `UNIT_HUAYNA_SETTLER` — No field changes.
- **KEEP** `BUILDING_INCAN_TERRACE` — No field changes.
- **MODIFY** `TXT_KEY_TRAIT_HUAYNA_CAPAC` — Rewrite help/strategy text to enumerate promotion recipients and observable civilian effects; no mechanic changes.

**Art.** Reuse current stock/civilian art; inspect Worker and Settler animation groups.

**AI/UI/save/MP risk.** Localization/UI only; no AI, save, schema or MP behavior change.

**Worker action.** None proposed.

**Validation.** Text-key resolution; pedia and hover review at 1024x768; Worker/Settler movement/build/found smoke; baseline digest unchanged outside text.

### 11. `LEADER_GANDHI` — `CIVILIZATION_INDIA` (Keep)

**Historical/gameplay thesis.** The pacific/civic emphasis is recognizable and not overdesigned.

**Power budget.** Frozen at live values; zero numeric, mapping, type, art, AI or text changes.

**Frozen object decisions.**

- **KEEP** `TRAIT_GHANDI` — No changes.
- **KEEP** `UNIT_INDIAN_FAST_WORKER` — No changes.
- **KEEP** `BUILDING_INDIAN_MAUSOLEUM` — No changes.
- **KEEP** `BUILDING_GANDHI_FORGE` — No changes.

**No-change rationale.** A clear nonmilitary Great People and civil-society package with real tradeoffs. Asoka shares the Fast Worker, but their buildings, trait and personality diverge.

**Art.** Retain every current art tag and repository asset; smoke only.

**AI/UI/save/MP risk.** Regression-only: no intended AI/UI/save/MP behavior change.

**Worker action.** None proposed.

**Validation.** Baseline/type/mapping digest unchanged; Fast Worker; Mausoleum/Forge tradeoffs; pacific AI; pedia/art smoke; AI autoplay; save/reload and MP checksum.

### 12. `LEADER_TOKUGAWA` — `CIVILIZATION_JAPAN` (Keep)

**Historical/gameplay thesis.** Samurai and bakufu administration fit Tokugawa rule; science flavor prevents a purely isolationist caricature.

**Power budget.** Frozen at live values; zero numeric, mapping, type, art, AI or text changes.

**Frozen object decisions.**

- **KEEP** `TRAIT_TOKUGAWA` — No changes.
- **KEEP** `UNIT_JAPAN_SAMURAI` — No changes.
- **KEEP** `BUILDING_JAPAN_BAKUFU_MAGISTRACY` — No changes.

**No-change rationale.** Earlier Tokugawa work produces a focused disciplined-army plus bakufu administration identity. Military promotion breadth is strong but coherent; limited overlap with Qin/Churchill defensive promotions is offset by Samurai and espionage court.

**Art.** Retain every current art tag and repository asset; smoke only.

**AI/UI/save/MP risk.** Regression-only: no intended AI/UI/save/MP behavior change.

**Worker action.** None proposed.

**Validation.** Baseline/type/mapping digest unchanged; Samurai prerequisite/promotion stack; Magistracy XP/espionage; AI unit valuation; pedia/art smoke; AI autoplay; save/reload and MP checksum.

### 13. `LEADER_SURYAVARMAN` — `CIVILIZATION_KHMER` (Keep)

**Historical/gameplay thesis.** Baray/reservoir infrastructure and monumental religious state power are good Angkorian signals.

**Power budget.** Frozen at live values; zero numeric, mapping, type, art, AI or text changes.

**Frozen object decisions.**

- **KEEP** `TRAIT_SURYAVARMAN` — No changes.
- **KEEP** `UNIT_KHMER_BALLISTA_ELEPHANT` — No changes.
- **KEEP** `BUILDING_KHMER_BARAY` — No changes.

**No-change rationale.** Water management, growth and elephant warfare create a compact Khmer identity. Farm growth overlaps other agrarian packages but the Aqueduct attachment is distinctive.

**Art.** Retain every current art tag and repository asset; smoke only.

**AI/UI/save/MP risk.** Regression-only: no intended AI/UI/save/MP behavior change.

**Worker action.** None proposed.

**Validation.** Baseline/type/mapping digest unchanged; Ballista target logic; Baray Farm yield/help; AI improvement valuation; pedia/art smoke; AI autoplay; save/reload and MP checksum.

### 14. `LEADER_WANGKON` — `CIVILIZATION_KOREA` (Targeted differentiation)

**Historical/gameplay thesis.** Defensive artillery plus one signature university; ordinary Library and Academy pacing prevents triple multiplicative science.

**Power budget.** Mid: retain Hwacha, trait and 35% Seowon; remove two redundant unique building mappings.

**Frozen object decisions.**

- **KEEP** `TRAIT_WANGKON` — No field changes.
- **KEEP** `UNIT_KOREAN_HWACHA` — No field changes.
- **KEEP** `BUILDING_KOREAN_SEOWON` — 35% research unchanged.
- **REPLACE** `BUILDING_KOREAN_LIBRARY` — CIVILIZATION_KOREA BUILDINGCLASS_LIBRARY mapping -> BUILDING_LIBRARY; leave dormant type in place for save/type-order stability.
- **REPLACE** `BUILDING_KOREAN_ACADEMY` — CIVILIZATION_KOREA BUILDINGCLASS_ACADEMY mapping -> default BUILDING_ACADEMY resolved from BuildingClassInfos; leave dormant type in place.

**Art.** Use stock Library/Academy and current Seowon/Hwacha art; no new art.

**AI/UI/save/MP risk.** AI science curve normalizes; dormant types preserve InfoType order, but mapping affects build availability in existing saves. MP synchronized XML.

**Worker action.** None proposed.

**Validation.** Resolve default class IDs; mapping/build-list assertions; science multiplier comparison; AI tech autoplay; old-save city production and MP checksum.

### 15. `LEADER_ASOKA` — `CIVILIZATION_MAURYA` (Targeted differentiation)

**Historical/gameplay thesis.** Dharma pillar rewards Asoka rather than another leader and represents reduced, not increased, conflict burden.

**Power budget.** Power-neutral bounded bug correction: ownership coupling fixed and war-weariness sign corrected; no added channel.

**Frozen object decisions.**

- **KEEP** `TRAIT_ASOKA` — -50% civic upkeep unchanged.
- **KEEP** `UNIT_INDIAN_FAST_WORKER` — No field changes.
- **MODIFY** `BUILDING_MAURYAN_OBELISK` — ProductionTraitType TRAIT_RAMESSES->TRAIT_ASOKA at 50; HappinessTraitType TRAIT_RAMESSES->TRAIT_ASOKA at +1; iWarWearinessModifier 25->-25.
- **KEEP** `BUILDING_MAURYAN_GREAT_PALACE` — No field changes.

**Art.** Reuse current pillar/palace/worker art.

**AI/UI/save/MP risk.** AI-safe passive effects; changes city calculations but no schema/type order. Validate Ramesses no longer receives Mauryan benefit; synchronized MP.

**Worker action.** None proposed.

**Validation.** Asoka/Ramesses trait matrix test; war-weariness sign test; pedia help; AI peace autoplay; save/reload and MP checksum.

### 16. `LEADER_PACAL` — `CIVILIZATION_MAYA` (Keep)

**Historical/gameplay thesis.** Monumental court culture and dynastic growth are plausible without forcing speculative mechanics.

**Power budget.** Frozen at live values; zero numeric, mapping, type, art, AI or text changes.

**Frozen object decisions.**

- **KEEP** `TRAIT_PACAL` — No changes.
- **KEEP** `UNIT_MAYA_HOLKAN` — No changes.
- **KEEP** `BUILDING_MAYA_BALL_COURT` — No changes.

**No-change rationale.** Simple growth/culture package with an early defensive UU. Generic health/commerce is less evocative than newer traits but the Ball Court supplies identity.

**Art.** Retain every current art tag and repository asset; smoke only.

**AI/UI/save/MP risk.** Regression-only: no intended AI/UI/save/MP behavior change.

**Worker action.** None proposed.

**Validation.** Baseline/type/mapping digest unchanged; Holkan prerequisites/combat; Ball Court happiness/culture; early AI growth; pedia/art smoke; AI autoplay; save/reload and MP checksum.

### 17. `LEADER_GENGHIS_KHAN` — `CIVILIZATION_MONGOL_EMPIRE` (Targeted differentiation)

**Historical/gameplay thesis.** Mounted command and steppe logistics without unrelated Japanese urban income.

**Power budget.** High package reduced by exactly one leaked improvement-commerce channel.

**Frozen object decisions.**

- **MODIFY** `TRAIT_GENGHIS_KAHN` — Delete ImprovementCommerceChanges entry for IMPROVEMENT_JAPAN_CASTLE_TOWN; every other trait field unchanged.
- **KEEP** `UNIT_MONGOL_KESHIK` — No field changes.
- **KEEP** `BUILDING_MONGOL_GER` — No field changes.
- **KEEP** `BUILDING_MONGOLIAN_PALACE` — No field changes.

**Art.** Reuse current Keshik/Ger/Palace art.

**AI/UI/save/MP risk.** No AI planning loss for an inaccessible foreign improvement; existing Castle Town tiles lose accidental bonus. XML-only, save/MP deterministic.

**Worker action.** None proposed.

**Validation.** Trait parser fixture; Japanese Castle Town before/after with Genghis and Japanese owners; pedia; autoplay; save/reload/MP checksum.

### 18. `LEADER_SITTING_BULL` — `CIVILIZATION_NATIVE_AMERICA` (Targeted differentiation)

**Historical/gameplay thesis.** Healthy defensive communities and trained archers, with transparent trade rather than punitive yield corruption.

**Power budget.** Mid: normalize trade array to neutral [0,0,0]; +2 health, Dog Soldier and Totem remain the complete budget.

**Frozen object decisions.**

- **MODIFY** `TRAIT_SITTING_BULL` — TradeYieldModifiers [150,-500,-500]->[0,0,0]; iHealth=2 unchanged.
- **KEEP** `UNIT_NATIVE_AMERICA_DOG_SOLDIER` — No field changes.
- **KEEP** `BUILDING_NATIVE_AMERICA_TOTEM` — No field changes.

**Art.** Reuse all stock/current art.

**AI/UI/save/MP risk.** Large removal of pathological arithmetic should improve AI; economy of existing saves changes immediately but no schema/type drift; MP deterministic.

**Worker action.** None proposed.

**Validation.** Domestic/foreign route yield cases; negative/overflow regression; tooltip; AI economy autoplay; old-save load and MP checksum.

### 19. `LEADER_WILLEM_VAN_ORANJE` — `CIVILIZATION_NETHERLANDS` (Keep)

**Historical/gameplay thesis.** Dutch maritime commerce, water engineering and religious tolerance are well aligned.

**Power budget.** Frozen at live values; zero numeric, mapping, type, art, AI or text changes.

**Frozen object decisions.**

- **KEEP** `TRAIT_ORANGE` — No changes.
- **KEEP** `UNIT_NETHERLANDS_OOSTINDIEVAARDER` — No changes.
- **KEEP** `BUILDING_NETHERLANDS_DIKE` — No changes.
- **KEEP** `BUILDING_ORANGE_LIGHTHOUSE` — No changes.

**No-change rationale.** Exceptionally coherent water, shipping and trade-city package. Strong trade overlap with Portugal/Venice, but Dike terrain dependence and Galleon timing distinguish it.

**Art.** Retain every current art tag and repository asset; smoke only.

**AI/UI/save/MP risk.** Regression-only: no intended AI/UI/save/MP behavior change.

**Worker action.** None proposed.

**Validation.** Baseline/type/mapping digest unchanged; Oostindievaarder missions; Dike sea production; Lighthouse trade routes; pedia/art smoke; AI autoplay; save/reload and MP checksum.

### 20. `LEADER_CHINESE_LEADER` — `CIVILIZATION_PEOPLES_REPUBLIC_CHINA` (Targeted differentiation)

**Historical/gameplay thesis.** Mass mobilization and danwei administration; remove duplicated farm espionage while keeping workshop production.

**Power budget.** High-to-mid correction: delete only Farm +1 espionage from trait; Volunteer, Danwei and all other trait channels stay.

**Frozen object decisions.**

- **MODIFY** `TRAIT_MAO_MASS_LINE` — Delete ImprovementCityCommerceChanges IMPROVEMENT_FARM espionage +1; retain Workshop production and Spy espionage entries.
- **KEEP** `UNIT_PRC_PEOPLES_VOLUNTEER` — No field changes.
- **KEEP** `BUILDING_PRC_DANWEI_COMMITTEE` — No field changes.

**Art.** Reuse current Volunteer and Danwei art.

**AI/UI/save/MP risk.** AI does not deliberately exploit farm espionage, so clarity improves; recalculates city commerce without save/type change; MP deterministic.

**Worker action.** None proposed.

**Validation.** Worked Farm/Workshop/Spy channel tests; tooltip; AI espionage/production autoplay; save/reload and MP checksum.

### 21. `LEADER_PETER` — `CIVILIZATION_PETRINE_RUSSIA` (Keep)

**Historical/gameplay thesis.** Admiralty and collegial administration fit Petrine reform.

**Power budget.** Frozen at live values; zero numeric, mapping, type, art, AI or text changes.

**Frozen object decisions.**

- **KEEP** `TRAIT_PETER` — No changes.
- **KEEP** `BUILDING_PETER_ADMIRALTY` — No changes.
- **KEEP** `BUILDING_PETER_COLLEGIUM_OF_FOREIGN_AFFAIRS` — No changes.

**No-change rationale.** Modernization, maritime development, bureaucracy and knowledge transfer are sharply expressed without another Russian cavalry unit. No-UU shape differs from most packages but avoids Russian cavalry redundancy.

**Art.** Retain every current art tag and repository asset; smoke only.

**AI/UI/save/MP risk.** Regression-only: no intended AI/UI/save/MP behavior change.

**Worker action.** None proposed.

**Validation.** Baseline/type/mapping digest unchanged; intentional no-UU mapping; Admiralty and Collegium; science/espionage AI; pedia/art smoke; AI autoplay; save/reload and MP checksum.

### 22. `LEADER_CASIMIR` — `CIVILIZATION_POLAND` (Polish)

**Historical/gameplay thesis.** Peaceful legal-cultural development with a mounted reserve.

**Power budget.** Power-neutral Polish: AI flavor redistribution only.

**Frozen object decisions.**

- **KEEP** `TRAIT_CASIMIR` — No field changes.
- **KEEP** `UNIT_POLISH_DRAGOON` — No field changes.
- **KEEP** `BUILDING_POLISH_ROYAL_CASTLE` — No field changes.
- **MODIFY** `LEADER_CASIMIR` — FLAVOR_GROWTH 6->5 and FLAVOR_CULTURE 3->4; all war/diplomacy values unchanged.

**Art.** Reuse current Dragoon and Royal Castle art; animation smoke remains required.

**AI/UI/save/MP risk.** AI build priorities shift slightly; no save schema/type drift; same synchronized values required in MP.

**Worker action.** None proposed.

**Validation.** Leader flavor diff; seeded AI city/culture/autoplay comparison; Dragoon collateral regression; art smoke; MP checksum.

### 23. `LEADER_SALAMASINA_BTG` — `CIVILIZATION_POLYNESIA_BTG` (Polish)

**Historical/gameplay thesis.** Navigation, reef stewardship and ceremonial community should lead; unconditional welfare is support.

**Power budget.** High-to-mid Polish: iHealth 5->3 and iHappiness 3->2; Navigation I and all uniques unchanged.

**Frozen object decisions.**

- **MODIFY** `TRAIT_SALAMASINA_BTG` — iHealth 5->3; iHappiness 3->2; naval Navigation I unchanged.
- **KEEP** `UNIT_POLYNESIA_OCEAN_CANOE_BTG` — No field changes.
- **KEEP** `UNIT_POLYNESIA_WAYFINDER_WORKBOAT_BTG` — No field changes and no new worker action.
- **KEEP** `BUILDING_POLYNESIA_MARAE_BTG` — No field changes.

**Art.** Reuse existing canoe/workboat/Marae and complete Reef Works tile art only; no new worker action proposed.

**AI/UI/save/MP risk.** Passive AI-safe nerf. Existing Reef action remains a high render/placement/persistence risk; no new action/schema. MP synchronized.

**Worker action.** No new worker action; validate existing Reef Works only.

**Validation.** Health/happiness regression; existing Reef Works full build-button-placement-render-pillage-repair-save/AI test; naval animation; MP checksum.

### 24. `LEADER_JOAO` — `CIVILIZATION_PORTUGAL` (Keep)

**Historical/gameplay thesis.** Portuguese oceanic expansion and feitoria trade network fit strongly.

**Power budget.** Frozen at live values; zero numeric, mapping, type, art, AI or text changes.

**Frozen object decisions.**

- **KEEP** `TRAIT_JOAO` — No changes.
- **KEEP** `UNIT_PORTUGAL_CARRACK` — No changes.
- **KEEP** `UNIT_JOAO_SCOUT` — No changes.
- **KEEP** `BUILDING_PORTUGAL_FEITORIA` — No changes.

**No-change rationale.** Exploration, overseas settlement and maritime commerce are clear and highly playable. Some overlap with Willem/Elizabeth, but fast scouting and transport capacity distinguish Portugal.

**Art.** Retain every current art tag and repository asset; smoke only.

**AI/UI/save/MP risk.** Regression-only: no intended AI/UI/save/MP behavior change.

**Worker action.** None proposed.

**Validation.** Baseline/type/mapping digest unchanged; Carrack settler AI/cargo; Scout animation; Feitoria sea commerce; pedia/art smoke; AI autoplay; save/reload and MP checksum.

### 25. `LEADER_QIN_SHI_HUANG` — `CIVILIZATION_QIN_DYNASTY` (Keep)

**Historical/gameplay thesis.** Centralization, fortification and standardization are plausible Qin themes.

**Power budget.** Frozen at live values; zero numeric, mapping, type, art, AI or text changes.

**Frozen object decisions.**

- **KEEP** `TRAIT_QIN_SHI_HUANG` — No changes.
- **KEEP** `UNIT_CHINA_CHOKONU` — No changes.
- **KEEP** `BUILDING_CHINESE_PAVILLION` — No changes.

**No-change rationale.** Strong fortified-state, mass construction and ranged-army identity. Defensive promotion overlap with Churchill/Tokugawa, but collateral crossbows and production AI differentiate it.

**Art.** Retain every current art tag and repository asset; smoke only.

**AI/UI/save/MP risk.** Regression-only: no intended AI/UI/save/MP behavior change.

**Worker action.** None proposed.

**Validation.** Baseline/type/mapping digest unchanged; Cho-Ko-Nu collateral; promotion grants; Pavilion culture; pedia/art smoke; AI autoplay; save/reload and MP checksum.

### 26. `LEADER_ISABELLA` — `CIVILIZATION_SPAIN` (Keep)

**Historical/gameplay thesis.** Theocracy and overseas conquest fit, though later text should avoid reducing Isabella solely to religious warfare.

**Power budget.** Frozen at live values; zero numeric, mapping, type, art, AI or text changes.

**Frozen object decisions.**

- **KEEP** `TRAIT_ISABELLA` — No changes.
- **KEEP** `UNIT_SPANISH_CONQUISTADOR` — No changes.
- **KEEP** `BUILDING_SPANISH_CITADEL` — No changes.

**No-change rationale.** Compact religious-expansion and combined mounted/naval identity. Mounted overlap is common, but naval Morale and siege Citadel provide breadth.

**Art.** Retain every current art tag and repository asset; smoke only.

**AI/UI/save/MP risk.** Regression-only: no intended AI/UI/save/MP behavior change.

**Worker action.** None proposed.

**Validation.** Baseline/type/mapping digest unchanged; mounted/naval Morale; Conquistador melee modifier; Citadel siege XP; pedia/art smoke; AI autoplay; save/reload and MP checksum.

### 27. `LEADER_STALIN` — `CIVILIZATION_USSR` (Major redesign)

**Historical/gameplay thesis.** Forced industrialization and research at a visible happiness cost; espionage remains bounded support.

**Power budget.** Major rebudget to high-but-comparable: one production/research strength and -2 happiness cost; eliminate constraint-breaking Spy/slot/commerce outliers.

**Frozen object decisions.**

- **MODIFY** `TRAIT_STALIN` — Keep iHappiness=-2; change CommerceChanges espionage +50->0 and add existing BuildingYieldChanges entry `BUILDINGCLASS_FACTORY` production +1; no new DLL field.
- **KEEP** `UNIT_RUSSIA_COSSACK` — No field changes.
- **REPLACE** `UNIT_RUSSIA_SPY` — CIVILIZATION_USSR UNITCLASS_SPY mapping -> UNIT_SPY; retain dormant type for type-order/save stability.
- **MODIFY** `BUILDING_RUSSIAN_RESEARCH_INSTITUTE` — Free SPECIALIST_SCIENTIST count 2->1; all other fields unchanged.
- **MODIFY** `BUILDING_USSR_MONUMENT` — iCost 10->30; SPECIALIST_SPY slots 100->1; durable espionage CommerceChange 10->1.
- **MODIFY** `BUILDING_LUBYANKA` — iHappiness 5->-1; espionage CommerceChange 50->0; CommerceModifier 100 retained.

**Art.** Reuse Cossack, stock Spy, current Institute/Monument/Lubyanka art and buttons; no imports.

**AI/UI/save/MP risk.** Major economy/AI valuation change but no IDs removed. Confirm negative building happiness UI. Old saves may contain UNIT_RUSSIA_SPY and keep it valid; MP requires identical XML.

**Worker action.** None proposed.

**Validation.** Exact outlier assertions; capital/city budget model; Spy build mapping; AI industrial/espionage autoplay; pedia; all art; old saves with legacy Spy; MP OOS test.

### 28. `LEADER_ENRICO_DANDOLO` — `CIVILIZATION_VENICE` (Major redesign)

**Historical/gameplay thesis.** Hard-bargaining Venetian trade and expedition logistics through one merchant mission and a normal capital.

**Power budget.** Major rebudget to mid-high: remove +100% upkeep penalty, normalize Palace, and restrict merchant to trade mission only.

**Frozen object decisions.**

- **MODIFY** `TRAIT_DANDOLO` — iUpkeepModifier 100->0; set existing TradeYieldModifiers [food, production, commerce] from [0,0,0] to [0,0,25]; no new mechanic.
- **REPLACE** `UNIT_VENICE_FOUNDER` — CIVILIZATION_VENICE UNITCLASS_SETTLER mapping -> UNIT_SETTLER; retain dormant type.
- **MODIFY** `UNIT_VENETIAN_MERCHANT` — Keep UNITCLASS_MERCHANT trade mission; remove Found, Build Road, BUILDING_GRAND_COLOSSEUM construction, Great Work and worker build actions; iWorkRate 1000->0; retain current movement/cost and art.
- **MODIFY** `BUILDING_VENETIAN_DOGE_PALACE` — iGreatPeopleRateChange 4->2; iHealth 30->2; iHappiness 15->2; iTradeRoutes 6->2; iTradeRouteModifier 50->25; iForeignTradeRouteModifier 50->25; YieldChanges [0,0,8]->[0,0,8]; CommerceChanges espionage 4->0.
- **MODIFY** `LEADER_ENRICO_DANDOLO` — iBasePeaceWeight 8->4; FLAVOR_GROWTH 6->3; add/replace FLAVOR_GOLD=6 and FLAVOR_MILITARY=3; keep Caste System.

**Art.** Reuse stock Settler plus current Venetian Merchant and Palace art. No new worker/build/improvement art and no new action.

**AI/UI/save/MP risk.** Removing unit missions changes UI/AI action set but uses existing XML flags. Legacy Founders/Merchants remain loadable. Validate AI trade mission, save and deterministic MP.

**Worker action.** None proposed.

**Validation.** Action enumeration must show trade mission only; Palace numeric snapshot; AI merchant mission/expedition autoplay; pedia/buttons/models; legacy-unit save; MP OOS test.

### 29. `LEADER_RAGNAR` — `CIVILIZATION_VIKING` (Keep)

**Historical/gameplay thesis.** Viking-Age raiding and ship mobility fit the intended semi-legendary leader archetype.

**Power budget.** Frozen at live values; zero numeric, mapping, type, art, AI or text changes.

**Frozen object decisions.**

- **KEEP** `TRAIT_RAGNAR` — No changes.
- **KEEP** `UNIT_VIKING_BESERKER` — No changes.
- **KEEP** `UNIT_VIKING_SWORDSMAN` — No changes.
- **KEEP** `UNIT_VIKING_AXEMAN` — No changes.
- **KEEP** `BUILDING_VIKING_TRADING_POST` — No changes.

**No-change rationale.** A direct, legible amphibious raiding progression across land and sea. Extreme warmonger overlap with Genghis/Shaka/Montezuma, but amphibious and naval progression distinguishes Ragnar.

**Art.** Retain every current art tag and repository asset; smoke only.

**AI/UI/save/MP risk.** Regression-only: no intended AI/UI/save/MP behavior change.

**Worker action.** None proposed.

**Validation.** Baseline/type/mapping digest unchanged; three raider units and Pillage I; amphibious combat; Trading Post navigation; pedia/art smoke; AI autoplay; save/reload and MP checksum.

### 30. `LEADER_CHURCHILL` — `CIVILIZATION_WARTIME_BRITAIN` (Targeted differentiation)

**Historical/gameplay thesis.** Air defense and war-room intelligence, with MI6 normalized to the stock national-agency envelope.

**Power budget.** High-to-mid correction: MI6 espionage modifier 200->100 and free Spies 2->0; one Spy slot retained.

**Frozen object decisions.**

- **KEEP** `TRAIT_CHURCHILL` — No field changes.
- **KEEP** `UNIT_BRITISH_FIGHTER_COMMAND` — No field changes.
- **KEEP** `BUILDING_BRITISH_WAR_ROOMS` — No field changes.
- **MODIFY** `BUILDING_BRITISH_MI6` — Espionage CommerceModifier 200->100; free SPECIALIST_SPY count 2->0; specialist Spy slot 1 retained.
- **MODIFY** `LEADER_CHURCHILL` — Add FLAVOR_ESPIONAGE=3 while retaining military 5 and gold 2.

**Art.** Reuse current Fighter Command, War Rooms and stock Scotland Yard art for MI6.

**AI/UI/save/MP risk.** AI gains aligned flavor while building loses passive specialists; no schema/type change; synchronized MP.

**Worker action.** None proposed.

**Validation.** MI6 field snapshot/help; Fighter/War Rooms unchanged; interception and espionage AI autoplay; save/reload and MP checksum.

### 31. `LEADER_KUBLAI_KHAN` — `CIVILIZATION_YUAN_DYNASTY` (Targeted differentiation)

**Historical/gameplay thesis.** Yuan road administration and cultural integration capped by a distinct bureaucratic Palace.

**Power budget.** Mid-high but bounded: replace shared resource/Golden Age Palace with a normal Palace variant offering +1 trade route and +2 culture.

**Frozen object decisions.**

- **KEEP** `TRAIT_KUBLAI` — No field changes.
- **KEEP** `UNIT_YUAN_QIANHU_CAVALRY` — No field changes.
- **KEEP** `BUILDING_YUAN_ORTOO_HUB` — No field changes.
- **REPLACE** `BUILDING_MONGOLIAN_PALACE` — Create BUILDING_YUAN_IMPERIAL_SECRETARIAT in BUILDINGCLASS_PALACE, copied from stock Palace: iTradeRoutes=1, CommerceChanges culture +2, no free Horse, no Golden Age/stable prerequisite; map only CIVILIZATION_YUAN_DYNASTY to it. Genghis retains BUILDING_MONGOLIAN_PALACE.

**Art.** Reuse ART_DEF_BUILDING_PALACE and its button; no new model or texture.

**AI/UI/save/MP risk.** One appended BuildingInfo changes synchronized InfoType count/order and save compatibility; must append, never insert. AI handles passive trade/culture; MP manifest update mandatory.

**Worker action.** None proposed.

**Validation.** Type append/order assertion; civ mapping isolation; no Horse/Golden Age trigger; capital trade/culture; pedia; old save and MP OOS test.

### 32. `LEADER_SHAKA` — `CIVILIZATION_ZULU` (Keep)

**Historical/gameplay thesis.** Regimental warfare and centralized military expansion fit the Shakan package.

**Power budget.** Frozen at live values; zero numeric, mapping, type, art, AI or text changes.

**Frozen object decisions.**

- **KEEP** `TRAIT_SHAKA` — No changes.
- **KEEP** `UNIT_ZULU_IMPI` — No changes.
- **KEEP** `BUILDING_ZULU_IKHANDA` — No changes.

**No-change rationale.** Compact, powerful military expansion package with a real economic enabler. Warmonger overlap is inevitable, but fast spear plus maintenance Barracks is unique.

**Art.** Retain every current art tag and repository asset; smoke only.

**AI/UI/save/MP risk.** Regression-only: no intended AI/UI/save/MP behavior change.

**Worker action.** None proposed.

**Validation.** Baseline/type/mapping digest unchanged; Impi mobility; Ikhanda maintenance; trait XP/GG and promotion stack; pedia/art smoke; AI autoplay; save/reload and MP checksum.

## Downstream execution gates

1. Implement one package per slice, except shared text-only updates. Do not broaden a bounded correction.
2. Before each slice, assert baseline mappings/type orders. After XML edits run `tools/test_gate.ps1`; use `-CheckDll` where existing custom-channel compatibility is touched.
3. Run static art closure, Civilopedia/help review, seeded AI autoplay, installed-game action/render smoke, representative old-save load, and deterministic multiplayer test specified per package.
4. Major packages require a before/after budget report. Kublai requires an appended-type manifest/save gate.
5. Installed-game testing remains mandatory; automated schema checks alone do not establish gameplay readiness.

## Readiness

The matrix is complete and implementation-ready. It authorizes no gameplay edit by itself and records no unresolved design question. Runtime merge/deploy readiness is **No** until downstream implementation and installed-game validation complete.
