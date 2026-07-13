# Remaining 32 Roster Audit and Design Input

- Status: `complete`
- Owner / agent: roster-audit
- Last updated: `2026-07-12`
- Runtime changes: **none**

## Scope and method

This audit covers exactly the 32 `remaining_32` packages in
`tools/baselines/roster_baseline.json`, including Washington, Tokugawa, and
Hammurabi. The 27 `recent_27` packages were comparison context only. Live BtS
leader, trait, unit, building, civilization-mapping XML is primary truth;
the baseline fixes cohort membership and mappings. Historical sources support
every non-`Keep` recommendation. No gameplay, XML, DLL, Python, or art file
was changed.

Tiers are deliberately conservative: **Keep** means no identity change;
**Polish** means text, AI, validation, or small tuning; **Targeted
differentiation** means one bounded correction; **Major redesign** means the
whole package needs a separately approved design. Tier assignment is not
implementation approval.

## Executive matrix

| Leader / civilization | Tier | Core identity | Main reason |
|---|---|---|---|
| `LEADER_WASHINGTON` / `CIVILIZATION_AMERICA_FOUNDING_REPUBLIC` | **Targeted differentiation** | A clear revolutionary army plus federal administration identity with good early-to-midgame continuity | Retain the UU/UB and Great General core; in the next matrix collapse the long tail to one bounded institutions/logistics channel |
| `LEADER_GERONIMO_BTG` / `CIVILIZATION_APACHE_CONFEDERACY` | **Polish** | Coherent mobile resistance and field-support package; every component reinforces mobility and endurance | Keep the identity; distinguish the AI from Sitting Bull and verify the Raider's total power budget rather than add mechanics |
| `LEADER_MONTEZUMA` / `CIVILIZATION_AZTEC` | **Keep** | Exceptionally unified conquest, sacrifice, forest warfare and priest economy | No redesign |
| `LEADER_HAMMURABI` / `CIVILIZATION_BABYLON` | **Targeted differentiation** | Law/administration and urban prosperity are strongly expressed and the earlier Hammurabi work is visible in live XML | Preserve all names and the legal identity, but consolidate or reduce duplicate Palace/Courthouse/Garden yields in one bounded balance pass |
| `LEADER_HANNIBAL` / `CIVILIZATION_CARTHAGE` | **Keep** | Combined-arms mobility, elephant access and port commerce form a recognizable Carthaginian package | No redesign; only cross-roster power testing is needed |
| `LEADER_ELIZABETH` / `CIVILIZATION_ELIZABETHAN_ENGLAND` | **Targeted differentiation** | Naval defense, commerce and Great People create a strong Elizabethan maritime-economy identity | Keep the maritime thesis and Royal Exchange; redesign the Sea Dog mapping into one clear era/role or explicitly prove the multi-class contract |
| `LEADER_DE_GAULLE` / `CIVILIZATION_FRANCE_FIFTH_REPUBLIC` | **Keep** | Distinct late national-resilience package with useful early civic identity and mobile gunpowder | No redesign; retain and validate |
| `LEADER_BISMARCK` / `CIVILIZATION_GERMAN_EMPIRE` | **Keep** | Industrial military identity is compact, legible and AI-friendly | No redesign |
| `LEADER_CATHERINE` / `CIVILIZATION_IMPERIAL_RUSSIA` | **Keep** | Culture, elite cavalry and provincial administration combine into a broad but coherent imperial-expansion package | No redesign; later tests should compare Russian cavalry packages |
| `LEADER_HUAYNA_CAPAC` / `CIVILIZATION_INCA` | **Polish** | Strong early expansion and infrastructure identity with a famous, functional Quechua/Terrace core | Retain the package; clarify the civilian promotion and remove a replacement only if it has no observable gameplay value |
| `LEADER_GANDHI` / `CIVILIZATION_INDIA` | **Keep** | A clear nonmilitary Great People and civil-society package with real tradeoffs | No redesign |
| `LEADER_TOKUGAWA` / `CIVILIZATION_JAPAN` | **Keep** | Earlier Tokugawa work produces a focused disciplined-army plus bakufu administration identity | No redesign; retain the earlier work and test its promotion stack |
| `LEADER_SURYAVARMAN` / `CIVILIZATION_KHMER` | **Keep** | Water management, growth and elephant warfare create a compact Khmer identity | No redesign |
| `LEADER_WANGKON` / `CIVILIZATION_KOREA` | **Targeted differentiation** | Very legible scholarship plus defensive artillery identity | Keep Hwacha and one signature science building; use the next matrix to differentiate or normalize the other two rather than add a fourth mechanic |
| `LEADER_ASOKA` / `CIVILIZATION_MAURYA` | **Targeted differentiation** | Dharma, Buddhist spread and low-upkeep governance form a strong nonconquest identity | Correct the bounded Ramesses coupling and reconsider the positive war-weariness modifier; retain the pillar/palace identity |
| `LEADER_PACAL` / `CIVILIZATION_MAYA` | **Keep** | Simple growth/culture package with an early defensive UU | No redesign |
| `LEADER_GENGHIS_KHAN` / `CIVILIZATION_MONGOL_EMPIRE` | **Targeted differentiation** | Mounted mobility, horse access and Great Generals strongly communicate steppe conquest | Delete or replace the Japanese-improvement coupling and narrow the trait to mounted command/logistics |
| `LEADER_SITTING_BULL` / `CIVILIZATION_NATIVE_AMERICA` | **Targeted differentiation** | Defensive denial, health and archer development offer a recognizable survival identity | Replace the extreme trade array with one transparent defensive/diplomatic effect while preserving Dog Soldier and Totem |
| `LEADER_WILLEM_VAN_ORANJE` / `CIVILIZATION_NETHERLANDS` | **Keep** | Exceptionally coherent water, shipping and trade-city package | No redesign |
| `LEADER_CHINESE_LEADER` / `CIVILIZATION_PEOPLES_REPUBLIC_CHINA` | **Targeted differentiation** | Mass mobilization, cheaper infantry, workplace organization and state administration are mechanically integrated | Retain the volunteer/danwei core and reduce one duplicated trait channel after numerical comparison |
| `LEADER_PETER` / `CIVILIZATION_PETRINE_RUSSIA` | **Keep** | Modernization, maritime development, bureaucracy and knowledge transfer are sharply expressed without another Russian cavalry unit | No redesign; keep the deliberate no-UU structure |
| `LEADER_CASIMIR` / `CIVILIZATION_POLAND` | **Polish** | Peaceful domestic identity paired with a bounded mounted military reserve | Keep the package; improve text/AI framing first, and only later consider one small civic-development adjustment |
| `LEADER_SALAMASINA_BTG` / `CIVILIZATION_POLYNESIA_BTG` | **Polish** | Excellent seafaring, ocean development and ceremonial/community package | Do not redesign |
| `LEADER_JOAO` / `CIVILIZATION_PORTUGAL` | **Keep** | Exploration, overseas settlement and maritime commerce are clear and highly playable | No redesign |
| `LEADER_QIN_SHI_HUANG` / `CIVILIZATION_QIN_DYNASTY` | **Keep** | Strong fortified-state, mass construction and ranged-army identity | No redesign |
| `LEADER_ISABELLA` / `CIVILIZATION_SPAIN` | **Keep** | Compact religious-expansion and combined mounted/naval identity | No redesign |
| `LEADER_STALIN` / `CIVILIZATION_USSR` | **Major redesign** | Production, research and secret-police identity is unmistakable | Rebuild around one production/research strength and one explicit coercion cost; retain recognizable names but rebudget every component together |
| `LEADER_ENRICO_DANDOLO` / `CIVILIZATION_VENICE` | **Keep** | Venetian trade and merchant-government identity is immediately visible | No redesign; preserve the complete package by explicit user direction |
| `LEADER_RAGNAR` / `CIVILIZATION_VIKING` | **Keep** | A direct, legible amphibious raiding progression across land and sea | No redesign |
| `LEADER_CHURCHILL` / `CIVILIZATION_WARTIME_BRITAIN` | **Targeted differentiation** | Excellent air defense, national resilience and intelligence identity | Keep Fighter Command and War Rooms; normalize MI6 or the duplicated espionage channel and align AI flavor/weight |
| `LEADER_KUBLAI_KHAN` / `CIVILIZATION_YUAN_DYNASTY` | **Targeted differentiation** | Road logistics, postal/trade hub and culturally oriented conquest are a strong Yuan identity | Retain Qianhu/Ortoo logistics and replace or specialize the shared Palace so Yuan administration, not generic Mongol horse supply, is the capstone |
| `LEADER_SHAKA` / `CIVILIZATION_ZULU` | **Keep** | Compact, powerful military expansion package with a real economic enabler | No redesign |

Tier totals: **Targeted differentiation 10**, **Polish 4**, **Keep 17**, **Major redesign 1**.

## Package audits

