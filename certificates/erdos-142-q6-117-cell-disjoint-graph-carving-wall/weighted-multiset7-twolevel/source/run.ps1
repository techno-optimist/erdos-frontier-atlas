$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Manifest = Join-Path $Root "SHA256SUMS"

foreach ($Line in Get-Content -LiteralPath $Manifest) {
    if ([string]::IsNullOrWhiteSpace($Line)) { continue }
    $Parts = $Line -split '\s+', 2
    if ($Parts.Count -ne 2) { throw "malformed SHA256SUMS line: $Line" }
    $Expected = $Parts[0].ToUpperInvariant()
    $Relative = $Parts[1].TrimStart('*')
    $Actual = (Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $Root $Relative)).Hash
    if ($Actual -ne $Expected) {
        throw "SHA256 mismatch for $Relative`: expected $Expected, got $Actual"
    }
}

Write-Output "PASS_SHA256SUMS"
python -I (Join-Path $Root "verify.py")
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Output "PASS_WEIGHTED_MULTISET7_TWO_LEVEL_RUNNER"
