from __future__ import annotations

import argparse
import json
import os
import tempfile
import time
import traceback
import uuid
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dxt3_fullcolor import (
    AlphaEncoding,
    alpha_block_summary,
    encode_image,
    validate_dds,
)
from flag_pipeline import (
    ART_XML,
    REPO_ROOT,
    asset_path,
    changed_civilizations,
    records_by_civilization,
    repository_path,
    rasterize_master,
    parse_live_mappings,
    set_fixed_color_flags,
    sha256_bytes,
    validate_manifest_against_live,
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def encode_record(record: dict[str, Any]) -> dict[str, Any]:
    started_at = utc_now()
    started = time.perf_counter()
    try:
        master = repository_path(str(record["master_path"]))
        image = rasterize_master(master)
        data, mip_records = encode_image(
            image,
            alpha_encoding=AlphaEncoding.FIXED_COLOR_ZERO,
        )
        alpha = alpha_block_summary(data)
        return {
            "civilization_type": record["civilization_type"],
            "status": "success",
            "started_at": started_at,
            "ended_at": utc_now(),
            "duration_ms": round((time.perf_counter() - started) * 1000, 3),
            "input_bytes": master.stat().st_size,
            "output_bytes": len(data),
            "sha256": sha256_bytes(data),
            "header": validate_dds(data),
            "nonzero_alpha_texel_count": sum(
                int(mip["nonzero_alpha_texel_count"]) for mip in alpha
            ),
            "mip_records": mip_records,
            "data": data,
        }
    except Exception as error:
        return {
            "civilization_type": record.get("civilization_type"),
            "status": "error",
            "started_at": started_at,
            "ended_at": utc_now(),
            "duration_ms": round((time.perf_counter() - started) * 1000, 3),
            "error": f"{type(error).__name__}: {error}",
            "traceback": traceback.format_exc(),
        }


def emit(event: dict[str, Any], log_path: Path | None) -> None:
    record = {"timestamp": utc_now(), **event}
    print(json.dumps(record, sort_keys=True), flush=True)
    if log_path is not None:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(record, sort_keys=True) + "\n")


def select_civilizations(args: argparse.Namespace) -> tuple[list[str], bool]:
    records = records_by_civilization()
    if args.civilization:
        if args.civilization not in records:
            raise ValueError(f"Unknown civilization: {args.civilization}")
        return [args.civilization], False
    if args.changed:
        return changed_civilizations(), False
    return sorted(records), bool(args.check)


