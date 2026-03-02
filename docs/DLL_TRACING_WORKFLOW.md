# DLL Tracing Workflow

## Purpose

This documents the lightweight logging infrastructure kept in the BtS DLL so future debugging does not have to start from scratch.

The current design goal is:

- tracing infrastructure remains available
- tracing is off by default for normal play
- heavy city/luxury tracing is opt-in

## Log File Location

The DLL writes the trace beside the loaded DLL as:

- `CvGameCoreDLL_trace.log`

Typical live path:

- [CvGameCoreDLL_trace.log](/C:/Program%20Files%20(x86)/Steam/steamapps/common/Sid%20Meier%27s%20Civilization%20IV%20Beyond%20the%20Sword/Beyond%20the%20Sword/Assets/CvGameCoreDLL_trace.log)

## Runtime Toggles

Tracing is controlled at DLL process attach, so restart the game after changing these.

### Generic DLL trace

Enable generic tracing by either:

- creating an empty file beside the loaded DLL named `CvGameCoreDLL_trace.on`
- or setting environment variable `CIV4_DLL_TRACE=1`

This enables normal `dllTrace(...)` output such as:

- save/load tracing
- explicit debug lines left in code
- DLL attach/detach trace lines

### Heavy city / luxury trace

Enable the expensive city-industry tracing by either:

- creating an empty file beside the loaded DLL named `CvGameCoreDLL_city_trace.on`
- or setting environment variable `CIV4_DLL_CITY_TRACE=1`

This controls the very verbose logs in [CvCity.cpp](/c:/DowagerMod/third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvCity.cpp), including:

- luxury activation lines
- luxury free-bonus delta lines
- city radius audits
- per-plot spice audits

## Crash Logging

Crash logging is still allowed even when generic tracing is disabled.

That means `CRASH` category lines can still be emitted by the unhandled exception filter in:

- [CvGameCoreDLL.cpp](/c:/DowagerMod/third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvGameCoreDLL.cpp)

## How To Add Logging

### Basic logging

Use:

```cpp
dllTrace("SAVE", "BEGIN CvPlayer::read id=%d", (int)m_eID);
```

Current common categories:

- `SAVE`
- `CITY`
- `DLL`
- `CRASH`

### For hot paths

Do not build expensive strings unconditionally in tight loops.

Guard them like this:

```cpp
if (isCityTraceEnabled())
{
    dllTrace("CITY", "Luxury activation city=%d building=%s", getID(), kBuilding.getType());
}
```

or:

```cpp
if (isDllTraceEnabled())
{
    dllTrace("SAVE", "END CvPlot::read x=%d y=%d", m_iX, m_iY);
}
```

This matters because otherwise the string formatting and helper calls still run even when tracing is disabled.

### For structured one-off investigations

If a bug is in a hot system such as city bonus updates:

1. add narrow helper functions in the target file
2. gate them behind `isCityTraceEnabled()` or `isDllTraceEnabled()`
3. keep the logs scoped to:
   - one bonus
   - one building
   - one civ
   - one city pair

That keeps the trace readable and avoids slowing the whole game unnecessarily.

## Current Trace-Related Code

Core infrastructure:

- [CvGameCoreDLL.h](/c:/DowagerMod/third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvGameCoreDLL.h)
- [CvGameCoreDLL.cpp](/c:/DowagerMod/third_party/beyond-the-sword-sdk/CvGameCoreDLL/CvGameCoreDLL.cpp)

Important exported helpers:

- `dllTrace(...)`
- `isDllTraceEnabled()`
- `isCityTraceEnabled()`

## Build / Deploy Workflow

After editing DLL code under:

- [CvGameCoreDLL](/c:/DowagerMod/third_party/beyond-the-sword-sdk/CvGameCoreDLL)

run:

```powershell
.\tools\test_gate.ps1
```

Then copy the rebuilt DLL into:

- [CvGameCoreDLL.dll](/c:/DowagerMod/CoreFiles/Sid%20Meier%27s%20Civilization%20IV%20Beyond%20the%20Sword/Beyond%20the%20Sword/Assets/CvGameCoreDLL.dll)

Then deploy to the live install using:

- [install.py](/c:/DowagerMod/CoreFiles/install.py)

## Recommended Future Workflow

When chasing a new DLL bug:

1. turn on generic trace first
2. reproduce once
3. if that is not enough, turn on city trace second
4. narrow the logging to the smallest useful scope
5. remove or gate the heavy logs again once the bug is understood

## Current Status

As of 2026-03-02:

- generic DLL tracing is available but off by default
- heavy luxury/city tracing is available but off by default
- this keeps the debug tooling available without leaving the game in a permanently slow trace-heavy state
