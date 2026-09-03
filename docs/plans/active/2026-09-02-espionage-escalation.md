# Espionage Escalation: Backchannels and Casus Belli

- Status: `implemented; automated validation complete; installed and multiplayer acceptance pending`
- Owner / agent: GitHub Copilot CLI
- Last updated: `2026-09-02`

## Problem Statement

The existing Stage Diplomatic Incident mission can make an AI territory owner
dislike a framed civilization, but attitude alone does not force Civ4's AI to
begin a war plan. The desired expansion adds:

1. **Establish Backchannels**, a mission that makes the infiltrated AI like the
   acting player slightly more.
2. **Fabricate Casus Belli**, a separate high-cost escalation mission that can
   convert an already-hostile relationship into a native limited-war
   preparation.

The two missions should support a deliberate sequence: damage T's relationship
with F, improve T's relationship with S, then either negotiate a normal
declare-war trade or attempt a covert casus belli.

## Actors and Directionality

- **S**: player who owns the spy.
- **T**: AI-controlled owner of the territory containing the spy.
- **F**: civilization selected as the alleged aggressor.

Effects:

- Establish Backchannels: T gains a small, decaying positive memory toward S.
- Fabricate Casus Belli success: T begins
  `WARPLAN_PREPARING_LIMITED` against F.
- Neither mission changes F's attitude or directly declares war.

## Trusted Runtime Paths

- Espionage popup and synchronized extra data:
  `CvDLLButtonPopup.cpp:1831-1904`.
- Mission eligibility, cost, execution, and EP charging:
  `CvPlayer.cpp:13366-13534`, `CvPlayer.cpp:14009-14053`.
- Pre-interception validation:
  `CvUnit.cpp:6168-6172`.
- AI espionage selection and valuation:
  `CvPlayerAI.cpp:9740-9750`, `CvPlayerAI.cpp:9946-9958`.
- Native war-plan state and preparation:
  `CvTeamAI.cpp:3163-3280`, `CvTeamAI.h:139-143`.
- Native rejected-demand precedent:
  `CvPlayer.cpp:3785-3794`,
  `CvPlayerAI.cpp:4751-4785`.
- Attitude thresholds:
  `CvPlayerAI.cpp:4817-4838`.
- Goodwill memory calculation and decay:
  `CvPlayerAI.cpp:5243-5247`, `CvPlayerAI.cpp:10695-10703`.

## Mission 1: Establish Backchannels

### Player-facing contract

- Name: `Establish Backchannels`.
- Active, one-phase, non-city-targeted mission.
- Base cost: **500 EP** before normal Civ4 modifiers.
- No technology prerequisite.
- Operates from any valid tile owned by an AI civilization.
- T must be alive, major, AI-controlled, known to S, and at peace with S.

### Effect

On successful execution:

```cpp
GET_PLAYER(T).AI_changeMemoryCount(S, MEMORY_GIVE_HELP, 1);
```

- All 59 playable leader personalities currently assign
  `MEMORY_GIVE_HELP` exactly `+100%`, producing `+1` attitude per count.
- The existing memory is already serialized.
- It decays naturally:
  - 57 leaders use a 1-in-200 per-turn decay roll.
  - Casimir and Enrico Dandolo use 1-in-60.
- Repeated missions stack without a cap. This is intentional because each use
  provides only `+1`, the memory decays naturally, and every additional use
  requires another spy mission and full EP payment.
- Actual diplomatic help and fabricated help share the same memory count. This
  is acceptable for the first version and avoids adding save-format state.
- The diplomacy breakdown uses the existing help wording rather than a unique
  backchannels reason.

### Notifications

- Actor success:
  `Our agents have established discreet backchannels within [T].`
- Interception follows the existing spy-caught path and can offset the intended
  goodwill.
- T is AI-only, so no human-target notification is required.

### AI use

- AI spies may use the mission when it crosses an attitude tier with T.
- Prefer Cautious or Annoyed targets where one point reaches a more useful
  diplomatic tier.
- Value the expected diplomatic improvement against the effective EP cost.
- Do not use during war or when no visible tier changes.

## Mission 2: Fabricate Casus Belli

### Player-facing contract

- Name: `Fabricate Casus Belli`.
- Active, two-phase, non-city-targeted mission.
- Base cost: **900 EP** before normal Civ4 modifiers.
- No technology prerequisite in the first version.
- The second popup selects F and shows the current synchronized political
  success chance.
- Canceling the popup consumes no EP, action, or movement.
- A political failure consumes EP and the spy's action; otherwise the player
  could reroll without cost.

### Hard eligibility checks

The mission is hidden or F is excluded when any condition is false:

