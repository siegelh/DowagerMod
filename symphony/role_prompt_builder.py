from __future__ import annotations

from typing import Iterable

from .models import GitHubIssue, PullRequestFile, PullRequestInfo, RunSummary, WorkflowDefinition
from .squad_registry import SquadRegistry
from .workflow_loader import render_prompt


class RolePromptBuilder:
    def __init__(self, workflow: WorkflowDefinition, registry: SquadRegistry):
        self._workflow = workflow
        self._registry = registry

    def build_implementer_prompt(
        self,
        issue: GitHubIssue,
        branch_name: str,
        workspace_path: str,
        repo_root: str,
    ) -> str:
        base_prompt = render_prompt(
            self._workflow,
            {
                "issue": issue.template_context(),
                "attempt": None,
                "branch_name": branch_name,
                "workspace_path": workspace_path,
                "repo_root": repo_root,
                "workflow_path": str(self._workflow.path),
            },
        )
        return self._compose(
            role_name="implementer",
            headline=f"Implement GitHub issue #{issue.number} in the provided worktree.",
            sections=[
                ("Issue", _issue_block(issue)),
                ("Execution", base_prompt),
            ],
        )

    def build_triage_prompt(self, issue: GitHubIssue) -> str:
        return self._compose(
            role_name="triage",
            headline=(
                "Classify the GitHub issue for implementation readiness. "
                "Return JSON only with keys action, summary, and missing."
            ),
            sections=[
                ("Issue", _issue_block(issue)),
                (
                    "Required JSON format",
                    (
                        '{\n'
                        '  "action": "ready" | "inbox" | "blocked",\n'
                        '  "summary": "One short TLDR for the human.",\n'
                        '  "missing": ["missing detail 1", "missing detail 2"]\n'
                        '}'
                    ),
                ),
                (
                    "Rules",
                    "\n".join(
                        [
                            "- Use `ready` only if the issue is actionable for an implementation agent now.",
                            "- Use `inbox` if the issue needs clarification or decomposition but is not blocked by policy.",
                            "- Use `blocked` if the issue should not proceed without a human decision or dependency.",
                            "- Keep `summary` concise and practical.",
                            "- Keep `missing` empty when action is `ready`.",
                        ]
                    ),
                ),
            ],
        )

    def build_review_pr_prompt(
        self,
        pull_request: PullRequestInfo,
        files: Iterable[PullRequestFile],
        latest_summary: RunSummary | None,
    ) -> str:
        file_section = "\n".join(_render_pr_file(file_info) for file_info in files) or "- No file list available."
        validation_section = (
            f"Latest validation: {latest_summary.validation_command or 'none'} | "
            f"passed={latest_summary.validation_passed}"
            if latest_summary is not None
            else "Latest validation: no local Symphony summary found."
        )
        return self._compose(
            role_name="reviewer",
            headline="Review this Symphony-authored pull request and produce a concise markdown review summary.",
            sections=[
                (
                    "Pull Request",
                    "\n".join(
                        [
                            f"- Number: #{pull_request.number}",
                            f"- Title: {pull_request.title}",
                            f"- URL: {pull_request.url}",
                            f"- Head: {pull_request.head_ref_name}",
                            f"- Base: {pull_request.base_ref_name}",
                        ]
                    ),
                ),
                ("Validation", validation_section),
                ("Changed Files", file_section),
                (
                    "Required format",
                    "\n".join(
                        [
                            "Reply in markdown with these headings:",
                            "## TLDR",
                            "## Findings",
                            "## Human Test Focus",
                            "Keep each section short and action-oriented.",
                        ]
                    ),
                ),
            ],
        )

    def build_hygiene_prompt(self, findings_markdown: str) -> str:
        return self._compose(
            role_name="hygiene",
            headline="Turn these repo hygiene findings into a concise maintenance issue body.",
            sections=[
                ("Findings", findings_markdown or "- No findings."),
                (
                    "Required format",
                    "\n".join(
                        [
                            "Reply in markdown with headings:",
                            "## TLDR",
                            "## Findings",
                            "## Recommended Follow-up",
                            "Keep it concrete and conservative.",
                        ]
                    ),
                ),
            ],
        )

    def _compose(self, role_name: str, headline: str, sections: list[tuple[str, str]]) -> str:
        role = self._registry.get_role(role_name)
        lines = [
            f"Team Charter:\n{self._registry.team_charter}",
            "",
            f"Role Charter ({role.name}):\n{role.charter}",
            "",
            headline,
        ]
        for title, body in sections:
            lines.extend(["", f"{title}:", body.strip()])
        return "\n".join(lines).strip()


def _issue_block(issue: GitHubIssue) -> str:
    return "\n".join(
        [
            f"- Number: #{issue.number}",
            f"- Title: {issue.title}",
            f"- URL: {issue.url}",
            f"- Labels: {', '.join(issue.labels) if issue.labels else 'none'}",
            f"- Project Status: {issue.project_status}",
            "",
            "Body:",
            issue.body or "(empty)",
        ]
    )


def _render_pr_file(file_info: PullRequestFile) -> str:
    patch = file_info.patch.strip() or "(patch unavailable)"
    if len(patch) > 1200:
        patch = patch[:1185].rstrip() + "\n...[truncated]"
    return "\n".join(
        [
            f"- `{file_info.filename}` ({file_info.status}, +{file_info.additions}/-{file_info.deletions})",
            "```diff",
            patch,
            "```",
        ]
    )
