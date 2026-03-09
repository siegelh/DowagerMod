# Manual Smoke Tests

Use this runbook after gameplay-affecting changes. If XML, Python, DLL, UI, art references, entrypoints, or persistence changed, a smoke test is required.

## Minimum smoke test

1. Install or copy the updated files into the live game tree.
2. Launch the mod.
3. Confirm it reaches the main menu without XML or Python error popups.
4. Load a representative save or start a quick single-player game.
5. Open the affected screen or advisor if relevant.
6. Exercise the changed mechanic, building, unit, or art reference at least once.
7. End one turn.
8. If the task touched save-state, serialization, or persistent Python state, save and reload once.

## Extra checks by change type

- XML rules/content:
  - confirm the relevant object appears with expected text, costs, prereqs, and effects
- DLL:
  - confirm the changed mechanic actually resolves in-game, not just in tooltips
- UI / HUD / advisors:
  - open the target screen from its real entrypoint and verify input, update, and close behavior
- Art:
  - verify the art path resolves without pink boxes, missing buttons, or crash-on-open behavior
- Persistence:
  - save and reload once, then confirm the changed state still exists

## What to report

- Which smoke path you ran
- Which save or scenario you used
- What passed
- What you did not test
- Any unresolved warnings or suspicious behavior
