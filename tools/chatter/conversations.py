"""In-memory store for shared chat-room history (one room per game session).

Replaces the older per-leader ConversationStore. Every chat -- whether typed
by a human player or spoken by an AI leader (regular reply OR chain reply)
-- goes into ONE transcript per game session. From any leader's POV the
room is a chat channel: that leader sees the full transcript, with each
turn that isn't their own attributed by speaker name.

Bounds:
  * Rolling window: when a room has more than `max_turns` turns, the
    oldest ones drop off the front. Conversation keeps going.
  * Idle GC: when a room hasn't seen activity for `history_seconds`,
    it's wiped entirely on the next access. The next chat starts fresh.

The store keys by `session_id` only. There is no per-leader thread
anymore; if two leaders are in the same session, they are in the same
room.

Thread-safety: the daemon is single-threaded today, so this is a plain
dict. If the daemon ever goes multi-threaded, wrap operations in a Lock.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class RoomTurn:
    """One message in a shared-room transcript.

    speaker_type narrows the source:
      'human'   -- a real connected human typed it; speaker_name is the
                   typer's display name from chrome.
      'leader'  -- an AI leader spoke (regular reply OR chime/chain
                   reply). speaker_name is the leader's display name;
                   speaker_player_id is their pid.

    Stored fields are speaker-centric, not POV-centric. A single turn is
    "X said Y at time T". When rendering for one leader's prompt we
    decide per-turn whether it's 'assistant' (the speaker IS the leader
    being prompted) or 'user' (everybody else, prefixed with the
    speaker's name).
    """
    speaker_type: str           # 'human' | 'leader'
    speaker_name: str           # display name (may be empty)
    speaker_player_id: int      # pid of the speaker (-1 if unknown)
    content: str
    ts: float = field(default_factory=time.time)


@dataclass
class Room:
    """Every turn spoken in one game-session room."""
    session_id: str
    turns: List[RoomTurn] = field(default_factory=list)
    last_activity_at: float = field(default_factory=time.time)


class RoomStore:
    """In-memory bounded room store.

    `history_seconds`: idle GC window. After this many seconds with no
    activity in a room, the room is dropped wholesale on next access.
    `max_turns`: rolling window bound. When exceeded, oldest turns drop
    off the front; conversation keeps going.

    For backward compatibility this class is also exported as
    `ConversationStore` (alias at the bottom of the module). Callers
    upgrading to the room API should use `RoomStore` directly.
    """

    def __init__(self, *, history_seconds: float = 300.0, max_turns: int = 24):
        self._rooms: Dict[str, Room] = {}
        self.history_seconds = float(history_seconds)
        self.max_turns = int(max_turns)

    # ----- public API -----

    def append_human(self, session_id: str, content: str, *,
                     speaker_name: str = "",
                     speaker_player_id: int = -1) -> Room:
        """Append a human-typed message. Creates the room if missing."""
        room = self._get_or_create(session_id)
        room.turns.append(RoomTurn(
            speaker_type="human",
            speaker_name=speaker_name or "",
            speaker_player_id=int(speaker_player_id),
            content=content,
        ))
        room.last_activity_at = time.time()
        self._trim(room)
        return room

    def append_leader(self, session_id: str, content: str, *,
                      speaker_name: str = "",
                      speaker_player_id: int = -1) -> Room:
        """Append an AI-leader-spoken message. Creates the room if missing."""
        room = self._get_or_create(session_id)
        room.turns.append(RoomTurn(
            speaker_type="leader",
            speaker_name=speaker_name or "",
            speaker_player_id=int(speaker_player_id),
            content=content,
        ))
        room.last_activity_at = time.time()
        self._trim(room)
        return room

    def get(self, session_id: str) -> Optional[Room]:
        """Return the room if it exists and isn't expired, else None.

        Triggers idle GC on every access; an expired room returns None
        AND is removed.
        """
        self._gc_idle()
        return self._rooms.get(session_id)

    def get_messages_for(self, session_id: str, *,
                         leader_player_id: int) -> List[dict]:
        """Render the room transcript as messages for one leader's prompt.

        From `leader_player_id`'s POV:
        - their own past lines render as role='assistant'.
        - every other turn (humans + other AI leaders) renders as
          role='user', prefixed with `[<speaker_name>]` (human) or
          `[<speaker_name> said]` (other leader). This lets the LLM
          tell speakers apart even when several humans / leaders share
          the room.
        """
        room = self.get(session_id)
        if room is None:
            return []
        out: List[dict] = []
        for t in room.turns:
            if (t.speaker_type == "leader"
                    and int(t.speaker_player_id) == int(leader_player_id)):
                out.append({"role": "assistant", "content": t.content})
                continue
            name = t.speaker_name or (
                "leader" if t.speaker_type == "leader" else "human"
            )
            if t.speaker_type == "leader":
                prefix = "[" + name + " said] "
            else:
                prefix = "[" + name + "] "
            out.append({"role": "user", "content": prefix + t.content})
        return out

    def humans_heard(self, session_id: str) -> List[str]:
        """Return distinct human typer names in first-seen order."""
        room = self.get(session_id)
        if room is None:
            return []
        seen: List[str] = []
        for t in room.turns:
            if (t.speaker_type == "human" and t.speaker_name
                    and t.speaker_name not in seen):
                seen.append(t.speaker_name)
        return seen

    def leaders_heard(self, session_id: str) -> List[int]:
        """Return distinct leader pids that have spoken, first-seen order."""
        room = self.get(session_id)
        if room is None:
            return []
        seen: List[int] = []
        for t in room.turns:
            if t.speaker_type == "leader":
                pid = int(t.speaker_player_id)
                if pid >= 0 and pid not in seen:
                    seen.append(pid)
        return seen

    def clear(self, session_id: str) -> bool:
        """Remove one room. Returns True if it existed."""
        return self._rooms.pop(session_id, None) is not None

    def clear_session(self, session_id: str) -> int:
        """Remove one room. Returns 1 if removed, 0 if not present.

        Kept for back-compat with the older multi-conversation API where
        a "session" could contain many conversations and this returned
        the count removed. With one room per session, the count is at
        most 1.
        """
        return 1 if self.clear(session_id) else 0

    def clear_all(self) -> int:
        n = len(self._rooms)
        self._rooms.clear()
        return n

    def __len__(self) -> int:
        return len(self._rooms)

    # ----- internal -----

    def _get_or_create(self, session_id: str) -> Room:
        self._gc_idle()
        room = self._rooms.get(session_id)
        if room is None:
            room = Room(session_id=session_id or "")
            self._rooms[session_id] = room
        return room

    def _gc_idle(self) -> None:
        """Drop rooms that haven't seen activity for history_seconds."""
        if self.history_seconds <= 0:
            return
        now = time.time()
        cutoff = now - self.history_seconds
        stale = [k for k, r in self._rooms.items() if r.last_activity_at < cutoff]
        for k in stale:
            del self._rooms[k]

    def _trim(self, room: Room) -> None:
        """Bound a room's history. Keep most-recent turns; drop from front."""
        if self.max_turns <= 0:
            return
        excess = len(room.turns) - self.max_turns
        if excess > 0:
            del room.turns[:excess]


# Back-compat alias. Existing callers that import `ConversationStore`
# get the new RoomStore (the old per-leader semantics no longer apply).
# Both names are public and supported.
ConversationStore = RoomStore
