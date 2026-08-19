param(
    [Parameter(Position = 0)]
    [string]$FiveStateDir = ""
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest
Set-Location -LiteralPath $PSScriptRoot

if ([string]::IsNullOrWhiteSpace($FiveStateDir)) {
    if (-not [string]::IsNullOrWhiteSpace($env:Q42_FIVE_STATE_DIR)) {
        $FiveStateDir = $env:Q42_FIVE_STATE_DIR
    }
    else {
        $FiveStateDir = Join-Path (Split-Path -Parent $PSScriptRoot) `
            "erdos142_q42_partial_at_most_five_state_wall_20260819"
        Write-Warning "Using convenience-only sibling <=5 path; pinned hashes, not this location, establish trust."
    }
}
if (-not (Test-Path -LiteralPath $FiveStateDir -PathType Container)) {
    throw "Missing <=5 dependency directory: $FiveStateDir"
}

$expected = @{}
Get-Content -LiteralPath ".\SHA256SUMS" | ForEach-Object {
    if ($_ -notmatch '^([0-9a-f]{64})  (.+)$') {
        throw "Malformed SHA256SUMS line: $_"
    }
    $expected[$Matches[2]] = $Matches[1]
}
if ($expected.Count -ne 7) { throw "Manifest must bind exactly seven payload files" }
foreach ($name in $expected.Keys) {
    $actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $name).Hash.ToLowerInvariant()
    if ($actual -ne $expected[$name]) { throw "SHA-256 mismatch: $name" }
}
Write-Output "PASS_SHA256SUMS"

$compiler = (Get-Command g++ -ErrorAction Stop).Source
$primary = Join-Path ([IO.Path]::GetTempPath()) ("q42-six-primary-" + [Guid]::NewGuid().ToString("N") + ".exe")
$burnside = Join-Path ([IO.Path]::GetTempPath()) ("q42-six-burnside-" + [Guid]::NewGuid().ToString("N") + ".exe")
$certificate = Join-Path ([IO.Path]::GetTempPath()) ("q42-six-boundary-" + [Guid]::NewGuid().ToString("N") + ".tsv")
try {
    & $compiler -std=c++14 -O3 -Wall -Wextra -pedantic `
        .\exhaust_six_state_orbits_cegar.cpp -o $primary
    if ($LASTEXITCODE -ne 0) { throw "Primary C++ compilation failed" }
    & $primary $certificate
    if ($LASTEXITCODE -ne 0) { throw "Primary six-state replay failed" }

    & $compiler -std=c++14 -O3 -Wall -Wextra -pedantic `
        .\verify_six_state_burnside.cpp -o $burnside
    if ($LASTEXITCODE -ne 0) { throw "Burnside C++ compilation failed" }
    & $burnside
    if ($LASTEXITCODE -ne 0) { throw "Burnside replay failed" }

    & python -I .\verify_six_boundary.py $certificate
    if ($LASTEXITCODE -ne 0) { throw "Boundary replay failed" }
    & python -I .\verify_six_scope_physical.py $FiveStateDir
    if ($LASTEXITCODE -ne 0) { throw "Scope/physical replay failed" }
    Write-Output "PASS_AT_MOST_SIX_STATE_SUNFLOWER_WALL"
}
finally {
    foreach ($path in @($primary, $burnside, $certificate)) {
        if (Test-Path -LiteralPath $path) { Remove-Item -LiteralPath $path -Force }
    }
}
