#!/usr/bin/env bash
# hello_frontier.sh — the EFA-DR1 10-minute quickstart.
#
# A stranger's machine sees the atlas's epistemic loop end-to-end:
#
#   1. replay a solver-emitted DRAT nonexistence proof (R(3,3)=6, upper half)
#      through the independent drat-trim checker — INCLUDING a truncated-proof
#      negative control that must FAIL, proving the checker can actually fail;
#   2. re-verify a witness/table certificate (Erdős #1107, Mollin–Walsh)
#      with a dependency-free exact recomputation;
#   3. print one gap-map entry with its MECHANICALLY COMPUTED confidence class
#      and what that class means.
#
# Requirements: git, a C compiler (cc), python3. Nothing else. If drat-trim is
# not already on PATH, a pinned upstream commit is cloned into a temp dir and
# built with `cc -O2` (single C file; the only network access this script can
# make, and only in that case).
#
# Usage:  scripts/hello_frontier.sh     (or: make hello-frontier)
# Exits non-zero, loudly, on ANY failed check.

set -euo pipefail

# ---------------------------------------------------------------------------
# plumbing
# ---------------------------------------------------------------------------
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

DRAT_TRIM_REPO="https://github.com/marijnheule/drat-trim"
DRAT_TRIM_COMMIT="2e3b2dc0ecf938addbd779d42877b6ed69d9a985"   # pinned checker
CERT_DIR="certificates/ramsey-3-3"

step=0
banner() {
    step=$((step + 1))
    printf '\n=== [%d/3] %s\n' "$step" "$1"
}
die() {
    printf '\nFAIL: %s\n' "$1" >&2
    printf 'The quickstart stops at the first failed check — nothing after this ran.\n' >&2
    exit 1
}
need() {
    command -v "$1" >/dev/null 2>&1 || die "required tool '$1' not found on PATH ($2)"
}

printf 'Erdős Frontier Atlas — hello, frontier (EFA-DR1 quickstart)\n'
printf 'repo: %s\n' "$REPO_ROOT"

need python3 "https://www.python.org"
need git     "needed to fetch the pinned drat-trim checker if it is not on PATH"

# ---------------------------------------------------------------------------
# [1/3] certified nonexistence: replay the R(3,3)=6 upper-half DRAT proof
# ---------------------------------------------------------------------------
banner "Replay a DRAT nonexistence certificate: R(3,3) = 6, upper half"
printf 'Claim: every 2-coloring of the edges of K_6 has a monochromatic triangle.\n'
printf 'Artifact: %s (40-clause CNF + 247-byte solver-emitted DRAT proof).\n' "$CERT_DIR"

# Locate or build the independent checker.
if command -v drat-trim >/dev/null 2>&1; then
    DRAT_TRIM="$(command -v drat-trim)"
    printf 'checker: drat-trim already on PATH (%s)\n' "$DRAT_TRIM"
    printf 'note: a PATH-provided checker is NOT the pinned build; for a fully pinned\n'
    printf '      replay, remove it from PATH and re-run to build commit %.12s.\n' "$DRAT_TRIM_COMMIT"
else
    CC_BIN="${CC:-cc}"
    command -v "$CC_BIN" >/dev/null 2>&1 || die "no C compiler ('$CC_BIN') — install one or put drat-trim on PATH"
    BUILD_DIR="${TMPDIR:-/tmp}/efa-drat-trim-${DRAT_TRIM_COMMIT}"
    DRAT_TRIM="$BUILD_DIR/drat-trim"
    if [ -x "$DRAT_TRIM" ]; then
        printf 'checker: reusing cached pinned build (%s)\n' "$DRAT_TRIM"
    else
        printf 'checker: building drat-trim @ %.12s into %s\n' "$DRAT_TRIM_COMMIT" "$BUILD_DIR"
        rm -rf "$BUILD_DIR"
        git clone --quiet "$DRAT_TRIM_REPO" "$BUILD_DIR" \
            || die "could not clone $DRAT_TRIM_REPO (network down? put drat-trim on PATH instead)"
        git -C "$BUILD_DIR" -c advice.detachedHead=false checkout --quiet "$DRAT_TRIM_COMMIT" \
            || die "pinned commit $DRAT_TRIM_COMMIT not found in the drat-trim clone"
        actual="$(git -C "$BUILD_DIR" rev-parse HEAD)"
        [ "$actual" = "$DRAT_TRIM_COMMIT" ] || die "checkout landed on $actual, not the pinned $DRAT_TRIM_COMMIT"
        "$CC_BIN" -O2 -o "$DRAT_TRIM" "$BUILD_DIR/drat-trim.c" \
            || die "drat-trim did not compile with '$CC_BIN -O2'"
        printf 'checker: built OK (single C file, cc -O2, pinned commit verified)\n'
    fi
fi

# Positive replay. drat-trim can exit 0 on both verified and not-verified
# outcomes, so we parse its verdict, never the exit code. And the checker's
# progress output uses carriage returns, so the verdict may not start a line:
# match "s VERIFIED" as a SUBSTRING. ("s NOT VERIFIED" does not contain it.)
positive_out="$("$DRAT_TRIM" "$CERT_DIR/problem.cnf" "$CERT_DIR/proof.drat" 2>&1 || true)"
if printf '%s' "$positive_out" | grep -q "s VERIFIED"; then
    printf 'PASS  proof.drat            -> s VERIFIED (the nonexistence claim is machine-checked)\n'
