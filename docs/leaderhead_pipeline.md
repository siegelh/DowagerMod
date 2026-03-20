# Civilization IV BTS Leaderhead Pipeline

_Last updated: 2026-03-19_

This document captures the research, tooling, and workflow required to build a fully animated Civilization IV: Beyond the Sword (BTS) leaderhead from real-person photo references. It consolidates the answers requested in GitHub issue #56 and maps them onto live DowagerMod assets.

---

## 1. Required BTS Asset Stack

| Asset Type | Required Files | Notes / Source of Truth |
|------------|----------------|-------------------------|
| Geometry & Skin | `.nif` (shader), `.nif` (non-shader fallback) | Lives under `CoreFiles/.../Assets/Art/Leaderheads/<Leader>/`. Mesh must include NiTriShapes for head, body, props, plus NiSkinInstance bound to the Civ4 leader skeleton. |
| Animation Controller | `.kfm` | KFM file references KF clips for greeting, idles, actions, defeat, background loops. Reuse or duplicate from a vanilla leader when retargeting. |
| Animation Clips | `.kf` per emotion | Minimum viable set: `idle_01`–`idle_05`, `greeting`, `action_01_negative`, `action_02_affirmative`. Optional: `lose`, `win`, background loops. |
| Background Set | `*_bg.nif`, `*_bg.kfm`, `*_bg_background.kf`, environment DDSes | Controls the diplomacy room camera, skybox, and parallax props. Can reuse vanilla backgrounds initially. |
| Textures | Diffuse, normal, specular, environment, mask DDS files (DXT1/DXT5) | Example naming: `victoria_diff.dds`, `victoria_nrml.dds`, `victoria_spec.dds`. Buttons live under `Art/LeaderHeads/*.dds` or `Art/Interface/LeaderHeads/*.dds`. |
| Material Metadata | `.settings`, `.anim.h`, `.bg_anim.h` (optional) | Provide shader parameters and states for Firaxis’ art toolchain; keep existing files from base rig unless recompiled. |
| XML Art Entry | `CIV4ArtDefines_Leaderhead.xml` | Defines `<NIF>`, `<KFM>`, `<BackgroundKFM>`, and button art. |
| Gameplay Entry | `CIV4LeaderHeadInfos.xml` | References `<ArtDefineTag>`, sets diplomacy audio/personality stats. |

DowagerMod already ships dozens of vanilla and custom leaderheads under `CoreFiles/.../Assets/Art/Leaderheads/`. These files are our implementation truth for structure, naming, and compression formats.

---

## 2. Reference Breakdown – Dowager Countess

Use `CoreFiles/.../Assets/Art/Leaderheads/DowagerCountess/` plus matching XML entries as the canonical example of a working BTS leaderhead:

* Geometry: `victoria.nif`, `victoria_noshader.nif`
* Animation controller: `victoria.kfm`
* Animation clips: `victoria_idle_01_friendly.kf`, `victoria_idle_05_furious.kf`, `victoria_action_01_negative.kf`, etc. (each mirrors Firaxis’ Catherine/Victoria clip list)
* Background: `victoria_bg.nif`, `victoria_bg.kfm`, `victoria_bg_background.kf`, sky/environment DDS textures
* Textures: `victoria_diff.dds`, `victoria_nrml.dds`, `victoria_spec.dds`, accessory/env DDSes
* Button art: `Art/LeaderHeads/dowager_button.dds`
* XML linkages:
  * `CIV4ArtDefines_Leaderhead.xml` entry `ART_DEF_LEADER_DOWAGER_COUNTESS`
  * `CIV4LeaderHeadInfos.xml` entry `LEADER_DOWAGER_COUNTESS`

This breakdown answers Technical Questions 1–3 & 6 in the issue body: we can inspect these files directly, copy the structure, and confirm Civ4 expects Gamebryo `.nif/.kfm/.kf` plus DDS textures and ArtDefines/XML references.

---

## 3. Toolchain Overview

