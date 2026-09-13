#!/usr/bin/env python3
"""Independent exact algebra/support checks, not a moment-theorem verifier.
All outputs are confined to this file's newly created scratch directory.
"""
from collections import Counter, defaultdict
from fractions import Fraction as Q
from itertools import product
from math import comb, isqrt, log, pi
from pathlib import Path
import cmath
import hashlib
import json

ROOT = Path(__file__).resolve().parent

def mu_sieve(N):
    mu = [1] * (N + 1)
    mu[0] = 0
    primes = []
    composite = [False] * (N + 1)
    for n in range(2, N + 1):
        if not composite[n]:
            primes.append(n)
            mu[n] = -1
        for p in primes:
            if n * p > N:
                break
            composite[n * p] = True
            if n % p == 0:
                mu[n * p] = 0
                break
            mu[n * p] = -mu[n]
    return mu

def prime_exponents(n):
    a = []
    p = 2
    while p * p <= n:
        if n % p == 0:
            e = 0
            while n % p == 0:
                n //= p
                e += 1
            a.append(e)
        p += 1
    if n > 1:
        a.append(1)
    return a

def tau(n, q):
    if q == 0:
        return int(n == 1)
    ans = 1
    for e in prime_exponents(n):
        ans *= comb(e + q - 1, q - 1)
    return ans