else
    printf '%s\n' "$positive_out" | tr '\r' '\n' | tail -5 >&2
    die "drat-trim did not report 's VERIFIED' for $CERT_DIR/proof.drat"
fi

# Negative control: the deliberately truncated proof MUST fail. A checker that
# cannot fail verifies nothing.
negative_out="$("$DRAT_TRIM" "$CERT_DIR/problem.cnf" "$CERT_DIR/truncated_negctl.drat" 2>&1 || true)"
if printf '%s' "$negative_out" | grep -q "s VERIFIED"; then
    die "negative control UNEXPECTEDLY VERIFIED — the truncated proof must not pass; do not trust this checker build"
fi
if printf '%s' "$negative_out" | grep -q "NOT VERIFIED"; then
    printf 'PASS  truncated_negctl.drat -> s NOT VERIFIED (the checker demonstrably rejects a bad proof)\n'
else
    printf '%s\n' "$negative_out" | tr '\r' '\n' | tail -5 >&2
    die "negative control produced neither verdict — checker output not understood"
fi

# ---------------------------------------------------------------------------
# [2/3] verification frontier: Erdős #1107 (Mollin–Walsh) exception table
# ---------------------------------------------------------------------------
banner "Re-verify a witness certificate: Erdős #1107 (Mollin–Walsh, A056828)"
printf 'Claim: over [1, 200000], the integers that are NOT a sum of at most three\n'
printf 'powerful numbers are exactly {7, 15, 23, 87, 111, 119} — recomputed here\n'
printf 'from scratch by an exact bitset sumset (dependency-free python3).\n\n'
python3 certificates/erdos-1107/verify.py 200000 \
    || die "certificates/erdos-1107/verify.py did not validate at N=200000"
printf '\nPASS  the exception table replays on your machine (the 10^10 frontier is the\n'
printf '      pinned receipt documented in certificates/erdos-1107/README.md)\n'

# ---------------------------------------------------------------------------
# [3/3] the epistemic ledger: one gap-map entry + its confidence class
# ---------------------------------------------------------------------------
banner "Read the gap map: one entry with its computed confidence class"
python3 - <<'PYEOF' || die "could not read atlas/gap_map.json"
import json

MEANING = {
    "C0": "formal proof, machine-checked — the strongest class",
    "C1": ">= 2 independent implementations or replays with DISTINCT artifacts "
          "at the claimed range",
    "C2": "exactly one verified, replayable implementation",
    "C3": "literature- or numerics-grade: no independent in-project "
          "verification artifact yet",
}
RANK = {"C0": 0, "C1": 1, "C2": 2, "C3": 3}

with open("atlas/gap_map.json", encoding="utf-8") as fh:
    gm = json.load(fh)
entries = gm["entries"]

dist = {}
for e in entries:
    dist[e["confidence"]] = dist.get(e["confidence"], 0) + 1

# Show the atlas's current best-evidenced entry (highest class, lowest problem
# number as the deterministic tie-break) — chosen from the data, not hard-coded.
e = min(entries, key=lambda x: (RANK[x["confidence"]], x["problem"], x["quantity"]))

def bound(b):
    return "-" if b is None else f"{b['value']}  ({b['source']}, {b['year']})"

print(f"The gap map holds {len(entries)} bounded quantities. Class distribution: "
      + ", ".join(f"{k}: {dist[k]}" for k in sorted(dist)))
print()
print(f"Best-evidenced entry right now — Erdős problem #{e['problem']} "
      f"(https://www.erdosproblems.com/{e['problem']}):")
print(f"  quantity   : {e['quantity']}")
print(f"  kind       : {e['kind']}")
print(f"  lower      : {bound(e['lower'])}")
print(f"  upper      : {bound(e['upper'])}")
print(f"  witness    : {e['witness_object']}")
print(f"  verifier   : {e['witness_verifier']}")
print()
print(f"  confidence : {e['confidence']} — {MEANING[e['confidence']]}")
print("  ...computed MECHANICALLY from the recorded evidence, never asserted:")
for item in e["evidence"]:
    print(f"    - [{item['type']}] {item['artifact']}")
print()
print("  (tools/validate_gap_map.py recomputes every entry's class from its")
print("   evidence[] and fails the atlas if any stored class overclaims.)")
PYEOF

# ---------------------------------------------------------------------------
# done
# ---------------------------------------------------------------------------
printf '\n=== All three checks passed in %d seconds.\n\n' "$SECONDS"
printf 'You just saw the whole epistemic loop: a machine-checked nonexistence proof\n'
printf '(with a negative control), a replayed witness certificate, and a ledger entry\n'
printf 'whose confidence class is computed from evidence. Where to go next:\n'
printf '  - views/state_of_frontier.md      the generated State of the Frontier report\n'
printf '  - atlas/gap_map.json              all entries (python3 tools/validate_gap_map.py)\n'
printf '  - certificates/                   every certificate ships its own checker\n'
printf '  - FRONTIER_CARTOGRAPHY.md         the field charter: tenets, workstreams, gates\n'
