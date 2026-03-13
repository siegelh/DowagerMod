# Symphony Squad

Symphony is the orchestration layer for DowagerMod. The squad is the set of functional agent roles Symphony uses to move GitHub work from `Inbox` to `Human Review`.

## Team Contract

- GitHub Issues and the `DowagerMod` Project board are the visible task surface.
- `agent-baseline` remains the runtime base branch for issue worktrees until squad behavior is proven.
- Only one heavy implementation job runs at a time.
- Lighter jobs like triage, review, and hygiene may run separately.
- Manual gameplay validation remains a human responsibility before merge.
- Squad outputs must be visible through GitHub comments, draft PRs, project status changes, and local Symphony logs.
- The squad must follow `AGENTS.md`, `WORKFLOW.md`, `ARCHITECTURE.md`, and `docs/index.md`.
