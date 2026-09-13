#!/usr/bin/env python3
"""Exact checks for the complete i=2 case of P699."""
import math
import unittest

from i2all import identity, binom2_gt, gcd_both


class I2CompleteTest(unittest.TestCase):
    def test_identity_on_the_domain(self):
        for n in range(6, 41):
            for j in range(3, n // 2 + 1):
                self.assertEqual(identity(n, j), 0)

    def test_size_bound_is_strict(self):
        for n in range(6, 41):
            for j in range(3, n // 2 + 1):
                self.assertTrue(binom2_gt(n, j))

    def test_gcd_never_one(self):
        for n in range(6, 81):
            for j in range(3, n // 2 + 1):
                self.assertGreaterEqual(gcd_both(n, j), 2)

    def test_smallest_triple(self):
        self.assertEqual(gcd_both(6, 3), 5)
        self.assertEqual(math.comb(6, 2), 15)
        self.assertEqual(math.comb(6, 3), 20)

    def test_false_divisibility_is_rejected(self):
        # The proof uses a size bound, not C(n,2) | j(j-1).
        self.assertNotEqual(math.comb(6, 2) % (3 * 2), 0)


if __name__ == '__main__':
    unittest.main()
