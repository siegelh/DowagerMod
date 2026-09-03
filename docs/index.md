# Docs Index

## How to use this docs tree

- Treat code, imports, configs, scripts, and test gates as primary truth.
- Start with [`../README.md`](../README.md), [`../AGENTS.md`](../AGENTS.md), [`../WORKFLOW.md`](../WORKFLOW.md), [`../ARCHITECTURE.md`](../ARCHITECTURE.md), [`../INSTALLER.md`](../INSTALLER.md), [`../tools/`](../tools/), [`../CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/`](../CoreFiles/Sid%20Meier%27s%20Civilization%20IV%20Beyond%20the%20Sword/Beyond%20the%20Sword/Assets/XML/), [`../CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/Python/`](../CoreFiles/Sid%20Meier%27s%20Civilization%20IV%20Beyond%20the%20Sword/Beyond%20the%20Sword/Assets/Python/), and [`../third_party/beyond-the-sword-sdk/CvGameCoreDLL/`](../third_party/beyond-the-sword-sdk/CvGameCoreDLL/).
- Use docs as support material, not as a substitute for reading the live BtS assets root and current tools.
- When docs and code disagree, trust code/scripts and note the mismatch explicitly.
- Status labels:
  - `Current`: corroborated by current code or scripts
  - `Provisional`: useful now, but not architecture truth
  - `Historical / verify before relying`: archived context only

## Current

### Repo Guidance

- [`../README.md`](../README.md) - `Current`. Human-facing repo entry doc and navigation layer.
- [`../AGENTS.md`](../AGENTS.md) - `Current`. Cold-start instructions for coding agents.
- [`../WORKFLOW.md`](../WORKFLOW.md) - `Current`. Normative task workflow for future agents.
- [`../ARCHITECTURE.md`](../ARCHITECTURE.md) - `Current`. Code-first architecture-as-implemented map.
- [`../INSTALLER.md`](../INSTALLER.md) - `Current`. Canonical installer behavior and packaging caveats centered on `CoreFiles/install.py`.

### Automation

- [`../SYMPHONY_SPEC.md`](../SYMPHONY_SPEC.md) - `Current design spec`. Base service design for Symphony.
- [`../SYMPHONY_REPO_DELTA.md`](../SYMPHONY_REPO_DELTA.md) - `Current repo delta`. DowagerMod-specific adaptation of the base Symphony spec.
- [`../symphony/WORKFLOW.md`](../symphony/WORKFLOW.md) - `Current runtime config`. Machine-readable Symphony workflow and prompt template.
- [`../symphony/README.md`](../symphony/README.md) - `Current`. Scope and usage for the implemented Symphony delivery slice and local worker mode.
- [`../symphony/squad/team.md`](../symphony/squad/team.md) - `Current`. Checked-in squad charter for the local Symphony team model.
- [`../symphony/squad/jobs.yaml`](../symphony/squad/jobs.yaml) - `Current runtime config`. Enabled squad jobs, role sequences, priorities, and concurrency classes.
- [`../symphony/squad/schedule.yaml`](../symphony/squad/schedule.yaml) - `Current runtime config`. Scheduled background cadence for squad jobs.
- [`../tools/Start-Symphony.ps1`](../tools/Start-Symphony.ps1) - `Current`. Start the local Symphony worker for a modding session.
- [`../tools/Symphony-Status.ps1`](../tools/Symphony-Status.ps1) - `Current`. Show local Symphony worker status.
- [`../tools/Stop-Symphony.ps1`](../tools/Stop-Symphony.ps1) - `Current`. Request or force-stop the local Symphony worker.
- [`../tools/Cleanup-Symphony.ps1`](../tools/Cleanup-Symphony.ps1) - `Current`. Dry-run or prune completed Symphony worktrees and local branches.

### Engineering / Runbooks

