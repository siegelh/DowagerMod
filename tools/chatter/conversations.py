"""In-memory store for player <-> AI multi-turn chat conversations.

Each conversation is keyed by (session_id, leader_player_id) -- one
independent thread per AI leader you're talking to. Histories are bounded
in length and expire after a configurable idle window so a daemon restart
or 10 minutes of silence cleans them up automatically.

Turns can come from multiple speakers in MP: any connected human (typer
name carried via `from_human`) or, in chain replies, another AI leader
(prior leader name carried via `speaker_name` with speaker_type='leader').
The render-side prefixes user content with `[<name>]` so the LLM can
distinguish who said what within a single conversation thread.

Thread-safety: the daemon is single-threaded today, so this is a plain
dict. If the daemon ever goes multi-threaded, wrap operations in a Lock.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class ConversationTurn:
    """One message in a conversation history.

    role is 'user' or 'assistant' (from the current leader's POV).
    speaker_type narrows the source for 'user' turns:
      'human'      -- a real connected human typed it; from_human is set.
      'leader'     -- a chain-reply where another AI leader is speaking
                      to the current leader; speaker_name is set.
      ''           -- legacy / unspecified (treated as human-typed).

    For 'assistant' turns speaker_type is unused (always the current leader).
    """
    role: str
    content: str
    ts: float = field(default_factory=time.time)
    from_human: str = ""      # set when speaker_type == 'human'
    speaker_type: str = ""    # 'human' | 'leader' | ''
    speaker_name: str = ""    # set when speaker_type == 'leader' (prior leader's name)


@dataclass
class Conversation:
    leader_id: int
    leader_name: str
    turns: List[ConversationTurn] = field(default_factory=list)
    last_activity_at: float = field(default_factory=time.time)

    def to_messages(self) -> List[dict]:
        """Render turns as OpenAI-style messages list (no system prompt).

        User turns are prefixed with `[<name>]` so the LLM sees who is
        talking when the same thread has multiple humans (or a chain
        reply from another leader). Assistant turns pass through.
        """
        out = []
        for t in self.turns:
            content = t.content
            if t.role == "user":
                if t.speaker_type == "leader" and t.speaker_name:
                    content = "[" + t.speaker_name + " said] " + content
                elif t.from_human:
                    content = "[" + t.from_human + "] " + content
            out.append({"role": t.role, "content": content})
        return out

    def humans_heard(self) -> List[str]:
        """Return distinct typer names seen in this thread, in first-seen order."""
        seen = []
        for t in self.turns:
            name = t.from_human
            if name and name not in seen:
                seen.append(name)
        return seen


# Conversation key: (session_id, leader_player_id)
ConvKey = Tuple[str, int]


class ConversationStore:
    """In-memory bounded conversation store.

    `idle_seconds` is the active-partner expiry window (game-side concern;
    we accept it here for consistent gc semantics). `history_seconds` is
    when the full history is GC'd. Both are checked on every access.
    `max_turns` bounds memory per conversation -- when exceeded the oldest
    turns are dropped from the front (we always keep the most recent
    user/assistant pairs intact).
    """

    def __init__(self, *, history_seconds: float = 600.0, max_turns: int = 24):
        self._convs: Dict[ConvKey, Conversation] = {}
        self.history_seconds = float(history_seconds)
        self.max_turns = int(max_turns)

    # ----- public API -----

    def append_user(self, key: ConvKey, content: str, *,
                    leader_name: str = "",
                    from_human: str = "") -> Conversation:
        """Append a user (human) message. Creates the conversation if missing.

        from_human is the typer's player name (Civ4 chat chrome). When set,
        the rendered history prefixes the line with `[<name>]` so the LLM
        knows which human spoke -- relevant in MP and harmless in SP.
        """
        self._gc_idle()
        conv = self._convs.get(key)
        if conv is None:
            conv = Conversation(leader_id=key[1], leader_name=leader_name or "")
            self._convs[key] = conv
        elif leader_name and not conv.leader_name:
            conv.leader_name = leader_name
        conv.turns.append(ConversationTurn(
            role="user",
            content=content,
            from_human=from_human or "",
            speaker_type="human" if from_human else "",
        ))
        conv.last_activity_at = time.time()
        self._trim(conv)
        return conv

    def append_leader_speaker(self, key: ConvKey, content: str, *,
                              leader_name: str = "",
                              prior_speaker_name: str = "") -> Conversation:
        """Append a chain-reply turn from another AI leader.

        Used when another leader has just spoken to/about the current
        leader and we're queueing the current leader's reply. From the
        current leader's POV this is still a 'user' role message (it's
        what they're being asked to respond to), but speaker_type is
        'leader' so rendering can prefix `[<prior leader> said] ...`.
        """
        self._gc_idle()
        conv = self._convs.get(key)
        if conv is None:
            conv = Conversation(leader_id=key[1], leader_name=leader_name or "")
            self._convs[key] = conv
        elif leader_name and not conv.leader_name:
            conv.leader_name = leader_name
        conv.turns.append(ConversationTurn(
            role="user",
            content=content,
            speaker_type="leader",
            speaker_name=prior_speaker_name or "",
        ))
        conv.last_activity_at = time.time()
        self._trim(conv)
        return conv

    def append_assistant(self, key: ConvKey, content: str) -> Conversation:
        """Append an assistant (AI leader) message. Conversation must exist."""
        self._gc_idle()
        conv = self._convs.get(key)
        if conv is None:
            # Defensive: shouldn't happen in normal flow but never crash.
            conv = Conversation(leader_id=key[1], leader_name="")
            self._convs[key] = conv
        conv.turns.append(ConversationTurn(role="assistant", content=content))
        conv.last_activity_at = time.time()
        self._trim(conv)
        return conv

    def get(self, key: ConvKey) -> Conversation | None:
        """Return the conversation if it exists and isn't expired, else None."""
        self._gc_idle()
        return self._convs.get(key)

    def get_messages(self, key: ConvKey) -> List[dict]:
        """Return the messages list for a conversation, or [] if missing."""
        conv = self.get(key)
        return conv.to_messages() if conv else []

    def humans_heard(self, key: ConvKey) -> List[str]:
        """Return distinct typer names seen in this thread, first-seen order."""
        conv = self.get(key)
        return conv.humans_heard() if conv else []

    def clear(self, key: ConvKey) -> bool:
        """Remove one conversation. Returns True if it existed."""
        return self._convs.pop(key, None) is not None

    def clear_session(self, session_id: str) -> int:
        """Remove every conversation in a session. Returns count removed."""
        keys = [k for k in self._convs if k[0] == session_id]
        for k in keys:
            del self._convs[k]
        return len(keys)

    def clear_all(self) -> int:
        n = len(self._convs)
        self._convs.clear()
        return n

    def __len__(self) -> int:
        return len(self._convs)

    # ----- internal -----

    def _gc_idle(self) -> None:
        """Drop conversations that haven't seen activity for history_seconds."""
        if self.history_seconds <= 0:
            return
        now = time.time()
        cutoff = now - self.history_seconds
        stale = [k for k, c in self._convs.items() if c.last_activity_at < cutoff]
        for k in stale:
            del self._convs[k]

    def _trim(self, conv: Conversation) -> None:
        """Bound a conversation's history. Keep most-recent turns; drop from front."""
        if self.max_turns <= 0:
            return
        excess = len(conv.turns) - self.max_turns
        if excess > 0:
            del conv.turns[:excess]

