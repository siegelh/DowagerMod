# Remaining-roster DLL contracts

- Status: `complete`
- Owner: `dll-contracts`
- Scope: all 16 non-`Keep` packages in the frozen implementation matrix
- Runtime edits: **none**
- Machine-readable companion: `tools/baselines/remaining_roster_dll_contracts.json`

## Verdict

**NO NEW DLL MECHANIC.** Every approved proposal is representable by an
existing schema field and live loader/getter/runtime path. No package needs a
new XML tag, enum, mission, command, persisted member, Python binding, network
message, or random decision path.

This verdict has one release condition: the trait channels cached in
`CvPlayer` are serialized. Existing saves can therefore retain pre-change
values. The implementation must either declare the roster pass **new-game
only** or separately approve a DLL cache migration. A migration would be DLL
maintenance, not a new gameplay mechanic, and is not part of the frozen
matrix. The matrix itself proposes no migration
(`tools/baselines/remaining_roster_implementation_matrix.json:26-69`).

## Review of every non-Keep package

| Package | Frozen change | Existing contract | New DLL? |
|---|---|---|---|
| Washington | Remove Town, Barracks, Courthouse, Bank, Spy, Merchant, Wheat and Horse trait bonuses; retain Road commerce | Trait improvement/building/specialist/bonus/route tables | No |
| Geronimo | Peace weight and limited-war scalar tuning | `CvLeaderHeadInfo` stock personality fields | No |
| Hammurabi | Palace yield/commerce reductions | `CvBuildingInfo` stock yield/commerce arrays | No |
| Elizabeth | Restore Galley/Trireme defaults; retain Privateer→Sea Dog | `CvCivilizationInfo` unit-class overrides | No |
| Huayna Capac | Help/strategy rewrite only | text keys; no runtime field | No |
| Wang Kon | Restore Library/Academy mappings; keep dormant types | civilization building-class overrides | No |
| Asoka | Obelisk trait links and war-weariness scalar | stock building trait/scalar fields | No |
| Genghis Khan | Remove worked Castle Town commerce | trait `ImprovementCityCommerceChangesWorked` | No |
| Sitting Bull | Reset trade-yield array to zero | trait `TradeYieldModifiers` | No |
| Chinese Leader | Remove worked Farm espionage | trait `ImprovementCityCommerceChangesWorked` | No |
| Casimir | Growth/Culture flavor rebalance | stock leader flavor array | No |
| Salamasina | Health/happiness reductions | stock trait scalars | No |
| Stalin | Replace flat espionage with Factory production; tune units/buildings | trait commerce/building-yield arrays plus stock mappings/building fields | No |
| Enrico Dandolo | Trade commerce, ordinary Settler, restricted Merchant actions, Palace/personality rebalance | trait trade array, stock civ mapping/unit actions/building/leader fields | No |
| Churchill | MI6 and espionage-flavor rebalance | stock building specialist/commerce and leader flavor fields | No |
| Kublai Khan | Append and map Yuan Palace replacement | stock building fields and civ building-class override | No |

The package decisions are at
`tools/baselines/remaining_roster_implementation_matrix.json:329-1945`.
The matrix phrase “ImprovementCommerceChanges” for Genghis is not a schema
name. The live entry is specifically
`ImprovementCityCommerceChangesWorked`
(`CIV4TraitInfos.xml:695-707`); downstream implementation must edit that exact
container.

## Shared trait schema and loader contract

The trait schema defines `TradeYieldModifiers` and all typed sparse tables
(`CIV4CivilizationsSchema.xml:301-419`), then admits them on `TraitInfo`.
`CvTraitInfo::read` loads scalar fields and trade yields
(`CvInfos.cpp:17090-17134`) and the sparse tables at:

- improvement yield: `CvInfos.cpp:17158-17209`
- building yield/commerce: `CvInfos.cpp:17319-17412`
- specialist commerce: `CvInfos.cpp:17460-17504`
- bonus yield: `CvInfos.cpp:17507-17551`
- route yield: `CvInfos.cpp:17554-17598`
- worked/BFC improvement commerce: `CvInfos.cpp:17601-17695`

