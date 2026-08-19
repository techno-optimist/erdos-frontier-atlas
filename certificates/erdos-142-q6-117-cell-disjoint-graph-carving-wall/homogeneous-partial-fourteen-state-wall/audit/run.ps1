$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$source = Join-Path (Split-Path -Parent $root) 'erdos142_q42_partial_fourteen_state_closure_20260819'
python -I (Join-Path $root 'hostile_core_audit.py') --source $source
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
