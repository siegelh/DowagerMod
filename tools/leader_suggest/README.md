# Leader/Civ Suggestion Harness (Phase 2)

Turns the Phase 1 unused-art manifest (`docs/art_inventory/`) into an LLM-ready prompt, and
validates the LLM's structured proposals back against the manifest and the live game data.

**Core pattern:** each NEW leader gets exactly **one bespoke custom trait** and is paired
**1:1 with a single civilization** — the leader + civ + trait are designed together (mirroring
the mod's existing `TRAIT_STALIN` / `TRAIT_ROOSEVELT` per-leader traits).

## Files

| File | Role |
| --- | --- |
| `suggest_leaders.py` | CLI harness (`build-input`, `validate`). Stdlib only. |
| `suggestion_spec.schema.json` | Output contract for a proposals batch. |
| `prompt_template.md` | Prompt scaffold filled by `build-input`. |

## Workflow

1. **Build the prompt** (reads manifest + live XML context, picks curated unused leaderheads):
   ```powershell
   python tools\leader_suggest\suggest_leaders.py build-input --out-dir docs\art_inventory
   ```
   Writes `docs/art_inventory/prompt_input.json` (structured facts) and `prompt.md`
   (human/LLM-facing instructions + candidate table).

2. **Generate proposals** — hand `prompt.md` (or `prompt_input.json`) to any LLM. It returns a
   JSON batch conforming to `suggestion_spec.schema.json`. Leaderhead `nif`/`kfm` must be copied
   verbatim from the candidate table so the art wiring is guaranteed valid.

3. **Validate**:
   ```powershell
   python tools\leader_suggest\suggest_leaders.py validate <proposals.json>
   ```
   Checks, per proposal:
   - `leader_type` / new `civilization_type` / `custom_trait` are **unique and new** (not
     already in the live XML, not duplicated within the batch);
   - `favorite_civic` and (for a new civ) `art_style` are valid live types;
   - `leaderhead.nif` and `.kfm` are **unused, on-disk** art (present in the manifest CSV);
   - any `unique_unit` / `unique_building` art is likewise unused.
   Exits non-zero on any hard error.

## Candidate selection & confidence

`build-input` ranks unused leaderhead folders by source tier (base-game > BTG > C2C) and
enrichment hints, and picks a main `nif`/`kfm` pair per folder. It flags
`model_pair_confidence`:

- **high** — the `nif` and `kfm` share a base name (render as a coherent pair).
- **low** — no shared-base pair found; a human should verify the art before shipping.

**Caveat:** many imported leaderheads reuse a stock animation `.kfm` with a custom mesh, so a
`high`-confidence pair guarantees the art *loads*, not that the face matches the label. Confirm
visual identity with an in-game smoke test (Phase 3).

## Demo

`docs/art_inventory/suggested_leaders.sample.json` is a validated 4-proposal demo batch
(Seleucus/Seleucids, Kanishka/Kushans, Franz Joseph/Austria-Hungary, Suppiluliuma/Hittites).

## Not in scope (Phase 3)

Applying a validated proposal to XML (leader/civ/trait/UU/UB + text + art defines per the
`docs/plans/active/2026-07-02-unused-art-inventory-scanner.md` §A.2 checklist), art-path
existence validation, `test_gate`, and manual smoke test.
