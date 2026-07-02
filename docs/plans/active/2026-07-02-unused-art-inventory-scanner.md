# Unused Art Inventory Scanner + Manifest (Foundation for LLM-Suggested Leaders/Civs)

- Status: `in_progress`
- Owner / agent: @hasiegel_microsoft (with Copilot CLI)
- Last updated: `2026-07-02`

## Problem Statement

- Task: Build the foundation layer of a framework that lets an LLM suggest new leaders
  and civilizations which reuse **currently unused** art assets (leaderheads, units,
  buildings). This first slice is a deterministic **inventory scanner** that produces an
  LLM-readable **manifest** of unused art. Suggestion and XML generation are later phases.
- Current observed behavior: The mod references 60 leaderheads, 4,443 unit art-defines,
  and 658 building art-defines, but the on-disk art tree contains far more (base
  `Leaderheads`/`Units`/`Structures` plus large imported libraries `BTG` ~4,750 files and
  `Caveman2Cosmos` ~29,878 files). There is **no tool** that identifies which art is unused.
- Why this is a real repo/code problem: Adding a leader/civ here is XML-only (no DLL
  rebuild), and the main historical failure mode is bad/missing art paths crashing the game.
  A reliable "what art exists but isn't wired up" inventory is the missing sensing layer that
  makes safe, art-grounded content suggestion possible.

## Why This Matters

- User/gameplay impact: Unlocks a repeatable path to add thematically-coherent new
  leaders/civs cheaply by reusing art already present in the repo, instead of commissioning
  new art or leaving thousands of imported assets dormant.
- Maintenance / workflow / agent impact: Gives future agents (and the LLM suggestion phase)
  a structured, evidence-backed catalog to reason over. The bonus `dangling_art_refs` output
  also surfaces referenced-but-missing art that is a latent crash risk today.

## Scope

- In scope: A Python 3 (stdlib-only) scanner `tools/art_inventory.py` that (a) extracts all
  referenced art paths from XML, (b) enumerates on-disk art files, (c) diffs them, and
  (d) emits a rich grouped manifest plus flat CSV plus a dangling-refs report.
- In scope: Scan **all** art trees including `Caveman2Cosmos` (widest candidate pool).
- In scope: Rich manifest — leaderheads clustered by folder with inferred subject/era/culture
  keywords and same-folder/name-matched candidate units & buildings attached. Each asset
  carries a `source_tier` field (`base-game` / `BTG` / `caveman2cosmos`).
- In scope: Generated outputs are checked into the repo under `docs/art_inventory/`
  (grouped JSON + flat CSV + dangling CSV).

## Non-Goals

- Not building the LLM suggestion step (choosing which leaders/civs to add).
- Not building the XML generator that applies a chosen leader/civ spec.
- Not changing any BtS XML, DLL source, or game art. This phase only adds a tool + generated
  docs.
- Not rendering `.dds` thumbnails (deferred; would add a Pillow dependency).

## Trusted Sources Of Truth

- Primary code/config/scripts:
  - `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Art/CIV4ArtDefines_*.xml`
    (referenced-art tables: Leaderhead, Unit, Building, Civilization, Misc, Interface, Bonus,
    Improvement, Feature, Terrain, Movie, Route).
  - `.../Beyond the Sword/Assets/Art/**` (on-disk art: Leaderheads, Units, Structures, BTG,
    Caveman2Cosmos).
- Runtime entrypoints/import paths to verify: N/A for the scanner (offline tool), but the
  art-path format (`art/...` relative to `Assets/`, atlas-style `Button`) must match how the
  game loads art — verified from `CIV4ArtDefines_Leaderhead.xml` (`<NIF>art/LeaderHeads/DowagerCountess/victoria.nif</NIF>`)
  and `CIV4ArtDefines_Unit.xml` (`<NIF>Art/Units/Lion/Lion.nif</NIF>`).
- Validation scripts/tests/hooks: `tools/test_gate.ps1` (not strictly required — no BtS XML
  or DLL change). Sanity check: referenced-leaderhead count from the scanner should ≈ 60.

## Existing Docs / Plans Trust Review

