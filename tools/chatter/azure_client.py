"""Thin wrapper around the OpenAI SDK pointed at Azure Foundry.

Hides the SDK detail from the daemon and provides a single `call_responses`
method that returns either text (single-line) or a parsed list of
{speaker, line} dicts (multi-turn).
"""
from __future__ import annotations

import json
import random
import re
import time
from dataclasses import dataclass
from typing import List, Optional


# Fallback canned lines for when the model refuses or fails. Speaker-agnostic
# (they fit any leader) and intentionally short. Used by the daemon to
# substitute for refusals so the user sees *something* rather than silence.
FALLBACK_DIRECTED = [
    "{speaker} regards {target} in pointed silence.",
    "{speaker} pauses, then turns away from {target}.",
    "{speaker} offers {target} only a thin, unreadable smile.",
    "{speaker} considers {target} for a long moment without speaking.",
]

FALLBACK_BROADCAST = [
    "{speaker} surveys the world in measured silence.",
    "{speaker} lets the moment speak for itself.",
    "{speaker} accepts the day's news with the calm of an empire.",
]


def fallback_line(speaker_name: str, target_name: str = "", broadcast: bool = False) -> str:
    """Pick a canned fallback line. Never raises."""
    pool = FALLBACK_BROADCAST if broadcast else FALLBACK_DIRECTED
    tmpl = random.choice(pool)
    try:
        return tmpl.format(speaker=speaker_name or "The leader", target=target_name or "the rival")
    except Exception:
        return "The leader is silent."


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
    def __init__(
        self,
        endpoint: str,
        api_key: str,
        deployment: str,
        *,
        request_timeout_seconds: float = 8.0,
        api_version: str = "",
    ):
        self.endpoint = endpoint
        self.api_key = api_key
        self.deployment = deployment
        self.request_timeout = request_timeout_seconds
        # Auto-detect mode by URL shape.
        # OpenAI mode: Foundry "/openai/v1" base URLs (compat with the OpenAI SDK).
        # AzureOpenAI mode: classic Cognitive Services / Azure OpenAI hostnames
        # (no /openai/v1 suffix; require explicit api_version).
        ep_low = (endpoint or "").lower().rstrip("/")
        self._mode = "azure" if (
            "cognitiveservices.azure.com" in ep_low
            or "openai.azure.com" in ep_low
        ) and not ep_low.endswith("/openai/v1") else "openai"
        # Default api_version for AzureOpenAI mode if caller didn't supply one.
        self.api_version = api_version or "2024-12-01-preview"
        self._client = None

    def _ensure_client(self):
        if self._client is None:
            if self._mode == "azure":
                from openai import AzureOpenAI  # lazy import
                # AzureOpenAI infers the /openai/deployments/<deployment>/chat/completions
                # path from azure_endpoint + api_version + model (== deployment name).
                self._client = AzureOpenAI(
                    azure_endpoint=self.endpoint,
                    api_key=self.api_key,
                    api_version=self.api_version,
                    timeout=self.request_timeout,
                )
            else:
                from openai import OpenAI
                self._client = OpenAI(
                    base_url=self.endpoint,
                    api_key=self.api_key,
                    timeout=self.request_timeout,
                )
        return self._client

    def call_responses(self, system_msg: str, user_msg: str, *, max_tokens: int = 80) -> ApiResult:
        """Single API call. Raises AuthError on auth failure, ApiError on others.

        Auto-routes to either the OpenAI Responses API (for /openai/v1 endpoints)
        or the Chat Completions API (for AzureOpenAI / cognitiveservices endpoints).
        Both return the same ApiResult shape so callers don't care.
        """
        return self.call_chat(
            [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg},
            ],
            max_tokens=max_tokens,
        )

    def call_chat(self, messages: list, *, max_tokens: int = 80) -> ApiResult:
        """Multi-turn API call. messages is a list of {role, content} dicts.

        The first message MUST be role='system'; the rest alternate user/assistant.
        Auto-routes to AzureOpenAI chat.completions or OpenAI Responses API.
        """
        if not messages:
            raise ApiError("call_chat: messages list is empty")
        # Pull the system message out (first occurrence; ignore any later ones).
        system_msg = ""
        rest: list = []
        for i, m in enumerate(messages):
            role = (m.get("role") or "").lower()
            content = m.get("content") or ""
            if role == "system" and not system_msg:
                system_msg = content
            else:
                rest.append({"role": role, "content": content})

        client = self._ensure_client()
        t0 = time.perf_counter()
        try:
            if self._mode == "azure":
                # AzureOpenAI: full messages list including system.
                full = ([{"role": "system", "content": system_msg}] if system_msg else []) + rest
                kwargs = {"model": self.deployment, "messages": full}
                try:
                    response = client.chat.completions.create(
                        max_completion_tokens=max_tokens, **kwargs
                    )
                except TypeError:
                    response = client.chat.completions.create(
                        max_tokens=max_tokens, **kwargs
                    )
            else:
                # Responses API: instructions + input list of role/content items.
                response = client.responses.create(
                    model=self.deployment,
                    instructions=system_msg,
                    input=rest if rest else "",
                    max_output_tokens=max_tokens,
                )
        except Exception as exc:  # noqa: BLE001
            elapsed_ms = int((time.perf_counter() - t0) * 1000)
            msg = str(exc)
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
        if self._mode == "azure":
            try:
                text = (response.choices[0].message.content or "").strip()
            except Exception:
                text = ""
            usage = getattr(response, "usage", None)
            ti = getattr(usage, "prompt_tokens", 0) if usage else 0
            to = getattr(usage, "completion_tokens", 0) if usage else 0
        else:
            text = (getattr(response, "output_text", "") or "").strip()
            usage = getattr(response, "usage", None)
            ti = getattr(usage, "input_tokens", 0) if usage else 0
            to = getattr(usage, "output_tokens", 0) if usage else 0
        return ApiResult(text=text, latency_ms=elapsed_ms, input_tokens=ti, output_tokens=to)