- [`TESTING_WORKFLOW.md`](TESTING_WORKFLOW.md) - `Current`. Local XML and DLL validation flow. Matches [`../tools/test_gate.ps1`](../tools/test_gate.ps1), [`../tools/test_xml.ps1`](../tools/test_xml.ps1), and [`../tools/test_full.ps1`](../tools/test_full.ps1).
- [`MANUAL_SMOKE_TESTS.md`](MANUAL_SMOKE_TESTS.md) - `Current`. Minimum gameplay smoke-test runbook for gameplay-affecting changes.
- [`DLL_TRACING_WORKFLOW.md`](DLL_TRACING_WORKFLOW.md) - `Current`. DLL tracing and logging workflow for [`../third_party/beyond-the-sword-sdk/CvGameCoreDLL/`](../third_party/beyond-the-sword-sdk/CvGameCoreDLL/).
- [`GLYPH_DIAGNOSTICS.md`](GLYPH_DIAGNOSTICS.md) - `Current`. In-game and offline `GameFont` glyph triage workflow.
- [`CIV4_UNIT_ART_CRASH_PLAYBOOK.md`](CIV4_UNIT_ART_CRASH_PLAYBOOK.md) - `Current`. Art/XML crash triage workflow.
- [`INDUSTRY_ICON_PIPELINE.md`](INDUSTRY_ICON_PIPELINE.md) - `Current`. Live icon pipeline reference for industry buttons and `GameFont` glyph usage.
- [`FLAG_PIPELINE.md`](FLAG_PIPELINE.md) - `Current`. Versioned civilization flag masters, provenance, deterministic fixed-color DXT3 generation, review, validation, and original-design recovery.
- [`CHATTER_OVERVIEW.md`](CHATTER_OVERVIEW.md) - `Current`. Design overview for the AI Leader Chatter feature (Azure Foundry sidecar + game-side hooks).
- [`CHATTER_RUNBOOK.md`](CHATTER_RUNBOOK.md) - `Current`. Operator runbook for the chatter sidecar (setup, run, troubleshoot).

### Process / Planning

- [`LEADER_OVERHAUL_PLAN_OF_RECORD.md`](LEADER_OVERHAUL_PLAN_OF_RECORD.md) - `Current process doc`. Overhaul methodology and guardrails. Use it with live XML/DLL verification, not as architecture truth.
- [`plans/README.md`](plans/README.md) - `Current`. Standard location, naming, and expectations for checked-in plan docs.
- [`plans/active/TEMPLATE.md`](plans/active/TEMPLATE.md) - `Current`. Reusable task plan template for non-trivial agent work.
- [`plans/active/2026-03-10-symphony-pr-handoff.md`](plans/active/2026-03-10-symphony-pr-handoff.md) - `Current active plan`. Next Symphony milestone for validated PR handoff and future job-type evolution.
- [`plans/active/2026-03-12-symphony-local-server.md`](plans/active/2026-03-12-symphony-local-server.md) - `Current active plan`. Local background-worker mode, status reporting, and start/stop controls for modding sessions.
- [`plans/active/2026-03-12-symphony-worktree-cleanup.md`](plans/active/2026-03-12-symphony-worktree-cleanup.md) - `Current active plan`. Conservative cleanup flow for merged/completed Symphony worktrees.
- [`plans/active/2026-03-13-symphony-squad-integration.md`](plans/active/2026-03-13-symphony-squad-integration.md) - `Current active plan`. Squad roles, GitHub-facing job routing, observability, and human workflow for Symphony.
- [`plans/active/2026-03-19-symphony-auto-cleanup-merged-closed.md`](plans/active/2026-03-19-symphony-auto-cleanup-merged-closed.md) - `Current active plan`. Auto-prune clean Symphony worktrees only after merged PR plus closed issue.
- [`plans/active/2026-08-30-versioned-historical-flags.md`](plans/active/2026-08-30-versioned-historical-flags.md) - `Current active plan`. Repository-owned historical flag pipeline, source/history preservation, production adoption, and two-commit delivery.
- [`plans/active/2026-08-31-issue-provided-leader-flags.md`](plans/active/2026-08-31-issue-provided-leader-flags.md) - `Current active plan`. Apply the 56 leader flag images attached to issues #87-#142 while retaining three historical-v1 designs.
- [`plans/active/2026-09-02-staged-diplomatic-incident.md`](plans/active/2026-09-02-staged-diplomatic-incident.md) - `Current active plan`. Add a synchronized two-phase spy mission that frames a selected third civilization and reduces the territory owner's attitude toward it.
- [`plans/active/2026-08-26-harbor-water-food.md`](plans/active/2026-08-26-harbor-water-food.md) - `Implemented; gameplay validation pending`. Class-based Harbor Food from full-BFC water tiles, including Cothon and Admiralty inheritance.
- [`plans/active/2026-07-14-current-release-status.md`](plans/active/2026-07-14-current-release-status.md) - `Current status`. Consolidated landed-commit inventory, remaining manual gates, and explicitly outstanding era-peak audit.
- [`plans/active/2026-07-14-loading-screen-modernization.md`](plans/active/2026-07-14-loading-screen-modernization.md) - `Implemented; visual validation pending`. Sol Patch loading art and preserved custom Dowager/Barclay home scene.
- [`plans/active/2026-07-10-leader-civ-diversity-overhaul.md`](plans/active/2026-07-10-leader-civ-diversity-overhaul.md) - `Implemented; gameplay validation pending`. Historical and gameplay differentiation for the 27 era-specific packages.
- [`plans/active/2026-07-12-remaining-roster-audit.md`](plans/active/2026-07-12-remaining-roster-audit.md) - `Implemented contract`. Additive restoration and protected dispositions for the remaining 32 packages.
- [`plans/active/2026-07-13-great-person-landmark-improvements.md`](plans/active/2026-07-13-great-person-landmark-improvements.md) - `Implemented; gameplay validation pending`. Great Person landmark mechanics, deterministic AI, exact previews, art, and validation contract.
- [`plans/active/2026-07-13-landmark-scale-installer-reliability.md`](plans/active/2026-07-13-landmark-scale-installer-reliability.md) - `Implemented; visual validation pending`. Landmark map-scale reduction to 0.5 and always-mirror installer restoration.
- [`plans/active/2026-07-17-pristine-metadata-validation.md`](plans/active/2026-07-17-pristine-metadata-validation.md) - `Implemented installer guard`. Exact file-count and logical-byte validation for pristine capture and every restore.
- [`plans/active/2026-07-13-unique-civilization-colors.md`](plans/active/2026-07-13-unique-civilization-colors.md) - `Implemented; visual validation pending`. Unique default border colors for all 59 playable civilizations.
- [`plans/active/2026-07-13-experimental-additive-signatures.md`](plans/active/2026-07-13-experimental-additive-signatures.md) - `Implemented experiment; gameplay validation pending`. One reversible historical building-class signature addition for each of the 59 playable packages.
- [`plans/active/2026-07-13-industry-building-output-rebalance-proposal.md`](plans/active/2026-07-13-industry-building-output-rebalance-proposal.md) - `Approved and implemented; balance validation pending`. Complete 69-row industry cost/output rebalance with protected runtime scope.
- [`plans/active/2026-07-12-remaining-roster-expansion.md`](plans/active/2026-07-12-remaining-roster-expansion.md) - `Implemented; runtime validation pending`. Additive restoration and expansion of the 32 playable packages outside the 27-package overhaul.
- [`plans/active/2026-07-12-remaining-roster-implementation-matrix.md`](plans/active/2026-07-12-remaining-roster-implementation-matrix.md) - `Implemented contract`. Exact 32-package disposition and protected values.
- [`plans/active/2026-07-12-remaining-roster-dll-contracts.md`](plans/active/2026-07-12-remaining-roster-dll-contracts.md) - `Satisfied contract`. Confirms the roster pass required no new DLL/schema behavior.
- [`plans/active/2026-07-12-worker-action-gates.md`](plans/active/2026-07-12-worker-action-gates.md) - `Satisfied contract`. Confirms no roster worker-action expansion was authorized or introduced.
- [`../tools/baselines/roster_baseline.json`](../tools/baselines/roster_baseline.json) - `Generated reference`. Commit-pinned playable roster, synchronized InfoType order, and deterministic XML/Python/DLL digest baseline.

