# Thirteen-Leader Expansion

- Status: `in_progress`; four native packages integrated; native extensions next.
- Owner / agent: repository owner / GitHub Copilot.
- Last updated: `2026-09-30`.

## Problem Statement

Add thirteen historically bounded civilizations using suitable existing
animated leaderheads, with distinct unique units, buildings and leader traits.
Retain accepted visual/gameplay improvements and the finalized Barclay art.
Do not equate offline portraits or XML validation with in-game readiness.

## Why This Matters

The unused asset catalog can support new content without automatically
remaking recognizable leaders. Native mechanics need consistent AI, help,
ownership, modifier and save behavior, not only descriptive localization.
An isolated worktree protects concurrent work and the accepted game baseline.

## Scope

- Branch: `agent-baseline-leader-chatter-sol-leader-update-visual-overhaul-new-leaders`.
- Worktree: `C:\DowagerMod-new-leaders`.
- Visual/gameplay parent: `267e47ca0`.
- Combined baseline: `cb87ce542`, the local cherry-pick of Barclay `e88837d6e`.
- Thirteen selected packages, one UU/UB/trait each; two selective worker
  improvements. Starting from 59 playable entries, target 72 selectable civs.
- Local validated checkpoint commits permitted; no push, merge or installation.
- Preserve existing IDs, order, rules, art and flag mappings.
- Native XML first; new native support only for the active contracts below.
- Existing leaderheads are provisional, with bounded technical dependency
  repairs. Preserve primary appearance, including Ho's blue shirt.
- David explicitly remains selected despite a REMAKE audit recommendation:
  use the existing asset provisionally, repair dependencies, do not redesign.
- Suitable existing UU/UB/improvement visuals may be provisional; document
  gaps and require final visual acceptance.

## Non-Goals

- No existing-roster rebalance, new religions/resources or player-slot increase.
- No automatic leaderhead remakes or anachronistic art substitutions.
- No contiguous-farm rendering, navigable irrigation canals or terrain overhaul.
- No source edits in the original/visual worktrees or the other agent's outputs.
- No installer, live-game changes, push, merge or external imports without
  separate authorization.
- Sunni Ali, Mursili II, Suppiluliuma I, Nzinga a Nkuwu, Seleucus I and
  Bayinnaung are design-only backlog, not authorized additions.

## Selected Content

All numbers in the approved design are initial balance targets. Retain live
parent mechanics except explicit deltas; do not replace basic early buildings
with versions that cannot be constructed until a modern technology.

| Leader / civilization | UU parent / concept | UB parent / concept | Signature |
|---|---|---|---|
| Sennacherib / Nineveh Assyria | Catapult / Siege Tower | Aqueduct / Royal Waterworks | With Waterworks, worked riverside Farms/Canals provide city Production, +1 each capped at +3 |
| Hiram / Tyre Phoenicia | Galley / Merchant Galley | Market / Counting House | Coastal city Gold from distinct foreign trade-route teams, +1 each capped at +3 |
| Piye / Napatan Kush | Archer / Kushite Archer | Monument / Cult Chapel | Ordinary Priests +1 Food; domestic Great General rate +25% |
| Matthias / Corvinian Hungary | Musketman / Black Army Arquebusier | University / Corvinian College | Melee/Gunpowder upgrade-discount promotion 25%; ordinary Artists +1 Research |
| Ramkhamhaeng / Sukhothai | War Elephant / Sukhothai Elephant | Library / Ho Trai | After Writing, worked riverside Farms provide city Culture, +1 each capped at +3 |
| Mongkut / Rama IV Siam | Rifleman / Royal Rifle | Observatory / Royal Observatory | +20 research-modifier points for tech known to an eligible foreign Open Borders partner |
| Ho / Democratic Republic Vietnam | Infantry / Viet Minh Infantry | Intelligence Agency / Resistance Headquarters | Worked Forest/Jungle plots provide city Production, +1 each capped at +3; domestic GG +50% |
| Askia / Askia Songhai | Knight / Escort Cavalry | University / Scholarly College | Worked riverside Cottage/Hamlet/Village/Town plots provide city Gold, +1 each capped at +4 |
| Dusan / Serbian Empire | Knight / Vlastela Cavalry | Courthouse / Zakonik Court | Mines +1 Commerce yield; ordinary Priests +1 Espionage |
| Pedro II / Second Empire Brazil | Rifleman / Voluntarios da Patria | University / Imperial Lyceum | Ordinary Scientists +1 Culture, Artists +1 Research; GP rate +25% |
| Bolivar / Gran Colombia | Cavalry / Llanero | Courthouse / Republican Cabildo | Newly generated military-conquest occupation becomes ceil(native / 2); GG +50% |
| Zenobia / Palmyra | Horse Archer / Clibanarius | Market / Caravan Court | Worked improved Desert with Road/Railroad provides city Gold, +2 each capped at +6 |
| David / Davidic Israel | Swordsman / Gibbor Retainer | Walls / Royal Citadel | City +3 Culture with owned non-cargo combat land unit level 3+; domestic GG +25% |

Plot contributions require owned, assigned, citizen-worked plots; no overlap
duplication or unworked payment. Apply city commerce before modifiers and
show counts/caps in UI. Specialists require assignment, not merely slots.

Royal Canals: Mathematics; featureless flat Grassland/Plains/Desert, riverside
or already irrigated, resource-free owned assigned BFC; build cap two per
assigned city; +1 Food/+1 Commerce; normal irrigation-tech rules.

Caravan Stations: Currency; featureless flat Desert, existing Road/Railroad,
resource-free owned assigned BFC; build cap one per assigned city;
+1 Food/+3 Commerce. No unworked payout or free city/trade route.

Both require civilization-gated Worker builds and distinct pillaged identity
for cap/repair accounting. Capture never silently deletes an existing copy.
Recheck caps at completion; no great-person landmark replacement.

## Trusted Sources Of Truth

- BtS `Assets\XML` and `Assets\Python`; authoritative DLL source is
  `third_party\beyond-the-sword-sdk\CvGameCoreDLL`.
- `tools\test_gate.ps1`, `test_xml.ps1`, `build_civ4_dll.ps1`.
- `tools\validate_roster_safety.py`, `tools\flags` and targeted tests.
- The approved session design supplies full per-package deltas, historical
  sources and UI/AI contracts; transcribe these into reviewed machine-readable
  expansion fixtures before content generation, not inferred vanilla values.
- Original workspace audit: `tmp\leaderhead-preview-audit\AUDIT-REPORT.md`,
  `verification.json` and selected per-leader inventories/view/failure records.
  The temporary audit is evidence, not runtime content or a committed asset.

## Existing Docs / Plans Trust Review

- `WORKFLOW.md`, `AGENTS.md`, testing/flag runbooks: trusted workflow.
- `LEADER_OVERHAUL_PLAN_OF_RECORD.md`: methodology, not current-runtime proof.
- Earlier roster plans/test baseline `12e22297f`: historical contracts requiring
  comparison with accepted citystyle changes, not grounds to revert those changes.
- Visual audit: usable retention guidance, not dependency or animation approval.

## Baseline Observations and Blocker

Before expansion XML/DLL-source edits, at `cb87ce542`:

- Full `.\tools\test_gate.ps1 -All` passed: Py2.4 compatibility, full XML,
  roster safety/localization/art checks, citystyle coverage and DLL compilation.
- Six relevant unittest modules ran 78 tests and reported 11 failures.
  These are failures, not skipped or passing tests.
- Seven failures concern city `ArtStyleType` changes absent from the old
  exact-roster test's allowed deltas. Its normalization at
  `tools\tests\test_additive_roster_exact_contract.py:170-185` covers player
  colors/flags, but not the accepted styles.
- Affected civilizations: Founding America, Babylon, Elizabethan England,
  Korea, Venice, Yuan and USSR. Current styles are respectively Anglo-America,
  Crescent, Europe, Asia, Europe, Mongolia and Russia.
- Four failures in `tools\tests\test_great_person_landmarks.py:595-692`:
  Grand Colosseum and Jokamachi each match two root routes instead of one;
  a selector has 205 characters versus the test's 182 maximum; LNode ordering
  follows an earlier production instead of all nodes preceding productions.
- BtS `XML\Buildings\CIV4PlotLSystem.xml:10778-10780` has the broad generic
  root route. Dedicated routes appear at `11762-11795`; the broad route can
  also select these improvements. This is not proof that the engine accepts
  every selector length or that the tests are all stale.
- `git diff --exit-code 267e47ca0 HEAD` for both failing test files,
  CivilizationInfos and PlotLSystem returned 0: these inputs are unchanged
  from the pre-expansion visual branch.
- The full build replaced only the expansion worktree's mirrored DLL; its
  rebuilt binary is an uncommitted generated change, not a gameplay-source edit.
- No new civilizations, units, buildings, traits or asset repairs are integrated.

Logs are in the active session `files\expansion-baseline-gate.log` and
`files\expansion-baseline-tests.log`; the reproducible commands are:

```powershell
.\tools\test_gate.ps1 -All
python -m unittest tools.tests.test_validate_roster_safety tools.tests.test_additive_roster_exact_contract tools.tests.test_flag_pipeline tools.tests.test_flag_contract_fullcolor tools.tests.test_unique_civilization_flags tools.tests.test_great_person_landmarks
```

The owner's subsequent instruction to continue autonomously was applied to
a bounded cleanup: exact old/new citystyle assertions for the seven affected
civs, and a plot-route normalization shared with the visual importer.
The generic root selector now uses bounded positive groups excluding the
preserved custom routes; existing art nodes and specialized productions are
unchanged. Preserved nodes precede all productions. No size limit was raised
and no landmark assertion was removed.

After cleanup, the six original modules plus neutral-wonder and importer
regressions passed: 106 tests. The changed-file repository gate passed.
Its XML validator explicitly skips PlotLSystem's unavailable
`CIV4LSystemSchema.xml`; XML parsing, routing, preservation and ordering are
covered by targeted tests, not claimed as full engine/schema certification.
In-game visual acceptance remains pending and no live install was changed.

## Affected Files / Directories

- Civilization/leader/trait, unit/promotion/build, building, improvement,
  art, color, localization XML under BtS only.
- Native info/schema/cache, city/player/plot/unit logic, AI and game text.
- `tools\flags`, additive roster fixtures/tests, chatter CLI convenience roster.
- Avoid base/Warlords, vendored HUD, installer, live installation, and `tmp`.

## Assumptions That Need Human Confirmation

- Operating scope, provisional art, David reuse, Ho fallback and local commits:
  confirmed. No new up-front permission needed for those bounded actions.
- Baseline failures: bounded cleanup completed after the instruction to proceed.
- Pedro II identity and final art/graphics/gameplay acceptance remain pending.

## Proposed Implementation Steps

1. Resolve the baseline-test stop boundary explicitly.
2. Freeze append-only baseline and exact thirteen-package deltas/manifests.
3. Native pilot: Piye and Dusan; then Matthias and Pedro.
4. Shared capped worked-plot effects: Ramkhamhaeng, Ho, Askia, Sennacherib,
   Zenobia; prototype the two improvements and their Worker AI.
5. Hiram route diversity, Mongkut research access, Bolivar conquest occupation,
   David veteran-garrison Culture, each with neutral-default native support.
6. Integrate retained/repaired art and provisional suitable supporting art.
7. Run cumulative automation, commit validated local checkpoints and hand off
   the explicit manual acceptance matrix. No install, push or merge.

No E4 vassal tribute, E6 founding culture or E8 foreign-founder mobilization;
those belong solely to the unselected backlog.

## Validation Plan