### 1. `LEADER_WASHINGTON` — `CIVILIZATION_AMERICA_FOUNDING_REPUBLIC`

- **Tier:** Targeted differentiation
- **Current trait:** TRAIT_GEORGE_WASHINGTON: +50% Great General and domestic Great General rates; Town +1 commerce; Barracks +1 production; Courthouse +2 espionage; Bank +2 gold; Spy +1 espionage; Merchant +1 gold; Wheat +1 food; Horse +1 production; Road +1 commerce.
- **Personality theme:** Peace-weight 8, military 5/growth 2, Free Speech; reluctant to initiate major war, no razing, above-normal espionage.
- **UU/UB/replacement package:** Continental Line Infantry replaces Musketman (75 cost, Drill I and City Garrison I); Federal Hall replaces Courthouse (+2 culture and +2 espionage in the live entry).
- **Palace/improvement/DLL dependency:** Trait relies on the extended trait yield tables read by the custom DLL; no unique palace or improvement.
- **Current strengths:** A clear revolutionary army plus federal administration identity with good early-to-midgame continuity.
- **Overlap/redundancy:** The trait occupies ten economic/military channels and overlaps generic American growth, commerce, espionage, and command identities; it is difficult to read and budget.
- **Historical fit:** Continental infantry and civil administration fit Washington, while the broad resource/Town/Bank bundle is less specific than his military and institution-building record.
- **AI/art risks:** Stock leader/unit art lowers rendering risk. AI can use passive yields, but does not deliberately optimize the scattered resource, specialist, and route bonuses.
- **Design input:** Retain the UU/UB and Great General core; in the next matrix collapse the long tail to one bounded institutions/logistics channel.
- **Historical research:** [https://www.mountvernon.org/george-washington/the-revolutionary-war/washingtons-revolutionary-war-battles](https://www.mountvernon.org/george-washington/the-revolutionary-war/washingtons-revolutionary-war-battles)
- **Live evidence:** leader `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Civilizations/CIV4LeaderHeadInfos.xml:28153-28726`; trait `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Civilizations/CIV4TraitInfos.xml:317-427`; units `UNIT_CONTINENTAL_LINE_INFANTRY` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Units/CIV4UnitInfos.xml:10675-10863); buildings `BUILDING_FEDERAL_HALL` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Buildings/CIV4BuildingInfos.xml:17028-17232).

### 2. `LEADER_GERONIMO_BTG` — `CIVILIZATION_APACHE_CONFEDERACY`

- **Tier:** Polish
- **Current trait:** TRAIT_LEADER_GERONIMO: +25% Great General and domestic Great General rates; Combat I to mounted and gun units.
- **Personality theme:** Peace-weight 8, military 5/growth 2, Environmentalism; defensive/high unit build profile copied almost exactly from Sitting Bull.
- **UU/UB/replacement package:** Three-move Medicine Man scout with Medic I/II and Sentry; three-move Apache Raider with Flanking I/II, Sentry, rival-territory access, hills bonuses and 40% withdrawal; War Council Barracks adds XP, happiness and military production.
- **Palace/improvement/DLL dependency:** Uses ordinary promotion/leader XML channels; no unique palace or improvement.
- **Current strengths:** Coherent mobile resistance and field-support package; every component reinforces mobility and endurance.
- **Overlap/redundancy:** Personality is materially redundant with Sitting Bull, and the Raider is carrying many advantages at once.
- **Historical fit:** Mobile raiding and resistance fit Geronimo's documented defense of Chiricahua homelands; the generalized 'medicine man' combat support role should be handled carefully.
- **AI/art risks:** Custom unit/leader art needs in-game animation checks. Copied diplomacy logic may make Geronimo too passive to exploit the raider.
- **Design input:** Keep the identity; distinguish the AI from Sitting Bull and verify the Raider's total power budget rather than add mechanics.
- **Historical research:** [https://www.britannica.com/biography/Geronimo](https://www.britannica.com/biography/Geronimo)
- **Live evidence:** leader `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Civilizations/CIV4LeaderHeadInfos.xml:7855-8910`; trait `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Civilizations/CIV4TraitInfos.xml:2766-2819`; units `UNIT_APACHE_MEDICINE_MAN_BTG` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Units/CIV4UnitInfos.xml:28719-28903), `UNIT_APACHE_RAIDER_BTG` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Units/CIV4UnitInfos.xml:28904-29119); buildings `BUILDING_APACHE_WAR_COUNCIL_BTG` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Buildings/CIV4BuildingInfos.xml:38874-39094).

### 3. `LEADER_MONTEZUMA` — `CIVILIZATION_AZTEC`

- **Tier:** Keep
- **Current trait:** TRAIT_MONTEZUMA: custom Montezuma promotion to recon, archery and melee units.
- **Personality theme:** Peace-weight 0, military 5/religion 2, Police State; extremely frequent war, high unit production and razing.
- **UU/UB/replacement package:** Cheap strength-4 Jaguar with Woodsman I; early Sacrificial Altar with priest slots and -90% hurry anger; Aztec Great Palace adds priest production, population and global hurry support.
- **Palace/improvement/DLL dependency:** Unique Great Palace; trait promotion requires the existing custom promotion/DLL rules but no new contract.
- **Current strengths:** Exceptionally unified conquest, sacrifice, forest warfare and priest economy.
- **Overlap/redundancy:** Some thematic overlap with other extreme warmongers, but the hurry/priest axis is distinct.
- **Historical fit:** The package captures militarized Mexica state religion, though sacrificial framing should remain precise rather than sensationalized.
- **AI/art risks:** Stock core art is low risk; palace and custom promotion still require tooltip and render smoke coverage. AI already values war and units.
- **Design input:** No redesign. Validate the palace/promotion help and watch early hurry stacking in later balance tests.
- **Historical research:** No change recommendation; live package retained.
- **Live evidence:** leader `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Civilizations/CIV4LeaderHeadInfos.xml:17673-18217`; trait `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Civilizations/CIV4TraitInfos.xml:1494-1551`; units `UNIT_AZTEC_JAGUAR` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Units/CIV4UnitInfos.xml:7362-7550); buildings `BUILDING_AZTEC_SACRIFICIAL_ALTAR` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Buildings/CIV4BuildingInfos.xml:17442-17622), `BUILDING_AZTEC_PALACE` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Buildings/CIV4BuildingInfos.xml:887-1079).

### 4. `LEADER_HAMMURABI` — `CIVILIZATION_BABYLON`

- **Tier:** Targeted differentiation
- **Current trait:** TRAIT_HAMMURABI: -35% civic upkeep.
- **Personality theme:** Peace-weight 8, culture flavor 10, Bureaucracy; peaceful, non-razing builder with moderate unit production.
- **UU/UB/replacement package:** Bowman gains +50% versus melee; Royal Palace adds yields, commerce, Great Spy points, health, happiness, maintenance and trade; Garden adds health/culture/Great People; Babylon Courthouse adds production, commerce, culture, happiness and Great People.
- **Palace/improvement/DLL dependency:** Unique Palace plus two further building replacements; no unique improvement.
- **Current strengths:** Law/administration and urban prosperity are strongly expressed and the earlier Hammurabi work is visible in live XML.
- **Overlap/redundancy:** Three enhanced buildings plus a large Palace cause cumulative city-economy overlap; the culture-10 personality underplays administration and expansion.
- **Historical fit:** Law and centralized administration are strongly grounded; gardens are plausible Babylonian urban identity but should not eclipse the legal thesis.
- **AI/art risks:** Mostly stock art, but custom palace/courthouse entries need render/help closure. Passive bonuses are AI-safe; the cumulative budget is the main risk.
- **Design input:** Preserve all names and the legal identity, but consolidate or reduce duplicate Palace/Courthouse/Garden yields in one bounded balance pass.
- **Historical research:** [https://www.britannica.com/biography/Hammurabi](https://www.britannica.com/biography/Hammurabi)
- **Live evidence:** leader `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Civilizations/CIV4LeaderHeadInfos.xml:9996-10542`; trait `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Civilizations/CIV4TraitInfos.xml:2044-2083`; units `UNIT_BABYLON_BOWMAN` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Units/CIV4UnitInfos.xml:14633-14817); buildings `BUILDING_BABYLON_ROYAL_PALACE` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Buildings/CIV4BuildingInfos.xml:349-518), `BUILDING_BABYLON_GARDEN` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Buildings/CIV4BuildingInfos.xml:13477-13647), `BUILDING_BABYLON_COURTHOUSE` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Buildings/CIV4BuildingInfos.xml:17623-17807).

### 5. `LEADER_HANNIBAL` — `CIVILIZATION_CARTHAGE`

