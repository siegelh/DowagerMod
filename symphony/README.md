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
- supports a local polling worker so Symphony can be started for a modding session and watch GitHub for `Ready` issues

Current workspace root:

- `C:\sw`

This intentionally keeps worktree checkout paths short enough for the mirrored game tree on Windows.

Current non-goals for this slice:

- no auto-merge
- no direct issue closure
- no background PR-review, triage, or hygiene jobs yet

Run from repo root:

```powershell
python -m symphony.main --workflow symphony/WORKFLOW.md run-once --dry-run
python -m symphony.main --workflow symphony/WORKFLOW.md run-once
python -m symphony.main --workflow symphony/WORKFLOW.md serve
python -m symphony.main --workflow symphony/WORKFLOW.md status
python -m symphony.main --workflow symphony/WORKFLOW.md stop
python -m symphony.main --workflow symphony/WORKFLOW.md cleanup
python -m symphony.main --workflow symphony/WORKFLOW.md cleanup --apply
```

Use `--issue-number <n>` to limit a run to one specific `Ready` issue.

Windows helper scripts:

```powershell
.\tools\Start-Symphony.ps1
.\tools\Symphony-Status.ps1
.\tools\Stop-Symphony.ps1
.\tools\Cleanup-Symphony.ps1
```

Worktree lifecycle right now:

- Symphony creates one local git worktree per issue under `C:\sw\gh-<issue-number>`.
- The corresponding branch is named `symphony/<issue-number>-<short-slug>`.
- Worktrees persist after PR creation and even after merge unless they are explicitly cleaned up.
- This is intentional for now so you can inspect, rebuild, and manually test candidate branches locally.
- `cleanup` is conservative and dry-run-first. It only removes clean local worktrees/branches when the issue is clearly done and there is no open PR.
- Cleanup can also move the GitHub Project item to `Done` when the merged/closed work is confirmed during pruning.

Planned next job types:

- `implement_issue`
- `review_pr`
- `triage_issue`
- `hygiene_scan`
