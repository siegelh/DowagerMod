# DowagerMod: New Quest Proposals

**Date**: 2026-06-19  
**Status**: Proposal (no implementation yet)  
**Branch**: TBD (worktree off agent-baseline-leader-chatter)

---

## How BtS Quests Work (Reference)

Each quest consists of:
1. **Start Trigger** (`EVENTTRIGGER_*`) — conditions for the quest to appear
2. **Start Event** (`EVENT_*`) — what happens when it fires (flavor text, initial setup)
3. **Done Trigger** (`EVENTTRIGGER_*_DONE`) — conditions for completion (chains via `PrereqEvents`)
4. **Done Event** (`EVENT_*_DONE_*`) — reward choices (1–3 options)

**Key trigger fields**: `OrPreReqs` (tech), `BuildingsRequired`, `UnitsRequired`, `iNumBuildings/Units/UnitsGlobal`, `iMinTreasury`, `Civic`, `bStateReligion`, `bPickPlayer`, `iOtherPlayerShareBorders`, `BonusesRequired`, `iPercentGamesActive`, `iWeight`, `PythonCanDo`

**Reward mechanisms in events**: gold, units, buildings, happiness, health, culture, commerce, Great People, techs, promotions, temporary modifiers

**Era constants**: Ancient=0, Classical=1, Medieval=2, Renaissance=3, Industrial=4, Modern=5, Future=6

---

## Existing Vanilla Quests (18 total)

| # | Quest | Era Gate | Theme |
|---|-------|----------|-------|
| 1 | Blessed Sea | Classical+ | Naval expansion |
| 2 | Holy Mountain | Ancient+ | Religious pilgrimage |
| 3 | Horse Whispering | Ancient | Mounted units |
| 4 | Harbormaster | Classical+ | Coastal trade |
| 5 | Classic Literature | Classical+ | Culture/writing |
| 6 | Master Blacksmith | Classical+ | Production/forges |
| 7 | Best Defense | Medieval+ | Defensive buildup |
| 8 | National Sports League | Industrial+ | Happiness/stadiums |
| 9 | Crusade | Medieval | Holy war |
| 10 | Greed | Any (Bronze Working) | Commerce/gold |
| 11 | War Chariots | Ancient | Mounted military |
| 12 | Elite Swordsmen | Classical | Melee combat |
| 13 | Warships | Renaissance+ | Naval military |
| 14 | Guns, Not Butter | Industrial+ | Military vs economy |
| 15 | Noble Knights | Medieval | Chivalry/cavalry |
| 16 | Overwhelm Doctrine | Modern | Military overmatch |
| 17 | Corporate Expansion | Industrial+ | Corporation spread |
| 18 | Hostile Takeover | Industrial+ | Economic sabotage |

---

## New Quest Proposals

### ANCIENT ERA (Bronze Working – Alphabet)

#### 1. Blood and Iron
- **Prereq**: Bronze Working + 4 Melee units
- **Objective**: Build 6 Axemen/Swordsmen
- **Reward choices**: All melee get Combat I free / +25% production toward melee / Free Bronze resource appears near capital
- **Weight**: 200 / 30% of games
- **Rationale**: Fills a gap — existing ancient quests focus on horses/chariots but not foot soldiers

#### 2. River Valley
- **Prereq**: Agriculture + city on river + 3 farms
- **Objective**: Build 5 farms on river tiles
- **Reward choices**: +1 food on all river tiles for this city / Free Granary / +2 health in river cities
- **Weight**: 250 / 40% of games
- **Rationale**: Thematic for early agrarian civilizations; river mechanics underused in quests

#### 3. Tribal Confederation
- **Prereq**: 3+ cities + no contact with other civs yet
- **Objective**: Grow total population to 15 within 20 turns
- **Reward choices**: Free Settler / +1 pop in all cities / Free Monument in all cities
- **Weight**: 150 / 25% of games
- **Rationale**: Rewards early expansion before meeting rivals; interesting isolation mechanic

#### 4. Stone Circles
- **Prereq**: Mysticism + city adjacent to 2+ hills/peaks
- **Objective**: Build Monument and Temple in that city
- **Reward choices**: +4 culture per turn in that city / Free Great Prophet points / City never loses religion
- **Weight**: 200 / 35% of games
- **Rationale**: Gives religious/cultural players an early quest; terrain-specific makes it interesting

---

### CLASSICAL ERA (Math – Construction – Currency)

