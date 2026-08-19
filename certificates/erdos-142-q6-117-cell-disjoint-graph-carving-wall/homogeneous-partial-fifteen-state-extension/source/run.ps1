$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path

python -I (Join-Path $Root "verify_chain_residual.py")
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$Build = Join-Path $env:TEMP ("erdos142_m15_" + [guid]::NewGuid().ToString("N") + ".exe")
try {
    & g++ -O3 -std=c++14 (Join-Path $Root "probe_chain_product.cpp") -o $Build
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    & $Build all-critical
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
} finally {
    if (Test-Path -LiteralPath $Build) { Remove-Item -LiteralPath $Build -Force }
}

Write-Output "PASS_FIFTEEN_STATE_CHAIN_CLOSURE"
