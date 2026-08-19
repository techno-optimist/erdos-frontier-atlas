param(
    [Parameter(Position = 0)]
    [string]$SourceDir = "",
    [Parameter(Position = 1)]
    [string]$FiveStateDir = ""
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest
$AuditDir = $PSScriptRoot
Set-Location -LiteralPath $AuditDir

if ([string]::IsNullOrWhiteSpace($SourceDir)) {
    $SourceDir = Join-Path (Split-Path -Parent $PSScriptRoot) `
        "erdos142_q42_partial_six_state_frontier_20260819"
}
if ([string]::IsNullOrWhiteSpace($FiveStateDir)) {
    $FiveStateDir = Join-Path (Split-Path -Parent $PSScriptRoot) `
        "erdos142_q42_partial_at_most_five_state_wall_20260819"
}
foreach ($path in @($SourceDir, $FiveStateDir)) {
    if (-not (Test-Path -LiteralPath $path -PathType Container)) {
        throw "Missing dependency directory: $path"
    }
}

$expected = @{}
Get-Content -LiteralPath ".\SHA256SUMS.hostile" | ForEach-Object {
    if ($_ -notmatch '^([0-9a-f]{64})  (.+)$') {
        throw "Malformed hostile manifest line: $_"
    }
    $expected[$Matches[2]] = $Matches[1]
}
if ($expected.Count -ne 5) { throw "Hostile manifest must bind five payloads" }
foreach ($name in $expected.Keys) {
    $actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $name).Hash.ToLowerInvariant()
    if ($actual -ne $expected[$name]) { throw "Hostile SHA-256 mismatch: $name" }
}
Write-Output "PASS_HOSTILE_SHA256SUMS"

& python -I .\independent_six_scope_physical.py `
    --source $SourceDir --five $FiveStateDir
if ($LASTEXITCODE -ne 0) { throw "Independent scope/physical replay failed" }

& (Join-Path $SourceDir "run.ps1") -FiveStateDir $FiveStateDir
if ($LASTEXITCODE -ne 0) { throw "Frozen source replay failed" }
Set-Location -LiteralPath $AuditDir

$compiler = (Get-Command g++ -ErrorAction Stop).Source
$binary = Join-Path ([IO.Path]::GetTempPath()) `
    ("q42-six-hostile-" + [Guid]::NewGuid().ToString("N") + ".exe")
try {
    & $compiler -std=c++14 -O3 -Wall -Wextra -pedantic `
        .\independent_six_state.cpp -o $binary
    if ($LASTEXITCODE -ne 0) { throw "Independent C++ compilation failed" }
    & $binary
    if ($LASTEXITCODE -ne 0) { throw "Independent six-state census failed" }
}
finally {
    if (Test-Path -LiteralPath $binary) {
        Remove-Item -LiteralPath $binary -Force
    }
}

Write-Output "PASS_HOSTILE_SIX_STATE_NATIVE_AUDIT"
