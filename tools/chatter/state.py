"""Per-pair conversation state for the chatter sidecar.

Currently in-memory only; lost on daemon restart. v1.1 may persist to disk.
Keys are (session_id, ordered_pair) tuples.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple


PairKey = Tuple[str, int, int]  # (session_id, speaker_id, target_id)


@dataclass
class PairState:
    last_event_unix: float = 0.0
    exchanges_done: int = 0
    last_response_id: Optional[str] = None  # for future Responses API threading


class StateStore:
    def __init__(self):
        self._pairs: Dict[PairKey, PairState] = {}

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

    def reset_session(self, session_id: str) -> int:
        """Drop all state for the given session. Returns number removed."""
        before = len(self._pairs)
        self._pairs = {k: v for k, v in self._pairs.items() if k[0] != session_id}
        return before - len(self._pairs)

    def reset_all(self) -> None:
        self._pairs.clear()