def publish_transaction(
    selected: list[str],
    records: dict[str, dict[str, Any]],
    results: dict[str, dict[str, Any]],
) -> int:
    originals: dict[Path, bytes | None] = {}
    staged: dict[Path, Path] = {}
    original_xml = ART_XML.read_bytes()
    try:
        for civilization_type in selected:
            destination = asset_path(
                str(records[civilization_type]["runtime_dds_path"])
            )
            destination.parent.mkdir(parents=True, exist_ok=True)
            originals[destination] = (
                destination.read_bytes() if destination.is_file() else None
            )
            temporary = destination.with_name(
                f".{destination.name}.{uuid.uuid4().hex}.tmp"
            )
            temporary.write_bytes(results[civilization_type]["data"])
            if temporary.read_bytes() != results[civilization_type]["data"]:
                raise IOError(f"Staged bytes differ for {civilization_type}")
            staged[destination] = temporary

        for destination, temporary in staged.items():
            os.replace(temporary, destination)

        xml_changes = set_fixed_color_flags(set(selected))
        _, art_by_type = parse_live_mappings()
        for civilization_type in selected:
            art_define = str(records[civilization_type]["art_define"])
            if art_by_type[art_define]["white_flag"] != "1":
                raise ValueError(
                    f"{civilization_type}/{art_define} was not enabled"
                )
        return xml_changes
    except Exception:
        for destination, original in originals.items():
            if original is None:
                destination.unlink(missing_ok=True)
            else:
                rollback = destination.with_name(
                    f".{destination.name}.{uuid.uuid4().hex}.rollback"
                )
                rollback.write_bytes(original)
                os.replace(rollback, destination)
        ART_XML.write_bytes(original_xml)
        raise
    finally:
        for temporary in staged.values():
            temporary.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build deterministic Civ4 historical full-color flags"
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--check",
        action="store_true",
        help="Rebuild all 59 in temporary storage and compare expected/live bytes",
    )
    mode.add_argument("--all", action="store_true", help="Write all 59 runtime DDS files")
    mode.add_argument(
        "--civilization",
        help="Write one exact CIVILIZATION_* target",
    )
    mode.add_argument(
        "--changed",
        action="store_true",
        help="Write targets whose masters or manifest differ from HEAD",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=max(1, min(8, os.cpu_count() or 1)),
    )
    parser.add_argument(
        "--log",
        type=Path,
        default=REPO_ROOT / "tmp" / "flags" / "build-log.jsonl",
    )
    args = parser.parse_args()
    if not (args.check or args.all or args.civilization or args.changed):
        args.check = True
    if args.workers < 1:
        parser.error("--workers must be at least 1")

    selected, check_only = select_civilizations(args)
    if args.log:
        args.log.parent.mkdir(parents=True, exist_ok=True)
        args.log.write_text("", encoding="utf-8")
    emit(
        {
            "event": "batch_started",
            "mode": (
                "check"
                if check_only
                else "changed"
                if args.changed
                else "single"
                if args.civilization
                else "all"
            ),
            "batch_total": len(selected),
            "workers": args.workers,
            "retry_count": 0,
        },
        args.log,
    )
    if not selected:
        emit(
            {
                "event": "batch_summary",
                "expected_total": 0,
                "processed_total": 0,
                "persisted_total": 0,
                "skipped_total": 0,
                "duplicate_total": 0,
                "error_total": 0,
                "input_bytes": 0,
                "output_bytes": 0,
                "status": "success",
                "passed": True,
            },
            args.log,
        )
        return

    validate_manifest_against_live(require_fixed_color=check_only)
    records = records_by_civilization()
    ordered_records = [records[civilization_type] for civilization_type in selected]
    started = time.perf_counter()
    results: dict[str, dict[str, Any]] = {}
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(encode_record, record): str(record["civilization_type"])
            for record in ordered_records
        }
        for future in as_completed(futures):
            civilization_type = futures[future]
            result = future.result()
            results[civilization_type] = result
            emit(
                {
                    "event": "flag_encoded",
                    "batch_index": selected.index(civilization_type) + 1,
                    "batch_total": len(selected),
                    **{key: value for key, value in result.items() if key != "data"},
                    "retry_count": 0,
                },
                args.log,
            )

    errors: list[str] = []
    persisted = 0
    total_input_bytes = 0
    total_output_bytes = 0
    generated: dict[str, bytes] = {}
    temporary_root = Path(tempfile.mkdtemp(prefix="dowager-flags-")) if check_only else None
    try:
        for civilization_type in selected:
            record = records[civilization_type]
            result = results[civilization_type]
            if result["status"] != "success":
                errors.append(
                    f"{civilization_type}: {result.get('error', 'encoding failed')}"
                )
                continue
            data = result["data"]
            total_input_bytes += int(result["input_bytes"])
            total_output_bytes += int(result["output_bytes"])
            expected_sha = str(record["production_dds_sha256"])
            if result["sha256"] != expected_sha:
                errors.append(
                    f"{civilization_type}: generated sha256={result['sha256']}, "
                    f"expected={expected_sha}"
                )
                continue
            if result["nonzero_alpha_texel_count"] != 0:
                errors.append(f"{civilization_type}: generated nonzero DXT3 alpha")
                continue
            generated[civilization_type] = data
            if check_only:
                live_path = asset_path(str(record["runtime_dds_path"]))
                destination = temporary_root / f"{civilization_type}.dds"
                destination.write_bytes(data)
                if destination.read_bytes() != data:
                    errors.append(f"{civilization_type}: persisted bytes differ")
                    continue
                if not live_path.is_file():
                    errors.append(f"{civilization_type}: live DDS is missing")
                    continue
                if live_path.read_bytes() != data:
                    errors.append(
                        f"{civilization_type}: live DDS differs from deterministic build"
                    )
                    continue
        xml_changes = 0
        if not errors and len(generated) == len(selected):
            if check_only:
                persisted = len(selected)
            else:
                xml_changes = publish_transaction(selected, records, results)
                persisted = len(selected)
                validate_manifest_against_live(
                    require_fixed_color=len(selected) == len(records)
                )
    finally:
        if temporary_root is not None:
            for child in temporary_root.iterdir():
                child.unlink()
            temporary_root.rmdir()

    passed = not errors and persisted == len(selected)
    emit(
        {
            "event": "batch_summary",
            "expected_total": len(selected),
            "processed_total": len(results),
            "persisted_total": persisted,
            "skipped_total": 0,
            "duplicate_total": 0,
            "error_total": len(errors),
            "input_bytes": total_input_bytes,
            "output_bytes": total_output_bytes,
            "xml_values_changed": xml_changes,
            "duration_ms": round((time.perf_counter() - started) * 1000, 3),
            "errors": errors,
            "status": "success" if passed else "failure",
            "passed": passed,
        },
        args.log,
    )
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
