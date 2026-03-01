# Industry Advisor Flow Graph Plan

## Status

This document captures a potential future implementation for replacing the current Industry Advisor
chains table with a left-to-right flow graph modeled after the technology tree.

This is not scheduled work. It is a design note for later.

## Goal

Improve readability of the Industry Advisor progression view by changing it from a dense table into
a graph that shows:

1. raw resources
2. local processing buildings
3. synthetic goods
4. composite industries
5. corporations

The target user experience is the same core visual idea as the tech tree:

1. start on the left
2. follow arrows to the right
3. understand what each node unlocks or feeds
4. see current availability by color

## Recommendation

Reuse the tech chooser's rendering mechanics, not the tech chooser screen itself.

The stock chooser already provides the pieces that matter:

1. scroll panel rendering
2. tech-style boxed nodes
3. arrow art and arrow routing
4. grid-based manual layout
5. node color states

The chooser should not be reused as-is because it is hard-wired to:

1. actual `TechInfo` records
2. research queue state
3. Advanced Start behavior
4. the full-screen tech screen shell

## Current Relevant Files

Industry Advisor implementation:

- `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/Python/Screens/CvIndustryAdvisor.py`

Industry screen utils dispatch:

- `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/Python/CvIndustryScreenUtils.py`
- `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/Python/EntryPoints/CvScreenUtilsInterface.py`

Existing chain data currently embedded in the advisor:

1. `PROCESSING_CHAINS`
2. `COMPOSITES`
3. `CORPORATIONS`

Stock tech tree implementation to reuse conceptually:

- `CvTechChooser.py` from the installed BtS Python assets

Important chooser mechanics to port:

1. `attachPanelAt(..., PanelStyles.PANEL_STYLE_TECH, ...)`
2. scroll panel creation and `setViewMin`
3. arrow drawing using `ARROW_X`, `ARROW_Y`, `ARROW_XY`, `ARROW_MXY`, `ARROW_XMY`, `ARROW_MXMY`, `ARROW_HEAD`
4. geometry helpers like `getXStart`, `getWidth`, `getHeight`, `getYStart`
5. `setPanelColor`

## Important Constraint

The active repo currently vendors only a small subset of the Python screen stack. The stock
`CvTechChooser.py` is not present in the mod tree at the moment.

If this plan is executed, the first practical step is to vendor the relevant chooser source into the
mod's Python tree so the renderer can be adapted locally instead of being retyped from memory.

## Recommended UI Shape

Keep this inside the existing Industry Advisor instead of creating a new standalone screen.

Recommended changes:

1. keep the existing `Cities` and `Goods` tabs
2. replace `Chains` with a graph-first progression tab
3. optionally keep the current table behind a `Graph | Table` toggle during transition

Recommended tab contents:

1. small legend row
2. optional filter control
3. large scrollable graph panel
4. optional detail/help strip for the selected node

## Proposed Data Model

The current tuple constants are enough for the table, but not ideal for a graph renderer.

Create a dedicated flow-data module, for example:

- `CvIndustryFlowData.py`

That module should define explicit nodes and edges.

### Node Types

1. raw bonus
2. processor building
3. synthetic bonus
4. composite building
5. corporation

### Node Fields

Each node should carry:

1. stable node id
2. node type
3. underlying game type string such as `BONUS_*`, `BUILDING_*`, or `CORPORATION_*`
4. `gridX`
5. `gridY`
6. button path or a way to derive it
7. display label

### Edge Types

1. raw resource -> processor
2. processor -> synthetic good
3. synthetic good -> composite industry
4. composite industry -> corporation

### Layout Rule

Use hand-authored coordinates, exactly like the tech tree.

Do not attempt automatic graph layout in the first pass.

The graph is small enough that manual placement will be:

1. faster to implement
2. easier to tune
3. more stable across resolutions

## Corporation Nuance That The Graph Must Respect

The current Python table treats corporations mostly as consumers of synthetic goods.

That is not the full rule set anymore.

The actual game data and DLL logic now also require active composite industries from a founding set.

Corporation founding rules are driven by:

1. `FoundingBuildingClasses`
2. `iFoundingMinActiveBuildingClasses`
3. `PrereqBonuses`

in:

- `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/GameInfo/CIV4CorporationInfo.xml`

and enforced in DLL logic in:

- `third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvPlayer.cpp`
- `third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvCity.cpp`

Implication:

The graph should show corporations as the last stage of the chain, but should also reflect that they
depend on:

1. empire-level active composite industry presence for founding
2. synthetic goods for ongoing inputs

This is the biggest place where the current table model is too simple.

## Recommended Architecture

### 1. Split Data From Screen Code

Move the supply-chain definitions out of `CvIndustryAdvisor.py`.

Expected result:

1. cleaner screen code
2. explicit graph structure
3. easier filtering
4. easier validation against XML/DLL rules

### 2. Build A Reusable Flow Renderer

Create a renderer module, for example:

- `CvIndustryFlowRenderer.py`

Responsibilities:

1. create the scroll panel
2. render node panels at manual grid coordinates
3. draw arrows between nodes
4. apply node colors from current game state
5. own graph widget naming and cleanup

This module should be a port of the tech chooser's rendering kernel, but generalized so it accepts:

1. arbitrary node list
2. arbitrary edge list
3. custom per-node widgets
4. custom color states

### 3. Keep Screen Ownership In `CvIndustryAdvisor`

`CvIndustryAdvisor.py` should remain responsible for:

