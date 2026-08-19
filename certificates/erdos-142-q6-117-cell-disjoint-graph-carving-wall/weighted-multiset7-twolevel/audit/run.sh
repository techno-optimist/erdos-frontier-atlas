#!/usr/bin/env sh
set -eu
root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
source_dir=${1:-"$(dirname -- "$root")/erdos142_weighted_multiset7_twolevel_20260819"}

python3 -I "$root/independent_audit.py" "$source_dir"
printf '%s\n' 'PASS_TWO_LEVEL_WEIGHTED_HOSTILE_AUDIT_RUNNER'
