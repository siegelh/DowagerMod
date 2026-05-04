"""Thin wrapper around the OpenAI SDK pointed at Azure Foundry.

Hides the SDK detail from the daemon and provides a single `call_responses`
method that returns either text (single-line) or a parsed list of
{speaker, line} dicts (multi-turn).
"""
from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass
from typing import List, Optional


class AuthError(Exception):
    """API key is wrong / expired. Trips circuit immediately."""


class ApiError(Exception):
    """Any other API failure (timeout, 5xx, network)."""


@dataclass
class ApiResult:
    text: str  # raw output_text
    latency_ms: int
    input_tokens: int
    output_tokens: int


class AzureClient:
    def __init__(self, endpoint: str, api_key: str, deployment: str, *, request_timeout_seconds: float = 8.0):
        self.endpoint = endpoint
        self.api_key = api_key
        self.deployment = deployment
        self.request_timeout = request_timeout_seconds
        self._client = None

    def _ensure_client(self):
        if self._client is None:
            from openai import OpenAI  # lazy import — only required at call time
            self._client = OpenAI(
                base_url=self.endpoint,
                api_key=self.api_key,
                timeout=self.request_timeout,
            )
        return self._client

    def call_responses(self, system_msg: str, user_msg: str, *, max_tokens: int = 80) -> ApiResult:
        """Single API call. Raises AuthError on auth failure, ApiError on others."""
        client = self._ensure_client()
        t0 = time.perf_counter()
        try:
            response = client.responses.create(
                model=self.deployment,
                instructions=system_msg,
                input=user_msg,
                max_output_tokens=max_tokens,
            )
        except Exception as exc:  # noqa: BLE001
            elapsed_ms = int((time.perf_counter() - t0) * 1000)
            msg = str(exc)
            # Best-effort auth detection
            low = msg.lower()
            if (
                "401" in msg
                or "403" in msg
                or "invalid api key" in low
                or "authentication" in low
                or "unauthorized" in low
            ):
                raise AuthError(f"auth failure after {elapsed_ms}ms: {msg}") from exc
            raise ApiError(f"api failure after {elapsed_ms}ms: {msg}") from exc

        elapsed_ms = int((time.perf_counter() - t0) * 1000)
        text = (getattr(response, "output_text", "") or "").strip()
        usage = getattr(response, "usage", None)
        ti = getattr(usage, "input_tokens", 0) if usage else 0
        to = getattr(usage, "output_tokens", 0) if usage else 0
        return ApiResult(text=text, latency_ms=elapsed_ms, input_tokens=ti, output_tokens=to)


def parse_multi_turn_lines(raw: str) -> List[dict]:
    """Parse a JSON array of {speaker, line} from the model's output.

    Tolerates code fences, leading/trailing whitespace, and minor format
    quirks. Raises ValueError if it can't be parsed.
    """
    text = raw.strip()
    # Strip common code fences
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```\s*$", "", text)
    # Trim anything before the first '['
    idx = text.find("[")
    if idx > 0:
        text = text[idx:]
    parsed = json.loads(text)
    if not isinstance(parsed, list):
        raise ValueError("multi-turn output is not a JSON array")
    out = []
    for i, item in enumerate(parsed):
        if not isinstance(item, dict):
            raise ValueError(f"item {i} is not an object")
        speaker = str(item.get("speaker", "")).strip()
        line = str(item.get("line", "")).strip()
        if not speaker or not line:
            raise ValueError(f"item {i} missing speaker or line")
        out.append({"speaker": speaker, "line": line})
    if not out:
        raise ValueError("empty exchange")
    return out


def looks_like_refusal(text: str) -> bool:
    """Heuristic detection of safety refusals."""
    if not text:
        return True
    low = text.lower()
    return (
        "i cannot" in low
        or "i can't" in low
        or "i'm sorry" in low
        or "as an ai" in low
        or "i am not able" in low
    )
