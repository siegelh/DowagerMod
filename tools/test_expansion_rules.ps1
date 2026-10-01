param([string]$RepoRoot = "")
$ErrorActionPreference = "Stop"
if (-not $RepoRoot) {
    $RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
}
$vcvars = "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"
if (!(Test-Path -LiteralPath $vcvars)) {
    throw "Native expansion tests require the installed Visual Studio 2022 C++ tools: $vcvars"
}
$scratch = Join-Path ([IO.Path]::GetTempPath()) ("dowager-expansion-tests-" + [guid]::NewGuid())
New-Item -ItemType Directory -Path $scratch | Out-Null
$exe = Join-Path $scratch "expansion_rules_test.exe"
$obj = Join-Path $scratch "expansion_rules_test.obj"
$source = Join-Path $RepoRoot "tools\tests\expansion_rules_test.cpp"
$include = Join-Path $RepoRoot "third_party\beyond-the-sword-sdk\CvGameCoreDLL"
try {
    $command = 'call "{0}" >nul && cl /nologo /EHsc /W4 /WX /I"{1}" /Fo"{2}" /Fe"{3}" "{4}" && "{3}"' -f $vcvars, $include, $obj, $exe, $source
    & $env:ComSpec /d /c $command
    if ($LASTEXITCODE -ne 0) {
        throw "Native expansion scenarios failed with exit code $LASTEXITCODE"
    }
}
finally {
    foreach ($path in @($exe, $obj)) {
        if (Test-Path -LiteralPath $path) { Remove-Item -LiteralPath $path -Force }
    }
    Remove-Item -LiteralPath $scratch
}
