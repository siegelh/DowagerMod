# Corporation Overhaul Implementation Draft

## Purpose

This draft defines the next corporation pass for the industry overhaul.

The goal is to make corporations:

1. founded from mature sector development rather than raw map bonuses
2. easier to understand in play
3. easier to represent in the Industry Advisor graph
4. less dependent on stale vanilla BTS corporation assumptions

This draft intentionally settles the design before code or XML work begins.

## Final Direction

Use a fixed-family corporation model.

Do not use the dynamic "fill a corporation slot from any qualifying bundle" model in this pass.

### Why

The slot-based model is interesting, but it is a different system rather than a simple corporation rebalance.

It would create several problems:

1. Civ4 corporations are globally unique by type, and the existing DLL assumes that model.
2. The UI, pedia, advisor graph, and text become much harder to explain if the same slot can represent different sectors in different games.
3. "These composites have already been consumed to found another corporation" is hidden state and not very legible to the player.
4. AI logic becomes much harder because it has to reserve or spend sector progress strategically.
5. Seven fixed corporation slots are not enough to support a truly player-specific charter system cleanly.

If that idea is ever pursued, it should be treated as a separate "charter" mechanic, not as a minor extension of the current corporation implementation.

## Core Design Decisions

### 1. Keep fixed named corporations

Corporations remain fixed global entities:

1. `Continental Provisions Company`
2. `Grand Hospitality Company`
3. `Imperial Luxury Exchange`
4. `Courtly Arts & Regalia Consortium`
5. `Aromatics & Festival Consortium`
6. `World Media Syndicate`

`CORPORATION_7` remains reserved and inactive for now.

### 2. Founding comes from broad composite families

Each corporation owns a family of composite industry building classes.

A player becomes eligible to found that corporation when the empire has at least `3` distinct active composite industry classes from that family.

Important:

1. "distinct" means three different composite building classes, not three copies of one class
2. "active" means the building exists and its local prereqs are currently met
3. composites are not consumed or reserved when the corporation is founded
4. corporation families should be exclusive: one composite class belongs to one corporation family only

### 3. Use broad buckets, not anchor composites

This draft does not require one special "anchor" composite plus two others.

The rule is intentionally simpler:

1. each corporation has a broad qualifying family
2. any `3` distinct active composites from that family are enough to found it

This keeps the system legible and gives the player multiple valid routes into a sector.

### 4. Keep a Great Person trigger, but unify it

Use `Great Merchant` for all active corporations.

Reasoning:

1. the new corporation model is about empire-scale commercial organization, not specialized inventor types
2. a single founder type is easier to understand
3. this preserves player agency over when and where a corporation is founded
4. it removes the stale mixed Scientist / Engineer / Artist / Merchant mapping now scattered across XML

This draft does not recommend a no-Great-Person founding model yet.

That can be revisited later if the Merchant requirement feels like unnecessary friction.

### 5. Separate founding families from operating inputs

A corporation should have:

1. a broad founding family of composite industries
2. a smaller signature set of synthetic goods that power spread and scaling

These two lists do not need to be identical.

This is important because it lets us:

1. use broad founding buckets without making operating inputs too noisy
2. keep the spread rule readable
3. reduce accidental corporation competition from overlapping bonus lists

## Founding Model

### Eligibility

A corporation can be founded only if all of the following are true:

1. the corporation is not already founded globally
2. the player is not blocked by a no-corporation civic state
3. the team has `TECH_CORPORATION`
4. the team has the corporation's sector tech
5. the player has at least `3` distinct active composite industry classes from that corporation's founding family
6. the player expends a `Great Merchant` to found the corporation headquarters

### HQ behavior

For the first pass, keep HQ founding behavior city-chosen and simple:

1. the player moves the `Great Merchant` into a city
2. the merchant founds the corresponding HQ building there
3. the HQ building founds the corporation in that city

Do not add a new local HQ-city requirement in this pass.

Empire-level sector maturity is the important gate.

### Post-founding behavior

Once founded:

1. the corporation stays founded even if the founding composite threshold later falls below `3`
2. spread and city value continue to depend on the corporation's synthetic operating inputs
3. the founding threshold is a charter requirement, not an ongoing maintenance check

This matches how religions and corporations generally behave in Civ4 and avoids unstable on/off HQ states.

## Operating Model

Corporation `PrereqBonuses` should represent signature synthetic goods for the sector.

These bonuses drive:

1. whether a city is eligible for spread
2. corporation value in that city
3. corporate yield / commerce scaling

