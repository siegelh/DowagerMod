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
- Pacifism / Emancipation civic rebalance:
  - SP: compare a worked Town before and after adopting Emancipation; confirm the city receives exactly +2 gold and no other commerce
  - SP: adopt Pacifism and confirm a worked Town receives no civic food bonus
  - SP: adopt Free Market and confirm a worked Town receives no civic food bonus
  - Help: hover Emancipation and confirm its civic help lists +2 gold per worked Town with a valid gold icon
  - Save/reload: save with Emancipation active, reload, and reconfirm the worked-Town gold
  - MP: load the same setup on two clients, adopt Emancipation, and confirm identical yields with no OOS
  - These installed SP, save/reload, and MP checks remain required acceptance gates unless their actual runs are reported
- Remaining-roster additive release:
  - Start a **fresh game** for every SP and MP run; old saves are not acceptance evidence
  - Confirm Washington, Hammurabi, Elizabeth, Wang Kon, Genghis Khan, Sitting Bull, Mao/Chinese Leader, Salamasina, Stalin, and Churchill retain their complete baseline features with no last-pass removals or reductions
  - Confirm Geronimo uses the approved AI/personality values; Huayna's approved text is visible; Asoka's Obelisk uses Asoka (not Ramesses) trait links and the corrected war-weariness sign; Casimir and Churchill expose the approved flavors
  - Confirm Stalin retains the baseline USSR package and receives exactly +1 Production from each active Factory
  - Confirm Enrico Dandolo/Venice is unchanged, including Founder mapping, Merchant actions, Palace, trait, personality, text, buttons, and art
  - Confirm Kublai retains both approved Palace layers, including the Yuan Imperial Secretariat, and each layer exposes its expected help/effects
  - Confirm Peter has Great People rate 50; Library +2 research/+1 culture; University +3 research/+1 culture; Admiralty and Collegium each 25% research
  - Found and exercise Corporations 1-6; confirm ordered gold values 100/200/350/100/250/200; confirm Corporation 7 remains inert
  - Run representative AI autoplay for Geronimo, Casimir, Churchill, Peter, Stalin, and Kublai; report observed behavior and any stalls
  - Start the same fresh scenario on two clients with identical assets; confirm the restored/additive values match and no OOS occurs
  - Confirm no new worker action or art appears; Salamasina and Enrico retain only their baseline action surfaces
- AI Leader Chatter (`Chatter\CvLeaderChatter.py`, sidecar in `tools\chatter\`):
  - SP: start a game with at least 2 AI civs; force a DoW via WorldBuilder; confirm a chat line appears within ~10s
  - If multi-turn fired: confirm follow-up lines arrive ~5-10s after the first
  - Save mid-game, exit, reload; confirm no replay of the previous DoW line
  - Run `.\tools\Stop-Chatter.ps1` mid-game; play a few more turns; confirm zero in-game errors and no slowdown
  - Quit, ensure sidecar is not running, launch fresh; confirm the game is normal with no chatter and no errors
  - 2-client MP (LAN or two instances): force a DoW; verify exactly ONE entry in your sidecar's `daemon.log` AND BOTH clients display the SAME chat line; confirm no OOS warning fires
  - See [`CHATTER_RUNBOOK.md`](CHATTER_RUNBOOK.md) for detailed troubleshooting

## What to report

- Which smoke path you ran
- Which save or scenario you used
- What passed
- What you did not test
- Any unresolved warnings or suspicious behavior
