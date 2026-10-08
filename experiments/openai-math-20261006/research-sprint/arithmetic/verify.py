#!/usr/bin/env python3
"""Small exact falsification checks; the unbounded proof is in README.md."""
import hashlib
import json
from math import comb, gcd
from pathlib import Path


def factors(n):
    result = []
    p = 2
    while p * p <= n:
        power, exponent = 1, 0
        while n % p == 0:
            n //= p
            power *= p
            exponent += 1
        if exponent:
            result.append((p, exponent, power))
        p += 1
    if n > 1:
        result.append((n, 1, n))
    return result


def blocks(n, positions=(0, 1, 2)):
    return [(t, p, power) for t in positions for p, e, power in factors(n - t)
            if p > 3 or (p == 3 and e >= 2)]


def reduced(n, j):
    g = gcd(n, j)
    u, v = j // g, n // g
    return g, u, v, u * (v - u) * (v - 2 * u)


def odd_part(n):
    while n % 2 == 0:
        n //= 2
    return n


def verify():
    counts = {"binomial_pairs": 0, "individual_localizations": 0,
              "positional_pairs": 0, "positional_passes": 0,
              "diagonal_binomial_pairs": 0, "cubic_divisibility_passes": 0}
    # Do not assume every prime survives division by 6: compare against actual C(n,3).
    for n in range(8, 401):
        bn3 = comb(n, 3)
        bb = blocks(n)
        for j in range(1, n // 2 + 1):
            bnj = comb(n, j)
            counts["binomial_pairs"] += 1
            for t, p, power in bb:
                assert bn3 % p == 0
                if bnj % p:
                    assert j % power <= t, (n, j, t, p, power)
                    _, u, v, _ = reduced(n, j)
                    product = 1
                    for r in range(t + 1):
                        product *= t * u - r * v
                    assert product % power == 0
                    counts["individual_localizations"] += 1

    passes = []
    nontrivial_cubic_passes = []
    for n in range(4, 1501, 4):
        bb = blocks(n, (1, 2))  # Stronger lemma omits position 0.
        for j in range(1, n // 2):
            counts["positional_pairs"] += 1
            g, u, v, q = reduced(n, j)
            nn, d = (n - 1) * (n - 2), n - 2 * j
            if q % nn == 0:
                counts["cubic_divisibility_passes"] += 1
                if d >= 4:
                    assert d * d >= 3 * n - 2
                    k = q // nn
                    m = 4 * g ** 3 * k - d
                    assert m * nn == d * (3 * n - d * d - 2)
                    assert m <= -1
                    assert d ** 3 >= n * n + (d - 1) * (3 * n - 2) > n * n
                    assert m % 2 == 0 and m <= -2
                    assert d ** 3 >= 2 * n * n + (d - 2) * (3 * n - 2) > 2 * n * n
                    assert d > 4 * g ** 3
                    r = d - 4 * g ** 3 * ((d - 1) // (4 * g ** 3))
                    assert 1 <= r <= 4 * g ** 3 and -m >= r
                    assert d ** 3 >= r * nn + d * (3 * n - 2)
                    if d % 4 == 0:
                        assert g >= 2 and d > 32 and m % 4 == 0 and m <= -4
                        assert d ** 3 >= 4 * n * n + (d - 4) * (3 * n - 2) > 4 * n * n
                if j > 1:
                    nontrivial_cubic_passes.append([n, j])
            if d >= 4:
                y = d - 4
                discriminant_opposite = 4 * d ** 3 - 9 * d ** 2 - 10 * d - 1
                assert discriminant_opposite == 4 * y ** 3 + 39 * y ** 2 + 110 * y + 71 > 0
                f = nn - d * (3 * n - d * d - 2)
                assert 4 * f == (2 * n - 3 * d - 3) ** 2 + discriminant_opposite > 0
            if all(j % power <= t for t, _, power in bb):
                g, u, v, q = reduced(n, j)
                nn = (n - 1) * (n - 2)
                assert q > 0 and q % nn == 0, (n, j, q, nn)
                assert v ** 6 >= 108 * nn ** 2
                d = n - 2 * j
                assert 4 * g ** 3 * nn <= d * (n * n - d * d)
                passes.append([n, j])
    counts["positional_passes"] = len(passes)
    assert passes, "The cubic implication test must not be vacuous."
    assert passes == [[n, 1] for n in range(4, 1501, 4)]
    assert nontrivial_cubic_passes == [[496, 171], [1464, 561]]

    coefficients = []
    for d in range(4, 29, 4):
        a, b, c = 32 - d, -2 * d * d + 48 * d + 416, 16 * d * d + 352 * d + 1344
        assert min(a, b, c) > 0
        coefficients.append({"d": d, "coefficients": [a, b, c]})
        for j in range(4, 501):
            n = 2 * j + d
            x = n - d - 8
            lhs = 32 * (n - 1) * (n - 2) - d * (n * n - d * d)
            assert lhs == a * x * x + b * x + c > 0
            if n % 4 == 0:
                g, _, _, _ = reduced(n, j)
                assert g >= 2
                assert 4 * g ** 3 * (n - 1) * (n - 2) > d * (n * n - d * d)
            assert odd_part(gcd(comb(n, 3), comb(n, j))) > 1, (n, j)
            counts["diagonal_binomial_pairs"] += 1

    # Eighth diagonal follows from the integer quotient, beyond polynomial positivity.
    for j in range(4, 501):
        n, d = 2 * j + 32, 32
        if n % 4 == 0:
            g = gcd(n, j)
            assert g >= 2 and d <= 4 * g ** 3
        assert odd_part(gcd(comb(n, 3), comb(n, j))) > 1
        counts["diagonal_binomial_pairs"] += 1

    n, j = 348, 158
    g, u, v, q = reduced(n, j)
    d, nn = n - 2 * j, (n - 1) * (n - 2)
    assert d == 32 and g == 2
    assert 4 * g ** 3 * nn <= d * (n * n - d * d)
    assert q % nn != 0
    assert odd_part(gcd(comb(n, 3), comb(n, j))) > 1
    boundary = {"n": n, "j": j, "d": d, "g": g, "Q": q,
                "n_product": nn, "Q_remainder": q % nn,
                "size_margin": 4 * g ** 3 * nn - d * (n * n - d * d)}

    # Multiplying (1) by an extra 3 is false even at a genuine positional pass.
    n, j = 16, 1
    assert all(j % power <= t for t, _, power in blocks(n))
    _, _, _, q = reduced(n, j)
    assert q == (n - 1) * (n - 2)
    assert q % (3 * (n - 1) * (n - 2)) != 0
    n, j = 496, 171
    _, _, _, q = reduced(n, j)
    assert q == 35 * (n - 1) * (n - 2)
    assert (1, 11, 11) in blocks(n) and j % 11 == 6
    assert gcd(comb(n, 3), comb(n, j)) == 310992
    return {"status": "passed", "scope": "bounded exact checks; unbounded proof in README.md",
            "bounds": {"binomial_n_max": 400, "positional_n_max": 1500,
                       "diagonal_j_min": 4, "diagonal_j_max": 500},
            "counts": counts, "positional_passes": "Exactly (n,1) for n=4,8,...,1500 (t=1,2 only).",
            "nontrivial_cubic_passes": nontrivial_cubic_passes,
            "diagonal_coefficients": coefficients, "distance_32_boundary": boundary,
            "negative_control": "False extra factor 3 rejected at (16,1); cubic sufficiency rejected at (496,171)."}


if __name__ == "__main__":
    result = verify()
    here = Path(__file__).resolve().parent
    result["source_sha256"] = {name: hashlib.sha256((here / name).read_bytes()).hexdigest()
                               for name in ("README.md", "verify.py")}
    print(json.dumps(result, indent=2, sort_keys=True))
