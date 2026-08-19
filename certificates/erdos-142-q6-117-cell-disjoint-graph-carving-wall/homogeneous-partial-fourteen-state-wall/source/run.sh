#!/usr/bin/env sh
set -eu
root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

python3 "$root/verify_structural_closure.py"
python3 "$root/independent_structural_audit.py"

printf '%s\n' 'PASS_AT_MOST_FOURTEEN_STATE_STRUCTURAL_WALL'
