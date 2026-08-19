$ErrorActionPreference = 'Stop'
$env:PYTHONDONTWRITEBYTECODE = '1'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
python -I (Join-Path $root 'replay.py') @args
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
