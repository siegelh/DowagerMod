from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .config import ConfigError, build_config
from .github_client import GitHubClient, GitHubClientError
from .logging_utils import configure_logging, log_event
from .orchestrator import SymphonyService
from .workflow_loader import WorkflowError, load_workflow


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Symphony orchestration CLI for DowagerMod.")
    parser.add_argument(
        "--workflow",
        default="symphony/WORKFLOW.md",
        help="Path to the machine-readable Symphony workflow file.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)
    run_once = subparsers.add_parser("run-once", help="Fetch one Ready issue and run one Codex turn.")
    run_once.add_argument("--dry-run", action="store_true", help="Select and report an issue without mutating GitHub or git.")
    run_once.add_argument("--issue-number", type=int, help="Limit processing to one Ready issue number.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repo_root = Path(__file__).resolve().parent.parent

    try:
        workflow = load_workflow(repo_root / args.workflow)
        config = build_config(workflow, repo_root)
        logger = configure_logging(config.runtime.state_root)
        service = SymphonyService(
            repo_root=repo_root,
            workflow=workflow,
            config=config,
            github=GitHubClient(config.github),
            logger=logger,
        )
        if args.command == "run-once":
            summary = service.run_once(issue_number=args.issue_number, dry_run=args.dry_run)
            if summary is None:
                return 0
            log_event(
                logger,
                "Run completed",
                event="run_summary",
                issue_number=summary.issue_number,
                outcome=summary.outcome,
                project_status=summary.project_status,
                branch_name=summary.branch_name,
                workspace_path=summary.workspace_path,
            )
            return 0
    except (WorkflowError, ConfigError, GitHubClientError) as exc:
        print(f"Symphony startup failed: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # pragma: no cover - final guardrail
        print(f"Symphony run failed: {exc}", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