#### 5. Bread Basket
- **Prereq**: Currency + Granary in 3 cities + total pop ≥ 20
- **Objective**: Build Granaries in all cities (min 5)
- **Reward choices**: +1 food in all cities / Free Aqueduct in capital / Population boom (+1 in each city)
- **Weight**: 200 / 40% of games
- **Rationale**: Food infrastructure rewarded; parallel to how Master Blacksmith rewards forges

#### 6. Road Network
- **Prereq**: Construction + 5 cities + roads connecting at least 4
- **Objective**: Connect all cities with roads within 15 turns
- **Reward choices**: +1 commerce on all roads / Free trade route in all cities / Workers move +1
- **Weight**: 250 / 45% of games
- **Rationale**: Infrastructure building — surprisingly no vanilla quest rewards road building

#### 7. Arena Games
- **Prereq**: Construction + Colosseum + 3 military units in city
- **Objective**: Win 3 combat victories within 15 turns
- **Reward choices**: +2 happiness from Colosseums / Units in that city get +2 XP / Free Gladiator unit
- **Weight**: 180 / 30% of games
- **Rationale**: Combines military action with buildings; fun flavor

#### 8. Foreign Traders
- **Prereq**: Currency + contact with 2+ civs + Open Borders with 1
- **Objective**: Accumulate 500 gold in treasury
- **Reward choices**: +2 gold per trade route / Free Great Merchant / Rival shares map
- **Weight**: 200 / 35% of games
- **Rationale**: Rewards diplomatic/economic play in classical era

---

### MEDIEVAL ERA (Feudalism – Guilds – Theology)

#### 9. Cathedral Builders
- **Prereq**: Theology + State Religion + 4 cities with that religion
- **Objective**: Build Cathedrals/Monasteries in 4 cities
- **Reward choices**: +3 culture from religious buildings / Free Great Artist / Double religion spread rate
- **Weight**: 200 / 40% of games
- **Rationale**: Religious building chain quest; complements Crusade's military religion focus

#### 10. Feudal Levy
- **Prereq**: Feudalism + 6 cities + Hereditary Rule civic
- **Objective**: Train 8 military units within 20 turns
- **Reward choices**: Units start with Combat I / +25% military production / Free Great General
- **Weight**: 180 / 35% of games
- **Rationale**: Civic-specific quest adds weight to civic choice decisions

#### 11. Merchant Guild
- **Prereq**: Guilds + Market in 3 cities + 750 gold
- **Objective**: Build Markets in 6 cities
- **Reward choices**: +25% gold in all cities for 30 turns / Free Bank in capital / Great Merchant born
- **Weight**: 220 / 40% of games
- **Rationale**: Economy-focused; Guilds tech feels underrepresented in events

#### 12. Plague Doctor
- **Prereq**: 3+ cities with negative health + Medicine NOT yet discovered
- **Objective**: Build Aqueduct in 3 unhealthy cities within 15 turns
- **Reward choices**: +2 health empire-wide / Free Hospital when Medicine discovered / Remove unhealthiness penalty
- **Weight**: 250 / 50% of games
- **Rationale**: Turns a common problem (unhealthy cities) into an engaging challenge

#### 13. Fortification
- **Prereq**: Engineering + borders with rival + 2+ border cities without Walls
- **Objective**: Build Walls/Castles in 4 border cities
- **Reward choices**: +50% defense in border cities / Free Castle in capital / Walls free in all cities
- **Weight**: 180 / 35% of games
- **Rationale**: Defensive infrastructure quest; complements the offensive Best Defense quest

---

### RENAISSANCE ERA (Gunpowder – Astronomy – Economics)

#### 14. Cannon Foundry
- **Prereq**: Gunpowder + Forge in 2 cities + Iron
- **Objective**: Build 4 Cannons/Trebuchets
- **Reward choices**: Siege units get +25% vs cities / Free Cannon in capital / +1 movement for siege
- **Weight**: 200 / 35% of games
- **Rationale**: Siege warfare quest; era of gunpowder should have one

#### 15. New World
- **Prereq**: Astronomy + unexplored tiles > 30% of map
- **Objective**: Discover a new landmass (make contact with new continent via Python check)
- **Reward choices**: Free Settler on new continent / +2 trade routes in coastal cities / Reveal all coastline
- **Weight**: 250 / 40% of games
- **Rationale**: Exploration is one of the most exciting parts of the game; finally a quest for it

