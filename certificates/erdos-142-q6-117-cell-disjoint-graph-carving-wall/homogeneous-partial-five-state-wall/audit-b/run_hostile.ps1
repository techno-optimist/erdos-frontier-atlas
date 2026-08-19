param(
    [string]$Source = "D:\p42_scratch\erdos142_q42_partial_at_most_five_state_wall_20260819"
)

$ErrorActionPreference = "Stop"
$Here = $PSScriptRoot
$Stopwatch = [Diagnostics.Stopwatch]::StartNew()

& (Join-Path $Source "run.ps1")
if ($LASTEXITCODE -ne 0) { throw "frozen source replay failed" }

$Binary = Join-Path $env:TEMP "q42-five-state-hostile-$PID.exe"
try {
    & g++ -O3 -std=c++17 -Wall -Wextra -pedantic `
        (Join-Path $Here "independent_five_state.cpp") -o $Binary
    if ($LASTEXITCODE -ne 0) { throw "hostile C++ compilation failed" }
    & $Binary
    if ($LASTEXITCODE -ne 0) { throw "hostile five-state replay failed" }
    & python -I (Join-Path $Here "independent_lower_trim_physical.py") `
        --source $Source
    if ($LASTEXITCODE -ne 0) { throw "hostile lower/physical replay failed" }
} finally {
    if (Test-Path -LiteralPath $Binary) {
        Remove-Item -LiteralPath $Binary -Force
    }
}

$Stopwatch.Stop()
Write-Output ("HOSTILE_NATIVE_SECONDS={0:N3}" -f $Stopwatch.Elapsed.TotalSeconds)
Write-Output "PASS_HOSTILE_FIVE_STATE_NATIVE"
