#!/usr/bin/env python3
"""RED: even n, 3 doesn't divide n-1 ⇒ n-1 divides C(n,3) and hence o."""
import math
import unittest

from typeB2b import n_minus_1_divides_binom3, leftover_class


class TypeB2bStructTest(unittest.TestCase):
    def test_lemma_on_range(self):
        for n in range(6, 200, 2):
            if (n - 1) % 3 == 0:
                continue
            self.assertTrue(n_minus_1_divides_binom3(n), n)
            C = math.comb(n, 3)
            self.assertEqual(C % (n - 1), 0, n)

    def test_n10_excluded_because_three_divides_n_minus_1(self):
        self.assertEqual(10 % 6, 4)
        self.assertFalse(n_minus_1_divides_binom3(10))
        self.assertNotEqual(math.comb(10, 3) % 9, 0)

    def test_leftover_class_is_n_eq_4_mod_6_or_smooth_n_minus_1(self):
        # n=16 ≡ 4 (mod 6): 3 | 15, leftover class
        self.assertEqual(leftover_class(16), 'three_divides_n_minus_1')
        # n=8 ≡ 2 (mod 6): n-1=7 prime > n/10, not Type B2b
        self.assertEqual(leftover_class(8), 'n_minus_1_divides_C')


if __name__ == '__main__':
    unittest.main()
