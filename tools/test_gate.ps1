param(
    [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path,
    [switch]$All,
    [switch]$CheckDll,
    [switch]$SkipXml,
    [switch]$SkipDll
)

$ErrorActionPreference = "Stop"
if ($PSVersionTable.PSVersion.Major -ge 7) {
    $PSNativeCommandUseErrorActionPreference = $false
}

function Invoke-Git {
    param(
        [string]$RepoRootPath,
        [string[]]$Arguments
    )

    $oldEap = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        $output = & git -C $RepoRootPath @Arguments 2>&1
    }
    finally {
        $ErrorActionPreference = $oldEap
    }

    if ($LASTEXITCODE -ne 0) {
        throw "git $($Arguments -join ' ') failed with exit code $LASTEXITCODE."
    }

    return $output |
        ForEach-Object { $_.ToString() } |
        Where-Object {
            $_ -and
            ($_ -notlike "warning: LF will be replaced by CRLF*") -and
            ($_ -notlike "The file will have its original line endings in your working directory*")
        }
}

function Get-ChangedRepoPaths {
    param(
        [string]$RepoRootPath
    )

    $paths = @()
    $paths += Invoke-Git -RepoRootPath $RepoRootPath -Arguments @("diff", "--name-only", "--diff-filter=ACMRTUXB")
    $paths += Invoke-Git -RepoRootPath $RepoRootPath -Arguments @("diff", "--cached", "--name-only", "--diff-filter=ACMRTUXB")
    $paths += Invoke-Git -RepoRootPath $RepoRootPath -Arguments @("ls-files", "--others", "--exclude-standard")

    return $paths |
        ForEach-Object { $_.ToString().Trim() } |
        Where-Object { $_ -ne "" } |
        Sort-Object -Unique
}

function Test-IsDllSourcePath {
    param(
        [string]$RepoPath
    )

    $normalized = $RepoPath.Replace("/", "\")
    $dllPrefix = "third_party\beyond-the-sword-sdk\CvGameCoreDLL\"
    if (-not $normalized.StartsWith($dllPrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
        return $false
    }

    $fileName = [System.IO.Path]::GetFileName($normalized)
    if ($fileName -like "Makefile*") {
        return $true
    }

    $extension = [System.IO.Path]::GetExtension($normalized)
    $dllExtensions = @(
        ".c", ".cpp", ".cc", ".h", ".hpp", ".hh",
        ".inl", ".rc", ".def", ".vcxproj", ".sln"
    )

    return $dllExtensions -contains $extension.ToLowerInvariant()
}

$failed = $false

if ($All) {
    $CheckDll = $true
}

if (-not $SkipXml) {
    try {
        if ($All) {
            & (Join-Path $PSScriptRoot "test_xml.ps1") -RepoRoot $RepoRoot -All
        }
        else {
            & (Join-Path $PSScriptRoot "test_xml.ps1") -RepoRoot $RepoRoot -ChangedOnly
        }
        Write-Host "[GATE] XML checks passed."
    }
    catch {
        $failed = $true
        Write-Host "[GATE] XML checks failed: $($_.Exception.Message)"
    }
}

$shouldRunDllBuild = $false
if ($CheckDll -and -not $SkipDll) {
    $shouldRunDllBuild = $All
    if (-not $All) {
        $changedPaths = Get-ChangedRepoPaths -RepoRootPath $RepoRoot
        foreach ($repoPath in $changedPaths) {
            if (Test-IsDllSourcePath -RepoPath $repoPath) {
                $shouldRunDllBuild = $true
                break
            }
        }
    }
}

if ($CheckDll -and -not $SkipDll) {
    if ($shouldRunDllBuild) {
        try {
            & (Join-Path $PSScriptRoot "build_civ4_dll.ps1") -RepoRoot $RepoRoot -NoDeploy
            Write-Host "[GATE] DLL build passed."
        }
        catch {
            $failed = $true
            Write-Host "[GATE] DLL build failed: $($_.Exception.Message)"
        }
    }
    else {
        Write-Host "[GATE] DLL build skipped (no DLL-source changes detected)."
    }
}
elseif (-not $SkipDll) {
    Write-Host "[GATE] DLL build skipped (XML-focused gate mode)."
}

if ($failed) {
    throw "test_gate failed."
}

Write-Host "[GATE] All requested checks passed."
