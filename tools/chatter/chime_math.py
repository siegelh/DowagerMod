"""Pure-Python twin of the chime-in math used by CvLeaderChatter.py.

The game-side `_maybe_queue_chime` lives in py24 inside CvLeaderChatter and
talks to the Civ4 Python API directly (gc, isAlive, AI_getAttitude, etc.).
That function can't be unit-tested directly without a Civ4 runtime, so the
arithmetic core -- attitude-to-weight, at-war bonus, weighted random pick --
lives here too and is exercised by tools/chatter/tests/test_chime_math.py.

The two copies MUST stay in sync. Game-side constants of record:

    _CHIME_ATTITUDE_WEIGHT = {"Furious": 4, "Friendly": 4,
                              "Annoyed": 2, "Pleased": 2,
                              "Cautious": 1}
    _CHIME_AT_WAR_BONUS = 2
    CHIME_BASE_PROB = 0.5
    CHIME_DECAY_FACTOR = 0.6
"""
from __future__ import annotations

import random
from typing import Iterable, Optional


CHIME_ATTITUDE_WEIGHT = {
    "Furious": 4,
    "Friendly": 4,
    "Annoyed": 2,
    "Pleased": 2,
    "Cautious": 1,
}
CHIME_AT_WAR_BONUS = 2
CHIME_BASE_PROB = 0.5
CHIME_DECAY_FACTOR = 0.6


def candidate_weight(attitude: str, at_war: bool) -> int:
    """Weight assigned to a chime candidate based on attitude + war state.

    Unknown attitude strings default to Cautious (weight 1). At-war adds
    a flat bonus regardless of attitude.
    """
    base = CHIME_ATTITUDE_WEIGHT.get(attitude, 1)
    if at_war:
        base += CHIME_AT_WAR_BONUS
    return base


def chime_probability(chain_depth: int) -> float:
    """Probability of a chime firing at the given chain depth.

    Decays geometrically: 0.5, 0.3, 0.18, ... Cap is enforced separately
    by CHAIN_MAX_DEPTH on the game side; this function alone never
    returns 0 for nonneg depth, but callers should still gate on cap.
    """
    if chain_depth < 0:
        return 0.0
    return CHIME_BASE_PROB * (CHIME_DECAY_FACTOR ** chain_depth)


def weighted_pick(candidates: Iterable, rng: Optional[random.Random] = None) -> Optional[int]:
    """Pick one (pid, weight) tuple proportional to weight. Returns the pid, or None.

    `candidates` is an iterable of (pid, weight) tuples; weight > 0.
    `rng` defaults to the module-level `random` for prod use; pass a seeded
    Random for deterministic tests.
    """
    pool = [(int(pid), int(w)) for pid, w in candidates if int(w) > 0]
    if not pool:
        return None
    total = sum(w for _pid, w in pool)
    if total <= 0:
        return None
    r = rng if rng is not None else random
    pick = r.randint(1, total)
    running = 0
    for pid, w in pool:
        running += w
        if pick <= running:
            return pid
    return pool[-1][0]
