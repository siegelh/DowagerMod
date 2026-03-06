#!/usr/bin/env python3
"""
Generate and wire the Art Masterpieces system content.

This script:
1) pulls artwork metadata from Wikidata (paintings, sculptures, architecture),
2) selects 200 unique pieces across eras,
3) downloads and converts image thumbnails into Civ4 button icons,
4) writes generated XML/text/python payloads,
5) patches required XML hooks (bonuses/art defs/corp prereqs/unit ability/building trigger).
"""

from __future__ import annotations

import csv
import io
import re
import sys
import time
from collections import defaultdict, OrderedDict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Sequence
from xml.sax.saxutils import escape as xml_escape

import requests
from PIL import Image, ImageOps


REPO_ROOT = Path(__file__).resolve().parents[1]
ASSETS_ROOT = (
    REPO_ROOT
    / "CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets"
)
XML_ROOT = ASSETS_ROOT / "XML"

BONUS_INFOS_PATH = XML_ROOT / "Terrain/CIV4BonusInfos.xml"
BONUS_ART_DEFS_PATH = XML_ROOT / "Art/CIV4ArtDefines_Bonus.xml"
BUILDING_CLASS_INFOS_PATH = XML_ROOT / "Buildings/CIV4BuildingClassInfos.xml"
BUILDING_INFOS_PATH = XML_ROOT / "Buildings/CIV4BuildingInfos.xml"
UNIT_INFOS_PATH = XML_ROOT / "Units/CIV4UnitInfos.xml"
CORPORATION_INFOS_PATH = XML_ROOT / "GameInfo/CIV4CorporationInfo.xml"
TEXT_OUT_PATH = XML_ROOT / "Text/ZZZ_ART_Masterpieces_Text.xml"

PY_DATA_OUT_PATH = ASSETS_ROOT / "Python/CvArtMasterpieceData.py"
ICON_DIR = ASSETS_ROOT / "Art/Interface/Buttons/resources/ArtMasterpieces"
GALLERY_DIR = ASSETS_ROOT / "Art/Interface/ArtMasterpieces/Gallery"
CATALOG_CSV_PATH = REPO_ROOT / "docs/art_masterpiece_sources.csv"

SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"
HEADERS = {
    "Accept": "application/sparql-results+json",
    "User-Agent": "DowagerMod-ArtMasterpieceGenerator/1.0",
}

TARGET_COUNT = 200

ERA_ORDER = [
    "ANTIQUITY",
    "MEDIEVAL",
    "RENAISSANCE",
    "INDUSTRIAL",
    "MODERN",
    "CONTEMPORARY",
]

ERA_LABELS = {
    "ANTIQUITY": "Antiquity",
    "MEDIEVAL": "Medieval",
    "RENAISSANCE": "Renaissance",
    "INDUSTRIAL": "Industrial",
    "MODERN": "Modern",
    "CONTEMPORARY": "Contemporary",
}

ERA_TARGETS = OrderedDict(
    [
        ("ANTIQUITY", 24),
        ("MEDIEVAL", 12),
        ("RENAISSANCE", 48),
        ("INDUSTRIAL", 44),
        ("MODERN", 36),
        ("CONTEMPORARY", 36),
    ]
)

TYPE_LABELS = {
    "PAINTING": "painting",
    "SCULPTURE": "sculpture",
}

TYPE_CAPS = {
    "PAINTING": 120,
    "SCULPTURE": 120,
}

QUERY_SPEC = [
    ("Q3305213", "PAINTING", 520),
    ("Q860861", "SCULPTURE", 520),
]

RESAMPLING_LANCZOS = getattr(Image, "Resampling", Image).LANCZOS
ICON_SIZE = (64, 64)
GALLERY_SIZE = (420, 260)


@dataclass(frozen=True)
class Candidate:
    qid: str
    label: str
    year: int
    era: str
    art_type: str
    image_url: str
    item_url: str
    sitelinks: int


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _replace_or_insert_marker_block(
    text: str,
    begin_comment: str,
    end_comment: str,
    block_content: str,
    insert_before: str,
) -> str:
    begin = "<!-- {} -->".format(begin_comment)
    end = "<!-- {} -->".format(end_comment)
    wrapped = "{}\n{}\n{}".format(begin, block_content.rstrip(), end)

    if begin in text and end in text:
        pattern = re.compile(re.escape(begin) + r".*?" + re.escape(end), re.S)
        return pattern.sub(wrapped, text, count=1)

    idx = text.find(insert_before)
    if idx < 0:
        raise RuntimeError("Could not find insertion anchor '{}'".format(insert_before))
    return text[:idx] + wrapped + "\n" + text[idx:]


