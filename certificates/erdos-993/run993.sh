#!/bin/sh
# ./run993.sh <nlo> <nhi> <nshards> <outdir>
set -e
LO="$1"; HI="$2"; S="$3"; OUT="$4"
HERE=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$OUT"
n="$LO"
while [ "$n" -le "$HI" ]; do
  i=0
  while [ "$i" -lt "$S" ]; do
    "$HERE/unimodal" "$n" "$i" "$S" > "$OUT/n${n}_s$i.out" 2>&1 &
    i=$((i+1))
  done
  wait
  echo "n=$n done: trees=$(cat "$OUT"/n${n}_s*.out | grep SUMMARY | awk -F'trees=' '{split($2,a,"\t"); s+=a[1]} END {print s}') violations=$(cat "$OUT"/n${n}_s*.out | grep -c '^VIOLATION')"
  n=$((n+1))
done