- **Tier:** Keep
- **Current trait:** TRAIT_HANNIBAL: +1 happiness; Ivory gains +1 food and +1 production.
- **Personality theme:** Peace-weight 2, military 5/gold 2, Free Market; opportunistic warfare, moderate razing and unit production.
- **UU/UB/replacement package:** Numidian Cavalry is a flanking/melee-counter horse archer; African War Elephant trades strength for two moves; Cothon adds a trade route; Byrsa treasury Great Palace supplies Ivory.
- **Palace/improvement/DLL dependency:** Unique Great Palace and resource-yield trait; no unique improvement.
- **Current strengths:** Combined-arms mobility, elephant access and port commerce form a recognizable Carthaginian package.
- **Overlap/redundancy:** Shares mounted aggression with several leaders, but Cothon/trade and generated Ivory give it a distinct strategic arc.
- **Historical fit:** Carthage's maritime commerce and Hannibal's mixed army are well represented.
- **AI/art risks:** Core art is largely established; elephant treasury art/help needs smoke testing. AI flavors can exploit both military and trade.
- **Design input:** No redesign; only cross-roster power testing is needed.
- **Historical research:** No change recommendation; live package retained.
- **Live evidence:** leader `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Civilizations/CIV4LeaderHeadInfos.xml:10543-11095`; trait `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Civilizations/CIV4TraitInfos.xml:1878-1927`; units `UNIT_CARTHAGE_NUMIDIAN_CAVALRY` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Units/CIV4UnitInfos.xml:16151-16362), `UNIT_CARTHAGE_AFRICAN_WAR_ELEPHANT` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Units/CIV4UnitInfos.xml:18733-18917); buildings `BUILDING_CARTHAGE_COTHON` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Buildings/CIV4BuildingInfos.xml:5987-6166), `BUILDING_CARTHAGE_BYRSA_ELEPHANT_TREASURY` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Buildings/CIV4BuildingInfos.xml:703-886).

### 6. `LEADER_ELIZABETH` — `CIVILIZATION_ELIZABETHAN_ENGLAND`

- **Tier:** Targeted differentiation
- **Current trait:** TRAIT_ELIZABETH: +75% Great People rate and an extra-yield threshold of 2 in the live trait table.
- **Personality theme:** Peace-weight 9, gold 5/culture 2, Free Religion; very peaceful, low unit build and no razing.
- **UU/UB/replacement package:** One Sea Dog type is assigned as the Galley, Trireme and Privateer replacement; its live unit class is Privateer, with early Sailing/Metal Casting access, strength 6, three moves, cargo 4, bombard and mixed naval AIs. Royal Exchange is an early Guilds Bank with +5 gold and 65% gold.
- **Palace/improvement/DLL dependency:** No palace/improvement; multi-class civilization mapping to one UnitInfo is an unusual synchronization and AI contract.
- **Current strengths:** Naval defense, commerce and Great People create a strong Elizabethan maritime-economy identity.
- **Overlap/redundancy:** The same unit replacing three eras/classes collapses naval progression and creates AI/upgrade ambiguity; Royal Exchange and trait are already powerful.
- **Historical fit:** Maritime defense, intelligence and commercial expansion fit Elizabeth I, but a single ship spanning galley through privateer is historically and mechanically blunt.
- **AI/art risks:** High AI risk from conflicting class/default-AI/cargo roles; high art/animation test burden across three replacement contexts.
- **Design input:** Keep the maritime thesis and Royal Exchange; redesign the Sea Dog mapping into one clear era/role or explicitly prove the multi-class contract.
- **Historical research:** [https://www.rmg.co.uk/stories/royal-history/elizabeth-i-spanish-armada](https://www.rmg.co.uk/stories/royal-history/elizabeth-i-spanish-armada)
- **Live evidence:** leader `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Civilizations/CIV4LeaderHeadInfos.xml:6759-7309`; trait `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Civilizations/CIV4TraitInfos.xml:1788-1827`; units `UNIT_ENGLISH_SEA_DOG` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Units/CIV4UnitInfos.xml:22903-23105), `UNIT_ENGLISH_SEA_DOG` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Units/CIV4UnitInfos.xml:22903-23105), `UNIT_ENGLISH_SEA_DOG` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Units/CIV4UnitInfos.xml:22903-23105); buildings `BUILDING_ENGLISH_ROYAL_EXCHANGE` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Buildings/CIV4BuildingInfos.xml:15478-15646).

### 7. `LEADER_DE_GAULLE` — `CIVILIZATION_FRANCE_FIFTH_REPUBLIC`

- **Tier:** Keep
- **Current trait:** TRAIT_DE_GAULLE: +1 happiness.
- **Personality theme:** Peace-weight 0, production 5/growth 2, Nationhood; aggressive limited-war planner, no razing.
- **UU/UB/replacement package:** Two-move Musketeer; strengthened Broadcast Tower with defense, XP, military production/healing and war-weariness relief; cheap Fifth Republic Monument with durable culture.
- **Palace/improvement/DLL dependency:** No palace or improvement; building fields are standard XML.
- **Current strengths:** Distinct late national-resilience package with useful early civic identity and mobile gunpowder.
- **Overlap/redundancy:** Some defensive morale overlap with Churchill, but era and production channels differ.
- **Historical fit:** Nationhood, resistance and mass communication fit de Gaulle's wartime and Fifth Republic careers.
- **AI/art risks:** Stock leader/unit art is low risk; custom monument needs button/help smoke. AI production flavor can use the package.
- **Design input:** No redesign; retain and validate.
- **Historical research:** No change recommendation; live package retained.
- **Live evidence:** leader `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Civilizations/CIV4LeaderHeadInfos.xml:6212-6758`; trait `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Civilizations/CIV4TraitInfos.xml:1045-1084`; units `UNIT_FRENCH_MUSKETEER` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Units/CIV4UnitInfos.xml:10864-11047); buildings `BUILDING_FRENCH_BROADCAST_TOWER` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Buildings/CIV4BuildingInfos.xml:13841-14042), `BUILDING_FRENCH_FIFTH_REPUBLIC_MONUMENT` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Buildings/CIV4BuildingInfos.xml:8850-9024).

### 8. `LEADER_BISMARCK` — `CIVILIZATION_GERMAN_EMPIRE`

- **Tier:** Keep
- **Current trait:** TRAIT_BISMARCK: +3 health and a production extra-yield threshold of 5.
- **Personality theme:** Peace-weight 6, military flavor 10, Nationhood; moderate war and strong unit emphasis without razing.
- **UU/UB/replacement package:** Panzer gains +50% versus armor; Assembly Plant gains coal production and four engineer slots.
- **Palace/improvement/DLL dependency:** No unique palace/improvement; standard trait and building channels.
- **Current strengths:** Industrial military identity is compact, legible and AI-friendly.
- **Overlap/redundancy:** Late timing overlaps other industrial leaders, but the armor/engineer combination remains distinct.
- **Historical fit:** Industrialization and state military power fit imperial Germany under Bismarck, even if the Panzer is chronologically later.
- **AI/art risks:** Stock assets and standard AI roles are low risk; late-era balance is the only material unknown.
- **Design input:** No redesign.
- **Historical research:** No change recommendation; live package retained.
- **Live evidence:** leader `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Civilizations/CIV4LeaderHeadInfos.xml:1832-2374`; trait `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Civilizations/CIV4TraitInfos.xml:1248-1287`; units `UNIT_GERMAN_PANZER` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Units/CIV4UnitInfos.xml:19297-19490); buildings `BUILDING_GERMAN_ASSEMBLY_PLANT` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Buildings/CIV4BuildingInfos.xml:7610-7805).

### 9. `LEADER_CATHERINE` — `CIVILIZATION_IMPERIAL_RUSSIA`

- **Tier:** Keep
- **Current trait:** TRAIT_CATHERINE: +50% Great People and Great General rates plus a flat commerce-channel bonus.
- **Personality theme:** Peace-weight 2, culture 6/military 4/gold 5, Bureaucracy; expansionist, espionage-aware and willing to wage war.
- **UU/UB/replacement package:** Three-move Black Sea Hussar with Flanking I and Sentry; Noble Assembly Courthouse adds gold/culture and an Artist slot.
- **Palace/improvement/DLL dependency:** Extended trait commerce channel; no palace/improvement.
- **Current strengths:** Culture, elite cavalry and provincial administration combine into a broad but coherent imperial-expansion package.
- **Overlap/redundancy:** Some overlap with other Russian cavalry leaders, but the culture/assembly angle distinguishes it.
- **Historical fit:** Elite cavalry, court culture and noble administration plausibly fit Catherine's imperial program.
- **AI/art risks:** Custom cavalry/building art requires smoke checks; AI flavors cover military, culture and gold.
- **Design input:** No redesign; later tests should compare Russian cavalry packages.
- **Historical research:** No change recommendation; live package retained.
- **Live evidence:** leader `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Civilizations/CIV4LeaderHeadInfos.xml:3473-4014`; trait `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Civilizations/CIV4TraitInfos.xml:1006-1045`; units `UNIT_IMPERIAL_RUSSIA_BLACK_SEA_HUSSAR` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Units/CIV4UnitInfos.xml:17747-17953); buildings `BUILDING_IMPERIAL_RUSSIA_NOBLE_ASSEMBLY` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Buildings/CIV4BuildingInfos.xml:16815-17027).

