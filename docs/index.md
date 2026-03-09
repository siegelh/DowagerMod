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

### Engineering / Runbooks

- [`TESTING_WORKFLOW.md`](TESTING_WORKFLOW.md) - `Current`. Local XML and DLL validation flow. Matches [`../tools/test_gate.ps1`](../tools/test_gate.ps1), [`../tools/test_xml.ps1`](../tools/test_xml.ps1), and [`../tools/test_full.ps1`](../tools/test_full.ps1).
- [`MANUAL_SMOKE_TESTS.md`](MANUAL_SMOKE_TESTS.md) - `Current`. Minimum gameplay smoke-test runbook for gameplay-affecting changes.
- [`DLL_TRACING_WORKFLOW.md`](DLL_TRACING_WORKFLOW.md) - `Current`. DLL tracing and logging workflow for [`../third_party/beyond-the-sword-sdk/CvGameCoreDLL/`](../third_party/beyond-the-sword-sdk/CvGameCoreDLL/).
- [`CIV4_UNIT_ART_CRASH_PLAYBOOK.md`](CIV4_UNIT_ART_CRASH_PLAYBOOK.md) - `Current`. Art/XML crash triage workflow.
- [`INDUSTRY_ICON_PIPELINE.md`](INDUSTRY_ICON_PIPELINE.md) - `Current`. Live icon pipeline reference for industry buttons and `GameFont` glyph usage.

### Process / Planning

- [`LEADER_OVERHAUL_PLAN_OF_RECORD.md`](LEADER_OVERHAUL_PLAN_OF_RECORD.md) - `Current process doc`. Overhaul methodology and guardrails. Use it with live XML/DLL verification, not as architecture truth.
- [`plans/README.md`](plans/README.md) - `Current`. Standard location, naming, and expectations for checked-in plan docs.
- [`plans/active/TEMPLATE.md`](plans/active/TEMPLATE.md) - `Current`. Reusable task plan template for non-trivial agent work.

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
