$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$scratch = Split-Path -Parent $root
$source = Join-Path $scratch 'erdos142_q42_partial_fifteen_chain_frontier_20260819'
$m14 = Join-Path $scratch 'erdos142_q42_partial_fourteen_state_closure_20260819'
$cert = 'D:\p42_pr_worktrees\erdos142-pr131-refresh-20260818\certificates\erdos-142-q6-117-cell-disjoint-graph-carving-wall'
$six = Join-Path $cert 'homogeneous-partial-six-state-extension\source'
$five = Join-Path $cert 'homogeneous-partial-five-state-wall\source'
$physical = Join-Path $cert 'homogeneous-partial-six-state-extension\audit\independent_six_scope_physical.py'

foreach ($line in Get-Content (Join-Path $root 'SHA256SUMS')) {
    $parts = $line -split '  ', 2
    $actual = (Get-FileHash -Algorithm SHA256 (Join-Path $root $parts[1])).Hash.ToLowerInvariant()
    if ($actual -ne $parts[0]) { throw "audit hash mismatch: $($parts[1])" }
}

& (Join-Path $source 'run.ps1')
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python -I $physical --source $six --five $five
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python -I (Join-Path $root 'hostile_fifteen_audit.py') --source $source --m14 $m14 --six $six --five $five --physical-auditor $physical
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Output 'PASS_FROZEN_M15_HOSTILE_AUDIT_NATIVE'
