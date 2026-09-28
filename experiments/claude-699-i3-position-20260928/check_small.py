#!/usr/bin/env python3
"""Exact checks on small n (no dependencies).

1. (*) itself, on every odd prime q | C(n,3) with q not dividing C(n,j), for 8 <= n < 600,
   4 <= j <= n/2, straight from the binomial coefficients: no violation.
2. No pair with 8 <= n <= NMAX (default 3000) passes (*) for all odd q | C(n,3); in
   particular none violates the reduction (every passing pair would need 4 | n and a small
   odd part).
3. Negative control: the position-blind condition odd_part(C(n,3)) | j(j-1)(j-2) DOES admit
   (10,5), (16,7) and (65,15) -- the positions are what exclude them.
"""
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import position as P  # noqa: E402


def main():
    nmax = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
    viol = pairs = 0
    for n in range(8, 600):
        c3 = math.comb(n, 3)
        for j in range(4, n // 2 + 1):
            cj = math.comb(n, j)
            for M, t in P.blocks(n):
                q = min(P.factor(M))
                if cj % q and (j % M) + ((n - j) % M) != t:
                    viol += 1
            pairs += 1
    assert viol == 0, viol
    print(f"1. (*) holds on all {pairs} pairs with 8 <= n < 600")

    hits = [(n, j) for n in range(8, nmax + 1) for blk in [P.blocks(n)]
            for j in range(4, n // 2 + 1) if P.passes(n, j, blk)]
    assert hits == [], hits[:10]
    assert all(P.in_reduction(n) for n, _ in hits)
    print(f"2. no pair with 8 <= n <= {nmax} passes (*) for every odd prime of C(n,3)")

    blind = [(n, j) for n in range(8, 70) for j in range(4, n // 2 + 1)
             if P.passes_position_blind(n, j)]
    assert blind == [(10, 5), (16, 7), (65, 15)], blind
    assert not any(P.passes(n, j) for n, j in blind)
    print(f"3. control: the position-blind condition admits {blind}; (*) rejects all three")
    print("all checks passed")


if __name__ == "__main__":
    main()
