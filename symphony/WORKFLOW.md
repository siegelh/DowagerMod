---
tracker:
  kind: github
  owner: siegelh
  owner_type: user
  repo: DowagerMod
  project_number: 1
  api_token_env: GITHUB_TOKEN
  status_field: Status
  ready_state: Ready
  planning_state: Planning
  in_progress_state: In Progress
  blocked_state: Blocked
  human_review_state: Human Review
  done_state: Done
  blocker_labels:
    - blocked
    - needs-human
    - do-not-touch
    - design-needed
workspace:
  root: C:\sw
  base_branch: agent-baseline
  branch_prefix: symphony
runtime:
  state_root: $LOCALAPPDATA\Symphony\DowagerMod
  poll_interval_seconds: 60
  error_backoff_seconds: 120
codex:
  command:
    - codex
    - app-server
  approval_policy: never
  thread_sandbox: danger-full-access
  turn_sandbox_policy: danger-full-access
  model: gpt-5-codex
  model_provider: openai
  effort: low
  read_timeout_ms: 10000
  turn_timeout_ms: 3600000
---
You are Symphony operating on GitHub issue #{{ issue.number }} in {{ issue.repository_full_name }}.

Worktree:
- Branch: `{{ branch_name }}`
- Path: `{{ workspace_path }}`

Issue:
- Title: {{ issue.title }}
- URL: {{ issue.url }}
- Labels: {{ issue.labels | join(", ") if issue.labels else "none" }}
- Current project status: {{ issue.project_status }}

Issue body:
{{ issue.body if issue.body else "(empty)" }}

Repo rules you must follow:
- Read `README.md`, `AGENTS.md`, `WORKFLOW.md`, `ARCHITECTURE.md`, `docs/index.md`, and `docs/TESTING_WORKFLOW.md` before making changes.
- Read `docs/MANUAL_SMOKE_TESTS.md` if the task changes gameplay behavior.
- Use the repo's code-first trust model. If docs and code disagree, code wins unless a human says otherwise.
- For non-trivial tasks, create or update a checked-in plan under `docs/plans/active/`.
- Respect `tools/test_gate.ps1` for BtS XML and DLL edits.
- Do not auto-merge, do not close the issue, and do not treat historical docs as authoritative without verification.
- Stop and mark uncertainty when runtime entrypoints, ownership boundaries, or validation requirements are unclear.

Your goal is to complete the issue as far as safely possible inside this worktree and leave the branch ready for human review.
