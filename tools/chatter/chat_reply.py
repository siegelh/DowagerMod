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


# How many of the prior thread's most recent turns to include in the
# pivot recap. Each turn is one short bullet line.
PIVOT_RECAP_TURNS = 4


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


def _summarize_prior_thread(store: ConversationStore, prior_key,
                            *, max_turns: int = PIVOT_RECAP_TURNS) -> tuple[str, str]:
    """Return (prior_leader_name, summary_text) for the pivot context block.

    If the prior conversation doesn't exist or is empty, returns ("", "").
    The summary is a short multi-line string with the most recent N turns
    rendered as `<speaker>: <content>` -- speaker is either the typer name
    (for human turns) or "<leader>" (for assistant turns).
    """
    prior = store.get(prior_key)
    if prior is None or not prior.turns:
        return "", ""
    leader_name = prior.leader_name or ""
    recent = prior.turns[-max_turns:]
    lines = []
    for t in recent:
        content = (t.content or "").strip()
        if not content:
            continue
        # Trim per-line length so a long monologue doesn't blow the cap.
        if len(content) > 140:
            content = content[:140].rstrip() + "..."
        if t.role == "assistant":
            speaker_label = leader_name or "leader"
        elif t.speaker_type == "leader" and t.speaker_name:
            speaker_label = t.speaker_name
        elif t.from_human:
            speaker_label = t.from_human
        else:
            speaker_label = "human"
        lines.append("- " + speaker_label + ': "' + content + '"')
    summary = "\n".join(lines)
    return leader_name, summary


def make_chat_reply_response(*, request: dict, ok: bool, line: str = "", tone: str = "theatrical",
                             address_to: str = "",
                             error: Optional[str] = None, latency_ms: int = 0,
                             input_tokens: int = 0, output_tokens: int = 0) -> dict:
    """Render the response dict for a CHAT_REPLY request.

    Same envelope shape as the regular response, but the single line dict
    carries an extra `tone` key so the synth side can apply tone-specific
    SSML <prosody> on top of the leader's base voice. `address_to`, when
    non-empty, names another AI leader the line is calling out (used by
    the game-side chain-reply hook).
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
            "address_to": address_to or "",
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
    {line, tone, address_to}, appends the assistant message to history,
    and returns (response_dict, line, tone).

    Chain-reply mode: when ctx['chain_reply'] == '1', the user_message is
    treated as a line spoken by another AI leader (named in
    ctx['prior_leader_speaker_name']) rather than by a human. The history
    turn is appended via append_leader_speaker so it renders with the
    "[<leader> said] ..." prefix, and a chain-flavored system prompt is
    used.

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

    # Chain-reply context: prior AI leader spoke to us; humans are watching.
    chain_reply = (ctx.get("chain_reply") or "").strip() == "1"
    prior_leader_speaker_name = (ctx.get("prior_leader_speaker_name") or "").strip()

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

    # Append the latest line BEFORE calling the LLM. Chain replies append
    # as a "leader" speaker_type turn so the renderer prefixes it with
    # [<leader> said] and the LLM doesn't mistake it for a human message.
    if chain_reply:
        store.append_leader_speaker(
            key, user_message,
            leader_name=speaker.get("leader_name", ""),
            prior_speaker_name=prior_leader_speaker_name,
        )
    else:
        store.append_user(
            key, user_message,
            leader_name=speaker.get("leader_name", ""),
            from_human=from_human,
        )
    history = store.get_messages(key)
    humans_heard = store.humans_heard(key)
    others = [n for n in humans_heard if n and n != from_human]

    # MP pivot: the human just turned from another AI leader to us.
    # Look up the prior thread (same session, prior leader id) and
    # build a short recap so we can address the pivot in character.
    # Pivot context is suppressed for chain replies (they have their own framing).
    prior_leader_name = ""
    prior_thread_summary = ""
    if not chain_reply:
        prior_id_raw = ctx.get("prior_thread_with_leader_id")
        if prior_id_raw not in (None, "", -1):
            try:
                prior_id = int(prior_id_raw)
            except (TypeError, ValueError):
                prior_id = -1
            if prior_id >= 0 and prior_id != leader_id:
                prior_leader_name, prior_thread_summary = _summarize_prior_thread(
                    store, (session_id, prior_id),
                )
                if logger and prior_thread_summary:
                    logger.info(
                        "chat_reply: pivot detected -- prior_leader=%s summary_chars=%d",
                        prior_leader_name, len(prior_thread_summary),
                    )

    # Build (system_msg, history_messages_for_llm) and call the model.
    system_msg, msgs = build_chat_reply_prompt(
        request, history,
        latest_typer_name=from_human,
        other_humans_in_thread=others,
        prior_leader_name=prior_leader_name,
        prior_thread_summary=prior_thread_summary,
        chain_reply=chain_reply,
        prior_leader_speaker_name=prior_leader_speaker_name,
    )
    full = [{"role": "system", "content": system_msg}] + msgs

    if logger and chain_reply:
        logger.info(
            "chat_reply: chain reply -- speaker=%s prior=%s",
            speaker.get("leader_name", ""), prior_leader_speaker_name,
        )

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
    address_to = parsed.get("address_to", "").strip()

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
        address_to=address_to,
        latency_ms=api.latency_ms,
        input_tokens=api.input_tokens, output_tokens=api.output_tokens,
    )
    return resp, cleaned, tone