#### 16. Mercantilism
- **Prereq**: Economics + 5 Markets + running Mercantilism civic
- **Objective**: Maintain 1000+ gold treasury for 15 turns
- **Reward choices**: +1 free specialist in all cities / Free Bank in 3 cities / Great Merchant born
- **Weight**: 180 / 30% of games
- **Rationale**: Another civic-specific quest; rewards committing to a civic

#### 17. Privateers
- **Prereq**: Astronomy + at war + 3 naval units
- **Objective**: Sink 3 enemy ships within 20 turns
- **Reward choices**: Free Privateer fleet (3 units) / +50 gold per ship sunk / Enemy loses trade routes
- **Weight**: 200 / 35% of games
- **Rationale**: Naval warfare in Renaissance; piracy flavor

#### 18. Palace Intrigue
- **Prereq**: Nationalism + Spy unit + rival shares border
- **Objective**: Successfully conduct 2 espionage missions in 15 turns
- **Reward choices**: +50% espionage for 30 turns / See rival's cities / Free Great Spy
- **Weight**: 180 / 30% of games
- **Rationale**: Espionage gets very little quest attention in vanilla

---

### INDUSTRIAL ERA (Railroad – Assembly Line – Radio)

#### 19. Iron Horse
- **Prereq**: Railroad + 5 cities + Coal
- **Objective**: Connect all cities with Railroad within 20 turns
- **Reward choices**: +1 production on all Railroad tiles / Free Factory / +25% trade route yield
- **Weight**: 250 / 45% of games
- **Rationale**: Railroad revolution — one of the biggest real-world infrastructure shifts

#### 20. Mass Production
- **Prereq**: Assembly Line + Factory in 2 cities
- **Objective**: Build Factories in 5 cities
- **Reward choices**: +25% production empire-wide for 20 turns / Free Power Plant / Great Engineer born
- **Weight**: 200 / 40% of games
- **Rationale**: Industrialization parallel to Guns Not Butter but focused on building, not choosing

#### 21. Workers' Revolt
- **Prereq**: 4+ cities with Factories + NOT running Emancipation + unhappy city
- **Objective**: Choose path — switch to Emancipation OR build Jail in 3 cities within 10 turns
- **Switch reward**: No anarchy for this switch + happiness bonus
- **Jail reward**: +2 espionage in all cities + unrest ends
- **Weight**: 200 / 40% of games
- **Rationale**: Forced decision quest; civic pressure mechanic is novel

#### 22. Propaganda Machine
- **Prereq**: Radio + Broadcast Tower in 4 cities
- **Objective**: Build Broadcast Towers in 6 cities
- **Reward choices**: +3 happiness from Broadcast Towers / +50% culture for 20 turns / Enemy culture pressure reduced
- **Weight**: 180 / 35% of games
- **Rationale**: Cultural/media power in industrial age; fills a gap in culture quests at this era

#### 23. Oil Baron
- **Prereq**: Combustion + Oil resource improved
- **Objective**: Control 3+ Oil sources simultaneously for 15 turns
- **Reward choices**: +100% oil yield / Free units requiring oil / Gold income from oil
- **Weight**: 200 / 35% of games
- **Rationale**: Resource control quest; oil is the critical industrial resource

---

### MODERN/FUTURE ERA (Computers – Satellites – Future Tech)

#### 24. Nuclear Deterrence
- **Prereq**: Fission + rival has Manhattan Project or nukes
- **Objective**: Build Manhattan Project + 2 ICBMs within 15 turns
- **Reward choices**: Free SDI in all cities / Rivals won't declare war for 30 turns / Free tech
- **Weight**: 200 / 35% of games
- **Rationale**: Cold War flavor; nuclear strategy is underserved by quests

#### 25. Information Warfare
- **Prereq**: Computers + 3 Spies + rival within 5 tiles
- **Objective**: Conduct 3 successful espionage missions in 20 turns
- **Reward choices**: See entire rival empire / Steal a tech / +100% espionage for 30 turns
- **Weight**: 180 / 30% of games
- **Rationale**: Modern espionage escalation; cyber warfare theme

#### 26. Space Race
- **Prereq**: Satellites + Apollo Program built + rival building spaceship
- **Objective**: Complete 2 spaceship parts before rival completes 1
- **Reward choices**: +50% spaceship production / Free spaceship part / Sabotage rival (they lose 1 part)
- **Weight**: 200 / 30% of games
- **Rationale**: Space victory gets a competitive edge quest

