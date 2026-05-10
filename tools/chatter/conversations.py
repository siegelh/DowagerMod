"""In-memory store for player <-> AI multi-turn chat conversations.

Each conversation is keyed by (session_id, leader_player_id) -- one
independent thread per AI leader you're talking to. Histories are bounded
in length and expire after a configurable idle window so a daemon restart
or 10 minutes of silence cleans them up automatically.

Thread-safety: the daemon is single-threaded today, so this is a plain
dict. If the daemon ever goes multi-threaded, wrap operations in a Lock.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class ConversationTurn:
    """One message in a conversation history. role is 'user' or 'assistant'."""
    role: str
    content: str
    ts: float = field(default_factory=time.time)


@dataclass
class Conversation:
    leader_id: int
    leader_name: str
    turns: List[ConversationTurn] = field(default_factory=list)
    last_activity_at: float = field(default_factory=time.time)

    def to_messages(self) -> List[dict]:
        """Render turns as OpenAI-style messages list (no system prompt)."""
        return [{"role": t.role, "content": t.content} for t in self.turns]


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

    def append_user(self, key: ConvKey, content: str, *, leader_name: str = "") -> Conversation:
        """Append a user (human) message. Creates the conversation if missing."""
        self._gc_idle()
        conv = self._convs.get(key)
        if conv is None:
            conv = Conversation(leader_id=key[1], leader_name=leader_name or "")
            self._convs[key] = conv
        elif leader_name and not conv.leader_name:
            conv.leader_name = leader_name
        conv.turns.append(ConversationTurn(role="user", content=content))
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
