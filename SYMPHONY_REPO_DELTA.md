# Symphony Repo Delta For DowagerMod

Status: Draft v1 for this repository

This document adapts `SYMPHONY_SPEC.md` to the actual DowagerMod repo environment. It is a delta, not a replacement. The base spec remains the detailed service design; this file defines what must change so Symphony fits this repo.

If this file and the repo disagree, trust the current repo policy in `AGENTS.md`, `WORKFLOW.md`, `ARCHITECTURE.md`, and the live scripts.

## 1. What Stays The Same

These parts of `SYMPHONY_SPEC.md` still fit this repo well:

- Symphony should be a long-running Python orchestration service, not a one-off script.
- It should isolate work per issue in persistent per-issue workspaces.
- It should keep orchestration state outside the coding agent itself.
- It should load a machine-readable runtime workflow/config file from the repo.
- It should treat structured logs and restart recovery as first-class concerns.
- It should separate:
  - workflow/policy
  - configuration
  - orchestration
  - workspace management
  - agent execution
  - tracker integration

## 2. Core Repo Constraints

### Confirmed from this repo

- The default code-edit target is the BtS assets root:
  - `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets`
- The authoritative DLL source is:
  - `third_party/beyond-the-sword-sdk/CvGameCoreDLL`
- The canonical installer is:
  - `CoreFiles/install.py`
- The current long-lived baseline branch is:
  - `agent-baseline`
- Non-trivial work is expected to create or update a checked-in plan under:
  - `docs/plans/active/`
- BtS XML and DLL changes must respect:
  - `.\tools\test_gate.ps1`
- Gameplay changes require a manual smoke test per:
  - `docs/MANUAL_SMOKE_TESTS.md`

### Important repo realities Symphony must respect

- The repo contains historical docs and legacy material; Symphony must use the code-first trust model from `AGENTS.md`.
- The repo is Windows-first in practice.
- The repo uses PowerShell tooling.
- The full mirrored game tree under `CoreFiles/Sid Meier's Civilization IV Beyond the Sword` is intentional, but it is not the default edit target.
- Some runtime behavior still depends on legacy-looking content such as `petromod_v1`; Symphony must not assume that old-looking paths are safe to remove.

## 3. Replace Linear With GitHub

### Base spec assumption

- `SYMPHONY_SPEC.md` is currently Linear-first.

### DowagerMod delta

- Replace the tracker adapter with a GitHub adapter.
- Source of work should be:
  - GitHub Issues in the `siegelh/DowagerMod` repo
  - GitHub Projects v2 for queue/state tracking

### Confirmed GitHub board for this repo

- Owner:
  - `siegelh`
- Project name:
  - `DowagerMod`
- Project number:
  - `1`
- Project URL:
  - `https://github.com/users/siegelh/projects/1`

### Recommended v1 tracker model

- GitHub Issues are the canonical task records.
- GitHub Projects v2 is the canonical workflow state surface.
- The GitHub project should expose a single-select field named:
  - `Status`

### Recommended initial GitHub Project v2 setup

If you do not already have a project board, create one first:

1. Create a new GitHub Project v2 under the `siegelh` owner.
2. Add the `DowagerMod` repository to that project.
3. Add a single-select field named `Status`.
4. Populate `Status` with the recommended values in this section.
5. Create a default view filtered to open items from `DowagerMod`.
6. Add issues to the project and move only agent-safe work into `Ready`.

### Recommended initial project states

- `Inbox`
- `Ready`
- `Planning`
- `In Progress`
- `Blocked`
- `Human Review`
- `Done`

### Recommended blocker / escalation labels

Symphony should treat these labels as human blockers or escalation signals:

- `blocked`
- `needs-human`
- `do-not-touch`
- `design-needed`

These labels now exist on `siegelh/DowagerMod`.

### Recommended dispatch eligibility

An issue should be dispatch-eligible only if all are true:

- the issue is open
- it belongs to the configured GitHub Project v2
- its project status is `Ready`
- it is not already claimed by Symphony
- it does not carry any blocker/escalation label from the list above

### Recommended v1 simplification

- Do not port the Linear blocker/dependency logic directly into v1.
- GitHub dependency handling should be treated as unresolved unless you explicitly define a dependency source that Symphony can trust.
- For v1, use project status and labels as the dispatch gate instead of inferred dependency graphs.

### Recommended initial concurrency and dispatch order

- Start with:
  - `max_concurrent_agents = 1`
- If multiple issues are eligible at once:
  - dispatch oldest `Ready` issue first
- Do not add dependency-aware or multi-priority dispatch logic in v1 unless the GitHub project model is made more explicit.