1. tab switching
2. overall screen shell
3. filter selection
4. active player lookup
5. delegating the graph area to the renderer

### 4. Reuse Tech Tree Visual Language

Use:

1. `PanelStyles.PANEL_STYLE_TECH`
2. the stock arrow art
3. similar spacing and left-to-right progression

Avoid:

1. tech-specific buttons or widgets
2. research queue text
3. Advanced Start logic
4. full-screen chooser dimensions

## State And Color Model

The graph is most useful if it communicates state immediately.

Recommended node states:

1. active now
2. constructible now
3. visible but missing inputs
4. not yet available

Recommended colors:

1. green for active
2. cyan for constructible now
3. blue or muted blue for visible but not active
4. red for unavailable

Interpretation by node type:

- raw resources: owned and connected vs not owned
- processors: built and locally active vs visible but not buildable yet
- synthetic goods: currently produced somewhere vs not produced
- composites: active vs inactive due to missing network goods vs not buildable
- corporations: founding available now vs blocked by missing active composite count or missing goods

## Availability Logic

The graph should try to reflect real game state, not just static relationships.

### Buildings

For buildings, prefer using the game's own checks through the Python interfaces where possible, such
as city `canConstruct(...)`, instead of duplicating rules in Python.

### Synthetic Goods

Synthetic goods should be marked active if the player is currently producing or holding them through
the existing industry system.

### Corporations

Corporation state needs two separate concepts:

1. founding eligibility
2. input support

The founding state should reflect real corporation prerequisites, including minimum active founding
building classes. If the necessary Python accessors are not currently exposed for all of that data,
the first pass can use a Python-side mirror of the XML setup.

## Filtering

Filtering should be included in the first implementation, otherwise the all-up graph will still be
too busy.

Recommended filters:

1. `All Chains`
2. one filter per corporation family
3. maybe one filter per broad branch later, such as `Food`, `Prestige`, `Performance`, `Stone`

Filtering should prune the node and edge lists before rendering. It should not render the full graph
and merely hide widgets afterward.

## Layout Guidance

The graph should preserve the basic mental model:

1. raw bonuses on the far left
2. processing buildings next
3. synthetic goods in the middle
4. composite industries next
5. corporations on the far right

Suggested row grouping:

1. provisions and hospitality
2. aromatics and celebration
3. textiles and regalia
4. metals and treasury
5. maritime and curios
6. performance and media
7. marble and antiquities

The goal is not perfect symmetry. The goal is readable branch identity.

## Implementation Sequence

### Phase 1: Preparation

1. vendor the stock chooser file into the mod tree for local reference
2. identify the chooser code to port directly
3. define the graph data model

### Phase 2: Data Extraction

1. move supply-chain constants into a dedicated module
2. add explicit graph nodes and edges
3. add hand-authored grid coordinates
4. add a fuller corporation representation that matches XML rules

### Phase 3: Renderer

1. create the graph renderer module
2. port chooser geometry helpers
3. port arrow drawing using the existing arrow art
4. port node panel construction using `PANEL_STYLE_TECH`

### Phase 4: Screen Integration

1. replace the current chains table with the graph panel
2. add a legend
3. add filtering
4. optionally keep a fallback table toggle during transition

### Phase 5: State Wiring

1. compute player ownership and availability states
2. color nodes correctly
3. support pedia jumps from node icons
4. add tooltip text where needed

### Phase 6: Cleanup

1. remove obsolete table-only helpers if no longer needed
2. keep the data definitions separate from rendering
3. document any remaining Python visibility gaps

## Risks

### 1. Chooser Code Is Not Fully Portable As-Is

The chooser is heavily coupled to tech data and old screen assumptions. Some adaptation is guaranteed.

### 2. Resolution Behavior

The stock chooser is designed around a fixed-size screen. The Industry Advisor is already using
dynamic resolution. The renderer will need to preserve tech-tree feel without inheriting a hard-coded
`1024x768` layout.

### 3. Corporation Rules Are Easy To Misstate

The graph must not imply that corporations depend only on synthetic bonuses. They also depend on
active composite founding sets at the empire level.

### 4. Widget Count And Cleanup

The graph will create many more widgets than the current table tab. Widget naming and deletion need
to stay disciplined to avoid stale UI artifacts when switching tabs.

### 5. Overcrowding In The Full View

Even with graph rendering, the all-up industry web can get dense. Filtering is not optional polish.

## Deliberate Non-Goals For The First Pass

1. no automatic graph layout
2. no new DLL work just for the screen
3. no attempt to replace the actual tech chooser with a shared engine
4. no animated routing or fancy transitions
5. no new XML schema work

## Validation Checklist For Future Work

When this is eventually implemented, validate:

1. `1024x768` behavior
2. widescreen behavior
3. repeated tab switching and widget cleanup
4. one complete branch such as Marble from raw bonus through corporation
5. one complete branch such as Performance from raw bonus through corporation
6. node colors after building construction, trade connection loss, and restoration
7. corporation node state when composite founding thresholds are and are not met
8. pedia jump targets from bonus, building, and corporation nodes

## Bottom Line

This is feasible and should produce a much better explanation of the industry's progression rules.

The right approach is:

1. keep the Industry Advisor screen
2. port the tech chooser's graph-rendering mechanics
3. drive them from industry-specific node and edge data
4. reflect the real corporation rules, not the simplified current table model

If this work is picked up later, the best first deliverable is a graph-first `Chains` tab with a
fallback table toggle until the graph is proven stable.
