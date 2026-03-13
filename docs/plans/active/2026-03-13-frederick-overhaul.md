# Frederick Overhaul

- Status: `in_progress`
- Owner / agent: Symphony (ChatGPT)
- Last updated: `2026-03-13`

## Problem Statement

- Task: Apply the Detailed Overhaul v4 workflow to redesign Frederick (Germany) with new history-grounded mechanics and implement them in XML.
- Current observed behavior: Frederick still uses a legacy financial + GP trait, late industrial-only UB (Assembly Plant), and WW2-era UU emphasis that does not surface his 18th-century cameralist reforms.
- Why this is a real repo/code problem: The repo owners expect modernized, leader-specific mechanics that leverage the repo's extended XML channels, but Frederick's content is still largely stock BtS plus a custom trait with narrow scalar bonuses.

## Why This Matters

- User or gameplay impact: Frederick lacks a distinctive play loop despite being labeled "Ready" on the issue board; players cannot leverage Prussian bureaucracy or disciplined infantry.
- Maintenance / workflow / agent impact: Keeping a stale leader undermines the overhaul program and wastes the repo's extra XML hooks for traits and uniques.

## Scope

- In scope:
  - `CIV4LeaderHeadInfos.xml`, `CIV4TraitInfos.xml`, `CIV4CivilizationInfos.xml`, `CIV4BuildingInfos.xml`, `CIV4UnitInfos.xml`, `CIV4ArtDefines_Unit.xml`, BtS text files.
  - Git plan + documentation artifacts describing the new mechanics.
- In scope:
  - Repo-required testing via `tools/test_gate.ps1` after XML edits.

## Non-Goals

- Not changing:
  - DLL code unless XML cannot express the mechanic (plan is to stay XML-only so we can finish within the task window).
- Not changing:
  - Base `Assets` or `Warlords` trees beyond what BtS already overrides.

## Trusted Sources Of Truth

- Primary code/config/scripts:
  - `CoreFiles/.../Assets/XML/Civilizations/CIV4TraitInfos.xml`
  - `CoreFiles/.../Assets/XML/Buildings/CIV4BuildingInfos.xml`
  - `CoreFiles/.../Assets/XML/Units/CIV4UnitInfos.xml`
  - `CoreFiles/.../Assets/XML/Civilizations/CIV4CivilizationInfos.xml`
  - `CoreFiles/.../Assets/XML/Civilizations/CIV4LeaderHeadInfos.xml`
- Runtime entrypoints/import paths to verify:
  - Trait/tooltips via Civilopedia text (new `ZZZ_CIV4GameText_Frederick_Overhaul.xml`).
  - Art references for the new unit via `CIV4ArtDefines_Unit.xml`.
- Validation scripts/tests/hooks:
  - `.
tools\test_gate.ps1`

## Existing Docs / Plans Trust Review

- Reviewed docs/plans:
  - `README.md`, `AGENTS.md`, `WORKFLOW.md`, `ARCHITECTURE.md`, `docs/index.md`, `docs/TESTING_WORKFLOW.md`, `docs/MANUAL_SMOKE_TESTS.md`, `docs/LEADER_OVERHAUL_PLAN_OF_RECORD.md`, skill `detailed-overhaul-v4` references.
- Classification for each:
  - All marked `trusted for this task` because they describe repo workflow, architecture, and the patched leader methodology.
- Conflicts with code/config/scripts:
  - None observed so far.

## Potentially Stale Or Conflicting Materials

- Item: legacy Frederick trait text in vanilla BtS files.
  - Why it may be stale: describes stock Financial/Philosophical style power that no longer matches repo custom trait.
  - What code/config overrode or verified it: we will replace it with a new `ZZZ_` text file in BtS.
- Item: Base Germany uniques (Panzer + Assembly Plant) do not highlight Frederick's era.
  - Why it may be stale: they bias toward 20th century warfare only.
  - What code/config overrode or verified it: plan introduces an additional mid-game UU and a bureaucratic UB within BtS overrides.

## Affected Files / Directories

- Primary implementation paths:
  - `CoreFiles/.../Assets/XML/Civilizations/CIV4TraitInfos.xml`
  - `CoreFiles/.../Assets/XML/Civilizations/CIV4LeaderHeadInfos.xml`
  - `CoreFiles/.../Assets/XML/Civilizations/CIV4CivilizationInfos.xml`
  - `CoreFiles/.../Assets/XML/Buildings/CIV4BuildingInfos.xml`
  - `CoreFiles/.../Assets/XML/Units/CIV4UnitInfos.xml`
  - `CoreFiles/.../Assets/XML/Art/CIV4ArtDefines_Unit.xml`
  - `CoreFiles/.../Assets/XML/Text/ZZZ_CIV4GameText_Frederick_Overhaul.xml` (new)
- Adjacent paths to inspect:
  - `.../Assets/XML/Text/CIV4GameTextInfos_Objects.xml` for trait references.
  - `.../Assets/XML/Text/CIV4GameText_Civilopedia_BTS.xml` for biography updates if needed.
- Paths to avoid unless evidence requires them:
  - `CoreFiles/.../Assets/Assets/...` (stock mirror) and `Warlords` tree.

## Assumptions That Need Human Confirmation

- Assumption: Germany/Prussia both rely on the BtS override tree we are editing.
  - Why it matters: ensures new UB/UU appear for Frederick regardless of which Germany variant is selected.
  - What changes if false: would need to duplicate overrides again in whichever civ entry is actually exposed in UI.
- Assumption: Repo leadership is fine with retaining the Assembly Plant while adding a second UB (General Directory) to carry Frederick's bureaucratic signature.
  - Why it matters: determines whether we deprecate the Assembly Plant entirely.
  - What changes if false: would need to remove or heavily retune the Factory replacement and rebalance total power budget.

