<#
.SYNOPSIS
Collects a bounded DowagerMod crash report and creates a GitHub issue.

.DESCRIPTION
Run after Civilization IV: Beyond the Sword crashes. The script suggests the
newest multiplayer autosave, collects sanitized diagnostics, writes a ZIP under
%LOCALAPPDATA%\DowagerMod\CrashReports, and creates an issue when GitHub CLI is
installed and authenticated. Save files and minidumps are never uploaded
automatically.
#>
[CmdletBinding()]
param(
    [string]$RepoRoot,
    [string]$LastAction,
    [ValidateSet("Only me", "Host only", "One client", "Multiple players", "Everyone", "Unknown")]
    [string]$WhoCrashed = "Unknown",
    [ValidateSet("Yes", "No", "Not attempted")]
    [string]$Reproduction = "Not attempted",
    [string]$Notes = "",
    [string]$SavePath,
    [switch]$NoSave,
    [switch]$NonInteractive,
    [switch]$DryRun,
    [switch]$SkipIssue,
    [switch]$NoOpen,
    [string]$OutputRoot,
    [string]$ConfigPath,
    [string]$DocumentsPath,
    [string]$LiveInstallRoot,
    [string]$GhPath
)

$ErrorActionPreference = "Stop"
Import-Module Microsoft.PowerShell.Utility -ErrorAction Stop
$script:StartedAt = Get-Date
$script:ExpectedSteps = 9
$script:ProcessedSteps = 0
$script:PersistedFiles = 0
$script:SkippedItems = 0
$script:ErrorItems = 0
$script:CollectedBytes = [Int64]0
$script:CollectionNotes = New-Object System.Collections.Generic.List[string]
$script:TextRedactions = 0

function Get-FileSha256 {
    param([string]$Path)
    $stream = [System.IO.File]::OpenRead($Path)
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        return ([System.BitConverter]::ToString($sha.ComputeHash($stream))).Replace("-", "").ToLowerInvariant()
    }
    finally {
        $sha.Dispose()
        $stream.Dispose()
    }
}

function Write-Utf8NoBom {
    param([string]$Path, [string]$Content)
    $parent = Split-Path -Parent $Path
    if ($parent -and -not (Test-Path -LiteralPath $parent)) {
        New-Item -ItemType Directory -Path $parent -Force | Out-Null
    }
    [System.IO.File]::WriteAllText(
        $Path,
        $Content,
        (New-Object System.Text.UTF8Encoding($false)))
}

function Write-Step {
    param(
        [string]$Name,
        [string]$Status,
        [datetime]$Start,
        [Int64]$InputBytes = 0,
        [Int64]$OutputBytes = 0,
        [string]$Detail = ""
    )
    $script:ProcessedSteps++
    $duration = [Math]::Round(((Get-Date) - $Start).TotalMilliseconds)
    $stamp = (Get-Date).ToString("o")
    Write-Host ((
        "[crash-report] timestamp={0} step={1}/{2} name={3} status={4} " +
        "input_bytes={5} output_bytes={6} duration_ms={7} retries=0 detail={8}") -f
        $stamp, $script:ProcessedSteps, $script:ExpectedSteps, $Name, $Status,
        $InputBytes, $OutputBytes, $duration, ($Detail -replace "\s+", "_"))
}

function Invoke-GitText {
    param([string[]]$Arguments)
    try {
        $output = & git -C $RepoRoot @Arguments 2>$null
        if ($LASTEXITCODE -eq 0) {
            return (($output | Out-String).Trim())
        }
    }
    catch {}
    return ""
}

function Protect-Text {
    param([AllowEmptyString()][string]$Text)
    if ($null -eq $Text) { return "" }

    $result = $Text
    $profile = [Environment]::GetFolderPath("UserProfile")
    if ($profile) {
        $updated = [Regex]::Replace($result, [Regex]::Escape($profile), "<USERPROFILE>", [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)
        if ($updated -ne $result) { $script:TextRedactions++ }
        $result = $updated
    }
    if ($env:USERNAME) {
        $userPattern = "(?i)(?<![A-Za-z0-9])" + [Regex]::Escape($env:USERNAME) + "(?![A-Za-z0-9])"
        $updated = [Regex]::Replace($result, $userPattern, "<USERNAME>")
        if ($updated -ne $result) { $script:TextRedactions++ }
        $result = $updated
    }

    $patterns = @(
        [PSCustomObject]@{ Pattern = "(?i)\bgithub_pat_[A-Za-z0-9_]{20,}\b"; Replacement = "<REDACTED:GITHUB_TOKEN>" },
        [PSCustomObject]@{ Pattern = "(?i)\bgh[pousr]_[A-Za-z0-9]{20,}\b"; Replacement = "<REDACTED:GITHUB_TOKEN>" },
        [PSCustomObject]@{ Pattern = "(?i)\bBearer\s+[A-Za-z0-9._~+/\-=]{12,}"; Replacement = "Bearer <REDACTED:TOKEN>" },
        [PSCustomObject]@{ Pattern = "(?i)(token|password|passwd|secret|api[_-]?key)\s*[:=]\s*[^\s;]+"; Replacement = '$1=<REDACTED>' },
        [PSCustomObject]@{ Pattern = "(?i)(https?://)([^/@:\s]+):([^/@\s]+)@"; Replacement = '$1<REDACTED:CREDENTIALS>@' },
        [PSCustomObject]@{ Pattern = "\b(?:\d{1,3}\.){3}\d{1,3}\b"; Replacement = "<REDACTED:IP>" },
        [PSCustomObject]@{ Pattern = "(?i)\b[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}\b"; Replacement = "<REDACTED:EMAIL>" }
    )
    foreach ($pattern in $patterns) {
        $updated = [Regex]::Replace($result, $pattern.Pattern, $pattern.Replacement)
        if ($updated -ne $result) { $script:TextRedactions++ }
        $result = $updated
    }
    return $result
}

function Get-FileRecord {
    param([string]$Path, [string]$Kind)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return $null }
    $item = Get-Item -LiteralPath $Path
    return [PSCustomObject][ordered]@{
        Kind = $Kind
        Name = $item.Name
        Bytes = [Int64]$item.Length
        LastWriteUtc = $item.LastWriteTimeUtc.ToString("o")
        Sha256 = Get-FileSha256 -Path $item.FullName
    }
}

