# Leaderhead Pipeline Helper Scripts

This folder hosts lightweight automation that supports the photo-to-leaderhead workflow described in `docs/leaderhead_pipeline.md`.

## `scaffold_leaderhead.py`

Creates all repo-side scaffolding for a new leaderhead:

1. Art directory under `CoreFiles/.../Assets/Art/Leaderheads/<slug>/` with a drop-in checklist.
2. Prototype build-log doc under `docs/leaderhead_pipeline/prototypes/<slug>.md`.
3. JSON manifest under `tools/leaderhead_pipeline/configs/<slug>.json` that records file expectations (NIF, KFM, KF, textures, button, XML snippets).

### Usage

```
python tools/leaderhead_pipeline/scaffold_leaderhead.py ^
  --name "Eleanor Roosevelt" ^
  --slug eleanor_roosevelt ^
  --art-def ART_DEF_LEADER_ELEANOR_ROOSEVELT ^
  --base-art-def ART_DEF_LEADER_VICTORIA
```

Options:

| Flag | Description |
|------|-------------|
| `--name` | Display name (used in docs + manifest). |
| `--slug` | Filesystem-friendly identifier. Defaults to snake_case of name. |
| `--art-def` | Target `ART_DEF_LEADER_*` tag. Autofills from slug if omitted. |
| `--base-art-def` | Existing art define whose animations/rig you plan to reuse. |
| `--force` | Overwrite existing manifest/doc/art README if you need to regenerate. |

The script prints ready-to-paste XML snippets for `CIV4ArtDefines_Leaderhead.xml` and `CIV4LeaderHeadInfos.xml`, but it does **not** edit those files automatically. Keep XML edits manual until we finish end-to-end validation.

## Future Helpers

Reserved namespace for:

- `bundle_leaderhead.py` – zip art assets and emit XML patches.
- `verify_textures.py` – ensure DDS compression/size requirements.
- `kf_report.py` – list animation clips referenced by a `.kfm`.