## 4. Keep Root WORKFLOW.md Human-Normative

### Base spec assumption

- `WORKFLOW.md` is the machine-readable runtime workflow file.

### DowagerMod delta

- Do not overload the existing repo-root `WORKFLOW.md`.
- In this repo, root `WORKFLOW.md` is already a human normative workflow contract.
- Symphony should read a separate machine-readable runtime workflow file.

### Recommended file path

- `symphony/WORKFLOW.md`

### Recommended launch rule

- Start Symphony with an explicit workflow path.
- Do not rely on cwd default resolution to root `WORKFLOW.md`.

### Why this matters

- It preserves the repo's current human workflow document.
- It avoids breaking or reformatting `WORKFLOW.md` just to satisfy Symphony parsing.
- It keeps repo policy and Symphony runtime config related but distinct.

## 5. Use Git Worktrees, Not Generic Empty Workspaces

### Base spec assumption

- Workspaces are generic per-issue directories.

### DowagerMod delta

- For this repo, each workspace should be a git worktree rooted from `agent-baseline`.
- Plain directories are not sufficient.

### Recommended workspace model

- Base branch:
  - `agent-baseline`
- Per-issue branch:
  - `symphony/<issue-number>-<short-slug>`
- Workspace root:
  - outside the main repo working tree
  - Windows-friendly absolute path

### Recommended workspace root

- `%LOCALAPPDATA%\\Symphony\\workspaces\\DowagerMod`

### Worktree lifecycle

- Create the worktree on first dispatch for an issue.
- Reuse it across retries and continuation runs for that issue.
- Remove it only when all are true:
  - the linked PR is merged or explicitly abandoned
  - the issue is closed
  - the project item has been moved to `Done`
- Do not clean it eagerly after every run; it is useful for debugging failed agent attempts.
- If you later want automatic cleanup, add a retention delay rather than deleting immediately on merge.

## 6. Windows / PowerShell First

### Base spec assumption

- Commands launch via `bash -lc`.

### DowagerMod delta

- This repo is Windows-first and PowerShell-first.
- Do not hard-code `bash -lc` as the primary execution model.

### Recommended execution rules

- Launch Codex directly as a process when possible.
- Run hooks under PowerShell by default.
- Treat shell selection as explicit config, not an implicit Unix default.

### Recommended v1 default

- hook shell: `powershell`
- Codex command: direct `codex app-server`

## 7. Symphony Must Respect Repo Workflow Docs

Before an agent run starts, the prompt and/or runtime setup must direct the agent to read:

- `README.md`
- `AGENTS.md`
- `WORKFLOW.md`
- `ARCHITECTURE.md`
- `docs/index.md`
- `docs/TESTING_WORKFLOW.md`
- `docs/MANUAL_SMOKE_TESTS.md` when gameplay validation is relevant

The repo-specific Symphony workflow prompt should reinforce:

- code-first trust model
- checked-in plan requirement for non-trivial tasks
- `agent-baseline` branch ancestry
- mandatory test gate rules
- manual smoke-test requirement for gameplay changes
- explicit uncertainty escalation rules

## 8. Planning Is Not Optional For Non-Trivial Tasks

### Repo requirement

- Non-trivial work must create or update a checked-in plan under:
  - `docs/plans/active/`

### Symphony implication

- The agent prompt must instruct the agent to create or update a plan doc when the task is non-trivial.
- The plan should usually use the template at:
  - `docs/plans/active/TEMPLATE.md`

### Recommended plan naming

- `docs/plans/active/YYYY-MM-DD-gh-<issue-number>-short-slug.md`

## 9. Validation And Handoff Must Match Repo Reality

### Repo reality

- XML and DLL edits require `.\tools\test_gate.ps1`
- gameplay changes require manual smoke testing
- the repo has no authoritative CI pipeline doing that for you

### Symphony implication

- Symphony should never declare gameplay work complete purely from code edits and static checks.
- A successful code-edit run should usually end in a review/handoff state, not directly in `Done`.

### Recommended completion model

- `Human Review` is the default post-run handoff state for implementation work.
- `Done` should remain a human or merge-driven transition.

### Recommended v1 rule

- Symphony may:
  - branch
  - edit
  - validate what it can
  - commit
  - push
  - open or update a PR
  - move the issue/project item to `Human Review`
- Symphony should not auto-merge in v1.

### Issue closure recommendation

- Do not let Symphony close issues independently before merge.
- Prefer merge-driven issue closure by linking the PR to the issue with closing language such as:
  - `Closes #123`
- That keeps issue closure tied to reviewed code landing, not to an unfinished agent run.