def parse_multi_turn_lines(raw: str) -> List[dict]:
    """Parse a JSON array of {speaker, line[, line_native]} from the model's output.

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
        entry = {"speaker": speaker, "line": line}
        # Optional native-tongue translation
        line_native = str(item.get("line_native", "")).strip()
        if line_native:
            entry["line_native"] = line_native
        out.append(entry)
    if not out:
        raise ValueError("empty exchange")
    return out


def parse_single_line_native(raw: str) -> dict:
    """Parse a JSON object {line, line_native} from the single-line native call.
    Returns {'line': str, 'line_native': str}. Falls back to {'line': raw} if parse fails.
    """
    text = raw.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```\s*$", "", text)
    idx = text.find("{")
    if idx > 0:
        text = text[idx:]
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict) and parsed.get("line"):
            out = {"line": str(parsed["line"]).strip()}
            ln = str(parsed.get("line_native", "")).strip()
            if ln:
                out["line_native"] = ln
            return out
    except Exception:  # noqa: BLE001
        pass
    return {"line": text}


# Tones the LLM is allowed to emit in CHAT_REPLY mode. Anything else is
# coerced to "theatrical" (the safe neutral default) -- mirrors tone.py.
_VALID_CHAT_TONES = {
    "angry", "amused", "haughty", "pleased", "cold", "menacing", "wistful", "theatrical",
}


def parse_chat_reply(raw: str) -> dict:
    """Parse a CHAT_REPLY JSON object {line, tone, address_to?}.

    Returns {'line': str, 'tone': str, 'address_to': str}. Tone is
    normalized to lowercase and coerced to 'theatrical' if not in the
    allowed set. address_to is optional in the LLM output -- when set it
    names another AI leader the line is calling out (used for chain
    replies). Empty string when missing or not a string. Falls back to
    {'line': raw, 'tone': 'theatrical', 'address_to': ''} if JSON parse
    fails so the caller still gets something speakable.
    """
    text = (raw or "").strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```\s*$", "", text)
    idx = text.find("{")
    if idx > 0:
        text = text[idx:]
    try:
        parsed = json.loads(text)
    except Exception:  # noqa: BLE001
        return {"line": (raw or "").strip(), "tone": "theatrical", "address_to": ""}
    if not isinstance(parsed, dict):
        return {"line": (raw or "").strip(), "tone": "theatrical", "address_to": ""}
    line = str(parsed.get("line", "")).strip()
    tone = str(parsed.get("tone", "")).strip().lower()
    if tone not in _VALID_CHAT_TONES:
        tone = "theatrical"
    addr_raw = parsed.get("address_to")
    if isinstance(addr_raw, str):
        address_to = addr_raw.strip()
    else:
        address_to = ""
    if not line:
        return {"line": (raw or "").strip(), "tone": tone, "address_to": address_to}
    return {"line": line, "tone": tone, "address_to": address_to}



# Simple post-render denylist. Triggered after the model returns text but
# before we hand back to the caller. Keeps a tiny safety net for known-bad
# substrings the model might slip past its own filters. Case-insensitive.
DENY_SUBSTRINGS = (
    # Empty for v1 — extend per-incident if real refusals leak ugly content.
)


def post_filter_clean(text: str) -> Optional[str]:
    """Return None if the text trips the denylist. Else return text trimmed."""
    if not text:
        return None
    low = text.lower()
    for bad in DENY_SUBSTRINGS:
        if bad in low:
            return None
    return text.strip()


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

