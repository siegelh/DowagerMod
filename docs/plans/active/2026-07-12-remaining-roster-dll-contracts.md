# Remaining-roster DLL contract

- Status: `no_dll_work_authorized`
- Last updated: `2026-07-13`
- Runtime edits in this task: **none**

## Verdict

**No DLL or new schema work is required or authorized.**

The approved direction restores baseline package features and uses only
existing XML/text channels for the retained additions. Do not add an XML tag,
reader, getter, cache, persisted member, Python binding, AI hook, mission,
command, network message, or random decision path.

## Existing channels used

| Approved item | Existing channel |
|---|---|
| Geronimo AI | stock leader personality fields |
| Huayna clarification | text/help only |
| Asoka fixes | stock building trait and war-weariness fields |
| Casimir flavor | stock leader flavor array |
| Stalin Factory +1 Production | existing trait `BuildingYieldChanges` |
| Churchill espionage flavor | stock leader flavor array |
| Kublai Palace layers/Secretariat | existing building and civilization mapping fields |
| Peter Great People rate | existing trait scalar |
| Peter Library/University research and culture | existing trait building-commerce tables |
| Peter Admiralty/Collegium research | existing building commerce modifier |
| Corporation gold values | existing corporation XML value channel |

Restoring Washington, Hammurabi, Elizabeth, Wang Kon, Genghis, Sitting Bull,
Mao/Chinese Leader, Salamasina, Stalin, and Churchill requires no new runtime
mechanic. Enrico remains exact and untouched.

## Prohibited DLL scope

- No cache migration for old saves.
- No dual-path compatibility logic.
- No worker/build/mission logic.
- No corporation runtime special case for Corporation 7; it must be inert
  through existing data fields.
- No Palace stacking hook. Kublai's two approved layers must use existing XML
  behavior.
- No new AI valuation code for Peter, Stalin, Churchill, or corporations.

## Save and multiplayer rule

Trait and player values may be cached or serialized by the existing game.
Therefore:

1. **Fresh games are mandatory.**
2. Old-save behavior is not a release criterion and must not motivate DLL
   migration work.
3. Multiplayer validation starts fresh on every peer with identical assets.
4. No compatibility claim may be made from loading a pre-change save.

## DLL release gate

1. Source-control diff contains no DLL source/header/project/schema/binding
   changes for this pass.
2. XML validation proves every approved field uses an existing schema path.
3. Roster checks prove restored baseline features were not reduced.
4. Fresh-game SP and MP smoke checks pass.
5. Enrico remains exact.

If implementation appears to require DLL work, stop: that implementation is
outside the approved contract.
