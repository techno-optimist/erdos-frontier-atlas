#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"

source_dir=/mnt/d/p42_scratch/erdos142_q42_partial_at_most_five_state_wall_20260819
check_source() {
    local expected="$1" name="$2" actual
    actual="$(sha256sum "$source_dir/$name" | cut -d' ' -f1)"
    test "$actual" = "$expected"
}
check_source 6fa6b6b2fb2a113f837e37960a63edb17c759691af982fa24e3a6ab3c575eb72 AT_MOST_FIVE_STATE_SUNFLOWER_WALL.md
check_source 2f311d5aa389cca75ba75c1d21a6fc13d8612ba013a952704a8163103e00c6cb exhaust_five_state_orbits.cpp
check_source b59ac9c7da552ff520755a43ebd317c51b0d5ebdfd41ae835a90515e9d9b1139 verify_lower_state_live_sccs.py
check_source 302a244d71a4f5668239c388cc4ba6237ea44a54a3b9a4999ccdd1bd87038631 run.ps1
check_source 853d765139a5839ae4f90fe357abf13a1f96115ce6389f499195cd229d947c74 run.sh
check_source 2005c6c005f97393f0e69b1ea8ec9656b800e3731c409eaa67092e7d5d736d71 SHA256SUMS
sha256sum -c SHA256SUMS
echo PASS_FROZEN_SOURCE_AND_AUDIT_HASHES

binary="$(mktemp /tmp/q42-five-hostile.XXXXXX)"
trap 'rm -f -- "$binary"' EXIT
g++ -std=c++14 -O3 -Wall -Wextra -pedantic independent_five_state_orbit_audit.cpp -o "$binary"
"$binary"
python3 -I independent_lower_physical_scope_audit.py
echo APPROVE_Q42_AT_MOST_FIVE_STATE_SUNFLOWER_WALL
