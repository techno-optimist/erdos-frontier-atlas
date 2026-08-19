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
if ($expected.Count -ne 3) {
    throw "Audit manifest must bind exactly three payload files"
}
foreach ($name in $expected.Keys) {
    $actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $name).Hash.ToLowerInvariant()
    if ($actual -ne $expected[$name]) {
        throw "SHA-256 mismatch for ${name}: expected $($expected[$name]), got $actual"
    }
}
Write-Output "PASS_AUDIT_SHA256SUMS"

python -I .\independent_weighted_multiset7_audit.py
if ($LASTEXITCODE -ne 0) {
    throw "Independent audit failed with exit code $LASTEXITCODE"
}