Keep the current low-scaling rule:

1. count distinct operating inputs only, or
2. cap each input type at `1`

This prevents runaway scaling from one synthetic good being mass-stacked.

## Proposed Corporation Roster

### Corporation 1: Continental Provisions Company

Role:

Empire-scale food supply, preservation, victualing, and staple provisioning.

Founding threshold:

`3` active composites from this family.

Sector tech:

`TECH_REFRIGERATION`

Required extra tech:

`TECH_CORPORATION`

Signature operating inputs:

1. `Flour`
2. `Cured Meats`
3. `Preserved Seafood`
4. `Fruit Preserves`

Founding family:

1. `Bakers' Exchange`
2. `Spiced Carvery`
3. `Preserves Market`
4. `Victuallers' Exchange`
5. `Spiced Fish Market`

Notes:

1. This is the practical supply-and-storage food corporation.
2. It should not include the courtly banquet branch.

Executive display name:

`Provisions Factor`

### Corporation 2: Grand Hospitality Company

Role:

Banquets, kitchens, elite service, and ceremonial dining.

Founding threshold:

`3` active composites from this family.

Sector tech:

`TECH_MEDICINE`

Required extra tech:

`TECH_CORPORATION`

Signature operating inputs:

1. `Vintage Wine`
2. `Confections`

Founding family:

1. `Festival Kitchens`
2. `Royal Kitchens`
3. `Grand Banquet Hall`
4. `Ceremonial Cellars`
5. `Maritime Supper Club`
6. `Pastry House`
7. `Dessert Cellars`

Notes:

1. This is the prepared-consumption and luxury hospitality branch.
2. It is intentionally distinct from practical provisioning.
3. The smaller operating-input set is acceptable because this corporation represents service and prestige consumption rather than broad supply logistics.

Executive display name:

`Hospitality Steward`

### Corporation 3: Imperial Luxury Exchange

Role:

Textiles, bullion, gems, silverwork, and exchangeable elite luxuries.

Founding threshold:

`3` active composites from this family.

Sector tech:

`TECH_BANKING`

Required extra tech:

`TECH_CORPORATION`

Signature operating inputs:

1. `Fine Silk`
2. `Fine Dyes`
3. `Fine Furs`
4. `Gold Bullion`
5. `Worked Silver`
6. `Cut Gems`

Founding family:

1. `Royal Garments House`
2. `Noble Tailors' Hall`
3. `Dyed Fur Salon`
4. `Crown Jeweler`
5. `Royal Mint`
6. `Gemcutters' Exchange`

Notes:

1. This is the cleanest and most coherent existing sector.
2. It should be kept narrow and not absorb the regalia / antique / marble branch.

Executive display name:

`Luxury Broker`

### Corporation 4: Courtly Arts & Regalia Consortium

Role:

Court regalia, state display, curios, antiques, carved prestige goods, and marble ceremonial works.

Founding threshold:

`3` active composites from this family in phase 1.

Balance note:

Because this family is large, it is the first candidate to move to `4` active composites if playtesting shows it founding too easily.

Sector tech:

`TECH_AESTHETICS`

Required extra tech:

`TECH_CORPORATION`

Signature operating inputs:

1. `Ivory Carvings`
2. `Lamp Oil`
3. `Marble Statuary`

Founding family:

1. `Court Regalia Atelier`
2. `Regal Treasures Court`
3. `Imperial Outfitters`
4. `Admiralty Curios House`
5. `Navigator's Instrument Works`
6. `Hall of Cameos`
7. `Triumphal Court`
8. `Gallery of Antiquities`
9. `Curio Auction House`

Notes:

1. This family is about prestige display and ceremonial material culture.
2. `Sculptors' Yard` is not part of the family because it is a processor, not a composite.

Executive display name:

`Regalia Envoy`

### Corporation 5: Aromatics & Festival Consortium

Role:

Incense, spice, perfume, ceremony, and festival ambience.

Founding threshold:

`3` active composites from this family.

Sector tech:

`TECH_DRAMA`

Required extra tech:

`TECH_CORPORATION`

Signature operating inputs:

1. `Temple Incense`
2. `Spice Blends`

Founding family:

1. `Perfumers' Quarter`
2. `Confectioners' Exchange`
3. `Festival Market`
4. `Perfumed Salon`
5. `Lantern Procession Works`
6. `Sacred Precinct`

Notes:

1. This family is intentionally narrower than hospitality.
2. It is about atmosphere, ceremony, and festival culture rather than kitchens and banquets.

Executive display name:

