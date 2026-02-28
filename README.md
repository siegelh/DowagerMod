# DowagerMod

## Install

1. Build or obtain the installer executable from `dist`.
2. Run `install.exe`.
3. The installer copies files from:
   - `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/`
   into the live game install.

## Build DLL (CvGameCoreDLL)

Use the canonical build script from repo root:

```powershell
.\tools\build_civ4_dll.ps1
```

Compile-only (no asset replacement):

```powershell
.\tools\build_civ4_dll.ps1 -NoDeploy
```

What it does:

1. Builds `CvGameCoreDLL.dll` from:
   - `third_party/beyond-the-sword-sdk/CvGameCoreDLL`
2. Copies a timestamped DLL to:
   - `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets`
3. Output name format:
   - `CvGameCoreDLL_YYYYMMDD_HHMMSS.dll`

Notes:

- This timestamped DLL is ignored by git via `.gitignore`.
- Rename/copy it to `CvGameCoreDLL.dll` when you want it to be the active shipped DLL.

## Automated Test Gates

Run these from repo root:

1. Smart changed-file gate:

```powershell
.\tools\test_gate.ps1
```

`test_gate.ps1` is XML-focused by default. Add `-CheckDll` to also compile DLL when DLL source changes:

```powershell
.\tools\test_gate.ps1 -CheckDll
```

`-CheckDll` uses compile-only mode (`-NoDeploy`) so the gate does not replace files in `CoreFiles`.

2. XML-only full sweep:

```powershell
.\tools\test_xml.ps1 -All
```

3. Full gate (all XML + DLL build):

```powershell
.\tools\test_full.ps1
```

Details:

- `docs/TESTING_WORKFLOW.md`

## XML Targeting (Important)

When modding and testing **Beyond the Sword**, treat BTS XML files as authoritative.

Primary trait file:

- `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Civilizations/CIV4TraitInfos.xml`

Compatibility/legacy copies may exist under:

- `.../Warlords/Assets/...`
- `.../Assets/...` (base Civ4)

but BTS gameplay should read the BTS path above. New trait behavior and trait data changes should be made there first.

## XML Schema Validation Lessons

When adding new XML tags, update schema and data together.

What broke in this incident:

- `CIV4TraitInfos.xml` failed to load after adding:
  - `ImprovementTerrainYieldChanges`
  - `ImprovementFeatureYieldChanges`
- The schema referenced `TerrainType` and `FeatureType` in those blocks, but those element types were not declared in `CIV4CivilizationsSchema.xml`.
- Once trait loading failed, follow-on XML loads produced misleading secondary errors (for example memory errors while loading `CIV4CivicOptionInfos.xml`).

Required checklist for new XML capability work:

1. Add new tags to the correct schema sequence (`TraitInfo`, `CivicInfo`, etc.) in all relevant copies:
   - `.../Beyond the Sword/Assets/...`
   - `.../Assets/...`
   - `.../Warlords/Assets/...` when shared schemas are used
2. Add any new referenced element types (`<ElementType name=\"...\"/>`) in schema files.
3. Keep element order in data XML consistent with schema order.
4. Validate XML with schema before launch (MSXML 3.0 style validation is closest to Civ4 runtime behavior).
5. If the game shows:
   - `Failed Loading XML file .../CIV4TraitInfos.xml`
   treat that as the primary error and fix it first before investigating later popups.

## Tooltip Text Formatting Lessons

When adding or editing text keys used by DLL help-formatting (`gDLL->getText(...)`), treat format specifiers as runtime-sensitive.

Known pitfall:
- `%+d` can leak into UI in some help paths (for example civic tooltips), showing raw tokens like `%+d%c`.

Safe guideline:
1. Prefer `%d` over `%+d` in XML text keys unless a specific call site has been validated.
2. After text changes, verify in-game tooltips for unresolved `%` tokens.

## Rebuild Installer

From repo root:

```powershell
python -m PyInstaller --onefile install.py
```

## More DLL Build Details

See:

- `third_party/beyond-the-sword-sdk/BUILDING_CVGAMECOREDLL.md`

## Leader Overhaul Rules

Plan-of-record document:

- `docs/LEADER_OVERHAUL_PLAN_OF_RECORD.md`

This includes required standards for:

- mixing legacy and new trait mechanisms
- sparse use of trait-level `BuildingYieldChanges`/`BuildingCommerceChanges` in favor of UB/UU/Palace-driven identity
- art sourcing workflow (including external art import rules)
- civilization-specific unique tile improvements (for example, Sphinx-style desert improvements with optional city-range bonuses)
- explicit UU/UB fit review (`KEEP`/`MODIFY`/`REPLACE`) before any unique replacement
- explicit power-budget choice per overhaul (`Leader Heavy`, `Civ Heavy`, `Hybrid`) to preserve asymmetry
- rarity and gating standards for civilization-specific tile improvements
- living tracker for which leaders/civilizations are already overhauled
- creativity/naming/UI clarity guardrails to keep overhauls distinct and readable
- mandatory proposal gate: UU/UB fit verdicts, rare-improvement justification, art feasibility pass, and UI exposure plan

## Overhaul Request Template

For consistent execution, start overhaul requests with:

`Follow docs/LEADER_OVERHAUL_PLAN_OF_RECORD.md and README.md strictly before proposing or implementing.`

Then require:
1. checklist echo before changes
2. docs-compliance summary after changes
