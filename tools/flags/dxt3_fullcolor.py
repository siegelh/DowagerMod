from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import struct
import time
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path

from PIL import Image


DDS_MAGIC = b"DDS "
FOURCC = b"DXT3"
BASE_SIZE = (128, 128)
MIP_COUNT = 8
HEADER_BYTES = 128
EXPECTED_FILE_BYTES = 22_000


class AlphaEncoding(str, Enum):
    RGBA = "rgba"
    FIXED_COLOR_ZERO = "fixed-color-zero-alpha"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def rgb_to_565(rgb: tuple[int, int, int]) -> int:
    red, green, blue = rgb
    return ((red * 31 + 127) // 255 << 11) | ((green * 63 + 127) // 255 << 5) | (
        (blue * 31 + 127) // 255
    )


def rgb_from_565(value: int) -> tuple[int, int, int]:
    red = (value >> 11) & 31
    green = (value >> 5) & 63
    blue = value & 31
    return (
        (red << 3) | (red >> 2),
        (green << 2) | (green >> 4),
        (blue << 3) | (blue >> 2),
    )


def color_palette(
    endpoint0: int, endpoint1: int
) -> tuple[tuple[int, int, int], ...]:
    if endpoint0 <= endpoint1:
        raise ValueError("DXT3 color blocks must use four-color mode (endpoint0 > endpoint1)")
    color0 = rgb_from_565(endpoint0)
    color1 = rgb_from_565(endpoint1)
    return (
        color0,
        color1,
        tuple((2 * color0[channel] + color1[channel]) // 3 for channel in range(3)),
        tuple((color0[channel] + 2 * color1[channel]) // 3 for channel in range(3)),
    )


def color_error(
    pixels: list[tuple[int, int, int]], endpoint0: int, endpoint1: int
) -> tuple[int, int]:
    palette = color_palette(endpoint0, endpoint1)
    indices = 0
    error = 0
    for pixel_index, pixel in enumerate(pixels):
        distances = [
            sum((pixel[channel] - color[channel]) ** 2 for channel in range(3))
            for color in palette
        ]
        index = min(range(4), key=lambda candidate: (distances[candidate], candidate))
        error += distances[index]
        indices |= index << (pixel_index * 2)
    return error, indices


def endpoint_seed_pairs(
    pixels: list[tuple[int, int, int]]
) -> list[tuple[int, int]]:
    channel_min = tuple(min(pixel[channel] for pixel in pixels) for channel in range(3))
    channel_max = tuple(max(pixel[channel] for pixel in pixels) for channel in range(3))

    means = tuple(sum(pixel[channel] for pixel in pixels) / 16.0 for channel in range(3))
    centered = [
        tuple(pixel[channel] - means[channel] for channel in range(3))
        for pixel in pixels
    ]
    axis = [1.0, 1.0, 1.0]
    for _ in range(8):
        projected = [
            sum(vector[channel] * axis[channel] for channel in range(3))
            for vector in centered
        ]
        next_axis = [
            sum(vector[channel] * projection for vector, projection in zip(centered, projected))
            for channel in range(3)
        ]
        magnitude = math.sqrt(sum(component * component for component in next_axis))
        if magnitude < 1e-12:
            break
        axis = [component / magnitude for component in next_axis]
    projections = [
        sum(vector[channel] * axis[channel] for channel in range(3))
        for vector in centered
    ]
    low = pixels[min(range(16), key=lambda index: projections[index])]
    high = pixels[max(range(16), key=lambda index: projections[index])]
    farthest = max(
        (
            (
                sum(
                    (pixels[first][channel] - pixels[second][channel]) ** 2
                    for channel in range(3)
                ),
                first,
                second,
            )
            for first in range(16)
            for second in range(first + 1, 16)
        ),
        default=(0, 0, 0),
    )
    return sorted(
        {
            (rgb_to_565(channel_max), rgb_to_565(channel_min)),
            (rgb_to_565(high), rgb_to_565(low)),
            (
                rgb_to_565(pixels[farthest[1]]),
                rgb_to_565(pixels[farthest[2]]),
            ),
        }
    )


def endpoint_neighbors(value: int) -> list[int]:
    red = (value >> 11) & 31
    green = (value >> 5) & 63
    blue = value & 31
    values = {value}
    for red_delta, green_delta, blue_delta in (
        (-1, 0, 0),
        (1, 0, 0),
        (0, -1, 0),
        (0, 1, 0),
        (0, 0, -1),
        (0, 0, 1),
    ):
        values.add(
            (max(0, min(31, red + red_delta)) << 11)
            | (max(0, min(63, green + green_delta)) << 5)
            | max(0, min(31, blue + blue_delta))
        )
    return sorted(values)


def encode_color_block(pixels: list[tuple[int, int, int]]) -> bytes:
    best: tuple[int, int, int, int] | None = None
    seeds = endpoint_seed_pairs(pixels)
    for first_seed, second_seed in seeds:
        for first in endpoint_neighbors(first_seed):
            for second in endpoint_neighbors(second_seed):
                endpoint0, endpoint1 = max(first, second), min(first, second)
                if endpoint0 == endpoint1:
                    continue
                error, indices = color_error(pixels, endpoint0, endpoint1)
                score = (error, endpoint0, endpoint1, indices)
                if best is None or score < best:
                    best = score

    if best is None:
        value = rgb_to_565(pixels[0])
        endpoint0 = value + 1 if value < 0xFFFF else value
        endpoint1 = value if value < 0xFFFF else value - 1
        _, indices = color_error(pixels, endpoint0, endpoint1)
    else:
        _, endpoint0, endpoint1, indices = best
    return struct.pack("<HHI", endpoint0, endpoint1, indices)


def encode_dxt3_level(
    image: Image.Image, *, alpha_encoding: AlphaEncoding
) -> bytes:
    if not isinstance(alpha_encoding, AlphaEncoding):
        raise TypeError("alpha_encoding must be an AlphaEncoding value")
    rgba = image.convert("RGBA")
    payload = bytearray()
    for block_y in range(0, rgba.height, 4):
        for block_x in range(0, rgba.width, 4):
            block: list[tuple[int, int, int, int]] = []
            for pixel_index in range(16):
                x = min(rgba.width - 1, block_x + pixel_index % 4)
                y = min(rgba.height - 1, block_y + pixel_index // 4)
                block.append(rgba.getpixel((x, y)))

            alpha_bits = 0
            if alpha_encoding is AlphaEncoding.RGBA:
                for pixel_index, pixel in enumerate(block):
                    alpha_bits |= min(15, (pixel[3] + 8) // 17) << (
                        pixel_index * 4
                    )
            payload.extend(alpha_bits.to_bytes(8, "little"))
            payload.extend(encode_color_block([pixel[:3] for pixel in block]))

    expected = 16 * max(1, (rgba.width + 3) // 4) * max(
        1, (rgba.height + 3) // 4
    )
    if len(payload) != expected:
        raise ValueError(f"Compressed size mismatch for {rgba.size}: {len(payload)} != {expected}")
    return bytes(payload)


def build_header(width: int = 128, height: int = 128, mip_count: int = 8) -> bytes:
    linear_size = max(1, (width + 3) // 4) * max(1, (height + 3) // 4) * 16
    values = [
        124,
        0x000A1007,
        height,
        width,
        linear_size,
        0,
        mip_count,
        *([0] * 11),
        32,
        0x4,
        struct.unpack("<I", FOURCC)[0],
        0,
        0,
        0,
        0,
        0,
        0x00401008,
        0,
        0,
        0,
        0,
    ]
    header = DDS_MAGIC + struct.pack("<31I", *values)
    if len(header) != HEADER_BYTES:
        raise AssertionError(f"DDS header is {len(header)} bytes, expected {HEADER_BYTES}")
    return header


def mip_dimensions(width: int, height: int, mip_count: int) -> list[tuple[int, int]]:
    return [
        (max(1, width >> index), max(1, height >> index))
        for index in range(mip_count)
    ]


def encode_image(
    image: Image.Image, *, alpha_encoding: AlphaEncoding
) -> tuple[bytes, list[dict[str, object]]]:
    if not isinstance(alpha_encoding, AlphaEncoding):
        raise TypeError("alpha_encoding must be an AlphaEncoding value")
    base = image.convert("RGBA")
    if base.size != BASE_SIZE:
        raise ValueError(f"Input must be exactly 128x128 RGBA-compatible; got {base.size}")

    levels: list[bytes] = []
    records: list[dict[str, object]] = []
    for index, dimensions in enumerate(mip_dimensions(*BASE_SIZE, MIP_COUNT)):
        started = time.perf_counter()
        level = (
            base
            if index == 0
            else base.resize(dimensions, Image.Resampling.LANCZOS)
        )
        encoded = encode_dxt3_level(level, alpha_encoding=alpha_encoding)
        levels.append(encoded)
        records.append(
            {
                "event": "mip_encoded",
                "alpha_encoding": alpha_encoding.value,
                "mip_index": index,
                "mip_total": MIP_COUNT,
                "width": dimensions[0],
                "height": dimensions[1],
                "input_pixels": dimensions[0] * dimensions[1],
                "output_bytes": len(encoded),
                "duration_ms": round((time.perf_counter() - started) * 1000, 3),
                "status": "success",
                "retry_count": 0,
            }
        )
    data = build_header(*BASE_SIZE, MIP_COUNT) + b"".join(levels)
    validate_dds(data)
    return data, records


def alpha_block_summary(data: bytes) -> list[dict[str, object]]:
    fields = validate_dds(data)
    dimensions = mip_dimensions(
        int(fields["width"]), int(fields["height"]), int(fields["mip_count"])
    )
    summaries: list[dict[str, object]] = []
    offset = HEADER_BYTES
    for mip_index, (width, height) in enumerate(dimensions):
        block_count = max(1, (width + 3) // 4) * max(1, (height + 3) // 4)
        alpha_words = [
            int.from_bytes(
                data[offset + block_index * 16 : offset + block_index * 16 + 8],
                "little",
            )
            for block_index in range(block_count)
        ]
        alpha_nibbles = {
            (word >> (texel_index * 4)) & 0xF
            for word in alpha_words
            for texel_index in range(16)
        }
        nonzero_texel_count = sum(
            (word >> (texel_index * 4)) & 0xF != 0
            for word in alpha_words
            for texel_index in range(16)
        )
        summaries.append(
            {
                "mip_index": mip_index,
                "width": width,
                "height": height,
                "block_count": block_count,
                "raw_alpha_words": sorted(set(alpha_words)),
                "raw_alpha_nibbles": sorted(alpha_nibbles),
                "nonzero_alpha_texel_count": nonzero_texel_count,
            }
        )
        offset += block_count * 16
    return summaries


def validate_dds(data: bytes) -> dict[str, object]:
    if len(data) < HEADER_BYTES or data[:4] != DDS_MAGIC:
        raise ValueError("Invalid DDS magic or truncated header")
    (
        header_size,
        flags,
        height,
        width,
        linear_size,
        depth,
        mip_count,
    ) = struct.unpack_from("<7I", data, 4)
    pixel_format_size, pixel_format_flags = struct.unpack_from("<II", data, 76)
    fourcc = data[84:88]
    caps = struct.unpack_from("<I", data, 108)[0]
    expected_payload = sum(
        16 * max(1, (mip_width + 3) // 4) * max(1, (mip_height + 3) // 4)
        for mip_width, mip_height in mip_dimensions(width, height, mip_count)
    )
    errors = []
    if header_size != 124:
        errors.append(f"header size {header_size}")
    if (width, height) != BASE_SIZE:
        errors.append(f"dimensions {width}x{height}")
    if mip_count != MIP_COUNT:
        errors.append(f"mip count {mip_count}")
    if fourcc != FOURCC:
        errors.append(f"fourcc {fourcc!r}")
    if pixel_format_size != 32 or not pixel_format_flags & 0x4:
        errors.append("invalid compressed pixel format")
    if linear_size != 16 * 32 * 32:
        errors.append(f"linear size {linear_size}")
    if len(data) != HEADER_BYTES + expected_payload:
        errors.append(f"file bytes {len(data)}")
    if not flags & 0x20000 or not caps & 0x400000:
        errors.append("mipmap flags/caps missing")
    if depth != 0:
        errors.append(f"unexpected depth {depth}")
    if errors:
        raise ValueError("Invalid DXT3 DDS: " + ", ".join(errors))
    return {
        "width": width,
        "height": height,
        "mip_count": mip_count,
        "fourcc": fourcc.decode("ascii"),
        "linear_size": linear_size,
        "payload_bytes": expected_payload,
        "file_bytes": len(data),
    }


def decode_dxt3_level(data: bytes, width: int, height: int) -> Image.Image:
    expected = 16 * max(1, (width + 3) // 4) * max(1, (height + 3) // 4)
    if len(data) != expected:
        raise ValueError(f"Level payload is {len(data)} bytes, expected {expected}")
    image = Image.new("RGBA", (width, height))
    offset = 0
    for block_y in range(0, height, 4):
        for block_x in range(0, width, 4):
            alpha_bits = int.from_bytes(data[offset : offset + 8], "little")
            endpoint0, endpoint1, indices = struct.unpack_from("<HHI", data, offset + 8)
            palette = color_palette(endpoint0, endpoint1)
            offset += 16
            for pixel_index in range(16):
                x = block_x + pixel_index % 4
                y = block_y + pixel_index // 4
                if x >= width or y >= height:
                    continue
                color = palette[(indices >> (pixel_index * 2)) & 0x3]
                alpha = ((alpha_bits >> (pixel_index * 4)) & 0xF) * 17
                image.putpixel((x, y), (*color, alpha))
    return image


def decode_dds(data: bytes, mip_index: int = 0) -> Image.Image:
    fields = validate_dds(data)
    dimensions = mip_dimensions(
        int(fields["width"]), int(fields["height"]), int(fields["mip_count"])
    )
    if not 0 <= mip_index < len(dimensions):
        raise ValueError(f"Mip index {mip_index} is out of range")
    offset = HEADER_BYTES
    for index, (width, height) in enumerate(dimensions):
        size = 16 * max(1, (width + 3) // 4) * max(1, (height + 3) // 4)
        if index == mip_index:
            return decode_dxt3_level(data[offset : offset + size], width, height)
        offset += size
    raise AssertionError("Mip traversal failed")


def fidelity_metrics(reference: Image.Image, decoded: Image.Image) -> dict[str, object]:
    reference_bytes = reference.convert("RGBA").tobytes()
    decoded_bytes = decoded.convert("RGBA").tobytes()
    channel_errors = [[], [], [], []]
    for offset in range(0, len(reference_bytes), 4):
        for channel in range(4):
            channel_errors[channel].append(
                abs(reference_bytes[offset + channel] - decoded_bytes[offset + channel])
            )
    names = ("red", "green", "blue", "alpha")
    result: dict[str, object] = {}
    for name, errors in zip(names, channel_errors):
        mse = sum(error * error for error in errors) / len(errors)
        result[name] = {
            "mae": round(sum(errors) / len(errors), 4),
            "rmse": round(math.sqrt(mse), 4),
            "max_abs": max(errors),
            "psnr_db": None if mse == 0 else round(20 * math.log10(255 / math.sqrt(mse)), 4),
        }
    rgb_errors = channel_errors[0] + channel_errors[1] + channel_errors[2]
    rgb_mse = sum(error * error for error in rgb_errors) / len(rgb_errors)
    result["rgb"] = {
        "mae": round(sum(rgb_errors) / len(rgb_errors), 4),
        "rmse": round(math.sqrt(rgb_mse), 4),
        "max_abs": max(rgb_errors),
        "psnr_db": None
        if rgb_mse == 0
        else round(20 * math.log10(255 / math.sqrt(rgb_mse)), 4),
    }
    return result


def emit(record: dict[str, object], log_path: Path | None) -> None:
    complete = {"timestamp": utc_now(), **record}
    line = json.dumps(complete, sort_keys=True)
    print(line, flush=True)
    if log_path is not None:
        with log_path.open("a", encoding="utf-8") as stream:
            stream.write(line + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Deterministic full-color DXT3 encoder")
    parser.add_argument("input", type=Path, help="128x128 RGBA-compatible source image")
    parser.add_argument("output", type=Path, help="DDS output path")
    parser.add_argument(
        "--alpha-encoding",
        required=True,
        choices=[encoding.value for encoding in AlphaEncoding],
        help=(
            "Use fixed-color-zero-alpha for Civ IV bWhiteFlag=1 production flags; "
            "use rgba only for conventional alpha-preserving DXT3"
        ),
    )
    parser.add_argument("--decoded-preview", type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--log", type=Path)
    parser.add_argument("--batch-index", type=int, default=1)
    parser.add_argument("--batch-total", type=int, default=1)
    args = parser.parse_args()
    alpha_encoding = AlphaEncoding(args.alpha_encoding)

    started = time.perf_counter()
    if args.log:
        args.log.parent.mkdir(parents=True, exist_ok=True)
        args.log.write_text("", encoding="utf-8")
    emit(
        {
            "event": "batch_started",
            "batch_index": args.batch_index,
            "batch_total": args.batch_total,
            "input": str(args.input.resolve()),
            "output": str(args.output.resolve()),
            "alpha_encoding": alpha_encoding.value,
            "retry_count": 0,
        },
        args.log,
    )
    with Image.open(args.input) as source:
        reference = source.convert("RGBA")
    data, mip_records = encode_image(
        reference, alpha_encoding=alpha_encoding
    )
    for record in mip_records:
        emit(record, args.log)
    decoded = decode_dds(data)
    metrics = fidelity_metrics(reference, decoded)
    alpha_summary = alpha_block_summary(data)
    nonzero_alpha_texel_count = sum(
        int(mip["nonzero_alpha_texel_count"]) for mip in alpha_summary
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(data)
    if args.output.read_bytes() != data:
        raise IOError("Persisted DDS bytes differ from generated bytes")
    if args.decoded_preview:
        args.decoded_preview.parent.mkdir(parents=True, exist_ok=True)
        decoded.save(args.decoded_preview)

    rgb_psnr = metrics["rgb"]["psnr_db"]
    rgb_passed = rgb_psnr is None or rgb_psnr >= 20.0
    report = {
        "schema_version": 1,
        "input": str(args.input.resolve()),
        "output": str(args.output.resolve()),
        "input_bytes": args.input.stat().st_size,
        "output_bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "alpha_encoding": alpha_encoding.value,
        "header": validate_dds(data),
        "alpha_blocks": alpha_summary,
        "fidelity": metrics,
        "pass_criteria": {
            "deterministic": True,
            "rgb_psnr_min_db": 20.0,
            "alpha": (
                "all encoded DXT3 alpha nibbles equal 0"
                if alpha_encoding is AlphaEncoding.FIXED_COLOR_ZERO
                else "source-to-decoded alpha max absolute error <= 8"
            ),
        },
        "passed": rgb_passed
        and (
            nonzero_alpha_texel_count == 0
            if alpha_encoding is AlphaEncoding.FIXED_COLOR_ZERO
            else metrics["alpha"]["max_abs"] <= 8
        ),
    }
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    emit(
        {
            "event": "batch_summary",
            "batch_index": args.batch_index,
            "batch_total": args.batch_total,
            "expected_total": 1,
            "processed_total": 1,
            "persisted_total": 1,
            "dropped_total": 0,
            "skipped_total": 0,
            "duplicate_total": 0,
            "error_total": 0,
            "input_bytes": args.input.stat().st_size,
            "output_bytes": len(data),
            "sha256": report["sha256"],
            "alpha_encoding": alpha_encoding.value,
            "rgb_psnr_db": rgb_psnr,
            "source_to_decoded_alpha_max_abs": metrics["alpha"]["max_abs"],
            "nonzero_alpha_texel_count": nonzero_alpha_texel_count,
            "duration_ms": round((time.perf_counter() - started) * 1000, 3),
            "status": "success" if report["passed"] else "failure",
            "passed": report["passed"],
        },
        args.log,
    )
    if not report["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
