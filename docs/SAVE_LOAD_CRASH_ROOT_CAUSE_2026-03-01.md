# Save Load Crash Root Cause

Date: March 1, 2026

## Symptom

The game could start normally, but loading a save could crash to desktop with no useful in-game error. The failure reproduced even when the save had been created moments earlier from the same build.

## What We Logged

A native DLL trace was added and written to `CvGameCoreDLL_trace.log` next to the loaded DLL. The trace showed:

- map, team, and early player deserialization completed normally
- the crash consistently occurred during `CvPlayer::read()` for player slot `10`
- player `10` finished all major stream reads before the access violation
- the last successful step was the `setNetID(...)` block

That narrowed the fault to the tail of `CvPlayer::read()`.

## Root Cause

The crash was in `CvPlayer::rebuildTraitGoldenAgeYieldChangeCache()` in:

- `third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvPlayer.cpp`

During save load, that function was being called for a player slot with no valid leader definition. It used `hasTrait()`, which in turn dereferenced `GC.getLeaderHeadInfo(getLeaderType())` without a safe runtime guard for invalid leader values in release builds.

For an unused or invalid slot, that produced an access violation during load.

## Fix

`rebuildTraitGoldenAgeYieldChangeCache()` now:

- zeroes the cache as before
- checks whether `getLeaderType()` is within the valid leader-info range
- returns early if the slot has no valid leader
- uses the validated leader info directly when rebuilding the cache

## Gameplay Impact

For normal civilizations with valid leaders, nothing changes.

The only behavior change is for invalid or unused player slots:

- before: possible crash during save load
- now: the trait golden-age yield cache is skipped and remains zero for that invalid slot

This does not change save format, industry mechanics, or normal player balance.

## Operational Note

The live game was loading the DLL from the Steam install directory, not just the repo copy. When testing future DLL fixes, confirm the active runtime DLL matches the rebuilt output:

- `C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Assets\CvGameCoreDLL.dll`
