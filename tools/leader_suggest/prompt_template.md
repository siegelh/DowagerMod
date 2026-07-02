# DowagerMod — New Leader/Civ Suggestion Prompt

You are designing new **leaders and civilizations** for DowagerMod (a Civilization IV:
Beyond the Sword overhaul) that **reuse currently-unused leaderhead art** already present in
the repo.

## The pattern (required)

For each proposal, follow the mod's established 1:1 pattern:

- **One NEW leader** paired with **exactly one civilization**.
- The leader gets **exactly one bespoke custom trait** (`TRAIT_*`) that does **not** already
  exist — it is designed specifically for this leader (mirroring existing custom traits like
  `TRAIT_STALIN`, `TRAIT_ROOSEVELT`, `TRAIT_VICTORIA`).
- The leader + civilization + custom trait are designed **together** as a coherent unit.

## Hard rules

{RULES}

## Live game context

{CONTEXT}

## Output

Return JSON conforming to `tools/leader_suggest/suggestion_spec.schema.json`:
a top-level object with a `proposals` array. Copy `leaderhead.nif` / `leaderhead.kfm`
**verbatim** from the candidate table so the art wiring is guaranteed valid. Then run:

```
python tools/leader_suggest/suggest_leaders.py validate <your_proposals.json>
```

## Unused leaderhead candidates

Each row is a verified-unused, on-disk leaderhead you may reuse. `nif`/`kfm` are the
Assets-relative model paths to copy into `leaderhead`.

{CANDIDATES}
