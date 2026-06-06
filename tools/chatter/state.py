"""Per-pair conversation state for the chatter sidecar.

Currently in-memory only; lost on daemon restart. v1.1 may persist to disk.
Keys are (session_id, ordered_pair) tuples.

Also hosts a per-leader recent-lines ring buffer (`RecentLines`) used to
feed the prompt builder a short list of each leader's most recent broadcast
/ directed / multi-turn lines so the LLM can avoid echoing its own wording
and structure across triggers. This addresses a real complaint from play
sessions where every leader kept reaching for the same handful of poetic
words ("crumbling", "ashes", etc.) because each commentary call was
amnesiac.
"""
from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass, field
from typing import Deque, Dict, List, Optional, Tuple


PairKey = Tuple[str, int, int]  # (session_id, speaker_id, target_id)
LeaderKey = Tuple[str, int]  # (session_id, player_id)


# How many recent lines to keep per leader per session. Six is enough to
# discourage repetition within a typical 10-15 turn window without bloating
# the prompt -- each line is ~14 words so the rendered block is small.
RECENT_LINES_PER_LEADER = 6


@dataclass
class PairState:
    last_event_unix: float = 0.0
    exchanges_done: int = 0
    last_response_id: Optional[str] = None  # for future Responses API threading


class StateStore:
    def __init__(self):
        self._pairs: Dict[PairKey, PairState] = {}
        # Per-leader ring buffer of recent spoken lines (newest at the right).
        # Keyed by (session_id, player_id). Used by the prompt builder to ask
        # the LLM to avoid echoing the leader's own previous wording.
        self._recent: Dict[LeaderKey, Deque[str]] = {}

    def key(self, session_id: str, a: int, b: int) -> PairKey:
        return (session_id or "", int(a), int(b))

    def touch(self, session_id: str, a: int, b: int) -> PairState:
        k = self.key(session_id, a, b)
        st = self._pairs.get(k)
        if st is None:
            st = PairState()
            self._pairs[k] = st
        st.last_event_unix = time.time()
        st.exchanges_done += 1
        return st

    def get(self, session_id: str, a: int, b: int) -> Optional[PairState]:
        return self._pairs.get(self.key(session_id, a, b))

    # ----- per-leader recent-lines ring buffer -----

    def _leader_key(self, session_id: str, player_id: int) -> LeaderKey:
        return (session_id or "", int(player_id))

    def record_line(self, session_id: str, player_id: int, text: str) -> None:
        """Append a spoken line to the leader's recent-lines ring buffer.

        Empty / whitespace-only / non-int player_id values are dropped
        silently -- callers don't need to pre-validate. The buffer is
        bounded to RECENT_LINES_PER_LEADER per (session, player).
        """
        if not text or not text.strip():
            return
        try:
            pid = int(player_id)
        except (TypeError, ValueError):
            return
        if pid < 0:
            return
        k = self._leader_key(session_id, pid)
        buf = self._recent.get(k)
        if buf is None:
            buf = deque(maxlen=RECENT_LINES_PER_LEADER)
            self._recent[k] = buf
        buf.append(text.strip())

    def recent_lines(self, session_id: str, player_id: int) -> List[str]:
        """Return the leader's recent lines, oldest first. Empty list if none."""
        try:
            pid = int(player_id)
        except (TypeError, ValueError):
            return []
        if pid < 0:
            return []
        buf = self._recent.get(self._leader_key(session_id, pid))
        if buf is None:
            return []
        return list(buf)

    def reset_session(self, session_id: str) -> int:
        """Drop all state for the given session. Returns number removed."""
        before = len(self._pairs) + len(self._recent)
        sid = session_id or ""
        self._pairs = {k: v for k, v in self._pairs.items() if k[0] != sid}
        self._recent = {k: v for k, v in self._recent.items() if k[0] != sid}
        return before - len(self._pairs) - len(self._recent)

    def reset_all(self) -> None:
        self._pairs.clear()
        self._recent.clear()
