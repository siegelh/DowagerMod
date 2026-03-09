# Brennus / Gaul Overhaul Draft

## Status
Saved for later implementation. No XML, DLL, art, or text assets have been changed for this design yet.

## Target
- `LEADER_BRENNUS`
- `CIVILIZATION_GAULIC_CONFEDERATION`

## Historical Thesis
Brennus should play as a charismatic confederation war-leader, not a stable palace-state ruler. The center of gravity is rapid coalition warfare, sacred arbitration, and selective hilltop consolidation through oppida.

## Gameplay Thesis
The design should peak in the Classical era through raiding, hill warfare, and fast promotion tempo, then stabilize conquest through a sacred court and per-city oppida instead of broad bureaucratic scaling.

## Power Budget
`Hybrid`, leaning slightly toward civ-specific uniques.

## Trait Channels Selected
- Scalar:
  - `iMaxAnarchy = -1`
  - `iLevelExperienceModifier = -25`
- Free promotions:
  - free `PROMOTION_PILLAGE1` for `UNITCOMBAT_MELEE`
  - free `PROMOTION_PILLAGE1` for `UNITCOMBAT_MOUNTED`
- Mapped channels:
  - `SpecialistCommerceChanges`: `SPECIALIST_PRIEST` gets `+1 Culture`
  - `ImprovementCityCommerceChangesWorked`: worked `IMPROVEMENT_OPPIDUM` gives city `+1 Gold, +1 Culture`

## Trait Identity
- Trait display name: `War-League`
- Intent:
  - fast regrouping after civic/religious shifts
  - quicker veteran snowball
  - raid economy through pillage pressure
  - druidic legitimacy through priest culture
  - oppida as worked tile anchors rather than passive empire-wide auras

## UU / UB Fit Verdict
- UU: `REPLACE`
  - Replace the shared `UNIT_CELTIC_GALLIC_WARRIOR`. The concept is too pan-Celtic and not specific enough for Brennus' Gaulic confederation.
- UB: `REPLACE`
  - Replace the shared `BUILDING_CELTIC_DUN`. The hillfort concept fits better as a map object than as Brennus' core institutional building.

## Settled Unique Package
### UU: `UNIT_GAESATAE`
- Replaces: `UNITCLASS_SWORDSMAN`
- Stats:
  - `Strength 6`
  - `Cost 45`
  - `TECH_IRON_WORKING`
  - strategic resource access from `Copper or Iron`
  - free `PROMOTION_GUERRILLA1`
  - `iCityAttack = 20`
  - `iWithdrawalProb = 15`
- Role:
  - aggressive hill raider that converts Brennus' faster promotions into early tempo

### UB: `BUILDING_NEMETON`
- Replaces: `BUILDINGCLASS_COURTHOUSE`
- Stats:
  - `Cost 110`
  - `TECH_CODE_OF_LAWS`
  - `iMaintenanceModifier = -50`
  - `iHappiness = 1`
  - `+2 Culture`
  - `1 Priest` specialist slot
- Role:
  - sacred-legal center that makes conquest governable without pretending Gaul had Roman administration

### Unique Improvement: `IMPROVEMENT_OPPIDUM` via `BUILD_OPPIDUM`
- Why this civ gets one:
  - oppida are the clearest map-level institution of later Iron Age Gaul and express concentration, fortification, and exchange better on the map than through a generic building bonus
- Base effects:
  - `TECH_IRON_WORKING`
  - hills only
  - `+2 Production`
  - `+1 Commerce`
  - `+25% Defense`
- Trait synergy:
  - with `War-League`, a worked Oppidum gives the city `+1 Gold, +1 Culture`

## Settled Oppidum Rule
This is the version to implement later:
- Gaulic Confederation only
- must be built on hills
- must be inside one of your cities' workable radius
- must be in that city's inner ring only
- each city may have at most `1` Oppidum
- no global per-player cap
- adjacency between different cities' Oppida is allowed

Implementation note:
- this is a DLL placement rule, not an XML-only rule
- intended hook point: `CvUnit::canBuild` in `third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvUnit.cpp`
- clean expression: target city satisfies `stepDistance(cityX, cityY, plotX, plotY) == 1`, and that city's plots are scanned for an existing `IMPROVEMENT_OPPIDUM`

## Expression Priority Verdict
Identity should be expressed first through:
- `UNIT_GAESATAE`
- `BUILDING_NEMETON`
- `IMPROVEMENT_OPPIDUM`

Avoid broad generic `BuildingCommerceChanges` on common building classes. Brennus already has enough identity through the civ package and the narrow trait hooks above.

## AI Personality Notes
- `FavoriteCivic -> CIVIC_VASSALAGE`
- `iBuildUnitProb 30 -> 38`
- `iDogpileWarRand 25 -> 35`
- `iMakePeaceRand 80 -> 65`
- `iRazeCityProb 50 -> 60`
- keep `FavoriteReligion = NONE`

## Art Feasibility Notes
Candidate workspace sources identified during planning:
- Unit:
  - `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/Art/Caveman2Cosmos/art/units/celtic_sparth/swordsman/celtichvyfootman.nif`
- Building:
  - `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/Art/Caveman2Cosmos/art/structures/buildings/rodnovery_cathedral/celtic_temple.nif`
- Improvement:
  - `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/Art/Caveman2Cosmos/art/structures/buildings/celtic_dun/celtic_dun_post.nif`
- External button fallback:
  - `C:\Users\Harrison\Downloads\civ4mods-code\realism\bts\trunk\mod\Assets\Art\Interface\Buttons\units\NU_celt_gallic_warrior.dds`

If implemented later, copy any external asset into workspace before updating XML references.

## UI Exposure Plan
- Trait text must explicitly surface:
  - pillage promotion coverage
  - priest culture
  - worked Oppidum city bonus
- `BUILD_OPPIDUM` help text must explicitly state:
  - hills only
  - within city radius
  - inner ring only
  - one Oppidum per city
- Civilopedia entries for `Gaesatae`, `Nemeton`, and `Oppidum` should state exact numeric effects

## Expected Implementation Touchpoints Later
- `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Civilizations/CIV4TraitInfos.xml`
- `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Civilizations/CIV4LeaderHeadInfos.xml`
- `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Civilizations/CIV4CivilizationInfos.xml`
- `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Units/CIV4UnitInfos.xml`
- `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Buildings/CIV4BuildingInfos.xml`
- `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Units/CIV4BuildInfos.xml`
- `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Terrain/CIV4ImprovementInfos.xml`
- `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Art/CIV4ArtDefines_Unit.xml`
- `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Art/CIV4ArtDefines_Building.xml`
- `CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML/Art/CIV4ArtDefines_Improvement.xml`
- new Brennus text XML under `Assets/XML/Text`
- `third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvUnit.cpp`

## Deferred Test Gate
When implementation starts later:
- run `.\tools\test_gate.ps1 -CheckDll` after XML and DLL edits

