#!/usr/bin/env python3
"""Art inventory scanner for DowagerMod.

Phase 1 of the "LLM-suggested leaders/civs that reuse unused art" framework.

Cross-references the art model/texture files that physically exist under the BtS
``Assets/Art`` tree against every art path referenced by the XML, and emits a
catalog of *unused* art (candidate assets an LLM could reuse) plus a bonus report
of *dangling* references (referenced-but-missing paths = latent art-path crashes).

Pure standard library. Run from anywhere:

    python tools/art_inventory.py

Outputs (default under ``docs/art_inventory/``):
  * unused_art_manifest.json  -- rich, grouped, LLM-facing
  * unused_art_manifest.csv   -- flat per-asset rows
  * dangling_art_refs.csv     -- referenced paths with no file on disk
"""

import argparse
import csv
import json
import os
import re
import sys
from collections import defaultdict

ART_EXTENSIONS = (".nif", ".kfm", ".dds", ".tga")

# Candidate art trees scanned for UNUSED assets (relative to the Assets root,
# forward-slash, lowercase). Everything is scanned for dangling-ref existence,
# but only assets under these roots are proposed as reusable candidates.
DEFAULT_CANDIDATE_ROOTS = (
    "art/leaderheads",
    "art/units",
    "art/structures",
    "art/btg",
    "art/caveman2cosmos",
)

# Captures an art path from XML text: everything up to the extension that is not
# a tag boundary or comma (so folder names with spaces survive, and atlas-style
# ``<Button>,path.dds,6,12</Button>`` yields just ``path.dds``).
_ART_PATH_RE = re.compile(
    r"([^<>,\r\n\t]*?\.(?:nif|kfm|dds|tga))",
    re.IGNORECASE,
)

# Era / culture keyword dictionary for lightweight enrichment. Matched (as
# substrings) against the normalized folder + file tokens of each asset.
ERA_KEYWORDS = {
    "ancient": ["ancient", "sumer", "babylon", "egypt", "greek", "greece", "rome",
                "roman", "persia", "persian", "celt", "maya", "aztec", "inca",
                "classical", "antiquity", "hittite", "phoenician", "carthage"],
    "medieval": ["medieval", "middle_ages", "knight", "castle", "feudal",
                 "archbishop", "byzant", "crusad", "viking", "norse", "samurai",
                 "gothic", "renaissance"],
    "colonial": ["colonial", "colonization", "conquistador", "musket",
                 "napoleon", "revolution", "frigate", "galleon"],
    "industrial": ["industrial", "steam", "victorian", "rifle", "cannon",
                   "ironclad", "railroad"],
    "modern": ["modern", "ww1", "ww2", "wwii", "tank", "infantry", "marine",
               "fighter", "bomber", "panzer", "gi_", "jet"],
    "future": ["future", "space", "mech", "laser", "robot", "cyber", "nano"],
}

CULTURE_KEYWORDS = {
    "european": ["europe", "english", "britain", "french", "german", "spanish",
                 "italian", "dutch", "portug", "russia", "greek", "roman",
                 "byzant", "viking", "norse", "celt", "napoleon", "victoria"],
    "asian": ["china", "chinese", "japan", "japanese", "korea", "korean",
              "mongol", "khan", "india", "indian", "asian", "samurai", "qin",
              "han_", "tang", "ming"],
    "middle_eastern": ["arab", "persia", "persian", "ottoman", "turk", "islam",
                       "babylon", "sumer", "assyr", "egypt", "mamluk", "moor"],
    "african": ["africa", "african", "zulu", "mali", "ethiopia", "songhai",
                "nubia", "aksum"],
    "american": ["america", "native", "sioux", "apache", "maya", "aztec",
                 "inca", "iroquois", "comanche"],
}


def norm(path):
    """Normalize an art path for set comparison."""
    p = path.strip().replace("\\", "/").lower()
    while p.startswith("./"):
        p = p[2:]
    return p


def find_assets_root(repo_root):
    candidate = os.path.join(
        repo_root,
        "CoreFiles",
        "Sid Meier's Civilization IV Beyond the Sword",
        "Beyond the Sword",
        "Assets",
    )
    return candidate


