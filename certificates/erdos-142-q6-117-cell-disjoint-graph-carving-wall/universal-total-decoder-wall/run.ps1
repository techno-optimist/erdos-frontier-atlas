$ErrorActionPreference = 'Stop'
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $here
try {
    foreach ($line in Get-Content .\SHA256SUMS) {
        if (-not $line.Trim()) { continue }
        $parts = $line -split '\s+', 2
        $actual = (Get-FileHash -Algorithm SHA256 $parts[1]).Hash.ToLowerInvariant()
        if ($actual -ne $parts[0].ToLowerInvariant()) {
            throw "SHA256 mismatch: $($parts[1])"
        }
    }
    Write-Output 'PASS_UNIVERSAL_TOTAL_DECODER_SHA256SUMS'
    python -I .\verify.py
    if ($LASTEXITCODE -ne 0) { throw 'primary replay failed' }
    python -I .\independent_replay.py
    if ($LASTEXITCODE -ne 0) { throw 'independent replay failed' }
}
finally {
    Pop-Location
}
