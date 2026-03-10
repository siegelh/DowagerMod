from __future__ import annotations

from .models import ChangeSet, GitHubIssue, PullRequestInfo, ValidationResult


def build_commit_message(issue: GitHubIssue, plan_paths: tuple[str, ...]) -> str:
    lines = [f"symphony: address #{issue.number}", "", f"Issue: #{issue.number}", f"Title: {issue.title}"]
    if plan_paths:
        lines.append(f"Plans: {', '.join(plan_paths)}")
    return "\n".join(lines)


def build_pull_request_title(issue: GitHubIssue) -> str:
    return issue.title


def build_pull_request_body(
    issue: GitHubIssue,
    branch_name: str,
    change_set: ChangeSet,
    validation: ValidationResult,
) -> str:
    lines = [
        f"Automated Symphony handoff for #{issue.number}.",
        "",
        "## Summary",
        f"- Issue: #{issue.number}",
        f"- Branch: `{branch_name}`",
    ]
    if change_set.files:
        lines.extend(["", "## Changed Files"])
        lines.extend(_render_paths(change_set.files))
    if change_set.plan_paths:
        lines.extend(["", "## Plan Docs"])
        lines.extend(_render_paths(change_set.plan_paths))
    lines.extend(["", "## Validation", _render_validation_summary(validation)])
    if _requires_manual_smoke_test(change_set):
        lines.extend(
            [
                "",
                "## Manual Testing",
                "- Gameplay-impacting DLL/XML changes were detected.",
                "- Run the manual smoke test flow in `docs/MANUAL_SMOKE_TESTS.md` before merge.",
            ]
        )
    lines.extend(["", f"Closes #{issue.number}"])
    return "\n".join(lines).strip()


def build_success_issue_comment(
    issue: GitHubIssue,
    branch_name: str,
    workspace_path: str,
    pull_request: PullRequestInfo,
    change_set: ChangeSet,
    validation: ValidationResult,
) -> str:
    lines = [
        f"Symphony prepared a review handoff for #{issue.number}.",
        "",
        f"- Branch: `{branch_name}`",
        f"- Worktree: `{workspace_path}`",
        f"- Draft PR: {pull_request.url}",
        f"- Validation: {_render_validation_summary(validation)}",
    ]
    if change_set.plan_paths:
        lines.append(f"- Plan docs: {', '.join(f'`{path}`' for path in change_set.plan_paths)}")
    if change_set.files:
        lines.extend(["", "Changed files:"])
        lines.extend(_render_paths(change_set.files))
    if _requires_manual_smoke_test(change_set):
        lines.extend(
            [
                "",
                "Manual follow-up:",
                "- Gameplay-impacting DLL/XML changes were detected.",
                "- Use the worktree above to rebuild/install/test before merge.",
                "- Follow `docs/MANUAL_SMOKE_TESTS.md` for the smoke-test checklist.",
            ]
        )
    return "\n".join(lines).strip()


def build_blocked_issue_comment(
    issue: GitHubIssue,
    branch_name: str,
    workspace_path: str,
    change_set: ChangeSet,
    reason: str,
    validation: ValidationResult | None = None,
) -> str:
    lines = [
        f"Symphony stopped in `Blocked` for #{issue.number}.",
        "",
        f"- Branch: `{branch_name}`",
        f"- Worktree: `{workspace_path}`",
        f"- Reason: {reason}",
    ]
    if validation is not None:
        lines.append(f"- Validation: {_render_validation_summary(validation)}")
        if validation.output:
            lines.extend(["", "Validation output:", "```text", _truncate(validation.output), "```"])
    if change_set.files:
        lines.extend(["", "Changed files:"])
        lines.extend(_render_paths(change_set.files))
    return "\n".join(lines).strip()


def _render_paths(paths: tuple[str, ...]) -> list[str]:
    return [f"- `{path}`" for path in paths]


def _render_validation_summary(validation: ValidationResult) -> str:
    if not validation.required:
        return "No repo-native validation gate was required."
    command = " ".join(validation.command)
    status = "passed" if validation.passed else "failed"
    return f"`{command}` {status}."


def _requires_manual_smoke_test(change_set: ChangeSet) -> bool:
    return change_set.requires_xml_gate or change_set.requires_dll_gate


def _truncate(value: str, limit: int = 4000) -> str:
    if len(value) <= limit:
        return value
    return value[: limit - 15].rstrip() + "\n...[truncated]"
