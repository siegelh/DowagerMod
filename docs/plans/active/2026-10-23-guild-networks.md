# Guild Networks and Royal Armaments Company

- Status: `in_progress`
- Owner / agent: GitHub Copilot CLI
- Last updated: `2026-10-23`
- Source commit: `08605ed46fcb234fe65b319aa140c9e970959760`
- Delivery branch: `agent-baseline-leader-chatter-sol-leader-update-visual-overhaul-new-leaders-guilds`

## Problem Statement

- Task: add an early institutional guild layer, three missing refined-resource
  chains, and a late-game destination for those goods.
- Current observed behavior: corporations provide a late network layer, but
  cities cannot create scarce processor-bound guild branches. Iron, copper,
  and horses also lack the approved processed goods.
- Why this is a real repo/code problem: guild ownership is per civilization,
  while corporations are globally unique and cannot preserve the required
  sponsor and processor identity. The mechanic therefore needs native state
  rather than a corporation reskin.

## Why This Matters

- Guilds make local processors strategically important before corporations.
- Three licenses force meaningful domestic-versus-foreign placement choices.
- Civic, diplomacy, conquest, and processor state create readable network
  behavior instead of permanent passive bonuses.
- Royal Armaments gives the new military goods a distinct late-game payoff.

## Scope

- Add Iron Foundry -> Forged Iron, Coppersmiths' Hall -> Copperware, and Stud
  Farm -> Trained Mounts.
- Add five data-driven guilds with per-player headquarters, Guild Houses, and
  guild-specific emissaries.
- Add native sponsor/processor state, license accounting, activity/dormancy,
  founding, spread, removal, capture/transfer behavior, AI, and persistence.
- Add guild civic and diplomacy behavior.
- Add a Guilds Industry Advisor tab and Civilopedia category.
- Activate `CORPORATION_7` as the Royal Armaments Company.
- Add tests, documentation, art/reference audits, and manual acceptance steps.

## Non-Goals

- Do not reuse corporation identities or competition for guilds.
- Guild Houses do not become corporation branches.
- Do not add a stone chain or more than the five approved guilds.
- Do not add unlimited emissaries or resource-count guild scaling.
- Do not edit base Assets, Warlords, generated installer output, backup DLLs,
  or `petromod_v1`.
- Pre-branch saves are not supported because appended InfoTypes alter
  engine-sized arrays. Saves created by this branch must reload correctly.

## Trusted Sources Of Truth

- BtS XML:
  `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML`
- BtS Python:
  `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/Python`
- DLL:
  `third_party/beyond-the-sword-sdk/CvGameCoreDLL`
- Industry UI:
  `CvIndustryAdvisor.py`, `CvIndustryFlowData.py`,
  `CvIndustryFlowRenderer.py`
- Validation:
  `tools/test_gate.ps1`, `tools/test_xml.ps1`, `tools/test_full.ps1`

## Existing Docs / Plans Trust Review

- Issues #154 and #155: useful product context; this plan is the approved
  implementation contract.
- `ARCHITECTURE.md`, `docs/TESTING_WORKFLOW.md`, and
  `docs/MANUAL_SMOKE_TESTS.md`: trusted when corroborated by live code/scripts.
- Older idea notes and archived plans: historical context only.

## Confirmed Gameplay Contract

### Ownership, Headquarters, And Licenses

- Every living major civilization may own one headquarters of each guild.
- Headquarters are national institutions and may coexist in one city.
- Headquarters unlock at `TECH_GUILDS` and are founded by the mapped Great
  Person through the normal construct mission.
- Each `(sponsor, guild)` network has three licenses.
- `available = max(0, 3 - sponsored branches - living emissaries)`.
- Founding or re-founding grants only currently unused emissaries.
- Replacement emissaries cost 100 production and require an active sponsor HQ.
- Each HQ has +2 Culture, +2 matching Great Person points, one matching
  specialist slot, and a dynamic return from active sponsored branches.

| Guild | Founder | Eligible processed goods | Guild House | HQ return per active branch |
|---|---|---|---|---|
| Artificers and Farriers | Great Engineer | Forged Iron, Copperware, Trained Mounts, Cut Gems, Gold Bullion, Worked Silver, Ivory Carvings, Marble Statuary | +25% Production, 2 Engineer slots | +1 Production |
| Merchant Adventurers | Great Merchant | Fine Silk, Fine Dyes, Fine Furs, Cut Gems, Gold Bullion, Worked Silver, Spice Blends, Vintage Wine | +2 Trade Routes, +25% Gold, 2 Merchant slots | +2 Gold |
| Apothecaries and Chandlers | Great Scientist | Temple Incense, Spice Blends, Confections, Fruit Preserves, Lamp Oil, Vintage Wine | +25% Research, +3 Health, 2 Scientist slots | +2 Research |
| Victuallers | Great Merchant | Flour, Cured Meats, Preserved Seafood, Fruit Preserves, Confections, Vintage Wine | +3 Food, +3 Health, 2 Merchant slots | +1 Food |
| Fellowship of Pageantry | Great Artist | Stage Plays, Fine Silk, Fine Dyes, Ivory Carvings, Marble Statuary, Cut Gems | +25% Culture, +3 Happiness, 2 Artist slots | +2 Culture |

