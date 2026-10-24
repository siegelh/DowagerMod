# Expansion Leader Balance and Research Campus Clustering

- Status: `implementation complete; installed-game validation pending`
- Owner / agent: GitHub Copilot
- Last updated: `2026-10-23`

## Problem Statement

- Task: Strengthen Ramkhamhaeng, David, Askia Muhammad, Hiram I, and Mongkut;
  preserve Piye; and redesign Great Scientist Research Campuses around adjacent
  clusters.
- Current observed behavior: The five selected packages have coherent themes
  but low or unreliable output compared with the expansion's A-tier leaders.
  Research Campuses currently discourage clusters through minimum spacing and
  reward nearby empty Peaks far more than adjacent Campuses.
- Why this is a real repo/code problem: The live behavior is defined jointly by
  the expansion manifest/generator, BtS XML, custom DLL calculations, UI help,
  and AI valuation. Tuning only XML or prose would leave those surfaces
  inconsistent.

## Why This Matters

- User or gameplay impact: The approved designs give each selected civilization
  a legible power loop and make mountain Campus clusters an intentional Great
  Scientist strategy.
- Maintenance / workflow / agent impact: Authoritative helpers, generated
  contracts, exact help, and tests must continue to agree.

## Scope

- In scope: Approved trait, UU, UB, and Campus tuning; required DLL/XML schema;
  generator parity; AI/UI updates; tests and current documentation.
- In scope: Save-safe derived calculations with zero defaults for new optional
  XML fields.

## Non-Goals

- Not changing Piye's trait, Kushite Archer, or Napatan Cult Chapel.
- Not replacing leaderhead, unit, building, Campus, or civilization art.
- Not changing base `Assets`, Warlords, installer behavior, or chatter.
- Not redesigning leaders outside the six reviewed packages.

## Trusted Sources Of Truth

- Primary code/config/scripts:
  - `tools/manifests/new_leaders_expansion.json`
  - `tools/add_expansion_packages.py`
  - `third_party/beyond-the-sword-sdk/CvGameCoreDLL`
  - `CoreFiles/.../Beyond the Sword/Assets/XML`
- Runtime entrypoints/import paths to verify:
  - `CvPlot::calculateImprovementYieldChange`
  - shared worked-plot city accounting in `CvCity`
  - veteran-garrison lifecycle refresh hooks
  - active trade-route accounting
  - `CvPlot::canBuildLandmark`
  - `CvPlot::accumulateLandmarkResearchCampus`
  - Campus preview/help and AI callers
- Validation scripts/tests/hooks:
  - `tools/tests/test_new_leaders_expansion.py`
  - `tools/tests/test_great_person_landmarks.py`
  - `tools/test_gate.ps1 -CheckDll`

## Existing Docs / Plans Trust Review

- `docs/LEADER_OVERHAUL_PLAN_OF_RECORD.md`: trusted for methodology and UI/AI
  requirements.
- `docs/plans/active/2026-09-30-new-leaders-expansion.md`: useful context only;
  live manifest and runtime code override old tuning.
- `.vscode/leader-expansion-overview.md`: current overview that must be updated
  with the new final mechanics.
- Session planning artifact: approved design source for this balance pass, not a
  runtime source.

## Per-Leader Design Briefs

### Ramkhamhaeng / Sukhothai

- Historical thesis: Irrigated rice prosperity and open commerce support a
  visible productive-commercial farm economy.
- Gameplay thesis: Strong early terrain development with exceptional but
  lower-food Rice Farms; power spike begins with Farms rather than a late city
  modifier.
- Power budget: `Leader Trait Heavy`.
- Trait channels: conditional improvement-plus-bonus yield calculation.
- UU decision: `KEEP` — the War Elephant is coherent and already useful.
- UB decision: `KEEP` — Ho Trai already supports cultural/scientific identity.
- Unique improvement decision: none; modify normal Farms only for this trait.
- Art: no new art; retain existing workspace assets.
- UI/AI: exact ordinary Farm and Rice override text; worker/governor valuation
  consumes authoritative yields.

### David / Israel: Davidic Kingdom

- Historical thesis: A veteran royal following unifies cities and enables
  sustained state building.
- Gameplay thesis: Barracks plus Royal Citadel creates level-3 garrisons that
  activate powerful non-stacking city Culture, Happiness, and Production.
