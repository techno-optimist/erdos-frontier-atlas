#!/usr/bin/env python3
"""RED tests: Type B2a o|P is empty."""
import unittest

from typeB2a import typeB2a_hits, family_hits


class TypeB2aTest(unittest.TestCase):
    def test_global_typeB2a_through_5000(self):
        self.assertEqual(typeB2a_hits(8, 5001), [])

    def test_n_eq_6p_empty(self):
        self.assertEqual(family_hits('6p', 3, 1500), [])

    def test_n_eq_6p_plus_1_empty(self):
        self.assertEqual(family_hits('6p+1', 3, 1500), [])

    def test_n_eq_6p_plus_2_empty(self):
        self.assertEqual(family_hits('6p+2', 3, 1500), [])

    def test_n_eq_7p_empty(self):
        self.assertEqual(family_hits('7p', 3, 1500), [])

    def test_n_eq_7p_plus_1_empty(self):
        self.assertEqual(family_hits('7p+1', 3, 1500), [])

    def test_n_eq_7p_plus_2_empty(self):
        self.assertEqual(family_hits('7p+2', 3, 1500), [])


if __name__ == '__main__':
    unittest.main()
