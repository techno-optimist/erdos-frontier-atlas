#!/usr/bin/env python3
"""RED tests: n≡3 (mod 4) ⇒ odd_part(C(n,3)) never divides j(j-1)(j-2)."""
import math
import unittest

from mod4 import falling_max, size_gap_poly, o_divides_P_hits_mod4


class Mod4ResidualTest(unittest.TestCase):
    def test_size_gap_poly_positive(self):
        for t in range(1, 200):
            self.assertGreater(size_gap_poly(t), 0)

    def test_six_C_minus_six_P_is_cubic(self):
        for t in range(1, 80):
            n = 4 * t + 3
            gap = 6 * math.comb(n, 3) - 6 * falling_max(n)
            self.assertEqual(gap, 16 * t ** 3 + 96 * t ** 2 + 56 * t + 6)

    def test_C_odd_and_exceeds_falling_max(self):
        for n in range(7, 401, 4):
            self.assertEqual(n % 4, 3)
            C = math.comb(n, 3)
            self.assertEqual(C % 2, 1)
            self.assertGreater(C, falling_max(n))

    def test_no_oP_hits_through_400(self):
        self.assertEqual(o_divides_P_hits_mod4(7, 401), [])


if __name__ == '__main__':
    unittest.main()