### Repo-Local Skills

- [`../skills/`](../skills/) - `Current task aids`. Repo-local skill packages for task-specific workflows. They are workflow references, not runtime truth.

### Third-Party Build Notes

- [`../third_party/README.md`](../third_party/README.md) - `Current supplemental`. Third-party area entry note; build scripts still win over prose.
- [`../third_party/beyond-the-sword-sdk/BUILDING_CVGAMECOREDLL.md`](../third_party/beyond-the-sword-sdk/BUILDING_CVGAMECOREDLL.md) - `Current supplemental`. DLL build details aligned to `tools/build_civ4_dll.ps1`.

## Provisional

- [`art_masterpiece_sources.csv`](art_masterpiece_sources.csv) - `Generated reference`. Reused by the Art Masterpieces generator pipeline; not runtime behavior by itself.

## Archive

- [`archive/README.md`](archive/README.md) - `Historical / verify before relying`. Archive structure and trust rules.
- [`archive/plans/`](archive/plans/) - `Historical / verify before relying`. Superseded plans and saved drafts.
- [`archive/debug/`](archive/debug/) - `Historical / verify before relying`. Dated debugging notes.
- [`archive/ideas/`](archive/ideas/) - `Historical / verify before relying`. Brainstorms and idea backlog.

## Suggested Reading Order

1. [`../README.md`](../README.md)
2. [`../AGENTS.md`](../AGENTS.md)
3. [`../WORKFLOW.md`](../WORKFLOW.md)
4. [`../ARCHITECTURE.md`](../ARCHITECTURE.md)
5. [`../INSTALLER.md`](../INSTALLER.md) if install/package behavior matters
6. [`TESTING_WORKFLOW.md`](TESTING_WORKFLOW.md) and [`MANUAL_SMOKE_TESTS.md`](MANUAL_SMOKE_TESTS.md)
7. Live code and config under the BtS assets root and DLL source
8. Only then consult `Provisional` or archived docs for context