- Free Market increases the summed HQ branch return by 50%, with integer
  truncation after summing the network.

### Branch Identity And Activity

- Each branch stores its guild, sponsor, and supporting processor building
  class.
- A city may have one branch of each guild, but each processor may support
  only one branch.
- Multiple branches may coexist only when they claim distinct processors.
- The selected processor must physically exist and be locally active.
- One eligible processor spreads directly; multiple candidates use a
  synchronized native selection popup.
- The emissary is consumed only after final validation and successful creation.
- A branch is active only when the sponsor lives, has an active HQ, is not
  using State Property, the Guild House and metadata are valid, the selected
  processor is active, and foreign-host diplomacy/civic requirements pass.
- Temporary invalidity makes a branch dormant without releasing its license.
- Dormant branches provide no local benefit and no HQ return.
- Removing the selected processor destroys the branch and releases its license.

### Diplomacy, Civics, Capture, Transfer, And Removal

- Foreign spread requires peace, Open Borders, and physical access.
- AI foreign spread requires Pleased or Friendly relations.
- Decentralization and Environmentalism are neutral.
- Mercantilism permits domestic networks only and makes foreign branches
  dormant.
- Free Market grants the HQ return bonus.
- State Property cannot found, train, spread, or actively own guild networks.
  Owned networks become dormant, while foreign branches hosted in State
  Property cities may remain active.
- Military capture destroys every guild HQ and branch in the captured city.
- Remote branches survive HQ destruction as dormant, license-occupying state.
- Peaceful transfer preserves normal branch metadata.
- A peacefully transferred HQ relocates free to the sponsor capital, or the
  highest-population valid remaining city with stable city-ID tie-breaking.
- Sponsor elimination removes its remaining branches.
- Hosts may revoke and sponsors may withdraw branches without an automatic
  diplomatic penalty.

## New Processor Chains

| Processor | Technology | Required building | Local resource | Good | Effect |
|---|---|---|---|---|---|
| Iron Foundry | Metal Casting | Forge | Iron | Forged Iron | +2 Production, Engineer slot, -1 Health |
| Coppersmiths' Hall | Metal Casting | Forge | Copper | Copperware | +1 Production, +2 Gold, Engineer slot |
| Stud Farm | Horseback Riding | Stable | Horses | Trained Mounts | +1 Food, +1 Production, +1 Health |

- All cost 120 production and use the current local-resource activation and
  industry-cap pipeline.

## Royal Armaments Company

- Activate `CORPORATION_7` as Royal Armaments Company.
- Great Engineer founder; Rifling corporation prerequisite.
- Inputs: Forged Iron, Copperware, and Trained Mounts.
- Output: +1 Production per distinct active input, up to +3.
- Active branch cities grant fixed +2 experience to combat-capable units.
- Suggested values: spread factor 170, spread cost 60, maintenance 110, and
  +4 HQ Gold.
- Founding requires all three active composites:
  - Arsenal: Forged Iron + Copperware, Steel, 150 production, +3 Production,
    +10% military production.
  - Remount Depot: Forged Iron + Trained Mounts, Military Tradition,
    150 production, +2 Production, +1 Happiness, +10% military production.
  - Military Outfitters: Copperware + Trained Mounts, Rifling,
    150 production, +2 Production, +2 Gold, +10% military production.
- Add a neutral-default corporation military-experience XML field and apply it
  only for active corporations and combat-capable trained units.

## Native Architecture

- Add `GuildTypes`, `NO_GUILD`, and `CvGuildInfo`.
- Load `XML/GameInfo/CIV4GuildInfo.xml` through the game schema and global XML
  loader.
- `CvGuildInfo` stores text/button, prerequisite technology, founder/HQ/house/
  emissary classes, cap, eligible processor classes, and per-branch HQ yield
  and commerce arrays.
- Expose guild infos and enum values to Python.
- Add per-city sponsor and supporting-processor arrays indexed by guild.
- Derive license totals from live branches and emissaries; do not serialize a
  duplicate player ledger.
- Centralize branch validity, activity reason, processor candidates, HQ lookup,
  license queries, creation/removal, and network refresh.
- Keep dormant Guild Houses visible but remove/reapply their static effects
  through the existing active-building transition and `processBuilding`.
- Add `MISSION_ESTABLISH_GUILD_BRANCH`; `iData1` is guild and `iData2` is the
  selected processor or `NO_BUILDINGCLASS`.
