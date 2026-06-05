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

function Get-ChatterRepoRoot {
    # tools\Chatter-Common.ps1 -> tools -> repo root
    return (Split-Path -Parent $PSScriptRoot)
}

function Get-ChatterEnvPath {
    # Mirror tools/chatter/dotenv.py: DOWAGER_CHATTER_ENV_PATH override
    # wins; else <repo_root>\.env. We deliberately do NOT fall through
    # to tools/chatter/.env from the PS side -- if someone has a legacy
    # placement there, env_check.py will still find it; the PS scripts
    # only ever create/edit the canonical repo-root path.
    if ($env:DOWAGER_CHATTER_ENV_PATH) {
        return $env:DOWAGER_CHATTER_ENV_PATH
    }
    return (Join-Path (Get-ChatterRepoRoot) '.env')
}

function Get-ChatterEnvExamplePath {
    return (Join-Path (Get-ChatterRepoRoot) '.env.example')
}

function Get-ChatterLegacyConfigPath {
    $local = $env:LOCALAPPDATA
    if (-not $local) { $local = Join-Path $env:USERPROFILE 'AppData\Local' }
    return (Join-Path $local 'DowagerMod\chatter\config.json')
}

function Invoke-ChatterEnvCheck {
    <#
    .SYNOPSIS
        Run tools/chatter/env_check.py and return its parsed JSON output.

    .DESCRIPTION
        Single source of truth for "what does the daemon see right now?".
        Returns a PSCustomObject with fields:
          env_present, env_path, problems[], redacted{...}, legacy_present,
          legacy_path, ready, [candidates[]]
        Exit code is preserved in $script:LastEnvCheckExit so callers can
        branch on it (0 = ready, 2 = validation problems, 3 = no .env).
    #>
    $py = (Get-Command python -ErrorAction SilentlyContinue)
    if (-not $py) {
        # python.exe missing: emit a fake report so callers can still
        # render something coherent rather than crashing on $null.$field.
        $script:LastEnvCheckExit = 4
        return [PSCustomObject]@{
            env_present = $false
            env_path = $null
            problems = @("python.exe not found on PATH; cannot validate .env")
            redacted = [PSCustomObject]@{}
            legacy_present = $false
            legacy_path = ""
            ready = $false
        }
    }
    $repo = Get-ChatterRepoRoot
    Push-Location $repo
    try {
        $json = & python -m tools.chatter.env_check 2>&1 | Out-String
        $script:LastEnvCheckExit = $LASTEXITCODE
    } finally {
        Pop-Location
    }
    try {
        return ($json | ConvertFrom-Json)
    } catch {
        # Couldn't parse -- dump raw output so the operator sees it.
        Write-Warning "env_check.py output was not valid JSON:`n$json"
        return $null
    }
}

