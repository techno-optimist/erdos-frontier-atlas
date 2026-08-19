#!/usr/bin/env bash
set -euo pipefail

here="$(cd -- "$(dirname -- "$0")" && pwd)"
source_dir="${1:-/mnt/d/p42_scratch/erdos142_q42_partial_at_most_five_state_wall_20260819}"
start="$(date +%s)"

"$source_dir/run.sh"

binary="${TMPDIR:-/tmp}/q42-five-state-hostile-$$"
trap 'rm -f -- "$binary"' EXIT
g++ -O3 -std=c++17 -Wall -Wextra -pedantic \
    "$here/independent_five_state.cpp" -o "$binary"
"$binary"
python3 -I "$here/independent_lower_trim_physical.py" --source "$source_dir"

end="$(date +%s)"
printf 'HOSTILE_WSL_SECONDS=%s\n' "$((end-start))"
printf '%s\n' PASS_HOSTILE_FIVE_STATE_WSL
