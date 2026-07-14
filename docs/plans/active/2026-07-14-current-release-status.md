# Current Release Status

- Status: `implementation complete / manual acceptance pending`
- Owner / agent: GitHub Copilot CLI
- Last updated: `2026-07-14`
- Branch: `agent-baseline-leader-chatter-sol-leader-update`
- Current implementation head: `046656da1`

## Purpose

This is the consolidated current-state record for the July roster, landmark,
industry, installer, color, and Sol Patch presentation work. Detailed mechanic
contracts remain in their linked plans; this file records what is landed and
what is genuinely still open.

## Landed implementation

| Track | State | Commit |
| --- | --- | --- |
| Full 27-package diversity overhaul and 32-package additive restoration | Implemented | `b4020964e` |
| Great Person landmark system | Implemented | `49430d6a4` |
| Exact landmark output previews | Implemented | `2bc28cd7f` |
| Landmark multiplayer/turn-processing optimization | Implemented | `8336d0314` |
| Landmark half-scale art and always-mirror installer | Implemented | `e82900863` |
| Productive Industrial Zone AI floor | Implemented | `1850a0177` |
| Unique colors for all 59 playable civilizations | Implemented | `7da9963f6` |
| One additive historical signature for every playable package | Implemented experiment | `b0b6c0eb2` |
| Approved 69-building industry output rebalance | Implemented | `15fa7e404` |
| Sol Patch loading backgrounds | Implemented | `f498352e3` |
| Preserved custom Dowager/Barclay Sol home scene | Implemented | `046656da1` |

The Emancipation Town bonus was also normalized in `15fa7e404` to the standard
`+2 Commerce` improvement-yield representation.

## Automated evidence

- Full repository unit suite: 116 tests passing at the current head.
- Changed XML and roster-safety gate passing.
- Relevant DLL builds, payload/source hash checks, art-reference closure,
  installer migration tests, proposal fingerprints, and exact package contracts
  passed in their implementation tracks.
- The worktree was clean and every listed implementation commit was pushed.

## Outstanding manual acceptance

1. Install `046656da1` and verify:
   - giant Dowager and embedded/floating Barclay imagery remain;
   - the Sol plaque replaces the obsolete label;
   - loading backgrounds render without clipping or progress-text overlap.
2. Verify all 13 landmark scales and exact build/map hover previews in game.
3. Run representative landmark AI autoplay, especially Industrial Zone
   placement and Great Person processing overhead.
4. Review all 59 civilization colors on a large world map and minimap.
5. Exercise representative additive signatures at early, middle, and late
   building unlocks.
6. Stress the approved industry Food/GPP/output stacks, city caps, AI build
   choices, health/happiness pacing, and corporation progression.
7. Run fresh-game save/reload and fresh two-client multiplayer/OOS acceptance
   with identical installed payloads.

These runtime gates are tracked as the remaining roster-integration and
release-evidence blockers. Old saves are not acceptance evidence for roster
changes that require fresh games.

## Explicitly outstanding design work

The systematic **59-package era-peak power audit** has not been designed or
implemented. The additive signature layer gives every package one historical
`+1` building-class output, which creates small unlock-timed bonuses, but it is
not a complete analysis of:

- intended peak era and duration;
- UU/UB unlock timing and upgrade window;
- trait, worker-action, resource, map, and technology synergy;
- AI ability to exploit the peak;
- comparative package strength before, during, and after that window.

That audit requires a separate reviewable proposal before additional runtime
balance changes.

## Readiness

- Ready for further implementation planning: **Yes**.
- Ready for merge/deploy: **No**.
- Blockers: installed visual/gameplay acceptance, AI autoplay, save/reload,
  and fresh two-client multiplayer/OOS evidence.
