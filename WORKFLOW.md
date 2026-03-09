# Workflow

This file defines the expected working method for future agents in this repo. It is normative. If older docs describe a different process, follow this file unless a human says otherwise.

## Purpose

- Keep work grounded in the live BtS mod implementation, not in stale plans or historical artifacts.
- Make changes safe, reviewable, and reproducible in a repo that contains mixed-current and legacy material.
- Ensure implementation, validation, and documentation stay in sync.

## Core Policy

- Running code, imports, configs, tests, scripts, and CI are the primary source of truth.
- Existing docs are secondary and must be corroborated when they affect implementation.
- Historical plans, specs, notes, and artifacts are not authoritative unless still reflected in code/config.
- When docs and code disagree, code wins unless a human explicitly says otherwise.
- The mirror under `CoreFiles/Sid Meier's Civilization IV Beyond the Sword` is intentional installer payload, but the default edit target is the BtS assets root: `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets`.
- A few oversized stock archives are intentionally excluded from git; do not treat their absence as task-created deltas.
- Every significant change should update both implementation and corresponding documentation.
- Agents must record assumptions, open questions, and residual risks.

## Task Lifecycle

### 1. Orient

- Restate the task in concrete terms.
- Classify the task surface: XML, Python, DLL, art, installer, tooling, or docs.
- Read first: `README.md`, `AGENTS.md`, `docs/index.md`, `ARCHITECTURE.md`, and `docs/TESTING_WORKFLOW.md`.
- Run `git status --short` before planning or editing.
- Note whether the worktree contains broad intentional mirror noise, generated artifacts, or unrelated user changes.
- Identify the likely runtime path before editing anything.

### 2. Verify Source Of Truth

- Inspect live code/config before trusting prose.
- Start with: `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML`, `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/Python`, `third_party/beyond-the-sword-sdk/CvGameCoreDLL`, and `tools/`.
- If a BtS Python import target is missing, check `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Assets/Python`.
- Record inherited-base dependencies explicitly; do not assume the BtS tree is fully self-contained.
- Remember that git-based changed-file gates include untracked files. A noisy mirror can change what the gate validates.
- Search for imports, call sites, entrypoints, and script/tool usage before using old docs as architecture evidence.

### 3. Plan

- For non-trivial tasks, create or update a checked-in plan doc under `docs/plans/active/`. Use a name like `docs/plans/active/YYYY-MM-DD-short-slug.md`.
- Start new plans from `docs/plans/active/TEMPLATE.md`.
- A task is non-trivial if it:
- touches more than one runtime layer
- changes entrypoints, shared schemas, generators, installers, or DLL-exposed XML capabilities
- affects multiple directories or systems
- includes cleanup or deletion of legacy/transitional material
- starts with unresolved architecture ambiguity
- contradicts an existing doc or plan
- The plan doc must record:
- goal and scope
- affected paths
- validation to run
- assumptions
- unresolved questions
- expected documentation updates
- Small, single-surface fixes may skip a checked-in plan doc, but the agent must still state scope and validation before editing.

### 4. Implement

- Edit the BtS tree first unless the task proves another target is required.
- Do not update base `Assets` or `Warlords` by default.
- Treat `third_party/beyond-the-sword-sdk/CvGameCoreDLL` as the DLL source of truth.
- Do not recreate or use a duplicate `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/CvGameCoreDLL` tree unless a human explicitly directs otherwise.
- Leave `petromod_v1` alone unless the task explicitly touches HUD/main interface behavior.
- Keep edits scoped to the task; do not opportunistically refactor unrelated legacy material.
- If importing external art or reference material, copy it into the repo first.
- If using generator/patch tools, inspect their target paths first; some still write to BtS, base `Assets`, and `Warlords`.
- Never leave XML or Python pointing to external absolute paths outside the repo.

### 5. Validate

- After editing BtS XML, run `.\tools\test_gate.ps1`.
- After editing DLL source, run `.\tools\test_gate.ps1`.
- If XML work may depend on DLL support, run `.\tools\test_gate.ps1 -CheckDll`.
- For broad changes, run `.\tools\test_full.ps1`.
- For any gameplay change, also do a manual smoke test.
- A gameplay change includes XML, Python, DLL, UI, art-reference, entrypoint, and persistence changes that can alter in-game behavior.
- Use `docs/MANUAL_SMOKE_TESTS.md` as the minimum smoke-test runbook.
- If required validation cannot run, stop and escalate to a human instead of declaring the task complete.

### 6. Document

- Update docs in the same task when behavior, paths, workflow, or architecture understanding changes.
- Update `docs/index.md` when a doc becomes current, provisional, or historical.
- Update `ARCHITECTURE.md` when runtime structure or dependency understanding changes materially.
- Update `README.md`, `INSTALLER.md`, or testing runbooks when build/install/validation behavior changes.
- Historical docs should be updated, archived, or marked stale when contradicted.
- If a historical doc is contradicted, do one of these:
- update it
- move it under a clearly historical or archive location
- mark it `Historical / verify before relying`
- Do not leave contradicted docs sounding authoritative.
- If a doc tells agents to follow stale instructions strictly, fix that wording or archive the doc in the same task when practical.

### 7. Summarize Residual Risks

- End each significant task with:
- what changed
- what validation ran
- assumptions made
- unresolved questions
- stale/transitional areas left untouched
- documentation updated or intentionally deferred
- notable worktree noise or unrelated changes that may affect future tasks
- state explicitly if manual smoke testing was not run

## Handling Stale Or Conflicting Docs

- Do not blend stale docs with current code into a false narrative.
- Prefer code, scripts, imports, configs, tests, and runtime wiring.
- If a doc is still useful but not trustworthy, label it rather than deleting it casually.
- If a doc conflict affects future work, either fix the doc in the same task or record the exact follow-up needed.

## When To Escalate To A Human

- The live entrypoint or active asset path cannot be identified.
- BtS versus base `Assets` versus `Warlords` ownership is unclear for the task.
- `petromod_v1` or inherited base Python behavior is involved and the active dependency is uncertain.
- A file import or runtime path appears broken and there is no safe replacement path.
- Validation fails for reasons that may be unrelated to the task.
- The task would delete or reorganize legacy/transitional material with unclear runtime impact.
- Installer or deployment behavior matters and `CoreFiles/install.py` is not sufficient to answer the question.

## Definition Of Done

- The implementation matches the requested task.
- Required validation has passed, or the validation block was explicitly escalated before completion.
- Manual smoke testing has been completed for gameplay changes.
- Relevant docs were updated to match the change.
- A checked-in plan doc exists for non-trivial work.
- Assumptions and unresolved questions were recorded.
- No known contradicted doc was left presenting itself as authoritative.

## What Not To Do

- Do not trust historical docs over live code.
- Do not update base `Assets` or `Warlords` just to "keep things in sync."
- Do not treat duplicate source trees as equally authoritative without verification.
- Do not reference external asset libraries directly from runtime XML or Python.
- Do not mark XML or DLL work complete without running the gate or explicitly escalating the inability to do so.