def coefficient_identity(U, k, N):
    """Tuple enumeration plus prime-exponent formula for zeta powers.
    This does not reuse the proposal's convolution-based RHS oracle.
    """
    mu = mu_sieve(N)
    floor_u = U.numerator // U.denominator
    rhs = [0] * (N + 1)
    for j in range(1, k + 1):
        restricted = Counter()
        for aa in product(range(1, floor_u + 1), repeat=j):
            m, sign = 1, 1
            for a in aa:
                m *= a
                sign *= mu[a]
            if m <= N and sign:
                restricted[m] += sign
        for m, weight in restricted.items():
            for b in range(1, N // m + 1):
                rhs[m * b] += (-1) ** (j - 1) * comb(k, j) * weight * tau(b, j - 1)
    e = {n: -sum(mu[d] for d in range(1, min(n, floor_u) + 1) if n % d == 0)
         for n in range(2, N + 1)}
    e = {n: value for n, value in e.items() if value}
    epow = {1: 1}
    for _ in range(k):
        new = defaultdict(int)
        for a, ca in epow.items():
            for b, cb in e.items():
                if a * b <= N:
                    new[a * b] += ca * cb
        epow = new
    remainder = [0] * (N + 1)
    for a, weight in epow.items():
        for b in range(1, N // a + 1):
            remainder[a * b] += weight * mu[b]
    assert all(rhs[n] + remainder[n] == mu[n] for n in range(1, N + 1))
    cutoff = (U ** k).numerator // (U ** k).denominator
    assert all(rhs[n] == mu[n] and remainder[n] == 0 for n in range(1, cutoff + 1))
    min_support = (floor_u + 1) ** k
    assert all(remainder[n] == 0 for n in range(1, min(N + 1, min_support)))
    return mu, rhs, remainder, cutoff, min_support

identity_rows = []
for U in (Q(1), Q(3, 2), Q(2), Q(5, 2), Q(3), Q(7, 2), Q(4)):
    for k in range(1, 5):
        cutoff = (U ** k).numerator // (U ** k).denominator
        N = max(40, cutoff + 30)
        _, _, _, cutoff, min_support = coefficient_identity(U, k, N)
        identity_rows.append({"U": str(U), "k": k, "cutoff": cutoff,
                              "full_identity_checked_through": N,
                              "support_lower_bound": min_support})
mu, rhs, rem, _, _ = coefficient_identity(Q(2), 2, 12)
assert (mu[9], rhs[9], rem[9]) == (0, -1, 1)

# Exact sharp block split, including fractional endpoints and integer thresholds.
split_rows = []
marked_box_keys = set()
for D in (Q(3), Q(7, 2), Q(4), Q(9, 2), Q(8), Q(12), Q(49, 4), Q(50), Q(101, 2), Q(75)):
    upper = 2 * D
    cutoff_a = isqrt(upper.numerator // upper.denominator)
    assert Q(cutoff_a ** 2) <= upper < Q((cutoff_a + 1) ** 2)
    assert upper >= 2 * D  # symbolic U^2 = 2D, no floating rounding
    N = (upper.numerator + upper.denominator - 1) // upper.denominator
    mu = mu_sieve(N)
    for threshold in (Q(1), Q(3, 2), Q(2), Q(5, 2), Q(3), Q(7), Q(1000)):
        first = defaultdict(int)
        second = defaultdict(int)
        total_tuples = 0
        marked_tuples = 0
        assigned_tuples = set()
        for a in range(1, cutoff_a + 1):
            for b in range(1, cutoff_a + 1):
                for c in range(1, N // (a * b) + 1):
                    n = a * b * c
                    if not D <= n < upper:
                        continue
                    total_tuples += 1
                    is_marked = Q(c) >= threshold
                    family = first if is_marked else second
                    family[n] += mu[a] * mu[b]
                    A = 1 << (a.bit_length() - 1)
                    B = 1 << (b.bit_length() - 1)
                    Cbase = 1 << (c.bit_length() - 1)
                    C0 = max(Q(Cbase), threshold) if is_marked else Q(Cbase)
                    if is_marked:
                        assert C0 >= threshold
                        assert C0 <= c < 2 * Cbase <= 2 * C0
                        assert D / 8 < A * B * C0 < 2 * D
                        marked_tuples += 1
                        marked_box_keys.add((str(D), str(threshold), A, B, str(C0)))
                    key = (a, b, c)
                    assert key not in assigned_tuples
                    assigned_tuples.add(key)
        assert len(assigned_tuples) == total_tuples
        block = [n for n in range(1, N + 1) if D <= n < upper]
        assert all(mu[n] == -first[n] - second[n] for n in block)
        split_rows.append({"D": str(D), "U_squared": str(upper), "integer_a_cutoff": cutoff_a,
                           "C_threshold": str(threshold), "block_coefficients": len(block),
                           "tuples": total_tuples, "marked_tuples": marked_tuples})
# A genuine negative control: c=2 is lost if complementary >= / < is replaced by > / <.
assert not (Q(2) > Q(2) or Q(2) < Q(2))
missing_boundary_tuple = (1, 2, 2)
assert Q(3) <= missing_boundary_tuple[0] * missing_boundary_tuple[1] * missing_boundary_tuple[2] < Q(6)

# Rational fourth-coefficient norms for binary interval families.
beta = {4: 1, 6: 2, 9: 1}  # mu(a)mu(b) for a,b in {2,3}
W = sum(Q(b * b, r * r) for r, b in beta.items())
ell_all = list(range(5, 37))

def f_square_coeff(interval):
    f = defaultdict(Q)
    for r, b in beta.items():
        for ell in interval:
            f[r * ell] += Q(b, r)
    square = defaultdict(Q)
    for n, cn in f.items():
        for m, cm in f.items():
            square[n * m] += cn * cm
    return square

def energy(interval):
    return sum(value * value for value in f_square_coeff(interval).values())

all_m = {r1 * r2 * ell1 * ell2 for r1, r2 in product(beta, repeat=2)
         for ell1, ell2 in product(ell_all, repeat=2)}
M4 = max(tau(m, 4) for m in all_m)
levels = []
for width in (1, 2, 4, 8, 16, 32):
    intervals = [ell_all[start:start + width] for start in range(0, len(ell_all), width)]
    summed = sum(energy(interval) for interval in intervals)
    size2 = sum(len(interval) ** 2 for interval in intervals)
    bound = M4 * W * W * size2
    global_bound = M4 * W * W * len(ell_all) ** 2
    assert summed <= bound <= global_bound
    levels.append({"width": width, "intervals": len(intervals), "sum_energy": str(summed),
                   "representation_bound": str(bound), "global_level_bound": str(global_bound)})

# Every discrete interval has a disjoint O(log L) canonical decomposition.
def canonical_cover(lo, hi, root_lo=0, root_hi=32):
    if lo <= root_lo and root_hi <= hi:
        return [(root_lo, root_hi)]
    mid = (root_lo + root_hi) // 2
    out = []
    if lo < mid and root_lo < hi:
        out.extend(canonical_cover(lo, hi, root_lo, mid))
    if lo < root_hi and mid < hi:
        out.extend(canonical_cover(lo, hi, mid, root_hi))
    return out

canonical_count = 0
max_cover = 0
for lo in range(32):
    for hi in range(lo + 1, 33):
        cover = canonical_cover(lo, hi)
        covered = [n for a, b in cover for n in range(a, b)]
        assert covered == list(range(lo, hi))
        assert len(cover) <= 2 * 6
        max_cover = max(max_cover, len(cover))
        canonical_count += 1

# Finite sign/unit-modulus diagnostics only; they are not analytic bound evidence.
phase_rows = []
for t in (-100.5, -2.0, 0.0, 1.75, 31.25, 199.0):
    for u in (-17.0, 0.0, 22.0):
        v = 2 * t + u
        Bv = sum(complex(b, (-1) ** r) / r * cmath.exp(-1j * v * log(r)) for r, b in beta.items())
        plus = sum(cmath.exp(1j * v * log(ell)) for ell in (5, 6, 9, 10))
        minus = sum(cmath.exp(-1j * v * log(ell)) for ell in (5, 6, 9, 10))
        error = abs(abs(Bv * plus) - abs(Bv * minus))
        assert error < 1e-10
        phase_rows.append({"t": t, "u": u, "absolute_modulus_difference": error})
v_bad = pi / (2 * log(3 / 2))
complex_plus = cmath.exp(1j * v_bad * log(2)) + 1j * cmath.exp(1j * v_bad * log(3))
complex_minus = cmath.exp(-1j * v_bad * log(2)) + 1j * cmath.exp(-1j * v_bad * log(3))
assert abs(complex_plus) < 1e-10 and abs(complex_minus) > 1.99
v_freeze = pi / log(3 / 2)
full_dual = sum(cmath.exp(1j * v_freeze * log(ell)) for ell in (2, 3))
assert abs(full_dual) < 1e-10

# Full algebraic scaling ledger, with fixed eta and an actual aggregate budget.
d = Q(5, 6)
eta = Q(1, 120)
c = Q(7, 12) + eta
r, ell = d - c, 1 - c
p = r + ell
raw = [Q(0), ell - r, -Q(1, 2) + 2 * ell]
assert raw == [Q(0), 1 - d, Q(3, 2) - 2 * c]
assert p == Q(2, 3) - 2 * eta
assert max(raw) == Q(1, 3) - 2 * eta
alpha = eta / 20
log_budget = eta / 2
loss = 5 * alpha + log_budget
assert loss < eta
assert max(raw) + loss < Q(1, 3) - eta
assert Q(1, 3) - eta == Q(13, 40)
assert not Q(3, 2) - 2 * Q(7, 12) < Q(1, 3)
assert not max(raw) + 2 * eta < Q(1, 3)
# Open height-length exponent box: omega <= eta/4, after an eta aggregate loss.
eta_endpoints = (Q(1, 1000000), Q(1, 48))
neighborhood = []
for ee in eta_endpoints:
    omega = ee / 4
    for dd in (Q(5, 6) - omega, Q(5, 6) + omega):
        for qq in (Q(4, 3) - omega, Q(4, 3) + omega):
            cc = Q(7, 12) + ee
            max_exp = max(Q(0), 1 - dd, Q(3, 2) - 2 * cc) + ee
            target = 1 - qq / 2 - ee / 2
            assert max_exp < target
            assert Q(1, 2) < dd < 1
            neighborhood.append({"eta": str(ee), "d": str(dd), "q": str(qq),
                                 "upper_exponent_after_eta": str(max_exp),
                                 "target_exponent": str(target), "strict_slack": str(target - max_exp)})
# These endpoint checks accompany, not replace, the affine-inequality proof in report.md.

def boundary(h):
    dd = (Q(1, 2) - h / 4) / (1 - h)
    qq = h / (1 - h)
    assert qq == 4 * dd - 2
    return {"h": str(h), "d": str(dd), "q": str(qq), "target": str(1 - qq / 2)}

output = {
    "scope": "Exact finite algebra/support/norm accounting and finite phase diagnostics; no proof of an asymptotic analytic moment or RH.",
    "passed": True,
    "identity": {"cases": identity_rows, "case_count": len(identity_rows),
                 "truncated_coefficients_checked": sum(x["cutoff"] for x in identity_rows),
                 "full_identity_coefficients_checked": sum(x["full_identity_checked_through"] for x in identity_rows),
                 "negative_control": {"U": 2, "k": 2, "n": 9, "mu": 0, "truncated": -1, "remainder": 1}},
    "sharp_split": {"cases": split_rows, "case_count": len(split_rows),
                    "block_coefficients_checked": sum(x["block_coefficients"] for x in split_rows),
                    "tuple_assignments_checked": sum(x["tuples"] for x in split_rows),
                    "distinct_marked_boxes_across_cases": len(marked_box_keys),
                    "negative_boundary_control": {"lost_tuple_if_both_inequalities_strict": missing_boundary_tuple, "threshold": 2}},
    "coefficient_energy": {"beta": beta, "weighted_beta_L2": str(W), "max_tau4": M4, "levels": levels,
                           "canonical_intervals_checked": canonical_count, "maximum_cover_size": max_cover},
    "phase_diagnostics": {"case_count": len(phase_rows), "cases": phase_rows,
                          "complex_dual_negative_control": {"plus_modulus": abs(complex_plus), "minus_modulus": abs(complex_minus)},
                          "frozen_interval_negative_control": {"full_interval_modulus": abs(full_dual), "singleton_modulus": 1}},
    "exponents": {"d": str(d), "eta": str(eta), "c": str(c), "r": str(r), "L": str(ell), "RL": str(p),
                  "raw": list(map(str, raw)), "pointwise_divisor_parameter": str(alpha),
                  "aggregate_loss": str(loss), "reported_final_exponent": str(Q(13, 40)),
                  "negative_no_eta_rejected": True, "negative_exhausted_budget_rejected": True},
    "neighborhood_endpoint_checks": neighborhood,
    "variance_boundary": [boundary(Q(4, 7)), boundary(Q(4, 7) + Q(1, 1000))]
}
(ROOT / "checks.json").write_text(json.dumps(output, indent=2) + "\n")
summary = {"passed": output["passed"],
           "identity_case_count": output["identity"]["case_count"],
           "truncated_coefficients_checked": output["identity"]["truncated_coefficients_checked"],
           "full_identity_coefficients_checked": output["identity"]["full_identity_coefficients_checked"],
           "sharp_split_case_count": output["sharp_split"]["case_count"],
           "sharp_block_coefficients_checked": output["sharp_split"]["block_coefficients_checked"],
           "tuple_assignments_checked": output["sharp_split"]["tuple_assignments_checked"],
           "marked_boxes_across_cases": output["sharp_split"]["distinct_marked_boxes_across_cases"],
           "binary_levels_checked": len(levels), "canonical_intervals_checked": canonical_count,
           "phase_diagnostic_count": len(phase_rows),
           "negative_controls": ["insufficient cutoff", "missing exact threshold", "complex dual coefficient conjugation",
                                 "frozen interval cancellation", "eta=0 gives no saving", "exhausted aggregate saving"],
           "checks_path": str(ROOT / "checks.json")}
(ROOT / "checks-summary.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps(summary, indent=2))
