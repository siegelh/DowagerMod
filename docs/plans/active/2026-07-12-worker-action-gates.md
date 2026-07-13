# Remaining-roster worker-action gates

Date: 2026-07-12  
Owner: `worker-action-gates`  
Scope: static feasibility audit only; no gameplay, XML, DLL, or art changes.

## Verdict

**No-art-no-action: REJECT every new worker action in the frozen 32-package
matrix.** No non-Keep package has both a package-owned action proposal and a
complete, tracked, correctly gated repository tile-art package.

The existing Polynesian Reef Works action is **functionally wired but not
release-approved**. Its BuildInfo, ImprovementInfo, Wayfinder permission,
mission execution, AI selection, ownership, pillage, and no-upgrade paths are
connected. Release approval is blocked by:

1. no repository-closed tile model package (the referenced stock Nets NIF/KFM
   and direct button are absent, and the atlas present in this worktree is not
   tracked);
2. no resource prohibition for human use, despite the Reef AI explicitly
   excluding bonus tiles;
3. player-level city AI can rank the build for every civilization because the
   build itself has no civilization gate;
4. required in-game render, interaction, AI, save/reload, and multiplayer proof
   is not available from static inspection.

This supersedes the unsupported statement that Reef Works has a “complete
custom build/art/AI contract” in
`docs/plans/active/2026-07-12-remaining-roster-audit.md:398-403`.

## Existing Reef Works closure matrix

| Gate | Evidence | Result |
|---|---|---|
| Build -> improvement | `CIV4BuildInfos.xml:817-834` maps `BUILD_POLYNESIA_REEF_WORKS_BTG` to the Reef Works improvement; Fishing, 300 time, zero cost, non-consuming, build mission, Fishing Boats button. | APPROVE |
| Improvement legality | `CIV4ImprovementInfos.xml:1996-2053` is water-only, valid on Coast/Ocean, non-permanent, inside borders, +1 food/+1 production. `CvPlot.cpp:2060-2160` enforces water/terrain/feature validity. | APPROVE with resource defect |
| Unit permission | `CIV4UnitInfos.xml:29122-29202` gives only the Wayfinder Canoe the Reef build in live BtS XML; it is a sea worker with Fishing prerequisite and work rate 100. Polynesia maps `UNITCLASS_WORKBOAT` to it at `CIV4CivilizationInfos.xml:3977-3980`. | APPROVE |
| Tech and ownership | `CvPlayer.cpp:6111-6143` enforces Fishing; `CvPlot.cpp:2210-2265` rejects non-owner culture because `bOutsideBorders=0`; `CvUnit.cpp:6359-6525` checks unit permission, player legality, and domain. | APPROVE |
| Terrain/features | Coast and Ocean are valid; city and impassable plots are rejected; `NoImprovement` features are rejected (`CvPlot.cpp:2060-2149`). Empty `FeatureStructs` removes nothing. | APPROVE |
| Resources | Terrain validity still makes resource Coast/Ocean legal, and `CvPlot::canBuild` permits replacement of a non-permanent existing improvement (`CvPlot.cpp:2210-2245`). AI skips every bonus tile (`CvUnitAI.cpp:14239-14246`; `CvCityAI.cpp:4428-4431`). | **REJECT** |
| Mission/action/help | XML loader assigns `MISSION_BUILD` (`CvXMLLoadUtilitySet.cpp:1067`); `CvUnit.cpp:6527-6544` executes build progress and preserves the unit because `bKill=0`; action hover calculates yield deltas and legality (`CvDLLWidgetData.cpp:2474-2565`). Text keys exist at `BTG_Polynesia_Text.xml:17-27`. Build `<Help/>` is empty and the pedia says production but omits the XML food yield. | CONDITIONAL |
| AI valuation | `AI_bestPlotBuild` ranks legal improvements from yields/time (`CvCityAI.cpp:7715-7895`); Reef adds food/production. Polynesian demand and unit execution are gated by unit permission and positive city best-build value (`CvCityAI.cpp:4387-4449`; `CvUnitAI.cpp:14193-14298`). | APPROVE for Polynesia |
| AI isolation | `AI_bestPlotBuild` calls player-level `canBuild`, not unit-level `canBuild`; the Reef build has no civ gate (`CvPlayer.cpp:6111-6143`). Non-Polynesian city AI can therefore rank an inaccessible Reef build, although Reef sea-worker demand is separately gated. | **REJECT** |
| Upgrade | Empty `ImprovementUpgrade` means no upgrade target; `CvPlot.cpp:453-475` only advances improvements with a target. | APPROVE |
| Pillage | Non-permanent improvement is pillageable; empty `ImprovementPillage` resolves to removal (`CvUnit.cpp:4439-4585`). `iPillageGold=5` supplies the base amount. | APPROVE |
| Ownership | Building is own-culture only. Ownership changes transfer improvement accounting without deleting the improvement (`CvPlot.cpp:4563-4619`); subsequent rebuilding still follows the new owner’s unit/build legality. | APPROVE, manual transfer proof required |
| Tile art | `CIV4ArtDefines_Improvement.xml:64-70` references stock Nets NIF/KFM plus the Fishing Boats direct button/atlas cell. Nets NIF, Nets KFM, and `BuildFishingBoats.dds` are absent from all three repository asset layers. The 512x1024 DXT3 atlas found in the worktree is untracked. Embedded model textures cannot be audited because the NIF is absent. | **REJECT** |