- Add a synchronized processor-choice popup using the same candidate evaluator
  as AI/help/execution.
- Use a reserved ModNet opcode for Advisor revoke/withdraw requests; native
  code validates and mutates state on every client.
- Add a new `CvCity` expansion bit and serialize sponsor/processor arrays.
- Reconcile impossible metadata and refresh activity/HQ returns after load.

## AI Contract

- Great People compare guild HQ value with normal actions and may re-found a
  network when surviving branches justify it.
- Emissaries are produced only with an active HQ, a free license, and useful
  targets.
- Targeting uses native legality, prioritizes productive domestic cities, and
  permits only Pleased/Friendly foreign partners.
- Processor selection is deterministic and avoids wasting flexible processors.
- Building/civic AI values actual active guild and Royal Armaments effects.
- Corporation 7 uses normal founder, executive, and spread behavior.

## UI, Civilopedia, Text, And Art

- Add a fourth Industry Advisor tab showing sponsor, HQ state, cap usage,
  emissaries, active/dormant branches, hosts, processors, dormancy reasons,
  benefits, and valid revoke/withdraw actions.
- Preserve Cities/Goods/Chains behavior, flow routing, and corporation filters.
- Add a Guilds Civilopedia category/page with complete mechanics and cross-links.
- Add exact help and English text for new buildings, units, mission, civics,
  states, errors, and Royal Armaments.
- Reuse verified repository-owned caravan, guild/civic, arsenal, and military
  assets with distinct buttons and no external runtime paths.

## Proposed Implementation Steps

1. Create the clean worktree at the pinned source commit and record this plan.
2. Add the three processor chains and Royal Armaments content/mechanics.
3. Add guild schema/info/XML/content and Python exposure.
4. Add authoritative city/network state, persistence, civic/diplomatic
   refresh, capture/transfer, and management operations.
5. Add synchronized establishment mission and processor popup.
6. Add Great Person, emissary, building, civic, and corporation AI.
7. Add Advisor, Civilopedia, help, text, and complete art wiring.
8. Add tests/docs, run all gates, record manual blockers/results, and push.

## Validation Plan

- Focused tests cover content mappings, Armaments thresholds/XP, license
  accounting, processor exclusivity, civic/diplomacy activity, HQ returns,
  transfer/capture/elimination, serialization, mission/popup/AI bindings,
  Advisor/Pedia registration, art/text references, and flow UI preservation.
- Run:
  - `.\tools\test_gate.ps1 -CheckDll`
  - `.\tools\test_xml.ps1 -All`
  - `.\tools\test_full.ps1`
  - `git diff --check`
- Manual acceptance covers fresh-game loading, all processors and guilds,
  popup choices, cap behavior, dormancy/destruction/re-founding, civics,
  diplomacy, capture/transfer, save/reload, Advisor/Pedia at 1024 and
  widescreen, Royal Armaments, AI autoplay, art, and a two-client OOS pass.

## Documentation Updates Required

- Update `ARCHITECTURE.md` for guild state and runtime paths.
- Update `docs/MANUAL_SMOKE_TESTS.md` with the acceptance matrix.
- Keep this plan's status and validation results current.
- Keep `docs/index.md` linked to this active plan.

## Risks / Rollback

- Centralize activity transitions to prevent duplicate building effects.
- Derive license counts to prevent re-founding exploits.
- Synchronize every player choice and mutation to avoid OOS.
- Snapshot guild metadata before city reconstruction on capture/transfer.
- Require fresh games and test branch-created save read/write symmetry.
- Use known-safe bundled art and audit every dependency.
- Roll back by reverting the guild commits; do not touch source-worktree or
  unrelated expansion history.

## Resolved Assumptions

- Royal Armaments ships with guilds and uses fixed +2 military experience.
- Peacefully transferred HQs relocate automatically and free.
- Voluntary branch removal has no diplomatic penalty.
- Balance constants remain XML-driven.
- New-branch save/reload is mandatory; pre-branch saves are unsupported.

## Completion Checklist

- [x] Clean target worktree created directly from `08605ed46`.
- [x] Trusted runtime paths and design assumptions verified.
- [ ] Three processor chains and Royal Armaments implemented.
- [ ] Five guild networks and native state implemented.
- [ ] AI, Advisor, Civilopedia, help, text, and art implemented.
- [ ] Required automated gates pass.
- [ ] New-branch save/reload verified.
- [ ] Manual gameplay/art/AI/UI results recorded.
- [ ] Two-client OOS result recorded or explicitly blocks readiness.
- [ ] Exact guild branch pushed to `origin`.

## Final Outcome Summary

- What changed: implementation in progress.
- Validation performed: clean branch/worktree baseline verified.
- Docs updated: this active plan and docs index.
- Remaining risks: native implementation and all runtime acceptance remain.
- Follow-up tasks: execute the implementation and validation sequence above.
