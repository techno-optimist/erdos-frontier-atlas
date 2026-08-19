#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"

if (( $# > 2 )); then
    echo "usage: $0 [six-state-source-directory] [five-state-directory]" >&2
    exit 2
fi
source_dir="${1:-../erdos142_q42_partial_six_state_frontier_20260819}"
five_dir="${2:-../erdos142_q42_partial_at_most_five_state_wall_20260819}"
[[ -d "$source_dir" ]] || { echo "missing source: $source_dir" >&2; exit 2; }
[[ -d "$five_dir" ]] || { echo "missing <=5 dependency: $five_dir" >&2; exit 2; }

sha256sum -c SHA256SUMS.hostile
python3 -I independent_six_scope_physical.py \
    --source "$source_dir" --five "$five_dir"
bash "$source_dir/run.sh" "$five_dir"

binary="$(mktemp /tmp/q42-six-hostile.XXXXXX)"
trap 'rm -f -- "$binary"' EXIT
g++ -std=c++14 -O3 -Wall -Wextra -pedantic \
    independent_six_state.cpp -o "$binary"
"$binary"
echo PASS_HOSTILE_SIX_STATE_WSL_AUDIT
