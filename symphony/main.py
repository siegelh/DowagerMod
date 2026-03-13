from __future__ import annotations

import argparse
import json
import os
import signal
import sys
import time
from pathlib import Path

from .cleanup import CleanupManager
from .config import ConfigError, build_config
from .github_client import GitHubClient, GitHubClientError
from .logging_utils import configure_logging, log_event
from .orchestrator import SymphonyService
from .server import SymphonyServer
from .service_runtime import ServiceRuntime, ServiceRuntimeError, wait_for_stop
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

    serve = subparsers.add_parser("serve", help="Run Symphony as a local polling worker.")
    serve.add_argument(
        "--poll-interval-seconds",
        type=int,
        help="Override the workflow poll interval for this process.",
    )
    serve.add_argument(
        "--error-backoff-seconds",
        type=int,
        help="Override the workflow error backoff interval for this process.",
    )

    status = subparsers.add_parser("status", help="Show the local Symphony worker status.")
    status.add_argument("--json", action="store_true", help="Print status as JSON.")

    stop = subparsers.add_parser("stop", help="Request that the local Symphony worker stop.")
    stop.add_argument(
        "--wait-seconds",
        type=int,
        default=30,
        help="How long to wait for a graceful stop before returning.",
    )
    stop.add_argument("--force", action="store_true", help="Force-kill the worker if it does not stop in time.")

    cleanup = subparsers.add_parser("cleanup", help="Scan or prune completed Symphony worktrees.")
    cleanup.add_argument("--issue-number", type=int, help="Limit cleanup scanning to one issue.")
    cleanup.add_argument("--apply", action="store_true", help="Remove eligible worktrees and local branches.")
    cleanup.add_argument("--json", action="store_true", help="Print cleanup candidates as JSON.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repo_root = Path(__file__).resolve().parent.parent

    try:
        workflow = load_workflow(repo_root / args.workflow)
        config = build_config(workflow, repo_root)
        logger = configure_logging(config.runtime.state_root)
        runtime = ServiceRuntime(config.runtime.state_root)
        cleanup_manager = CleanupManager(
            repo_root=repo_root,
            github_config=config.github,
            workspace_config=config.workspace,
        )
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
        if args.command == "serve":
            server = SymphonyServer(
                service=service,
                runtime=runtime,
                logger=logger,
                poll_interval_seconds=(
                    args.poll_interval_seconds
                    if args.poll_interval_seconds is not None
                    else config.runtime.poll_interval_seconds
                ),
                error_backoff_seconds=(
                    args.error_backoff_seconds
                    if args.error_backoff_seconds is not None
                    else config.runtime.error_backoff_seconds
                ),
            )
            return server.serve_forever()
        if args.command == "status":
            status = runtime.read_status().payload
            if args.json:
                print(json.dumps(status, indent=2))
            else:
                print(_format_status(status))
            return 0
        if args.command == "stop":
            status = runtime.read_status().payload
            if not status.get("is_running"):
                print("Symphony is not running.")
                return 0

            runtime.request_stop()
            stopped = wait_for_stop(runtime, timeout_seconds=max(1, args.wait_seconds))
            if stopped.is_running and args.force:
                pid = status.get("pid")
                if pid:
                    os.kill(int(pid), signal.SIGTERM)
                    time.sleep(1)
                    stopped = runtime.read_status()
            final_status = stopped.payload
            if final_status.get("is_running"):
                print(_format_status(final_status))
                return 1
            print("Symphony stopped.")
            return 0
        if args.command == "cleanup":
            candidates = cleanup_manager.scan(issue_number=args.issue_number)
            cleaned = ()
            if args.apply:
                cleaned = cleanup_manager.apply(candidates)
            payload = {
                "apply": args.apply,
                "cleaned_count": len(cleaned),
                "candidates": [
                    {
                        "issue_number": candidate.issue_number,
                        "issue_title": candidate.issue_title,
                        "issue_state": candidate.issue_state,
                        "project_status": candidate.project_status,
                        "branch_name": candidate.branch_name,
                        "workspace_path": candidate.workspace_path,
                        "has_open_pull_request": candidate.has_open_pull_request,
                        "merged_pull_request_url": candidate.merged_pull_request_url,
                        "is_clean": candidate.is_clean,
                        "eligible": candidate.eligible,
                        "reasons": list(candidate.reasons),
                    }
                    for candidate in candidates
                ],
            }
            if args.json:
                print(json.dumps(payload, indent=2))
            else:
                print(_format_cleanup_report(payload))
            return 0
    except (WorkflowError, ConfigError, GitHubClientError, ServiceRuntimeError) as exc:
        print(f"Symphony startup failed: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # pragma: no cover - final guardrail
        print(f"Symphony run failed: {exc}", file=sys.stderr)
        return 2

def _format_status(status: dict[str, object]) -> str:
    lines = [
        f"running: {status.get('is_running', False)}",
        f"state: {status.get('state', 'unknown')}",
        f"mode: {status.get('mode', 'unknown')}",
    ]
    if status.get("pid") is not None:
        lines.append(f"pid: {status['pid']}")
    if status.get("last_pid") is not None and status.get("pid") is None:
        lines.append(f"last_pid: {status['last_pid']}")
    for key in (
        "started_at",
        "heartbeat_at",
        "stopped_at",
        "last_issue_number",
        "last_issue_title",
        "last_outcome",
        "last_project_status",
        "last_pull_request_url",
        "note",
        "status_path",
    ):
        value = status.get(key)
        if value not in (None, ""):
            lines.append(f"{key}: {value}")
    return "\n".join(lines)


def _format_cleanup_report(payload: dict[str, object]) -> str:
    candidates = list(payload.get("candidates", []))
    lines = [f"apply: {payload.get('apply', False)}", f"cleaned_count: {payload.get('cleaned_count', 0)}"]
    if not candidates:
        lines.append("candidates: none")
        return "\n".join(lines)

    lines.append("candidates:")
    for candidate in candidates:
        reason_text = ", ".join(candidate.get("reasons", [])) or "eligible"
        lines.append(
            f"- #{candidate['issue_number']} {candidate['branch_name']} | eligible={candidate['eligible']} | clean={candidate['is_clean']} | status={candidate['project_status']} | issue_state={candidate['issue_state']} | reasons={reason_text}"
        )
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
