#!/usr/bin/env python3
"""RED tests: Type A o|P hits are only (10,5) and (16,7)."""
import unittest

from typeA import typeA_hits, family_hits


class TypeATest(unittest.TestCase):
    def test_global_typeA_through_5000(self):
        self.assertEqual(typeA_hits(8, 5001), [(10, 5), (16, 7)])

    def test_n_eq_2p_only_10_5(self):
        self.assertEqual(family_hits('2p', 3, 2000), [(10, 5)])

    def test_n_eq_2p_plus_2_only_16_7(self):
        self.assertEqual(family_hits('2p+2', 3, 2000), [(16, 7)])

    def test_n_eq_2p_plus_1_empty(self):
        self.assertEqual(family_hits('2p+1', 3, 2000), [])

    def test_n_eq_3p_empty(self):
        self.assertEqual(family_hits('3p', 3, 2000), [])

    def test_n_eq_3p_plus_1_only_overlaps(self):
        # 10=3*3+1=2*5, 16=3*5+1=2*7+2
        self.assertEqual(family_hits('3p+1', 3, 2000), [(10, 5), (16, 7)])

    def test_n_eq_3p_plus_2_empty(self):
        self.assertEqual(family_hits('3p+2', 3, 2000), [])


if __name__ == '__main__':
    unittest.main()
