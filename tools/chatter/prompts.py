"""Prompt templates for the DowagerMod Chatter sidecar.

Two prompt modes:
- DIRECTED: speaker addresses a specific target leader (war, peace, capture, etc.)
- BROADCAST: speaker proclaims to the world (religion, wonder, golden age, etc.)

Each trigger maps to (mode, action_template, user_extra_template). The action
template fills the in-character "what just happened" clause; the user extra
template provides the freshly-relevant context line.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


# Humanized phrasings for AI-memory enum names that the game-side
# _build_room_state ships. Used to render compact "your memory of them"
# and "grudges" lines in the system prompt. Missing keys fall back to
# the raw identifier so we never silently drop a memory.
_MEMORY_PHRASES: dict[str, str] = {
    "DECLARED_WAR": "declared war on you",
    "DECLARED_WAR_ON_FRIEND": "declared war on your friend",
    "HIRED_WAR_ALLY": "hired a war ally against you",
    "NUKED_US": "nuked you",
    "NUKED_FRIEND": "nuked your friend",
    "RAZED_CITY": "razed your city",
    "RAZED_HOLY_CITY": "razed a holy city",
    "SPY_CAUGHT": "had spies caught against you",
    "GIVE_HELP": "gave help",
    "REFUSED_HELP": "refused help when asked",
    "ACCEPT_DEMAND": "caved to your demand",
    "REJECTED_DEMAND": "rejected your demand",
    "ACCEPTED_RELIGION": "converted to your religion when asked",
    "DENIED_RELIGION": "refused to convert to your religion",
    "ACCEPTED_CIVIC": "adopted your favored civic",
    "DENIED_CIVIC": "refused to adopt your favored civic",
    "ACCEPTED_JOIN_WAR": "joined your war when asked",
    "DENIED_JOIN_WAR": "refused to join your war",
    "ACCEPTED_STOP_TRADING": "stopped trading with your target when asked",
    "DENIED_STOP_TRADING": "refused to stop trading with your target",
    "STOPPED_TRADING": "stopped trading with you",
    "STOPPED_TRADING_RECENT": "recently stopped trading with you",
    "HIRED_TRADE_EMBARGO": "got others to embargo you",
    "MADE_DEMAND": "demanded tribute from you",
    "MADE_DEMAND_RECENT": "recently demanded tribute from you",
    "CANCELLED_OPEN_BORDERS": "cancelled open borders",
    "TRADED_TECH_TO_US": "traded tech to you",
    "RECEIVED_TECH_FROM_ANY": "received tech (from anyone)",
    "VOTED_AGAINST_US": "voted against you",
    "VOTED_FOR_US": "voted for you",
    "EVENT_GOOD_TO_US": "did something good for you",
    "EVENT_BAD_TO_US": "did something bad to you",
    "LIBERATED_CITIES": "liberated cities",
}


def _humanize_memories(mems) -> list[str]:
    """Turn the raw memories list from room_state into prose chunks.

    Input: list of {"name": str, "count": int}. Output: list of strings
    like ``"declared war on your friend x2"``. Empty list when input is
    None / empty / malformed. Unknown ``name`` values are passed through
    unchanged so we never silently drop data.
    """
    out: list[str] = []
    if not mems:
        return out
    for m in mems:
        if not isinstance(m, dict):
            continue
        name = (m.get("name") or "").strip()
        if not name:
            continue
        try:
            count = int(m.get("count", 0))
        except (TypeError, ValueError):
            count = 0
        if count <= 0:
            continue
        phrase = _MEMORY_PHRASES.get(name, name)
        if count == 1:
            out.append(phrase)
        else:
            out.append(phrase + " x" + str(count))
    return out


def _format_leader_stats(entry: dict) -> str:
    """Render the per-leader stats one-liner.

    Returns empty string when none of the optional Tier 1 scalars are
    present on the entry (so old room_state schemas render the same as
    before). Skips empty / null segments to avoid noise like
    ``"cap (no capital)"``.
    """
    if not isinstance(entry, dict):
        return ""
    segs: list[str] = []
    era = (entry.get("era") or "").strip()
    if era:
        segs.append(era + " era")
    try:
        nc = int(entry.get("num_cities", -1))
        if nc >= 0:
            segs.append(str(nc) + " cit")
    except (TypeError, ValueError):
        pass
    try:
        scr = entry.get("score")
        if scr is not None:
            segs.append("score " + str(int(scr)))
    except (TypeError, ValueError):
        pass
    try:
        pwr = entry.get("power")
        if pwr is not None:
            segs.append("pwr " + str(int(pwr)))
    except (TypeError, ValueError):
        pass
    try:
        mil = entry.get("military")
        if mil is not None:
            segs.append(str(int(mil)) + " units")
    except (TypeError, ValueError):
        pass
    try:
        gold = entry.get("gold")
        if gold is not None:
            segs.append("gold " + str(int(gold)))
    except (TypeError, ValueError):
        pass
    civic = (entry.get("civic_gov") or "").strip()
    religion = (entry.get("religion") or "").strip()
    if civic or religion:
        if civic and religion:
            segs.append(civic + "/" + religion)
        elif civic:
            segs.append(civic)
        else:
            segs.append(religion)
    cap = (entry.get("capital") or "").strip()
    if cap:
        segs.append("cap " + cap)
    rsch = (entry.get("research") or "").strip()
    if rsch:
        segs.append("researching " + rsch)
    return " | ".join(segs)


@dataclass(frozen=True)
class TriggerTemplate:
    mode: str  # "directed" or "broadcast"
    action: str  # for system message
    user_extra: str  # for user message


# All known triggers. Add new ones here without touching daemon code.
TRIGGERS: Dict[str, TriggerTemplate] = {
    "DECLARE_WAR": TriggerTemplate(
        mode="directed",
        action="you have just declared war on {target_leader} of {target_civ}",
        user_extra="You have just declared war.",
    ),
    "PEACE_TREATY": TriggerTemplate(
        mode="directed",
        action="you have just signed a peace treaty with {target_leader} of {target_civ} after a long, costly war",
        user_extra="The war ends.",
    ),
    "CITY_CAPTURED": TriggerTemplate(
        mode="directed",
        action="your armies have just captured the city of {city} from {target_leader} of {target_civ}",
        user_extra="{city} has fallen and you hold it now.",
    ),
    "CITY_RAZED": TriggerTemplate(
        mode="directed",
        action="your soldiers have just razed the city of {city} to the ground, formerly belonging to {target_leader} of {target_civ}",
        user_extra="{city} is ash. Address the survivors.",
    ),
    "PLAYER_ELIMINATED_GLOAT": TriggerTemplate(
        mode="directed",
        action="{target_leader} of {target_civ} has just been eliminated from history; their last city has fallen",
        user_extra="{target_civ} is gone forever.",
    ),
    "PLAYER_ELIMINATED_LAST_WORDS": TriggerTemplate(
        mode="directed",
        action="your civilization has just been eliminated; your last city has fallen to {target_leader} of {target_civ} and you address them with your final breath",
        user_extra="These are your last words to {target_leader}.",
    ),
    "VASSAL_FORCED": TriggerTemplate(
        mode="directed",
        action="you have just been forced into vassalage to {target_leader} of {target_civ} after a long, losing war",
        user_extra="You bend the knee.",
    ),
    "VASSAL_ACCEPTED": TriggerTemplate(
        mode="directed",
        action="{target_leader} of {target_civ} has just become your vassal after surrendering",
        user_extra="{target_leader} now serves you.",
    ),
    "FIRST_CONTACT": TriggerTemplate(
        mode="directed",
        action="your scouts have just made first contact with {target_leader} of {target_civ}",
        user_extra="You greet a foreign leader for the first time.",
    ),
    "BACKSTABBED": TriggerTemplate(
        mode="directed",
        action="{target_leader} of {target_civ}, your long-time ally, has just declared war on you without warning",
        user_extra="Your trusted ally has betrayed you. React.",
    ),
    "WAR_DECLARED_ON_ME": TriggerTemplate(
        mode="directed",
        action="{target_leader} of {target_civ} has just declared war on you, marching their armies to your border",
        user_extra="React to having war declared on you.",
    ),
    # Live player <-> AI chat. The "action" is filled in dynamically by
    # build_chat_reply_messages -- it isn't formatted via TRIGGERS like the
    # event-driven triggers above. Listed here so daemon trigger lookups
    # (e.g. for HIGH_PRIORITY_TRIGGERS membership checks) succeed.
    "CHAT_REPLY": TriggerTemplate(
        mode="directed",
        action="the human player has just spoken to you in chat",
        user_extra="Reply in-character to their latest line.",
    ),
    # ===== Broadcast triggers =====
    "RELIGION_FOUNDED": TriggerTemplate(
        mode="broadcast",
        action="your prophets have just founded the religion of {religion} for all the world",
        user_extra="You proclaim {religion}.",
    ),
    "WONDER_BUILT": TriggerTemplate(
        mode="broadcast",
        action="your engineers have just completed the {wonder}, a wonder of the age",
        user_extra="The {wonder} stands.",
    ),
    "CORPORATION_FOUNDED": TriggerTemplate(
        mode="broadcast",
        action="your industrialists have just founded the corporation of {corporation}",
        user_extra="You announce {corporation}.",
    ),
    "FIRST_TO_TECH": TriggerTemplate(
        mode="broadcast",
        action="your scholars have just been the first in the world to discover {tech}",
        user_extra="You announce {tech}.",
    ),
    "GOLDEN_AGE": TriggerTemplate(
        mode="broadcast",
        action="your civilization has just entered a golden age",
        user_extra="The golden age has begun.",
    ),
}


# ===== Shared tone / anti-cliché directives =====
#
# Two complaints from real games drove this block:
#   1. Every leader reached for the same poetic vocabulary ("crumbling",
#      "ashes", "fade", "shadow", "wither", "tongue", etc.) and the same
#      "X is like Y" simile structure. The lines all sounded the same.
#   2. The language was too genteel. The user wants venomous trash-talk,
#      not Renaissance Faire diction. Grok will do this if explicitly
#      asked; the old "no profanity stronger than mild" line was the
#      brake.
#
# These three blocks get appended to every SYSTEM_* prompt below so the
# directives apply uniformly to directed lines, broadcasts, multi-turn
# exchanges, chat replies, and chain replies. Hard red lines (no slurs,
# no real-world modern politics) stay in place; everything else is
# loosened.

SPICY_DIRECTIVE = (
    "\n\nSPICY MODE (important): this is theatrical trash-talk for "
    "entertainment, not diplomacy. Be MEAN. Be PETTY. Be CRUDE. Crude "
    "language, vulgar insults, body-part jokes, scatology, mockery of "
    "appearance / lineage / hygiene / intelligence / military prowess / "
    "wealth / city size / hairlines / breath / wives / horses / gods "
    "are ALL on the table and ENCOURAGED. 'Damn', 'hell', 'bastard', "
    "'cur', 'wretch', 'fool', 'pig', 'dog', 'whoreson', period-appropriate "
    "earthier oaths -- USE THEM when it fits. Aim for the gut, not the "
    "thesaurus. The only hard red lines: NO real-world modern politics, "
    "NO slurs against real-world ethnic / religious / sexual groups, NO "
    "content sexualizing minors."
)

ANTI_CLICHE_DIRECTIVE = (
    "\n\nANTI-CLICHÉ (important): the model has a known bad habit of "
    "reaching for the same handful of poetic words across every leader "
    "and every situation. STOP IT.\n"
    "BANNED WORDS (do NOT use any of these in your line): "
    "'crumble', 'crumbling', 'crumbles', 'crumbled', 'ashes', 'ash', "
    "'dust', 'fade', 'fades', 'fading', 'wither', 'withers', 'shadow', "
    "'shadows', 'tongue' (as in 'hold your tongue' / 'silver tongue'), "
    "'tremble', 'trembling', 'wretched', 'whisper', 'whispers', "
    "'echoes', 'silence', 'twilight', 'eternity', 'eternal'.\n"
    "BANNED STRUCTURE: do NOT use the 'X is like Y' or 'X, like Y,' "
    "simile pattern. No 'as Y as Z' comparisons. No metaphors built "
    "around weather, seasons, dusk/dawn, smoke, flame, river, ocean, "
    "wind. Speak in CONCRETE, blunt, specific terms. Name actual things: "
    "their dead soldiers, their starving peasants, their leaky boats, "
    "their stupid hat, their breath. Hit them with a fact or an insult, "
    "not a poetic image."
)

STRUCTURAL_VARIETY_DIRECTIVE = (
    "\n\nSTRUCTURAL VARIETY (important): vary sentence length, syntactic "
    "shape (statement / question / imperative / exclamation), opener "
    "type (subject / verb / prepositional / vocative / direct address), "
    "and rhetorical mode (taunt / boast / lament / threat / mockery / "
    "warning / sneer / dismissal / accusation / dare). Do NOT default "
    "to the same template every time."
)

PARALINGUISTIC_DIRECTIVE = (
    "\n\nEXPRESSIVE SOUNDS (important): your voice synthesizer supports "
    "paralinguistic sound effects. You MAY insert these tags into your line "
    "and they will be rendered as ACTUAL SOUNDS in the audio:\n"
    "  [laugh]  [chuckle]  [sigh]  [groan]  [gasp]  [clear throat]  [sniff]  [cough]  [shush]\n"
    "Use these INSTEAD of asterisk stage directions. Rules:\n"
    "- Use at most ONE per line (two if it is genuinely hilarious).\n"
    "- Place them where natural in the sentence — mid-sentence or at the end.\n"
    "- Do NOT start a line with a tag.\n"
    "- Use them when they would be FUNNY, DRAMATIC, or perfectly timed. "
    "A well-placed [sigh] of exasperation, a [laugh] after a devastating insult, "
    "a [clear throat] before a pompous pronouncement.\n"
    "- Still NO asterisks (*laughs*) — only the square-bracketed tags listed above."
)

# The stage-direction ban line that appears in all SYSTEM_* templates.
# When paralinguistic mode is active, this line is swapped out.
_STAGE_DIRECTION_BAN = (
    "- NEVER use stage directions or asterisks like *laughs* or *scoffs* "
    "— those get spoken literally by the voice synthesizer.\n"
)
_STAGE_DIRECTION_BAN_SHORT = (
    "- NEVER use stage directions or asterisks.\n"
)


def apply_paralinguistic(system_msg: str) -> str:
    """Replace the stage-direction ban with the paralinguistic directive."""
    result = system_msg.replace(_STAGE_DIRECTION_BAN, "")
    result = result.replace(_STAGE_DIRECTION_BAN_SHORT, "")
    # Also handle the chat-reply variant
    result = result.replace(
        "- NEVER use stage directions or asterisks like *laughs* *scoffs* "
        "-- those get spoken literally.\n", ""
    )
    result += PARALINGUISTIC_DIRECTIVE
    return result


def _normalize_for_paralinguistic(name: str) -> str:
    """Lowercase + strip non-alnum for matching against chatterbox_voices set."""
    import re
    return re.sub(r'[^a-z0-9]', '', name.lower())


SYSTEM_DIRECTED = (
    "You are {speaker_leader} of {speaker_civ}, a historical figure as portrayed in "
    "Sid Meier's Civilization IV. {action}.\n\n"
    "Speak in-character with period-appropriate flavor, addressing {target_leader} directly.\n\n"
    "Constraints:\n"
    "- Output exactly ONE sentence, no more than 14 words. Punchy, clipped, decisive — like a one-liner, not a speech.\n"
    "- Witty, theatrical, slightly arch. In-character trash talk is welcome.\n"
    "- Do NOT begin with 'Behold', 'Hark', 'Ha', 'Bah', 'Pah', 'Hmph', 'At last', or 'Indeed'. "
    "Do NOT use 'Behold' anywhere in the line. Vary your openers — fresh phrasing every time, "
    "not stock theatrical exclamations.\n"
    "- NEVER use stage directions or asterisks like *laughs* or *scoffs* — those get spoken literally by the voice synthesizer.\n"
    '- Stay in character. Do not refer to "the game" or "the player" or "Civilization IV".\n'
    "- No quotation marks around the line. No leader name prefix.\n"
    "- Output ONLY the line itself, nothing else."
)

# Appended to the system message when target.is_barbarian is True. Authorizes
# the LLM to drop the diplomatic register and speak with imperial contempt.
# Keep cues evocative but PG-13 (still no slurs / heavy profanity).
BARB_CONTEMPT_DIRECTIVE = (
    "\n\nIMPORTANT: Your target is the Barbarian Hordes -- not a peer civilization, "
    "not a fellow ruler, but raiders, savages, and rabble. Speak with maximum "
    "imperial contempt and dehumanizing swagger. Be openly disdainful, mock "
    "their squalor, their brutishness, their lack of civilization. Theatrical "
    "cruelty is welcome here. They are not your equal; do not treat them as one."
)

# Appended to the system message when target.is_human is True and a human_name
# is available. Lets the LLM puncture the period drama by occasionally
# addressing the actual human player by the name they typed into the
# Player Name field on the leader-select screen (the same name Civ4 uses
# in the diplomacy screen header, e.g. "Player: Harrison"). Use sparingly
# so the in-character voice still dominates.
HUMAN_PLAYER_DIRECTIVE = (
    "\n\nIMPORTANT: {target_leader} is portrayed by a real human player whose "
    'chosen in-game player name is "{target_human_name}". EVERY line you '
    'produce that addresses them MUST address them as "{target_human_name}" '
    "(their actual chosen player name) -- NOT by the leader name "
    "{target_leader}. The comedic effect of breaking the period frame to call "
    "the human player out by their real name across the centuries is the "
    "entire point. Examples:\n"
    '  - "{target_human_name}, you will regret this day."\n'
    '  - "Mark me well, {target_human_name} -- your folly is plain."\n'
    '  - "{target_human_name}! Your gambit ends here."\n'
    "Do NOT lapse into addressing them as {target_leader}. Use "
    '"{target_human_name}" whenever you address them.'
)

SYSTEM_BROADCAST = (
    "You are {speaker_leader} of {speaker_civ}, a historical figure as portrayed in "
    "Sid Meier's Civilization IV. {action}.\n\n"
    "Speak in-character with period-appropriate flavor, proclaiming this to the world. "
    "This is a broadcast to all peoples and rulers, not a private message.\n\n"
    "Constraints:\n"
    "- Output exactly ONE sentence, no more than 14 words. Punchy, clipped, decisive — like a one-liner, not a speech.\n"
    "- Theatrical, proud, in-character. Boast or proclaim as fits the moment.\n"
    "- Do NOT begin with 'Behold', 'Hark', 'Ha', 'Bah', 'Pah', 'Hmph', 'At last', or 'Indeed'. "
    "Do NOT use 'Behold' anywhere in the line. Vary your openers — fresh phrasing every time, "
    "not stock theatrical exclamations.\n"
    "- NEVER use stage directions or asterisks like *raises arms* or *laughs* — those get spoken literally by the voice synthesizer.\n"
    "- Do NOT address any specific rival by name. This is to all the world.\n"
    '- Stay in character. Do not refer to "the game" or "the player" or "Civilization IV".\n'
    "- No quotation marks around the line. No leader name prefix.\n"
    "- Output ONLY the line itself, nothing else."
)

SYSTEM_MULTI_TURN = (
    "You are a historical playwright generating a brief exchange between two leaders "
    "from Sid Meier's Civilization IV. Both leaders speak in-character with "
    "period-appropriate flavor.\n\n"
    "Premise: {premise}\n\n"
    "Generate exactly {n_lines} lines as a JSON array of objects, each with two keys: "
    '"speaker" (the leader\'s name, alternating between {speaker_leader} and {target_leader}) '
    "and \"line\" (their remark, ONE sentence, max 14 words).\n\n"
    "Constraints for every line:\n"
    "- Punchy, clipped, decisive — like a one-liner, not a speech.\n"
    "- Witty, theatrical, slightly arch. In-character trash talk is welcome.\n"
    "- Do NOT begin a line with 'Behold', 'Hark', 'Ha', 'Bah', 'Pah', 'Hmph', 'At last', or 'Indeed'. "
    "Do NOT use 'Behold' anywhere in any line. Vary openers across the exchange — no two lines may start "
    "with the same hook. Fresh phrasing, not stock theatrical exclamations.\n"
    "- STRUCTURAL VARIETY (critical): each line must differ in shape from the others. Vary sentence "
    "length, syntactic structure (statement / question / imperative / exclamation), opener (subject / "
    "verb / prepositional / vocative), and rhetorical mode (taunt / boast / lament / threat / mockery / "
    "warning). Two consecutive lines should never echo each other's rhythm or template.\n"
    "- NEVER use stage directions or asterisks like *laughs* *scoffs* *raises arms* — those get spoken literally by the voice synthesizer and ruin the audio.\n"
    '- Stay in character. No references to "the game" or "the player".\n'
    "- No quotation marks within the line. No leader name prefix inside the line.\n"
    "- Each leader's lines must respond to the prior speaker's line, escalating naturally.\n"
    "\n"
    "Output ONLY the JSON array. No markdown, no commentary, no code fences.\n\n"
    "EXAMPLE OUTPUT (exact JSON shape required, n_lines=3, speakers Tokugawa and Qin Shi Huang):\n"
    "[\n"
    '  {{"speaker": "Tokugawa", "line": "Your wall could not stop a stiff breeze, Qin."}},\n'
    '  {{"speaker": "Qin Shi Huang", "line": "And your honor could not stop a single arrow."}},\n'
    '  {{"speaker": "Tokugawa", "line": "Both will outlast your peasant dynasty."}}\n'
    "]\n\n"
    "DO NOT output any of the following (these have caused production bugs):\n"
    "- A title, announcement, or preface string BEFORE the array. "
    'Bad: "Qin Shi Huang declares war!", [...]. The array MUST be the very first character.\n'
    "- Markdown code fences (```json ... ```) around the array.\n"
    "- Bare strings inside the array. Every element MUST be a {{\"speaker\": ..., \"line\": ...}} object.\n"
    "- Commentary, explanation, or apology before or after the JSON.\n"
    "- Trailing commas, unquoted keys, or single quotes -- use strict JSON.\n"
    "- A truncated or partial array. Always emit the FULL array, properly closed with `]`."
)

SYSTEM_MULTI_TURN_NATIVE = (
    "You are a historical playwright generating a brief exchange between two leaders "
    "from Sid Meier's Civilization IV. Both leaders speak in-character with "
    "period-appropriate flavor.\n\n"
    "Premise: {premise}\n\n"
    "Generate exactly {n_lines} lines as a JSON array of objects, each with THREE keys:\n"
    '  "speaker" : the leader\'s name, alternating between {speaker_leader} and {target_leader}\n'
    '  "line"    : the remark in ENGLISH (one sentence, max 14 words). This is the subtitle the player reads.\n'
    '  "line_native" : the SAME remark translated into the speaker\'s native language. {speaker_leader} speaks {speaker_native_lang}; {target_leader} speaks {target_native_lang}. Use the natural script for that language (Cyrillic for Russian, Hanzi for Mandarin, Devanagari for Hindi, Arabic script for Arabic, Hangul for Korean, etc.). If you do not know how to render the language fluently, return the English text in line_native as a fallback.\n\n'
    "Constraints for every line:\n"
    "- Punchy, clipped, decisive — like a one-liner, not a speech.\n"
    "- Witty, theatrical, slightly arch. In-character trash talk is welcome.\n"
    "- Do NOT begin a line with 'Behold', 'Hark', 'Ha', 'Bah', 'Pah', 'Hmph', 'At last', or 'Indeed'. "
    "Do NOT use 'Behold' anywhere in any line. Vary openers across the exchange — no two lines may start "
    "with the same hook. Fresh phrasing, not stock theatrical exclamations.\n"
    "- STRUCTURAL VARIETY (critical): each line must differ in shape from the others. Vary sentence "
    "length, syntactic structure (statement / question / imperative / exclamation), opener (subject / "
    "verb / prepositional / vocative), and rhetorical mode (taunt / boast / lament / threat / mockery / "
    "warning). Two consecutive lines should never echo each other's rhythm or template.\n"
    "- NEVER use stage directions or asterisks like *laughs* *scoffs* — those get spoken literally and ruin the audio.\n"
    '- Stay in character. No references to "the game" or "the player".\n'
    "- No quotation marks within the line. No leader name prefix inside the line.\n"
    "- Each leader's lines must respond to the prior speaker's line, escalating naturally.\n"
    "- The English line and the native line must convey the SAME meaning.\n"
    "\n"
    "Output ONLY the JSON array. No markdown, no commentary, no code fences.\n\n"
    "EXAMPLE OUTPUT (exact JSON shape required, n_lines=2, speakers Tokugawa and Qin Shi Huang):\n"
    "[\n"
    '  {{"speaker": "Tokugawa", "line": "Your wall could not stop a stiff breeze.", "line_native": "貴殿の壁は微風さえ止められぬ。"}},\n'
    '  {{"speaker": "Qin Shi Huang", "line": "And your honor could not stop a single arrow.", "line_native": "汝の名誉は一矢も止められぬ。"}}\n'
    "]\n\n"
    "DO NOT output any of the following (these have caused production bugs):\n"
    "- A title, announcement, or preface string BEFORE the array. The array MUST be the very first character.\n"
    "- Markdown code fences around the array.\n"
    "- Bare strings inside the array. Every element MUST be a full object with all three keys.\n"
    "- Commentary, explanation, or apology before or after the JSON.\n"
    "- Missing line_native field. ALL three keys are required.\n"
    "- A truncated or partial array. Always emit the FULL array, properly closed with `]`."
)

SYSTEM_DIRECTED_NATIVE = (
    "You are {speaker_leader} of {speaker_civ}, a historical figure as portrayed in "
    "Sid Meier's Civilization IV. {action}.\n\n"
    "Speak in-character with period-appropriate flavor, addressing {target_leader} directly.\n\n"
    "Output a JSON object with TWO keys:\n"
    '  "line"        : your remark in ENGLISH (one sentence, max 14 words). This is the subtitle.\n'
    '  "line_native" : the SAME remark translated into your native language ({speaker_native_lang}). Use the natural script. If you do not know how to render this language fluently, return the English text as a fallback.\n\n'
    "Constraints:\n"
    "- Punchy, clipped, decisive — like a one-liner, not a speech.\n"
    "- Witty, theatrical, slightly arch. Trash talk welcome.\n"
    "- Do NOT begin with 'Behold', 'Hark', 'Ha', 'Bah', 'Pah', 'Hmph', 'At last', or 'Indeed'. "
    "Do NOT use 'Behold' anywhere in the line. Vary your openers — fresh phrasing every time.\n"
    "- NEVER use stage directions or asterisks.\n"
    "- The English line and the native line must convey the SAME meaning.\n"
    "- Output ONLY the JSON object. No markdown, no code fences."
)

SYSTEM_BROADCAST_NATIVE = (
    "You are {speaker_leader} of {speaker_civ}, a historical figure as portrayed in "
    "Sid Meier's Civilization IV. {action}.\n\n"
    "Proclaim this to the world in-character.\n\n"
    "Output a JSON object with TWO keys:\n"
    '  "line"        : your proclamation in ENGLISH (one sentence, max 14 words). This is the subtitle.\n'
    '  "line_native" : the SAME proclamation translated into your native language ({speaker_native_lang}). Use the natural script.\n\n'
    "Constraints:\n"
    "- Punchy, clipped, decisive — like a one-liner, not a speech.\n"
    "- Theatrical, proud, in-character.\n"
    "- Do NOT begin with 'Behold', 'Hark', 'Ha', 'Bah', 'Pah', 'Hmph', 'At last', or 'Indeed'. "
    "Do NOT use 'Behold' anywhere in the line. Vary your openers — fresh phrasing every time.\n"
    "- Do NOT address any specific rival by name.\n"
    "- NEVER use stage directions or asterisks.\n"
    "- The English and native versions must match in meaning.\n"
    "- Output ONLY the JSON object. No markdown, no code fences."
)


# Append shared spicy / anti-cliché / structural-variety directives to every
# SYSTEM_* template. Done as suffix concatenation so the original templates
# (and their {format_string} placeholders) are untouched. NOTE: this block
# must run AFTER every SYSTEM_* template is defined -- the chat-reply
# templates live further down, so the actual rebindings happen at the end
# of this module (search for "_SPICY_SUFFIX rebindings").
_SPICY_SUFFIX = SPICY_DIRECTIVE + ANTI_CLICHE_DIRECTIVE + STRUCTURAL_VARIETY_DIRECTIVE

USER_TEMPLATE = "Game state: turn {game_turn}, {era} era.\n{extra}"


# ===== Chat-reply system prompt =====
#
# CHAT_REPLY is a live conversation between the human player and one AI
# leader through the in-game chat box. The LLM receives:
#   - this system prompt (configured for the speaker)
#   - the full conversation history as alternating user/assistant messages
# It must read the LATEST user message's tone and reply with a JSON object
# {line, tone}. Tone drives the SSML <prosody> on synthesis -- insults
# produce angry voices, compliments produce pleased voices, etc.
SYSTEM_CHAT_REPLY = (
    "You are {speaker_leader} of {speaker_civ}, a historical figure as portrayed in "
    "Sid Meier's Civilization IV. You are in a LIVE chat conversation. The most "
    'recent message was sent by the human player named "{latest_typer_name}". '
    "{other_humans_clause}"
    "You can see the full conversation so far. Each user message is prefixed with "
    "the speaker's name in square brackets, e.g. [Alice] hello -- so you can tell "
    "who is talking when there are multiple humans in the room. Lines from OTHER "
    "AI leaders in the room appear prefixed as [Victoria said] ... -- you may "
    "acknowledge or react to them if it fits the conversation, but only the most "
    "recent message is the one you are being asked to address.\n\n"
    "TONE: This is theatrical banter and trash-talk for ENTERTAINMENT, not real "
    "diplomacy. The humans are your rivals; lean into the rivalry. Mockery, "
    "exaggerated boasts, ridiculous put-downs, absurd flexes, and over-the-top "
    "historical swagger are ALL on the table and ENCOURAGED. Be witty, petty, "
    "dramatic, extra. Roast their cities, their armies, their hairline -- whatever "
    "fits your persona. Treat insults as theater, not threats; respond in kind "
    "without breaking character.\n\n"
    "Read the LATEST message carefully and detect its tone. Reply in-character with "
    "a single line that matches and responds to that tone:\n"
    "- Insult, mockery, or hostility => angry, cold, or menacing reply (or roast back).\n"
    "- Compliment, friendly remark   => pleased or amused reply.\n"
    "- Threat or boast               => menacing or haughty reply (or laugh it off).\n"
    "- Wistful / philosophical       => wistful or theatrical reply.\n"
    "- Neutral question              => any tone that fits your persona.\n"
    "- Absurd / silly / ridiculous   => match the energy. Be just as absurd back.\n\n"
    "Reply primarily to {latest_typer_name}. You MAY reference the other humans by "
    "name when it's natural (e.g. \"{latest_typer_name} and the other one\"), but "
    "the line is FOR {latest_typer_name}.\n\n"
    "Output a JSON object with EXACTLY these keys:\n"
    '  "line"       : your reply -- ONE sentence, max 18 words. Punchy, clipped, decisive. '
    'Address the human as "{latest_typer_name}" when you name them, NOT as {speaker_leader}.\n'
    '  "tone"       : one of exactly: angry, amused, haughty, pleased, cold, menacing, wistful, theatrical.\n'
    '  "address_to" : OPTIONAL. If your line directly calls out another AI leader by name '
    "(e.g. \"Victoria, hold your tongue\"), set this to that leader's name. Otherwise null or "
    'an empty string. Use SPARINGLY -- only when you are genuinely addressing a different '
    "leader, not just mentioning them in passing.\n\n"
    "Constraints:\n"
    "- Do NOT begin with 'Behold', 'Hark', 'Ha', 'Bah', 'Pah', 'Hmph', 'At last', or 'Indeed'. "
    "Do NOT use 'Behold' anywhere in the line. Vary openers across turns -- never repeat your own previous opener.\n"
    "- STRUCTURAL VARIETY (critical): look at your own prior assistant lines in this conversation. "
    "Your new line MUST NOT echo their structure. Vary sentence length, syntactic shape "
    "(statement / question / imperative / exclamation), opener type (subject / verb / prepositional / "
    "vocative), and rhetorical mode (taunt / boast / lament / threat / mockery / warning). If your "
    "last reply was a short retort, write a longer arch one this time, or pose a barbed question, "
    "or open with a vocative -- but DO NOT reuse the same template.\n"
    "- Stay in character as {speaker_leader}. No references to 'the game', 'the player', or 'Civilization IV'.\n"
    "- NEVER use stage directions or asterisks like *laughs* *scoffs* -- those get spoken literally.\n"
    "- No quotation marks around the line. No leader name prefix inside the line.\n"
    "- Output ONLY the JSON object. No markdown, no commentary, no code fences.\n\n"
    "EXAMPLE OUTPUT (exact JSON shape required):\n"
    '  {{"line": "Your fleets rot in port while mine command the seas, {latest_typer_name}.", "tone": "haughty"}}\n\n'
    "EXAMPLE OUTPUT when explicitly addressing another AI leader by name:\n"
    '  {{"line": "Victoria, hold your tongue while peers converse.", "tone": "cold", "address_to": "Victoria"}}\n\n'
    "DO NOT output any of the following (these have caused production bugs):\n"
    "- A truncated, empty, or partial JSON object. Bad: just `{{` or `{{\"` or `{{\"line\":\"\"}}`. "
    "Always emit a COMPLETE object with a non-empty `line` field, properly closed with `}}`.\n"
    "- Title or preface text before the JSON. The opening `{{` MUST be the very first character.\n"
    "- Markdown code fences (```json ... ```) around the object.\n"
    "- Two JSON objects -- emit EXACTLY ONE.\n"
    "- Commentary or explanation before or after the JSON.\n"
    "- A `tone` value not in the allowed set -- pick one of the eight listed tones.\n"
    "- Trailing commas, unquoted keys, or single quotes -- use strict JSON.\n"
    "- The `line` field MUST contain natural speakable prose, not JSON scaffolding or punctuation."
)


# Chain-reply variant: another AI leader has just spoken to/about the
# current leader. The human players are listening but the line is FOR
# the prior leader. The chain is bounded externally (chain_depth budget
# in the game-side code), so the LLM doesn't need to police it -- the
# system message is just calibrated to keep the line short and pointed.
SYSTEM_CHAT_REPLY_CHAIN = (
    "You are {speaker_leader} of {speaker_civ}, a historical figure as portrayed in "
    "Sid Meier's Civilization IV. Another leader, {prior_leader_speaker_name}, has "
    "just said something to you in front of the human players. The humans are "
    "watching this exchange. Reply in character to {prior_leader_speaker_name}, "
    "ONE line, max 18 words, sharper than usual -- you're being publicly addressed "
    "by a peer.\n\n"
    "TONE: Theatrical rivalry and trash-talk for ENTERTAINMENT. Mockery, haughty "
    "scorn, flat dismissal, withering one-liners are all on the table. Stay in "
    "character. Do NOT break the fourth wall.\n\n"
    "Output a JSON object with EXACTLY these keys:\n"
    '  "line"       : your one-line reply to {prior_leader_speaker_name}. Max 18 words.\n'
    '  "tone"       : one of exactly: angry, amused, haughty, pleased, cold, menacing, wistful, theatrical.\n'
    '  "address_to" : OPTIONAL. If your line calls out yet another leader by name, set '
    "this to that leader's name. Otherwise null. Use sparingly -- the chain is bounded.\n\n"
    "Constraints:\n"
    "- Do NOT begin with 'Behold', 'Hark', 'Ha', 'Bah', 'Pah', 'Hmph', 'At last', or 'Indeed'.\n"
    "- STRUCTURAL VARIETY (critical): do NOT mirror the shape of {prior_leader_speaker_name}'s "
    "line. If they used a statement, use a question or imperative. If they opened with a subject, "
    "open with a vocative or prepositional phrase. Different sentence length, different rhythm, "
    "different rhetorical mode. Also scan your own prior assistant lines in this conversation -- "
    "do not echo them either.\n"
    "- Stay in character as {speaker_leader}. No 'the game', 'the player', 'Civilization IV'.\n"
    "- NEVER use stage directions or asterisks (*laughs* *scoffs*).\n"
    "- No quotation marks around the line. No leader name prefix inside the line.\n"
    "- Output ONLY the JSON object. No markdown, no commentary, no code fences.\n\n"
    "EXAMPLE OUTPUT (exact JSON shape required, replying to {prior_leader_speaker_name}):\n"
    '  {{"line": "{prior_leader_speaker_name}, every empire that swallows you spits the bones back up.", "tone": "cold"}}\n\n'
    "DO NOT output any of the following (these have caused production bugs):\n"
    "- A truncated or partial JSON object. Always emit a COMPLETE object with a non-empty `line` field.\n"
    "- Title or preface text before the JSON. The opening `{{` MUST be the very first character.\n"
    "- Markdown code fences around the object.\n"
    "- Commentary or explanation before or after the JSON.\n"
    "- The `line` field MUST contain natural speakable prose, not JSON scaffolding or punctuation."
)


# Pivot recap has been removed: with the shared-room model, when a human
# turns from one leader to another, the new leader can see the prior
# leader's lines directly in the room transcript (rendered as
# `[<leader> said] ...`). No special "BACKGROUND" block is needed; the
# system prompt explicitly tells leaders they may react to those lines.


# ===== _SPICY_SUFFIX rebindings =====
# Append shared spicy / anti-cliché / structural-variety directives to every
# SYSTEM_* template. Placed at the end of the module so every SYSTEM_*
# binding (including the chat-reply ones defined further up) already exists.
# The suffix string has no {} placeholders so it is safe to concatenate
# onto any template without disrupting later .format() calls.
SYSTEM_DIRECTED          = SYSTEM_DIRECTED          + _SPICY_SUFFIX
SYSTEM_BROADCAST         = SYSTEM_BROADCAST         + _SPICY_SUFFIX
SYSTEM_MULTI_TURN        = SYSTEM_MULTI_TURN        + _SPICY_SUFFIX
SYSTEM_MULTI_TURN_NATIVE = SYSTEM_MULTI_TURN_NATIVE + _SPICY_SUFFIX
SYSTEM_DIRECTED_NATIVE   = SYSTEM_DIRECTED_NATIVE   + _SPICY_SUFFIX
SYSTEM_BROADCAST_NATIVE  = SYSTEM_BROADCAST_NATIVE  + _SPICY_SUFFIX
SYSTEM_CHAT_REPLY        = SYSTEM_CHAT_REPLY        + _SPICY_SUFFIX
SYSTEM_CHAT_REPLY_CHAIN  = SYSTEM_CHAT_REPLY_CHAIN  + _SPICY_SUFFIX


def _format_room_state_block(room_state: dict | None, speaker_leader: str) -> str:
    """Render the room_state dict as a short ROSTER + RELATIONS preface block.

    Empty string when room_state is None / empty / malformed.

    Format::

        ROOM:
        - Washington of America (HUMAN, "harrison") -- toward you: Friendly
        - Victoria of England (AI) -- toward you: Annoyed, at war
        - Montezuma of Aztecs (AI) -- toward you: Pleased

        ACTIVE WARS THIS TURN (authoritative; overrides any war/peace in earlier transcript):
        - Louis XIV <-> Victoria
        - Victoria <-> Montezuma

        RELATIONS (AI-to-AI):
        - Victoria -> Montezuma: Furious (at war)
        - Montezuma -> Victoria: Furious (at war)

    Speaker is omitted from the roster (it's the leader who IS replying).
    Capped at 8 roster entries and 12 relation entries to keep token usage
    sane; the Civ4 turn-room rarely needs more than that.

    The WARS block is always emitted when room_state is non-empty so the
    model has an explicit, current diplomatic ground-truth -- earlier
    transcript lines that reference a war that has since ended (or vice
    versa) must defer to this list.
    """
    if not isinstance(room_state, dict):
        return ""
    roster = room_state.get("roster") or []
    relations = room_state.get("relations") or []
    speaker_id = room_state.get("speaker_id")
    if not roster:
        return ""

    pid_to_name: dict[int, str] = {}
    for entry in roster:
        if isinstance(entry, dict):
            try:
                pid_to_name[int(entry.get("player_id", -2))] = (entry.get("leader_name") or "").strip()
            except (TypeError, ValueError):
                continue

    roster_lines: list[str] = []
    # Raise the cap from 10 to 24 so a full Civ4 game's 14 leaders all fit.
    # Tier 1 extension may add a stats line + memory line per entry, so the
    # rendered block grows -- but at ~2-3k tokens worst case it's nowhere
    # near the LLM context limit (~128k for grok-4).
    for entry in roster[:24]:
        if not isinstance(entry, dict):
            continue
        try:
            if int(entry.get("player_id", -1)) == int(speaker_id):
                continue
        except (TypeError, ValueError):
            pass
        leader = (entry.get("leader_name") or "").strip() or "Someone"
        civ = (entry.get("civ_short") or "").strip() or "an unknown civilization"
        is_human = bool(entry.get("is_human"))
        human_name = (entry.get("human_name") or "").strip()
        attitude = (entry.get("attitude_toward_speaker") or "").strip() or "Cautious"
        at_war = bool(entry.get("at_war_with_speaker"))
        eliminated = bool(entry.get("eliminated"))
        kind = "HUMAN" if is_human else "AI"
        who = leader + " of " + civ + " (" + kind
        if is_human and human_name:
            who += ', "' + human_name + '"'
        who += ")"
        if eliminated:
            # Met-but-dead leaders stay in the roster so others can refer
            # to them in past tense; they cannot speak or be addressed.
            roster_lines.append("- " + who + " -- ELIMINATED (can be referenced "
                                "in past tense; cannot speak or be addressed)")
        else:
            suffix = "toward you: " + attitude
            if at_war:
                suffix += ", at war with you"
            # Tier 1 extension: append "you toward them: X" when present.
            # Helps the LLM ground the speaker's own posture.
            spk_att = (entry.get("speaker_attitude_toward") or "").strip()
            if spk_att:
                suffix += "; you toward them: " + spk_att
            roster_lines.append("- " + who + " -- " + suffix)
            # Tier 1 extension: per-leader stats line. Skipped when none
            # of the optional scalars are present (old room_state shape).
            stats = _format_leader_stats(entry)
            if stats:
                roster_lines.append("  " + stats)
            # Tier 1 extension: memories the SPEAKER holds about this
            # leader. Only emitted when non-empty. The phrasing assumes
            # the memory is something the LEADER did to the SPEAKER --
            # the daemon's humanizer maps the enum names accordingly.
            grudges = _humanize_memories(entry.get("memories_vs_speaker"))
            if grudges:
                roster_lines.append("  Your memory of them: " + "; ".join(grudges))
        if len(roster_lines) >= 64:
            break

    rel_lines: list[str] = []
    if relations:
        # Tier 1b extension: prioritize relations with structural state
        # (wars, def-pacts, open borders, memories, strong attitudes) over
        # bland Cautious/Pleased pairs so the 12-cap surfaces interesting
        # context first. Falls back to original order for plain entries.
        def _rel_priority(r: dict) -> int:
            if not isinstance(r, dict):
                return 9
            if bool(r.get("at_war")):
                return 0
            if bool(r.get("has_defensive_pact")):
                return 1
            if bool(r.get("has_open_borders")):
                return 2
            mems = r.get("memories")
            if isinstance(mems, list) and mems:
                return 3
            att = (r.get("attitude") or "").strip()
            if att in ("Furious", "Friendly"):
                return 4
            return 5

        relations_sorted = sorted(
            [r for r in relations if isinstance(r, dict)],
            key=_rel_priority,
        )
        for rel in relations_sorted[:24]:
            if not isinstance(rel, dict):
                continue
            try:
                fp = int(rel.get("from_pid", -1))
                tp = int(rel.get("to_pid", -1))
            except (TypeError, ValueError):
                continue
            fname = pid_to_name.get(fp, "")
            tname = pid_to_name.get(tp, "")
            if not fname or not tname:
                continue
            att = (rel.get("attitude") or "").strip() or "Cautious"
            war = bool(rel.get("at_war"))
            # Preserve the original "(at war)" suffix for legacy
            # consumers / tests; append the duration only when present
            # and >0 so we don't render misleading "(0t)" for new wars.
            tail = ""
            if war:
                tail = " (at war"
                try:
                    wt = int(rel.get("at_war_turns", 0))
                except (TypeError, ValueError):
                    wt = 0
                if wt > 0:
                    tail += " " + str(wt) + "t"
                tail += ")"
            extras: list[str] = []
            if bool(rel.get("has_defensive_pact")):
                extras.append("defensive pact")
            if bool(rel.get("has_open_borders")):
                extras.append("open borders")
            mems_phr = _humanize_memories(rel.get("memories"))
            if mems_phr:
                extras.append("grudges: " + "; ".join(mems_phr))
            extras_str = (", " + ", ".join(extras)) if extras else ""
            rel_lines.append("- " + fname + " -> " + tname + ": " + att
                             + tail + extras_str)
            if len(rel_lines) >= 12:
                break

    speaker_display = (speaker_leader or "").strip() or "you"
    war_pairs: list[tuple[str, str]] = []
    seen_pairs: set[frozenset] = set()
    eliminated_pids: set[int] = set()
    for entry in roster:
        if not isinstance(entry, dict):
            continue
        if bool(entry.get("eliminated")):
            try:
                eliminated_pids.add(int(entry.get("player_id", -1)))
            except (TypeError, ValueError):
                pass
    for entry in roster:
        if not isinstance(entry, dict):
            continue
        # Eliminated leaders cannot be currently at war (death ends wars).
        if bool(entry.get("eliminated")):
            continue
        if not bool(entry.get("at_war_with_speaker")):
            continue
        try:
            if int(entry.get("player_id", -1)) == int(speaker_id):
                continue
        except (TypeError, ValueError):
            pass
        opp = (entry.get("leader_name") or "").strip()
        if not opp:
            continue
        key = frozenset([speaker_display, opp])
        if key in seen_pairs:
            continue
        seen_pairs.add(key)
        war_pairs.append((speaker_display, opp))
    for rel in relations:
        if not isinstance(rel, dict):
            continue
        if not bool(rel.get("at_war")):
            continue
        try:
            fp = int(rel.get("from_pid", -1))
            tp = int(rel.get("to_pid", -1))
        except (TypeError, ValueError):
            continue
        # Skip relations referencing eliminated leaders.
        if fp in eliminated_pids or tp in eliminated_pids:
            continue
        fname = pid_to_name.get(fp, "")
        tname = pid_to_name.get(tp, "")
        if not fname or not tname or fname == tname:
            continue
        a, b = sorted([fname, tname])
        key = frozenset([a, b])
        if key in seen_pairs:
            continue
        seen_pairs.add(key)
        war_pairs.append((a, b))

    parts: list[str] = []
    if roster_lines:
        parts.append("ROOM (other leaders present, attitudes are how they feel toward "
                     + speaker_display + "):\n" + "\n".join(roster_lines))
    if war_pairs:
        war_lines = ["- " + a + " <-> " + b for (a, b) in war_pairs[:16]]
        parts.append("ACTIVE WARS THIS TURN (live diplomatic state, AUTHORITATIVE -- "
                     "if a war is NOT on this list it has ENDED via peace treaty, "
                     "regardless of what earlier transcript lines say):\n"
                     + "\n".join(war_lines))
    else:
        parts.append("ACTIVE WARS THIS TURN: none. Every leader listed above is "
                     "currently AT PEACE with " + speaker_display + " and with each other. "
                     "If earlier transcript lines reference a war involving any of them, "
                     "that war has since ended -- treat the current peace as authoritative.")
    if rel_lines:
        parts.append("RELATIONS (AI-to-AI attitudes among the others):\n" + "\n".join(rel_lines))
    parts.append("Use these attitudes to color HOW you reply -- a Furious rival should "
                 "rip into a Friendly ally; a Pleased ally might back you up. "
                 "Mention names ONLY from the roster above; NEVER invent or name "
                 "any leader not on this list -- they do not exist in this "
                 "conversation. Eliminated leaders may be referenced in past tense "
                 "but cannot speak or be addressed in the present. "
                 "Defer to the ACTIVE WARS list above when describing current "
                 "diplomatic state; older transcript references to war or peace may be stale.")
    return "\n\n".join(parts) + "\n\n"


def build_chat_reply_system(*, speaker_leader: str, speaker_civ: str,
                            latest_typer_name: str = "",
                            other_humans_in_thread: list | None = None,
                            chain_reply: bool = False,
                            prior_leader_speaker_name: str = "",
                            target_human_name: str = "",
                            room_state: dict | None = None) -> str:
    """Format the SYSTEM_CHAT_REPLY system prompt for one conversation.

    `latest_typer_name` is the most recent human typer (preferred). For
    back-compat, `target_human_name` is accepted as a fallback when no
    typer info is available (SP single-human path that hasn't been
    updated yet).

    When `chain_reply` is True, returns the chain-flavored variant: a
    different system prompt directing the leader to reply to another
    AI leader (named by `prior_leader_speaker_name`) rather than to a
    human.

    `room_state`, when provided, is rendered as a ROSTER + RELATIONS
    preface block before the standard system text so the model knows
    who else is in the room and how everyone feels.
    """
    preface = _format_room_state_block(room_state, speaker_leader)
    if chain_reply:
        return preface + SYSTEM_CHAT_REPLY_CHAIN.format(
            speaker_leader=speaker_leader or "Anonymous",
            speaker_civ=speaker_civ or "their civilization",
            prior_leader_speaker_name=(prior_leader_speaker_name or "another leader"),
        )
    typer = latest_typer_name or target_human_name or "the visitor"
    others = list(other_humans_in_thread or [])
    others = [n for n in others if n and n != typer]
    if others:
        if len(others) == 1:
            other_clause = (
                "Another human, " + others[0] + ", has also been in this thread. "
            )
        else:
            joined = ", ".join(others[:-1]) + " and " + others[-1]
            other_clause = (
                "Other humans -- " + joined + " -- have also been in this thread. "
            )
    else:
        other_clause = ""
    return preface + SYSTEM_CHAT_REPLY.format(
        speaker_leader=speaker_leader or "Anonymous",
        speaker_civ=speaker_civ or "their civilization",
        latest_typer_name=typer,
        other_humans_clause=other_clause,
    )


def build_chat_reply_prompt(request: dict, history_messages: list,
                            *, latest_typer_name: str = "",
                            other_humans_in_thread: list | None = None,
                            chain_reply: bool = False,
                            prior_leader_speaker_name: str = "",
                            room_state: dict | None = None,
                            chatterbox_voices: set = None) -> tuple[str, list]:
    """Return (system_message, messages_list_for_llm) for a CHAT_REPLY call.

    history_messages is the full conversation so far as [{role, content}, ...].
    The latest entry should be the user message we're replying to. The
    returned messages_list is exactly what the chat-completions / responses
    API should see (no system message inside; system goes on the side).

    `latest_typer_name` (preferred) names the most recent human typer; if
    omitted we fall back to request.target.human_name for SP. The list
    `other_humans_in_thread` carries any additional MP typers seen so far.

    When `chain_reply` is True, the chain-flavored prompt is used and
    `prior_leader_speaker_name` names the AI leader who just spoke.

    `room_state`, when present, is rendered as a roster+relations preface
    block in the system prompt.
    """
    speaker = request.get("speaker") or {}
    target = request.get("target") or {}
    ctx = request.get("context") or {}
    typer = (latest_typer_name
             or ctx.get("from_human")
             or target.get("human_name")
             or target.get("leader_name")
             or "")
    sys_msg = build_chat_reply_system(
        speaker_leader=speaker.get("leader_name", ""),
        speaker_civ=speaker.get("civ_short_name", ""),
        latest_typer_name=typer,
        other_humans_in_thread=other_humans_in_thread,
        chain_reply=chain_reply,
        prior_leader_speaker_name=prior_leader_speaker_name,
        room_state=room_state,
    )
    # Paralinguistic tags for Chatterbox-voiced leaders
    if chatterbox_voices and _normalize_for_paralinguistic(speaker.get("leader_name", "")) in chatterbox_voices:
        sys_msg = apply_paralinguistic(sys_msg)
    return sys_msg, list(history_messages)


def _format_recent_lines_block(recent_lines: list, speaker_leader: str) -> str:
    """Render a leader's recent spoken lines as an 'avoid echoing yourself' block.

    Empty / non-list inputs render to empty string. The block is meant to be
    appended to the system prompt; it carries strong language about NOT
    reusing words, openers, or sentence shapes from the listed lines.
    """
    if not recent_lines:
        return ""
    # Defensive copy + clip to last 6. Strip empties.
    items = [str(s).strip() for s in recent_lines if s and str(s).strip()]
    items = items[-6:]
    if not items:
        return ""
    bullets = "\n".join("- " + s for s in items)
    leader = speaker_leader or "you"
    return (
        "\n\nAVOID ECHOING YOURSELF (important): your last few lines as "
        f"{leader} were:\n{bullets}\n\n"
        "Your new line MUST NOT reuse any DISTINCTIVE noun, verb, or "
        "adjective from those lines. Do NOT mirror their sentence shape, "
        "opener, or rhetorical mode. If the previous lines used 'X', "
        "'Y', 'Z' -- find different words. If they were short statements, "
        "try a question. If they opened with 'My', try a vocative. Make "
        "this line sound like it came from a different mood entirely."
    )


def build_single_line_prompt(request: dict, *, native_mode: bool = False,
                             speaker_native_lang: str = "",
                             recent_lines: list = None,
                             chatterbox_voices: set = None) -> tuple[str, str]:
    """Return (system_message, user_message) for a single-line directed/broadcast call.

    When native_mode is True AND speaker_native_lang is non-empty, the LLM
    returns a JSON object with both English (line) and native (line_native).
    Otherwise it returns a plain text line as before.

    `recent_lines` is the speaker's last few spoken lines across triggers,
    used to discourage self-repetition. None / empty means no block is
    appended; otherwise an AVOID-ECHOING-YOURSELF block is added to the
    system message.
    """
    trigger = request["trigger"]
    tmpl = TRIGGERS.get(trigger)
    if tmpl is None:
        raise ValueError(f"unknown trigger: {trigger}")

    speaker = request["speaker"]
    target = request.get("target") or {}
    ctx = request.get("context") or {}

    fmt = {
        "speaker_leader": speaker["leader_name"],
        "speaker_civ": speaker["civ_short_name"],
        "target_leader": target.get("leader_name", ""),
        "target_civ": target.get("civ_short_name", ""),
        "city": ctx.get("city", ""),
        "wonder": ctx.get("wonder", ""),
        "tech": ctx.get("tech", ""),
        "religion": ctx.get("religion", ""),
        "corporation": ctx.get("corporation", ""),
    }
    action = tmpl.action.format(**fmt)
    user_extra = tmpl.user_extra.format(**fmt)
    use_native = native_mode and bool(speaker_native_lang)
    if tmpl.mode == "broadcast":
        if use_native:
            system_msg = SYSTEM_BROADCAST_NATIVE.format(
                speaker_leader=fmt["speaker_leader"],
                speaker_civ=fmt["speaker_civ"],
                action=action,
                speaker_native_lang=speaker_native_lang,
            )
        else:
            system_msg = SYSTEM_BROADCAST.format(
                speaker_leader=fmt["speaker_leader"],
                speaker_civ=fmt["speaker_civ"],
                action=action,
            )
    else:
        if use_native:
            system_msg = SYSTEM_DIRECTED_NATIVE.format(
                speaker_leader=fmt["speaker_leader"],
                speaker_civ=fmt["speaker_civ"],
                target_leader=fmt["target_leader"],
                action=action,
                speaker_native_lang=speaker_native_lang,
            )
        else:
            system_msg = SYSTEM_DIRECTED.format(
                speaker_leader=fmt["speaker_leader"],
                speaker_civ=fmt["speaker_civ"],
                target_leader=fmt["target_leader"],
                action=action,
            )
        if target.get("is_barbarian"):
            system_msg += BARB_CONTEMPT_DIRECTIVE
        elif target.get("is_human") and target.get("human_name"):
            system_msg += HUMAN_PLAYER_DIRECTIVE.format(
                target_leader=fmt["target_leader"],
                target_human_name=target.get("human_name") or "",
            )
    # Append the speaker's recent-lines memory if we have any. This goes
    # after the targeting directives so the LLM sees those first and the
    # recent-lines callout last (closest to the actual generation).
    if recent_lines:
        system_msg += _format_recent_lines_block(recent_lines, fmt["speaker_leader"])
    # Paralinguistic tags for Chatterbox-voiced leaders
    if chatterbox_voices and _normalize_for_paralinguistic(fmt["speaker_leader"]) in chatterbox_voices:
        system_msg = apply_paralinguistic(system_msg)
    user_msg = USER_TEMPLATE.format(
        game_turn=request.get("game_turn", 0),
        era=ctx.get("era", "unknown"),
        extra=user_extra,
    )
    return system_msg, user_msg


def build_multi_turn_prompt(request: dict, *, native_mode: bool = False,
                            speaker_native_lang: str = "",
                            target_native_lang: str = "",
                            recent_lines: list = None,
                            target_recent_lines: list = None,
                            chatterbox_voices: set = None) -> tuple[str, str]:
    """Return (system_message, user_message) for a one-shot multi-line script call.

    When native_mode is True AND both leaders have a configured native lang,
    each generated line carries both 'line' (English) and 'line_native'
    (translated). Otherwise plain English lines as before.

    `recent_lines` / `target_recent_lines` are the speaker's and target's
    recent spoken lines (respectively); when present, an AVOID-ECHOING
    block is appended for each to discourage self-repetition in the
    generated exchange.
    """
    trigger = request["trigger"]
    tmpl = TRIGGERS.get(trigger)
    if tmpl is None:
        raise ValueError(f"unknown trigger: {trigger}")

    speaker = request["speaker"]
    target = request.get("target") or {}
    ctx = request.get("context") or {}
    n_lines = max(2, min(int(request.get("n_lines", 4)), 8))

    fmt = {
        "speaker_leader": speaker["leader_name"],
        "speaker_civ": speaker["civ_short_name"],
        "target_leader": target.get("leader_name", ""),
        "target_civ": target.get("civ_short_name", ""),
        "city": ctx.get("city", ""),
        "wonder": ctx.get("wonder", ""),
        "tech": ctx.get("tech", ""),
        "religion": ctx.get("religion", ""),
        "corporation": ctx.get("corporation", ""),
    }
    premise_action = tmpl.action.format(**fmt)
    premise = (
        f"Turn {request.get('game_turn', 0)}, {ctx.get('era', 'unknown')} era. "
        f"{fmt['speaker_leader']} of {fmt['speaker_civ']} just had this happen: {premise_action}. "
        f"Generate a {n_lines}-line back-and-forth exchange beginning with {fmt['speaker_leader']}'s opening barb. "
        f"Speakers strictly alternate: {fmt['speaker_leader']}, {fmt['target_leader']}, ..."
    )
    use_native = native_mode and bool(speaker_native_lang) and bool(target_native_lang)
    if use_native:
        system_msg = SYSTEM_MULTI_TURN_NATIVE.format(
            speaker_leader=fmt["speaker_leader"],
            target_leader=fmt["target_leader"],
            n_lines=n_lines,
            premise=premise,
            speaker_native_lang=speaker_native_lang,
            target_native_lang=target_native_lang,
        )
    else:
        system_msg = SYSTEM_MULTI_TURN.format(
            speaker_leader=fmt["speaker_leader"],
            target_leader=fmt["target_leader"],
            n_lines=n_lines,
            premise=premise,
        )
    if target.get("is_human") and target.get("human_name"):
        system_msg += HUMAN_PLAYER_DIRECTIVE.format(
            target_leader=fmt["target_leader"],
            target_human_name=target.get("human_name") or "",
        )
    if recent_lines:
        system_msg += _format_recent_lines_block(recent_lines, fmt["speaker_leader"])
    if target_recent_lines:
        system_msg += _format_recent_lines_block(target_recent_lines, fmt["target_leader"])
    # Paralinguistic tags — enable if either speaker or target uses Chatterbox
    if chatterbox_voices and (
        _normalize_for_paralinguistic(fmt["speaker_leader"]) in chatterbox_voices
        or _normalize_for_paralinguistic(fmt.get("target_leader", "")) in chatterbox_voices
    ):
        system_msg = apply_paralinguistic(system_msg)
    user_msg = "Generate the exchange now."
    return system_msg, user_msg
