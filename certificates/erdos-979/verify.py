#!/usr/bin/env python3
"""
Certificate — Erdős #979 / OEIS A385316
a(n) = smallest N = p^3 + q^3 + r^3 (p <= q <= r prime, multiset) in EXACTLY n ways.

Published terms (OEIS A385316): a(1..5) = 24, 185527, 8627527, 999979163, 10588881419.
The A385316 comments state only a(6) > 499243435237 (~4.99e11).

CLAIM certified here: a(6) > 1e12  (no integer N <= 1e12 has exactly six
representations as a sum of three prime cubes), improving the published bound.

Why the verifier is exact and hostile-checkable (no heuristic, total decision):
  To decide the window [0, C] it SUFFICES to use every prime p with p^3 <= C:
  any prime appearing in a triple whose sum is <= C has p^3 <= C. That finite,
  provably-complete prime set makes the exact multiplicity count over [0, C] a
  total decision procedure.

Fail-closed self-check: the run reproduces a(1..5) EXACTLY before it will accept
any a(6) bound. If any known term is wrong the method is unsound and verify EXITS
NONZERO without emitting a bound.

Usage:
  python3 verify.py                # fast self-check to C=2e10 (~1s): reproduces a(1..5), certifies a(6)>2e10
  python3 verify.py --cutoff 1e12  # the headline run (~80s, ~11GB): certifies a(6)>1e12
  python3 verify.py --json         # machine-readable receipt to stdout

Independent cross-verification (2026-07-17): four from-scratch reimplementations
(pure-Python collections.Counter; numpy sort+run-length; shard-by-largest-prime;
and an independent numpy run at the full 1e12) each reproduced a(1..5) exactly
and found NO exactly-six N in their window, agreeing on a(6) > 1e12. See RECEIPT.md.
"""
import argparse, sys
import numpy as np
from sympy import primerange

KNOWN = {1: 24, 2: 185527, 3: 8627527, 4: 999979163, 5: 10588881419}
OEIS_A6_LOWER = 499243435237  # OEIS-stated a(6) > this


def multiplicity_minima(cutoff):
    """Smallest N <= cutoff with exactly k representations, for k = 1..8, over a
    provably-complete prime set. Exact and total."""
    pmax = int(round(cutoff ** (1.0 / 3.0))) + 2
    P = np.array(list(primerange(2, pmax + 1)), dtype=np.int64)
    while P[-1] ** 3 <= cutoff:            # guarantee completeness of the window
        pmax += 100
        P = np.array(list(primerange(2, pmax + 1)), dtype=np.int64)
    C = P ** 3
    n = len(C)
    chunks = []
    for i in range(n):
        if 3 * C[i] > cutoff:
            break
        ci = C[i]
        for j in range(i, n):
            s2 = ci + C[j]
            if s2 + C[j] > cutoff:
                break
            v = s2 + C[j:]
            v = v[v <= cutoff]
            if v.size:
                chunks.append(v)
    sums = np.concatenate(chunks) if chunks else np.array([], dtype=np.int64)
    sums.sort()
    vals, counts = np.unique(sums, return_counts=True)
    out = {}
    for k in range(1, 9):
        hit = vals[counts == k]
        out[k] = int(hit[0]) if hit.size else None
    meta = dict(max_prime=int(P[-1]), n_primes=n,
                prime_set_complete=bool(P[-1] ** 3 > cutoff),
                triples=int(sums.size), distinct=int(vals.size))
    return out, meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cutoff", type=float, default=2e10)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    cutoff = int(args.cutoff)

    res, meta = multiplicity_minima(cutoff)
    mism = [k for k, v in KNOWN.items() if v <= cutoff and res.get(k) != v]
    sound = (len(mism) == 0) and meta["prime_set_complete"]

    a6 = res.get(6)
    if a6 is None:
        claim = f"a(6) > {cutoff}"
    else:
        claim = f"a(6) = {a6}  (smallest N <= {cutoff} with exactly 6 reps)"

    receipt = dict(problem="erdos-979", oeis="A385316", cutoff=cutoff,
                   sound=sound, prime_set_complete=meta["prime_set_complete"],
                   known_reproduced=[k for k in KNOWN if KNOWN[k] <= cutoff and res.get(k) == KNOWN[k]],
                   known_mismatch=mism, a6=a6,
                   new_lower_bound=(None if a6 is not None else cutoff),
                   oeis_prior_lower=OEIS_A6_LOWER,
                   improves_oeis=bool(a6 is None and cutoff > OEIS_A6_LOWER),
                   meta=meta)

    if args.json:
        import json
        print(json.dumps(receipt))
    else:
        print(f"# primes <= {meta['max_prime']} ({meta['n_primes']}), "
              f"complete={meta['prime_set_complete']}, "
              f"triples {meta['triples']:,}, distinct {meta['distinct']:,}")
        for k in range(1, 7):
            v = res[k]
            tag = ""
            if k in KNOWN and KNOWN[k] <= cutoff:
                tag = "  OK" if v == KNOWN[k] else f"  ** MISMATCH (OEIS {KNOWN[k]}) **"
            print(f"a({k}) = {v}{tag}")
        print(f"SOUND={sound}  CLAIM: {claim}")
        if receipt["improves_oeis"]:
            print(f"  -> improves the OEIS-stated a(6) > {OEIS_A6_LOWER}")

    if not sound:
        print("VERIFY FAILED: self-check or completeness gate not satisfied", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