## Non-Keep package approval matrix

| Package | Tier | Existing package-owned worker/tile action evidence | Decision |
|---|---|---|---|
| Washington | Targeted | None | REJECT NEW ACTION |
| Geronimo | Polish | None | REJECT NEW ACTION |
| Hammurabi | Targeted | None | REJECT NEW ACTION |
| Elizabeth | Targeted | None | REJECT NEW ACTION |
| Huayna Capac | Polish | Worker has stock actions and global XML permissions for Sphinx/Castle Town/Royal Station, but DLL civilization gates bind those actions to Egypt/Japan/Persia (`CvUnit.cpp:6367-6505`). No Incan action or tile package exists. | REJECT NEW ACTION |
| Wang Kon | Targeted | None | REJECT NEW ACTION |
| Asoka | Targeted | Fast Worker has the same cross-civ-gated permissions; no Mauryan action or tile package exists. | REJECT NEW ACTION |
| Genghis Khan | Targeted | Matrix removes a leaked Japan Castle Town trait yield; it does not grant a Mongol build action. | REJECT NEW ACTION |
| Sitting Bull | Targeted | None | REJECT NEW ACTION |
| Chinese Leader | Targeted | Matrix removes a Farm trait yield; stock Farm is not a new unique action. | REJECT NEW ACTION |
| Casimir | Polish | None | REJECT NEW ACTION |
| Salamasina | Polish | Existing Reef Works only; no new action. Static functional wiring passes, but resource/AI isolation and repository-art closure fail. | RETAIN FOR VALIDATION; REJECT RELEASE APPROVAL |
| Stalin | Major | None | REJECT NEW ACTION |
| Enrico Dandolo | Keep | Existing Venetian Merchant road and Grand Colosseum actions are explicitly preserved by user direction. No new action is proposed. | RETAIN EXISTING ACTIONS; REJECT NEW ACTION |
| Churchill | Targeted | None | REJECT NEW ACTION |
| Kublai Khan | Targeted | None | REJECT NEW ACTION |

The Sphinx, Japan Castle Town, and Persia Royal Station entries do have tracked
NIF, embedded texture, and direct-button closure, but they belong to other
civilizations and are hard-gated accordingly. Their incidental presence in
Huayna/Asoka worker build lists does not establish package ownership or justify
a new action.

## Manual proof still required

1. Normal/hover/pressed/disabled action-button states and hotkey `F`, including
   installed-game fallback to stock packed assets.
2. Enabled/disabled legality on owned/unowned/foreign Coast and Ocean, before
   and after Fishing, with seafood/oil/whale resources, existing improvements,
   impassable tiles, cities, and water features.
3. Construction animation/progress at normal and quick speeds; the Wayfinder
   must survive and repeat the action.
4. Reef tile rendering on Coast and Ocean at all zooms, low/high graphics,
   shader/non-shader paths, fogged/revealed state, worked/unworked state,
   adjacent copies, culture-border changes, and globe/strategic views.
5. Texture/model behavior during build completion, pillage/removal, ownership
   transfer, save/reload, and reload after graphics-option changes.
6. AI autoplay proving Wayfinder production, reachable target selection,
   resource avoidance, no overwrite loops, no stranded missions, bounded boat
   demand, and no inaccessible Reef ranking side effects for other civs.
7. Multiplayer host/client action visibility, completion, save/reload, and
   checksum stability.

## Approval rule

Do not add or approve a worker action until all of these are repository-closed:
BuildInfo, ImprovementInfo, unit/civilization permission, tech/terrain/resource
legality, mission/help/localization, AI valuation and execution, upgrade/pillage
and ownership behavior, tracked NIF/KFM/textures/buttons, plus recorded in-game
proof for every applicable render state.
