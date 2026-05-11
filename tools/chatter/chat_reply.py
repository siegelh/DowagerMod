"""Shared handler for live player <-> AI chat replies.

This is called from two places:
- chatter_daemon's process_request when the spool delivers a CHAT_REPLY trigger.
- tools/chatter/chat_test.py CLI harness (in-process; no spool).

Both paths produce the same response_dict shape so downstream rendering
(voiceover_response, sendChat broadcast on game side) works uniformly.

Conversation history is owned by the caller (a RoomStore lives in the
daemon process; the CLI uses its own short-lived store). This module
just builds the LLM messages list, calls the API, parses the JSON, and
returns the response dict + tone.

Shared-room semantics: every CHAT_REPLY (human-typed or chain) reads from
and writes to ONE room per session. There is no "pivot" anymore -- when
a human turns from one leader to another the new leader already sees the
prior exchange in the shared transcript. Chain replies (one AI leader
replying to another) do NOT append the prior leader's line; that line
was already added to the room when the prior leader spoke.
"""
from __future__ import annotations

import json
import random
from typing import Optional, Tuple

from tools.chatter.azure_client import (
    ApiError, ApiResult, AuthError, AzureClient,
    parse_chat_reply, post_filter_clean,
)
from tools.chatter.conversations import RoomStore
from tools.chatter.prompts import _format_room_state_block, build_chat_reply_prompt


CONTENT_FILTER_FALLBACKS = [
    "{speaker} regards {target} in pointed silence.",
    "{speaker} pretends not to have heard {target}.",
    "{speaker} dismisses the remark with a cold half-smile.",
    "{speaker} lets the comment hang in the air, untouched.",
    "{speaker} turns away from {target} and says nothing.",
    "{speaker} considers replying, then thinks better of it.",
]


def _parse_room_state(raw: str) -> Optional[dict]:
    """Decode the JSON room_state ctx field. None on missing/bad input."""
    if not raw:
        return None
    try:
        obj = json.loads(raw)
    except (TypeError, ValueError):
        return None
    if not isinstance(obj, dict):
        return None
    return obj


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


def handle_chat_reply(*, request: dict, store: RoomStore,
                      client: AzureClient, max_tokens: int = 120,
                      logger=None) -> Tuple[dict, str, str]:
    """Run one CHAT_REPLY round-trip against the shared room.

    Reads the latest user message from request['context']['user_message'],
    appends it to the room as a human turn (unless this is a chain reply,
    in which case the prior leader's line is already in the room from
    that leader's earlier response), calls the LLM, parses
    {line, tone, address_to}, appends the assistant message as a leader
    turn in the same room, and returns (response_dict, line, tone).

    Chain-reply mode: when ctx['chain_reply'] == '1', this is one AI
    leader replying to another. The user_message field is the prior
    leader's line; it's NOT re-appended (the prior leader already added
    it when their CHAT_REPLY ran). A chain-flavored system prompt is
    used; ctx['prior_leader_speaker_name'] tells the prompt who just
    spoke.

    On any failure returns a response with ok=False and a short error
    code. Never raises.
    """
    speaker = request.get("speaker") or {}
    target = request.get("target") or {}
    ctx = request.get("context") or {}
    user_message = (ctx.get("user_message") or "").strip()
    session_id = request.get("session_id") or ""
    leader_id = int(speaker.get("player_id", -1))
    leader_name = speaker.get("leader_name", "") or ""

    chain_reply = (ctx.get("chain_reply") or "").strip() == "1"
    prior_leader_speaker_name = (ctx.get("prior_leader_speaker_name") or "").strip()

    # MP: chrome carries the typer's player name. SP fallback is the
    # target.human_name we already had. Empty is fine -- the room will
    # render the line without a [name] prefix.
    from_human = (ctx.get("from_human") or "").strip()
    if not from_human:
        from_human = (target.get("human_name") or "").strip()

    if not user_message:
        resp = make_chat_reply_response(
            request=request, ok=False, error="empty_user_message",
        )
        return resp, "", "theatrical"

    # In chain mode the prior leader's line is already in the room (added
    # when that leader's CHAT_REPLY ran). For human-typed chats we add a
    # new human turn here, BEFORE calling the LLM, so the LLM sees the
    # full context including the latest message.
    if not chain_reply:
        human_pid = -1
        try:
            human_pid = int(target.get("player_id", -1))
        except (TypeError, ValueError):
            human_pid = -1
        store.append_human(
            session_id, user_message,
            speaker_name=from_human,
            speaker_player_id=human_pid,
        )

    history = store.get_messages_for(session_id, leader_player_id=leader_id)
    humans_heard = store.humans_heard(session_id)
    others = [n for n in humans_heard if n and n != from_human]

    room_state = _parse_room_state(ctx.get("room_state") or "")

    if logger:
        rs_size = 0
        if room_state:
            rs_size = len(room_state.get("roster") or [])
        logger.info(
            "chat_reply: rid=%s leader=%d (%s) from_human=%r chain=%s"
            " session=%r turns=%d roster=%d",
            request.get("request_id"), leader_id, leader_name, from_human,
            "1" if chain_reply else "0", session_id[:12], len(history), rs_size,
        )
        # ROOM_DEBUG: dump raw JSON + rendered preface so we can audit
        # what the LLM is actually seeing. Grep daemon.log for ROOM_DEBUG.
        if room_state is not None:
            try:
                rs_json = json.dumps(room_state, indent=2, sort_keys=True)
            except (TypeError, ValueError):
                rs_json = repr(room_state)
            logger.info("ROOM_DEBUG raw rid=%s json:\n%s",
                        request.get("request_id"), rs_json)
            try:
                preface = _format_room_state_block(room_state, leader_name)
            except Exception as exc:  # noqa: BLE001
                preface = "<preface render failed: %s>" % (exc,)
            logger.info("ROOM_DEBUG preface rid=%s:\n%s",
                        request.get("request_id"),
                        preface or "<empty preface>")
        else:
            logger.info("ROOM_DEBUG rid=%s: no room_state in ctx",
                        request.get("request_id"))

    system_msg, msgs = build_chat_reply_prompt(
        request, history,
        latest_typer_name=from_human,
        other_humans_in_thread=others,
        chain_reply=chain_reply,
        prior_leader_speaker_name=prior_leader_speaker_name,
        room_state=room_state,
    )
    full = [{"role": "system", "content": system_msg}] + msgs

    if logger and chain_reply:
        logger.info(
            "chat_reply: chain reply -- speaker=%s prior=%s",
            leader_name, prior_leader_speaker_name,
        )

    try:
        api: ApiResult = client.call_chat(full, max_tokens=max_tokens, json_mode=True)
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
                speaker_name=leader_name,
                target_name=target.get("human_name", "") or target.get("leader_name", ""),
            )
            store.append_leader(
                session_id, fb,
                speaker_name=leader_name, speaker_player_id=leader_id,
            )
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

    store.append_leader(
        session_id, cleaned,
        speaker_name=leader_name, speaker_player_id=leader_id,
    )

    resp = make_chat_reply_response(
        request=request, ok=True, line=cleaned, tone=tone,
        address_to=address_to,
        latency_ms=api.latency_ms,
        input_tokens=api.input_tokens, output_tokens=api.output_tokens,
    )
    return resp, cleaned, tone

