#!/usr/bin/env python3
"""RED tests: p-bands m=8,9 of o|P are empty; known hits sit in m=2 and m=5."""
import unittest

from bands import family_m_hits, band_hits


class BandTest(unittest.TestCase):
    def test_m2_contains_10_5(self):
        hits = family_m_hits(2, 3, 200)
        self.assertIn((10, 5), hits)

    def test_m5_contains_65_15(self):
        hits = family_m_hits(5, 3, 200)
        self.assertIn((65, 15), hits)

    def test_m8_empty(self):
        self.assertEqual(family_m_hits(8, 3, 400), [])

    def test_m9_only_overlap_65_15(self):
        # 65=9*7+2=5*13, already Type B1
        self.assertEqual(family_m_hits(9, 3, 400), [(65, 15)])

    def test_band_8p_to_10p_through_3000_empty(self):
        self.assertEqual(band_hits(8, 10, 8, 3001), [])


if __name__ == '__main__':
    unittest.main()
