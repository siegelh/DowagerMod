# Art Inventory (generated)

Phase 1 of the framework for **LLM-suggested new leaders/civilizations that reuse currently
unused art**. These files are **generated** by `tools/art_inventory.py` — do not hand-edit;
regenerate instead:

```powershell
python .\tools\art_inventory.py
```

## Files

| File | What it is |
| --- | --- |
| `unused_art_manifest.json` | Tight, LLM-facing **grouped** view: summary + candidate leaderhead folders (with era/culture hints and linked candidate units/buildings) + DDS-only portrait leaderheads. |
| `unused_art_manifest.csv` | **Exhaustive** flat per-asset rows (`type, source_tier, inferred_name, folder, ext, era_hints, culture_hints, path`) for every unused candidate. |
| `dangling_art_refs.csv` | Referenced-but-missing art paths. **See caveat below.** |

## What "unused" means

An on-disk art file (`.nif/.kfm/.dds/.tga`) under one of the candidate roots
(`Art/{Leaderheads, Units, Structures, BTG, Caveman2Cosmos}`) that is not referenced by any
`.nif/.kfm/.dds` path anywhere in the `Assets/XML` tree.

- Leaderhead **groups** are folders that contain a real model (`.nif`/`.kfm`) and whose models
  are entirely unreferenced. Folders already in use (with only stray unreferenced textures) are
  excluded, as are model-less folders.
- **Portrait-only** leaderheads are DDS-only folders (common in Caveman2Cosmos
  `custom_leaderheads/`). They can be reused only if paired with a generic diplomacy model, so
  they are listed separately.
- Each asset carries a `source_tier` (`base-game` / `BTG` / `caveman2cosmos`) so a later
  suggestion phase can prefer higher-quality art without re-scanning.

## Caveat: dangling references are NOISY here

The repo mirror intentionally omits the oversized stock archives (`Assets[012].fpk`), so a large
share of `dangling_art_refs.csv` entries (stock `interface/`, `terrain/`, `units/` art) are
**false positives** — those files exist in a real game install, just packed inside `.fpk`.
Additionally, some imported libraries reference nested paths that differ from the on-disk layout.
Treat this report as a lead list, not ground truth, and **do not gate CI on it** without making
it `.fpk`-aware first.

## Regeneration notes

- Pure Python 3 standard library; safe to run from any machine with the repo checked out.
- Reads only; writes only into this folder. Changes nothing in the game tree.
- Options: `--assets-root`, `--candidate-roots`, `--out-dir` (see `--help`).
