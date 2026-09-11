#!/usr/bin/env python3
"""RED tests for the i=3 2-adic residual."""
import math
import unittest

from residual import cancel, odd_part, op_divides_P


class ResidualTest(unittest.TestCase):
    def test_cancel_when_coprime_to_fac(self):
        # 11 | C(11,3)=165 and 11 > 4 = j, gcd(11, 24)=1
        self.assertEqual(math.comb(11, 3) % 11, 0)
        self.assertTrue(cancel(11, 11, 4))
        self.assertEqual(math.comb(11, 4) % 11, 0)

    def test_cancel_rejects_shared_fac_prime(self):
        # 5 | C(10,3)=120 but gcd(5, 5!)=5 ≠ 1
        self.assertFalse(cancel(5, 10, 5))

    def test_gcd_has_odd_prime_to_200(self):
        for n in range(8, 201):
            for j in range(4, n // 2 + 1):
                g = math.gcd(math.comb(n, 3), math.comb(n, j))
                self.assertGreaterEqual(odd_part(g), 3, (n, j, g))

    def test_op_divides_P_only_three_pairs(self):
        hits = op_divides_P(8, 201)
        self.assertEqual(hits, [(10, 5), (16, 7), (65, 15)])
        for n, j in hits:
            g = math.gcd(math.comb(n, 3), math.comb(n, j))
            self.assertGreaterEqual(odd_part(g), 3)

    def test_i4_still_fails_size(self):
        self.assertLessEqual(math.comb(20, 4), 10 * 9 * 8 * 7)


if __name__ == '__main__':
    unittest.main()
