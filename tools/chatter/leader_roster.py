"""Static BTS leader roster used by the CLI test harness.

This is a sidecar (py3) parallel of the game-side leader index that
CvLeaderChatter._build_leader_name_index() builds at runtime. It exists
so chat_test.py can resolve --leader fuzzy strings ("Louie" -> Louis XIV)
without needing the game running.

Voice mapping is NOT included here -- the daemon's voice_picker handles
that separately, keyed off leader_name. We just supply the roster of
{leader_name, civ_short_name} pairs for fuzzy resolution.

Source: vanilla BTS Civ4LeaderHeadInfos.xml (LeaderHead descriptions,
trimmed to the in-game display names). Not exhaustive of every mod
leader -- the game-side resolver uses live data and is always correct;
this static list is purely a CLI convenience.
"""
from __future__ import annotations

# (leader_name, civ_short_name)
LEADERS: tuple = (
    ("Asoka", "India"),
    ("Augustus Caesar", "Rome"),
    ("Bismarck", "Germany"),
    ("Boudica", "Celtia"),
    ("Brennus", "Celtia"),
    ("Catherine", "Russia"),
    ("Charlemagne", "Holy Roman Empire"),
    ("Churchill", "England"),
    ("Cyrus", "Persia"),
    ("Darius I", "Persia"),
    ("De Gaulle", "France"),
    ("Elizabeth", "England"),
    ("Frederick", "Germany"),
    ("Gandhi", "India"),
    ("Genghis Khan", "Mongolia"),
    ("Gilgamesh", "Sumeria"),
    ("Hammurabi", "Babylon"),
    ("Hannibal", "Carthage"),
    ("Hatshepsut", "Egypt"),
    ("Huayna Capac", "Inca"),
    ("Isabella", "Spain"),
    ("Joao II", "Portugal"),
    ("Julius Caesar", "Rome"),
    ("Justinian I", "Byzantium"),
    ("Kublai Khan", "Mongolia"),
    ("Lincoln", "America"),
    ("Louis XIV", "France"),
    ("Mansa Musa", "Mali"),
    ("Mao Zedong", "China"),
    ("Mehmed II", "Ottoman Empire"),
    ("Montezuma", "Aztec"),
    ("Napoleon", "France"),
    ("Nebuchadnezzar II", "Babylon"),
    ("Pacal II", "Maya"),
    ("Pericles", "Greece"),
    ("Peter", "Russia"),
    ("Qin Shi Huang", "China"),
    ("Ragnar", "Vikings"),
    ("Ramesses II", "Egypt"),
    ("Roosevelt", "America"),
    ("Saladin", "Arabia"),
    ("Shaka", "Zulu"),
    ("Sitting Bull", "Native America"),
    ("Stalin", "Russia"),
    ("Suleiman", "Ottoman Empire"),
    ("Suryavarman II", "Khmer"),
    ("Tokugawa", "Japan"),
    ("Victoria", "England"),
    ("Wang Kon", "Korea"),
    ("Washington", "America"),
    ("Willem van Oranje", "Netherlands"),
    ("Zara Yaqob", "Ethiopia"),
)


def all_leader_names() -> list:
    return [name for name, _ in LEADERS]


def civ_for_leader(leader_name: str) -> str:
    """Return the civ_short_name for a leader, or '' if not found."""
    target = (leader_name or "").strip().lower()
    for name, civ in LEADERS:
        if name.lower() == target:
            return civ
    return ""
