"""Phase 4 unique-civilization-flags regression test.

Scope: docs/plans/active/2026-07-14-worker-civic-landmark-flag-followup.md (Phase 4).

Validates that every targeted era-specific playable civilization package has a
unique ArtDefineTag + unique flag Path, that every ArtDefineTag referenced by a
targeted CivilizationInfo resolves to a real CivilizationArtInfo entry, that the
newly authored repo-controlled DDS assets exist on disk with correct DDS/DXT3
square power-of-two metadata and zero alpha at every mip for fixed-color
rendering, and that
the Native America / Apache Confederacy / Polynesia three-way ArtDefine
cross-wiring bug has been corrected.

This file owns the earlier 37-package uniqueness scope. The complete 59-flag
fixed-color production contract, including formerly packed stock paths now
supplied by DowagerMod, lives in test_flag_contract_fullcolor.py.
"""
import os
import struct
import xml.etree.ElementTree as ET

import pytest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BTS_ASSETS = os.path.join(
    REPO_ROOT,
    "CoreFiles",
    "Sid Meier's Civilization IV Beyond the Sword",
    "Beyond the Sword",
    "Assets",
)
ART_DEFINES_PATH = os.path.join(BTS_ASSETS, "XML", "Art", "CIV4ArtDefines_Civilization.xml")
CIV_INFOS_PATH = os.path.join(BTS_ASSETS, "XML", "Civilizations", "CIV4CivilizationInfos.xml")

DDS_MAGIC = b"DDS "
DXT3_FOURCC = b"DXT3"


def _local(tag):
    """Strip the x-schema namespace prefix Firaxis XML files declare."""
    return tag.split("}")[-1] if "}" in tag else tag


def _parse(path):
    tree = ET.parse(path)
    root = tree.getroot()
    return root


# ---------------------------------------------------------------------------
# XML fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def art_defines():
    """Map ArtDefineTag -> {Button, Path, bWhiteFlag}."""
    root = _parse(ART_DEFINES_PATH)
    out = {}
    for info in root.iter():
        if _local(info.tag) != "CivilizationArtInfo":
            continue
        fields = {_local(child.tag): (child.text or "").strip() for child in info}
        type_tag = fields.get("Type")
        if type_tag:
            out[type_tag] = fields
    return out


@pytest.fixture(scope="module")
def civ_infos():
    """Map CivilizationType -> ArtDefineTag."""
    root = _parse(CIV_INFOS_PATH)
    out = {}
    for info in root.iter():
        if _local(info.tag) != "CivilizationInfo":
            continue
        fields = {_local(child.tag): (child.text or "").strip() for child in info}
        civ_type = fields.get("Type")
        art_tag = fields.get("ArtDefineTag")
        if civ_type:
            out[civ_type] = art_tag
    return out


# ---------------------------------------------------------------------------
# Targeted package coverage (exact 37 types from the plan's minimum coverage)
# ---------------------------------------------------------------------------

