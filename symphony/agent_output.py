from __future__ import annotations

import json
import re
from typing import Any


class AgentOutputError(RuntimeError):
    """Raised when Symphony cannot parse role output from an agent turn."""


def extract_json_object(text: str) -> dict[str, Any]:
    candidate = text.strip()
    if candidate.startswith("```"):
        match = re.search(r"```(?:json)?\s*(\{.*\})\s*```", candidate, flags=re.DOTALL)
        if match:
            candidate = match.group(1).strip()
    else:
        match = re.search(r"(\{.*\})", candidate, flags=re.DOTALL)
        if match:
            candidate = match.group(1).strip()

    try:
        parsed = json.loads(candidate)
    except json.JSONDecodeError as exc:
        raise AgentOutputError("Agent response was not valid JSON.") from exc
    if not isinstance(parsed, dict):
        raise AgentOutputError("Agent JSON response must be an object.")
    return parsed
