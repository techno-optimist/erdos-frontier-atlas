"""Independent exact algebra checks for a proof-transfer audit.
No analytic theorem is certified by these finite calculations.
Writes only inside this new scratch directory.
"""
from fractions import Fraction as Q
from math import comb
from pathlib import Path
import hashlib
import json

class P:
    def __init__(self, a):
        self.a = tuple(map(Q, a))
        while len(self.a) > 1 and not self.a[-1]:
            self.a = self.a[:-1]
    @staticmethod
    def coerce(x):
        return x if isinstance(x, P) else P([x])
    def __add__(self, other):
        b = self.coerce(other).a
        return P([(self.a[i] if i < len(self.a) else 0) +
                  (b[i] if i < len(b) else 0)
                  for i in range(max(len(self.a), len(b)))])
    __radd__ = __add__
    def __neg__(self):
        return P([-x for x in self.a])
    def __sub__(self, other):
        return self + -self.coerce(other)
    def __rsub__(self, other):
        return self.coerce(other) + -self
    def __mul__(self, other):
        b = self.coerce(other).a
        ans = [Q(0)] * (len(self.a) + len(b) - 1)
        for i, x in enumerate(self.a):
            for j, y in enumerate(b):
                ans[i+j] += x*y
        return P(ans)
    __rmul__ = __mul__
    def strings(self):
        return list(map(str, self.a))

# A polynomial with nonnegative Bernstein coefficients is nonnegative on
# [0, 1]. Strip factors of epsilon, scale epsilon=u/100, and require every
# Bernstein coefficient strictly positive: this proves strict positivity on
# the entire requested open interval, not merely finitely sampled epsilons.
def strictly_positive(p):
    a = list(P.coerce(p).a)
    power = 0
    while len(a) > 1 and a[0] == 0:
        power += 1
        a.pop(0)
    n = len(a) - 1
    scaled = [x * Q(1, 100)**i for i, x in enumerate(a)]
    bernstein = [sum((scaled[i] * Q(comb(k, i), comb(n, i))
                      for i in range(k+1)), Q(0)) for k in range(n+1)]
    assert min(bernstein) > 0, (p.a, bernstein)
    return {"polynomial_coefficients": p.strings(),
            "epsilon_factors_removed": power,
            "positive_Bernstein_coefficients": list(map(str, bernstein))}

e = P([0, 1])
# Check the explicitly expanded original small-level estimate in the report.
old_small_level_power = (1+Q(1, 16)*e)+(-1+Q(1, 8)*e)*(Q(5, 8)+Q(1, 2)*e)
assert old_small_level_power.a == (Q(3, 8), Q(-23, 64), Q(1, 16))
hmax = Q(4, 7) - e
loss = Q(1, 10) * e * e
certificates = {}
for label, h in [("h=epsilon", e), ("h=4/7-epsilon", hmax)]:
    d = (Q(5, 8) + Q(1, 2)*e) * h
    a = 2*d
    t = 1-h
    target_tail = (Q(1, 2)-Q(1, 4)*e)*h
    target_final = (Q(1, 2)-Q(1, 16)*e)*h
    terms = {
        "low values": h-d,
        "Weyl": h-Q(2, 3)*t,
        "GM middle": h-Q(1, 5)*d-Q(1, 2)*t,
        "GM T term": h-Q(4, 5)*d,
    }
    slacks = {
        "P1 H upper": Q(2, 3)-e-h,
        "P1 z lower": a-(1+e)*h,
        "P1 z upper 1": 1-(Q(1, 2)+e)*h-a,
        "P1 z upper 2": Q(1, 2)+(Q(1, 2)-e)*h-a,
        "stricter internal P1 z upper": 1-e-Q(1, 2)*h-a,
        "height witness": 1-(Q(7, 4)+3*e)*h,
        "original pre-(42) small-level bound vs tail target":
            target_tail-((1+Q(1, 16)*e)*h+(-1+Q(1, 8)*e)*d),
        "centering cross vs final target": target_final-(Q(5, 4)*h-Q(1, 2)),
        "centering square vs final target": target_final-(2*h-1),
        "endpoint sliver H/X is o(1)": 1-h,
        "endpoint sliver H^3/X^2 is o(1)": 2-3*h,
        "O(1) endpoint vs tail target": target_tail,
        "P1 error vs final target": (Q(1, 10)-Q(1, 16))*e*h,
        "I1-I2 cross vs final target": (Q(1, 8)-Q(1, 16))*e*h,
    }
    slacks.update({name+" after aggregate X^(epsilon^2/10) loss":
                   target_tail-v-loss for name, v in terms.items()})
    certificates[label] = {k: strictly_positive(v) for k, v in slacks.items()}