- Power budget: `Hybrid`, intentionally S-tier leaning.
- Trait channels: veteran-garrison derived Culture, Happiness, Production, and
  domestic Great General rate.
- UU decision: `MODIFY` — retain the coherent Gibbor concept and combat bonuses,
  reduce cost to 40.
- UB decision: `MODIFY` — retain the Walls replacement, reduce cost to 50,
  replace the Priest slot with +2 land XP.
- Unique improvement decision: none.
- Art: no new art.
- UI/AI: city help exposes one activation; city/unit AI values veteran routing
  and the active production/happiness benefit.

### Piye / Kush: Napata

- Historical thesis: Priest-supported population and early archery remain the
  accepted identity.
- Gameplay thesis: Preserve the current early religious and military package.
- Power budget: `Hybrid`.
- Trait, UU, UB decisions: `KEEP`.
- Unique improvement decision: none.
- Art: no change.
- UI/AI: regression coverage only.

### Askia Muhammad / Songhai: Askia Dynasty

- Historical thesis: Regulated river commerce finances administration and
  scholarship centered on Timbuktu.
- Gameplay thesis: Develop riverside Cottage-stage plots, field accessible
  escort cavalry, then multiply Research through an improved College.
- Power budget: `Hybrid`.
- Trait channels: shared capped worked-plot Gold and Research.
- UU decision: `MODIFY` — cost 80, Horse only, retain Sentry and withdrawal.
- UB decision: `MODIFY` — cost 160, +35% Research, retain Priest slot.
- Unique improvement decision: none.
- Art: no change.
- UI/AI: one six-plot cap shared by both outputs; exact city breakdown and
  worker/governor estimates.

### Hiram I / Phoenicia: Tyre

- Historical thesis: Tyrian shipping and long-distance partnerships create a
  maritime commercial network.
- Gameplay thesis: Fast high-capacity Galleys establish coastal settlements;
  Counting Houses create routes; actual foreign routes pay trait Gold.
- Power budget: `Civ UU/UB Heavy` with a strong route trait.
- Trait channels: coastal per-active-foreign-route Gold, four-route cap.
- UU decision: `MODIFY` — cost 45, 3 movement, 3 cargo.
- UB decision: `MODIFY` — cost 120, retain foreign-route modifier, add one route.
- Unique improvement decision: none.
- Art: no change.
- UI/AI: city help counts qualifying routes; treaty/building valuation uses
  reachable route benefits.

### Mongkut / Siam: Rama IV

- Historical thesis: Scientific study and foreign diplomacy let Siam acquire
  demonstrated knowledge while preserving sovereignty.
- Gameplay thesis: Rapid diplomatic catch-up followed by efficient defensive
  modernization and stronger Observatories.
- Power budget: `Hybrid`.
- Trait channels: existing known-technology diplomatic Research modifier.
- UU decision: `MODIFY` — cost 100, retain Drill I and city defense.
- UB decision: `MODIFY` — cost 120, +35% Research, two Scientists, +2 Culture.
- Unique improvement decision: none.
- Art: no change.
- UI/AI: update exact 30-point modifier in help and technology valuation.

## Research Campus Design

- Retain Peak-only, ownership, assigned-city BFC, and resource-preservation
  requirements.
- Remove minimum same-owner spacing.
- Formula before city modifiers:
  - +2 base Research
  - +1 per adjacent Hill
  - +1 per adjacent empty Peak
  - +6 per adjacent Research Campus instead of that plot's Peak contribution
  - at most four adjacent Campuses contribute
- Placement remains unlimited; only the contribution is capped.
- Update exact output, preview breakdown, refresh behavior, Civilopedia, build
  help, governor valuation, and Great Scientist placement AI.

## Affected Files / Directories

- Primary implementation paths:
  - `tools/manifests/new_leaders_expansion.json`
  - `tools/add_expansion_packages.py`
  - `third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvInfos.*`
  - `third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvPlot.cpp`
  - `third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvCity.cpp`
  - `third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvGameTextMgr.cpp`
  - relevant AI files
  - BtS XML generated by the expansion generator
