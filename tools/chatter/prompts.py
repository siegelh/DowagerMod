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
    "- Output exactly ONE sentence, no more than 25 words.\n"
    "- Witty, theatrical, slightly arch. In-character trash talk is welcome.\n"
    "- No real-world modern politics, no slurs, no profanity stronger than mild.\n"
    '- Stay in character. Do not refer to "the game" or "the player" or "Civilization IV".\n'
    "- No quotation marks around the line. No leader name prefix.\n"
    "- Output ONLY the line itself, nothing else."
)

SYSTEM_BROADCAST = (
    "You are {speaker_leader} of {speaker_civ}, a historical figure as portrayed in "
    "Sid Meier's Civilization IV. {action}.\n\n"
    "Speak in-character with period-appropriate flavor, proclaiming this to the world. "
    "This is a broadcast to all peoples and rulers, not a private message.\n\n"
    "Constraints:\n"
    "- Output exactly ONE sentence, no more than 25 words.\n"
    "- Theatrical, proud, in-character. Boast or proclaim as fits the moment.\n"
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
    "and \"line\" (their remark, ONE sentence, max 25 words).\n\n"
    "Constraints for every line:\n"
    "- Witty, theatrical, slightly arch. In-character trash talk is welcome.\n"
    '- Stay in character. No references to "the game" or "the player".\n'
    "- No quotation marks within the line. No leader name prefix inside the line.\n"
    "- Each leader's lines must respond to the prior speaker's line, escalating naturally.\n"
    "- No real-world modern politics, no slurs, no profanity stronger than mild.\n\n"
    "Output ONLY the JSON array. No markdown, no commentary, no code fences."
)

USER_TEMPLATE = "Game state: turn {game_turn}, {era} era.\n{extra}"


def build_single_line_prompt(request: dict) -> tuple[str, str]:
    """Return (system_message, user_message) for a single-line directed/broadcast call."""
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
    if tmpl.mode == "broadcast":
        system_msg = SYSTEM_BROADCAST.format(
            speaker_leader=fmt["speaker_leader"],
            speaker_civ=fmt["speaker_civ"],
            action=action,
        )
    else:
        system_msg = SYSTEM_DIRECTED.format(
            speaker_leader=fmt["speaker_leader"],
            speaker_civ=fmt["speaker_civ"],
            target_leader=fmt["target_leader"],
            action=action,
        )
    user_msg = USER_TEMPLATE.format(
        game_turn=request.get("game_turn", 0),
        era=ctx.get("era", "unknown"),
        extra=user_extra,
    )
    return system_msg, user_msg


def build_multi_turn_prompt(request: dict) -> tuple[str, str]:
    """Return (system_message, user_message) for a one-shot multi-line script call."""
    trigger = request["trigger"]
    tmpl = TRIGGERS.get(trigger)
    if tmpl is None:
        raise ValueError(f"unknown trigger: {trigger}")

    speaker = request["speaker"]
    target = request.get("target") or {}
    ctx = request.get("context") or {}
    n_lines = max(2, min(int(request.get("n_lines", 3)), 4))

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
    system_msg = SYSTEM_MULTI_TURN.format(
        speaker_leader=fmt["speaker_leader"],
        target_leader=fmt["target_leader"],
        n_lines=n_lines,
        premise=premise,
    )
    user_msg = "Generate the exchange now."
    return system_msg, user_msg
