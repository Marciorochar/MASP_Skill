param(
    [string]$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")),
    [string]$OutputDir = "docs/masp/evidencias"
)

$ErrorActionPreference = "Stop"
Push-Location $Root
try {
    $SourcePath = Join-Path $Root "src"
    if ($env:PYTHONPATH) {
        $env:PYTHONPATH = "$SourcePath;$env:PYTHONPATH"
    } else {
        $env:PYTHONPATH = $SourcePath
    }
    python -m masp_skill.cli runtime-smoke --root $Root --output-dir $OutputDir
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
} finally {
    Pop-Location
}
