#!/usr/bin/env python3
"""Independent bounded falsification checks for the rational-position proofs."""
import hashlib
import json
from math import comb, gcd
from pathlib import Path


def factors(n):
    result = []
    p = 2
    while p * p <= n:
        power, e = 1, 0
        while n % p == 0:
            power *= p
            e += 1
            n //= p
        if e:
            result.append((p, e, power))
        p += 1
    if n > 1:
        result.append((n, 1, n))
    return result


def blocks(n, i, t):
    return [(p, power) for p, e, power in factors(n - t)
            if p > i or (p == i and e >= 2)]


def prod(xs):
    p = 1
    for x in xs:
        p *= x
    return p


def h(n, j, t, a, b):
    d = b * j - a * n
    return prod(d + t * a - r * b for r in range(t + 1))


def odd_part(n):
    while n % 2 == 0:
        n //= 2
    return n


def verify():
    refs = [(1, 2), (1, 3), (1, 4), (2, 5), (1, 5), (2, 7),
            (3, 8), (5, 12), (1, 13), (2, 6), (0, 5), (-1, 5)]
    counts = {"binomial_pairs": 0, "individual_localizations": 0,
              "position_reference_checks": 0, "nontrivial_gcd_gains": 0,
              "restored_divisor_checks": 0, "third_gap_implications": 0,
              "third_gap_direct_binomial_checks": 0, "generic_gap_implications": 0,
              "quotient_identities": 0}

    # Actual binomial values independently validate localization inputs.
    for i in range(3, 9):
        for n in range(2 * i + 2, 101):
            bi = comb(n, i)
            for j in range(i + 1, n // 2 + 1):
                bj = comb(n, j)
                counts["binomial_pairs"] += 1
                for t in range(i):
                    for p, power in blocks(n, i, t):
                        assert bi % p == 0
                        if bj % p:
                            assert j % power <= t
                            counts["individual_localizations"] += 1

    # Test each whole position separately, ensuring nonvacuous input populations.
    for i in range(3, 9):
        for n in range(2 * i + 2, 181):
            for t in range(i):
                bb = blocks(n, i, t)
                rough = prod(power for _, power in bb)
                for j in range(1, n // 2 + 1):
                    if all(j % power <= t for _, power in bb):
                        for a, b in refs:
                            gain = gcd(rough, b) ** t
                            value = h(n, j, t, a, b)
                            assert value % (rough * gain) == 0, (n, i, j, t, a, b)
                            counts["position_reference_checks"] += 1
                            if gain > 1 and value:
                                counts["nontrivial_gcd_gains"] += 1

    for n in range(8, 601, 4):
        b1, b2 = blocks(n, 3, 1), blocks(n, 3, 2)
        for j in range(1, n // 2 + 1):
            pos1 = all(j % power <= 1 for _, power in b1)
            pos2 = all(j % power <= 2 for _, power in b2)
            if pos1:
                for a, b in [(1, 3), (1, 6), (5, 12), (7, 15), (2, 6)]:
                    assert h(n, j, 1, a, b) % ((n - 1) * gcd(n - 1, b)) == 0
                    counts["restored_divisor_checks"] += 1
            d = 3 * j - n
            if j > 3 and d in (-1, 2):
                assert not pos2, (n, j)
            if pos1 and pos2 and j > 3:
                assert (6 * j - 2 * n - 1) ** 2 >= 4 * (n - 1) * gcd(n - 1, 3) + 9
                counts["third_gap_implications"] += 1
            if j > 3 and (6 * j - 2 * n - 1) ** 2 < 4 * (n - 1) * gcd(n - 1, 3) + 9:
                assert odd_part(gcd(comb(n, 3), comb(n, j))) > 1
                counts["third_gap_direct_binomial_checks"] += 1

            # Generic theorem also holds for j=1, supplying nonvacuous implications.
            if pos1 and pos2:
                for a, b in [(1, 3), (1, 4), (1, 5), (2, 5), (1, 6), (2, 7)]:
                    threshold = 6 * a * (b - a) * (2 * b - a) + 2
                    if n > threshold:
                        d = b * j - a * n
                        assert 3 * (2 * d + 2 * a - b) ** 2 >= 3 * b * b + 4 * (n - 1)
                        if b % 3 == 0:
                            assert (2 * d + 2 * a - b) ** 2 >= b * b + 4 * (n - 1) * gcd(n - 1, b)
                        counts["generic_gap_implications"] += 1

    # Prior cubic has nontrivial false positives. Test the rational quotient identity
    # on all cubic passes through 1500, not on claimed P699 counterexamples.
    nontrivial = []
    for n in range(4, 1501, 4):
        nn = (n - 1) * (n - 2)
        for j in range(1, n // 2):
            g = gcd(n, j)
            u, v = j // g, n // g
            q = u * (v - u) * (v - 2 * u)
            if q % nn == 0:
                k = q // nn
                if j > 1:
                    nontrivial.append([n, j])
                for a, b in refs:
                    d = b * j - a * n
                    c0, c1, c2 = a * (b - a) * (b - 2 * a), b * b - 6 * a * b + 6 * a * a, 6 * a - 3 * b
                    m = b ** 3 * g ** 3 * k - c0 * (n + 3) - c1 * d
                    assert m * nn == (c2 * d * d + 3 * c1 * d + 7 * c0) * n + 2 * d ** 3 - 2 * c1 * d - 6 * c0
                    counts["quotient_identities"] += 1
    assert nontrivial == [[496, 171], [1464, 561]]
    for n, j in nontrivial:
        d = 3 * j - n
        assert (d + 1) * (d - 2) % ((n - 1) * gcd(n - 1, 3)) != 0

    # Negative controls: exponent t is sharp; omitted lone3 needs 3|b restoration.
    assert all(5 % power <= 1 for _, power in blocks(16, 3, 1))
    assert h(16, 5, 1, 1, 5) == 50
    assert 50 % 25 == 0 and 50 % 125 != 0
    assert h(16, 5, 1, 1, 2) == 35 and 35 % 15 != 0
    assert counts["nontrivial_gcd_gains"] > 0
    assert counts["generic_gap_implications"] > 0
    assert counts["third_gap_direct_binomial_checks"] > 0
    return {"status": "passed", "scope": "bounded exact tests; unbounded proofs in README.md",
            "bounds": {"i_max": 8, "localization_n_max": 100, "transfer_n_max": 180,
                       "rational_gap_n_max": 600, "cubic_identity_n_max": 1500},
            "counts": counts, "reference_positions": refs,
            "nontrivial_cubic_falsepositives_rejected": nontrivial,
            "negative_controls": ["gcd exponent t+1 rejected at (i,n,j,t,a,b)=(3,16,5,1,1,5)",
                                  "unconditional lone3 restoration rejected at (n,j,a,b)=(16,5,1,2)"],
            "third_gap_note": "No nontrivial t1,t2 positional passes occur at this bound; separate binomial checks test the excluded interval directly."}


if __name__ == "__main__":
    result = verify()
    here = Path(__file__).resolve().parent
    result["source_sha256"] = {name: hashlib.sha256((here / name).read_bytes()).hexdigest()
                               for name in ("README.md", "verify.py")}
    print(json.dumps(result, indent=2, sort_keys=True))
