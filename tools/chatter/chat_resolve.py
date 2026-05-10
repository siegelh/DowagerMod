"""Sidecar (py3) fuzzy resolver for "which leader is the human addressing?".

This is a parallel of CvLeaderChatter._resolve_addressed_leader() in the
game-side py24 module. It exists for two reasons:

1. The game-side resolver imports CvPythonExtensions and can't be unit-
   tested directly, so this sidecar implementation lets us cover the
   scoring/threshold logic in pytest.

2. The CLI test harness (chat_test.py) needs to resolve --leader strings
   like "Louie" -> "Louis XIV" without launching the game.

KEEP THIS IN SYNC with the game-side implementation. The two should
produce the same result for the same inputs (modulo the live alive-AI
filter, which only applies in-game).
"""
from __future__ import annotations

from typing import Iterable, Optional, Tuple

from tools.chatter.leader_roster import LEADERS

# Match the game-side tunable.
CHAT_FUZZY_THRESHOLD = 60
CHAT_IDLE_SECONDS = 300


def strip_chat_chrome(text: str) -> str:
    """Strip Civ4 chat color tags and '[Name to all]:' channel prefix.

    Civ4 onChat hands us the formatted display string, e.g.
        '<color=165,140,229,255>[hasiegel to all]:  uhhh hello?</color>'
    We want just 'uhhh hello?' for the resolver and the LLM prompt.

    Mirror of CvLeaderChatter._strip_chat_chrome (game-side py24).
    """
    if not text:
        return text
    s = text
    while True:
        i = s.find("<color=")
        if i < 0:
            break
        j = s.find(">", i)
        if j < 0:
            break
        s = s[:i] + s[j + 1:]
    for closer in ("</color>", "</COLOR>", "</Color>"):
        s = s.replace(closer, "")
    s = s.lstrip()
    if s.startswith("["):
        end = s.find("]:")
        if end > 0:
            s = s[end + 2:]
    return s.strip()

# Common English words that look like leader-name prefixes / fuzzy matches
# but are almost never the user actually addressing a leader. Filtered
# BEFORE scoring so they can never produce a false positive.
# Keep this list short and conservative -- adding more words risks
# blocking legitimate addresses (e.g. 'gilg' is short, but isn't English).
COMMON_STOPWORDS = frozenset((
    # 3-letter
    "the", "and", "for", "are", "but", "not", "you", "any", "can",
    "had", "her", "his", "she", "was", "one", "our", "out", "day",
    "get", "has", "him", "how", "man", "new", "now", "old", "see",
    "two", "way", "who", "boy", "did", "its", "let", "say", "too",
    "use", "all", "got",
    # 4-letter
    "this", "that", "with", "have", "from", "they", "your", "what",
    "when", "make", "like", "time", "just", "know", "take", "into",
    "good", "some", "than", "then", "look", "only", "come", "over",
    "also", "back", "well", "even", "much", "want", "give", "here",
    "more", "most", "find", "tell", "many", "both", "left", "next",
    "open", "play", "real", "high", "long", "gone", "city", "lord",
    "hello", "hey",
    # 4-letter -- common verbs that prefix-match leader names. Without
    # these the resolver false-positives:
    #   "I will go"  -> "will" prefix of "Willem van Oranje"
    #   "wash up"    -> "wash" prefix of "Washington"
    #   "talk soon"  -> no current leader, but reserved
    "will", "wash", "talk", "tell", "told", "said", "show", "kept",
    "hand", "head", "team", "year", "feel", "felt", "live", "kind",
    "rest", "side", "wait", "stop", "work", "hear", "deal", "save",
    "burn",
    # 5+ letter (only the worst false-positive triggers)
    "their", "would", "there", "could", "about", "after", "first",
    "where", "these", "those", "still", "still", "world", "every",
    "shall", "while", "going", "wonder", "wonders",
    "people", "before", "really", "thanks", "please", "should",
    "testing",
))


def _levenshtein(a: str, b: str) -> int:
    """Classic Levenshtein distance."""
    if a == b:
        return 0
    la, lb = len(a), len(b)
    if la == 0:
        return lb
    if lb == 0:
        return la
    prev = list(range(lb + 1))
    for i in range(1, la + 1):
        curr = [i] + [0] * lb
        ai = a[i - 1]
        for j in range(1, lb + 1):
            cost = 0 if ai == b[j - 1] else 1
            curr[j] = min(curr[j - 1] + 1, prev[j] + 1, prev[j - 1] + cost)
        prev = curr
    return prev[lb]


def _score_leader_match(token: str, leader_name_lower: str) -> int:
    """Score one (lowercase) token against one (lowercase) leader name."""
    if not token:
        return 0
    if token == leader_name_lower:
        return 100
    parts = leader_name_lower.split()
    best = 0
    for w in parts:
        if not w:
            continue
        if token == w and len(w) >= 3:
            best = max(best, 90)
        if len(token) >= 4 and w.startswith(token):
            best = max(best, 70)
        if len(w) >= 5 and len(token) >= 4 and abs(len(token) - len(w)) <= 2:
            d = _levenshtein(token, w)
            if d <= 2:
                best = max(best, 100 - 25 * d)
    return best


def _tokenize(text: str) -> list:
    """Split lowercase text into >=3-char alphanumeric tokens, dropping stopwords."""
    s = (text or "").lower()
    cur = []
    out = []
    for ch in s:
        if ch.isalnum():
            cur.append(ch)
        else:
            if cur:
                out.append("".join(cur))
                cur = []
    if cur:
        out.append("".join(cur))
    return [t for t in out if len(t) >= 3 and t not in COMMON_STOPWORDS]


def resolve_addressed_leader(
    text: str,
    *,
    leaders: Iterable = None,
    active_partner_name: Optional[str] = None,
    active_partner_idle_seconds: float = 1e9,
    threshold: int = CHAT_FUZZY_THRESHOLD,
) -> Tuple[Optional[str], Optional[str]]:
    """Decide which leader the human is talking to.

    Returns (leader_name, why) where why is one of:
      'name_match'      -- a leader name was found in the message.
      'active_partner'  -- no name, but we have an active partner in window.
      None              -- no match; caller should ignore.

    leaders is an iterable of (leader_name, civ_short_name) tuples;
    defaults to the static BTS roster. Pass a custom roster to test
    edge cases or restrict the search to alive AIs.
    """
    s = (text or "").strip()
    if not s:
        return (None, None)
    s_low = s.lower()
    tokens = _tokenize(s_low)
    if leaders is None:
        leaders = LEADERS

    best_name = None
    best_score = 0
    best_namelen = 9_999
    for name, _civ in leaders:
        name_low = name.lower()
        if name_low in s_low:
            score = 100
            if score > best_score or (score == best_score and len(name_low) < best_namelen):
                best_score = score
                best_name = name
                best_namelen = len(name_low)
            continue
        local_best = 0
        for tok in tokens:
            sc = _score_leader_match(tok, name_low)
            if sc > local_best:
                local_best = sc
        if local_best >= threshold:
            if local_best > best_score or (local_best == best_score and len(name_low) < best_namelen):
                best_score = local_best
                best_name = name
                best_namelen = len(name_low)

    if best_name is not None:
        return (best_name, "name_match")

    if active_partner_name and active_partner_idle_seconds <= CHAT_IDLE_SECONDS:
        return (active_partner_name, "active_partner")

    return (None, None)
