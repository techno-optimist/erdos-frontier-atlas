#!/usr/bin/env python3
"""Exact checks for the i=3 slice of P699."""
import math
import unittest

from i3 import identity, binom3_gt, gcd_both, binom3_odd


class I3Test(unittest.TestCase):
    def test_identity_on_the_domain(self):
        for n in range(8, 31):
            for j in range(4, n // 2 + 1):
                self.assertEqual(identity(n, j), 0)

    def test_size_bound_is_strict(self):
        for n in range(8, 31):
            for j in range(4, n // 2 + 1):
                self.assertTrue(binom3_gt(n, j))

    def test_gcd_never_one(self):
        for n in range(8, 61):
            for j in range(4, n // 2 + 1):
                self.assertGreaterEqual(gcd_both(n, j), 2)

    def test_n_mod4_eq_3_gcd_is_odd_at_least_three(self):
        for n in range(11, 61, 4):
            self.assertTrue(binom3_odd(n))
            for j in range(4, n // 2 + 1):
                g = gcd_both(n, j)
                self.assertGreaterEqual(g, 3)
                self.assertEqual(g % 2, 1)

    def test_smallest_triple(self):
        self.assertEqual(gcd_both(8, 4), 14)
        self.assertEqual(math.comb(8, 3), 56)
        self.assertEqual(math.comb(8, 4), 70)

    def test_i4_size_bound_fails(self):
        # The 2^i > i! cut dies at i=4.
        n, j = 20, 10
        self.assertLessEqual(math.comb(n, 4), j * (j - 1) * (j - 2) * (j - 3))


if __name__ == '__main__':
    unittest.main()
