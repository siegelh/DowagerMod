# Buff Environmentalism Civic

- Status: `draft`
- Owner / agent: Symphony Implementer
- Last updated: `2026-03-13`

## Problem Statement

- Task: Design a concrete, implementation-ready proposal to make the Environmentalism civic attractive by removing its crippling trade-route penalty and by adding incentives to farm tiles and grow city populations.
- Current observed behavior: In `CIV4CivicInfos.xml`, `CIVIC_ENVIRONMENTALISM` applies +10% food yield and +1  to scientist output, but it also carries +25% corporation maintenance, -20% military production, `bNoForeignCorporations = 1`, and an extreme `TradeYieldModifiers` commerce penalty of -100%. Its only tile-centric perks touch Forest Preserves, Windmills, and Watermills—nothing nudges players toward farms, and the civic actively destroys trade-route value.
- Why this is a real repo/code problem: Compared to Free Market and State Property, Environmentalism currently deletes a major commerce pillar while offering no compensating economy or growth levers, so late-game players simply never adopt it. The issue explicitly asks for a better plan.

## Why This Matters

- User or gameplay impact: Without a viable green economy choice, tall empire players lack a civic that rewards feature preservation, food-focused infrastructure, or megacity play. Fixing this keeps the late-game civic column diverse.
- Maintenance / workflow / agent impact: The change is strictly XML/text, so once the plan is approved we can implement and validate via the standard gate without touching DLL/Python.

## Scope

- In scope:
  - Updating `CIV4CivicInfos.xml` values for `CIVIC_ENVIRONMENTALISM`.
  - Updating the corresponding Civilopedia/strategy text so players understand the new incentives.
- Out of scope:
  - Rebalancing other Economy civics (Free Market, State Property, etc.).
  - Touching DLL logic or adding new mechanic hooks beyond the existing XML surface.

## Non-Goals

- Not changing: Other civic options or corporation mechanics unless Environmentalism directly references them.
- Not changing: Art assets, advisors, or installer content.

## Trusted Sources Of Truth

- Primary code/config/scripts:
  - `CoreFiles/.../Assets/XML/GameInfo/CIV4CivicInfos.xml`
  - `CoreFiles/.../Assets/XML/Text/CIV4GameText_Civics.xml` (exact text key TBD after inspecting live file)
- Runtime entrypoints/import paths to verify:
  - None beyond the BtS XML civic definitions.
- Validation scripts/tests/hooks:
  - `.\tools\test_gate.ps1`
  - Manual smoke as outlined in `docs/MANUAL_SMOKE_TESTS.md` after XML changes.

## Existing Docs / Plans Trust Review

- Reviewed docs/plans:
  - `README.md`, `AGENTS.md`, `WORKFLOW.md`, `ARCHITECTURE.md`, `docs/index.md`, `docs/TESTING_WORKFLOW.md`, `docs/MANUAL_SMOKE_TESTS.md`
- Classification:
  - All of the above are `trusted for this task` and matched the current repo state.
- Conflicts with code/config/scripts: None observed; XML confirmed Environmentalism penalties described in the issue.

## Potentially Stale Or Conflicting Materials

None encountered—the civic behavior is driven directly from the XML we inspected.

## Affected Files / Directories

- Primary implementation paths:
  - `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/GameInfo/CIV4CivicInfos.xml`
  - `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Text/*Civics*.xml` (Civilopedia + Strategy text)
- Adjacent paths to inspect:
  - `CoreFiles/.../Assets/XML/Text/CIV4GameText_Strategy.xml` (wherever `TXT_KEY_CIVIC_ENVIRONMENTALISM_STRATEGY` resides)
- Paths to avoid unless required:
  - DLL source (`third_party/...`) and non-BtS asset roots.

## Assumptions That Need Human Confirmation

- Assumption: Stacking a +1 food Farm bonus onto Environmentalism (in addition to the existing Caste System +1 farm food) is acceptable power-wise; this is key to making farms the dominant tile choice.
  - Why it matters: If stacking is too strong we may need a softer +15% global food modifier instead.
  - What changes if false: We pivot to a smaller +10% farm yield plus health bonuses rather than a flat +1 food.
- Assumption: Keeping `bNoForeignCorporations = 1` is still desired thematically.
  - Why it matters: If we also remove the foreign-corp ban, we must rebalance corp maintenance to avoid runaway corp spam.
  - What changes if false: Revert `bNoForeignCorporations` and possibly keep a mild corp maintenance penalty to differentiate Environmentalism from Free Market.

## Proposed Implementation Steps