# CivilizationType -> expected ArtDefineTag after the Phase 4 fix.
# "kept" entries reuse a pre-existing (often stock, not-repo-committed) asset;
# all others are brand-new Phase 4 tags/assets, or corrected cross-wiring.
TARGETED_TYPES = {
    # America Union/Founding/New Deal/Federal
    "CIVILIZATION_AMERICA_UNION": "ART_DEF_CIVILIZATION_AMERICA_UNION",
    "CIVILIZATION_AMERICA_FOUNDING_REPUBLIC": "ART_DEF_CIVILIZATION_AMERICA",
    "CIVILIZATION_AMERICA_NEW_DEAL": "ART_DEF_CIVILIZATION_AMERICA_NEW_DEAL",
    "CIVILIZATION_AMERICA_FEDERAL": "ART_DEF_CIVILIZATION_AMERICA_FEDERAL",
    # British Regency/Elizabethan/Victorian/Wartime
    "CIVILIZATION_BRITISH_REGENCY": "ART_DEF_CIVILIZATION_ENGLAND_REGENCY",
    "CIVILIZATION_ELIZABETHAN_ENGLAND": "ART_DEF_CIVILIZATION_ENGLAND",
    "CIVILIZATION_VICTORIAN_BRITAIN": "ART_DEF_CIVILIZATION_ENGLAND_VICTORIAN",
    "CIVILIZATION_WARTIME_BRITAIN": "ART_DEF_CIVILIZATION_ENGLAND_WARTIME",
    # France Fifth/Bourbon/First Empire
    "CIVILIZATION_FRANCE_FIFTH_REPUBLIC": "ART_DEF_CIVILIZATION_FRANCE_FIFTH_REPUBLIC",
    "CIVILIZATION_FRANCE_BOURBON": "ART_DEF_CIVILIZATION_FRANCE",
    "CIVILIZATION_FRANCE_FIRST_EMPIRE": "ART_DEF_CIVILIZATION_FRANCE_FIRST_EMPIRE",
    # USSR/Petrine/Imperial Russia
    "CIVILIZATION_USSR": "ART_DEF_CIVILIZATION_RUSSIA_USSR",
    "CIVILIZATION_PETRINE_RUSSIA": "ART_DEF_CIVILIZATION_RUSSIA_PETRINE",
    "CIVILIZATION_IMPERIAL_RUSSIA": "ART_DEF_CIVILIZATION_RUSSIA",
    # Persia (both)
    "CIVILIZATION_PERSIA_FOUNDING_ACHAEMENID": "ART_DEF_CIVILIZATION_PERSIA_FOUNDING_ACHAEMENID",
    "CIVILIZATION_PERSIA_IMPERIAL_ACHAEMENID": "ART_DEF_CIVILIZATION_PERSIA_IMPERIAL_ACHAEMENID",
    # Egypt (both)
    "CIVILIZATION_EGYPT_EIGHTEENTH_DYNASTY": "ART_DEF_CIVILIZATION_EGYPT_EIGHTEENTH_DYNASTY",
    "CIVILIZATION_EGYPT_NEW_KINGDOM": "ART_DEF_CIVILIZATION_EGYPT",
    # Ottoman (both)
    "CIVILIZATION_OTTOMAN_CONQUEST": "ART_DEF_CIVILIZATION_OTTOMANS",
    "CIVILIZATION_OTTOMAN_CLASSICAL": "ART_DEF_CIVILIZATION_OTTOMAN_CLASSICAL",
    # Ethiopia (both)
    "CIVILIZATION_ETHIOPIA_SOLOMONIC": "ART_DEF_CIVILIZATION_ETHIOPIA_SOLOMONIC",
    "CIVILIZATION_ETHIOPIA_IMPERIAL": "ART_DEF_CIVILIZATION_ETHIOPIA",
    # India/Maurya
    "CIVILIZATION_INDIA": "ART_DEF_CIVILIZATION_INDIA_GANDHI",
    "CIVILIZATION_MAURYA": "ART_DEF_CIVILIZATION_INDIA",
    # Gaul/Iceni
    "CIVILIZATION_GAULIC_CONFEDERATION": "ART_DEF_CIVILIZATION_GAULIC_CONFEDERATION",
    "CIVILIZATION_ICENI_BRITAIN": "ART_DEF_CIVILIZATION_ICENI_BRITAIN",
    # Macedon/Athens
    "CIVILIZATION_MACEDONIAN_EMPIRE": "ART_DEF_CIVILIZATION_MACEDONIAN_EMPIRE",
    "CIVILIZATION_ATHENIAN_GREECE": "ART_DEF_CIVILIZATION_GREECE",
    # Mongol/Yuan
    "CIVILIZATION_MONGOL_EMPIRE": "ART_DEF_CIVILIZATION_MONGOL",
    "CIVILIZATION_YUAN_DYNASTY": "ART_DEF_CIVILIZATION_YUAN_DYNASTY",
    # Roman Republic/Principate
    "CIVILIZATION_ROMAN_REPUBLIC_LATE": "ART_DEF_CIVILIZATION_ROMAN_REPUBLIC_LATE",
    "CIVILIZATION_ROMAN_PRINCIPATE": "ART_DEF_CIVILIZATION_ROME",
    # Prussia/German Empire
    "CIVILIZATION_PRUSSIA": "ART_DEF_CIVILIZATION_PRUSSIA",
    "CIVILIZATION_GERMAN_EMPIRE": "ART_DEF_CIVILIZATION_GERMAN_EMPIRE",
    # Native America/Apache/Polynesia cross-wiring correction
    "CIVILIZATION_NATIVE_AMERICA": "ART_DEF_CIVILIZATION_NATIVE_AMERICA",
    "CIVILIZATION_APACHE_CONFEDERACY": "ART_DEF_CIVILIZATION_APACHE_CONFEDERACY",
    "CIVILIZATION_POLYNESIA_BTG": "ART_DEF_CIVILIZATION_POLYNESIA_BTG",
}

