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
- Great Person landmarks (Industrial Zone, Naval Foundry, Research Campus, Commercial District, Grand Bazaar, Sacred Grove):
  - Start a **fresh game** (new InfoTypes are appended; old saves are not acceptance evidence)
  - Rendering: build each landmark and confirm its model and build-button render with no pink boxes or missing icons; hover the tile and the build action and confirm the generated help lists the correct adjacency mechanics
  - Map model scale: confirm each of the 13 new landmarks (Industrial Zone, Naval Foundry, Research Campus, Commercial District, Grand Bazaar, and all 8 Sacred Grove variants) renders at roughly half size on the map (`fScale = 0.5`) and no longer reads as large as a city; check readability at normal and strategic zoom
  - Interface scale unchanged: confirm the Civilopedia entry and the build/action buttons for each landmark are still normal size (`fInterfaceScale` stays `1.0`) — only the on-map model shrank
  - Grand Colosseum unchanged: build (or view) the Great Artist's Grand Colosseum and confirm its on-map size is visually identical to before (still `fScale = 1.5`, not shrunk)
  - Landmark output tooltips (exact total + breakdown), for **each** landmark type, check **both** places:
    - Build-action hover (before construction): select the Great Person, hover its "Create ..." build action, and confirm a **"Projected landmark output:"** block appears with an exact total and a per-contributor breakdown, and that the generic ", +N" native-yield line is **not** duplicated for the landmark
    - Built-map hover (after construction): build the landmark, then mouse over its tile and confirm a **"Current landmark output:"** block appears with the same numbers the tile actually produces
    - Industrial Zone: breakdown lists adjacent owned Watermills/Workshops/Mines-or-Quarries counts (+3/+2/+1) and a Production total; with none adjacent it explicitly states zero and shows Total +0
    - Naval Foundry: shows "This tile: +2", the count of your water tiles within 2 that effectively gain the aura (+1, and "of which water resources" +2), and a combined footprint Production total; place a second overlapping Foundry and confirm the effective aura count/total shrink (non-stacking, exact effective)
    - Research Campus: shows the exact direct Research to the working city (this is the reported previously-missing value), the on-Tundra/Snow +3 component, and adjacent Peak/Jungle/Hill/Tundra/Snow counts with stacking (e.g. a Snow Peak lists both Peak +3 and Snow +2)
    - Commercial District: shows bordering city center +6 and adjacent owned Cottage/Hamlet/Village/Town counts (+1/+2/+3/+4) and a Commerce total
    - Grand Bazaar: shows adjacent owned happiness-resource count (+4 each) and, of those, the count connected by their valid improvement (+2 each), and a Commerce total
    - Sacred Grove: shows adjacent Forest/Jungle and adjacent water counts (+1 Food each) and adjacent owned Forest Preserve count (+1 Food/+1 Commerce each), with Food and Commerce totals
    - Fog/ownership: confirm the built-map block only shows for a revealed landmark you can see, and never leaks values for tiles you have not revealed
  - Great Engineer: confirm Industrial Zone (flat owned land) shows +3/+2/+1 Production for adjacent owned Watermill/Workshop/Mine or Quarry; Naval Foundry (flat coastal land) shows +2 Production on its tile and grants +1 Production (+2 more on resources) to your water tiles within 2, and confirm two overlapping Foundries do **not** stack the aura
  - Great Scientist: confirm Research Campus adds base Research to the working city before Research modifiers (+3 on Tundra/Snow; adjacent Peak +3, Jungle +2, Hill +1, Tundra +1, Snow +2 stack, including Jungle Hills and Snow Peaks); verify the number lands in the city's base Research, not slider-split commerce
  - Great Merchant / Venetian Merchant Prince: confirm Commercial District must border your city center (+6 Commerce) and adds +1/+2/+3/+4 for adjacent owned Cottage/Hamlet/Village/Town, and that two Districts cannot be built adjacent; confirm Grand Bazaar gives +4 per adjacent owned happiness resource and +2 more when connected; confirm both remain slider-dependent
  - Great Prophet: with each state religion (and none), confirm only the matching Sacred Grove variant is buildable, its art is the expected shrine/Naiku model, adjacent Forest/Jungle gives +1 Food, an owned adjacent Forest Preserve adds +1 Food/+1 Commerce, adjacent water adds +1 Food, and the art stays fixed after a later state-religion change
  - Spacing: confirm same-type landmarks require plot distance 4, all eight Sacred Grove variants share one spacing group, and Commercial Districts are exempt from distance 4 but cannot be adjacent
  - Legality: confirm a landmark cannot be placed on a resource tile, outside a workable owned city radius, or over an existing improvement via the AI path
  - Pillage/ownership: pillage a landmark and confirm it is destroyed completely; flip a plot's owner and confirm owned-only adjacency and the Foundry aura recompute correctly
  - Venetian preservation: confirm the Merchant Prince still Founds cities, builds Roads and the Grand Colosseum, and performs every prior action; confirm it can also build both Merchant landmarks
  - AI: run autoplay and confirm Great Engineers/Scientists/Merchants/Prophets place their landmarks on sensible tiles, the empire's first copy of each type is placed at least once, and Venice still expands (Founder safety) while also scoring both Merchant landmarks
  - Save/reload: save with landmarks placed and reload; confirm yields, city Research, and art persist
  - MP: start the same fresh scenario on two clients; place landmarks and run AI; confirm identical yields and no OOS
- AI Leader Chatter (`Chatter\CvLeaderChatter.py`, sidecar in `tools\chatter\`):
  - SP: start a game with at least 2 AI civs; force a DoW via WorldBuilder; confirm a chat line appears within ~10s
  - If multi-turn fired: confirm follow-up lines arrive ~5-10s after the first
  - Save mid-game, exit, reload; confirm no replay of the previous DoW line
  - Run `.\tools\Stop-Chatter.ps1` mid-game; play a few more turns; confirm zero in-game errors and no slowdown
  - Quit, ensure sidecar is not running, launch fresh; confirm the game is normal with no chatter and no errors
  - 2-client MP (LAN or two instances): force a DoW; verify exactly ONE entry in your sidecar's `daemon.log` AND BOTH clients display the SAME chat line; confirm no OOS warning fires
  - See [`CHATTER_RUNBOOK.md`](CHATTER_RUNBOOK.md) for detailed troubleshooting

- Installer reliability (wipe-and-restore; retired hot-swap fast path):
  - Close Civ4 completely, then run the rebuilt installer (`Install DowagerMod.bat` / `CoreFiles\dist\DowagerMod-Installer\DowagerMod-Installer.exe`)
  - Confirm the install completes and the game launches with DowagerMod applied
  - Confirm **no** new sibling folder named `<install> - DELETE_ME` or `<install> - PRISTINE_HOT` is created next to the live install (the retired fast path used to create these)
  - Migration: if an **older** installer previously left a `<install> - DELETE_ME` or `<install> - PRISTINE_HOT` folder and it is not locked, confirm the installer reports removing it and it is gone afterward
  - Locked migration: if such a stale folder is held open (e.g. Explorer window inside it), confirm the installer prints a prominent path-specific WARNING, does **not** claim success for that folder, and still completes the install
  - Confirm the `<install> - PRISTINE` snapshot and the live install are both intact and untouched by migration cleanup
  - Re-run the installer a second time and confirm it wipes back to pristine and reapplies cleanly (still no `DELETE_ME`/`PRISTINE_HOT` siblings)

## What to report

- Which smoke path you ran
- Which save or scenario you used
- What passed
- What you did not test
- Any unresolved warnings or suspicious behavior
