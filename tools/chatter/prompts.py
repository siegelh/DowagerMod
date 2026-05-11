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


# ===== System prompt templates =====

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
    "- No real-world modern politics, no slurs, no profanity stronger than mild.\n"
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
    "- No real-world modern politics, no slurs, no profanity stronger than mild.\n"
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
    "- No real-world modern politics, no slurs, no profanity stronger than mild.\n\n"
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
    "- No real-world modern politics, no slurs, no profanity stronger than mild.\n\n"
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
    "- No real-world modern politics, no slurs.\n"
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
    "- No real-world modern politics, no slurs.\n"
    "- The English and native versions must match in meaning.\n"
    "- Output ONLY the JSON object. No markdown, no code fences."
)

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
    "- No real-world modern politics, no slurs, no profanity stronger than mild.\n"
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
    "- No real-world modern politics, no slurs, no profanity stronger than mild.\n"
    "- Output ONLY the JSON object. No markdown, no commentary, no code fences.\n\n"
    "EXAMPLE OUTPUT (exact JSON shape required, replying to {prior_leader_speaker_name}):\n"
    '  {{"line": "{prior_leader_speaker_name}, your tongue grows tiresome with each empire that buries you.", "tone": "cold"}}\n\n'
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
    for entry in roster[:14]:
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
            roster_lines.append("- " + who + " -- " + suffix)
        if len(roster_lines) >= 10:
            break

    rel_lines: list[str] = []
    if relations:
        for rel in relations[:24]:
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
            tail = " (at war)" if war else ""
            rel_lines.append("- " + fname + " -> " + tname + ": " + att + tail)
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
                            room_state: dict | None = None) -> tuple[str, list]:
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
    return sys_msg, list(history_messages)


def build_single_line_prompt(request: dict, *, native_mode: bool = False,
                             speaker_native_lang: str = "") -> tuple[str, str]:
    """Return (system_message, user_message) for a single-line directed/broadcast call.

    When native_mode is True AND speaker_native_lang is non-empty, the LLM
    returns a JSON object with both English (line) and native (line_native).
    Otherwise it returns a plain text line as before.
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
    user_msg = USER_TEMPLATE.format(
        game_turn=request.get("game_turn", 0),
        era=ctx.get("era", "unknown"),
        extra=user_extra,
    )
    return system_msg, user_msg


def build_multi_turn_prompt(request: dict, *, native_mode: bool = False,
                            speaker_native_lang: str = "",
                            target_native_lang: str = "") -> tuple[str, str]:
    """Return (system_message, user_message) for a one-shot multi-line script call.

    When native_mode is True AND both leaders have a configured native lang,
    each generated line carries both 'line' (English) and 'line_native'
    (translated). Otherwise plain English lines as before.
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
    user_msg = "Generate the exchange now."
    return system_msg, user_msg
