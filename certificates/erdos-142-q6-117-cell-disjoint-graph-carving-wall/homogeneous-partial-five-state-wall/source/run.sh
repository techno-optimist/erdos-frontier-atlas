#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"

sha256sum -c SHA256SUMS
binary="$(mktemp /tmp/q42-five-state.XXXXXX)"
trap 'rm -f -- "$binary"' EXIT
g++ -std=c++14 -O3 -Wall -Wextra -pedantic \
    exhaust_five_state_orbits.cpp -o "$binary"
"$binary"
python3 -I verify_lower_state_live_sccs.py
echo PASS_AT_MOST_FIVE_STATE_SUNFLOWER_WALL