#### 27. Climate Crisis
- **Prereq**: 8+ cities + 5 Factories + no Recycling Centers
- **Objective**: Build Recycling Centers in 4 cities within 15 turns or suffer consequences
- **If solved**: +3 health in all cities / "Green" golden age
- **If failed**: -2 food in all cities / Coastal improvements destroyed
- **Weight**: 250 / 50% of games
- **Rationale**: Modern consequence quest; negative pressure with preparation reward

---

### ANY ERA (era-agnostic, like Greed)

#### 28. Gold Fever
- **Prereq**: Gold/Silver/Gems resource + Mining
- **Objective**: Accumulate 1000 gold without spending for 15 turns
- **Reward choices**: Double yield from precious resources / Free Market in all cities / Great Merchant
- **Weight**: 200 / 35% of games
- **Rationale**: Simple wealth quest; parallel to Greed with different trigger/reward

#### 29. Border Dispute
- **Prereq**: Shared border with rival + both have 3+ cities + culture pressure
- **Objective**: Build culture buildings in 3 border cities OR build 4 military units on border
- **Cultural path reward**: Border pushes +3 culture in border cities
- **Military path reward**: Free units, rival backs down
- **Weight**: 250 / 45% of games
- **Rationale**: Branching quest — choose diplomacy or force. Novel choice mechanic.

#### 30. Famine
- **Prereq**: 2+ cities losing food + no Granary in those cities
- **Objective**: Build Granaries in starving cities within 10 turns
- **Reward choices**: +2 food empire-wide / Free Aqueduct / Bonus health
- **If failed**: Cities lose 1-2 pop
- **Weight**: 250 / 50% of games
- **Rationale**: Urgency quest with failure state; realistic historical pressure

#### 31. Exodus
- **Prereq**: Rival captures one of your cities + you have 3+ remaining cities
- **Objective**: Found or capture a new city within 20 turns
- **Reward choices**: City starts at size 4 / Free buildings in new city / +50% production for 15 turns
- **Weight**: 200 / 40% of games
- **Rationale**: Recovery quest after loss; comeback mechanic is rewarding

#### 32. Warlord's Challenge
- **Prereq**: Heroic Epic built + Great General alive + at war
- **Objective**: Win 5 battles in 10 turns
- **Reward choices**: All units gain +2 XP / Free elite unit / Great General bonus doubled
- **Weight**: 180 / 30% of games
- **Rationale**: Aggressive military quest for warmongers

#### 33. Enlightenment
- **Prereq**: Education + Library + University in same city + 10+ techs discovered
- **Objective**: Generate a Great Scientist within 15 turns
- **Reward choices**: Free Academy / +25% research for 30 turns / Discover a random tech
- **Weight**: 200 / 35% of games
- **Rationale**: Research-focused quest; Great Scientist generation as objective is unique

#### 34. Cultural Renaissance
- **Prereq**: 3 Wonders in empire + Drama or Music
- **Objective**: Generate 3000 total culture across empire in 20 turns
- **Reward choices**: Free Great Artist / Golden Age / Borders expand double speed for 30 turns
- **Weight**: 200 / 35% of games
- **Rationale**: Culture victory enabler; wonders already built → leverage them

#### 35. Deforestation
- **Prereq**: 5+ lumber mills OR 3+ chopped forests in last 20 turns (Python check)
- **Objective**: Plant 3 forests (Forest Preserve) OR build a Park
- **If solved**: +2 health in all cities / +1 commerce on remaining forests
- **If ignored**: -1 health in all cities for 30 turns
- **Weight**: 200 / 40% of games
- **Rationale**: Environmental consequence; penalizes over-chopping without making it game-breaking

#### 36. Distant Shores
- **Prereq**: Astronomy + found city on new continent
- **Objective**: Grow that city to size 5 within 25 turns
- **Reward choices**: +3 trade routes from colony / Free resources revealed nearby / Colony gets free buildings
- **Weight**: 200 / 35% of games
- **Rationale**: Colony development quest; rewards investing in distant cities

#### 37. Diplomatic Summit
- **Prereq**: Contact with 5+ civs + no active wars + United Nations NOT built
- **Objective**: Sign Open Borders with 3 civs within 10 turns
- **Reward choices**: +2 diplomacy with all known civs / Gold bonus from trade / Vote influence
- **Weight**: 200 / 40% of games
- **Rationale**: Diplomatic play finally gets a quest; peaceful players rewarded

