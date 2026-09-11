#!/usr/bin/env python3
"""RED tests: Kummer digit form of gcd(C(2n,n), 105)=1."""
import math
import unittest

from kummer105 import coprime_105, digits_ok, enumerate_below


class Kummer105Test(unittest.TestCase):
    def test_equivalence_through_400(self):
        for n in range(0, 401):
            self.assertEqual(coprime_105(n), digits_ok(n), n)

    def test_n_with_base3_digit_2_fails(self):
        # 5 = 12_3 has a digit 2
        self.assertFalse(digits_ok(5))
        self.assertNotEqual(math.gcd(math.comb(10, 5), 105), 1)

    def test_prefix_below_200(self):
        got = enumerate_below(200)
        self.assertIn(0, got)
        self.assertIn(1, got)
        self.assertTrue(all(digits_ok(n) and coprime_105(n) for n in got))
        self.assertEqual(got, [n for n in range(200) if coprime_105(n)])


if __name__ == '__main__':
    unittest.main()
