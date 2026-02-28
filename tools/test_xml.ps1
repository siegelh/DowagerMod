param(
    [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path,
    [switch]$All,
    [switch]$ChangedOnly,
    [string]$XmlRootRelative = "CoreFiles\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Assets\XML"
)

$ErrorActionPreference = "Stop"
if ($PSVersionTable.PSVersion.Major -ge 7) {
    $PSNativeCommandUseErrorActionPreference = $false
}

if ($All -and $ChangedOnly) {
    throw "Use either -All or -ChangedOnly, not both."
}

if (-not $All -and -not $ChangedOnly) {
    $ChangedOnly = $true
}

function Get-RelativePath {
    param(
        [string]$BasePath,
        [string]$TargetPath
    )

    $baseFull = [System.IO.Path]::GetFullPath($BasePath)
    if (-not $baseFull.EndsWith([System.IO.Path]::DirectorySeparatorChar.ToString())) {
        $baseFull += [System.IO.Path]::DirectorySeparatorChar
    }

    $baseUri = New-Object System.Uri($baseFull)
    $targetUri = New-Object System.Uri([System.IO.Path]::GetFullPath($TargetPath))
    return [System.Uri]::UnescapeDataString($baseUri.MakeRelativeUri($targetUri).ToString()).Replace("/", "\")
}

function Test-PathUnderRoot {
    param(
        [string]$Path,
        [string]$RootPath
    )

    $fullPath = [System.IO.Path]::GetFullPath($Path)
    $fullRoot = [System.IO.Path]::GetFullPath($RootPath)

    if (-not $fullRoot.EndsWith([System.IO.Path]::DirectorySeparatorChar.ToString())) {
        $fullRoot += [System.IO.Path]::DirectorySeparatorChar
    }

    return $fullPath.StartsWith($fullRoot, [System.StringComparison]::OrdinalIgnoreCase)
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

function Invoke-XmlValidation {
    param(
        [string]$XmlPath
    )

    $doc = New-Object -ComObject "MSXML2.DOMDocument.3.0"
    $doc.async = $false
    $doc.validateOnParse = $true
    $doc.resolveExternals = $true
    $doc.preserveWhiteSpace = $true

    try {
        $loaded = $doc.load($XmlPath)
    }
    catch {
        return [PSCustomObject]@{
            Kind     = "ValidationError"
            File     = $XmlPath
            Line     = 0
            Column   = 0
            Code     = 0
            Reason   = $_.Exception.Message.Trim()
            Source   = ""
        }
    }

    $parseError = $doc.parseError
    if ((-not $loaded) -or ($null -ne $parseError -and $parseError.errorCode -ne 0)) {
        $reason = "Unknown XML parse/validation error."
        $src = ""
        $line = 0
        $col = 0
        $code = 0

        if ($null -ne $parseError) {
            $line = [int]$parseError.line
            $col = [int]$parseError.linepos
            $code = [int]$parseError.errorCode

            if ($parseError.reason) {
                $reason = $parseError.reason.Trim()
            }
            if ($parseError.srcText) {
                $src = $parseError.srcText.Trim()
            }
        }

        $kind = "ValidationError"
        if ($reason -like "Error opening input file:*") {
            $kind = "MissingSchema"
        }

        return [PSCustomObject]@{
            Kind     = $kind
            File     = $XmlPath
            Line     = $line
            Column   = $col
            Code     = $code
            Reason   = $reason
            Source   = $src
        }
    }

    return $null
}

$xmlRoot = Join-Path $RepoRoot $XmlRootRelative
if (-not (Test-Path $xmlRoot)) {
    throw "XML root not found: $xmlRoot"
}

$allXmlFiles = Get-ChildItem -Path $xmlRoot -Recurse -File -Filter *.xml |
    Select-Object -ExpandProperty FullName

$xmlFileMap = @{}

if ($All) {
    foreach ($xmlFile in $allXmlFiles) {
        $xmlFileMap[$xmlFile] = $true
    }
}
else {
    $schemaNames = @()
    $changedRepoPaths = Get-ChangedRepoPaths -RepoRootPath $RepoRoot

    foreach ($repoPath in $changedRepoPaths) {
        if (-not $repoPath.EndsWith(".xml", [System.StringComparison]::OrdinalIgnoreCase)) {
            continue
        }

        $fullPath = Join-Path $RepoRoot $repoPath
        if (-not (Test-Path $fullPath)) {
            continue
        }

        if (-not (Test-PathUnderRoot -Path $fullPath -RootPath $xmlRoot)) {
            continue
        }

        $xmlFileMap[$fullPath] = $true

        $fileName = [System.IO.Path]::GetFileName($fullPath)
        if ($fileName.IndexOf("Schema", [System.StringComparison]::OrdinalIgnoreCase) -ge 0) {
            $schemaNames += $fileName
        }
    }

    foreach ($schemaName in ($schemaNames | Sort-Object -Unique)) {
        $schemaNeedle = "x-schema:$schemaName"
        $matches = Select-String -Path $allXmlFiles -SimpleMatch -Pattern $schemaNeedle
        foreach ($match in $matches) {
            $xmlFileMap[$match.Path] = $true
        }
    }
}

$xmlFilesToValidate = $xmlFileMap.Keys | Sort-Object

if ($xmlFilesToValidate.Count -eq 0) {
    Write-Host "[XML] No XML files selected for validation."
    return
}

Write-Host "[XML] Validating $($xmlFilesToValidate.Count) file(s)..."

$failures = @()
$missingSchemaWarnings = @()
foreach ($xmlFile in $xmlFilesToValidate) {
    $failure = Invoke-XmlValidation -XmlPath $xmlFile
    if ($null -ne $failure) {
        if ($failure.Kind -eq "MissingSchema") {
            $missingSchemaWarnings += $failure
        }
        else {
            $failures += $failure
        }
    }
}

if ($missingSchemaWarnings.Count -gt 0) {
    Write-Host "[XML] Skipping $($missingSchemaWarnings.Count) file(s) due to unresolved schema file references."
    foreach ($warning in $missingSchemaWarnings) {
        $relative = Get-RelativePath -BasePath $RepoRoot -TargetPath $warning.File
        Write-Host "  [WARN] $relative"
        Write-Host "         $($warning.Reason)"
    }
}

if ($failures.Count -gt 0) {
    Write-Host "[XML] Validation failed with $($failures.Count) error(s)."
    foreach ($failure in $failures) {
        $relative = Get-RelativePath -BasePath $RepoRoot -TargetPath $failure.File
        $location = $relative
        if ($failure.Line -gt 0) {
            $location += ":$($failure.Line)"
            if ($failure.Column -gt 0) {
                $location += ":$($failure.Column)"
            }
        }

        Write-Host "  [FAIL] $location"
        Write-Host "         code=$($failure.Code) reason=$($failure.Reason)"
        if ($failure.Source) {
            Write-Host "         src=$($failure.Source)"
        }
    }

    throw "XML validation failed."
}

Write-Host "[XML] Validation passed."