Typed getters resolve XML type strings at access time and return zero for no
entry (`CvInfos.cpp:16935-17079`; declarations and storage
`CvInfos.h:4213-4279`). All calculations are integer-only and deterministic.

### 1. Trait scalar and `TradeYieldModifiers`

**Consumers:** Sitting Bull (`[150,-500,-500]→[0,0,0]`), Dandolo
(`[0,0,0]→[0,0,25]`), Salamasina (`iHealth 5→3`, `iHappiness 3→2`), Stalin
(flat espionage `CommerceChanges` 50→0), Dandolo (`iUpkeepModifier 100→0`).

- **Getters/runtime:** traits are accumulated during player initialization
  (`CvPlayer.cpp:231-254`). Trade yield is
  `tradeProfit * playerModifier / 100` (`CvCity.cpp:8937-8948`); health,
  happiness, upkeep and free city commerce use the ordinary player totals.
- **AI valuation:** trade commerce has a narrow culture-victory-stage weight
  (`CvPlayerAI.cpp:13631-13649`). There is no direct trait-choice valuation
  for food/production trade modifiers or these scalar edits; leaders do not
  choose traits. City/economic AI observes the resulting totals.
- **Help/UI:** trait help prints each nonzero trade modifier
  (`CvGameTextMgr.cpp:3947-3950`) and stock scalar/commerce help. Zero entries
  disappear.
- **State/cache:** player totals are derived at initialization but then
  persisted. `m_aiTradeYieldModifier` is read/written
  (`CvPlayer.cpp:16110`, `16743`). Trade-route city yield is updated through
  normal trade-route recalculation; no new invalidator is required for static
  XML.
- **Python:** trait trade/scalar getters are exposed
  (`CyInfoInterface3.cpp:280-297`); player trade modifier is exposed through
  `CyPlayer` (`CyPlayer.cpp:1512-1514`).
- **Save/load:** new games receive the XML values. Existing saves retain the
  serialized old player totals. Use a new-game-only release rule unless a
  cache migration is approved.
- **MP risk:** low with identical XML. Asset mismatch produces divergent
  deterministic city yields; require identical XML/DLL manifests. No RNG or
  active-player dependency is introduced.
- **Exact tests:** (a) Sitting Bull city with a known domestic and foreign
  trade route returns ordinary food/production/commerce, not 150/-500/-500;
  (b) Dandolo's same route produces exactly +25% commerce yield after integer
  truncation; (c) trait help shows Dandolo +25 commerce and no Sitting Bull
  trade modifiers; (d) Salamasina empire totals change by -2 health/-1
  happiness versus baseline; (e) Stalin loses exactly 50 free espionage per
  city; (f) save/reload a new game and compare all values; (g) load a
  pre-change save and confirm/document the expected stale-cache policy; (h)
  two-player MP checksum smoke after route recalculation.

### 2. `ImprovementYieldChanges`

**Consumer:** Washington removes Town commerce +1. Genghis retains Workshop
production and is not changing this channel.

- **Runtime:** trait values are folded into
  `CvPlayer::m_ppaaiImprovementYieldChange` at init
  (`CvPlayer.cpp:257-264`), read by plot yield calculation
  (`CvPlot.cpp:5872-5879`). The changer calls `updateYield`
  (`CvPlayer.cpp:11860-11883`).
- **AI valuation:** no direct trait-table valuation was found. Worker/city AI
  sees the resulting plot yields through normal plot evaluation.
- **Help/UI:** enumerated in trait help (`CvGameTextMgr.cpp:3968-3981`).
- **State/cache:** derived player array, persisted at
  `CvPlayer.cpp:16167/16798`; plot yield and assignment caches are refreshed
  by the existing changer only during initialization.
- **Python:** `CvTraitInfo.getImprovementYieldChanges` is exposed
  (`CyInfoInterface3.cpp:297`); the aggregate player getter is not exposed.
