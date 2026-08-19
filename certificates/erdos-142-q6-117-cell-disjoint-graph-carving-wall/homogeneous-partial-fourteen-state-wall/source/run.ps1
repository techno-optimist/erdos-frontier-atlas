$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path

& python (Join-Path $root "verify_structural_closure.py")
if ($LASTEXITCODE -ne 0) { throw "primary structural replay failed" }

& python (Join-Path $root "independent_structural_audit.py")
if ($LASTEXITCODE -ne 0) { throw "independent structural audit failed" }

Write-Output "PASS_AT_MOST_FOURTEEN_STATE_STRUCTURAL_WALL"
