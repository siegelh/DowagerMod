# Symphony

Symphony is a repo-local Python orchestration tool for agent-driven issue execution against `siegelh/DowagerMod`.

Current scope of the implemented delivery slice:

- loads machine-readable runtime config from `symphony/WORKFLOW.md`
- reads GitHub Issues plus GitHub Project v2 state for the `DowagerMod` board
- selects the oldest eligible `Ready` issue
- creates or reuses a git worktree from `agent-baseline`
- runs one Codex app-server turn inside that worktree
- runs repo-native validation when DLL or BtS XML changes are detected
- commits and pushes the issue branch after successful validation
- creates or reuses a draft PR targeting `agent-baseline`
- posts an issue summary comment for human handoff
- writes a local JSON run summary outside the repo tree
- moves the project item to `Human Review` only after a validated draft-PR handoff exists, or to `Blocked` on failure

Current workspace root:

- `C:\sw`

This intentionally keeps worktree checkout paths short enough for the mirrored game tree on Windows.

Current non-goals for this slice:

- no auto-merge
- no direct issue closure
- no daemon loop yet
- no background PR-review, triage, or hygiene jobs yet

Run from repo root:

```powershell
python -m symphony.main --workflow symphony/WORKFLOW.md run-once --dry-run
python -m symphony.main --workflow symphony/WORKFLOW.md run-once
```

Use `--issue-number <n>` to limit a run to one specific `Ready` issue.

Planned next job types:

- `implement_issue`
- `review_pr`
- `triage_issue`
- `hygiene_scan`
