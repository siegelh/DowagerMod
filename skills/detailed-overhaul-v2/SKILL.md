---
name: detailed-overhaul-v2
description: Build deeply historical, highly distinctive Civilization IV BtS leader/civilization overhaul specs by mapping salient historical facts onto the full XML/DLL design space (leader, civ, trait, personality, UU, UB, palace, improvements, text, art, and mechanics interactions). Use when users ask for creative but grounded overhauls and want explicit plain-English history-to-mechanics reasoning.
---

# Detailed Overhaul V2

Use this skill to design one leader/civ overhaul at a time with strong historical grounding and high gameplay distinctiveness.

## Workflow

1. Intake and scope lock
- Ask only for the target `LEADER_*` + `CIVILIZATION_*`.
- Infer all other design settings from baseline data, historical evidence, and distinctiveness requirements.

2. Scan the current mechanics first
- Run `scripts/scan_mechanics.ps1` against the live repo.
- Treat all modifiable levers as valid design space. Do not pre-rank categories as “more important.”

3. Baseline audit
- Audit all relevant baseline axes for the selected target:
- Leader traits/modifiers (legacy + custom), leader personality/diplomacy AI, favorite civic/religion.
- Civ mapping, UU/UB/palace replacements and full stats.
- Civ defaults (free techs, initial civics, free classes, disabled techs), city names, civilopedia text.
- Unique improvements/build actions/caps/prereqs and art/audio/style/playercolor bindings.
- Tooltip/localization keys and interactions with civics/routes/bonuses/specialists/DLL-gated mechanics.

4. Historical research (internet required)
- Research the leader/civilization using primary or high-quality secondary sources.
- Extract 5-8 salient historical themes (statecraft, military doctrine, economy, administration, religion, geography, infrastructure, culture).
- Include source links in the output.

5. Plain-English historical summary (required)
- Provide a concise summary of the person/civilization in plain English before mechanics.
- Then map each major historical point to concrete game concepts and exact mechanics.

6. Generate asymmetric design concepts
- Produce 2-3 variant concepts, then recommend one.
- Avoid repeated templates across civs (for example “roads + resources + generic building buffs” every time).
- Use rare unique tile improvements only when strongly justified and gated (hard cap and/or terrain/tech constraints).

7. Implementation-ready spec
- Provide exact object IDs, numbers, prerequisites, and affected files.
- Include civpedia/tooltip text plan and art sourcing plan.
- If using art from `C:\Users\Harrison\Downloads\civ4mods-code`, copy assets into workspace before XML references.

8. Validation and risk controls
- Include schema/tag placement checks, localization placeholder checks, in-game verification checklist, and rollback plan.

## Output Contract

Follow [references/output-template.md](references/output-template.md).

Must include:
- Plain-English historical summary.
- History-to-mechanics mapping table.
- Distinctiveness check: explain why this package does not feel like prior overhauls.
- Keep/modify/replace decision for existing UU/UB with rationale.

## References

- Baseline XML docs: [references/modiki-baseline-links.md](references/modiki-baseline-links.md)
- Output structure: [references/output-template.md](references/output-template.md)
- Intake prompts: [references/intake-questions.md](references/intake-questions.md)
