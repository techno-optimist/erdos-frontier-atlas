#!/usr/bin/env sh
set -eu
root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
source_dir=$(CDPATH= cd -- "$root/../erdos142_q42_partial_fourteen_state_closure_20260819" && pwd)
python3 -I "$root/hostile_core_audit.py" --source "$source_dir"
