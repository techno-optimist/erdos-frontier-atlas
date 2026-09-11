#!/usr/bin/env python3
"""RED tests: Type B1 o|P is only (65,15)."""
import unittest

from typeB1 import typeB1_hits, family_hits


class TypeB1Test(unittest.TestCase):
    def test_global_typeB1_through_5000(self):
        self.assertEqual(typeB1_hits(8, 5001), [(65, 15)])

    def test_n_eq_5p_only_65_15(self):
        self.assertEqual(family_hits('5p', 3, 2000), [(65, 15)])

    def test_n_eq_4p_empty(self):
        self.assertEqual(family_hits('4p', 3, 2000), [])

    def test_n_eq_4p_plus_1_empty(self):
        self.assertEqual(family_hits('4p+1', 3, 2000), [])

    def test_n_eq_4p_plus_2_empty(self):
        self.assertEqual(family_hits('4p+2', 3, 2000), [])

    def test_n_eq_5p_plus_1_only_overlap(self):
        # 16=5*3+1=2*7+2, already Type A
        self.assertEqual(family_hits('5p+1', 3, 2000), [(16, 7)])

    def test_n_eq_5p_plus_2_empty(self):
        self.assertEqual(family_hits('5p+2', 3, 2000), [])


if __name__ == '__main__':
    unittest.main()
