#!/usr/bin/env python3
"""Recompute i=3 witnesses. Never overwrite evidence."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from i3 import gcd_both, identity, binom3_gt, binom3_odd


def main():
    pairs = 0
    mod4 = 0
    for n in range(8, 81):
        for j in range(4, n // 2 + 1):
            assert identity(n, j) == 0
            assert binom3_gt(n, j)
            assert gcd_both(n, j) >= 2
            pairs += 1
            if n % 4 == 3:
                assert binom3_odd(n)
                assert gcd_both(n, j) >= 3
                assert gcd_both(n, j) % 2 == 1
                mod4 += 1
    rec = {
        'verified': True,
        'n_min': 8,
        'n_max': 80,
        'pairs': pairs,
        'mod4_eq_3_pairs': mod4,
        'smallest': {'n': 8, 'j': 4, 'gcd': gcd_both(8, 4)},
        'scope': 'i=3 gcd>=2 on the size-bound domain; gcd odd when n=3 mod 4; not full P699',
    }
    print(json.dumps(rec, indent=2))


if __name__ == '__main__':
    main()