1. Verify live entrypoints, imports, runtime paths, and active asset roots. ✅ (done during investigation)
2. Confirm trusted sources and classify stale/conflicting materials. ✅
3. Implement the smallest change that solves the problem (outlined below).
4. Update Civilopedia/strategy text to document the new bonuses.
5. Validate with `.\tools\test_gate.ps1` and run the minimum manual smoke test (load a late-game save, adopt Environmentalism, confirm yields, and inspect city screen trade routes).

### Task-Specific Steps

1. **Baseline Viability Tweaks**
   - Zero out the current `TradeYieldModifiers` penalty (set the commerce entry from `-100` to `0` so routes function again).
   - Lower `iCorporationMaintenanceModifier` from `+25` to `0` (neutral) so green economies do not suffer double taxation versus Free Market's `-35`.
   - Keep `bNoForeignCorporations = 1` for thematic differentiation unless playtesting proves it too punishing.
2. **Farm & Growth Incentives**
   - Add an `ImprovementYieldChange` entry granting `IMPROVEMENT_FARM` `[1, 0, 0]` (global +1 food on farms). This directly answers the issue ask to “incentivize farms and city growth.”
   - Increase `iYieldModifiers` food bonus from `+10%` to `+15%` to further reward tall play without overhauling other yields.
   - Add `FeatureHappinessChanges` for `FEATURE_FOREST` and `FEATURE_JUNGLE` at `+1` happiness each inside city tiles to reinforce preserving green features around farm belts (optional if concern about jungle positivity).
3. **Population Support & Text Updates**
   - Raise `iExtraHealth` from `0` to `+2` and extend the existing `BuildingHealthChanges` list with `BUILDINGCLASS_RECYCLING_CENTER` (+2) so large cities can sustain their added population.
   - Update `TXT_KEY_CIVIC_ENVIRONMENTALISM` Civilopedia and `TXT_KEY_CIVIC_ENVIRONMENTALISM_STRATEGY` strings to mention:
     - No more trade-route penalty.
     - +1 Food on farms, stronger food modifier, and extra health.
     - Forest/jungle happiness if that hook ships.
4. **Validation**
   - Run `.\tools\test_gate.ps1` (covers XML schema + changed-file validation).
   - Manual smoke: install to live tree, load/post-Medicine save, switch to Environmentalism, verify:
     - Trade routes produce commerce.
     - Farms show +1 food (stacking correctly with Biology/Caste).
     - City health totals reflect the new bonuses.

## Validation Plan

- Required automated checks:
  - `.\tools\test_gate.ps1`
- Required manual smoke test:
  - Follow `docs/MANUAL_SMOKE_TESTS.md` focusing on the civic switch, farm yields, and trade routes.
- Validation blocked or not yet runnable:
  - None; both XML gate and manual test are available locally.

## Documentation Updates Required

- Update whichever text file houses `TXT_KEY_CIVIC_ENVIRONMENTALISM` and `_STRATEGY`.
- If Feature happiness is added, note it briefly in `docs/ARCHITECTURE.md` “Known civic mechanics” section in a future doc pass (optional).

## Risks / Rollback

- Main risks:
  - Over-buffing farms when stacked with Caste System or Biology.
  - Removing corp maintenance penalty might make Environmentalism the strict default for corp-heavy empires if `bNoForeignCorporations` is also dropped later.
- Likely failure modes:
  - Misordered `ImprovementYieldChange` entries causing XML validation errors.
  - Forgetting to update Civilopedia text, leading to player confusion.
- Safe rollback approach:
  - Revert the `CIV4CivicInfos.xml` diff and regenerate text from git history; no DLL or binary changes involved.

## Open Questions

- Should Environmentalism also grant a small commerce boost to coastal improvements (representing carbon pricing) to keep hybrid economies viable, or is the farm plan sufficient?
- Do we want to keep `bNoForeignCorporations = 1`? If testers find it too punishing even with neutral corp maintenance, we may need to revisit.

## Completion Checklist

- [ ] Trusted sources of truth were verified from code/config/scripts. (XML inspected; keep box unchecked until main work finishes.)
- [ ] Existing docs/plans in this area were reviewed and classified for trustworthiness.
- [ ] Assumptions needing human confirmation were recorded.
- [ ] Implementation steps were completed or explicitly deferred.
- [ ] Required validation ran and results were recorded.
- [ ] Required manual smoke test ran, or the blocker was escalated.
- [ ] Related docs were updated or explicitly deferred with reason.
- [ ] Residual risks and open questions were summarized.

## Final Outcome Summary

- What changed: Plan only—no XML edits yet. The above steps spell out the mechanical changes required to buff Environmentalism.
- Validation performed: None yet; to run after implementation.
- Docs updated: This plan file.
- Remaining risks: Need confirmation on farm stacking power level and the fate of `bNoForeignCorporations`.
- Follow-up tasks: Implement XML + text changes per plan, validate, and update docs/issue once done.