`Festival Envoy`

### Corporation 6: World Media Syndicate

Role:

Performance, recording, film, broadcast spectacle, and mass entertainment.

Founding threshold:

`3` active composites from this family.

Sector tech:

`TECH_MASS_MEDIA`

Required extra tech:

`TECH_CORPORATION`

Signature operating inputs:

1. `Stage Plays`
2. `Master Recordings`
3. `Film Prints`

Founding family:

1. `Opera House`
2. `Cinema Palace`
3. `Soundstage Complex`
4. `Mass Entertainment Network`
5. `Illuminated Theatre`

Notes:

1. This family should stay late and relatively exclusive.
2. It is the clearest end-of-chain modern corporation.

Executive display name:

`Syndicate Agent`

## Corporation 7 Policy

`CORPORATION_7` should remain reserved and inactive.

Do not try to "use it because it exists."

For now:

1. keep it technically unused
2. remove or suppress it from UI where possible
3. do not let it appear as a valid advisor target or implied missing content

If a seventh corporation is ever added, it should be attached to a real sector rather than being revived by inertia.

## Great Person and HQ Policy

### Recommended founding unit

All six active corporations should use `Great Merchant`.

### Required cleanup

1. HQ buildings `BUILDING_CORPORATION_1` through `BUILDING_CORPORATION_6` should all use `UNITCLASS_MERCHANT` for `GreatPeopleUnitClass`.
2. `BUILDING_CORPORATION_7` remains `NONE`.
3. `UNIT_MERCHANT` should gain access to all six active HQ buildings.
4. `UNIT_VENETIAN_MERCHANT` should mirror the normal Great Merchant corporation-building list, not its current mixed bag.
5. `UNIT_ARTIST`, `UNIT_SCIENTIST`, `UNIT_ENGINEER`, and `UNIT_PROPHET` should lose stale corporation-building entries.

### Why unify to Merchant

1. fewer weird exceptions
2. clearer UX
3. fits the idea of corporate chartering
4. preserves manual player timing

## Executive / Spread Unit Policy

Keep the internal `UNIT_EXECUTIVE_*` XML type ids for save compatibility.

Change only data and displayed text.

### Spread model

Keep the existing spread model in principle:

1. corporations spread through dedicated missionary-like units
2. a target city must have at least one valid operating input for that corporation
3. corporation spread still costs gold

This is already compatible with the synthetic-good model.

### Required cleanup

1. fix `UNIT_EXECUTIVE_2`, which currently has stray placeholder text and an invalid `BUILDING_BOMB_SHELTER` prereq
2. rename all six active spread units in text
3. keep `UNIT_EXECUTIVE_7` reserved or hide it from practical play

### Proposed display names

1. `UNIT_EXECUTIVE_1` -> `Provisions Factor`
2. `UNIT_EXECUTIVE_2` -> `Hospitality Steward`
3. `UNIT_EXECUTIVE_3` -> `Luxury Broker`
4. `UNIT_EXECUTIVE_4` -> `Regalia Envoy`
5. `UNIT_EXECUTIVE_5` -> `Festival Envoy`
6. `UNIT_EXECUTIVE_6` -> `Syndicate Agent`
7. `UNIT_EXECUTIVE_7` -> reserved / hidden

## Competition Policy

### Phase 1 recommendation

Do not add a new explicit competition system yet.

Instead:

1. use mostly non-overlapping signature operating-input sets
2. let the existing shared-input competition rule become mostly irrelevant

This keeps the first pass simpler and avoids immediate DLL/schema work just for competition.

### Phase 2 option if needed

If later tuning shows we want richer overlap between corporation operating inputs, then add explicit corporation competition metadata in XML and stop inferring competition from shared `PrereqBonuses`.

