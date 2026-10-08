#!/usr/bin/env python3
"""Exact bounded checks for the smooth-defect proof; prints a read-only receipt."""
from fractions import Fraction
from hashlib import sha256
import json
from math import comb, factorial, gcd, prod
from pathlib import Path


HERE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def blocks(value):
    answer = []
    prime = 2
    while prime * prime <= value:
        power = 1
        while value % prime == 0:
            power *= prime
            value //= prime
        if power > 1:
            answer.append((prime, power))
        prime += 1
    if value > 1:
        answer.append((value, value))
    return answer


def valuation_factorial(n, p):
    total = 0
    while n:
        n //= p
        total += n
    return total


def main():
    counts = dict(rows=0, pairs=0, retained_blocks=0, localization_checks=0,
                  positional_passes=0, nontrivial_positional_passes=0,
                  eligible_quotient_checks=0, forbidden_region_pairs=0,
                  explicit_prime_witnesses=0, crt_residue_checks=0)
    max_n, max_i = 640, 16
    for n in range(8, max_n + 1, 4):
        row = [comb(n, j) for j in range(n // 2 + 1)]
        all_blocks = [(1, p, m) for p, m in blocks(n - 1)]
        all_blocks += [(2, p, m) for p, m in blocks((n - 2) // 2)]
        p_product = (n - 1) * (n - 2)
        for i in range(3, min(max_i, n // 2 - 1) + 1):
            counts['rows'] += 1
            retained = [(t, p, m) for t, p, m in all_blocks if p > i]
            b = prod(m for t, _, m in retained if t == 1)
            c = prod(m for t, _, m in retained if t == 2)
            a = p_product // (2 * b * c)
            require(p_product == 2 * a * b * c, 'factorization')
            require(gcd(b, c) == 1 and (b * c) % 2 == 1, 'coprimality/parity')
            require(all(p <= i for p, _ in blocks(a)), 'smooth defect')
            require((a == 1) == (gcd(p_product // 2, factorial(i)) == 1),
                    'defect-free characterization')
            for t, p, m in retained:
                counts['retained_blocks'] += 1
                require((n - t) % m == 0 and row[i] % p == 0,
                        'retained prime survives i factorial')
            for j in range(1, n // 2 + 1):
                counts['pairs'] += 1
                d, g = n - 2 * j, gcd(n, j)
                u, v = j // g, n // g
                q = u * (v - u) * (v - 2 * u)
                require(4 * g**3 * q == d * (n*n - d*d), 'cubic identity')
                for t, p, m in retained:
                    counts['localization_checks'] += 1
                    val = (valuation_factorial(n, p) - valuation_factorial(j, p)
                           - valuation_factorial(n - j, p))
                    require((val > 0) == (row[j] % p == 0), 'Legendre/direct binomial')
                    require(row[j] % p == 0 or j % m <= t, 'localization')
                positional = all(j % m <= t for t, _, m in retained)
                if positional:
                    counts['positional_passes'] += 1
                    counts['nontrivial_positional_passes'] += int(j > i)
                    require((u * (v-u)) % b == 0 and q % c == 0,
                            'position-specific products')
                    require((a*q) % p_product == 0, 'weighted cubic divisibility')
                    if d > 0:
                        k = a*q // p_product
                        m = 4 * g**3 * k - a*d
                        require(k >= 1 and m*p_product == a*d*(3*n-d*d-2),
                                'positive quotient identity')
                        if d >= 4*a:
                            counts['eligible_quotient_checks'] += 1
                            f = p_product - a*d*(3*n-d*d-2)
                            require(4*f == (2*n-3*a*d-3)**2
                                    + a*d*d*(4*d-9*a)-10*a*d-1, 'square identity')
                            require(f > 0 and m <= -2 and m % 2 == 0, 'negative even quotient')
                            require(a*d**3 >= 2*n*n+(a*d-2)*(3*n-2) > 2*n*n,
                                    'weighted strip')
                            require(a*d > 4*g**3, 'gcd gap')
                            r = a*d - 4*g**3*((a*d-1)//(4*g**3))
                            require(a*d**3 >= r*p_product+a*d*(3*n-2), 'residue refinement')
                            if d % 4 == 0:
                                require(a*d**3 >= 4*n*n+(a*d-4)*(3*n-2), 'four refinement')
                forbidden = d >= 4*a and (a*d**3 <= 2*n*n or a*d <= 4*g**3)
                if a == 1:
                    forbidden |= d**3 <= 2*n*n or (0 < d <= 32 and d % 4 == 0)
                if j > i and forbidden:
                    counts['forbidden_region_pairs'] += 1
                    require(not positional, 'forbidden region contains positional pass')
                    witness = next((p for t, p, m in retained if j % m > t), None)
                    require(witness is not None and witness > i
                            and row[i] % witness == row[j] % witness == 0,
                            'explicit common prime witness')
                    counts['explicit_prime_witnesses'] += 1

    densities = []
    for i in (3, 4, 5, 7, 11, 13):
        primes = [p for p in range(3, i+1) if blocks(p) == [(p, p)]]
        period, expected = 4*prod(primes), prod(p-2 for p in primes)
        actual = 0
        for n in range(period):
            counts['crt_residue_checks'] += 1
            condition = n % 4 == 0 and all(n % p not in (1, 2) for p in primes)
            gcd_condition = n % 4 == 0 and gcd((n-1)*(n-2)//2, factorial(i)) == 1
            require(condition == gcd_condition, 'CRT versus factorial characterization')
            actual += int(condition)
        require(actual == expected, 'CRT count')
        density = Fraction(actual, period)
        densities.append(dict(i=i, period=period, allowed_classes=actual, density=str(density)))

    # These satisfy the two-position hypotheses, not the full failure premise.
    n, i, j, a = 16, 6, 7, 15
    d, q, p_product = 2, 126, 210
    retained = [(t, p, m) for t, value in ((1,n-1), (2,(n-2)//2))
                for p, m in blocks(value) if p > i]
    require(all(j % m <= t for t, _, m in retained), 'negative-control premises')
    require(q % p_product != 0 and a*q % p_product == 0, 'defect omission control')
    k = a*q // p_product
    m = 4*k-a*d
    require(m > 0 and d < 4*a, 'threshold omission control')
    require(gcd(comb(n,i),comb(n,j)) == 1144, 'control is not a counterexample')

    receipt = dict(schema='efa-smooth-defect-v1', graph_nodes=['P699','S:triage:699'],
                   evidence='bounded_exact_checks_of_an_informal_unbounded_proof',
                   bounds=dict(n_max=max_n, i_max=max_i, n_step=4, j_min=1, j_max='floor(n/2)'),
                   counts=counts, densities=densities,
                   negative_controls=dict(n=n, i=i, j=j, A=a, P=p_product, Q=q, k=k, m=m,
                                          omitted_defect='rejected', omitted_threshold='rejected'),
                   formalized=False, literature_novelty_verified=False,
                   canonical_status_changed=False,
                   source_sha256={name: sha256((HERE/name).read_bytes()).hexdigest()
                                  for name in ('README.md','verify.py')})
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
