# Symphony

Symphony is a repo-local Python orchestration tool for agent-driven work against `siegelh/DowagerMod`.

It now supports a **squad-oriented model** on top of the original issue-delivery flow.

## Current squad jobs

- `implement_issue`
  - `Lead` kickoff comment
  - `Implementer` worktree edits and validation
  - `Reviewer` review-ready issue handoff
- `triage_issue`
  - consumes `Inbox` issues
  - comments with a TLDR and moves issues to `Ready`, `Inbox`, or `Blocked`
- `review_pr`
  - targets open Symphony-authored PRs
  - posts a concise PR review summary comment
- `hygiene_scan`
  - scheduled repo-health scan
  - creates or updates a GitHub maintenance issue when findings exist

## Human workflow

1. Create a GitHub issue.
2. Add it to the `DowagerMod` Project.
3. Leave it in `Inbox` if it needs triage, or move it to `Ready` if it is clearly implementation-ready.
4. Start Symphony for the session.
5. Symphony routes the work through the squad and leaves a GitHub-visible handoff.
6. Review the draft PR.
7. For gameplay changes, test locally from the preserved issue worktree before merge.

When the local worker is running, it may pick up:

- `Ready` issues for implementation
- `Inbox` issues for triage
- open Symphony-authored PRs for review
- scheduled hygiene scans when due

## Current implementation scope

- loads machine-readable runtime config from `symphony/WORKFLOW.md`
- loads checked-in squad charters from `symphony/squad/`
- reads GitHub Issues and GitHub Project v2 state for the `DowagerMod` board
- routes work across `Inbox`, `Ready`, open Symphony PRs, and scheduled hygiene runs
- creates or reuses a git worktree from `agent-baseline` for implementation work
- runs Codex app-server turns for implementation, triage, review, and hygiene roles
- runs repo-native validation when DLL or BtS XML changes are detected
- commits and pushes the issue branch after successful implementation validation
- creates or reuses a draft PR targeting `agent-baseline`
- auto-cleans clean local issue worktrees during polling once the associated Symphony PR is merged and the GitHub issue is closed
- writes local JSON run summaries outside the repo tree
- updates GitHub comments and project state for handoff
- supports a local polling worker so Symphony can run during a modding session

Current workspace root:

- `C:\sw`

This intentionally keeps worktree checkout paths short enough for the mirrored game tree on Windows.

Current non-goals for this slice:

- no auto-merge
- no direct issue closure
- no cloud-hosted worker requirement
- no multiple simultaneous heavy implementation jobs

Run from repo root:

```powershell
python -m symphony.main --workflow symphony/WORKFLOW.md run-once --dry-run
python -m symphony.main --workflow symphony/WORKFLOW.md run-once
python -m symphony.main --workflow symphony/WORKFLOW.md run-once --job triage_issue --issue-number 123
python -m symphony.main --workflow symphony/WORKFLOW.md run-once --job review_pr --pull-request-number 456
python -m symphony.main --workflow symphony/WORKFLOW.md serve
python -m symphony.main --workflow symphony/WORKFLOW.md status
python -m symphony.main --workflow symphony/WORKFLOW.md status --verbose
python -m symphony.main --workflow symphony/WORKFLOW.md stop
python -m symphony.main --workflow symphony/WORKFLOW.md cleanup
python -m symphony.main --workflow symphony/WORKFLOW.md cleanup --apply
```

Use `--issue-number <n>` or `--pull-request-number <n>` to target one specific GitHub item.

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
- Worktrees persist after PR creation so you can inspect, rebuild, and manually test candidate branches locally.
- When the local worker is polling, Symphony now auto-cleans clean local worktrees only after the associated PR is merged and the GitHub issue is closed.
- `cleanup` is conservative and dry-run-first. It only removes clean local worktrees/branches when the issue is clearly done and there is no open PR.
- Cleanup can also move the GitHub Project item to `Done` when the merged/closed work is confirmed during pruning.
