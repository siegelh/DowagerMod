# Crash Reporting

## Immediate workflow

Continue launching and playing Civilization IV: Beyond the Sword normally
through Steam. No diagnostic game launcher is required.

After a crash:

1. Do **not** relaunch Civ4 first. A new launch resets
   `CvGameCoreDLL_trace.log`.
2. Double-click:

   ```text
   Report DowagerMod Crash.bat
   ```

3. Confirm the suggested save and answer the short incident questions.
4. The reporter creates the GitHub issue when authenticated GitHub CLI is
   available.
5. The reporter opens the issue and selects the ZIP in Explorer.
6. Drag the selected ZIP onto the open issue, wait for GitHub to finish the
   upload, then click **Comment**.

The save and ZIP are never uploaded automatically.

## Save discovery

The canonical multiplayer autosave directory is:

```text
<Documents>\My Games\Beyond the Sword\Saves\multi\auto
```

Typical path without Documents redirection:

```text
C:\Users\<user>\Documents\My Games\Beyond the Sword\Saves\multi\auto
```

Windows may redirect Documents to OneDrive, for example:

```text
C:\Users\<user>\OneDrive - Organization\Documents\My Games\Beyond the Sword\Saves\multi\auto
```

The reporter asks Windows for the real Documents known folder first. It then
checks normal Documents and OneDrive fallback locations. Save candidates are
ranked in this order:

1. `Saves\multi\auto`
2. other files below `Saves\multi`
3. other `auto` directories
4. single-player saves
5. other Civ4 saves

Within each category, the newest file is preferred. The suggested filename,
category, modification time, age, and size are displayed before selection.
The user can accept it, enter another path, or omit the save.

## Output location and retention

Generated incident data is outside the repository:

```text
%LOCALAPPDATA%\DowagerMod\CrashReports
```

Typical ZIP:

```text
C:\Users\<user>\AppData\Local\DowagerMod\CrashReports\DowagerMod-Crash-YYYYMMDD-HHMMSS.zip
```

Crash-only minidumps are initially written under:

```text
%LOCALAPPDATA%\DowagerMod\CrashReports\Pending
```

The collector and DLL retain at most the newest three relevant artifacts and
at most 250 MB per artifact category. Generated reports do not enter a Git
worktree and need no `.gitignore` rule.

## Evidence collected

The report attempts to collect:

- selected save/autosave;
- newest crash-only minidump;
- DLL trace and relevant Civ4 Python/XML/init/network/synchronization logs;
- recent glyph diagnostics;
- recent Windows Application Error and Windows Error Reporting records;
- repository branch, commit, dirty state, and remote;
- repository and installed DLL hashes;
- repository/installed XML, Python, and DLL multiplayer manifests;
- `GameFont.tga` and `GameFont_75.tga` hashes;
- sanitized Windows, RAM, GPU, disk, and Civ4 configuration facts.

Missing evidence is explicitly listed. The ZIP includes:

- `report.md`
- `manifest.json`
- `issue-body.md`
- collected evidence files

Console progress lines report each collection step, input/output byte counts,
duration, status, and a final expected/processed/persisted/skipped/error
reconciliation.

## Privacy boundary

Text evidence is sanitized before packaging. The reporter redacts:

- user profile paths and username;
- email addresses and IPv4 addresses;
- credential-bearing URLs;
- common GitHub/token/password/secret patterns.

It does not collect environment-variable values, GitHub tokens, browser data,
or unrelated files.

Save files can contain game and player names. Minidumps contain thread and
module state and may contain small portions of process memory. These binary
files cannot be meaningfully text-redacted, which is why the reporter requires
visible manual drag-and-drop before GitHub receives the ZIP.

## GitHub behavior

When `gh` is installed and authenticated, the reporter runs the equivalent of:

```powershell
gh issue create `
  --repo siegelh/DowagerMod `
  --title "[Crash] <last action>" `
  --label bug `
  --body-file <generated issue body>
```

GitHub CLI does not provide a supported issue-attachment argument. The issue is
therefore created automatically, while the ZIP attachment remains one explicit
manual step.

If `gh` is unavailable or unauthenticated, the reporter still creates the ZIP,
copies the issue body to the clipboard when possible, opens a prefilled browser
issue, and prints exact paste/submit/attach instructions.

## Runtime cost

Normal gameplay does not enable generic or city tracing. The DLL performs no
new per-turn file logging for this workflow.

The minidump path runs only after an unhandled exception. Normal startup only
checks the small pending-dump directory to enforce retention. Existing trace
toggles remain opt-in:

```text
CvGameCoreDLL_trace.on
CvGameCoreDLL_city_trace.on
```

See [DLL_TRACING_WORKFLOW.md](DLL_TRACING_WORKFLOW.md) before enabling them.
Heavy city tracing should be used only for a narrowed, reproducible incident.

## Diagnostic limits

A save, matching build fingerprint, minidump, exception record, and logs will
usually identify the failing stack and subsystem. They cannot guarantee the
semantic root cause of every crash. For example, the faulting instruction may
be downstream of earlier invalid state.

If the first issue does not establish causation:

1. reproduce from the attached save;
2. identify the smallest failing action and first bad commit;
3. enable only the relevant opt-in trace;
4. reproduce once;
5. compare the trace and dump before attempting a fix.

Late-game 32-bit address-space pressure remains a first-class possibility.
Post-crash system information cannot reconstruct the process's exact peak
memory after it exits.

## Developer validation

Run the synthetic workflow without creating an issue:

```powershell
.\tools\test_crash_reporter.ps1
```

Validate DLL changes with:

```powershell
.\tools\test_gate.ps1 -CheckDll
```
