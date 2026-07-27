#!/bin/sh
# ./run743.sh <n> <nshards> <budget> <outdir>
set -e
N="$1"; S="$2"; B="$3"; OUT="$4"
HERE=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$OUT"; i=0
while [ "$i" -lt "$S" ]; do
  "$HERE/pack" "$HERE/trees.txt" "$N" "$i" "$S" "$B" > "$OUT/s$i.out" 2>"$OUT/s$i.err" &
  i=$((i+1))
done
wait
cat "$OUT"/s*.out | grep -c '^HARD' > "$OUT/hardcount" || true
echo "done: $(cat "$OUT"/s*.out | grep -c '^HARD' || echo 0) HARD, $(cat "$OUT"/s*.out | grep -c '^UNPACKABLE' || echo 0) UNPACKABLE"
