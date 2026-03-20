# Eleanor Roosevelt Leaderhead Prototype (WIP)

- **Last updated:** 2026-03-19
- **Owner:** Symphony Squad – Implementer (art handoff pending)
- **Goal:** Build a Civ IV BTS leaderhead for Eleanor Roosevelt using public-domain WWII-era photos as reference.

## Source References

| Photo | Repository | License | Notes |
|-------|------------|---------|-------|
| Front three-quarter portrait (Oct 1937) | Library of Congress, LC-USZ62-104132 | Public domain (U.S. Gov) | Primary albedo projection; near-neutral lighting. |
| Profile with hat (Dec 1941) | National Archives, Local Identifier 196469 | Public domain | Used for side silhouette and hat volume. |
| Press conference smile (May 1945) | Library of Congress, LC-USW3-016123-D | Public domain | Provides expression data for wrinkles and nasolabial folds. |

Store downloaded TIFF/PNG files under `reference/eleanor_roosevelt/` (not committed) and document any edits (color balance, de-noise) here.

## Toolchain & Settings

| Stage | Tool | Version / Notes |
|-------|------|-----------------|
| Reconstruction | Blender 3.6.5 LTS + KeenTools FaceBuilder 2024.1 | Camera FOV solved per photo metadata (50–55 mm). |
| Sculpt | Blender sculpt mode, 0.5 m unit scale | Separate collections for head, hair, fur collar. |
| Retopology | Quad Remesh 1.4 + shrinkwrap cleanup | Target 24k tris for combined head/torso. |
| Texture bake | Blender cycles bake @ 4k → downscale to 1k for BTS | Keep linear workflow, convert to SRGB before DDS. |
| Rig & animation | Base rig from `ART_DEF_LEADER_VICTORIA` imported via PyNifly commit `ff6f5b7` | Weight transfer with Data Transfer modifier (nearest surface). |
| Export | PyNifly CLI `pynifly export` preset `civ4_leaderhead` | Non-shader copy created by duplicating mesh and disabling shader nodes. |
| Texture compression | `texconv 10.1.3` | Diffuse/spec: `-f DXT5`, normal: `-f BC5_UNORM`. |

## Progress Checklist

- [x] Repo scaffolding created (`CoreFiles/.../Leaderheads/eleanor_roosevelt`, manifest JSON, doc stub).
- [x] Reference photos curated and licensed.
- [ ] FaceBuilder solve – aligned but needs manual adjustment for chin fullness.
- [ ] Sculpt refinement – add period-accurate hairstyle and fur collar.
- [ ] Retopology + UV unwrap.
- [ ] Texture baking + DDS conversion.
- [ ] Rig/skin transfer (Victoria skeleton).
- [ ] Animation binding (reuse Victoria KF set for MVP).
- [ ] XML snippets inserted & validated.
- [ ] `.\tools\test_gate.ps1` run covering new XML.
- [ ] In-game diplomacy smoke test recorded.

## File Expectations

`CoreFiles/.../Assets/Art/Leaderheads/eleanor_roosevelt/`

- `eleanor_roosevelt.nif` / `eleanor_roosevelt_noshader.nif`
- `eleanor_roosevelt.kfm`
- `eleanor_roosevelt_idle_01_friendly.kf` (etc.) – start by copying Victoria clips.
- `eleanor_roosevelt_bg.nif` / `.kfm` (temporary reuse of Victoria background)
- Textures: `eleanor_roosevelt_diff.dds`, `eleanor_roosevelt_nrml.dds`, `eleanor_roosevelt_spec.dds`, `eleanor_roosevelt_env.dds`, `eleanor_roosevelt_env_mask.dds`.
- Button: `Art/LeaderHeads/eleanor_roosevelt_button.dds` (64×64).

Manifest path: `tools/leaderhead_pipeline/configs/eleanor_roosevelt.json`.

## Validation Plan

1. Run `.\tools\test_gate.ps1` after XML hook-up.
2. Install assets into a local BTS copy, launch DowagerMod, and:
   - Start a custom game as Eleanor, ensure portrait loads.
   - Enter diplomacy and cycle through all deal responses.
   - Save/load to ensure no crash.
3. Document observations (lighting, clipping, facial animation quality) back here.

## Outstanding Questions / Risks

- Does reusing Victoria’s animation set create noticeable mismatch (e.g., gesture style) for Eleanor?
- Hat brim may clip through the reused skeleton bones; may require simple bone-driven controllers or soft-body animation.
- Need confirmation on shader choice (non-shader fallback mandatory for low-end users).