### 10. `LEADER_HUAYNA_CAPAC` — `CIVILIZATION_INCA`

- **Tier:** Polish
- **Current trait:** TRAIT_HUAYNA_CAPAC: extra-yield threshold 5, +25% trade-yield modifier, and a custom Huayna promotion for recon, archery, mounted and melee units.
- **Personality theme:** Peace-weight 2, gold 5/production 2, Hereditary Rule; opportunistic expansion and moderate aggression.
- **UU/UB/replacement package:** Quechua receives Combat I and +100% versus archery; Worker and Settler receive the Huayna promotion; Terrace adds production and durable culture.
- **Palace/improvement/DLL dependency:** Trait/promotion DLL support; no unique palace or improvement.
- **Current strengths:** Strong early expansion and infrastructure identity with a famous, functional Quechua/Terrace core.
- **Overlap/redundancy:** Leader-wide promotion plus separate Worker/Settler replacements broadens the package without making their actual advantage obvious.
- **Historical fit:** Imperial expansion and road/infrastructure administration fit Huayna Capac.
- **AI/art risks:** Stock core art is low risk; custom Worker/Settler art groups and noncombat promotions need animation/help checks. AI valuation of promoted civilian units is uncertain.
- **Design input:** Retain the package; clarify the civilian promotion and remove a replacement only if it has no observable gameplay value.
- **Historical research:** [https://www.britannica.com/biography/Huayna-Capac](https://www.britannica.com/biography/Huayna-Capac)
- **Live evidence:** leader `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Civilizations/CIV4LeaderHeadInfos.xml:11640-12188`; trait `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Civilizations/CIV4TraitInfos.xml:1084-1145`; units `UNIT_INCAN_QUECHUA` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Units/CIV4UnitInfos.xml:6794-6988), `UNIT_HUAYNA_WORKER` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Units/CIV4UnitInfos.xml:1861-2151), `UNIT_HUAYNA_SETTLER` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Units/CIV4UnitInfos.xml:1093-1297); buildings `BUILDING_INCAN_TERRACE` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Buildings/CIV4BuildingInfos.xml:4029-4220).

### 11. `LEADER_GANDHI` — `CIVILIZATION_INDIA`

- **Tier:** Keep
- **Current trait:** TRAIT_GHANDI: +75% Great People rate.
- **Personality theme:** Peace-weight 10, culture flavor 10, Universal Suffrage; least warlike profile, minimal unit production and no razing.
- **UU/UB/replacement package:** Three-move Fast Worker; Mausoleum Jail adds happiness; Gandhi Forge adds happiness/Great People but modest worker and war-weariness penalties.
- **Palace/improvement/DLL dependency:** No palace/improvement; standard XML modifiers.
- **Current strengths:** A clear nonmilitary Great People and civil-society package with real tradeoffs.
- **Overlap/redundancy:** Asoka shares the Fast Worker, but their buildings, trait and personality diverge.
- **Historical fit:** The pacific/civic emphasis is recognizable and not overdesigned.
- **AI/art risks:** Stock Fast Worker and leader art lower risk; custom Forge/Mausoleum need pedia/render validation. AI can use passive effects.
- **Design input:** No redesign.
- **Historical research:** No change recommendation; live package retained.
- **Live evidence:** leader `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Civilizations/CIV4LeaderHeadInfos.xml:7855-8367`; trait `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Civilizations/CIV4TraitInfos.xml:1927-1966`; units `UNIT_INDIAN_FAST_WORKER` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Units/CIV4UnitInfos.xml:1584-1860); buildings `BUILDING_INDIAN_MAUSOLEUM` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Buildings/CIV4BuildingInfos.xml:18546-18726), `BUILDING_GANDHI_FORGE` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Buildings/CIV4BuildingInfos.xml:7048-7214).

### 12. `LEADER_TOKUGAWA` — `CIVILIZATION_JAPAN`

- **Tier:** Keep
- **Current trait:** TRAIT_TOKUGAWA: Combat I, City Garrison I and Drill I to archery, melee and gun units.
- **Personality theme:** Peace-weight 1, science 5/military 2, Mercantilism; guarded, war-capable and low-espionage, with moderate unit production.
- **UU/UB/replacement package:** Iron-requiring Samurai with two first strikes, Drill I and Kamikaze prerequisite; Bakufu Magistracy Courthouse adds espionage and 3 XP.
- **Palace/improvement/DLL dependency:** Custom promotion prerequisite and trait free-promotion tables; no palace/improvement.
- **Current strengths:** Earlier Tokugawa work produces a focused disciplined-army plus bakufu administration identity.
- **Overlap/redundancy:** Military promotion breadth is strong but coherent; limited overlap with Qin/Churchill defensive promotions is offset by Samurai and espionage court.
- **Historical fit:** Samurai and bakufu administration fit Tokugawa rule; science flavor prevents a purely isolationist caricature.
- **AI/art risks:** Stock Samurai/leader art is low risk; Kamikaze prerequisite/help and Magistracy art still need gameplay smoke. AI understands XP and promotions.
- **Design input:** No redesign; retain the earlier work and test its promotion stack.
- **Historical research:** No change recommendation; live package retained.
- **Live evidence:** leader `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Civilizations/CIV4LeaderHeadInfos.xml:26469-27028`; trait `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Civilizations/CIV4TraitInfos.xml:3083-3148`; units `UNIT_JAPAN_SAMURAI` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Units/CIV4UnitInfos.xml:9114-9319); buildings `BUILDING_JAPAN_BAKUFU_MAGISTRACY` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Buildings/CIV4BuildingInfos.xml:17808-17988).

### 13. `LEADER_SURYAVARMAN` — `CIVILIZATION_KHMER`

- **Tier:** Keep
- **Current trait:** TRAIT_SURYAVARMAN: +2 happiness, +50% trade yield and a flat commerce bonus.
- **Personality theme:** Peace-weight 1, gold 5/culture 2, Organized Religion; expansionist, moderately aggressive and religious.
- **UU/UB/replacement package:** Ballista Elephant targets mounted units; Baray Aqueduct adds food and +1 food to Farms.
- **Palace/improvement/DLL dependency:** Baray uses the custom building improvement-yield table already supported by the DLL.
- **Current strengths:** Water management, growth and elephant warfare create a compact Khmer identity.
- **Overlap/redundancy:** Farm growth overlaps other agrarian packages but the Aqueduct attachment is distinctive.
- **Historical fit:** Baray/reservoir infrastructure and monumental religious state power are good Angkorian signals.
- **AI/art risks:** Stock unit/building art is comparatively safe; improvement-yield tooltip and AI valuation require smoke/autoplay.
- **Design input:** No redesign.
- **Historical research:** No change recommendation; live package retained.
- **Live evidence:** leader `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Civilizations/CIV4LeaderHeadInfos.xml:25911-26468`; trait `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Civilizations/CIV4TraitInfos.xml:3044-3083`; units `UNIT_KHMER_BALLISTA_ELEPHANT` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Units/CIV4UnitInfos.xml:18918-19107); buildings `BUILDING_KHMER_BARAY` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Buildings/CIV4BuildingInfos.xml:4563-4743).

### 14. `LEADER_WANGKON` — `CIVILIZATION_KOREA`

- **Tier:** Targeted differentiation
- **Current trait:** TRAIT_WANGKON: +2 in a flat commerce channel.
- **Personality theme:** Peace-weight 8, gold 5/science 2, Caste System; peaceful but not helpless, with moderate espionage.
- **UU/UB/replacement package:** Hwacha gains +50% versus melee; Seowon University has 35% research; Korean Library has 50% research, durable research and +5 Great People; Korean Academy has 75% research and +5 siege XP.
- **Palace/improvement/DLL dependency:** No palace/improvement; three science-building replacements create a civilization-level progression.
- **Current strengths:** Very legible scholarship plus defensive artillery identity.
- **Overlap/redundancy:** Library, University and Academy all amplify the same science channel, producing redundant multiplicative scaling and crowding other scholar civilizations.
- **Historical fit:** Goryeo's state formation and cultural institutions support scholarship, but Wang Kon's unification and administration are underrepresented.
- **AI/art risks:** Mostly standard building art; three replacements increase button/model closure workload. AI science flavor uses them, but may overvalue the stack.
- **Design input:** Keep Hwacha and one signature science building; use the next matrix to differentiate or normalize the other two rather than add a fourth mechanic.
- **Historical research:** [https://www.britannica.com/biography/Wang-Kon](https://www.britannica.com/biography/Wang-Kon)
- **Live evidence:** leader `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Civilizations/CIV4LeaderHeadInfos.xml:27588-28152`; trait `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Civilizations/CIV4TraitInfos.xml:840-879`; units `UNIT_KOREAN_HWACHA` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Units/CIV4UnitInfos.xml:20050-20239); buildings `BUILDING_KOREAN_SEOWON` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Buildings/CIV4BuildingInfos.xml:11252-11434), `BUILDING_KOREAN_LIBRARY` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Buildings/CIV4BuildingInfos.xml:10680-10857), `BUILDING_KOREAN_ACADEMY` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Buildings/CIV4BuildingInfos.xml:10287-10464).

