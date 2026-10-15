[CmdletBinding()]
param(
    [string]$RepoRoot
)

$ErrorActionPreference = "Stop"
if (-not $RepoRoot) {
    $RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
}

$scratch = Join-Path $env:TEMP ("DowagerMod-CrashReporterTest-" + [Guid]::NewGuid().ToString("N"))
$documents = Join-Path $scratch "Documents"
$output = Join-Path $scratch "output"
$fallbackOutput = Join-Path $scratch "fallback-output"
$expanded = Join-Path $scratch "expanded"
$fakeGh = Join-Path $scratch "fake-gh.cmd"
$fakeGhLog = Join-Path $scratch "fake-gh.log"
$reporter = Join-Path $RepoRoot "tools\report_crash.ps1"
$gameRoot = Join-Path $RepoRoot "CoreFiles\Sid Meier's Civilization IV Beyond the Sword"
$engine = (Get-Process -Id $PID).Path

function Assert-True {
    param([bool]$Condition, [string]$Message)
    if (-not $Condition) { throw $Message }
}

function Write-AsciiFile {
    param([string]$Path, [string]$Content)
    $parent = Split-Path -Parent $Path
    if (-not (Test-Path -LiteralPath $parent)) {
        New-Item -ItemType Directory -Path $parent -Force | Out-Null
    }
    [System.IO.File]::WriteAllText($Path, $Content, [System.Text.Encoding]::ASCII)
}

