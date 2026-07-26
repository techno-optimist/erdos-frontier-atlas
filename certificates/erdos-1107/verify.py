#!/usr/bin/env python3
"""Independent, dependency-free verifier for Erdős #1107 / OEIS A056828 (Mollin–Walsh).

A056828 lists the positive integers that are NOT the sum of at most three POWERFUL
numbers (n is powerful iff p | n ⇒ p² | n; 1 is powerful). The Mollin–Walsh conjecture
is that this set is finite; the only known members are {7, 15, 23, 87, 111, 119}.

This script recomputes the exception set over [1, N] by an exact bitset sumset and asserts
it equals exactly those six values — reproducing the published data (and Jobling's null
result: no seventh exception). All six known exceptions are < 120, so any N ≥ 120 already
pins the table; the default N = 10^6 gives a wide, fast independent re-check.

An operational private run separately reported a 10^10 frontier, but its canonical runner and
receipt are not part of this public package. This verifier therefore makes no 10^10 claim:
it certifies exactly the requested N (default 10^6).

  python3 certificates/erdos-1107/verify.py            # N = 10^6
  python3 certificates/erdos-1107/verify.py 2000000    # custom N
Exit 0 iff the [1,N] exception set is exactly {7,15,23,87,111,119}.
"""
import sys

KNOWN = [7, 15, 23, 87, 111, 119]


def powerful_upto(n):
    """All powerful numbers in [1, n] via the a²·b³ generator (exact, no factorization)."""
    s = set()
    a = 1
    while a * a <= n:
        a2 = a * a
        b = 1
        while a2 * b * b * b <= n:
            s.add(a2 * b * b * b)
            b += 1
        a += 1
    return sorted(s)              # includes 1 (a=b=1)


def exceptions_upto(n):
    pw = powerful_upto(n)
    mask = (1 << (n + 1)) - 1
    bits = 0
    for p in pw:                  # sums of exactly one powerful number
        bits |= 1 << p
    reach = bits
    two = 0
    for p in pw:                  # + one more (sums of two)
        two |= bits << p
    two &= mask
    reach |= two
    three = 0
    for p in pw:                  # + one more (sums of three)
        three |= two << p
    three &= mask
    reach |= three
    return [k for k in range(1, n + 1) if not (reach >> k) & 1]


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 1_000_000
    exc = exceptions_upto(n)
    ok = exc == KNOWN
    print(f"N={n}: exceptions = {exc}")
    print(f"expected {KNOWN} -> {'MATCH' if ok else 'MISMATCH'}")
    if ok:
        print("VALID: A056828 ∩ [1,N] = {7,15,23,87,111,119}; no seventh exception below N.")
        print(f"PUBLIC SCOPE: this run certifies N={n}; no larger private run is implied.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
