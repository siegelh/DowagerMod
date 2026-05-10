"""Sidecar (py3) parser for Civ4 onChat chrome strings.

This is a parallel of CvLeaderChatter._parse_chat_chrome() in the
game-side py24 module. It exists so we can unit-test the parsing logic
without launching Civ4.

KEEP THIS IN SYNC with the game-side implementation. They must produce
identical (typer_name, stripped_text) tuples for the same input.

Civ4 hands `onChat` the formatted display string. Examples:

    '<color=165,140,229,255>[hasiegel to all]:  uhhh hello?</color>'
    -> ('hasiegel', 'uhhh hello?')

    '[Foo to Player3]:  psst'
    -> ('Foo', 'psst')

    'just text'      -> ('', 'just text')      # no chrome (raw call?)
    ''               -> ('', '')

The typer name is the first whitespace-trimmed token preceding ' to ',
inside the leading '[...]:' bracket. We capture only the typer; the
recipient ('all', 'Player3', 'TeamN', ...) is not yet useful for our
pipeline. Recipient parsing can be added later if PM-only flows matter.
"""
from __future__ import annotations

from typing import Tuple


def _strip_color_tags(text: str) -> str:
    """Remove <color=...> opening tags and </color> closers."""
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
    return s


def parse_chat_chrome(text: str) -> Tuple[str, str]:
    """Return (typer_name, stripped_text) from a Civ4 onChat string.

    typer_name is '' if no '[Name to recipient]:' chrome was found.
    stripped_text is the message body with chrome and color tags removed.
    """
    if not text:
        return "", text or ""
    s = _strip_color_tags(text).lstrip()
    if not s.startswith("["):
        # No bracket chrome; return whole body, no typer.
        return "", s.strip()
    end = s.find("]:")
    if end <= 0:
        # Malformed: '[' but no ']:' close. Treat as no chrome.
        return "", s.strip()
    inside = s[1:end]               # what's between '[' and ']:'
    body = s[end + 2:].strip()      # message body after the colon
    # Find the first ' to ' separator inside the bracket.
    sep = inside.find(" to ")
    if sep <= 0:
        # No ' to ' separator -- can't isolate typer. Drop chrome cleanly.
        return "", body
    typer = inside[:sep].strip()
    return typer, body


def strip_chat_chrome(text: str) -> str:
    """Back-compat wrapper that returns only the stripped body."""
    return parse_chat_chrome(text)[1]
