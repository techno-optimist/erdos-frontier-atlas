param([switch]$ExhaustiveTemplate0)

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Arguments = @((Join-Path $Root "verify_all.py"))
if ($ExhaustiveTemplate0) { $Arguments += "--exhaustive-template0" }
python @Arguments
if ($LASTEXITCODE -ne 0) { throw "verify_all.py failed" }
