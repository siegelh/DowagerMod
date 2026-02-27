# Output Template

## 1) Historical Thesis
- Era scope
- Core identity statement (1-2 lines)
- 3-5 historical anchors with sources

## 2) Current Baseline (As-Is)
- Leader traits and standout mechanics
- Civ package (UU, UB, palace replacement, specials)
- What should stay and why
- What should change and why

## 3) Overhaul Package (Recommended)
- `LEADER_*` trait changes
- `CIVILIZATION_*` changes
- UU decision: keep / modify / replace
- UB decision: keep / modify / replace
- Palace decision: keep / modify / replace
- Rare improvement (if used): full spec + gating + cap

## 4) Numbers and Exact Targets
- Precise XML ids and values
- Prerequisites and terrain/resource constraints
- AI-relevant notes

## 5) Art Plan
- Existing in-workspace art candidates
- External candidates from `C:\Users\Harrison\Downloads\civ4mods-code`
- Copy plan into workspace before reference
- Fallback art if custom import fails

## 6) UX/Text Plan
- Civilopedia trait/civ text keys to add/update
- Worker/build action help text
- Tooltip validation points (avoid raw `%` placeholders)

## 7) Risk and Validation
- Schema and XML validation checks
- In-game test cases
- Rollback/minimal fallback plan

## 8) Implementation Phasing
- Phase 1: low-risk core
- Phase 2: medium-risk identity extras
- Phase 3: optional polish
