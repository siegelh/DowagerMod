import json
from pathlib import Path

from tools.chatter.audit_leader_voices import LEADER_XML, list_leaders
from tools.chatter.leader_roster import LEADERS
from tools.chatter.voice_picker import VoicePicker, normalize_name


ROOT = Path(__file__).resolve().parents[3]
VOICE_JSON = ROOT / "tools" / "chatter" / "leader_voices.json"
EXPANSION_NAMES = [name for name, _ in LEADERS[-13:]]


def test_audit_resolves_expansion_display_names_from_text_xml():
    leaders = dict(list_leaders(ROOT / LEADER_XML))

    assert leaders["LEADER_EXP_DUSAN"] == "Stefan Dusan"
    assert leaders["LEADER_EXP_MATTHIAS"] == "Matthias Corvinus"
    assert leaders["LEADER_EXP_ZENOBIA"] == "Zenobia"


def test_all_expansion_leaders_have_explicit_voice_mappings():
    data = json.loads(VOICE_JSON.read_text(encoding="utf-8"))
    explicit = data["map"]

    missing = [
        name for name in EXPANSION_NAMES
        if normalize_name(name) not in explicit
    ]
    assert missing == []


def test_expansion_voice_mappings_resolve_without_fallback():
    picker = VoicePicker(json_path=VOICE_JSON)

    for name in EXPANSION_NAMES:
        key = normalize_name(name)
        expected = json.loads(VOICE_JSON.read_text(encoding="utf-8"))["map"][key]["voice"]
        assert picker.pick_voice(name) == expected


def test_zenobia_uses_explicit_female_syrian_voice():
    spec = VoicePicker(json_path=VOICE_JSON).pick_spec("Zenobia")

    assert spec.voice == "ar-SY-AmanyNeural"
    assert spec.locale == "ar-SY"
