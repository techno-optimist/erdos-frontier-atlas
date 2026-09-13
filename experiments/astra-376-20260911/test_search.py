#!/usr/bin/env python3
"""RED tests: complete 0-1 base-3 search reconstructs the A030979 prefix."""
import pathlib
import shutil
import subprocess
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

    def test_committed_d35_hits_are_kummer_and_below_cutoff(self):
        path = pathlib.Path(__file__).resolve().parent / 'hits-d35.txt'
        hits = [int(x) for x in path.read_text().split()]
        self.assertEqual(len(hits), 43)
        self.assertEqual(hits, sorted(set(hits)))
        cutoff = 3 ** 35
        for n in hits:
            self.assertTrue(digits_ok(n), n)
            self.assertLess(n, cutoff)
        # next OEIS term after this cutoff
        self.assertGreater(673333777170421930, cutoff)

    @unittest.skipUnless(shutil.which('clang') or shutil.which('gcc'), 'no C compiler')
    def test_c_search_d12_matches_python(self):
        src = pathlib.Path(__file__).resolve().parent / 'search_base3.c'
        cc = shutil.which('clang') or shutil.which('gcc')
        self.assertIsNotNone(cc)
        bin_path = pathlib.Path('/tmp/erdos376-search_base3-d12')
        subprocess.check_call([cc, '-O3', '-o', str(bin_path), str(src)])
        out = subprocess.check_output([str(bin_path), '12'], text=True)
        got = [int(x) for x in out.split() if x.strip()]
        self.assertEqual(got, search_base3(12))

    @unittest.skipUnless(shutil.which('clang') or shutil.which('gcc'), 'no C compiler')
    def test_c_search_d12_split_ranges_cover(self):
        src = pathlib.Path(__file__).resolve().parent / 'search_base3.c'
        cc = shutil.which('clang') or shutil.which('gcc')
        self.assertIsNotNone(cc)
        bin_path = pathlib.Path('/tmp/erdos376-search_base3-d12')
        subprocess.check_call([cc, '-O3', '-o', str(bin_path), str(src)])
        a = subprocess.check_output([str(bin_path), '12', '0', '2048'], text=True)
        b = subprocess.check_output([str(bin_path), '12', '2048', '4096'], text=True)
        got = sorted(int(x) for x in (a + b).split() if x.strip())
        self.assertEqual(got, search_base3(12))


if __name__ == '__main__':
    unittest.main()