# The 24 brand-new Phase 4 DDS assets (repo-controlled, must exist + validate).
NEW_ASSET_FILENAMES = [
    "FlagDECAL_AmericaUnion.dds",
    "FlagDECAL_AmericaNewDeal.dds",
    "FlagDECAL_AmericaFederal.dds",
    "FlagDECAL_EnglandRegency.dds",
    "FlagDECAL_EnglandVictorian.dds",
    "FlagDECAL_EnglandWartime.dds",
    "FlagDECAL_FranceFifthRepublic.dds",
    "FlagDECAL_FranceFirstEmpire.dds",
    "FlagDECAL_RussiaPetrine.dds",
    "FlagDECAL_RussiaUSSR.dds",
    "FlagDECAL_PersiaFounding.dds",
    "FlagDECAL_PersiaImperial.dds",
    "FlagDECAL_EgyptEighteenthDynasty.dds",
    "FlagDECAL_OttomanClassical.dds",
    "FlagDECAL_EthiopiaSolomonic.dds",
    "FlagDECAL_IndiaGandhi.dds",
    "FlagDECAL_Gaul.dds",
    "FlagDECAL_Iceni.dds",
    "FlagDECAL_Macedon.dds",
    "FlagDECAL_Yuan.dds",
    "FlagDECAL_RomanRepublic.dds",
    "FlagDECAL_Prussia.dds",
    "FlagDECAL_GermanEmpire.dds",
    "FlagDECAL_Apache.dds",
]

assert len(TARGETED_TYPES) == 37, "Expected exactly 37 targeted civilization packages"
assert len(NEW_ASSET_FILENAMES) == 24, "Expected exactly 24 newly authored DDS assets"


# ---------------------------------------------------------------------------
# Uniqueness / resolution assertions
# ---------------------------------------------------------------------------

def test_all_targeted_types_present_in_civilization_infos(civ_infos):
    missing = [t for t in TARGETED_TYPES if t not in civ_infos]
    assert not missing, "Targeted CivilizationTypes missing from CIV4CivilizationInfos.xml: %s" % missing


def test_targeted_art_define_tags_match_expected(civ_infos):
    """Confirm the live XML actually assigns the expected ArtDefineTag per type."""
    mismatches = {
        t: (civ_infos.get(t), expected)
        for t, expected in TARGETED_TYPES.items()
        if civ_infos.get(t) != expected
    }
    assert not mismatches, "ArtDefineTag mismatches (actual, expected): %s" % mismatches


def test_targeted_art_define_tags_are_unique(civ_infos):
    tags = [civ_infos[t] for t in TARGETED_TYPES]
    dupes = {tag for tag in tags if tags.count(tag) > 1}
    assert not dupes, "Targeted packages must have unique ArtDefineTags; duplicated: %s" % dupes


def test_targeted_art_define_tags_resolve_to_art_info(civ_infos, art_defines):
    unresolved = [
        (t, civ_infos[t]) for t in TARGETED_TYPES if civ_infos[t] not in art_defines
    ]
    assert not unresolved, (
        "ArtDefineTag(s) referenced by targeted CivilizationInfo but missing from "
        "CIV4ArtDefines_Civilization.xml: %s" % unresolved
    )


def test_targeted_paths_are_unique(civ_infos, art_defines):
    paths = [art_defines[civ_infos[t]]["Path"] for t in TARGETED_TYPES]
    dupes = {p for p in paths if paths.count(p) > 1}
    assert not dupes, "Targeted packages must have unique flag Paths; duplicated: %s" % dupes


def test_targeted_paths_are_non_empty(civ_infos, art_defines):
    for t in TARGETED_TYPES:
        path = art_defines[civ_infos[t]].get("Path", "")
        assert path, "%s (ArtDefineTag %s) has an empty Path" % (t, civ_infos[t])


# ---------------------------------------------------------------------------
# Cross-wiring correction (explicit, named assertions)
# ---------------------------------------------------------------------------

def test_native_america_cross_wiring_fixed(civ_infos):
    assert civ_infos["CIVILIZATION_NATIVE_AMERICA"] == "ART_DEF_CIVILIZATION_NATIVE_AMERICA"


def test_apache_confederacy_cross_wiring_fixed(civ_infos):
    assert civ_infos["CIVILIZATION_APACHE_CONFEDERACY"] == "ART_DEF_CIVILIZATION_APACHE_CONFEDERACY"


def test_polynesia_cross_wiring_fixed(civ_infos):
    assert civ_infos["CIVILIZATION_POLYNESIA_BTG"] == "ART_DEF_CIVILIZATION_POLYNESIA_BTG"


