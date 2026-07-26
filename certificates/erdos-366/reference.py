#!/usr/bin/env python3
"""Independent reference implementation for Erdős #366 (slow, obviously correct).

Erdős #366: is there a 2-full (powerful) n with n+1 3-full (cubefull)?
  powerful:  p | n  =>  p^2 | n
  cubefull:  p | n  =>  p^3 | n

This file exists to cross-check the fast sweeper (search366.c) on small ranges.
It shares NO code and NO algorithm with it:

  * powerfulness here is decided by FULL factorization by trial division,
    not by the "trial-divide to N^(1/5) then perfect-power the cofactor" test;
  * cubefull numbers here are found by FILTERING every integer in the range,
    not by generating a^3 b^4 c^5 triples.

Two independent wrongs would have to agree to fool the cross-check.

  python3 -I reference.py 1 2000000      # sweep a range, print hits
"""
import sys


def factorize(n):
    """Complete factorization by trial division. Exact; no floats."""
    f = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            f[d] = f.get(d, 0) + 1
            n //= d
        d += 1 if d == 2 else 2
    if n > 1:
        f[n] = f.get(n, 0) + 1
    return f


def is_k_full(n, k):
    """Every prime exponent >= k. 1 is vacuously k-full for every k."""
    if n < 1:
        return False
    return all(e >= k for e in factorize(n).values())


def sweep(lo, hi):
    """Every n in [lo, hi] that answers #366 in either orientation.

    strict  : n powerful AND n+1 cubefull   (the Lean-stub orientation)
    reverse : n cubefull AND n+1 powerful   ((8,9) and (12167,12168) are here)
    """
    hits = []
    for n in range(max(lo, 1), hi + 1):
        if not is_k_full(n, 2):
            continue
        if is_k_full(n + 1, 3):
            hits.append((n, "strict"))
        if is_k_full(n, 3) and is_k_full(n + 1, 2):
            hits.append((n, "reverse"))
    return hits


def main():
    lo = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    hi = int(sys.argv[2]) if len(sys.argv) > 2 else 2_000_000
    for n, orientation in sweep(lo, hi):
        print(f"{orientation}\t{n}\t{factorize(n)}\t{factorize(n + 1)}")
    print(f"# swept [{lo}, {hi}]", file=sys.stderr)


if __name__ == "__main__":
    main()