## 10. Deterministic GitHub Writes Should Be Owned By Symphony

The base spec leaves many ticket writes to the coding agent. For this repo, that is too loose for core workflow state.

### Recommended split

- Symphony should directly own:
  - issue claiming / release
  - project status transitions
  - workspace-to-issue branch association
  - retry / blocked / human-review state updates
  - PR creation
- The coding agent may own:
  - implementation comments
  - plan/result summaries
  - PR body content

### Why

- project state should not depend on prompt quality alone
- deterministic state transitions belong in the orchestrator
- agent-authored narrative output is still useful, but should not be the only workflow record

## 11. Suggested GitHub Data Model

### Minimum issue fields Symphony should normalize

- repo issue node id
- issue number
- title
- body
- labels
- open/closed state
- assignees
- url
- created_at
- updated_at
- project item id
- project status field value

### Recommended optional fields

- linked PRs
- milestone
- issue type label(s)
- blocked / needs-human labels

### Recommended v1 non-goal

- Do not require full GitHub dependency graph support in v1.

## 12. Single-Repo, Local-First V1

### Recommended scope

- Support only `siegelh/DowagerMod` in v1.
- Run locally on the developer machine first.
- Keep the design clean enough to support a long-running host later, but do not optimize for multi-repo or multi-tenant operation yet.

### Why

- This repo is still hardening its agent workflow.
- The operational risk is much lower if the first version serves one repo in one known environment.

## 13. GitHub Authentication Requirements

### Confirmed working local setup

- `gh` is installed on the local Windows machine.
- GitHub CLI auth is working against `github.com`.
- Project access works with the current token.

### Required token capability for this repo

For local development and for any GitHub-backed Symphony runtime, the token must support:

- `repo`
- `project`
- `read:org`

### Environment recommendation

- Keep the token in:
  - `.env`
- Use:
  - `GITHUB_TOKEN=...`
- Do not commit `.env`.

## 14. Suggested Python Implementation Shape

This is not an implementation instruction set yet. It is a recommended shape for when coding begins.

- `symphony/`
  - `config.py`
  - `workflow_loader.py`
  - `github_client.py`
  - `orchestrator.py`
  - `worktree_manager.py`
  - `agent_runner.py`
  - `logging_utils.py`
  - `models.py`
  - `main.py`

### Recommended supporting assets

- `symphony/WORKFLOW.md`
- `symphony/README.md`
- `tests/` for unit tests
- local runtime state outside the repo root

## 15. Runtime State And Logs Should Not Dirty The Repo

### Recommended rule

- Do not store runtime logs, lock files, retry state, or orchestrator metadata inside the main repo working tree.

### Recommended locations

- logs/state:
  - `%LOCALAPPDATA%\\Symphony\\DowagerMod`
- worktrees:
  - `%LOCALAPPDATA%\\Symphony\\workspaces\\DowagerMod`

### Reason

- this repo already relies on git-aware changed-file validation
- runtime noise inside the main repo would confuse both agents and humans

## 16. Repo-Specific Safety Rules Symphony Must Enforce

- Always start issue work from `agent-baseline`.
- Never treat old docs or archived plans as authoritative without corroboration.
- Never skip `.\tools\test_gate.ps1` for BtS XML or DLL edits.
- Never assume manual smoke testing can be replaced by static validation for gameplay changes.
- Never rewrite or archive historical material unless the issue explicitly calls for it.
- Never assume the BtS Python tree is fully self-contained.
- Never assume `petromod_v1` is removable just because it looks legacy.

## 17. What Symphony Should Not Do In V1

- no auto-merge
- no automatic issue close on successful code edit alone
- no deletion/pruning of live install files
- no blind multi-root generator execution
- no automatic large-scale cleanup of legacy docs or runtime-coupled assets
- no assumption that GitHub dependency features are mature enough to drive scheduling without explicit repo policy

## 18. Current Readiness

The GitHub-side prerequisites are now in place:

- canonical project exists
- `Status` field exists
- status values are configured
- blocker labels exist
- `gh` access is working locally

No hard platform blocker remains before implementation.

The remaining practical prerequisites are:

- create one or more real GitHub Issues for Symphony to work against
- move a clearly scoped issue into `Ready`
- keep this delta and the implementation plan checked into the repo

## 19. Recommended Next Step

Before implementation, create a short checked-in implementation plan that locks down:

- branch naming
- worktree root
- review/merge policy
- cleanup policy

After that, implementation can begin against:

- `SYMPHONY_SPEC.md` as the base service spec
- `SYMPHONY_REPO_DELTA.md` as the DowagerMod adaptation layer