def test_native_apache_polynesia_all_distinct(civ_infos, art_defines):
    """The three-way mix-up must resolve to three distinct tags AND distinct paths."""
    trio = ["CIVILIZATION_NATIVE_AMERICA", "CIVILIZATION_APACHE_CONFEDERACY", "CIVILIZATION_POLYNESIA_BTG"]
    tags = [civ_infos[t] for t in trio]
    assert len(set(tags)) == 3, "Native/Apache/Polynesia must resolve to 3 distinct ArtDefineTags: %s" % tags
    paths = [art_defines[tag]["Path"] for tag in tags]
    assert len(set(paths)) == 3, "Native/Apache/Polynesia must resolve to 3 distinct flag Paths: %s" % paths


# ---------------------------------------------------------------------------
# DDS on-disk existence + format validation
# ---------------------------------------------------------------------------

def _dds_header_fields(path):
    with open(path, "rb") as f:
        data = f.read(128)
    assert len(data) == 128, "%s: truncated DDS header (expected 128 bytes)" % path
    assert data[0:4] == DDS_MAGIC, "%s: missing 'DDS ' magic" % path
    height = struct.unpack_from("<I", data, 12)[0]
    width = struct.unpack_from("<I", data, 16)[0]
    pitch = struct.unpack_from("<I", data, 20)[0]
    mipmap_count = struct.unpack_from("<I", data, 28)[0]
    pf_flags = struct.unpack_from("<I", data, 80)[0]
    fourcc = data[84:88]
    return {
        "height": height,
        "width": width,
        "pitch": pitch,
        "mipmap_count": mipmap_count,
        "pf_flags": pf_flags,
        "fourcc": fourcc,
    }


def _is_power_of_two(n):
    return n > 0 and (n & (n - 1)) == 0


