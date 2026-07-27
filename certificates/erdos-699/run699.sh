#!/bin/sh
# ./run699.sh <lo> <hi> <nshards> <outdir>   -- shards the row range across cores
set -e
LO="$1"; HI="$2"; S="$3"; OUT="$4"
HERE=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$OUT"
SPAN=$(( (HI - LO + S - 1) / S ))
i=0
while [ "$i" -lt "$S" ]; do
  A=$(( LO + i * SPAN )); B=$(( A + SPAN )); [ "$B" -gt "$HI" ] && B="$HI"
  [ "$A" -lt "$B" ] && python3 -I "$HERE/exact.py" --sweep "$A" "$B" > "$OUT/s$i.out" 2>&1 &
  i=$((i+1))
done
wait
echo "counterexamples: $(cat "$OUT"/s*.out | grep -o '[0-9]* counterexamples' | awk '{s+=$1} END {print s+0}')"
