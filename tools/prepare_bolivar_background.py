"""Rebuild the bounded Bolivar background repair using optional PyFFI 2.2.3.

Run with --apply to publish; default mode checks the existing repair.
PyFFI is needed only for this art-maintenance tool, not the package compiler.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/Art"
SOURCE = ART / "BTG/LeaderHeads/harun_al-rashid/julius_caesar_bg_background.kf"
MODEL = ART / "Leaderheads/new/bolivar_v3/julius_caesar_BG.nif"
TARGET = ART / "Leaderheads/new/bolivar_v3/julius_caesar_BG_background.kf"
SOURCE_SHA256 = "402b52b658a2a6b68548ded52ec03b5c1dc3aa0fb313e3c2b08a573406351cd0"
MODEL_SHA256 = "dd862a23c5f62c7f264ec4af655e47811f8542d35e062af4f87da9d33e0df37c"
ROOT_NODE = b"_julius_caesar_parent"
KEEP = (ROOT_NODE, ROOT_NODE + b" NonAccum")
ABSENT = (b"background sky", b"Editable Mesh")


def build() -> bytes:
    # PyFFI 2.2.3's schema loader still calls the removed Python time.clock.
    if not hasattr(time, "clock"):
        time.clock = time.perf_counter
    from pyffi.formats.nif import NifFormat

    def read(path: Path, digest: str):
        payload = path.read_bytes()
        if hashlib.sha256(payload).hexdigest() != digest:
            raise ValueError("Reviewed art input changed: " + str(path))
        data = NifFormat.Data()
        data.read(io.BytesIO(payload))
        return data

    model = read(MODEL, MODEL_SHA256)
    data = read(SOURCE, SOURCE_SHA256)
    nodes = {b.name: b for b in model.get_global_iterator() if isinstance(b, NifFormat.NiAVObject)}
    sequences = [b for b in data.roots if isinstance(b, NifFormat.NiControllerSequence)]
    if len(sequences) != 1:
        raise ValueError("Expected one reviewed background sequence")
    sequence = sequences[0]
    links = list(sequence.controlled_blocks)
    if tuple(link.get_node_name() for link in links) != ABSENT + KEEP:
        raise ValueError("Background controller targets changed")
    if any(name in nodes for name in ABSENT) or not all(name in nodes for name in KEEP):
        raise ValueError("Retained model no longer matches reviewed target hierarchy")
    descendants = list(nodes[KEEP[1]].get_global_iterator())
    if any(b not in descendants for b in nodes.values()
           if isinstance(b, (NifFormat.NiCamera, NifFormat.NiGeometry))):
        raise ValueError("A camera or mesh is outside the preserved composite transform")
    if any(nodes[name].scale != 1 or any(abs(v) > 1e-6 for v in nodes[name].translation.as_list())
           for name in KEEP):
        raise ValueError("Retained root scale or translation changed")
    if sequence.target_name != ROOT_NODE or sequence.name != b"background":
        raise ValueError("Background sequence binding changed")
    kept = links[2:]
    for link in kept:
        if link.get_controller_type() != b"NiTransformController" or link.interpolator.data is not None:
            raise ValueError("Expected only constant root transforms")
        if link.interpolator.scale != 1 or any(abs(v) > 1e-6 for v in link.interpolator.translation.as_list()):
            raise ValueError("Unexpected root scale or translation")
    def quaternion_values(q):
        return (q.w, q.x, q.y, q.z)

    if quaternion_values(kept[0].interpolator.rotation) != (1, 0, 0, 0):
        raise ValueError("Expected identity parent rotation")
    expected = nodes[KEEP[1]].rotation * nodes[KEEP[0]].rotation
    _, expected_quaternion = expected.get_scale_quat()
    actual = quaternion_values(kept[1].interpolator.rotation)
    expected_values = quaternion_values(expected_quaternion)
    if min(max(abs(a - sign * b) for a, b in zip(actual, expected_values))
           for sign in (-1, 1)) > 1e-5:
        raise ValueError("Donor transforms would change retained background orientation")

    sequence.num_controlled_blocks = len(kept)
    sequence.controlled_blocks.update_size()
    for index, link in enumerate(kept):
        for field in ("interpolator", "controller", "string_palette", "node_name_offset",
                      "property_type_offset", "controller_type_offset", "variable_1_offset",
                      "variable_2_offset"):
            setattr(sequence.controlled_blocks[index], field, getattr(link, field))
    output = io.BytesIO()
    data.write(output)
    payload = output.getvalue()
    verified = NifFormat.Data()
    verified.read(io.BytesIO(payload))
    repaired = verified.roots[0]
    if tuple(link.get_node_name() for link in repaired.controlled_blocks) != KEEP:
        raise ValueError("Serialized repair target mismatch")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    payload = build()
    if args.apply:
        if TARGET.exists() and TARGET.read_bytes() != payload:
            raise ValueError("Refusing to replace a different existing background repair")
        TARGET.write_bytes(payload)
    if not TARGET.exists() or TARGET.read_bytes() != payload:
        raise ValueError("Prepared background differs; review and run with --apply")
    print("PASS: two matching constant root controllers; retained orientation; no orphan targets")
    print("SHA256:", hashlib.sha256(payload).hexdigest())


if __name__ == "__main__":
    main()