function Add-BinaryEvidence {
    param(
        [string]$Source,
        [string]$DestinationDirectory,
        [string]$Kind
    )
    if (-not (Test-Path -LiteralPath $Source -PathType Leaf)) {
        $script:SkippedItems++
        $script:CollectionNotes.Add("$Kind unavailable.")
        return $null
    }
    if (-not (Test-Path -LiteralPath $DestinationDirectory)) {
        New-Item -ItemType Directory -Path $DestinationDirectory -Force | Out-Null
    }
    $item = Get-Item -LiteralPath $Source
    $destination = Join-Path $DestinationDirectory $item.Name
    Copy-Item -LiteralPath $item.FullName -Destination $destination -Force
    $script:PersistedFiles++
    $script:CollectedBytes += [Int64]$item.Length
    return Get-FileRecord -Path $destination -Kind $Kind
}

function Add-SanitizedTextEvidence {
    param(
        [string]$Source,
        [string]$DestinationDirectory,
        [string]$Kind,
        [Int64]$MaximumBytes = 10MB
    )
    if (-not (Test-Path -LiteralPath $Source -PathType Leaf)) {
        $script:SkippedItems++
        return $null
    }
    $item = Get-Item -LiteralPath $Source
    if ($item.Length -gt $MaximumBytes) {
        $script:SkippedItems++
        $script:CollectionNotes.Add("$Kind exceeded $MaximumBytes bytes and was not collected: $($item.Name)")
        return $null
    }
    try {
        $content = [System.IO.File]::ReadAllText($item.FullName)
        $sanitized = Protect-Text -Text $content
        if (-not (Test-Path -LiteralPath $DestinationDirectory)) {
            New-Item -ItemType Directory -Path $DestinationDirectory -Force | Out-Null
        }
        $destination = Join-Path $DestinationDirectory $item.Name
        Write-Utf8NoBom -Path $destination -Content $sanitized
        $written = Get-Item -LiteralPath $destination
        $script:PersistedFiles++
        $script:CollectedBytes += [Int64]$written.Length
        return Get-FileRecord -Path $destination -Kind $Kind
    }
    catch {
        $script:ErrorItems++
        $script:CollectionNotes.Add("Failed to sanitize $Kind $($item.Name): $($_.Exception.Message)")
        return $null
    }
}

function Get-DocumentsDirectory {
    if ($DocumentsPath) {
        return [System.IO.Path]::GetFullPath($DocumentsPath)
    }

    $candidates = New-Object System.Collections.Generic.List[string]
    $known = [Environment]::GetFolderPath("MyDocuments")
    if ($known) { $candidates.Add($known) }
    if ($env:USERPROFILE) {
        $candidates.Add((Join-Path $env:USERPROFILE "Documents"))
    }
    foreach ($name in @("OneDrive", "OneDriveCommercial", "OneDriveConsumer")) {
        $value = [Environment]::GetEnvironmentVariable($name)
        if ($value) { $candidates.Add((Join-Path $value "Documents")) }
    }

    foreach ($candidate in @($candidates | Select-Object -Unique)) {
        if (Test-Path -LiteralPath $candidate -PathType Container) {
            return (Resolve-Path -LiteralPath $candidate).Path
        }
    }
    return $known
}

function Get-LiveInstallDirectory {
    if ($LiveInstallRoot) {
        return [System.IO.Path]::GetFullPath($LiveInstallRoot)
    }

    $resolvedConfig = $ConfigPath
    if (-not $resolvedConfig) {
        $resolvedConfig = Join-Path $env:LOCALAPPDATA "DowagerMod\config.json"
    }
    if (Test-Path -LiteralPath $resolvedConfig -PathType Leaf) {
        try {
            $config = Get-Content -LiteralPath $resolvedConfig -Raw | ConvertFrom-Json
            if ($config.install_dir -and (Test-Path -LiteralPath $config.install_dir -PathType Container)) {
                return (Resolve-Path -LiteralPath $config.install_dir).Path
            }
        }
        catch {
            $script:CollectionNotes.Add("Installer config could not be read: $($_.Exception.Message)")
        }
    }

    $steamRoots = @(
        "C:\Program Files (x86)\Steam\steamapps\common",
        "C:\Program Files\Steam\steamapps\common",
        "D:\Steam\steamapps\common",
        "D:\SteamLibrary\steamapps\common",
        "E:\SteamLibrary\steamapps\common"
    )
    foreach ($steamRoot in $steamRoots) {
        $candidate = Join-Path $steamRoot "Sid Meier's Civilization IV Beyond the Sword"
        if (Test-Path -LiteralPath (Join-Path $candidate "Beyond the Sword\Civ4BeyondSword.exe") -PathType Leaf) {
            return $candidate
        }
    }
    return ""
}