- **Save/MP/determinism:** integer deterministic; existing saves retain Town
  +1 because the player array is serialized. Identical-assets requirement
  applies.
- **Exact tests:** Washington Town has no trait delta; Workshop/other
  improvements are unchanged; Civilopedia omits Town; city governor
  reassignment does not assume the old commerce; new-game save/reload is
  stable; pre-change save follows the declared compatibility policy; MP
  yields/checksum match.

### 3. `ImprovementCityCommerceChangesWorked`

**Consumers:** Genghis removes Castle Town commerce +3; Chinese Leader removes
Farm espionage +1.

- **Runtime:** `CvCity` iterates city plots, active traits and civics, counting
  only worked plots for this container (`CvCity.cpp:9079-9128`). It caches
  totals by commerce type (`CvCity.cpp:9132-9164`).
- **Invalidation:** refreshed at city initialization, plot assignment changes,
  civic changes, improvement changes, and after city read
  (`CvCity.cpp:770`, `11137`, `13296`; `CvPlayer.cpp:11766`).
- **AI valuation:** no direct trait-table valuation. Removal corrects city
  commerce totals used by the economy/espionage AI.
- **Help/UI:** worked entries are rendered in trait help
  (`CvGameTextMgr.cpp:4160-4178`).
- **State:** the city cache is derived/recomputed from live XML, not a trait
  array restored by the player save-v2 block. Thus existing saves should adopt
  these two removals when cities are read.
- **Python:** these `CvTraitInfo` getters are **not** bound in
  `CyInfoInterface3.cpp:277-304`; no Python dependency exists.
- **Save/MP/determinism:** deterministic city-plot iteration; low MP risk with
  matched XML. Recompute timing is already explicit.
- **Exact tests:** Genghis works/unworks a Japanese Castle Town and commerce
  stays unchanged; Chinese Leader works/unworks a Farm and espionage stays
  unchanged; retained Workshop/Spy bonuses are unchanged; pillage/rebuild,
  civic swap, save/reload and city transfer all reconcile; MP peers report
  identical city commerce. Also assert the implementation edits
  `ImprovementCityCommerceChangesWorked`, not the nonexistent matrix shorthand.

### 4. Trait building yield and commerce tables

**Consumers:** Washington removes Barracks production +1, Courthouse
espionage +2 and Bank gold +2. Stalin adds Factory production +1 through
`BuildingYieldChanges`.

- **Runtime:** init folds values by building **class**
  (`CvPlayer.cpp:266-279`). Active building base yield applies the trait class
  delta (`CvCity.cpp:1481`, `4764`); commerce uses the parallel city update.
  Changers update all active mapped buildings, invalidate yield ranks and dirty
  AI assignment (`CvPlayer.cpp:11886-11948`).
- **AI valuation:** no direct trait-table valuation. Building/city evaluation
  observes resulting yield/commerce, but this contract does not add bespoke
  Factory preference.
- **Help/UI:** both tables are listed in trait help
  (`CvGameTextMgr.cpp:4029-4080`); building help incorporates player trait
  yield (`CvGameTextMgr.cpp:7331`).
- **State/cache:** player class arrays are derived then persisted. Save-v2
  reads/writes building yield and commerce arrays
  (`CvPlayer.cpp:16178-16183`, `16806-16811`); legacy backfill and city
  reconciliation are at `CvPlayer.cpp:16213-16224`, `16568-16594`.
- **Python:** neither custom trait getter is bound in
  `CyInfoInterface3.cpp:277-304`.
- **Save/MP/determinism:** new games deterministic. Existing current-format
  saves retain Washington's old bonuses and omit Stalin's new Factory bonus
  unless migrated.
- **Exact tests:** Washington with one/two active Barracks, Courthouse and Bank
  has zero trait deltas; Stalin Factory adds exactly +1 base production per
  active Factory and stops when obsolete/disabled; replacement Factory class
  receives the class bonus; capture, sell/disable, save/reload, help text, AI
  city assignment and MP checksum all reconcile. Explicitly test a pre-change
  save under the chosen compatibility policy.