### 15. `LEADER_ASOKA` — `CIVILIZATION_MAURYA`

- **Tier:** Targeted differentiation
- **Current trait:** TRAIT_ASOKA: -50% civic upkeep.
- **Personality theme:** Peace-weight 8, religion 8/science 2, Pacifism; peaceful, low unit build and non-razing.
- **UU/UB/replacement package:** Fast Worker; Mauryan Obelisk adds Priest slot, happiness and war-weariness, but its production/happiness trait references point to TRAIT_RAMESSES; Mauryan Great Palace supplies an Asoka bonus, Buddhism, free Obelisks, Golden Age and happiness.
- **Palace/improvement/DLL dependency:** Unique Great Palace and custom bonus; live Obelisk contains cross-leader Ramesses references.
- **Current strengths:** Dharma, Buddhist spread and low-upkeep governance form a strong nonconquest identity.
- **Overlap/redundancy:** Fast Worker overlaps Gandhi; the Ramesses coupling appears accidental and the Obelisk's +25% war weariness cuts against the intended thesis.
- **Historical fit:** Buddhist patronage, edicts/pillars and post-Kalinga dharma are directly grounded.
- **AI/art risks:** Cross-trait XML is an AI/balance maintenance risk; custom palace/bonus art and help require closure.
- **Design input:** Correct the bounded Ramesses coupling and reconsider the positive war-weariness modifier; retain the pillar/palace identity.
- **Historical research:** [https://www.britannica.com/biography/Ashoka](https://www.britannica.com/biography/Ashoka)
- **Live evidence:** leader `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Civilizations/CIV4LeaderHeadInfos.xml:741-1289`; trait `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Civilizations/CIV4TraitInfos.xml:2820-2859`; units `UNIT_INDIAN_FAST_WORKER` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Units/CIV4UnitInfos.xml:1584-1860); buildings `BUILDING_MAURYAN_OBELISK` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Buildings/CIV4BuildingInfos.xml:9394-9582), `BUILDING_MAURYAN_GREAT_PALACE` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Buildings/CIV4BuildingInfos.xml:1256-1426).

### 16. `LEADER_PACAL` — `CIVILIZATION_MAYA`

- **Tier:** Keep
- **Current trait:** TRAIT_PACAL: +2 health and a flat +2 commerce-channel bonus.
- **Personality theme:** Peace-weight 2, culture 5/growth 2, Hereditary Rule; generally reluctant to major-war, moderate unit production.
- **UU/UB/replacement package:** Holkan is first-strike immune and has alternate Bronze Working access; Ball Court adds substantial happiness and durable culture.
- **Palace/improvement/DLL dependency:** No palace/improvement or notable new DLL contract.
- **Current strengths:** Simple growth/culture package with an early defensive UU.
- **Overlap/redundancy:** Generic health/commerce is less evocative than newer traits but the Ball Court supplies identity.
- **Historical fit:** Monumental court culture and dynastic growth are plausible without forcing speculative mechanics.
- **AI/art risks:** Stock assets and passive AI effects are low risk.
- **Design input:** No redesign.
- **Historical research:** No change recommendation; live package retained.
- **Live evidence:** leader `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Civilizations/CIV4LeaderHeadInfos.xml:18769-19319`; trait `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Civilizations/CIV4TraitInfos.xml:2473-2512`; units `UNIT_MAYA_HOLKAN` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Units/CIV4UnitInfos.xml:9924-10112); buildings `BUILDING_MAYA_BALL_COURT` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Buildings/CIV4BuildingInfos.xml:13307-13476).

### 17. `LEADER_GENGHIS_KHAN` — `CIVILIZATION_MONGOL_EMPIRE`

- **Tier:** Targeted differentiation
- **Current trait:** TRAIT_GENGHIS_KAHN: +50% upkeep, +75% Great General rate; Workshop/Barracks/Castle/Courthouse, Horse/Rice and specialist yields; Sentry and Mobility to mounted units. It also grants commerce from IMPROVEMENT_JAPAN_CASTLE_TOWN.
- **Personality theme:** Peace-weight 0, military flavor 10, Police State; extremely aggressive, high unit build and 75% razing.
- **UU/UB/replacement package:** Keshik ignores terrain, has first strike and withdrawal; Ger gives mounted XP; Mongolian Great Palace supplies Horses and a Golden Age after stable prerequisites.
- **Palace/improvement/DLL dependency:** Unique Great Palace; trait uses many extended DLL yield tables and contains a cross-civilization Japanese improvement dependency.
- **Current strengths:** Mounted mobility, horse access and Great Generals strongly communicate steppe conquest.
- **Overlap/redundancy:** The Japanese Castle Town reference is unrelated leakage; broad building/resource/specialist bonuses overfill an already excellent Keshik/Ger/Palace package.
- **Historical fit:** Unification of Mongol tribes, disciplined mobile armies and continental conquest fit; Japanese Castle Town income does not.
- **AI/art risks:** Stock Keshik/Ger art is safe, palace less so. AI is already optimized for war; passive unrelated bonuses inflate power without improving decisions.
- **Design input:** Delete or replace the Japanese-improvement coupling and narrow the trait to mounted command/logistics.
- **Historical research:** [https://www.britannica.com/biography/Genghis-Khan](https://www.britannica.com/biography/Genghis-Khan)
- **Live evidence:** leader `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Civilizations/CIV4LeaderHeadInfos.xml:8911-9453`; trait `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Civilizations/CIV4TraitInfos.xml:636-801`; units `UNIT_MONGOL_KESHIK` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Units/CIV4UnitInfos.xml:16363-16556); buildings `BUILDING_MONGOL_GER` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Buildings/CIV4BuildingInfos.xml:3162-3333), `BUILDING_MONGOLIAN_PALACE` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Buildings/CIV4BuildingInfos.xml:1080-1255).

### 18. `LEADER_SITTING_BULL` — `CIVILIZATION_NATIVE_AMERICA`

- **Tier:** Targeted differentiation
- **Current trait:** TRAIT_SITTING_BULL: +2 health and live TradeYieldModifiers of +150%, -500%, -500% across the three yield slots.
- **Personality theme:** Peace-weight 8, military 5/growth 2, Environmentalism; defensive-peaceful profile but 35% unit build and some razing.
- **UU/UB/replacement package:** Strength-4 Dog Soldier gets +100% versus melee; Totem adds 3 Archer XP and a trade route.
- **Palace/improvement/DLL dependency:** Extended trait trade-yield array; no palace/improvement.
- **Current strengths:** Defensive denial, health and archer development offer a recognizable survival identity.
- **Overlap/redundancy:** Personality overlaps Geronimo; extreme negative trade-yield values look like a brittle exploit/penalty rather than legible differentiation.
- **Historical fit:** Coalition leadership and resistance to encroachment fit a defensive diplomatic leader better than punitive abstract trade conversion.
- **AI/art risks:** Stock unit/leader art is low risk. Extreme modifiers need runtime tooltip/economic tests; AI may not understand the penalty.
- **Design input:** Replace the extreme trade array with one transparent defensive/diplomatic effect while preserving Dog Soldier and Totem.
- **Historical research:** [https://www.britannica.com/biography/Sitting-Bull](https://www.britannica.com/biography/Sitting-Bull)
- **Live evidence:** leader `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Civilizations/CIV4LeaderHeadInfos.xml:24242-24783`; trait `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Civilizations/CIV4TraitInfos.xml:2591-2630`; units `UNIT_NATIVE_AMERICA_DOG_SOLDIER` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Units/CIV4UnitInfos.xml:8723-8911); buildings `BUILDING_NATIVE_AMERICA_TOTEM` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Buildings/CIV4BuildingInfos.xml:9767-9946).

### 19. `LEADER_WILLEM_VAN_ORANJE` — `CIVILIZATION_NETHERLANDS`