def collect_referenced(xml_root):
    """Return (referenced_norm_set, referenced_examples) from all XML under xml_root."""
    referenced = set()
    for dirpath, _dirs, files in os.walk(xml_root):
        for fn in files:
            if not fn.lower().endswith(".xml"):
                continue
            full = os.path.join(dirpath, fn)
            try:
                with open(full, "r", encoding="utf-8", errors="replace") as fh:
                    text = fh.read()
            except OSError:
                continue
            for match in _ART_PATH_RE.finditer(text):
                token = match.group(1).strip()
                if not token:
                    continue
                referenced.add(norm(token))
    return referenced


def collect_ondisk(art_root, assets_root):
    """Return {normalized_relpath: relpath} for all art files under art_root."""
    ondisk = {}
    for dirpath, _dirs, files in os.walk(art_root):
        for fn in files:
            if not fn.lower().endswith(ART_EXTENSIONS):
                continue
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, assets_root).replace("\\", "/")
            ondisk[norm(rel)] = rel
    return ondisk


def source_tier(nrel):
    if nrel.startswith("art/btg/"):
        return "BTG"
    if nrel.startswith("art/caveman2cosmos/"):
        return "caveman2cosmos"
    return "base-game"


def classify(nrel, ext):
    segs = nrel.split("/")
    joined = "/" + nrel
    if ext == ".kfm" or "/leaderheads/" in joined:
        # .kfm outside leaderheads is usually a unit animation; disambiguate below.
        if "/leaderheads/" in joined:
            return "leaderhead"
    if "/custom_leaderheads/" in joined:
        return "leaderhead"
    if "/units/" in joined or "/unit/" in joined:
        return "unit"
    if "/structures/" in joined or "/buildings/" in joined or "/building/" in joined:
        return "building"
    if ext == ".kfm":
        return "unit"
    return "other"


def infer_name(nrel):
    base = nrel.split("/")[-1]
    stem = re.sub(r"\.(nif|kfm|dds|tga)$", "", base, flags=re.IGNORECASE)
    parent = nrel.split("/")[-2] if "/" in nrel else ""
    label = stem or parent
    label = label.replace("_", " ").replace("-", " ").strip()
    return label, parent


def match_keywords(text, table):
    hits = []
    for label, kws in table.items():
        for kw in kws:
            if kw in text:
                hits.append(label)
                break
    return hits


def build_asset_record(nrel, rel):
    ext = os.path.splitext(nrel)[1].lower()
    kind = classify(nrel, ext)
    name, folder = infer_name(nrel)
    tier = source_tier(nrel)
    key_text = nrel
    eras = match_keywords(key_text, ERA_KEYWORDS)
    cultures = match_keywords(key_text, CULTURE_KEYWORDS)
    return {
        "type": kind,
        "path": rel,
        "source_tier": tier,
        "inferred_name": name,
        "folder": folder,
        "ext": ext,
        "era_hints": eras,
        "culture_hints": cultures,
    }


def is_candidate(nrel, candidate_roots):
    return any(nrel.startswith(root + "/") for root in candidate_roots)


