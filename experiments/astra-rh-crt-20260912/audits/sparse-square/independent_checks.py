"""Independent exact finite/algebra checks; no asymptotic moment evidence.
All writes stay beside this script in its newly created scratch directory.
"""
from collections import Counter
from fractions import Fraction as F
from math import gcd, erfc, exp, log, sqrt, pi
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import tarfile

ROOT = Path(__file__).resolve().parent
INPUT = Path(__file__).resolve().parents[1] / 'twisted-square'


def factor_distinct(n):
    primes = []
    p = 2
    while p * p <= n:
        if n % p == 0:
            primes.append(p)
            while n % p == 0:
                n //= p
        p += 1
    if n > 1:
        primes.append(n)
    return primes


def mobius(n):
    ps = factor_distinct(n)
    return 0 if any(n % (p * p) == 0 for p in ps) else (-1) ** len(ps)


def jordan(n):
    ans = F(n * n)
    for p in factor_distinct(n):
        ans *= F(p * p - 1, p * p)
    assert ans.denominator == 1
    return ans.numerator


def quadratic_checks(D, mask):
    coeff = {d: F(mobius(d)) * mask(d) for d in range(D, 2 * D)}
    direct = sum((coeff[d] * coeff[e] * F(gcd(d, e) ** 2, d*d*e*e)
                  for d in coeff for e in coeff), F())
    gram = sum((jordan(r) * sum((coeff[d] / (d*d) for d in coeff if d % r == 0), F()) ** 2
                for r in range(1, 2 * D)), F())
    singleton = sum((coeff[r]**2 * F(jordan(r), r**4) for r in coeff), F())
    absolute = sum((F(gcd(d, e)**2, d*d*e*e) for d in coeff for e in coeff), F())
    assert direct == gram and 0 <= singleton <= direct <= absolute
    return {'D': D, 'Q': str(direct), 'D_Q_decimal': float(D * direct),
            'isolated_Gram_lower': str(singleton), 'identity_and_order': True}


full_grams = [quadratic_checks(D, lambda d: F(1))
              for D in [1, 2, 3, 4, 7, 12, 16, 24, 32, 48, 64]]
assert all(F(r['isolated_Gram_lower']) > 0 for r in full_grams)
masked_grams = []
for D in [2, 7, 16, 32]:
    for name, mask in [('initial_half', lambda d, D=D: F(int(2*d < 3*D))),
                       ('ramp', lambda d, D=D: F(2*D-d, D)),
                       ('zero', lambda d: F())]:
        masked_grams.append({'mask': name, **quadratic_checks(D, mask)})
assert all(F(r['Q']) == 0 for r in masked_grams if r['mask'] == 'zero')

jordan_identities = []
for n in range(1, 201):
    assert sum(jordan(r) for r in range(1, n+1) if n % r == 0) == n*n
    jordan_identities.append(n)

