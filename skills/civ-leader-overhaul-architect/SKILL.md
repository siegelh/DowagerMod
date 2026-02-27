---
name: civ-leader-overhaul-architect
description: Design distinctive, historically grounded Civilization IV (BtS) leader/civilization overhaul proposals with implementation-ready specs. Use when a user asks to redesign a leader or civ identity, rebalance traits, evaluate or replace UU/UB/palace, consider rare unique improvements, map gameplay to historical era context, compare current vs proposed mechanics, or prepare XML/DLL/art change plans.
---

# Civ Leader Overhaul Architect

Use this skill to produce high-variance, high-flavor overhaul designs that are historically rooted but gameplay-distinct.

Prefer BtS content first. Treat Warlords as reference-only unless explicitly requested.

## Workflow

1. Confirm scope and intake
- Ask for: target leader/civ, desired power level, historical strictness, whether UU/UB should be preserved, and whether rare unique improvements are allowed.
- Use concise intake prompts from [intake-questions](references/intake-questions.md).

2. Scan current mechanics before ideation
- Run `scripts/scan_mechanics.ps1` to inventory current trait/civic/improvement/build mechanics from live XML.
- Do not assume yesterday's mechanic set is still valid.

3. Audit current in-mod baseline
- Read current entries for leader/civ across all relevant axes: leader traits and modifiers (legacy + custom), leader personality/diplomacy AI, favorite civic/religion, civilization mapping, UU/UB/palace replacements and full unit/building stats, civ defaults (free techs/initial civics/free classes/disabled techs), city-name list and era flavor text, unique improvements/build actions/caps/prerequisites, linked art/audio/playercolor/style definitions, localization keys/tooltips, and interactions with civics/routes/bonuses/specialists/DLL-gated mechanics.
- Explicitly note what already works and should be retained.

4. Perform historical research (internet required)
- Use the web for modern/historical verification.
- Prefer primary and credible secondary sources (encyclopedias, museums, academic publishers, national archives).
- Capture source links and map each major mechanic to a historical rationale.

5. Generate proposals with asymmetry
- Produce 2-3 concept variants, then select one recommendation.
- Avoid template feel. Vary where power lives:
- `Leader-heavy`: stronger trait package, lighter civ kit.
- `Civ-heavy`: stronger UU/UB/palace/improvement identity, lighter traits.
- `Hybrid`: both medium.
- Treat rare unique tile improvements as exceptional, not default.

6. Enforce overhaul constraints
- Evaluate fit of existing UU/UB before replacing.
- Prefer modifying or extending existing UU/UB when historically plausible.
- Use generic `BuildingYieldChanges`/`BuildingCommerceChanges` sparingly; prefer identity via unique content.
- If using external art from `C:\Users\Harrison\Downloads\civ4mods-code`, copy assets into workspace before XML references.

7. Produce implementation-ready spec
- Use the format in [output-template](references/output-template.md).
- Include: exact XML object ids, values, prerequisites, civilopedia text intent, art source plan, AI/UX risks, and phased rollout.

8. Pre-implementation validation checklist
- Confirm schema-valid tag placement and non-empty required elements.
- Confirm text keys exist for any new tooltip strings.
- Confirm improvement buildability rules (unit, tech, terrain, route, ownership, caps).
- Confirm trait/civic tooltip formatting uses valid translation templates.

## Guardrails

1. Be historically inspired, not mechanically repetitive.
2. Keep each civ/leader playstyle materially distinct from existing overhauls.
3. Prefer explicit tradeoffs over pure stat inflation.
4. For rare unique improvements, justify cap/gating and communicate UX text clearly.
5. Always include citations when historical claims are central to mechanics.

## Resources

- Intake prompts: [references/intake-questions.md](references/intake-questions.md)
- Output structure: [references/output-template.md](references/output-template.md)
- Mechanics scanner: `scripts/scan_mechanics.ps1`
