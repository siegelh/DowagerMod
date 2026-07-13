# Remaining-roster worker-action gate

- Status: `approved_additive_freeze`
- Last updated: `2026-07-13`
- Scope: remaining-roster implementation only

## Decision

**No new worker actions and no new worker-action art are authorized.**

The approved roster direction is additive and does not use worker actions as a
leader-differentiation channel. Existing actions remain baseline behavior and
must not be removed, reduced, remapped, or expanded by this pass.

## Package rules

- Salamasina retains the baseline Wayfinder/Reef Works action exactly; this
  contract neither adds a new action nor approves new art.
- Enrico Dandolo remains exact and untouched, including every existing
  Venetian Merchant action.
- No other remaining-roster package receives a build, improvement, mission,
  command, worker permission, worker AI branch, button, model, texture, or
  animation change.
- Kublai's approved Palace layers and Peter's science buffs are building/trait
  work only and do not create worker actions.
- Corporation gold values do not create worker or unit actions.

## Release gate

1. Diff checks show no new or changed worker-action, improvement, mission,
   unit-build permission, worker AI, or action-art records.
2. Enrico's action surface is byte-for-byte/node-for-node unchanged.
3. Salamasina's baseline Reef Works action is unchanged.
4. Manual checks use a fresh game; old-save acceptance is out of scope.

Any proposed worker-action or art change requires a separate approval and is
not part of this contract.
