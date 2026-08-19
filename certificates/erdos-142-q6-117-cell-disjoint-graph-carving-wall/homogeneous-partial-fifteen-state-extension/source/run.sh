#!/usr/bin/env sh
set -eu
root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
build=$(mktemp "${TMPDIR:-/tmp}/erdos142_m15.XXXXXX")
trap 'rm -f "$build"' EXIT HUP INT TERM

python3 -I "$root/verify_chain_residual.py"
c++ -O3 -std=c++14 "$root/probe_chain_product.cpp" -o "$build"
"$build" all-critical

printf '%s\n' 'PASS_FIFTEEN_STATE_CHAIN_CLOSURE'
