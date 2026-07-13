<#
.SYNOPSIS
Creates or compares deterministic Civilization IV BtS multiplayer manifests.

.EXAMPLE
.\tools\multiplayer_manifest.ps1 -Root ".\CoreFiles\Sid Meier's Civilization IV Beyond the Sword" -OutputPath .\host.json

.EXAMPLE
.\tools\multiplayer_manifest.ps1 -ReferenceRoot ".\CoreFiles\Sid Meier's Civilization IV Beyond the Sword" -CandidateRoot "C:\Games\Sid Meier's Civilization 4 Beyond the Sword"

.EXAMPLE
.\tools\multiplayer_manifest.ps1 -ReferenceManifest .\host.json -CandidateManifest .\friend.json
#>
[CmdletBinding(DefaultParameterSetName = "Generate")]
param(
    [Parameter(Mandatory = $true, ParameterSetName = "Generate")]
    [string]$Root,

    [Parameter(Mandatory = $true, ParameterSetName = "Generate")]
    [string]$OutputPath,

    [Parameter(Mandatory = $true, ParameterSetName = "CompareRoots")]
    [string]$ReferenceRoot,

    [Parameter(Mandatory = $true, ParameterSetName = "CompareRoots")]
    [string]$CandidateRoot,

    [Parameter(ParameterSetName = "CompareRoots")]
    [string]$ReferenceOutputPath,

    [Parameter(ParameterSetName = "CompareRoots")]
    [string]$CandidateOutputPath,

    [Parameter(Mandatory = $true, ParameterSetName = "CompareManifests")]
    [string]$ReferenceManifest,

    [Parameter(Mandatory = $true, ParameterSetName = "CompareManifests")]
    [string]$CandidateManifest
)

$ErrorActionPreference = "Stop"

function Get-StringSha256 {
    param([string]$Value)

    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        $bytes = (New-Object System.Text.UTF8Encoding($false)).GetBytes($Value)
        return ([System.BitConverter]::ToString($sha.ComputeHash($bytes))).Replace("-", "").ToLowerInvariant()
    }
    finally {
        $sha.Dispose()
    }
}

