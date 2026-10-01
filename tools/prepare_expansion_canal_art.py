"""Build the original, texture-free Royal Canal prototype (optional PyFFI 2.2.3)."""
from __future__ import annotations

import argparse
import hashlib
import io
import time
from pathlib import Path

from remaster_visual_phase_3_6 import emit

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/Art/Structures/Improvements/Expansion/RoyalCanal.nif"


def build() -> bytes:
    if not hasattr(time, "clock"):
        time.clock = time.perf_counter
    from pyffi.formats.nif import NifFormat as N

    document = N.Data(version=0x14000004)
    document.header.endian_type = 1
    root = N.NiNode()
    root.name = b"Royal Canal prototype"
    root.flags = 14
    document.roots = [root]
    shapes = []

    def box(name, center, size, color):
        shape = N.NiTriShape()
        shape.name = name.encode("ascii")
        shape.flags = 14
        shape.data = N.NiTriShapeData()
        points = [(center[0] + x * size[0] / 2,
                   center[1] + y * size[1] / 2,
                   center[2] + z * size[2] / 2)
                  for x, y, z in [(-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1),
                                  (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)]]
        faces = [((0, 3, 2, 1), (0, 0, -1)), ((4, 5, 6, 7), (0, 0, 1)),
                 ((0, 1, 5, 4), (0, -1, 0)), ((1, 2, 6, 5), (1, 0, 0)),
                 ((2, 3, 7, 6), (0, 1, 0)), ((3, 0, 4, 7), (-1, 0, 0))]
        data = shape.data
        data.num_vertices = 24
        data.has_vertices = True
        data.vertices.update_size()
        data.has_normals = True
        data.normals.update_size()
        triangles = []
        for face_index, (indices, normal) in enumerate(faces):
            for corner, point_index in enumerate(indices):
                index = face_index * 4 + corner
                data.vertices[index].x, data.vertices[index].y, data.vertices[index].z = points[point_index]
                data.normals[index].x, data.normals[index].y, data.normals[index].z = normal
            start = face_index * 4
            triangles.extend([(start, start + 1, start + 2), (start, start + 2, start + 3)])
        data.set_triangles(triangles)
        data.update_center_radius()
        material = N.NiMaterialProperty()
        material.name = b"Original untextured prototype material"
        material.ambient_color.r = material.ambient_color.g = material.ambient_color.b = 1.0
        material.diffuse_color.r, material.diffuse_color.g, material.diffuse_color.b = color
        material.alpha = 1.0
        shape.add_property(material)
        shapes.append(shape)

    for i, x in enumerate((-9, 0, 9)):
        box(f"Channel {i}", (x, 0, 0.6), (3, 26, 0.4), (0.18, 0.38, 0.36))
        for side in (-1, 1):
            box(f"Earth bank {i} {side}", (x + side * 2.2, 0, 0.75),
                (1.4, 28, 1.5), (0.53, 0.43, 0.28))
    for y in (-13.8, 13.8):
        box(f"End bank {y}", (0, y, 0.75), (23, 1.4, 1.5), (0.53, 0.43, 0.28))
    root.num_children = len(shapes)
    root.children.update_size()
    for i, shape in enumerate(shapes):
        root.children[i] = shape
    stream = io.BytesIO()
    document.write(stream)
    payload = stream.getvalue()
    check = N.Data()
    check.read(io.BytesIO(payload))
    meshes = [b for b in dict.fromkeys(check.get_global_iterator()) if isinstance(b, N.NiTriShape)]
    if len(meshes) != 11 or sum(m.data.num_triangles for m in meshes) != 132:
        raise ValueError("Canal prototype geometry did not round-trip")
    if any(isinstance(b, N.NiSourceTexture) for b in check.get_global_iterator()):
        raise ValueError("Texture-free prototype acquired an external dependency")
    return payload


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    started = time.monotonic()
    emit("batch_start", batch="canal_prototype", index=1, total=1, inputCount=11,
         inputBytes=Path(__file__).stat().st_size, retryCount=0)
    payload = build()
    if TARGET.exists() and TARGET.read_bytes() != payload:
        raise ValueError("Refusing to overwrite a different canal prototype")
    if args.apply:
        TARGET.parent.mkdir(parents=True, exist_ok=True)
        TARGET.write_bytes(payload)
    if not TARGET.exists() or TARGET.read_bytes() != payload:
        raise ValueError("Run --apply to publish the canal prototype")
    emit("batch_end", batch="canal_prototype", status="success", outputCount=1,
         outputBytes=len(payload), sha256=hashlib.sha256(payload).hexdigest(),
         durationSeconds=round(time.monotonic() - started, 3), retryCount=0)
    emit("reconciliation", expected=1, processed=1, persisted=1, dropped=0, skipped=0,
         duplicates=0, errors=0, passed=True)


if __name__ == "__main__":
    main()
