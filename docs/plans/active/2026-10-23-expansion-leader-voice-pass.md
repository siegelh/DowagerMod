# Expansion Leader Voice Pass

- Status: `complete`
- Owner / agent: Copilot
- Last updated: `2026-10-23`

## Problem Statement

- Task: resolve issue #152 by assigning intentional voices to all thirteen
  leaders added by the current expansion branch.
- Current observed behavior: the expansion leaders are absent from
  `tools/chatter/leader_voices.json`, so they use generic English fallback
  voices. The audit also derives names such as `Exp Zenobia` from XML IDs
  instead of resolving the localized leader description.
- Why this is a real repo/code problem: the game sends localized leader
  descriptions to the chatter sidecar, while the audit was checking different
  names and therefore could not verify the live lookup contract.

## Why This Matters

- The fallback pool does not preserve historical region, language, age, or
  gender. In particular, Zenobia currently resolves through the male pool.
- Explicit mappings make playtests reproducible and let reviewers audition the
  same voice for every run.

## Scope

- Resolve audit names from the live BtS text XML.
- Add explicit mappings for all thirteen expansion leaders.
- Use supported standard Azure Speech voices and record prosody/native-language
  choices in the existing voice map.
- Add regression tests for coverage and Zenobia's female voice.

## Non-Goals

- No gameplay XML, DLL, leader art, dialogue-writing, or ElevenLabs changes.
- No claim that a modern regional voice reconstructs an unavailable ancient
  language.

## Trusted Sources Of Truth

- `Beyond the Sword/Assets/Python/CvLeaderChatter.py` supplies
  `CvLeaderHeadInfo.getDescription()` as the runtime leader name.
- `Beyond the Sword/Assets/XML/Civilizations/CIV4LeaderHeadInfos.xml` and the
  BtS text XML define leader IDs and localized display names.
- `tools/chatter/leader_voices.json` and `voice_picker.py` define runtime voice
  selection.
- Microsoft Azure Speech language-support documentation defines valid standard
  voice IDs.

## Proposed Implementation Steps

1. Resolve audit display names through the live English text keys.
2. Add explicit supported mappings for every expansion leader.
3. Add focused coverage and gender regression tests.
4. Generate a no-audio audit and, when credentials are configured, audition
   WAVs for all thirteen leaders.
5. Run focused chatter tests and the repository gate.

## Validation Plan

- `python tools/chatter/audit_leader_voices.py --no-audio`
- `python -m pytest -q tools/chatter/tests/test_leader_voices.py`
- Relevant existing chatter tests.
- `.\tools\test_gate.ps1`
- Human listening review of the generated expansion audition WAVs remains the
  authoritative quality gate.

## Risks / Rollback

- Regional modern voices for Piye, Hiram I, Askia Muhammad, and Sennacherib are
  approximations because their historical languages lack supported voices.
- Mongkut and Ramkhamhaeng share Azure's standard male Thai voice and are
  differentiated through rate and pitch.
- Rollback is limited to the voice map, audit, tests, and this plan.

## Completion Checklist

- [x] Runtime name source verified.
- [x] Supported voice IDs verified against current Azure documentation.
- [x] Explicit mappings added for all thirteen leaders.
- [x] Focused regression tests added.
- [x] No-audio audit reports zero fallback leaders.
- [x] Audition WAVs generated or credential blocker recorded.
- [x] Focused chatter tests pass.
- [x] Repository gate passes.
- [x] Human listening review completed or recorded as pending.

## Final Outcome Summary

- What changed: all thirteen expansion leaders now have explicit supported
  Azure voice mappings, and the audit resolves the same localized names used
  by the game runtime.
- Validation performed: 72/72 explicit audit coverage, four focused
  regressions, 317 complete chatter tests with two skips, and the repository
  changed-file gate.
- Remaining risk: none identified within the voice-mapping scope. All thirteen
  audition WAVs synthesized successfully, and the user approved the listening
  review on 2026-10-23.
