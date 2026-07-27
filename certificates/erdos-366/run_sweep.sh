#!/bin/sh
# Shard the #366 sweep across cores and wait for every shard.
#
#   ./run_sweep.sh <lo> <hi> <nshards> <outdir>
#
# Each shard writes <outdir>/shard<i>.out. Union of shards == whole range:
# shard i takes a = amin+i, amin+i+nshards, ... in every (b,c) block, so the
# shards partition the candidate set exactly (verify.py checks this).
set -e
LO="$1"; HI="$2"; N="$3"; OUT="$4"
HERE=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$OUT"
i=0
while [ "$i" -lt "$N" ]; do
    "$HERE/search366" "$LO" "$HI" "$i" "$N" > "$OUT/shard$i.out" 2> "$OUT/shard$i.err" &
    i=$((i + 1))
done
wait
cat "$OUT"/shard*.out | grep '^HIT' | sort -u > "$OUT/hits.txt" || true
cat "$OUT"/shard*.out | grep '^SUMMARY' > "$OUT/summaries.txt"
echo "sweep complete: $(wc -l < "$OUT/hits.txt") hit lines, $(wc -l < "$OUT/summaries.txt") shards"
