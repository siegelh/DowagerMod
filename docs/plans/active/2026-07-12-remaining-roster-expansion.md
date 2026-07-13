# Remaining roster implementation and release contract

- Status: `approved_additive_direction_runtime_pending`
- Last updated: `2026-07-13`
- Runtime edits in this task: **none**

## Release scope

Implement the approved additive remaining-roster direction without reducing
the pre-last-pass baseline. The authoritative object/value matrix is
`2026-07-12-remaining-roster-implementation-matrix.md` and its machine-readable
companion in `tools/baselines`.

## Required release payload

1. Restore Washington, Hammurabi, Elizabeth, Wang Kon, Genghis Khan, Sitting
   Bull, Mao/Chinese Leader, Salamasina, Stalin, and Churchill to their
   baseline feature sets.
2. Retain approved additive Geronimo AI, Huayna text, Asoka fixes, Casimir
   flavor, Stalin Factory `+1` Production, Churchill espionage flavor, and both
   Kublai Palace layers including the Yuan Imperial Secretariat.
3. Leave Enrico Dandolo/Venice exact and untouched.
4. Add Peter's approved broad science package:
   - Great People rate `50`;
   - Library `+2` research and `+1` culture;
   - University `+3` research and `+1` culture;
   - Admiralty `25%` research;
   - Collegium `25%` research.
5. Set Corporation 1-6 ordered gold values to
   `100/200/350/100/250/200`; keep Corporation 7 inert.

## Explicit exclusions

- No baseline feature removals or reductions for touched packages.
- No DLL or schema work.
- No new worker actions or worker-action art.
- No new, replaced, or remapped art.
- No old-save migration or compatibility work.
- No changes outside the approved roster/corporation contract.

## Implementation sequencing

1. Restore baseline package nodes and mappings first.
2. Apply the retained additive/corrective records.
3. Apply Peter's science package.
4. Apply the corporation values and Corp7 inert state.
5. Run static and XML/roster validation.
6. Install the synchronized payload.
7. Start fresh SP and fresh two-client MP games for manual acceptance.

Each step must be independently diffable. A later additive step may not hide a
baseline restoration failure.

## Automated release gates

- JSON and XML parse successfully.
- Package and corporation contracts match the machine-readable matrix.
- Restored package snapshots contain no last-pass removals/reductions.
- Enrico matches baseline exactly.
- Peter's five science values match exactly.
- Corporation values match exactly and Corp7 has no effective gold behavior.
- No DLL, worker-action, test-code, or art paths are changed.
- Existing repository roster/XML gates pass during implementation.

## Manual release gates

Use `docs/MANUAL_SMOKE_TESTS.md`.

- Fresh game is mandatory for every SP and MP check.
- Verify affected Civilopedia/help surfaces and city/unit availability.
- Exercise representative restored yields/mappings.
- Verify Peter's trait and building research/culture effects.
- Verify Stalin Factory Production and Churchill/Geronimo/Casimir AI data
  through observable AI behavior over representative turns.
- Verify both Kublai Palace layers.
- Verify Corporation 1-6 gold values and Corporation 7 inactivity.
- Run fresh two-client MP with identical assets and confirm no OOS.

## Release verdict

**Not ready for merge/deploy until runtime implementation, automated gates,
installed fresh-game smoke, and fresh two-client MP acceptance are recorded.**

Old-save loading does not satisfy any release gate.