| Stage | Recommended Tooling | Reason |
|-------|---------------------|--------|
| Photo capture & cleanup | High-res public-domain photos; optional Photoshop/GIMP color correction | BTS textures top out around 1024²; start with quality lighting. |
| Head reconstruction | Blender 3.6 LTS + KeenTools FaceBuilder (or InSilico FaceBuilder), or free photogrammetry (RealityCapture CLI / Meshroom) | Produces a mesh that matches supplied photos with camera solving. |
| Retopology & UVs | Blender (Quad Remesh, Bsurfaces) + Instant Meshes | Civ4 meshes perform best with 20k–25k tris for head/torso combined. |
| Texture baking | Blender’s texture bake, Substance Painter, or ArmorPaint | Bake diffuse/albedo, normal, curvature, and masks into the UV set expected by Civ4. |
| Clothing/hair sculpt | Blender sculpt mode; hair cards via Geometry Nodes | Keeps everything in one DCC package. |
| Rigging & skinning | Blender with Rigify disabled; instead import Firaxis skeleton using updated NifTools or PyNifly and transfer weights via Data Transfer modifier. |
| Animation reuse | Import vanilla `.kf` via PyNifly, retarget to the new mesh using bone names. Custom animations can be authored with Blender’s Action system and exported to KF. |
| NIF/KF/KFM export | PyNifly (https://github.com/niftools/pynifly) or the civilopedia-friendly Blender NIF plugin fork that targets Gamebryo 20.2.0.7. | Maintains compatibility with Civ4’s NiController sequences and NiTriStrips. |
| Texture conversion | Compressonator CLI or `texconv.exe` (DXT1/DXT5), fallback: GIMP DDS export | Civ4 requires DDS with correct mipmaps; use SRGB for diffuse, linear for normal/spec. |
| Validation | NifSkope 2.0 Dev 7, `tools/test_gate.ps1`, in-game diplomacy smoke test | Ensures NiSkinInstance, NiMaterialProperty, shader flags, and XML hooks are valid. |

Automation boundaries:

* Reconstruction & sculpting still need a human artist, but the workflow standardizes file locations and rig expectations.
* Export/packaging is scriptable (see Section 8).

---

## 4. Photo → 3D Workflow (Phase 2 of the issue)

1. **Collect references**: minimum of front, 45°, and side photos with neutral expression. Document source URLs and licensing in the prototype doc.
2. **FaceBuilder solve**: in Blender, run FaceBuilder to project the photos onto the neutral mesh. Adjust camera FOV per photo metadata.
3. **Sculpt refinement**: add asymmetry, wrinkles, and clothing volumes. Keep hair as separate meshes for easier normal/spec baking.
4. **Retopology**: shrinkwrap a production mesh onto the sculpt. Use 1 UV set for skin, optional second for clothing if needed.
5. **Texture baking**:
   * Bake albedo from photo projections into `leader_diffuse.png`.
   * Generate normal from high poly (tangent space) and convert to BC5/DXT5_NM for Civ4.
   * Create spec/gloss masks – Civ4 expects grayscale spec in the alpha channel of `*_spec.dds`.
   * Prepare environment mask (white where reflective, black otherwise) for `*_env_mask.dds`.
6. **Rig transfer**:
   * Import a vanilla leader skeleton + mesh (closest body type) via PyNifly.
   * Use Blender’s Data Transfer to copy vertex groups and weights to the new mesh.
   * Test deformations with sample poses to ensure eyelids and jaw behave correctly.
7. **Animation binding**:
   * Keep the reused skeleton bone names identical to the source KFM.
   * Optionally author new Actions (greeting, idle) and export as KF.
8. **Export**:
   * Export main mesh to `.nif` (shader) with NiTriStrips.
   * Duplicate and simplify materials for non-shader `.nif`.
   * Export `.kfm` referencing either reused or newly authored `.kf` files.
   * Export background `.nif/.kfm` or reuse a vanilla scene.
9. **Texture conversion**: run `texconv -f DXT5` for diffuse/spec/normal as appropriate; ensure mipmaps.
10. **Packaging**: run `tools/leaderhead_pipeline/scaffold_leaderhead.py` (Section 8) to stage directories, then drop exported files into the path it creates.

---

## 5. Base Rig / Skeleton Strategy

* Civ4 leaderheads share a common bone hierarchy (Pelvis → Spine → Neck → Head → Facial bones). Reusing an existing Firaxis rig is the safest way to avoid animation or shader crashes.
* Selection criteria:
  * Match posture (standing vs seated) and clothing mass (armor vs gown).
  * Pick a rig with similar facial bone coverage (Victoria, Boudica, Suleiman, etc.).
* Implementation steps:
  1. Import the reference leader `.nif` into Blender via PyNifly.
  2. Keep the `NiNode` names identical; do not rename bones.
  3. Use Blender’s `Armature Deform` with vertex groups and copy weights.
  4. If you need new bones (e.g., hat tassels), parent them under an unused extra node and keyframe them manually, but retain the base hierarchy for compatibility.
* Output: Document which base rig was used in `docs/leaderhead_pipeline/prototypes/<slug>.md` so future artists know where the animation set originated.

---

## 6. Animation Compatibility Plan

Minimum animations to ship (all `.kf` referenced inside `.kfm`):

| Clip | Purpose | Source Example (`DowagerCountess`) |
|------|---------|------------------------------------|
| `idle_01_friendly` .. `idle_05_furious` | Emotion-specific loops used when diplomacy attitude changes | `victoria_idle_01_friendly.kf` etc. |
| `greeting` | Played once when entering diplomacy | `victoria_greeting.kf` |
| `action_01_negative` | Reaction to a negative proposal | `victoria_action_01_negative.kf` |
| `action_02_affirmative` | Reaction to a positive proposal | `victoria_action_02_affirmative.kf` |
| `lose` / `win` (optional) | Endgame scenes | Borrow from closest vanilla leader if not authored. |
| Background loop | `*_bg_background.kf` controlling camera move/prop sway | Reuse vanilla background until a custom scene is modeled. |

Implementation approach:

1. Start by referencing the exact KFM (e.g., Victoria’s) so Civ4 loads proven clips.
2. Once the new mesh deforms correctly, author new KF clips by keyframing in Blender. Export via PyNifly with identical bone names and track identifiers.
3. Update the `.kfm` (or use NifSkope) to point to your new KF files.
4. Record animation coverage status in the prototype doc.

---

## 7. Texture / Material Pipeline

* **Diffuse (`*_diff.dds`)** – Color map, SRGB, DXT5 with alpha reserved for transparency (lace, veils). Use at most 1024×1024 to stay in BTS limits.
* **Normal (`*_nrml.dds`)** – Tangent-space, store X in alpha, Y in green (BC5). Generated from sculpt hi-poly.
* **Specular (`*_spec.dds`)** – Grayscale + alpha packing for gloss/roughness. Controls highlight intensity.
* **Environment mask (`*_env_mask.dds`)** – White where reflective metal/jewels, black elsewhere. Combined with `*_env.dds`.
* **Environment cube/sphere (`*_env.dds`, `*_env2.dds`)** – Usually reused from vanilla leaders unless a unique scene is required.
* **Background textures** – `*_bg.dds`, `*_sky.dds` etc. Reuse until custom backgrounds exist.
* Buttons (`Art/LeaderHeads/<slug>_button.dds`) – 64×64 DXT3, contain leader portrait for UI.

Recommended workflow:

1. Author textures in linear color space, export PNG/TGA.
2. Use Compressonator CLI: `compressonatorcli input.png output.dds -fd DXT5 -mipmaps`.
3. Run `tools/leaderhead_pipeline/verify_textures.py` (future work) to ensure dimensions and compression match expectations.
4. Document texture ownership and source references in the prototype doc.

---

## 8. Packaging & Repo Tooling

### New helper: `tools/leaderhead_pipeline/scaffold_leaderhead.py`

This script (added in this issue) standardizes how we stage new leaderhead assets inside the repo.

```
python tools/leaderhead_pipeline/scaffold_leaderhead.py ^
  --name "Eleanor Roosevelt" ^
  --slug eleanor_roosevelt ^
  --art-def ART_DEF_LEADER_ELEANOR_ROOSEVELT ^
  --base-art-def ART_DEF_LEADER_VICTORIA
```

What it does:

1. Creates `CoreFiles/.../Assets/Art/Leaderheads/<slug>/` with a README stub describing required files.
2. Generates `tools/leaderhead_pipeline/configs/<slug>.json` manifest listing expected file names (NIF/KFM/KF/texture/button paths).
3. Creates `docs/leaderhead_pipeline/prototypes/<slug>.md` populated with a build log template so artists can document photo sources, rig choice, pending tasks, and validation status.
4. Echoes XML snippets you can paste into `CIV4ArtDefines_Leaderhead.xml` and `CIV4LeaderHeadInfos.xml` once the art is ready.

Future automation hooks:

* A `bundle` subcommand could zip the art tree and emit ready-to-commit XML patches.
* Texture verification and DDS metadata checks can be added as separate scripts inside the same folder.

### Repository structure for leaderheads

```
CoreFiles/Sid Meier's Civilization IV Beyond the Sword/
└─ Beyond the Sword/Assets
   ├─ Art/Leaderheads/<slug>/  ← exported meshes, KFMs, textures
   ├─ Art/Interface/LeaderHeads/<slug>_btn.dds
   └─ XML
      ├─ Art/CIV4ArtDefines_Leaderhead.xml (art references)
      └─ Civilizations/CIV4LeaderHeadInfos.xml (gameplay definition)
docs/
└─ leaderhead_pipeline/prototypes/<slug>.md  ← build log
tools/leaderhead_pipeline/
 ├─ scaffold_leaderhead.py
 └─ configs/<slug>.json
```

---

## 9. Prototype Work – Eleanor Roosevelt (WIP)

We selected **Eleanor Roosevelt** as the first photo-driven prototype because her imagery is public-domain (U.S. federal photographer, e.g., Library of Congress LC-USZ62-104132) and she fits DowagerMod’s planned civ roster.

Current status (see `docs/leaderhead_pipeline/prototypes/eleanor_roosevelt.md` for details):

* ✅ Scaffolded repo directories and manifest via the new tool.
* ✅ Documented reference photos and licensing.
* 🔄 FaceBuilder solve in progress (needs manual cleanup to address hat occlusion).
* 🔄 Texture baking pending after sculpt refinements.
* 🔄 Rig transfer planned to reuse `ART_DEF_LEADER_VICTORIA`.
* ⛔ KF customization not yet authored (will reuse Victoria animations for the first playable test).
* ⛔ In-game validation pending once textures/exports are ready.

Risks:

* Photogrammetry reconstruction struggles with historical lighting; manual paint-over needed.
* Hat and fur collar increase poly count—must stay within Civ4 performance limits.

---

## 10. Validation & Testing Expectations

1. **Automated**: `.\tools\test_gate.ps1` whenever XML art defines or leader infos change.
2. **Art sanity**: open exported `.nif` and `.kfm` in NifSkope, check for missing textures, NiSkinInstances, and animation references.
3. **In-game smoke test** (`docs/MANUAL_SMOKE_TESTS.md`):
   * Install updated assets into the live Civ4 BTS folder.
   * Launch DowagerMod, open the Civ selection screen to ensure portrait loads.
   * Use WorldBuilder to spawn the leader and open diplomacy to verify animations, background, and buttons.
   * Cycle through diplomacy states (gift gold, refuse deal) to trigger every animation clip.
   * Save/load once to confirm no serialization issues.

Document every validation run inside the prototype doc so reviewers know which steps were performed.

---

## 11. Automation vs Manual Effort

| Step | Automatable? | Plan |
|------|--------------|------|
| Directory scaffolding | ✅ | `scaffold_leaderhead.py` |
| Photo cleanup | ❌ | Manual artist work |
| Head reconstruction | ⚠️ | Semi-automated using FaceBuilder; still needs supervision |
| Retopology & rigging | ⚠️ | Assisted with Blender modifiers but requires manual review |
| Animation retargeting | ✅ for reuse, manual for bespoke clips | Provide Blender Action templates |
| DDS conversion | ✅ | Future `convert_textures.py` script will batch-run `texconv` |
| XML updates | ⚠️ | We can auto-generate snippets but still want manual review |
| In-game validation | ❌ | Requires human to launch BTS |

---

## 12. Next Steps / Open Questions

1. Finish the Eleanor Roosevelt prototype: bake textures, export NIF/KFM, integrate into XML, and run diplomacy smoke tests.
2. Extend `scaffold_leaderhead.py` with a `--bundle` option that zips the leaderhead folder and emits XML patches automatically.
3. Evaluate whether we can share a pre-weighted “neutral body” mesh to accelerate future leaders.
4. Decide if we need a separate facial animation standard (blendshapes) beyond the vanilla bone rig.

Please record new findings in this doc and update `docs/index.md` whenever the pipeline evolves.