- Reviewed docs/plans:
  - Session discovery context `files/repo-discovery-context.md` §A — `trusted for this task`
    (counts and art-tree landscape gathered this session).
  - `docs/CIV4_UNIT_ART_CRASH_PLAYBOOK.md` — `trusted for this task` (motivates the
    dangling-refs output and art-path validation emphasis).
  - `skills/civ-leader-overhaul-architect`, `skills/detailed-overhaul-v2` — `useful context
    only` (design skills; their `scan_mechanics.ps1` is a pattern reference, not art audit).
  - Leaderhead-pipeline PRs #57/#59/#61 — `historical / verify before relying` (all closed,
    unmerged; `tools/leaderhead_pipeline/` is not in the tree).
- Conflicts with code/config/scripts: None material for this tool.

## Potentially Stale Or Conflicting Materials

- Item: `tools/leaderhead_pipeline/` referenced by closed PRs.
  - Why it may be stale: PRs #57/#59/#61 were closed unmerged.
  - What code/config overrode it: The path does not exist in the current checkout.
- Item: `ARCHITECTURE.md` / `CHATTER_OVERVIEW.md` chatter-transport wording.
  - Why it may be stale: unrelated to art inventory, but noted as repo drift in discovery.
  - What verified it: live `CvLeaderChatter.py` (out of scope here).

## Affected Files / Directories

- Primary implementation paths:
  - `tools/art_inventory.py` (new scanner)
  - `docs/art_inventory/unused_art_manifest.json` (generated, rich/grouped)
  - `docs/art_inventory/unused_art_manifest.csv` (generated, flat)
  - `docs/art_inventory/dangling_art_refs.csv` (generated, referenced-but-missing)
- Adjacent paths to inspect (read-only): the ArtDefines XML and `Assets/Art/**` trees above.
- Paths to avoid unless evidence requires them: any BtS gameplay XML, DLL source,
  `petromod_v1`, base `Assets`/`Warlords`.

## Assumptions That Need Human Confirmation

- Assumption: A model file (`.nif`/`.kfm`) not referenced by any `.nif/.kfm/.dds` string in
  any XML is genuinely "unused."
  - Why it matters: Determines the manifest's core definition of unused.
  - What changes if false: If some art is loaded by DLL/Python convention (not XML), it could
    be falsely flagged. Mitigation: the broad all-XML string pass; and we treat the manifest
    as *candidates*, not ground truth, for the human/LLM to vet.
- Assumption: Checking the generated manifest into `docs/art_inventory/` is acceptable despite
  potential large CSV size from C2C. RESOLVED: user chose to check in JSON + both CSVs.
  - Why it matters: Repo hygiene / diff noise.
  - What changes if false: Revisit and gitignore the large CSV, or write to the session
    workspace instead.

## Proposed Implementation Steps

1. Verify live art-path format and confirm the full set of ArtDefines files to parse.
2. Implement `tools/art_inventory.py`:
   - Referenced set: parse ArtDefines path tags + a broad all-XML `.nif/.kfm/.dds` regex pass;
     normalize (lowercase, `/`, strip atlas suffix, unify `art/` prefix).
   - On-disk set: walk configured art roots for `.nif/.kfm/.dds`; normalize to Assets-relative.
   - Diff → unused; also compute referenced-but-missing (dangling).
   - Classify by type (leaderhead / unit / building/structure) via path heuristics.
   - Enrich/group: cluster leaderheads by folder; infer subject/era/culture via a keyword
     dictionary; attach same-folder/name-token-matched units & buildings.
   - Emit JSON + CSV + dangling CSV + console summary. Make art roots and output dir CLI flags.
3. Run the scanner; sanity-check (referenced leaderheads ≈ 60; dangling list reviewed).
4. Update `docs/index.md` (new `docs/art_inventory/` generated artifacts) and note the tool in
   `ARCHITECTURE.md` tooling list. Record the framework's later phases as follow-ups.
5. Validation: run the scanner successfully; optional `tools/test_gate.ps1` for hygiene.

### Task-Specific Steps

1. Set up a fresh worktree off `agent-baseline-leader-chatter`: branch
   `agent-baseline-leader-chatter-new-leader-civ-tooling`, fully up to date with the baseline;
   merge back to the baseline branch when done.
2. Build and iterate on the scanner against the live art trees.
3. Decide manifest check-in vs gitignore based on actual output size.

