"""Append reviewed native packages without regenerating existing XML records.

Run with --apply to publish; otherwise verifies the generated records in place.
The manifest is deliberately limited to packages whose native contracts exist.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import io
import json
import re
import struct
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image

from flags.dxt3_fullcolor import AlphaEncoding, encode_image
from flags.flag_pipeline import rasterize_master
from remaster_visual_phase_3_6 import emit

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets"
XML = ASSETS / "XML"
MANIFEST = ROOT / "tools/manifests/new_leaders_expansion.json"
FILES = {
    "civ": ("Civilizations/CIV4CivilizationInfos.xml", "CivilizationInfo", "CivilizationInfos"),
    "leader": ("Civilizations/CIV4LeaderHeadInfos.xml", "LeaderHeadInfo", "LeaderHeadInfos"),
    "trait": ("Civilizations/CIV4TraitInfos.xml", "TraitInfo", "TraitInfos"),
    "unit": ("Units/CIV4UnitInfos.xml", "UnitInfo", "UnitInfos"),
    "building": ("Buildings/CIV4BuildingInfos.xml", "BuildingInfo", "BuildingInfos"),
    "leader_art": ("Art/CIV4ArtDefines_Leaderhead.xml", "LeaderheadArtInfo", "LeaderheadArtInfos"),
    "civ_art": ("Art/CIV4ArtDefines_Civilization.xml", "CivilizationArtInfo", "CivilizationArtInfos"),
    "color": ("Interface/CIV4PlayerColorInfos.xml", "PlayerColorInfo", "PlayerColorInfos"),
    "promotion": ("Units/CIV4PromotionInfos.xml", "PromotionInfo", "PromotionInfos"),
}


def parse(data: str | bytes) -> ET.Element:
    root = ET.fromstring(data)
    for node in root.iter():
        node.tag = node.tag.rsplit("}", 1)[-1]
    return root


def canonical(node: ET.Element) -> tuple:
    return (node.tag, sorted(node.attrib.items()), (node.text or "").strip(),
            tuple(canonical(child) for child in node))


def baseline(path: Path, commit: str) -> ET.Element:
    return parse(subprocess.check_output(
        ["git", "show", f"{commit}:{path.relative_to(ROOT).as_posix()}"], cwd=ROOT
    ))


def field(node: ET.Element, tag: str, value: object) -> None:
    child = node.find(tag)
    if child is None:
        raise ValueError(f"Missing field {tag} in {node.findtext('Type')}")
    child.text = str(value)


def trait_scalar(node: ET.Element, tag: str, value: int, schema: ET.Element) -> None:
    declaration = schema.find(f"./ElementType[@name='TraitInfo']/element[@type='{tag}']")
    definition = schema.find(f"./ElementType[@name='{tag}']")
    if (declaration is None or definition is None or
            definition.get("{urn:schemas-microsoft-com:datatypes}type") != "int" or
            type(value) is not int):
        raise ValueError(f"Not a declared integer trait scalar: {tag}")
    if node.find(tag) is None:
        if declaration.get("minOccurs") != "0":
            raise ValueError(f"Missing required trait scalar: {tag}")
        ET.SubElement(node, tag)
    field(node, tag, value)


def retarget_kfm_model(data: bytes, old: str, new: str) -> bytes:
    headers = (b";Gamebryo KFM File Version 1.2.4b\n",
               b";Gamebryo KFM File Version 2.0.0.0b\n\x01")
    header = next((value for value in headers if data.startswith(value)), None)
    if header is None:
        raise ValueError("Unreviewed KFM version")
    old_bytes, new_bytes = old.encode("ascii"), new.encode("ascii")
    prefix = header + struct.pack("<I", len(old_bytes)) + old_bytes
    if not data.startswith(prefix):
        raise ValueError("KFM model binding differs from reviewed source")
    return header + struct.pack("<I", len(new_bytes)) + new_bytes + data[len(prefix):]


def resize_portrait_button(data: bytes, old_size: list[int], new_size: list[int]) -> bytes:
    if len(new_size) != 2 or any(n <= 0 or n & (n - 1) for n in new_size):
        raise ValueError("Portrait output dimensions must be positive powers of two")
    with Image.open(io.BytesIO(data)) as source:
        if source.size != tuple(old_size):
            raise ValueError("Portrait input dimensions differ from reviewed source")
        image = source.convert("RGBA").resize(tuple(new_size), Image.Resampling.LANCZOS)
    output = io.BytesIO()
    image.save(output, format="DDS")
    return output.getvalue()


def replace_fragment(node: ET.Element, fragment: str) -> None:
    for child in ET.fromstring("<Fragments>" + fragment + "</Fragments>"):
        existing = node.find(child.tag)
        if existing is None:
            node.append(child)
        else:
            index = list(node).index(existing)
            node.remove(existing)
            node.insert(index, child)


def serialize(node: ET.Element) -> bytes:
    node = copy.deepcopy(node)
    node.tail = None
    ET.indent(node, space="  ")
    return ET.tostring(node, encoding="ascii", xml_declaration=False)


def append_record(data: bytes, node: ET.Element, container: str) -> bytes:
    type_name = node.findtext("Type")
    matches = [n for n in parse(data).iter(node.tag) if n.findtext("Type") == type_name]
    if matches:
        if len(matches) != 1 or canonical(matches[0]) != canonical(node):
            raise ValueError(f"Existing expansion record differs: {type_name}; review before replacing")
        return data
    end = f"</{container}>".encode()
    if data.count(end) != 1:
        raise ValueError(f"Expected one {container} container")
    newline = b"\r\n" if b"\r\n" in data else b"\n"
    block = serialize(node).replace(b"\n", newline)
    return data.replace(end, block + newline + end, 1)


def generate(document: dict) -> dict[Path, bytes]:
    staged = {XML / spec[0]: (XML / spec[0]).read_bytes() for spec in FILES.values()}
    parents = {kind: baseline(XML / spec[0], document["baseline_commit"]) for kind, spec in FILES.items()}
    trait_schema = parse((XML / "Civilizations/CIV4CivilizationsSchema.xml").read_bytes())
    trait_order = [n.get("type") for n in trait_schema.find("./ElementType[@name='TraitInfo']").findall("element")]
    texts: dict[str, str] = {}
    flags_path = ROOT / "tools/flags/manifest.json"
    flags = json.loads(flags_path.read_bytes())
    diplomacy_path = XML / "GameInfo/CIV4DiplomacyInfos.xml"
    diplomacy_data = diplomacy_path.read_bytes()
    provenance = []

    def clone(kind: str, name: str) -> ET.Element:
        matches = [n for n in parents[kind].iter(FILES[kind][1]) if n.findtext("Type") == name]
        if len(matches) != 1:
            raise ValueError(f"Parent must resolve uniquely: {kind}/{name}")
        return copy.deepcopy(matches[0])

    def add(kind: str, node: ET.Element) -> None:
        path = XML / FILES[kind][0]
        staged[path] = append_record(staged[path], node, FILES[kind][2])
        record_sizes.append(len(serialize(node)))

    def localized(node: ET.Element, tag: str, key: str, value: str) -> None:
        texts[key] = value
        field(node, tag, key)

    for index, package in enumerate(document["packages"], 1):
        started = time.monotonic()
        record_sizes: list[int] = []
        repair_sizes: list[int] = []
        identifier = package["id"]
        if identifier not in document["approved_leaders"]:
            raise ValueError(f"Unapproved package {identifier}")
        emit("package_start", batch=identifier, index=index, total=len(document["packages"]), retryCount=0)
        suffix = "EXP_" + identifier
        civ_type = "CIVILIZATION_EXP_" + package["civilization"]
        leader_type = "LEADER_" + suffix
        trait_type = "TRAIT_" + suffix
        civ_art_type = "ART_DEF_" + civ_type
        for repair in package.get("repairs", []):
            data = (ASSETS / repair["source"]).read_bytes()
            if hashlib.sha256(data).hexdigest() != repair["sha256"]:
                raise ValueError("Repair source changed: " + repair["source"])
            target = ASSETS / repair["target"]
            if "kfm_model" in repair:
                data = retarget_kfm_model(data, **repair["kfm_model"])
            if "portrait_resize" in repair:
                data = resize_portrait_button(data, **repair["portrait_resize"])
            if "prepared_sha256" in repair:
                data = target.read_bytes()
                if hashlib.sha256(data).hexdigest() != repair["prepared_sha256"]:
                    raise ValueError("Prepared art repair changed: " + repair["target"])
            if target.exists() and target.read_bytes() != data:
                raise ValueError("Refusing to overwrite a different repair target: " + str(target))
            staged[target] = data
            repair_sizes.append(len(data))

        if "promotion" in package:
            promotion = clone("promotion", "PROMOTION_COMBAT1")
            for child in promotion:
                if child.tag.startswith(("i", "b")):
                    child.text = "0"
                elif list(child):
                    child.clear()
            field(promotion, "Type", package["promotion"])
            localized(promotion, "Description", "TXT_KEY_" + package["promotion"], "Paid Professionals")
            field(promotion, "iUpgradeDiscount", 25)
            field(promotion, "bLeader", 1)
            replace_fragment(promotion, "<UnitCombats><UnitCombat><UnitCombatType>UNITCOMBAT_MELEE</UnitCombatType><bUnitCombat>1</bUnitCombat></UnitCombat><UnitCombat><UnitCombatType>UNITCOMBAT_GUN</UnitCombatType><bUnitCombat>1</bUnitCombat></UnitCombat></UnitCombats>")
            add("promotion", promotion)

        unit = clone("unit", package["unit"]["parent"])
        building = clone("building", package["building"]["parent"])
        for kind, node in (("unit", unit), ("building", building)):
            spec = package[kind]
            type_name = kind.upper() + "_EXP_" + spec["id"]
            field(node, "Type", type_name)
            localized(node, "Description", "TXT_KEY_" + type_name, spec["name"])
            localized(node, "Civilopedia", "TXT_KEY_" + type_name + "_PEDIA", package["history"])
            localized(node, "Strategy", "TXT_KEY_" + type_name + "_STRATEGY", spec["strategy"])
            if node.find("Help") is not None:
                node.find("Help").text = None
            for tag, value in spec["scalars"].items():
                field(node, tag, value)
            replace_fragment(node, spec["xml"])
            add(kind, node)

        trait = clone("trait", "TRAIT_AGGRESSIVE")
        for child in trait:
            if child.tag.startswith("i"):
                child.text = "-1" if child.tag == "iMaxAnarchy" else "0"
            elif child.tag not in ("Type", "Description", "ShortDescription"):
                child.clear()
        field(trait, "Type", trait_type)
        localized(trait, "Description", "TXT_KEY_" + trait_type, package["trait_name"])
        localized(trait, "ShortDescription", "TXT_KEY_" + trait_type + "_SHORT", package["trait_name"])
        for tag, value in package["trait_scalars"].items():
            trait_scalar(trait, tag, value, trait_schema)
        replace_fragment(trait, package["trait_xml"])
        trait[:] = sorted(trait, key=lambda child: trait_order.index(child.tag))
        add("trait", trait)

        leader = clone("leader", package["leader_parent"])
        field(leader, "Type", leader_type)
        localized(leader, "Description", "TXT_KEY_" + leader_type, package["name"])
        localized(leader, "Civilopedia", "TXT_KEY_" + leader_type + "_PEDIA", package["history"])
        field(leader, "ArtDefineTag", "ART_DEF_" + leader_type)
        field(leader, "FavoriteCivic", package["civic"])
        field(leader, "FavoriteReligion", package["religion"])
        for tag, value in package["leader_scalars"].items():
            field(leader, tag, value)
        replace_fragment(leader, f"<Traits><Trait><TraitType>{trait_type}</TraitType><bTrait>1</bTrait></Trait></Traits>")
        flavors = ET.Element("Flavors")
        for flavor, value in package["flavors"].items():
            entry = ET.SubElement(flavors, "Flavor")
            ET.SubElement(entry, "FlavorType").text = flavor
            ET.SubElement(entry, "iFlavor").text = str(value)
        replace_fragment(leader, ET.tostring(flavors, encoding="unicode"))
        add("leader", leader)

        civ = clone("civ", package["civ_parent"])
        field(civ, "Type", civ_type)
        for tag, value in (("Description", package["civ_name"]), ("ShortDescription", package["civ_name"]),
                           ("Adjective", package["adjective"]), ("Civilopedia", package["history"])):
            localized(civ, tag, "TXT_KEY_" + civ_type + "_" + tag.upper(), value)
        field(civ, "DefaultPlayerColor", "PLAYERCOLOR_" + suffix)
        field(civ, "ArtDefineTag", civ_art_type)
        for tag in ("Cities", "Buildings", "Units", "FreeTechs", "Leaders"):
            civ.find(tag).clear()
        for number, city in enumerate(package["cities"], 1):
            key = f"TXT_KEY_CITY_{suffix}_{number}"
            texts[key] = city
            ET.SubElement(civ.find("Cities"), "City").text = key
        replace_fragment(civ,
            f"<Buildings><Building><BuildingClassType>{building.findtext('BuildingClass')}</BuildingClassType><BuildingType>{building.findtext('Type')}</BuildingType></Building></Buildings>"
            f"<Units><Unit><UnitClassType>{unit.findtext('Class')}</UnitClassType><UnitType>{unit.findtext('Type')}</UnitType></Unit></Units>"
            f"<Leaders><Leader><LeaderName>{leader_type}</LeaderName><bLeaderAvailability>1</bLeaderAvailability></Leader></Leaders>")
        for technology in package["techs"]:
            entry = ET.SubElement(civ.find("FreeTechs"), "FreeTech")
            ET.SubElement(entry, "TechType").text = technology
            ET.SubElement(entry, "bFreeTech").text = "1"
        add("civ", civ)

        color = ET.Element("PlayerColorInfo")
        for tag, value in zip(("Type", "ColorTypePrimary", "ColorTypeSecondary", "TextColorType"),
                              ["PLAYERCOLOR_" + suffix] + package["colors"]):
            ET.SubElement(color, tag).text = value
        add("color", color)

        art = ET.Element("LeaderheadArtInfo")
        ET.SubElement(art, "Type").text = "ART_DEF_" + leader_type
        dependencies = {}
        for tag in ("Button", "NIF", "KFM", "NoShaderNIF", "BackgroundKFM"):
            if tag == "Button" and package["art"][tag] is None:
                relative = f"Art/Interface/Buttons/Civilizations/{suffix}.dds"
            else:
                relative = "Art/Leaderheads/new/" + package["art"]["folder"] + "/" + package["art"][tag]
                path = ASSETS / relative
                data = staged[path] if path in staged else path.read_bytes()
                dependencies[relative] = hashlib.sha256(data).hexdigest()
            ET.SubElement(art, tag).text = relative
        add("leader_art", art)
        provenance.append({"leader": leader_type, "status": package["art_status"], "direct_reference_sha256": dependencies,
                           "repairs": package.get("repairs", []),
                           "dependency_closure": "Per-package audit read; main/background KF playback and graphics modes still require game acceptance."})

        master = ROOT / f"tools/flags/designs/expansion-v1/masters/{identifier.lower()}.svg"
        image = rasterize_master(master)
        dds, _ = encode_image(image, alpha_encoding=AlphaEncoding.FIXED_COLOR_ZERO)
        button, _ = encode_image(image, alpha_encoding=AlphaEncoding.RGBA)
        flag_relative = f"Art/Interface/TeamColor/FlagDECAL_{suffix}.dds"
        button_relative = f"Art/Interface/Buttons/Civilizations/{suffix}.dds"
        staged[ASSETS / flag_relative] = dds
        staged[ASSETS / button_relative] = button
        if package["art"]["Button"] is None:
            dependencies[button_relative] = hashlib.sha256(button).hexdigest()
        art = ET.Element("CivilizationArtInfo")
        for tag, value in (("Type", civ_art_type), ("Button", button_relative), ("Path", flag_relative), ("bWhiteFlag", "1")):
            ET.SubElement(art, tag).text = value
        add("civ_art", art)
        record = {
            "civilization_type": civ_type, "civilization": package["civ_name"],
            "leaders": [leader_type], "leader_display": package["name"],
            "art_define": civ_art_type, "runtime_dds_path": flag_relative,
            "active_design_version": "expansion-v1", "master_path": master.relative_to(ROOT).as_posix(),
            "master_sha256": hashlib.sha256(master.read_bytes()).hexdigest(),
            "production_dds_sha256": hashlib.sha256(dds).hexdigest(),
            "source_method": "Original geometric SVG reconstruction; no external artwork imported.",
            "source_page_url": package["source_url"], "source_license": "CC0-1.0",
            "attribution": "Original DowagerMod expansion artwork, dedicated under CC0-1.0.",
            "historical_scope": package["history"], "design_notes": package["flag_note"],
            "licensing_note": "Original geometric drawing; historical reference is not copied artwork.",
            "citations": [{"url": package["source_url"], "claim": "Historical setting, not a specification of an attested flag."}],
        }
        existing = [r for r in flags["records"] if r["civilization_type"] == civ_type]
        if existing and existing != [record]:
            raise ValueError(f"Flag manifest drift for {civ_type}")
        if not existing:
            flags["records"].append(record)

        greeting_key = "TXT_KEY_DIPLO_FIRST_CONTACT_" + suffix
        texts[greeting_key] = "I am " + package["name"] + ". Let us speak of peace and the prosperity of our peoples."
        response = parse(
            f"<Response><Civilizations/><Leaders><Leader><LeaderType>{leader_type}</LeaderType>"
            f"<bLeaderType>1</bLeaderType></Leader></Leaders><Attitudes/><DiplomacyPowers/>"
            f"<DiplomacyText><Text>{greeting_key}</Text></DiplomacyText></Response>")
        if greeting_key.encode() not in diplomacy_data:
            pattern = rb"(<DiplomacyInfo>\s*<Type>AI_DIPLOCOMMENT_FIRST_CONTACT</Type>.*?)(</Responses>)"
            diplomacy_data, count = re.subn(pattern, lambda m: m[1] + serialize(response) + b"\r\n" + m[2],
                                           diplomacy_data, count=1, flags=re.DOTALL)
            if count != 1:
                raise ValueError("Cannot locate first-contact diplomacy responses")
        emit("package_end", batch=identifier, status="success", durationSeconds=round(time.monotonic()-started, 3),
             inputCount=1, outputCount=len(record_sizes)+len(repair_sizes)+2,
             inputBytes=len(json.dumps(package).encode()),
             outputBytes=sum(record_sizes)+sum(repair_sizes)+len(dds)+len(button),
             outputScope="core_xml_records_flags_buttons_repairs", retryCount=0)

    text_root = ET.Element("Civ4GameText", xmlns="http://www.firaxis.com")
    for key, value in texts.items():
        entry = ET.SubElement(text_root, "TEXT")
        ET.SubElement(entry, "Tag").text = key
        for language in ("English", "French", "German", "Italian", "Spanish"):
            ET.SubElement(entry, language).text = value
    staged[XML / "Text/ZZZ_CIV4GameText_Expansion.xml"] = b'<?xml version="1.0" encoding="ASCII"?>\n' + serialize(text_root) + b"\n"
    staged[diplomacy_path] = diplomacy_data
    flags["record_count"] = len(flags["records"])
    flags["design_version_summary"]["expansion-v1"] = len(document["packages"])
    staged[flags_path] = (json.dumps(flags, indent=2, ensure_ascii=False) + "\n").encode()
    staged[ROOT / "tools/manifests/new_leaders_art.json"] = (json.dumps(provenance, indent=2) + "\n").encode()
    return staged


def main() -> None:
    sys.stdout.reconfigure(line_buffering=True)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    document = json.loads(MANIFEST.read_bytes())
    outputs = generate(document)
    originals = {path: path.read_bytes() if path.exists() else None for path in outputs}
    changed = [path for path, data in outputs.items() if originals[path] != data]
    if not args.apply and changed:
        raise ValueError("Generated output differs: " + ", ".join(str(path.relative_to(ROOT)) for path in changed))
    published = []
    started = time.monotonic()
    emit("batch_start", batch="expansion_publish", index=1, total=1, inputCount=len(outputs),
         inputBytes=sum(len(data) for data in outputs.values()), retryCount=0)
    try:
        for path in changed if args.apply else []:
            path.parent.mkdir(parents=True, exist_ok=True)
            published.append(path)
            path.write_bytes(outputs[path])
            if path.read_bytes() != outputs[path]:
                raise IOError(f"Publication mismatch: {path}")
    except OSError:
        for path in reversed(published):
            if originals[path] is None:
                path.unlink(missing_ok=True)
            else:
                path.write_bytes(originals[path])
        emit("reconciliation", batch="expansion_publish", expected=len(outputs), persisted=0,
             errors=1, passed=False, status="rolled_back")
        raise
    emit("batch_end", batch="expansion_publish", status="success", durationSeconds=round(time.monotonic()-started, 3),
         inputCount=len(outputs), outputCount=len(outputs), outputBytes=sum(len(data) for data in outputs.values()),
         changed=len(changed), retryCount=0)
    emit("reconciliation", expected=len(outputs), processed=len(outputs), persisted=len(outputs),
         skipped=0, dropped=0, duplicates=0, errors=0, passed=True)


if __name__ == "__main__":
    main()