- **Tier:** Keep
- **Current trait:** TRAIT_ORANGE: extra-yield threshold 4 and +100% trade yield.
- **Personality theme:** Peace-weight 4, gold 5/science 2, Free Religion; balanced, trade-friendly and moderately cautious.
- **UU/UB/replacement package:** Oostindievaarder is a stronger rival-territory Galleon with trade mission values; Dike adds production to sea plots; Orange Lighthouse adds two trade routes and +50% trade route yield.
- **Palace/improvement/DLL dependency:** Building sea-plot yield and unit trade mission fields use existing DLL/XML behavior; no palace/improvement.
- **Current strengths:** Exceptionally coherent water, shipping and trade-city package.
- **Overlap/redundancy:** Strong trade overlap with Portugal/Venice, but Dike terrain dependence and Galleon timing distinguish it.
- **Historical fit:** Dutch maritime commerce, water engineering and religious tolerance are well aligned.
- **AI/art risks:** Mostly stock art; custom Lighthouse and trade-capable ship require pedia/AI checks. Gold/science AI supports the package.
- **Design input:** No redesign.
- **Historical research:** No change recommendation; live package retained.
- **Live evidence:** leader `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Civilizations/CIV4LeaderHeadInfos.xml:28727-29293`; trait `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Civilizations/CIV4TraitInfos.xml:558-597`; units `UNIT_NETHERLANDS_OOSTINDIEVAARDER` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Units/CIV4UnitInfos.xml:22518-22702); buildings `BUILDING_NETHERLANDS_DIKE` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Buildings/CIV4BuildingInfos.xml:18892-19059), `BUILDING_ORANGE_LIGHTHOUSE` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Buildings/CIV4BuildingInfos.xml:5419-5584).

### 20. `LEADER_CHINESE_LEADER` — `CIVILIZATION_PEOPLES_REPUBLIC_CHINA`

- **Tier:** Targeted differentiation
- **Current trait:** TRAIT_MAO_MASS_LINE: -15% upkeep, Great General bonuses, production threshold, Golden Age production, flat commerce and modifier bonuses, Workshop production, Farm espionage, and Spy espionage.
- **Personality theme:** Peace-weight 1; production 6/growth 4/military 6/espionage 5; State Property; aggressive limited-war planner with high espionage.
- **UU/UB/replacement package:** People's Volunteer Infantry is cheaper but weaker, with Drill/Guerilla, city/hill/withdrawal bonuses; Danwei Committee Courthouse adds production, commerce/espionage, defense and war-weariness relief.
- **Palace/improvement/DLL dependency:** Trait uses several extended DLL channels, including worked-improvement city commerce.
- **Current strengths:** Mass mobilization, cheaper infantry, workplace organization and state administration are mechanically integrated.
- **Overlap/redundancy:** Trait and Danwei both stack production, espionage and administration; the package is much denser than comparable modern leaders.
- **Historical fit:** Mass line, rural mobilization and danwei organization are historically legible, but should not become an undifferentiated bundle of every state bonus.
- **AI/art risks:** Custom unit/building art and worked-improvement tooltip need validation. AI flavors are unusually well aligned but cumulative power remains uncertain.
- **Design input:** Retain the volunteer/danwei core and reduce one duplicated trait channel after numerical comparison.
- **Historical research:** [https://www.britannica.com/biography/Mao-Zedong](https://www.britannica.com/biography/Mao-Zedong)
- **Live evidence:** leader `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Civilizations/CIV4LeaderHeadInfos.xml:16565-17119`; trait `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Civilizations/CIV4TraitInfos.xml:434-518`; units `UNIT_PRC_PEOPLES_VOLUNTEER` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Units/CIV4UnitInfos.xml:12578-12779); buildings `BUILDING_PRC_DANWEI_COMMITTEE` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Buildings/CIV4BuildingInfos.xml:17233-17441).

### 21. `LEADER_PETER` — `CIVILIZATION_PETRINE_RUSSIA`

- **Tier:** Keep
- **Current trait:** TRAIT_PETER: +25% Great People rate; Libraries/Universities and Spies gain small commerce bonuses.
- **Personality theme:** Peace-weight 1, science 6/espionage 4/culture 2/growth 1, Bureaucracy; expansionist, science/espionage-forward and moderately militarized.
- **UU/UB/replacement package:** No UU. Admiralty Harbor adds trade, culture/research and a trade route; Collegium Courthouse adds research/espionage, modifiers and two specialist slots.
- **Palace/improvement/DLL dependency:** No palace/improvement; intentionally building-led package.
- **Current strengths:** Modernization, maritime development, bureaucracy and knowledge transfer are sharply expressed without another Russian cavalry unit.
- **Overlap/redundancy:** No-UU shape differs from most packages but avoids Russian cavalry redundancy.
- **Historical fit:** Admiralty and collegial administration fit Petrine reform.
- **AI/art risks:** Custom buildings need art/help closure; AI science/espionage flavors use them. No unit-art risk.
- **Design input:** No redesign; keep the deliberate no-UU structure.
- **Historical research:** No change recommendation; live package retained.
- **Live evidence:** leader `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Civilizations/CIV4LeaderHeadInfos.xml:19871-20436`; trait `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Civilizations/CIV4TraitInfos.xml:2512-2591`; units none; buildings `BUILDING_PETER_ADMIRALTY` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Buildings/CIV4BuildingInfos.xml:5777-5986), `BUILDING_PETER_COLLEGIUM_OF_FOREIGN_AFFAIRS` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Buildings/CIV4BuildingInfos.xml:16601-16814).

### 22. `LEADER_CASIMIR` — `CIVILIZATION_POLAND`

- **Tier:** Polish
- **Current trait:** TRAIT_CASIMIR: +2 happiness and a flat culture-channel bonus.
- **Personality theme:** Peace-weight 8, growth 6/culture 3/religion 2, Bureaucracy; peaceful builder and non-razing diplomat.
- **UU/UB/replacement package:** Polish Dragoon loses one strength but gains collateral damage; Royal Castle gives mounted XP and small Great General bonuses.
- **Palace/improvement/DLL dependency:** No palace/improvement; standard XML combat/building channels.
- **Current strengths:** Peaceful domestic identity paired with a bounded mounted military reserve.
- **Overlap/redundancy:** Trait is generic and thin; Dragoon/castle military focus does not fully express the AI's growth, law and culture themes.
- **Historical fit:** Casimir III's diplomacy, legal codification, towns and Kraków university support a civic-development identity.
- **AI/art risks:** Custom Dragoon/coat art must be animated in-game; AI may undervalue collateral cavalry. Passive trait is safe.
- **Design input:** Keep the package; improve text/AI framing first, and only later consider one small civic-development adjustment.
- **Historical research:** [https://www.britannica.com/biography/Casimir-III](https://www.britannica.com/biography/Casimir-III)
- **Live evidence:** leader `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Civilizations/CIV4LeaderHeadInfos.xml:30959-31535`; trait `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Civilizations/CIV4TraitInfos.xml:2630-2669`; units `UNIT_POLISH_DRAGOON` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Units/CIV4UnitInfos.xml:17954-18146); buildings `BUILDING_POLISH_ROYAL_CASTLE` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Buildings/CIV4BuildingInfos.xml:2385-2587).

### 23. `LEADER_SALAMASINA_BTG` — `CIVILIZATION_POLYNESIA_BTG`

- **Tier:** Polish
- **Current trait:** TRAIT_SALAMASINA_BTG: +5 health, +3 happiness and Navigation I to naval units.
- **Personality theme:** Peace-weight 9, culture 5/religion 2, Organized Religion; very peaceful, low unit production and no razing.
- **UU/UB/replacement package:** Three-move Ocean Canoe; Wayfinder Workboat can build fishing, whaling, offshore and Polynesian Reef Works improvements; Marae gives sea plots +1 commerce.
- **Palace/improvement/DLL dependency:** Unique Reef Works worker action/improvement is a complete custom build/art/AI contract; trait uses naval promotion tables.
- **Current strengths:** Excellent seafaring, ocean development and ceremonial/community package.
- **Overlap/redundancy:** Large unconditional health/happiness is generic and may overshadow the more distinctive navigation/reef system.
- **Historical fit:** Genealogical authority and Samoan political unification support a culture/legitimacy theme; ocean navigation belongs to the broader Polynesian package.
- **AI/art risks:** Highest art/AI risk among otherwise polished packages: workboat actions, reef placement, model state, persistence and AI use all require live tests.
- **Design input:** Do not redesign. Verify the existing reef vertical slice and consider conservative trait tuning only after autoplay.
- **Historical research:** [George Turner, *Samoa, a Hundred Years Ago and Long Before* (1884), digitized by Internet Archive](https://archive.org/details/samoaahundredye00turngoog)
- **Live evidence:** leader `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Civilizations/CIV4LeaderHeadInfos.xml:23157-23700`; trait `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Civilizations/CIV4TraitInfos.xml:2716-2765`; units `UNIT_POLYNESIA_OCEAN_CANOE_BTG` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Units/CIV4UnitInfos.xml:29306-29482), `UNIT_POLYNESIA_WAYFINDER_WORKBOAT_BTG` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Units/CIV4UnitInfos.xml:29120-29305); buildings `BUILDING_POLYNESIA_MARAE_BTG` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Buildings/CIV4BuildingInfos.xml:39095-39281).

### 24. `LEADER_JOAO` — `CIVILIZATION_PORTUGAL`