def _replace_tag_value(block: str, tag: str, value: str) -> str:
    pattern = re.compile(r"(<{0}>)(.*?)(</{0}>)".format(re.escape(tag)))
    if not pattern.search(block):
        raise RuntimeError("Tag '{}' not found in block".format(tag))
    return pattern.sub(lambda m: m.group(1) + value + m.group(3), block, count=1)


def _parse_year(raw: str) -> int | None:
    if not raw:
        return None
    m = re.match(r"^(-?\d+)", raw)
    if not m:
        return None
    try:
        return int(m.group(1))
    except ValueError:
        return None


def _era_from_year(year: int) -> str:
    if year <= 500:
        return "ANTIQUITY"
    if year <= 1400:
        return "MEDIEVAL"
    if year <= 1700:
        return "RENAISSANCE"
    if year <= 1900:
        return "INDUSTRIAL"
    if year <= 1970:
        return "MODERN"
    return "CONTEMPORARY"


def _query_candidates(instance_qid: str, art_type: str, limit: int) -> List[Candidate]:
    query = """
SELECT ?item ?itemLabel ?inception ?image ?sitelinks WHERE {
  ?item wdt:P31/wdt:P279* wd:%(instance)s ;
        wdt:P18 ?image ;
        wdt:P571 ?inception ;
        wikibase:sitelinks ?sitelinks .
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
ORDER BY DESC(?sitelinks)
LIMIT %(limit)d
""" % {
        "instance": instance_qid,
        "limit": limit,
    }

    resp = requests.get(
        SPARQL_ENDPOINT,
        params={"query": query, "format": "json"},
        headers=HEADERS,
        timeout=120,
    )
    resp.raise_for_status()
    payload = resp.json()
    rows = payload.get("results", {}).get("bindings", [])

    out: List[Candidate] = []
    for row in rows:
        label = row.get("itemLabel", {}).get("value", "").strip()
        if not label:
            continue
        item_url = row.get("item", {}).get("value", "").strip()
        image_url = row.get("image", {}).get("value", "").strip()
        inception = row.get("inception", {}).get("value", "").strip()
        sitelinks_raw = row.get("sitelinks", {}).get("value", "0").strip()
        year = _parse_year(inception)
        if not item_url or not image_url or year is None:
            continue
        qid = item_url.rsplit("/", 1)[-1]
        if not qid.startswith("Q"):
            continue
        try:
            sitelinks = int(float(sitelinks_raw))
        except ValueError:
            sitelinks = 0

        out.append(
            Candidate(
                qid=qid,
                label=label,
                year=year,
                era=_era_from_year(year),
                art_type=art_type,
                image_url=image_url,
                item_url=item_url,
                sitelinks=sitelinks,
            )
        )

    return out


