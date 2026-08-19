#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"

if (( $# > 1 )); then
    echo "usage: $0 [five-state-directory]" >&2
    exit 2
fi
if (( $# == 1 )); then
    five_state_dir="$1"
elif [[ -n "${Q42_FIVE_STATE_DIR:-}" ]]; then
    five_state_dir="$Q42_FIVE_STATE_DIR"
else
    five_state_dir="../erdos142_q42_partial_at_most_five_state_wall_20260819"
    echo "NOTICE: using convenience-only sibling <=5 path; pinned hashes, not this location, establish trust." >&2
fi
if [[ ! -d "$five_state_dir" ]]; then
    echo "missing <=5 dependency directory: $five_state_dir" >&2
    exit 2
fi

sha256sum -c SHA256SUMS

primary="$(mktemp /tmp/q42-six-primary.XXXXXX)"
burnside="$(mktemp /tmp/q42-six-burnside.XXXXXX)"
certificate="$(mktemp /tmp/q42-six-boundary.XXXXXX)"
trap 'rm -f -- "$primary" "$burnside" "$certificate"' EXIT

g++ -std=c++14 -O3 -Wall -Wextra -pedantic \
    exhaust_six_state_orbits_cegar.cpp -o "$primary"
"$primary" "$certificate"
g++ -std=c++14 -O3 -Wall -Wextra -pedantic \
    verify_six_state_burnside.cpp -o "$burnside"
"$burnside"
python3 -I verify_six_boundary.py "$certificate"
python3 -I verify_six_scope_physical.py "$five_state_dir"
echo PASS_AT_MOST_SIX_STATE_SUNFLOWER_WALL
