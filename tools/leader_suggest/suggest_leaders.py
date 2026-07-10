#!/usr/bin/env python3
"""Leader/Civ suggestion harness (Phase 2).

Turns the unused-art manifest (Phase 1, ``tools/art_inventory.py``) into an
LLM-ready prompt, and validates the LLM's structured proposals back against the
manifest and the live game data.

Core pattern (per repo owner): each NEW leader gets exactly ONE bespoke custom
trait and is paired 1:1 with a single civilization, so the leader+civ+trait
triple is designed together.

Subcommands
-----------
  build-input   Read the manifest + live XML context, pick a curated set of
                unused leaderhead candidates, and emit:
                  * prompt_input.json  (structured facts for the LLM)
                  * prompt.md          (filled instructions + candidate table)

  validate      Check a proposals JSON against suggestion_spec.schema.json and
                the live game data: unique new leader/civ/trait ids, valid
                civic/art-style, and leaderhead / UU / UB art that is actually
                unused and on disk (per the manifest CSV).

Pure standard library.
"""

import argparse
import csv
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(HERE))
SCHEMA_PATH = os.path.join(HERE, "suggestion_spec.schema.json")
TEMPLATE_PATH = os.path.join(HERE, "prompt_template.md")

TIER_WEIGHT = {"base-game": 3, "BTG": 2, "caveman2cosmos": 1}


def find_assets_root(repo_root):
    return os.path.join(
        repo_root, "CoreFiles",
        "Sid Meier's Civilization IV Beyond the Sword",
        "Beyond the Sword", "Assets")


def default_manifest_dir(repo_root):
    return os.path.join(repo_root, "docs", "art_inventory")


def norm(path):
    p = path.strip().replace("\\", "/").lower()
    while p.startswith("./"):
        p = p[2:]
    return p


# ---------------------------------------------------------------------------
# Live game context (read from XML so it stays current)
# ---------------------------------------------------------------------------

def _types_from(xml_path, pattern):
    out = []
    try:
        with open(xml_path, "r", encoding="utf-8", errors="replace") as fh:
            text = fh.read()
    except OSError:
        return out
    for m in re.finditer(pattern, text):
        out.append(m.group(1))
    return out


def load_game_context(assets_root):
    xml = os.path.join(assets_root, "XML")
    civdir = os.path.join(xml, "Civilizations")
    gameinfo = os.path.join(xml, "GameInfo")
    traits = _types_from(os.path.join(civdir, "CIV4TraitInfos.xml"),
                         r"<Type>(TRAIT_\w+)</Type>")
    leaders = _types_from(os.path.join(civdir, "CIV4LeaderHeadInfos.xml"),
                          r"<Type>(LEADER_\w+)</Type>")
    civs = _types_from(os.path.join(civdir, "CIV4CivilizationInfos.xml"),
                       r"<Type>(CIVILIZATION_\w+)</Type>")
    civics = _types_from(os.path.join(gameinfo, "CIV4CivicInfos.xml"),
                         r"<Type>(CIVIC_\w+)</Type>")
    civinfo_text = ""
    try:
        with open(os.path.join(civdir, "CIV4CivilizationInfos.xml"),
                  "r", encoding="utf-8", errors="replace") as fh:
            civinfo_text = fh.read()
    except OSError:
        pass
    art_styles = sorted(set(re.findall(r"ARTSTYLE_\w+", civinfo_text)))
    return {
        "existing_traits": sorted(set(traits)),
        "existing_leaders": sorted(set(leaders)),
        "existing_civilizations": sorted(set(civs)),
        "existing_civics": sorted(set(civics)),
        "art_styles": art_styles,
    }


# ---------------------------------------------------------------------------
# Manifest loading
# ---------------------------------------------------------------------------

