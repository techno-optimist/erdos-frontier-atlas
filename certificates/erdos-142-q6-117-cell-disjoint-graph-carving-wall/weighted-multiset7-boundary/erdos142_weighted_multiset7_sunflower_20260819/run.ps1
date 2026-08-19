$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
Set-Location -LiteralPath $PSScriptRoot

$manifest = Get-Content -LiteralPath '.\SHA256SUMS'
foreach ($line in $manifest) {
    if ($line -notmatch '^([0-9a-f]{64})  (.+)$') {
        throw "Malformed SHA256SUMS line: $line"
    }
    $expected = $Matches[1]
    $path = $Matches[2]
    $actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $path).Hash.ToLowerInvariant()
    if ($actual -ne $expected) {
        throw "SHA-256 mismatch for ${path}: expected $expected, got $actual"
    }
}
Write-Output 'PASS_SHA256SUMS'

python .\verify_weighted_multiset7.py
if ($LASTEXITCODE -ne 0) {
    throw "Verifier failed with exit code $LASTEXITCODE"
}
python .\finite_state_explorer.py
if ($LASTEXITCODE -ne 0) {
    throw "Finite-state verifier failed with exit code $LASTEXITCODE"
}
Write-Output 'PASS_REPLAY'
