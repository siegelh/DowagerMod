param(
    [string]$RepoRoot = "."
)

$ErrorActionPreference = "Stop"

function Get-XmlDirectChildTags {
    param(
        [string]$Path,
        [string]$NodeName
    )
    if (-not (Test-Path $Path)) { return @() }
    [xml]$xml = Get-Content -Path $Path
    $node = $xml.SelectSingleNode("//*[local-name()='$NodeName']")
    if (-not $node) { return @() }
    $names = @()
    foreach ($n in $node.ChildNodes) { $names += $n.LocalName }
    return $names | Sort-Object -Unique
}

$assetsRoot = Join-Path $RepoRoot "CoreFiles/Sid Meier's Civilization IV Beyond the Sword/Beyond the Sword/Assets/XML"

$traitFile = Join-Path $assetsRoot "Civilizations/CIV4TraitInfos.xml"
$civicFile = Join-Path $assetsRoot "GameInfo/CIV4CivicInfos.xml"
$improvementFile = Join-Path $assetsRoot "Terrain/CIV4ImprovementInfos.xml"
$buildFile = Join-Path $assetsRoot "Units/CIV4BuildInfos.xml"
$unitFile = Join-Path $assetsRoot "Units/CIV4UnitInfos.xml"
$buildingFile = Join-Path $assetsRoot "Buildings/CIV4BuildingInfos.xml"

Write-Output "# Mechanics Scan"
Write-Output ""
Write-Output "Repo root: $((Resolve-Path $RepoRoot).Path)"
Write-Output ""

Write-Output "## TraitInfo Direct Tags"
Get-XmlDirectChildTags -Path $traitFile -NodeName "TraitInfo" | ForEach-Object {
    Write-Output "- $_"
}
Write-Output ""

Write-Output "## CivicInfo Direct Tags"
Get-XmlDirectChildTags -Path $civicFile -NodeName "CivicInfo" | ForEach-Object {
    Write-Output "- $_"
}
Write-Output ""

Write-Output "## ImprovementInfo Direct Tags"
Get-XmlDirectChildTags -Path $improvementFile -NodeName "ImprovementInfo" | ForEach-Object {
    Write-Output "- $_"
}
Write-Output ""

Write-Output "## BuildInfo Direct Tags"
Get-XmlDirectChildTags -Path $buildFile -NodeName "BuildInfo" | ForEach-Object {
    Write-Output "- $_"
}
Write-Output ""

Write-Output "## UnitInfo Build Actions"
if (Test-Path $unitFile) {
    [xml]$unitXml = Get-Content -Path $unitFile
    $builds = $unitXml.SelectNodes("//*[local-name()='UnitInfo']/*[local-name()='Builds']/*[local-name()='Build']")
    $types = @()
    foreach ($b in $builds) { $types += $b.InnerText.Trim() }
    $types | Where-Object { $_ } | Sort-Object -Unique | ForEach-Object {
        Write-Output "- $_"
    }
}
Write-Output ""

Write-Output "## BuildingClass References (for UB planning)"
if (Test-Path $buildingFile) {
    [xml]$buildingXml = Get-Content -Path $buildingFile
    $classes = $buildingXml.SelectNodes("//*[local-name()='BuildingInfo']/*[local-name()='BuildingClass']")
    $vals = @()
    foreach ($c in $classes) { $vals += $c.InnerText.Trim() }
    $vals | Where-Object { $_ } | Sort-Object -Unique | ForEach-Object {
        Write-Output "- $_"
    }
}
Write-Output ""

Write-Output "## Quick Grep: Custom Change Blocks"
$patterns = @(
    "TraitBuildingCommerceChanges",
    "TraitBuildingYieldChanges",
    "TraitSpecialistCommerceChanges",
    "TraitSpecialistYieldChanges",
    "TraitBonusYieldChanges",
    "TraitRouteYieldChanges",
    "ImprovementWorkedCityCommerceChanges",
    "ImprovementInBFCCommerceChanges",
    "MaxPlayerInstances"
)

foreach ($p in $patterns) {
    $hits = rg -n --glob "*.xml" $p $assetsRoot 2>$null
    if ($LASTEXITCODE -eq 0 -and $hits) {
        Write-Output "- $p"
    }
}
