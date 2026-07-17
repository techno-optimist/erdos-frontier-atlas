#!/usr/bin/env python3
"""Independent, dependency-free verifier for the Erdős #13 (Erdős–Sárközy) table.

Problem: f(N) = max |A|, A ⊆ {1,…,N}, with NO a,b,c ∈ A, b ≠ c, such that
a | (b+c) and a < min(b,c). (Bedert, arXiv:2301.07065, proved |A| ≤ ⌊N/3⌋+1 for
sufficiently large N; the small-N table is what this certifies.)

Checks, all exact:
  1. recompute f(N) by branch-and-bound for N=1..45 and match table.json;
  2. cross-check N=1..16 by exhaustive subset search (a second, independent method);
  3. re-verify every listed "exception" (f(N) > ⌊N/3⌋+1) witness: it is valid,
     has the claimed size, and beats the asymptotic bound;
  4. confirm the exceptions are exactly the listed N and the last one is 17.
Exit 0 iff everything holds.
"""
import json
import sys
from itertools import combinations
from pathlib import Path


def valid(A):
    """No a,b,c in A with b != c, a | (b+c), a < min(b,c)."""
    A = sorted(A)
    for a in A:
        for i in range(len(A)):
            if A[i] <= a:
                continue
            for j in range(i + 1, len(A)):
                if (A[i] + A[j]) % a == 0:      # a < A[i] < A[j], b != c
                    return False
    return True


def _can_add(A, cand):
    for a in A:
        for x in A:
            if x > a and (cand + x) % a == 0:
                return False
    return True


def f_backtrack(N):
    best = [0]
    def bt(i, A):
        if len(A) + (N - i + 1) <= best[0]:
            return
        if i > N:
            best[0] = max(best[0], len(A))
            return
        if _can_add(A, i):
            A.append(i); bt(i + 1, A); A.pop()
        bt(i + 1, A)
    bt(1, [])
    return best[0]


def f_brute(N):
    for size in range(N, 0, -1):
        for S in combinations(range(1, N + 1), size):
            if valid(S):
                return size
    return 0


def main():
    doc = json.loads((Path(__file__).parent / "table.json").read_text())
    fvals = doc["f"]
    N = len(fvals)

    # 1. backtracking recompute
    for n in range(1, N + 1):
        assert f_backtrack(n) == fvals[n - 1], f"backtrack mismatch at N={n}"
    # 2. exhaustive cross-check for small N (independent method)
    for n in range(1, 17):
        assert f_brute(n) == fvals[n - 1], f"brute mismatch at N={n}"
    # 3. exception witnesses
    exc = doc["exceptions_over_floor_n_over_3_plus_1"]
    for n_str, rec in exc.items():
        n = int(n_str); w = rec["witness"]
        assert max(w) <= n and valid(w), f"invalid witness at N={n}"
        assert len(w) == rec["f"] == fvals[n - 1], f"witness size wrong at N={n}"
        assert rec["f"] > n // 3 + 1, f"N={n} is not actually an exception"
    # 4. exceptions are exactly those with f(N) > floor(N/3)+1; last is 17
    computed_exc = [n for n in range(1, N + 1) if fvals[n - 1] > n // 3 + 1]
    assert computed_exc == sorted(int(k) for k in exc), "exception set mismatch"
    assert max(computed_exc) == 17, "last exception is not 17"
    assert all(fvals[n - 1] == n // 3 + 1 for n in range(18, N + 1)), \
        "f(N) != floor(N/3)+1 somewhere in 18..45"

    print(json.dumps({
        "valid": True,
        "f_1_to_45": fvals,
        "exceptions_f_exceeds_floor_N_over_3_plus_1": computed_exc,
        "last_exception": 17,
        "note": "f(N) = floor(N/3)+1 exactly for 18 <= N <= 45 (empirical threshold "
                "for Bedert's asymptotic bound); N=17 is the last N that beats it.",
    }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
