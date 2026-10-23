# Matthias Corvinus Rebalance

- Status: `implemented_pending_gameplay_smoke`
- Owner / agent: GitHub Copilot CLI
- Last updated: `2026-10-23`

## Problem Statement

- Task: Resolve GitHub issue #153 by replacing Matthias Corvinus's weak,
  disconnected kit with the user-approved Sword and Codex design.
- Current observed behavior: the trait grants a 25% upgrade discount to Melee
  and Gunpowder units plus +1 Research to Artists; the Corvinian College loses
  the normal University's Scientist slots; the Black Army pays extra upkeep
  without a supporting production or training loop.
- Why this is a real repo/code problem: the live XML and expansion manifest
  confirm that the package is weaker and less cohesive than comparable kits.

## Scope

- Replace Paid Professionals gameplay with Sword and Codex: Scientists provide
  +1 Culture.
- Add Bibliotheca Corviniana as a Library replacement granting +2 experience
  to Archery and Gunpowder units.
- Make Corvinian College retain normal University behavior and grant +3
  experience to Archery and Gunpowder units.
- Allow the two building bonuses to stack to +5 experience.
- Keep the Black Army Arquebusier unchanged.
- Preserve the legacy promotion record at zero effect for XML/save index
  compatibility, but stop granting it.

## Trusted Sources Of Truth

- `tools/manifests/new_leaders_expansion.json`
- `tools/add_expansion_packages.py`
- Live BtS XML under
  `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML`
- `tools/tests/test_new_leaders_expansion.py`
- `tools/test_gate.ps1`

## Proposed Implementation Steps

1. Extend expansion package generation to support optional additional unique
   buildings without changing existing package order.
2. Update Matthias's manifest contract and focused regression tests.
3. Generate Bibliotheca Corviniana and the revised live XML/text mappings.
4. Run focused expansion tests and the repository XML gate.

## Validation Plan

- Run focused expansion and building tests.
- Run `.\tools\test_gate.ps1`.
- Run `git diff --check`.
- Manual gameplay smoke test remains required to confirm the displayed
  building effects and +5 combined experience in-game.

## Completion Checklist

- [x] User approved the exact design and names.
- [x] Manifest/generator contract updated.
- [x] Live XML/text generated.
- [x] Focused tests pass.
- [x] Repository gate passes.
- [x] Manual gameplay smoke test recorded as pending.

## Final Outcome Summary

- What changed: Sword and Codex now gives Scientists +1 Culture; Bibliotheca
  Corviniana and Corvinian College grant +2/+3 experience to Archery and
  Gunpowder units; the Black Army remains unchanged; and the legacy promotion
  remains as a zero-effect compatibility record.
- Validation performed:
  `python -m unittest tools.tests.test_new_leaders_expansion tools.tests.test_batch_buildings`
  passed 31 tests; `.\tools\test_gate.ps1` passed XML, roster, and citystyle
  checks; `git diff --check` passed.
- Remaining risks: the intended +5 experience stacking and final in-game
  Civilopedia presentation still require manual gameplay acceptance.
