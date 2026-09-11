#!/usr/bin/env python3
"""RED tests for closing i=3: n=2p family and coprime-6 self-division."""
import math
import unittest

from residual import odd_part, op_divides_P, twice_prime_hits


class CloseI3Test(unittest.TestCase):
    def test_twice_prime_only_n10(self):
        hits = twice_prime_hits(5, 200)
        self.assertEqual(hits, [(10, 5)])

    def test_coprime_six_self_divides(self):
        for n in range(5, 40):
            if math.gcd(n, 6) != 1:
                continue
            self.assertEqual(math.comb(n, 3) % n, 0)
            for j in range(3, n):
                if math.gcd(n, math.factorial(j)) == 1:
                    self.assertEqual(math.comb(n, j) % n, 0)

    def test_op_P_still_three_through_400(self):
        self.assertEqual(op_divides_P(8, 401), [(10, 5), (16, 7), (65, 15)])


if __name__ == '__main__':
    unittest.main()
