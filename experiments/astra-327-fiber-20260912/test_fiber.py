"""Exact oracle tests for multiplier-sensitive P327 fibers."""
import importlib.util
import math
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent


def module():
    path = HERE / 'fiber.py'
    if not path.exists():
        raise AssertionError('fiber.py implementation is missing')
    spec = importlib.util.spec_from_file_location('fiber', path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class FiberTest(unittest.TestCase):
    def test_activation_modulus_matches_original_divisibility(self):
        f = module()
        for k in (1, 2, 3):
            for a in range(1, 18):
                for b in range(a + 1, 19):
                    r = f.activation_modulus(a, b, k)
                    for m in range(1, 25):
                        direct = (k * (m * a) * (m * b)) % (m * a + m * b) == 0
                        self.assertEqual(m % r == 0, direct, (a, b, k, m))
        # Scaling can introduce a forbidden pair: {1, 4} -> {5, 20}.
        self.assertEqual(f.activation_modulus(1, 4, 1), 5)
        self.assertNotEqual(1 * 4 % (1 + 4), 0)
        self.assertEqual(5 * 20 % (5 + 20), 0)

    def test_state_counts_and_weights_match_direct_enumeration(self):
        from fractions import Fraction
        f = module()
        self.assertTrue(hasattr(f, 'state_count'), 'state_count is missing')
        self.assertTrue(hasattr(f, 'state_weight'), 'state_weight is missing')
        for P, L in (([2, 3], 5), ([2, 3], 25), ([2], 9), ([], 6), ([2, 3], 1)):
            Q = math.prod(P)
            divisors = [d for d in range(1, L + 1) if L % d == 0]
            self.assertEqual(sum(f.state_weight(P, L, d) for d in divisors),
                             math.prod(Fraction(p - 1, p) for p in P))
            for d in divisors:
                for N in range(91):
                    direct = sum(math.gcd(m, Q) == 1 and math.gcd(m, L) == d
                                 for m in range(1, N + 1))
                    self.assertEqual(f.state_count(N, P, L, d), direct, (P,L,d,N))

    def test_prefix_deficits_match_independent_subset_oracle(self):
        from fractions import Fraction
        from itertools import combinations
        f = module()
        self.assertTrue(hasattr(f, 'analyze'), 'analyze is missing')
        for k in (1, 2, 3):
            result = f.analyze([2, 3], 5, 12, k)
            S = [1, 2, 3, 4, 6, 8, 9, 12]
            self.assertEqual(result['smooth'], S)
            bound = Fraction(1)
            for row in result['states']:
                d = row['d']
                betas = []
                for i in range(1, len(S) + 1):
                    best = 0
                    for size in range(i + 1):
                        for sub in combinations(S[:i], size):
                            if all((k*d*a*d*b) % (d*a+d*b) != 0
                                   for a,b in combinations(sub, 2)):
                                best = max(best, size)
                    betas.append(best)
                self.assertEqual(row['alpha'], betas)
                deficits = [0] + [i-b for i,b in enumerate(betas, 1)]
                increments = [b-a for a,b in zip(deficits, deficits[1:])]
                self.assertEqual(row['delta'], increments)
                self.assertTrue(set(increments) <= {0,1})
                bound -= row['weight'] * sum(Fraction(e,c) for e,c in zip(increments,S))
                for i, witness in enumerate(row['witnesses']):
                    self.assertTrue(set(witness) <= set(S[:i+1]))
                    self.assertEqual(len(witness), betas[i])
                    self.assertTrue(all((k*d*a*d*b) % (d*a+d*b) != 0
                                        for a,b in combinations(witness, 2)))
            self.assertEqual(result['coefficient'], bound)
            baseline = f.analyze([2,3], 1, 12, k)
            self.assertLess(result['coefficient'], baseline['coefficient'])

    def test_finite_bound_is_fiber_deficit_sum_at_every_endpoint(self):
        f = module()
        self.assertTrue(hasattr(f, 'finite_bound'), 'finite_bound is missing')
        for L in (1,5,25):
            for k in (1,2,3):
                result = f.analyze([2,3],L,12,k)
                rows = {r['d']:r for r in result['states']}
                for N in range(201):
                    missing = 0
                    for m in range(1,N+1):
                        if math.gcd(m,6)!=1:
                            continue
                        row = rows[math.gcd(m,L)]
                        i = sum(c*m<=N for c in result['smooth'])
                        missing += i-row['alpha'][i-1] if i else 0
                    bound = f.finite_bound(N,result)
                    self.assertEqual(bound,N-missing,(L,k,N))
                    self.assertGreaterEqual(bound,0)
                    if k%2:
                        self.assertGreaterEqual(bound,(N+1)//2)
                self.assertLessEqual(f.finite_bound(1000,result),
                                     f.finite_bound(1000,f.analyze([2,3],1,12,k)))

    def test_bound_dominates_direct_small_extremal_values(self):
        from itertools import combinations
        f = module()
        for k in (1,2,3):
            result = f.analyze([2,3],5,12,k)
            for N in range(17):
                optimum = 0
                for size in range(N,-1,-1):
                    if any(all(k*a*b % (a+b) != 0 for a,b in combinations(sub,2))
                           for sub in combinations(range(1,N+1),size)):
                        optimum = size
                        break
                self.assertLessEqual(optimum,f.finite_bound(N,result),(k,N))

    def test_prime_power_activation_is_not_truncated_to_the_state(self):
        f = module()
        self.assertEqual(f.activation_modulus(1,24,1),25)
        coarse = f.analyze([2,3],5,24,1)
        fine = f.analyze([2,3],25,24,1)
        state5 = next(r for r in coarse['states'] if r['d']==5)
        state25 = next(r for r in fine['states'] if r['d']==25)
        self.assertNotIn([1,24],state5['edges'])
        self.assertIn([1,24],state25['edges'])
        self.assertNotEqual((5*1)*(5*24) % (5*1+5*24),0)
        self.assertEqual((25*1)*(25*24) % (25*1+25*24),0)

    def test_hand_certificates_and_closed_floor_formulas(self):
        from itertools import combinations
        f = module()
        # Disjoint cliques force sum(|clique|-1) omitted vertices.
        certificates = [
            (1,1,6,[(3,6)]),
            (1,1,12,[(3,6),(4,12)]),
            (1,5,3,[(2,3)]),
            (1,5,4,[(1,4),(2,3)]),
            (1,5,8,[(1,4),(2,8),(3,6)]),
            (1,5,12,[(1,4),(2,8),(3,12),(6,9)]),
            (2,5,3,[(2,3)]),
            (2,5,4,[(1,4),(2,3)]),
            (2,5,6,[(1,4),(2,3,6)]),
            (2,5,12,[(1,4),(2,8),(3,12),(6,9)]),
        ]
        for k,d,cutoff,cliques in certificates:
            vertices = [x for clique in cliques for x in clique]
            self.assertEqual(len(vertices),len(set(vertices)))
            self.assertLessEqual(max(vertices),cutoff)
            for clique in cliques:
                self.assertTrue(all(k*(d*a)*(d*b) % (d*a+d*b)==0
                                    for a,b in combinations(clique,2)))
            result = f.analyze([2,3],5,12,k)
            row = next(r for r in result['states'] if r['d']==d)
            i = sum(c<=cutoff for c in result['smooth'])
            self.assertTrue(set(vertices) <= set(result['smooth'][:i]))
            self.assertEqual(sum(len(c)-1 for c in cliques),i-row['alpha'][i-1])
        r1 = f.analyze([2,3],5,12,1)
        r2 = f.analyze([2,3],5,12,2)
        for N in range(501):
            def H(q):
                X = N//q
                return X-X//2-X//3+X//6
            self.assertEqual(f.finite_bound(N,r1),N-H(6)-H(12)-H(15)-H(20)-H(40)+H(30))
            self.assertEqual(f.finite_bound(N,r2),N-H(6)-H(12)-H(15)-H(20))

    def test_invalid_hypotheses_are_rejected_not_normalized(self):
        f = module()
        for args in ((0,4,1),(1,1,1),(1,4,0),(1.5,4,1),(True,4,1)):
            with self.subTest(activation=args), self.assertRaises(ValueError):
                f.activation_modulus(*args)
        for args in (([2,2],5,12,1),([4],5,12,1),([2,3],6,12,1),
                     ([2,3],0,12,1),([2,3],5,0,1),([2,3],5,12,0),
                     ([3,2],5,12,1),([2,3],5,12.5,1)):
            with self.subTest(analyze=args), self.assertRaises(ValueError):
                f.analyze(*args)
        for args in ((10,[2,3],5,2),(-1,[2,3],5,1),(10,[2],2,1)):
            with self.subTest(state=args), self.assertRaises(ValueError):
                f.state_count(*args)
        with self.assertRaises(ValueError):
            f.finite_bound(-1,f.analyze([2,3],5,12,1))
        with self.assertRaises(ValueError):
            f.analyze([2,3,5],1,10000,1)  # explicit demo resource cap


if __name__ == '__main__':
    unittest.main()
