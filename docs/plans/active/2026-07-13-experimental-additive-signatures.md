# Experimental Additive Signature Layer

- Status: `implemented experimental; gameplay validation pending`
- Owner / agent: GitHub Copilot CLI
- Last updated: `2026-07-14`
- Rollback boundary: the single commit titled
  `Add experimental signatures to all 59 packages`

## Goal

Give each of the 59 playable one-leader civilization packages exactly one
additional historically themed feature without removing, reducing, replacing,
or reordering any existing content.

## Implementation

The authoritative 59-row specification is
[`tools/manifests/additive_signature_manifest.json`](../../../tools/manifests/additive_signature_manifest.json).
Every row records the dedicated trait, historical signature name, affected
building class, exact additive yield or commerce vector, and rationale.

All additions use the existing trait `BuildingYieldChanges` or
`BuildingCommerceChanges` channels. They therefore:

- apply automatically to the civilization's replacement of that building
  class, where one exists;
- use existing building AI and generated trait/building help;
- require no new InfoTypes, art, schema, Python, or DLL behavior;
- remain deterministic in multiplayer.

The bonuses are intentionally one point each: one Food, Production, Gold,
Research, Culture, or Espionage on a historically relevant building class.
This makes each addition visible and meaningful while containing the power
added on top of the already-complete roster.

## Safety contract

`tools/tests/test_additive_signature_manifest.py` proves:

1. The manifest covers exactly the 59 dedicated traits used by the 59 playable
   one-to-one packages.
2. Every referenced building class resolves.
3. Each trait differs from pre-experiment commit `7da9963f6` by exactly its one
   approved manifest delta and nothing else.
4. Every delta is non-negative, has magnitude exactly one, and includes a
   signature name and rationale.

The older restored-roster exact contract normalizes these explicit additions
before checking its original baseline, so the experiment cannot hide a
regression in previously restored content.

## Risks and acceptance

- Building-class channels can affect the normal building and its unique
  replacement. That spillover is intentional and recorded in the manifest.
- AI uses normal building valuation; it may undervalue the trait-only bonus
  when deciding build order.
- Early Food/Production bonuses and late multiplier buildings need gameplay
  observation even though every raw delta is only one.
- Fresh single-player autoplay and two-client multiplayer/OOS acceptance
  remain user-owned.

## Readiness

- Ready for implementation: **Yes** (implemented).
- Ready for merge/deploy: **No** until representative gameplay and multiplayer
  acceptance.