## Proposed Implementation Steps

1. Verify live entrypoints, imports, runtime paths, and active asset roots.
2. Confirm trusted sources and classify stale/conflicting materials in this area.
3. Implement the smallest change that solves the problem.
4. Update related docs/runbooks affected by the change.
5. Validate with repo test gates and required smoke testing.

### Task-Specific Steps

1. Produce a history-grounded overhaul spec using `detailed-overhaul-v4`, documenting sources, mechanics coverage, and the per-leader checklist (historical, gameplay, power budget, UU/UB verdicts, UI plan, AI notes).
2. Update XML:
   - Rebuild `TRAIT_FREDERICK` with cameralist yield/com commerce effects and Great People / Great General knobs.
   - Add the "General Directory" Courthouse replacement and wire it into German/Prussian civ entries.
   - Add the "Prussian Fusilier" Rifleman replacement, art define, and `Units` overrides.
   - Retune Frederick's leaderhead AI flavor and favorite civic.
3. Create `ZZZ_CIV4GameText_Frederick_Overhaul.xml` with new trait/UB/UU names, Civilopedia, and strategy blurbs plus UI surfacing for trait bullets.
4. Run `.
tools\test_gate.ps1` (XML gate) and document results; manual smoke test remains pending because gameplay validation requires a human install/run.

## Validation Plan

- Required automated checks: `.
tools\test_gate.ps1`
- Required repo scripts:
  - `.
tools\test_gate.ps1`
- Required manual smoke test:
  - Follow `docs/MANUAL_SMOKE_TESTS.md` after human install (not runnable in-agent).
- Validation blocked or not yet runnable:
  - Manual smoke pending.

## Documentation Updates Required

- Docs to update with the implementation:
  - `docs/plans/active/2026-03-13-frederick-overhaul.md` (this document, kept up-to-date during work).
  - Add new `ZZZ_` text file to document trait/UB/UU tooltips.
- Docs/plans to mark stale, historical, or superseded:
  - None yet; trait text lives entirely in XML.
- `docs/index.md` updates needed:
  - None (plan doc already under `docs/plans/active`).
- `ARCHITECTURE.md` / `WORKFLOW.md` / runbook updates needed:
  - None.

## Risks / Rollback

- Main risks:
  - Over-buffing farms/mills/shops via trait-level bonuses causing runaway midgame yields.
  - Text or art define typos causing XML validation failures.
- Likely failure modes:
  - Missing Civilopedia text keys for the new UB/UU/trait.
  - Forgetting to point both `CIVILIZATION_PRUSSIA` and `CIVILIZATION_GERMAN_EMPIRE` at the new uniques.
- Safe rollback approach:
  - Revert the XML/text files touched in this branch.
- Paths that should not be touched during rollback:
  - DLL source tree and installer scripts.

## Open Questions

- Question: Do both `CIVILIZATION_GERMAN_EMPIRE` and `CIVILIZATION_PRUSSIA` appear in-game, or is one a compatibility alias? (Plan: update both.)
- Question: Should the Assembly Plant remain part of Frederick's loadout? (Plan: keep it for now and focus on the new Courthouse UB.)

## Per-Leader Checklist (LEADER_OVERHAUL_PLAN_OF_RECORD)

- Historical thesis: Frederick II fused Prussia's cameralist bureaucracy with a canton-based standing army that could mobilize faster than any rival.
- Gameplay thesis: Hybrid tall-core empire that leans on watermills/workshops for science + production, spikes in midgame wars through disciplined gunpowder timing.
- Power budget thesis: Hybrid — meaningful trait economy plus UB/UU pair to carry visible mechanics.
- Trait channels selected: scalar (-35% upkeep, GP/GG modifiers), `ImprovementYieldChanges` (workshops + watermills), `ImprovementCityCommerceChangesWorked` (watermills + windmills), `SpecialistYieldChanges` (scientists), `SpecialistCommerceChanges` (engineers).
- UU decision: `KEEP` Panzer for late-game flavor, `ADD` Prussian Fusilier to express Frederick's 18th-century spike (Rifleman replacement with anti-gun bonuses).
- UB decision: `ADD` General Directory Courthouse replacement to highlight cameralist governance while preserving the Assembly Plant for industrial Germany.
- Unique improvement decision: `FORBIDDEN BY ISSUE` — no new tile improvement is proposed.
- Art sources used: reused in-repo `ART_DEF_BUILDING_COURTHOUSE` and `ART_DEF_UNIT_RIFLEMAN` (no external copy required after searching the workspace for Prussian-specific assets).
- UI clarity checks: new `ZZZ_CIV4GameText_Frederick_Overhaul.xml` overrides trait/UB/UU names, Civilopedia entries, and strategy blurbs with explicit numeric bullet points.
- AI impact notes: Trait pushes AI to value watermills/workshops (existing improvement logic applies), UB grants tangible military production + XP so city AI should prioritize it midgame, new fusilier remains in the standard Rifleman class so drafting/build logic still works while the anti-gun bonus encourages AI to trade into wars once Rifling is online.

## Completion Checklist

- [ ] Trusted sources of truth were verified from code/config/scripts.
- [ ] Existing docs/plans in this area were reviewed and classified for trustworthiness.
- [ ] Assumptions needing human confirmation were recorded.
- [ ] Implementation steps were completed or explicitly deferred.
- [ ] Required validation ran and results were recorded.
- [ ] Required manual smoke test ran, or the blocker was escalated.
- [ ] Related docs were updated or explicitly deferred with reason.
- [ ] Residual risks and open questions were summarized.

## Final Outcome Summary

- What changed:
- Validation performed:
- Docs updated:
- Remaining risks:
- Follow-up tasks:
