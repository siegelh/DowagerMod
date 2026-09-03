# Staged Diplomatic Incident Spy Mission

- Status: `implemented_pending_gameplay_validation`
- Owner / agent: GitHub Copilot CLI
- Last updated: `2026-09-02`

## Problem Statement

- Task: add an active spy mission that lets the acting player manufacture a
  diplomatic incident between the civilization whose territory contains the
  spy and a separately selected civilization.
- Intended interaction:
  1. A spy stands in another civilization's territory.
  2. The player selects the staged-incident espionage mission.
  3. A second popup lists eligible civilizations to frame.
  4. If the mission succeeds, the territory owner loses attitude toward the
     selected framed civilization.
- Direction of the effect: if player S owns the spy, player T owns the
  territory, and player F is selected in the popup, only T's opinion of F is
  reduced. S does not automatically dislike either party, and F does not
  automatically dislike T.
- Current observed behavior: BtS supports two-phase espionage missions, but the
  second-phase popup only knows how to select buildings, units, projects,
  technologies, civics, and religions. No mission currently selects another
  player or changes third-party diplomatic attitude.
- Why this is a real repo/code problem: the selection must travel through the
  synchronized mission command, remain deterministic in multiplayer, validate
  the selected player again at execution time, charge espionage points only
  after a valid effect, and provide AI behavior.

## Why This Matters

- Adds an espionage action that changes the diplomatic map rather than directly
  damaging the civilization being infiltrated.
- Creates indirect strategic play: undermine alliances, increase tension
  between rivals, or worsen an enemy's relationship with a potential partner.
- Reuses the normal spy interception and escape systems, so a failed operation
  can still expose the actual spy owner.

## Scope

- Add one active espionage mission provisionally named
  `ESPIONAGEMISSION_STAGE_DIPLOMATIC_INCIDENT`.
- Permit the mission from a spy's current tile in foreign-owned territory; a
  city is not required.
- Add a civilization/player selection branch to the existing second-phase
  espionage popup.
- Carry the selected framed player as the existing synchronized
  `MISSION_ESPIONAGE` extra-data value.
- Apply a one-way diplomatic penalty from the territory owner toward the
  framed player.
- Add human-facing mission, popup, success, and target-notification text.
- Add deterministic AI target selection and mission valuation.
- Add XML/DLL contracts and focused regression tests.

## Non-Goals

- Do not force war, cancel treaties, alter war success, or directly change
  peace/vassal state.
- Do not make the framed civilization reciprocally dislike the territory
  owner.
- Do not change spy interception, escape, stationary-spy discounts, or generic
  espionage cost modifiers.
- Do not reveal the actual spy owner when the mission succeeds.
- Do not add a custom Python screen when the native synchronized popup flow is
  sufficient.
- Keep the mission implementation in a separate commit from the flag work.
- Do not push the mission commit without separate explicit approval.

## Trusted Sources Of Truth

- Mission entry and second-phase dispatch:
  - `third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvUnit.cpp:6138-6191`
  - `third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvDLLButtonPopup.cpp:260-278`
  - `third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvDLLButtonPopup.cpp:1805-2021`
- Mission validation, cost, execution, notification, and EP payment:
  - `third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvPlayer.cpp:13366-13829`
  - `third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvPlayer.cpp:13942-14388`
- Diplomatic attitude storage:
  - `third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvPlayerAI.cpp:10470-10488`
  - the existing `m_aiAttitudeExtra` matrix is already saved and loaded.
- Espionage mission data:
  - `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/GameInfo/CIV4EspionageMissionInfo.xml`
  - `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/GameInfo/CIV4GameInfoSchema.xml:1189-1234`
- AI mission selection and valuation:
  - `third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvPlayerAI.cpp:9726-10080`

## Existing Docs / Plans Trust Review

- `WORKFLOW.md`: `trusted for this task`; requires a checked-in plan, DLL/XML
  validation, documentation updates, and manual gameplay testing.
- `ARCHITECTURE.md`: `useful context only`; confirms the authoritative DLL and
  BtS asset roots, but live espionage code remains primary.
- `docs/MANUAL_SMOKE_TESTS.md`: `trusted for this task`; minimum installed-game
  validation guidance.
- Repository discovery context §2 and §10: `trusted for runtime roots and
  validation guardrails`.

## Affected Files / Directories

- Primary DLL implementation:
  - `third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvInfos.h`
  - `third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvInfos.cpp`
  - `third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvDLLButtonPopup.cpp`
  - `third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvPlayer.cpp`
  - `third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvPlayerAI.cpp`
- Primary XML:
  - `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/GameInfo/CIV4GameInfoSchema.xml`
  - `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/GameInfo/CIV4EspionageMissionInfo.xml`
  - a BtS text XML file under `Beyond the Sword/Assets/XML/Text/`
- Tests:
  - a focused new contract under `tools/tests/`
- Documentation:
  - this plan
  - `docs/index.md`
  - `ARCHITECTURE.md` only if the final implementation introduces a reusable
    mission-data extension worth documenting.
- Avoid:
  - base `Assets`, Warlords, bundled scenario/mod DLL copies, and
    `petromod_v1`.

## Proposed Data Contract

Extend `CvEspionageMissionInfo` with explicit mission semantics rather than
hard-coding behavior to one XML type string:

- `bStagesDiplomaticIncident`
- `iDiplomaticAttitudeChange`

The staged-incident XML record would use:

- active mission;
- two phases;
- no city requirement;
- no plot-selection requirement beyond the spy's current valid foreign tile;
- an appropriate technology prerequisite if balance review requires one;
- a positive base EP cost;
- a negative `iDiplomaticAttitudeChange`.

The generic fallback cost path already supports an active mission with a base
cost and no existing special cost-factor field.

## Framed-Civilization Eligibility

The second popup and execution-time validation should use one shared helper.
An eligible framed player must:

- be alive and a major playable civilization;
- not be the spy owner;
- not be the territory owner;
- not share a team with the spy owner or territory owner;
- have met the territory owner's team, so an attitude relationship exists;
- be known to the acting human, so the popup does not reveal an unmet
  civilization;
- remain eligible when the synchronized mission executes.

- A territory owner's master or vassal is excluded from the framed-player
  list.

If no eligible framed civilization exists, the mission must not appear as
available.

The territory owner must be AI-controlled. Civ4 has no enforceable attitude
model for a human player's personal diplomatic opinion, so allowing this
mission against a human territory owner would consume EP without a meaningful
gameplay effect. Human civilizations remain valid as the framed party.

## Diplomatic Effect Model

### Recommended first implementation

- Use `AI_changeAttitudeExtra(eFramedPlayer, iDiplomaticAttitudeChange)` on the
  territory owner.
- Configured value: `-2` attitude per successful mission.
- This gives a fixed, leader-independent penalty and automatically persists in
  saves through the existing attitude-extra matrix.
- Repeated missions stack without a cap.
- The standard diplomacy breakdown will classify it under the generic
  positive/negative extra-attitude line rather than a uniquely named staged
  incident.

### Alternative: diplomatic memory

- Apply `MEMORY_SPY_CAUGHT` or add a new diplomatic memory against the framed
  player.
- This gives a named and potentially decaying reason in the diplomacy
  breakdown, but the magnitude and decay become leader-specific.
- Adding a brand-new memory would require coordinated enum/info, leader XML,
  text, save, and AI work across the roster and is not recommended for the
  first implementation.

The fixed attitude-extra model is the smallest reliable implementation matching
the request. A named/decaying incident can be a later enhancement if the
generic breakdown text is not satisfactory in game.

## Human Interaction And Notifications

1. The normal espionage popup shows `Stage Diplomatic Incident` with its EP
   cost.
2. Selecting it opens the native second-phase popup with one button per
   eligible framed civilization, showing civilization and leader identity.
3. Cancel returns without consuming the spy's action or espionage points.
4. After a successful mission:
   - the acting player receives a success message naming T and F;
   - the territory owner receives a message indicating that evidence implicates
     F, without identifying S;
   - F receives no automatic notification.
5. If the spy is intercepted before execution, the existing interception path
   applies and the staged incident does not occur.
6. Successful execution continues through the existing spy escape/return path.

## AI Behavior

- Extend `AI_bestPlotEspionage` so AI spies consider the mission on any valid
  foreign-owned plot, not only as an unrecognized dataless mission.
- Evaluate candidate framed players deterministically.
- Prefer framing a civilization the territory owner currently likes and that
  competes strategically with the acting AI.
- Avoid framing teammates and invalid/unmet players.
- Set `iData` to the chosen framed player so AI and human execution use the same
  synchronized mission path.
- Value should account for:
  - configured attitude loss;
  - current T-to-F attitude, with more value when crossing an attitude
    threshold is plausible;
  - diplomatic relevance of T and F;
  - mission EP cost;
  - avoiding repeated spending when the relationship is already at the lowest
    useful attitude tier.
- Tie-breaking must use stable player iteration order, with no asynchronous
  randomness.

## Proposed Implementation Steps

1. Add staged-incident boolean and attitude-change fields to the espionage
   mission schema and `CvEspionageMissionInfo`.
2. Add a shared DLL helper that validates framed-player eligibility.
3. Add the XML mission and localized text with provisional cost and effect
   values.
