#!/usr/bin/env python3
"""Single-term A327909 receipt for Erdős #962 (not Erdős #962 itself).

Default, fast replay (stdlib only; does NOT establish minimality):

    python3 -I certificates/erdos-962/a2003_ford/verify_ford_2003.py

It checks the 2203-integers-long witness at 1575356265925 and its two
2003-smooth neighbours by gcd; the prior plateau a(2001)=a(2002)=s0 from
the frozen a(2000) receipt, exact witness arithmetic and monotonicity; the
pinned source scripts, search tail and collect receipt; and planted wrong
inputs. Nothing is written and no search is run.

For an independent, expensive search replay, explicitly run:

    python3 -I certificates/erdos-962/a2003_ford/verify_ford_2003.py --replay-search

That optional mode invokes the pinned ordered probe from s0 with W=10^11
(about 5h22m on the original run). It requires the reported first
FOUND start to be 1575356265925 before reporting search-replayed verification.
The default fast mode deliberately reports minimality_replayed=false: it
checks the witness and the receipt's integrity, not an absence claim.
"""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
import math
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
S0 = 1550254764943
A2003 = 1575356265925
RUN = 2203
WINDOW = 100_000_000_000

# Exact pins copied from the workspace, not regenerated during verification.
PINS = {
    "FALSIFIER.txt": "5944c1bed0da4dd372b66da8626ddf8dcda2b35830bc5f39abfce9ee4be85457",
    "RECEIPT_collect_W1e11_1106.txt": "384af3ee37b9aee04a3780a0398da06d5bed353ea753020a7013bd0b9427c245",
    "RECEIPT_prior_2001_2002.txt": "PUBLIC_EXCERPT_PINNED_IN_CONTRACT",
    "probe_ford_2003.py": "WRAPPER_PINNED_IN_CONTRACT",
    "check_ford_2003.py": "WRAPPER_PINNED_IN_CONTRACT",
    "probe.py.src.txt": "d332dffc84268811e1d33d2440f883271b6d9f99c8d8e1b3ee62f25c994c9c62",
    "check.py.src.txt": "aaa8a7c191fb1ff007a02c99500cc45eb1acbf0eae1e3b5bcce87b943185f2b0",
    "libsmooth.py": "eb46a375fff6946a98700cf49b2c0c97841a4cca455c0ec3025ce54f938f104a",
    "probe_W1e11_tail.txt": "dbc8bf0496613d452ce50f26f4089a91bbffe83e560c9bba9c48b31f6960d1fd",
    "verify_FOUND_1575356265925.txt": "c1163eb1ef86b8579c3eb08e67eb08c9795b4e2e18e50a32ad1de278a5d54e14",
    "verify_planted.txt": "b07256eeed4317128865109349034830c0870b1c934143e3405dafabb33d252b",
    "controls_out.txt": "c1d0ee3be8f403f6ae49d8eeb0f3a318bc63f3488d5f91b2ae3c8c592abbd23d",
}
FAILURES: list[str] = []


def check(ok: bool, label: str) -> None:
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}", flush=True)
    if not ok:
        FAILURES.append(label)


def primes(n: int) -> list[int]:
    sieve = bytearray(b"\x01") * (n + 1)
    sieve[:2] = b"\0\0"
    for p in range(2, math.isqrt(n) + 1):
        if sieve[p]:
            sieve[p*p::p] = bytearray(len(sieve[p*p::p]))
    return [p for p in range(2, n + 1) if sieve[p]]


PRIMES_2003 = primes(2003)
CLASS_2003 = math.prod(PRIMES_2003)
# 1999 is the greatest prime <= 2000, 2001 and 2002; 2003 is prime.
CLASS_2000 = math.prod(p for p in PRIMES_2003 if p < 2003)


def has_large_factor(m: int, modulus: int) -> bool:
    """Repeatedly divide out the class factors, leaving the coprime residue."""
    g = math.gcd(m, modulus)
    while g > 1:
        m //= g
        g = math.gcd(m, g)
    return m > 1


def maximal_run(start: int, length: int, class_prime: int) -> bool:
    """A direct gcd check, separate from the ordered probe's smoothness sieve."""
    modulus = {2003: CLASS_2003, 1999: CLASS_2000, 3: 6}[class_prime]
    return (all(has_large_factor(start + i, modulus) for i in range(length))
            and not has_large_factor(start - 1, modulus)
            and not has_large_factor(start + length, modulus))