- **Tier:** Keep
- **Current trait:** TRAIT_JOAO: custom Joao promotion to naval units.
- **Personality theme:** Peace-weight 6, science 5/military 2, Hereditary Rule; peaceful explorer with moderate naval/military interest.
- **UU/UB/replacement package:** Carrack carries four, supports settler/assault AI and bombards; three-move Scout has Mobility/Sentry and extreme animal combat; Feitoria adds sea-plot commerce.
- **Palace/improvement/DLL dependency:** Building sea-plot yield and custom naval promotion; no palace/improvement.
- **Current strengths:** Exploration, overseas settlement and maritime commerce are clear and highly playable.
- **Overlap/redundancy:** Some overlap with Willem/Elizabeth, but fast scouting and transport capacity distinguish Portugal.
- **Historical fit:** Portuguese oceanic expansion and feitoria trade network fit strongly.
- **AI/art risks:** Mostly stock Carrack/Feitoria art; custom Scout group needs animation checks. Settler-sea AI is present.
- **Design input:** No redesign.
- **Historical research:** No change recommendation; live package retained.
- **Live evidence:** leader `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Civilizations/CIV4LeaderHeadInfos.xml:12743-13293`; trait `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Civilizations/CIV4TraitInfos.xml:918-967`; units `UNIT_PORTUGAL_CARRACK` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Units/CIV4UnitInfos.xml:22128-22336), `UNIT_JOAO_SCOUT` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Units/CIV4UnitInfos.xml:2324-2504); buildings `BUILDING_PORTUGAL_FEITORIA` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Buildings/CIV4BuildingInfos.xml:6339-6509).

### 25. `LEADER_QIN_SHI_HUANG` — `CIVILIZATION_QIN_DYNASTY`

- **Tier:** Keep
- **Current trait:** TRAIT_QIN_SHI_HUANG: +100% domestic Great General rate; City Garrison I/II and Drill I to archery and gun units.
- **Personality theme:** Peace-weight 2, production 5/growth 2, Bureaucracy; cautious about major war but authoritarian and defensive.
- **UU/UB/replacement package:** Cho-Ko-Nu has two first strikes and collateral; Pavilion Theatre adds +25% culture.
- **Palace/improvement/DLL dependency:** Free-promotion trait tables use existing DLL support; no palace/improvement.
- **Current strengths:** Strong fortified-state, mass construction and ranged-army identity.
- **Overlap/redundancy:** Defensive promotion overlap with Churchill/Tokugawa, but collateral crossbows and production AI differentiate it.
- **Historical fit:** Centralization, fortification and standardization are plausible Qin themes.
- **AI/art risks:** Stock art and normal unit AI are low risk; promotion stacking needs ordinary balance testing.
- **Design input:** No redesign.
- **Historical research:** No change recommendation; live package retained.
- **Live evidence:** leader `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Civilizations/CIV4LeaderHeadInfos.xml:20437-20974`; trait `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Civilizations/CIV4TraitInfos.xml:1187-1248`; units `UNIT_CHINA_CHOKONU` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Units/CIV4UnitInfos.xml:15195-15391); buildings `BUILDING_CHINESE_PAVILLION` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Buildings/CIV4BuildingInfos.xml:12563-12755).

### 26. `LEADER_ISABELLA` — `CIVILIZATION_SPAIN`

- **Tier:** Keep
- **Current trait:** TRAIT_ISABELLA: Morale to mounted and naval units.
- **Personality theme:** Peace-weight 6, religion flavor 10, Theocracy; religiously polarized, moderately warlike and willing to raze.
- **UU/UB/replacement package:** Conquistador gains +50% versus melee; Citadel grants 5 siege XP.
- **Palace/improvement/DLL dependency:** Custom promotion distribution; no palace/improvement.
- **Current strengths:** Compact religious-expansion and combined mounted/naval identity.
- **Overlap/redundancy:** Mounted overlap is common, but naval Morale and siege Citadel provide breadth.
- **Historical fit:** Theocracy and overseas conquest fit, though later text should avoid reducing Isabella solely to religious warfare.
- **AI/art risks:** Stock art and standard combat channels are low risk. Religion flavor 10 can dominate diplomacy by design.
- **Design input:** No redesign.
- **Historical research:** No change recommendation; live package retained.
- **Live evidence:** leader `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Civilizations/CIV4LeaderHeadInfos.xml:12189-12742`; trait `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Civilizations/CIV4TraitInfos.xml:2264-2317`; units `UNIT_SPANISH_CONQUISTADOR` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Units/CIV4UnitInfos.xml:17333-17548); buildings `BUILDING_SPANISH_CITADEL` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Buildings/CIV4BuildingInfos.xml:2178-2384).

### 27. `LEADER_STALIN` — `CIVILIZATION_USSR`

- **Tier:** Major redesign
- **Current trait:** TRAIT_STALIN: -2 happiness and a flat +50 commerce-channel value.
- **Personality theme:** Peace-weight 2, military 5/production 2, State Property; aggressive, espionage weight 150, high unit production and some razing.
- **UU/UB/replacement package:** Cossack; 5-cost two-move Spy with Mobility/Sentry; Research Institute adds two free Scientists; 10-cost USSR Monument allows 100 Spy slots and +10 durable commerce; Lubyanka adds +50 commerce and +5 happiness.
- **Palace/improvement/DLL dependency:** No unique improvement/palace, but espionage/specialist quantities depend on synchronized XML/DLL interpretation.
- **Current strengths:** Production, research and secret-police identity is unmistakable.
- **Overlap/redundancy:** Numbers are outliers: +50 trait commerce, 100 Spy slots, 5-cost Spy, +5 happiness Lubyanka and multiple research/espionage buildings erase normal constraints.
- **Historical fit:** Forced industrialization, centralized rule and political repression are relevant; large happiness and unconstrained spy capacity invert the historical human cost.
- **AI/art risks:** Custom Spy/monument/Lubyanka art needs closure. Extreme specialist and commerce values can distort AI valuation, UI, saves and economy.
- **Design input:** Rebuild around one production/research strength and one explicit coercion cost; retain recognizable names but rebudget every component together.
- **Historical research:** [https://www.britannica.com/biography/Joseph-Stalin](https://www.britannica.com/biography/Joseph-Stalin)
- **Live evidence:** leader `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Civilizations/CIV4LeaderHeadInfos.xml:24784-25341`; trait `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Civilizations/CIV4TraitInfos.xml:801-840`; units `UNIT_RUSSIA_COSSACK` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Units/CIV4UnitInfos.xml:18345-18547), `UNIT_RUSSIA_SPY` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Units/CIV4UnitInfos.xml:2859-3044); buildings `BUILDING_RUSSIAN_RESEARCH_INSTITUTE` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Buildings/CIV4BuildingInfos.xml:12174-12353), `BUILDING_USSR_MONUMENT` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Buildings/CIV4BuildingInfos.xml:9025-9196), `BUILDING_LUBYANKA` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Buildings/CIV4BuildingInfos.xml:26988-27159).

### 28. `LEADER_ENRICO_DANDOLO` — `CIVILIZATION_VENICE`

- **Tier:** Keep
- **Current trait:** TRAIT_DANDOLO: +100% civic upkeep.
- **Personality theme:** Peace-weight 8, growth 6/culture 3/religion 2, Caste System; peaceful builder personality identical to Casimir's key fields.
- **UU/UB/replacement package:** Founder is functionally the default Settler; Venetian Merchant combines founding, roads, Grand Colosseum build, trade mission, great work and 1000 work rate; Doge Palace gives +6 trade routes, +50% domestic/foreign trade, +15 happiness, +30 health and +4 Great People.
- **Palace/improvement/DLL dependency:** Unique Palace and a multi-role Great Merchant/worker/founder unit; several unusual DLL/UI action paths.
- **Current strengths:** Venetian trade and merchant-government identity is immediately visible.
- **Overlap/redundancy:** User-directed preservation: the unusual founder, multi-role merchant, Palace, trait and personality are the package's intended identity.
- **Historical fit:** The package intentionally emphasizes Venice's exceptional merchant government and Enrico Dandolo's outsized role.
- **AI/art risks:** Regression-only after the user-directed Keep decision; preserve all existing actions and art, then smoke the complete package.
- **Design input:** No redesign.
- **Historical research:** [https://www.britannica.com/biography/Enrico-Dandolo](https://www.britannica.com/biography/Enrico-Dandolo)
- **Live evidence:** leader `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Civilizations/CIV4LeaderHeadInfos.xml:31536-32112`; trait `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Civilizations/CIV4TraitInfos.xml:2669-2708`; units `UNIT_VENICE_FOUNDER` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Units/CIV4UnitInfos.xml:918-1092), `UNIT_VENETIAN_MERCHANT` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Units/CIV4UnitInfos.xml:27645-27875); buildings `BUILDING_VENETIAN_DOGE_PALACE` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Buildings/CIV4BuildingInfos.xml:179-348).

### 29. `LEADER_RAGNAR` — `CIVILIZATION_VIKING`

