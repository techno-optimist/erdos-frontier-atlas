#!/usr/bin/env python3
"""Erdős #142 (r_3(N)) — certified construction no-go on the 39-piece graph-directed EHPS geometry.

Runs two independent, dependency-free (Python stdlib only) checks and passes iff
BOTH hold:

  (1) COMPLETE CELL-CLASS LOCK — the geometry's full-dimensional EHPS-convexity
      constraint class is EXACTLY 12,349 cells (hash-pinned). _verify_enum.py
      re-derives it from the primitive geometry using per-cell exact certificates
      (a strict-interior rational anchor for each full cell; an exact
      Farkas/Gordan certificate for each degenerate/empty cell). No floating
      point touches the certified path; `--exhaustive` re-classifies the entire
      box-feasible universe.

  (2) AFFINE-FAMILY NO-GO — no affine / curvature-cancelling per-piece potential
      satisfies the EHPS convexity V >= 0 on that class. _verify_affine.py checks
      an exact 34-term rational vertex-Farkas certificate (positive multipliers,
      coefficient row cancels over all free columns, negative constant), with a
      mandatory full-dimensionality check on every support cell.

Together: any per-piece potential on this fixed geometry that could realize a
rate above the EHPS 7/24 lower-bound constant for r_3(N) must be GENUINELY
QUADRATIC — the natural affine/additive sub-family is exactly dead.

This does NOT bound r_3(N). Erdős #142 (the asymptotic formula) is an open WALL.
See README.md for the full, honest scope.

    python3 verify.py               # both checks (enumeration sampled) — ~1 min
    python3 verify.py --exhaustive  # full enumeration re-classification — slower

Exit 0 iff both certificates verify.
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GEOM_SHA = "607841330978360a10b3440598a034f6ade903b8afe872c1cbe7bdf441e92ada"
CELLSET_SHA = "35fb19672b28d318f1ea468587a378ebc9906cba9f419b7dbca1a1ff7aa859b6"


def _fail_pin(label: str, expected: str, actual: str) -> bool:
    print(f"\n[PIN MISMATCH] {label}\n   expected {expected}\n   on disk  {actual}")
    return False


def check_pins() -> bool:
    """The pinned hashes must be load-bearing, not decorative: if the objects on
    disk are not the pinned ones, say so instead of printing the pins as if they
    described what was just verified.

    geometry.json is pinned directly. The cell-set hash is canonical (recomputed
    from the geometry by _verify_enum, which checks it against the value embedded
    in enumeration_certificate.json); here we pin that embedded value, closing the
    chain driver-pin -> cert claim -> value re-derived from the geometry.
    """
    ok = True
    actual = hashlib.sha256(open(os.path.join(HERE, "geometry.json"), "rb").read()).hexdigest()
    if actual != GEOM_SHA:
        ok = _fail_pin("geometry.json", GEOM_SHA, actual)
    with open(os.path.join(HERE, "enumeration_certificate.json"), "rb") as fh:
        claimed = json.load(fh).get("canonical_cellset_sha256")
    if claimed != CELLSET_SHA:
        ok = _fail_pin("enumeration_certificate.canonical_cellset_sha256", CELLSET_SHA, str(claimed))
    return ok


def run(label: str, argv: list[str]) -> bool:
    print(f"\n=== {label} ===", flush=True)
    r = subprocess.run([sys.executable, "-S", *argv], cwd=HERE, text=True, capture_output=True)
    tail = [ln for ln in r.stdout.strip().splitlines() if ln.strip()][-3:]
    for ln in tail:
        print("   " + ln)
    if r.returncode != 0 and r.stderr.strip():
        print(r.stderr.strip()[-800:])
    return r.returncode == 0


def main() -> int:
    exhaustive = "--exhaustive" in sys.argv[1:]
    pins_ok = check_pins()
    enum_args = ["_verify_enum.py", "enumeration_certificate.json", "geometry.json"]
    enum_args += ["--exhaustive"] if exhaustive else ["--sample", "200"]

    ok1 = run("(1) complete 12,349-cell class lock", enum_args)
    ok2 = run(
        "(2) affine-family no-go (34-term vertex-Farkas)",
        ["_verify_affine.py", "affine_farkas_cert.json", "geometry.json", "--anchors", "fulldim_cells.json"],
    )

    print("\n" + "=" * 62)
    print(f"  geometry sha256   {GEOM_SHA}")
    print(f"  cell-set sha256   {CELLSET_SHA}")
    print(f"  (0) pinned-object check                      : {'PASS' if pins_ok else 'FAIL'}")
    print(f"  (1) enumeration lock (12,349 full-dim cells) : {'PASS' if ok1 else 'FAIL'}")
    print(f"  (2) affine-family no-go (34-term Farkas)     : {'PASS' if ok2 else 'FAIL'}")
    ok = pins_ok and ok1 and ok2
    print(f"  RESULT: {'CERTIFICATE VALID' if ok else 'CERTIFICATE FAILED'}")
    print("  (a construction on this geometry must be genuinely quadratic; NOT an r_3(N) bound)")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