try {
    $multiAuto = Join-Path $documents "My Games\Beyond the Sword\Saves\multi\auto"
    $singleAuto = Join-Path $documents "My Games\Beyond the Sword\Saves\single\auto"
    $logs = Join-Path $documents "My Games\Beyond the Sword\Logs"
    New-Item -ItemType Directory -Path $multiAuto, $singleAuto, $logs, (Join-Path $output "Pending") -Force | Out-Null

    $multiSave = Join-Path $multiAuto "Multi-Auto.CivBeyondSwordSave"
    $singleSave = Join-Path $singleAuto "Newer-Single-Auto.CivBeyondSwordSave"
    Write-AsciiFile -Path $multiSave -Content "multiplayer save"
    Write-AsciiFile -Path $singleSave -Content "single player save"
    (Get-Item -LiteralPath $multiSave).LastWriteTime = (Get-Date).AddMinutes(-10)
    (Get-Item -LiteralPath $singleSave).LastWriteTime = (Get-Date).AddMinutes(-1)

    $fakeToken = "github_" + "pat_" + "abcdefghijklmnopqrstuvwxyz123456"
    $fakeSecret = "super-" + "secret-" + "value"
    Write-AsciiFile -Path (Join-Path $logs "PythonErr.log") -Content @"
User $env:USERNAME at $env:USERPROFILE
Email player@example.com IP 192.168.1.55
Token $fakeToken
"@
    Write-AsciiFile -Path (Join-Path $output "Pending\synthetic.dmp") -Content "synthetic minidump"

    for ($i = 1; $i -le 4; $i++) {
        $oldZip = Join-Path $output ("DowagerMod-Crash-2000010{0}-000000.zip" -f $i)
        Write-AsciiFile -Path $oldZip -Content "old zip $i"
        (Get-Item -LiteralPath $oldZip).LastWriteTime = (Get-Date).AddDays(-10 + $i)

        $oldDump = Join-Path $output ("Pending\old-$i.dmp")
        Write-AsciiFile -Path $oldDump -Content "old dump $i"
        (Get-Item -LiteralPath $oldDump).LastWriteTime = (Get-Date).AddDays(-10 + $i)
    }
    $staleStaging = Join-Path $output ".staging-stale"
    New-Item -ItemType Directory -Path $staleStaging -Force | Out-Null
    Write-AsciiFile -Path (Join-Path $staleStaging "orphan.txt") -Content "orphaned staging data"
    (Get-Item -LiteralPath $staleStaging).LastWriteTime = (Get-Date).AddHours(-2)

    Write-AsciiFile -Path $fakeGh -Content @"
@echo off
echo %*>>"%FAKE_GH_LOG%"
echo https://github.com/siegelh/DowagerMod/issues/999
exit /b 0
"@
    $env:FAKE_GH_LOG = $fakeGhLog

    $arguments = @(
        "-NoProfile",
        "-ExecutionPolicy", "Bypass",
        "-File", $reporter,
        "-RepoRoot", $RepoRoot,
        "-LastAction", "End turn from 10.20.30.40 player@example.com",
        "-WhoCrashed", "Everyone",
        "-Reproduction", "Not attempted",
        "-Notes", "token=$fakeSecret",
        "-NonInteractive",
        "-DryRun",
        "-NoOpen",
        "-OutputRoot", $output,
        "-DocumentsPath", $documents,
        "-LiveInstallRoot", $gameRoot,
        "-GhPath", $fakeGh
    )
    $result = & $engine @arguments 2>&1
    $exitCode = $LASTEXITCODE
    $result | Out-Host
    Assert-True ($exitCode -eq 0) "Crash reporter exited with $exitCode."

    $zips = @(Get-ChildItem -LiteralPath $output -File -Filter "DowagerMod-Crash-*.zip")
    Assert-True ($zips.Count -le 3) "ZIP retention exceeded three files."
    $createdZip = $zips | Sort-Object LastWriteTimeUtc -Descending | Select-Object -First 1
    Assert-True ($null -ne $createdZip) "No crash ZIP was created."

    $dumps = @(Get-ChildItem -LiteralPath (Join-Path $output "Pending") -File -Filter *.dmp)
    Assert-True ($dumps.Count -le 3) "Dump retention exceeded three files."
    Assert-True (-not (Test-Path -LiteralPath $staleStaging)) "Stale staging directory was not removed."

    Expand-Archive -LiteralPath $createdZip.FullName -DestinationPath $expanded -Force
    $manifestPath = Join-Path $expanded "manifest.json"
    $issueBodyPath = Join-Path $expanded "issue-body.md"
    Assert-True (Test-Path -LiteralPath $manifestPath) "manifest.json missing from ZIP."
    Assert-True (Test-Path -LiteralPath $issueBodyPath) "issue-body.md missing from ZIP."

    $manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
    Assert-True ($manifest.Autosave.Selected -eq "Multi-Auto.CivBeyondSwordSave") "Newest prioritized multi/auto save was not selected."
    Assert-True ($manifest.Autosave.SelectedCategory -eq "Multiplayer autosave") "Selected save category was incorrect."
    Assert-True ($manifest.MultiplayerManifest.Match -eq $true) "Equivalent repository/live manifests did not match."

    $allText = @(
        Get-ChildItem -LiteralPath $expanded -Recurse -File |
            Where-Object { $_.Extension -in @(".md", ".json", ".log", ".txt") } |
            ForEach-Object { Get-Content -LiteralPath $_.FullName -Raw }
    ) -join "`n"
    Assert-True ($allText -notmatch [Regex]::Escape($env:USERPROFILE)) "User profile path was not redacted."
    Assert-True ($allText -notmatch "player@example\.com") "Email was not redacted."
    Assert-True ($allText -notmatch "192\.168\.1\.55|10\.20\.30\.40") "IP address was not redacted."
    Assert-True ($allText -notmatch [Regex]::Escape($fakeToken)) "GitHub token-shaped value was not redacted."
    Assert-True ($allText -notmatch [Regex]::Escape($fakeSecret)) "Secret value was not redacted."
    Assert-True ($allText -match "<REDACTED:IP>") "Expected IP redaction marker was absent."

    $issueBody = Get-Content -LiteralPath $issueBodyPath -Raw
    Assert-True ($issueBody -match "Diagnostic bundle attachment:\*\* \*\*PENDING|Diagnostic bundle attachment:\*\* \*\*PENDING") "Issue body did not mark attachment pending."
    Assert-True (([System.Text.Encoding]::UTF8.GetByteCount($issueBody)) -lt 60000) "Issue body exceeded size limit."

    Assert-True (Test-Path -LiteralPath $fakeGhLog) "Fake gh was not invoked."
    $ghArguments = Get-Content -LiteralPath $fakeGhLog -Raw
    Assert-True ($ghArguments -match "issue create") "Fake gh did not receive issue create."
    Assert-True ($ghArguments -match "siegelh/DowagerMod") "Fake gh repository argument missing."
    Assert-True ($ghArguments -match "--label bug") "Fake gh bug label missing."
    Assert-True ($ghArguments -match "--body-file") "Fake gh body-file argument missing."

    $summary = ($result | Out-String)
    Assert-True ($summary -match "result=PASS") "Reporter did not print a PASS reconciliation summary."
    Assert-True ($summary -match "step=9/9") "Reporter did not complete all nine planned steps."

    $fallbackArguments = @(
        "-NoProfile",
        "-ExecutionPolicy", "Bypass",
        "-File", $reporter,
        "-RepoRoot", $RepoRoot,
        "-LastAction", "Fallback test",
        "-WhoCrashed", "Unknown",
        "-Reproduction", "Not attempted",
        "-NoSave",
        "-NonInteractive",
        "-NoOpen",
        "-OutputRoot", $fallbackOutput,
        "-DocumentsPath", $documents,
        "-LiveInstallRoot", $gameRoot,
        "-GhPath", (Join-Path $scratch "missing-gh.exe")
    )
    $fallbackResult = & $engine @fallbackArguments 2>&1
    $fallbackExitCode = $LASTEXITCODE
    $fallbackResult | Out-Host
    Assert-True ($fallbackExitCode -eq 0) "Browser fallback run exited with $fallbackExitCode."
    $fallbackText = $fallbackResult | Out-String
    Assert-True ($fallbackText -match "status=browser-fallback") "Missing gh did not select browser fallback."
    Assert-True ($fallbackText -match "inside the ZIP as issue-body.md") "No-open fallback instructions were incomplete."
    Assert-True (@(Get-ChildItem -LiteralPath $fallbackOutput -File -Filter "DowagerMod-Crash-*.zip").Count -eq 1) "Fallback did not create one local ZIP."

    Write-Host "PASS: crash reporter selected multi/auto, redacted text, bounded artifacts, packaged evidence, and invoked fake gh."
    Write-Host "PASS: missing gh produced the no-network browser/local fallback without creating an issue."
}
finally {
    Remove-Item Env:FAKE_GH_LOG -ErrorAction SilentlyContinue
    if (Test-Path -LiteralPath $scratch) {
        Remove-Item -LiteralPath $scratch -Recurse -Force
    }
}