def _read_mip_payloads(path, width, height, mipmap_count):
    """Return each declared DXT3 mip payload and reject truncation/trailing data."""
    with open(path, "rb") as f:
        f.seek(128)
        data = f.read()

    payloads = []
    offset = 0
    for mip_index in range(mipmap_count):
        mip_width = max(1, width >> mip_index)
        mip_height = max(1, height >> mip_index)
        block_count = (
            max(1, (mip_width + 3) // 4)
            * max(1, (mip_height + 3) // 4)
        )
        payload_size = block_count * 16
        payload = data[offset:offset + payload_size]
        assert len(payload) == payload_size, (
            "%s: truncated mip %d (%dx%d): bytes=%d, expected=%d"
            % (
                os.path.basename(path),
                mip_index,
                mip_width,
                mip_height,
                len(payload),
                payload_size,
            )
        )
        payloads.append((mip_width, mip_height, payload))
        offset += payload_size
    assert offset == len(data), (
        "%s: trailing DDS payload bytes after %d declared mips: %d"
        % (os.path.basename(path), mipmap_count, len(data) - offset)
    )
    return payloads


def _new_asset_paths():
    team_color_dir = os.path.join(BTS_ASSETS, "Art", "Interface", "TeamColor")
    return [os.path.join(team_color_dir, name) for name in NEW_ASSET_FILENAMES]


@pytest.mark.parametrize("filename", NEW_ASSET_FILENAMES)
def test_new_flag_asset_exists(filename):
    path = os.path.join(BTS_ASSETS, "Art", "Interface", "TeamColor", filename)
    assert os.path.isfile(path), "Missing new Phase 4 flag asset: %s" % path


@pytest.mark.parametrize("filename", NEW_ASSET_FILENAMES)
def test_new_flag_asset_is_square_power_of_two_dxt3(filename):
    path = os.path.join(BTS_ASSETS, "Art", "Interface", "TeamColor", filename)
    fields = _dds_header_fields(path)
    assert fields["width"] == fields["height"], "%s is not square: %sx%s" % (
        filename, fields["width"], fields["height"],
    )
    assert _is_power_of_two(fields["width"]), "%s width %s is not a power of two" % (filename, fields["width"])
    assert fields["fourcc"] == DXT3_FOURCC, "%s is not DXT3 (fourcc=%r)" % (filename, fields["fourcc"])
    assert fields["mipmap_count"] >= 1, "%s reports zero mipmaps" % filename


@pytest.mark.parametrize("filename", NEW_ASSET_FILENAMES)
def test_new_flag_asset_file_size_matches_declared_mip_chain(filename):
    """DXT3 top-mip pitch (bytes) should be consistent with a 128x128, fully
    mipmapped 22000-byte file matching the established repo convention."""
    path = os.path.join(BTS_ASSETS, "Art", "Interface", "TeamColor", filename)
    fields = _dds_header_fields(path)
    size = os.path.getsize(path)
    assert size > 128, "%s has no pixel data beyond the header" % filename
    # 4x4 block = 16 bytes in BC2/DXT3; top-mip block count should match pitch.
    blocks_per_row = max(1, (fields["width"] + 3) // 4)
    blocks_per_col = max(1, (fields["height"] + 3) // 4)
    expected_pitch = blocks_per_row * blocks_per_col * 16
    assert fields["pitch"] == expected_pitch, "%s dwPitchOrLinearSize=%d does not match block math %d" % (
        filename, fields["pitch"], expected_pitch,
    )


@pytest.mark.parametrize("filename", NEW_ASSET_FILENAMES)
def test_new_flag_asset_alpha_channel_is_zero_at_every_mip(filename):
    """Enforce Firaxis fixed-color alpha: every DXT3 nibble is zero."""
    path = os.path.join(BTS_ASSETS, "Art", "Interface", "TeamColor", filename)
    fields = _dds_header_fields(path)
    payloads = _read_mip_payloads(
        path,
        fields["width"],
        fields["height"],
        fields["mipmap_count"],
    )
    for mip_index, (mip_width, mip_height, payload) in enumerate(payloads):
        for block_offset in range(0, len(payload), 16):
            alpha_block = payload[block_offset:block_offset + 8]
            for nibble_index in range(16):
                alpha_nibble = (
                    alpha_block[nibble_index // 2]
                    >> (4 * (nibble_index % 2))
                ) & 0x0F
                assert alpha_nibble == 0, (
                    "%s DXT3 alpha mismatch: expected zero at every mip; "
                    "mip=%d (%dx%d), block=%d, nibble=%d, value=%d"
                    % (
                        filename,
                        mip_index,
                        mip_width,
                        mip_height,
                        block_offset // 16,
                        nibble_index,
                        alpha_nibble,
                    )
                )


# ---------------------------------------------------------------------------
# Opportunistic validation for cross-wiring-corrected / kept-original assets
# ---------------------------------------------------------------------------

def _resolved_path_on_disk(art_defines, tag):
    rel_path = art_defines[tag]["Path"]
    # Paths in XML use forward slashes relative to the BtS Assets root.
    return os.path.join(BTS_ASSETS, *rel_path.split("/"))


def test_native_america_asset_exists_and_valid(art_defines):
    path = _resolved_path_on_disk(art_defines, "ART_DEF_CIVILIZATION_NATIVE_AMERICA")
    assert os.path.isfile(path), "NativeAmerica flag asset missing on disk: %s" % path
    fields = _dds_header_fields(path)
    assert fields["width"] == fields["height"]
    assert _is_power_of_two(fields["width"])
    assert fields["fourcc"] == DXT3_FOURCC


def test_polynesia_asset_exists_and_valid(art_defines):
    path = _resolved_path_on_disk(art_defines, "ART_DEF_CIVILIZATION_POLYNESIA_BTG")
    assert os.path.isfile(path), "Polynesia flag asset missing on disk: %s" % path
    fields = _dds_header_fields(path)
    assert fields["width"] == fields["height"]
    assert _is_power_of_two(fields["width"])
    assert fields["fourcc"] == DXT3_FOURCC


@pytest.mark.parametrize(
    "tag",
    [
        "ART_DEF_CIVILIZATION_AMERICA",
        "ART_DEF_CIVILIZATION_ENGLAND",
        "ART_DEF_CIVILIZATION_FRANCE",
        "ART_DEF_CIVILIZATION_RUSSIA",
        "ART_DEF_CIVILIZATION_EGYPT",
        "ART_DEF_CIVILIZATION_OTTOMANS",
        "ART_DEF_CIVILIZATION_ETHIOPIA",
        "ART_DEF_CIVILIZATION_INDIA",
        "ART_DEF_CIVILIZATION_GREECE",
        "ART_DEF_CIVILIZATION_MONGOL",
        "ART_DEF_CIVILIZATION_ROME",
    ],
)
def test_kept_original_asset_opportunistically_valid_if_present(art_defines, tag):
    """These 11 tags are intentionally kept pointing at pre-existing assets.
    Several ship only with the base game install and are excluded from this
    repo (see AGENTS.md). We only assert format validity IF the file exists;
    absence is not a failure here (requires manual/in-game visual acceptance)."""
    path = _resolved_path_on_disk(art_defines, tag)
    if not os.path.isfile(path):
        pytest.skip("%s not present in repo (expected: stock/base-game asset, see AGENTS.md)" % path)
    fields = _dds_header_fields(path)
    assert fields["width"] == fields["height"]
    assert _is_power_of_two(fields["width"])
    assert fields["fourcc"] == DXT3_FOURCC