That would require DLL work around [CvGame.cpp](/c:/DowagerMod/third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvGame.cpp#L8054).

Do not do this in phase 1 unless playtesting proves it necessary.

## Availability and Tech Normalization

All active HQ buildings should be normalized to the same tech pattern:

1. `PrereqTech` = sector tech
2. first `TechTypes` entry = `TECH_CORPORATION`
3. corporation XML `TechPrereq` should match the same sector tech

This fixes the current inconsistency where `CORPORATION_2` is using `TECH_CODE_OF_LAWS` in the HQ building tech list.

### Proposed sector-tech map

1. `Continental Provisions Company` -> `TECH_REFRIGERATION`
2. `Grand Hospitality Company` -> `TECH_MEDICINE`
3. `Imperial Luxury Exchange` -> `TECH_BANKING`
4. `Courtly Arts & Regalia Consortium` -> `TECH_AESTHETICS`
5. `Aromatics & Festival Consortium` -> `TECH_DRAMA`
6. `World Media Syndicate` -> `TECH_MASS_MEDIA`

Interpretation:

1. `TECH_CORPORATION` is the general legal / institutional framework
2. the sector tech is the thematic specialization gate
3. if the sector tech is earlier than `TECH_CORPORATION`, actual unlock remains effectively at `TECH_CORPORATION`

## Distinct Active Composite Count: Exact Meaning

The founding threshold should continue to use the current DLL concept of active composite presence:

1. count building classes, not building copies
2. count only composites already built somewhere in the empire
3. count only composites whose local synthetic prereqs are currently active

This means:

1. conquered but inactive composites do not count
2. duplicate copies of the same composite class do not stack
3. losing required synthetic goods can delay founding if the threshold is no longer met before the corporation is founded

This is the correct rule and should be preserved.

## Recommended XML and DLL Changes

### XML: required

1. `CIV4CorporationInfo.xml`
   - rewrite `FoundingBuildingClasses`
   - rewrite `PrereqBonuses`
   - set `iFoundingMinActiveBuildingClasses = 3` for `CORPORATION_1` through `CORPORATION_6`
   - keep `CORPORATION_7` reserved
2. `CIV4BuildingInfos.xml`
   - normalize HQ tech requirements
   - normalize HQ `GreatPeopleUnitClass` to Merchant
3. `CIV4UnitInfos.xml`
   - fix executive data
   - move all active corporation HQ-building access to Great Merchant
   - clean stale HQ-building access from other Great People
4. text XML
   - update corporation names, pedia, strategy, and executive display names
   - update the corporation concept text so it matches the new model

### DLL: not required for phase 1

The current DLL already supports:

1. per-corporation founding families
2. distinct active family counts
3. synthetic-good operating inputs
4. corporation spread via input bonuses

### DLL: optional phase 2

If later desired:

1. explicit competition matrix instead of shared-bonus competition inference
2. per-player HQ cap if one civilization starts monopolizing too many corporations

Neither is required for the first implementation pass.

## Text Cleanup Requirements

The current text state is split between stale vanilla BTS text and newer override text.

This pass should make the industry-supply-chain text authoritative.

### Required cleanup

1. update `TXT_KEY_CONCEPT_CORPORATIONS_PEDIA` so it no longer describes vanilla Great Person and raw-resource founding
2. ensure corporation names are only the new sector names
3. ensure executive names are only the new sector spread-unit names
4. ensure `Civilized Jewelers` no longer appears as a false active corporation in player-facing text

## Advisor / UI Implications

This draft is intentionally structured to help the future graph view.

The graph can represent corporations cleanly if each corporation has:

1. a fixed family of composite industries
2. a fixed founding threshold
3. a fixed set of operating synthetic goods

The graph should not be built until this corporation family data is stabilized.

## Implementation Sequence

### Phase 1: data cleanup and rule normalization

1. normalize corporation names and active roster
2. normalize founding thresholds to `3`
3. rewrite founding families
4. rewrite operating-input synthetic bonuses
5. normalize HQ tech requirements
6. normalize all HQ founder GP classes to Merchant
7. clean Great Person building lists
8. fix executive XML and names
9. keep slot `7` reserved and hidden

### Phase 2: rebalance and text polish

1. tune corporation yield / commerce output based on the new input counts
2. update pedia and strategy text
3. check AI spread behavior and spread cost tuning

### Phase 3: advisor graph integration

1. feed the fixed corporation family data into the graph layer
2. show founding progress as `X / 3 active composites`
3. show operating input availability separately from founding availability

## Playtest Questions

After phase 1, the first questions to answer in live games should be:

1. Are `3` active composites too easy or too hard for each family?
2. Does `Courtly Arts & Regalia Consortium` need a threshold of `4` because its family is larger?
3. Does a single strong civilization still monopolize too many corporations?
4. Do the reduced operating-input sets for Hospitality and Aromatics feel too narrow?
5. Are renamed spread units clear enough in the city build list?

## Balance Levers To Keep In Reserve

If the first pass needs tuning, use these levers in this order:

1. change `iFoundingMinActiveBuildingClasses`
2. change corporation spread cost
3. change corporation yield / commerce output
4. add a per-player HQ cap
5. add explicit competition metadata

Do not jump straight to a dynamic charter-slot system unless the fixed-family model clearly fails.