function Get-ManifestDigest {
    param(
        [object[]]$Files,
        [string]$Scope
    )

    $records = New-Object System.Collections.Generic.List[string]
    foreach ($file in $Files) {
        if ($Scope -eq "All" -or $file.Scope -eq $Scope) {
            $canonicalPath = $file.Path.ToString().Replace("\", "/").ToLowerInvariant()
            $records.Add("$($file.Scope)`0$canonicalPath`0$([Int64]$file.Bytes)`0$($file.Sha256.ToString().ToLowerInvariant())`n")
        }
    }
    $records.Sort([System.StringComparer]::Ordinal)
    return Get-StringSha256 -Value ([string]::Concat($records))
}

function Write-ManifestJson {
    param(
        [object]$Manifest,
        [string]$Path
    )

    $fullPath = [System.IO.Path]::GetFullPath($Path)
    $parent = Split-Path -Parent $fullPath
    if ($parent -and -not (Test-Path -LiteralPath $parent)) {
        New-Item -ItemType Directory -Path $parent -Force | Out-Null
    }
    $json = $Manifest | ConvertTo-Json -Depth 5
    [System.IO.File]::WriteAllText($fullPath, $json + [Environment]::NewLine, (New-Object System.Text.UTF8Encoding($false)))
}

function New-MultiplayerManifest {
    param([string]$GameRoot)

    $resolvedRoot = (Resolve-Path -LiteralPath $GameRoot).Path
    $assetsRoot = Join-Path $resolvedRoot "Beyond the Sword\Assets"
    $xmlRoot = Join-Path $assetsRoot "XML"
    $pythonRoot = Join-Path $assetsRoot "Python"
    $dllPath = Join-Path $assetsRoot "CvGameCoreDLL.dll"

    foreach ($requiredPath in @($xmlRoot, $pythonRoot, $dllPath)) {
        if (-not (Test-Path -LiteralPath $requiredPath)) {
            throw "Required multiplayer payload path not found: $requiredPath"
        }
    }

    $selected = @()
    $selected += Get-ChildItem -LiteralPath $xmlRoot -Recurse -File |
        Where-Object { $_.Extension -ieq ".xml" } |
        ForEach-Object { [PSCustomObject]@{ File = $_; Scope = "Xml" } }
    $selected += Get-ChildItem -LiteralPath $pythonRoot -Recurse -File |
        Where-Object { $_.Extension -ieq ".py" -or $_.Extension -ieq ".pyc" } |
        ForEach-Object { [PSCustomObject]@{ File = $_; Scope = "Python" } }
    $selected += [PSCustomObject]@{ File = Get-Item -LiteralPath $dllPath; Scope = "Dll" }

    $byCanonicalPath = @{}
    foreach ($item in $selected) {
        $relative = $item.File.FullName.Substring($resolvedRoot.Length).TrimStart("\", "/").Replace("\", "/")
        $canonical = $relative.ToLowerInvariant()
        if ($byCanonicalPath.ContainsKey($canonical)) {
            throw "Case-insensitive duplicate manifest path: $relative"
        }
        $byCanonicalPath[$canonical] = [PSCustomObject][ordered]@{
            Path   = $relative
            Scope  = $item.Scope
            Bytes  = [Int64]$item.File.Length
            Sha256 = (Get-FileHash -LiteralPath $item.File.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
        }
    }

    $keys = New-Object System.Collections.Generic.List[string]
    foreach ($key in $byCanonicalPath.Keys) {
        $keys.Add($key)
    }
    $keys.Sort([System.StringComparer]::Ordinal)
    $files = @($keys | ForEach-Object { $byCanonicalPath[$_] })

    return [PSCustomObject][ordered]@{
        SchemaVersion = 1
        Scope = [PSCustomObject][ordered]@{
            Xml = "Beyond the Sword/Assets/XML/**/*.xml"
            Python = "Beyond the Sword/Assets/Python/**/*.py and **/*.pyc"
            Dll = "Beyond the Sword/Assets/CvGameCoreDLL.dll"
            OptionalArtIncluded = $false
        }
        FileCount = $files.Count
        Digests = [PSCustomObject][ordered]@{
            All = Get-ManifestDigest -Files $files -Scope "All"
            Xml = Get-ManifestDigest -Files $files -Scope "Xml"
            Python = Get-ManifestDigest -Files $files -Scope "Python"
            Dll = Get-ManifestDigest -Files $files -Scope "Dll"
        }
        Files = $files
    }
}

function Read-MultiplayerManifest {
    param([string]$Path)

    $manifest = Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
    if ([int]$manifest.SchemaVersion -ne 1 -or $null -eq $manifest.Files -or $null -eq $manifest.Digests) {
        throw "Unsupported or invalid multiplayer manifest: $Path"
    }

    $seen = @{}
    foreach ($file in @($manifest.Files)) {
        $normalized = $file.Path.ToString().Replace("\", "/")
        if ($normalized.StartsWith("/") -or $normalized -match "(^|/)\.\.(/|$)" -or
            $file.Sha256.ToString() -notmatch "^[0-9a-fA-F]{64}$" -or [Int64]$file.Bytes -lt 0 -or
            @("Xml", "Python", "Dll") -notcontains $file.Scope.ToString()) {
            throw "Invalid file record in multiplayer manifest $Path."
        }
        $canonical = $normalized.ToLowerInvariant()
        if ($seen.ContainsKey($canonical)) {
            throw "Duplicate path in multiplayer manifest $Path`: $normalized"
        }
        $seen[$canonical] = $true
        $file.Path = $normalized
        $file.Sha256 = $file.Sha256.ToString().ToLowerInvariant()
    }

    if ([int]$manifest.FileCount -ne @($manifest.Files).Count) {
        throw "FileCount does not match the file records in $Path."
    }
    foreach ($scope in @("All", "Xml", "Python", "Dll")) {
        $actual = Get-ManifestDigest -Files @($manifest.Files) -Scope $scope
        if ($actual -ne $manifest.Digests.$scope.ToString().ToLowerInvariant()) {
            throw "$scope aggregate digest validation failed for $Path."
        }
    }
    return $manifest
}

function Compare-MultiplayerManifests {
    param(
        [object]$Reference,
        [object]$Candidate
    )

    $referenceFiles = @{}
    $candidateFiles = @{}
    foreach ($file in @($Reference.Files)) {
        $referenceFiles[$file.Path.ToString().ToLowerInvariant()] = $file
    }
    foreach ($file in @($Candidate.Files)) {
        $candidateFiles[$file.Path.ToString().ToLowerInvariant()] = $file
    }

    $missing = @()
    $extra = @()
    $different = @()
    foreach ($key in $referenceFiles.Keys) {
        if (-not $candidateFiles.ContainsKey($key)) {
            $missing += $referenceFiles[$key].Path
        }
        elseif ($referenceFiles[$key].Sha256 -ne $candidateFiles[$key].Sha256 -or
                [Int64]$referenceFiles[$key].Bytes -ne [Int64]$candidateFiles[$key].Bytes) {
            $different += $referenceFiles[$key].Path
        }
    }
    foreach ($key in $candidateFiles.Keys) {
        if (-not $referenceFiles.ContainsKey($key)) {
            $extra += $candidateFiles[$key].Path
        }
    }

    $missing = @($missing | Sort-Object)
    $extra = @($extra | Sort-Object)
    $different = @($different | Sort-Object)

    if ($missing.Count -eq 0 -and $extra.Count -eq 0 -and $different.Count -eq 0) {
        Write-Host "MATCH: $($Reference.FileCount) synchronized files; SHA-256 $($Reference.Digests.All)"
        return $true
    }

    Write-Host "MISMATCH: missing=$($missing.Count) extra=$($extra.Count) different=$($different.Count)"
    foreach ($path in $missing) { Write-Host "  MISSING   $path" }
    foreach ($path in $extra) { Write-Host "  EXTRA     $path" }
    foreach ($path in $different) { Write-Host "  DIFFERENT $path" }
    return $false
}

try {
    switch ($PSCmdlet.ParameterSetName) {
        "Generate" {
            $manifest = New-MultiplayerManifest -GameRoot $Root
            Write-ManifestJson -Manifest $manifest -Path $OutputPath
            Write-Host "Wrote $($manifest.FileCount)-file manifest: $([System.IO.Path]::GetFullPath($OutputPath))"
            Write-Host "Aggregate SHA-256: $($manifest.Digests.All)"
            exit 0
        }
        "CompareRoots" {
            $reference = New-MultiplayerManifest -GameRoot $ReferenceRoot
            $candidate = New-MultiplayerManifest -GameRoot $CandidateRoot
            if ($ReferenceOutputPath) { Write-ManifestJson -Manifest $reference -Path $ReferenceOutputPath }
            if ($CandidateOutputPath) { Write-ManifestJson -Manifest $candidate -Path $CandidateOutputPath }
            if (Compare-MultiplayerManifests -Reference $reference -Candidate $candidate) { exit 0 }
            exit 1
        }
        "CompareManifests" {
            $reference = Read-MultiplayerManifest -Path $ReferenceManifest
            $candidate = Read-MultiplayerManifest -Path $CandidateManifest
            if (Compare-MultiplayerManifests -Reference $reference -Candidate $candidate) { exit 0 }
            exit 1
        }
    }
}
catch {
    Write-Error $_
    exit 2
}