function Get-SaveCandidates {
    param([string]$SavesRoot)
    if (-not (Test-Path -LiteralPath $SavesRoot -PathType Container)) { return @() }

    $root = (Resolve-Path -LiteralPath $SavesRoot).Path
    $candidates = foreach ($file in Get-ChildItem -LiteralPath $root -Recurse -File -Filter *.CivBeyondSwordSave -ErrorAction SilentlyContinue) {
        $relative = $file.FullName.Substring($root.Length).TrimStart("\", "/")
        $normalized = $relative.Replace("/", "\").ToLowerInvariant()
        $priority = 4
        $category = "Other save"
        if ($normalized -match '(^|\\)multi\\auto\\') {
            $priority = 0
            $category = "Multiplayer autosave"
        }
        elseif ($normalized -match '(^|\\)multi\\') {
            $priority = 1
            $category = "Multiplayer save"
        }
        elseif ($normalized -match '(^|\\)auto\\') {
            $priority = 2
            $category = "Autosave"
        }
        elseif ($normalized -match '(^|\\)single\\') {
            $priority = 3
            $category = "Single-player save"
        }
        [PSCustomObject]@{
            Path = $file.FullName
            Name = $file.Name
            RelativePath = $relative
            Category = $category
            Priority = $priority
            LastWriteTime = $file.LastWriteTime
            Bytes = [Int64]$file.Length
        }
    }
    return @($candidates | Sort-Object Priority, @{ Expression = "LastWriteTime"; Descending = $true })
}

function Select-CrashSave {
    param([object[]]$Candidates)
    if ($NoSave) { return $null }
    if ($SavePath) {
        if (-not (Test-Path -LiteralPath $SavePath -PathType Leaf)) {
            throw "Requested save does not exist: $SavePath"
        }
        return Get-Item -LiteralPath $SavePath
    }
    if ($Candidates.Count -eq 0) { return $null }

    $preferred = $Candidates[0]
    if ($NonInteractive) {
        return Get-Item -LiteralPath $preferred.Path
    }

    Write-Host ""
    Write-Host "Suggested crash save:"
    Write-Host "  $($preferred.Name)"
    Write-Host "  Category: $($preferred.Category)"
    Write-Host "  Modified: $($preferred.LastWriteTime) ($([Math]::Round(((Get-Date) - $preferred.LastWriteTime).TotalMinutes, 1)) minutes ago)"
    Write-Host "  Size: $([Math]::Round($preferred.Bytes / 1MB, 2)) MB"
    Write-Host ""
    Write-Host "Save files can contain game and player names. The save is copied only"
    Write-Host "into the local ZIP and is never uploaded automatically."
    $answer = Read-Host "Use this save? [Y/n/path]"
    if ([string]::IsNullOrWhiteSpace($answer) -or $answer -match '^(?i)y(es)?$') {
        return Get-Item -LiteralPath $preferred.Path
    }
    if ($answer -match '^(?i)n(o)?$') {
        return $null
    }
    if (Test-Path -LiteralPath $answer -PathType Leaf) {
        return Get-Item -LiteralPath $answer
    }
    throw "Save selection was neither yes, no, nor an existing file path."
}

function Invoke-MultiplayerManifest {
    param([string]$GameRoot, [string]$OutputPath, [string]$Label)
    if (-not $GameRoot -or -not (Test-Path -LiteralPath $GameRoot -PathType Container)) {
        $script:SkippedItems++
        $script:CollectionNotes.Add("$Label multiplayer manifest root unavailable.")
        return $null
    }
    $tool = Join-Path $RepoRoot "tools\multiplayer_manifest.ps1"
    try {
        $engine = (Get-Process -Id $PID).Path
        & $engine -NoProfile -ExecutionPolicy Bypass -File $tool -Root $GameRoot -OutputPath $OutputPath | Out-Host
        if ($LASTEXITCODE -ne 0) {
            throw "$Label multiplayer manifest exited with $LASTEXITCODE."
        }
        $script:PersistedFiles++
        $script:CollectedBytes += (Get-Item -LiteralPath $OutputPath).Length
        return Get-Content -LiteralPath $OutputPath -Raw | ConvertFrom-Json
    }
    catch {
        $script:ErrorItems++
        $script:CollectionNotes.Add("$Label multiplayer manifest failed: $($_.Exception.Message)")
        return $null
    }
}

function Get-SystemSummary {
    $summary = [ordered]@{}
    try {
        $os = Get-CimInstance Win32_OperatingSystem
        $summary.OperatingSystem = "$($os.Caption) $($os.Version)"
        $summary.TotalMemoryBytes = [Int64]$os.TotalVisibleMemorySize * 1KB
        $summary.FreeMemoryBytes = [Int64]$os.FreePhysicalMemory * 1KB
    }
    catch {
        $summary.OperatingSystem = "Unavailable"
    }
    try {
        $summary.Gpu = @(
            Get-CimInstance Win32_VideoController |
                ForEach-Object {
                    [ordered]@{
                        Name = $_.Name
                        DriverVersion = $_.DriverVersion
                        AdapterRamBytes = if ($_.AdapterRAM) { [Int64]$_.AdapterRAM } else { $null }
                    }
                }
        )
    }
    catch {
        $summary.Gpu = @()
    }
    try {
        $driveName = if ($LiveInstallRoot) { (Split-Path -Qualifier $LiveInstallRoot).TrimEnd("\") } else { $env:SystemDrive }
        $drive = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='$driveName'"
        $summary.Disk = [ordered]@{
            Drive = $driveName
            FreeBytes = [Int64]$drive.FreeSpace
            SizeBytes = [Int64]$drive.Size
        }
    }
    catch {
        $summary.Disk = $null
    }
    return [PSCustomObject]$summary
}

function Get-WindowsCrashEvents {
    try {
        $start = (Get-Date).AddDays(-2)
        $events = Get-WinEvent -FilterHashtable @{ LogName = "Application"; StartTime = $start } -MaxEvents 250 -ErrorAction Stop |
            Where-Object {
                $_.ProviderName -in @("Application Error", "Windows Error Reporting") -and
                $_.Message -match "(?i)Civ4BeyondSword"
            } |
            Select-Object -First 10
        return @($events | ForEach-Object {
            [PSCustomObject][ordered]@{
                TimeCreated = $_.TimeCreated.ToString("o")
                Provider = $_.ProviderName
                EventId = $_.Id
                Message = Protect-Text -Text $_.Message
            }
        })
    }
    catch {
        $script:CollectionNotes.Add("Windows crash events unavailable: $($_.Exception.Message)")
        return @()
    }
}

function Remove-OldArtifacts {
    param(
        [string]$Directory,
        [string]$Pattern,
        [int]$MaximumFiles = 3,
        [Int64]$MaximumBytes = 250MB
    )
    if (-not (Test-Path -LiteralPath $Directory -PathType Container)) { return }
    $files = @(
        Get-ChildItem -LiteralPath $Directory -File -Filter $Pattern -ErrorAction SilentlyContinue |
            Sort-Object LastWriteTimeUtc -Descending
    )
    $kept = New-Object System.Collections.Generic.List[object]
    [Int64]$keptBytes = 0
    foreach ($file in $files) {
        if ($kept.Count -lt $MaximumFiles -and ($keptBytes + $file.Length) -le $MaximumBytes) {
            $kept.Add($file)
            $keptBytes += [Int64]$file.Length
        }
        else {
            Remove-Item -LiteralPath $file.FullName -Force
        }
    }
}

function Remove-StaleStagingDirectories {
    param([string]$Directory)
    if (-not (Test-Path -LiteralPath $Directory -PathType Container)) { return }
    $cutoff = (Get-Date).AddHours(-1)
    foreach ($candidate in Get-ChildItem -LiteralPath $Directory -Directory -Filter ".staging-*" -ErrorAction SilentlyContinue) {
        if ($candidate.LastWriteTime -lt $cutoff -and $candidate.Name.StartsWith(".staging-", [StringComparison]::Ordinal)) {
            Remove-Item -LiteralPath $candidate.FullName -Recurse -Force
        }
    }
}

if (-not $RepoRoot) {
    $RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
}
else {
    $RepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path
}
if (-not (Test-Path -LiteralPath (Join-Path $RepoRoot ".git"))) {
    $gitDir = Invoke-GitText -Arguments @("rev-parse", "--git-dir")
    if (-not $gitDir) { throw "Repository root could not be resolved: $RepoRoot" }
}

if (-not $OutputRoot) {
    if (-not $env:LOCALAPPDATA) { throw "LOCALAPPDATA is not available." }
    $OutputRoot = Join-Path $env:LOCALAPPDATA "DowagerMod\CrashReports"
}
$OutputRoot = [System.IO.Path]::GetFullPath($OutputRoot)
$pendingRoot = Join-Path $OutputRoot "Pending"
New-Item -ItemType Directory -Path $OutputRoot -Force | Out-Null
New-Item -ItemType Directory -Path $pendingRoot -Force | Out-Null
Remove-StaleStagingDirectories -Directory $OutputRoot
Remove-OldArtifacts -Directory $pendingRoot -Pattern *.dmp
Remove-OldArtifacts -Directory $OutputRoot -Pattern "DowagerMod-Crash-*.zip"

$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$incidentId = "DowagerMod-Crash-$stamp"
$stagingRoot = Join-Path $OutputRoot (".staging-" + [Guid]::NewGuid().ToString("N"))
$evidenceRoot = Join-Path $stagingRoot "evidence"
New-Item -ItemType Directory -Path $evidenceRoot -Force | Out-Null

try {
    $stepStart = Get-Date
    $branch = Invoke-GitText -Arguments @("branch", "--show-current")
    $commit = Invoke-GitText -Arguments @("rev-parse", "HEAD")
    $status = Invoke-GitText -Arguments @("status", "--short")
    $remote = Invoke-GitText -Arguments @("remote", "get-url", "origin")
    $repoState = [PSCustomObject][ordered]@{
        Branch = $branch
        Commit = $commit
        Dirty = -not [string]::IsNullOrWhiteSpace($status)
        Status = Protect-Text -Text $status
        Remote = Protect-Text -Text $remote
    }
    Write-Step -Name "repository" -Status "success" -Start $stepStart -Detail $branch

    $stepStart = Get-Date
    $documents = Get-DocumentsDirectory
    $userDataRoot = if ($documents) { Join-Path $documents "My Games\Beyond the Sword" } else { "" }
    $savesRoot = if ($userDataRoot) { Join-Path $userDataRoot "Saves" } else { "" }
    $saveCandidates = @(Get-SaveCandidates -SavesRoot $savesRoot)
    $selectedSave = Select-CrashSave -Candidates $saveCandidates
    $saveRecord = $null
    if ($selectedSave) {
        $saveRecord = Add-BinaryEvidence -Source $selectedSave.FullName -DestinationDirectory (Join-Path $evidenceRoot "save") -Kind "SelectedSave"
    }
    else {
        $script:SkippedItems++
        $script:CollectionNotes.Add("No save was selected.")
    }
    Write-Step -Name "save" -Status $(if ($selectedSave) { "success" } else { "skipped" }) -Start $stepStart -InputBytes $(if ($selectedSave) { $selectedSave.Length } else { 0 }) -OutputBytes $(if ($saveRecord) { $saveRecord.Bytes } else { 0 }) -Detail $(if ($selectedSave) { $selectedSave.Name } else { "none" })

    if (-not $NonInteractive) {
        if (-not $LastAction) { $LastAction = Read-Host "What were you doing immediately before the crash?" }
        $whoAnswer = Read-Host "Who crashed? [$WhoCrashed]"
        if ($whoAnswer) { $WhoCrashed = $whoAnswer }
        $reproAnswer = Read-Host "Does the same save/action reproduce the crash? [$Reproduction]"
        if ($reproAnswer) { $Reproduction = $reproAnswer }
        $notesAnswer = Read-Host "Additional notes (optional)"
        if ($notesAnswer) { $Notes = $notesAnswer }
    }
    if (-not $LastAction) { $LastAction = "Not provided" }

    $stepStart = Get-Date
    $LiveInstallRoot = Get-LiveInstallDirectory
    $repoGameRoot = Join-Path $RepoRoot "CoreFiles\Sid Meier's Civilization IV Beyond the Sword"
    $repoAssets = Join-Path $repoGameRoot "Beyond the Sword\Assets"
    $liveAssets = if ($LiveInstallRoot) { Join-Path $LiveInstallRoot "Beyond the Sword\Assets" } else { "" }
    $repoDll = Join-Path $repoAssets "CvGameCoreDLL.dll"
    $liveDll = if ($liveAssets) { Join-Path $liveAssets "CvGameCoreDLL.dll" } else { "" }
    $hashRecords = @()
    $hashTargets = @(
        [PSCustomObject]@{ Path = $repoDll; Kind = "Repository DLL" },
        [PSCustomObject]@{ Path = $liveDll; Kind = "Installed DLL" },
        [PSCustomObject]@{ Path = (Join-Path $repoAssets "res\Fonts\GameFont.tga"); Kind = "Repository GameFont" },
        [PSCustomObject]@{ Path = (Join-Path $repoAssets "res\Fonts\GameFont_75.tga"); Kind = "Repository GameFont75" },
        [PSCustomObject]@{ Path = $(if ($liveAssets) { Join-Path $liveAssets "res\Fonts\GameFont.tga" } else { "" }); Kind = "Installed GameFont" },
        [PSCustomObject]@{ Path = $(if ($liveAssets) { Join-Path $liveAssets "res\Fonts\GameFont_75.tga" } else { "" }); Kind = "Installed GameFont75" }
    )
    foreach ($target in $hashTargets) {
        if ($target.Path) {
            $record = Get-FileRecord -Path $target.Path -Kind $target.Kind
            if ($record) { $hashRecords += $record }
        }
    }
    Write-Step -Name "runtime_identity" -Status $(if ($LiveInstallRoot) { "success" } else { "partial" }) -Start $stepStart -Detail $(if ($LiveInstallRoot) { "live_install_found" } else { "live_install_missing" })

    $stepStart = Get-Date
    $manifestDir = Join-Path $evidenceRoot "manifests"
    New-Item -ItemType Directory -Path $manifestDir -Force | Out-Null
    $repoManifestPath = Join-Path $manifestDir "repository-multiplayer-manifest.json"
    $liveManifestPath = Join-Path $manifestDir "installed-multiplayer-manifest.json"
    $repoManifest = Invoke-MultiplayerManifest -GameRoot $repoGameRoot -OutputPath $repoManifestPath -Label "Repository"
    $liveManifest = Invoke-MultiplayerManifest -GameRoot $LiveInstallRoot -OutputPath $liveManifestPath -Label "Installed"
    $manifestMatch = $null
    if ($repoManifest -and $liveManifest) {
        $manifestMatch = $repoManifest.Digests.All -eq $liveManifest.Digests.All
    }
    Write-Step -Name "manifests" -Status $(if ($null -eq $manifestMatch) { "partial" } elseif ($manifestMatch) { "success" } else { "mismatch" }) -Start $stepStart -Detail "match=$manifestMatch"

    $stepStart = Get-Date
    $logRecords = @()
    if ($liveAssets) {
        $tracePath = Join-Path $liveAssets "CvGameCoreDLL_trace.log"
        $record = Add-SanitizedTextEvidence -Source $tracePath -DestinationDirectory (Join-Path $evidenceRoot "logs") -Kind "DLL trace"
        if ($record) { $logRecords += $record }
    }
    $logsRoot = if ($userDataRoot) { Join-Path $userDataRoot "Logs" } else { "" }
    if ($logsRoot -and (Test-Path -LiteralPath $logsRoot -PathType Container)) {
        $knownLogPattern = "(?i)^(PythonErr|PythonDbg|xml|init|resmgr|SynchLog|MPLog|network|OOS).*"
        $logs = @(
            Get-ChildItem -LiteralPath $logsRoot -File -ErrorAction SilentlyContinue |
                Where-Object { $_.Name -match $knownLogPattern } |
                Sort-Object LastWriteTimeUtc -Descending |
                Select-Object -First 30
        )
        foreach ($log in $logs) {
            $record = Add-SanitizedTextEvidence -Source $log.FullName -DestinationDirectory (Join-Path $evidenceRoot "logs") -Kind "Civ4 log"
            if ($record) { $logRecords += $record }
        }
    }
    $glyphRoot = Join-Path $env:LOCALAPPDATA "DowagerMod\GlyphDiagnostics"
    if (Test-Path -LiteralPath $glyphRoot -PathType Container) {
        foreach ($glyph in @(
            Get-ChildItem -LiteralPath $glyphRoot -File -Filter *.log -ErrorAction SilentlyContinue |
                Sort-Object LastWriteTimeUtc -Descending |
                Select-Object -First 4
        )) {
            $record = Add-SanitizedTextEvidence -Source $glyph.FullName -DestinationDirectory (Join-Path $evidenceRoot "glyph") -Kind "Glyph diagnostic"
            if ($record) { $logRecords += $record }
        }
    }
    Write-Step -Name "logs" -Status "success" -Start $stepStart -OutputBytes (($logRecords | Measure-Object Bytes -Sum).Sum) -Detail "files=$($logRecords.Count)"

    $stepStart = Get-Date
    $dumpRecord = $null
    $pendingDump = Get-ChildItem -LiteralPath $pendingRoot -File -Filter *.dmp -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTimeUtc -Descending |
        Select-Object -First 1
    if ($pendingDump) {
        $dumpRecord = Add-BinaryEvidence -Source $pendingDump.FullName -DestinationDirectory (Join-Path $evidenceRoot "dump") -Kind "Crash minidump"
    }
    else {
        $script:SkippedItems++
        $script:CollectionNotes.Add("No pending crash minidump was found.")
    }
    Write-Step -Name "minidump" -Status $(if ($dumpRecord) { "success" } else { "skipped" }) -Start $stepStart -OutputBytes $(if ($dumpRecord) { $dumpRecord.Bytes } else { 0 }) -Detail $(if ($dumpRecord) { $dumpRecord.Name } else { "none" })

    $stepStart = Get-Date
    $windowsEvents = @(Get-WindowsCrashEvents)
    $systemSummary = Get-SystemSummary
    $systemPath = Join-Path $evidenceRoot "system.json"
    $systemDocument = [PSCustomObject][ordered]@{
        CollectedAt = (Get-Date).ToString("o")
        System = $systemSummary
        WindowsCrashEvents = $windowsEvents
    }
    Write-Utf8NoBom -Path $systemPath -Content (($systemDocument | ConvertTo-Json -Depth 8) + [Environment]::NewLine)
    $script:PersistedFiles++
    $script:CollectedBytes += (Get-Item -LiteralPath $systemPath).Length
    Write-Step -Name "system" -Status "success" -Start $stepStart -Detail "events=$($windowsEvents.Count)"

    $stepStart = Get-Date
    $allEvidence = @()
    if ($saveRecord) { $allEvidence += $saveRecord }
    if ($dumpRecord) { $allEvidence += $dumpRecord }
    $allEvidence += $logRecords
    $allEvidence += $hashRecords
    $manifestDocument = [PSCustomObject][ordered]@{
        SchemaVersion = 1
        IncidentId = $incidentId
        CollectedAt = (Get-Date).ToString("o")
        Report = [PSCustomObject][ordered]@{
            LastAction = Protect-Text -Text $LastAction
            WhoCrashed = Protect-Text -Text $WhoCrashed
            Reproduction = Protect-Text -Text $Reproduction
            Notes = Protect-Text -Text $Notes
        }
        Repository = $repoState
        Paths = [PSCustomObject][ordered]@{
            Documents = "<REDACTED>"
            UserDataFound = [bool]($userDataRoot -and (Test-Path -LiteralPath $userDataRoot))
            SavesFound = [bool]($savesRoot -and (Test-Path -LiteralPath $savesRoot))
            LiveInstallFound = [bool]$LiveInstallRoot
            Output = "%LOCALAPPDATA%\DowagerMod\CrashReports"
        }
        Autosave = [PSCustomObject][ordered]@{
            CandidateCount = $saveCandidates.Count
            Selected = if ($saveRecord) { $saveRecord.Name } else { $null }
            SelectedCategory = if ($selectedSave) {
                $match = $saveCandidates | Where-Object { $_.Path -eq $selectedSave.FullName } | Select-Object -First 1
                if ($match) { $match.Category } else { "Explicit path" }
            } else { $null }
        }
        RuntimeHashes = $hashRecords
        MultiplayerManifest = [PSCustomObject][ordered]@{
            RepositoryDigest = if ($repoManifest) { $repoManifest.Digests.All } else { $null }
            InstalledDigest = if ($liveManifest) { $liveManifest.Digests.All } else { $null }
            Match = $manifestMatch
        }
        Evidence = $allEvidence
        Reconciliation = [PSCustomObject][ordered]@{
            ExpectedSteps = $script:ExpectedSteps
            ProcessedStepsBeforePackage = $script:ProcessedSteps
            PersistedFilesBeforePackage = $script:PersistedFiles
            SkippedItems = $script:SkippedItems
            Errors = $script:ErrorItems
            CollectedBytesBeforePackage = $script:CollectedBytes
            RedactionMatches = $script:TextRedactions
        }
        Notes = @($script:CollectionNotes)
    }
    $manifestPath = Join-Path $stagingRoot "manifest.json"
    Write-Utf8NoBom -Path $manifestPath -Content (($manifestDocument | ConvertTo-Json -Depth 10) + [Environment]::NewLine)

    $latestEvent = $windowsEvents | Select-Object -First 1
    $repoDllRecord = $hashRecords | Where-Object { $_.Kind -eq "Repository DLL" } | Select-Object -First 1
    $liveDllRecord = $hashRecords | Where-Object { $_.Kind -eq "Installed DLL" } | Select-Object -First 1
    $dllMatch = $repoDllRecord -and $liveDllRecord -and $repoDllRecord.Sha256 -eq $liveDllRecord.Sha256
    $reportLines = @(
        "# DowagerMod Crash Report",
        "",
        "- Incident: $incidentId",
        "- Last action: $(Protect-Text -Text $LastAction)",
        "- Who crashed: $(Protect-Text -Text $WhoCrashed)",
        "- Reproduction: $(Protect-Text -Text $Reproduction)",
        "- Notes: $(Protect-Text -Text $Notes)",
        "",
        "## Build",
        "",
        "- Branch: $branch",
        "- Commit: $commit",
        "- Worktree dirty: $($repoState.Dirty)",
        "- Installed DLL matches repository: $dllMatch",
        "- Multiplayer payload matches: $manifestMatch",
        "",
        "## Evidence",
        "",
        "- Suggested save candidates: $($saveCandidates.Count)",
        "- Selected save: $(if ($saveRecord) { $saveRecord.Name } else { 'None' })",
        "- Crash minidump: $(if ($dumpRecord) { $dumpRecord.Name } else { 'Unavailable' })",
        "- Sanitized logs: $($logRecords.Count)",
        "- Windows crash events: $($windowsEvents.Count)",
        "- Diagnostic ZIP attachment: pending manual upload",
        "",
        "## Latest Windows event",
        "",
        $(if ($latestEvent) { ('```text' + "`n" + $latestEvent.Message + "`n" + '```') } else { "No matching Civ4 event was found in the last two days." }),
        "",
        "## Collection notes",
        "",
        $(if ($script:CollectionNotes.Count) { ($script:CollectionNotes | ForEach-Object { "- $(Protect-Text -Text $_)" }) -join "`n" } else { "- None" })
    )
    $reportPath = Join-Path $stagingRoot "report.md"
    Write-Utf8NoBom -Path $reportPath -Content (($reportLines -join [Environment]::NewLine) + [Environment]::NewLine)

    $issueLines = @(
        "## Crash summary",
        "",
        "- **Action:** $(Protect-Text -Text $LastAction)",
        "- **Affected players:** $(Protect-Text -Text $WhoCrashed)",
        "- **Reproduction:** $(Protect-Text -Text $Reproduction)",
        "- **Notes:** $(Protect-Text -Text $Notes)",
        "",
        "## Build identity",
        "",
        "- **Branch:** ``$branch``",
        "- **Commit:** ``$commit``",
        "- **Worktree dirty:** $($repoState.Dirty)",
        "- **Installed DLL matches repository:** $dllMatch",
        "- **Multiplayer XML/Python/DLL manifest matches:** $manifestMatch",
        "",
        "## Collected evidence",
        "",
        "- **Selected save:** $(if ($saveRecord) { $saveRecord.Name } else { 'None' })",
        "- **Crash minidump:** $(if ($dumpRecord) { $dumpRecord.Name } else { 'Unavailable' })",
        "- **Sanitized logs:** $($logRecords.Count)",
        "- **Windows crash events:** $($windowsEvents.Count)",
        "- **Diagnostic bundle attachment:** **PENDING**",
        "",
        "> The reporter created a local ZIP. Drag it onto this issue in a comment, wait for the upload to finish, then submit the comment.",
        "",
        "## Latest Windows crash event",
        "",
        $(if ($latestEvent) { ('```text' + "`n" + $latestEvent.Message + "`n" + '```') } else { "No matching Civ4 event was found in the last two days." }),
        "",
        "## Collector notes",
        "",
        $(if ($script:CollectionNotes.Count) { ($script:CollectionNotes | ForEach-Object { "- $(Protect-Text -Text $_)" }) -join "`n" } else { "- None" }),
        "",
        "_Generated by ``tools/report_crash.ps1``. Binary saves and dumps were not uploaded automatically._"
    )
    $issueBody = ($issueLines -join [Environment]::NewLine) + [Environment]::NewLine
    if ((New-Object System.Text.UTF8Encoding($false)).GetByteCount($issueBody) -gt 60000) {
        throw "Generated issue body exceeded the 60,000-byte safety limit."
    }
    $issueBodyPath = Join-Path $stagingRoot "issue-body.md"
    Write-Utf8NoBom -Path $issueBodyPath -Content $issueBody

    $zipPath = Join-Path $OutputRoot "$incidentId.zip"
    Compress-Archive -LiteralPath @($manifestPath, $reportPath, $issueBodyPath, $evidenceRoot) -DestinationPath $zipPath -CompressionLevel Optimal -Force
    $zipItem = Get-Item -LiteralPath $zipPath
    if ($zipItem.Length -gt 250MB) {
        Remove-Item -LiteralPath $zipItem.FullName -Force
        throw "The diagnostic ZIP exceeded the 250 MB storage limit. Run the reporter again without the save or attach the save separately."
    }
    Write-Step -Name "package" -Status "success" -Start $stepStart -InputBytes $script:CollectedBytes -OutputBytes $zipItem.Length -Detail $zipItem.Name

    Remove-OldArtifacts -Directory $OutputRoot -Pattern "DowagerMod-Crash-*.zip"

    $stepStart = Get-Date
    $issueUrl = ""
    $issueMode = "skipped"
    $issueCreated = $false
    $issueBodyCopied = $false
    $titleAction = (Protect-Text -Text $LastAction) -replace "[\r\n]+", " "
    if ($titleAction.Length -gt 80) { $titleAction = $titleAction.Substring(0, 80) }
    $issueTitle = "[Crash] $titleAction"

    if (-not $SkipIssue -and -not $DryRun) {
        $ghCommand = $null
        if ($GhPath) {
            if (Test-Path -LiteralPath $GhPath -PathType Leaf) { $ghCommand = $GhPath }
        }
        else {
            $resolvedGh = Get-Command gh -ErrorAction SilentlyContinue
            if ($resolvedGh) { $ghCommand = $resolvedGh.Source }
        }

        $authenticated = $false
        if ($ghCommand) {
            & $ghCommand auth status --hostname github.com *> $null
            $authenticated = $LASTEXITCODE -eq 0
        }
        if ($authenticated) {
            $output = & $ghCommand issue create --repo "siegelh/DowagerMod" --title $issueTitle --label "bug" --body-file $issueBodyPath 2>&1
            if ($LASTEXITCODE -eq 0) {
                $issueCreated = $true
                $issueUrl = (($output | Out-String).Trim() -split "\s+" | Where-Object { $_ -match "^https://github\.com/" } | Select-Object -Last 1)
                if ($issueUrl) {
                    $issueMode = "created"
                }
                else {
                    $issueMode = "created-url-unavailable"
                    $issueUrl = "https://github.com/siegelh/DowagerMod/issues"
                    $script:CollectionNotes.Add("GitHub reported successful issue creation but did not return a parseable issue URL.")
                }
            }
            else {
                $script:ErrorItems++
                $script:CollectionNotes.Add("GitHub issue creation failed: $(Protect-Text -Text (($output | Out-String).Trim()))")
            }
        }

        if (-not $issueCreated -and -not $issueUrl) {
            $issueMode = "browser-fallback"
            if (-not $NoOpen) {
                try {
                    Set-Clipboard -Value $issueBody
                    $issueBodyCopied = $true
                }
                catch {}
            }
            $encodedTitle = [Uri]::EscapeDataString($issueTitle)
            $issueUrl = "https://github.com/siegelh/DowagerMod/issues/new?labels=bug&title=$encodedTitle"
        }
    }
    elseif ($DryRun) {
        $issueMode = "dry-run"
        if ($GhPath) {
            & $GhPath issue create --repo "siegelh/DowagerMod" --title $issueTitle --label "bug" --body-file $issueBodyPath | Out-Null
            if ($LASTEXITCODE -ne 0) { throw "Fake gh dry-run invocation failed." }
        }
    }

    if (-not $NoOpen) {
        if ($issueUrl) {
            Start-Process $issueUrl
        }
        Start-Process explorer.exe -ArgumentList "/select,`"$zipPath`""
    }
    Write-Step -Name "github" -Status $issueMode -Start $stepStart -Detail $(if ($issueUrl) { $issueUrl } else { "none" })

    $duration = [Math]::Round(((Get-Date) - $script:StartedAt).TotalSeconds, 2)
    $pass = $script:ErrorItems -eq 0
    Write-Host ""
    Write-Host ((("[crash-report-summary] expected_steps={0} processed_steps={1} persisted_files={2} " +
        "skipped_items={3} errors={4} collected_bytes={5} zip_bytes={6} duration_seconds={7} result={8}") -f
        $script:ExpectedSteps, $script:ProcessedSteps, $script:PersistedFiles,
        $script:SkippedItems, $script:ErrorItems, $script:CollectedBytes,
        $zipItem.Length, $duration, $(if ($pass) { "PASS" } else { "PARTIAL" })))
    Write-Host ""
    Write-Host "Crash report ZIP:"
    Write-Host "  $zipPath"
    if ($issueMode -eq "created") {
        Write-Host "GitHub issue:"
        Write-Host "  $issueUrl"
        Write-Host ""
        Write-Host "Drag the selected ZIP onto the open GitHub issue, wait for the upload"
        Write-Host "to finish, then click Comment."
    }
    elseif ($issueMode -eq "browser-fallback") {
        Write-Host ""
        Write-Host "GitHub CLI was unavailable or unauthenticated."
        if ($issueBodyCopied) {
            Write-Host "The issue body was copied to the clipboard and a browser draft was opened."
            Write-Host "Paste the body, submit the issue, then drag the selected ZIP into a"
            Write-Host "comment, wait for the upload to finish, and click Comment."
        }
        else {
            Write-Host "The prepared issue body is inside the ZIP as issue-body.md."
        }
    }
    elseif ($DryRun) {
        Write-Host "Dry run complete; no GitHub issue was created."
    }

    if (-not $pass) { exit 2 }
    exit 0
}
finally {
    if (Test-Path -LiteralPath $stagingRoot) {
        Remove-Item -LiteralPath $stagingRoot -Recurse -Force
    }
}
