#!/bin/sh
# Replay EVERY certificate in certificates/jc-anatomy/ (stdlib python3 only;
# `-I` isolates the interpreter from PYTHONPATH and the user site-dir, so a
# stray sympy install cannot creep into a trust path).
#
# Exit 0 iff every certificate passes with all planted controls firing as
# planted. Path-independent: it cds to its own directory first, so it can be
# invoked from any cwd (e.g. `bash certificates/jc-anatomy/run_all.sh` from the
# repo root).
set -e
cd "$(dirname "$0")"
for c in certify_nonproperness.py \
         galois_group_s3.py \
         fiber_count_generic.py \
         fiber_anchors.py \
         cusp_curve_empty.py \
         degree_floor_check.py; do
  echo "== $c"
  python3 -I "$c"
  echo
done
echo "ALL SIX CERTIFICATES PASSED"
