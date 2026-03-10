# Symphony

Symphony is a repo-local Python orchestration tool for agent-driven issue execution against `siegelh/DowagerMod`.

Current scope of the first vertical slice:

- loads machine-readable runtime config from `symphony/WORKFLOW.md`
- reads GitHub Issues plus GitHub Project v2 state for the `DowagerMod` board
- selects the oldest eligible `Ready` issue
- creates or reuses a git worktree from `agent-baseline`
- runs one Codex app-server turn inside that worktree
- writes a local JSON run summary outside the repo tree
- moves the project item to `Human Review` on success or `Blocked` on failure

Current non-goals for this slice:

- no auto-merge
- no direct issue closure
- no PR creation yet
- no daemon loop yet

Run from repo root:

```powershell
python -m symphony.main --workflow symphony/WORKFLOW.md run-once --dry-run
python -m symphony.main --workflow symphony/WORKFLOW.md run-once
```

Use `--issue-number <n>` to limit a run to one specific `Ready` issue.