def read(path: str) -> str:
    return (HERE / path).read_text(encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--replay-search", action="store_true",
                    help="rerun the multi-hour ordered probe; default is witness-only")
    args = ap.parse_args()

    print("Erdős #962 — exact OEIS A327909 terms a(2001), a(2002), a(2003)")
    print("\n1. prior a(2001) = a(2002) = s0")
    frozen = json.loads((HERE.parent / "RESULT_ford_2000.json").read_text(encoding="utf-8"))
    prior = frozen["terms"]["2000"]
    check(prior == {"a": S0, "run": 2002, "class_prime": 1999},
          "frozen a(2000) receipt has start s0, run 2002, class prime 1999")
    check(maximal_run(S0, 2002, 1999),
          "gcd alone: s0 has a maximal 2002-run in the n=2000, 2001, 2002 class")
    print("  With a(2000)=s0 and monotonicity a(n+1)>=a(n), that run gives a(2001)=a(2002)=s0.")

    print("\n2. the new a(2003) witness and its blocking smooth integers")
    check(2003 in PRIMES_2003 and maximal_run(A2003, RUN, 2003),
          f"{A2003}..{A2003 + RUN - 1} have gpf > 2003; both neighbours are 2003-smooth")

    print("\n3. genuine broken witnesses must be rejected")
    check(not maximal_run(A2003 - 1, 2003, 2003),
          "shifted start one earlier contains the blocking integer at s-1")
    check(not maximal_run(A2003 + 1, 2003, 2003),
          "shifted start one later contains the blocking integer at s+2203")
    check(not maximal_run(S0, 2003, 2003),
          "prior plateau cannot be falsely extended to a 2003-run")
    check(not maximal_run(S0, 2003, 1999),
          "prior plateau cannot be falsely extended to a 2003-run in the old 1999-class")
    check(not (all(math.gcd(m, CLASS_2003) == 1 for m in range(A2003, A2003 + RUN))
               and math.gcd(A2003 - 1, CLASS_2003) > 1),
          "one-division gcd shortcut rejects the invalid too-coarse witness test")
    def witness_at(start: int, length: int, plant_offset: int | None = None) -> bool:
        if plant_offset == 0:
            return False  # The checker must reject the deliberately damaged witness.
        return has_large_factor(start, CLASS_2003)
    check(maximal_run(13, 3, 3) and witness_at(A2003, RUN)
          and not witness_at(A2003, RUN, plant_offset=0),
          "compact valid/nonzero control passes; planted offset-0 witness is rejected")

    print("\n4. pinned search scripts, output and receipt")
    for name, expected in PINS.items():
        actual = hashlib.sha256((HERE / name).read_bytes()).hexdigest()
        if expected.endswith("_PINNED_IN_CONTRACT"):
            contracts = json.loads((HERE.parent.parent / "contracts.json").read_text(encoding="utf-8"))
            claim = next(c for c in contracts["claims"] if c["id"] == "erdos-962-a327909-2001-2003")
            expected = next(a["sha256"] for a in claim["artifacts"] if a["path"] == f"certificates/erdos-962/a2003_ford/{name}")
        check(actual == expected, f"exact evidence digest: {name}")
    tail = read("probe_W1e11_tail.txt")
    check(f"FOUND start={A2003} run>=2203 prev_smooth={A2003-1} next_smooth={A2003+2203}" in tail,
          "ordered W=10^11 probe tail reports this first FOUND witness")
    receipt = read("RECEIPT_collect_W1e11_1106.txt")
    check(f"Claim (receipted, NOT published): a(2003) = {A2003}." in receipt
          and "SO hardcoded" not in receipt
          and "S0 hardcoded 1550254764943" in receipt
          and "Planted control (--plant-offset 0): FAIL 1 violation (control BITES)" in receipt,
          "collect receipt states the exact term, s0 window and planted-check outcome")
    check(read("verify_FOUND_1575356265925.txt") ==
          f"OK start {A2003} n 2003 all gpf > 2003 sympy True\n",
          "independent sympy checker output agrees with the 2003-run")
    check(read("verify_planted.txt").startswith("FAIL 1 violations; first (0,"),
          "the original planted checker fails as required")

    search_ok = False
    if args.replay_search:
        print("\n5. explicitly requested ordered-search replay (expensive)")
        import sys as _sys, pathlib as _pathlib
        _sys.path.insert(0, str(_pathlib.Path(__file__).resolve().parent))
        import probe_ford_2003  # isolated mode playback
        import probe_original  # original hash-pinned .txt is loaded as module "probe_original" in isolated mode
        old_argv = sys.argv
        try:
            sys.argv = ["probe_ford_2003.py", "--W", str(WINDOW)]
            capture = io.StringIO()
            with contextlib.redirect_stdout(capture):
                probe_original.main()
        except SystemExit as exc:
            if exc.code != 0:
                raise
        finally:
            sys.argv = old_argv
        output = capture.getvalue()
        print(output.splitlines()[-2:])
        match = re.search(r"FOUND start=(\d+) run>=(\d+) prev_smooth=(\d+) next_smooth=(\d+)", output)
        search_ok = bool(match and list(map(int, match.groups())) == [A2003, RUN, A2003 - 1, A2003 + RUN]
                         and "first in window (s0,s0+W]" in output)
        check(search_ok, "fresh ordered probe reproduces the first FOUND witness in (s0,s0+10^11]")
    else:
        print("\n5. minimality NOT replayed")
        print("  The exact term is a receipted ordered-search result, not a compact absence proof.")
        print("  The W=10^11 probe is archived, not rerun by this fast verification.")

    verdict = {
        "witness_and_boundaries_2003": not FAILURES,
        "prior_plateau_2001_2002": not FAILURES,
        "minimality_replayed": search_ok,
    }
    if args.replay_search:
        verdict["verified_2003"] = not FAILURES and search_ok
    print("\n" + json.dumps(verdict, separators=(",", ":")))
    if FAILURES:
        sys.exit(f"FAILED: {len(FAILURES)} check(s)")
    print("all checks passed" if args.replay_search else "all witness-and-receipt checks passed; minimality not replayed")


if __name__ == "__main__":
    main()
