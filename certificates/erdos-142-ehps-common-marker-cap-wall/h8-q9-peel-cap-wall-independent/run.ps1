$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
python -I -B (Join-Path $Root "independent_replay.py")
if ($LASTEXITCODE -ne 0) { throw "independent hostile replay failed" }