- T and F are alive major civilizations.
- T and its team are AI-controlled, and T's team is not a vassal.
- S, T, and F are distinct and on different teams.
- S and T have both met F.
- T is Annoyed or Furious with F: raw attitude `<= -3`.
- T is at peace and has no existing war plan.
- T can legally declare war on F.
- No forced peace, same-team, master/vassal, or defensive-pact relationship
  blocks war.
- T considers F an accessible land target through the existing team-AI
  land-target helper.
- T's power is at least **70%** of F's defensive power.

Every condition is recalculated during cost lookup, popup construction,
pre-interception validation, and synchronized execution. A stale selection is
rejected before EP loss or spy risk.

### Success chance

Use T's raw attitude toward F:

```text
chance = 10
       + 4 * max(0, -3 - rawAttitude)
       + 15 if rawAttitude <= -10
       + powerAdjustment
chance = clamp(chance, 10, 70)
```

Power adjustment:

| T power relative to F defensive power | Adjustment |
|---|---:|
| Below 70% | Ineligible |
| 70-89% | -20 |
| 90-109% | 0 |
| 110-129% | +10 |
| 130% or greater | +20 |

Examples before power adjustment:

| Raw attitude | Display | Base chance |
|---:|---|---:|
| -3 | Annoyed | 10% |
| -6 | Annoyed | 22% |
| -9 | Annoyed | 34% |
| -10 | Furious | 53% |
| -15 | Furious | 70% cap |

The chance calculation must live in one shared DLL helper used by popup text,
AI valuation, and execution.

### Synchronized outcome

After normal spy interception is survived, roll only with synchronized game
RNG:

```cpp
GC.getGameINLINE().getSorenRandNum(100, "Fabricate Casus Belli")
```

On political success:

```cpp
GET_TEAM(GET_PLAYER(T).getTeam()).AI_setWarPlan(
    GET_PLAYER(F).getTeam(),
    WARPLAN_PREPARING_LIMITED
);
```

This does not declare war immediately. Native AI preparation normally converts
the plan into limited war after roughly five game-speed-adjusted turns.

On political failure:

- Create no war plan.
- Charge the mission cost exactly once.
- Consume the spy action through the normal successful-operation path.
- Do not apply additional attitude damage; Stage Diplomatic Incident remains
  the relationship-damage mission.

### Result visibility

The actor must receive an unambiguous result:

- Success:
  `Our agents report that [T] accepted the fabricated evidence and has begun
  military preparations against [F].`
- Political failure:
  `The fabricated evidence caused outrage in [T], but its leadership declined
  to mobilize against [F].`
- Interception:
  use the existing interception/exposure result; no war plan is created.

The message reveals only whether preparation began, not military strength,
exact preparation duration, or unrelated hidden plans.

External state can still cancel or invalidate preparation later. Success means
the war plan was genuinely created, not an unconditional guarantee that war
must occur under every subsequent diplomatic event.

### AI use

- AI spies evaluate every eligible F deterministically in ascending player
  order.
- Expected value is:

```text
political chance
* strategic value of T fighting F
- effective EP cost
```

- Prefer F when:
  - F is a strategic rival or stronger competitor of S;
  - T and F share borders;
  - T has enough power to sustain the war;
  - the chance is high because T is already Furious.
- Avoid triggering wars that primarily benefit F or expose S to an immediate
  strategic threat.
- Use strict `>` comparisons for stable tie-breaking and no asynchronous
  randomness.

## XML and DLL Data Contract

Append optional mission-info fields:

- `bEstablishesBackchannels`
- `bFabricatesCasusBelli`
- `iCasusBelliMinAttitude`
- `iCasusBelliMinPowerRatio`
- `iCasusBelliBaseChance`
- `iCasusBelliAttitudeChancePerPoint`
- `iCasusBelliFuriousBonus`
- `iCasusBelliMaxChance`

Old mission records default to false/zero. New mission records are appended
after the existing staged incident so previous espionage mission indices do
not shift.

Expose read-only getters to Python consistently with the staged-incident
fields.

## Shared Implementation Structure

Add explicit helpers rather than duplicating popup/execution/AI rules:

- `canEstablishBackchannels(T)`
- `canFabricateCasusBelli(mission, T, F)`
- `getFabricateCasusBelliChance(mission, T, F)`
- a shared physical spy/plot/territory validation helper for all custom
  diplomatic espionage missions.

The existing `canStageDiplomaticIncident` candidate rules should be reused or
factored into common third-party eligibility where applicable.

All state mutation remains in synchronized DLL execution. Popup code remains
presentation-only.

## Primary Files

