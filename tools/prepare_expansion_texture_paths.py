"""Prepare narrowly scoped Ho/Askia texture references; requires PyFFI 2.2.3.

Original models and textures remain unchanged. Default verifies the prepared
runtime models; --apply publishes them after both preservation checks pass.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import struct
import time
from pathlib import Path

from remaster_visual_phase_3_6 import emit

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/Art/Leaderheads/new"
SPECS = (
    {
        "folder": "hochiminh_v2", "source": "HoChiMinh_Nonshader.nif",
        "target": "HoChiMinh_Nonshader_Runtime.nif", "geometry": b"Mao-new",
        "old": b"gengis_nonshader.dds", "new": b"gengis_diff.dds",
        "sha256": "92752dbf56a10091fb11069c782c7372dcbb4c1383ded7172435a0a0cd733127",
    },
    {
        "folder": "askia", "source": "Zara Yaqob.nif",
        "target": "Askia_Runtime.nif", "geometry": b"zara_trans",
        "old": b"d:\\games\\strategy\\firaxis\\civilization 4\\beyond the sword\\mods\\test\\assets\\art\\leaderheads\\newalex\\zara_diff.dds",
        "new": b"Zara_DIFF.dds",
        "sha256": "b505164f05aaaab81e4d48db5d2782e54a37a6678186761af5e76f65d3f8e86a",
    },
)


def build(spec: dict) -> bytes:
    if not hasattr(time, "clock"):
        time.clock = time.perf_counter
    from pyffi.formats.nif import NifFormat

    def read(raw):
        document = NifFormat.Data()
        document.read(io.BytesIO(raw))
        return document

    def serialize(document):
        stream = io.BytesIO()
        document.write(stream)
        return stream.getvalue()

    def geometry(document):
        matches = [node for node in dict.fromkeys(document.get_global_iterator())
                   if isinstance(node, NifFormat.NiTriBasedGeom) and node.name == spec["geometry"]]
        if len(matches) != 1:
            raise ValueError("Expected one reviewed geometry")
        return matches[0]

    def texture(mesh):
        properties = [prop for prop in mesh.properties
                      if isinstance(prop, NifFormat.NiTexturingProperty) and prop.has_base_texture]
        if len(properties) != 1:
            raise ValueError("Expected one base-texture property")
        return properties[0].base_texture.source

    folder = ART / spec["folder"]
    raw = (folder / spec["source"]).read_bytes()
    if hashlib.sha256(raw).hexdigest() != spec["sha256"]:
        raise ValueError("Reviewed source changed: " + spec["source"])
    if not (folder / spec["new"].decode("ascii")).is_file():
        raise ValueError("Reviewed relative texture is absent")
    document = read(raw)
    mesh = geometry(document)
    source = texture(mesh)
    if source.file_name != spec["old"]:
        raise ValueError("Texture binding differs from reviewed source")
    users = [node for node in dict.fromkeys(document.get_global_iterator())
             if isinstance(node, NifFormat.NiTriBasedGeom) and
             any(isinstance(prop, NifFormat.NiTexturingProperty) and prop.has_base_texture and
                 prop.base_texture.source is source for prop in node.properties)]
    if users != [mesh]:
        raise ValueError("Texture reference is shared outside the reviewed geometry")
    if spec["folder"] == "hochiminh_v2":
        primary_raw = (folder / "HoChiMinh.nif").read_bytes()
        if hashlib.sha256(primary_raw).hexdigest() != "efcabc6509e044db16230ad0150ca4342f5e62335965aac5e8c21c33c8f3e659":
            raise ValueError("Ho's retained primary model changed")
        primary = geometry(read(primary_raw))
        def uvs(node):
            return tuple(tuple((float(uv.u), float(uv.v)) for uv in group) for group in node.data.uv_sets)
        if (texture(primary).file_name != spec["new"] or mesh.data.num_vertices != 1794 or
                primary.data.num_vertices != 1794 or not uvs(mesh) or uvs(primary) != uvs(mesh)):
            raise ValueError("Ho clothing does not share the primary blue texture's UV layout")

    before = serialize(document)
    old = struct.pack("<I", len(spec["old"])) + spec["old"]
    new = struct.pack("<I", len(spec["new"])) + spec["new"]
    matches = []
    offset = raw.find(old)
    while offset >= 0:
        payload = raw[:offset] + new + raw[offset + len(old):]
        check = read(payload)
        corrected = texture(geometry(check))
        if corrected.file_name == spec["new"]:
            corrected.file_name = spec["old"]
            if serialize(check) != before:
                raise ValueError("Something other than the reviewed texture filename changed")
            matches.append(payload)
        offset = raw.find(old, offset + len(old))
    if len(matches) != 1:
        raise ValueError("Expected one exact binary edit of the reviewed texture reference")
    return matches[0]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    outputs = {}
    for index, spec in enumerate(SPECS, 1):
        started = time.monotonic()
        input_bytes = (ART / spec["folder"] / spec["source"]).stat().st_size
        emit("batch_start", batch=spec["folder"], index=index, total=len(SPECS),
             inputCount=1, inputBytes=input_bytes, retryCount=0)
        try:
            payload = build(spec)
        except (ValueError, OSError):
            emit("batch_end", batch=spec["folder"], status="failure", retryCount=0,
                 durationSeconds=round(time.monotonic() - started, 3), outputCount=0)
            raise
        target = ART / spec["folder"] / spec["target"]
        if target.exists() and target.read_bytes() != payload:
            raise ValueError("Refusing to overwrite different runtime art: " + str(target))
        outputs[target] = payload
        emit("batch_end", batch=spec["folder"], status="success", inputCount=1,
             inputBytes=input_bytes, outputCount=1, outputBytes=len(payload), retryCount=0,
             durationSeconds=round(time.monotonic() - started, 3),
             sha256=hashlib.sha256(payload).hexdigest())
    created = []
    try:
        for target, payload in outputs.items():
            if args.apply and not target.exists():
                created.append(target)
                target.write_bytes(payload)
            if not target.exists() or target.read_bytes() != payload:
                raise ValueError("Prepared art differs; review and run with --apply: " + str(target))
    except (ValueError, OSError):
        for target in created:
            target.unlink(missing_ok=True)
        emit("reconciliation", expected=len(outputs), errors=1, passed=False, status="rolled_back")
        raise
    emit("reconciliation", expected=len(outputs), processed=len(outputs), persisted=len(outputs),
         dropped=0, skipped=0, duplicates=0, errors=0, passed=True)


if __name__ == "__main__":
    main()