- Required XML/roster/art gates and DLL compilation.
- Exact parent-delta/type-order/old-value assertions, numeric caps/rounding,
  plot assignment/ownership/pillage, specialist and unit eligibility.
- Native UI/AI parity, cache invalidation, deterministic multiplayer behavior,
  save/reload and no undocumented migration.
- Flags: deterministic DXT3, eight mips, zero alpha, retain original mappings.
- Manual: full diplomacy composition, greeting, attitudes, affirmative/negative
  actions, transitions, clipping, reopen and supported graphics settings.
- New-campaign gameplay/AI and multiplayer acceptance; old saves investigated,
  not promised. No manual install/run authorized or performed by this task.

## Documentation Updates Required

- This plan and `docs\index.md`.
- Final expansion manifest, provenance and manual test matrix.
- Update only directly affected schema/behavior/flag/chatter runbooks.

## Risks / Rollback

- Missing dependency versus offline-renderer limitation must be distinguished.
- No art redesign or unsupported shader fallback without fresh approval.
- New info tables may invalidate old saves despite append-only ordering.
- Isolated local commits provide review/rollback boundaries; never reset or
  modify either original worktree to recover this expansion.

## Open Questions

- Final art and in-game acceptance remain unresolved, as intended.

## Completion / Outcome

Combined branch exists; the baseline gate and reconciled targeted tests pass.
Piye and Dusan are integrated using native XML trait channels, parent-preserving
UU/UB clones, distinct colors/flags/buttons, existing animated leaderheads,
first-contact text, AI profiles and inherited era-complete citystyles.
Matthias and Pedro II are also integrated, bringing the selectable roster to
63; nine selected packages remain. Matthias uses the existing native
upgrade-discount promotion channel, limited to Melee/Gunpowder, not generally
selectable; Python override precedence is unchanged. Pedro uses native
specialist commerce and Great Person modifiers.
Stock UU/UB models, retained portraits and generated heraldry are provisional.

Matthias's missing Darius specular map was restored from the stock repository
donor: neighboring normal/environment/mask textures match byte-for-byte.
His absent portrait button is replaced explicitly by a provisional Corvinian
raven emblem; the animated leaderhead is unchanged. Pedro's existing 64px
portrait is retained. The roster validator now distinguishes five audited,
hash-pinned internal NIF names from file dependencies without bypassing the
rest of the model; TGA texture references are checked as well. No model names,
meshes, costumes or background transforms were rewritten.

New SVG masters are LF-normalized to match Git attributes; their source
digests therefore survive a fresh checkout. The original 59 flag records and
production digests remain unchanged.

The package compiler `tools\add_expansion_packages.py --apply` appends only
reviewed manifest packages. Its default mode checks deterministic output;
it rejects conflicting existing package records and stages all output before
publication with rollback on write failure. It does not rebuild old XML tables.
`tools\manifests\new_leaders_expansion.json` holds exact native deltas;
`new_leaders_art.json` records direct leader-art digests and limitations.
The existing 59 flag records and all pre-expansion XML records remain intact.

Validation: 252 tests passed across the expansion, roster, flag, landmark,
neutral-wonder and plot-merge modules, plus the repository gate and an
idempotent generator check. The earlier unittest command did not collect
function-based flag tests; running those with pytest exposed one additional
pre-expansion whole-file citystyle hash expectation. Its original byte hash
remains pinned against `c9bfb5892`, followed by exact structural preservation
with only accepted citystyles and declared appended records allowed.
There are no remaining failures in this combined targeted run.

The second native group passed the repository gate and 48 focused
expansion/validator/flag/exact-roster tests. Full cumulative reruns remain part
of the subsequent engine/content integration.

Native compilation passed at the combined baseline; the pilot adds no DLL
code. Manual gameplay, diplomacy/graphics, AI games, old saves and multiplayer
were NOT run. The complete expansion is NOT ready to merge/deploy.
No push, merge, installer or live-game action occurred.
