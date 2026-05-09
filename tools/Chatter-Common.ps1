# Shared helpers for the chatter PS1 scripts. Dot-source from each.
#
# Spool lives under %LOCALAPPDATA% (not OneDrive-synced, not touched by the
# installer). See CvLeaderChatter.py:_spool_dir for relocation history.

function Get-ChatterSpoolDir {
    $local = $env:LOCALAPPDATA
    if (-not $local) {
        $local = Join-Path $env:USERPROFILE 'AppData\Local'
    }
    return (Join-Path $local 'DowagerMod\chatter\spool')
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