def group_leaderheads(unused_records, referenced):
    """Cluster unused leaderhead art by folder.

    A folder is a genuine reuse candidate only if it contains at least one model
    file (.nif/.kfm) and NONE of that folder's models are referenced by the XML.
    Folders that are already in use (but happen to have stray unreferenced
    texture files) are counted separately, not offered as candidates.
    """
    # Folders (normalized) that contain a referenced leaderhead model.
    used_lh_folders = set()
    for nref in referenced:
        joined = "/" + nref
        if "/leaderheads/" not in joined and "/custom_leaderheads/" not in joined:
            continue
        if not nref.endswith((".nif", ".kfm")):
            continue
        used_lh_folders.add(os.path.dirname(nref))

    lh_by_folder = defaultdict(list)
    units = []
    buildings = []
    for rec in unused_records:
        if rec["type"] == "leaderhead":
            folder = os.path.dirname(rec["path"]).replace("\\", "/")
            lh_by_folder[folder].append(rec)
        elif rec["type"] == "unit":
            units.append(rec)
        elif rec["type"] == "building":
            buildings.append(rec)

    def tokens(text):
        return set(t for t in re.split(r"[^a-z0-9]+", text.lower()) if len(t) > 2)

    groups = []
    portrait_only = []
    in_use_with_stray = 0
    for folder, recs in sorted(lh_by_folder.items()):
        folder_norm = norm(folder)
        has_model = any(r["ext"] in (".nif", ".kfm") for r in recs)
        folder_name = folder.split("/")[-1]
        if folder_norm in used_lh_folders:
            in_use_with_stray += 1
            continue
        if not has_model:
            # DDS-only leaderhead portrait (e.g. C2C custom_leaderheads); usable
            # only if paired with a generic diplomacy model. Surfaced separately.
            dds = sorted(r["path"] for r in recs if r["ext"] == ".dds")
            if dds:
                portrait_only.append({
                    "leaderhead_folder": folder,
                    "leader_label": folder_name.replace("_", " ").strip(),
                    "source_tier": recs[0]["source_tier"],
                    "era_hints": sorted({e for r in recs for e in r["era_hints"]}),
                    "culture_hints": sorted({c for r in recs for c in r["culture_hints"]}),
                    "portrait_files": dds,
                })
            continue

        ftoks = tokens(folder_name)
        eras = sorted({e for r in recs for e in r["era_hints"]})
        cultures = sorted({c for r in recs for c in r["culture_hints"]})
        tier = recs[0]["source_tier"]

        def near(pool):
            out = []
            for r in pool:
                if r["source_tier"] != tier:
                    continue
                rtoks = tokens(r["folder"] + " " + r["inferred_name"])
                if ftoks & rtoks:
                    out.append(r["path"])
            return sorted(out)[:12]

        groups.append({
            "leaderhead_folder": folder,
            "leader_label": folder_name.replace("_", " ").strip(),
            "source_tier": tier,
            "era_hints": eras,
            "culture_hints": cultures,
            "model_files": sorted(r["path"] for r in recs
                                  if r["ext"] in (".nif", ".kfm")),
            "art_files": sorted(r["path"] for r in recs),
            "candidate_units": near(units),
            "candidate_buildings": near(buildings),
        })
    return groups, portrait_only, {
        "leaderhead_folders_in_use_with_stray_files": in_use_with_stray,
        "portrait_only_leaderhead_folders": len(portrait_only),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Scan for unused Civ4 art assets.")
    here = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(here)
    parser.add_argument("--repo-root", default=repo_root)
    parser.add_argument("--assets-root", default=None,
                        help="Override the BtS Assets root.")
    parser.add_argument("--candidate-roots", nargs="*",
                        default=list(DEFAULT_CANDIDATE_ROOTS),
                        help="Assets-relative art roots scanned for unused candidates.")
    parser.add_argument("--out-dir", default=None,
                        help="Output dir (default docs/art_inventory).")
    args = parser.parse_args(argv)

    assets_root = args.assets_root or find_assets_root(args.repo_root)
    xml_root = os.path.join(assets_root, "XML")
    art_root = os.path.join(assets_root, "Art")
    out_dir = args.out_dir or os.path.join(args.repo_root, "docs", "art_inventory")

    if not os.path.isdir(assets_root):
        print("ERROR: assets root not found: %s" % assets_root, file=sys.stderr)
        return 2
    if not os.path.isdir(art_root):
        print("ERROR: art root not found: %s" % art_root, file=sys.stderr)
        return 2

    print("[art-inventory] assets root: %s" % assets_root)
    print("[art-inventory] scanning referenced art paths in XML ...")
    referenced = collect_referenced(xml_root)
    print("[art-inventory]   referenced art tokens: %d" % len(referenced))

    print("[art-inventory] enumerating on-disk art under Assets/Art ...")
    ondisk = collect_ondisk(art_root, assets_root)
    print("[art-inventory]   on-disk art files: %d" % len(ondisk))

    candidate_roots = [norm(r) for r in args.candidate_roots]

    # Unused = on-disk candidate-root files with no XML reference.
    unused_records = []
    for nrel, rel in ondisk.items():
        if nrel in referenced:
            continue
        if not is_candidate(nrel, candidate_roots):
            continue
        unused_records.append(build_asset_record(nrel, rel))

    # Dangling = path-like referenced tokens under art/ that exist in no file on disk.
    dangling = []
    for nref in sorted(referenced):
        if "/" not in nref or not nref.startswith("art/"):
            continue
        if nref not in ondisk:
            dangling.append(nref)

    # Self-check: how many distinct referenced leaderhead .kfm/.nif do we see?
    ref_lh = sum(1 for r in referenced
                 if r.startswith("art/leaderheads/") and r.endswith((".nif", ".kfm")))

    groups, portrait_only, lh_stats = group_leaderheads(unused_records, referenced)

    # Tallies.
    by_type = defaultdict(int)
    by_tier = defaultdict(int)
    for r in unused_records:
        by_type[r["type"]] += 1
        by_tier[r["source_tier"]] += 1

    os.makedirs(out_dir, exist_ok=True)

    manifest = {
        "summary": {
            "referenced_art_tokens": len(referenced),
            "ondisk_art_files": len(ondisk),
            "unused_candidate_assets": len(unused_records),
            "unused_by_type": dict(sorted(by_type.items())),
            "unused_by_source_tier": dict(sorted(by_tier.items())),
            "dangling_references": len(dangling),
            "referenced_leaderhead_models": ref_lh,
            "candidate_leaderhead_folders": len(groups),
            "leaderhead_folders_in_use_with_stray_files":
                lh_stats["leaderhead_folders_in_use_with_stray_files"],
            "portrait_only_leaderhead_folders":
                lh_stats["portrait_only_leaderhead_folders"],
            "candidate_roots": candidate_roots,
            "notes": [
                "unused = on-disk art under candidate_roots with no XML reference.",
                "dangling is NOISY in this repo: stock art lives in git-excluded "
                ".fpk archives, so many 'missing' interface/terrain/unit refs are "
                "false positives. Interpret with the .fpk caveat; do NOT gate on it.",
                "leaderhead groups exclude folders already in use and folders "
                "without a .nif/.kfm model.",
                "full per-asset unit/building/other rows are in "
                "unused_art_manifest.csv, not duplicated in this JSON.",
            ],
        },
        "unused_leaderhead_groups": groups,
        "portrait_only_leaderhead_folders": portrait_only,
    }
    # Note: exhaustive per-asset unit/building/other listings are intentionally
    # NOT duplicated here (they live in unused_art_manifest.csv). The JSON stays a
    # tight, LLM-facing grouped view; leaderhead groups already embed the most
    # relevant candidate_units / candidate_buildings by path.

    json_path = os.path.join(out_dir, "unused_art_manifest.json")
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2, ensure_ascii=False)

    csv_path = os.path.join(out_dir, "unused_art_manifest.csv")
    with open(csv_path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["type", "source_tier", "inferred_name", "folder",
                         "ext", "era_hints", "culture_hints", "path"])
        for r in sorted(unused_records, key=lambda r: (r["type"], r["path"])):
            writer.writerow([
                r["type"], r["source_tier"], r["inferred_name"], r["folder"],
                r["ext"], ";".join(r["era_hints"]), ";".join(r["culture_hints"]),
                r["path"],
            ])

    dangling_path = os.path.join(out_dir, "dangling_art_refs.csv")
    with open(dangling_path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["referenced_path"])
        for d in dangling:
            writer.writerow([d])

    print("")
    print("[art-inventory] === SUMMARY ===")
    print("  referenced art tokens : %d" % len(referenced))
    print("  on-disk art files     : %d" % len(ondisk))
    print("  unused candidates     : %d" % len(unused_records))
    for t, n in sorted(by_type.items()):
        print("      %-10s : %d" % (t, n))
    print("  by source tier        :")
    for t, n in sorted(by_tier.items()):
        print("      %-14s : %d" % (t, n))
    print("  leaderhead groups     : %d (candidate, fully-unused folders)" % len(groups))
    print("      in-use folders w/ stray files : %d" %
          lh_stats["leaderhead_folders_in_use_with_stray_files"])
    print("      portrait-only (DDS, no model) : %d" %
          lh_stats["portrait_only_leaderhead_folders"])
    print("  dangling references   : %d (NOISY - stock art is in .fpk; not gate-worthy)"
          % len(dangling))
    print("  referenced leaderhead models : %d" % ref_lh)
    print("")
    print("[art-inventory] wrote:")
    print("  %s" % json_path)
    print("  %s" % csv_path)
    print("  %s" % dangling_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