def load_manifest(manifest_dir):
    with open(os.path.join(manifest_dir, "unused_art_manifest.json"),
              "r", encoding="utf-8") as fh:
        manifest = json.load(fh)
    unused_paths = set()
    by_type = {}
    csv_path = os.path.join(manifest_dir, "unused_art_manifest.csv")
    with open(csv_path, "r", encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            n = norm(row["path"])
            unused_paths.add(n)
            by_type[n] = row["type"]
    return manifest, unused_paths, by_type


# ---------------------------------------------------------------------------
# build-input
# ---------------------------------------------------------------------------

def score_group(g):
    s = TIER_WEIGHT.get(g.get("source_tier"), 0)
    if g.get("era_hints"):
        s += 1
    if g.get("culture_hints"):
        s += 1
    label = (g.get("leader_label") or "").strip()
    if len(label) >= 3 and re.search(r"[a-zA-Z]", label):
        s += 1
    return s


def pick_main_model(models, folder_name):
    """Choose the primary (nif, kfm) pair for a leaderhead folder.

    Avoids auxiliary models (_BG/background/noshader/boundshape/shadow) and
    prefers the model whose base name matches the folder and whose nif shares
    the kfm's base name (the Civ4 convention, e.g. victoria.nif + victoria.kfm).
    """
    def base(p):
        return re.sub(r"\.(nif|kfm)$", "", os.path.basename(p), flags=re.I).lower()

    def is_aux(p):
        b = base(p)
        return any(x in b for x in ("_bg", "background", "noshader",
                                    "boundshape", "shadow"))

    def toks(s):
        return set(t for t in re.split(r"[^a-z0-9]+", s.lower()) if t)

    ftoks = toks(folder_name)

    def folder_score(p):
        return len(toks(base(p)) & ftoks)

    def choose(cands):
        if not cands:
            return None
        return sorted(cands, key=lambda p: (is_aux(p), -folder_score(p),
                                            len(base(p))))[0]

    nifs = [p for p in models if p.lower().endswith(".nif")]
    kfms = [p for p in models if p.lower().endswith(".kfm")]

    # Preferred: a nif+kfm that share a base name (the Civ4 convention) and are
    # not auxiliary. These render as a coherent pair -> high confidence.
    shared = [(n, k) for n in nifs for k in kfms
              if base(n) == base(k) and not is_aux(n) and not is_aux(k)]
    if shared:
        n, k = sorted(shared, key=lambda pr: (-folder_score(pr[0]),
                                              len(base(pr[0]))))[0]
        return n, k, "high"

    # Fallback: pick separately (nif base may not match kfm) -> low confidence,
    # flagged so a human verifies the art before shipping.
    kfm = choose(kfms)
    nif = choose(nifs)
    return nif, kfm, "low"


def cmd_build_input(args):
    assets_root = args.assets_root or find_assets_root(args.repo_root)
    manifest_dir = args.manifest_dir or default_manifest_dir(args.repo_root)
    out_dir = args.out_dir or manifest_dir

    manifest, _unused, _bytype = load_manifest(manifest_dir)
    ctx = load_game_context(assets_root)

    groups = manifest.get("unused_leaderhead_groups", [])
    ranked = sorted(groups, key=lambda g: (-score_group(g),
                                           g.get("leaderhead_folder", "")))
    picked = ranked[:args.max_leaderheads]

    candidates = []
    for g in picked:
        models = g.get("model_files", [])
        nif, kfm, pair_conf = pick_main_model(models, g.get("leader_label") or "")
        candidates.append({
            "leader_label": g.get("leader_label"),
            "source_folder": g.get("leaderhead_folder"),
            "source_tier": g.get("source_tier"),
            "era_hints": g.get("era_hints", []),
            "culture_hints": g.get("culture_hints", []),
            "nif": nif,
            "kfm": kfm,
            "model_pair_confidence": pair_conf,
            "candidate_units": g.get("candidate_units", [])[:6],
            "candidate_buildings": g.get("candidate_buildings", [])[:6],
        })

    candidates.sort(key=lambda c: (0 if c["model_pair_confidence"] == "high" else 1,
                                    c["source_tier"]))

    portraits = [{
        "leader_label": p.get("leader_label"),
        "source_folder": p.get("leaderhead_folder"),
        "source_tier": p.get("source_tier"),
    } for p in manifest.get("portrait_only_leaderhead_folders", [])[:args.max_portraits]]

    prompt_input = {
        "task": "Propose new DowagerMod leaders/civilizations that REUSE the "
                "unused leaderhead art listed below. Follow the 1:1 pattern: one "
                "NEW leader gets exactly ONE bespoke custom trait and is paired "
                "with exactly ONE civilization.",
        "output_schema": "tools/leader_suggest/suggestion_spec.schema.json",
        "rules": [
            "Each proposal: exactly one NEW custom_trait (TRAIT_* that does NOT "
            "already exist) unique to that leader.",
            "leader_type and (if new_civilization) civilization_type must not "
            "collide with any existing id below.",
            "favorite_civic must be one of available_civics; art_style (for a "
            "new civ) must be one of available_art_styles.",
            "leaderhead.nif and leaderhead.kfm MUST be copied verbatim from a "
            "candidate below (they are verified-unused, on-disk art).",
            "Only add a unique_unit / unique_building if you can point it at an "
            "unused art path from candidate_units / candidate_buildings.",
            "Prefer historically coherent leader+civ+trait triples that fit the "
            "mod's era/dynasty-specific civ style.",
        ],
        "existing_leaders": ctx["existing_leaders"],
        "existing_civilizations": ctx["existing_civilizations"],
        "existing_traits": ctx["existing_traits"],
        "available_civics": ctx["existing_civics"],
        "available_art_styles": ctx["art_styles"],
        "candidate_leaderheads": candidates,
        "candidate_portraits_need_model": portraits,
        "manifest_summary": manifest.get("summary", {}),
    }

    os.makedirs(out_dir, exist_ok=True)
    pin_path = os.path.join(out_dir, "prompt_input.json")
    with open(pin_path, "w", encoding="utf-8") as fh:
        json.dump(prompt_input, fh, indent=2, ensure_ascii=False)

    prompt_md = render_prompt(prompt_input)
    prompt_path = os.path.join(out_dir, "prompt.md")
    with open(prompt_path, "w", encoding="utf-8") as fh:
        fh.write(prompt_md)

    print("[suggest] picked %d leaderhead candidates (of %d), %d portraits."
          % (len(candidates), len(groups), len(portraits)))
    print("[suggest] wrote:\n  %s\n  %s" % (pin_path, prompt_path))
    return 0


def render_prompt(pin):
    if os.path.isfile(TEMPLATE_PATH):
        with open(TEMPLATE_PATH, "r", encoding="utf-8") as fh:
            template = fh.read()
    else:
        template = "# Suggest leaders\n\n{RULES}\n\n{CANDIDATES}\n"

    rules = "\n".join("- " + r for r in pin["rules"])
    lines = []
    for c in pin["candidate_leaderheads"]:
        hints = ",".join(c["era_hints"] + c["culture_hints"]) or "-"
        lines.append("| %s | %s | %s | %s | %s | %s |" % (
            c["leader_label"], c["source_tier"], c.get("model_pair_confidence", "?"),
            hints, c["nif"] or "-", c["kfm"] or "-"))
    candidates = ("| leader_label | tier | pair | hints | nif | kfm |\n"
                  "| --- | --- | --- | --- | --- | --- |\n" + "\n".join(lines))

    ctxblock = (
        "Existing civilizations (%d), leaders (%d), traits (%d). "
        "Available civics: %s. Art styles: %s."
        % (len(pin["existing_civilizations"]), len(pin["existing_leaders"]),
           len(pin["existing_traits"]),
           ", ".join(pin["available_civics"]),
           ", ".join(pin["available_art_styles"])))

    return (template
            .replace("{RULES}", rules)
            .replace("{CANDIDATES}", candidates)
            .replace("{CONTEXT}", ctxblock))


# ---------------------------------------------------------------------------
# validate
# ---------------------------------------------------------------------------

def _require(cond, errors, msg):
    if not cond:
        errors.append(msg)


def validate_proposal(p, idx, ctx, unused_paths, by_type,
                      seen, errors, warnings):
    tag = "proposal[%d] %s" % (idx, p.get("id", "?"))

    for field in ("id", "leader_type", "leader_display_name",
                  "civilization_type", "new_civilization", "custom_trait",
                  "favorite_civic", "leaderhead", "rationale"):
        _require(field in p, errors, "%s: missing required field '%s'" % (tag, field))
    if errors and any(tag in e for e in errors[-9:]):
        # keep going, but downstream lookups guard on presence
        pass

    lt = p.get("leader_type", "")
    ct = p.get("civilization_type", "")
    _require(re.match(r"^LEADER_[A-Z0-9_]+$", lt), errors,
             "%s: leader_type '%s' malformed" % (tag, lt))
    _require(lt not in ctx["existing_leaders"], errors,
             "%s: leader_type '%s' already exists" % (tag, lt))
    _require(lt not in seen["leaders"], errors,
             "%s: leader_type '%s' duplicated in batch" % (tag, lt))
    seen["leaders"].add(lt)

    if p.get("new_civilization"):
        _require(ct not in ctx["existing_civilizations"], errors,
                 "%s: new civilization_type '%s' already exists" % (tag, ct))
        style = p.get("art_style")
        _require(style in ctx["art_styles"], errors,
                 "%s: art_style '%s' not in %s" % (tag, style, ctx["art_styles"]))
        _require(bool(p.get("civilization_display_name")), warnings,
                 "%s: new civ should set civilization_display_name" % tag)
    else:
        _require(ct in ctx["existing_civilizations"], errors,
                 "%s: civilization_type '%s' does not exist (set new_civilization?)"
                 % (tag, ct))
    seen["civs"].add(ct)

    tr = p.get("custom_trait", {}) or {}
    tt = tr.get("trait_type", "")
    _require(re.match(r"^TRAIT_[A-Z0-9_]+$", tt), errors,
             "%s: custom_trait.trait_type '%s' malformed" % (tag, tt))
    _require(tt not in ctx["existing_traits"], errors,
             "%s: custom_trait '%s' already exists (must be NEW)" % (tag, tt))
    _require(tt not in seen["traits"], errors,
             "%s: custom_trait '%s' duplicated in batch" % (tag, tt))
    _require(bool(tr.get("design")), warnings,
             "%s: custom_trait should describe its 'design'" % tag)
    seen["traits"].add(tt)

    civic = p.get("favorite_civic", "")
    _require(civic in ctx["existing_civics"], errors,
             "%s: favorite_civic '%s' not a valid civic" % (tag, civic))

    lh = p.get("leaderhead", {}) or {}
    for key in ("nif", "kfm"):
        path = lh.get(key)
        if not path:
            errors.append("%s: leaderhead.%s missing" % (tag, key))
            continue
        n = norm(path)
        _require(n in unused_paths, errors,
                 "%s: leaderhead.%s '%s' is not an unused on-disk art path"
                 % (tag, key, path))
    btn = lh.get("button")
    if btn and norm(btn) not in unused_paths:
        warnings.append("%s: leaderhead.button '%s' not in unused set "
                        "(may be a shared atlas - ok)" % (tag, btn))

    uu = p.get("unique_unit")
    if uu and uu.get("nif"):
        n = norm(uu["nif"])
        _require(n in unused_paths and by_type.get(n) in ("unit", "other"),
                 warnings,
                 "%s: unique_unit.nif '%s' not a confirmed unused unit art path"
                 % (tag, uu["nif"]))
    ub = p.get("unique_building")
    if ub and ub.get("nif"):
        n = norm(ub["nif"])
        _require(n in unused_paths and by_type.get(n) in ("building", "other"),
                 warnings,
                 "%s: unique_building.nif '%s' not a confirmed unused building art path"
                 % (tag, ub["nif"]))


def cmd_validate(args):
    assets_root = args.assets_root or find_assets_root(args.repo_root)
    manifest_dir = args.manifest_dir or default_manifest_dir(args.repo_root)

    with open(args.proposals, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    proposals = data.get("proposals", [])
    if not isinstance(proposals, list) or not proposals:
        print("ERROR: no proposals[] found in %s" % args.proposals, file=sys.stderr)
        return 2

    ctx = load_game_context(assets_root)
    _manifest, unused_paths, by_type = load_manifest(manifest_dir)

    errors, warnings = [], []
    seen = {"leaders": set(), "civs": set(), "traits": set()}
    for i, p in enumerate(proposals):
        validate_proposal(p, i, ctx, unused_paths, by_type, seen, errors, warnings)

    print("[validate] %d proposal(s): %d error(s), %d warning(s)."
          % (len(proposals), len(errors), len(warnings)))
    for w in warnings:
        print("  WARN  " + w)
    for e in errors:
        print("  ERROR " + e)
    if errors:
        print("[validate] FAILED")
        return 1
    print("[validate] OK - all proposals reference valid, unused art and unique ids.")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description="Leader/civ suggestion harness.")
    parser.add_argument("--repo-root", default=REPO_ROOT)
    parser.add_argument("--assets-root", default=None)
    parser.add_argument("--manifest-dir", default=None,
                        help="Dir with unused_art_manifest.{json,csv} (default docs/art_inventory).")
    sub = parser.add_subparsers(dest="cmd", required=True)

    bi = sub.add_parser("build-input", help="Emit prompt_input.json + prompt.md.")
    bi.add_argument("--out-dir", default=None)
    bi.add_argument("--max-leaderheads", type=int, default=40)
    bi.add_argument("--max-portraits", type=int, default=20)
    bi.set_defaults(func=cmd_build_input)

    va = sub.add_parser("validate", help="Validate a proposals JSON.")
    va.add_argument("proposals")
    va.set_defaults(func=cmd_validate)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