#### 38. Mercenary Companies
- **Prereq**: Feudalism + 500 gold + at war
- **Objective**: Immediate choice — pay 300 gold for 3 strong melee units (disband after 15 turns)
- **If yes**: Receive mercenaries
- **If no**: Nothing (quest resolves immediately)
- **Weight**: 200 / 35% of games
- **Rationale**: Quick-fire decision quest; gold-for-power tradeoff with temporal limit

#### 39. Scorched Earth
- **Prereq**: Enemy has pillaged 3+ of your improvements + at war
- **Objective**: Pillage 5 enemy improvements within 15 turns
- **Reward choices**: All improvements immune to pillaging for 20 turns / Free workers / +25% defense
- **Weight**: 200 / 35% of games
- **Rationale**: Revenge/retaliation quest triggered by enemy aggression

#### 40. Succession Crisis
- **Prereq**: Golden Age just ended + 5+ cities (Python checks golden age history)
- **Objective**: Choose an heir philosophy (immediate decision)
- **Militaristic**: +2 XP all units, -1 commerce for 20 turns
- **Economic**: +25% gold, -1 happiness for 20 turns
- **Cultural**: +50% culture, -25% production for 20 turns
- **Weight**: 180 / 30% of games
- **Rationale**: Post-golden-age transition; interesting risk/reward with tradeoffs

---

### NOVEL MECHANICS (require more Python, possibly DLL)

#### 41. Duel of Champions
- **Trigger**: Rival denounces you + both have military units on shared border
- **Mechanic**: Propose a "champion duel" — AI accepts/declines based on relative power. Single unit vs unit simulated combat. Winner gets 200 gold + happiness. Loser gets nothing but no war.
- **Implementation**: Python callback simulates combat, awards gold/happiness via event
- **Rationale**: Flavor mechanic; avoids full war for a grudge

#### 42. Wager
- **Trigger**: Two civs at similar tech count (within 2 techs)
- **Mechanic**: Rival proposes bet — "First to discover [random expensive tech] wins 500 gold." Accept/decline.
- **Implementation**: Python tracks tech discovery, fires done trigger when either discovers it
- **Rationale**: Fun gamble mechanic; creates tension around tech race

#### 43. World Fair
- **Trigger**: Industrial Era + 5+ known civs + all at peace
- **Mechanic**: All civs contribute hammers toward a shared pool for 10 turns. Top contributor gets choice of: Free tech, Golden Age, or world wonder. Others get consolation prizes.
- **Implementation**: Would need Python to track contributions and rank; most complex quest here
- **Rationale**: Cooperative/competitive hybrid; interesting multiplayer dynamics

#### 44. Prophecy
- **Trigger**: Random, once per game, after Classical Era begins
- **Mechanic**: "A great calamity will strike in 30 turns." Player can spend gold/production preparing (building walls, granaries, military). Severity inversely proportional to preparation level.
- **Outcomes**: Barbarian invasion / Plague / Earthquake / Volcanic eruption (random)
- **Implementation**: Python countdown + preparation scoring + scaled negative event
- **Rationale**: Creates interesting tension and forward planning; unique in quest landscape

#### 45. Trade Embargo
- **Trigger**: You're trading with a civ that another rival has negative relations with
- **Mechanic**: Rival demands you stop trading with their enemy. Comply = +diplomacy with rival, lose trade gold. Refuse = rival relationship drops, keep income.
- **Implementation**: Simple Python check on trade + relationship modifiers
- **Rationale**: Realistic diplomatic pressure; forces interesting relationship decisions

---

## Implementation Priority Tiers

**Tier 1 — Pure XML (easiest, no Python needed)**:
- Blood and Iron, Bread Basket, Iron Horse, Mass Production, Propaganda Machine, Cathedral Builders, Feudal Levy

**Tier 2 — Simple Python callbacks (canTrigger + apply)**:
- Gold Fever, Border Dispute, Famine, Road Network, Mercantilism, Oil Baron, Mercenary Companies

**Tier 3 — Complex Python (tracking state over turns)**:
- Scorched Earth, Warlord's Challenge, Enlightenment, Deforestation, Workers' Revolt, Succession Crisis

**Tier 4 — Novel mechanics (significant Python, possibly DLL)**:
- Duel of Champions, Wager, World Fair, Prophecy, Trade Embargo

---

## Next Steps

1. Choose 5-8 quests from Tier 1-2 to implement first
2. Write XML trigger + event entries
3. Write Python callbacks where needed
4. Add text keys
5. Test gate validation
6. Manual smoke test in-game
