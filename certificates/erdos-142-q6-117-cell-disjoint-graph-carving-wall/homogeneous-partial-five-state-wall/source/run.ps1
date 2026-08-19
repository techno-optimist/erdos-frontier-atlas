$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest
Set-Location -LiteralPath $PSScriptRoot

$expected = @{}
Get-Content -LiteralPath ".\SHA256SUMS" | ForEach-Object {
    if ($_ -notmatch '^([0-9a-f]{64})  (.+)$') {
        throw "Malformed SHA256SUMS line: $_"
    }
    $expected[$Matches[2]] = $Matches[1]
}
if ($expected.Count -ne 5) {
    throw "Manifest must bind exactly five payload files"
}
foreach ($name in $expected.Keys) {
    $actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $name).Hash.ToLowerInvariant()
    if ($actual -ne $expected[$name]) {
        throw "SHA-256 mismatch for ${name}: expected $($expected[$name]), got $actual"
    }
}
Write-Output "PASS_SHA256SUMS"

$compiler = (Get-Command g++ -ErrorAction Stop).Source
$binary = Join-Path ([IO.Path]::GetTempPath()) (
    "q42-five-state-" + [Guid]::NewGuid().ToString("N") + ".exe")
try {
    & $compiler -std=c++14 -O3 -Wall -Wextra -pedantic `
        .\exhaust_five_state_orbits.cpp -o $binary
    if ($LASTEXITCODE -ne 0) {
        throw "C++ compilation failed with exit code $LASTEXITCODE"
    }
    & $binary
    if ($LASTEXITCODE -ne 0) {
        throw "Five-state verifier failed with exit code $LASTEXITCODE"
    }
    python -I .\verify_lower_state_live_sccs.py
    if ($LASTEXITCODE -ne 0) {
        throw "Lower-state verifier failed with exit code $LASTEXITCODE"
    }
    Write-Output "PASS_AT_MOST_FIVE_STATE_SUNFLOWER_WALL"
}
finally {
    if (Test-Path -LiteralPath $binary) {
        Remove-Item -LiteralPath $binary -Force
    }
}
