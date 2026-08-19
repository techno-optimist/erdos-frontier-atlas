param(
    [string]$SourceDir
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
if ([string]::IsNullOrWhiteSpace($SourceDir)) {
    $SourceDir = Join-Path (Split-Path -Parent $Root) "erdos142_weighted_multiset7_twolevel_20260819"
}

python -I (Join-Path $Root "independent_audit.py") $SourceDir
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Output "PASS_TWO_LEVEL_WEIGHTED_HOSTILE_AUDIT_RUNNER"