## Validation Plan

- Required automated checks: run `python tools/art_inventory.py` to completion without error;
  assert referenced-leaderhead count ≈ 60 as a self-check.
- Required repo scripts: `.\tools\test_gate.ps1` (optional here — no BtS XML/DLL change).
- Required manual smoke test: **N/A** — this phase does not change game behavior; no in-game
  smoke test is required. (Manual smoke testing WILL be required once the generator phase
  actually adds leaders/civs to XML.)
- Validation blocked or not yet runnable: none anticipated.

## Documentation Updates Required

- Docs to update: `docs/index.md` (add `docs/art_inventory/` generated artifacts + the tool),
  `ARCHITECTURE.md` tooling section (add `tools/art_inventory.py`).
- Docs/plans to mark stale/superseded: none.
- `ARCHITECTURE.md` / `WORKFLOW.md` / runbook updates: minor tooling note in `ARCHITECTURE.md`.

## Risks / Rollback

- Main risks: false "unused" flags (art loaded outside XML); false "dangling" flags due to
  path-normalization mismatches (case, `art/` prefix, atlas syntax); large manifest size (C2C).
- Likely failure modes: normalization edge cases causing over/under-counting.
- Safe rollback approach: the tool + generated docs are additive and isolated; delete
  `tools/art_inventory.py` and `docs/art_inventory/` to fully revert. No game files touched.
- Paths that should not be touched during rollback: any `Assets/**` game content.

## Open Questions

- ~~Check the generated CSV into the repo, gitignore it, or session-only?~~ RESOLVED: check in
  JSON + both CSVs under `docs/art_inventory/`.
- ~~Constrain the suggestion phase to base-game + BTG art?~~ RESOLVED: no scan-time restriction;
  tag each asset with a `source_tier` and decide at Phase 2 suggestion time.
- ~~Promote `dangling_art_refs` into a `test_gate` check?~~ DEFERRED: revisit after seeing how
  many dangling refs the first scan finds.

## Completion Checklist

- [ ] Trusted sources of truth were verified from code/config/scripts.
- [ ] Existing docs/plans in this area were reviewed and classified for trustworthiness.
- [ ] Assumptions needing human confirmation were recorded.
- [ ] Implementation steps were completed or explicitly deferred.
- [ ] Required validation ran and results were recorded.
- [ ] Required manual smoke test ran, or the blocker was escalated (N/A this phase).
- [ ] Related docs were updated or explicitly deferred with reason.
- [ ] Residual risks and open questions were summarized.

## Final Outcome Summary

- What changed: Added `tools/art_inventory.py` (stdlib Python 3) and generated
  `docs/art_inventory/` (`unused_art_manifest.json`, `unused_art_manifest.csv`,
  `dangling_art_refs.csv`, `README.md`). Updated `docs/index.md` and `ARCHITECTURE.md`.
- Results (first run): 40,479 on-disk art files vs 9,089 referenced tokens →
  33,165 unused candidates (unit 11,460 / leaderhead 6,745 / building 5,127 / other 9,833;
  base-game 8,194 / BTG 2,837 / C2C 22,134). **285 model-backed candidate leaderhead folders**
  + 72 DDS-only portrait leaderheads; 24 in-use folders correctly excluded.
- Validation: `python tools/art_inventory.py` runs clean; `py_compile` OK; `.\tools\test_gate.ps1`
  passes (Py2.4 check + XML; no BtS XML/DLL changed). Manually verified in-use leaders
  (Dowager, Victoria, Lincoln) are NOT misflagged; sampled candidates are real figures
  (Theodore Roosevelt, Hirohito, Attila, Nebuchadnezzar, Caligula…).
- Key finding: `dangling_art_refs` is noisy because stock art lives in git-excluded `.fpk`
  archives → documented; NOT suitable as a gate without `.fpk`-awareness (answers deferred Q3).
- Remaining risks: keyword era/culture enrichment is best-effort; C2C nested-path refs inflate
  dangling; JSON is a curated grouped view (full flat data is in the CSV).
- Follow-up tasks: Phase 2 (LLM suggestion over the manifest); Phase 3 (XML generator +
  art-path existence validation + smoke test); optional `.fpk`-aware dangling gate.
