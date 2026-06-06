"""Tone -> SSML <prosody> mapping for CHAT_REPLY lines.

The LLM emits a JSON object {line, tone} where tone is one of the values in
TONE_PROSODY. We map each tone to (pitch_offset, rate_offset) values that
get added on top of the speaker's base pitch/rate (the per-leader voice
spec, or the global cfg.voiceover.speech_rate fallback).

Why universal <prosody> instead of mstts:express-as styles? Style support
varies wildly per Azure voice -- the matrix is incomplete and changes
across model updates. <prosody pitch=... rate=...> works on every neural
voice, gives us consistent results, and can be combined predictably with
the leader's signature pacing.

Offsets are RELATIVE percentage adjustments. add_percent("+50%", "+12%")
returns "+62%". Empty base means the offset is used as-is.
"""
from __future__ import annotations

import re
from typing import Tuple


# Tone -> (pitch_offset, rate_offset). Both as SSML percentage strings.
# Empty string means no change on that axis.
#
# Direction: positive rate = faster, positive pitch = higher.
# Values are conservative -- per-tone modulation should be felt, not
# overpower the leader's signature voice.
TONE_PROSODY = {
    "angry":      ("+8%",  "+12%"),   # raised, faster -- spitting words
    "amused":     ("+4%",  "+8%"),    # slight lift, brisker -- enjoying it
    "haughty":    ("-3%",  "-2%"),    # lower, deliberate -- looking down nose
    "pleased":    ("+5%",  "+5%"),    # warm, brighter -- genuine
    "cold":       ("-4%",  "-6%"),    # lower, slower -- contempt
    "menacing":   ("-7%",  "-8%"),    # gravelly, slow -- threat
    "wistful":    ("-3%",  "-10%"),   # softer, slower -- regretful
    "theatrical": ("",     ""),       # neutral -- inherits base, default fallback
}


_PERCENT_RE = re.compile(r"^([+-]?)(\d+(?:\.\d+)?)%$")


def _parse_percent(value: str) -> float | None:
    """Parse '+50%' -> 50.0, '-10%' -> -10.0, '+0%' -> 0.0, '' -> None.

    Returns None for unparseable values (e.g. 'slow', 'x-low', '') so the
    caller can fall back. We only support percentage form because that's
    all the rest of the pipeline emits.
    """
    if not value:
        return None
    s = value.strip()
    if not s:
        return None
    m = _PERCENT_RE.match(s)
    if not m:
        return None
    sign, num = m.group(1), m.group(2)
    try:
        v = float(num)
    except ValueError:
        return None
    return -v if sign == "-" else v


def add_percent(base: str, offset: str) -> str:
    """Layer a percentage offset on top of a percentage base.

    Both inputs are SSML percent strings ('+50%', '-10%', '') or empty.
    add_percent('+50%', '+12%') -> '+62%'.
    add_percent('+50%', '')     -> '+50%' (no change).
    add_percent('', '+12%')     -> '+12%' (offset alone).

    NON-PERCENT BASE (e.g. semitones '+24st', Hz '+400Hz', named keywords
    like 'slow' / 'x-low'): the base is preserved verbatim and the offset
    is DROPPED on that axis. We don't try to convert units cross-domain,
    and dropping the offset is safer than dropping a deliberately picked
    extreme base like a chipmunk '+24st' pitch.

    Always returns a string. Caller passes it directly into SSML.
    """
    b = _parse_percent(base)
    o = _parse_percent(offset)
    if b is None and o is None:
        return ""
    if b is None and base:
        # Non-percent base (semitones / Hz / named keyword): preserve as-is,
        # drop the offset rather than silently clobbering the base value.
        return base
    total = (b or 0.0) + (o or 0.0)
    # Render as integer when possible -- SSML accepts both, integer is tidier
    if abs(total - round(total)) < 1e-6:
        return _format_int_percent(int(round(total)))
    return _format_float_percent(total)


def _format_int_percent(n: int) -> str:
    if n == 0:
        return "+0%"
    return ("+%d%%" % n) if n > 0 else ("%d%%" % n)


def _format_float_percent(n: float) -> str:
    if n == 0.0:
        return "+0%"
    return ("+%.1f%%" % n) if n > 0 else ("%.1f%%" % n)


def prosody_for(tone: str) -> Tuple[str, str]:
    """Return the (pitch_offset, rate_offset) prosody pair for a tone.

    Unknown / empty / None tones fall back to 'theatrical' (no change).
    """
    if not tone:
        return TONE_PROSODY["theatrical"]
    return TONE_PROSODY.get(tone.strip().lower(), TONE_PROSODY["theatrical"])
