$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest
Set-Location -LiteralPath $PSScriptRoot

$source = "D:\p42_scratch\erdos142_q42_partial_at_most_five_state_wall_20260819"
$sourceExpected = @{
    "AT_MOST_FIVE_STATE_SUNFLOWER_WALL.md" = "6fa6b6b2fb2a113f837e37960a63edb17c759691af982fa24e3a6ab3c575eb72"
    "exhaust_five_state_orbits.cpp" = "2f311d5aa389cca75ba75c1d21a6fc13d8612ba013a952704a8163103e00c6cb"
    "verify_lower_state_live_sccs.py" = "b59ac9c7da552ff520755a43ebd317c51b0d5ebdfd41ae835a90515e9d9b1139"
    "run.ps1" = "302a244d71a4f5668239c388cc4ba6237ea44a54a3b9a4999ccdd1bd87038631"
    "run.sh" = "853d765139a5839ae4f90fe357abf13a1f96115ce6389f499195cd229d947c74"
}
foreach ($name in $sourceExpected.Keys) {
    $actual = (Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $source $name)).Hash.ToLowerInvariant()
    if ($actual -ne $sourceExpected[$name]) { throw "Frozen source mismatch: $name" }
}
$sourceManifest = (Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $source "SHA256SUMS")).Hash.ToLowerInvariant()
if ($sourceManifest -ne "2005c6c005f97393f0e69b1ea8ec9656b800e3731c409eaa67092e7d5d736d71") {
    throw "Frozen source manifest mismatch"
}

Get-Content -LiteralPath ".\SHA256SUMS" | ForEach-Object {
    if ($_ -notmatch '^([0-9a-f]{64})  (.+)$') { throw "Malformed audit manifest line: $_" }
    $actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $Matches[2]).Hash.ToLowerInvariant()
    if ($actual -ne $Matches[1]) { throw "Audit SHA-256 mismatch: $($Matches[2])" }
}
Write-Output "PASS_FROZEN_SOURCE_AND_AUDIT_HASHES"

$binary = Join-Path ([IO.Path]::GetTempPath()) ("q42-five-hostile-" + [Guid]::NewGuid().ToString("N") + ".exe")
try {
    & g++ -std=c++14 -O3 -Wall -Wextra -pedantic .\independent_five_state_orbit_audit.cpp -o $binary
    if ($LASTEXITCODE -ne 0) { throw "Independent C++ compile failed" }
    & $binary
    if ($LASTEXITCODE -ne 0) { throw "Independent C++ audit failed" }
    & python -I .\independent_lower_physical_scope_audit.py
    if ($LASTEXITCODE -ne 0) { throw "Independent Python audit failed" }
    Write-Output "APPROVE_Q42_AT_MOST_FIVE_STATE_SUNFLOWER_WALL"
}
finally {
    if (Test-Path -LiteralPath $binary) { Remove-Item -LiteralPath $binary -Force }
}
