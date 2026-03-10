from __future__ import annotations

import itertools
import json
import queue
import subprocess
import threading
import time
from pathlib import Path
from typing import Any

from .config import CodexConfig
from .models import AgentRunResult


class AgentRunError(RuntimeError):
    """Raised when the Codex app-server lifecycle fails."""


class AgentRunner:
    def __init__(self, codex_config: CodexConfig, cwd: Path):
        self._config = codex_config
        self._cwd = cwd

    def run_turn(self, prompt: str) -> AgentRunResult:
        process = subprocess.Popen(
            list(self._config.command),
            cwd=self._cwd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            bufsize=1,
        )
        rpc = _JsonRpcProcess(process)
        try:
            rpc.start()
            rpc.request(
                "initialize",
                {
                    "clientInfo": {"name": "symphony", "version": "0.1.0"},
                    "capabilities": {"experimentalApi": True},
                },
                timeout_seconds=self._config.read_timeout_ms / 1000.0,
            )
            rpc.notify("notifications/initialized", {})

            thread_response = rpc.request(
                "thread/start",
                {
                    "cwd": str(self._cwd),
                    "approvalPolicy": self._config.approval_policy,
                    "sandbox": self._config.thread_sandbox,
                    "model": self._config.model,
                    "modelProvider": self._config.model_provider,
                    "developerInstructions": self._config.developer_instructions,
                    "baseInstructions": self._config.base_instructions,
                    "config": {},
                },
                timeout_seconds=self._config.read_timeout_ms / 1000.0,
            )
            thread_id = thread_response["thread"]["id"]

            turn_response = rpc.request(
                "turn/start",
                {
                    "threadId": thread_id,
                    "input": [{"type": "text", "text": prompt}],
                    "cwd": str(self._cwd),
                    "approvalPolicy": self._config.approval_policy,
                    "sandboxPolicy": _build_turn_sandbox_policy(self._config.turn_sandbox_policy),
                    "model": self._config.model,
                    "effort": self._config.effort,
                },
                timeout_seconds=self._config.read_timeout_ms / 1000.0,
            )
            turn = turn_response["turn"]
            turn_id = turn["id"]
            status = turn["status"]
            notifications: list[dict[str, Any]] = []

            if status != "inProgress":
                return AgentRunResult(
                    thread_id=thread_id,
                    turn_id=turn_id,
                    status=status,
                    notifications=notifications,
                    final_turn=turn,
                )

            deadline = time.time() + (self._config.turn_timeout_ms / 1000.0)
            final_turn: dict[str, Any] | None = None
            while time.time() < deadline:
                remaining = max(0.1, deadline - time.time())
                notification = rpc.next_notification(timeout_seconds=min(1.0, remaining))
                if notification is None:
                    continue
                notifications.append(notification)
                if notification.get("method") == "turn/completed":
                    candidate = notification.get("params", {}).get("turn")
                    if candidate and candidate.get("id") == turn_id:
                        final_turn = candidate
                        status = candidate.get("status", status)
                        break
            else:
                raise AgentRunError("Timed out waiting for turn/completed notification")

            return AgentRunResult(
                thread_id=thread_id,
                turn_id=turn_id,
                status=status,
                notifications=notifications,
                final_turn=final_turn,
            )
        finally:
            rpc.close()


class _JsonRpcProcess:
    def __init__(self, process: subprocess.Popen[str]):
        self._process = process
        self._responses: dict[str, queue.Queue[dict[str, Any]]] = {}
        self._notifications: queue.Queue[dict[str, Any]] = queue.Queue()
        self._counter = itertools.count(1)
        self._closed = threading.Event()
        self._stdout_thread = threading.Thread(target=self._read_stdout, daemon=True)
        self._stderr_thread = threading.Thread(target=self._read_stderr, daemon=True)

    def start(self) -> None:
        self._stdout_thread.start()
        self._stderr_thread.start()

    def close(self) -> None:
        if self._closed.is_set():
            return
        self._closed.set()
        if self._process.poll() is None:
            self._process.terminate()
            try:
                self._process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._process.kill()

    def notify(self, method: str, params: dict[str, Any]) -> None:
        self._send({"jsonrpc": "2.0", "method": method, "params": params})

    def request(self, method: str, params: dict[str, Any], timeout_seconds: float) -> dict[str, Any]:
        request_id = str(next(self._counter))
        response_queue: queue.Queue[dict[str, Any]] = queue.Queue(maxsize=1)
        self._responses[request_id] = response_queue
        self._send({"jsonrpc": "2.0", "id": request_id, "method": method, "params": params})
        try:
            response = response_queue.get(timeout=timeout_seconds)
        except queue.Empty as exc:
            raise AgentRunError(f"Timed out waiting for response to {method}") from exc
        finally:
            self._responses.pop(request_id, None)
        if "error" in response:
            raise AgentRunError(f"{method} failed: {response['error']}")
        return response["result"]

    def next_notification(self, timeout_seconds: float) -> dict[str, Any] | None:
        try:
            return self._notifications.get(timeout=timeout_seconds)
        except queue.Empty:
            if self._process.poll() is not None:
                raise AgentRunError("Codex app-server exited unexpectedly")
            return None

    def _send(self, payload: dict[str, Any]) -> None:
        if self._process.stdin is None:
            raise AgentRunError("Codex app-server stdin is unavailable")
        self._process.stdin.write(json.dumps(payload) + "\n")
        self._process.stdin.flush()

    def _read_stdout(self) -> None:
        if self._process.stdout is None:
            return
        for raw_line in self._process.stdout:
            if self._closed.is_set():
                break
            line = raw_line.strip()
            if not line:
                continue
            try:
                message = json.loads(line)
            except json.JSONDecodeError:
                self._notifications.put({"method": "protocol/raw", "params": {"line": line}})
                continue
            if "id" in message:
                request_id = str(message["id"])
                response_queue = self._responses.get(request_id)
                if response_queue is not None:
                    response_queue.put(message)
                continue
            self._notifications.put(message)

    def _read_stderr(self) -> None:
        if self._process.stderr is None:
            return
        for raw_line in self._process.stderr:
            if self._closed.is_set():
                break
            line = raw_line.rstrip()
            if line:
                self._notifications.put({"method": "process/stderr", "params": {"line": line}})


def _build_turn_sandbox_policy(value: str) -> dict[str, Any]:
    mapping = {
        "danger-full-access": {"type": "dangerFullAccess"},
        "read-only": {"type": "readOnly"},
        "workspace-write": {"type": "workspaceWrite"},
    }
    return mapping.get(value, {"type": "dangerFullAccess"})
