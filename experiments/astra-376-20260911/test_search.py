#!/usr/bin/env python3
"""RED tests: complete 0-1 base-3 search reconstructs the A030979 prefix."""
import unittest

from kummer105 import digits_ok, search_base3


# OEIS A030979, 1-indexed including 0 as first term in the data line.
OEIS_PREFIX = [
    0, 1, 10, 756, 757, 3160, 3186, 3187, 3250, 7560, 7561, 7651, 20007,
    59548377, 59548401,
]


class SearchBase3Test(unittest.TestCase):
    def test_search_20_digits_matches_oeis_through_59548401(self):
        # 3^20 = 3486784401 > 59548401; 2^20 masks, complete in this range.
        got = search_base3(20)
        cut = [n for n in got if n <= 59548401]
        self.assertEqual(cut, OEIS_PREFIX)

    def test_every_hit_passes_kummer(self):
        for n in search_base3(16):
            self.assertTrue(digits_ok(n), n)

    def test_no_extra_term_between_20007_and_59548377(self):
        got = search_base3(18)
        between = [n for n in got if 20007 < n < 59548377]
        self.assertEqual(between, [])

    def test_oeis_45e9_terms_satisfy_kummer(self):
        for n in (45773612811, 45775397187):
            self.assertTrue(digits_ok(n), n)


if __name__ == '__main__':
    unittest.main()
