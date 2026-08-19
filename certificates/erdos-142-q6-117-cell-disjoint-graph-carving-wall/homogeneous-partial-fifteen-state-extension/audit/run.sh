#!/usr/bin/env sh
set -eu
root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
scratch=$(CDPATH= cd -- "$root/.." && pwd)
source_dir="$scratch/erdos142_q42_partial_fifteen_chain_frontier_20260819"
m14="$scratch/erdos142_q42_partial_fourteen_state_closure_20260819"
cert=/mnt/d/p42_pr_worktrees/erdos142-pr131-refresh-20260818/certificates/erdos-142-q6-117-cell-disjoint-graph-carving-wall
six="$cert/homogeneous-partial-six-state-extension/source"
five="$cert/homogeneous-partial-five-state-wall/source"
physical="$cert/homogeneous-partial-six-state-extension/audit/independent_six_scope_physical.py"

(cd "$root" && sha256sum -c SHA256SUMS)
sh "$source_dir/run.sh"
python3 -I "$physical" --source "$six" --five "$five"
python3 -I "$root/hostile_fifteen_audit.py" --source "$source_dir" --m14 "$m14" --six "$six" --five "$five" --physical-auditor "$physical"
printf '%s\n' 'PASS_FROZEN_M15_HOSTILE_AUDIT_WSL'