# GM substitutions U=D*V; tuple entries are powers of D,V,T.
raw = [(Q(2), Q(-2), Q(0)),
       (Q(18, 5), Q(-4), Q(0)),
       (Q(12, 5), Q(-4), Q(1))]
normalized = [(d+v, v, t) for d, v, t in raw]
assert normalized == [(Q(0), Q(-2), Q(0)),
                      (Q(-2, 5), Q(-4), Q(0)),
                      (Q(-8, 5), Q(-4), Q(1))]
after_CS = [(d/2, 2+v/2, (t-1)/2) for d, v, t in normalized[1:]]
assert after_CS == [(Q(-1, 5), Q(0), Q(-1, 2)),
                    (Q(-4, 5), Q(0), Q(0))]

# Endpoint/truncation partition sanity checks for integer block origins.
# These tests are only combinatorial, not numerical squarefree evidence.
partition_tests = 0
for cutoff in [Q(3, 2), Q(4), Q(99, 4), Q(64), Q(80)]:
    for xmax in [50, 120, 300]:
        def isqrt_q(q):
            from math import isqrt
            return isqrt(q.numerator // q.denominator)
        first = isqrt_q(cutoff)+1
        expected = {d for d in range(1, xmax+1)
                    if cutoff < d*d <= 2*xmax}
        actual = []
        D = first
        while D*D <= 2*xmax:
            actual.extend(d for d in range(D, 2*D) if d*d <= 2*xmax)
            D *= 2
        assert set(actual) == expected
        assert len(actual) == len(set(actual))
        partition_tests += 1

# Freshly hash only the primary inputs actually used.
root = Path(__file__).resolve().parents[1] / 'gm-candidate'
manifest = json.loads((root/'primary-manifest.json').read_text())
used = {'gmrr-source/squfv.tex', 'gm-source/LargevaluesDirichlet17.tex',
        'gmrr-v2.pdf', 'gm-v2.pdf'}
hashes = []
for item in manifest:
    if item['file'] in used:
        digest = hashlib.sha256((root/item['file']).read_bytes()).hexdigest()
        assert digest == item['sha256']
        hashes.append({'file': item['file'], 'sha256': digest, 'matches': True})
assert len(hashes) == len(used)

result = {
    'all_assertions_passed': True,
    'analytic_proof_certified_by_code': False,
    'positivity_domain': 'all 0<epsilon<1/100, epsilon<=h<=4/7-epsilon',
    'reason_h_endpoints_suffice': 'every tested slack is affine in h for fixed epsilon',
    'GM_normalized_D_V_T': [[str(x) for x in row] for row in normalized],
    'after_fourth_D_V_T': [[str(x) for x in row] for row in after_CS],
    'strict_positivity_certificates': certificates,
    'number_of_positive_polynomial_certificates': sum(map(len, certificates.values())),
    'integer_dyadic_partition_tests': partition_tests,
    'primary_hashes': hashes,
}
out = Path(__file__).with_name('independent-results.json')
out.write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps({k: v for k, v in result.items()
                  if k not in ('strict_positivity_certificates', 'primary_hashes')}, indent=2))
print('Full exact results:', out)