4. Extend the second-phase espionage popup to list eligible civilizations for
   this mission.
5. Revalidate `iExtraData` in mission cost and execution paths.
6. Apply the one-way attitude change only after all mission checks pass, then
   let the existing path charge EP and resolve spy escape.
7. Add actor and territory-owner messages that preserve the false attribution.
8. Add deterministic AI candidate selection and valuation.
9. Add focused contracts for XML fields, popup dispatch, eligibility,
   directionality, EP charging, save-backed attitude state, and AI wiring.
10. Build the DLL, run the repository gates, install, and perform single-player
    plus two-client multiplayer smoke tests.

## Validation Plan

- Required automated checks:
  - mission is active, two-phase, and non-city-targeted;
  - mission is unavailable without at least one eligible framed civilization;
  - human territory owners are excluded while human framed civilizations
    remain eligible;
  - popup includes each eligible player exactly once and excludes invalid
    players;
  - execution rejects forged/stale `iExtraData`;
  - only T's attitude toward F changes;
  - S-to-T, S-to-F, and F-to-T attitude values remain unchanged;
  - mission cost is paid exactly once only on success;
  - mission output is deterministic and AI tie-breaking is stable;
  - attitude change survives save serialization through existing state.
- Required repo scripts:
  - `.\tools\test_gate.ps1 -CheckDll`
  - `.\tools\test_full.ps1`
  - `git diff --check`
- Required manual smoke test:
  - install the modified payload;
  - verify mission visibility on city and non-city foreign tiles;
  - confirm the second popup lists only intended civilizations;
  - cancel and confirm no EP/action loss;
  - complete the mission and inspect the territory owner's diplomacy breakdown
    toward the framed civilization;
  - verify the acting civilization remains concealed on success;
  - test interception and confirm no false penalty is applied;
  - save/reload and confirm the penalty persists;
  - run the same scenario in a fresh two-client multiplayer game and confirm
    identical diplomacy state with no OOS.

## Risks / Rollback

- `AI_changeAttitudeExtra` is persistent and shown under generic attitude text;
  repeated missions could create a large permanent penalty.
- A per-pair floor or repeat-use restriction may be needed after balance
  testing.
- Human popup selection must not mutate state locally; all mutation must occur
  after the synchronized mission command.
- Invalid player IDs must fail before interception, EP charging, or attitude
  mutation.
- Team and vassal relationships can create edge cases that need focused tests.
- Rollback is a single coordinated DLL/XML/text/test change; do not partially
  remove schema fields while leaving mission XML behind.

## Locked Gameplay Decisions

- Permanent fixed `-2` attitude per successful mission.
- Unlimited stacking.
- Base cost `400` EP before normal espionage modifiers.
- No technology prerequisite.
- Territory-owner master/vassal relationships are excluded.
- The first version uses Civ4's generic extra-attitude diplomacy breakdown.

## Completion Checklist

- [x] Live mission, popup, attitude, save, and AI paths were mapped.
- [x] Feasibility and synchronization approach were confirmed.
- [x] Scope, directionality, eligibility, and risks were recorded.
- [x] Balance and permanence decisions were confirmed.
- [x] The flag commit `c9bfb5892` was pushed and remotely verified before
  mission implementation began.
- [x] DLL/XML/text implementation completed.
- [x] Focused tests and repository gates passed.
- [x] Installed single-player smoke test passed.
- [ ] Installed two-client multiplayer/OOS smoke test passed.
- [x] Implementation committed locally as a separate contained commit.
- [x] Mission commit pushed only after explicit approval.

## Final Outcome Summary

- Implemented the mission through the existing native two-phase espionage
  popup and synchronized `MISSION_ESPIONAGE` extra-data channel.
- Added optional espionage-info fields, the appended mission XML record,
  localized text, execution-time validation, actor/target notifications,
  deterministic AI selection, and a rebuilt runtime DLL.
- The effect is a configurable, fixed, one-way `-2` attitude penalty from the
  AI-controlled territory owner toward the selected framed civilization.
- Automated evidence:
  - 9 focused staged-incident tests passed.
  - changed-file XML validation passed.
  - `tools/test_gate.ps1 -CheckDll` passed.
  - `tools/test_full.ps1` passed.
  - two follow-up reviews found no remaining significant issues after fixes.
  - the complete `tools/tests` suite ran 336 tests; 335 passed and one
    pre-existing additive-trait manifest test failed against unchanged
    branch content outside this mission's diff.
- Installed single-player, save/reload, and fresh two-client multiplayer/OOS
  smoke tests were requested. The user subsequently confirmed the installed
  mission works; fresh two-client multiplayer/OOS evidence remains pending.
