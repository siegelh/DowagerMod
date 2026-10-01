# New Civilizations and Leaders

## Implementation status

**Target: 13 new civilizations, increasing the selectable roster from 59 to 72.**
Each civilization has one intended leader, one unique unit, one unique building,
and one signature trait. This does not increase simultaneous player slots.

All thirteen packages are integrated: **Piye, Stefan Dusan, Matthias Corvinus,
Pedro II, Mongkut, Simon Bolivar, Hiram I, Ramkhamhaeng, Ho Chi Minh,
Askia Muhammad, David, Sennacherib and Zenobia**. The current selectable roster is **72**.
Mongkut's diplomatic-research
and Bolivar's conquest-occupation rules are wired into their civilizations;
their native support has compiled and the content has passed its gate.
Hiram's coastal trade-team Gold rule, city breakdown and AI treaty-value
estimate are integrated too; the bonus pays only for actual active routes.
The shared capped worked-plot engine is compiled: city accounting, governor
and worker estimates, technology/building refreshes and tooltips are wired.
Ramkhamhaeng, Ho and Askia now use those rules. David's veteran-garrison
Culture refreshes with unit movement, level, transport and death changes;
animals do not qualify. Sennacherib and Zenobia have their UU, UB, trait
and civilization-specific Worker improvements, including intact/pillaged
identities, assigned-city build caps, restoration and capture behavior.
Human and AI actions share legality checks; AI can prepare Station roads.

The required full content/native gate passes. Reconstruction verifies all
58 outputs with no changes; native rules pass 1,422,460 exact cases.
The complete tools suite reports **399 passed and one historical
additive-signature failure**; it is not represented as fully green.
See the expansion plan's final handoff for evidence and the exact DLL hash.

All balance numbers are initial targets, not playtested conclusions.
Leaderheads and supporting visuals are provisional until in-game acceptance.
Nothing has been pushed, merged, installed, or applied to the live game.
**Ready for merge/deploy: No.** The manual gameplay, graphics, AI, old-save
and multiplayer checks in `docs\MANUAL_SMOKE_TESTS.md` remain unperformed.

## At a glance

| Leader | New civilization | Main idea | Signature trait |
|---|---|---|---|
| **Sennacherib** | Neo-Assyria: Nineveh | Productive river infrastructure supports deliberate siege warfare. | With Royal Waterworks, each worked riverside Farm or Royal Canal gives **+1 city Production**, capped at **+3 per city**. |
| **Hiram I** | Phoenicia: Tyre | Build a diverse coastal trading network. | A coastal city gets **+1 Gold per distinct foreign trade-route team**, capped at **+3**. Multiple routes to the same team count once. |
| **Piye** | Kush: Napata | Priest-supported population and early archery. | Ordinary Priests give **+1 Food**; **+25% domestic Great General rate**. |
| **Matthias Corvinus** | Hungary: Corvinian Kingdom | Maintain and modernize a paid professional army. | Melee/Gunpowder units receive a **25% upgrade-discount promotion**; ordinary Artists give **+1 Research**. |
| **Ramkhamhaeng** | Sukhothai | River agriculture supports cultural growth. | From Writing, each worked riverside Farm gives **+1 city Culture**, capped at **+3**. |
| **Mongkut** | Siam: Rama IV | Scientific catch-up through open diplomacy. | **+20 percentage points** to a technology's research modifier if an eligible foreign Open Borders team knows it. Once per technology, not per partner. |
| **Ho Chi Minh** | Vietnam: Democratic Republic | Preserve useful woodland to sustain mobilization. | Each worked Forest/Jungle plot gives **+1 city Production**, capped at **+3**; **+50% domestic Great General rate**. |
| **Askia Muhammad** | Songhai: Askia Dynasty | Commercial river settlements support scholarship. | Worked riverside Cottage/Hamlet/Village/Town plots give **+1 city Gold each**, capped at **+4** across all stages. |
| **Stefan Dusan** | Serbia: Dusan's Empire | Mining revenue and legal institutions support noble cavalry. | Mines give **+1 Commerce yield**; ordinary Priests give **+1 Espionage**. |
| **Pedro II** | Brazil: Second Empire | Cross-disciplinary specialists develop science and culture. | Ordinary Scientists give **+1 Culture**, Artists **+1 Research**; **+25% Great Person rate**. |
| **Simon Bolivar** | Gran Colombia | Mobile campaigns with faster recovery of captured cities. | Newly generated military-conquest occupation is **halved, rounded up**; **+50% Great General rate**. |
| **Zenobia** | Palmyrene Empire | Develop desert trade sites to fund expensive armored cavalry. | Each worked Desert plot with an unpillaged, non-ruins improvement and Road/Railroad gives **+2 city Gold**, capped at **+6**. |
| **David** | Israel: Davidic Kingdom | Experienced defenders become cultural symbols. | A city with an owned, non-cargo, combat-capable land unit of **level 3+** gets **+3 Culture once**, plus **+25% domestic Great General rate**. |

## Unique units and buildings