### 5. `SpecialistCommerceChanges`

**Consumer:** Washington removes Spy espionage +1 and Merchant gold +1.

- **Runtime:** folded at init (`CvPlayer.cpp:281-288`), read when specialist
  commerce is calculated (`CvPlayer.cpp:7734`; `CvCity.cpp:9185`).
- **AI/help:** assignment is dirtied by the changer
  (`CvPlayer.cpp:11836-11856`); help enumerates entries
  (`CvGameTextMgr.cpp:4107-4125`). There is no separate trait valuation.
- **State/cache:** derived player array is serialized
  (`CvPlayer.cpp:16173-16177`, `16801-16805`); legacy backfill reconciles
  existing specialists (`CvPlayer.cpp:16199-16211`, `16596-16606`).
- **Python:** custom trait getter is not bound.
- **Save/MP/determinism:** deterministic; current-format old saves retain old
  values unless migrated.
- **Exact tests:** Washington assigned/free Spy and Merchant each contribute
  no trait commerce; other specialist output remains unchanged; governor
  choices, add/remove specialist, capture, new-game save/reload, declared old
  save policy, help and MP checksum pass.

### 6. `BonusYieldChanges`

**Consumer:** Washington removes Wheat food +1 and Horse production +1.

- **Runtime:** folded at init (`CvPlayer.cpp:290-296`) and applied by plot
  yield calculation (`CvPlot.cpp:6006-6013`). Changer calls `updateYield`
  (`CvPlayer.cpp:11955-11975`).
- **AI/help:** normal plot valuation sees final yield; no direct trait
  valuation. Help enumerates entries (`CvGameTextMgr.cpp:4125-4143`).
- **State/Python:** derived player array is serialized
  (`CvPlayer.cpp:16184-16188`, `16812-16816`); getter is not Python-bound.
- **Save/MP/determinism:** deterministic; old current-format saves retain
  bonuses unless migrated.
- **Exact tests:** improved and unimproved visible Wheat/Horse tiles have no
  Washington trait delta; connect/disconnect, reveal, pillage, city
  reassignment, help, new-game save/reload, old-save policy and MP checksum
  pass.

### 7. `RouteYieldChanges`

**Consumer:** Washington retains Road commerce +1 while deleting all other
long-tail entries. This retained value must not be accidentally removed.

- **Runtime:** folded at init (`CvPlayer.cpp:298-304`) and added whenever a
  plot has a route (`CvPlot.cpp:5994-6004`). Changer calls `updateYield`
  (`CvPlayer.cpp:11978-11998`).
- **AI valuation:** no direct trait valuation. Generic route/worker AI has
  route-aware improvement valuation, but those call sites primarily read
  improvement route yields, not this trait table; validate behavior rather
  than assuming bespoke Road planning.
- **Help/UI:** listed in trait help (`CvGameTextMgr.cpp:4143-4160`).
- **State/Python:** player route array is serialized
  (`CvPlayer.cpp:16189-16193`, `16817-16821`). Trait getter is not
  Python-bound.
- **Save/MP/determinism:** deterministic; because the value is unchanged,
  save compatibility is expected for this retained entry.
- **Exact tests:** Washington Road on city, improved and unimproved plots adds
  exactly +1 commerce; no Road/no owner gives no trait delta; Railroad does
  not inherit the Road entry unless its own XML says so; pillage/rebuild,
  capture, save/reload, help, worker behavior and MP checksum pass.

### 8. Venetian Merchant action contraction

**Consumer:** Enrico Dandolo only. Keep the existing Merchant trade mission,
movement/cost/art, Golden Age, discovery, joining and corporation construction
unless the matrix is amended. Set `bFound=0`, clear `Builds` (Road and Grand
Colosseum), set `iWorkRate=0`, and set `iGreatWorkCulture=0`. The live action
surface is at `CIV4UnitInfos.xml:27647-27921`.

