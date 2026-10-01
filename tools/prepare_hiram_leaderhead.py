"""Remove Hiram's non-scene export roots without changing his visible scene.

Requires optional PyFFI 2.2.3. Default checks the prepared asset; --apply writes
a separate runtime model and never overwrites the original.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / "CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/Art/Leaderheads/new/Amra_Hiram_v2"
SOURCE = FOLDER / "Darius.nif"
TARGET = FOLDER / "Darius_Runtime.nif"
SOURCE_SHA256 = "42dd29992d223ae7c7def1e250438b0d49689f4bb57a3002174ed0bee5cd6ee9"


def build() -> bytes:
    if not hasattr(time, "clock"):
        time.clock = time.perf_counter
    from pyffi.formats.nif import NifFormat

    raw = SOURCE.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SOURCE_SHA256:
        raise ValueError("Reviewed Hiram model changed")
    data = NifFormat.Data()
    data.read(io.BytesIO(raw))
    expected_roots = ("NiNode", "NiTexturingProperty", "NiAlphaProperty",
                      "NiVertexColorProperty", "NiMaterialProperty", "NiTriStripsData")
    if tuple(type(root).__name__ for root in data.roots) != expected_roots:
        raise ValueError("Unreviewed export root structure")
    scene = data.roots[0]
    active = set(scene.get_global_iterator())
    if scene.name != b"Scene Root" or any(root in active for root in data.roots[1:]):
        raise ValueError("Extra export roots are not independent of the visible scene")
    if any(b"saruman" in block.file_name.lower() for block in active
           if isinstance(block, NifFormat.NiSourceTexture)):
        raise ValueError("Missing texture is used by the visible scene")

    def scene_bytes(document):
        # Initialize canonical reference indices before comparing every block.
        document.write(io.BytesIO())
        blocks = dict.fromkeys(document.roots[0].get_global_iterator())
        result = []
        for block in blocks:
            if isinstance(block, NifFormat.NiObject):
                stream = io.BytesIO()
                block.write(stream, document)
                result.append((type(block).__name__, stream.getvalue()))
        return result

    before = scene_bytes(data)
    data.roots = [scene]
    output = io.BytesIO()
    data.write(output)
    payload = output.getvalue()
    check = NifFormat.Data()
    check.read(io.BytesIO(payload))
    if len(check.roots) != 1 or scene_bytes(check) != before:
        raise ValueError("Visible scene block data or reference mapping changed")
    if b"saruman.dds" in payload.lower():
        raise ValueError("Stray missing texture reference remains")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    payload = build()
    if args.apply:
        if TARGET.exists() and TARGET.read_bytes() != payload:
            raise ValueError("Refusing to replace a different runtime model")
        TARGET.write_bytes(payload)
    if not TARGET.exists() or TARGET.read_bytes() != payload:
        raise ValueError("Prepared model differs; review and run with --apply")
    print("PASS: every visible scene block preserved; five separate non-scene export roots removed")
    print("SHA256:", hashlib.sha256(payload).hexdigest())


if __name__ == "__main__":
    main()