def _query_candidates_with_retries(
    instance_qid: str, art_type: str, limit: int
) -> List[Candidate]:
    attempt_limits = [limit, max(120, limit // 2), max(80, limit // 4)]
    last_error: Exception | None = None
    for attempt_limit in attempt_limits:
        try:
            return _query_candidates(instance_qid, art_type, attempt_limit)
        except requests.RequestException as exc:
            last_error = exc
            print(
                "Query retry for {} (limit {}): {}".format(
                    art_type.lower(), attempt_limit, exc
                ),
                file=sys.stderr,
            )
            continue
    if last_error is not None:
        raise last_error
    return []


def _collect_candidates() -> List[Candidate]:
    all_rows: List[Candidate] = []
    for instance_qid, art_type, limit in QUERY_SPEC:
        rows = _query_candidates_with_retries(instance_qid, art_type, limit)
        print(
            "Fetched {:4d} {} candidates".format(len(rows), art_type.lower()),
            file=sys.stderr,
        )
        all_rows.extend(rows)

    # De-duplicate by QID, preferring higher sitelinks.
    best_by_qid: Dict[str, Candidate] = {}
    for row in all_rows:
        prev = best_by_qid.get(row.qid)
        if prev is None or row.sitelinks > prev.sitelinks:
            best_by_qid[row.qid] = row

    merged = list(best_by_qid.values())
    merged.sort(key=lambda c: (-c.sitelinks, c.year, c.label))
    print("Unique candidate pool: {}".format(len(merged)), file=sys.stderr)
    return merged


def _select_masterpieces(candidates: Sequence[Candidate], count: int) -> List[Candidate]:
    by_era: Dict[str, List[Candidate]] = defaultdict(list)
    for row in candidates:
        by_era[row.era].append(row)

    for era in ERA_ORDER:
        by_era[era].sort(key=lambda c: (-c.sitelinks, c.year, c.label))

    selected: List[Candidate] = []
    selected_qids = set()
    selected_names = set()
    type_counts = defaultdict(int)

    def try_add(row: Candidate) -> bool:
        key_name = row.label.strip().lower()
        if row.qid in selected_qids or key_name in selected_names:
            return False
        if type_counts[row.art_type] >= TYPE_CAPS.get(row.art_type, 999):
            return False
        selected.append(row)
        selected_qids.add(row.qid)
        selected_names.add(key_name)
        type_counts[row.art_type] += 1
        return True

    # Era targets first.
    for era, target in ERA_TARGETS.items():
        if len(selected) >= count:
            break
        added = 0
        for row in by_era.get(era, []):
            if len(selected) >= count or added >= target:
                break
            if try_add(row):
                added += 1
        print(
            "Selected {:3d} / {:3d} for {}".format(added, target, ERA_LABELS[era]),
            file=sys.stderr,
        )

    # Fill any remaining slots from global popularity.
    if len(selected) < count:
        for row in candidates:
            if len(selected) >= count:
                break
            try_add(row)

    if len(selected) < count:
        raise RuntimeError(
            "Could only select {} unique artworks; need {}".format(len(selected), count)
        )

    selected = selected[:count]
    selected.sort(
        key=lambda c: (
            ERA_ORDER.index(c.era),
            c.year,
            -c.sitelinks,
            c.label.lower(),
        )
    )
    return selected


def _thumbnail_url(raw_image_url: str, width: int | None = 256) -> str:
    if raw_image_url.startswith("http://"):
        raw_image_url = "https://" + raw_image_url[len("http://") :]
    if width is None:
        return raw_image_url
    sep = "&" if "?" in raw_image_url else "?"
    return "{}{}width={}".format(raw_image_url, sep, width)


def _download_art_assets(raw_image_url: str, icon_path: Path, gallery_path: Path) -> bool:
    primary_url = _thumbnail_url(raw_image_url, width=256)
    fallback_url = _thumbnail_url(raw_image_url, width=None)
    candidate_urls = [primary_url]
    if fallback_url != primary_url:
        candidate_urls.append(fallback_url)

    for url in candidate_urls:
        for attempt in range(4):
            try:
                resp = requests.get(url, headers=HEADERS, timeout=90)
                if resp.status_code == 200 and resp.content:
                    content_type = (resp.headers.get("content-type") or "").lower()
                    if not content_type.startswith("image/"):
                        return False
                    with Image.open(io.BytesIO(resp.content)) as img:
                        img = ImageOps.exif_transpose(img).convert("RGB")

                        icon = ImageOps.fit(
                            img,
                            ICON_SIZE,
                            method=RESAMPLING_LANCZOS,
                            centering=(0.5, 0.5),
                        )
                        gallery = ImageOps.fit(
                            img,
                            GALLERY_SIZE,
                            method=RESAMPLING_LANCZOS,
                            centering=(0.5, 0.5),
                        )

                        icon_path.parent.mkdir(parents=True, exist_ok=True)
                        gallery_path.parent.mkdir(parents=True, exist_ok=True)
                        icon.save(icon_path, format="TGA")
                        gallery.save(gallery_path, format="TGA")
                    return True

                if resp.status_code in (429, 502, 503, 504):
                    time.sleep(2.0 + attempt * 2.0)
                    continue
                break
            except requests.RequestException:
                time.sleep(1.5 + attempt * 1.2)
                continue
            except Exception:
                return False
    return False


def _bonus_block(bonus_type: str, text_tag: str, art_define: str) -> str:
    return (
        "\t\t<BonusInfo>\n"
        "\t\t\t<Type>{}</Type>\n"
        "\t\t\t<Description>{}</Description>\n"
        "\t\t\t<Civilopedia>{}_PEDIA</Civilopedia>\n"
        "\t\t\t<BonusClassType>BONUSCLASS_GENERAL</BonusClassType>\n"
        "\t\t\t<ArtDefineTag>{}</ArtDefineTag>\n"
        "\t\t\t<TechReveal>NONE</TechReveal>\n"
        "\t\t\t<TechCityTrade>NONE</TechCityTrade>\n"
        "\t\t\t<TechObsolete>NONE</TechObsolete>\n"
        "\t\t\t<YieldChanges/>\n"
        "\t\t\t<iAITradeModifier>20</iAITradeModifier>\n"
        "\t\t\t<iAIObjective>0</iAIObjective>\n"
        "\t\t\t<iHealth>0</iHealth>\n"
        "\t\t\t<iHappiness>1</iHappiness>\n"
        "\t\t\t<iPlacementOrder>-1</iPlacementOrder>\n"
        "\t\t\t<iConstAppearance>0</iConstAppearance>\n"
        "\t\t\t<iMinAreaSize>-1</iMinAreaSize>\n"
        "\t\t\t<iMinLatitude>0</iMinLatitude>\n"
        "\t\t\t<iMaxLatitude>90</iMaxLatitude>\n"
        "\t\t\t<Rands>\n"
        "\t\t\t\t<iRandApp1>0</iRandApp1>\n"
        "\t\t\t\t<iRandApp2>0</iRandApp2>\n"
        "\t\t\t\t<iRandApp3>0</iRandApp3>\n"
        "\t\t\t\t<iRandApp4>0</iRandApp4>\n"
        "\t\t\t</Rands>\n"
        "\t\t\t<iPlayer>0</iPlayer>\n"
        "\t\t\t<iTilesPer>0</iTilesPer>\n"
        "\t\t\t<iMinLandPercent>0</iMinLandPercent>\n"
        "\t\t\t<iUnique>0</iUnique>\n"
        "\t\t\t<iGroupRange>0</iGroupRange>\n"
        "\t\t\t<iGroupRand>0</iGroupRand>\n"
        "\t\t\t<bArea>0</bArea>\n"
        "\t\t\t<bHills>0</bHills>\n"
        "\t\t\t<bFlatlands>0</bFlatlands>\n"
        "\t\t\t<bNoRiverSide>0</bNoRiverSide>\n"
        "\t\t\t<bNormalize>0</bNormalize>\n"
        "\t\t\t<TerrainBooleans/>\n"
        "\t\t\t<FeatureBooleans/>\n"
        "\t\t\t<FeatureTerrainBooleans/>\n"
        "\t\t</BonusInfo>"
    ).format(bonus_type, text_tag, text_tag, art_define)


def _art_define_block(art_define: str, button_path: str) -> str:
    return (
        "\t\t<BonusArtInfo>\n"
        "\t\t\t<Type>{}</Type>\n"
        "\t\t\t<fScale>.7</fScale>\n"
        "\t\t\t<fInterfaceScale>1.0</fInterfaceScale>\n"
        "\t\t\t<NIF>Art/Terrain/Resources/Marble/Marble.nif</NIF>\n"
        "\t\t\t<KFM>Art/Terrain/Resources/Marble/Marble.kfm</KFM>\n"
        "\t\t\t<Button>{}</Button>\n"
        "\t\t\t<FontButtonIndex>5</FontButtonIndex>\n"
        "\t\t</BonusArtInfo>"
    ).format(art_define, button_path)


def _text_entries(rows: Sequence[Dict[str, str]]) -> str:
    lines: List[str] = []
    lines.append('<?xml version="1.0" encoding="utf-8"?>')
    lines.append('<Civ4GameText xmlns="http://www.firaxis.com">')
    lines.append("\t<TEXT><Tag>TXT_KEY_BUILDING_ART_MASTERPIECE_TRIGGER</Tag><English>Curate Masterpiece</English></TEXT>")
    lines.append(
        "\t<TEXT><Tag>TXT_KEY_BUILDING_ART_MASTERPIECE_TRIGGER_PEDIA</Tag><English>A hidden trigger used by Great Artists to create unique Masterpiece resources.</English></TEXT>"
    )
    lines.append(
        "\t<TEXT><Tag>TXT_KEY_BUILDING_ART_MASTERPIECE_TRIGGER_STRATEGY</Tag><English>Consumes a Great Artist to add a globally unique Masterpiece resource to this city.</English></TEXT>"
    )
    lines.append(
        "\t<TEXT><Tag>TXT_KEY_ART_MASTERPIECE_SET_BONUS_HELP</Tag><English>Art Curation Bonus: +1 global happiness for each era with at least 3 owned Masterpieces and each art type with at least 4 owned Masterpieces.</English></TEXT>"
    )

    for row in rows:
        text_tag = row["text_tag"]
        title = xml_escape(row["title"])
        year_label = row["year_label"]
        era_label = ERA_LABELS[row["era"]]
        type_label = TYPE_LABELS[row["art_type"]]
        pedia = "{} ({}), a {} from the {} era.".format(
            xml_escape(row["title"]),
            xml_escape(year_label),
            xml_escape(type_label),
            xml_escape(era_label),
        )
        lines.append(
            "\t<TEXT><Tag>{}</Tag><English>{}</English></TEXT>".format(text_tag, title)
        )
        lines.append(
            "\t<TEXT><Tag>{}_PEDIA</Tag><English>{}</English></TEXT>".format(
                text_tag, pedia
            )
        )

    lines.append("</Civ4GameText>")
    return "\n".join(lines) + "\n"


def _python_data_content(rows: Sequence[Dict[str, str]]) -> str:
    lines: List[str] = []
    lines.append("# Auto-generated by tools/generate_art_masterpieces.py")
    lines.append("")
    lines.append("ART_ERA_ORDER = {}".format(repr(ERA_ORDER)))
    lines.append("")
    lines.append("ART_MASTERPIECES = [")
    for row in rows:
        lines.append(
            "    ({!r}, {!r}, {!r}, {!r}, {!r}),".format(
                row["bonus_type"],
                row["era"],
                row["art_type"],
                row["button_path"],
                row["gallery_path"],
            )
        )
    lines.append("]")
    lines.append("")
    lines.append("ART_BONUS_TYPES = [row[0] for row in ART_MASTERPIECES]")
    lines.append("ART_BUTTON_BY_BONUS = dict([(row[0], row[3]) for row in ART_MASTERPIECES])")
    lines.append("ART_GALLERY_BY_BONUS = dict([(row[0], row[4]) for row in ART_MASTERPIECES])")
    lines.append("")
    lines.append("ART_BY_ERA = {}")
    lines.append("ART_BY_TYPE = {}")
    lines.append("for _bonus, _era, _art_type, _button, _gallery in ART_MASTERPIECES:")
    lines.append("    ART_BY_ERA.setdefault(_era, []).append(_bonus)")
    lines.append("    ART_BY_TYPE.setdefault(_art_type, []).append(_bonus)")
    lines.append("")
    return "\n".join(lines) + "\n"


def _build_connected_bonus_prereq_block(bonus_types: Sequence[str]) -> str:
    bonus_lines = ["\t\t\t\t\t\t<BonusType>{}</BonusType>".format(b) for b in bonus_types]
    return (
        "\t\t\t<LocalImprovementCountPrereqs/>\n"
        "\t\t\t<LocalBonusPrereqs/>\n"
        "\t\t\t<ConnectedBonusPrereqs>\n"
        "\t\t\t\t<ConnectedBonusPrereq>\n"
        "\t\t\t\t\t<BonusTypes>\n"
        "{}\n"
        "\t\t\t\t\t</BonusTypes>\n"
        "\t\t\t\t\t<iMinCount>5</iMinCount>\n"
        "\t\t\t\t</ConnectedBonusPrereq>\n"
        "\t\t\t</ConnectedBonusPrereqs>"
    ).format("\n".join(bonus_lines))


def _insert_or_update_trigger_building_class() -> None:
    text = _read_text(BUILDING_CLASS_INFOS_PATH)
    block = (
        "\t\t<BuildingClassInfo>\n"
        "\t\t\t<Type>BUILDINGCLASS_ART_MASTERPIECE_TRIGGER</Type>\n"
        "\t\t\t<Description>TXT_KEY_BUILDING_ART_MASTERPIECE_TRIGGER</Description>\n"
        "\t\t\t<iMaxGlobalInstances>-1</iMaxGlobalInstances>\n"
        "\t\t\t<iMaxTeamInstances>-1</iMaxTeamInstances>\n"
        "\t\t\t<iMaxPlayerInstances>-1</iMaxPlayerInstances>\n"
        "\t\t\t<iExtraPlayerInstances>0</iExtraPlayerInstances>\n"
        "\t\t\t<bNoLimit>0</bNoLimit>\n"
        "\t\t\t<bMonument>0</bMonument>\n"
        "\t\t\t<DefaultBuilding>BUILDING_ART_MASTERPIECE_TRIGGER</DefaultBuilding>\n"
        "\t\t\t<VictoryThresholds/>\n"
        "\t\t</BuildingClassInfo>"
    )
    updated = _replace_or_insert_marker_block(
        text,
        "ART_MASTERPIECE_BUILDINGCLASS_BEGIN",
        "ART_MASTERPIECE_BUILDINGCLASS_END",
        block,
        "\t</BuildingClassInfos>",
    )
    _write_text(BUILDING_CLASS_INFOS_PATH, updated)


def _insert_or_update_trigger_building_and_corp_prereq(bonus_types: Sequence[str]) -> None:
    text = _read_text(BUILDING_INFOS_PATH)

    # 1) Add trigger building entry (derived from CORPORATION_7 for schema safety).
    corp7_pattern = re.compile(
        r"(<BuildingInfo>\s*<BuildingClass>BUILDINGCLASS_CORPORATION_7</BuildingClass>.*?</BuildingInfo>)",
        re.S,
    )
    m = corp7_pattern.search(text)
    if not m:
        raise RuntimeError("Failed to locate BUILDING_CORPORATION_7 block")
    corp7_block = m.group(1)

    trigger_block = corp7_block
    trigger_block = trigger_block.replace(
        "<BuildingClass>BUILDINGCLASS_CORPORATION_7</BuildingClass>",
        "<BuildingClass>BUILDINGCLASS_ART_MASTERPIECE_TRIGGER</BuildingClass>",
    )
    trigger_block = trigger_block.replace(
        "<Type>BUILDING_CORPORATION_7</Type>",
        "<Type>BUILDING_ART_MASTERPIECE_TRIGGER</Type>",
    )
    trigger_block = trigger_block.replace(
        "<Description>TXT_KEY_CORPORATION_7</Description>",
        "<Description>TXT_KEY_BUILDING_ART_MASTERPIECE_TRIGGER</Description>",
    )
    trigger_block = trigger_block.replace(
        "<Civilopedia>TXT_KEY_CORPORATION_7_PEDIA</Civilopedia>",
        "<Civilopedia>TXT_KEY_BUILDING_ART_MASTERPIECE_TRIGGER_PEDIA</Civilopedia>",
    )
    trigger_block = trigger_block.replace(
        "<Strategy>TXT_KEY_BUILDING_CORPORATION_7_STRATEGY</Strategy>",
        "<Strategy>TXT_KEY_BUILDING_ART_MASTERPIECE_TRIGGER_STRATEGY</Strategy>",
    )
    trigger_block = _replace_tag_value(trigger_block, "FoundsCorporation", "NONE")
    trigger_block = _replace_tag_value(trigger_block, "iGreatPeopleRateChange", "0")
    trigger_block = _replace_tag_value(trigger_block, "bNeverCapture", "1")
    trigger_block = _replace_tag_value(trigger_block, "iConquestProb", "0")
    trigger_block = _replace_tag_value(trigger_block, "bNukeImmune", "0")
    trigger_block = _replace_tag_value(trigger_block, "iAsset", "0")
    trigger_block = re.sub(
        r"<TechTypes>.*?</TechTypes>",
        (
            "<TechTypes>\n"
            "\t\t\t\t<PrereqTech>NONE</PrereqTech>\n"
            "\t\t\t\t<PrereqTech>NONE</PrereqTech>\n"
            "\t\t\t\t<PrereqTech>NONE</PrereqTech>\n"
            "\t\t\t</TechTypes>"
        ),
        trigger_block,
        flags=re.S,
    )
    trigger_block = re.sub(
        r"<!-- ART_CORP7_CONNECTED_PREREQS_BEGIN -->.*?<!-- ART_CORP7_CONNECTED_PREREQS_END -->",
        (
            "\t\t\t<LocalImprovementCountPrereqs/>\n"
            "\t\t\t<LocalBonusPrereqs/>\n"
            "\t\t\t<ConnectedBonusPrereqs/>"
        ),
        trigger_block,
        flags=re.S,
    )

    updated = _replace_or_insert_marker_block(
        text,
        "ART_MASTERPIECE_BUILDINGINFO_BEGIN",
        "ART_MASTERPIECE_BUILDINGINFO_END",
        trigger_block,
        "\t</BuildingInfos>",
    )

    # 2) Activate corp7 founding and connect 5-distinct-art requirement.
    m2 = corp7_pattern.search(updated)
    if not m2:
        raise RuntimeError("Failed to locate BUILDING_CORPORATION_7 block after insertion")
    corp7_current = m2.group(1)
    corp7_new = _replace_tag_value(corp7_current, "FoundsCorporation", "CORPORATION_7")

    connected_block = _build_connected_bonus_prereq_block(bonus_types)
    corp7_new = _replace_or_insert_marker_block(
        corp7_new,
        "ART_CORP7_CONNECTED_PREREQS_BEGIN",
        "ART_CORP7_CONNECTED_PREREQS_END",
        connected_block,
        "\t\t\t<Flavors>",
    )

    updated = updated.replace(corp7_current, corp7_new, 1)
    _write_text(BUILDING_INFOS_PATH, updated)


def _patch_unit_artist_buildings() -> None:
    text = _read_text(UNIT_INFOS_PATH)
    unit_pattern = re.compile(
        r"(<UnitInfo>\s*<Class>UNITCLASS_ARTIST</Class>.*?<Type>UNIT_ARTIST</Type>.*?</UnitInfo>)",
        re.S,
    )
    m = unit_pattern.search(text)
    if not m:
        raise RuntimeError("Failed to locate UNIT_ARTIST block")

    unit_block = m.group(1)
    buildings_block = (
        "      <!-- ART_ARTIST_BUILDINGS_BEGIN -->\n"
        "      <Buildings>\n"
        "        <Building>\n"
        "          <BuildingType>BUILDING_ART_MASTERPIECE_TRIGGER</BuildingType>\n"
        "          <bBuilding>1</bBuilding>\n"
        "        </Building>\n"
        "        <Building>\n"
        "          <BuildingType>BUILDING_CORPORATION_7</BuildingType>\n"
        "          <bBuilding>1</bBuilding>\n"
        "        </Building>\n"
        "      </Buildings>\n"
        "      <!-- ART_ARTIST_BUILDINGS_END -->"
    )

    if "<!-- ART_ARTIST_BUILDINGS_BEGIN -->" in unit_block:
        unit_block_new = re.sub(
            r"<!-- ART_ARTIST_BUILDINGS_BEGIN -->.*?<!-- ART_ARTIST_BUILDINGS_END -->",
            buildings_block,
            unit_block,
            flags=re.S,
        )
    elif "<Buildings />" in unit_block:
        unit_block_new = unit_block.replace("<Buildings />", buildings_block, 1)
    else:
        unit_block_new = re.sub(
            r"<Buildings>.*?</Buildings>",
            buildings_block,
            unit_block,
            count=1,
            flags=re.S,
        )

    updated = text.replace(unit_block, unit_block_new, 1)
    _write_text(UNIT_INFOS_PATH, updated)


def _patch_corporation_7() -> None:
    text = _read_text(CORPORATION_INFOS_PATH)
    corp_pattern = re.compile(
        r"(<CorporationInfo>\s*<Type>CORPORATION_7</Type>.*?</CorporationInfo>)",
        re.S,
    )
    m = corp_pattern.search(text)
    if not m:
        raise RuntimeError("Failed to locate CORPORATION_7 block")

    block = m.group(1)
    block = _replace_tag_value(block, "TechPrereq", "TECH_CORPORATION")
    block = _replace_tag_value(block, "iSpreadFactor", "120")
    block = _replace_tag_value(block, "iSpreadCost", "70")
    block = _replace_tag_value(block, "iMaintenance", "120")
    block = _replace_tag_value(block, "iFoundingMinActiveBuildingClasses", "0")
    block = _replace_tag_value(block, "bCountDistinctPrereqBonusesOnly", "1")
    block = _replace_tag_value(block, "iMaxPrereqBonusCountPerType", "1")

    updated = text.replace(m.group(1), block, 1)
    _write_text(CORPORATION_INFOS_PATH, updated)


def main() -> int:
    reuse_catalog = "--reuse-catalog" in sys.argv
    force_redownload = "--force-redownload" in sys.argv

    rows: List[Dict[str, str]] = []
    if reuse_catalog and CATALOG_CSV_PATH.exists():
        with CATALOG_CSV_PATH.open("r", encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
        if len(rows) != TARGET_COUNT:
            raise RuntimeError(
                "--reuse-catalog expected {} rows but found {}".format(
                    TARGET_COUNT, len(rows)
                )
            )
        print("Reusing existing catalog rows: {}".format(len(rows)), file=sys.stderr)
        for row in rows:
            year = int(row["year"])
            row["year_label"] = "{} BCE".format(abs(year)) if year < 0 else str(year)
            idx = int(row["index"])
            row["bonus_type"] = "BONUS_ART_{:03d}".format(idx)
            row["art_define"] = "ART_DEF_BONUS_ART_{:03d}".format(idx)
            row["text_tag"] = "TXT_KEY_BONUS_ART_{:03d}".format(idx)
            row["button_path"] = "Art/Interface/Buttons/resources/ArtMasterpieces/ART_{:03d}.tga".format(
                idx
            )
            row["gallery_path"] = "Art/Interface/ArtMasterpieces/Gallery/ART_{:03d}.tga".format(
                idx
            )
    else:
        candidates = _collect_candidates()
        selected = _select_masterpieces(candidates, TARGET_COUNT)
        print("Selected {} masterpieces.".format(len(selected)), file=sys.stderr)

        for idx, row in enumerate(selected, start=1):
            if row.year < 0:
                year_label = "{} BCE".format(abs(row.year))
            else:
                year_label = str(row.year)

            rows.append(
                {
                    "index": str(idx),
                    "qid": row.qid,
                    "title": row.label,
                    "year": str(row.year),
                    "year_label": year_label,
                    "era": row.era,
                    "art_type": row.art_type,
                    "item_url": row.item_url,
                    "image_url": row.image_url,
                    "sitelinks": str(row.sitelinks),
                    "bonus_type": "BONUS_ART_{:03d}".format(idx),
                    "art_define": "ART_DEF_BONUS_ART_{:03d}".format(idx),
                    "text_tag": "TXT_KEY_BONUS_ART_{:03d}".format(idx),
                    "button_path": "Art/Interface/Buttons/resources/ArtMasterpieces/ART_{:03d}.tga".format(
                        idx
                    ),
                    "gallery_path": "Art/Interface/ArtMasterpieces/Gallery/ART_{:03d}.tga".format(
                        idx
                    ),
                }
            )

        # Write catalog CSV only when not reusing an existing one.
        CATALOG_CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
        with CATALOG_CSV_PATH.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "index",
                    "bonus_type",
                    "title",
                    "year",
                    "era",
                    "art_type",
                    "qid",
                    "sitelinks",
                    "item_url",
                    "image_url",
                    "button_path",
                    "gallery_path",
                ],
            )
            writer.writeheader()
            for row in rows:
                writer.writerow({k: row.get(k, "") for k in writer.fieldnames})

    bonus_blocks: List[str] = []
    art_define_blocks: List[str] = []
    failed_images = 0

    for row in rows:
        idx = int(row["index"])
        icon_path = ICON_DIR / "ART_{:03d}.tga".format(idx)
        gallery_path = GALLERY_DIR / "ART_{:03d}.tga".format(idx)
        attempted_download = False
        have_icon = icon_path.exists() and icon_path.stat().st_size > 0
        have_gallery = gallery_path.exists() and gallery_path.stat().st_size > 0
        if not force_redownload and have_icon and have_gallery:
            ok = True
        else:
            attempted_download = True
            ok = _download_art_assets(row["image_url"], icon_path, gallery_path)
        if not ok:
            failed_images += 1

        bonus_blocks.append(
            _bonus_block(row["bonus_type"], row["text_tag"], row["art_define"])
        )
        art_define_blocks.append(_art_define_block(row["art_define"], row["button_path"]))
        if attempted_download:
            # Keep request pace polite for Wikimedia endpoint stability.
            time.sleep(0.25)

    print("Image conversion failures: {}".format(failed_images), file=sys.stderr)

    # Generated XML blocks.
    bonus_block_joined = "\n".join(bonus_blocks)
    art_def_block_joined = "\n".join(art_define_blocks)

    bonus_xml = _read_text(BONUS_INFOS_PATH)
    bonus_xml = _replace_or_insert_marker_block(
        bonus_xml,
        "ART_MASTERPIECES_BONUSINFOS_BEGIN",
        "ART_MASTERPIECES_BONUSINFOS_END",
        bonus_block_joined,
        "\t</BonusInfos>",
    )
    _write_text(BONUS_INFOS_PATH, bonus_xml)

    art_defs_xml = _read_text(BONUS_ART_DEFS_PATH)
    art_defs_xml = _replace_or_insert_marker_block(
        art_defs_xml,
        "ART_MASTERPIECES_ARTDEFS_BEGIN",
        "ART_MASTERPIECES_ARTDEFS_END",
        art_def_block_joined,
        "\t</BonusArtInfos>",
    )
    _write_text(BONUS_ART_DEFS_PATH, art_defs_xml)

    _insert_or_update_trigger_building_class()
    _insert_or_update_trigger_building_and_corp_prereq([row["bonus_type"] for row in rows])
    _patch_unit_artist_buildings()
    _patch_corporation_7()

    # Generated text + python data.
    _write_text(TEXT_OUT_PATH, _text_entries(rows))
    _write_text(PY_DATA_OUT_PATH, _python_data_content(rows))

    era_counts = defaultdict(int)
    type_counts = defaultdict(int)
    for row in rows:
        era_counts[row["era"]] += 1
        type_counts[row["art_type"]] += 1

    print("Era distribution:", file=sys.stderr)
    for era in ERA_ORDER:
        print("  {:12s} {}".format(era, era_counts.get(era, 0)), file=sys.stderr)
    print("Type distribution:", file=sys.stderr)
    for art_type in sorted(type_counts):
        print("  {:12s} {}".format(art_type, type_counts[art_type]), file=sys.stderr)

    print("Generated {} art resources.".format(len(rows)), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