- **Schema/loader/getters:** `bFound`, `Builds`, `Buildings`, `GreatPeoples`,
  `iWorkRate` and `iGreatWorkCulture` are existing unit schema fields
  (`CIV4UnitSchema.xml:123,215-259,303-310`). XML loading is at
  `CvInfos.cpp:4698,4729,4753-4754,4855-4862`; getters at
  `CvInfos.cpp:3238,3273,3929-3979`.
- **Runtime:** Found gates settlement (`CvUnit.cpp:5218`); builds use ordinary
  build missions; construction checks unit building arrays
  (`CvUnit.cpp:5599-5638`); trade validates a foreign city, grants deterministic
  gold and consumes the unit (`CvUnit.cpp:5872-5920`); Great Work is disabled
  when culture is zero (`CvUnit.cpp:5928-5999`).
- **AI valuation:** removing `bFound` deliberately bypasses the custom
  Venetian Prince chooser (`CvUnitAI.cpp:3769-3783`, `14472-14555`). The
  normal merchant cascade still tries construct, discover, trade, Golden Age
  and join (`CvUnitAI.cpp:3758-3820`). Clearing `Builds` removes worker build
  choices. This is deletion of access to existing actions, not a new action.
- **Help/UI:** action buttons are generated from the same capability checks;
  disabled actions disappear. Update the unit strategy/help because current
  prose promises only the trade role but stale action buttons are observable.
- **State/cache:** capabilities are immutable `CvUnitInfo` data, not copied
  into each unit. Existing unit instances adopt current XML on load. Unit
  mission queues are persisted: do not release with an old save paused during
  an action that is being removed without a cancellation smoke test.
- **Python:** unit-info getters for work rate, Great Work, Found, Builds,
  GreatPeoples and Buildings are exposed
  (`CyInfoInterface1.cpp:206-213,286,334-341`). No new binding.
- **Determinism/save/MP:** all retained actions are deterministic under
  existing mission rules. Removing the custom chooser reduces, rather than
  adds, MP risk; its prior active-player announcement was already removed for
  OOS safety (`CvUnitAI.cpp:14516-14534`). Identical XML remains mandatory.
- **Exact tests:** Civilopedia/action bar show Trade, Discover, Golden Age,
  Join and permitted corporation construction; they show no Found, Road,
  Grand Colosseum or Great Work. Human trade mission grants the exact previewed
  gold and consumes the unit. AI merchant selects only retained actions and
  never enters `AI_venetianPrinceChoice`. Save/reload an idle Merchant and one
  with each legal queued mission; load/cancel a pre-change queued removed
  build; verify ordinary Great Merchant behavior is unchanged; run two-player
  MP turns with AI Venice and compare checksums.

## Standard-channel implementation checks

The remaining changes use stock info fields and need no dedicated DLL work:

1. Leader personality/flavor edits are immutable XML inputs to existing AI.
2. Building yield, commerce, health, happiness, trade-route, specialist,
   trait-production and war-weariness fields already drive building runtime,
   AI and help.
3. Civilization unit/building override arrays already resolve the concrete
   type for production and AI.
4. Dormant unit/building types must remain in place and
   `BUILDING_YUAN_IMPERIAL_SECRETARIAT` must be appended, never inserted, to
   preserve InfoType ordering as required by the matrix guardrail.
5. Text-only Huayna changes have no DLL contract.

For each such package, tests must cover XML schema validation, Civilopedia,
AI availability/valuation, construction/production, capture/obsolescence where
applicable, new-game save/reload, and a matched-assets MP smoke. Wang Kon,
Elizabeth, Stalin, Venice and Kublai additionally need assertions that the
civilization class mapping resolves exactly to the frozen target and that
dormant types remain addressable.

## Release gates

1. `tools/test_gate.ps1` passes after XML implementation.
2. Machine contract validation passes.
3. Every channel-specific scenario above is recorded in the implementation
   test evidence.
4. New-game-only versus trait-cache migration is explicitly decided before
   release.
5. Manual Civilopedia/action/yield and MP checksum smoke is completed; there
   is no automated gameplay suite.