Unmentioned statistics, prerequisites, resource requirements, abilities and
upgrades remain those of the **live DowagerMod parent**, not an assumed vanilla
version. Costs below are normal-speed Production.

| Package | Unique unit | Unique building |
|---|---|---|
| **Sennacherib** | **Assyrian Siege Tower**, replacing Catapult: cost **60**; strength 5, movement 1; bombard **12** instead of 8; **+25% city attack**; collateral damage **50** instead of 100. Trades field/collateral efficiency for city assault. | **Royal Waterworks**, replacing Aqueduct: cost **100**, Mathematics; retains **+2 health** and adds **one Engineer slot**. Enables the trait's city Production bonus. |
| **Hiram** | **Tyrian Merchant Galley**, replacing Galley: cost **60**; movement **3** instead of 2; strength 2 and ordinary cargo/ocean restrictions retained. | **Tyrian Counting House**, replacing Market: cost **150**, Currency; retains **+25% Gold** and two Merchant slots; adds **+25% foreign trade-route modifier**. |
| **Piye** | **Kushite Archer**, replacing Archer: cost **25**, strength 3; **two guaranteed first strikes** instead of one and **+25% hills attack**. Retains city/hill defenses and both medieval upgrade paths. | **Napatan Cult Chapel**, replacing Monument: cost **40** instead of 30; **+1 Culture above the parent** and **one Priest slot**; Mysticism and Astronomy obsolescence retained. |
| **Matthias** | **Black Army Arquebusier**, replacing Musketman: cost **100** instead of 80; strength **10** instead of 9; **Drill I** and **+1 Gold extra unit cost**. | **Corvinian College**, replacing University: cost **200**, Education; retains **+25% Research**; adds **+3 Culture** and **one Artist slot**. |
| **Ramkhamhaeng** | **Sukhothai War Elephant**, replacing War Elephant: cost **65** instead of 60; strength 8; **20% withdrawal**. Still requires Ivory, Construction and Horseback Riding. | **Ho Trai**, replacing Library: cost **100** instead of 90; Writing, **+25% Research**, two Scientist slots; adds **+2 Culture** and **one Priest slot**. |
| **Mongkut** | **Siamese Royal Rifle**, replacing Rifleman: cost **120** instead of 110; strength 14; **Drill I** and **+25% city defense**. | **Royal Observatory**, replacing Observatory: cost **150**, Astronomy; retains **+25% Research**; **two Scientist slots total** and **+1 Culture**. This is a city building, not the mountain Research Campus. |
| **Ho** | **Viet Minh Infantry**, replacing Infantry: cost **120** instead of 140; strength **18** instead of 20; **Woodsman I and II**. Still needs Assembly Line and Rifling. | **Resistance Headquarters**, replacing Intelligence Agency: cost **180**, existing **Utopia** prerequisite; retains **+8 Espionage, +50% Espionage and two Spy slots**; adds **+15% military Production**. |
| **Askia** | **Sahelian Escort Cavalry**, replacing Knight: cost **90**, strength 10, movement 2; **Sentry** and **20% withdrawal**. Retains Horse AND Iron requirements. | **Timbuktu Scholarly College**, replacing University: cost **180** instead of 200; Education, **+25% Research**, and **one Priest slot**. Not another University of Sankore wonder. |
| **Dusan** | **Vlastela Cavalry**, replacing Knight: cost **95** instead of 90; strength 10, movement 2; **+25% hills attack** and **+25% versus Melee**. Pikemen remain important counters. | **Zakonik Court**, replacing Courthouse: cost **130** instead of 120; **-60% maintenance total** rather than -50%; adds **+2 Culture** and retains +2 Espionage/Spy slot. |
| **Pedro** | **Voluntarios da Patria**, replacing Rifleman: cost **100** instead of 110; strength 14; **March**. No extra drafting or free unit spawning. | **Imperial Lyceum**, replacing University: cost **220** instead of 200; **+35% Research total** rather than +25%; **one Artist slot** and **+1 Culture**. |
| **Bolivar** | **Llanero**, replacing Cavalry: cost **140** instead of 120; strength 15; movement **3** instead of 2; withdrawal **40% total** instead of 30%. Retains the full Cavalry tech/resource requirements. | **Republican Cabildo**, replacing Courthouse: cost **120**, Code of Laws; retains maintenance/Espionage/Spy effects; **+2 experience for trained land units**. |
| **Zenobia** | **Palmyrene Clibanarius**, replacing Horse Archer: cost **70** instead of 50; strength **8** instead of 6; movement 2; withdrawal **10% total** instead of the live parent's 40%; requires **Horse AND Iron**. | **Caravan Court**, replacing Market: cost **180** instead of 150; Currency, **+25% Gold**, two Merchant slots; adds **one trade route**. |
| **David** | **Gibbor Royal Retainer**, replacing Swordsman: cost **45** instead of 40; strength 6; **+25% city attack total** instead of +10%; **+25% hills defense**; **Copper OR Iron**, not Iron only. Iron Working remains. | **Royal Citadel**, replacing Walls: cost **60** instead of 50; Masonry, normal defenses and Rifling obsolescence; adds **+1 Culture** and **one Priest slot**. Available in flatland cities too. |

