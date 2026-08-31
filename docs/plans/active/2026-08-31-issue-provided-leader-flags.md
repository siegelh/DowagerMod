# Issue-Provided Leader Flag Adoption

- Status: `complete`
- Owner / agent: GitHub Copilot CLI
- Last updated: `2026-08-31`

## Problem Statement

- Task: apply the flag designs attached to GitHub issues #87 through #142 so
  they can be reviewed in game.
- Current observed behavior: all 56 issues contain one accessible image, but
  production still uses the prior historical-v1 designs.
- Why this is a real repo/code problem: the issue artwork must be versioned,
  normalized to Civ4's square texture input, encoded with the fixed-color
  zero-alpha convention, and connected to exact civilization mappings.

## Scope

- Adopt all 56 issue-provided designs.
- Keep the current historical-v1 designs for Genghis Khan, Gilgamesh, and
  Huayna Capac because no corresponding issue images exist.
- Preserve historical-v1 sources and create a new versioned source generation.
- Update production DDS files, manifest metadata, tests, and flag docs.
- Create one local commit without pushing.

## Non-Goals

- No redesign beyond technical square-texture normalization.
- No changes to player/border colors.
- No changes to Barbarian, Minor Civilization, or unused art definitions.
- No new design research for the three leaders without issue images.

## Trusted Sources Of Truth

- GitHub issues #87-#142 and their user-attachment URLs.
- `tools/flags/manifest.json` and live civilization/art XML.
- `tools/flags/build_flags.py` and the exact production contracts.

## Assumptions Confirmed By Human

- The issue-image source licensing is acceptable for repository use.
- Genghis Khan, Gilgamesh, and Huayna Capac retain historical-v1.
- The result should be committed for installed-game review.

## Proposed Implementation Steps

1. Map each issue title to exactly one playable civilization.
2. Download the 56 original attachments into
   `tools/flags/designs/issue-flags-v2/masters/`.
3. Extend source rasterization to accept the attachment's native dimensions
   and normalize it deterministically to the 1024x1024 working square.
4. Update manifest version/source/issue metadata and master hashes.
5. Calculate new production digests and transactionally regenerate runtime
   DDS files.
6. Update exact tests and documentation.
7. Generate the temporary review gallery and run all flag/repository gates.
8. Commit the complete change without pushing.

## Validation Plan

- Exactly 56 issue-v2 records and three historical-v1 records.
- Every issue from #87 through #142 maps once; every attachment is accessible.
- All 59 deterministic DDS outputs match the manifest and live files.
- All DDS files remain 128x128 DXT3, eight mips, 22,000 bytes, and zero alpha.
- Focused flag tests, `tools/test_gate.ps1`, and `git diff --check`.
- User performs the installed visual smoke test after the commit.

## Risks / Rollback

- Rectangular issue artwork must be resampled into Civ4's square UV texture;
  the installed renderer may expose composition problems requiring feedback.
- Several issue images are heraldic devices, photographs, or seals rather than
  finished square flags; this pass intentionally preserves their supplied
  composition rather than redesigning them.
- Revert the final commit to restore historical-v1 production and metadata.

## Completion Checklist

- [x] 56 issue attachments versioned and mapped.
- [x] Manifest and deterministic production files updated.
- [x] Review output and automated validation pass.
- [x] One local commit created without pushing.

## Final Outcome Summary

- Added the exact 56 issue attachments as the `issue-flags-v2` source
  generation and retained historical-v1 for Inca, Mongol Empire, and Sumeria.
- Published exactly 56 changed production DDS files without changing
  civilization art XML or the three retained DDS files.
- Raster attachments are stretched to the square working texture. Issue-v2
  SVGs are first rendered at their native canvas and then stretched, preventing
  transparent SVG letterboxing from becoming black bands in Civ4's RGB-only
  fixed-color path.
- Focused validation passed with 139 tests.
- The read-only deterministic builder reproduced all 59 production files
  byte-for-byte with zero errors and no XML changes.
- The repository changed-file gate and `git diff --check` passed.
- Automated validation is complete. Installed visual smoke testing remains a
  user action after the local commit is installed.
