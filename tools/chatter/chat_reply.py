"""Shared handler for live player <-> AI chat replies.

This is called from two places:
- chatter_daemon's process_request when the spool delivers a CHAT_REPLY trigger.
- tools/chatter/chat_test.py CLI harness (in-process; no spool).

Both paths produce the same response_dict shape so downstream rendering
(voiceover_response, sendChat broadcast on game side) works uniformly.

Conversation history is owned by the caller (a ConversationStore lives in
the daemon process; the CLI uses its own short-lived store). This module
just builds the LLM messages list, calls the API, parses the JSON, and
returns the response dict + tone.
"""
from __future__ import annotations

import random
from typing import Optional, Tuple

from tools.chatter.azure_client import (
    ApiError, ApiResult, AuthError, AzureClient,
    parse_chat_reply, post_filter_clean,
)
from tools.chatter.conversations import ConversationStore
from tools.chatter.prompts import build_chat_reply_prompt


# Theatrical fallbacks used when Azure's content filter blocks the prompt
# OR the model refuses outright. Speaker-agnostic and intentionally short
# so the human still sees *something* and the conversation thread doesn't
# break. Tone defaults to "cold" -- a deliberate non-engagement.
CONTENT_FILTER_FALLBACKS = [
    "{speaker} regards {target} in pointed silence.",
    "{speaker} pretends not to have heard {target}.",
    "{speaker} dismisses the remark with a cold half-smile.",
    "{speaker} lets the comment hang in the air, untouched.",
    "{speaker} turns away from {target} and says nothing.",
    "{speaker} considers replying, then thinks better of it.",
]


def _content_filter_fallback(speaker_name: str, target_name: str) -> str:
    """Pick a 'pretends not to hear you' line. Never raises."""
    tmpl = random.choice(CONTENT_FILTER_FALLBACKS)
    try:
        return tmpl.format(
            speaker=speaker_name or "The leader",
            target=target_name or "the rival",
        )
    except Exception:
        return "The leader regards you in pointed silence."


def make_chat_reply_response(*, request: dict, ok: bool, line: str = "", tone: str = "theatrical",
                             error: Optional[str] = None, latency_ms: int = 0,
                             input_tokens: int = 0, output_tokens: int = 0) -> dict:
    """Render the response dict for a CHAT_REPLY request.

    Same envelope shape as the regular response, but the single line dict
    carries an extra `tone` key so the synth side can apply tone-specific
    SSML <prosody> on top of the leader's base voice.
    """
    speaker = request.get("speaker") or {}
    lines = []
    if ok and line:
        lines.append({
            "speaker_player_id": int(speaker.get("player_id", -1)),
            "speaker_name": speaker.get("leader_name", ""),
            "text": line,
            "delay_ms": 0,
            "tone": tone or "theatrical",
        })
    return {
        "schema": 1,
        "request_id": request.get("request_id"),
        "session_id": request.get("session_id"),
        "elector_player_id": request.get("elector_player_id"),
        "ok": ok,
        "lines": lines,
        "error": error,
        "latency_ms": latency_ms,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "trigger": "CHAT_REPLY",
    }


def handle_chat_reply(*, request: dict, store: ConversationStore,
                      client: AzureClient, max_tokens: int = 120,
                      logger=None) -> Tuple[dict, str, str]:
    """Run one CHAT_REPLY round-trip.

    Reads the latest user message from request['context']['user_message'],
    appends it to the conversation history, calls the LLM, parses
    {line, tone}, appends the assistant message to history, and returns
    (response_dict, line, tone).

    On any failure returns a response with ok=False and a short error code.
    Never raises.
    """
    speaker = request.get("speaker") or {}
    target = request.get("target") or {}
    ctx = request.get("context") or {}
    user_message = (ctx.get("user_message") or "").strip()
    session_id = request.get("session_id") or ""
    leader_id = int(speaker.get("player_id", -1))
    key = (session_id, leader_id)

    # MP: chrome carries the typer's player name. SP fallback is the
    # target.human_name we already had. Empty is fine -- store will just
    # render messages without a [name] prefix.
    from_human = (ctx.get("from_human") or "").strip()
    if not from_human:
        from_human = (target.get("human_name") or "").strip()

    if not user_message:
        resp = make_chat_reply_response(
            request=request, ok=False, error="empty_user_message",
        )
        return resp, "", "theatrical"

    # Append the user's latest line BEFORE calling the LLM. If the LLM call
    # fails we still want this message in history (so a retry sees it).
    store.append_user(
        key, user_message,
        leader_name=speaker.get("leader_name", ""),
        from_human=from_human,
    )
    history = store.get_messages(key)
    humans_heard = store.humans_heard(key)
    others = [n for n in humans_heard if n and n != from_human]

    # Build (system_msg, history_messages_for_llm) and call the model.
    system_msg, msgs = build_chat_reply_prompt(
        request, history,
        latest_typer_name=from_human,
        other_humans_in_thread=others,
    )
    full = [{"role": "system", "content": system_msg}] + msgs

    try:
        api: ApiResult = client.call_chat(full, max_tokens=max_tokens)
    except AuthError as exc:
        if logger:
            logger.error("chat_reply: auth failure: %s", exc)
        resp = make_chat_reply_response(request=request, ok=False, error="auth_failure")
        return resp, "", "theatrical"
    except ApiError as exc:
        msg_low = str(exc).lower()
        is_content_filter = (
            "content_filter" in msg_low
            or "responsibleaipolicy" in msg_low
            or "content management policy" in msg_low
        )
        if is_content_filter:
            if logger:
                logger.info(
                    "chat_reply: content filter blocked prompt — substituting "
                    "non-engagement fallback line"
                )
            fb = _content_filter_fallback(
                speaker_name=speaker.get("leader_name", ""),
                target_name=target.get("human_name", "") or target.get("leader_name", ""),
            )
            store.append_assistant(key, fb)
            resp = make_chat_reply_response(
                request=request, ok=True, line=fb, tone="cold",
            )
            return resp, fb, "cold"
        if logger:
            logger.warning("chat_reply: api failure: %s", exc)
        resp = make_chat_reply_response(request=request, ok=False, error="api_failure")
        return resp, "", "theatrical"
    except Exception as exc:  # noqa: BLE001
        if logger:
            logger.exception("chat_reply: unexpected: %s", exc)
        resp = make_chat_reply_response(request=request, ok=False, error="unexpected")
        return resp, "", "theatrical"

    parsed = parse_chat_reply(api.text)
    line = parsed.get("line", "").strip()
    tone = parsed.get("tone", "theatrical")

    cleaned = post_filter_clean(line) if line else None
    if not cleaned:
        if logger:
            logger.info("chat_reply: empty/filtered line, raw=%r", api.text[:200])
        resp = make_chat_reply_response(
            request=request, ok=False, error="empty_reply",
            latency_ms=api.latency_ms,
            input_tokens=api.input_tokens, output_tokens=api.output_tokens,
        )
        return resp, "", "theatrical"

    # Persist the assistant message in history for the next turn.
    store.append_assistant(key, cleaned)

    resp = make_chat_reply_response(
        request=request, ok=True, line=cleaned, tone=tone,
        latency_ms=api.latency_ms,
        input_tokens=api.input_tokens, output_tokens=api.output_tokens,
    )
    return resp, cleaned, tone