## Two civilization-specific worker improvements

### Assyrian Royal Canal

- Built by normal Workers after **Mathematics**, at **125% of Farm work time**.
- **+1 Food and +1 Commerce** on the tile; must be worked to contribute output.
- Flat, featureless Grassland/Plains/Desert; **riverside OR already irrigated**.
- Owned, resource-free plot assigned to a city BFC; **two per assigned city**.
- Carries irrigation under the normal irrigation-technology rules.
- A worked riverside Canal shares Sennacherib's **+3 Production cap** with Farms.
- **Not navigable by ships** and does not create rivers or city fresh water.

### Palmyrene Caravan Station

- Built by normal Workers after **Currency**, at **150% of Farm work time**.
- **+1 Food and +3 Commerce** on the tile; must be worked.
- Flat, featureless Desert, including **no Oasis/Flood Plains**; existing
  **Road/Railroad** required.
- Owned, resource-free plot assigned to a city BFC; **one per assigned city**.
- Can qualify for Zenobia's existing **+6 city Gold cap**.
- Road pillage removes trait eligibility, not the Station's ordinary tile yields.

For both: pillaged copies still count toward the construction cap; repair does
not take another slot. Capture never deletes surplus copies automatically.
Existing yields survive capture, but only the matching civilization can build
or restore its unique improvement. No great-person landmark replacement.

## Important rules and tradeoffs

- **Gold and Commerce are different.** Commerce yield goes through the slider;
  flat Gold/Research/Culture/Espionage goes to that specific channel before
  normal city modifiers.
- Worked-plot trait bonuses require ownership, the assigned working city,
  and an actually working citizen. No double payment from overlapping BFCs,
  city centers, or unworked plots. The mountain Research Campus remains its
  separate, existing unworked-BFC mechanic.
- Specialist bonuses require an assigned specialist, including genuinely free
  assigned specialists. Empty slots and settled Great People do not qualify
  unless specifically stated.
- Hiram needs real foreign routes and coastal cities. Mongkut needs Open Borders
  with a qualifying non-vassal team that already knows the researched technology.
- Bolivar changes only **new conquest occupation**, not peaceful transfers or
  an already running occupation timer.
- David's Culture is **once per city**, not once per veteran. Foreign units,
  Workers, cargo and Great Generals alone do not qualify.
- Under **Unrestricted Leaders**, traits follow leaders; units, buildings and
  unique-improvement permissions follow civilizations. Some package synergies
  therefore do not transfer.

## Visual and historical caveats

Existing animated leaderheads are being retained, not automatically remade.
David's existing art is explicitly provisional; Ho's primary blue shirt must
be preserved. Pedro II's identity and final appearance still need acceptance.

Piye/Dusan currently use provisional stock unit/building art. Matthias uses a
provisional raven-emblem button because his package lacks a portrait button;
his animated portrait is unchanged. New flags are labeled reconstructions
where an attested period flag is not established.

Mongkut's missing eye texture is restored from an identical bundled stock
texture. Bolivar retains his portrait, now in a valid 64x64 runtime button,
and his head-animation data. His background repair preserves the model's
camera/mesh orientation while omitting animation targets absent from that model.
Hiram's visible scene is preserved exactly in a runtime model that removes
five unrelated export roots. Those roots, not his visible meshes, contained
the unresolved texture references. His separate nonshader model is retained.
Ho's primary blue shirt is unchanged; only his fallback clothing texture
reference changes to that same blue map, with identical clothing UVs.
Askia's obsolete absolute texture path now uses the bundled relative texture.
Both repaired models preserve every other original byte. Ramkhamhaeng's
existing primary, fallback, background and portrait are retained.
David's missing background texture is reconstructed without changing decoded
pixels; his existing model and static background remain provisional.
Zenobia's exact named stock environment texture is restored, with a separate
filename-only runtime KFM. Sennacherib uses his retained primary in both slots
instead of the bundled stock-Stalin fallback. Low-settings certification
remains open. The original small canal and reused caravan-house map models
are prototypes, not approved final visuals.

Ancient/traditional biographies, especially David's, will distinguish
historical evidence from literary tradition. No modern-state analogy or new
religion is being added.

## Work boundaries

Development branch:
`agent-baseline-leader-chatter-sol-leader-update-visual-overhaul-new-leaders`

Worktree: `C:\DowagerMod-new-leaders`

The original roster, accepted Blue Marble/visual corrections, Barclay uniform,
and existing Research Campus changes are being preserved. Six original
suggestions remain backlog only: Sunni Ali, Mursili II, Suppiluliuma I,
Nzinga a Nkuwu, Seleucus I and Bayinnaung.

Detailed progress and evidence:
[`../docs/plans/active/2026-09-30-new-leaders-expansion.md`](../docs/plans/active/2026-09-30-new-leaders-expansion.md)

Implemented package definitions:
[`../tools/manifests/new_leaders_expansion.json`](../tools/manifests/new_leaders_expansion.json)
