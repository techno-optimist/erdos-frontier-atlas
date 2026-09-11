#!/usr/bin/env python3
"""Independent exact checks for the i=2, n=2j+3 P699 family."""
import math
import unittest

from i2 import erdos699_i2_witness, min_prime_divisor, modulus


class I2FamilyTest(unittest.TestCase):
    def test_smallest_triple_has_odd_common_prime(self):
        rec = erdos699_i2_witness(3)
        self.assertEqual(rec['n'], 9)
        self.assertEqual(rec['m'], 3)
        self.assertEqual(rec['prime'], 3)
        self.assertEqual(math.comb(9, 2) % 3, 0)
        self.assertEqual(math.comb(9, 3) % 3, 0)

    def test_composite_m_still_supplies_a_prime(self):
        rec = erdos699_i2_witness(12)
        self.assertEqual(rec['n'], 27)
        self.assertEqual(rec['m'], 9)
        self.assertFalse(math.isqrt(rec['m']) ** 2 != rec['m'] and rec['m'] in (2, 3, 5, 7))
        self.assertGreaterEqual(rec['prime'], 3)
        self.assertEqual(rec['m'] % rec['prime'], 0)
        self.assertEqual(math.comb(27, 2) % rec['prime'], 0)
        self.assertEqual(math.comb(27, 12) % rec['prime'], 0)

    def test_exhaustive_j_through_400(self):
        for j in range(3, 401):
            rec = erdos699_i2_witness(j)
            n = 2 * j + 3
            m = n // math.gcd(n, j)
            self.assertEqual(rec['n'], n)
            self.assertEqual(rec['m'], m)
            self.assertGreaterEqual(m, 3)
            self.assertEqual(math.comb(n, 2) % m, 0)
            self.assertEqual(math.comb(n, j) % m, 0)
            p = rec['prime']
            self.assertGreaterEqual(p, 3)
            self.assertEqual(m % p, 0)
            self.assertTrue(math.comb(n, 2) % p == 0 == math.comb(n, j) % p)

    def test_false_claim_that_m_is_always_prime_is_rejected(self):
        rec = erdos699_i2_witness(12)
        self.assertEqual(rec['m'], 9)
        self.assertGreater(min_prime_divisor(rec['m']), 1)
        self.assertNotEqual(rec['m'], rec['prime'])

    def test_wrong_shift_n_equals_2j_plus_2_need_not_give_this_m(self):
        j = 4
        n = 2 * j + 2
        m = n // math.gcd(n, j)
        self.assertEqual((n, m), (10, 5))
        self.assertEqual(math.comb(n, 2) % m, 0)
        # The i=2 d=3 cancellation uses n=2j+3; this control records a different line.


if __name__ == '__main__':
    unittest.main()