collision_checks = []
for N, D in [(1, 8), (3, 12), (8, 16), (16, 24), (32, 48)]:
    groups = {}
    for n in range(N, 2*N):
        for d in range(D, 2*D):
            groups.setdefault(n*d*d, []).append((n, d))
    direct_count = sum(len(v)**2 for v in groups.values())
    param_count = 0
    weighted_direct = F()
    weighted_param = F()
    for group in groups.values():
        for n, d in group:
            for m, e in group:
                g = gcd(d, e)
                a, b = d//g, e//g
                assert n % (b*b) == 0
                ell = n // (b*b)
                assert m == ell*a*a and gcd(a, b) == 1
                assert (ell*a*b)**2 == n*m
                weighted_direct += F(mobius(d)*mobius(e), d*e*ell*a*b)
    for d in range(D, 2*D):
        for e in range(D, 2*D):
            g = gcd(d, e)
            a, b = d//g, e//g
            lo = max((N+a*a-1)//(a*a), (N+b*b-1)//(b*b))
            hi = min((2*N-1)//(a*a), (2*N-1)//(b*b))
            param_count += max(0, hi-lo+1)
            for ell in range(lo, hi+1):
                weighted_param += F(mobius(d)*mobius(e), g*g*a*a*b*b*ell)
    assert param_count == direct_count and weighted_param == weighted_direct
    collision_checks.append({'N': N, 'D': D, 'ordered_equalities': direct_count,
                             'equality_to_ND_ratio': str(F(direct_count, N*D)),
                             'weighted_collision_sum': str(weighted_direct),
                             'parametrization_exact': True})

# The genuine entry cloud, including multiplicity, not an invented scalar model.
# These finite boxes illustrate counting identities only, not an asymptotic claim.
cloud_checks = []
for T, N, D, c1 in [(64, 1, 8192, F(1, 16)),
                      (256, 4, 4096, F(1, 16)),
                      (4096, 64, 1024, F(1))]:
    sf = [d for d in range(D, 2*D) if mobius(d)]
    gap = c1 * F(N*D*D, T)
    bins, values = Counter(), Counter()
    origin = N*D*D
    for n in range(N, 2*N):
        for d in sf:
            value = n*d*d
            bin_id = ((value-origin)*gap.denominator)//gap.numerator
            bins[bin_id] += 1
            values[value] += 1
    M = N*len(sf)
    maximum = (2*N-1)*(2*D-1)**2
    B = ((maximum-origin)*gap.denominator)//gap.numerator + 1
    same_bin = sum(v*v for v in bins.values())
    equal = sum(v*v for v in values.values())
    nonzero = same_bin-equal
    assert sum(bins.values()) == M
    assert same_bin*B >= M*M
    assert nonzero == same_bin-equal >= 0
    cs_after_subtraction = F(M*M, B)-equal
    assert nonzero >= cs_after_subtraction
    cloud_checks.append({'T': T, 'N': N, 'D': D, 'c1': str(c1), 'gap': str(gap),
                         'entries': M, 'available_bins': B, 'occupied_bins': len(bins),
                         'same_bin_ordered_pairs': same_bin, 'all_exact_equalities': equal,
                         'nonzero_same_bin_pairs': nonzero,
                         'CS_lower_after_exact_subtraction': str(cs_after_subtraction),
                         'CS_lower_after_subtraction_positive': cs_after_subtraction > 0,
                         'finite_count_check': True})

# Formal Laurent polynomial over Q[A,gamma,Gprime], not a sampled residue.
def poly_times(p, q):
    out = {}
    for (z, A, g, gp), v in p.items():
        for (w, B, h, hp), u in q.items():
            k = (z+w, A+B, g+h, gp+hp)
            out[k] = out.get(k, F()) + v*u
    return {k:v for k,v in out.items() if v}

laurent = {(-1, 0, 0, 0): F(1,2), (0, 0, 1, 0): F(1)}
laurent = poly_times(laurent, {(0, 0, 0, 0): F(1), (1, 1, 0, 0): F(1)})
laurent = poly_times(laurent, {(0, 0, 0, 0): F(1), (1, 0, 0, 1): F(1)})
laurent = poly_times(laurent, {(-1, 0, 0, 0): F(2)})
residue = {k[1:]:v for k,v in laurent.items() if k[0] == -1}
assert residue == {(1, 0, 0): F(1), (0, 1, 0): F(2), (0, 0, 1): F(1)}

# Check prefactors in cases where sqrt(n*m) is exact rational.
for T, N, D, n, m, d, e in [(100, 8, 12, 4, 9, 13, 17),
                             (256, 4, 32, 4, 4, 35, 41)]:
    s = int(sqrt(n*m))
    assert s*s == n*m
    assert F(T, N*D*D)*F(D*D, d*e)*F(N, s)*F(1,T) == F(1, d*e*s)

alpha, n = F(5,6), F(1,2)
exponents = {
    'ordinary_square_index': 2*alpha,
    'product_index': n+2*alpha,
    'entries': n+alpha,
    'core_gap': n+2*alpha-1,
    'off_diagonal_prefactor': 1-n-2*alpha,
    'unsigned_pair_lower': 2*n+2*alpha-1,
    'exact_collision_upper': n+alpha,
    'unsigned_weighted_lower': 1-n-2*alpha+(2*n+2*alpha-1),
    'diagonal': 1-alpha,
    'AFE_error_T_over_D_piece': -F(2,3)+1-alpha,
    'AFE_error_one_piece': -F(2,3),
    'R_target_before_eta_delta': F(1,3)-(1-n-2*alpha),
    'R_target_for_diagonal_scale': 1-alpha-(1-n-2*alpha),
    'required_unsigned_saving_before_eta': F(1,2)-F(1,3),
    'baseline_T_over_D': 1-alpha,
    'baseline_T_one_third': F(1,3),
    'baseline_sqrtT_D_minus_one_fifth': F(1,2)-alpha/5,
    'baseline_T_D_minus_four_fifths': 1-F(4,5)*alpha,
    'H_over_T': F(4,3)-1,
    'weighted_old_moment': F(4,3)-1+F(1,3),
    'sqrt_H': F(4,3)/2,
}
assert exponents['unsigned_pair_lower'] == F(5,3)
assert exponents['exact_collision_upper'] == F(4,3)
assert exponents['unsigned_weighted_lower'] == F(1,2)
assert exponents['R_target_before_eta_delta'] == F(3,2)
assert exponents['R_target_for_diagonal_scale'] == F(4,3)
eta = F(1,100)
rho = eta/100
loss = eta/100
reserve_delta = eta
assert rho+eta+reserve_delta < F(1,6)
assert 2*eta-loss > eta
assert F(1,6)+rho < F(1,3)-eta

# Closed form is derived analytically in the report; these are sanity values.
def W(x):
    y = log(x)
    return erfc(y/2)/2 - y*exp(-y*y/4)/sqrt(pi)

weight_values = {str(y):W(exp(y)) for y in [-10, -2, 0, 2, 10]}
assert weight_values['2'] < 0 and weight_values['0'] == 0.5
assert abs(weight_values['-10']-1) < 1e-8

# Source-archive membership checked without extracting or changing original files.
source_archive_checks = []
for archive, target in [('bcr-v1.src','bcr-v1/main.tex'),
                        ('lr-v1.src','lr-v1/draft.tex'),
                        ('gmrr-v2.src','gmrr-v2/squfv.tex')]:
    archive_path = INPUT/'primary'/archive
    wanted = (INPUT/'primary'/target).read_bytes()
    exact = []
    if tarfile.is_tarfile(archive_path):
        with tarfile.open(archive_path) as tf:
            for member in tf.getmembers():
                if member.isfile() and member.name.endswith(Path(target).name):
                    f = tf.extractfile(member)
                    if f is not None:
                        exact.append((member.name, f.read() == wanted))
    else:
        import gzip
        exact.append(('single_gzip_source', gzip.decompress(archive_path.read_bytes()) == wanted))
    assert any(v for _,v in exact), (archive, exact)
    source_archive_checks.append({'archive':archive, 'local_tex':target,
                                  'members_compared':exact, 'exact_bytes':True})

out = {
    'status': 'PASS',
    'scope': 'Finite identities, actual finite counts, source bytes and exact exponent algebra only. Analytic proofs are in report.md; no new signed moment bound is tested or proved.',
    'full_Gram_checks': full_grams,
    'masked_Gram_checks': masked_grams,
    'Jordan_identity_count': len(jordan_identities),
    'collision_checks': collision_checks,
    'point_cloud_checks': cloud_checks,
    'formal_residue': 'log(X)+2*gamma+Gprime(0); Gprime(0)=0 by evenness',
    'normalization_identity_checked': True,
    'critical_exponents': {k:str(v) for k,v in exponents.items()},
    'loss_budget': {'eta':str(eta), 'rho':str(rho), 'loss':str(loss),
                    'delta':str(reserve_delta), 'diagonal_slack':str(F(1,6)-rho-eta),
                    'postloss_saving':str(2*eta-loss), 'strict':True},
    'W_exp_y_values_noncertifying': weight_values,
    'source_archive_checks': source_archive_checks,
}
(ROOT/'independent-checks.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