- Adjacent paths to inspect:
  - `tools/tests/test_new_leaders_expansion.py`
  - `tools/tests/test_great_person_landmarks.py`
  - `.vscode/leader-expansion-overview.md`
  - `docs/MANUAL_SMOKE_TESTS.md`
- Paths to avoid unless evidence requires them:
  - base `Assets`
  - `Warlords`
  - `CoreFiles/dist`
  - external asset libraries
  - `petromod_v1`

## Assumptions Confirmed During Planning

- The approved balance values are intentional even where they create S-tier
  packages, especially David and Campus clusters.
- Commerce is used for visible plot money-like output because plots cannot
  expose direct Gold.
- New behavior should be derived from live plot, unit, route, and city state;
  no new save ledger is required.
- Existing art remains accepted for this tuning pass.

## Proposed Implementation Steps

1. Update the manifest contract and generator/schema capability.
2. Implement authoritative trait calculations and lifecycle refreshes.
3. Apply approved UU/UB XML values.
4. Implement Campus spacing and cluster output.
5. Wire exact UI and AI consumers to authoritative helpers.
6. Regenerate BtS XML and verify deterministic parity.
7. Add focused regression tests and update current documentation.
8. Run the required DLL/XML gate and record manual smoke-test status.

## Validation Plan

- Required automated checks:
  - focused expansion and landmark pytest files
  - generator determinism/parity
  - `git diff --check`
- Required repo scripts:
  - `.\tools\test_gate.ps1 -CheckDll`
- Required manual smoke test:
  - install updated payload into the live game tree
  - verify Ramkhamhaeng plot yields
  - verify David's city output as a veteran enters/leaves
  - verify Askia's capped dual output
  - verify Hiram's route gain/loss
  - verify Mongkut catch-up Research
  - construct adjacent Campus pair/triangle and compare displayed output
- Validation blocked or not yet runnable: live gameplay requires a human-operated
  Civ4 session after automated implementation.

## Documentation Updates Required

- Update `.vscode/leader-expansion-overview.md`.
- Update `docs/MANUAL_SMOKE_TESTS.md` with the final balance checks.
- Update this plan's status, validation, and final outcome.
- Update `docs/index.md` only if this plan is added to its active-plan listing.

## Risks / Rollback

- Main risks: duplicate Ramkhamhaeng bonuses, divergent Askia caps, stale David
  city caches, nominal rather than active Hiram routes, Campus double-counting,
  and AI/help drift.
- Likely failure modes: XML schema rejection, DLL compile errors, stale city
  output until a turn boundary, and Campus cluster output not refreshing.
- Safe rollback approach: revert the manifest/schema/runtime changes together;
  do not leave generated XML ahead of DLL support.
- Paths that should not be touched during rollback: unrelated expansion
  packages, art, installer, and base/Warlords mirrors.

## Open Questions

- None for implementation. Manual gameplay balance remains an acceptance step.

## Completion Checklist

- [x] Trusted sources of truth were verified from code/config/scripts.
- [x] Existing docs/plans in this area were reviewed and classified.
- [x] Assumptions needing human confirmation were resolved during planning.
- [x] Implementation steps completed.
- [x] Required validation recorded.
- [x] Required manual smoke test completed or blocker escalated.
- [x] Related docs updated.
- [x] Residual risks summarized.

## Final Outcome Summary

- What changed: Implemented visible Ramkhamhaeng Farm/Rice yields; Askia's
  shared six-plot Gold/Research engine; David's veteran Culture, Happiness and
  Production state; Hiram's active foreign-route Gold; Mongkut's approved
  values; all approved UU/UB changes; and the adjacent Research Campus formula.
- Validation performed: 98 focused pytest contracts passed; generator parity
  and idempotence passed twice with 58/58 outputs and zero reconciliation
  errors; `test_gate.ps1 -CheckDll` passed XML, roster, localization, citystyle,
  and DLL compilation; the post-text XML gate and `git diff --check` passed.
- Docs updated: expansion overview, manual smoke tests, landmark/trait game
  text, and this implementation record.
- Remaining risks: Installed-game smoke testing has not been performed, so
  gameplay feel, rendered map yields/tooltips, and live cluster balance remain
  human acceptance items.
- Follow-up tasks: Run the documented fresh-game smoke matrix for the five
  leaders and Campus pair/triangle/four-neighbor cases.