- **Tier:** Keep
- **Current trait:** TRAIT_RAGNAR: Pillage I to melee and naval units.
- **Personality theme:** Peace-weight 0, military flavor 10, Hereditary Rule; extremely aggressive, 40% unit build and 50% razing.
- **UU/UB/replacement package:** Berserker has Amphibious/Pillage I and city attack; unique Swordsman/Axeman also gain Pillage I; Trading Post grants Navigation I to ships.
- **Palace/improvement/DLL dependency:** Custom promotion but no palace/improvement.
- **Current strengths:** A direct, legible amphibious raiding progression across land and sea.
- **Overlap/redundancy:** Extreme warmonger overlap with Genghis/Shaka/Montezuma, but amphibious and naval progression distinguishes Ragnar.
- **Historical fit:** Viking-Age raiding and ship mobility fit the intended semi-legendary leader archetype.
- **AI/art risks:** Mostly stock art; additional Viking unit art needs normal animation checks. AI military profile is aligned.
- **Design input:** No redesign.
- **Historical research:** No change recommendation; live package retained.
- **Live evidence:** leader `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Civilizations/CIV4LeaderHeadInfos.xml:21524-22064`; trait `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Civilizations/CIV4TraitInfos.xml:2317-2370`; units `UNIT_VIKING_BESERKER` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Units/CIV4UnitInfos.xml:9320-9534), `UNIT_VIKING_SWORDSMAN` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Units/CIV4UnitInfos.xml:7173-7361), `UNIT_VIKING_AXEMAN` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Units/CIV4UnitInfos.xml:8131-8329); buildings `BUILDING_VIKING_TRADING_POST` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Buildings/CIV4BuildingInfos.xml:5250-5418).

### 30. `LEADER_CHURCHILL` — `CIVILIZATION_WARTIME_BRITAIN`

- **Tier:** Targeted differentiation
- **Current trait:** TRAIT_CHURCHILL: +3 happiness, -25% XP threshold, Spy +1 espionage; City Garrison I/II and Drill I to archery/gun units.
- **Personality theme:** Peace-weight 6, military 5/gold 2, Nationhood; defensive, no razing and moderately reluctant to war.
- **UU/UB/replacement package:** Fighter Command is stronger/cheaper with Interception I; War Rooms replaces Bank with espionage, spy slots, war-weariness relief and 75% gold; MI6 replaces Scotland Yard with 200% espionage and two free Spies.
- **Palace/improvement/DLL dependency:** No palace/improvement; specialist/commerce and promotion tables use existing DLL support.
- **Current strengths:** Excellent air defense, national resilience and intelligence identity.
- **Overlap/redundancy:** War Rooms and MI6 double-stack espionage while the Bank replacement also improves gold; defensive promotions overlap Qin/Tokugawa.
- **Historical fit:** Wartime coordination, fighter defense and intelligence fit Churchill, but MI6's institutional identity extends beyond his personal wartime leadership.
- **AI/art risks:** Custom fighter/building art and heavy espionage UI require smoke tests. Military/gold flavors do not include espionage despite two espionage UBs.
- **Design input:** Keep Fighter Command and War Rooms; normalize MI6 or the duplicated espionage channel and align AI flavor/weight.
- **Historical research:** [https://www.britannica.com/biography/Winston-Churchill](https://www.britannica.com/biography/Winston-Churchill)
- **Live evidence:** leader `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Civilizations/CIV4LeaderHeadInfos.xml:4557-5107`; trait `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Civilizations/CIV4TraitInfos.xml:1596-1668`; units `UNIT_BRITISH_FIGHTER_COMMAND` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Units/CIV4UnitInfos.xml:25491-25671); buildings `BUILDING_BRITISH_WAR_ROOMS` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Buildings/CIV4BuildingInfos.xml:19237-19413), `BUILDING_BRITISH_MI6` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Buildings/CIV4BuildingInfos.xml:26811-26987).

### 31. `LEADER_KUBLAI_KHAN` — `CIVILIZATION_YUAN_DYNASTY`

- **Tier:** Targeted differentiation
- **Current trait:** TRAIT_KUBLAI: flat commerce bonuses plus +1 production from Road and Railroad routes.
- **Personality theme:** Peace-weight 1, military 5/culture 2, Bureaucracy; aggressive but lower razing, with Buddhist preference.
- **UU/UB/replacement package:** Qianhu Cavalry ignores terrain, has first strike, withdrawal, city/siege bonuses; Ortoo Hub Stable adds commerce/trade route but less XP; shares the Mongolian Great Palace with Genghis.
- **Palace/improvement/DLL dependency:** Shared unique Great Palace; route-yield trait uses the extended DLL table.
- **Current strengths:** Road logistics, postal/trade hub and culturally oriented conquest are a strong Yuan identity.
- **Overlap/redundancy:** Shared Palace blurs Genghis/Kublai; mounted package still closely parallels Keshik/Ger.
- **Historical fit:** Kublai's Yuan state, China-wide rule and transcontinental administration support route, culture and bureaucracy themes.
- **AI/art risks:** Custom cavalry/hub art needs closure; AI values military/culture but may not optimize route yields. Shared Palace makes independent balancing harder.
- **Design input:** Retain Qianhu/Ortoo logistics and replace or specialize the shared Palace so Yuan administration, not generic Mongol horse supply, is the capstone.
- **Historical research:** [https://www.britannica.com/biography/Kublai-Khan](https://www.britannica.com/biography/Kublai-Khan)
- **Live evidence:** leader `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Civilizations/CIV4LeaderHeadInfos.xml:14378-14924`; trait `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Civilizations/CIV4TraitInfos.xml:2083-2140`; units `UNIT_YUAN_QIANHU_CAVALRY` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Units/CIV4UnitInfos.xml:16557-16755); buildings `BUILDING_YUAN_ORTOO_HUB` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Buildings/CIV4BuildingInfos.xml:3334-3510), `BUILDING_MONGOLIAN_PALACE` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Buildings/CIV4BuildingInfos.xml:1080-1255).

### 32. `LEADER_SHAKA` — `CIVILIZATION_ZULU`

- **Tier:** Keep
- **Current trait:** TRAIT_SHAKA: -50% XP threshold, +100% Great General rates; Pinch and Flanking I to melee and gun units.
- **Personality theme:** Peace-weight 2, military flavor 10, Police State; extremely frequent war, 40% unit build and 50% razing.
- **UU/UB/replacement package:** Two-move Mobility Impi; Ikhanda Barracks adds -20% maintenance.
- **Palace/improvement/DLL dependency:** Promotion tables use existing DLL support; no palace/improvement.
- **Current strengths:** Compact, powerful military expansion package with a real economic enabler.
- **Overlap/redundancy:** Warmonger overlap is inevitable, but fast spear plus maintenance Barracks is unique.
- **Historical fit:** Regimental warfare and centralized military expansion fit the Shakan package.
- **AI/art risks:** Stock art and highly aligned AI are low risk; promotion stack requires balance testing only.
- **Design input:** No redesign.
- **Historical research:** No change recommendation; live package retained.
- **Live evidence:** leader `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Civilizations/CIV4LeaderHeadInfos.xml:23701-24241`; trait `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Civilizations/CIV4TraitInfos.xml:2927-2984`; units `UNIT_ZULU_IMPI` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Units/CIV4UnitInfos.xml:9725-9923); buildings `BUILDING_ZULU_IKHANDA` (CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Buildings/CIV4BuildingInfos.xml:2809-2984).

## Cross-roster conclusions

1. Preserve the sixteen `Keep` packages. Their remaining need is comparative
   balance and runtime validation, not new mechanics.
2. Treat Washington, Elizabeth, Hammurabi, Genghis, Sitting Bull, Wang Kon,
   Asoka, Mao, Churchill, and Kublai as bounded package slices; do not turn
   their findings into shared-system refactors.
3. Give Stalin a separate design record before editing. Preserve Dandolo and
   Venice exactly as directed by the user.
4. Reuse no new DLL mechanic until existing extended trait/building channels
   have tooltip, AI valuation, save/load, and deterministic MP evidence.
5. Salamasina's Reef Works and Elizabeth's multi-class Sea Dog require
   contract validation even if their numeric design is otherwise retained.

## Validation and limitations

- Parsed the baseline and asserted exactly 32 unique target leaders.
- Parsed live XML and resolved every target trait, leader, unit, and building.
- Embedded exact live XML line ranges in the machine-readable matrix.
- Validated the matrix schema/count/tier vocabulary and Markdown coverage.
- Historical URLs were checked where the provider permitted automated access;
  some institutional sites may block automated clients.
- No game launch, art render, AI autoplay, save/load, or multiplayer test was
  run because this todo is research-only. Those remain implementation gates.

## Machine-readable handoff

The canonical next-todo input is
`tools/baselines/remaining_roster_audit_matrix.json`. It includes current
mappings, personality values, flavors, tier, assessment fields, historical
links, and path/line evidence for every package.