- `third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvInfos.{h,cpp}`
- `third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvPlayer.{h,cpp}`
- `third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvPlayerAI.cpp`
- `third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvTeamAI.{h,cpp}`
- `third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvUnit.cpp`
- `third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvDLLButtonPopup.cpp`
- `third_party/beyond-the-sword-sdk/CvGameCoreDLL/CyInfoInterface3.cpp`
- BtS game-info schema and espionage mission XML
- a new or extended BtS text XML file
- focused tests under `tools/tests/`
- `ARCHITECTURE.md`
- `docs/MANUAL_SMOKE_TESTS.md`

Do not edit base Assets, Warlords, scenario DLL copies, or `petromod_v1`.

## Validation Plan

Automated contracts must cover:

- append-only mission ordering;
- schema/info/Python bindings;
- Backchannels target eligibility, repeated `MEMORY_GIVE_HELP +1` stacking,
  natural decay, existing save persistence, and AI tier-crossing valuation;
- Casus Belli hard exclusions for human/vassal/war-plan/forced-peace/team/
  defensive-pact/unmet/unreachable/under-70%-power cases;
- exact chance values at attitude and power boundaries;
- popup-displayed chance equals execution chance;
- stale `iExtraData` rejection before interception;
- synchronized RNG only;
- political failure charges EP exactly once and creates no plan;
- success creates only T-to-F `WARPLAN_PREPARING_LIMITED`;
- actor receives distinct success/failure messages;
- deterministic AI candidate ordering and valuation;
- unrelated espionage missions and existing Destroy Project values remain
  unchanged.

Run:

- focused pytest contracts;
- `.\tools\test_gate.ps1 -CheckDll`;
- `.\tools\test_full.ps1`;
- `git diff --check`.

Manual installed smoke testing:

1. Establish Backchannels increases T's displayed attitude toward S by one.
2. Repeated successful uses stack by exactly one each without a cap.
3. Save/reload preserves the memory and natural decay remains functional.
4. Casus Belli popup includes only eligible F and shows the correct chance.
5. Cancel consumes nothing.
6. Hard-invalid states do not expose the mission.
7. Political failure consumes EP/action and reports failure without a war plan.
8. Success reports mobilization and produces war after native preparation.
9. Interception creates no war plan.
10. Fresh two-client multiplayer reproduces identical odds, RNG result,
    attitude/memory state, war plan, and eventual war with no OOS.

## Risks and Tradeoffs

- Starting a war plan is far stronger than an attitude penalty; the 900 EP
  cost, hard eligibility checks, and 70% chance cap are intentional controls.
- Requiring a land target excludes naval provocations in version one but avoids
  creating wars the AI cannot execute.
- `MEMORY_GIVE_HELP` uses generic diplomacy wording and shares its count with
  genuine help.
- Political failure must be represented as a completed espionage operation so
  EP cannot be rerolled for free.
- War-plan success does not override later peace treaties, vassalization, or
  other state changes.
- Multiplayer requires exact synchronized RNG and execution-time revalidation.

## Implementation Outcome

- Both mission records were appended after Stage Diplomatic Incident, with
  optional schema/info fields and read-only Python bindings.
- Shared DLL validation now covers the spy, plot, territory owner, target
  eligibility, Casus Belli chance, popup display, AI valuation, and
  synchronized execution.
- Establish Backchannels adds one unlimited, save-backed
  `MEMORY_GIVE_HELP` count per successful operation.
- Fabricate Casus Belli charges EP on either political outcome and creates
  only `WARPLAN_PREPARING_LIMITED` on synchronized success.
- Team-level human control is excluded so a reported mobilization always
  belongs to a team whose native AI war-plan processing can advance.
- Seventeen focused espionage contracts, the changed-file gate with DLL
  compilation, and the full repository gate passed.

## Proposed Implementation Sequence

1. Add focused failing contracts for both missions and chance boundaries.
2. Add optional XML/info fields and append both mission records.
3. Factor shared diplomatic-spy physical and candidate validation.
4. Implement Establish Backchannels effect, unlimited stacking, messages, cost,
   and AI value.
5. Implement Casus Belli eligibility and shared chance calculation.
6. Add second-popup odds display and execution result messages.
7. Add synchronized political roll and native limited-war preparation.
8. Add deterministic AI candidate selection and expected-value scoring.
9. Update architecture and manual smoke documentation.
10. Build/deploy the DLL and run focused, changed-file, full, installed, and
    multiplayer validation.
11. Commit as a contained espionage-escalation change; do not push without
    explicit user approval.

## Readiness

- Existing runtime path supports both missions: **Yes**.
- Backchannels can reuse save-backed native memory without new save state:
  **Yes**.
- Native synchronized war-plan creation is available: **Yes**.
- Proposed behavior is deterministic and implementable: **Yes**.
- Implemented and automated gates passing: **Yes**.
- Ready for installed acceptance: **Yes**.
- Ready for merge/deploy: **No**; installed single-player and fresh two-client
  multiplayer/OOS validation remain pending.
