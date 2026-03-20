#!/usr/bin/env python3
"""
Scaffold directories, docs, and manifests for a new Civ4 BTS leaderhead.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
import re
import sys
from textwrap import dedent


REPO_ROOT = Path(__file__).resolve().parents[2]
ASSETS_ROOT = (
    REPO_ROOT
    / "CoreFiles"
    / "Sid Meier's Civilization IV Beyond the Sword"
    / "Beyond the Sword"
    / "Assets"
)
LEADERHEAD_ART_ROOT = ASSETS_ROOT / "Art" / "Leaderheads"
DOCS_PROTO_ROOT = REPO_ROOT / "docs" / "leaderhead_pipeline" / "prototypes"
CONFIG_ROOT = Path(__file__).resolve().parent / "configs"


def slugify(name: str) -> str:
    slug = re.sub(r"[^0-9a-zA-Z]+", "_", name.strip()).strip("_").lower()
    return slug or "leaderhead"


def derive_art_def(slug: str) -> str:
    return f"ART_DEF_LEADER_{slug.upper()}"


def derive_leader_type(slug: str) -> str:
    return f"LEADER_{slug.upper()}"


def write_text(path: Path, content: str, force: bool) -> bool:
    if path.exists() and not force:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def build_manifest(
    name: str,
    slug: str,
    art_def: str,
    leader_type: str,
    base_art_def: str,
) -> dict:
    art_rel = f"art/LeaderHeads/{slug}"
    button_rel = f"art/LeaderHeads/{slug}_button.dds"
    manifest = {
        "name": name,
        "slug": slug,
        "art_def": art_def,
        "leader_type": leader_type,
        "base_art_def": base_art_def,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "paths": {
            "nif": f"{art_rel}/{slug}.nif",
            "nif_noshader": f"{art_rel}/{slug}_noshader.nif",
            "kfm": f"{art_rel}/{slug}.kfm",
            "background_nif": f"{art_rel}/{slug}_bg.nif",
            "background_kfm": f"{art_rel}/{slug}_bg.kfm",
            "button": button_rel,
            "textures": {
                "diffuse": f"{art_rel}/{slug}_diff.dds",
                "normal": f"{art_rel}/{slug}_nrml.dds",
                "specular": f"{art_rel}/{slug}_spec.dds",
                "env": f"{art_rel}/{slug}_env.dds",
                "env_mask": f"{art_rel}/{slug}_env_mask.dds",
            },
        },
    }
    return manifest


def art_readme_content(name: str, slug: str) -> str:
    return dedent(
        f"""\
        # {name} Leaderhead Drop Folder

        Place exported assets here once Blender/PyNifly export completes.

        Required files:
        - {{slug}}.nif / {{slug}}_noshader.nif (shader + fallback)
        - {{slug}}.kfm (animation controller)
        - Animation clips (KF) referenced by the KFM
        - Background: {{slug}}_bg.nif / {{slug}}_bg.kfm / {{slug}}_bg_background.kf
        - Textures: {{slug}}_diff.dds, {{slug}}_nrml.dds, {{slug}}_spec.dds, {{slug}}_env.dds, {{slug}}_env_mask.dds
        - Button art: ../Interface/LeaderHeads/{{slug}}_button.dds

        Run `python tools/leaderhead_pipeline/scaffold_leaderhead.py --help` for details.
        """
    ).replace("{slug}", slug)


def prototype_doc_template(name: str, slug: str, art_def: str, base_art_def: str) -> str:
    return dedent(
        f"""\
        # {name} Leaderhead Prototype (WIP)

        - **Slug:** `{slug}`
        - **ArtDefine:** `{art_def}`
        - **Base rig / animation set:** `{base_art_def}`
        - **Last scaffolded:** {datetime.now(timezone.utc).date().isoformat()}

        ## TODO

        - [ ] Collect/record photo references + licensing
        - [ ] Face reconstruction & sculpt
        - [ ] Retopology + UVs
        - [ ] Texture bake + DDS export
        - [ ] Rig transfer + animation binding
        - [ ] Background + button art
        - [ ] XML snippets inserted
        - [ ] `tools/test_gate.ps1`
        - [ ] In-game diplomacy smoke test

        Update this doc as you make progress (see `docs/leaderhead_pipeline.md` for the expected content).
        """
    )


def xml_snippets(name: str, slug: str, art_def: str, leader_type: str) -> tuple[str, str]:
    art = dedent(
        f"""\
        <!-- {name} -->
        <LeaderheadArtInfo>
            <Type>{art_def}</Type>
            <Button>art/LeaderHeads/{slug}_button.dds</Button>
            <NIF>art/LeaderHeads/{slug}/{slug}.nif</NIF>
            <KFM>art/LeaderHeads/{slug}/{slug}.kfm</KFM>
            <NoShaderNIF>art/LeaderHeads/{slug}/{slug}_noshader.nif</NoShaderNIF>
            <BackgroundKFM>art/LeaderHeads/{slug}/{slug}_bg.kfm</BackgroundKFM>
        </LeaderheadArtInfo>"""
    )
    info = dedent(
        f"""\
        <!-- {name} -->
        <LeaderHeadInfo>
            <Type>{leader_type}</Type>
            <Description>{name}</Description>
            <Civilopedia>{name}</Civilopedia>
            <ArtDefineTag>{art_def}</ArtDefineTag>
            <!-- TODO: fill in personality stats before committing -->
        </LeaderHeadInfo>"""
    )
    return art, info


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", required=True, help="Display name for the leader.")
    parser.add_argument("--slug", help="Filesystem/name slug (snake_case).")
    parser.add_argument("--art-def", help="Art define tag (ART_DEF_LEADER_*).")
    parser.add_argument(
        "--base-art-def",
        default="ART_DEF_LEADER_VICTORIA",
        help="Existing art define whose rig/animations you plan to reuse.",
    )
    parser.add_argument("--force", action="store_true", help="Overwrite existing files.")
    args = parser.parse_args(argv)

    slug = args.slug or slugify(args.name)
    art_def = args.art_def or derive_art_def(slug)
    leader_type = derive_leader_type(slug)

    # 1. Art directory + README
    art_dir = LEADERHEAD_ART_ROOT / slug
    art_dir.mkdir(parents=True, exist_ok=True)
    art_readme_path = art_dir / "README.txt"
    art_readme_written = write_text(
        art_readme_path, art_readme_content(args.name, slug), args.force
    )

    # 2. Prototype doc template
    DOCS_PROTO_ROOT.mkdir(parents=True, exist_ok=True)
    proto_doc_path = DOCS_PROTO_ROOT / f"{slug}.md"
    prototype_written = write_text(
        proto_doc_path,
        prototype_doc_template(args.name, slug, art_def, args.base_art_def),
        args.force,
    )

    # 3. Manifest JSON
    CONFIG_ROOT.mkdir(parents=True, exist_ok=True)
    manifest_path = CONFIG_ROOT / f"{slug}.json"
    manifest = build_manifest(args.name, slug, art_def, leader_type, args.base_art_def)
    manifest_written = write_text(
        manifest_path, json.dumps(manifest, indent=2) + "\n", args.force
    )

    art_xml, info_xml = xml_snippets(args.name, slug, art_def, leader_type)

    print(f"[+] Art directory: {art_dir}")
    if art_readme_written:
        print(f"    • Wrote {art_readme_path.name}")
    else:
        print(f"    • Kept existing {art_readme_path.name}")

    print(f"[+] Prototype doc: {proto_doc_path}")
    print(
        "    • "
        + (
            "Created template"
            if prototype_written
            else "Already existed (not overwritten)"
        )
    )

    print(f"[+] Manifest: {manifest_path}")
    print(
        "    • "
        + ("Wrote manifest" if manifest_written else "Already existed (not overwritten)")
    )

    print("\n=== CIV4ArtDefines_Leaderhead snippet ===")
    print(art_xml)
    print("\n=== CIV4LeaderHeadInfos snippet ===")
    print(info_xml)

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
