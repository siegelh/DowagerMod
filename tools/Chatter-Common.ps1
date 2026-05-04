# Shared helpers for the chatter PS1 scripts. Dot-source from each.
#
# Civ4 uses Windows SHGetFolderPath(CSIDL_PERSONAL) which respects OneDrive
# Documents redirection. USERPROFILE\Documents may NOT match. We enumerate
# all plausible candidates and pick the first that exists, mirroring the
# game-side and sidecar logic in CvLeaderChatter.py and tools/chatter/config.py.

function Get-ChatterMyGamesRoot {
    $candidates = New-Object 'System.Collections.Generic.List[string]'
    $up = $env:USERPROFILE
    if ($up) {
        # OneDrive-prefixed sibling dirs of USERPROFILE
        try {
            Get-ChildItem -Path $up -Directory -ErrorAction Stop |
                Where-Object { $_.Name -ilike 'OneDrive*' } |
                ForEach-Object {
                    $candidates.Add((Join-Path $_.FullName 'Documents\My Games\Beyond the Sword'))
                    $candidates.Add((Join-Path $_.FullName 'Documents\My Games\beyond the sword'))
                }
        } catch { }
        $candidates.Add((Join-Path $up 'Documents\My Games\Beyond the Sword'))
        $candidates.Add((Join-Path $up 'Documents\My Games\beyond the sword'))
    }
    foreach ($k in @('OneDriveCommercial', 'OneDriveConsumer', 'OneDrive')) {
        $r = [Environment]::GetEnvironmentVariable($k)
        if ($r) {
            $candidates.Add((Join-Path $r 'Documents\My Games\Beyond the Sword'))
            $candidates.Add((Join-Path $r 'Documents\My Games\beyond the sword'))
        }
    }
    foreach ($c in $candidates) {
        if ($c -and (Test-Path $c -PathType Container)) {
            return $c
        }
    }
    # Fall back: first candidate (not yet existing — we may create dirs later)
    if ($candidates.Count -gt 0) { return $candidates[0] }
    return (Join-Path $up 'Documents\My Games\Beyond the Sword')
}

function Get-ChatterSpoolDir {
    $root = Get-ChatterMyGamesRoot
    return (Join-Path $root 'Logs\DowagerMod\chatter')
}

function Get-ChatterPidFile {
    return (Join-Path (Get-ChatterSpoolDir) 'daemon.pid')
}

function Get-ChatterDaemonLog {
    return (Join-Path (Get-ChatterSpoolDir) 'daemon.log')
}

function Get-ChatterGameLog {
    return (Join-Path (Get-ChatterSpoolDir) 'chatter.log')
}
